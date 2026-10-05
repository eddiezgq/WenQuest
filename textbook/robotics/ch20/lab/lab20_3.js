// 实验 20.3 步态参数与腿的运动（配 20.3 节）。零件库 Go2 三维模型。
// 机器人在“跑步机”上：机身不动，地面上的标记以速度 v 向后移动（与机身坐标系中看到的一样）。机身高度取站立高度 0.2868 m，姿态不变。
// 每条腿：相位 φ_i（以左后腿为 0）、占地系数 β、步态周期 t_c；u = (t/t_c − φ_i) mod 1。支撑相（u < β）足端相对大腿关节
//   x = ℓ/2 − ℓτ（ℓ = vβt_c，中性落脚点，式 (20.3.4)、(20.3.7)）；摆动相按式 (20.3.10)：x = −ℓ/2 + ℓτ − L_s sin(2πτ)/(2π)，
//   z 抬高 h_s(1 − cos 2πτ)/2（式 (20.3.8)）。足端的侧向位置不变（髋外摆为零），由侧视平面两连杆求大腿、小腿关节角，
//   超出小腿关节或大腿关节的限位即判为“超出工作空间”。
// 生活场景“狗的走与跑”：速度 < 0.4 m/s 用爬行（β = 0.8、t_c = 1.0 s），0.4～1.6 m/s 用小跑（β = 0.5、t_c = 0.45 s），
//   ≥ 1.6 m/s 用奔跑（β = 0.3、t_c = 0.35 s）。这些取值是示意值。
WQ.lab({
  title: ["实验 20.3 步态参数与腿的运动", "Lab 20.3 Gait parameters and leg motion"],
  goal: ["选择步态，改变速度、步态周期、占地系数和抬脚高度，看任一时刻几只脚着地、每一步迈多远、摆动脚要多快，以及腿的工作空间够不够用。",
         "Choose a gait and change speed, cycle time, duty factor and step height; see how many feet are down, how far each step reaches, how fast the swinging foot must move, and whether the leg's workspace suffices."],
  view: "3d",
  models: ["B-LEG-GO2"],
  scenes: [
    { id: "gait", robot: true, name: ["Go2 步态", "Go2 gaits"],
      problem: { title: ["机器人问题：四条腿按什么节奏轮流着地", "Robot problem: in what rhythm do the four legs take turns"],
                 text: ["按“开始”让 Go2 在原地“跑步机”上行走（地面标记向后移动）。改变步态参数，读出步幅、支撑行程、摆动脚的最高速度和着地腿数。",
                        "Press Start: Go2 walks on a treadmill (the ground marks move back). Change the gait parameters and read stride, stance stroke, peak swing speed and feet down."] } },
    { id: "dog", name: ["生活：狗的走与跑", "Everyday: a dog walks and runs"], hide: ["gait", "tc", "beta", "hs"],
      problem: { title: ["生活中的例子：狗加快速度时换步态", "Everyday example: a dog changes gait as it speeds up"],
                 text: ["Go2 代表一只狗。只改变速度：慢时爬行，快些小跑，再快就奔跑。看占地系数怎样随步态变小。",
                        "Go2 stands for a dog. Change only the speed: slow, it walks; faster, it trots; faster still, it gallops. Watch the duty factor fall."] } },
  ],
  params: [
    { id: "gait", name: ["步态：0 爬行 1 小跑 2 踱步 3 跳跑 4 奔跑", "gait: 0 walk 1 trot 2 pace 3 bound 4 gallop"], min: 0, max: 4, step: 1, value: 1, digits: 0 },
    { id: "v", name: ["速度 v", "speed v"], min: 0.0, max: 3.0, step: 0.05, value: 0.8, unit: "m/s", digits: 2 },
    { id: "tc", name: ["步态周期 t_c", "cycle time t_c"], min: 0.25, max: 2.0, step: 0.05, value: 0.5, unit: "s", digits: 2 },
    { id: "beta", name: ["占地系数 β", "duty factor β"], min: 0.2, max: 0.95, step: 0.01, value: 0.5, digits: 2 },
    { id: "hs", name: ["抬脚高度 h_s", "step height h_s"], min: 0.02, max: 0.12, step: 0.01, value: 0.08, unit: "m", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "trot", robot: true, text: ["以默认参数（小跑、0.8 m/s、t_c = 0.5 s、β = 0.5）走一个周期以上，腿始终在工作空间内。", "Trot with the defaults (0.8 m/s, t_c = 0.5 s, β = 0.5) for more than one cycle, legs always within their workspace."],
      demo: { scene: "gait", set: { gait: 1, v: 0.8, tc: 0.5, beta: 0.5, hs: 0.08 }, press: ["start"], wait: 60 } },
    { id: "flight", robot: true, text: ["把小跑的占地系数降到 0.5 以下，读出每个周期的腾空时间。", "Lower the trot's duty factor below 0.5 and read the flight time per cycle."],
      demo: { scene: "gait", set: { gait: 1, v: 0.8, tc: 0.5, beta: 0.4, hs: 0.08 }, press: [], wait: 6 } },
    { id: "reach", robot: true, text: ["保持 t_c = 0.5 s、β = 0.5，加大速度，找出支撑行程超出腿的工作空间的速度。", "Keep t_c = 0.5 s, β = 0.5 and raise the speed until the stance stroke exceeds the leg's workspace."],
      demo: { scene: "gait", set: { gait: 1, v: 2.5, tc: 0.5, beta: 0.5, hs: 0.08 }, press: [], wait: 6 } },
    { id: "walk", robot: true, text: ["用爬行步态（β ≥ 0.75）走一个周期，任何时刻至少三只脚着地。", "Walk with the crawl gait (β ≥ 0.75) for one cycle, with at least three feet down at all times."],
      demo: { scene: "gait", set: { gait: 0, v: 0.2, tc: 1.0, beta: 0.8, hs: 0.06 }, press: ["start"], wait: 60 } },
    { id: "dog", text: ["让“狗”加速到 2 m/s 以上，看它换成奔跑并跑一个周期。", "Speed the “dog” up beyond 2 m/s and watch it switch to a gallop for a cycle."],
      demo: { scene: "dog", set: { v: 2.2 }, press: ["start"], wait: 60 } },
  ],
  think: ["为什么占地系数越大，摆动脚要摆得越快？占地系数和速度一定时，缩短步态周期对摆动脚的速度有没有帮助？",
          "Why must the swinging foot move faster when the duty factor grows? With duty factor and speed fixed, does a shorter cycle help the swing speed?"],

  AX: 0.1934, AY: 0.0465, DY: 0.0955, L1: 0.213, L2: 0.213, HH: 0.2648,
  LEGS: ["FL", "FR", "RL", "RR"],
  GAITS: [
    { zh: "爬行", en: "walk", ph: { RL: 0, FL: 0.25, RR: 0.5, FR: 0.75 } },
    { zh: "小跑", en: "trot", ph: { RL: 0, FR: 0, FL: 0.5, RR: 0.5 } },
    { zh: "踱步", en: "pace", ph: { RL: 0, FL: 0, RR: 0.5, FR: 0.5 } },
    { zh: "跳跑", en: "bound", ph: { RL: 0, RR: 0, FL: 0.5, FR: 0.5 } },
    { zh: "奔跑", en: "gallop", ph: { RL: 0, RR: 0.1, FL: 0.5, FR: 0.6 } },
  ],
  LIMT: { F: [-1.5708, 3.4907], R: [-0.5236, 4.5379] }, LIM3: [-2.7227, -0.83776],

  cfg(api) {   // 当前的步态参数
    const p = api.p;
    if (api.scene === "dog") {
      if (p.v < 0.4) return { g: 0, v: p.v, tc: 1.0, beta: 0.8, hs: 0.05 };
      if (p.v < 1.6) return { g: 1, v: p.v, tc: 0.45, beta: 0.5, hs: 0.08 };
      return { g: 4, v: p.v, tc: 0.35, beta: 0.3, hs: 0.08 };
    }
    return { g: Math.round(p.gait), v: p.v, tc: p.tc, beta: p.beta, hs: p.hs };
  },
  foot(c, leg, t) {   // 足端相对大腿关节的 (x, z) 与是否支撑
    const ph = this.GAITS[c.g].ph[leg], u = (((t / c.tc - ph) % 1) + 1) % 1, ell = c.v * c.beta * c.tc, Ls = c.v * c.tc;
    if (u < c.beta) { const tau = u / c.beta; return { x: ell / 2 - ell * tau, z: -this.HH, st: true }; }
    const tau = (u - c.beta) / (1 - c.beta);
    return { x: -ell / 2 + ell * tau - Ls * Math.sin(2 * Math.PI * tau) / (2 * Math.PI), z: -this.HH + c.hs * (1 - Math.cos(2 * Math.PI * tau)) / 2, st: false };
  },
  ik2(leg, x, z) {   // 侧视平面两连杆：膝向后
    const l1 = this.L1, l2 = this.L2, D = Math.hypot(x, z);
    const c3 = (D * D - l1 * l1 - l2 * l2) / (2 * l1 * l2);
    if (c3 > 1 || c3 < -1) return null;
    const t3 = -Math.acos(c3);
    let t2 = Math.atan2(-x, -z) - Math.atan2(l2 * Math.sin(t3), l1 + l2 * Math.cos(t3));
    const L = this.LIMT[leg[0]];
    if (t2 < L[0]) t2 += 2 * Math.PI;
    if (t2 > L[1]) t2 -= 2 * Math.PI;
    if (t3 < this.LIM3[0] || t3 > this.LIM3[1] || t2 < L[0] || t2 > L[1]) return null;
    return [t2, t3];
  },
  analyse(c) {   // 一个周期取 400 个时刻：着地腿数的最少值、腾空时间、是否超出工作空间
    let nmin = 4, flight = 0, bad = null;
    const N = 400;
    for (let k = 0; k < N; k++) {
      const t = c.tc * k / N;
      let n = 0;
      this.LEGS.forEach((leg) => { const f = this.foot(c, leg, t); if (f.st) n++; if (!bad && !this.ik2(leg, f.x, f.z)) bad = leg; });
      nmin = Math.min(nmin, n);
      if (n === 0) flight += c.tc / N;
    }
    return { nmin, flight, bad };
  },

  setup3d(api, keep) {
    const T = api.three, go = api.m["B-LEG-GO2"];
    go.place(0, 0);
    keep.marks = [];
    for (let k = 0; k < 24; k++) {
      const m = new T.Mesh(new T.BoxGeometry(0.02, 0.004, 0.5), new T.MeshStandardMaterial({ color: 0x8a959b }));
      api.st.scene.add(m);
      keep.marks.push(m);
    }
    keep.shown = null;
  },
  reset(api, s) { s.t = 0; s.cycles = 0; s.key = null; },
  start(api, s) { s.t = 0; },
  update(dt, api, s) {
    s.t += dt * 0.5;                     // 慢放一半
    const c = this.cfg(api);
    if (s.t >= c.tc * 1.02) {
      const a = this.analyse(c);
      if (api.scene === "gait" && !a.bad && c.g === 1 && Math.abs(c.v - 0.8) < 0.03 && Math.abs(c.beta - 0.5) < 0.02) api.done("trot");
      if (api.scene === "gait" && !a.bad && c.g === 0 && c.beta >= 0.75 && a.nmin >= 3) api.done("walk");
      if (api.scene === "dog" && !a.bad && c.g === 4 && c.v >= 2) api.done("dog");
    }
    if (s.t > 3 * c.tc + 1) api.stop();
  },

  pose(api, s) {
    const go = api.m["B-LEG-GO2"], c = this.cfg(api), t = s.t || 0, o = Object.assign({}, go.entry.rest);
    this.LEGS.forEach((leg) => {
      const f = this.foot(c, leg, t), q = this.ik2(leg, f.x, f.z);
      if (q) { o[leg + "_hip_joint"] = 0; o[leg + "_thigh_joint"] = q[0]; o[leg + "_calf_joint"] = q[1]; }
    });
    go.set(o);
    const span = 2.4;
    api.keep.marks.forEach((m, k) => {
      const x = ((((k % 12) * 0.2 - c.v * t) % span) + span) % span - span / 2;
      m.position.set(x, 0.002, k < 12 ? 0.32 : -0.32);
    });
  },

  readouts(api, s) {
    const go = api.m["B-LEG-GO2"];
    if (!go || !api.keep.marks) return [];
    this.pose(api, s);
    const c = this.cfg(api), f = (x, n) => api.fmt(x, n), a = this.analyse(c), G = this.GAITS[c.g];
    const down = this.LEGS.filter((leg) => this.foot(c, leg, s.t || 0).st);
    const ell = c.v * c.beta * c.tc;
    if (api.scene === "gait" && c.g === 1 && c.beta < 0.5 && a.flight > 0) api.done("flight");
    if (api.scene === "gait" && a.bad && c.g === 1 && Math.abs(c.tc - 0.5) < 0.03 && Math.abs(c.beta - 0.5) < 0.02) api.done("reach");
    const rows = [[["步态", "gait"], api.T(G.zh, G.en) + (api.scene === "dog" ? api.T(`（β = ${f(c.beta, 2)}，t_c = ${f(c.tc, 2)} s）`, ` (β = ${f(c.beta, 2)}, t_c = ${f(c.tc, 2)} s)`) : "")],
                  [["此刻着地的腿", "feet down now"], down.length ? down.join(" ") : api.T("无（腾空）", "none (flight)")],
                  [["一个周期中着地腿数的最少值", "fewest feet down over a cycle"], String(a.nmin)],
                  [["每个周期的腾空时间", "flight time per cycle"], f(a.flight, 3) + " s"],
                  [["步幅 L_s、支撑行程 ℓ", "stride L_s, stance stroke ℓ"], `${f(c.v * c.tc, 3)} m, ${f(ell, 3)} m`],
                  [["中性落脚点（髋前方）", "neutral foothold (ahead of hip)"], f(ell / 2, 3) + " m"],
                  [["摆动脚对地最高速度 2v/(1−β)", "peak swing speed 2v/(1−β)"], f(2 * c.v / (1 - c.beta), 2) + " m/s"],
                  [["腿的工作空间", "leg workspace"], a.bad ? api.T(`超出：${a.bad} 腿够不着或超限`, `exceeded: leg ${a.bad} cannot reach or hits a limit`) : api.T("够用", "sufficient")]];
    return rows;
  },

  draw(api, s) {
    const K = api.keep;
    if (!K.marks) return;
    if (K.shown !== api.scene) { K.shown = api.scene; api.view(30, 14, 0.75, api.m["B-LEG-GO2"]); }
    this.pose(api, s);
  },
});
