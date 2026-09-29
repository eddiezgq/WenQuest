<template>
  <view class="page">
    <view class="top">
      <view class="brand" @click="home">
        <text class="mark">问渠</text>
        <text class="sub">{{ t("auth.academy") }}</text>
      </view>
      <view class="lang" @click="toggleLocale">{{ t("lang.switch") }}</view>
    </view>
    <view class="card" :class="{ wide }">
      <slot />
    </view>
    <view class="foot">
      <text class="flink" @click="open('/terms.html')">{{ t("auth.terms") }}</text>
      <text class="dot">·</text>
      <text class="flink" @click="open('/privacy.html')">{{ t("auth.privacy") }}</text>
      <text class="dot">·</text>
      <text class="flink" @click="catalog">{{ t("catalog.title") }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { siteUrl } from "../../accountApi";
import { t, toggleLocale } from "../../i18n";

defineProps<{ wide?: boolean }>();
function open(path: string) {
  // #ifdef H5
  window.open(siteUrl(path), "_blank");
  // #endif
}
const catalog = () => uni.reLaunch({ url: "/pages/catalog/catalog" });
function home() {
  // #ifdef H5
  window.location.href = siteUrl("/");
  // #endif
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--wq-ink); padding: 16px; box-sizing: border-box; }
.top { display: flex; justify-content: space-between; align-items: center; max-width: 960px; margin: 0 auto; }
.brand { display: flex; align-items: baseline; gap: 10px; cursor: pointer; }
.mark { font-family: "Noto Serif SC", "Songti SC", serif; font-weight: 900; font-size: 22px; color: #fff; letter-spacing: 2px; }
.sub { color: var(--wq-accent); font-size: 13px; }
.lang { color: #fff; font-size: 14px; padding: 6px 14px; border: 1px solid rgba(255,255,255,0.35); border-radius: 999px; cursor: pointer; }
.card { max-width: 420px; margin: 40px auto 0; background: #fff; border-radius: 16px; padding: 30px 26px; display: flex; flex-direction: column; box-sizing: border-box; }
.card.wide { max-width: 560px; }
.foot { text-align: center; margin: 22px 0 10px; font-size: 13px; }
.flink { color: #b9c7cc; cursor: pointer; }
.flink:hover { color: #fff; }
.dot { color: #62757d; margin: 0 8px; }
</style>
