// 第 52 轮 案例三，第 73 轮重录：绷缝机三维样机；弯针定时 ±6° 变红、设计优化放回窗口正中；五种线迹的用线计划
const { clip } = require('./rec.js');
clip('web-11-case-cv', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click();
  // 第 73 轮：样机页签是三维样机（模型 10-1）；iframe 里的页面用 __set / __api 控制视角、转角
  const inFrame = async (fn, arg) => { const h = await p.locator('iframe.proto').elementHandle(); const f = await h.contentFrame(); return f.evaluate(fn, arg); };
  await r.sewing(); await p.locator('.mopt', { hasText: '绷缝机' }).click(); await r.wait(3500); await tab('样机'); await p.locator('iframe.proto').scrollIntoViewIfNeeded(); await p.evaluate(() => scrollBy(0, 120)); await r.wait(3000);
  r.cue('案例三：406 两针绷缝。“样机”是教材的三维样机（模型 10-1）：两根针、一根弯针、送布牙'); await r.wait(5500);
  await inFrame(() => { window.__set({ mode: 'xray', view: 'iso' }); document.getElementById('play').click(); }); await r.wait(500);
  r.cue('透视着色：引线（蓝）、弯针（橙）、送布（紫）；弯针由下轴的偏心经球头连杆带动'); await r.wait(6000);
  await inFrame(() => { document.getElementById('play').click(); document.querySelector('[data-v="close"]').click(); document.querySelector('[data-go="fc"]').click(); }); await r.wait(800);
  r.cue('成缝区特写，转到钩线时刻：弯针尖从针后钻进针线环。弯针定时窗口只有 7.5°，最高转速下不到 0.2 毫秒'); await r.wait(7000);
  r.cue('弯针定时拖到 −6°（来早了）'); await r.param('弯针', '弯针定时', -6); await p.locator('iframe.proto').scrollIntoViewIfNeeded(); await p.evaluate(() => scrollBy(0, 120)); await r.wait(2500);
  await inFrame(() => document.querySelector('[data-go="bad"]').click()); await r.wait(800);
  r.cue('三维样机马上跟着变：右上角“跳针”，机针标红；转到出问题的转角——针下到弯针平面时刺不进线三角'); await r.wait(7500);
  await tab('校核'); await p.evaluate(() => scrollTo(0, 0)); await r.wait(1000);
  r.cue('校核里同样三项变红：弯针尖不在线环高度内、针下行时让不开、离窗口边缘不够'); await r.wait(6500);
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
