// 第 172b 轮：WQ-LS 整机虚拟样机（index.html?proto=1 时载入）。
// 画面还是三维整机那 98 个真零件、每 2° 的真运动；这里加上：布料和送布、布面线迹、脚踏工作周期（控制器固件在 Renode 里跑出来的
// 转速、轴角、电流、电磁铁，第 159 轮 sim_sew.json）、仪表盘（驱动力矩、惯性力、挑线余量…，数据 proto.json 由 tools/wqls/proto_web.py 从设计计算生成）。
// 转速 5000 r/min 肉眼看不清，按“慢放”倍数放慢画面，仪表盘显示真实值。
(async function () {
'use strict';
const W = window.__wq, THREE = W.THREE, $ = id => document.getElementById(id);
const PD = await fetch('proto.json').then(r => r.json());
const C = PD.curves, TK = PD.takeup, DY = PD.dyn, CY = PD.cycle;
const TXT = {
  zh: { title: 'WQ-LS 整机虚拟样机', sub: '真设计的 {n} 个零件在转；布料、线迹、脚踏和仪表盘都来自设计计算和控制器固件仿真', demo: '演示', seam: '缝一段', seamD: '起缝加固 → 半踩 → 停下针位 → 后踩剪线 → 拨线、抬压脚',
    cycle: '工作周期', cycleD: '一脚踩到底 5000 r/min → 后踩剪线 → 停上针位', manual: '手动脚踏', manualD: '拖滑块定转速，看稳态', fabric: '布料', lining: '衬里 0.4', cotton: '棉布 1.5', denim: '轻牛仔四层 3.0',
    stitch: '针距', slow: '慢放', look: '看', sew: '针下', whole: '整机', head: '机头', feedV: '送布', hookV: '旋梭', shell: '机壳', solid: '实体', glass: '半透明',
    rpm: '主轴转速', state: '缝纫状态', tm: '电机力矩', tl: '负载力矩', iq: '电机电流', nb: '针杆惯性力', lev: '挑线杆惯性力', slack: '面线松紧（此刻）',
    margin: '挑线余量 / 入布欠线', gap: '梭尖间隙', count: '针数', travel: '布走了', sol: '电磁铁', s_trim: '剪线', s_wipe: '拨线', s_rev: '倒缝', s_lift: '抬压脚',
    pedal: '脚踏', fw: '控制器固件（Renode 仿真）', model: '设计计算', chart: '转速与电流（整个过程）', chartT: '一转的驱动力矩（此转速）', limit: '超限', ok: '合格',
    disc: '示例设计，经计算和仿真校核，没有实物试制', spec: '设计说明书 ↗', lang: 'English', play: '暂停', resume: '继续', restart: '从头', nm: 'N·m', A: 'A', N: 'N', mm: 'mm', r: 'r/min',
    loose: '多出', tight: '欠', x: '慢放 ×', stopped: '停' },
  en: { title: 'WQ-LS virtual prototype', sub: 'The {n} real parts of the design in motion; fabric, stitches, pedal and gauges all come from the design calculations and the controller firmware simulation', demo: 'Demo', seam: 'Sew a seam', seamD: 'Back-tack → half pedal → needle-down stop → heel back to trim → wipe, lift foot',
    cycle: 'Work cycle', cycleD: 'Full pedal to 5000 r/min → heel back to trim → needle-up stop', manual: 'Manual pedal', manualD: 'Drag to set the speed, see the steady state', fabric: 'Fabric', lining: 'Lining 0.4', cotton: 'Cotton 1.5', denim: 'Light denim ×4 3.0',
    stitch: 'Stitch', slow: 'Slow-mo', look: 'View', sew: 'Needle', whole: 'Whole', head: 'Head', feedV: 'Feed', hookV: 'Hook', shell: 'Housing', solid: 'Solid', glass: 'See-through',
    rpm: 'Main shaft', state: 'Sewing state', tm: 'Motor torque', tl: 'Load torque', iq: 'Motor current', nb: 'Needle-bar inertia force', lev: 'Take-up lever inertia force', slack: 'Needle-thread slack (now)',
    margin: 'Take-up margin / shortfall', gap: 'Hook point gap', count: 'Stitches', travel: 'Fabric moved', sol: 'Solenoids', s_trim: 'Trim', s_wipe: 'Wipe', s_rev: 'Reverse', s_lift: 'Foot lift',
    pedal: 'Pedal', fw: 'Controller firmware (Renode)', model: 'Design calculation', chart: 'Speed and current (whole run)', chartT: 'Drive torque over one turn (this speed)', limit: 'over limit', ok: 'OK',
    disc: 'Example design, checked by calculation and simulation; no physical prototype built', spec: 'Design documentation ↗', lang: '中文', play: 'Pause', resume: 'Resume', restart: 'Restart', nm: 'N·m', A: 'A', N: 'N', mm: 'mm', r: 'r/min',
    loose: 'spare', tight: 'short', x: 'slow-mo ×', stopped: 'stopped' },
};
const STATE_EN = ['Power-up', 'Ready', 'Back-tack fwd', 'Back-tack rev', 'Sewing', 'Stopping', 'Needle down', 'Trimming', 'Wiping', 'Foot lifted', 'Fault'];
let LANG = W.LANG;
const t = k => TXT[LANG][k] ?? k;

// ---------------------------------------------------------------- 样式与界面
const st = document.createElement('style');
st.textContent = `
.pp{position:fixed;left:12px;top:12px;width:min(320px,calc(100vw - 24px));max-height:calc(100vh - 24px);overflow:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);z-index:3}
.pp h1{font-size:16px;margin:0}.pp .sub{margin:2px 0 6px}
.dash{position:fixed;right:12px;top:12px;width:min(300px,calc(100vw - 24px));background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);z-index:3;font-variant-numeric:tabular-nums}
.dash .big{display:flex;align-items:baseline;gap:6px}.dash .big b{font:700 34px/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--acc)}.dash .big span{color:var(--mut);font-size:12px}
.dash .st{font-weight:650;margin:2px 0 6px}
.dash .g{display:grid;grid-template-columns:1fr auto;gap:2px 8px;font-size:12.5px}.dash .g span{color:var(--mut)}.dash .g b{font-weight:600;text-align:right}
.dash .g b.bad{color:#d33}.dash .g b.good{color:#2e9e6a}
.dash .sols{display:flex;gap:4px;flex-wrap:wrap;margin-top:6px}.dash .sols i{font-style:normal;font-size:11.5px;border:1px solid var(--line);border-radius:10px;padding:1px 7px;color:var(--mut)}
.dash .sols i.on{background:#e0a33b;border-color:#e0a33b;color:#111}
.dash .src{font-size:11px;color:var(--mut);margin-top:6px}
.strip{position:fixed;left:50%;transform:translateX(-50%);bottom:12px;width:min(640px,calc(100vw - 24px));background:var(--card);border:1px solid var(--line);border-radius:12px;padding:6px 10px;z-index:3}
.strip b{font-size:11.5px;color:var(--mut);font-weight:600}.strip canvas{display:block;width:100%;height:96px}
.pp .seg{display:block;width:100%;text-align:left;margin:3px 0}.pp .seg small{display:block;color:inherit;opacity:.75;font-size:11px}
@media (max-width:900px){.strip{display:none}}
@media (max-width:640px){.pp{top:auto;bottom:0;left:0;width:100vw;max-height:46vh;border-radius:12px 12px 0 0}.pp.closed>*:not(.row:first-child){display:none}.dash{top:8px;right:8px;width:calc(100vw - 16px);padding:6px 10px}.dash .g{grid-template-columns:1fr auto 1fr auto}.dash .big b{font-size:24px}.dash .x,.dash .src,.dash .sols{display:none}}
.pp #pFold{display:none}@media (max-width:640px){.pp #pFold{display:inline-block}}
body.embed .pp{display:none}`;
document.head.appendChild(st);
const pp = document.createElement('div'); pp.className = 'pp'; document.body.appendChild(pp);
const dash = document.createElement('div'); dash.className = 'dash'; document.body.appendChild(dash);
const strip = document.createElement('div'); strip.className = 'strip'; strip.innerHTML = '<b id="pcT"></b><canvas id="pc"></canvas>'; document.body.appendChild(strip);
document.querySelector('.top').style.display = 'none';

const P = { mode: new URLSearchParams(location.search).get('proto') === 'manual' ? 'manual' : 'seam', fab: 'cotton', s: 's3', slow: 20, man: 3000, paused: false };
function ui() {
  const b = (attr, v, label, on) => `<button data-${attr}="${v}"${on ? ' class="on"' : ''}>${label}</button>`;
  pp.innerHTML = `<div class="row" style="justify-content:space-between;margin:0"><h1>${t('title')}</h1><span><button id="pFold">${LANG === 'en' ? 'Controls' : '控制'}</button> <button id="pLang">${t('lang')}</button></span></div>
  <p class="sub">${t('sub').replace('{n}', Object.keys(W.D.parts).length)}</p>
  <div class="sec"><b>${t('demo')}</b>
   ${['seam', 'cycle', 'manual'].map(m => `<button class="seg${P.mode === m ? ' on' : ''}" data-mode="${m}">${t(m)}<small>${t(m + 'D')}</small></button>`).join('')}
   <div id="manRow" ${P.mode === 'manual' ? '' : 'hidden'}><div class="read"><span>${t('pedal')}</span><span id="manV">${P.man} ${t('r')}</span></div>
   <input id="man" type="range" min="0" max="5000" step="50" value="${P.man}"></div>
   <div class="row"><button id="pPause">${P.paused ? t('resume') : t('play')}</button><button id="pRestart">${t('restart')}</button></div></div>
  <div class="sec"><b>${t('fabric')}</b><div class="row">${b('fab', 'lining', t('lining'), P.fab === 'lining')}${b('fab', 'cotton', t('cotton'), P.fab === 'cotton')}${b('fab', 'light_denim_x4', t('denim'), P.fab === 'light_denim_x4')}</div>
   <div class="row"><span class="l">${t('stitch')}</span>${b('s', 's3', '3 mm', P.s === 's3')}${b('s', 's5', '5 mm', P.s === 's5')}</div>
   <div class="row"><span class="l">${t('slow')}</span>${[200, 50, 20].map(k => b('slow', k, '1/' + k, P.slow === k)).join('')}</div></div>
  <div class="sec"><b>${t('look')}</b><div class="row">${b('v', 'sew', t('sew'))}${b('v', 'whole', t('whole'))}${b('v', 'iso', t('head'))}${b('v', 'feed', t('feedV'))}${b('v', 'hook', t('hookV'))}</div>
   <div class="row"><span class="l">${t('shell')}</span>${b('sh', 'solid', t('solid'), W.S.shell === 'solid')}${b('sh', 'glass', t('glass'), W.S.shell === 'glass')}</div></div>
  <p class="hint">${t('disc')}</p><p class="hint"><a href="spec/index.html" target="_blank" rel="noopener">${t('spec')}</a></p>`;
  pp.querySelectorAll('[data-mode]').forEach(e => e.onclick = () => { P.mode = e.dataset.mode; restart(); ui(); });
  pp.querySelectorAll('[data-fab]').forEach(e => e.onclick = () => { P.fab = e.dataset.fab; makeFabric(); ui(); });
  pp.querySelectorAll('[data-s]').forEach(e => e.onclick = () => { P.s = e.dataset.s; ui(); });
  pp.querySelectorAll('[data-slow]').forEach(e => e.onclick = () => { P.slow = +e.dataset.slow; ui(); });
  pp.querySelectorAll('[data-v]').forEach(e => e.onclick = () => look(e.dataset.v));
  pp.querySelectorAll('[data-sh]').forEach(e => e.onclick = () => { W.S.shell = e.dataset.sh; W.refreshState(); ui(); });
  const m = $('man'); if (m) m.oninput = () => { P.man = +m.value; $('manV').textContent = `${P.man} ${t('r')}`; };
  $('pPause').onclick = () => { P.paused = !P.paused; ui(); };
  $('pRestart').onclick = () => { restart(); };
  $('pFold').onclick = () => pp.classList.toggle('closed');
  $('pLang').onclick = () => { LANG = LANG === 'en' ? 'zh' : 'en'; try { localStorage.setItem('wq-factory-lang', LANG); } catch (e) { /* 无痕 */ } ui(); };
}

// ---------------------------------------------------------------- 布料与线迹（机器坐标 mm：针在 x 0、y 0，针板面 z 0；送布沿 y）
const fab = new THREE.Group(); W.root.add(fab);
const FCOL = { lining: 0xcfc7e6, cotton: 0xe8e1cf, light_denim_x4: 0x3e5f8a };
let cloth = null, stitches = [], lastPt = null, fy = 0, nStitch = 0;
const STM = new THREE.MeshStandardMaterial({ color: 0xe0203a, roughness: 0.45, emissive: 0x5a0010, emissiveIntensity: 0.6 });
function weave(col) {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  const base = new THREE.Color(col); g.fillStyle = '#' + base.getHexString(); g.fillRect(0, 0, 128, 128);
  g.globalAlpha = 0.28; g.strokeStyle = '#000';
  for (let i = 0; i < 128; i += 4) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 128); g.stroke(); g.beginPath(); g.moveTo(0, i + 2); g.lineTo(128, i + 2); g.stroke(); }
  const tx = new THREE.CanvasTexture(c); tx.wrapS = tx.wrapT = THREE.RepeatWrapping; tx.repeat.set(14, 10); return tx;
}
function makeFabric() {
  if (cloth) { fab.remove(cloth); cloth.geometry.dispose(); }
  const th = PD.fabric_t[P.fab];
  cloth = new THREE.Mesh(new THREE.BoxGeometry(250, 620, th), new THREE.MeshStandardMaterial({ map: weave(FCOL[P.fab]), color: FCOL[P.fab], roughness: 1, metalness: 0, envMapIntensity: 0.25 }));
  cloth.position.set(-20, -200, th / 2 + 0.02); fab.add(cloth);
  clearStitches();
}
function clearStitches() { for (const s of stitches) { fab.remove(s); } stitches = []; lastPt = null; fy = 0; nStitch = 0; fab.position.y = 0; }
function addStitch(y) {
  const th = PD.fabric_t[P.fab], p = new THREE.Vector3(0, y, th + 0.35);
  if (lastPt && Math.abs(lastPt.y - p.y) > 0.3) {
    const len = Math.abs(lastPt.y - p.y), m = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, len, 8), STM);
    m.position.set(0, (lastPt.y + p.y) / 2, p.z); fab.add(m); stitches.push(m);
    if (stitches.length > 80) fab.remove(stitches.shift());
  }
  lastPt = p; nStitch++;
}

