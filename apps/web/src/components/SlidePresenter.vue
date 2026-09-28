<template>
  <view class="sp">
    <!-- converting / failed / unavailable -->
    <view v-if="!deck || deck.status !== 'ready'" class="state">
      <template v-if="!deck || deck.status === 'converting' || deck.status === 'missing'">
        <view class="spinner" />
        <text class="st-title">{{ deck && deck.queue ? t("slides.queued", { n: deck.queue }) : t("slides.converting") }}</text>
        <text class="st-sub">{{ deck && deck.elapsed ? t("slides.elapsed", { s: deck.elapsed }) : t("slides.convertingHint") }}</text>
        <view v-if="waited > 180 && deck" class="st-btns">
          <text class="st-sub">{{ t("slides.slow") }}</text>
          <view class="btn" @click="retryConvert">{{ t("common.retry") }}</view>
          <view v-if="deck.download_url" class="btn ghost" @click="download">{{ t("activity.download") }}</view>
        </view>
      </template>
      <template v-else>
        <text class="st-title">{{ deck.status === "failed" ? t("slides.failed") : t("slides.unavailable") }}</text>
        <view class="st-btns">
          <view v-if="deck.status === 'failed'" class="btn" @click="retryConvert">{{ t("common.retry") }}</view>
          <view v-if="deck.download_url" class="btn ghost" @click="download">{{ t("activity.download") }}</view>
        </view>
      </template>
      <text v-if="error" class="err">{{ errorText(error) }}</text>
    </view>

    <!-- #ifdef H5 -->
    <view v-else ref="root" class="pres" :class="{ fs: isFs }">
      <view class="bar">
        <view v-if="lab" class="seg">
          <text class="seg-i" :class="{ on: pane === 'slides' }" @click="pane = 'slides'">{{ t("slides.slides") }}</text>
          <text class="seg-i" :class="{ on: pane === 'lab' }" @click="openLab()">{{ t("slides.lab") }}</text>
        </view>
        <text v-if="pane === 'slides'" class="count">{{ i + 1 }} / {{ total }}</text>
        <text v-else class="count">{{ lab && lab.name }}</text>
        <view class="grow" />
        <template v-if="pane === 'slides'">
          <view v-for="r in goRefs" :key="r" class="go-lab" @click="openLab(r)">⚗ {{ t("slides.goLab", { n: r }) }}</view>
          <view class="tool" :class="{ on: showThumbs }" @click="showThumbs = !showThumbs">▦ <text class="tl">{{ t("slides.thumbs") }}</text></view>
          <view v-if="deck.teacher" class="tool" :class="{ on: showNotes }" @click="showNotes = !showNotes">✎ <text class="tl">{{ t("slides.notes") }}</text></view>
        </template>
        <view v-else class="tool" @click="pane = 'slides'">‹ <text class="tl">{{ t("slides.backToSlides", { n: i + 1 }) }}</text></view>
        <view class="tool" @click="toggleFs">{{ isFs ? "⤡" : "⛶" }} <text class="tl">{{ isFs ? t("slides.exitFull") : t("viewer.fullscreen") }}</text></view>
      </view>

      <view class="panes">
        <!-- slides -->
        <view class="pane slides-pane" :class="{ active: pane === 'slides' }">
          <view class="stage-wrap">
            <div class="stage" :style="{ aspectRatio: ratio }" @click="onStageClick" @touchstart.passive="onTouchStart" @touchend="onTouchEnd">
              <img class="slide-img" :src="slide.image" :alt="`${i + 1}`" draggable="false" />
              <div v-for="(v, vi) in slide.videos" :key="'v' + i + '-' + vi" class="hot video" :style="box(v)" @click.stop>
                <video v-if="playing === vi" class="vid" :src="v.src" autoplay controls playsinline />
                <div v-else class="play" @click.stop="playing = vi"><span>▶</span></div>
              </div>
              <div v-for="(l, li) in slide.links" :key="'l' + i + '-' + li" class="hot link" :style="box(l)"
                   :title="l.lab ? t('slides.goLab', { n: l.lab }) : l.href" @click.stop="follow(l)" />
              <div class="nav prev" :class="{ off: i === 0 }" @click.stop="go(i - 1)">‹</div>
              <div class="nav next" :class="{ off: i >= total - 1 }" @click.stop="go(i + 1)">›</div>
            </div>
          </view>
          <view v-if="showNotes && deck.teacher" class="notes">
            <text class="notes-h">{{ t("slides.notes") }} · {{ i + 1 }}</text>
            <text class="notes-b">{{ slide.notes || t("slides.noNotes") }}</text>
          </view>
          <view v-if="showThumbs" class="thumbs">
            <div v-for="(s, si) in deck.slides" :key="si" :ref="(el) => (si === i ? (activeThumb = el) : null)"
                 class="thumb" :class="{ on: si === i }" @click="go(si)">
              <img :src="s.thumb" loading="lazy" />
              <span class="tn">{{ si + 1 }}</span>
              <span v-if="s.labs.length" class="tlab">⚗</span>
            </div>
          </view>
        </view>

        <!-- lab: loaded together with the slides, so switching is instant and keeps its state -->
        <view v-if="lab" class="pane lab-pane" :class="{ active: pane === 'lab' }">
          <iframe v-if="labUrl" ref="frame" class="lab" :src="labUrl" :title="lab.name"
                  sandbox="allow-scripts allow-popups allow-forms allow-modals allow-downloads" allow="fullscreen" @load="onLabLoad" />
          <view v-else class="state small"><view class="spinner" /></view>
        </view>
      </view>

      <view v-if="!isFs" class="foot">
        <text class="hint keys">{{ t("slides.keys") }}</text>
        <text class="hint swipe">{{ t("slides.swipe") }}</text>
        <view class="grow" />
        <view v-if="deck.teacher" class="allow" @click="toggleAllow">
          <text class="sw" :class="{ on: deck.allow_download }" />
          <text>{{ t("slides.allowDownload") }}</text>
        </view>
        <view v-if="deck.download_url" class="tool plain" @click="download">⤓ {{ t("activity.download") }}</view>
      </view>
    </view>
    <!-- #endif -->

    <!-- #ifndef H5 -->
    <view v-else class="mp-list">
      <view v-for="(s, si) in deck.slides" :key="si" class="mp-slide">
        <image class="mp-img" :src="s.image" mode="widthFix" />
        <text class="mp-n">{{ si + 1 }} / {{ total }}</text>
      </view>
    </view>
    <!-- #endif -->
  </view>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { absolute, api, ApiError, type Slide, type SlideBox, type SlideDeck } from "../api";
