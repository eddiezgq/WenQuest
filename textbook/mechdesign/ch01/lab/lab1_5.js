// 实验 1.5 安全系数与可靠度（配 1.5 节）。强度 σlim、应力 σ 都按正态分布；平均安全系数 S = μlim/μσ（参数 n），变异系数 Clim（CS）、Cσ（Cs）。
// 可靠性指标 z = (S − 1)/√(S²Clim² + Cσ²)，可靠度 R = Φ(z)，失效概率 1 − R —— 与正文程序 1.5.1 同一公式。
function erfc1_5(x) {                              // 互补误差函数（Numerical Recipes 的切比雪夫近似，相对误差 < 1.2e-7）
  const z = Math.abs(x), t = 1 / (1 + 0.5 * z);
  const r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 +
    t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? r : 2 - r;
}
const pf1_5 = (z) => 0.5 * erfc1_5(z / Math.SQRT2);          // 1 − Φ(z)
function calc1_5(api) {
  const n = api.p.n, CS = api.p.CS, Cs = api.p.Cs;
  const z = (n - 1) / Math.sqrt(n * n * CS * CS + Cs * Cs);
  return { z, pf: pf1_5(z) };
}
const pdf1_5 = (x, m, s) => Math.exp(-0.5 * ((x - m) / s) ** 2) / (s * Math.sqrt(2 * Math.PI));
WQ.lab({
  title: ["实验 1.5 安全系数与可靠度", "Lab 1.5 Safety factor and reliability"],
  goal: ["改变强度和应力的平均值之比（安全系数）与各自的分散程度，看两条分布的重叠和失效概率怎样变化，体会“同样的安全系数，可靠度可以差很多”。",
         "Change the ratio of mean strength to mean stress (the safety factor) and the scatter of each; watch the overlap and the probability of failure, and see that the same safety factor can mean very different reliabilities."],
  scenes: [
    { id: "robot", robot: true, name: ["减速器输出轴外伸段", "Gearbox output-shaft extension"],
      problem: { title: ["工程问题：SH-301 外伸段起动时会不会屈服", "Engineering problem: will the SH-301 extension yield at start-up"],
                 text: ["Ø30 外伸段按平均起动峰值的安全系数约 1.81（算例 1.5.1）。钢材屈服强度的变异系数约 0.08；起动峰值的分散取决于工作机——输送机平稳（跑合试验台实测约 0.03），搅拌机、破碎机冲击大。",
                        "The Ø30 extension has a safety factor of about 1.81 on the mean starting peak (Example 1.5.1). Yield strength scatters by about 8%; the scatter of the starting peak depends on the driven machine — smooth for a conveyor (about 0.03 on the run-in bench), large for a mixer or crusher."] } },
    { id: "life", name: ["电梯钢丝绳", "Lift rope"],
      params: { n: { min: 2, max: 16, step: 0.1, value: 6 }, CS: { min: 0.02, max: 0.2, step: 0.01, value: 0.05 }, Cs: { min: 0.05, max: 0.6, step: 0.01, value: 0.35 } },
      problem: { title: ["生活中的例子：电梯钢丝绳的安全系数为什么那么大", "Everyday example: why lift ropes have such a large safety factor"],
                 text: ["钢丝绳本身的强度很稳定，但它的载荷变化大：乘客多少、急停时的冲击，再加上磨损、锈蚀使强度逐年下降。电梯规范（GB/T 7588.1）要求钢丝绳的安全系数不小于 12（三根及以上）。",
                        "The rope's strength is consistent, but its load varies a lot: the number of passengers, the shock of an emergency stop, plus wear and corrosion lowering the strength year by year. Lift codes (EN 81-20 / GB/T 7588.1) require a rope safety factor of at least 12 (three or more ropes)."] } },
  ],
  params: [
    { id: "n", name: ["平均安全系数 S = μlim/μσ", "Mean safety factor S = μlim/μσ"], min: 1.0, max: 4.0, step: 0.01, value: 1.81, unit: "", digits: 2 },
    { id: "CS", name: ["强度的变异系数 Clim", "Strength COV Clim"], min: 0.02, max: 0.20, step: 0.01, value: 0.08, unit: "", digits: 2 },
    { id: "Cs", name: ["应力的变异系数 Cσ", "Stress COV Cσ"], min: 0.02, max: 0.40, step: 0.01, value: 0.03, unit: "", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["评估", "Evaluate"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "var(--red)", name: ["应力分布", "stress"] }, { color: "var(--accent)", name: ["强度分布", "strength"] }],
  tasks: [
    { id: "base", robot: true, text: ["默认参数（S = 1.81，Clim = 0.08，Cσ = 0.03）评估一次，记下 z 和失效概率。", "Evaluate the defaults (S = 1.81, Clim = 0.08, Cσ = 0.03); record z and the probability of failure."],
      demo: { scene: "robot", set: { n: 1.81, CS: 0.08, Cs: 0.03 }, press: ["start"], wait: 1 } },
    { id: "ppm", robot: true, text: ["把 Cσ 改为 0.25（冲击大的工作机），找出使失效概率不超过百万分之一的最小安全系数。", "Set Cσ = 0.25 (a shock-loaded machine) and find the smallest safety factor with at most one failure in a million."],
      demo: { scene: "robot", set: { n: 2.55, CS: 0.08, Cs: 0.25 }, press: ["start"], wait: 1 } },
    { id: "life", text: ["电梯钢丝绳：Clim = 0.05、Cσ = 0.35 时，安全系数多大才能使失效概率低于千万分之一？与规范的 12 比较。", "Lift rope: with Clim = 0.05 and Cσ = 0.35, how large must the safety factor be for a probability of failure below one in ten million? Compare with the code value of 12."],
      demo: { scene: "life", set: { n: 3.0, CS: 0.05, Cs: 0.35 }, press: ["start"], wait: 1 } },
  ],
  think: ["为什么提高安全系数到一定程度以后，失效概率下降得越来越慢？哪一个变异系数在这时起主要作用？",
          "Why does raising the safety factor beyond a point reduce the probability of failure more and more slowly? Which COV dominates then?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    s.r = calc1_5(api);
    const p = api.p;
    if (api.scene === "robot" && Math.abs(p.n - 1.81) < 0.005 && Math.abs(p.CS - 0.08) < 0.005 && Math.abs(p.Cs - 0.03) < 0.005) api.done("base");
    if (api.scene === "robot" && p.Cs >= 0.245 && p.CS >= 0.075 && s.r.pf <= 1e-6 && p.n <= 2.6) api.done("ppm");
    if (api.scene === "life" && p.Cs >= 0.345 && s.r.pf <= 1e-7) api.done("life");
    api.stop();
  },
  readouts(api, s) {
    const r = calc1_5(api), f = api.fmt;
    const ppm = r.pf * 1e6;
    return [
      [["可靠性指标 z", "Reliability index z"], f(r.z, 2)],
      [["可靠度 R", "Reliability R"], r.pf < 1e-9 ? "> 0.999 999 999" : f(1 - r.pf, 7)],
      [["失效概率 1 − R", "Probability of failure 1 − R"], r.pf.toExponential(2)],
      [["每百万件（次）失效", "Failures per million"], ppm >= 1 ? f(ppm, 0) : f(ppm, 3)],
    ];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p;
    const xmax = Math.max(2.5, p.n * (1 + 4 * p.CS) + 0.2);
    const N = 240, st = [], sg = [], ov = [];
    let ymax = 0;
    for (let i = 0; i <= N; i++) {
      const x = i / N * xmax;
      const a = pdf1_5(x, 1, p.Cs), b = pdf1_5(x, p.n, p.n * p.CS);
      st.push([x, a]); sg.push([x, b]); ov.push([x, Math.min(a, b)]);
      ymax = Math.max(ymax, a, b);
    }
    const P = api.plot(w * 0.06, h * 0.08, w * 0.56, h * 0.78, [
      { pts: st, color: css("--red") },
      { pts: sg, color: css("--accent") },
    ], { xmin: 0, xmax, ymin: 0, ymax: ymax * 1.1, xlabel: api.T("应力或强度（平均应力 = 1）", "stress or strength (mean stress = 1)"), ylabel: "" });
    ov.forEach(([x, v]) => { if (v > ymax * 0.002) api.line(P.X(x), P.Y(0), P.X(x), P.Y(v), "rgba(214,39,40,0.30)", 2); });   // 干涉区
    api.line(P.X(1), P.Y(0), P.X(1), P.Y(ymax * 1.05), css("--muted"), 1, [3, 3]);
    api.line(P.X(p.n), P.Y(0), P.X(p.n), P.Y(ymax * 1.05), css("--muted"), 1, [3, 3]);
    // 右：失效概率与安全系数（对数坐标，以 log10 画）
    const curve = [];
    for (let i = 0; i <= 120; i++) {
      const n = 1 + i / 120 * 3;
      const z = (n - 1) / Math.sqrt(n * n * p.CS * p.CS + p.Cs * p.Cs);
      curve.push([n, Math.max(-10, Math.log10(Math.max(pf1_5(z), 1e-12)))]);
    }
    const Q = api.plot(w * 0.68, h * 0.08, w * 0.29, h * 0.78, [{ pts: curve, color: css("--blue") }],
      { xmin: 1, xmax: 4, ymin: -10, ymax: 0, xlabel: "S", ylabel: "log₁₀(1 − R)" });
    api.line(Q.X(1), Q.Y(-6), Q.X(4), Q.Y(-6), css("--green"), 1, [4, 4]);
    const r = calc1_5(api);
    api.circle(Q.X(Math.min(p.n, 4)), Q.Y(Math.max(-10, Math.log10(Math.max(r.pf, 1e-12)))), 5, css("--accent"), css("--ink"));
  },
});
