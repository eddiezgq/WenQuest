const { clip } = require('./rec.js');
clip('web-07-lib-use', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p;
  await r.sewing(); await r.wait(2000);
  r.cue('设计里用：能接零件库的那组参数下面，有“从本单位零件库选”'); await p.getByText(/从本单位零件库选/).first().scrollIntoViewIfNeeded(); await r.wait(2000);
  await p.getByText(/从本单位零件库选/).first().click(); await r.wait(2500);
  r.cue('选一个曲柄：孔距 15.0 mm 填进“曲柄半径”，马上重算，全部合格'); await p.locator('.libitem', { hasText: 'NC-150' }).first().click(); await r.wait(4000);
  await p.evaluate(() => window.scrollTo(0, 0)); await r.wait(2500);
  r.cue('CAE 里用：机壳固有频率直接选库里的机壳，不用每次上传'); await p.locator('.tab', { hasText: 'CAE 分析' }).click(); await r.wait(2000);
  const box = p.locator('.cae .box', { hasText: '机壳固有频率' }).first(); await box.scrollIntoViewIfNeeded(); await r.wait(1500);
  await box.locator('.opt', { hasText: 'FR-100' }).click(); await r.wait(1500);
    await box.locator('.btn', { hasText: '提交计算' }).click(); await r.wait(2000);
  r.cut(true); await r.wait(3000); for (let i = 0; i < 200 && !(await p.evaluate(() => { const x = [...document.querySelectorAll('.cae .res')].find((e) => e.querySelector(':scope > .ct')); return !!(x && !x.querySelector(':scope > .hint') && x.querySelector('.lamp, .kgrid, svg, img, .para')); })); i++) await r.wait(2000); await r.wait(3000); r.cut(false);
  r.cue('CalculiX 算出前几阶固有频率；点“采用”回填“机壳一阶固有频率”，共振校核跟着变'); await p.evaluate(() => { const x = [...document.querySelectorAll('.cae .res')].find((e) => e.querySelector(':scope > .ct')); x && x.scrollIntoView({ block: 'start' }); }); await r.wait(7000);
});