// ---------------------------------------------------------------- 一转的数据（每 1°）
const at = (arr, ph) => { const i = Math.floor(ph) % 360, j = (i + 1) % 360, u = ph - Math.floor(ph); return arr[i] + (arr[j] - arr[i]) * u; };
function slackAt(ph) {
  const th = PD.fabric_t[P.fab], top = TK.python.new[P.fab].top, c = TK.s_ref + th;
  const D = Math.floor(ph) < top ? c : at(TK.demand[P.fab], ph);
  return at(C.supply, ph) - D;
}
const Kt = 0.496;
const PRESS_UP = ['presser_foot', 'presser_bar', 'presser_collar', 'lift_bracket', 'presser_spring'];                                  // 力矩常数（第 159 轮参数表）

// ---------------------------------------------------------------- 工作周期：固件仿真的时间序列
let sim = 0, phi = 0, prevPhi = 0, cur = {};
function series() { return CY.scenarios[P.mode === 'cycle' ? 'cycle' : 'seam']; }
function restart() { const s = series(); sim = s.t[0]; phi = s.ang[0]; prevPhi = phi; clearStitches(); W.S.trim = 'sew'; W.S.press = 'down'; W.refreshState(); }
function sample(s, tt) {
  const k = Math.max(0, Math.min(s.t.length - 2, Math.floor((tt - s.t[0]) / (s.t[1] - s.t[0])))), u = Math.max(0, Math.min(1, (tt - s.t[k]) / (s.t[k + 1] - s.t[k])));
  const L = a => a[k] + (a[k + 1] - a[k]) * u;
  return { rpm: L(s.rpm), iq: L(s.iq), tm: L(s.tm), tl: L(s.tl), ang: s.ang[k], state: s.state[k], sol: s.sol[k], pedal: s.pedal[k], k };
}

