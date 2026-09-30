<template>
  <AppShell nav="create" :title="t('studio.title')" :crumb="p ? courseTitle : ''">
    <view v-if="!p" class="muted">{{ error ? errorText(error) : t("common.loading") }}</view>
    <view v-else class="ws">
      <!-- stages -->
      <view class="stages">
        <view v-for="(s, i) in STAGES" :key="s" class="stg" :class="{ on: p.stage === s, done: stageIndex > i }">
          <text class="stg-n">{{ stageIndex > i ? "✓" : i + 1 }}</text>
          <text>{{ t("studio.stage." + s) }}</text>
        </view>
        <view class="grow" />
        <view v-if="p.busy" class="working">
          <view class="dot" />
          <text>{{ p.busy.label }}</text>
          <text class="stop" @click="stop">{{ t("studio.stop") }}</text>
        </view>
      </view>
      <view v-if="error" class="alert">{{ errorText(error) }}</view>

      <!-- phone: switch between conversation and dossier -->
      <view class="mtabs">
        <text :class="{ on: mpane === 'chat' }" @click="mpane = 'chat'">{{ t("studio.chat") }}</text>
        <text :class="{ on: mpane === 'dossier' }" @click="mpane = 'dossier'">{{ t("studio.dossier") }}</text>
      </view>

      <view class="cols">
        <!-- ================= conversation with the course lead ================= -->
        <view class="chat" :class="{ hide: mpane !== 'chat' }">
          <scroll-view class="msgs" scroll-y :scroll-into-view="lastMsgId">
            <view v-for="m in p.messages" :id="'m' + m.id" :key="m.id" class="msg" :class="[m.role, m.kind]">
              <text v-if="m.role === 'lead'" class="who">{{ t("studio.role.lead") }}</text>
              <text class="bubble">{{ m.text }}</text>
            </view>
            <!-- open questions, answered with one click -->
            <view v-for="q in openQuestions" :id="'q' + q.id" :key="q.id" class="qcard">
              <text class="q-text">{{ q.text }}</text>
              <view class="q-opts">
                <text v-for="o in q.options" :key="o" class="q-opt" @click="answer(q.id, o)">{{ o }}</text>
              </view>
              <view class="q-own">
                <input v-model="own[q.id]" class="q-input" :placeholder="t('studio.ownAnswer')" @confirm="answer(q.id, own[q.id])" />
                <text class="q-send" @click="answer(q.id, own[q.id])">{{ t("studio.answer") }}</text>
              </view>
            </view>
            <view id="bottom" />
          </scroll-view>

          <!-- files: dropped here while the materials are being gathered -->
          <!-- #ifdef H5 -->
          <div v-if="p.stage === 'intake' || p.stage === 'materials'" class="drop" :class="{ over: dragOver }"
               @dragover.prevent="dragOver = true" @dragleave="dragOver = false" @drop.prevent="onDrop">
            <text v-if="uploads.total && uploads.done < uploads.total">{{ t("import.uploading", { done: uploads.done, total: uploads.total }) }}</text>
            <text v-else>{{ p.files.length ? t("studio.filesIn", { n: p.files.length }) : t("studio.dropHere") }}</text>
            <text class="link" @click="pick(true)">{{ t("import.pickFolder") }}</text>
            <text class="link" @click="pick(false)">{{ t("import.pickFiles") }}</text>
          </div>
          <!-- #endif -->

          <view class="compose">
            <textarea v-model="draft" class="input" :placeholder="t('studio.say.' + p.stage)" auto-height :maxlength="4000" />
            <view class="send" :class="{ disabled: !draft.trim() || !!p.busy }" @click="send">{{ t("studio.send") }}</view>
          </view>

          <!-- the one action that moves the course forward -->
          <view class="next">
            <view v-if="p.stage === 'intake'" class="primary" :class="{ disabled: !!p.busy || (!p.files.length && !p.requirements.notes) || uploading }" @click="start">
              {{ t("studio.go.intake") }}
            </view>
            <view v-else-if="p.stage === 'materials'" class="primary" :class="{ disabled: !!p.busy }" @click="approveMaterials">
              {{ t("studio.go.materials") }}
            </view>
            <view v-else-if="p.stage === 'outline'" class="primary" :class="{ disabled: !!p.busy || dirty }" @click="approveOutline">
              {{ busyAction ? t("studio.creating") : t("studio.go.outline") }}
            </view>
            <template v-else>
              <view class="primary" :class="{ disabled: !!p.busy || !p.progress.planned && !p.progress.failed }" @click="writeNext">
                ✎ {{ t("studio.go.lessons") }}
              </view>
              <text class="pace-note">{{ p.pace.mode === "daily" ? t("studio.paceDailyNote", { h: p.pace.hour }) : t("studio.paceManualNote") }}</text>
            </template>
            <text v-if="p.stage === 'materials' && openQuestions.length" class="hint">{{ t("studio.answerFirst", { n: openQuestions.length }) }}</text>
            <text v-if="p.stage === 'outline' && dirty" class="hint">{{ t("studio.saveOutlineFirst") }}</text>
          </view>
        </view>

        <!-- ================= course dossier ================= -->
        <view class="dossier" :class="{ hide: mpane !== 'dossier' }">
          <view class="tabs">
            <text v-for="tb in TABS" :key="tb" class="tab" :class="{ on: tab === tb }" @click="tab = tb">
              {{ t("studio.tab." + tb) }}<text v-if="badge(tb)" class="badge">{{ badge(tb) }}</text>
            </text>
          </view>

          <!-- materials list -->
          <view v-if="tab === 'materials'" class="pane">
            <!-- add, download: at any stage (files added after the materials were settled are sorted at once) -->
            <!-- #ifdef H5 -->
            <div class="mtools" :class="{ over: dragOver }" @dragover.prevent="dragOver = true" @dragleave="dragOver = false" @drop.prevent="onDrop">
              <text class="mt-btn" @click="pick(false)">＋ {{ t("studio.addFiles") }}</text>
              <text class="mt-btn" @click="pick(true)">＋ {{ t("studio.addFolder") }}</text>
              <text v-if="uploading" class="muted-s">{{ t("import.uploading", { done: uploads.done, total: uploads.total }) }}</text>
              <text v-else class="muted-s">{{ t("studio.dropAnytime") }}</text>
              <text v-if="p.zip_url" class="mt-btn right" @click="download(p.zip_url)">↓ {{ t("studio.downloadAll") }}</text>
            </div>
            <!-- #endif -->
            <text v-if="p.materials.summary" class="note">{{ p.materials.summary }}</text>
            <view v-if="!p.files.length" class="empty">{{ t("studio.noFiles") }}</view>
            <view v-else class="ftable">
              <view class="frow fhead">
                <text class="f-name">{{ t("import.file") }}</text>
                <text class="f-role">{{ t("studio.role") }}</text>
                <text class="f-ch">{{ t("import.chapter") }}</text>
                <text class="f-act"></text>
              </view>
              <view v-for="f in p.files" :key="f.id" class="frow" :class="{ low: f.confidence === 'low', bad: f.error }">
                <view class="f-name">
                  <text class="fname">{{ f.id === p.materials.textbook ? "★ " : "" }}{{ f.path }}</text>
                  <text class="fsub">{{ size(f.size) }}<text v-if="f.pages"> · {{ f.pages }} {{ t("studio.pages") }}</text><text v-if="f.ocr"> · {{ t("studio.ocrPages", { n: f.ocr }) }}</text><text v-if="f.title"> · {{ f.title }}</text></text>
                  <text v-if="f.error" class="ferr">{{ t("studio.fileError." + f.error) }}</text>
                  <text v-else-if="f.confidence === 'low'" class="fwarn">{{ t("studio.lowConfidence") }}<text v-if="f.note">：{{ f.note }}</text></text>
                </view>
                <view class="f-role">
                  <!-- #ifdef H5 -->
                  <select class="sel" :value="f.role" @change="(e: any) => setRole(f, e.target.value)">
                    <option v-for="(label, key) in p.roles" :key="key" :value="key">{{ label }}</option>
                  </select>
                  <!-- #endif -->
                  <!-- #ifndef H5 -->
                  <text>{{ f.role_label }}</text>
                  <!-- #endif -->
                </view>
                <view class="f-ch">
                  <input class="chin" :value="f.chapters.join(',')" @blur="(e: any) => setChapters(f, e.detail.value)" />
                </view>
                <view class="f-act">
                  <text class="fa star" :class="{ on: f.id === p.materials.textbook }" :title="t('studio.setTextbook')" @click="setTextbook(f.id)">{{ f.id === p.materials.textbook ? "★" : "☆" }}</text>
                  <text class="fa" :title="t('studio.download')" @click="download(f.url || '')">↓</text>
                  <text class="fa del" :title="t('common.delete')" @click="removeFile(f)">✕</text>
                </view>
              </view>
            </view>
            <view v-if="roleEdits.size" class="bar-save">
              <text>{{ t("studio.unsaved") }}</text>
              <view class="primary small" @click="saveMaterials">{{ t("studio.save") }}</view>
            </view>
            <view v-if="p.toc.length" class="toc">
              <text class="h3">{{ t("studio.tocOf", { name: p.materials.book_title || textbookName }) }}</text>
              <view v-for="c in p.toc" :key="c.no" class="toc-ch">
                <text class="toc-c">{{ t("studio.chapterN", { n: c.no }) }} {{ c.title }}<text v-if="c.start" class="pg"> · p.{{ c.start }}</text></text>
                <text v-for="s in c.sections" :key="s.no" class="toc-s">{{ s.no }} {{ s.title }}<text v-if="s.start" class="pg"> · p.{{ s.start }}</text></text>
              </view>
            </view>
          </view>

          <!-- outline and calendar (editable until the lessons are published) -->
          <view v-if="tab === 'outline'" class="pane">
            <view v-if="!ed" class="empty">{{ t("studio.noOutline") }}</view>
            <template v-else>
              <input class="o-title" v-model="ed.title[lang]" :disabled="p.stage === 'lessons'" @input="dirty = true" />
              <view v-for="(c, ci) in ed.chapters" :key="c.id || ci" class="o-ch">
                <view class="o-ch-head">
                  <text class="o-no">{{ ci + 1 }}</text>
                  <input class="o-in strong" v-model="c.title[lang]" @input="dirty = true" />
                  <text class="o-act" @click="moveChapter(ci, -1)">↑</text>
                  <text class="o-act" @click="moveChapter(ci, 1)">↓</text>
                  <text class="o-act danger" @click="removeChapter(ci)">✕</text>
                </view>
                <view v-for="(l, li) in c.lessons" :key="l.id || li" class="o-les" :class="{ locked: l.status === 'published' }">
                  <input class="o-week" type="number" v-model.number="l.week" :disabled="l.status === 'published'" @input="dirty = true" />
                  <view class="grow">
                    <input class="o-in" v-model="l.title[lang]" :disabled="l.status === 'published'" @input="dirty = true" />
                    <input class="o-in goal" v-model="l.goal[lang]" :placeholder="t('studio.goal')" :disabled="l.status === 'published'" @input="dirty = true" />
                    <text v-if="l.sections.length" class="o-sec">{{ t("studio.textbookSections") }}：{{ l.sections.join("、") }}</text>
                  </view>
                  <template v-if="l.status !== 'published'">
                    <text class="o-act" @click="moveLesson(c, li, -1)">↑</text>
                    <text class="o-act" @click="moveLesson(c, li, 1)">↓</text>
                    <text class="o-act danger" @click="c.lessons.splice(li, 1); dirty = true">✕</text>
                  </template>
                  <text v-else class="st published">{{ t("studio.status.published") }}</text>
                </view>
                <text class="link" @click="addLesson(c)">{{ t("create.addLesson") }}</text>
              </view>
              <text class="link" @click="addChapter">{{ t("studio.addChapter") }}</text>
              <view v-if="dirty" class="bar-save">
                <text>{{ t("studio.unsaved") }}</text>
                <text class="link" @click="resetOutline">{{ t("studio.discard") }}</text>
                <view class="primary small" @click="saveOutline">{{ t("studio.save") }}</view>
              </view>
              <view class="calendar">
                <text class="h3">{{ t("studio.calendar") }}</text>
                <view v-for="w in weeks" :key="w.week" class="cal-w">
                  <text class="cal-n">{{ w.week ? t("studio.weekN", { n: w.week }) : t("studio.noWeek") }}</text>
                  <text class="cal-l">{{ w.titles.join(" · ") }}</text>
                </view>
                <text v-if="p.outline && p.outline.calendar_note" class="note">{{ p.outline.calendar_note }}</text>
              </view>
            </template>
          </view>

          <!-- lessons: progress, review, publish -->
          <view v-if="tab === 'lessons'" class="pane">
            <view v-if="!p.outline" class="empty">{{ t("studio.noOutline") }}</view>
            <template v-else>
              <view class="pace">
                <text class="h3">{{ t("studio.pace") }}</text>
                <view class="pace-row">
                  <text class="chip2" :class="{ on: p.pace.mode === 'manual' }" @click="setPace('manual', p.pace.hour)">{{ t("studio.paceManual") }}</text>
                  <text class="chip2" :class="{ on: p.pace.mode === 'daily' }" @click="setPace('daily', p.pace.hour)">{{ t("studio.paceDaily") }}</text>
                  <template v-if="p.pace.mode === 'daily'">
                    <!-- #ifdef H5 -->
                    <select class="sel small" :value="p.pace.hour" @change="(e: any) => setPace('daily', Number(e.target.value))">
                      <option v-for="h in 24" :key="h" :value="h - 1">{{ String(h - 1).padStart(2, "0") }}:00</option>
                    </select>
                    <!-- #endif -->
                    <text class="muted-s">{{ p.pace.tz }}</text>
                  </template>
                </view>
                <text class="muted-s">{{ t("studio.progress", { published: p.progress.published, total: p.progress.total, awaiting: p.progress.awaiting }) }}</text>
              </view>
              <view v-for="c in p.outline.chapters" :key="c.id" class="l-ch">
                <text class="l-ch-t">{{ disp(c.title) }}</text>
                <view v-for="l in c.lessons" :key="l.id" class="l-row" :class="{ open: openLesson === l.id }">
                  <view class="l-head" @click="openLesson = openLesson === l.id ? '' : l.id">
                    <text class="l-week">{{ l.week ? t("studio.weekShort", { n: l.week }) : "" }}</text>
                    <text class="l-title">{{ disp(l.title) }}</text>
                    <text class="st" :class="l.status">{{ t("studio.status." + l.status) }}</text>
                  </view>
                  <view v-if="openLesson === l.id" class="l-body">
                    <template v-if="l.status === 'awaiting' || l.status === 'published'">
                      <view v-if="l.review" class="review" :class="l.review.verdict">
                        <text class="rv-h">{{ l.review.verdict === "pass" ? t("studio.reviewPass") : t("studio.reviewRevise") }}</text>
                        <text v-if="l.review.summary" class="rv-s">{{ l.review.summary }}</text>
                        <text v-for="(i, ii) in l.review.issues" :key="ii" class="rv-i">· {{ i.text }}</text>
                      </view>
                      <view v-if="l.files?.length" class="deliv">
                        <text class="h4">{{ t("studio.deliverables") }}</text>
                        <view class="dv-list">
                          <view v-for="f in l.files" :key="f.name" class="dv" @click="download(f.url)">
                            <text class="dv-k">{{ t("studio.kind." + f.kind) }}</text>
                            <text class="dv-n">{{ f.name }}</text>
                            <text v-if="f.teacher_only" class="dv-t">{{ t("studio.teacherOnly") }}</text>
                            <text class="dv-d">↓</text>
                          </view>
                        </view>
                        <template v-for="f in l.files" :key="'v' + f.name">
                          <video v-if="f.kind === 'animation'" class="dv-video" :src="absolute(f.url)" controls preload="metadata" />
                          <!-- #ifdef H5 -->
                          <iframe v-if="f.kind === 'lab'" class="dv-lab" :src="absolute(f.url)" :title="f.name"
                                  sandbox="allow-scripts allow-popups allow-forms allow-modals" />
                          <!-- #endif -->
                        </template>
                        <view v-if="p.labs_on" class="ghost small" :class="{ disabled: !!p.busy }" @click="redoLab(l.id)">
                          ⚗ {{ l.files.some((f) => f.kind === 'lab') ? t("studio.redoLab") : t("studio.makeLab") }}
                        </view>
                        <view v-if="l.files.some((f) => f.kind === 'slides')" class="ghost small" @click="previewDeck(l.id)">
                          {{ deckFor === l.id && deckMsg ? deckMsg : t("studio.previewDeck") }}
                        </view>
                        <scroll-view v-if="deckFor === l.id && deckImgs.length" scroll-x class="dv-deck">
                          <image v-for="(s, si) in deckImgs" :key="si" :src="s" mode="widthFix" class="dv-img" />
                        </scroll-view>
                      </view>
                      <view class="lesson-html"><MathContent :html="disp(l.content)" /></view>
                      <view v-if="disp(l.exercises)" class="sub">
                        <text class="h4">{{ t("studio.exercises") }}</text>
                        <MathContent :html="disp(l.exercises)" />
                      </view>
                      <view v-if="disp(l.answers)" class="sub teacher">
                        <text class="h4">{{ t("studio.answers") }}</text>
                        <MathContent :html="disp(l.answers)" />
                      </view>
                    </template>
                    <text v-else-if="l.status === 'planned' || l.status === 'failed'" class="muted-s">{{ disp(l.goal) || t("studio.notWritten") }}</text>
                    <text v-else class="muted-s">{{ p.busy ? p.busy.label : "" }}</text>
                    <view v-if="l.status !== 'published' && l.status !== 'writing' && l.status !== 'reviewing'" class="l-actions">
                      <textarea v-if="l.status === 'awaiting'" v-model="notes[l.id]" class="note-in" auto-height :placeholder="t('studio.changeHint')" />
                      <view class="btns">
                        <view v-if="l.status === 'awaiting'" class="ghost" :class="{ disabled: !!p.busy }" @click="rewrite(l.id)">
                          {{ notes[l.id] ? t("studio.rewriteWithNote") : t("create.rewrite") }}
                        </view>
                        <view v-if="l.status === 'planned' || l.status === 'failed'" class="ghost" :class="{ disabled: !!p.busy || p.stage !== 'lessons' }" @click="rewrite(l.id)">
                          {{ t("studio.writeThis") }}
                        </view>
                        <view v-if="l.status === 'awaiting'" class="primary small" :class="{ disabled: busyAction }" @click="publish(l.id)">
                          {{ busyAction ? t("create.publishing") : t("studio.approve") }}
                        </view>
                      </view>
                    </view>
                    <view v-if="l.status === 'published' && p.course.id" class="l-actions">
                      <text class="link" @click="openCourse">{{ t("studio.seeInCourse") }} ›</text>
                    </view>
                  </view>
                </view>
              </view>
            </template>
          </view>

          <!-- questions -->
          <view v-if="tab === 'questions'" class="pane">
            <view v-if="!p.questions.length" class="empty">{{ t("studio.noQuestions") }}</view>
            <view v-for="q in p.questions" :key="q.id" class="q-row" :class="q.status">
              <text class="q-text">{{ q.text }}</text>
              <text v-if="q.status === 'answered'" class="q-ans">→ {{ q.answer }}</text>
              <view v-else class="q-opts">
                <text v-for="o in q.options" :key="o" class="q-opt" @click="answer(q.id, o)">{{ o }}</text>
              </view>
            </view>
            <view class="req">
              <text class="h3">{{ t("studio.requirements") }}</text>
              <text v-for="(v, k) in p.requirements" :key="k" class="req-row">{{ t("studio.req." + k) }}：{{ v }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from "vue";
import { onHide, onLoad, onShow, onUnload } from "@dcloudio/uni-app";
import { confirmAction } from "../../courseApi";
import AppShell from "../../components/AppShell.vue";
import MathContent from "../../components/MathContent.vue";
import {
  absolute, api, ApiError, type StudioChapter, type StudioFile, type StudioOutline, type StudioProject, type Text, token,
} from "../../api";
import { errorText, locale, t } from "../../i18n";

// Page query parameters must not fall through onto the layout component.
defineOptions({ inheritAttrs: false });

const STAGES = ["intake", "materials", "outline", "lessons"];
const TABS = ["materials", "outline", "lessons", "questions"] as const;
type Tab = (typeof TABS)[number];

const id = ref("");
const p = ref<StudioProject | null>(null);
const error = ref("");
const tab = ref<Tab>("materials");
const mpane = ref<"chat" | "dossier">("chat");
const draft = ref("");
const own = reactive<Record<string, string>>({});
const notes = reactive<Record<string, string>>({});
const openLesson = ref("");
const busyAction = ref(false);
const dragOver = ref(false);
const uploads = reactive({ total: 0, done: 0 });
const uploading = computed(() => uploads.total > 0 && uploads.done < uploads.total);
const roleEdits = ref(new Map<string, { role: string; chapters: number[] }>());
const ed = ref<StudioOutline | null>(null);  // the outline being edited
const dirty = ref(false);
let timer: ReturnType<typeof setTimeout> | null = null;

const stageIndex = computed(() => (p.value ? STAGES.indexOf(p.value.stage) : 0));
const lang = computed<"zh" | "en">(() => (p.value?.outline?.languages === "en" ? "en" : "zh"));
const disp = (tx?: Text) => (tx ? tx[locale.value] || tx.zh || tx.en || "" : "");
const courseTitle = computed(() => (p.value?.outline ? disp(p.value.outline.title) : p.value?.requirements.course_title || t("studio.untitled")));
const openQuestions = computed(() => (p.value?.questions || []).filter((q) => q.status === "open"));
// Scroll the conversation to the newest message whenever something arrives.
const lastMsgId = ref("");
watch(() => (p.value ? p.value.messages.length + openQuestions.value.length : 0), () => {
  lastMsgId.value = "";
  nextTick(() => { lastMsgId.value = "bottom"; });
});
const textbookName = computed(() => p.value?.files.find((f) => f.id === p.value?.materials.textbook)?.name || "");
const weeks = computed(() => {
  const map = new Map<number, string[]>();
  for (const c of ed.value?.chapters || []) for (const l of c.lessons) {
    const w = Number(l.week) || 0;
    map.set(w, [...(map.get(w) || []), l.title[lang.value] || ""]);
  }
  return [...map.entries()].sort((a, b) => (a[0] || 999) - (b[0] || 999)).map(([week, titles]) => ({ week, titles }));
});

function badge(tb: Tab): number {
  if (!p.value) return 0;
  if (tb === "questions") return openQuestions.value.length;
  if (tb === "lessons") return p.value.progress.awaiting || 0;
  if (tb === "materials") return p.value.files.filter((f) => f.confidence === "low" || f.error).length;
  return 0;
}

// --- loading and polling -------------------------------------------------------------------
function take(np: StudioProject) {
  const stageChanged = p.value && p.value.stage !== np.stage;
  p.value = np;
  if (!dirty.value) ed.value = np.outline ? JSON.parse(JSON.stringify(np.outline)) : null;
  // Show the part of the dossier that matters now.
  if (stageChanged || !tabChosen) tab.value = np.stage === "lessons" ? "lessons" : np.stage === "outline" ? "outline" : "materials";
  schedule();
}
let tabChosen = false;
watch(tab, () => { tabChosen = true; });

function schedule() {
  if (timer) clearTimeout(timer);
  if (p.value?.busy) timer = setTimeout(load, 2000);
}

async function load() {
  try {
    take(await api.studio(id.value));
    error.value = "";
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
    if (timer) clearTimeout(timer);
    timer = setTimeout(load, 5000);
  }
}

async function act(fn: () => Promise<StudioProject>) {
  error.value = "";
  try {
    take(await fn());
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  }
}

// --- conversation ----------------------------------------------------------------------------
function send() {
  const text = draft.value.trim();
  if (!text || p.value?.busy) return;
  draft.value = "";
  act(() => api.studioSay(id.value, text));
}
function answer(qid: string, text?: string) {
  if (!text || !text.trim()) return;
  act(() => api.studioAnswer(id.value, qid, text.trim()));
}
const start = () => act(() => api.studioStart(id.value));
const approveMaterials = () => act(() => api.studioApproveMaterials(id.value));
async function approveOutline() {
  busyAction.value = true;
  await act(() => api.studioApproveOutline(id.value));
  busyAction.value = false;
}
const writeNext = () => act(() => api.studioNext(id.value));
async function stop() {
  try { await api.studioStop(id.value); } catch { /* shown on next load */ }
  setTimeout(load, 600);
}

// --- materials ---------------------------------------------------------------------------------
function setRole(f: StudioFile, role: string) {
  const cur = roleEdits.value.get(f.id) || { role: f.role, chapters: f.chapters };
  roleEdits.value = new Map(roleEdits.value).set(f.id, { ...cur, role });
}
function setChapters(f: StudioFile, value: string) {
  const chapters = String(value || "").split(/[,，\s]+/).map(Number).filter((n) => n > 0 && n < 100);
  if (chapters.join(",") === f.chapters.join(",")) return;
  const cur = roleEdits.value.get(f.id) || { role: f.role, chapters: f.chapters };
  roleEdits.value = new Map(roleEdits.value).set(f.id, { ...cur, chapters });
}
async function saveMaterials() {
  const files = [...roleEdits.value.entries()].map(([fid, v]) => ({ id: fid, ...v }));
  const tb = files.find((f) => f.role === "main_textbook");
  roleEdits.value = new Map();
  await act(() => api.studioMaterials(id.value, files, tb ? tb.id : undefined));
}

// --- outline ------------------------------------------------------------------------------------
const emptyText = (): Text => ({ zh: "", en: "" });
function addLesson(c: StudioChapter) {
  c.lessons.push({ id: "", title: emptyText(), goal: emptyText(), week: 0, sections: [], status: "planned", content: {}, exercises: {},
    answers: {}, notes: "", error: "", review: null });
  dirty.value = true;
}
function addChapter() {
  ed.value?.chapters.push({ id: "", no: (ed.value?.chapters.length || 0) + 1, title: emptyText(), summary: emptyText(), lessons: [] });
  dirty.value = true;
}
function moveChapter(i: number, d: number) {
  const list = ed.value!.chapters;
  const j = i + d;
  if (j < 0 || j >= list.length) return;
  [list[i], list[j]] = [list[j], list[i]];
  dirty.value = true;
}
function moveLesson(c: StudioChapter, i: number, d: number) {
  const j = i + d;
  if (j < 0 || j >= c.lessons.length) return;
  [c.lessons[i], c.lessons[j]] = [c.lessons[j], c.lessons[i]];
  dirty.value = true;
}
function removeChapter(i: number) {
  if (ed.value!.chapters[i].lessons.some((l) => l.status === "published")) return;
  ed.value!.chapters.splice(i, 1);
  dirty.value = true;
}
function resetOutline() {
  dirty.value = false;
  ed.value = p.value?.outline ? JSON.parse(JSON.stringify(p.value.outline)) : null;
}
async function saveOutline() {
  if (!ed.value) return;
  const o = ed.value;
  o.chapters.forEach((c, i) => (c.no = i + 1));
  dirty.value = false;
  await act(() => api.studioOutline(id.value, o));
}

// --- lessons -------------------------------------------------------------------------------------
const deckFor = ref("");
const deckImgs = ref<string[]>([]);
const deckMsg = ref("");

function download(link: string) {
  const url = absolute(link);
  // #ifdef H5
  window.open(url, "_blank", "noopener");
  // #endif
  // #ifndef H5
  uni.downloadFile({ url, success: (r) => uni.openDocument({ filePath: r.tempFilePath, showMenu: true }) });
  // #endif
}

async function previewDeck(lid: string) {
  deckFor.value = lid;
  deckImgs.value = [];
  for (let n = 0; n < 120 && deckFor.value === lid; n++) {
    try {
      const d = await api.studioDeck(p.value!.id, lid);
      if (d.status === "ready") { deckImgs.value = (d.slides || []).map((x) => absolute(x.image)); deckMsg.value = ""; return; }
      if (d.status === "unavailable" || d.status === "failed") { deckMsg.value = t("studio.deckUnavailable"); return; }
      deckMsg.value = t("studio.deckConverting") + (d.total ? ` ${d.done || 0}/${d.total}` : "");
    } catch (e: any) { deckMsg.value = e?.message || String(e); return; }
    await new Promise((r) => setTimeout(r, 2000));
  }
}
function redoLab(lid: string) {
  act(() => api.studioRedoLab(id.value, lid));
}
function rewrite(lid: string) {
  const note = (notes[lid] || "").trim();
  notes[lid] = "";
  act(() => api.studioWrite(id.value, lid, note));
}
async function publish(lid: string) {
  busyAction.value = true;
  await act(() => api.studioPublish(id.value, lid));
  busyAction.value = false;
}
function setPace(mode: "manual" | "daily", hour: number) {
  let tz = "Asia/Shanghai";
  try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || tz; } catch { /* default */ }
  act(() => api.studioPace(id.value, mode, hour, tz));
}
function openCourse() {
  if (p.value?.course.id) uni.navigateTo({ url: `/pages/course/course?id=${p.value.course.id}&tab=modules` });
}

