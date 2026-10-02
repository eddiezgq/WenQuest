// 实验 10.2 位置、速度、加速度与速度图（配 10.2 节）。
// 场景 glue：SCARA 涂胶，工具尖按 x = xc + a cos ωt、y = yc + b sin ωt 运动（式 (10.2.9)），ω = 2π/T，xc = 0.40 m、yc = 0.05 m；
//   速度、加速度按式 (10.2.10) 计算。左边俯视轨迹，右边速度图（速度矢量平移到同一起点后端点画出的曲线）。
// 场景 ball：投篮，出手速度 v0、仰角 α，加速度 (0, −g)，g = 9.81 m/s²；速度图是一条竖直线。
WQ.lab({
  title: ["实验 10.2 位置、速度、加速度与速度图", "Lab 10.2 Position, velocity, acceleration and the hodograph"],
  goal: ["观察动点的位置矢量、速度和加速度怎样随时间变化，并在速度图上看出加速度就是速度图的切线方向。",
         "Watch the position vector, velocity and acceleration change in time, and see on the hodograph that the acceleration is tangent to it."],
  scenes: [
    { id: "glue", robot: true, name: ["SCARA 涂胶椭圆", "SCARA glue ellipse"], hide: ["v0", "ang"],
      problem: { title: ["机器人问题：胶条为什么粗细不匀", "Robot problem: why the glue bead is uneven"],
                 text: ["工具尖按参数均匀增加的方式走椭圆，出胶量恒定。速率在哪里最大、哪里最小？",
                        "The tool follows the ellipse with an evenly growing parameter at constant glue flow. Where is the speed largest and smallest?"] } },
    { id: "ball", name: ["投篮", "Shooting a basketball"], hide: ["a", "b", "T"],
      problem: { title: ["生活中的例子：篮球的速度图", "Everyday example: the hodograph of a basketball"],
                 text: ["出手后篮球只受重力，加速度始终竖直向下。它的速度图是什么形状？",
                        "After release the ball feels only gravity, so its acceleration always points down. What does its hodograph look like?"] } },
  ],
  params: [
    { id: "a", name: ["半长轴 a", "Semi-major axis a"], min: 0.05, max: 0.15, step: 0.01, value: 0.12, unit: "m", digits: 2 },
    { id: "b", name: ["半短轴 b", "Semi-minor axis b"], min: 0.03, max: 0.15, step: 0.01, value: 0.08, unit: "m", digits: 2 },
    { id: "T", name: ["走一圈的时间 T", "Time per loop T"], min: 2, max: 8, step: 0.5, value: 4, unit: "s", digits: 1 },
    { id: "v0", name: ["出手速度 v₀", "Release speed v₀"], min: 5, max: 12, step: 0.5, value: 8, unit: "m/s", digits: 1 },
    { id: "ang", name: ["出手仰角 α", "Release angle α"], min: 30, max: 70, step: 1, value: 52, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["位置矢量 r", "position r"], color: "#1d2327" }, { name: ["速度 v", "velocity v"], color: "#e07b00" }, { name: ["加速度 a", "acceleration a"], color: "#c0392b" }],
  tasks: [
    { id: "ex", robot: true, text: ["按算例 10.2.1 设置（a = 0.12 m，b = 0.08 m，T = 4 s），运行一整圈，读出速率的最大值和最小值。",
                                    "Set Example 10.2.1 (a = 0.12 m, b = 0.08 m, T = 4 s), run one full loop and read the largest and smallest speed."],
      demo: { scene: "glue", set: { a: 0.12, b: 0.08, T: 4 }, press: ["start"], wait: 6 } },
    { id: "circle", robot: true, text: ["把椭圆调成圆（a = b），运行：速率恒定，加速度仍然指向中心。",
                                        "Make the ellipse a circle (a = b) and run: the speed is constant, the acceleration still points to the centre."],
      demo: { scene: "glue", set: { a: 0.1, b: 0.1, T: 4 }, press: ["start"], wait: 3 } },
    { id: "apex", text: ["投篮场景中运行，观察速度图是一条竖直线；读出篮球到达最高点的时间。",
                         "Run the basketball: the hodograph is a vertical line; read the time to the top of the flight."],
      demo: { scene: "ball", set: { v0: 8, ang: 52 }, press: ["start"], wait: 3 } },
  ],
  think: ["按算例 10.2.1 的参数化，速率最大和最小之比是多少？要让胶条粗细均匀，应当怎样改变工具尖的运动规律（10.5 节）？",
          "With the parametrisation of Example 10.2.1, what is the ratio of the largest to the smallest speed? How should the motion be changed for an even bead (Section 10.5)?"],

  G: 9.81,
  kin(api, t) {               // 位置、速度、加速度（二维）
    if (api.scene === "ball") {
      const al = api.p.ang * Math.PI / 180, vx = api.p.v0 * Math.cos(al), vy = api.p.v0 * Math.sin(al);
      return { r: [vx * t, 2.0 + vy * t - 0.5 * this.G * t * t], v: [vx, vy - this.G * t], a: [0, -this.G] };
    }
    const w = 2 * Math.PI / api.p.T, a = api.p.a, b = api.p.b;
    return { r: [0.4 + a * Math.cos(w * t), 0.05 + b * Math.sin(w * t)], v: [-a * w * Math.sin(w * t), b * w * Math.cos(w * t)],
             a: [-a * w * w * Math.cos(w * t), -b * w * w * Math.sin(w * t)] };
  },
  reset(api, s) { s.vmax = 0; s.vmin = Infinity; s.hod = []; s.path = []; s.apex = null; s.const = true; },
  update(dt, api, s) {
    const k = this.kin(api, api.t), sp = Math.hypot(k.v[0], k.v[1]);
    s.vmax = Math.max(s.vmax, sp); s.vmin = Math.min(s.vmin, sp);
    s.hod.push(k.v); s.path.push(k.r);
    if (s.hod.length > 3000) { s.hod.shift(); s.path.shift(); }
    if (api.scene === "glue") {
      const w = 2 * Math.PI / api.p.T;
      if (Math.abs(sp - api.p.a * w) > 1e-9) s.const = false;
      if (api.t >= api.p.T) {
        if (Math.abs(api.p.a - 0.12) < 1e-9 && Math.abs(api.p.b - 0.08) < 1e-9 && Math.abs(api.p.T - 4) < 1e-9) api.done("ex");
        api.stop();
      }
      if (Math.abs(api.p.a - api.p.b) < 1e-9 && api.t > 0.5 && s.const) {
        const c = [k.r[0] - 0.4, k.r[1] - 0.05], dotp = c[0] * k.a[0] + c[1] * k.a[1];
        if (dotp < 0 && Math.abs(c[0] * k.a[1] - c[1] * k.a[0]) < 1e-9) api.done("circle");
      }
    } else {
      if (k.v[1] <= 0 && s.apex === null) { s.apex = api.t; api.done("apex"); }
      if (k.r[1] < 0) api.stop();
    }
  },
  readouts(api, s) {
    const k = this.kin(api, api.t), sp = Math.hypot(k.v[0], k.v[1]), am = Math.hypot(k.a[0], k.a[1]);
    const ang = Math.acos(Math.max(-1, Math.min(1, (k.v[0] * k.a[0] + k.v[1] * k.a[1]) / (sp * am || 1)))) * 180 / Math.PI;
    const V = (x, d) => `(${api.fmt(x[0], d)}, ${api.fmt(x[1], d)})`;
    const rows = [[["时间 t", "time t"], api.fmt(api.t, 2) + " s"], [["位置", "position"], V(k.r, 4) + " m"],
                  [["速度", "velocity"], V(k.v, 4) + " m/s"], [["加速度", "acceleration"], V(k.a, 4) + " m/s²"],
                  [["速率 |v|", "speed |v|"], api.fmt(sp, 5) + " m/s"], [["v 与 a 的夹角", "angle between v and a"], api.fmt(ang, 1) + "°"]];
    if (api.scene === "glue") rows.push([["已测速率最大 / 最小", "speed max / min so far"], s.vmax ? `${api.fmt(s.vmax, 5)} / ${api.fmt(s.vmin, 5)} m/s` : "—"]);
    else rows.push([["到达最高点的时间", "time to the top"], s.apex === null ? "—" : api.fmt(s.apex, 3) + " s"]);
    return rows;
  },
  draw(api, s) {
    const { w, h, ctx } = api, split = w * 0.6;
    api.line(split, 10, split, h - 10, api.css("--grid"), 1, [5, 5]);
    api.label(api.T("轨迹（俯视）", "Path (top view)"), split / 2, 16, api.css("--ink"), 13, "center");
    api.label(api.T("速度图", "Hodograph"), (split + w) / 2, 16, api.css("--ink"), 13, "center");
    const ball = api.scene === "ball";
    const k = ball ? Math.min(split / 8, h / 5.5) : Math.min(split / 0.75, h / 0.4);
    const O = ball ? [30, h - 30] : [40, h * 0.72];
    const X = (p) => [O[0] + k * p[0], O[1] - k * p[1]];
    const kv = ball ? Math.min((w - split) / 22, h / 26) : Math.min((w - split) / 0.5, h / 0.5);
    const H0 = [(split + w) / 2, h / 2];
    const Hp = (v) => [H0[0] + kv * v[0], H0[1] - kv * v[1]];
    api.line(H0[0] - (w - split) * 0.45, H0[1], H0[0] + (w - split) * 0.45, H0[1], api.css("--grid"), 1);
    api.line(H0[0], 30, H0[0], h - 20, api.css("--grid"), 1);
    // 完整轨迹与速度图（虚线）
    const N = 120, full = [], fullv = [];
    const Tt = ball ? 2 * api.p.v0 * Math.sin(api.p.ang * Math.PI / 180) / this.G * 1.2 : api.p.T;
    for (let i = 0; i <= N; i++) { const q = this.kin(api, Tt * i / N); full.push(X(q.r)); fullv.push(Hp(q.v)); }
    ctx.setLineDash([4, 4]); ctx.strokeStyle = api.css("--muted"); ctx.lineWidth = 1;
    [full, fullv].forEach((pts) => { ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.stroke(); });
    ctx.setLineDash([]);
    if (ball) { api.ground(O[1], split - 10); api.circle(X([7.0, 3.05])[0], X([7.0, 3.05])[1], 8, null, "#c0392b"); }
    else { api.frame(O[0], O[1], 0, 30, ["x", "y"], "{s}"); const c = X([0.4, 0.05]); api.line(c[0] - 5, c[1], c[0] + 5, c[1], api.css("--muted"), 1); api.line(c[0], c[1] - 5, c[0], c[1] + 5, api.css("--muted"), 1); }
    const q = this.kin(api, api.t), P = X(q.r);
    if (!ball) api.arrow(O[0], O[1], P[0], P[1], api.css("--ink"), 1.5);
    const sv = ball ? 0.12 * k : 0.6 * k, sa = ball ? 0.04 * k : 0.35 * k;
    api.arrow(P[0], P[1], P[0] + sv * q.v[0], P[1] - sv * q.v[1], "#e07b00", 3);
    api.arrow(P[0], P[1], P[0] + sa * q.a[0], P[1] - sa * q.a[1], "#c0392b", 3);
    api.circle(P[0], P[1], ball ? 7 : 4, ball ? "#e07b00" : api.css("--ink"));
    const V = Hp(q.v);
    api.arrow(H0[0], H0[1], V[0], V[1], "#e07b00", 2.5);
    const ka = ball ? 0.08 : 0.35;
    api.arrow(V[0], V[1], V[0] + ka * kv * q.a[0], V[1] - ka * kv * q.a[1], "#c0392b", 2.5);
  },
});
