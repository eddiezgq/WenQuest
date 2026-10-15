/* 问渠白板讲课播放器（第 35 轮）。WB.init(svg, DATA) 后 WB.seek(秒) 画到那一刻：
   线条按笔画走（rough.js 手绘线，Excalidraw 同款），字先描边再填色，镜头在画板之间平移，一支笔跟着笔尖。
   seek 只由时间决定（同一时刻画面相同），网页播放和逐帧出视频用同一份代码。 */
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  const ease = (p) => (p < .5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2);
  const clamp = (v) => Math.max(0, Math.min(1, v));
  let D, world, pen, items = [], gen, groups = {}, moves = [], media = [], stage = null;

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
    groups = {};
    items = D.items.map((it) => {
      // each drawn thing has its own group, so "moves" can turn, shift or spin it (第 35 轮：画的东西活起来)
      const g = mk('g', {}, D.boards[it.b].g);
      if (it.eid) (groups[it.b + ':' + it.eid] = groups[it.b + ':' + it.eid] || []).push(g);
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
      return Object.assign({}, it, { parts, total: acc, ox: D.boards[it.b].ox, oy: D.boards[it.b].oy, g });
    });
    moves = (D.moves || []).map((m) => {
      const gs = [].concat(...m.targets.map((id) => groups[m.b + ':' + id] || []));
      let c = m.pivot;
      if (!c && gs.length) {   // pulse and spin without a pivot: the centre of what moves
        const bb = gs.map((g) => g.getBBox()).filter((b) => b.width || b.height);
        if (bb.length) {
          const x0 = Math.min(...bb.map((b) => b.x)), y0 = Math.min(...bb.map((b) => b.y));
          const x1 = Math.max(...bb.map((b) => b.x + b.width)), y1 = Math.max(...bb.map((b) => b.y + b.height));
          c = [(x0 + x1) / 2, (y0 + y1) / 2];
        }
      }
      const parts = [].concat(...items.filter((it) => it.eid && m.targets.includes(it.eid) && it.b === m.b).map((it) => it.parts));
      return Object.assign({}, m, { gs, c: c || [0, 0], parts });
    });
    initMedia();
    pen = document.getElementById('pen');
    seek(0);
  }

  // ---- media frames: our own virtual labs, animations and digital-factory videos, played inside a hand-drawn frame
  function initMedia() {
    media = [];
    stage = document.getElementById('stage');
    if (!stage || !(D.media || []).length) return;
    let layer = document.getElementById('wbmedia');
    if (!layer) { layer = document.createElement('div'); layer.id = 'wbmedia'; stage.appendChild(layer); }
    layer.style.cssText = 'position:absolute;inset:0;pointer-events:none;overflow:hidden';
    media = D.media.map((m) => {
      const box = document.createElement('div');
      box.style.cssText = 'position:absolute;left:0;top:0;transform-origin:0 0;opacity:0;background:#fff;overflow:hidden';
      let el;
      if (m.kind === 'video') {
        el = document.createElement('video');
        el.src = m.url; el.muted = true; el.playsInline = true; el.preload = 'auto';
        el.style.cssText = 'width:100%;height:100%;object-fit:contain;background:#fff';
      } else {
        el = document.createElement('iframe');
        if (m.html) el.srcdoc = m.html; else el.src = m.url;
        el.setAttribute('sandbox', 'allow-scripts allow-same-origin');
        el.style.cssText = 'border:0;width:' + m.w * (m.zoom || 1.6) + 'px;height:' + m.h * (m.zoom || 1.6) + 'px;transform:scale(' + 1 / (m.zoom || 1.6) + ');transform-origin:0 0';
        if (m.hash) el.addEventListener('load', () => { try { el.contentWindow.location.hash = m.hash; } catch (e) { /* cross-origin */ } });
      }
      box.appendChild(el);
      layer.appendChild(box);
      return Object.assign({}, m, { box, el });
    });
  }

  function placeMedia(t, cam) {
    if (!media.length) return;
    const k = stage.clientWidth / D.W;
    for (const m of media) {
      const b = D.boards[m.b];
      const x = (b.ox + m.x - cam.x) * k, y = (b.oy + m.y - cam.y) * k;
      m.box.style.width = m.w + 'px'; m.box.style.height = m.h + 'px';
      m.box.style.transform = `translate(${x}px,${y}px) scale(${k})`;
      const on = t >= m.start;
      m.box.style.opacity = on ? Math.min(1, (t - m.start) / 0.4) : 0;
      m.box.style.pointerEvents = on && m.kind !== 'video' ? 'auto' : 'none';
      if (m.kind === 'video' && m.el.readyState >= 1) {
        const want = Math.max(0, Math.min(m.play || m.el.duration || 0, t - m.start)) + (m.from || 0);
        const playing = window.WB_PLAYING && on && t < m.start + (m.play || 1e9);
        if (playing) { if (m.el.paused) m.el.play().catch(() => {}); if (Math.abs(m.el.currentTime - want) > 0.35) m.el.currentTime = want; }
        else { if (!m.el.paused) m.el.pause(); if (Math.abs(m.el.currentTime - want) > 0.04) m.el.currentTime = want; }
      }
    }
  }

  // frame-by-frame recording waits until every video shows the asked frame
  function settle() {
    return Promise.all(media.filter((m) => m.kind === 'video').map((m) => new Promise((ok) => {
      if (!m.el.seeking && m.el.readyState >= 2) return ok();
      const done = () => { m.el.removeEventListener('seeked', done); m.el.removeEventListener('loadeddata', done); ok(); };
      m.el.addEventListener('seeked', done); m.el.addEventListener('loadeddata', done);
      setTimeout(ok, 3000);
    })));
  }

  function applyMoves(t) {
    const tf = new Map();
    for (const m of moves) {
      if (t < m.start) continue;
      const p = clamp((t - m.start) / (m.dur || 1)), e = ease(p);
      let s = '';
      if (m.kind === 'rotate') s = `rotate(${(m.to || 0) * e} ${m.c[0]} ${m.c[1]})`;
      else if (m.kind === 'shift') s = `translate(${(m.dx || 0) * e},${(m.dy || 0) * e})`;
      else if (m.kind === 'spin') s = `rotate(${(m.rpm || 30) * 6 * (Math.min(t, m.end || 1e9) - m.start)} ${m.c[0]} ${m.c[1]})`;
      else if (m.kind === 'pulse') { const k = 1 + 0.14 * Math.sin(Math.PI * p); s = `translate(${m.c[0]},${m.c[1]}) scale(${k}) translate(${-m.c[0]},${-m.c[1]})`; }
      if (s) for (const g of m.gs) tf.set(g, s + ' ' + (tf.get(g) || ''));
      if (m.kind === 'flow' && t < (m.end || 1e9)) {
        for (const q of m.parts) { q.e.style.strokeDasharray = '18 14'; q.e.style.strokeDashoffset = -(t - m.start) * (m.speed || 70); }
      }
    }
    for (const it of items) it.g.setAttribute('transform', tf.get(it.g) || '');
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
        q.e.style.strokeDasharray = q.L + ' ' + q.L;
        q.e.style.strokeDashoffset = q.L - drawn;
        q.e.style.visibility = drawn > 0 ? 'visible' : 'hidden';   // a round cap would show a dot before the stroke starts
        if (q.f) { const done = it.start + it.dur * q.z / it.total; q.e.style.fillOpacity = clamp((t - done) / 0.3); }
      }
      if (t >= it.start && t < it.start + it.dur) cur = it;
      if (it.start + it.dur <= t) prev = it; else if (!next && it.start > t) next = it;
    }
    applyMoves(t);
    const cam = camAt(t);
    world.setAttribute('transform', `translate(${-cam.x},${-cam.y})`);
    placeMedia(t, cam);
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

  window.WB = { init, seek, settle };
})();
