// 第 138 轮 G4.1：把 mech.html 一转逐帧截图（Playwright + 软件渲染），再用 ffmpeg 合成视频。
//   node mech_film.js <输出目录> <视角> <每帧度数> [宽 高] [零件目录]      页面要在 http://127.0.0.1:8511/mech.html 上
const { chromium } = require('playwright');
(async () => {
  const [,, out, view, step, w, h, dir] = process.argv;
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: +(w || 1280), height: +(h || 800) }, deviceScaleFactor: 1 });
  // 没法连 CDN 的机器（如云端容器）：THREE_DIR 指向本地 npm 装的 three（node_modules/three），从本地读
  if (process.env.THREE_DIR) await p.route('https://cdn.jsdelivr.net/npm/three@0.170.0/**', r => r.fulfill({ path: `${process.env.THREE_DIR}/` + r.request().url().split('three@0.170.0/')[1], contentType: 'application/javascript' }));
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.goto(`http://127.0.0.1:8511/mech.html?film=1&pr=1&view=${view}${dir ? '&d=' + dir : ''}&w=${w || 1280}&h=${h || 800}`);
  await p.waitForFunction(() => document.title === 'ready', null, { timeout: 600000 });
  let i = 0;
  for (let phi = 0; phi < 360; phi += +step) {
    await p.evaluate(([f, v]) => window.go(f, v), [phi, view]);
    await p.screenshot({ path: `${out}/f${String(i++).padStart(4, '0')}.png` });
  }
  await b.close();
  console.log('frames', i);
})();
