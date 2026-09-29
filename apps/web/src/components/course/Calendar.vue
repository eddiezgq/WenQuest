<template>
  <view>
    <view class="wq-head">
      <text class="wq-h1">{{ t("menu.calendar") }}</text>
      <view class="wq-row">
        <view class="wq-btn small" @click="shift(-1)">‹</view>
        <text class="month">{{ monthLabel }}</text>
        <view class="wq-btn small" @click="shift(1)">›</view>
        <view class="wq-btn small" @click="today">{{ t("cal.today") }}</view>
        <view v-if="canAdd && !adding" class="wq-btn primary small" @click="startAdd">＋ {{ t("cal.add") }}</view>
      </view>
    </view>

    <view v-if="adding" class="wq-card">
      <text class="wq-label">{{ t("cal.name") }}</text>
      <input v-model="form.name" class="wq-input" :placeholder="t('cal.nameHint')" />
      <view class="g3">
        <view><text class="wq-label">{{ t("online.date") }}</text>
          <picker mode="date" :value="form.date" @change="(e: any) => (form.date = e.detail.value)"><view class="wq-input pk">{{ form.date }}</view></picker></view>
        <view><text class="wq-label">{{ t("online.time") }}</text>
          <picker mode="time" :value="form.time" @change="(e: any) => (form.time = e.detail.value)"><view class="wq-input pk">{{ form.time }}</view></picker></view>
        <view><text class="wq-label">{{ t("online.duration") }}</text><input v-model.number="form.duration" type="number" class="wq-input" /></view>
      </view>
      <text class="wq-label">{{ t("online.notes") }}</text>
      <input v-model="form.description" class="wq-input" />
      <text v-if="formError" class="wq-error">{{ formError }}</text>
      <view class="wq-row acts">
        <view class="wq-btn primary" :class="{ disabled: saving }" @click="save">{{ t("common.save") }}</view>
        <view class="wq-btn" @click="adding = false">{{ t("common.cancel") }}</view>
      </view>
    </view>

    <text v-if="error" class="wq-error">{{ errorText(error) }}</text>
    <view class="cal">
      <view class="cal-grid">
        <text v-for="w in weekNames" :key="w" class="wd">{{ w }}</text>
        <view v-for="c in cells" :key="c.key" class="day" :class="{ other: !c.inMonth, today: c.isToday, pick: c.key === picked }" @click="picked = c.key">
          <text class="d-n">{{ c.day }}</text>
          <view class="dots">
            <text v-for="e in c.events.slice(0, 3)" :key="e.id" class="ev" :class="evClass(e)">{{ e.name }}</text>
            <text v-if="c.events.length > 3" class="more">+{{ c.events.length - 3 }}</text>
          </view>
        </view>
      </view>
      <view class="agenda">
        <text class="a-h">{{ pickedLabel }}</text>
        <text v-if="loading" class="wq-muted">{{ t("common.loading") }}</text>
        <view v-else-if="!pickedEvents.length" class="wq-muted">{{ t("cal.nothing") }}</view>
        <view v-for="e in pickedEvents" :key="e.id" class="item" :class="evClass(e)">
          <view class="i-top">
            <text class="i-time">{{ timeOf(e) }}</text>
            <text v-if="!courseId && e.course" class="wq-tag">{{ e.course }}</text>
          </view>
          <text class="i-name" :class="{ link: !!e.cmid }" @click="openEvent(e)">{{ e.name }}</text>
          <view v-if="e.description" class="i-desc"><MathContent :html="e.description" /></view>
          <text v-if="e.can_delete" class="wq-link danger" @click="remove(e)">{{ t("common.delete") }}</text>
        </view>
        <text class="a-h up">{{ t("cal.upcoming") }}</text>
        <view v-for="e in upcoming" :key="'u' + e.id" class="up-row" @click="pickEvent(e)">
          <text class="u-d">{{ md(e.start) }}</text><text class="u-n">{{ e.name }}</text>
        </view>
        <text v-if="!upcoming.length" class="wq-muted">{{ t("cal.noUpcoming") }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import MathContent from "../MathContent.vue";
import { ApiError } from "../../api";
import { type CalEvent, confirmAction, workApi } from "../../courseApi";
import { errorText, t } from "../../i18n";

const props = defineProps<{ courseId?: number }>();
const courseId = computed(() => props.courseId || 0);
const pad = (n: number) => String(n).padStart(2, "0");
const keyOf = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const base = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
const picked = ref(keyOf(new Date()));
const events = ref<CalEvent[]>([]);
const canAdd = ref(false);
const loading = ref(true);
const error = ref("");
const adding = ref(false);
const saving = ref(false);
const formError = ref("");
const form = reactive({ name: "", date: keyOf(new Date()), time: "09:00", duration: 60, description: "" });

const weekNames = computed(() => t("online.week").split(",").slice(1).concat(t("online.week").split(",")[0]));
const monthLabel = computed(() => t("cal.month", { y: base.value.getFullYear(), m: base.value.getMonth() + 1 }));
const range = computed(() => {
  const first = new Date(base.value);
  const offset = (first.getDay() + 6) % 7;          // weeks start on Monday
  const start = new Date(first.getFullYear(), first.getMonth(), 1 - offset);
  return { start, end: new Date(start.getFullYear(), start.getMonth(), start.getDate() + 42) };
});
const byDay = computed(() => {
  const m = new Map<string, CalEvent[]>();
  for (const e of events.value) {
    const k = keyOf(new Date(e.start * 1000));
    m.set(k, [...(m.get(k) || []), e]);
  }
  return m;
});
const cells = computed(() => {
  const out = [];
  const tk = keyOf(new Date());
  for (let i = 0; i < 42; i++) {
    const d = new Date(range.value.start.getFullYear(), range.value.start.getMonth(), range.value.start.getDate() + i);
    const k = keyOf(d);
    out.push({ key: k, day: d.getDate(), inMonth: d.getMonth() === base.value.getMonth(), isToday: k === tk, events: byDay.value.get(k) || [] });
  }
  return out;
});
const pickedEvents = computed(() => byDay.value.get(picked.value) || []);
const pickedLabel = computed(() => {
  const [y, m, d] = picked.value.split("-").map(Number);
  const w = t("online.week").split(",")[new Date(y, m - 1, d).getDay()];
  return `${m}/${d} ${w}`;
});
const upcoming = computed(() => events.value.filter((e) => e.start * 1000 >= Date.now()).slice(0, 8));
const md = (ts: number) => { const d = new Date(ts * 1000); return `${d.getMonth() + 1}/${d.getDate()}`; };
function timeOf(e: CalEvent) {
  const s = new Date(e.start * 1000);
  const hm = (d: Date) => `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  return e.duration ? `${hm(s)}–${hm(new Date((e.start + e.duration) * 1000))}` : hm(s);
}
function evClass(e: CalEvent) {
  if (/腾讯会议|Zoom|在线课堂/.test(e.name)) return "k-online";
  if (e.module === "assign") return "k-assign";
  if (e.module === "quiz") return "k-quiz";
  return e.type === "user" ? "k-user" : "k-course";
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const r = await workApi.calendar(Math.floor(range.value.start.getTime() / 1000), Math.floor(range.value.end.getTime() / 1000), courseId.value);
    events.value = r.events;
    canAdd.value = r.can_add;
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}
function shift(n: number) {
  base.value = new Date(base.value.getFullYear(), base.value.getMonth() + n, 1);
  load();
}
function today() {
  base.value = new Date(new Date().getFullYear(), new Date().getMonth(), 1);
  picked.value = keyOf(new Date());
  load();
}
function pickEvent(e: CalEvent) { picked.value = keyOf(new Date(e.start * 1000)); }
function openEvent(e: CalEvent) {
  if (e.cmid) uni.navigateTo({ url: `/pages/activity/activity?id=${e.cmid}&course=${e.course_id}` });
}
function startAdd() {
  Object.assign(form, { name: "", date: picked.value, time: "09:00", duration: 60, description: "" });
  formError.value = "";
  adding.value = true;
}
async function save() {
  if (!form.name.trim()) return (formError.value = t("error.name_required"));
  const [y, m, d] = form.date.split("-").map(Number);
  const [h, mi] = form.time.split(":").map(Number);
  saving.value = true;
  try {
    await workApi.addEvent(courseId.value, { name: form.name, timestart: Math.round(new Date(y, m - 1, d, h, mi).getTime() / 1000),
      duration: Number(form.duration) || 0, description: form.description });
    adding.value = false;
    await load();
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    saving.value = false;
  }
}
async function remove(e: CalEvent) {
  if (!(await confirmAction(t("cal.confirmDelete", { name: e.name }), t("common.delete"), t("common.cancel")))) return;
  try {
    await workApi.deleteEvent(e.id);
    await load();
  } catch (err) {
    uni.showToast({ title: errorText(err instanceof ApiError ? err.code : "unknown"), icon: "none" });
  }
}

onMounted(load);
defineExpose({ load });
</script>

<style scoped>
.month { font-weight: 700; color: var(--wq-ink); min-width: 110px; text-align: center; }
.g3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.pk { display: flex; align-items: center; }
.acts { margin-top: 12px; }
.cal { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 16px; align-items: start; }
.cal-grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; overflow: hidden; }
.wd { text-align: center; font-size: 12px; color: var(--wq-muted); padding: 6px 0; background: #f3f5f5; border-bottom: 1px solid var(--wq-line); }
.day { min-height: 92px; border-right: 1px solid #eef1f0; border-bottom: 1px solid #eef1f0; padding: 4px 6px; cursor: pointer; overflow: hidden; }
.day:nth-child(7n) { border-right: 0; }
.day.other { background: #fafbfb; color: #aab5b9; }
.day.pick { box-shadow: inset 0 0 0 2px var(--wq-accent); }
.d-n { font-size: 13px; font-weight: 600; }
.day.today .d-n { background: var(--wq-ink); color: #fff; border-radius: 999px; padding: 0 7px; }
.dots { display: flex; flex-direction: column; gap: 2px; margin-top: 4px; }
.ev { font-size: 11px; line-height: 1.5; padding: 0 4px; border-radius: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; background: #eef2f1; }
.more { font-size: 11px; color: var(--wq-muted); }
.k-online { background: #fde7e5; color: #8c1d18; }
.k-assign { background: #fff3d6; color: #7a5a00; }
.k-quiz { background: #e3eff4; color: #1f5f78; }
.k-course { background: #e3f3ea; color: #1f5c43; }
.agenda { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 14px; display: flex; flex-direction: column; gap: 8px; }
.a-h { font-weight: 700; color: var(--wq-ink); }
.a-h.up { margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--wq-line); }
.item { border-radius: 8px; padding: 8px 10px; display: flex; flex-direction: column; gap: 4px; }
.i-top { display: flex; align-items: center; gap: 8px; }
.i-time { font-family: "IBM Plex Mono", Menlo, monospace; font-size: 12px; }
.i-name { font-weight: 600; }
.i-name.link { cursor: pointer; text-decoration: underline; }
.i-desc { font-size: 13px; }
.up-row { display: flex; gap: 10px; font-size: 13px; cursor: pointer; }
.u-d { width: 44px; color: var(--wq-muted); font-family: "IBM Plex Mono", Menlo, monospace; }
.u-n { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
@media (max-width: 900px) {
  .cal { grid-template-columns: 1fr; }
  .day { min-height: 54px; }
  .ev { display: none; }
  .dots::after { content: ""; }
  .g3 { grid-template-columns: 1fr; }
}
</style>
