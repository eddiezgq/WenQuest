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

// ---------- linear algebra (《线性代数》第 10 轮): small dense matrices as arrays of rows ----------
// The lab computes with these and draws with plane / heat / image / bars, so every linear-algebra lab looks alike.
const LA = {
  zeros: (m, n) => Array.from({ length: m }, () => new Array(n).fill(0)),
  eye: (n) => Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))),
  T: (A) => A[0].map((_, j) => A.map((r) => r[j])),
  mul: (A, B) => A.map((r) => B[0].map((_, j) => r.reduce((s, a, k) => s + a * B[k][j], 0))),
  mv: (A, x) => A.map((r) => r.reduce((s, a, k) => s + a * x[k], 0)),
  dot: (a, b) => a.reduce((s, x, i) => s + x * b[i], 0),
  norm: (a) => Math.sqrt(a.reduce((s, x) => s + x * x, 0)),
  fro: (A) => Math.sqrt(A.reduce((s, r) => s + r.reduce((t, x) => t + x * x, 0), 0)),
  sub: (A, B) => A.map((r, i) => r.map((x, j) => x - B[i][j])),
  det(A) {   // Gaussian elimination with partial pivoting
    const M = A.map((r) => r.slice()), n = M.length; let d = 1;
    for (let k = 0; k < n; k++) {
      let p = k; for (let i = k + 1; i < n; i++) if (Math.abs(M[i][k]) > Math.abs(M[p][k])) p = i;
      if (M[p][k] === 0) return 0;
      if (p !== k) { [M[p], M[k]] = [M[k], M[p]]; d = -d; }
      d *= M[k][k];
      for (let i = k + 1; i < n; i++) { const f = M[i][k] / M[k][k]; for (let j = k; j < n; j++) M[i][j] -= f * M[k][j]; }
    }
    return d;
  },
  svd(A) {   // one-sided Jacobi (Hestenes): {U: m×p, s: [p] largest first, V: n×p}, p = min(m, n); each v_i's largest entry > 0
    const m = A.length, n = A[0].length;
    if (m < n) { const r = LA.svd(LA.T(A)); return { U: r.V, s: r.s, V: r.U }; }
    const W = A.map((r) => r.slice()), V = LA.eye(n);
    for (let sweep = 0; sweep < 60; sweep++) {
      let off = 0;
      for (let i = 0; i < n - 1; i++) for (let j = i + 1; j < n; j++) {
        let a = 0, b = 0, g = 0;
        for (let k = 0; k < m; k++) { a += W[k][i] * W[k][i]; b += W[k][j] * W[k][j]; g += W[k][i] * W[k][j]; }
        if (Math.abs(g) <= 1e-15 * Math.sqrt(a * b) || g === 0) continue;
        off = Math.max(off, Math.abs(g) / Math.sqrt(a * b));
        const z = (b - a) / (2 * g), t = Math.sign(z || 1) / (Math.abs(z) + Math.sqrt(1 + z * z)), c = 1 / Math.sqrt(1 + t * t), s = c * t;
        for (let k = 0; k < m; k++) { const x = W[k][i], y = W[k][j]; W[k][i] = c * x - s * y; W[k][j] = s * x + c * y; }
        for (let k = 0; k < n; k++) { const x = V[k][i], y = V[k][j]; V[k][i] = c * x - s * y; V[k][j] = s * x + c * y; }
      }
      if (off < 1e-13) break;
    }
    const sv = Array.from({ length: n }, (_, j) => Math.sqrt(W.reduce((t, r) => t + r[j] * r[j], 0)));
    const order = sv.map((_, j) => j).sort((x, y) => sv[y] - sv[x]);
    const U = LA.zeros(m, n), Vs = LA.zeros(n, n), s = order.map((j) => sv[j]);
    order.forEach((j, c) => {
      let big = 0; for (let k = 0; k < n; k++) if (Math.abs(V[k][j]) > Math.abs(big) + 1e-12) big = V[k][j];
      const f = big < 0 ? -1 : 1;
      for (let k = 0; k < n; k++) Vs[k][c] = f * V[k][j];
      for (let k = 0; k < m; k++) U[k][c] = sv[j] > 1e-300 ? f * W[k][j] / sv[j] : 0;
    });
    return { U, s, V: Vs };
  },
  rank(A, tol) { const s = LA.svd(A).s; const t = tol ?? Math.max(A.length, A[0].length) * 2.2e-16 * (s[0] || 0); return s.filter((x) => x > t).length; },
  lowrank({ U, s, V }, k) {   // A_k = sum of the first k terms σ_i u_i v_iᵀ
    return U.map((ur) => V.map((vr) => { let x = 0; for (let i = 0; i < k; i++) x += s[i] * ur[i] * vr[i]; return x; }));
  },
  pinv(A, tol) {   // A⁺ = V Σ⁺ Uᵀ, singular values ≤ tol treated as zero
    const { U, s, V } = LA.svd(A), t = tol ?? Math.max(A.length, A[0].length) * 2.2e-16 * (s[0] || 0);
    return V.map((vr) => U.map((ur) => s.reduce((x, si, i) => (si > t ? x + vr[i] * ur[i] / si : x), 0)));
  },
  eigSym(A) {   // symmetric matrices, cyclic Jacobi: {values ascending, vectors as columns}
    const n = A.length, M = A.map((r) => r.slice()), Q = LA.eye(n);
    for (let sweep = 0; sweep < 60; sweep++) {
      let off = 0; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) off += M[i][j] * M[i][j];
      if (off < 1e-26) break;
      for (let p = 0; p < n - 1; p++) for (let q = p + 1; q < n; q++) {
        if (Math.abs(M[p][q]) < 1e-300) continue;
        const th = (M[q][q] - M[p][p]) / (2 * M[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1));
        const c = 1 / Math.sqrt(t * t + 1), s = t * c;
        for (let k = 0; k < n; k++) { const a = M[k][p], b = M[k][q]; M[k][p] = c * a - s * b; M[k][q] = s * a + c * b; }
        for (let k = 0; k < n; k++) { const a = M[p][k], b = M[q][k]; M[p][k] = c * a - s * b; M[q][k] = s * a + c * b; }
        for (let k = 0; k < n; k++) { const a = Q[k][p], b = Q[k][q]; Q[k][p] = c * a - s * b; Q[k][q] = s * a + c * b; }
      }
    }
    const idx = M.map((_, i) => i).sort((x, y) => M[x][x] - M[y][y]);
    return { values: idx.map((i) => M[i][i]), vectors: Q.map((r) => idx.map((i) => r[i])) };
  },
  str(A, d = 3) { return "[" + A.map((r) => r.map((x) => fmt(x, d)).join(", ")).join("; ") + "]"; },
  vstr(v, d = 3) { return "(" + v.map((x) => fmt(x, d)).join(", ") + ")"; },
};
function plane(ctx, o) {   // a 2D coordinate plane: o = {cx, cy, s: pixels per unit, w, h}
  const X = (x, y) => [o.cx + o.s * x, o.cy - o.s * y];
  const P = {
    X,
    axes(color) { const c = color || css("--muted"); line(ctx, 0, o.cy, o.w, o.cy, c, 1); line(ctx, o.cx, 0, o.cx, o.h, c, 1); },
    grid(M, opt) {   // images of the lines x = i and y = j (|i|, |j| ≤ n) under the 2×2 matrix M
      const q = opt || {}, n = q.n || 6, A = M || [[1, 0], [0, 1]], col = q.color || css("--blue");
      ctx.globalAlpha = q.alpha ?? 0.45;
      for (let i = -n; i <= n; i++) {
        let a = LA.mv(A, [i, -n]), b = LA.mv(A, [i, n]); line(ctx, ...X(...a), ...X(...b), i ? col : css("--ink"), i ? 1 : 1.6);
        a = LA.mv(A, [-n, i]); b = LA.mv(A, [n, i]); line(ctx, ...X(...a), ...X(...b), i ? col : css("--ink"), i ? 1 : 1.6);
      }
      ctx.globalAlpha = 1;
    },
    vec(v, color, name, width) { const e = X(v[0], v[1]); arrow(ctx, o.cx, o.cy, e[0], e[1], color, width || 3);
      if (name) label(ctx, name, e[0] + 8, e[1] - 10, color, 14); },
    curve(pts, color, width, fill, dash) {
      ctx.beginPath(); pts.forEach((p, i) => { const [x, y] = X(p[0], p[1]); if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); }); ctx.closePath();
      if (fill) { ctx.fillStyle = fill; ctx.fill(); }
      ctx.strokeStyle = color || css("--ink"); ctx.lineWidth = width || 2; ctx.setLineDash(dash || []); ctx.stroke(); ctx.setLineDash([]);
    },
    circle(M, color, fill, dash, r = 1) {   // the image of the circle of radius r under M (an ellipse)
      const A = M || [[1, 0], [0, 1]];
      P.curve(Array.from({ length: 121 }, (_, k) => LA.mv(A, [r * Math.cos(k * Math.PI / 60), r * Math.sin(k * Math.PI / 60)])), color, 2, fill, dash);
    },
    point(v, color, name) { const [x, y] = X(v[0], v[1]); circle(ctx, x, y, 4.5, color, css("--ink")); if (name) label(ctx, name, x + 8, y - 9, color, 13); },
  };
  return P;
}
const _img = { c: null };
function heat(ctx, x, y, w, h, M, opt) {   // a matrix as coloured cells: red > 0, blue < 0 (or grey 0..1 with opt.grey)
  const q = opt || {}, m = M.length, n = M[0].length, cw = w / n, ch = h / m;
  const big = q.max || Math.max(1e-12, ...M.map((r) => Math.max(...r.map(Math.abs))));
  if (m * n > 900 && !q.numbers) {   // large matrices: one pixel per entry, scaled up (fast enough for every frame)
    if (!_img.c) _img.c = document.createElement("canvas");
    const c = _img.c; c.width = n; c.height = m;
    const g = c.getContext("2d"), d = g.createImageData(n, m);
    for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) {
      const v = Math.max(-1, Math.min(1, M[i][j] / big)), k = 4 * (i * n + j), a = Math.abs(v);
      const rgb = q.grey ? [255 * (1 - Math.max(0, v)), 255 * (1 - Math.max(0, v)), 255 * (1 - Math.max(0, v))]
        : v >= 0 ? [255 - a * (255 - 207), 255 - a * (255 - 34), 255 - a * (255 - 46)] : [255 - a * (255 - 31), 255 - a * (255 - 111), 255 - a * (255 - 235)];
      d.data[k] = rgb[0]; d.data[k + 1] = rgb[1]; d.data[k + 2] = rgb[2]; d.data[k + 3] = 255;
    }
    g.putImageData(d, 0, 0);
    ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(c, x, y, w, h); ctx.restore();
    rect(ctx, x, y, w, h, null, css("--line"));
    return;
  }
  for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) {
    const v = Math.max(-1, Math.min(1, M[i][j] / big));
    const col = q.grey ? `rgb(${Math.round(255 * (1 - Math.max(0, v)))},${Math.round(255 * (1 - Math.max(0, v)))},${Math.round(255 * (1 - Math.max(0, v)))})`
      : v >= 0 ? `rgba(207,34,46,${Math.abs(v)})` : `rgba(31,111,235,${Math.abs(v)})`;
    rect(ctx, x + j * cw, y + i * ch, cw + 0.5, ch + 0.5, col);
    if (q.numbers && cw > 26) label(ctx, fmt(M[i][j], q.digits ?? 2), x + (j + 0.5) * cw, y + (i + 0.5) * ch, css("--ink"), Math.min(13, ch * 0.45), "center");
  }
  rect(ctx, x, y, w, h, null, css("--line"));
}
function image(ctx, x, y, w, h, pix) {   // a grey image: pix = rows of values, 0 black … 1 white (clipped)
  const m = pix.length, n = pix[0].length;
  if (!_img.c) _img.c = document.createElement("canvas");
  const c = _img.c; c.width = n; c.height = m;
  const g = c.getContext("2d"), d = g.createImageData(n, m);
  for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) {
    const v = Math.round(255 * Math.max(0, Math.min(1, pix[i][j]))), k = 4 * (i * n + j);
    d.data[k] = d.data[k + 1] = d.data[k + 2] = v; d.data[k + 3] = 255;
  }
  g.putImageData(d, 0, 0);
  ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(c, x, y, w, h); ctx.restore();
  rect(ctx, x, y, w, h, null, css("--line"));
}
function bars(ctx, x, y, w, h, values, opt) {   // a bar chart (e.g. singular values); opt = {log, mark: k (first k bars highlighted), label}
  const q = opt || {}, n = values.length, bw = w / n;
  const f = q.log ? (v) => Math.log10(Math.max(v, 1e-16)) : (v) => v;
  const vs = values.map(f), top = Math.max(...vs), bot = q.log ? Math.min(...vs) - 0.3 : 0;
  rect(ctx, x, y, w, h, null, css("--grid"));
  values.forEach((v, i) => { const hh = (f(v) - bot) / ((top - bot) || 1) * h;
    rect(ctx, x + i * bw + bw * 0.12, y + h - hh, bw * 0.76, hh, q.mark != null && i < q.mark ? css("--accent") : css("--muted")); });
  if (q.label) label(ctx, q.label, x + 4, y + 10, css("--muted"), 12);
}