// 走过一段转角：送布牙在针板上面时布跟着牙走；针尖从布里出来时布面上落一针
function advance(from, to, rpm) {
  const n = Math.min(3600, Math.floor(to) - Math.floor(from));
  const key = cur.feed || 's3', dog = PD.dog[key], th = PD.fabric_t[P.fab];
  for (let i = 0; i < n; i++) {
    const a = (Math.floor(from) + i + 360000) % 360, b = (a + 1) % 360;
    if (dog.z[a] > 0 && dog.z[b] > 0 && rpm > 1) { fy += dog.y[b] - dog.y[a]; }
    if (C.tip[a] <= th && C.tip[b] > th && !cur.cut) addStitch(-fy);
  }
  fab.position.y = fy;
  if (fy > 380 || fy < -60) { const keep = cur; clearStitches(); cur = keep; }   // 布走完一段，换一块
}

let lastFeed = '', lastTrim = '', lastPress = '', wipeT = 0;
W.frame.push(dt => {
  if (!cloth) return;
  let rpm, s = null;
  if (P.mode === 'manual') { rpm = P.paused ? 0 : P.man; cur = { rpm, state: rpm > 0 ? 4 : 1, sol: 0, feed: P.s }; }
  else {
    s = series();
    if (!P.paused) { sim += dt / P.slow; if (sim > s.t[s.t.length - 1] + 0.4) restart(); }
    const v = sample(s, Math.min(sim, s.t[s.t.length - 1]));
    rpm = v.rpm; cur = v; cur.feed = v.state === 3 ? 'r5' : P.s;
  }
  const dphi = P.paused ? 0 : rpm * 6 * dt / P.slow;
  if (s && Math.abs(rpm) < 40) phi += ((cur.ang - phi + 540) % 360 - 180) * Math.min(1, dt * 4);   // 停下来时对齐固件的轴角
  else phi += dphi;
  cur.cut = !!(cur.sol & 1) || (cur.state >= 7 && cur.state <= 9);
  if (Math.floor(phi) !== Math.floor(prevPhi) && phi > prevPhi) advance(prevPhi, phi, rpm);
  prevPhi = phi;
  // 三维状态：倒缝用倒缝 5 那组运动；剪线电磁铁吸合时放剪线那一转；拨线、抬压脚
  const feedKey = cur.feed === 'r5' ? 'r5' : P.s;
  const trim = (cur.sol & 1) ? 'trim' : (cur.sol & 2) ? 'wipe' : 'sew';
  const press = (cur.sol & 8) ? 'hand' : 'down';
  if (feedKey !== lastFeed || trim !== lastTrim || press !== lastPress) {
    W.S.feed = feedKey; W.S.trim = trim; W.S.press = press; if (trim === 'wipe') wipeT = 0;
    W.refreshState(); lastFeed = feedKey; lastTrim = trim; lastPress = press;
  }
  if (trim === 'wipe') { wipeT = Math.min(W.D.frames - 1, wipeT + dt / P.slow / 0.05 * (W.D.frames - 1)); W.S.wipe = wipeT; W.pose(); }
  else W.setPhi(((phi % 360) + 360) % 360);
  if (W.S.ex === 0) {                                         // 压脚放下时压在布面上：压脚组整体抬起一个布厚
    const th = PD.fabric_t[P.fab];
    for (const k of PRESS_UP) if (W.P[k] && W.P[k].mesh.visible) { W.P[k].mesh.matrix.elements[14] += th; W.P[k].mesh.matrixWorldNeedsUpdate = true; }
  }
  cloth.visible = !(W.S.ex > 0);
  gauges(rpm);
  chart();
});

