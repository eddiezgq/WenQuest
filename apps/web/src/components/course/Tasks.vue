<template>
  <view>
    <view class="wq-head">
      <text class="wq-h1">{{ t("menu.tasks") }}</text>
      <view v-if="teacher" class="wq-row nowrap">
        <view class="wq-btn primary" @click="openIssue">＋ {{ t("tasks.fromBook") }}</view>
      </view>
    </view>
    <text class="lead wq-muted">{{ t("tasks.lead") }}</text>
    <text v-if="loading && !tasks.length" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error" class="wq-error">{{ errorText(error) }}</text>
    <text v-if="factoryError" class="wq-error block">{{ t("tasks.factoryDown") }}</text>
    <view v-if="!loading && !error && !tasks.length" class="wq-empty">
      <text class="block">{{ teacher ? t("tasks.noneTeacher") : t("tasks.none") }}</text>
    </view>

    <!-- the issue dialog -->
    <view v-if="issue" class="wq-card dialog">
      <view class="wq-row d-head"><text class="b">{{ t("tasks.issueTitle") }}</text><text class="wq-link" @click="issue = null">✕</text></view>
      <text v-if="!catalog.connected" class="wq-error block">{{ t("tasks.notConnected") }}</text>
      <text class="wq-label">{{ t("tasks.pick") }}</text>
      <view class="cat">
        <view v-for="c in catalog.tasks" :key="c.book + c.no" class="cat-row" :class="{ on: issue.pick === c }" @click="issue.pick = c">
          <text class="mono">{{ c.code }}</text>
          <view class="grow">
            <text class="b">{{ c.title[lang === "en" ? 1 : 0] }}</text>
            <text class="wq-muted small block">{{ c.book_title }} · {{ c.section }} · {{ c.role?.[lang === "en" ? 1 : 0] }} · {{ c.hours }} {{ t("tasks.hours") }}</text>
          </view>
        </view>
        <text v-if="!catalog.tasks.length" class="wq-muted">{{ t("tasks.noCatalog") }}</text>
      </view>
      <view class="form">
        <view class="field"><text class="wq-label">{{ t("tasks.factory") }}</text>
          <picker :range="catalog.factories.map((f) => f.name)" :value="issue.factoryIndex" @change="(e: any) => (issue!.factoryIndex = Number(e.detail.value))">
            <view class="wq-input">{{ catalog.factories[issue.factoryIndex]?.name || "—" }}</view></picker></view>
        <view class="field"><text class="wq-label">{{ t("tasks.due") }}</text>
          <picker mode="date" :value="issue.due" @change="(e: any) => (issue!.due = e.detail.value)"><view class="wq-input">{{ issue.due || "—" }}</view></picker></view>
        <view class="field"><text class="wq-label">{{ t("tasks.mode") }}</text>
          <view class="wq-row"><text>◉ {{ t("tasks.individual") }}</text><text class="wq-muted">○ {{ t("tasks.group") }}</text></view></view>
        <view class="field"><text class="wq-label">{{ t("tasks.attach") }}</text>
          <text class="small">☑ {{ t("tasks.docs") }}</text></view>
      </view>
      <view class="wq-row end">
        <view class="wq-btn" @click="issue = null">{{ t("common.cancel") }}</view>
        <view class="wq-btn primary" :class="{ disabled: !issue.pick || busy || !catalog.connected }" @click="doIssue">{{ t("tasks.issue") }}</view>
      </view>
      <text v-if="msg" :class="msgOk ? 'ok' : 'wq-error'" class="block">{{ msg }}</text>
    </view>

    <!-- the issued task sheets -->
    <view v-for="x in tasks" :key="x.code" class="wq-card task">
      <view class="wq-row t-head">
        <text class="mono">{{ x.code }}</text>
        <text class="b grow">{{ lang === "en" ? x.title.en : x.title.zh }}</text>
        <text class="wq-muted small">{{ x.factory_name }} · {{ t("tasks.dueOn") }} {{ x.due ? day(x.due) : "—" }}</text>
      </view>

      <template v-if="teacher">
        <view class="wq-row counts">
          <text v-for="k in ORDER" :key="k" class="pill" :class="'s-' + k">{{ t("tasks.st." + k) }} {{ x.counts?.[k] || 0 }}</text>
          <view class="grow"></view>
          <view class="wq-btn" @click="openUrl(x.url)">↗ {{ t("tasks.openFactory") }}</view>
          <view class="wq-btn primary" :class="{ disabled: !x.to_push || busy }" @click="push(x)">{{ t("tasks.push", { n: x.to_push || 0 }) }}</view>
        </view>
        <view class="table">
          <view class="tr th"><text class="c-n">{{ t("grades.student") }}</text><text class="c-s">{{ t("tasks.status") }}</text>
            <text class="c-a">{{ t("tasks.aiOpen") }}</text><text class="c-g">{{ t("tasks.aiScore") }}</text><text class="c-g">{{ t("grades.grade") }}</text><text class="c-o"></text></view>
          <view v-for="s in x.submissions" :key="s.id" class="tr">
            <text class="c-n">{{ s.name }}</text>
            <text class="c-s"><text class="pill" :class="'s-' + s.status">{{ t("tasks.st." + s.status) }}</text></text>
            <text class="c-a">{{ t("tasks.openN", { e: s.open_errors, w: s.open_warnings }) }}</text>
            <text class="c-g">{{ s.suggested ?? "—" }}</text>
            <text class="c-g">{{ s.total ?? "—" }}<text v-if="s.total != null && s.pushed_at" class="ok"> ✓</text></text>
            <text class="c-o wq-link" @click="openUrl(s.review_url)">{{ s.status === "draft" ? "" : t("tasks.review") }}</text>
          </view>
          <text v-if="!x.submissions?.length" class="wq-muted pad">{{ t("tasks.noSubs") }}</text>
        </view>
      </template>

      <template v-else>
        <view class="wq-row counts">
          <text class="pill" :class="'s-' + (x.mine?.status || 'draft')">{{ x.mine ? t("tasks.st." + x.mine.status) : t("tasks.notStarted") }}</text>
          <text v-if="x.mine?.total != null" class="b">{{ x.mine.total }} / 100</text>
          <view class="grow"></view>
          <view class="wq-btn primary" @click="openUrl(x.url)">↗ {{ t("tasks.doIt") }}</view>
        </view>
      </template>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ApiError } from "../../api";
