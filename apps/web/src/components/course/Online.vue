<template>
  <view>
    <view class="wq-head">
      <text class="wq-h1">{{ t("menu.online") }}</text>
      <view v-if="canManage && !editing" class="wq-btn primary" @click="startNew">＋ {{ t("online.add") }}</view>
    </view>

    <view v-if="editing" class="wq-card">
      <text class="wq-label">{{ t("online.topic") }}</text>
      <input v-model="form.name" class="wq-input" :placeholder="t('online.topicHint')" />
      <text class="wq-label">{{ t("online.provider") }}</text>
      <view class="wq-row">
        <view v-for="p in PROVIDERS" :key="p" class="wq-btn small" :class="{ dark: form.provider === p }" @click="form.provider = p">{{ t("online.p." + p) }}</view>
      </view>
      <view class="grid">
        <view>
          <text class="wq-label">{{ t("online.date") }}</text>
          <picker mode="date" :value="date" @change="(e: any) => (date = e.detail.value)">
            <view class="wq-input picker">{{ date || t("online.pick") }}</view>
          </picker>
        </view>
        <view>
          <text class="wq-label">{{ t("online.time") }}</text>
          <picker mode="time" :value="time" @change="(e: any) => (time = e.detail.value)">
            <view class="wq-input picker">{{ time || t("online.pick") }}</view>
          </picker>
        </view>
        <view>
          <text class="wq-label">{{ t("online.duration") }}</text>
          <input v-model.number="form.duration" type="number" class="wq-input" />
        </view>
      </view>
      <text class="wq-label">{{ t("online.url") }}</text>
      <input v-model="form.url" class="wq-input" :placeholder="form.provider === 'zoom' ? 'https://zoom.us/j/…' : 'https://meeting.tencent.com/dm/…'" />
      <view class="grid two">
        <view>
          <text class="wq-label">{{ t("online.code") }}</text>
          <input v-model="form.meetingcode" class="wq-input" placeholder="123 456 789" />
        </view>
        <view>
          <text class="wq-label">{{ t("online.passcode") }}</text>
          <input v-model="form.passcode" class="wq-input" />
        </view>
      </view>
      <text class="wq-label">{{ t("online.notes") }}</text>
      <input v-model="form.notes" class="wq-input" :placeholder="t('online.notesHint')" />
      <text v-if="formError" class="wq-error">{{ formError }}</text>
      <view class="wq-row actions">
        <view class="wq-btn primary" :class="{ disabled: saving }" @click="save">{{ saving ? t("common.saving") : t("common.save") }}</view>
        <view class="wq-btn" @click="editing = false">{{ t("common.cancel") }}</view>
        <text class="wq-muted">{{ t("online.calendarNote") }}</text>
      </view>
    </view>

    <text v-if="loading && !items.length" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error" class="wq-error">{{ errorText(error) }}</text>
    <view v-else-if="!items.length" class="wq-empty">{{ canManage ? t("online.noneTeacher") : t("online.none") }}</view>

    <template v-for="block in blocks" :key="block.key">
      <text v-if="block.items.length" class="section">{{ t("online." + block.key) }}</text>
      <view v-for="m in block.items" :key="m.id" class="wq-card meet" :class="block.key">
        <view class="m-when">
          <text class="m-day">{{ day(m.timestart) }}</text>
          <text class="m-time">{{ clock(m.timestart) }}–{{ clock(m.timestart + m.duration * 60) }}</text>
        </view>
        <view class="m-body">
          <view class="wq-row">
            <text class="wq-tag" :class="m.provider === 'zoom' ? 'info' : 'ok'">{{ t("online.p." + m.provider) }}</text>
            <text v-if="block.key === 'live'" class="wq-tag live">● {{ t("online.liveNow") }}</text>
            <text class="m-name">{{ m.name }}</text>
          </view>
          <text v-if="m.meetingcode" class="wq-muted">{{ t("online.code") }}：{{ m.meetingcode }}<text v-if="m.passcode">　{{ t("online.passcode") }}：{{ m.passcode }}</text></text>
          <text v-if="m.notes" class="wq-muted block">{{ m.notes }}</text>
          <view v-if="canManage" class="wq-row m-admin">
            <text class="wq-link" @click="startEdit(m)">{{ t("common.edit") }}</text>
            <text class="wq-link danger" @click="remove(m)">{{ t("common.delete") }}</text>
          </view>
        </view>
        <view class="m-go">
          <view v-if="block.key !== 'past' && m.url" class="wq-btn" :class="block.key === 'live' ? 'primary' : ''" @click="join(m)">{{ t("online.join") }}</view>
          <view v-else-if="block.key !== 'past'" class="wq-btn small" @click="copy(m.meetingcode)">{{ t("online.copyCode") }}</view>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from "vue";
import { ApiError } from "../../api";
import { confirmAction, courseApi, type Meeting, type MeetingIn, openOutside } from "../../courseApi";
import { errorText, t } from "../../i18n";

