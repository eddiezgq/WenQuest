// 第 172b 轮第二批：说明书互动块共用的小工具（语言、SVG、和三维整机 index.html 的连接）
(function () {
  'use strict';
  const q = new URLSearchParams(location.search);
  const LANG = (q.get('lang') || (navigator.language || 'zh')).startsWith('en') ? 'en' : 'zh';
  const S = (tag, a, txt) => `<${tag} ${Object.entries(a).map(([k, v]) => `${k}="${v}"`).join(' ')}>${txt === undefined ? '' : txt}</${tag}>`;
  const $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  // 三维整机：iframe 载入 index.html?embed=1…，等 window.__wq 准备好再回调
  function m3d(frame, params, cb) {
    frame.src = `index.html?embed=1&lang=${LANG}&${params}`;
    frame.addEventListener('load', () => {
      const tryHook = () => { const w = frame.contentWindow; if (w && w.__wq) { w.__wq.setPlay(false); cb(w.__wq); } else setTimeout(tryHook, 300); };
      tryHook();
    });
  }
  // 折线：xs 索引 → 像素
  function path(arr, X, Y, step) { let d = ''; arr.forEach((v, i) => { d += `${i ? 'L' : 'M'}${X(i * (step || 1)).toFixed(1)},${Y(v).toFixed(1)}`; }); return d; }
  function ink() { return getComputedStyle(document.body).color; }
  function tipper() {
    let el = document.querySelector('.tip'); if (!el) { el = document.createElement('div'); el.className = 'tip'; document.body.appendChild(el); }
    return { show(x, y, h) { el.innerHTML = h; el.style.display = 'block'; const w = el.offsetWidth; el.style.left = Math.min(innerWidth - w - 8, x + 12) + 'px'; el.style.top = (y + 14) + 'px'; }, hide() { el.style.display = 'none'; } };
  }
  // 色带（蓝 → 青 → 黄 → 红），t 0–1
  function heat(t) {
    t = Math.max(0, Math.min(1, t));
    const st = [[0.19, 0.31, 0.69], [0.13, 0.62, 0.74], [0.45, 0.78, 0.38], [0.98, 0.78, 0.2], [0.85, 0.2, 0.15]];
    const x = t * (st.length - 1), i = Math.min(st.length - 2, Math.floor(x)), u = x - i;
    return st[i].map((c, k) => c + (st[i + 1][k] - c) * u);
  }
  function heatCss(t) { return `rgb(${heat(t).map(c => Math.round(c * 255)).join(',')})`; }
  window.WQL = { q, LANG, S, $, esc, m3d, path, ink, tipper, heat, heatCss, labs: () => fetch('labs.json').then(r => r.json()), proto: () => fetch('proto.json').then(r => r.json()) };
})();
