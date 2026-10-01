<template>
  <AppShell nav="admin" :title="t('admin.title')">
    <view class="wrap">
      <view class="wq-head">
        <text class="wq-h1">{{ t("admin.title") }}</text>
        <view v-if="info" class="wq-row health">
          <text class="wq-tag" :class="info.mail ? 'ok' : 'live'">{{ info.mail ? t("admin.mailOn") : t("admin.mailOff") }}</text>
          <text class="wq-tag" :class="info.ai && info.ai !== 'none' ? 'ok' : 'live'">AI · {{ info.ai }}</text>
        </view>
      </view>
      <text v-if="denied" class="wq-error">{{ t("admin.denied") }}</text>
      <template v-else>
        <view class="wq-tabs">
          <text class="wq-tab" :class="{ on: tab === 'apps' }" @click="setTab('apps')">{{ t("admin.apps") }}<text v-if="info?.applications" class="count">{{ info.applications }}</text></text>
          <text class="wq-tab" :class="{ on: tab === 'requests' }" @click="setTab('requests')">{{ t("admin.requests") }}<text v-if="info?.requests" class="count">{{ info.requests }}</text></text>
          <text class="wq-tab" :class="{ on: tab === 'users' }" @click="setTab('users')">{{ t("admin.users") }}</text>
          <text class="wq-tab" :class="{ on: tab === 'committee' }" @click="setTab('committee')">{{ t("rev.committee") }}</text>
        </view>

        <!-- teacher applications -->
        <template v-if="tab === 'apps'">
          <view class="wq-row filter">
            <text class="chip" :class="{ on: appFilter === 'open' }" @click="appFilter = 'open'; loadApps()">{{ t("admin.open") }}</text>
            <text class="chip" :class="{ on: appFilter === 'done' }" @click="appFilter = 'done'; loadApps()">{{ t("admin.done") }}</text>
          </view>
          <text v-if="loading" class="wq-muted">{{ t("common.loading") }}</text>
          <view v-else-if="!apps.length" class="wq-empty">{{ appFilter === 'open' ? t("admin.noApps") : t("admin.noDone") }}</view>
          <view v-for="a in apps" :key="a.id" class="wq-card appcard" :class="'rec-' + (a.ai?.recommendation || 'none')">
            <view class="a-top">
              <view class="a-who">
                <text class="a-name">{{ a.name }}</text>
                <text class="a-org">{{ a.institution }}<text v-if="a.department"> · {{ a.department }}</text><text v-if="a.title"> · {{ a.title }}</text></text>
                <text class="wq-muted">{{ a.email }} · {{ day(a.created) }}<text v-if="a.school"> · {{ t("admin.schoolMail") }}</text></text>
              </view>
              <text class="wq-tag" :class="statusClass(a)">{{ statusText(a) }}</text>
            </view>

            <view v-if="a.ai" class="ai">
              <view class="wq-row">
                <text class="rec" :class="a.ai.recommendation">✦ {{ t("admin.rec." + a.ai.recommendation) }}</text>
                <text class="ai-reason">{{ a.ai.reason }}</text>
              </view>
              <view v-if="a.ai.checks.length" class="checks">
                <text v-for="(c, i) in a.ai.checks" :key="i" class="check" :class="c.result">{{ mark(c.result) }} {{ c.item }}：{{ c.note }}</text>
              </view>
              <text v-if="a.status === 'need_more'" class="wq-muted block">{{ t("admin.askedMore", { d: day(a.more_requested) }) }}</text>
            </view>
            <text v-else-if="!a.school" class="wq-muted block">{{ t("admin.notReviewed") }}</text>
            <text v-if="a.note" class="a-note">“{{ a.note }}”</text>

            <view v-if="a.evidence.length" class="ev">
              <view v-for="(e, i) in a.evidence" :key="i" class="ev-item" @click="openFile(e.url)">
                <image v-if="e.mime.startsWith('image/')" :src="e.url" mode="aspectFill" class="ev-img" />
                <text v-else class="ev-pdf">PDF</text>
                <text class="ev-name">{{ e.name }}</text>
              </view>
            </view>

            <view v-if="a.status === 'pending' || a.status === 'need_more'" class="acts">
              <template v-if="rejecting === a.id">
                <text class="wq-label">{{ t("admin.rejectReason") }}</text>
                <textarea v-model="reason" class="wq-textarea short" />
                <view class="wq-row">
                  <view class="wq-btn dark" :class="{ disabled: busy === a.id }" @click="decide(a, false)">{{ t("admin.sendReject") }}</view>
                  <view class="wq-btn" @click="rejecting = 0">{{ t("common.cancel") }}</view>
                </view>
              </template>
              <view v-else class="wq-row">
                <view class="wq-btn primary big" :class="{ disabled: busy === a.id }" @click="decide(a, true)">✓ {{ t("admin.approve") }}</view>
                <view class="wq-btn" @click="startReject(a)">{{ t("admin.reject") }}</view>
                <text class="wq-link" @click="rereview(a)">{{ busy === a.id ? t("admin.reviewing") : t("admin.rereview") }}</text>
              </view>
            </view>
            <text v-else-if="a.reason" class="wq-muted block">{{ t("admin.reasonSent") }}：{{ a.reason }}</text>
          </view>
        </template>

        <!-- paid course requests -->
        <template v-if="tab === 'requests'">
          <text v-if="loading" class="wq-muted">{{ t("common.loading") }}</text>
          <view v-else-if="!reqs.length" class="wq-empty">{{ t("admin.noRequests") }}</view>
          <view v-for="r in reqs" :key="r.id" class="wq-card req">
            <view class="r-main">
              <text class="a-name">{{ r.name }}</text>
              <text class="wq-muted">{{ r.email }} · {{ day(r.created) }}</text>
              <text class="r-course">{{ t("admin.wants") }}《{{ r.course }}》 · {{ money(r.price, r.currency) }}</text>
              <text v-if="r.note" class="a-note">“{{ r.note }}”</text>
            </view>
            <view class="wq-row">
              <view class="wq-btn primary" :class="{ disabled: busy === r.id }" @click="decideReq(r.id, true)">✓ {{ t("admin.openCourse") }}</view>
              <view class="wq-btn" :class="{ disabled: busy === r.id }" @click="decideReq(r.id, false)">{{ t("admin.reject") }}</view>
            </view>
          </view>
        </template>

        <!-- users -->
        <template v-if="tab === 'users'">
          <view class="wq-row filter">
            <input v-model="q" class="wq-input search" :placeholder="t('admin.search')" @confirm="loadUsers(0)" />
            <view class="wq-btn" @click="loadUsers(0)">{{ t("admin.find") }}</view>
            <text class="wq-muted">{{ t("admin.total", { n: total }) }}</text>
          </view>
          <view class="table">
            <view class="tr th">
              <text class="c-n">{{ t("admin.person") }}</text><text class="c-r">{{ t("admin.role") }}</text>
              <text class="c-d">{{ t("admin.joined") }}</text><text class="c-a"></text>
            </view>
            <view v-for="u in users" :key="u.id" class="tr" :class="{ off: u.suspended }">
              <view class="c-n"><text class="u-name">{{ u.fullname }}</text><text class="wq-muted">{{ u.email || u.username }}</text></view>
              <view class="c-r">
                <text class="wq-tag" :class="u.admin ? 'live' : u.teacher ? 'info' : ''">{{ u.admin ? t("admin.isAdmin") : u.teacher ? t("admin.roleTeacher") : t("admin.roleStudent") }}</text>
                <text v-if="u.suspended" class="wq-tag live">{{ t("admin.suspended") }}</text>
              </view>
              <text class="c-d wq-muted">{{ day(u.timecreated) }}</text>
              <view v-if="!u.admin" class="c-a wq-row">
                <text class="wq-link" @click="change(u, { teacher: !u.teacher })">{{ u.teacher ? t("admin.unteacher") : t("admin.makeTeacher") }}</text>
                <text class="wq-link" :class="{ danger: !u.suspended }" @click="change(u, { suspended: !u.suspended })">{{ u.suspended ? t("admin.restore") : t("admin.suspend") }}</text>
                <text class="wq-link" @click="resetPw(u)">{{ t("admin.resetPw") }}</text>
              </view>
            </view>
          </view>
          <view class="wq-row pager">
            <view v-if="page > 0" class="wq-btn small" @click="loadUsers(page - 1)">‹</view>
            <view v-if="(page + 1) * 50 < total" class="wq-btn small" @click="loadUsers(page + 1)">›</view>
          </view>
        </template>
        <!-- course committee (round 6) -->
        <template v-if="tab === 'committee'">
          <view class="com">
            <text class="wq-muted">{{ t("rev.adminHint") }}</text>
            <text class="com-l">{{ t("rev.members") }}</text>
            <textarea v-model="comMembers" class="com-in" auto-height :placeholder="t('rev.membersHint')" />
            <text class="com-l">{{ t("rev.chair") }}</text>
            <input v-model="comChair" class="wq-input" :placeholder="t('rev.chairHint')" />
            <label class="wq-row"><switch :checked="comSelf" @change="(e: any) => (comSelf = e.detail.value)" /><text>{{ t("rev.selfReview") }}</text></label>
            <view class="wq-row"><view class="wq-btn primary" @click="saveCommittee">{{ t("common.save") }}</view></view>
            <view v-if="comNow.length" class="com-now">
              <text v-for="m in comNow" :key="m.id" class="wq-tag" :class="m.id === comChairId ? 'live' : 'info'">{{ m.name }}{{ m.id === comChairId ? " · " + t("rev.chair") : "" }}</text>
            </view>
          </view>
        </template>
        <text v-if="error" class="wq-error">{{ error }}</text>
      </template>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { type AdminUser, type Application, type EnrolRequest, accountApi, loadAdmin } from "../../accountApi";
