// 实验 12.4 两种读法与错误的次序（配 12.4 节）。平面 3R 臂，L = (0.425, 0.392, 0.1) m。
// 读法 0：从外往里（空间形式，先转关节 3，各轴在零位处）；读法 1：从里往外（先转关节 1，每转一个关节就更新外侧各轴）；
// 读法 2：写反次序 e^[S3]θ3 e^[S2]θ2 e^[S1]θ1 M（先绕零位的 q1 转，再绕零位的 q2、q3 转）。
WQ.lab({
  title: ["实验 12.4 两种读法与错误的次序", "Lab 12.4 Two readings and the wrong order"],
  goal: ["逐步演示指数积的两种正确读法和一种错误写法，看清每一步各关节轴在哪里。",
         "Step through two correct readings of the PoE and one wrong order, and see where each joint axis is at every step."],
  scenes: [
    { id: "arm", robot: true, name: ["平面 3R 臂", "Planar 3R arm"],
      problem: { title: ["机器人问题：程序里的指数为什么不能写反", "Robot problem: why the exponentials cannot be reversed"],
                 text: ["正运动学程序把指数的次序写反了，算出的末端会落在哪里？能否一眼看出这个错误？",
                        "A forward-kinematics routine has the exponentials reversed. Where does the computed tip land, and can you spot the bug at a glance?"] } },
    { id: "lamp", name: ["台灯", "Desk lamp"],
      problem: { title: ["生活中的例子：先转底座，铰链跟着走", "Everyday example: turn the base and the hinges go along"],
                 text: ["转动台灯底座以后再拧灯臂的铰链，铰链已经跟着底座转到了新位置。",
                        "Turn the lamp's base, then a hinge: the hinge has moved with the base."] } },
  ],
  params: [
    { id: "t1", name: ["关节角 θ₁", "Joint θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "t2", name: ["关节角 θ₂", "Joint θ₂"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "t3", name: ["关节角 θ₃", "Joint θ₃"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "mode", name: ["读法：0 从外往里 / 1 从里往外 / 2 写反次序", "Reading: 0 outside-in / 1 inside-out / 2 reversed"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["逐步演示", "Step through"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "q2", robot: true, text: ["读法 1、θ₁ = 30°：逐步演示，记下关节 1 转过以后关节 2 的中心坐标。", "Reading 1 with θ₁ = 30°: step through and note joint 2's centre after joint 1 has turned."],
      demo: { scene: "arm", set: { t1: 30, t2: 45, t3: -90, mode: 1 }, press: ["start"], wait: 5 } },
    { id: "same", robot: true, text: ["演示读法 0 或读法 1 到结束，对照界面给出的另一种读法的末端，验证两者相同。", "Step through reading 0 or 1 to the end and compare with the tip by the other reading: they agree."],
      demo: { scene: "lamp", set: { t1: 30, t2: 45, t3: -90, mode: 0 }, press: ["start"], wait: 5 } },
    { id: "wrong", text: ["选择读法 2，找一组关节角，使算出的末端离原点超过 0.917 m（够不到的地方）。", "Reading 2: find angles that put the computed tip more than 0.917 m from the origin."],
      demo: { scene: "arm", set: { t1: 30, t2: 45, t3: -90, mode: 2 }, press: [] } },
  ],
  think: ["从里往外读时，关节 2 的新轴为什么等于 [Ad_E₁] 乘以旧轴？它与第 16 章雅可比矩阵的列有什么关系？",
          "Reading inside-out, why is joint 2's new axis [Ad_E₁] times the old one? How does it relate to the Jacobian columns of Chapter 16?"],

  L: [0.425, 0.392, 0.1],
  rot(p, c, t) { const x = p[0] - c[0], y = p[1] - c[1], co = Math.cos(t), si = Math.sin(t); return [c[0] + co * x - si * y, c[1] + si * x + co * y]; },
  th(api) { const d = Math.PI / 180; return [api.p.t1 * d, api.p.t2 * d, api.p.t3 * d]; },
  // 完成 k 步以后：手臂四个点（三个关节中心 + 末端）。写反次序时整体按“绕零位点转”搬动，关节中心只作参考
  state(api, k) {
    const th = this.th(api), L = this.L;
    let P = [[0, 0], [L[0], 0], [L[0] + L[1], 0], [L[0] + L[1] + L[2], 0]];
    const home = P.map((p) => p.slice());
    const order = api.p.mode === 0 ? [2, 1, 0] : [0, 1, 2];
    for (let s = 0; s < k; s++) {
      const i = order[s];
      if (api.p.mode === 2) P = P.map((p) => this.rot(p, home[i], th[i]));          // 绕零位时的点
      else P = P.map((p, j) => (j > i ? this.rot(p, P[i], th[i]) : p));            // 绕关节 i 当前位置，只动外侧
    }
    return P;
  },
  // 末端位姿用矩阵算（平面齐次矩阵 3×3），三种读法是三种不同的算法：
  //   读法 0：e^[S1]θ1 … e^[S3]θ3 M，从右往左乘，各轴在零位；读法 1：每转一个关节就用 E 搬动外侧各轴（定理 12.4.1 的伴随作用）；
  //   读法 2：e^[S3]θ3 e^[S2]θ2 e^[S1]θ1 M（错误）。
  E(q, t) { const c = Math.cos(t), s = Math.sin(t); return [[c, -s, q[0] - c * q[0] + s * q[1]], [s, c, q[1] - s * q[0] - c * q[1]], [0, 0, 1]]; },
  mm(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  ap(A, q) { return [A[0][0] * q[0] + A[0][1] * q[1] + A[0][2], A[1][0] * q[0] + A[1][1] * q[1] + A[1][2]]; },
  tipT(api, mode, k) {
    const th = this.th(api), L = this.L, home = [[0, 0], [L[0], 0], [L[0] + L[1], 0]];
    let T = [[1, 0, L[0] + L[1] + L[2]], [0, 1, 0], [0, 0, 1]], axes = home.map((q) => q.slice()), q2 = null;
    if (mode === 0) { for (let i = 2; i >= 3 - k; i--) T = this.mm(this.E(home[i], th[i]), T); }
    else if (mode === 1) {
      for (let i = 0; i < k; i++) {
        const Ei = this.E(axes[i], th[i]);
        T = this.mm(Ei, T);
        axes = axes.map((q, j) => (j > i ? this.ap(Ei, q) : q));
        if (i === 0) q2 = axes[1];
      }
    } else { for (let i = 0; i < k; i++) T = this.mm(this.E(home[i], th[i]), T); }
    return { T, q2 };
  },
  pivot(api, step) { const order = api.p.mode === 0 ? [2, 1, 0] : [0, 1, 2]; return order[step]; },

  reset(api, s) { s.k = 3; s.clock = 0; },
  start(api, s) { s.k = 0; s.clock = 0; s.q2 = null; },
  update(dt, api, s) {
    s.clock += dt;
    if (s.clock > 1.2) {
      s.clock = 0; s.k += 1;
      if (s.k === 1 && api.p.mode === 1) s.q2 = this.tipT(api, 1, 1).q2;
      if (s.k >= 3) {
        api.stop();
        if (api.p.mode === 1 && api.p.t1 === 30) api.done("q2");
        if (api.p.mode <= 1) {
          const a = this.tipT(api, api.p.mode, 3).T, b = this.tipT(api, 1 - api.p.mode, 3).T;
          s.other = [b[0][2], b[1][2]];
          if (Math.hypot(a[0][2] - b[0][2], a[1][2] - b[1][2]) < 1e-9 && Math.abs(a[0][0] - b[0][0]) < 1e-9) api.done("same");
        }
      }
    }
  },
  readouts(api, s) {
    const P = this.state(api, api.running ? s.k : 3), T = this.tipT(api, api.p.mode, api.running ? s.k : 3).T;
    const tip = [T[0][2], T[1][2]], r = Math.hypot(tip[0], tip[1]);
    if (api.p.mode === 2 && r > 0.917 + 1e-6) api.done("wrong");
    const names = [["从外往里（空间形式）", "outside-in (space form)"], ["从里往外", "inside-out"], ["写反次序（错误）", "reversed (wrong)"]];
    const rows = [[["读法", "reading"], api.lang() === "en" ? names[api.p.mode][1] : names[api.p.mode][0]],
                  [["末端位置", "tip"], `(${api.fmt(tip[0], 4)}, ${api.fmt(tip[1], 4)}) m`],
                  [["末端到原点的距离", "tip distance from origin"], api.fmt(r, 3) + " m" + (r > 0.917 + 1e-6 ? (api.lang() === "en" ? "  (out of reach)" : "（够不到）") : "")]];
    if (api.p.mode !== 2) rows.push([["关节 2 中心（当前）", "joint 2 centre (now)"], `(${api.fmt(P[1][0], 4)}, ${api.fmt(P[1][1], 4)}) m`]);
    if (s.other) rows.push([["另一种读法的末端", "tip by the other reading"], `(${api.fmt(s.other[0], 4)}, ${api.fmt(s.other[1], 4)}) m`]);
    if (s.q2) rows.push([["关节 1 转过后关节 2 的中心", "joint 2 centre after joint 1"], `(${api.fmt(s.q2[0], 4)}, ${api.fmt(s.q2[1], 4)}) m`]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, k = Math.min(w / 2.6, h / 2.0) * 0.95, cx = w * 0.33, cy = h * 0.62;
    const X = ([x, y]) => [cx + k * x, cy - k * y];
    const c = api.ctx;
    // 工作空间边界
    c.beginPath(); c.setLineDash([5, 5]); c.arc(cx, cy, k * 0.917, 0, Math.PI * 2); c.strokeStyle = api.css("--muted"); c.lineWidth = 1; c.stroke(); c.setLineDash([]);
    const home = [[0, 0], [0.425, 0], [0.817, 0], [0.917, 0]].map(X);
    for (let i = 0; i < 3; i++) api.line(...home[i], ...home[i + 1], api.css("--muted"), 2, [6, 5]);
    const step = api.running ? s.k : 3;
    const P = this.state(api, step).map(X);
    const col = api.p.mode === 2 ? api.css("--red") : api.scene === "lamp" ? api.css("--amber") : api.css("--accent");
    if (api.p.mode === 2) {
      api.line(...P[2], ...P[3], col, 5);
      api.circle(P[3][0], P[3][1], 6, col);
      home.slice(0, 3).forEach((q) => api.circle(q[0], q[1], 6, api.css("--orange")));
    } else {
      for (let i = 0; i < 3; i++) api.line(...P[i], ...P[i + 1], col, 9 - 2 * i);
      P.slice(0, 3).forEach((q, i) => api.circle(q[0], q[1], 7, api.css("--panel"), i > 0 ? api.css("--red") : col));
    }
    if (api.running && s.k < 3) {
      const i = this.pivot(api, s.k);
      const piv = api.p.mode === 1 ? P[i] : home[i];
      api.circle(piv[0], piv[1], 12, null, api.css("--red"));
      api.label((api.lang() === "en" ? "next: about joint " : "下一步：绕关节 ") + (i + 1), piv[0] + 14, piv[1] - 18, api.css("--red"), 13);
    }
    api.frame(cx, cy, 0, k * 0.12, ["x", "y"], "{s}");
  },
});
