<template>
  <AppShell nav="video3d" :title="t('v3.title')">
    <view class="wrap">
      <view class="head">
        <view>
          <text class="h1">{{ t("v3.title") }}</text>
          <text class="lead">{{ t("v3.lead") }}</text>
        </view>
      </view>

      <view v-if="error" class="alert">{{ errorText(error) }}</view>
      <view v-if="!loading && !error && !renderOn" class="note">{{ t("v3.noMachines") }}</view>

      <!-- 第 56 轮：只开通了缝纫机设计软件的单位，从设计软件一键出讲解片，这里只看、改自己的讲解片 -->
      <view v-if="!loading && !error && !general" class="note">{{ t("v3.sewingOnly") }}</view>
      <!-- 一句话新建 -->
      <view v-if="!error && general" class="card new">
        <text class="label">{{ t("v3.ask") }}</text>
        <textarea v-model="prompt" class="area" :placeholder="t('v3.askPh')" maxlength="2000" />
        <view class="row-end">
          <text class="hint">{{ t("v3.askHint") }}</text>
          <view class="primary" :class="{ disabled: busy }" @click="create('')">{{ busy || t("v3.write") }}</view>
        </view>
      </view>

      <!-- 样片 -->
      <view v-if="samples.length" class="sec">
        <text class="h2">{{ t("v3.samples") }}</text>
        <view class="grid">
          <view v-for="s in samples" :key="s.id" class="sample">
            <text class="s-title">{{ pick(s.title) }}</text>
            <text class="s-meta">{{ t("v3.seconds", { n: s.duration }) }}</text>
            <text class="link" @click="create(s.id)">{{ t("v3.fromSample") }} →</text>
          </view>
        </view>
      </view>

      <!-- 我的视频 -->
      <view v-if="!error" class="sec">
        <text class="h2">{{ t("v3.mine") }}</text>
        <view v-if="loading" class="muted">{{ t("common.loading") }}</view>
        <view v-else-if="!videos.length" class="empty">{{ t("v3.none") }}</view>
        <view v-else class="list">
          <view v-for="v in videos" :key="v.id" class="row" @click="open(v.id)">
            <image v-if="v.poster" class="thumb" :src="v.poster" mode="aspectFill" />
            <view v-else class="thumb blank" />
            <view class="r-main">
              <text class="r-title">{{ pick(v.title) }}</text>
              <text class="r-meta">{{ formatDate(v.updated) }}</text>
            </view>
            <text v-if="v.busy" class="chip busy">{{ t("v3.aiWriting") }}</text>
            <text v-for="(r, q) in v.renders" :key="q" class="chip" :class="chipClass(r.state)">{{ t("v3.q." + q) }} · {{ t("v3.st." + r.state) }}</text>
            <text class="link danger" @click.stop="remove(v)">{{ t("v3.delete") }}</text>
            <text class="chev">›</text>
          </view>
        </view>
      </view>

      <!-- 管理员：开通企业账号、用机记录 -->
      <view v-if="isAdmin" class="sec">
        <text class="h2">{{ t("v3.admin") }}</text>
        <view class="card">
          <text class="hint">{{ t("v3.grantHint") }}</text>
          <view class="grant">
            <input v-model="grantName" class="input" :placeholder="t('v3.grantName')" maxlength="120" />
            <input v-model="grantNote" class="input" :placeholder="t('v3.grantNote')" maxlength="200" />
            <view class="primary" @click="grant">{{ t("v3.grant") }}</view>
          </view>
          <view v-if="adminMsg" class="hint">{{ adminMsg }}</view>
          <view v-for="g in ov?.grants || []" :key="g.user_id" class="g-row">
            <text>{{ g.username }}<text v-if="g.note" class="muted"> · {{ g.note }}</text></text>
            <text class="link danger" @click="revoke(g.user_id)">{{ t("v3.revoke") }}</text>
          </view>
          <text class="label">{{ t("v3.runs") }}</text>
          <text class="hint">{{ t("v3.runsSum", { n: ov?.runs.length || 0, h: ov?.hours || 0, c: ov?.cost || 0 }) }}</text>
          <view v-for="r in (ov?.runs || []).slice(0, 30)" :key="r.id" class="g-row small">
            <text>{{ formatDate(r.queued_at) }} · {{ t("v3.q." + r.quality) }} · {{ r.kind || "—" }} · {{ t("v3.st." + r.state) }}</text>
            <text class="muted">{{ Math.round((r.seconds || 0) / 60) }} min · ${{ (r.cost || 0).toFixed(2) }}</text>
          </view>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { api, ApiError, token, type V3AdminOverview, type V3Sample, type V3Summary } from "../../api";
import { errorText, formatDate, locale, t } from "../../i18n";

defineOptions({ inheritAttrs: false });

const samples = ref<V3Sample[]>([]);
const videos = ref<V3Summary[]>([]);
const loading = ref(true);
const error = ref("");
const busy = ref("");
const prompt = ref("");
const general = ref(true);
const renderOn = ref(true);
const isAdmin = ref(false);
const ov = ref<V3AdminOverview | null>(null);
const grantName = ref("");
const grantNote = ref("");
const adminMsg = ref("");

const pick = (x: { zh: string; en: string } | undefined) => (x ? (locale.value === "en" ? x.en || x.zh : x.zh || x.en) : "");
const chipClass = (s: string) => (s === "done" ? "ok" : s === "failed" ? "bad" : s === "cancelled" ? "" : "busy");