// ---------------------------------------------------------------- 仪表盘
let gT = 0;
function gauges(rpm) {
  gT += 1; if (gT % 4) return;                                   // 每 4 帧刷一次字
  const ph = ((phi % 360) + 360) % 360, k2 = (rpm / 5000) ** 2;
  const manual = P.mode === 'manual';
  const tl = manual ? at(DY.T_inertial, ph) * k2 + (rpm > 0 ? at(DY.T_rest, ph) : 0) : cur.tl;
  const tm = manual ? tl : cur.tm, iq = manual ? tm / Kt : cur.iq;
  const nb = at(DY.F_inertia.needle_bar, ph) * k2, lev = at(DY.F_inertia.lever, ph) * k2;
  const py = TK.python.new[P.fab], sl = slackAt(ph);
  const stName = LANG === 'en' ? STATE_EN[cur.state] : CY.states[cur.state];
  const sols = [[1, 's_trim'], [2, 's_wipe'], [4, 's_rev'], [8, 's_lift']].map(([b, k]) => `<i class="${cur.sol & b ? 'on' : ''}">${t(k)}</i>`).join('');
  const f = (v, d) => (Math.abs(v) < 0.5 * 10 ** -d ? 0 : v).toFixed(d);
  const marOk = py.margin >= TK.margin_min && py.neg <= TK.neg_max;
  dash.innerHTML = `<div class="big"><b>${Math.round(rpm)}</b><span>${t('r')} · ${t('rpm')}</span></div>
   <div class="st">${t('state')}：${stName || '—'}${P.mode !== 'manual' ? ` · <span class="mut">${t('x')}1/${P.slow}</span>` : ''}</div>
   <div class="g"><span>${t('tm')}</span><b>${f(tm, 2)} ${t('nm')}</b><span>${t('tl')}</span><b>${f(tl, 2)} ${t('nm')}</b>
   <span>${t('iq')}</span><b class="${Math.abs(iq) > 6.05 ? 'bad' : ''}">${f(iq, 2)} ${t('A')}</b>
   <span>${t('nb')}</span><b>${f(nb, 0)} ${t('N')}</b><span class="x">${t('lev')}</span><b class="x">${f(lev, 0)} ${t('N')}</b>
   <span>${t('slack')}</span><b class="${sl < -1 ? 'bad' : ''}">${sl >= 0 ? t('loose') : t('tight')} ${Math.abs(sl).toFixed(1)} ${t('mm')}</b>
   <span class="x">${t('margin')}</span><b class="x ${marOk ? 'good' : 'bad'}">${py.margin.toFixed(2)} / ${py.neg.toFixed(2)} ${t('mm')}</b>
   <span class="x">${t('gap')}</span><b class="x good">${PD.catch.point_gap.toFixed(2)} ${t('mm')}</b>
   <span>${t('count')}</span><b>${nStitch}</b><span class="x">${t('travel')}</span><b class="x">${Math.abs(fy).toFixed(1)} ${t('mm')}</b></div>
   <div class="sols"><span class="mut" style="font-size:11.5px">${t('sol')}</span>${sols}</div>
   <div class="src">${manual ? t('model') : t('fw')} · 5000 r/min ${t('model')}</div>`;
}

