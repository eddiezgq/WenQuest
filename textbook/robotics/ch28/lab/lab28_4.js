// 实验 28.4 跳下台阶：落地的冲击（配 28.4 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex28_4.py 同一版本。
// 场景“Go2 跳下台阶”：书中的 Go2（textbook/robotics/models/mjcf/go2.xml，由 MuJoCo Menagerie unitree_go2 生成），
//   保持“home”姿态，足端离地 h 时从静止落下（机身原点高 0.2884 + h m；home 关键帧的 0.27 m 处足端已压进地面 18 mm）；12 个关节用 PD 控制保持站立姿态 τ = kp(q* − q) − kd q̇，按电机的力矩上限截断
//   （髋、大腿 ±23.7 N·m，小腿 ±45.43 N·m）。机身上可以加负载（加在机身的质量上）。
// 测量：地面对机器人的竖直合力（由 mj_rnePostConstraint 的 cfrc_ext 求和，10 ms 平均）的峰值与体重之比、
//   机身原点比脚刚着地时（0.2884 m）最多下沉多少、小腿电机所需力矩的最大值（截断前）。
// 生活场景“人从台阶上跳下”：把人简化成 70 kg 的身体加一条弹簧-阻尼的腿（腿的刚度可调，阻尼比 0.3，示意值）。
// 由 ex28_4.py 与本页的流程在 Python 中核算（h = 0.3 m）：kp = 60、kd = 2 时峰值 8.48 倍、下沉 63 mm、小腿 32.4 N·m；
//   kp = 35、kd = 1 时 7.13 倍、81 mm；kp = 30、kd = 1 时 7.08 倍、84 mm；h = 0.5 m、kp = 60 时小腿 40.2 N·m，不饱和；kp = 100、kd = 3 时 56.8 N·m，饱和。
WQ.lab({
  title: ["实验 28.4 跳下台阶：落地的冲击", "Lab 28.4 Jumping down a step: the landing impact"],
  goal: ["让 Go2 从不同高度落下，测出地面的冲击力、机身下沉的距离和电机所需的力矩，看腿的刚度怎样在三者之间权衡。",
         "Drop Go2 from different heights, measure the ground impact, how far the body sinks and the motor torque needed, and see how leg stiffness trades them off."],
  view: "physics",
  models: ["B-LEG-GO2"],
  scenes: [
    { id: "go2", robot: true, name: ["Go2 跳下台阶", "Go2 jumps down a step"], hide: ["kl"],
      problem: { title: ["机器人问题：从 0.3 m 的平台跳下，腿受得了吗", "Robot problem: can the legs take a jump from a 0.3 m platform"],
                 text: ["巡检的 Go2 要从装卸平台跳到地面上。落地时地面的力有多大？小腿的电机够不够？关节应该硬一点还是软一点？",
                        "On patrol, Go2 must jump from the loading platform to the floor. How large is the ground force on landing? Are the calf motors strong enough? Should the joints be stiff or soft?"] } },
    { id: "person", name: ["生活：人从台阶上跳下", "Everyday: a person jumps down a step"], hide: ["kp", "kd", "load"],
      problem: { title: ["生活中的例子：为什么跳下来要屈膝", "Everyday example: why you bend your knees when you land"],
                 text: ["直着腿落地，脚后跟和膝盖都疼；屈膝缓冲，就好多了。腿“软”一些，冲击力会小多少？",
                        "Landing stiff-legged hurts the heels and knees; bending the knees helps. How much does a 'softer' leg reduce the impact?"] } },
  ],
  params: [
    { id: "h", name: ["落下高度 h", "Drop height h"], min: 0, max: 0.6, step: 0.05, value: 0.3, unit: "m", digits: 2 },
    { id: "kp", name: ["关节刚度 kp", "Joint stiffness kp"], min: 10, max: 150, step: 5, value: 60, unit: "N·m/rad", digits: 0 },
    { id: "kd", name: ["关节阻尼 kd", "Joint damping kd"], min: 0.2, max: 5, step: 0.1, value: 2, unit: "N·m·s/rad", digits: 1 },
    { id: "load", name: ["机身上的负载", "Payload on the body"], min: 0, max: 5, step: 0.5, value: 0, unit: "kg", digits: 1 },
    { id: "kl", name: ["腿的刚度（人）", "Leg stiffness (person)"], min: 5, max: 100, step: 1, value: 20, unit: "kN/m", digits: 0 },
  ],
  legend: [{ color: "#2ca02c", name: ["地面合力 / 体重", "ground force / weight"] }, { color: "#1f77b4", name: ["机身下沉 / 10 mm", "body sink / 10 mm"] }],
  physics: {
    camera: [30, 10, 0.8],
    rate: 1e-9,                                   // 本页自己逐步推进
    DT: 0.002, G: 9.81, TE: 1.2, Z0: 0.2884,                 // Z0：脚刚碰到地面时机身原点的高度
    HOME: [0, 0.9, -1.8, 0, 0.9, -1.8, 0, 0.9, -1.8, 0, 0.9, -1.8],
    xml(api) {
      const floor = '<geom name="floor" type="plane" size="20 20 .1" rgba="0.8 0.8 0.8 1"/>';
      if (api.scene === "person") {
        const k = api.p.kl * 1000, M = 70, c = 2 * 0.3 * Math.sqrt(k * M);
        return `<mujoco><option timestep="0.0005"/><worldbody>${floor}
<body name="person" pos="0 0 ${1.0 + api.p.h}"><joint name="zb" type="slide" axis="0 0 1"/>
<geom type="capsule" fromto="0 0 0 0 0 0.7" size="0.15" mass="${M}" rgba="0.9 0.6 0.4 1"/>
<body name="leg" pos="0 0 0"><joint name="knee" type="slide" axis="0 0 1" stiffness="${k}" damping="${c}" range="-0.5 0.3"/>
<geom type="capsule" fromto="0 0 0 0 0 -0.9" size="0.06" mass="5" rgba="0.3 0.3 0.6 1"/>
<geom name="foot" type="sphere" pos="0 0 -0.95" size="0.05" mass="0.5" rgba="0.2 0.2 0.2 1"/></body></body></worldbody></mujoco>`;
      }
      return api.mjcf("go2", { world: floor }).replace('mass="6.921"', `mass="${(6.921 + api.p.load).toFixed(3)}"`);
    },
  },
  reset(api, s) {
    const { mj, m, d } = api.sim, ph = this.physics;
    if (api.scene === "go2") {
      d.qpos[0] = 0; d.qpos[1] = 0; d.qpos[2] = ph.Z0 + api.p.h; d.qpos[3] = 1; d.qpos[4] = 0; d.qpos[5] = 0; d.qpos[6] = 0;
      for (let i = 0; i < 12; i++) d.qpos[7 + i] = ph.HOME[i];
      for (let i = 0; i < m.nv; i++) d.qvel[i] = 0;
    }
    mj.mj_forward(m, d);
    const g = api.m && api.m["B-LEG-GO2"];
    if (g && g.holder) g.holder.visible = api.scene === "go2";                   // 人的场景不画 Go2 的外观
    let M = 0; for (let b = 1; b < m.nbody; b++) M += m.body_mass[b];
    if (api.scene === "go2") for (let i = 0; i < 12; i++) {                      // 先给好关节力矩：页面开始时可能先走一步
      const lo = m.actuator_ctrlrange[2 * i], hi = m.actuator_ctrlrange[2 * i + 1];
      d.ctrl[i] = Math.min(hi, Math.max(lo, -api.p.kd * d.qvel[6 + i] + api.p.kp * (ph.HOME[i] - d.qpos[7 + i])));
    }
    s.W = M * ph.G; s.t = 0; s.fz = []; s.hist = []; s.peak = 0; s.zmin = 1e9; s.tq = 0; s.fin = false; s.z0 = null;
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim, ph = this.physics;
    if (s.fin) { api.stop(); return; }
    const DT = api.scene === "go2" ? ph.DT : 0.0005, n = Math.max(1, Math.round(dt / DT));
    for (let k = 0; k < n && !s.fin; k++) {
      if (api.scene === "go2") {
        let tmax = 0;
        for (let i = 0; i < 12; i++) {
          const tau = api.p.kp * (ph.HOME[i] - d.qpos[7 + i]) - api.p.kd * d.qvel[6 + i];
          const lo = m.actuator_ctrlrange[2 * i], hi = m.actuator_ctrlrange[2 * i + 1];
          d.ctrl[i] = Math.min(hi, Math.max(lo, tau));
          if (i % 3 === 2) tmax = Math.max(tmax, Math.abs(tau));
        }
        s.tq = Math.max(s.tq, tmax);
      }
      mj.mj_step(m, d);
      mj.mj_rnePostConstraint(m, d);
      let fz = 0; for (let b = 1; b < m.nbody; b++) fz += d.cfrc_ext[6 * b + 5];
      s.fz.push(fz); if (s.fz.length > Math.round(0.01 / DT)) s.fz.shift();
      const avg = s.fz.reduce((a, b) => a + b, 0) / s.fz.length;
      s.peak = Math.max(s.peak, avg / s.W);
      const z = api.scene === "go2" ? d.qpos[2] : d.qpos[0];                    // 机身原点的高度（人：身体的竖直位移）
      s.touch = api.scene === "go2" ? ph.Z0 : -api.p.h;                          // 脚刚着地时的值
      s.zmin = Math.min(s.zmin, z);
      s.t += DT;
      if (Math.round(s.t / DT) % 5 === 0) s.hist.push([s.t, avg / s.W, Math.max(0, (s.touch - z) * 100)]);
      if (s.t >= ph.TE) s.fin = true;
    }
    if (s.fin) {
      const p = api.p, sinkmm = (s.touch - s.zmin) * 1000, sat = s.tq > 45.43;
      if (api.scene === "go2" && Math.abs(p.h - 0.3) < 0.01 && p.load === 0 && s.peak > 3) api.done("drop");
      if (api.scene === "go2" && Math.abs(p.h - 0.3) < 0.01 && p.load === 0 && s.peak <= 7.2 && sinkmm <= 85) api.done("soft");
      if (api.scene === "go2" && Math.abs(p.h - 0.5) < 0.01 && p.load === 0 && !sat && d.qpos[2] > 0.2) api.done("high");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    api.cplot(48, 10, w - 60, h - 34, [{ pts: H.map((r) => [r[0], r[1]]), color: "#2ca02c" }, { pts: H.map((r) => [r[0], r[2]]), color: "#1f77b4" }],
      { xmin: 0, xmax: this.physics.TE, ymin: 0, ymax: 14, xlabel: "t / s", ylabel: "" });
  },
  readouts(api, s) {
    const f = (v, k = 3) => api.fmt(v, k), go2 = api.scene === "go2";
    const sink = s.zmin < 1e8 && s.touch !== undefined ? (s.touch - s.zmin) * 1000 : NaN;
    const est = sink > 0 ? 1 + api.p.h / (sink / 1000) : NaN;
    return [
      [["体重", "Weight"], f(s.W, 1) + " N"],
      [["地面合力的峰值 / 体重（10 ms 平均）", "Peak ground force / weight (10 ms mean)"], s.peak ? f(s.peak, 2) : "—"],
      [["机身最多下沉（比脚刚着地时）", "Largest sink of the body (from touchdown)"], isFinite(sink) ? f(sink, 1) + " mm" : "—"],
      [["式 (28.4.6) 的估计 1 + h/s", "Estimate 1 + h/s by Eq. (28.4.6)"], isFinite(est) ? f(est, 2) : "—"],
      [["小腿电机所需力矩的最大值 / 上限", "Largest calf torque demanded / limit"], go2 ? `${f(s.tq, 1)} / 45.43 N·m` + (s.tq > 45.43 ? api.T("（饱和）", " (saturated)") : "") : "—"],
    ];
  },
  tasks: [
    { id: "drop", robot: true, text: ["Go2 从 0.3 m 落下，读出冲击力是体重的几倍，与式 (28.4.6) 的估计比较。", "Drop Go2 from 0.3 m; read how many body weights the impact is and compare with the estimate of Eq. (28.4.6)."],
      demo: { scene: "go2", set: { h: 0.3, kp: 60, kd: 2, load: 0 }, wait: 3 } },
    { id: "soft", robot: true, text: ["仍从 0.3 m 落下：调关节刚度和阻尼，使冲击力不超过体重的 7.2 倍，而机身下沉不超过 85 mm。",
                                     "Still from 0.3 m: tune the joint stiffness and damping so that the impact stays below 7.2 body weights while the body sinks no more than 85 mm."],
      demo: { scene: "go2", set: { h: 0.3, kp: 35, kd: 1, load: 0 }, wait: 3 } },
    { id: "high", robot: true, text: ["从 0.5 m 落下：找一个关节刚度，使小腿电机不饱和（所需力矩不超过 45.43 N·m）、机身也不会趴下。",
                                     "From 0.5 m: find a joint stiffness for which the calf motors do not saturate (torque below 45.43 N·m) and the body does not collapse."],
      demo: { scene: "go2", set: { h: 0.5, kp: 60, kd: 2, load: 0 }, wait: 3 } },
  ],
  think: ["关节刚度越大，冲击力越大，机身下沉越少；刚度越小则相反。真实的四足机器人落地时常常在着地前“预先屈腿”、着地瞬间降低刚度，再慢慢站起来。为什么这样做能同时减小冲击力和电机力矩？",
          "Stiffer joints mean a larger impact and less sink; softer joints the opposite. Real quadrupeds often pre-bend their legs before touchdown and lower the stiffness at impact, then stand up slowly. Why does this reduce both the impact and the motor torque?"],
});
