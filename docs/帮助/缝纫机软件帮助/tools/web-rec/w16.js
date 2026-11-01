// 第 65 轮 案例七：多头刺绣机——8 mm 缎纹定转速、8 头还是 12 头、推力 1200 N、伺服选型、横梁模态、电控箱（38 °C、飞絮）
const { clip } = require('./rec.js');
const M = require('../../data/cases.json').embroid;        // 字幕里的数和帮助同一份（tools/run_cases.py --only embroid 真算）
const r0 = (x) => Math.round(Number(x));
clip('web-16-case-em', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click(), top = () => p.evaluate(() => scrollTo(0, 0));
  await r.sewing(); await p.locator('.mopt', { hasText: '多头刺绣机' }).click(); await r.wait(3000);
  r.cut(true);
  await r.param('基本参数', '最长针长', 8); await r.param('断线与产能', '花样针数', 12000);
  r.cut(false);
  await tab('校核'); await top(); await r.wait(1200);
  r.cue(`案例七：logo 花样 1.2 万针、8 mm 缎纹边，8 头机 650 r/min——最长那一针走不完，红灯（可用 / 所需 ${M.h8.res['可用加速度 / 最长针所需']}）`); await r.wait(6500);
  await r.param('基本参数', '设计转速', 640); await tab('校核'); await top(); await r.wait(800);
  r.cue(`这一针定了转速上限 ${r0(M.h8.limit)} r/min；改 640 全部合格，每小时 ${M.h8_640.per_h} 件，这张订单 ${M.h8_640.days} 天`); await r.wait(6000);
  await tab('零件与制造'); await r.wait(1500);
  const sp = p.getByText('针长与转速').first(); await sp.scrollIntoViewIfNeeded().catch(() => {}); await r.wait(600);
  r.cue('“针长与转速”表：缎纹窄到 6 mm 就能上 740 r/min——制版和机器设计之间的取舍'); await r.wait(6000);
  await r.param('基本参数', '头数', 12); await r.param('基本参数', '设计转速', 650);
  await tab('校核'); await top(); await r.wait(1000);
  r.cue(`换 12 头：绷架 ${r0(M.h12.mass)} kg，转速上限掉到 ${r0(M.h12.limit)}；断线一次十二个头一起停，效率 ${M.h12.eff}——每小时仍有 ${M.h12.per_h} 件`); await r.wait(7000);
  await tab('零件与制造'); await r.wait(1200);
  const hd = p.getByText('头数与效率').first(); await hd.scrollIntoViewIfNeeded().catch(() => {}); await r.wait(600);
  r.cue('“头数与效率”表：头越多每小时越多，但每多一个头带来的越来越少'); await r.wait(5500);
  await r.param('绷架', 'Y 轴驱动力', 1200); await tab('校核'); await top(); await r.wait(1000);
  r.cue(`Y 轴驱动力 800 → 1200 N：上限 ${r0(M.h12_F1200.limit)} r/min，650 全部合格；每小时 ${M.h12_F1200.per_h} 件，订单 ${M.h12_F1200.days} 天（8 头 ${M.h8_640.days} 天）`); await r.wait(7000);
  await r.param('基本参数', '设计转速', 800); await tab('校核'); await top(); await r.wait(1000);
  r.cue(`再提到 800 r/min？这一针要 ${M.h12_800.res['设计转速下这一针需要的推力']} 的推力——红灯。先改花样，不是先提转速`); await r.wait(6000);
  await r.param('基本参数', '设计转速', 650);
  await tab('CAE 分析'); await r.wait(2500);
  const drv = p.locator('.cae .box', { hasText: '伺服电机选型' }).first(); await drv.scrollIntoViewIfNeeded();
  await drv.locator('.btn', { hasText: '电机选型' }).click(); await r.wait(2500);
  await drv.locator('.res').first().scrollIntoViewIfNeeded().catch(() => {}); await r.wait(500);
  r.cue(`伺服电机选型：12 头的绷架 ${r0(M.motor.mass)} kg、推力 ${M.motor.force} N，第一台合格的是 ${M.motor.pick}（8 头用 ${M.motor8.pick}）`); await r.wait(7000);
  // 横梁模态：打开 run_cases.py 算好的两次（列表新的在前：先是三根立柱，再是两根）
  const jobs = p.locator('.job', { hasText: '固有频率' });
  await jobs.nth(1).scrollIntoViewIfNeeded(); await jobs.nth(1).click(); await r.wait(3000);
  await p.getByText('移动一针的时间').last().scrollIntoViewIfNeeded({ timeout: 4000 }).catch(() => {}); await r.wait(500);
  r.cue(`简化横梁 4.2 m、两端立柱：${M.beam2.checks[0].value}，黄灯——下一针之前停不稳`); await r.wait(6500);
  await jobs.nth(0).scrollIntoViewIfNeeded(); await jobs.nth(0).click(); await r.wait(3000);
  await p.getByText('移动一针的时间').last().scrollIntoViewIfNeeded({ timeout: 4000 }).catch(() => {}); await r.wait(500);
  r.cue(`中间加一根立柱：${M.beam3.checks[0].value}，合格——加支撑比加厚截面有效`); await r.wait(6000);
  const eb = p.locator('.ebox'); await eb.scrollIntoViewIfNeeded(); await r.wait(1500);
  r.cue(`电控箱：主轴 + 绷架 X / Y 三台驱动，平均 ${M.ebox.Pavg} W；40 °C 车间散热器 ${r0(M.ebox.Ths)} °C、结温 ${r0(M.ebox.Tj)} °C`); await r.wait(6000);
  const ep = async (grp, label, v) => {
    const g = eb.locator('.grp', { hasText: grp }).first();
    if (!(await g.locator('.prm').count())) { await g.locator('.gt').click(); await r.wait(300); }
    const inp = g.locator('.prm', { hasText: label }).locator('input').last();
    await inp.scrollIntoViewIfNeeded(); await inp.click(); await inp.fill(String(v)); await inp.press('Enter'); await inp.blur(); await r.wait(1500);
  };
  await ep('工况', '车间温度', 38); await ep('散热', '飞絮堵塞', 0.3);
  await eb.locator('.chk').first().scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue(`夏天 38 °C、飞絮堵塞 0.3：结温 ${r0(M.ebox38.Tj)} °C 超上限，开关时间也出了窗口——红灯`); await r.wait(6000);
  await eb.locator('.tbl').nth(1).scrollIntoViewIfNeeded(); await r.wait(500);
  r.cue('改进方案：加散热面积、加风扇、定期清理，单做一条都能消掉红灯；只降起停电流不够'); await r.wait(7000);
  await tab('导出'); await r.wait(1500);
  r.cue(`导出计算书、参数表、调机卡：12 头、推力 1200 N，交期 ${M.h12_F1200.days} 天`); await r.wait(5000);
});
