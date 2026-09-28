<template>
  <view ref="box" class="math-content"><RichContent :html="html" /></view>
</template>

<script setup lang="ts">
// Rich content with formulas: after the HTML is in place, MathJax (loaded in index.html) typesets
// \( \), \[ \], $$ $$ in it. In the mini program formulas stay as written.
import { nextTick, onMounted, ref, watch } from "vue";
import RichContent from "./RichContent.vue";

const props = defineProps<{ html: string }>();
const box = ref<any>(null);

async function typeset() {
  // #ifdef H5
  await nextTick();
  const mj = (window as any).MathJax;
  const el = box.value?.$el || box.value;
  if (mj && mj.typesetPromise && el) {
    try { await mj.typesetPromise([el]); } catch { /* leave the source visible */ }
  } else if (el && !(window as any).__wqMathWait) {
    (window as any).__wqMathWait = true;
    window.addEventListener("wq-mathjax-ready", () => typeset(), { once: true });
  }
  // #endif
}
onMounted(typeset);
watch(() => props.html, typeset);
</script>
