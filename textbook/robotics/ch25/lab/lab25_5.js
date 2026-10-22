// 实验 25.5 加负载，看哪个关节先超限（配 25.5 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex25_5.py 同一版本。
// 书中的 UR5e 模型（外观为零件库 glTF）做第 22 章的上下料动作（A → B，五次多项式，用时 T），法兰上是夹爪 + SH-301 毛坯
//   （算例 23.2.2 的组合体按质量等比缩放；3.8 kg 时与之相同，质心在法兰外 0.161 m，可再沿工具方向外移 r）。
// 每一帧用牛顿-欧拉递推（算法 25.2.1；连杆数据由页面从 MuJoCo 模型读出，负载 body 并入连杆 6）算出六个关节的力矩，
//   与上限比较：关节 1～3 为 150 N·m，关节 4～6 为 28 N·m（UR 公司资料）。递推与 MuJoCo 的 mj_inverse 逐帧核对。
// 1.318 s 是第 22 章按速度、加速度、加加速度上限（后两者为设定的示意值）求出的最短时间；短于 1.077 s 时关节 1 的速度会超过 180 °/s，读数里会提示。
// 阈值由 ex25_5.py 核算：3.8 kg、T = 1.318 s 时峰值与上限之比最大的是关节 2（34%）和关节 4（33%）；
//   同一动作负载加到 11.70 kg 时关节 4 先到上限；5 kg 时不超限的最短动作时间 0.608 s（关节 4）；5 kg、T = 1.318 s 时
//   质心再外移 0.350 m 关节 4 到上限。
WQ.lab({
  title: ["实验 25.5 加负载，看哪个关节先超限", "Lab 25.5 Add payload and see which joint hits its limit first"],
  goal: ["用牛顿-欧拉递推算出 UR5e 搬运毛坯时六个关节的力矩，改变负载、重心位置和动作快慢，找出最先超过力矩上限的关节。",
         "Compute the UR5e's six joint torques with the recursive Newton–Euler algorithm while it carries a blank, change the payload, its centre of gravity and the speed, and find the joint that exceeds its torque limit first."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "move", robot: true, name: ["上下料动作", "The loading move"], hide: [],
      problem: { title: ["机器人问题：换一个更重的工件，这台 UR5e 还行吗", "Robot problem: can this UR5e handle a heavier part"],
                 text: ["车间要改做一种更重的轴，或者想把节拍再压短一点。哪个关节会最先吃不消？是扛着整条手臂的肩，还是手腕？",
                        "The shop wants to switch to a heavier shaft, or to shorten the cycle a little more. Which joint gives out first: the shoulder that carries the whole arm, or the wrist?"] } },
  ],
  params: [
    { id: "load", name: ["负载（夹爪 + 毛坯）", "Payload (gripper + blank)"], min: 0, max: 15, step: 0.1, value: 3.8, unit: "kg", digits: 1 },
    { id: "T", name: ["动作用时 T", "Duration of the move T"], min: 0.5, max: 2.5, step: 0.001, value: 1.318, unit: "s", digits: 3 },
    { id: "r", name: ["重心再外移 r", "Extra centre-of-gravity offset r"], min: 0, max: 0.5, step: 0.01, value: 0, unit: "m", digits: 2 },
  ],
  legend: [{ color: "#7a868d", name: ["关节 1", "joint 1"] }, { color: "#1f77b4", name: ["关节 2", "joint 2"] }, { color: "#2ca02c", name: ["关节 3", "joint 3"] },
           { color: "#d62728", name: ["关节 4", "joint 4"] }, { color: "#b8860b", name: ["关节 5", "joint 5"] }, { color: "#9467bd", name: ["关节 6（纵轴：|τ| / 上限）", "joint 6 (vertical: |τ| / limit)"] }],
  physics: {
    camera: [30, 18, 0.75],
    payload(load, r) {
      const k = load / 3.8, I = [0.0260338 * k, 0.0017083 * k, 0.0262671 * k];
      return `<body name="payload" pos="0 0.1 0"><inertial pos="0 ${0.16114 + r} 0" mass="${Math.max(load, 1e-6)}" diaginertia="${Math.max(I[0], 1e-9)} ${Math.max(I[1], 1e-9)} ${Math.max(I[2], 1e-9)}"/>
<geom type="box" pos="0 0.05 0" size="0.04 0.05 0.03" rgba="0.36 0.42 0.45 1" mass="0" contype="0" conaffinity="0"/>
<geom type="cylinder" pos="0 ${0.2008 + r / 2} 0" quat="0.7071068 0.7071068 0 0" size="0.025 ${0.0908 + r / 2}" rgba="0.62 0.55 0.35 1" mass="0" contype="0" conaffinity="0"/></body>`;
    },
    xml(api) { return api.mjcf("ur5e", { option: `<option timestep="0.002"><flag contact="disable"/></option>`, tool: api.p.load > 0 ? this.payload(api.p.load, api.p.r) : "" }); },
  },
  QA: [98.1725, -86.0425, 114.5326, -118.4901, -90.0, 8.1725].map((x) => x * Math.PI / 180),
  QB: [201.5997, -50.543, 79.7267, -29.1837, -68.4003, 0.0].map((x) => x * Math.PI / 180),
  TM: 1.318,
  LIM: [150, 150, 150, 28, 28, 28],
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
  traj(T, t) {
    const u = Math.min(Math.max(t / T, 0), 1);
    const s = 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5, sd = (30 * u ** 2 - 60 * u ** 3 + 30 * u ** 4) / T, sdd = (60 * u - 180 * u ** 2 + 120 * u ** 3) / T ** 2;
    const dl = this.QB.map((b, i) => b - this.QA[i]);
    return { q: this.QA.map((a, i) => a + s * dl[i]), qd: dl.map((v) => sd * v), qdd: dl.map((v) => sdd * v) };
  },
  sweep(api, T) {                                 // 整个动作的峰值（与画面播放无关，按 400 个时刻算）
    const pk = [0, 0, 0, 0, 0, 0], first = [Infinity, Infinity, Infinity, Infinity, Infinity, Infinity];
    for (let k = 0; k <= 400; k++) {
      const t = T * k / 400, tr = this.traj(T, t), tau = this.rnea(this.links, tr.q, tr.qd, tr.qdd).tau;
      tau.forEach((x, j) => { const u = Math.abs(x) / this.LIM[j]; pk[j] = Math.max(pk[j], u); if (u > 1 && first[j] === Infinity) first[j] = t; });
    }
    return { pk, first };
  },
  reset(api, s) {
    const { mj, m, d } = api.sim;
    this.links = this.chain(api);
    s.clock = 0; s.fin = false; s.err = 0; s.hist = []; s.cur = [0, 0, 0, 0, 0, 0];
    s.sw = this.sweep(api, api.p.T);
    const vmax = Math.max(...this.QB.map((b, i) => Math.abs(b - this.QA[i]))) * 1.875 / api.p.T * 180 / Math.PI;
    s.vmax = vmax;
    const q = this.QA.slice();
    for (let i = 0; i < 6; i++) { d.qpos[i] = q[i]; d.qvel[i] = 0; d.ctrl[i] = q[i]; }
    mj.mj_forward(m, d);
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim, T = api.p.T;
    s.clock += dt * (api.rate || 1) / 2;            // 放慢 2 倍播放
    const t = Math.min(s.clock, T), tr = this.traj(T, t), tau = this.rnea(this.links, tr.q, tr.qd, tr.qdd).tau;
    for (let i = 0; i < 6; i++) { d.qpos[i] = tr.q[i]; d.qvel[i] = tr.qd[i]; d.qacc[i] = tr.qdd[i]; }
    mj.mj_inverse(m, d);
    for (let i = 0; i < 6; i++) s.err = Math.max(s.err, Math.abs(tau[i] - d.qfrc_inverse[i]));
    s.cur = tau.map((x, j) => Math.abs(x) / this.LIM[j]);
    s.hist.push([t, ...s.cur]);
    for (let i = 0; i < 6; i++) { d.qpos[i] = tr.q[i]; d.qvel[i] = 0; d.ctrl[i] = tr.q[i]; }
    mj.mj_forward(m, d);
    if (s.clock >= T && !s.fin) {
      s.fin = true;
      const P = s.sw.pk, L = api.p.load, over = P.map((u) => u > 1), j4 = P[3] > 1 && P.every((u, j) => j === 3 || u <= 1);
      if (Math.abs(L - 3.8) < 0.05 && Math.abs(T - this.TM) < 0.002 && api.p.r === 0 && s.err < 1e-9) api.done("base");
      if (Math.abs(T - this.TM) < 0.002 && api.p.r === 0 && L >= 11.6 && L <= 12.5 && j4) api.done("first");
      if (Math.abs(L - 5) < 0.05 && api.p.r === 0 && T >= 0.608 && T <= 0.64 && !over.some(Boolean)) api.done("fast");
      if (Math.abs(L - 5) < 0.05 && Math.abs(T - this.TM) < 0.002 && api.p.r >= 0.34 && api.p.r <= 0.4 && j4) api.done("offset");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    const cols = ["#7a868d", "#1f77b4", "#2ca02c", "#d62728", "#b8860b", "#9467bd"];
    const ser = cols.map((c, k) => ({ pts: H.map((r) => [r[0], r[k + 1]]), color: c }));
    ser.push({ pts: [[0, 1], [api.p.T, 1]], color: "#e8b4b4" });
    api.cplot(56, 10, w - 70, h - 34, ser, { xmin: 0, xmax: api.p.T, ymin: 0, ymax: Math.max(1.2, ...s.sw.pk) * 1.05, xlabel: "t / s", ylabel: "|τ| / τmax" });
  },
  readouts(api, s) {
    if (!s.sw) return [];
    const pc = (u) => api.fmt(100 * u, 0) + "%", P = s.sw.pk;
    let fj = -1, ft = Infinity;
    s.sw.first.forEach((t, j) => { if (t < ft) { ft = t; fj = j; } });
    const rows = [
      [["此刻 |τ| / 上限（关节 1～6）", "Now |τ| / limit (joints 1–6)"], s.cur.map(pc).join(", ")],
      [["整个动作的峰值 / 上限（关节 1～6）", "Peak / limit over the move (joints 1–6)"], P.map(pc).join(", ")],
      [["最先超限的关节（时刻）", "First joint over its limit (time)"], fj < 0 ? api.T("都没有超限", "none") : `${fj + 1} (t = ${api.fmt(ft, 3)} s)`],
      [["峰值速度（上限 180 °/s）", "Peak joint speed (limit 180 °/s)"], api.fmt(s.vmax, 1) + " °/s" + (s.vmax > 180.5 ? api.T("  超过上限", "  over the limit") : "")],
      [["递推与 MuJoCo 的最大差别", "Largest difference from MuJoCo"], (s.err || 0).toExponential(1) + " N·m"],
    ];
    return rows;
  },
  tasks: [
    { id: "base", robot: true, text: ["3.8 kg、T = 1.318 s 运行一次：峰值与上限之比最大的是哪两个关节？",
                                      "Run with 3.8 kg and T = 1.318 s: which two joints come closest to their limits?"],
      demo: { scene: "move", set: { load: 3.8, T: 1.318, r: 0 }, wait: 4 } },
    { id: "first", robot: true, text: ["T = 1.318 s，把负载加到刚好有一个关节超限（不超过 12.5 kg）：是哪个关节？",
                                       "With T = 1.318 s, raise the payload until just one joint is over its limit (12.5 kg at most): which joint?"],
      demo: { scene: "move", set: { load: 12, T: 1.318, r: 0 }, wait: 4 } },
    { id: "fast", robot: true, text: ["负载 5 kg：找出六个关节都不超限的最短动作时间（误差 0.03 s 以内）。这时速度还在上限以内吗？",
                                      "With 5 kg, find the shortest move time with all six joints within their limits (to within 0.03 s). Are the speeds still within the limit?"],
      demo: { scene: "move", set: { load: 5, T: 0.62, r: 0 }, wait: 3 } },
    { id: "offset", robot: true, text: ["负载 5 kg、T = 1.318 s：把重心沿工具方向外移，移多远开始有关节超限？是哪个关节？",
                                        "With 5 kg and T = 1.318 s, move the centre of gravity outward along the tool: how far before a joint exceeds its limit, and which one?"],
      demo: { scene: "move", set: { load: 5, T: 1.318, r: 0.36 }, wait: 4 } },
  ],
  think: ["关节 4 的力矩并不比关节 2 大，为什么它反而先超限？如果你是 UR 的设计师，会把腕部电机加大吗？代价是什么？",
          "Joint 4's torque is far smaller than joint 2's, so why does it exceed its limit first? If you were designing the UR5e, would you fit a bigger wrist motor, and what would it cost?"],
});
