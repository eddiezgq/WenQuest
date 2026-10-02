// 实验 18.6 冗余机械臂的零空间与最小范数解（配 18.3.3、18.6.3 节）。Franka Panda（零件库 2026.10.9 版），
// 准备姿态 θ = (0, −π/4, 0, −3π/4, 0, π/2, π/4)；法兰中心取 link7 坐标系 z 轴上 0.107 m 处。
WQ.lab({
  title: ["实验 18.6 冗余机械臂的零空间与最小范数解", "Lab 18.6 Null space and minimum-norm solution of a redundant arm"],
  goal: ["沿雅可比矩阵的零空间移动 Panda 的七个关节，看法兰几乎不动而臂身在动；比较最小范数关节速度与加入零空间分量的关节速度。",
         "Move Panda's seven joints along the Jacobian's null space: the flange hardly moves while the arm does; compare the minimum-norm joint velocity with ones that add a null-space part."],
  view: "3d",
  models: ["B-ARM-PANDA"],
  scenes: [
    { id: "self", robot: true, name: ["自运动", "Self-motion"], hide: ["beta"],
      problem: { title: ["机器人问题：末端不动，让肘部让开", "Robot problem: keep the flange still, move the elbow aside"],
                 text: ["七个关节、六维的末端运动，雅可比矩阵有一维零空间。沿零空间运动时，法兰中心不动，肘部可以移开，避开旁边的障碍。",
                        "Seven joints for six-dimensional tool motion leave a one-dimensional null space. Moving along it keeps the flange still while the elbow can move out of the way."] } },
    { id: "min", robot: true, name: ["最小范数解", "Minimum-norm solution"], hide: ["c"],
      problem: { title: ["机器人问题：用最少的关节转动完成末端运动", "Robot problem: the least joint motion for a given tool motion"],
                 text: ["要求法兰以 0.1 m/s 沿基座 x 方向平动、不转动。满足要求的关节速度有无穷多个，J⁺ξ 是其中长度最小的。",
                        "The flange must translate at 0.1 m/s along the base x axis without turning. Infinitely many joint velocities do this; J⁺ξ is the shortest."] } },
  ],
  params: [
    { id: "c", name: ["零空间运动量（沿路径的弧度）", "Null-space motion (rad along the path)"], min: -1.2, max: 1.2, step: 0.02, value: 0, digits: 2 },
    { id: "beta", name: ["零空间分量 β（关节速度中 v₇ 的倍数）", "Null-space part β (multiple of v₇)"], min: -0.2, max: 0.2, step: 0.005, value: 0.05, unit: "rad/s", digits: 3 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "aside", robot: true, text: ["让肘部（关节 4）向侧面移开 10 cm 以上，法兰漂移不超过 1 mm。", "Move the elbow (joint 4) sideways by more than 10 cm with flange drift below 1 mm."],
      demo: { scene: "self", set: { c: 0.8 }, press: [], wait: 1 } },
    { id: "least", robot: true, text: ["在“最小范数解”场景找出关节速度长度最小的 β。", "In the minimum-norm scene find the β with the shortest joint velocity."],
      demo: { scene: "min", set: { beta: 0 }, press: [], wait: 1 } },
    { id: "same", text: ["取 β = 0.1，确认末端运动仍满足要求，而关节速度变长了。", "Set β = 0.1: the tool motion is still exact but the joint velocity is longer."],
      demo: { scene: "min", set: { beta: 0.1 }, press: [], wait: 1 } },
  ],
  think: ["为什么 ‖θ̇‖² 恰好等于 ‖J⁺ξ‖² + β²？", "Why is ‖θ̇‖² exactly ‖J⁺ξ‖² + β²?"],

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
    arm.set(this.pose(this.q0));
    s.e0 = arm.local("link4", [0, 0, 0]);
    if (api.scene === "self") {
      s.q = this.walk(api, api.p.c);
      const now = this.jac(api, s.q);
      s.drift = Math.hypot(now.p[0] - s.p0[0], now.p[1] - s.p0[1], now.p[2] - s.p0[2]);
      const e = arm.local("link4", [0, 0, 0]);
      s.elbow = Math.hypot(e[0] - s.e0[0], e[1] - s.e0[1]);
      s.dz = e[2] - s.e0[2];
    } else {
      const J = base.J, Jp = api.la.pinv(J), xi = [0, 0, 0, 0.1, 0, 0];
      s.qmin = api.la.mv(Jp, xi);
      s.z = this.nullvec(api, J, null);
      s.qd = s.qmin.map((x, k) => x + api.p.beta * s.z[k]);
      const tw = api.la.mv(J, s.qd);
      s.err = Math.max(...tw.map((x, k) => Math.abs(x - xi[k])));
      s.q = this.q0.slice();
    }
    if (api.keep.trace) api.keep.trace.clear();
  },
  readouts(api, s) {
    if (!s.q) return [];
    const d = 180 / Math.PI;
    if (api.scene === "self") {
      if (s.elbow > 0.10 && s.drift < 0.001) api.done("aside");
      return [[["关节角变化 / °", "Joint changes / °"], s.q.map((x, i) => api.fmt((x - this.q0[i]) * d, 1)).join(", ")],
              [["肘部水平移开", "Elbow moved sideways"], api.fmt(100 * s.elbow, 1) + " cm"],
              [["肘部高度变化", "Elbow height change"], api.fmt(100 * s.dz, 1) + " cm"],
              [["法兰漂移", "Flange drift"], api.fmt(1000 * s.drift, 3) + " mm"]];
    }
    const nq = api.la.norm(s.qd), nmin = api.la.norm(s.qmin);
    if (Math.abs(api.p.beta) < 0.003) api.done("least");
    if (Math.abs(api.p.beta - 0.1) < 0.003 && s.err < 1e-9) api.done("same");
    return [[["J⁺ξ / (rad/s)", "J⁺ξ / (rad/s)"], api.la.vstr(s.qmin, 3)],
            [["v₇（零空间）", "v₇ (null space)"], api.la.vstr(s.z, 3)],
            [["θ̇ = J⁺ξ + βv₇", "θ̇ = J⁺ξ + βv₇"], api.la.vstr(s.qd, 3)],
            [["‖θ̇‖ 与 √(‖J⁺ξ‖² + β²)", "‖θ̇‖ and √(‖J⁺ξ‖² + β²)"], api.fmt(nq, 4) + " / " + api.fmt(Math.sqrt(nmin * nmin + api.p.beta * api.p.beta), 4) + " rad/s"],
            [["末端运动误差 max|Jθ̇ − ξ|", "Tool-motion error max|Jθ̇ − ξ|"], s.err.toExponential(1)]];
  },
  draw(api, s) {
    const arm = api.m["B-ARM-PANDA"];
    if (!arm || !s.q) return;
    arm.set(this.pose(s.q));
    if (api.keep.trace && api.scene === "self") api.keep.trace.add(arm.point("link4", [0, 0, 0]));
  },
});
