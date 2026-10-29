const { clip } = require('./rec.js');
clip('web-01-first', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p;
  await r.sewing();
  r.cue('这是问渠缝纫机设计软件：上面选机型，左边改参数，右边当场看结果'); await r.wait(3500);
  for (const [m, c] of [['包缝机', '包缝机：引针、上下弯针、差动送布、切刀'], ['电子花样机', '电子花样机：X / Y 伺服带着模板走，每针都要在机针离开布的窗口里走完'], ['平缝机', '回到平缝机（教材算例）']]) {
    r.cue(c); await p.locator('.mopt', { hasText: m }).click(); await r.wait(2200); }
  await p.locator('.tab', { hasText: '校核' }).click(); await r.wait(800);
  r.cue('教材算例：21 项校核全部合格（绿）'); await r.wait(2500);
  r.cue('把最高转速从 5000 提到 6000 r/min'); await r.param('基本参数', '最高转速', 6000); await r.wait(1500);
  r.cue('两盏红灯：针杆惯性力超了，二阶激振频率离机壳固有频率太近'); await p.mouse.wheel(0, 300); await r.wait(4000);
  r.cue('每项都写着数值、判据、出自第几讲，以及怎么改'); await r.wait(3000);
  await p.mouse.wheel(0, -300);
  r.cue('按提示：针杆组件减到 0.10 kg'); await r.param('刺布机构', '针杆组件质量', 0.1); await r.wait(1500);
  r.cue('机壳一阶固有频率提到 240 Hz（机壳加筋）'); await r.param('平衡与机壳', '机壳一阶固有频率', 240); await r.wait(1500);
  await p.evaluate(() => window.scrollTo(0, 0)); await r.wait(500);
  r.cue('又全部合格了。改参数、看红绿灯、按提示改——这就是基本用法'); await r.wait(4000);
});
