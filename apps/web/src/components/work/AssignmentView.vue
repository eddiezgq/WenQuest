<template>
  <view>
    <text v-if="loading && !a" class="wq-muted">{{ t("common.loading") }}</text>
    <text v-else-if="error && !a" class="wq-error">{{ errorText(error) }}</text>
    <template v-else-if="a">
      <!-- key facts -->
      <view class="facts">
        <view class="fact"><text class="f-k">{{ t("work.due") }}</text><text class="f-v">{{ a.due ? formatDate(a.due) : t("activity.noDue") }}</text></view>
        <view class="fact"><text class="f-k">{{ t("work.points") }}</text><text class="f-v">{{ a.max_grade }}</text></view>
        <view class="fact"><text class="f-k">{{ t("work.submitAs") }}</text><text class="f-v">{{ submitAs }}</text></view>
        <view v-if="a.cutoff" class="fact"><text class="f-k">{{ t("work.cutoff") }}</text><text class="f-v">{{ formatDate(a.cutoff) }}</text></view>
      </view>

      <view class="paper"><MathContent :html="a.intro" /></view>
      <view v-if="a.attachments.length" class="wq-card">
        <text class="wq-label">{{ t("work.attachments") }}</text>
        <text v-for="f in a.attachments" :key="f.url" class="file wq-link" @click="open(f.url)">📎 {{ f.name }}</text>
      </view>

      <!-- ===================== student ===================== -->
      <template v-if="!a.teacher && sub">
        <view class="wq-card status" :class="statusClass">
          <view class="wq-row">
            <text class="st-badge">{{ t("work.status." + (sub.graded ? "graded" : sub.status)) }}</text>
            <text v-if="sub.modified" class="wq-muted">{{ t("work.lastSaved") }} {{ formatDate(sub.modified) }}</text>
            <text v-if="late" class="wq-tag live">{{ t("work.late") }}</text>
          </view>
          <view v-if="sub.graded" class="graded">
            <text class="g-num">{{ sub.grade }}</text>
            <view v-if="sub.feedback" class="g-fb">
              <text class="wq-label">{{ t("work.teacherFeedback") }}</text>
              <MathContent :html="sub.feedback" />
            </view>
            <text v-for="f in sub.feedback_files" :key="f.url" class="wq-link file" @click="open(f.url)">📎 {{ f.name }}</text>
          </view>
        </view>

        <!-- what was handed in -->
        <view v-if="!editing && (sub.text || sub.files.length)" class="wq-card">
          <text class="wq-label">{{ t("work.myWork") }}</text>
          <view v-if="sub.text" class="paper small"><MathContent :html="sub.text" /></view>
          <view v-for="f in sub.files" :key="f.url" class="frow">
            <text class="wq-link" @click="open(f.url)">📎 {{ f.name }}</text>
            <text class="wq-muted">{{ fileSize(f.size) }}</text>
          </view>
        </view>

        <!-- editor -->
        <view v-if="editing" class="wq-card editor">
          <template v-if="a.config.text">
            <text class="wq-label">{{ t("work.onlineText") }}<text v-if="a.config.wordlimit">（{{ t("work.wordLimit", { n: a.config.wordlimit }) }}）</text></text>
            <textarea v-model="text" class="wq-textarea big" auto-height :maxlength="-1" :placeholder="t('work.textHint')" />
          </template>
          <template v-if="a.config.files">
            <text class="wq-label">{{ t("work.files") }}<text v-if="a.config.maxfiles">（{{ t("work.maxFiles", { n: a.config.maxfiles }) }}）</text></text>
            <view v-for="f in keep" :key="f.name" class="frow">
              <text>📎 {{ f.name }}</text><text class="wq-muted">{{ fileSize(f.size) }}</text>
              <text class="wq-link danger" @click="keep = keep.filter((x) => x.name !== f.name)">{{ t("work.remove") }}</text>
            </view>
            <view v-for="f in added" :key="'n' + f.name" class="frow new">
              <text>＋ {{ f.name }}</text><text class="wq-muted">{{ fileSize(f.size) }}</text>
              <text class="wq-link danger" @click="added = added.filter((x) => x !== f)">{{ t("work.remove") }}</text>
            </view>
            <view class="wq-btn small" :class="{ disabled: full }" @click="choose">＋ {{ t("work.addFile") }}</view>
            <text v-if="a.config.filetypes" class="wq-muted block">{{ t("work.types") }}：{{ a.config.filetypes }}</text>
          </template>
          <text v-if="formError" class="wq-error">{{ formError }}</text>
          <view class="wq-row actions">
            <view v-if="a.config.drafts" class="wq-btn" :class="{ disabled: saving }" @click="save(false)">{{ t("work.saveDraft") }}</view>
            <view class="wq-btn primary" :class="{ disabled: saving }" @click="save(true)">{{ saving ? progress || t("common.saving") : t("work.handIn") }}</view>
            <view v-if="hasWork" class="wq-btn" @click="editing = false">{{ t("common.cancel") }}</view>
          </view>
          <text class="wq-muted block">{{ a.config.drafts ? t("work.draftNote") : t("work.noDraftNote") }}</text>
        </view>
        <view v-else-if="sub.can_edit" class="wq-row">
          <view class="wq-btn primary" @click="startEdit">{{ hasWork ? t("work.edit") : t("work.start") }}</view>
          <view v-if="a.config.drafts && sub.status === 'draft' && sub.can_submit" class="wq-btn dark" @click="handIn">{{ t("work.handIn") }}</view>
        </view>
        <text v-else-if="!sub.graded && sub.status !== 'submitted'" class="wq-muted block">{{ t("work.closed") }}</text>
      </template>

      <!-- ===================== teacher ===================== -->
      <template v-else-if="a.teacher">
        <view v-if="a.summary" class="counts">
          <view class="count"><text class="c-n">{{ a.summary.participants }}</text><text class="wq-muted">{{ t("work.participants") }}</text></view>
          <view class="count"><text class="c-n">{{ a.summary.submitted }}</text><text class="wq-muted">{{ t("work.submitted") }}</text></view>
          <view class="count warn"><text class="c-n">{{ a.summary.needs_grading }}</text><text class="wq-muted">{{ t("work.needsGrading") }}</text></view>
        </view>
        <view class="grading" :class="{ split: !!current }">
          <view class="list">
            <view v-for="r in rows" :key="r.id" class="srow" :class="{ on: current && current.id === r.id }" @click="openStudent(r)">
              <view class="wq-avatar">{{ initials(r.fullname) }}</view>
              <view class="s-main">
                <text class="s-name">{{ r.fullname }}</text>
                <text class="wq-muted">{{ r.groups.join("、") }}<text v-if="r.modified"> · {{ formatDate(r.modified) }}</text></text>
              </view>
              <text v-if="r.late" class="wq-tag live">{{ t("work.late") }}</text>
              <text class="wq-tag" :class="r.grade !== null ? 'ok' : r.needs_grading ? 'accent' : ''">
                {{ r.grade !== null ? `${r.grade}/${a.max_grade}` : t("work.status." + r.status) }}
              </text>
            </view>
            <view v-if="!rows.length" class="wq-empty">{{ t("work.noStudents") }}</view>
          </view>
          <view v-if="current" class="panel">
            <view class="wq-row p-head">
              <text class="p-name">{{ current.fullname }}</text>
              <text class="wq-link" @click="current = null">✕</text>
            </view>
            <text v-if="!work" class="wq-muted">{{ t("common.loading") }}</text>
            <template v-else>
              <text class="wq-tag">{{ t("work.status." + work.status) }}</text>
              <view v-if="work.text" class="paper small"><MathContent :html="work.text" /></view>
              <view v-for="f in work.files" :key="f.url" class="frow"><text class="wq-link" @click="open(f.url)">📎 {{ f.name }}</text><text class="wq-muted">{{ fileSize(f.size) }}</text></view>
              <text v-if="!work.text && !work.files.length" class="wq-muted block">{{ t("work.nothingYet") }}</text>

              <view class="ai-box">
                <view class="wq-btn dark small" :class="{ disabled: aiBusy || (!work.text && !work.files.length) }" @click="suggest">
                  ✦ {{ aiBusy ? t("work.aiBusy") : t("work.aiSuggest") }}
                </view>
                <text class="wq-muted">{{ t("work.aiNote") }}</text>
              </view>
              <view v-if="criteria.length" class="criteria">
                <view v-for="c in criteria" :key="c.name" class="crit"><text>{{ c.name }}</text><text class="c-s">{{ c.score }}/{{ c.max }}</text><text class="wq-muted">{{ c.note }}</text></view>
              </view>

              <text class="wq-label">{{ t("work.grade") }}（0–{{ a.max_grade }}）</text>
              <input v-model="gradeText" type="digit" class="wq-input grade-in" />
              <text class="wq-label">{{ t("work.feedback") }}</text>
              <textarea v-model="feedback" class="wq-textarea" auto-height :maxlength="-1" :placeholder="t('work.feedbackHint')" />
              <text v-if="formError" class="wq-error">{{ formError }}</text>
              <view class="wq-row actions">
                <view class="wq-btn primary" :class="{ disabled: saving }" @click="saveGrade(false)">{{ saving ? t("common.saving") : t("common.save") }}</view>
                <view class="wq-btn" :class="{ disabled: saving }" @click="saveGrade(true)">{{ t("work.saveNext") }}</view>
              </view>
            </template>
          </view>
        </view>
      </template>
    </template>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import MathContent from "../MathContent.vue";
