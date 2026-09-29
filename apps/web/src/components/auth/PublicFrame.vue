<template>
  <view class="pf">
    <view class="bar">
      <view class="brand" @click="home">
        <text class="mark">问渠</text>
        <text class="sub">{{ t("auth.academy") }}</text>
      </view>
      <view class="right">
        <text class="lang" @click="toggleLocale">{{ t("lang.switch") }}</text>
        <text class="in" @click="go('/pages/login/login')">{{ t("login.submit") }}</text>
        <text class="up" @click="go('/pages/register/register')">{{ t("login.register") }}</text>
      </view>
    </view>
    <view class="body"><slot /></view>
  </view>
</template>

<script setup lang="ts">
import { siteUrl } from "../../accountApi";
import { t, toggleLocale } from "../../i18n";

const props = defineProps<{ back?: string }>();
const go = (url: string) => uni.navigateTo({ url: `${url}?back=${encodeURIComponent(props.back || "/pages/catalog/catalog")}` });
function home() {
  // #ifdef H5
  window.location.href = siteUrl("/");
  // #endif
}
</script>

<style scoped>
.pf { min-height: 100vh; background: var(--wq-bg); }
.bar { background: var(--wq-ink); display: flex; justify-content: space-between; align-items: center; padding: 12px 24px; }
.brand { display: flex; align-items: baseline; gap: 10px; cursor: pointer; }
.mark { font-family: "Noto Serif SC", "Songti SC", serif; font-weight: 900; font-size: 20px; color: #fff; letter-spacing: 2px; }
.sub { color: var(--wq-accent); font-size: 13px; }
.right { display: flex; gap: 14px; align-items: center; }
.lang { color: #c9d4d8; font-size: 13px; cursor: pointer; }
.in { color: #fff; font-size: 14px; cursor: pointer; }
.up { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 6px 14px; border-radius: 999px; font-size: 14px; cursor: pointer; }
.body { max-width: 1080px; margin: 0 auto; padding: 24px 20px 64px; }
</style>
