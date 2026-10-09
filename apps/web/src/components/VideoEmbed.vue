<template>
  <!-- 讲课视频（第 25 轮）：B 站 / YouTube 的视频在页里播放。中文界面先放 B 站版，英文界面先放 YouTube 版，可切换。 -->
  <view v-if="list.length" class="vembed">
    <view v-if="list.length > 1" class="vtabs">
      <view v-for="(m, i) in list" :key="m.id" class="vtab" :class="{ on: i === cur }" @click="pick(i)">{{ label(m) }}</view>
    </view>
    <view class="frame">
      <!-- #ifdef H5 -->
      <iframe v-if="playing" :key="src" class="player" :src="src" :title="list[cur].name"
        allow="autoplay; fullscreen; encrypted-media; picture-in-picture" allowfullscreen referrerpolicy="strict-origin-when-cross-origin" />
      <view v-else class="poster" @click="play">
        <view class="big">▶</view>
        <text class="ptitle">{{ list[cur].name }}</text>
        <text class="psub">{{ t("video.from", { p: provider(list[cur]) }) }}</text>
      </view>
      <!-- #endif -->
      <!-- #ifndef H5 -->
      <view class="poster" @click="openOut"><view class="big">▶</view><text class="ptitle">{{ list[cur].name }}</text></view>
      <!-- #endif -->
    </view>
    <view class="vbar">
      <text class="small muted">{{ t("video.note") }}</text>
      <text class="out" @click="openOut">{{ t("video.openOn", { p: provider(list[cur]) }) }} ↗</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { api, type Module } from "../api";
import { locale, t } from "../i18n";

const props = defineProps<{ modules: Module[] }>();
const emit = defineEmits<{ (e: "viewed", id: number): void }>();

const list = computed(() => props.modules.filter((m) => m.video));
const cur = ref(0);
const playing = ref(false);
const src = computed(() => list.value[cur.value]?.video?.embed || "");

// Chinese interface: the B 站 version first; English: YouTube first.
function preferred() {
  const want = locale.value === "en" ? "youtube" : "bilibili";
  const i = list.value.findIndex((m) => m.video?.provider === want);
  return i >= 0 ? i : 0;
}
watch(() => list.value.map((m) => m.id).join(",") + locale.value, () => { cur.value = preferred(); playing.value = false; }, { immediate: true });

const provider = (m: Module) => (m.video?.provider === "youtube" ? "YouTube" : t("video.bilibili"));
function label(m: Module) {
  return m.video?.provider === "youtube" ? "YouTube" : t("video.bilibili");   // 两个平台的版本不一定分中英文
}
function pick(i: number) {
  cur.value = i;
  playing.value = false;
}
async function play() {
  playing.value = true;
  const m = list.value[cur.value];
  try { await api.activity(m.id); emit("viewed", m.id); } catch { /* playing never waits for the progress record */ }
}
function openOut() {
  const url = list.value[cur.value]?.video?.page || "";
  // #ifdef H5
  window.open(url, "_blank", "noopener");
  // #endif
  // #ifndef H5
  uni.setClipboardData({ data: url });
  // #endif
}
</script>

<style scoped>
.vembed { margin-top: 8px; }
.vtabs { display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
.vtab { padding: 6px 14px; border: 1px solid var(--wq-line); border-radius: 999px; cursor: pointer; font-size: 14px; }
.vtab.on { background: #1d4e75; color: #fff; border-color: #1d4e75; }
.frame { position: relative; width: 100%; aspect-ratio: 16 / 9; background: #0b1220; border-radius: 8px; overflow: hidden; }
.player { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
.poster { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
  cursor: pointer; color: #fff; background: radial-gradient(circle at 50% 40%, #1d3a5a, #0b1220 70%); padding: 16px; text-align: center; }
.big { width: 76px; height: 76px; border-radius: 50%; background: #f2b705; color: #0b1220; font-size: 32px; display: flex; align-items: center; justify-content: center; padding-left: 6px; }
.ptitle { font-size: 18px; font-weight: 600; }
.psub { font-size: 13px; opacity: .75; }
.vbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin: 8px 0; flex-wrap: wrap; }
.out { color: #1d6fa5; cursor: pointer; font-size: 14px; }
</style>
