<template>
  <view class="app" :class="{ 'has-course': !!course }">
    <!-- Global navigation: a left rail on wide screens, a bottom bar on phones and in the mini program -->
    <view class="gnav">
      <view class="logo" @click="go('dashboard')">
        <text class="logo-mark">问渠</text>
        <text class="logo-sub">WenQuest</text>
      </view>
      <view class="gitem" :class="{ on: nav === 'account' || accountOpen }" @click="accountOpen = !accountOpen">
        <view class="avatar">{{ initial }}</view>
        <text class="glabel">{{ t("shell.account") }}</text>
      </view>
      <view class="gitem" :class="{ on: nav === 'dashboard' }" @click="go('dashboard')">
        <text class="gicon">⌂</text>
        <text class="glabel">{{ t("shell.dashboard") }}</text>
      </view>
      <view class="gitem" :class="{ on: nav === 'courses' }" @click="go('courses')">
        <text class="gicon">▤</text>
        <text class="glabel">{{ t("shell.courses") }}</text>
      </view>
      <view class="gitem wide-only" :class="{ on: nav === 'calendar' }" @click="go('calendar')">
        <text class="gicon">▦</text>
        <text class="glabel">{{ t("shell.calendar") }}</text>
      </view>
      <view class="gitem wide-only" :class="{ on: nav === 'inbox' }" @click="go('inbox')">
        <text class="gicon">✉</text>
        <text class="glabel">{{ t("shell.inbox") }}</text>
      </view>
      <view class="gitem" :class="{ on: nav === 'catalog' }" @click="go('catalog')">
        <text class="gicon">☷</text>
        <text class="glabel">{{ t("catalog.nav") }}</text>
      </view>
      <view v-if="user && user.can_create_courses" class="gitem" :class="{ on: nav === 'create' }" @click="go('create')">
        <text class="gicon">✦</text>
        <text class="glabel">{{ t("create.button") }}</text>
      </view>
      <view v-if="admin && admin.admin" class="gitem" :class="{ on: nav === 'admin' }" @click="go('admin')">
        <text class="gicon">⚑</text>
        <text class="glabel">{{ t("admin.nav") }}</text>
        <text v-if="(admin.applications || 0) + (admin.requests || 0) > 0" class="badge">{{ (admin.applications || 0) + (admin.requests || 0) }}</text>
      </view>
      <view class="gspacer" />
      <view class="gitem wide-only" :class="{ on: nav === 'help' }" @click="go('help')">
        <text class="gicon">?</text>
        <text class="glabel">{{ t("shell.help") }}</text>
      </view>
      <view class="gitem lang wide-only" @click="toggleLocale">
        <text class="gicon small">{{ t("lang.switch") }}</text>
        <text class="glabel">{{ t("shell.language") }}</text>
      </view>
    </view>

    <!-- Account panel -->
    <view v-if="accountOpen" class="scrim" @click="accountOpen = false" />
    <view v-if="accountOpen" class="account">
      <view class="acc-head">
        <view class="avatar big">{{ initial }}</view>
        <view>
          <text class="acc-name">{{ user ? user.fullname : "" }}</text>
          <text class="acc-user">{{ user ? user.username : "" }}</text>
        </view>
      </view>
      <view class="acc-row narrow-only" @click="go('calendar')">{{ t("shell.calendar") }}</view>
      <view class="acc-row narrow-only" @click="go('inbox')">{{ t("shell.inbox") }}</view>
      <view class="acc-row narrow-only" @click="go('help')">{{ t("shell.help") }}</view>
      <view v-if="user && !user.can_create_courses" class="acc-row" @click="go('apply')">{{ t("apply.menu") }}</view>
      <view class="acc-row" @click="toggleLocale">{{ t("shell.language") }} · {{ t("lang.switch") }}</view>
      <view class="acc-row" @click="logout">{{ t("nav.logout") }}</view>
    </view>

    <view class="main">
      <view class="topbar">
        <view class="crumbs">
          <text v-if="course" class="crumb link" @click="openCourse('home')">{{ course.info.name }}</text>
          <text v-if="course && crumb" class="sep">›</text>
          <text class="crumb here">{{ crumb || (course ? "" : title) }}</text>
        </view>
        <view class="top-right">
          <view v-if="course && course.info.role === 'teacher'" class="preview" @click="studentPreview = !studentPreview">
            <text class="pv-dot" :class="{ on: studentPreview }" />
            <text>{{ t("shell.studentView") }}</text>
          </view>
          <slot name="actions" />
        </view>
      </view>

      <view class="body" :class="{ 'no-side': !$slots.side }">
        <!-- Course menu -->
        <view v-if="course" class="cnav">
          <text class="term">{{ course.info.shortname }}</text>
          <view v-for="item in menu" :key="item.key" class="citem" :class="{ on: item.key === tab }" @click="openCourse(item.key)">
            {{ t("menu." + item.key) }}
          </view>
        </view>
        <view class="content">
          <view v-if="studentPreview && course && course.info.role === 'teacher'" class="pv-banner">
            {{ t("shell.previewing") }}
            <text class="pv-exit" @click="studentPreview = false">{{ t("shell.exitPreview") }}</text>
          </view>
          <slot />
        </view>
        <view v-if="$slots.side" class="side"><slot name="side" /></view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { admin, accountApi, loadAdmin } from "../accountApi";
