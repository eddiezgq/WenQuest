<template>
  <AuthCard>
    <text class="title">{{ t("login.title") }}</text>
    <text class="tagline">{{ t("app.tagline") }}</text>
    <view v-if="checking" class="wq-muted">{{ t("common.loading") }}</view>
    <template v-else>
      <view class="field">
        <text class="label">{{ t("login.username") }}</text>
        <input class="input" v-model="username" :placeholder="t('login.usernameHint')" autocomplete="username" @confirm="submit" />
      </view>
      <view class="field">
        <view class="label-row">
          <text class="label">{{ t("login.password") }}</text>
          <text class="wq-link" @click="forgot">{{ t("login.forgot") }}</text>
        </view>
        <input class="input" v-model="password" password :placeholder="t('login.password')" autocomplete="current-password" @confirm="submit" />
      </view>
      <text v-if="error" class="error" role="alert">{{ error }}</text>
      <view class="submit" role="button" :class="{ disabled: busy || !username || !password }" @click="submit">
        {{ busy ? t("login.busy") : t("login.submit") }}
      </view>
      <view class="alt">
        <text class="wq-muted">{{ t("login.noAccount") }}</text>
        <text class="wq-link strong" @click="register">{{ t("login.register") }}</text>
      </view>
    </template>
  </AuthCard>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AuthCard from "../../components/auth/AuthCard.vue";
import { accountApi, afterLogin } from "../../accountApi";
import { api, ApiError, token } from "../../api";
import { errorText, locale, t } from "../../i18n";

const username = ref("");
const password = ref("");
const busy = ref(false);
const checking = ref(true);
const errorCode = ref("");
const error = ref("");
const back = ref("");

watch([errorCode, locale], () => (error.value = errorCode.value ? errorText(errorCode.value) : ""));

onLoad((q: any) => {
  back.value = q?.back ? decodeURIComponent(String(q.back)) : "";
  if (q?.email) username.value = decodeURIComponent(String(q.email));
});
onShow(async () => {
  uni.setNavigationBarTitle({ title: t("app.name") });
  if (token.value) return afterLogin(back.value);
  // Signed in on the academy website or another platform: no second sign-in.
  if (await accountApi.sso()) return afterLogin(back.value);
  checking.value = false;
});

async function submit() {
  if (busy.value || !username.value || !password.value) return;
  busy.value = true;
  errorCode.value = "";
  try {
    await api.login(username.value.trim(), password.value);
    afterLogin(back.value);
  } catch (e) {
    errorCode.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    busy.value = false;
  }
}
const q = () => (back.value ? `?back=${encodeURIComponent(back.value)}` : "");
const forgot = () => uni.navigateTo({ url: `/pages/login/forgot${q()}${username.value.includes("@") ? `${q() ? "&" : "?"}email=${encodeURIComponent(username.value.trim())}` : ""}` });
const register = () => uni.navigateTo({ url: `/pages/register/register${q()}` });
</script>

<style scoped>
.title { font-size: 24px; font-weight: 700; color: var(--wq-ink); }
.tagline { font-size: 14px; color: var(--wq-muted); margin: 6px 0 24px; }
.field { display: flex; flex-direction: column; margin-bottom: 16px; }
.label-row { display: flex; justify-content: space-between; align-items: baseline; }
.label { font-size: 14px; color: var(--wq-text); margin-bottom: 6px; }
.input { height: 44px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 0 12px; font-size: 16px; background: #fafbfa; }
.error { color: var(--wq-danger); font-size: 14px; margin-bottom: 12px; }
.submit { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; border-radius: 8px; height: 46px; line-height: 46px;
  font-size: 16px; margin-top: 4px; text-align: center; cursor: pointer; width: 100%; }
.submit.disabled { opacity: 0.5; cursor: default; }
.alt { display: flex; justify-content: center; gap: 8px; margin-top: 18px; align-items: baseline; }
.strong { font-size: 15px; font-weight: 600; }
</style>
