// 实验 18.1 线性变换演示台：单位圆怎样变成椭圆（配 18.1 节；“分步”场景配 18.2.3 节）。
// 矩阵 A = [[a, b], [c, d]]；UR5e 上臂 0.425 m、前臂 0.392 m（零件库 2026.10.9 版关节表）。
WQ.lab({
  title: ["实验 18.1 线性变换演示台：单位圆变成椭圆", "Lab 18.1 Linear-map bench: the unit circle becomes an ellipse"],
  goal: ["拖动矩阵元素，看网格和单位圆怎样变形，读出奇异值与奇异向量；在机器人场景中看速度椭圆随肘关节角的变化。",
         "Drag the matrix entries, watch the grid and the unit circle deform, read the singular values and vectors; in the robot scene watch the velocity ellipse change with the elbow angle."],
  scenes: [
    { id: "mat", name: ["一般矩阵", "Any matrix"], hide: ["s", "t1", "t2"],
      problem: { title: ["生活中的例子：圆牌的影子", "Everyday example: the shadow of a round sign"],
                 text: ["阳光把倾斜的圆形标志牌投影到地面上，这是一个 2×2 线性映射。影子为什么总是椭圆？哪两条直径的影子仍然垂直？",
                        "Sunlight projects a tilted round sign onto the ground: a 2×2 linear map. Why is the shadow always an ellipse? Which two diameters keep perpendicular shadows?"] } },
    { id: "steps", name: ["分步：转—伸缩—转", "Steps: rotate–stretch–rotate"], hide: ["t1", "t2"],
      problem: { title: ["A = UΣVᵀ 的三步", "The three steps of A = UΣVᵀ"],
                 text: ["拖动“步骤”从 0 到 3：先由 Vᵀ 转动，再由 Σ 沿坐标轴伸缩，最后由 U 转动。", "Drag the step from 0 to 3: Vᵀ rotates, Σ stretches along the axes, U rotates."] } },
    { id: "robot", robot: true, name: ["UR5e 肩、肘关节", "UR5e shoulder and elbow"], hide: ["a", "b", "c", "d", "s"],
      problem: { title: ["机器人问题：腕心往哪个方向走得最快？", "Robot problem: in which direction can the wrist centre move fastest?"],
                 text: ["关节速度的长度不超过 1 rad/s 时，腕心速度的端点画出一个椭圆。改变两个关节角，看椭圆怎样变化，肘关节伸直时会发生什么。",
                        "With joint speeds of length at most 1 rad/s the wrist velocity traces an ellipse. Change the two joint angles; what happens as the elbow straightens?"] } },
  ],
  params: [
    { id: "a", name: ["a（第 1 行第 1 列）", "a (row 1, col 1)"], min: -5, max: 5, step: 0.1, value: 3, digits: 1 },
    { id: "b", name: ["b（第 1 行第 2 列）", "b (row 1, col 2)"], min: -5, max: 5, step: 0.1, value: 0, digits: 1 },
    { id: "c", name: ["c（第 2 行第 1 列）", "c (row 2, col 1)"], min: -5, max: 5, step: 0.1, value: 4, digits: 1 },
    { id: "d", name: ["d（第 2 行第 2 列）", "d (row 2, col 2)"], min: -5, max: 5, step: 0.1, value: 5, digits: 1 },
    { id: "s", name: ["步骤（0 → 3）", "Step (0 → 3)"], min: 0, max: 3, step: 0.01, value: 0, digits: 2 },
    { id: "t1", name: ["肩关节角 θ₁", "Shoulder angle θ₁"], min: -30, max: 120, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "t2", name: ["肘关节角 θ₂", "Elbow angle θ₂"], min: 0, max: 170, step: 0.5, value: 60, unit: "°", digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "circle", text: ["让椭圆变成圆（σ₁/σ₂ < 1.02）。这样的矩阵有什么特点？", "Make the ellipse a circle (σ₁/σ₂ < 1.02). What is special about such a matrix?"],
      demo: { scene: "mat", set: { a: 2, b: -1, c: 1, d: 2 }, press: [] } },
    { id: "flat", text: ["让椭圆压成一条线段（σ₂ < 0.02 σ₁）。此时行列式是多少？", "Flatten the ellipse to a segment (σ₂ < 0.02 σ₁). What is the determinant now?"],
      demo: { scene: "mat", set: { a: 1, b: 2, c: 2, d: 4 }, press: [] } },
    { id: "steps", text: ["在“分步”场景把步骤拖到 3，确认三步的结果与 A 直接作用的结果重合。", "In the steps scene drag the step to 3 and check the result equals A applied directly."],
      demo: { scene: "steps", set: { s: 3 }, press: [] } },
    { id: "round", robot: true, text: ["找出速度椭圆最“圆”的肘关节角（σ₁/σ₂ < 1.47）。", "Find the elbow angle with the roundest velocity ellipse (σ₁/σ₂ < 1.47)."],
      demo: { scene: "robot", set: { t2: 133 }, press: [] } },
    { id: "sing", robot: true, text: ["让肘关节接近伸直，使 σ₂ < 0.01 m/s。腕心哪个方向动不了？", "Nearly straighten the elbow so that σ₂ < 0.01 m/s. Which direction can the wrist no longer move?"],
      demo: { scene: "robot", set: { t2: 1.5 }, press: [] } },
  ],
  think: ["σ₁σ₂ 与 |det A| 为什么总是相等？用椭圆的面积解释。", "Why is σ₁σ₂ always equal to |det A|? Explain with the area of the ellipse."],

  mat(api) {
    if (api.scene !== "robot") return [[api.p.a, api.p.b], [api.p.c, api.p.d]];
    const l1 = 0.425, l2 = 0.392, t1 = api.p.t1 * Math.PI / 180, t12 = t1 + api.p.t2 * Math.PI / 180;
    return [[-l1 * Math.sin(t1) - l2 * Math.sin(t12), -l2 * Math.sin(t12)], [l1 * Math.cos(t1) + l2 * Math.cos(t12), l2 * Math.cos(t12)]];
  },
  readouts(api, s) {
    const A = this.mat(api), r = api.la.svd(A), d = api.la.det(A), k = r.s[1] > 1e-12 ? r.s[0] / r.s[1] : Infinity;
    const V = r.V, U = r.U;
    if (api.scene === "mat" && r.s[0] > 0.2 && k < 1.02) api.done("circle");
    if (api.scene === "mat" && r.s[0] > 0.5 && r.s[1] < 0.02 * r.s[0]) api.done("flat");
    if (api.scene === "steps" && api.p.s > 2.99) api.done("steps");
    if (api.scene === "robot" && k < 1.47) api.done("round");
    if (api.scene === "robot" && r.s[1] < 0.01) api.done("sing");
    const unit = api.scene === "robot" ? " m/s" : "";
    return [[["矩阵", "Matrix"], api.la.str(A, api.scene === "robot" ? 4 : 1)],
            [["σ₁, σ₂", "σ₁, σ₂"], api.fmt(r.s[0], 4) + ", " + api.fmt(r.s[1], 4) + unit],
            [["v₁（输入方向）", "v₁ (input)"], api.la.vstr([V[0][0], V[1][0]], 3)],
            [["u₁（椭圆长轴方向）", "u₁ (major axis)"], api.la.vstr([U[0][0], U[1][0]], 3)],
            [["det A 与 σ₁σ₂", "det A and σ₁σ₂"], api.fmt(d, 4) + " / " + api.fmt(r.s[0] * r.s[1], 4)],
            [["σ₁/σ₂", "σ₁/σ₂"], isFinite(k) ? api.fmt(k, 3) : "∞"]];
  },
  draw(api, s) {
    const { w, h } = api, A = this.mat(api), r = api.la.svd(A);
    const V = r.V, U = r.U, red = api.css("--red"), green = api.css("--green"), muted = api.css("--muted");
    if (api.scene === "robot") {
      const k = h * 0.75, ox = w * 0.28, oy = h * 0.88, X = (x, y) => [ox + k * x, oy - k * y];
      const l1 = 0.425, l2 = 0.392, t1 = api.p.t1 * Math.PI / 180, t12 = t1 + api.p.t2 * Math.PI / 180;
      const j = [l1 * Math.cos(t1), l1 * Math.sin(t1)], p = [j[0] + l2 * Math.cos(t12), j[1] + l2 * Math.sin(t12)];
      api.line(...X(-0.3, 0), ...X(1.0, 0), muted, 1);
      api.line(...X(0, 0), ...X(...j), api.css("--blue"), 10); api.line(...X(...j), ...X(...p), api.css("--blue"), 8);
      api.circle(...X(0, 0), 7, api.css("--panel"), api.css("--ink")); api.circle(...X(...j), 6, api.css("--panel"), api.css("--ink"));
      const e = 0.35, pts = [];
      for (let i = 0; i <= 120; i++) { const t = i * Math.PI / 60, v = api.la.mv(A, [Math.cos(t), Math.sin(t)]); pts.push(X(p[0] + e * v[0], p[1] + e * v[1])); }
      const c = api.ctx; c.beginPath(); pts.forEach((q, i) => (i ? c.lineTo(...q) : c.moveTo(...q))); c.strokeStyle = red; c.lineWidth = 2; c.stroke();
      const a1 = X(p[0] + e * r.s[0] * U[0][0], p[1] + e * r.s[0] * U[1][0]), a2 = X(p[0] + e * r.s[1] * U[0][1], p[1] + e * r.s[1] * U[1][1]);
      api.arrow(...X(...p), ...a1, red, 3); api.arrow(...X(...p), ...a2, green, 3);
      api.label(api.T("腕心", "wrist"), ...X(p[0] + 0.03, p[1] - 0.05), muted, 12);
      api.label(api.T("0.35 m 代表 1 m/s", "0.35 m ≙ 1 m/s"), w - 10, 16, muted, 12, "right");
      return;
    }
    const big = Math.max(1, r.s[0]);
    if (api.scene === "mat") {
      const sc = Math.min(w * 0.22, h * 0.42);
      const L = api.plane({ cx: w * 0.22, cy: h * 0.5, s: sc * 0.8, w, h });
      const R = api.plane({ cx: w * 0.68, cy: h * 0.5, s: sc * 0.8 / big * 1.0, w, h });
      L.grid(null, { n: 3, alpha: 0.25 }); L.circle(null, api.css("--ink"));
      L.vec([V[0][0], V[1][0]], red, "v₁"); L.vec([V[0][1], V[1][1]], green, "v₂");
      R.grid(A, { n: 3, alpha: 0.25 }); R.circle(A, api.css("--ink"), "rgba(201,143,0,0.12)");
      R.vec([r.s[0] * U[0][0], r.s[0] * U[1][0]], red, "σ₁u₁"); R.vec([r.s[1] * U[0][1], r.s[1] * U[1][1]], green, "σ₂u₂");
      api.label(api.T("单位圆", "unit circle"), w * 0.22, 16, muted, 13, "center");
      api.label(api.T("像（按比例缩小）", "image (scaled)"), w * 0.68, 16, muted, 13, "center");
      api.arrow(w * 0.42, h * 0.5, w * 0.47, h * 0.5, muted, 2); api.label("A", w * 0.445, h * 0.5 - 14, muted, 14, "center");
      return;
    }
    // steps: M(s) = U-part · Σ-part · Vᵀ-part
    const Ur = U.map((row) => row.slice()), Vr = V.map((row) => row.slice());
    if (api.la.det(Ur) < 0 && api.la.det(Vr) < 0) { Ur.forEach((row) => (row[1] = -row[1])); Vr.forEach((row) => (row[1] = -row[1])); }
    const part = (Q, u) => {   // rotation part of the way; a reflection is blended linearly
      if (api.la.det(Q) > 0) { const a = Math.atan2(Q[1][0], Q[0][0]) * u; return [[Math.cos(a), -Math.sin(a)], [Math.sin(a), Math.cos(a)]]; }
      return [[1 - u + u * Q[0][0], u * Q[0][1]], [u * Q[1][0], 1 - u + u * Q[1][1]]];
    };
    const x = api.p.s, u1 = Math.min(1, x), u2 = Math.min(1, Math.max(0, x - 1)), u3 = Math.min(1, Math.max(0, x - 2));
    const Vt = part(api.la.T(Vr), u1), S = [[1 + u2 * (r.s[0] - 1), 0], [0, 1 + u2 * (r.s[1] - 1)]], Uq = part(Ur, u3);
    const M = api.la.mul(Uq, api.la.mul(S, Vt));
    const P = api.plane({ cx: w * 0.42, cy: h * 0.5, s: Math.min(w, h) * 0.38 / big, w, h });
    P.grid(M, { n: 3, alpha: 0.25 });
    if (x > 2.99) P.circle(A, api.css("--blue"), null, [6, 5]);
    P.circle(M, api.css("--ink"), "rgba(201,143,0,0.12)");
    const flag = [[0.25, 0.15], [0.56, 0.15], [0.56, 0.27], [0.44, 0.27], [0.44, 0.36], [0.25, 0.36]].map((q) => api.la.mv(M, q));
    P.curve(flag, api.css("--amber"), 1.5, "rgba(201,143,0,0.7)");
    P.vec(api.la.mv(M, [Vr[0][0], Vr[1][0]]), red); P.vec(api.la.mv(M, [Vr[0][1], Vr[1][1]]), green);
    const name = x < 1 ? api.T("① Vᵀ：转", "① Vᵀ: rotate") : x < 2 ? api.T("② Σ：沿坐标轴伸缩", "② Σ: stretch") : api.T("③ U：再转", "③ U: rotate");
    api.label(name, w * 0.8, h * 0.12, api.css("--ink"), 15, "center");
    if (x > 2.99) api.label(api.T("虚线：A 直接作用", "dashed: A applied directly"), w * 0.8, h * 0.2, api.css("--blue"), 12, "center");
  },
});
