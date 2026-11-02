// 实验 24.6 用幂级数计算误差函数（配 24.1、24.3、24.6 节）。“两个级数”场景：erf x 的交错级数与正项级数，截断项数与精度、
// 最大项与相消；“定位公差”场景：机器人重复定位误差服从正态分布，落在公差带内的概率 erf(a/(σ√2)) 与超差率。
WQ.lab({
  title: ["实验 24.6 用幂级数计算误差函数", "Lab 24.6 Computing the error function with power series"],
  goal: ["用两种幂级数计算 erf x，比较截断项数与精度：交错级数在 x 大时各项先变得极大再相消，双精度下损失有效数字；正项级数没有相消。再用 erf 计算机器人定位误差落在公差带内的概率。",
         "Compute erf x with two power series and compare truncation and accuracy: for large x the alternating series' terms become huge before cancelling, losing digits in double precision; the positive series has no cancellation. Then use erf to find the probability that a robot's positioning error stays within tolerance."],
  scenes: [
    { id: "series", name: ["两个级数", "Two series"], hide: ["sig", "tol"],
      problem: { title: ["同一个函数，两个级数，哪个好用？", "One function, two series: which works?"],
                 text: ["级数 1（逐项积分 e^(−t²) 的展开）：erf x = (2/√π) Σ (−1)ⁿ x^(2n+1)/(n!(2n+1))；级数 2：erf x = (2/√π) e^(−x²) Σ 2ⁿ x^(2n+1)/(1·3·5···(2n+1))。选 x 和项数 n，看部分和的误差。",
                        "Series 1 (term-by-term integral of the expansion of e^(−t²)): erf x = (2/√π) Σ (−1)ⁿ x^(2n+1)/(n!(2n+1)); series 2: erf x = (2/√π) e^(−x²) Σ 2ⁿ x^(2n+1)/(1·3·5···(2n+1)). Choose x and the number of terms n and watch the error of the partial sum."] } },
    { id: "robot", robot: true, name: ["定位公差", "Positioning tolerance"], hide: ["x", "s", "n"],
      problem: { title: ["机器人问题：重复定位误差落在公差带内的概率是多少？", "Robot problem: how likely is the repeat-positioning error to stay within tolerance?"],
                 text: ["机械臂反复回到同一位置，某一方向的偏差近似服从均值为 0、标准差为 σ 的正态分布。偏差落在 ±a 内的概率为 erf(a/(σ√2))。装配要求超差率不超过百万分之一（1 ppm），公差带至少要多宽？",
                        "An arm returns to the same pose again and again; its deviation in one direction is roughly normal with mean 0 and standard deviation σ. The probability of staying within ±a is erf(a/(σ√2)). If assembly allows at most one part per million out of tolerance, how wide must the band be?"] } },
  ],
  params: [
    { id: "x", name: ["自变量 x", "Argument x"], min: 0.1, max: 6, step: 0.1, value: 1, digits: 1 },
    { id: "s", name: ["级数：1 交错级数，2 正项级数", "Series: 1 alternating, 2 positive"], min: 1, max: 2, step: 1, value: 1, digits: 0 },
    { id: "n", name: ["项数 n", "Terms n"], min: 1, max: 120, step: 1, value: 3, digits: 0 },
    { id: "sig", name: ["标准差 σ", "Standard deviation σ"], min: 0.005, max: 0.05, step: 0.001, value: 0.01, unit: "mm", digits: 3 },
    { id: "tol", name: ["公差带半宽 a", "Half-width of tolerance a"], min: 0.005, max: 0.1, step: 0.001, value: 0.02, unit: "mm", digits: 3 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["级数 1（交错）", "series 1 (alternating)"], color: "#d62728" }, { name: ["级数 2（正项）", "series 2 (positive)"], color: "#1f77b4" }],
  tasks: [
    { id: "few", text: ["x = 1：交错级数取多少项，误差小于 10⁻⁶？用交错级数的误差界（第一个略去的项）预测，再核对。", "x = 1: how many terms of the alternating series make the error below 10⁻⁶? Predict with the alternating-series bound and check."],
      demo: { scene: "series", set: { x: 1, s: 1, n: 9 }, wait: 1 } },
    { id: "cancel", text: ["x = 5：交错级数无论取多少项，误差都降不到 10⁻⁹ 以下。记下最大项的大小，解释原因；换成正项级数，使误差小于 10⁻¹⁴。",
                           "x = 5: however many terms you take, the alternating series cannot get below 10⁻⁹. Note the size of the largest term and explain; switch to the positive series and get below 10⁻¹⁴."],
      demo: { scene: "series", set: { x: 5, s: 2, n: 90 }, wait: 1 } },
    { id: "prob", robot: true, text: ["σ = 0.01 mm、公差 ±0.03 mm（即 ±3σ）：落在公差带内的概率是多少？超差率是多少 ppm？", "σ = 0.01 mm, tolerance ±0.03 mm (±3σ): what is the probability of staying within it, and the out-of-tolerance rate in ppm?"],
      demo: { scene: "robot", set: { sig: 0.01, tol: 0.03 }, wait: 1 } },
    { id: "ppm", robot: true, text: ["σ = 0.01 mm：公差带半宽至少多大，超差率才不超过 1 ppm？（找出最小的 a，精确到 0.001 mm）", "σ = 0.01 mm: what is the smallest half-width a (to 0.001 mm) that keeps the out-of-tolerance rate at or below 1 ppm?"],
      demo: { scene: "robot", set: { sig: 0.01, tol: 0.049 }, wait: 1 } },
  ],
  think: ["交错级数在 x = 3 时最大项约 200，而和不到 1。双精度有约 16 位有效数字，计算结果大约能剩几位？由此估计 x = 5 时的误差。",
          "At x = 3 the alternating series' largest term is about 200 while the sum is below 1. With about 16 significant digits in double precision, how many survive? Use this to estimate the error at x = 5."],

  C: 2 / Math.sqrt(Math.PI),
  alt(x, n) {   // 交错级数前 n 项：部分和、最大项
    let t = x, s = 0, big = 0;
    const ps = [];
    for (let k = 0; k < n; k++) {
      const term = (k % 2 ? -1 : 1) * t / (2 * k + 1);
      s += term; big = Math.max(big, Math.abs(term)); ps.push(this.C * s);
      t *= x * x / (k + 1);
    }
    return { ps, big: this.C * big };
  },
  pos(x, n) {   // 正项级数前 n 项
    let t = x, s = 0;
    const ps = [], f = this.C * Math.exp(-x * x);
    for (let k = 0; k < n; k++) { s += t; ps.push(f * s); t *= 2 * x * x / (2 * k + 3); }
    return { ps };
  },
  erf(x) {   // 参考值：x < 2 用正项级数取 400 项（远多于需要）；x ≥ 2 用 1 − erfc（连分式）
    if (x >= 2) return 1 - this.erfc(x);
    const r = this.pos(x, 400).ps; return r[r.length - 1];
  },
  erfc(x) {   // 1 − erf 的可靠值（超差率要用；x 大时 1 − erf 会相消）：连分式
    if (x < 2) { const r = this.pos(x, 400).ps; return 1 - r[r.length - 1]; }
    let f = 0;
    for (let k = 60; k >= 1; k--) f = (k / 2) / (x + f);
    return Math.exp(-x * x) / Math.sqrt(Math.PI) / (x + f);
  },
  reset() {},
  readouts(api) {
    const p = api.p;
    if (api.scene === "series") {
      const ex = this.erf(p.x), A = this.alt(p.x, p.n), B = this.pos(p.x, p.n);
      const sv = p.s === 1 ? A.ps[A.ps.length - 1] : B.ps[B.ps.length - 1], err = Math.abs(sv - ex);
      if (Math.abs(p.x - 1) < 1e-9 && p.s === 1 && err < 1e-6 && Math.abs(this.alt(p.x, p.n - 1).ps[p.n - 2] - ex) >= 1e-6) api.done("few");
      if (Math.abs(p.x - 5) < 1e-9 && p.s === 2 && err < 1e-14) api.done("cancel");
      const nextB = this.C * Math.pow(p.x, 2 * p.n + 1) / (this.fact(p.n) * (2 * p.n + 1));
      return [[["erf x（参考值）", "erf x (reference)"], ex.toPrecision(16)],
              [["所选级数前 n 项", "chosen series, n terms"], sv.toPrecision(16)],
              [["误差", "error"], err === 0 ? "< 1e-16" : err.toExponential(2)],
              [["交错级数：最大项 / 第一个略去的项", "alternating: largest term / first omitted"], A.big.toPrecision(3) + " / " + nextB.toPrecision(3)]];
    }
    const xa = p.tol / (p.sig * Math.SQRT2), out = this.erfc(xa), P = 1 - out, ppm = out * 1e6;
    if (Math.abs(p.sig - 0.01) < 1e-9 && Math.abs(p.tol - 0.03) < 1e-9) api.done("prob");
    if (Math.abs(p.sig - 0.01) < 1e-9 && ppm <= 1 && this.erfc((p.tol - 0.001) / (p.sig * Math.SQRT2)) * 1e6 > 1) api.done("ppm");
    return [[["x = a/(σ√2)", "x = a/(σ√2)"], xa.toFixed(4)],
            [["a 是 σ 的多少倍", "a in units of σ"], (p.tol / p.sig).toFixed(2) + "σ"],
            [["落在公差带内的概率 erf x", "probability within band, erf x"], P.toFixed(8)],
            [["超差率", "out-of-tolerance rate"], ppm < 0.01 ? ppm.toExponential(2) + " ppm" : ppm.toFixed(2) + " ppm"]];
  },
  fact(n) { let f = 1; for (let k = 2; k <= n; k++) f *= k; return f; },
  draw(api) {
    const p = api.p, w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), muted = api.css("--muted");
    if (api.scene === "series") {
      const ex = this.erf(p.x), A = this.alt(p.x, 120), B = this.pos(p.x, 120);
      const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 1, xmax: 120, ymin: -17, ymax: 10, xlabel: api.T("项数 n", "terms n"), ylabel: "log₁₀|error|" });
      G.axes();
      const lg = (v) => Math.max(-17, Math.min(10, Math.log10(Math.max(Math.abs(v - ex), 1e-18))));
      G.pts(A.ps.map((v, i) => [i + 1, lg(v)]), red, 2);
      G.pts(B.ps.map((v, i) => [i + 1, lg(v)]), blue, 2);
      G.vline(p.n, muted, [4, 4]);
      G.hline(Math.log10(2.2e-16), muted, [2, 4]);
      return;
    }
    const s = p.sig, G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: -6 * s, xmax: 6 * s, ymin: 0, ymax: 1.15 / (s * Math.sqrt(2 * Math.PI)), xlabel: api.T("偏差 / mm", "deviation / mm"), ylabel: api.T("概率密度", "density") });
    G.axes();
    const f = (x) => Math.exp(-x * x / (2 * s * s)) / (s * Math.sqrt(2 * Math.PI));
    if (G.area) G.area(f, -Math.min(p.tol, 6 * s), Math.min(p.tol, 6 * s), blue);
    G.fn(f, blue, 2.5);
    G.vline(p.tol, red, [5, 4]); G.vline(-p.tol, red, [5, 4]);
  },
});
