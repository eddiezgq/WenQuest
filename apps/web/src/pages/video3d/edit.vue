<template>
  <AppShell nav="video3d" :title="t('v3.title')">
    <view class="wrap">
      <view class="top">
        <text class="back" @click="back">‹ {{ t("v3.title") }}</text>
        <text class="h1">{{ v ? pick(v.title) : "" }}</text>
      </view>
      <view v-if="error" class="alert">{{ errorText(error) }}</view>
      <view v-if="v" class="cols">
        <!-- 左：对话 -->
        <view class="chat card">
          <text class="label">{{ t("v3.talk") }}</text>
          <scroll-view scroll-y class="msgs">
            <view v-for="(c, i) in v.chat" :key="i" class="msg" :class="c.who">
              <AiBadge v-if="c.who === 'ai'" />
              <text>{{ c.text }}</text>
            </view>
            <view v-if="v.busy" class="msg ai muted">{{ t(v.busy === "voice" ? "v3.voicing" : "v3.aiWriting") }}…</view>
          </scroll-view>
          <view v-if="v.ai_error" class="alert small">{{ v.ai_error }}</view>
          <textarea v-model="say" class="area" :placeholder="t('v3.sayPh')" maxlength="2000" :disabled="!!v.busy" />
          <view class="primary" :class="{ disabled: !!v.busy || !say.trim() }" @click="send">{{ t("v3.send") }}</view>
        </view>

        <!-- 中：出片 -->
        <view class="main">
          <view class="tabs">
            <text v-for="k in ['stills', 'draft', 'hd']" :key="k" class="tab" :class="{ on: tab === k }" @click="tab = k">{{ t("v3.tab." + k) }}</text>
          </view>
          <!-- 第 99 轮：配旁白开关（老视频打开就配一次；关掉不再配） -->
          <view v-if="v.voice_on || (v.voice && v.voice.on)" class="vsw" :class="{ disabled: !!v.busy }" @click="toggleVoice">
            <text class="box">{{ v.voice && v.voice.on ? "☑" : "☐" }}</text><text>{{ t("v3.voiceSwitch") }}</text>
            <text v-if="voiceNote" class="muted"> · {{ voiceNote }}</text>
          </view>

          <view class="card stage">
            <template v-if="tab === 'stills'">
              <view v-if="stills.state === 'running'" class="wait">{{ t("v3.stillsRunning") }}</view>
              <view v-else-if="stills.state === 'failed'" class="alert small">{{ t("v3.failed") }}：{{ stills.error }}</view>
              <view v-else-if="stills.urls && stills.urls.length" class="stills">
                <view v-for="(u, i) in stills.urls" :key="u" class="still">
                  <image :src="u" mode="widthFix" class="img" @click="preview(i)" />
                  <text class="cap">{{ (stills.times || [])[i] }} s</text>
                </view>
              </view>
              <view v-else class="wait">{{ t("v3.stillsNone") }}</view>
              <view class="acts">
                <text v-if="stills.stale && stills.urls" class="stale">{{ t("v3.stale") }}</text>
                <view class="primary" :class="{ disabled: stills.state === 'running' || !!v.busy || !v.stills_on }" @click="doStills">{{ t("v3.doStills") }}</view>
              </view>
            </template>

            <template v-else>
              <view v-if="r && r.urls && r.urls.mp4">
                <!-- #ifdef H5 -->
                <video :src="r.urls.mp4" controls class="video" />
                <!-- #endif -->
                <view class="acts left">
                  <a class="link" :href="r.urls.mp4" target="_blank" rel="noopener" download>{{ t("v3.download") }} MP4</a>
                  <a v-if="r.urls.webm" class="link" :href="r.urls.webm" target="_blank" rel="noopener" download>WebM</a>
                </view>
              </view>
              <view v-if="r && live(r.state)" class="wait">
                <text>{{ stageText(r) }}</text>
                <view v-if="r.total" class="bar"><view class="fill" :style="{ width: Math.round(100 * (r.done || 0) / r.total) + '%' }" /></view>
              </view>
              <view v-else-if="r && r.state === 'failed'" class="alert small">{{ t("v3.failed") }}：{{ r.error }}</view>
              <view v-else-if="!r" class="wait">{{ t(tab === "hd" ? "v3.hdNone" : "v3.draftNone") }}</view>
              <view class="acts">
                <text v-if="r && r.stale && r.state === 'done'" class="stale">{{ t("v3.stale") }}</text>
                <text v-if="r && live(r.state)" class="link danger" @click="cancel">{{ t("v3.cancel") }}</text>
                <view v-else class="primary" :class="{ disabled: !!v.busy || !v.render_on }" @click="render">{{ t(tab === "hd" ? "v3.doHd" : "v3.doDraft") }}</view>
              </view>
              <text v-if="v.voice && v.voice.on && v.voice.state === 'done' && v.voice.version === v.version" class="hint">{{ t("v3.withVoice") }}</text>
              <text v-if="!v.render_on" class="hint">{{ t("v3.noMachines") }}</text>
              <text v-else class="hint">{{ t(tab === "hd" ? "v3.hdHint" : "v3.draftHint") }}</text>
            </template>
          </view>

          <!-- 时间线（只读）与场景文件（高级） -->
          <view class="card">
            <text class="label">{{ t("v3.timeline") }} <text class="muted">· {{ t("v3.seconds", { n: v.timeline?.duration || 0 }) }} · {{ t("v3.shots", { n: v.timeline?.shots || 0 }) }}</text></text>
            <view v-for="(x, i) in tlRows" :key="i" class="tl" :class="{ say: x.kind === 'voice' }">
              <text class="tl-t">{{ x.when }}</text>
              <text v-if="x.kind === 'voice'" class="tl-x"><text class="vtag">{{ t("v3.narration") }}</text> {{ x.text }}</text>
              <text v-else class="tl-x">{{ x.text }}<text v-if="x.bottom" class="muted"> · {{ t("v3.subtitle") }}</text></text>
            </view>
            <text class="link" @click="showScene = !showScene">{{ showScene ? t("v3.hideScene") : t("v3.editScene") }}</text>
            <template v-if="showScene">
              <textarea v-model="scene" class="code" maxlength="40000" />
              <view v-if="sceneErr" class="alert small">{{ sceneErr }}</view>
              <view class="acts"><view class="primary" :class="{ disabled: !!v.busy }" @click="saveScene">{{ t("v3.saveScene") }}</view></view>
            </template>
          </view>
        </view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import AiBadge from "../../components/AiBadge.vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { api, ApiError, token, type V3Video } from "../../api";
