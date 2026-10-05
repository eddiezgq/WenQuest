// 实验 14.2 机械臂末端的刚度椭圆（配 14.2 节）。平面两连杆臂，l₁ = 0.40 m，l₂ = 0.30 m，关节刚度 k₁ = 2000 N·m/rad、k₂ 可调。
// 末端柔度 C = J diag(1/k₁, 1/k₂) Jᵀ（对称），刚度 K_x = C⁻¹；谱分解给出两个互相垂直的主方向与主刚度。与程序 14.2.1（_arm2.py）相同。
WQ.lab({
  title: ["实验 14.2 机械臂末端的刚度椭圆", "Lab 14.2 The stiffness ellipse at a robot's tip"],
  goal: ["改变姿态和关节刚度，观察末端刚度矩阵的两个主方向与主刚度；沿不同方向推末端，看位移与推力是否同向；找出最软的方向和各向同性的姿态。",
         "Change the pose and joint stiffness and watch the two principal directions and stiffnesses of the tip stiffness matrix; push the tip in different directions to see whether the deflection follows the push; find the softest direction and an isotropic pose."],
  scenes: [
    { id: "arm", robot: true, name: ["两连杆臂", "Two-link arm"],
      problem: { title: ["末端在哪个方向最软？", "In which direction is the tip softest?"],
                 text: ["关节的伺服和减速器都有弹性。末端受力 F 时位移 d = C F，C 是对称矩阵。它的两个特征向量互相垂直，是末端的“软轴”和“硬轴”。磨削、去毛刺时要知道工具在哪个方向最容易被顶开。",
                        "Servos and gears are elastic. A tip force F gives a deflection d = C F with C symmetric. Its two eigenvectors are perpendicular: the tip's soft and stiff axes. For grinding or deburring you need to know where the tool gives way most easily."] } },
  ],
  params: [
    { id: "q1", name: ["关节 1 角度 q₁", "Joint 1 angle q₁"], min: 0, max: 180, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "q2", name: ["关节 2 角度 q₂", "Joint 2 angle q₂"], min: 10, max: 170, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "k2", name: ["关节 2 刚度 k₂", "Joint 2 stiffness k₂"], min: 500, max: 3000, step: 100, value: 1000, unit: "N·m/rad", digits: 0 },
    { id: "phi", name: ["推力方向 φ（10 N）", "Push direction φ (10 N)"], min: 0, max: 359, step: 1, value: 270, unit: "°", digits: 0 },
  ],
  buttons: [],
  tasks: [
    { id: "soft", robot: true, text: ["在姿态 (0°, 90°)、k₂ = 1000 时，找出最软的方向：位移与推力同向（夹角小于 1°），且位移最大。", "At pose (0°, 90°) with k₂ = 1000, find the softest direction: deflection along the push (within 1°) and largest."],
      demo: { scene: "arm", set: { q1: 0, q2: 90, k2: 1000, phi: 147 }, press: [] } },
    { id: "rot", robot: true, text: ["保持 q₂ = 90°、k₂ = 1000，把 q₁ 转到 60° 以上，确认两个主刚度不变、主方向跟着转了同样的角度。", "Keep q₂ = 90° and k₂ = 1000, turn q₁ to 60° or more, and check that the principal stiffnesses stay the same while the axes turn by the same angle."],
      demo: { scene: "arm", set: { q1: 60, q2: 90, k2: 1000, phi: 270 }, press: [] } },
    { id: "firm", robot: true, text: ["保持 k₂ = 1000，调 q₂，使最软方向的刚度也超过 10000 N/m。", "Keep k₂ = 1000 and adjust q₂ until even the softest direction is stiffer than 10000 N/m."],
      demo: { scene: "arm", set: { q1: 0, q2: 130, k2: 1000, phi: 270 }, press: [] } },
    { id: "iso", robot: true, text: ["同时调 q₂ 和 k₂，使末端在各个方向一样硬：两个主刚度之比小于 1.05（椭圆接近圆）。", "Adjust q₂ and k₂ together until the tip is equally stiff in all directions: ratio of principal stiffnesses below 1.05 (a near circle)."],
      demo: { scene: "arm", set: { q1: 0, q2: 139, k2: 2600, phi: 270 }, press: [] } },
  ],
  think: ["为什么主刚度只与 q₂、k₁、k₂ 有关，与 q₁ 无关？用 J(q₁, q₂) = R(q₁) J(0, q₂) 说明。", "Why do the principal stiffnesses depend on q₂, k₁, k₂ but not on q₁? Use J(q₁, q₂) = R(q₁) J(0, q₂)."],

  l1: 0.40, l2: 0.30, k1: 2000,
  reset(api, s) {
    const d2r = Math.PI / 180, q1 = api.p.q1 * d2r, q2 = api.p.q2 * d2r, a2 = q1 + q2, l1 = this.l1, l2 = this.l2;
    const J = [[-l1 * Math.sin(q1) - l2 * Math.sin(a2), -l2 * Math.sin(a2)], [l1 * Math.cos(q1) + l2 * Math.cos(a2), l2 * Math.cos(a2)]];
    const c1 = 1 / this.k1, c2 = 1 / api.p.k2;
    const C = [[c1 * J[0][0] * J[0][0] + c2 * J[0][1] * J[0][1], c1 * J[0][0] * J[1][0] + c2 * J[0][1] * J[1][1]], [0, c1 * J[1][0] * J[1][0] + c2 * J[1][1] * J[1][1]]];
    C[1][0] = C[0][1];
    const det = C[0][0] * C[1][1] - C[0][1] * C[0][1];
    s.K = [[C[1][1] / det, -C[0][1] / det], [-C[0][1] / det, C[0][0] / det]];
    // eigen of the symmetric 2×2 compliance: c_soft ≥ c_stiff
    const tr = C[0][0] + C[1][1], disc = Math.sqrt(Math.max(0, (C[0][0] - C[1][1]) ** 2 / 4 + C[0][1] ** 2));
    const cs = tr / 2 + disc, ch = tr / 2 - disc;
    let ang = 0.5 * Math.atan2(2 * C[0][1], C[0][0] - C[1][1]);   // direction of the larger compliance (soft axis)
    s.cs = cs; s.ch = ch; s.ksoft = 1 / cs; s.khard = 1 / ch; s.angSoft = ang * 180 / Math.PI;
    s.C = C; s.J = J;
    const ph = api.p.phi * d2r, F = [10 * Math.cos(ph), 10 * Math.sin(ph)];
    s.F = F; s.d = [C[0][0] * F[0] + C[0][1] * F[1], C[1][0] * F[0] + C[1][1] * F[1]];
    const dn = Math.hypot(...s.d);
    s.ang = Math.acos(Math.max(-1, Math.min(1, (s.d[0] * F[0] + s.d[1] * F[1]) / (dn * 10)))) * 180 / Math.PI;
    s.dn = dn;
    s.P = [[0, 0], [l1 * Math.cos(q1), l1 * Math.sin(q1)], [l1 * Math.cos(q1) + l2 * Math.cos(a2), l1 * Math.sin(q1) + l2 * Math.sin(a2)]];
  },
  readouts(api, s) {
    if (!s.K) return [];
    const f = api.fmt, base = api.p.q2 === 90 && api.p.k2 === 1000;
    if (base && api.p.q1 === 0 && s.ang < 1 && Math.abs(s.dn - 10 * s.cs) < 0.01 * 10 * s.cs) api.done("soft");
    if (base && api.p.q1 >= 60) api.done("rot");
    if (api.p.k2 === 1000 && s.ksoft > 10000) api.done("firm");
    if (s.khard / s.ksoft < 1.05) api.done("iso");
    let a = ((s.angSoft % 180) + 180) % 180;
    return [[["末端刚度 K_x / (N/m)", "Tip stiffness K_x / (N/m)"], "[[" + f(s.K[0][0], 0) + ", " + f(s.K[0][1], 0) + "], [" + f(s.K[1][0], 0) + ", " + f(s.K[1][1], 0) + "]]"],
            [["主刚度：软、硬 / (N/m)", "Principal stiffness: soft, stiff / (N/m)"], f(s.ksoft, 0) + ", " + f(s.khard, 0)],
            [["硬软之比", "Stiff-to-soft ratio"], f(s.khard / s.ksoft, 3)],
            [["软轴方向（与 x 轴的夹角）", "Soft axis (angle from x)"], f(a, 1) + "°（" + api.T("硬轴 ", "stiff axis ") + f((a + 90) % 180, 1) + "°）"],
            [["推力 F / N", "Push F / N"], "(" + f(s.F[0], 2) + ", " + f(s.F[1], 2) + ")"],
            [["位移 d / mm", "Deflection d / mm"], "(" + f(1000 * s.d[0], 3) + ", " + f(1000 * s.d[1], 3) + ")"],
            [["位移与推力的夹角", "Angle between deflection and push"], f(s.ang, 1) + "°"]];
  },
  draw(api, s) {
    if (!s.K) return;
    const { w, h } = api, ink = api.css("--ink"), mu = api.css("--muted");
    const sc = Math.min(w / 1.6, h / 1.1), ox = w * 0.38, oy = h * 0.72;
    const X = (p) => [ox + sc * p[0], oy - sc * p[1]];
    api.line(ox - 30, oy + 8, ox + 30, oy + 8, ink, 3);
    for (let i = 0; i < 2; i++) { const a = X(s.P[i]), b = X(s.P[i + 1]); api.line(a[0], a[1], b[0], b[1], ink, 8); }
    for (let i = 0; i < 2; i++) { const a = X(s.P[i]); api.circle(a[0], a[1], 6, "#fff", ink); }
    const tip = X(s.P[2]), ds = Math.min(60000, 0.3 * Math.min(w, h) / (10 * s.cs));   // deflection drawn up to 60000× (m → px), smaller if the ellipse would leave the canvas
    const c = api.ctx; c.beginPath();
    for (let k = 0; k <= 120; k++) {
      const t = 2 * Math.PI * k / 120, F = [10 * Math.cos(t), 10 * Math.sin(t)];
      const d = [s.C[0][0] * F[0] + s.C[0][1] * F[1], s.C[1][0] * F[0] + s.C[1][1] * F[1]];
      const x = tip[0] + ds * d[0], y = tip[1] - ds * d[1];
      if (k) c.lineTo(x, y); else c.moveTo(x, y);
    }
    c.strokeStyle = api.css("--amber"); c.lineWidth = 2; c.stroke();
    const a = s.angSoft * Math.PI / 180, L = 160;
    api.line(tip[0] - L * Math.cos(a), tip[1] + L * Math.sin(a), tip[0] + L * Math.cos(a), tip[1] - L * Math.sin(a), api.css("--green"), 1, [5, 4]);
    api.line(tip[0] + L * Math.sin(a), tip[1] + L * Math.cos(a), tip[0] - L * Math.sin(a), tip[1] - L * Math.cos(a), api.css("--red"), 1, [5, 4]);
    api.arrow(tip[0], tip[1], tip[0] + 6 * s.F[0], tip[1] - 6 * s.F[1], api.css("--blue"), 2);
    api.arrow(tip[0], tip[1], tip[0] + ds * s.d[0], tip[1] - ds * s.d[1], ink, 3);
    api.label(api.T("推力（蓝）、位移（黑，放大 " + Math.round(ds) + " 倍）、柔度椭圆（黄）；虚线：软轴（绿）、硬轴（红）", "push (blue), deflection (black, ×" + Math.round(ds) + "), compliance ellipse (amber); dashed: soft (green), stiff (red) axes"), 12, 20, mu, 12);
  },
});
