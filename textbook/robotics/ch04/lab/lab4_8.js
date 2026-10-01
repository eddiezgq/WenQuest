// 实验 4.8 数值漂移与正交化（配 4.8 节）。姿态按一阶近似或罗德里格斯公式反复更新，可选定期正交化。
WQ.lab({
  title: ["实验 4.8 数值漂移与正交化", "Lab 4.8 Numerical drift and re-orthonormalization"],
  goal: ["看反复更新后 RᵀR 偏离 I 的程度怎样增长，以及定期正交化怎样把它拉回来。", "Watch how far RᵀR drifts from I under repeated updates, and how regular re-orthonormalization pulls it back."],
  scenes: [
    { id: "ctrl", robot: true, name: ["控制器里的姿态更新", "Attitude update in a controller"],
      problem: { title: ["机器人问题：一秒上千次的乘法", "Robot problem: a thousand multiplications a second"],
                 text: ["末端以角速度 ω_b = (0.3, −0.5, 0.8) rad/s 转动，控制器每个周期右乘一个小转动来更新姿态。", "The tool turns at ω_b = (0.3, −0.5, 0.8) rad/s; each cycle the controller right-multiplies a small rotation."] } },
    { id: "imu", name: ["手机里的陀螺仪", "A phone's gyroscope"],
      problem: { title: ["生活中的例子：手机姿态", "Everyday example: phone attitude"], text: ["手机把陀螺仪读数积分成姿态，同样会漂移。", "A phone integrates its gyro into attitude, and drifts the same way."] } },
  ],
  params: [
    { id: "dt", name: ["时间步长 Δt", "Time step Δt"], min: 1, max: 20, step: 1, value: 10, unit: "ms", digits: 0 },
    { id: "exact", name: ["更新方法：0 一阶近似 / 1 罗德里格斯", "Update: 0 first order / 1 Rodrigues"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "every", name: ["每多少步正交化一次（0 = 不做）", "Re-orthonormalize every N steps (0 = never)"], min: 0, max: 200, step: 10, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["运行 20 s", "Run 20 s"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "drift", robot: true, text: ["一阶近似、Δt = 10 ms、不正交化：20 s 后偏差超过 1%。", "First order, Δt = 10 ms, no fix: the deviation exceeds 1% within 20 s."],
      demo: { scene: "ctrl", set: { dt: 10, exact: 0, every: 0 }, press: ["start"], wait: 8 } },
    { id: "exact", robot: true, text: ["改用罗德里格斯公式：偏差小于 10⁻⁹。", "Use Rodrigues: the deviation stays below 10⁻⁹."],
      demo: { scene: "ctrl", set: { dt: 10, exact: 1, every: 0 }, press: ["start"], wait: 8 } },
    { id: "fix", text: ["一阶近似，但每 20 步正交化一次：偏差始终小于 0.5%。", "First order, re-orthonormalized every 20 steps: the deviation stays below 0.5%."],
      demo: { scene: "imu", set: { dt: 10, exact: 0, every: 20 }, press: ["start"], wait: 8 } },
  ],
  think: ["步长减半，一阶近似 20 s 后的偏差大约变成多少？为什么？", "Halve the step: roughly what happens to the drift after 20 s, and why?"],

  reset(api, s) { s.R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; s.time = 0; s.steps = 0; s.hist = [[0, 0]]; s.max = 0; },
  mul(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  dev(R) { let m = 0; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) { let v = 0; for (let k = 0; k < 3; k++) v += R[k][i] * R[k][j]; m = Math.max(m, Math.abs(v - (i === j ? 1 : 0))); } return m; },
  ortho(R) { // Gram–Schmidt on the columns is enough to show the effect here (the SVD gives the nearest; see 4.8.4)
    const c = [0, 1, 2].map((j) => [R[0][j], R[1][j], R[2][j]]), n = (v) => { const L = Math.hypot(...v); return v.map((x) => x / L); };
    const x = n(c[0]), d = x[0] * c[1][0] + x[1] * c[1][1] + x[2] * c[1][2], y = n(c[1].map((v, i) => v - d * x[i]));
    const z = [x[1] * y[2] - x[2] * y[1], x[2] * y[0] - x[0] * y[2], x[0] * y[1] - x[1] * y[0]];
    return [0, 1, 2].map((i) => [x[i], y[i], z[i]]); },
  step(api, s) {
    const w = [0.3, -0.5, 0.8], dt = api.p.dt / 1000;
    let M;
    if (api.p.exact) { const th = Math.hypot(...w) * dt, u = w.map((v) => v / Math.hypot(...w)), c = Math.cos(th), sn = Math.sin(th), C = 1 - c, [x, y, z] = u;
      M = [[c + x * x * C, x * y * C - z * sn, x * z * C + y * sn], [y * x * C + z * sn, c + y * y * C, y * z * C - x * sn], [z * x * C - y * sn, z * y * C + x * sn, c + z * z * C]]; }
    else M = [[1, -w[2] * dt, w[1] * dt], [w[2] * dt, 1, -w[0] * dt], [-w[1] * dt, w[0] * dt, 1]];
    s.R = this.mul(s.R, M); s.steps++; s.time += dt;
    if (api.p.every && s.steps % api.p.every === 0) s.R = this.ortho(s.R);
  },
  update(dt, api, s) {
    if (!s.R) this.reset(api, s);
    const per = Math.max(1, Math.round(2 / (api.p.dt / 1000) * dt));    // about 2 simulated seconds per real second
    for (let i = 0; i < per && s.time < 20; i++) { this.step(api, s); const d = this.dev(s.R); s.max = Math.max(s.max, d); }
    s.hist.push([s.time, Math.log10(Math.max(1e-16, this.dev(s.R)))]);
    if (s.time >= 20) {
      api.stop();
      const p = api.p;
      if (api.scene === "ctrl" && !p.exact && !p.every && this.dev(s.R) > 0.01) api.done("drift");
      if (api.scene === "ctrl" && p.exact && !p.every && s.max < 1e-9) api.done("exact");
      if (api.scene === "imu" && !p.exact && p.every && p.every <= 20 && s.max < 5e-3) api.done("fix");
    }
  },
  readouts(api, s) {
    if (!s.R) this.reset(api, s);
    const len = [0, 1, 2].map((j) => Math.hypot(s.R[0][j], s.R[1][j], s.R[2][j]));
    return [[["模拟时间", "simulated time"], api.fmt(s.time, 2) + " s"], [["更新次数", "updates"], String(s.steps)],
            [["RᵀR 偏离 I 的最大值", "max |RᵀR − I|"], this.dev(s.R).toExponential(2)],
            [["三根轴的长度", "axis lengths"], len.map((v) => api.fmt(v, 5)).join(", ")]];
  },
  draw(api, s) {
    if (!s.R) this.reset(api, s);
    const { w, h } = api, k = Math.min(w * 0.2, h * 0.32), cx = w * 0.22, cy = h * 0.58, az = -0.6, el = 0.4;
    const P = ([x, y, z]) => { const u = x * Math.cos(az) - y * Math.sin(az), v = x * Math.sin(az) + y * Math.cos(az); return [cx + k * u, cy - k * (z * Math.cos(el) - v * Math.sin(el))]; };
    const cols = [api.css("--red"), api.css("--green"), api.css("--accent")];
    for (let j = 0; j < 3; j++) api.arrow(cx, cy, ...P([s.R[0][j], s.R[1][j], s.R[2][j]]), cols[j], 3);
    api.plot(w * 0.46, 18, w * 0.5, h - 60, [{ pts: s.hist, color: api.css("--accent") }],
      { xmin: 0, xmax: 20, ymin: -16, ymax: 0, xlabel: "t / s", ylabel: "lg |RᵀR − I|" });
  },
});
