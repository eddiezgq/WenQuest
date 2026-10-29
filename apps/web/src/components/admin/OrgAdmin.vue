<template>
  <!-- 第 50 轮：国内服务器上的“体验单位”：按单位开通在线体验，每家若干账号，体验期满自动停用 -->
  <view class="orgs">
    <view v-if="info" class="wq-row head">
      <text class="wq-tag info">体验单位 {{ info.live }} / {{ info.max }}</text>
      <text class="wq-muted">每家默认 {{ info.default_seats }} 个账号（最多 {{ info.max_seats }}），体验期 {{ info.trial_days }} 天</text>
      <text v-if="info.expiring.length" class="wq-tag live">{{ info.expiring.length }} 家 7 天内到期</text>
    </view>
    <text v-if="err" class="wq-error block">{{ err }}</text>

    <!-- 开通 -->
    <view class="wq-card">
      <text class="wq-label strong">开通一家单位</text>
      <view v-if="reqs.length" class="reqs">
        <text class="wq-muted block">从官网的预约申请带入（点一下）：</text>
        <view class="chips">
          <text v-for="r in reqs.slice(0, 12)" :key="r.id" class="chip" :class="{ trial: r.trial }" @click="fromReq(r)">{{ r.trial ? "申请体验 · " : "" }}{{ r.org }} · {{ r.name }}<template v-if="r.trial"> · {{ r.seats }} 个账号</template></text>
        </view>
      </view>
      <view class="grid">
        <input v-model="f.name" class="wq-input" placeholder="单位名称 *" maxlength="100" />
        <picker :range="KIND_NAMES" :value="KINDS.indexOf(f.kind)" @change="(e: any) => (f.kind = KINDS[+e.detail.value])">
          <view class="wq-input pk">{{ KIND_NAMES[KINDS.indexOf(f.kind)] }} ▾</view>
        </picker>
        <input v-model="f.contact" class="wq-input" placeholder="联系人" maxlength="40" />
        <input v-model="f.phone" class="wq-input" placeholder="联系电话" maxlength="20" />
        <input v-model="f.email" class="wq-input" placeholder="联系邮箱" maxlength="254" />
        <input v-model.number="f.seats" class="wq-input" type="number" :placeholder="'账号数（默认 ' + (info?.default_seats || 5) + '）'" />
      </view>
      <view class="wq-row">
        <view class="wq-btn primary" :class="{ disabled: busy || !f.name.trim() }" @click="openOrg">开通体验</view>
        <text class="wq-muted">体验期从今天起 {{ info?.trial_days || 90 }} 天</text>
      </view>
    </view>

    <view v-if="!orgs.length && info" class="wq-empty">还没有体验单位。</view>
    <view v-for="o in orgs" :key="o.id" class="wq-card org" :class="{ off: !o.live }">
      <view class="wq-row o-head">
        <text class="o-name">{{ o.name }}</text>
        <text class="wq-tag">{{ KIND_NAMES[KINDS.indexOf(o.kind)] || o.kind }}</text>
        <text v-if="o.live" class="wq-tag ok">体验中 · 还剩 {{ o.days_left }} 天</text>
        <text v-else-if="o.status === 'stopped'" class="wq-tag live">已停用</text>
        <text v-else class="wq-tag live">已到期</text>
        <text class="wq-muted">账号 {{ o.used }} / {{ o.seats }}</text>
      </view>
      <text class="wq-muted block">{{ [o.contact, o.phone, o.email].filter(Boolean).join(" · ") || "（没有登记联系人）" }}</text>
      <view class="wq-row acts">
        <text class="wq-link" @click="change(o, { extend_days: 30 })">延长 30 天</text>
        <text class="wq-link" @click="change(o, { extend_days: 90 })">延长 90 天</text>
        <text v-if="o.seats < (info?.max_seats || 20)" class="wq-link" @click="change(o, { seats: o.seats + 1 })">账号数 +1</text>
        <text v-if="o.status === 'active'" class="wq-link danger" @click="change(o, { status: 'stopped' })">停用</text>
        <text v-else class="wq-link" @click="change(o, { status: 'active' })">恢复</text>
      </view>

      <view v-for="mb in o.members" :key="mb.userid" class="wq-row mem">
        <text class="m-name">{{ mb.name }}</text>
        <text class="wq-muted">{{ mb.email }} · {{ mb.phone }}</text>
        <text v-if="mb.stopped" class="wq-tag live">已停用</text>
        <view class="gap" />
        <text class="wq-link" @click="newPw(o, mb)">重设密码</text>
        <text class="wq-link" :class="{ danger: !mb.stopped }" @click="stopMember(o, mb)">{{ mb.stopped ? "恢复" : "停用" }}</text>
      </view>

      <view v-if="o.live && o.used < o.seats" class="add">
        <view class="grid3">
          <input v-model="mf(o.id).name" class="wq-input" placeholder="姓名 *" maxlength="40" />
          <input v-model="mf(o.id).phone" class="wq-input" placeholder="手机 *" maxlength="20" />
          <input v-model="mf(o.id).email" class="wq-input" placeholder="邮箱（登录用）*" maxlength="254" />
        </view>
        <view class="wq-btn" :class="{ disabled: busy }" @click="addMember(o)">添加账号</view>
      </view>

      <view v-if="shown && shown.org === o.id" class="pw">
        <text class="block strong">账号已就绪，请把下面的登录信息交给本人（密码只显示这一次）：</text>
        <text class="block mono">登录：{{ shown.login }}　密码：{{ shown.password }}</text>
        <text class="wq-link" @click="copy(`登录：${shown.login}  密码：${shown.password}`)">复制</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ApiError, request } from "../../api";
