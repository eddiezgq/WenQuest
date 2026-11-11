<template>
  <!-- 第 97 轮：问渠质量 ERP 试点企业。管理员发邀请，企业凭链接自己注册，服务器自动开通（每家一套） -->
  <view class="pilots">
    <view v-if="info" class="wq-row head">
      <text class="wq-tag info">{{ zh ? "试点企业" : "Pilot companies" }} {{ info.used }} / {{ info.max }}</text>
      <text v-if="info.host.fresh" class="wq-tag" :class="(info.host.mem_free_mb || 0) >= info.min_free_mb ? 'ok' : 'live'">
        {{ zh ? "服务器可用内存" : "Free memory" }} {{ ((info.host.mem_free_mb || 0) / 1024).toFixed(1) }} GB</text>
      <text v-else class="wq-tag live">{{ zh ? "开通程序没在运行（服务器上还没装好，或停了）" : "The server's opening program is not running" }}</text>
    </view>
    <text v-if="err" class="wq-error block">{{ err }}</text>

    <view class="wq-card">
      <text class="wq-label strong">{{ zh ? "邀请一家企业" : "Invite a company" }}</text>
      <text class="wq-muted block">{{ zh
        ? "对方收到邮件，7 天内打开链接，填单位名称和联系人、用这个邮箱收验证码确认，系统自动开通（约 15 分钟），账号发到这个邮箱。免费试用 3 个月。"
        : "They get an email, open the link within 7 days, enter the company and their name, confirm with a code sent to this address, and it is set up automatically (about 15 minutes); the sign-in is emailed. Free for 3 months." }}</text>
      <view class="grid">
        <input v-model="f.email" class="wq-input" :placeholder="zh ? '对方邮箱 *' : 'Their email *'" maxlength="254" />
        <input v-model="f.company" class="wq-input" :placeholder="zh ? '单位名称（写在邀请信里，可不填）' : 'Company (for the letter, optional)'" maxlength="100" />
      </view>
      <view class="wq-row">
        <view class="wq-btn primary" :class="{ disabled: busy || !f.email.trim() }" @click="invite">{{ zh ? "发邀请" : "Send invitation" }}</view>
        <text v-if="sent" class="wq-muted">{{ zh ? "已发到" : "Sent to" }} {{ sent.email }} · <text class="wq-link" @click="copy(sent.link)">{{ zh ? "复制邀请链接" : "Copy the link" }}</text></text>
      </view>
    </view>

    <view v-if="info && !info.tenants.length" class="wq-empty">{{ zh ? "还没有试点企业。" : "No pilot companies yet." }}</view>
    <view v-for="x in info?.tenants || []" :key="x.id" class="wq-card">
      <view class="wq-row">
        <text class="strong">{{ x.company }}</text>
        <text class="wq-tag" :class="TAG[x.status] || ''">{{ (zh ? ZH : EN)[x.status] || x.status }}</text>
        <text class="wq-muted">{{ x.contact }} · {{ x.email }}</text>
      </view>
      <text v-if="x.url" class="wq-link block" @click="open(x.url)">{{ x.url }}</text>
      <text v-if="x.error" class="wq-error block">{{ x.error }}</text>
      <view class="wq-row acts">
        <text v-if="x.status === 'active'" class="wq-link danger" @click="act(x.id, 'stop')">{{ zh ? "停用（记录保留）" : "Stop (records kept)" }}</text>
        <text v-if="x.status === 'stopped'" class="wq-link" @click="act(x.id, 'start')">{{ zh ? "恢复" : "Start again" }}</text>
      </view>
    </view>

    <view v-if="info?.invites.length" class="wq-card">
      <text class="wq-label strong">{{ zh ? "最近的邀请" : "Recent invitations" }}</text>
      <view v-for="v in info.invites" :key="v.created + v.email" class="wq-row">
        <text>{{ v.email }}</text><text class="wq-muted">{{ v.company }}</text>
        <text class="wq-tag" :class="v.used ? 'ok' : v.live ? 'info' : ''">{{ v.used ? (zh ? "已注册" : "registered") : v.live ? (zh ? "等对方注册" : "waiting") : (zh ? "已过期" : "expired") }}</text>
        <!-- 第 151 轮：对方收不到验证码邮件时，管理员当场取码转给他 -->
        <template v-if="v.live && !v.used">
          <text class="wq-link" @click="copy(v.link)">{{ zh ? "复制邀请链接" : "Copy the link" }}</text>
          <text class="wq-link" @click="giveCode(v.token)">{{ zh ? "给验证码" : "Get a code for them" }}</text>
        </template>
      </view>
      <text v-if="given" class="wq-muted block">{{ zh ? "给" : "Code for" }} {{ given.email }}{{ zh ? " 的验证码：" : ": " }}<text class="strong code">{{ given.code }}</text>
        · <text class="wq-link" @click="copy(given.code)">{{ zh ? "复制" : "Copy" }}</text>
        · {{ zh ? "24 小时内有效，没发邮件。请转给对方，在邀请页填进去；再点一次“给验证码”，这个码就作废。"
              : "Valid for 24 hours; no email was sent. Pass it on; they enter it on the invitation page. Getting another code voids this one." }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from "vue";
import { ApiError, request } from "../../api";
import { errorText, locale } from "../../i18n";

interface Tenant { id: string; company: string; contact: string; email: string; status: string; error: string | null; url: string | null }
interface Info { max: number; used: number; min_free_mb: number; host: { fresh: boolean; mem_free_mb?: number };
  invites: { email: string; company: string; created: number; used: number; live: boolean; token: string; link: string }[]; tenants: Tenant[] }

const ZH: Record<string, string> = { queued: "排队开通", installing: "正在开通", active: "使用中", stopped: "已停用", failed: "开通失败" };
const EN: Record<string, string> = { queued: "queued", installing: "being set up", active: "in use", stopped: "stopped", failed: "failed" };
const TAG: Record<string, string> = { active: "ok", failed: "live", stopped: "live", installing: "info", queued: "info" };
const zh = computed(() => locale.value === "zh");
const info = ref<Info | null>(null);
const err = ref("");
const busy = ref(false);
const sent = ref<{ email: string; link: string } | null>(null);
const f = reactive({ email: "", company: "" });
const given = ref<{ email: string; code: string } | null>(null);
let timer: ReturnType<typeof setTimeout> | undefined;

function fail(e: unknown) {
  err.value = e instanceof ApiError ? (e.message && /[一-龥A-Za-z]/.test(e.message) ? e.message : errorText(e.code)) : String(e);
}
async function load() {
  clearTimeout(timer);
  try { info.value = await request<Info>("GET", "/api/v1/admin/pilots"); } catch (e) { fail(e); }
  if (info.value?.tenants.some((x) => x.status === "queued" || x.status === "installing")) timer = setTimeout(load, 15000);
}
async function invite() {
  if (busy.value || !f.email.trim()) return;
  busy.value = true; err.value = "";
  try {
    sent.value = await request<{ email: string; link: string }>("POST", "/api/v1/admin/pilots/invite",
      { email: f.email.trim(), company: f.company.trim() });   // 第 129 轮：语言按站点（美国英文、国内中文），不跟管理员界面走
    Object.assign(f, { email: "", company: "" });
    await load();
  } catch (e) { fail(e); } finally { busy.value = false; }
}
async function giveCode(token: string) {
  err.value = "";
  try { given.value = await request<{ email: string; code: string }>("POST", `/api/v1/admin/pilots/invites/${token}/code`); }
  catch (e) { fail(e); }
}
async function act(id: string, what: "stop" | "start") {
  try { await request("POST", `/api/v1/admin/pilots/${id}/${what}`); await load(); } catch (e) { fail(e); }
}
function copy(text: string) { uni.setClipboardData({ data: text }); }
function open(url: string) {
  // #ifdef H5
  window.open(url, "_blank", "noopener");
  // #endif
}
onMounted(load);
onUnmounted(() => clearTimeout(timer));
</script>

<style scoped>
.head { flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px; margin: 10px 0; }
.acts { gap: 16px; margin-top: 6px; }
.block { display: block; }
.strong { font-weight: 600; }
.code { font-size: 18px; letter-spacing: 2px; }
</style>
