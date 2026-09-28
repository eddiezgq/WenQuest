<template>
  <view class="pdf">
    <view class="bar">
      <text class="count">{{ status }}</text>
      <view class="zoom">
        <text class="zb" @click="zoom(-0.15)">−</text>
        <text class="zv">{{ Math.round(scale * 100) }}%</text>
        <text class="zb" @click="zoom(0.15)">＋</text>
      </view>
    </view>
    <view ref="pages" class="pages" />
  </view>
</template>

<script setup lang="ts">
// H5 only: renders a PDF page by page with pdf.js (the browser's own viewer is blocked by the
// file proxy's sandbox policy, and this also works the same in every browser and on phones).
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as pdfjsLib from "pdfjs-dist";
import workerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import { t } from "../i18n";

// Static imports: uni-app's H5 build mis-names lazily loaded vendor chunks.
pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

const props = defineProps<{ url: string }>();
const pages = ref<any>(null);
const status = ref("");
const scale = ref(1);
let doc: any = null;
let observer: IntersectionObserver | null = null;

function container(): HTMLElement | null {
  return (pages.value?.$el || pages.value) as HTMLElement | null;
}

async function render() {
  const box = container();
  if (!box || !doc) return;
  box.innerHTML = "";
  observer?.disconnect();
  const width = Math.min(box.clientWidth || 800, 1100);
  observer = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      const holder = e.target as HTMLElement;
      observer!.unobserve(holder);
      drawPage(holder, Number(holder.dataset.page), width);
    }
  }, { rootMargin: "600px 0px" });
  const first = await doc.getPage(1);
  const vp1 = first.getViewport({ scale: 1 });
  for (let i = 1; i <= doc.numPages; i++) {
    const holder = document.createElement("div");
    holder.className = "wq-pdf-page";
    holder.dataset.page = String(i);
    holder.style.aspectRatio = `${vp1.width} / ${vp1.height}`;
    holder.style.width = `${Math.round(width * scale.value)}px`;
    box.appendChild(holder);
    observer.observe(holder);
  }
}

async function drawPage(holder: HTMLElement, n: number, width: number) {
  const page = await doc.getPage(n);
  const base = page.getViewport({ scale: 1 });
  const cssWidth = width * scale.value;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const vp = page.getViewport({ scale: (cssWidth / base.width) * dpr });
  const canvas = document.createElement("canvas");
  canvas.width = Math.floor(vp.width);
  canvas.height = Math.floor(vp.height);
  canvas.style.width = "100%";
  canvas.style.display = "block";
  holder.style.aspectRatio = "";
  holder.appendChild(canvas);
  await page.render({ canvasContext: canvas.getContext("2d"), viewport: vp }).promise;
}

async function load() {
  status.value = t("common.loading");
  try {
    doc = await pdfjsLib.getDocument({ url: props.url }).promise;
    status.value = t("viewer.pages", { n: doc.numPages });
    await render();
  } catch (e) {
    console.warn("PDF viewer:", e);
    status.value = t("viewer.pdfFailed");
  }
}

function zoom(d: number) {
  scale.value = Math.min(2, Math.max(0.5, +(scale.value + d).toFixed(2)));
  render();
}

onMounted(load);
watch(() => props.url, load);
onBeforeUnmount(() => { observer?.disconnect(); doc?.destroy?.(); });
</script>

<style scoped>
.pdf { background: #e9edec; border-radius: 10px; overflow: hidden; }
.bar { display: flex; justify-content: space-between; align-items: center; padding: 8px 14px; background: #fff; border-bottom: 1px solid var(--wq-line); position: sticky; top: 0; z-index: 2; }
.count { font-size: 13px; color: var(--wq-muted); }
.zoom { display: flex; align-items: center; gap: 10px; }
.zb { width: 28px; height: 28px; border-radius: 6px; border: 1px solid var(--wq-line); display: flex; align-items: center; justify-content: center; cursor: pointer; }
.zv { font-size: 13px; font-family: "IBM Plex Mono", Menlo, monospace; min-width: 44px; text-align: center; }
.pages { padding: 16px; display: flex; flex-direction: column; align-items: center; gap: 14px; overflow-x: auto; }
.pages :deep(.wq-pdf-page) { background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,.12); max-width: 100%; }
</style>
