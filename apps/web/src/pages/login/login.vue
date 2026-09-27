<template>
  <view class="page">
    <view class="lang-row">
      <view class="lang" @click="toggleLocale">{{ t("lang.switch") }}</view>
    </view>
    <view class="card">
      <view class="logo">渠</view>
      <text class="title">{{ t("login.title") }}</text>
      <text class="tagline">{{ t("app.tagline") }}</text>

      <view class="field">
        <text class="label">{{ t("login.username") }}</text>
        <input class="input" v-model="username" :placeholder="t('login.username')" autocomplete="username"
               @confirm="submit" />
      </view>
      <view class="field">
        <text class="label">{{ t("login.password") }}</text>
        <input class="input" v-model="password" password :placeholder="t('login.password')"
               autocomplete="current-password" @confirm="submit" />
      </view>
      <text v-if="error" class="error" role="alert">{{ error }}</text>
      <view class="submit" role="button" :class="{ disabled: busy || !username || !password }" @click="submit">
        {{ busy ? t("login.busy") : t("login.submit") }}
      </view>
      <text class="hint">{{ t("login.hint") }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { api, ApiError, token } from "../../api";
import { errorText, locale, t, toggleLocale } from "../../i18n";

const username = ref("");
const password = ref("");
const busy = ref(false);
const errorCode = ref("");
const error = ref("");

watch([errorCode, locale], () => (error.value = errorCode.value ? errorText(errorCode.value) : ""));

onShow(() => {
  if (token.value) uni.reLaunch({ url: "/pages/courses/courses" });
  uni.setNavigationBarTitle({ title: t("app.name") });
});

async function submit() {
  if (busy.value || !username.value || !password.value) return;
  busy.value = true;
  errorCode.value = "";
  try {
    await api.login(username.value.trim(), password.value);
    uni.reLaunch({ url: "/pages/courses/courses" });
  } catch (e) {
    errorCode.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    busy.value = false;
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--wq-ink); padding: 16px; box-sizing: border-box; }
.lang-row { display: flex; justify-content: flex-end; }
.lang { color: #fff; font-size: 14px; padding: 6px 14px; border: 1px solid rgba(255,255,255,0.35); border-radius: 999px; cursor: pointer; }
.card {
  max-width: 400px; margin: 48px auto 0; background: #fff; border-radius: 16px; padding: 32px 24px;
  display: flex; flex-direction: column;
}
.logo {
  width: 52px; height: 52px; border-radius: 12px; background: var(--wq-accent); color: var(--wq-ink);
  font-size: 28px; font-weight: 700; display: flex; align-items: center; justify-content: center; margin-bottom: 16px;
}
.title { font-size: 24px; font-weight: 700; color: var(--wq-ink); }
.tagline { font-size: 14px; color: var(--wq-muted); margin: 6px 0 24px; }
.field { display: flex; flex-direction: column; margin-bottom: 16px; }
.label { font-size: 14px; color: var(--wq-text); margin-bottom: 6px; }
.input { height: 44px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 0 12px; font-size: 16px; background: #fafbfa; }
.error { color: var(--wq-danger); font-size: 14px; margin-bottom: 12px; }
.submit {
  background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; border-radius: 8px; height: 46px;
  line-height: 46px; font-size: 16px; margin-top: 4px; text-align: center; cursor: pointer; width: 100%;
}
.submit.disabled { opacity: 0.5; cursor: default; }
.hint { font-size: 13px; color: var(--wq-muted); margin-top: 16px; text-align: center; }
</style>
