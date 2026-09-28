<template>
  <AppShell :nav="all ? 'courses' : 'dashboard'" :title="all ? t('shell.courses') : t('shell.dashboard')">
    <view class="head">
      <view>
        <text class="hello">{{ all ? t("shell.courses") : t("dash.hello", { name: firstName }) }}</text>
        <text class="date">{{ today }}</text>
      </view>
      <view v-if="user && user.can_create_courses" class="create" @click="create">✦ {{ t("create.button") }}</view>
    </view>

    <view v-if="loading" class="muted">{{ t("common.loading") }}</view>
    <view v-else-if="error" class="state">
      <text class="error">{{ errorText(error) }}</text>
      <view class="btn" @click="load">{{ t("common.retry") }}</view>
    </view>
    <view v-else-if="!courses.length" class="empty">
      <text class="muted">{{ t("courses.empty") }}</text>
    </view>
    <view v-else class="grid">
      <view v-for="c in courses" :key="c.id" class="card" @click="open(c)">
        <view class="cover" :style="{ background: tint(c.id) }">
          <image v-if="c.image" class="img" :src="absolute(c.image)" mode="aspectFill" />
          <text v-else class="code">{{ c.shortname }}</text>
        </view>
        <view class="body">
          <text class="name">{{ c.name }}</text>
          <text class="summary">{{ c.summary }}</text>
          <view v-if="c.progress !== null && c.progress !== undefined" class="progress">
            <view class="bar"><view class="fill" :style="{ width: Math.round(c.progress) + '%' }" /></view>
            <text class="pct">{{ t("courses.progress", { n: Math.round(c.progress) }) }}</text>
          </view>
        </view>
      </view>
    </view>

    <template #side>
      <view class="panel">
        <text class="ph">{{ t("dash.todo") }}</text>
        <text class="muted small">{{ t("dash.todoEmpty") }}</text>
      </view>
      <view v-if="user && user.can_create_courses" class="panel ai">
        <text class="ph">{{ t("dash.aiTitle") }}</text>
        <text class="small">{{ t("dash.aiBody") }}</text>
        <view class="create full" @click="create">✦ {{ t("create.button") }}</view>
      </view>
    </template>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { absolute, api, ApiError, type Course, token, user } from "../../api";
import { errorText, locale, t } from "../../i18n";

// Page query parameters (id, course, tab) must not fall through onto the layout component.
defineOptions({ inheritAttrs: false });

const courses = ref<Course[]>([]);
const loading = ref(true);
const error = ref("");
const all = ref(false);

const TINTS = ["#1F4E5F", "#2E5E4B", "#5A4A1E", "#43396B", "#6B2F2F"];
const tint = (id: number) => TINTS[id % TINTS.length];
const firstName = computed(() => (user.value?.fullname || "").split(/\s+/)[0] || "");
const today = computed(() =>
  new Date().toLocaleDateString(locale.value === "en" ? "en-US" : "zh-CN", { weekday: "long", month: "long", day: "numeric" }));

async function load() {
  loading.value = true;
  error.value = "";
  try {
    courses.value = await api.courses();
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

const create = () => uni.navigateTo({ url: "/pages/create/create" });
const open = (c: Course) => uni.navigateTo({ url: `/pages/course/course?id=${c.id}` });

onLoad((q: any) => { all.value = q?.view === "all"; });
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t(all.value ? "shell.courses" : "shell.dashboard") });
  load();
  api.me().catch(() => {}); // refresh permissions (e.g. the AI course button)
});
watch(locale, () => { load(); api.me().catch(() => {}); });
</script>

<style scoped>
.head { display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; margin-bottom: 22px; }
.hello { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); }
.date { display: block; font-size: 14px; color: var(--wq-muted); margin-top: 2px; }
.create { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 9px 18px; border-radius: 8px; cursor: pointer; font-size: 15px; white-space: nowrap; }
.create.full { text-align: center; margin-top: 10px; }
.muted { color: var(--wq-muted); font-size: 15px; }
.small { font-size: 14px; line-height: 1.6; display: block; }
.state { display: flex; align-items: center; gap: 12px; }
.error { color: var(--wq-danger); }
.btn { padding: 6px 14px; border-radius: 8px; background: var(--wq-ink); color: #fff; font-size: 14px; cursor: pointer; }
.empty { background: #fff; border: 1px dashed var(--wq-line); border-radius: 10px; padding: 32px; text-align: center; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 18px; }
.card { background: #fff; border: 1px solid var(--wq-line); border-radius: 6px; overflow: hidden; cursor: pointer; display: flex; flex-direction: column; box-shadow: 0 1px 3px rgba(20,33,43,.05); transition: box-shadow .15s; }
.card:hover { box-shadow: 0 8px 22px rgba(20,33,43,.12); }
.cover { height: 130px; position: relative; display: flex; align-items: flex-end; padding: 12px 14px; box-sizing: border-box;
  background-image: repeating-linear-gradient(115deg, transparent 0 34px, rgba(255,255,255,.06) 34px 35px); }
.img { position: absolute; inset: 0; width: 100%; height: 100%; }
.code { font-family: "IBM Plex Mono", Menlo, monospace; color: rgba(255,255,255,.85); font-size: 13px; letter-spacing: 1px; }
.body { padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 6px; }
.name { font-size: 17px; font-weight: 600; color: var(--wq-link); line-height: 1.35; }
.summary { font-size: 14px; color: var(--wq-text); line-height: 1.55; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.progress { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
.bar { flex: 1; height: 6px; background: #e8ecea; border-radius: 3px; overflow: hidden; }
.fill { height: 100%; background: var(--wq-accent); }
.pct { font-size: 12px; color: var(--wq-muted); }
.panel { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 14px 16px; }
.panel.ai { background: #fffaf0; border-color: #f1dfae; }
.ph { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 6px; padding-bottom: 8px; border-bottom: 1px solid var(--wq-line); }
</style>
