// 实验 29.1 积分方法与步长（配 29.3 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex29_3.py 同一版本、同一个模型。
// 场景“WQ-CR5 的手腕”：零件库的 WQ-CR5（教材 models/mjcf/wqcr5.xml），出厂位置环写成 6 个 position 执行器（kp = 2000、2000、1000、300、300、300，
//   kv = 400、400、200、40、40、40，与 factory/digital/cae/wqcr5.py 的 SERVO_KP、SERVO_KV 相同）；关掉接触和关节的库仑摩擦。
//   从工作姿态 θ = (0, −60°, 80°, −110°, −90°, 0) 出发，目标改变 0.05 rad，仿真 2 s，记最后 1 s 关节速度的幅值（与程序相同）。
//   程序算出 Euler 的步长上限 2.0 ms（1.8 ms 稳定、2.2 ms 振荡），RK4 2.8 ms，implicitfast 不受限。
// 场景“荡秋千”：程序 29.2.1 的两连杆臂（铝胶囊体），只有连杆 1 时是单摆（秋千）。静止放开，仿真 20 s，记能量误差。
//   程序：两连杆、Euler、h = 2 ms 时 20 s 后能量多约 4.7 J，h = 1 ms 时约一半；RK4、h = 2 ms 时误差约 3×10⁻⁶ J。
WQ.lab({
  title: ["实验 29.1 积分方法与步长", "Lab 29.1 Integrators and time steps"],
  goal: ["改变 MuJoCo 的积分方法和时间步长，看能量怎样漂移、什么时候仿真会“炸”；找出 WQ-CR5 出厂位置环的步长上限，与 29.3 节的计算比较。",
         "Change MuJoCo's integrator and time step, watch how energy drifts and when the simulation blows up; find the step limit of the WQ-CR5's stock position loop and compare it with Section 29.3."],
  view: "physics",
  models: ["B-ARM-WQCR5"],
  scenes: [
    { id: "cr", robot: true, name: ["WQ-CR5 的手腕", "The WQ-CR5's wrist"], hide: ["links"],
      problem: { title: ["机器人问题：步长从 2 ms 改成 3 ms，机器人就“炸”了", "Robot problem: change the step from 2 ms to 3 ms and the robot blows up"],
                 text: ["机器人厂的工程师为了让仿真快一点，把时间步长调大，WQ-CR5 的手腕就疯狂地抖起来。步长最大能取多少？由谁决定？",
                        "To speed up a simulation an engineer enlarges the time step, and the WQ-CR5's wrist starts to shake wildly. How large may the step be, and what decides it?"] } },
    { id: "swing", name: ["荡秋千", "A swing"], params: { integ: { value: 0 }, h: { value: 2 } },
      problem: { title: ["生活中的例子：步长取大了，秋千越荡越高", "Everyday example: with too large a step the swing goes ever higher"],
                 text: ["没有人推的秋千（单摆）和两节的“双摆”静止放开。仿真里它们的能量会不会凭空变多？",
                        "A swing nobody pushes (a pendulum) and a two-piece double pendulum are let go from rest. Does their energy grow out of nothing in the simulation?"] } },
  ],
  params: [
    { id: "integ", name: ["积分方法：0 Euler / 1 implicit / 2 implicitfast / 3 RK4", "Integrator: 0 Euler / 1 implicit / 2 implicitfast / 3 RK4"], min: 0, max: 3, step: 1, value: 0, unit: "", digits: 0 },
    { id: "h", name: ["时间步长 h", "Time step h"], min: 0.5, max: 8, step: 0.1, value: 1.8, unit: "ms", digits: 1 },
    { id: "links", name: ["连杆数（1 = 单摆）", "Links (1 = pendulum)"], min: 1, max: 2, step: 1, value: 2, unit: "", digits: 0 },
  ],
  legend: [{ color: "#d62728", name: ["场景 1：J6 的角速度；场景 2：能量误差", "scene 1: J6's angular rate; scene 2: energy error"] }],
  physics: {
    camera: [30, 18, 0.75],
    INTEG: ["Euler", "implicit", "implicitfast", "RK4"],
    KP: [2000, 2000, 1000, 300, 300, 300], KV: [400, 400, 200, 40, 40, 40], LIM: [333, 333, 167.25, 54, 54, 54],
    xml(api) {
      const h = api.p.h / 1000, integ = this.INTEG[Math.round(api.p.integ)];
      if (api.scene === "cr") {
        const act = ["J1", "J2", "J3", "J4", "J5", "J6"].map((n, i) =>
          `<position name="pos_${n}" joint="${n}" kp="${this.KP[i]}" kv="${this.KV[i]}" forcerange="${-this.LIM[i]} ${this.LIM[i]}"/>`).join("");
        const t = api.mjcf("wqcr5", { option: `<option timestep="${h}" integrator="${integ}"><flag contact="disable" frictionloss="disable"/></option>`, actuator: act });
        return t.replace('<option integrator="implicitfast" />', "");
      }
      const two = Math.round(api.p.links) === 2;
      const link2 = two ? `<body name="link2" pos="0.4 0 0"><joint name="j2" range="-150 150"/><geom fromto="0 0 0 0.3 0 0" rgba="0.95 0.55 0.15 1"/></body>` : "";
      return `<mujoco model="arm2"><option timestep="${h}" integrator="${integ}"><flag energy="enable" limit="disable"/></option>
<default><joint type="hinge" axis="0 1 0" damping="0"/><geom type="capsule" size="0.025" density="2700" rgba="0.35 0.6 0.85 1"/></default>
<worldbody><geom type="cylinder" fromto="0 -0.06 1 0 0.06 1" size="0.03" rgba="0.3 0.3 0.32 1" contype="0" conaffinity="0" mass="0"/>
<body name="link1" pos="0 0 1"><joint name="j1" range="-170 170"/><geom fromto="0 0 0 0.4 0 0"/>${link2}</body></worldbody></mujoco>`;
    },
  },
  QCR: [0, -60, 80, -110, -90, 0].map((x) => x * Math.PI / 180),
  reset(api, s) {
    const { mj, m, d } = api.sim;
    s.hist = []; s.fin = false; s.vmax = 0; s.dEmax = 0; s.dE = 0;
    api.rate = api.scene === "swing" ? 5 : 1;
    if (api.scene === "cr") {
      for (let i = 0; i < 6; i++) { d.qpos[i] = this.QCR[i]; d.qvel[i] = 0; }
      for (let i = 0; i < m.nu; i++) d.ctrl[i] = 0;
      for (let i = 0; i < 6; i++) d.ctrl[6 + i] = this.QCR[i] + 0.05;
      s.T = 2;
    } else {
      d.qpos[0] = 0; if (m.nq > 1) d.qpos[1] = 0.5;
      s.T = 20;
    }
    mj.mj_forward(m, d);
    const E = api.energy(); s.E0 = E[0] + E[1];
  },
  update(dt, api, s) {
    const { d } = api.sim;
    if (s.fin) { api.stop(); return; }
    const t = d.time, bad = !Array.from(d.qvel.slice(0, 6)).every(isFinite);
    if (api.scene === "cr") {
      const v6 = d.qvel[5];
      if (t >= 1) s.vmax = Math.max(s.vmax, bad ? Infinity : Math.max(...Array.from(d.qvel.slice(0, 6)).map(Math.abs)));
      if (s.hist.length === 0 || t - s.hist[s.hist.length - 1][0] >= 0.004) s.hist.push([t, Math.max(-20, Math.min(20, isFinite(v6) ? v6 : 20))]);
    } else {
      const E = api.energy(); s.dE = E[0] + E[1] - s.E0; s.dEmax = Math.max(s.dEmax, Math.abs(s.dE));
      if (s.hist.length === 0 || t - s.hist[s.hist.length - 1][0] >= 0.05) s.hist.push([t, s.dE]);
    }
    if (t >= s.T - 1e-9 || bad) {
      s.fin = true;
      const h = api.p.h, integ = Math.round(api.p.integ);
      api.keep.eu = api.keep.eu || {}; api.keep.cr = api.keep.cr || [];
      if (api.scene === "swing" && Math.round(api.p.links) === 2) {
        if (integ === 0 && t >= s.T - 1e-6) {
          api.keep.eu[h.toFixed(1)] = s.dE;
          if (Math.abs(h - 2) < 1e-6 && s.dE > 0.3) api.done("eu");
          const e2 = api.keep.eu["2.0"];
          if (Math.abs(h - 1) < 1e-6 && e2 && s.dE > 0 && e2 / s.dE > 1.6 && e2 / s.dE < 2.6) api.done("half");
        }
        if (integ === 3 && Math.abs(h - 2) < 1e-6 && s.dEmax < 1e-3 && t >= s.T - 1e-6) api.done("rk");
      }
      if (api.scene === "cr") {
        const stable = s.vmax < 0.01, osc = s.vmax > 0.1;
        api.keep.cr.push({ h, integ, stable, osc });
        if (integ === 0 && stable && h >= 1.5) api.done("crok");
        const ok = api.keep.cr.filter((r) => r.integ === 0 && r.stable).map((r) => r.h);
        if (integ === 0 && osc && ok.some((x) => x < h && h - x <= 0.5 + 1e-9)) api.done("crit");
        if (integ === 2 && stable && h >= 3) api.done("impl");
      }
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    if (!H.length) return;
    if (api.scene === "cr") {
      const ym = Math.max(0.06, ...H.map((r) => Math.abs(r[1]))) * 1.1;
      api.cplot(56, 10, w - 70, h - 34, [{ pts: H.map((r) => [r[0], r[1]]), color: "#d62728" }], { xmin: 0, xmax: 2, ymin: -ym, ymax: ym, xlabel: "t / s", ylabel: "θ̇₆ / (rad/s)" });
    } else {
      const ym = Math.max(1e-6, ...H.map((r) => Math.abs(r[1]))) * 1.1;
      api.cplot(56, 10, w - 70, h - 34, [{ pts: H.map((r) => [r[0], r[1]]), color: "#d62728" }], { xmin: 0, xmax: 20, ymin: -ym, ymax: ym, xlabel: "t / s", ylabel: "ΔE / J" });
    }
  },
  readouts(api, s) {
    const f = (v, k = 3) => api.fmt(v, k), integ = this.physics.INTEG[Math.round(api.p.integ)], d = api.sim && api.sim.d;
    const rows = [[["积分方法、时间步长", "Integrator, time step"], `${integ}，${f(api.p.h, 2)} ms`]];
    if (!d) return rows;
    if (api.scene === "cr") {
      rows.push([["仿真时间", "Simulated time"], `${f(d.time, 3)} s / 2 s`]);
      rows.push([["最后 1 s 关节速度的幅值", "Joint-speed amplitude in the last 1 s"], isFinite(s.vmax) ? `${f(s.vmax, 3)} rad/s` : api.T("算飞了", "blew up")]);
      rows.push([["判断（< 0.01 稳定，> 0.1 振荡）", "Verdict (< 0.01 stable, > 0.1 oscillating)"], s.fin ? (s.vmax < 0.01 ? api.T("稳定", "stable") : s.vmax > 0.1 ? api.T("振荡", "oscillating") : api.T("还在衰减", "still decaying")) : "…"]);
      rows.push([["29.3 节算出的步长上限：Euler / RK4", "Step limits from Section 29.3: Euler / RK4"], "2.0 / 2.8 ms"]);
    } else {
      rows.push([["仿真时间", "Simulated time"], `${f(d.time, 3)} s / 20 s`]);
      rows.push([["初始能量 E₀", "Initial energy E₀"], `${f(s.E0, 4)} J`]);
      rows.push([["能量误差：现在 / 最大", "Energy error: now / largest"], `${f(s.dE, 3)} / ${f(s.dEmax, 3)} J`]);
    }
    return rows;
  },
  tasks: [
    { id: "eu", text: ["场景“荡秋千”，两节，Euler、h = 2 ms，跑满 20 s：能量增加了多少？", "Scene “A swing”, two links, Euler, h = 2 ms, run the full 20 s: how much has the energy grown?"],
      demo: { scene: "swing", set: { links: 2, integ: 0, h: 2 }, wait: 8 } },
    { id: "half", text: ["同样的条件把步长减半到 1 ms：能量的增加量约变为原来的一半。", "Same conditions with the step halved to 1 ms: the energy gain drops to about half."],
      demo: { scene: "swing", set: { links: 2, integ: 0, h: 1 }, wait: 10 } },
    { id: "rk", text: ["换成 RK4、h = 2 ms：20 s 内能量误差的最大值小于 0.001 J。", "Switch to RK4 with h = 2 ms: the largest energy error in 20 s is below 0.001 J."],
      demo: { scene: "swing", set: { links: 2, integ: 3, h: 2 }, wait: 10 } },
    { id: "crok", robot: true, text: ["场景“WQ-CR5 的手腕”，Euler，取一个不小于 1.5 ms 的步长让它稳定。", "Scene “The WQ-CR5's wrist”, Euler: pick a step of at least 1.5 ms that is stable."],
      demo: { scene: "cr", set: { integ: 0, h: 1.8 }, wait: 4 } },
    { id: "crit", robot: true, text: ["继续用 Euler，把步长加大到振荡为止：稳定与振荡的两个步长相差不超过 0.5 ms，与 29.3 节的 2.0 ms 比较。", "Keep Euler and enlarge the step until it oscillates: the stable and the oscillating steps differ by at most 0.5 ms; compare with 2.0 ms from Section 29.3."],
      demo: { scene: "cr", set: { integ: 0, h: 2.2 }, wait: 4 } },
    { id: "impl", robot: true, text: ["换成 implicitfast，步长取 3 ms 或更大：仍然稳定。", "Switch to implicitfast with a step of 3 ms or more: still stable."],
      demo: { scene: "cr", set: { integ: 2, h: 3 }, wait: 4 } },
  ],
  think: ["场景 1 中，J6 的惯量八成来自电机转子（29.2 节）。如果模型里漏掉了 armature，Euler 的步长上限会变成多少？这时仿真里看到的振动在真机上有吗？",
          "In scene 1, four fifths of J6's inertia is the motor rotor (Section 29.2). Leave out the armature and what becomes of Euler's step limit? Would the vibration seen in the simulation exist on the real robot?"],
});
