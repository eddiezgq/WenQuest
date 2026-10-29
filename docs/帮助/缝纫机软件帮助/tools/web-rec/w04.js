const { clip } = require('./rec.js');
clip('web-04-cae-fea', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p;
  await r.sewing(); await r.wait(1500);
  r.cue('“CAE 分析”页签：零件强度与疲劳，约束和载荷都自动加'); await p.locator('.tab', { hasText: 'CAE 分析' }).click(); await r.wait(3500);
  const box = p.locator('.cae .box', { hasText: '零件强度' }).first();
  r.cue('选“针杆曲柄”，材料用左边选的 45 钢（调质），点“提交计算”'); await box.locator('.opt', { hasText: '针杆曲柄' }).click(); await r.wait(1500);
    await box.locator('.btn', { hasText: '提交计算' }).click(); await r.wait(2500);
  r.cue('数字工厂排队：Gmsh 剖网格，CalculiX 求解，pyLife 算疲劳（等待的时间剪掉了）'); await r.wait(2500);
  r.cut(true);
  await r.wait(3000); for (let i = 0; i < 200 && !(await p.evaluate(() => { const x = [...document.querySelectorAll('.cae .res')].find((e) => e.querySelector(':scope > .ct')); return !!(x && !x.querySelector(':scope > .hint') && x.querySelector('.lamp, .kgrid, svg, img, .para')); })); i++) await r.wait(2000);
  await r.wait(3000); r.cut(false);
  r.cue('算完：应力云图、最大等效应力、安全系数、疲劳寿命，都和判据比过');
  await p.evaluate(() => { const x = [...document.querySelectorAll('.cae .res')].find((e) => e.querySelector(':scope > .ct')); x && x.scrollIntoView({ block: 'start' }); }); await r.wait(6000);
  await p.mouse.wheel(0, 400); r.cue('Word 报告可以下载；结果也自动写进同一组参数导出的计算书'); await r.wait(5000);
});