import { errorText, t } from "../i18n";

/** A lab module of the same unit, which the "virtual lab" side of the presenter runs. */
export interface LabRef { id: number; name: string }

const props = defineProps<{ cmid: number; labs: LabRef[] }>();

const deck = ref<SlideDeck | null>(null);
const error = ref("");
const i = ref(0);
const pane = ref<"slides" | "lab">("slides");
const showThumbs = ref(false);
const showNotes = ref(false);
const playing = ref<number | null>(null);
const isFs = ref(false);
const root = ref<any>(null);
const frame = ref<HTMLIFrameElement | null>(null);
const activeThumb = ref<any>(null);
const labUrl = ref("");
const labReady = ref(false);
const pendingLab = ref("");
const chosenLab = ref<LabRef | null>(null);
let timer: ReturnType<typeof setTimeout> | null = null;
const openedAt = Date.now();
const waited = ref(0);  // seconds since the page asked for this deck

const total = computed(() => deck.value?.slides?.length || 0);
const slide = computed<Slide>(() => deck.value?.slides?.[i.value] || { image: "", thumb: "", labs: [], videos: [], links: [] });
const ratio = computed(() => `${deck.value?.width || 16} / ${deck.value?.height || 9}`);
const lab = computed<LabRef | null>(() => chosenLab.value || props.labs[0] || null);
// "去做实验 1.3": only when this unit has a lab to go to.
const goRefs = computed(() => (props.labs.length ? slide.value.labs : []));
const storeKey = computed(() => `wq-slide-${props.cmid}`);

const box = (b: SlideBox) => ({ left: b.x * 100 + "%", top: b.y * 100 + "%", width: b.w * 100 + "%", height: b.h * 100 + "%" });

function go(n: number) {
  if (!total.value) return;
  const next = Math.max(0, Math.min(total.value - 1, n));
  if (next === i.value) return;
  i.value = next;
}
watch(i, (n) => {
  playing.value = null;
  try { localStorage.setItem(storeKey.value, String(n)); } catch { /* private mode */ }
  preload(n);
  setTimeout(() => (activeThumb.value as HTMLElement | null)?.scrollIntoView?.({ block: "nearest", inline: "center" }), 0);
});

