<template>
  <AppShell nav="courses" :course="d" tab="quizzes" :crumb="title" :title="t('menu.quizzes')">
    <text v-if="loading && !questions.length" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error && !questions.length" class="wq-error">{{ errorText(error) }}</text>
    <view v-else-if="reviewMode && notAvailable" class="wq-empty">{{ t("quiz.reviewLater") }}</view>

    <view v-else class="quiz">
      <view class="bar">
        <view class="b-left">
          <text class="wq-link" @click="back">‹ {{ quizName }}</text>
          <text v-if="reviewMode && grade !== null" class="score">{{ t("quiz.score") }} <text class="s-n">{{ grade }}</text> / {{ maxGrade }}</text>
        </view>
        <view class="b-right">
          <text v-if="!reviewMode && deadline" class="timer" :class="{ low: left < 300 }">⏱ {{ clock(left) }}</text>
          <text v-if="!reviewMode" class="wq-muted">{{ saveState }}</text>
          <view v-if="!reviewMode" class="wq-btn primary" :class="{ disabled: busy }" @click="askFinish">{{ t("quiz.finish") }}</view>
        </view>
      </view>

      <view class="layout">
        <view class="nav">
          <text class="n-h">{{ t("quiz.nav") }}</text>
          <view class="n-grid">
            <text v-for="(q, i) in questions" :key="q.slot" class="n-cell"
              :class="[{ on: i === index && !showAll }, reviewMode ? q.result : answered(q) ? 'done' : '']" @click="jump(i)">{{ q.number || i + 1 }}</text>
          </view>
          <text class="wq-link" @click="showAll = !showAll">{{ showAll ? t("quiz.oneByOne") : t("quiz.showAll") }}</text>
          <text v-if="!reviewMode" class="wq-muted block">{{ t("quiz.answeredN", { n: answeredCount, m: questions.length }) }}</text>
        </view>

        <view class="main">
          <template v-if="showAll">
            <QuestionCard v-for="q in questions" :key="q.slot" class="spaced" :q="q" :answer="answers[q.slot]" :review="reviewMode" @update="(v) => set(q, v)" />
          </template>
          <template v-else-if="current">
            <QuestionCard :q="current" :answer="answers[current.slot]" :review="reviewMode" @update="(v) => set(current!, v)" />
            <view class="wq-row pager">
              <view class="wq-btn" :class="{ disabled: index === 0 }" @click="jump(index - 1)">‹ {{ t("quiz.prev") }}</view>
              <view v-if="index < questions.length - 1" class="wq-btn dark" @click="jump(index + 1)">{{ t("quiz.next") }} ›</view>
              <view v-else-if="!reviewMode" class="wq-btn primary" @click="askFinish">{{ t("quiz.finish") }}</view>
            </view>
          </template>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import { onHide, onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import QuestionCard from "../../components/work/QuestionCard.vue";
import { ApiError, token } from "../../api";
import { confirmAction, type QuizQuestion, workApi } from "../../courseApi";
import { errorText, t } from "../../i18n";
import { type CourseData, loadCourse } from "../../store";

defineOptions({ inheritAttrs: false });

const aid = ref(0);
const cid = ref(0);
const reviewMode = ref(false);
const d = ref<CourseData | null>(null);
const questions = ref<QuizQuestion[]>([]);
const answers = ref<Record<number, unknown>>({});
const index = ref(0);
const showAll = ref(false);
const loading = ref(true);
const error = ref("");
const busy = ref(false);
const dirty = ref(false);
const saveState = ref("");
const quizName = ref("");
const quizCmid = ref(0);
const deadline = ref(0);
const skew = ref(0);
const now = ref(Date.now() / 1000);
const grade = ref<number | null>(null);
const maxGrade = ref(0);
const notAvailable = ref(false);
let tick: ReturnType<typeof setInterval> | null = null;
let autosave: ReturnType<typeof setInterval> | null = null;

const current = computed(() => questions.value[index.value] || null);
const title = computed(() => quizName.value + (reviewMode.value ? ` · ${t("quiz.review")}` : ""));
const left = computed(() => Math.max(0, Math.round(deadline.value - (now.value + skew.value))));
const answered = (q: QuizQuestion) => {
  const a = answers.value[q.slot];
  return Array.isArray(a) ? a.length > 0 : a !== undefined && a !== "";
};
const answeredCount = computed(() => questions.value.filter(answered).length);
const pad = (n: number) => String(n).padStart(2, "0");
const clock = (s: number) => (s >= 3600 ? `${Math.floor(s / 3600)}:` : "") + `${pad(Math.floor((s % 3600) / 60))}:${pad(s % 60)}`;

async function load(): Promise<void> {
  loading.value = true;
  error.value = "";
  try {
    if (!d.value && cid.value) d.value = await loadCourse(cid.value);
    if (reviewMode.value) {
      const r = await workApi.review(aid.value);
      if (!r.available) { notAvailable.value = true; return; }
      questions.value = r.questions || [];
      grade.value = r.grade ?? null;
      maxGrade.value = r.max_grade || 0;
      quizName.value = r.quiz?.name || "";
      quizCmid.value = r.quiz?.cmid || 0;
      showAll.value = true;
    } else {
      const a = await workApi.attempt(aid.value);
      if (a.state !== "inprogress") {
        reviewMode.value = true;
        return load();
      }
      questions.value = a.questions;
      quizName.value = a.quiz.name;
      quizCmid.value = a.quiz.cmid;
      deadline.value = a.deadline;
      skew.value = a.now - Date.now() / 1000;
      const ans: Record<number, unknown> = {};
      for (const q of a.questions) {
        if (q.kind === "multi") ans[q.slot] = q.options.filter((o) => o.checked).map((o) => o.name);
        else if (q.value) ans[q.slot] = q.value;
      }
      answers.value = ans;
      startTimers();
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

function set(q: QuizQuestion, v: unknown) {
  answers.value = { ...answers.value, [q.slot]: v };
  dirty.value = true;
  saveState.value = t("quiz.unsaved");
}
function jump(i: number) {
  if (i < 0 || i >= questions.value.length) return;
  index.value = i;
  showAll.value = false;
  if (dirty.value) save();
}
async function save(finish = false, timeup = false) {
  if (reviewMode.value) return;
  busy.value = true;
  saveState.value = t("common.saving");
  try {
    const payload = Object.fromEntries(Object.entries(answers.value).map(([k, v]) => [String(k), v]));
    const r = await workApi.saveAttempt(aid.value, payload, finish, timeup);
    dirty.value = false;
    saveState.value = t("quiz.saved");
    if (r.state === "finished") {
      stopTimers();
      reviewMode.value = true;
      await load();
    }
  } catch (e) {
    saveState.value = errorText(e instanceof ApiError ? e.code : "unknown");
    if (e instanceof ApiError && e.code === "attempt_closed") {
      reviewMode.value = true;
      await load();
    }
  } finally {
    busy.value = false;
  }
}
async function askFinish() {
  const missing = questions.value.length - answeredCount.value;
  const msg = missing ? t("quiz.confirmFinishMissing", { n: missing }) : t("quiz.confirmFinish");
  if (await confirmAction(msg, t("quiz.finish"), t("quiz.keepGoing"))) await save(true);
}
function startTimers() {
  stopTimers();
  tick = setInterval(() => {
    now.value = Date.now() / 1000;
    if (deadline.value && left.value <= 0 && !busy.value && !reviewMode.value) {
      stopTimers();
      uni.showToast({ title: t("quiz.timeUp"), icon: "none" });
      save(true, true);
    }
  }, 1000);
  autosave = setInterval(() => dirty.value && !busy.value && save(), 60000);
}
function stopTimers() {
  if (tick) clearInterval(tick);
  if (autosave) clearInterval(autosave);
  tick = autosave = null;
}
function back() {
  if (dirty.value) save();
  if (quizCmid.value) uni.redirectTo({ url: `/pages/activity/activity?id=${quizCmid.value}&course=${cid.value}` });
  else uni.navigateBack();
}

onLoad((q: any) => {
  aid.value = Number(q?.id || 0);
  cid.value = Number(q?.course || 0);
  reviewMode.value = q?.review === "1";
});
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  load();
});
onHide(() => { if (dirty.value) save(); });
onUnmounted(stopTimers);
</script>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; background: #fff; border: 1px solid var(--wq-line);
  border-radius: 10px; padding: 10px 16px; margin-bottom: 14px; position: sticky; top: 0; z-index: 5; }
.b-left, .b-right { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.score { font-weight: 600; color: var(--wq-ink); }
.s-n { font-size: 22px; font-weight: 800; color: var(--wq-ok); font-family: "IBM Plex Mono", Menlo, monospace; }
.timer { font-family: "IBM Plex Mono", Menlo, monospace; font-size: 18px; font-weight: 700; color: var(--wq-ink); }
.timer.low { color: var(--wq-danger); }
.layout { display: grid; grid-template-columns: 200px minmax(0, 1fr); gap: 16px; align-items: start; }
.nav { background: #fff; border: 1px solid var(--wq-line); border-radius: 10px; padding: 12px; position: sticky; top: 70px; display: flex; flex-direction: column; gap: 10px; }
.n-h { font-weight: 700; color: var(--wq-ink); }
.n-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; }
.n-cell { height: 30px; border: 1px solid var(--wq-line); border-radius: 6px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 13px; }
.n-cell.done { background: #e3eff4; border-color: #b9d5e0; }
.n-cell.on { outline: 2px solid var(--wq-accent); }
.n-cell.correct { background: #e3f3ea; border-color: var(--wq-ok); color: var(--wq-ok); }
.n-cell.incorrect { background: #fde7e5; border-color: var(--wq-danger); color: var(--wq-danger); }
.n-cell.partiallycorrect { background: #fff3d6; border-color: var(--wq-accent); }
.spaced { margin-bottom: 14px; display: block; }
.pager { margin-top: 14px; justify-content: space-between; }
.block { display: block; }
@media (max-width: 760px) {
  .layout { grid-template-columns: 1fr; }
  .nav { position: static; }
  .n-grid { grid-template-columns: repeat(8, 1fr); }
}
</style>