// ---------- calculus (《微积分》第 12 轮): the one-variable bench ----------
// CALC computes (difference quotients, dual numbers, quadrature, root finding, seeded noise);
// graph() draws in world coordinates (axes with ticks, function curves, tangents, secants, Riemann boxes).
function Dual(a, b) { this.a = a; this.b = b; }   // a + b·ε with ε² = 0: value and derivative together (forward-mode AD)
const D = (x) => (x instanceof Dual ? x : new Dual(+x, 0));
const CALC = {
  diff(f, x, h = 1e-5, kind = "central") {   // difference quotients D⁺, D⁻, D⁰ (符号约定 五)
    if (kind === "forward") return (f(x + h) - f(x)) / h;
    if (kind === "backward") return (f(x) - f(x - h)) / h;
    return (f(x + h) - f(x - h)) / (2 * h);
  },
  diff2(f, x, h = 1e-4) { return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h); },
  // forward-mode automatic differentiation: CALC.ad(x => CALC.d.sin(CALC.d.mul(x, x)), 1.2) → [value, derivative]
  ad(f, x) { const r = D(f(new Dual(x, 1))); return [r.a, r.b]; },
  d: {
    v: (x) => new Dual(x, 1), c: (x) => new Dual(x, 0),
    add: (x, y) => { x = D(x); y = D(y); return new Dual(x.a + y.a, x.b + y.b); },
    sub: (x, y) => { x = D(x); y = D(y); return new Dual(x.a - y.a, x.b - y.b); },
    mul: (x, y) => { x = D(x); y = D(y); return new Dual(x.a * y.a, x.b * y.a + x.a * y.b); },
    div: (x, y) => { x = D(x); y = D(y); return new Dual(x.a / y.a, (x.b * y.a - x.a * y.b) / (y.a * y.a)); },
    pow: (x, n) => { x = D(x); return new Dual(Math.pow(x.a, n), n * Math.pow(x.a, n - 1) * x.b); },
    sin: (x) => { x = D(x); return new Dual(Math.sin(x.a), Math.cos(x.a) * x.b); },
    cos: (x) => { x = D(x); return new Dual(Math.cos(x.a), -Math.sin(x.a) * x.b); },
    exp: (x) => { x = D(x); const e = Math.exp(x.a); return new Dual(e, e * x.b); },
    log: (x) => { x = D(x); return new Dual(Math.log(x.a), x.b / x.a); },
    sqrt: (x) => { x = D(x); const r = Math.sqrt(x.a); return new Dual(r, x.b / (2 * r)); },
  },
  simpson(f, a, b, n = 200) { if (n % 2) n++; const h = (b - a) / n; let s = f(a) + f(b);
    for (let i = 1; i < n; i++) s += (i % 2 ? 4 : 2) * f(a + i * h); return s * h / 3; },
  riemann(f, a, b, n, rule = "mid") {   // left / right / mid
    const h = (b - a) / n, off = rule === "left" ? 0 : rule === "right" ? 1 : 0.5; let s = 0;
    for (let i = 0; i < n; i++) s += f(a + (i + off) * h); return s * h;
  },
  bisect(f, a, b, tol = 1e-10, max = 200) { let fa = f(a); const steps = [];
    for (let k = 0; k < max && b - a > tol; k++) { const m = (a + b) / 2, fm = f(m); steps.push([a, b]);
      if (fa * fm <= 0) b = m; else { a = m; fa = fm; } }
    return { x: (a + b) / 2, steps }; },
  newton(f, x, df, tol = 1e-12, max = 50) { const steps = [x];
    for (let k = 0; k < max; k++) { const d = df ? df(x) : CALC.diff(f, x), dx = f(x) / d; x -= dx; steps.push(x); if (Math.abs(dx) < tol) break; }
    return { x, steps }; },
  rng(seed = 1) {   // mulberry32: the same seed gives the same numbers in every browser (and in the book's programs)
    let s = seed >>> 0;
    const u = () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    return { u, gauss: () => { let a = 0; while (a === 0) a = u(); return Math.sqrt(-2 * Math.log(a)) * Math.cos(2 * Math.PI * u()); } };
  },
  ticks(lo, hi, n = 6) {   // "nice" tick values (1, 2, 5 × 10ᵏ)
    const raw = (hi - lo) / Math.max(1, n), p = Math.pow(10, Math.floor(Math.log10(raw || 1))), m = raw / p;
    const step = (m < 1.5 ? 1 : m < 3 ? 2 : m < 7 ? 5 : 10) * p, out = [];
    for (let v = Math.ceil(lo / step) * step; v <= hi + step * 1e-9; v += step) out.push(Math.abs(v) < step * 1e-9 ? 0 : v);
    return out;
  },
};
function graph(ctx, o) {   // o = {x, y, w, h (pixels), xmin, xmax, ymin, ymax, xlabel, ylabel, ticks: true}
  const X = (v) => o.x + (v - o.xmin) / (o.xmax - o.xmin) * o.w, Y = (v) => o.y + o.h - (v - o.ymin) / (o.ymax - o.ymin) * o.h;
  const clip = (fn) => { ctx.save(); ctx.beginPath(); ctx.rect(o.x, o.y, o.w, o.h); ctx.clip(); fn(); ctx.restore(); };
  const tickTxt = (v) => { const a = Math.abs(v); return a === 0 ? "0" : a >= 1e4 || a < 1e-3 ? v.toExponential(0) : String(+v.toPrecision(4)); };
  const G = {
    X, Y, o,
    axes() {
      rect(ctx, o.x, o.y, o.w, o.h, null, css("--grid"));
      const mu = css("--muted");
      if (o.ticks !== false) {
        CALC.ticks(o.xmin, o.xmax, Math.max(3, Math.round(o.w / 90))).forEach((v) => { line(ctx, X(v), o.y + o.h, X(v), o.y + o.h + 4, mu, 1);
          label(ctx, tickTxt(v), X(v), o.y + o.h + 15, mu, 11, "center"); });
        CALC.ticks(o.ymin, o.ymax, Math.max(3, Math.round(o.h / 60))).forEach((v) => { line(ctx, o.x - 4, Y(v), o.x, Y(v), mu, 1);
          label(ctx, tickTxt(v), o.x - 6, Y(v) + 4, mu, 11, "right"); });
      }
      if (o.ymin < 0 && o.ymax > 0) line(ctx, o.x, Y(0), o.x + o.w, Y(0), mu, 1);
      if (o.xmin < 0 && o.xmax > 0) line(ctx, X(0), o.y, X(0), o.y + o.h, mu, 1);
      if (o.xlabel) label(ctx, o.xlabel, o.x + o.w, o.y + o.h + 28, mu, 12, "right");
      if (o.ylabel) label(ctx, o.ylabel, o.x + 4, o.y - 6, mu, 12, "left");
      return G;
    },
    fn(f, color, width = 2, dash, a = o.xmin, b = o.xmax) {   // one sample per pixel; breaks the line at jumps and non-finite values
      clip(() => {
        ctx.strokeStyle = color || css("--accent"); ctx.lineWidth = width; ctx.setLineDash(dash || []); ctx.beginPath();
        const n = Math.max(2, Math.ceil((X(b) - X(a)) * 1.5)); let pen = false, lastY = 0;
        for (let i = 0; i <= n; i++) {
          const x = a + (b - a) * i / n, y = f(x), py = Y(y);
          if (!isFinite(y) || (pen && Math.abs(py - lastY) > o.h * 0.9)) { pen = false; if (!isFinite(y)) continue; }
          if (pen) ctx.lineTo(X(x), py); else ctx.moveTo(X(x), py);
          pen = true; lastY = py;
        }
        ctx.stroke(); ctx.setLineDash([]);
      });
      return G;
    },
    pts(points, color, width = 2, dash) {
      clip(() => { ctx.strokeStyle = color || css("--ink"); ctx.lineWidth = width; ctx.setLineDash(dash || []); ctx.beginPath();
        points.forEach((p, i) => (i ? ctx.lineTo(X(p[0]), Y(p[1])) : ctx.moveTo(X(p[0]), Y(p[1])))); ctx.stroke(); ctx.setLineDash([]); });
      return G;
    },
    dots(points, color, r = 2.5) { clip(() => points.forEach((p) => circle(ctx, X(p[0]), Y(p[1]), r, color || css("--ink")))); return G; },
    line(x0, y0, m, color, width = 2, dash) {   // the whole line through (x0, y0) with slope m, clipped to the box
      return G.pts([[o.xmin, y0 + m * (o.xmin - x0)], [o.xmax, y0 + m * (o.xmax - x0)]], color, width, dash);
    },
    seg(x0, y0, x1, y1, color, width = 2, dash) { return G.pts([[x0, y0], [x1, y1]], color, width, dash); },
    vline(x, color, dash = [4, 4]) { line(ctx, X(x), o.y, X(x), o.y + o.h, color || css("--muted"), 1, dash); return G; },
    hline(y, color, dash = [4, 4]) { line(ctx, o.x, Y(y), o.x + o.w, Y(y), color || css("--muted"), 1, dash); return G; },
    point(x, y, color, name, dx = 8, dy = -9) {
      if (x < o.xmin || x > o.xmax || y < o.ymin || y > o.ymax) return G;
      circle(ctx, X(x), Y(y), 4.5, color || css("--accent"), css("--ink")); if (name) label(ctx, name, X(x) + dx, Y(y) + dy, color || css("--ink"), 13);
      return G;
    },
    riemann(f, a, b, n, rule = "mid", fill = "rgba(31,119,180,0.18)", stroke) {
      const h = (b - a) / n, off = rule === "left" ? 0 : rule === "right" ? 1 : 0.5;
      clip(() => { for (let i = 0; i < n; i++) { const xa = a + i * h, v = f(xa + off * h);
        rect(ctx, X(xa), Math.min(Y(0), Y(v)), X(xa + h) - X(xa), Math.abs(Y(v) - Y(0)), fill, stroke || css("--blue")); } });
      return G;
    },
    area(f, a, b, fill = "rgba(201,143,0,0.18)") {
      clip(() => { const n = Math.max(2, Math.ceil(X(b) - X(a))); ctx.beginPath(); ctx.moveTo(X(a), Y(0));
        for (let i = 0; i <= n; i++) { const x = a + (b - a) * i / n; ctx.lineTo(X(x), Y(f(x))); }
        ctx.lineTo(X(b), Y(0)); ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); });
      return G;
    },
    text(s, x, y, color, size = 12, align = "left") { label(ctx, s, X(x), Y(y), color || css("--ink"), size, align); return G; },
  };
  return G;
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
    la: LA, plane: (o) => plane(ctx, o), heat: (...a) => heat(ctx, ...a), image: (...a) => image(ctx, ...a), bars: (...a) => bars(ctx, ...a),
    calc: CALC, graph: (o) => graph(ctx, o),
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
