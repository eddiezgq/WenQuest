// 实验 2.2 换一个坐标系看同一个线性变换（配 2.2 节）。变换本身固定，只转动观察用的坐标系 {b}（相对 {s} 转过 φ）。
WQ.lab({
  title: ["实验 2.2 相似变换：换坐标系，矩阵变而迹与行列式不变", "Lab 2.2 Similarity: a new frame changes the matrix, not its trace and determinant"],
  goal: ["转动观察用的坐标系，看同一个线性变换的矩阵怎样变化，哪些量保持不变。",
         "Turn the frame you look from; see how the matrix of one fixed linear map changes, and what stays the same."],
  scenes: [
    { id: "wrist", robot: true, name: ["柔顺手腕的刚度", "Stiffness of a compliant wrist"],
      problem: { title: ["机器人问题：同一个刚度，两个矩阵", "Robot problem: one stiffness, two matrices"],
                 text: ["手腕在自身轴上的刚度是 2000 N/m 和 500 N/m，它的轴相对基座转过 30°。在转过 φ 的坐标系中，刚度矩阵是 Rᵀ K_s R。",
                        "The wrist is 2000 N/m and 500 N/m along its own axes, which are turned 30° from the base. In a frame turned by φ the stiffness matrix is Rᵀ K_s R."] } },
    { id: "shadow", name: ["窗棂的影子", "A window's shadow"],
      problem: { title: ["生活中的例子：影子是剪切加伸缩", "Everyday example: a shadow is a shear plus a scaling"],
                 text: ["窗面上的点到它在地上的影子：A = [1, 0.8; 0, 0.6]。换一个记录用的坐标系，矩阵变了，面积的放大倍数不变。",
                        "From a point on the window to its shadow: A = [1, 0.8; 0, 0.6]. Record it in another frame: the matrix changes, the area factor does not."] } },
  ],
  params: [{ id: "phi", name: ["坐标系转角 φ", "Frame angle φ"], min: -90, max: 90, step: 1, value: 0, unit: "°", digits: 0 }],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "diag", robot: true, text: ["找到使刚度矩阵成为对角矩阵的坐标系。", "Find the frame in which the stiffness matrix is diagonal."],
      demo: { scene: "wrist", set: { phi: 30 }, press: [] } },
    { id: "equal", robot: true, text: ["找到使两个对角元相等的坐标系。", "Find a frame in which the two diagonal entries are equal."],
      demo: { scene: "wrist", set: { phi: -15 }, press: [] } },
    { id: "turn90", text: ["把观察影子的坐标系转过 90°，读出矩阵，验证迹和行列式不变。", "Turn the frame for the shadow by 90°; read the matrix and check that trace and determinant are unchanged."],
      demo: { scene: "shadow", set: { phi: 90 }, press: [] } },
  ],
  think: ["刚度矩阵在哪个坐标系中最简单？这个坐标系的两根轴与 2.3 节的特征向量有什么关系？",
          "In which frame is the stiffness matrix simplest? How are its axes related to the eigenvectors of Section 2.3?"],

  A(api) {
    if (api.scene === "shadow") return [[1, 0.8], [0, 0.6]];
    const c = Math.cos(Math.PI / 6), s = Math.sin(Math.PI / 6);
    return [[2000 * c * c + 500 * s * s, 1500 * c * s], [1500 * c * s, 2000 * s * s + 500 * c * c]];
  },
  inFrame(api) {   // Rᵀ A R
    const A = this.A(api), t = api.p.phi * Math.PI / 180, c = Math.cos(t), s = Math.sin(t);
    const R = [[c, -s], [s, c]];
    const AR = [[A[0][0] * R[0][0] + A[0][1] * R[1][0], A[0][0] * R[0][1] + A[0][1] * R[1][1]],
                [A[1][0] * R[0][0] + A[1][1] * R[1][0], A[1][0] * R[0][1] + A[1][1] * R[1][1]]];
    return [[R[0][0] * AR[0][0] + R[1][0] * AR[1][0], R[0][0] * AR[0][1] + R[1][0] * AR[1][1]],
            [R[0][1] * AR[0][0] + R[1][1] * AR[1][0], R[0][1] * AR[0][1] + R[1][1] * AR[1][1]]];
  },
  reset(api, s) {},
  readouts(api, s) {
    const B = this.inFrame(api), f = api.fmt, wr = api.scene === "wrist", d = wr ? 1 : 3;
    const tr = B[0][0] + B[1][1], det = B[0][0] * B[1][1] - B[0][1] * B[1][0];
    if (wr && Math.abs(B[0][1]) < 1 && Math.abs(api.p.phi - 30) < 0.5) api.done("diag");
    if (wr && Math.abs(B[0][0] - B[1][1]) < 1) api.done("equal");
    if (!wr && Math.abs(api.p.phi - 90) < 0.5) api.done("turn90");
    return [[["在 {b} 中的矩阵", "matrix in {b}"], `[${f(B[0][0], d)}, ${f(B[0][1], d)}; ${f(B[1][0], d)}, ${f(B[1][1], d)}]`],
            [["迹", "trace"], f(tr, d) + (wr ? " N/m" : "")],
            [["行列式", "determinant"], wr ? f(det / 1e6, 4) + " × 10⁶ N²/m²" : f(det, 3)],
            [["非对角元", "off-diagonal entries"], `${f(B[0][1], d)}, ${f(B[1][0], d)}`]];
  },
  draw(api, s) {
    const { w, h } = api, cx = w * 0.42, cy = h * 0.52, k = Math.min(w, h) * 0.32;
    const A = this.A(api), sc = api.scene === "wrist" ? 1 / 2000 : 1;
    const X = (x, y) => [cx + k * x, cy - k * y];
    api.grid(w, h, 40);
    // 变换本身：单位圆的像（固定不动）
    const ctx = api.ctx;
    ctx.beginPath();
    for (let i = 0; i <= 120; i++) { const a = i / 120 * 2 * Math.PI, x = Math.cos(a), y = Math.sin(a);
      const p = X(sc * (A[0][0] * x + A[0][1] * y), sc * (A[1][0] * x + A[1][1] * y)); i ? ctx.lineTo(...p) : ctx.moveTo(...p); }
    ctx.strokeStyle = api.css("--amber"); ctx.lineWidth = 2; ctx.stroke();
    ctx.beginPath(); for (let i = 0; i <= 120; i++) { const a = i / 120 * 2 * Math.PI, p = X(Math.cos(a), Math.sin(a)); i ? ctx.lineTo(...p) : ctx.moveTo(...p); }
    ctx.strokeStyle = api.css("--grid"); ctx.lineWidth = 1; ctx.stroke();
    // {s} 与 {b}
    api.arrow(cx - k * 1.3, cy, cx + k * 1.3, cy, api.css("--muted"), 1.2); api.arrow(cx, cy + k * 1.3, cx, cy - k * 1.3, api.css("--muted"), 1.2);
    api.label("xₛ", cx + k * 1.33, cy + 12, api.css("--muted"), 13); api.label("yₛ", cx + 8, cy - k * 1.3, api.css("--muted"), 13);
    const t = api.p.phi * Math.PI / 180, u = [[Math.cos(t), Math.sin(t)], [-Math.sin(t), Math.cos(t)]];
    const cols = [api.css("--red"), api.css("--green")];
    u.forEach((e, j) => {
      const Ae = [sc * (A[0][0] * e[0] + A[0][1] * e[1]), sc * (A[1][0] * e[0] + A[1][1] * e[1])];
      api.line(cx, cy, ...X(e[0] * 1.4, e[1] * 1.4), cols[j], 1, [6, 4]);
      api.arrow(cx, cy, ...X(...e), cols[j], 2);
      api.arrow(cx, cy, ...X(...Ae), cols[j], 4);
      api.label(j ? "y_b" : "x_b", ...X(e[0] * 1.5, e[1] * 1.5), cols[j], 14, "center");
      api.label(j ? "A y_b" : "A x_b", ...X(Ae[0] * 1.12 + 0.06, Ae[1] * 1.12 + 0.06), cols[j], 13, "center");
    });
    api.label(api.T("金色：单位圆的像（变换本身，不随 φ 变化）", "gold: image of the unit circle (the map itself, independent of φ)"), 12, h - 16, api.css("--amber"), 12);
  },
});
