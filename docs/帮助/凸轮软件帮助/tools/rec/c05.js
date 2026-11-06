const { clip } = require('../../../_帮助生成/rec/vrec.js'); const D = __dirname;
clip(D + '/out', D + '/voice', 'web-05-3d-cae', async (r) => {
  const p = r.p;
  await r.open('/cam/?example=atc-globoidal&mode=sys3d'); await r.wait(1500);
  await r.say('三维与制造：整套机构动起来。弧面凸轮按加工方法生成，可以下载四轴加工程序和 STEP。');
  await p.locator('canvas').first().hover();
  await p.mouse.down(); for (let i = 0; i < 20; i++) { await p.mouse.move(640 + i * 8, 360, { steps: 2 }); await r.wait(30); } await p.mouse.up();
  await r.say('鼠标拖动旋转，滚轮缩放。');
  await p.locator('nav.modes button', { hasText: 'CAE 分析' }).click(); await r.wait(2500);
  await r.say('CAE 分析页：换刀臂的有限元强度、固有频率和疲劳，以及整机多体动力学。');
  await r.say('示例结果：最大应力三十一点九兆帕，安全系数十六点九，第一阶固有频率七百九十一赫兹。');
  await r.smooth(400);
  await r.say('多体动力学算的凸轮轴转矩，和本软件的解析结果对照，峰值相差约百分之一。');
  await r.say('新的计算要提交到计算服务排队，接上之后才能用。');
});
