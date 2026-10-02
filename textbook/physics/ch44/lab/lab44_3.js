// 实验 44.3 薛定谔方程求解台（配 44.3、44.4、44.6 节；谐振子在“自己画势能”场景里作为例子）。用工具包的 api.qm.levels（有限差分 + 三对角本征值，
// 与程序 _qm.levels 同一算法）数值求解一维定态薛定谔方程。长度 nm，能量 eV。
// “自己画势能”场景：在势能图上按住拖动，就把那一段的势能画成指针所在的高度；画的势能放在闭包里，重置时不丢。
const draw44 = { N: 240, X: 10, V: null, preset: "", touched: false, last: null };
// 画的势能 0–10 nm、0–2 eV；preset 记下最近一次用的例子；touched：改过参数或按过按钮之后才判定任务（打开页面时不算完成）
const C44 = 0.0380998212;

function grid44(api) {   // 当前场景的格点、势能、有效质量
  const p = api.p, sc = api.scene;
  let x0, x1, N = 700, mr = 1, Vf;
  if (sc === "box") { x0 = 0; x1 = p.L; N = Math.round(150 * p.L + 300); mr = p.mr; Vf = () => 0; }
  else if (sc === "qw") { const h = p.L / 2; x0 = -h - 30; x1 = h + 30; N = 1200; mr = p.mr; Vf = (x) => (Math.abs(x) < h ? 0 : p.V0); }
  else if (sc === "double") { const w = 5, b = p.b, h = w + b / 2; x0 = -h - 20; x1 = h + 20; N = 1200; mr = 0.067;
    Vf = (x) => (Math.abs(x) < b / 2 || Math.abs(x) > h ? 0.3 : 0); }
  else { x0 = 0; x1 = draw44.X; N = draw44.N; mr = p.mr; }
  const dx = (x1 - x0) / (N + 1), x = new Float64Array(N), V = new Float64Array(N);
  for (let i = 0; i < N; i++) { x[i] = x0 + (i + 1) * dx; V[i] = sc === "draw" ? draw44.V[i] : Vf(x[i]); }
  return { x0, x1, N, dx, x, V, mr };
}

function solve44(api, s) {
  if (!draw44.V) draw44.V = new Float64Array(draw44.N).fill(0);
  const g = grid44(api), r = api.qm.levels(g.V, g.dx, 6, g.mr);
  let vmax = -Infinity; for (let i = 0; i < g.N; i++) vmax = Math.max(vmax, g.V[i]);
  const top = Math.min(g.V[0], g.V[g.N - 1]);       // 区间两端的势能：低于它的是束缚态（有限深势阱、双势阱）
  s.g = g; s.E = r.E; s.psi = r.psi; s.vmax = vmax;
  s.bound = api.scene === "qw" || api.scene === "double" ? r.E.filter((e) => e < top - 1e-6).length : null;
}

