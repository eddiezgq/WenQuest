// 第 52 轮 案例三：绷缝机——弯针定时 ±6° 变红、设计优化放回窗口正中；五种线迹的用线计划
const { clip } = require('./rec.js');
clip('web-11-case-cv', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click();
  await r.sewing(); await p.locator('.mopt', { hasText: '绷缝机' }).click(); await r.wait(3000); await tab('样机'); await r.wait(1500);
  r.cue('案例三：406 两针绷缝。弯针定时窗口只有 7.5°，最高转速下不到 0.2 毫秒'); await r.wait(6000);
  await tab('校核');
  r.cue('弯针定时拖到 −6°（来早了）'); await r.param('弯针', '弯针定时', -6); await p.evaluate(() => scrollTo(0, 0)); await r.wait(1500);
  r.cue('三项变红：弯针尖不在线环高度内、针下行时让不开、离窗口边缘不够'); await r.wait(6500);
  r.cue('拖到 +6°（来晚了）：线环过大、离窗口边缘不够'); await r.param('弯针', '弯针定时', 6); await p.evaluate(() => scrollTo(0, 0)); await r.wait(6000);
  await tab('CAE 分析'); await r.wait(2500);
  const opt = p.locator('.cae .box', { hasText: '设计优化' }).first(); await opt.scrollIntoViewIfNeeded();
  r.cue('设计优化：弯针定时放在窗口正中'); await opt.locator('.opt', { hasText: '弯针定时' }).click(); await r.wait(5000);
  r.cue('点“采用”：全部合格'); await opt.locator('.btn', { hasText: '采用' }).first().click(); await r.wait(2000); await tab('校核'); await p.evaluate(() => scrollTo(0, 0)); await r.wait(4000);
  await tab('零件与制造'); await r.wait(1500);
  r.cue('用线计划：1000 件 × 172 cm，406 要 32,364 m、7 个线团'); await p.locator('.tbl').first().scrollIntoViewIfNeeded().catch(() => {}); await r.wait(6000);
  for (const [k, t] of [['401', '401 双线链缝：3 个线团'], ['605', '605 三针带覆盖线：12 个线团，用线是 401 的 4.7 倍']]) {
    r.cue(t); await r.choose('基本参数', '线迹', k); await p.locator('.tbl').first().scrollIntoViewIfNeeded().catch(() => {}); await r.wait(5500);
  }
});
