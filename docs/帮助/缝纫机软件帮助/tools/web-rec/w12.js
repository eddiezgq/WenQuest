// 第 52 轮 案例四：花样机——2000 r/min 红灯、加速度 50 又一盏、带轮 8 mm 全部合格；产能；模板槽板数控
const { clip } = require('./rec.js');
clip('web-12-case-pt', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click();
  await r.sewing(); await p.locator('.mopt', { hasText: '电子花样机' }).click(); await r.wait(3000); await tab('校核'); await r.wait(1500);
  r.cue('案例四：口袋盖花样，1800 r/min，14 项全部合格，每小时 282 件'); await r.wait(5000);
  r.cue('设计转速提到 2000：Y 轴走不完（上限 1860），红灯'); await r.param('基本参数', '设计缝纫转速', 2000); await p.evaluate(() => scrollTo(0, 0)); await r.wait(6000);
  r.cue('Y 轴加速度 40 → 50：转速过了，可 Y 轴电机发热超额定，又一盏红灯'); await r.param('Y 轴', '加速度', 50); await p.evaluate(() => scrollTo(0, 0)); await r.wait(6500);
  r.cue('不换电机，换带轮：Y 轴同步带轮半径 10 → 8 mm'); await r.param('Y 轴', '同步带轮节圆半径', 8); await p.evaluate(() => scrollTo(0, 0)); await r.wait(2000);
  r.cue('全部合格。但每小时只多 3 件——一个周期里真正缝的只有两秒多，大头是剪线、空走、上下料'); await r.wait(7500);
  await tab('CAE 分析'); await r.wait(2500);
  const cam = p.locator('.cae .box', { hasText: '数控编程' }).first(); await cam.scrollIntoViewIfNeeded();
  r.cue('最后做模板：数控编程选“花样模板（槽板）”，槽宽 5 mm、板厚 3 mm'); await cam.locator('.opt', { hasText: '花样模板' }).click();
  await cam.locator('.opt', { hasText: '5 mm' }).first().click(); await cam.locator('.opt', { hasText: '3 mm' }).last().click(); await r.wait(1500);
  await cam.locator('.btn', { hasText: '出铣削程序' }).click(); await r.wait(2000);
  await r.job('pattern');
  r.cue('按 49 个针位开通槽，两个定位销孔；刀路、加工时间、试切检查 0 错误，下载 G 代码和模板 STEP'); await r.wait(8000);
});
