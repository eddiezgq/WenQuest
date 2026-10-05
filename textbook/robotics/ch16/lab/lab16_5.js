// 实验 16.5 静力学：τ = Jᵀ F（配 16.5 节）。
// 场景 1（机器人）：零件库的 UR5e 停在 θ* = (30°, −60°, 90°, −120°, −90°, 45°)，法兰盘中心对外施加一个纯力 f
//   （方向由方位角 az、仰角 el 给出，大小 F）。关节力矩 τ = J_vᵀ f（定理 16.5.1，J_v 为几何雅可比的后三行），
//   与 UR5e 的关节力矩上限 150、150、150、28、28、28 N·m（厂商资料）比较；只计外力，不计手臂自重。
//   沿方向 u 按力矩上限能平衡的最大力 F_max(u) = min_i τ_max,i / |(J_vᵀ u)_i|；橙色为单位力矩的力椭球（定理 16.5.2）。
// 场景 2（机器人）：零件库的 Panda 停在 ready 姿态 (0, −45°, 0, −135°, 0, 90°, 45°)。外力作用在手上（沿 x_s）或
//   第 4 个关节处（肘部，沿 y_s）。七个关节力矩传感器的读数 τ = Jᵀ F + 噪声（固定种子的高斯噪声，标准差 σ）。
//   用最小二乘 F̂ = (J_sᵀ)⁺ τ 估计手上的力旋量（式 (16.5.7)）；J 的零空间方向 n 上的残差 |nᵀ τ| > 5σ 时报警：
//   手上的任何力旋量都解释不了这一部分，说明力作用在别处（碰撞检测）。
// 场景 3（生活）：撬棍撬石头：力臂之比 k = a/b，手压下 0.4 m，石头升起 0.4/k m；手上的力 = 石头的重力 / k。
WQ.lab({
  title: ["实验 16.5 静力学：τ = Jᵀ F", "Lab 16.5 Statics: τ = Jᵀ F"],
  goal: ["用雅可比矩阵的转置把末端的力换成关节力矩：看 UR5e 向下能压多大的力、哪个方向最能扛力；用 Panda 的关节力矩传感器反过来估计外力，并发现碰撞。",
         "Turn an end-effector force into joint torques with the transposed Jacobian: how hard the UR5e can press down and in which direction it resists best; then use the Panda's joint-torque sensors the other way round to estimate an external force and detect a collision."],
  view: "3d",
  models: ["B-ARM-UR5E", "B-ARM-PANDA"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 向外施力", "UR5e applying a force"], hide: ["where", "noise", "ratio"],
      problem: { title: ["机器人问题：法兰盘压在工件上，各关节要出多大的力矩", "Robot problem: with the flange pressing on a workpiece, how much torque does each joint need"],
                 text: ["用方位角、仰角和大小设定法兰盘中心对外施加的力（红色箭头）。测量区给出六个关节力矩及其占上限的比例，以及这个方向上按力矩上限能平衡的最大力。橙色是单位关节力矩的力椭球。",
                        "Set the force the flange centre applies (red arrow) by azimuth, elevation and size. The readouts give the six joint torques and their share of the limits, and the largest force the torque limits allow in this direction. The orange body is the force ellipsoid of unit joint torque."] } },
    { id: "panda", robot: true, name: ["Panda 估计外力", "Panda estimating an external force"], hide: ["az", "el", "ratio"],
      params: { fmag: { min: 0, max: 30, value: 10 } },
      problem: { title: ["机器人问题：只靠关节力矩传感器，能否知道谁在推机器人、推在哪里", "Robot problem: from the joint-torque sensors alone, can the robot tell who pushes it and where"],
                 text: ["选择外力作用的位置（0 手上，1 肘部）和大小。测量区给出七个关节力矩读数、按“力作用在手上”估计出的力，以及手上的力解释不了的残差；残差超过 5σ 时报警。",
                        "Choose where the force acts (0 on the hand, 1 on the elbow) and its size. The readouts give the seven torque readings, the force estimated assuming it acts on the hand, and the residual no hand wrench can explain; the alarm goes off above 5σ."] } },
    { id: "lever", name: ["撬棍撬石头", "Prying a stone with a lever"], hide: ["az", "el", "fmag", "where", "noise"],
      problem: { title: ["生活中的例子：省力就费距离", "Everyday example: what you gain in force you lose in distance"],
                 text: ["石头 100 kg。调节力臂之比 k，按“开始”把撬棍的手柄压下 0.4 m。测量区给出手上要用的力、石头升起的高度，以及力的放大倍数与速度的缩小倍数之积。",
                        "The stone weighs 100 kg. Set the lever ratio k and press “Start” to push the handle down 0.4 m. The readouts give the hand force, how high the stone rises, and the product of the force gain and the speed reduction."] } },
  ],
  params: [
    { id: "az", name: ["力的方位角（从 x_s 量起）", "azimuth of the force (from x_s)"], min: -180, max: 180, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "el", name: ["力的仰角（向上为正）", "elevation of the force (up positive)"], min: -90, max: 90, step: 5, value: -90, unit: "°", digits: 0 },
    { id: "fmag", name: ["力的大小", "size of the force"], min: 0, max: 600, step: 1, value: 50, unit: "N", digits: 0 },
    { id: "where", name: ["作用位置：0 手上 / 1 肘部", "where it acts: 0 hand / 1 elbow"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "noise", name: ["传感器噪声 σ", "sensor noise σ"], min: 0.01, max: 0.2, step: 0.01, value: 0.05, unit: "N·m", digits: 2 },
    { id: "ratio", name: ["力臂之比 k = a/b", "lever ratio k = a/b"], min: 1, max: 8, step: 0.5, value: 2, unit: "", digits: 1 },
  ],
  legend: [{ color: "#d62728", name: ["外力", "external force"] }, { color: "#e8912d", name: ["力椭球", "force ellipsoid"] }],
  tasks: [
    { id: "down50", robot: true, text: ["UR5e 向下压 50 N：读出六个关节力矩，确认都在上限以内。", "UR5e pressing down with 50 N: read the six joint torques and check they are all within the limits."],
      demo: { scene: "ur", set: { el: -90, fmag: 50 }, press: [], wait: 3 } },
    { id: "downmax", robot: true, text: ["找出 UR5e 向下最多能压多大的力：某个关节达到上限的 98% 以上，且都不超限。",
                                         "Find the largest downward force of the UR5e: one joint at 98% of its limit or more, none above."],
      demo: { scene: "ur", set: { el: -90, fmag: 228 }, press: [], wait: 3 } },
    { id: "bestdir", robot: true, text: ["找出 UR5e 最能扛力的方向：这个方向上按力矩上限能平衡的力，达到所有方向中最大值的 97% 以上。",
                                         "Find the direction in which the UR5e resists best: the force its torque limits allow there is at least 97% of the largest over all directions."],
      demo: { scene: "ur", set: { az: -120, el: -20 }, press: [], wait: 3 } },
    { id: "hand", robot: true, text: ["Panda：手上受 10 N 以上的力，估计误差小于 1 N，且不报警。", "Panda: with 10 N or more on the hand, the estimate is within 1 N and no alarm goes off."],
      demo: { scene: "panda", set: { where: 0, fmag: 10, noise: 0.05 }, press: [], wait: 3 } },
    { id: "elbow", robot: true, text: ["Panda：肘部被推 10 N 以上，残差超过 5σ，报警。", "Panda: with 10 N or more pushing the elbow, the residual exceeds 5σ and the alarm goes off."],
      demo: { scene: "panda", set: { where: 1, fmag: 15, noise: 0.05 }, press: [], wait: 3 } },
    { id: "lever", text: ["生活场景：用不超过 25 kg 力（245 N）撬起 100 kg 的石头，并记下石头升起的高度。", "Everyday scene: lift the 100 kg stone with no more than a 25 kg force (245 N), and note how high it rises."],
      demo: { scene: "lever", set: { ratio: 4 }, press: ["start"], wait: 4 } },
  ],
  think: ["任务 3 找到的方向，与 16.4 节速度椭球最短的半轴方向有什么关系？为什么最能扛力的方向恰恰是动得最慢的方向？",
          "How is the direction of task 3 related to the shortest semi-axis of the velocity ellipsoid in Section 16.4? Why is the direction that resists best exactly the one that moves slowest?"],

  // ---------------- 公用小函数
  dot(a, b) { return a.reduce((s, x, i) => s + x * b[i], 0); },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  add(a, b) { return a.map((x, i) => x + b[i]); },
  sub(a, b) { return a.map((x, i) => x - b[i]); },
  mul(a, s) { return a.map((x) => x * s); },
  norm(a) { return Math.sqrt(a.reduce((s, x) => s + x * x, 0)); },
  mv(R, v) { return [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]); },
  mm(A, B) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j])); },
  rot(w, t) {
    const c = Math.cos(t), s = Math.sin(t), v = 1 - c, [x, y, z] = w;
    return [[c + x * x * v, x * y * v - z * s, x * z * v + y * s], [y * x * v + z * s, c + y * y * v, y * z * v - x * s], [z * x * v - y * s, z * y * v + x * s, c + z * z * v]];
  },
  // 一条串联臂此刻的各轴（方向 ω_i、轴上一点 q_i），由零位的轴按指数积“从里往外”搬动（16.1 节）
  axesNow(AX, th) {
    let R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p = [0, 0, 0];
    const out = [];
    AX.forEach(([w, q], i) => {
      out.push([this.mv(R, w), this.add(this.mv(R, q), p)]);
      const Ri = this.rot(w, th[i]), pi = this.sub(q, this.mv(Ri, q));
      p = this.add(this.mv(R, pi), p); R = this.mm(R, Ri);
    });
    return { axes: out, R, p };
  },
  UR: { AX() {
    const H1 = 0.163, W1 = 0.138, L1 = 0.425, W2 = 0.131, L2 = 0.392, W3 = 0.127, H2 = 0.1, Y = [0, -1, 0];
    return [[[0, 0, 1], [0, 0, H1]], [Y, [0, -W1, H1]], [Y, [-L1, -W1 + W2, H1]], [Y, [-L1 - L2, -W1 + W2, H1]],
            [[0, 0, -1], [-L1 - L2, -W1 + W2 - W3, H1]], [Y, [-L1 - L2, -W1 + W2 - W3, H1 - H2]]];
  }, MP: [-0.817, -0.234, 0.063], NAMES: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  TH: [30, -60, 90, -120, -90, 45].map((d) => d * Math.PI / 180), TMAX: [150, 150, 150, 28, 28, 28] },
  PA: { AX: [[[0, 0, 1], [0, 0, 0.333]], [[0, 1, 0], [0, 0, 0.333]], [[0, 0, 1], [0, 0, 0.649]], [[0, -1, 0], [0.0825, 0, 0.649]],
             [[0, 0, 1], [0, 0, 1.033]], [[0, -1, 0], [0, 0, 1.033]], [[0, 0, -1], [0.088, 0, 1.033]]],
        MP: [0.088, 0, 0.926], TH: [0, -45, 0, -135, 0, 90, 45].map((d) => d * Math.PI / 180) },
  pointNow(AX, th, P0) {                          // 零位时的点 P0 随整条臂搬到此刻的位置
    const n = this.axesNow(AX, th); return this.add(this.mv(n.R, P0), n.p);
  },
  urJv(api) {                                     // UR5e 在 θ* 处的 J_v（3×6）：第 i 列 ω_i × (p − q_i)
    const n = this.axesNow(this.UR.AX(), this.UR.TH), p = this.add(this.mv(n.R, this.UR.MP), n.p);
    return { p, cols: n.axes.map(([w, q]) => this.cross(w, this.sub(p, q))) };
  },
  dirOf(az, el) { const a = az * Math.PI / 180, e = el * Math.PI / 180; return [Math.cos(e) * Math.cos(a), Math.cos(e) * Math.sin(a), Math.sin(e)]; },
  fmax(cols, u) { return Math.min(...cols.map((c, i) => this.UR.TMAX[i] / Math.max(Math.abs(this.dot(c, u)), 1e-12))); },
  gauss(seed) {                                   // 固定种子的标准正态样本（线性同余 + 博克斯-马勒）
    let s = seed >>> 0; const r = () => { s = (1664525 * s + 1013904223) >>> 0; return (s + 0.5) / 4294967296; };
    return () => Math.sqrt(-2 * Math.log(r())) * Math.cos(2 * Math.PI * r());
  },

  reset(api, s) {
    s.t = 0; s.anim = 0; s.done = false;
    if (api.scene === "ur") {
      const { p, cols } = this.urJv(api), u = this.dirOf(api.p.az, api.p.el), f = this.mul(u, api.p.fmag);
      s.p = p; s.cols = cols; s.u = u; s.tau = cols.map((c) => this.dot(c, f));
      s.ratio = s.tau.map((t, i) => Math.abs(t) / this.UR.TMAX[i]);
      s.Fmax = this.fmax(cols, u);
      if (!this._gmax) { let g = 0; for (let a = -180; a <= 180; a += 5) for (let e = -90; e <= 90; e += 5) g = Math.max(g, this.fmax(cols, this.dirOf(a, e))); this._gmax = g; }
      s.gmax = this._gmax;
      // 单位力矩的力椭球：J_v J_vᵀ 的特征分解，半轴 1/σ_i
      const A = [0, 1, 2].map((i) => [0, 1, 2].map((j) => cols.reduce((t, c) => t + c[i] * c[j], 0)));
      const E = api.la.eigSym(A);
      s.fe = { a: E.values.map((l) => 1 / Math.sqrt(Math.max(l, 1e-12))), D: [0, 1, 2].map((k) => [E.vectors[0][k], E.vectors[1][k], E.vectors[2][k]]) };
    } else if (api.scene === "panda") {
      const AX = this.PA.AX, th = this.PA.TH, n = this.axesNow(AX, th);
      const Js = n.axes.map(([w, q]) => [...w, ...this.mul(this.cross(w, q), -1)]);    // 空间雅可比的七列 (ω_i, −ω_i × q_i)
      const hand = this.add(this.mv(n.R, this.PA.MP), n.p), elbow = n.axes[3][1];
      const atp = api.p.where === 0 ? hand : elbow, f = api.p.where === 0 ? [api.p.fmag, 0, 0] : [0, api.p.fmag, 0];
      const Fs = [...this.cross(atp, f), ...f];
      const g = this.gauss(16052 + Math.round(api.p.noise * 1000));
      s.tau = Js.map((c, i) => (api.p.where === 1 && i >= 4 ? 0 : this.dot(c, Fs)) + api.p.noise * g());
      // 最小二乘：F̂ = (J Jᵀ)⁻¹ J τ（J = J_s，6×7）；零空间方向 n（J n = 0）上的残差
      const JJt = [0, 1, 2, 3, 4, 5].map((i) => [0, 1, 2, 3, 4, 5].map((j) => Js.reduce((t, c) => t + c[i] * c[j], 0)));
      const Jt = [0, 1, 2, 3, 4, 5].map((i) => Js.reduce((t, c, k) => t + c[i] * s.tau[k], 0));
      const F = api.la.mv(api.la.pinv(JJt), Jt);
      s.fhat = F.slice(3); s.mhat = this.sub(F.slice(0, 3), this.cross(hand, s.fhat));    // 对手上那一点的力矩
      // J_sᵀ（7×6）的值域是 6 维，补上的第 7 维就是 n：τ 减去它在值域上的投影 J_sᵀ F̂，剩下的就是 n 方向的残差
      const proj = api.la.mv(Js.map((c) => c.slice()), F);
      s.res = this.norm(this.sub(s.tau, proj)); s.ftrue = f; s.hand = hand; s.elbow = elbow; s.where = api.p.where;
      s.err = api.p.where === 0 ? this.norm(this.sub(s.fhat, f)) : NaN;
    } else {
      s.k = api.p.ratio; s.handF = 100 * 9.81 / s.k;
    }
  },
  update(dt, api, s) {
    if (api.scene !== "lever") { api.stop(); return; }
    s.anim = Math.min(1, s.anim + dt / 2.0);
    if (s.anim >= 1) { s.done = true; api.stop(); }
  },
  readouts(api, s) {
    const f2 = (x) => x.toFixed(2);
    if (api.scene === "ur") {
      if (!s.tau) return [];
      const mx = Math.max(...s.ratio);
      if (api.p.el === -90 && api.p.fmag === 50 && mx < 1) api.done("down50");
      if (api.p.el === -90 && mx >= 0.98 && mx <= 1) api.done("downmax");
      if (s.Fmax >= 0.97 * s.gmax) api.done("bestdir");
      return [[["关节力矩 τ₁…τ₃ / (N·m)", "joint torques τ₁…τ₃ / (N·m)"], s.tau.slice(0, 3).map(f2).join(", ")],
              [["关节力矩 τ₄…τ₆ / (N·m)", "joint torques τ₄…τ₆ / (N·m)"], s.tau.slice(3).map(f2).join(", ")],
              [["占上限的比例", "share of the limit"], s.ratio.map((x) => (x * 100).toFixed(1) + "%").join(", ")],
              [["状态", "status"], mx > 1 ? api.T("超过力矩上限！", "torque limit exceeded!") : api.T("在上限以内", "within the limits")],
              [["这个方向能平衡的最大力", "largest force in this direction"], s.Fmax.toFixed(1) + " N"],
              [["所有方向中的最大值（5° 网格）", "largest over all directions (5° grid)"], s.gmax.toFixed(1) + " N"],
              [["力椭球半轴 / (N 每 N·m)", "force-ellipsoid semi-axes / (N per N·m)"], s.fe.a.map((x) => x.toFixed(3)).join(", ")]];
    }
    if (api.scene === "panda") {
      if (!s.tau) return [];
      const alarm = s.res > 5 * api.p.noise;
      if (s.where === 0 && api.p.fmag >= 10 && s.err < 1 && !alarm) api.done("hand");
      if (s.where === 1 && api.p.fmag >= 10 && alarm) api.done("elbow");
      return [[["关节力矩读数 / (N·m)", "torque readings / (N·m)"], s.tau.map(f2).join(", ")],
              [["实际的力", "actual force"], "(" + s.ftrue.map((x) => x.toFixed(1)).join(", ") + ") N " + (s.where === 0 ? api.T("在手上", "on the hand") : api.T("在肘部", "on the elbow"))],
              [["按“在手上”估计的力", "force estimated as if on the hand"], "(" + s.fhat.map(f2).join(", ") + ") N"],
              [["估计的力矩（对手上那一点）", "estimated moment (about the hand point)"], this.norm(s.mhat).toFixed(2) + " N·m"],
              [["残差 |nᵀτ|", "residual |nᵀτ|"], s.res.toFixed(3) + " N·m  (5σ = " + (5 * api.p.noise).toFixed(2) + ")"],
              [["碰撞报警", "collision alarm"], alarm ? api.T("报警：力不在手上！", "ALARM: the force is not on the hand!") : api.T("正常", "normal")]];
    }
    if (s.done && s.k >= 4) api.done("lever");
    return [[["力臂之比 k", "lever ratio k"], s.k.toFixed(1)], [["石头的重力", "weight of the stone"], "981 N"],
            [["手上要用的力", "hand force"], s.handF.toFixed(0) + " N (" + (s.handF / 9.81).toFixed(1) + " kg)"],
            [["手压下 / 石头升起", "hand down / stone up"], (0.4 * s.anim).toFixed(3) + " m / " + (0.4 * s.anim / s.k).toFixed(3) + " m"],
            [["力的放大 × 速度的缩小", "force gain × speed reduction"], (s.k * (1 / s.k)).toFixed(3)],
            [["状态", "status"], s.done ? api.T("撬起来了", "lifted") : api.running ? api.T("正在压", "pressing") : "—"]];
  },

  // ---------------- 三维
  setup3d(api, keep) {
    const T = api.three, ur = api.m["B-ARM-UR5E"], pa = api.m["B-ARM-PANDA"];
    ur.root.updateMatrixWorld(true); pa.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(ur.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    const GP = new T.Group(); GP.matrixAutoUpdate = false; GP.matrix.copy(pa.nodes.root.matrixWorld); api.st.scene.add(GP); keep.GP = GP;
    keep.arrow = new T.ArrowHelper(new T.Vector3(0, 0, -1), new T.Vector3(), 0.3, 0xd62728, 0.07, 0.04); G.add(keep.arrow);
    keep.parrow = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(), 0.3, 0xd62728, 0.07, 0.04); GP.add(keep.parrow);
    keep.ell = new T.Mesh(new T.SphereGeometry(1, 32, 20), new T.MeshStandardMaterial({ color: 0xe8912d, transparent: true, opacity: 0.25, depthWrite: false }));
    keep.ell.matrixAutoUpdate = false; G.add(keep.ell);
    // 撬棍：支点、木棍、石头、手（放在 UR5e 旁边 (2.5, 4, 0) 处）
    const L = new T.Group(); L.position.set(2.5, 4.0, 0); G.add(L); keep.L = L;
    const m = (c) => new T.MeshStandardMaterial({ color: c });
    keep.fulcrum = new T.Mesh(new T.ConeGeometry(0.12, 0.25, 4), m(0x6e7681)); keep.fulcrum.rotation.x = Math.PI / 2; keep.fulcrum.position.set(0, 0, 0.125); L.add(keep.fulcrum);
    keep.bar = new T.Mesh(new T.BoxGeometry(1, 0.06, 0.06), m(0x8b5a2b)); L.add(keep.bar);
    keep.stone = new T.Mesh(new T.DodecahedronGeometry(0.22), m(0x9aa0a6)); L.add(keep.stone);
    keep.handm = new T.Mesh(new T.SphereGeometry(0.06, 16, 12), m(0xd9a679)); L.add(keep.handm);
    const gr = new T.Mesh(new T.BoxGeometry(2.4, 0.8, 0.02), m(0xb8a27a)); gr.position.set(0, 0, -0.01); L.add(gr);
    keep.box = () => { G.updateMatrixWorld(true); return new T.Box3().setFromObject(gr).expandByScalar(0.3); };
    api.m.leverView = { entry: { robot: {} }, holder: { visible: false }, box: () => keep.box() };
  },
  draw(api, s) {
    const k = api.keep, ur = api.m["B-ARM-UR5E"], pa = api.m["B-ARM-PANDA"], T = api.three;
    if (!k.G) return;
    const sc = api.scene;
    if (k.shown !== sc) {
      k.shown = sc;
      if (sc === "ur") api.view(35, 25, 0.6, ur); else if (sc === "panda") api.view(-60, 20, 0.7, pa); else api.view(0, 12, 0.95, api.m.leverView);
    }
    ur.holder.visible = sc === "ur"; pa.holder.visible = sc === "panda"; k.L.visible = sc === "lever";
    k.arrow.visible = sc === "ur" && !!s.u; k.ell.visible = sc === "ur" && !!s.fe; k.parrow.visible = sc === "panda" && !!s.tau;
    if (sc === "ur" && s.u) {
      const o = {}; this.UR.NAMES.forEach((n, i) => { o[n] = this.UR.TH[i]; }); ur.set(o);
      const L = 0.2 + 0.3 * Math.min(1, api.p.fmag / 300), d = new T.Vector3(...s.u);
      k.arrow.position.set(...this.sub(s.p, this.mul(s.u, L))); k.arrow.setDirection(d); k.arrow.setLength(L, 0.08, 0.05);
      const A = s.fe.D.map((v, i) => this.mul(v, s.fe.a[i] * 0.03));
      k.ell.matrix.set(A[0][0], A[1][0], A[2][0], s.p[0], A[0][1], A[1][1], A[2][1], s.p[1], A[0][2], A[1][2], A[2][2], s.p[2], 0, 0, 0, 1);
      k.ell.matrixWorldNeedsUpdate = true;
    }
    if (sc === "panda" && s.tau) {
      const o = {}; this.PA.TH.forEach((x, i) => { o[`joint${i + 1}`] = x; }); pa.set(o);
      const at = s.where === 0 ? s.hand : s.elbow, u = this.mul(s.ftrue, 1 / Math.max(this.norm(s.ftrue), 1e-9)), L = 0.08 + 0.3 * api.p.fmag / 30;
      k.parrow.position.set(...this.sub(at, this.mul(u, L))); k.parrow.setDirection(new T.Vector3(...u)); k.parrow.setLength(L, 0.06, 0.035);
    }
    if (sc === "lever" && s.k) {
      const a = 1.6 * s.k / (1 + s.k), b = 1.6 / (1 + s.k), drop = 0.4 * (s.anim || 0);
      // 木棍：支点在 (0, 0, 0.25)，手端在左、石头端在右；未压时手端比支点高 0.35 m，压下 drop 后高 0.35 − drop
      const base = 0.25, tilt = Math.atan2(0.35 - drop, a);
      const hp = [-a * Math.cos(tilt), 0, base + a * Math.sin(tilt)], sp = [b * Math.cos(tilt), 0, base - b * Math.sin(tilt)];
      k.bar.scale.set(a + b, 1, 1); k.bar.position.set((hp[0] + sp[0]) / 2, 0, (hp[2] + sp[2]) / 2); k.bar.rotation.set(0, tilt, 0);
      k.handm.position.set(hp[0], 0, hp[2] + 0.07); k.stone.position.set(sp[0] + 0.05, 0, Math.max(0.22, sp[2] + 0.22));
    }
  },
});
