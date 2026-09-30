<template>
  <AppShell nav="courses" :course="d" tab="modules" :crumb="crumb">
    <view v-if="loading && !a" class="muted">{{ t("common.loading") }}</view>
    <view v-else-if="error && !a" class="state">
      <text class="error">{{ errorText(error) }}</text>
      <view class="btn" @click="load">{{ t("common.retry") }}</view>
    </view>
    <view v-else-if="a" class="viewer" :class="{ wide: fileKind === 'lab' || fileKind === 'slides' }">
      <view class="head">
        <text class="kind">{{ t("kind." + kindKey) }}</text>
        <text v-if="a.hidden" class="tag teacher">{{ t("course.teacherOnly") }}</text>
        <text v-if="canEdit" class="edit-link" @click="editThis">✎ {{ t("common.edit") }}</text>
      </view>
      <text class="h1">{{ a.name }}</text>

      <!-- Reading page -->
      <view v-if="a.type === 'page'" class="paper"><MathContent :html="a.html || ''" /></view>

      <!-- External link -->
      <view v-else-if="a.type === 'url'" class="paper">
        <RichContent v-if="a.intro" :html="a.intro" />
        <view class="primary" @click="openLink(a.url || '')">{{ t("activity.openLink") }} ↗</view>
        <text class="small">{{ a.url }}</text>
      </view>

      <!-- Assignment: hand in, or (teachers) grade -->
      <AssignmentView v-else-if="a.type === 'assign'" :cmid="id" />

      <!-- Quiz -->
      <QuizView v-else-if="a.type === 'quiz'" :cmid="id" :course-id="courseId" />

      <!-- Files -->
      <view v-else-if="a.type === 'resource' && file">
        <!-- 讲解视频: Chinese / English voice, subtitles -->
        <LecturePlayer v-if="a.lecture" :lecture="a.lecture" />

        <!-- Video -->
        <view v-else-if="fileKind === 'video'" class="player">
          <video class="video" :src="absolute(file.url)" controls preload="metadata" />
        </view>

        <!-- PDF -->
        <view v-else-if="fileKind === 'pdf'">
          <!-- #ifdef H5 -->
          <PdfViewer :url="absolute(file.url)" />
          <!-- #endif -->
          <!-- #ifndef H5 -->
          <view class="primary" @click="download(file.url, file.name)">{{ t("activity.open") }}</view>
          <!-- #endif -->
        </view>

        <!-- Virtual lab, running inside the page -->
        <view v-else-if="fileKind === 'lab'">
          <!-- #ifdef H5 -->
          <view ref="labBox" class="lab-box">
            <iframe class="lab" :src="absolute(file.lab_url || '')" :title="a.name"
              sandbox="allow-scripts allow-popups allow-forms allow-modals allow-downloads" allow="fullscreen" />
          </view>
          <view class="lab-bar">
            <text class="small">{{ t("viewer.labNote") }}</text>
            <view class="ghost" @click="fullscreen">⛶ {{ t("viewer.fullscreen") }}</view>
          </view>
          <!-- #endif -->
          <!-- #ifndef H5 -->
          <text class="muted block">{{ t("viewer.labWebOnly") }}</text>
          <!-- #endif -->
        </view>

        <!-- Image -->
        <view v-else-if="fileKind === 'image'" class="paper center">
          <image class="img" :src="absolute(file.url)" mode="widthFix" />
        </view>

        <!-- Slides: presented in the page, with the unit's virtual lab one click away -->
        <SlidePresenter v-else-if="fileKind === 'slides'" :cmid="id" :labs="unitLabs" />

        <!-- Word, Excel and other files -->
        <view v-else class="paper">
          <view v-for="f in a.files" :key="f.url" class="file">
            <text class="f-icon">{{ KIND_ICON[f.kind] || "▢" }}</text>
            <text class="file-name">{{ f.name }}</text>
            <text class="file-size">{{ size(f.size) }}</text>
            <view class="btn" @click="download(f.url, f.name)">{{ t("activity.download") }}</view>
          </view>
        </view>
      </view>

      <!-- Kinds of activity WenQuest does not use -->
      <view v-else class="paper">
        <RichContent v-if="a.intro" :html="a.intro" />
        <text class="muted block">{{ t("activity.unsupported") }}</text>
      </view>

      <view v-if="ctx" class="pager">
        <view v-if="prevMod" class="pg" @click="go(prevMod.id)">‹ {{ prevMod.name }}</view>
        <view v-else class="pg" @click="openUnit">‹ {{ ctx.section.name }}</view>
        <view v-if="nextMod" class="pg right" @click="go(nextMod.id)">{{ nextMod.name }} ›</view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import MathContent from "../../components/MathContent.vue";
