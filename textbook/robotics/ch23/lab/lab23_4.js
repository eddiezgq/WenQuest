// 实验 23.4 转动不同形状的物体看稳定性：网球拍定理（配 23.4 节，物理仿真）。由第 41 轮的样板 demo_physics.js 改成正式实验。
// 浏览器里运行 MuJoCo 3.14.0（与书中程序 ex23_4.py 用的 Python 版同一版本），失重（gravity = 0），自由刚体（freejoint）。
// 场景 1（机器人）：空间站外机械臂松开的工具箱，0.40 × 中间边 b × 0.10 m、6 kg（示意值；b 可调，默认 0.24 m，即算例 23.4.2）。
// 场景 2（生活）：抛起的手机 0.16 × 0.075 × 0.008 m、0.2 kg（示意值）。
// 物体坐标系：x 沿最长边（惯量最小），y 沿中间边（居中），z 沿最短边（最大）。初始角速度：主要绕所选轴 ω₀，另两轴各加 ε·ω₀。
// 积分器 RK4、步长 1 ms。MuJoCo 自由刚体的 qvel[3..5] 是物体坐标系中的角速度。
// 阈值由 ex23_4.py 用 Python 版 MuJoCo 核算：工具箱 ω₀ = 8 rad/s、ε = 1% 时绕中间轴在 1.60 s 第一次翻转、此后每 2.71 s 一次；
// 绕最大、最小惯量轴 10 s 内主轴方向的角速度不低于 ω₀ 的 99.99%（任务取 95%）；ε = 0.1% 时第一次翻转在 2.10 s（任务：10 s 内）；
// 动能和 |L| 的相对漂移 10 s 后小于 10⁻⁹（任务取 10⁻⁶）。手机以 12 rad/s 绕中间轴转，增长率 λ = 9.49 rad/s，零点几秒就翻转。
WQ.lab({
  title: ["实验 23.4 转动不同形状的物体看稳定性", "Lab 23.4 Spinning bodies of different shapes: the tennis-racket theorem"],
  goal: ["让长方体分别绕三根主轴转起来，看哪根轴上的转动稳定、哪根会翻转；用角动量和动能守恒解释，并测出翻转的时间。",
         "Spin a box about each of its three principal axes, see which spins are stable and which flips, explain it with conservation of angular momentum and kinetic energy, and measure when it flips."],
  view: "physics",
  scenes: [
    { id: "kit", robot: true, name: ["空间站工具箱", "Tool case in orbit"],
      problem: { title: ["机器人问题：机械臂松开的工具箱会怎样转", "Robot problem: how does a released tool case tumble"],
                 text: ["空间站外的机械臂松开一个工具箱时，手腕带着它转动。绕哪根轴转，工具箱飘走时姿态才不乱？",
                        "Outside a space station the arm releases a tool case while its wrist is turning. About which axis should it turn so that the case drifts away without tumbling?"] } },
    { id: "phone", name: ["抛起的手机", "A tossed phone"], hide: ["mid"],
      params: { w0: { value: 12 } },
      problem: { title: ["生活中的例子：抛手机", "Everyday example: tossing a phone"],
                 text: ["把手机抛起来，让它绕长边、短边或中间那根轴转。哪一种落回手里时屏幕朝向会变？",
                        "Toss a phone so that it turns about its long axis, its short axis or the middle one. In which case does the screen come back facing the other way?"] } },
  ],
  params: [
    { id: "axis", name: ["转轴：0 最小惯量 / 1 中间 / 2 最大惯量", "Axis: 0 least inertia / 1 intermediate / 2 greatest"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "w0", name: ["初始角速度 ω₀", "Initial angular speed ω₀"], min: 2, max: 20, step: 0.5, value: 8, unit: "rad/s", digits: 1 },
    { id: "eps", name: ["扰动 ε（另两轴）", "Perturbation ε (other axes)"], min: 0.1, max: 5, step: 0.1, value: 1, unit: "%", digits: 1 },
    { id: "mid", name: ["工具箱的中间边 b", "Middle edge b of the case"], min: 12, max: 38, step: 1, value: 24, unit: "cm", digits: 0 },
  ],
  legend: [{ color: "#d62728", name: ["ω_x（最长边）", "ω_x (longest edge)"] }, { color: "#2ca02c", name: ["ω_y（中间边）", "ω_y (middle edge)"] },
           { color: "#1f77b4", name: ["ω_z（最短边）", "ω_z (shortest edge)"] }, { color: "#b8860b", name: ["画面中：角动量 L（不动）", "on stage: angular momentum L (fixed)"] },
           { color: "#7a868d", name: ["画面中：角速度 ω", "on stage: angular velocity ω"] }],
  physics: {
    camera: [35, 20, 0.4],
    xml(api) {
      const kit = api.scene === "kit";
      const [a, b, c] = kit ? [0.20, api.p.mid / 200, 0.05] : [0.08, 0.0375, 0.004];   // half sizes / m
      const mass = kit ? 6 : 0.2;
      return `<mujoco><option timestep="0.001" integrator="RK4" gravity="0 0 0"><flag energy="enable"/></option>
<worldbody><body name="box" pos="0 0 0.8"><freejoint/>
<geom type="box" size="${a} ${b} ${c}" mass="${mass}" rgba="${kit ? "0.85 0.55 0.15 1" : "0.15 0.17 0.2 1"}"/>
<geom type="box" size="${a * 0.98} ${b * 0.9} 0.0005" pos="0 0 ${c}" mass="0.000001" rgba="0.35 0.65 0.95 1"/>
</body></worldbody></mujoco>`;
    },
  },
  setup3d(api, keep) {
    const T3 = api.three;
    keep.g = new T3.Group(); keep.g.rotation.x = -Math.PI / 2;           // MuJoCo 的 z 向上
    keep.L = new T3.ArrowHelper(new T3.Vector3(0, 0, 1), new T3.Vector3(0, 0, 0.8), 0.3, 0xb8860b, 0.05, 0.03);
    keep.w = new T3.ArrowHelper(new T3.Vector3(0, 0, 1), new T3.Vector3(0, 0, 0.8), 0.3, 0x7a868d, 0.04, 0.025);
    keep.g.add(keep.L, keep.w);
    api.st.scene.add(keep.g);
  },
  inertia(api) {
    const m = api.sim.m;
    return [m.body_inertia[3], m.body_inertia[4], m.body_inertia[5]];
  },
  reset(api, s) {
    const k = Math.round(api.p.axis), w = api.p.w0, e = api.p.eps / 100 * w;
    const om = [e, e, e]; om[k] = w;
    for (let i = 0; i < 3; i++) api.sim.d.qvel[3 + i] = om[i];   // 自由刚体：物体坐标系中的角速度
    s.k = k; s.w = w; s.hist = []; s.flips = 0; s.first = null; s.sign = 1; s.minRatio = 1; s.E0 = null; s.L0 = null;
    s.I = this.inertia(api);
  },
  update(dt, api, s) {
    const d = api.sim.d, wk = d.qvel[3 + s.k];
    const sg = Math.sign(wk) || s.sign;
    if (sg !== s.sign) { s.flips++; s.sign = sg; if (s.first === null) s.first = d.time; }
    s.minRatio = Math.min(s.minRatio, Math.abs(wk) / s.w);
    const I = s.I, w = [d.qvel[3], d.qvel[4], d.qvel[5]];
    const E = 0.5 * (I[0] * w[0] * w[0] + I[1] * w[1] * w[1] + I[2] * w[2] * w[2]);
    const L2 = (I[0] * w[0]) ** 2 + (I[1] * w[1]) ** 2 + (I[2] * w[2]) ** 2;
    if (s.E0 === null) { s.E0 = E; s.L0 = L2; }
    s.drift = Math.max(Math.abs(E - s.E0) / s.E0, Math.abs(L2 - s.L0) / s.L0);
    s.hist.push([d.time, w[0], w[1], w[2]]);
    if (s.hist.length > 4000) s.hist.shift();
    const kit = api.scene === "kit";
    if (kit && s.k === 1 && s.flips >= 2) api.done("flip");
    if (kit && s.k === 2 && d.time >= 10 && s.minRatio > 0.95) api.done("max");
    if (kit && s.k === 0 && d.time >= 10 && s.minRatio > 0.95) api.done("min");
    if (kit && s.k === 1 && api.p.eps <= 0.2 + 1e-9 && s.flips >= 1 && s.first <= 10) api.done("small");
    if (d.time >= 10 && s.drift < 1e-6) api.done("energy");
    if (!kit && s.k === 1 && s.flips >= 1) api.done("phone");
    if (d.time >= 30) api.stop();
  },
  draw(api, s) {
    const k = api.keep;
    if (!k || !k.L || !api.sim) return;
    const d = api.sim.d, I = s.I || this.inertia(api), R = d.xmat, p = d.xpos;
    const w = [d.qvel[3], d.qvel[4], d.qvel[5]], Lb = [I[0] * w[0], I[1] * w[1], I[2] * w[2]];
    const toS = (v) => [R[9] * v[0] + R[10] * v[1] + R[11] * v[2], R[12] * v[0] + R[13] * v[1] + R[14] * v[2], R[15] * v[0] + R[16] * v[1] + R[17] * v[2]];   // xmat：物体到世界，按行存
    const T3 = api.three, o = new T3.Vector3(p[3], p[4], p[5]);
    const size = api.scene === "kit" ? 0.35 : 0.14;
    [[k.L, toS(Lb)], [k.w, toS(w)]].forEach(([arrow, v]) => {
      const n = Math.hypot(v[0], v[1], v[2]);
      arrow.position.copy(o);
      if (n > 1e-12) arrow.setDirection(new T3.Vector3(v[0] / n, v[1] / n, v[2] / n));
      arrow.setLength(size, size * 0.18, size * 0.1);
    });
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    const t1 = H.length ? Math.max(10, H[H.length - 1][0]) : 10;
    const W = s.w || api.p.w0;
    api.cplot(48, 10, w - 60, h - 34, [1, 2, 3].map((j, i) => ({
      pts: H.filter((_, n) => n % 4 === 0).map((r) => [r[0], r[j]]), color: ["#d62728", "#2ca02c", "#1f77b4"][i] })),
      { xmin: Math.max(0, t1 - 10), xmax: t1, ymin: -1.1 * W, ymax: 1.1 * W, xlabel: "t / s", ylabel: "ω / (rad/s)" });
  },
  readouts(api, s) {
    if (!api.sim) return [];
    const d = api.sim.d, I = s.I || this.inertia(api), w0 = api.p.w0;
    const lam = w0 * Math.sqrt(Math.max(0, (I[2] - I[1]) * (I[1] - I[0]) / (I[0] * I[2])));
    return [
      [["时间", "Time"], api.fmt(d.time, 2) + " s"],
      [["主惯量 I₁、I₂、I₃", "Principal moments I₁, I₂, I₃"], I.map((x) => x.toExponential(3)).join(", ") + " kg·m²"],
      [["物体坐标系角速度 ω", "Body angular velocity ω"], `(${api.fmt(d.qvel[3], 2)}, ${api.fmt(d.qvel[4], 2)}, ${api.fmt(d.qvel[5], 2)}) rad/s`],
      [["绕中间轴的增长率 λ（式 (23.4.13)）", "Growth rate λ about the middle axis (Eq. 23.4.13)"], api.fmt(lam, 3) + " rad/s"],
      [["所选轴上角速度变号的次数", "Sign changes of ω about the chosen axis"], String(s.flips || 0)],
      [["第一次翻转的时刻", "Time of the first flip"], s.first == null ? "—" : api.fmt(s.first, 3) + " s"],
      [["动能、|L|² 的最大相对漂移", "Largest relative drift of energy and |L|²"], s.drift == null ? "—" : s.drift.toExponential(1)],
    ];
  },
  tasks: [
    { id: "flip", robot: true, text: ["工具箱绕中间轴（1）转起来，看到所选轴上的角速度来回变号（翻转两次）。", "Spin the tool case about the intermediate axis (1) and see its angular velocity change sign back and forth (two flips)."],
      demo: { scene: "kit", set: { axis: 1, w0: 8, eps: 1, mid: 24 }, wait: 8 } },
    { id: "max", robot: true, text: ["工具箱绕最大惯量轴（2）转 10 s，角速度始终保持在 ω₀ 的 95% 以上。", "Spin it about the axis of greatest inertia (2) for 10 s; the angular velocity stays above 95 % of ω₀."],
      demo: { scene: "kit", set: { axis: 2, w0: 8, eps: 1, mid: 24 }, wait: 20 } },
    { id: "min", robot: true, text: ["工具箱绕最小惯量轴（0）转 10 s，同样稳定。", "Spin it about the axis of least inertia (0) for 10 s; it is stable too."],
      demo: { scene: "kit", set: { axis: 0, w0: 8, eps: 1, mid: 24 }, wait: 20 } },
    { id: "small", robot: true, text: ["把扰动减小到 0.2% 以下再绕中间轴转：翻转来得晚一点，但 10 s 内仍然出现。", "Reduce the perturbation below 0.2 % and spin about the middle axis: the flip comes a little later but still within 10 s."],
      demo: { scene: "kit", set: { axis: 1, w0: 8, eps: 0.1, mid: 24 }, wait: 6 } },
    { id: "energy", text: ["转满 10 s，动能和角动量的大小都守恒（相对漂移小于 10⁻⁶）。", "After 10 s both kinetic energy and |L| are conserved (relative drift below 10⁻⁶)."],
      demo: { scene: "kit", set: { axis: 1, w0: 8, eps: 1, mid: 24 }, wait: 20 } },
    { id: "phone", text: ["生活场景：让手机绕中间轴转，看到屏幕翻面（角速度变号）。", "Everyday scene: spin the phone about its middle axis and see the screen turn over (the angular velocity changes sign)."],
      demo: { scene: "phone", set: { axis: 1, w0: 12, eps: 1 }, wait: 4 } },
  ],
  think: ["为什么扰动 ε 越小，翻转来得越晚，却总会来？用式 (23.4.13) 的 λ 估计：ε 缩小 10 倍，翻转大约推迟多久？", "Why does a smaller ε delay the flip but never prevent it? Using λ of Eq. (23.4.13), estimate how much later the flip comes when ε is ten times smaller."],
});
