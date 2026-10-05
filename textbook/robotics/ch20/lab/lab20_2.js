// 实验 20.2 脚不动，机身动（配 20.2 节）。零件库 Go2 与 G1 三维模型。
// 场景“机身位姿”：四只脚的足端中心固定在站立位置 (±0.1934, ±0.142, 0.022) m（{s}，z 向上，地面 z = 0）；滑块给出机身原点的
//   侧移 y、高度 z 和横滚 φ、俯仰 ϑ、偏航 ψ（R_sb = Rot(z,ψ) Rot(y,ϑ) Rot(x,φ)）。按定理 20.2.1：p_{b,i} = T_sb⁻¹ p_{s,i}，逐腿求逆解
//   （与实验 20.1 相同的公式），限位取模型关节表。机身在三维中的放置：基座节点的世界矩阵 = C·T_sb，C 把模型坐标 (x, y, z) 换成
//   世界坐标 (x, z, −y)；由站立时记下的“基座在 holder 中的矩阵”反求 holder 的位姿。
//   “开始”：机身以 V_b = (0.2, −0.3, 0.1, 0.05, 0.02, −0.04)（rad/s、m/s，算例 20.2.2）运动 1.5 s，右后脚可设打滑速度（沿 x_s），
//   每一步由关节角的变化求关节速度，用式 (20.2.8) 的最小二乘估计 V_b，显示估计误差和四条腿的残差。
// 生活场景“扎马步”：G1 两脚不动，骨盆竖直下降 gdz、侧移 gdy（不转动）；每条腿 6 个关节，用牛顿迭代（差商雅可比）
//   使踝横滚连杆的位姿保持在站立时的位置。
WQ.lab({
  title: ["实验 20.2 脚不动，机身动", "Lab 20.2 Feet planted, body moving"],
  goal: ["四只脚踩在原地，改变机身的位置和姿态，看 12 个关节怎样随之变化、机身能动多大范围；用腿式里程计由关节速度估计机身的速度，并由残差找出打滑的脚。",
         "With the four feet planted, change the body's position and orientation; see how the 12 joints follow and how far the body can go; estimate the body velocity from the joint rates by leg odometry and find a slipping foot from the residuals."],
  view: "3d",
  models: ["B-LEG-GO2", "B-HUM-G1"],
  scenes: [
    { id: "pose", robot: true, name: ["Go2 机身位姿", "Go2 body pose"], hide: ["gdz", "gdy"],
      problem: { title: ["机器人问题：抬头看桌面、压低身子钻过去", "Robot problem: look up at a table, crouch to pass under it"],
                 text: ["四只脚不动，只改变机身的位姿。每条腿由“脚在机身坐标系中的位置”单独求逆解；按“开始”机身晃动，腿式里程计估计机身速度。",
                        "Feet stay put; only the body pose changes. Each leg is solved on its own from where its foot lies in the body frame; press Start to sway the body and estimate its velocity by leg odometry."] } },
    { id: "life", name: ["生活：扎马步", "Everyday: horse stance"], hide: ["by", "bz", "roll", "pitch", "yaw", "slip"],
      problem: { title: ["生活中的例子：两脚生根，身体下蹲", "Everyday example: feet rooted, body lowered"],
                 text: ["G1 代表人。两只脚贴在地上不动，骨盆下降、左右移动，两条腿的 12 个关节跟着变：这也是一个并联机构。",
                        "G1 stands for a person. Both feet stay flat on the ground while the pelvis lowers and shifts; the 12 leg joints follow: another parallel mechanism."] } },
  ],
  params: [
    { id: "by", name: ["机身侧移 y", "body shift y"], min: -0.10, max: 0.10, step: 0.005, value: 0, unit: "m", digits: 3 },
    { id: "bz", name: ["机身高度 z", "body height z"], min: 0.08, max: 0.44, step: 0.005, value: 0.287, unit: "m", digits: 3 },
    { id: "roll", name: ["横滚 φ", "roll φ"], min: -60, max: 60, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "pitch", name: ["俯仰 ϑ（负为抬头）", "pitch ϑ (negative: nose up)"], min: -45, max: 45, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "yaw", name: ["偏航 ψ", "yaw ψ"], min: -70, max: 70, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "slip", name: ["右后脚打滑速度", "rear-right slip speed"], min: 0, max: 0.10, step: 0.01, value: 0, unit: "m/s", digits: 2 },
    { id: "gdz", name: ["G1 骨盆下降", "G1 pelvis drop"], min: 0.02, max: 0.25, step: 0.01, value: 0.02, unit: "m", digits: 2 },
    { id: "gdy", name: ["G1 骨盆侧移", "G1 pelvis shift"], min: -0.08, max: 0.08, step: 0.005, value: 0, unit: "m", digits: 3 },
  ],
  buttons: [{ id: "start", name: ["开始（机身晃动 1.5 s）", "Start (body sways 1.5 s)"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "up", robot: true, text: ["四只脚不动，让 Go2 抬头 15°（俯仰 −15°），所有关节都在限位内。", "Feet planted, make Go2 look up 15° (pitch −15°) with every joint within its limits."],
      demo: { scene: "pose", set: { by: 0, bz: 0.287, roll: 0, pitch: -15, yaw: 0, slip: 0 }, press: [], wait: 6 } },
    { id: "low", robot: true, text: ["把机身降到离地 0.20 m，读出小腿关节的角度。", "Lower the body to 0.20 m above the ground and read the calf angles."],
      demo: { scene: "pose", set: { by: 0, bz: 0.20, roll: 0, pitch: 0, yaw: 0, slip: 0 }, press: [], wait: 6 } },
    { id: "bad", robot: true, text: ["找出一个不可行的机身姿态（例如抬头 42°），读出是哪条腿、为什么。", "Find an infeasible body pose (say pitch −42°) and read which leg fails and why."],
      demo: { scene: "pose", set: { by: 0, bz: 0.287, roll: 0, pitch: -42, yaw: 0, slip: 0 }, press: [], wait: 6 } },
    { id: "slip", robot: true, text: ["把右后脚的打滑速度设为 0.05 m/s，按“开始”，由残差找出打滑的脚。", "Set the rear-right slip to 0.05 m/s, press Start, and find the slipping foot from the residuals."],
      demo: { scene: "pose", set: { by: 0, bz: 0.287, roll: 0, pitch: 0, yaw: 0, slip: 0.05 }, press: ["start"], wait: 60 } },
    { id: "squat", text: ["让 G1 两脚不动，骨盆下降 0.10 m（扎马步）。", "Keep G1's feet planted and lower its pelvis by 0.10 m (horse stance)."],
      demo: { scene: "life", set: { gdz: 0.10, gdy: 0 }, press: [], wait: 6 } },
  ],
  think: ["小跑时只有对角两只脚着地。这时腿式里程计能测出机身的哪些速度，测不出哪一个？",
          "When trotting only two diagonal feet are down. Which body velocities can leg odometry still measure, and which one not?"],

  AX: 0.1934, AY: 0.0465, DY: 0.0955, L1: 0.213, L2: 0.213, RF: 0.022, H0: 0.2868,
  LEGS: ["FL", "FR", "RL", "RR"], SG: { FL: [1, 1], FR: [1, -1], RL: [-1, 1], RR: [-1, -1] },
  LIM: [[-1.0472, 1.0472], [-1.5708, 3.4907], [-2.7227, -0.83776]], LIMR: [[-1.0472, 1.0472], [-0.5236, 4.5379], [-2.7227, -0.83776]],
  ZH: { FL: ["左前", "front left"], FR: ["右前", "front right"], RL: ["左后", "rear left"], RR: ["右后", "rear right"] },

  // ---------------- 小矩阵
  mul3(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  mv3(A, v) { return A.map((r) => r[0] * v[0] + r[1] * v[1] + r[2] * v[2]); },
  tr3(A) { return [0, 1, 2].map((i) => [A[0][i], A[1][i], A[2][i]]); },
  rpy(r, p, y) {
    const c = Math.cos, s = Math.sin;
    const Rz = [[c(y), -s(y), 0], [s(y), c(y), 0], [0, 0, 1]], Ry = [[c(p), 0, s(p)], [0, 1, 0], [-s(p), 0, c(p)]], Rx = [[1, 0, 0], [0, c(r), -s(r)], [0, s(r), c(r)]];
    return this.mul3(Rz, this.mul3(Ry, Rx));
  },
  expSO3(w) {
    const t = Math.hypot(w[0], w[1], w[2]);
    if (t < 1e-12) return [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    const k = w.map((x) => x / t), K = [[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]], K2 = this.mul3(K, K);
    return [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + Math.sin(t) * K[i][j] + (1 - Math.cos(t)) * K2[i][j]));
  },
  // ---------------- Go2 一条腿（与实验 20.1 相同）
  hip(leg) { const g = this.SG[leg]; return [g[0] * this.AX, g[1] * this.AY, 0]; },
  ik(leg, p) {
    const g = this.SG[leg], h = this.hip(leg), r = [p[0] - h[0], p[1] - h[1], p[2] - h[2]], d = this.DY, l1 = this.L1, l2 = this.L2;
    const LIM = g[0] > 0 ? this.LIM : this.LIMR, rho2 = r[1] * r[1] + r[2] * r[2];
    if (rho2 < d * d) return { ok: false, why: "rho" };
    const zp = -Math.sqrt(rho2 - d * d), xp = r[0], D = Math.hypot(xp, zp);
    if (D > 2 * l1 * Math.cos(Math.abs(LIM[2][1]) / 2) + 1e-9) return { ok: false, why: "far" };
    if (D < 2 * l1 * Math.cos(Math.abs(LIM[2][0]) / 2) - 1e-9) return { ok: false, why: "near" };
    const t1 = Math.atan2(r[2], r[1]) - Math.atan2(zp, g[1] * d);
    const t3 = -Math.acos(Math.max(-1, Math.min(1, (D * D - l1 * l1 - l2 * l2) / (2 * l1 * l2))));
    let t2 = Math.atan2(-xp, -zp) - Math.atan2(l2 * Math.sin(t3), l1 + l2 * Math.cos(t3));
    if (t2 < LIM[1][0]) t2 += 2 * Math.PI;
    if (t2 > LIM[1][1]) t2 -= 2 * Math.PI;
    let t1w = t1;
    while (t1w > Math.PI) t1w -= 2 * Math.PI;
    while (t1w < -Math.PI) t1w += 2 * Math.PI;
    const th = [t1w, t2, t3], bad = th.findIndex((v, i) => v < LIM[i][0] - 1e-9 || v > LIM[i][1] + 1e-9);
    return bad >= 0 ? { ok: false, why: "limit", bad, th } : { ok: true, th };
  },
  jac(leg, th) {
    const [t1, t2, t3] = th, l1 = this.L1, l2 = this.L2, d = this.SG[leg][1] * this.DY;
    const xp = -l1 * Math.sin(t2) - l2 * Math.sin(t2 + t3), zp = -l1 * Math.cos(t2) - l2 * Math.cos(t2 + t3);
    const c = Math.cos(t1), s = Math.sin(t1), rot = (v) => [v[0], c * v[1] - s * v[2], s * v[1] + c * v[2]];
    const cols = [rot([0, -zp, d]), rot([zp, 0, -xp]), rot([-l2 * Math.cos(t2 + t3), 0, l2 * Math.sin(t2 + t3)])];
    return { J: [0, 1, 2].map((i) => cols.map((cc) => cc[i])), det: -l1 * l2 * zp * Math.sin(t3) };
  },
  feet0() { const f = {}; this.LEGS.forEach((l) => { const h = this.hip(l), g = this.SG[l]; f[l] = [h[0], h[1] + g[1] * this.DY, this.RF]; }); return f; },
  solve(R, p, feet) {   // 定理 20.2.1
    const Rt = this.tr3(R), out = {};
    this.LEGS.forEach((l) => { const f = feet[l], pb = this.mv3(Rt, [f[0] - p[0], f[1] - p[1], f[2] - p[2]]); out[l] = Object.assign(this.ik(l, pb), { pb }); });
    return out;
  },

  // ---------------- 三维放置
  placeGo2(api, R, p) {
    const T = api.three, K = api.keep, go = api.m["B-LEG-GO2"];
    const Ts = new T.Matrix4().set(R[0][0], R[0][1], R[0][2], p[0], R[1][0], R[1][1], R[1][2], p[1], R[2][0], R[2][1], R[2][2], p[2], 0, 0, 0, 1);
    const W = K.C.clone().multiply(Ts).multiply(K.MhbInv);
    W.decompose(go.holder.position, go.holder.quaternion, go.holder.scale);
    go.holder.updateMatrixWorld(true);
  },
  setLegs(go, sol) {
    const o = Object.assign({}, go.entry.rest);
    this.LEGS.forEach((l) => { const s = sol[l]; if (s && s.th && s.ok) { o[l + "_hip_joint"] = s.th[0]; o[l + "_thigh_joint"] = s.th[1]; o[l + "_calf_joint"] = s.th[2]; } });
    go.set(o);
  },

  // ---------------- G1 两腿的数值逆解（6 个关节、6 维位姿，差商雅可比）
  G1L: { left: ["left_hip_pitch_joint", "left_hip_roll_joint", "left_hip_yaw_joint", "left_knee_joint", "left_ankle_pitch_joint", "left_ankle_roll_joint"],
         right: ["right_hip_pitch_joint", "right_hip_roll_joint", "right_hip_yaw_joint", "right_knee_joint", "right_ankle_pitch_joint", "right_ankle_roll_joint"] },
  relPose(api, g, side) {   // 踝横滚连杆相对骨盆的位姿：R（3×3）与 p
    const T = api.three, pel = g.nodes.pelvis, an = g.nodes[side + "_ankle_roll_link"];
    g.root.updateMatrixWorld(true);
    const M = new T.Matrix4().copy(pel.matrixWorld).invert().multiply(an.matrixWorld), e = M.elements;
    return { R: [[e[0], e[4], e[8]], [e[1], e[5], e[9]], [e[2], e[6], e[10]]], p: [e[12], e[13], e[14]] };
  },
  err6(cur, tgt) {
    const Rt = tgt.R, Rc = cur.R, E = this.mul3(Rt, this.tr3(Rc));
    return [(E[2][1] - E[1][2]) / 2, (E[0][2] - E[2][0]) / 2, (E[1][0] - E[0][1]) / 2, tgt.p[0] - cur.p[0], tgt.p[1] - cur.p[1], tgt.p[2] - cur.p[2]];
  },
  g1leg(api, g, side, tgt, q) {
    const names = this.G1L[side], set = () => { const o = {}; names.forEach((n, i) => { o[n] = q[i]; }); g.set(o); };
    for (let it = 0; it < 30; it++) {
      set();
      const e = this.err6(this.relPose(api, g, side), tgt);
      if (Math.hypot(...e) < 1e-8) break;
      const J = [[], [], [], [], [], []], h = 1e-5;
      for (let k = 0; k < 6; k++) {
        q[k] += h; set();
        const ek = this.err6(this.relPose(api, g, side), tgt);
        for (let i = 0; i < 6; i++) J[i][k] = (e[i] - ek[i]) / h;
        q[k] -= h;
      }
      const dq = api.la.mv(api.la.pinv(J, 1e-9), e);
      for (let k = 0; k < 6; k++) q[k] += dq[k];
    }
    set();
    const e = this.err6(this.relPose(api, g, side), tgt), ok = Math.hypot(...e) < 1e-5 && names.every((n, i) => q[i] >= g.joints[n].lower - 1e-6 && q[i] <= g.joints[n].upper + 1e-6);
    return { ok, q };
  },

  setup3d(api, keep) {
    const T = api.three, go = api.m["B-LEG-GO2"], g1 = api.m["B-HUM-G1"];
    go.place(0, 0);
    g1.place(0, 0);
    go.holder.updateMatrixWorld(true);
    const base = go.nodes.base;
    keep.C = new T.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1);
    const Mhb = new T.Matrix4().copy(go.holder.matrixWorld).invert().multiply(base.matrixWorld);
    keep.MhbInv = Mhb.clone().invert();
    keep.feet = this.feet0();
    keep.balls = this.LEGS.map(() => { const b = new T.Mesh(new T.SphereGeometry(0.02, 14, 10), new T.MeshStandardMaterial({ color: 0x2ca02c })); api.st.scene.add(b); return b; });
    api.axes(go, "base", 0.12);
    keep.g1pos = g1.holder.position.clone();
    g1.set({ left_knee_joint: 0, right_knee_joint: 0 });
    keep.g1t = { left: this.relPose(api, g1, "left"), right: this.relPose(api, g1, "right") };
    keep.g1q = { left: [-0.2, 0, 0, 0.4, -0.2, 0], right: [-0.2, 0, 0, 0.4, -0.2, 0] };
    const box = new T.Box3(new T.Vector3(-0.45, 0, -0.35), new T.Vector3(0.45, 0.5, 0.35));
    api.m.fPose = { entry: { robot: {} }, holder: { visible: false }, box: () => box.clone() };
    keep.shown = null;
  },
  reset(api, s) { s.t = 0; s.est = null; s.prev = null; s.done = false; s.run = false; },
  start(api, s) { s.run = true; s.t = 0; },
  V: [0.2, -0.3, 0.1, 0.05, 0.02, -0.04],
  bodyAt(api, t) {   // 起始位姿（滑块）右乘 exp([V_b] t)：常运动旋量下的姿态与位置（小步逐次积分）
    const p = api.p, d = Math.PI / 180;
    let R = this.rpy(p.roll * d, p.pitch * d, p.yaw * d), x = [0, p.by, p.bz];
    const n = Math.max(1, Math.round(t / 0.002)), h = t / n;
    for (let k = 0; k < n; k++) {
      const v = this.mv3(R, this.V.slice(3));
      x = [x[0] + v[0] * h, x[1] + v[1] * h, x[2] + v[2] * h];
      R = this.mul3(R, this.expSO3(this.V.slice(0, 3).map((w) => w * h)));
    }
    return { R, x };
  },
  update(dt, api, s) {
    if (api.scene !== "pose") { api.stop(); return; }
    const h = 0.01;
    s.t = Math.min(1.5, s.t + dt);
    if (s.t >= 1.5) {
      // 在 t = 1.5 s 处用差商求关节速度，做最小二乘
      const t = 1.5, b0 = this.bodyAt(api, t - h), b1 = this.bodyAt(api, t), feetA = Object.assign({}, api.keep.feet), feetB = Object.assign({}, api.keep.feet);
      const sl = api.p.slip;
      feetA.RR = [api.keep.feet.RR[0] + sl * (t - h), api.keep.feet.RR[1], api.keep.feet.RR[2]];
      feetB.RR = [api.keep.feet.RR[0] + sl * t, api.keep.feet.RR[1], api.keep.feet.RR[2]];
      const sa = this.solve(b0.R, b0.x, feetA), sb = this.solve(b1.R, b1.x, feetB);
      if (this.LEGS.every((l) => sa[l].ok && sb[l].ok)) {
        const A = [], y = [];
        this.LEGS.forEach((l) => {
          const th = sb[l].th, thd = th.map((v, i) => (v - sa[l].th[i]) / h), Jm = this.jac(l, th).J, Jt = this.mv3(Jm, thd), p = sb[l].pb;
          const sk = [[0, -p[2], p[1]], [p[2], 0, -p[0]], [-p[1], p[0], 0]];
          for (let i = 0; i < 3; i++) { A.push([sk[i][0], sk[i][1], sk[i][2], i === 0 ? -1 : 0, i === 1 ? -1 : 0, i === 2 ? -1 : 0]); y.push(Jt[i]); }
        });
        const Vh = api.la.mv(api.la.pinv(A), y), r = api.la.mv(A, Vh).map((v, i) => v - y[i]);
        s.est = { V: Vh, res: [0, 1, 2, 3].map((k) => Math.hypot(r[3 * k], r[3 * k + 1], r[3 * k + 2])) };
        const kmax = s.est.res.indexOf(Math.max(...s.est.res));
        if (sl >= 0.03 && kmax === 3) api.done("slip");
      }
      s.run = false;
      api.stop();
    }
  },

  readouts(api, s) {
    const go = api.m["B-LEG-GO2"], f = (x, n) => api.fmt(x, n), deg = 180 / Math.PI, p = api.p, K = api.keep;
    if (!go || !K.C) return [];
    if (api.scene === "pose") {
      const b = s.t > 0 ? this.bodyAt(api, s.t) : this.bodyAt(api, 0);
      const feet = Object.assign({}, K.feet);
      if (s.t > 0) feet.RR = [K.feet.RR[0] + p.slip * s.t, K.feet.RR[1], K.feet.RR[2]];
      const sol = this.solve(b.R, b.x, feet), rows = [];
      let all = true, mindet = 1e9;
      this.LEGS.forEach((l) => {
        const r = sol[l];
        if (r.ok) {
          mindet = Math.min(mindet, Math.abs(this.jac(l, r.th).det));
          rows.push([[`${this.ZH[l][0]} ${l}：θ₁, θ₂, θ₃`, `${this.ZH[l][1]} ${l}: θ₁, θ₂, θ₃`], `${f(r.th[0] * deg, 1)}°, ${f(r.th[1] * deg, 1)}°, ${f(r.th[2] * deg, 1)}°`]);
        } else {
          all = false;
          const why = { rho: api.T("离髋外摆轴太近", "too close to the abduction axis"), far: api.T("离得太远（小腿关节要过 −48°）", "too far (calf joint past −48°)"),
                        near: api.T("折叠过度（小腿关节要过 −156°）", "folded too far (calf joint past −156°)"),
                        limit: api.T("关节 " + ((r.bad || 0) + 1) + " 超出限位", "joint " + ((r.bad || 0) + 1) + " out of range") }[r.why];
          rows.push([[`${this.ZH[l][0]} ${l}`, `${this.ZH[l][1]} ${l}`], api.T("不可行：", "infeasible: ") + why]);
        }
      });
      this.placeGo2(api, b.R, b.x);
      this.setLegs(go, sol);
      this.LEGS.forEach((l, i) => { const q = feet[l]; K.balls[i].position.set(q[0], q[2], -q[1]); K.balls[i].material.color.setHex(sol[l].ok ? 0x2ca02c : 0xd62728); });
      rows.push([["各腿 |det J| 的最小值", "smallest |det J| of the legs"], all ? f(mindet * 1000, 2) + " ×10⁻³ m³" : "—"]);
      if (s.est) {
        const e = s.est.V.map((v, i) => v - this.V[i]);
        rows.push([["里程计误差 |Δω|、|Δv|", "odometry error |Δω|, |Δv|"], `${f(Math.hypot(e[0], e[1], e[2]), 4)} rad/s, ${f(Math.hypot(e[3], e[4], e[5]) * 1000, 1)} mm/s`]);
        rows.push([["残差 FL, FR, RL, RR", "residuals FL, FR, RL, RR"], s.est.res.map((r) => f(r * 1000, 1)).join(", ") + " mm/s"]);
      } else if (s.t > 0) rows.push([["机身晃动", "body swaying"], f(s.t, 2) + " s"]);
      if (s.t === 0) {
        if (all && p.pitch <= -15) api.done("up");
        if (all && p.bz <= 0.2005) api.done("low");
        if (!all) api.done("bad");
      }
      return rows;
    }
    const g = api.m["B-HUM-G1"], tgt = {};
    ["left", "right"].forEach((side) => { const t0 = K.g1t[side]; tgt[side] = { R: t0.R, p: [t0.p[0], t0.p[1] - p.gdy, t0.p[2] + p.gdz] }; });
    const rl = this.g1leg(api, g, "left", tgt.left, K.g1q.left.slice()), rr = this.g1leg(api, g, "right", tgt.right, K.g1q.right.slice());
    if (rl.ok && rr.ok) { K.g1q.left = rl.q; K.g1q.right = rr.q; }
    const o = {};
    ["left", "right"].forEach((side) => this.G1L[side].forEach((n, i) => { o[n] = K.g1q[side][i]; }));
    g.set(o);
    g.holder.position.set(K.g1pos.x, K.g1pos.y - p.gdz, K.g1pos.z - p.gdy);
    g.holder.updateMatrixWorld(true);
    const ok = rl.ok && rr.ok, q = K.g1q.left;
    if (ok && p.gdz >= 0.099) api.done("squat");
    return [[["骨盆下降、侧移", "pelvis drop, shift"], `${f(p.gdz, 2)} m, ${f(p.gdy, 3)} m`],
            [["左腿：髋俯仰、膝、踝俯仰", "left leg: hip pitch, knee, ankle pitch"], `${f(q[0] * deg, 1)}°, ${f(q[3] * deg, 1)}°, ${f(q[4] * deg, 1)}°`],
            [["左腿：髋横滚、踝横滚", "left leg: hip roll, ankle roll"], `${f(q[1] * deg, 1)}°, ${f(q[5] * deg, 1)}°`],
            [["结果", "result"], ok ? api.T("两脚贴地不动，可行", "feet flat and fixed: feasible") : api.T("超出关节限位或够不着（保持上一个可行姿态）", "past a joint limit or out of reach (last feasible pose kept)")]];
  },

  draw(api, s) {
    const m = api.m, sc = api.scene, K = api.keep;
    if (!K.C) return;
    m["B-LEG-GO2"].holder.visible = sc === "pose";
    K.balls.forEach((b) => { b.visible = sc === "pose"; });
    m["B-HUM-G1"].holder.visible = sc === "life";
    if (K.shown !== sc) {
      K.shown = sc;
      api.view(sc === "pose" ? 40 : 60, sc === "pose" ? 20 : 12, 0.85, sc === "pose" ? m.fPose : m["B-HUM-G1"]);
    }
    if (api.running) api.readout();
  },
});