import RichContent from "../../components/RichContent.vue";
import SlidePresenter from "../../components/SlidePresenter.vue";
import LecturePlayer from "../../components/LecturePlayer.vue";
import AssignmentView from "../../components/work/AssignmentView.vue";
import QuizView from "../../components/work/QuizView.vue";
// #ifdef H5
import PdfViewer from "../../components/PdfViewer.vue";
// #endif
import { absolute, api, ApiError, type Activity, token } from "../../api";
import { errorText, formatDate, locale, t } from "../../i18n";
import { type CourseData, findModule, isTeacher, KIND_ICON, loadCourse, moduleKind, rememberVisit, visibleModules } from "../../store";

// Page query parameters (id, course, tab) must not fall through onto the layout component.
defineOptions({ inheritAttrs: false });

const id = ref(0);
const courseId = ref(0);
const a = ref<Activity | null>(null);
const d = ref<CourseData | null>(null);
const loading = ref(true);
const error = ref("");
const labBox = ref<any>(null);

const file = computed(() => (a.value?.files || [])[0] || null);
const fileKind = computed(() => file.value?.kind || "file");
const kindKey = computed(() => {
  if (!a.value) return "file";
  if (a.value.type === "resource") return a.value.lecture ? "lecture" : fileKind.value;
  if (a.value.type === "page") return "reading";
  if (a.value.type === "url") return "link";
  return ["assign", "quiz", "forum"].includes(a.value.type) ? a.value.type : "file";
});
const ctx = computed(() => (d.value ? findModule(d.value, id.value) : null));
const canEdit = computed(() => !!a.value && isTeacher(d.value) && ["page", "url", "assign", "quiz"].includes(a.value.type));
function editThis() {
  if (!a.value) return;
  uni.navigateTo({ url: `/pages/edit/${a.value.type === "quiz" ? "quiz" : "edit"}?course=${courseId.value}&cmid=${id.value}` });
}
const siblings = computed(() => (d.value && ctx.value ? visibleModules(d.value, ctx.value.section) : []));
const pos = computed(() => siblings.value.findIndex((m) => m.id === id.value));
const prevMod = computed(() => (pos.value > 0 ? siblings.value[pos.value - 1] : null));
const nextMod = computed(() => (pos.value >= 0 && pos.value < siblings.value.length - 1 ? siblings.value[pos.value + 1] : null));
// The unit's virtual labs, for the presenter's "slides | virtual lab" switch.
const unitLabs = computed(() => (d.value && ctx.value
  ? visibleModules(d.value, ctx.value.section).filter((m) => moduleKind(m) === "lab").map((m) => ({ id: m.id, name: m.name || "" }))
  : []));
const crumb = computed(() => (ctx.value ? `${ctx.value.section.name} › ${a.value?.name || ""}` : a.value?.name || ""));

