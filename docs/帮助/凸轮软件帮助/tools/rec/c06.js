const { clip } = require('../../../_帮助生成/rec/vrec.js'); const D = __dirname;
clip(D + '/out', D + '/voice', 'web-06-cyl', async (r) => {
  const p = r.p;
  await r.open('/cam/?example=barrel-feed');
  await r.say('圆柱凸轮：自动机送料凸轮，锥形滚子在槽里走，参数是虚构的。');
  await r.say('压力角按槽底算，因为槽底那里最大。推程三十点四度，回程三十四点一度，限值三十五度。');
  await p.getByRole('button', { name: '槽展开图' }).click(); await r.wait(1500);
  await r.say('槽展开图把圆柱面摊平，看得清槽的走向和每段的转角。');
  await p.getByRole('button', { name: '三维', exact: true }).click(); await r.wait(1000);
  await p.locator('nav.modes button', { hasText: '制造' }).click(); await r.wait(2500);
  await r.say('制造页是四轴加工：回转工作台转毛坯，刀具和滚子一样大，沿滚子轴线走一遍就是槽。');
  await p.getByRole('button', { name: '生成程序并仿真' }).click(); r.cut(true); await p.getByRole('button', { name: '生成程序并仿真' }).waitFor({ timeout: 120000 }); await r.wait(1500); r.cut(false);
  await r.say('程序读回来让刀具扫过毛坯，再和精确槽侧面比法向偏差。');
});
