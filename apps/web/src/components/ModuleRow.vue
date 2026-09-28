<template>
  <view class="row" :class="{ locked: m.locked }" @click="open">
    <view class="icon" :class="'k-' + kind">{{ KIND_ICON[kind] || "•" }}</view>
    <view class="text">
      <text class="name">{{ m.name }}</text>
      <text class="sub">{{ t("kind." + kind) }}<text v-if="m.file && m.file.size"> · {{ size(m.file.size) }}</text></text>
    </view>
    <text v-if="m.hidden" class="tag teacher">{{ t("course.teacherOnly") }}</text>
    <text v-if="m.locked" class="tag">{{ t("course.locked") }}</text>
    <text v-else-if="m.completed" class="tag done">✓ {{ t("course.done") }}</text>
    <text class="chev">›</text>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Module } from "../api";
import { t } from "../i18n";
import { KIND_ICON, moduleKind } from "../store";

const props = defineProps<{ m: Module; courseId: number }>();
const kind = computed(() => moduleKind(props.m));

function open() {
  if (props.m.locked) return;
  uni.navigateTo({ url: `/pages/activity/activity?id=${props.m.id}&course=${props.courseId}` });
}
const size = (n: number) => (n > 1048576 ? `${(n / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`);
</script>

<style scoped>
.row { display: flex; align-items: center; gap: 12px; padding: 10px 14px; cursor: pointer; background: #fff; }
.row:hover { background: #f1f6f8; }
.row.locked { cursor: default; opacity: .6; }
.icon { width: 30px; height: 30px; border-radius: 7px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; background: #e8eef0; color: var(--wq-ink); }
.k-reading { background: #e5eef7; color: #1f5f8b; }
.k-video { background: #fde9e4; color: #b3261e; }
.k-slides, .k-pdf { background: #fff3d6; color: #7a5a00; }
.k-lab { background: #e2f3ea; color: #2e7d5b; }
.k-assign { background: #ece8f6; color: #5b4b8a; }
.text { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.name { color: var(--wq-ink); font-size: 15px; line-height: 1.4; }
.sub { color: var(--wq-muted); font-size: 12px; }
.tag { font-size: 12px; padding: 1px 8px; border-radius: 999px; background: #eef1f0; color: var(--wq-muted); white-space: nowrap; }
.tag.done { background: #dcefe5; color: var(--wq-ok); }
.tag.teacher { background: #fff3d6; color: #7a5a00; }
.chev { color: var(--wq-muted); font-size: 18px; }
</style>
