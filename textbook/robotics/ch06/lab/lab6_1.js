// 实验 6.1 找出平面位移的极点（配 6.1 节）。零件从位姿 A 移到位姿 B；学生选一个候选中心和转角，
// 零件的“影子”绕这个中心转动；影子与 B 重合时，候选中心就是极点。中垂线作法同时画出，供对照。
WQ.lab({
  title: ["实验 6.1 找出平面位移的极点", "Lab 6.1 Finding the pole of a planar displacement"],
  goal: ["验证定理 6.1.1：转角不为零的平面位移，等价于绕唯一的一点（极点）转一次。",
         "Check Theorem 6.1.1: a planar displacement with non-zero turn is a single rotation about one point, the pole."],
  scenes: [
    { id: "scara", robot: true, name: ["SCARA 搬运零件", "SCARA moves a part"],
      params: { cx: { min: -0.1, max: 0.7, step: 0.001, value: 0.2 }, cy: { min: -0.1, max: 0.6, step: 0.001, value: 0.0 } },
      problem: { title: ["机器人问题：算例 6.1.1", "Robot problem: Example 6.1.1"],
                 text: ["零件参考点从 (0.30, 0.05) m 移到 (0.54, 0.13) m，并逆时针转 60°。哪一点转一次就能完成这次位移？",
                        "The part's reference point goes from (0.30, 0.05) m to (0.54, 0.13) m and turns 60° anticlockwise. About which point does one turn do it?"] } },
    { id: "desk", name: ["挪动书桌", "Moving a desk"],
      params: { cx: { min: 0, max: 3.2, step: 0.01, value: 0.5 }, cy: { min: 0, max: 2.4, step: 0.01, value: 0.5 } },
      problem: { title: ["生活中的例子：挪书桌", "Everyday example: moving a desk"],
                 text: ["书桌中心从 (1.0, 0.6) m 挪到 (2.2, 1.4) m，并转了 90°。只绕一个点转一次也能挪到。",
                        "The desk centre goes from (1.0, 0.6) m to (2.2, 1.4) m and turns 90°. A single turn about one point does the same."] } },
  ],
  params: [
    { id: "cx", name: ["候选中心 x", "Centre x"], min: -0.1, max: 0.7, step: 0.001, value: 0.2, unit: "m", digits: 3 },
    { id: "cy", name: ["候选中心 y", "Centre y"], min: -0.1, max: 0.6, step: 0.001, value: 0.0, unit: "m", digits: 3 },
    { id: "ang", name: ["转角 φ", "Turn φ"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "pole", robot: true, text: ["找出 SCARA 搬运的极点和转角，使影子与位姿 B 重合。", "Find the pole and turn that put the shadow on pose B."],
      demo: { scene: "scara", set: { cx: 0.351, cy: 0.298, ang: 60 }, press: [] } },
    { id: "half", robot: true, text: ["保持极点不变，只转 30°：零件停在以极点为圆心的圆弧中途。", "Keep the pole, turn only 30°: the part stops half-way along the arc about the pole."],
      demo: { scene: "scara", set: { cx: 0.351, cy: 0.298, ang: 30 }, press: [] } },
    { id: "desk", text: ["找出挪书桌的转动中心。", "Find the centre of the desk move."],
      demo: { scene: "desk", set: { cx: 1.2, cy: 1.6, ang: 90 }, press: [] } },
  ],
  think: ["如果书桌只平移、不转动，极点在哪里？中垂线会怎样？", "If the desk only slides without turning, where is the pole? What happens to the bisectors?"],

  data(api) {
    return api.scene === "desk"
      ? { A: [1.0, 0.6, 0], B: [2.2, 1.4, 90], shape: [[-0.6, -0.3], [0.6, -0.3], [0.6, 0.3], [-0.6, 0.3]], pts: [[0, 0], [0.6, 0.3]],
          box: [-0.1, 3.3, -0.1, 2.5], tol: 0.01 }
      : { A: [0.30, 0.05, 0], B: [0.54, 0.13, 60], shape: [[-0.03, -0.025], [0.18, -0.025], [0.18, 0.025], [-0.03, 0.025]], pts: [[0, 0], [0.15, 0]],
          box: [-0.12, 0.72, -0.12, 0.6], tol: 0.003 };
  },
  place(pose, xy) { const t = pose[2] * Math.PI / 180, c = Math.cos(t), s = Math.sin(t); return [pose[0] + c * xy[0] - s * xy[1], pose[1] + s * xy[0] + c * xy[1]]; },
  shadow(api, d) {     // A 绕 (cx, cy) 转 ang 之后的位姿
    const t = api.p.ang * Math.PI / 180, c = Math.cos(t), s = Math.sin(t), dx = d.A[0] - api.p.cx, dy = d.A[1] - api.p.cy;
    return [api.p.cx + c * dx - s * dy, api.p.cy + s * dx + c * dy, d.A[2] + api.p.ang];
  },
  pole(d) {            // 解 (I − R) c = p
    const t = (d.B[2] - d.A[2]) * Math.PI / 180, c = Math.cos(t), s = Math.sin(t);
    const p = [d.B[0] - (c * d.A[0] - s * d.A[1]), d.B[1] - (s * d.A[0] + c * d.A[1])];
    const a = 1 - c, b = s, det = a * a + b * b;               // I − R = [[a, b], [−b, a]]
    return [(a * p[0] - b * p[1]) / det, (b * p[0] + a * p[1]) / det];
  },
  reset(api, s) {},
  readouts(api, s) {
    const d = this.data(api), g = this.shadow(api, d);
    const err = Math.hypot(g[0] - d.B[0], g[1] - d.B[1]);
    const dang = (((g[2] - d.B[2]) % 360) + 540) % 360 - 180;
    const c = this.pole(d), off = Math.hypot(api.p.cx - c[0], api.p.cy - c[1]);
    const rA = Math.hypot(d.A[0] - api.p.cx, d.A[1] - api.p.cy), rB = Math.hypot(d.B[0] - api.p.cx, d.B[1] - api.p.cy);
    if (api.scene === "scara" && err < d.tol && Math.abs(dang) < 0.5) api.done("pole");
    if (api.scene === "scara" && off < 0.003 && api.p.ang === 30) api.done("half");
    if (api.scene === "desk" && err < d.tol && Math.abs(dang) < 0.5) api.done("desk");
    const u = api.scene === "desk" ? 2 : 3;
    return [[["影子与 B 的位置差", "shadow–B position gap"], api.fmt(err * 1000, 1) + " mm"],
            [["影子与 B 的角度差", "shadow–B angle gap"], api.fmt(dang, 1) + "°"],
            [["参考点到中心的距离：A / B", "reference point to centre: A / B"], `${api.fmt(rA, u)} / ${api.fmt(rB, u)} m`]];
  },
  draw(api, s) {
    const d = this.data(api), [x0, x1, y0, y1] = d.box, W = api.w, H = api.h;
    const k = Math.min(W / (x1 - x0), H / (y1 - y0)) * 0.95, ox = (W - k * (x1 - x0)) / 2, oy = (H - k * (y1 - y0)) / 2;
    const X = (x) => ox + (x - x0) * k, Y = (y) => H - oy - (y - y0) * k;
    const poly = (pose, fill, stroke, dash) => {
      const P = d.shape.map((q) => this.place(pose, q));
      const c = api.ctx; c.beginPath(); P.forEach((q, i) => (i ? c.lineTo(X(q[0]), Y(q[1])) : c.moveTo(X(q[0]), Y(q[1])))); c.closePath();
      if (fill) { c.fillStyle = fill; c.fill(); }
      c.setLineDash(dash || []); c.strokeStyle = stroke; c.lineWidth = 2; c.stroke(); c.setLineDash([]);
    };
    if (api.scene === "desk") { api.rect(X(0), Y(2.4), 3.2 * k, 2.4 * k, null, api.css("--ink")); api.label(api.T("房间（3.2 m × 2.4 m）", "room (3.2 m × 2.4 m)"), X(0.05), Y(2.3), api.css("--muted"), 12); }
    else { api.grid(api.w, api.h, k * 0.1); }
    api.arrow(X(Math.max(x0, -0.05)), Y(0), X(x1 - 0.02), Y(0), api.css("--red"), 1.5); api.arrow(X(0), Y(Math.max(y0, -0.05)), X(0), Y(y1 - 0.02), api.css("--green"), 1.5);
    api.label("x", X(x1 - 0.02) - 4, Y(0) + 12, api.css("--red"), 13); api.label("y", X(0) + 8, Y(y1 - 0.02) + 4, api.css("--green"), 13);
    // 两点的中垂线
    d.pts.forEach((q) => {
      const P = this.place(d.A, q), Q = this.place(d.B, q), m = [(P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2];
      const n = [-(Q[1] - P[1]), Q[0] - P[0]], L = Math.hypot(n[0], n[1]) || 1, e = (x1 - x0) * 1.5;
      api.line(X(P[0]), Y(P[1]), X(Q[0]), Y(Q[1]), api.css("--muted"), 1, [4, 4]);
      api.line(X(m[0] - e * n[0] / L), Y(m[1] - e * n[1] / L), X(m[0] + e * n[0] / L), Y(m[1] + e * n[1] / L), api.css("--blue"), 1, [2, 4]);
      api.circle(X(P[0]), Y(P[1]), 3, api.css("--ink")); api.circle(X(Q[0]), Y(Q[1]), 3, api.css("--ink"));
    });
    poly(d.A, "rgba(150,160,170,0.35)", api.css("--muted"));
    poly(d.B, "rgba(201,143,0,0.18)", api.css("--amber"), [6, 4]);
    const g = this.shadow(api, d);
    poly(g, "rgba(9,105,218,0.25)", api.css("--accent"));
    api.label("A", X(d.A[0]) - 4, Y(d.A[1]) + 18, api.css("--muted"), 14); api.label("B", X(d.B[0]) + 8, Y(d.B[1]) - 14, api.css("--amber"), 14);
    // 候选中心与圆弧
    const cx = X(api.p.cx), cy = Y(api.p.cy), r = Math.hypot(d.A[0] - api.p.cx, d.A[1] - api.p.cy) * k;
    const a0 = Math.atan2(d.A[1] - api.p.cy, d.A[0] - api.p.cx), a1 = a0 + api.p.ang * Math.PI / 180;
    api.ctx.beginPath(); api.ctx.strokeStyle = api.css("--accent"); api.ctx.lineWidth = 1.5;
    api.ctx.arc(cx, cy, r, -a0, -a1, a1 > a0); api.ctx.stroke();
    api.circle(cx, cy, 5, api.css("--red")); api.label(api.T("候选中心", "centre"), cx + 8, cy + 12, api.css("--red"), 12);
    if (api.scene === "scara") {        // SCARA 两段臂（0.35 m、0.30 m），手爪抓在影子的参考点上
      const L1 = 0.35, L2 = 0.30, px = g[0], py = g[1], r2 = px * px + py * py;
      const c2 = (r2 - L1 * L1 - L2 * L2) / (2 * L1 * L2);
      api.rect(X(0) - 12, Y(0) - 12, 24, 24, api.css("--panel"), api.css("--ink"), 4);
      if (Math.abs(c2) <= 1) {
        const t2 = Math.acos(c2), t1 = Math.atan2(py, px) - Math.atan2(L2 * Math.sin(t2), L1 + L2 * Math.cos(t2));
        const e = [L1 * Math.cos(t1), L1 * Math.sin(t1)];
        api.line(X(0), Y(0), X(e[0]), Y(e[1]), api.css("--ink"), 7); api.line(X(e[0]), Y(e[1]), X(px), Y(py), api.css("--ink"), 5);
        api.circle(X(e[0]), Y(e[1]), 5, api.css("--panel"), api.css("--ink"));
      }
      api.label("SCARA", X(0) + 14, Y(0) + 16, api.css("--muted"), 12);
    }
  },
});