function preload(n: number) {
  // #ifdef H5
  for (const k of [n + 1, n + 2, n - 1]) {
    const s = deck.value?.slides?.[k];
    if (s) new Image().src = s.image;
  }
  // #endif
}

function onStageClick(e: MouseEvent) {
  // Click the left fifth to go back, anywhere else to go forward (like a projector remote).
  const el = e.currentTarget as HTMLElement;
  const x = (e.clientX - el.getBoundingClientRect().left) / el.clientWidth;
  go(x < 0.2 ? i.value - 1 : i.value + 1);
}

// Phones: swipe left / right to turn pages.
let touchX = 0;
let touchY = 0;
function onTouchStart(e: TouchEvent) {
  touchX = e.touches[0].clientX;
  touchY = e.touches[0].clientY;
}
function onTouchEnd(e: TouchEvent) {
  const dx = e.changedTouches[0].clientX - touchX;
  const dy = e.changedTouches[0].clientY - touchY;
  if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
    e.preventDefault();  // a swipe is not also a tap
    go(dx < 0 ? i.value + 1 : i.value - 1);
  }
}

function follow(l: { href: string; lab?: string }) {
  if (l.lab && props.labs.length) return openLab(l.lab);
  if (l.href) window.open(l.href, "_blank", "noopener");
}

// --- the lab side ----------------------------------------------------------------------------
function pickLab(ref?: string): LabRef | null {
  if (!props.labs.length) return null;
  if (ref) {
    const hit = props.labs.find((m) => (m.name || "").replace(/\s/g, "").includes(ref));
    if (hit) return hit;
  }
  return chosenLab.value || props.labs[0];
}

async function loadLab(target: LabRef) {
  if (chosenLab.value?.id === target.id && labUrl.value) return;
  chosenLab.value = target;
  labReady.value = false;
  labUrl.value = "";
  try {
    const a = await api.activity(target.id);
    const f = (a.files || []).find((x) => x.kind === "lab");
    labUrl.value = f?.lab_url ? absolute(f.lab_url) : "";
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  }
}

async function openLab(ref?: string) {
  const target = pickLab(ref);
  if (!target) return;
  pane.value = "lab";
  if (ref) pendingLab.value = ref;
  await loadLab(target);
  sendPending();
}

function onLabLoad() {
  labReady.value = true;
  sendPending();
}

function sendPending() {
  if (!pendingLab.value || !labReady.value || !frame.value?.contentWindow) return;
  // The lab switches experiments in place (WenQuest lab protocol), keeping what the student set.
  frame.value.contentWindow.postMessage({ type: "wq-lab", lab: pendingLab.value }, "*");
  pendingLab.value = "";
}

// --- keyboard and fullscreen ---------------------------------------------------------------------
function onKey(e: KeyboardEvent) {
  if (pane.value !== "slides" || !deck.value || deck.value.status !== "ready") return;
  const tag = (e.target as HTMLElement)?.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
  if (["ArrowRight", "PageDown", " ", "Enter"].includes(e.key)) go(i.value + 1);
  else if (["ArrowLeft", "PageUp", "Backspace"].includes(e.key)) go(i.value - 1);
  else if (e.key === "Home") go(0);
  else if (e.key === "End") go(total.value - 1);
  else if (e.key === "f" || e.key === "F") toggleFs();
  else return;
  e.preventDefault();
}

function toggleFs() {
  // #ifdef H5
  const el = (root.value?.$el || root.value) as HTMLElement | null;
  if (document.fullscreenElement) document.exitFullscreen?.();
  else el?.requestFullscreen?.();
  // #endif
}
const onFsChange = () => { isFs.value = !!document.fullscreenElement; };

