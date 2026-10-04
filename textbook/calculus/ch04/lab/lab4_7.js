// 实验 4.7 浮点数里的极限（配 4.7 节）。在双精度下按原式与改写式计算 sin x / x、(1 − cos x)/x²、(eˣ − 1)/x，
// 与泰勒级数给出的真值比较相对误差；“机器人”场景：差速 AGV 里程计的横向位移 Δy = (v/ω)(1 − cos ωT)，v = 1 m/s，T = 20 ms。
WQ.lab({
  title: ["实验 4.7 浮点数里的极限：何时出错，怎样改写", "Lab 4.7 Limits in floating point: when they fail and how to rewrite"],
  goal: ["把自变量一步步缩小，看原式的相对误差何时开始变大、何时完全错误，理解相消；用改写式或专门的函数恢复精度。",
         "Shrink the variable step by step, see when the original formula's relative error starts to grow and when it fails completely, understand cancellation, and recover accuracy with a rewritten formula or a special function."],
  scenes: [
    { id: "lim", name: ["函数的极限", "Limits of functions"], hide: ["lw"],
      problem: { title: ["数学上越小越准，计算机上却越小越错", "Smaller is better in mathematics, worse on a computer"],
                 text: ["x → 0 时三个函数都有极限。用双精度计算，x 取多小时结果开始不可信？为什么 sin x / x 没有问题，(1 − cos x)/x² 却有？",
                        "All three functions have limits as x → 0. In double precision, how small can x get before the result becomes untrustworthy? Why is sin x / x fine while (1 − cos x)/x² is not?"] } },
    { id: "odo", robot: true, name: ["AGV 里程计", "AGV odometry"], hide: ["f", "lx"],
      problem: { title: ["机器人问题：转得越慢，横向位移算得越错", "Robot problem: the slower the turn, the worse the sideways step"],
                 text: ["差速 AGV 一个控制周期（20 ms）内的横向位移 Δy = (v/ω)(1 − cos ωT)。ω 很小时，原式与改写式 (v/ω)·2 sin²(ωT/2) 各给出多少？",
                        "The sideways step of a differential AGV in one 20 ms cycle is Δy = (v/ω)(1 − cos ωT). For tiny ω, what do the original and the rewritten (v/ω)·2 sin²(ωT/2) give?"] } },
  ],
  params: [
    { id: "f", name: ["函数：1 sin x/x，2 (1 − cos x)/x²，3 (eˣ − 1)/x", "Function: 1 sin x/x, 2 (1 − cos x)/x², 3 (eˣ − 1)/x"], min: 1, max: 3, step: 1, value: 2, digits: 0 },
    { id: "lx", name: ["lg x", "lg x"], min: -12, max: 0, step: 0.1, value: -1, digits: 1 },
    { id: "lw", name: ["lg ω（ω 以 rad/s 计）", "lg ω (ω in rad/s)"], min: -10, max: 0, step: 0.1, value: -2, digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["原式", "original"], color: "#d62728" }, { name: ["改写式", "rewritten"], color: "#2ca02c" }],
  tasks: [
    { id: "fail", text: ["选 (1 − cos x)/x²，把 x 缩小，找到原式相对误差超过 1% 的 x。", "Choose (1 − cos x)/x², shrink x and find an x where the original formula's relative error exceeds 1%."],
      demo: { scene: "lim", set: { f: 2, lx: -7.5 }, press: [], wait: 1 } },
    { id: "fix", text: ["同一个函数，令 x = 10⁻⁸，确认改写式的相对误差小于 10⁻¹²。", "Same function at x = 10⁻⁸: check that the rewritten formula's relative error is below 10⁻¹²."],
      demo: { scene: "lim", set: { f: 2, lx: -8 }, press: [], wait: 1 } },
    { id: "odo", robot: true, text: ["在“AGV 里程计”中令 ω = 10⁻⁶ rad/s，读出原式与改写式的 Δy，原式的相对误差应超过 5%。", "In 'AGV odometry' set ω = 10⁻⁶ rad/s and read Δy from both formulas; the original's relative error should exceed 5%."],
      demo: { scene: "odo", set: { lw: -6 }, press: [], wait: 1 } },
  ],
  think: ["表 4.7.1 中原式的相对误差大约按 ε_mach/x² 增长，为什么？若函数是 (x − sin x)/x³，误差会按 x 的几次方增长？",
          "In Table 4.7.1 the original's relative error grows roughly like ε_mach/x². Why? For (x − sin x)/x³, with what power of x would it grow?"],

  // value of the original formula, the rewritten one, and the truth (Taylor series, accurate for |x| ≤ 1 to ~1e−16)
  evalf(k, x) {
    const t = (cs) => { let s = 0, p = 1; for (const c of cs) { s += c * p; p *= x; } return s; };
    if (k === 1) {
      const tr = (() => { let s = 0, term = 1; for (let n = 0; n < 12; n++) { s += term; term *= -x * x / ((2 * n + 2) * (2 * n + 3)); } return s; })();
      return { o: Math.sin(x) / x, r: Math.sin(x) / x, tr, no: "sin x / x", nr: "sin x / x" };
    }
    if (k === 2) {
      const tr = (() => { let s = 0, term = 0.5; for (let n = 0; n < 12; n++) { s += term; term *= -x * x / ((2 * n + 3) * (2 * n + 4)); } return s; })();
      const h = Math.sin(x / 2);
      return { o: (1 - Math.cos(x)) / (x * x), r: 2 * h * h / (x * x), tr, no: "(1 − cos x)/x²", nr: "2 sin²(x/2)/x²" };
    }
    const tr = (() => { let s = 0, term = 1; for (let n = 0; n < 16; n++) { s += term; term *= x / (n + 2); } return s; })();
    return { o: (Math.exp(x) - 1) / x, r: Math.expm1(x) / x, tr, no: "(eˣ − 1)/x", nr: "expm1(x)/x" };
  },
  odo(w) {   // v = 1 m/s, T = 0.02 s
    const v = 1, T = 0.02, u = w * T, s = Math.sin(u / 2);
    const tr = (() => { let sum = 0, term = u / 2; for (let n = 0; n < 10; n++) { sum += term; term *= -u * u / ((2 * n + 3) * (2 * n + 4)); } return v * T * sum; })();
    return { o: v / w * (1 - Math.cos(u)), r: v / w * 2 * s * s, tr };
  },
  // scientific notation (api.fmt uses fixed decimals and would print 0.000 for tiny numbers)
  sf(v, d) {
    if (v === 0) return "0";
    const [m, e] = v.toExponential(d).split("e"), n = +e;
    if (n >= -2 && n <= 3) return (+v).toPrecision(d + 1);
    const sup = String(n).replace("-", "⁻").replace(/[0-9]/g, (c) => "⁰¹²³⁴⁵⁶⁷⁸⁹"[c]);
    return m + "×10" + sup;
  },
  rel(a, b) { return Math.abs(a - b) / Math.abs(b); },
  readouts(api) {
    if (api.scene === "odo") {
      const w = Math.pow(10, api.p.lw), R = this.odo(w), eo = this.rel(R.o, R.tr), er = this.rel(R.r, R.tr);
      if (Math.abs(api.p.lw + 6) < 0.051 && eo > 0.05 && er < 1e-12) api.done("odo");
      return [[["ω", "ω"], this.sf(w, 3) + " rad/s"],
              [["原式 Δy", "Original Δy"], this.sf(R.o, 6) + " m" + api.T("（相对误差 ", " (rel. error ") + this.sf(eo, 2) + api.T("）", ")")],
              [["改写式 Δy", "Rewritten Δy"], this.sf(R.r, 6) + " m" + api.T("（相对误差 ", " (rel. error ") + this.sf(er, 2) + api.T("）", ")")],
              [["真值（级数）", "True value (series)"], this.sf(R.tr, 6) + " m"]];
    }
    const x = Math.pow(10, api.p.lx), R = this.evalf(api.p.f, x), eo = this.rel(R.o, R.tr), er = this.rel(R.r, R.tr);
    if (api.p.f === 2 && eo > 0.01) api.done("fail");
    if (api.p.f === 2 && Math.abs(api.p.lx + 8) < 0.051 && er < 1e-12) api.done("fix");
    return [[["x", "x"], this.sf(x, 3)],
            [["原式 " + R.no, "Original " + R.no], this.sf(R.o, 12) + api.T("（相对误差 ", " (rel. error ") + this.sf(eo, 2) + api.T("）", ")")],
            [["改写式 " + R.nr, "Rewritten " + R.nr], this.sf(R.r, 12) + api.T("（相对误差 ", " (rel. error ") + this.sf(er, 2) + api.T("）", ")")],
            [["真值（级数）", "True value (series)"], this.sf(R.tr, 12)]];
  },
  draw(api) {
    const w = api.w, h = api.h, red = api.css("--red"), green = api.css("--green"), mu = api.css("--muted");
    const odo = api.scene === "odo", lo = odo ? -10 : -12, hi = 0, cur = odo ? api.p.lw : api.p.lx;
    const lg = (v) => Math.log10(Math.max(v, 1e-17));
    const G = api.graph({ x: 60, y: 20, w: w - 80, h: h - 70, xmin: lo, xmax: hi, ymin: -17, ymax: 1,
      xlabel: odo ? "lg ω" : "lg x", ylabel: api.T("lg 相对误差", "lg relative error") });
    G.axes();
    const po = [], pr = [];
    for (let s = lo; s <= hi + 1e-9; s += 0.05) {
      const z = Math.pow(10, s), R = odo ? this.odo(z) : this.evalf(api.p.f, z);
      po.push([s, lg(this.rel(R.o, R.tr))]); pr.push([s, lg(this.rel(R.r, R.tr))]);
    }
    G.pts(po, red, 2); G.pts(pr, green, 2);
    G.hline(Math.log10(2.22e-16), mu); G.hline(-2, mu); G.vline(cur, mu);
  },
});
