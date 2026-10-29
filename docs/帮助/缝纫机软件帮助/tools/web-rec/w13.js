// 第 54 轮 案例五：电脑横机——E18 选针跟不上、多段选针；不补偿；一趟的时间分配；改进方案；两系统电机红灯；设计优化；伺服选型
const { clip } = require('./rec.js');
clip('web-13-case-fk', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click(), top = () => p.evaluate(() => scrollTo(0, 0));
  await r.sewing(); await p.locator('.mopt', { hasText: '电脑横机' }).click(); await r.wait(3000); await tab('校核'); await r.wait(1500);
  r.cue('案例五：E12 横机织一片 275 针的前片（教材 17.8 节），10 项校核全部合格'); await r.wait(5000);
  r.cue('机号改成 18：每枚针只剩 1.18 ms，选针器一次要 1.2 ms——红灯'); await r.param('基本参数', '机号', 18); await top(); await r.wait(6000);
  r.cue('办法之一：选针器分两段，相邻的针分开选——又全部合格'); await r.param('选针', '选针器段数', 2); await top(); await r.wait(5000);
  await p.getByText('恢复教材算例参数').click(); await r.wait(1500);
  r.cue('提前量不补偿：选针器延迟 0.6 ms，全速时滞后 0.34 个针距——红灯'); await r.choose('选针', '提前量补偿', '不补偿'); await top(); await r.wait(6000);
  await p.getByText('恢复教材算例参数').click(); await r.wait(1500);
  await tab('时序与曲线'); r.cue('一趟 0.90 秒，真正在织物上选针编织的只占一半多；其余是加减速、换向余量和停顿'); await r.wait(7000);
  await tab('零件与制造'); await p.locator('.tbl').first().scrollIntoViewIfNeeded().catch(() => {});
  r.cue('改进方案对照：实时补偿快 10%，加一个系统快 31%，提速 1/3 只快 8%'); await r.wait(7500);
  await tab('校核'); await top();
  r.cue('只改成两系统、实时补偿：机头重了，电机发热超额定——红灯'); await r.param('基本参数', '系统数', 2); await r.choose('选针', '提前量补偿', '按实时速度'); await top(); await r.wait(6000);
  await p.getByText('恢复教材算例参数').click(); await r.wait(1500);
  await tab('CAE 分析'); await r.wait(2500);
  const opt = p.locator('.cae .box', { hasText: '设计优化' }).first(); await opt.scrollIntoViewIfNeeded();
  r.cue('设计优化：一片用时最短，补偿方式 × 系统数逐个试，不许出红灯'); await opt.locator('.opt').first().click(); await r.wait(5000);
  r.cue('最好的一组：两系统、实时补偿、1.55 m/s、加速度降到 6.5——一片 6.8 分钟，快四成。点“采用”'); await r.wait(6000);
  await opt.locator('.btn', { hasText: '采用' }).first().click(); await r.wait(2000);
  const drv = p.locator('.cae .box', { hasText: '伺服电机选型' }).first(); await drv.scrollIntoViewIfNeeded();
  r.cue('伺服电机选型：原来的 1 kW 发热只剩 3% 余量，按 1.2 倍余量推荐 1.5 kW'); await drv.locator('.btn', { hasText: '电机选型' }).click(); await r.wait(2500);
  await drv.locator('.res').first().scrollIntoViewIfNeeded().catch(() => {}); await r.wait(6500);
  await tab('校核'); await top(); r.cue('采用后全部合格'); await r.wait(4000);
});
