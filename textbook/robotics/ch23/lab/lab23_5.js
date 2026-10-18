// 实验 23.5 UR5e 的质心、惯量与角动量守恒（配 23.5 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex23_5.py 同一版本。
// 模型是书中的网页版 UR5e（MuJoCo Menagerie，去掉网格，质量、惯量与原版相同），外观用零件库 glTF（B-ARM-UR5E）。
// 测量区按 23.5 节的方法，用 MuJoCo 给出的各连杆质心 xipos、惯量主轴 ximat 和主惯量 body_inertia 算出整臂（不含固定的基座）的
// 质量、质心、绕关节 1 轴的转动惯量 I_zz = Σ [(R I Rᵀ)_zz + m(x² + y²)]；同时显示 MuJoCo 质量矩阵的 M₁₁（d.M[dof_Madr[0]]）减去电机转子惯量。
// 场景 1（机器人，静止）：拖滑块摆姿态 θ = (0, θ₂, θ₃, 0, 0, 0)，法兰上可装负载：夹爪 + SH-301 毛坯（算例 23.2.2）按质量等比缩放，
//   3.8 kg 时与算例 23.5.3 相同。
// 场景 2（机器人，动态）：关节 1 的执行器增益设为零、电机转子惯量设为零、取消转角限位，以 1 rad/s 转动；其余关节位置伺服，
//   1 s 后用 3 s 把小臂从 θ₃ = 0 平滑地折到 150°（θ₄ = −90°）。角动量守恒：θ̇₁ 之比 = I_zz 之比（式 (23.5.4)）。
// 场景 3（生活）：转椅上的人（示意值）：椅子与躯干 61 kg，两臂各 3.5 kg、手持 2 kg 哑铃，从平伸放到身体两侧（伺服），转椅无摩擦。
// 阈值由 ex23_5.py 用 Python 版 MuJoCo 核算：零位 I_zz = 3.3981 kg·m²；大臂竖直时 0.2425；装 3.8 kg 负载后零位 6.5542（+93%）；
// 收臂：θ̇₁ 从 1 变为 3.967 rad/s，I_zz 之比 3.970，相差 0.07%（任务取 1%）；转椅：转速之比与 I_zz 之比相差 < 10⁻⁶。
WQ.lab({
  title: ["实验 23.5 UR5e 的质心、惯量与角动量守恒", "Lab 23.5 Centre of mass, inertia and conservation of angular momentum of the UR5e"],
  goal: ["由模型的惯性参数算出 UR5e 整臂的质心和绕关节 1 轴的转动惯量，看它们怎样随姿态和负载变化；关节 1 不出力时收臂，验证角动量守恒。",
         "From the model's inertial parameters compute the UR5e's centre of mass and its inertia about joint 1, see how they change with pose and payload, and check conservation of angular momentum when the arm folds with joint 1 free."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "hold", robot: true, name: ["摆姿态、读惯量", "Pose and inertia"], hide: [],
      problem: { title: ["机器人问题：关节 1 推的是多大的惯量", "Robot problem: how much inertia does joint 1 drive"],
                 text: ["关节 1 带着整条手臂绕竖直轴转。手臂伸直、收拢、举着工件时，它要推动的转动惯量差多少？",
                        "Joint 1 swings the whole arm about the vertical axis. How different is the inertia it drives with the arm stretched, folded, or holding a part?"] } },
    { id: "spin", robot: true, name: ["关节 1 自由转动时收臂", "Folding with joint 1 free"], hide: ["q2", "q3", "load"],
      problem: { title: ["机器人问题：关节 1 不出力，收臂会怎样", "Robot problem: what happens if the arm folds while joint 1 is free"],
                 text: ["关节 1 断电、刹车也松开，手臂还在绕竖直轴转。这时把小臂折起来，关节 1 会转得更快还是更慢？快多少？",
                        "Joint 1 is unpowered with its brake released and the arm still turns about the vertical. If the forearm now folds, does joint 1 speed up or slow down, and by how much?"] } },
    { id: "chair", name: ["转椅上收臂", "Arms in on a swivel chair"], hide: ["q2", "q3", "load"],
      problem: { title: ["生活中的例子：花样滑冰的收臂加速", "Everyday example: the skater's spin-up"],
                 text: ["坐在转椅上，两手各握一个哑铃平伸，让人推一下，再把手臂放下来贴着身体。转速怎样变？",
                        "Sit on a swivel chair holding dumbbells at arm's length, get a push, then drop your arms to your sides. How does the spin change?"] } },
  ],
  params: [
    { id: "q2", name: ["关节 2 角 θ₂（肩）", "Joint 2 angle θ₂ (shoulder)"], min: -180, max: 0, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "q3", name: ["关节 3 角 θ₃（肘）", "Joint 3 angle θ₃ (elbow)"], min: -160, max: 160, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "load", name: ["法兰上的负载（夹爪 + 毛坯）", "Payload on the flange (gripper + blank)"], min: 0, max: 5, step: 0.1, value: 0, unit: "kg", digits: 1 },
  ],
  legend: [{ color: "#1f77b4", name: ["关节 1（转椅）的角速度", "joint 1 (chair) speed"] }, { color: "#d62728", name: ["由 I_zz 之比预测的终值", "final value predicted from the I_zz ratio"] }],
  physics: {
    camera: [30, 18, 0.75],
    payload(load) {                               // 算例 23.2.2 的组合体按质量缩放：质心在法兰外 0.1611 m（工具方向 y）
      const k = load / 3.8, I = [0.0260338 * k, 0.0017083 * k, 0.0262671 * k];
      return `<body name="payload" pos="0 0.1 0"><inertial pos="0 0.16114 0" mass="${Math.max(load, 1e-6)}" diaginertia="${Math.max(I[0], 1e-9)} ${Math.max(I[1], 1e-9)} ${Math.max(I[2], 1e-9)}"/>
<geom type="box" pos="0 0.05 0" size="0.04 0.05 0.03" rgba="0.36 0.42 0.45 1" mass="0" contype="0" conaffinity="0"/>
<geom type="cylinder" pos="0 0.2008 0" quat="0.7071068 0.7071068 0 0" size="0.025 0.0908" rgba="0.62 0.55 0.35 1" mass="0" contype="0" conaffinity="0"/></body>`;
    },
    xml(api) {
      if (api.scene === "chair") {
        const arm = (sg) => `<body name="arm${sg > 0 ? "L" : "R"}" pos="0 ${sg * 0.2} 1.15"><joint name="sh${sg > 0 ? "L" : "R"}" type="hinge" axis="${sg > 0 ? 1 : -1} 0 0" range="-1.6 0.2"/>
<geom type="capsule" fromto="0 0 0 0 ${sg * 0.6} 0" size="0.04" mass="3.5" rgba="0.95 0.8 0.65 1" contype="0" conaffinity="0"/>
<geom type="sphere" size="0.06" pos="0 ${sg * 0.62} 0" mass="2" rgba="0.3 0.3 0.32 1" contype="0" conaffinity="0"/></body>`;
        return `<mujoco><compiler angle="radian"/><option timestep="0.001" integrator="RK4"/><worldbody>
<geom type="cylinder" size="0.04 0.24" pos="0 0 0.24" rgba="0.3 0.3 0.32 1" contype="0" conaffinity="0"/>
<body name="chair"><joint name="swivel" type="hinge" axis="0 0 1"/>
<geom type="cylinder" size="0.22 0.03" pos="0 0 0.5" mass="6" rgba="0.2 0.35 0.6 1" contype="0" conaffinity="0"/>
<geom type="cylinder" size="0.15 0.35" pos="0 0 0.85" mass="50" rgba="0.25 0.5 0.75 1" contype="0" conaffinity="0"/>
<geom type="sphere" size="0.11" pos="0 0 1.33" mass="5" rgba="0.95 0.8 0.65 1" contype="0" conaffinity="0"/>
<geom type="box" size="0.02 0.02 0.03" pos="0.15 0 1.0" mass="0" rgba="0.85 0.55 0.15 1" contype="0" conaffinity="0"/>
${arm(1)}${arm(-1)}</body></worldbody>
<actuator><position joint="shL" kp="1500" kv="150"/><position joint="shR" kp="1500" kv="150"/></actuator></mujoco>`;
      }
      let t = api.mjcf("ur5e", { option: `<option timestep="0.002"/>`, tool: api.scene === "hold" && api.p.load > 0 ? this.payload(api.p.load) : "" });
      if (api.scene === "spin") {
        t = t.replace(`<joint name="shoulder_pan_joint" class="size3" axis="0 0 1" />`, `<joint name="shoulder_pan_joint" class="size3" axis="0 0 1" armature="0" limited="false" />`)
             .replace(`<general class="size3" name="shoulder_pan" joint="shoulder_pan_joint" />`, `<general class="size3" name="shoulder_pan" joint="shoulder_pan_joint" gainprm="0" biasprm="0 0 0" />`);
      }
      return t;
    },
  },
  izz(api) {                                      // 23.5 节：Σ [(R I Rᵀ)_zz + m(x² + y²)]，从第 1 个会动的 body 算起
    const { m, d } = api.sim, first = api.scene === "chair" ? 1 : 2;
    let I = 0, M = 0;
    const c = [0, 0, 0];
    for (let b = first; b < m.nbody; b++) {
      const R = (k) => d.ximat[9 * b + k], J = [m.body_inertia[3 * b], m.body_inertia[3 * b + 1], m.body_inertia[3 * b + 2]];
      I += R(6) * R(6) * J[0] + R(7) * R(7) * J[1] + R(8) * R(8) * J[2];     // (R diag(J) Rᵀ)_zz
      const x = d.xipos[3 * b], y = d.xipos[3 * b + 1], z = d.xipos[3 * b + 2], mb = m.body_mass[b];
      I += mb * (x * x + y * y); M += mb; c[0] += mb * x; c[1] += mb * y; c[2] += mb * z;
    }
    return { I, M, c: c.map((v) => v / M), M11: d.M[m.dof_Madr[0]] - m.dof_armature[0] };
  },
  reset(api, s) {
    const { mj, m, d } = api.sim, rad = Math.PI / 180;
    const ur = api.m && api.m["B-ARM-UR5E"];
    if (ur && ur.holder) ur.holder.visible = api.scene !== "chair";
    s.hist = []; s.done = false;
    if (api.scene === "chair") {
      d.qvel[0] = 2 * Math.PI;                               // 每秒 1 圈
      mj.mj_forward(m, d);
      s.I0 = this.izz(api).I; s.w0 = d.qvel[0];
      return;
    }
    const q = api.scene === "hold" ? [0, api.p.q2 * rad, api.p.q3 * rad, 0, 0, 0] : [0, 0, 0, -90 * rad, 0, 0];
    q.forEach((v, i) => { d.qpos[i] = v; d.ctrl[i] = v; });
    if (api.scene === "spin") d.qvel[0] = 1.0;
    mj.mj_forward(m, d);
    const r = this.izz(api);
    s.I0 = r.I; s.w0 = d.qvel[0]; s.r = r;
    if (api.scene === "hold") {
      const close = (a, b) => Math.abs(a - b) < 1e-9;
      if (api.p.q2 === 0 && api.p.q3 === 0 && api.p.load === 0 && close(r.I, r.M11)) api.done("zero");
      if (api.p.load === 0 && r.I < 1.0 && close(r.I, r.M11)) api.done("small");
      if (api.p.q2 === 0 && api.p.q3 === 0 && api.p.load >= 3.7 && close(r.I, r.M11)) api.done("load");
    }
  },
  update(dt, api, s) {
    const d = api.sim.d;
    if (api.scene === "hold") { api.stop(); return; }
    if (api.scene === "spin") {
      const u = Math.min(1, Math.max(0, (d.time - 1) / 3)), sm = u * u * (3 - 2 * u), rad = Math.PI / 180;
      d.ctrl[2] = 150 * rad * sm;
    } else {
      const u = Math.min(1, Math.max(0, (d.time - 1) / 2)), sm = u * u * (3 - 2 * u);
      d.ctrl[0] = -1.45 * sm; d.ctrl[1] = -1.45 * sm;
    }
    s.hist.push([d.time, d.qvel[0]]);
    if (d.time >= 5.5 && !s.done) {
      s.done = true;
      const r = this.izz(api);
      s.I1 = r.I; s.ratioI = s.I0 / r.I; s.ratioW = d.qvel[0] / s.w0; s.pred = s.w0 * s.ratioI;
      if (Math.abs(s.ratioW / s.ratioI - 1) < 0.01 && s.ratioW > 1.5) api.done(api.scene === "spin" ? "fold" : "skater");
    }
    if (d.time >= 6) api.stop();
  },
  chart(api, s, ctx, w, h) {
    if (api.scene === "hold") return;
    const H = s.hist || [], top = Math.max(2, ...H.map((r) => r[1]), s.pred || 0) * 1.15;
    const series = [{ pts: H.filter((_, n) => n % 4 === 0), color: "#1f77b4" }];
    if (s.pred) series.push({ pts: [[0, s.pred], [6, s.pred]], color: "#d62728" });
    api.cplot(56, 10, w - 70, h - 34, series, { xmin: 0, xmax: 6, ymin: 0, ymax: top, xlabel: "t / s", ylabel: "ω / (rad/s)" });
  },
  readouts(api, s) {
    if (!api.sim) return [];
    const r = this.izz(api);
    const rows = [
      [["会动部分的质量", "Mass of the moving parts"], api.fmt(r.M, 3) + " kg"],
      [["质心 (x, y, z)", "Centre of mass (x, y, z)"], `(${r.c.map((v) => api.fmt(v, 4)).join(", ")}) m`],
      [["质心到关节 1 轴的水平距离", "Horizontal distance of the CoM from joint 1"], api.fmt(Math.hypot(r.c[0], r.c[1]), 4) + " m"],
      [["绕竖直轴的转动惯量 I_zz（23.5 节）", "Inertia about the vertical axis I_zz (Sec. 23.5)"], api.fmt(r.I, 4) + " kg·m²"],
    ];
    if (api.scene !== "chair") rows.push([["MuJoCo：M₁₁ − 转子惯量", "MuJoCo: M₁₁ − rotor inertia"], api.fmt(r.M11, 4) + " kg·m²"]);
    if (api.scene !== "hold") {
      rows.push([["转速 ω", "Speed ω"], api.fmt(api.sim.d.qvel[0], 3) + " rad/s"]);
      rows.push([["转速之比 / I_zz 之比", "Speed ratio / I_zz ratio"], s.ratioW ? `${api.fmt(s.ratioW, 3)} / ${api.fmt(s.ratioI, 3)}` : "—"]);
    }
    return rows;
  },
  tasks: [
    { id: "zero", robot: true, text: ["零位（θ₂ = θ₃ = 0）、无负载：读出绕关节 1 轴的转动惯量，并与 MuJoCo 质量矩阵的值核对。", "Zero position (θ₂ = θ₃ = 0), no payload: read the inertia about joint 1 and check it against MuJoCo's mass matrix."],
      demo: { scene: "hold", set: { q2: 0, q3: 0, load: 0 }, press: [], wait: 2 } },
    { id: "small", robot: true, text: ["不加负载，找一个姿态使绕关节 1 轴的转动惯量小于 1 kg·m²。", "Without payload, find a pose with an inertia about joint 1 below 1 kg·m²."],
      demo: { scene: "hold", set: { q2: -90, q3: 0, load: 0 }, press: [], wait: 2 } },
    { id: "load", robot: true, text: ["零位装上 3.8 kg 的夹爪与毛坯：转动惯量增加多少？", "At the zero position mount the 3.8 kg gripper and blank: how much does the inertia grow?"],
      demo: { scene: "hold", set: { q2: 0, q3: 0, load: 3.8 }, press: [], wait: 2 } },
    { id: "fold", robot: true, text: ["关节 1 自由转动时折起小臂：转速之比与 I_zz 之比相差不到 1%。", "Fold the forearm with joint 1 free: the speed ratio agrees with the I_zz ratio within 1 %."],
      demo: { scene: "spin", wait: 8 } },
    { id: "skater", text: ["转椅：放下手臂后转速加快，转速之比与 I_zz 之比相差不到 1%。", "Swivel chair: with the arms down the spin speeds up, and the speed ratio agrees with the I_zz ratio within 1 %."],
      demo: { scene: "chair", wait: 8 } },
  ],
  think: ["收臂以后转得更快，动能也增加了。多出来的动能从哪里来？角动量为什么不变？", "After folding, the spin is faster and the kinetic energy larger. Where does the extra energy come from, and why does the angular momentum not change?"],
});
