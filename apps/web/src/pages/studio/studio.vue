<template>
  <AppShell nav="create" :title="t('studio.title')">
    <view class="wrap">
      <view class="head">
        <view>
          <text class="h1">{{ t("studio.title") }}</text>
          <text class="lead">{{ t("studio.lead") }}</text>
        </view>
        <view class="primary" :class="{ disabled: busy }" @click="create">＋ {{ t("studio.new") }}</view>
      </view>

      <view class="team">
        <view v-for="r in ROLES" :key="r" class="member">
          <text class="m-name">{{ t("studio.role." + r) }}</text>
          <text class="m-job">{{ t("studio.roleJob." + r) }}</text>
        </view>
      </view>

      <view v-if="error" class="alert">{{ errorText(error) }}</view>
      <view v-if="loading" class="muted">{{ t("common.loading") }}</view>
      <view v-else-if="!list.length" class="empty">{{ t("studio.none") }}</view>
      <view v-else class="list">
        <view v-for="p in list" :key="p.id" class="row" @click="open(p.id)">
          <view class="r-main">
            <text class="r-title">{{ p.title || t("studio.untitled") }}</text>
            <text class="r-meta">{{ t("studio.stage." + p.stage) }} · {{ t("studio.lessonsDone", { done: p.published, total: p.lessons }) }} · {{ formatDate(p.updated) }}</text>
          </view>
          <text v-if="p.busy" class="chip busy">{{ t("studio.working") }}</text>
          <text v-if="p.awaiting" class="chip warn">{{ t("studio.awaitingN", { n: p.awaiting }) }}</text>
          <text v-if="p.open_questions" class="chip warn">{{ t("studio.questionsN", { n: p.open_questions }) }}</text>
          <text class="chev">›</text>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { api, ApiError, type StudioSummary, token, user } from "../../api";
import { errorText, formatDate, t } from "../../i18n";

// Page query parameters must not fall through onto the layout component.
defineOptions({ inheritAttrs: false });

const ROLES = ["lead", "librarian", "designer", "author", "assessor", "reviewer"];
const list = ref<StudioSummary[]>([]);
const loading = ref(true);
const busy = ref(false);
const error = ref("");

async function load() {
  error.value = "";
  try {
    list.value = await api.studioProjects();
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

async function create() {
  if (busy.value) return;
  busy.value = true;
  try {
    const p = await api.studioCreate("");
    open(p.id);
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    busy.value = false;
  }
}

const open = (id: string) => uni.navigateTo({ url: `/pages/studio/project?id=${id}` });

onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t("studio.title") });
  if (user.value && user.value.can_create_courses === false) error.value = "forbidden";
  load();
});
</script>

<style scoped>
.wrap { max-width: 980px; }
.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); }
.lead { display: block; color: var(--wq-muted); margin-top: 6px; line-height: 1.7; max-width: 640px; }
.primary { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 10px 20px; border-radius: 8px; cursor: pointer; white-space: nowrap; }
.disabled { opacity: .5; pointer-events: none; }
.team { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; margin: 20px 0; }
.member { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 10px 12px; }
.m-name { display: block; font-weight: 600; color: var(--wq-ink); font-size: 14px; }
.m-job { display: block; font-size: 12px; color: var(--wq-muted); margin-top: 3px; line-height: 1.5; }
.alert { background: #fdecea; color: var(--wq-danger); padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; }
.muted, .empty { color: var(--wq-muted); }
.empty { background: #fff; border: 1px dashed var(--wq-line); border-radius: 8px; padding: 28px; text-align: center; }
.list { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; overflow: hidden; }
.row { display: flex; align-items: center; gap: 10px; padding: 14px 16px; cursor: pointer; border-top: 1px solid var(--wq-line); }
.row:first-child { border-top: 0; }
.row:hover { background: #f7f9f8; }
.r-main { flex: 1; min-width: 0; }
.r-title { display: block; font-weight: 600; color: var(--wq-ink); }
.r-meta { display: block; font-size: 13px; color: var(--wq-muted); margin-top: 2px; }
.chip { font-size: 12px; padding: 2px 8px; border-radius: 999px; white-space: nowrap; }
.chip.busy { background: #e7f1f5; color: var(--wq-link); }
.chip.warn { background: #fff3d6; color: #7a5a00; }
.chev { color: var(--wq-muted); }
</style>
