// 实验 1.2 差速 AGV 与线性变换演示台（配 1.2 节）。轮半径 r = 0.075 m，轮距 b = 0.40 m（与程序 1.2.1 相同）。
// (v, ω)ᵀ = A (ω_L, ω_R)ᵀ，A = [[r/2, r/2], [−r/b, r/b]]；车体从原点出发、车头朝上，按 v、ω 匀速走 2 s。
WQ.lab({
  title: ["实验 1.2 差速 AGV 与线性变换演示台", "Lab 1.2 Differential-drive AGV and linear-map bench"],
  goal: ["拖动两个轮速，看 AGV 在 2 秒内走出的轨迹，读出车体的前进速度、转动角速度和转弯半径；拖动矩阵的四个元素，看平面网格怎样变形。",
         "Drag the two wheel speeds and watch the path the AGV drives in 2 s; read the forward speed, the turn rate and the turning radius. Drag the four matrix entries and watch the plane's grid deform."],
  scenes: [
    { id: "agv", robot: true, name: ["差速 AGV", "Differential-drive AGV"], hide: ["a", "b", "c", "d"],
      problem: { title: ["机器人问题：两个轮子各该转多快？", "Robot problem: how fast should each wheel turn?"],
                 text: ["调度系统给出车体的前进速度 v 和转动角速度 ω，电机能控制的却是左右轮的角速度。两者之间是一个 2×2 矩阵。",
                        "The scheduler gives the body's forward speed v and turn rate ω; the motors control the left and right wheel speeds. A 2×2 matrix links the two."] } },
    { id: "mat", name: ["矩阵与网格", "Matrix and grid"], hide: ["wl", "wr"],
      problem: { title: ["矩阵是一个几何变换", "A matrix is a geometric map"],
                 text: ["矩阵把平面上的每个点 (x, y) 映到新的位置。红、绿两个向量是 (1, 0) 和 (0, 1) 的像，也就是矩阵的两列。",
                        "A matrix moves every point (x, y) of the plane. The red and green vectors are the images of (1, 0) and (0, 1): the two columns."] } },
  ],
  params: [
    { id: "wl", name: ["左轮角速度 ω_L", "Left wheel speed ω_L"], min: -10, max: 10, step: 0.01, value: 2, unit: "rad/s", digits: 2 },
    { id: "wr", name: ["右轮角速度 ω_R", "Right wheel speed ω_R"], min: -10, max: 10, step: 0.01, value: 6, unit: "rad/s", digits: 2 },
    { id: "a", name: ["a（第 1 行第 1 列）", "a (row 1, col 1)"], min: -2, max: 2, step: 0.1, value: 1.5, digits: 1 },
    { id: "b", name: ["b（第 1 行第 2 列）", "b (row 1, col 2)"], min: -2, max: 2, step: 0.1, value: 0, digits: 1 },
    { id: "c", name: ["c（第 2 行第 1 列）", "c (row 2, col 1)"], min: -2, max: 2, step: 0.1, value: 0, digits: 1 },
    { id: "d", name: ["d（第 2 行第 2 列）", "d (row 2, col 2)"], min: -2, max: 2, step: 0.1, value: 0.5, digits: 1 },
  ],
  tasks: [
    { id: "straight", robot: true, text: ["让 AGV 以 0.3 m/s 直线前进。两个轮速有什么关系？", "Drive the AGV straight at 0.3 m/s. How are the two wheel speeds related?"],
      demo: { scene: "agv", set: { wl: 4, wr: 4 }, press: [], wait: 1 } },
    { id: "spin", robot: true, text: ["让 AGV 原地转圈（v = 0，ω ≠ 0）。", "Make the AGV spin on the spot (v = 0, ω ≠ 0)."],
      demo: { scene: "agv", set: { wl: -3, wr: 3 }, press: [], wait: 1 } },
    { id: "target", robot: true, text: ["找出使 v = 0.5 m/s、ω = 0.5 rad/s 的轮速（误差小于 0.005），与 1.2 节的结果比较。", "Find the wheel speeds giving v = 0.5 m/s, ω = 0.5 rad/s (within 0.005); compare with Section 1.2."],
      demo: { scene: "agv", set: { wl: 5.33, wr: 8 }, press: [], wait: 1 } },
    { id: "shear", text: ["在“矩阵与网格”场景做出一个剪切：一条坐标轴不动，另一条斜过去，面积不变。", "In the matrix scene make a shear: one axis stays, the other slants, the area is unchanged."],
      demo: { scene: "mat", set: { a: 1, b: 1, c: 0, d: 1 }, press: [], wait: 1 } },
  ],
  think: ["两个轮速都加倍，轨迹怎样变化？两组轮速相加呢？这说明了 (ω_L, ω_R) 到 (v, ω) 的映射有什么性质？",
          "Double both wheel speeds: how does the path change? Add two sets of wheel speeds? What property of the map (ω_L, ω_R) → (v, ω) does this show?"],

  r: 0.075, b: 0.40, T: 2,
  body(api) { const r = this.r, b = this.b, wl = api.p.wl, wr = api.p.wr; return { v: r * (wl + wr) / 2, w: r * (wr - wl) / b }; },
  at(v, w, t) {   // pose after time t, starting at the origin heading up (+y)
    const h = Math.PI / 2;
    if (Math.abs(w) < 1e-9) return [v * t * Math.cos(h), v * t * Math.sin(h), h];
    const R = v / w;
    return [R * (Math.sin(h + w * t) - Math.sin(h)), -R * (Math.cos(h + w * t) - Math.cos(h)), h + w * t];
  },
  update(dt, api) { if (api.t >= this.T) api.stop(); },
  readouts(api) {
    if (api.scene === "mat") {
      const A = [[api.p.a, api.p.b], [api.p.c, api.p.d]], det = api.la.det(A);
      const near = (x, y) => Math.abs(x - y) < 1e-6;
      if (near(api.p.a, 1) && near(api.p.d, 1) && ((near(api.p.c, 0) && Math.abs(api.p.b) > 0.15) || (near(api.p.b, 0) && Math.abs(api.p.c) > 0.15))) api.done("shear");
      return [[["矩阵", "Matrix"], api.la.str(A, 1)],
              [["第 1 列：(1, 0) 的像", "Column 1: image of (1, 0)"], api.la.vstr([api.p.a, api.p.c], 1)],
              [["第 2 列：(0, 1) 的像", "Column 2: image of (0, 1)"], api.la.vstr([api.p.b, api.p.d], 1)],
              [["单位正方形的像的面积 |ad − bc|", "Area of the unit square's image |ad − bc|"], api.fmt(Math.abs(det), 3)],
              [["是否翻面（ad − bc < 0）", "Flipped (ad − bc < 0)"], det < 0 ? api.T("是", "yes") : api.T("否", "no")]];
    }
    const { v, w } = this.body(api);
    if (Math.abs(v - 0.3) < 0.005 && Math.abs(w) < 0.005) api.done("straight");
    if (Math.abs(v) < 0.005 && Math.abs(w) > 0.1) api.done("spin");
    if (Math.abs(v - 0.5) < 0.005 && Math.abs(w - 0.5) < 0.005) api.done("target");
    const R = Math.abs(w) < 1e-6 ? "∞" : api.fmt(v / w, 3) + " m";
    return [[["车体前进速度 v", "Forward speed v"], api.fmt(v, 4) + " m/s"],
            [["车体角速度 ω（逆时针为正）", "Turn rate ω (counter-clockwise +)"], api.fmt(w, 4) + " rad/s"],
            [["转弯半径 v/ω", "Turning radius v/ω"], R],
            [["左轮单独的贡献 ω_L a₁", "Left wheel alone ω_L a₁"], api.la.vstr([this.r / 2 * api.p.wl, -this.r / this.b * api.p.wl], 4)],
            [["右轮单独的贡献 ω_R a₂", "Right wheel alone ω_R a₂"], api.la.vstr([this.r / 2 * api.p.wr, this.r / this.b * api.p.wr], 4)],
            [["两者之和 (v, ω)", "Their sum (v, ω)"], api.la.vstr([v, w], 4)]];
  },
  draw(api) {
    const { w: W, h: H } = api, muted = api.css("--muted"), red = api.css("--red"), green = api.css("--green");
    if (api.scene === "mat") {
      const A = [[api.p.a, api.p.b], [api.p.c, api.p.d]], s = Math.min(W * 0.2, H * 0.4) * 0.55;
      const L = api.plane({ cx: W * 0.25, cy: H * 0.55, s, w: W, h: H });
      const R = api.plane({ cx: W * 0.72, cy: H * 0.55, s, w: W, h: H });
      L.grid(null, { n: 3, alpha: 0.3 }); L.curve([[0, 0], [1, 0], [1, 1], [0, 1]], api.css("--ink"), 1.5, "rgba(201,143,0,0.25)");
      L.vec([1, 0], red, "(1, 0)"); L.vec([0, 1], green, "(0, 1)");
      R.grid(A, { n: 3, alpha: 0.3 }); R.curve([[0, 0], [1, 0], [1, 1], [0, 1]].map((q) => api.la.mv(A, q)), api.css("--ink"), 1.5, "rgba(201,143,0,0.25)");
      R.vec([api.p.a, api.p.c], red, api.T("第 1 列", "col 1")); R.vec([api.p.b, api.p.d], green, api.T("第 2 列", "col 2"));
      api.label(api.T("原来的平面", "original plane"), W * 0.25, 18, muted, 13, "center");
      api.label(api.T("矩阵作用之后", "after the matrix"), W * 0.72, 18, muted, 13, "center");
      api.arrow(W * 0.46, H * 0.55, W * 0.51, H * 0.55, muted, 2);
      return;
    }
    // AGV top view: 1 m = k px, origin at the start point
    const { v, w } = this.body(api), k = Math.min(W, H) * 0.32, ox = W * 0.42, oy = H * 0.62, X = (x, y) => [ox + k * x, oy - k * y];
    for (let i = -6; i <= 6; i++) {
      const c = i ? api.css("--grid") : muted;
      api.line(...X(i * 0.25, -1.6), ...X(i * 0.25, 1.6), c, 1); api.line(...X(-1.6, i * 0.25), ...X(1.6, i * 0.25), c, 1);
    }
    const pts = [];
    for (let i = 0; i <= 100; i++) pts.push(X(...this.at(v, w, this.T * i / 100)));
    const c = api.ctx; c.beginPath(); pts.forEach((q, i) => (i ? c.lineTo(...q) : c.moveTo(...q)));
    c.setLineDash([6, 5]); c.strokeStyle = api.css("--blue"); c.lineWidth = 2; c.stroke(); c.setLineDash([]);
    const t = api.running ? api.t : api.t >= this.T ? this.T : 0, pose = this.at(v, w, Math.min(t, this.T));
    if (t > 0) {
      c.beginPath(); for (let i = 0; i <= 100; i++) { const q = X(...this.at(v, w, t * i / 100)); i ? c.lineTo(...q) : c.moveTo(...q); }
      c.strokeStyle = api.css("--amber"); c.lineWidth = 3; c.stroke();
    }
    api.robot(...X(pose[0], pose[1]), pose[2] * 180 / Math.PI, 0.4 * k, api.css("--accent"));
    api.label(api.T("虚线：2 s 内的轨迹；网格 0.25 m", "dashed: path in 2 s; grid 0.25 m"), W - 10, 18, muted, 12, "right");
    api.label(api.T("出发点", "start"), ...X(0.22, -0.3), muted, 12);
  },
});
