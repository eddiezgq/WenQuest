// 实验 2.4 拖动矩阵元素，看变换和奇异值（配 2.4 节）。2×2 矩阵的奇异值由 AᵀA 的特征值求出（定理 2.4.1）。
WQ.lab({
  title: ["实验 2.4 奇异值分解：单位圆变成椭圆", "Lab 2.4 The SVD: the unit circle becomes an ellipse"],
  goal: ["拖动矩阵元素或机械臂的关节角，看单位圆的像怎样变化，读出奇异值、条件数和可操作度。",
         "Drag the matrix entries or the arm's joint angles; watch the image of the unit circle and read the singular values, condition number and manipulability."],
  scenes: [
    { id: "mat", name: ["影子与椭圆：任意矩阵", "Shadows and ellipses: any matrix"], hide: ["th1", "th2"],
      problem: { title: ["生活中的例子：圆的影子总是椭圆", "Everyday example: a circle's shadow is always an ellipse"],
                 text: ["拖动 A 的四个元素。任何 2×2 矩阵都把单位圆变成椭圆（可能压扁成线段），半轴是两个奇异值。",
                        "Drag the four entries of A. Every 2×2 matrix maps the unit circle to an ellipse (perhaps flattened to a segment) with the singular values as semi-axes."] } },
    { id: "arm", robot: true, name: ["2R 臂的可操作度", "Manipulability of a 2R arm"], hide: ["a11", "a12", "a21", "a22"],
      problem: { title: ["机器人问题：末端往哪个方向走得最快", "Robot problem: which way can the end-effector move fastest?"],
                 text: ["A 是雅可比矩阵（L₁ = 0.425 m，L₂ = 0.392 m）。末端处的椭圆是 |θ̇| = 1 rad/s 时末端速度的集合。",
                        "A is the Jacobian (L₁ = 0.425 m, L₂ = 0.392 m). The ellipse at the end-effector holds the end-effector velocities for |θ̇| = 1 rad/s."] } },
  ],
  params: [
    { id: "a11", name: ["a₁₁", "a₁₁"], min: -2, max: 2, step: 0.1, value: 1.2, unit: "", digits: 1 },
    { id: "a12", name: ["a₁₂", "a₁₂"], min: -2, max: 2, step: 0.1, value: 0.6, unit: "", digits: 1 },
    { id: "a21", name: ["a₂₁", "a₂₁"], min: -2, max: 2, step: 0.1, value: 0.2, unit: "", digits: 1 },
    { id: "a22", name: ["a₂₂", "a₂₂"], min: -2, max: 2, step: 0.1, value: 0.9, unit: "", digits: 1 },
    { id: "th1", name: ["关节角 θ₁", "Joint angle θ₁"], min: -180, max: 180, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "th2", name: ["关节角 θ₂", "Joint angle θ₂"], min: -180, max: 180, step: 1, value: 60, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "sing", text: ["让一个奇异值变为零：椭圆压扁成线段。", "Make one singular value zero: the ellipse collapses to a segment."],
      demo: { scene: "mat", set: { a11: 1, a12: 2, a21: 0.5, a22: 1 }, press: [] } },
    { id: "round", text: ["让单位圆变成同样大小的圆（两个奇异值都是 1）。", "Make the unit circle map to a circle of the same size (both singular values 1)."],
      demo: { scene: "mat", set: { a11: 0, a12: -1, a21: 1, a22: 0 }, press: [] } },
    { id: "wmax", robot: true, text: ["找出可操作度 w = σ₁σ₂ 最大的形态。", "Find the configuration with the largest manipulability w = σ₁σ₂."],
      demo: { scene: "arm", set: { th1: 30, th2: 90 }, press: [] } },
    { id: "flat", robot: true, text: ["把手臂伸直，看椭圆退化，条件数趋于无穷。", "Straighten the arm: the ellipse degenerates and the condition number blows up."],
      demo: { scene: "arm", set: { th1: 30, th2: 0 }, press: [] } },
  ],
  think: ["“让单位圆变成同样大小的圆”的矩阵是哪一类矩阵？它们的行列式可能是多少？", "Which matrices map the unit circle to a circle of the same size? What can their determinant be?"],

  L: [0.425, 0.392],
  A(api) {
    if (api.scene === "mat") return [[api.p.a11, api.p.a12], [api.p.a21, api.p.a22]];
    const t1 = api.p.th1 * Math.PI / 180, t12 = t1 + api.p.th2 * Math.PI / 180, [l1, l2] = this.L;
    return [[-l1 * Math.sin(t1) - l2 * Math.sin(t12), -l2 * Math.sin(t12)], [l1 * Math.cos(t1) + l2 * Math.cos(t12), l2 * Math.cos(t12)]];
  },
  svd(A) {   // AᵀA = [[a, b], [b, c]]
    const a = A[0][0] ** 2 + A[1][0] ** 2, b = A[0][0] * A[0][1] + A[1][0] * A[1][1], c = A[0][1] ** 2 + A[1][1] ** 2;
    const m = (a + c) / 2, r = Math.hypot((a - c) / 2, b), l1 = m + r, l2 = Math.max(0, m - r);
    const ph = 0.5 * Math.atan2(2 * b, a - c), v1 = [Math.cos(ph), Math.sin(ph)], v2 = [-Math.sin(ph), Math.cos(ph)];
    const s1 = Math.sqrt(l1), s2 = Math.sqrt(l2);
    const Av = (v) => [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]];
    const u1 = s1 > 1e-12 ? Av(v1).map((x) => x / s1) : [1, 0];
    const u2 = s2 > 1e-9 ? Av(v2).map((x) => x / s2) : [-u1[1], u1[0]];
    return { s1, s2, v1, v2, u1, u2, det: A[0][0] * A[1][1] - A[0][1] * A[1][0] };
  },
  reset(api, s) {},
  readouts(api, s) {
    const A = this.A(api), d = this.svd(A), f = api.fmt, mat = api.scene === "mat", dg = mat ? 2 : 4;
    if (mat && d.s2 < 1e-6) api.done("sing");
    if (mat && Math.abs(d.s1 - 1) < 1e-9 && Math.abs(d.s2 - 1) < 1e-9) api.done("round");
    if (!mat && Math.abs(Math.abs(api.p.th2) - 90) < 0.5) api.done("wmax");
    if (!mat && Math.abs(api.p.th2) < 0.5 && d.s2 < 1e-6) api.done("flat");
    const cond = d.s2 > 1e-6 ? f(d.s1 / d.s2, 2) : "∞";
    return [[["矩阵 A", "matrix A"], `[${f(A[0][0], dg)}, ${f(A[0][1], dg)}; ${f(A[1][0], dg)}, ${f(A[1][1], dg)}]`],
            [["奇异值 σ₁, σ₂", "singular values σ₁, σ₂"], `${f(d.s1, 4)}, ${f(d.s2, 4)}` + (mat ? "" : " m/rad")],
            [["条件数 σ₁/σ₂", "condition number σ₁/σ₂"], cond],
            [mat ? ["行列式 det A", "determinant det A"] : ["可操作度 w = σ₁σ₂", "manipulability w = σ₁σ₂"], f(mat ? d.det : d.s1 * d.s2, 4) + (mat ? "" : " m²")],
            [["u₁ 的方向", "direction of u₁"], f(Math.atan2(d.u1[1], d.u1[0]) * 180 / Math.PI, 1) + "°"]];
  },
  ellipse(api, A, cx, cy, k, color, width) {
    const ctx = api.ctx; ctx.beginPath();
    for (let i = 0; i <= 120; i++) { const a = i / 120 * 2 * Math.PI, x = Math.cos(a), y = Math.sin(a);
      const px = cx + k * (A[0][0] * x + A[0][1] * y), py = cy - k * (A[1][0] * x + A[1][1] * y); i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
    ctx.strokeStyle = color; ctx.lineWidth = width; ctx.stroke();
  },
  draw(api, s) {
    const { w, h } = api, A = this.A(api), d = this.svd(A);
    api.grid(w, h, 40);
    if (api.scene === "mat") {
      const k = Math.min(w * 0.18, h * 0.2), lx = w * 0.24, rx = w * 0.68, cy = h * 0.5;
      this.ellipse(api, [[1, 0], [0, 1]], lx, cy, k, api.css("--muted"), 1.5);
      api.arrow(lx, cy, lx + k * d.v1[0], cy - k * d.v1[1], api.css("--red"), 3); api.arrow(lx, cy, lx + k * d.v2[0], cy - k * d.v2[1], api.css("--blue"), 3);
      api.label("v₁", lx + k * d.v1[0] * 1.2, cy - k * d.v1[1] * 1.2, api.css("--red"), 14, "center");
      api.label("v₂", lx + k * d.v2[0] * 1.2, cy - k * d.v2[1] * 1.2, api.css("--blue"), 14, "center");
      api.label(api.T("输入：单位圆", "input: unit circle"), lx, h - 18, api.css("--muted"), 13, "center");
      const kr = k * Math.min(1, 1.4 / Math.max(d.s1, 1e-9));      // 输出太大时整体缩小
      this.ellipse(api, [[1, 0], [0, 1]], rx, cy, kr, api.css("--grid"), 1);
      this.ellipse(api, A, rx, cy, kr, api.css("--amber"), 2.5);
      api.arrow(rx, cy, rx + kr * d.s1 * d.u1[0], cy - kr * d.s1 * d.u1[1], api.css("--red"), 3);
      api.arrow(rx, cy, rx + kr * d.s2 * d.u2[0], cy - kr * d.s2 * d.u2[1], api.css("--blue"), 3);
      api.label("σ₁u₁", rx + kr * d.s1 * d.u1[0] * 1.1, cy - kr * d.s1 * d.u1[1] * 1.1 - 8, api.css("--red"), 14, "center");
      if (d.s2 > 0.05) api.label("σ₂u₂", rx + kr * d.s2 * d.u2[0] * 1.2, cy - kr * d.s2 * d.u2[1] * 1.2 + 10, api.css("--blue"), 14, "center");
      if (kr < k) api.label(api.T("（已按比例缩小）", "(scaled down)"), rx, 18, api.css("--muted"), 12, "center");
      api.label(api.T("输出：A 作用后的像", "output: image under A"), rx, h - 18, api.css("--muted"), 13, "center");
      api.arrow(w * 0.42, cy, w * 0.5, cy, api.css("--ink"), 2); api.label("A", w * 0.46, cy - 14, api.css("--ink"), 15, "center");
      return;
    }
    const k = Math.min(w, h) * 0.75, ox = w * 0.35, oy = h * 0.8;
    const pts = api.arm(ox, oy, [api.p.th1, api.p.th2], [this.L[0] * k, this.L[1] * k], api.css("--muted"), 10);
    const tip = pts[2], sc = k * 0.4;
    this.ellipse(api, A, tip[0], tip[1], sc, api.css("--amber"), 2.5);
    api.arrow(...tip, tip[0] + sc * d.s1 * d.u1[0], tip[1] - sc * d.s1 * d.u1[1], api.css("--red"), 3);
    if (d.s2 > 1e-3) api.arrow(...tip, tip[0] + sc * d.s2 * d.u2[0], tip[1] - sc * d.s2 * d.u2[1], api.css("--blue"), 3);
    api.label(api.T("椭圆：1 m/s 画成 0.4 m", "ellipse: 1 m/s drawn as 0.4 m"), 12, h - 16, api.css("--muted"), 12);
  },
});
