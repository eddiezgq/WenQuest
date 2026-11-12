/* 白板三维简画：人物、场景、讲故事（第 162 轮）。
 * 手绘线条（rough.js）画三维人物和场景：每一帧按镜头投影，用画家算法（远的先画）排遮挡。
 * 只按时间决定画面（render(t)），网页播放和逐帧出视频用同一份代码。
 * 数据：STORY = {size:[W,H], cast:{名字:{look}}, shots:[{t0,t1,scene,cam:[{t,pos,look,fov}],chars:{名字:[{t,...}]},props:{id:[{t,...}]},bubbles,subs,title}]}
 */
(function (global) {
  'use strict';
  const { sin, cos, sqrt, PI, abs, min, max, atan2 } = Math;
  const D = PI / 180;
  const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
  const ease = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
  const lerp = (a, b, k) => a + (b - a) * k;
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const norm = (a) => { const l = sqrt(dot(a, a)) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  const vlerp = (a, b, k) => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];
  // 3×3 matrices, row-major arrays of 9
  const M = {
    x: (a) => [1, 0, 0, 0, cos(a), -sin(a), 0, sin(a), cos(a)],
    y: (a) => [cos(a), 0, sin(a), 0, 1, 0, -sin(a), 0, cos(a)],
    z: (a) => [cos(a), -sin(a), 0, sin(a), cos(a), 0, 0, 0, 1],
    m: (A, B) => { const C = []; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) C.push(A[i * 3] * B[j] + A[i * 3 + 1] * B[3 + j] + A[i * 3 + 2] * B[6 + j]); return C; },
    v: (A, v) => [A[0] * v[0] + A[1] * v[1] + A[2] * v[2], A[3] * v[0] + A[4] * v[1] + A[5] * v[2], A[6] * v[0] + A[7] * v[1] + A[8] * v[2]],
  };
  function hash(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0) % 2147483647 + 1; }
  function shade(hex, k) {   // k>0 lighter, k<0 darker
    const n = parseInt(hex.slice(1), 16); let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
    const f = (c) => Math.round(k > 0 ? c + (255 - c) * k : c * (1 + k));
    return '#' + ((1 << 24) + (f(r) << 16) + (f(g) << 8) + f(b)).toString(16).slice(1);
  }
  function hull(P) {
    if (P.length < 3) return P.slice();
    const p = P.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const c = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], up = [];
    for (const q of p) { while (lo.length >= 2 && c(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
    for (let i = p.length - 1; i >= 0; i--) { const q = p[i]; while (up.length >= 2 && c(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
    up.pop(); lo.pop(); return lo.concat(up);
  }
  const f1 = (x) => Math.round(x * 10) / 10;
  function smoothD(pts, closed = true) {   // Catmull-Rom through points → cubic path
    const n = pts.length; if (n < 2) return '';
    let d = `M${f1(pts[0][0])} ${f1(pts[0][1])}`;
    const P = (i) => pts[closed ? (i + n) % n : clamp(i, 0, n - 1)];
    const m = closed ? n : n - 1;
    for (let i = 0; i < m; i++) {
      const p0 = P(i - 1), p1 = P(i), p2 = P(i + 1), p3 = P(i + 2);
      d += `C${f1(p1[0] + (p2[0] - p0[0]) / 6)} ${f1(p1[1] + (p2[1] - p0[1]) / 6)} ${f1(p2[0] - (p3[0] - p1[0]) / 6)} ${f1(p2[1] - (p3[1] - p1[1]) / 6)} ${f1(p2[0])} ${f1(p2[1])}`;
    }
    return d + (closed ? 'Z' : '');
  }
  const polyD = (pts, closed = true) => 'M' + pts.map((p) => f1(p[0]) + ' ' + f1(p[1])).join('L') + (closed ? 'Z' : '');

  // ───────────── camera ─────────────
  function Camera(pos, look, fov, W, H) {
    const fw = norm(sub(look, pos)), rt = norm(cross(fw, [0, 1, 0])), up = cross(rt, fw);
    const f = (H / 2) / Math.tan((fov || 42) * D / 2);
    return {
      pos, fw, f, W, H,
      p(v) { const d = sub(v, pos); const z = dot(d, fw); const zz = max(z, 0.05); return [W / 2 + f * dot(d, rt) / zz, H / 2 - f * dot(d, up) / zz, z]; },
      depth(v) { return dot(sub(v, pos), fw); },
      k(v) { return f / max(this.depth(v), 0.05); },   // pixels per metre at v
      facing(pt, n) { return dot(n, sub(pos, pt)) > 0; },
    };
  }

  // ───────────── drawing list ─────────────
  // item: {z (depth, far drawn first), fill d, stroke d, ...}
  function Canvas(cam, gen) {
    const items = [];
    let order = 0;
    const api = {
      items, cam,
      shape(z, d, o) {   // d: path; o: {fill, stroke, w, seed, rough, layer, alpha, smoothFill}
        items.push({ z, d, o, n: order++ });
      },
      blob(z, pts2, o) { if (pts2.length >= 3) api.shape(z, o.poly ? polyD(pts2) : smoothD(pts2), o); },
      line(z, pts2, o) { if (pts2.length >= 2) items.push({ z, d: o.smooth ? smoothD(pts2, false) : polyD(pts2, false), o: Object.assign({ fill: null }, o), n: order++ }); },
      svg(z, raw, layer) { items.push({ z, raw, o: { layer: layer || 0 }, n: order++ }); },
      render(reveal, focus) {
        items.sort((a, b) => (a.o.layer || 0) - (b.o.layer || 0) || b.z - a.z || a.n - b.n);
        const N = items.length; let out = '', blurOpen = false;
        const far = focus == null ? 1e9 : focus + 1.1;
        items.forEach((it, i) => {
          const bl = it.z > far;
          if (bl && !blurOpen) { out += '<g filter="url(#wq-dof)">'; blurOpen = true; }
          if (!bl && blurOpen) { out += '</g>'; blurOpen = false; }
          let f = 1;
          if (reveal < 1) f = clamp((reveal * (N + 12) - i) / 12);
          if (f <= 0) return;
          if (it.raw) { out += f < 1 ? `<g opacity="${f1(f)}">${it.raw}</g>` : it.raw; return; }
          const o = it.o;
          if (o.fill) {
            const fa = (o.alpha == null ? 1 : o.alpha) * clamp(f * 2 - 1);
            if (fa > 0) out += `<path d="${it.d}" fill="${o.fill}"${fa < 1 ? ` fill-opacity="${f1(fa * 100) / 100}"` : ''}${o.off === false ? '' : ' transform="translate(1.6 1.2)"'}/>`;
          }
          if (o.stroke) {
            const w = o.w || 2;
            let ds;
            if (o.rough === 0) ds = [it.d];
            else {
              const dr = gen.path(it.d, { stroke: o.stroke, strokeWidth: w, roughness: o.rough == null ? 0.7 : o.rough, bowing: 0.6, seed: o.seed || 1, fill: undefined, disableMultiStroke: !!o.single, preserveVertices: true });
              ds = gen.toPaths(dr).filter((p) => p.stroke && p.stroke !== 'none').map((p) => p.d);
            }
            const dash = f < 1 ? ` pathLength="1" stroke-dasharray="${f1(f * 1000) / 1000} 1"` : '';
            for (const d of ds) out += `<path d="${d}" fill="none" stroke="${o.stroke}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"${o.dash ? ` stroke-dasharray="${o.dash}"` : dash}${o.salpha ? ` stroke-opacity="${o.salpha}"` : ''}/>`;
          }
        });
        if (blurOpen) out += '</g>';
        if (focus != null) out = '<defs><filter id="wq-dof" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="2.6"/></filter></defs>' + out;
        return out;
      },
    };
    return api;
  }

  const INK = '#2a2f36';

  // ───────────── primitives ─────────────
  function ring(c, u, v, a, b, n = 16) { const P = []; for (let i = 0; i < n; i++) { const t = (i / n) * 2 * PI; P.push(add(c, add(mul(u, a * cos(t)), mul(v, b * sin(t))))); } return P; }
  function ellipsoidPts(c, R, rx, ry, rz, n = 10, m = 14, filter) {
    const P = [];
    for (let i = 0; i <= n; i++) {
      const th = (i / n) * PI;
      for (let j = 0; j < m; j++) {
        const ph = (j / m) * 2 * PI;
        const l = [rx * sin(th) * cos(ph), ry * cos(th), rz * sin(th) * sin(ph)];
        if (filter && !filter(l)) continue;
        P.push(add(c, M.v(R, l)));
      }
    }
    return P;
  }
  function sphere2(cv, c, r, n = 14) { const q = cv.cam.p(c), k = cv.cam.k(c) * r, P = []; for (let i = 0; i < n; i++) { const t = i / n * 2 * PI; P.push([q[0] + k * cos(t), q[1] + k * sin(t)]); } return P; }
  function capsule2(cv, a, ra, b, rb) { return hull(sphere2(cv, a, ra).concat(sphere2(cv, b, rb))); }
  function proj(cv, P) { return P.map((p) => cv.cam.p(p)); }

  function box(cv, o) {   // o: {x,y,z (min corner), w,h,d, c, id, edge, rough, z bias}
    const { x, y, z, w, h, d } = o; const c = o.c || '#ddd';
    const V = [[x, y, z], [x + w, y, z], [x + w, y + h, z], [x, y + h, z], [x, y, z + d], [x + w, y, z + d], [x + w, y + h, z + d], [x, y + h, z + d]];
    const F = [[[0, 3, 2, 1], [0, 0, -1], -0.1], [[4, 5, 6, 7], [0, 0, 1], 0], [[0, 4, 7, 3], [-1, 0, 0], -0.16], [[1, 2, 6, 5], [1, 0, 0], -0.16], [[3, 7, 6, 2], [0, 1, 0], 0.12], [[0, 1, 5, 4], [0, -1, 0], -0.3]];
    const ctr = [x + w / 2, y + h / 2, z + d / 2];
    const zc = cv.cam.depth(ctr) + (o.bias || 0);
    F.forEach(([ix, n, k], fi) => {
      const pc = mul(ix.reduce((s, i) => add(s, V[i]), [0, 0, 0]), 0.25);
      if (!cv.cam.facing(pc, n)) return;
      const pts = ix.map((i) => cv.cam.p(V[i]));
      if (pts.some((p) => p[2] < 0.1)) return;
      cv.blob(zc - 0.001 * fi, pts, { poly: true, fill: shade(c, k), stroke: o.edge || INK, w: o.lw || 2, seed: hash((o.id || 'b') + fi), rough: o.rough == null ? 0.9 : o.rough, layer: o.layer, off: o.off });
    });
    return zc;
  }
  function cyl(cv, o) {   // vertical cylinder: {x,z,y,h,r,c}
    const a = [o.x, o.y, o.z], b = [o.x, o.y + o.h, o.z];
    const R1 = ring(a, [1, 0, 0], [0, 0, 1], o.r, o.r, 20), R2 = ring(b, [1, 0, 0], [0, 0, 1], o.r2 == null ? o.r : o.r2, o.r2 == null ? o.r : o.r2, 20);
    const zc = cv.cam.depth(mul(add(a, b), 0.5)) + (o.bias || 0);
    cv.blob(zc, hull(proj(cv, R1.concat(R2))), { poly: true, fill: shade(o.c, -0.08), stroke: INK, w: o.lw || 2, seed: hash(o.id || 'c'), rough: 0.8, layer: o.layer });
    const top = cv.cam.pos[1] > b[1] ? R2 : R1;
    cv.blob(zc - 0.002, proj(cv, top), { fill: shade(o.c, 0.15), stroke: INK, w: o.lw || 2, seed: hash((o.id || 'c') + 't'), rough: 0.6, layer: o.layer });
    return zc;
  }
  function clipNear(cv, P, zn = 0.15) {   // Sutherland–Hodgman against the plane depth = zn
    const out = [], d = P.map((p) => cv.cam.depth(p));
    for (let i = 0; i < P.length; i++) {
      const j = (i + 1) % P.length, a = P[i], b = P[j], da = d[i], db = d[j];
      if (da >= zn) out.push(a);
      if ((da >= zn) !== (db >= zn)) out.push(vlerp(a, b, (zn - da) / (db - da)));
    }
    return out;
  }
  function quad(cv, P, o) { const C = clipNear(cv, P); if (C.length < 3) return; const pts = proj(cv, C); cv.blob(o.z != null ? o.z : cv.cam.depth(mul(P.reduce((s, p) => add(s, p), [0, 0, 0]), 1 / P.length)), pts, Object.assign({ poly: true }, o)); }
  function line3(cv, A, B, o) { const da = cv.cam.depth(A), db = cv.cam.depth(B); if (da < 0.15 && db < 0.15) return; if (da < 0.15) A = vlerp(A, B, (0.15 - da) / (db - da)); else if (db < 0.15) B = vlerp(B, A, (0.15 - db) / (da - db)); const a = cv.cam.p(A), b = cv.cam.p(B); cv.line(o.z != null ? o.z : cv.cam.depth(mul(add(A, B), 0.5)), [a, b], o); }

  // ───────────── people ─────────────
  const POSES = {
    stand: { ls: [4, 7, 12], rs: [4, 7, 12] },
    talk: { ls: [8, 8, 25], rs: [28, 12, 75], g: 'talk' },
    talk2: { ls: [30, 14, 70], rs: [30, 14, 70], g: 'talk2' },
    point: { rs: [78, 14, 6], ls: [4, 7, 15] },
    phone: { rs: [38, 42, 140], ls: [4, 7, 15], hp: -4, hr: -8, prop: 'phone' },
    type: { ls: [32, -6, 78], rs: [32, -6, 78], lean: 10, hp: 12, g: 'type' },
    sit_type: { ls: [36, -6, 72], rs: [36, -6, 72], lean: 6, hp: 10, sit: 1, g: 'type' },
    sit: { ls: [20, 4, 60], rs: [20, 4, 60], sit: 1 },
    clap: { ls: [48, -18, 92], rs: [48, -18, 92], g: 'clap' },
    cheer: { ls: [150, 22, 20], rs: [150, 22, 20], g: 'bounce' },
    shake: { rs: [46, -18, 34], ls: [4, 7, 15], g: 'shake' },
    write: { rs: [105, 18, 30], ls: [6, 7, 20], g: 'write' },
    think: { rs: [34, -28, 140], ls: [26, -20, 96], hr: 6, hp: 5 },
    cross: { ls: [32, -36, 112], rs: [32, -36, 108] },
    hips: { ls: [6, 38, 100], rs: [6, 38, 100] },
    shrug: { ls: [14, 32, 95], rs: [14, 32, 95], hr: -6 },
    surprised: { ls: [14, 12, 128], rs: [14, 12, 128], lean: -5, hp: -6 },
    stir: { rs: [40, 6, 70], ls: [26, -8, 80], lean: 8, hp: 16, g: 'stir' },
    look_screen: { ls: [10, 6, 30], rs: [10, 6, 30], lean: 14, hp: 8 },
    lean_desk: { ls: [42, 6, 25], rs: [42, 6, 25], lean: 30, hp: -6 },
    bow: { ls: [4, 6, 10], rs: [4, 6, 10], lean: 25 },
    thumbs: { rs: [60, 12, 95], ls: [4, 7, 15], prop: 'thumb' },
    hold_paper: { ls: [40, -6, 80], rs: [40, -6, 80], hp: 12, prop: 'paper' },
    wave: { rs: [10, 150, 30], ls: [4, 7, 15], g: 'wave' },
  };
  const POSE_KEYS = ['lean', 'twist', 'hy', 'hp', 'hr', 'sit'];
  function poseVec(name) {
    const p = POSES[name] || POSES.stand;
    const v = { ls: (p.ls || [4, 7, 12]).slice(), rs: (p.rs || [4, 7, 12]).slice(), lh: [0, 0], rh: [0, 0] };
    POSE_KEYS.forEach((k) => (v[k] = p[k] || 0));
    if (v.sit) { v.lh = [88, 92]; v.rh = [88, 92]; }
    return v;
  }
  function mixPose(a, b, k) {
    const o = { ls: [], rs: [], lh: [], rh: [] };
    ['ls', 'rs', 'lh', 'rh'].forEach((q) => { for (let i = 0; i < a[q].length; i++) o[q][i] = lerp(a[q][i], b[q][i], k); });
    POSE_KEYS.forEach((q) => (o[q] = lerp(a[q], b[q], k)));
    return o;
  }

  const LOOK0 = { height: 1.72, sex: 'm', skin: '#f2cfae', hair: 'short', hairColor: '#2b2621', top: 'shirt', topColor: '#6d8fb3', pants: '#3b4252', shoes: '#2b2b2b', build: 1 };

  // state of a character at time t from its keyframes
  function charState(keys, t) {
    // keys: [{t, pos, face, pose, expr, look(target name/point), walk:{to,dur}, speak}]
    let st = { prevExpr: 'neutral', exprT: -9, mark: null, markT: -9, pos: [0, 0], face: 0, pose: 'stand', expr: 'neutral', poseT: -9, prevPose: 'stand', faceT: -9, prevFace: 0, walkFrom: null, show: true };
    for (const k of keys) {
      if (k.t > t) break;
      if (k.pos) { st.pos = k.pos.slice(); st.walkFrom = null; }
      if (k.show != null) st.show = k.show;
      if (k.walk) {
        const done = t >= k.t + k.walk.dur;
        const from = st.pos, to = k.walk.to;
        const kk = done ? 1 : (t - k.t) / k.walk.dur;
        st.pos = [lerp(from[0], to[0], kk), lerp(from[1], to[1], kk)];
        if (!done) { st.walking = { phase: (t - k.t) * 1.9, dir: atan2(to[0] - from[0], to[1] - from[1]) / D }; }
        else st.walking = null;
        if (!done) { st.prevFace = st.face; st.face = atan2(to[0] - from[0], to[1] - from[1]) / D; st.faceT = k.t - 0.3; }
        else { st.prevFace = atan2(to[0] - from[0], to[1] - from[1]) / D; st.face = k.walk.face != null ? k.walk.face : st.prevFace; st.faceT = k.t + k.walk.dur; }
      }
      if (k.face != null && !k.walk) { st.prevFace = curFace(st, k.t); st.face = k.face; st.faceT = k.t; }
      if (k.pose) { st.prevPose = st.pose; st.prevPoseK = curPoseK(st, k.t); st.pose = k.pose; st.poseT = k.t; }
      if (k.expr && k.expr !== st.expr) { st.prevExpr = st.expr; st.expr = k.expr; st.exprT = k.t; }
      if (k.mark !== undefined) { st.mark = k.mark; st.markT = k.t; }
      if (k.lookAt !== undefined) st.lookAt = k.lookAt;
    }
    return st;
  }
  function curFace(st, t) { let d = ((st.face - st.prevFace) % 360 + 540) % 360 - 180; return st.prevFace + d * ease((t - st.faceT) / 0.5); }
  function curPoseK(st, t) { return ease((t - st.poseT) / 0.45); }

  const HAND = { type: ['type', 'type'], sit_type: ['type', 'type'], point: ['relax', 'point'], cross: ['fist', 'fist'], thumbs: ['relax', 'thumb'],
    shake: ['relax', 'shake'], clap: ['flat', 'flat'], phone: ['relax', 'grip'], stir: ['grip', 'grip'], write: ['relax', 'grip'], cheer: ['spread', 'spread'],
    wave: ['relax', 'spread'], talk: ['relax', 'open'], talk2: ['open', 'open'], think: ['fist', 'grip'], surprised: ['spread', 'spread'], shrug: ['open', 'open'], hold_paper: ['grip', 'grip'] };
  function handKind(pose, s, gk) { const k = (HAND[pose] || [])[s > 0 ? 0 : 1] || 'relax'; return gk < 0.5 ? 'relax' : k; }
  function drawHand(cv, parts, name, look, s, wrist, fu, ax, kind, h, t, z) {
    const cam = cv.cam;
    let pn;   // palm normal
    if (kind === 'type' || kind === 'flat') pn = norm(sub([0, -1, 0], mul(fu, dot([0, -1, 0], fu))));
    else pn = norm(sub(mul(ax, -s), mul(fu, dot(mul(ax, -s), fu))));
    if (kind === 'flat') pn = mul(pn, -1);
    if (kind === 'shake') pn = norm(sub(mul(ax, -s), mul(fu, dot(mul(ax, -s), fu))));
    const sp = norm(cross(fu, pn)), th = mul(sp, -s);
    const L = 0.048 * h, pw = 0.019 * h;
    const P1 = add(wrist, mul(fu, L));
    const corners = [add(wrist, mul(sp, pw * 0.75)), add(wrist, mul(sp, -pw * 0.75)), add(P1, mul(sp, pw)), add(P1, mul(sp, -pw))];
    const palmPts = hull([].concat(...corners.map((c) => sphere2(cv, c, 0.008 * h, 8))));
    const skin = look.skin, o = { stroke: INK, w: 1.6, rough: 0.25 };
    const curlOf = { relax: 30, open: 12, spread: 5, fist: 115, point: 110, thumb: 115, grip: 95, type: 38, flat: 5, shake: 55 };
    const items = [];
    items.push({ z: cam.depth(mul(add(wrist, P1), 0.5)), fn: () => cv.blob(0, palmPts, Object.assign({ fill: skin, seed: hash(name + 'palm' + s) }, o)) });
    for (let i = 0; i < 4; i++) {
      let c = curlOf[kind] == null ? 30 : curlOf[kind];
      if (kind === 'point' && i === 0) c = 4;
      if (kind === 'type') c += 22 * max(0, sin(t * 13 + i * 1.9 + s));
      const spread = kind === 'spread' ? (i - 1.5) * 0.12 : 0;
      const off = (1.5 - i) * pw * 0.62;
      const base = add(add(P1, mul(th, off)), mul(fu, -0.004 * h));
      const fl = (i === 3 ? 0.75 : i === 0 ? 0.92 : 1) * 0.044 * h;
      const dir = (a) => norm(add(add(mul(fu, cos(a)), mul(pn, sin(a))), mul(th, spread)));
      const m = add(base, mul(dir(c * 0.5 * D), fl * 0.55)), tip = add(m, mul(dir(c * D), fl * 0.45));
      const r = 0.0072 * h;
      items.push({ z: cam.depth(m) - (c > 70 ? 0.004 : 0), fn: () => { cv.blob(0, capsule2(cv, base, r, m, r * 0.95), Object.assign({ fill: skin, seed: hash(name + 'f' + i + s) }, o)); cv.blob(0, capsule2(cv, m, r * 0.95, tip, r * 0.85), Object.assign({ fill: skin, seed: hash(name + 'g' + i + s) }, o)); } });
    }
    // thumb
    let tdir = norm(add(add(mul(fu, 0.55), mul(th, 0.7)), mul(pn, 0.35)));
    if (kind === 'thumb') tdir = [0, 1, 0];
    if (kind === 'fist' || kind === 'point' || kind === 'grip') tdir = norm(add(add(mul(fu, 0.6), mul(pn, 0.6)), mul(th, 0.3)));
    if (kind === 'type') tdir = norm(add(add(mul(fu, 0.7), mul(pn, 0.5)), mul(th, 0.4)));
    const tb = add(add(wrist, mul(fu, 0.012 * h)), mul(th, pw * 0.8)), tt2 = add(tb, mul(tdir, 0.04 * h));
    items.push({ z: cam.depth(tt2) - 0.003, fn: () => cv.blob(0, capsule2(cv, tb, 0.0095 * h, tt2, 0.0078 * h), Object.assign({ fill: skin, seed: hash(name + 'th' + s) }, o)) });
    items.sort((a, b) => b.z - a.z);
    items.forEach((it, i) => parts.push({ z: z - i * 0.00001, fn: it.fn }));
  }

  function drawPerson(cv, name, look, st, t, speaking, ctx) {
    look = Object.assign({}, LOOK0, look);
    const h = look.height, bw = look.build || 1, fem = look.sex === 'f';
    const cam = cv.cam;
    // pose
    let P = mixPose(poseVec(st.prevPose), poseVec(st.pose), curPoseK(st, t));
    const g = (POSES[st.pose] || {}).g, gk = curPoseK(st, t);
    const tt = t * 2 * PI;
    if (g === 'talk') { P.rs[0] += 12 * sin(tt * 0.55) * gk; P.rs[2] += 18 * sin(tt * 0.8 + 1) * gk; P.ls[2] += 8 * sin(tt * 0.4) * gk; }
    if (g === 'talk2') { P.rs[1] += 10 * sin(tt * 0.6) * gk; P.ls[1] += 10 * sin(tt * 0.6 + 1.3) * gk; P.rs[2] += 12 * sin(tt * 0.7) * gk; }
    if (g === 'type') { P.ls[2] += 5 * sin(tt * 3.1) * gk; P.rs[2] += 5 * sin(tt * 2.7 + 1) * gk; }
    if (g === 'clap') { const c = abs(sin(tt * 1.6)); P.ls[1] = lerp(P.ls[1], 10, c * gk); P.rs[1] = lerp(P.rs[1], 10, c * gk); }
    if (g === 'bounce') { P.ls[1] += 8 * sin(tt * 1.2) * gk; P.rs[1] += 8 * sin(tt * 1.2) * gk; }
    if (g === 'shake') { P.rs[0] += 8 * sin(tt * 1.8) * gk; }
    if (g === 'write') { P.rs[0] += 8 * sin(tt * 1.3) * gk; P.rs[1] += 8 * cos(tt * 1.3) * gk; }
    if (g === 'stir') { P.rs[1] += 10 * cos(tt * 0.9) * gk; P.rs[0] += 8 * sin(tt * 0.9) * gk; }
    if (g === 'wave') { P.rs[1] += 18 * sin(tt * 1.5) * gk; }
    if (st.nod) P.hp += 10 * sin(tt * 1.6);
    let bob = 0;
    if (st.walking) {
      const ph = st.walking.phase * 2 * PI, s = sin(ph);
      P.lh = [26 * s, 10 + 30 * max(0, -cos(ph))]; P.rh = [-26 * s, 10 + 30 * max(0, cos(ph))];
      if (['stand', 'talk', 'cross', 'surprised', 'shrug'].includes(st.pose)) { P.ls = [-22 * s, 6, 18]; P.rs = [22 * s, 6, 18]; }
      bob = 0.012 * abs(cos(ph)) * h;
    }
    // head turn toward target
    const face = curFace(st, t);
    const yaw = face * D;
    let hy = P.hy;
    if (st.lookAt) {
      const tp = typeof st.lookAt === 'string' ? (ctx.pos[st.lookAt] || null) : st.lookAt;
      if (tp) { let a = atan2(tp[0] - st.pos[0], tp[1] - st.pos[1]) / D - face; a = ((a % 360) + 540) % 360 - 180; hy += clamp(a, -65, 65); }
    }
    const Rw = M.y(yaw);
    const base = [st.pos[0], 0, st.pos[1]];
    const W = (l) => add(base, M.v(Rw, l));
    const legL = 0.245 * h, hipY0 = 0.535 * h;
    const hipY = P.sit ? 0.47 + (h - 1.7) * 0.05 : hipY0 - bob * 0.3 - (st.walking ? 0.01 * h : 0);
    const pelvis = [0, hipY, P.sit ? -0.02 : 0];
    const Ru = M.m(M.y(P.twist * D), M.x(P.lean * D));
    const U = (l) => W(add(pelvis, M.v(Ru, l)));
    const UR = M.m(Rw, Ru);
    const sw = (fem ? 0.105 : 0.118) * h * bw;
    const parts = [];
    const zOf = (p) => cam.depth(p);
    const outline = { stroke: INK, w: 2.2, rough: 0.55 };
    const part = (z, pts2, fill, id, extra) => parts.push({ z, fn: () => cv.blob(0, pts2, Object.assign({ fill, seed: hash(name + id) }, outline, extra || {})) });

    // legs
    const legs = [];
    for (const s of [1, -1]) {
      const hp = s > 0 ? P.lh : P.rh;
      const hip = W(add(pelvis, [s * 0.052 * h * bw, -0.01 * h, 0]));
      const f = hp[0] * D, k = hp[1] * D;
      const dir1 = M.v(Rw, [0, -cos(f), sin(f)]), dir2 = M.v(Rw, [0, -cos(f - k), sin(f - k)]);
      const knee = add(hip, mul(dir1, legL)), ankle = add(knee, mul(dir2, legL * (P.sit ? 0.92 : 1)));
      const ankleG = P.sit ? [ankle[0], max(ankle[1], 0.06 * h), ankle[2]] : ankle;
      legs.push({ s, hip, knee, ankle: ankleG });
    }
    const skirt = look.skirt;
    for (const L of legs) {
      const zl = zOf(L.knee) + 0.02;
      const pantsC = look.pants;
      if (!skirt) part(zl, capsule2(cv, L.hip, 0.058 * h * bw, L.knee, 0.044 * h), pantsC, 'th' + L.s);
      part(zl + 0.001, capsule2(cv, L.knee, (skirt ? 0.03 : 0.043) * h, L.ankle, (skirt ? 0.024 : 0.034) * h), skirt ? look.skin : pantsC, 'sh' + L.s);
      // knee fold
      if (!skirt && !P.sit && abs((L.s > 0 ? P.lh[1] : P.rh[1])) > 30) {
        const a = cam.p(add(L.knee, M.v(Rw, [0.02 * h, 0.01 * h, 0.03 * h]))), b = cam.p(add(L.knee, M.v(Rw, [-0.015 * h, -0.005 * h, 0.035 * h])));
        parts.push({ z: zl - 0.002, fn: () => cv.line(0, [a, b], { stroke: INK, w: 1.4, rough: 0.4, seed: hash(name + 'kf' + L.s) }) });
      }
      // shoe
      const fdir = M.v(Rw, [0, 0, 1]);
      const toe = add([L.ankle[0], 0.025 * h, L.ankle[2]], mul(fdir, 0.075 * h)), heel = add([L.ankle[0], 0.028 * h, L.ankle[2]], mul(fdir, -0.012 * h));
      const fy = P.sit ? L.ankle[1] - 0.03 * h : (st.walking ? L.ankle[1] - 0.04 * h : 0);
      const T = add(toe, [0, max(0, fy), 0]), Hh = add(heel, [0, max(0, fy), 0]);
      part(zOf(T) + 0.01, capsule2(cv, Hh, 0.03 * h, T, 0.026 * h), look.shoes, 'ft' + L.s);
      // floor shadow
      const sh = ring([L.ankle[0], 0.002, L.ankle[2]], [1, 0, 0], [0, 0, 1], 0.07 * h, 0.05 * h, 14);
      if (!P.sit) cv.blob(0, proj(cv, sh), { fill: '#000', alpha: 0.08, layer: 1, off: false });
    }
    // torso
    const hipW = (fem ? 0.1 : 0.094) * h * bw, waistW = (fem ? 0.078 : 0.088) * h * bw, chestW = (fem ? 0.092 : 0.104) * h * bw;
    const lvl = (y, a, b) => ring(U([0, y * h, 0]), M.v(UR, [1, 0, 0]), M.v(UR, [0, 0, 1]), a, b, 18);
    const pelvisPts = lvl(0, hipW, 0.07 * h * bw).concat(lvl(-0.055, hipW * 0.75, 0.06 * h * bw));
    const torsoC = U([0, 0.15 * h, 0]);
    const torsoZ = zOf(torsoC);
    if (!skirt) part(torsoZ + 0.012, hull(proj(cv, pelvisPts)), look.pants, 'pv');
    else {
      const sk = lvl(0.08, waistW * 1.02, 0.062 * h).concat(ring(W([0, 0.31 * h, 0]), M.v(Rw, [1, 0, 0]), M.v(Rw, [0, 0, 1]), 0.15 * h, 0.12 * h, 18));
      part(torsoZ + 0.004, hull(proj(cv, sk)), look.skirt, 'sk');
    }
    const topLen = look.top === 'coat' ? -0.16 : look.top === 'suit' ? -0.02 : 0.02;
    const torsoPts = lvl(topLen, hipW * (look.top === 'coat' ? 1.12 : 1.02), 0.072 * h * bw).concat(lvl(0.09, waistW, 0.066 * h * bw), lvl(0.19, chestW, (fem ? 0.075 : 0.072) * h * bw), lvl(0.25, sw * 0.95, 0.058 * h * bw), lvl(0.292, 0.062 * h * bw, 0.042 * h * bw));
    part(torsoZ, hull(proj(cv, torsoPts)), look.topColor, 'to');
    // torso front details (visible from front)
    const fwd = M.v(UR, [0, 0, 1]);
    const frontVis = dot(fwd, norm(sub(cam.pos, torsoC)));
    if (frontVis > 0.1) {
      const fz = 0.07 * h * bw;
      const Fp = (x, y, zz) => cam.p(U([x * h, y * h, (zz == null ? 1 : zz) * fz]));
      const a = clamp(frontVis * 2);
      parts.push({ z: torsoZ - 0.003, fn: () => {
        const o = { stroke: INK, w: 1.6, rough: 0.4, salpha: a };
        if (look.top === 'suit' || look.top === 'coat') {
          cv.blob(0, [Fp(-0.035, 0.275, 0.6), Fp(0, 0.19, 1.05), Fp(0.035, 0.275, 0.6)], { poly: true, fill: look.shirt || '#fff', stroke: INK, w: 1.5, rough: 0.3, seed: hash(name + 'sh'), off: false });
          if (look.tie) cv.blob(0, [Fp(-0.008, 0.262, 0.9), Fp(0.008, 0.262, 0.9), Fp(0.012, 0.2, 1.05), Fp(0, 0.17, 1.05), Fp(-0.012, 0.2, 1.05)], { poly: true, fill: look.tie, stroke: INK, w: 1.3, rough: 0.2, seed: hash(name + 'ti'), off: false });
          cv.line(0, [Fp(-0.05, 0.27, 0.7), Fp(-0.012, 0.13, 1.05), Fp(-0.01, topLen + 0.01, 1.0)], Object.assign({ seed: hash(name + 'l1') }, o));
          cv.line(0, [Fp(0.05, 0.27, 0.7), Fp(0.012, 0.13, 1.05)], Object.assign({ seed: hash(name + 'l2') }, o));
          for (const y of [0.1, 0.05]) cv.blob(0, sphere2(cv, U([0.016 * h, y * h, fz * 1.02]), 0.004 * h, 8), { fill: INK, off: false });
        } else if (look.top === 'hoodie') {
          cv.line(0, [Fp(-0.045, 0.27, 0.8), Fp(0, 0.225, 1.05), Fp(0.045, 0.27, 0.8)], Object.assign({ seed: hash(name + 'h1'), smooth: true }, o));
          cv.line(0, [Fp(-0.012, 0.23, 1.04), Fp(-0.014, 0.17, 1.06)], Object.assign({ seed: hash(name + 'h2') }, o));
          cv.line(0, [Fp(0.012, 0.23, 1.04), Fp(0.014, 0.17, 1.06)], Object.assign({ seed: hash(name + 'h3') }, o));
          cv.line(0, [Fp(-0.05, 0.03, 1.0), Fp(-0.04, 0.09, 1.02), Fp(0.04, 0.09, 1.02), Fp(0.05, 0.03, 1.0)], Object.assign({ seed: hash(name + 'h4') }, o));
          if (look.logo) cv.blob(0, sphere2(cv, U([0, 0.15 * h, fz * 1.05]), 0.014 * h, 10), { fill: look.logo, stroke: INK, w: 1.2, rough: 0.3, seed: 3, off: false });
        } else {
          cv.line(0, [Fp(-0.035, 0.272, 0.7), Fp(0, 0.235, 1.03), Fp(0.035, 0.272, 0.7)], Object.assign({ seed: hash(name + 'c1') }, o));
          cv.line(0, [Fp(0, 0.235, 1.03), Fp(0, topLen + 0.02, 1.0)], Object.assign({ seed: hash(name + 'c2'), salpha: a * 0.6 }, o));
          if (look.badge) cv.blob(0, [Fp(0.03, 0.2), Fp(0.06, 0.2), Fp(0.06, 0.16), Fp(0.03, 0.16)], { poly: true, fill: look.badge, stroke: INK, w: 1.2, rough: 0.2, seed: 5, off: false });
        }
        // waist folds
        cv.line(0, [Fp(-0.07, 0.1, 0.8), Fp(-0.05, 0.075, 0.95)], Object.assign({ seed: hash(name + 'wf1') }, o, { salpha: a * 0.7 }));
        cv.line(0, [Fp(0.07, 0.1, 0.8), Fp(0.05, 0.075, 0.95)], Object.assign({ seed: hash(name + 'wf2') }, o, { salpha: a * 0.7 }));
      } });
    }
    if (look.belt && !skirt) parts.push({ z: torsoZ - 0.002, fn: () => cv.line(0, proj(cv, lvl(0.005, hipW * 1.02, 0.073 * h).filter((p) => cam.facing(p, sub(p, U([0, 0.005 * h, 0]))))), { stroke: INK, w: 1.4, rough: 0.3 }) });

    // arms
    const hands = {};
    for (const s of [1, -1]) {
      const A = s > 0 ? P.ls : P.rs;
      const S = U([s * sw * 0.9, 0.238 * h, -0.005 * h]);
      const fl = A[0] * D, ab = s * A[1] * D, el = A[2] * D;
      const R0 = M.m(M.z(ab), M.x(-fl));
      const u = M.v(UR, M.v(R0, [0, -1, 0]));
      const ax = M.v(UR, M.v(M.z(ab), [1, 0, 0]));
      // Rodrigues: rotate u about ax by -el
      const c = cos(-el), sn = sin(-el);
      const fu = add(add(mul(u, c), mul(cross(ax, u), sn)), mul(ax, dot(ax, u) * (1 - c)));
      const E = add(S, mul(u, 0.165 * h)), Hn = add(E, mul(fu, 0.15 * h)), Hc = add(E, mul(fu, 0.175 * h));
      hands[s] = { E, H: Hc, fu, u };
      const zE = zOf(E), zH = zOf(Hc);
      const bias = -0.035;   // arms in front of the torso unless clearly behind
      const sleeve = look.short ? look.skin : look.topColor;
      part(zE + bias, capsule2(cv, S, 0.033 * h * bw, E, 0.029 * h * bw), look.topColor, 'ua' + s);
      part((zE + zH) / 2 + bias - 0.001, capsule2(cv, E, 0.029 * h * bw, Hn, 0.023 * h), sleeve, 'fa' + s);
      const hk = handKind(st.pose, s, gk);
      const hz = zH + bias - 0.002;
      if (cam.k(Hc) * 0.1 * h < 22) part(hz, sphere2(cv, Hc, 0.024 * h, 12), look.skin, 'hd' + s);
      else drawHand(cv, parts, name, look, s, add(E, mul(fu, 0.15 * h)), fu, ax, hk, h, t, hz);
      if (A[2] > 40) {   // elbow folds
        const inner = norm(sub(fu, mul(u, dot(fu, u))));
        const p0 = add(E, mul(inner, 0.022 * h)), q = cam.p(p0);
        const k = cam.k(p0) * 0.012 * h;
        parts.push({ z: zE + bias - 0.0015, fn: () => { cv.line(0, [[q[0] - k, q[1] - k * 0.5], [q[0] + k * 0.2, q[1]], [q[0] - k * 0.7, q[1] + k]], { stroke: INK, w: 1.3, rough: 0.3, smooth: true, seed: hash(name + 'ef' + s) }); } });
      }
    }
    // props in hand
    const pr = (POSES[st.pose] || {}).prop;
    if (pr === 'phone' && gk > 0.6) {
      const Hh = hands[-1].H, q = add(Hh, mul(hands[-1].fu, 0.02 * h));
      parts.push({ z: zOf(q) - 0.05, fn: () => cv.blob(0, capsule2(cv, add(q, [0, 0.03, 0]), 0.012, add(q, [0, -0.04, 0]), 0.012), { fill: '#33373d', stroke: INK, w: 1.6, rough: 0.3, seed: 9 }) });
    }
    if (pr === 'paper' && gk > 0.6) {
      const c0 = mul(add(hands[1].H, hands[-1].H), 0.5), up = [0, 1, 0], fw = M.v(Rw, [0, 0, 1]), side = M.v(Rw, [1, 0, 0]);
      const cc = add(c0, add(mul(up, 0.06), mul(fw, 0.02)));
      const Q = [add(cc, add(mul(side, -0.1), mul(up, 0.07))), add(cc, add(mul(side, 0.1), mul(up, 0.07))), add(cc, add(mul(side, 0.1), add(mul(up, -0.07), mul(fw, 0.04)))), add(cc, add(mul(side, -0.1), add(mul(up, -0.07), mul(fw, 0.04))))];
      parts.push({ z: zOf(cc) - 0.06, fn: () => cv.blob(0, proj(cv, Q), { poly: true, fill: '#fffdf2', stroke: INK, w: 1.6, rough: 0.4, seed: 21 }) });
    }
    ctx.hands[name] = hands;

    // neck + head
    const neckA = U([0, 0.26 * h, -0.004 * h]), neckB = U([0, 0.32 * h, 0.004 * h]);
    part(zOf(neckA) - 0.004, capsule2(cv, neckA, 0.03 * h, neckB, 0.028 * h), look.skin, 'nk');
    const hs = look.head || 1.08, hr = { x: 0.056 * h * hs, y: 0.07 * h * hs, z: 0.063 * h * hs };
    const Hc = U([0, (0.385 + (hs - 1) * 0.05) * h, 0.008 * h]);
    const RH = M.m(UR, M.m(M.y(hy * D), M.m(M.x((P.hp) * D), M.z(P.hr * D))));
    const HP = (l) => add(Hc, M.v(RH, l));
    const zHead = zOf(Hc) - 0.03;
    const headPts = ellipsoidPts(Hc, RH, hr.x, hr.y, hr.z, 8, 14);
    // jaw a bit narrower: add chin point
    headPts.push(HP([0, -hr.y * 1.02, hr.z * 0.35]));
    const headPoly = hull(proj(cv, headPts));
    parts.push({ z: zHead, fn: () => cv.blob(0, headPoly, Object.assign({ fill: look.skin, seed: hash(name + 'hd') }, outline)) });
    ctx.heads[name] = { top: HP([0, hr.y * 1.25, 0]), c: Hc };
    // hair pieces
    const shell = (filter, n = 9, m = 16, s = 1.1) => ellipsoidPts(Hc, RH, hr.x * s, hr.y * s, hr.z * s, n, m, filter);
    const hc = look.hairColor;
    const hairPieces = [];
    const fr = look.fringe == null ? 0.66 : look.fringe;
    if (look.hair !== 'bald') { hairPieces.push(['top', shell((l) => l[1] > fr * hr.y * 1.1 || (l[1] > 0.25 * hr.y && l[2] < -0.35 * hr.z))]); hairPieces.push(['crown', shell((l) => l[1] > 0.2 * hr.y && l[2] < 0.15 * hr.z && l[1] > fr * hr.y * 1.1 - 0.5 * hr.y * (0.15 - l[2] / hr.z))]); }
    const backLow = look.hair === 'long' ? -2.3 : look.hair === 'bob' ? -1.0 : look.hair === 'bald' ? -0.3 : -0.55;
    const backPts = shell((l) => l[2] < -0.25 * hr.z && l[1] > -0.6 * hr.y * 1.1 && (look.hair !== 'bald' || l[1] < 0.5 * hr.y), 9, 16, 1.12);
    if (backLow < -0.6) { for (const x of [-1, -0.5, 0, 0.5, 1]) backPts.push(HP([x * hr.x * (look.hair === 'long' ? 1.25 : 1.15), backLow * hr.y, -0.35 * hr.z])); }
    hairPieces.push(['back', backPts]);
    for (const s of [1, -1]) {
      const low = look.hair === 'long' ? -1.6 : look.hair === 'bob' ? -0.9 : -0.1;
      if (look.hair === 'bald') continue;
      const P2 = shell((l) => s * l[0] > 0.78 * hr.x * 1.1 && l[1] > -0.2 * hr.y && l[2] < (look.hair === 'short' ? 0.45 : 0.1) * hr.z, 9, 16, 1.12);
      P2.push(HP([s * hr.x * 1.12, low * hr.y, (look.hair === 'short' ? 0.0 : -0.2) * hr.z]));
      if (look.hair !== 'short') P2.push(HP([s * hr.x * 1.15, low * hr.y, -0.5 * hr.z]));
      hairPieces.push(['side' + s, P2]);
    }
    if (look.hair === 'bun') hairPieces.push(['bun', ellipsoidPts(HP([0, hr.y * 0.95, -hr.z * 0.7]), RH, 0.035 * h, 0.03 * h, 0.035 * h, 6, 10)]);
    if (look.hair === 'pony') { const a = HP([0, hr.y * 0.5, -hr.z * 1.1]), b = add(HP([0, -hr.y * 0.6, -hr.z * 1.35]), [0, 0, 0]); hairPieces.push(['pony', ellipsoidPts(a, RH, 0.03 * h, 0.03 * h, 0.03 * h, 5, 8).concat(ellipsoidPts(b, RH, 0.02 * h, 0.04 * h, 0.02 * h, 5, 8))]); }
    for (const [id, pts] of hairPieces) {
      if (!pts.length) continue;
      const cc = mul(pts.reduce((s, p) => add(s, p), [0, 0, 0]), 1 / pts.length);
      const behind = zOf(cc) > zOf(Hc) + 0.012;
      parts.push({ z: behind ? zHead + 0.01 + (id === 'back' && look.hair === 'long' ? 0.08 : 0) : zHead - 0.004, fn: () => cv.blob(0, hull(proj(cv, pts)), { fill: hc, stroke: INK, w: 2, rough: 0.5, seed: hash(name + id) }) });
    }
    // face patch: re-paint the face below the hairline over any hair hull that bridged across it
    if (look.hair !== 'bald') {
      const fp = ellipsoidPts(Hc, RH, hr.x * 0.97, hr.y * 0.97, hr.z * 0.97, 10, 18, (l) => l[2] > 0.3 * hr.z && l[1] < (fr - 0.08) * hr.y && abs(l[0]) < 0.78 * hr.x && l[1] > -0.92 * hr.y);
      const fn = M.v(RH, [0, 0, 1]);
      if (fp.length > 3 && dot(fn, norm(sub(cam.pos, Hc))) > 0.1) parts.push({ z: zHead - 0.0065, fn: () => cv.blob(0, hull(proj(cv, fp)), { fill: look.skin, off: false }) });
    }
    // hair strands (close shots)
    if (look.hair !== 'bald' && cam.k(Hc) * h > 700) parts.push({ z: zHead - 0.005, fn: () => {
      for (let i = 0; i < 5; i++) {
        const ax2 = -0.6 + i * 0.3, pts = [];
        for (let j = 0; j <= 4; j++) { const th = (0.15 + j * 0.13) * PI, x = hr.x * 1.1 * sin(th) * sin(ax2), y = hr.y * 1.1 * cos(th), z = hr.z * 1.1 * sin(th) * cos(ax2); if (y < fr * hr.y * 1.1) break; pts.push([x, y, z]); }
        if (pts.length < 3) continue;
        const n = M.v(RH, norm(pts[1])); if (dot(n, norm(sub(cam.pos, HP(pts[1])))) < 0.2) continue;
        cv.line(0, pts.map((q) => cam.p(HP(q))), { stroke: shade(hc, 0.35), w: 1.6, smooth: true, rough: 0 });
      }
    } });
    // face
    parts.push({ z: zHead - 0.008, fn: () => drawFace(cv, name, look, HP, RH, hr, h * hs, st, t, speaking, ctx) });

    // order within the person
    parts.sort((a, b) => b.z - a.z);
    const zc = zOf(W([0, 0.9, 0]));
    return { z: zc, draw: () => parts.forEach((p) => p.fn()) };
  }

  // expression: bh brow height, bi inner brow raise (−: frown), bo outer brow, lid eye openness, sq lower-lid squint, sm smile,
  // op mouth open, tw teeth, mw mouth width, tg tongue, bl blush, sw sweat, he happy closed eyes, asy smirk, ly look up; mk comic mark
  const E0 = { bh: 0, bi: 0, bo: 0, lid: 1, sq: 0, sm: 0.08, op: 0, tw: 0, mw: 1, tg: 0, bl: 0, sw: 0, he: 0, asy: 0, ly: 0 };
  const EXPR = {
    neutral: {},
    smile: { bh: 0.05, bi: 0.1, lid: 0.95, sq: 0.35, sm: 0.8, mw: 1.1, bl: 0.35 },
    happy: { bh: 0.15, bi: 0.2, lid: 0.95, sq: 0.5, sm: 1, op: 0.35, tw: 1, mw: 1.2, bl: 0.6 },
    laugh: { bh: 0.25, bi: 0.2, sq: 1, sm: 1, op: 0.75, tw: 1, tg: 1, mw: 1.25, bl: 0.9, he: 1 },
    surprised: { bh: 0.9, bi: 0.5, bo: 0.6, lid: 1.35, op: 0.7, mw: 0.5, sm: 0, mk: '!' },
    shocked: { bh: 1, bi: 0.7, bo: 0.5, lid: 1.4, op: 0.9, mw: 0.6, sm: -0.2, sw: 1, mk: '!' },
    worried: { bh: 0.3, bi: 1, bo: -0.35, lid: 0.9, sm: -0.5, mw: 0.85, sw: 1 },
    nervous: { bh: 0.3, bi: 0.9, bo: -0.25, lid: 1.05, sm: 0.7, op: 0.22, tw: 1, mw: 1.3, sw: 1 },
    serious: { bh: -0.25, bi: -1, bo: 0.25, lid: 0.82, sm: -0.2, mw: 0.9 },
    determined: { bh: -0.1, bi: -0.8, bo: 0.3, lid: 0.95, sm: 0.25, mw: 1, asy: 0.3 },
    thinking: { bh: 0.25, bi: 0.4, bo: -0.1, lid: 0.85, sm: -0.12, mw: 0.6, asy: 0.6, ly: 1, mk: '?' },
    idea: { bh: 0.75, bi: 0.4, bo: 0.4, lid: 1.25, sm: 0.8, op: 0.45, tw: 1, mw: 1.15, bl: 0.4, mk: 'idea' },
    sad: { bh: 0.1, bi: 0.9, bo: -0.5, lid: 0.78, sm: -0.6, mw: 0.85 },
    proud: { bh: 0.1, bi: -0.2, bo: 0.2, lid: 0.85, sq: 0.3, sm: 0.85, mw: 1.1, asy: 0.4, bl: 0.3 },
  };
  function exprAt(st, t) {
    const a = Object.assign({}, E0, EXPR[st.prevExpr] || {}), b = Object.assign({}, E0, EXPR[st.expr] || {});
    const k = ease((t - st.exprT) / 0.28), o = {};
    for (const q in E0) o[q] = lerp(a[q], b[q], k);
    o.mk = st.mark !== undefined && st.mark !== null ? st.mark : b.mk; o.mkT = st.mark ? st.markT : st.exprT;
    return o;
  }
  function drawFace(cv, name, look, HP, RH, hr, h, st, t, speaking, ctx) {
    const cam = cv.cam;
    const E = exprAt(st, t);
    const surf = (x, y, out = 0) => { const zz = hr.z * sqrt(max(0.02, 1 - (x / hr.x) ** 2 - (y / hr.y) ** 2)); const n = norm([x / (hr.x * hr.x), y / (hr.y * hr.y), zz / (hr.z * hr.z)]); return { p: HP([x, y, zz + out]), n: M.v(RH, n) }; };
    const vis = (q) => dot(q.n, norm(sub(cam.pos, q.p)));
    const P2 = (x, y, out) => cam.p(surf(x, y, out).p);
    const ink = INK;
    const kc = cam.k(HP([0, 0, hr.z]));
    const lw = clamp(kc * h / 900, 1.2, 5);   // line width grows in close-ups
    let svg = '';
    const path = (pts, closed) => (closed ? smoothD(pts) : smoothD(pts, false));
    const uid = name.charCodeAt(0) + '_' + Math.round(t * 1000);
    // ears
    for (const sx of [1, -1]) {
      const c = HP([sx * hr.x * 0.98, -0.005 * h, -0.004 * h]), n = M.v(RH, [sx, 0, 0]);
      const v = dot(n, norm(sub(cam.pos, c)));
      if (v > 0.15 && look.hair !== 'long' && look.hair !== 'bob') {
        const k = cam.k(c), q = cam.p(c);
        const pts = ring([0, 0, 0], [1, 0, 0], [0, 1, 0], 0.012 * h * k * v, 0.021 * h * k, 12).map((p) => [q[0] + p[0], q[1] + p[1]]);
        svg += `<path d="${smoothD(pts)}" fill="${shade(look.skin, -0.05)}" stroke="${ink}" stroke-width="${f1(lw * 0.8)}"/>`;
        if (k * h > 900) svg += `<path d="${smoothD([[q[0], q[1] - 0.012 * h * k], [q[0] - 0.004 * h * k * v * sx, q[1]], [q[0], q[1] + 0.01 * h * k]], false)}" fill="none" stroke="${shade(look.skin, -0.35)}" stroke-width="${f1(lw * 0.6)}"/>`;
      }
    }
    // gaze: toward the look-at target if any
    let gx = 0, gy = E.ly * 0.35;
    if (st.lookAt && ctx) {
      const tp = typeof st.lookAt === 'string' ? (ctx.heads[st.lookAt] ? ctx.heads[st.lookAt].c : (ctx.pos[st.lookAt] ? [ctx.pos[st.lookAt][0], 1.5, ctx.pos[st.lookAt][1]] : null)) : [st.lookAt[0], 1.0, st.lookAt[1]];
      if (tp) { const d = norm(sub(tp, HP([0, 0, 0]))); const RT = [RH[0], RH[3], RH[6], RH[1], RH[4], RH[7], RH[2], RH[5], RH[8]]; const l = M.v(RT, d); gx = clamp(l[0] * 1.6, -1, 1); gy = clamp(l[1] * 1.6, -0.6, 0.6); }
    }
    if (E.asy > 0.4) gx = lerp(gx, 0.7, 0.5);
    const blink = ((t + (hash(name) % 17) * 0.23) % 3.9) < 0.11;
    const eyeY = 0.007 * h, eyeX = 0.0215 * h, ew = 0.0118 * h;
    for (const sx of [1, -1]) {
      const c0 = surf(sx * eyeX, eyeY), v = vis(c0);
      if (v < 0.12) continue;
      const lid = blink ? 0.06 : E.lid;
      const eh = 0.0082 * h;
      const up = [], lo = [];
      for (let i = 0; i <= 8; i++) {
        const u = -1 + i / 4; const x = sx * eyeX + u * ew;
        const tilt = sx * u * 0.0012 * h;   // outer corner a little higher
        up.push(P2(x, eyeY + tilt + eh * lid * Math.pow(max(0, 1 - u * u), 0.7) * (1 + 0.15 * u * sx)));
        lo.push(P2(x, eyeY + tilt - eh * 0.7 * (1 - u * u) * (1 - E.sq * 0.75) + E.sq * 0.0018 * h));
      }
      if (E.he > 0.5 || (E.sq > 0.95 && lid < 1)) {   // happy closed eyes ∩
        const arc = []; for (let i = 0; i <= 8; i++) { const u = -1 + i / 4; arc.push(P2(sx * eyeX + u * ew, eyeY + eh * 0.9 * (1 - u * u) - 0.002 * h)); }
        svg += `<path d="${path(arc)}" fill="none" stroke="${ink}" stroke-width="${f1(lw * 1.3)}" stroke-linecap="round"/>`;
      } else if (blink || lid < 0.15) {
        svg += `<path d="${path(lo)}" fill="none" stroke="${ink}" stroke-width="${f1(lw * 1.2)}" stroke-linecap="round"/>`;
      } else {
        const outline = up.concat(lo.slice().reverse());
        const id = `e${uid}_${sx > 0 ? 'l' : 'r'}`;
        const qc = cam.p(surf(sx * eyeX + gx * ew * 0.42, eyeY + gy * eh * 0.4 - 0.0008 * h).p), k = cam.k(c0.p);
        const ir = 0.0068 * h * k * min(1, 0.85 + 0.15 * lid);
        svg += `<clipPath id="${id}"><path d="${polyD(outline)}"/></clipPath><path d="${polyD(outline)}" fill="#fffdf8"/>`;
        svg += `<g clip-path="url(#${id})"><ellipse cx="${f1(qc[0])}" cy="${f1(qc[1])}" rx="${f1(ir * clamp(v * 1.15, 0.4, 1))}" ry="${f1(ir)}" fill="${look.eye || '#4a3426'}"/>`;
        svg += `<ellipse cx="${f1(qc[0])}" cy="${f1(qc[1])}" rx="${f1(ir * 0.52 * clamp(v * 1.15, 0.4, 1))}" ry="${f1(ir * 0.52)}" fill="#111"/>`;
        svg += `<circle cx="${f1(qc[0] + ir * 0.35)}" cy="${f1(qc[1] - ir * 0.38)}" r="${f1(ir * 0.28)}" fill="#fff"/></g>`;
        svg += `<path d="${path(up, false)}" fill="none" stroke="${ink}" stroke-width="${f1(lw * 1.45)}" stroke-linecap="round"/>`;
        svg += `<path d="${path(lo.slice(2, 7), false)}" fill="none" stroke="${ink}" stroke-width="${f1(lw * 0.55)}" stroke-opacity="0.7"/>`;
        if (look.sex === 'f') { const oc = up[sx > 0 ? 8 : 0], q1 = up[sx > 0 ? 7 : 1]; svg += `<path d="M${f1(q1[0])} ${f1(q1[1])}L${f1(oc[0] + sx * 0.006 * h * k)} ${f1(oc[1] - 0.004 * h * k)}" stroke="${ink}" stroke-width="${f1(lw)}"/>`; }
        if (kc * h > 700) { const cr = []; for (let i = 1; i <= 7; i++) { const u = -1 + i / 4; cr.push(P2(sx * eyeX + u * ew * 0.9, eyeY + eh * lid * 1.25 + 0.0025 * h)); } svg += `<path d="${path(cr, false)}" fill="none" stroke="${shade(look.skin, -0.3)}" stroke-width="${f1(lw * 0.5)}"/>`; }
      }
      // brow: tapered, inner and outer ends move separately
      const by = eyeY + 0.0215 * h + E.bh * 0.0055 * h;
      const bp = [[0.0075, E.bi * 0.0065, 0.0042], [0.016, E.bi * 0.003 + 0.0016, 0.0036], [0.025, E.bo * 0.003 + 0.001, 0.0026], [0.033, E.bo * 0.0055 - 0.002, 0.0012]];
      const top = bp.map(([x, dy, w]) => P2(sx * x * h, by + dy * h + w * h * 0.5)), bot = bp.map(([x, dy, w]) => P2(sx * x * h, by + dy * h - w * h * 0.5));
      if (vis(surf(sx * 0.02 * h, by)) > 0.1) svg += `<path d="${smoothD(top.concat(bot.reverse()))}" fill="${shade(look.hairColor, -0.15)}" stroke="${shade(look.hairColor, -0.3)}" stroke-width="${f1(lw * 0.4)}"/>`;
      if (look.glasses) {
        const q = cam.p(c0.p), k = cam.k(c0.p);
        const gr = ring([0, 0, 0], [1, 0, 0], [0, 1, 0], 0.0165 * h * k * clamp(v, 0.3, 1), 0.0145 * h * k, 16).map((p) => [q[0] + p[0], q[1] + p[1] + 0.0015 * h * k]);
        svg += `<path d="${smoothD(gr)}" fill="#dfeaf2" fill-opacity="0.18" stroke="${ink}" stroke-width="${f1(lw * 0.9)}"/>`;
      }
    }
    if (look.glasses) { const a = surf(0.006 * h, eyeY + 0.003 * h, 0.003 * h), b = surf(-0.006 * h, eyeY + 0.003 * h, 0.003 * h); if (vis(a) > 0.1 || vis(b) > 0.1) { const A = cam.p(a.p), B = cam.p(b.p); svg += `<path d="M${f1(A[0])} ${f1(A[1])}Q${f1((A[0] + B[0]) / 2)} ${f1((A[1] + B[1]) / 2 - 2)} ${f1(B[0])} ${f1(B[1])}" fill="none" stroke="${ink}" stroke-width="${f1(lw * 0.9)}"/>`; } }
    // nose
    const nb = surf(0, -0.001 * h), nt = surf(0, -0.019 * h, 0.012 * h);
    if (vis(nb) > -0.3) {
      const side = dot(M.v(RH, [1, 0, 0]), norm(sub(cam.pos, nb.p))) > 0 ? -1 : 1;   // draw the shadow side of the nose
      const pts = [cam.p(surf(side * 0.004 * h, 0.006 * h).p), cam.p(surf(side * 0.005 * h, -0.008 * h, 0.004 * h).p), cam.p(nt.p), cam.p(surf(-side * 0.008 * h, -0.024 * h, 0.003 * h).p)];
      svg += `<path d="${smoothD(pts, false)}" fill="none" stroke="${shade(look.skin, -0.45)}" stroke-width="${f1(lw * 0.85)}" stroke-linecap="round"/>`;
      for (const sx of [1, -1]) { const nn = surf(sx * 0.0055 * h, -0.023 * h, 0.004 * h); if (vis(nn) > 0.25 && kc * h > 500) { const q = cam.p(nn.p); svg += `<circle cx="${f1(q[0])}" cy="${f1(q[1])}" r="${f1(lw * 0.7)}" fill="${shade(look.skin, -0.5)}"/>`; } }
    }
    // mouth
    const my = -0.039 * h, mw0 = 0.016 * h * E.mw;
    const mc = surf(0, my);
    let open = E.op;
    if (speaking) open = max(open, 0.18 + 0.42 * abs(sin(t * 11 + sin(t * 4.3) * 2)) * (0.6 + 0.4 * abs(sin(t * 2.7))));
    if (vis(mc) > 0.05) {
      const cy = E.sm * 0.0062 * h;
      const L = P2(-mw0, my + cy - E.asy * 0.003 * h), R = P2(mw0, my + cy + E.asy * 0.003 * h);
      const midUp = my + 0.0015 * h - max(0, E.sm) * 0.002 * h, midLo = my - (0.003 + open * 0.017 + max(0, E.sm) * open * 0.005) * h;
      const U1 = P2(-mw0 * 0.45, midUp + cy * 0.4), U2 = P2(mw0 * 0.45, midUp + cy * 0.4), UM = P2(0, midUp);
      const D1 = P2(-mw0 * 0.5, midLo + cy * 0.3), D2 = P2(mw0 * 0.5, midLo + cy * 0.3), DM = P2(0, midLo);
      if (open > 0.06) {
        const shape = [L, U1, UM, U2, R, D2, DM, D1];
        const id = `m${uid}`;
        svg += `<clipPath id="${id}"><path d="${smoothD(shape)}"/></clipPath><path d="${smoothD(shape)}" fill="#7a2e33"/>`;
        svg += `<g clip-path="url(#${id})">`;
        if (E.tw > 0.3) { const tL = P2(-mw0, midUp - 0.006 * h), tR = P2(mw0, midUp - 0.006 * h); svg += `<path d="M${f1(L[0])} ${f1(L[1] - 20)}L${f1(R[0])} ${f1(R[1] - 20)}L${f1(tR[0])} ${f1(tR[1])}L${f1(tL[0])} ${f1(tL[1])}Z" fill="#fff"/>`; }
        if (E.tg > 0.3 || open > 0.5) { const tc = P2(0, midLo + 0.004 * h), kk = cam.k(mc.p); svg += `<ellipse cx="${f1(tc[0])}" cy="${f1(tc[1])}" rx="${f1(mw0 * 0.6 * kk)}" ry="${f1(0.006 * h * kk)}" fill="#d9707a"/>`; }
        svg += `</g><path d="${smoothD(shape)}" fill="none" stroke="${ink}" stroke-width="${f1(lw * 1.1)}" stroke-linejoin="round"/>`;
      } else {
        const mid = P2(0, my - E.sm * 0.004 * h + (E.sm < 0 ? -E.sm * 0.003 * h : 0));
        svg += `<path d="${smoothD([L, P2(-mw0 * 0.5, my + cy * 0.25 - E.sm * 0.003 * h), mid, P2(mw0 * 0.5, my + cy * 0.25 - E.sm * 0.003 * h), R], false)}" fill="none" stroke="${ink}" stroke-width="${f1(lw * 1.15)}" stroke-linecap="round"/>`;
        if (kc * h > 600 && E.sm < 0.5) { const lp = P2(0, my - 0.0085 * h); svg += `<path d="M${f1(lp[0] - lw * 3)} ${f1(lp[1])}Q${f1(lp[0])} ${f1(lp[1] + lw * 1.4)} ${f1(lp[0] + lw * 3)} ${f1(lp[1])}" fill="none" stroke="${shade(look.skin, -0.3)}" stroke-width="${f1(lw * 0.6)}"/>`; }
      }
      if (E.sm > 0.55 && kc * h > 500) for (const sx of [1, -1]) { const a = P2(sx * (mw0 + 0.004 * h), my + cy + 0.006 * h), b = P2(sx * (mw0 + 0.006 * h), my + cy - 0.002 * h), c = P2(sx * (mw0 + 0.003 * h), my + cy - 0.007 * h); svg += `<path d="${smoothD([a, b, c], false)}" fill="none" stroke="${shade(look.skin, -0.35)}" stroke-width="${f1(lw * 0.6)}"/>`; }
    }
    if (E.bl > 0.05) for (const sx of [1, -1]) { const q0 = surf(sx * 0.033 * h, -0.017 * h); if (vis(q0) > 0.3) { const q = cam.p(q0.p), kk = cam.k(q0.p); svg += `<ellipse cx="${f1(q[0])}" cy="${f1(q[1])}" rx="${f1(0.011 * h * kk)}" ry="${f1(0.0055 * h * kk)}" fill="#f07c7c" fill-opacity="${f1(E.bl * 0.38 * 100) / 100}"/>`; } }
    if (look.wrinkles) { const a = surf(-0.018 * h, 0.044 * h), b = surf(0.018 * h, 0.044 * h); if (vis(a) > 0.3 && vis(b) > 0.3) svg += `<path d="${smoothD([cam.p(a.p), cam.p(surf(0, 0.046 * h).p), cam.p(b.p)], false)}" fill="none" stroke="${shade(look.skin, -0.35)}" stroke-width="${f1(lw * 0.55)}"/>`; }
    if (look.beard) { const pts = [surf(-0.034 * h, -0.03 * h), surf(-0.02 * h, -0.06 * h), surf(0, -0.068 * h), surf(0.02 * h, -0.06 * h), surf(0.034 * h, -0.03 * h)]; if (vis(pts[2]) > 0) svg += `<path d="${smoothD(pts.map((q) => cam.p(q.p)), false)}" fill="none" stroke="${shade(look.hairColor, 0.25)}" stroke-width="${f1(lw * 0.9)}" stroke-dasharray="${f1(lw)} ${f1(lw * 2.4)}"/>`; }
    // chin
    if (kc * h > 800) { const a = surf(-0.012 * h, -0.067 * h), b = surf(0.012 * h, -0.067 * h); if (vis(a) > 0.2) svg += `<path d="${smoothD([cam.p(a.p), cam.p(surf(0, -0.069 * h).p), cam.p(b.p)], false)}" fill="none" stroke="${shade(look.skin, -0.25)}" stroke-width="${f1(lw * 0.5)}"/>`; }
    cv.svg(0, svg, 0);
    // comic marks, sweat (screen space near the head)
    const top = cam.p(HP([0, hr.y * 1.15, 0])), kk = cam.k(HP([0, 0, 0])) * h;
    const age = t - E.mkT;
    if (E.sw > 0.4) {
      const sd = surf(-0.05 * h, 0.02 * h); const q = cam.p(sd.p); const yy = q[1] + ((t * 0.25) % 1) * 0.03 * kk, r = 0.008 * kk;
      cv.svg(0, `<path d="M${f1(q[0])} ${f1(yy - r * 2.2)}Q${f1(q[0] + r * 1.1)} ${f1(yy)} ${f1(q[0])} ${f1(yy + r)}Q${f1(q[0] - r * 1.1)} ${f1(yy)} ${f1(q[0])} ${f1(yy - r * 2.2)}Z" fill="#9fd3f2" stroke="${INK}" stroke-width="${f1(lw * 0.7)}"/>`, 0);
    }
    if (E.mk && age < 2.2 && age > -0.01) {
      const pop = clamp(age * 5), sc = (0.6 + 0.4 * pop) * kk;
      const x = top[0] + 0.08 * sc, y = top[1] - 0.02 * sc;
      let m = '';
      if (E.mk === '!') { m = `<text x="${f1(x)}" y="${f1(y)}" font-size="${f1(0.11 * sc)}" font-family="WQHand" fill="#c2410c" font-weight="bold">!</text>`; for (let i = 0; i < 3; i++) { const a = -2.2 + i * 0.55; m += `<path d="M${f1(top[0] + cos(a) * 0.07 * sc)} ${f1(top[1] + sin(a) * 0.07 * sc)}L${f1(top[0] + cos(a) * 0.11 * sc)} ${f1(top[1] + sin(a) * 0.11 * sc)}" stroke="${INK}" stroke-width="${f1(lw)}" stroke-linecap="round"/>`; } }
      if (E.mk === '?') m = `<text x="${f1(x)}" y="${f1(y)}" font-size="${f1(0.1 * sc)}" font-family="WQHand" fill="#1f6f9f">?</text>`;
      if (E.mk === 'idea') { const r = 0.028 * sc, bx = top[0] + 0.07 * sc, byy = top[1] - 0.05 * sc; m = `<circle cx="${f1(bx)}" cy="${f1(byy)}" r="${f1(r)}" fill="#ffe27a" stroke="${INK}" stroke-width="${f1(lw)}"/><rect x="${f1(bx - r * 0.5)}" y="${f1(byy + r * 0.85)}" width="${f1(r)}" height="${f1(r * 0.6)}" fill="#9aa3ad" stroke="${INK}" stroke-width="${f1(lw * 0.8)}"/>`; for (let i = 0; i < 6; i++) { const a = -PI + i * PI / 5; m += `<path d="M${f1(bx + cos(a) * r * 1.4)} ${f1(byy + sin(a) * r * 1.4)}L${f1(bx + cos(a) * r * 1.9)} ${f1(byy + sin(a) * r * 1.9)}" stroke="#e0a400" stroke-width="${f1(lw)}" stroke-linecap="round"/>`; } }
      cv.svg(0, `<g opacity="${f1(clamp((2.2 - age) * 2) * 100) / 100}">${m}</g>`, 0);
    }
  }

  // ───────────── props & scenes ─────────────
  const PROPS = {};
  PROPS.room = (cv, o) => {   // stage-set room: floor, back wall, side walls
    const w = o.w || 8, d = o.d || 6, ht = o.h || 3;
    const x0 = -w / 2, x1 = w / 2, z0 = -d / 2, z1 = d / 2;
    quad(cv, [[x0, 0, z0], [x1, 0, z0], [x1, 0, z1], [x0, 0, z1]], { fill: o.floor || '#e9e2d4', stroke: null, layer: -2, off: false });
    // floor lines
    const step = o.tile || 1;
    for (let x = x0 + step; x < x1; x += step) line3(cv, [x, 0, z0], [x, 0, z1], { stroke: shade(o.floor || '#e9e2d4', -0.12), w: 1.2, rough: 0.6, layer: -2, seed: hash('fx' + x) });
    for (let z = z0 + step; z < z1; z += step) line3(cv, [x0, 0, z], [x1, 0, z], { stroke: shade(o.floor || '#e9e2d4', -0.12), w: 1.2, rough: 0.6, layer: -2, seed: hash('fz' + z) });
    const wall = o.wall || '#f4efe6';
    quad(cv, [[x0, 0, z0], [x1, 0, z0], [x1, ht, z0], [x0, ht, z0]], { fill: wall, stroke: INK, w: 2, rough: 0.8, layer: -2, seed: 11, off: false });
    if (cv.cam.pos[0] > x0) quad(cv, [[x0, 0, z0], [x0, ht, z0], [x0, ht, z1], [x0, 0, z1]], { fill: shade(wall, -0.07), stroke: INK, w: 2, rough: 0.8, layer: -2, seed: 12, off: false });
    if (cv.cam.pos[0] < x1) quad(cv, [[x1, 0, z0], [x1, 0, z1], [x1, ht, z1], [x1, ht, z0]], { fill: shade(wall, -0.1), stroke: INK, w: 2, rough: 0.8, layer: -2, seed: 13, off: false });
    // skirting
    line3(cv, [x0, 0.1, z0 + 0.01], [x1, 0.1, z0 + 0.01], { stroke: INK, w: 1.2, rough: 0.5, layer: -2 });
  };
  PROPS.window = (cv, o) => {   // on back wall (z) or side wall (x)
    const { x, y, z, w, h } = o; const side = o.side;
    const P = side ? [[x, y, z], [x, y, z + w], [x, y + h, z + w], [x, y + h, z]] : [[x, y, z], [x + w, y, z], [x + w, y + h, z], [x, y + h, z]];
    const night = (o.state || {}).night || (o.mood && o.mood.night);
    quad(cv, P, { fill: night ? '#1d2b4a' : '#cfe6f2', stroke: INK, w: 2.2, rough: 0.6, layer: -1, seed: hash('win' + x + z) });
    if (night) { for (let i = 0; i < 14; i++) { const q = vlerp(vlerp(P[0], P[1], ((i * 37) % 13) / 13 + 0.03), vlerp(P[3], P[2], ((i * 37) % 13) / 13 + 0.03), 0.08 + ((i * 53) % 7) / 18); cv.blob(cv.cam.depth(q) - 0.01, sphere2(cv, add(q, side ? [0.01, 0, 0] : [0, 0, 0.01]), 0.018, 6), { fill: '#ffd76a', layer: -1, off: false }); } const mq = vlerp(P[0], P[2], 0.8); cv.blob(cv.cam.depth(mq) - 0.01, sphere2(cv, add(mq, side ? [0.01, 0, 0] : [0, 0, 0.01]), 0.08, 14), { fill: '#f4f1d0', stroke: INK, w: 1.2, layer: -1, off: false }); }
    const mid = (a, b) => mul(add(a, b), 0.5);
    line3(cv, mid(P[0], P[1]), mid(P[3], P[2]), { stroke: INK, w: 2, layer: -1, seed: 4 });
    line3(cv, mid(P[0], P[3]), mid(P[1], P[2]), { stroke: INK, w: 2, layer: -1, seed: 5 });
    // sky strokes
    const a = vlerp(P[0], P[2], 0.25), b = vlerp(P[0], P[2], 0.32);
    line3(cv, a, add(b, [0, 0, 0]), { stroke: '#ffffff', w: 3, layer: -1, rough: 0.2 });
    if (o.city && !night) { for (let i = 0; i < 5; i++) { const k = (i + 0.5) / 5; const bh = 0.18 + 0.25 * ((i * 37) % 5) / 5; const b0 = vlerp(P[0], P[1], k - 0.07), b1 = vlerp(P[0], P[1], k + 0.07); quad(cv, [b0, b1, add(b1, [0, h * bh, 0]), add(b0, [0, h * bh, 0])].map((p) => add(p, side ? [0.01, 0.01, 0] : [0, 0.01, 0.01])), { fill: '#9fb6c6', stroke: '#6d8394', w: 1.2, rough: 0.6, layer: -1, seed: 40 + i, off: false }); } }
  };
  PROPS.table = (cv, o) => {
    const { x, z, w, d } = o, ht = o.h || 0.75, c = o.c || '#c9a27a';
    const zc = cv.cam.depth([x, ht, z]) + (o.bias || 0);
    const legs = [[-1, -1], [1, -1], [-1, 1], [1, 1]];
    for (const [a, b] of legs) box(cv, { x: x + a * (w / 2 - 0.08) - 0.03, y: 0, z: z + b * (d / 2 - 0.08) - 0.03, w: 0.06, h: ht - 0.04, d: 0.06, c: shade(c, -0.2), id: 'tl' + a + b + x, bias: o.bias });
    box(cv, { x: x - w / 2, y: ht - 0.04, z: z - d / 2, w, h: 0.04, d, c, id: 'tt' + x + z, bias: (o.bias || 0) - 0.01 });
    return zc;
  };
  PROPS.chair = (cv, o) => {
    const { x, z } = o, a = (o.face || 0) * D, c = o.c || '#4a5a6a';
    const R = M.y(a), Wp = (l) => add([x, 0, z], M.v(R, l));
    // seat
    const s = [[-0.22, 0.45, -0.22], [0.22, 0.45, -0.22], [0.22, 0.45, 0.22], [-0.22, 0.45, 0.22]].map(Wp);
    const zb = cv.cam.depth(Wp([0, 0.45, 0])) + (o.bias || 0);
    for (const [i, j] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) line3(cv, Wp([i * 0.19, 0.44, j * 0.19]), Wp([i * 0.2, 0, j * 0.2]), { stroke: INK, w: 3, z: zb + 0.02, seed: hash('cl' + x + i + j) });
    quad(cv, s, { fill: c, stroke: INK, w: 2, z: zb, seed: hash('cs' + x + z) });
    const bk = [[-0.22, 0.47, -0.24], [0.22, 0.47, -0.24], [0.22, 0.95, -0.27], [-0.22, 0.95, -0.27]].map(Wp);
    const bc = mul(add(bk[0], bk[2]), 0.5);
    quad(cv, bk, { fill: shade(c, -0.1), stroke: INK, w: 2, z: cv.cam.depth(bc) + (o.bias || 0) + 0.05, seed: hash('cb' + x + z) });
  };
  PROPS.whiteboard = (cv, o) => {   // on back wall
    const { x, y, z, w, h } = o;
    quad(cv, [[x, y, z], [x + w, y, z], [x + w, y + h, z], [x, y + h, z]], { fill: '#fbfbf8', stroke: INK, w: 3, rough: 0.5, layer: -1, seed: 31 });
    line3(cv, [x + 0.05, y - 0.04, z + 0.03], [x + w - 0.05, y - 0.04, z + 0.03], { stroke: INK, w: 4, layer: -1 });
    const st = o.state || {};
    const lines = st.lines || [];
    const k = st.k == null ? 1 : st.k;
    let inner = '';
    lines.forEach((ln, i) => {
      const n = Math.floor(ln.length * clamp(k * lines.length - i));
      if (n > 0) inner += `<text x="40" y="${90 + i * 95}" font-size="${i === 0 ? 76 : 64}" font-family="WQHand" fill="${i === 0 ? '#1f6f9f' : '#2a2f36'}">${esc(ln.slice(0, n))}</text>`;
    });
    if (inner) planeSvg(cv, cv.cam.depth([x + w / 2, y + h / 2, z]) - 0.05, [x, y + h, z + 0.01], [x + w, y + h, z + 0.01], [x, y, z + 0.01], 1000, 1000 * h / w, inner, -1);
  };
  PROPS.screen = (cv, o) => {   // wall-mounted TV/projection on back wall
    const { x, y, z, w, h } = o;
    quad(cv, [[x, y, z], [x + w, y, z], [x + w, y + h, z], [x, y + h, z]], { fill: '#30363f', stroke: INK, w: 3, rough: 0.4, layer: -1, seed: 32 });
    quad(cv, [[x + 0.06, y + 0.06, z + 0.01], [x + w - 0.06, y + 0.06, z + 0.01], [x + w - 0.06, y + h - 0.06, z + 0.01], [x + 0.06, y + h - 0.06, z + 0.01]], { fill: '#e9f1f7', stroke: null, layer: -1, off: false });
    if (o.chip) { const c = [x + w / 2, y + h / 2, z + 0.02]; quad(cv, [add(c, [-0.25, -0.25, 0]), add(c, [0.25, -0.25, 0]), add(c, [0.25, 0.25, 0]), add(c, [-0.25, 0.25, 0])], { fill: '#3a7d5c', stroke: INK, w: 2, layer: -1, seed: 33 }); for (let i = -2; i <= 2; i++) { line3(cv, add(c, [i * 0.09, 0.25, 0]), add(c, [i * 0.09, 0.33, 0]), { stroke: INK, w: 2, layer: -1 }); line3(cv, add(c, [i * 0.09, -0.25, 0]), add(c, [i * 0.09, -0.33, 0]), { stroke: INK, w: 2, layer: -1 }); } }
  };
  PROPS.monitor = (cv, o) => {   // on a desk, facing +z by default (face deg)
    const { x, y, z } = o, a = (o.face || 0) * D, R = M.y(a), Wp = (l) => add([x, y, z], M.v(R, l));
    const w = o.w || 0.6, h = o.h || 0.38;
    const zc = cv.cam.depth(Wp([0, 0.3, 0])) + (o.bias || 0);
    line3(cv, Wp([0, 0, -0.05]), Wp([0, 0.12, -0.05]), { stroke: INK, w: 5, z: zc + 0.03 });
    quad(cv, [Wp([-0.12, 0.002, -0.12]), Wp([0.12, 0.002, -0.12]), Wp([0.12, 0.002, 0.02]), Wp([-0.12, 0.002, 0.02])], { fill: '#555b63', stroke: INK, w: 1.5, z: zc + 0.04 });
    const F = [Wp([-w / 2, 0.12, -0.04]), Wp([w / 2, 0.12, -0.04]), Wp([w / 2, 0.12 + h, -0.04]), Wp([-w / 2, 0.12 + h, -0.04])];
    const n = M.v(R, [0, 0, 1]);
    const front = cv.cam.facing(F[0], n);
    quad(cv, F, { fill: '#30363f', stroke: INK, w: 2.4, z: zc, seed: hash('mon' + x) });
    if (!front) return;
    const S = (u, v) => Wp([-w / 2 + 0.03 + u * (w - 0.06), 0.15 + v * (h - 0.06), -0.035]);
    quad(cv, [S(0, 0), S(1, 0), S(1, 1), S(0, 1)], { fill: '#f4f8fb', stroke: null, z: zc - 0.001, off: false });
    const st = o.state || {}, mode = st.mode || 'code', T = o.t || 0;
    const code = o.code || ['# 关节 3 · 电机参数', 'kp = 2.40   # 旧芯片', 'ki = 0.15', 'kd = 0.02', 'run_test(joint=3)'];
    const fixed = o.fixed || 'kp = 1.65   # 新芯片';
    let inner = `<rect width="400" height="240" fill="#f4f8fb"/><rect width="400" height="22" fill="#dfe6ec"/><circle cx="12" cy="11" r="5" fill="#e06c5a"/><circle cx="27" cy="11" r="5" fill="#e0b04a"/><circle cx="42" cy="11" r="5" fill="#6aa56f"/>`;
    inner += `<rect x="0" y="22" width="200" height="218" fill="#22272e"/>`;
    const shown = mode === 'code' ? Math.floor(((T * 1.2) % 8) * 1.0) + 2 : code.length;
    code.forEach((l, i) => {
      if (i >= shown) return;
      let txt = l, col = l.startsWith('#') ? '#8b9aa8' : '#e6edf3';
      if (i === 1 && (mode === 'find')) { col = '#ff8a7a'; inner += `<rect x="4" y="${30 + i * 30}" width="192" height="26" fill="#5a2a2a"/>`; }
      if (i === 1 && mode === 'ok') { txt = fixed; col = '#8fe0a5'; inner += `<rect x="4" y="${30 + i * 30}" width="192" height="26" fill="#1f4a32"/>`; }
      inner += `<text x="10" y="${49 + i * 30}" font-size="15" font-family="WQHand" fill="${col}">${esc(txt)}</text>`;
    });
    if (mode === 'code' && Math.floor(T * 2) % 2 === 0) inner += `<rect x="10" y="${34 + Math.min(shown, code.length) * 30}" width="8" height="18" fill="#e6edf3"/>`;
    // right: joint-3 response
    let d = '';
    for (let i = 0; i <= 60; i++) { const u = i / 60; let v = 0.5 + 0.3 * sin(u * 6.3 + T * 1.5); if (mode !== 'ok' && mode !== 'code') v += 0.13 * sin(u * 80 + T * 9) * clamp((u - 0.3) * 4); d += (i ? 'L' : 'M') + f1(210 + u * 180) + ' ' + f1(215 - v * 170); }
    inner += `<text x="210" y="44" font-size="14" font-family="WQHand" fill="#5f6b76">关节 3 角度</text><path d="M210 215H392" stroke="#9aa6b2" stroke-width="1.5"/><path d="${d}" fill="none" stroke="${mode === 'ok' || mode === 'code' ? '#2e7d4f' : '#c2410c'}" stroke-width="3"/>`;
    if (mode === 'find') inner += `<ellipse cx="320" cy="120" rx="58" ry="46" fill="none" stroke="#c2410c" stroke-width="4"/>`;
    if (mode === 'ok') inner += `<path d="M352 50l10 12 20-24" fill="none" stroke="#2e7d4f" stroke-width="6" stroke-linecap="round"/>`;
    planeSvg(cv, zc - 0.002, S(0, 1), S(1, 1), S(0, 0), 400, 240, inner);
  };
  PROPS.laptop = (cv, o) => { const { x, y, z } = o; box(cv, { x: x - 0.17, y, z: z - 0.12, w: 0.34, h: 0.02, d: 0.24, c: '#9aa3ad', id: 'lp' + x }); quad(cv, [[x - 0.17, y + 0.02, z - 0.12], [x + 0.17, y + 0.02, z - 0.12], [x + 0.17, y + 0.24, z - 0.17], [x - 0.17, y + 0.24, z - 0.17]], { fill: '#3a4049', stroke: INK, w: 2, seed: 61 }); };
  PROPS.plant = (cv, o) => {
    const { x, z } = o; const zc = cyl(cv, { x, z, y: 0, h: 0.4, r: 0.17, r2: 0.2, c: o.c || '#c8714f', id: 'pl' + x });
    const c = [x, 0.75, z];
    for (let i = 0; i < 6; i++) { const a = i / 6 * 2 * PI; const p = add(c, [0.18 * cos(a), 0.12 * sin(i * 2.1), 0.18 * sin(a)]); cv.blob(zc - 0.05 - 0.001 * i, sphere2(cv, p, 0.17, 10), { fill: i % 2 ? '#6aa56f' : '#7fb97f', stroke: INK, w: 1.8, rough: 0.8, seed: hash('lf' + i + x) }); }
  };
  PROPS.cabinet = (cv, o) => { const zc = box(cv, Object.assign({ c: '#b8c2cc', id: 'cab' + o.x }, o)); const n = o.drawers || 3; for (let i = 1; i < n; i++) line3(cv, [o.x + 0.02, o.y + (o.h * i) / n, o.z + o.d + 0.003], [o.x + o.w - 0.02, o.y + (o.h * i) / n, o.z + o.d + 0.003], { stroke: INK, w: 1.5, z: zc - 0.01 }); };
  PROPS.shelf = (cv, o) => {
    const { x, z, w, h, d } = o; const c = o.c || '#8b9aa8';
    const zc = cv.cam.depth([x + w / 2, h / 2, z + d / 2]) + (o.bias || 0);
    box(cv, { x, y: 0, z, w: 0.04, h, d, c, id: 'sh1' + x, bias: o.bias }); box(cv, { x: x + w - 0.04, y: 0, z, w: 0.04, h, d, c, id: 'sh2' + x, bias: o.bias });
    for (let i = 0; i < 4; i++) { const y = 0.1 + i * (h - 0.15) / 3; box(cv, { x, y, z, w, h: 0.03, d, c, id: 'sh' + i + x, bias: (o.bias || 0) - 0.01 }); if (i < 3) for (let j = 0; j < 3; j++) box(cv, { x: x + 0.08 + j * (w - 0.1) / 3, y: y + 0.03, z: z + 0.05, w: (w - 0.2) / 3 - 0.04, h: 0.22, d: d - 0.1, c: ['#d9a35a', '#7aa0c4', '#c9b07d'][(i + j) % 3], id: 'bx' + i + j + x, bias: (o.bias || 0) - 0.02 }); }
    return zc;
  };
  PROPS.arm = (cv, o) => {   // robot arm on a bench: joints animate by mode
    const { x, y, z } = o; const st = o.state || {}; const T = o.t || 0;
    const mode = st.mode || 'still';
    const w = 2 * PI * 0.35;
    let q1 = 0.6 * sin(T * w * 0.5), q2 = -0.4 + 0.25 * sin(T * w), q3 = 1.1 + 0.3 * sin(T * w + 1);
    if (mode === 'still') { q1 = 0.3; q2 = -0.35; q3 = 1.2; }
    if (mode === 'jitter') q3 += 0.12 * sin(T * 47) + 0.07 * sin(T * 31);
    const base = [x, y, z]; const S = o.s || 1;
    const zc = cyl(cv, { x, z, y, h: 0.12 * S, r: 0.16 * S, c: '#e7a33e', id: 'ab' }) ;
    const R1 = M.y(q1);
    const j1 = add(base, [0, 0.28 * S, 0]);
    const d2 = M.v(R1, [sin(q2), cos(q2), 0]);
    const j2 = add(j1, mul(d2, 0.42 * S));
    const d3 = M.v(R1, [sin(q2 + q3), cos(q2 + q3), 0]);
    const j3 = add(j2, mul(d3, 0.36 * S));
    const C = '#f0b14a';
    const segs = [[add(base, [0, 0.1 * S, 0]), j1, 0.075 * S, 0.07 * S], [j1, j2, 0.065 * S, 0.055 * S], [j2, j3, 0.05 * S, 0.04 * S]];
    const items = [];
    segs.forEach(([a, b, ra, rb], i) => items.push({ z: cv.cam.depth(mul(add(a, b), 0.5)), fn: () => cv.blob(0, capsule2(cv, a, ra, b, rb), { fill: i === 2 && mode === 'jitter' ? '#f3a35a' : C, stroke: INK, w: 2.2, rough: 0.6, seed: hash('as' + i) }) }));
    [j1, j2].forEach((j, i) => items.push({ z: cv.cam.depth(j) - 0.06, fn: () => cv.blob(0, sphere2(cv, j, 0.06 * S), { fill: '#4b535c', stroke: INK, w: 2, rough: 0.5, seed: hash('aj' + i) }) }));
    const g1 = add(j3, mul(d3, 0.07 * S)), side = mul(M.v(R1, [0, 0, 1]), S);
    items.push({ z: cv.cam.depth(j3) - 0.05, fn: () => { cv.line(0, [cv.cam.p(add(j3, mul(side, -0.05))), cv.cam.p(add(g1, mul(side, -0.05)))], { stroke: INK, w: 4 }); cv.line(0, [cv.cam.p(add(j3, mul(side, 0.05))), cv.cam.p(add(g1, mul(side, 0.05)))], { stroke: INK, w: 4 }); } });
    if (mode === 'jitter') { const q = cv.cam.p(j2), k = cv.cam.k(j2) * 0.09; items.push({ z: cv.cam.depth(j2) - 0.1, fn: () => { for (let i = 0; i < 3; i++) cv.line(0, [[q[0] + k * (1 + i * 0.4), q[1] - k * 0.6], [q[0] + k * (1.25 + i * 0.4), q[1]], [q[0] + k * (1 + i * 0.4), q[1] + k * 0.6]], { stroke: '#c2410c', w: 2.4, smooth: true, rough: 0.4, seed: 90 + i }); } }); }
    if (st.trace) { const P = []; for (let i = 0; i <= 24; i++) { const tt = T - i * 0.06; const a1 = 0.6 * sin(tt * w * 0.5), a2 = -0.4 + 0.25 * sin(tt * w), a3 = 1.1 + 0.3 * sin(tt * w + 1); const r = M.y(a1); const p2 = add(j1, mul(M.v(r, [sin(a2), cos(a2), 0]), 0.42 * S)); P.push(cv.cam.p(add(p2, mul(M.v(r, [sin(a2 + a3), cos(a2 + a3), 0]), 0.43 * S)))); } items.push({ z: zc - 0.5, fn: () => cv.line(0, P, { stroke: '#1f6f9f', w: 2, dash: '6 6', rough: 0 }) }); }
    items.sort((a, b) => b.z - a.z);
    const zz = cv.cam.depth(j2) + (o.bias || 0);
    cv.svg(zz, '', 0);
    // draw now into the shared list with one depth so the arm stays together
    const start = cv.items.length;
    items.forEach((it) => it.fn());
    for (let i = start; i < cv.items.length; i++) cv.items[i].z = zz - (i - start) * 0.0001;
  };
  PROPS.stove = (cv, o) => {
    const { x, z } = o; const zc = box(cv, { x, y: 0, z, w: 1.2, h: 0.88, d: 0.6, c: '#e9e4dc', id: 'cnt' + x, bias: o.bias });
    box(cv, { x, y: 0.88, z, w: 1.2, h: 0.04, d: 0.6, c: '#8d8478', id: 'ct' + x, bias: (o.bias || 0) - 0.01 });
    for (let i = 1; i < 3; i++) line3(cv, [x + i * 0.4, 0.05, z + 0.601], [x + i * 0.4, 0.82, z + 0.601], { stroke: INK, w: 1.4, z: zc - 0.02 });
    // pot
    const pc = [x + 0.35, 0.92, z + 0.3];
    cyl(cv, { x: pc[0], z: pc[2], y: 0.92, h: 0.18, r: 0.16, c: '#7d8892', id: 'pot', bias: (o.bias || 0) - 0.05 });
    const T = o.t || 0; for (let i = 0; i < 3; i++) { const yy = 1.2 + ((T * 0.3 + i / 3) % 1) * 0.35; const s = [pc[0] - 0.06 + i * 0.06, yy, pc[2]]; line3(cv, s, add(s, [0.03 * sin(T * 2 + i), 0.1, 0]), { stroke: '#9aa6b2', w: 2, z: zc - 0.2, salpha: 1 - ((T * 0.3 + i / 3) % 1) }); }
    // cutting board
    box(cv, { x: x + 0.7, y: 0.92, z: z + 0.15, w: 0.4, h: 0.03, d: 0.3, c: '#d9b07a', id: 'cb', bias: (o.bias || 0) - 0.05 });
  };
  PROPS.fridge = (cv, o) => {
    const { x, z } = o; const zc = box(cv, { x, y: 0, z, w: 0.7, h: 1.8, d: 0.65, c: '#eef2f4', id: 'fr' });
    line3(cv, [x, 1.15, z + 0.651], [x + 0.7, 1.15, z + 0.651], { stroke: INK, w: 1.6, z: zc - 0.02 });
    line3(cv, [x + 0.6, 1.25, z + 0.66], [x + 0.6, 1.5, z + 0.66], { stroke: INK, w: 3, z: zc - 0.02 });
    // recipe note
    quad(cv, [[x + 0.12, 1.25, z + 0.655], [x + 0.45, 1.25, z + 0.655], [x + 0.45, 1.62, z + 0.655], [x + 0.12, 1.62, z + 0.655]], { fill: '#fff6c9', stroke: INK, w: 1.5, z: zc - 0.03, seed: 71 });
    const p = cv.cam.p([x + 0.15, 1.56, z + 0.66]), k = cv.cam.k([x + 0.15, 1.56, z + 0.66]);
    cv.svg(zc - 0.04, `<text x="${f1(p[0])}" y="${f1(p[1])}" font-size="${f1(0.07 * k)}" font-family="WQHand" fill="#c2410c">${esc(o.note || '菜谱')}</text>` + [1, 2, 3].map((i) => { const a = cv.cam.p([x + 0.15, 1.56 - i * 0.07, z + 0.66]), b = cv.cam.p([x + 0.4, 1.56 - i * 0.07, z + 0.66]); return `<path d="M${f1(a[0])} ${f1(a[1])}L${f1(b[0])} ${f1(b[1])}" stroke="#5f6b76" stroke-width="1.5"/>`; }).join(''), 0);
  };
  PROPS.dishes = (cv, o) => {   // a few plates and bowls on a table top at y
    const { x, z, y } = o;
    [[-0.3, -0.1, '#e8b04b'], [0.25, -0.15, '#7fb97f'], [0, 0.2, '#d9734a'], [-0.35, 0.25, '#f2e3c6']].forEach(([dx, dz, c], i) => {
      cyl(cv, { x: x + dx, z: z + dz, y, h: 0.03, r: 0.15, r2: 0.17, c: '#fafafa', id: 'pl' + i, bias: -0.02 });
      cv.blob(cv.cam.depth([x + dx, y, z + dz]) - 0.03, proj(cv, ring([x + dx, y + 0.035, z + dz], [1, 0, 0], [0, 0, 1], 0.1, 0.1, 14)), { fill: c, stroke: INK, w: 1.4, rough: 0.8, seed: hash('fd' + i) });
    });
  };
  PROPS.sofa = (cv, o) => { const { x, z } = o; const c = o.c || '#7a8fa6'; box(cv, { x, y: 0, z, w: o.w || 1.6, h: 0.42, d: 0.8, c, id: 'sf1' }); box(cv, { x, y: 0.42, z, w: o.w || 1.6, h: 0.45, d: 0.2, c: shade(c, -0.08), id: 'sf2', bias: 0.1 }); };
  PROPS.door = (cv, o) => { const { x, z } = o; quad(cv, [[x, 0, z], [x + 0.95, 0, z], [x + 0.95, 2.1, z], [x, 2.1, z]], { fill: o.c || '#b88a5e', stroke: INK, w: 2.4, layer: -1, seed: 81 }); cv.blob(cv.cam.depth([x, 1, z]), sphere2(cv, [x + 0.82, 1.0, z + 0.03], 0.035), { fill: '#d9b54a', stroke: INK, w: 1.5, layer: -1 }); };
  PROPS.sign = (cv, o) => {   // wall text label {x,y,z,text,size}
    const p = cv.cam.p([o.x, o.y, o.z]), k = cv.cam.k([o.x, o.y, o.z]);
    cv.svg(cv.cam.depth([o.x, o.y, o.z]), `<text x="${f1(p[0])}" y="${f1(p[1])}" font-size="${f1((o.size || 0.2) * k)}" font-family="WQHand" fill="${o.c || '#1f6f9f'}" text-anchor="middle">${esc(o.text)}</text>`, -1);
  };
  PROPS.bench = (cv, o) => { const { x, z } = o; const zc = box(cv, { x: x - (o.w || 1.4) / 2, y: 0, z: z - 0.35, w: o.w || 1.4, h: 0.8, d: 0.7, c: o.c || '#8a98a6', id: 'bn' + x }); for (let i = 0; i < 6; i++) line3(cv, [x - 0.7 + i * 0.28, 0.802, z + 0.351], [x - 0.6 + i * 0.28, 0.802, z + 0.351], { stroke: '#e0b33a', w: 6, z: zc - 0.02, rough: 0 }); return zc; };
  PROPS.stripe = (cv, o) => { const { x, z, w, d } = o; quad(cv, [[x, 0.003, z], [x + w, 0.003, z], [x + w, 0.003, z + d], [x, 0.003, z + d]], { fill: null, stroke: '#e0b33a', w: 5, layer: -2, dash: '18 10', rough: 0 }); };
  PROPS.rug = (cv, o) => { const { x, z, w, d } = o; quad(cv, [[x, 0.004, z], [x + w, 0.004, z], [x + w, 0.004, z + d], [x, 0.004, z + d]], { fill: o.c || '#c8d6c3', stroke: INK, w: 1.5, layer: -2, seed: 91 }); };
  // SVG drawn in a plane: TL, TR, BL corners (3D), local units w×h → affine transform
  function planeSvg(cv, z, TL, TR, BL, w, h, inner, layer) {
    if (cv.cam.depth(TL) < 0.15 || cv.cam.depth(TR) < 0.15 || cv.cam.depth(BL) < 0.15) return;
    const a = cv.cam.p(TL), b = cv.cam.p(TR), c = cv.cam.p(BL);
    const m = [(b[0] - a[0]) / w, (b[1] - a[1]) / w, (c[0] - a[0]) / h, (c[1] - a[1]) / h, a[0], a[1]].map((x) => Math.round(x * 10000) / 10000);
    cv.svg(z, `<g transform="matrix(${m.join(' ')})">${inner}</g>`, layer || 0);
  }
  PROPS.keyboard = (cv, o) => {   // on a desk top at y, facing the typist at angle face (deg; 0 = typist at +z)
    const { x, y, z } = o, R = M.y((o.face || 0) * D), Wp = (l) => add([x, y, z], M.v(R, l));
    const w = 0.44, d = 0.15;
    const zc = cv.cam.depth(Wp([0, 0, 0])) + (o.bias || 0);
    const top = [Wp([-w / 2, 0.022, -d / 2]), Wp([w / 2, 0.022, -d / 2]), Wp([w / 2, 0.016, d / 2]), Wp([-w / 2, 0.016, d / 2])];
    const bot = top.map((p) => [p[0], y + 0.001, p[2]]);
    cv.blob(zc, hull(proj(cv, top.concat(bot))), { poly: true, fill: '#3b4048', stroke: INK, w: 1.8, rough: 0.3, seed: hash('kb' + x) });
    if (cv.cam.k(Wp([0, 0, 0])) * w < 90) return;
    let inner = `<rect x="2" y="2" width="436" height="146" rx="6" fill="#4b525c"/>`;
    const T = o.t || 0, typing = (o.state || {}).typing !== false;
    for (let r = 0; r < 5; r++) for (let c = 0; c < 14; c++) {
      if (r === 4 && c > 3 && c < 10) { if (c === 4) inner += `<rect x="${6 + 4 * 30.5}" y="${6 + r * 28}" width="${6 * 30.5 - 4}" height="24" rx="3" fill="#e8e8e2"/>`; continue; }
      const hit = typing && (((Math.floor(T * 9) * 7 + r * 5 + c * 3) % 23) === 0);
      inner += `<rect x="${6 + c * 30.5}" y="${6 + r * 28}" width="26.5" height="24" rx="3" fill="${hit ? '#f0b14a' : '#e8e8e2'}"/>`;
    }
    planeSvg(cv, zc - 0.002, top[0], top[1], top[3], 440, 150, inner);
  };
  PROPS.mouse = (cv, o) => { const c = [o.x, o.y + 0.018, o.z]; cv.blob(cv.cam.depth(c) + (o.bias || 0), hull(proj(cv, ellipsoidPts(c, M.y(0), 0.032, 0.018, 0.05, 5, 10))), { fill: '#d6d9dd', stroke: INK, w: 1.6, rough: 0.3, seed: 52 }); };
  PROPS.mug = (cv, o) => {
    const { x, y, z } = o; const zc = cyl(cv, { x, z, y, h: 0.1, r: 0.042, c: o.c || '#f2f2ee', id: 'mug' + x + z, lw: 1.6, bias: o.bias });
    const hs = [[x + 0.04, y + 0.08, z], [x + 0.075, y + 0.065, z], [x + 0.075, y + 0.035, z], [x + 0.04, y + 0.022, z]];
    cv.line(zc - 0.001, proj(cv, hs), { stroke: INK, w: 2.4, smooth: true, rough: 0.2 });
    if (o.steam !== false) { const T = o.t || 0; for (let i = 0; i < 2; i++) { const k = (T * 0.4 + i * 0.5) % 1; const b = [x - 0.012 + i * 0.024, y + 0.12 + k * 0.12, z]; cv.line(zc - 0.002, proj(cv, [b, add(b, [0.012 * sin(T * 3 + i), 0.04, 0]), add(b, [-0.01, 0.08, 0])]), { stroke: '#a7b2bd', w: 1.8, smooth: true, rough: 0, salpha: f1(1 - k) }); } }
  };
  PROPS.papers = (cv, o) => {
    const { x, y, z } = o; const a = (o.rot || 0) * D, R = M.y(a);
    for (let i = 0; i < (o.n || 2); i++) {
      const r = M.y(a + i * 0.25), c = add([x, y + 0.002 + i * 0.002, z], M.v(R, [i * 0.03, 0, i * 0.02]));
      const Q = [[-0.105, 0, -0.148], [0.105, 0, -0.148], [0.105, 0, 0.148], [-0.105, 0, 0.148]].map((l) => add(c, M.v(r, l)));
      quad(cv, Q, { fill: '#fffef8', stroke: INK, w: 1.3, rough: 0.3, seed: hash('pp' + x + i), z: cv.cam.depth(c) - 0.01 * i + (o.bias || 0) });
      if (cv.cam.k(c) * 0.2 > 40) for (let j = 0; j < 6; j++) line3(cv, add(c, M.v(r, [-0.08, 0.001, -0.11 + j * 0.035])), add(c, M.v(r, [0.04 + 0.03 * ((j * 7) % 3), 0.001, -0.11 + j * 0.035])), { stroke: '#9aa6b2', w: 1.2, rough: 0.2, z: cv.cam.depth(c) - 0.01 * i - 0.001 + (o.bias || 0) });
    }
  };
  PROPS.sticky = (cv, o) => { const { x, y, z } = o; const s = 0.07; const n = o.side ? [[x, y, z], [x, y, z + s], [x, y - s, z + s], [x, y - s, z]] : [[x, y, z], [x + s, y, z], [x + s, y - s, z], [x, y - s, z]]; quad(cv, n, { fill: o.c || '#ffe680', stroke: INK, w: 1.2, rough: 0.3, seed: hash('st' + x + y), z: cv.cam.depth([x, y, z]) - 0.06 }); };
  PROPS.clock = (cv, o) => {   // wall clock on the back wall (or side: true on the x wall)
    const { x, y, z } = o, r = o.r || 0.22; const st = o.state || {};
    const u = o.side ? [0, 0, 1] : [1, 0, 0], v = [0, 1, 0], c = [x, y, z];
    const zc = cv.cam.depth(c) - 0.02;
    cv.blob(zc, proj(cv, ring(c, u, v, r, r, 28)), { fill: '#ffffff', stroke: INK, w: 3, rough: 0.5, seed: 61, layer: -1 });
    const [hh, mm] = String(st.time || o.time || '09:00').split(':').map(Number);
    const T = o.t || 0, sec = (T * 6) % 60;
    const hand = (ang, len, w, col) => { const e = add(c, add(mul(u, sin(ang) * len), mul(v, cos(ang) * len))); line3(cv, c, e, { stroke: col || INK, w, rough: 0.1, layer: -1, z: zc - 0.001 }); };
    for (let i = 0; i < 12; i++) { const a = i / 12 * 2 * PI; line3(cv, add(c, add(mul(u, sin(a) * r * 0.82), mul(v, cos(a) * r * 0.82))), add(c, add(mul(u, sin(a) * r * 0.93), mul(v, cos(a) * r * 0.93))), { stroke: INK, w: i % 3 ? 1.4 : 2.6, rough: 0, layer: -1, z: zc - 0.0005 }); }
    hand(((hh % 12) + mm / 60) / 12 * 2 * PI, r * 0.5, 4.5); hand(mm / 60 * 2 * PI, r * 0.75, 3); hand(sec / 60 * 2 * PI, r * 0.82, 1.4, '#c2410c');
  };
  PROPS.calendar = (cv, o) => {
    const { x, y, z } = o, w = 0.42, h = 0.52;
    const TL = [x, y + h, z], TR = [x + w, y + h, z], BL = [x, y, z];
    quad(cv, [BL, [x + w, y, z], TR, TL], { fill: '#ffffff', stroke: INK, w: 2, rough: 0.4, seed: 62, layer: -1 });
    let inner = `<rect x="0" y="0" width="420" height="110" fill="#c2410c"/><text x="210" y="80" font-size="64" font-family="WQHand" fill="#fff" text-anchor="middle">${esc(o.month || '十一月')}</text>`;
    for (let r = 0; r < 5; r++) for (let c = 0; c < 7; c++) { const n = r * 7 + c + 1; if (n > 30) continue; inner += `<text x="${30 + c * 58}" y="${165 + r * 72}" font-size="34" font-family="WQHand" fill="#5f6b76" text-anchor="middle">${n}</text>`; }
    const mark = o.mark || 19, mr = Math.floor((mark - 1) / 7), mc = (mark - 1) % 7;
    inner += `<ellipse cx="${30 + mc * 58}" cy="${153 + mr * 72}" rx="30" ry="26" fill="none" stroke="#c2410c" stroke-width="6"/><text x="${30 + mc * 58}" y="${195 + mr * 72}" font-size="26" font-family="WQHand" fill="#c2410c" text-anchor="middle">${esc(o.label || '发布')}</text>`;
    planeSvg(cv, cv.cam.depth([x + w / 2, y + h / 2, z]) - 0.05, add(TL, [0, 0, 0.005]), add(TR, [0, 0, 0.005]), add(BL, [0, 0, 0.005]), 420, 520, inner, -1);
  };
  PROPS.lamp = (cv, o) => {
    const { x, y, z } = o; const on = (o.state || {}).on;
    const zc = cyl(cv, { x, z, y, h: 0.025, r: 0.08, c: '#3d4450', id: 'lb' + x, bias: o.bias });
    const j = [x + 0.05, y + 0.32, z], hd = [x + 0.2, y + 0.42, z];
    line3(cv, [x, y + 0.02, z], j, { stroke: '#3d4450', w: 5, z: zc - 0.01 }); line3(cv, j, hd, { stroke: '#3d4450', w: 5, z: zc - 0.01 });
    const sh = ring(add(hd, [0.04, -0.06, 0]), [1, 0, 0], [0, 0, 1], 0.1, 0.1, 16).concat(ring(add(hd, [0, 0.03, 0]), [1, 0, 0], [0, 0, 1], 0.045, 0.045, 12));
    cv.blob(zc - 0.02, hull(proj(cv, sh)), { poly: true, fill: on ? '#f6c453' : '#4a5260', stroke: INK, w: 2, rough: 0.4, seed: 63 });
    if (on) { const q = cv.cam.p(add(hd, [0.06, -0.38, 0])), k = cv.cam.k(add(hd, [0.06, -0.38, 0])); cv.svg(zc + 0.4, `<ellipse cx="${f1(q[0])}" cy="${f1(q[1])}" rx="${f1(0.45 * k)}" ry="${f1(0.16 * k)}" fill="#ffe9a8" fill-opacity="0.45"/>`, 0); }
  };
  PROPS.cable = (cv, o) => { const pts = o.pts.map((p) => cv.cam.p(p)); cv.line(cv.cam.depth(o.pts[0]) + (o.bias || 0), pts, { stroke: o.c || '#2d3540', w: 3.4, smooth: true, rough: 0.3, seed: 64 }); };
  PROPS.pans = (cv, o) => {   // pans and a ladle hanging on the back wall
    const { x, y, z } = o; line3(cv, [x, y, z + 0.02], [x + 1.0, y, z + 0.02], { stroke: '#6b7280', w: 4, layer: -1 });
    [[0.15, 0.13, '#5b6470'], [0.5, 0.17, '#a5562f'], [0.85, 0.11, '#5b6470']].forEach(([dx, r, c], i) => { const cc = [x + dx, y - 0.12 - r, z + 0.03]; line3(cv, [x + dx, y, z + 0.03], add(cc, [0, r, 0]), { stroke: INK, w: 3, layer: -1 }); cv.blob(cv.cam.depth(cc), proj(cv, ring(cc, [1, 0, 0], [0, 1, 0], r, r, 18)), { fill: c, stroke: INK, w: 2, rough: 0.6, seed: 70 + i, layer: -1 }); });
  };
  PROPS.jars = (cv, o) => { const { x, y, z } = o; ['#c94f3d', '#e2b04a', '#6aa56f', '#8b6b4a'].forEach((c, i) => { cyl(cv, { x: x + i * 0.11, z, y, h: 0.14 + (i % 2) * 0.03, r: 0.035, c, id: 'jar' + i, lw: 1.5 }); }); };
  PROPS.hood = (cv, o) => { const { x, z } = o; box(cv, { x, y: 1.75, z, w: 0.8, h: 0.12, d: 0.55, c: '#b9c0c8', id: 'hood' }); box(cv, { x: x + 0.25, y: 1.87, z, w: 0.3, h: 0.93, d: 0.3, c: '#c7cdd3', id: 'hood2' }); };
  PROPS.cup = (cv, o) => cyl(cv, { x: o.x, z: o.z, y: o.y, h: 0.11, r: 0.035, r2: 0.042, c: o.c || '#dbe9f3', id: 'cup' + o.x + o.z, lw: 1.5 });
  PROPS.notebook = (cv, o) => { box(cv, { x: o.x - 0.1, y: o.y, z: o.z - 0.14, w: 0.2, h: 0.015, d: 0.28, c: o.c || '#2f5d8a', id: 'nb' + o.x }); };
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }

  // ───────────── shots ─────────────
  function camAt(keys, t) {
    if (t <= keys[0].t) return keys[0];
    for (let i = 0; i < keys.length - 1; i++) {
      const a = keys[i], b = keys[i + 1];
      if (t <= b.t) { const k = ease((t - a.t) / (b.t - a.t || 1)); return { pos: vlerp(a.pos, b.pos, k), look: vlerp(a.look, b.look, k), fov: lerp(a.fov || 42, b.fov || 42, k) }; }
    }
    return keys[keys.length - 1];
  }
  function propState(keys, t) { let s = {}; for (const k of keys || []) { if (k.t > t) break; s = Object.assign({}, s, k.set); } return s; }

  function bubble(cv, W, H, anchor, text, k, style, name) {
    // anchor: screen point of the speaker's head top
    const lines = wrap(text, 15);
    const fs = 26, lh = 34;
    const bw = Math.max(...lines.map((l) => textW(l))) * fs + 36, bh = lines.length * lh + 22;
    let bx = anchor[0] - bw * 0.3, by = anchor[1] - bh - 46;
    bx = clamp(bx, 16, W - bw - 16); by = clamp(by, 12, H - bh - 120);
    const s = 0.6 + 0.4 * ease(k * 3);
    const cx = bx + bw / 2, cy = by + bh / 2;
    const r = 18;
    let d = `M${bx + r} ${by}H${bx + bw - r}Q${bx + bw} ${by} ${bx + bw} ${by + r}V${by + bh - r}Q${bx + bw} ${by + bh} ${bx + bw - r} ${by + bh}`;
    const tx = clamp(anchor[0], bx + 30, bx + bw - 30);
    const tip = [clamp(anchor[0], 10, W - 10), clamp(anchor[1] - 10, by + bh + 18, H - 10)];
    d += `H${tx + 14}L${tip[0]} ${tip[1]}L${tx - 8} ${by + bh}H${bx + r}Q${bx} ${by + bh} ${bx} ${by + bh - r}V${by + r}Q${bx} ${by} ${bx + r} ${by}Z`;
    const g = cv.gen;
    const dr = g.path(d, { stroke: INK, strokeWidth: 2.4, roughness: 0.6, seed: hash(text), disableMultiStroke: false });
    const strokes = g.toPaths(dr).map((p) => `<path d="${p.d}" fill="none" stroke="${INK}" stroke-width="2.4"${style === 'phone' ? ' stroke-dasharray="8 6"' : ''}/>`).join('');
    let out = `<g transform="translate(${f1(cx)} ${f1(cy)}) scale(${f1(s * 100) / 100}) translate(${f1(-cx)} ${f1(-cy)})" opacity="${f1(clamp(k * 4) * 100) / 100}">`;
    out += `<path d="${d}" fill="#ffffff"/>` + strokes;
    if (name) out += `<text x="${f1(bx + 14)}" y="${f1(by - 8)}" font-size="20" font-family="WQHand" fill="#5f6b76">${esc(name)}</text>`;
    lines.forEach((l, i) => (out += `<text x="${f1(bx + 18)}" y="${f1(by + 11 + (i + 0.8) * lh)}" font-size="${fs}" font-family="WQHand" fill="${INK}">${esc(l)}</text>`));
    return out + '</g>';
  }
  function textW(s) { let w = 0; for (const ch of s) w += /[\x00-\x7f]/.test(ch) ? 0.55 : 1; return w; }
  function wrap(s, n) {
    const out = []; let cur = '';
    const punct = '，。！？、：；”）》,.!?';
    for (const ch of s) { if (textW(cur + ch) > n && !punct.includes(ch)) { out.push(cur); cur = ''; } cur += ch; }
    if (cur) out.push(cur);
    return out;
  }

  // approximate head centre of a character (for camera framing)
  function headOf(story, shot, name, t) {
    const keys = (shot.chars || {})[name]; if (!keys) return null;
    const st = charState(keys, t), look = Object.assign({}, LOOK0, story.cast[name] || {}), h = look.height;
    const P = mixPose(poseVec(st.prevPose), poseVec(st.pose), curPoseK(st, t));
    const hipY = P.sit ? 0.47 + (h - 1.7) * 0.05 : 0.535 * h;
    const r = 0.39 * h, fa = curFace(st, t) * D, ln = P.lean * D;
    return { c: [st.pos[0] + sin(fa) * sin(ln) * r, hipY + cos(ln) * r, st.pos[1] + cos(fa) * sin(ln) * r], face: curFace(st, t), h };
  }
  function shake(t, a) { return [a * (sin(t * 1.31) * 0.6 + sin(t * 2.93 + 1) * 0.4), a * (sin(t * 1.07 + 2) * 0.6 + sin(t * 2.41) * 0.4), a * sin(t * 0.9 + 4) * 0.5]; }
  function cutCam(story, shot, cut, t, t1) {
    const sp = cut.spec, k = clamp((t - cut.t) / max(0.5, t1 - cut.t));
    if (sp.pos) {   // fixed / insert shot, gentle move from pos to pos2
      return { pos: vlerp(sp.pos, sp.pos2 || sp.pos, ease(k)), look: vlerp(sp.look, sp.look2 || sp.look, ease(k)), fov: sp.fov || 36, focus: sp.focus, dof: sp.dof !== false && !!sp.insert };
    }
    if (sp.close || sp.medium) {
      const who = sp.close || sp.medium, hd = headOf(story, shot, who, t); if (!hd) return null;
      const close = !!sp.close;
      const dist = (sp.dist || (close ? 0.95 : 2.0)) * (1.07 - 0.1 * k);
      const a = (hd.face + (sp.ang == null ? 28 : sp.ang)) * D;
      const tgt = add(hd.c, [0, close ? -0.06 : -0.32, 0]);
      const pos = add(tgt, [sin(a) * dist, (sp.up == null ? (close ? 0.04 : 0.1) : sp.up), cos(a) * dist]);
      return { pos, look: tgt, fov: sp.fov || (close ? 30 : 36), focus: dist, dof: true };
    }
    if (sp.ots) {
      const A = headOf(story, shot, sp.ots[0], t), B = headOf(story, shot, sp.ots[1], t); if (!A || !B) return null;
      const d = norm([B.c[0] - A.c[0], 0, B.c[2] - A.c[2]]), side = [-d[2], 0, d[0]], sg = sp.side || 1;
      const pos = add(A.c, add(mul(d, -0.62 * (1.04 - 0.06 * k)), add(mul(side, 0.36 * sg), [0, 0.07, 0])));
      const look = add(B.c, [0, -0.1, 0]);
      return { pos, look, fov: sp.fov || 34, focus: sqrt(dot(sub(look, pos), sub(look, pos))), dof: true };
    }
    if (sp.two) {
      const A = headOf(story, shot, sp.two[0], t), B = headOf(story, shot, sp.two[1], t); if (!A || !B) return null;
      const m = add(mul(add(A.c, B.c), 0.5), [0, -0.25, 0]), d = norm([B.c[0] - A.c[0], 0, B.c[2] - A.c[2]]);
      let n = [-d[2], 0, d[0]]; if (sp.flip) n = mul(n, -1);
      const dist = (sp.dist || 2.4) * (1.04 - 0.06 * k);
      return { pos: add(m, add(mul(n, dist), [0, 0.15, 0])), look: m, fov: sp.fov || 36, focus: dist, dof: true };
    }
    return null;
  }

  function render(story, t, opts) {
    opts = opts || {};
    const [W, H] = story.size;
    const shot = story.shots.find((s) => t >= s.t0 && t < s.t1) || story.shots[story.shots.length - 1];
    const tl = t - shot.t0;
    const gen = global.rough.generator();
    let svg = `<rect width="${W}" height="${H}" fill="#fbf8f2"/>`;
    if (shot.title) return svg + titleCard(shot, tl, W, H, gen);
    let ck = camAt(shot.cam, t), focus = null, closeUp = false;
    const cuts = shot.cuts || [];
    let ci = -1; for (let i = 0; i < cuts.length; i++) if (cuts[i].t <= t) ci = i;
    if (ci >= 0 && !cuts[ci].spec.wide) { const c = cutCam(story, shot, cuts[ci], t, ci + 1 < cuts.length ? cuts[ci + 1].t : shot.t1); if (c) { ck = c; focus = c.dof ? c.focus : null; closeUp = true; } }
    const hand = shake(t, closeUp ? 0.006 : 0.012);
    let cpos = add(ck.pos, hand), clook = add(ck.look, mul(hand, 0.5));
    if (opts.orbit) {   // viewer drags while paused
      const d = sub(cpos, clook), r = sqrt(d[0] * d[0] + d[2] * d[2]), a = atan2(d[0], d[2]) + opts.orbit[0];
      cpos = [clook[0] + r * sin(a), clamp(cpos[1] + opts.orbit[1], 0.4, 6), clook[2] + r * cos(a)];
      focus = null;
    }
    const cam = Camera(cpos, clook, ck.fov, W, H);
    const cv = Canvas(cam, gen); cv.gen = gen;
    // scene props
    const pstate = {};
    for (const p of story.scenes[shot.scene]) {
      const fn = PROPS[p.type]; if (!fn) continue;
      const o = Object.assign({}, p, { t, state: propState((shot.props || {})[p.id], t), mood: shot.mood });
      if (o.state.hide) continue;
      pstate[p.id] = o.state;
      fn(cv, o);
    }
    // people
    const ctx = { pos: {}, heads: {}, hands: {} };
    const states = {};
    for (const [name, keys] of Object.entries(shot.chars || {})) { const st = charState(keys, t); states[name] = st; ctx.pos[name] = st.pos; }
    const speaking = {};
    for (const b of shot.bubbles || []) if (t >= b.t0 && t < b.t1 - 0.15 && b.style !== 'phone') speaking[b.who] = true;
    for (const [name, st] of Object.entries(states)) {
      if (!st.show) continue;
      const look = story.cast[name] || {};
      const person = drawPerson(cv, name, look, st, t, speaking[name], ctx);
      const start = cv.items.length;
      person.draw();
      for (let i = start; i < cv.items.length; i++) cv.items[i].z = person.z - (i - start) * 0.00001;
    }
    const reveal = shot.reveal === false ? 1 : clamp(tl / 1.3);
    svg += cv.render(reveal, focus);
    // mood: night = dark room with a pool of lamp light
    if (shot.mood && shot.mood.night) {
      const L = shot.mood.light ? cam.p(shot.mood.light) : [W / 2, H / 2];
      svg += `<defs><radialGradient id="wq-night" gradientUnits="userSpaceOnUse" cx="${f1(L[0])}" cy="${f1(L[1])}" r="${f1(W * 0.75)}"><stop offset="0" stop-color="#0d1a3a" stop-opacity="0"/><stop offset="0.3" stop-color="#0d1a3a" stop-opacity="0.22"/><stop offset="1" stop-color="#0d1a3a" stop-opacity="0.62"/></radialGradient></defs><rect width="${W}" height="${H}" fill="url(#wq-night)"/>`;
    }
    svg += `<defs><radialGradient id="wq-vig" cx="50%" cy="50%" r="75%"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.22"/></radialGradient></defs><rect width="${W}" height="${H}" fill="url(#wq-vig)"/>`;
    // speech: bubble in wide shots; lower-third caption with the speaker's name in close-ups or when the speaker is off screen
    for (const b of shot.bubbles || []) {
      if (t < b.t0 || t >= b.t1) continue;
      let anchor, big = false, off = false;
      if (b.style === 'phone') { const hd = ctx.heads[b.at]; anchor = hd ? cam.p(add(hd.c, [0.15, 0.05, 0])) : [W * 0.7, H * 0.3]; big = closeUp; }
      else {
        const hd = ctx.heads[b.who];
        if (hd) { anchor = cam.p(hd.top); const c = cam.p(hd.c); big = (c[1] - anchor[1]) > 70; off = c[2] < 0.2 || c[0] < 0 || c[0] > W || c[1] < 0 || c[1] > H; }
        else off = true;
      }
      if (big || off || closeUp) svg += caption(W, H, b, t - b.t0);
      else svg += bubble(cv, W, H, anchor, b.text, t - b.t0, b.style, b.label);
    }
    // subtitles (narration)
    for (const s of shot.subs || []) {
      if (t < s.t0 || t >= s.t1) continue;
      const lines = wrap(s.text, 30), fs = 30, lh = 40;
      const bh = lines.length * lh + 16, y0 = H - bh - 22;
      const bw = Math.max(...lines.map(textW)) * fs + 48;
      svg += `<rect x="${f1(W / 2 - bw / 2)}" y="${f1(y0)}" width="${f1(bw)}" height="${bh}" rx="10" fill="#1d2329" fill-opacity="0.72"/>`;
      lines.forEach((l, i) => (svg += `<text x="${W / 2}" y="${f1(y0 + 8 + (i + 0.78) * lh)}" font-size="${fs}" font-family="WQHand" fill="#fff" text-anchor="middle">${esc(l)}</text>`));
    }
    if (story.watermark) svg += `<text x="18" y="30" font-size="18" font-family="WQHand" fill="#8a96a3">${esc(story.watermark)}</text>`;
    return svg;
  }
  function caption(W, H, b, age) {
    const lines = wrap(b.text, 26), fs = 32, lh = 42;
    const name = b.label || b.who;
    const bh = lines.length * lh + 18, y0 = H - bh - 24;
    const bw = Math.max(...lines.map(textW)) * fs + 52;
    const a = clamp(age * 6);
    let o = `<g opacity="${f1(a * 100) / 100}"><rect x="${f1(W / 2 - bw / 2)}" y="${f1(y0)}" width="${f1(bw)}" height="${bh}" rx="10" fill="#fffdf6" stroke="${INK}" stroke-width="2.4"${b.style === 'phone' ? ' stroke-dasharray="8 6"' : ''}/>`;
    o += `<rect x="${f1(W / 2 - bw / 2 + 14)}" y="${f1(y0 - 18)}" width="${f1(textW(name) * 22 + 22)}" height="30" rx="8" fill="#f0b14a" stroke="${INK}" stroke-width="2"/><text x="${f1(W / 2 - bw / 2 + 25)}" y="${f1(y0 + 4)}" font-size="22" font-family="WQHand" fill="${INK}">${esc(name)}</text>`;
    lines.forEach((l, i) => (o += `<text x="${W / 2}" y="${f1(y0 + 12 + (i + 0.8) * lh)}" font-size="${fs}" font-family="WQHand" fill="${INK}" text-anchor="middle">${esc(l)}</text>`));
    return o + '</g>';
  }
  function titleCard(shot, tl, W, H, gen) {
    let out = '';
    const k = clamp(tl / 1.2);
    const T = shot.title;
    out += `<clipPath id="wq-wipe"><rect x="0" y="0" width="${f1(W * k)}" height="${H}"/></clipPath>`;
    out += `<g clip-path="url(#wq-wipe)"><text x="${W / 2}" y="${H * 0.45}" font-size="84" font-family="WQHand" fill="#1d2329" text-anchor="middle">${esc(T.zh)}</text></g>`;
    const dr = gen.line(W * 0.3, H * 0.5, W * 0.3 + W * 0.4 * clamp((tl - 0.6) / 0.8), H * 0.5, { stroke: '#c98a00', strokeWidth: 5, roughness: 1.2, seed: 5 });
    if (tl > 0.6) out += gen.toPaths(dr).map((p) => `<path d="${p.d}" stroke="#c98a00" stroke-width="5" fill="none" stroke-linecap="round"/>`).join('');
    if (T.sub) out += `<text x="${W / 2}" y="${H * 0.58}" font-size="30" font-family="WQHand" fill="#5f6b76" text-anchor="middle" opacity="${f1(clamp((tl - 1) / 0.6) * 100) / 100}">${esc(T.sub)}</text>`;
    if (T.note) out += `<text x="${W / 2}" y="${H * 0.9}" font-size="22" font-family="WQHand" fill="#8a96a3" text-anchor="middle" opacity="${f1(clamp((tl - 1.2) / 0.6) * 100) / 100}">${esc(T.note)}</text>`;
    return out;
  }

  global.WQScene3D = { render, POSES, EXPR };
})(typeof window !== 'undefined' ? window : globalThis);
