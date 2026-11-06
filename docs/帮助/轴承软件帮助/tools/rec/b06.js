const { clip } = require('../../../_帮助生成/rec/vrec.js'); const D = __dirname;
clip(D + '/out', D + '/voice', 'web-06-spc', async (r) => {
  const p = r.p;
  await r.open('/bearing/?mode=quality');
  await r.say('检测与 SPC 分两页：圆度与波纹度，控制图与过程能力。');
  await p.getByRole('button', { name: /合成数据/ }).first().click(); await r.wait(1500);
  await p.locator('.btns button.accent').first().click().catch(() => {}); r.cut(true); await r.wait(3000); r.cut(false);
  await r.smooth(300);
  await r.say('贴入圆度仪测的一圈轮廓，软件去掉偏心，给圆度和各阶谐波的幅值。这里用的是标明了的合成数据。');
  await r.smooth(-300);
  await p.getByRole('tab', { name: '控制图与过程能力' }).click(); await r.wait(1000);
  await p.getByRole('button', { name: /合成数据/ }).first().click(); await r.wait(1500);
  await p.locator('.btns button.accent').first().click().catch(() => {}); r.cut(true); await r.wait(3000); r.cut(false);
  await r.smooth(300);
  await r.say('控制图按子组大小自动选，用纳尔逊八条规则判异；填了规格限，才算过程能力。');
});
