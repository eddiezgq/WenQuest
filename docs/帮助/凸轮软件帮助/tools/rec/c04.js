const { clip } = require('../../../_帮助生成/rec/vrec.js'); const D = __dirname;
clip(D + '/out', D + '/voice', 'web-04-system', async (r) => {
  const p = r.p;
  await r.open('/cam/?example=atc-globoidal');
  await r.say('案例二：加工中心的凸轮式换刀机构，一根凸轮轴带弧面分度凸轮和槽凸轮，参数是虚构的。');
  await r.say('时序图上看两个动作的先后。联锁校核确认：换刀臂转动时不拔刀，拔刀时不转动。');
  await r.say('一次换刀一点零八秒。电机峰值转矩十七点九牛米，电机额定值没填，所以是未知。');
  await r.smooth(450);
  await r.say('停歇段残余振动：停下来时换刀臂端部还在晃两百五十二微米。');
  await r.say('点搜索运动规律与最高转速，每种运动规律都试一遍。');
  await p.getByRole('button', { name: '搜索运动规律与最高转速' }).click(); r.cut(true); await r.wait(8000); r.cut(false);
  await r.say('摆线和多项式规律振动更小，但弧面分度凸轮的压力角超了，只有修正正弦没有不合格。');
  await r.say('填上电机峰值转矩、最高转速和允许振动，还能算出满足它们的最高转速。');
});
