// 实验 4.2 绕固定轴与绕自身轴（配 4.2 节）。按钮让物体绕 {s} 或 {b} 的轴转 90°；旋转矩阵实时显示。
WQ.lab({
  title: ["实验 4.2 绕固定轴与绕自身轴", "Lab 4.2 Fixed axes vs body axes"],
  goal: ["用 90° 转动按钮复现书本实验，并体会“左乘绕固定轴、右乘绕自身轴”。", "Reproduce the book experiment with 90° turns; left-multiply = fixed axes, right-multiply = body axes."],
  scenes: [
    { id: "tool", robot: true, name: ["机械臂末端", "Robot tool"],
      problem: { title: ["机器人问题：示教器上的两种微动", "Robot problem: two kinds of jog on the pendant"],
                 text: ["“基坐标系微动”绕固定轴转，“工具坐标系微动”绕工具自己的轴转。同样按两下，结果可能不同。",
                        "Base-frame jog turns about fixed axes, tool-frame jog about the tool's own axes; the same two presses can end differently."] } },
    { id: "book", name: ["一本书", "A book"],
      problem: { title: ["生活中的例子：书本实验", "Everyday example: the book experiment"], text: ["算例 4.2.2：书脊朝前平放，按两种次序各转两个 90°。", "Example 4.2.2: book flat, spine forward, two 90° turns in two orders."] } },
  ],
  params: [{ id: "view", name: ["观察方向", "View azimuth"], min: -90, max: 90, step: 1, value: -35, unit: "°", digits: 0 }],
  buttons: [
    { id: "xs", name: ["绕 x_s 转 90°", "90° about x_s"] }, { id: "zs", name: ["绕 z_s 转 90°", "90° about z_s"] },
    { id: "xb", name: ["绕 x_b 转 90°", "90° about x_b"] }, { id: "zb", name: ["绕 z_b 转 90°", "90° about z_b"] },
    { id: "reset", name: ["回到起始", "Back to start"] },
  ],
  tasks: [
    { id: "A", text: ["复现做法 A：先绕 x_s、再绕 z_s 各转 90°，书脊竖直向上。", "Method A: x_s then z_s, spine ends pointing up."],
      demo: { scene: "book", set: {}, press: ["reset", "xs", "zs"] } },
    { id: "B", text: ["复现做法 B：先绕 z_s、再绕 x_s，书脊水平向左。", "Method B: z_s then x_s, spine ends pointing left."],
      demo: { scene: "book", set: {}, press: ["reset", "zs", "xs"] } },
    { id: "same", robot: true, text: ["只用绕自身轴的按钮（先 z_b 后 x_b），得到与做法 A 相同的姿态。", "Using body-axis buttons only (z_b then x_b), reach the same pose as method A."],
      demo: { scene: "tool", set: {}, press: ["reset", "zb", "xb"] } },
  ],
  think: ["为什么“绕固定轴先 x 后 z”与“绕自身轴先 z 后 x”结果相同？", "Why do 'fixed x then z' and 'body z then x' agree?"],

  reset(api, s) { s.R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; s.log = []; },
  action(id, api, s) {
    const R90 = { x: [[1, 0, 0], [0, 0, -1], [0, 1, 0]], z: [[0, -1, 0], [1, 0, 0], [0, 0, 1]] };
    const mul = (A, B) => A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j]));
    if (!s.R) this.reset(api, s);
    const M = R90[id[0]];
    s.R = id[1] === "s" ? mul(M, s.R) : mul(s.R, M);
    s.log.push(id);
  },
  readouts(api, s) {
    if (!s.R) this.reset(api, s);
    const R = s.R, eq = (A) => A.every((r, i) => r.every((v, j) => Math.abs(v - R[i][j]) < 1e-9));
    const A = [[0, 0, 1], [1, 0, 0], [0, 1, 0]], B = [[0, -1, 0], [0, 0, -1], [1, 0, 0]];
    const L = s.log.join(",");
    if (api.scene === "book" && L === "xs,zs" && eq(A)) api.done("A");
    if (api.scene === "book" && L === "zs,xs" && eq(B)) api.done("B");
    if (api.scene === "tool" && s.log.length && s.log.every((x) => x[1] === "b") && eq(A)) api.done("same");
    const row = (r) => r.map((v) => api.fmt(v, 0)).join("  ");
    return [[["旋转矩阵 第 1 行", "R row 1"], row(R[0])], [["第 2 行", "row 2"], row(R[1])], [["第 3 行", "row 3"], row(R[2])],
            [["已做的转动", "Turns so far"], L || "—"]];
  },
  draw(api, s) {
    if (!s.R) this.reset(api, s);
    const { w, h } = api, cx = w / 2, cy = h * 0.58, k = Math.min(w, h) * 0.34;
    const az = api.p.view * Math.PI / 180, el = 0.42;
    const P = ([x, y, z]) => { const u = x * Math.cos(az) - y * Math.sin(az), v = x * Math.sin(az) + y * Math.cos(az);
      return [cx + k * u, cy - k * (z * Math.cos(el) - v * Math.sin(el))]; };
    const ap = (R, v) => [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]);
    const cols = [api.css("--red"), api.css("--green"), api.css("--accent")], names = ["x", "y", "z"];
    for (let i = 0; i < 3; i++) { const e = [0, 0, 0]; e[i] = 1.25; const q = P(e); api.line(cx, cy, ...q, cols[i], 1, [4, 4]); api.label(names[i] + "_s", q[0] + 4, q[1], cols[i], 12); }
    const d = api.scene === "book" ? [0.7, 1.0, 0.18] : [0.5, 0.5, 0.5];
    const V = []; for (const a of [-1, 1]) for (const b of [-1, 1]) for (const c of [-1, 1]) V.push(P(ap(s.R, [a * d[0] / 2, b * d[1] / 2, c * d[2] / 2])));
    [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7], [0, 4], [1, 5], [2, 6], [3, 7]].forEach(([i, j]) =>
      api.line(...V[i], ...V[j], api.css("--muted"), 1.5));
    if (api.scene === "book") { api.line(...V[0], ...V[2], api.css("--amber"), 5); api.line(...V[1], ...V[3], api.css("--amber"), 5); }
    for (let i = 0; i < 3; i++) { const e = [0, 0, 0]; e[i] = 0.75; const q = P(ap(s.R, e)); api.arrow(cx, cy, ...q, cols[i], 3); api.label(names[i] + "_b", q[0] + 6, q[1] - 6, cols[i], 13); }
  },
});
