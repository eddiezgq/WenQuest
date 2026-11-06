const { clip } = require('../../../_帮助生成/rec/vrec.js'); const D = __dirname;
clip(D + '/out', D + '/voice', 'web-05-parts', async (r) => {
  const p = r.p;
  await r.open('/bearing/?example=demo-deep-groove');
  await r.say('零件图与三维：内圈、外圈、钢球各一张截面图，尺寸公差在企业填之前写未知。');
  await p.getByRole('button', { name: '零件图与三维' }).click(); r.cut(true); await r.wait(3000); r.cut(false);
  await r.smooth(400);
  await r.say('可以下载整套和单件的 STEP，以及截面 DXF。STEP 用开源几何内核读回检查过，实体有效、不干涉。');
  await r.smooth(400);
  await r.say('还可以下载 FreeCAD 工作台，在本机建精确实体、出工作图和工序简图。');
});
