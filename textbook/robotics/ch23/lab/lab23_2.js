// 实验 23.2 复摆与平行轴定理（配 23.2 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex23_2.py 同一版本。
// 场景 1（生活）：长 1 m 的均匀米尺（0.15 kg，示意值）挂在离中点 d 处的钉子上（水平铰链，无摩擦），从 θ₀ 释放。
// 场景 2（机器人）：UR5e 关节 3 的刹车松开，小臂绕关节 3 轴摆动。质量、质心、惯量取自书中的 UR5e 模型（正则读出 forearm_link 的 <inertial>）；
//   电机转子惯量（armature）不计；末端（距轴 0.392 m）可挂一个质点负载。
// 周期由角速度相邻两次变号的间隔求得（取最近几次的平均）。预测：小幅 T₀ = 2π √(J_o/(m𝔤d))（式 (23.2.6)），
//   振幅 θ₀ 的精确值 T = T₀ · (2/π) K(sin²(θ₀/2))（K 用算术-几何平均计算）。
// 阈值由 ex23_2.py 用 Python 版 MuJoCo 核算：5° 时测得的周期比小幅公式只长 0.048%（任务取 0.5%）；小臂 T₀ = 1.0345 s；
// 末端加 1 kg 时 T₀ = 1.1435 s；米尺 d = k = 28.87 cm 时周期最短 1.524 s。
WQ.lab({
  title: ["实验 23.2 复摆与平行轴定理", "Lab 23.2 The physical pendulum and the parallel-axis theorem"],
  goal: ["测量刚体绕不同悬挂点摆动的周期，用平行轴定理预测它，找出周期最短的悬挂点。",
         "Measure the period of a body swinging about different pivots, predict it with the parallel-axis theorem, and find the pivot with the shortest period."],
  view: "physics",
  scenes: [
    { id: "stick", name: ["钉子上的米尺", "A metre stick on a nail"], hide: ["load"],
      problem: { title: ["生活中的例子：米尺挂在哪里摆得最快", "Everyday example: where should a metre stick hang to swing fastest"],
                 text: ["一根 1 m 的米尺上钻了一排孔，挂在钉子上摆动。挂在一端、挂在靠近中点的地方，哪一种摆得快？",
                        "A metre stick with a row of holes swings on a nail. Does it swing faster hung at one end or near the middle?"] } },
    { id: "forearm", robot: true, name: ["UR5e 小臂", "UR5e forearm"], hide: ["d"],
      problem: { title: ["机器人问题：刹车松开后小臂怎样摆", "Robot problem: how does the forearm swing once the brake is released"],
                 text: ["关节 3 的刹车松开，小臂在重力下绕关节 3 轴摆动。摆动的周期由什么决定？末端挂了负载又会怎样？",
                        "With the joint-3 brake released the forearm swings about joint 3 under gravity. What sets the period, and what does a payload at the end change?"] } },
  ],
  params: [
    { id: "d", name: ["悬挂点离中点的距离 d", "Pivot distance d from the centre"], min: 2, max: 50, step: 0.5, value: 50, unit: "cm", digits: 1 },
    { id: "amp", name: ["释放角 θ₀", "Release angle θ₀"], min: 2, max: 60, step: 1, value: 5, unit: "°", digits: 0 },
    { id: "load", name: ["末端负载", "Payload at the end"], min: 0, max: 2, step: 0.1, value: 0, unit: "kg", digits: 1 },
  ],
  legend: [{ color: "#1f77b4", name: ["摆角 θ", "angle θ"] }],
  physics: {
    camera: [0, 5, 0.6],
    fa(api) {                                     // 书中 UR5e 模型的小臂 <inertial>
      const t = api.mjcf("ur5e");
      const m = t.match(/name="forearm_link"[^>]*>\s*<inertial mass="([\d.]+)" pos="0 0 ([\d.]+)" diaginertia="([\d.e-]+) ([\d.e-]+) ([\d.e-]+)"/);
      return { m: +m[1], d: +m[2], It: +m[3], Ia: +m[5] };
    },
    xml(api) {
      const G = 9.81;
      let body;
      if (api.scene === "stick") {
        const d = api.p.d / 100, m = 0.15, I = m * 1.0 / 12;
        body = `<inertial pos="0 0 ${-d}" mass="${m}" diaginertia="${I} ${I} 1e-6"/>
<geom type="box" size="0.015 0.003 0.5" pos="0 0 ${-d}" rgba="0.93 0.78 0.35 1" contype="0" conaffinity="0"/>`;
      } else {
        const f = this.fa(api);
        body = `<inertial pos="0 0 ${-f.d}" mass="${f.m}" diaginertia="${f.It} ${f.It} ${f.Ia}"/>
<geom type="capsule" fromto="0 0 0 0 0 -0.392" size="0.038" rgba="0.72 0.80 0.86 1" contype="0" conaffinity="0"/>
${api.p.load > 0 ? `<body pos="0 0 -0.392"><inertial pos="0 0 0" mass="${api.p.load}" diaginertia="1e-9 1e-9 1e-9"/><geom type="sphere" size="0.045" rgba="0.85 0.55 0.15 1" contype="0" conaffinity="0"/></body>` : ""}`;
      }
      return `<mujoco><option timestep="0.0005" integrator="RK4" gravity="0 0 -${G}"/><worldbody>
<geom type="cylinder" size="0.012 0.04" pos="0 0 1" quat="0.7071068 0.7071068 0 0" rgba="0.3 0.3 0.32 1" contype="0" conaffinity="0"/>
<body name="pend" pos="0 0 1"><joint name="pivot" type="hinge" axis="0 1 0"/>${body}</body></worldbody></mujoco>`;
    },
  },
  props(api) {                                    // 质量、质心距离、对轴的转动惯量（平行轴定理）
    if (api.scene === "stick") {
      const d = api.p.d / 100, m = 0.15;
      return { m, d, J: m / 12 + m * d * d };
    }
    const f = this.physics.fa(api), mL = api.p.load, L = 0.392;
    const m = f.m + mL, d = (f.m * f.d + mL * L) / m;
    return { m, d, J: f.It + f.m * f.d * f.d + mL * L * L };
  },
  ellipK(m) {                                     // K(m) = π / (2 AGM(1, √(1 − m)))
    let a = 1, b = Math.sqrt(1 - m);
    for (let i = 0; i < 30; i++) { const a1 = (a + b) / 2; b = Math.sqrt(a * b); a = a1; }
    return Math.PI / (2 * a);
  },
  reset(api, s) {
    api.sim.d.qpos[0] = api.p.amp * Math.PI / 180;
    s.cross = []; s.prev = 0; s.tprev = 0; s.hist = []; s.T = null;
    const p = this.props(api);
    s.T0 = 2 * Math.PI * Math.sqrt(p.J / (p.m * 9.81 * p.d));
    s.Texact = s.T0 * 2 / Math.PI * this.ellipK(Math.sin(api.p.amp * Math.PI / 360) ** 2);
  },
  update(dt, api, s) {
    const d = api.sim.d, w = d.qvel[0];
    if (s.prev !== 0 && Math.sign(w) !== Math.sign(s.prev) && w !== 0) {
      // 两帧之间线性插值求变号的时刻：角速度在变号处是正弦曲线的拐点，线性插值很准
      s.cross.push(s.tprev + (d.time - s.tprev) * s.prev / (s.prev - w));
      const c = s.cross;
      if (c.length >= 3) s.T = 2 * (c[c.length - 1] - c[Math.max(0, c.length - 5)]) / (Math.min(c.length, 5) - 1);
    }
    s.prev = w; s.tprev = d.time;
    s.hist.push([d.time, d.qpos[0] * 180 / Math.PI]);
    if (s.hist.length > 4000) s.hist.shift();
    if (s.T && s.cross.length >= 4) {
      const err = Math.abs(s.T / s.T0 - 1);
      if (api.scene === "stick") {
        if (api.p.d === 50 && api.p.amp <= 5 && err < 0.005) api.done("end");
        if (api.p.d >= 28 && api.p.d <= 29.5 && err < 0.005) api.done("best");
      } else {
        if (api.p.load === 0 && api.p.amp <= 5 && err < 0.005) api.done("forearm");
        if (api.p.load >= 1 && api.p.amp <= 5 && err < 0.005) api.done("load");
      }
    }
    if (d.time >= 12) api.stop();
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    const t1 = H.length ? Math.max(6, H[H.length - 1][0]) : 6, A = api.p.amp * 1.15;
    api.cplot(48, 10, w - 60, h - 34, [{ pts: H.filter((_, n) => n % 8 === 0).map((r) => [r[0], r[1]]), color: "#1f77b4" }],
      { xmin: Math.max(0, t1 - 6), xmax: t1, ymin: -A, ymax: A, xlabel: "t / s", ylabel: "θ / (°)" });
  },
  readouts(api, s) {
    if (!api.sim) return [];
    const p = this.props(api);
    return [
      [["质量 m、质心到轴的距离 d", "Mass m, distance d of the CoM"], `${api.fmt(p.m, 3)} kg, ${api.fmt(p.d, 4)} m`],
      [["对轴的转动惯量 J_o（平行轴定理）", "Moment of inertia J_o about the axis"], api.fmt(p.J, 5) + " kg·m²"],
      [["小幅周期的预测 T₀", "Small-angle prediction T₀"], api.fmt(s.T0 || 0, 4) + " s"],
      [["考虑振幅的精确周期", "Exact period for this amplitude"], api.fmt(s.Texact || 0, 4) + " s"],
      [["测得的周期", "Measured period"], s.T ? api.fmt(s.T, 4) + " s" : "—"],
    ];
  },
  tasks: [
    { id: "end", text: ["米尺挂在一端（d = 50 cm），释放角不大于 5°：测得的周期与小幅预测相差不到 0.5%。", "Hang the stick at one end (d = 50 cm) and release it from at most 5°: the measured period agrees with the small-angle prediction within 0.5 %."],
      demo: { scene: "stick", set: { d: 50, amp: 5 }, wait: 6 } },
    { id: "best", text: ["找出周期最短的悬挂点（在 28～29.5 cm 之间），并测出周期。", "Find the pivot with the shortest period (between 28 and 29.5 cm) and measure the period."],
      demo: { scene: "stick", set: { d: 29, amp: 5 }, wait: 6 } },
    { id: "forearm", robot: true, text: ["小臂不挂负载、小幅摆动：测得的周期与平行轴定理的预测相差不到 0.5%。", "Forearm without payload, small swing: the measured period agrees with the parallel-axis prediction within 0.5 %."],
      demo: { scene: "forearm", set: { load: 0, amp: 5 }, wait: 6 } },
    { id: "load", robot: true, text: ["小臂末端挂 1 kg 以上的负载：周期变长，仍与预测相差不到 0.5%。", "With at least 1 kg at the end the period grows, still within 0.5 % of the prediction."],
      demo: { scene: "forearm", set: { load: 1, amp: 5 }, wait: 6 } },
  ],
  think: ["米尺挂在离中点 d = 20 cm 处，和挂在中点另一侧多远处周期相同？做一次验证（定理 23.2.3）。", "With the stick hung 20 cm from the centre, at what distance on the other side is the period the same? Check it (Theorem 23.2.3)."],
});
