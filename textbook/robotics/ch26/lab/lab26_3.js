// 实验 26.3 辨识负载（配 26.3 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex26_3.py 同一版本。
// “真实”的 UR5e：书中模型 + 法兰上的负载（夹爪 + 毛坯的组合体按质量等比缩放，质心可再偏移 (c_x, c_y, c_z)）+ 关节摩擦
//   （frictionloss 为干摩擦、damping 为黏性摩擦，与程序 _ch26.py 的 FC_TRUE、FV_TRUE 相同，示意值）；执行器关掉，力矩直接加在关节上。
// 实验：另开一份 MjData，从激励轨迹（26.2 节优化的傅里叶级数，系数与程序相同）的起点出发，每 1 ms 算一次
//   τ = RNEA_手臂(θ_d, θ̇_d, θ̈_d) + K_p(θ_d − θ) + K_d(θ̇_d − θ̇)（控制器只知道不带负载的手臂），每 2 ms 记录 θ、θ̇、θ̈（直接读 MuJoCo；
//   真实机器人要由编码器数值微分，见 26.3.3 节）和电机力矩（加上测量噪声，与程序相同的标准差）。画面按记录回放。
// 辨识：手臂（含转子惯量）已知，未知数是负载的十个惯性参数（写在连杆 6 坐标系中）和六个关节的库仑、黏性摩擦，共 22 个；
//   τ − τ_手臂 = [Y_6, diag(sign θ̇), diag(θ̇)] x，用正规方程（楚列斯基分解）边测边解。
// 阈值由 ex26_3.py 核算：用滤波求导的完整流程，3.8 kg 的质量误差 0.1%、质心误差 0.2 mm；这里不经过滤波，误差更小。
WQ.lab({
  title: ["实验 26.3 辨识负载", "Lab 26.3 Identifying the payload"],
  goal: ["让 UR5e 按激励轨迹动一遍，由关节角和电机力矩求出法兰上负载的质量、质心和关节摩擦，与真值比较。",
         "Run the UR5e along an exciting trajectory and work out the payload's mass and centre of gravity, and the joint friction, from the joint angles and motor torques; compare with the true values."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "id", robot: true, name: ["负载辨识", "Payload identification"], hide: [],
      problem: { title: ["机器人问题：示教器里的负载该填多少", "Robot problem: what payload should be entered on the teach pendant"],
                 text: ["换了夹爪和工件，示教器要填负载的质量和质心。填错了，碰撞检测会误报（第 26.1 节）。能不能让机器人自己称出来？",
                        "After a new gripper and part, the payload mass and centre of gravity must be entered on the pendant. Wrong values cause false collision alarms (Section 26.1). Can the robot weigh it by itself?"] } },
  ],
  params: [
    { id: "load", name: ["负载质量（真值）", "Payload mass (true)"], min: 0.5, max: 5, step: 0.1, value: 3.8, unit: "kg", digits: 1 },
    { id: "cx", name: ["质心再偏移 c_x（真值）", "Extra CoG offset c_x (true)"], min: -0.08, max: 0.08, step: 0.01, value: 0, unit: "m", digits: 2 },
    { id: "cy", name: ["质心再偏移 c_y（沿工具方向，真值）", "Extra CoG offset c_y (along the tool, true)"], min: -0.1, max: 0.1, step: 0.01, value: 0, unit: "m", digits: 2 },
    { id: "cz", name: ["质心再偏移 c_z（真值）", "Extra CoG offset c_z (true)"], min: -0.08, max: 0.08, step: 0.01, value: 0, unit: "m", digits: 2 },
    { id: "Trun", name: ["实验时长", "Duration of the run"], min: 1, max: 10, step: 0.5, value: 10, unit: "s", digits: 1 },
  ],
  legend: [{ color: "#d62728", name: ["质量估计的相对误差（%）", "relative error of the mass estimate (%)"] }, { color: "#1f77b4", name: ["质心估计的误差（mm）", "error of the CoG estimate (mm)"] }],
  physics: {
    camera: [30, 18, 0.75],
    FC: [2.0, 2.0, 1.5, 0.6, 0.6, 0.5], FV: [1.5, 1.5, 1.0, 0.3, 0.3, 0.3],
    payload(p) {
      const k = p.load / 3.8, I = [0.0260338 * k, 0.0017083 * k, 0.0262671 * k];
      return `<body name="payload" pos="0 0.1 0"><inertial pos="${p.cx} ${0.16114 + p.cy} ${p.cz}" mass="${p.load}" diaginertia="${I[0]} ${I[1]} ${I[2]}"/>
<geom type="box" pos="0 0.05 0" size="0.04 0.05 0.03" rgba="0.36 0.42 0.45 1" mass="0" contype="0" conaffinity="0"/>
<geom type="cylinder" pos="0 0.2008 0" quat="0.7071068 0.7071068 0 0" size="0.025 0.0908" rgba="0.62 0.55 0.35 1" mass="0" contype="0" conaffinity="0"/></body>`;
    },
    xml(api) {
      let t = api.mjcf("ur5e", { option: `<option timestep="0.001"><flag contact="disable" actuation="disable"/></option>`, tool: this.payload(api.p) });
      const names = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"];
      names.forEach((nm, i) => { t = t.replace(`<joint name="${nm}"`, `<joint name="${nm}" frictionloss="${this.FC[i]}" damping="${this.FV[i]}"`); });
      return t.replace('<option integrator="implicitfast" />', "");
    },
  },
  Q0: [0, -90, 90, -90, -90, 0].map((x) => x * Math.PI / 180),
  EA: [[-0.797811,  0.134195, -0.033239, -0.21617 , -0.281421], [-0.098781, -0.138661, -0.297528,  0.202307, -0.644069], [ 0.06109 ,  0.162527,  0.243568, -0.441413,  0.00809 ], [-0.582489,  0.198841,  0.423006,  0.135481, -0.099577], [ 0.171012,  0.260319,  0.144237, -0.004926, -0.238638], [-0.757907, -0.086944, -0.351509,  0.357326,  0.44112 ]],
  EB: [[-0.304145, -0.19026 , -0.375126, -0.255614,  0.387034], [-0.057374,  0.252901, -0.052444,  0.282505,  0.201235], [ 0.269002,  0.156995, -0.013454, -0.225422,  0.29934 ], [ 0.320599,  0.201782, -0.245445,  0.15699 , -0.134112], [ 0.249801,  0.600106,  0.082994,  0.257953, -0.270796], [ 0.062983,  0.077135, -0.195247,  0.18391 , -0.038834]],
  KP: [2000, 2000, 2000, 400, 400, 400], KD: [400, 400, 400, 80, 80, 80],
  SIG: [0.4, 0.4, 0.3, 0.08, 0.08, 0.08],
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
  chain(api) { return this.chainM(api.sim.m); },
  chainM(m) {                      // 连杆坐标系 = MJCF 的 body 坐标系；没有关节的 body（基座、负载）并入有关节的祖先
    const R3 = this.R3, nb = m.nbody, jb = {};
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
  // ---- 回归矩阵（式 (26.1.5)），列的次序与书中程序 _ch26.py 相同：每个连杆十个参数，再是转子惯量、库仑摩擦、黏性摩擦 ----
  Gpi(p) {
    const G = this.zero6(), P = [[0, -p[3], p[2]], [p[3], 0, -p[1]], [-p[2], p[1], 0]], I = [[p[4], p[5], p[6]], [p[5], p[7], p[8]], [p[6], p[8], p[9]]];
    for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) { G[i][j] = I[i][j]; G[i][j + 3] = P[i][j]; G[i + 3][j] = -P[i][j]; }
    for (let i = 0; i < 3; i++) G[i + 3][i + 3] = p[0];
    return G;
  },
  regressor(links, q, qd, qdd, g = 9.81) {
    if (!this.GB) this.GB = [...Array(10).keys()].map((k) => this.Gpi([...Array(10).keys()].map((j) => (j === k ? 1 : 0))));
    const R3 = this.R3, n = links.length, Ts = [], Vs = [], Vds = [];
    let V = [0, 0, 0, 0, 0, 0], Vd = [0, 0, 0, 0, 0, g];
    for (let i = 0; i < n; i++) {
      const L = links[i], T = R3.mul(R3.T(R3.rot(L.axis, -q[i]), [0, 0, 0]), L.M), Ad = this.Ad(T), A = [...L.axis, 0, 0, 0];
      V = this.mv6(Ad, V).map((x, k) => x + A[k] * qd[i]);
      const aV = this.adv(V, A);
      Vd = this.mv6(Ad, Vd).map((x, k) => x + aV[k] * qd[i] + A[k] * qdd[i]);
      Ts.push(Ad); Vs.push(V); Vds.push(Vd);
    }
    const Y = Array.from({ length: n }, () => new Array(13 * n).fill(0));
    for (let i = 0; i < n; i++) {
      let X = this.GB.map((Gk) => { const a = this.mv6(Gk, Vds[i]), b = this.adTv(Vs[i], this.mv6(Gk, Vs[i])); return a.map((x, k) => x - b[k]); });
      for (let j = i; j >= 0; j--) {
        for (let k = 0; k < 10; k++) Y[j][10 * i + k] = R3.dot(links[j].axis, X[k].slice(0, 3));
        if (j > 0) X = X.map((x) => this.mtv6(Ts[j], x));
      }
      Y[i][10 * n + i] = qdd[i]; Y[i][11 * n + i] = Math.sign(qd[i]); Y[i][12 * n + i] = qd[i];
    }
    return Y;
  },
  solveSym(A, b) {                // 对称正定方程组（楚列斯基分解）
    const n = b.length, L = Array.from({ length: n }, () => new Array(n).fill(0));
    for (let j = 0; j < n; j++) {
      let s = A[j][j]; for (let k = 0; k < j; k++) s -= L[j][k] * L[j][k];
      L[j][j] = Math.sqrt(Math.max(s, 1e-300));
      for (let i = j + 1; i < n; i++) { let t = A[i][j]; for (let k = 0; k < j; k++) t -= L[i][k] * L[j][k]; L[i][j] = t / L[j][j]; }
    }
    const y = new Array(n), x = new Array(n);
    for (let i = 0; i < n; i++) { let s = b[i]; for (let k = 0; k < i; k++) s -= L[i][k] * y[k]; y[i] = s / L[i][i]; }
    for (let i = n - 1; i >= 0; i--) { let s = y[i]; for (let k = i + 1; k < n; k++) s -= L[k][i] * x[k]; x[i] = s / L[i][i]; }
    return x;
  },
  gauss(rng) {                    // 标准正态（Box–Muller）；rng 为 [0, 1) 均匀分布
    const u = Math.max(rng(), 1e-12), v = rng();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  },
  mulberry(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; },
  fourier(t) {
    const wf = 2 * Math.PI / 10, q = [], qd = [], qdd = [];
    for (let i = 0; i < 6; i++) {
      let a = this.Q0[i], b = 0, c = 0;
      for (let l = 1; l <= 5; l++) {
        const w = wf * l, s = Math.sin(w * t), co = Math.cos(w * t), A = this.EA[i][l - 1], B = this.EB[i][l - 1];
        a += A / w * s - B / w * co; b += A * co + B * s; c += -A * w * s + B * w * co;
      }
      q.push(a); qd.push(b); qdd.push(c);
    }
    return { q, qd, qdd };
  },
  truth(api) {                                    // 负载的真值，质心写在法兰坐标系中
    return { m: api.p.load, c: [api.p.cx, 0.16114 + api.p.cy, api.p.cz] };
  },
  solve(s) {
    const x = this.solveSym(s.A.map((r, i) => r.map((v, j) => v + (i === j ? 1e-12 : 0))), s.b);
    const m = x[0], c = [x[1] / m, x[2] / m - 0.1, x[3] / m];
    return { m, c, fc: x.slice(10, 16), fv: x.slice(16, 22) };
  },
  reset(api, s) {
    const { mj, m, d } = api.sim;
    if (!this.armLinks) {                          // 不带负载的手臂（控制器和辨识都把它当作已知）
      const ma = mj.MjModel.from_xml_string(api.mjcf("ur5e", { option: `<option><flag contact="disable"/></option>` }));
      this.armLinks = this.chainM(ma);
      ma.delete();
    }
    if (s.d2) { try { s.d2.delete(); } catch (e) { /* freed */ } }
    s.d2 = new mj.MjData(m);
    const tr = this.fourier(0);
    for (let i = 0; i < 6; i++) { s.d2.qpos[i] = tr.q[i]; s.d2.qvel[i] = tr.qd[i]; d.qpos[i] = tr.q[i]; d.qvel[i] = 0; }
    mj.mj_forward(m, s.d2); mj.mj_forward(m, d);
    s.A = Array.from({ length: 22 }, () => new Array(22).fill(0)); s.b = new Array(22).fill(0);
    s.k = 0; s.fin = false; s.hist = []; s.est = null; s.rng = this.mulberry(2603);
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim, d2 = s.d2, Tr = api.p.Trun, DT = 0.001;
    if (s.fin) { api.stop(); return; }
    for (let step = 0; step < 100 && s.k * DT < Tr; step++, s.k++) {
      const t = s.k * DT, tr = this.fourier(t), q = Array.from(d2.qpos.slice(0, 6)), v = Array.from(d2.qvel.slice(0, 6));
      const ff = this.rnea(this.armLinks, tr.q, tr.qd, tr.qdd).tau;
      const tau = ff.map((x, i) => x + this.KP[i] * (tr.q[i] - q[i]) + this.KD[i] * (tr.qd[i] - v[i]));
      for (let i = 0; i < 6; i++) d2.qfrc_applied[i] = tau[i];
      mj.mj_step(m, d2);
      if (s.k % 2 === 0 && t >= 0.2) {               // 记录：这一步开始时的 θ、θ̇，这一步用的 θ̈ 和力矩（加噪声）
        const a = Array.from(d2.qacc.slice(0, 6)), Y = this.regressor(this.armLinks, q, v, a);
        const arm = this.rnea(this.armLinks, q, v, a).tau;
        for (let i = 0; i < 6; i++) {
          const yv = tau[i] + this.SIG[i] * this.gauss(s.rng) - arm[i];
          const row = [...Y[i].slice(50, 60), ...Y[i].slice(66, 78)];
          for (let p = 0; p < 22; p++) { if (row[p] === 0) continue; s.b[p] += row[p] * yv; for (let r = 0; r < 22; r++) s.A[p][r] += row[p] * row[r]; }
        }
      }
    }
    for (let i = 0; i < 6; i++) { d.qpos[i] = d2.qpos[i]; d.qvel[i] = 0; }
    mj.mj_forward(m, d);
    const t = s.k * DT;
    if (t >= 0.7 && (s.k % 500 === 0 || t >= Tr)) {
      s.est = this.solve(s);
      const tru = this.truth(api);
      s.em = Math.abs(s.est.m - tru.m) / tru.m * 100;
      s.ec = Math.hypot(...s.est.c.map((x, i) => x - tru.c[i])) * 1000;
      s.hist.push([t, s.em, s.ec]);
    }
    if (t >= Tr - 1e-9 && !s.fin) {
      s.fin = true;
      const tru = this.truth(api), e = s.est;
      if (e) {
        api.keep.err = api.keep.err || {};
        api.keep.err[Tr] = s.em;
        const def = Math.abs(tru.m - 3.8) < 0.05 && api.p.cx === 0 && api.p.cy === 0 && api.p.cz === 0;
        if (def && Tr >= 10 && s.em < 1) api.done("mass");
        if (!def && Math.abs(tru.m - 3.8) > 0.05 && (api.p.cx !== 0 || api.p.cy !== 0 || api.p.cz !== 0) && Tr >= 10 && s.ec < 5) api.done("cog");
        const ks = Object.keys(api.keep.err).map(Number), sh = ks.filter((x) => x <= 2), lo = ks.filter((x) => x >= 10);
        if (sh.length && lo.length && api.keep.err[sh[0]] > api.keep.err[lo[0]]) api.done("short");
        if (Tr >= 10 && Math.abs(e.fc[0] - this.physics.FC[0]) / this.physics.FC[0] < 0.05) api.done("fric");
      }
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    api.cplot(56, 10, w - 70, h - 34, [{ pts: H.map((r) => [r[0], Math.min(r[1], 20)]), color: "#d62728" }, { pts: H.map((r) => [r[0], Math.min(r[2], 20)]), color: "#1f77b4" }],
      { xmin: 0, xmax: api.p.Trun, ymin: 0, ymax: 20, xlabel: "t / s", ylabel: "%, mm" });
  },
  readouts(api, s) {
    const f = (v, k = 3) => api.fmt(v, k), tru = this.truth(api), e = s.est;
    const rows = [[["负载的真值：质量 / 质心（法兰坐标系）", "True payload: mass / CoG (flange frame)"], `${f(tru.m, 2)} kg / (${tru.c.map((x) => f(x * 1000, 1)).join(", ")}) mm`]];
    if (e) {
      rows.push([["估计：质量 / 质心", "Estimate: mass / CoG"], `${f(e.m, 3)} kg / (${e.c.map((x) => f(x * 1000, 1)).join(", ")}) mm`]);
      rows.push([["误差：质量 / 质心", "Error: mass / CoG"], `${f(s.em, 2)} % / ${f(s.ec, 2)} mm`]);
      rows.push([["估计的库仑摩擦 f_c1…f_c6（真值 2, 2, 1.5, 0.6, 0.6, 0.5）", "Estimated Coulomb friction f_c1…f_c6 (true 2, 2, 1.5, 0.6, 0.6, 0.5)"], e.fc.map((x) => f(x, 2)).join(", ") + " N·m"]);
    }
    rows.push([["已用的数据", "Data used"], `${f(s.k * 0.001, 1)} s`]);
    return rows;
  },
  tasks: [
    { id: "mass", robot: true, text: ["负载取默认的 3.8 kg、质心不偏移，跑满 10 s：质量估计的误差小于 1%。", "With the default 3.8 kg payload and no extra offset, run the full 10 s: the mass error is below 1 %."],
      demo: { scene: "id", set: { load: 3.8, cx: 0, cy: 0, cz: 0, Trun: 10 }, wait: 10 } },
    { id: "cog", robot: true, text: ["换一个负载：改质量、让质心偏到一侧，跑满 10 s：质心估计的误差小于 5 mm。", "Change the payload: a different mass and an off-centre CoG; run the full 10 s: the CoG error is below 5 mm."],
      demo: { scene: "id", set: { load: 2, cx: 0.05, cy: 0.03, cz: 0, Trun: 10 }, wait: 10 } },
    { id: "short", robot: true, text: ["同一个负载只跑 2 s 以内，再跑满 10 s：比较质量估计的误差。", "With the same payload run for 2 s or less, then for the full 10 s: compare the mass errors."],
      demo: { scene: "id", set: { load: 3.8, cx: 0, cy: 0, cz: 0, Trun: 1.5 }, wait: 4 } },
    { id: "fric", robot: true, text: ["跑满 10 s，看关节 1 的库仑摩擦估计：与真值相差不到 5%。", "Run the full 10 s and look at joint 1's Coulomb friction estimate: within 5 % of the true value."],
      demo: { scene: "id", set: { load: 3.8, cx: 0, cy: 0, cz: 0, Trun: 10 }, wait: 10 } },
  ],
  think: ["实验中控制器只知道手臂、不知道负载，跟踪误差有 1° 量级，可辨识用的是实际测到的运动，不是指令。为什么跟踪得不准并不妨碍辨识？",
          "The controller knows only the arm, not the payload, so tracking errors reach about 1°; but identification uses the measured motion, not the command. Why does poor tracking not spoil the identification?"],
});
