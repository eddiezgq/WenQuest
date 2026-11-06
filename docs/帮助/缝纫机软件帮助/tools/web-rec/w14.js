// 第 95 轮重录（带配音）：花样机 2000 r/min 未改那一版（有红灯）——导出 → 出三维讲解片（配旁白）→ 关键画面；
// 分 a、b 两段录，出片时接上，片尾再接这台设计出的配旁白小样开头一段（join95.sh，小样在 docs/截图/第90轮-讲解片配音/）
const { clip } = require('./rec.js');
let url = '';
const partA = () => clip('web-14-video-a', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p, tab = (t) => p.locator('.tab', { hasText: t }).click();
  await r.sewing(); await p.getByText('电子花样机', { exact: true }).first().click(); await r.settle(400);
  await p.getByText('恢复教材算例参数').click(); await r.settle(400);
  await r.say('花样机把设计转速提到 2000 r/min，先不改别的。');
  await r.param('基本参数', '设计缝纫转速', 2000); await r.settle(); await p.getByText(/不合格 [1-9]/).waitFor({ timeout: 120000 }).catch(() => console.log('WAITFAIL')); await r.wait(1500); await r.wait(600);
  await tab('校核'); await r.wait(1200);
  await r.say('校核里有红灯：标准针距走不完。', 800);
  await tab('导出'); await p.evaluate(() => scrollTo(0, 0)); await r.wait(800);
  const box = p.locator('.fc', { hasText: '三维讲解片' }).first(); await box.scrollIntoViewIfNeeded(); await r.wait(600);
  await r.say('“导出”页签的“出三维讲解片”：按这台的花样、每针转速和运动自动写好讲解片，不用写一句话。', 600);
  await r.say('“配旁白”默认勾上：念画面上的标题和字幕，旁白长的段落放慢拉长，不抢话。', 600);
  await box.locator('.btn').first().click(); await p.waitForURL(/video3d/, { timeout: 600000 }); await r.wait(3000);
  url = p.url();
});
// 关键画面要出几分钟：这段不录（录得太久，无显卡的机器上画面时间会漂），出好以后另录一段打开这个页面，出片时接上（join95.sh）
async function waitStills() {
  const id = new URL(url).searchParams.get('id');
  const tok = (await (await fetch('http://localhost:8090/api/v1/auth/login', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ username: 'teacher1', password: 'Test#2026' }) })).json()).token;
  for (let i = 0; i < 300; i++) {
    const d = await (await fetch('http://localhost:8090/api/v1/video3d/' + id, { headers: { authorization: 'Bearer ' + tok } })).json();
    if (d.stills && d.stills.state === 'done') return; if (d.stills && d.stills.state === 'failed') throw new Error('stills failed: ' + d.stills.error);
    await new Promise((r) => setTimeout(r, 3000));
  }
}
const partB = () => clip('web-14-video-b', 'teacher1', 'Test#2026', async (r) => {
  const p = r.p;
  await p.goto(url.replace(/^https?:\/\/[^/]+/, 'http://localhost:8088')); await r.wait(4000); await r.settle(0);
  await r.say('跳到“三维视频”页：整机、各机构，再把红黄灯慢放到出问题的那一针；几分钟后关键画面出好。', 600);
  await r.say('关键画面：机构照教材模型，尺寸是示意；针迹、每针转速和读数是这台设计自己的数。', 1200);
  const n = await p.locator('.stills .img').count();
  await p.locator('.stills .img').nth(Math.min(n - 1, 4)).click(); await r.wait(800);
  await r.say('红灯那一段：停在最紧的那一针，标题标红，字幕写数值和判据。', 1500);
  await p.keyboard.press('Escape'); await r.wait(300);
  if (await p.locator('.uni-preview-image, uni-preview-image').count()) { await p.mouse.click(640, 360); await r.wait(600); }
  await r.say('看过再出小样、高清，旁白合成进视频；左边可以让 AI 改镜头、节奏和字幕，设计参数和数值改不了。', 800);
  await r.say('下面是这台设计出的小样，开头一段。', 300);
});
(async () => { await partA(); await waitStills(); await partB(); })();
