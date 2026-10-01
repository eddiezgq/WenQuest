/* WenQuest lab kit (round 3, A3): the fixed shell every AI-written virtual lab runs in.
   Same layout and behaviour as the Chapter 1 benchmark: tabs, EN/中文, scene chips, parameter sliders,
   task list that ticks itself, "k / n tasks done", canvas loop, WenQuest lab protocol (#lab-2-1 and
   {type: "wq-lab", lab: "2.1"}). A lab only supplies its physics and drawing through WQ.lab({...}). */
(() => {
"use strict";
const $ = (id) => document.getElementById(id);
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage unavailable in the sandbox */ } },
};
const KEY = document.documentElement.dataset.key || "wq-lab";
let lang = store.get(KEY + "-lang") || document.documentElement.dataset.lang || "zh";
if (/(^|[-#])en$/.test(location.hash)) lang = "en";
const T = (zh, en) => (lang === "en" ? (en || zh) : (zh || en));
const P = (pair) => (Array.isArray(pair) ? T(pair[0], pair[1]) : String(pair == null ? "" : pair));
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const fmt = (x, d = 2) => (Math.abs(x) < 1e-9 ? 0 : +x).toFixed(d);
const errors = [];
const LABS = {};
const ORDER = [];
let current = null;   // the lab id being defined (set by WQ.begin)
let active = null;
const saved = store.get(KEY + "-tasks") || {};

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}
function biText(e, pair) {   // an element whose text follows the language switch
  e.dataset.zh = Array.isArray(pair) ? pair[0] : pair;
  e.dataset.en = Array.isArray(pair) ? (pair[1] || pair[0]) : pair;
  e.classList.add("bi");
  e.textContent = lang === "en" ? e.dataset.en : e.dataset.zh;
  return e;
}

// ---------- drawing helpers handed to labs ----------
function arrow(ctx, x1, y1, x2, y2, color, width = 3) {
  const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy);
  if (L < 1) return;
  const head = Math.min(12, L * 0.35), ang = Math.atan2(dy, dx);
  ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = width; ctx.lineCap = "round";
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2 - head * 0.8 * Math.cos(ang), y2 - head * 0.8 * Math.sin(ang)); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x2, y2);
  ctx.lineTo(x2 - head * Math.cos(ang - 0.4), y2 - head * Math.sin(ang - 0.4));
  ctx.lineTo(x2 - head * Math.cos(ang + 0.4), y2 - head * Math.sin(ang + 0.4));
  ctx.closePath(); ctx.fill();
}
function label(ctx, text, x, y, color, size = 13, align = "left") {
  ctx.fillStyle = color || css("--ink"); ctx.font = `${size}px ${css("--sans")}`; ctx.textAlign = align; ctx.textBaseline = "middle"; ctx.fillText(text, x, y);
}
function line(ctx, x1, y1, x2, y2, color, width = 2, dash) {
  ctx.strokeStyle = color || css("--ink"); ctx.lineWidth = width; ctx.setLineDash(dash || []);
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); ctx.setLineDash([]);
}
function rect(ctx, x, y, w, h, fill, stroke, r = 0) {
  ctx.beginPath();
  if (r && ctx.roundRect) ctx.roundRect(x, y, w, h, r); else ctx.rect(x, y, w, h);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1.5; ctx.stroke(); }
}
function circle(ctx, x, y, r, fill, stroke) {
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1.5; ctx.stroke(); }
}
function ground(ctx, y, w, shift = 0, step = 40) {   // floor line with hatching; `shift` scrolls it (moving camera)
  line(ctx, 0, y, w, y, css("--ground"), 2);
  ctx.strokeStyle = css("--ground"); ctx.lineWidth = 1; ctx.globalAlpha = 0.5;
  const s = ((shift % step) + step) % step;
  for (let x = -s; x < w + step; x += step) { ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 10, y + 10); ctx.stroke(); }
  ctx.globalAlpha = 1;
}
function grid(ctx, w, h, step = 40) {
  ctx.strokeStyle = css("--grid"); ctx.lineWidth = 1;
  for (let x = 0; x < w; x += step) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
  for (let y = 0; y < h; y += step) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
}
function agv(ctx, x, y, w, color) {   // warehouse AGV: bottom-centre at (x, y), deck top at y - 0.32w
  const h = w * 0.26, wr = w * 0.07;
  rect(ctx, x - w / 2, y - h - wr, w, h, color || css("--accent"), null, 6);
  circle(ctx, x - w * 0.32, y - wr, wr, css("--ink")); circle(ctx, x + w * 0.32, y - wr, wr, css("--ink"));
  rect(ctx, x + w * 0.36, y - h - wr + h * 0.3, w * 0.1, h * 0.25, css("--amber"));
}
function box(ctx, x, y, s, color) {   // a crate: bottom-centre at (x, y)
  rect(ctx, x - s / 2, y - s, s, s, color || css("--amber"), css("--ink"), 3);
  line(ctx, x - s / 2, y - s, x + s / 2, y, css("--ink"), 1); line(ctx, x + s / 2, y - s, x - s / 2, y, css("--ink"), 1);
}

