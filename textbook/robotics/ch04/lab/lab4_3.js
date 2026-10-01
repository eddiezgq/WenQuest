// 实验 4.3 找出看不见的转轴（配 4.3 节）。目标姿态是算例 4.3.1 的 R；学生调转轴方向和转角，一次转到目标。
WQ.lab({
  title: ["实验 4.3 找出看不见的转轴", "Lab 4.3 Find the hidden axis"],
  goal: ["调节转轴方向和转角，用一次转动把物体从起始姿态转到目标姿态。", "Set an axis and an angle so that one turn takes the object to the target pose."],
  scenes: [
    { id: "two", robot: true, name: ["两步转动的结果", "Result of two turns"],
      problem: { title: ["机器人问题：一步到位", "Robot problem: in one move"],
                 text: ["末端先绕 z 转 30°、再绕自身 x 轴转 45°。能否绕一根轴一次转到？", "The tool turned 30° about z, then 45° about its own x. Can one turn about one axis do it?"] } },
    { id: "half", name: ["转了半圈", "Half a turn"],
      problem: { title: ["生活中的例子：把杯子倒过来", "Everyday example: turning a cup upside down"],
                 text: ["目标姿态是绕 (0.6, 0.8, 0) 转 180°。找到一根轴后，试试反方向的轴是否也对。", "Target: 180° about (0.6, 0.8, 0). Once found, try the opposite axis too."] } },
  ],
  params: [
    { id: "az", name: ["转轴方位角", "Axis azimuth"], min: -180, max: 180, step: 0.5, value: 0, unit: "°", digits: 1 },
    { id: "el", name: ["转轴仰角", "Axis elevation"], min: -90, max: 90, step: 0.5, value: 0, unit: "°", digits: 1 },
    { id: "ang", name: ["转角", "Angle"], min: 0, max: 180, step: 0.5, value: 0, unit: "°", digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "found", robot: true, text: ["让一次转动与目标姿态相差不到 1°。", "Get within 1° of the target with one turn."],
      demo: { scene: "two", set: { az: 15, el: 32, ang: 53.5 }, press: [] } },
    { id: "trace", robot: true, text: ["读出目标的迹，用 tr R = 1 + 2cos θ 求转角，与你找到的转角比较。", "Read the target's trace, compute θ from tr R = 1 + 2cos θ, compare."],
      demo: { scene: "two", set: { az: 15, el: 32, ang: 53.5 }, press: [] } },
    { id: "pip", text: ["半圈的情形：用 (0.6, 0.8, 0) 方向转 180°，与目标重合。", "Half turn: 180° about (0.6, 0.8, 0) gives the target."],
      demo: { scene: "half", set: { az: 53, el: 0, ang: 180 }, press: [] } },
    { id: "pim", text: ["再用相反的方向 (−0.6, −0.8, 0) 转 180°，也与目标重合。", "Then 180° about the opposite (−0.6, −0.8, 0): also the target."],
      demo: { scene: "half", set: { az: -127, el: 0, ang: 180 }, press: [] } },
  ],
  think: ["为什么转角为 180° 时，转轴的方向有两种选法？", "Why does a 180° turn allow two axis directions?"],

  reset(api, s) {},
  target(api) {
    const d = Math.PI / 180;
    if (api.scene === "half") return this.rod([0.6, 0.8, 0], Math.PI);
    const Rz = this.rod([0, 0, 1], 30 * d), Rx = this.rod([1, 0, 0], 45 * d);
    return this.mul(Rz, Rx);
  },
  rod(w, t) {
    const n = Math.hypot(...w), [x, y, z] = w.map((v) => v / n), c = Math.cos(t), s = Math.sin(t), C = 1 - c;
    return [[c + x * x * C, x * y * C - z * s, x * z * C + y * s], [y * x * C + z * s, c + y * y * C, y * z * C - x * s], [z * x * C - y * s, z * y * C + x * s, c + z * z * C]];
  },
  mul(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  axis(api) { const d = Math.PI / 180, a = api.p.az * d, e = api.p.el * d; return [Math.cos(e) * Math.cos(a), Math.cos(e) * Math.sin(a), Math.sin(e)]; },
  err(A, B) { const t = [0, 1, 2].reduce((acc, i) => acc + A[0][i] * B[0][i] + A[1][i] * B[1][i] + A[2][i] * B[2][i], 0);
    return Math.acos(Math.max(-1, Math.min(1, (t - 1) / 2))) * 180 / Math.PI; },
  readouts(api, s) {
    const T = this.target(api), w = this.axis(api), R = this.rod(w, api.p.ang * Math.PI / 180);
    const e = this.err(T, R), tr = T[0][0] + T[1][1] + T[2][2];
    if (api.scene === "two" && e < 1) { api.done("found"); api.done("trace"); }
    if (api.scene === "half" && e < 1 && api.p.ang > 179) api.done(0.6 * w[0] + 0.8 * w[1] > 0 ? "pip" : "pim");
    return [[["目标 R 的迹", "trace of target R"], api.fmt(tr, 4)],
            [["由迹算出的转角", "angle from the trace"], api.fmt(Math.acos(Math.max(-1, Math.min(1, (tr - 1) / 2))) * 180 / Math.PI, 2) + "°"],
            [["你的转轴", "your axis"], `(${api.fmt(w[0], 3)}, ${api.fmt(w[1], 3)}, ${api.fmt(w[2], 3)})`],
            [["与目标相差", "off the target by"], api.fmt(e, 2) + "°"]];
  },
  draw(api, s) {
    const { w, h } = api, cx = w / 2, cy = h * 0.56, k = Math.min(w, h) * 0.33, az = -0.6, el = 0.4;
    const P = ([x, y, z]) => { const u = x * Math.cos(az) - y * Math.sin(az), v = x * Math.sin(az) + y * Math.cos(az); return [cx + k * u, cy - k * (z * Math.cos(el) - v * Math.sin(el))]; };
    const ap = (R, v) => [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]);
    const box = (R, color, width) => { const V = []; for (const a of [-1, 1]) for (const b of [-1, 1]) for (const c of [-1, 1]) V.push(P(ap(R, [a * 0.55, b * 0.35, c * 0.2])));
      [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7], [0, 4], [1, 5], [2, 6], [3, 7]].forEach(([i, j]) => api.line(...V[i], ...V[j], color, width)); };
    const T = this.target(api), ax = this.axis(api), R = this.rod(ax, api.p.ang * Math.PI / 180);
    box(T, api.css("--muted"), 1.5);
    box(R, api.css("--accent"), 2.5);
    const a0 = P(ax.map((v) => -1.3 * v)), a1 = P(ax.map((v) => 1.3 * v));
    api.arrow(...a0, ...a1, api.css("--amber"), 2.5);
    api.label("ω̂", a1[0] + 6, a1[1], api.css("--amber"), 15);
    api.label(api.T("灰：目标　蓝：你的一次转动", "grey: target   blue: your single turn"), 12, 18, api.css("--muted"), 12);
  },
});
