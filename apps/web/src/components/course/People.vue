<template>
  <view>
    <view class="wq-head">
      <text class="wq-h1">{{ t("menu.people") }}</text>
      <view v-if="canManage" class="wq-row">
        <view class="wq-btn" @click="panel = panel === 'add' ? '' : 'add'">＋ {{ t("people.add") }}</view>
        <view class="wq-btn primary" @click="panel = panel === 'ai' ? '' : 'ai'">✦ {{ t("people.aiGroups") }}</view>
      </view>
    </view>

    <!-- add people -->
    <view v-if="panel === 'add'" class="wq-card">
      <text class="wq-label">{{ t("people.addHint") }}</text>
      <textarea v-model="addText" class="wq-textarea" :placeholder="'student4\nzhang.san@example.edu.cn'" />
      <view class="wq-row actions">
        <view class="wq-btn primary" :class="{ disabled: busy || !addText.trim() }" @click="addPeople">{{ busy ? t("common.saving") : t("people.addBtn") }}</view>
        <view class="wq-btn" @click="panel = ''">{{ t("common.cancel") }}</view>
      </view>
      <view v-if="addResult" class="result">
        <text v-if="addResult.added.length" class="ok">✓ {{ t("people.added", { n: addResult.added.length }) }}：{{ addResult.added.join("、") }}</text>
        <text v-if="addResult.already.length" class="wq-muted block">{{ t("people.already") }}：{{ addResult.already.join("、") }}</text>
        <text v-if="addResult.notfound.length" class="wq-error">{{ t("people.notfound") }}：{{ addResult.notfound.join("、") }}</text>
      </view>
    </view>

    <!-- AI grouping -->
    <view v-if="panel === 'ai'" class="wq-card ai">
      <text class="wq-label">{{ t("people.aiHint") }}</text>
      <view class="wq-row">
        <input v-model="aiReq" class="wq-input grow" :placeholder="t('people.aiPlaceholder')" @confirm="askAi" />
        <view class="wq-btn dark" :class="{ disabled: busy }" @click="askAi">{{ busy ? t("people.aiBusy") : t("people.aiGo") }}</view>
      </view>
      <text v-if="aiError" class="wq-error">{{ aiError }}</text>
      <template v-if="plan">
        <text class="explain">{{ plan.explanation }}</text>
        <text v-if="!plan.has_grades" class="wq-muted block">{{ t("people.noGrades") }}</text>
        <view class="plan">
          <view v-for="(g, gi) in plan.groups" :key="gi" class="pg">
            <input v-model="g.name" class="pg-name" />
            <text v-for="n in g.names" :key="n" class="pg-m">{{ n }}</text>
            <text v-if="g.note" class="wq-muted">{{ g.note }}</text>
          </view>
        </view>
        <view class="wq-row actions">
          <view class="wq-btn primary" :class="{ disabled: busy }" @click="apply(true)">{{ plan.existing ? t("people.applyReplace") : t("people.apply") }}</view>
          <view v-if="plan.existing" class="wq-btn" :class="{ disabled: busy }" @click="apply(false)">{{ t("people.applyKeep") }}</view>
          <view class="wq-btn" @click="plan = null">{{ t("common.cancel") }}</view>
        </view>
      </template>
    </view>

    <view class="wq-tabs">
      <view class="wq-tab" :class="{ on: view === 'members' }" @click="view = 'members'">{{ t("people.members") }} · {{ members.length }}</view>
      <view class="wq-tab" :class="{ on: view === 'groups' }" @click="view = 'groups'">{{ t("people.groups") }} · {{ groups.length }}</view>
    </view>

    <text v-if="loading && !members.length" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error" class="wq-error">{{ errorText(error) }}</text>

    <!-- members -->
    <template v-else-if="view === 'members'">
      <view class="wq-row filters">
        <input v-model="q" class="wq-input search" :placeholder="t('people.search')" />
        <picker v-if="groups.length" :range="groupOptions" range-key="name" @change="(e: any) => (groupFilter = groupOptions[e.detail.value].id)">
          <view class="wq-input picker">{{ groupOptions.find((g) => g.id === groupFilter)?.name }} ▾</view>
        </picker>
      </view>
      <view class="table">
        <view v-for="u in shown" :key="u.id" class="person">
          <view class="wq-avatar">{{ initials(u.fullname) }}</view>
          <view class="p-main">
            <text class="p-name">{{ u.fullname }}</text>
            <text v-if="u.email" class="wq-muted">{{ u.email }}</text>
          </view>
          <text class="wq-tag" :class="u.role === 'teacher' ? 'accent' : u.role === 'assistant' ? 'info' : ''">{{ t("people.role." + u.role) }}</text>
          <text class="p-groups wq-muted">{{ groupNames(u) }}</text>
          <text v-if="canManage" class="wq-muted p-last">{{ u.lastaccess ? formatDate(u.lastaccess) : t("people.never") }}</text>
          <text v-if="canManage && u.role === 'student'" class="wq-link danger" @click="remove(u)">{{ t("people.remove") }}</text>
        </view>
        <view v-if="!shown.length" class="wq-empty">{{ t("people.noMatch") }}</view>
      </view>
    </template>

    <!-- groups -->
    <template v-else>
      <view v-if="canManage" class="wq-row new-group">
        <input v-model="newGroup" class="wq-input grow" :placeholder="t('people.newGroupHint')" @confirm="createGroup" />
        <view class="wq-btn" :class="{ disabled: !newGroup.trim() || busy }" @click="createGroup">＋ {{ t("people.newGroup") }}</view>
      </view>
      <view v-if="!groups.length" class="wq-empty">{{ canManage ? t("people.noGroupsTeacher") : t("people.noGroups") }}</view>
      <text v-if="canManage && ungrouped.length && groups.length" class="wq-muted block ungrouped">{{ t("people.ungrouped", { n: ungrouped.length }) }}：{{ ungrouped.map((u) => u.fullname).join("、") }}</text>
      <view class="groups">
        <view v-for="g in groups" :key="g.id" class="wq-card group" :class="{ mine: g.members.includes(me) }">
          <view class="g-head">
            <input v-if="renaming === g.id" v-model="renameText" class="wq-input" @confirm="rename(g)" @blur="rename(g)" />
            <text v-else class="g-name">{{ g.name }}</text>
            <text v-if="g.members.includes(me)" class="wq-tag ok">{{ t("people.myGroup") }}</text>
            <text class="wq-muted">{{ t("people.count", { n: g.members.length }) }}</text>
          </view>
          <view class="g-members">
            <text v-for="uid in g.members" :key="uid" class="chip">{{ nameOf(uid) }}</text>
            <text v-if="!g.members.length" class="wq-muted">{{ t("people.emptyGroup") }}</text>
          </view>
          <view v-if="canManage" class="wq-row g-actions">
            <text class="wq-link" @click="startMembers(g)">{{ t("people.editMembers") }}</text>
            <text class="wq-link" @click="startRename(g)">{{ t("people.rename") }}</text>
            <text class="wq-link danger" @click="removeGroup(g)">{{ t("common.delete") }}</text>
          </view>
          <view v-if="picking === g.id" class="pick">
            <view v-for="u in students" :key="u.id" class="pick-row" @click="togglePick(u.id)">
              <text class="box" :class="{ on: picked.includes(u.id) }">{{ picked.includes(u.id) ? "✓" : "" }}</text>
              <text>{{ u.fullname }}</text>
              <text v-if="otherGroup(u, g)" class="wq-muted">（{{ otherGroup(u, g) }}）</text>
            </view>
            <view class="wq-row">
              <view class="wq-btn primary small" :class="{ disabled: busy }" @click="saveMembers(g)">{{ t("common.save") }}</view>
              <view class="wq-btn small" @click="picking = 0">{{ t("common.cancel") }}</view>
            </view>
          </view>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { ApiError, user } from "../../api";