async function load() {
  error.value = "";
  try {
    const r = await api.v3Index();
    samples.value = r.samples;
    videos.value = r.videos;
    renderOn.value = r.render_on;
    isAdmin.value = r.admin;
    general.value = r.general !== false;
    if (r.admin) ov.value = await api.v3Admin();
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  } finally {
    loading.value = false;
  }
}

async function create(sample: string) {
  if (busy.value) return;
  if (!sample && !prompt.value.trim()) return uni.showToast({ title: t("v3.needAsk"), icon: "none" });
  busy.value = t("v3.creating");
  try {
    const v = await api.v3Create(sample ? { sample } : { prompt: prompt.value.trim() });
    prompt.value = "";
    open(v.id);
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  } finally {
    busy.value = "";
  }
}

function open(id: string) {
  uni.navigateTo({ url: `/pages/video3d/edit?id=${id}` });
}

function remove(v: V3Summary) {
  uni.showModal({
    title: t("v3.delete"), content: t("v3.deleteAsk", { name: pick(v.title) }),
    success: async (r) => {
      if (!r.confirm) return;
      try { await api.v3Delete(v.id); await load(); } catch (e) { error.value = e instanceof ApiError ? e.code : "unknown"; }
    },
  });
}

async function grant() {
  adminMsg.value = "";
  if (!grantName.value.trim()) return;
  try {
    const r = await api.v3Grant(grantName.value.trim(), grantNote.value.trim());
    adminMsg.value = t("v3.granted", { name: r.fullname || r.username });
    grantName.value = grantNote.value = "";
    ov.value = await api.v3Admin();
  } catch (e) {
    adminMsg.value = errorText(e instanceof ApiError ? e.code : "unknown");
  }
}

async function revoke(uid: number) {
  try { await api.v3Revoke(uid); ov.value = await api.v3Admin(); } catch { /* shown on next load */ }
}

onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t("v3.title") });
  load();
});
</script>

<style scoped>
.wrap { max-width: 1040px; }
.head { margin-bottom: 16px; }
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); }
.h2 { display: block; font-size: 18px; font-weight: 700; color: var(--wq-ink); margin: 22px 0 10px; }
.lead { display: block; color: var(--wq-muted); margin-top: 6px; line-height: 1.7; max-width: 720px; }
.card { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 16px; }
.label { display: block; font-weight: 600; color: var(--wq-ink); margin: 6px 0; font-size: 14px; }
.area { border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 10px; height: 84px; width: 100%; box-sizing: border-box; font-size: 15px; }
.input { border: 1px solid var(--wq-line); border-radius: 8px; padding: 0 10px; height: 38px; line-height: 38px; font-size: 15px; box-sizing: border-box; flex: 1; min-width: 160px; }
.row-end { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-top: 10px; flex-wrap: wrap; }
.hint { color: var(--wq-muted); font-size: 13px; line-height: 1.6; display: block; }
.primary { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 9px 18px; border-radius: 8px; cursor: pointer; white-space: nowrap; text-align: center; }
.disabled { opacity: .6; pointer-events: none; }
.alert { background: #fdecea; color: var(--wq-danger); padding: 10px 14px; border-radius: 8px; margin: 10px 0; }
.note { background: #fff3d6; color: #7a5a00; padding: 10px 14px; border-radius: 8px; margin: 10px 0; line-height: 1.6; }
.muted { color: var(--wq-muted); }
.empty { background: #fff; border: 1px dashed var(--wq-line); border-radius: 8px; padding: 24px; text-align: center; color: var(--wq-muted); line-height: 1.7; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.sample { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 14px; display: flex; flex-direction: column; gap: 4px; }
.s-title { font-weight: 600; color: var(--wq-ink); }
.s-meta { color: var(--wq-muted); font-size: 13px; }
.list { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; overflow: hidden; }
.row { display: flex; align-items: center; gap: 10px; padding: 12px 14px; cursor: pointer; border-top: 1px solid var(--wq-line); flex-wrap: wrap; }
.row:first-child { border-top: 0; }
.row:hover { background: #f7f9f8; }
.thumb { width: 96px; height: 54px; border-radius: 4px; background: #eef1f0; flex: none; }
.r-main { flex: 1; min-width: 160px; }
.r-title { display: block; font-weight: 600; color: var(--wq-ink); }
.r-meta { display: block; font-size: 13px; color: var(--wq-muted); margin-top: 2px; }
.chip { font-size: 12px; padding: 2px 8px; border-radius: 999px; white-space: nowrap; background: #f1f3f2; color: var(--wq-muted); }
.chip.busy { background: #e7f1f5; color: var(--wq-link); }
.chip.bad { background: #fdecea; color: var(--wq-danger); }
.chip.ok { background: #e6f4ea; color: #2e7d4f; }
.link { color: var(--wq-link); font-size: 14px; white-space: nowrap; cursor: pointer; }
.link.danger { color: var(--wq-muted); }
.chev { color: var(--wq-muted); }
.grant { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0; }
.g-row { display: flex; justify-content: space-between; gap: 10px; padding: 8px 0; border-top: 1px solid var(--wq-line); font-size: 14px; flex-wrap: wrap; }
.g-row.small { font-size: 13px; }
</style>
