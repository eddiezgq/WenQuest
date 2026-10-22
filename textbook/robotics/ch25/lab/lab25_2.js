// 实验 25.2 关节里的力（配 25.2 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex25_2.py 同一版本。
// 书中的 UR5e 模型（外观为零件库 glTF），法兰上可装夹爪 + SH-301 毛坯（算例 23.2.2 的组合体，按质量等比缩放，3.8 kg 时与之相同）。
// 牛顿-欧拉递推（算法 25.2.1）用的连杆数据由页面从 MuJoCo 模型读出（chain()；负载 body 没有关节，并入连杆 6），与程序 _ch25.py 相同。
// 递推给出关节力矩 τ 和各关节传给连杆 i 的力旋量 ℱ_i；ℱ_i 分成绕轴力矩、弯曲力矩、轴向力、径向力（25.2.5 节）。
// 与 MuJoCo 比较：τ 对 mj_inverse 的 qfrc_inverse；ℱ_i 对 mj_rnePostConstraint 的 cfrc_int（换到连杆坐标系 {i}）。
// 场景 1（机器人，静止）：θ = (0, θ₂, θ₃, θ₄, 0, 0)。场景 2（机器人）：第 22 章的上下料动作（T = 1.318 s，放慢 2 倍）。
// 阈值由 ex25_2.py、ex25_5.py 与 Python 版 MuJoCo 核算：手臂（连杆 1～6）16.9949 kg；水平伸直 θ = (0, 0, 0, −90°, 0, 0)、
//   法兰处 5 kg 时关节 2 力矩 98.77 N·m（这里的负载是夹爪 + 毛坯放大到 5 kg，质心在法兰外 0.161 m；这一姿态下工具方向与关节 2 的轴平行，τ₂ 相同）；
//   装 3.8 kg 走上下料动作，关节 2 的弯曲力矩峰值 14.2 N·m，只有重力时 3.2 N·m。
WQ.lab({
  title: ["实验 25.2 关节里的力", "Lab 25.2 The forces inside the joints"],
  goal: ["用反向递推求 UR5e 六个关节的力矩，以及每个关节的轴承和减速器承受的力和弯曲力矩，并与 MuJoCo 逐项比较。",
         "Use the backward recursion to get the UR5e's six joint torques and the forces and tilting moments carried by each joint's bearings and gearbox, and compare them with MuJoCo term by term."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "hold", robot: true, name: ["静止地拿着", "Holding still"], hide: [],
      problem: { title: ["机器人问题：关节轴承要承受多大的力", "Robot problem: how much load do the joint bearings carry"],
                 text: ["电机只管绕轴的力矩；另外五个方向的力和力矩由轴承、减速器扛着。手臂伸出去、再拿上工件，它们是多少？",
                        "The motor only supplies the moment about the axis; the other five components are carried by the bearings and gearbox. How large are they with the arm stretched out holding a part?"] } },
    { id: "move", robot: true, name: ["上下料动作中的关节受力", "Joint loads during the loading move"], hide: ["q2", "q3", "q4"],
      problem: { title: ["机器人问题：动起来以后，关节受力多了多少", "Robot problem: how much do the joint loads grow when the arm moves"],
                 text: ["同样的姿态，慢慢走和按节拍快走，关节 2 的轴承受力差多少？",
                        "Through the same poses, how different are joint 2's bearing loads when the arm creeps and when it moves at cycle speed?"] } },
  ],
  params: [
    { id: "q2", name: ["关节 2 角 θ₂", "Joint 2 angle θ₂"], min: -180, max: 0, step: 1, value: -60, unit: "°", digits: 0 },
    { id: "q3", name: ["关节 3 角 θ₃", "Joint 3 angle θ₃"], min: -160, max: 160, step: 1, value: 60, unit: "°", digits: 0 },
    { id: "q4", name: ["关节 4 角 θ₄", "Joint 4 angle θ₄"], min: -180, max: 0, step: 1, value: -90, unit: "°", digits: 0 },
    { id: "load", name: ["法兰上的负载（夹爪 + 毛坯）", "Payload on the flange (gripper + blank)"], min: 0, max: 8, step: 0.1, value: 3.8, unit: "kg", digits: 1 },
    { id: "jsel", name: ["看哪个关节", "Joint to inspect"], min: 1, max: 6, step: 1, value: 2, unit: "", digits: 0 },
  ],
  legend: [{ color: "#d62728", name: ["绕轴力矩（关节力矩）", "moment about the axis (joint torque)"] }, { color: "#b8860b", name: ["弯曲力矩", "tilting moment"] },
           { color: "#1f77b4", name: ["轴向力 / 10", "axial force / 10"] }, { color: "#2ca02c", name: ["径向力 / 10（动作中：浅色线只有重力）", "radial force / 10 (move: light lines = gravity only)"] }],
  physics: {
    camera: [30, 18, 0.75],
    payload(load) {
      const k = load / 3.8, I = [0.0260338 * k, 0.0017083 * k, 0.0262671 * k];
      return `<body name="payload" pos="0 0.1 0"><inertial pos="0 0.16114 0" mass="${Math.max(load, 1e-6)}" diaginertia="${Math.max(I[0], 1e-9)} ${Math.max(I[1], 1e-9)} ${Math.max(I[2], 1e-9)}"/>
<geom type="box" pos="0 0.05 0" size="0.04 0.05 0.03" rgba="0.36 0.42 0.45 1" mass="0" contype="0" conaffinity="0"/>
<geom type="cylinder" pos="0 0.2008 0" quat="0.7071068 0.7071068 0 0" size="0.025 0.0908" rgba="0.62 0.55 0.35 1" mass="0" contype="0" conaffinity="0"/></body>`;
    },
    xml(api) { return api.mjcf("ur5e", { option: `<option timestep="0.002"><flag contact="disable"/></option>`, tool: api.p.load > 0 ? this.payload(api.p.load) : "" }); },
  },
  QA: [98.1725, -86.0425, 114.5326, -118.4901, -90.0, 8.1725].map((x) => x * Math.PI / 180),
  QB: [201.5997, -50.543, 79.7267, -29.1837, -68.4003, 0.0].map((x) => x * Math.PI / 180),
  TM: 1.318,
  M_ARM: 16.9949,
  // ---- 牛顿-欧拉递推（算法 25.2.1），与书中程序 _ch25.py 的 Chain 相同；数据从 MuJoCo 模型读出 ----
  R3: {
    q(a, k) { const w = a[k], x = a[k + 1], y = a[k + 2], z = a[k + 3], n = Math.hypot(w, x, y, z), W = w / n, X = x / n, Y = y / n, Z = z / n;
      return [[1 - 2 * (Y * Y + Z * Z), 2 * (X * Y - W * Z), 2 * (X * Z + W * Y)], [2 * (X * Y + W * Z), 1 - 2 * (X * X + Z * Z), 2 * (Y * Z - W * X)],
              [2 * (X * Z - W * Y), 2 * (Y * Z + W * X), 1 - 2 * (X * X + Y * Y)]]; },
    mm(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
    mv(A, v) { return A.map((r) => r[0] * v[0] + r[1] * v[1] + r[2] * v[2]); },
    tr(A) { return [0, 1, 2].map((i) => [A[0][i], A[1][i], A[2][i]]); },
    cr(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
    add(a, b) { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; },
    sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; },
    sc(a, s) { return [a[0] * s, a[1] * s, a[2] * s]; },
    dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; },
    rot(w, t) { const c = Math.cos(t), s = Math.sin(t), k = 1 - c;
      return [[c + k * w[0] * w[0], k * w[0] * w[1] - s * w[2], k * w[0] * w[2] + s * w[1]], [k * w[1] * w[0] + s * w[2], c + k * w[1] * w[1], k * w[1] * w[2] - s * w[0]],
              [k * w[2] * w[0] - s * w[1], k * w[2] * w[1] + s * w[0], c + k * w[2] * w[2]]]; },
    T(R, p) { return { R, p }; },
    mul(A, B) { return { R: this.mm(A.R, B.R), p: this.add(this.mv(A.R, B.p), A.p) }; },
    inv(A) { const Rt = this.tr(A.R); return { R: Rt, p: this.sc(this.mv(Rt, A.p), -1) }; },
  },
  chain(api) {                     // 连杆坐标系 = MJCF 的 body 坐标系；没有关节的 body（基座、负载）并入有关节的祖先
    const { m } = api.sim, R3 = this.R3, nb = m.nbody, jb = {};
    for (let j = 0; j < m.njnt; j++) jb[m.jnt_bodyid[j]] = j;
    const rel = [], own = [-1], Tow = [R3.T([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, 0, 0])];
    const links = [], idx = {};
    for (let b = 1; b < nb; b++) {
      rel[b] = R3.T(R3.q(m.body_quat, 4 * b), [m.body_pos[3 * b], m.body_pos[3 * b + 1], m.body_pos[3 * b + 2]]);
      const par = m.body_parentid[b], Tp = R3.mul(Tow[par], rel[b]);    // b 在父 body 的“主人”坐标系中的位姿
      if (jb[b] !== undefined) {
        const j = jb[b];
        own[b] = b; Tow[b] = R3.T([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, 0, 0]);
        idx[b] = links.length;
        links.push({ b, axis: [m.jnt_axis[3 * j], m.jnt_axis[3 * j + 1], m.jnt_axis[3 * j + 2]], M: R3.inv(Tp), G: this.zero6(), arm: m.dof_armature[m.jnt_dofadr[j]] });
      } else { own[b] = own[par]; Tow[b] = Tp; }
      if (own[b] < 0 || m.body_mass[b] === 0) continue;
      const Ri = R3.q(m.body_iquat, 4 * b), Ic = R3.mm(R3.mm(Ri, [[m.body_inertia[3 * b], 0, 0], [0, m.body_inertia[3 * b + 1], 0], [0, 0, m.body_inertia[3 * b + 2]]]), R3.tr(Ri));
      const c = [m.body_ipos[3 * b], m.body_ipos[3 * b + 1], m.body_ipos[3 * b + 2]];
      const Gb = this.Gframe(m.body_mass[b], c, Ic), L = links[idx[own[b]]];
      const A = this.Ad(R3.inv(Tow[b]));                                // 主人坐标系在 b 中的位姿
      L.G = this.add6x6(L.G, this.mtm(A, Gb, A));                       // 𝒢 = [Ad]ᵀ 𝒢_b [Ad]（式 (23.3.13)）
    }
    return links;
  },
  zero6() { return Array.from({ length: 6 }, () => new Array(6).fill(0)); },
  add6x6(A, B) { return A.map((r, i) => r.map((x, j) => x + B[i][j])); },
  mtm(A, G, B) { const n = 6, AG = this.zero6(), O = this.zero6();
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { let s = 0; for (let k = 0; k < n; k++) s += A[k][i] * G[k][j]; AG[i][j] = s; }
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { let s = 0; for (let k = 0; k < n; k++) s += AG[i][k] * B[k][j]; O[i][j] = s; }
    return O; },
  Gframe(mass, c, Ic) {          // 式 (23.3.15)：质心在 c，Ic 已转到本坐标系方向
    const P = [[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]], G = this.zero6();
    for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
      let pp = 0; for (let k = 0; k < 3; k++) pp += P[i][k] * P[k][j];
      G[i][j] = Ic[i][j] - mass * pp; G[i][j + 3] = mass * P[i][j]; G[i + 3][j] = -mass * P[i][j];
    }
    for (let i = 0; i < 3; i++) G[i + 3][i + 3] = mass;
    return G; },
  Ad(T) {                        // [Ad_T]（式 (6.5.4)）
    const R = T.R, p = T.p, A = this.zero6(), P = [[0, -p[2], p[1]], [p[2], 0, -p[0]], [-p[1], p[0], 0]];
    for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
      A[i][j] = R[i][j]; A[i + 3][j + 3] = R[i][j];
      A[i + 3][j] = P[i][0] * R[0][j] + P[i][1] * R[1][j] + P[i][2] * R[2][j];
    }
    return A; },
  mv6(A, v) { return A.map((r) => r.reduce((s, x, k) => s + x * v[k], 0)); },
  mtv6(A, v) { return [0, 1, 2, 3, 4, 5].map((j) => A.reduce((s, r, k) => s + r[j] * v[k], 0)); },
  adv(V, X) {                    // [ad_V] X = (ω × ξ, v × ξ + ω × u)，X = (ξ, u)
    const R3 = this.R3, w = V.slice(0, 3), v = V.slice(3), a = X.slice(0, 3), b = X.slice(3);
    return [...R3.cr(w, a), ...R3.add(R3.cr(v, a), R3.cr(w, b))]; },
  adTv(V, F) {                   // [ad_V]ᵀ F，F = (m, f)：(−ω × m − v × f, −ω × f)
    const R3 = this.R3, w = V.slice(0, 3), v = V.slice(3), mo = F.slice(0, 3), f = F.slice(3);
    return [...R3.sc(R3.add(R3.cr(w, mo), R3.cr(v, f)), -1), ...R3.sc(R3.cr(w, f), -1)]; },
  rnea(links, q, qd, qdd, g = 9.81) {
    const R3 = this.R3, n = links.length, Ts = [], Vs = [], Vds = [];
    let V = [0, 0, 0, 0, 0, 0], Vd = [0, 0, 0, 0, 0, g];               // 𝒱̇₀ = (0, −𝔤)：基座以 𝔤 向上加速
    for (let i = 0; i < n; i++) {
      const L = links[i], T = R3.mul(R3.T(R3.rot(L.axis, -q[i]), [0, 0, 0]), L.M), Ad = this.Ad(T), A = [...L.axis, 0, 0, 0];
      V = this.mv6(Ad, V).map((x, k) => x + A[k] * qd[i]);
      const aV = this.adv(V, A);
      Vd = this.mv6(Ad, Vd).map((x, k) => x + aV[k] * qd[i] + A[k] * qdd[i]);
      Ts.push(Ad); Vs.push(V); Vds.push(Vd);
    }
    let F = [0, 0, 0, 0, 0, 0];
    const tau = new Array(n), Fs = new Array(n);
    for (let i = n - 1; i >= 0; i--) {
      const L = links[i];
      if (i < n - 1) F = this.mtv6(Ts[i + 1], F);
      const GV = this.mv6(L.G, Vs[i]), GVd = this.mv6(L.G, Vds[i]), aT = this.adTv(Vs[i], GV);
      F = F.map((x, k) => x + GVd[k] - aT[k]);
      Fs[i] = F;
      tau[i] = R3.dot(L.axis, F.slice(0, 3)) + L.arm * qdd[i];
    }
    return { tau, F: Fs, V: Vs, Vd: Vds };
  },
  traj(t) {
    const T = this.TM, u = Math.min(Math.max(t / T, 0), 1);
    const s = 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5, sd = (30 * u ** 2 - 60 * u ** 3 + 30 * u ** 4) / T, sdd = (60 * u - 180 * u ** 2 + 120 * u ** 3) / T ** 2;
    const dl = this.QB.map((b, i) => b - this.QA[i]);
    return { q: this.QA.map((a, i) => a + s * dl[i]), qd: dl.map((v) => sd * v), qdd: dl.map((v) => sdd * v) };
  },
  split(F, w) {                                   // 绕轴力矩、弯曲力矩、轴向力、径向力
    const R3 = this.R3, mo = F.slice(0, 3), f = F.slice(3), ma = R3.dot(mo, w), fa = R3.dot(f, w);
    return [ma, Math.hypot(...R3.sub(mo, R3.sc(w, ma))), fa, Math.hypot(...R3.sub(f, R3.sc(w, fa)))];
  },
  mjCheck(api, q, qd, qdd, r) {                   // 与 MuJoCo 比较：τ 与 ℱ_i
    const { mj, m, d } = api.sim, R3 = this.R3;
    for (let i = 0; i < 6; i++) { d.qpos[i] = q[i]; d.qvel[i] = qd[i]; d.qacc[i] = qdd[i]; }
    mj.mj_inverse(m, d);
    let et = 0, ef = 0;
    for (let i = 0; i < 6; i++) et = Math.max(et, Math.abs(r.tau[i] - d.qfrc_inverse[i]));
    for (let i = 0; i < 6; i++) { d.qpos[i] = q[i]; d.qvel[i] = qd[i]; d.qacc[i] = qdd[i]; }
    mj.mj_fwdPosition(m, d); mj.mj_fwdVelocity(m, d); mj.mj_rnePostConstraint(m, d);
    this.links.forEach((L, i) => {
      const b = L.b, rt = m.body_rootid[b], c = [d.subtree_com[3 * rt], d.subtree_com[3 * rt + 1], d.subtree_com[3 * rt + 2]];
      const p = [d.xpos[3 * b], d.xpos[3 * b + 1], d.xpos[3 * b + 2]];
      const Rt = [[d.xmat[9 * b], d.xmat[9 * b + 3], d.xmat[9 * b + 6]], [d.xmat[9 * b + 1], d.xmat[9 * b + 4], d.xmat[9 * b + 7]], [d.xmat[9 * b + 2], d.xmat[9 * b + 5], d.xmat[9 * b + 8]]];
      const mc = Array.from(d.cfrc_int.slice(6 * b, 6 * b + 3)), f = Array.from(d.cfrc_int.slice(6 * b + 3, 6 * b + 6));
      const Fi = [...R3.mv(Rt, R3.sub(mc, R3.cr(R3.sub(p, c), f))), ...R3.mv(Rt, f)];
      for (let k = 0; k < 6; k++) ef = Math.max(ef, Math.abs(Fi[k] - r.F[i][k]));
    });
    return [et, ef];
  },
  pose(api) {
    const r = Math.PI / 180;
    return [0, api.p.q2 * r, api.p.q3 * r, api.p.q4 * r, 0, 0];
  },
  evalAt(api, s, q, qd, qdd) {
    const r = this.rnea(this.links, q, qd, qdd), j = api.p.jsel - 1;
    const z = [0, 0, 0, 0, 0, 0], rg = this.rnea(this.links, q, z, z);
    s.r = r; s.parts = this.split(r.F[j], this.links[j].axis); s.partsG = this.split(rg.F[j], this.links[j].axis);
    s.all = r.F.map((F, i) => this.split(F, this.links[i].axis));
    const e = this.mjCheck(api, q, qd, qdd, r);
    s.et = Math.max(s.et || 0, e[0]); s.ef = Math.max(s.ef || 0, e[1]);
  },
  reset(api, s) {
    const { mj, m, d } = api.sim;
    this.links = this.chain(api);
    s.clock = 0; s.fin = false; s.et = 0; s.ef = 0; s.hist = []; s.pk = [0, 0]; s.pkG = [0, 0];
    const q = api.scene === "hold" ? this.pose(api) : this.QA.slice(), z = [0, 0, 0, 0, 0, 0];
    this.evalAt(api, s, q, z, z);
    for (let i = 0; i < 6; i++) { d.qpos[i] = q[i]; d.qvel[i] = 0; d.ctrl[i] = q[i]; }
    mj.mj_forward(m, d);
    if (api.scene === "hold") {
      const W = (this.M_ARM + api.p.load) * 9.81, ax1 = this.split(s.r.F[0], this.links[0].axis)[2];
      s.W = W; s.ax1 = ax1;
      const moved = api.p.q2 !== -60 || api.p.q3 !== 60 || api.p.q4 !== -90;      // 先改动姿态再判定
      if (Math.abs(api.p.load - 3.8) < 0.05 && moved && s.et < 1e-9 && s.ef < 1e-9) api.done("inv");
      if (api.p.jsel === 1 && Math.abs(api.p.load - 3.8) > 0.05 && Math.abs(Math.abs(ax1) - W) < 1e-6) api.done("weight");
      if (api.p.q2 === 0 && api.p.q3 === 0 && api.p.q4 === -90 && Math.abs(api.p.load - 5) < 0.05) api.done("horiz");
    }
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim;
    if (api.scene === "hold") { api.stop(); return; }
    s.clock += dt * (api.rate || 1) / 2;
    const t = Math.min(s.clock, this.TM), tr = this.traj(t);
    this.evalAt(api, s, tr.q, tr.qd, tr.qdd);
    const P = s.parts, G = s.partsG;
    s.hist.push([t, Math.abs(P[0]), P[1], Math.abs(P[2]) / 10, P[3] / 10, Math.abs(G[0]), G[1], Math.abs(G[2]) / 10, G[3] / 10]);
    s.pk = [Math.max(s.pk[0], P[1]), Math.max(s.pk[1], P[3])]; s.pkG = [Math.max(s.pkG[0], G[1]), Math.max(s.pkG[1], G[3])];
    for (let i = 0; i < 6; i++) { d.qpos[i] = tr.q[i]; d.qvel[i] = 0; d.ctrl[i] = tr.q[i]; }
    mj.mj_forward(m, d);
    if (s.clock >= this.TM && !s.fin) {
      s.fin = true;
      if (api.p.jsel === 2 && Math.abs(api.p.load - 3.8) < 0.05 && s.pk[0] > 3 * s.pkG[0] && s.et < 1e-9 && s.ef < 1e-9) api.done("dyn");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const cols = ["#d62728", "#b8860b", "#1f77b4", "#2ca02c"];
    if (api.scene === "move") {
      const H = s.hist || [];
      if (!H.length) return;
      const ser = cols.map((c, k) => ({ pts: H.map((r) => [r[0], r[k + 1]]), color: c }))
        .concat(["#f4a6a6", "#e3cf8f", "#9ecae1", "#a1d99b"].map((c, k) => ({ pts: H.map((r) => [r[0], r[k + 5]]), color: c })));
      const ymax = Math.max(10, ...H.map((r) => Math.max(...r.slice(1)))) * 1.1;
      api.cplot(56, 10, w - 70, h - 34, ser, { xmin: 0, xmax: this.TM, ymin: 0, ymax, xlabel: "t / s", ylabel: "N·m, N/10" });
      return;
    }
    if (!s.all) return;                             // 六个关节的四个部分（柱状）
    const vals = s.all.map((p) => [Math.abs(p[0]), p[1], Math.abs(p[2]) / 10, p[3] / 10]);
    const vmax = Math.max(10, ...vals.flat()) * 1.1, x0 = 50, bw = (w - x0 - 20) / 6, H0 = h - 24;
    ctx.font = "11px sans-serif"; ctx.fillStyle = "#1d2327";
    vals.forEach((v, i) => {
      v.forEach((x, k) => {
        const hh = (H0 - 10) * x / vmax;
        ctx.fillStyle = cols[k]; ctx.fillRect(x0 + bw * i + 6 + k * (bw - 12) / 4, H0 - hh, (bw - 12) / 4 - 2, hh);
      });
      ctx.fillStyle = "#1d2327"; ctx.fillText(String(i + 1), x0 + bw * i + bw / 2 - 3, h - 8);
    });
    ctx.fillText("N·m, N/10", 4, 14);
  },
  readouts(api, s) {
    if (!s.r) return [];
    const f = (v, k = 2) => api.fmt(v, k), P = s.parts, j = api.p.jsel;
    const rows = [
      [["六个关节的力矩 τ", "Joint torques τ"], s.r.tau.map((x) => f(x, 2)).join(", ") + " N·m"],
      [[`关节 ${j}：绕轴力矩 / 弯曲力矩`, `Joint ${j}: moment about the axis / tilting moment`], `${f(P[0])} / ${f(P[1])} N·m`],
      [[`关节 ${j}：轴向力 / 径向力`, `Joint ${j}: axial / radial force`], `${f(P[2])} / ${f(P[3])} N`],
      [["与 MuJoCo 的最大差别：τ / ℱ", "Largest difference from MuJoCo: τ / ℱ"], `${(s.et || 0).toExponential(1)} N·m / ${(s.ef || 0).toExponential(1)}`],
    ];
    if (api.scene === "hold") rows.push([["手臂（连杆 1～6）加负载的重力", "Weight of links 1–6 plus payload"], f(s.W) + " N"]);
    if (api.scene === "move") rows.push([[`关节 ${j} 的峰值：弯曲力矩 / 径向力（只有重力时）`, `Joint ${j} peaks: tilting moment / radial force (gravity only)`],
      `${f(s.pk[0])} (${f(s.pkG[0])}) N·m / ${f(s.pk[1])} (${f(s.pkG[1])}) N`]);
    return rows;
  },
  tasks: [
    { id: "inv", robot: true, text: ["装 3.8 kg 的夹爪和毛坯，换一个姿态：递推的关节力矩和关节力旋量与 MuJoCo 一致。",
                                     "With the 3.8 kg gripper and blank, change the pose: the recursion's joint torques and joint wrenches agree with MuJoCo."],
      demo: { scene: "hold", set: { q2: -45, q3: 90, q4: -90, load: 3.8, jsel: 2 }, wait: 2 } },
    { id: "weight", robot: true, text: ["看关节 1，把负载换成 3.8 kg 以外的值：它的轴向力为什么正好等于手臂加负载的重力？", "Inspect joint 1 and set a payload other than 3.8 kg: why is its axial force exactly the weight of the arm plus the payload?"],
      demo: { scene: "hold", set: { q2: -60, q3: 60, q4: -90, load: 6, jsel: 1 }, wait: 2 } },
    { id: "horiz", robot: true, text: ["手臂水平伸直（θ₂ = θ₃ = 0，θ₄ = −90°），装 5 kg：读出关节 2 的力矩，其中手臂自重的部分有多少？",
                                       "Stretch the arm horizontally (θ₂ = θ₃ = 0, θ₄ = −90°) with 5 kg: read joint 2's torque; how much of it is the arm's own weight?"],
      demo: { scene: "hold", set: { q2: 0, q3: 0, q4: -90, load: 5, jsel: 2 }, wait: 2 } },
    { id: "dyn", robot: true, text: ["装 3.8 kg 运行上下料动作，看关节 2：弯曲力矩的峰值是只有重力时的 3 倍以上。",
                                     "Run the loading move with 3.8 kg and inspect joint 2: the peak tilting moment is more than 3 times the gravity-only value."],
      demo: { scene: "move", set: { load: 3.8, jsel: 2 }, wait: 5 } },
  ],
  think: ["关节 1 的轴向力等于整条手臂的重力，与姿态无关；它的弯曲力矩却随姿态变化很大。选关节 1 的轴承时，哪个量更要紧？",
          "Joint 1's axial force equals the whole arm's weight whatever the pose, but its tilting moment varies greatly with pose. Which matters more when choosing joint 1's bearing?"],
});
