<template>
  <view class="wq-card gpu">
    <view class="wq-row g-head">
      <text class="b grow">{{ t("gpu.title") }}</text>
      <text class="wq-muted small">{{ t("gpu.hint") }}</text>
    </view>
    <view class="wq-row">
      <text>{{ t("gpu.perStudent") }}</text>
      <input class="wq-input hours" type="digit" v-model="hours" />
      <text>{{ t("gpu.hours") }}</text>
      <view class="wq-btn primary" :class="{ disabled: busy }" @click="save">{{ t("common.save") }}</view>
      <text v-if="msg" class="small" :class="ok ? 'ok' : 'wq-error'">{{ msg }}</text>
    </view>
    <view v-if="students.length" class="tbl">
      <view class="wq-row th"><text class="c1">{{ t("gpu.student") }}</text><text class="c2">{{ t("gpu.used") }}</text><text class="c2">{{ t("gpu.sessions") }}</text><text class="c2">{{ t("gpu.cost") }}</text></view>
      <view v-for="s in students" :key="s.user_id" class="wq-row tr">
        <text class="c1">{{ s.name }}</text><text class="c2">{{ s.hours }}</text><text class="c2">{{ s.sessions }}</text><text class="c2">{{ s.cost }}</text>
      </view>
    </view>
    <text v-else class="wq-muted small block">{{ t("gpu.noUse") }}</text>
  </view>
</template>

<script setup lang="ts">
// 云端 GPU 实验（《人工智能》第 14 轮附）：老师给本课程每名学生的 GPU 小时额度，并看用量与费用。
import { onMounted, ref } from "vue";
import { courseApi, type GpuUsage } from "../../courseApi";
import { t } from "../../i18n";

const props = defineProps<{ courseId: number }>();
const hours = ref("0");
const students = ref<GpuUsage["students"]>([]);
const busy = ref(false);
const msg = ref("");
const ok = ref(false);

async function load() {
  try {
    const u = await courseApi.gpuUsage(props.courseId);
    hours.value = String(u.grant_hours);
    students.value = u.students;
  } catch { /* not a teacher, or GPU labs not set up: the card stays quiet */ }
}

async function save() {
  const h = Number(hours.value);
  if (!(h >= 0 && h <= 1000)) { ok.value = false; msg.value = t("gpu.bad"); return; }
  busy.value = true;
  try {
    await courseApi.gpuGrant(props.courseId, h);
    ok.value = true; msg.value = t("gpu.saved");
  } catch (e: any) {
    ok.value = false; msg.value = String(e?.message || e);
  }
  busy.value = false;
}

onMounted(load);
</script>

<style scoped>
.gpu { margin: 0 0 16px; }
.g-head { margin-bottom: 8px; gap: 10px; }
.hours { width: 80px; margin: 0 6px; }
.tbl { margin-top: 10px; font-size: 14px; }
.th { font-weight: 600; border-bottom: 1px solid #d9dee2; padding: 4px 0; }
.tr { border-bottom: 1px solid #eef0f2; padding: 4px 0; }
.c1 { flex: 2; } .c2 { flex: 1; text-align: right; }
.ok { color: #2f6f4f; }
</style>
