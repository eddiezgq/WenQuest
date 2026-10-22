// 实验 24.1 拉格朗日方程：桁架吊运的防摆与秋千（配 24.1 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex24_1.py 同一版本。
// 场景 1（机器人）：桁架小车（滑动关节）吊着一箱毛坯（转动关节 + 质点，吊绳无质量），广义坐标 x、φ（算例 24.1.2）。
//   小车由伺服电机驱动、严格按设定的加速度运动：滑动关节加上很大的等效惯量（armature = 10⁴ kg），电机力 = 总惯性 × 设定加速度，
//   吊重对小车的反作用只改变小车加速度的 0.2% 以下。每一帧按下一帧时间段内的平均加速度给力（加速结束的时刻不必落在帧上）。
//   加速 t_a 秒后匀速，再看 1.5 s。残留摆幅由加速结束后的能量换算：φ_res = arccos(1 − (½l²φ̇² + 𝔤l(1 − cos φ))/(𝔤l))；
//   预测式 (24.1.21)：(2a/𝔤)|sin(ω t_a/2)|，ω = √(𝔤/l)。
// 场景 2（生活）：秋千（绳长 2.5 m、30 kg 的质点，示意值），从 φ₀ 静止放开；周期由 φ̇ 相邻两次由负变正的间隔求得，
//   与小摆角公式 2π√(l/𝔤) 及精确值 (24.1.14)（K 用算术-几何平均计算）比较；变号的时刻在两帧之间线性插值。
// 阈值由 ex24_1.py 核算：l = 1 m、a = 0.5 m/s² 时 T_p = 2.006 s；t_a = T_p/2 残留 5.84°；t_a = T_p 残留 0.01°；
//   60° 的秋千周期是小摆角公式的 1.0732 倍。
WQ.lab({
  title: ["实验 24.1 拉格朗日方程：桁架吊运的防摆与秋千", "Lab 24.1 Lagrange's equations: anti-sway gantry transfer and a swing"],
  goal: ["用拉格朗日方程的结论设计小车的加速时间，使吊重到匀速时不再摆动；测量大摆角秋千的周期，与椭圆积分的公式比较。",
         "Use the result of Lagrange's equations to choose the cart's acceleration time so the load stops swinging once cruising; measure the period of a swing at a large angle and compare it with the elliptic-integral formula."],
  view: "physics",
  scenes: [
    { id: "crane", robot: true, name: ["桁架吊运", "Gantry transfer"], hide: ["phi0"],
      problem: { title: ["机器人问题：吊着的毛坯箱一路晃", "Robot problem: the hanging box of blanks keeps swaying"],
                 text: ["车间的桁架小车吊着一箱毛坯起动，到了匀速段箱子还在前后晃，放到料架上要等它停下来。加速多久，箱子到匀速时就不晃？",
                        "A gantry cart starts off with a box of blanks hanging from it, and the box is still swaying once the cart cruises, so it must settle before it can be set down. How long should the cart accelerate so that the box is still when cruising?"] } },
    { id: "swing", name: ["秋千", "A swing"], hide: ["ta", "acc", "rope"],
      problem: { title: ["生活中的例子：荡得越高，周期越长吗", "Everyday example: does a higher swing take longer"],
                 text: ["小摆角时秋千的周期与摆幅无关。从 60° 放开，周期还是 2π√(l/𝔤) 吗？",
                        "At small angles the period of a swing does not depend on the amplitude. Released from 60°, is it still 2π√(l/𝔤)?"] } },
  ],
  params: [
    { id: "ta", name: ["加速时间 t_a", "Acceleration time t_a"], min: 0.2, max: 4, step: 0.01, value: 1.0, unit: "s", digits: 2 },
    { id: "acc", name: ["小车加速度 a", "Cart acceleration a"], min: 0.1, max: 1.5, step: 0.05, value: 0.5, unit: "m/s²", digits: 2 },
    { id: "rope", name: ["吊绳长度 l", "Rope length l"], min: 0.5, max: 2.5, step: 0.05, value: 1.0, unit: "m", digits: 2 },
    { id: "phi0", name: ["秋千的起始摆角 φ₀", "Swing release angle φ₀"], min: 5, max: 80, step: 1, value: 60, unit: "°", digits: 0 },
  ],
  legend: [{ color: "#1f77b4", name: ["摆角 φ", "angle φ"] }, { color: "#d62728", name: ["式 (24.1.21) 预测的残留摆幅", "residual swing by Eq. (24.1.21)"] }],
  physics: {
    camera: [0, 8, 0.85],
    G: 9.81, MC: 50, ML: 20, ARM: 10000, LS: 2.5, MS: 30,
    xml(api) {
      const G = this.G;
      if (api.scene === "swing") {
        const L = this.LS;
        return `<mujoco><option timestep="0.0005" integrator="RK4" gravity="0 0 -${G}"><flag contact="disable"/></option><worldbody>
<geom type="cylinder" size="0.04 1.3" pos="0 0 3.1" quat="0.7071068 0.7071068 0 0" rgba="0.45 0.3 0.2 1"/>
<geom type="cylinder" size="0.05 1.55" pos="0 -1.25 1.55" rgba="0.45 0.3 0.2 1"/><geom type="cylinder" size="0.05 1.55" pos="0 1.25 1.55" rgba="0.45 0.3 0.2 1"/>
<body name="seat" pos="0 0 3.1"><joint name="phi" type="hinge" axis="0 -1 0"/>
<inertial pos="0 0 ${-L}" mass="${this.MS}" diaginertia="1e-6 1e-6 1e-6"/>
<geom type="capsule" fromto="0 -0.22 0 0 -0.22 ${-L}" size="0.008" mass="0" rgba="0.55 0.55 0.55 1"/>
<geom type="capsule" fromto="0 0.22 0 0 0.22 ${-L}" size="0.008" mass="0" rgba="0.55 0.55 0.55 1"/>
<geom type="box" size="0.14 0.24 0.02" pos="0 0 ${-L}" mass="0" rgba="0.85 0.55 0.15 1"/>
<geom type="sphere" size="0.11" pos="0 0 ${-L + 0.55}" mass="0" rgba="0.95 0.8 0.65 1"/>
<geom type="capsule" fromto="0 0 ${-L + 0.05} 0 0 ${-L + 0.42}" size="0.1" mass="0" rgba="0.25 0.5 0.75 1"/></body>
</worldbody></mujoco>`;
      }
      const L = api.p.rope;
      return `<mujoco><option timestep="0.001" integrator="RK4" gravity="0 0 -${G}"><flag contact="disable"/></option><worldbody>
<geom type="box" size="3.3 0.05 0.05" pos="2.7 0 3.0" rgba="0.3 0.3 0.32 1"/>
<geom type="box" size="0.05 0.05 1.5" pos="-0.55 0 1.5" rgba="0.3 0.3 0.32 1"/><geom type="box" size="0.05 0.05 1.5" pos="5.95 0 1.5" rgba="0.3 0.3 0.32 1"/>
<geom type="box" size="0.4 0.3 0.25" pos="5.4 0 0.25" rgba="0.55 0.6 0.65 1"/>
<body name="cart" pos="0 0 2.9"><joint name="x" type="slide" axis="1 0 0" armature="${this.ARM}"/>
<geom type="box" size="0.22 0.16 0.08" mass="${this.MC}" rgba="0.25 0.5 0.75 1"/>
<body name="load"><joint name="phi" type="hinge" axis="0 -1 0"/>
<inertial pos="0 0 ${-L}" mass="${this.ML}" diaginertia="1e-6 1e-6 1e-6"/>
<geom type="capsule" fromto="0 0 0 0 0 ${-L + 0.12}" size="0.006" mass="0" rgba="0.55 0.55 0.55 1"/>
<geom type="box" size="0.16 0.14 0.12" pos="0 0 ${-L}" mass="0" rgba="0.85 0.55 0.15 1"/></body></body>
</worldbody><actuator><motor joint="x" gear="1" ctrllimited="false"/></actuator></mujoco>`;
    },
  },
  K(k) {                                          // 第一类完全椭圆积分（算术-几何平均）
    let a = 1, b = Math.sqrt(1 - k * k);
    for (let i = 0; i < 30; i++) { const a1 = (a + b) / 2; b = Math.sqrt(a * b); a = a1; }
    return Math.PI / (2 * a);
  },
  force(api, t0, dt) {                            // 下一帧 [t0, t0 + dt] 内的平均加速度 × 总惯性
    const ph = this.physics, ta = api.p.ta, overlap = Math.max(0, Math.min(t0 + dt, ta) - t0);
    return (ph.ARM + ph.MC + ph.ML) * api.p.acc * overlap / dt;
  },
  reset(api, s) {
    const { mj, m, d } = api.sim, ph = this.physics;
    s.hist = []; s.res = null; s.turns = [];
    if (api.scene === "swing") {
      d.qpos[0] = api.p.phi0 * Math.PI / 180;
      mj.mj_forward(m, d);
      return;
    }
    d.ctrl[0] = this.force(api, 0, 1 / 60);
    mj.mj_forward(m, d);
    s.Tp = 2 * Math.PI * Math.sqrt(api.p.rope / ph.G);
    s.pred = 2 * api.p.acc / ph.G * Math.abs(Math.sin(Math.PI * api.p.ta / s.Tp));
  },
  update(dt, api, s) {
    const d = api.sim.d, ph = this.physics, deg = 180 / Math.PI;
    if (api.scene === "swing") {
      s.hist.push([d.time, d.qpos[0] * deg]);
      if (s.wPrev !== undefined && s.wPrev < 0 && d.qvel[0] >= 0)      // φ̇ 由负变正：在两帧之间线性插值求时刻
        s.turns.push(s.tPrev + (0 - s.wPrev) * (d.time - s.tPrev) / (d.qvel[0] - s.wPrev));
      s.wPrev = d.qvel[0]; s.tPrev = d.time;
      if (s.turns.length >= 2 && !s.T) {
        s.T = s.turns[1] - s.turns[0];
        s.T0 = 2 * Math.PI * Math.sqrt(ph.LS / ph.G);
        const k = Math.sin(api.p.phi0 * Math.PI / 360);
        s.Tth = 4 * Math.sqrt(ph.LS / ph.G) * this.K(k);
        if (api.p.phi0 >= 55 && Math.abs(s.T / s.Tth - 1) < 0.005 && s.T / s.T0 > 1.05) api.done("swing");
      }
      if (d.time >= 7.5) api.stop();
      return;
    }
    d.ctrl[0] = this.force(api, d.time, dt * (api.rate || 1));
    const L = api.p.rope, phi = d.qpos[1], w = d.qvel[1];
    s.hist.push([d.time, phi * deg]);
    if (d.time > api.p.ta + 0.05 && s.res === null) {
      const E = 0.5 * L * L * w * w + ph.G * L * (1 - Math.cos(phi));
      s.res = Math.acos(Math.max(-1, 1 - E / (ph.G * L))) * deg;
      const big = 2 * api.p.acc / ph.G * deg;
      if (Math.abs(api.p.ta - s.Tp / 2) < 0.05 * s.Tp && s.res > 0.9 * big) api.done("half");
      if (s.res < 0.5 && api.p.acc >= 0.3) {
        api.done("zero");
        if (L >= 1.8) api.done("long");
      }
    }
    if (d.time >= api.p.ta + 1.5) api.stop();
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    const t1 = api.scene === "swing" ? 7.5 : api.p.ta + 1.5;
    const ylim = api.scene === "swing" ? 1.1 * api.p.phi0 : Math.max(3, 2.4 * api.p.acc / 9.81 * 180 / Math.PI);
    const series = [{ pts: H.filter((_, n) => n % 2 === 0), color: "#1f77b4" }];
    if (api.scene === "crane" && s.pred !== undefined) {
      const r = s.pred * 180 / Math.PI;
      series.push({ pts: [[api.p.ta, r], [t1, r]], color: "#d62728" }, { pts: [[api.p.ta, -r], [t1, -r]], color: "#d62728" });
    }
    api.cplot(56, 10, w - 70, h - 34, series, { xmin: 0, xmax: t1, ymin: -ylim, ymax: ylim, xlabel: "t / s", ylabel: "φ / (°)" });
  },
  readouts(api, s) {
    if (!api.sim) return [];
    const d = api.sim.d, deg = 180 / Math.PI;
    if (api.scene === "swing") {
      return [
        [["摆角 φ", "Angle φ"], api.fmt(d.qpos[0] * deg, 2) + "°"],
        [["测得的周期 T", "Measured period T"], s.T ? api.fmt(s.T, 4) + " s" : "—"],
        [["小摆角公式 2π√(l/𝔤)", "Small-angle formula 2π√(l/𝔤)"], api.fmt(2 * Math.PI * Math.sqrt(2.5 / 9.81), 4) + " s"],
        [["式 (24.1.14)", "Eq. (24.1.14)"], s.Tth ? api.fmt(s.Tth, 4) + " s" : "—"],
        [["T / 小摆角周期", "T / small-angle period"], s.T ? api.fmt(s.T / s.T0, 4) : "—"],
      ];
    }
    return [
      [["摆动周期 T_p = 2π√(l/𝔤)", "Swing period T_p = 2π√(l/𝔤)"], api.fmt(s.Tp || 0, 3) + " s"],
      [["小车位置 x、速度", "Cart position x, speed"], `${api.fmt(d.qpos[0], 3)} m, ${api.fmt(d.qvel[0], 3)} m/s`],
      [["吊重摆角 φ", "Swing angle φ"], api.fmt(d.qpos[1] * deg, 2) + "°"],
      [["残留摆幅（实测，加速结束后）", "Residual swing (measured after the acceleration)"], s.res === null || s.res === undefined ? "—" : api.fmt(s.res, 2) + "°"],
      [["式 (24.1.21) 预测", "Predicted by Eq. (24.1.21)"], api.fmt((s.pred || 0) * deg, 2) + "°"],
    ];
  },
  tasks: [
    { id: "half", robot: true, text: ["加速时间取半个摆动周期（l = 1 m 时约 1.0 s）：读出残留摆幅，它接近最大值 2a/𝔤。",
                                      "Accelerate for half a swing period (about 1.0 s with l = 1 m): read the residual swing, close to its maximum 2a/𝔤."],
      demo: { scene: "crane", set: { ta: 1.0, acc: 0.5, rope: 1.0 }, wait: 6 } },
    { id: "zero", robot: true, text: ["调加速时间（a ≥ 0.3 m/s²），使残留摆幅小于 0.5°。", "Adjust the acceleration time (with a ≥ 0.3 m/s²) so that the residual swing is below 0.5°."],
      demo: { scene: "crane", set: { ta: 2.01, acc: 0.5, rope: 1.0 }, wait: 7 } },
    { id: "long", robot: true, text: ["换一根 1.8 m 以上的吊绳，重新找一个不残留摆动（< 0.5°）的加速时间。", "With a rope of 1.8 m or longer, find again an acceleration time that leaves no swing (< 0.5°)."],
      demo: { scene: "crane", set: { ta: 2.84, acc: 0.5, rope: 2.0 }, wait: 8 } },
    { id: "swing", text: ["秋千从 55° 以上放开，测得的周期比小摆角公式长 5% 以上，并与式 (24.1.14) 相差不到 0.5%。",
                          "Release the swing from 55° or more: the period is over 5 % longer than the small-angle formula and within 0.5 % of Eq. (24.1.14)."],
      demo: { scene: "swing", set: { phi0: 60 }, wait: 8 } },
  ],
  think: ["式 (24.1.21) 说加速时间取 T_p、2T_p、3T_p 都不残留摆动。实际起重机为什么常把加速分成两段、中间隔半个周期，而不是一直加速一个周期？",
          "Eq. (24.1.21) says T_p, 2T_p, 3T_p all leave no swing. Why do real cranes often split the acceleration into two pulses half a period apart instead of accelerating for a whole period?"],
});