// ---------- robotics helpers (angles in degrees, counter-clockwise on screen; y grows downwards) ----------
function rot2(deg) { const t = deg * Math.PI / 180, c = Math.cos(t), s = Math.sin(t); return [[c, -s], [s, c]]; }
function fk(x, y, angles, lengths) {   // joint points of a planar n-link arm; each angle relative to the previous link
  const pts = [[x, y]]; let t = 0;
  angles.forEach((a, i) => { t += a * Math.PI / 180; const [px, py] = pts[pts.length - 1];
    pts.push([px + lengths[i] * Math.cos(t), py - lengths[i] * Math.sin(t)]); });
  return pts;
}
function frame(ctx, x, y, deg, len, labels, name, color) {   // a 2D coordinate frame (x axis red, y axis green)
  const t = deg * Math.PI / 180, lb = labels || ["x", "y"];
  const xe = [x + len * Math.cos(t), y - len * Math.sin(t)], ye = [x - len * Math.sin(t), y - len * Math.cos(t)];
  arrow(ctx, x, y, xe[0], xe[1], css("--red"), 2.5); arrow(ctx, x, y, ye[0], ye[1], css("--green"), 2.5);
  label(ctx, lb[0], xe[0] + 6 * Math.cos(t), xe[1] - 6 * Math.sin(t), css("--red"), 13, "center");
  label(ctx, lb[1], ye[0] - 6 * Math.sin(t), ye[1] - 6 * Math.cos(t), css("--green"), 13, "center");
  circle(ctx, x, y, 3, color || css("--ink"));
  if (name) label(ctx, name, x - 8, y + 12, color || css("--blue"), 13, "right");
}
function arm(ctx, x, y, angles, lengths, color, width) {   // planar n-link arm with base, joints and gripper; returns the joint points
  const pts = fk(x, y, angles, lengths), w = width || Math.max(6, lengths[0] * 0.08);
  ctx.fillStyle = css("--muted"); ctx.beginPath(); ctx.moveTo(x - w * 2, y + w * 1.2); ctx.lineTo(x + w * 2, y + w * 1.2);
  ctx.lineTo(x + w, y); ctx.lineTo(x - w, y); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = color || css("--accent"); ctx.lineWidth = w; ctx.lineCap = "round";
  ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); pts.slice(1).forEach((p) => ctx.lineTo(p[0], p[1])); ctx.stroke();
  pts.slice(0, -1).forEach((p) => circle(ctx, p[0], p[1], w * 0.6, css("--panel"), css("--ink")));
  const e = pts[pts.length - 1], q = pts[pts.length - 2], t = Math.atan2(e[1] - q[1], e[0] - q[0]);
  [0.5, -0.5].forEach((d) => line(ctx, e[0], e[1], e[0] + w * 1.6 * Math.cos(t + d), e[1] + w * 1.6 * Math.sin(t + d), css("--ink"), 2.5));
  return pts;
}
function robot(ctx, x, y, deg, size, color) {   // differential-drive mobile robot seen from above; heading in degrees
  const t = -deg * Math.PI / 180;
  ctx.save(); ctx.translate(x, y); ctx.rotate(t);
  rect(ctx, -size * 0.2, -size * 0.62, size * 0.4, size * 0.14, css("--ink"), null, 3);
  rect(ctx, -size * 0.2, size * 0.48, size * 0.4, size * 0.14, css("--ink"), null, 3);
  circle(ctx, 0, 0, size / 2, color || css("--accent"), css("--ink"));
  ctx.fillStyle = css("--amber"); ctx.beginPath(); ctx.moveTo(size * 0.46, 0); ctx.lineTo(size * 0.02, -size * 0.22); ctx.lineTo(size * 0.02, size * 0.22); ctx.closePath(); ctx.fill();
  ctx.restore();
}
function lidar(ctx, x, y, angles, ranges, color) {   // laser rays (degrees, lengths in px) with hit points
  angles.forEach((a, i) => { const t = a * Math.PI / 180, ex = x + ranges[i] * Math.cos(t), ey = y - ranges[i] * Math.sin(t);
    ctx.globalAlpha = 0.6; line(ctx, x, y, ex, ey, color || css("--amber"), 1); ctx.globalAlpha = 1; circle(ctx, ex, ey, 2.5, color || css("--amber")); });
}
function plot(ctx, x, y, w, h, series, opt) {   // a small chart: series = [{pts: [[x, y], ...], color, name}], opt = {xmin, xmax, ymin, ymax, xlabel, ylabel}
  const o = opt || {}, all = series.flatMap((s) => s.pts);
  const xmin = o.xmin ?? Math.min(0, ...all.map((p) => p[0])), xmax = o.xmax ?? Math.max(1, ...all.map((p) => p[0]));
  const ymin = o.ymin ?? Math.min(0, ...all.map((p) => p[1])), ymax = o.ymax ?? Math.max(1, ...all.map((p) => p[1]));
  const X = (v) => x + (v - xmin) / ((xmax - xmin) || 1) * w, Y = (v) => y + h - (v - ymin) / ((ymax - ymin) || 1) * h;
  rect(ctx, x, y, w, h, null, css("--grid"));
  if (ymin < 0 && ymax > 0) line(ctx, x, Y(0), x + w, Y(0), css("--grid"), 1);
  series.forEach((s) => { if (!s.pts.length) return; ctx.strokeStyle = s.color || css("--accent"); ctx.lineWidth = 2; ctx.beginPath();
    s.pts.forEach((p, i) => (i ? ctx.lineTo(X(p[0]), Y(p[1])) : ctx.moveTo(X(p[0]), Y(p[1])))); ctx.stroke(); });
  if (o.xlabel) label(ctx, o.xlabel, x + w, y + h + 12, css("--muted"), 12, "right");
  if (o.ylabel) label(ctx, o.ylabel, x + 4, y + 10, css("--muted"), 12, "left");
  return { X, Y };
}

