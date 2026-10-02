// 实验 2.5 TCP 标定与直线拟合（配 2.5 节）。平面 TCP 标定：R(φᵢ) t − c = −pᵢ，按正规方程求最小二乘解。
// 真值 t = (120, 35) mm（工具尖端在法兰坐标系中），c = (650, 150) mm（顶针）。随机误差用固定种子的伪随机数，结果可重复。
WQ.lab({
  title: ["实验 2.5 最小二乘：TCP 标定与直线拟合", "Lab 2.5 Least squares: TCP calibration and line fitting"],
  goal: ["改变接触次数、姿态范围和测量误差，看最小二乘标定的精度；手动拟合直线，体会“残差平方和最小”。",
         "Change the number of touches, the spread of poses and the measurement error to see how accurate least-squares calibration is; fit a line by hand and feel what “least sum of squares” means."],
  scenes: [
    { id: "tcp", robot: true, name: ["TCP 标定", "TCP calibration"], hide: ["k", "b0"],
      problem: { title: ["机器人问题：工具尖端在哪里", "Robot problem: where is the tool tip?"],
                 text: ["以 N 个姿态让工具尖端碰同一个顶针，每次得到两个方程 R(φᵢ)t − c = −pᵢ。未知数 t、c 共 4 个。",
                        "Touch one pin from N poses; each touch gives two equations R(φᵢ)t − c = −pᵢ. There are 4 unknowns, t and c."] } },
    { id: "scale", name: ["弹簧秤", "Spring scale"], hide: ["n", "spread", "noise"],
      problem: { title: ["生活中的例子：拟合一条直线", "Everyday example: fitting a line"],
                 text: ["砝码 0～5 kg，伸长 0.3、10.2、19.6、30.4、40.1、49.6 mm。拖动斜率和截距，让残差平方和尽量小。",
                        "Masses 0–5 kg, extensions 0.3, 10.2, 19.6, 30.4, 40.1, 49.6 mm. Drag the slope and intercept to make the sum of squared residuals small."] } },
  ],
  params: [
    { id: "n", name: ["接触次数 N", "Number of touches N"], min: 2, max: 8, step: 1, value: 5, unit: "", digits: 0 },
    { id: "spread", name: ["姿态转角范围", "Spread of pose angles"], min: 0, max: 180, step: 10, value: 120, unit: "°", digits: 0 },
    { id: "noise", name: ["测量误差（标准差）", "Measurement error (std)"], min: 0, max: 1, step: 0.1, value: 0.3, unit: "mm", digits: 1 },
    { id: "k", name: ["斜率 k", "Slope k"], min: 8, max: 12, step: 0.01, value: 10.5, unit: "mm/kg", digits: 2 },
    { id: "b0", name: ["截距 b₀", "Intercept b₀"], min: -2, max: 2, step: 0.05, value: -1, unit: "mm", digits: 2 },
  ],
  buttons: [{ id: "measure", name: ["接触并求解", "Touch and solve"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "exact", robot: true, text: ["无测量误差、两次接触：恰好解出真值。", "No measurement error, two touches: the solution is exact."],
      demo: { scene: "tcp", set: { n: 2, spread: 120, noise: 0 }, press: ["measure"], wait: 2 } },
    { id: "good", robot: true, text: ["测量误差 0.5 mm 时，使工具尖端的标定误差小于 0.3 mm。", "With 0.5 mm measurement error, make the tool-tip error smaller than 0.3 mm."],
      demo: { scene: "tcp", set: { n: 8, spread: 180, noise: 0.5 }, press: ["measure"], wait: 2 } },
    { id: "line", text: ["手动调直线，使残差平方和不超过最小值的 1.1 倍。", "Adjust the line by hand until the sum of squares is within 1.1 times the minimum."],
      demo: { scene: "scale", set: { k: 9.91, b0: 0.25 }, press: [] } },
  ],
  think: ["所有姿态的转角都相同时（范围 0°），为什么无法标定？从 A 的各列来解释。", "Why does calibration fail when all poses have the same angle (spread 0°)? Explain with the columns of A."],

  T0: [120, 35], C0: [650, 150],
  M: [0, 1, 2, 3, 4, 5], Y: [0.3, 10.2, 19.6, 30.4, 40.1, 49.6],
  rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; },
  gauss(r) { const u = Math.max(1e-12, r()), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  solve(M, b) {   // 高斯消元（选主元）
    const n = b.length, A = M.map((r, i) => [...r, b[i]]);
    for (let i = 0; i < n; i++) {
      let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(A[j][i]) > Math.abs(A[p][i])) p = j;
      [A[i], A[p]] = [A[p], A[i]];
      if (Math.abs(A[i][i]) < 1e-12) return null;
      for (let j = i + 1; j < n; j++) { const f = A[j][i] / A[i][i]; for (let k = i; k <= n; k++) A[j][k] -= f * A[i][k]; }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let s = A[i][n]; for (let k = i + 1; k < n; k++) s -= A[i][k] * x[k]; x[i] = s / A[i][i]; }
    return x;
  },
  calibrate(api, s) {
    const N = api.p.n, sp = api.p.spread, sg = api.p.noise;
    const r = this.rng(1000 * N + 7 * sp + Math.round(sg * 10) + 9973 * (s.trial || 0));
    const poses = [];
    for (let i = 0; i < N; i++) {
      const phi = (20 + sp * (N > 1 ? i / (N - 1) - 0.5 : 0)) * Math.PI / 180, c = Math.cos(phi), sn = Math.sin(phi);
      const Rt = [c * this.T0[0] - sn * this.T0[1], sn * this.T0[0] + c * this.T0[1]];
      poses.push({ phi, p: [this.C0[0] - Rt[0] + sg * this.gauss(r), this.C0[1] - Rt[1] + sg * this.gauss(r)] });
    }
    const AtA = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], Atb = [0, 0, 0, 0];
    poses.forEach(({ phi, p }) => {
      const c = Math.cos(phi), sn = Math.sin(phi), rows = [[c, -sn, -1, 0], [sn, c, 0, -1]], b = [-p[0], -p[1]];
      rows.forEach((row, k) => { for (let i = 0; i < 4; i++) { Atb[i] += row[i] * b[k]; for (let j = 0; j < 4; j++) AtA[i][j] += row[i] * row[j]; } });
    });
    const x = this.solve(AtA, Atb);
    s.poses = poses; s.x = x; s.trial = (s.trial || 0) + 1;
    if (!x) { s.err = null; return; }
    s.err = Math.hypot(x[0] - this.T0[0], x[1] - this.T0[1]);
    let ss = 0; poses.forEach(({ phi, p }) => { const c = Math.cos(phi), sn = Math.sin(phi);
      ss += (c * x[0] - sn * x[1] - x[2] + p[0]) ** 2 + (sn * x[0] + c * x[1] - x[3] + p[1]) ** 2; });
    s.rms = Math.sqrt(ss / (2 * N));
    if (N === 2 && sg === 0 && s.err < 1e-6) api.done("exact");
    if (Math.abs(sg - 0.5) < 1e-9 && s.err < 0.3) api.done("good");
  },
  sse(k, b0) { return this.M.reduce((a, m, i) => a + (this.Y[i] - k * m - b0) ** 2, 0); },
  fit() { const n = 6, sx = 15, sy = this.Y.reduce((a, b) => a + b, 0), sxx = 55, sxy = this.M.reduce((a, m, i) => a + m * this.Y[i], 0);
    const k = (n * sxy - sx * sy) / (n * sxx - sx * sx); return [k, (sy - k * sx) / n]; },
  reset(api, s) { s.poses = null; s.x = null; s.trial = 0; },
  action(id, api, s) { if (id === "measure" && api.scene === "tcp") this.calibrate(api, s); },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "scale") {
      const [k, b] = this.fit(), mn = this.sse(k, b), cur = this.sse(api.p.k, api.p.b0);
      if (cur <= 1.1 * mn) api.done("line");
      return [[["残差平方和", "sum of squared residuals"], f(cur, 4) + " mm²"], [["最小值（最小二乘）", "minimum (least squares)"], f(mn, 4) + " mm²"],
              [["比值", "ratio"], f(cur / mn, 3)], [["最小二乘的 k、b₀", "least-squares k, b₀"], `${f(k, 3)} mm/kg, ${f(b, 3)} mm`]];
    }
    if (!s.x) return [[["状态", "status"], api.T(s.poses ? "无法求解：A 的各列线性相关" : "按“接触并求解”", s.poses ? "cannot solve: columns of A dependent" : "press “Touch and solve”")],
                      [["方程个数 / 未知数", "equations / unknowns"], `${2 * api.p.n} / 4`]];
    return [[["标定出的 t", "calibrated t"], `(${f(s.x[0], 3)}, ${f(s.x[1], 3)}) mm`], [["标定出的 c", "calibrated c"], `(${f(s.x[2], 2)}, ${f(s.x[3], 2)}) mm`],
            [["t 的误差", "error of t"], f(s.err, 3) + " mm"], [["残差均方根", "RMS residual"], f(s.rms, 3) + " mm"],
            [["方程个数 / 未知数", "equations / unknowns"], `${2 * api.p.n} / 4`]];
  },
  draw(api, s) {
    const { w, h } = api;
    api.grid(w, h, 40);
    if (api.scene === "scale") {
      const ox = w * 0.1, oy = h * 0.88, sx = w * 0.8 / 5.5, sy = h * 0.78 / 55, P = (m, y) => [ox + m * sx, oy - y * sy];
      api.line(ox, oy, ox + 5.5 * sx, oy, api.css("--ink"), 1.5); api.line(ox, oy, ox, oy - 55 * sy, api.css("--ink"), 1.5);
      api.label("m / kg", ox + 5.5 * sx, oy + 16, api.css("--muted"), 12, "right"); api.label("y / mm", ox + 6, oy - 55 * sy + 6, api.css("--muted"), 12);
      api.line(...P(-0.1, -0.1 * api.p.k + api.p.b0), ...P(5.4, 5.4 * api.p.k + api.p.b0), api.css("--amber"), 2.5);
      this.M.forEach((m, i) => { const yl = api.p.k * m + api.p.b0, d = (this.Y[i] - yl) * 10;   // 残差放大 10 倍画出
        api.line(...P(m, yl), ...P(m, yl + d), api.css("--red"), 3); api.circle(...P(m, this.Y[i]), 4, api.css("--ink")); });
      api.label(api.T("红：残差（放大 10 倍画出）", "red: residuals (drawn 10× larger)"), 12, 16, api.css("--red"), 12);
      return;
    }
    const k = Math.min(w, h) * 0.36 / 125, X = (x, y) => [w * 0.5 + k * (x - this.C0[0]), h * 0.5 - k * (y - this.C0[1])];   // 以顶针为中心
    const pin = X(...this.C0);
    api.circle(...pin, 6, api.css("--ink")); api.label(api.T("顶针 c", "pin c"), pin[0] + 10, pin[1] + 14, api.css("--ink"), 13);
    (s.poses || []).forEach(({ phi, p }) => {
      const c = Math.cos(phi), sn = Math.sin(phi), P0 = X(...p), corner = [p[0] + c * this.T0[0], p[1] + sn * this.T0[0]];
      api.line(...P0, ...X(...corner), api.css("--amber"), 4); api.line(...X(...corner), ...pin, api.css("--amber"), 4);
      api.circle(...P0, 7, api.css("--muted"));
      api.arrow(...P0, ...X(p[0] + 30 * c, p[1] + 30 * sn), api.css("--red"), 2); api.arrow(...P0, ...X(p[0] - 30 * sn, p[1] + 30 * c), api.css("--green"), 2);
    });
    if (s.x) { const q = X(s.x[2], s.x[3]); api.circle(...q, 4, api.css("--red")); }
    if (!s.poses) api.label(api.T("设置参数后按“接触并求解”", "set the parameters, then press “Touch and solve”"), w / 2, h / 2, api.css("--muted"), 14, "center");
  },
});
