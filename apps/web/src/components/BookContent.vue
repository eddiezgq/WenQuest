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
.book :deep(.wq-tabcap) { font-family: "Noto Sans CJK SC", sans-serif; font-size: 13px; color: #5d6b73; text-align: center; margin-top: 18px; }
.book :deep(figcaption) { font-family: "Noto Sans CJK SC", sans-serif; font-size: 13px; color: #5d6b73; text-align: center; margin-top: 6px; }
.book :deep(.wq-media-box) { border: 1px dashed #b9c2c8; border-radius: 6px; padding: 26px 16px; text-align: center; color: #5d6b73; font-size: 13.5px; background: #fafbfb; }
.book :deep(.wq-lab .wq-media-box) { border-color: #b8860b; background: #fffaf0; }
.book :deep(.wq-prog) { border: 1px solid #d9dee2; border-radius: 6px; padding: 8px 12px; }
.book :deep(.wq-prog figcaption) { text-align: left; margin: 0 0 4px; }
.book :deep(.wq-prog summary) { cursor: pointer; font-size: 13px; color: #5d6b73; }
</style>