import { api, user } from "../api";
import { t, toggleLocale } from "../i18n";
import { type CourseData, courseMenu, studentPreview } from "../store";

const props = defineProps<{
  nav?: string;
  title?: string;
  crumb?: string;
  course?: CourseData | null;
  tab?: string;
}>();

const accountOpen = ref(false);
const initial = computed(() => (user.value?.fullname || "?").trim().slice(0, 1).toUpperCase());
const menu = computed(() => (props.course ? courseMenu(props.course) : []));

function go(where: string) {
  accountOpen.value = false;
  if (where === "create") return uni.reLaunch({ url: "/pages/studio/studio" });
  if (["catalog", "admin", "apply"].includes(where)) return uni.reLaunch({ url: `/pages/${where}/${where}` });
  if (["calendar", "inbox", "help"].includes(where)) return uni.reLaunch({ url: `/pages/hub/hub?view=${where}` });
  uni.reLaunch({ url: where === "courses" ? "/pages/courses/courses?view=all" : "/pages/courses/courses" });
}

function openCourse(key: string) {
  if (!props.course) return;
  const url = `/pages/course/course?id=${props.course.info.id}&tab=${key}`;
  const pages = getCurrentPages();
  const here: any = pages[pages.length - 1];
  if (here && here.route === "pages/course/course") uni.redirectTo({ url });
  else uni.navigateTo({ url });
}

async function logout() {
  // Sign out everywhere: the site-wide cookie would otherwise sign this browser straight back in.
  await accountApi.logoutEverywhere();
  api.logout();
  admin.value = null;
  uni.reLaunch({ url: "/pages/login/login" });
}
onMounted(() => loadAdmin());
</script>

<style scoped>
.app { min-height: 100vh; background: var(--wq-bg); display: flex; }

