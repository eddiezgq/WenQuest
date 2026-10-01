// 实验 4.5 万向节锁（配 4.5 节）。调偏航、俯仰、横滚，看旋转矩阵和由矩阵反求的欧拉角。
WQ.lab({
  title: ["实验 4.5 万向节锁", "Lab 4.5 Gimbal lock"],
  goal: ["俯仰调到 90° 时，偏航和横滚只剩它们的差起作用；在 90° 附近，姿态的微小变化会使反求的欧拉角大幅跳变。",
         "At 90° pitch only yaw − roll matters; near 90°, a tiny change of attitude makes the recovered angles jump."],
  scenes: [
    { id: "plane", robot: true, name: ["飞机姿态", "Aircraft attitude"],
      problem: { title: ["机器人问题：无人机机头竖直向上", "Robot problem: a drone pointing straight up"],
                 text: ["飞控用 ZYX 欧拉角显示姿态。机头竖直向上（俯仰 90°）时，显示的偏航和横滚会怎样？", "The flight controller shows ZYX angles. What happens to yaw and roll when the nose points straight up?"] } },
    { id: "near", name: ["接近 90° 时", "Near 90°"],
      problem: { title: ["生活中的例子：陀螺仪读数突变", "Everyday example: a gyro reading that jumps"],
                 text: ["俯仰 89° 附近，物体只绕地面 x 轴多转了 0.5°，读数却变了很多。", "Near 89° pitch, a 0.5° extra turn about the ground x axis changes the readings a lot."] } },
  ],
  params: [
    { id: "yaw", name: ["偏航 ψ", "Yaw ψ"], min: -180, max: 180, step: 1, value: 10, unit: "°", digits: 0 },
    { id: "pitch", name: ["俯仰 θ", "Pitch θ"], min: -90, max: 90, step: 0.5, value: 30, unit: "°", digits: 1 },
    { id: "roll", name: ["横滚 φ", "Roll φ"], min: -180, max: 180, step: 1, value: 20, unit: "°", digits: 0 },
    { id: "extra", name: ["再绕地面 x 轴转", "Extra turn about ground x"], min: 0, max: 2, step: 0.1, value: 0, unit: "°", digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "lock", robot: true, text: ["把俯仰调到 90°，偏航 40°、横滚 10°：记下旋转矩阵。", "Pitch 90°, yaw 40°, roll 10°: note the matrix."],
      demo: { scene: "plane", set: { pitch: 90, yaw: 40, roll: 10, extra: 0 }, press: [] } },
    { id: "same", robot: true, text: ["保持俯仰 90°，改成偏航 70°、横滚 40°：矩阵不变。", "Keep 90° pitch, set yaw 70°, roll 40°: the same matrix."],
      demo: { scene: "plane", set: { pitch: 90, yaw: 70, roll: 40, extra: 0 }, press: [] } },
    { id: "jump", text: ["俯仰 89.5°，再绕地面 x 轴多转 0.5°：反求的偏航跳变超过 10°。", "Pitch 89.5°, extra 0.5° about ground x: recovered yaw jumps by more than 10°."],
      demo: { scene: "near", set: { pitch: 89.5, yaw: 10, roll: 20, extra: 0.5 }, press: [] } },
  ],
  think: ["为什么俯仰 90° 时只剩 ψ − φ 起作用？在图上看，哪两根转轴重合了？", "Why does only ψ − φ matter at 90° pitch? Which two axes coincide?"],

  reset(api, s) {},
  R(api) {
    const d = Math.PI / 180, ps = api.p.yaw * d, th = api.p.pitch * d, ph = api.p.roll * d, e = api.p.extra * d;
    const Rz = [[Math.cos(ps), -Math.sin(ps), 0], [Math.sin(ps), Math.cos(ps), 0], [0, 0, 1]];
    const Ry = [[Math.cos(th), 0, Math.sin(th)], [0, 1, 0], [-Math.sin(th), 0, Math.cos(th)]];
    const Rx = (a) => [[1, 0, 0], [0, Math.cos(a), -Math.sin(a)], [0, Math.sin(a), Math.cos(a)]];
    const mul = (A, B) => A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j]));
    return mul(Rx(e), mul(Rz, mul(Ry, Rx(ph))));
  },
  angles(R) {
    const g = 180 / Math.PI;
    return [Math.atan2(R[1][0], R[0][0]) * g, Math.atan2(-R[2][0], Math.hypot(R[0][0], R[1][0])) * g, Math.atan2(R[2][1], R[2][2]) * g];
  },
  readouts(api, s) {
    const R = this.R(api), [ps, th, ph] = this.angles(R);
    const f = (r) => r.map((v) => api.fmt(Math.abs(v) < 5e-4 ? 0 : v, 3)).join("  ");
    const key = R.flat().map((v) => v.toFixed(3)).join(",");
    if (api.scene === "plane" && api.p.pitch === 90 && api.p.extra === 0) {
      if (api.p.yaw === 40 && api.p.roll === 10) { s.lockKey = key; api.done("lock"); }
      if (s.lockKey && key === s.lockKey && !(api.p.yaw === 40 && api.p.roll === 10)) api.done("same");
      if (api.p.yaw - api.p.roll === 30 && !(api.p.yaw === 40 && api.p.roll === 10)) api.done("same");
    }
    let jump = 0;
    if (api.p.extra > 0) { const base = this.angles(this.R({ p: Object.assign({}, api.p, { extra: 0 }) })); jump = Math.abs(ps - base[0]); }
    if (api.scene === "near" && api.p.extra > 0 && jump > 10) api.done("jump");
    return [[["R 第 1 行", "R row 1"], f(R[0])], [["第 2 行", "row 2"], f(R[1])], [["第 3 行", "row 3"], f(R[2])],
            [["由 R 反求 (ψ, θ, φ)", "recovered (ψ, θ, φ)"], `${api.fmt(ps, 1)}°, ${api.fmt(th, 1)}°, ${api.fmt(ph, 1)}°`],
            [["反求的偏航变化", "change of recovered yaw"], api.p.extra > 0 ? api.fmt(jump, 1) + "°" : "—"]];
  },
  draw(api, s) {
    const { w, h } = api, cx = w / 2, cy = h * 0.55, k = Math.min(w, h) * 0.34, az = -0.7, el = 0.38;
    const P = ([x, y, z]) => { const u = x * Math.cos(az) - y * Math.sin(az), v = x * Math.sin(az) + y * Math.cos(az); return [cx + k * u, cy - k * (z * Math.cos(el) - v * Math.sin(el))]; };
    const R = this.R(api), ap = (v) => [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]);
    // aircraft: fuselage along body x, wings along body y, fin along body z
    const seg = (a, b, c, wd) => api.line(...P(ap(a)), ...P(ap(b)), c, wd);
    seg([-0.9, 0, 0], [1.0, 0, 0], api.css("--ink"), 5);
    seg([0.1, -0.9, 0], [0.1, 0.9, 0], api.css("--accent"), 4);
    seg([-0.8, -0.35, 0], [-0.8, 0.35, 0], api.css("--accent"), 3);
    seg([-0.8, 0, 0], [-0.8, 0, 0.35], api.css("--amber"), 3);
    api.circle(...P(ap([1.0, 0, 0])), 5, api.css("--red"));
    // the first (yaw) axis: ground z; the third (roll) axis: body x
    api.line(...P([0, 0, -1.2]), ...P([0, 0, 1.3]), api.css("--accent"), 1.5, [5, 4]);
    api.label(api.T("偏航轴（地面 z）", "yaw axis (ground z)"), ...P([0.05, 0, 1.35]), api.css("--accent"), 12);
    api.label(api.T("横滚轴（机体 x）", "roll axis (body x)"), ...P(ap([1.15, 0, 0])), api.css("--red"), 12);
  },
});
