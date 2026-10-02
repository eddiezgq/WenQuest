// 实验 10.1 同一运动，两个参考系（配 10.1 节）。
// 场景 agv：地面坐标系 {s} 中，AGV 从原点出发、车头朝 +x，车速 v、转弯角速度 Ω（Ω > 0 左转）；零件静止于 (2.0, 0.5) m。
//   零件在 AGV 坐标系 {b} 中的位置 p_b = R_sb^T (p_s − p_sb)（式 (10.1.6)），速度 ṗ_b = −Ω ẑ × p_b − (v, 0, 0)。
// 场景 rain：雨滴相对地面以 6 m/s 竖直下落，汽车以 v 行驶；车上看雨滴的速度 = 雨滴速度 − 车速，倾角 atan(v/6)。
WQ.lab({
  title: ["实验 10.1 同一运动，两个参考系", "Lab 10.1 One motion, two reference frames"],
  goal: ["同时从地面和从 AGV 上观察同一个静止的零件；体会运动依赖于参考系，而换坐标系只换读数。",
         "Watch the same resting part from the ground and from the AGV at once; see that motion depends on the reference frame."],
  scenes: [
    { id: "agv", robot: true, name: ["转弯的 AGV", "A turning AGV"], hide: ["vc"],
      problem: { title: ["机器人问题：雷达说静止的零件在转圈", "Robot problem: the lidar says a resting part is circling"],
                 text: ["AGV 以 0.5 m/s 沿半径 2 m 的圆左转，地面上的零件静止。车上的雷达看到零件怎样运动？",
                        "The AGV turns left on a 2 m circle at 0.5 m/s; the part on the floor is at rest. How does the AGV's lidar see it move?"] } },
    { id: "rain", name: ["雨中行车", "Driving in the rain"], hide: ["v", "om"],
      problem: { title: ["生活中的例子：斜着落下的雨", "Everyday example: rain that falls slanted"],
                 text: ["无风时雨滴竖直下落，速度 6 m/s。坐在行驶的汽车里，雨丝为什么是斜的？",
                        "With no wind the drops fall straight down at 6 m/s. Why do they look slanted from a moving car?"] } },
  ],
  params: [
    { id: "v", name: ["AGV 车速 v", "AGV speed v"], min: 0, max: 1, step: 0.05, value: 0.5, unit: "m/s", digits: 2 },
    { id: "om", name: ["转弯角速度 Ω", "Turn rate Ω"], min: -0.5, max: 0.5, step: 0.05, value: 0.25, unit: "rad/s", digits: 2 },
    { id: "vc", name: ["汽车车速", "Car speed"], min: 0, max: 30, step: 1, value: 10, unit: "m/s", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["AGV", "AGV"], color: "#1f77b4" }, { name: ["零件", "part"], color: "#e07b00" }],
  tasks: [
    { id: "ex", robot: true, text: ["按算例 10.1.1 设置（v = 0.5 m/s，Ω = 0.25 rad/s），开始运行，读出零件在 {b} 中的速率。",
                                    "Set Example 10.1.1 (v = 0.5 m/s, Ω = 0.25 rad/s), run, and read the part's speed in {b}."],
      demo: { scene: "agv", set: { v: 0.5, om: 0.25 }, press: ["start"], wait: 6 } },
    { id: "straight", robot: true, text: ["把转弯角速度调为零：在 AGV 看来，零件沿直线以车速后退。",
                                          "Set the turn rate to zero: seen from the AGV the part moves straight back at the AGV's speed."],
      demo: { scene: "agv", set: { v: 0.6, om: 0 }, press: ["start"], wait: 6 } },
    { id: "rain", text: ["汽车以 10 m/s 行驶，读出车上看到的雨丝倾角。", "At 10 m/s read the slant of the rain seen from the car."],
      demo: { scene: "rain", set: { vc: 10 }, press: [], wait: 1 } },
  ],
  think: ["算例 10.1.1 中零件在 AGV 看来有指向 C 的加速度，可零件并没有受到水平方向的力。这说明了 AGV 参考系的什么性质？",
          "In Example 10.1.1 the part has an acceleration towards C as seen from the AGV, yet no horizontal force acts on it. What does this say about the AGV frame?"],

  P: [2.0, 0.5],
  pose(api, t) {                         // AGV 在 {s} 中的位置与航向
    const v = api.p.v, om = api.p.om;
    if (Math.abs(om) < 1e-9) return [v * t, 0, 0];
    return [v / om * Math.sin(om * t), v / om * (1 - Math.cos(om * t)), om * t];
  },
  inB(api, t) {                          // 零件在 {b} 中的位置与速度
    const [x, y, psi] = this.pose(api, t), dx = this.P[0] - x, dy = this.P[1] - y, c = Math.cos(psi), s = Math.sin(psi);
    const p = [c * dx + s * dy, -s * dx + c * dy];
    const om = api.p.om, v = api.p.v;
    return { p, vel: [om * p[1] - v, -om * p[0]] };
  },

  reset(api, s) { s.trail = []; s.drops = []; for (let i = 0; i < 40; i++) s.drops.push([Math.random(), Math.random()]); },
  update(dt, api, s) {
    if (api.scene === "agv") {
      const q = this.inB(api, api.t);
      if (!s.trail.length || Math.hypot(q.p[0] - s.trail[s.trail.length - 1][0], q.p[1] - s.trail[s.trail.length - 1][1]) > 0.03) s.trail.push(q.p);
      if (s.trail.length > 2000) s.trail.shift();
      const sp = Math.hypot(q.vel[0], q.vel[1]);
      if (api.t > 1 && Math.abs(api.p.v - 0.5) < 1e-6 && Math.abs(api.p.om - 0.25) < 1e-6 && Math.abs(sp - 0.625) < 1e-6) api.done("ex");
      if (api.t > 1 && Math.abs(api.p.om) < 1e-9 && api.p.v > 0 && Math.abs(sp - api.p.v) < 1e-9 && Math.abs(q.p[1] - this.P[1]) < 1e-9) api.done("straight");
      if (api.t > 40) api.stop();
    } else {
      s.drops.forEach((d) => { d[1] += dt * 0.6; if (d[1] > 1) { d[1] -= 1; d[0] = Math.random(); } });
      if (api.t > 30) api.stop();
    }
  },
  readouts(api, s) {
    if (api.scene === "rain") {
      const ang = Math.atan2(api.p.vc, 6) * 180 / Math.PI;
      if (Math.abs(api.p.vc - 10) < 1e-6) api.done("rain");
      return [[["雨滴相对地面", "drops relative to ground"], "6.0 m/s " + api.T("竖直向下", "straight down")],
              [["雨滴相对汽车的速率", "drop speed relative to car"], api.fmt(Math.hypot(api.p.vc, 6), 2) + " m/s"],
              [["雨丝与竖直方向的夹角", "slant from vertical"], api.fmt(ang, 1) + "°"]];
    }
    const q = this.inB(api, api.t), [x, y, psi] = this.pose(api, api.t);
    const sp = Math.hypot(q.vel[0], q.vel[1]);
    const rows = [[["AGV 在 {s} 中", "AGV in {s}"], `(${api.fmt(x, 2)}, ${api.fmt(y, 2)}) m, ${api.fmt(psi * 180 / Math.PI, 0)}°`],
                  [["零件在 {s} 中（静止）", "part in {s} (at rest)"], "(2.00, 0.50) m"],
                  [["零件在 {b} 中", "part in {b}"], `(${api.fmt(q.p[0], 3)}, ${api.fmt(q.p[1], 3)}) m`],
                  [["零件在 {b} 中的速率", "part speed in {b}"], api.fmt(sp, 4) + " m/s"]];
    if (Math.abs(api.p.om) > 1e-9) {
      const R0 = api.p.v / api.p.om, d = Math.hypot(this.P[0], this.P[1] - R0);
      rows.push([["Ω·|CP|（公式）", "Ω·|CP| (formula)"], api.fmt(Math.abs(api.p.om) * d, 4) + " m/s"]);
    }
    return rows;
  },
  draw(api, s) {
    const { w, h, ctx } = api, half = w / 2;
    api.line(half, 10, half, h - 10, api.css("--grid"), 1, [5, 5]);
    api.label(api.T("以地面为参考系", "Ground as reference"), half * 0.5, 16, api.css("--ink"), 13, "center");
    api.label(api.T("以 AGV（或汽车）为参考系", "AGV (or car) as reference"), half * 1.5, 16, api.css("--ink"), 13, "center");
    if (api.scene === "rain") {
      const gy = h * 0.78, cx = half * 0.5, carx = (api.t * api.p.vc * 8) % (half * 1.2) - half * 0.1;
      api.ground(gy, half - 6);
      s.drops.forEach((d) => { const px = d[0] * (half - 20) + 10, py = 30 + d[1] * (gy - 40); api.line(px, py, px, py + 12, "#58a6ff", 1.5); });
      api.agv(Math.max(30, Math.min(half - 40, carx)), gy, 70, "#1f77b4");
      const k = Math.atan2(api.p.vc, 6);
      s.drops.forEach((d) => { const px = half + 10 + d[0] * (half - 20), py = 30 + d[1] * (gy - 40); api.line(px, py, px - 12 * Math.sin(k), py + 12 * Math.cos(k), "#58a6ff", 1.5); });
      api.line(half + 6, gy, w, gy, api.css("--ground"), 2);
      api.agv(half * 1.5, gy, 70, "#1f77b4");
      return;
    }
    const k = Math.min(half / 7.5, h / 7);
    const L = (x, y) => [half * 0.42 + k * x, h * 0.62 - k * y], R = (x, y) => [half * 1.5 + k * x, h * 0.72 - k * y];
    // 左：地面
    const [x, y, psi] = this.pose(api, api.t);
    if (Math.abs(api.p.om) > 1e-9) { const R0 = api.p.v / api.p.om, c = L(0, R0); ctx.strokeStyle = api.css("--grid"); ctx.setLineDash([4, 4]); ctx.beginPath(); ctx.arc(c[0], c[1], Math.abs(R0) * k, 0, 2 * Math.PI); ctx.stroke(); ctx.setLineDash([]); }
    api.frame(...L(-2.6, -1.0), 0, 22, ["x", "y"], "{s}");
    const pp = L(...this.P);
    api.rect(pp[0] - 6, pp[1] - 6, 12, 12, "#e07b00");
    api.robot(...L(x, y), psi * 180 / Math.PI, 22, "#1f77b4");
    // 右：AGV 参考系
    api.robot(...R(0, 0), 0, 22, "#1f77b4");
    api.frame(...R(0, 0), 0, 30, ["x_b", "y_b"]);
    ctx.strokeStyle = "#e07b00"; ctx.lineWidth = 2; ctx.beginPath();
    s.trail.forEach((p, i) => { const q = R(p[0], p[1]); if (i) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]); });
    ctx.stroke();
    const qb = this.inB(api, api.t), pb = R(...qb.p);
    api.rect(pb[0] - 6, pb[1] - 6, 12, 12, "#e07b00");
    api.arrow(pb[0], pb[1], pb[0] + 40 * qb.vel[0], pb[1] - 40 * qb.vel[1], api.css("--amber"), 2.5);
  },
});
