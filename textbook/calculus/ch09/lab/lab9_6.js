// 实验 9.6 泰勒多项式与误差（配 9.5、9.6 节）。改变次数和展开点，看泰勒多项式怎样贴合函数、误差与拉格朗日余项的上界；
// “机器人”场景：AGV 里程计 Δy/(vT) = (1 − cos u)/u 在 u = ωT 很小时，直接公式与泰勒公式在双精度下的相对误差。
WQ.lab({
  title: ["实验 9.6 泰勒多项式与误差", "Lab 9.6 Taylor polynomials and their error"],
  goal: ["看清 n 次泰勒多项式在展开点附近怎样贴合函数，误差为什么不超过拉格朗日余项的上界；体会展开点的选择、收敛范围的限制；用泰勒公式避开相消，给里程计公式选切换阈值。",
         "See how the degree-n Taylor polynomial hugs the function near the expansion point and why the error stays below the Lagrange bound; feel the effect of the expansion point and of the range of convergence; use Taylor's formula to avoid cancellation and choose a switching threshold for the odometry formula."],
  scenes: [
    { id: "fn", name: ["泰勒多项式", "Taylor polynomials"], hide: ["lu", "m"],
      problem: { title: ["用多项式贴合函数：几次够用？展开点放在哪里？", "Fit a function by a polynomial: what degree, and where to expand?"],
                 text: ["Pₙ(x) = Σ f⁽ᵏ⁾(a)(x − a)ᵏ/k!，k = 0, …, n。在探测点 x 处比较 f(x) 与 Pₙ(x)，并与拉格朗日余项的上界 max|f⁽ⁿ⁺¹⁾|·|x − a|ⁿ⁺¹/(n + 1)! 比较。",
                        "Pₙ(x) = Σ f⁽ᵏ⁾(a)(x − a)ᵏ/k!, k = 0, …, n. At the probe x compare f(x) with Pₙ(x) and with the Lagrange bound max|f⁽ⁿ⁺¹⁾|·|x − a|ⁿ⁺¹/(n + 1)!."] } },
    { id: "odo", robot: true, name: ["AGV 里程计：小转角", "AGV odometry: small turns"], hide: ["f", "n", "a", "x"],
      problem: { title: ["机器人问题：ωT 很小时，侧向位移怎样算才准？", "Robot problem: computing the sideways shift accurately when ωT is tiny"],
                 text: ["AGV 在时间 T 内以速度 v、角速度 ω 行驶，侧向位移 Δy = vT·(1 − cos u)/u，u = ωT。u 很小时 1 − cos u 是相近数相减。改用泰勒公式 u/2 − u³/24 + u⁵/720 − ⋯，取几项、u 小于多少时切换？",
                        "An AGV moving with speed v and turn rate ω for time T shifts sideways by Δy = vT·(1 − cos u)/u, u = ωT. For small u, 1 − cos u subtracts nearly equal numbers. Switch to u/2 − u³/24 + u⁵/720 − ⋯: how many terms, and below which u?"] } },
  ],
  params: [
    { id: "f", name: ["函数：1 eˣ，2 sin x，3 cos x，4 ln(1 + x)，5 √(1 + x)", "Function: 1 eˣ, 2 sin x, 3 cos x, 4 ln(1 + x), 5 √(1 + x)"], min: 1, max: 5, step: 1, value: 2, digits: 0 },
    { id: "n", name: ["次数 n", "Degree n"], min: 0, max: 24, step: 1, value: 3, digits: 0 },
    { id: "a", name: ["展开点 a", "Expansion point a"], min: -0.5, max: 5, step: 0.05, value: 0, digits: 2 },
    { id: "x", name: ["探测点 x", "Probe x"], min: -0.9, max: 6, step: 0.005, value: 1.5, digits: 3 },
    { id: "lu", name: ["lg u（u = ωT）", "lg u (u = ωT)"], min: -8, max: 0, step: 0.1, value: -2, digits: 1 },
    { id: "m", name: ["泰勒公式的项数", "Number of Taylor terms"], min: 1, max: 5, step: 1, value: 1, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["函数 / 直接公式", "function / direct formula"], color: "#222222" }, { name: ["泰勒多项式 / 泰勒公式", "Taylor polynomial / formula"], color: "#d62728" }],
  tasks: [
    { id: "sin", text: ["选 sin x，展开点 a = 0，探测点 x = 0.785（约 π/4），找出使误差小于 10⁻¹⁰ 的最小次数。", "Choose sin x, a = 0, x = 0.785 (about π/4): find the smallest degree with error below 10⁻¹⁰."],
      demo: { scene: "fn", set: { f: 2, a: 0, x: 0.785, n: 11 }, wait: 1 } },
    { id: "ln", text: ["选 ln(1 + x)，a = 0，x = 1.5，把次数逐步加到 15 以上：次数越高误差越大，远远超过 1。", "Choose ln(1 + x), a = 0, x = 1.5 and raise the degree step by step past 15: the error grows with the degree, far beyond 1."],
      demo: { scene: "fn", set: { f: 4, a: 0, x: 1.5, n: 16 }, wait: 1 } },
    { id: "exp", text: ["选 eˣ，x = 5，次数不超过 8，展开点与 x 至少相距 0.5，把误差压到 10⁻⁶ 以下（提示：移动展开点）。", "Choose eˣ, x = 5, degree at most 8, expansion point at least 0.5 away from x, and get the error below 10⁻⁶ (hint: move the expansion point)."],
      demo: { scene: "fn", set: { f: 1, x: 5, n: 8, a: 4.5 }, wait: 1 } },
    { id: "odo", robot: true, text: ["在“AGV 里程计”中取 lg u = −4、泰勒公式 3 项：直接公式的相对误差超过 10⁻⁹，泰勒公式的小于 10⁻¹⁵。", "In 'AGV odometry' take lg u = −4 with 3 Taylor terms: the direct formula errs by more than 10⁻⁹, the Taylor formula by less than 10⁻¹⁵."],
      demo: { scene: "odo", set: { lu: -4, m: 3 }, wait: 1 } },
  ],
  think: ["ln(1 + x) 的泰勒多项式在 x > 1 时次数越高越差，而 eˣ 的无论 x 多大最终都会收敛。区别在哪里？（第 16 章：收敛半径。）",
          "Taylor polynomials of ln(1 + x) get worse with degree for x > 1, while those of eˣ eventually converge for any x. What is the difference? (Chapter 16: radius of convergence.)"],

  // 第 k 阶导数在 t 处的值
  D(f, k, t) {
    switch (f) {
      case 1: return Math.exp(t);
      case 2: return Math.sin(t + k * Math.PI / 2);
      case 3: return Math.cos(t + k * Math.PI / 2);
      case 4: { if (k === 0) return Math.log1p(t); let c = 1; for (let i = 1; i < k; i++) c *= -i; return c / Math.pow(1 + t, k); }
      default: { let c = 1; for (let i = 0; i < k; i++) c *= 0.5 - i; return c * Math.pow(1 + t, 0.5 - k); }
    }
  },
  name(f) { return ["eˣ", "sin x", "cos x", "ln(1 + x)", "√(1 + x)"][f - 1]; },
  P(f, n, a, t) {
    let s = 0, fac = 1, pw = 1;
    for (let k = 0; k <= n; k++) { if (k > 0) { fac *= k; pw *= t - a; } s += this.D(f, k, a) * pw / fac; }
    return s;
  },
  bound(f, n, a, t) {
    let m = 0;
    for (let i = 0; i <= 200; i++) m = Math.max(m, Math.abs(this.D(f, n + 1, a + (t - a) * i / 200)));
    let fac = 1; for (let k = 2; k <= n + 1; k++) fac *= k;
    return m * Math.pow(Math.abs(t - a), n + 1) / fac;
  },
  odo(u, m) {
    const ref = 2 * Math.sin(u / 2) ** 2 / u, dir = (1 - Math.cos(u)) / u;
    let ser = 0, term = u / 2;                               // u/2 − u³/24 + u⁵/720 − …：第 k 项 (−1)ᵏ u^{2k+1}/(2k+2)!
    for (let k = 0; k < m; k++) { ser += term; term *= -u * u / ((2 * k + 3) * (2 * k + 4)); }
    return { ref, dir, ser, ed: Math.abs(dir - ref) / ref, es: Math.abs(ser - ref) / ref };
  },
  ok(api) { const f = api.p.f; return !((f === 4 || f === 5) && (api.p.a <= -0.95 || api.p.x <= -0.95)); },
  reset(api, s) { s.t = 0; },
  check(api) {
    if (api.scene === "odo") {
      const R = this.odo(Math.pow(10, api.p.lu), api.p.m);
      if (api.p.lu <= -3.95 && api.p.m >= 3 && R.ed > 1e-9 && R.es < 1e-15) api.done("odo");
      return;
    }
    const p = api.p, e = Math.abs(this.D(p.f, 0, p.x) - this.P(p.f, p.n, p.a, p.x));
    if (p.f === 2 && Math.abs(p.a) < 1e-9 && Math.abs(p.x - 0.785) < 0.003 && e < 1e-10) api.done("sin");
    if (p.f === 4 && Math.abs(p.a) < 1e-9 && p.x >= 1.45 && p.n >= 15 && e > 1) api.done("ln");
    if (p.f === 1 && Math.abs(p.x - 5) < 0.003 && Math.abs(p.x - p.a) >= 0.499 && p.n <= 8 && e < 1e-6) api.done("exp");
  },
  readouts(api, s) {
    const fe = (v) => (v === 0 ? "0" : v.toExponential(2));
    if (api.scene === "odo") {
      const u = Math.pow(10, api.p.lu), R = this.odo(u, api.p.m);
      this.check(api);
      return [[["u = ωT", "u = ωT"], u.toExponential(2)], [["参考值 2sin²(u/2)/u", "reference 2sin²(u/2)/u"], R.ref.toPrecision(16)],
              [["直接公式 (1 − cos u)/u", "direct (1 − cos u)/u"], R.dir.toPrecision(16)], [["直接公式的相对误差", "relative error, direct"], fe(R.ed)],
              [["泰勒公式", "Taylor formula"], R.ser.toPrecision(16)], [["泰勒公式的相对误差", "relative error, Taylor"], fe(R.es)]];
    }
    const p = api.p;
    if (!this.ok(api)) return [[["提示", "Note"], api.T("ln(1 + x)、√(1 + x) 要求 x > −1", "ln(1 + x) and √(1 + x) need x > −1")]];
    const fx = this.D(p.f, 0, p.x), px = this.P(p.f, p.n, p.a, p.x), e = Math.abs(fx - px);
    this.check(api);
    return [[["函数", "Function"], this.name(p.f)], [["f(x)", "f(x)"], fx.toPrecision(12)], [["Pₙ(x)", "Pₙ(x)"], px.toPrecision(12)],
            [["误差 |f(x) − Pₙ(x)|", "Error |f(x) − Pₙ(x)|"], fe(e)], [["拉格朗日余项的上界", "Lagrange bound"], fe(this.bound(p.f, p.n, p.a, p.x))]];
  },
  draw(api, s) {
    const w = api.w, h = api.h, ink = api.css("--ink"), red = api.css("--red"), mu = api.css("--muted"), blue = api.css("--blue");
    if (api.scene === "odo") {
      const G = api.graph({ x: 60, y: 24, w: w - 80, h: h - 74, xmin: -8, xmax: 0, ymin: -17, ymax: 1, xlabel: "lg u", ylabel: api.T("lg 相对误差", "lg relative error") });
      G.axes();
      const lg = (v) => Math.log10(Math.max(v, 1e-17)), D = [], S = [];
      for (let i = 0; i <= 240; i++) { const lu = -8 + 8 * i / 240, R = this.odo(Math.pow(10, lu), api.p.m); D.push([lu, lg(R.ed)]); S.push([lu, lg(R.es)]); }
      G.dots(D, ink, 1.8); G.dots(S, red, 1.8);
      G.vline(api.p.lu, blue); G.hline(-16, mu);
      return;
    }
    if (!this.ok(api)) return;
    const p = api.p, lo = (p.f === 4 || p.f === 5) ? -0.95 : -3, hi = 6;
    const vals = [];
    for (let i = 0; i <= 300; i++) { const t = lo + (hi - lo) * i / 300; vals.push(this.D(p.f, 0, t)); }
    let ymin = Math.min(...vals), ymax = Math.max(...vals);
    if (p.f === 1) { ymin = -1; ymax = Math.min(ymax, 160); }
    const pad = 0.15 * (ymax - ymin + 1e-9);
    ymin -= pad; ymax += pad;
    const G = api.graph({ x: 60, y: 24, w: w - 80, h: h - 74, xmin: lo, xmax: hi, ymin, ymax, xlabel: "x", ylabel: this.name(p.f) });
    G.axes();
    G.fn((t) => this.D(p.f, 0, t), ink, 2.2);
    G.fn((t) => { const v = this.P(p.f, p.n, p.a, t); return v > ymax + 10 * (ymax - ymin) || v < ymin - 10 * (ymax - ymin) ? NaN : v; }, red, 1.6);
    G.vline(p.x, mu);
    G.point(p.a, this.D(p.f, 0, p.a), red, "a");
    G.point(p.x, this.D(p.f, 0, p.x), blue, "x");
  },
});
