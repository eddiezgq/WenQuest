// 实验 25.1 运动旋量一级一级传出去（配 25.1 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex25_1.py 同一版本。
// 书中的 UR5e 模型（外观为零件库 glTF）。前向递推（式 (25.1.3)、(25.1.4)）用的连杆数据由页面从 MuJoCo 模型读出（chain()），与程序 _ch25.py 相同。
// 场景 1（机器人）：从算例 22.1.1 的位姿 θ_A 出发，六个关节各以滑块给定的恒定角速度转动（θ̈ = 0）。每一帧把 θ、θ̇ 写进 MuJoCo，
//   递推求出各连杆的 (ω_i, v_i) 与连杆原点的加速度 a = v̇ + ω × v（式 (25.1.6)），与 MuJoCo 的 cvel、cacc（mj_rnePostConstraint，
//   换到连杆原点）比较。重力的处理与 MuJoCo 相同：基座以 𝔤 向上加速，所以静止时加速度读数是 9.81 m/s²（向上）；表中另列去掉这一项的值。
// 场景 2（机器人）：第 22 章的上下料动作（A → B，五次多项式，T = 1.318 s，放慢 2 倍），画出各连杆原点与 TCP 的速度。
// 阈值由 ex25_1.py 与 Python 版 MuJoCo 核算：动作中 TCP 速度最大 1.335 m/s（t = 0.623 s）；递推与 MuJoCo 相差 10⁻¹⁴ 量级（任务取 10⁻⁹）。
WQ.lab({
  title: ["实验 25.1 运动旋量一级一级传出去", "Lab 25.1 Passing twists outward link by link"],
  goal: ["用前向递推算出 UR5e 每个连杆的角速度、速度和加速度，与 MuJoCo 的结果逐项比较，看速度怎样一级一级累积。",
         "Compute every UR5e link's angular velocity, velocity and acceleration by the forward recursion, compare them with MuJoCo, and see how the speeds build up link by link."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "speeds", robot: true, name: ["关节匀速转动", "Joints at constant speed"], hide: [],
      problem: { title: ["机器人问题：关节都匀速转，末端为什么还有加速度", "Robot problem: the joints turn steadily, so why does the end accelerate"],
                 text: ["六个关节各以恒定的角速度转动，法兰的速度却在不断改变方向和大小。它的加速度有多大？由哪些关节的转动造成？",
                        "Each joint turns at a constant rate, yet the flange's velocity keeps changing in size and direction. How large is its acceleration, and which joints cause it?"] } },
    { id: "move", robot: true, name: ["上下料动作中的速度", "Speeds during the loading move"], hide: ["w1", "w2", "w3", "w4", "w5", "w6"],
      problem: { title: ["机器人问题：TCP 最快有多快", "Robot problem: how fast does the TCP go"],
                 text: ["UR5e 把毛坯从料架上方送到卡盘前（第 22 章）。动作中各连杆、TCP 的速度是多少？最快的时刻，各关节各贡献多少？",
                        "The UR5e carries the blank from above the rack to the chuck (Chapter 22). How fast do the links and the TCP move, and at the fastest moment how much does each joint contribute?"] } },
  ],
  params: [
    { id: "w1", name: ["关节 1 角速度 θ̇₁", "Joint 1 rate θ̇₁"], min: -2, max: 2, step: 0.1, value: 1, unit: "rad/s", digits: 1 },
    { id: "w2", name: ["关节 2 角速度 θ̇₂", "Joint 2 rate θ̇₂"], min: -2, max: 2, step: 0.1, value: 0, unit: "rad/s", digits: 1 },
    { id: "w3", name: ["关节 3 角速度 θ̇₃", "Joint 3 rate θ̇₃"], min: -2, max: 2, step: 0.1, value: 0, unit: "rad/s", digits: 1 },
    { id: "w4", name: ["关节 4 角速度 θ̇₄", "Joint 4 rate θ̇₄"], min: -2, max: 2, step: 0.1, value: 0, unit: "rad/s", digits: 1 },
    { id: "w5", name: ["关节 5 角速度 θ̇₅", "Joint 5 rate θ̇₅"], min: -2, max: 2, step: 0.1, value: 0, unit: "rad/s", digits: 1 },
    { id: "w6", name: ["关节 6 角速度 θ̇₆", "Joint 6 rate θ̇₆"], min: -2, max: 2, step: 0.1, value: 0, unit: "rad/s", digits: 1 },
  ],
  legend: [{ color: "#4292c6", name: ["各连杆原点的速度（场景 1：角速度为浅色）", "link-origin speeds (scene 1: angular rates in light colour)"] },
           { color: "#d62728", name: ["TCP 的速度", "TCP speed"] }],
  physics: {
    camera: [30, 18, 0.75],
    xml(api) { return api.mjcf("ur5e", { option: `<option timestep="0.002"><flag contact="disable"/></option>` }); },
  },
  QA: [98.1725, -86.0425, 114.5326, -118.4901, -90.0, 8.1725].map((x) => x * Math.PI / 180),
  QB: [201.5997, -50.543, 79.7267, -29.1837, -68.4003, 0.0].map((x) => x * Math.PI / 180),
  TM: 1.318,
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
  traj(t) {                                       // 五次多项式 (22.1.8)
    const T = this.TM, u = Math.min(Math.max(t / T, 0), 1);
    const s = 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5, sd = (30 * u ** 2 - 60 * u ** 3 + 30 * u ** 4) / T, sdd = (60 * u - 180 * u ** 2 + 120 * u ** 3) / T ** 2;
    const dl = this.QB.map((b, i) => b - this.QA[i]);
    return { q: this.QA.map((a, i) => a + s * dl[i]), qd: dl.map((v) => sd * v), qdd: dl.map((v) => sdd * v) };
  },
  mjMotion(api, q, qd, qdd) {                     // MuJoCo 的结果：各连杆原点的速度、加速度（世界坐标系），由 cvel、cacc 换到原点
    const { mj, m, d } = api.sim, R3 = this.R3, out = [];
    for (let i = 0; i < 6; i++) { d.qpos[i] = q[i]; d.qvel[i] = qd[i]; d.qacc[i] = qdd[i]; d.ctrl[i] = q[i]; }
    mj.mj_fwdPosition(m, d); mj.mj_fwdVelocity(m, d); mj.mj_rnePostConstraint(m, d);
    for (const L of this.links) {
      const b = L.b, c = [d.subtree_com[3 * m.body_rootid[b]], d.subtree_com[3 * m.body_rootid[b] + 1], d.subtree_com[3 * m.body_rootid[b] + 2]];
      const p = [d.xpos[3 * b], d.xpos[3 * b + 1], d.xpos[3 * b + 2]], r = R3.sub(p, c);
      const w = Array.from(d.cvel.slice(6 * b, 6 * b + 3)), vc = Array.from(d.cvel.slice(6 * b + 3, 6 * b + 6));
      const al = Array.from(d.cacc.slice(6 * b, 6 * b + 3)), ac = Array.from(d.cacc.slice(6 * b + 3, 6 * b + 6));
      const v = R3.add(vc, R3.cr(w, r));
      const a = R3.add(R3.add(ac, R3.cr(al, r)), R3.cr(w, v));
      const R = [[d.xmat[9 * b], d.xmat[9 * b + 1], d.xmat[9 * b + 2]], [d.xmat[9 * b + 3], d.xmat[9 * b + 4], d.xmat[9 * b + 5]], [d.xmat[9 * b + 6], d.xmat[9 * b + 7], d.xmat[9 * b + 8]]];
      out.push({ w, v, al, a, R, p });
    }
    return out;
  },
  compute(api, s, q, qd, qdd) {
    const R3 = this.R3, r = this.rnea(this.links, q, qd, qdd), mjm = this.mjMotion(api, q, qd, qdd);
    let dv = 0, da = 0;
    const rows = r.V.map((V, i) => {
      const w = V.slice(0, 3), v = V.slice(3), a = R3.add(r.Vd[i].slice(3), R3.cr(w, v)), R = mjm[i].R;
      const Wv = R3.mv(R, w), Vv = R3.mv(R, v), Al = R3.mv(R, r.Vd[i].slice(0, 3)), Aa = R3.mv(R, a);
      for (let k = 0; k < 3; k++) {
        dv = Math.max(dv, Math.abs(Wv[k] - mjm[i].w[k]), Math.abs(Vv[k] - mjm[i].v[k]));
        da = Math.max(da, Math.abs(Al[k] - mjm[i].al[k]), Math.abs(Aa[k] - mjm[i].a[k]));
      }
      const a0 = R3.sub(Aa, [0, 0, 9.81]);                // 去掉“基座向上加速 𝔤”
      return { w: Math.hypot(...w), v: Math.hypot(...v), a: Math.hypot(...Aa), a0: Math.hypot(...a0) };
    });
    const V6 = r.V[5], tcpB = R3.add(V6.slice(3), R3.cr(V6.slice(0, 3), [0, 0.25, 0]));
    s.rows = rows; s.tcp = Math.hypot(...tcpB);
    s.dv = Math.max(s.dv || 0, dv); s.da = Math.max(s.da || 0, da);
  },
  reset(api, s) {
    const { mj, m, d } = api.sim;
    this.links = this.chain(api);
    s.clock = 0; s.fin = false; s.dv = 0; s.da = 0; s.hist = []; s.pk = 0; s.tpk = 0; s.tRun = 0;
    const q = this.QA.slice(), qd = api.scene === "speeds" ? [1, 2, 3, 4, 5, 6].map((k) => api.p["w" + k]) : [0, 0, 0, 0, 0, 0];
    this.compute(api, s, q, qd, [0, 0, 0, 0, 0, 0]);
    for (let i = 0; i < 6; i++) { d.qpos[i] = q[i]; d.qvel[i] = 0; d.ctrl[i] = q[i]; }
    mj.mj_forward(m, d);
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim;
    s.clock += dt * (api.rate || 1) / (api.scene === "move" ? 2 : 1);
    let q, qd, qdd;
    if (api.scene === "speeds") {
      qd = [1, 2, 3, 4, 5, 6].map((k) => api.p["w" + k]);
      const t = Math.min(s.clock, 3);
      q = this.QA.map((a, i) => a + qd[i] * t); qdd = [0, 0, 0, 0, 0, 0];
      this.compute(api, s, q, qd, qdd);
      s.hist.push([t, ...s.rows.map((r) => r.v), s.tcp]);
      s.tRun = t;
      const w = qd, only1 = Math.abs(w[0]) > 0.05 && w.slice(1).every((x) => Math.abs(x) < 1e-9);
      if (t >= 0.5 && only1 && s.rows.every((r) => Math.abs(r.w - Math.abs(w[0])) < 1e-9) && s.dv < 1e-9) api.done("same");
      const par = Math.abs(w[0]) < 1e-9 && Math.abs(w[1] - 1) < 1e-9 && Math.abs(w[2] - 1) < 1e-9 && w.slice(3).every((x) => Math.abs(x) < 1e-9);
      if (t >= 0.5 && par && Math.abs(s.rows[2].w - 2) < 1e-9) api.done("add");
      if (t >= 0.5 && s.rows[5].a0 > 1 && s.da < 1e-9) api.done("accel");
      if (t >= 3) { s.fin = true; api.stop(); }
    } else {
      const t = Math.min(s.clock, this.TM), tr = this.traj(t);
      q = tr.q; qd = tr.qd; qdd = tr.qdd;
      this.compute(api, s, q, qd, qdd);
      s.hist.push([t, ...s.rows.map((r) => r.v), s.tcp]);
      if (s.tcp > s.pk) { s.pk = s.tcp; s.tpk = t; }
      if (s.clock >= this.TM && !s.fin) {
        s.fin = true;
        if (s.dv < 1e-9 && s.da < 1e-9 && s.pk > 1.3 && s.pk < 1.37) api.done("move");
        api.stop();
      }
    }
    for (let i = 0; i < 6; i++) { d.qpos[i] = q[i]; d.qvel[i] = 0; d.ctrl[i] = q[i]; }
    mj.mj_forward(m, d);
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    if (!H.length) return;
    const cols = ["#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"];
    const xmax = api.scene === "move" ? this.TM : 3;
    const ser = cols.map((c, k) => ({ pts: H.filter((_, n) => n % 2 === 0).map((r) => [r[0], r[k + 1]]), color: c }));
    ser.push({ pts: H.filter((_, n) => n % 2 === 0).map((r) => [r[0], r[7]]), color: "#d62728" });
    const ymax = Math.max(0.5, ...H.map((r) => Math.max(...r.slice(1)))) * 1.1;
    api.cplot(56, 10, w - 70, h - 34, ser, { xmin: 0, xmax, ymin: 0, ymax, xlabel: "t / s", ylabel: "|v| / (m/s)" });
  },
  readouts(api, s) {
    if (!s.rows) return [];
    const f = (v, k = 3) => api.fmt(v, k), R = s.rows;
    const rows = [
      [["各连杆的角速度 |ω₁|…|ω₆|", "Angular rates |ω₁|…|ω₆|"], R.map((r) => f(r.w, 3)).join(", ") + " rad/s"],
      [["各连杆原点的速度 |v₁|…|v₆|", "Link-origin speeds |v₁|…|v₆|"], R.map((r) => f(r.v, 3)).join(", ") + " m/s"],
      [["TCP 的速度", "TCP speed"], f(s.tcp) + " m/s"],
      [["连杆 6 原点（腕 3 中心）的加速度：含 / 不含“向上 𝔤”", "Acceleration of link 6's origin (wrist 3 centre): with / without the upward g"], `${f(R[5].a, 3)} / ${f(R[5].a0, 3)} m/s²`],
      [["递推与 MuJoCo 的最大差别：速度 / 加速度", "Largest difference from MuJoCo: velocity / acceleration"], `${(s.dv || 0).toExponential(1)} / ${(s.da || 0).toExponential(1)}`],
    ];
    if (api.scene === "move") rows.push([["TCP 速度的最大值（时刻）", "Peak TCP speed (time)"], `${f(s.pk)} m/s (t = ${f(s.tpk, 3)} s)`]);
    return rows;
  },
  tasks: [
    { id: "same", robot: true, text: ["只转关节 1（其余角速度为 0）：六个连杆的角速度都等于 θ̇₁，递推与 MuJoCo 一致。",
                                      "Turn joint 1 only (other rates zero): all six links have the angular rate θ̇₁, and the recursion agrees with MuJoCo."],
      demo: { scene: "speeds", set: { w1: 1, w2: 0, w3: 0, w4: 0, w5: 0, w6: 0 }, wait: 2 } },
    { id: "add", robot: true, text: ["只转关节 2、3，都取 1 rad/s：连杆 3 的角速度是多少？为什么正好是两者之和？",
                                     "Turn joints 2 and 3 only, both at 1 rad/s: what is link 3's angular rate, and why is it exactly the sum?"],
      demo: { scene: "speeds", set: { w1: 0, w2: 1, w3: 1, w4: 0, w5: 0, w6: 0 }, wait: 2 } },
    { id: "accel", robot: true, text: ["关节都匀速转动（θ̈ = 0）时，找一组角速度使连杆 6 原点（腕 3 中心）的加速度（去掉“向上 𝔤”）超过 1 m/s²。",
                                       "With all joints at constant rates (θ̈ = 0), find rates that give link 6's origin (the wrist 3 centre) an acceleration (without the upward g) above 1 m/s²."],
      demo: { scene: "speeds", set: { w1: 1.5, w2: 0.5, w3: 0, w4: 0, w5: 0, w6: 0 }, wait: 2 } },
    { id: "move", robot: true, text: ["运行上下料动作：读出 TCP 速度的最大值和时刻，递推与 MuJoCo 在整个动作中一致。",
                                      "Run the loading move: read the peak TCP speed and when it occurs; the recursion agrees with MuJoCo throughout."],
      demo: { scene: "move", wait: 5 } },
  ],
  think: ["关节匀速转动时，法兰的加速度是从哪里来的？把式 (25.1.4) 中的 [ad_𝒱]A θ̇ 项和第 10 章的向心加速度、科氏加速度对照一下。",
          "Where does the flange's acceleration come from when every joint turns steadily? Compare the [ad_𝒱]𝒜θ̇ term of Eq. (25.1.4) with the centripetal and Coriolis accelerations of Chapter 10."],
});
