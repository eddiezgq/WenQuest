// 实验 8.5 用不同方法求同一个逆运动学问题（配 8.5 节）。零件库 UR5e：法兰盘中心的位置逆解，手腕关节固定在 (−90°, −90°, 0°)，
// 求关节 1～3（算例 8.5.1）。位置由表 12.1.1 的旋量轴按指数积公式计算：从关节 6 起，每个关节绕它零位时的轴转动。
// 雅可比矩阵第 i 列 = ω_i(θ) × (p − q_i(θ))。四种方法：梯度下降（阿米霍回溯）、牛顿法（完整黑塞矩阵，负特征值取绝对值）、
// 高斯-牛顿法（式 (8.5.4)）、LM 法（式 (8.5.5)，尼尔森的阻尼系数 μ 更新 (8.5.9)）。
// “室内定位”：4 个 UWB 基站，测距误差取算例 8.5.3 的同一组值；房间按约 1:5.5 缩小显示。
WQ.lab({
  title: ["实验 8.5 用不同方法求同一个逆运动学问题", "Lab 8.5 One inverse-kinematics problem, several methods"],
  goal: ["用梯度下降、牛顿法、高斯-牛顿法和 LM 法求 UR5e 的位置逆解，比较迭代次数和对初值的敏感程度；用高斯-牛顿法做室内定位。",
         "Solve the UR5e position inverse kinematics by gradient descent, Newton, Gauss-Newton and Levenberg-Marquardt; compare iteration counts and sensitivity to the start; locate a phone indoors by Gauss-Newton."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 位置逆解", "UR5e position IK"], hide: ["ux", "uy", "uz"],
      problem: { title: ["机器人问题：法兰盘中心到达目标点", "Robot problem: bring the flange centre to a target"],
                 text: ["目标点由“目标关节角”算出（红球）。从起始形态出发迭代，手臂一步步运动，直到法兰盘中心到达红球。",
                        "The target (red ball) is computed from the “target joint angles”. Starting from the chosen posture the arm moves step by step until the flange centre reaches it."] } },
    { id: "uwb", name: ["室内定位", "Indoor positioning"], hide: ["method", "start", "j1", "j2", "j3"],
      problem: { title: ["生活中的例子：手机在哪里", "Everyday example: where is the phone?"],
                 text: ["四个 UWB 基站（蓝球）测出到手机的距离，带有标准差约 5 cm 的误差。高斯-牛顿法从房间中央出发，求出手机的位置（红球），绿块是实际位置。",
                        "Four UWB anchors (blue) measure their distances to the phone, with errors of standard deviation about 5 cm. Gauss-Newton starts at the room centre and finds the phone (red); the green block is the true position."] } },
  ],
  params: [
    { id: "method", name: ["方法：0 梯度下降 / 1 牛顿 / 2 高斯-牛顿 / 3 LM", "Method: 0 GD / 1 Newton / 2 Gauss-Newton / 3 LM"], min: 0, max: 3, step: 1, value: 2, unit: "", digits: 0 },
    { id: "start", name: ["起始形态：0 (0°, −90°, 90°) / 1 伸直 (0, 0, 0)", "Start: 0 (0°, −90°, 90°) / 1 stretched (0, 0, 0)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "j1", name: ["目标关节角 θ₁", "Target joint θ₁"], min: -180, max: 180, step: 1, value: 40, unit: "°", digits: 0 },
    { id: "j2", name: ["目标关节角 θ₂", "Target joint θ₂"], min: -180, max: 0, step: 1, value: -70, unit: "°", digits: 0 },
    { id: "j3", name: ["目标关节角 θ₃", "Target joint θ₃"], min: -160, max: 160, step: 1, value: 100, unit: "°", digits: 0 },
    { id: "ux", name: ["手机实际位置 x", "Phone x (true)"], min: 0.5, max: 5.5, step: 0.1, value: 3.6, unit: "m", digits: 1 },
    { id: "uy", name: ["手机实际位置 y", "Phone y (true)"], min: 0.5, max: 3.5, step: 0.1, value: 1.2, unit: "m", digits: 1 },
    { id: "uz", name: ["手机实际位置 z", "Phone z (true)"], min: 0.2, max: 2.2, step: 0.1, value: 1.0, unit: "m", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["求解", "Solve"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "gn", robot: true, text: ["用高斯-牛顿法复现算例 8.5.1（默认目标、起始形态 0），记下迭代次数。", "Reproduce Example 8.5.1 with Gauss-Newton (default target, start 0) and note the iterations."],
      demo: { scene: "ur", set: { method: 2, start: 0, j1: 40, j2: -70, j3: 100 }, press: ["start"], wait: 6 } },
    { id: "gd", robot: true, text: ["换用梯度下降求同一问题，比较迭代次数。", "Solve the same problem by gradient descent and compare the iterations."],
      demo: { scene: "ur", set: { method: 0, start: 0, j1: 40, j2: -70, j3: 100 }, press: ["start"], wait: 10 } },
    { id: "sing", robot: true, text: ["从伸直的形态出发用 LM 法求解：关节角不绕圈，直接收敛到目标关节角。", "Start from the stretched posture with LM: the joints do not wind round and converge straight to the target angles."],
      demo: { scene: "ur", set: { method: 3, start: 1, j1: 40, j2: -70, j3: 100 }, press: ["start"], wait: 8 } },
    { id: "uwb", text: ["在“室内定位”中求出手机的位置，误差小于 15 cm。", "In “Indoor positioning” locate the phone to within 15 cm."],
      demo: { scene: "uwb", set: { ux: 3.6, uy: 1.2, uz: 1.0 }, press: ["start"], wait: 8 } },
  ],
  think: ["从伸直的形态出发，高斯-牛顿法第一步为什么转了那么大的角度？用 JᵀJ 的最小特征值解释，再说明 LM 的阻尼项起了什么作用。",
          "Starting from the stretched posture, why is Gauss-Newton's first step so large? Explain with the smallest eigenvalue of JᵀJ, and say what LM's damping term does."],

  WRIST: [-90, -90, 0].map((d) => d * Math.PI / 180),
  NOISE: [0.10204596, -0.12778325, 0.02090494, -0.02838848],
  ANCH: [[0, 0, 2.5], [6, 0, 2.5], [6, 4, 2.5], [0, 4, 0.3]],
  axes() {
    const H1 = 0.163, W1 = 0.138, L1 = 0.425, W2 = 0.131, L2 = 0.392, W3 = 0.127, H2 = 0.1, W4 = 0.1, yd = [0, -1, 0];
    return { w: [[0, 0, 1], yd, yd, yd, [0, 0, -1], yd],
             q: [[0, 0, H1], [0, -W1, H1], [-L1, -W1 + W2, H1], [-L1 - L2, -W1 + W2, H1], [-L1 - L2, -W1 + W2 - W3, H1], [-L1 - L2, -W1 + W2 - W3, H1 - H2]],
             p0: [-L1 - L2, -W1 + W2 - W3 - W4, H1 - H2] };
  },
  rot(w, t) { const c = Math.cos(t), s = Math.sin(t), K = [[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]];
    return [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + s * K[i][j] + (1 - c) * (K[i][0] * K[0][j] + K[i][1] * K[1][j] + K[i][2] * K[2][j]))); },
  mv(R, v) { return [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]); },
  mm(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  flange(th6) {                                                // 指数积：从关节 6 起，绕零位时的轴转动
    const { w, q, p0 } = this.axes(); let p = p0.slice();
    for (let i = 5; i >= 0; i--) { const R = this.rot(w[i], th6[i]), d = [p[0] - q[i][0], p[1] - q[i][1], p[2] - q[i][2]], e = this.mv(R, d); p = [e[0] + q[i][0], e[1] + q[i][1], e[2] + q[i][2]]; }
    return p;
  },
  jac3(th6) {                                                  // 前三列：ω_i(θ) × (p − q_i(θ))
    const { w, q } = this.axes(), p = this.flange(th6); let R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], t = [0, 0, 0]; const J = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
    for (let i = 0; i < 3; i++) {
      const wi = this.mv(R, w[i]), qi = this.mv(R, q[i]).map((v, k) => v + t[k]), c = this.cross(wi, [p[0] - qi[0], p[1] - qi[1], p[2] - qi[2]]);
      for (let k = 0; k < 3; k++) J[k][i] = c[k];
      const Ri = this.rot(w[i], th6[i]), dq = this.mv(Ri, q[i]); t = this.mv(R, [q[i][0] - dq[0], q[i][1] - dq[1], q[i][2] - dq[2]]).map((v, k) => v + t[k]); R = this.mm(R, Ri);
    }
    return J;
  },
  full(x) { return [x[0], x[1], x[2], ...this.WRIST]; },
  target(api) { return this.flange(this.full([api.p.j1, api.p.j2, api.p.j3].map((d) => d * Math.PI / 180))); },
  solve3(A, b) {
    const M = A.map((r, i) => [...r, b[i]]);
    for (let i = 0; i < 3; i++) { let p = i; for (let j = i + 1; j < 3; j++) if (Math.abs(M[j][i]) > Math.abs(M[p][i])) p = j; [M[i], M[p]] = [M[p], M[i]];
      for (let j = i + 1; j < 3; j++) { const f = M[j][i] / M[i][i]; for (let k = i; k < 4; k++) M[j][k] -= f * M[i][k]; } }
    const x = [0, 0, 0]; for (let i = 2; i >= 0; i--) { let s = M[i][3]; for (let k = i + 1; k < 3; k++) s -= M[i][k] * x[k]; x[i] = s / M[i][i]; }
    return x;
  },
  eig3(A) {                                                    // 对称 3×3 矩阵的雅可比旋转法：A = V diag(d) Vᵀ
    let a = A.map((r) => r.slice()), V = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    for (let sweep = 0; sweep < 30; sweep++) for (const [p, q] of [[0, 1], [0, 2], [1, 2]]) {
      if (Math.abs(a[p][q]) < 1e-15) continue;
      const th = 0.5 * Math.atan2(2 * a[p][q], a[q][q] - a[p][p]), c = Math.cos(th), s = Math.sin(th);
      const G = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; G[p][p] = c; G[q][q] = c; G[p][q] = s; G[q][p] = -s;
      const Gt = [0, 1, 2].map((i) => [0, 1, 2].map((j) => G[j][i]));
      a = this.mm(this.mm(Gt, a), G); V = this.mm(V, G);
    }
    return { d: [a[0][0], a[1][1], a[2][2]], V };
  },
  res(api, x) { const p = this.flange(this.full(x)), t = this.target(api); return [p[0] - t[0], p[1] - t[1], p[2] - t[2]]; },
  F(api, x) { const r = this.res(api, x); return 0.5 * (r[0] * r[0] + r[1] * r[1] + r[2] * r[2]); },
  JtJ(J) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => J[0][i] * J[0][j] + J[1][i] * J[1][j] + J[2][i] * J[2][j])); },
  Jtr(J, r) { return [0, 1, 2].map((i) => J[0][i] * r[0] + J[1][i] * r[1] + J[2][i] * r[2]); },
  stepIK(api, s) {
    const x = s.x, r = this.res(api, x), J = this.jac3(this.full(x)), g = this.Jtr(J, r), A = this.JtJ(J), m = api.p.method;
    const gn = Math.hypot(...g), xn = Math.hypot(...x);
    // 停止条件与程序 8.5.1 相同：梯度下降 ‖∇F‖ < 10⁻¹⁰，牛顿法 ‖∇F‖ < 10⁻¹²，高斯-牛顿与 LM 法步长 < 10⁻¹²(1 + ‖θ‖)
    if ((m === 0 && gn < 1e-10) || (m === 1 && gn < 1e-12) || (m === 3 && Math.max(...g.map(Math.abs)) < 1e-12)) { this.finish(api, s); return; }
    let d;
    if (m === 0) {                                             // 梯度下降 + 阿米霍回溯（试探步长 8）
      let a = 8; const f0 = this.F(api, x), gg = g[0] * g[0] + g[1] * g[1] + g[2] * g[2];
      while (this.F(api, x.map((v, k) => v - a * g[k])) > f0 - 1e-4 * a * gg && a > 1e-12) a *= 0.5;
      d = g.map((v) => -a * v);
    } else if (m === 1) {                                      // 牛顿法：∇²r_i 由 J 的差商求得，负特征值取绝对值，回溯
      const H = A.map((row) => row.slice()), h = 1e-6;
      for (let j = 0; j < 3; j++) { const xp = x.slice(), xm = x.slice(); xp[j] += h; xm[j] -= h;
        const Jp = this.jac3(this.full(xp)), Jm = this.jac3(this.full(xm));
        for (let i = 0; i < 3; i++) { const dJ = [0, 1, 2].map((k) => (Jp[k][i] - Jm[k][i]) / (2 * h)); H[i][j] += 0.5 * (dJ[0] * r[0] + dJ[1] * r[1] + dJ[2] * r[2]); H[j][i] += 0.5 * (dJ[0] * r[0] + dJ[1] * r[1] + dJ[2] * r[2]); } }
      const { d: ev, V } = this.eig3(H), mx = Math.max(...ev.map(Math.abs)), lam = ev.map((v) => Math.max(Math.abs(v), 0.01 * mx));
      const Vg = [0, 1, 2].map((i) => V[0][i] * g[0] + V[1][i] * g[1] + V[2][i] * g[2]);
      d = [0, 1, 2].map((k) => -(V[k][0] * Vg[0] / lam[0] + V[k][1] * Vg[1] / lam[1] + V[k][2] * Vg[2] / lam[2]));
      let a = 1; const f0 = this.F(api, x), slope = g[0] * d[0] + g[1] * d[1] + g[2] * d[2];
      while (this.F(api, x.map((v, k) => v + a * d[k])) > f0 + 1e-4 * a * slope && a > 1e-8) a *= 0.5;
      d = d.map((v) => a * v);
    } else if (m === 2) {
      d = this.solve3(A, g.map((v) => -v));                    // 高斯-牛顿：JᵀJ Δ = −Jᵀr
    } else {                                                   // LM：(JᵀJ + μI) Δ = −Jᵀr，按增益比调整 μ
      if (s.lam === null) { s.lam = 1e-3 * Math.max(A[0][0], A[1][1], A[2][2]); s.nu = 2; }
      for (let tries = 0; tries < 30; tries++) {
        d = this.solve3(A.map((row, i) => row.map((v, j) => v + (i === j ? s.lam : 0))), g.map((v) => -v));
        const pred = 0.5 * (d[0] * (s.lam * d[0] - g[0]) + d[1] * (s.lam * d[1] - g[1]) + d[2] * (s.lam * d[2] - g[2]));
        const rho = (this.F(api, x) - this.F(api, x.map((v, k) => v + d[k]))) / pred;
        if (rho > 0) { s.lam *= Math.max(1 / 3, 1 - (2 * rho - 1) ** 3); s.nu = 2; break; }
        s.lam *= s.nu; s.nu *= 2; d = [0, 0, 0];
      }
      if (Math.hypot(...d) < 1e-12 * (1 + xn)) { this.finish(api, s); return; }
    }
    s.x = x.map((v, k) => v + d[k]); s.k += 1;
    s.rn = Math.hypot(...this.res(api, s.x));
    if ((m === 2 && Math.hypot(...d) < 1e-12 * (1 + xn)) || s.k >= 400 || !isFinite(s.rn)) this.finish(api, s);
  },
  finish(api, s) { s.rn = Math.hypot(...this.res(api, s.x)); s.done = s.rn < 1e-9; api.stop(); },
  stepUWB(api, s) {                                            // 高斯-牛顿：残差 ‖x − aᵢ‖ − ρᵢ，雅可比第 i 行是从基站指向 x 的单位向量
    const u = s.u, r = [], J = [];
    this.ANCH.forEach((a, i) => { const dv = [u[0] - a[0], u[1] - a[1], u[2] - a[2]], n = Math.hypot(...dv); r.push(n - s.rho[i]); J.push(dv.map((v) => v / n)); });
    const A = [0, 1, 2].map((i) => [0, 1, 2].map((j) => J.reduce((t, row) => t + row[i] * row[j], 0)));
    const g = [0, 1, 2].map((i) => J.reduce((t, row, k) => t + row[i] * r[k], 0));
    const d = this.solve3(A, g.map((v) => -v));
    s.u = u.map((v, k) => v + d[k]); s.k += 1; s.path.push(s.u.slice());
    if (Math.hypot(...d) < 1e-12 * (1 + Math.hypot(...u)) || s.k >= 50) { s.done = true; api.stop(); }
  },

  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    arm.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    keep.goal = new T.Mesh(new T.SphereGeometry(0.022, 20, 14), new T.MeshStandardMaterial({ color: 0xcf222e })); G.add(keep.goal);
    const line = (color, n) => { const g = new T.BufferGeometry(); g.setAttribute("position", new T.BufferAttribute(new Float32Array(n * 3), 3)); g.setDrawRange(0, 0);
      const l = new T.Line(g, new T.LineBasicMaterial({ color })); l.frustumCulled = false; G.add(l); return l; };
    keep.trace = line(0xc98f00, 500);
    keep.room = new T.Group(); G.add(keep.room);
    const S = 0.18, O = [-0.54, -0.36, 0];                     // 房间按约 1:5.5 缩小
    keep.S = S; keep.O = O;
    const P = (v) => new T.Vector3(O[0] + S * v[0], O[1] + S * v[1], O[2] + S * v[2]);
    const edges = [[0, 0, 0], [6, 0, 0], [6, 4, 0], [0, 4, 0], [0, 0, 2.8], [6, 0, 2.8], [6, 4, 2.8], [0, 4, 2.8]];
    const pairs = [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]];
    const eg = new T.BufferGeometry().setFromPoints(pairs.flatMap(([a, b]) => [P(edges[a]), P(edges[b])]));
    keep.room.add(new T.LineSegments(eg, new T.LineBasicMaterial({ color: 0x5a6a73 })));
    const floor = new T.Mesh(new T.PlaneGeometry(6 * S, 4 * S), new T.MeshStandardMaterial({ color: 0xe5ecea, side: T.DoubleSide }));
    floor.position.copy(P([3, 2, 0])); keep.room.add(floor);
    this.ANCH.forEach((a) => { const m = new T.Mesh(new T.SphereGeometry(0.03, 16, 12), new T.MeshStandardMaterial({ color: 0x1f6feb })); m.position.copy(P(a)); keep.room.add(m); });
    keep.phone = new T.Mesh(new T.BoxGeometry(0.03, 0.05, 0.012), new T.MeshStandardMaterial({ color: 0x1a7f37 })); keep.room.add(keep.phone);
    keep.est = new T.Mesh(new T.SphereGeometry(0.022, 16, 12), new T.MeshStandardMaterial({ color: 0xcf222e })); keep.room.add(keep.est);
    keep.upath = line(0xcf222e, 60);
    keep.P = P;
  },
  reset(api, s) {
    s.x = api.p.start === 1 ? [0, 0, 0] : [0, -Math.PI / 2, Math.PI / 2]; s.k = 0; s.lam = null; s.nu = 2; s.done = false; s.clock = 0;
    s.rn = Math.hypot(...this.res(api, s.x)); s.trace = [this.flange(this.full(s.x))];
    const truth = [api.p.ux, api.p.uy, api.p.uz];
    s.rho = this.ANCH.map((a, i) => Math.hypot(truth[0] - a[0], truth[1] - a[1], truth[2] - a[2]) + this.NOISE[i]);
    s.u = [3, 2, 1.2]; s.path = [s.u.slice()];
  },
  update(dt, api, s) {
    s.clock += dt;
    const per = api.scene === "uwb" ? 0.3 : api.p.method === 0 ? 0.04 : 0.3;
    while (s.clock >= per && api.running) {
      s.clock -= per;
      if (api.scene === "uwb") this.stepUWB(api, s); else { this.stepIK(api, s); s.trace.push(this.flange(this.full(s.x))); }
    }
  },
  readouts(api, s) {
    const f = (x, n) => api.fmt(x, n), dg = (x) => f(x * 180 / Math.PI, 1);
    if (api.scene === "uwb") {
      const err = Math.hypot(s.u[0] - api.p.ux, s.u[1] - api.p.uy, s.u[2] - api.p.uz);
      if (s.done && err < 0.15) api.done("uwb");
      return [[["迭代次数 k", "iteration k"], String(s.k)], [["估计位置", "estimate"], `(${f(s.u[0], 3)}, ${f(s.u[1], 3)}, ${f(s.u[2], 3)}) m`],
              [["与实际位置之差", "error"], f(err * 100, 1) + " cm"], [["测得的距离 ρ", "measured ranges ρ"], s.rho.map((v) => f(v, 3)).join(", ") + " m"]];
    }
    const def = api.p.j1 === 40 && api.p.j2 === -70 && api.p.j3 === 100;
    if (s.done && def && api.p.start === 0 && api.p.method === 2) api.done("gn");
    if (s.done && def && api.p.start === 0 && api.p.method === 0) api.done("gd");
    if (s.done && def && api.p.start === 1 && api.p.method === 3 && s.x.every((v) => Math.abs(v) <= Math.PI + 1e-9)) api.done("sing");
    const names = [api.T("梯度下降", "gradient descent"), api.T("牛顿法", "Newton"), api.T("高斯-牛顿法", "Gauss-Newton"), api.T("LM 法", "Levenberg-Marquardt")];
    const t = this.target(api), J = this.jac3(this.full(s.x)), ev = this.eig3(this.JtJ(J)).d;
    return [[["方法", "method"], names[api.p.method]], [["迭代次数 k", "iteration k"], String(s.k)],
            [["残差 ‖r‖", "residual ‖r‖"], s.rn < 1e-3 ? s.rn.toExponential(1) + " m" : f(s.rn, 4) + " m"],
            [["当前 (θ₁, θ₂, θ₃)", "current (θ₁, θ₂, θ₃)"], `(${dg(s.x[0])}°, ${dg(s.x[1])}°, ${dg(s.x[2])}°)`],
            [["目标点 p_d", "target p_d"], `(${f(t[0], 4)}, ${f(t[1], 4)}, ${f(t[2], 4)}) m`],
            [["JᵀJ 的最小特征值", "smallest eigenvalue of JᵀJ"], Math.min(...ev).toExponential(2)],
            [["状态", "status"], s.done ? api.T("已收敛", "converged") : s.k >= 400 ? api.T("未收敛", "not converged") : api.running ? api.T("迭代中", "iterating") : "—"]];
  },
  setLine(l, pts) { const a = l.geometry.attributes.position, n = Math.min(pts.length, a.count); for (let i = 0; i < n; i++) a.setXYZ(i, pts[i][0], pts[i][1], pts[i][2]); a.needsUpdate = true; l.geometry.setDrawRange(0, n); },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep;
    const ur = api.scene === "ur";
    arm.holder.visible = ur; k.goal.visible = ur; k.trace.visible = ur; k.room.visible = !ur; k.upath.visible = !ur;
    if (k.shown !== api.scene) { k.shown = api.scene; arm.holder.visible = true; api.view(ur ? 35 : 25, 28, ur ? 0.6 : 0.5, arm); arm.holder.visible = ur; }
    if (ur) {
      const th = this.full(s.x);
      arm.set({ shoulder_pan_joint: th[0], shoulder_lift_joint: th[1], elbow_joint: th[2], wrist_1_joint: th[3], wrist_2_joint: th[4], wrist_3_joint: th[5] });
      const t = this.target(api); k.goal.position.set(t[0], t[1], t[2]);
      this.setLine(k.trace, s.trace.slice(-500));
      return;
    }
    k.phone.position.copy(k.P([api.p.ux, api.p.uy, api.p.uz]));
    k.est.position.copy(k.P(s.u));
    this.setLine(k.upath, s.path.map((p) => { const v = k.P(p); return [v.x, v.y, v.z]; }));
  },
});
