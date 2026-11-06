// 第 95 轮重录（带配音）：六种机型的样机都跟设计走——平缝机旋梭定时调错、试缝跳针；包缝机下弯针偏心加大，慢放到出问题的转角
const { clip } = require('./rec.js');
clip('web-02-proto', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click();
  await r.sewing(); await p.getByText('恢复教材算例参数').click(); await r.settle(400);
  await r.frameTop(); await r.wait(1500);
  await r.say('“样机”页签：六种机型的三维样机都跟着设计走，改一个参数，样机马上换成这台设计。', 800);
  await r.say('平缝机：把旋梭定时调错到负 20 度，旋梭来得太早。');
  await r.param('钩线机构', '旋梭定时', -20); await r.settle(); await p.getByText('不合格 2 项').waitFor({ timeout: 120000 }).catch(() => console.log('WAITFAIL')); await r.wait(2000); await r.frameTop(); await r.wait(800);
  await r.say('样机跟着变了：钩线提前，针回升得还不够，旋梭尖就到了。', 1000);
  await tab('校核'); await r.wait(1000); await p.locator('.trial').scrollIntoViewIfNeeded(); await r.wait(600);
  await r.say('“校核”页签：30 针虚拟试缝全部跳针，钩线两项变红。', 800);
  await r.param('钩线机构', '旋梭定时', 0); await r.settle(); await p.getByText('全部 21 项校核合格').waitFor({ timeout: 120000 }).catch(() => console.log('WAITFAIL')); await r.wait(2000); await p.locator('.trial').scrollIntoViewIfNeeded(); await r.wait(600);
  await r.say('改回 0 度，30 针全部成缝。', 600);
  await p.getByText('包缝机', { exact: true }).first().click(); await r.settle(400); await tab('样机'); await r.wait(800);
  await r.frameTop(); await r.wait(1500);
  await r.say('包缝机也一样。把下弯针的偏心半径从 4.4 毫米改到 8 毫米。');
  await r.param('下弯针', '偏心半径', 8); await r.settle(); await p.getByText('注意 5 项').waitFor({ timeout: 120000 }).catch(() => console.log('WAITFAIL')); await r.wait(3000); await r.frameTop(); await r.wait(1200);
  const f = p.frameLocator('iframe.proto'); await f.locator('#gobad').scrollIntoViewIfNeeded(); await r.wait(800);
  await r.say('下弯针四项变黄，加上原来就有的上弯针一项，样机右边列出每一项出问题的转角。', 600);
  await f.locator('#gobad').click(); await r.wait(600); await r.proto(() => scrollTo({ top: 0, behavior: 'smooth' })); await r.wait(900);
  await r.say('点“慢放到出问题的转角”：自动切到透视、成缝区特写，停在下弯针摆到最远的 104 度，下弯针标黄。', 1500);
  await r.say('花样机、刺绣机、横机按针、按趟走，停在出问题的那一针、那一趟，见案例四、五、七。', 800);
  await p.getByText('恢复教材算例参数').click(); await r.wait(800);
});
