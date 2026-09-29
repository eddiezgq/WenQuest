<template>
  <view class="bi">
    <text v-if="label" class="wq-label">{{ label }}</text>
    <template v-if="two">
      <view class="pair" :class="{ rich: kind === 'rich' }">
        <view class="half">
          <text class="lang">中文</text>
          <RichEditor v-if="kind === 'rich'" :model-value="modelValue.zh || ''" @update:model-value="(v) => set('zh', v)" />
          <textarea v-else-if="kind === 'area'" class="wq-textarea" :value="modelValue.zh || ''" auto-height :maxlength="-1" @input="(e: any) => set('zh', e.detail.value)" />
          <input v-else class="wq-input" :value="modelValue.zh || ''" @input="(e: any) => set('zh', e.detail.value)" />
        </view>
        <view class="half">
          <text class="lang">English</text>
          <RichEditor v-if="kind === 'rich'" :model-value="modelValue.en || ''" @update:model-value="(v) => set('en', v)" />
          <textarea v-else-if="kind === 'area'" class="wq-textarea" :value="modelValue.en || ''" auto-height :maxlength="-1" @input="(e: any) => set('en', e.detail.value)" />
          <input v-else class="wq-input" :value="modelValue.en || ''" @input="(e: any) => set('en', e.detail.value)" />
        </view>
      </view>
    </template>
    <template v-else>
      <RichEditor v-if="kind === 'rich'" :model-value="modelValue.text || ''" :placeholder="placeholder" @update:model-value="(v) => set('text', v)" />
      <textarea v-else-if="kind === 'area'" class="wq-textarea" :value="modelValue.text || ''" auto-height :maxlength="-1" :placeholder="placeholder" @input="(e: any) => set('text', e.detail.value)" />
      <input v-else class="wq-input" :value="modelValue.text || ''" :placeholder="placeholder" @input="(e: any) => set('text', e.detail.value)" />
    </template>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import RichEditor from "./RichEditor.vue";
import type { Bi } from "../../courseApi";

const props = withDefaults(defineProps<{ modelValue: Bi; label?: string; kind?: "line" | "area" | "rich"; placeholder?: string }>(), { kind: "line" });
const emit = defineEmits<{ (e: "update:modelValue", v: Bi): void }>();
const two = computed(() => props.modelValue.text === undefined && (props.modelValue.zh !== undefined || props.modelValue.en !== undefined));
function set(k: keyof Bi, v: string) {
  emit("update:modelValue", { ...props.modelValue, [k]: v });
}
</script>

<style scoped>
.bi { margin-bottom: 6px; }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.pair.rich { grid-template-columns: 1fr; }
.lang { display: block; font-size: 12px; color: var(--wq-muted); margin-bottom: 2px; }
@media (max-width: 700px) { .pair { grid-template-columns: 1fr; } }
</style>
