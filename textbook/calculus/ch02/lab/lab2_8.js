// 实验 2.8 从数据到函数：舵机的标定（配 2.8 节）。舵机数据与程序 2.8.1 相同：示意模型 θ = 90 + 0.095(p − 1500) − 1.5×10⁻⁸(p − 1500)³，
// 脉宽 600–2400 μs 每 100 μs 一组，读数误差 σ = 0.3°（种子 28），取到 0.1°。“热茶”场景：室温 20 °C，T = 20 + 65e^(−t/22)，
// 每 5 min 一次，误差 σ = 0.3 °C（种子 5）。最小二乘拟合一次、二次、三次多项式（自变量先换到标准区间）或指数模型，看残差，反求目标值。
WQ.lab({
  title: ["实验 2.8 从数据到函数：舵机的标定", "Lab 2.8 From data to functions: calibrating a servo"],
  goal: ["为一组实测数据选择函数模型，用最小二乘法确定参数，用残差判断模型的好坏，再用模型的反函数解决实际问题。",
         "Choose a model for measured data, fit it by least squares, judge it by its residuals, and use its inverse to answer a practical question."],
  scenes: [
    { id: "servo", robot: true, name: ["舵机标定", "Servo calibration"], hide: [],
      problem: { title: ["机器人问题：要转到 150°，该发多宽的脉冲？", "Robot problem: what pulse width turns the servo to 150°?"],
                 text: ["手册说舵机的角度与脉宽成线性关系。用 19 组实测数据检验这个说法：拟合几种模型，看哪一种的残差没有规律，再用它反求转到目标角所需的脉宽。",
                        "The datasheet says the angle is linear in the pulse width. Test this on 19 measurements: fit several models, find the one whose residuals show no pattern, then invert it for the pulse width that reaches the target angle."] } },
    { id: "tea", name: ["生活中的例子：一杯热茶", "Everyday example: a cup of tea"], hide: [],
      problem: { title: ["生活中的例子：茶什么时候能喝？", "Everyday example: when is the tea drinkable?"],
                 text: ["85 °C 的茶放在 20 °C 的房间里，每 5 分钟测一次温度。比较直线、多项式和指数模型，用最合适的模型预测茶降到目标温度的时刻。",
                        "Tea at 85 °C cools in a 20 °C room, measured every 5 minutes. Compare a line, polynomials and an exponential, and use the best one to predict when the tea reaches the target temperature."] } },
  ],
  params: [
    { id: "m", name: ["模型：1 一次，2 二次，3 三次，4 指数", "Model: 1 linear, 2 quadratic, 3 cubic, 4 exponential"], min: 1, max: 4, step: 1, value: 4, digits: 0 },
    { id: "y", name: ["目标值（舵机：角度 / °；茶：温度 / °C）", "Target (servo: angle / °; tea: temperature / °C)"], min: 25, max: 165, step: 0.5, value: 120, digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["实测数据", "data"], color: "#1d2327" }, { name: ["模型", "model"], color: "#d62728" }, { name: ["残差", "residuals"], color: "#1f77b4" }],
  tasks: [
    { id: "line", robot: true, text: ["在“舵机标定”场景中选一次模型，读出斜率（°/μs）和残差的均方根。", "In 'Servo calibration' choose the linear model and read the slope (°/μs) and the RMS residual."],
      demo: { scene: "servo", set: { m: 1 }, press: [], wait: 1 } },
    { id: "pattern", robot: true, text: ["找出残差没有明显规律、均方根小于 0.4° 的模型。", "Find a model whose residuals show no clear pattern and whose RMS is below 0.4°."],
      demo: { scene: "servo", set: { m: 3 }, press: [], wait: 1 } },
    { id: "inverse", robot: true, text: ["把目标角设为 150°，用模型反求所需的脉宽，使它与真正需要的脉宽相差小于 3 μs。", "Set the target to 150° and invert the model for the pulse width, within 3 μs of the true one."],
      demo: { scene: "servo", set: { m: 3, y: 150 }, press: [], wait: 1 } },
  ],
  think: ["一次模型的均方根还不到 2°，看上去也不坏。为什么还要看残差图？十次多项式的均方根更小，为什么不用它？", "The linear model's RMS is under 2°, which looks fine. Why look at the residual plot at all? A tenth-degree polynomial has an even smaller RMS; why not use it?"],

  // the data of each scene, exactly as in program 2.8.1 (same seeds, same rounding)
  data(api, s) {
    if (s.d && s.d.scene === api.scene) return s.d;
    let d;
    if (api.scene === "servo") {
      const truth = (p) => 90 + 0.095 * (p - 1500) - 1.5e-8 * (p - 1500) ** 3, rng = api.calc.rng(28), x = [], y = [];
      for (let p = 600; p <= 2400; p += 100) { x.push(p); y.push(Math.round((truth(p) + 0.3 * rng.gauss()) * 10) / 10); }
      d = { x, y, truth, u: (p) => (p - 1500) / 1000, xmin: 500, xmax: 2500, base: 0, xl: api.T("脉宽 p / μs", "pulse width p / μs"),
            yl: api.T("角度 θ / (°)", "angle θ / (°)"), xu: " μs", yu: "°" };
    } else {
      const truth = (t) => 20 + 65 * Math.exp(-t / 22), rng = api.calc.rng(5), x = [], y = [];
      for (let t = 0; t <= 60; t += 5) { x.push(t); y.push(Math.round((truth(t) + 0.3 * rng.gauss()) * 10) / 10); }
      d = { x, y, truth, u: (t) => (t - 30) / 30, xmin: -2, xmax: 65, base: 20, xl: api.T("时间 t / min", "time t / min"),
            yl: api.T("温度 / °C", "temperature / °C"), xu: " min", yu: " °C" };
    }
    d.scene = api.scene; s.d = d; return d;
  },
  solve(A, b) {   // Gaussian elimination with partial pivoting (small systems only)
    const n = b.length, M = A.map((r, i) => r.concat([b[i]]));
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      [M[c], M[p]] = [M[p], M[c]];
      for (let r = c + 1; r < n; r++) { const f = M[r][c] / M[c][c]; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; }
    }
    const x = new Array(n).fill(0);
    for (let r = n - 1; r >= 0; r--) { let t = M[r][n]; for (let k = r + 1; k < n; k++) t -= M[r][k] * x[k]; x[r] = t / M[r][r]; }
    return x;
  },
  polyfit(u, y, deg) {   // least squares by the normal equations; coefficients c0 + c1 u + … + c_deg u^deg
    const n = deg + 1, A = Array.from({ length: n }, () => new Array(n).fill(0)), b = new Array(n).fill(0);
    u.forEach((ui, i) => { for (let r = 0; r < n; r++) { b[r] += Math.pow(ui, r) * y[i]; for (let c = 0; c < n; c++) A[r][c] += Math.pow(ui, r + c); } });
    return this.solve(A, b);
  },
  model(api, s) {   // the fitted model f(x) for the chosen form, cached per scene and model
    const D = this.data(api, s), key = api.scene + "|" + api.p.m;
    if (s.mk === key) return s.M;
    const m = api.p.m;
    let f, text;
    if (m <= 3) {
      const c = this.polyfit(D.x.map(D.u), D.y, m);
      f = (x) => c.reduce((a, ci, k) => a + ci * Math.pow(D.u(x), k), 0);
      text = c.map((ci, k) => api.fmt(ci, 3) + (k ? (k === 1 ? "u" : "u" + "  ²³"[k]) : "")).join(" + ").replace(/\+ -/g, "− ");
      if (api.scene === "servo" && m === 1) s.slope = c[1] / 1000;
    } else {   // exponential: ln(y − base) is linear in x
      const c = this.polyfit(D.x, D.y.map((v) => Math.log(v - D.base)), 1);
      f = (x) => D.base + Math.exp(c[0] + c[1] * x);
      text = (D.base ? D.base + " + " : "") + api.fmt(Math.exp(c[0]), 3) + " e^(" + api.fmt(c[1], 5) + " x)";
    }
    const res = D.y.map((v, i) => v - f(D.x[i]));
    const rms = Math.sqrt(res.reduce((a, r) => a + r * r, 0) / res.length);
    s.mk = key; s.M = { f, text, res, rms, rmax: Math.max(...res.map(Math.abs)) };
    return s.M;
  },
  reset(api, s) { s.d = null; s.mk = null; },
  readouts(api, s) {
    const D = this.data(api, s), M = this.model(api, s), servo = api.scene === "servo";
    const lo = D.x[0], hi = D.x[D.x.length - 1];
    const bis = (f) => { const g = (x) => f(x) - api.p.y; if (g(lo) * g(hi) > 0) return NaN; return api.calc.bisect(g, lo, hi, 1e-9).x; };
    const xf = bis(M.f), xt = bis(D.truth);
    if (servo && api.p.m === 1) api.done("line");
    if (servo && M.rms < 0.4) api.done("pattern");
    if (servo && Math.abs(api.p.y - 150) < 0.26 && Math.abs(xf - xt) < 3) api.done("inverse");
    const names = [api.T("一次", "linear"), api.T("二次", "quadratic"), api.T("三次", "cubic"), api.T("指数", "exponential")];
    const rows = [[["模型", "Model"], names[api.p.m - 1] + (api.p.m <= 3 ? api.T("（u 为标准化的自变量）", " (u: scaled variable)") : "")],
                  [["拟合结果", "Fit"], M.text],
                  [["残差的均方根 / 最大值", "RMS / largest residual"], api.fmt(M.rms, 3) + " / " + api.fmt(M.rmax, 3) + D.yu]];
    if (servo && api.p.m === 1) rows.push([["斜率", "Slope"], api.fmt(s.slope, 5) + " °/μs"]);
    rows.push([[servo ? "转到目标角所需的脉宽（模型 / 真值）" : "降到目标温度的时刻（模型 / 真值）", servo ? "Pulse for the target (model / true)" : "Time to the target (model / true)"],
               (isFinite(xf) ? api.fmt(xf, 1) : "—") + " / " + (isFinite(xt) ? api.fmt(xt, 1) : "—") + D.xu]);
    return rows;
  },
  draw(api, s) {
    const D = this.data(api, s), M = this.model(api, s), w = api.w, h = api.h;
    const red = api.css("--red"), blue = api.css("--blue"), ink = api.css("--ink"), mu = api.css("--muted");
    const ys = D.y.concat([D.truth(D.xmin), D.truth(D.xmax)]);
    const ymin = Math.min(...ys), ymax = Math.max(...ys), pad = (ymax - ymin) * 0.08;
    const gh = (h - 110) * 0.62, rh = (h - 110) * 0.38;
    const G = api.graph({ x: 60, y: 20, w: w - 80, h: gh, xmin: D.xmin, xmax: D.xmax, ymin: ymin - pad, ymax: ymax + pad, ylabel: D.yl });
    G.axes();
    G.fn(M.f, red, 2);
    G.dots(D.x.map((x, i) => [x, D.y[i]]), ink, 3.5);
    G.hline(api.p.y, mu);
    const rmax = Math.max(1, ...M.res.map(Math.abs)) * 1.2;
    const R = api.graph({ x: 60, y: 50 + gh, w: w - 80, h: rh, xmin: D.xmin, xmax: D.xmax, ymin: -rmax, ymax: rmax, xlabel: D.xl,
                          ylabel: api.T("残差", "residual") + " / " + D.yu.trim() });
    R.axes();
    D.x.forEach((x, i) => R.seg(x, 0, x, M.res[i], blue, 2));
    R.dots(D.x.map((x, i) => [x, M.res[i]]), blue, 3);
  },
});
