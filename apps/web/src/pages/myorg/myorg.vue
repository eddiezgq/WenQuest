<template>
  <!-- 第 96 轮：单位负责人自己给同事开账号、停用、重设密码（名额和体验期由问渠定） -->
  <AppShell nav="account" title="我的单位">
    <text class="h1">我的单位</text>
    <view v-if="loading" class="wq-muted">正在加载…</view>
    <view v-else-if="!o" class="wq-empty">你不是哪家单位的负责人。需要给同事开账号，请联系问渠科技。</view>
    <template v-else>
      <view class="wq-card">
        <text class="org-name">{{ o.name }}</text>
        <view class="wq-row tags">
          <text v-if="o.live" class="wq-tag ok">体验中 · 还剩 {{ o.days_left }} 天</text>
          <text v-else class="wq-tag live">体验已到期或已停用</text>
          <text class="wq-muted">账号 {{ o.used }} / {{ o.seats }}（要更多账号或延长体验，请联系问渠科技）</text>
        </view>
      </view>

      <view class="wq-card">
        <text class="wq-label strong">账号</text>
        <view v-for="mb in o.members" :key="mb.userid" class="wq-row mem">
          <text class="m-name">{{ mb.name }}<text v-if="mb.owner" class="wq-tag info">负责人</text></text>
          <text class="wq-muted">{{ [mb.phone, mb.email].filter(Boolean).join(" · ") }}</text>
          <text v-if="mb.stopped" class="wq-tag live">已停用</text>
          <view class="gap" />
          <template v-if="!mb.owner">
            <text class="wq-link" @click="newPw(mb)">重设密码</text>
            <text class="wq-link" :class="{ danger: !mb.stopped }" @click="stop(mb)">{{ mb.stopped ? "恢复" : "停用" }}</text>
          </template>
        </view>

        <view v-if="o.live && o.used < o.seats" class="add">
          <text class="wq-label">给同事开账号</text>
          <view class="grid3">
            <input v-model="f.name" class="wq-input" placeholder="姓名 *" maxlength="40" />
            <input v-model="f.phone" class="wq-input" placeholder="手机 *（登录用）" maxlength="20" />
            <input v-model="f.email" class="wq-input" placeholder="邮箱（选填）" maxlength="254" />
          </view>
          <view class="wq-btn primary" :class="{ disabled: busy }" @click="add">{{ busy ? "正在开通…" : "开通账号" }}</view>
        </view>
        <text v-if="err" class="wq-error block">{{ err }}</text>

        <view v-if="shown" class="pw">
          <text class="block strong">账号已就绪，请把下面的登录信息发给本人（密码只显示这一次；本人也可以用手机号收验证码登录）：</text>
          <text class="block mono">网址：{{ loginUrl }}　登录：{{ shown.login }}　密码：{{ shown.password }}</text>
          <text class="wq-link" @click="copy">复制</text>
        </view>
      </view>
    </template>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import AppShell from "../../components/AppShell.vue";
import { ApiError, request } from "../../api";
import { errorText } from "../../i18n";

interface Member { userid: number; name: string; phone: string; email: string; stopped: number; owner: number }
interface Org { id: number; name: string; seats: number; used: number; live: boolean; days_left: number; members: Member[] }

const o = ref<Org | null>(null);
const loading = ref(true);
const busy = ref(false);
const err = ref("");
const shown = ref<{ login: string; password: string } | null>(null);
const f = reactive({ name: "", phone: "", email: "" });
const loginUrl = typeof window !== "undefined" && window.location ? `${window.location.origin}/pages/login/login` : "";

function fail(e: unknown) {
  err.value = e instanceof ApiError ? (e.detail && /[一-龥]/.test(e.detail) ? e.detail : errorText(e.code)) : String(e);
}
async function load() {
  try { o.value = await request<Org>("GET", "/api/v1/my/org"); } catch { o.value = null; } finally { loading.value = false; }
}
async function run(fn: () => Promise<unknown>) {
  if (busy.value) return;
  busy.value = true;
  err.value = "";
  try { await fn(); await load(); } catch (e) { fail(e); } finally { busy.value = false; }
}
function add() {
  const phone = f.phone.replace(/\D/g, "").replace(/^86(?=1\d{10}$)/, "");
  if (!f.name.trim()) return (err.value = "请填姓名");
  if (!/^1[3-9]\d{9}$/.test(phone)) return (err.value = "请填 11 位手机号，本人用它登录");
  if (f.email.trim() && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email.trim())) return (err.value = "邮箱格式不对，例如 123456789@qq.com");
  run(async () => {
    shown.value = await request<{ login: string; password: string }>("POST", "/api/v1/my/org/members",
      { name: f.name.trim(), phone, email: f.email.trim() });
    Object.assign(f, { name: "", phone: "", email: "" });
  });
}
function stop(mb: Member) {
  run(() => request("PUT", `/api/v1/my/org/members/${mb.userid}`, { stopped: !mb.stopped }));
}
function newPw(mb: Member) {
  run(async () => { shown.value = await request("POST", `/api/v1/my/org/members/${mb.userid}/password`); });
}
function copy() {
  if (!shown.value) return;
  uni.setClipboardData({ data: `问渠学习平台\n网址：${loginUrl}\n登录：${shown.value.login}\n密码：${shown.value.password}` });
}
onMounted(load);
</script>

<style scoped>
.h1 { font-size: 22px; font-weight: 700; display: block; margin-bottom: 14px; }
.org-name { font-size: 18px; font-weight: 700; display: block; margin-bottom: 8px; }
.tags { gap: 10px; flex-wrap: wrap; align-items: center; }
.mem { gap: 10px; align-items: center; padding: 8px 0; border-top: 1px solid var(--wq-line); flex-wrap: wrap; }
.m-name { font-weight: 600; display: inline-flex; gap: 6px; align-items: center; }
.gap { flex: 1; }
.add { margin-top: 12px; padding-top: 12px; border-top: 1px dashed var(--wq-line); }
.grid3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 8px; margin: 8px 0 10px; }
.pw { margin-top: 12px; background: #fff8e1; border: 1px solid #f2d27a; border-radius: 8px; padding: 10px 12px; }
.mono { font-family: ui-monospace, Menlo, monospace; margin: 6px 0; word-break: break-all; }
.block { display: block; }
.strong { font-weight: 600; }
</style>
