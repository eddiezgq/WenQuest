<template>
  <AppShell nav="courses" :course="d" tab="quizzes" :crumb="heading" :title="heading">
    <text v-if="loading" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error" class="wq-error">{{ errorText(error) }}</text>
    <view v-else class="qe">
      <view class="wq-head">
        <text class="wq-h1">{{ heading }}</text>
        <view class="wq-row">
          <view class="wq-btn primary" :class="{ disabled: saving }" @click="save">{{ saving ? t("common.saving") : t("common.save") }}</view>
          <view class="wq-btn" @click="back">{{ t("common.cancel") }}</view>
        </view>
      </view>
      <text v-if="formError" class="wq-error top">{{ formError }}</text>

      <!-- settings -->
      <view class="wq-card">
        <text class="wq-label">{{ t("edit.name") }}</text>
        <input v-model="q.name" class="wq-input" :placeholder="t('edit.nameHint.quiz')" />
        <text class="wq-label">{{ t("edit.description") }}</text>
        <textarea v-model="q.intro" class="wq-textarea small" auto-height :maxlength="-1" :placeholder="t('quizEdit.introHint')" />
        <view class="grid">
          <view><text class="wq-label">{{ t("quizEdit.limitMin") }}</text><input v-model.number="limitMin" type="number" class="wq-input" /></view>
          <view><text class="wq-label">{{ t("quiz.attemptsAllowed") }}</text><input v-model.number="q.attempts" type="number" class="wq-input" /></view>
          <view><text class="wq-label">{{ t("work.points") }}</text><input v-model.number="q.grade" type="digit" class="wq-input" /></view>
          <view>
            <text class="wq-label">{{ t("quizEdit.showAnswers") }}</text>
            <picker :range="SHOW" range-key="label" @change="(e: any) => (q.showanswers = SHOW[e.detail.value].key)">
              <view class="wq-input pk">{{ SHOW.find((x) => x.key === q.showanswers)?.label }} ▾</view>
            </picker>
          </view>
        </view>
        <view class="grid two">
          <view>
            <text class="wq-label">{{ t("quiz.opens") }}</text>
            <view class="wq-row">
              <picker mode="date" :value="opens.date" @change="(e: any) => (opens.date = e.detail.value)"><view class="wq-input pk">{{ opens.date || t("quizEdit.now") }}</view></picker>
              <picker v-if="opens.date" mode="time" :value="opens.time" @change="(e: any) => (opens.time = e.detail.value)"><view class="wq-input pk">{{ opens.time }}</view></picker>
              <text v-if="opens.date" class="wq-link" @click="opens.date = ''">✕</text>
            </view>
          </view>
          <view>
            <text class="wq-label">{{ t("quiz.closes") }}</text>
            <view class="wq-row">
              <picker mode="date" :value="closes.date" @change="(e: any) => (closes.date = e.detail.value)"><view class="wq-input pk">{{ closes.date || t("edit.none") }}</view></picker>
              <picker v-if="closes.date" mode="time" :value="closes.time" @change="(e: any) => (closes.time = e.detail.value)"><view class="wq-input pk">{{ closes.time }}</view></picker>
              <text v-if="closes.date" class="wq-link" @click="closes.date = ''">✕</text>
            </view>
          </view>
        </view>
      </view>

      <!-- AI question writer -->
      <view v-if="!locked" class="wq-card ai">
        <view class="wq-row">
          <text class="ai-h">✦ {{ t("quizEdit.ai") }}</text>
          <text class="wq-muted">{{ t("quizEdit.aiHint") }}</text>
        </view>
        <view class="wq-row ai-row">
          <picker :range="chapters" range-key="label" @change="(e: any) => (aiSection = chapters[e.detail.value].number)">
            <view class="wq-input pk">{{ chapters.find((c) => c.number === aiSection)?.label || t("quizEdit.pickChapter") }} ▾</view>
          </picker>
          <input v-model.number="aiCount" type="number" class="wq-input tiny" />
          <text class="wq-muted">{{ t("quizEdit.questions") }}</text>
          <input v-model="aiNote" class="wq-input grow" :placeholder="t('quizEdit.aiNote')" />
          <view class="wq-btn dark" :class="{ disabled: aiBusy || !aiSection }" @click="aiWrite">{{ aiBusy ? t("quizEdit.aiBusy") : t("quizEdit.aiGo") }}</view>
        </view>
        <text v-if="aiError" class="wq-error">{{ aiError }}</text>
      </view>
      <view v-else class="wq-card locked">{{ t("quizEdit.locked") }}</view>

      <!-- questions -->
      <view v-for="(x, qi) in q.questions" :key="qi" class="wq-card qq">
        <view class="wq-row qh">
          <text class="q-no">{{ qi + 1 }}</text>
          <picker v-if="!locked" :range="TYPES" range-key="label" @change="(e: any) => setType(x, TYPES[e.detail.value].key)">
            <text class="wq-tag info">{{ TYPES.find((y) => y.key === x.type)?.label }} ▾</text>
          </picker>
          <text v-else class="wq-tag info">{{ TYPES.find((y) => y.key === x.type)?.label }}</text>
          <text class="wq-muted">{{ t("quizEdit.mark") }}</text>
          <input v-model.number="x.mark" type="digit" class="wq-input tiny" :disabled="locked" />
          <view v-if="!locked" class="q-acts">
            <text v-if="qi > 0" class="wq-link" @click="swap(qi, qi - 1)">↑</text>
            <text v-if="qi < q.questions.length - 1" class="wq-link" @click="swap(qi, qi + 1)">↓</text>
            <text class="wq-link danger" @click="q.questions.splice(qi, 1)">{{ t("common.delete") }}</text>
          </view>
        </view>
        <textarea v-model="x.text" class="wq-textarea small" auto-height :maxlength="-1" :disabled="locked" :placeholder="t('quizEdit.textHint')" />

        <!-- options -->
        <view v-if="x.type === 'single' || x.type === 'multiple'" class="opts">
          <view v-for="(a, ai) in x.answers" :key="ai" class="opt">
            <text class="right" :class="{ on: a.fraction > 0 }" @click="!locked && markRight(x, ai)">{{ a.fraction > 0 ? "✓" : String.fromCharCode(65 + ai) }}</text>
            <input v-model="a.text" class="wq-input grow" :disabled="locked" :placeholder="t('quizEdit.option')" />
            <text v-if="!locked && x.answers.length > 2" class="wq-link danger" @click="x.answers.splice(ai, 1)">✕</text>
          </view>
          <text v-if="!locked" class="wq-link" @click="x.answers.push(blank())">＋ {{ t("quizEdit.addOption") }}</text>
          <text class="wq-muted block">{{ x.type === "single" ? t("quizEdit.singleNote") : t("quizEdit.multiNote") }}</text>
        </view>
        <view v-else-if="x.type === 'truefalse'" class="wq-row">
          <text class="chk" :class="{ on: x.correct }" @click="!locked && (x.correct = true)">{{ x.correct ? "●" : "○" }} {{ t("quiz.true") }}</text>
          <text class="chk" :class="{ on: !x.correct }" @click="!locked && (x.correct = false)">{{ !x.correct ? "●" : "○" }} {{ t("quiz.false") }}</text>
        </view>
        <view v-else class="opts">
          <view v-for="(a, ai) in x.answers" :key="ai" class="opt">
            <text class="wq-muted">{{ x.type === "numerical" ? t("quizEdit.answerNum") : t("quizEdit.accepted") }}</text>
            <input v-model="a.text" class="wq-input grow" :type="x.type === 'numerical' ? 'digit' : 'text'" :disabled="locked" />
            <template v-if="x.type === 'numerical'">
              <text class="wq-muted">±</text>
              <input v-model.number="a.tolerance" type="digit" class="wq-input tiny" :disabled="locked" />
            </template>
            <text v-if="!locked && x.answers.length > 1" class="wq-link danger" @click="x.answers.splice(ai, 1)">✕</text>
          </view>
          <text v-if="!locked && x.type === 'shortanswer'" class="wq-link" @click="x.answers.push({ ...blank(), fraction: 1 })">＋ {{ t("quizEdit.addAccepted") }}</text>
        </view>
        <text class="wq-label">{{ t("quiz.explanation") }}</text>
        <textarea v-model="x.feedback" class="wq-textarea small" auto-height :maxlength="-1" :disabled="locked" />
      </view>

      <view v-if="!locked" class="wq-row add">
        <text class="wq-muted">＋ {{ t("quizEdit.addQuestion") }}</text>
        <text v-for="k in TYPES" :key="k.key" class="add-k" @click="addQuestion(k.key)">{{ k.label }}</text>
      </view>
      <view v-if="q.questions.length" class="wq-row foot">
        <text class="wq-muted">{{ t("quizEdit.total", { n: q.questions.length, m: totalMarks }) }}</text>
        <view class="wq-btn primary" :class="{ disabled: saving }" @click="save">{{ saving ? t("common.saving") : t("common.save") }}</view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { ApiError, token } from "../../api";
