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

/* Shared building blocks of the course menus (announcements, discussions, people ...) */
.wq-h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); margin-bottom: 16px; }
.wq-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.wq-head .wq-h1 { margin-bottom: 0; }
.wq-card { background: #fff; border: 1px solid var(--wq-line); border-radius: 8px; padding: 16px 18px; margin-bottom: 12px; }
.wq-empty { background: #fff; border: 1px dashed var(--wq-line); border-radius: 8px; padding: 22px; color: var(--wq-muted); text-align: center; margin-bottom: 12px; }
.wq-muted { color: var(--wq-muted); font-size: 13px; }
.wq-btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 16px; border-radius: 8px; font-size: 14px;
  cursor: pointer; border: 1px solid var(--wq-line); background: #fff; color: var(--wq-ink); white-space: nowrap; line-height: 1.3; }
.wq-btn:hover { border-color: var(--wq-link); }
.wq-btn.primary { background: var(--wq-accent); border-color: var(--wq-accent); font-weight: 600; }
.wq-btn.dark { background: var(--wq-ink); border-color: var(--wq-ink); color: #fff; }
.wq-btn.danger { color: var(--wq-danger); }
.wq-btn.small { padding: 4px 10px; font-size: 13px; border-radius: 6px; }
.wq-btn.disabled { opacity: .5; pointer-events: none; }
.wq-link { color: var(--wq-link); cursor: pointer; font-size: 13px; }
.wq-link.danger { color: var(--wq-danger); }
.wq-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.wq-label { display: block; font-size: 13px; color: var(--wq-muted); margin: 10px 0 4px; }
.wq-input { width: 100%; box-sizing: border-box; border: 1px solid var(--wq-line); border-radius: 6px; padding: 8px 10px; font-size: 14px; background: #fff; min-height: 38px; }
.wq-textarea { width: 100%; box-sizing: border-box; border: 1px solid var(--wq-line); border-radius: 6px; padding: 8px 10px; font-size: 14px; background: #fff; min-height: 110px; line-height: 1.6; }
.wq-tag { display: inline-block; font-size: 12px; padding: 1px 8px; border-radius: 999px; background: #eef2f1; color: var(--wq-text); white-space: nowrap; }
.wq-tag.accent { background: #fff3d6; color: #7a5a00; }
.wq-tag.ok { background: #e3f3ea; color: var(--wq-ok); }
.wq-tag.live { background: #fde7e5; color: var(--wq-danger); }
.wq-tag.info { background: #e3eff4; color: var(--wq-link); }
.wq-avatar { width: 34px; height: 34px; border-radius: 50%; background: #dde7ea; color: var(--wq-ink); display: inline-flex; align-items: center;
  justify-content: center; font-weight: 600; font-size: 14px; flex-shrink: 0; overflow: hidden; }
.wq-error { color: var(--wq-danger); font-size: 13px; display: block; margin-top: 6px; }
.wq-tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--wq-line); margin-bottom: 16px; }
.wq-tab { padding: 8px 14px; cursor: pointer; color: var(--wq-muted); border-bottom: 2px solid transparent; margin-bottom: -1px; }
.wq-tab.on { color: var(--wq-ink); border-bottom-color: var(--wq-accent); font-weight: 600; }
</style>
