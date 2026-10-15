/* 问渠白板讲课播放器（第 35 轮）。WB.init(svg, DATA) 后 WB.seek(秒) 画到那一刻：
   线条按笔画走（rough.js 手绘线，Excalidraw 同款），字先描边再填色，镜头在画板之间平移，一支笔跟着笔尖。
   seek 只由时间决定（同一时刻画面相同），网页播放和逐帧出视频用同一份代码。 */
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  const ease = (p) => (p < .5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2);
  const clamp = (v) => Math.max(0, Math.min(1, v));
  let D, world, pen, items = [], gen;

  function mk(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function roughPaths(it) {
    const s = it.shape, o = Object.assign({ roughness: 1.1, bowing: 1.2, disableMultiStroke: false }, it.opts);
    let dr;
    if (s.type === 'rect') dr = gen.rectangle(s.x, s.y, s.w, s.h, o);
    else if (s.type === 'ellipse') dr = gen.ellipse(s.x + s.w / 2, s.y + s.h / 2, s.w, s.h, o);
    else dr = gen.linearPath(s.pts, o);
    return gen.toPaths(dr).map((p) => ({ d: p.d, c: p.stroke === 'none' ? (p.fill || o.stroke) : p.stroke, w: p.strokeWidth || o.strokeWidth, fillPath: p.stroke === 'none' }));
  }

  function init(svg, data) {
    D = data;
    gen = rough.generator();
    world = mk('g', { id: 'world' }, svg);
    D.boards.forEach((b, i) => {
      const g = mk('g', { transform: `translate(${b.ox},${b.oy})` }, world);
      b.g = g;
    });
    items = D.items.map((it) => {
      const g = D.boards[it.b].g;
      const paths = it.k === 'rough' ? roughPaths(it) : it.paths;
      const parts = paths.filter((p) => !p.fillPath).map((p) => {
        const e = mk('path', { d: p.d, fill: p.f ? p.c : 'none', stroke: p.c, 'stroke-width': p.w || 1.4,
          'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, g);
        const L = Math.max(1, e.getTotalLength());
        e.style.strokeDasharray = L + ' ' + L;
        e.style.strokeDashoffset = L;
        if (p.f) e.style.fillOpacity = 0;
        e.style.visibility = 'hidden';
        return { e, L, f: !!p.f };
      });
      let acc = 0;
      parts.forEach((p) => { p.a = acc; acc += p.L; p.z = acc; });
      return Object.assign({}, it, { parts, total: acc, ox: D.boards[it.b].ox, oy: D.boards[it.b].oy });
    });
    pen = document.getElementById('pen');
    seek(0);
  }

  function pointOf(it, p) {
    const d = it.total * clamp(p);
    let part = it.parts[it.parts.length - 1];
    for (const q of it.parts) if (d <= q.z) { part = q; break; }
    const pt = part.e.getPointAtLength(Math.max(0, Math.min(part.L, d - part.a)));
    return { x: pt.x + it.ox, y: pt.y + it.oy };
  }

  function camAt(t) {
    let c = { x: D.boards[0].ox, y: D.boards[0].oy, moving: false };
    for (const k of D.cam) {
      if (t >= k.t1) c = { x: k.b[0], y: k.b[1], moving: false };
      else if (t >= k.t0) { const p = ease((t - k.t0) / (k.t1 - k.t0)); c = { x: k.a[0] + (k.b[0] - k.a[0]) * p, y: k.a[1] + (k.b[1] - k.a[1]) * p, moving: true }; break; }
      else break;
    }
    return c;
  }

  function seek(t) {
    let cur = null, prev = null, next = null;
    for (const it of items) {
      const p = clamp((t - it.start) / it.dur), d = it.total * p;
      for (const q of it.parts) {
        const drawn = Math.max(0, Math.min(q.L, d - q.a));
        q.e.style.strokeDashoffset = q.L - drawn;
        q.e.style.visibility = drawn > 0 ? 'visible' : 'hidden';   // a round cap would show a dot before the stroke starts
        if (q.f) { const done = it.start + it.dur * q.z / it.total; q.e.style.fillOpacity = clamp((t - done) / 0.3); }
      }
      if (t >= it.start && t < it.start + it.dur) cur = it;
      if (it.start + it.dur <= t) prev = it; else if (!next && it.start > t) next = it;
    }
    const cam = camAt(t);
    world.setAttribute('transform', `translate(${-cam.x},${-cam.y})`);
    let pos, away = { x: 2300, y: 1500 };
    if (cam.moving) pos = null;
    else if (cur) pos = pointOf(cur, (t - cur.start) / cur.dur);
    else if (prev && next && next.b === prev.b && next.start - (prev.start + prev.dur) < 1.8) {
      const a = pointOf(prev, 1), b = pointOf(next, 0), g = next.start - (prev.start + prev.dur);
      const p = ease(clamp((t - prev.start - prev.dur) / g));
      pos = { x: a.x + (b.x - a.x) * p, y: a.y + (b.y - a.y) * p };
    } else if (prev && (!next || next.start - t > 0.9 || next.b !== prev.b)) {
      const a = pointOf(prev, 1), k = ease(clamp((t - prev.start - prev.dur) / 0.9));
      pos = { x: a.x + 340 * k, y: a.y + 900 * k };
    } else if (next) {
      const n = pointOf(next, 0), k = ease(clamp((t - (next.start - 0.9)) / 0.9));
      pos = { x: n.x + 340 * (1 - k), y: n.y + 900 * (1 - k) };
    }
    const sp = pos ? { x: pos.x - cam.x, y: pos.y - cam.y } : away;
    pen.setAttribute('transform', `translate(${sp.x},${sp.y})`);
    return t;
  }

  window.WB = { init, seek };
})();