// ---------- tasks & progress ----------
function paintTasks() {
  let n = 0, k = 0;
  ORDER.forEach((id) => {
    const L = LABS[id];
    const ul = L.dom.tasks;
    ul.innerHTML = "";
    let ok = 0;
    L.def.tasks.forEach((t) => {
      n++; if (t.ok) { k++; ok++; }
      const li = el("li", t.ok ? "ok" : "");
      const b = el("span", "box", t.ok ? "✓" : ""); b.setAttribute("aria-hidden", "true");
      const s = el("span", "t");
      if (t.robot) s.appendChild(el("span", "tag", T("机器人", "Robot")));
      s.appendChild(document.createTextNode(P(t.text)));
      li.append(b, s);
      ul.appendChild(li);
    });
    L.dom.tabDone.textContent = ok === L.def.tasks.length && ok ? "✓" : ok ? `${ok}/${L.def.tasks.length}` : "";
  });
  const pr = $("progress");
  if (pr) pr.textContent = n ? T(`已完成 ${k} / ${n} 个任务`, `${k} / ${n} tasks done`) : "";
}
function done(lab, id) {
  const L = LABS[lab];
  const t = L && L.def.tasks.find((x) => x.id === id);
  if (!t || t.ok) return;
  t.ok = true; saved[lab + ":" + id] = true; store.set(KEY + "-tasks", saved); paintTasks();
  try {
    const tot = L.def.tasks.length, k = L.def.tasks.filter((x) => x.ok).length;
    if (window.parent !== window) window.parent.postMessage({ type: "wq-lab-progress", lab: lab.replace("-", "."), task: id, done: k, total: tot }, "*");
  } catch (e) { /* no parent */ }
}

