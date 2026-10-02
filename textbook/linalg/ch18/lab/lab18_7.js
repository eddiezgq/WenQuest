// 实验 18.7 UR5e 的奇异值与奇异位形（配 18.7.3 节）。UR5e（零件库 2026.10.9 版），工作姿态
// θ = (0, −60°, θ₃, −120°, θ₅, 0)，末端点取 wrist_3_link 坐标系原点；雅可比矩阵的前三行为角速度，后三行为线速度。
WQ.lab({
  title: ["实验 18.7 UR5e 的奇异值与奇异位形", "Lab 18.7 Singular values and singularities of the UR5e"],
  goal: ["改变肘关节和腕关节的角度，看 UR5e 雅可比矩阵的六个奇异值、可操作度和条件数怎样变化，找出肘部奇异和腕部奇异。",
         "Change the elbow and wrist angles and watch the six singular values, the manipulability and the condition number of the UR5e Jacobian; find the elbow and wrist singularities."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "robot", robot: true, name: ["UR5e 工作姿态", "UR5e working pose"],
      problem: { title: ["机器人问题：离奇异位形还有多远？", "Robot problem: how far from a singularity?"],
                 text: ["接近奇异位形时，末端某个方向的运动所需的关节速度会突然变得很大。用最小奇异值 σ₆ 判断机械臂离奇异位形有多远。",
                        "Near a singularity some tool motions need huge joint speeds. Use the smallest singular value σ₆ to judge how far the arm is from one."] } },
    { id: "life", name: ["生活中的例子：伸直的手臂", "Everyday example: a straight arm"],
      problem: { title: ["生活中的例子：伸直的手臂", "Everyday example: a straight arm"],
                 text: ["把手臂伸直去够远处的东西，手就很难再往外伸。机械臂的肘部伸直时也一样：看哪个奇异值变成零。",
                        "With your arm fully stretched your hand cannot reach further. The same happens when the robot's elbow straightens: watch which singular value vanishes."] } },
  ],
  params: [
    { id: "q3", name: ["肘关节角 θ₃", "Elbow angle θ₃"], min: -20, max: 160, step: 0.5, value: 90, unit: "°", digits: 1 },
    { id: "q5", name: ["腕关节 2 的角 θ₅", "Wrist-2 angle θ₅"], min: -150, max: 30, step: 0.5, value: -90, unit: "°", digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "elbow", robot: true, text: ["让肘关节接近伸直，使 σ₆ 低于 0.01。", "Nearly straighten the elbow so that σ₆ < 0.01."], demo: { scene: "robot", set: { q3: 1, q5: -90 }, press: [], wait: 1 } },
    { id: "wrist", robot: true, text: ["转动腕关节 2，使第六个关节的转轴与第二、三、四个关节的转轴平行（σ₆ < 0.01）。", "Turn wrist 2 until the sixth axis is parallel to axes 2, 3, 4 (σ₆ < 0.01)."], demo: { scene: "robot", set: { q3: 90, q5: 0 }, press: [], wait: 1 } },
    { id: "best", robot: true, text: ["保持 θ₅ = −90°，找出 σ₆ 最大的肘关节角（σ₆ > 0.25）。", "Keep θ₅ = −90° and find the elbow angle with the largest σ₆ (σ₆ > 0.25)."], demo: { scene: "robot", set: { q3: 115, q5: -90 }, press: [], wait: 1 } },
  ],
  think: ["可操作度 w 很小时，是否一定有一个奇异值很小？反过来呢？", "If the manipulability w is small, must one singular value be small? And conversely?"],

  names: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  q(api) { const d = Math.PI / 180; return [0, -60 * d, api.p.q3 * d, -120 * d, api.p.q5 * d, 0]; },
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"];
    api.axes(arm, "wrist_3_link", 0.08);
    api.view(40, 18, 0.62);
  },
  sv(api) {
    const arm = api.m["B-ARM-UR5E"], q = this.q(api), o = {};
    this.names.forEach((n, i) => (o[n] = q[i]));
    arm.set(o);
    const p = arm.local("wrist_3_link", [0, 0, 0]);
    const cols = this.names.map((n) => {
      const j = arm.joints[n], a = arm.local(j.child, [0, 0, 0]), e = arm.local(j.child, j.axis);
      const z = [e[0] - a[0], e[1] - a[1], e[2] - a[2]], r = [p[0] - a[0], p[1] - a[1], p[2] - a[2]];
      return [z[0], z[1], z[2], z[1] * r[2] - z[2] * r[1], z[2] * r[0] - z[0] * r[2], z[0] * r[1] - z[1] * r[0]];
    });
    return api.la.svd(api.la.T(cols)).s;
  },
  readouts(api, s) {
    if (!api.m || !api.m["B-ARM-UR5E"]) return [];
    const sv = this.sv(api), w = sv.reduce((t, x) => t * x, 1), k = sv[5] > 1e-12 ? sv[0] / sv[5] : Infinity;
    if (sv[5] < 0.01 && Math.abs(api.p.q3) < 5) api.done("elbow");
    if (sv[5] < 0.01 && Math.abs(api.p.q5) < 5) api.done("wrist");
    if (sv[5] > 0.25 && Math.abs(api.p.q5 + 90) < 0.6) api.done("best");
    return [[["σ₁ … σ₆", "σ₁ … σ₆"], sv.map((x) => api.fmt(x, 4)).join(", ")],
            [["最小奇异值 σ₆", "Smallest σ₆"], api.fmt(sv[5], 5)],
            [["可操作度 w = σ₁⋯σ₆", "Manipulability w"], api.fmt(w, 5)],
            [["条件数 σ₁/σ₆", "Condition number σ₁/σ₆"], isFinite(k) && k < 1e6 ? api.fmt(k, 1) : "∞"]];
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], q = this.q(api), o = {};
    this.names.forEach((n, i) => (o[n] = q[i]));
    arm.set(o);
  },
});
