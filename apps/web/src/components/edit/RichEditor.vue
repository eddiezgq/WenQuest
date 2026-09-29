<template>
  <view class="rich">
    <!-- #ifdef H5 -->
    <view class="bar">
      <text class="tb" title="Bold" @mousedown.prevent="cmd('bold')"><b>B</b></text>
      <text class="tb" title="Italic" @mousedown.prevent="cmd('italic')"><i>I</i></text>
      <text class="tb" @mousedown.prevent="cmd('formatBlock', 'h3')">{{ t("editor.heading") }}</text>
      <text class="tb" @mousedown.prevent="cmd('formatBlock', 'p')">{{ t("editor.paragraph") }}</text>
      <text class="tb" @mousedown.prevent="cmd('insertUnorderedList')">• {{ t("editor.list") }}</text>
      <text class="tb" @mousedown.prevent="cmd('insertOrderedList')">1. {{ t("editor.list") }}</text>
      <text class="tb" @mousedown.prevent="link">🔗 {{ t("editor.link") }}</text>
      <text class="tb" @mousedown.prevent="formula">∑ {{ t("editor.formula") }}</text>
      <text class="tb" @mousedown.prevent="cmd('removeFormat')">{{ t("editor.clear") }}</text>
      <text class="tb right" :class="{ on: mode === 'html' }" @click="toggleHtml">&lt;/&gt;</text>
      <text class="tb" :class="{ on: preview }" @click="preview = !preview">{{ t("editor.preview") }}</text>
    </view>
    <div v-show="mode === 'rich'" ref="box" class="box" contenteditable="true" :data-placeholder="placeholder" @input="sync" @blur="sync" />
    <textarea v-if="mode === 'html'" v-model="raw" class="wq-textarea code" @input="emit('update:modelValue', raw)" />
    <!-- #endif -->
    <!-- #ifndef H5 -->
    <textarea v-model="raw" class="wq-textarea" auto-height :maxlength="-1" :placeholder="placeholder" @input="emit('update:modelValue', raw)" />
    <!-- #endif -->
    <view v-if="preview" class="preview"><MathContent :html="modelValue" /></view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import MathContent from "../MathContent.vue";
import { t } from "../../i18n";

const props = defineProps<{ modelValue: string; placeholder?: string }>();
const emit = defineEmits<{ (e: "update:modelValue", v: string): void }>();
const box = ref<HTMLElement | null>(null);
const raw = ref(props.modelValue || "");
const mode = ref<"rich" | "html">("rich");
// Formulas cannot render while editing, so text with LaTeX opens with the preview shown.
const preview = ref(/\\\(|\\\[/.test(props.modelValue || ""));
let own = false;

function sync() {
  // #ifdef H5
  if (!box.value) return;
  own = true;
  raw.value = box.value.innerHTML === "<br>" ? "" : box.value.innerHTML;
  emit("update:modelValue", raw.value);
  // #endif
}
function cmd(name: string, value?: string) {
  // #ifdef H5
  box.value?.focus();
  document.execCommand(name, false, value);
  sync();
  // #endif
}
function link() {
  // #ifdef H5
  const url = window.prompt(t("editor.linkPrompt"), "https://");
  if (url && /^https?:\/\//.test(url)) cmd("createLink", url);
  // #endif
}
function formula() {
  // #ifdef H5
  const tex = window.prompt(t("editor.formulaPrompt"), "a = \\frac{v^2}{R}");
  if (tex) cmd("insertText", `\\(${tex}\\)`);
  // #endif
}
function toggleHtml() {
  // #ifdef H5
  if (mode.value === "rich") {
    sync();
    mode.value = "html";
  } else {
    mode.value = "rich";
    if (box.value) box.value.innerHTML = raw.value;
  }
  // #endif
}

watch(() => props.modelValue, (v) => {
  if (!preview.value && /\\\(|\\\[/.test(v || "")) preview.value = true;
  if (own) { own = false; return; }
  raw.value = v || "";
  // #ifdef H5
  if (box.value && mode.value === "rich" && box.value.innerHTML !== raw.value) box.value.innerHTML = raw.value;
  // #endif
});
onMounted(() => {
  // #ifdef H5
  if (box.value) box.value.innerHTML = raw.value;
  // #endif
});
</script>

<style scoped>
.rich { border: 1px solid var(--wq-line); border-radius: 8px; background: #fff; overflow: hidden; }
.bar { display: flex; flex-wrap: wrap; gap: 2px; padding: 6px; border-bottom: 1px solid var(--wq-line); background: #f7f9f9; }
.tb { padding: 4px 9px; border-radius: 5px; cursor: pointer; font-size: 13px; color: var(--wq-ink); user-select: none; }
.tb:hover, .tb.on { background: #e6ecee; }
.tb.right { margin-left: auto; font-family: Menlo, monospace; }
.box { min-height: 260px; padding: 14px 16px; outline: none; line-height: 1.8; font-size: 15px; }
.box:empty::before { content: attr(data-placeholder); color: #a4b0b5; }
.box :deep(h3) { font-size: 18px; margin: 12px 0 6px; }
.code { font-family: Menlo, monospace; font-size: 13px; min-height: 260px; border: 0; border-radius: 0; }
.preview { border-top: 1px dashed var(--wq-line); padding: 12px 16px; background: #fcfcfb; }
</style>
