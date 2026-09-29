<template>
  <view>
    <view class="wq-head">
      <text class="wq-h1">{{ t("edit.title") }}</text>
      <view class="wq-row">
        <view class="wq-btn" @click="settingsOpen = !settingsOpen">⚙ {{ t("edit.settings") }}</view>
        <view class="wq-btn dark" @click="emit('done')">{{ t("edit.done") }}</view>
      </view>
    </view>
    <text v-if="loading && !s" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error && !s" class="wq-error">{{ errorText(error) }}</text>

    <template v-else-if="s">
      <!-- course settings -->
      <view v-if="settingsOpen" class="wq-card">
        <BiField v-model="course.name" :label="t('edit.courseName')" />
        <BiField v-model="course.summary" :label="t('edit.courseSummary')" kind="rich" />
        <view class="wq-row sw" @click="course.visible = !course.visible">
          <text class="switch" :class="{ on: course.visible }" /><text>{{ course.visible ? t("edit.courseVisible") : t("edit.courseHidden") }}</text>
        </view>
        <!-- course catalogue (step C3) -->
        <text class="wq-label">{{ t("listing.title") }}</text>
        <view class="wq-row">
          <text v-for="m in MODES" :key="m" class="lchip" :class="{ on: listing.mode === m }" @click="listing.mode = m">{{ t("listing." + m) }}</text>
        </view>
        <view v-if="listing.mode === 'paid'" class="wq-row lrow">
          <picker :range="['CNY ¥', 'USD $']" @change="(e: any) => (listing.currency = e.detail.value == 1 ? 'USD' : 'CNY')">
            <view class="wq-input pk">{{ listing.currency === 'USD' ? 'USD $' : 'CNY ¥' }} ▾</view>
          </picker>
          <input v-model.number="listing.price" type="digit" class="wq-input price" :placeholder="t('listing.price')" />
          <text class="wq-muted">{{ t("listing.payLater") }}</text>
        </view>
        <template v-if="listing.mode !== 'private'">
          <text class="wq-label">{{ t("listing.blurb") }}</text>
          <textarea v-model="listing.blurb" class="wq-textarea blurb" :placeholder="t('listing.blurbHint')" />
        </template>
        <view class="wq-row acts">
          <view class="wq-btn primary" :class="{ disabled: busy }" @click="saveSettings">{{ t("common.save") }}</view>
          <view class="wq-btn" @click="settingsOpen = false">{{ t("common.cancel") }}</view>
        </view>
      </view>

      <view v-for="(sec, si) in s.sections" :key="sec.id" class="sec" :class="{ hidden: !sec.visible }">
        <view class="s-head">
          <template v-if="renaming === 'sec' + sec.id">
            <view class="grow"><BiField v-model="draftName" /></view>
            <view class="wq-btn primary small" @click="saveSectionName(sec)">{{ t("common.save") }}</view>
            <view class="wq-btn small" @click="renaming = ''">{{ t("common.cancel") }}</view>
          </template>
          <template v-else>
            <text class="s-title">{{ sec.number === 0 ? t("edit.general") : sec.title }}</text>
            <text v-if="!sec.visible" class="wq-tag accent">{{ t("course.teacherOnly") }}</text>
            <view class="s-acts">
              <text v-if="sec.number > 0" class="wq-link" @click="startRename('sec' + sec.id, sec.name)">{{ t("people.rename") }}</text>
              <text v-if="sec.number > 0" class="wq-link" @click="editSummary(sec)">{{ t("edit.summary") }}</text>
              <text v-if="sec.number > 0" class="wq-link" @click="toggleSection(sec)">{{ sec.visible ? t("edit.hide") : t("edit.show") }}</text>
              <text v-if="sec.number > 1" class="wq-link" @click="moveSection(sec, sec.number - 1)">↑</text>
              <text v-if="sec.number > 0 && si < s.sections.length - 1" class="wq-link" @click="moveSection(sec, sec.number + 1)">↓</text>
              <text v-if="sec.number > 0" class="wq-link danger" @click="removeSection(sec)">{{ t("common.delete") }}</text>
            </view>
          </template>
        </view>
        <view v-if="summaryFor === sec.id" class="s-sum">
          <BiField v-model="draftSummary" kind="rich" />
          <view class="wq-row acts">
            <view class="wq-btn primary small" @click="saveSummary(sec)">{{ t("common.save") }}</view>
            <view class="wq-btn small" @click="summaryFor = 0">{{ t("common.cancel") }}</view>
          </view>
        </view>

        <view v-for="(mod, mi) in sec.modules" :key="mod.cmid" class="mod" :class="{ hidden: !mod.visible }">
          <text class="m-icon">{{ icon(mod) }}</text>
          <template v-if="renaming === 'mod' + mod.cmid">
            <view class="grow"><BiField v-model="draftName" /></view>
            <view class="wq-btn primary small" @click="saveModName(mod)">{{ t("common.save") }}</view>
            <view class="wq-btn small" @click="renaming = ''">{{ t("common.cancel") }}</view>
          </template>
          <template v-else>
            <view class="m-main">
              <text class="m-name">{{ mod.title }}</text>
              <text class="wq-muted">{{ t("type." + typeKey(mod)) }}<text v-if="!mod.visible"> · {{ t("course.teacherOnly") }}</text></text>
            </view>
            <view class="m-acts">
              <text v-if="editable(mod)" class="wq-link" @click="openEditor(mod)">{{ t("common.edit") }}</text>
              <text class="wq-link" @click="startRename('mod' + mod.cmid, mod.name)">{{ t("people.rename") }}</text>
              <text class="wq-link" @click="toggleMod(mod)">{{ mod.visible ? t("edit.hide") : t("edit.show") }}</text>
              <text v-if="mi > 0" class="wq-link" @click="moveMod(mod, sec, sec.modules[mi - 1].cmid)">↑</text>
              <text v-if="mi < sec.modules.length - 1" class="wq-link" @click="moveMod(mod, sec, sec.modules[mi + 2]?.cmid || 0)">↓</text>
              <picker :range="targets" range-key="label" @change="(e: any) => moveMod(mod, targets[e.detail.value].section, 0)">
                <text class="wq-link">{{ t("edit.moveTo") }}</text>
              </picker>
              <text class="wq-link danger" @click="removeMod(mod)">{{ t("common.delete") }}</text>
            </view>
          </template>
        </view>
        <view v-if="!sec.modules.length" class="empty">{{ t("edit.emptySection") }}</view>

        <view class="add">
          <text class="wq-muted">＋ {{ t("edit.add") }}</text>
          <text v-for="k in ADD" :key="k" class="add-k" @click="add(sec, k)">{{ t("edit.kind." + k) }}</text>
        </view>
      </view>

      <view class="wq-card new-sec">
        <BiField v-model="newSection" :placeholder="t('edit.newSectionHint')" />
        <view class="wq-btn primary" :class="{ disabled: busy }" @click="addSection">＋ {{ t("edit.addSection") }}</view>
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import BiField from "../edit/BiField.vue";
import { ApiError } from "../../api";
import { type Bi, confirmAction, editApi, type EditModule, type EditSection, pickFiles, type Structure, uploadToSection } from "../../courseApi";
import { errorText, t } from "../../i18n";
import { KIND_ICON } from "../../store";
import { type Listing, accountApi } from "../../accountApi";

