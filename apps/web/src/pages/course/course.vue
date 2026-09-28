<template>
  <AppShell nav="courses" :course="d" :tab="tab" :crumb="d ? t('menu.' + tab) : ''" :title="t('common.loading')">
    <view v-if="loading && !d" class="muted">{{ t("common.loading") }}</view>
    <view v-else-if="error && !d" class="state">
      <text class="error">{{ errorText(error) }}</text>
      <view class="btn" @click="load(true)">{{ t("common.retry") }}</view>
    </view>

    <template v-else-if="d">
      <!-- ================= Home ================= -->
      <view v-if="tab === 'home'" class="home">
        <view class="banner">
          <view class="b-text">
            <text class="b-code">{{ d.info.shortname }}</text>
            <text class="b-title">{{ d.info.name }}</text>
            <text class="b-meta">
              <text v-if="d.info.teachers.length">{{ t("course.teachers") }}：{{ d.info.teachers.join("、") }} · </text>{{ t("course.unitCount", { n: unitList.length }) }}
            </text>
          </view>
          <image v-if="d.info.image" class="b-img" :src="absolute(d.info.image)" mode="aspectFill" />
          <view v-else class="b-art">
            <view class="b-arc a1" /><view class="b-arc a2" /><view class="b-dot" />
          </view>
        </view>
        <view class="cards">
          <view v-if="syllabus || d.info.summary" class="card" @click="goTab('syllabus')">
            <text class="c-icon">▤</text>
            <text class="c-title">{{ t("menu.syllabus") }}</text>
            <text class="c-text">{{ t("course.cardSyllabus") }}</text>
            <text class="c-btn">{{ t("course.view") }}</text>
          </view>
          <view class="card" @click="resume">
            <text class="c-icon">▶</text>
            <text class="c-title">{{ last ? t("course.continue") : t("course.start") }}</text>
            <text class="c-text">{{ resumeText }}</text>
            <text class="c-btn">{{ t("course.enter") }}</text>
          </view>
          <view class="card" @click="goTab(counts.lab ? 'labs' : 'slides')">
            <text class="c-icon">{{ counts.lab ? "⚗" : "◧" }}</text>
            <text class="c-title">{{ counts.lab ? t("menu.labs") : t("menu.slides") }}</text>
            <text class="c-text">{{ counts.lab ? t("course.cardLabs", { n: counts.lab }) : t("course.cardSlides", { n: counts.slides }) }}</text>
            <text class="c-btn">{{ t("course.view") }}</text>
          </view>
        </view>

        <text class="h2">{{ t("course.units") }}</text>
        <view class="unit-list">
          <view v-for="(s, i) in unitList" :key="s.id" class="unit" @click="openUnit(s)">
            <text class="u-no">{{ String(i + 1).padStart(2, "0") }}</text>
            <view class="u-body">
              <text class="u-name">{{ s.name }}</text>
              <text class="u-meta">{{ unitMeta(s) }}</text>
            </view>
            <text v-if="!s.visible" class="tag teacher">{{ t("course.teacherOnly") }}</text>
            <text class="chev">›</text>
          </view>
        </view>

        <view v-if="d.info.summary" class="about">
          <text class="h2">{{ t("course.about") }}</text>
          <MathContent :html="d.info.summary" />
        </view>
      </view>

      <!-- ================= Syllabus ================= -->
      <view v-else-if="tab === 'syllabus'">
        <text class="h1">{{ t("menu.syllabus") }}</text>
        <view v-if="d.info.summary" class="panel-block"><MathContent :html="d.info.summary" /></view>
        <view v-if="syllabus" class="list">
          <text v-if="syllabus.summary" class="sec-summary">{{ syllabus.summary }}</text>
          <ModuleRow v-for="m in visibleModules(d, syllabus)" :key="m.id" :m="m" :course-id="id" />
        </view>
        <text v-if="!syllabus && !d.info.summary" class="muted">{{ t("course.nothing") }}</text>
      </view>

      <!-- ================= Modules ================= -->
      <view v-else-if="tab === 'modules'">
        <view class="h1-row">
          <text class="h1">{{ t("menu.modules") }}</text>
          <text class="link" @click="toggleAll">{{ allOpen ? t("course.collapseAll") : t("course.expandAll") }}</text>
        </view>
        <view v-for="s in shownSections" :key="s.id" class="module">
          <view class="m-head" @click="toggle(s.id)">
            <text class="m-caret" :class="{ open: isOpen(s.id) }">›</text>
            <text class="m-name">{{ s.name }}</text>
            <text class="m-meta">{{ unitMeta(s) }}</text>
            <text v-if="!s.visible" class="tag teacher">{{ t("course.teacherOnly") }}</text>
            <text v-if="isUnit(d, s)" class="m-over" @click.stop="openUnit(s)">{{ t("course.overview") }} ›</text>
          </view>
          <view v-if="isOpen(s.id)" class="m-body">
            <ModuleRow v-for="m in visibleModules(d, s)" :key="m.id" :m="m" :course-id="id" />
          </view>
        </view>
      </view>

      <!-- ================= Slides / Labs / Assignments: grouped by unit ================= -->
      <view v-else-if="tab === 'slides' || tab === 'labs' || tab === 'assignments'">
        <text class="h1">{{ t("menu." + tab) }}</text>
        <text v-if="tab === 'labs'" class="lead">{{ t("course.labsLead") }}</text>
        <view v-if="!grouped.length" class="muted">{{ t("course.nothing") }}</view>
        <view v-for="g in grouped" :key="g.section.id" class="group">
          <text class="g-name">{{ g.section.name }}</text>
          <view v-if="tab === 'labs'" class="lab-grid">
            <view v-for="m in g.items" :key="m.id" class="lab-card" @click="openModule(m.id)">
              <view class="lab-art"><text class="lab-glyph">⚗</text></view>
              <text class="lab-name">{{ m.name }}</text>
              <text class="lab-go">{{ t("course.runLab") }} ›</text>
            </view>
          </view>
          <view v-else class="list">
            <ModuleRow v-for="m in g.items" :key="m.id" :m="m" :course-id="id" />
          </view>
          <view v-if="tab === 'labs' && g.guides.length" class="list guides">
            <text class="g-sub">{{ t("course.labGuides") }}</text>
            <ModuleRow v-for="m in g.guides" :key="m.id" :m="m" :course-id="id" />
          </view>
        </view>
      </view>

      <!-- ================= Menus the new UI completes in later steps (2B framework) ================= -->
      <view v-else-if="HUB[tab]">
        <text class="h1">{{ t("menu." + tab) }}</text>

        <view v-if="tab === 'online'" class="empty">{{ t("hub.noOnline") }}</view>

        <view v-if="hubItems.length" class="hub-list">
          <text class="g-sub">{{ t("hub.existing") }}</text>
          <view class="list">
            <ModuleRow v-for="m in hubItems" :key="m.id" :m="m" :course-id="id" />
          </view>
        </view>
        <view v-else-if="HUB[tab].lists" class="empty">{{ t("hub.noneYet") }}</view>

        <view class="soon">
          <text class="soon-h">{{ t("hub.what") }}</text>
          <text class="soon-p">{{ t("hub." + tab) }}</text>
          <text class="soon-step">{{ tab === "quizzes" ? t("hub.quizStep") : tab === "online" ? t("hub.onlineStep") : t("hub.step", { n: HUB[tab].step }) }}</text>
          <view v-if="tab !== 'online'" class="soon-btns">
            <view class="primary" @click="openUrl(classicLink(d, tab))">{{ t("hub.classic") }} ↗</view>
            <view v-if="tab === 'people' && isTeacher(d)" class="ghost" @click="openUrl(classicLink(d, 'groups'))">{{ t("hub.classicGroups") }} ↗</view>
          </view>
        </view>
      </view>
    </template>

    <template v-if="d && tab === 'home'" #side>
      <view class="panel">
        <text class="ph">{{ t("course.atAGlance") }}</text>
        <view class="stat"><text>{{ t("kind.reading") }}</text><text class="num">{{ counts.reading }}</text></view>
        <view class="stat"><text>{{ t("kind.video") }}</text><text class="num">{{ counts.video }}</text></view>
        <view class="stat"><text>{{ t("kind.slides") }}</text><text class="num">{{ counts.slides }}</text></view>
        <view class="stat"><text>{{ t("kind.lab") }}</text><text class="num">{{ counts.lab }}</text></view>
        <view class="stat"><text>{{ t("kind.assign") }}</text><text class="num">{{ counts.assign }}</text></view>
      </view>
      <view v-if="isTeacher(d)" class="panel">
        <text class="ph">{{ t("course.teacherTools") }}</text>
        <view class="side-btn" @click="openClassic">{{ t("course.editClassic") }} ↗</view>
        <view class="side-btn" @click="create">✦ {{ t("create.button") }}</view>
      </view>
    </template>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import MathContent from "../../components/MathContent.vue";
