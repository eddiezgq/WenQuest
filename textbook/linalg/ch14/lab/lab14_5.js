// 实验 14.5 AGV 定位误差的置信椭圆（配 14.5 节）。位置误差的协方差 Σ = [[σx², ρσxσy], [ρσxσy, σy²]]（cm²），
// 95% 置信椭圆 xᵀΣ⁻¹x = 5.991：主轴沿 Σ 的特征向量，半轴 √(5.991 λᵢ)。1000 个误差样本 = L z，L 是 Σ 的乔列斯基因子，z 为固定种子的标准正态。
WQ.lab({
  title: ["实验 14.5 定位误差的置信椭圆", "Lab 14.5 Confidence ellipse of a position error"],
  goal: ["改变 x、y 方向的标准差和相关系数，观察协方差矩阵的特征向量怎样决定误差椭圆的主轴、特征值怎样决定半轴；数一数落在 95% 椭圆内的样本。",
         "Change the standard deviations in x and y and their correlation; see how the eigenvectors of the covariance matrix set the axes of the error ellipse and the eigenvalues its semi-axes; count the samples inside the 95% ellipse."],
  scenes: [
    { id: "agv", robot: true, name: ["AGV 定位", "AGV localization"],
      problem: { title: ["AGV 在哪个方向最不确定？", "In which direction is the AGV least certain?"],
                 text: ["激光雷达与里程计融合后，AGV 位置的误差用协方差矩阵 Σ 描述。沿走廊行驶时，横向有墙壁约束、误差小，纵向缺少特征、误差大，而且走廊未必与地图坐标轴平行。",
                        "After fusing lidar and odometry, the AGV's position error is described by a covariance matrix Σ. In a corridor the walls pin down the sideways error while the error along the corridor stays large, and the corridor need not be parallel to the map axes."] } },
  ],
  params: [
    { id: "sx", name: ["x 方向标准差 σx", "Standard deviation σx"], min: 0.5, max: 4, step: 0.1, value: 2, unit: "cm", digits: 1 },
    { id: "sy", name: ["y 方向标准差 σy", "Standard deviation σy"], min: 0.5, max: 4, step: 0.1, value: 1.7, unit: "cm", digits: 1 },
    { id: "rho", name: ["相关系数 ρ", "Correlation ρ"], min: -0.95, max: 0.95, step: 0.05, value: 0.6, digits: 2 },
  ],
  buttons: [],
  tasks: [
    { id: "align", robot: true, text: ["让椭圆的主轴与坐标轴平行，且 x 方向更不确定。这时协方差矩阵有什么特点？", "Make the ellipse's axes parallel to the coordinate axes with x the less certain direction. What does the covariance matrix look like then?"],
      demo: { scene: "agv", set: { sx: 3, sy: 1, rho: 0 }, press: [] } },
    { id: "circle", robot: true, text: ["让误差在各个方向一样大：两个特征值之比小于 1.02（圆）。", "Make the error the same in every direction: eigenvalue ratio below 1.02 (a circle)."],
      demo: { scene: "agv", set: { sx: 2, sy: 2, rho: 0 }, press: [] } },
    { id: "corr", robot: true, text: ["模拟沿 45° 方向的走廊：σx = σy，调 ρ 使长短半轴之比超过 5，读出长轴方向。", "Model a corridor at 45°: σx = σy, adjust ρ until the semi-axis ratio exceeds 5, and read the long axis direction."],
      demo: { scene: "agv", set: { sx: 2, sy: 2, rho: 0.95 }, press: [] } },
  ],
  think: ["σx = σy 时，无论 ρ 取多少（ρ ≠ 0），主轴都沿 45° 和 135° 方向。用 Σ 的特征向量说明原因。", "With σx = σy the axes lie along 45° and 135° whatever ρ is (ρ ≠ 0). Explain with the eigenvectors of Σ."],

  c95: 5.991464547107982,
  reset(api, s) {
    const sx = api.p.sx, sy = api.p.sy, r = api.p.rho;
    const a = sx * sx, b = r * sx * sy, c = sy * sy;
    s.S = [[a, b], [b, c]];
    const tr = a + c, disc = Math.sqrt((a - c) ** 2 / 4 + b * b);
    s.l1 = tr / 2 + disc; s.l2 = tr / 2 - disc;
    s.ang = 0.5 * Math.atan2(2 * b, a - c);       // direction of the larger eigenvalue
    if (!this.z) { const g = api.calc.rng(145); this.z = Array.from({ length: 1000 }, () => [g.gauss(), g.gauss()]); }
    const L11 = Math.sqrt(a), L21 = b / L11, L22 = Math.sqrt(Math.max(c - L21 * L21, 1e-12));
    s.X = this.z.map(([u, v]) => [L11 * u, L21 * u + L22 * v]);
    const det = a * c - b * b;
    s.inside = s.X.filter(([x, y]) => (c * x * x - 2 * b * x * y + a * y * y) / det <= this.c95).length;
  },
  readouts(api, s) {
    if (!s.S) return [];
    const f = api.fmt, deg = ((s.ang * 180 / Math.PI) % 180 + 180) % 180;
    const tilt = Math.min(deg, 180 - deg);
    if (Math.abs(s.S[0][1]) < 1e-12 && s.S[0][0] > s.S[1][1]) api.done("align");
    if (s.l1 / s.l2 < 1.02) api.done("circle");
    if (Math.abs(api.p.sx - api.p.sy) < 1e-9 && api.p.rho > 0 && Math.sqrt(s.l1 / s.l2) > 5) api.done("corr");
    return [[["协方差 Σ / cm²", "Covariance Σ / cm²"], "[[" + f(s.S[0][0], 2) + ", " + f(s.S[0][1], 2) + "], [" + f(s.S[1][0], 2) + ", " + f(s.S[1][1], 2) + "]]"],
            [["最大、最小特征值 / cm²", "Largest, smallest eigenvalue / cm²"], f(s.l1, 3) + ", " + f(s.l2, 3)],
            [["主方向的标准差 / cm", "Standard deviation along the axes / cm"], f(Math.sqrt(s.l1), 3) + ", " + f(Math.sqrt(s.l2), 3)],
            [["长轴方向（与 x 轴的夹角）", "Long axis (angle from x)"], f(deg, 1) + "°"],
            [["95% 椭圆的半轴 / cm", "Semi-axes of the 95% ellipse / cm"], f(Math.sqrt(this.c95 * s.l1), 2) + ", " + f(Math.sqrt(this.c95 * s.l2), 2)],
            [["长短半轴之比", "Semi-axis ratio"], f(Math.sqrt(s.l1 / s.l2), 2)],
            [["1000 个样本中落在椭圆内的", "Samples inside (of 1000)"], s.inside + "（" + f(s.inside / 10, 1) + "%）"]];
  },
  draw(api, s) {
    if (!s.S) return;
    const { w, h } = api, mu = api.css("--muted"), cx = w / 2, cy = h / 2, R = Math.max(11, 1.1 * Math.sqrt(this.c95 * s.l1)), sc = Math.min(w, h) / 2 / R;
    api.line(10, cy, w - 10, cy, mu, 1); api.line(cx, 10, cx, h - 10, mu, 1);
    const st = R > 16 ? 4 : 2; for (let k = -Math.floor(R / st) * st; k <= R; k += st) { if (k) { api.label(String(k), cx + k * sc, cy + 14, mu, 10, "center"); } }
    const dot = api.css("--blue");
    api.ctx.globalAlpha = 0.35;
    s.X.forEach(([x, y]) => api.circle(cx + sc * x, cy - sc * y, 1.6, dot, null));
    api.ctx.globalAlpha = 1;
    const a = s.ang, A = Math.sqrt(this.c95 * s.l1), B = Math.sqrt(this.c95 * s.l2), c = api.ctx;
    c.beginPath();
    for (let k = 0; k <= 120; k++) { const t = 2 * Math.PI * k / 120, u = A * Math.cos(t), v = B * Math.sin(t);
      const x = cx + sc * (u * Math.cos(a) - v * Math.sin(a)), y = cy - sc * (u * Math.sin(a) + v * Math.cos(a)); if (k) c.lineTo(x, y); else c.moveTo(x, y); }
    c.strokeStyle = api.css("--amber"); c.lineWidth = 2.5; c.stroke();
    api.arrow(cx, cy, cx + sc * A * Math.cos(a), cy - sc * A * Math.sin(a), api.css("--green"), 2.5);
    api.arrow(cx, cy, cx - sc * B * Math.sin(a), cy - sc * B * Math.cos(a), api.css("--red"), 2.5);
    api.label(api.T("单位：cm；黄：95% 置信椭圆；绿、红：主轴（半轴长）", "units: cm; amber: 95% ellipse; green, red: principal semi-axes"), 12, 20, mu, 12);
  },
});
