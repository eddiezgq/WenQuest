<template>
  <view class="page">
    <TopBar />
    <view class="wrap">
      <view class="back" @click="back">‹ {{ t("nav.courses") }}</view>
      <text class="h1">{{ courseName || t("course.outline") }}</text>
      <view v-if="loading" class="muted">{{ t("common.loading") }}</view>
      <view v-else-if="error" class="state">
        <text class="error">{{ errorText(error) }}</text>
        <view class="btn" @click="load">{{ t("common.retry") }}</view>
      </view>
      <view v-else-if="!sections.length" class="muted">{{ t("course.empty") }}</view>
      <view v-else>
        <view v-for="s in sections" :key="s.id" class="section">
          <text class="sec-name">{{ s.name }}</text>
          <text v-if="s.summary" class="sec-summary">{{ s.summary }}</text>
          <view class="mods">
            <template v-for="m in s.modules" :key="m.id">
              <view v-if="m.type === 'label'" class="label"><RichContent :html="m.html || ''" /></view>
              <view v-else class="mod" :class="{ locked: m.locked }" @click="open(m)">
                <view class="icon" :class="'t-' + kind(m.type)">{{ icon(m.type) }}</view>
                <view class="mod-body">
                  <text class="mod-name">{{ m.name }}</text>
                  <text class="mod-type">{{ t("type." + kind(m.type)) }}</text>
                </view>
                <text v-if="m.locked" class="tag">{{ t("course.locked") }}</text>
                <text v-else-if="m.completed" class="tag done">✓ {{ t("course.done") }}</text>
              </view>
            </template>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import TopBar from "../../components/TopBar.vue";
import RichContent from "../../components/RichContent.vue";
import { api, ApiError, type Module, type Section, token } from "../../api";
import { errorText, locale, t } from "../../i18n";

const id = ref(0);
const sections = ref<Section[]>([]);
const courseName = ref("");
const loading = ref(true);
const error = ref("");

const KNOWN = ["page", "url", "assign", "resource", "quiz", "forum"];
const kind = (type: string) => (KNOWN.includes(type) ? type : "other");
const ICONS: Record<string, string> = { page: "文", url: "↗", assign: "✎", resource: "▤", quiz: "?", forum: "✉", other: "•" };
const icon = (type: string) => ICONS[kind(type)];

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const [outline, courses] = await Promise.all([api.outline(id.value), api.courses()]);
    sections.value = outline;
    courseName.value = courses.find((c) => c.id === id.value)?.name || "";
    uni.setNavigationBarTitle({ title: courseName.value || t("course.outline") });
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

function open(m: Module) {
  if (m.locked) return;
  uni.navigateTo({ url: `/pages/activity/activity?id=${m.id}` });
}
function back() {
  const pages = getCurrentPages();
  if (pages.length > 1) uni.navigateBack();
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
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); margin-bottom: 20px; line-height: 1.3; }
.muted { color: var(--wq-muted); }
.state { display: flex; align-items: center; gap: 12px; }
.error { color: var(--wq-danger); }
.btn { padding: 6px 14px; border-radius: 8px; background: var(--wq-ink); color: #fff; font-size: 14px; cursor: pointer; }
.section { background: #fff; border: 1px solid var(--wq-line); border-radius: 12px; padding: 18px 16px; margin-bottom: 16px; }
.sec-name { display: block; font-size: 18px; font-weight: 600; color: var(--wq-ink); }
.sec-summary { display: block; font-size: 14px; color: var(--wq-muted); margin-top: 4px; }
.mods { margin-top: 12px; display: flex; flex-direction: column; gap: 4px; }
.mod { display: flex; align-items: center; gap: 12px; padding: 10px 8px; border-radius: 8px; cursor: pointer; }
.mod:hover { background: #f4f6f5; }
.mod.locked { opacity: 0.5; cursor: default; }
.icon {
  width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 600; flex-shrink: 0; background: #e8eef0; color: var(--wq-ink);
}
.t-assign, .t-quiz { background: #fff3cc; color: #7a5a00; }
.t-url { background: #e3f0f5; color: #1f6f8b; }
.mod-body { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.mod-name { font-size: 15px; color: var(--wq-ink); line-height: 1.4; }
.mod-type { font-size: 12px; color: var(--wq-muted); }
.tag { font-size: 12px; color: var(--wq-muted); flex-shrink: 0; }
.tag.done { color: var(--wq-ok); }
.label { padding: 4px 8px; }
</style>