// ---------------------------------------------------------------- 底部曲线
function chart() {
  const cv = $('pc'); if (!cv || !cv.offsetWidth) return;
  const w = cv.width = cv.offsetWidth * devicePixelRatio, h = cv.height = 96 * devicePixelRatio, g = cv.getContext('2d');
  const css = getComputedStyle(document.documentElement), ink = css.getPropertyValue('--mut').trim() || '#666';
  g.clearRect(0, 0, w, h); g.lineWidth = 1.5 * devicePixelRatio; g.font = `${10 * devicePixelRatio}px system-ui`;
  if (P.mode === 'manual') {
    $('pcT').textContent = t('chartT');
    const k2 = (P.man / 5000) ** 2, T = DY.T_inertial.map((v, i) => v * k2 + (P.man > 0 ? DY.T_rest[i] : 0));
    const lo = Math.min(...T, 0), hi = Math.max(...T, 0.1);
    const Y = v => h - 6 - (v - lo) / (hi - lo) * (h - 14);
    g.strokeStyle = ink; g.globalAlpha = 0.4; g.beginPath(); g.moveTo(0, Y(0)); g.lineTo(w, Y(0)); g.stroke(); g.globalAlpha = 1;
    g.strokeStyle = '#2f6fd6'; g.beginPath(); T.forEach((v, i) => { const x = i / 359 * w; i ? g.lineTo(x, Y(v)) : g.moveTo(x, Y(v)); }); g.stroke();
    const x = (((phi % 360) + 360) % 360) / 360 * w; g.strokeStyle = '#e0a33b'; g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke();
    g.fillStyle = ink; g.fillText(`${hi.toFixed(2)} N·m`, 4, 12 * devicePixelRatio); g.fillText(`${lo.toFixed(2)}`, 4, h - 4);
    return;
  }
  const s = series(); $('pcT').textContent = t('chart');
  const t0 = s.t[0], t1 = s.t[s.t.length - 1], X = tt => (tt - t0) / (t1 - t0) * w;
  const line = (arr, max, col) => { g.strokeStyle = col; g.beginPath(); for (let i = 0; i < arr.length; i += 3) { const x = X(s.t[i]), y = h - 6 - arr[i] / max * (h - 14); i ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); };
  line(s.rpm, 5200, '#2f6fd6'); line(s.iq.map(Math.abs), 7.5, '#d9622b');
  g.fillStyle = '#2f6fd6'; g.fillText('r/min (0–5000)', 4, 12 * devicePixelRatio); g.fillStyle = '#d9622b'; g.fillText('|iq| A (0–7.5)', 110 * devicePixelRatio, 12 * devicePixelRatio);
  const x = X(Math.min(sim, t1)); g.strokeStyle = '#e0a33b'; g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke();
}

// 针下视角：从左前上方看针、压脚、布面线迹（three 坐标：x = 机器 x，y = 机器 z，z = −机器 y，单位 m）
function look(v) {
  if (v !== 'sew') { W.view(v); return; }
  W.ctl.target.set(0.0, 0.006, -0.004); W.ctl.sph.setFromVector3(new THREE.Vector3(-0.075, 0.07, 0.11));
  const asp = innerWidth / innerHeight; if (asp < 1.2) W.ctl.sph.radius *= Math.min(1.8, 1.2 / asp);
  W.camApply();
}
// ---------------------------------------------------------------- 开始
W.setPlay(false); W.S.T = true; W.S.E = true; W.S.shell = 'solid';
W.refreshState(); look(new URLSearchParams(location.search).get('pv') || 'sew');
makeFabric(); restart(); ui(); if (matchMedia('(max-width:640px)').matches) pp.classList.add('closed');
window.__proto = { P, PD, cur: () => cur, sim: () => sim, restart };
})();
