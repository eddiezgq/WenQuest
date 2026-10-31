// 实验 14.7 积不出来的积分（配 14.1、14.7 节）。“机器人”场景：断电后自由摆动的连杆（均匀细杆绕一端，近似物理摆），
// 大振幅时周期由椭圆积分给出，与小振幅公式比较；“积分检验”场景：对几个不定积分的候选答案求导验算，并比较定积分。
WQ.lab({
  title: ["实验 14.7 积不出来的积分", "Lab 14.7 Integrals with no elementary formula"],
  goal: ["体会“积不出来”不等于“算不出来”：单摆的大振幅周期是一个椭圆积分，写不成初等函数，却能精确计算；再用“求导验算”检查不定积分的答案。",
         "See that 'no formula' does not mean 'no answer': the large-swing period of a pendulum is an elliptic integral with no elementary form, yet it is computed precisely. Then check antiderivatives by differentiating them."],
  scenes: [
    { id: "pend", robot: true, name: ["连杆自由摆动", "Free-swinging link"], hide: ["f", "cand"],
      problem: { title: ["机器人问题：断电后连杆摆动的周期有多长？", "Robot problem: how long is the swing period of an unpowered link?"],
                 text: ["关节断电、刹车松开时，连杆在重力下来回摆动。把它看作均匀细杆绕一端摆动，等效摆长为杆长的 2/3。小振幅时周期为 2π√(L/g)；振幅大了，周期是一个椭圆积分。",
                        "With the joint unpowered and the brake released, the link swings under gravity. Treat it as a uniform rod pivoting at one end, equivalent length 2/3 of the rod. For small swings the period is 2π√(L/g); for large ones it is an elliptic integral."] } },
    { id: "check", name: ["积分检验", "Checking integrals"], hide: ["th0", "l"],
      problem: { title: ["哪个答案是对的？", "Which answer is right?"],
                 text: ["每个被积函数给了三个候选的原函数。对候选答案求导，看是否等于被积函数；再比较 F(b) − F(a) 与数值积分。",
                        "Each integrand comes with three candidate antiderivatives. Differentiate the candidate and compare with the integrand; then compare F(b) − F(a) with a numerical integral."] } },
  ],
  params: [
    { id: "th0", name: ["振幅 θ₀", "Amplitude θ₀"], min: 5, max: 170, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "l", name: ["杆长 l", "Rod length l"], min: 0.2, max: 1, step: 0.05, value: 0.4, unit: "m", digits: 2 },
    { id: "f", name: ["被积函数：1 x eˣ，2 ln x，3 x cos x，4 1/(x² − 1)", "Integrand: 1 x eˣ, 2 ln x, 3 x cos x, 4 1/(x² − 1)"], min: 1, max: 4, step: 1, value: 1, digits: 0 },
    { id: "cand", name: ["候选答案（1、2、3）", "Candidate (1, 2, 3)"], min: 1, max: 3, step: 1, value: 1, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["精确 / 被积函数", "exact / integrand"], color: "#1f77b4" }, { name: ["小振幅近似 / 候选的导数", "small-angle / candidate's derivative"], color: "#d62728" }],
  tasks: [
    { id: "pct", robot: true, text: ["振幅多大时，真实周期比小振幅公式长 1%？（精确到 1°）", "At what amplitude is the true period 1% longer than the small-angle formula? (to 1°)"],
      demo: { scene: "pend", set: { th0: 23, l: 0.4 }, wait: 1 } },
    { id: "big", robot: true, text: ["振幅 90° 时周期长多少？杆长从 0.4 m 改为 0.8 m，周期之比变不变？", "How much longer is the period at 90°? Does the ratio change when the rod goes from 0.4 m to 0.8 m?"],
      demo: { scene: "pend", set: { th0: 90, l: 0.8 }, wait: 1 } },
    { id: "ln", text: ["找出 ∫ln x dx 的正确答案（导数与被积函数处处重合）。", "Find the correct answer for ∫ln x dx (its derivative matches the integrand everywhere)."],
      demo: { scene: "check", set: { f: 2, cand: 2 }, wait: 1 } },
    { id: "rat", text: ["找出 ∫dx/(x² − 1) 的正确答案。哪个错误答案的导数在形状上最像？", "Find the correct answer for ∫dx/(x² − 1). Which wrong answer's derivative looks most similar?"],
      demo: { scene: "check", set: { f: 4, cand: 2 }, wait: 1 } },
  ],
  think: ["椭圆积分、误差函数、正弦积分都“积不出来”，计算器和数学库却能算到十几位有效数字。它们用的是什么方法？（第 15 章数值积分、第 24 章幂级数）",
          "Elliptic integrals, the error function and the sine integral have no elementary form, yet calculators give them to 15 digits. What methods do they use? (Chapter 15: numerical integration; Chapter 24: power series)"],

  G: 9.81,
  agm(a, b) { for (let i = 0; i < 40; i++) { const an = (a + b) / 2, bn = Math.sqrt(a * b); a = an; b = bn; } return a; },
  ratio(th0) {   // T/T₀ = (2/π)K(k)，K(k) = π/(2·agm(1, √(1 − k²)))
    const k = Math.sin(th0 * Math.PI / 360);
    return 1 / this.agm(1, Math.sqrt(1 - k * k));
  },
  swing(th0, w0, tEnd) {   // θ'' = −w0² sin θ，RK4
    const n = 1200, h = tEnd / n, out = [];
    let th = th0, om = 0;
    const f = (a) => -w0 * w0 * Math.sin(a);
    for (let i = 0; i <= n; i++) {
      out.push([i * h, th]);
      const k1t = om, k1o = f(th), k2t = om + h / 2 * k1o, k2o = f(th + h / 2 * k1t), k3t = om + h / 2 * k2o, k3o = f(th + h / 2 * k2t), k4t = om + h * k3o, k4o = f(th + h * k3t);
      th += h / 6 * (k1t + 2 * k2t + 2 * k3t + k4t);
      om += h / 6 * (k1o + 2 * k2o + 2 * k3o + k4o);
    }
    return out;
  },
  FN(f) {
    const L = (x) => Math.log(Math.abs(x));
    return [
      { f: (x) => x * Math.exp(x), a: 0, b: 2, name: "x eˣ", c: [[(x) => x * Math.exp(x) - Math.exp(x), "x eˣ − eˣ"], [(x) => x * x * Math.exp(x) / 2, "x² eˣ/2"], [(x) => x * Math.exp(x), "x eˣ"]] },
      { f: Math.log, a: 1, b: 3, name: "ln x", c: [[(x) => 1 / x, "1/x"], [(x) => x * Math.log(x) - x, "x ln x − x"], [(x) => x * Math.log(x), "x ln x"]] },
      { f: (x) => x * Math.cos(x), a: 0, b: 3, name: "x cos x", c: [[(x) => x * Math.sin(x), "x sin x"], [(x) => x * Math.sin(x) + Math.cos(x), "x sin x + cos x"], [(x) => x * x / 2 * Math.sin(x), "(x²/2) sin x"]] },
      { f: (x) => 1 / (x * x - 1), a: 2, b: 4, name: "1/(x² − 1)", c: [[(x) => L(x * x - 1), "ln|x² − 1|"], [(x) => 0.5 * L((x - 1) / (x + 1)), "½ ln|(x − 1)/(x + 1)|"], [(x) => Math.atan(x), "arctan x"]] },
    ][f - 1];
  },
  dF(F, x) { const h = 1e-5; return (F(x + h) - F(x - h)) / (2 * h); },
  reset() {},
  readouts(api) {
    const p = api.p;
    if (api.scene === "pend") {
      const Leq = 2 * p.l / 3, T0 = 2 * Math.PI * Math.sqrt(Leq / this.G), r = this.ratio(p.th0);
      if (Math.abs(p.th0 - 23) < 0.5) api.done("pct");
      if (p.th0 === 90 && p.l >= 0.79) api.done("big");
      return [[["等效摆长 2l/3", "Equivalent length 2l/3"], Leq.toFixed(3) + " m"], [["小振幅周期 T₀", "Small-angle period T₀"], T0.toFixed(4) + " s"],
              [["真实周期 T", "True period T"], (T0 * r).toFixed(4) + " s"], [["T/T₀", "T/T₀"], r.toFixed(5)], [["多出", "Excess"], ((r - 1) * 100).toFixed(2) + " %"]];
    }
    const D = this.FN(p.f), [F, cname] = D.c[p.cand - 1];
    let err = 0;
    for (let i = 0; i <= 100; i++) { const x = D.a + (D.b - D.a) * i / 100; err = Math.max(err, Math.abs(this.dF(F, x) - D.f(x))); }
    const n = 2000, h = (D.b - D.a) / n;
    let I = 0;
    for (let k = 0; k < n; k++) I += D.f(D.a + (k + 0.5) * h) * h;
    const ok = err < 1e-5;
    if (ok && p.f === 2) api.done("ln");
    if (ok && p.f === 4) api.done("rat");
    return [[["被积函数", "Integrand"], D.name], [["候选答案 F", "Candidate F"], cname], [["max |F′ − f|", "max |F′ − f|"], err < 1e-9 ? "< 1e-9" : err.toExponential(2)],
            [["数值积分 ∫ₐᵇ f", "Numerical ∫ₐᵇ f"], I.toFixed(6)], [["F(b) − F(a)", "F(b) − F(a)"], (F(D.b) - F(D.a)).toFixed(6)],
            [["结论", "Verdict"], ok ? api.T("正确", "correct") : api.T("不对", "wrong")]];
  },
  draw(api) {
    const w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), muted = api.css("--muted");
    const p = api.p;
    if (api.scene === "pend") {
      const Leq = 2 * p.l / 3, w0 = Math.sqrt(this.G / Leq), T0 = 2 * Math.PI / w0, th0 = p.th0 * Math.PI / 180, tEnd = 3 * T0 * this.ratio(p.th0);
      const S = this.swing(th0, w0, tEnd).map(([t, a]) => [t, a * 180 / Math.PI]);
      const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: tEnd, ymin: -p.th0 * 1.15, ymax: p.th0 * 1.15, xlabel: "t / s", ylabel: "θ / (°)" });
      G.axes();
      G.fn((t) => p.th0 * Math.cos(w0 * t), red, 1.6, [6, 4]);
      G.pts(S, blue, 2.2);
      return;
    }
    const D = this.FN(p.f), [F] = D.c[p.cand - 1];
    let lo = 0, hi = 0;
    for (let i = 0; i <= 200; i++) {
      const x = D.a + (D.b - D.a) * i / 200;
      for (const v of [D.f(x), this.dF(F, x)]) if (isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
    }
    const pad = 0.1 * (hi - lo + 0.1);
    const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: D.a, xmax: D.b, ymin: lo - pad, ymax: hi + pad, xlabel: "x", ylabel: "" });
    G.axes();
    G.hline(0, muted);
    G.fn(D.f, blue, 3);
    G.fn((x) => this.dF(F, x), red, 1.8, [6, 4]);
  },
});
