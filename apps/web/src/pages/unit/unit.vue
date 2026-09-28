<template>
  <AppShell nav="courses" :course="d" tab="modules" :crumb="section ? section.name : ''">
    <view v-if="!d || !section" class="muted">{{ error ? errorText(error) : t("common.loading") }}</view>
    <view v-else class="unit">
      <view class="banner">
        <view class="b-title">
          <text class="b-no">{{ t("unit.number", { n: unitIndex + 1 }) }}</text>
          <view class="b-dots" />
          <text class="b-name">{{ section.name }}</text>
        </view>
        <view class="b-bar"><view class="b-fill" :style="{ width: progress + '%' }" /></view>
        <text class="b-prog">{{ t("unit.progress", { done: doneCount, total: trackable.length }) }}</text>
      </view>

      <view class="blocks">
        <view v-if="section.summary" class="block">
          <text class="bh">{{ t("unit.intro") }}</text>
          <text class="intro">{{ section.summary }}</text>
        </view>

        <!-- Videos: watch right here -->
        <view v-if="groups.video.length" class="block">
          <text class="bh">{{ t("unit.videos") }}</text>
          <view class="tabs">
            <view v-for="(m, i) in groups.video" :key="m.id" class="vtab" :class="{ on: i === videoIndex }" @click="playVideo(i)">{{ m.name }}</view>
          </view>
          <view class="player">
            <!-- #ifdef H5 -->
            <video v-if="videoUrl" :key="videoUrl" class="video" :src="videoUrl" controls preload="metadata" />
            <!-- #endif -->
            <!-- #ifndef H5 -->
            <video v-if="videoUrl" class="video" :src="videoUrl" controls />
            <!-- #endif -->
            <text v-if="!videoUrl" class="muted pad">{{ t("common.loading") }}</text>
          </view>
        </view>

        <view v-if="groups.reading.length" class="block">
          <text class="bh">{{ t("unit.readings") }}</text>
          <view class="list"><ModuleRow v-for="m in groups.reading" :key="m.id" :m="m" :course-id="courseId" /></view>
        </view>

        <view v-if="groups.slides.length" class="block">
          <text class="bh">{{ t("unit.slides") }}</text>
          <view class="list"><ModuleRow v-for="m in groups.slides" :key="m.id" :m="m" :course-id="courseId" /></view>
        </view>

        <view v-if="groups.lab.length || groups.guides.length" class="block">
          <text class="bh">{{ t("unit.labs") }}</text>
          <view class="labs">
            <view v-for="m in groups.lab" :key="m.id" class="lab" @click="openModule(m.id)">
              <text class="lab-glyph">⚗</text>
              <view class="lab-text">
                <text class="lab-name">{{ m.name }}</text>
                <text class="lab-go">{{ t("course.runLab") }} ›</text>
              </view>
            </view>
          </view>
          <view v-if="groups.guides.length" class="list guides">
            <text class="g-sub">{{ t("course.labGuides") }}</text>
            <ModuleRow v-for="m in groups.guides" :key="m.id" :m="m" :course-id="courseId" />
          </view>
        </view>

        <view v-if="groups.assign.length" class="block">
          <text class="bh">{{ t("unit.assignments") }}</text>
          <view class="list"><ModuleRow v-for="m in groups.assign" :key="m.id" :m="m" :course-id="courseId" /></view>
        </view>

        <view v-if="groups.other.length" class="block">
          <text class="bh">{{ t("unit.materials") }}</text>
          <view class="list"><ModuleRow v-for="m in groups.other" :key="m.id" :m="m" :course-id="courseId" /></view>
        </view>

        <view v-if="groups.teacher.length" class="block teacher">
          <text class="bh">{{ t("unit.teacherOnly") }}</text>
          <text class="note">{{ t("unit.teacherOnlyNote") }}</text>
          <view class="list"><ModuleRow v-for="m in groups.teacher" :key="m.id" :m="m" :course-id="courseId" /></view>
        </view>
      </view>

      <view class="pager">
        <view v-if="prev" class="pg" @click="goUnit(prev)">‹ {{ prev.name }}</view>
        <view v-else />
        <view v-if="next" class="pg" @click="goUnit(next)">{{ next.name }} ›</view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import ModuleRow from "../../components/ModuleRow.vue";
