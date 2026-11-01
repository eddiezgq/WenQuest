// 实验 19.2 机械臂重复定位误差的主方向（配 19.2 节）。
// 机器人场景：UR5e 肩、肘两关节（上臂 0.425 m、前臂 0.392 m，零件库 2026.10.9 版关节表），肩关节角 30°。
// 机械臂 30 次回到同一个目标点；每次两个关节的定位误差各为标准差 30 μrad 的随机数，经雅可比矩阵 J 变成末端误差，
// 再加上测量仪器 0.2 μm 的随机误差。末端误差的总体协方差为 σ_q² J Jᵀ + σ_m² I。
// 生活场景：投 30 支飞镖，落点散布成一个倾斜的椭圆。
// 随机数用课程包的 mulberry32（api.calc.rng），同一个种子在每个浏览器里得到相同的数。
WQ.lab({
  title: ["实验 19.2 机械臂重复定位误差的主方向", "Lab 19.2 Principal directions of a robot's repeatability error"],
  goal: ["转动一条试探直线，找出点云投影方差最大和最小的方向，与协方差矩阵的特征向量比较；看误差椭圆怎样随机械臂的姿态变扁；体会一个异常测点对主成分的影响。",
         "Turn a trial line to find the directions of largest and smallest projected variance and compare them with the eigenvectors of the covariance matrix; watch the error ellipse flatten with the arm's pose; see how one outlier distorts the principal components."],
  scenes: [
    { id: "arm", robot: true, name: ["机械臂重复定位", "Robot repeatability"],
      problem: { title: ["机器人问题：误差主要朝哪个方向？", "Robot problem: in which direction is the error largest?"],
                 text: ["按 ISO 9283 的做法，让机械臂 30 次回到同一个点，用激光跟踪仪测末端位置。误差点云的主方向告诉我们：哪个方向的定位最不稳、它与机械臂的姿态有什么关系。",
                        "Following ISO 9283, the arm returns 30 times to the same point and a laser tracker measures the tool position. The principal directions of the error cloud tell us which direction is least repeatable and how that depends on the pose."] } },
    { id: "dart", name: ["生活中的例子：飞镖的落点", "Everyday example: darts"], hide: ["q2", "out"],
      problem: { title: ["生活中的例子：手臂往哪个方向抖得最厉害？", "Everyday example: in which direction does the hand shake most?"],
                 text: ["投 30 支飞镖，落点散布成一个倾斜的椭圆：出手时间早一点晚一点，飞镖沿上下方向偏；手腕左右偏，飞镖沿左右方向偏。椭圆的长轴就是第一主成分。",
                        "Throw 30 darts; the hits spread into a tilted ellipse: releasing early or late moves the dart up or down, a wrist turn moves it sideways. The long axis is the first principal component."] } },
  ],
  params: [
    { id: "phi", name: ["试探直线的方向 φ", "Trial direction φ"], min: 0, max: 180, step: 0.5, value: 0, unit: "°", digits: 1 },
    { id: "q2", name: ["肘关节角 θ₂", "Elbow angle θ₂"], min: 2, max: 170, step: 1, value: 60, unit: "°", digits: 0 },
    { id: "out", name: ["异常测点（0 无，1 有）", "Outlier (0 none, 1 one)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "max", robot: true, text: ["机械臂场景、无异常测点：把试探直线转到投影方差最大的方向（与第一主成分相差不到 1°）。", "Arm scene, no outlier: turn the line to the direction of largest projected variance (within 1° of PC 1)."],
      demo: { scene: "arm", set: { q2: 40, out: 0, phi: 143.5 }, press: [] } },
    { id: "min", robot: true, text: ["再把它转到投影方差最小的方向（与第二主成分相差不到 1°）。此时残差平方和是多少？", "Now turn it to the direction of smallest variance (within 1° of PC 2). What is the residual sum of squares?"],
      demo: { scene: "arm", set: { q2: 40, out: 0, phi: 53.5 }, press: [] } },
    { id: "flat", robot: true, text: ["让肘关节接近伸直，使误差椭圆的长短轴之比 √(λ₁/λ₂) 超过 10。短轴沿什么方向？", "Nearly straighten the elbow so that the axis ratio √(λ₁/λ₂) exceeds 10. Along which direction is the short axis?"],
      demo: { scene: "arm", set: { q2: 3, out: 0, phi: 0 }, press: [] } },
    { id: "outl", robot: true, text: ["加入异常测点，使第一主成分方向转过 10° 以上。", "Add the outlier so that PC 1 turns by more than 10°."],
      demo: { scene: "arm", set: { q2: 90, out: 1, phi: 0 }, press: [] } },
    { id: "dart", text: ["飞镖场景：把试探直线转到落点散布最大的方向（相差不到 2°）。", "Darts: turn the line to the direction of largest spread (within 2°)."],
      demo: { scene: "dart", set: { phi: 35.5 }, press: [] } },
  ],
  think: ["机械臂的关节误差是各向同性的（两个关节都是 30 μrad），为什么末端误差却是一个扁椭圆？用 Σ = σ_q² J Jᵀ 和第 18 章的奇异值分解解释，并说明短轴方向与机械臂的哪条线有关。",
          "The joint errors are isotropic (30 μrad at both joints), yet the tool error is a flat ellipse. Explain with Σ = σ_q² J Jᵀ and the SVD of Chapter 18; which line of the arm is the short axis related to?"],

  N: 30, SQ: 30e-6, SM: 0.2, L1: 0.425, L2: 0.392, T1: 30,
  jac(q2) {
    const t1 = this.T1 * Math.PI / 180, t12 = t1 + q2 * Math.PI / 180, l1 = this.L1, l2 = this.L2;
    return [[-l1 * Math.sin(t1) - l2 * Math.sin(t12), -l2 * Math.sin(t12)], [l1 * Math.cos(t1) + l2 * Math.cos(t12), l2 * Math.cos(t12)]];
  },
  data(api) {
    const g = api.calc.rng(19021), pts = [];
    if (api.scene === "dart") {
      const a = 32 * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
      for (let k = 0; k < this.N; k++) { const u = 40 * g.gauss(), v = 12 * g.gauss(); pts.push([c * u - s * v, s * u + c * v]); }   // mm
      return pts;
    }
    const J = this.jac(api.p.q2);
    for (let k = 0; k < this.N; k++) {
      const d1 = this.SQ * g.gauss(), d2 = this.SQ * g.gauss();
      pts.push([1e6 * (J[0][0] * d1 + J[0][1] * d2) + this.SM * g.gauss(), 1e6 * (J[1][0] * d1 + J[1][1] * d2) + this.SM * g.gauss()]);   // μm
    }
    if (api.p.out >= 1) pts[6] = [pts[6][0] + 70, pts[6][1] - 45];   // 第 7 次测量读错（跟踪仪丢光后的跳变）
    return pts;
  },
  pca(pts) {
    const n = pts.length, m = [0, 1].map((j) => pts.reduce((s, p) => s + p[j], 0) / n);
    const c = pts.map((p) => [p[0] - m[0], p[1] - m[1]]);
    const sxx = c.reduce((s, p) => s + p[0] * p[0], 0) / (n - 1), syy = c.reduce((s, p) => s + p[1] * p[1], 0) / (n - 1), sxy = c.reduce((s, p) => s + p[0] * p[1], 0) / (n - 1);
    const tr = sxx + syy, dif = Math.sqrt(((sxx - syy) / 2) ** 2 + sxy * sxy), l1 = tr / 2 + dif, l2 = tr / 2 - dif;
    const ang = (0.5 * Math.atan2(2 * sxy, sxx - syy) * 180 / Math.PI + 180) % 180;   // 第一主成分与 x 轴的夹角，0…180°
    return { m, c, S: [[sxx, sxy], [sxy, syy]], l1, l2, ang };
  },
  adiff(a, b) { const d = Math.abs(a - b) % 180; return Math.min(d, 180 - d); },
  reset(api, s) {},
  readouts(api, s) {
    const pts = this.data(api), P = this.pca(pts), f = api.fmt, n = pts.length;
    const ph = api.p.phi * Math.PI / 180, u = [Math.cos(ph), Math.sin(ph)];
    const vproj = P.c.reduce((a, p) => a + (p[0] * u[0] + p[1] * u[1]) ** 2, 0) / (n - 1);
    const res = P.c.reduce((a, p) => { const t = p[0] * u[0] + p[1] * u[1]; return a + (p[0] - t * u[0]) ** 2 + (p[1] - t * u[1]) ** 2; }, 0) / (n - 1);
    const unit = api.scene === "dart" ? "mm²" : "μm²";
    const rows = [[["试探方向上的投影方差 uᵀSu", "Projected variance uᵀSu"], f(vproj, 2) + " " + unit],
                  [["残差平方和 /(N − 1)", "Residual sum of squares /(N − 1)"], f(res, 2) + " " + unit],
                  [["两者之和 = tr S", "Sum = tr S"], f(vproj + res, 2) + " " + unit],
                  [["特征值 λ₁, λ₂", "Eigenvalues λ₁, λ₂"], f(P.l1, 2) + ", " + f(P.l2, 2) + " " + unit],
                  [["第一主成分的方向", "Direction of PC 1"], f(P.ang, 1) + "°"],
                  [["试探方向与第一主成分相差", "Trial line vs PC 1"], f(this.adiff(api.p.phi, P.ang), 1) + "°"],
                  [["长短轴之比 √(λ₁/λ₂)", "Axis ratio √(λ₁/λ₂)"], f(Math.sqrt(P.l1 / Math.max(P.l2, 1e-12)), 2)]];
    if (api.scene === "dart") {
      if (this.adiff(api.p.phi, P.ang) < 2) api.done("dart");
      return rows;
    }
    const J = this.jac(api.p.q2), JJ = api.la.mul(J, api.la.T(J));
    const Sig = [[1e12 * this.SQ ** 2 * JJ[0][0] + this.SM ** 2, 1e12 * this.SQ ** 2 * JJ[0][1]], [1e12 * this.SQ ** 2 * JJ[1][0], 1e12 * this.SQ ** 2 * JJ[1][1] + this.SM ** 2]];
    const angT = (0.5 * Math.atan2(2 * Sig[0][1], Sig[0][0] - Sig[1][1]) * 180 / Math.PI + 180) % 180;
    let rot = 0;
    if (api.p.out >= 1) { const clean = this.data({ ...api, p: { ...api.p, out: 0 } }); rot = this.adiff(this.pca(clean).ang, P.ang); }
    const ratio = Math.sqrt(P.l1 / Math.max(P.l2, 1e-12));
    if (api.p.out === 0 && this.adiff(api.p.phi, P.ang) < 1) api.done("max");
    if (api.p.out === 0 && this.adiff(api.p.phi, (P.ang + 90) % 180) < 1) api.done("min");
    if (api.p.out === 0 && ratio > 10) api.done("flat");
    if (api.p.out >= 1 && rot > 10) api.done("outl");
    rows.push([["理论协方差 σ_q²JJᵀ + σ_m²I 的主方向", "Principal direction of σ_q²JJᵀ + σ_m²I"], f(angT, 1) + "°"]);
    rows.push([["前臂方向（与 x 轴的夹角）", "Forearm direction (from the x-axis)"], f((this.T1 + api.p.q2) % 360, 0) + "°"]);
    if (api.p.out >= 1) rows.push([["异常测点使第一主成分转过", "PC 1 turned by the outlier"], f(rot, 1) + "°"]);
    return rows;
  },
  draw(api, s) {
    const pts = this.data(api), P = this.pca(pts), { w, h } = api, mu = api.css("--muted"), dart = api.scene === "dart";
    const cx = w * 0.32, cy = h * 0.52, R = Math.min(w * 0.29, h * 0.44);
    const ext = Math.max(...pts.map((p) => Math.max(Math.abs(p[0] - P.m[0]), Math.abs(p[1] - P.m[1])))) * 1.1 || 1;
    const sc = R / ext, X = (x) => cx + (x - P.m[0]) * sc, Y = (y) => cy - (y - P.m[1]) * sc;
    api.line(cx - R, cy, cx + R, cy, mu, 1); api.line(cx, cy - R, cx, cy + R, mu, 1);
    const ph = api.p.phi * Math.PI / 180, u = [Math.cos(ph), Math.sin(ph)];
    api.line(cx - R * u[0], cy + R * u[1], cx + R * u[0], cy - R * u[1], api.css("--amber"), 2);
    P.c.forEach((c) => { const t = c[0] * u[0] + c[1] * u[1]; api.line(X(P.m[0] + c[0]), Y(P.m[1] + c[1]), X(P.m[0] + t * u[0]), Y(P.m[1] + t * u[1]), api.css("--amber"), 1); });
    // 2 倍标准差的椭圆与两个主成分方向
    const a = P.ang * Math.PI / 180, e1 = [Math.cos(a), Math.sin(a)], e2 = [-Math.sin(a), Math.cos(a)], r1 = 2 * Math.sqrt(P.l1), r2 = 2 * Math.sqrt(Math.max(P.l2, 0));
    let prev = null;
    for (let k = 0; k <= 72; k++) { const t = 2 * Math.PI * k / 72, x = P.m[0] + r1 * Math.cos(t) * e1[0] + r2 * Math.sin(t) * e2[0], y = P.m[1] + r1 * Math.cos(t) * e1[1] + r2 * Math.sin(t) * e2[1];
      if (prev) api.line(prev[0], prev[1], X(x), Y(y), mu, 1, [4, 3]); prev = [X(x), Y(y)]; }
    api.arrow(cx, cy, cx + r1 * sc * e1[0], cy - r1 * sc * e1[1], api.css("--red"), 3);
    api.arrow(cx, cy, cx + Math.max(r2 * sc, 12) * e2[0], cy - Math.max(r2 * sc, 12) * e2[1], api.css("--green"), 3);
    pts.forEach((p, i) => api.circle(X(p[0]), Y(p[1]), api.p.out >= 1 && i === 6 && !dart ? 6 : 3.5, api.p.out >= 1 && i === 6 && !dart ? api.css("--red") : api.css("--blue")));
    api.label(api.T(dart ? "落点（mm）、试探直线（橙）、主成分（红、绿）" : "末端误差（μm）、试探直线（橙）、主成分（红、绿）",
                    dart ? "hits (mm), trial line (orange), PCs (red, green)" : "tool error (μm), trial line (orange), PCs (red, green)"), 10, 16, mu, 11);
    // 右边：机械臂姿态（或靶子）
    const bx = w * 0.72, by = h * 0.78;
    if (dart) {
      [90, 60, 30, 8].forEach((r, i) => api.circle(bx, h * 0.45, r, i % 2 ? api.css("--panel") : null, api.css("--ink")));
      pts.forEach((p) => api.circle(bx + p[0] * 0.9, h * 0.45 - p[1] * 0.9, 2.5, api.css("--red")));
      return;
    }
    const sz = Math.min(w * 0.3, h * 0.6) / (this.L1 + this.L2);
    const j = api.arm(bx, by, [this.T1, api.p.q2], [this.L1 * sz, this.L2 * sz]);
    const tip = j[j.length - 1];
    prev = null;
    const big = 2.0e-3 * sz;   // 椭圆放大画：每 μm 画 2 mm（按图的比例）
    for (let k = 0; k <= 72; k++) { const t = 2 * Math.PI * k / 72, x = r1 * Math.cos(t) * e1[0] + r2 * Math.sin(t) * e2[0], y = r1 * Math.cos(t) * e1[1] + r2 * Math.sin(t) * e2[1];
      const q = [tip[0] + x * big, tip[1] - y * big]; if (prev) api.line(prev[0], prev[1], q[0], q[1], api.css("--red"), 2); prev = q; }
    api.label(api.T("误差椭圆（放大约 2000 倍）", "error ellipse (×≈2000)"), bx - w * 0.12, h * 0.1, mu, 11);
  },
});