async function load() {
  loading.value = true;
  error.value = "";
  try {
    a.value = await api.activity(id.value);
    uni.setNavigationBarTitle({ title: a.value.name });
    const cid = courseId.value || a.value.course_id;
    if (a.value.type === "forum") {
      // Discussion forums live under the course's Discussions menu.
      return uni.redirectTo({ url: `/pages/course/course?id=${cid}&tab=discussions&forum=${id.value}` });
    }
    courseId.value = cid;
    rememberVisit(cid, id.value);
    loadCourse(cid).then((x) => { d.value = x; }).catch(() => {});
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

function go(cmid: number) {
  uni.redirectTo({ url: `/pages/activity/activity?id=${cmid}&course=${courseId.value}` });
}
function openUnit() {
  if (ctx.value) uni.redirectTo({ url: `/pages/unit/unit?course=${courseId.value}&section=${ctx.value.section.id}` });
}

function fullscreen() {
  // #ifdef H5
  const el = (labBox.value?.$el || labBox.value) as HTMLElement | null;
  el?.requestFullscreen?.();
  // #endif
}

function openLink(url: string) {
  if (!url) return;
  // #ifdef H5
  window.open(url, "_blank", "noopener");
  // #endif
  // #ifndef H5
  uni.setClipboardData({ data: url, success: () => uni.showToast({ title: t("activity.linkCopied"), icon: "none" }) });
  // #endif
}

function download(url: string, name: string) {
  const full = absolute(url);
  // #ifdef H5
  const link = document.createElement("a");
  link.href = full;
  link.download = name;
  link.click();
  // #endif
  // #ifndef H5
  uni.downloadFile({ url: full, success: (r) => uni.openDocument({ filePath: r.tempFilePath }) });
  // #endif
}

const size = (n: number) => (n > 1048576 ? `${(n / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`);

onLoad((q: any) => {
  id.value = Number(q?.id || 0);
  courseId.value = Number(q?.course || 0);
});
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  load();
});
watch(locale, load);
</script>

<style scoped>
.viewer { max-width: 900px; }
.viewer.wide { max-width: none; }
.head { display: flex; align-items: center; gap: 10px; }
.kind { font-size: 12px; letter-spacing: 1px; color: var(--wq-muted); }
.edit-link { margin-left: auto; font-size: 13px; color: #fff; background: var(--wq-ink); padding: 3px 12px; border-radius: 6px; cursor: pointer; }
.tag { font-size: 12px; padding: 1px 8px; border-radius: 999px; }
.tag.teacher { background: #fff3d6; color: #7a5a00; }
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); margin: 4px 0 18px; line-height: 1.35; }
.paper { background: #fff; border: 1px solid var(--wq-line); border-radius: 6px; padding: 24px 26px; }
.paper.center { text-align: center; }
.muted { color: var(--wq-muted); }
.block { display: block; margin-bottom: 16px; }
.state { display: flex; align-items: center; gap: 12px; }
.error { color: var(--wq-danger); }
.btn { padding: 6px 14px; border-radius: 8px; background: var(--wq-ink); color: #fff; font-size: 14px; cursor: pointer; flex-shrink: 0; }
.ghost { padding: 6px 14px; border-radius: 8px; border: 1px solid var(--wq-line); background: #fff; color: var(--wq-ink); font-size: 14px; cursor: pointer; }
.primary { display: inline-block; margin-top: 16px; background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
.small { display: block; font-size: 12px; color: var(--wq-muted); word-break: break-all; }
.due { display: flex; gap: 12px; align-items: baseline; padding: 10px 14px; background: #fff8e0; border-radius: 8px; margin-bottom: 16px; }
.due-label { font-size: 13px; color: #7a5a00; }
.due-value { font-size: 15px; color: var(--wq-ink); font-weight: 600; }
.file { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--wq-line); }
.file:last-child { border-bottom: 0; }
.f-icon { width: 28px; text-align: center; color: var(--wq-muted); }
.file-name { flex: 1; color: var(--wq-ink); word-break: break-all; }
.file-size { font-size: 12px; color: var(--wq-muted); }
.player { background: #000; border-radius: 6px; overflow: hidden; }
.video { width: 100%; aspect-ratio: 16 / 9; display: block; }
.img { max-width: 100%; }
.lab-box { border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; background: #fff; height: calc(100vh - 210px); min-height: 560px; }
.lab-box:fullscreen { border-radius: 0; height: 100vh; }
.lab { width: 100%; height: 100%; border: 0; display: block; }
.lab-bar { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-top: 8px; }
.pager { display: flex; justify-content: space-between; gap: 12px; margin-top: 28px; padding-top: 14px; border-top: 1px solid var(--wq-line); }
.pg { color: var(--wq-link); cursor: pointer; max-width: 48%; }
.pg.right { margin-left: auto; text-align: right; }
@media (max-width: 860px) { .paper { padding: 18px 16px; } .lab-box { height: 75vh; min-height: 480px; } }
</style>
