// 实验 10.5 多项式拟合：次数与过拟合（配 10.5 节）。力传感器零点随温度漂移，真实曲线 y = 0.20 + 0.35x − 0.25x² + 0.30x³（N），
// x = (T − 40)/20，T 在 20～60 °C；测量噪声 σ = 0.03 N。训练点在温度上等距分布，检验点另外随机取 40 个（固定种子；与正文程序 10.5.1 的 12 个检验点不同，数值会略有差别）。
// 拟合用伪逆（奇异值分解）求最小二乘解，次数从 1 到 11。
WQ.lab({
  title: ["实验 10.5 多项式拟合：次数与过拟合", "Lab 10.5 Polynomial fitting: degree and overfitting"],
  goal: ["改变多项式的次数，读出训练误差与检验误差，找出最合适的次数；体会次数过高时“训练得很好、预测得很差”；比较训练点多少的影响。",
         "Change the polynomial degree, read the training and test errors and find the best degree; see how too high a degree fits the training data well and predicts badly; compare more and fewer training points."],
  scenes: [
    { id: "few", robot: true, name: ["12 个训练点", "12 training points"],
      problem: { title: ["机器人问题：力传感器的温度补偿", "Robot problem: temperature compensation of a force sensor"],
                 text: ["腕部力传感器的零点随温度漂移。标定时在 20～60 °C 之间测了 12 个温度点，要找一个多项式来补偿。次数取多少合适？",
                        "A wrist force sensor's zero drifts with temperature. Calibration measured 12 temperatures between 20 and 60 °C, and a polynomial is wanted for compensation. What degree is right?"] } },
    { id: "many", robot: true, name: ["36 个训练点", "36 training points"],
      problem: { title: ["多测一些点会怎样？", "What if we measure more points?"],
                 text: ["同样的温度范围、同样的噪声，测 36 个点。高次多项式还会过拟合得那么厉害吗？",
                        "Same range, same noise, 36 points. Does a high-degree polynomial still overfit as badly?"] } },
  ],
  params: [{ id: "d", name: ["多项式次数", "Degree"], min: 1, max: 11, step: 1, value: 1, digits: 0 }],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "best", robot: true, text: ["在 12 个训练点的场景中，找出检验误差最小的次数。", "With 12 training points, find the degree with the smallest test error."],
      demo: { scene: "few", set: { d: 3 }, press: [] } },
    { id: "interp", robot: true, text: ["在 12 个训练点的场景中，让训练误差变为零，读出此时的检验误差，与最佳次数比较。", "With 12 training points, make the training error zero; read the test error and compare with the best degree."],
      demo: { scene: "few", set: { d: 11 }, press: [] } },
    { id: "many", robot: true, text: ["在 36 个训练点的场景中取 11 次，确认检验误差比 12 个点时的 11 次小得多。", "With 36 points and degree 11, check that the test error is much smaller than with 12 points at degree 11."],
      demo: { scene: "many", set: { d: 11 }, press: [] } },
  ],
  think: ["12 个点、11 次多项式时训练误差为什么恰好是零？这时最小二乘问题变成了什么问题？（提示：9.2.5 节的插值。）",
          "Why is the training error exactly zero with 12 points and degree 11? What has the least-squares problem become? (Hint: interpolation, Section 9.2.5.)"],

  truth(x) { return 0.20 + 0.35 * x - 0.25 * x * x + 0.30 * x * x * x; },
  data(api, n) {
    const r = api.calc.rng(n === 12 ? 2024 : 2036), tr = [], te = [];
    for (let i = 0; i < n; i++) { const x = -1 + 2 * i / (n - 1); tr.push([x, this.truth(x) + 0.03 * r.gauss()]); }
    const r2 = api.calc.rng(4040);
    for (let i = 0; i < 40; i++) { const x = -1 + 2 * r2.u(); te.push([x, this.truth(x) + 0.03 * r2.gauss()]); }
    return { tr, te };
  },
  fit(pts, d, la) {
    const A = pts.map(([x]) => Array.from({ length: d + 1 }, (_, k) => Math.pow(x, k)));
    return la.mv(la.pinv(A, 1e-12), pts.map((p) => p[1]));
  },
  ev(c, x) { return c.reduceRight((s, a) => s * x + a, 0); },
  rms(c, pts) { return Math.sqrt(pts.reduce((s, [x, y]) => s + (this.ev(c, x) - y) ** 2, 0) / pts.length); },
  reset(api, s) {
    const n = api.scene === "few" ? 12 : 36, D = this.data(api, n);
    s.D = D;
    s.curve = [];
    for (let d = 1; d <= 11; d++) { const c = this.fit(D.tr, d, api.la); s.curve.push([d, this.rms(c, D.tr) * 1000, this.rms(c, D.te) * 1000]); }
    s.c = this.fit(D.tr, api.p.d, api.la);
  },
  readouts(api, s) {
    if (!s.c) return [];
    const d = api.p.d, [_, tr, te] = s.curve[d - 1], best = s.curve.reduce((b, r) => (r[2] < b[2] ? r : b));
    if (api.scene === "few" && d === best[0]) api.done("best");
    if (api.scene === "few" && tr < 1e-6) api.done("interp");
    if (api.scene === "many" && d === 11) {
      const D12 = this.data(api, 12), te12 = this.rms(this.fit(D12.tr, 11, api.la), D12.te) * 1000;
      if (te < 0.6 * te12) api.done("many");
    }
    return [[["训练误差（均方根）", "Training error (RMS)"], api.fmt(tr, 1) + " mN"],
            [["检验误差（均方根）", "Test error (RMS)"], api.fmt(te, 1) + " mN"],
            [["测量噪声 σ", "Measurement noise σ"], "30.0 mN"],
            [["系数个数 / 训练点数", "Coefficients / training points"], (d + 1) + " / " + s.D.tr.length]];
  },
  draw(api, s) {
    if (!s.c) return;
    const { w, h } = api, muted = api.css("--muted"), red = api.css("--red"), blue = api.css("--blue"), acc = api.css("--green");
    const L = api.plot(50, 30, w * 0.58 - 60, h - 70, [{ pts: Array.from({ length: 121 }, (_, i) => { const x = -1 + i / 60; return [20 + 20 * (x + 1), this.truth(x)]; }), color: muted }],
                       { xmin: 20, xmax: 60, ymin: -0.9, ymax: 0.8, xlabel: api.T("温度 T / °C", "temperature T / °C"), ylabel: api.T("零点漂移 / N", "zero drift / N") });
    const T = (x) => 20 + 20 * (x + 1), c = api.ctx;
    c.save(); c.beginPath(); c.rect(50, 30, w * 0.58 - 60, h - 70); c.clip();
    c.strokeStyle = red; c.lineWidth = 2.5; c.beginPath();
    for (let i = 0; i <= 400; i++) { const x = -1 + i / 200, X = L.X(T(x)), Y = L.Y(this.ev(s.c, x)); if (i) c.lineTo(X, Y); else c.moveTo(X, Y); }
    c.stroke(); c.restore();
    s.D.te.forEach(([x, y]) => { c.beginPath(); c.arc(L.X(T(x)), L.Y(y), 3.5, 0, 7); c.strokeStyle = acc; c.lineWidth = 1.5; c.stroke(); });
    s.D.tr.forEach(([x, y]) => api.circle(L.X(T(x)), L.Y(y), 4, blue, blue));
    api.label(api.T("● 训练点  ○ 检验点（绿）  — 真实曲线（灰）与拟合（红）", "● training  ○ test (green)  — true (grey) and fit (red)"), 54, 22, api.css("--ink"), 12);
    const x0 = w * 0.62, wd = w * 0.36, ymax = Math.max(120, ...s.curve.map((r) => Math.min(r[2], 300)));
    const P = api.plot(x0, 30, wd, h - 70, [{ pts: s.curve.map((r) => [r[0], r[1]]), color: blue }, { pts: s.curve.map((r) => [r[0], Math.min(r[2], ymax)]), color: acc }],
                       { xmin: 1, xmax: 11, ymin: 0, ymax, xlabel: api.T("次数", "degree"), ylabel: api.T("误差 / mN", "error / mN") });
    const cur = s.curve[api.p.d - 1];
    api.line(P.X(cur[0]), 30, P.X(cur[0]), h - 40, muted, 1, [4, 3]);
    api.label(api.T("蓝：训练  绿：检验", "blue: training  green: test"), x0 + 4, 22, api.css("--ink"), 12);
  },
});
