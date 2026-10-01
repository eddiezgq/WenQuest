<template>
  <!-- #ifdef H5 -->
  <view ref="root" class="rich" v-html="html"></view>
  <!-- #endif -->
  <!-- #ifndef H5 -->
  <rich-text class="rich" :nodes="html"></rich-text>
  <!-- #endif -->
</template>

<script setup lang="ts">
// HTML arrives already sanitized by the gateway (see services/gateway/app/content.py).
// A link with class wq-factory (问渠数字工厂's live workshop) gets a "show it here" button on the web: the factory's
// read-only 3D workshop opens inside the page. In the mini program it stays a plain link.
import { nextTick, onMounted, ref, watch } from "vue";
import { t } from "../i18n";

const props = defineProps<{ html: string }>();
const root = ref<any>(null);

async function enhance() {
  // #ifdef H5
  await nextTick();
  const el: HTMLElement | null = root.value?.$el || root.value;
  if (!el || !el.querySelectorAll) return;
  el.querySelectorAll("a.wq-factory").forEach((a: Element) => {
    const link = a as HTMLAnchorElement;
    link.target = "_blank";
    if (link.dataset.wq) return;
    link.dataset.wq = "1";
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "wq-factory-btn";
    btn.textContent = t("factory.showHere");
    let frame: HTMLIFrameElement | null = null;
    btn.onclick = () => {
      if (frame) { frame.remove(); frame = null; btn.textContent = t("factory.showHere"); return; }
      frame = document.createElement("iframe");
      frame.src = link.href;
      frame.className = "wq-factory-frame";
      frame.title = link.textContent || "";
      frame.setAttribute("sandbox", "allow-scripts allow-same-origin");
      frame.setAttribute("loading", "lazy");
      (link.closest("p") || link).after(frame);
      btn.textContent = t("factory.hide");
    };
    link.after(btn);
  });
  // #endif
}
onMounted(enhance);
watch(() => props.html, enhance);
</script>

<style scoped>
/* uni-app scopes component styles, so rules for injected HTML use :deep().
   Media use attribute selectors because uni-app rewrites the video tag name in CSS. */
.rich { font-size: 16px; line-height: 1.75; color: var(--wq-text); word-break: break-word; }
.rich :deep(p) { display: block; margin: 0 0 12px; }
.rich :deep(h1), .rich :deep(h2), .rich :deep(h3) { color: var(--wq-ink); margin: 20px 0 10px; line-height: 1.35; }
.rich :deep(img), .rich :deep(iframe), .rich :deep([controls]) { max-width: 100%; height: auto; border-radius: 8px; }
.rich :deep(iframe) { width: 100%; aspect-ratio: 16 / 9; border: 0; }
.rich :deep(.wq-fig), .rich :deep(figure) { margin: 18px auto; text-align: center; max-width: 760px; }
.rich :deep(.wq-fig img), .rich :deep(figure img) { max-height: 440px; width: auto; max-width: 100%; border: 1px solid var(--wq-line); background: #fff; }
.rich :deep(.wq-cap), .rich :deep(figcaption) { font-size: 13px; color: var(--wq-muted); margin-top: 6px; }
.rich :deep(pre) { background: #f2f4f3; padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 14px; }
.rich :deep(code) { font-family: "IBM Plex Mono", Menlo, Consolas, monospace; }
.rich :deep(table) { border-collapse: collapse; width: 100%; display: block; overflow-x: auto; }
.rich :deep(th), .rich :deep(td) { border: 1px solid var(--wq-line); padding: 6px 10px; text-align: left; }
.rich :deep(a) { color: var(--wq-link); }
.rich :deep(blockquote) { border-left: 4px solid var(--wq-accent); margin: 12px 0; padding: 4px 14px; color: var(--wq-muted); }
.rich :deep(.wq-factory-btn) { margin-left: 8px; font-size: 13px; padding: 2px 10px; border: 1px solid var(--wq-line); border-radius: 12px; background: #fff; cursor: pointer; }
.rich :deep(.wq-factory-frame) { display: block; width: 100%; aspect-ratio: 16 / 9; border: 1px solid var(--wq-line); border-radius: 8px; margin: 8px 0 14px; }
.rich :deep(ul), .rich :deep(ol) { padding-left: 24px; margin: 0 0 12px; }
</style>
