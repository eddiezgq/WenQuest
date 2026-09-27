<template>
  <view class="topbar">
    <view class="brand" @click="home">
      <view class="mark">渠</view>
      <text class="name">{{ t("app.name") }}</text>
    </view>
    <view class="right">
      <text v-if="user" class="who">{{ user.fullname }}</text>
      <view class="chip" @click="toggleLocale" :aria-label="'language'">{{ t("lang.switch") }}</view>
      <view v-if="user" class="chip ghost" @click="logout">{{ t("nav.logout") }}</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { api, user } from "../api";
import { t, toggleLocale } from "../i18n";

function home() {
  if (user.value) uni.reLaunch({ url: "/pages/courses/courses" });
}
function logout() {
  api.logout();
  uni.reLaunch({ url: "/pages/login/login" });
}
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--wq-ink);
  color: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}
.brand { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.mark {
  width: 30px; height: 30px; border-radius: 8px; background: var(--wq-accent); color: var(--wq-ink);
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 17px;
}
.name { font-size: 18px; font-weight: 600; letter-spacing: 0.5px; }
.right { display: flex; align-items: center; gap: 8px; }
.who { font-size: 14px; color: #c9d4d8; margin-right: 4px; }
.chip {
  font-size: 13px; padding: 5px 12px; border-radius: 999px; background: rgba(255,255,255,0.12); cursor: pointer;
}
.chip.ghost { background: transparent; border: 1px solid rgba(255,255,255,0.3); }
@media (max-width: 480px) { .who { display: none; } }
</style>