// --- files (browser only) ----------------------------------------------------------------------
type Picked = { file: File; path: string };
const skip = (name: string) => name.startsWith(".") || name.startsWith("~$") || name === "Thumbs.db" || name === "desktop.ini";
function pick(folder: boolean) {
  // #ifdef H5
  const input = document.createElement("input");
  input.type = "file";
  input.multiple = true;
  if (folder) (input as any).webkitdirectory = true;
  input.style.display = "none";
  document.body.appendChild(input);
  input.onchange = () => {
    const list = Array.from(input.files || []).map((f) => ({ file: f, path: (f as any).webkitRelativePath || f.name }));
    input.remove();
    upload(list);
  };
  input.click();
  // #endif
}
async function readEntry(entry: any, prefix = ""): Promise<Picked[]> {
  if (entry.isFile) return new Promise((res) => entry.file((f: File) => res([{ file: f, path: prefix + f.name }]), () => res([])));
  const reader = entry.createReader();
  const all: Picked[] = [];
  for (;;) {
    const batch: any[] = await new Promise((res) => reader.readEntries(res, () => res([])));
    if (!batch.length) break;
    for (const e of batch) all.push(...(await readEntry(e, prefix + entry.name + "/")));
  }
  return all;
}
async function onDrop(e: DragEvent) {
  dragOver.value = false;
  const list: Picked[] = [];
  for (const it of Array.from(e.dataTransfer?.items || [])) {
    const entry = (it as any).webkitGetAsEntry?.();
    if (entry) list.push(...(await readEntry(entry)));
    else if (it.kind === "file" && it.getAsFile()) list.push({ file: it.getAsFile()!, path: it.getAsFile()!.name });
  }
  upload(list);
}
async function upload(list: Picked[]) {
  list = list.filter((x) => !skip(x.file.name)).slice(0, 400);
  if (!list.length) return;
  uploads.total += list.length;
  const queue = [...list];
  const worker = async () => {
    while (queue.length) {
      const x = queue.shift()!;
      try {
        await api.studioUpload(id.value, x.file, x.path);
      } catch (e) {
        error.value = e instanceof ApiError ? e.code : "unknown";
      } finally {
        uploads.done++;
      }
    }
  };
  await Promise.all([worker(), worker(), worker()]);
  // Once the materials were read, the librarian sorts the new files at once (before that, "start" reads them all).
  try { take(await api.studioFilesDone(id.value)); } catch { await load(); }
}
function setTextbook(fid: string) {
  if (fid === p.value?.materials.textbook) return;
  act(() => api.studioMaterials(id.value, [], fid));
}
async function removeFile(f: { id: string; name: string }) {
  if (!(await confirmAction(t("studio.deleteFileConfirm", { name: f.name }), t("common.delete"), t("common.cancel")))) return;
  act(() => api.studioDeleteFile(id.value, f.id));
}