import { editApi, type QAnswer, type QuestionDef, type QuizDef } from "../../courseApi";
import { errorText, t } from "../../i18n";
import { type CourseData, loadCourse, units } from "../../store";

defineOptions({ inheritAttrs: false });

const cid = ref(0);
const cmid = ref(0);
const d = ref<CourseData | null>(null);
const loading = ref(true);
const error = ref("");
const saving = ref(false);
const formError = ref("");
const locked = ref(false);
const q = reactive<QuizDef>({ cmid: 0, section: 0, name: "", intro: "", timeopen: 0, timeclose: 0, timelimit: 0, attempts: 1, grade: 100,
  showanswers: "immediately", visible: true, questions: [] });
const limitMin = ref(20);
const opens = reactive({ date: "", time: "08:00" });
const closes = reactive({ date: "", time: "23:59" });
const aiSection = ref(0);
const aiCount = ref(8);
const aiNote = ref("");
const aiBusy = ref(false);
const aiError = ref("");

const TYPES = computed(() => ["single", "multiple", "truefalse", "shortanswer", "numerical"].map((k) => ({
  key: k as QuestionDef["type"], label: t("quiz.type." + (k === "multiple" ? "multi" : k)) })));
const SHOW = computed(() => ["immediately", "afterclose", "never"].map((k) => ({ key: k as QuizDef["showanswers"], label: t("quizEdit.show." + k) })));
const chapters = computed(() => (d.value ? units(d.value).map((s) => ({ number: s.number ?? 0, label: s.name })) : []));
const heading = computed(() => (cmid.value ? t("quizEdit.editTitle") : t("quizEdit.newTitle")));
const totalMarks = computed(() => q.questions.reduce((a, x) => a + (Number(x.mark) || 0), 0));
const pad = (n: number) => String(n).padStart(2, "0");
const blank = (): QAnswer => ({ text: "", fraction: 0, feedback: "", tolerance: 0 });
/** Questions are edited as plain text (LaTeX stays as typed) and saved as simple HTML paragraphs. */
const plain = (h: string) => String(h || "").replace(/<br\s*\/?>/gi, "\n").replace(/<\/p>\s*<p[^>]*>/gi, "\n\n").replace(/<[^>]+>/g, "")
  .replace(/&nbsp;/g, " ").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#0?39;/g, "'").replace(/&amp;/g, "&").trim();
