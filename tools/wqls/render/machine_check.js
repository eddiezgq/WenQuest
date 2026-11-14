// 第 138 轮 G6.1 验收脚本：网页三维整机。限速 20 Mbps 计载入时间；拖手轮；点零件；8 种变型 × 各状态都切一遍；三向剖开；中英切换。
//   页面要在静态服务上（如 cd factory/digital/web/public && python3 -m http.server 8512），然后 node machine_check.js http://127.0.0.1:8512/wqls/index.html
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('404')) errs.push(m.text()); });
  const c = await p.context().newCDPSession(p);
  await c.send('Network.enable'); await c.send('Network.setCacheDisabled', { cacheDisabled: true });
  await c.send('Network.emulateNetworkConditions', { offline: false, latency: 40, downloadThroughput: 20e6 / 8, uploadThroughput: 5e6 / 8 });
  const t0 = Date.now();
  await p.goto(process.argv[2]);
  await p.waitForFunction(() => window.__wq, null, { timeout: 120000 });
  console.log('20Mbps load-to-ready ms', Date.now() - t0);
  await c.send('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  await p.click('#play');                                     // 停下
  await p.evaluate(() => { window.__wq.view('wheel'); window.__wq.setPhi(0); });
  await p.waitForTimeout(300);
  // 手轮在屏幕上的位置
  const hw = await p.evaluate(() => {
    const w = window.__wq; const m = w.P.handwheel.mesh; m.geometry.computeBoundingBox();
    const bb = m.geometry.boundingBox; const c = bb.getCenter(new THREE.Vector3()); c.x = bb.max.x; c.z += 40;
    c.applyMatrix4(m.matrixWorld);
    const cam = window.__cam; const v = c.clone().project(cam); return [(v.x + 1) / 2 * innerWidth, (1 - v.y) / 2 * innerHeight];
  });
  console.log('handwheel at', hw.map(Math.round));
  for (const dy of [-35,-25,-15,0,15,25]) console.log('hit', dy, await p.evaluate(([x, y]) => window.__hit(x, y), [hw[0], hw[1] + dy]));
  const phi0 = await p.evaluate(() => window.__wq.S.phi);
  await p.mouse.move(hw[0], hw[1]); await p.mouse.down();
  for (let k = 1; k <= 12; k++) { await p.mouse.move(hw[0] + 3 * k, hw[1] + 1 * k); }
  await p.mouse.up();
  const phi1 = await p.evaluate(() => window.__wq.S.phi);
  console.log('drag handwheel: phi', phi0.toFixed(1), '->', phi1.toFixed(1));
  // 点零件：上轴中间
  const pt = await p.evaluate(() => { const m = window.__wq.P.shaft.mesh; m.geometry.computeBoundingBox(); const c = m.geometry.boundingBox.getCenter(new THREE.Vector3()); c.x = 250; c.applyMatrix4(m.matrixWorld); const v = c.project(window.__cam); return [(v.x + 1) / 2 * innerWidth, (1 - v.y) / 2 * innerHeight]; });
  await p.click('[data-shell=off]');
  await p.mouse.click(pt[0], pt[1]);
  await p.waitForTimeout(200);
  console.log('clicked card:', (await p.textContent('#card')).slice(0, 80));
  // 全部变型和状态
  let n = 0;
  for (const o of ['', 'T', 'E', 'TE']) for (const d of [false, true]) for (const f of ['s3', 's5', 'r5']) for (const pr of ['down', 'hand', 'knee']) for (const tr of ['sew', 'trim', 'wipe']) {
    if (tr !== 'sew' && !o.includes('T')) continue;
    await p.evaluate(([o, d, f, pr, tr]) => { const S = window.__wq.S; S.T = o.includes('T'); S.E = o.includes('E'); S.Dd = d; S.feed = f; S.press = pr; S.trim = tr; window.__wq.refreshState(); for (let a = 0; a < 360; a += 37) { S.phi = a; S.wipe = a / 2; window.__wq.pose(); } }, [o, d, f, pr, tr]);
    n++;
  }
  console.log('states visited', n);
  // 每个零件都点得到（按名字选中），都有物料号
  const miss = await p.evaluate(() => { const out = []; for (const [k, i] of Object.entries(window.__wq.P)) { if (!i.info.code) out.push(k); } return out; });
  console.log('parts without code', miss.length, 'total parts', await p.evaluate(() => Object.keys(window.__wq.P).length));
  for (const ax of ['x', 'y', 'z']) { await p.click(`[data-cut=${ax}]`); await p.waitForTimeout(100); }
  await p.click('[data-cut=""]');
  await p.click('#lang'); console.log('lang now', await p.textContent('h1'));
  console.log('errors', JSON.stringify(errs));
  await b.close();
})();
