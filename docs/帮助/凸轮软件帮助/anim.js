// 问渠凸轮帮助的动画与小计算器（第 90 轮）。数据在 DATA 里（build.py 由计算核心真算）；小计算器调软件自己的接口（DATA.api）。
(function () {
  const css = (k) => getComputedStyle(document.documentElement).getPropertyValue(k).trim();
  const C = () => ({ ink: css("--ink"), muted: css("--muted"), line: css("--line"), soft: css("--soft"), paper: css("--paper"),
    accent: css("--accent"), accent2: css("--accent2"), ok: css("--ok"), bad: css("--bad"), warn: css("--warn"), gold: css("--gold") });
  const FONT = '"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",system-ui,sans-serif';
  function canvas(el, h) {
    const cv = document.createElement("canvas");
    el.appendChild(cv);
    const fit = () => { const w = el.clientWidth - 28; cv.width = w * devicePixelRatio; cv.height = h * devicePixelRatio; cv.style.height = h + "px"; };
    fit();
    addEventListener("resize", fit);
    const g = cv.getContext("2d");
    return { cv, g, W: () => cv.width / devicePixelRatio, H: h, begin() { g.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0); g.clearRect(0, 0, cv.width, cv.height); } };
  }
  function bar(el, html) { const b = document.createElement("div"); b.className = "bar"; b.innerHTML = html; el.appendChild(b); return b; }
  function cap(el, text) { const c = document.createElement("div"); c.className = "cap"; c.innerHTML = text; el.appendChild(c); return c; }
  function visible(el, fn) { // 滚到眼前才开始动，省电
    let on = false;
    new IntersectionObserver((es) => { on = es[0].isIntersecting; }).observe(el);
    let last = 0;
    (function loop(t) { if (on && !document.hidden) { fn(t, t - (last || t)); } last = t; requestAnimationFrame(loop); })(0);
  }
  function txt(g, s, x, y, col, size, align, bold) { g.fillStyle = col; g.font = `${bold ? "600 " : ""}${size || 13}px ${FONT}`; g.textAlign = align || "left"; g.fillText(s, x, y); }
  function arrow(g, x0, y0, x1, y1, col, w) {
    g.strokeStyle = col; g.fillStyle = col; g.lineWidth = w || 2; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke();
    const a = Math.atan2(y1 - y0, x1 - x0), s = 8 + (w || 2);
    g.beginPath(); g.moveTo(x1, y1); g.lineTo(x1 - s * Math.cos(a - 0.4), y1 - s * Math.sin(a - 0.4)); g.lineTo(x1 - s * Math.cos(a + 0.4), y1 - s * Math.sin(a + 0.4)); g.closePath(); g.fill();
  }
  function rbox(g, x, y, w, h, r, fill, stroke, lw) { g.beginPath(); g.roundRect(x, y, w, h, r); if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = lw || 1.5; g.stroke(); } }
  function jet(t) { // 0→1 蓝→青→绿→黄→红（应力云图常用色带）
    t = Math.max(0, Math.min(1, t));
    const r = Math.max(0, Math.min(1, 1.5 - Math.abs(4 * t - 3))), g = Math.max(0, Math.min(1, 1.5 - Math.abs(4 * t - 2))), b = Math.max(0, Math.min(1, 1.5 - Math.abs(4 * t - 1)));
    return `rgb(${(r * 255) | 0},${(g * 255) | 0},${(b * 255) | 0})`;
  }
  function plot(g, x, y, w, h, series, opt) { // 简单曲线图：series = [{y:[], col, label}]
    const c = C();
    const all = series.flatMap((s) => s.y).filter((v) => isFinite(v));
    let lo = Math.min(...all, opt.zero ? 0 : Infinity), hi = Math.max(...all);
    if (hi - lo < 1e-9) hi = lo + 1;
    rbox(g, x, y, w, h, 6, c.paper, c.line, 1);
    const X = (i, n) => x + 8 + ((w - 16) * i) / (n - 1), Y = (v) => y + h - 18 - ((h - 34) * (v - lo)) / (hi - lo);
    if (lo < 0 && hi > 0) { g.strokeStyle = c.line; g.lineWidth = 1; g.beginPath(); g.moveTo(x + 6, Y(0)); g.lineTo(x + w - 6, Y(0)); g.stroke(); }
    series.forEach((s) => {
      if (!s.y.length) return;
      g.strokeStyle = s.col; g.lineWidth = s.w || 2; g.setLineDash(s.dash || []); g.beginPath();
      s.y.forEach((v, i) => (i ? g.lineTo(X(i, s.y.length), Y(v)) : g.moveTo(X(i, s.y.length), Y(v)))); g.stroke(); g.setLineDash([]);
    });
    txt(g, opt.title || "", x + 10, y + 16, c.muted, 12);
    txt(g, hi.toFixed(opt.dec ?? 1), x + w - 8, y + 16, c.muted, 11, "right");
    txt(g, lo.toFixed(opt.dec ?? 1), x + w - 8, y + h - 6, c.muted, 11, "right");
    let lx = x + 10;
    series.forEach((s) => { if (!s.label) return; g.fillStyle = s.col; g.fillRect(lx, y + h - 13, 14, 3); txt(g, s.label, lx + 18, y + h - 6, c.muted, 11); lx += 30 + g.measureText(s.label).width; });
    return { X, Y };
  }

  const A = {}, CALC = {};
  const API = () => DATA.api;            // "../api/" beside the software; "" in the offline FreeCAD copy
  const ONLINE_HELP = "https://wenquestrobotics.com/cam/help/";
  function offline(el) { // the offline copy has no API: say so and point online
    if (API()) return false;
    const d = document.createElement("div"); d.className = "sum warn";
    d.innerHTML = `这是离线帮助：这个计算器要调软件的计算接口，打开<a href="${ONLINE_HELP}">在线帮助</a>就能用。`;
    el.appendChild(d); return true;
  }
  function slider(el, rows, vals, on) { // rows: [key, 名称, lo, hi, step, unit]
    rows.forEach(([k, zh, lo, hi, st, u]) => {
      const r = document.createElement("div"); r.className = "row";
      r.innerHTML = `<span>${zh}</span><input type="range" min="${lo}" max="${hi}" step="${st}" value="${vals[k]}"><b>${vals[k]} ${u}</b>`;
      r.querySelector("input").oninput = (e) => { vals[k] = +e.target.value; r.querySelector("b").textContent = `${vals[k]} ${u}`; on(); };
      el.appendChild(r);
    });
  }
  function seg(el, label, opts, val, on) { // a row of buttons
    const b = bar(el, `<span>${label}</span>` + opts.map(([k, t]) => `<button data-k="${k}"${k === val ? ' class="on"' : ""}>${t}</button>`).join(""));
    b.querySelectorAll("button").forEach((x) => (x.onclick = () => { b.querySelectorAll("button").forEach((y) => y.classList.toggle("on", y === x)); on(x.dataset.k); }));
    return b;
  }
  const fx = (x, k = 1) => (x == null || !isFinite(x) ? "—" : Number(x).toFixed(k));

  // ---------- 系统结构：设计 → 制造 → 测量 → 补偿的闭环 ----------
  A.arch = (el) => {
    const N = [
      { k: "web", x: 0.04, y: 0.04, w: 0.28, t: "网页版", s: "设计 · 制造 · 测量 · 系统", d: "浏览器打开就用，不登录也能算。单个凸轮三页、凸轮系统三页；项目存浏览器、文件或云端。" },
      { k: "fc", x: 0.68, y: 0.04, w: 0.28, t: "FreeCAD 工作台", s: "精确实体 · 装配 · 工作图", d: "“问渠 → 凸轮”：同一个计算核心，建盘形、圆柱、弧面凸轮的精确实体，凸轮系统按时序装配，出 STEP、程序、工作图。" },
      { k: "core", x: 0.33, y: 0.25, w: 0.34, t: "计算核心 camkit", s: "纯 Python · 不联网 · 不调 AI", d: "运动程序与运动规律、廓线、压力角与曲率、接触与跳离、制造程序与读回仿真、测量与补偿、凸轮系统与设计搜索、STEP。每个模块带标准题。" },
      { k: "mfg", x: 0.04, y: 0.5, w: 0.28, t: "机床", s: "磨削 X–C · 铣削 · 四轴", d: "加工程序 .nc：先读回仿真、确认不过切、偏差在弦高公差内，再上机床。机床参数是示例，按本厂设备改。" },
      { k: "meas", x: 0.36, y: 0.72, w: 0.28, t: "测量", s: "升程表 · 廓线点", d: "测出的升程或廓线贴回来：对相位、分阶次、算加速度误差和最高能跑的转速。" },
      { k: "comp", x: 0.68, y: 0.5, w: 0.28, t: "补偿", s: "选阶次 → 新程序", d: "把选中阶次的误差反向加到运动程序上，按同一把刀、同一台机床重新出程序，并预测剩下的误差。" },
      { k: "cae", x: 0.68, y: 0.8, w: 0.28, t: "CAE（凸轮系统）", s: "有限元 · 疲劳 · 多体动力学", d: "换刀臂强度、固有频率、疲劳，整机 MuJoCo 与解析结果对照；在数字工厂计算服务排队。" },
    ];
    const E = [["web", "core"], ["fc", "core"], ["core", "mfg"], ["mfg", "meas"], ["meas", "comp"], ["comp", "core"], ["core", "cae"]];
    const S = canvas(el, 400), info = cap(el, "点任意一块看它做什么。小圆点沿着“设计 → 机床 → 测量 → 补偿 → 再出程序”的闭环走。");
    let sel = null;
    const box = (n) => { const W = S.W(); return { x: n.x * W, y: n.y * 380 + 6, w: n.w * W, h: 54 }; };
    const mid = (n) => { const b = box(n); return [b.x + b.w / 2, b.y + b.h / 2]; };
    S.cv.addEventListener("click", (e) => {
      const r = S.cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
      sel = N.find((n) => { const b = box(n); return x > b.x && x < b.x + b.w && y > b.y && y < b.y + b.h; }) || null;
      info.innerHTML = sel ? `<b>${sel.t}</b>：${sel.d}` : "点任意一块看它做什么。";
    });
    visible(el, (t) => {
      const c = C(), g = S.g; S.begin();
      E.forEach(([a, b], i) => {
        const [x0, y0] = mid(N.find((n) => n.k === a)), [x1, y1] = mid(N.find((n) => n.k === b));
        g.strokeStyle = c.line; g.lineWidth = 2; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke();
        const p = (t / 2400 + i * 0.37) % 1;
        g.fillStyle = i % 2 ? c.accent2 : c.accent; g.beginPath(); g.arc(x0 + (x1 - x0) * p, y0 + (y1 - y0) * p, 4, 0, 7); g.fill();
      });
      const small = S.W() < 560;
      N.forEach((n) => {
        const b = box(n), on = sel === n;
        rbox(g, b.x, b.y, b.w, b.h, 10, on ? c.paper : c.soft, on ? c.accent : c.line, on ? 2.5 : 1.5);
        txt(g, n.t, b.x + b.w / 2, b.y + (small ? 32 : 23), c.ink, small ? 12.5 : 14.5, "center", true);
        if (!small) txt(g, n.s, b.x + b.w / 2, b.y + 42, c.muted, 11.5, "center");
      });
    });
  };

  // ---------- 运动规律：位移、速度、加速度（计算核心算的曲线） ----------
  CALC.laws = (el) => {
    const L = DATA.laws, keys = Object.keys(L);
    el.innerHTML = "<b>运动规律对比</b><div class='cap'>升程和转角都归一化（0 到 1）；曲线和系数由计算核心算出。点上面的按钮换规律，可以同时比两种。</div>";
    let a = "mod_sine", b = "cycloidal";
    seg(el, "规律一", keys.map((k) => [k, L[k].zh]), a, (k) => { a = k; draw(); });
    seg(el, "规律二", keys.map((k) => [k, L[k].zh]), b, (k) => { b = k; draw(); });
    const S = canvas(el, 300), out = document.createElement("div"); out.className = "sum ok"; el.appendChild(out);
    function draw() {
      const c = C(), g = S.g; S.begin();
      const W = S.W(), w = (W - 20) / 3;
      [["s", "位移"], ["v", "速度"], ["a", "加速度"]].forEach(([k, t], i) => {
        plot(g, 5 + i * (w + 5), 6, w, 280, [{ y: L[a][k], col: c.accent, label: L[a].zh }, { y: L[b][k], col: c.accent2, label: L[b].zh, dash: [5, 3] }], { title: t, dec: 2, zero: true });
      });
      const imp = (x) => (x.jump === "velocity" ? "刚性冲击" : x.jump === "acceleration" ? "柔性冲击" : "无冲击");
      out.innerHTML = [a, b].map((k) => `<b>${L[k].zh}</b>：Cv ${L[k].Cv}　Ca ${L[k].Ca}　Cj ${L[k].Cj}　（从静止起升：${imp(L[k])}）`).join("<br>");
    }
    draw();
  };

  // ---------- 小计算器：跳离（调软件接口，送布抬牙凸轮示例） ----------
  CALC.jump = (el) => {
    el.innerHTML = "<b>小计算器：转速、弹簧与跳离</b><div class='cap'>用“送布抬牙凸轮”示例（虚构），调的就是软件的计算接口。</div>";
    if (offline(el)) return;
    const v = { rpm: 5000, k: 3, preload: 6 };
    slider(el, [["rpm", "转速", 1000, 7000, 100, "r/min"], ["k", "弹簧刚度", 1, 10, 0.5, "N/mm"], ["preload", "弹簧预压量", 0, 20, 1, "mm"]], v, go);
    const sum = document.createElement("div"); sum.className = "sum"; el.appendChild(sum);
    let base = null, tm = null;
    function go() { clearTimeout(tm); tm = setTimeout(run, 200); }
    async function run() {
      try {
        if (!base) base = await (await fetch(API() + "examples/sewing-feed")).json();
        const p = JSON.parse(JSON.stringify(base));
        p.loads.rpm = v.rpm; p.loads.k = v.k; p.loads.preload = v.preload;
        const r = await fetch(API() + "analyse", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(p) });
        const R = await r.json();
        if (!r.ok) { sum.className = "sum warn"; sum.textContent = (R.detail && (R.detail.zh || R.detail.en)) || "算不出来"; return; }
        const j = R.checks.find((c) => c.id === "jump");
        sum.className = "sum " + (j.status === "fail" ? "bad" : "ok");
        sum.innerHTML = `不跳离的最高转速 <b>${fx(j.value, 0)} r/min</b>；现在 ${v.rpm} r/min：${j.status === "fail" ? "<b>会跳离</b>" : "不跳离"}`;
      } catch (e) { sum.className = "sum warn"; sum.textContent = "连不上计算接口（" + e.message + "）"; }
    }
    run();
  };

  // ---------- 小计算器：许用压力角 → 最小基圆（调软件接口） ----------
  CALC.minrb = (el) => {
    el.innerHTML = "<b>小计算器：许用压力角与最小基圆</b><div class='cap'>用挑线槽凸轮示例（虚构），调软件的“求最小基圆”接口。</div>";
    if (offline(el)) return;
    const v = { phi: 45 };
    slider(el, [["phi", "许用压力角（推程、回程）", 20, 60, 1, "°"]], v, go);
    const sum = document.createElement("div"); sum.className = "sum ok"; el.appendChild(sum);
    let base = null, tm = null;
    function go() { clearTimeout(tm); tm = setTimeout(run, 200); }
    async function run() {
      try {
        if (!base) base = await (await fetch(API() + "examples/sewing-takeup-groove")).json();
        const p = JSON.parse(JSON.stringify(base));
        p.limits = { ...(p.limits || {}), phi_rise_deg: v.phi, phi_return_deg: v.phi };
        const r = await fetch(API() + "min-base-radius", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(p) });
        const R = await r.json();
        if (!r.ok) { sum.className = "sum warn"; sum.textContent = (R.detail && (R.detail.zh || R.detail.en)) || "算不出来"; return; }
        const what = { phi_rise: "推程压力角", phi_return: "回程压力角", undercut: "根切", rho_min: "最小曲率半径" };
        sum.innerHTML = `最小基圆半径 <b>${fx(R.rb, 2)} mm</b>（示例用 ${base.mechanism.rb} mm），卡在：${(R.binding || []).map((x) => what[x] || x).join("、")}`;
      } catch (e) { sum.className = "sum warn"; sum.textContent = "连不上计算接口（" + e.message + "）"; }
    }
    run();
  };

  // ---------- 测量 → 分阶次 → 补偿（案例一的合成测量数据，计算核心算的结果） ----------
  A.comp = (el) => {
    const D0 = DATA.comp;
    let show = "before";
    seg(el, "看", [["before", "补偿前"], ["after", "补偿 1–6 阶后（预测）"]], show, (k) => { show = k; });
    const S = canvas(el, 280);
    cap(el, `上：误差曲线（${D0.unit}，凸轮转一圈）；下：各阶谐波幅值。红 = 1 阶（偏心、装夹），黄 = 2–6 阶（热处理变形等），蓝 = 高阶（机床、颤振）。数据是演示用的合成测量，由计算核心分析和补偿。`);
    visible(el, () => {
      const c = C(), g = S.g; S.begin();
      const W = S.W();
      const e = show === "before" ? D0.e : D0.rest;
      plot(g, 5, 6, W - 10, 130, [{ y: e, col: show === "before" ? c.bad : c.ok }], { title: "误差", dec: 1 });
      const A_ = show === "before" ? D0.before : D0.after, am = Math.max(...D0.before, 1e-9);
      rbox(g, 5, 144, W - 10, 130, 6, c.paper, c.line, 1);
      const bw = (W - 40) / A_.length;
      A_.forEach((x, i) => {
        const k = D0.k[i], h = (x / am) * 100;
        g.fillStyle = k === 1 ? c.bad : k <= 6 ? c.warn : c.accent;
        g.fillRect(20 + i * bw, 264 - h, Math.max(2, bw - 3), h);
        if (i % 4 === 0) txt(g, String(k), 20 + i * bw + bw / 2, 272, c.muted, 10, "center");
      });
      txt(g, "阶次", W - 14, 160, c.muted, 11, "right");
    });
  };

  document.querySelectorAll(".anim").forEach((el) => { const f = A[el.dataset.anim]; if (f) f(el); });
  document.querySelectorAll(".calc").forEach((el) => { const f = CALC[el.dataset.calc]; if (f) f(el); });
  if (location.hash) { const t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) setTimeout(() => t.scrollIntoView(), 60); }
})();