/* ---- global nav ---- */
.gnav {
  width: 84px; flex-shrink: 0; background: var(--wq-ink); color: #c9d4d8; display: flex; flex-direction: column;
  position: sticky; top: 0; height: 100vh; z-index: 20;
  overflow-y: auto; overflow-x: hidden; scrollbar-width: none;   /* never cut off the bottom (help, language) */
}
.gnav::-webkit-scrollbar { display: none; }
.logo { display: flex; flex-direction: column; align-items: center; padding: 16px 4px 14px; border-bottom: 1px solid rgba(255,255,255,.08); cursor: pointer; }
.logo-mark { font-family: "Noto Serif SC", "Songti SC", serif; font-weight: 900; font-size: 20px; color: #fff; letter-spacing: 2px; }
.logo-sub { font-family: "IBM Plex Mono", Menlo, monospace; font-size: 9px; letter-spacing: 1.5px; color: var(--wq-accent); margin-top: 3px; }
.gitem { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 11px 4px; cursor: pointer; position: relative; }
.gitem:hover { background: rgba(255,255,255,.06); color: #fff; }
.gitem.on { background: #fff; color: var(--wq-ink); }
.gitem.on::before { content: ""; position: absolute; left: 0; top: 8px; bottom: 8px; width: 3px; background: var(--wq-accent); }
.gicon { font-size: 20px; line-height: 24px; }
.gicon.small { font-size: 13px; font-weight: 600; border: 1px solid rgba(255,255,255,.3); border-radius: 999px; padding: 0 8px; line-height: 22px; }
.gitem.on .gicon.small { border-color: var(--wq-line); }
.glabel { font-size: 12px; }
.badge { position: absolute; top: 6px; right: 18px; background: var(--wq-danger); color: #fff; font-size: 10px; border-radius: 999px; padding: 0 5px; line-height: 15px; }
.gspacer { flex: 1; }
.avatar { width: 28px; height: 28px; border-radius: 50%; background: var(--wq-accent); color: var(--wq-ink); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
.avatar.big { width: 44px; height: 44px; font-size: 20px; }

/* account panel */
.scrim { position: fixed; inset: 0; z-index: 29; }
.account {
  position: fixed; left: 92px; top: 60px; z-index: 30; width: 260px; background: #fff; border: 1px solid var(--wq-line);
  border-radius: 10px; box-shadow: 0 12px 32px rgba(20,33,43,.16); padding: 14px; display: flex; flex-direction: column; gap: 4px;
}
.acc-head { display: flex; align-items: center; gap: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--wq-line); margin-bottom: 4px; }
.acc-name { display: block; font-weight: 600; color: var(--wq-ink); }
.acc-user { display: block; font-size: 12px; color: var(--wq-muted); }
.acc-row { padding: 10px 8px; border-radius: 6px; cursor: pointer; color: var(--wq-ink); font-size: 14px; }
.acc-row:hover { background: var(--wq-bg); }
.narrow-only { display: none; }

/* ---- main ---- */
.main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.topbar {
  display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;
  padding: 14px 24px; background: #fff; border-bottom: 1px solid var(--wq-line); min-height: 56px; box-sizing: border-box;
}
.crumbs { display: flex; align-items: center; gap: 8px; min-width: 0; font-size: 16px; }
.crumb { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 42vw; }
.crumb.link { color: var(--wq-link); cursor: pointer; }
.crumb.here { color: var(--wq-ink); font-weight: 500; }
.sep { color: var(--wq-muted); }
.top-right { display: flex; align-items: center; gap: 10px; }
.preview { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--wq-text); border: 1px solid var(--wq-line); border-radius: 999px; padding: 5px 12px; cursor: pointer; }
.pv-dot { width: 26px; height: 14px; border-radius: 7px; background: #cfd8d6; position: relative; }
.pv-dot::after { content: ""; position: absolute; top: 2px; left: 2px; width: 10px; height: 10px; border-radius: 50%; background: #fff; transition: left .15s; }
.pv-dot.on { background: var(--wq-link); }
.pv-dot.on::after { left: 14px; }

.body { display: grid; grid-template-columns: 176px minmax(0, 1fr) 260px; gap: 28px; padding: 20px 24px 64px; align-items: start; }
.body.no-side { grid-template-columns: 176px minmax(0, 1fr); }
.app:not(.has-course) .body { grid-template-columns: minmax(0, 1fr) 280px; }
.app:not(.has-course) .body.no-side { grid-template-columns: minmax(0, 1fr); }
.cnav { display: flex; flex-direction: column; gap: 2px; position: sticky; top: 16px; }
.term { font-size: 12px; color: var(--wq-muted); font-family: "IBM Plex Mono", Menlo, monospace; padding: 2px 10px 10px; }
.citem { padding: 6px 10px; border-left: 3px solid transparent; color: var(--wq-link); font-size: 15px; cursor: pointer; }
.citem:hover { text-decoration: underline; }
.citem.on { border-left-color: var(--wq-ink); color: var(--wq-ink); font-weight: 600; text-decoration: none; }
.content { min-width: 0; }
.side { position: sticky; top: 16px; display: flex; flex-direction: column; gap: 12px; }
.pv-banner { background: #e7f1f5; color: var(--wq-link); border-radius: 8px; padding: 8px 14px; font-size: 14px; margin-bottom: 14px; display: flex; justify-content: space-between; gap: 12px; }
.pv-exit { font-weight: 600; cursor: pointer; }

/* shorter screens: a more compact rail so every item, down to 语言, stays in view */
@media (min-width: 861px) and (max-height: 940px) {
  .logo { padding: 10px 4px 8px; }
  .gitem { padding: 7px 4px; gap: 2px; }
  .gicon { font-size: 18px; line-height: 21px; }
  .avatar { width: 24px; height: 24px; font-size: 12px; }
  .glabel { font-size: 11px; }
}
@media (min-width: 861px) and (max-height: 720px) {
  .gitem { padding: 5px 4px; }
  .logo-sub { display: none; }
}
@media (max-width: 1180px) {
  .body { grid-template-columns: 160px minmax(0, 1fr); }
  .side { grid-column: 2; position: static; }
  .app:not(.has-course) .body { grid-template-columns: minmax(0, 1fr); }
  .app:not(.has-course) .side { grid-column: 1; }
}
@media (max-width: 860px) {
  .app { flex-direction: column; padding-bottom: 60px; }
  .gnav { position: fixed; left: 0; right: 0; bottom: 0; top: auto; width: auto; height: 60px; flex-direction: row; justify-content: space-around; padding-bottom: env(safe-area-inset-bottom); }
  .logo, .gspacer, .wide-only { display: none; }
  .narrow-only { display: block; }
  .gitem { flex: 1; padding: 6px 2px; }
  .gitem.on { background: transparent; color: #fff; }
  .gitem.on::before { left: 20%; right: 20%; top: 0; bottom: auto; width: auto; height: 3px; }
  .gitem.on .gicon.small { border-color: rgba(255,255,255,.3); }
  .account { left: 12px; right: 12px; top: auto; bottom: 70px; width: auto; }
  .topbar { padding: 10px 16px; }
  .crumb { max-width: 60vw; }
  .body, .body.no-side, .app:not(.has-course) .body { grid-template-columns: minmax(0, 1fr); padding: 12px 16px 32px; gap: 14px; }
  .cnav { position: static; flex-direction: row; overflow-x: auto; gap: 4px; border-bottom: 1px solid var(--wq-line); padding-bottom: 6px; }
  .term { display: none; }
  .citem { border-left: 0; border-bottom: 2px solid transparent; white-space: nowrap; }
  .citem.on { border-bottom-color: var(--wq-ink); }
  .side { grid-column: 1; }
}
</style>