const props = defineProps<{ courseId: number }>();
const PROVIDERS = ["tencent", "zoom", "other"] as const;
const items = ref<Meeting[]>([]);
const canManage = ref(false);
const loading = ref(true);
const error = ref("");
const editing = ref(false);
const editingId = ref(0);
const saving = ref(false);
const formError = ref("");
const date = ref("");
const time = ref("");
const now = ref(Date.now() / 1000);
const form = reactive<MeetingIn>({ name: "", provider: "tencent", url: "", meetingcode: "", passcode: "", notes: "", timestart: 0, duration: 90 });
let timer: ReturnType<typeof setInterval> | null = null;

const pad = (n: number) => String(n).padStart(2, "0");
const clock = (ts: number) => { const d = new Date(ts * 1000); return `${pad(d.getHours())}:${pad(d.getMinutes())}`; };
function day(ts: number) {
  const d = new Date(ts * 1000);
  const w = t("online.week").split(",")[d.getDay()];
  return `${d.getMonth() + 1}/${d.getDate()} ${w}`;
}

const blocks = computed(() => {
  const live: Meeting[] = [], upcoming: Meeting[] = [], past: Meeting[] = [];
  for (const m of items.value) {
    const end = m.timestart + m.duration * 60;
    // The room opens 15 minutes early.
    if (now.value >= m.timestart - 900 && now.value <= end) live.push(m);
    else if (now.value < m.timestart) upcoming.push(m);
    else past.push(m);
  }
  return [{ key: "live", items: live }, { key: "upcoming", items: upcoming }, { key: "past", items: past.reverse() }];
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const r = await courseApi.meetings(props.courseId);
    items.value = r.meetings;
    canManage.value = r.can_manage;
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

function startNew() {
  Object.assign(form, { name: "", provider: "tencent", url: "", meetingcode: "", passcode: "", notes: "", timestart: 0, duration: 90 });
  const d = new Date(Date.now() + 86400000);
  date.value = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  time.value = "19:00";
  editingId.value = 0;
  formError.value = "";
  editing.value = true;
}
function startEdit(m: Meeting) {
  Object.assign(form, { name: m.name, provider: m.provider, url: m.url, meetingcode: m.meetingcode, passcode: m.passcode, notes: m.notes, duration: m.duration });
  const d = new Date(m.timestart * 1000);
  date.value = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  time.value = clock(m.timestart);
  editingId.value = m.id;
  formError.value = "";
  editing.value = true;
}
async function save() {
  const [y, mo, da] = date.value.split("-").map(Number);
  const [h, mi] = time.value.split(":").map(Number);
  const start = new Date(y, (mo || 1) - 1, da || 1, h || 0, mi || 0).getTime() / 1000;
  if (!form.name.trim() || !date.value || !time.value) return (formError.value = t("online.needTopic"));
  if (!form.url.trim() && !form.meetingcode.trim()) return (formError.value = t("error.meeting_link_required"));
  saving.value = true;
  formError.value = "";
  try {
    const body = { ...form, timestart: Math.round(start), duration: Number(form.duration) || 90 };
    if (editingId.value) await courseApi.editMeeting(props.courseId, editingId.value, body);
    else await courseApi.addMeeting(props.courseId, body);
    editing.value = false;
    await load();
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    saving.value = false;
  }
}
async function remove(m: Meeting) {
  if (!(await confirmAction(t("online.confirmDelete", { name: m.name }), t("common.delete"), t("common.cancel")))) return;
  try {
    await courseApi.deleteMeeting(props.courseId, m.id);
    await load();
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  }
}
const join = (m: Meeting) => openOutside(m.url, t("activity.linkCopied"));
function copy(code: string) {
  uni.setClipboardData({ data: code, success: () => uni.showToast({ title: t("online.copied"), icon: "none" }) });
}

onMounted(() => {
  load();
  timer = setInterval(() => (now.value = Date.now() / 1000), 30000);
});
onUnmounted(() => timer && clearInterval(timer));
defineExpose({ load });
</script>

<style scoped>
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.picker { display: flex; align-items: center; cursor: pointer; }
.actions { margin-top: 14px; }
.section { display: block; font-weight: 700; color: var(--wq-ink); margin: 18px 0 8px; }
.meet { display: flex; align-items: center; gap: 16px; }
.meet.live { border-left: 4px solid var(--wq-danger); }
.meet.past { opacity: .7; }
.m-when { width: 110px; flex-shrink: 0; display: flex; flex-direction: column; }
.m-day { font-weight: 700; color: var(--wq-ink); }
.m-time { font-family: "IBM Plex Mono", Menlo, monospace; font-size: 13px; color: var(--wq-muted); }
.m-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.m-name { font-size: 16px; font-weight: 600; color: var(--wq-ink); }
.block { display: block; }
.m-admin { gap: 14px; }
@media (max-width: 700px) {
  .grid, .grid.two { grid-template-columns: 1fr; }
  .meet { flex-wrap: wrap; }
  .m-go { width: 100%; }
}
</style>
