// 实验 26.2 激励轨迹与条件数（配 26.2 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex26_2.py 同一版本。
// 书中的 UR5e 模型（外观为零件库 glTF）按轨迹回放（运动学），每 0.05 s（轨迹时间）取一个时刻，用回归矩阵（式 (26.1.5)；
//   连杆数据由页面从 MuJoCo 模型读出，列的次序与程序 _ch26.py 相同）算出这一时刻的 6 × 78 矩阵，只留 52 个基参数的列（IND，
//   由程序 26.1.1 的带列主元 QR 分解求出），把 WᵀW 累加起来；条件数 = √(λ_max/λ_min)，λ 由雅可比法求出。
// 场景 1：26.2 节优化的激励轨迹（傅里叶级数，周期 10 s，系数 EXC_A、EXC_B 与程序相同），可按比例缩小幅度。
// 场景 2：第 22 章的上下料动作，往返一次。
// 阈值由 ex26_2.py 按同样的取样核算：幅度 1、0.7、0.5、0.3 时整个周期的条件数为 88、284、858、4299；只跑前半个周期为 352；
//   上下料动作秩亏（条件数 10¹⁷ 量级）。
WQ.lab({
  title: ["实验 26.2 激励轨迹与条件数", "Lab 26.2 Exciting trajectories and the condition number"],
  goal: ["看 UR5e 沿不同的轨迹运动时，回归矩阵的条件数怎样随运动的“丰富程度”变化，理解为什么辨识要专门设计激励轨迹。",
         "Watch how the regressor's condition number depends on how rich the UR5e's motion is, and see why identification needs a specially designed exciting trajectory."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "exc", robot: true, name: ["激励轨迹", "Exciting trajectory"], hide: [],
      problem: { title: ["机器人问题：怎样动，参数才测得准", "Robot problem: how should the arm move to measure its parameters well"],
                 text: ["辨识要让机器人按某条轨迹动起来，测关节角和电机力矩。动作幅度小一点安全，可数据够不够？",
                        "Identification makes the robot follow a trajectory while joint angles and motor torques are recorded. Smaller motions are safer, but is the data good enough?"] } },
    { id: "cell", robot: true, name: ["拿日常动作来辨识", "Using an everyday move"], hide: ["amp"],
      problem: { title: ["机器人问题：能不能直接用生产中的动作", "Robot problem: could the production moves be used directly"],
                 text: ["上下料动作每天重复几千次，数据多得是。拿它来辨识行不行？", "The loading move repeats thousands of times a day, so there is plenty of data. Can it be used for identification?"] } },
  ],
  params: [
    { id: "amp", name: ["幅度（相对于优化的轨迹）", "Amplitude (relative to the optimized trajectory)"], min: 0.1, max: 1, step: 0.05, value: 1, unit: "", digits: 2 },
  ],
  legend: [{ color: "#1f77b4", name: ["条件数随数据的变化（对数）", "condition number as data accumulate (log)"] }],
  physics: {
    camera: [30, 18, 0.75],
    xml(api) { return api.mjcf("ur5e", { option: `<option timestep="0.002"><flag contact="disable"/></option>` }); },
  },
  Q0: [0, -90, 90, -90, -90, 0].map((x) => x * Math.PI / 180),
  EA: [[-0.797811,  0.134195, -0.033239, -0.21617 , -0.281421], [-0.098781, -0.138661, -0.297528,  0.202307, -0.644069], [ 0.06109 ,  0.162527,  0.243568, -0.441413,  0.00809 ], [-0.582489,  0.198841,  0.423006,  0.135481, -0.099577], [ 0.171012,  0.260319,  0.144237, -0.004926, -0.238638], [-0.757907, -0.086944, -0.351509,  0.357326,  0.44112 ]],
  EB: [[-0.304145, -0.19026 , -0.375126, -0.255614,  0.387034], [-0.057374,  0.252901, -0.052444,  0.282505,  0.201235], [ 0.269002,  0.156995, -0.013454, -0.225422,  0.29934 ], [ 0.320599,  0.201782, -0.245445,  0.15699 , -0.134112], [ 0.249801,  0.600106,  0.082994,  0.257953, -0.270796], [ 0.062983,  0.077135, -0.195247,  0.18391 , -0.038834]],
  QA: [98.1725, -86.0425, 114.5326, -118.4901, -90.0, 8.1725].map((x) => x * Math.PI / 180),
  QB: [201.5997, -50.543, 79.7267, -29.1837, -68.4003, 0.0].map((x) => x * Math.PI / 180),
  TM: 1.318,
  IND: [11, 13, 14, 15, 16, 18, 21, 23, 24, 25, 26, 27, 28, 31, 35, 36, 38, 39, 41, 42, 43, 45, 46, 47, 48, 49, 51, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77],
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
  fourier(t, amp) {                               // 式 (26.2.1)，T_f = 10 s
    const wf = 2 * Math.PI / 10, q = [], qd = [], qdd = [];
    for (let i = 0; i < 6; i++) {
      let a = this.Q0[i], b = 0, c = 0;
      for (let l = 1; l <= 5; l++) {
        const w = wf * l, s = Math.sin(w * t), co = Math.cos(w * t), A = amp * this.EA[i][l - 1], B = amp * this.EB[i][l - 1];
        a += A / w * s - B / w * co; b += A * co + B * s; c += -A * w * s + B * w * co;
      }
      q.push(a); qd.push(b); qdd.push(c);
    }
    return { q, qd, qdd };
  },
  quintic(qa, qb, T, t) {
    const u = Math.min(Math.max(t / T, 0), 1);
    const s = 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5, sd = (30 * u ** 2 - 60 * u ** 3 + 30 * u ** 4) / T, sdd = (60 * u - 180 * u ** 2 + 120 * u ** 3) / T ** 2;
    const dl = qb.map((b, i) => b - qa[i]);
    return { q: qa.map((a, i) => a + s * dl[i]), qd: dl.map((v) => sd * v), qdd: dl.map((v) => sdd * v) };
  },
  sample(api, t) {
    if (api.scene === "exc") return this.fourier(t, api.p.amp);
    return t <= this.TM ? this.quintic(this.QA, this.QB, this.TM, t) : this.quintic(this.QB, this.QA, this.TM, t - this.TM);
  },
  duration(api) { return api.scene === "exc" ? 10 : 2 * this.TM; },
  cond(s) {
    const ev = this.la.eigSym(s.A).values, lmax = ev[ev.length - 1], lmin = ev[0];
    return lmin <= lmax * 1e-13 ? Infinity : Math.sqrt(lmax / lmin);
  },
  reset(api, s) {
    const { mj, m, d } = api.sim;
    this.la = api.la;
    this.links = this.chain(api);
    const nb = this.IND.length;
    s.A = Array.from({ length: nb }, () => new Array(nb).fill(0));
    s.n = 0; s.clock = 0; s.next = 0; s.hist = []; s.c = NaN; s.fin = false; s.vmax = 0; s.c5 = NaN;
    const tr = this.sample(api, 0);
    for (let i = 0; i < 6; i++) { d.qpos[i] = tr.q[i]; d.qvel[i] = 0; d.ctrl[i] = tr.q[i]; }
    mj.mj_forward(m, d);
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim, T = this.duration(api);
    s.clock += dt * (api.rate || 1) * 2;            // 两倍速回放
    while (s.next <= Math.min(s.clock, T) + 1e-9 && s.next < T - 1e-9) {
      const tr = this.sample(api, s.next), Y = this.regressor(this.links, tr.q, tr.qd, tr.qdd);
      const rows = Y.map((r) => this.IND.map((j) => r[j]));
      for (const r of rows) for (let a = 0; a < r.length; a++) { if (r[a] === 0) continue; for (let b = 0; b < r.length; b++) s.A[a][b] += r[a] * r[b]; }
      s.n++; s.vmax = Math.max(s.vmax, ...tr.qd.map(Math.abs));
      s.next += 0.05;
      if (s.n % 20 === 0 && s.n >= 20) { s.c = this.cond(s); s.hist.push([s.next, Math.log10(Math.min(s.c, 1e18))]); }
      if (api.scene === "exc" && Math.abs(s.next - 5) < 1e-6) s.c5 = this.cond(s);
    }
    const tr = this.sample(api, Math.min(s.clock, T));
    for (let i = 0; i < 6; i++) { d.qpos[i] = tr.q[i]; d.qvel[i] = 0; d.ctrl[i] = tr.q[i]; }
    mj.mj_forward(m, d);
    if (s.clock >= T && !s.fin) {
      s.fin = true;
      s.c = this.cond(s); s.hist.push([T, Math.log10(Math.min(s.c, 1e18))]);
      if (api.scene === "exc") {
        const a = api.p.amp;
        if (Math.abs(a - 1) < 1e-9 && s.c < 150) api.done("opt");
        if (a <= 0.3 + 1e-9 && s.c > 1000) api.done("small");
        if (Math.abs(a - 1) < 1e-9 && s.c5 > 2 * s.c) api.done("half");
      } else if (!(s.c < 1e5)) api.done("cell");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    api.cplot(56, 10, w - 70, h - 34, [{ pts: H, color: "#1f77b4" }], { xmin: 0, xmax: this.duration(api), ymin: 0, ymax: 18, xlabel: "t / s", ylabel: "log₁₀ κ" });
  },
  readouts(api, s) {
    const f = (v, k = 0) => api.fmt(v, k);
    const cs = (c) => (Number.isNaN(c) ? "—" : !Number.isFinite(c) ? api.T("无穷大（秩亏）", "infinite (rank deficient)") : c > 1e6 ? c.toExponential(1) : f(c, 0));
    const rows = [
      [["已取的时刻 / 方程个数", "Instants taken / equations"], `${s.n || 0} / ${6 * (s.n || 0)}`],
      [["基参数的个数", "Number of base parameters"], String(this.IND.length)],
      [["条件数 κ", "Condition number κ"], cs(s.c)],
      [["最大关节速度", "Largest joint rate"], f(s.vmax || 0, 2) + " rad/s"],
    ];
    if (api.scene === "exc") rows.push([["前半个周期结束时的条件数", "Condition number after the first half period"], cs(s.c5)]);
    return rows;
  },
  tasks: [
    { id: "opt", robot: true, text: ["按优化的轨迹（幅度 1）跑完一个周期：条件数小于 150。", "Run the optimized trajectory (amplitude 1) for a full period: the condition number is below 150."],
      demo: { scene: "exc", set: { amp: 1 }, wait: 8 } },
    { id: "half", robot: true, text: ["同一条轨迹，比较跑完前半个周期和整个周期的条件数：前者是后者的 2 倍以上。", "On the same trajectory compare the condition number after half a period and after the full period: the first is more than twice the second."],
      demo: { scene: "exc", set: { amp: 1 }, wait: 8 } },
    { id: "small", robot: true, text: ["把幅度缩小到 0.3 或更小再跑一个周期：条件数超过 1000。", "Shrink the amplitude to 0.3 or less and run a full period: the condition number exceeds 1000."],
      demo: { scene: "exc", set: { amp: 0.3 }, wait: 8 } },
    { id: "cell", robot: true, text: ["拿第 22 章的上下料动作（往返）来辨识：回归矩阵秩亏，有的参数组合根本测不出来。", "Use the Chapter 22 loading move (there and back): the regressor is rank deficient, so some parameter combinations cannot be measured at all."],
      demo: { scene: "cell", wait: 4 } },
  ],
  think: ["上下料动作每天重复几千次，数据量很大，为什么仍然测不出全部基参数？如果把多种生产动作的数据合在一起呢？",
          "The loading move repeats thousands of times a day, so why can it still not reveal all the base parameters? What if data from several production moves were combined?"],
});