// ---------- language ----------
function applyLang() {
  document.documentElement.lang = lang === "en" ? "en" : "zh-CN";
  document.querySelectorAll(".bi").forEach((e) => { e.textContent = lang === "en" ? e.dataset.en : e.dataset.zh; });
  $("lang").textContent = lang === "en" ? "中文" : "EN";
  ORDER.forEach((id) => { const L = LABS[id]; paintParams(L); paintProblem(L); readouts(L); });
  document.title = P(JSON.parse(document.documentElement.dataset.title || '["虚拟实验","Virtual lab"]'));
  paintTasks();
}
$("lang").onclick = () => { lang = lang === "en" ? "zh" : "en"; store.set(KEY + "-lang", lang); applyLang(); };

// ---------- one lab ----------
function fail(id, e) {
  const msg = (e && (e.stack || e.message)) || String(e);
  errors.push(`[${id}] ${msg}`);
  console.error(`lab ${id}:`, e);
  const L = LABS[id];
  if (L) { L.broken = true; L.dom.err.textContent = T("实验出错：", "Lab error: ") + (e && e.message ? e.message : String(e)); L.dom.err.classList.add("on"); }
}
function safe(L, fn) { try { return fn(); } catch (e) { fail(L.id, e); return undefined; } }

function paintParams(L) {
  L.def.params.forEach((p) => {
    const c = L.dom.params[p.id];
    const hidden = (L.sceneDef.hide || []).includes(p.id);
    c.wrap.hidden = hidden;
    c.out.textContent = fmt(L.api.p[p.id], p.digits == null ? 2 : p.digits) + (p.unit ? " " + p.unit : "");
  });
}
function paintProblem(L) {
  const pr = L.sceneDef.problem;
  L.dom.problem.hidden = !pr;
  if (pr) { L.dom.problem.innerHTML = ""; L.dom.problem.append(el("b", "", P(pr.title)), el("span", "", P(pr.text))); }
}
function setScene(L, sid) {
  const sc = L.def.scenes.find((s) => s.id === sid) || L.def.scenes[0];
  L.api.scene = sc.id; L.sceneDef = sc;
  L.dom.chips.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.scene === sc.id)));
  L.def.params.forEach((p) => {
    const o = Object.assign({}, p, (sc.params || {})[p.id] || {});
    const inp = L.dom.params[p.id].input;
    inp.min = o.min; inp.max = o.max; inp.step = o.step || (o.max - o.min) / 100; inp.value = o.value;
    L.api.p[p.id] = +inp.value;
  });
  paintParams(L); paintProblem(L);
  reset(L);
}
function reset(L) {
  if (!L.ready) return;   // a 3D lab resets once its models are loaded
  L.api.running = false; L.api.t = 0;
  L.state = {};
  safe(L, () => L.def.reset && L.def.reset(L.api, L.state));
  readouts(L);
}
function start(L) {
  reset(L);
  L.api.running = true;
  safe(L, () => L.def.start && L.def.start(L.api, L.state));
}
function readouts(L) {
  if (!L.ready) return;
  const rows = safe(L, () => (L.def.readouts ? L.def.readouts(L.api, L.state) : [])) || [];
  const dl = L.dom.read;
  if (dl.childElementCount !== rows.length * 2) dl.innerHTML = rows.map(() => "<dt></dt><dd></dd>").join("");
  rows.forEach((r, i) => { dl.children[2 * i].textContent = P(r[0]); dl.children[2 * i + 1].textContent = String(r[1]); });
}

