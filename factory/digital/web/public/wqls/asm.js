// 第 172b 轮：G8.1 机头 19 步装配动画（index.html?asm=1 时载入）。
// 顺序、装入路径（离装好位置的一串偏移，mm）、每步的主轴转角都来自 tools/wqls/g81_assembly.py（proto.json 的 assembly），
// 那个程序沿同一路径每 2 mm 查一次和机壳、已装零件碰不碰，19 步都走通。
(async function () {
'use strict';
const W = window.__wq, $ = id => document.getElementById(id);
const PD = await fetch('proto.json').then(r => r.json());
const ST = PD.assembly;
const zh = W.LANG !== 'en';
const st = document.createElement('style');
st.textContent = `.asm{position:fixed;left:50%;transform:translateX(-50%);bottom:12px;width:min(720px,calc(100vw - 24px));background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 14px;z-index:3;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.asm .h{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}.asm .n{font:700 22px/1 ui-monospace,Menlo,monospace;color:var(--acc)}.asm b{font-size:15px}
.asm p{margin:4px 0 6px;font-size:12.5px;color:var(--mut);line-height:1.5;max-height:5.6em;overflow:auto}.asm .row{display:flex;gap:6px;align-items:center}
.asm .bar{flex:1;height:5px;border-radius:3px;background:var(--line);overflow:hidden}.asm .bar i{display:block;height:100%;background:var(--acc)}`;
document.head.appendChild(st);
const box = document.createElement('div'); box.className = 'asm'; document.body.appendChild(box);
document.body.classList.add('embed'); W.fit();
const seqParts = new Set(ST.flatMap(s => s.parts));
const STEP_T = 2.6, MOVE_T = 1.9;
let T = 0, play = true;
function render(k, u) {
  const s = ST[k];
  box.innerHTML = `<div class="h"><span class="n">${k + 1} / ${ST.length}</span><b>${s.step}</b><span class="mut" style="font-size:12px">φ ${s.phi}°${s.ok ? (zh ? ' · 路上不碰' : ' · clear path') : ''}</span></div>
   <p>${s.note}</p><div class="row"><button id="aPrev">◀</button><button id="aPlay">${play ? (zh ? '暂停' : 'Pause') : (zh ? '播放' : 'Play')}</button><button id="aNext">▶</button>
   <div class="bar"><i style="width:${(100 * (k + u) / ST.length).toFixed(1)}%"></i></div></div>`;
  $('aPrev').onclick = () => { T = Math.max(0, (k - 1) * STEP_T); lastK = -1; };
  $('aNext').onclick = () => { T = Math.min(ST.length - 1, k + 1) * STEP_T; lastK = -1; };
  $('aPlay').onclick = () => { play = !play; lastK = -1; };
}
function along(path, u) {                               // 沿折线走，u 0→1（按长度）
  const L = [0]; for (let i = 1; i < path.length; i++) L.push(L[i - 1] + Math.hypot(...[0, 1, 2].map(j => path[i][j] - path[i - 1][j])));
  const d = u * L[L.length - 1]; let i = 1; while (i < path.length - 1 && L[i] < d) i++;
  const a = path[i - 1], b = path[i], w = L[i] > L[i - 1] ? (d - L[i - 1]) / (L[i] - L[i - 1]) : 1;
  return [0, 1, 2].map(j => a[j] + (b[j] - a[j]) * Math.min(1, Math.max(0, w)));
}
let lastK = -1;
W.setPlay(false);
W.S.shell = 'glass'; W.S.T = false; W.S.E = false; W.refreshState(); W.view('iso');
W.frame.push(dt => {
  if (play) T += dt; if (T > ST.length * STEP_T + 2) T = 0;
  const k = Math.min(ST.length - 1, Math.floor(T / STEP_T)), tt = T - k * STEP_T, u = Math.min(1, tt / MOVE_T);
  const ease = u < 0.5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2;
  const done = new Set(ST.slice(0, k).flatMap(s => s.parts)), now = new Set(ST[k].parts);
  for (const [name, p] of Object.entries(W.P)) {
    const on = p.info.group === 'hsg' || done.has(name) || now.has(name);
    p.mesh.visible = on && W.present(p.info);
  }
  W.S.phi = ST[k].phi; W.pose(); W.thr.visible = false;
  const off = along(ST[k].path, ease);
  for (const name of now) { const m = W.P[name] && W.P[name].mesh; if (!m) continue; m.matrix.elements[12] += off[0]; m.matrix.elements[13] += off[1]; m.matrix.elements[14] += off[2]; m.matrixWorldNeedsUpdate = true; }
  if (k !== lastK || (W._asmTick = (W._asmTick || 0) + 1) % 10 === 0) { render(k, u); lastK = k; }
});
window.__asm = { ST, seek: s => { T = s * STEP_T; } };
})();
