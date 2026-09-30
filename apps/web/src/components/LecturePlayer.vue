<template>
  <view class="lp">
    <view class="stage">
      <video :id="vid" :key="src + ':' + gen" class="video" :src="src" :poster="poster || ''" :initial-time="startAt"
        :autoplay="resume" controls preload="metadata" show-fullscreen-btn
        @timeupdate="onTime" @play="playing = true" @pause="playing = false" @ended="playing = false">
        <cover-view v-if="lines.length" class="subs">
          <cover-view v-for="(l, i) in lines" :key="i" class="line" :class="'l-' + l.lang">{{ l.text }}</cover-view>
        </cover-view>
      </video>
    </view>
    <view class="bar">
      <view v-if="dubs.length > 1" class="group">
        <text class="label">{{ t("lecture.voice") }}</text>
        <view v-for="d in dubs" :key="d" class="seg" :class="{ on: dub === d }" @click="setDub(d)">{{ LANG_NAME[d] }}</view>
      </view>
      <view v-if="subModes.length > 1" class="group">
        <text class="label">{{ t("lecture.subs") }}</text>
        <view v-for="s in subModes" :key="s" class="seg" :class="{ on: sub === s }" @click="sub = s">{{ subName(s) }}</view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
// 讲解视频 player (round 4, step 5): Chinese / English voice switched at the same moment (two files, one picture),
// subtitles 中文 / English / 中英 / 关 drawn over the picture (the same way on the web and in the mini program).
import { computed, onMounted, ref, watch } from "vue";
import { absolute } from "../api";
import { locale, t } from "../i18n";

type Lang = "zh" | "en";
interface Cue { start: number; end: number; text: string }
const props = defineProps<{ lecture: { video: Partial<Record<Lang, string>>; subs: Partial<Record<Lang, string>>; poster?: string } }>();

const LANG_NAME: Record<Lang, string> = { zh: "中文", en: "English" };
const vid = "lp" + Math.random().toString(36).slice(2, 8);
const dubs = computed(() => (["zh", "en"] as Lang[]).filter((x) => props.lecture.video[x]));
const subLangs = computed(() => (["zh", "en"] as Lang[]).filter((x) => props.lecture.subs[x]));
const subModes = computed(() => {
  const s: string[] = [...subLangs.value];
  if (s.length === 2) s.push("both");
  if (s.length) s.push("off");
  return s;
});
const dub = ref<Lang>(locale.value === "en" && props.lecture.video.en ? "en" : props.lecture.video.zh ? "zh" : "en");
const sub = ref<string>(subLangs.value.length === 2 ? "both" : subLangs.value[0] || "off");
const src = computed(() => absolute(props.lecture.video[dub.value] || ""));
const poster = computed(() => absolute(props.lecture.poster || ""));
const now = ref(0);
const startAt = ref(0);
const resume = ref(false);
const playing = ref(false);
const gen = ref(0);
const cues = ref<Record<Lang, Cue[]>>({ zh: [], en: [] });

function subName(s: string) {
  return s === "both" ? t("lecture.both") : s === "off" ? t("lecture.off") : s === "zh" ? "中文" : "EN";
}

function setDub(d: Lang) {
  if (d === dub.value) return;
  startAt.value = Math.max(0, now.value - 0.2);   // go on from the same moment
  resume.value = playing.value;
  dub.value = d;
  gen.value += 1;
}

function onTime(e: any) {
  now.value = e.detail?.currentTime || 0;
}

function active(list: Cue[], at: number): Cue | null {
  let hit: Cue | null = null;
  for (const c of list) {
    if (c.start > at) break;
    if (at <= c.end) hit = c;
  }
  return hit;
}

const lines = computed(() => {
  const want: Lang[] = sub.value === "both" ? ["zh", "en"] : sub.value === "zh" || sub.value === "en" ? [sub.value as Lang] : [];
  const out: { lang: Lang; text: string }[] = [];
  for (const l of want) {
    const c = active(cues.value[l], now.value);
    if (c) out.push({ lang: l, text: c.text });
  }
  return out;
});

function parse(text: string): Cue[] {
  const out: Cue[] = [];
  const secs = (h: string, m: string, s: string) => Number(h) * 3600 + Number(m) * 60 + Number(s);
  for (const block of text.replace(/\r/g, "").split(/\n\s*\n/)) {
    const m = block.match(/(\d+):(\d{2}):(\d{2}\.\d+)\s*-->\s*(\d+):(\d{2}):(\d{2}\.\d+)[^\n]*\n([\s\S]+)/);
    if (m) out.push({ start: secs(m[1], m[2], m[3]), end: secs(m[4], m[5], m[6]), text: m[7].trim() });
  }
  return out.sort((a, b) => a.start - b.start);
}

function loadSubs() {
  for (const l of subLangs.value) {
    const url = absolute(props.lecture.subs[l] || "");
    uni.request({
      url, method: "GET", dataType: "text", responseType: "text",
      success: (r) => { if (r.statusCode === 200 && typeof r.data === "string") cues.value = { ...cues.value, [l]: parse(r.data) }; },
    });
  }
}

onMounted(loadSubs);
watch(() => props.lecture, () => { cues.value = { zh: [], en: [] }; startAt.value = 0; resume.value = false; loadSubs(); });
</script>

<style scoped>
.lp { width: 100%; }
.stage { position: relative; width: 100%; background: #000; border-radius: 8px; overflow: hidden; }
.video { width: 100%; height: 56.25vw; max-height: 540px; display: block; }
/* #ifdef H5 */
.video { height: auto; aspect-ratio: 16 / 9; max-height: none; }
/* #endif */
.subs { position: absolute; left: 0; right: 0; bottom: 44px; display: flex; flex-direction: column; align-items: center; pointer-events: none; }
.line { max-width: 90%; margin-top: 3px; padding: 2px 10px; border-radius: 4px; background: rgba(0, 0, 0, 0.62); color: #fff;
  font-size: 17px; line-height: 1.45; text-align: center; white-space: normal; }
.l-en { font-size: 14px; color: #e6edf7; }
.bar { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 10px; align-items: center; }
.group { display: flex; align-items: center; gap: 4px; }
.label { font-size: 13px; color: #5b6b7b; margin-right: 4px; }
.seg { font-size: 13px; padding: 4px 10px; border: 1px solid #c9d3dd; border-radius: 14px; color: #2d3b45; cursor: pointer; }
.seg.on { background: #2d3b45; border-color: #2d3b45; color: #fff; }
</style>
