// 实验 24.4 能量守恒检验：积分器、步长与混沌（配 24.4 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex24_4.py 同一版本。
// 场景 1（机器人）：书中的 UR5e 模型（外观为零件库 glTF），六个关节都不加驱动（<flag actuation="disable"/>），取消转角限位
//   （每个 <joint> 加 limited="false"），关闭碰撞，从 θ = (0, −30°, 0, −90°, 0, 0) 静止放开，仿真 10 s。模型文件自带的
//   <option integrator="implicitfast"/> 写在占位注释之后，会覆盖前面的设置，先把它删去，再按选择写入积分器和步长。
//   可加关节黏性阻尼 b（每个关节相同）。机械能取 MuJoCo 的 energy（势能 + 动能，动能含转子等效惯量）。
// 场景 2（生活）：两个双摆（两根 0.3 m、0.2 kg 的均匀细杆，示意值，与算例 24.4.5 相同）并排放在同一个模型里，互不接触，
//   从 (120°, 60°) 放开，第二个的上杆多 10⁻⁹ rad；RK4，1 ms。每个双摆的机械能按式 (24.2.3)、(24.2.5) 单独计算。
// 阈值由 ex24_4.py 用 Python 版 MuJoCo 核算（同一初始姿态，10 s）：RK4 1 ms 偏差 3.0 × 10⁻⁷ J、4 ms 7.9 × 10⁻⁵ J；
//   Euler 1 ms 1.98 J、4 ms 8.5 J；implicitfast 与 Euler 相同（无阻尼）。双摆约 8.2 s 后相差 0.1 rad 以上。
WQ.lab({
  title: ["实验 24.4 能量守恒检验：积分器、步长与混沌", "Lab 24.4 Testing with energy: integrators, step size and chaos"],
  goal: ["让 UR5e 不加驱动地落下，用机械能是否守恒来检验 MuJoCo 的几种积分器和步长；再看两个几乎一样的双摆怎样分道扬镳。",
         "Let the UR5e fall with no drive and use the conservation of energy to test MuJoCo's integrators and step sizes; then watch two almost identical double pendulums part ways."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "fall", robot: true, name: ["UR5e 自由下落", "UR5e falling freely"], hide: [],
      problem: { title: ["机器人问题：仿真的结果可信吗", "Robot problem: can the simulation be trusted"],
                 text: ["用仿真设计控制器之前，先要知道仿真本身准不准。手臂不加驱动、没有摩擦地落下，机械能应当守恒。换不同的积分器和步长，它守恒得怎么样？",
                        "Before designing a controller in simulation, check the simulation itself. With no drive and no friction the falling arm should keep its energy. How well does it, with different integrators and step sizes?"] } },
    { id: "chaos", name: ["两个双摆", "Two double pendulums"], hide: ["integ", "h", "b"],
      problem: { title: ["生活中的例子：差之毫厘，谬以千里", "Everyday example: a hair's breadth at the start, miles apart later"],
                 text: ["两个一模一样的双摆，放手时的角度只差十亿分之一弧度。它们会一直同步摆下去吗？",
                        "Two identical double pendulums are released a billionth of a radian apart. Will they keep swinging in step?"] } },
  ],
  params: [
    { id: "integ", name: ["积分器：0 Euler / 1 RK4 / 2 implicitfast", "Integrator: 0 Euler / 1 RK4 / 2 implicitfast"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "h", name: ["步长 Δt", "Time step Δt"], min: 1, max: 4, step: 1, value: 1, unit: "ms", digits: 0 },
    { id: "b", name: ["关节阻尼 b", "Joint damping b"], min: 0, max: 1, step: 0.05, value: 0, unit: "N·m·s/rad", digits: 2 },
  ],
  legend: [{ color: "#d62728", name: ["动能 K", "kinetic K"] }, { color: "#1f77b4", name: ["势能 U", "potential U"] }, { color: "#1d2327", name: ["机械能 E", "total E"] }],
  physics: {
    camera: [30, 15, 0.7],
    INTEG: ["Euler", "RK4", "implicitfast"],
    LD: 0.3, MD: 0.2, X0: [120, 60],
    xml(api) {
      if (api.scene === "chaos") {
        const L = this.LD, m = this.MD, I = m * L * L / 12;
        const rod = (n, y) => `<body name="r${n}a" pos="0 ${y} 1.2"><joint name="j${n}a" type="hinge" axis="0 -1 0"/>
<inertial pos="${L / 2} 0 0" mass="${m}" diaginertia="1e-9 ${I} ${I}"/><geom type="capsule" fromto="0 0 0 ${L} 0 0" size="0.012" mass="0" rgba="${n === 1 ? "0.12 0.47 0.71 1" : "0.84 0.15 0.16 1"}"/>
<body name="r${n}b" pos="${L} 0 0"><joint name="j${n}b" type="hinge" axis="0 -1 0"/>
<inertial pos="${L / 2} 0 0" mass="${m}" diaginertia="1e-9 ${I} ${I}"/><geom type="capsule" fromto="0 0 0 ${L} 0 0" size="0.01" mass="0" rgba="${n === 1 ? "0.12 0.47 0.71 1" : "0.84 0.15 0.16 1"}"/></body></body>`;
        return `<mujoco><option timestep="0.001" integrator="RK4" gravity="0 0 -9.81"><flag contact="disable"/></option><worldbody>
<geom type="cylinder" size="0.015 0.25" pos="0 0.08 1.2" quat="0.7071068 0.7071068 0 0" rgba="0.3 0.3 0.32 1"/>
${rod(1, 0)}${rod(2, 0.16)}</worldbody></mujoco>`;
      }
      const integ = this.INTEG[Math.round(api.p.integ)], h = Math.round(api.p.h) / 1000;
      let t = api.mjcf("ur5e", { option: `<option timestep="${h}" integrator="${integ}"><flag contact="disable" actuation="disable" energy="enable"/></option>` });
      t = t.replace(`<option integrator="implicitfast" />`, "");
      t = t.replace(/<joint /g, `<joint limited="false" damping="${api.p.b}" `);
      return t;
    },
  },
  dpE(q1, q2, w1, w2) {                           // 一个双摆的机械能（两杆下垂为零点），式 (24.2.3)、(24.2.5)
    const L = this.physics.LD, m = this.physics.MD, r = L / 2, J = m * L * L / 3, G = 9.81;
    const b = m * L * r * Math.cos(q2);
    const M11 = J + J + m * L * L + 2 * b, M12 = J + b, M22 = J;
    const K = 0.5 * (M11 * w1 * w1 + 2 * M12 * w1 * w2 + M22 * w2 * w2);
    const U = m * G * (r * Math.sin(q1) + L * Math.sin(q1) + r * Math.sin(q1 + q2)) + m * G * (r + L + r);
    return [K, U];
  },
  fixedRun(api) {                                // 另开一份 MjData，从同一初始状态精确地走 10 s，逐步记录机械能的最大偏差（与帧率无关）
    const { mj, m } = api.sim, d2 = new mj.MjData(m), rad = Math.PI / 180;
    [0, -30, 0, -90, 0, 0].forEach((v, i) => { d2.qpos[i] = v * rad; });
    mj.mj_forward(m, d2);
    const E0 = d2.energy[0] + d2.energy[1], n = Math.round(10 / m.opt.timestep);
    let dev = 0;
    for (let k = 0; k < n; k++) {
      mj.mj_step(m, d2);
      mj.mj_forward(m, d2);
      dev = Math.max(dev, Math.abs(d2.energy[0] + d2.energy[1] - E0));
    }
    d2.delete();
    return dev;
  },
  reset(api, s) {
    const { mj, m, d } = api.sim, rad = Math.PI / 180;
    s.hist = []; s.fin = false; s.dev = 0; s.mono = true;
    if (api.scene === "chaos") {
      const [a, b] = this.physics.X0;
      d.qpos[0] = a * rad; d.qpos[1] = b * rad; d.qpos[2] = a * rad + 1e-9; d.qpos[3] = b * rad;
      mj.mj_forward(m, d);
      s.E0 = [this.dpE(d.qpos[0], d.qpos[1], 0, 0), this.dpE(d.qpos[2], d.qpos[3], 0, 0)].map((e) => e[0] + e[1]);
      s.tdiv = null;
      return;
    }
    [0, -30, 0, -90, 0, 0].forEach((v, i) => { d.qpos[i] = v * rad; });
    mj.mj_forward(m, d);
    mj.mj_energyPos(m, d); mj.mj_energyVel(m, d);
    s.E0 = d.energy[0] + d.energy[1]; s.Eprev = s.E0; s.U0 = d.energy[0];
  },
  update(dt, api, s) {
    const d = api.sim.d;
    if (api.scene === "chaos") {
      const e1 = this.dpE(d.qpos[0], d.qpos[1], d.qvel[0], d.qvel[1]), e2 = this.dpE(d.qpos[2], d.qpos[3], d.qvel[2], d.qvel[3]);
      s.dev = Math.max(s.dev, Math.abs(e1[0] + e1[1] - s.E0[0]), Math.abs(e2[0] + e2[1] - s.E0[1]));
      s.gap = Math.max(Math.abs(d.qpos[0] - d.qpos[2]), Math.abs(d.qpos[1] - d.qpos[3]));
      if (s.tdiv === null && s.gap > 0.1) s.tdiv = d.time;
      s.hist.push([d.time, e1[0], e1[1], e1[0] + e1[1], e2[0] + e2[1]]);
      if (d.time >= 12 && !s.fin) {
        s.fin = true;
        if (s.tdiv !== null && s.dev < 1e-4) api.done("chaos");
        api.stop();
      }
      return;
    }
    const E = d.energy[0] + d.energy[1];
    s.dev = Math.max(s.dev, Math.abs(E - s.E0));
    if (E > s.Eprev + 1e-9) s.mono = false;
    s.Eprev = E;
    s.hist.push([d.time, d.energy[1], d.energy[0] - s.U0, E - s.U0]);
    if (d.time >= 10 && !s.fin) {
      s.fin = true;
      const integ = Math.round(api.p.integ), h = Math.round(api.p.h), b = api.p.b;
      if (b === 0) {
        s.devFixed = this.fixedRun(api);
        if (integ === 1 && h === 1 && s.devFixed < 1e-5) api.done("rk4");
        if (integ === 0 && h === 4 && s.devFixed > 1) api.done("euler");
        api.keep.dev = api.keep.dev || {};
        api.keep.dev[`${integ}-${h}`] = s.devFixed;
        const e = api.keep.dev[`0-${h}`], f = api.keep.dev[`2-${h}`];
        if (e !== undefined && f !== undefined && Math.abs(e - f) <= 1e-9 * Math.max(e, 1)) api.done("same");
      }
      if (b >= 0.2 && s.mono && s.E0 - E > 1) api.done("damp");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    if (api.scene === "chaos") {
      api.cplot(56, 10, w - 70, h - 34, [
        { pts: H.filter((_, n) => n % 3 === 0).map((r) => [r[0], r[1]]), color: "#d62728" },
        { pts: H.filter((_, n) => n % 3 === 0).map((r) => [r[0], r[2]]), color: "#1f77b4" },
        { pts: H.map((r) => [r[0], r[3]]), color: "#1d2327" }, { pts: H.map((r) => [r[0], r[4]]), color: "#7a868d" }],
        { xmin: 0, xmax: 12, ymin: 0, ymax: 2.3, xlabel: "t / s", ylabel: "E / J" });
      return;
    }
    const top = Math.max(10, ...H.map((r) => Math.max(r[1], r[3]))) * 1.1, bot = Math.min(-60, ...H.map((r) => r[2])) * 1.1;
    api.cplot(56, 10, w - 70, h - 34, [1, 2, 3].map((k) => ({ pts: H.filter((_, n) => n % 3 === 0).map((r) => [r[0], r[k]]),
      color: ["#d62728", "#1f77b4", "#1d2327"][k - 1] })), { xmin: 0, xmax: 10, ymin: bot, ymax: top, xlabel: "t / s", ylabel: "E / J" });
  },
  readouts(api, s) {
    if (!api.sim) return [];
    const d = api.sim.d;
    if (api.scene === "chaos") {
      return [
        [["时间", "Time"], api.fmt(d.time, 2) + " s"],
        [["两个双摆的最大角度差", "Largest angle difference"], s.gap === undefined ? "—" : s.gap.toExponential(2) + " rad"],
        [["相差超过 0.1 rad 的时刻", "Time the difference passes 0.1 rad"], s.tdiv ? api.fmt(s.tdiv, 2) + " s" : "—"],
        [["机械能的最大偏差（两个中较大的）", "Largest energy error (worse of the two)"], (s.dev || 0).toExponential(2) + " J"],
      ];
    }
    const E = d.energy[0] + d.energy[1];
    return [
      [["积分器、步长", "Integrator, step"], `${this.physics.INTEG[Math.round(api.p.integ)]}, ${Math.round(api.p.h)} ms`],
      [["时间", "Time"], api.fmt(d.time, 2) + " s"],
      [["动能 K", "Kinetic energy K"], api.fmt(d.energy[1], 3) + " J"],
      [["机械能的变化 E − E₀", "Change of energy E − E₀"], (E - s.E0).toExponential(2) + " J"],
      [["机械能的最大偏差（画面各帧）", "Largest energy error (frames shown)"], (s.dev || 0).toExponential(2) + " J"],
      [["10 s 逐步计算的最大偏差（无阻尼时）", "Largest error over every step in 10 s (no damping)"], s.devFixed === undefined ? "—" : s.devFixed.toExponential(2) + " J"],
    ];
  },
  tasks: [
    { id: "rk4", robot: true, text: ["RK4、步长 1 ms、无阻尼，仿真 10 s：机械能的最大偏差小于 10⁻⁵ J。", "RK4, 1 ms, no damping, 10 s: the largest energy error is below 10⁻⁵ J."],
      demo: { scene: "fall", set: { integ: 1, h: 1, b: 0 }, wait: 12 } },
    { id: "euler", robot: true, text: ["Euler、步长 4 ms、无阻尼：机械能偏差超过 1 J。", "Euler, 4 ms, no damping: the energy error exceeds 1 J."],
      demo: { scene: "fall", set: { integ: 0, h: 4, b: 0 }, wait: 12 } },
    { id: "same", robot: true, text: ["关掉执行器、无阻尼时，同一步长下 implicitfast 与 Euler 的能量偏差完全相同（两个都运行一次）。", "With the actuators off and no damping, implicitfast and Euler give exactly the same energy error at the same step (run both)."],
      demo: { scene: "fall", set: { integ: 2, h: 4, b: 0 }, wait: 12 } },
    { id: "damp", robot: true, text: ["加上 0.2 N·m·s/rad 以上的阻尼：机械能单调减少，10 s 内减少 1 J 以上。", "Add at least 0.2 N·m·s/rad of damping: the energy decreases monotonically, by more than 1 J in 10 s."],
      demo: { scene: "fall", set: { integ: 1, h: 1, b: 0.5 }, wait: 12 } },
    { id: "chaos", text: ["两个双摆：12 s 内角度差超过 0.1 rad，而两者的机械能偏差都小于 10⁻⁴ J。", "Two double pendulums: within 12 s their angles differ by more than 0.1 rad, while both energies stay within 10⁻⁴ J."],
      demo: { scene: "chaos", wait: 14 } },
  ],
  think: ["Euler 步长 4 ms 时机械能偏差可达几焦耳，手臂的运动看起来却很“正常”。只看动画能不能发现积分误差？为什么能量是更灵敏的检验？",
          "With Euler at 4 ms the energy error reaches several joules, yet the falling arm looks “normal”. Can the animation alone reveal the integration error? Why is energy a sharper test?"],
});
