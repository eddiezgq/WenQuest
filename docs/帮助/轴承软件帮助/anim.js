// 问渠轴承帮助的动画与小计算器（第 90 轮）。数据在 DATA 里（build.py 由计算核心真算）；小计算器调软件自己的接口（DATA.api）。
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
  const ONLINE_HELP = "https://wenquestrobotics.com/bearing/help/";
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

  // ---------- 系统结构 ----------
  A.arch = (el) => {
    const N = [
      { k: "web", x: 0.04, y: 0.04, w: 0.28, t: "网页版", s: "设计校核 · 合套 · SPC · 工艺", d: "浏览器打开就用，不登录也能算。四个页面：设计校核、合套选配、检测与 SPC、工艺。项目存在浏览器里、文件里或云端。" },
      { k: "fc", x: 0.68, y: 0.04, w: 0.28, t: "FreeCAD 工作台", s: "精确实体 · 工作图 · 工序简图", d: "“问渠 → 轴承”：同一张表单、同一个计算核心，在本机建精确实体、查干涉、出 A3 工作图和工序简图。" },
      { k: "core", x: 0.33, y: 0.25, w: 0.34, t: "计算核心 bearingkit", s: "纯 Python · 不联网 · 不调 AI", d: "几何、赫兹接触、载荷分布、成对与预紧、温度对游隙、柔性轴承、交叉滚子、薄壁轴承、合套、尺寸链、SPC、工艺倒推、剖面与 STEP。每个模块带标准题。" },
      { k: "svc", x: 0.04, y: 0.48, w: 0.3, t: "计算服务", s: "…/bearing/api/", d: "网页版的接口：校核、零件、合套、SPC、工艺、尺寸链、产品库核对。和网页版同一个网址，国内版、美国版都一样。" },
      { k: "gw", x: 0.66, y: 0.48, w: 0.3, t: "问渠网关", s: "账号 · 企业授权 · 云端 · 产品库 · AI", d: "认人、按单位隔离云端项目和产品库、调大模型（国内已备案模型，美国 Claude）。AI 的数先过程序检查。" },
      { k: "out", x: 0.04, y: 0.8, w: 0.3, t: "出件", s: "计算书 · STEP · DXF · 工序卡", d: "计算书（打印 / PDF）、STEP 整套与单件、DXF 截面、工序卡、配套清单 CSV。" },
      { k: "shop", x: 0.66, y: 0.8, w: 0.3, t: "车间数据", s: "实测沟径 · 圆度 · 检测值", d: "合套选配用实测沟径和钢球分组；检测与 SPC 用圆度仪轮廓和检测数据。数据由企业贴入，不进代码。" },
    ];
    const E = [["web", "core"], ["fc", "core"], ["core", "svc"], ["svc", "web"], ["web", "gw"], ["svc", "out"], ["fc", "out"], ["shop", "svc"]];
    const S = canvas(el, 400), info = cap(el, "点任意一块看它做什么。小圆点是一次“改参数 → 重算 → 出件”的数据。");
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

  // ---------- AI 起草 → 程序核对 → 人采用 ----------
  A.aiguard = (el) => {
    const steps = [
      ["一句话", "“减速器输出轴，斜齿轮模数 3、齿数 34，18 kW、960 r/min，跨距 160 mm”"],
      ["AI 起草", "选“减速器齿轮轴”，把句子里的数填进去"],
      ["程序核对", "句子里没有的数一律清空并列出来；不换算、不估计"],
      ["黄格子", "没给的格子（压力角、螺旋角……）标黄，等人补"],
      ["人点“采用”", "这时才放进表单，可以撤销"],
      ["计算核心校核", "合格、不合格、未知——全由程序判"],
    ];
    const S = canvas(el, 230), b = bar(el, '<button>重播</button><span class="cap">AI 只起草；数先过程序检查，人点“采用”才进项目，判定全由计算核心做。</span>');
    let t0 = performance.now();
    b.querySelector("button").onclick = () => (t0 = performance.now());
    function wrap(g, s, x, y, w, lh, col) { g.fillStyle = col; let line = ""; for (const ch of s) { if (g.measureText(line + ch).width > w) { g.fillText(line, x, y); y += lh; line = ch; } else line += ch; } g.fillText(line, x, y); }
    visible(el, (t) => {
      const c = C(), g = S.g; S.begin();
      const W = S.W(), k = Math.min(steps.length, Math.floor((t - t0) / 1300) + 1), cols = W < 640 ? 2 : 3, bw = (W - 16 * (cols + 1)) / cols;
      const bh = W < 640 ? 60 : 96;
      steps.forEach((s, i) => {
        const cx = 16 + (i % cols) * (bw + 16), cy = 10 + Math.floor(i / cols) * (bh + 12);
        const on = i < k, warn = i === 2 || i === 3;
        rbox(g, cx, cy, bw, bh, 10, on ? c.paper : c.soft, on ? (warn ? c.warn : i === 5 ? c.ok : c.accent) : c.line, on ? 2.2 : 1);
        txt(g, `${i + 1} ${s[0]}`, cx + 10, cy + 20, on ? c.ink : c.muted, 14, "left", true);
        if (W >= 640) { g.save(); g.font = `12px ${FONT}`; wrap(g, s[1], cx + 10, cy + 42, bw - 20, 17, on ? c.muted : c.line); g.restore(); }
      });
    });
  };

  // ---------- 小计算器：游隙 → 接触角与轴向游隙（与 tolerance.py 同一组公式） ----------
  CALC.clearance = (el) => {
    const d = DATA.dg;
    el.innerHTML = "<b>小计算器：径向游隙与接触角</b><div class='cap'>页内计算，公式与软件相同。</div>";
    const v = { Pd: 15, fi: d.fi, fo: d.fo, Dw: d.Dw };
    slider(el, [["Pd", "径向游隙 Pd", 0, 60, 1, "µm"], ["fi", "内沟曲率系数 fi", 0.505, 0.58, 0.005, ""], ["fo", "外沟曲率系数 fo", 0.505, 0.58, 0.005, ""]], v, draw);
    const S = canvas(el, 230), out = document.createElement("div"); out.className = "sum ok"; el.appendChild(out);
    function draw() {
      const c = C(), g = S.g; S.begin();
      const A_ = (v.fi + v.fo - 1) * v.Dw, Pd = v.Pd / 1000;
      const ca = 1 - Pd / (2 * A_), a0 = Math.acos(Math.max(-1, Math.min(1, ca)));
      const Ga = 2 * Math.sqrt(Math.max(A_ * A_ - (A_ - Pd / 2) ** 2, 0));
      out.innerHTML = `A = (fi + fo − 1)·Dw = ${fx(A_, 4)} mm　自由接触角 α₀ = <b>${fx(a0 * 180 / Math.PI, 2)}°</b>　轴向游隙 Ga = <b>${fx(Ga * 1000, 0)} µm</b>（约为径向游隙的 ${Pd > 0 ? fx(Ga / Pd, 1) : "—"} 倍）`;
      // groove section: ball pushed to the contact angle, both groove arcs
      const W = S.W(), s = 150 / v.Dw, cx = W / 2, cy = 115, K = 8;   // the gaps between ball and groove drawn 8 times larger
      const ri = v.Dw / 2 + K * (v.fi * v.Dw - v.Dw / 2), ro = v.Dw / 2 + K * (v.fo * v.Dw - v.Dw / 2), n = [Math.sin(a0), Math.cos(a0)];
      txt(g, "间隙放大 8 倍画", W - 12, S.H - 12, c.muted, 11.5, "right");
      const ci = [cx + (ri - v.Dw / 2) * n[0] * s, cy - (ri - v.Dw / 2) * n[1] * s];
      const co = [cx - (ro - v.Dw / 2) * n[0] * s, cy + (ro - v.Dw / 2) * n[1] * s];
      g.lineWidth = 3; g.strokeStyle = c.accent; g.beginPath(); g.arc(ci[0], ci[1], ri * s, Math.PI * 0.2, Math.PI * 0.8); g.stroke();
      g.strokeStyle = c.accent2; g.beginPath(); g.arc(co[0], co[1], ro * s, -Math.PI * 0.8, -Math.PI * 0.2); g.stroke();
      g.fillStyle = c.soft; g.strokeStyle = c.ink; g.lineWidth = 1.5; g.beginPath(); g.arc(cx, cy, v.Dw / 2 * s, 0, 7); g.fill(); g.stroke();
      g.setLineDash([5, 4]); g.strokeStyle = c.muted; g.beginPath(); g.moveTo(cx - n[0] * 90, cy + n[1] * 90); g.lineTo(cx + n[0] * 90, cy - n[1] * 90); g.stroke(); g.setLineDash([]);
      txt(g, "外圈沟道（内侧）", 12, 22, c.accent, 12); txt(g, "内圈沟道", 12, S.H - 12, c.accent2, 12);
      txt(g, `α₀ ${fx(a0 * 180 / Math.PI, 1)}°`, cx + n[0] * 95 + 6, cy - n[1] * 95, c.muted, 12);
    }
    draw();
  };

  // ---------- 小计算器：深沟球示例的载荷分布（调软件的计算接口） ----------
  CALC.loads = (el) => {
    el.innerHTML = "<b>小计算器：径向力、轴向力、游隙 → 每个钢球的载荷</b><div class='cap'>用深沟球示例（虚构），调的就是软件的计算接口，结果和软件里一模一样。</div>";
    if (offline(el)) return;
    const v = { Fr: 2500, Fa: 400, Pd: 15 };
    slider(el, [["Fr", "径向力 Fr", 0, 6000, 100, "N"], ["Fa", "轴向力 Fa", 0, 2000, 50, "N"], ["Pd", "初始径向游隙", 0, 60, 1, "µm"]], v, go);
    const S = canvas(el, 250), sum = document.createElement("div"); sum.className = "sum"; el.appendChild(sum);
    let base = null, tm = null, R = null;
    function go() { clearTimeout(tm); tm = setTimeout(run, 200); }
    async function run() {
      try {
        if (!base) base = await (await fetch(API() + "examples/demo-deep-groove")).json();
        const p = JSON.parse(JSON.stringify(base));
        p.loads.Fr = v.Fr; p.loads.Fa = v.Fa; p.inner.Pd = v.Pd / 1000;
        const r = await fetch(API() + "analyse", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(p) });
        R = await r.json();
        if (!r.ok) { sum.className = "sum warn"; sum.textContent = (R.detail && (R.detail.zh || R.detail.en)) || "算不出来"; R = null; draw(); return; }
        const ck = Object.fromEntries(R.checks.map((c) => [c.id, c]));
        const bad = R.checks.filter((c) => c.status === "fail");
        sum.className = "sum " + (bad.length ? "bad" : "ok");
        sum.innerHTML = `最重钢球 <b>${fx(ck.qmax.value, 0)} N</b>，${ck.loaded.value} 个受载；内圈最大接触应力 <b>${fx(ck.p_inner.value, 0)} MPa</b>（示例许用 ${fx(ck.p_inner.limit, 0)}）` +
          (bad.length ? `；不合格：${bad.map((c) => c.zh).join("、")}` : "；静强度合格");
        draw();
      } catch (e) { sum.className = "sum warn"; sum.textContent = "连不上计算接口（" + e.message + "）"; }
    }
    function draw() {
      const c = C(), g = S.g; S.begin();
      if (!R || !R.balls) return;
      const W = S.W(), cx = W / 2, cy = 125, Rr = 70, Q = R.balls.Q, qm = Math.max(...Q, 1);
      g.strokeStyle = c.line; g.lineWidth = 1; g.beginPath(); g.arc(cx, cy, Rr, 0, 7); g.stroke();
      R.balls.psi_deg.forEach((d, j) => {
        const a = (d * Math.PI) / 180, x = cx + Rr * Math.sin(a), y = cy + Rr * Math.cos(a), w = Q[j] / qm;
        g.fillStyle = Q[j] > 0 ? c.accent : c.soft; g.globalAlpha = Q[j] > 0 ? 0.35 + 0.65 * w : 1;
        g.beginPath(); g.arc(x, y, 9, 0, 7); g.fill(); g.globalAlpha = 1; g.strokeStyle = c.muted; g.stroke();
        if (Q[j] > 0) { g.strokeStyle = c.accent2; g.lineWidth = 3; g.beginPath(); g.moveTo(cx + (Rr + 14) * Math.sin(a), cy + (Rr + 14) * Math.cos(a)); g.lineTo(cx + (Rr + 14 + 36 * w) * Math.sin(a), cy + (Rr + 14 + 36 * w) * Math.cos(a)); g.stroke(); }
      });
      arrow(g, cx, cy - 20, cx, cy + 24, c.bad, 2); txt(g, "Fr", cx + 8, cy - 8, c.bad, 12);
    }
    run();
  };

  // ---------- 小计算器：圆锥成对的温度（与 taper_thermal.py 同一组公式） ----------
  CALC.taperheat = (el) => {
    const tp = DATA.tp;
    el.innerHTML = "<b>小计算器：冷态调的游隙，热了还剩多少</b><div class='cap'>页内计算，公式与软件相同；以案例二的轴承为例（外圈滚道直径 62.2 mm、接触角 15°），轴承钢线膨胀系数取示例值 11.5×10⁻⁶/°C，调整时 20 °C。</div>";
    const v = { s: 160, set: 20, Ti: 50, To: 45, Ts: 50, Th: 40 };
    let arr = "DF", ah = 10.5;
    seg(el, "安装", [["DF", "面对面 DF"], ["DB", "背对背 DB"]], arr, (k) => { arr = k; draw(); });
    seg(el, "轴承座材料（示例值）", [["11.5", "钢 11.5"], ["10.5", "铸铁 10.5"], ["23", "铝 23"]], "10.5", (k) => { ah = +k; draw(); });
    slider(el, [["set", "调整值（冷态）", -30, 80, 1, "µm"], ["s", "两列距离", 30, 400, 5, "mm"], ["Ti", "内圈温度", 20, 90, 1, "°C"], ["To", "外圈温度", 20, 90, 1, "°C"],
      ["Ts", "轴温度", 20, 90, 1, "°C"], ["Th", "轴承座温度", 20, 90, 1, "°C"]], v, draw);
    const S = canvas(el, 120), out = document.createElement("div"); out.className = "sum"; el.appendChild(out);
    function draw() {
      const ar = 11.5e-6, a = (15 * Math.PI) / 180, d_o = 54 + 8.5 * Math.cos(a);
      const rad = -(d_o / Math.tan(a)) * ar * ((v.Ti - 20) - (v.To - 20)) * 1000;
      const ax = (arr === "DB" ? 1 : -1) * v.s * (ar * (v.Ts - 20) - ah * 1e-6 * (v.Th - 20)) * 1000;
      const work = v.set + rad + ax;
      out.className = "sum " + (work < 0 ? "warn" : "ok");
      out.innerHTML = `调整值 ${fx(v.set)} µm + 内外圈温差 ${fx(rad)} µm + 轴与座轴向伸长 ${fx(ax)} µm = 工作时 <b>${fx(work)} µm</b>` + (work < 0 ? "（变成预紧）" : "") +
        (arr === "DB" ? `　背对背锥顶重合距离 ${fx(d_o / Math.tan(a), 0)} mm` : "");
      const c = C(), g = S.g; S.begin();
      const W = S.W(), lo = Math.min(0, v.set, work, v.set + rad) - 10, hi = Math.max(0, v.set, work, v.set + rad) + 10, X = (x) => 20 + ((x - lo) / (hi - lo)) * (W - 40);
      g.strokeStyle = c.line; g.beginPath(); g.moveTo(X(0), 10); g.lineTo(X(0), 110); g.stroke(); txt(g, "0", X(0), 118, c.muted, 11, "center");
      const bars = [["调整值", 0, v.set, c.accent], ["温差", v.set, v.set + rad, c.warn], ["轴向伸长", v.set + rad, work, c.accent2]];
      bars.forEach(([t, x0, x1, col], i) => { const y = 14 + i * 28; rbox(g, Math.min(X(x0), X(x1)), y, Math.max(2, Math.abs(X(x1) - X(x0))), 18, 4, col); txt(g, t, Math.max(X(x0), X(x1)) + 6, y + 13, c.muted, 11.5); });
      g.strokeStyle = work < 0 ? c.bad : c.ok; g.lineWidth = 2.5; g.beginPath(); g.moveTo(X(work), 8); g.lineTo(X(work), 100); g.stroke();
    }
    draw();
  };

  // ---------- 小计算器：四点接触的桃形沟（与 thin.py 同一套几何） ----------
  CALC.gothic = (el) => {
    el.innerHTML = "<b>小计算器：四点接触的桃形沟</b><div class='cap'>页内计算，几何与软件相同（钢球 5 mm）。两段圆弧的中心偏在中线两侧，钢球沿两条对角线接触。</div>";
    const v = { a: 30, f: 0.53, Gr: 10 };
    slider(el, [["a", "接触角 α₀", 15, 45, 1, "°"], ["f", "沟曲率系数 f", 0.505, 0.58, 0.005, ""], ["Gr", "径向游隙", -20, 40, 1, "µm"]], v, draw);
    const S = canvas(el, 250), out = document.createElement("div"); out.className = "sum ok"; el.appendChild(out);
    function draw() {
      const Dw = 5, r = v.f * Dw, a0 = r - Dw / 2, al = (v.a * Math.PI) / 180, A_ = 2 * a0, Gr = v.Gr / 1000;
      const zoff = a0 * Math.sin(al), mid = Math.asin(Math.min(zoff / r, 1)) * 180 / Math.PI;
      const ga = Gr >= 0 ? 2 * (Math.sqrt(Math.max(A_ * A_ - (A_ * Math.cos(al) - Gr / 2) ** 2, 0)) - A_ * Math.sin(al)) : null;
      out.innerHTML = `圆弧中心偏离中线 ±${fx(zoff * 1000, 0)} µm，两段圆弧在中线处相接的角度 ${fx(mid, 1)}°；` +
        (ga != null ? `空载轴向游隙 <b>${fx(ga * 1000, 0)} µm</b>（径向游隙 ${v.Gr} µm）` : `径向游隙为负：<b>预紧</b>，两条对角线都压紧`);
      const c = C(), g = S.g; S.begin();
      const W = S.W(), s = 32, cx = W / 2, cy = 125;
      // inner groove (below the ball): arcs centred above the ball at ±zoff; outer groove (above): arcs centred below
      const arc = (zc, rc, rad, from, to, col) => { g.strokeStyle = col; g.lineWidth = 3; g.beginPath(); g.arc(cx + zc * s, cy - rc * s, rad * s, from, to); g.stroke(); };
      const K = 8, a0k = K * a0, rk = Dw / 2 + a0k, zk = a0k * Math.sin(al);   // the gaps drawn 8 times larger
      const ci = a0k * Math.cos(al), co = a0k * Math.cos(al) + (K * Gr) / 2;
      arc(zk, ci, rk, Math.PI * 0.5, Math.PI * 0.88, c.accent2); arc(-zk, ci, rk, Math.PI * 0.12, Math.PI * 0.5, c.accent2);
      arc(-zk, -co, rk, -Math.PI * 0.5, -Math.PI * 0.12, c.accent); arc(zk, -co, rk, -Math.PI * 0.88, -Math.PI * 0.5, c.accent);
      txt(g, "沟道与钢球之间的间隙放大 8 倍画", W - 12, S.H - 12, c.muted, 11.5, "right");
      g.fillStyle = c.soft; g.strokeStyle = c.ink; g.lineWidth = 1.5; g.beginPath(); g.arc(cx, cy, (Dw / 2) * s, 0, 7); g.fill(); g.stroke();
      g.setLineDash([5, 4]); g.strokeStyle = c.muted; g.lineWidth = 1;
      [1, -1].forEach((sg) => { g.beginPath(); g.moveTo(cx - sg * 110 * Math.sin(al), cy + 110 * Math.cos(al)); g.lineTo(cx + sg * 110 * Math.sin(al), cy - 110 * Math.cos(al)); g.stroke(); });
      g.setLineDash([]);
      txt(g, "外圈桃形沟", 12, 22, c.accent, 12); txt(g, "内圈桃形沟", 12, S.H - 12, c.accent2, 12);
      txt(g, `对角线 ±${v.a}°`, cx + 115 * Math.sin(al) + 6, cy - 110 * Math.cos(al) + 4, c.muted, 12);
    }
    draw();
  };

  // ---------- 小计算器：游隙尺寸链（调软件的计算接口） ----------
  CALC.tolmc = (el) => {
    el.innerHTML = "<b>小计算器：游隙尺寸链（蒙特卡洛）</b><div class='cap'>名义尺寸取深沟球示例（虚构）；偏差是演示数，按企业的填。调软件的计算接口。</div>";
    if (offline(el)) return;
    const d = DATA.dg, v = { ring: 4, ball: 0.5, rad: 10 };
    let dist = "normal";
    slider(el, [["ring", "沟底直径偏差 ±", 0, 12, 0.5, "µm"], ["ball", "钢球直径偏差 ±", 0, 3, 0.25, "µm"], ["rad", "沟曲率半径偏差 ±", 0, 30, 1, "µm"]], v, go);
    seg(el, "分布", [["normal", "正态（±3σ）"], ["uniform", "均匀"]], dist, (k) => { dist = k; go(); });
    const S = canvas(el, 170), sum = document.createElement("div"); sum.className = "sum ok"; el.appendChild(sum);
    let tm = null;
    function go() { clearTimeout(tm); tm = setTimeout(run, 250); }
    async function run() {
      const e = (x) => ({ es: x / 1000, ei: -x / 1000 });
      const spec = { di: { nom: d.di, ...e(v.ring) }, do: { nom: d.do, ...e(v.ring) }, Dw: { nom: d.Dw, ...e(v.ball) }, ri: { nom: d.fi * d.Dw, ...e(v.rad) }, ro: { nom: d.fo * d.Dw, ...e(v.rad) } };
      try {
        const r = await fetch(API() + "tolerance", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ spec, n: 100000, dist, target: { Pd: { min: 0.010, max: 0.024 } } }) });
        const R = await r.json();
        if (!r.ok) { sum.className = "sum warn"; sum.textContent = (R.detail && (R.detail.zh || R.detail.en)) || "算不出来"; return; }
        const mc = R.montecarlo.Pd, ex = R.extremes.Pd, st = R.statistical.Pd;
        sum.className = "sum " + (mc.outside > 0.0027 ? "warn" : "ok");
        sum.innerHTML = `径向游隙 µm：极值法 ${fx(ex.min * 1000)}–${fx(ex.max * 1000)}；统计法 ${fx(st.lo * 1000)}–${fx(st.hi * 1000)}；蒙特卡洛 ${fx(mc.p_lo * 1000)}–${fx(mc.p_hi * 1000)}；要求 10–24 µm 时超出 <b>${fx(mc.outside * 100, 2)}%</b>`;
        const c = C(), g = S.g; S.begin();
        const W = S.W(), h = mc.hist, ed = mc.edges, hm = Math.max(...h), x0 = ed[0], x1 = ed[ed.length - 1];
        const lo = Math.min(x0, ex.min, 0.010), hi = Math.max(x1, ex.max, 0.024), X = (x) => 16 + ((x - lo) / (hi - lo)) * (W - 32);
        h.forEach((n, i) => { const xa = X(ed[i]), xb = X(ed[i + 1]), y = 140 - (n / hm) * 120; g.fillStyle = (ed[i] < 0.010 || ed[i + 1] > 0.024) ? c.warn : c.accent; g.fillRect(xa, y, Math.max(1, xb - xa - 1), 140 - y); });
        [[0.010, "10"], [0.024, "24"]].forEach(([x, t]) => { g.strokeStyle = c.bad; g.setLineDash([4, 3]); g.beginPath(); g.moveTo(X(x), 10); g.lineTo(X(x), 140); g.stroke(); g.setLineDash([]); txt(g, t + " µm", X(x), 158, c.bad, 11, "center"); });
        g.strokeStyle = c.muted; g.lineWidth = 2; g.beginPath(); g.moveTo(X(ex.min), 146); g.lineTo(X(ex.max), 146); g.stroke(); txt(g, "极值法范围", X(ex.max) + 4, 150, c.muted, 11);
      } catch (e2) { sum.className = "sum warn"; sum.textContent = "连不上计算接口（" + e2.message + "）"; }
    }
    run();
  };

  // ---------- 预紧量：四点接触薄壁轴承（案例三，计算核心真算的数据） ----------
  A.preload = (el) => {
    const cv = DATA.thin_curve, rings = DATA.thin_rings, Z = DATA.thin_Z;
    let pick = "-12";
    seg(el, "径向游隙", [["10", "+10 µm"], ["-4", "−4 µm"], ["-12", "−12 µm（示例）"]], pick, (k) => { pick = k; });
    const S = canvas(el, 300);
    cap(el, "左：每个钢球两条对角线的接触载荷（橙向外 = 对角线 +，蓝向内 = 对角线 −；淡的是脱开）。右：预紧量曲线——倾覆刚度和最大接触应力随径向游隙怎么变，竖线是左边选的游隙。数据由计算核心算出。");
    visible(el, () => {
      const c = C(), g = S.g; S.begin();
      const W = S.W(), half = W < 620 ? W : W * 0.42, cx = half / 2, cy = 140, R0 = 78, RM = 46;
      const rr = rings[pick], qm = Math.max(...rings["-12"].plus, ...rings["-12"].minus, ...rr.plus, ...rr.minus, 1);
      g.strokeStyle = c.line; g.lineWidth = 1; g.beginPath(); g.arc(cx, cy, R0, 0, 7); g.stroke();
      for (let j = 0; j < Z; j++) {
        const a = (2 * Math.PI * j) / Z;
        [[rr.plus[j], 1, c.accent2], [rr.minus[j], -1, c.accent]].forEach(([q, sg, col]) => {
          const L = (q / qm) * RM; g.strokeStyle = col; g.globalAlpha = q > 0 ? 1 : 0.2; g.lineWidth = 2.5;
          g.beginPath(); g.moveTo(cx + R0 * Math.cos(a), cy - R0 * Math.sin(a)); g.lineTo(cx + (R0 + sg * Math.max(L, 3)) * Math.cos(a), cy - (R0 + sg * Math.max(L, 3)) * Math.sin(a)); g.stroke(); g.globalAlpha = 1;
        });
      }
      const off = rr.plus.filter((q) => q <= 0).length + rr.minus.filter((q) => q <= 0).length;
      txt(g, off ? `${off} 处脱开` : "全部保持接触", cx, cy + 4, off ? c.bad : c.ok, 13, "center", true);
      if (W >= 620) {
        const x = half + 10, w = W - half - 20;
        const ys = cv.e_um, k = ys.indexOf(+pick);
        const P1 = plot(g, x, 8, w, 128, [{ y: cv.k_tilt, col: c.accent }], { title: "倾覆刚度 N·m/mrad", dec: 0 });
        const P2 = plot(g, x, 146, w, 128, [{ y: cv.p_max, col: c.accent2 }], { title: "最大接触应力 MPa", dec: 0 });
        [P1, P2].forEach((P, i) => { if (k >= 0) { g.strokeStyle = c.muted; g.setLineDash([4, 3]); g.beginPath(); g.moveTo(P.X(k, ys.length), 10 + i * 138); g.lineTo(P.X(k, ys.length), 134 + i * 138); g.stroke(); g.setLineDash([]); } });
        txt(g, `${ys[0]} µm`, x + 8, 290 - 6, c.muted, 11); txt(g, `${ys[ys.length - 1]} µm`, x + w - 8, 290 - 6, c.muted, 11, "right");
      }
    });
  };

  document.querySelectorAll(".anim").forEach((el) => { const f = A[el.dataset.anim]; if (f) f(el); });
  document.querySelectorAll(".calc").forEach((el) => { const f = CALC[el.dataset.calc]; if (f) f(el); });
  if (location.hash) { const t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) setTimeout(() => t.scrollIntoView(), 60); }
})();
