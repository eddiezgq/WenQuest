// 帮助录屏：登录后带着登录状态开一个录像的页面；cue(文字) 记字幕时间，cut(true/false) 标要剪掉的等待段
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const OUT = __dirname + '/out';
async function session(user, pass) {
  const b = await chromium.launch();
  const c0 = await b.newContext({ viewport: { width: 1280, height: 720 } });
  const p0 = await c0.newPage();
  await p0.goto('http://localhost:8088/#/pages/login/login'); await p0.waitForTimeout(1500);
  const inputs = p0.locator('input'); await inputs.nth(0).fill(user); await inputs.nth(1).fill(pass); await p0.keyboard.press('Enter'); await p0.waitForTimeout(2500);
  if (await p0.getByText('Language').count()) { await p0.getByText('Language').click(); await p0.waitForTimeout(600); }
  const state = await c0.storageState(); await c0.close();
  return { b, state };
}
async function clip(name, user, pass, body) {
  fs.mkdirSync(OUT, { recursive: true });
  const { b, state } = await session(user, pass);
  const dir = fs.mkdtempSync(OUT + '/v-');
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, storageState: state, recordVideo: { dir, size: { width: 1280, height: 720 } } });
  const p = await ctx.newPage(); const t0 = Date.now();
  p.on('pageerror', (e) => console.log('PAGEERROR', e.message));
  const cues = [], cuts = []; let cutStart = null;
  const now = () => (Date.now() - t0) / 1000;
  const api = {
    p, wait: (ms) => p.waitForTimeout(ms),
    cue(text, dur) { cues.push({ t: now(), text, dur }); },
    cut(on) { if (on) cutStart = now(); else if (cutStart != null) { cuts.push([cutStart, now()]); cutStart = null; } },
    async sewing() { await p.goto('http://localhost:8088/'); await p.waitForTimeout(2500); await p.getByText('缝纫机设计').first().click(); await p.waitForTimeout(3000); },
    async type(loc, text) { await loc.click(); await loc.fill(''); await loc.pressSequentially(text, { delay: 60 }); },
    async param(group, label, value) {
      const g = p.locator('.grp', { hasText: group }).first();
      if (!(await g.locator('.prm').count())) { await g.locator('.gt').click(); await p.waitForTimeout(300); }
      const inp = g.locator('.prm', { hasText: label }).locator('input').last();
      await inp.scrollIntoViewIfNeeded(); await inp.click(); await inp.fill(String(value)); await inp.press('Enter'); await p.waitForTimeout(900);
    },
  };
  await body(api);
  const end = now();
  await ctx.close(); await b.close();
  const webm = fs.readdirSync(dir).find((f) => f.endsWith('.webm'));
  fs.renameSync(path.join(dir, webm), `${OUT}/${name}.webm`); fs.rmdirSync(dir);
  fs.writeFileSync(`${OUT}/${name}.json`, JSON.stringify({ cues, cuts, end }, null, 1));
  console.log(name, 'done', end.toFixed(1), 's', cues.length, 'cues', cuts.length, 'cuts');
}
module.exports = { clip };
