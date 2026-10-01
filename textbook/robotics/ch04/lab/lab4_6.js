// 实验 4.6 四元数与转动（配 4.6 节）。转角可到 720°；q 与 −q 表示同一姿态。
WQ.lab({
  title: ["实验 4.6 四元数与转动", "Lab 4.6 Quaternions and rotation"],
  goal: ["转角连续增加到 720°：旋转矩阵每转一圈复原一次，四元数要转两圈才复原。", "Turn up to 720°: the matrix repeats every turn, the quaternion only every two turns."],
  scenes: [
    { id: "drone", robot: true, name: ["无人机绕竖直轴转", "Drone yawing"],
      problem: { title: ["机器人问题：飞控里的四元数", "Robot problem: quaternions in a flight controller"],
                 text: ["飞控用四元数保存姿态。无人机原地转一圈，姿态回到原样，四元数却变成了 −q。", "The controller stores attitude as a quaternion. After one full yaw turn the attitude is back, but q has become −q."] } },
    { id: "plate", name: ["盘子把戏", "The plate trick"],
      problem: { title: ["生活中的例子：手托盘子转两圈", "Everyday example: carrying a plate round twice"],
                 text: ["手托盘子转一圈，胳膊拧着；再转一圈，胳膊复原。", "One turn twists the arm; a second turn untwists it."] } },
  ],
  params: [
    { id: "az", name: ["转轴方位角", "Axis azimuth"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "el", name: ["转轴仰角", "Axis elevation"], min: -90, max: 90, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "ang", name: ["转角 θ", "Angle θ"], min: 0, max: 720, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "neg", name: ["用 −q 代替 q（0 否 / 1 是）", "Use −q instead of q (0/1)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "one", robot: true, text: ["转到 360°：姿态复原，q₀ = −1。", "Turn to 360°: attitude restored, q₀ = −1."],
      demo: { scene: "drone", set: { ang: 360, neg: 0 }, press: [] } },
    { id: "two", robot: true, text: ["转到 720°：q₀ 才回到 +1。", "Turn to 720°: only now q₀ = +1."],
      demo: { scene: "drone", set: { ang: 720, neg: 0 }, press: [] } },
    { id: "neg", text: ["在任一转角下把 q 换成 −q：画面中的姿态不变。", "At any angle switch to −q: the picture does not change."],
      demo: { scene: "plate", set: { ang: 75, neg: 1 }, press: [] } },
  ],
  think: ["为什么转一圈后 q₀ = −1？这与式 (4.6.5) 中的半角有什么关系？", "Why is q₀ = −1 after one turn? What does the half angle in (4.6.5) have to do with it?"],

  reset(api, s) {},
  q(api) {
    const d = Math.PI / 180, a = api.p.az * d, e = api.p.el * d, t = api.p.ang * d, sg = api.p.neg ? -1 : 1;
    const w = [Math.cos(e) * Math.cos(a), Math.cos(e) * Math.sin(a), Math.sin(e)];
    return [Math.cos(t / 2), ...w.map((v) => v * Math.sin(t / 2))].map((v) => sg * v);
  },
  R(q) {
    const [a, b, c, d] = q;
    return [[1 - 2 * (c * c + d * d), 2 * (b * c - a * d), 2 * (b * d + a * c)], [2 * (b * c + a * d), 1 - 2 * (b * b + d * d), 2 * (c * d - a * b)], [2 * (b * d - a * c), 2 * (c * d + a * b), 1 - 2 * (b * b + c * c)]];
  },
  readouts(api, s) {
    const q = this.q(api), R = this.R(q);
    if (api.scene === "drone" && api.p.ang === 360 && !api.p.neg) api.done("one");
    if (api.scene === "drone" && api.p.ang === 720 && !api.p.neg) api.done("two");
    if (api.scene === "plate" && api.p.neg && api.p.ang % 360 !== 0) api.done("neg");
    const z = (v) => api.fmt(Math.abs(v) < 5e-4 ? 0 : v, 3);
    return [[["四元数 q = (q₀, q₁, q₂, q₃)", "quaternion q"], q.map(z).join(", ")],
            [["R 第 1 行", "R row 1"], R[0].map(z).join("  ")], [["第 2 行", "row 2"], R[1].map(z).join("  ")], [["第 3 行", "row 3"], R[2].map(z).join("  ")]];
  },
  draw(api, s) {
    const { w, h } = api, k = Math.min(w, h) * 0.3, cx = w * 0.3, cy = h * 0.55, az = -0.6, el = 0.4;
    const P = ([x, y, z]) => { const u = x * Math.cos(az) - y * Math.sin(az), v = x * Math.sin(az) + y * Math.cos(az); return [cx + k * u, cy - k * (z * Math.cos(el) - v * Math.sin(el))]; };
    const R = this.R(this.q(api)), ap = (v) => [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]);
    const arms = [[1, 1, 0], [1, -1, 0], [-1, 1, 0], [-1, -1, 0]].map((v) => v.map((x) => x * 0.5));
    arms.forEach((a) => { api.line(...P([0, 0, 0]), ...P(ap(a)), api.css("--ink"), 4); api.circle(...P(ap(a)), 12, null, api.css("--accent")); });
    api.arrow(...P([0, 0, 0]), ...P(ap([0.8, 0, 0])), api.css("--red"), 3);
    // q0 against the angle, 0..720°
    const px = w * 0.58, pw = w * 0.38, py = h * 0.15, ph = h * 0.7;
    const pts = [], rr = []; for (let a = 0; a <= 720; a += 6) { pts.push([a, Math.cos(a * Math.PI / 360)]); }
    for (let a = 0; a <= 720; a += 6) rr.push([a, Math.cos(a * Math.PI / 180)]);
    const ax = api.plot(px, py, pw, ph, [{ pts: rr, color: api.css("--accent") }, { pts, color: api.css("--amber") }],
      { xmin: 0, xmax: 720, ymin: -1.1, ymax: 1.1, xlabel: "θ / °", ylabel: "q₀ (amber), cos θ (blue)" });
    const q0 = this.q(api)[0];
    api.circle(ax.X(api.p.ang), ax.Y(q0), 5, api.css("--amber"), api.css("--ink"));
  },
});
