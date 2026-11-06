<template>
  <!-- 第 102 轮：三维视频旁白选声音（点一下就试听）、调语速三档；视频页和网页版缝纫机设计软件共用 -->
  <view v-if="list.length" class="vp">
    <view class="row">
      <text class="lab">{{ t("v3.voiceName") }}</text>
      <text v-for="v in list" :key="v.id" class="pick" :class="{ on: cur.voice === v.id }" @click="pickVoice(v)">{{ locale === "en" ? v.en : v.zh }}</text>
    </view>
    <view class="row">
      <text class="lab">{{ t("v3.voiceSpeed") }}</text>
      <text v-for="s in speeds" :key="s.v" class="pick" :class="{ on: cur.speed === s.v }" @click="pickSpeed(s.v)">{{ locale === "en" ? s.en : s.zh }}</text>
      <text class="muted">{{ t("v3.voiceTry") }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { api, request, type Voice } from "../../api";
import { locale, t } from "../../i18n";

// src="sewing"：网页版缝纫机设计软件用缝纫机那边的列表（开通了缝纫机软件就能取，不要求三维视频权限）
const props = defineProps<{ lang: string; modelValue: { voice: string; speed: number }; src?: string }>();
const emit = defineEmits<{ (e: "update:modelValue", v: { voice: string; speed: number }): void }>();
const all = ref<Voice[]>([]);
const speeds = ref<{ v: number; zh: string; en: string }[]>([]);
const defaults = ref<{ zh?: string; en?: string; speed?: number }>({});
// 中文、中英两行念中文：列中文声音；只出英文：列英文声音
const key = computed(() => (props.lang === "en" ? "en" : "zh"));
const list = computed(() => all.value.filter((v) => v.lang === key.value));
const cur = computed(() => ({
  voice: props.modelValue.voice || (defaults.value as any)[key.value] || "",
  speed: props.modelValue.speed || defaults.value.speed || 1.1,
}));

onMounted(async () => {
  try {
    const r: any = props.src === "sewing" ? await request("GET", "/api/v1/sewing/video/voices") : await api.v3Voices();
    if (r.available) { all.value = r.voices; speeds.value = r.speeds; defaults.value = r.default; }
  } catch { /* 没有语音服务：不显示 */ }
});

let audio: any = null;
function pickVoice(v: Voice) {
  emit("update:modelValue", { voice: v.id, speed: cur.value.speed });
  try { audio?.pause(); audio = new Audio(v.sample); audio.play(); } catch { /* 放不出声：不要紧 */ }
}
function pickSpeed(s: number) { emit("update:modelValue", { voice: cur.value.voice, speed: s }); }
</script>

<style scoped>
.vp { display: flex; flex-direction: column; gap: 6px; margin: 6px 0; }
.row { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.lab { font-size: 13px; color: var(--wq-muted); min-width: 34px; }
.pick { font-size: 12.5px; padding: 3px 9px; border: 1px solid var(--wq-line); border-radius: 12px; cursor: pointer; color: var(--wq-ink); background: #fff; }
.pick.on { border-color: #2b6cb0; background: #ebf4ff; color: #2b6cb0; }
.muted { font-size: 12px; color: var(--wq-muted); }
</style>
