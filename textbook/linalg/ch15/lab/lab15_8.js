// 实验 15.8 质量矩阵、可操作度与等效质量（配 15.8 节）。平面两连杆臂（水平放置，不计重力），参数与 code/_arm2m.py 相同：
// l = 0.4/0.3 m，m = 2/1 kg，均匀细杆，末端可挂负载 mp（质点）。质量矩阵 M(q₂) 见式 (15.8.3)；末端速度椭圆 {Jq̇ : ‖q̇‖ ≤ 1}；
// 等效质量矩阵 Λ = (J M⁻¹ Jᵀ)⁻¹，椭圆 xᵀΛ⁻¹x = 1 沿方向 u 的半径² = 沿 u 推末端时的等效质量；关节空间的动能椭圆 q̇ᵀMq̇ = 1。
WQ.lab({
  title: ["实验 15.8 质量矩阵、可操作度与等效质量", "Lab 15.8 Mass matrix, manipulability and effective mass"],
  goal: ["改变两连杆臂的姿态和末端负载，观察质量矩阵的特征值始终为正，以及末端的速度椭圆和等效质量椭圆怎样随姿态变化。",
         "Change the pose and tip load of a two-link arm; see that the eigenvalues of the mass matrix stay positive, and how the tip's velocity ellipse and effective-mass ellipse change with the pose."],
  scenes: [
    { id: "arm", robot: true, name: ["平面两连杆臂", "Planar two-link arm"],
      problem: { title: ["末端往哪个方向最灵活、最“重”？", "Which way is the tip most agile, and which way is it heaviest?"],
                 text: ["协作机器人与人接触时，碰撞力取决于运动方向上的等效质量；做精细装配时，希望末端在需要的方向上容易运动。两者都由姿态决定。",
                        "When a collaborative robot touches a person, the impact force depends on the effective mass in the direction of motion; for fine assembly the tip should move easily in the needed direction. Both depend on the pose."] } },
  ],
  params: [
    { id: "q1", name: ["关节 1 角度 q₁", "Joint 1 angle q₁"], min: -180, max: 180, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "q2", name: ["关节 2 角度 q₂", "Joint 2 angle q₂"], min: -170, max: 170, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "mp", name: ["末端负载 mp", "Tip load mp"], min: 0, max: 1, step: 0.1, value: 0, unit: "kg", digits: 1 },
  ],
  buttons: [],
  tasks: [
    { id: "decouple", robot: true, text: ["无负载时，找出使两个关节惯性解耦（|m₁₂| < 0.002 kg·m²）的 q₂。再挂 0.5 kg 负载，解耦角变成多少？", "With no load find q₂ that decouples the joints (|m₁₂| < 0.002 kg·m²). With a 0.5 kg load, where does the decoupled angle move?"],
      demo: { scene: "arm", set: { q1: 30, q2: 120, mp: 0 }, press: [] } },
    { id: "wmax", robot: true, text: ["找出可操作度 w 最大的姿态（达到最大值的 99.5% 以上）。它与 q₁ 有关吗？", "Find a pose with the largest manipulability w (at least 99.5% of the maximum). Does it depend on q₁?"],
      demo: { scene: "arm", set: { q1: 30, q2: 90, mp: 0 }, press: [] } },
    { id: "sing", robot: true, text: ["让手臂接近伸直（或完全折叠），使等效质量的最大、最小特征值之比超过 20，读出沿手臂方向的等效质量。质量矩阵的特征值还都为正吗？", "Bring the arm close to straight (or fully folded) so the ratio of the largest to smallest effective mass exceeds 20; read the effective mass along the arm. Are the eigenvalues of M still positive?"],
      demo: { scene: "arm", set: { q1: 30, q2: 8, mp: 0 }, press: [] } },
  ],
  think: ["速度椭圆和等效质量椭圆的长轴为什么大致互相垂直？在什么条件下它们恰好互相垂直？（提示：M = I 时 Λ = (JJᵀ)⁻¹。）", "Why are the long axes of the velocity ellipse and the effective-mass ellipse roughly perpendicular? When are they exactly perpendicular? (Hint: with M = I, Λ = (JJᵀ)⁻¹.)"],

  L1: 0.4, L2: 0.3, M1: 2, M2: 1,
  sym2(A) {   // eigen-decomposition of a symmetric 2×2 matrix: values ascending, unit vectors
    const a = A[0][0], b = A[0][1], d = A[1][1], m = (a + d) / 2, r = Math.hypot((a - d) / 2, b);
    const ang = 0.5 * Math.atan2(2 * b, a - d);   // direction of the larger eigenvalue
    return { l: [m - r, m + r], v: [[-Math.sin(ang), Math.cos(ang)], [Math.cos(ang), Math.sin(ang)]] };
  },
  inv2(A) { const det = A[0][0] * A[1][1] - A[0][1] * A[1][0]; return [[A[1][1] / det, -A[0][1] / det], [-A[1][0] / det, A[0][0] / det]]; },
  mul(A, B) { return [[A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]], [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]]; },
  T2(A) { return [[A[0][0], A[1][0]], [A[0][1], A[1][1]]]; },
  reset(api, s) {
    const d = Math.PI / 180, q1 = api.p.q1 * d, q2 = api.p.q2 * d, mp = api.p.mp, { L1, L2, M1, M2 } = this;
    const c1 = L1 / 2, c2 = L2 / 2, I1 = M1 * L1 * L1 / 12, I2 = M2 * L2 * L2 / 12, cq = Math.cos(q2);
    const m11 = I1 + I2 + M1 * c1 * c1 + M2 * (L1 * L1 + c2 * c2 + 2 * L1 * c2 * cq) + mp * (L1 * L1 + L2 * L2 + 2 * L1 * L2 * cq);
    const m12 = I2 + M2 * (c2 * c2 + L1 * c2 * cq) + mp * (L2 * L2 + L1 * L2 * cq);
    const m22 = I2 + M2 * c2 * c2 + mp * L2 * L2;
    s.M = [[m11, m12], [m12, m22]]; s.eM = this.sym2(s.M);
    const a1 = q1, a2 = q1 + q2;
    s.J = [[-L1 * Math.sin(a1) - L2 * Math.sin(a2), -L2 * Math.sin(a2)], [L1 * Math.cos(a1) + L2 * Math.cos(a2), L2 * Math.cos(a2)]];
    s.P = [[0, 0], [L1 * Math.cos(a1), L1 * Math.sin(a1)], [L1 * Math.cos(a1) + L2 * Math.cos(a2), L1 * Math.sin(a1) + L2 * Math.sin(a2)]];
    s.JJ = this.mul(s.J, this.T2(s.J)); s.eV = this.sym2(s.JJ);
    s.w = Math.abs(s.J[0][0] * s.J[1][1] - s.J[0][1] * s.J[1][0]);
    s.Li = this.mul(this.mul(s.J, this.inv2(s.M)), this.T2(s.J));         // Λ⁻¹ = J M⁻¹ Jᵀ
    s.eLi = this.sym2(s.Li);                                                // eigenvalues of Λ = 1 / eigenvalues of Λ⁻¹
    const r = Math.hypot(s.P[2][0], s.P[2][1]), u = [s.P[2][0] / r, s.P[2][1] / r];
    s.ma = 1 / (u[0] * (s.Li[0][0] * u[0] + s.Li[0][1] * u[1]) + u[1] * (s.Li[1][0] * u[0] + s.Li[1][1] * u[1]));
  },
  readouts(api, s) {
    if (!s.M) return [];
    const f = api.fmt, wmax = this.L1 * this.L2, sing = s.w < 1e-6, lmax = sing ? Infinity : 1 / s.eLi.l[0], lmin = 1 / s.eLi.l[1];
    if (api.p.mp === 0 && Math.abs(s.M[0][1]) < 0.002) api.done("decouple");
    if (s.w >= 0.995 * wmax) api.done("wmax");
    if (!sing && lmax / lmin > 20) api.done("sing");
    return [[["质量矩阵 M / kg·m²", "Mass matrix M / kg·m²"], "[[" + f(s.M[0][0], 4) + ", " + f(s.M[0][1], 4) + "], [" + f(s.M[1][0], 4) + ", " + f(s.M[1][1], 4) + "]]"],
            [["M 的特征值 / kg·m²", "Eigenvalues of M / kg·m²"], f(s.eM.l[0], 4) + ", " + f(s.eM.l[1], 4)],
            [["惯性耦合 m₁₂ / kg·m²", "Inertial coupling m₁₂ / kg·m²"], f(s.M[0][1], 4)],
            [["J 的奇异值（速度椭圆半轴）/ m·rad⁻¹", "Singular values of J (velocity semi-axes) / m·rad⁻¹"], f(Math.sqrt(s.eV.l[1]), 3) + ", " + f(Math.sqrt(Math.max(s.eV.l[0], 0)), 3)],
            [["可操作度 w = |det J| / m²", "Manipulability w = |det J| / m²"], f(s.w, 4) + "（" + api.T("最大", "max") + " " + f(wmax, 2) + "）"],
            [["等效质量 Λ 的特征值 / kg", "Eigenvalues of Λ / kg"], sing ? api.T("奇异姿态：Λ 不存在（沿手臂方向为 ∞）", "singular pose: Λ does not exist (∞ along the arm)") : f(lmin, 2) + ", " + f(lmax, 2) + "（" + api.T("比", "ratio") + " " + f(lmax / lmin, 1) + "）"],
            [["沿基座→末端方向的等效质量 / kg", "Effective mass along base→tip / kg"], sing || !isFinite(s.ma) ? "∞" : f(s.ma, 2)]];
  },
  draw(api, s) {
    if (!s.M) return;
    const { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink"), ctx = api.ctx;
    // left: workspace view (1 m = sc px)
    const ox = w * 0.33, oy = h * 0.55, sc = Math.min(w * 0.6, h) / 1.65;
    const X = (x) => ox + sc * x, Y = (y) => oy - sc * y;
    api.line(X(-0.75), Y(0), X(0.8), Y(0), mu, 1); api.line(X(0), Y(-0.75), X(0), Y(0.8), mu, 1);
    api.circle(X(0), Y(0), sc * 0.7, null, mu);
    const P = s.P;
    api.line(X(P[0][0]), Y(P[0][1]), X(P[1][0]), Y(P[1][1]), api.css("--blue"), 12);
    api.line(X(P[1][0]), Y(P[1][1]), X(P[2][0]), Y(P[2][1]), api.css("--blue"), 8);
    api.circle(X(0), Y(0), 7, ink); api.circle(X(P[1][0]), Y(P[1][1]), 6, ink);
    if (api.p.mp > 0) api.circle(X(P[2][0]), Y(P[2][1]), 5 + 8 * api.p.mp, api.css("--amber"));
    const ell = (A, k, color, width) => {     // curve A·(cos t, sin t)·k around the tip, A a 2×2 "square root"
      ctx.beginPath();
      for (let i = 0; i <= 96; i++) { const t = 2 * Math.PI * i / 96, c = Math.cos(t), si = Math.sin(t);
        const x = P[2][0] + k * (A[0][0] * c + A[0][1] * si), y = P[2][1] + k * (A[1][0] * c + A[1][1] * si);
        i ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y)); }
      ctx.strokeStyle = color; ctx.lineWidth = width; ctx.stroke();
    };
    ell(s.J, 0.25, api.css("--green"), 2.5);                  // velocity ellipse J·(unit circle)
    const e = s.eLi;
    if (s.w > 1e-6 && e.l[0] > 0) { const R = [[e.v[0][0] / Math.sqrt(e.l[0]), e.v[1][0] / Math.sqrt(e.l[1])], [e.v[0][1] / Math.sqrt(e.l[0]), e.v[1][1] / Math.sqrt(e.l[1])]];
    ell(R, 0.06, api.css("--red"), 2.5); }                    // xᵀΛ⁻¹x = 1, columns √λ(Λ)·v; skipped at a singular pose
    api.label(api.T("绿：速度椭圆（×0.25）；红：等效质量椭圆（×0.06）", "green: velocity ellipse (×0.25); red: effective-mass ellipse (×0.06)"), 12, 20, mu, 12);
    // right: joint-space kinetic-energy ellipse q̇ᵀMq̇ = 1 (rad/s)
    const cx = w * 0.82, cy = h * 0.5, R2 = Math.min(w * 0.16, h * 0.4), kmax = 1 / Math.sqrt(s.eM.l[0]), k = R2 / Math.max(kmax, 1e-9);
    api.line(cx - R2, cy, cx + R2, cy, mu, 1); api.line(cx, cy - R2, cx, cy + R2, mu, 1);
    ctx.beginPath();
    for (let i = 0; i <= 96; i++) { const t = 2 * Math.PI * i / 96;
      const a = Math.cos(t) / Math.sqrt(s.eM.l[0]), b = Math.sin(t) / Math.sqrt(s.eM.l[1]);
      const x = a * s.eM.v[0][0] + b * s.eM.v[1][0], y = a * s.eM.v[0][1] + b * s.eM.v[1][1];
      i ? ctx.lineTo(cx + k * x, cy - k * y) : ctx.moveTo(cx + k * x, cy - k * y); }
    ctx.strokeStyle = api.css("--amber"); ctx.lineWidth = 2.5; ctx.stroke();
    api.label("q̇₁", cx + R2 - 14, cy + 16, mu, 12); api.label("q̇₂", cx + 6, cy - R2 + 12, mu, 12);
    api.label(api.T("关节空间：动能 ½q̇ᵀMq̇ = ½ 的椭圆", "joint space: kinetic energy ½q̇ᵀMq̇ = ½"), cx - R2, cy + R2 + 18, mu, 11);
  },
});
