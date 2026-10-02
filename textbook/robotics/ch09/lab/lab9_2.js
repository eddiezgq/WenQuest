// 实验 9.2 不确定性椭圆（配 9.2 节）。平面 2R 臂取 UR5e 的大臂与小臂，L = (0.425, 0.392) m。
// 线性化：Σp = J Σθ Jᵀ（式 (9.2.12)），J 为式 (2.1.9)；95% 椭圆 c = √(−2 ln 0.05)（定理 9.2.4）。
// 蒙特卡洛：按“开始”逐批抽取关节角（固定种子），用正运动学算末端，统计样本标准差和均值偏移。
// 激光笔：光点在墙上的偏移 = 距离 × 手的转角误差 + 手的平移误差，二者独立，方差相加（式 (9.2.13)）。
WQ.lab({
  title: ["实验 9.2 不确定性椭圆", "Lab 9.2 The uncertainty ellipse"],
  goal: ["由关节角的误差求末端位置的协方差矩阵和不确定性椭圆，用蒙特卡洛模拟核对，并找出线性化失效的条件。",
         "Propagate joint-angle errors to the tip covariance and uncertainty ellipse, check by Monte Carlo, and find where linearization fails."],
  scenes: [
    { id: "arm", robot: true, name: ["平面 2R 臂（UR5e 侧视）", "Planar 2R arm (UR5e side view)"], hide: ["d", "hand"],
      problem: { title: ["机器人问题：关节角差 0.1°，末端差多少", "Robot problem: 0.1° on the joints, how much at the tip"],
                 text: ["编码器、背隙和连杆变形使关节角有小的随机误差。末端位置的误差有多大、朝哪个方向？",
                        "Encoders, backlash and link bending give the joint angles small random errors. How large is the tip error, and in which direction?"] } },
    { id: "laser", name: ["手持激光笔照墙", "A hand-held laser pointer"], hide: ["t2", "s2", "mag"],
      params: { t1: { min: -20, max: 20, step: 1, value: 0 }, s1: { min: 0, max: 2, step: 0.05, value: 0.5 } },
      problem: { title: ["生活中的例子：光点为什么在墙上晃", "Everyday example: why the dot dances on the wall"],
                 text: ["手腕抖一点点，远处墙上的光点就晃得很厉害；手的平移则与距离无关。",
                        "A tiny wrist tremor moves a distant dot a lot; a shift of the hand does not grow with distance."] } },
  ],
  params: [
    { id: "t1", name: ["关节角 θ₁（激光笔：光束方向）", "Joint θ₁ (laser: beam direction)"], min: -90, max: 180, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "t2", name: ["关节角 θ₂", "Joint θ₂"], min: -170, max: 170, step: 1, value: 60, unit: "°", digits: 0 },
    { id: "s1", name: ["θ₁ 的标准差（激光笔：手的转角误差）", "Std of θ₁ (laser: hand angle error)"], min: 0, max: 10, step: 0.05, value: 0.1, unit: "°", digits: 2 },
    { id: "s2", name: ["θ₂ 的标准差", "Std of θ₂"], min: 0, max: 10, step: 0.05, value: 0.1, unit: "°", digits: 2 },
    { id: "mag", name: ["椭圆放大倍数", "Ellipse magnification"], min: 1, max: 300, step: 1, value: 100, unit: "×", digits: 0 },
    { id: "d", name: ["到墙的距离", "Distance to the wall"], min: 0.5, max: 10, step: 0.5, value: 5, unit: "m", digits: 1 },
    { id: "hand", name: ["手的平移误差（标准差）", "Hand shift (std)"], min: 0, max: 20, step: 1, value: 0, unit: "mm", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始蒙特卡洛", "Run Monte Carlo"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 9.2.3：θ = (30°, 60°)，两个标准差都为 0.1°，蒙特卡洛 2000 次以上，两种方法的 σx 相差不到 5%。", "Example 9.2.3: θ = (30°, 60°), both stds 0.1°, at least 2000 Monte Carlo runs; the two σx agree within 5%."],
      demo: { scene: "arm", set: { t1: 30, t2: 60, s1: 0.1, s2: 0.1, mag: 100 }, press: ["start"], wait: 6 } },
    { id: "flat", robot: true, text: ["把手臂接近伸直，使椭圆长短轴之比超过 20。", "Nearly straighten the arm so the ellipse axis ratio exceeds 20."],
      demo: { scene: "arm", set: { t1: 30, t2: 8, s1: 0.1, s2: 0.1 }, press: [], wait: 1 } },
    { id: "big", robot: true, text: ["两个标准差都加大到 8°，运行蒙特卡洛，观察末端均值偏离 f(μ) 超过 5 mm。", "Raise both stds to 8°, run Monte Carlo, and see the mean tip move more than 5 mm from f(μ)."],
      demo: { scene: "arm", set: { t1: 30, t2: 60, s1: 8, s2: 8, mag: 1 }, press: ["start"], wait: 6 } },
    { id: "laser", text: ["激光笔：手抖 0.5°、距墙 5 m、手不平移，读出光点的标准差。", "Laser: 0.5° tremor, 5 m to the wall, no hand shift; read the dot's standard deviation."],
      demo: { scene: "laser", set: { t1: 0, s1: 0.5, d: 5, hand: 0 }, press: ["start"], wait: 5 } },
  ],
  think: ["二维的 1 倍椭圆只包含约 39% 的点，为什么比一维 ±σ 的 68% 少？手臂伸直时，为什么沿手臂方向几乎没有误差？",
          "Why does the 2-D 1σ ellipse hold only about 39% of the points, fewer than 68% in 1-D? Why is there almost no error along a straight arm?"],

  L: [0.425, 0.392],
  C95: Math.sqrt(-2 * Math.log(0.05)),
  rad: Math.PI / 180,
  fk(t1, t2) { const L = this.L; return [L[0] * Math.cos(t1) + L[1] * Math.cos(t1 + t2), L[0] * Math.sin(t1) + L[1] * Math.sin(t1 + t2)]; },
  jac(t1, t2) { const L = this.L, s1 = Math.sin(t1), c1 = Math.cos(t1), s12 = Math.sin(t1 + t2), c12 = Math.cos(t1 + t2);
    return [[-L[0] * s1 - L[1] * s12, -L[1] * s12], [L[0] * c1 + L[1] * c12, L[1] * c12]]; },
  gauss(s) {
    s.seed = (s.seed * 1103515245 + 12345) % 2147483648; const u1 = s.seed / 2147483648 + 1e-12;
    s.seed = (s.seed * 1103515245 + 12345) % 2147483648; const u2 = s.seed / 2147483648;
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  },
  // 线性化的协方差矩阵（m²）、特征值与长轴方向
  lin(api) {
    const r = this.rad, J = this.jac(api.p.t1 * r, api.p.t2 * r), a = (api.p.s1 * r) ** 2, b = (api.p.s2 * r) ** 2;
    const S = [[J[0][0] ** 2 * a + J[0][1] ** 2 * b, J[0][0] * J[1][0] * a + J[0][1] * J[1][1] * b], [0, J[1][0] ** 2 * a + J[1][1] ** 2 * b]];
    S[1][0] = S[0][1];
    const tr = S[0][0] + S[1][1], det = S[0][0] * S[1][1] - S[0][1] ** 2, q = Math.sqrt(Math.max(0, tr * tr / 4 - det));
    const l1 = tr / 2 + q, l2 = Math.max(0, tr / 2 - q), ang = 0.5 * Math.atan2(2 * S[0][1], S[0][0] - S[1][1]);
    return { S, l1, l2, ang };
  },
  laserSig(api) { const r = this.rad; return Math.sqrt((api.p.d * api.p.s1 * r) ** 2 + (api.p.hand / 1000) ** 2); },

  reset(api, s) { s.seed = 9021; s.pts = []; },
  update(dt, api, s) {
    const r = this.rad;
    for (let i = 0; i < 80 && s.pts.length < 3000; i++) {
      if (api.scene === "arm") {
        const t1 = (api.p.t1 + api.p.s1 * this.gauss(s)) * r, t2 = (api.p.t2 + api.p.s2 * this.gauss(s)) * r;
        s.pts.push(this.fk(t1, t2));
      } else {
        const e = api.p.d * Math.tan(api.p.s1 * r * this.gauss(s)) + api.p.hand / 1000 * this.gauss(s);
        s.pts.push([0, e]);
      }
    }
    if (s.pts.length >= 3000) api.stop();
  },
  mc(s) {
    const n = s.pts.length; if (n < 2) return null;
    let mx = 0, my = 0; s.pts.forEach((p) => { mx += p[0]; my += p[1]; }); mx /= n; my /= n;
    let xx = 0, yy = 0, xy = 0; s.pts.forEach((p) => { xx += (p[0] - mx) ** 2; yy += (p[1] - my) ** 2; xy += (p[0] - mx) * (p[1] - my); });
    return { n, mx, my, sx: Math.sqrt(xx / (n - 1)), sy: Math.sqrt(yy / (n - 1)), rho: xy / Math.sqrt(xx * yy) };
  },
  readouts(api, s) {
    const m = this.mc(s), mm = (v) => api.fmt(v * 1000, 3) + " mm";
    if (api.scene === "laser") {
      const sl = this.laserSig(api);
      if (m && m.n >= 500 && Math.abs(api.p.s1 - 0.5) < 0.01 && Math.abs(api.p.d - 5) < 0.01 && api.p.hand === 0) api.done("laser");
      return [[["光点标准差（公式）", "dot std (formula)"], mm(sl)],
              [["其中转角部分 d·σ", "angle part d·σ"], mm(api.p.d * api.p.s1 * this.rad)],
              [["其中平移部分", "shift part"], mm(api.p.hand / 1000)],
              [["蒙特卡洛次数", "Monte Carlo runs"], m ? String(m.n) : "0"],
              [["光点标准差（蒙特卡洛）", "dot std (Monte Carlo)"], m ? mm(m.sy) : "—"]];
    }
    const L = this.lin(api), sx = Math.sqrt(L.S[0][0]), sy = Math.sqrt(L.S[1][1]), ratio = Math.sqrt(L.l1 / Math.max(L.l2, 1e-30));
    const r = this.rad, f = this.fk(api.p.t1 * r, api.p.t2 * r);
    if (ratio > 20) api.done("flat");
    const shift = m ? Math.hypot(m.mx - f[0], m.my - f[1]) : 0;
    const ex = api.p.t1 === 30 && api.p.t2 === 60 && Math.abs(api.p.s1 - 0.1) < 1e-6 && Math.abs(api.p.s2 - 0.1) < 1e-6;
    if (ex && m && m.n >= 2000 && Math.abs(m.sx / sx - 1) < 0.05) api.done("ex");
    if (api.p.s1 >= 7.99 && api.p.s2 >= 7.99 && m && m.n >= 2000 && shift > 0.005) api.done("big");
    return [[["σx、σy（线性化）", "σx, σy (linearized)"], `${api.fmt(sx * 1000, 3)}, ${api.fmt(sy * 1000, 3)} mm`],
            [["相关系数 ρ（线性化）", "correlation ρ (linearized)"], api.fmt(L.S[0][1] / (sx * sy || 1), 3)],
            [["1 倍椭圆半轴 √λ₁、√λ₂", "1σ semi-axes √λ₁, √λ₂"], `${api.fmt(Math.sqrt(L.l1) * 1000, 3)}, ${api.fmt(Math.sqrt(L.l2) * 1000, 3)} mm`],
            [["长短轴之比", "axis ratio"], api.fmt(ratio, 1)],
            [["蒙特卡洛次数", "Monte Carlo runs"], m ? String(m.n) : "0"],
            [["σx、σy（蒙特卡洛）", "σx, σy (Monte Carlo)"], m ? `${api.fmt(m.sx * 1000, 3)}, ${api.fmt(m.sy * 1000, 3)} mm` : "—"],
            [["均值偏离 f(μ)", "mean minus f(μ)"], m ? mm(shift) : "—"]];
  },
  draw(api, s) {
    const { w, h } = api, r = this.rad, c = api.ctx;
    if (api.scene === "laser") {
      const x0 = 70, y0 = h * 0.5, wallX = w - 120, sc = (wallX - x0) / 10;          // 10 m 占满宽度
      const wx = x0 + api.p.d * sc;
      api.line(wx, 20, wx, h - 20, api.css("--ink"), 4);
      api.label(api.T("墙", "wall"), wx + 8, 30, api.css("--muted"), 12);
      const beam = api.p.t1 * r;
      const yc = y0 - api.p.d * Math.tan(beam) * sc;
      api.line(x0, y0, wx, yc, api.css("--red"), 1.5, [6, 4]);
      api.circle(x0, y0, 10, api.css("--amber-soft"), api.css("--ink"));
      api.label(api.T("手", "hand"), x0 - 14, y0 + 22, api.css("--muted"), 12, "center");
      const k = 1500;      // 墙上的偏差放大 1500 px/m（标尺见下）
      s.pts.forEach((p) => { c.globalAlpha = 0.35; api.circle(wx + 14, yc - p[1] * k, 2.2, api.css("--red")); c.globalAlpha = 1; });
      const sl = this.laserSig(api);
      api.line(wx + 30, yc - 2 * sl * k, wx + 30, yc + 2 * sl * k, api.css("--blue"), 3);
      api.label("±2σ", wx + 36, yc, api.css("--blue"), 12);
      api.label(api.T("光点在墙上的位置（红点，放大显示：10 mm = 15 px）", "dot positions on the wall (red, enlarged: 10 mm = 15 px)"), 16, h - 14, api.css("--muted"), 12);
      return;
    }
    const sc = Math.min(w, h) * 0.75, bx = w * 0.32, by = h * 0.86;
    const P = (x, y) => [bx + sc * x, by - sc * y];
    api.arm(bx, by, [api.p.t1, api.p.t2], [this.L[0] * sc, this.L[1] * sc], api.css("--accent"), 12);
    const f = this.fk(api.p.t1 * r, api.p.t2 * r), tip = P(f[0], f[1]), mag = api.p.mag;
    // 蒙特卡洛点（相对 f(μ) 放大 mag 倍）
    s.pts.forEach((p) => { c.globalAlpha = 0.3; api.circle(tip[0] + sc * mag * (p[0] - f[0]), tip[1] - sc * mag * (p[1] - f[1]), 1.8, api.css("--blue")); c.globalAlpha = 1; });
    // 95% 椭圆
    const L = this.lin(api);
    c.beginPath();
    for (let i = 0; i <= 80; i++) {
      const t = 2 * Math.PI * i / 80, u = this.C95 * Math.sqrt(L.l1) * Math.cos(t), v = this.C95 * Math.sqrt(L.l2) * Math.sin(t);
      const ex = u * Math.cos(L.ang) - v * Math.sin(L.ang), ey = u * Math.sin(L.ang) + v * Math.cos(L.ang);
      const q = [tip[0] + sc * mag * ex, tip[1] - sc * mag * ey];
      i ? c.lineTo(q[0], q[1]) : c.moveTo(q[0], q[1]);
    }
    c.strokeStyle = api.css("--blue"); c.lineWidth = 2; c.stroke();
    const m = this.mc(s);
    if (m) { const q = [tip[0] + sc * mag * (m.mx - f[0]), tip[1] - sc * mag * (m.my - f[1])]; api.rect(q[0] - 4, q[1] - 4, 8, 8, api.css("--red")); }
    api.circle(tip[0], tip[1], 3.5, api.css("--ink"));
    api.label(api.T(`蓝线：95% 不确定性椭圆；蓝点：蒙特卡洛；红方块：蒙特卡洛均值（均相对末端放大 ${mag} 倍）`,
                    `blue line: 95% ellipse; blue dots: Monte Carlo; red square: MC mean (all magnified ×${mag} about the tip)`), 12, 16, api.css("--muted"), 12);
  },
});