import { errorText, locale, t } from "../../i18n";

defineOptions({ inheritAttrs: false });

const id = ref("");
const v = ref<V3Video | null>(null);
const error = ref("");
const tab = ref("stills");
const say = ref("");
const showScene = ref(false);
const scene = ref("");
const sceneErr = ref("");
let timer: ReturnType<typeof setTimeout> | null = null;

const LIVE = ["queued", "starting", "rendering", "stopping"];
const live = (s?: string) => !!s && LIVE.includes(s);
const pick = (x: { zh: string; en: string } | undefined) => (x ? (locale.value === "en" ? x.en || x.zh : x.zh || x.en) : "");
const stills = computed(() => v.value?.stills || ({ stale: false } as any));
const r = computed(() => (v.value?.renders || {})[tab.value] as any);
const voiceNote = computed(() => {
  const vo = v.value?.voice;
  if (!vo || !vo.on) return "";
  if (v.value?.busy === "voice" || vo.state === "running") return t("v3.voiceRunning");
  if (vo.state === "failed") return t("v3.voiceFailed");
  if (vo.state === "done" && vo.version === v.value?.version) return t(vo.src === "script" ? "v3.voiceScript" : "v3.voiceLabels", { n: vo.n || 0 });
  return t("v3.voicePending");                        // 开着但还没配（AI 没写成、或配好后场景又改了还没重配）
});
// 时间线：标注和旁白按时间排在一起；旁白配好以后写的是实际念的稿，没配之前是解说词原文
const tlRows = computed(() => {
  const tl = v.value?.timeline;
  if (!tl) return [];
  const rows: { at: number; when: string; text: string; kind: string; bottom?: boolean }[] = (tl.labels || []).map((lb) => ({
    at: +lb.t[0], when: fmtSpan(lb.t), text: locale.value === "en" ? lb.en : lb.zh, kind: "label", bottom: lb.bottom }));
  for (const x of tl.voice || []) {
    const text = (locale.value === "en" ? x.en || x.zh : x.zh || x.en) || x.say;   // 解说词原文；念字幕配的只有实际念的稿
    if (!text) continue;
    rows.push({ at: +x.t + 0.001, when: x.dur ? fmtSpan([x.t, +x.t + +x.dur]) : `${(+x.t).toFixed(1)} s`, text, kind: "voice" });
  }
  return rows.sort((a, b) => a.at - b.at);
});
let toggling = false;
const toggleVoice = async () => {
  if (!v.value || v.value.busy || toggling) return;
  toggling = true;
  try { await act(() => api.v3Voice(id.value, !(v.value?.voice && v.value.voice.on))); } finally { toggling = false; }
};
const fmtSpan = (s: any) => (Array.isArray(s) ? `${(+s[0]).toFixed(1)}–${(+s[1]).toFixed(1)} s` : "");

