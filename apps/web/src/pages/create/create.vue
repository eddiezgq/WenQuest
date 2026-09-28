<template>
  <AppShell nav="create" :title="t('create.title')">
    <view class="wrap">
      <text class="h1">{{ t("create.title") }}</text>

      <!-- steps -->
      <view class="steps">
        <view v-for="(k, i) in stepKeys" :key="k" class="step" :class="{ on: step === k, done: stepIndex > i }">
          <text class="num">{{ stepIndex > i ? "✓" : i + 1 }}</text>
          <text class="label">{{ t("gen.step." + k) }}</text>
        </view>
      </view>

      <view v-if="error" class="alert" role="alert">{{ errorText(error) }}</view>

      <!-- 1. materials or a description -->
      <view v-if="step === 'input'" class="modes">
        <view class="mode" :class="{ on: mode === 'upload' }" @click="mode = 'upload'">{{ t("import.modeUpload") }}</view>
        <view class="mode" :class="{ on: mode === 'describe' }" @click="mode = 'describe'">{{ t("import.modeDescribe") }}</view>
      </view>

      <view v-if="step === 'input' && mode === 'upload'" class="card">
        <!-- #ifdef H5 -->
        <!-- a native div: uni-app views do not forward drag-and-drop events -->
        <div class="drop" :class="{ over: dragOver }" @dragover.prevent="dragOver = true" @dragleave="dragOver = false" @drop.prevent="onDrop">
          <text class="drop-title">{{ t("import.drop") }}</text>
          <text class="drop-hint">{{ t("import.dropHint") }}</text>
          <view class="drop-buttons">
            <view class="primary" @click="pick(true)">{{ files.length ? t("import.addMore") : t("import.pickFolder") }}</view>
            <view class="ghost" @click="pick(false)">{{ t("import.pickFiles") }}</view>
          </view>
        </div>
        <view v-if="phase === 'uploading'" class="phase">
          <text>{{ t("import.uploading", { done: uploads.done, total: uploads.total }) }}</text>
          <view class="bar"><view class="fill" :style="{ width: (uploads.total ? (uploads.done / uploads.total) * 100 : 0) + '%' }" /></view>
        </view>
        <view v-if="phase === 'classifying'" class="phase">{{ t("import.classifying") }}</view>

        <view v-if="files.length && phase === 'ready'">
          <view class="table-head">
            <text class="lbl">{{ t("import.summary", { n: files.length, c: chapterCount }) }}</text>
            <text class="link plain" @click="showTable = !showTable">{{ showTable ? t("gen.hideTable") : t("gen.reviewTable") }}</text>
          </view>
          <view v-if="showTable" class="mtable">
            <view class="mrow mhead">
              <text class="c-file">{{ t("import.file") }}</text>
              <text class="c-cat">{{ t("import.category") }}</text>
              <text class="c-ch">{{ t("import.chapter") }}</text>
            </view>
            <view v-for="f in files" :key="f.id" class="mrow" :class="{ unsure: f.confidence === 'unsure' }">
              <view class="c-file">
                <text class="fname">{{ shortPath(f.path) }}</text>
                <text v-if="f.error" class="tag-err">{{ t("import.unreadable") }}</text>
                <text v-else-if="f.confidence === 'unsure'" class="tag-warn">{{ t("import.unsure") }}</text>
                <text v-if="teacherOnly(f.category)" class="tag-lock">🔒 {{ t("import.teacherOnly") }}</text>
              </view>
              <view class="c-cat">
                <select class="msel" v-model="f.category" @change="f.confidence = 'teacher'">
                  <option v-for="(label, key) in categories" :key="key" :value="key">{{ label }}</option>
                </select>
              </view>
              <view class="c-ch">
                <select class="msel" v-model="f.chapter" @change="f.confidence = 'teacher'">
                  <option :value="null">{{ t("import.whole") }}</option>
                  <option v-for="n in 20" :key="n" :value="n">{{ n }}</option>
                </select>
              </view>
            </view>
          </view>
          <view class="row lang-row">
            <text class="lbl">{{ t("create.languages") }}</text>
            <view class="chips">
              <view v-for="lg in ['zh', 'en']" :key="lg" class="chip" :class="{ sel: importLang === lg }"
                    @click="importLang = lg as any">{{ t("create.lang." + lg) }}</view>
            </view>
          </view>
          <view class="go">
            <text class="go-hint">{{ t("gen.oneClickHint") }}</text>
            <view class="actions">
              <view class="ghost" :class="{ disabled: busy }" @click="makeImportOutline">{{ busy ? t("import.planning") : t("gen.outlineFirst") }}</view>
              <view class="primary big" :class="{ disabled: busy }" @click="generateNow">✨ {{ t("gen.oneClick") }}</view>
            </view>
          </view>
        </view>
        <!-- #endif -->
        <!-- #ifndef H5 -->
        <text class="muted-s">{{ t("import.webOnly") }}</text>
        <!-- #endif -->
      </view>

      <view v-if="step === 'input' && mode === 'describe'" class="card">
        <view class="field">
          <text class="lbl">{{ t("create.topic") }} *</text>
          <input class="input" v-model="brief.topic" :placeholder="t('create.topicHint')" />
        </view>
        <view class="field">
          <text class="lbl">{{ t("create.audience") }}</text>
          <input class="input" v-model="brief.audience" :placeholder="t('create.audienceHint')" />
        </view>
        <view class="row">
          <view class="field grow">
            <text class="lbl">{{ t("create.level") }}</text>
            <view class="chips">
              <view v-for="lv in levels" :key="lv" class="chip" :class="{ sel: brief.level === t('create.level.' + lv) }"
                    @click="brief.level = t('create.level.' + lv)">{{ t("create.level." + lv) }}</view>
            </view>
          </view>
          <view class="field grow">
            <text class="lbl">{{ t("create.languages") }}</text>
            <view class="chips">
              <view v-for="lg in langs" :key="lg" class="chip" :class="{ sel: brief.languages === lg }"
                    @click="brief.languages = lg">{{ t("create.lang." + lg) }}</view>
            </view>
          </view>
        </view>
        <view class="row">
          <view class="field">
            <text class="lbl">{{ t("create.sections") }}</text>
            <view class="stepper">
              <view class="sb" @click="brief.sections = Math.max(1, brief.sections - 1)">−</view>
              <text class="sv">{{ brief.sections }}</text>
              <view class="sb" @click="brief.sections = Math.min(12, brief.sections + 1)">＋</view>
            </view>
          </view>
          <view class="field">
            <text class="lbl">{{ t("create.lessons") }}</text>
            <view class="stepper">
              <view class="sb" @click="brief.lessons_per_section = Math.max(1, brief.lessons_per_section - 1)">−</view>
              <text class="sv">{{ brief.lessons_per_section }}</text>
              <view class="sb" @click="brief.lessons_per_section = Math.min(5, brief.lessons_per_section + 1)">＋</view>
            </view>
          </view>
          <view class="field">
            <text class="lbl">{{ t("create.assignments") }}</text>
            <switch :checked="brief.assignments" color="#f2b705" @change="(e: any) => (brief.assignments = e.detail.value)" />
          </view>
        </view>
        <view class="field">
          <text class="lbl">{{ t("create.notes") }}</text>
          <textarea class="area" v-model="brief.notes" :maxlength="30000" :placeholder="t('create.notesHint')" />
        </view>
        <view class="go">
          <text class="go-hint">{{ t("gen.oneClickHintBrief") }}</text>
          <view class="actions">
            <view class="ghost" :class="{ disabled: busy || brief.topic.trim().length < 2 }" @click="makeOutline">{{ busy ? t("create.thinking") : t("gen.outlineFirst") }}</view>
            <view class="primary big" :class="{ disabled: busy || brief.topic.trim().length < 2 }" @click="generateNow">✨ {{ t("gen.oneClick") }}</view>
          </view>
        </view>
      </view>

      <!-- optional: adjust the outline first -->
      <view v-if="step === 'outline' && outline" class="card">
        <view class="field">
          <text class="lbl">{{ t("create.courseTitle") }}</text>
          <view v-for="k in keys" :key="'t' + k" class="lang-line">
            <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
            <input class="input" v-model="outline.title[k]" />
          </view>
        </view>
        <view class="field">
          <text class="lbl">{{ t("create.summary") }}</text>
          <view v-for="k in keys" :key="'s' + k" class="lang-line">
            <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
            <textarea class="area small" v-model="outline.summary[k]" :maxlength="2000" />
          </view>
        </view>

        <view v-for="(sec, si) in outline.sections" :key="si" class="sec">
          <view class="sec-head">
            <text class="sec-no">{{ si + 1 }}</text>
            <view class="grow">
              <view v-for="k in keys" :key="'st' + k" class="lang-line">
                <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
                <input class="input strong" v-model="sec.title[k]" />
              </view>
            </view>
            <text class="link danger" @click="outline.sections.splice(si, 1)">{{ t("create.remove") }}</text>
          </view>
          <view v-for="(les, li) in sec.lessons" :key="li" class="lesson">
            <text class="dot">•</text>
            <view class="grow">
              <view v-for="k in keys" :key="'lt' + k" class="lang-line">
                <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
                <input class="input" v-model="les.title[k]" />
              </view>
              <text v-if="les.goal && disp(les.goal)" class="goal">{{ disp(les.goal) }}</text>
              <text v-if="les.sources && les.sources.length" class="goal">📄 {{ t("import.sources") }}：{{ les.sources.map((id) => outline!.files?.[id]?.name).filter(Boolean).join("、") }}</text>
            </view>
            <text class="link danger" @click="sec.lessons.splice(li, 1)">✕</text>
          </view>
          <text class="link" @click="addLesson(sec)">{{ t("create.addLesson") }}</text>
          <view v-if="sec.files && sec.files.length" class="attach">
            <text class="lbl">📎 {{ t("import.attached") }}</text>
            <view class="chips">
              <view v-for="(fid, fi) in sec.files" :key="fid" class="fchip">
                <text>{{ outline.files?.[fid]?.teacher_only ? "🔒 " : "" }}{{ outline.files?.[fid]?.name }}</text>
                <text class="x" @click="sec.files!.splice(fi, 1)">✕</text>
              </view>
            </view>
          </view>
          <view v-if="sec.assignment" class="assign">
            <text class="lbl">✎ {{ t("create.assignment") }}</text>
            <view v-for="k in keys" :key="'at' + k" class="lang-line">
              <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
              <input class="input" v-model="sec.assignment.title[k]" />
            </view>
            <view v-for="k in keys" :key="'ab' + k" class="lang-line">
              <text v-if="keys.length > 1" class="tag">{{ k === "zh" ? "中" : "EN" }}</text>
              <textarea class="area small" v-model="sec.assignment.brief[k]" :maxlength="3000" />
            </view>
          </view>
        </view>

        <view class="actions">
          <view class="ghost" @click="step = 'input'">{{ t("create.back") }}</view>
          <view v-if="mode === 'describe'" class="ghost" :class="{ disabled: busy }" @click="makeOutline">{{ busy ? t("create.thinking") : t("create.regenOutline") }}</view>
          <view class="primary big" :class="{ disabled: !lessonCount || busy }" @click="generateFromOutline">✨ {{ t("create.writeAll") }}</view>
        </view>
      </view>

      <!-- 2. generating, in the background on the server -->
      <view v-if="step === 'generate' && job" class="card">
        <view v-if="restored" class="note">{{ t("gen.restored") }}</view>
        <view class="phases">
          <view v-if="job.files.total" class="ph done">
            <text class="ph-mark">✓</text>
            <text>{{ t("gen.phase.read", { n: job.files.total }) }}<text v-if="job.files.unreadable" class="muted-s">{{ t("gen.phase.readBad", { n: job.files.unreadable }) }}</text></text>
          </view>
          <view v-if="job.files.total" class="ph" :class="phaseClass('classify')">
            <text class="ph-mark">{{ phaseMark("classify") }}</text><text>{{ t("gen.phase.classify") }}</text>
          </view>
          <view class="ph" :class="phaseClass('plan')">
            <text class="ph-mark">{{ phaseMark("plan") }}</text><text>{{ t("gen.phase.plan") }}</text>
          </view>
          <view class="ph" :class="phaseClass('write')">
            <text class="ph-mark">{{ phaseMark("write") }}</text>
            <text>{{ t("gen.phase.write", { done: job.progress.lessons_done, total: job.progress.lessons_total || "…" }) }}</text>
          </view>
        </view>
        <view class="bar"><view class="fill" :style="{ width: pct + '%' }" /></view>
        <text v-if="job.state === 'running'" class="muted-s block">{{ t("gen.leaveOk") }}</text>
        <view v-if="job.state === 'interrupted'" class="alert">{{ t("gen.interrupted") }}</view>
        <view v-if="job.state === 'error'" class="alert">{{ t("gen.stopped") }}{{ errorText(job.error) }}</view>
        <view v-if="job.progress.lessons_failed && job.state !== 'running'" class="warnbox">{{ t("gen.failedSome", { n: job.progress.lessons_failed }) }}</view>

        <view v-if="job.outline" class="tree">
          <text class="course-title">{{ disp(job.outline.title) }}</text>
          <view v-for="(sec, si) in job.outline.sections" :key="si" class="w-sec">
            <text class="w-sec-title">{{ disp(sec.title) }}</text>
            <view v-for="(les, li) in sec.lessons" :key="li" class="w-row">
              <text class="w-name">{{ disp(les.title) }}</text>
              <text v-if="job.errors[key(si, li)]" class="w-err">{{ errorText(job.errors[key(si, li)]) }}</text>
              <text class="w-status" :class="lessonState(si, li)">{{ t("create.status." + lessonState(si, li)) }}</text>
              <text v-if="lessonState(si, li) === 'fail'" class="link" @click="retry(si, li)">{{ t("create.retry") }}</text>
            </view>
            <text v-if="!sec.lessons.length && sec.files && sec.files.length" class="muted-s">📎 {{ sec.files.length }}</text>
          </view>
        </view>

        <view class="actions">
          <view class="ghost" @click="startOver">{{ t("gen.startOver") }}</view>
          <view v-if="job.state === 'interrupted' || job.state === 'error'" class="ghost" @click="resume">{{ t("gen.resume") }}</view>
          <view class="primary" :class="{ disabled: job.state !== 'done' }" @click="step = 'preview'">{{ t("gen.toPreview") }} →</view>
        </view>
      </view>

      <!-- 3. review and publish -->
      <view v-if="step === 'preview' && job && job.outline" class="card">
        <view v-if="restored" class="note">{{ t("gen.restored") }}</view>
        <text class="course-title">{{ disp(job.outline.title) }}</text>
        <text class="course-summary">{{ disp(job.outline.summary) }}</text>
        <view v-for="(sec, si) in job.outline.sections" :key="si" class="r-sec">
          <text class="w-sec-title">{{ disp(sec.title) }}</text>
          <view v-for="(les, li) in sec.lessons" :key="li" class="r-lesson">
            <view class="r-head" @click="toggle(key(si, li))">
              <text class="r-arrow">{{ open[key(si, li)] ? "▾" : "▸" }}</text>
              <text class="w-name">{{ disp(les.title) }}</text>
              <text v-if="lessonState(si, li) === 'fail'" class="w-status fail">{{ t("create.status.fail") }}</text>
              <text class="link" @click.stop="retry(si, li)">
                {{ lessonState(si, li) === "busy" ? t("create.status.busy") : lessonState(si, li) === "fail" ? t("create.retry") : t("create.rewrite") }}
              </text>
            </view>
            <view v-if="open[key(si, li)]" class="r-body"><RichContent :html="disp(les.content)" /></view>
          </view>
          <view v-if="sec.assignment" class="r-assign">✎ {{ disp(sec.assignment.title) }}</view>
          <view v-if="sec.files && sec.files.length" class="r-files">
            <text v-for="fid in sec.files" :key="fid" class="r-file">{{ job.outline.files?.[fid]?.teacher_only ? "🔒" : "📎" }} {{ job.outline.files?.[fid]?.name }}</text>
          </view>
        </view>
        <view class="actions">
          <view class="ghost" @click="startOver">{{ t("gen.startOver") }}</view>
          <view class="primary big" :class="{ disabled: busy || !allWritten }" @click="publish">
            {{ busy ? t("create.publishing") : t("create.publish") }}
          </view>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
