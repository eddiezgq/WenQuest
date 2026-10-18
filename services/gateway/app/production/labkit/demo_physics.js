// 物理仿真实验样板（第 41 轮）：网球拍定理——自由刚体绕最大、最小惯量轴转动稳定，绕中间轴转动会翻转。
// 浏览器里跑的是 MuJoCo 官方 WebAssembly 版（3.14.0），与教材构建用的 Python 版结果一致。
// 场景 1（机器人）：空间站外，机械臂松开的工具箱 0.40 × 0.24 × 0.10 m，质量 6 kg（示意值），失重。
// 场景 2（生活）：抛起的手机 0.16 × 0.075 × 0.008 m，0.2 kg，看它在空中怎样转（不计重力，只看转动）。
// 体坐标系：x 沿最长边（惯量最小），y 沿中间边（惯量居中），z 沿最短边（惯量最大）。
// 初始角速度：主要绕所选轴 ω₀，另两轴各加 ε·ω₀ 的小扰动。积分器 RK4，步长 1 ms。
WQ.lab({
  title: ["物理仿真样板：网球拍定理", "Physics sample: the tennis-racket theorem"],
  goal: ["让一个长方体分别绕三根主轴转起来，看哪根轴上的转动稳定、哪根会翻转，并用角动量和能量守恒解释。",
         "Spin a box about each of its three principal axes, see which spins are stable and which flips, and explain it with conservation of angular momentum and energy."],
  view: "physics",
  scenes: [
    { id: "kit", robot: true, name: ["空间站工具箱", "Tool case in orbit"],
      problem: { title: ["机器人问题：机械臂松开的工具箱会怎样转", "Robot problem: how does a released tool case tumble"],
                 text: ["空间站外的机械臂松开一个工具箱时，手腕带着它转动。绕哪根轴转，工具箱飘走时姿态才不乱？",
                        "Outside a space station the arm releases a tool case while its wrist is turning. About which axis should it turn so that the case drifts away without tumbling?"] } },
    { id: "phone", name: ["抛起的手机", "A tossed phone"],
      params: { w0: { value: 12 } },
      problem: { title: ["生活中的例子：抛手机", "Everyday example: tossing a phone"],
                 text: ["把手机抛起来让它绕长边、短边或中间那根轴转一圈半再接住。哪一种落回手里时屏幕朝向会变？",
                        "Toss a phone so that it turns about its long axis, its short axis or the middle one, and catch it. In which case does the screen come back facing the other way?"] } },
  ],
  params: [
    { id: "axis", name: ["转轴：0 最小惯量 / 1 中间 / 2 最大惯量", "Axis: 0 least inertia / 1 intermediate / 2 greatest"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "w0", name: ["初始角速度 ω₀", "Initial angular speed ω₀"], min: 2, max: 20, step: 0.5, value: 8, unit: "rad/s", digits: 1 },
    { id: "eps", name: ["扰动 ε（另两轴）", "Perturbation ε (other axes)"], min: 0.1, max: 5, step: 0.1, value: 1, unit: "%", digits: 1 },
  ],
  legend: [{ color: "#d62728", name: ["ω_x（最长边）", "ω_x (longest edge)"] }, { color: "#2ca02c", name: ["ω_y（中间边）", "ω_y (middle edge)"] },
           { color: "#1f77b4", name: ["ω_z（最短边）", "ω_z (shortest edge)"] }],
  physics: {
    camera: [35, 20, 0.45],
    xml(api) {
      const kit = api.scene === "kit";
      const [a, b, c] = kit ? [0.20, 0.12, 0.05] : [0.08, 0.0375, 0.004];   // half sizes / m
      const mass = kit ? 6 : 0.2;
      return `<mujoco><option timestep="0.001" integrator="RK4" gravity="0 0 0"><flag energy="enable"/></option>
<worldbody><body name="box" pos="0 0 ${kit ? 0.8 : 0.5}"><freejoint/>
<geom type="box" size="${a} ${b} ${c}" mass="${mass}" rgba="${kit ? "0.85 0.55 0.15 1" : "0.15 0.17 0.2 1"}"/>
<geom type="box" size="${a * 0.98} ${b * 0.9} 0.0005" pos="0 0 ${c}" mass="0.000001" rgba="0.35 0.65 0.95 1"/>
</body></worldbody></mujoco>`;
    },
  },
  reset(api, s) {
    const k = Math.round(api.p.axis), w = api.p.w0, e = api.p.eps / 100 * w;
    const om = [e, e, e]; om[k] = w;
    for (let i = 0; i < 3; i++) api.sim.d.qvel[3 + i] = om[i];   // free joint: angular velocity in the body frame
    s.k = k; s.w = w; s.hist = []; s.flips = 0; s.sign = 1; s.minRatio = 1; s.E0 = null;
  },
  update(dt, api, s) {
    const d = api.sim.d, wk = d.qvel[3 + s.k];
    const sg = Math.sign(wk) || s.sign;
    if (sg !== s.sign) { s.flips++; s.sign = sg; }
    s.minRatio = Math.min(s.minRatio, Math.abs(wk) / s.w);
    const E = d.energy[1];
    if (s.E0 === null) s.E0 = E;
    s.drift = Math.abs(E - s.E0) / s.E0;
    s.hist.push([d.time, d.qvel[3], d.qvel[4], d.qvel[5]]);
    if (s.hist.length > 4000) s.hist.shift();
    if (s.k === 1 && s.flips >= 2) api.done("flip");
    if (s.k === 2 && d.time >= 10 && s.minRatio > 0.95) api.done("max");
    if (s.k === 0 && d.time >= 10 && s.minRatio > 0.95) api.done("min");
    if (d.time >= 10 && s.drift < 1e-4) api.done("energy");
    if (d.time >= 30) api.stop();
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
    const d = api.sim.d;
    return [
      [["时间", "Time"], api.fmt(d.time, 2) + " s"],
      [["体坐标系角速度 ω", "Body angular velocity ω"], `(${api.fmt(d.qvel[3], 2)}, ${api.fmt(d.qvel[4], 2)}, ${api.fmt(d.qvel[5], 2)}) rad/s`],
      [["绕所选轴翻转次数", "Flips about the chosen axis"], String(s.flips || 0)],
      [["动能相对漂移", "Relative drift of kinetic energy"], s.drift == null ? "—" : s.drift.toExponential(1)],
    ];
  },
  tasks: [
    { id: "flip", text: ["绕中间轴（1）转起来，看到所选轴上的角速度来回变号（翻转两次）。", "Spin about the intermediate axis (1) and see the angular velocity about it change sign back and forth (two flips)."],
      demo: { set: { axis: 1, w0: 8, eps: 1 }, wait: 8 } },
    { id: "max", text: ["绕最大惯量轴（2）转 10 s，角速度始终保持在 ω₀ 的 95% 以上。", "Spin about the axis of greatest inertia (2) for 10 s; the angular velocity stays above 95 % of ω₀."],
      demo: { set: { axis: 2, w0: 8, eps: 1 }, wait: 12 } },
    { id: "min", text: ["绕最小惯量轴（0）转 10 s，同样稳定。", "Spin about the axis of least inertia (0) for 10 s; it is stable too."],
      demo: { set: { axis: 0, w0: 8, eps: 1 }, wait: 12 } },
    { id: "energy", text: ["转满 10 s，动能的相对漂移小于 10⁻⁴（没有外力矩，能量守恒）。", "After 10 s the kinetic energy has drifted by less than 10⁻⁴ (no external torque: energy is conserved)."],
      demo: { set: { axis: 1, w0: 8, eps: 1 }, wait: 12 } },
  ],
  think: ["为什么扰动 ε 越小，翻转来得越晚，却总会来？用 ω_y 的线性化方程说明。", "Why does a smaller ε delay the flip but never prevent it? Explain with the linearized equation for ω_y."],
});