import { type CourseTask, type TaskCatalogItem, taskApi } from "../../courseApi";
import { errorText, locale, t } from "../../i18n";

const ORDER = ["draft", "submitted", "returned", "approved", "graded"];
const props = defineProps<{ courseId: number }>();
const tasks = ref<CourseTask[]>([]);
const teacher = ref(false);
const loading = ref(true);
const error = ref("");
const factoryError = ref(false);
const busy = ref(false);
const msg = ref("");
const msgOk = ref(true);
const lang = locale;
const catalog = ref<{ tasks: TaskCatalogItem[]; factories: { id: string; name: string }[]; connected: boolean }>({ tasks: [], factories: [], connected: true });
const issue = ref<{ pick: TaskCatalogItem | null; factoryIndex: number; due: string } | null>(null);

const day = (ts: number) => new Date(ts * 1000).toISOString().slice(0, 10);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const r = await taskApi.list(props.courseId);
    teacher.value = r.teacher;
    tasks.value = r.tasks;
    factoryError.value = !!r.factory_error;
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}
async function openIssue() {
  msg.value = "";
  try { catalog.value = await taskApi.catalog(); } catch (e) { error.value = e instanceof ApiError ? e.code : "unknown"; return; }
  const fi = catalog.value.factories.findIndex((f) => f.id !== "");
  issue.value = { pick: null, factoryIndex: fi >= 0 ? fi : 0, due: "" };
}
async function doIssue() {
  const i = issue.value;
  if (!i || !i.pick || busy.value) return;
  busy.value = true;
  msg.value = "";
  try {
    const due = i.due ? Math.floor(new Date(i.due + "T23:59:00").getTime() / 1000) : 0;
    await taskApi.issue(props.courseId, { book: i.pick.book, no: i.pick.no, factory: catalog.value.factories[i.factoryIndex]?.id || "", due, section: 0 });
    issue.value = null;
    await load();
  } catch (e) {
    msgOk.value = false;
    msg.value = e instanceof ApiError ? errorText(e.code) : String(e);
  } finally {
    busy.value = false;
  }
}
async function push(x: CourseTask) {
  if (!x.to_push || busy.value) return;
  busy.value = true;
  try {
    const r = await taskApi.push(props.courseId, x.code);
    uni.showToast({ title: t("tasks.pushed", { n: r.pushed }) + (r.failed.length ? t("tasks.pushFailed", { n: r.failed.length }) : ""), icon: "none" });
    await load();
  } catch (e) {
    uni.showToast({ title: e instanceof ApiError ? errorText(e.code) : String(e), icon: "none" });
  } finally {
    busy.value = false;
  }
}
/** The factory is another site: open it in a new tab on the web; in the mini program copy the link. */
function openUrl(url: string) {
  // #ifdef H5
  window.open(url, "_blank");
  // #endif
  // #ifndef H5
  uni.setClipboardData({ data: url });
  uni.showToast({ title: t("tasks.copied"), icon: "none" });
  // #endif
}
onMounted(load);
</script>