// Page query parameters must not fall through onto the layout component.
defineOptions({ inheritAttrs: false });

import { computed, reactive, ref } from "vue";
import { onHide, onShow, onUnload } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import RichContent from "../../components/RichContent.vue";
import {
  api, ApiError, type Brief, type Job, type LessonState, type Material, type Outline, type OutlineSection, type Text, token, user,
} from "../../api";
import { errorText, locale, t } from "../../i18n";

// The import being generated survives leaving the page (D28): remember it per browser.
const JOB_KEY = "wq_gen_import";

type Step = "input" | "outline" | "generate" | "preview";
const step = ref<Step>("input");
const usedOutline = ref(false);
const mode = ref<"upload" | "describe">("upload");
const importId = ref("");
const files = ref<Material[]>([]);
const categories = ref<Record<string, string>>({});
const phase = ref<"idle" | "uploading" | "classifying" | "ready">("idle");
const uploads = reactive({ total: 0, done: 0 });
const dragOver = ref(false);
const showTable = ref(false);
const importLang = ref<"zh" | "en">(locale.value === "en" ? "en" : "zh");
const TEACHER_ONLY = ["lesson_plan", "answer_key"];
const teacherOnly = (cat: string) => TEACHER_ONLY.includes(cat);
// Hide the folder name every file shares ("大学物理（上）课程资料/…") so the table stays readable.
const commonRoot = computed(() => {
  const firsts = new Set(files.value.map((f) => (f.path.includes("/") ? f.path.split("/")[0] : "")));
  return firsts.size === 1 && !firsts.has("") ? [...firsts][0] + "/" : "";
});
const shortPath = (p: string) => (commonRoot.value && p.startsWith(commonRoot.value) ? p.slice(commonRoot.value.length) : p);
const chapterCount = computed(() => new Set(files.value.filter((f) => f.chapter && f.category !== "other").map((f) => f.chapter)).size);
const busy = ref(false);
const error = ref("");
const outline = ref<Outline | null>(null);   // only while the teacher adjusts the outline first
const job = ref<Job | null>(null);
const restored = ref(false);
const open = reactive<Record<string, boolean>>({});

