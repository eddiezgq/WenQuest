// 实验 13.1 寻找不改变方向的向量（配 13.1、13.2 节）。转动单位向量 v 的方向 φ，看 Av 是否与 v 共线。
// 场景 1：柔顺腕（刚度 K = [[4, 1], [1, 4]] kN/m），沿方向 φ 推 10 N，位移 d = K⁻¹F；只有沿主轴推时位移与力同向。
// 场景 2：A = [[3, 1], [0, 2]]，两个特征方向互不垂直。场景 3：A = 1.2·R(40°)（旋转加伸缩），没有实的特征方向。
WQ.lab({
  title: ["实验 13.1 寻找不改变方向的向量", "Lab 13.1 Looking for vectors that keep their direction"],
  goal: ["转动向量的方向，观察它经过矩阵变换后的方向；找出变换前后共线的方向（特征向量），读出伸缩倍数（特征值）；体会旋转为什么没有实的特征向量。",
         "Turn a vector and watch the direction of its image; find the directions where the vector and its image are collinear (eigenvectors), read the stretch (eigenvalue), and see why a rotation has no real eigenvector."],
  scenes: [
    { id: "stiff", robot: true, name: ["柔顺腕", "Compliant wrist"],
      problem: { title: ["往哪个方向推，工具就往哪个方向退？", "Which push makes the tool give way in the same direction?"],
                 text: ["装配用的柔顺腕在两个方向上软硬不同。沿 φ 方向推工具尖端 10 N，位移 d = K⁻¹F 一般会偏到一边。找出位移与推力同向的方向，并读出这两个方向上的刚度。",
                        "An assembly wrist is stiffer one way than another. Push the tool tip with 10 N along φ: the deflection d = K⁻¹F usually swerves. Find the directions where deflection and push agree, and read the stiffness along them."] } },
    { id: "shear", name: ["A = [[3, 1], [0, 2]]", "A = [[3, 1], [0, 2]]"],
      problem: { title: ["两个特征方向不一定垂直", "Eigen-directions need not be perpendicular"],
                 text: ["转动 v，找出 Av 与 v 共线的两个方向，读出每个方向上的伸缩倍数。", "Turn v, find the two directions where Av is collinear with v, and read the stretch along each."] } },
    { id: "rot", name: ["旋转加伸缩", "Rotation and stretch"],
      problem: { title: ["旋转没有实的特征方向", "A rotation has no real eigen-direction"],
                 text: ["A = 1.2·R(40°)：每个向量都被转过 40° 再拉长。转动 v 至少半圈，看能不能找到 Av 与 v 共线的方向。", "A = 1.2·R(40°) turns every vector by 40° and stretches it. Turn v through at least half a turn: is there any direction where Av is collinear with v?"] } },
  ],
  params: [{ id: "phi", name: ["v 的方向 φ", "Direction φ of v"], min: 0, max: 359, step: 1, value: 0, unit: "°", digits: 0 }],
  buttons: [],
  tasks: [
    { id: "hard", robot: true, text: ["在柔顺腕场景中找出“硬”的主轴：位移与推力同向（夹角小于 0.5°），且刚度 |F|/|d| 为 5 kN/m。", "In the wrist scene find the stiff axis: deflection along the push (within 0.5°) and stiffness |F|/|d| of 5 kN/m."],
      demo: { scene: "stiff", set: { phi: 45 }, press: [] } },
    { id: "soft", robot: true, text: ["再找出“软”的主轴（刚度 3 kN/m），并读出两条主轴的夹角。", "Then find the soft axis (3 kN/m) and read the angle between the two axes."],
      demo: { scene: "stiff", set: { phi: 135 }, press: [] } },
    { id: "two", text: ["在 A = [[3, 1], [0, 2]] 场景中先后找到两个特征方向（夹角小于 0.5°），读出两个伸缩倍数。", "In the A = [[3, 1], [0, 2]] scene find both eigen-directions in turn (within 0.5°) and read the two stretches."],
      demo: { scene: "shear", set: { phi: 135 }, press: [] } },
    { id: "none", text: ["在旋转加伸缩场景中让 v 转过至少半圈（φ 的变化范围达到 180°），确认 Av 与 v 的夹角始终是 40°。", "In the rotation scene turn v through at least half a turn (φ ranging over 180°) and check that the angle between Av and v stays at 40°."],
      demo: { scene: "rot", set: { phi: 200 }, press: [] } },
  ],
  think: ["柔顺腕的两条主轴互相垂直，A = [[3, 1], [0, 2]] 的两个特征方向却不垂直。区别在哪里？（提示：看矩阵是否对称，第 14 章。）",
          "The wrist's two axes are perpendicular, but the eigen-directions of [[3, 1], [0, 2]] are not. What makes the difference? (Hint: is the matrix symmetric? Chapter 14.)"],

  mat(api) {
    if (api.scene === "stiff") return [[4 / 15, -1 / 15], [-1 / 15, 4 / 15]];   // K⁻¹ (mm per N); K = [[4, 1], [1, 4]] kN/m
    if (api.scene === "shear") return [[3, 1], [0, 2]];
    const c = Math.cos(40 * Math.PI / 180), s = Math.sin(40 * Math.PI / 180);
    return [[1.2 * c, -1.2 * s], [1.2 * s, 1.2 * c]];
  },
  reset(api, s) {
    const M = this.mat(api), p = api.p.phi * Math.PI / 180, v = [Math.cos(p), Math.sin(p)];
    const w = [M[0][0] * v[0] + M[0][1] * v[1], M[1][0] * v[0] + M[1][1] * v[1]];
    s.v = v; s.w = w; s.norm = Math.hypot(...w);
    s.ang = Math.atan2(v[0] * w[1] - v[1] * w[0], v[0] * w[0] + v[1] * w[1]) * 180 / Math.PI;   // signed angle from v to Av
    s.col = Math.min(Math.abs(s.ang), 180 - Math.abs(s.ang));   // 0 when collinear (same or opposite)
  },
  readouts(api, s) {
    if (!s.v) return [];
    const f = api.fmt;
    this.seen = this.seen || {};   // what the student has visited in each scene (cleared when the scene is entered again)
    if (this.lastScene !== api.scene) { this.seen[api.scene] = null; this.lastScene = api.scene; }
    const sc = this.seen[api.scene] = this.seen[api.scene] || { lo: 999, hi: -999, found: {} };
    sc.lo = Math.min(sc.lo, api.p.phi); sc.hi = Math.max(sc.hi, api.p.phi);
    const lam = Math.sign(s.v[0] * s.w[0] + s.v[1] * s.w[1]) * s.norm;
    if (api.scene === "stiff") {
      const kst = 1 / s.norm;   // kN/m, since |d| in mm for |F| = 1 N
      if (s.col < 0.5 && Math.abs(kst - 5) < 0.05) api.done("hard");
      if (s.col < 0.5 && Math.abs(kst - 3) < 0.05) api.done("soft");
      return [[["推力方向 φ", "Push direction φ"], api.p.phi + "°"],
              [["位移 d（推 10 N）/ mm", "Deflection d (10 N push) / mm"], "(" + f(10 * s.w[0], 3) + ", " + f(10 * s.w[1], 3) + ")"],
              [["位移方向与推力方向的夹角", "Angle between deflection and push"], f(s.ang, 2) + "°"],
              [["这个方向上的刚度 |F|/|d|", "Stiffness |F|/|d| along this direction"], f(kst, 3) + " kN/m"]];
    }
    if (api.scene === "shear" && s.col < 0.5) {
      sc.found[Math.round(Math.abs(lam))] = true;
      if (sc.found[3] && sc.found[2]) api.done("two");
    }
    if (api.scene === "rot" && sc.hi - sc.lo >= 180) api.done("none");
    return [[["v", "v"], "(" + f(s.v[0], 3) + ", " + f(s.v[1], 3) + ")"],
            [["Av", "Av"], "(" + f(s.w[0], 3) + ", " + f(s.w[1], 3) + ")"],
            [["从 v 到 Av 转过的角度", "Angle turned from v to Av"], f(s.ang, 2) + "°"],
            [["|Av| / |v|", "|Av| / |v|"], f(s.norm, 3)],
            [["共线时的伸缩倍数 λ", "Stretch λ when collinear"], s.col < 0.5 ? f(lam, 3) : "—"],
            [["已经转过的 φ 范围", "Range of φ visited"], sc.lo + "° ～ " + sc.hi + "°"]];
  },
  draw(api, s) {
    if (!s.v) return;
    const { w, h } = api, ink = api.css("--ink"), mu = api.css("--muted"), cx = w / 2, cy = h / 2;
    const big = api.scene === "stiff" ? 1 / 3 : api.scene === "shear" ? 3.6 : 1.2;
    const R = Math.min(w, h) * 0.42 / Math.max(1, big * (api.scene === "stiff" ? 3 : 1)), sw = api.scene === "stiff" ? 3 * R : R;
    api.line(cx - w / 2 + 10, cy, cx + w / 2 - 10, cy, mu, 1); api.line(cx, 10, cx, h - 10, mu, 1);
    api.ctx.beginPath(); api.ctx.arc(cx, cy, R, 0, 2 * Math.PI); api.ctx.strokeStyle = mu; api.ctx.lineWidth = 1; api.ctx.setLineDash([3, 4]); api.ctx.stroke(); api.ctx.setLineDash([]);
    const L = Math.max(w, h);
    api.line(cx - L * s.v[0], cy + L * s.v[1], cx + L * s.v[0], cy - L * s.v[1], api.css("--grid"), 1);
    const good = s.col < 0.5, cv = api.css("--blue"), cw = good ? api.css("--green") : api.css("--red");
    api.arrow(cx, cy, cx + R * s.v[0], cy - R * s.v[1], cv, 3);
    api.arrow(cx, cy, cx + sw * s.w[0], cy - sw * s.w[1], cw, 3);
    const nv = api.scene === "stiff" ? api.T("推力 F", "push F") : "v", nw = api.scene === "stiff" ? api.T("位移 d", "deflection d") : "Av";
    api.label(nv, cx + R * s.v[0] * 1.08 + 4, cy - R * s.v[1] * 1.08, cv, 14);
    api.label(nw, cx + sw * s.w[0] * 1.06 + 4, cy - sw * s.w[1] * 1.06 + 14, cw, 14);
    if (good) api.label(api.T("共线！", "collinear!"), 16, 24, api.css("--green"), 15);
  },
});
