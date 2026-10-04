// 实验 6.1 行列式：有向面积（配 6.1、6.6 节）。拖动 2×2 矩阵的四个元素，看单位正方形的像、面积与方向；
// “乘积”场景中 B 固定为 [[1, 0.5], [0, 1.5]]（det B = 1.5），看 det(AB) = det A · det B。
WQ.lab({
  title: ["实验 6.1 行列式：有向面积", "Lab 6.1 The determinant as signed area"],
  goal: ["拖动矩阵元素，读出单位正方形的像的面积与方向，与行列式比较；让平行四边形压扁、翻面；验证乘积的行列式等于行列式之积。",
         "Drag the matrix entries; read the area and orientation of the image of the unit square and compare with the determinant; flatten and flip the parallelogram; check that det(AB) = det A det B."],
  scenes: [
    { id: "area", name: ["有向面积", "Signed area"],
      problem: { title: ["生活中的例子：地图的比例尺", "Everyday example: map scale"],
                 text: ["把一张地图斜着拉伸，地图上每一块地的面积都按同一个倍数变化。这个倍数是多少？地图会不会被“翻面”？",
                        "Stretch a map obliquely: every field's area changes by the same factor. What is the factor? Can the map be flipped?"] } },
    { id: "prod", name: ["乘积", "Product"],
      problem: { title: ["先 B 后 A：面积倍数相乘", "B then A: area factors multiply"],
                 text: ["左图是 B 作用后的平行四边形，右图是再作用 A 之后的结果。比较三个行列式。", "Left: after B; right: after A as well. Compare the three determinants."] } },
  ],
  params: [
    { id: "a", name: ["a（第 1 行第 1 列）", "a (row 1, col 1)"], min: -3, max: 3, step: 0.1, value: 2, digits: 1 },
    { id: "b", name: ["b（第 1 行第 2 列）", "b (row 1, col 2)"], min: -3, max: 3, step: 0.1, value: 0.5, digits: 1 },
    { id: "c", name: ["c（第 2 行第 1 列）", "c (row 2, col 1)"], min: -3, max: 3, step: 0.1, value: 0.5, digits: 1 },
    { id: "d", name: ["d（第 2 行第 2 列）", "d (row 2, col 2)"], min: -3, max: 3, step: 0.1, value: 1.5, digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "six", text: ["让单位正方形的像面积为 6、方向不变（det A = 6）。", "Make the image have area 6 with the same orientation (det A = 6)."],
      demo: { scene: "area", set: { a: 3, b: 0, c: 1, d: 2 }, press: [] } },
    { id: "flat", text: ["让 A 的元素都不为零，而平行四边形压成线段（det A = 0）。", "With every entry nonzero, flatten the parallelogram to a segment (det A = 0)."],
      demo: { scene: "area", set: { a: 1, b: 2, c: 1.5, d: 3 }, press: [] } },
    { id: "flip", text: ["让图形翻面且面积为 2（det A = −2）。", "Flip the figure with area 2 (det A = −2)."],
      demo: { scene: "area", set: { a: 0, b: 1, c: 2, d: 0 }, press: [] } },
    { id: "prod", text: ["在“乘积”场景中让 det A = 2，确认 det(AB) = 3。", "In the product scene make det A = 2 and check det(AB) = 3."],
      demo: { scene: "prod", set: { a: 2, b: 0, c: 0, d: 1 }, press: [] } },
  ],
  think: ["剪切矩阵 [[1, k], [0, 1]] 把正方形拉成了平行四边形，为什么面积不变？", "The shear [[1, k], [0, 1]] turns the square into a parallelogram; why is the area unchanged?"],

  B: [[1, 0.5], [0, 1.5]],
  A(api) { return [[api.p.a, api.p.b], [api.p.c, api.p.d]]; },
  det(M) { return M[0][0] * M[1][1] - M[0][1] * M[1][0]; },
  near(x, y) { return Math.abs(x - y) < 1e-9; },
  readouts(api) {
    const A = this.A(api), dA = this.det(A), p = api.p;
    if (api.scene === "area" && this.near(dA, 6)) api.done("six");
    if (api.scene === "area" && this.near(dA, 0) && [p.a, p.b, p.c, p.d].every((x) => Math.abs(x) > 1e-9)) api.done("flat");
    if (api.scene === "area" && this.near(dA, -2)) api.done("flip");
    const rows = [[["矩阵 A", "Matrix A"], api.la.str(A, 1)], [["det A = ad − bc", "det A = ad − bc"], api.fmt(dA, 2)],
                  [["面积 |det A|", "Area |det A|"], api.fmt(Math.abs(dA), 2)],
                  [["方向", "Orientation"], dA > 1e-9 ? api.T("不变（逆时针）", "kept (counter-clockwise)") : dA < -1e-9 ? api.T("翻面（顺时针）", "flipped (clockwise)") : api.T("压扁（面积为零）", "flattened (zero area)")]];
    if (api.scene !== "prod") return rows;
    const AB = api.la.mul(A, this.B), dAB = this.det(AB);
    if (this.near(dA, 2) && this.near(dAB, 3)) api.done("prod");
    return rows.concat([[["det B", "det B"], "1.50"], [["det(AB)", "det(AB)"], api.fmt(dAB, 2)],
                        [["det A · det B", "det A · det B"], api.fmt(dA * 1.5, 2)]]);
  },
  draw(api) {
    const { w, h } = api, A = this.A(api), muted = api.css("--muted"), red = api.css("--red"), green = api.css("--green");
    const sq = [[0, 0], [1, 0], [1, 1], [0, 1]];
    const panel = (M, cx, s, name) => {
      const P = api.plane({ cx, cy: h * 0.55, s, w, h });
      P.grid(M, { n: 4, alpha: 0.18 });
      const d = this.det(M);
      P.curve(sq.map((q) => api.la.mv(M, q)), api.css("--ink"), 1.5, d >= 0 ? "rgba(201,143,0,0.5)" : "rgba(160,100,200,0.5)");
      P.vec([M[0][0], M[1][0]], red, "1"); P.vec([M[0][1], M[1][1]], green, "2");
      api.label(name + "  det = " + api.fmt(d, 2), cx, 18, api.css("--ink"), 13, "center");
    };
    const c = api.ctx;
    if (api.scene === "area") {
      c.save(); c.beginPath(); c.rect(0, 26, w * 0.4, h - 26); c.clip(); panel([[1, 0], [0, 1]], w * 0.2, Math.min(w, h) * 0.09, "I"); c.restore();
      c.save(); c.beginPath(); c.rect(w * 0.4, 26, w * 0.6, h - 26); c.clip(); panel(A, w * 0.7, Math.min(w, h) * 0.09, "A"); c.restore();
      return;
    }
    const AB = api.la.mul(A, this.B);
    c.save(); c.beginPath(); c.rect(0, 26, w * 0.5, h - 26); c.clip(); panel(this.B, w * 0.25, Math.min(w, h) * 0.08, "B"); c.restore();
    c.save(); c.beginPath(); c.rect(w * 0.5, 26, w * 0.5, h - 26); c.clip(); panel(AB, w * 0.75, Math.min(w, h) * 0.08, "AB"); c.restore();
    api.line(w * 0.5, 30, w * 0.5, h - 10, api.css("--line"), 1);
  },
});
