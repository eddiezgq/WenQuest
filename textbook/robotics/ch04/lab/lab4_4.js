// 实验 4.4 轴角与旋转矩阵（配 4.4 节）。显示罗德里格斯公式三项各自的矩阵和它们的和。
WQ.lab({
  title: ["实验 4.4 轴角与旋转矩阵", "Lab 4.4 Axis-angle and the rotation matrix"],
  goal: ["拖动转轴和转角，看式 (4.4.5) 中 I、sin θ[ω̂]、(1 − cos θ)[ω̂]² 三项怎样合成旋转矩阵。",
         "Drag the axis and angle; see how I, sin θ[ω̂] and (1 − cos θ)[ω̂]² add up to the rotation matrix."],
  scenes: [
    { id: "tool", robot: true, name: ["绕倾斜方向转工具", "Turn the tool about a tilted axis"],
      problem: { title: ["机器人问题：绕任意方向转 15°", "Robot problem: turn 15° about any direction"],
                 text: ["示教器指令要求工具绕一个倾斜方向转一个角度，转轴不是坐标轴。", "The pendant asks for a turn about a tilted direction, not a coordinate axis."] } },
    { id: "cube", name: ["立方体沿对角线转", "A cube about its diagonal"],
      problem: { title: ["生活中的例子：魔方的对角线", "Everyday example: a cube's diagonal"],
                 text: ["把立方体沿对角线竖起来转 120°，三根轴正好轮换一次。", "Stand a cube on its diagonal and turn 120°: the three axes trade places."] } },
  ],
  params: [
    { id: "az", name: ["转轴方位角", "Axis azimuth"], min: -180, max: 180, step: 0.5, value: 0, unit: "°", digits: 1 },
    { id: "el", name: ["转轴仰角", "Axis elevation"], min: -90, max: 90, step: 0.1, value: 90, unit: "°", digits: 1 },
    { id: "ang", name: ["转角 θ", "Angle θ"], min: 0, max: 180, step: 1, value: 30, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "z", robot: true, text: ["转轴取 z 轴（仰角 90°），确认结果就是 Rot(ẑ, θ)。", "Axis = z (elevation 90°): the result is Rot(ẑ, θ)."],
      demo: { scene: "tool", set: { el: 90, ang: 30 }, press: [] } },
    { id: "perm", text: ["找到使结果只含 0 和 1 的轴和角：(1,1,1) 方向转 120°。", "Find the axis and angle giving only 0s and 1s: (1,1,1), 120°."],
      demo: { scene: "cube", set: { az: 45, el: 35.3, ang: 120 }, press: [] } },
    { id: "pi", text: ["把转角调到 180°，观察 R − Rᵀ 为什么变成零。", "Set 180°: see why R − Rᵀ becomes zero."],
      demo: { scene: "tool", set: { ang: 180 }, press: [] } },
  ],
  think: ["θ = 180° 时，为什么不能再用 (R − Rᵀ)/(2 sin θ) 求转轴？", "At θ = 180°, why can't (R − Rᵀ)/(2 sin θ) give the axis?"],

  reset(api, s) {},
  parts(api) {
    const d = Math.PI / 180, a = api.p.az * d, e = api.p.el * d, t = api.p.ang * d;
    const w = [Math.cos(e) * Math.cos(a), Math.cos(e) * Math.sin(a), Math.sin(e)];
    const K = [[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]];
    const K2 = K.map((r) => [0, 1, 2].map((j) => r[0] * K[0][j] + r[1] * K[1][j] + r[2] * K[2][j]));
    const R = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + Math.sin(t) * K[i][j] + (1 - Math.cos(t)) * K2[i][j]));
    return { w, K, R, t };
  },
  readouts(api, s) {
    const { w, R, t } = this.parts(api);
    const f = (M) => M.map((r) => r.map((v) => api.fmt(Math.abs(v) < 5e-4 ? 0 : v, 3)).join(" ")).join(" | ");
    const near = (A) => A.every((r, i) => r.every((v, j) => Math.abs(v - R[i][j]) < 5e-3));
    const c = Math.cos(t), sn = Math.sin(t);
    if (api.scene === "tool" && w[2] > 0.9999 && near([[c, -sn, 0], [sn, c, 0], [0, 0, 1]])) api.done("z");
    if (api.scene === "cube" && near([[0, 0, 1], [1, 0, 0], [0, 1, 0]])) api.done("perm");
    if (api.scene === "tool" && api.p.ang >= 179.5) api.done("pi");
    const asym = [0, 1, 2].map((i) => [0, 1, 2].map((j) => R[i][j] - R[j][i]));
    return [[["转轴 ω̂", "axis ω̂"], `(${api.fmt(w[0], 3)}, ${api.fmt(w[1], 3)}, ${api.fmt(w[2], 3)})`],
            [["R（按行）", "R (rows)"], f(R)],
            [["R − Rᵀ（按行）", "R − Rᵀ (rows)"], f(asym)]];
  },
  draw(api, s) {
    const { w, h } = api, cx = w / 2, cy = h * 0.58, k = Math.min(w, h) * 0.32, az = -0.6, el = 0.42;
    const P = ([x, y, z]) => { const u = x * Math.cos(az) - y * Math.sin(az), v = x * Math.sin(az) + y * Math.cos(az); return [cx + k * u, cy - k * (z * Math.cos(el) - v * Math.sin(el))]; };
    const { w: ax, R } = this.parts(api);
    const ap = (v) => [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]);
    const cols = [api.css("--red"), api.css("--green"), api.css("--accent")];
    for (let i = 0; i < 3; i++) { const e = [0, 0, 0]; e[i] = 1; api.line(cx, cy, ...P(e), cols[i], 1, [4, 4]); api.arrow(cx, cy, ...P(ap(e)), cols[i], 3); }
    const s3 = 0.5, V = []; for (const a of [-1, 1]) for (const b of [-1, 1]) for (const c of [-1, 1]) V.push(P(ap([a * s3, b * s3, c * s3])));
    [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7], [0, 4], [1, 5], [2, 6], [3, 7]].forEach(([i, j]) => api.line(...V[i], ...V[j], api.css("--muted"), 1.2));
    const a1 = P(ax.map((v) => 1.3 * v)); api.arrow(...P(ax.map((v) => -1.1 * v)), ...a1, api.css("--amber"), 2.5);
    api.label("ω̂", a1[0] + 6, a1[1], api.css("--amber"), 15);
  },
});