const esc = (x: string) => x.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const html = (x: string) => (x.trim() ? x.trim().split(/\n\s*\n/).map((p) => `<p>${esc(p).replace(/\n/g, "<br>")}</p>`).join("") : "");
const toPlain = (x: QuestionDef): QuestionDef => ({ ...x, text: plain(x.text), feedback: plain(x.feedback),
  answers: x.answers.map((a) => ({ ...a, text: plain(a.text), feedback: plain(a.feedback) })) });

function toParts(ts: number, target: { date: string; time: string }) {
  if (!ts) { target.date = ""; return; }
  const x = new Date(ts * 1000);
  target.date = `${x.getFullYear()}-${pad(x.getMonth() + 1)}-${pad(x.getDate())}`;
  target.time = `${pad(x.getHours())}:${pad(x.getMinutes())}`;
}
function fromParts(p: { date: string; time: string }): number {
  if (!p.date) return 0;
  const [y, m, dd] = p.date.split("-").map(Number);
  const [h, mi] = p.time.split(":").map(Number);
  return Math.round(new Date(y, m - 1, dd, h, mi).getTime() / 1000);
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    d.value = await loadCourse(cid.value);
    if (cmid.value) {
      const c = await editApi.content(cid.value, cmid.value);
      if (c.quiz) {
        Object.assign(q, { ...c.quiz, intro: plain(c.quiz.intro), visible: !!c.quiz.visible, questions: c.quiz.questions.map(toPlain) });
        limitMin.value = Math.round((c.quiz.timelimit || 0) / 60);
        toParts(c.quiz.timeopen, opens);
        toParts(c.quiz.timeclose, closes);
        locked.value = !!c.quiz.hasattempts;
      }
    }
    aiSection.value = q.section || chapters.value[0]?.number || 0;
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

function addQuestion(type: QuestionDef["type"]) {
  const x: QuestionDef = { type, text: "", answers: [], correct: true, feedback: "", mark: type === "numerical" ? 2 : 1 };
  setType(x, type);
  q.questions.push(x);
}
function setType(x: QuestionDef, type: QuestionDef["type"]) {
  x.type = type;
  if (type === "single" || type === "multiple") {
    if (x.answers.length < 2) x.answers = [blank(), blank(), blank(), blank()];
  } else if (type === "truefalse") {
    x.answers = [];
  } else {
    x.answers = [{ ...blank(), fraction: 1 }];
  }
}
function markRight(x: QuestionDef, i: number) {
  if (x.type === "single") x.answers.forEach((a, j) => (a.fraction = j === i ? 1 : 0));
  else x.answers[i].fraction = x.answers[i].fraction > 0 ? 0 : 1;
}
function swap(i: number, j: number) {
  const a = q.questions;
  [a[i], a[j]] = [a[j], a[i]];
}

async function aiWrite() {
  aiBusy.value = true;
  aiError.value = "";
  try {
    const r = await editApi.aiQuiz(cid.value, aiSection.value, Math.max(1, Math.min(30, Number(aiCount.value) || 8)),
      ["single", "multiple", "truefalse", "shortanswer", "numerical"], aiNote.value);
    q.questions.push(...r.questions.map(toPlain));
    if (!q.name) q.name = t("quizEdit.defaultName", { name: r.title });
    if (!q.section) q.section = aiSection.value;
  } catch (e) {
    aiError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    aiBusy.value = false;
  }
}

function problems(): string {
  if (!q.name.trim()) return t("error.name_required");
  if (!cmid.value && !q.questions.length) return t("error.no_questions");
  for (const [i, x] of q.questions.entries()) {
    const n = i + 1;
    if (!x.text.trim()) return t("quizEdit.needText", { n });
    const filled = x.answers.filter((a) => String(a.text).trim());
    if ((x.type === "single" || x.type === "multiple") && (filled.length < 2 || !filled.some((a) => a.fraction > 0)))
      return t("quizEdit.needRight", { n });
    if ((x.type === "shortanswer" || x.type === "numerical") && !filled.length) return t("quizEdit.needAnswer", { n });
  }
  return "";
}

async function save() {
  const p = problems();
  if (p) return (formError.value = p);
  saving.value = true;
  formError.value = "";
  try {
    const body: QuizDef = {
      ...q, cmid: cmid.value, section: q.section || aiSection.value, intro: html(q.intro),
      timelimit: Math.max(0, Number(limitMin.value) || 0) * 60, timeopen: fromParts(opens), timeclose: fromParts(closes),
      attempts: Number(q.attempts) || 0, grade: Number(q.grade) || 100, keep_questions: locked.value,
      questions: locked.value ? [] : q.questions.map((x) => ({ ...x, mark: Number(x.mark) || 1, text: html(x.text), feedback: html(x.feedback),
        answers: x.answers.filter((a) => String(a.text).trim()).map((a) => ({ ...a, feedback: html(a.feedback), tolerance: Number(a.tolerance) || 0,
          text: x.type === "single" || x.type === "multiple" ? html(String(a.text)) : String(a.text).trim() })) })),
    };
    const r = await editApi.saveQuiz(cid.value, body);
    await loadCourse(cid.value, true);
    uni.showToast({ title: t("work.saved"), icon: "none" });
    uni.redirectTo({ url: `/pages/activity/activity?id=${r.cmid}&course=${cid.value}` });
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    saving.value = false;
  }
}
function back() {
  if (getCurrentPages().length > 1) uni.navigateBack();
  else uni.redirectTo({ url: `/pages/course/course?id=${cid.value}&tab=quizzes` });
}

onLoad((x: any) => {
  cid.value = Number(x?.course || 0);
  cmid.value = Number(x?.cmid || 0);
  q.section = Number(x?.section || 0);
});
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  if (loading.value) load();
});
</script>

