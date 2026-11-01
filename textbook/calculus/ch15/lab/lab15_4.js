// 实验 15.4 数值积分的误差与运算量（配 15.1–15.4 节）。“机器人”场景：夹爪碰撞时 1 ms 级的冲击脉冲，比较均匀步长的梯形公式
// 与自适应辛普森求冲量的误差和求值次数；“收敛阶”场景：几个被积函数上梯形、辛普森、高斯的误差随求值次数的变化（双对数）。
WQ.lab({
  title: ["实验 15.4 数值积分的误差与运算量", "Lab 15.4 Error versus work in numerical integration"],
  goal: ["看清数值积分的两个要点：方法的阶决定误差随运算量下降的快慢；被积函数有很窄的尖峰时，均匀步长要很小，自适应方法把点用在要紧的地方，但容差太松也会漏掉尖峰。",
         "See two essentials of numerical integration: the order of a method sets how fast the error falls with work; when the integrand has a narrow spike, uniform steps must be tiny, while adaptive methods put points where they matter, though too loose a tolerance can miss the spike."],
  scenes: [
    { id: "impact", robot: true, name: ["夹爪碰撞冲量", "Gripper impact impulse"], hide: ["f", "n"],
      problem: { title: ["机器人问题：力传感器记录了 1 秒的接触力，碰撞冲量是多少？", "Robot problem: a force sensor records 1 s of contact force — what is the impact impulse?"],
                 text: ["夹爪碰到工件时，接触力在约 1 ms 内冲到几百牛又回落，随后是逐渐建立的 2 N 夹持力。冲量是力对时间的积分。步长取多大才算得准？自适应方法能省多少次计算？",
                        "When the gripper hits the part, the force spikes to several hundred newtons within about 1 ms, then a 2 N holding force builds up. The impulse is the time integral of force. How small must the step be, and how much work does an adaptive method save?"] } },
    { id: "order", name: ["收敛阶", "Order of convergence"], hide: ["w", "h", "meth", "tol"],
      problem: { title: ["误差随运算量怎样下降？", "How does the error fall with work?"],
                 text: ["双对数坐标中，误差—求值次数是一条直线，斜率就是方法的阶。被积函数不光滑、或者是周期函数时，阶会改变。",
                        "On log–log axes, error versus evaluations is a straight line whose slope is the order. Non-smooth or periodic integrands change the picture."] } },
  ],
  params: [
    { id: "w", name: ["冲击脉冲持续时间", "Pulse duration"], min: 0.2, max: 5, step: 0.1, value: 1, unit: "ms", digits: 1 },
    { id: "meth", name: ["方法：1 均匀梯形，2 自适应辛普森", "Method: 1 uniform trapezoid, 2 adaptive Simpson"], min: 1, max: 2, step: 1, value: 1, digits: 0 },
    { id: "h", name: ["均匀步长", "Uniform step"], min: 0.05, max: 20, step: 0.05, value: 10, unit: "ms", digits: 2 },
    { id: "tol", name: ["自适应容差 10^k 中的 k", "Adaptive tolerance exponent k (10^k)"], min: -8, max: -2, step: 1, value: -5, digits: 0 },
    { id: "f", name: ["被积函数：1 e^(−x²)，2 √x，3 1/(1 + 0.5 cos x)（整周期），4 x³", "Integrand: 1 e^(−x²), 2 √x, 3 1/(1 + 0.5 cos x) (full period), 4 x³"], min: 1, max: 4, step: 1, value: 1, digits: 0 },
    { id: "n", name: ["小区间数（梯形、辛普森）/ 点数（高斯）n", "Subintervals (trapezoid, Simpson) / points (Gauss) n"], min: 2, max: 128, step: 2, value: 8, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["梯形", "trapezoid"], color: "#1f77b4" }, { name: ["辛普森", "Simpson"], color: "#2ca02c" }, { name: ["高斯 / 求值点", "Gauss / evaluation points"], color: "#d62728" }],
  tasks: [
    { id: "miss", robot: true, text: ["脉冲 1 ms，均匀梯形步长 10 ms：误差多大？把步长逐步减小到 1、0.5、0.25、0.1 ms，误差怎样变化？步长要小到多少（与脉冲宽度相比），误差才可靠地小于 1%？完成条件：步长不超过 0.1 ms。", "1 ms pulse, uniform trapezoid with a 10 ms step: how large is the error? Reduce the step to 1, 0.5, 0.25, 0.1 ms: how does the error behave? How small must the step be (compared with the pulse width) for the error to stay reliably below 1%? Completed at a step of 0.1 ms or less."],
      demo: { scene: "impact", set: { w: 1, meth: 1, h: 0.1 }, wait: 1 } },
    { id: "adapt", robot: true, text: ["改用自适应辛普森，容差 10⁻⁵：误差小于 0.01% 时求值多少次？与均匀梯形比较。", "Switch to adaptive Simpson with tolerance 10⁻⁵: how many evaluations for error below 0.01%? Compare with the uniform trapezoid."],
      demo: { scene: "impact", set: { w: 1, meth: 2, tol: -5 }, wait: 1 } },
    { id: "loose", robot: true, text: ["把容差放宽到 10⁻²：自适应方法为什么反而漏掉了脉冲？", "Loosen the tolerance to 10⁻²: why does the adaptive method miss the pulse?"],
      demo: { scene: "impact", set: { w: 1, meth: 2, tol: -2 }, wait: 1 } },
    { id: "sqrt", text: ["选 √x：辛普森的阶还是 4 吗？读出“观测到的阶”。", "Choose √x: is Simpson still fourth order? Read the observed order."],
      demo: { scene: "order", set: { f: 2, n: 32 }, wait: 1 } },
  ],
  think: ["力传感器的采样频率一般是 1 kHz。若碰撞脉冲只有 0.5 ms，传感器的数据还能用来算冲量吗？硬件上和算法上各有什么办法？",
          "Force sensors typically sample at 1 kHz. If the impact lasts only 0.5 ms, can the data still give the impulse? What hardware and algorithmic remedies are there?"],

  T0: 0.4013, TEND: 1.0,
  force(t, w) {
    const t0 = this.T0;
    const hold = 2 * (1 - Math.exp(-Math.max(t - t0, 0) / 0.05));
    const pulse = t >= t0 && t <= t0 + w ? 400 * Math.sin(Math.PI * (t - t0) / w) : 0;
    return hold + pulse;
  },
  exact(w) {
    const T = this.TEND, t0 = this.T0;
    return 2 * ((T - t0) - 0.05 * (1 - Math.exp(-(T - t0) / 0.05))) + 400 * 2 * w / Math.PI;
  },
  trapz(f, a, b, n) { const h = (b - a) / n; let s = 0.5 * (f(a) + f(b)); for (let k = 1; k < n; k++) s += f(a + k * h); return s * h; },
  simpson(f, a, b, n) { if (n % 2) n++; const h = (b - a) / n; let s = f(a) + f(b); for (let k = 1; k < n; k++) s += (k % 2 ? 4 : 2) * f(a + k * h); return s * h / 3; },
  gaussNodes(n) {
    if (this._gn && this._gn[n]) return this._gn[n];
    const xs = [], ws = [];
    for (let i = 1; i <= n; i++) {
      let x = Math.cos(Math.PI * (i - 0.25) / (n + 0.5)), dp = 1;
      for (let it = 0; it < 100; it++) {
        let p0 = 1, p1 = x;
        for (let k = 2; k <= n; k++) { const p2 = ((2 * k - 1) * x * p1 - (k - 1) * p0) / k; p0 = p1; p1 = p2; }
        dp = n * (x * p1 - p0) / (x * x - 1);
        const dx = p1 / dp; x -= dx;
        if (Math.abs(dx) < 1e-15) break;
      }
      xs.push(x); ws.push(2 / ((1 - x * x) * dp * dp));
    }
    this._gn = this._gn || {};
    this._gn[n] = [xs, ws];
    return this._gn[n];
  },
  gauss(f, a, b, n) { const [xs, ws] = this.gaussNodes(n), c = (a + b) / 2, d = (b - a) / 2; let s = 0; for (let i = 0; i < n; i++) s += ws[i] * f(c + d * xs[i]); return d * s; },
  adaptive(f, a, b, tol) {
    const pts = [];
    const F = (x) => { pts.push(x); return f(x); };
    const simp = (a, fa, b, fb) => { const m = (a + b) / 2, fm = F(m); return [m, fm, (b - a) / 6 * (fa + 4 * fm + fb)]; };
    const rec = (a, fa, b, fb, m, fm, whole, tol, d) => {
      const [lm, flm, left] = simp(a, fa, m, fm), [rm, frm, right] = simp(m, fm, b, fb);
      if (d <= 0 || Math.abs(left + right - whole) <= 15 * tol) return left + right + (left + right - whole) / 15;
      return rec(a, fa, m, fm, lm, flm, left, tol / 2, d - 1) + rec(m, fm, b, fb, rm, frm, right, tol / 2, d - 1);
    };
    const fa = F(a), fb = F(b), [m, fm, whole] = simp(a, fa, b, fb);
    return [rec(a, fa, b, fb, m, fm, whole, tol, 40), pts];
  },
  FN(f) {
    return [
      { f: (x) => Math.exp(-x * x), a: 0, b: 1, ex: 0.746824132812427, name: "e^(−x²)" },
      { f: Math.sqrt, a: 0, b: 1, ex: 2 / 3, name: "√x" },
      { f: (x) => 1 / (1 + 0.5 * Math.cos(x)), a: 0, b: 2 * Math.PI, ex: 2 * Math.PI / Math.sqrt(0.75), name: "1/(1 + 0.5 cos x)" },
      { f: (x) => x * x * x, a: 0, b: 1, ex: 0.25, name: "x³" },
    ][f - 1];
  },
  impact(api) {
    const p = api.p, w = p.w / 1000, f = (t) => this.force(t, w), J = this.exact(w);
    if (p.meth === 1) {
      const n = Math.max(1, Math.round(this.TEND / (p.h / 1000))), pts = [];
      for (let k = 0; k <= n; k++) pts.push(k * this.TEND / n);
      return { v: this.trapz(f, 0, this.TEND, n), pts, J };
    }
    const [v, pts] = this.adaptive(f, 0, this.TEND, Math.pow(10, p.tol));
    return { v, pts, J };
  },
  reset() {},
  readouts(api) {
    const p = api.p;
    if (api.scene === "impact") {
      const R = this.impact(api), rel = Math.abs(R.v - R.J) / R.J * 100;
      const w1 = Math.abs(p.w - 1) < 1e-9;
      if (w1 && p.meth === 1 && p.h <= 0.1 + 1e-9 && rel < 1) api.done("miss");
      if (w1 && p.meth === 2 && p.tol === -5 && rel < 0.01) api.done("adapt");
      if (w1 && p.meth === 2 && p.tol === -2 && rel > 5) api.done("loose");
      return [[["方法", "Method"], p.meth === 1 ? api.T("均匀梯形", "uniform trapezoid") : api.T("自适应辛普森", "adaptive Simpson")],
              [["求值次数", "Evaluations"], String(R.pts.length)], [["算得的冲量", "Computed impulse"], R.v.toFixed(5) + " N·s"],
              [["准确冲量", "Exact impulse"], R.J.toFixed(5) + " N·s"], [["其中脉冲部分", "of which the pulse"], (400 * 2 * p.w / 1000 / Math.PI).toFixed(5) + " N·s"],
              [["相对误差", "Relative error"], rel.toPrecision(3) + " %"]];
    }
    const D = this.FN(p.f), n = p.n;
    const et = Math.abs(this.trapz(D.f, D.a, D.b, n) - D.ex), et2 = Math.abs(this.trapz(D.f, D.a, D.b, 2 * n) - D.ex);
    const es = Math.abs(this.simpson(D.f, D.a, D.b, n) - D.ex), es2 = Math.abs(this.simpson(D.f, D.a, D.b, 2 * n) - D.ex);
    const ng = Math.min(n, 20), eg = Math.abs(this.gauss(D.f, D.a, D.b, ng) - D.ex);
    const ord = (e1, e2) => (e1 > 1e-14 && e2 > 1e-14 ? (Math.log(e1 / e2) / Math.LN2).toFixed(2) : "—");
    if (p.f === 2 && n >= 16) api.done("sqrt");
    const fe = (e) => (e < 1e-15 ? "< 1e-15" : e.toExponential(2));
    return [[["被积函数", "Integrand"], D.name], [["梯形误差", "Trapezoid error"], fe(et)], [["梯形观测到的阶", "Trapezoid observed order"], ord(et, et2)],
            [["辛普森误差", "Simpson error"], fe(es)], [["辛普森观测到的阶", "Simpson observed order"], ord(es, es2)],
            [[`高斯 ${ng} 点误差`, `Gauss ${ng}-point error`], fe(eg)]];
  },
  draw(api) {
    const w = api.w, h = api.h, ink = api.css("--ink"), blue = api.css("--blue"), red = api.css("--red"), green = api.css("--green") || "#2ca02c", muted = api.css("--muted");
    const p = api.p;
    if (api.scene === "impact") {
      const R = this.impact(api), ww = p.w / 1000, t0 = this.T0;
      const H = (h - 100) / 2;
      const g1 = api.graph({ x: 70, y: 20, w: w - 90, h: H, xmin: 0, xmax: 1, ymin: -40, ymax: 440, xlabel: "t / s", ylabel: "F / N" });
      g1.axes();
      g1.fn((t) => this.force(t, ww), ink, 1.2);
      const stride = Math.max(1, Math.ceil(R.pts.length / 3000));
      g1.dots(R.pts.filter((_, i) => i % stride === 0).map((t) => [t, -25]), red, 1.5);
      const lo = t0 - 0.002, hi = t0 + ww + 0.002;
      const g2 = api.graph({ x: 70, y: 60 + H, w: w - 90, h: H, xmin: (lo - t0) * 1000, xmax: (hi - t0) * 1000, ymin: -40, ymax: 440, xlabel: api.T("t − t₀ / ms", "t − t₀ / ms"), ylabel: "F / N" });
      g2.axes();
      g2.fn((s) => this.force(t0 + s / 1000, ww), ink, 1.6);
      g2.dots(R.pts.filter((t) => t >= lo && t <= hi).map((t) => [(t - t0) * 1000, this.force(t, ww)]), red, 3);
      return;
    }
    const D = this.FN(p.f), ns = [2, 4, 8, 16, 32, 64, 128];
    const L = (e) => Math.log10(Math.max(e, 1e-16));
    const tr = ns.map((n) => [Math.log10(n + 1), L(Math.abs(this.trapz(D.f, D.a, D.b, n) - D.ex))]);
    const si = ns.map((n) => [Math.log10(n + 1), L(Math.abs(this.simpson(D.f, D.a, D.b, n) - D.ex))]);
    const ga = [2, 3, 4, 6, 8, 12, 16, 20].map((n) => [Math.log10(n), L(Math.abs(this.gauss(D.f, D.a, D.b, n) - D.ex))]);
    const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0.2, xmax: 2.2, ymin: -16, ymax: 0.5, xlabel: api.T("lg 求值次数", "lg evaluations"), ylabel: api.T("lg 误差", "lg error") });
    G.axes();
    G.pts(tr, blue, 2); G.dots(tr, blue, 3);
    G.pts(si, green, 2); G.dots(si, green, 3);
    G.pts(ga, red, 2); G.dots(ga, red, 3);
    G.vline(Math.log10(p.n + 1), muted);
  },
});
