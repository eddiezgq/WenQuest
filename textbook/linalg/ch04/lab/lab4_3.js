// 实验 4.3 变换的复合：AB 与 BA（配 4.3.5 节）。左图先做 B 再做 A（矩阵 AB），右图先做 A 再做 B（矩阵 BA）；
// A 是转 θ 的旋转，B 是剪切 [[1, k], [0, 1]] 或伸缩 diag(sx, sy)。AGV 场景用 3×3 齐次变换：“前进 d”与“原地转 θ”的两种次序。
WQ.lab({
  title: ["实验 4.3 变换的复合：AB 与 BA", "Lab 4.3 Composing transformations: AB versus BA"],
  goal: ["把旋转与剪切、旋转与伸缩按两种次序复合，比较网格、小旗和乘积矩阵；找出可以交换次序的情形；看 AGV 的两种运动次序走到哪里。",
         "Compose a rotation with a shear or a stretch in both orders; compare the grids, the flag and the product matrices; find when the order does not matter; see where the AGV ends up for the two orders of motion."],
  scenes: [
    { id: "shear", name: ["旋转与剪切", "Rotation and shear"], hide: ["sx", "sy", "d"],
      problem: { title: ["生活中的例子：先穿袜子还是先穿鞋", "Everyday example: socks first or shoes first"],
                 text: ["两个操作换个次序，结果往往不同。A 是转 θ 的旋转，B 是水平剪切 [[1, k], [0, 1]]。左图先剪切再旋转（AB），右图先旋转再剪切（BA）。",
                        "Swapping two operations usually changes the result. A rotates by θ, B is the horizontal shear [[1, k], [0, 1]]. Left: shear then rotate (AB); right: rotate then shear (BA)."] } },
    { id: "scale", name: ["旋转与伸缩", "Rotation and stretch"], hide: ["k", "d"],
      problem: { title: ["什么时候次序无关？", "When does the order not matter?"],
                 text: ["B 改为沿两个坐标轴的伸缩 diag(sx, sy)。调节 sx、sy 和 θ，找出 AB = BA 的条件。",
                        "B is now the stretch diag(sx, sy) along the axes. Adjust sx, sy and θ and find when AB = BA."] } },
    { id: "agv", robot: true, name: ["AGV 的两种走法", "Two AGV routes"], hide: ["k", "sx", "sy"],
      problem: { title: ["机器人问题：先走后转，还是先转后走？", "Robot problem: drive then turn, or turn then drive?"],
                 text: ["AGV 从原点出发、车头朝 x 轴。路线①：先前进 d，再原地转 θ；路线②：先原地转 θ，再前进 d。两条路线的终点和朝向一样吗？每一步是一个 3×3 齐次变换（4.4 节）。",
                        "The AGV starts at the origin facing +x. Route ①: drive d, then turn θ in place; route ②: turn θ, then drive d. Do the routes end at the same pose? Each step is a 3×3 homogeneous transform (Section 4.4)."] } },
  ],
  params: [
    { id: "th", name: ["转角 θ", "Angle θ"], min: -180, max: 180, step: 5, value: 30, unit: "°", digits: 0 },
    { id: "k", name: ["剪切系数 k", "Shear k"], min: -2, max: 2, step: 0.1, value: 1, digits: 1 },
    { id: "sx", name: ["x 方向伸缩 sx", "Stretch sx"], min: 0.2, max: 2, step: 0.1, value: 2, digits: 1 },
    { id: "sy", name: ["y 方向伸缩 sy", "Stretch sy"], min: 0.2, max: 2, step: 0.1, value: 1, digits: 1 },
    { id: "d", name: ["前进距离 d", "Distance d"], min: 0, max: 2, step: 0.1, value: 1, unit: "m", digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "fig", text: ["取 θ = 30°、k = 1，读出 AB 与 BA，与图 4.3.1 和算例 4.3.1 对照。", "Set θ = 30°, k = 1; read AB and BA and compare with Figure 4.3.1 and Example 4.3.1."],
      demo: { scene: "shear", set: { th: 30, k: 1 }, press: [], wait: 2 } },
    { id: "half", text: ["保持 k ≠ 0，找出一个不为 0° 的转角，使旋转与剪切可以交换（‖AB − BA‖ = 0）。", "Keep k ≠ 0 and find a nonzero angle for which the rotation and the shear commute (‖AB − BA‖ = 0)."],
      demo: { scene: "shear", set: { th: 180, k: 1 }, press: [], wait: 2 } },
    { id: "iso", text: ["在“旋转与伸缩”场景，θ 不是 0° 或 ±180° 时，调节 sx、sy 使 AB = BA。这时伸缩有什么特点？", "In the stretch scene, with θ not 0° or ±180°, adjust sx and sy so that AB = BA. What is special about the stretch?"],
      demo: { scene: "scale", set: { th: 60, sx: 1.5, sy: 1.5 }, press: [], wait: 2 } },
    { id: "agv90", robot: true, text: ["取 d = 1 m、θ = 90°，读出两条路线终点之间的距离。", "Set d = 1 m and θ = 90°; read the distance between the two end points."],
      demo: { scene: "agv", set: { d: 1, th: 90 }, press: [], wait: 2 } },
    { id: "agvfar", robot: true, text: ["保持 d ≥ 0.5 m，找出使两个终点相距最远的转角。最远是 d 的几倍？", "With d ≥ 0.5 m, find the angle that puts the two end points farthest apart. How many times d is that?"],
      demo: { scene: "agv", set: { d: 1, th: 180 }, press: [], wait: 2 } },
  ],
  think: ["两个绕原点的旋转总可以交换，两个剪切 [[1, k₁], [0, 1]]、[[1, k₂], [0, 1]] 也可以交换。一个水平剪切和一个竖直剪切呢？为什么？",
          "Two rotations about the origin always commute, and so do two horizontal shears. What about a horizontal and a vertical shear? Why?"],

  rot(th) { const t = th * Math.PI / 180, c = Math.cos(t), s = Math.sin(t); return [[c, -s], [s, c]]; },
  mats(api) {   // A, B and the two products
    const A = this.rot(api.p.th), B = api.scene === "scale" ? [[api.p.sx, 0], [0, api.p.sy]] : [[1, api.p.k], [0, 1]];
    return { A, B, AB: api.la.mul(A, B), BA: api.la.mul(B, A) };
  },
  H(R, t) { return [[R[0][0], R[0][1], t[0]], [R[1][0], R[1][1], t[1]], [0, 0, 1]]; },
  routes(api) {   // homogeneous transforms: route ① = Move(d)·Rot(θ), route ② = Rot(θ)·Move(d)
    const M = this.H([[1, 0], [0, 1]], [api.p.d, 0]), R = this.H(this.rot(api.p.th), [0, 0]);
    return { M, R, T1: api.la.mul(M, R), T2: api.la.mul(R, M) };
  },
  readouts(api) {
    const la = api.la;
    if (api.scene === "agv") {
      const { T1, T2 } = this.routes(api), gap = Math.hypot(T1[0][2] - T2[0][2], T1[1][2] - T2[1][2]);
      if (api.p.d === 1 && Math.abs(Math.abs(api.p.th) - 90) < 1e-9) api.done("agv90");
      if (api.p.d >= 0.5 && Math.abs(Math.abs(api.p.th) - 180) < 1e-9) api.done("agvfar");
      const pose = (T) => la.vstr([T[0][2], T[1][2]], 3) + " m, " + api.fmt(Math.atan2(T[1][0], T[0][0]) * 180 / Math.PI, 0) + "°";
      return [[["路线①：前进再转，矩阵", "Route ①: drive, turn — matrix"], la.str(T1, 2)],
              [["路线②：转再前进，矩阵", "Route ②: turn, drive — matrix"], la.str(T2, 2)],
              [["路线①终点与朝向", "Route ① end pose"], pose(T1)],
              [["路线②终点与朝向", "Route ② end pose"], pose(T2)],
              [["两终点的距离", "Distance between end points"], api.fmt(gap, 3) + " m"]];
    }
    const { A, B, AB, BA } = this.mats(api), diff = la.fro(la.sub(AB, BA)), comm = diff < 1e-9;
    if (api.scene === "shear" && api.p.th === 30 && api.p.k === 1) api.done("fig");
    if (api.scene === "shear" && Math.abs(api.p.k) > 0.05 && api.p.th !== 0 && comm) api.done("half");
    if (api.scene === "scale" && Math.abs(Math.sin(api.p.th * Math.PI / 180)) > 0.05 && comm) api.done("iso");
    return [[["A（旋转）", "A (rotation)"], la.str(A, 3)],
            [[api.scene === "scale" ? "B（伸缩）" : "B（剪切）", api.scene === "scale" ? "B (stretch)" : "B (shear)"], la.str(B, 2)],
            [["AB：先 B 后 A", "AB: B first, then A"], la.str(AB, 3)],
            [["BA：先 A 后 B", "BA: A first, then B"], la.str(BA, 3)],
            [["‖AB − BA‖", "‖AB − BA‖"], api.fmt(diff, 4)],
            [["可以交换吗", "Do they commute?"], comm ? api.T("可以：AB = BA", "yes: AB = BA") : api.T("不可以", "no")]];
  },
  flag: [[0, 0], [1, 0], [1, 0.5], [0.5, 0.5], [0.5, 1], [0, 1]],
  draw(api) {
    const { w, h } = api, la = api.la, red = api.css("--red"), green = api.css("--green"), muted = api.css("--muted");
    if (api.scene === "agv") { this.drawAgv(api); return; }
    const { AB, BA } = this.mats(api), s = Math.min(w * 0.085, h * 0.15), c = api.ctx;
    [[AB, w * 0.25, api.T("AB：先 B，再 A", "AB: B first, then A")], [BA, w * 0.75, api.T("BA：先 A，再 B", "BA: A first, then B")]].forEach(([M, cx, name]) => {
      c.save(); c.beginPath(); c.rect(cx - w * 0.25, 30, w * 0.5, h - 30); c.clip();
      const P = api.plane({ cx, cy: h * 0.55, s, w, h });
      P.grid(M, { n: 2, alpha: 0.3 });
      P.curve(this.flag, muted, 1, "rgba(140,140,140,0.15)", [4, 4]);
      P.curve(this.flag.map((q) => la.mv(M, q)), api.css("--amber"), 1.5, "rgba(201,143,0,0.6)");
      P.vec([M[0][0], M[1][0]], red); P.vec([M[0][1], M[1][1]], green);
      c.restore();
      api.label(name, cx, 18, api.css("--ink"), 14, "center");
    });
    api.line(w * 0.5, 30, w * 0.5, h - 10, api.css("--line"), 1);
    api.label(api.T("虚线：原来的小旗", "dashed: the original flag"), 10, h - 10, muted, 12);
  },
  drawAgv(api) {
    const { w, h } = api, { T1, T2 } = this.routes(api), s = Math.min(w / 6, h / 4.2), ox = w * 0.5, oy = h * 0.52;
    const X = (x, y) => [ox + s * x, oy - s * y], muted = api.css("--muted");
    for (let i = -3; i <= 3; i++) { api.line(...X(i, -2.2), ...X(i, 2.2), api.css("--grid"), 1); }
    for (let j = -2; j <= 2; j++) { api.line(...X(-3, j), ...X(3, j), api.css("--grid"), 1); }
    api.line(...X(-3, 0), ...X(3, 0), muted, 1); api.line(...X(0, -2.2), ...X(0, 2.2), muted, 1);
    const car = (T, color, name) => {
      const pts = [[-0.18, -0.12], [0.18, -0.12], [0.24, 0], [0.18, 0.12], [-0.18, 0.12]].map((q) => api.la.mv(T, [q[0], q[1], 1]));
      const c = api.ctx; c.beginPath(); pts.forEach((q, i) => { const [x, y] = X(q[0], q[1]); if (i) c.lineTo(x, y); else c.moveTo(x, y); });
      c.closePath(); c.fillStyle = color; c.globalAlpha = 0.75; c.fill(); c.globalAlpha = 1; c.strokeStyle = api.css("--ink"); c.lineWidth = 1.2; c.stroke();
      if (name) api.label(name, ...X(T[0][2] + 0.1, T[1][2] + 0.28), color, 14);
    };
    const d = api.p.d, t = api.p.th * Math.PI / 180;
    api.line(...X(0, 0), ...X(d, 0), api.css("--blue"), 2);   // route ①: straight along x, then turn
    api.line(...X(0, 0), ...X(d * Math.cos(t), d * Math.sin(t)), api.css("--red"), 2);   // route ②: turn first, then drive along the new heading
    car([[1, 0, 0], [0, 1, 0], [0, 0, 1]], api.css("--soft"), api.T("起点", "start"));
    car(T1, api.css("--blue"), "①"); car(T2, api.css("--red"), "②");
    api.label(api.T("蓝：先前进再转；红：先转再前进（网格 1 m）", "blue: drive then turn; red: turn then drive (grid 1 m)"), 10, 18, muted, 12);
  },
});
