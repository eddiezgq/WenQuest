// 实验 10.7 差速 AGV 的里程计标定（配 10.7 节）。真实轮半径 r = 74.5 mm、轮距 b = 412 mm（图纸值 75 mm、400 mm）。
// 直线试验：两轮转约 20～30 rad；原地转向试验：两轮反向各转约 15～20 rad（车体约转一圈）。激光跟踪仪测路程（σ = 1 mm）与航向变化（σ = 0.2°）。
// 模型 d = r(φ_R + φ_L)/2，Δθ = k(φ_R − φ_L)，k = r/b，用 1/σ² 加权的最小二乘求 (r, k)，b = r/k；标准差由 (AᵀWA)⁻¹ 与误差传播给出。
WQ.lab({
  title: ["实验 10.7 差速 AGV 的里程计标定", "Lab 10.7 Calibrating a differential-drive AGV's odometry"],
  goal: ["选择直线试验与原地转向试验的次数，用加权最小二乘由测量数据标定轮半径与轮距，读出估计值与标准差；比较图纸参数与标定参数下里程计推算的轨迹。",
         "Choose how many straight and turn-in-place runs to make, calibrate the wheel radius and track width by weighted least squares, and read the estimates and standard deviations; compare odometry with drawing values and with calibrated values."],
  scenes: [
    { id: "calib", robot: true, name: ["标定试验", "Calibration runs"],
      problem: { title: ["机器人问题：AGV 总是“走不够、转不准”", "Robot problem: the AGV falls short and turns wrong"],
                 text: ["轮胎磨损后半径变小，轮距也和图纸有出入。用激光跟踪仪记录几次直线行驶和原地转向，求出真实的 r 和 b。试验做几次、各做多少才够？",
                        "Worn tyres shrink the radius, and the track width differs from the drawing. A laser tracker records some straight runs and turns in place; find the true r and b. How many runs of each kind are enough?"] } },
    { id: "square", robot: true, name: ["检验：走正方形", "Check: drive a square"],
      problem: { title: ["标定好了吗？走一个正方形", "Is it calibrated? Drive a square"],
                 text: ["控制器按图纸参数规划“走 2 m、左转 90°”四次。小车真实走出的轨迹不闭合；用两组参数由编码器推算轨迹，看哪一组与真实轨迹一致。",
                        "The controller plans 'drive 2 m, turn left 90°' four times with the drawing values. The true path does not close; compute odometry with both parameter sets and see which agrees with the truth."] } },
  ],
  params: [
    { id: "nl", name: ["直线试验次数", "Straight runs"], min: 0, max: 10, step: 1, value: 2, digits: 0 },
    { id: "nt", name: ["原地转向试验次数", "Turn-in-place runs"], min: 0, max: 10, step: 1, value: 0, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "noturn", robot: true, text: ["只做直线试验（至少 3 次、转向 0 次），读出轮距 b 的标准差，说明为什么定不出轮距。", "Make only straight runs (at least 3, no turns); read the standard deviation of b and explain why the track width is not determined."],
      demo: { scene: "calib", set: { nl: 4, nt: 0 }, press: [] } },
    { id: "plan", robot: true, text: ["总共不超过 9 次试验，使 r 的标准差小于 0.02 mm、b 的标准差小于 0.16 mm。", "With at most 9 runs in all, make the standard deviation of r below 0.02 mm and that of b below 0.16 mm."],
      demo: { scene: "calib", set: { nl: 5, nt: 4 }, press: [] } },
    { id: "square", robot: true, text: ["在检验场景中，用标定结果推算的终点与真实终点相差不到 5 mm。", "In the check scene, make the odometry end point from the calibrated values within 5 mm of the true end point."],
      demo: { scene: "square", set: { nl: 5, nt: 4 }, press: [] } },
  ],
  think: ["原地转向试验对估计 r 几乎没有帮助，直线试验对估计 b 也几乎没有帮助。从 AᵀWA 的形状解释这一点。",
          "Turns in place hardly help estimate r, and straight runs hardly help estimate b. Explain this from the shape of AᵀWA."],

  r: 0.0745, b: 0.412, rn: 0.075, bn: 0.400, sd: 0.001, sth: 0.2 * Math.PI / 180,
  runs(api, nl, nt) {   // the i-th run of each kind is always the same, so adding runs only adds data
    const R = api.calc.rng(1071), T = api.calc.rng(1072), out = [];
    for (let i = 0; i < nl; i++) {
      const ph = 20 + 10 * R.u(), pr = ph * (1 + 0.002 * R.gauss()), pl = ph;
      out.push([pr, pl, this.r * (pr + pl) / 2 + this.sd * R.gauss(), this.r * (pr - pl) / this.b + this.sth * R.gauss()]);
    }
    for (let i = 0; i < nt; i++) {
      const ph = (15 + 5 * T.u()) * (i % 2 ? -1 : 1), pr = ph, pl = -ph * (1 + 0.002 * T.gauss());
      out.push([pr, pl, this.r * (pr + pl) / 2 + this.sd * T.gauss(), this.r * (pr - pl) / this.b + this.sth * T.gauss()]);
    }
    return out;
  },
  calib(data) {   // AᵀWA is diagonal here: each measurement row has a single nonzero entry
    let a11 = 0, a22 = 0, y1 = 0, y2 = 0;
    for (const [pr, pl, d, th] of data) {
      const s = (pr + pl) / 2, u = pr - pl;
      a11 += s * s / this.sd ** 2; y1 += s * d / this.sd ** 2;
      a22 += u * u / this.sth ** 2; y2 += u * th / this.sth ** 2;
    }
    if (a11 <= 0 || a22 <= 0) return null;
    const r = y1 / a11, k = y2 / a22, vr = 1 / a11, vk = 1 / a22;
    return { r, k, b: r / k, sr: Math.sqrt(vr), sb: Math.sqrt(vr / k ** 2 + (r / k ** 2) ** 2 * vk) };
  },
  path(r, b) {   // the square planned with the drawing values, integrated with (r, b)
    let x = 0, y = 0, th = 0; const pts = [[0, 0]];
    for (let s = 0; s < 4; s++) {
      for (let i = 0; i < 100; i++) { const p = 2 / this.rn / 100, d = r * p; x += d * Math.cos(th); y += d * Math.sin(th); pts.push([x, y]); }
      const a = (Math.PI / 2) * (this.bn / 2) / this.rn / 50;
      for (let i = 0; i < 50; i++) { const dth = r * 2 * a / b; th += dth; pts.push([x, y]); }
    }
    return pts;
  },
  reset(api, s) {
    s.data = this.runs(api, api.p.nl, api.p.nt);
    s.c = this.calib(s.data);
  },
  readouts(api, s) {
    const c = s.c, p = api.p, rows = [[["试验数据", "Runs"], api.T(`直线 ${p.nl} 次，转向 ${p.nt} 次，共 ${2 * (p.nl + p.nt)} 个方程`, `${p.nl} straight, ${p.nt} turns, ${2 * (p.nl + p.nt)} equations`)]];
    if (!c) return rows.concat([[["标定结果", "Result"], api.T("数据不足：至少做一次试验", "not enough data: make at least one run")]]);
    const nb = c.sb > 1000 ? api.T("（极大，定不出来）", " (huge: undetermined)") : "";
    if (api.scene === "calib" && p.nt === 0 && p.nl >= 3) api.done("noturn");
    if (api.scene === "calib" && p.nl + p.nt <= 9 && c.sr * 1000 < 0.02 && c.sb * 1000 < 0.16) api.done("plan");
    const out = rows.concat([[["轮半径 r̂ ± 标准差", "r̂ ± std"], api.fmt(c.r * 1000, 3) + " ± " + api.fmt(c.sr * 1000, 3) + " mm"],
                             [["轮距 b̂ ± 标准差", "b̂ ± std"], (c.sb > 1000 ? "—" : api.fmt(c.b * 1000, 2)) + " ± " + api.fmt(c.sb * 1000, 2) + " mm" + nb],
                             [["真实值（仿真中已知）", "True values (known in simulation)"], "r = 74.500 mm, b = 412.00 mm"],
                             [["图纸值", "Drawing values"], "r = 75 mm, b = 400 mm"]]);
    if (api.scene !== "square") return out;
    const T = this.path(this.r, this.b), N = this.path(this.rn, this.bn), C = this.path(c.r, c.b);
    const e = (A) => Math.hypot(A[A.length - 1][0] - T[T.length - 1][0], A[A.length - 1][1] - T[T.length - 1][1]) * 1000;
    if (e(C) < 5) api.done("square");
    return out.concat([[["图纸参数推算的终点误差", "End error, drawing values"], api.fmt(e(N), 1) + " mm"],
                       [["标定参数推算的终点误差", "End error, calibrated values"], api.fmt(e(C), 1) + " mm"]]);
  },
  draw(api, s) {
    const { w, h } = api, ink = api.css("--ink"), blue = api.css("--blue"), red = api.css("--red"), muted = api.css("--muted"), c = s.c;
    if (api.scene === "calib") {
      // residuals of the distance and heading measurements with the fitted (r, k): they should look like noise
      const pts = s.data;
      api.label(api.T("每次试验的残差（测量 − 模型）：路程（mm，左）与航向（°，右）", "Residual of each run (measured − model): distance (mm, left) and heading (°, right)"), 16, 22, ink, 13);
      if (!c || !pts.length) return;
      const half = (w - 60) / 2;
      [[0, (q) => (q[2] - c.r * (q[0] + q[1]) / 2) * 1000, 4, "mm"], [1, (q) => (q[3] - c.k * (q[0] - q[1])) * 180 / Math.PI, 0.8, "°"]].forEach(([k, f, lim, u]) => {
        const x0 = 30 + k * (half + 20), P = api.plot(x0, 40, half - 10, h - 90, [{ pts: [[0, 0], [pts.length + 1, 0]], color: muted }],
                                                       { xmin: 0, xmax: Math.max(pts.length + 1, 4), ymin: -lim, ymax: lim, xlabel: api.T("试验编号", "run"), ylabel: u });
        pts.forEach((q, i) => api.circle(P.X(i + 1), P.Y(Math.max(-lim, Math.min(lim, f(q)))), 5, i < api.p.nl ? blue : red, ink));
      });
      api.label(api.T("蓝：直线试验  红：转向试验", "blue: straight  red: turn"), 16, h - 14, ink, 12);
      return;
    }
    if (!c) return;
    const T = this.path(this.r, this.b), N = this.path(this.rn, this.bn), C = this.path(c.r, c.b);
    const pl = api.plane({ cx: w * 0.32, cy: h * 0.8, s: Math.min(w, h) * 0.3, w, h });
    const poly = (pts, col, wd, dash) => {   // an open polyline (plane.curve would close the path)
      const g = api.ctx; g.beginPath(); pts.forEach((q, i) => { const [x, y] = pl.X(q[0], q[1]); if (i) g.lineTo(x, y); else g.moveTo(x, y); });
      g.strokeStyle = col; g.lineWidth = wd; g.setLineDash(dash || []); g.stroke(); g.setLineDash([]);
    };
    poly(T, ink, 3); poly(N, blue, 2, [7, 5]); poly(C, red, 1.5);
    const [ex, ey] = pl.X(...T[T.length - 1]), [sx, sy] = pl.X(0, 0);
    api.circle(sx, sy, 5, ink); api.label(api.T("起点", "start"), sx + 8, sy + 16, ink, 12);
    api.circle(ex, ey, 4, red, ink); api.label(api.T("真实终点", "true end"), ex - 70, ey - 8, ink, 12);
    api.label(api.T("黑：真实轨迹  蓝虚线：图纸参数推算  红：标定参数推算", "black: true path  blue dashed: drawing values  red: calibrated"), 16, 22, ink, 13);
  },
});