// --- loading ------------------------------------------------------------------------------------
async function load(force = false) {
  if (timer) clearTimeout(timer);
  try {
    const d = force ? await api.slidesRetry(props.cmid) : await api.slides(props.cmid);
    d.slides = (d.slides || []).map((s) => ({
      ...s, image: absolute(s.image), thumb: absolute(s.thumb),
      videos: s.videos.map((v) => ({ ...v, src: absolute(v.src) })),
    }));
    d.download_url = d.download_url ? absolute(d.download_url) : null;
    deck.value = d;
    error.value = "";
    if (d.status === "ready") {
      let saved = 0;
      try { saved = Number(localStorage.getItem(storeKey.value) || 0); } catch { /* ignore */ }
      i.value = Math.min(Math.max(0, saved), (d.slides?.length || 1) - 1);
      preload(i.value);
    } else if (d.status === "converting" || d.status === "missing") {
      waited.value = Math.round((Date.now() - openedAt) / 1000);
      timer = setTimeout(() => load(), 2000);
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
    timer = setTimeout(() => load(), 5000);
  }
}
const retryConvert = () => load(true);

async function toggleAllow() {
  if (!deck.value) return;
  try {
    const r = await api.slideSettings(props.cmid, !deck.value.allow_download);
    deck.value.allow_download = r.allow_download;
  } catch (e) {
    error.value = e instanceof ApiError ? e.code : "unknown";
  }
}

function download() {
  if (!deck.value?.download_url) return;
  // #ifdef H5
  const a = document.createElement("a");
  a.href = deck.value.download_url;
  a.download = deck.value.file_name;
  a.click();
  // #endif
}

// Load the lab alongside the slides, so the first switch is already instant.
watch(() => props.labs, (labs) => { if (labs.length && !labUrl.value) loadLab(labs[0]); }, { immediate: true });

onMounted(() => {
  load();
  // #ifdef H5
  window.addEventListener("keydown", onKey);
  document.addEventListener("fullscreenchange", onFsChange);
  // #endif
});
onBeforeUnmount(() => {
  if (timer) clearTimeout(timer);
  // #ifdef H5
  window.removeEventListener("keydown", onKey);
  document.removeEventListener("fullscreenchange", onFsChange);
  // #endif
});
</script>

<style scoped>
.sp { width: 100%; }
.state { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 48px 20px; display: flex; flex-direction: column; align-items: center; gap: 10px; text-align: center; }
.state.small { border: 0; padding: 80px 0; background: transparent; }
.st-title { font-size: 17px; color: var(--wq-ink); font-weight: 600; }
.st-sub { font-size: 13px; color: var(--wq-muted); }
.st-btns { display: flex; gap: 10px; margin-top: 8px; align-items: center; flex-wrap: wrap; justify-content: center; }
.err { color: var(--wq-danger); font-size: 13px; }
.btn { padding: 8px 16px; border-radius: 8px; background: var(--wq-ink); color: #fff; cursor: pointer; font-size: 14px; }
.btn.ghost { background: #fff; color: var(--wq-ink); border: 1px solid var(--wq-line); }
.spinner { width: 28px; height: 28px; border-radius: 50%; border: 3px solid #e3e8e6; border-top-color: var(--wq-accent); animation: spin .9s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.pres { background: #0d1a20; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; }
.pres.fs { border-radius: 0; height: 100vh; }
.bar { display: flex; align-items: center; gap: 8px; padding: 8px 10px; background: #0a141a; color: #c9d4d8; flex-wrap: wrap; }
.seg { display: flex; background: #16262e; border-radius: 8px; padding: 3px; }
.seg-i { padding: 5px 14px; border-radius: 6px; cursor: pointer; font-size: 14px; color: #c9d4d8; }
.seg-i.on { background: #fff; color: var(--wq-ink); font-weight: 600; }
.count { font-family: "IBM Plex Mono", Menlo, monospace; font-size: 13px; color: #8fa3ab; padding: 0 6px; }
.grow { flex: 1; }
.go-lab { background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; font-size: 14px; padding: 6px 12px; border-radius: 8px; cursor: pointer; }
.tool { font-size: 13px; padding: 6px 10px; border-radius: 8px; cursor: pointer; color: #c9d4d8; border: 1px solid rgba(255,255,255,.12); }
.tool:hover, .tool.on { background: rgba(255,255,255,.1); color: #fff; }

.panes { position: relative; flex: 1; min-height: 0; }
/* The inactive pane stays laid out (hidden, same size), so the lab keeps running and its canvas keeps its size. */
.pane { position: absolute; inset: 0; visibility: hidden; pointer-events: none; }
.pane.active { position: relative; visibility: visible; pointer-events: auto; }
.pres.fs .pane.active { height: 100%; }

.stage-wrap { display: flex; justify-content: center; background: #0d1a20; }
.stage { position: relative; width: 100%; max-height: calc(100vh - 220px); max-width: calc((100vh - 220px) * 16 / 9); cursor: pointer; user-select: none; }
.pres.fs .stage-wrap { height: 100%; align-items: center; }
.pres.fs .stage { max-height: calc(100vh - 52px); max-width: calc((100vh - 52px) * 16 / 9); }
.slide-img { width: 100%; height: 100%; display: block; object-fit: contain; background: #fff; }
.hot { position: absolute; }
.hot.link { cursor: pointer; border-radius: 6px; }
.hot.link:hover { box-shadow: 0 0 0 3px rgba(242,183,5,.8); background: rgba(242,183,5,.08); }
.hot.video { cursor: default; }
.vid { width: 100%; height: 100%; display: block; background: #000; }
.play { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.play span { width: 64px; height: 64px; border-radius: 50%; background: rgba(13,26,32,.72); color: #fff; font-size: 26px; display: flex; align-items: center; justify-content: center; padding-left: 5px; box-sizing: border-box; box-shadow: 0 0 0 3px rgba(255,255,255,.5); }
.play:hover span { background: var(--wq-accent); color: var(--wq-ink); }
.nav { position: absolute; top: 50%; transform: translateY(-50%); width: 44px; height: 64px; display: flex; align-items: center; justify-content: center; font-size: 34px; color: #fff; background: rgba(13,26,32,.35); opacity: 0; transition: opacity .15s; cursor: pointer; border-radius: 6px; }
.nav.prev { left: 6px; }
.nav.next { right: 6px; }
.stage:hover .nav { opacity: 1; }
.nav.off { display: none; }

.notes { background: #fffbea; padding: 12px 16px; border-top: 1px solid #f0e2a6; }
.notes-h { display: block; font-size: 12px; color: #7a5a00; margin-bottom: 4px; }
.notes-b { display: block; white-space: pre-wrap; color: var(--wq-ink); line-height: 1.7; font-size: 14px; }
.thumbs { display: flex; gap: 8px; overflow-x: auto; padding: 10px; background: #0a141a; }
.thumb { position: relative; flex: 0 0 132px; border: 2px solid transparent; border-radius: 4px; cursor: pointer; background: #fff; }
.thumb.on { border-color: var(--wq-accent); }
.thumb img { width: 100%; display: block; border-radius: 2px; }
.tn { position: absolute; left: 4px; bottom: 3px; font-size: 11px; background: rgba(13,26,32,.75); color: #fff; padding: 0 5px; border-radius: 3px; }
.tlab { position: absolute; right: 4px; top: 3px; font-size: 12px; background: var(--wq-accent); color: var(--wq-ink); padding: 0 4px; border-radius: 3px; }

.lab-pane { background: #fff; }
.lab { width: 100%; height: calc(100vh - 220px); min-height: 520px; border: 0; display: block; background: #fff; }
.pres.fs .lab { height: 100%; min-height: 0; }

.foot { display: flex; align-items: center; gap: 12px; padding: 8px 12px; background: #fff; border-top: 1px solid var(--wq-line); flex-wrap: wrap; }
.hint { font-size: 12px; color: var(--wq-muted); }
.hint.swipe { display: none; }
.allow { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--wq-text); cursor: pointer; }
.sw { width: 30px; height: 16px; border-radius: 8px; background: #cfd8d6; position: relative; }
.sw::after { content: ""; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 50%; background: #fff; transition: left .15s; }
.sw.on { background: var(--wq-link); }
.sw.on::after { left: 16px; }
.tool.plain { color: var(--wq-ink); border-color: var(--wq-line); }
.tool.plain:hover { background: var(--wq-bg); color: var(--wq-ink); }

.mp-list { display: flex; flex-direction: column; gap: 12px; }
.mp-slide { background: #fff; border-radius: 6px; overflow: hidden; }
.mp-img { width: 100%; display: block; }
.mp-n { display: block; font-size: 12px; color: var(--wq-muted); padding: 4px 8px; }
@media (max-width: 860px) { .hint.keys { display: none; } .hint.swipe { display: inline; } .tl { display: none; } .stage { max-height: none; max-width: none; } .lab { height: 70vh; } }
</style>
