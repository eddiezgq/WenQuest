// 实验 5.1 同一点在两个坐标系中的坐标（配 5.1 节）。车间地图 {m}（x 向东、y 向北，单位 m）；
// AGV 坐标系 {v}：原点在车体中心，x 轴指向车头，航向 ψ 从正东逆时针量。工位 Q 在 {m} 中为 (14.5, 8.0) m。
// q_v = R(ψ)ᵀ (q_m − p_mv)（式 (5.1.3)）；速度只用 R 变换（式 (5.1.4)）。
WQ.lab({
  title: ["实验 5.1 同一点在两个坐标系中的坐标", "Lab 5.1 One point in two frames"],
  goal: ["拖动 AGV（或游客）的位置和朝向，看同一个目标在地图坐标系和随身坐标系中的坐标怎样变化；比较点与速度的换算。",
         "Drag the AGV (or visitor): watch one target's coordinates in the map frame and in the moving frame; compare points with velocities."],
  scenes: [
    { id: "agv", robot: true, name: ["AGV 与货架工位", "AGV and shelf station"],
      problem: { title: ["机器人问题：工位在车头的哪一侧？", "Robot problem: on which side of the AGV is the station?"],
                 text: ["地图给出工位 Q 的坐标 (14.5, 8.0) m。AGV 的控制器需要知道它在车头前方多远、偏左还是偏右。",
                        "The map gives station Q at (14.5, 8.0) m. The AGV controller needs how far ahead it is and whether it is to the left or right."] } },
    { id: "museum", name: ["博物馆里的游客", "A visitor in a museum"],
      problem: { title: ["生活中的例子：展品在我的左边还是右边？", "Everyday example: is the exhibit to my left or right?"],
                 text: ["导览图标出展品的位置。游客站在某处、面朝某个方向，展品在他前方多远、左边多远？",
                        "The guide map marks the exhibit. Standing somewhere and facing some way, how far ahead and to the left is it?"] },
      params: { x: { value: 13.0 }, y: { value: 4.0 }, psi: { value: 90 } } },
  ],
  params: [
    { id: "x", name: ["位置 x（向东）", "Position x (east)"], min: 8, max: 18, step: 0.1, value: 10, unit: "m", digits: 1 },
    { id: "y", name: ["位置 y（向北）", "Position y (north)"], min: 1, max: 11, step: 0.1, value: 3, unit: "m", digits: 1 },
    { id: "psi", name: ["航向 ψ（从正东逆时针）", "Heading ψ (ccw from east)"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["把 AGV 停在算例 5.1.2 的位置 (12.0, 5.0) m、航向 30°，核对 Q 在 {v} 中的坐标。", "Park the AGV as in Example 5.1.2, (12.0, 5.0) m, heading 30°, and check Q in {v}."],
      demo: { scene: "agv", set: { x: 12, y: 5, psi: 30 }, press: [] } },
    { id: "ahead", robot: true, text: ["调整 AGV，使工位恰在车头正前方 2 m（Q 在 {v} 中为 (2, 0)）。", "Move the AGV so that the station is exactly 2 m straight ahead (Q in {v} = (2, 0))."],
      demo: { scene: "agv", set: { x: 12.5, y: 8, psi: 0 }, press: [] } },
    { id: "left", text: ["让游客站好、转身，使展品恰在他的正左方（前方分量为 0）。", "Place and turn the visitor so that the exhibit is exactly to the left (ahead component 0)."],
      demo: { scene: "museum", set: { x: 14.5, y: 5, psi: 0 }, press: [] } },
  ],
  think: ["AGV 只转动、不移动时，Q 到 AGV 的距离变不变？Q 在 {v} 中的坐标变不变？为什么？",
          "If the AGV only turns on the spot, does its distance to Q change? Do Q's coordinates in {v}? Why?"],

  Q: [14.5, 8.0],
  calc(api) {
    const t = api.p.psi * Math.PI / 180, c = Math.cos(t), s = Math.sin(t);
    const d = [this.Q[0] - api.p.x, this.Q[1] - api.p.y];
    const qv = [c * d[0] + s * d[1], -s * d[0] + c * d[1]];
    return { c, s, d, qv, vm: [c, s] };
  },
  reset(api, s) {},
  readouts(api, s) {
    const k = this.calc(api), near = (a, b, e) => Math.abs(a - b) < (e || 1e-6);
    if (api.scene === "agv" && near(api.p.x, 12) && near(api.p.y, 5) && near(api.p.psi, 30)) api.done("ex");
    if (api.scene === "agv" && near(k.qv[0], 2, 0.05) && near(k.qv[1], 0, 0.05)) api.done("ahead");
    if (api.scene === "museum" && near(k.qv[0], 0, 0.05) && k.qv[1] > 0.5) api.done("left");
    const f = (v, n) => `(${api.fmt(v[0], n)}, ${api.fmt(v[1], n)})`;
    const who = api.scene === "agv" ? ["AGV", "AGV"] : ["游客", "visitor"];
    return [
      [["{v} 的原点在 {m} 中 p_mv", "origin of {v} in {m}, p_mv"], f([api.p.x, api.p.y], 1) + " m"],
      [["Q 在 {m} 中 q_m", "Q in {m}, q_m"], f(this.Q, 1) + " m"],
      [["Q 在 {v} 中 q_v = Rᵀ(q_m − p_mv)", "Q in {v}, q_v = Rᵀ(q_m − p_mv)"], f(k.qv, 4) + " m"],
      [["前方 / 左方", "ahead / left"], `${api.fmt(k.qv[0], 3)} m / ${api.fmt(k.qv[1], 3)} m`],
      [[`Q 到${who[0]}的距离`, `distance from the ${who[1]} to Q`], api.fmt(Math.hypot(k.qv[0], k.qv[1]), 4) + " m"],
      [["1 m/s 前进的速度：{v} 中 / {m} 中", "1 m/s forward: in {v} / in {m}"], `(1, 0) / ${f(k.vm, 3)} m/s`],
    ];
  },
  draw(api, s) {
    const { w, h } = api, k = Math.min((w - 60) / 20, (h - 40) / 12.5), X = (x) => 45 + k * x, Y = (y) => h - 28 - k * y;
    const ctx = api.ctx;
    ctx.strokeStyle = api.css("--grid"); ctx.lineWidth = 1;
    for (let x = 0; x <= 20; x += 1) api.line(X(x), Y(0), X(x), Y(12), api.css("--grid"), 1);
    for (let y = 0; y <= 12; y += 1) api.line(X(0), Y(y), X(20), Y(y), api.css("--grid"), 1);
    api.frame(X(0), Y(0), 0, 2.2 * k, ["x", "y"], "{m}");
    const museum = api.scene === "museum";
    // 目标 Q
    if (museum) { api.rect(X(this.Q[0]) - 0.5 * k, Y(this.Q[1]) - 0.5 * k, k, k, api.css("--amber"), api.css("--ink"), 4);
      api.label(api.T("展品 Q", "exhibit Q"), X(this.Q[0]) + 0.7 * k, Y(this.Q[1]) - 0.6 * k, api.css("--ink"), 13); }
    else { api.rect(X(this.Q[0]) - 0.8 * k, Y(this.Q[1]) - 0.4 * k, 1.6 * k, 0.8 * k, api.css("--amber"), api.css("--ink"), 2);
      api.label(api.T("货架工位 Q", "station Q"), X(this.Q[0]) + 1.0 * k, Y(this.Q[1]) - 0.7 * k, api.css("--ink"), 13); }
    api.circle(X(this.Q[0]), Y(this.Q[1]), 4, api.css("--ink"));
    const px = X(api.p.x), py = Y(api.p.y);
    api.line(px, py, X(this.Q[0]), Y(this.Q[1]), api.css("--muted"), 1.5, [6, 5]);
    if (museum) {   // 游客：俯视的圆形头部和指向前方的鼻尖
      api.circle(px, py, 0.45 * k, api.css("--accent"), api.css("--ink"));
      const t = -api.p.psi * Math.PI / 180;
      api.circle(px + 0.5 * k * Math.cos(t), py + 0.5 * k * Math.sin(t), 0.12 * k, api.css("--ink"));
    } else api.robot(px, py, api.p.psi, 1.4 * k, api.css("--accent"));
    api.frame(px, py, api.p.psi, 1.8 * k, ["x", "y"], "{v}", api.css("--blue"));
    // 速度箭头（自由矢量）：画在车上，沿车头
    const t = api.p.psi * Math.PI / 180;
    if (!museum) api.arrow(px, py, px + 2.6 * k * Math.cos(t), py - 2.6 * k * Math.sin(t), api.css("--amber"), 2);
  },
});
