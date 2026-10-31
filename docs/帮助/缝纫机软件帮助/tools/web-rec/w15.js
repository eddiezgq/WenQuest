// 第 62 轮 案例六：电控箱夏天频繁报过热——电流从设计来、夏天 38 °C + 飞絮、改进方案、AI 一句话、CAE 复核结果
const { clip } = require('./rec.js');
clip('web-15-case-eb', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click();
  await r.sewing(); await p.getByText('恢复教材算例参数').click(); await r.wait(1200);
  r.cut(true);
  await r.param('基本参数', '最高转速', 6000); await r.param('刺布机构', '针杆组件质量', 0.1); await r.param('平衡与机壳', '机壳一阶固有频率', 240);
  await r.wait(800); r.cut(false);
  r.cue('案例一的 6000 r/min 改型（针杆 0.10 kg、机壳 240 Hz），全部合格'); await r.wait(3000);
  await tab('CAE 分析'); await r.wait(2500);
  const eb = p.locator('.ebox'); await eb.scrollIntoViewIfNeeded(); await r.wait(800);
  r.cue('“CAE 分析 → 电控箱”：主轴伺服 3.67 A 按这台设计算出来；40 °C 车间散热器 86 °C、结温峰值 114 °C'); await r.wait(6000);
  await eb.locator('.chk').first().scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue('只有一盏黄灯：飞絮堵塞到 0.3 就会超——余量并不大'); await r.wait(4500);
  await p.getByText('教材 18.7 节').scrollIntoViewIfNeeded(); await p.getByText('教材 18.7 节').click(); await r.wait(1500);
  await eb.scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue('夏天午后 38 °C、散热片糊了一层飞絮（堵塞 0.5）：散热器 115 °C 报过热，结温 142 °C 超上限'); await r.wait(6000);
  await eb.locator('.charts').scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue('曲线：间歇缝纫时结温在每次起停跳一下；飞絮越多越热；电容每热 10 °C 寿命减半'); await r.wait(6000);
  await eb.locator('.tbl').nth(1).scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue('改进方案对照：加散热、加风扇、限电流单用都消不掉红灯；定期清理一条就全消'); await r.wait(6500);
  const ai = eb.locator('.ainp'); await ai.scrollIntoViewIfNeeded();
  await r.type(ai.locator('input').first().count ? ai.locator('input').first() : ai, '车间夏天 40 度，飞絮堵塞 0.3，会不会报过热');
  await eb.getByText('AI 起草').click(); await r.wait(2500);
  r.cue('也可以一句话问：AI 改环境参数，计算核心重算，红灯照实列出，点“采用”才填进去'); await r.wait(5500);
  // CAE 复核：打开已经算完的那一个（清理 + 10 片翅片，自然对流 + 温度场）
  const job = p.locator('.job', { hasText: '电控箱' }).first(); await job.scrollIntoViewIfNeeded(); await job.click(); await r.wait(3000);
  await p.locator('.res .kgrid').last().scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue('CAE 复核（清理 + 10 片翅片）：自然对流算外壳每个面的散热系数，再算温度场——箱子热阻 0.487，和公式 0.493 对得上'); await r.wait(7000);
  r.cue('代回公式：38 °C 下散热器 87 °C、结温 115 °C、电容 11 年；计算书、参数表都多了“电控箱”一节'); await r.wait(6000);
});
