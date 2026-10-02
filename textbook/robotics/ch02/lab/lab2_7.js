// 实验 2.7 三点法示教与正交化（配 2.7 节）。俯视图：p0 = (0, 0)，p1 = (300, ε₁)，p2 = (ε₂, 300)，单位 mm。
WQ.lab({
  title: ["实验 2.7 格拉姆-施密特正交化", "Lab 2.7 Gram–Schmidt orthonormalisation"],
  goal: ["改变示教误差和处理次序，看格拉姆-施密特法怎样把两个不垂直的方向整理成一对垂直的坐标轴，以及误差由哪根轴承担。",
         "Change the teaching errors and the order of processing; see how Gram–Schmidt turns two non-perpendicular directions into perpendicular axes, and which axis absorbs the error."],
  scenes: [
    { id: "teach", robot: true, name: ["三点法示教", "Three-point teaching"], hide: ["err"],
      problem: { title: ["机器人问题：示教三个点，建一个工件坐标系", "Robot problem: teach three points, build a work frame"],
                 text: ["p₀ 为原点，p₁ 定 x 方向，p₂ 定 xy 平面。示教误差使 p₀→p₁ 与 p₀→p₂ 不垂直。",
                        "p₀ is the origin, p₁ fixes the x direction, p₂ the xy plane. Teaching errors make p₀→p₁ and p₀→p₂ non-perpendicular."] } },
    { id: "wood", name: ["木工画直角", "A carpenter's right angle"], hide: ["e1", "e2", "order"],
      problem: { title: ["生活中的例子：靠着板边画垂线", "Everyday example: a line square to the board's edge"],
                 text: ["凭眼睛画的线与板边不垂直。用直角尺靠住板边重画：板边保留，线被修正。",
                        "A line drawn by eye is not square to the edge. Redraw it against a try square: the edge is kept, the line corrected."] } },
  ],
  params: [
    { id: "e1", name: ["p₁ 的横向误差", "Sideways error of p₁"], min: -30, max: 30, step: 1, value: 5, unit: "mm", digits: 0 },
    { id: "e2", name: ["p₂ 的横向误差", "Sideways error of p₂"], min: -30, max: 30, step: 1, value: 5, unit: "mm", digits: 0 },
    { id: "order", name: ["次序：0 先 x 后 y / 1 先 y 后 x", "Order: 0 x first / 1 y first"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "err", name: ["画线的角度误差", "Angle error of the drawn line"], min: -10, max: 10, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "square", name: ["用直角尺修正", "Correct with a try square"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "orth", robot: true, text: ["让两个示教方向的夹角偏离 90° 超过 3°，确认正交化后两轴严格垂直。", "Make the taught directions deviate from 90° by more than 3°; check that the result is exactly perpendicular."],
      demo: { scene: "teach", set: { e1: 10, e2: 10, order: 0 }, press: [] } },
    { id: "order", robot: true, text: ["改为先处理 y 方向，比较 x 轴的变化。", "Process the y direction first and compare the x axis."],
      demo: { scene: "teach", set: { e1: 10, e2: 10, order: 1 }, press: [] } },
    { id: "wood", text: ["把偏了 6° 的线修正为直角。", "Correct a line that is 6° off square."],
      demo: { scene: "wood", set: { err: 6 }, press: ["square"] } },
  ],
  think: ["示教时，为什么应把精度要求最高的那条边作为 p₀→p₁？", "When teaching, why should p₀→p₁ run along the edge that matters most?"],

  gs(a, b) {   // 二维格拉姆-施密特：返回 [q1, q2]
    const n1 = Math.hypot(...a), q1 = [a[0] / n1, a[1] / n1], d = q1[0] * b[0] + q1[1] * b[1];
    const w = [b[0] - d * q1[0], b[1] - d * q1[1]], n2 = Math.hypot(...w);
    return [q1, [w[0] / n2, w[1] / n2]];
  },
  frame(api) {
    const a1 = [300, api.p.e1], a2 = [api.p.e2, 300];
    let x, y;
    if (api.p.order < 0.5) [x, y] = this.gs(a1, a2); else [y, x] = this.gs(a2, a1);
    return { a1, a2, x, y };
  },
  ang(u, v) { return Math.acos(Math.max(-1, Math.min(1, (u[0] * v[0] + u[1] * v[1]) / (Math.hypot(...u) * Math.hypot(...v))))) * 180 / Math.PI; },
  reset(api, s) { s.fixed = false; },
  action(id, api, s) { if (id === "square" && api.scene === "wood") s.fixed = true; },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "wood") {
      if (s.fixed && Math.abs(api.p.err) >= 6) api.done("wood");
      return [[["画线与板边的夹角", "angle between line and edge"], f(90 + api.p.err, 0) + "°"],
              [["修正后", "after correction"], s.fixed ? "90°" : api.T("尚未修正", "not yet corrected")]];
    }
    const F = this.frame(api), taught = this.ang(F.a1, F.a2), dot = F.x[0] * F.y[0] + F.x[1] * F.y[1];
    const dx = this.ang(F.x, F.a1), dy = this.ang(F.y, F.a2), det = F.x[0] * F.y[1] - F.x[1] * F.y[0];
    if (Math.abs(taught - 90) > 3 && Math.abs(dot) < 1e-12) api.done("orth");
    if (api.p.order > 0.5 && Math.abs(taught - 90) > 0.5 && dx > 0.5) api.done("order");
    return [[["示教方向的夹角", "angle between taught directions"], f(taught, 2) + "°"],
            [["x 轴偏离 p₀→p₁", "x axis off p₀→p₁"], f(dx, 2) + "°"], [["y 轴偏离 p₀→p₂", "y axis off p₀→p₂"], f(dy, 2) + "°"],
            [["x · y（应为 0）", "x · y (should be 0)"], dot.toExponential(1)], [["det（应为 +1）", "det (should be +1)"], f(det, 6)]];
  },
  draw(api, s) {
    const { w, h } = api;
    api.grid(w, h, 40);
    if (api.scene === "wood") {
      const ox = w * 0.25, oy = h * 0.8, L = Math.min(w, h) * 0.6;
      api.rect(ox - 30, oy - L - 20, L + 120, L + 50, "#d8b98a", "#8a6a3a", 4);
      api.line(ox, oy, ox + L + 60, oy, "#5b3d16", 4);
      api.label(api.T("板边（保留）", "edge (kept)"), ox + L, oy + 18, api.css("--ink"), 13);
      const t = (90 + api.p.err) * Math.PI / 180;
      api.line(ox, oy, ox + L * Math.cos(t), oy - L * Math.sin(t), s.fixed ? api.css("--muted") : api.css("--red"), 2, s.fixed ? [6, 5] : null);
      if (s.fixed) {
        api.line(ox, oy, ox, oy - L, api.css("--green"), 3);
        api.rect(ox, oy - 120, 24, 120, "rgba(120,130,140,0.5)"); api.rect(ox, oy - 24, 150, 24, "rgba(120,130,140,0.5)");
        api.label(api.T("直角尺", "try square"), ox + 30, oy - 40, api.css("--ink"), 13);
      }
      api.label(api.T("凭眼睛画的线", "line drawn by eye"), ox + L * Math.cos(t) + 8, oy - L * Math.sin(t), api.css("--red"), 13);
      return;
    }
    const F = this.frame(api), k = Math.min(w, h) * 0.0022, ox = w * 0.25, oy = h * 0.8, X = (p) => [ox + k * p[0], oy - k * p[1]];
    const amp = 5;   // 示教误差放大 5 倍画出，便于看清
    const A1 = [300, api.p.e1 * amp], A2 = [api.p.e2 * amp, 300];
    api.line(...X([0, 0]), ...X(A1), api.css("--muted"), 1.5, [6, 5]); api.line(...X([0, 0]), ...X(A2), api.css("--muted"), 1.5, [6, 5]);
    api.circle(...X([0, 0]), 6, api.css("--ink")); api.circle(...X(A1), 6, api.css("--ink")); api.circle(...X(A2), 6, api.css("--ink"));
    api.label("p₀", ...X([-30, -25]), api.css("--ink"), 14); api.label("p₁", ...X([310, A1[1] - 20]), api.css("--ink"), 14); api.label("p₂", ...X([A2[0] + 12, 315]), api.css("--ink"), 14);
    const G = api.p.order < 0.5 ? this.gs(A1, A2) : this.gs(A2, A1).reverse();
    api.arrow(...X([0, 0]), ...X([G[0][0] * 230, G[0][1] * 230]), api.css("--red"), 4);
    api.arrow(...X([0, 0]), ...X([G[1][0] * 230, G[1][1] * 230]), api.css("--green"), 4);
    api.label("x_u", ...X([G[0][0] * 245, G[0][1] * 245 + 12]), api.css("--red"), 14); api.label("y_u", ...X([G[1][0] * 245 - 30, G[1][1] * 245]), api.css("--green"), 14);
    api.label(api.T("虚线：示教方向（误差放大 5 倍画出）；彩色：正交化后的轴", "dashed: taught directions (errors drawn 5× larger); colour: axes after orthonormalisation"), 12, 18, api.css("--muted"), 12);
  },
});
