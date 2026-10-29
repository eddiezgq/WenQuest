// 第 52 轮 案例一：平缝机提速到 6000 r/min——红灯、改两处、零件复核、电机选型（零件库补一台高速伺服）、导出
const { clip } = require('./rec.js');
clip('web-09-case-ls', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click();
  // 幕后准备：确保零件库里还没有示例电机
  for (const x of (await r.api('GET', '/api/v1/sewing/parts?q=SV-3000H')).parts || []) await r.api('DELETE', `/api/v1/sewing/parts/${x.id}`);
  await r.sewing(); await tab('校核'); await r.wait(1500);
  r.cue('案例一：教材算例平缝机，5000 r/min，21 项校核全部合格'); await r.wait(4000);
  r.cue('客户要 6000 r/min：“最高转速”改成 6000'); await r.param('基本参数', '最高转速', 6000); await r.wait(1500);
  r.cue('两盏红灯：针杆惯性力超过轴套允许值；二阶激振频率逼近机壳固有频率（共振）'); await r.wait(6000);
  r.cue('改法一：针杆组件减到 0.10 kg（轻的针杆、针夹）'); await r.param('刺布机构', '针杆组件质量', 0.1); await r.wait(3000);
  r.cue('改法二：机壳一阶固有频率提到 240 Hz（机臂加筋、加厚）'); await r.param('平衡与机壳', '机壳一阶固有频率', 240); await r.wait(2000);
  r.cue('重算：21 项全部合格'); await p.evaluate(() => scrollTo(0, 0)); await r.wait(4500);
  await tab('CAE 分析'); await r.wait(3000);
  const box = p.locator('.cae .box', { hasText: '零件强度' }).first();
  r.cue('零件还行吗？针杆曲柄按 6000 r/min 的受力重新做有限元与疲劳'); await box.locator('.opt', { hasText: '针杆曲柄' }).click(); await r.wait(1200);
  await box.locator('.btn', { hasText: '提交计算' }).click(); await r.wait(2000);
  await r.job('lockstitch');
  r.cue('安全系数仍远大于 2，疲劳寿命 > 1000 年：零件不用改'); await r.wait(6000);
  const drv = p.locator('.cae .box', { hasText: '机构动力学' }).first(); await drv.scrollIntoViewIfNeeded();
  r.cue('电机呢？点“电机选型”'); await drv.locator('.btn', { hasText: '电机选型' }).click(); await r.wait(2500);
  await drv.locator('.res').first().scrollIntoViewIfNeeded().catch(() => {});
  r.cue('表里没有够用的：转矩够的只到 5000 r/min，转得到 6000 的额定转矩又不够'); await r.wait(7000);
  // 幕后：把一台示例高速主轴伺服录进本单位零件库（入库办法见“本单位零件库”一节的录屏）
  r.cut(true);
  await r.api('POST', '/api/v1/sewing/parts', { cat: 'motor', code: 'SV-3000H', name: '高速主轴伺服 3 kW（示例）', confirm: true,
    fields: { power_w: 3000, rated_nm: 4.8, peak_nm: 14.4, rated_rpm: 6000, max_rpm: 7000, inertia: 3.0 } });
  await tab('零件库'); await r.wait(3000); r.cut(false);
  r.cue('这就是本单位零件库的用处：录进供应商的高速主轴伺服（示例 SV-3000H，最高 7000 r/min）'); await r.wait(6000);
  await tab('CAE 分析'); await r.wait(2500); await drv.scrollIntoViewIfNeeded();
  r.cue('再点“电机选型”：推荐的就是本单位库里的这台'); await drv.locator('.btn', { hasText: '电机选型' }).click(); await r.wait(2500);
  await drv.locator('.res').first().scrollIntoViewIfNeeded().catch(() => {}); await r.wait(6500);
  await tab('导出'); await p.evaluate(() => scrollTo(0, 0)); await r.wait(1500);
  r.cue('出件进工厂：计算书、调机卡、参数表、STEP、FreeCAD 宏、DXF，同一组参数一次导出'); await r.wait(7000);
  for (const x of (await r.api('GET', '/api/v1/sewing/parts?q=SV-3000H')).parts || []) await r.api('DELETE', `/api/v1/sewing/parts/${x.id}`);
});
