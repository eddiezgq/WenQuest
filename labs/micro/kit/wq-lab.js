/* 问渠微电子实验组件库（第 17 轮 RM4）
 * 参数面板、读数、曲线图、任务判定、中 / EN 切换、操作记录。
 * 不依赖外部库；构建时内联进单个 HTML，可离线打开。
 */
(function (root) {
  const $ = (id) => document.getElementById(id);
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

  // ---------- 存储（私密窗口等环境可能不可用，全部 try/catch） ----------
  function makeStore(prefix) {
    return {
      get(k) { try { const v = localStorage.getItem(prefix + k); return v ? JSON.parse(v) : null; } catch (e) { return null; } },
      set(k, v) { try { localStorage.setItem(prefix + k, JSON.stringify(v)); } catch (e) { /* 忽略 */ } },
    };
  }

  const Lab = { log: [], tasks: {}, hooks: [], lang: 'zh' };
  let store = makeStore('wq-');
  let LAB_ID = 'lab';

  // ---------- 操作记录：报给问渠（父窗口），字段对齐第 2 轮附录 lab_task_status ----------
  Lab.report = function (type, data) {
    const msg = Object.assign({ source: 'wenquest-lab', lab_page: LAB_ID, type, t: new Date().toISOString() }, data);
    Lab.log.push(msg);
    try { if (root.parent && root.parent !== root) root.parent.postMessage(msg, '*'); } catch (e) { /* 忽略 */ }
  };

  // ---------- 语言 ----------
  Lab.T = (zh, en) => (Lab.lang === 'en' ? en : zh);
  Lab.onLang = (f) => { Lab.hooks.push(f); };
  Lab.applyLang = function () {
    document.documentElement.lang = Lab.lang === 'en' ? 'en' : 'zh-CN';
    document.querySelectorAll('[data-en]').forEach((el) => {
      if (el.dataset.zh === undefined) el.dataset.zh = el.innerHTML;
      el.innerHTML = Lab.lang === 'en' ? el.dataset.en : el.dataset.zh;
    });
    document.querySelectorAll('[data-ph-en]').forEach((el) => {
      if (el.dataset.phZh === undefined) el.dataset.phZh = el.placeholder;
      el.placeholder = Lab.lang === 'en' ? el.dataset.phEn : el.dataset.phZh;
    });
    const b = $('lang'); if (b) b.textContent = Lab.lang === 'en' ? '中文' : 'EN';
    Lab.hooks.forEach((f) => f());
    paintTasks();
  };

  Lab.init = function (opts) {
    LAB_ID = opts.id; store = makeStore('wq-' + opts.id + '-');
    Lab.lang = store.get('lang') || 'zh';
    if (/(^|[-#])en$/.test(location.hash)) Lab.lang = 'en';
    const b = $('lang');
    if (b) b.onclick = () => { Lab.lang = Lab.lang === 'en' ? 'zh' : 'en'; store.set('lang', Lab.lang); Lab.report('lang', { lang: Lab.lang }); Lab.applyLang(); };
    Lab.saved = store.get('tasks') || {};
    Lab.report('open', {});
  };

  // ---------- 选项卡 ----------
  Lab.tabs = function (onShow) {
    const btns = [...document.querySelectorAll('nav.tabs button[data-lab]')];
    function show(key) {
      btns.forEach((b) => b.setAttribute('aria-selected', b.dataset.lab === key));
      document.querySelectorAll('section.lab').forEach((s) => (s.hidden = s.id !== 'lab-' + key));
      store.set('tab', key); onShow && onShow(key);
      Lab.report('tab', { lab: key });
    }
    btns.forEach((b) => (b.onclick = () => show(b.dataset.lab)));
    const want = (location.hash.match(/lab(\d+)/) || [])[1];
    show(want && btns.some((b) => b.dataset.lab === want) ? want : store.get('tab') || btns[0].dataset.lab);
    Lab.show = show;
  };

  // ---------- 控件 ----------
  Lab.range = function (id, show, onChange) {
    const el = $(id), out = $(id + 'o');
    const upd = () => { if (out) out.textContent = show(+el.value); };
    el.addEventListener('input', () => { upd(); onChange && onChange(); });
    el.addEventListener('change', () => Lab.report('param', { param: id, value: +el.value }));
    Lab.onLang(upd); upd();
    el.refresh = upd;
    el.set = (v) => { el.value = v; upd(); };
    return el;
  };
  Lab.readout = function (id, rows) {
    const dl = $(id);
    if (dl.childElementCount !== rows.length * 2) dl.innerHTML = rows.map(() => '<dt></dt><dd></dd>').join('');
    rows.forEach((r, i) => { dl.children[2 * i].textContent = r[0]; dl.children[2 * i + 1].textContent = r[1]; });
  };
  Lab.problem = function (id, zhT, zhX, enT, enX) {
    const el = $(id); el.hidden = false;
    el.innerHTML = '<b></b><span></span>';
    el.firstChild.textContent = Lab.T(zhT, enT); el.lastChild.textContent = Lab.T(zhX, enX);
  };

  // ---------- 数字格式 ----------
  Lab.fmt = (v, d = 2) => (Number.isFinite(v) ? v.toFixed(d) : '—');
  Lab.si = function (v, unit, digits = 3) {
    if (!Number.isFinite(v)) return '—';
    if (v === 0) return '0 ' + unit;
    const pre = [[1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'], [1e-6, 'μ'], [1e-9, 'n'], [1e-12, 'p'], [1e-15, 'f']];
    const a = Math.abs(v);
    for (const [s, p] of pre) if (a >= s * 0.9995) return (v / s).toPrecision(digits) + ' ' + p + unit;
    return v.toExponential(2) + ' ' + unit;
  };

  // ---------- 任务 ----------
  // t = {id, zh, en, robot?, check?(state)→bool, answer?:{value, tol, unit}}
  Lab.defineTasks = function (lab, list, ulId) {
    Lab.tasks[lab] = { ul: ulId, list: list.map((t) => Object.assign({}, t, { ok: !!Lab.saved[lab + ':' + t.id] })) };
  };
  Lab.done = function (lab, id) {
    const t = Lab.tasks[lab].list.find((x) => x.id === id);
    if (!t || t.ok) return;
    t.ok = true; Lab.saved[lab + ':' + id] = true; store.set('tasks', Lab.saved);
    Lab.report('task', { lab, task: id, ok: true });
    paintTasks();
  };
  Lab.check = function (lab, state) {
    const g = Lab.tasks[lab]; if (!g) return;
    g.list.forEach((t) => { if (!t.ok && t.check) { try { if (t.check(state)) Lab.done(lab, t.id); } catch (e) { /* 忽略 */ } } });
  };
  Lab.reset = function () {
    Lab.saved = {}; store.set('tasks', {});
    Object.values(Lab.tasks).forEach((g) => g.list.forEach((t) => (t.ok = false)));
    Lab.report('reset', {}); paintTasks();
  };
  function paintTasks() {
    let n = 0, k = 0;
    Object.entries(Lab.tasks).forEach(([lab, g]) => {
      const ul = $(g.ul); if (!ul) return;
      const keepVals = {};
      ul.querySelectorAll('input[data-task]').forEach((i) => (keepVals[i.dataset.task] = i.value));
      ul.innerHTML = '';
      let ok = 0;
      g.list.forEach((t) => {
        n++; if (t.ok) { k++; ok++; }
        const li = document.createElement('li');
        li.className = t.ok ? 'ok' : '';
        li.dataset.task = t.id;
        li.innerHTML = `<span class="box" aria-hidden="true">${t.ok ? '✓' : ''}</span><div class="t"></div>`;
        const box = li.querySelector('.t');
        if (t.robot) { const tag = document.createElement('span'); tag.className = 'tag'; tag.textContent = Lab.T('机器人', 'Robot'); box.appendChild(tag); }
        box.appendChild(document.createTextNode(Lab.T(t.zh, t.en)));
        if (t.answer && !t.ok) {
          const row = document.createElement('div'); row.className = 'ans';
          row.innerHTML = `<input inputmode="decimal" data-task="${lab}:${t.id}" aria-label="${Lab.T('答案', 'Answer')}"><span class="unit"></span><button class="btn chip">${Lab.T('提交', 'Check')}</button><span class="msg"></span>`;
          row.querySelector('.unit').textContent = t.answer.unit || '';
          const inp = row.querySelector('input'); inp.value = keepVals[lab + ':' + t.id] || '';
          const go = () => {
            const v = parseFloat(String(inp.value).replace(',', '.'));
            const a = t.answer, okv = Number.isFinite(v) && Math.abs(v - a.value) <= Math.abs(a.value) * a.tol;
            Lab.report('answer', { lab, task: t.id, value: v, ok: okv });
            if (okv) Lab.done(lab, t.id);
            else row.querySelector('.msg').textContent = Lab.T('再算一下', 'Not yet — check again');
          };
          row.querySelector('button').onclick = go;
          inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') go(); });
          box.appendChild(row);
        }
        ul.appendChild(li);
      });
      const tab = document.querySelector(`nav.tabs [data-lab="${lab}"] .done`);
      if (tab) tab.textContent = ok === g.list.length && ok ? '✓' : ok ? `${ok}/${g.list.length}` : '';
    });
    const p = $('progress'); if (p) p.textContent = Lab.T(`已完成 ${k} / ${n} 个任务`, `${k} / ${n} tasks done`);
  }
  Lab.paintTasks = paintTasks;

  // ---------- 开放问题：本地暂存，离开输入框时报给问渠 ----------
  Lab.openQuestion = function (lab, taId) {
    const ta = $(taId); if (!ta) return;
    ta.value = store.get('open:' + lab) || '';
    ta.addEventListener('input', () => store.set('open:' + lab, ta.value));
    ta.addEventListener('change', () => Lab.report('open_answer', { lab, length: ta.value.length }));
  };

  // ---------- 曲线图 ----------
  // opts: {x:[min,max], y:[min,max], xlabel, ylabel, xlog?, ylog?, series:[{x,y,color,width,dash,label}],
  //        points:[{x,y,color,label,r}], hlines:[{y,color,dash,label}], vlines:[{x,color,dash,label}], bands:[{y0,y1,color}],
  //        xfmt, yfmt}
  Lab.plot = function (canvas, opts) {
    const dpr = root.devicePixelRatio || 1;
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) { canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr); }
    const c = canvas.getContext('2d'); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, w, h);
    const small = w < 480, fs = small ? 11 : 12;
    const pad = { l: small ? 46 : 58, r: 14, t: 14, b: small ? 34 : 40 };
    const X0 = pad.l, X1 = w - pad.r, Y0 = h - pad.b, Y1 = pad.t;
    const tx = opts.xlog ? Math.log10 : (v) => v, ty = opts.ylog ? Math.log10 : (v) => v;
    const [xa, xb] = opts.x.map(tx), [ya, yb] = opts.y.map(ty);
    const sx = (v) => X0 + (tx(v) - xa) / (xb - xa) * (X1 - X0);
    const sy = (v) => Y0 - (ty(v) - ya) / (yb - ya) * (Y0 - Y1);
    const grid = css('--grid'), muted = css('--muted'), ink = css('--ink'), sans = css('--sans'), mono = css('--mono');
    c.font = `${fs}px ${mono}`; c.lineWidth = 1;
    const ticks = (a, b, log) => {
      if (log) { const out = []; for (let e = Math.ceil(a); e <= Math.floor(b); e++) out.push(Math.pow(10, e)); return out; }
      const span = b - a, raw = span / (small ? 4 : 6), mag = Math.pow(10, Math.floor(Math.log10(raw)));
      const step = [1, 2, 2.5, 5, 10].map((s) => s * mag).find((s) => s >= raw);
      const out = []; for (let v = Math.ceil(a / step) * step; v <= b + step * 1e-9; v += step) out.push(+v.toPrecision(12)); return out;
    };
    const xf = opts.xfmt || ((v) => String(+v.toPrecision(4))), yf = opts.yfmt || ((v) => String(+v.toPrecision(4)));
    c.strokeStyle = grid; c.fillStyle = muted;
    c.textAlign = 'center'; c.textBaseline = 'top';
    ticks(xa, xb, opts.xlog).forEach((v) => { const X = sx(v); c.beginPath(); c.moveTo(X, Y0); c.lineTo(X, Y1); c.stroke(); c.fillText(xf(v), X, Y0 + 5); });
    c.textAlign = 'right'; c.textBaseline = 'middle';
    ticks(ya, yb, opts.ylog).forEach((v) => { const Y = sy(v); c.beginPath(); c.moveTo(X0, Y); c.lineTo(X1, Y); c.stroke(); c.fillText(yf(v), X0 - 6, Y); });
    c.strokeStyle = muted; c.strokeRect(X0, Y1, X1 - X0, Y0 - Y1);
    c.font = `${fs}px ${sans}`; c.fillStyle = muted;
    if (opts.xlabel) { c.textAlign = 'right'; c.textBaseline = 'bottom'; c.fillText(opts.xlabel, X1, h - 2); }
    if (opts.ylabel) { c.textAlign = 'left'; c.textBaseline = 'top'; c.fillText(opts.ylabel, X0 + 6, Y1 + 4); }
    c.save(); c.beginPath(); c.rect(X0, Y1, X1 - X0, Y0 - Y1); c.clip();
    (opts.bands || []).forEach((b) => { c.fillStyle = b.color; c.fillRect(X0, sy(b.y1), X1 - X0, sy(b.y0) - sy(b.y1)); });
    (opts.xbands || []).forEach((b) => { c.fillStyle = b.color; c.fillRect(sx(b.x0), Y1, sx(b.x1) - sx(b.x0), Y0 - Y1); });
    const line = (pts, color, width, dash) => {
      c.strokeStyle = color; c.lineWidth = width || 2; c.setLineDash(dash || []); c.beginPath();
      pts.forEach(([X, Y], i) => (i ? c.lineTo(X, Y) : c.moveTo(X, Y))); c.stroke(); c.setLineDash([]);
    };
    (opts.hlines || []).forEach((l) => line([[X0, sy(l.y)], [X1, sy(l.y)]], l.color || muted, 1, l.dash || [5, 4]));
    (opts.vlines || []).forEach((l) => line([[sx(l.x), Y0], [sx(l.x), Y1]], l.color || muted, 1, l.dash || [5, 4]));
    (opts.series || []).forEach((s) => line(s.x.map((v, i) => [sx(v), sy(s.y[i])]), s.color, s.width, s.dash));
    c.restore();
    c.font = `${fs}px ${sans}`;
    (opts.hlines || []).forEach((l) => { if (l.label) { c.fillStyle = l.color || muted; c.textAlign = 'right'; c.textBaseline = 'bottom'; c.fillText(l.label, X1 - 4, sy(l.y) - 2); } });
    (opts.vlines || []).forEach((l) => { if (l.label) { c.fillStyle = l.color || muted; c.textAlign = 'left'; c.textBaseline = 'top'; c.fillText(l.label, sx(l.x) + 4, Y1 + 18); } });
    (opts.points || []).forEach((p) => {
      const X = sx(p.x), Y = sy(p.y);
      c.fillStyle = p.color || ink; c.beginPath(); c.arc(X, Y, p.r || 4.5, 0, 2 * Math.PI); c.fill();
      if (p.label) { c.fillStyle = p.color || ink; c.textAlign = X > (X0 + X1) / 2 ? 'right' : 'left'; c.textBaseline = 'bottom'; c.fillText(p.label, X + (X > (X0 + X1) / 2 ? -8 : 8), Y - 6); }
    });
    return { sx, sy, X0, X1, Y0, Y1, c, w, h };
  };

  Lab.css = css; Lab.$ = $;
  root.WQLab = Lab;
})(typeof window !== 'undefined' ? window : this);
