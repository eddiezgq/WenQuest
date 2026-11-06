const { clip } = require('../../../_帮助生成/rec/vrec.js'); const D = __dirname;
clip(D + '/out', D + '/voice', 'web-04-case-thin', async (r) => {
  const p = r.p;
  await r.open('/bearing/?example=demo-thin-x');
  await r.say('案例三：机器人腕关节的四点接触薄壁轴承，一个轴承同时扛径向力、轴向力和倾覆力矩。');
  await r.say('中间是每个钢球两条对角线的接触载荷，橙色向外、蓝色向内。');
  await r.say('现在的径向游隙是负十二微米，也就是预紧，所有钢球都保持接触。');
  await r.num('径向游隙 Gr', -4); await r.wait(1500);
  await r.say('预紧减小到负四微米：有对角线在载荷下脱开，预紧不脱开这一项判不合格。');
  await r.num('径向游隙 Gr', -12); await r.wait(1500);
  await r.say('改回负十二微米。下面的预紧量曲线画出倾覆刚度和接触应力随游隙怎么变。');
  await p.locator('.setting').first().scrollIntoViewIfNeeded().catch(() => {}); await r.wait(2500);
  await r.say('四点接触还查接触椭圆不越过桃形沟中线。套圈按刚性计算，薄壁套圈实际会变形，刚度会更低。');
});