const levels = ["intro", "mid", "adv"];
const langs = ["zh", "en", "both"] as const;
const stepKeys = computed<Step[]>(() => (usedOutline.value ? ["input", "outline", "generate", "preview"] : ["input", "generate", "preview"]));
const stepIndex = computed(() => stepKeys.value.indexOf(step.value));

const brief = reactive<Brief>({
  topic: "",
  audience: "",
  level: "",
  sections: 4,
  lessons_per_section: 2,
  assignments: true,
  languages: locale.value === "zh" ? "zh" : "en",
  notes: "",
});

const keys = computed<("zh" | "en")[]>(() =>
  outline.value?.languages === "both" ? ["zh", "en"] : [(outline.value?.languages as "zh" | "en") || "zh"],
);
const key = (si: number, li: number) => `${si}-${li}`;
const disp = (tx?: Text) => (tx ? tx[locale.value] || tx.zh || tx.en || "" : "");
const lessonCount = computed(() => outline.value?.sections.reduce((n, s) => n + s.lessons.length, 0) || 0);
const lessonState = (si: number, li: number): LessonState => job.value?.lessons[key(si, li)] || "wait";
const allWritten = computed(() => !!job.value && job.value.progress.lessons_total > 0
  && job.value.progress.lessons_done === job.value.progress.lessons_total);
