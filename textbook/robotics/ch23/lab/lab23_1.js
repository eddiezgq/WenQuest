// 实验 23.1 动不平衡与静不平衡（配 23.1 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex23_1.py 同一版本。
// 场景 1（机器人）：机器人送进车床卡盘的 SH-301 毛坯（Ø50 mm × 181.7 mm、2.8 kg，数字工厂物料清单）装在竖直的主轴上，
//   绕主轴的 x 轴夹偏 α，质心偏离轴线 e（沿 x）。主轴是无摩擦的铰链，给定初速度后自由转动（没有力矩沿轴，转速不变）。
//   主轴上的 torque、force 传感器读出铰链对毛坯的约束力矩和约束力，它们在随主轴转动的坐标系中是常量。
//   预测：|M| = ω²|I_t − I_a| sin α cos α（式 (23.1.16)），水平力 m e ω²。
// 场景 2（生活）：上开门洗衣机脱水，滚筒（5 kg、半径 0.25 m，示意值）里一团 m 千克的湿衣服偏在离轴 0.2 m 处。
// 阈值由 ex23_1.py 用 Python 版 MuJoCo 核算：α = 1°、1200 r/min 时力矩 2.0012 N·m，与公式相差 < 10⁻⁹；α = 45° 时 57.34 N·m（最大）；
// α = 0°、90° 时为零；e = 1 mm、1200 r/min 时 44.22 N；洗衣机 0.5 kg、510 r/min 时 285.2 N（任务区间 270～300 N）。
WQ.lab({
  title: ["实验 23.1 动不平衡与静不平衡", "Lab 23.1 Dynamic and static unbalance"],
  goal: ["让夹偏、偏心的工件绕主轴转动，测量轴承受到的力矩和力，与惯量张量的非对角元素和质心偏离量的计算比较。",
         "Spin a tilted or off-centre workpiece on a spindle, measure the moment and force on the bearing, and compare them with the off-diagonal inertia and the centre-of-mass offset."],
  view: "physics",
  scenes: [
    { id: "spindle", robot: true, name: ["车床主轴上的毛坯", "Blank on a lathe spindle"], hide: ["lump"],
      problem: { title: ["机器人问题：毛坯送进卡盘时夹偏了", "Robot problem: the blank went into the chuck tilted"],
                 text: ["UR5e 把 SH-301 毛坯送进车床卡盘，没有夹正。主轴转起来后，轴承受到多大的力矩？夹偏多少度最糟？",
                        "The UR5e put the SH-301 blank into the chuck slightly tilted. Once the spindle turns, what moment do the bearings carry? Which tilt is worst?"] } },
    { id: "washer", name: ["洗衣机脱水", "Washing machine spin"], hide: ["alpha", "ecc"],
      params: { n: { min: 100, max: 1200, value: 800, step: 10 } },
      problem: { title: ["生活中的例子：衣服缠成一团", "Everyday example: the laundry bunched up"],
                 text: ["脱水时一团湿衣服甩在滚筒一边。转速多高时，离心力会把洗衣机晃得“走”起来？",
                        "During the spin a wet lump of laundry sits at one side of the drum. At what speed does the centrifugal force shake the machine across the floor?"] } },
  ],
  params: [
    { id: "alpha", name: ["夹偏角 α", "Tilt α"], min: 0, max: 90, step: 1, value: 1, unit: "°", digits: 0 },
    { id: "n", name: ["主轴转速 n", "Spindle speed n"], min: 100, max: 2000, step: 10, value: 1200, unit: "r/min", digits: 0 },
    { id: "ecc", name: ["质心偏离轴线 e", "Centre-of-mass offset e"], min: 0, max: 2, step: 0.1, value: 0, unit: "mm", digits: 1 },
    { id: "lump", name: ["湿衣服的质量", "Mass of the wet lump"], min: 0.1, max: 2, step: 0.1, value: 0.5, unit: "kg", digits: 1 },
  ],
  legend: [{ color: "#b8860b", name: ["轴承力矩 |M|", "bearing moment |M|"] }, { color: "#1f77b4", name: ["水平力 |F|", "horizontal force |F|"] }],
  physics: {
    camera: [30, 20, 0.55],
    blank: { m: 2.8, r: 0.025, L: 0.1816597 },          // SH-301 毛坯（算例 23.1.2）
    xml(api) {
      const sen = `<sensor><torque site="s"/><force site="s"/></sensor>`;
      if (api.scene === "washer") {
        return `<mujoco><option timestep="0.0002" integrator="RK4"/><worldbody>
<geom type="cylinder" size="0.04 0.1" pos="0 0 0.2" rgba="0.6 0.62 0.65 1" contype="0" conaffinity="0"/>
<body name="drum" pos="0 0 0.55"><joint name="spin" type="hinge" axis="0 0 1"/><site name="s"/>
<geom type="cylinder" size="0.25 0.175" mass="5" rgba="0.75 0.8 0.86 0.35" contype="0" conaffinity="0"/>
<geom type="box" size="0.25 0.01 0.17" rgba="0.5 0.55 0.6 1" mass="0" contype="0" conaffinity="0"/>
<geom type="sphere" size="0.07" pos="0.2 0 0" mass="${api.p.lump}" rgba="0.2 0.45 0.8 1" contype="0" conaffinity="0"/>
</body></worldbody>${sen}</mujoco>`;
      }
      const b = this.blank, a = api.p.alpha * Math.PI / 180, e = api.p.ecc / 1000;
      return `<mujoco><option timestep="0.0002" integrator="RK4"/><worldbody>
<geom type="cylinder" size="0.09 0.06" pos="0 0 0.33" rgba="0.36 0.42 0.45 1" contype="0" conaffinity="0"/>
<body name="spindle" pos="0 0 0.5"><joint name="spin" type="hinge" axis="0 0 1"/><site name="s"/>
<geom type="cylinder" size="0.08 0.03" pos="0 0 -0.09" mass="0.000001" rgba="0.55 0.6 0.63 1" contype="0" conaffinity="0"/>
<geom type="box" size="0.012 0.03 0.02" pos="0.07 0 -0.04" mass="0" rgba="0.85 0.55 0.15 1" contype="0" conaffinity="0"/>
<body name="blank" pos="${e} 0 0" quat="${Math.cos(a / 2)} ${Math.sin(a / 2)} 0 0">
<geom type="cylinder" size="${b.r} ${b.L / 2}" mass="${b.m}" rgba="0.62 0.64 0.66 1" contype="0" conaffinity="0"/>
<geom type="box" size="0.003 0.026 0.091" pos="0 0 0" mass="0" rgba="0.85 0.55 0.15 1" contype="0" conaffinity="0"/></body>
</body></worldbody>${sen}</mujoco>`;
    },
  },
  reset(api, s) {
    s.w = api.p.n * 2 * Math.PI / 60;
    api.sim.d.qvel[0] = s.w;
    s.hist = []; s.M = 0; s.F = 0;
  },
  pred(api, s) {
    const w = s.w || api.p.n * 2 * Math.PI / 60;
    if (api.scene === "washer") return { M: 0, F: api.p.lump * 0.2 * w * w };
    const b = this.physics.blank, It = b.m * (3 * b.r * b.r + b.L * b.L) / 12, Ia = b.m * b.r * b.r / 2, a = api.p.alpha * Math.PI / 180;
    return { M: w * w * Math.abs(It - Ia) * Math.sin(a) * Math.cos(a), F: b.m * api.p.ecc / 1000 * w * w };
  },
  update(dt, api, s) {
    const d = api.sim.d, q = d.sensordata;
    s.M = Math.hypot(q[0], q[1]);                                 // 垂直于主轴的力矩（site 随主轴转）
    s.F = Math.hypot(q[3], q[4]);                                 // 水平力
    s.hist.push([d.time, s.M, s.F]);
    if (s.hist.length > 3000) s.hist.shift();
    if (d.time < 0.2) return;
    const p = this.pred(api, s);
    if (api.scene === "spindle") {
      if (api.p.alpha === 0 && api.p.ecc === 0 && s.M < 1e-6 && s.F < 1e-6) api.done("zero");
      if (Math.abs(api.p.alpha - 45) <= 1 && api.p.ecc === 0 && Math.abs(s.M - p.M) < 0.005 * p.M) api.done("max");
      if (api.p.alpha === 90 && api.p.ecc === 0 && s.M < 1e-6) api.done("ninety");
      if (api.p.alpha === 0 && api.p.ecc >= 0.5 && Math.abs(s.F - p.F) < 0.01 * p.F) api.done("static");
    } else if (s.F >= 270 && s.F <= 300) api.done("washer");
    if (d.time >= 1.0) api.stop();
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    const p = this.pred(api, s);
    const top = Math.max(1, 1.3 * p.M, 1.3 * p.F, ...H.map((r) => Math.max(r[1], r[2])));
    api.cplot(56, 10, w - 70, h - 34, [
      { pts: H.filter((_, n) => n % 10 === 0).map((r) => [r[0], r[1]]), color: "#b8860b" },
      { pts: H.filter((_, n) => n % 10 === 0).map((r) => [r[0], r[2]]), color: "#1f77b4" }],
      { xmin: 0, xmax: 1, ymin: 0, ymax: top, xlabel: "t / s", ylabel: "|M| / (N·m), |F| / N" });
  },
  readouts(api, s) {
    if (!api.sim) return [];
    const p = this.pred(api, s);
    const rows = [[["主轴角速度 ω", "Spindle speed ω"], api.fmt(api.sim.d.qvel[0], 2) + " rad/s"]];
    if (api.scene === "spindle") {
      rows.push([["轴承力矩 |M|（MuJoCo）", "Bearing moment |M| (MuJoCo)"], api.fmt(s.M || 0, 4) + " N·m"]);
      rows.push([["式 (23.1.16) 的预测", "Prediction of Eq. (23.1.16)"], api.fmt(p.M, 4) + " N·m"]);
    }
    rows.push([["水平力 |F|（MuJoCo）", "Horizontal force |F| (MuJoCo)"], api.fmt(s.F || 0, 3) + " N"]);
    rows.push([["预测 m e ω²", "Prediction m e ω²"], api.fmt(p.F, 3) + " N"]);
    return rows;
  },
  tasks: [
    { id: "zero", robot: true, text: ["把毛坯夹正（α = 0°、e = 0），按“开始”：轴承力矩和水平力都为零。", "Clamp the blank straight (α = 0°, e = 0) and press Start: both the bearing moment and the horizontal force are zero."],
      demo: { scene: "spindle", set: { alpha: 0, ecc: 0, n: 1200 }, wait: 3 } },
    { id: "max", robot: true, text: ["找出使轴承力矩最大的夹偏角（e = 0），测得的力矩与式 (23.1.16) 相差不到 0.5%。", "Find the tilt that gives the largest bearing moment (e = 0); the measured moment agrees with Eq. (23.1.16) within 0.5 %."],
      demo: { scene: "spindle", set: { alpha: 45, ecc: 0, n: 1200 }, wait: 3 } },
    { id: "ninety", robot: true, text: ["找出夹偏了却不产生力矩的角度（e = 0）：此时转轴是毛坯的哪根主轴？", "Find the tilt that produces no moment although the blank is tilted (e = 0): which principal axis is the spin axis then?"],
      demo: { scene: "spindle", set: { alpha: 90, ecc: 0, n: 1200 }, wait: 3 } },
    { id: "static", robot: true, text: ["夹正但质心偏离轴线 0.5 mm 以上：测得的水平力与 m e ω² 相差不到 1%（静不平衡）。", "Straight but with the centre of mass at least 0.5 mm off the axis: the horizontal force agrees with m e ω² within 1 % (static unbalance)."],
      demo: { scene: "spindle", set: { alpha: 0, ecc: 1, n: 1200 }, wait: 3 } },
    { id: "washer", text: ["洗衣机：0.5 kg 的湿衣服，把转速调到离心力在 270～300 N 之间。", "Washer: with a 0.5 kg lump, set the speed so that the centrifugal force is between 270 and 300 N."],
      demo: { scene: "washer", set: { lump: 0.5, n: 510 }, wait: 3 } },
  ],
  think: ["力矩和力都与转速的平方成正比。主轴转速从 1200 r/min 提高到 2000 r/min，夹偏 1° 的毛坯引起的力矩变为多少？", "Moment and force grow with the square of the speed. If the spindle goes from 1200 to 2000 r/min, what does the moment from a 1° tilt become?"],
});