WQ.lab({
  title: ["实验 44.3 薛定谔方程求解台", "Lab 44.3 A Schrödinger-equation bench"],
  goal: ["在浏览器里数值求解一维定态薛定谔方程，看能级和波函数怎样随势能的形状、宽度、深度和粒子质量变化。",
         "Solve the one-dimensional time-independent Schrödinger equation in the browser and see how levels and wave functions depend on the shape, width and depth of the potential and on the mass."],
  scenes: [
    { id: "box", robot: true, name: ["无限深势阱（FinFET 的硅鳍）", "Infinite well (a FinFET fin)"], hide: ["V0", "b"],
      problem: { title: ["机器人问题：几纳米宽的硅鳍里的电子", "Robot problem: electrons in a fin a few nanometres wide"],
                 text: ["控制器芯片的晶体管鳍宽只有几纳米。电子在宽度方向上的能量还能连续变化吗？", "The fins of the controller's transistors are a few nanometres wide. Can an electron's energy across the fin still vary continuously?"] } },
    { id: "qw", robot: true, name: ["有限深势阱（激光雷达的量子阱激光器）", "Finite well (the LiDAR's quantum-well laser)"], hide: ["b"],
      params: { L: { min: 2, max: 20, step: 0.5, value: 8 }, mr: { value: 0.067 } },
      problem: { title: ["机器人问题：量子阱有几个束缚态", "Robot problem: how many bound states in a quantum well"],
                 text: ["GaAs 量子阱：阱深就是导带阶 0.243 eV，电子有效质量 0.067mₑ。阱宽决定了能级和激光的波长。", "A GaAs quantum well: depth 0.243 eV (the conduction-band offset), effective mass 0.067 mₑ. The width sets the levels and the laser wavelength."] } },
    { id: "double", robot: true, name: ["双势阱（耦合量子阱）", "Double well (coupled quantum wells)"], hide: ["L", "V0", "mr"],
      problem: { title: ["机器人问题：两个靠近的量子阱", "Robot problem: two quantum wells close together"],
                 text: ["两个 5 nm 宽、0.3 eV 深的 GaAs 量子阱，中间隔着宽 b 的势垒。b 变小，最低两个能级怎样变化？", "Two GaAs wells, 5 nm wide and 0.3 eV deep, separated by a barrier of width b. What happens to the two lowest levels as b shrinks?"] } },
    { id: "draw", name: ["自己画势能", "Draw your own potential"], hide: ["L", "V0", "b"],
      problem: { title: ["生活中的例子：分子振动与自己画的势能", "Everyday example: molecular vibration, and potentials of your own"],
                 text: ["在左边的势能图上按住拖动（鼠标或手指），画出任意形状的势能（0–10 nm，0–2 eV），松开后立即求出能级。“清空”把势能恢复为零，“阶梯”“三角阱”“谐振子”给出三个例子；谐振子取 ħω = 0.291 eV，与 CO₂ 分子的振动量子相同（44.6 节）。",
                        "Press and drag on the potential plot (mouse or finger) to draw any potential (0–10 nm, 0–2 eV); the levels appear when you let go. “Clear” resets it to zero; “Steps”, “Triangle” and “Oscillator” are three examples, the oscillator with ħω = 0.291 eV, the vibrational quantum of CO₂ (Section 44.6)."] } },
  ],
  params: [
    { id: "L", name: ["阱宽 L", "Width L"], min: 0.5, max: 10, step: 0.1, value: 1, unit: "nm", digits: 1 },
    { id: "V0", name: ["阱深 V₀", "Depth V₀"], min: 0.05, max: 0.5, step: 0.001, value: 0.243, unit: "eV", digits: 3 },
    { id: "b", name: ["中间势垒宽 b", "Barrier width b"], min: 0.5, max: 8, step: 0.5, value: 1, unit: "nm", digits: 1 },
    { id: "mr", name: ["有效质量 m*/mₑ", "Effective mass m*/mₑ"], min: 0.05, max: 1, step: 0.001, value: 1, digits: 3 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }, { id: "clear", name: ["清空", "Clear"] }, { id: "steps", name: ["阶梯", "Steps"] },
            { id: "tri", name: ["三角阱", "Triangle"] }, { id: "osc", name: ["谐振子 ħω = 0.291 eV", "Oscillator ħω = 0.291 eV"] }],
  legend: [{ color: "var(--muted)", name: ["势能", "potential"] }, { color: "var(--orange)", name: ["能级", "levels"] }, { color: "var(--blue)", name: ["波函数", "wave functions"] }],
  tasks: [
    { id: "box1", robot: true, text: ["无限深势阱：L = 1.0 nm、m*/mₑ = 1，读出最低三个能级，与式 (44.3.1) 比较。", "Infinite well, L = 1.0 nm, m*/mₑ = 1: read the three lowest levels and compare with Eq. (44.3.1)."],
      demo: { scene: "box", set: { L: 1, mr: 1 }, press: [], wait: 1 } },
    { id: "box2", robot: true, text: ["把阱宽加倍到 2.0 nm：E₁ 变为原来的 1/4。", "Double the width to 2.0 nm: E₁ falls to a quarter."],
      demo: { scene: "box", set: { L: 2, mr: 1 }, press: [], wait: 1 } },
    { id: "qw", robot: true, text: ["量子阱：L = 8 nm、V₀ = 0.243 eV、m*/mₑ = 0.067，数一数束缚态；再加宽到出现第三个束缚态（L 就是 44.4 节的阱宽 a）。", "Quantum well: L = 8 nm, V₀ = 0.243 eV, m*/mₑ = 0.067; count the bound states, then widen it until a third appears."],
      demo: { scene: "qw", set: { L: 10, V0: 0.243, mr: 0.067 }, press: [], wait: 1 } },
    { id: "ho", text: ["自己画势能：点“谐振子”（ħω = 0.291 eV，与 CO₂ 的振动量子相同），读出能级，验证等间距、最低能级等于 ħω/2（读数中的 E1 对应 n = 0）。", "Draw: press “Oscillator” (ħω = 0.291 eV, CO₂'s vibrational quantum), read the levels and check they are equally spaced with the lowest equal to ħω/2 (E1 in the readouts is n = 0)."],
      demo: { scene: "draw", set: { mr: 1 }, press: ["osc"], wait: 1 } },
    { id: "split", robot: true, text: ["双势阱：加宽中间势垒，使最低两个能级之差小于 10 meV。", "Double well: widen the barrier until the two lowest levels are less than 10 meV apart."],
      demo: { scene: "double", set: { b: 4 }, press: [], wait: 1 } },
  ],
  think: ["“自己画势能”：画一个左右不对称的双势阱，最低两个态的波函数各集中在哪一边？与对称的双势阱有什么不同？",
          "“Draw”: make an asymmetric double well. Where do the two lowest states sit? How does this differ from a symmetric double well?"],

  reset(api, s) { solve44(api, s); if (draw44.touched) check44(api, s); },
  change(api, s, pid) { draw44.touched = true; },
  action(id, api, s) {
    if (api.scene !== "draw") return;
    const V = draw44.V, N = draw44.N;
    for (let i = 0; i < N; i++) {
      const x = (i + 1) * draw44.X / (N + 1);
      V[i] = id === "steps" ? (x < 3 ? 0 : x < 6 ? 0.3 : 0.8) : id === "tri" ? 0.15 * x
           : id === "osc" ? Math.min(2, 0.291 * 0.291 * (x - 5) * (x - 5) / (4 * C44)) : 0;
    }
    draw44.preset = id; draw44.touched = true;
    solve44(api, s); check44(api, s);
  },
  pointer(kind, px, py, api, s) {
    if (api.scene !== "draw" || !s.P) return;
    const P = s.P, x = (px - P.x) / P.w * draw44.X, v = (P.y + P.h - py) / P.h * 2;
    if (kind !== "up" && x >= -0.2 && x <= draw44.X + 0.2) {
      draw44.preset = "";
      const N = draw44.N, i1 = Math.round(x / draw44.X * (N + 1)) - 1, ww = 3, v1 = Math.max(0, Math.min(2, v));
      // 拖得快时两次事件之间相隔好几个格点：在上一个点与这一点之间按直线补齐
      const prev = kind === "move" && draw44.last ? draw44.last : [i1, v1];
      const n = Math.max(1, Math.abs(i1 - prev[0]));
      for (let j = 0; j <= n; j++) {
        const ic = Math.round(prev[0] + (i1 - prev[0]) * j / n), vc = prev[1] + (v1 - prev[1]) * j / n;
        for (let i = ic - ww; i <= ic + ww; i++) if (i >= 0 && i < N) draw44.V[i] = vc;
      }
      draw44.last = [i1, v1];
    }
    if (kind === "up") draw44.last = null;
    if (kind === "up" || kind === "down") solve44(api, s);
    else s.dirty = true;
  },
  readouts(api, s) {
    const f = api.fmt, mev = api.scene === "qw" || api.scene === "double";
    const rows = (s.E || []).slice(0, s.bound != null ? Math.min(5, s.bound) : 5).map((e, k) => [[`E${k + 1}`, `E${k + 1}`], mev ? f(e * 1000, 1) + " meV" : f(e, 4) + " eV"]);
    if (api.scene === "box") rows.push([["式 (44.3.1) 的 E₁", "E₁ from Eq. (44.3.1)"], f(C44 / api.p.mr * Math.pow(Math.PI / api.p.L, 2), 4) + " eV"]);
    if (s.bound != null) rows.push([["束缚态个数", "Bound states"], String(s.bound)]);
    if (api.scene === "draw" && s.E) rows.push([["E₂ − E₁", "E₂ − E₁"], f(s.E[1] - s.E[0], 4) + " eV"]);
    if (api.scene === "double" && s.E) rows.push([["E₂ − E₁", "E₂ − E₁"], f((s.E[1] - s.E[0]) * 1000, 2) + " meV"]);
    return rows;
  },
  draw(api, s) {
    if (s.dirty) { solve44(api, s); s.dirty = false; }
    const { w, h } = api, css = api.css, g = s.g;
    if (!g) return;
    const draw = api.scene === "draw";
    // 纵轴范围：势能与前几个能级都要看得见
    const nshow = Math.min(5, s.E.length);
    let ytop = draw ? 2 : api.scene === "box" ? s.E[Math.min(3, nshow - 1)] * 1.25 : Math.max(s.vmax > 5 ? 0 : s.vmax, s.E[nshow - 1]) * 1.15;
    if (api.scene === "qw" || api.scene === "double") ytop = Math.max(g.V[0], s.E[0]) * 1.25;
    let xa = g.x0, xb = g.x1;
    if (api.scene === "qw") { xa = -Math.max(8, api.p.L); xb = -xa; }
    if (api.scene === "double") { xa = -(5 + api.p.b / 2 + 6); xb = -xa; }
    const P = { x: w * 0.07, y: 16, w: w * 0.88, h: h - 50 };
    s.P = P;
    const Vpts = [];
    for (let i = 0; i < g.N; i += 2) if (g.x[i] >= xa && g.x[i] <= xb) Vpts.push([g.x[i], Math.min(g.V[i], ytop * 1.5)]);
    const Q = api.plot(P.x, P.y, P.w, P.h, [{ pts: Vpts, color: css("--muted") }],
                       { xmin: xa, xmax: xb, ymin: api.scene === "draw" ? 0 : -0.05 * ytop, ymax: ytop, xlabel: "x / nm", ylabel: "E / eV" });
    if (api.scene === "box") { api.line(Q.X(0), Q.Y(-0.05 * ytop), Q.X(0), Q.Y(ytop), css("--muted"), 4); api.line(Q.X(api.p.L), Q.Y(-0.05 * ytop), Q.X(api.p.L), Q.Y(ytop), css("--muted"), 4); }
    // 能级与波函数（画在各自能级的高度上；在势能曲线以上的部分才是“束缚”的）
    const gap = nshow > 1 ? (s.E[1] - s.E[0]) : s.E[0];
    for (let k = 0; k < nshow; k++) {
      const E = s.E[k];
      if (E > ytop || (s.bound != null && k >= s.bound)) break;      // 阱口以上的属于连续谱，不画
      api.line(Q.X(xa), Q.Y(E), Q.X(xb), Q.Y(E), css("--orange"), 1, [5, 4]);
      let mx = 0; for (let i = 0; i < g.N; i++) mx = Math.max(mx, Math.abs(s.psi[k][i]));
      const pts = [];
      for (let i = 0; i < g.N; i += 2) if (g.x[i] >= xa && g.x[i] <= xb) pts.push([g.x[i], E + 0.4 * gap * s.psi[k][i] / mx]);
      api.ctx.strokeStyle = css("--blue"); api.ctx.lineWidth = 1.8; api.ctx.beginPath();
      pts.forEach((p, i) => (i ? api.ctx.lineTo(Q.X(p[0]), Q.Y(p[1])) : api.ctx.moveTo(Q.X(p[0]), Q.Y(p[1])))); api.ctx.stroke();
      api.label(`n=${k + 1}`, Q.X(xb) - 4, Q.Y(E) - 4, css("--muted"), 11, "right");
    }
    if (draw) api.label(api.T("在这里按住拖动画势能", "press and drag here to draw"), P.x + 8, P.y + 28, css("--muted"), 12);
  },
});

function check44(api, s) {
  const p = api.p, sc = api.scene;
  if (!s.E) return;
  if (sc === "box" && p.mr === 1 && Math.abs(p.L - 1) < 1e-9) api.done("box1");
  if (sc === "box" && p.mr === 1 && Math.abs(p.L - 2) < 1e-9 && Math.abs(s.E[0] * 4 - C44 * Math.PI * Math.PI) < 1e-3) api.done("box2");
  if (sc === "qw" && Math.abs(p.V0 - 0.243) < 1e-9 && Math.abs(p.mr - 0.067) < 1e-9 && s.bound >= 3) api.done("qw");
  if (sc === "draw" && draw44.preset === "osc" && p.mr === 1 && Math.abs((s.E[2] - s.E[1]) - (s.E[1] - s.E[0])) < 0.01 * 0.291) api.done("ho");
  if (sc === "double" && (s.E[1] - s.E[0]) < 0.010) api.done("split");
}