const pct = computed(() => {
  const j = job.value;
  if (!j) return 0;
  // planning is the first 15%, writing the rest
  if (j.phase === "classify") return 4;
  if (j.phase === "plan") return 10;
  const p = j.progress;
  return p.lessons_total ? 15 + Math.round((p.lessons_done / p.lessons_total) * 85) : 15;
});

const ORDER = ["classify", "plan", "write", "done"];
function phaseClass(p: string) {
  const j = job.value;
  if (!j) return "wait";
  const at = ORDER.indexOf(j.phase);
  const me = ORDER.indexOf(p);
  if (at > me) return "done";
  if (at < me) return "wait";
  return j.state === "running" ? "on" : "err";
}
const phaseMark = (p: string) => ({ done: "✓", on: "◌", err: "!", wait: "·" })[phaseClass(p)];

function fail(e: unknown) {
  error.value = e instanceof ApiError ? e.code : "unknown";
}

// --- polling the background job ------------------------------------------------------------
let timer: ReturnType<typeof setTimeout> | null = null;
function stopPolling() {
  if (timer) clearTimeout(timer);
  timer = null;
}
function needsPolling(j: Job) {
  return j.state === "running" || Object.values(j.lessons).includes("busy");
}
async function poll() {
  stopPolling();
  if (!importId.value) return;
  try {
    const j = await api.job(importId.value);
    const wasRunning = job.value?.state === "running";
    job.value = j;
    // Finished cleanly: go straight to the preview (D28).
    if (wasRunning && j.state === "done" && !j.progress.lessons_failed && step.value === "generate") step.value = "preview";
    if (needsPolling(j)) timer = setTimeout(poll, 2000);
  } catch (e) {
    fail(e);
    timer = setTimeout(poll, 5000);
  }
}
function follow(j: Job) {
  job.value = j;
  uni.setStorageSync(JOB_KEY, importId.value);
  step.value = "generate";
  timer = setTimeout(poll, 1000);
}

