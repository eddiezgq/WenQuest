// 实验 26.4 关节摩擦的恒速试验（配 26.4 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex26_4.py 同一版本。
// “真实”的 UR5e：书中模型加关节摩擦（frictionloss 为干摩擦、damping 为黏性摩擦，与程序 _ch26.py 的 FC_TRUE、FV_TRUE 相同，示意值），
//   执行器关掉，力矩直接加在关节上。另开一份 MjData，从初始姿态 θ₀ = (0, −90°, 90°, −90°, −90°, 0) 出发，让所选关节以滑块给定的恒定速度转动，
//   其余关节由 PD 保持：τ = RNEA(θ_d, θ̇_d, 0) + K_p(θ_d − θ) + K_d(θ̇_d − θ̇)。3 s 后取最后 1.5 s 的平均力矩，减去模型的重力项和速度项
//   （关节 1 的轴竖直，两者为零），就是这个速度下的摩擦力矩；每做一次，记下一个点（保留到重做实验为止）。
// 正、负速度各有两个以上的点时，用最小二乘拟合 τ = f_c sign θ̇ + f_v θ̇。
// 阈值由 ex26_4.py 核算：关节 1 拟合得 f_c = 2.0000、f_v = 1.5000（模型中的值 2.0、1.5），关节 6 为 0.5000、0.3000。
WQ.lab({
  title: ["实验 26.4 关节摩擦的恒速试验", "Lab 26.4 Constant-speed friction tests"],
  goal: ["让 UR5e 的一个关节以不同的恒定速度转动，测出摩擦力矩与速度的关系，拟合库仑摩擦和黏性摩擦。",
         "Turn one UR5e joint at several constant speeds, measure how the friction torque depends on speed, and fit the Coulomb and viscous friction."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "const", robot: true, name: ["恒速试验", "Constant-speed test"], hide: [],
      problem: { title: ["机器人问题：电机有一部分力气花在了摩擦上", "Robot problem: part of the motor effort goes into friction"],
                 text: ["关节里的减速器和轴承有摩擦。它有多大？与速度有什么关系？不知道它，前馈和碰撞检测都做不准。",
                        "The gearbox and bearings in a joint have friction. How large is it, and how does it depend on speed? Without it, feedforward and collision detection are inaccurate."] } },
  ],
  params: [
    { id: "joint", name: ["关节", "Joint"], min: 1, max: 6, step: 5, value: 1, unit: "", digits: 0 },
    { id: "w", name: ["转速 θ̇", "Speed θ̇"], min: -1.5, max: 1.5, step: 0.05, value: 0.5, unit: "rad/s", digits: 2 },
    { id: "auto", name: ["一次测一组（±0.2、±0.5、±1.0 rad/s）", "Measure a set in one go (±0.2, ±0.5, ±1.0 rad/s)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  legend: [{ color: "#d62728", name: ["测得的点", "measured points"] }, { color: "#1f77b4", name: ["拟合的 f_c sign θ̇ + f_v θ̇", "fitted f_c sign θ̇ + f_v θ̇"] }],
  physics: {
    camera: [30, 18, 0.75],
    FC: [2.0, 2.0, 1.5, 0.6, 0.6, 0.5], FV: [1.5, 1.5, 1.0, 0.3, 0.3, 0.3],
    xml(api) {
      let t = api.mjcf("ur5e", { option: `<option timestep="0.001"><flag contact="disable" actuation="disable"/></option>` });
      const names = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"];
      names.forEach((nm, i) => { t = t.replace(`<joint name="${nm}"`, `<joint name="${nm}" frictionloss="${this.FC[i]}" damping="${this.FV[i]}"`); });
      return t.replace('<option integrator="implicitfast" />', "");
    },
  },
  Q0: [0, -90, 90, -90, -90, 0].map((x) => x * Math.PI / 180),
  KP: [2000, 2000, 2000, 400, 400, 400], KD: [400, 400, 400, 80, 80, 80],
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
  fit(pts) {
    let a = 0, b = 0, c = 0, p = 0, q = 0;                       // 正规方程：[sign, w]
    pts.forEach(([w, t]) => { const s = Math.sign(w); a += s * s; b += s * w; c += w * w; p += s * t; q += w * t; });
    const det = a * c - b * b;
    return det > 1e-12 ? { fc: (p * c - b * q) / det, fv: (a * q - b * p) / det } : null;
  },
  spin(api, s, w) {                               // 从 θ₀ 出发，所选关节以 w 匀速转动
    const { mj, m } = api.sim, j = api.p.joint - 1;
    if (s.d2) { try { s.d2.delete(); } catch (e) { /* freed */ } }
    s.d2 = new mj.MjData(m);
    for (let i = 0; i < 6; i++) { s.d2.qpos[i] = this.Q0[i]; s.d2.qvel[i] = i === j ? w : 0; }
    mj.mj_forward(m, s.d2);
    s.k = 0; s.sum = 0; s.cnt = 0; s.cur = w;
  },
  reset(api, s) {
    const { mj, m, d } = api.sim;
    if (!this.links) this.links = this.chain(api);
    s.queue = api.p.auto ? [0.2, 0.5, 1.0, -0.2, -0.5, -1.0] : [api.p.w];
    s.qi = 0;
    this.spin(api, s, s.queue[0]);
    for (let i = 0; i < 6; i++) { d.qpos[i] = this.Q0[i]; d.qvel[i] = 0; }
    mj.mj_forward(m, d);
    s.fin = false; s.mean = null;
    api.keep.pts = api.keep.pts || { 1: [], 6: [] };
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim, j = api.p.joint - 1, DT = 0.001;
    if (s.fin) { api.stop(); return; }
    const d2 = s.d2, w = s.cur;
    for (let step = 0; step < 150 && s.k < 3000; step++, s.k++) {
      const t = s.k * DT, qd = this.Q0.slice(), vd = [0, 0, 0, 0, 0, 0];
      qd[j] += w * t; vd[j] = w;
      const q = Array.from(d2.qpos.slice(0, 6)), v = Array.from(d2.qvel.slice(0, 6));
      const ff = this.rnea(this.links, qd, vd, [0, 0, 0, 0, 0, 0]).tau;
      const tau = ff.map((x, i) => x + this.KP[i] * (qd[i] - q[i]) + this.KD[i] * (vd[i] - v[i]));
      for (let i = 0; i < 6; i++) d2.qfrc_applied[i] = tau[i];
      mj.mj_step(m, d2);
      if (t >= 1.5) { s.sum += tau[j] - this.rnea(this.links, q, v, [0, 0, 0, 0, 0, 0]).tau[j]; s.cnt++; }
    }
    for (let i = 0; i < 6; i++) { d.qpos[i] = d2.qpos[i]; d.qvel[i] = 0; }
    mj.mj_forward(m, d);
    if (s.k >= 3000 && !s.fin) {
      s.mean = s.sum / s.cnt;
      const P = api.keep.pts[api.p.joint];
      if (Math.abs(w) > 1e-9) P.push([w, s.mean]);
      if (api.p.joint === 1 && Math.abs(w - 0.5) < 1e-9 && Math.abs(s.mean - 2.75) < 0.02) api.done("one");
      if (++s.qi < s.queue.length) { this.spin(api, s, s.queue[s.qi]); return; }
      s.fin = true;
      const F = this.fitJ(api, 1), F6 = this.fitJ(api, 6);
      if (F && Math.abs(F.fc - 2.0) < 0.02 && Math.abs(F.fv - 1.5) < 0.015) api.done("fit1");
      if (F6 && Math.abs(F6.fc - 0.5) < 0.01 && Math.abs(F6.fv - 0.3) < 0.006) api.done("fit6");
      api.stop();
    }
  },
  fitJ(api, jn) {
    const P = (api.keep.pts || {})[jn] || [];
    const np = P.filter((x) => x[0] > 0).length, nn = P.filter((x) => x[0] < 0).length;
    return np >= 2 && nn >= 2 ? this.fit(P) : null;
  },
  chart(api, s, ctx, w, h) {
    const jn = api.p.joint, P = ((api.keep.pts || {})[jn]) || [], F = this.fitJ(api, jn);
    const ymax = jn === 1 ? 5 : 1.2;
    const ser = [{ pts: [[-1.6, 0], [1.6, 0]], color: "#c8ced3" }];
    if (F) { ser.push({ pts: [[0.001, F.fc + F.fv * 0.001], [1.6, F.fc + F.fv * 1.6]], color: "#1f77b4" }); ser.push({ pts: [[-1.6, -F.fc - F.fv * 1.6], [-0.001, -F.fc - F.fv * 0.001]], color: "#1f77b4" }); }
    const o = api.cplot(56, 10, w - 70, h - 34, ser, { xmin: -1.6, xmax: 1.6, ymin: -ymax, ymax, xlabel: "θ̇ / (rad/s)", ylabel: "τ_f / (N·m)" });
    ctx.fillStyle = "#d62728";
    P.forEach(([x, y]) => { ctx.beginPath(); ctx.arc(o.X(x), o.Y(y), 4, 0, 2 * Math.PI); ctx.fill(); });
  },
  readouts(api, s) {
    const f = (v, k = 3) => api.fmt(v, k), jn = api.p.joint, P = ((api.keep.pts || {})[jn]) || [], F = this.fitJ(api, jn);
    const rows = [
      [["这次的平均摩擦力矩", "Mean friction torque in this run"], s.mean === null || s.mean === undefined ? "—" : f(s.mean, 3) + " N·m"],
      [[`关节 ${jn} 已测的点（正 / 负速度）`, `Points measured for joint ${jn} (positive / negative speed)`], `${P.filter((x) => x[0] > 0).length} / ${P.filter((x) => x[0] < 0).length}`],
      [["拟合：f_c / f_v", "Fit: f_c / f_v"], F ? `${f(F.fc, 4)} N·m / ${f(F.fv, 4)} N·m·s/rad` : api.T("正、负速度各要两个点以上", "need two or more points on each side")],
      [["模型中设的值（示意值）", "Values set in the model (illustrative)"], `${this.physics.FC[jn - 1]} N·m / ${this.physics.FV[jn - 1]} N·m·s/rad`],
    ];
    return rows;
  },
  tasks: [
    { id: "one", robot: true, text: ["关节 1 以 0.5 rad/s 匀速转动：测得的摩擦力矩是多少？", "Turn joint 1 at 0.5 rad/s: what friction torque is measured?"],
      demo: { scene: "const", set: { joint: 1, w: 0.5, auto: 0 }, wait: 4 } },
    { id: "fit1", robot: true, text: ["关节 1 在正、负速度下各测两个点以上，拟合的 f_c、f_v 与模型中的值相差不到 1%。", "Measure joint 1 at two or more positive and two or more negative speeds; the fitted f_c and f_v agree with the model within 1 %."],
      demo: { scene: "const", set: { joint: 1, auto: 1 }, wait: 10 } },
    { id: "fit6", robot: true, text: ["换成关节 6 做同样的试验，拟合它的摩擦。", "Do the same test on joint 6 and fit its friction."],
      demo: { scene: "const", set: { joint: 6, auto: 1 }, wait: 10 } },
  ],
  think: ["恒速试验测得的点正好落在两条直线上，是因为仿真中的摩擦本来就是这样设的。真实的减速器在低速处还有斯特里贝克效应，摩擦还随温度变化。你会怎样安排速度点，才能看出这些效应？",
          "The points fall exactly on two straight lines because that is how friction is set in the simulation. A real gearbox shows the Stribeck effect at low speed and changes with temperature. How would you choose the test speeds to reveal these effects?"],
});
