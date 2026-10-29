const { clip } = require('./rec.js');
clip('web-06-lib', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p;
  await r.sewing(); await p.locator('.tab', { hasText: '零件库' }).click(); await r.wait(2500);
  r.cue('“零件库”：本单位自己的库，同单位共享，别的单位看不见'); await p.locator('.lib').scrollIntoViewIfNeeded(); await r.wait(3500);
  r.cue('手填：选类别“伺服 / 主轴电机”，填参数（带 * 的必填）'); await p.getByText('新增零件').click(); await r.wait(600);
  await p.locator('.detail .opt', { hasText: '伺服 / 主轴电机' }).click();
  const F = (l) => p.locator('.detail .f', { hasText: l }).locator('input');
  await p.locator('.detail').scrollIntoViewIfNeeded();
  for (const [l, v] of [['本单位编号', 'SV-750'], ['名称', '750 W 交流伺服'], ['ERP', 'MOT-0750'], ['额定功率', '750'], ['额定转矩', '2.39'], ['峰值转矩', '8.36'], ['额定转速', '3000'], ['最高转速', '6000'], ['转子惯量', '1.6'], ['法兰边长', '80'], ['机身长', '120'], ['轴径', '19']]) await r.type(F(l), v);
  r.cue('保存：自动生成示意外形（STEP），拖动可以转'); await p.locator('.detail .btn', { hasText: '保存' }).click(); await r.wait(4000);
  await p.locator('.view3d').scrollIntoViewIfNeeded().catch(() => {}); await r.wait(4500);
  r.cue('表格批量：一张 Excel 一族零件；先逐行检查，全对才入库'); await p.locator('.lib').scrollIntoViewIfNeeded(); await p.getByText('表格批量（零件族）').click(); await r.wait(800);
  await p.locator('.box .opt', { hasText: '曲柄 / 连杆' }).click(); await r.wait(600);
  const [fc] = await Promise.all([p.waitForEvent('filechooser'), p.getByText('上传填好的表').click()]);
  await fc.setFiles(__dirname + '/links2.xlsx'); await r.wait(3500);
  r.cue('检查通过，确认入库：每个规格自动生成三维'); await p.getByText(/确认入库/).click(); await r.wait(4500);
  await p.mouse.wheel(0, 500); await r.wait(3500);
});
