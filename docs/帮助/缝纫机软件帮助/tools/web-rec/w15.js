// 第 62 轮 案例六：电控箱夏天频繁报过热——电流从设计来、夏天 38 °C + 飞絮、改进方案、AI 一句话、CAE 复核结果
const { clip } = require('./rec.js');
const EB = require('../../data/cases.json').ebox;          // 字幕里的数和帮助同一份（tools/run_cases.py --only ebox 真算）
const f1 = (x) => Number(x).toFixed(1).replace(/\.0$/, ''), r0 = (x) => Math.round(Number(x));
clip('web-15-case-eb', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click();
  await r.sewing(); await p.getByText('恢复教材算例参数').click(); await r.wait(1200);
  r.cut(true);
  await r.param('基本参数', '最高转速', 6000); await r.param('刺布机构', '针杆组件质量', 0.1); await r.param('平衡与机壳', '机壳一阶固有频率', 240);
  await r.wait(800); r.cut(false);
  r.cue('案例一的 6000 r/min 改型（针杆 0.10 kg、机壳 240 Hz），全部合格'); await r.wait(3000);
  await tab('CAE 分析'); await r.wait(2500);
  const eb = p.locator('.ebox'); await eb.scrollIntoViewIfNeeded(); await r.wait(800);
  r.cue(`“CAE 分析 → 电控箱”：主轴伺服 ${EB.base.Irun} A 按这台设计算出来；40 °C 车间散热器 ${r0(EB.base.Ths)} °C、结温峰值 ${r0(EB.base.Tj)} °C`); await r.wait(6000);
  await eb.locator('.chk').first().scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue('只有一盏黄灯：飞絮堵塞到 0.3 就会超——余量并不大'); await r.wait(4500);
  await p.getByText('教材 18.7 节').scrollIntoViewIfNeeded(); await p.getByText('教材 18.7 节').click(); await r.wait(1500);
  await eb.scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue(`夏天午后 38 °C、散热片糊了一层飞絮（堵塞 0.5）：散热器 ${r0(EB.summer.Ths)} °C 报过热，结温 ${r0(EB.summer.Tj)} °C 超上限`); await r.wait(6000);
  await eb.locator('.charts').scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue('曲线：间歇缝纫时结温在每次起停跳一下；飞絮越多越热；电容每热 10 °C 寿命减半'); await r.wait(6000);
  await eb.locator('.tbl').nth(1).scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue('改进方案对照：加散热、加风扇、限电流单用都消不掉红灯；定期清理一条就消掉全部红灯'); await r.wait(6500);
  const ai = eb.locator('.ainp'); await ai.scrollIntoViewIfNeeded();
  await r.type(ai.locator('input').first().count ? ai.locator('input').first() : ai, '车间夏天 40 度，飞絮堵塞 0.3，会不会报过热');
  await eb.getByText('AI 起草').click(); await r.wait(2500);
  r.cue('也可以一句话问：AI 改环境参数，计算核心重算，红灯照实列出，点“采用”才填进去'); await r.wait(5500);
  // CAE 复核：打开已经算完的那一个（清理以后、没有翅片；列表第二个——第一个是加了翅片的那次）
  const job = p.locator('.job', { hasText: '电控箱' }).nth(1); await job.scrollIntoViewIfNeeded(); await job.click(); await r.wait(3000);
  await p.locator('.res .kgrid').last().scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue(`CAE 复核（清理以后）：自然对流算外壳每个面的散热系数，再算温度场——箱子热阻 ${EB.cae.R_cae.toFixed(3)}，和公式 ${EB.cae.R_geo.toFixed(3)} 对得上`); await r.wait(7000);
  r.cue(`顶面只有 ${EB.cae.h_top}、侧面约 ${EB.cae.h_side} W/(m²·K)：顶面泡在热空气里；加 10 片顶面翅片热阻只降 ${r0((1 - EB.cae_fins.R_cae / EB.cae.R_cae) * 100)}%`); await r.wait(7000);
  r.cue(`代回公式：38 °C 下散热器 ${r0(EB.cae.with_cae.Ths)} °C、结温 ${r0(EB.cae.with_cae.Tjpk)} °C、电容 ${f1(EB.cae.with_cae.life_y)} 年；计算书、参数表都多了“电控箱”一节`); await r.wait(6000);
});