const props = defineProps<{ courseId: number }>();
const emit = defineEmits<{ (e: "done"): void; (e: "changed"): void }>();
const ADD = ["page", "file", "assign", "quiz", "url", "forum", "online"];
const s = ref<Structure | null>(null);
const loading = ref(true);
const error = ref("");
const busy = ref(false);
const settingsOpen = ref(false);
const course = ref<{ name: Bi; summary: Bi; visible: boolean }>({ name: { text: "" }, summary: { text: "" }, visible: true });
const MODES: Listing["mode"][] = ["private", "free", "paid"];
const listing = ref<Listing>({ mode: "private", price: 0, currency: "CNY", blurb: "" });
const renaming = ref("");
const draftName = ref<Bi>({ text: "" });
const summaryFor = ref(0);
const draftSummary = ref<Bi>({ text: "" });
const newSection = ref<Bi>({ text: "" });

const targets = computed(() => (s.value?.sections || []).map((x) => ({ label: x.number === 0 ? t("edit.general") : x.title, section: x })));
const typeKey = (m: EditModule) => (["page", "url", "assign", "resource", "quiz", "forum"].includes(m.type) ? m.type : "other");
const icon = (m: EditModule) => (m.type === "resource" ? KIND_ICON[m.file?.kind || "file"] : KIND_ICON[{ page: "reading", url: "link" }[m.type] || m.type]) || "•";
const editable = (m: EditModule) => ["page", "url", "assign", "forum", "quiz"].includes(m.type);
const fail = (e: unknown) => uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });

