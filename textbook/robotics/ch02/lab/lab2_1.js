// 实验 2.1 关节速度、雅可比矩阵与末端速度（配 2.1 节）。平面 2R 臂 L1 = 0.425 m、L2 = 0.392 m；生活场景：买水果。
WQ.lab({
  title: ["实验 2.1 雅可比矩阵：列的线性组合", "Lab 2.1 The Jacobian: a combination of columns"],
  goal: ["拖动关节角和关节速度，看末端速度怎样由雅可比矩阵的两列组合而成，以及 det J = 0 时发生了什么。",
         "Drag the joint angles and speeds; see the end-effector velocity built from the two columns of J, and what happens when det J = 0."],
  scenes: [
    { id: "arm", robot: true, name: ["平面 2R 臂", "Planar 2R arm"], hide: ["x1", "x2"],
      problem: { title: ["机器人问题：末端往哪里走", "Robot problem: where does the end-effector go?"],
                 text: ["v = θ̇₁ j₁ + θ̇₂ j₂：j₁ 垂直于基座到末端的连线，j₂ 垂直于肘部到末端的连线。",
                        "v = θ̇₁ j₁ + θ̇₂ j₂: j₁ is perpendicular to base→end-effector, j₂ to elbow→end-effector."] } },
    { id: "fruit", name: ["买水果", "Buying fruit"], hide: ["th1", "th2", "w1", "w2"],
      problem: { title: ["生活中的例子：凑出总价和维生素 C", "Everyday example: hit a price and a vitamin C total"],
                 text: ["苹果 12 元/kg、维生素 C 40 mg/kg；橙子 8 元/kg、500 mg/kg。目标：总价 40 元，维生素 C 1080 mg。",
                        "Apples ¥12/kg, 40 mg vitamin C per kg; oranges ¥8/kg, 500 mg/kg. Target: ¥40 and 1080 mg."] } },
  ],
  params: [
    { id: "th1", name: ["关节角 θ₁", "Joint angle θ₁"], min: -180, max: 180, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "th2", name: ["关节角 θ₂", "Joint angle θ₂"], min: -180, max: 180, step: 1, value: 60, unit: "°", digits: 0 },
    { id: "w1", name: ["关节速度 θ̇₁", "Joint speed θ̇₁"], min: -1, max: 1, step: 0.1, value: 0.5, unit: "rad/s", digits: 1 },
    { id: "w2", name: ["关节速度 θ̇₂", "Joint speed θ̇₂"], min: -1, max: 1, step: 0.1, value: -1, unit: "rad/s", digits: 1 },
    { id: "x1", name: ["苹果 x₁", "Apples x₁"], min: 0, max: 5, step: 0.1, value: 1, unit: "kg", digits: 1 },
    { id: "x2", name: ["橙子 x₂", "Oranges x₂"], min: 0, max: 5, step: 0.1, value: 1, unit: "kg", digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "xonly", robot: true, text: ["θ = (30°, 60°) 时只转关节 2，让末端沿 +x 方向运动。", "At θ = (30°, 60°) turn only joint 2 so that the end-effector moves along +x."],
      demo: { scene: "arm", set: { th1: 30, th2: 60, w1: 0, w2: -1 }, press: [] } },
    { id: "straight", robot: true, text: ["把手臂伸直（θ₂ = 0°），看 det J = 0 时两列变得平行。", "Straighten the arm (θ₂ = 0°): det J = 0 and the two columns become parallel."],
      demo: { scene: "arm", set: { th1: 30, th2: 0, w1: 0.5, w2: 0.5 }, press: [] } },
    { id: "fruit", text: ["凑出总价 40 元、维生素 C 1080 mg。", "Make the total ¥40 with 1080 mg of vitamin C."],
      demo: { scene: "fruit", set: { x1: 2, x2: 2 }, press: [] } },
  ],
  think: ["手臂伸直时，无论关节速度取什么值，末端速度都朝哪个方向？这与 det J = 0 有什么关系？",
          "With the arm straight, which way does the end-effector move whatever the joint speeds are? How is that related to det J = 0?"],

  L: [0.425, 0.392],
  J(api) {
    const t1 = api.p.th1 * Math.PI / 180, t12 = t1 + api.p.th2 * Math.PI / 180, [l1, l2] = this.L;
    return [[-l1 * Math.sin(t1) - l2 * Math.sin(t12), -l2 * Math.sin(t12)], [l1 * Math.cos(t1) + l2 * Math.cos(t12), l2 * Math.cos(t12)]];
  },
  reset(api, s) {},
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "arm") {
      const J = this.J(api), w = [api.p.w1, api.p.w2];
      const v = [J[0][0] * w[0] + J[0][1] * w[1], J[1][0] * w[0] + J[1][1] * w[1]];
      const det = J[0][0] * J[1][1] - J[0][1] * J[1][0];
      if (Math.abs(api.p.th1 - 30) < 0.5 && Math.abs(api.p.th2 - 60) < 0.5 && Math.abs(api.p.w1) < 1e-9 && api.p.w2 < 0 && v[0] > 0 && Math.abs(v[1]) < 1e-9) api.done("xonly");
      if (Math.abs(det) < 1e-9 && Math.abs(api.p.th2) < 0.5) api.done("straight");
      return [[["雅可比矩阵 J / m", "Jacobian J / m"], `[${f(J[0][0], 4)}, ${f(J[0][1], 4)}; ${f(J[1][0], 4)}, ${f(J[1][1], 4)}]`],
              [["det J / m²", "det J / m²"], f(det, 5)],
              [["末端速度 v", "end-effector velocity v"], `(${f(v[0], 4)}, ${f(v[1], 4)}) m/s`],
              [["速度大小 |v|", "speed |v|"], f(Math.hypot(v[0], v[1]), 4) + " m/s"]];
    }
    const price = 12 * api.p.x1 + 8 * api.p.x2, vc = 40 * api.p.x1 + 500 * api.p.x2;
    if (Math.abs(price - 40) < 0.05 && Math.abs(vc - 1080) < 1) api.done("fruit");
    return [[["矩阵（列：苹果、橙子）", "matrix (columns: apples, oranges)"], "[12, 8; 40, 500]"],
            [["总价", "total price"], f(price, 1) + api.T(" 元", " yuan")],
            [["维生素 C", "vitamin C"], f(vc, 0) + " mg"],
            [["目标", "target"], api.T("40 元，1080 mg", "40 yuan, 1080 mg")]];
  },
  draw(api, s) {
    const { w, h } = api;
    if (api.scene === "arm") {
      const k = Math.min(w, h) * 0.75, ox = w * 0.3, oy = h * 0.85;
      api.grid(w, h, 40);
      api.line(ox - 40, oy, ox + k * 1.0, oy, api.css("--red"), 1.5); api.line(ox, oy + 10, ox, oy - k * 1.0, api.css("--green"), 1.5);
      const pts = api.arm(ox, oy, [api.p.th1, api.p.th2], [this.L[0] * k, this.L[1] * k], api.css("--muted"), 10);
      const tip = pts[2], J = this.J(api), sc = k * 0.8;
      const a = [tip[0] + sc * api.p.w1 * J[0][0], tip[1] - sc * api.p.w1 * J[1][0]];
      const b = [tip[0] + sc * api.p.w2 * J[0][1], tip[1] - sc * api.p.w2 * J[1][1]];
      const v = [a[0] + b[0] - tip[0], a[1] + b[1] - tip[1]];
      api.line(...a, ...v, api.css("--muted"), 1, [4, 4]); api.line(...b, ...v, api.css("--muted"), 1, [4, 4]);
      api.arrow(...tip, ...a, api.css("--blue"), 3); api.arrow(...tip, ...b, api.css("--amber"), 3); api.arrow(...tip, ...v, api.css("--ink"), 4);
      if (Math.abs(api.p.w1) > 0.01) api.label("θ̇₁ j₁", a[0] + 6, a[1] - 8, api.css("--blue"), 13);
      if (Math.abs(api.p.w2) > 0.01) api.label("θ̇₂ j₂", b[0] + 6, b[1] + 12, api.css("--amber"), 13);
      api.label("v", v[0] + 8, v[1] - 6, api.css("--ink"), 15);
      return;
    }
    // 买水果：横轴总价（元），纵轴维生素 C（mg）
    const ox = w * 0.12, oy = h * 0.88, sx = w * 0.75 / 60, sy = h * 0.78 / 2600;
    const P = (p, v) => [ox + p * sx, oy - v * sy];
    api.line(ox, oy, ox + 60 * sx, oy, api.css("--ink"), 1.5); api.line(ox, oy, ox, oy - 2600 * sy, api.css("--ink"), 1.5);
    api.label(api.T("总价 / 元", "price / yuan"), ox + 60 * sx, oy + 16, api.css("--muted"), 12, "right");
    api.label(api.T("维生素 C / mg", "vitamin C / mg"), ox + 6, oy - 2600 * sy + 4, api.css("--muted"), 12);
    const A = P(12 * api.p.x1, 40 * api.p.x1), V = P(12 * api.p.x1 + 8 * api.p.x2, 40 * api.p.x1 + 500 * api.p.x2);
    api.arrow(ox, oy, ...A, api.css("--red"), 3); api.arrow(...A, ...V, api.css("--green"), 3);
    api.label(api.T("苹果 x₁·(12, 40)", "apples x₁·(12, 40)"), (ox + A[0]) / 2, (oy + A[1]) / 2 - 14, api.css("--red"), 12);
    api.label(api.T("橙子 x₂·(8, 500)", "oranges x₂·(8, 500)"), V[0] + 8, (A[1] + V[1]) / 2, api.css("--green"), 12);
    const Tg = P(40, 1080);
    api.circle(...Tg, 7, null, api.css("--amber")); api.circle(...V, 4, api.css("--ink"));
    api.label(api.T("目标", "target"), Tg[0] + 10, Tg[1] - 10, api.css("--amber"), 13);
  },
});

