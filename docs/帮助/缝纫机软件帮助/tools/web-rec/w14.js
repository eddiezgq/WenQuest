// 第 56 轮：按设计尺寸一键出三维讲解片——6000 r/min 未改那一版（有红灯），导出 → 出三维讲解片 → 关键画面
const { clip } = require('./rec.js');
clip('web-14-video', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click();
  await r.sewing(); await p.getByText('恢复教材算例参数').click(); await r.wait(1500);
  r.cue('平缝机改到 6000 r/min，先不改别的'); await r.wait(2500);
  r.cut(true); await r.param('基本参数', '最高转速', 6000); await r.wait(1200); r.cut(false);
  await tab('校核'); r.cue('不合格 2 项、注意 1 项'); await r.wait(4500);
  await tab('导出'); await p.evaluate(() => scrollTo(0, 0)); await r.wait(800);
  const box = p.locator('.fc', { hasText: '三维讲解片' }).first(); await box.scrollIntoViewIfNeeded();
  r.cue('“导出”页签：“出三维讲解片”——按这台的尺寸和运动自动写好讲解片，不用写一句话'); await r.wait(5000);
  await box.locator('.btn').click();
  r.cue('跳到“三维视频”页：整机、各机构、三项红黄灯慢放、结论，一共 65 秒；先出关键画面'); await r.wait(5000);
  r.cut(true);
  for (let i = 0; i < 120; i++) { if (await p.locator('.stills .img').count()) break; await r.wait(2000); }
  await r.wait(2500); r.cut(false);
  r.cue('关键画面：零件就是导出 STEP 的那些，读数面板是这台设计自己的数'); await r.wait(5000);
  await p.locator('.stills .img').nth(2).click(); await r.wait(800);
  r.cue('红灯那一段：停在出问题的 180°（针最低点），标题标红，字幕写数值和判据'); await r.wait(6000);
  await p.keyboard.press('Escape'); await r.wait(300);
  if (await p.locator('.uni-preview-image, uni-preview-image').count()) { await p.mouse.click(640, 360); await r.wait(600); }
  r.cue('看过再出小样、高清；左边可以让 AI 改镜头、节奏、字幕——设计参数和数值改不了'); await r.wait(6000);
});