import ModuleRow from "../../components/ModuleRow.vue";
import { absolute, ApiError, type Module, type Section, token } from "../../api";
import { errorText, locale, t } from "../../i18n";
import {
  type CourseData, findModule, isTeacher, isUnit, lastVisited, loadCourse, moduleKind, studentPreview,
  classicLink, isNewsForum, syllabusSection, units, visibleModules,
} from "../../store";

// Page query parameters (id, course, tab) must not fall through onto the layout component.
defineOptions({ inheritAttrs: false });

const id = ref(0);
const tab = ref("home");
const d = ref<CourseData | null>(null);
const loading = ref(true);
const error = ref("");
const open = ref<Record<number, boolean>>({});

async function load(force = false) {
  loading.value = true;
  error.value = "";
  try {
    d.value = await loadCourse(id.value, force);
    uni.setNavigationBarTitle({ title: d.value.info.name });
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

const unitList = computed(() => (d.value ? units(d.value) : []));
const syllabus = computed(() => (d.value ? syllabusSection(d.value) : null));
const shownSections = computed(() =>
  d.value ? d.value.sections.filter((s) => visibleModules(d.value!, s).length && (isTeacher(d.value) || s.visible !== false)) : []);

const counts = computed(() => {
  const c: Record<string, number> = { reading: 0, video: 0, slides: 0, lab: 0, assign: 0 };
  if (!d.value) return c;
  for (const s of d.value.sections) {
    for (const m of visibleModules(d.value, s)) {
      const k = moduleKind(m);
      if (k === "pdf") c.slides++;
      else if (k in c) c[k]++;
    }
  }
  return c;
});

function unitMeta(s: Section): string {
  const c: Record<string, number> = {};
  for (const m of visibleModules(d.value!, s)) {
    const k = moduleKind(m) === "pdf" ? "slides" : moduleKind(m);
    c[k] = (c[k] || 0) + 1;
  }
  const parts: string[] = [];
  for (const k of ["reading", "video", "slides", "lab", "assign"]) if (c[k]) parts.push(`${c[k]} ${t("kind." + k)}`);
  const other = Object.entries(c).filter(([k]) => !["reading", "video", "slides", "lab", "assign"].includes(k)).reduce((a, [, n]) => a + n, 0);
  if (other) parts.push(`${other} ${t("kind.file")}`);
  return parts.join(" · ");
}

const KINDS: Record<string, string[]> = { slides: ["slides", "pdf"], labs: ["lab"], assignments: ["assign"] };
const grouped = computed(() => {
  if (!d.value || !KINDS[tab.value]) return [];
  const want = KINDS[tab.value];
  return d.value.sections
    .map((section) => {
      const mods = visibleModules(d.value!, section);
      return {
        section,
        items: mods.filter((m) => want.includes(moduleKind(m))),
        guides: tab.value === "labs"
          ? mods.filter((m) => ["doc", "sheet", "pdf"].includes(moduleKind(m)) && /实验|lab|报告|report|量规|rubric/i.test(m.name || ""))
          : [],
      };
    })
    .filter((g) => g.items.length || g.guides.length);
});

// Menu pages whose new-UI version comes later in this round; step = step number in the plan.
const HUB: Record<string, { step: number; lists?: boolean }> = {
  announcements: { step: 4, lists: true }, discussions: { step: 4, lists: true }, quizzes: { step: 5, lists: true },
  online: { step: 4 }, grades: { step: 5 }, people: { step: 4 }, calendar: { step: 5 },
};
const hubItems = computed<Module[]>(() => {
  if (!d.value) return [];
  const mods = d.value.sections.flatMap((s) => visibleModules(d.value!, s));
  if (tab.value === "announcements") return mods.filter(isNewsForum);
  if (tab.value === "discussions") return mods.filter((m) => m.type === "forum" && !isNewsForum(m));
  if (tab.value === "quizzes") return mods.filter((m) => m.type === "quiz");
  return [];
});
function openUrl(url: string) {
  // #ifdef H5
  window.open(url, "_blank", "noopener");
  // #endif
  // #ifndef H5
  uni.setClipboardData({ data: url, success: () => uni.showToast({ title: t("activity.linkCopied"), icon: "none" }) });
  // #endif
}

const last = computed(() => {
  const cm = lastVisited(id.value);
  return cm && d.value ? findModule(d.value, cm) : null;
});
const resumeText = computed(() => {
  if (last.value) return last.value.module.name || "";
  const first = unitList.value[0];
  return first ? t("course.startAt", { name: first.name }) : "";
});

function isOpen(sid: number) { return open.value[sid] !== false; }
function toggle(sid: number) { open.value = { ...open.value, [sid]: !isOpen(sid) }; }
const allOpen = computed(() => shownSections.value.every((s) => isOpen(s.id)));
function toggleAll() {
  const v = !allOpen.value;
  open.value = Object.fromEntries(shownSections.value.map((s) => [s.id, v]));
}

function goTab(k: string) { uni.redirectTo({ url: `/pages/course/course?id=${id.value}&tab=${k}` }); }
function openUnit(s: Section) { uni.navigateTo({ url: `/pages/unit/unit?course=${id.value}&section=${s.id}` }); }
function openModule(cmid: number) { uni.navigateTo({ url: `/pages/activity/activity?id=${cmid}&course=${id.value}` }); }
function resume() {
  if (last.value) return openModule(last.value.module.id);
  if (unitList.value[0]) openUnit(unitList.value[0]);
}
function openClassic() {
  // #ifdef H5
  if (d.value) window.open(d.value.info.classic_url, "_blank", "noopener");
  // #endif
}
const create = () => uni.navigateTo({ url: "/pages/studio/studio" });

onLoad((q: any) => {
  id.value = Number(q?.id || 0);
  tab.value = String(q?.tab || "home");
});
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  load();
});
watch(locale, () => load(true));
watch(studentPreview, () => { open.value = {}; });
</script>