import { api, ApiError, token } from "../../api";
import { confirmAction } from "../../courseApi";
import { errorText, t } from "../../i18n";

const tab = ref<"apps" | "requests" | "users" | "committee">("apps");
const comMembers = ref("");
const comChair = ref("");
const comSelf = ref(true);
const comNow = ref<{ id: number; name: string; email: string; key?: string }[]>([]);
const comChairId = ref(0);
function showCommittee(r: { members: { id: number; name: string; email: string; key?: string }[]; chair: number; self_review: boolean }) {
  comNow.value = r.members;
  comChairId.value = r.chair;
  comMembers.value = r.members.map((m) => m.key || m.email || m.name).join("\n");
  const c = r.members.find((m) => m.id === r.chair);
  comChair.value = c ? c.key || c.email || c.name : "";
  comSelf.value = r.self_review;
}
async function loadCommittee() {
  try { showCommittee(await api.adminCommittee()); } catch (e) { fail(e); }
}
async function saveCommittee() {
  error.value = "";
  try {
    const members = comMembers.value.split(/[\n,，;；]+/).map((x) => x.trim()).filter(Boolean);
    showCommittee(await api.adminSetCommittee(members, comChair.value.trim(), comSelf.value));
    uni.showToast({ title: t("rev.saved"), icon: "none" });
  } catch (e) { fail(e); }
}
const info = ref<{ admin: boolean; applications?: number; requests?: number; mail?: boolean; ai?: string } | null>(null);
const denied = ref(false);
const loading = ref(false);
const error = ref("");
const busy = ref(0);
const apps = ref<Application[]>([]);
const appFilter = ref<"open" | "done">("open");
const rejecting = ref(0);
const reason = ref("");
const reqs = ref<EnrolRequest[]>([]);
const users = ref<AdminUser[]>([]);
const total = ref(0);
const page = ref(0);
const q = ref("");

