const { clip } = require('./rec.js');
clip('web-05-cae-mbd', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p;
  await r.sewing(); await p.locator('.tab', { hasText: 'CAE 分析' }).click(); await r.wait(3000);
  const box = p.locator('.cae .box', { hasText: '机构动力学' }).first(); await box.scrollIntoViewIfNeeded();
  r.cue('机构动力学：按曲柄、连杆、针杆质量自动建 MuJoCo 多体模型'); await r.wait(2500);
    await box.locator('.btn', { hasText: '算动力学' }).click(); await r.wait(2500);
  r.cut(true); await r.wait(3000); for (let i = 0; i < 200 && !(await p.evaluate(() => { const x = [...document.querySelectorAll('.cae .res')].find((e) => e.querySelector(':scope > .ct')); return !!(x && !x.querySelector(':scope > .hint') && x.querySelector('.lamp, .kgrid, svg, img, .para')); })); i++) await r.wait(2000); await r.wait(3000); r.cut(false);
  r.cue('算完：主轴转矩曲线，和本软件公式对照，相差不到 1%'); await p.evaluate(() => { const x = [...document.querySelectorAll('.cae .res')].find((e) => e.querySelector(':scope > .ct')); x && x.scrollIntoView({ block: 'start' }); }); await r.wait(6000);
  await box.scrollIntoViewIfNeeded(); r.cue('电机选型：峰值、均方根各留 1.2 倍余量；本单位零件库里的电机一起比，标“本单位”');
  await box.locator('.btn', { hasText: '电机选型' }).click(); await r.wait(2500); await box.locator('.tbl').first().scrollIntoViewIfNeeded().catch(() => {}); await r.wait(6000);
});
