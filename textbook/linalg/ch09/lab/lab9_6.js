// 实验 9.6 换一组基看同一个映射（配 9.6 节）。镜线（或投影的直线）与 x 轴成 30°。新基 b1、b2 都是单位向量，方向角由滑块给出；
// P = (b1 b2)，映射在新基下的矩阵 B = P⁻¹AP。迹、行列式与基无关。
WQ.lab({
  title: ["实验 9.6 换一组基看同一个映射", "Lab 9.6 The same map in another basis"],
  goal: ["转动两个基向量，读出同一个反射（或投影）在新基下的矩阵 P⁻¹AP；找出让矩阵最简单的基；验证迹和行列式不随基改变。",
         "Turn the two basis vectors and read the matrix P⁻¹AP of the same reflection (or projection) in the new basis; find the basis that makes it simplest; check that trace and determinant do not change."],
  scenes: [
    { id: "refl", name: ["反射", "Reflection"],
      problem: { title: ["生活中的例子：镜子里的字", "Everyday example: writing in a mirror"],
                 text: ["关于一条斜线的反射，在标准基下的矩阵四个数都不为零，看不出它在做什么。换一组顺着镜子的基，它会变成什么样？",
                        "A reflection in a slanted line has four nonzero entries in the standard basis, which hides what it does. What does it look like in a basis aligned with the mirror?"] } },
    { id: "proj", name: ["投影", "Projection"],
      problem: { title: ["机器人问题：激光测距只看一个方向", "Robot problem: a range sensor sees one direction"],
                 text: ["一束激光沿 30° 方向测距，只能感知位移沿激光方向的那一部分：把位移换成它沿 30° 方向的分量向量，这是向 30° 直线的投影。找一组基，让它的矩阵最简单。",
                        "A laser along 30° senses only the part of a displacement along its beam: replacing the displacement by its component vector along 30° is a projection onto the 30° line. Find the basis that makes its matrix simplest."] } },
  ],
  params: [
    { id: "a1", name: ["b₁ 的方向角", "Direction of b₁"], min: 0, max: 180, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "a2", name: ["b₂ 的方向角", "Direction of b₂"], min: 0, max: 180, step: 5, value: 90, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "diag", text: ["在反射场景中，让新基下的矩阵变成 diag(1, −1)。", "In the reflection scene make the matrix in the new basis diag(1, −1)."],
      demo: { scene: "refl", set: { a1: 30, a2: 120 }, press: [] } },
    { id: "swap", text: ["在反射场景中，让 b₁ 不在镜线上，而新基下的矩阵为 [[0, 1], [1, 0]]（反射把 b₁ 与 b₂ 互换）。", "In the reflection scene, with b₁ off the mirror line, make the matrix [[0, 1], [1, 0]] (the reflection swaps b₁ and b₂)."],
      demo: { scene: "refl", set: { a1: 0, a2: 60 }, press: [] } },
    { id: "proj", text: ["在投影场景中，让新基下的矩阵为 [[1, 0.5], [0, 0]]，读出迹与行列式，与 A 的比较。", "In the projection scene make the matrix [[1, 0.5], [0, 0]]; read its trace and determinant and compare with A's."],
      demo: { scene: "proj", set: { a1: 30, a2: 90 }, press: [] } },
  ],
  think: ["反射场景中，换了许多组基，迹总是 0、行列式总是 −1。这两个数各说明了反射的什么性质？", "In the reflection scene, whatever the basis, the trace is 0 and the determinant −1. What does each say about the reflection?"],

  A(api) {   // the map in the standard basis: reflection 2uuᵀ − I or projection uuᵀ, u at 30°
    const t = Math.PI / 6, u = [Math.cos(t), Math.sin(t)], o = [[u[0] * u[0], u[0] * u[1]], [u[1] * u[0], u[1] * u[1]]];
    return api.scene === "refl" ? [[2 * o[0][0] - 1, 2 * o[0][1]], [2 * o[1][0], 2 * o[1][1] - 1]] : o;
  },
  basis(api) {
    const d = Math.PI / 180, b1 = [Math.cos(api.p.a1 * d), Math.sin(api.p.a1 * d)], b2 = [Math.cos(api.p.a2 * d), Math.sin(api.p.a2 * d)];
    return { b1, b2, P: [[b1[0], b2[0]], [b1[1], b2[1]]], det: b1[0] * b2[1] - b1[1] * b2[0] };
  },
  B(api) {
    const { P, det } = this.basis(api);
    if (Math.abs(det) < 1e-9) return null;
    const Pi = [[P[1][1] / det, -P[0][1] / det], [-P[1][0] / det, P[0][0] / det]];
    return api.la.mul(Pi, api.la.mul(this.A(api), P));
  },
  near(M, N) { return M && Math.abs(M[0][0] - N[0][0]) < 1e-6 && Math.abs(M[0][1] - N[0][1]) < 1e-6 && Math.abs(M[1][0] - N[1][0]) < 1e-6 && Math.abs(M[1][1] - N[1][1]) < 1e-6; },
  readouts(api) {
    const A = this.A(api), B = this.B(api), { b1 } = this.basis(api);
    const onLine = Math.abs(b1[0] * Math.sin(Math.PI / 6) - b1[1] * Math.cos(Math.PI / 6)) < 1e-9;
    if (api.scene === "refl" && this.near(B, [[1, 0], [0, -1]])) api.done("diag");
    if (api.scene === "refl" && !onLine && this.near(B, [[0, 1], [1, 0]])) api.done("swap");
    if (api.scene === "proj" && this.near(B, [[1, 0.5], [0, 0]])) api.done("proj");
    const tr = (M) => M[0][0] + M[1][1], dt = (M) => M[0][0] * M[1][1] - M[0][1] * M[1][0];
    const rows = [[["标准基下的矩阵 A", "Matrix A in the standard basis"], api.la.str(A, 3)],
                  [["基矩阵 P = (b₁ b₂)", "Basis matrix P = (b₁ b₂)"], api.la.str(this.basis(api).P, 3)]];
    if (!B) return rows.concat([[["新基下的矩阵 P⁻¹AP", "Matrix P⁻¹AP"], api.T("b₁、b₂ 共线，不是基", "b₁ and b₂ are parallel: not a basis")]]);
    return rows.concat([[["新基下的矩阵 P⁻¹AP", "Matrix P⁻¹AP in the new basis"], api.la.str(B, 3)],
                        [["迹：A 与 P⁻¹AP", "Trace: A and P⁻¹AP"], api.fmt(tr(A), 3) + " / " + api.fmt(tr(B), 3)],
                        [["行列式：A 与 P⁻¹AP", "Determinant: A and P⁻¹AP"], api.fmt(dt(A), 3) + " / " + api.fmt(dt(B), 3)]]);
  },
  draw(api) {
    const { w, h } = api, A = this.A(api), { b1, b2, P } = this.basis(api), la = api.la;
    const red = api.css("--red"), green = api.css("--green"), ink = api.css("--ink"), muted = api.css("--muted");
    const pl = api.plane({ cx: w / 2, cy: h * 0.55, s: Math.min(w, h) * 0.32, w, h });
    pl.grid(Math.abs(b1[0] * b2[1] - b1[1] * b2[0]) > 1e-9 ? P : null, { n: 4, alpha: 0.18 });
    pl.axes(muted);
    const u = [Math.cos(Math.PI / 6), Math.sin(Math.PI / 6)];
    const m0 = pl.X(-3 * u[0], -3 * u[1]), m1 = pl.X(3 * u[0], 3 * u[1]);
    api.line(m0[0], m0[1], m1[0], m1[1], ink, 1.5, [8, 5]);
    const flag = [[0.3, 0.15], [1.2, 0.15], [1.2, 0.5], [0.85, 0.5], [0.85, 0.75], [0.3, 0.75]];
    pl.curve(flag, muted, 1, "rgba(150,150,160,0.35)");
    pl.curve(flag.map((p) => la.mv(A, p)), api.css("--blue"), 2, api.scene === "refl" ? "rgba(60,110,200,0.35)" : null);
    pl.vec(b1, red, "b₁", 3); pl.vec(b2, green, "b₂", 3);
    const X = pl.X, Ab1 = la.mv(A, b1), Ab2 = la.mv(A, b2);
    [[Ab1, red, "Ab₁"], [Ab2, green, "Ab₂"]].forEach(([v, col, nm]) => {
      const o = X(0, 0), e = X(v[0], v[1]);
      api.ctx.setLineDash([5, 4]); api.arrow(o[0], o[1], e[0], e[1], col, 2); api.ctx.setLineDash([]);
      api.label(nm, e[0] + 8, e[1] + 18, col, 13);
    });
    api.label(api.scene === "refl" ? api.T("虚线：镜线（30°）", "Dashed: the mirror line (30°)") : api.T("虚线：投影的直线（30°）", "Dashed: the line of projection (30°)"), 12, 20, ink, 13);
  },
});
