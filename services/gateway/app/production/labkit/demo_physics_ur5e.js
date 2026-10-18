// 物理仿真实验样板②（第 41 轮）：UR5e 的关节重力矩。模型是书中的网页版 UR5e（Menagerie，去掉网格，质量惯量不变），
// 外观是零件库 glTF。末端法兰上挂一个负载（边长 0.1 m 的方块，质量可调，示意值）。
// 场景 1（静止）：拖滑块摆姿态，MuJoCo 算出保持这个姿态每个关节要出的力矩（重力项 qfrc_bias，静止时科氏、离心项为零）。
// 场景 2（慢慢举起）：关节 2 的位置伺服把大臂从竖直慢慢放到水平，比较伺服实际出的力矩和同一时刻的重力矩。
// 关节角按 Menagerie 的零位：θ₂ = θ₃ = 0 时大臂、小臂水平伸直；θ₂ = −90° 时大臂竖直向上。
WQ.lab({
  title: ["物理仿真样板：UR5e 的关节重力矩", "Physics sample: gravity torques of the UR5e"],
  goal: ["摆出不同姿态、挂不同负载，读出保持静止时六个关节要出的力矩，找出最吃力的姿态。",
         "Pose the arm and change the payload, read the torque each joint needs to hold still, and find the hardest pose."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "hold", robot: true, name: ["静止保持", "Holding still"],
      problem: { title: ["机器人问题：伸直举着工件最费力", "Robot problem: holding a part at arm's length is hardest"],
                 text: ["UR5e 夹着工件停在空中，电机要一直出力顶住重力。哪个关节最吃力？什么姿态下它最吃力？",
                        "The UR5e holds a part in mid-air and its motors must keep pushing against gravity. Which joint works hardest, and in which pose?"] } },
    { id: "lift", name: ["慢慢举起（伺服）", "Slow lift (servo)"], hide: ["q2", "q3"],
      problem: { title: ["生活中的例子：平举一桶水", "Everyday example: holding a bucket at arm's length"],
                 text: ["手臂从竖直慢慢放到水平，肩膀越来越吃力。机械臂也一样：关节 2 的伺服力矩怎样变？",
                        "Lowering your arm from vertical to horizontal makes the shoulder work harder and harder. The robot is the same: how does the servo torque of joint 2 change?"] } },
  ],
  params: [
    { id: "q2", name: ["关节 2 角 θ₂（肩）", "Joint 2 angle θ₂ (shoulder)"], min: -180, max: 0, step: 1, value: -60, unit: "°", digits: 0 },
    { id: "q3", name: ["关节 3 角 θ₃（肘）", "Joint 3 angle θ₃ (elbow)"], min: -150, max: 150, step: 1, value: 60, unit: "°", digits: 0 },
    { id: "load", name: ["负载质量", "Payload mass"], min: 0, max: 5, step: 0.1, value: 2, unit: "kg", digits: 1 },
  ],
  physics: {
    camera: [30, 15, 0.7],
    xml(api) {
      const tool = `<body name="payload" pos="0 0.15 0"><geom type="box" size="0.05 0.05 0.05" mass="${Math.max(api.p.load, 1e-6)}" rgba="0.85 0.55 0.15 1"/></body>`;
      return api.mjcf("ur5e", { option: `<option timestep="0.002"/>`, tool });
    },
  },
  reset(api, s) {
    const { mj, m, d } = api.sim, rad = Math.PI / 180;
    const q = [0, api.p.q2 * rad, api.p.q3 * rad, -90 * rad, 0, 0];
    if (api.scene === "lift") { q[1] = -90 * rad; q[2] = 0; }
    q.forEach((v, i) => { d.qpos[i] = v; d.ctrl[i] = v; });
    mj.mj_forward(m, d);
    s.tau = Array.from(d.qfrc_bias).slice(0, 6);
    s.hist = [];
    if (api.scene === "hold") {
      if (api.p.load >= 5 && Math.abs(api.p.q2) <= 5 && Math.abs(api.p.q3) <= 5) api.done("max");
      if (Math.abs(s.tau[1]) < 1 && api.p.load >= 2) api.done("zero");
    }
  },
  update(dt, api, s) {
    if (api.scene !== "lift") { api.stop(); return; }
    const { d } = api.sim, rad = Math.PI / 180, T = 6;
    const u = Math.min(1, d.time / T), sm = u * u * (3 - 2 * u);
    d.ctrl[1] = (-90 + 90 * sm) * rad;                          // 6 s 内大臂从竖直放到水平（三次平滑）
    s.servo = d.actuator_force[1]; s.grav = d.qfrc_bias[1];
    s.hist.push([d.time, s.servo, s.grav]);
    if (d.time > T + 2) {
      if (Math.abs(s.servo - s.grav) / Math.abs(s.grav) < 0.02) api.done("servo");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    api.cplot(56, 10, w - 70, h - 34, [
      { pts: H.map((r) => [r[0], r[1]]), color: "#1f77b4" }, { pts: H.map((r) => [r[0], r[2]]), color: "#d62728" }],
      { xmin: 0, xmax: 8, ymin: -150, ymax: 150, xlabel: "t / s", ylabel: "τ₂ / (N·m)" });
  },
  legend: [{ color: "#1f77b4", name: ["伺服力矩 τ₂（慢慢举起）", "servo torque τ₂ (slow lift)"] }, { color: "#d62728", name: ["重力矩", "gravity torque"] }],
  readouts(api, s) {
    if (!api.sim) return [];
    const t = api.scene === "lift" ? Array.from(api.sim.d.qfrc_bias).slice(0, 6) : (s.tau || []);
    return [
      [["关节 1、2、3 力矩", "Joint 1, 2, 3 torques"], t.slice(0, 3).map((x) => api.fmt(x, 2)).join(", ") + " N·m"],
      [["关节 4、5、6 力矩", "Joint 4, 5, 6 torques"], t.slice(3, 6).map((x) => api.fmt(x, 2)).join(", ") + " N·m"],
      [["关节 2 额定（Menagerie 力矩上限）", "Joint 2 limit (Menagerie force range)"], "150 N·m"],
      ...(api.scene === "lift" ? [[["伺服力矩 / 重力矩（关节 2）", "Servo / gravity torque (joint 2)"],
        s.servo == null ? "—" : `${api.fmt(s.servo, 1)} / ${api.fmt(s.grav, 1)} N·m`]] : []),
    ];
  },
  tasks: [
    { id: "max", robot: true, text: ["挂 5 kg，把大臂、小臂都放到水平（θ₂ ≈ 0°，θ₃ ≈ 0°），读出关节 2 的力矩：这是最吃力的姿态。",
                                     "With 5 kg, put the upper arm and forearm horizontal (θ₂ ≈ 0°, θ₃ ≈ 0°) and read joint 2's torque: the hardest pose."],
      demo: { scene: "hold", set: { load: 5, q2: 0, q3: 0 }, press: [], wait: 2 } },
    { id: "zero", robot: true, text: ["挂 2 kg 以上，找一个关节 2 几乎不用出力（|τ₂| < 1 N·m）的姿态。",
                                      "With at least 2 kg, find a pose where joint 2 hardly works (|τ₂| < 1 N·m)."],
      demo: { scene: "hold", set: { load: 2, q2: -90, q3: 0 }, press: [], wait: 2 } },
    { id: "servo", text: ["“慢慢举起”运行到底：最后静止时伺服力矩与重力矩相差不到 2%。",
                          "Run the slow lift to the end: once still, the servo torque is within 2 % of the gravity torque."],
      demo: { scene: "lift", set: { load: 2 }, wait: 10 } },
  ],
  think: ["为什么 θ₂ = −90°（大臂竖直）时关节 2 几乎不出力，而关节 3 的力矩却随 θ₃ 变？", "Why does joint 2 hardly work at θ₂ = −90° (upper arm vertical), while joint 3's torque still depends on θ₃?"],
});
