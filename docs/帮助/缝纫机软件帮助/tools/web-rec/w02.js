const { clip } = require('./rec.js');
clip('web-02-proto', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p;
  await r.sewing(); await r.wait(4000);
  r.cue('“样机”页签：教材的平缝机三维虚拟样机，调机参数跟着设计同步'); await p.locator('.frame').scrollIntoViewIfNeeded(); await r.wait(5000);
  r.cue('把旋梭定时调错：−20°（旋梭来得太晚）'); await r.param('钩线机构', '旋梭定时', -20); await r.wait(2500);
  await p.locator('.frame').scrollIntoViewIfNeeded(); r.cue('样机里同步了：钩线时机不对'); await r.wait(5000);
  r.cue('“校核”页签：30 针虚拟试缝全部跳针，钩线两项变红'); await p.locator('.tab', { hasText: '校核' }).click(); await r.wait(1200);
  await p.locator('.trial').scrollIntoViewIfNeeded(); await r.wait(4500);
  r.cue('改回 0°，试缝 30 针全部成缝'); await r.param('钩线机构', '旋梭定时', 0); await p.locator('.tab', { hasText: '校核' }).scrollIntoViewIfNeeded(); await r.wait(4000);
});
