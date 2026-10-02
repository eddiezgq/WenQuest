// 实验 7.1 一元微积分演示台：割线变成切线，曲线放大后变直（配 7.1、7.2 节）。
// “机器人”场景：UR5e 肩关节在 T = 2 s 内由 0 转到 90°（五次多项式，式 (7.1.9)），切线斜率就是角速度。
WQ.lab({
  title: ["实验 7.1 一元微积分演示台：割线、切线与局部线性", "Lab 7.1 One-variable bench: secants, tangents and local linearity"],
  goal: ["拖动步长 h，看割线怎样转向切线、差商怎样逼近导数；把曲线放大，看光滑曲线变直而尖角不变；在机器人场景中读出关节的角速度。",
         "Drag the step h and watch the secant turn into the tangent and the quotient approach the derivative; zoom in and see a smooth curve straighten while a corner stays a corner; read a joint's angular velocity in the robot scene."],
  scenes: [
    { id: "secant", name: ["割线与切线", "Secant and tangent"], hide: ["f", "lz", "t0"],
      problem: { title: ["生活中的例子：区间测速与定点测速", "Everyday example: average-speed cameras and radar"],
                 text: ["区间测速测的是一段路上的平均速度，相当于割线的斜率；雷达测的是瞬时速度，相当于切线的斜率。把区间缩短，两者有什么关系？",
                        "An average-speed camera measures the slope of a secant; a radar gun measures the slope of the tangent. What happens as the section gets shorter?"] } },
    { id: "zoom", name: ["放大镜：局部线性", "Magnifier: local linearity"], hide: ["lh", "sg", "t0"],
      problem: { title: ["可导就是“放大后变直”", "Differentiable means 'straight when magnified'"],
                 text: ["选一个函数和一点，不断放大。光滑的曲线放大后与切线几乎重合；|x| 在原点的尖角、∛x 在原点的竖直切线又会怎样？",
                        "Pick a function and a point and keep zooming. A smooth curve merges with its tangent; what happens to the corner of |x| or the vertical tangent of ∛x at 0?"] } },
    { id: "robot", robot: true, name: ["UR5e 肩关节的角度曲线", "UR5e shoulder angle curve"], hide: ["x0", "f", "lz"],
      problem: { title: ["机器人问题：第 0.5 秒关节转得多快？", "Robot problem: how fast is the joint turning at t = 0.5 s?"],
                 text: ["关节角度曲线上割线的斜率是一段时间内的平均角速度，切线的斜率是瞬时角速度。把 h 缩小，读出 t = 0.5 s 时的角速度。",
                        "On the joint-angle curve the secant slope is an average angular velocity, the tangent slope the instantaneous one. Shrink h and read the angular velocity at t = 0.5 s."] } },
  ],
  params: [
    { id: "x0", name: ["切点 x₀", "Point x₀"], min: -3, max: 3, step: 0.01, value: 1, digits: 2 },
    { id: "lh", name: ["步长 lg|h|", "Step lg|h|"], min: -4, max: 0, step: 0.05, value: 0, digits: 2 },
    { id: "sg", name: ["h 的符号（−1 左侧，+1 右侧）", "Sign of h (−1 left, +1 right)"], min: -1, max: 1, step: 2, value: 1, digits: 0 },
    { id: "f", name: ["函数：0 光滑曲线，1 |x|，2 ∛x", "Function: 0 smooth, 1 |x|, 2 ∛x"], min: 0, max: 2, step: 1, value: 0, digits: 0 },
    { id: "lz", name: ["放大倍数 lg k", "Zoom lg k"], min: 0, max: 4, step: 0.05, value: 0, digits: 2 },
    { id: "t0", name: ["时刻 t₀", "Time t₀"], min: 0.05, max: 1.95, step: 0.01, value: 1.2, unit: "s", digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "close", text: ["在“割线与切线”场景中，让割线斜率与切线斜率相差不到 1%。h 大约要取多小？", "In 'Secant and tangent', make the secant slope within 1% of the tangent slope. How small must h be?"],
      demo: { scene: "secant", set: { x0: 1, lh: -2.5 }, press: [] } },
    { id: "straight", text: ["选光滑曲线，放大到 1000 倍以上，确认曲线与切线的偏离不到 1 像素。", "Choose the smooth curve and zoom beyond 1000×: the curve stays within 1 pixel of the tangent."],
      demo: { scene: "zoom", set: { f: 0, x0: 1, lz: 3.2 }, press: [] } },
    { id: "corner", text: ["选 |x|，在 x₀ = 0 处放大 100 倍以上。尖角变直了吗？读出左、右两侧的斜率。", "Choose |x| and zoom beyond 100× at x₀ = 0. Did the corner straighten? Read the slopes on both sides."],
      demo: { scene: "zoom", set: { f: 1, x0: 0, lz: 2.5 }, press: [] } },
    { id: "robot", robot: true, text: ["在机器人场景中把 t₀ 调到 0.5 s、h 缩小到 0.01 s 以下，读出肩关节的角速度。", "In the robot scene set t₀ = 0.5 s and h below 0.01 s; read the shoulder's angular velocity."],
      demo: { scene: "robot", set: { t0: 0.5, lh: -2.5 }, press: [] } },
  ],
  think: ["为什么割线斜率在 h > 0 和 h < 0 时从两侧逼近同一个数？对 |x| 在 0 点这还成立吗？", "Why do the secant slopes for h > 0 and h < 0 approach the same number from both sides? Is that still true for |x| at 0?"],

  // the functions of the bench and their derivatives
  fn(api) {
    const D = Math.PI / 2, T = 2;
    if (api.scene === "robot") {   // θ in degrees, t in s
      const th = (t) => { const s = Math.min(1, Math.max(0, t / T)); return 90 * (10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5); };
      const dth = (t) => { const s = Math.min(1, Math.max(0, t / T)); return 90 / T * 30 * s * s * (1 - s) * (1 - s); };
      return { f: th, d: dth, xmin: -0.1, xmax: 2.1, x0: api.p.t0, name: "θ(t)" };
    }
    const k = api.scene === "zoom" ? api.p.f : 0;
    if (k === 1) return { f: Math.abs, d: (x) => (x > 0 ? 1 : x < 0 ? -1 : NaN), x0: api.p.x0, name: "|x|" };
    if (k === 2) return { f: Math.cbrt, d: (x) => (x === 0 ? Infinity : 1 / (3 * Math.cbrt(x) ** 2)), x0: api.p.x0, name: "∛x" };
    return { f: (x) => Math.sin(x) + 0.2 * x * x, d: (x) => Math.cos(x) + 0.4 * x, x0: api.p.x0, name: "sin x + 0.2x²" };
  },
  h(api) { return api.p.sg * Math.pow(10, api.p.lh); },
  readouts(api, s) {
    const F = this.fn(api), x0 = F.x0, y0 = F.f(x0), m = F.d(x0);
    if (api.scene === "zoom") {
      const k = Math.pow(10, api.p.lz), half = 2 / k;
      const dev = isFinite(m) ? this.deviation(api, F, half) : NaN;
      if (api.p.f === 0 && k >= 999 && dev < 1) api.done("straight");
      if (api.p.f === 1 && Math.abs(x0) < 0.005 && k >= 99) api.done("corner");
      const left = (F.f(x0) - F.f(x0 - half * 0.5)) / (half * 0.5), right = (F.f(x0 + half * 0.5) - F.f(x0)) / (half * 0.5);
      return [[["函数", "Function"], F.name], [["放大倍数", "Zoom"], api.fmt(k, 0) + "×"],
              [["切线斜率 f′(x₀)", "Tangent slope f′(x₀)"], isFinite(m) ? api.fmt(m, 5) : api.T("不存在", "none")],
              [["左侧、右侧割线斜率", "Left / right secant slopes"], api.fmt(left, 4) + " / " + api.fmt(right, 4)],
              [["曲线偏离切线（像素）", "Curve off the tangent (px)"], isFinite(dev) ? api.fmt(dev, 2) : "—"]];
    }
    const h = this.h(api), q = (F.f(x0 + h) - y0) / h, err = Math.abs(q - m) / Math.max(1e-9, Math.abs(m));
    if (api.scene === "secant" && err < 0.01) api.done("close");
    if (api.scene === "robot" && Math.abs(x0 - 0.5) < 0.006 && Math.abs(h) <= 0.0101) api.done("robot");
    const unit = api.scene === "robot" ? " °/s" : "";
    const rows = [[["步长 h", "Step h"], api.fmt(h, 5) + (api.scene === "robot" ? " s" : "")],
                  [["割线斜率（差商）", "Secant slope (quotient)"], api.fmt(q, 5) + unit],
                  [["切线斜率（导数）", "Tangent slope (derivative)"], api.fmt(m, 5) + unit],
                  [["相对误差", "Relative error"], (100 * err).toFixed(3) + " %"]];
    if (api.scene === "robot") rows.push([["角速度（rad/s）", "Angular velocity (rad/s)"], api.fmt(m * Math.PI / 180, 5)]);
    return rows;
  },
  deviation(api, F, half) {   // largest distance (in pixels) between the curve and the tangent inside the zoom window
    const x0 = F.x0, y0 = F.f(x0), m = F.d(x0), px = Math.min(api.w - 74, api.h - 62) / (2 * half);
    let worst = 0;
    for (let i = -50; i <= 50; i++) { const x = x0 + half * i / 50; worst = Math.max(worst, Math.abs(F.f(x) - y0 - m * (x - x0))); }
    return worst * px;
  },
  draw(api, s) {
    const F = this.fn(api), x0 = F.x0, y0 = F.f(x0), m = F.d(x0);
    const red = api.css("--red"), blue = api.css("--blue"), ink = api.css("--ink"), acc = api.css("--accent");
    const pad = { l: 56, r: 18, t: 22, b: 40 };
    if (api.scene === "zoom") {
      const k = Math.pow(10, api.p.lz), half = 2 / k;
      const side = Math.min(api.w - pad.l - pad.r, api.h - pad.t - pad.b);
      const G = api.graph({ x: pad.l + (api.w - pad.l - pad.r - side) / 2, y: pad.t, w: side, h: side,
        xmin: x0 - half, xmax: x0 + half, ymin: y0 - half, ymax: y0 + half });
      G.axes();
      if (isFinite(m)) G.line(x0, y0, m, red, 1.5, [6, 4]);
      G.fn(F.f, ink, 2.5);
      G.point(x0, y0, acc);
      api.label(api.T("窗口宽 ", "window ") + api.fmt(2 * half, 6), api.w - 10, 16, api.css("--muted"), 12, "right");
      return;
    }
    const xmin = F.xmin ?? -3.5, xmax = F.xmax ?? 3.5;
    let ylo = Infinity, yhi = -Infinity;
    for (let i = 0; i <= 200; i++) { const v = F.f(xmin + (xmax - xmin) * i / 200); ylo = Math.min(ylo, v); yhi = Math.max(yhi, v); }
    const span = yhi - ylo || 1;
    const G = api.graph({ x: pad.l, y: pad.t, w: api.w - pad.l - pad.r, h: api.h - pad.t - pad.b, xmin, xmax,
      ymin: ylo - 0.1 * span, ymax: yhi + 0.1 * span,
      xlabel: api.scene === "robot" ? api.T("t / s", "t / s") : "x", ylabel: api.scene === "robot" ? api.T("θ / (°)", "θ / (°)") : "y" });
    G.axes();
    G.fn(F.f, ink, 2.5);
    const h = this.h(api), q = (F.f(x0 + h) - y0) / h;
    G.line(x0, y0, m, red, 2);
    G.line(x0, y0, q, blue, 1.5, [6, 4]);
    G.point(x0 + h, F.f(x0 + h), blue, "Q");
    G.point(x0, y0, acc, "P");
    api.label(api.T("红：切线　蓝：割线 PQ", "red: tangent   blue: secant PQ"), api.w - 10, 16, api.css("--muted"), 12, "right");
  },
});