import { confirmAction, courseApi, type Group, initials, type Member, type PlanGroup } from "../../courseApi";
import { errorText, formatDate, t } from "../../i18n";

const props = defineProps<{ courseId: number }>();
const members = ref<Member[]>([]);
const groups = ref<Group[]>([]);
const canManage = ref(false);
const loading = ref(true);
const error = ref("");
const view = ref<"members" | "groups">("members");
const panel = ref<"" | "add" | "ai">("");
const q = ref("");
const groupFilter = ref(0);
const busy = ref(false);
const addText = ref("");
const addResult = ref<{ added: string[]; already: string[]; notfound: string[] } | null>(null);
const aiReq = ref("");
const aiError = ref("");
const plan = ref<{ explanation: string; groups: PlanGroup[]; has_grades: boolean; existing: number } | null>(null);
const newGroup = ref("");
const renaming = ref(0);
const renameText = ref("");
const picking = ref(0);
const picked = ref<number[]>([]);

const me = computed(() => user.value?.id || 0);
const students = computed(() => members.value.filter((u) => u.role === "student"));
const ungrouped = computed(() => students.value.filter((u) => !groups.value.some((g) => g.members.includes(u.id))));
const groupOptions = computed(() => [{ id: 0, name: t("people.allGroups") }, ...groups.value.map((g) => ({ id: g.id, name: g.name }))]);
const shown = computed(() => {
  const s = q.value.trim().toLowerCase();
  return members.value.filter((u) =>
    (!s || u.fullname.toLowerCase().includes(s) || u.email.toLowerCase().includes(s)) &&
    (!groupFilter.value || u.groups.includes(groupFilter.value)));
});
const nameOf = (uid: number) => members.value.find((u) => u.id === uid)?.fullname || `#${uid}`;
const groupNames = (u: Member) => groups.value.filter((g) => g.members.includes(u.id)).map((g) => g.name).join("、");
const otherGroup = (u: Member, g: Group) => groups.value.filter((x) => x.id !== g.id && x.members.includes(u.id)).map((x) => x.name).join("、");
const fail = (e: unknown) => uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const r = await courseApi.people(props.courseId);
    members.value = r.members;
    groups.value = r.groups;
    canManage.value = r.can_manage;
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

