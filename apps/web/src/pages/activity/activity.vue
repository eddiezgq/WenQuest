<template>
  <view class="page">
    <TopBar />
    <view class="wrap">
      <view class="back" @click="back">‹ {{ t("common.back") }}</view>
      <view v-if="loading" class="muted">{{ t("common.loading") }}</view>
      <view v-else-if="error" class="state">
        <text class="error">{{ errorText(error) }}</text>
        <view class="btn" @click="load">{{ t("common.retry") }}</view>
      </view>
      <view v-else-if="a" class="card">
        <text class="kind">{{ t("type." + kind) }}</text>
        <text class="h1">{{ a.name }}</text>

        <!-- Reading page -->
        <RichContent v-if="a.type === 'page'" :html="a.html || ''" />

        <!-- External link -->
        <view v-else-if="a.type === 'url'">
          <RichContent v-if="a.intro" :html="a.intro" />
          <view class="primary" @click="openLink(a.url || '')">{{ t("activity.openLink") }} ↗</view>
          <text class="small">{{ a.url }}</text>
        </view>

        <!-- Assignment -->
        <view v-else-if="a.type === 'assign'">
          <view class="due">
            <text class="due-label">{{ t("activity.due") }}</text>
            <text class="due-value">{{ a.due ? formatDate(a.due) : t("activity.noDue") }}</text>
          </view>
          <RichContent :html="a.intro || ''" />
          <view class="primary" @click="openLink(a.classic_url)">{{ t("activity.classic") }}</view>
        </view>

        <!-- Files -->
        <view v-else-if="a.type === 'resource'">
          <view v-for="f in a.files" :key="f.url" class="file">
            <text class="file-name">{{ f.name }}</text>
            <text class="file-size">{{ size(f.size) }}</text>
            <view class="btn" @click="download(f.url, f.name)">{{ t("activity.download") }}</view>
          </view>
        </view>

        <!-- Not yet supported in the new UI -->
        <view v-else>
          <text class="muted block">{{ t("activity.classicHint") }}</text>
          <view class="primary" @click="openLink(a.classic_url)">{{ t("activity.classic") }}</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import TopBar from "../../components/TopBar.vue";
import RichContent from "../../components/RichContent.vue";
import { absolute, api, ApiError, type Activity, token } from "../../api";
import { errorText, formatDate, locale, t } from "../../i18n";

const id = ref(0);
const a = ref<Activity | null>(null);
const loading = ref(true);
const error = ref("");

const KNOWN = ["page", "url", "assign", "resource", "quiz", "forum"];
const kind = computed(() => (a.value && KNOWN.includes(a.value.type) ? a.value.type : "other"));

async function load() {
  loading.value = true;
  error.value = "";
  try {
    a.value = await api.activity(id.value);
    uni.setNavigationBarTitle({ title: a.value.name });
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
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

function back() {
  const pages = getCurrentPages();
  if (pages.length > 1) uni.navigateBack();
  else if (a.value) uni.reLaunch({ url: `/pages/course/course?id=${a.value.course_id}` });
  else uni.reLaunch({ url: "/pages/courses/courses" });
}

onLoad((q: any) => {
  id.value = Number(q?.id || 0);
});
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  load();
});
watch(locale, load);
</script>

<style scoped>
.page { min-height: 100vh; background: var(--wq-bg); }
.wrap { max-width: 820px; margin: 0 auto; padding: 16px 16px 48px; }
.back { color: var(--wq-link); font-size: 14px; cursor: pointer; margin-bottom: 8px; display: inline-block; }
.card { background: #fff; border: 1px solid var(--wq-line); border-radius: 12px; padding: 24px 20px; }
.kind { font-size: 12px; letter-spacing: 1px; color: var(--wq-muted); text-transform: uppercase; }
.h1 { display: block; font-size: 24px; font-weight: 700; color: var(--wq-ink); margin: 6px 0 18px; line-height: 1.35; }
.muted { color: var(--wq-muted); }
.block { display: block; margin-bottom: 16px; }
.state { display: flex; align-items: center; gap: 12px; }
.error { color: var(--wq-danger); }
.btn { padding: 6px 14px; border-radius: 8px; background: var(--wq-ink); color: #fff; font-size: 14px; cursor: pointer; flex-shrink: 0; }
.primary {
  display: inline-block; margin-top: 16px; background: var(--wq-accent); color: var(--wq-ink); font-weight: 600;
  padding: 10px 20px; border-radius: 8px; cursor: pointer;
}
.small { display: block; font-size: 12px; color: var(--wq-muted); margin-top: 8px; word-break: break-all; }
.due { display: flex; gap: 12px; align-items: baseline; padding: 10px 14px; background: #fff8e0; border-radius: 8px; margin-bottom: 16px; }
.due-label { font-size: 13px; color: #7a5a00; }
.due-value { font-size: 15px; color: var(--wq-ink); font-weight: 600; }
.file { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--wq-line); }
.file-name { flex: 1; color: var(--wq-ink); word-break: break-all; }
.file-size { font-size: 12px; color: var(--wq-muted); }
</style>
