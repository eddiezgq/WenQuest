<template>
  <AuthCard>
    <text class="title">{{ t("forgot.title") }}</text>
    <text class="tagline">{{ t("forgot.tagline") }}</text>
    <view class="field">
      <text class="label">{{ t("reg.email") }}</text>
      <view class="code-row">
        <input class="input grow" v-model="email" autocomplete="email" placeholder="name@example.com" />
        <view class="code-btn" :class="{ disabled: wait > 0 || sending || !emailOk }" @click="sendCode">
          {{ sending ? t("reg.sending") : wait > 0 ? t("reg.resendIn", { n: wait }) : sent ? t("reg.resend") : t("reg.sendCode") }}
        </view>
      </view>
      <text v-if="sent" class="hint">{{ t("forgot.sent") }}</text>
    </view>
    <view class="field">
      <text class="label">{{ t("reg.code") }}</text>
      <input class="input" v-model="code" type="number" maxlength="6" :placeholder="t('reg.codeHint')" autocomplete="one-time-code" />
    </view>
    <view class="field">
      <text class="label">{{ t("forgot.newPassword") }}</text>
      <input class="input" v-model="password" password autocomplete="new-password" :placeholder="t('reg.passwordHint')" />
      <text v-if="password && !pwOk" class="hint bad">{{ t("reg.passwordHint") }}</text>
    </view>
    <text v-if="error" class="error" role="alert">{{ error }}</text>
    <view class="submit" :class="{ disabled: busy || !ready }" @click="submit">{{ busy ? t("common.saving") : t("forgot.submit") }}</view>
    <text class="wq-link center" @click="toLogin">← {{ t("login.submit") }}</text>
  </AuthCard>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import AuthCard from "../../components/auth/AuthCard.vue";
import { PASSWORD_OK, accountApi, afterLogin } from "../../accountApi";
import { ApiError } from "../../api";
import { errorText, t } from "../../i18n";

const email = ref("");
const code = ref("");
const password = ref("");
const busy = ref(false);
const sending = ref(false);
const sent = ref(false);
const wait = ref(0);
const error = ref("");
const back = ref("");
let timer: ReturnType<typeof setInterval> | null = null;
const emailOk = computed(() => /^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$/.test(email.value.trim()));
const pwOk = computed(() => PASSWORD_OK(password.value));
const ready = computed(() => emailOk.value && code.value.trim().length >= 4 && pwOk.value);

onLoad((q: any) => {
  back.value = q?.back ? decodeURIComponent(String(q.back)) : "";
  if (q?.email) email.value = decodeURIComponent(String(q.email));
});
onUnmounted(() => timer && clearInterval(timer));

async function sendCode() {
  if (wait.value > 0 || sending.value || !emailOk.value) return;
  sending.value = true;
  error.value = "";
  try {
    await accountApi.sendCode(email.value.trim(), "reset");
    sent.value = true;
    wait.value = 60;
    timer && clearInterval(timer);
    timer = setInterval(() => { wait.value -= 1; if (wait.value <= 0 && timer) clearInterval(timer); }, 1000);
  } catch (e) {
    error.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    sending.value = false;
  }
}
async function submit() {
  if (busy.value || !ready.value) return;
  busy.value = true;
  error.value = "";
  try {
    await accountApi.reset(email.value.trim(), code.value.trim(), password.value);
    uni.showToast({ title: t("forgot.done"), icon: "none" });
    afterLogin(back.value);
  } catch (e) {
    error.value = errorText(e instanceof ApiError ? e.code : "unknown");
  } finally {
    busy.value = false;
  }
}
const toLogin = () => uni.redirectTo({ url: `/pages/login/login${back.value ? `?back=${encodeURIComponent(back.value)}` : ""}` });
</script>

<style scoped>
.title { font-size: 24px; font-weight: 700; color: var(--wq-ink); }
.tagline { font-size: 14px; color: var(--wq-muted); margin: 6px 0 20px; }
.field { display: flex; flex-direction: column; margin-bottom: 14px; }
.label { font-size: 14px; color: var(--wq-text); margin-bottom: 6px; }
.input { height: 42px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 0 12px; font-size: 15px; background: #fafbfa; }
.code-row { display: flex; gap: 8px; }
.grow { flex: 1; min-width: 0; }
.code-btn { flex-shrink: 0; height: 42px; line-height: 42px; padding: 0 14px; border-radius: 8px; background: var(--wq-ink); color: #fff; font-size: 14px; cursor: pointer; white-space: nowrap; }
.code-btn.disabled { opacity: .45; pointer-events: none; }
.hint { display: block; font-size: 12px; color: var(--wq-muted); margin-top: 5px; }
.hint.bad { color: var(--wq-danger); }
.error { color: var(--wq-danger); font-size: 14px; margin-bottom: 12px; }
.submit { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; border-radius: 8px; height: 46px; line-height: 46px;
  font-size: 16px; text-align: center; cursor: pointer; width: 100%; }
.submit.disabled { opacity: 0.5; cursor: default; }
.center { text-align: center; margin-top: 16px; font-size: 14px; }
</style>
