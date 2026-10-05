// 实验 8.7 Franka Panda：末端不动、肘部移动——在零空间里运动（配 8.7.4 节）。Franka Panda（零件库 2026.10.9 版），
// 准备姿态 θ = (0, −π/4, 0, −3π/4, 0, π/2, π/4)；法兰中心取 link7 坐标系 z 轴上 0.107 m 处。
// 6×7 雅可比矩阵的零空间是一维的：沿它积分得到“自运动”；作为对照，只转关节 3（不在零空间方向）时末端会动。
WQ.lab({
  title: ["实验 8.7 在零空间里运动：Panda 末端不动、肘部移动", "Lab 8.7 Moving in the null space: Panda's flange stays, the elbow moves"],
  goal: ["沿雅可比矩阵的零空间转动 Panda 的七个关节，读出法兰的漂移和肘部的位移；与只转一个关节对比；读出四个子空间的维数。",
         "Turn Panda's seven joints along the Jacobian's null space; read the flange drift and the elbow displacement; compare with turning one joint alone; read the dimensions of the four subspaces."],
  view: "3d",
  models: ["B-ARM-PANDA"],
  scenes: [
    { id: "self", robot: true, name: ["零空间运动", "Null-space motion"], hide: ["d3"],
      problem: { title: ["机器人问题：末端夹着工件不动，让肘部让开", "Robot problem: hold the part still and move the elbow aside"],
                 text: ["七个关节、六维的末端运动：J 是 6×7 矩阵，秩 6，零空间一维。关节速度落在零空间里，末端的速度就是零。",
                        "Seven joints, six-dimensional tool motion: J is 6×7 with rank 6 and a one-dimensional null space. Joint velocities in the null space give zero tool velocity."] } },
    { id: "one", robot: true, name: ["对照：只转关节 3", "Contrast: joint 3 alone"], hide: ["c"],
      problem: { title: ["对照：不在零空间里的运动", "Contrast: a motion outside the null space"],
                 text: ["只转关节 3 一个角度。J 的第 3 列不是零向量，这个关节速度不在零空间里，末端会跟着动。",
                        "Turn joint 3 alone. Column 3 of J is not zero, so this joint velocity is not in the null space and the tool moves."] } },
  ],
  params: [
    { id: "c", name: ["零空间运动量（沿路径的弧度）", "Null-space motion (rad along the path)"], min: -1.0, max: 1.0, step: 0.02, value: 0, digits: 2 },
    { id: "d3", name: ["关节 3 转角的改变", "Change of joint 3"], min: -0.4, max: 0.4, step: 0.02, value: 0, unit: "rad", digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "aside", robot: true, text: ["沿零空间正向运动，使肘部（关节 4）恰好移开 5.0 cm（误差 0.3 cm 以内）；读出哪几个关节在转动。", "Move forward along the null space until the elbow (joint 4) has moved 5.0 cm (within 0.3 cm); note which joints turn."],
      demo: { scene: "self", set: { c: 0.32 }, press: [], wait: 1 } },
    { id: "back", robot: true, text: ["向另一个方向运动，让肘部移开 8 cm 以上，同时确认法兰的位置漂移小于 0.01 mm、姿态变化小于 0.01°。", "Move the other way until the elbow has moved more than 8 cm, and check that the flange drifts less than 0.01 mm and turns less than 0.01°."],
      demo: { scene: "self", set: { c: -0.6 }, press: [], wait: 1 } },
    { id: "one", robot: true, text: ["对照场景：先读出 J 第 3 列线速度部分的长度，用它预测关节 3 转多少时法兰移动 40 mm；再调到这个角度，使法兰位移在 40 ± 2 mm 之内。", "Contrast scene: read the length of the linear part of column 3 of J, predict the joint-3 change that moves the flange 40 mm, then set it so the displacement is within 40 ± 2 mm."],
      demo: { scene: "one", set: { d3: 0.1 }, press: [], wait: 1 } },
  ],
  think: ["零空间是一维的，为什么肘部走过的是一条曲线而不是直线？（提示：J 随姿态变化，每一点的零空间方向都不同。）",
          "The null space is one-dimensional, so why does the elbow trace a curve and not a straight line? (Hint: J changes with the pose.)"],

  q0: [0, -Math.PI / 4, 0, -3 * Math.PI / 4, 0, Math.PI / 2, Math.PI / 4],
  names: ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6", "joint7"],
  pose(q) { const o = {}; this.names.forEach((n, i) => (o[n] = q[i])); return o; },
  jac(api, q) {   // 6×7: column i = (z_i, z_i × (p − o_i)) with z_i, o_i read from the model in its base frame
    const arm = api.m["B-ARM-PANDA"];
    arm.set(this.pose(q));
    const p = arm.local("link7", [0, 0, 0.107]);
    const cols = this.names.map((n) => {
      const j = arm.joints[n], o = arm.local(j.child, [0, 0, 0]), e = arm.local(j.child, j.axis);
      const z = [e[0] - o[0], e[1] - o[1], e[2] - o[2]], r = [p[0] - o[0], p[1] - o[1], p[2] - o[2]];
      return [z[0], z[1], z[2], z[1] * r[2] - z[2] * r[1], z[2] * r[0] - z[0] * r[2], z[0] * r[1] - z[1] * r[0]];
    });
    return { J: api.la.T(cols), p };
  },
  nullvec(api, J, prev) {   // the eigenvector of JᵀJ with the smallest eigenvalue, sign kept continuous
    const e = api.la.eigSym(api.la.mul(api.la.T(J), J));
    let z = e.vectors.map((r) => r[0]);
    if (prev ? api.la.dot(z, prev) < 0 : z[z.map(Math.abs).indexOf(Math.max(...z.map(Math.abs)))] < 0) z = z.map((x) => -x);
    return z;
  },
  walk(api, c) {   // integrate dθ = z ds along the null space from the ready pose (midpoint rule, steps of 0.01 rad)
    let q = this.q0.slice(), z = null;
    const n = Math.round(Math.abs(c) / 0.01), h = Math.sign(c) * 0.01;
    for (let i = 0; i < n; i++) {
      z = this.nullvec(api, this.jac(api, q).J, z);
      const qm = q.map((x, k) => x + 0.5 * h * z[k]);
      const zm = this.nullvec(api, this.jac(api, qm).J, z);
      q = q.map((x, k) => x + h * zm[k]);
    }
    return q;
  },
  frame(arm) {   // the flange's three axis directions in the base frame
    const o = arm.local("link7", [0, 0, 0]);
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]].map((a) => { const p = arm.local("link7", a); return [p[0] - o[0], p[1] - o[1], p[2] - o[2]]; });
  },
  angle(A, B) {   // rotation angle between two frames: cos φ = (tr(AᵀB) − 1)/2
    const t = A[0][0] * B[0][0] + A[0][1] * B[0][1] + A[0][2] * B[0][2] + A[1][0] * B[1][0] + A[1][1] * B[1][1] + A[1][2] * B[1][2]
      + A[2][0] * B[2][0] + A[2][1] * B[2][1] + A[2][2] * B[2][2];
    return Math.acos(Math.max(-1, Math.min(1, (t - 1) / 2)));
  },
  setup3d(api, keep) {
    const arm = api.m["B-ARM-PANDA"];
    api.axes(arm, "link7", 0.08);
    keep.trace = api.trace(0xe8913a);
    api.view(30, 18, 0.9);
  },
  reset(api, s) {
    if (!api.m || !api.m["B-ARM-PANDA"]) return;
    const arm = api.m["B-ARM-PANDA"];
    const base = this.jac(api, this.q0);
    s.p0 = base.p;
    s.j3 = Math.hypot(base.J[3][2], base.J[4][2], base.J[5][2]);
    arm.set(this.pose(this.q0));
    s.e0 = arm.local("link4", [0, 0, 0]);
    s.R0 = this.frame(arm);
    const ev = api.la.eigSym(api.la.mul(api.la.T(base.J), base.J)).values;
    s.nulldim = ev.filter((x) => x < 1e-10 * ev[ev.length - 1]).length;
    if (api.scene === "self") s.q = this.walk(api, api.p.c);
    else { s.q = this.q0.slice(); s.q[2] += api.p.d3; }
    const now = this.jac(api, s.q);
    s.drift = Math.hypot(now.p[0] - s.p0[0], now.p[1] - s.p0[1], now.p[2] - s.p0[2]);
    s.turn = this.angle(s.R0, this.frame(arm));
    const e = arm.local("link4", [0, 0, 0]);
    s.elbow = Math.hypot(e[0] - s.e0[0], e[1] - s.e0[1], e[2] - s.e0[2]);
    if (api.keep.trace) api.keep.trace.clear();
  },
  readouts(api, s) {
    if (!s.q) return [];
    const d = 180 / Math.PI, r = 7 - s.nulldim;
    if (api.scene === "self" && api.p.c > 0 && Math.abs(s.elbow - 0.05) <= 0.003) api.done("aside");
    if (api.scene === "self" && api.p.c < 0 && s.elbow > 0.08 && s.drift < 1e-5 && s.turn * 180 / Math.PI < 0.01) api.done("back");
    if (api.scene === "one" && Math.abs(s.drift - 0.04) <= 0.002) api.done("one");
    return [[["准备姿态下 J 的秩（J 为 6×7）", "Rank of J at the ready pose (J is 6×7)"], String(r)],
            [["四个子空间的维数 C(J), N(J), C(Jᵀ), N(Jᵀ)", "Dimensions C(J), N(J), C(Jᵀ), N(Jᵀ)"], [r, 7 - r, r, 6 - r].join(", ")],
            [["J 第 3 列线速度部分的长度", "Length of the linear part of column 3 of J"], api.fmt(s.j3, 3) + " m/rad"],
            [["关节角变化 / °", "Joint changes / °"], s.q.map((x, i) => api.fmt((x - this.q0[i]) * d, 1)).join(", ")],
            [["肘部（关节 4）位移", "Elbow (joint 4) displacement"], api.fmt(100 * s.elbow, 1) + " cm"],
            [["法兰位移", "Flange displacement"], api.fmt(1000 * s.drift, 3) + " mm"],
            [["法兰姿态变化", "Flange rotation"], api.fmt(s.turn * 180 / Math.PI, 4) + "°"]];
  },
  draw(api, s) {
    const arm = api.m["B-ARM-PANDA"];
    if (!arm || !s.q) return;
    arm.set(this.pose(s.q));
    if (api.keep.trace && api.scene === "self") api.keep.trace.add(arm.point("link4", [0, 0, 0]));
  },
});