import { errorText } from "../../i18n";

interface Member { userid: number; name: string; phone: string; email: string; stopped: number }
interface Org { id: number; name: string; kind: string; contact: string; phone: string; email: string; seats: number; used: number;
  status: string; live: boolean; days_left: number; members: Member[] }
interface Info { live: number; max: number; default_seats: number; max_seats: number; trial_days: number; expiring: number[]; orgs: Org[] }
interface Req { id: number; org: string; name: string; phone: string; email: string; industry: string; trial?: number; seats?: number }

const KINDS = ["company", "school", "other"];
const KIND_NAMES = ["企业", "学校", "其他"];
const info = ref<Info | null>(null);
const orgs = ref<Org[]>([]);
const reqs = ref<Req[]>([]);
const err = ref("");
const busy = ref(false);
const shown = ref<{ org: number; login: string; password: string } | null>(null);
const f = reactive({ name: "", kind: "company", contact: "", phone: "", email: "", seats: undefined as number | undefined, request_id: 0 });
const forms = reactive<Record<number, { name: string; phone: string; email: string }>>({});
const mf = (id: number) => (forms[id] ||= { name: "", phone: "", email: "" });

function fail(e: unknown) {
  err.value = e instanceof ApiError ? (e.message && /[一-龥]/.test(e.message) ? e.message : errorText(e.code)) : String(e);
}
async function load() {
  try {
    const r = await request<Info>("GET", "/api/v1/admin/orgs");
    info.value = r;
    orgs.value = r.orgs;
  } catch (e) { fail(e); }
  try {
    const rows = (await request<{ rows: Req[] }>("GET", "/api/v1/admin/demo-request")).rows;
    const opened = new Set(orgs.value.map((o) => o.name));
    reqs.value = rows.filter((r) => !opened.has(r.org)).sort((a, b) => (b.trial || 0) - (a.trial || 0));   // 申请体验的排前面
  } catch { reqs.value = []; }
}
function fromReq(r: Req) {
  Object.assign(f, { name: r.org, contact: r.name, phone: r.phone, email: r.email, request_id: r.id, seats: r.trial && r.seats ? r.seats : undefined,
    kind: /学校|学院|大学|职业/.test(r.org + r.industry) ? "school" : "company" });
}
async function run(fn: () => Promise<unknown>) {
  if (busy.value) return;
  busy.value = true;
  err.value = "";
  try { await fn(); await load(); } catch (e) { fail(e); } finally { busy.value = false; }
}
function openOrg() {
  if (!f.name.trim()) return;
  run(async () => {
    await request("POST", "/api/v1/admin/orgs", { name: f.name.trim(), kind: f.kind, contact: f.contact, phone: f.phone, email: f.email,
      seats: f.seats || undefined, request_id: f.request_id || undefined });
    Object.assign(f, { name: "", contact: "", phone: "", email: "", seats: undefined, request_id: 0 });
  });
}
function change(o: Org, body: Record<string, unknown>) {
  run(() => request("PUT", `/api/v1/admin/orgs/${o.id}`, body));
}
function addMember(o: Org) {
  const m = mf(o.id);
  if (!m.name.trim() || !m.phone.trim() || !m.email.trim()) { err.value = "姓名、手机、邮箱都要填"; return; }
  run(async () => {
    const r = await request<{ login: string; password: string }>("POST", `/api/v1/admin/orgs/${o.id}/members`, { ...m });
    shown.value = { org: o.id, ...r };
    forms[o.id] = { name: "", phone: "", email: "" };
  });
}
function newPw(o: Org, mb: Member) {
  run(async () => {
    const r = await request<{ login: string; password: string }>("POST", `/api/v1/admin/orgs/${o.id}/members/${mb.userid}/password`);
    shown.value = { org: o.id, ...r };
  });
}
function stopMember(o: Org, mb: Member) {
  run(() => request("PUT", `/api/v1/admin/orgs/${o.id}/members/${mb.userid}`, { stopped: !mb.stopped }));
}
function copy(text: string) {
  uni.setClipboardData({ data: text });
}
onMounted(load);
defineExpose({ load });
</script>

<style scoped>
.head { gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin: 10px 0; }
.grid3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-bottom: 8px; }
@media (max-width: 700px) { .grid, .grid3 { grid-template-columns: 1fr; } }
.pk { display: flex; align-items: center; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0; }
.chip { font-size: 13px; padding: 4px 10px; border: 1px solid var(--wq-line); border-radius: 999px; cursor: pointer; background: #fff; }
.chip:hover { border-color: var(--wq-link); }
.chip.trial { border-color: #9fd8cf; background: #e3f4f1; }
.org.off { opacity: .75; }
.o-head { gap: 8px; flex-wrap: wrap; align-items: center; }
.o-name { font-size: 17px; font-weight: 700; color: var(--wq-ink); }
.acts { gap: 14px; flex-wrap: wrap; margin: 8px 0; }
.mem { gap: 10px; align-items: center; padding: 8px 0; border-top: 1px solid var(--wq-line); flex-wrap: wrap; }
.m-name { font-weight: 600; }
.gap { flex: 1; }
.add { margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--wq-line); }
.pw { margin-top: 10px; background: #fff8e1; border: 1px solid #f2d27a; border-radius: 8px; padding: 10px 12px; }
.mono { font-family: ui-monospace, Menlo, monospace; margin: 4px 0; }
.danger { color: var(--wq-danger); }
.strong { font-weight: 600; }
.block { display: block; }
</style>