async function guarded(fn: () => Promise<void>) {
  busy.value = true;
  try {
    await fn();
  } catch (e) {
    fail(e);
  } finally {
    busy.value = false;
  }
}

const addPeople = () => guarded(async () => {
  const ids = addText.value.split(/[\s,，;；]+/).map((s) => s.trim()).filter(Boolean);
  addResult.value = await courseApi.enrol(props.courseId, ids);
  if (addResult.value.added.length) {
    addText.value = addResult.value.notfound.join("\n");
    await load();
  }
});
async function remove(u: Member) {
  if (!(await confirmAction(t("people.confirmRemove", { name: u.fullname }), t("people.remove"), t("common.cancel")))) return;
  await guarded(async () => {
    await courseApi.unenrol(props.courseId, u.id);
    await load();
  });
}

async function askAi() {
  aiError.value = "";
  busy.value = true;
  try {
    plan.value = await courseApi.aiGroups(props.courseId, aiReq.value);
  } catch (e) {
    aiError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    busy.value = false;
  }
}
const apply = (replace: boolean) => guarded(async () => {
  if (!plan.value) return;
  const r = await courseApi.applyGroups(props.courseId, plan.value.groups.map((g) => ({ name: g.name, members: g.members })), replace);
  groups.value = r.groups;
  plan.value = null;
  panel.value = "";
  view.value = "groups";
  await load();
});

const createGroup = () => guarded(async () => {
  if (!newGroup.value.trim()) return;
  groups.value = (await courseApi.addGroup(props.courseId, newGroup.value.trim())).groups;
  newGroup.value = "";
});
function startRename(g: Group) {
  renaming.value = g.id;
  renameText.value = g.name;
}
const rename = (g: Group) => guarded(async () => {
  if (renaming.value !== g.id) return;
  renaming.value = 0;
  if (renameText.value.trim() && renameText.value.trim() !== g.name) {
    groups.value = (await courseApi.editGroup(props.courseId, g.id, { name: renameText.value.trim() })).groups;
  }
});
async function removeGroup(g: Group) {
  if (!(await confirmAction(t("people.confirmDeleteGroup", { name: g.name }), t("common.delete"), t("common.cancel")))) return;
  await guarded(async () => {
    groups.value = (await courseApi.deleteGroup(props.courseId, g.id)).groups;
    await load();
  });
}
function startMembers(g: Group) {
  picking.value = g.id;
  picked.value = [...g.members];
}
function togglePick(uid: number) {
  picked.value = picked.value.includes(uid) ? picked.value.filter((x) => x !== uid) : [...picked.value, uid];
}
const saveMembers = (g: Group) => guarded(async () => {
  groups.value = (await courseApi.editGroup(props.courseId, g.id, { members: picked.value })).groups;
  picking.value = 0;
  await load();
});

onMounted(load);
defineExpose({ load });
</script>

<style scoped>
.actions { margin-top: 12px; }
.grow { flex: 1; min-width: 200px; }
.block { display: block; }
.result { margin-top: 10px; display: flex; flex-direction: column; gap: 4px; }
.ok { color: var(--wq-ok); }
.ai .explain { display: block; margin: 12px 0 4px; color: var(--wq-ink); }
.plan { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; margin-top: 10px; }
.pg { border: 1px solid var(--wq-line); border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 4px; background: #fafbfb; }
.pg-name { font-weight: 700; color: var(--wq-ink); border: 0; border-bottom: 1px dashed var(--wq-line); background: transparent; font-size: 15px; }
.pg-m { font-size: 14px; }
.filters { margin-bottom: 10px; }
.search { flex: 1; min-width: 200px; }
.picker { display: flex; align-items: center; cursor: pointer; min-width: 140px; }
.table { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; overflow: hidden; }
.person { display: flex; align-items: center; gap: 12px; padding: 10px 16px; border-top: 1px solid var(--wq-line); flex-wrap: wrap; }
.person:first-child { border-top: 0; }
.p-main { flex: 1; min-width: 160px; display: flex; flex-direction: column; }
.p-name { color: var(--wq-ink); font-weight: 600; }
.p-groups { min-width: 90px; }
.p-last { min-width: 120px; }
.new-group { margin-bottom: 12px; }
.ungrouped { margin-bottom: 10px; }
.groups { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.group { margin-bottom: 0; }
.group.mine { border-color: var(--wq-ok); }
.g-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.g-name { flex: 1; font-weight: 700; color: var(--wq-ink); font-size: 16px; }
.g-members { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { background: #eef2f1; border-radius: 999px; padding: 2px 10px; font-size: 13px; }
.g-actions { margin-top: 10px; gap: 14px; }
.pick { margin-top: 10px; border-top: 1px solid var(--wq-line); padding-top: 8px; display: flex; flex-direction: column; gap: 4px; max-height: 320px; overflow: auto; }
.pick-row { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 3px 0; font-size: 14px; }
.box { width: 18px; height: 18px; border: 1px solid var(--wq-line); border-radius: 4px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; }
.box.on { background: var(--wq-ink); color: #fff; border-color: var(--wq-ink); }
</style>
