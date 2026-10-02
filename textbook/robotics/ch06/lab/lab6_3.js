// 实验 6.3 平面运动旋量与瞬心（配 6.3 节）。平面刚体的运动旋量 V = (ω, v_x, v_y)：ω 为绕 z 轴的角速度，
// (v_x, v_y) 为此刻位于原点的那一点的速度。刚体上各点速度 v + ω ẑ × x；ω ≠ 0 时有一个速度为零的点（瞬心）
// q = (−v_y/ω, v_x/ω)，它是三维瞬时螺旋轴（节距为零）与平面的交点（式 (6.3.12)）。
WQ.lab({
  title: ["实验 6.3 平面运动旋量与瞬心", "Lab 6.3 Planar twists and the instantaneous centre"],
  goal: ["调节运动旋量的三个分量，看刚体上各点的速度怎样分布，找出速度为零的瞬心。",
         "Adjust the three components of a planar twist; see how velocities spread over the body and find the instantaneous centre where the velocity is zero."],
  scenes: [
    { id: "agv", robot: true, name: ["差速 AGV 转弯", "Differential AGV turning"],
      problem: { title: ["机器人问题：AGV 绕哪一点转弯", "Robot problem: about which point does the AGV turn?"],
                 text: ["AGV 坐标系此刻与 {s} 重合，原点在两轮轴线的中点。给定 AGV 的运动旋量，车上哪一点此刻不动？",
                        "The AGV frame coincides with {s} at this instant, its origin midway between the wheels. Given the AGV's twist, which point of it is momentarily still?"] } },
    { id: "wheel", name: ["滚动的车轮", "A rolling wheel"],
      problem: { title: ["生活中的例子：纯滚动的车轮", "Everyday example: a wheel rolling without slipping"],
                 text: ["半径 0.3 m 的车轮，原点在轮心。纯滚动时，轮子与地面的接触点速度为零。",
                        "A wheel of radius 0.3 m with the origin at its hub. Rolling without slipping, the contact point has zero velocity."] } },
  ],
  params: [
    { id: "w", name: ["角速度 ω", "Angular velocity ω"], min: -2, max: 2, step: 0.1, value: 0.5, unit: "rad/s", digits: 1 },
    { id: "vx", name: ["原点速度 v_x", "Velocity at origin v_x"], min: -1, max: 1, step: 0.05, value: 0.2, unit: "m/s", digits: 2 },
    { id: "vy", name: ["原点速度 v_y", "Velocity at origin v_y"], min: -1, max: 1, step: 0.05, value: 0, unit: "m/s", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["运动 3 s", "Move for 3 s"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "icr", robot: true, text: ["让 AGV 绕左侧 1.0 m 处的点 (0, 1.0) m 转弯。", "Make the AGV turn about the point (0, 1.0) m, 1.0 m to its left."],
      demo: { scene: "agv", set: { w: 0.5, vx: 0.5, vy: 0 }, press: [] } },
    { id: "spin", robot: true, text: ["让 AGV 原地转向：瞬心在原点。", "Make the AGV spin on the spot: the centre is at the origin."],
      demo: { scene: "agv", set: { w: 1, vx: 0, vy: 0 }, press: [] } },
    { id: "trans", robot: true, text: ["让 AGV 直线前进：ω = 0，瞬心跑到无穷远。", "Drive straight: ω = 0 and the centre goes to infinity."],
      demo: { scene: "agv", set: { w: 0, vx: 0.5, vy: 0 }, press: [] } },
    { id: "roll", text: ["车轮以 0.6 m/s 向右纯滚动：接触点速度为零。", "Roll the wheel to the right at 0.6 m/s without slipping: the contact point is still."],
      demo: { scene: "wheel", set: { w: -2, vx: 0.6, vy: 0 }, press: [] } },
  ],
  think: ["差速 AGV 的两个轮子不能侧滑，所以 v_y 只能为零。这对瞬心的位置有什么限制？", "A differential AGV's wheels cannot slide sideways, so v_y must be zero. What does that imply for where its centre can be?"],

  reset(api, s) { s.th = 0; s.p = [0, 0]; s.trail = []; },
  update(dt, api, s) {         // 运动旋量在物体坐标系中恒定：位姿按指数映射更新（平面情形）
    const w = api.p.w, v = [api.p.vx, api.p.vy];
    const c = Math.cos(s.th), sn = Math.sin(s.th), vs = [c * v[0] - sn * v[1], sn * v[0] + c * v[1]];
    let dx, dy;
    if (Math.abs(w) < 1e-9) { dx = vs[0] * dt; dy = vs[1] * dt; }
    else { const a = w * dt, A = Math.sin(a) / w, B = (1 - Math.cos(a)) / w; dx = A * vs[0] - B * vs[1]; dy = B * vs[0] + A * vs[1]; }
    s.p = [s.p[0] + dx, s.p[1] + dy]; s.th += w * dt; s.trail.push(s.p.slice());
    if (api.t >= 3) api.stop();
  },
  readouts(api, s) {
    const w = api.p.w, vx = api.p.vx, vy = api.p.vy;
    const icr = Math.abs(w) > 1e-9 ? [-vy / w, vx / w] : null;
    const vc = [vx - w * (-0.3), vy];          // 车轮接触点 (0, −0.3) 的速度：v + ω ẑ × x
    if (api.scene === "agv" && icr && Math.hypot(icr[0], icr[1] - 1) < 1e-6) api.done("icr");
    if (api.scene === "agv" && icr && Math.hypot(icr[0], icr[1]) < 1e-9 && Math.abs(w) > 0) api.done("spin");
    if (api.scene === "agv" && Math.abs(w) < 1e-9 && Math.hypot(vx, vy) > 0.01) api.done("trans");
    if (api.scene === "wheel" && Math.abs(vx - 0.6) < 1e-6 && Math.hypot(vc[0], vc[1]) < 1e-6) api.done("roll");
    const rows = [[["瞬心 q", "centre q"], icr ? `(${api.fmt(icr[0], 3)}, ${api.fmt(icr[1], 3)}) m` : api.T("无穷远（纯平移）", "at infinity (pure translation)")]];
    rows.push([["瞬心到原点的距离", "centre to origin"], icr ? api.fmt(Math.hypot(icr[0], icr[1]), 3) + " m" : "∞"]);
    if (api.scene === "wheel") rows.push([["接触点 (0, −0.3) 的速度", "velocity of contact point (0, −0.3)"], `(${api.fmt(vc[0], 3)}, ${api.fmt(vc[1], 3)}) m/s`]);
    else rows.push([["左轮 (0, 0.2) 的速度", "left wheel (0, 0.2) velocity"], `(${api.fmt(vx - w * 0.2, 3)}, ${api.fmt(vy, 3)}) m/s`]);
    return rows;
  },
  draw(api, s) {
    const W = api.w, H = api.h, k = Math.min(W, H) / 3.4, ox = W * 0.42, oy = H * 0.62;
    const X = (x) => ox + x * k, Y = (y) => oy - y * k;
    api.grid(W, H, k * 0.25);
    api.arrow(X(-1.5), Y(0), X(2.2), Y(0), api.css("--red"), 1.2); api.arrow(X(0), Y(-1.0), X(0), Y(1.5), api.css("--green"), 1.2);
    api.label("x", X(2.2) - 4, Y(0) + 12, api.css("--red"), 13); api.label("y", X(0) + 8, Y(1.5) + 4, api.css("--green"), 13);
    const w = api.p.w, v = [api.p.vx, api.p.vy];
    const th = s.th || 0, P = s.p || [0, 0], c = Math.cos(th), sn = Math.sin(th);
    const toS = (b) => [P[0] + c * b[0] - sn * b[1], P[1] + sn * b[0] + c * b[1]];
    if (s.trail && s.trail.length > 1) { for (let i = 1; i < s.trail.length; i++) api.line(X(s.trail[i - 1][0]), Y(s.trail[i - 1][1]), X(s.trail[i][0]), Y(s.trail[i][1]), api.css("--violet"), 2); }
    // 刚体轮廓
    const ctx = api.ctx;
    if (api.scene === "wheel") {
      api.line(X(-1.6), Y(-0.3), X(2.3), Y(-0.3), api.css("--ground"), 2);
      const cc = toS([0, 0]); ctx.beginPath(); ctx.arc(X(cc[0]), Y(cc[1]), 0.3 * k, 0, 2 * Math.PI); ctx.fillStyle = "rgba(9,105,218,0.12)"; ctx.fill(); ctx.strokeStyle = api.css("--accent"); ctx.lineWidth = 2; ctx.stroke();
      const sp = toS([0.3, 0]); api.line(X(cc[0]), Y(cc[1]), X(sp[0]), Y(sp[1]), api.css("--accent"), 2);
    } else {
      const B = [[-0.3, -0.25], [0.35, -0.25], [0.35, 0.25], [-0.3, 0.25]].map(toS);
      ctx.beginPath(); B.forEach((q, i) => (i ? ctx.lineTo(X(q[0]), Y(q[1])) : ctx.moveTo(X(q[0]), Y(q[1])))); ctx.closePath();
      ctx.fillStyle = "rgba(9,105,218,0.12)"; ctx.fill(); ctx.strokeStyle = api.css("--accent"); ctx.lineWidth = 2; ctx.stroke();
      [[0, 0.2], [0, -0.2]].map(toS).forEach((q) => api.circle(X(q[0]), Y(q[1]), 6, api.css("--ink")));
    }
    // 速度场：此刻（物体坐标系中）各点的速度
    if (!api.running) {
      const pts = api.scene === "wheel" ? [[0, 0], [0, 0.3], [0, -0.3], [0.3, 0], [-0.3, 0], [0.21, 0.21], [-0.21, 0.21], [0.21, -0.21], [-0.21, -0.21]]
                                        : [[-0.3, -0.25], [0.35, -0.25], [0.35, 0.25], [-0.3, 0.25], [0, 0], [0, 0.2], [0, -0.2], [0.35, 0]];
      pts.forEach((b) => {
        const q = toS(b), vb = [v[0] - w * b[1], v[1] + w * b[0]], vs = [c * vb[0] - sn * vb[1], sn * vb[0] + c * vb[1]];
        api.circle(X(q[0]), Y(q[1]), 3, api.css("--ink"));
        api.arrow(X(q[0]), Y(q[1]), X(q[0] + 0.6 * vs[0]), Y(q[1] + 0.6 * vs[1]), api.css("--orange"), 2.2);
      });
      if (Math.abs(w) > 1e-9) {
        const icr = toS([-v[1] / w, v[0] / w]);
        api.circle(X(icr[0]), Y(icr[1]), 6, null, api.css("--red")); api.circle(X(icr[0]), Y(icr[1]), 2.5, api.css("--red"));
        api.label(api.T("瞬心", "centre"), X(icr[0]) + 9, Y(icr[1]) - 9, api.css("--red"), 12);
      }
    }
    api.label(api.T("橙色箭头：各点速度（按 0.6 s 的位移画出）", "orange: velocities (drawn as 0.6 s of travel)"), 12, 18, api.css("--muted"), 12);
  },
});
