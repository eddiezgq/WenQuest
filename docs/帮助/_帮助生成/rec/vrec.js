// 带配音的帮助录屏（第 90 轮）：say(文字) 记字幕时间并等配音读完（时长来自 lines.py 写的 durations.json）；
// cut(true/false) 标要剪掉的等待段。网址 http://wenquestrobotics.test/<软件>/… 由本机服务应答（ROUTES）。
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const ROUTES = { bearing: 'http://localhost:8931', cam: 'http://localhost:8932' };
async function clip(outDir, voiceDir, name, body) {
  fs.mkdirSync(outDir, { recursive: true });
  const dur = JSON.parse(fs.readFileSync(path.join(voiceDir, 'durations.json'), 'utf8'));
  const b = await chromium.launch();
  const dir = fs.mkdtempSync(path.join(outDir, 'v-'));
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, locale: 'zh-CN', recordVideo: { dir, size: { width: 1280, height: 720 } }, acceptDownloads: true });
  await ctx.route('**/*', async (route) => {
    const u = new URL(route.request().url());
    const app = u.pathname.split('/')[1];
    if (u.hostname !== 'wenquestrobotics.test' || !ROUTES[app]) return route.continue();
    const p = u.pathname.replace('/' + app, '') || '/';
    if (p === '/api/me') return route.fulfill({ json: { login: false, licensed: false, reachable: true } });
    try { return route.fulfill({ response: await route.fetch({ url: ROUTES[app] + p + u.search }) }); } catch (e) { return route.abort(); }
  });
  const p = await ctx.newPage(); const t0 = Date.now();
  p.on('pageerror', (e) => console.log('PAGEERROR', e.message));
  const cues = [], cuts = []; let cutStart = null;
  const now = () => (Date.now() - t0) / 1000;
  const r = {
    p, wait: (ms) => p.waitForTimeout(ms),
    async open(url) { await p.goto('http://wenquestrobotics.test' + url); await p.waitForTimeout(2500); },
    async say(text, extra = 0) {
      const d = dur[text]; if (!d) throw new Error('no voice for: ' + text + '（先运行 lines.py）');
      cues.push({ t: now(), text, dur: d.sec, wav: d.wav }); await p.waitForTimeout(d.sec * 1000 + 350 + extra);
    },
    cut(on) { if (on) cutStart = now(); else if (cutStart != null) { cuts.push([cutStart, now()]); cutStart = null; } },
    async type(loc, text) { await loc.click(); await loc.fill(''); await loc.pressSequentially(String(text), { delay: 70 }); await loc.press('Tab'); },
    async scroll(sel) { await p.locator(sel).first().scrollIntoViewIfNeeded(); await p.waitForTimeout(500); },
    async num(label, value) {         // a number field by its label text (bearing: label.num; cam: label / label.nf with an input)
      const inp = p.locator('label', { hasText: label }).filter({ has: p.locator('input') }).locator('input').first();
      await inp.scrollIntoViewIfNeeded(); await inp.click(); await inp.fill(''); await inp.pressSequentially(String(value), { delay: 80 }); await inp.press('Tab'); await p.waitForTimeout(1500);
    },
    async pick(label, value) {        // a select by its label
      const s = p.locator('label.num', { hasText: label }).locator('select').first();
      await s.scrollIntoViewIfNeeded(); await s.selectOption(value); await p.waitForTimeout(1500);
    },
    async smooth(dy) { for (let i = 0; i < 10; i++) { await p.mouse.wheel(0, dy / 10); await p.waitForTimeout(40); } await p.waitForTimeout(300); },
  };
  await body(r);
  const end = now();
  await ctx.close(); await b.close();
  const webm = fs.readdirSync(dir).find((f) => f.endsWith('.webm'));
  fs.renameSync(path.join(dir, webm), path.join(outDir, name + '.webm')); fs.rmdirSync(dir);
  fs.writeFileSync(path.join(outDir, name + '.json'), JSON.stringify({ cues, cuts, end }, null, 1));
  console.log(name, 'done', end.toFixed(1), 's', cues.length, 'lines', cuts.length, 'cuts');
}
module.exports = { clip };