import { absolute, api, ApiError, type Module, type Section, token } from "../../api";
import { errorText, locale, t } from "../../i18n";
import { type CourseData, loadCourse, moduleKind, studentPreview, units, visibleModules } from "../../store";

// Page query parameters (id, course, tab) must not fall through onto the layout component.
defineOptions({ inheritAttrs: false });

const courseId = ref(0);
const sectionId = ref(0);
const d = ref<CourseData | null>(null);
const error = ref("");
const videoIndex = ref(0);
const videoUrl = ref("");

const section = computed(() => d.value?.sections.find((s) => s.id === sectionId.value) || null);
const unitList = computed(() => (d.value ? units(d.value) : []));
const unitIndex = computed(() => unitList.value.findIndex((s) => s.id === sectionId.value));
const prev = computed(() => (unitIndex.value > 0 ? unitList.value[unitIndex.value - 1] : null));
const next = computed(() => (unitIndex.value >= 0 && unitIndex.value < unitList.value.length - 1 ? unitList.value[unitIndex.value + 1] : null));

const groups = computed(() => {
  const g: Record<string, Module[]> = { video: [], reading: [], slides: [], lab: [], guides: [], assign: [], other: [], teacher: [] };
  if (!d.value || !section.value) return g;
  for (const m of visibleModules(d.value, section.value)) {
    if (m.hidden) { g.teacher.push(m); continue; }
    const k = moduleKind(m);
    if (k === "video") g.video.push(m);
    else if (k === "reading") g.reading.push(m);
    else if (k === "slides" || k === "pdf") g.slides.push(m);
    else if (k === "lab") g.lab.push(m);
    else if (k === "assign") g.assign.push(m);
    else if (["doc", "sheet", "pdf"].includes(k) && /实验|lab|报告|report|量规|rubric/i.test(m.name || "")) g.guides.push(m);
    else g.other.push(m);
  }
  return g;
});
const trackable = computed(() => (d.value && section.value ? visibleModules(d.value, section.value).filter((m) => m.has_completion) : []));
const doneCount = computed(() => trackable.value.filter((m) => m.completed).length);
const progress = computed(() => (trackable.value.length ? Math.round((doneCount.value / trackable.value.length) * 100) : 0));

async function playVideo(i: number) {
  videoIndex.value = i;
  videoUrl.value = "";
  const m = groups.value.video[i];
  if (!m) return;
  try {
    const a = await api.activity(m.id);
    const f = (a.files || []).find((x) => x.kind === "video") || (a.files || [])[0];
    videoUrl.value = f ? absolute(f.url) : "";
  } catch { /* keep the loading text; the row below still opens it */ }
}

async function load(force = false) {
  error.value = "";
  try {
    d.value = await loadCourse(courseId.value, force);
    if (section.value) uni.setNavigationBarTitle({ title: section.value.name });
    if (groups.value.video.length && !videoUrl.value) playVideo(videoIndex.value);
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  }
}

const openModule = (cmid: number) => uni.navigateTo({ url: `/pages/activity/activity?id=${cmid}&course=${courseId.value}` });
const goUnit = (s: Section) => uni.redirectTo({ url: `/pages/unit/unit?course=${courseId.value}&section=${s.id}` });

onLoad((q: any) => {
  courseId.value = Number(q?.course || 0);
  sectionId.value = Number(q?.section || 0);
});
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  load();
});
watch(locale, () => { videoUrl.value = ""; load(true); });
watch(studentPreview, () => { videoIndex.value = 0; videoUrl.value = ""; if (groups.value.video.length) playVideo(0); });
</script>

