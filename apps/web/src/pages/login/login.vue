<template>
  <AuthCard>
    <text class="title">{{ t("login.title") }}</text>
    <text class="tagline">{{ t("app.tagline") }}</text>
    <view v-if="checking" class="wq-muted">{{ t("common.loading") }}</view>
    <template v-else>
      <!-- 第 108 轮：国内手机号验证码、微信扫码 -->
      <view v-if="wxTicket" class="wx-note">初次用微信登录：请验证你的手机号，把微信绑定到你的账号上，以后扫码直接登录。</view>
      <text v-if="wxError" class="error" role="alert">{{ wxError }}</text>
      <view v-if="usePhone && !wxTicket" class="tabs">
        <text class="tab" :class="{ on: mode === 'phone' }" @click="mode = 'phone'">手机验证码登录</text>
        <text class="tab" :class="{ on: mode === 'password' }" @click="mode = 'password'">密码登录</text>
      </view>
      <PhoneAuth v-if="wxTicket" mode="bind" :ticket="wxTicket" @done="afterLogin(back)" />
      <PhoneAuth v-else-if="usePhone && mode === 'phone'" mode="login" @done="afterLogin(back)" />
      <template v-else>
      <view class="field">
        <text class="label">{{ isCN && usePhone ? "手机号、邮箱或用户名" : t("login.username") }}</text>
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
      </template>
      <view v-if="site.wechat && !wxTicket" class="wx-btn" @click="wechat">微信扫码登录</view>
      <view v-if="isCN && site.signup" class="alt">
        <text class="wq-muted">{{ t("login.noAccount") }}</text>
        <text class="wq-link strong" @click="register">手机号注册</text>
      </view>
      <view v-else-if="isCN" class="alt">
        <text class="wq-muted">{{ t("reg.cnClosedTitle") }}</text>
      </view>
      <view v-if="!isCN" class="alt">
        <text class="wq-muted">{{ t("login.noAccount") }}</text>
        <text class="wq-link strong" @click="register">{{ t("login.register") }}</text>
      </view>
    </template>
  </AuthCard>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { isCN, loadSite, site } from "../../site";
import PhoneAuth from "../../components/auth/PhoneAuth.vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AuthCard from "../../components/auth/AuthCard.vue";
import { accountApi, afterLogin } from "../../accountApi";
import { api, ApiError, request, token } from "../../api";
import { errorText, locale, t } from "../../i18n";

const username = ref("");
const password = ref("");
const busy = ref(false);
const checking = ref(true);
const errorCode = ref("");
const error = ref("");
const back = ref("");
const mode = ref<"phone" | "password">("phone");
const wxTicket = ref("");
const wxError = ref("");
const usePhone = computed(() => isCN.value && !!site.value.phone);
const WX_ERRORS: Record<string, string> = { expired: "微信扫码已过期，请重新扫码", failed: "微信登录没有成功，请重试",
  org_expired: "你所在单位的体验已到期，请联系问渠科技续期", account_stopped: "此账号已停用", account_suspended: "此账号已停用" };

watch([errorCode, locale], () => (error.value = errorCode.value ? errorText(errorCode.value) : ""));

onLoad((q: any) => {
  back.value = q?.back ? decodeURIComponent(String(q.back)) : "";
  if (q?.email) username.value = decodeURIComponent(String(q.email));
  if (q?.wx) wxTicket.value = String(q.wx);
  if (q?.wx_error) wxError.value = WX_ERRORS[String(q.wx_error)] || "微信登录没有成功，请重试";
});
onShow(async () => {
  uni.setNavigationBarTitle({ title: t("app.name") });
  if (token.value) return afterLogin(back.value);
  // Signed in on the academy website or another platform: no second sign-in.
  if (await accountApi.sso()) return afterLogin(back.value);
  await loadSite();
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
async function wechat() {
  try {
    const r = await request<{ url: string }>("GET", `/api/v1/auth/wechat/url?back=${encodeURIComponent(back.value)}`);
    // #ifdef H5
    window.location.href = r.url;
    // #endif
  } catch (e) {
    wxError.value = e instanceof ApiError && e.detail ? e.detail : "微信登录暂时不可用";
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
.tabs { display: flex; gap: 20px; margin-bottom: 18px; border-bottom: 1px solid var(--wq-line); }
.tab { padding: 0 0 8px; font-size: 15px; color: var(--wq-muted); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; }
.tab.on { color: var(--wq-ink); font-weight: 600; border-bottom-color: var(--wq-accent); }
.wx-btn { margin-top: 12px; height: 44px; line-height: 44px; text-align: center; border-radius: 8px; border: 1px solid #07c160;
  color: #07c160; font-size: 15px; cursor: pointer; }
.wx-note { background: #f0faf4; border: 1px solid #bfe8cf; border-radius: 8px; padding: 10px 12px; font-size: 14px; line-height: 1.6; margin-bottom: 16px; }
</style>