import { absolute, ApiError } from "../../api";
import {
  type Assignment, fileSize, initials, openOutside, type Picked, pickFiles, saveSubmission, type Submission, type SubmissionRow, workApi,
} from "../../courseApi";
import { errorText, formatDate, t } from "../../i18n";

const props = defineProps<{ cmid: number }>();
const emit = defineEmits<{ (e: "loaded", a: Assignment): void }>();
const a = ref<Assignment | null>(null);
const loading = ref(true);
const error = ref("");
const editing = ref(false);
const text = ref("");
const keep = ref<Submission["files"]>([]);
const added = ref<Picked[]>([]);
const saving = ref(false);
const progress = ref("");
const formError = ref("");
const rows = ref<SubmissionRow[]>([]);
const current = ref<SubmissionRow | null>(null);
const work = ref<(Submission & { max_grade: number }) | null>(null);
const gradeText = ref("");
const feedback = ref("");
const aiBusy = ref(false);
const criteria = ref<{ name: string; score: number; max: number; note: string }[]>([]);

const sub = computed(() => a.value?.submission || null);
const hasWork = computed(() => !!sub.value && (!!sub.value.text || sub.value.files.length > 0));
const late = computed(() => !!a.value?.due && !!sub.value?.modified && sub.value.status === "submitted" && sub.value.modified > a.value.due);
const full = computed(() => !!a.value?.config.maxfiles && keep.value.length + added.value.length >= a.value.config.maxfiles);
const statusClass = computed(() => (sub.value?.graded ? "ok" : sub.value?.status === "submitted" ? "info" : "todo"));
const submitAs = computed(() => {
  const c = a.value?.config;
  if (!c) return "";
  return [c.text ? t("work.asText") : "", c.files ? t("work.asFiles") : ""].filter(Boolean).join(" + ") || "—";
});
const open = (url: string) => openOutside(absolute(url), t("activity.linkCopied"));
const plain = (h: string) => h.replace(/<br\s*\/?>/g, "\n").replace(/<\/p>\s*<p>/g, "\n\n").replace(/<[^>]+>/g, "").replace(/&nbsp;/g, " ").trim();

