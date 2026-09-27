<template>
  <!-- #ifdef H5 -->
  <view class="rich" v-html="html"></view>
  <!-- #endif -->
  <!-- #ifndef H5 -->
  <rich-text class="rich" :nodes="html"></rich-text>
  <!-- #endif -->
</template>

<script setup lang="ts">
// HTML arrives already sanitized by the gateway (see services/gateway/app/content.py).
defineProps<{ html: string }>();
</script>

<style scoped>
/* uni-app scopes component styles, so rules for injected HTML use :deep().
   Media use attribute selectors because uni-app rewrites the video tag name in CSS. */
.rich { font-size: 16px; line-height: 1.75; color: var(--wq-text); word-break: break-word; }
.rich :deep(p) { display: block; margin: 0 0 12px; }
.rich :deep(h1), .rich :deep(h2), .rich :deep(h3) { color: var(--wq-ink); margin: 20px 0 10px; line-height: 1.35; }
.rich :deep(img), .rich :deep(iframe), .rich :deep([controls]) { max-width: 100%; height: auto; border-radius: 8px; }
.rich :deep(iframe) { width: 100%; aspect-ratio: 16 / 9; border: 0; }
.rich :deep(pre) { background: #f2f4f3; padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 14px; }
.rich :deep(code) { font-family: "IBM Plex Mono", Menlo, Consolas, monospace; }
.rich :deep(table) { border-collapse: collapse; width: 100%; display: block; overflow-x: auto; }
.rich :deep(th), .rich :deep(td) { border: 1px solid var(--wq-line); padding: 6px 10px; text-align: left; }
.rich :deep(a) { color: var(--wq-link); }
.rich :deep(blockquote) { border-left: 4px solid var(--wq-accent); margin: 12px 0; padding: 4px 14px; color: var(--wq-muted); }
.rich :deep(ul), .rich :deep(ol) { padding-left: 24px; margin: 0 0 12px; }
</style>