<style scoped>
.muted { color: var(--wq-muted); }
.empty { background: #fff; border: 1px dashed var(--wq-line); border-radius: 6px; padding: 18px 20px; color: var(--wq-muted); margin-bottom: 16px; }
.hub-list { margin-bottom: 18px; }
.soon { background: #fff; border: 1px solid var(--wq-line); border-left: 4px solid var(--wq-accent); border-radius: 6px; padding: 18px 22px; }
.soon-h { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 6px; }
.soon-p { display: block; color: var(--wq-text); line-height: 1.75; }
.soon-step { display: block; font-size: 13px; color: var(--wq-muted); margin-top: 10px; }
.soon-btns { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.soon .primary { display: inline-block; margin-top: 14px; background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 9px 18px; border-radius: 8px; cursor: pointer; }
.soon .ghost { display: inline-block; margin-top: 14px; border: 1px solid var(--wq-line); color: var(--wq-ink); padding: 8px 16px; border-radius: 8px; cursor: pointer; }
.state { display: flex; align-items: center; gap: 12px; }
.error { color: var(--wq-danger); }
.btn { padding: 6px 14px; border-radius: 8px; background: var(--wq-ink); color: #fff; font-size: 14px; cursor: pointer; }
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); margin-bottom: 16px; }
.h1-row { display: flex; justify-content: space-between; align-items: baseline; }
.h2 { display: block; font-size: 19px; font-weight: 700; color: var(--wq-ink); margin: 32px 0 12px; }
.lead { display: block; color: var(--wq-text); margin: -6px 0 18px; }
.link { color: var(--wq-link); cursor: pointer; font-size: 14px; }
.tag { font-size: 12px; padding: 1px 8px; border-radius: 999px; white-space: nowrap; }
.tag.teacher { background: #fff3d6; color: #7a5a00; }
.chev { color: var(--wq-muted); font-size: 18px; }

/* home */
.banner { background: #0d1a20; color: #fff; display: flex; align-items: stretch; min-height: 210px; border-radius: 4px; overflow: hidden;
  background-image: linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px);
  background-size: 28px 28px; }
.b-text { flex: 1.2; padding: 28px 30px 56px; display: flex; flex-direction: column; justify-content: center; gap: 8px; min-width: 0; }
.b-code { font-family: "IBM Plex Mono", Menlo, monospace; color: var(--wq-accent); letter-spacing: 1px; font-size: 14px; }
.b-title { font-family: "Noto Serif SC", "Songti SC", serif; font-weight: 900; font-size: 38px; line-height: 1.15; }
.b-meta { color: #a9bcc2; font-size: 14px; }
.b-img { flex: 0.8; height: auto; min-height: 210px; }
.b-art { flex: 0.8; position: relative; overflow: hidden; }
.b-arc { position: absolute; border: 2px dashed rgba(242,183,5,.8); border-radius: 50%; }
.a1 { width: 260px; height: 260px; left: 10%; top: 40px; border-bottom-color: transparent; border-right-color: transparent; transform: rotate(35deg); }
.a2 { width: 380px; height: 380px; left: -6%; top: 60px; border-color: rgba(92,184,214,.45); border-bottom-color: transparent; border-left-color: transparent; border-style: solid; transform: rotate(-20deg); }
.b-dot { position: absolute; width: 14px; height: 14px; border-radius: 50%; background: var(--wq-accent); left: 42%; top: 64px; box-shadow: 0 0 18px rgba(242,183,5,.7); }
.cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin: -36px 20px 0; position: relative; }
.card { background: #fff; border: 1px solid var(--wq-line); box-shadow: 0 6px 16px rgba(13,26,32,.12); padding: 20px 16px 16px; display: flex; flex-direction: column; align-items: center; gap: 6px; text-align: center; cursor: pointer; }
.card:hover .c-btn { border-color: var(--wq-link); color: var(--wq-link); }
.c-icon { font-size: 26px; color: var(--wq-ink); }
.c-title { font-size: 19px; font-weight: 700; color: var(--wq-ink); }
.c-text { font-size: 13px; color: var(--wq-muted); min-height: 38px; line-height: 1.5; }
.c-btn { font-size: 13px; border: 1px solid var(--wq-line); padding: 5px 14px; letter-spacing: 1px; margin-top: 4px; }
.unit-list { background: #fff; border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; }
.unit { display: flex; align-items: center; gap: 16px; padding: 14px 18px; border-top: 1px solid var(--wq-line); cursor: pointer; }
.unit:first-child { border-top: 0; }
.unit:hover { background: #f1f6f8; }
.u-no { font-family: "IBM Plex Mono", Menlo, monospace; color: #7a5a00; font-size: 15px; }
.u-body { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.u-name { color: var(--wq-link); font-size: 17px; }
.u-meta { color: var(--wq-muted); font-size: 13px; }
.about { margin-top: 8px; }

/* modules */
.module { border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; margin-bottom: 14px; background: #fff; }
.m-head { display: flex; align-items: center; gap: 10px; padding: 12px 14px; background: #f3f5f5; cursor: pointer; flex-wrap: wrap; }
.m-caret { display: inline-block; transition: transform .15s; font-size: 18px; color: var(--wq-muted); width: 12px; }
.m-caret.open { transform: rotate(90deg); }
.m-name { font-weight: 700; color: var(--wq-ink); }
.m-meta { font-size: 13px; color: var(--wq-muted); flex: 1; }
.m-over { font-size: 13px; color: var(--wq-link); }
.m-body :deep(.row) { border-top: 1px solid var(--wq-line); padding-left: 38px; }

/* grouped lists */
.group { margin-bottom: 26px; }
.g-name { display: block; font-weight: 700; color: var(--wq-ink); margin-bottom: 8px; padding-bottom: 6px; border-bottom: 3px solid #5cb8d6; }
.g-sub { display: block; font-size: 13px; color: var(--wq-muted); padding: 10px 14px 4px; }
.list { background: #fff; border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; }
.list :deep(.row) + :deep(.row) { border-top: 1px solid var(--wq-line); }
.guides { margin-top: 12px; }
.sec-summary { display: block; padding: 12px 14px; color: var(--wq-text); border-bottom: 1px solid var(--wq-line); }
.panel-block { background: #fff; border: 1px solid var(--wq-line); border-radius: 6px; padding: 18px 20px; margin-bottom: 16px; }
.lab-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
.lab-card { background: #fff; border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; cursor: pointer; display: flex; flex-direction: column; }
.lab-card:hover { box-shadow: 0 6px 16px rgba(13,26,32,.12); }
.lab-art { height: 96px; background: #0d1a20; display: flex; align-items: center; justify-content: center;
  background-image: linear-gradient(rgba(92,184,214,.12) 1px, transparent 1px), linear-gradient(90deg, rgba(92,184,214,.12) 1px, transparent 1px); background-size: 16px 16px; }
.lab-glyph { font-size: 34px; color: #5cb8d6; }
.lab-name { padding: 12px 14px 2px; color: var(--wq-ink); font-weight: 600; }
.lab-go { padding: 0 14px 12px; color: var(--wq-link); font-size: 13px; }

/* side */
.panel { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 14px 16px; }
.ph { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid var(--wq-line); }
.stat { display: flex; justify-content: space-between; padding: 4px 0; font-size: 14px; color: var(--wq-text); }
.num { font-family: "IBM Plex Mono", Menlo, monospace; color: var(--wq-ink); }
.side-btn { padding: 9px 12px; border: 1px solid var(--wq-line); border-radius: 6px; margin-top: 8px; cursor: pointer; font-size: 14px; color: var(--wq-ink); background: #f7f9f8; }
.side-btn:hover { border-color: var(--wq-link); }

@media (max-width: 860px) {
  .banner { flex-direction: column; min-height: 0; }
  .b-text { padding: 22px 20px 48px; }
  .b-title { font-size: 28px; }
  .b-img, .b-art { display: none; }
  .cards { grid-template-columns: 1fr; margin: -28px 12px 0; gap: 8px; }
  .card { flex-direction: row; text-align: left; padding: 12px 14px; gap: 12px; }
  .c-icon { font-size: 20px; }
  .c-title { font-size: 16px; white-space: nowrap; }
  .c-text { flex: 1; min-height: 0; font-size: 12px; }
  .c-btn { display: none; }
}
</style>
