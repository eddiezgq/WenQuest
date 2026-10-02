// 实验 7.3 牛顿法与逆运动学（配 7.3 节）。2R 臂 l₁ = 0.425 m、l₂ = 0.392 m（UR5e 的大臂、小臂）。
// 牛顿法 θ ← θ − J(θ)⁻¹(p(θ) − p_d)（式 (7.3.8)），雅可比矩阵见式 (7.3.9)；可选回溯线搜索（式 (7.3.11)）。
// 生活场景：用牛顿法开平方 x ← (x + a/x)/2（式 (7.3.5)）。
WQ.lab({
  title: ["实验 7.3 牛顿法与逆运动学", "Lab 7.3 Newton's method and inverse kinematics"],
  goal: ["一步一步地运行牛顿法，看它怎样把 2R 臂的末端送到目标，体会二次收敛、初值的作用和失败的情形。",
         "Run Newton's method step by step; watch it bring the 2R arm's tip to the target, and see quadratic convergence, the role of the start and how it fails."],
  scenes: [
    { id: "arm", robot: true, name: ["2R 臂的逆运动学", "Inverse kinematics of a 2R arm"], hide: ["a", "x0"],
      problem: { title: ["机器人问题：末端要到 p_d，关节角是多少", "Robot problem: which joint angles put the tip at p_d"],
                 text: ["拖动目标 (x_d, y_d) 和初始关节角，按“迭代一步”或“开始”。读数给出每一步末端到目标的距离。",
                        "Set the target (x_d, y_d) and the starting joint angles, then press “One step” or “Start”. The readings give the tip-to-target distance after each step."] } },
    { id: "sqrt", name: ["用牛顿法开平方", "Square roots by Newton's method"], hide: ["px", "py", "t1", "t2", "ls"],
      problem: { title: ["生活中的例子：计算器怎样算 √a", "Everyday example: how a calculator finds √a"],
                 text: ["解 x² − a = 0：猜一个 x，用 x 与 a/x 的平均值作下一个猜测。看有效位数怎样增长。",
                        "Solve x² − a = 0: guess x, then take the average of x and a/x. Watch how the number of correct digits grows."] } },
  ],
  params: [
    { id: "px", name: ["目标 x_d", "Target x_d"], min: -0.9, max: 0.9, step: 0.01, value: 0.45, unit: "m", digits: 2 },
    { id: "py", name: ["目标 y_d", "Target y_d"], min: -0.9, max: 0.9, step: 0.01, value: 0.35, unit: "m", digits: 2 },
    { id: "t1", name: ["初值 θ₁⁽⁰⁾", "Start θ₁⁽⁰⁾"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "t2", name: ["初值 θ₂⁽⁰⁾", "Start θ₂⁽⁰⁾"], min: -180, max: 180, step: 1, value: 57, unit: "°", digits: 0 },
    { id: "ls", name: ["线搜索：0 关，1 开", "Line search: 0 off, 1 on"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "a", name: ["被开方数 a", "Number a"], min: 2, max: 100, step: 1, value: 10, unit: "", digits: 0 },
    { id: "x0", name: ["初值 x₀", "Start x₀"], min: 1, max: 50, step: 1, value: 3, unit: "", digits: 0 },
  ],
  buttons: [{ id: "one", name: ["迭代一步", "One step"], primary: true }, { id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 7.3.4：目标 (0.45, 0.35) m，初值 (0°, 57°)，6 次迭代内收敛。", "Example 7.3.4: target (0.45, 0.35) m, start (0°, 57°): converge within 6 steps."],
      demo: { scene: "arm", set: { px: 0.45, py: 0.35, t1: 0, t2: 57, ls: 0 }, press: ["start"], wait: 8 } },
    { id: "other", robot: true, text: ["换一个初值，使牛顿法收敛到肘部在另一侧（θ₂ < 0）的解。", "Choose another start so that Newton converges to the other elbow (θ₂ < 0)."],
      demo: { scene: "arm", set: { px: 0.45, py: 0.35, t1: 60, t2: -60, ls: 0 }, press: ["start"], wait: 8 } },
    { id: "ls", robot: true, text: ["找一个纯牛顿法 40 步不收敛、打开线搜索后收敛的初值（例如 (−170°, −140°)）。", "Find a start where plain Newton fails in 40 steps but converges with line search (e.g. (−170°, −140°))."],
      demo: { scene: "arm", set: { px: 0.45, py: 0.35, t1: -170, t2: -140, ls: 1 }, press: ["start"], wait: 12 } },
    { id: "far", robot: true, text: ["把目标移到够不着的地方（距基座超过 0.817 m），迭代 10 次以上，观察残差不会小于距离之差。", "Move the target out of reach (more than 0.817 m away), iterate 10 times or more, and see that the residual cannot drop below the gap."],
      demo: { scene: "arm", set: { px: 0.9, py: 0.3, t1: 10, t2: 30, ls: 0 }, press: ["start"], wait: 12 } },
    { id: "sqrt", text: ["用牛顿法求 √10，迭代到误差小于 10⁻¹²，记录每一步的有效位数。", "Find √10 by Newton's method to an error below 10⁻¹²; record the correct digits at each step."],
      demo: { scene: "sqrt", set: { a: 10, x0: 3 }, press: ["start"], wait: 8 } },
  ],
  think: ["为什么从 θ₂ = 0（手臂伸直）出发，牛顿法一步都走不了？在控制器里应当怎样选初值？",
          "Why can Newton's method not take a single step from θ₂ = 0 (arm straight)? How should a controller choose its starting guess?"],

  L1: 0.425, L2: 0.392,
  fk(th) { return [this.L1 * Math.cos(th[0]) + this.L2 * Math.cos(th[0] + th[1]), this.L1 * Math.sin(th[0]) + this.L2 * Math.sin(th[0] + th[1])]; },
  res(th, p) { const q = this.fk(th); return Math.hypot(q[0] - p[0], q[1] - p[1]); },
  // 一次牛顿迭代；返回 null 表示雅可比矩阵奇异
  newton(th, p, ls) {
    const t1 = th[0], t12 = th[0] + th[1], q = this.fk(th), r = [q[0] - p[0], q[1] - p[1]];
    const a = -this.L1 * Math.sin(t1) - this.L2 * Math.sin(t12), b = -this.L2 * Math.sin(t12), c = this.L1 * Math.cos(t1) + this.L2 * Math.cos(t12), d = this.L2 * Math.cos(t12);
    const det = a * d - b * c;
    if (Math.abs(det) < 1e-12) return null;
    const dx = (d * r[0] - b * r[1]) / det, dy = (-c * r[0] + a * r[1]) / det, n0 = Math.hypot(r[0], r[1]);
    let al = 1;
    if (ls) for (let i = 0; i < 30 && this.res([th[0] - al * dx, th[1] - al * dy], p) >= n0; i++) al /= 2;
    return [th[0] - al * dx, th[1] - al * dy];
  },
  wrap(x) { return Math.atan2(Math.sin(x), Math.cos(x)); },
  plainFails(api) {
    const p = [api.p.px, api.p.py]; let th = [api.p.t1 * Math.PI / 180, api.p.t2 * Math.PI / 180];
    for (let k = 0; k < 40; k++) { if (this.res(th, p) < 1e-10) return false; th = this.newton(th, p, false); if (!th) return true; }
    return this.res(th, p) >= 1e-10;
  },

  reset(api, s) {
    s.k = 0; s.clock = 0; s.stuck = false;
    s.th = [api.p.t1 * Math.PI / 180, api.p.t2 * Math.PI / 180];
    s.hist = api.scene === "arm" ? [this.res(s.th, [api.p.px, api.p.py])] : [];
    s.path = [s.th.slice()];
    s.x = api.p.x0; s.xs = [s.x];
  },
  iterate(api, s) {
    if (api.scene === "sqrt") {
      if (Math.abs(s.x - Math.sqrt(api.p.a)) < 1e-15 * Math.sqrt(api.p.a) || s.k >= 30) return false;
      s.x = 0.5 * (s.x + api.p.a / s.x); s.xs.push(s.x); s.k += 1;
      if (api.p.a === 10 && Math.abs(s.x - Math.sqrt(10)) < 1e-12) api.done("sqrt");
      return true;
    }
    const p = [api.p.px, api.p.py];
    if (s.hist[s.hist.length - 1] < 1e-12 || s.k >= 40) return false;
    const nx = this.newton(s.th, p, api.p.ls === 1);
    if (!nx) { s.stuck = true; return false; }
    s.th = nx; s.k += 1; s.path.push(nx.slice());
    const r = this.res(nx, p); s.hist.push(r);
    const conv = r < 1e-10, reach = this.L1 + this.L2, dist = Math.hypot(p[0], p[1]);
    if (conv && Math.abs(p[0] - 0.45) < 1e-9 && Math.abs(p[1] - 0.35) < 1e-9 && api.p.t1 === 0 && api.p.t2 === 57 && s.k <= 6) api.done("ex");
    if (conv && this.wrap(nx[1]) < 0) api.done("other");
    if (conv && api.p.ls === 1 && this.plainFails(api)) api.done("ls");
    if (dist > reach && s.k >= 10) api.done("far");
    return true;
  },
  action(id, api, s) { if (id === "one") { api.running = false; this.iterate(api, s); } },
  update(dt, api, s) {
    s.clock += dt;
    if (s.clock > 0.45) { s.clock = 0; if (!this.iterate(api, s)) api.stop(); }
  },
  readouts(api, s) {
    if (api.scene === "sqrt") {
      const r = Math.sqrt(api.p.a), rows = [[["√a（参照值）", "√a (reference)"], r.toFixed(15)]];
      s.xs.forEach((x, i) => { const e = Math.abs(x - r); rows.push([[`x${i}`, `x${i}`], `${x.toFixed(15)}   ${api.T("误差", "error")} ${e === 0 ? "0" : e.toExponential(1)}`]); });
      return rows.slice(0, 9);
    }
    const p = [api.p.px, api.p.py], dist = Math.hypot(p[0], p[1]), reach = this.L1 + this.L2;
    const rows = [[["迭代次数 k", "iteration k"], String(s.k)],
                  [["关节角 θ⁽ᵏ⁾", "joints θ⁽ᵏ⁾"], `(${api.fmt(this.wrap(s.th[0]) * 180 / Math.PI, 2)}°, ${api.fmt(this.wrap(s.th[1]) * 180 / Math.PI, 2)}°)`],
                  [["det J = l₁l₂ sin θ₂", "det J = l₁l₂ sin θ₂"], api.fmt(this.L1 * this.L2 * Math.sin(s.th[1]), 4) + " m²"],
                  [["目标到基座的距离", "target distance from base"], api.fmt(dist, 3) + " m" + (dist > reach ? api.T("（够不着）", " (out of reach)") : "")]];
    if (s.stuck) rows.push([["状态", "status"], api.T("雅可比矩阵奇异，无法迭代", "Jacobian singular: cannot step")]);
    s.hist.slice(-5).forEach((r, i) => { const j = s.hist.length - Math.min(5, s.hist.length) + i; rows.push([[`‖p − p_d‖，第 ${j} 次`, `‖p − p_d‖ at k = ${j}`], r.toExponential(2) + " m"]); });
    return rows;
  },
  draw(api, s) {
    const { w, h } = api;
    if (api.scene === "sqrt") {
      const a = api.p.a, X0 = 40, W = w - 80, xmax = Math.max(api.p.x0, Math.sqrt(a)) * 1.3, Y0 = h * 0.82, H = h * 0.7;
      const X = (x) => X0 + x / xmax * W, ymax = xmax * xmax - a, ymin = -a, Y = (y) => Y0 - (y - ymin) / (ymax - ymin) * H;
      api.line(X0, Y(0), X0 + W, Y(0), api.css("--muted"), 1);
      let prev = null; for (let i = 0; i <= 100; i++) { const x = xmax * i / 100, pt = [X(x), Y(x * x - a)]; if (prev) api.line(...prev, ...pt, api.css("--ink"), 2); prev = pt; }
      s.xs.forEach((x, i) => {
        const col = i === s.xs.length - 1 ? api.css("--red") : api.css("--accent");
        api.circle(X(x), Y(0), 4, col);
        if (i < s.xs.length - 1) { const x1 = s.xs[i + 1]; api.line(X(x), Y(x * x - a), X(x1), Y(0), api.css("--amber"), 1.5); api.line(X(x), Y(0), X(x), Y(x * x - a), api.css("--grid"), 1, [3, 3]); }
      });
      api.label("f(x) = x² − a", X0 + 6, 18, api.css("--ink"), 13);
      api.label("√a", X(Math.sqrt(a)), Y(0) + 16, api.css("--red"), 13, "center");
      return;
    }
    const sc = Math.min(w * 0.42, h * 0.48) / (this.L1 + this.L2), bx = w * 0.45, by = h * 0.55;
    const P = (x, y) => [bx + sc * x, by - sc * y];
    const reach = this.L1 + this.L2;
    for (let i = 0; i < 72; i++) { const a0 = i / 72 * 2 * Math.PI, a1 = (i + 0.5) / 72 * 2 * Math.PI; api.line(...P(reach * Math.cos(a0), reach * Math.sin(a0)), ...P(reach * Math.cos(a1), reach * Math.sin(a1)), api.css("--grid"), 1); }
    const deg = (th) => [th[0] * 180 / Math.PI, th[1] * 180 / Math.PI];
    s.path.slice(0, -1).forEach((th) => {
      const e = P(this.L1 * Math.cos(th[0]), this.L1 * Math.sin(th[0])), t = this.fk(th);
      api.line(bx, by, ...e, api.css("--grid"), 3); api.line(...e, ...P(t[0], t[1]), api.css("--grid"), 3);
    });
    api.arm(bx, by, deg(s.th), [this.L1 * sc, this.L2 * sc], api.css("--accent"), 9);
    const tg = P(api.p.px, api.p.py);
    api.circle(tg[0], tg[1], 7, null, api.css("--red")); api.line(tg[0] - 10, tg[1], tg[0] + 10, tg[1], api.css("--red"), 1.5); api.line(tg[0], tg[1] - 10, tg[0], tg[1] + 10, api.css("--red"), 1.5);
    api.label("p_d", tg[0] + 10, tg[1] - 12, api.css("--red"), 13);
    api.label(api.T("灰色：前几次迭代的形态", "grey: earlier iterates"), 12, 18, api.css("--muted"), 12);
  },
});