function build(id, def) {
  const no = id.replace("-", ".");
  // tab
  const tab = el("button"); tab.setAttribute("role", "tab"); tab.id = "tab-" + id; tab.dataset.lab = id;
  tab.append(el("span", "no", no), biText(el("span"), def.title), el("span", "done"));
  tab.addEventListener("click", () => show(id));
  $("tabs").appendChild(tab);
  // section
  const sec = el("section", "lab"); sec.id = "lab-" + id; sec.setAttribute("role", "tabpanel"); sec.hidden = true;
  const stageBox = el("div", "stagebox");
  const scenes = el("div", "scenes");
  scenes.appendChild(biText(el("span", "lbl"), ["场景", "Scene"]));
  const chips = def.scenes.map((s) => {
    const b = biText(el("button", "btn chip"), s.robot ? [`机器人：${s.name[0]}`, `Robot: ${s.name[1] || s.name[0]}`] : s.name);
    b.dataset.scene = s.id; b.setAttribute("aria-pressed", "false");
    scenes.appendChild(b);
    return b;
  });
  const canvas = el("canvas"); canvas.setAttribute("aria-label", `${def.title[0]} ${def.title[1] || ""}`);
  const bar = el("div", "stagebar");
  const buttons = (def.buttons && def.buttons.length ? def.buttons : [
    { id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] },
  ]);
  buttons.forEach((b) => {
    const btn = biText(el("button", "btn" + (b.primary ? " primary" : "")), b.name);
    btn.dataset.action = b.id;
    bar.appendChild(btn);
  });
  if (def.legend && def.legend.length) {
    const lg = el("span", "legend");
    def.legend.forEach((g) => { const s = el("span"); const i = el("i"); i.style.background = g.color; s.append(i, biText(el("span"), g.name)); lg.appendChild(s); });
    bar.appendChild(lg);
  }
  const err = el("div", "err");
  const problem = el("div", "problem"); problem.hidden = true;
  const goal = el("div", "goal");
  goal.append(biText(el("b"), ["实验目的：", "Goal: "]), biText(el("span"), def.goal || ["", ""]));
  const circuit = def.view === "circuit" ? el("iframe", "circuit") : null;
  if (circuit) { circuit.title = `${def.title[0]} · CircuitJS`; stageBox.classList.add("withcircuit"); stageBox.append(scenes, circuit, canvas, bar, err, problem, goal); }
  else stageBox.append(scenes, canvas, bar, err, problem, goal);
  // side
  const side = el("div", "side");
  const pc = el("div", "card"); pc.appendChild(biText(el("h3"), ["参数", "PARAMETERS"]));
  const params = {};
  def.params.forEach((p) => {
    const wrap = el("div", "ctl");
    const lab = biText(el("label"), p.name);
    const out = el("output");
    const input = el("input"); input.type = "range"; input.dataset.param = p.id;
    input.min = p.min; input.max = p.max; input.step = p.step || (p.max - p.min) / 100; input.value = p.value;
    lab.htmlFor = input.id = `p-${id}-${p.id}`;
    wrap.append(lab, out, input);
    pc.appendChild(wrap);
    params[p.id] = { wrap, out, input };
  });
  const rc = el("div", "card"); rc.appendChild(biText(el("h3"), ["测量", "MEASUREMENTS"]));
  const read = el("dl", "readout"); rc.appendChild(read);
  const tc = el("div", "card"); tc.appendChild(biText(el("h3"), ["任务", "TASKS"]));
  const tasks = el("ul", "tasks"); tc.appendChild(tasks);
  if (def.think) tc.appendChild(biText(el("p", "hint"), def.think));
  side.append(pc, rc, tc);
  sec.append(stageBox, side);
  $("labs").appendChild(sec);

  const is3d = def.view === "3d";
  const ctx = is3d ? null : canvas.getContext("2d");
  const L = { id, def, broken: false, state: {}, sceneDef: def.scenes[0], is3d, ready: !is3d && !circuit, circuit,
    dom: { tab, tabDone: tab.querySelector(".done"), sec, canvas, chips, params, read, tasks, err, problem } };
  const api = {
    ctx, canvas, w: 0, h: 0, p: {}, scene: def.scenes[0].id, t: 0, running: false,
    T, P, css, fmt, lang: () => lang,
    done: (tid) => done(id, tid),
    stop: () => { api.running = false; readouts(L); },
    readout: () => readouts(L),
    arrow: (...a) => arrow(ctx, ...a), label: (...a) => label(ctx, ...a), line: (...a) => line(ctx, ...a),
    rect: (...a) => rect(ctx, ...a), circle: (...a) => circle(ctx, ...a), ground: (...a) => ground(ctx, ...a),
    grid: (...a) => grid(ctx, ...a), agv: (...a) => agv(ctx, ...a), box: (...a) => box(ctx, ...a),
    rot2, fk, frame: (...a) => frame(ctx, ...a), arm: (...a) => arm(ctx, ...a), robot: (...a) => robot(ctx, ...a),
    lidar: (...a) => lidar(ctx, ...a), plot: (...a) => plot(ctx, ...a),
  };
  L.api = api;
  if (is3d) setup3d(L);
  if (circuit) setupCircuit(L);
  def.tasks.forEach((t) => { t.ok = !!saved[id + ":" + t.id]; });
  LABS[id] = L; ORDER.push(id);
  // controls
  chips.forEach((b) => b.addEventListener("click", () => setScene(L, b.dataset.scene)));
  Object.entries(params).forEach(([pid, c]) => c.input.addEventListener("input", () => {
    api.p[pid] = +c.input.value; paintParams(L);
    safe(L, () => def.change && def.change(api, L.state, pid));
    if (!api.running) reset(L); else readouts(L);
  }));
  // "start" and "reset" are built in; any other button calls def.action(id, api, state).
  bar.querySelectorAll("[data-action]").forEach((b) => b.addEventListener("click", () => {
    const a = b.dataset.action;
    if (a === "start") start(L);
    else if (a === "reset") reset(L);
    else safe(L, () => def.action && def.action(a, api, L.state));
    readouts(L);
  }));
  setScene(L, def.scenes[0].id);
}

