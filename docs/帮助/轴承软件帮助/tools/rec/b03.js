const { clip } = require('../../../_帮助生成/rec/vrec.js'); const D = __dirname;
clip(D + '/out', D + '/voice', 'web-03-case-taper', async (r) => {
  const p = r.p;
  await r.open('/bearing/?example=scene-tapered-pair');
  await r.say('案例二：减速器中间轴两端的圆锥滚子轴承，面对面安装，冷态调了正二十微米的游隙。');
  await p.locator('fieldset', { hasText: '配合与温度' }).first().scrollIntoViewIfNeeded(); await r.wait(800);
  await r.say('配合与温度里填调整时温度、内外圈和轴、座的温度，以及三个线膨胀系数。系数按实际材料填，软件不替你假定。');
  await p.locator('aside.side').hover(); await r.smooth(700);
  await r.say('工作时的轴向游隙变成负十四点九微米，冷态的游隙热了变成预紧，每列大约八百一十牛。');
  await r.say('说明里逐项列出：内外圈温差，加上轴与轴承座的轴向伸长。');
  await r.pick('安装方式', 'DB').catch(async () => { await p.locator('select').filter({ hasText: '背对背' }).first().selectOption('DB'); });
  await r.wait(1500);
  await r.say('改成背对背，轴向伸长反过来使游隙变大，工作时还剩正二十八微米。');
  await r.say('选哪种、冷态调多少，看下面的调整量曲线，按企业自己的判据定。');
  await p.locator('.setting').first().scrollIntoViewIfNeeded().catch(() => {}); await r.wait(2500);
});