function stageText(x: any) {
  if (x.state === "queued") return t(x.stage === "waiting_machine" ? "v3.waitMachine" : "v3.st.queued");
  if (x.state === "starting") return t("v3.booting");
  if (x.stage === "setup") return t("v3.setup");
  if (x.stage === "encode") return t("v3.encode");
  if (x.total) return t("v3.frames", { d: x.done || 0, n: x.total });
  return t("v3.st." + x.state);
}

async function load() {
  try {
    v.value = await api.v3Get(id.value);
    if (!showScene.value) scene.value = v.value.scene;
    error.value = "";
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  }
  if (timer) clearTimeout(timer);
  const x = v.value;
  if (x && (x.busy || x.stills.state === "running" || Object.values(x.renders || {}).some((q: any) => live(q.state)))) timer = setTimeout(load, 3000);
}

async function act(fn: () => Promise<V3Video>) {
  try {
    v.value = await fn();
    scene.value = v.value.scene;
  } catch (e) {
    uni.showToast({ title: errorText(e instanceof ApiError ? e.code : "unknown"), icon: "none" });
  }
  load();
}

const send = () => { const s = say.value.trim(); if (!s) return; say.value = ""; act(() => api.v3Say(id.value, s)); };
const doStills = () => act(() => api.v3Stills(id.value));
const render = () => act(() => api.v3Render(id.value, tab.value as "draft" | "hd"));
const cancel = () => act(() => api.v3Cancel(id.value, tab.value as "draft" | "hd"));

async function saveScene() {
  sceneErr.value = "";
  try {
    v.value = await api.v3Scene(id.value, scene.value);
  } catch (e: any) {
    sceneErr.value = e instanceof ApiError ? (e.detail || errorText(e.code)) : "unknown";
  }
}

function preview(i: number) {
  const urls = stills.value.urls || [];
  uni.previewImage({ urls, current: urls[i] });
}

function back() {
  uni.reLaunch({ url: "/pages/video3d/video3d" });
}

onLoad((q: any) => { id.value = String(q?.id || ""); });
onShow(() => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t("v3.title") });
  load();
});
onUnmounted(() => { if (timer) clearTimeout(timer); });
</script>