<style scoped>
.qe { max-width: 1000px; }
.top { margin-bottom: 10px; }
.grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.pk { display: flex; align-items: center; min-width: 110px; cursor: pointer; }
.small { min-height: 60px; }
.ai { border-left: 4px solid var(--wq-ink); }
.ai-h { font-weight: 700; color: var(--wq-ink); }
.ai-row { margin-top: 8px; }
.grow { flex: 1; min-width: 160px; }
.tiny { width: 72px; }
.locked { color: #7a5a00; background: #fff8e0; }
.qq { border-left: 4px solid #cfd8db; }
.qh { margin-bottom: 8px; }
.q-no { width: 28px; height: 28px; border-radius: 50%; background: var(--wq-ink); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; }
.q-acts { margin-left: auto; display: flex; gap: 12px; }
.opts { display: flex; flex-direction: column; gap: 6px; margin: 8px 0; }
.opt { display: flex; align-items: center; gap: 8px; }
.right { width: 28px; height: 28px; border-radius: 50%; border: 1px solid var(--wq-line); display: inline-flex; align-items: center; justify-content: center; cursor: pointer; font-size: 13px; color: var(--wq-muted); flex-shrink: 0; }
.right.on { background: var(--wq-ok); border-color: var(--wq-ok); color: #fff; }
.chk { cursor: pointer; padding: 4px 10px; }
.chk.on { font-weight: 700; color: var(--wq-ink); }
.block { display: block; }
.add { margin: 6px 0 16px; }
.add-k { border: 1px solid var(--wq-line); border-radius: 999px; padding: 3px 12px; font-size: 13px; cursor: pointer; background: #fff; }
.foot { justify-content: space-between; margin-bottom: 30px; }
@media (max-width: 760px) { .grid, .grid.two { grid-template-columns: 1fr 1fr; } }
</style>
