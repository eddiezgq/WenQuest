<template>
  <!-- 第 108 轮：国内手机号 + 短信验证码（登录 / 注册 / 找回密码 / 微信首次绑定） -->
  <view class="phone-auth">
    <view v-if="mode === 'register'" class="field">
      <text class="label">姓名</text>
      <input class="input" v-model="name" maxlength="40" placeholder="真实姓名" />
    </view>
    <view class="field">
      <text class="label">手机号</text>
      <view class="code-row">
        <input class="input grow" v-model="phone" type="number" maxlength="11" placeholder="11 位手机号" autocomplete="tel" />
        <view class="code-btn" :class="{ disabled: wait > 0 || sending || !phoneOk }" @click="sendCode">
          {{ sending ? "发送中…" : wait > 0 ? `${wait} 秒后重发` : sent ? "重新获取" : "获取验证码" }}
        </view>
      </view>
      <text v-if="sent" class="hint">验证码已发到这个手机，5 分钟内有效</text>
    </view>
    <view class="field">
      <text class="label">验证码</text>
      <input class="input" v-model="code" type="number" maxlength="6" placeholder="6 位数字" autocomplete="one-time-code" @confirm="submit" />
    </view>
    <view v-if="mode === 'reset'" class="field">
      <text class="label">新密码</text>
      <input class="input" v-model="password" password autocomplete="new-password" placeholder="至少 8 位，字母和数字都要有" />
    </view>
    <view v-if="mode === 'register'" class="agree" @click="agree = !agree">
      <text class="box">{{ agree ? "☑" : "☐" }}</text>
      <text>我已阅读并同意<text class="wq-link" @click.stop="openSite('/terms.html')">用户协议</text>和<text class="wq-link" @click.stop="openSite('/privacy.html')">隐私政策</text></text>
    </view>
    <text v-if="error" class="error" role="alert">{{ error }}</text>
    <view class="submit" role="button" :class="{ disabled: busy || !ready }" @click="submit">{{ busy ? "请稍候…" : LABEL[mode] }}</view>
  </view>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import { ApiError, adoptSession, request, type User } from "../../api";
import { PASSWORD_OK, siteUrl } from "../../accountApi";
import { errorText } from "../../i18n";

const props = defineProps<{ mode: "login" | "register" | "reset" | "bind"; ticket?: string; initialPhone?: string }>();
const emit = defineEmits<{ (e: "done"): void }>();
const LABEL = { login: "登录", register: "注册并登录", reset: "重设密码并登录", bind: "绑定微信并登录" } as const;
const PATH = { login: "/api/v1/auth/sms/login", register: "/api/v1/auth/sms/register", reset: "/api/v1/auth/sms/reset",
  bind: "/api/v1/auth/wechat/bind" } as const;

const phone = ref(props.initialPhone || "");
const code = ref("");
const name = ref("");
const password = ref("");
const agree = ref(false);
const busy = ref(false);
const sending = ref(false);
const sent = ref(false);
const wait = ref(0);
const error = ref("");
let timer: ReturnType<typeof setInterval> | null = null;
onUnmounted(() => timer && clearInterval(timer));

const digits = () => phone.value.replace(/\D/g, "").replace(/^86(?=1\d{10}$)/, "");
const phoneOk = computed(() => /^1[3-9]\d{9}$/.test(digits()));
const ready = computed(() => phoneOk.value && code.value.trim().length >= 4
  && (props.mode !== "register" || (name.value.trim().length >= 2 && agree.value))
  && (props.mode !== "reset" || PASSWORD_OK(password.value)));

function say(e: unknown) {
  if (e instanceof ApiError) {
    if (e.code === "code_too_soon") return (error.value = `请 ${e.detail || 60} 秒后再获取`);
    error.value = e.detail && /[一-龥]/.test(e.detail) ? e.detail : errorText(e.code);
  } else error.value = String(e);
}
function countdown(n = 60) {
  wait.value = n;
  timer && clearInterval(timer);
  timer = setInterval(() => { wait.value -= 1; if (wait.value <= 0 && timer) clearInterval(timer); }, 1000);
}
async function sendCode() {
  if (wait.value > 0 || sending.value || !phoneOk.value) return;
  sending.value = true;
  error.value = "";
  try {
    await request("POST", "/api/v1/auth/sms/code", { phone: digits(), purpose: props.mode });
    sent.value = true;
    countdown();
  } catch (e) {
    if (e instanceof ApiError && e.code === "code_too_soon") countdown(Number(e.detail) || 60);
    say(e);
  } finally { sending.value = false; }
}
async function submit() {
  if (busy.value || !ready.value) return;
  busy.value = true;
  error.value = "";
  try {
    const body: Record<string, unknown> = { phone: digits(), code: code.value.trim(), lang: "zh" };
    if (props.mode === "register") Object.assign(body, { name: name.value.trim(), agree: agree.value });
    if (props.mode === "reset") body.password = password.value;
    if (props.mode === "bind") body.ticket = props.ticket;
    const r = await request<{ token: string; user: User }>("POST", PATH[props.mode], body);
    adoptSession(r.token, r.user);
    emit("done");
  } catch (e) { say(e); } finally { busy.value = false; }
}
function openSite(path: string) {
  // #ifdef H5
  window.open(siteUrl(path), "_blank");
  // #endif
}
</script>

<style scoped>
.field { display: flex; flex-direction: column; margin-bottom: 16px; }
.label { font-size: 14px; color: var(--wq-text); margin-bottom: 6px; }
.input { height: 44px; border: 1px solid var(--wq-line); border-radius: 8px; padding: 0 12px; font-size: 16px; background: #fafbfa; }
.code-row { display: flex; gap: 8px; }
.grow { flex: 1; min-width: 0; }
.code-btn { flex: none; height: 44px; line-height: 44px; padding: 0 14px; border-radius: 8px; border: 1px solid var(--wq-accent);
  color: var(--wq-ink); font-size: 14px; cursor: pointer; white-space: nowrap; }
.code-btn.disabled { opacity: 0.5; cursor: default; }
.hint { font-size: 12px; color: var(--wq-muted); margin-top: 6px; }
.agree { display: flex; gap: 8px; align-items: flex-start; font-size: 13px; color: var(--wq-text); margin: 0 0 12px; cursor: pointer; line-height: 1.6; }
.error { color: var(--wq-danger); font-size: 14px; margin-bottom: 12px; display: block; }
.submit { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; border-radius: 8px; height: 46px; line-height: 46px;
  font-size: 16px; margin-top: 4px; text-align: center; cursor: pointer; width: 100%; }
.submit.disabled { opacity: 0.5; cursor: default; }
</style>
