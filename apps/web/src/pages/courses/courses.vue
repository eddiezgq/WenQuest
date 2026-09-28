<template>
  <view class="page">
    <TopBar />
    <view class="wrap">
      <view class="head">
        <text class="h1">{{ t("nav.courses") }}</text>
        <view v-if="user && user.can_create_courses" class="create" @click="create">✨ {{ t("create.button") }}</view>
      </view>
      <view v-if="loading" class="muted">{{ t("common.loading") }}</view>
      <view v-else-if="error" class="state">
        <text class="error">{{ errorText(error) }}</text>
        <view class="btn" @click="load">{{ t("common.retry") }}</view>
      </view>
      <view v-else-if="!courses.length" class="muted">{{ t("courses.empty") }}</view>
      <view v-else class="grid">
        <view v-for="c in courses" :key="c.id" class="course" @click="open(c)">
          <image v-if="c.image" class="cover" :src="absolute(c.image)" mode="aspectFill" />
          <view v-else class="cover placeholder" :style="{ background: tint(c.id) }">
            <text class="initial">{{ c.name.slice(0, 1) }}</text>
          </view>
          <view class="body">
            <text class="code">{{ c.shortname }}</text>
            <text class="name">{{ c.name }}</text>
            <text class="summary">{{ c.summary }}</text>
            <view v-if="c.progress !== null && c.progress !== undefined" class="progress">
              <view class="bar"><view class="fill" :style="{ width: Math.round(c.progress) + '%' }" /></view>
              <text class="pct">{{ t("courses.progress", { n: Math.round(c.progress) }) }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { onShow } from "@dcloudio/uni-app";
import TopBar from "../../components/TopBar.vue";
import { absolute, api, ApiError, type Course, token, user } from "../../api";
import { errorText, locale, t } from "../../i18n";

const courses = ref<Course[]>([]);
const loading = ref(true);
const error = ref("");

const TINTS = ["#1F6F8B", "#2E7D5B", "#7A5A00", "#5B4B8A", "#8A3B3B"];
const tint = (id: number) => TINTS[id % TINTS.length];

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

function create() {
  uni.navigateTo({ url: "/pages/create/create" });
}

function open(c: Course) {
  uni.navigateTo({ url: `/pages/course/course?id=${c.id}` });
}

onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t("nav.courses") });
  load();
  api.me().catch(() => {}); // refresh permissions (e.g. the AI course button)
});
watch(locale, () => {
  uni.setNavigationBarTitle({ title: t("nav.courses") });
  load();
  api.me().catch(() => {}); // refresh permissions (e.g. the AI course button)
});
</script>

<style scoped>
.page { min-height: 100vh; background: var(--wq-bg); }
.wrap { max-width: 1080px; margin: 0 auto; padding: 24px 16px 48px; }
.head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 20px; }
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); }
.create { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 9px 18px; border-radius: 8px; cursor: pointer; font-size: 15px; }
.muted { color: var(--wq-muted); font-size: 15px; }
.state { display: flex; align-items: center; gap: 12px; }
.error { color: var(--wq-danger); }
.btn { padding: 6px 14px; border-radius: 8px; background: var(--wq-ink); color: #fff; font-size: 14px; cursor: pointer; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.course {
  background: #fff; border-radius: 12px; overflow: hidden; border: 1px solid var(--wq-line); cursor: pointer;
  display: flex; flex-direction: column; transition: transform .15s ease, box-shadow .15s ease;
}
.course:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(20,33,43,.08); }
.cover { width: 100%; height: 128px; }
.placeholder { display: flex; align-items: center; justify-content: center; }
.initial { font-size: 44px; font-weight: 700; color: rgba(255,255,255,.9); }
.body { padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 6px; }
.code { font-size: 12px; letter-spacing: 1px; color: var(--wq-muted); font-family: "IBM Plex Mono", Menlo, monospace; }
.name { font-size: 18px; font-weight: 600; color: var(--wq-ink); line-height: 1.35; }
.summary {
  font-size: 14px; color: var(--wq-text); line-height: 1.55; display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}
.progress { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
.bar { flex: 1; height: 6px; background: #e8ecea; border-radius: 3px; overflow: hidden; }
.fill { height: 100%; background: var(--wq-accent); }
.pct { font-size: 12px; color: var(--wq-muted); }
</style>
