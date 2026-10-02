// 实验 6.5 伴随变换：同一个运动在两个坐标系中（配 6.5 节）。平面情形：物体坐标系 {b} 相对 {s} 的位姿为
// (p_x, p_y, φ)，物体运动旋量 V_b = (ω, v_bx, v_by)。由伴随变换（式 (6.5.4) 的平面形式）
//   ω_s = ω，v_s = R(φ) v_b + ω (p_y, −p_x)，
// 得到空间运动旋量。界面同时画出刚体上各点的速度（由 V_s 算出）和瞬心。
WQ.lab({
  title: ["实验 6.5 伴随变换：同一个运动，两种写法", "Lab 6.5 The adjoint: one motion, two descriptions"],
  goal: ["给定物体运动旋量 V_b 和 {b} 的位姿，用伴随矩阵求空间运动旋量 V_s，并从速度场上验证两者描述的是同一个运动。",
         "Given the body twist V_b and the pose of {b}, find the spatial twist V_s with the adjoint, and check on the velocity field that both describe the same motion."],
  scenes: [
    { id: "tool", robot: true, name: ["工具坐标系与基座坐标系", "Tool frame and base frame"],
      problem: { title: ["机器人问题：工具坐标系下的速度指令", "Robot problem: a velocity command in the tool frame"],
                 text: ["示教器让工具“绕自身原点转动”，这是物体运动旋量；控制器要把它换成基座坐标系中的运动旋量。",
                        "The pendant asks the tool to turn about its own origin — a body twist; the controller must turn it into a spatial twist."] } },
    { id: "ride", name: ["转盘上的人", "On a merry-go-round"],
      problem: { title: ["生活中的例子：坐转盘", "Everyday example: riding a merry-go-round"],
                 text: ["转盘绕中心（{s} 原点）以 1 rad/s 转动。站在转盘上的人觉得自己怎样运动？这就是他的物体运动旋量。",
                        "The platform turns about its centre (the origin of {s}) at 1 rad/s. How does a rider feel she is moving? That is her body twist."] } },
  ],
  params: [
    { id: "px", name: ["{b} 的位置 p_x", "{b} position p_x"], min: -1.2, max: 1.2, step: 0.05, value: 0.6, unit: "m", digits: 2 },
    { id: "py", name: ["{b} 的位置 p_y", "{b} position p_y"], min: -1.2, max: 1.2, step: 0.05, value: 0.2, unit: "m", digits: 2 },
    { id: "phi", name: ["{b} 的朝向 φ", "{b} heading φ"], min: -180, max: 180, step: 15, value: 0, unit: "°", digits: 0 },
    { id: "w", name: ["角速度 ω", "angular velocity ω"], min: -1.5, max: 1.5, step: 0.1, value: 0.5, unit: "rad/s", digits: 1 },
    { id: "vbx", name: ["物体线速度 v_bx", "body velocity v_bx"], min: -1.5, max: 1.5, step: 0.05, value: 0, unit: "m/s", digits: 2 },
    { id: "vby", name: ["物体线速度 v_by", "body velocity v_by"], min: -1.5, max: 1.5, step: 0.05, value: 0, unit: "m/s", digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "own", robot: true, text: ["{b} 在 (0.6, 0.2) m、朝向 90°，工具绕自身原点以 0.5 rad/s 转动：读出 V_s。", "{b} at (0.6, 0.2) m, heading 90°, the tool turns about its own origin at 0.5 rad/s: read V_s."],
      demo: { scene: "tool", set: { px: 0.6, py: 0.2, phi: 90, w: 0.5, vbx: 0, vby: 0 }, press: [] } },
    { id: "base", robot: true, text: ["同一个 {b}，找出使工具绕基座原点转动（V_s 的线速度为零）的 V_b。", "Same {b}: find the V_b that turns the tool about the base origin (zero linear part in V_s)."],
      demo: { scene: "tool", set: { px: 0.6, py: 0.2, phi: 90, w: 0.5, vbx: 0.3, vby: 0.1 }, press: [] } },
    { id: "ride", text: ["人站在 (1.0, 0) m 处、面朝 +y，转盘以 1 rad/s 转动：求人的物体运动旋量。", "The rider stands at (1.0, 0) m facing +y; the platform turns at 1 rad/s: find her body twist."],
      demo: { scene: "ride", set: { px: 1, py: 0, phi: 90, w: 1, vbx: 1, vby: 0 }, press: [] } },
  ],
  think: ["转盘上的人觉得自己“一边向前走、一边转身”。为什么她的物体运动旋量有线速度，而转盘的空间运动旋量没有？", "The rider feels she is walking forward while turning. Why does her body twist have a linear part when the platform's spatial twist has none?"],

  vs(api) {
    const t = api.p.phi * Math.PI / 180, c = Math.cos(t), s = Math.sin(t), w = api.p.w;
    const Rv = [c * api.p.vbx - s * api.p.vby, s * api.p.vbx + c * api.p.vby];
    return [w, Rv[0] + w * api.p.py, Rv[1] - w * api.p.px];          // (ω_s, v_sx, v_sy)
  },
  reset(api, s) {},
  readouts(api, s) {
    const V = this.vs(api), near = (a, b) => Math.abs(a - b) < 1e-9;
    const atB = near(api.p.px, 0.6) && near(api.p.py, 0.2) && api.p.phi === 90;
    if (api.scene === "tool" && atB && near(api.p.w, 0.5) && near(api.p.vbx, 0) && near(api.p.vby, 0)) api.done("own");
    if (api.scene === "tool" && atB && near(api.p.w, 0.5) && Math.hypot(V[1], V[2]) < 1e-9) api.done("base");
    if (api.scene === "ride" && near(api.p.px, 1) && near(api.p.py, 0) && api.p.phi === 90 && near(api.p.w, 1) && Math.hypot(V[1], V[2]) < 1e-9) api.done("ride");
    const f = (x) => api.fmt(x, 3);
    const t = api.p.phi * Math.PI / 180, vB = [Math.cos(t) * api.p.vbx - Math.sin(t) * api.p.vby, Math.sin(t) * api.p.vbx + Math.cos(t) * api.p.vby];
    return [[["物体运动旋量 V_b = (ω, v_bx, v_by)", "body twist V_b = (ω, v_bx, v_by)"], `(${f(api.p.w)}, ${f(api.p.vbx)}, ${f(api.p.vby)})`],
            [["空间运动旋量 V_s = [Ad] V_b", "spatial twist V_s = [Ad] V_b"], `(${f(V[0])}, ${f(V[1])}, ${f(V[2])})`],
            [["{b} 原点的速度（{s} 中）", "velocity of {b}'s origin (in {s})"], `(${f(vB[0])}, ${f(vB[1])}) m/s`],
            [["{s} 原点处那一点的速度", "velocity of the point at {s}'s origin"], `(${f(V[1])}, ${f(V[2])}) m/s`]];
  },
  draw(api, s) {
    const W = api.w, H = api.h, k = Math.min(W / 2.6, H / 1.9), ox = W * 0.42, oy = H * 0.58;
    const X = (x) => ox + x * k, Y = (y) => oy - y * k, ctx = api.ctx;
    api.grid(W, H, k * 0.25);
    const V = this.vs(api), w = V[0];
    if (api.scene === "ride") {
      ctx.beginPath(); ctx.arc(X(0), Y(0), 1.3 * k, 0, 2 * Math.PI); ctx.fillStyle = "rgba(201,143,0,0.10)"; ctx.fill(); ctx.strokeStyle = api.css("--amber"); ctx.lineWidth = 2; ctx.stroke();
      for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; api.line(X(0), Y(0), X(1.3 * Math.cos(a)), Y(1.3 * Math.sin(a)), api.css("--amber"), 1); }
    }
    api.frame(X(0), Y(0), 0, 0.35 * k, ["x_s", "y_s"], "{s}");
    const t = api.p.phi * Math.PI / 180, c = Math.cos(t), sn = Math.sin(t), px = api.p.px, py = api.p.py;
    const toS = (b) => [px + c * b[0] - sn * b[1], py + sn * b[0] + c * b[1]];
    if (api.scene === "tool") {          // 平面机械臂的末端：手爪
      const shape = [[-0.25, -0.06], [0, -0.06], [0, -0.12], [0.15, -0.12], [0.15, -0.08], [0.04, -0.08], [0.04, 0.08], [0.15, 0.08], [0.15, 0.12], [0, 0.12], [0, 0.06], [-0.25, 0.06]].map(toS);
      ctx.beginPath(); shape.forEach((q, i) => (i ? ctx.lineTo(X(q[0]), Y(q[1])) : ctx.moveTo(X(q[0]), Y(q[1])))); ctx.closePath();
      ctx.fillStyle = "rgba(9,105,218,0.15)"; ctx.fill(); ctx.strokeStyle = api.css("--accent"); ctx.lineWidth = 2; ctx.stroke();
    } else {                             // 人：俯视的一个圆加一个朝向标记
      const q = toS([0, 0]); api.circle(X(q[0]), Y(q[1]), 0.12 * k, "rgba(9,105,218,0.2)", api.css("--accent"));
      const n = toS([0.18, 0]); api.line(X(q[0]), Y(q[1]), X(n[0]), Y(n[1]), api.css("--accent"), 3);
    }
    api.frame(X(px), Y(py), api.p.phi, 0.3 * k, ["x_b", "y_b"], "{b}", api.css("--accent"));
    // 速度场（由 V_s 算出）：在 {b} 附近取几点
    const pts = [[0, 0], [0.3, 0], [-0.3, 0], [0, 0.3], [0, -0.3]].map(toS).concat([[0, 0]]);
    pts.forEach((q, i) => {
      const v = [V[1] - w * q[1], V[2] + w * q[0]];
      api.circle(X(q[0]), Y(q[1]), 3, api.css("--ink"));
      api.arrow(X(q[0]), Y(q[1]), X(q[0] + 0.6 * v[0]), Y(q[1] + 0.6 * v[1]), i === pts.length - 1 ? api.css("--violet") : api.css("--orange"), 2.2);
    });
    if (Math.abs(w) > 1e-9) {
      const ic = [-V[2] / w, V[1] / w];
      api.circle(X(ic[0]), Y(ic[1]), 6, null, api.css("--red")); api.label(api.T("瞬心", "centre"), X(ic[0]) + 9, Y(ic[1]) - 9, api.css("--red"), 12);
    }
    api.label(api.T("紫色：{s} 原点处那一点的速度 v_s；橙色：其他点的速度", "violet: v_s, velocity of the point at {s}'s origin; orange: other points"), 12, 18, api.css("--muted"), 12);
  },
});
