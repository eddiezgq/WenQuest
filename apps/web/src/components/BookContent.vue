<template>
  <!-- #ifdef H5 -->
  <view class="book" v-html="html"></view>
  <!-- #endif -->
  <!-- #ifndef H5 -->
  <rich-text class="book" :nodes="html"></rich-text>
  <!-- #endif -->
</template>

<script setup lang="ts">
// A built textbook section (textbook/tools/build.py): our own trusted HTML, formulas already typeset —
// inline SVG on the web, SVG images in the mini program. Styles follow textbook/tools/book.css.
defineProps<{ html: string }>();
</script>

<style scoped>
.book { font-family: "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif; font-size: 16px; line-height: 1.85; color: #1d2327; word-break: break-word; }
.book :deep(h2) { font-family: "Noto Sans CJK SC", "PingFang SC", sans-serif; font-size: 22px; margin: 6px 0 16px; }
.book :deep(h3) { font-family: "Noto Sans CJK SC", "PingFang SC", sans-serif; font-size: 17px; margin: 28px 0 10px; }
.book :deep(p) { margin: 0 0 12px; text-align: justify; }
.book :deep(ol), .book :deep(ul) { padding-left: 1.6em; margin: 0 0 12px; }
.book :deep(blockquote) { margin: 12px 0; padding: 8px 16px; background: #f6f4ee; border-left: 3px solid #b8860b; }
.book :deep(hr) { border: 0; border-top: 1px solid #d9dee2; margin: 28px 0; }
.book :deep(table) { border-collapse: collapse; margin: 12px auto; font-size: 14px; }
.book :deep(th), .book :deep(td) { border: 1px solid #d9dee2; padding: 5px 10px; }
.book :deep(pre) { background: #f4f6f7; padding: 10px 12px; overflow-x: auto; font-size: 12.5px; line-height: 1.55; border-radius: 4px; }
.book :deep(code) { font-family: "JetBrains Mono", monospace; font-size: 13px; }
.book :deep(.wq-mi svg) { vertical-align: middle; }
.book :deep(.wq-eq) { margin: 14px 0; overflow-x: auto; text-align: center; }
.book :deep(.wq-eq .wq-md) { display: block; }
.book :deep(.wq-eq svg) { max-width: 100%; }
.book :deep(.wq-tagno) { float: right; }
.book :deep(figure) { margin: 18px 0; }
.book :deep(.wq-video) { display: block; width: 100%; max-height: 70vh; border-radius: 6px; background: #0f1419; }
.book :deep(.wq-poster) { display: block; width: 100%; border-radius: 6px; }
.book :deep(.wq-labbtn) { display: inline-block; margin: 6px 0 4px; padding: 10px 18px; border-radius: 8px; background: #b8860b; color: #fff; font-family: "Noto Sans CJK SC", sans-serif; font-size: 15px; text-decoration: none; }
.book :deep(.wq-labdoc) { display: inline-block; margin: 6px 0 4px 10px; padding: 9px 14px; border-radius: 8px; border: 1px solid #b8860b; color: #8a6508; font-family: "Noto Sans CJK SC", sans-serif; font-size: 14px; text-decoration: none; background: #fff; }
.book :deep(.wq-taskbox) { border: 1px solid #2f6f4f; border-left: 5px solid #2f6f4f; border-radius: 8px; background: #f4faf6; padding: 12px 14px; margin: 12px 0; font-family: "Noto Sans CJK SC", sans-serif; font-size: 15px; }
.book :deep(.wq-task-head) { color: #1f4d36; font-size: 16px; margin-bottom: 4px; }
.book :deep(.wq-task-role) { color: #4b5b52; font-size: 14px; margin-bottom: 6px; }
.book :deep(.wq-station) { display: inline-block; margin: 2px 6px 2px 0; padding: 2px 8px; border-radius: 10px; background: #dfeee5; color: #1f4d36; font-size: 13px; }
.book :deep(.wq-task-dl ul) { margin: 4px 0 0 1.2em; padding: 0; }
.book :deep(.wq-labrun) { margin: 6px 0; }
.book :deep(.wq-labrun > summary) { display: inline-block; padding: 10px 18px; border-radius: 8px; background: #1d2327; color: #fff; font-family: "Noto Sans CJK SC", sans-serif; font-size: 15px; cursor: pointer; list-style: none; }
.book :deep(.wq-labrun > summary::-webkit-details-marker) { display: none; }
.book :deep(.wq-labrun[open] > summary) { background: #5d6b73; }
.book :deep(.wq-labframe) { display: block; width: 100%; height: min(860px, 85vh); border: 1px solid #d9dee2; border-radius: 8px; margin-top: 10px; background: #eef0ee; }
.book :deep(.wq-note) { font-size: 13px; color: #5d6b73; text-align: center; }
.book :deep(.wq-tabcap) { font-family: "Noto Sans CJK SC", sans-serif; font-size: 13px; color: #5d6b73; text-align: center; margin-top: 18px; }
.book :deep(figcaption) { font-family: "Noto Sans CJK SC", sans-serif; font-size: 13px; color: #5d6b73; text-align: center; margin-top: 6px; }
.book :deep(.wq-media-box) { border: 1px dashed #b9c2c8; border-radius: 6px; padding: 26px 16px; text-align: center; color: #5d6b73; font-size: 13.5px; background: #fafbfb; }
.book :deep(.wq-lab .wq-media-box) { border-color: #b8860b; background: #fffaf0; }
.book :deep(.wq-prog) { border: 1px solid #d9dee2; border-radius: 6px; padding: 8px 12px; }
.book :deep(.wq-prog figcaption) { text-align: left; margin: 0 0 4px; }
.book :deep(.wq-prog summary) { cursor: pointer; font-size: 13px; color: #5d6b73; }
</style>
