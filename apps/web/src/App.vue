<script setup lang="ts">
import { onLaunch } from "@dcloudio/uni-app";
onLaunch(() => {});
</script>

<style>
/* WenQuest design tokens (match the academy site: ink + signal yellow) */
page, :root {
  --wq-ink: #14212b;
  --wq-accent: #f2b705;
  --wq-bg: #f4f6f5;
  --wq-text: #3a4a52;
  --wq-muted: #6b7c83;
  --wq-line: #dfe5e3;
  --wq-link: #1f6f8b;
  --wq-ok: #2e7d5b;
  --wq-danger: #b3261e;
}
page, body {
  background: var(--wq-bg);
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Noto Sans SC", "Microsoft YaHei", "Segoe UI", Roboto, sans-serif;
  color: var(--wq-text);
  -webkit-font-smoothing: antialiased;
}
</style>
