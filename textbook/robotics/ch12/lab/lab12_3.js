// 实验 12.3 指数积公式与三维模型对照（配 12.3 节）。
// 末端位置算两遍：一遍按表 12.1.1 / 表 12.3.2 用指数积公式（本程序自己算），一遍从三维模型读出（三维引擎逐个连杆累乘）。
// UR5e 的末端取法兰盘中心；模型 base 连杆相对 {s} 绕 z 转了 180°，读数 (x, y, z) 换成 (−x, −y, z)。
WQ.lab({
  title: ["实验 12.3 指数积公式与三维模型对照", "Lab 12.3 The PoE formula against the 3D model"],
  goal: ["拖动关节，比较指数积公式算出的末端位置与三维模型的读数，二者之差应在 10⁻⁶ m 以下。",
         "Drag the joints and compare the PoE tool position with the 3D model's reading; they should agree to better than 10⁻⁶ m."],
  view: "3d",
  models: ["B-ARM-UR5E", "B-SCA-WQ4"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e", "UR5e"],
      problem: { title: ["机器人问题：示教器显示的末端坐标从哪里来", "Robot problem: where the pendant's tool coordinates come from"],
                 text: ["控制器每个周期把六个关节角代入指数积公式，算出法兰盘中心的位置。",
                        "Every cycle the controller puts the six joint angles into the PoE formula to get the flange position."] } },
    { id: "scara", robot: true, name: ["SCARA", "SCARA"],
      problem: { title: ["机器人问题：分拣线上的 SCARA", "Robot problem: a SCARA on a sorting line"],
                 text: ["三个竖直转轴决定水平位置和工具转向，丝杠决定高度。移动关节在指数积中写成 (0, v)。",
                        "Three vertical axes set the horizontal position and tool heading; the screw sets the height. The prismatic joint enters the PoE as (0, v)."] } },
  ],
  params: [
    { id: "j1", name: ["关节 1 θ₁", "Joint 1 θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j2", name: ["关节 2 θ₂", "Joint 2 θ₂"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j3", name: ["关节 3 θ₃（UR5e）", "Joint 3 θ₃ (UR5e)"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "d3", name: ["关节 3 下降量 d₃（SCARA）", "Joint 3 drop d₃ (SCARA)"], min: 0, max: 150, step: 1, value: 0, unit: "mm", digits: 0 },
    { id: "j4", name: ["关节 4 θ₄", "Joint 4 θ₄"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j5", name: ["关节 5 θ₅（UR5e）", "Joint 5 θ₅ (UR5e)"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j6", name: ["关节 6 θ₆（UR5e）", "Joint 6 θ₆ (UR5e)"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["设置算例 12.3.1 的关节角 (30°, −60°, 90°, −120°, −90°, 45°)，读出末端位置，与书中比较。", "Set Example 12.3.1, (30°, −60°, 90°, −120°, −90°, 45°), and compare the tool position with the book."],
      demo: { scene: "ur", set: { j1: 30, j2: -60, j3: 90, j4: -120, j5: -90, j6: 45 }, press: [], wait: 1 } },
    { id: "sc", robot: true, text: ["切换到 SCARA，设置算例 12.3.2：(40°, −70°, 120 mm, 90°)，验证末端高度和水平位置。", "Switch to SCARA, set Example 12.3.2: (40°, −70°, 120 mm, 90°), and check height and horizontal position."],
      demo: { scene: "scara", set: { j1: 40, j2: -70, d3: 120, j4: 90 }, press: [], wait: 1 } },
    { id: "any", text: ["在 UR5e 上任意转动至少三个关节，观察两组坐标之差始终小于 10⁻⁶ m。", "On the UR5e turn at least three joints anyhow: the two positions always differ by less than 10⁻⁶ m."],
      demo: { scene: "ur", set: { j1: -50, j2: -110, j3: 70, j4: 20, j5: 35, j6: -15 }, press: [], wait: 1 } },
  ],
  think: ["两种算法的输入不同：一种是按尺寸写的旋量轴表，一种是模型文件的连杆矩阵。二者之差只有 10⁻¹⁵ m 量级，说明了什么？如果改用厂家 DH 参数，差别为什么变成毫米级？",
          "The two methods use different inputs (screw table vs model link matrices) yet agree to 10⁻¹⁵ m. What does that show? Why does the gap become millimetres with the maker's DH parameters?"],

  // ---- 指数积公式（与程序 12.3.1 相同的旋量轴表）
  exp6(S, t) {
    const [wx, wy, wz, vx, vy, vz] = S, n = Math.hypot(wx, wy, wz);
    if (n < 1e-12) return [[1, 0, 0, vx * t], [0, 1, 0, vy * t], [0, 0, 1, vz * t], [0, 0, 0, 1]];
    const K = [[0, -wz, wy], [wz, 0, -wx], [-wy, wx, 0]], K2 = this.m3(K, K), c = Math.cos(t), s = Math.sin(t);
    const R = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + s * K[i][j] + (1 - c) * K2[i][j]));
    const G = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? t : 0) + (1 - c) * K[i][j] + (t - s) * K2[i][j]));
    const p = [0, 1, 2].map((i) => G[i][0] * vx + G[i][1] * vy + G[i][2] * vz);
    return [[...R[0], p[0]], [...R[1], p[1]], [...R[2], p[2]], [0, 0, 0, 1]];
  },
  m3(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  m4(A, B) { return A.map((r) => [0, 1, 2, 3].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j] + r[3] * B[3][j])); },
  rev(w, q) { return [w[0], w[1], w[2], -(w[1] * q[2] - w[2] * q[1]), -(w[2] * q[0] - w[0] * q[2]), -(w[0] * q[1] - w[1] * q[0])]; },
  ur() {
    const H1 = 0.163, W1 = 0.138, L1 = 0.425, W2 = 0.131, L2 = 0.392, W3 = 0.127, H2 = 0.1, W4 = 0.1, yd = [0, -1, 0];
    const S = [this.rev([0, 0, 1], [0, 0, H1]), this.rev(yd, [0, -W1, H1]), this.rev(yd, [-L1, -W1 + W2, H1]), this.rev(yd, [-L1 - L2, -W1 + W2, H1]),
               this.rev([0, 0, -1], [-L1 - L2, -W1 + W2 - W3, H1]), this.rev(yd, [-L1 - L2, -W1 + W2 - W3, H1 - H2])];
    const M = [[1, 0, 0, -L1 - L2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]];
    return { S, M };
  },
  scara() {
    const S = [this.rev([0, 0, 1], [0, 0, 0.4]), this.rev([0, 0, 1], [0.35, 0, 0.4]), [0, 0, 0, 0, 0, -1], this.rev([0, 0, 1], [0.6, 0, 0.242])];
    const M = [[1, 0, 0, 0.6], [0, 1, 0, 0], [0, 0, 1, 0.242], [0, 0, 0, 1]];
    return { S, M };
  },
  q(api) {
    const d = Math.PI / 180;
    return api.scene === "ur" ? [api.p.j1, api.p.j2, api.p.j3, api.p.j4, api.p.j5, api.p.j6].map((x) => x * d)
                              : [api.p.j1 * d, api.p.j2 * d, api.p.d3 / 1000, api.p.j4 * d];
  },
  poe(api) {
    const { S, M } = api.scene === "ur" ? this.ur() : this.scara(), th = this.q(api);
    let T = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
    S.forEach((s, i) => { T = this.m4(T, this.exp6(s, th[i])); });
    return this.m4(T, M);
  },
  model(api) {
    const th = this.q(api);
    if (api.scene === "ur") {
      const arm = api.m["B-ARM-UR5E"], names = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"];
      const o = {}; names.forEach((n, i) => { o[n] = th[i]; }); arm.set(o);
      const [x, y, z] = arm.local("wrist_3_link", [0, 0.1, 0]);
      return [-x, -y, z];
    }
    const sc = api.m["B-SCA-WQ4"];
    sc.set({ J1: th[0], J2: th[1], J3: th[2], J4: th[3] });
    return sc.local("tool", [0, 0, 0]);
  },

  setup3d(api, keep) {
    keep.shown = null;
    api.m["B-ARM-UR5E"].nodes.root.add(new api.three.AxesHelper(0.15));   // 基座坐标系 {s}
    api.m["B-SCA-WQ4"].nodes.root.add(new api.three.AxesHelper(0.15));
  },
  reset(api, s) {},
  readouts(api, s) {
    if (!api.m["B-ARM-UR5E"] || !api.m["B-SCA-WQ4"]) return [];
    const T = this.poe(api), p = [T[0][3], T[1][3], T[2][3]], m = this.model(api);
    const gap = Math.hypot(p[0] - m[0], p[1] - m[1], p[2] - m[2]);
    const close = (a, b) => Math.abs(a - b) < 0.5;
    if (api.scene === "ur" && [[api.p.j1, 30], [api.p.j2, -60], [api.p.j3, 90], [api.p.j4, -120], [api.p.j5, -90], [api.p.j6, 45]].every(([a, b]) => close(a, b))) api.done("ex");
    if (api.scene === "scara" && close(api.p.j1, 40) && close(api.p.j2, -70) && close(api.p.d3, 120) && close(api.p.j4, 90)) api.done("sc");
    const moved = [api.p.j1, api.p.j2, api.p.j3, api.p.j4, api.p.j5, api.p.j6].filter((x) => x !== 0).length;
    if (api.scene === "ur" && moved >= 3 && gap < 1e-6) api.done("any");
    const v = (a) => `(${api.fmt(a[0], 4)}, ${api.fmt(a[1], 4)}, ${api.fmt(a[2], 4)}) m`;
    return [[["指数积公式算出的末端", "tool by the PoE formula"], v(p)], [["三维模型读出的末端", "tool read from the 3D model"], v(m)],
            [["二者之差", "difference"], gap.toExponential(1) + " m"],
            api.scene === "ur" ? [["末端 z 轴方向（指数积）", "tool z axis (PoE)"], `(${api.fmt(T[0][2], 3)}, ${api.fmt(T[1][2], 3)}, ${api.fmt(T[2][2], 3)})`]
                               : [["工具转向（指数积）", "tool heading (PoE)"], api.fmt(Math.atan2(T[1][0], T[0][0]) * 180 / Math.PI, 1) + "°"]];
  },
  draw(api, s) {
    const ur = api.m["B-ARM-UR5E"], sc = api.m["B-SCA-WQ4"];
    ur.holder.visible = api.scene === "ur";
    sc.holder.visible = api.scene === "scara";
    if (api.keep.shown !== api.scene) { api.keep.shown = api.scene; api.view(35, 22, 0.85, api.scene === "ur" ? ur : sc); }
    this.model(api);
  },
});