const fail = (e: unknown) => (error.value = errorText(e instanceof ApiError ? e.code : "unknown"));
async function refreshInfo() {
  info.value = await accountApi.summary();
  denied.value = !info.value.admin;
  loadAdmin(true);
}
async function loadApps() {
  loading.value = true;
  error.value = "";
  try { apps.value = await accountApi.applications(appFilter.value); } catch (e) { fail(e); } finally { loading.value = false; }
}
async function loadReqs() {
  loading.value = true;
  try { reqs.value = await accountApi.requests(); } catch (e) { fail(e); } finally { loading.value = false; }
}
async function loadUsers(p: number) {
  try {
    const r = await accountApi.users(q.value.trim(), p);
    users.value = r.users;
    total.value = r.total;
    page.value = p;
  } catch (e) { fail(e); }
}
function setTab(x: typeof tab.value) {
  tab.value = x;
  error.value = "";
  if (x === "apps") loadApps();
  else if (x === "requests") loadReqs();
  else if (x === "committee") loadCommittee();
  else loadUsers(0);
}

function startReject(a: Application) {
  rejecting.value = a.id;
  reason.value = a.ai && a.ai.recommendation !== "approve" ? a.ai.message_to_applicant : "";
}
async function decide(a: Application, approve: boolean) {
  busy.value = a.id;
  error.value = "";
  try {
    const r = await accountApi.decide(a.id, approve, approve ? "" : reason.value);
    uni.showToast({ title: r.mailed ? t("admin.doneMailed") : t("admin.doneNoMail"), icon: "none" });
    rejecting.value = 0;
    await Promise.all([loadApps(), refreshInfo()]);
  } catch (e) { fail(e); } finally { busy.value = 0; }
}
async function rereview(a: Application) {
  busy.value = a.id;
  try { await accountApi.rereview(a.id); await loadApps(); } catch (e) { fail(e); } finally { busy.value = 0; }
}
async function decideReq(id: number, approve: boolean) {
  busy.value = id;
  try {
    await accountApi.decideRequest(id, approve);
    uni.showToast({ title: approve ? t("admin.opened") : t("admin.declined"), icon: "none" });
    await Promise.all([loadReqs(), refreshInfo()]);
  } catch (e) { fail(e); } finally { busy.value = 0; }
}
async function change(u: AdminUser, body: { suspended?: boolean; teacher?: boolean }) {
  if (body.suspended && !(await confirmAction(t("admin.suspendConfirm", { name: u.fullname }), t("admin.suspend"), t("common.cancel")))) return;
  try {
    const n = await accountApi.changeUser(u.id, body);
    Object.assign(u, n);
  } catch (e) { fail(e); }
}
async function resetPw(u: AdminUser) {
  try {
    const r = await accountApi.resetUser(u.id);
    uni.showToast({ title: r.mailed ? t("admin.resetSent") : t("admin.doneNoMail"), icon: "none" });
  } catch (e) { fail(e); }
}