function fit(L) {
  const c = L.dom.canvas, r = c.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.width * (L.circuit ? 5 : 10) / 16));   // circuit labs: a short instrument strip under the circuit
  if (w !== L.api.w || h !== L.api.h) {
    L.api.w = w; L.api.h = h;
    if (L.is3d) { if (L.st) { L.st.renderer.setPixelRatio(dpr); L.st.resize(w, h); } }
    else { c.width = w * dpr; c.height = h * dpr; L.api.ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
  }
}

// ---------- circuit labs: CircuitJS (GPL-2.0, embedded without network) in a same-origin frame ----------
// def.circuit: the circuit in CircuitJS text form. api.cj: CircuitJS's own interface; api.v(label): voltage of a labelled
// node; api.setV(name, volts): an "external voltage" source; api.load(text): replace the circuit (e.g. a new resistor value).
const CJ_WAIT = {};
function setupCircuit(L) {
  const api = L.api, def = L.def;
  if (!window.WQ_CIRCUITJS) { fail(L.id, new Error("this page has no circuit simulator (view: 'circuit')")); return; }
  api.v = (name) => (api.cj ? api.cj.getNodeVoltage(name) : NaN);
  api.setV = (name, v) => { if (api.cj) api.cj.setExtVoltage(name, v); };
  api.load = (text) => { if (api.cj) api.cj.importCircuit(text, false); };
  api.simTime = () => (api.cj ? api.cj.getTime() : 0);
  CJ_WAIT[L.id] = (cj) => {
    api.cj = cj;
    if (active !== L.id) try { cj.setSimRunning(false); } catch (e) { /* older build */ }
    cj.onupdate = () => { if (L.ready && !L.broken && active === L.id) readouts(L); };
    safe(L, () => def.setupCircuit && def.setupCircuit(api));
    L.ready = true;
    reset(L);
  };
  const q = "?hideSidebar=true&hideInfoBox=false&whiteBackground=true&lang=zh&editable=true&running=true" + (def.circuitQuery || "");
  const cfg = "<script>window.CircuitJSQuery = " + JSON.stringify(q) + "; window.startCircuitText = " +
    JSON.stringify(def.circuit || "").replace(/</g, "\\u003c") + "; window.oncircuitjsloaded = function (c) { parent.WQ._cj(" + JSON.stringify(L.id) + ", c); };<\/script>";
  L.circuit.srcdoc = window.WQ_CIRCUITJS.replace("<!--WQ-CONFIG-->", cfg);
}