<style scoped>
.wrap { max-width: 1180px; }
.top { display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; margin-bottom: 12px; }
.back { color: var(--wq-link); cursor: pointer; }
.h1 { font-size: 22px; font-weight: 700; color: var(--wq-ink); }
.cols { display: flex; gap: 14px; align-items: flex-start; flex-wrap: wrap; }
.chat { width: 320px; flex: none; display: flex; flex-direction: column; gap: 8px; box-sizing: border-box; }
.main { flex: 1; min-width: 300px; display: flex; flex-direction: column; gap: 12px; }
@media (max-width: 860px) { .chat { width: 100%; } }
.card { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 14px; }
.label { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 6px; font-size: 14px; }
.msgs { max-height: 420px; }
.msg { padding: 8px 10px; border-radius: 8px; margin: 6px 0; line-height: 1.6; font-size: 14px; white-space: pre-wrap; }
.msg.me { background: #eef4f7; margin-left: 24px; }
.msg.ai { background: #f6f5ef; margin-right: 24px; }
.area { border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 10px; height: 72px; width: 100%; box-sizing: border-box; font-size: 14px; }
.code { border: 1px solid var(--wq-line); border-radius: 8px; padding: 8px 10px; height: 360px; width: 100%; box-sizing: border-box; font: 12.5px/1.5 ui-monospace, Menlo, monospace; margin-top: 8px; }
.primary { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 9px 18px; border-radius: 8px; cursor: pointer; white-space: nowrap; text-align: center; }
.disabled { opacity: .5; pointer-events: none; }
.tabs { display: flex; gap: 6px; background: #f1f3f2; border-radius: 8px; padding: 4px; }
.tab { flex: 1; text-align: center; padding: 7px; border-radius: 6px; cursor: pointer; color: var(--wq-muted); }
.tab.on { background: #fff; color: var(--wq-ink); font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.stage { min-height: 220px; }
.stills { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 8px; }
.still { position: relative; }
.img { width: 100%; border-radius: 4px; display: block; cursor: zoom-in; }
.cap { position: absolute; left: 6px; bottom: 6px; background: rgba(0,0,0,.55); color: #fff; font-size: 12px; padding: 1px 6px; border-radius: 4px; }
.video { width: 100%; border-radius: 4px; background: #000; }
.wait { color: var(--wq-muted); padding: 30px 10px; text-align: center; line-height: 1.7; }
.bar { height: 6px; background: #eef1f0; border-radius: 3px; margin: 10px auto 0; max-width: 360px; overflow: hidden; }
.fill { height: 100%; background: var(--wq-accent); }
.acts { display: flex; justify-content: flex-end; align-items: center; gap: 14px; margin-top: 12px; flex-wrap: wrap; }
.acts.left { justify-content: flex-start; }
.stale { color: #7a5a00; font-size: 13px; }
.hint { display: block; color: var(--wq-muted); font-size: 13px; margin-top: 8px; line-height: 1.6; }
.alert { background: #fdecea; color: var(--wq-danger); padding: 10px 14px; border-radius: 8px; margin: 10px 0; white-space: pre-wrap; }
.alert.small { font-size: 13px; padding: 8px 10px; }
.muted { color: var(--wq-muted); font-weight: 400; }
.link { color: var(--wq-link); font-size: 14px; cursor: pointer; display: inline-block; margin-top: 8px; }
.link.danger { color: var(--wq-muted); margin-top: 0; }
.vsw { display: flex; align-items: center; gap: 4px; font-size: 13px; color: var(--wq-ink); cursor: pointer; padding: 2px 4px; flex-wrap: wrap; }
.vsw .box { font-size: 16px; }
.vsw.disabled { opacity: 0.6; cursor: default; }
.vtag { font-size: 11.5px; color: #2b6cb0; background: #ebf4ff; border-radius: 4px; padding: 1px 5px; margin-right: 4px; }
.tl.say .tl-x { color: #2d3748; }
.tl { display: flex; gap: 10px; padding: 5px 0; border-top: 1px solid #f0f1f0; font-size: 13.5px; }
.tl-t { color: var(--wq-muted); font-family: ui-monospace, Menlo, monospace; width: 96px; flex: none; }
.tl-x { color: var(--wq-ink); }
</style>
