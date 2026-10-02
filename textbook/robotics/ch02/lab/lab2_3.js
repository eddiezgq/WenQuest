// 实验 2.3 找出特征方向（配 2.3 节）。拖动单位向量 x 的方向角 α，看它的像 Ax；Ax 与 x 共线时 x 是特征向量。
WQ.lab({
  title: ["实验 2.3 找出特征方向", "Lab 2.3 Finding the eigen-directions"],
  goal: ["转动单位向量 x，找出 Ax 与 x 共线的方向，读出特征值；比较对称与不对称的矩阵。",
         "Turn the unit vector x; find the directions where Ax lines up with x and read the eigenvalues; compare symmetric and non-symmetric matrices."],
  scenes: [
    { id: "wrist", robot: true, name: ["柔顺手腕的实测刚度", "Measured wrist stiffness"],
      problem: { title: ["机器人问题：往哪个方向推，就往哪个方向让", "Robot problem: push one way, give way the same way"],
                 text: ["K = [1600, 650; 650, 900] N/m。沿 x 推 1 mm，回复力为 Kx（图中以 1000 N/m 为单位画出）。",
                        "K = [1600, 650; 650, 900] N/m. Push 1 mm along x: the force is Kx (drawn in units of 1000 N/m)."] } },
    { id: "rubber", name: ["拉伸橡皮膜", "Stretching a rubber sheet"],
      problem: { title: ["生活中的例子：拉伸后不转向的直径", "Everyday example: diameters that do not turn"],
                 text: ["A = [1.5, 0.5; 0, 1]：沿 x 拉长并带一点错动。哪些直径拉伸后仍在原来的直线上？",
                        "A = [1.5, 0.5; 0, 1]: a stretch along x with a little shear. Which diameters stay on their own line?"] } },
  ],
  params: [{ id: "al", name: ["x 的方向角 α", "Direction of x, α"], min: 0, max: 179, step: 1, value: 0, unit: "°", digits: 0 }],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "hard", robot: true, text: ["找出“硬”的特征方向（Ax 与 x 共线且最长），读出主刚度。", "Find the stiff eigen-direction (Ax along x and longest); read the principal stiffness."],
      demo: { scene: "wrist", set: { al: 31 }, press: [] } },
    { id: "soft", robot: true, text: ["找出“软”的特征方向，验证它与硬方向垂直。", "Find the soft eigen-direction and check that it is perpendicular to the stiff one."],
      demo: { scene: "wrist", set: { al: 121 }, press: [] } },
    { id: "rub", text: ["对橡皮膜，找出不在 x 轴上的那个特征方向。", "For the rubber sheet, find the eigen-direction that is not the x axis."],
      demo: { scene: "rubber", set: { al: 135 }, press: [] } },
  ],
  think: ["橡皮膜的两个特征方向为什么不垂直？哪一种矩阵的特征方向一定垂直？", "Why are the rubber sheet's eigen-directions not perpendicular? For which matrices must they be?"],

  A(api) { return api.scene === "wrist" ? [[1.6, 0.65], [0.65, 0.9]] : [[1.5, 0.5], [0, 1]]; },
  calc(api) {
    const A = this.A(api), t = api.p.al * Math.PI / 180, x = [Math.cos(t), Math.sin(t)];
    const y = [A[0][0] * x[0] + A[0][1] * x[1], A[1][0] * x[0] + A[1][1] * x[1]];
    const L = Math.hypot(y[0], y[1]), cr = x[0] * y[1] - x[1] * y[0], dt = x[0] * y[0] + x[1] * y[1];
    return { A, x, y, L, ang: Math.abs(Math.atan2(cr, dt)) * 180 / Math.PI, sgn: Math.sign(dt) };
  },
  reset(api, s) {},
  readouts(api, s) {
    const c = this.calc(api), f = api.fmt, wr = api.scene === "wrist";
    const line = Math.min(c.ang, 180 - c.ang);
    if (wr && line < 1 && c.L > 1.5) api.done("hard");
    if (wr && line < 1 && c.L < 0.6) api.done("soft");
    if (!wr && line < 0.5 && Math.abs(api.p.al - 135) < 0.5) api.done("rub");
    return [[["x 与 Ax 的夹角", "angle between x and Ax"], f(c.ang, 2) + "°"],
            [["长度之比 |Ax| / |x|", "length ratio |Ax| / |x|"], wr ? f(c.L * 1000, 1) + " N/m" : f(c.L, 4)],
            [["Ax", "Ax"], wr ? `(${f(c.y[0], 4)}, ${f(c.y[1], 4)}) × 1000 N/m` : `(${f(c.y[0], 4)}, ${f(c.y[1], 4)})`],
            [["共线？", "on one line?"], line < 1 ? api.T("是：x 是特征向量", "yes: x is an eigenvector") : api.T("否", "no")]];
  },
  draw(api, s) {
    const { w, h } = api, cx = w * 0.42, cy = h * 0.52, k = Math.min(w, h) * 0.22, c = this.calc(api), A = c.A, ctx = api.ctx;
    const X = (x, y) => [cx + k * x, cy - k * y];
    api.grid(w, h, 40);
    ctx.beginPath(); for (let i = 0; i <= 120; i++) { const a = i / 120 * 2 * Math.PI, p = X(Math.cos(a), Math.sin(a)); i ? ctx.lineTo(...p) : ctx.moveTo(...p); }
    ctx.strokeStyle = api.css("--muted"); ctx.lineWidth = 1; ctx.stroke();
    ctx.beginPath(); for (let i = 0; i <= 120; i++) { const a = i / 120 * 2 * Math.PI, x = Math.cos(a), y = Math.sin(a);
      const p = X(A[0][0] * x + A[0][1] * y, A[1][0] * x + A[1][1] * y); i ? ctx.lineTo(...p) : ctx.moveTo(...p); }
    ctx.strokeStyle = api.css("--amber"); ctx.lineWidth = 1.5; ctx.stroke();
    // 方向线
    api.line(...X(-2.2 * c.x[0], -2.2 * c.x[1]), ...X(2.2 * c.x[0], 2.2 * c.x[1]), api.css("--grid"), 1, [5, 4]);
    const on = Math.min(c.ang, 180 - c.ang) < 1;
    api.arrow(cx, cy, ...X(...c.x), api.css("--ink"), 3);
    api.arrow(cx, cy, ...X(...c.y), on ? api.css("--red") : api.css("--orange"), 5);
    api.label("x", ...X(c.x[0] * 1.15 - 0.05, c.x[1] * 1.15 + 0.1), api.css("--ink"), 15);
    api.label("Ax", ...X(c.y[0] * 1.08 + 0.08, c.y[1] * 1.08 - 0.1), on ? api.css("--red") : api.css("--orange"), 15);
    api.label(api.T("灰：单位圆；金：它的像", "grey: unit circle; gold: its image"), 12, h - 16, api.css("--muted"), 12);
  },
});