// ---------- 3D labs: the course's library models on a 3D stage (WQ3D engine, models embedded in the page) ----------
function setup3d(L) {
  const api = L.api, def = L.def;
  if (!window.WQ3D) { fail(L.id, new Error("this page has no 3D engine (view: '3d' needs the models listed in models: [...])")); return; }
  const E = window.WQ3D;
  const st = E.stage(L.dom.canvas, { width: 800, height: 500, theme: "light" });
  L.st = st;
  api.three = E.THREE; api.st = st; api.m = {}; api.keep = {};   // keep: 3D objects that outlive reset (traces…)
  api.trace = (color) => E.trace(st, color);
  api.axes = (h, link, size) => E.axes(h, link, size);
  // Frame what the robots can reach (their workspace), so moving joints never leaves the picture.
  const reachBox = (h) => {
    const b = h.box();
    const r = ((h.entry.robot || {}).reach_mm || 0) / 1000;
    if (r > 0) {
      const c = h.point(h.entry.root);
      b.union(new E.THREE.Box3(new E.THREE.Vector3(c.x - r, 0, c.z - r), new E.THREE.Vector3(c.x + r, c.y + r, c.z + r)));
    }
    return b;
  };
  api.view = (az = 35, el = 22, fill = 0.8, target) => {
    const b = new E.THREE.Box3();
    Object.values(api.m).forEach((h) => { if (!target || h === target) b.union(reachBox(h)); });
    if (!b.isEmpty()) E.frame(st, b, az, el, fill);
    if (L.orbit) { L.orbit.target.copy(b.getCenter(new E.THREE.Vector3())); L.orbit.update(); }
  };
  const models = window.WQ_MODELS || {};
  const ids = def.models || [];
  Promise.all(ids.map(async (mid, k) => {
    const m = models[mid];
    if (!m) throw new Error(`model ${mid} is not in this page (use the ids listed for this course)`);
    api.m[mid] = await E.loadModel(st, m.glb, m.entry, { x: k * 1.2 });
    api.m[mid].rows = m.motion || [];
  })).then(() => {
    api.view();
    try {
      L.orbit = new E.OrbitControls(st.camera, L.dom.canvas);
      L.orbit.enableDamping = true;
    } catch (e) { /* view rotation is optional */ }
    api.view();
    safe(L, () => def.setup3d && def.setup3d(api, api.keep));
    L.ready = true;
    reset(L);
  }).catch((e) => fail(L.id, e));
}

function show(id) {
  if (!LABS[id]) return;
  active = id;
  ORDER.forEach((k) => { LABS[k].dom.tab.setAttribute("aria-selected", String(k === id)); LABS[k].dom.sec.hidden = k !== id; });
  ORDER.forEach((k) => { const c = LABS[k].api && LABS[k].api.cj; if (c) try { c.setSimRunning(k === id); } catch (e) { /* older build */ } });   // hidden circuits pause
  try { history.replaceState(null, "", "#lab-" + id); } catch (e) { /* ignore */ }
  store.set(KEY + "-tab", id);
}

function check(def) {   // clear messages for the lab author (the checker reports them)
  const need = (c, m) => { if (!c) throw new Error("WQ.lab: " + m); };
  need(def && typeof def === "object", "needs an object");
  need(Array.isArray(def.title) && def.title.length === 2, "title must be [中文, English]");
  need(Array.isArray(def.scenes) && def.scenes.length >= 1 && def.scenes.length <= 4, "scenes: 1-4 scenes");
  def.scenes.forEach((s) => need(s.id && Array.isArray(s.name), "every scene needs id and name [zh, en]"));
  need(Array.isArray(def.params) && def.params.length <= 8, "params: at most 8");
  def.params.forEach((p) => need(p.id && Array.isArray(p.name) && isFinite(p.min) && isFinite(p.max) && isFinite(p.value) && p.max > p.min,
    `param ${p.id}: needs id, name [zh, en], min < max, value`));
  need(Array.isArray(def.tasks) && def.tasks.length >= 2 && def.tasks.length <= 6, "tasks: 2-6 tasks");
  def.tasks.forEach((t) => need(t.id && Array.isArray(t.text), "every task needs id and text [zh, en]"));
  need(typeof def.draw === "function", "draw(api, state) is required");
}

