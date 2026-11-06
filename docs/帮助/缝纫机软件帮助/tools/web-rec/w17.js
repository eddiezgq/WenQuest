// 第 95 轮新录（带配音）：花样机、刺绣机、横机的样机按针 / 按趟走，改坏一项，慢放到出问题的那一针 / 那一趟
const { clip } = require('./rec.js');
clip('web-17-proto-seq', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p;
  const mach = async (m) => { await p.getByText(m, { exact: true }).first().click(); await r.settle(400); await p.locator('.tab', { hasText: '样机' }).click(); await r.wait(600); await r.frameTop(); await r.wait(1500); };
  const showPanel = async () => { await p.frameLocator('iframe.proto').locator('#gobad').scrollIntoViewIfNeeded(); await r.wait(700); };
  const gobad = async () => {
    await p.frameLocator('iframe.proto').locator('#gobad').click(); await r.wait(600);
    await r.proto(() => scrollTo({ top: 0, behavior: 'smooth' })); await r.wait(900);
  };
  await r.sewing(); await p.getByText('恢复教材算例参数').click(); await r.wait(1000);
  await mach('电子花样机'); await p.getByText('恢复教材算例参数').click(); await r.settle(400);
  await r.proto(() => document.getElementById('play') && document.getElementById('play').click()); await r.wait(500);
  await r.say('电子花样机：样机按这台设计的花样一针一针走，每一针的转速也按这台设计。', 1500);
  await r.say('把设计转速从 1800 提到 2000 r/min。');
  await r.param('基本参数', '设计缝纫转速', 2000); await r.settle(); await p.getByText('不合格 1 项').waitFor({ timeout: 120000 }).catch(() => console.log('WAITFAIL')); await r.wait(3000); await r.frameTop(); await r.wait(800); await showPanel();
  await r.say('亮红灯：设计转速下标准针距走不完。', 400);
  await gobad();
  await r.say('点“慢放到出问题的那一针”：停在最紧的那一针，机针扎下时工作台还在走，机针和压框标红。', 1500);

  await mach('多头刺绣机'); await p.getByText('恢复教材算例参数').click(); await r.settle(400);
  await r.say('多头刺绣机：头数改成 12，Y 轴驱动力减到 300 牛。');
  await r.param('基本参数', '头数', 12); await r.settle(); await r.param('绷架', 'Y 轴驱动力', 300); await r.settle(); await p.getByText('不合格 1 项').waitFor({ timeout: 120000 }).catch(() => console.log('WAITFAIL')); await r.wait(3000); await r.frameTop(); await r.wait(800); await showPanel();
  await r.say('绷架变重、力又小，最长那一针在机针离布的窗口里走不完。', 400);
  await gobad();
  await r.say('慢放到那一针：绷架还没停，机针已经扎下，绷架标红。', 1500);

  await mach('电脑横机'); await p.getByText('恢复教材算例参数').click(); await r.settle(400);
  await r.say('电脑横机：机号从 12 改成 18 针每英寸，针更密，机头经过每枚针的时间更短。');
  await r.param('基本参数', '机号', 18); await r.settle(); await p.getByText('不合格 1 项').waitFor({ timeout: 120000 }).catch(() => console.log('WAITFAIL')); await r.wait(3000); await r.frameTop(); await r.wait(800); await showPanel();
  await r.say('选针时间不够，选针器来不及动作。', 400);
  await gobad();
  await r.say('慢放到出问题的那一趟：机头走最宽的一趟，选针器标红。', 1500);
  await p.getByText('恢复教材算例参数').click(); await r.settle(400); await p.getByText(/全部 \d+ 项校核合格/).waitFor({ timeout: 120000 }).catch(() => console.log('WAITFAIL')); await r.wait(2500); await r.frameTop(); await r.wait(1500);
  await r.say('改回合格的参数，红灯就灭。改设计、看样机、再改，直到全部合格。', 800);
});
