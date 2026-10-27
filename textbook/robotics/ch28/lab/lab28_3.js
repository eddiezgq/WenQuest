// 实验 28.3 四旋翼的推力、力矩与配平（配 28.3 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex28_3.py 同一版本。
// 模型：书中的 X2（textbook/robotics/models/mjcf/x2.xml，由 MuJoCo Menagerie skydio_x2 生成）：质量 1.325 kg，四个推力执行器 0～13 N，
//   反扭矩系数 0.0201 m；x2.xml 带空气阻力（density = 1.225，惯量模型，式 (28.3.5)）。起始悬停在 1.5 m 高处。
// 两种操纵方式：
//   手动（hold = 0）：给总推力 f 和横滚力矩 m_x（m_y = m_z = 0），由推力分配矩阵（式 (21.1.6)）求四个推力。
//   姿态保持（hold = 1）：给俯仰角 θ*（低头为正），控制器保持横滚、偏航为零、俯仰为 θ*，并用总推力保持 1.5 m 的高度：
//     力矩 m_b = −K_R e_R − K_ω ω_b + ω_b × I_b ω_b（e_R 为 SO(3) 上的姿态误差，K_R = 225 I_b、K_ω = 27 I_b），
//     总推力 f = m(𝔤 + 4(1.5 − z) − 3ż)/R₃₃。四个推力截断在 0～13 N。
// 风：MuJoCo 的 opt.wind，风速 w 从机头方向吹来（wind = (−w, 0, 0)），在 reset 中直接写入模型的 opt.wind（不必重新编译模型）。本页自己逐步推进，比实时快 3 倍，每次 20 s。
// 由 ex28_3.py 与本页的流程在 Python 中核算：θ* = 11.03° 时平飞速度趋于 9.98 m/s；逆风 5 m/s、θ* = 2.79° 时悬停不动；
//   手动给 m_x 时第一步的角加速度与 I_b⁻¹ m_b 相同（含惯量积引起的偏航）。
WQ.lab({
  title: ["实验 28.3 四旋翼的推力、力矩与配平", "Lab 28.3 Quadrotor thrust, torque and trim"],
  goal: ["给 X2 四旋翼不同的推力和力矩，测出角加速度；再让它保持姿态平飞或在风中悬停，看空气阻力要求机身倾斜多少。",
         "Give the X2 quadrotor different thrusts and torques and measure its angular acceleration; then hold its attitude in level flight or in wind and see how much the body must tilt against drag."],
  view: "physics",
  models: ["B-UAV-X2"],
  scenes: [
    { id: "fly", robot: true, name: ["X2 巡检飞行", "X2 inspection flight"],
      problem: { title: ["机器人问题：巡检时 X2 要低头多少才能以 10 m/s 飞", "Robot problem: how far must X2 pitch down to fly at 10 m/s"],
                 text: ["第 21 章说不计阻力时平飞机身是平的。真实的空气有阻力，机身要低头多少？横滚、偏航各能多快？",
                        "Chapter 21 said the body is level in steady flight if drag is ignored. With real air, how far must it pitch? How fast can it roll and yaw?"] } },
    { id: "wind", name: ["生活：遥控飞机逆风悬停", "Everyday: hovering a toy drone in a headwind"], params: { hold: { value: 1 }, wind: { value: 5 }, theta: { value: 0 } },
      problem: { title: ["生活中的例子：有风的时候，飞机怎样停在原地", "Everyday example: how a drone stays put in the wind"],
                 text: ["风从前面吹来，飞机会被吹着往后退。要停在原地，机身应该朝哪边倾斜、倾斜多少？",
                        "The wind blows from the front and pushes the drone back. To stay put, which way and how far must the body tilt?"] } },
  ],
  params: [
    { id: "hold", name: ["姿态保持（0 手动，1 保持）", "Attitude hold (0 manual, 1 hold)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "f", name: ["总推力 f（手动）", "Total thrust f (manual)"], min: 0, max: 30, step: 0.05, value: 12.0, unit: "N", digits: 2 },
    { id: "mx", name: ["横滚力矩 m_x（手动）", "Roll torque m_x (manual)"], min: -1, max: 1, step: 0.01, value: 0, unit: "N·m", digits: 2 },
    { id: "theta", name: ["俯仰角 θ*（保持，低头为正）", "Pitch θ* (hold, nose down positive)"], min: -20, max: 30, step: 0.01, value: 0, unit: "°", digits: 2 },
    { id: "wind", name: ["迎面风速", "Headwind speed"], min: 0, max: 10, step: 0.5, value: 0, unit: "m/s", digits: 1 },
  ],
  legend: [{ color: "#1f77b4", name: ["前进速度 v_x", "forward speed v_x"] }, { color: "#d62728", name: ["高度 z − 1.5 m（×10）", "height z − 1.5 m (×10)"] }],
  physics: {
    camera: [-60, 15, 0.7],
    rate: 1e-9,                                   // 本页自己逐步推进
    DT: 0.01, G: 9.81, Z0: 1.5, SPEED: 3, TE: 20,
    xml(api) { return api.mjcf("x2"); },          // 风不写进模型（改风速不必重新编译模型），在 reset 里设 m.opt.wind
  },
  P: {                                            // X2 的参数：与 ex28_3.py 由 x2.xml 读出的相同
    m: 1.325,
    I: [[0.03665169811320774, 0, -0.0021000000000001703], [0, 0.025411698113207672, 0], [-0.0021000000000001703, 0, 0.060528]],
    r: [[-0.14, -0.18, -0.003962264150943405], [-0.14, 0.18, -0.003962264150943405], [0.14, 0.18, 0.026037735849056597], [0.14, -0.18, 0.026037735849056597]],
    sig: [-1, 1, -1, 1], c: 0.0201,
  },
  mat3: {
    mul: (A, v) => [0, 1, 2].map((i) => A[i][0] * v[0] + A[i][1] * v[1] + A[i][2] * v[2]),
    cross: (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]],
    inv: (A) => { const [a, b, c] = A[0], [d, e, f] = A[1], [g, h, i] = A[2], D = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
      return [[(e * i - f * h) / D, (c * h - b * i) / D, (b * f - c * e) / D], [(f * g - d * i) / D, (a * i - c * g) / D, (c * d - a * f) / D], [(d * h - e * g) / D, (b * g - a * h) / D, (a * e - b * d) / D]]; },
  },
  alloc() {                                       // (f, m_x, m_y, m_z) = A (f_1..f_4)，返回 A 的逆（4×4，用高斯消元）
    if (this._Ai) return this._Ai;
    const P = this.P, A = [[1, 1, 1, 1], [], [], []];
    for (let i = 0; i < 4; i++) { const r = P.r[i]; A[1][i] = r[1]; A[2][i] = -r[0]; A[3][i] = P.sig[i] * P.c; }
    const n = 4, M = A.map((row, i) => [...row, ...[0, 1, 2, 3].map((j) => (i === j ? 1 : 0))]);
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      [M[c], M[p]] = [M[p], M[c]];
      const v = M[c][c]; for (let k = 0; k < 2 * n; k++) M[c][k] /= v;
      for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c]; for (let k = 0; k < 2 * n; k++) M[r][k] -= f * M[c][k]; }
    }
    this._Ai = M.map((row) => row.slice(n));
    return this._Ai;
  },
  reset(api, s) {
    const { mj, m, d } = api.sim, ph = this.physics;
    d.qpos[0] = 0; d.qpos[1] = 0; d.qpos[2] = ph.Z0; d.qpos[3] = 1; d.qpos[4] = 0; d.qpos[5] = 0; d.qpos[6] = 0;
    for (let i = 0; i < 6; i++) d.qvel[i] = 0;
    const wv = m.opt.wind; wv[0] = -api.p.wind; wv[1] = 0; wv[2] = 0;
    mj.mj_forward(m, d);
    s.t = 0; s.hist = []; s.acc0 = null; s.fin = false; s.fi = [0, 0, 0, 0]; s.vxs = []; s.zds = [];
    s.lastView = -1;
    this.control(api, s);                         // 先给好推力：页面开始时可能先走一步
  },
  quatR(q) {
    const [w, x, y, z] = q;
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]];
  },
  control(api, s) {
    const d = api.sim.d, P = this.P, M3 = this.mat3, G = this.physics.G;
    let f, mb;
    if (api.p.hold < 0.5) { f = api.p.f; mb = [api.p.mx, 0, 0]; }
    else {
      const R = this.quatR([d.qpos[3], d.qpos[4], d.qpos[5], d.qpos[6]]), w = [d.qvel[3], d.qvel[4], d.qvel[5]];
      const th = api.p.theta * Math.PI / 180, c = Math.cos(th), sn = Math.sin(th);
      const Rd = [[c, 0, sn], [0, 1, 0], [-sn, 0, c]];
      const E = [0, 1, 2].map((i) => [0, 1, 2].map((j) => { let a = 0, b = 0; for (let k = 0; k < 3; k++) { a += Rd[k][i] * R[k][j]; b += R[k][i] * Rd[k][j]; } return 0.5 * (a - b); }));
      const eR = [E[2][1], E[0][2], E[1][0]];
      const Ie = M3.mul(P.I, eR), Iw = M3.mul(P.I, w), gy = M3.cross(w, Iw);
      mb = [0, 1, 2].map((i) => -225 * Ie[i] - 27 * Iw[i] + gy[i]);
      const z = d.qpos[2], zd = d.qvel[2];
      f = P.m * (G + 4 * (this.physics.Z0 - z) - 3 * zd) / Math.max(R[2][2], 0.5);
    }
    const Ai = this.alloc(), u = [f, ...mb];
    s.fi = [0, 1, 2, 3].map((i) => Math.min(13, Math.max(0, Ai[i][0] * u[0] + Ai[i][1] * u[1] + Ai[i][2] * u[2] + Ai[i][3] * u[3])));
    for (let i = 0; i < 4; i++) d.ctrl[i] = s.fi[i];
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim, ph = this.physics;
    if (s.fin) { api.stop(); return; }
    const n = Math.max(1, Math.round(dt * ph.SPEED / ph.DT));
    for (let k = 0; k < n && !s.fin; k++) {
      this.control(api, s);
      mj.mj_step(m, d);
      s.t += ph.DT;
      if (s.acc0 === null) s.acc0 = [d.qacc[3], d.qacc[4], d.qacc[5]];      // 第一步：由静止悬停开始的角加速度
      if (s.t > ph.TE - 2) { s.vxs.push(d.qvel[0]); s.zds.push(Math.abs(d.qvel[2])); }
      s.hist.push([s.t, d.qvel[0], (d.qpos[2] - ph.Z0) * 10]);
      if (s.t >= ph.TE || d.qpos[2] < 0 || Math.abs(d.qpos[0]) > 1000) s.fin = true;
      if (api.p.hold < 0.5 && Math.abs(api.p.mx) > 1e-9 && s.t >= 1.0) s.fin = true;   // 手动横滚：1 s 后停止（已经翻了好几圈）
      if (api.p.hold < 0.5 && Math.abs(api.p.mx) < 1e-9 && s.t >= 3.0) s.fin = true;
    }
    if (s.t - s.lastView > 0.5) { api.view(-60, 15, 0.55); s.lastView = s.t; }
    if (s.fin) {
      const p = api.p, mean = (a) => a.reduce((x, y) => x + y, 0) / Math.max(a.length, 1);
      if (p.hold < 0.5 && Math.abs(p.mx) < 1e-9 && Math.abs(d.qvel[2]) < 0.05 && Math.abs(d.qpos[2] - ph.Z0) < 0.1 && s.t >= 3) api.done("hover");
      if (p.hold < 0.5 && Math.abs(p.mx) >= 0.2 && s.acc0) {
        const pred = this.mat3.mul(this.mat3.inv(this.P.I), [p.mx, 0, 0]);
        if (Math.abs(s.acc0[0] / pred[0] - 1) < 0.02) api.done("roll");
      }
      const vx = mean(s.vxs);
      if (p.hold > 0.5 && p.wind === 0 && s.t >= ph.TE && vx >= 9.5 && vx <= 10.5 && mean(s.zds) < 0.1) api.done("cruise");
      if (p.hold > 0.5 && p.wind >= 4.99 && s.t >= ph.TE && Math.abs(vx) < 0.1) api.done("wind");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    api.cplot(48, 10, w - 60, h - 34, [{ pts: H.map((r) => [r[0], r[1]]), color: "#1f77b4" }, { pts: H.map((r) => [r[0], r[2]]), color: "#d62728" }],
      { xmin: 0, xmax: this.physics.TE, ymin: -3, ymax: 12, xlabel: "t / s", ylabel: "m/s" });
  },
  readouts(api, s) {
    const f = (v, k = 3) => api.fmt(v, k), d = api.sim ? api.sim.d : null;
    if (!d) return [];
    const R = this.quatR([d.qpos[3], d.qpos[4], d.qpos[5], d.qpos[6]]);
    const pitch = Math.atan2(R[0][2], R[2][2]) * 180 / Math.PI;      // 低头为正
    const pred = this.mat3.mul(this.mat3.inv(this.P.I), [api.p.mx, 0, 0]);
    const a0 = s.acc0 || [0, 0, 0];
    return [
      [["四个推力", "The four thrusts"], (s.fi || []).map((x) => f(x, 3)).join(", ") + " N"],
      [["前进速度 v_x、高度 z", "Forward speed v_x, height z"], `${f(d.qvel[0], 2)} m/s，${f(d.qpos[2], 3)} m`],
      [["机身俯仰角（低头为正）", "Body pitch (nose down positive)"], f(pitch, 2) + "°"],
      [["起始的角加速度 ω̇_x、ω̇_z（实测）", "Initial angular acceleration ω̇_x, ω̇_z (measured)"], `${f(a0[0], 2)}，${f(a0[2], 2)} rad/s²`],
      [["m_x/I_xx 与 I_b⁻¹m_b 的 x、z 分量", "m_x/I_xx and the x, z parts of I_b⁻¹m_b"], `${f(api.p.mx / this.P.I[0][0], 2)}；${f(pred[0], 2)}，${f(pred[2], 2)} rad/s²`],
      [["悬停所需的总推力 m𝔤", "Thrust to hover m𝔤"], f(this.P.m * this.physics.G, 3) + " N"],
    ];
  },
  tasks: [
    { id: "hover", robot: true, text: ["手动：横滚力矩为零，调总推力使 X2 悬停（3 s 后竖直速度小于 0.05 m/s）。", "Manual: zero roll torque; set the total thrust so that X2 hovers (vertical speed below 0.05 m/s after 3 s)."],
      demo: { scene: "fly", set: { hold: 0, f: 13.0, mx: 0, theta: 0, wind: 0 }, wait: 3 } },
    { id: "roll", robot: true, text: ["手动：给一个横滚力矩（|m_x| ≥ 0.2 N·m），测出起始的角加速度，与 I_b⁻¹m_b 相差不到 2%。比较它与 m_x/I_xx，并看偏航的角加速度。",
                                     "Manual: apply a roll torque (|m_x| ≥ 0.2 N·m) and measure the initial angular acceleration; it should match I_b⁻¹m_b within 2%. Compare it with m_x/I_xx and look at the yaw acceleration."],
      demo: { scene: "fly", set: { hold: 0, f: 13.0, mx: 0.5, theta: 0, wind: 0 }, wait: 2 } },
    { id: "cruise", robot: true, text: ["姿态保持：调俯仰角，使 X2 保持高度、以 9.5～10.5 m/s 平飞，读出所需的俯仰角（式 (28.3.6)）。",
                                       "Attitude hold: choose the pitch so that X2 holds its height and flies level at 9.5–10.5 m/s; read the pitch needed (Eq. (28.3.6))."],
      demo: { scene: "fly", set: { hold: 1, f: 13.0, mx: 0, theta: 11.03, wind: 0 }, wait: 9 } },
    { id: "wind", text: ["逆风 5 m/s：调俯仰角，使飞机停在原地（最后 2 s 的平均速度小于 0.1 m/s）。", "Headwind of 5 m/s: choose the pitch so that the drone stays put (mean speed below 0.1 m/s over the last 2 s)."],
      demo: { scene: "wind", set: { hold: 1, f: 13.0, mx: 0, theta: 2.79, wind: 5 }, wait: 9 } },
  ],
  think: ["真实四旋翼的阻力中有很大一部分来自旋翼（前飞时桨盘后倾），它大致与速度成正比，而 MuJoCo 的模型只有与速度平方成正比的机身阻力。如果改用与速度成正比的阻力，低速时所需的倾角会变大还是变小？",
          "Much of a real quadrotor's drag comes from the rotors (the discs tilt back in forward flight) and is roughly proportional to speed, whereas MuJoCo models only body drag proportional to the square of speed. With drag proportional to speed, would the tilt needed at low speed be larger or smaller?"],
});