// --- starting generation ----------------------------------------------------------------------
async function ensureImport() {
  if (!importId.value) importId.value = (await api.importStart()).import_id;
}

async function generateNow() {
  if (busy.value) return;
  error.value = "";
  busy.value = true;
  try {
    usedOutline.value = false;
    if (mode.value === "upload") {
      if (!importId.value || !files.value.length) return;
      await api.importEdit(importId.value, files.value.map((f) => ({ id: f.id, category: f.category, chapter: f.chapter })));
      follow(await api.generate(importId.value, { languages: importLang.value }));
    } else {
      if (brief.topic.trim().length < 2) return;
      importId.value = "";  // a description builds from scratch
      await ensureImport();
      follow(await api.generate(importId.value, { languages: brief.languages, brief: { ...brief, topic: brief.topic.trim() } }));
    }
  } catch (e) {
    fail(e);
  } finally {
    busy.value = false;
  }
}

async function generateFromOutline() {
  const o = outline.value;
  if (!o || busy.value || !lessonCount.value) return;
  error.value = "";
  busy.value = true;
  try {
    await ensureImport();
    follow(await api.generate(importId.value, { languages: o.languages, outline: o }));
  } catch (e) {
    fail(e);
  } finally {
    busy.value = false;
  }
}

async function resume() {
  if (!importId.value) return;
  error.value = "";
  try {
    follow(await api.generate(importId.value, {}));
  } catch (e) {
    fail(e);
  }
}

async function retry(si: number, li: number) {
  if (!importId.value || lessonState(si, li) === "busy") return;
  try {
    job.value = await api.retryLesson(importId.value, si, li);
    timer = setTimeout(poll, 1500);
  } catch (e) {
    fail(e);
  }
}

// --- "review the outline first" (optional) -------------------------------------------------
async function makeOutline() {
  if (busy.value || brief.topic.trim().length < 2) return;
  busy.value = true;
  error.value = "";
  try {
    outline.value = await api.aiOutline({ ...brief, topic: brief.topic.trim() });
    importId.value = "";
    usedOutline.value = true;
    step.value = "outline";
  } catch (e) {
    fail(e);
  } finally {
    busy.value = false;
  }
}