<style scoped>
.lead { display: block; margin: 4px 0 12px; }
.block { display: block; }
.b { font-weight: 600; }
.small { font-size: 12px; }
.mono { font-family: ui-monospace, monospace; font-size: 13px; margin-right: 8px; }
.grow { flex: 1; min-width: 0; }
.task { margin-bottom: 12px; }
.t-head { gap: 8px; align-items: baseline; flex-wrap: wrap; }
.counts { gap: 6px; align-items: center; flex-wrap: wrap; margin: 8px 0; }
.pill { padding: 2px 8px; border-radius: 10px; font-size: 12px; background: #eef1f4; }
.s-submitted { background: #fff3cd; } .s-returned { background: #fde2e1; } .s-approved, .s-graded { background: #dff3e6; }
.table { border: 1px solid var(--wq-line, #e3e6ea); border-radius: 8px; overflow: hidden; }
.tr { display: flex; padding: 8px 10px; border-top: 1px solid var(--wq-line, #e3e6ea); align-items: center; font-size: 14px; }
.tr.th { border-top: 0; background: #f6f7f9; font-weight: 600; font-size: 13px; }
.c-n { flex: 2; } .c-s { flex: 1.4; } .c-a { flex: 1.6; font-size: 12px; } .c-g { flex: 0.8; text-align: right; } .c-o { flex: 0.8; text-align: right; }
.pad { display: block; padding: 10px; }
.dialog { margin-bottom: 14px; display: flex; flex-direction: column; gap: 8px; }
.d-head { justify-content: space-between; }
.cat { max-height: 320px; overflow-y: auto; border: 1px solid var(--wq-line, #e3e6ea); border-radius: 8px; }
.cat-row { display: flex; gap: 8px; padding: 8px 10px; border-top: 1px solid var(--wq-line, #e3e6ea); cursor: pointer; }
.cat-row:first-child { border-top: 0; }
.cat-row.on { background: #eaf2fb; }
.form { display: flex; flex-wrap: wrap; gap: 12px; }
.field { display: flex; flex-direction: column; gap: 4px; min-width: 180px; }
.end { justify-content: flex-end; gap: 8px; }
.disabled { opacity: 0.5; pointer-events: none; }
.ok { color: #2e8b57; }
</style>
