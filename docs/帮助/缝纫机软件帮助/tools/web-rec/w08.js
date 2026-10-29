const { clip } = require('./rec.js');
clip('web-08-export', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p;
  await r.sewing(); await r.wait(1500);
  r.cue('先让 AI 写设计说明，放进计算书'); await p.locator('.ai .bar').click(); await r.wait(800); await p.getByText('写设计说明').click(); await r.wait(3000);
  await p.getByText('放进计算书').click(); await r.wait(2000);
  r.cue('“导出”页签：计算书、调机卡、参数表、STEP、FreeCAD 宏、DXF、参数文件'); await p.locator('.exp').first().scrollIntoViewIfNeeded(); await r.wait(4000);
  r.cue('勾着“计算书带上设计说明”，点“设计计算书”下载 Word'); await p.locator('.exp').first().click(); await r.wait(4000);
  r.cue('再下一个三维模型（STEP），任何 CAD 都能打开'); await p.locator('.exp', { hasText: 'STEP' }).first().click(); await r.wait(4000);
  r.cue('最下面是 FreeCAD 工作台安装包'); await p.locator('.fc').scrollIntoViewIfNeeded(); await r.wait(4000);
});