const size = (n: number) => (n > 1048576 ? `${(n / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`);

onLoad((q: any) => { id.value = String(q?.id || ""); });
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t("studio.title") });
  load();
});
onHide(() => { if (timer) clearTimeout(timer); });
onUnload(() => { if (timer) clearTimeout(timer); });
</script>

<style scoped>
.muted { color: var(--wq-muted); }
.muted-s { font-size: 12px; color: var(--wq-muted); }
.grow { flex: 1; min-width: 0; }
.alert { background: #fdecea; color: var(--wq-danger); padding: 8px 12px; border-radius: 8px; margin: 8px 0; font-size: 14px; }
.stages { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.stg { display: flex; align-items: center; gap: 6px; padding: 5px 12px; border-radius: 999px; background: #e8ecea; color: var(--wq-muted); font-size: 13px; }
.stg.on { background: var(--wq-ink); color: #fff; }
.stg.done { background: #dcefe5; color: var(--wq-ok); }
.stg-n { font-weight: 700; }
.working { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--wq-link); background: #e7f1f5; padding: 5px 12px; border-radius: 999px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--wq-accent); animation: pulse 1s ease-in-out infinite alternate; }
@keyframes pulse { to { opacity: .3; } }
.stop { color: var(--wq-danger); cursor: pointer; font-weight: 600; margin-left: 4px; }
.mtabs { display: none; }
.cols { display: grid; grid-template-columns: minmax(320px, 5fr) minmax(0, 7fr); gap: 16px; align-items: start; }

/* conversation */
.chat { background: #fff; border: 1px solid var(--wq-line); border-radius: 10px; display: flex; flex-direction: column; height: calc(100vh - 170px); min-height: 520px; position: sticky; top: 12px; }
.msgs { flex: 1; min-height: 0; padding: 14px; box-sizing: border-box; }
.msg { display: flex; flex-direction: column; margin-bottom: 12px; }
.msg.teacher { align-items: flex-end; }
.who { font-size: 11px; color: var(--wq-muted); margin: 0 0 3px 4px; }
.bubble { display: block; white-space: pre-wrap; line-height: 1.65; font-size: 14px; padding: 9px 12px; border-radius: 10px; max-width: 92%; background: #f1f4f3; color: var(--wq-ink); }
.msg.teacher .bubble { background: var(--wq-ink); color: #fff; }
.msg.system { align-items: center; }
.msg.system .bubble { background: transparent; color: var(--wq-muted); font-size: 12px; text-align: center; }
.msg.system.error .bubble { color: var(--wq-danger); }
.msg.report .bubble, .msg.lesson .bubble { background: #fff8e0; }
.qcard { border: 1px solid #f0d27a; background: #fffbea; border-radius: 10px; padding: 10px 12px; margin: 0 0 10px; }
.q-text { display: block; font-size: 14px; color: var(--wq-ink); font-weight: 600; line-height: 1.6; }
.q-opts { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.q-opt { padding: 4px 12px; border-radius: 999px; background: #fff; border: 1px solid var(--wq-line); font-size: 13px; cursor: pointer; }
.q-opt:hover { border-color: var(--wq-ink); }
.q-own { display: flex; gap: 6px; margin-top: 8px; }
.q-input { flex: 1; height: 32px; border: 1px solid var(--wq-line); border-radius: 6px; padding: 0 8px; font-size: 13px; background: #fff; }
.q-send { font-size: 13px; color: var(--wq-link); cursor: pointer; align-self: center; }
.drop { margin: 0 12px; border: 2px dashed #c5d0cc; border-radius: 8px; padding: 10px; display: flex; gap: 12px; align-items: center; justify-content: center; flex-wrap: wrap; font-size: 13px; color: var(--wq-muted); }
.drop.over { border-color: var(--wq-accent); background: #fffbea; }
.compose { display: flex; gap: 8px; padding: 10px 12px; align-items: flex-end; }
.input { flex: 1; min-height: 38px; max-height: 160px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 10px; font-size: 14px; background: #fafbfa; box-sizing: border-box; }
.send { background: var(--wq-ink); color: #fff; padding: 9px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; }
.next { padding: 10px 12px 14px; border-top: 1px solid var(--wq-line); display: flex; flex-direction: column; gap: 6px; }
.primary { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 10px 18px; border-radius: 8px; cursor: pointer; text-align: center; }
.primary.small { padding: 7px 14px; font-size: 14px; }
.ghost { border: 1px solid var(--wq-line); padding: 7px 14px; border-radius: 8px; cursor: pointer; color: var(--wq-ink); background: #fff; font-size: 14px; }
.disabled { opacity: .45; pointer-events: none; }
.hint, .pace-note { font-size: 12px; color: var(--wq-muted); text-align: center; }
.link { color: var(--wq-link); cursor: pointer; font-size: 13px; }

/* dossier */
.dossier { background: #fff; border: 1px solid var(--wq-line); border-radius: 10px; min-height: 520px; }
.tabs { display: flex; border-bottom: 1px solid var(--wq-line); padding: 0 8px; overflow-x: auto; }
.tab { padding: 12px 12px; font-size: 14px; color: var(--wq-muted); cursor: pointer; border-bottom: 2px solid transparent; white-space: nowrap; }
.tab.on { color: var(--wq-ink); border-bottom-color: var(--wq-ink); font-weight: 600; }
.badge { display: inline-block; min-width: 16px; padding: 0 5px; margin-left: 5px; border-radius: 999px; background: var(--wq-accent); color: var(--wq-ink); font-size: 11px; text-align: center; }
.pane { padding: 14px 16px 20px; }
.empty { color: var(--wq-muted); padding: 24px 0; text-align: center; }
.note { display: block; background: #f4f7f6; border-radius: 8px; padding: 10px 12px; font-size: 13px; line-height: 1.7; color: var(--wq-text); margin-bottom: 12px; white-space: pre-wrap; }
.h3 { display: block; font-weight: 600; color: var(--wq-ink); margin: 16px 0 8px; }
.h4 { display: block; font-weight: 600; color: var(--wq-ink); margin: 10px 0 4px; font-size: 14px; }
.ftable { border: 1px solid var(--wq-line); border-radius: 8px; overflow: hidden; }
.frow { display: flex; gap: 8px; align-items: center; padding: 8px 10px; border-top: 1px solid #eef1f0; }
.frow.fhead { background: #f4f6f5; border-top: 0; font-size: 12px; color: var(--wq-muted); font-weight: 600; }
.frow.low { background: #fffbea; }
.frow.bad { background: #fdf3f2; }
.f-name { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.fname { font-size: 13px; color: var(--wq-ink); word-break: break-all; }
.fsub { font-size: 11px; color: var(--wq-muted); }
.ferr { font-size: 12px; color: var(--wq-danger); }
.fwarn { font-size: 12px; color: #7a5a00; }
.f-role { width: 118px; flex-shrink: 0; }
.f-ch { width: 64px; flex-shrink: 0; }
.sel { width: 100%; height: 30px; border: 1px solid var(--wq-line); border-radius: 6px; background: #fff; font-size: 13px; }
.sel.small { width: auto; }
.chin { width: 100%; height: 30px; border: 1px solid var(--wq-line); border-radius: 6px; padding: 0 6px; font-size: 13px; box-sizing: border-box; }
.bar-save { display: flex; gap: 12px; align-items: center; justify-content: flex-end; margin-top: 10px; font-size: 13px; color: #7a5a00; }
.toc-ch { margin-bottom: 8px; }
.toc-c { display: block; font-weight: 600; font-size: 14px; color: var(--wq-ink); }
.toc-s { display: block; font-size: 13px; color: var(--wq-text); padding-left: 16px; }
.pg { color: var(--wq-muted); font-size: 11px; }
.o-title { width: 100%; height: 40px; font-size: 18px; font-weight: 700; border: 1px solid transparent; border-radius: 6px; padding: 0 8px; box-sizing: border-box; }
.o-title:hover, .o-in:hover { border-color: var(--wq-line); }
.o-ch { border-top: 1px solid var(--wq-line); padding: 10px 0; }
.o-ch-head { display: flex; align-items: center; gap: 6px; }
.o-no { width: 24px; height: 24px; border-radius: 6px; background: var(--wq-ink); color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.o-in { flex: 1; width: 100%; height: 32px; border: 1px solid transparent; border-radius: 6px; padding: 0 6px; font-size: 14px; box-sizing: border-box; }
.o-in.strong { font-weight: 600; }
.o-in.goal { font-size: 12px; color: var(--wq-muted); height: 26px; }
.o-les { display: flex; align-items: flex-start; gap: 6px; margin: 4px 0 4px 30px; }
.o-les.locked { opacity: .7; }
.o-week { width: 44px; height: 30px; border: 1px solid var(--wq-line); border-radius: 6px; font-size: 12px; text-align: center; flex-shrink: 0; }
.o-sec { display: block; font-size: 11px; color: var(--wq-muted); padding-left: 6px; }
.o-act { color: var(--wq-muted); cursor: pointer; padding: 4px 5px; font-size: 13px; }
.o-act.danger { color: var(--wq-danger); }
.calendar { margin-top: 12px; }
.cal-w { display: flex; gap: 10px; padding: 5px 0; border-bottom: 1px solid #f0f2f1; font-size: 13px; }
.cal-n { width: 64px; flex-shrink: 0; color: var(--wq-muted); }
.cal-l { flex: 1; color: var(--wq-text); }
.pace { background: #f7f9f8; border-radius: 8px; padding: 4px 12px 10px; margin-bottom: 12px; }
.pace .h3 { margin-top: 8px; }
.pace-row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 6px; }
.chip2 { padding: 5px 12px; border-radius: 999px; border: 1px solid var(--wq-line); background: #fff; font-size: 13px; cursor: pointer; }
.chip2.on { background: var(--wq-ink); color: #fff; border-color: var(--wq-ink); }
.l-ch { margin-bottom: 12px; }
.l-ch-t { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 4px; }
.l-row { border: 1px solid var(--wq-line); border-radius: 8px; margin: 5px 0; }
.l-row.open { border-color: #b9c6c2; }
.l-head { display: flex; gap: 8px; align-items: center; padding: 8px 10px; cursor: pointer; }
.l-week { font-size: 11px; color: var(--wq-muted); width: 38px; flex-shrink: 0; }
.l-title { flex: 1; font-size: 14px; color: var(--wq-ink); }
.st { font-size: 12px; padding: 1px 8px; border-radius: 999px; background: #eef1f0; color: var(--wq-muted); white-space: nowrap; }
.st.writing, .st.reviewing { background: #e7f1f5; color: var(--wq-link); }
.st.awaiting { background: #fff3d6; color: #7a5a00; }
.st.published { background: #dcefe5; color: var(--wq-ok); }
.st.failed { background: #fdecea; color: var(--wq-danger); }
.l-body { border-top: 1px solid var(--wq-line); padding: 10px 14px 12px; }
.review { border-radius: 8px; padding: 8px 12px; margin-bottom: 10px; font-size: 13px; }
.review.pass { background: #eef8f2; color: var(--wq-ok); }
.review.revise { background: #fff3d6; color: #7a5a00; }
.rv-h { display: block; font-weight: 600; }
.rv-s, .rv-i { display: block; line-height: 1.6; }
.deliv { margin: 8px 0 12px; }
.dv-list { display: flex; flex-direction: column; gap: 6px; margin: 6px 0 8px; }
.dv { display: flex; align-items: center; gap: 10px; border: 1px solid #e3e8e6; border-radius: 6px; padding: 8px 12px; cursor: pointer; background: #fff; }
.dv:hover { border-color: #1e2761; }
.dv-k { font-size: 12px; color: #fff; background: #1e2761; border-radius: 4px; padding: 1px 8px; flex-shrink: 0; }
.dv-n { flex: 1; font-size: 13px; word-break: break-all; }
.dv-t { font-size: 11px; color: #a15c00; background: #fff4de; border-radius: 4px; padding: 1px 6px; }
.dv-d { color: #1e2761; font-weight: 700; }
.dv-video { width: 100%; max-width: 720px; aspect-ratio: 16 / 9; display: block; margin: 4px 0 10px; background: #0f1419; border-radius: 6px; }
.dv-deck { white-space: nowrap; margin-top: 8px; width: 100%; max-width: 100%; }
.dv-img { display: inline-block; width: 320px; margin-right: 8px; border: 1px solid #e3e8e6; border-radius: 4px; }
.lesson-html { max-height: 520px; overflow: auto; border: 1px solid #f0f2f1; border-radius: 6px; padding: 4px 12px; }
.sub { margin-top: 8px; }
.sub.teacher { background: #fffbea; border-radius: 6px; padding: 2px 10px; }
.l-actions { margin-top: 10px; }
.note-in { width: 100%; min-height: 38px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 10px; font-size: 13px; box-sizing: border-box; }
.btns { display: flex; gap: 8px; justify-content: flex-end; margin-top: 8px; flex-wrap: wrap; }
.q-row { padding: 10px 0; border-bottom: 1px solid #f0f2f1; }
.q-row.answered .q-text { font-weight: 400; color: var(--wq-muted); }
.q-ans { display: block; color: var(--wq-ok); font-size: 13px; margin-top: 4px; }
.req { margin-top: 10px; }
.req-row { display: block; font-size: 13px; color: var(--wq-text); padding: 2px 0; white-space: pre-wrap; }

@media (max-width: 1180px) { .cols { grid-template-columns: 1fr; } .chat { position: static; height: 70vh; } }
@media (max-width: 860px) {
  .mtabs { display: flex; gap: 6px; margin-bottom: 8px; }
  .mtabs text { flex: 1; text-align: center; padding: 8px; border-radius: 8px; background: #e8ecea; color: var(--wq-muted); }
  .mtabs text.on { background: var(--wq-ink); color: #fff; }
  .hide { display: none; }
  .f-role { width: 96px; }
}
.dv-lab { display: block; width: 100%; height: 780px; border: 1px solid var(--wq-line); border-radius: 8px; margin-top: 10px; background: #fff; }
.mtools { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; padding: 10px 12px; margin-bottom: 10px; border: 1px dashed var(--wq-line); border-radius: 8px; background: #fbfcfc; }
.mtools.over { border-color: var(--wq-link); background: #eef6f9; }
.mt-btn { color: var(--wq-link); cursor: pointer; font-size: 14px; font-weight: 600; }
.mt-btn.right { margin-left: auto; }
.f-act { width: 80px; display: flex; gap: 10px; justify-content: flex-end; }
.fa { cursor: pointer; color: var(--wq-link); font-size: 15px; }
.fa.del { color: var(--wq-muted); }
.fa.star { color: #b9c2bf; }
.fa.star.on { color: var(--wq-accent); }
.fa.del:hover { color: var(--wq-danger); }
</style>