window.WQ = {
  speed: 1,                          // physics steps per frame (the checker speeds labs up)
  begin(id) { current = id; },
  lab(def) {
    const id = current || "1-1";
    current = null;
    try { check(def); build(id, def); } catch (e) { fail(id, e); if (!LABS[id]) { const d = el("div", "empty", String(e.message || e)); $("labs").appendChild(d); } }
  },
  fail,
  _cj(id, c) { const f = CJ_WAIT[id]; if (f) { delete CJ_WAIT[id]; const L = LABS[id]; if (L) safe(L, () => f(c)); } },
  status() {
    const labs = {};
    ORDER.forEach((id) => {
      const L = LABS[id];
      labs[id] = { broken: L.broken, ready: !!L.ready, view: L.is3d ? "3d" : L.circuit ? "circuit" : "2d", scenes: L.def.scenes.map((s) => s.id), params: L.def.params.map((p) => p.id),
        tasks: Object.fromEntries(L.def.tasks.map((t) => [t.id, !!t.ok])), demos: Object.fromEntries(L.def.tasks.map((t) => [t.id, t.demo || null])) };
    });
    return { errors: errors.slice(), active, labs };
  },
  // Do what a task's demo says, through the same controls a student uses (for the automatic trial run).
  demo(id, tid) {
    const L = LABS[id]; show(id);
    const t = L.def.tasks.find((x) => x.id === tid);
    const d = (t && t.demo) || {};
    if (d.scene) { const chip = L.dom.chips.find((b) => b.dataset.scene === d.scene); if (chip) chip.click(); }
    Object.entries(d.set || {}).forEach(([pid, v]) => {
      const c = L.dom.params[pid]; if (!c) return;
      c.input.value = v; c.input.dispatchEvent(new Event("input"));
    });
    (d.press || ["start"]).forEach((a) => { const b = L.dom.sec.querySelector(`[data-action="${a}"]`); if (b) b.click(); });
    return d.wait || 5;
  },
  reset(id) { const L = LABS[id]; if (L) { L.def.tasks.forEach((t) => { t.ok = false; }); paintTasks(); reset(L); } },
  show,
};

// ---------- loop, tabs, WenQuest lab protocol ----------
function begin() {
  if (!ORDER.length) return;
  const pick = (v) => { const k = String(v || "").replace(".", "-"); if (LABS[k] && k !== active) show(k); };
  addEventListener("message", (e) => { const d = e.data || {}; if (d && d.type === "wq-lab") pick(d.lab); });
  addEventListener("hashchange", () => pick((location.hash.match(/lab-(\d+-\d+)/) || [])[1]));
  const fromHash = (location.hash.match(/lab-(\d+-\d+)/) || [])[1];
  const last = store.get(KEY + "-tab");
  show(LABS[fromHash] ? fromHash : LABS[last] ? last : ORDER[0]);
  applyLang();
  let lastT = performance.now();
  function loop(now) {
    const dt = Math.min(0.05, (now - lastT) / 1000); lastT = now;
    const L = LABS[active];
    if (L && !L.broken && L.ready) {
      fit(L);
      const n = Math.max(1, Math.min(20, Math.round(WQ.speed)));
      for (let i = 0; i < n && L.api.running; i++) {
        L.api.t += dt;
        safe(L, () => L.def.update && L.def.update(dt, L.api, L.state));
      }
      if (L.api.running || !L.drawn || L.api.w !== L.lastW) { readouts(L); }
      if (L.is3d) {
        safe(L, () => { L.def.draw(L.api, L.state); if (L.orbit) L.orbit.update(); L.st.render(); });
      } else {
        safe(L, () => { L.api.ctx.clearRect(0, 0, L.api.w, L.api.h); L.def.draw(L.api, L.state); });
      }
      L.drawn = true; L.lastW = L.api.w;
    }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
}
window.addEventListener("error", (e) => errors.push(String(e.message || e)));
window.WQ.start = begin;
})();
