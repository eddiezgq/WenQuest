// 第 95 轮：fc-09-video 的后半段——FreeCAD“在浏览器里打开”的那个网页（网址由 fc95.py 写在 WQ_URLFILE），
// 等关键画面出好再录（不录等待），出片后接在 FreeCAD 那一段后面（join95.sh）
const fs = require('fs');
const { clip } = require('./rec.js');
const url = fs.readFileSync(process.env.WQ_URLFILE, 'utf8').trim().replace(/^https?:\/\/[^/]+/, 'http://localhost:8088');
async function waitStills() {
  const id = new URL(url).searchParams.get('id');
  const tok = (await (await fetch('http://localhost:8090/api/v1/auth/login', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ username: 'teacher1', password: 'Test#2026' }) })).json()).token;
  for (let i = 0; i < 300; i++) {
    const d = await (await fetch('http://localhost:8090/api/v1/video3d/' + id, { headers: { authorization: 'Bearer ' + tok } })).json();
    if (d.stills && d.stills.state === 'done') return; if (d.stills && d.stills.state === 'failed') throw new Error('stills failed: ' + d.stills.error);
    await new Promise((r) => setTimeout(r, 3000));
  }
}
(async () => {
  await waitStills();
  await clip('fc-09-web', 'teacher1', 'Test#2026', async (r) => {
    const p = r.p;
    await p.goto(url); await r.wait(4000); await r.settle(0);
    await r.say('浏览器里打开的就是这段视频的页面，用同一个账号登录：关键画面出好了。', 1200);
    await r.say('在这里看关键画面、提意见修改、出小样和高清、下载视频；片子记在钥匙主人名下，网页版“三维视频”里也找得到。', 1500);
  });
})();
