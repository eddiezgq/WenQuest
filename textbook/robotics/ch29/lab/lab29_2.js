// 实验 29.2 仿真与现实（配 29.4 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex29_4.py 同一版本、同一个模型、同一个算法（_ch29.cr_track）。
// “现场”的 WQ-CR5：零件库模型（教材 models/mjcf/wqcr5.xml）+ 法兰上的标准负载（钢块约 5 kg，质量、惯量可乘以负载倍数）+ 关节摩擦
//   （库仑摩擦 = 关节测试台“空载摩擦力矩”的名义值 × 摩擦倍数，黏性摩擦取 MJCF 的名义值 × 摩擦倍数）；执行器关掉，力矩直接加在关节上，
//   积分器 implicitfast、步长 0.5 ms（与程序相同）。另开一份 MjData 自己推进，画面按它显示。
// 控制器每个控制周期 T_c 采样一次，用 delay 以前的关节角、角速度（缓存按 0.5 ms 一格），零阶保持：
//   A 出厂位置环：τ = kp(θ_d − θ) + kv(θ̇_d − θ̇)，kp、kv 与 wqcr5.SERVO_KP、SERVO_KV 相同；
//   B 名义模型（标准负载、名义摩擦）的逆动力学 + 摩擦前馈 f_c tanh(θ̇_d/0.01) + f_v θ̇_d + PD，kp = M_ii ω_n²、kv = 2ω_n M_ii（ζ = 1），
//     M_ii 是工作姿态带标准负载时质量矩阵的对角元（由程序 29.4.1 算出，下面的 MD）。
// 标准动作 = wqcr5.runin_ref：初始位姿 → (90, −45, 60, −105, −90, 45)° → (−60, −110, 120, −100, −60, −45)° → 初始位姿，每段 1.2 s 五次多项式，段间停 0.3 s。
// 判据与程序相同：TCP（法兰前 0.1 m、偏 0.05 m）的最大误差；最后 0.3 s 关节速度的最大值超过 0.05 rad/s 算振荡。
// 程序的结果：名义条件 A 50 mm、B 0.19 mm；延迟 3 ms 时 B 不振荡；ω_n = 80 rad/s 时 1.3 ms 左右开始振荡；随机 24 台 B 全都不振荡，最大误差 9.7 mm。
WQ.lab({
  title: ["实验 29.2 仿真与现实", "Lab 29.2 Simulation and reality"],
  goal: ["让 WQ-CR5 在负载跑合台上做标准动作，比较两种控制器；给“现场”的机器人加上负载偏差、摩擦和延迟，看在名义仿真里好的控制器到了现场还好不好。",
         "Run the WQ-CR5's standard run-in motion with two controllers; give the “field” robot payload errors, friction and delays, and see whether a controller that looks good in the nominal simulation is still good in the field."],
  view: "physics",
  models: ["B-ARM-WQCR5"],
  scenes: [
    { id: "runin", robot: true, name: ["负载跑合台", "Load run-in stand"], hide: [],
      problem: { title: ["机器人问题：仿真里好好的，到了现场就抖", "Robot problem: fine in simulation, shaking in the field"],
                 text: ["软件组在仿真里调好的轨迹控制器，装到真机上误差大了一个数量级，有的机器人停下来手腕还在抖。差在哪里？怎样在仿真里就把现场考虑进去？",
                        "A tracking controller tuned in simulation is ten times less accurate on the real robots, and some wrists keep shaking after stopping. What differs, and how can the field be taken into account already in simulation?"] } },
    { id: "car", name: ["开车看手机", "Texting while driving"], hide: ["ctrl", "load", "fric", "Tc"], params: { wn: { value: 25 }, delay: { value: 0 } },
      problem: { title: ["生活中的例子：看手机的那一秒", "Everyday example: the second spent on the phone"],
                 text: ["开车时低头看手机，等于方向盘的“测量”晚了一点；方向盘打得越猛，车越容易左右蛇行。这里用同一台机器人、只看延迟和增益。",
                        "Looking at a phone while driving delays the steering's “measurement”; the harder you steer, the more the car weaves. Here the same robot shows the effect of delay and gain only."] } },
  ],
  params: [
    { id: "ctrl", name: ["控制器：0 = A 出厂位置环，1 = B 模型前馈 + PD", "Controller: 0 = A stock loop, 1 = B model feed-forward + PD"], min: 0, max: 1, step: 1, value: 1, unit: "", digits: 0 },
    { id: "wn", name: ["B 的固有频率 ω_n", "B's natural frequency ω_n"], min: 10, max: 120, step: 5, value: 25, unit: "rad/s", digits: 0 },
    { id: "delay", name: ["测量延迟", "Measurement delay"], min: 0, max: 5, step: 0.5, value: 0, unit: "ms", digits: 1 },
    { id: "Tc", name: ["控制周期 T_c", "Control period T_c"], min: 0.5, max: 4, step: 0.5, value: 2, unit: "ms", digits: 1 },
    { id: "load", name: ["负载倍数（现场 / 名义）", "Payload factor (field / nominal)"], min: 0.5, max: 1.5, step: 0.05, value: 1, unit: "", digits: 2 },
    { id: "fric", name: ["摩擦倍数（现场 / 名义）", "Friction factor (field / nominal)"], min: 0.5, max: 1.5, step: 0.05, value: 1, unit: "", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "random", name: ["随机一台", "Draw a robot"] }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "#d62728", name: ["TCP 误差（mm，对数坐标）", "TCP error (mm, log scale)"] }],
  physics: {
    camera: [30, 18, 0.75],
    xml(api) {
      // 画面用：执行器关掉，不推进（真正的仿真在 s.d2 里）
      return api.mjcf("wqcr5", { option: `<option timestep="0.0005" integrator="implicitfast"><flag contact="disable" actuation="disable" gravity="disable"/></option>`,
                                 tool: this.load(1) }).replace('<option integrator="implicitfast" />', "");
    },
    load(k) {              // 标准负载（wqcr5.runin_load_xml），质量、惯量乘以 k
      const m = 5 * k, a = 0.1, b = 0.1, c = 0.064;
      return `<body name="load" pos="0 0 0.09"><inertial pos="0 0 0.06" mass="${m}" diaginertia="${m / 12 * (b * b + c * c)} ${m / 12 * (a * a + c * c)} ${m / 12 * (a * a + b * b)}"/><site name="tcpL" pos="0.05 0 0.1"/><geom type="box" size="0.05 0.05 0.032" pos="0 0 0.06" rgba="0.95 0.55 0.15 1"/></body>`;
    },
  },
  KP: [2000, 2000, 1000, 300, 300, 300], KV: [400, 400, 200, 40, 40, 40], LIM: [333, 333, 167.25, 54, 54, 54],
  FC: [1.2, 1.2, 0.8, 0.4, 0.4, 0.4], FV: [2, 2, 1, 0.3, 0.3, 0.3], FSIG: [0.15, 0.15, 0.1, 0.08, 0.08, 0.08], FHI: [2, 2, 1.4, 0.8, 0.8, 0.8],
  MD: [4.267316835077498, 4.731245908768947, 2.338007759157896, 0.22881716876190686, 0.16164635133333318, 0.04854770833333309],
  POSES: [[0, -90, 90, -90, -90, 0], [90, -45, 60, -105, -90, 45], [-60, -110, 120, -100, -60, -45], [0, -90, 90, -90, -90, 0]],
  SEG: 1.2, DWELL: 0.3,
  ref(t) {
    const P = this.POSES.map((p) => p.map((x) => x * Math.PI / 180)), T = this.SEG, Dw = this.DWELL, z = [0, 0, 0, 0, 0, 0];
    t = Math.max(0, t);
    for (let k = 0; k < P.length - 1; k++) {
      const t0 = Dw + k * (T + Dw);
      if (t < t0) return { q: P[k].slice(), qd: z.slice(), qdd: z.slice() };
      if (t <= t0 + T) {
        const s = (t - t0) / T, d = P[k + 1].map((b, i) => b - P[k][i]);
        return { q: P[k].map((a, i) => a + d[i] * (10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5)),
                 qd: d.map((x) => x * (30 * s ** 2 - 60 * s ** 3 + 30 * s ** 4) / T), qdd: d.map((x) => x * (60 * s - 180 * s ** 2 + 120 * s ** 3) / T ** 2) };
      }
    }
    return { q: P[P.length - 1].slice(), qd: z.slice(), qdd: z.slice() };
  },
  TOTAL: 4.8,
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
  mulberry(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; },
  field(api, s) {                    // 现场的参数：随机抽的一台优先，否则按滑块
    const r = s.drawn;
    return r ? r : { load: api.p.load, fc: this.FC.map((x) => x * api.p.fric), fv: this.FV.map((x) => x * api.p.fric), delay: api.p.delay / 1000 };
  },
  reset(api, s) {
    const { mj, m, d } = api.sim;
    if (!this.nomLinks) {                         // 名义模型：零件库的 WQ-CR5 + 名义负载（B 的前馈用）
      const mn = mj.MjModel.from_xml_string(api.mjcf("wqcr5", { option: `<option><flag contact="disable"/></option>`, tool: this.physics.load(1) }));
      this.nomLinks = this.chainM(mn);
      mn.delete();
    }
    s.drawn = api.keep.next || null;
    const F = this.field(api, s);
    if (s.mr) { try { s.d2.delete(); s.mr.delete(); s.dref.delete(); } catch (e) { /* freed */ } }
    s.mr = mj.MjModel.from_xml_string(api.mjcf("wqcr5", { option: `<option timestep="0.0005" integrator="implicitfast"><flag contact="disable" actuation="disable" limit="disable"/></option>`,
                                                         tool: this.physics.load(F.load) }).replace('<option integrator="implicitfast" />', ""));
    for (let i = 0; i < 6; i++) { s.mr.dof_frictionloss[i] = F.fc[i]; s.mr.dof_damping[i] = F.fv[i]; }
    s.d2 = new mj.MjData(s.mr); s.dref = new mj.MjData(s.mr);
    const r0 = this.ref(0);
    for (let i = 0; i < 6; i++) { s.d2.qpos[i] = r0.q[i]; d.qpos[i] = r0.q[i]; d.qvel[i] = 0; }
    mj.mj_forward(s.mr, s.d2); mj.mj_forward(m, d);
    s.tcp = mj.mj_name2id(s.mr, 6, "tcpL");
    const nd = Math.round(F.delay / 0.0005);
    s.buf = Array.from({ length: nd + 1 }, () => [r0.q.slice(), [0, 0, 0, 0, 0, 0]]);
    s.k = 0; s.tau = [0, 0, 0, 0, 0, 0]; s.e = 0; s.vt = 0; s.hist = []; s.fin = false; s.F = F;
    const ctrl = api.scene === "car" ? 1 : Math.round(api.p.ctrl), wn = api.p.wn;
    s.ctrl = ctrl;
    s.kp = ctrl === 0 ? this.KP.slice() : this.MD.map((x) => x * wn * wn);
    s.kd = ctrl === 0 ? this.KV.slice() : this.MD.map((x) => 2 * wn * x);
    s.Tc = api.scene === "car" ? 0.002 : api.p.Tc / 1000;
  },
  action(a, api, s) {
    if (a !== "random") return;
    const rng = this.mulberry((api.keep.seed = (api.keep.seed || 2029) + 1));
    const g = () => { const u = Math.max(rng(), 1e-12), v = rng(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
    const fc = this.FC.map((x, i) => Math.min(Math.max(x + this.FSIG[i] * g(), 0), this.FHI[i]));
    const fs = this.FV.map(() => 0.5 + rng()), fv = this.FV.map((x, i) => x * fs[i]);
    api.keep.next = { load: 0.7 + 0.6 * rng(), fc, fv, delay: 0.003 * rng(), random: true };   // 按“开始”时用这一台
  },
  start(api, s) { api.keep.next = null; },     // 这一台只用一次：下次“开始”回到滑块的设置
  update(dt, api, s) {
    const { mj, m, d } = api.sim, mr = s.mr, d2 = s.d2, h = 0.0005, nc = Math.max(1, Math.round(s.Tc / h));
    if (s.fin) { api.stop(); return; }
    for (let step = 0; step < 400 && s.k * h < this.TOTAL - 1e-12; step++) {
      s.buf.push([Array.from(d2.qpos.slice(0, 6)), Array.from(d2.qvel.slice(0, 6))]); s.buf.shift();
      if (s.k % nc === 0) {
        const [q, qd] = s.buf[0], r = this.ref(s.k * h);
        let tau = r.q.map((x, i) => s.kp[i] * (x - q[i]) + s.kd[i] * (r.qd[i] - qd[i]));
        if (s.ctrl === 1) {
          const ff = this.rnea(this.nomLinks, r.q, r.qd, r.qdd).tau;
          tau = tau.map((x, i) => x + ff[i] + this.FC[i] * Math.tanh(r.qd[i] / 0.01) + this.FV[i] * r.qd[i]);
        }
        s.tau = tau.map((x, i) => Math.max(-this.LIM[i], Math.min(this.LIM[i], x)));
      }
      for (let i = 0; i < 6; i++) d2.qfrc_applied[i] = s.tau[i];
      mj.mj_step(mr, d2); s.k++;
      const v = Array.from(d2.qvel.slice(0, 6));
      if (!v.every(isFinite) || Math.max(...v.map(Math.abs)) > 100) { s.e = Infinity; s.vt = Infinity; s.k = Math.round(this.TOTAL / h); break; }
      if (s.k % 20 === 0) {
        const r = this.ref(s.k * h);
        for (let i = 0; i < 6; i++) s.dref.qpos[i] = r.q[i];
        mj.mj_kinematics(mr, s.dref);
        const a = [0, 1, 2].map((j) => d2.site_xpos[3 * s.tcp + j] - s.dref.site_xpos[3 * s.tcp + j]);
        const e = Math.hypot(...a);
        s.e = Math.max(s.e, e);
        s.hist.push([s.k * h, Math.max(e * 1000, 1e-3)]);
      }
      if (s.k * h > this.TOTAL - 0.3) s.vt = Math.max(s.vt, ...v.map(Math.abs));
    }
    for (let i = 0; i < 6; i++) { d.qpos[i] = d2.qpos[i]; d.qvel[i] = 0; }
    mj.mj_forward(m, d);
    if (s.k * h >= this.TOTAL - 1e-9 && !s.fin) {
      s.fin = true;
      const osc = !(s.vt <= 0.05), F = s.F, nominal = !F.random && Math.abs(F.load - 1) < 1e-9 && Math.abs(api.p.fric - 1) < 1e-9 && F.delay === 0 && Math.abs(s.Tc - 0.002) < 1e-9;
      if (api.scene === "runin" && nominal && s.ctrl === 0 && !osc && s.e > 0.03) api.done("nomA");
      if (api.scene === "runin" && nominal && s.ctrl === 1 && Math.abs(api.p.wn - 25) < 1e-9 && !osc && s.e < 0.001) api.done("nomB");
      if (api.scene === "runin" && s.ctrl === 1 && Math.abs(api.p.wn - 25) < 1e-9 && !F.random && F.delay >= 0.003 - 1e-9 && !osc) api.done("delay");
      if (s.ctrl === 1 && api.p.wn >= 80 - 1e-9 && !F.random && F.delay <= 0.0015 + 1e-9 && osc) api.done("hi");
      if (api.scene === "runin" && s.ctrl === 1 && Math.abs(api.p.wn - 25) < 1e-9 && F.random && !osc && s.e < 0.015) api.done("rand");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    if (!H.length) return;
    api.cplot(56, 10, w - 70, h - 34, [{ pts: H.map((r) => [r[0], Math.log10(r[1])]), color: "#d62728" }],
      { xmin: 0, xmax: this.TOTAL, ymin: -3, ymax: 2.5, xlabel: "t / s", ylabel: "lg(e / mm)" });
  },
  readouts(api, s) {
    const f = (v, k = 3) => api.fmt(v, k), F = s.F;
    if (!F) return [];
    const rows = [
      [["控制器", "Controller"], s.ctrl === 0 ? api.T("A 出厂位置环", "A stock loop") : api.T(`B 前馈 + PD，ω_n = ${f(api.p.wn, 3)} rad/s`, `B feed-forward + PD, ω_n = ${f(api.p.wn, 3)} rad/s`)],
      [["现场：负载倍数 / 延迟 / 控制周期", "Field: payload factor / delay / control period"], `${f(F.load, 3)} / ${f(F.delay * 1000, 2)} ms / ${f(s.Tc * 1000, 2)} ms`],
      [["现场：各关节的库仑摩擦", "Field: Coulomb friction of the joints"], F.fc.map((x) => f(x, 2)).join(", ") + " N·m"],
      [["TCP 的最大误差", "Largest TCP error"], isFinite(s.e) ? `${f(s.e * 1000, 3)} mm` : api.T("算飞了", "blew up")],
      [["最后 0.3 s 关节速度的最大值（> 0.05 算振荡）", "Largest joint speed in the last 0.3 s (> 0.05 means oscillating)"], s.fin ? (isFinite(s.vt) ? `${f(s.vt, 3)} rad/s` : "∞") : "…"],
    ];
    if (F.random) rows.push([["这一台是随机抽的（关节测试台的散布）", "This robot was drawn at random (test-bench spread)"], "✓"]);
    return rows;
  },
  tasks: [
    { id: "nomA", robot: true, text: ["名义条件（负载、摩擦倍数为 1，延迟 0，控制周期 2 ms）下用 A 跑一遍：TCP 误差超过 30 mm——出厂位置环没有重力补偿。", "Under nominal conditions (payload and friction factors 1, no delay, 2 ms period) run A: the TCP error exceeds 30 mm, since the stock loop has no gravity compensation."],
      demo: { scene: "runin", set: { ctrl: 0, wn: 25, delay: 0, Tc: 2, load: 1, fric: 1 }, wait: 8 } },
    { id: "nomB", robot: true, text: ["同样的名义条件用 B（ω_n = 25 rad/s）：TCP 误差不到 1 mm。", "Same nominal conditions with B (ω_n = 25 rad/s): the TCP error is below 1 mm."],
      demo: { scene: "runin", set: { ctrl: 1, wn: 25, delay: 0, Tc: 2, load: 1, fric: 1 }, wait: 8 } },
    { id: "delay", robot: true, text: ["用 B（ω_n = 25 rad/s），把测量延迟加到 3 ms 或更多：仍然不振荡，误差变大多少？", "With B (ω_n = 25 rad/s) raise the measurement delay to 3 ms or more: it still does not oscillate; how much larger is the error?"],
      demo: { scene: "runin", set: { ctrl: 1, wn: 25, delay: 3, Tc: 2, load: 1, fric: 1 }, wait: 8 } },
    { id: "hi", robot: true, text: ["把 ω_n 提高到 80 rad/s（名义上误差更小）：延迟只要 1.5 ms 或更少就振荡。", "Raise ω_n to 80 rad/s (more accurate on paper): a delay of 1.5 ms or less is enough to make it oscillate."],
      demo: { scene: "car", set: { wn: 80, delay: 1.5 }, wait: 8 } },
    { id: "rand", robot: true, text: ["用 B（ω_n = 25 rad/s），按“随机一台”再按“开始”：这台机器人不振荡，TCP 误差小于 15 mm。", "With B (ω_n = 25 rad/s) press “Draw a robot” and then Start: it does not oscillate and the TCP error is below 15 mm."],
      demo: { scene: "runin", set: { ctrl: 1, wn: 25, delay: 0, Tc: 2, load: 1, fric: 1 }, press: ["random", "start"], wait: 8 } },
  ],
  think: ["在名义仿真里，ω_n = 80 rad/s 的控制器误差最小；到了“现场”它却最先振荡。在一个只有名义模型、没有延迟的仿真里调出来的控制器，你会怎样检查它能不能上真机？",
          "In the nominal simulation the 80 rad/s controller is the most accurate, yet in the “field” it is the first to oscillate. How would you check a controller tuned in a nominal, delay-free simulation before it goes onto a real robot?"],
});
