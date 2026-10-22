// 实验 24.2 两连杆臂的力矩：惯性、速度与重力（配 24.2 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex24_2.py 同一版本。
// 场景 1（机器人）：书中的 UR5e 模型（外观为零件库 glTF），关节 1 = 0，手腕锁在 (−90°, 0, 0)，法兰上装夹爪 + SH-301 毛坯
//   （算例 23.2.2 的组合体，按质量等比缩放，3.8 kg 时与之相同）。关节 2、3 从 (−120°, 120°) 用五次多项式在 T 秒内走到 (−30°, 30°)。
//   每一帧把这一时刻的位置、速度、加速度写进 MuJoCo，做三次逆动力学 mj_inverse：
//   加速度、速度都为零 → 重力项 g；只令加速度为零 → c + g；全部 → τ。于是惯性项 = τ − (c + g)，速度项 = (c + g) − g。
//   显示的力矩按书中平面坐标的符号（τ = −τ_UR，式 (24.2.10)），与图 24.2.2 相同。
// 场景 2（生活）：在水平面内甩手臂（示意值，与算例 24.2.3 相同）：上臂 0.30 m；前臂连手 1.6 kg，质心距肘 0.20 m，
//   对质心的转动惯量 1.6 × 0.12² kg·m²。肩由速度伺服保持 10 rad/s，肘关节出一个可调的恒定力矩，肘从 90° 开始。
//   保持 90° 所需的力矩是离心项 hφ̇₁² = m₂a₁r₂ φ̇₁² = 9.6 N·m（式 (24.2.7)）。
// 阈值由 ex24_2.py 核算：装毛坯、T = 1 s 时关节 2 峰值 108.4 N·m；力矩不超过 150 N·m 的最短用时 0.644 s；
//   空手 T = 1 s 峰值 65.4 N·m；T = 0.5 s 时关节 2 的惯性项峰值（约 123 N·m）大于重力项峰值（80.8 N·m）。
WQ.lab({
  title: ["实验 24.2 两连杆臂的力矩：惯性、速度与重力", "Lab 24.2 Two-link arm torques: inertia, velocity and gravity"],
  goal: ["看 UR5e 的关节 2、3 搬动毛坯时，关节力矩怎样分成惯性项、速度项和重力项，各自随动作快慢和负载怎样变化。",
         "Watch how the torques of the UR5e's joints 2 and 3 split into inertial, velocity and gravity terms while moving a blank, and how each changes with the speed of the move and the payload."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "feed", robot: true, name: ["把毛坯送向卡盘", "Feeding the blank to the chuck"], hide: ["tel"],
      problem: { title: ["机器人问题：动作能快到什么程度", "Robot problem: how fast can the move be"],
                 text: ["UR5e 用大臂和小臂把毛坯平着送向卡盘。想把节拍缩短，动作要加快；关节力矩会怎样变？先撞到上限的是哪一项？",
                        "The UR5e moves the blank out flat with its upper arm and forearm. To shorten the cycle the move must be faster; how do the joint torques change, and which term hits the limit first?"] } },
    { id: "whip", name: ["甩手臂", "Swinging the arm"], hide: ["T", "load"],
      problem: { title: ["生活中的例子：肘一放松，前臂就被甩开", "Everyday example: relax the elbow and the forearm flies out"],
                 text: ["在水平面里甩手臂，肘关节不用力的话前臂会被甩直。肘要出多大的力矩，才能保持弯成 90°？",
                        "Swing your arm in a horizontal plane: with a relaxed elbow the forearm is flung straight. How much elbow torque keeps it bent at 90°?"] } },
  ],
  params: [
    { id: "T", name: ["动作用时 T", "Duration of the move T"], min: 0.4, max: 2, step: 0.01, value: 1.0, unit: "s", digits: 2 },
    { id: "load", name: ["法兰上的负载（夹爪 + 毛坯）", "Payload on the flange (gripper + blank)"], min: 0, max: 5, step: 0.1, value: 3.8, unit: "kg", digits: 1 },
    { id: "tel", name: ["肘关节力矩", "Elbow torque"], min: 0, max: 15, step: 0.1, value: 0, unit: "N·m", digits: 1 },
  ],
  legend: [{ color: "#1f77b4", name: ["惯性项", "inertial"] }, { color: "#2ca02c", name: ["速度项", "velocity"] },
           { color: "#7a868d", name: ["重力项", "gravity"] }, { color: "#d62728", name: ["关节 2 总力矩（甩手臂：肘角）", "joint 2 total (whip: elbow angle)"] }],
  physics: {
    camera: [0, 12, 0.75],
    payload(load) {                               // 算例 23.2.2 的组合体按质量缩放：质心在法兰外 0.16114 m（工具方向 y）
      const k = load / 3.8, I = [0.0260338 * k, 0.0017083 * k, 0.0262671 * k];
      return `<body name="payload" pos="0 0.1 0"><inertial pos="0 0.16114 0" mass="${Math.max(load, 1e-6)}" diaginertia="${Math.max(I[0], 1e-9)} ${Math.max(I[1], 1e-9)} ${Math.max(I[2], 1e-9)}"/>
<geom type="box" pos="0 0.05 0" size="0.04 0.05 0.03" rgba="0.36 0.42 0.45 1" mass="0" contype="0" conaffinity="0"/>
<geom type="cylinder" pos="0 0.2008 0" quat="0.7071068 0.7071068 0 0" size="0.025 0.0908" rgba="0.62 0.55 0.35 1" mass="0" contype="0" conaffinity="0"/></body>`;
    },
    xml(api) {
      if (api.scene === "whip") {
        return `<mujoco><option timestep="0.0005" integrator="RK4" gravity="0 0 -9.81"><flag contact="disable"/></option><worldbody>
<geom type="box" size="0.12 0.2 0.3" pos="0 0.22 1.05" rgba="0.25 0.5 0.75 1"/><geom type="sphere" size="0.11" pos="0 0.22 1.5" rgba="0.95 0.8 0.65 1"/>
<body name="upper" pos="0 0 1.3"><joint name="sh" type="hinge" axis="0 0 1"/>
<inertial pos="0.13 0 0" mass="2.1" diaginertia="0.001 0.016 0.016"/>
<geom type="capsule" fromto="0 0 0 0.3 0 0" size="0.045" mass="0" rgba="0.95 0.8 0.65 1"/>
<body name="fore" pos="0.3 0 0"><joint name="el" type="hinge" axis="0 0 1"/>
<inertial pos="0.2 0 0" mass="1.6" diaginertia="0.001 0.02304 0.02304"/>
<geom type="capsule" fromto="0 0 0 0.34 0 0" size="0.035" mass="0" rgba="0.95 0.8 0.65 1"/>
<geom type="sphere" size="0.055" pos="0.38 0 0" mass="0" rgba="0.95 0.8 0.65 1"/></body></body></worldbody>
<actuator><velocity joint="sh" kv="2000"/><motor joint="el" gear="1" ctrllimited="false"/></actuator></mujoco>`;
      }
      return api.mjcf("ur5e", { option: `<option timestep="0.01"><flag contact="disable"/></option>`, tool: api.p.load > 0 ? this.payload(api.p.load) : "" });
    },
  },
  traj(T, t) {                                    // 五次多项式 (22.1.8)，UR5e 的 θ₂、θ₃
    const u = Math.min(Math.max(t / T, 0), 1), r = Math.PI / 180;
    const s = 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5, sd = (30 * u ** 2 - 60 * u ** 3 + 30 * u ** 4) / T, sdd = (60 * u - 180 * u ** 2 + 120 * u ** 3) / T ** 2;
    const a = [-120 * r, 120 * r], dlt = [90 * r, -90 * r];
    return { q: a.map((v, i) => v + s * dlt[i]), qd: dlt.map((v) => sd * v), qdd: dlt.map((v) => sdd * v) };
  },
  inv(api, q, qd, qdd) {                          // 逆动力学：返回关节 2、3 的力矩（平面坐标的符号）
    const { mj, m, d } = api.sim, r = Math.PI / 180;
    const pos = [0, q[0], q[1], -90 * r, 0, 0];
    for (let i = 0; i < 6; i++) { d.qpos[i] = pos[i]; d.qvel[i] = 0; d.qacc[i] = 0; }
    d.qvel[1] = qd[0]; d.qvel[2] = qd[1]; d.qacc[1] = qdd[0]; d.qacc[2] = qdd[1];
    mj.mj_inverse(m, d);
    return [-d.qfrc_inverse[1], -d.qfrc_inverse[2]];
  },
  parts(api, t) {
    const T = api.p.T, tr = this.traj(T, t), z = [0, 0];
    const g = this.inv(api, tr.q, z, z), cg = this.inv(api, tr.q, tr.qd, z), tot = this.inv(api, tr.q, tr.qd, tr.qdd);
    return { tr, g, vel: [cg[0] - g[0], cg[1] - g[1]], inert: [tot[0] - cg[0], tot[1] - cg[1]], tot };
  },
  pose(api, tr) {
    const { mj, m, d } = api.sim, r = Math.PI / 180, pos = [0, tr.q[0], tr.q[1], -90 * r, 0, 0];
    for (let i = 0; i < 6; i++) { d.qpos[i] = pos[i]; d.qvel[i] = 0; d.ctrl[i] = pos[i]; }
    d.qvel[1] = tr.qd[0]; d.qvel[2] = tr.qd[1];
    mj.mj_forward(m, d);
  },
  reset(api, s) {
    const { mj, m, d } = api.sim;
    s.hist = []; s.pk = [0, 0]; s.pkIn = [0, 0]; s.pkG = [0, 0]; s.clock = 0; s.fin = false; s.dev = 0;
    if (api.scene === "whip") {
      d.qpos[1] = Math.PI / 2; d.qvel[0] = 10; d.ctrl[0] = 10; d.ctrl[1] = api.p.tel;
      mj.mj_forward(m, d);
      return;
    }
    s.cur = this.parts(api, 0);
    this.pose(api, s.cur.tr);
  },
  update(dt, api, s) {
    const d = api.sim.d;
    if (api.scene === "whip") {
      d.ctrl[0] = 10; d.ctrl[1] = api.p.tel;
      const el = d.qpos[1] * 180 / Math.PI;
      s.hist.push([d.time, el]);
      s.dev = Math.max(s.dev, Math.abs(el - 90));
      if (d.time >= 1.5) {
        if (!s.fin && s.dev < 3 && api.p.tel > 8.5 && api.p.tel < 10.7) api.done("whip");
        s.fin = true; api.stop();
      }
      return;
    }
    s.clock += dt * (api.rate || 1) / 3;            // 放慢 3 倍播放
    const t = Math.min(s.clock, api.p.T);
    const p = this.parts(api, t);
    s.cur = p;
    for (let j = 0; j < 2; j++) {
      s.pk[j] = Math.max(s.pk[j], Math.abs(p.tot[j])); s.pkIn[j] = Math.max(s.pkIn[j], Math.abs(p.inert[j])); s.pkG[j] = Math.max(s.pkG[j], Math.abs(p.g[j]));
    }
    s.hist.push([t, p.inert[0], p.vel[0], p.g[0], p.tot[0]]);
    this.pose(api, p.tr);
    if (s.clock >= api.p.T && !s.fin) {
      s.fin = true;
      const T = api.p.T, L = api.p.load, peak = Math.max(s.pk[0], s.pk[1]);
      if (Math.abs(T - 1) < 0.011 && Math.abs(L - 3.8) < 0.05) api.done("peak");
      if (peak <= 150 && T <= 0.7 && L >= 3.75) api.done("tmin");
      if (L < 0.05 && Math.abs(T - 1) < 0.011) api.done("empty");
      if (s.pkIn[0] > s.pkG[0]) api.done("inertia");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    if (api.scene === "whip") {
      api.cplot(56, 10, w - 70, h - 34, [{ pts: H.filter((_, n) => n % 4 === 0), color: "#d62728" }, { pts: [[0, 90], [1.5, 90]], color: "#7a868d" }],
        { xmin: 0, xmax: 1.5, ymin: 0, ymax: 180, xlabel: "t / s", ylabel: "φ₂ / (°)" });
      return;
    }
    const cols = ["#1f77b4", "#2ca02c", "#7a868d", "#d62728"];
    api.cplot(56, 10, w - 70, h - 34, cols.map((c, k) => ({ pts: H.map((r) => [r[0], r[k + 1]]), color: c })).concat(
      [{ pts: [[0, 150], [api.p.T, 150]], color: "#e8b4b4" }, { pts: [[0, -150], [api.p.T, -150]], color: "#e8b4b4" }]),
      { xmin: 0, xmax: api.p.T, ymin: -160, ymax: 220, xlabel: "t / s", ylabel: "τ₂ / (N·m)" });
  },
  readouts(api, s) {
    if (!api.sim) return [];
    if (api.scene === "whip") {
      const d = api.sim.d;
      return [
        [["肩的角速度", "Shoulder speed"], api.fmt(d.qvel[0], 2) + " rad/s"],
        [["肘角 φ₂", "Elbow angle φ₂"], api.fmt(d.qpos[1] * 180 / Math.PI, 2) + "°"],
        [["偏离 90° 的最大值", "Largest departure from 90°"], api.fmt(s.dev || 0, 2) + "°"],
        [["离心项 hφ̇₁²（式 (24.2.7)）", "Centrifugal term hφ̇₁² (Eq. 24.2.7)"], api.fmt(1.6 * 0.3 * 0.2 * 100, 2) + " N·m"],
      ];
    }
    const p = s.cur;
    if (!p) return [];
    const f = (v) => api.fmt(v, 1);
    return [
      [["关节 2：惯性 / 速度 / 重力 / 合计", "Joint 2: inertial / velocity / gravity / total"], `${f(p.inert[0])} / ${f(p.vel[0])} / ${f(p.g[0])} / ${f(p.tot[0])} N·m`],
      [["关节 3：惯性 / 速度 / 重力 / 合计", "Joint 3: inertial / velocity / gravity / total"], `${f(p.inert[1])} / ${f(p.vel[1])} / ${f(p.g[1])} / ${f(p.tot[1])} N·m`],
      [["峰值：关节 2 / 关节 3", "Peaks: joint 2 / joint 3"], `${f(s.pk[0])} / ${f(s.pk[1])} N·m`],
      [["关节 2 峰值：惯性项 / 重力项", "Joint 2 peaks: inertial / gravity"], `${f(s.pkIn[0])} / ${f(s.pkG[0])} N·m`],
      [["峰值速度（上限 180 °/s）", "Peak speed (limit 180 °/s)"], api.fmt(1.875 * 90 / api.p.T, 1) + " °/s"],
    ];
  },
  tasks: [
    { id: "peak", robot: true, text: ["装 3.8 kg 的夹爪和毛坯，T = 1 s 运行一次，读出关节 2 的力矩峰值和其中的重力项。",
                                      "With the 3.8 kg gripper and blank, run with T = 1 s and read joint 2's peak torque and its gravity part."],
      demo: { scene: "feed", set: { T: 1.0, load: 3.8 }, wait: 6 } },
    { id: "tmin", robot: true, text: ["装 3.8 kg 负载，找出两个关节力矩都不超过 150 N·m、用时不超过 0.7 s 的动作。",
                                      "With the 3.8 kg payload, find a move of at most 0.7 s with both joint torques within 150 N·m."],
      demo: { scene: "feed", set: { T: 0.66, load: 3.8 }, wait: 5 } },
    { id: "empty", robot: true, text: ["去掉负载，T = 1 s 再运行一次：力矩峰值降低了多少？", "Remove the payload and run again with T = 1 s: how much lower is the peak?"],
      demo: { scene: "feed", set: { T: 1.0, load: 0 }, wait: 6 } },
    { id: "inertia", robot: true, text: ["把动作加快，使关节 2 的惯性项峰值超过重力项峰值。", "Speed up the move until joint 2's inertial peak exceeds its gravity peak."],
      demo: { scene: "feed", set: { T: 0.5, load: 3.8 }, wait: 4 } },
    { id: "whip", text: ["甩手臂：调肘关节的力矩，使前臂在 1.5 s 内保持 90° 的弯曲（偏离不超过 3°）。",
                         "Swinging the arm: set the elbow torque so the forearm stays bent at 90° for 1.5 s (within 3°)."],
      demo: { scene: "whip", set: { tel: 9.6 }, wait: 5 } },
  ],
  think: ["速度项在两个关节上恰好相同，这个巧合依赖于什么？如果小臂在动作中也转动（例如终点改成 (−30°, 60°)），还会相同吗？",
          "The velocity terms of the two joints are exactly equal. What does this rely on? Would it still hold if the forearm also rotated during the move (say the end were (−30°, 60°))?"],
});
