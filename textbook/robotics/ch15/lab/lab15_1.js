// 实验 15.1 UR5e 的数值逆解：李群上的牛顿-拉夫森迭代（配 15.1 节）。
// 旋量轴与零位位姿取表 12.1.1；目标位姿由 θ* = (30°, −60°, 90°, −120°, −90°, 45°) 算出（算例 14.5.1、15.1.2）。
// 每一步：误差旋量 V_b = log(T⁻¹T_d)（定义 15.1.1），物体雅可比 J_b = [Ad_{T⁻¹}] J_s（式 (15.1.4)、(15.1.7)），
// 解 J_b Δθ = V_b（式 (15.1.8)）。J_b 的条件数超过 10¹² 时报告奇异。所得的解用 14.5 节的解析逆解编号（同表 14.5.1）。
// 生活场景：手持三轴云台（偏航 z、横滚 x、俯仰 y，R = Rz Rx Ry），相机光轴为 x，SO(3) 上的同一种迭代：J_b Δq = log(Rᵀ R_d)。
WQ.lab({
  title: ["实验 15.1 UR5e 的数值逆解：李群上的牛顿-拉夫森迭代", "Lab 15.1 Numerical IK of the UR5e: Newton-Raphson on a Lie group"],
  goal: ["看牛顿-拉夫森法怎样一步步把 UR5e 的末端送到目标位姿，误差的有效数字每步约翻一番；起点不同，得到的解可能不同；起点奇异时迭代无法开始。",
         "Watch Newton-Raphson bring the UR5e step by step to the target pose, the digits of the error roughly doubling each step; different starts may give different solutions; a singular start cannot begin."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 位姿逆解", "UR5e pose IK"], hide: ["az", "el"],
      problem: { title: ["机器人问题：法兰盘到达目标位姿", "Robot problem: bring the flange to the target pose"],
                 text: ["目标是算例 15.1.2 的位姿（红球为法兰盘中心，红色箭头为法兰盘法线）。选择起始姿态，按“迭代一步”或“求解”。",
                        "The target is the pose of Example 15.1.2 (red ball = flange centre, red arrow = flange normal). Choose a start and press “One step” or “Solve”."] } },
    { id: "gimbal", name: ["手持云台", "Handheld gimbal"], hide: ["start"],
      problem: { title: ["生活中的例子：把相机对准花，画面保持水平", "Everyday example: aim the camera at a flower, keep the horizon level"],
                 text: ["云台有偏航、横滚、俯仰三个电机。目标姿态：相机光轴（红色）指向花，相机的横轴（绿色）保持水平。用滑块移动花的方位和高度。",
                        "The gimbal has yaw, roll and pitch motors. Target orientation: the optical axis (red) points at the flower and the camera's side axis (green) stays level. Move the flower with the sliders."] } },
  ],
  params: [
    { id: "start", name: ["起始姿态：0 当前关节角 / 1 大臂竖直 / 2 习题 14.5.5 / 3 零位", "Start: 0 current / 1 upper arm up / 2 Exercise 14.5.5 / 3 home zero"], min: 0, max: 3, step: 1, value: 0, unit: "", digits: 0 },
    { id: "az", name: ["花的方位角", "flower azimuth"], min: -150, max: 150, step: 1, value: 60, unit: "°", digits: 0 },
    { id: "el", name: ["花的仰角", "flower elevation"], min: -60, max: 60, step: 1, value: -25, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "step", name: ["迭代一步", "One step"] }, { id: "start", name: ["求解", "Solve"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "#cf222e", name: ["目标", "target"] }, { color: "#c98f00", name: ["法兰盘中心的轨迹", "flange trace"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 15.1.2：从当前关节角出发，4 次迭代收敛到表 14.5.1 的第 3 组。", "Example 15.1.2: from the current angles, converge in 4 iterations to solution 3 of Table 14.5.1."],
      demo: { scene: "ur", set: { start: 0 }, press: ["start"], wait: 12 } },
    { id: "other", robot: true, text: ["从习题 14.5.5 的关节角出发求解，收敛到肩部另一侧的第 5 组。", "Start from the angles of Exercise 14.5.5 and converge to solution 5, on the other side of the shoulder."],
      demo: { scene: "ur", set: { start: 2 }, press: ["start"], wait: 12 } },
    { id: "sing", robot: true, text: ["从零位出发：J_b 奇异，迭代无法开始。", "Start from the home zero: J_b is singular and the iteration cannot begin."],
      demo: { scene: "ur", set: { start: 3 }, press: ["step"], wait: 1 } },
    { id: "digits", robot: true, text: ["用“迭代一步”逐步求解（至少 3 次单步），记下每步误差的指数。", "Solve with “One step” (at least 3 single steps) and note the exponent of the error at each step."],
      demo: { scene: "ur", set: { start: 0 }, press: ["step", "step", "step", "step", "step"], wait: 1 } },
    { id: "gimbal", text: ["生活场景：用云台把相机对准花，姿态误差小于 10⁻⁶ rad。", "Everyday scene: aim the camera at the flower with the gimbal, orientation error below 10⁻⁶ rad."],
      demo: { scene: "gimbal", set: { az: 60, el: -25 }, press: ["start"], wait: 4 } },
  ],
  think: ["从大臂竖直的姿态出发，第一步的误差下降得比从当前关节角出发慢得多，为什么？用引理 15.1.1 解释：离解远时，J_b 与误差旋量的真实导数差多少？",
          "From the upper-arm-up start the first step reduces the error much less than from the current angles. Why? Use Lemma 15.1.1: far from the solution, how much does J_b differ from the true derivative of the error twist?"],

  // ---------------- UR5e 几何（表 12.1.1）与 SE(3) 运算
  G: { H1: 0.163, W1: 0.138, L1: 0.425, W2: 0.131, L2: 0.392, W3: 0.127, H2: 0.1, W4: 0.1 },
  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  STARTS: [[25, -55, 85, -115, -85, 40], [0, -90, 90, -90, -90, 0], [-120, -100, -80, -60, 90, 60], [0, 0, 0, 0, 0, 0]],
  STAR: [30, -60, 90, -120, -90, 45],
  dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  add(a, b) { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; },
  sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; },
  mul(a, s) { return [a[0] * s, a[1] * s, a[2] * s]; },
  norm(a) { return Math.hypot(a[0], a[1], a[2]); },
  mv(R, v) { return [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]); },
  mm(A, B) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j])); },
  tr(A) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[j][i])); },
  rot(w, t) {
    const c = Math.cos(t), s = Math.sin(t), v = 1 - c, [x, y, z] = w;
    return [[c + x * x * v, x * y * v - z * s, x * z * v + y * s], [y * x * v + z * s, c + y * y * v, y * z * v - x * s], [z * x * v - y * s, z * y * v + x * s, c + z * z * v]];
  },
  wrap(a) { return Math.atan2(Math.sin(a), Math.cos(a)); },
  AX() {
    const g = this.G, Y = [0, -1, 0];
    return [[[0, 0, 1], [0, 0, g.H1]], [Y, [0, -g.W1, g.H1]], [Y, [-g.L1, -g.W1 + g.W2, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2, g.H1]],
            [[0, 0, -1], [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1 - g.H2]]];
  },
  M() { const g = this.G; return { R: [[1, 0, 0], [0, -1, 0], [0, 0, -1]], p: [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3 - g.W4, g.H1 - g.H2] }; },
  E(i, t) { const [w, q] = this.AX()[i], R = this.rot(w, t); return { R, p: this.sub(q, this.mv(R, q)) }; },
  comp(A, B) { return { R: this.mm(A.R, B.R), p: this.add(this.mv(A.R, B.p), A.p) }; },
  inv(A) { const Rt = this.tr(A.R); return { R: Rt, p: this.mul(this.mv(Rt, A.p), -1) }; },
  act(A, x) { return this.add(this.mv(A.R, x), A.p); },
  fk(th) { let T = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] }; th.forEach((t, i) => { T = this.comp(T, this.E(i, t)); }); return this.comp(T, this.M()); },
  logR(R) {                                       // SO(3) 的对数（定理 6.2.2），θ ≈ π 时单独处理
    const c = Math.max(-1, Math.min(1, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)), th = Math.acos(c);
    const d = [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]];
    if (th < 1e-9) return this.mul(d, 0.5);
    if (Math.PI - th < 1e-6) {
      const B = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (R[i][j] + (i === j ? 1 : 0)) / 2)), k = [0, 1, 2].reduce((a, i) => (B[i][i] > B[a][a] ? i : a), 0);
      return this.mul([B[0][k], B[1][k], B[2][k]], th / Math.sqrt(B[k][k]));
    }
    return this.mul(d, th / (2 * Math.sin(th)));
  },
  log6(T) {                                       // SE(3) 的对数（定理 6.4.3），返回 (ω, v)
    const wt = this.logR(T.R), th = this.norm(wt);
    if (th < 1e-12) return [0, 0, 0, ...T.p];
    const w = this.mul(wt, 1 / th), p = T.p, wp = this.cross(w, p), wwp = this.cross(w, wp);
    const k = 1 / th - 0.5 / Math.tan(th / 2);                 // G⁻¹ = I/θ − [ω]/2 + (1/θ − cot(θ/2)/2)[ω]²，式 (6.4.8)
    const v = [0, 1, 2].map((i) => th * (p[i] / th - 0.5 * wp[i] + k * wwp[i]));
    return [...wt, ...v];
  },
  jb(th) {                                        // 物体雅可比：J_s 的各列再乘 [Ad_{T⁻¹}]
    const A = this.AX(), T = this.fk(th), Rt = this.tr(T.R), out = [];
    let P = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] };
    for (let i = 0; i < 6; i++) {
      const w = this.mv(P.R, A[i][0]), q = this.act(P, A[i][1]), v = this.mul(this.cross(w, q), -1);
      out.push([...this.mv(Rt, w), ...this.mv(Rt, this.sub(v, this.cross(T.p, w)))]);
      P = this.comp(P, this.E(i, th[i]));
    }
    return [0, 1, 2, 3, 4, 5].map((r) => out.map((c) => c[r]));     // 6×6，第 i 列为 J_bi
  },
  solve(A, b) {                                   // 列主元高斯消去
    const n = b.length, M = A.map((r, i) => [...r, b[i]]);
    for (let i = 0; i < n; i++) {
      let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(M[j][i]) > Math.abs(M[p][i])) p = j;
      [M[i], M[p]] = [M[p], M[i]];
      for (let j = i + 1; j < n; j++) { const f = M[j][i] / M[i][i]; for (let k = i; k <= n; k++) M[j][k] -= f * M[i][k]; }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let s = M[i][n]; for (let k = i + 1; k < n; k++) s -= M[i][k] * x[k]; x[i] = s / M[i][i]; }
    return x;
  },
  // ---------------- 14.5 节的解析逆解（只用来给数值解编号，次序同表 14.5.1）
  sp1(w, r, p, q) {
    const u = this.sub(p, r), v = this.sub(q, r), up = this.sub(u, this.mul(w, this.dot(w, u))), vp = this.sub(v, this.mul(w, this.dot(w, v)));
    return this.norm(up) < 1e-12 ? 0 : Math.atan2(this.dot(w, this.cross(up, vp)), this.dot(up, vp));
  },
  sp2(w1, w2, r, p, q) {
    const u = this.sub(p, r), v = this.sub(q, r), k = this.dot(w1, w2), den = k * k - 1;
    const a = (k * this.dot(w2, u) - this.dot(w1, v)) / den, b = (k * this.dot(w1, v) - this.dot(w2, u)) / den, n = this.cross(w1, w2);
    const g2 = (this.dot(u, u) - a * a - b * b - 2 * a * b * k) / this.dot(n, n);
    if (g2 < -1e-10) return [];
    const gs = g2 <= 1e-10 ? [0, 0] : [Math.sqrt(g2), -Math.sqrt(g2)];
    return gs.map((g) => { const c = this.add(r, this.add(this.add(this.mul(w1, a), this.mul(w2, b)), this.mul(n, g)));
      return [this.sp1(w1, r, c, q), this.sp1(w2, r, p, c)]; });
  },
  sp3(w, r, p, q, d) {
    const u = this.sub(p, r), v = this.sub(q, r), up = this.sub(u, this.mul(w, this.dot(w, u))), vp = this.sub(v, this.mul(w, this.dot(w, v)));
    const d2 = d * d - Math.pow(this.dot(w, this.sub(p, q)), 2), nu = this.norm(up), nv = this.norm(vp);
    const t0 = Math.atan2(this.dot(w, this.cross(up, vp)), this.dot(up, vp)), c = (nu * nu + nv * nv - d2) / (2 * nu * nv);
    if (d2 < -1e-12 || Math.abs(c) > 1 + 1e-12) return [];
    const ph = Math.atan2(Math.sqrt(Math.max(0, 1 - c * c)), Math.max(-1, Math.min(1, c)));
    return ph < 1e-9 ? [t0] : [t0 + ph, t0 - ph];
  },
  chain(th) {
    const A = this.AX(), g = this.G, Ts = [{ R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] }];
    th.forEach((t, i) => Ts.push(this.comp(Ts[i], this.E(i, t))));
    const q = A.map((x) => x[1]);
    return [[0, [0, 0, 0]], [0, q[0]], [1, q[1]], [2, this.add(q[1], [-g.L1, 0, 0])], [2, q[2]], [3, q[3]], [4, q[4]], [5, q[5]], [6, this.add(q[5], [0, -g.W4, 0])]]
      .map(([k, p]) => this.act(Ts[k], p));
  },
  elbowUp(th) {
    const P = this.chain(th), sh = P[2], el = P[4], wr = P[5], ax = this.mv(this.rot([0, 0, 1], th[0]), [0, -1, 0]);
    let n = this.cross(ax, this.sub(wr, sh));
    if (n[2] < 0) n = this.mul(n, -1);
    return this.dot(this.sub(el, sh), n) > 0;
  },
  ik(Td) {
    const g = this.G, A = this.AX(), Y = [0, -1, 0], d4 = g.W1 - g.W2 + g.W3, out = [];
    const yb = [Td.R[0][1], Td.R[1][1], Td.R[2][1]], pw = this.sub(Td.p, this.mul(yb, g.W4)), rho = Math.hypot(pw[0], pw[1]);
    if (rho < d4 - 1e-12) return out;
    const base = Math.atan2(pw[0], -pw[1]), gam = Math.atan2(Math.sqrt(Math.max(0, rho * rho - d4 * d4)), d4);
    [[1, base + gam], [-1, base - gam]].forEach(([s1, t1]) => {
      const E1i = this.E(0, -t1), Rg = this.mm(this.mm(E1i.R, Td.R), this.tr(this.M().R)), v = this.mv(this.tr(Rg), Y);
      const P56 = A[5][1];
      this.sp2(A[4][0], A[5][0], P56, this.add(P56, v), this.add(P56, Y)).forEach(([t5, t6]) => {
        const gg = this.comp(this.comp(this.comp(this.comp(E1i, Td), this.inv(this.M())), this.E(5, -t6)), this.E(4, -t5));
        const p4 = this.act(gg, A[3][1]);
        this.sp3(A[2][0], A[2][1], A[3][1], A[1][1], this.norm(this.sub(p4, A[1][1]))).forEach((t3) => {
          const t2 = this.sp1(A[1][0], A[1][1], this.act(this.E(2, t3), A[3][1]), p4);
          const h = this.comp(this.inv(this.comp(this.E(1, t2), this.E(2, t3))), gg);
          const t4 = this.sp1(A[3][0], A[3][1], A[5][1], this.act(h, A[5][1]));
          const th = [t1, t2, t3, t4, t5, t6].map((x) => this.wrap(x));
          out.push({ th, sh: s1, nf: t5 > 0, up: this.elbowUp(th) });
        });
      });
    });
    out.sort((a, b) => (b.sh - a.sh) || (Number(b.nf) - Number(a.nf)) || (Number(b.up) - Number(a.up)));
    return out;
  },
  target() { return this.fk(this.STAR.map((d) => d * Math.PI / 180)); },

  // ---------------- 云台：R = Rz(q₁) Rx(q₂) Ry(q₃)，相机光轴为 x
  gR(q) { return this.mm(this.mm(this.rot([0, 0, 1], q[0]), this.rot([1, 0, 0], q[1])), this.rot([0, 1, 0], q[2])); },
  gTarget(api) {
    const a = api.p.az * Math.PI / 180, e = api.p.el * Math.PI / 180, x = [Math.cos(e) * Math.cos(a), Math.cos(e) * Math.sin(a), Math.sin(e)];
    let y = this.cross([0, 0, 1], x); y = this.mul(y, 1 / this.norm(y));
    const z = this.cross(x, y);
    return { R: [[x[0], y[0], z[0]], [x[1], y[1], z[1]], [x[2], y[2], z[2]]], dir: x };
  },
  gJb(q) {                                        // 物体雅可比的三列：俯仰 e_y，横滚 Ry(q₃)ᵀe_x，偏航 (Rx(q₂)Ry(q₃))ᵀe_z
    const Ry = this.rot([0, 1, 0], q[2]), Rxy = this.mm(this.rot([1, 0, 0], q[1]), Ry);
    const c1 = this.mv(this.tr(Rxy), [0, 0, 1]), c2 = this.mv(this.tr(Ry), [1, 0, 0]), c3 = [0, 1, 0];
    return [0, 1, 2].map((r) => [c1[r], c2[r], c3[r]]);
  },

  // ---------------- 迭代
  reset(api, s) {
    s.k = 0; s.done = false; s.sing = false; s.manual = 0; s.clock = 0; s.hist = [];
    s.th = this.STARTS[api.p.start].map((d) => d * Math.PI / 180);
    s.q = [0, 0.15, 0.35];                                       // 云台的起始姿态（弧度）
    this.measure(api, s);
    s.trace = [this.fk(s.th).p];
  },
  measure(api, s) {
    if (api.scene === "gimbal") {
      const Td = this.gTarget(api), w = this.logR(this.mm(this.tr(this.gR(s.q)), Td.R));
      s.ew = this.norm(w); s.ev = 0; s.V = w;
    } else {
      const V = this.log6(this.comp(this.inv(this.fk(s.th)), this.target()));
      s.V = V; s.ew = this.norm(V.slice(0, 3)); s.ev = this.norm(V.slice(3));
    }
    if (s.ew < 1e-13 && s.ev < 1e-13) s.done = true;
    if (s.hist.length === s.k) s.hist.push(Math.hypot(s.ew, s.ev));
  },
  step(api, s) {
    if (s.done || s.sing) return;
    if (api.scene === "gimbal") {
      const J = this.gJb(s.q), det = J[0][0] * (J[1][1] * J[2][2] - J[1][2] * J[2][1]) - J[0][1] * (J[1][0] * J[2][2] - J[1][2] * J[2][0]) + J[0][2] * (J[1][0] * J[2][1] - J[1][1] * J[2][0]);
      if (Math.abs(det) < 1e-9) { s.sing = true; return; }
      const d = this.solve(J, s.V);
      s.q = s.q.map((x, i) => x + d[i]);
    } else {
      const J = this.jb(s.th), sv = api.la.svd(J).s;
      if (sv[5] < 1e-12 * sv[0]) { s.sing = true; s.sv = sv; return; }
      const d = this.solve(J, s.V);
      s.th = s.th.map((x, i) => x + d[i]);
      s.trace.push(this.fk(s.th).p);
    }
    s.k += 1;
    this.measure(api, s);
    if (s.k >= 60) s.done = true;
  },
  action(id, api, s) { if (id === "step") { this.step(api, s); s.manual += 1; } },
  update(dt, api, s) {
    s.clock += dt;
    while (s.clock >= 0.35 && api.running) {
      s.clock -= 0.35;
      this.step(api, s);
      if (s.done || s.sing) api.stop();
    }
  },
  readouts(api, s) {
    const sci = (x) => (x === 0 ? "0" : x.toExponential(1)), dg = (x) => (x * 180 / Math.PI).toFixed(2) + "°";
    const status = s.sing ? api.T("奇异：J_b 不可逆，无法迭代", "singular: J_b not invertible, cannot iterate")
      : s.done ? api.T("已收敛", "converged") : api.running ? api.T("迭代中", "iterating") : "—";
    if (api.scene === "gimbal") {
      if (s.done && s.ew < 1e-6) api.done("gimbal");
      return [[["迭代次数 k", "iteration k"], String(s.k)], [["姿态误差 ‖ω_b‖", "orientation error ‖ω_b‖"], sci(s.ew) + " rad"],
              [["偏航、横滚、俯仰", "yaw, roll, pitch"], s.q.map(dg).join(", ")],
              [["误差的变化", "error history"], s.hist.slice(0, 7).map(sci).join(" → ")], [["状态", "status"], status]];
    }
    const rows = [[["迭代次数 k", "iteration k"], String(s.k)], [["‖ω_b‖", "‖ω_b‖"], sci(s.ew) + " rad"], [["‖v_b‖", "‖v_b‖"], sci(s.ev) + " m"],
                  [["θ₁, θ₂, θ₃", "θ₁, θ₂, θ₃"], s.th.slice(0, 3).map(dg).join(", ")], [["θ₄, θ₅, θ₆", "θ₄, θ₅, θ₆"], s.th.slice(3).map(dg).join(", ")],
                  [["‖V_b‖ 的变化", "‖V_b‖ history"], s.hist.slice(0, 8).map(sci).join(" → ")]];
    if (s.done) {
      const sols = this.ik(this.target()), k = sols.findIndex((x) => x.th.every((v, i) => Math.abs(this.wrap(v - s.th[i])) < 1e-6));
      const lab = k >= 0 ? `${k + 1}（${sols[k].sh > 0 ? "A" : "B"} · ${sols[k].up ? api.T("上", "up") : api.T("下", "down")} · ${sols[k].nf ? api.T("不翻", "no flip") : api.T("翻", "flip")}）` : "—";
      rows.push([["表 14.5.1 中的编号（肩 · 肘 · 腕）", "number in Table 14.5.1 (shoulder · elbow · wrist)"], lab]);
      if (api.p.start === 0 && k === 2 && s.k === 4) api.done("ex");
      if (api.p.start === 2 && k === 4) api.done("other");
      if (s.manual >= 3 && k >= 0) api.done("digits");
    }
    if (s.sing) {
      if (api.p.start === 3) api.done("sing");
      if (s.sv) rows.push([["J_b 的最小奇异值", "smallest singular value of J_b"], sci(s.sv[5])]);
    }
    rows.push([["状态", "status"], status]);
    return rows;
  },

  // ---------------- 三维
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    arm.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    const red = new T.MeshStandardMaterial({ color: 0xcf222e });
    keep.goal = new T.Mesh(new T.SphereGeometry(0.02, 20, 14), red); G.add(keep.goal);
    keep.normal = new T.ArrowHelper(new T.Vector3(0, 0, 1), new T.Vector3(), 0.15, 0xcf222e, 0.04, 0.025); G.add(keep.normal);
    const g = new T.BufferGeometry(); g.setAttribute("position", new T.BufferAttribute(new Float32Array(200 * 3), 3)); g.setDrawRange(0, 0);
    keep.trace = new T.Line(g, new T.LineBasicMaterial({ color: 0xc98f00 })); keep.trace.frustumCulled = false; G.add(keep.trace);
    // 云台：手柄、偏航臂、横滚臂、俯仰架与相机；三根轴交于相机中心 C
    const C = [0.35, -0.2, 0.45], mat = (c) => new T.MeshStandardMaterial({ color: c });
    const gim = new T.Group(); gim.position.set(...C); G.add(gim); keep.gim = gim;
    const handle = new T.Mesh(new T.CylinderGeometry(0.018, 0.022, 0.2, 20), mat(0x30363d)); handle.rotation.x = Math.PI / 2; handle.position.set(0, 0, -0.25); gim.add(handle);
    const yaw = new T.Group(); yaw.position.set(0, 0, 0); gim.add(yaw); keep.yaw = yaw;
    const yawArm = new T.Mesh(new T.BoxGeometry(0.012, 0.012, 0.13), mat(0x58a6ff)); yawArm.position.set(-0.07, 0, -0.08); yaw.add(yawArm);
    const yawTop = new T.Mesh(new T.BoxGeometry(0.08, 0.012, 0.012), mat(0x58a6ff)); yawTop.position.set(-0.035, 0, -0.145); yaw.add(yawTop);
    const yawPost = new T.Mesh(new T.CylinderGeometry(0.014, 0.014, 0.03, 16), mat(0x58a6ff)); yawPost.rotation.x = Math.PI / 2; yawPost.position.set(0, 0, -0.145); yaw.add(yawPost);
    const roll = new T.Group(); yaw.add(roll); keep.roll = roll;
    const rollArm = new T.Mesh(new T.BoxGeometry(0.012, 0.11, 0.012), mat(0xd29922)); rollArm.position.set(-0.07, 0.0, 0); roll.add(rollArm);
    const rollArm2 = new T.Mesh(new T.BoxGeometry(0.07, 0.012, 0.012), mat(0xd29922)); rollArm2.position.set(-0.035, 0.055, 0); roll.add(rollArm2);
    const pitch = new T.Group(); roll.add(pitch); keep.pitch = pitch;
    const cam = new T.Mesh(new T.BoxGeometry(0.07, 0.05, 0.045), mat(0x1f2328)); pitch.add(cam);
    const lens = new T.Mesh(new T.CylinderGeometry(0.016, 0.016, 0.04, 20), mat(0x6e7681)); lens.rotation.z = Math.PI / 2; lens.position.set(0.05, 0, 0); pitch.add(lens);
    pitch.add(new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(0.07, 0, 0), 0.1, 0xd62728, 0.025, 0.015));
    pitch.add(new T.ArrowHelper(new T.Vector3(0, 1, 0), new T.Vector3(0, 0.03, 0), 0.08, 0x2ca02c, 0.02, 0.012));
    const fl = new T.Group(); G.add(fl); keep.flower = fl;
    const head = new T.Mesh(new T.SphereGeometry(0.025, 16, 12), mat(0xe8590c)); fl.add(head);
    const stem = new T.Mesh(new T.CylinderGeometry(0.004, 0.004, 0.2, 8), mat(0x2f9e44)); stem.rotation.x = Math.PI / 2; stem.position.set(0, 0, -0.1); fl.add(stem);
    keep.C = C;
    G.updateMatrixWorld(true);
    api.m.gimbalView = { entry: { robot: {} }, holder: { visible: false },
      box: () => { G.updateMatrixWorld(true); const b = new T.Box3().setFromObject(gim); b.expandByObject(fl); return b.expandByScalar(0.02); } };
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep, ur = api.scene === "ur";
    if (!k.G) return;
    arm.holder.visible = ur; k.goal.visible = ur; k.normal.visible = ur; k.trace.visible = ur; k.gim.visible = !ur; k.flower.visible = !ur;
    if (k.shown !== api.scene) { k.shown = api.scene; arm.holder.visible = true; if (ur) api.view(35, 25, 0.6, arm); else api.view(30, 18, 1.0, api.m.gimbalView); arm.holder.visible = ur; }
    if (ur) {
      const o = {}; this.J.forEach((n, i) => { o[n] = s.th[i]; }); arm.set(o);
      const Td = this.target(), n = [Td.R[0][1], Td.R[1][1], Td.R[2][1]];
      k.goal.position.set(...Td.p); k.normal.position.set(...Td.p); k.normal.setDirection(new api.three.Vector3(...n));
      const a = k.trace.geometry.attributes.position, pts = s.trace.slice(-200);
      pts.forEach((p, i) => a.setXYZ(i, p[0], p[1], p[2])); a.needsUpdate = true; k.trace.geometry.setDrawRange(0, pts.length);
      return;
    }
    k.yaw.rotation.set(0, 0, s.q[0]); k.roll.rotation.set(s.q[1], 0, 0); k.pitch.rotation.set(0, s.q[2], 0);
    const d = this.gTarget(api).dir;
    k.flower.position.set(k.C[0] + 0.35 * d[0], k.C[1] + 0.35 * d[1], k.C[2] + 0.35 * d[2]);
  },
});