<style scoped>
.muted { color: var(--wq-muted); }
.pad { display: block; padding: 60px 0; text-align: center; color: #a9bcc2; }
.banner { background: #0d1a20; color: #fff; border-radius: 4px; overflow: hidden; padding: 22px 26px 18px;
  background-image: radial-gradient(circle at 12% 70%, rgba(242,183,5,.5) 0 5px, transparent 6px), radial-gradient(circle at 78% 30%, rgba(92,184,214,.6) 0 6px, transparent 7px),
  repeating-linear-gradient(115deg, transparent 0 38px, rgba(92,184,214,.1) 38px 39px), linear-gradient(90deg, #0a2530, #050e12 60%, #0a1e2a); }
.b-title { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.b-no { font-weight: 700; font-size: 18px; color: var(--wq-accent); font-family: "IBM Plex Mono", Menlo, monospace; }
.b-dots { width: 6px; height: 30px; background: radial-gradient(circle, #5cb8d6 2.5px, transparent 3px) 0 0 / 6px 12px repeat-y; }
.b-name { font-size: 30px; font-weight: 500; line-height: 1.25; }
.b-bar { height: 4px; background: rgba(255,255,255,.12); border-radius: 2px; margin-top: 18px; overflow: hidden; }
.b-fill { height: 100%; background: var(--wq-accent); }
.b-prog { display: block; font-size: 12px; color: #a9bcc2; margin-top: 6px; }
.blocks { padding: 4px 0 0; }
.block { margin-top: 28px; }
.bh { display: block; font-size: 21px; font-weight: 500; color: var(--wq-ink); padding-bottom: 8px; margin-bottom: 12px; border-bottom: 3px solid #5cb8d6; }
.intro { display: block; color: var(--wq-text); line-height: 1.8; }
.tabs { display: flex; gap: 6px; flex-wrap: wrap; }
.vtab { padding: 8px 16px; border: 1px solid #111; background: #111; color: #fff; border-radius: 3px 3px 0 0; cursor: pointer; font-size: 14px; }
.vtab.on { background: #fff; color: var(--wq-ink); border-color: var(--wq-line); border-bottom-color: #fff; }
.player { border: 1px solid var(--wq-line); margin-top: -1px; background: #000; }
.video { width: 100%; aspect-ratio: 16 / 9; display: block; background: #000; }
.list { background: #fff; border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; }
.list :deep(.row) + :deep(.row) { border-top: 1px solid var(--wq-line); }
.labs { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; }
.lab { display: flex; gap: 14px; align-items: center; padding: 14px 16px; background: #0d1a20; color: #fff; border-radius: 6px; cursor: pointer;
  background-image: linear-gradient(rgba(92,184,214,.12) 1px, transparent 1px), linear-gradient(90deg, rgba(92,184,214,.12) 1px, transparent 1px); background-size: 16px 16px; }
.lab:hover { box-shadow: 0 6px 18px rgba(13,26,32,.25); }
.lab-glyph { font-size: 28px; color: #5cb8d6; }
.lab-text { display: flex; flex-direction: column; min-width: 0; }
.lab-name { font-weight: 600; }
.lab-go { font-size: 13px; color: var(--wq-accent); }
.guides { margin-top: 12px; }
.g-sub { display: block; font-size: 13px; color: var(--wq-muted); padding: 10px 14px 4px; }
.teacher .bh { border-bottom-color: #f2b705; }
.note { display: block; font-size: 13px; color: #7a5a00; margin: -4px 0 10px; }
.pager { display: flex; justify-content: space-between; gap: 12px; margin-top: 36px; padding-top: 16px; border-top: 1px solid var(--wq-line); }
.pg { color: var(--wq-link); cursor: pointer; max-width: 48%; }
@media (max-width: 860px) { .b-name { font-size: 22px; } }
</style>