async function makeImportOutline() {
  if (busy.value || !importId.value) return;
  busy.value = true;
  error.value = "";
  try {
    await api.importEdit(importId.value, files.value.map((f) => ({ id: f.id, category: f.category, chapter: f.chapter })));
    outline.value = await api.importOutline(importId.value, importLang.value);
    usedOutline.value = true;
    step.value = "outline";
  } catch (e) {
    fail(e);
  } finally {
    busy.value = false;
  }
}

function addLesson(sec: OutlineSection) {
  const empty = () => Object.fromEntries(keys.value.map((k) => [k, ""])) as Text;
  sec.lessons.push({ title: empty(), goal: empty(), content: empty() });
}

// --- materials import (browser only) ---------------------------------------------------
type Picked = { file: File; path: string };
const skip = (name: string) => name.startsWith(".") || name.startsWith("~$") || name === "Thumbs.db" || name === "desktop.ini";

function pick(folder: boolean) {
  // #ifdef H5
  const input = document.createElement("input");
  input.type = "file";
  input.multiple = true;
  if (folder) (input as any).webkitdirectory = true;
  // Keep it in the DOM until used: some browsers ignore clicks on detached inputs.
  input.style.display = "none";
  document.body.appendChild(input);
  input.onchange = () => {
    const list = Array.from(input.files || []).map((f) => ({ file: f, path: (f as any).webkitRelativePath || f.name }));
    input.remove();
    processFiles(list);
  };
  input.click();
  // #endif
}

async function readEntry(entry: any, prefix = ""): Promise<Picked[]> {
  if (entry.isFile) {
    return new Promise((res) => entry.file((f: File) => res([{ file: f, path: prefix + f.name }]), () => res([])));
  }
  const reader = entry.createReader();
  const all: Picked[] = [];
  // readEntries returns results in batches; keep reading until empty.
  for (;;) {
    const batch: any[] = await new Promise((res) => reader.readEntries(res, () => res([])));
    if (!batch.length) break;
    for (const e of batch) all.push(...(await readEntry(e, prefix + entry.name + "/")));
  }
  return all;
}

async function onDrop(e: DragEvent) {
  dragOver.value = false;
  const items = Array.from(e.dataTransfer?.items || []);
  const list: Picked[] = [];
  for (const it of items) {
    const entry = (it as any).webkitGetAsEntry?.();
    if (entry) list.push(...(await readEntry(entry)));
    else if (it.kind === "file" && it.getAsFile()) list.push({ file: it.getAsFile()!, path: it.getAsFile()!.name });
  }
  processFiles(list);
}

async function processFiles(list: Picked[]) {
  list = list.filter((p) => !skip(p.file.name)).slice(0, 300);
  if (!list.length) return;
  error.value = "";
  try {
    await ensureImport();
    phase.value = "uploading";
    uploads.total += list.length;
    const queue = [...list];
    const worker = async () => {
      while (queue.length) {
        const p = queue.shift()!;
        try {
          const m = await api.importUpload(importId.value, p.file, p.path);
          files.value = [...files.value.filter((f) => f.path !== m.path), m];
        } catch (e) {
          fail(e);
        } finally {
          uploads.done++;
        }
      }
    };
    await Promise.all([worker(), worker(), worker()]);
    phase.value = "classifying";
    const r = await api.importClassify(importId.value);
    categories.value = r.categories;
    files.value = r.files.sort((a, b) => a.path.localeCompare(b.path, "zh"));
  } catch (e) {
    fail(e);
  } finally {
    phase.value = files.value.length ? "ready" : "idle";
  }
}

// --- preview and publish ---------------------------------------------------------------------
function toggle(k: string) {
  open[k] = !open[k];
}

async function publish() {
  const o = job.value?.outline;
  if (!o || busy.value) return;
  if (!allWritten.value) {
    uni.showToast({ title: t("create.needAll"), icon: "none" });
    return;
  }
  busy.value = true;
  error.value = "";
  try {
    const r = await api.publish(o);
    uni.removeStorageSync(JOB_KEY);
    uni.showToast({ title: t("create.published"), icon: "success" });
    setTimeout(() => uni.reLaunch({ url: `/pages/course/course?id=${r.course_id}` }), 800);
  } catch (e) {
    fail(e);
  } finally {
    busy.value = false;
  }
}

function startOver() {
  stopPolling();
  uni.removeStorageSync(JOB_KEY);
  uni.reLaunch({ url: "/pages/create/create" });
}

// Coming back to the page: pick up the course that is being (or was) generated.
async function restore() {
  const saved = uni.getStorageSync(JOB_KEY);
  if (!saved || importId.value) return;
  try {
    importId.value = saved;
    const j = await api.job(saved);
    job.value = j;
    restored.value = true;
    step.value = j.state === "done" && !j.progress.lessons_failed ? "preview" : "generate";
    if (needsPolling(j)) timer = setTimeout(poll, 2000);
  } catch {
    uni.removeStorageSync(JOB_KEY);  // expired (kept 24 hours) or someone else's
    importId.value = "";
  }
}

onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t("create.title") });
  if (user.value && user.value.can_create_courses === false) error.value = "forbidden";
  if (importId.value && job.value && needsPolling(job.value)) poll();
  else restore();
});
onHide(stopPolling);
onUnload(stopPolling);
</script>

<style scoped>
.page { min-height: 100vh; background: var(--wq-bg); }
.wrap { max-width: 900px; }
.back { color: var(--wq-link); font-size: 14px; cursor: pointer; margin-bottom: 8px; display: inline-block; }
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); margin-bottom: 16px; }
.steps { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.step { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; background: #e8ecea; color: var(--wq-muted); font-size: 13px; }
.step.on { background: var(--wq-ink); color: #fff; }
.step.done { background: #dcefe5; color: var(--wq-ok); }
.num { font-weight: 700; }
.primary.big { padding: 12px 26px; font-size: 16px; }
.go { margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--wq-line); }
.go-hint { display: block; font-size: 13px; color: var(--wq-muted); line-height: 1.7; }
.link.plain { margin-left: 0; }
.block { display: block; margin-bottom: 12px; }
.note { background: #e7f1f5; color: var(--wq-link); border-radius: 8px; padding: 8px 12px; font-size: 14px; margin-bottom: 14px; }
.warnbox { background: #fff8e0; color: #7a5a00; border-radius: 8px; padding: 10px 14px; font-size: 14px; margin-bottom: 12px; }
.phases { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.ph { display: flex; align-items: center; gap: 10px; font-size: 15px; color: var(--wq-muted); }
.ph.done { color: var(--wq-ok); }
.ph.on { color: var(--wq-ink); font-weight: 600; }
.ph.err { color: var(--wq-danger); }
.ph-mark { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; background: #eef1f0; flex-shrink: 0; }
.ph.done .ph-mark { background: #dcefe5; }
.ph.on .ph-mark { background: var(--wq-accent); animation: spin 1.2s linear infinite; }
.ph.err .ph-mark { background: #fdecea; }
@keyframes spin { to { transform: rotate(360deg); } }
.tree { margin-top: 18px; border-top: 1px solid var(--wq-line); padding-top: 14px; }
.tree .course-title { margin-bottom: 12px; }
.w-err { font-size: 12px; color: var(--wq-danger); }
.alert { background: #fdecea; color: var(--wq-danger); padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; font-size: 14px; }
.card { background: #fff; border: 1px solid var(--wq-line); border-radius: 12px; padding: 20px 18px; }
.field { display: flex; flex-direction: column; margin-bottom: 16px; }
.row { display: flex; gap: 20px; flex-wrap: wrap; }
.grow { flex: 1; min-width: 0; }
.lbl { font-size: 14px; color: var(--wq-text); margin-bottom: 6px; font-weight: 600; }
.input { height: 40px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 0 10px; font-size: 15px; background: #fafbfa; flex: 1; }
.input.strong { font-weight: 600; }
.area { width: 100%; min-height: 120px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 10px; font-size: 14px; background: #fafbfa; box-sizing: border-box; }
.area.small { min-height: 60px; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip { padding: 6px 14px; border-radius: 999px; border: 1px solid var(--wq-line); font-size: 14px; cursor: pointer; background: #fff; }
.chip.sel { background: var(--wq-ink); color: #fff; border-color: var(--wq-ink); }
.stepper { display: flex; align-items: center; gap: 10px; }
.sb { width: 32px; height: 32px; border-radius: 8px; border: 1px solid var(--wq-line); display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 18px; }
.sv { min-width: 24px; text-align: center; font-size: 16px; font-weight: 600; }
.actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; flex-wrap: wrap; }
.primary { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 10px 20px; border-radius: 8px; cursor: pointer; text-align: center; }
.ghost { border: 1px solid var(--wq-line); padding: 10px 18px; border-radius: 8px; cursor: pointer; color: var(--wq-ink); background: #fff; }
.disabled { opacity: 0.5; pointer-events: none; }
.lang-line { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.tag { font-size: 11px; font-weight: 700; color: var(--wq-muted); width: 22px; flex-shrink: 0; }
.sec { border-top: 1px solid var(--wq-line); padding-top: 14px; margin-top: 14px; }
.sec-head { display: flex; gap: 10px; align-items: flex-start; }
.sec-no { width: 28px; height: 28px; border-radius: 8px; background: var(--wq-ink); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0; margin-top: 6px; }
.lesson { display: flex; gap: 8px; align-items: flex-start; margin: 6px 0 6px 38px; }
.dot { color: var(--wq-muted); margin-top: 10px; }
.goal { display: block; font-size: 12px; color: var(--wq-muted); margin: -2px 0 4px; }
.link { color: var(--wq-link); font-size: 13px; cursor: pointer; margin-left: 38px; flex-shrink: 0; }
.lesson .link, .sec-head .link, .w-row .link, .r-head .link { margin-left: 0; margin-top: 10px; }
.link.danger { color: var(--wq-danger); }
.assign { margin: 10px 0 0 38px; padding: 10px 12px; background: #fff8e0; border-radius: 8px; }
.progress-text { display: block; font-size: 15px; color: var(--wq-ink); margin-bottom: 8px; }
.bar { height: 8px; background: #e8ecea; border-radius: 4px; overflow: hidden; margin-bottom: 16px; }
.fill { height: 100%; background: var(--wq-accent); transition: width .3s ease; }
.w-sec, .r-sec { margin-bottom: 14px; }
.w-sec-title { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 6px; }
.w-row { display: flex; align-items: center; gap: 10px; padding: 6px 0 6px 12px; border-bottom: 1px solid #f0f2f1; }
.w-name { flex: 1; font-size: 14px; color: var(--wq-text); }
.w-status { font-size: 12px; color: var(--wq-muted); }
.w-status.busy { color: #7a5a00; }
.w-status.done { color: var(--wq-ok); }
.w-status.fail { color: var(--wq-danger); }
.course-title { display: block; font-size: 22px; font-weight: 700; color: var(--wq-ink); }
.course-summary { display: block; font-size: 14px; color: var(--wq-muted); margin: 6px 0 16px; }
.r-lesson { border: 1px solid var(--wq-line); border-radius: 8px; margin: 6px 0; }
.r-head { display: flex; align-items: center; gap: 8px; padding: 8px 12px; cursor: pointer; }
.r-head .link { margin-top: 0; }
.r-arrow { color: var(--wq-muted); width: 12px; }
.r-body { padding: 4px 16px 12px; border-top: 1px solid #f0f2f1; }
.r-assign { font-size: 14px; color: #7a5a00; padding: 6px 12px; }
.modes { display: flex; gap: 8px; margin-bottom: 12px; }
.mode { flex: 1; text-align: center; padding: 12px; border-radius: 10px; border: 1px solid var(--wq-line); background: #fff; cursor: pointer; font-weight: 600; color: var(--wq-muted); }
.mode.on { border-color: var(--wq-ink); color: var(--wq-ink); box-shadow: inset 0 0 0 1px var(--wq-ink); }
.drop { border: 2px dashed #c5d0cc; border-radius: 12px; padding: 28px 20px; text-align: center; background: #fafbfa; }
.drop.over { border-color: var(--wq-accent); background: #fffbea; }
.drop-title { display: block; font-size: 18px; font-weight: 600; color: var(--wq-ink); }
.drop-hint { display: block; font-size: 13px; color: var(--wq-muted); margin: 8px auto 16px; max-width: 560px; line-height: 1.6; }
.drop-buttons { display: flex; gap: 10px; justify-content: center; }
.phase { margin-top: 16px; font-size: 14px; color: var(--wq-ink); }
.phase .bar { margin-top: 8px; }
.table-head { display: flex; justify-content: space-between; align-items: baseline; margin: 20px 0 8px; gap: 12px; flex-wrap: wrap; }
.muted-s { font-size: 13px; color: var(--wq-muted); }
.mtable { border: 1px solid var(--wq-line); border-radius: 10px; overflow: hidden; }
.mrow { display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-top: 1px solid #eef1f0; }
.mrow.mhead { background: #f4f6f5; border-top: 0; font-size: 13px; font-weight: 600; color: var(--wq-muted); }
.mrow.unsure { background: #fffbea; }
.c-file { flex: 1; min-width: 0; display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.fname { font-size: 13px; color: var(--wq-ink); word-break: break-all; }
.c-cat { width: 130px; flex-shrink: 0; }
.c-ch { width: 96px; flex-shrink: 0; }
.msel { width: 100%; height: 32px; border: 1px solid var(--wq-line); border-radius: 6px; background: #fff; font-size: 13px; padding: 0 6px; }
.tag-err, .tag-warn, .tag-lock { font-size: 11px; padding: 1px 6px; border-radius: 4px; }
.tag-err { background: #fdecea; color: var(--wq-danger); }
.tag-warn { background: #fff1bf; color: #7a5a00; }
.tag-lock { background: #eef1f0; color: var(--wq-muted); }
.lang-row { align-items: center; margin-top: 16px; gap: 12px; }
.attach { margin: 10px 0 0 38px; }
.fchip { display: flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; background: #eef1f0; font-size: 12px; color: var(--wq-ink); }
.fchip .x { color: var(--wq-muted); cursor: pointer; }
.r-files { display: flex; flex-wrap: wrap; gap: 6px 14px; padding: 4px 12px 8px; }
.r-file { font-size: 12px; color: var(--wq-muted); }
@media (max-width: 560px) { .c-cat { width: 104px; } .c-ch { width: 80px; } }
</style>
