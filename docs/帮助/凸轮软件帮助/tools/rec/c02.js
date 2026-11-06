const { clip } = require('../../../_帮助生成/rec/vrec.js'); const D = __dirname;
clip(D + '/out', D + '/voice', 'web-02-mfg', async (r) => {
  const p = r.p;
  await r.open('/cam/?example=sewing-takeup-groove&mode=mfg');
  await r.say('制造页：选加工方式，磨削、铣削或者慢走丝。机床设置是示例值，要按本厂设备改。');
  await r.say('填上砂轮半径四毫米。');
  await r.num('砂轮半径', 4); r.cut(true); await r.wait(2500); r.cut(false);
  await r.say('软件马上出磨削程序，并用程序反过来仿真：法向偏差一点零三微米，在一点一微米以内。');
  await p.getByRole('button', { name: '▶ 播放' }).click();
  await r.say('播放能看到砂轮沿槽走一圈。凹处曲率半径大于砂轮半径，不会过切。');
  await p.getByRole('button', { name: '❚❚ 暂停' }).click();
  await r.smooth(500);
  await r.say('下面是程序全文，开头注明示例数据和机床设置。');
  await r.smooth(-500);
  await r.say('右边可以下载加工程序、廓线 DXF、点表、STEP 三维模型和 FreeCAD 工作台。');
});
