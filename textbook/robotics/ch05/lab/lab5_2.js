// 实验 5.2 搭一个齐次变换（配 5.2 节）。平面情形：3×3 齐次矩阵 D = [[R(θ), p], [0, 1]] 作为位移算子作用在工件上。
// 机器人场景：垫块 0.4 m × 0.2 m，起初中心在 {a} 的原点；夹具的位姿为 θ = 90°、p = (0.8, 0.5) m。
// 点 P（垫块右上角）按 (P, 1) 变换，既转又移；方向 v（垫块长边方向）按 (v, 0) 变换，只转不移。
// 生活场景：沙发 2.0 m × 0.9 m，D = Trans(p)·[绕沙发自身中心 c 转 θ]，由式 (5.2.10) 得第三列 = c − R c + p。
WQ.lab({
  title: ["实验 5.2 搭一个齐次变换", "Lab 5.2 Building a homogeneous transform"],
  goal: ["拖动转角和平移量，看 3×3 齐次矩阵怎样把工件上的点和方向变到新位置；体会第三列的含义和“点既转又移、方向只转不移”。",
         "Drag the angle and the shift: see how the 3×3 homogeneous matrix moves a point and a direction of the part; understand the third column and why points move but directions only turn."],
  scenes: [
    { id: "fix", robot: true, name: ["垫块放进夹具", "Block into the fixture"],
      problem: { title: ["机器人问题：一次位移把垫块放进夹具", "Robot problem: one displacement puts the block into the fixture"],
                 text: ["垫块中心在原点、长边沿 x 轴。夹具在 (0.8, 0.5) m 处，转了 90°。写出把垫块放进去的齐次矩阵。",
                        "The block is centred at the origin with its long edge along x. The fixture is at (0.8, 0.5) m, turned 90°. Write the homogeneous matrix that puts it there."] } },
    { id: "sofa", name: ["沙发挪进凹位", "Sofa into the alcove"],
      problem: { title: ["生活中的例子：挪沙发", "Everyday example: moving a sofa"],
                 text: ["沙发先绕自身中心转，再整体平移。墙角的凹位要求沙发竖着放，中心移到 (1.0, 1.4) m。",
                        "The sofa turns about its own centre, then shifts. The alcove needs it upright, centred at (1.0, 1.4) m."] },
      params: { px: { min: -1, max: 1.5, value: 0 }, py: { min: -1, max: 1.5, value: 0 } } },
  ],
  params: [
    { id: "th", name: ["转角 θ", "Angle θ"], min: -180, max: 180, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "px", name: ["平移 x", "Shift x"], min: -1, max: 1.5, step: 0.1, value: 0, unit: "m", digits: 1 },
    { id: "py", name: ["平移 y", "Shift y"], min: -1, max: 1.5, step: 0.1, value: 0, unit: "m", digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "trans", robot: true, text: ["转角保持 0，只平移：方向 v 的读数 (v, 0) 不变，点 P 的读数改变。", "Keep θ = 0 and only shift: the direction (v, 0) stays, the point P changes."],
      demo: { scene: "fix", set: { th: 0, px: 0.5, py: 0.3 }, press: [] } },
    { id: "fix", robot: true, text: ["把垫块放进夹具（θ = 90°，平移 (0.8, 0.5) m），读出矩阵第三列：它是垫块中心的新位置。", "Put the block into the fixture (θ = 90°, shift (0.8, 0.5) m); read column 3: the block centre's new position."],
      demo: { scene: "fix", set: { th: 90, px: 0.8, py: 0.5 }, press: [] } },
    { id: "sofa", text: ["把沙发绕自身中心转 90°，再平移进凹位。", "Turn the sofa 90° about its own centre, then shift it into the alcove."],
      demo: { scene: "sofa", set: { th: 90, px: 0, py: 0.5 }, press: [] } },
  ],
  think: ["在沙发场景中，矩阵第三列为什么不等于你拖动的平移量？用式 (5.2.10) 解释。",
          "In the sofa scene, why is column 3 not equal to the shift you dragged? Explain with Eq. (5.2.10)."],

  shape(api) {
    return api.scene === "fix" ? { L: 0.4, W: 0.2, c: [0, 0], target: [0.8, 0.5, 90] }
      : { L: 2.0, W: 0.9, c: [1.0, 0.9], target: [1.0, 1.4, 90] };
  },
  D(api) {   // 3×3 齐次矩阵（按行）
    const t = api.p.th * Math.PI / 180, c = Math.cos(t), s = Math.sin(t), g = this.shape(api);
    let tx = api.p.px, ty = api.p.py;
    if (api.scene === "sofa") { tx += g.c[0] - (c * g.c[0] - s * g.c[1]); ty += g.c[1] - (s * g.c[0] + c * g.c[1]); }
    return [[c, -s, tx], [s, c, ty], [0, 0, 1]];
  },
  ap(D, x, y, w) { return [D[0][0] * x + D[0][1] * y + D[0][2] * w, D[1][0] * x + D[1][1] * y + D[1][2] * w, w]; },
  reset(api, s) {},
  readouts(api, s) {
    const D = this.D(api), g = this.shape(api);
    const P = [g.c[0] + g.L / 2, g.c[1] + g.W / 2], P2 = this.ap(D, P[0], P[1], 1), v2 = this.ap(D, 1, 0, 0);
    const near = (a, b) => Math.abs(a - b) < 1e-6;
    if (api.scene === "fix" && near(api.p.th, 0) && (Math.abs(api.p.px) > 1e-6 || Math.abs(api.p.py) > 1e-6)) api.done("trans");
    if (api.scene === "fix" && near(api.p.th, 90) && near(api.p.px, 0.8) && near(api.p.py, 0.5)) api.done("fix");
    const ctr = this.ap(D, g.c[0], g.c[1], 1);
    if (api.scene === "sofa" && near(Math.abs(api.p.th), 90) && near(ctr[0], 1.0) && near(ctr[1], 1.4)) api.done("sofa");
    const r = (row) => `[${row.map((x) => api.fmt(x, 3)).join("  ")}]`;
    return [
      [["D 第 1 行", "D row 1"], r(D[0])], [["D 第 2 行", "D row 2"], r(D[1])], [["D 第 3 行", "D row 3"], r(D[2])],
      [["点 P：(P′, 1)", "point P: (P′, 1)"], `(${api.fmt(P2[0], 3)}, ${api.fmt(P2[1], 3)}, 1)`],
      [["方向 v：(v′, 0)", "direction v: (v′, 0)"], `(${api.fmt(v2[0], 3)}, ${api.fmt(v2[1], 3)}, 0)`],
      [[api.scene === "fix" ? "垫块中心" : "沙发中心", api.scene === "fix" ? "block centre" : "sofa centre"], `(${api.fmt(ctr[0], 3)}, ${api.fmt(ctr[1], 3)}) m`],
    ];
  },
  draw(api, s) {
    const { w, h } = api, fix = api.scene === "fix";
    const k = fix ? Math.min(w / 3.2, h / 2.6) : Math.min(w / 4.4, h / 3.4);
    const ox = fix ? w * 0.32 : w * 0.25, oy = fix ? h * 0.7 : h * 0.82;
    const X = (x, y) => [ox + k * x, oy - k * y];
    const g = this.shape(api), D = this.D(api);
    const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([a, b]) => [g.c[0] + a * g.L / 2, g.c[1] + b * g.W / 2]);
    const poly = (pts, fill, stroke, dash) => {
      const c = api.ctx; c.beginPath(); pts.forEach((p, i) => { const q = X(p[0], p[1]); if (i) c.lineTo(...q); else c.moveTo(...q); });
      c.closePath(); if (fill) { c.fillStyle = fill; c.fill(); } c.setLineDash(dash || []); c.strokeStyle = stroke; c.lineWidth = 2; c.stroke(); c.setLineDash([]);
    };
    // 目标（夹具或凹位）
    const T = g.target, tt = T[2] * Math.PI / 180;
    const tgt = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([a, b]) => { const x = a * g.L / 2, y = b * g.W / 2; return [T[0] + Math.cos(tt) * x - Math.sin(tt) * y, T[1] + Math.sin(tt) * x + Math.cos(tt) * y]; });
    poly(tgt, null, api.css("--amber"), [7, 5]);
    api.label(fix ? api.T("夹具", "fixture") : api.T("凹位", "alcove"), ...X(T[0] + 0.15 * g.L, T[1] + 0.6 * g.L), api.css("--amber"), 13);
    if (!fix) { api.line(...X(0.4, 2.1), ...X(0.4, 0.6), api.css("--ink"), 3); api.line(...X(1.6, 2.1), ...X(1.6, 0.6), api.css("--ink"), 3); }
    poly(corners, null, api.css("--muted"), [3, 4]);
    const moved = corners.map((p) => this.ap(D, p[0], p[1], 1));
    poly(moved, "rgba(88,140,220,0.25)", api.css("--accent"));
    api.frame(...X(0, 0), 0, 0.35 * k, ["x", "y"], "{a}");
    const P = this.ap(D, g.c[0] + g.L / 2, g.c[1] + g.W / 2, 1);
    api.circle(...X(P[0], P[1]), 5, api.css("--amber"), api.css("--ink"));
    api.label("P′", X(P[0], P[1])[0] + 8, X(P[0], P[1])[1] - 10, api.css("--ink"), 13);
    const ctr = this.ap(D, g.c[0], g.c[1], 1), v = this.ap(D, 1, 0, 0), L = 0.35 * g.L;
    api.arrow(...X(ctr[0], ctr[1]), ...X(ctr[0] + L * v[0], ctr[1] + L * v[1]), api.css("--blue"), 3);
    api.label("v′", X(ctr[0] + L * v[0], ctr[1] + L * v[1])[0] + 6, X(ctr[0] + L * v[0], ctr[1] + L * v[1])[1] - 8, api.css("--blue"), 13);
  },
});