const day = (s: number) => (s ? new Date(s * 1000).toLocaleDateString() : "—");
const mark = (r: string) => ({ ok: "✓", doubt: "?", bad: "✕", unknown: "·" } as Record<string, string>)[r] || "·";
const money = (p: number, c: string) => (c === "USD" ? `$${p}` : `¥${p}`);
function statusText(a: Application) {
  if (a.status === "approved" && a.decided_by === "auto") return t("admin.autoApproved");
  return t("apply.status." + a.status);
}
const statusClass = (a: Application) => ({ approved: "ok", rejected: "live", pending: "info", need_more: "" } as Record<string, string>)[a.status] || "";
function openFile(url: string) {
  // #ifdef H5
  window.open(url, "_blank");
  // #endif
}

onLoad((qq: any) => { if (qq?.tab) tab.value = qq.tab; });
onShow(async () => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login?back=" + encodeURIComponent("/pages/admin/admin") });
  try { await refreshInfo(); } catch (e) { fail(e); }
  if (!denied.value) setTab(tab.value);
});
</script>

<style scoped>
.wrap { max-width: 980px; }
.health { gap: 6px; }
.count { display: inline-block; margin-left: 6px; background: var(--wq-danger); color: #fff; border-radius: 999px; font-size: 11px; padding: 0 6px; line-height: 17px; }
.filter { margin-bottom: 12px; }
.chip { padding: 4px 12px; border-radius: 999px; border: 1px solid var(--wq-line); font-size: 13px; cursor: pointer; background: #fff; }
.chip.on { background: var(--wq-ink); color: #fff; border-color: var(--wq-ink); }
.appcard { border-left: 4px solid var(--wq-line); }
.appcard.rec-approve { border-left-color: var(--wq-ok); }
.appcard.rec-reject { border-left-color: var(--wq-danger); }
.appcard.rec-more, .appcard.rec-manual { border-left-color: var(--wq-accent); }
.a-top { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.a-who { display: flex; flex-direction: column; gap: 2px; }
.a-name { font-size: 17px; font-weight: 700; color: var(--wq-ink); }
.a-org { font-size: 14px; color: var(--wq-text); }
.ai { background: #f7f9f9; border-radius: 8px; padding: 10px 12px; margin-top: 10px; }
.rec { font-weight: 700; font-size: 14px; }
.rec.approve { color: var(--wq-ok); }
.rec.reject { color: var(--wq-danger); }
.rec.more, .rec.manual { color: #8a6400; }
.ai-reason { color: var(--wq-text); font-size: 14px; }
.checks { display: flex; flex-direction: column; gap: 2px; margin-top: 6px; }
.check { font-size: 13px; color: var(--wq-muted); }
.check.ok { color: var(--wq-ok); }
.check.bad { color: var(--wq-danger); }
.a-note { display: block; margin-top: 8px; font-size: 13px; color: var(--wq-text); font-style: italic; }
.block { display: block; margin-top: 6px; }
.ev { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
.ev-item { width: 120px; cursor: pointer; }
.ev-img { width: 120px; height: 84px; border-radius: 6px; border: 1px solid var(--wq-line); background: #eee; display: block; }
.ev-pdf { display: flex; width: 120px; height: 84px; align-items: center; justify-content: center; border-radius: 6px; background: #fde7e5; color: var(--wq-danger); font-weight: 700; }
.ev-name { display: block; font-size: 12px; color: var(--wq-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.acts { margin-top: 12px; }
.wq-btn.big { padding: 9px 26px; font-size: 15px; }
.short { min-height: 70px; }
.req { display: flex; justify-content: space-between; gap: 12px; align-items: center; flex-wrap: wrap; }
.r-main { display: flex; flex-direction: column; gap: 2px; }
.r-course { font-size: 14px; color: var(--wq-ink); }
.search { width: 260px; }
.com { display: flex; flex-direction: column; gap: 8px; max-width: 560px; }
.com-l { font-weight: 600; margin-top: 6px; }
.com-in { width: 100%; min-height: 80px; border: 1px solid var(--wq-line); border-radius: 6px; padding: 8px; box-sizing: border-box; background: #fff; }
.com-now { display: flex; flex-wrap: wrap; gap: 6px; }
.table { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; }
.tr { display: flex; align-items: center; gap: 10px; padding: 9px 14px; border-top: 1px solid var(--wq-line); }
.tr.th { border-top: 0; background: #f3f5f5; font-size: 13px; color: var(--wq-muted); }
.tr.off { opacity: .6; }
.c-n { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.u-name { color: var(--wq-ink); font-weight: 600; }
.c-r { width: 130px; display: flex; gap: 4px; flex-wrap: wrap; }
.c-d { width: 90px; }
.c-a { width: 230px; justify-content: flex-end; }
.pager { margin-top: 10px; justify-content: flex-end; }
@media (max-width: 760px) { .c-d { display: none; } .c-a { width: auto; } .tr { flex-wrap: wrap; } }
</style>
