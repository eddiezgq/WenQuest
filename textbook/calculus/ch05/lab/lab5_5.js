// 实验 5.5 二分法求根（配 5.5 节）。一步步二分，看区间怎样收缩、需要多少步；
// 三种失效：两端同号（(x − 1)²）、多个根（x³ − x）、间断点（tan x）；“机器人”场景：关节阶跃响应首次到达 95% 的时刻。
WQ.lab({
  title: ["实验 5.5 二分法求根：每一步区间减半", "Lab 5.5 Bisection: halve the interval at every step"],
  goal: ["用零点定理确认有根，再一步步二分，体会“步数可以事先算出”；看看连续性、变号这两个条件不满足时二分法会怎样。",
         "Confirm a root with the zero theorem, then bisect step by step and see that the number of steps can be computed in advance; find out what happens when continuity or the sign change fails."],
  scenes: [
    { id: "fn", name: ["函数的根", "Roots of functions"], hide: ["z"],
      problem: { title: ["夹住一个根，然后每次砍掉一半", "Trap a root, then cut the interval in half again and again"],
                 text: ["两端函数值异号、函数连续，零点定理保证区间里有根。每二分一次，根所在的区间缩短一半。要把 √2 夹到 10⁻⁶ 以内，需要多少步？",
                        "If the end values differ in sign and the function is continuous, the zero theorem guarantees a root. Each halving shortens the interval containing it by half. How many steps to trap √2 within 10⁻⁶?"] } },
    { id: "rise", robot: true, name: ["关节到达 95% 的时间", "Joint time to 95%"], hide: ["f"],
      problem: { title: ["机器人问题：关节转到目标的 95% 用了多久", "Robot problem: how long until the joint reaches 95% of the target"],
                 text: ["关节阶跃响应 q(t) = 1 − e^(−ζωₙt)(cos ω_d t + ζ/√(1 − ζ²)·sin ω_d t)，ωₙ = 10 rad/s。在 [0, 峰值时刻] 上 q 单调递增。用二分法求 q(t) = 0.95 的 t。",
                        "Joint step response q(t) = 1 − e^(−ζωₙt)(cos ω_d t + ζ/√(1 − ζ²)·sin ω_d t), ωₙ = 10 rad/s, increasing on [0, peak time]. Use bisection to solve q(t) = 0.95."] } },
  ],
  params: [
    { id: "f", name: ["函数：1 x² − 2，2 cos x − x，3 x³ − x，4 tan x，5 (x − 1)²", "Function: 1 x² − 2, 2 cos x − x, 3 x³ − x, 4 tan x, 5 (x − 1)²"], min: 1, max: 5, step: 1, value: 1, digits: 0 },
    { id: "z", name: ["阻尼比 ζ", "Damping ratio ζ"], min: 0.3, max: 0.9, step: 0.05, value: 0.6, digits: 2 },
    { id: "lt", name: ["lg 容差", "lg tolerance"], min: -12, max: -1, step: 1, value: -3, digits: 0 },
  ],
  buttons: [{ id: "step", name: ["二分一步", "One step"], primary: true }, { id: "run", name: ["算到容差", "Run to tolerance"] }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["当前区间", "current interval"], color: "#1f77b4" }, { name: ["中点", "midpoints"], color: "#d62728" }],
  tasks: [
    { id: "sqrt2", text: ["选 x² − 2，容差取 10⁻⁶，算到容差。用了几步？与 ⌈log₂(2/10⁻⁶)⌉ 比较。", "Choose x² − 2 with tolerance 10⁻⁶ and run. How many steps? Compare with ⌈log₂(2/10⁻⁶)⌉."],
      demo: { scene: "fn", set: { f: 1, lt: -6 }, press: ["run"], wait: 1 } },
    { id: "nosign", text: ["选 (x − 1)²，按“二分一步”，看看为什么二分法无从下手。", "Choose (x − 1)² and press 'One step': why can bisection not start?"],
      demo: { scene: "fn", set: { f: 5 }, press: ["step"], wait: 1 } },
    { id: "tan", text: ["选 tan x（区间 [1, 2]），容差取 10⁻⁹，算到容差，看 f(m) 的值：二分法找到的是根吗？", "Choose tan x on [1, 2] with tolerance 10⁻⁹ and run. Look at f(m): is that a root?"],
      demo: { scene: "fn", set: { f: 4, lt: -9 }, press: ["run"], wait: 1 } },
    { id: "rise", robot: true, text: ["在“关节到达 95% 的时间”中取 ζ = 0.6、容差 10⁻⁴ s，求出到达 95% 的时刻。", "In 'Joint time to 95%' take ζ = 0.6 and tolerance 10⁻⁴ s, and find the time to reach 95%."],
      demo: { scene: "rise", set: { z: 0.6, lt: -4 }, press: ["run"], wait: 1 } },
  ],
  think: ["二分法每一步只用到函数值的符号。这是它的长处还是短处？若知道函数值的大小（比如 f(a) = −0.01，f(b) = 5），能不能更聪明地选分点？",
          "Bisection only uses the signs of function values. Is that a strength or a weakness? If you know the sizes (say f(a) = −0.01, f(b) = 5), could you choose a smarter point?"],

  F(api) {
    if (api.scene === "rise") {
      const z = api.p.z, wn = 10, wd = wn * Math.sqrt(1 - z * z), tp = Math.PI / wd;
      const q = (t) => 1 - Math.exp(-z * wn * t) * (Math.cos(wd * t) + z / Math.sqrt(1 - z * z) * Math.sin(wd * t));
      return { f: (t) => q(t) - 0.95, g: q, A: 0, B: tp, name: "q(t) − 0.95", xmax: 1.0, ymin: -0.1, ymax: 1.3, gy: 0.95, unit: " s" };
    }
    switch (api.p.f) {
      case 1: return { f: (x) => x * x - 2, A: 0, B: 2, name: "x² − 2", ymin: -2.5, ymax: 2.5 };
      case 2: return { f: (x) => Math.cos(x) - x, A: 0, B: 1, name: "cos x − x", ymin: -0.6, ymax: 1.1 };
      case 3: return { f: (x) => x * x * x - x, A: -2, B: 1.5, name: "x³ − x", ymin: -3, ymax: 2 };
      case 4: return { f: Math.tan, A: 1, B: 2, name: "tan x", ymin: -10, ymax: 10 };
      default: return { f: (x) => (x - 1) * (x - 1), A: 0, B: 3, name: "(x − 1)²", ymin: -0.5, ymax: 4.2 };
    }
  },
  reset(api, s) {
    const F = this.F(api);
    Object.assign(s, { a: F.A, b: F.B, fa: F.f(F.A), fb: F.f(F.B), k: 0, mids: [], msg: "" });
    s.nosign = (s.fa > 0) === (s.fb > 0);   // 比较符号，不相乘（5.5.3 节）
  },
  one(F, s) {
    const m = (s.a + s.b) / 2;
    if (m === s.a || m === s.b) { s.msg = "ulp"; return false; }
    const fm = F.f(m);
    s.mids.push(m); s.k++; s.m = m; s.fm = fm;
    if (fm === 0) { s.a = s.b = m; return false; }
    if ((fm > 0) === (s.fa > 0)) { s.a = m; s.fa = fm; } else { s.b = m; s.fb = fm; }
    return true;
  },
  action(id, api, s) {
    const F = this.F(api), tol = Math.pow(10, api.p.lt);
    if (s.nosign) { s.msg = "nosign"; if (api.scene === "fn" && api.p.f === 5) api.done("nosign"); return; }
    if (id === "step") { if (s.b - s.a > 0) this.one(F, s); }
    if (id === "run") { let n = 0; while (s.b - s.a > tol && n < 200 && this.one(F, s)) n++; }
    const w = s.b - s.a;
    if (api.scene === "fn" && api.p.f === 1 && api.p.lt === -6 && w <= 1e-6) api.done("sqrt2");
    if (api.scene === "fn" && api.p.f === 4 && api.p.lt <= -9 && w <= 1e-6 && Math.abs(s.fm) > 1e3) api.done("tan");
    if (api.scene === "rise" && Math.abs(api.p.z - 0.6) < 0.01 && w <= 1e-4) api.done("rise");
  },
  readouts(api, s) {
    const F = this.F(api), tol = Math.pow(10, api.p.lt), w = s.b - s.a, u = F.unit || "";
    const rows = [[["函数", "Function"], F.name + api.T("，初始区间 [", ", initial interval [") + api.fmt(F.A, 3) + ", " + api.fmt(F.B, 3) + "]" + u],
                  [["两端的符号", "End signs"], s.nosign ? api.T("同号：零点定理不适用，无法二分", "same sign: the zero theorem does not apply, cannot bisect")
                                                         : api.T("异号：区间内有根（若函数连续）", "opposite: a root inside (if continuous)")],
                  [["已二分的步数 k", "Steps k"], String(s.k)],
                  [["当前区间", "Current interval"], "[" + s.a.toPrecision(12) + ", " + s.b.toPrecision(12) + "]"],
                  [["区间宽度（误差上界）", "Width (error bound)"], w.toExponential(3) + u],
                  [["达到容差所需步数 ⌈log₂(初始宽度/容差)⌉", "Steps needed ⌈log₂(initial width/tol)⌉"], String(Math.max(0, Math.ceil(Math.log2((F.B - F.A) / tol))))]];
    if (s.k) rows.push([["最后一个中点 m 与 f(m)", "Last midpoint m and f(m)"], s.m.toPrecision(12) + u + "，f(m) = " + s.fm.toExponential(3)]);
    if (s.msg === "ulp") rows.push([["提示", "Note"], api.T("区间的两端已是相邻的浮点数，再也分不开了", "the ends are adjacent floating-point numbers; no further halving is possible")]);
    return rows;
  },
  draw(api, s) {
    const F = this.F(api), w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), ink = api.css("--ink"), mu = api.css("--muted");
    const lo = F.A - 0.08 * (F.B - F.A), hi = (F.xmax ?? F.B) + 0.08 * (F.B - F.A);
    const G = api.graph({ x: 60, y: 24, w: w - 80, h: h - 74, xmin: lo, xmax: hi, ymin: F.ymin, ymax: F.ymax,
      xlabel: api.scene === "rise" ? "t / s" : "x", ylabel: api.scene === "rise" ? "q(t)" : F.name });
    G.axes();
    const ctx = api.ctx;
    ctx.fillStyle = "rgba(31,119,180,0.15)";
    ctx.fillRect(G.X(s.a), G.o.y, Math.max(1, G.X(s.b) - G.X(s.a)), G.o.h);
    if (api.scene === "rise") { G.fn(F.g, ink, 2, null, 0, hi); G.hline(F.gy, red); G.vline(F.B, mu); }
    else G.fn(F.f, ink, 2);
    G.vline(F.A, mu); G.vline(F.B, mu);
    const y0 = api.scene === "rise" ? F.gy : 0;
    G.dots(s.mids.map((m) => [m, y0]), red, 3);
    G.seg(s.a, y0, s.b, y0, blue, 5);
  },
});