async function load() {
  loading.value = true;
  error.value = "";
  try {
    a.value = await workApi.assignment(props.cmid);
    emit("loaded", a.value);
    if (a.value.teacher) rows.value = (await workApi.submissions(props.cmid)).rows;
    else if (a.value.submission && !hasWork.value && a.value.submission.can_edit) startEdit();
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

function startEdit() {
  if (!sub.value) return;
  text.value = plain(sub.value.text);
  keep.value = [...sub.value.files];
  added.value = [];
  formError.value = "";
  editing.value = true;
}
async function choose() {
  const max = a.value?.config.maxfiles ? a.value.config.maxfiles - keep.value.length - added.value.length : 10;
  const picked = await pickFiles(Math.max(1, max));
  const limit = a.value?.config.maxbytes || 50 * 1048576;
  for (const f of picked) {
    if (f.size > limit) formError.value = t("error.file_too_large");
    else added.value.push(f);
  }
}
async function save(submit: boolean) {
  if (!a.value || !sub.value) return;
  if (submit && !text.value.trim() && !keep.value.length && !added.value.length) {
    formError.value = t("work.empty");
    return;
  }
  saving.value = true;
  formError.value = "";
  try {
    let names = keep.value.map((f) => f.name);
    const withText = a.value.config.text ? text.value : undefined;
    let result: Submission | null = null;
    // Files go up one at a time; the text and the hand-in come with the last call.
    const queue = [...added.value];
    if (!queue.length) {
      result = await saveSubmission(props.cmid, { text: withText, keep: names, submit });
    }
    for (let i = 0; i < queue.length; i++) {
      progress.value = t("work.uploading", { i: i + 1, n: queue.length });
      const last = i === queue.length - 1;
      result = await saveSubmission(props.cmid, { text: last ? withText : undefined, keep: names, submit: last && submit }, queue[i]);
      names = result.files.map((f) => f.name);
    }
    if (a.value && result) a.value.submission = result;
    editing.value = false;
    uni.showToast({ title: t(submit ? "work.handedIn" : "work.saved"), icon: "none" });
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    saving.value = false;
    progress.value = "";
  }
}
async function handIn() {
  if (!sub.value) return;
  saving.value = true;
  try {
    const r = await saveSubmission(props.cmid, { keep: sub.value.files.map((f) => f.name), submit: true });
    if (a.value) a.value.submission = r;
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  } finally {
    saving.value = false;
  }
}

async function openStudent(r: SubmissionRow) {
  current.value = r;
  work.value = null;
  criteria.value = [];
  formError.value = "";
  try {
    work.value = await workApi.studentWork(props.cmid, r.id);
    gradeText.value = work.value.grade_raw !== null && work.value.grade_raw !== undefined && work.value.grade_raw >= 0 ? String(Number(work.value.grade_raw)) : "";
    feedback.value = plain(work.value.feedback);
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  }
}
async function suggest() {
  if (!current.value) return;
  aiBusy.value = true;
  formError.value = "";
  try {
    const s = await workApi.aiGrade(props.cmid, current.value.id);
    gradeText.value = String(s.grade);
    feedback.value = s.comment;
    criteria.value = s.criteria;
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    aiBusy.value = false;
  }
}
async function saveGrade(next: boolean) {
  if (!current.value || !a.value) return;
  const g = gradeText.value.trim() === "" ? null : Number(gradeText.value);
  if (g !== null && (isNaN(g) || g < 0 || g > a.value.max_grade)) {
    formError.value = t("work.gradeRange", { n: a.value.max_grade });
    return;
  }
  saving.value = true;
  try {
    await workApi.saveGrade(props.cmid, current.value.id, g, feedback.value);
    const idx = rows.value.findIndex((r) => r.id === current.value!.id);
    rows.value[idx] = { ...rows.value[idx], grade: g, needs_grading: false };
    uni.showToast({ title: t("work.gradeSaved"), icon: "none" });
    if (next) {
      const after = rows.value.slice(idx + 1).find((r) => r.needs_grading) || rows.value[idx + 1];
      if (after) await openStudent(after);
      else current.value = null;
    }
  } catch (e) {
    formError.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    saving.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.facts { display: flex; flex-wrap: wrap; gap: 0; background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; margin-bottom: 14px; }
.fact { flex: 1; min-width: 140px; padding: 10px 16px; border-left: 1px solid var(--wq-line); display: flex; flex-direction: column; }
.fact:first-child { border-left: 0; }
.f-k { font-size: 12px; color: var(--wq-muted); }
.f-v { font-weight: 600; color: var(--wq-ink); }
.paper { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 18px 22px; margin-bottom: 14px; line-height: 1.8; }
.paper.small { padding: 10px 14px; margin: 8px 0; background: #fafbfb; }
.file { display: block; margin-top: 4px; }
.block { display: block; }
.status { border-left: 4px solid var(--wq-line); }
.status.ok { border-left-color: var(--wq-ok); }
.status.info { border-left-color: var(--wq-link); }
.status.todo { border-left-color: var(--wq-accent); }
.st-badge { font-weight: 700; color: var(--wq-ink); }
.graded { margin-top: 10px; }
.g-num { font-size: 28px; font-weight: 800; color: var(--wq-ok); font-family: "IBM Plex Mono", Menlo, monospace; }
.g-fb { margin-top: 6px; }
.frow { display: flex; align-items: center; gap: 12px; padding: 4px 0; }
.frow.new { color: var(--wq-link); }
.editor .big { min-height: 180px; }
.actions { margin: 12px 0 6px; }
.counts { display: flex; gap: 12px; margin-bottom: 14px; }
.count { flex: 1; background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 12px 16px; display: flex; flex-direction: column; }
.count.warn { border-color: var(--wq-accent); }
.c-n { font-size: 24px; font-weight: 800; color: var(--wq-ink); font-family: "IBM Plex Mono", Menlo, monospace; }
.grading { display: grid; grid-template-columns: 1fr; gap: 14px; }
.grading.split { grid-template-columns: minmax(260px, 1fr) minmax(0, 1.4fr); }
.list { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; overflow: hidden; align-self: start; }
.srow { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-top: 1px solid var(--wq-line); cursor: pointer; }
.srow:first-child { border-top: 0; }
.srow:hover, .srow.on { background: #f1f6f8; }
.s-main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.s-name { color: var(--wq-ink); font-weight: 600; }
.panel { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 14px 18px; align-self: start; position: sticky; top: 12px; }
.p-head { justify-content: space-between; margin-bottom: 8px; }
.p-name { font-size: 18px; font-weight: 700; color: var(--wq-ink); }
.ai-box { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin: 12px 0 4px; padding: 10px 12px; background: #f5f7fb; border-radius: 8px; }
.criteria { margin: 6px 0; display: flex; flex-direction: column; gap: 4px; }
.crit { display: grid; grid-template-columns: 1fr 70px; gap: 2px 10px; font-size: 13px; border-bottom: 1px dashed var(--wq-line); padding: 4px 0; }
.crit .wq-muted { grid-column: 1 / -1; }
.c-s { text-align: right; font-weight: 700; }
.grade-in { max-width: 160px; }
@media (max-width: 860px) {
  .grading.split { grid-template-columns: 1fr; }
  .panel { position: static; }
}
</style>