async function load() {
  loading.value = true;
  error.value = "";
  try {
    s.value = await editApi.structure(props.courseId);
    course.value = { name: { ...s.value.course.name }, summary: { ...s.value.course.summary }, visible: s.value.course.visible };
    accountApi.listing(props.courseId).then((l) => (listing.value = l)).catch(() => null);
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}
async function run(fn: () => Promise<unknown>) {
  busy.value = true;
  try {
    await fn();
    await load();
    emit("changed");
  } catch (e) {
    fail(e);
  } finally {
    busy.value = false;
  }
}

const saveSettings = () => run(async () => {
  await editApi.settings(props.courseId, course.value);
  await accountApi.saveListing(props.courseId, { ...listing.value, price: Number(listing.value.price) || 0 });
  settingsOpen.value = false;
});
function startRename(key: string, name: Bi) {
  renaming.value = key;
  draftName.value = { ...name };
}
const saveSectionName = (sec: EditSection) => run(async () => {
  await editApi.editSection(props.courseId, sec.id, { name: draftName.value });
  renaming.value = "";
});
const saveModName = (m: EditModule) => run(async () => {
  await editApi.editModule(props.courseId, m.cmid, { name: draftName.value });
  renaming.value = "";
});
function editSummary(sec: EditSection) {
  summaryFor.value = sec.id;
  draftSummary.value = { ...sec.summary };
}
const saveSummary = (sec: EditSection) => run(async () => {
  await editApi.editSection(props.courseId, sec.id, { summary: draftSummary.value });
  summaryFor.value = 0;
});
const toggleSection = (sec: EditSection) => run(() => editApi.editSection(props.courseId, sec.id, { visible: !sec.visible }));
const moveSection = (sec: EditSection, to: number) => run(() => editApi.moveSection(props.courseId, sec.id, to));
async function removeSection(sec: EditSection) {
  const n = sec.modules.length;
  if (!(await confirmAction(n ? t("edit.confirmDeleteSectionFull", { name: sec.title, n }) : t("edit.confirmDeleteSection", { name: sec.title }),
    t("common.delete"), t("common.cancel")))) return;
  await run(() => editApi.deleteSection(props.courseId, sec.id, n > 0));
}
const toggleMod = (m: EditModule) => run(() => editApi.editModule(props.courseId, m.cmid, { visible: !m.visible }));
const moveMod = (m: EditModule, sec: EditSection, before: number) => run(() => editApi.moveModule(props.courseId, m.cmid, sec.id, before));
async function removeMod(m: EditModule) {
  if (!(await confirmAction(t("edit.confirmDeleteItem", { name: m.title }), t("common.delete"), t("common.cancel")))) return;
  await run(() => editApi.deleteModule(props.courseId, m.cmid));
}
const addSection = () => run(async () => {
  const name = newSection.value;
  if (!(name.text || name.zh || name.en || "").trim()) throw new ApiError("name_required", 400);
  await editApi.addSection(props.courseId, { name });
  newSection.value = { text: "" };
});

function openEditor(m: EditModule) {
  const page = m.type === "quiz" ? "quiz" : "edit";
  uni.navigateTo({ url: `/pages/edit/${page}?course=${props.courseId}&cmid=${m.cmid}` });
}
async function add(sec: EditSection, kind: string) {
  if (kind === "online") return uni.redirectTo({ url: `/pages/course/course?id=${props.courseId}&tab=online` });
  if (kind === "quiz") return uni.navigateTo({ url: `/pages/edit/quiz?course=${props.courseId}&section=${sec.number}` });
  if (kind === "file") {
    const files = await pickFiles(10);
    if (!files.length) return;
    await run(async () => {
      for (const f of files) await uploadToSection(props.courseId, sec.number, f);
    });
    return;
  }
  uni.navigateTo({ url: `/pages/edit/edit?course=${props.courseId}&section=${sec.number}&type=${kind}` });
}

onMounted(load);
defineExpose({ load });
</script>

<style scoped>
.sec { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; margin-bottom: 14px; overflow: hidden; }
.sec.hidden { border-style: dashed; }
.s-head { display: flex; align-items: center; gap: 10px; padding: 12px 16px; background: #f3f5f5; flex-wrap: wrap; }
.s-title { font-weight: 700; color: var(--wq-ink); font-size: 16px; }
.s-acts, .m-acts { margin-left: auto; display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.s-sum { padding: 10px 16px; border-bottom: 1px solid var(--wq-line); }
.grow { flex: 1; min-width: 240px; }
.mod { display: flex; align-items: center; gap: 12px; padding: 10px 16px; border-top: 1px solid #eef1f0; flex-wrap: wrap; }
.mod.hidden { background: #fbfaf5; }
.m-icon { width: 26px; text-align: center; color: var(--wq-muted); }
.m-main { flex: 1; min-width: 180px; display: flex; flex-direction: column; }
.m-name { color: var(--wq-ink); }
.empty { padding: 10px 16px; color: var(--wq-muted); font-size: 13px; border-top: 1px solid #eef1f0; }
.add { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; padding: 10px 16px; border-top: 1px dashed var(--wq-line); background: #fcfcfb; }
.add-k { border: 1px solid var(--wq-line); border-radius: 999px; padding: 2px 12px; font-size: 13px; cursor: pointer; background: #fff; }
.add-k:hover { border-color: var(--wq-link); color: var(--wq-link); }
.new-sec { display: flex; gap: 12px; align-items: flex-end; }
.new-sec > :first-child { flex: 1; }
.acts { margin-top: 10px; }
.sw { margin-top: 10px; cursor: pointer; }
.switch { width: 38px; height: 22px; border-radius: 999px; background: #cfd8db; position: relative; display: inline-block; }
.switch::after { content: ""; position: absolute; width: 18px; height: 18px; border-radius: 50%; background: #fff; top: 2px; left: 2px; transition: left .15s; }
.switch.on { background: var(--wq-ok); }
.switch.on::after { left: 18px; }
.lchip { padding: 5px 14px; border-radius: 999px; border: 1px solid var(--wq-line); font-size: 13px; cursor: pointer; background: #fff; }
.lchip.on { background: var(--wq-ink); color: #fff; border-color: var(--wq-ink); }
.lrow { margin-top: 8px; }
.lrow .pk { display: flex; align-items: center; min-width: 90px; cursor: pointer; }
.lrow .price { width: 120px; }
.blurb { min-height: 70px; }
</style>
