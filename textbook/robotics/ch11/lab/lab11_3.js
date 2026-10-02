// 实验 11.3 构型空间（配 11.3 节）。
// 机器人场景：平面 2R 臂（大臂 0.425 m、小臂 0.392 m）与圆形立柱（圆心 (0.45, 0.35) m、半径 0.10 m），右边是构型空间 [−180°, 180°)²，
// 灰色为构型空间障碍物（2° 网格逐点检查两根连杆与立柱的距离）。生活场景：钟表的两根指针，构型空间同为环面，齿轮把构型限制在 θm = 12 θh 上。
WQ.lab({
  title: ["实验 11.3 构型空间", "Lab 11.3 Configuration space"],
  goal: ["拖动关节角，看手臂和构型空间中的点同步运动；认识构型空间障碍物、肘上与肘下两组解，以及环面的“粘合”。",
         "Drag the joint angles and watch the arm and its point in C-space move together; meet C-obstacles, elbow-up and elbow-down solutions, and the glued edges of the torus."],
  scenes: [
    { id: "arm", robot: true, name: ["两连杆臂与立柱", "2R arm and a post"], hide: ["tm"],
      problem: { title: ["机器人问题：在关节角里找一条不碰撞的路", "Robot problem: a collision-free path in joint angles"],
                 text: ["手臂缩成构型空间中的一个点，立柱变成灰色的禁区。θ = 180° 与 −180° 是同一个构型：正方形的左右边、上下边是粘在一起的。",
                        "The arm becomes one point in C-space and the post a grey forbidden region. θ = 180° and −180° are the same: the square's opposite edges are glued."] } },
    { id: "clock", name: ["钟表的两根指针", "Clock hands"], hide: ["t1", "t2"],
      problem: { title: ["生活中的例子：两针的构型空间", "Everyday example: the hands' C-space"],
                 text: ["两针各是一个转动关节，构型空间是环面；齿轮联动使分针角 = 12 × 时针角（模 360°），构型只能在一条曲线上。",
                        "Each hand is a revolute joint, so the C-space is a torus; the gearing sets minute angle = 12 × hour angle (mod 360°), a curve on it."] } },
  ],
  params: [
    { id: "t1", name: ["关节 1 θ₁", "Joint 1 θ₁"], min: -180, max: 180, step: 0.5, value: 150, unit: "°", digits: 1 },
    { id: "t2", name: ["关节 2 θ₂", "Joint 2 θ₂"], min: -180, max: 180, step: 0.5, value: -60, unit: "°", digits: 1 },
    { id: "tm", name: ["从 12:00 起经过的时间", "Time since 12:00"], min: 0, max: 720, step: 0.5, value: 0, unit: "min", digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "hit", robot: true, text: ["让手臂碰到立柱，观察构型空间中的点落在灰色区域里。", "Make the arm touch the post and see the point fall in the grey region."],
      demo: { scene: "arm", set: { t1: 38, t2: 0 }, press: [] } },
    { id: "up", robot: true, text: ["用肘上构型（θ₂ < 0）把末端送到绿色目标点 (0.55, −0.25) m（误差小于 1 cm）。", "With elbow up (θ₂ < 0) put the tip on the green target (0.55, −0.25) m, within 1 cm."],
      demo: { scene: "arm", set: { t1: 16, t2: -84.5 }, press: [] } },
    { id: "down", robot: true, text: ["用肘下构型（θ₂ > 0）到达同一个目标点，比较两组关节角。", "Reach the same target with elbow down (θ₂ > 0) and compare the two joint-angle pairs."],
      demo: { scene: "arm", set: { t1: -64.5, t2: 84.5 }, press: [] } },
    { id: "clock", text: ["生活场景：找出 12:00 以后两针第一次重合的时刻（两针相差小于 1°）。", "Everyday scene: find the first time after 12:00 when the hands overlap (within 1°)."],
      demo: { scene: "clock", set: { tm: 65.5 }, press: [] } },
  ],
  think: ["12 小时内两针重合几次？在构型空间的正方形上数一数橙色曲线与对角线的交点。", "How many times do the hands overlap in 12 hours? Count where the orange curve meets the diagonal on the square."],

  L1: 0.425, L2: 0.392, OC: [0.45, 0.35], OR: 0.1, TGT: [0.55, -0.25],
  fk(t1, t2) {
    const e = [this.L1 * Math.cos(t1), this.L1 * Math.sin(t1)];
    return [e, [e[0] + this.L2 * Math.cos(t1 + t2), e[1] + this.L2 * Math.sin(t1 + t2)]];
  },
  segd(p, a, b) {
    const ab = [b[0] - a[0], b[1] - a[1]], L = ab[0] * ab[0] + ab[1] * ab[1];
    const t = Math.max(0, Math.min(1, ((p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1]) / L));
    return Math.hypot(p[0] - a[0] - t * ab[0], p[1] - a[1] - t * ab[1]);
  },
  hit(t1, t2) {
    const [e, w] = this.fk(t1, t2);
    return this.segd(this.OC, [0, 0], e) < this.OR || this.segd(this.OC, e, w) < this.OR;
  },
  grid() {                              // 构型空间障碍物：2° 网格，只算一次
    if (this._g) return this._g;
    const g = [], d = Math.PI / 180;
    for (let i = 0; i < 180; i++) for (let j = 0; j < 180; j++) {
      const a = (-180 + 2 * i + 1) * d, b = (-180 + 2 * j + 1) * d;
      if (this.hit(a, b)) g.push([i, j]);
    }
    this._g = g;
    return g;
  },
  hands(api) {                          // 时针、分针角（度，从 12 点方向顺时针量）
    const t = api.p.tm;
    return [(0.5 * t) % 360, (6 * t) % 360];
  },
  readouts(api, s) {
    if (api.scene === "arm") {
      const d = Math.PI / 180, t1 = api.p.t1 * d, t2 = api.p.t2 * d, [, w] = this.fk(t1, t2), h = this.hit(t1, t2);
      const err = Math.hypot(w[0] - this.TGT[0], w[1] - this.TGT[1]);
      if (h) api.done("hit");
      if (err < 0.01 && api.p.t2 < 0) api.done("up");
      if (err < 0.01 && api.p.t2 > 0) api.done("down");
      return [[["构型 (θ₁, θ₂)", "configuration (θ₁, θ₂)"], `(${api.fmt(api.p.t1, 1)}°, ${api.fmt(api.p.t2, 1)}°)`],
              [["末端位置", "tip"], `(${api.fmt(w[0], 3)}, ${api.fmt(w[1], 3)}) m`],
              [["离目标", "to target"], api.fmt(err * 1000, 1) + " mm"],
              [["碰撞", "collision"], h ? (api.lang() === "en" ? "yes" : "是") : (api.lang() === "en" ? "no" : "否")],
              [["肘向", "elbow"], api.p.t2 < 0 ? (api.lang() === "en" ? "up" : "上") : (api.lang() === "en" ? "down" : "下")]];
    }
    const [ah, am] = this.hands(api), diff = Math.abs(((am - ah + 540) % 360) - 180);
    if (diff < 1 && api.p.tm > 1 && api.p.tm < 719) api.done("clock");
    const hh = Math.floor(api.p.tm / 60), mm = api.p.tm - 60 * hh;
    return [[["时刻", "time"], `${hh === 0 ? 12 : hh}:${String(Math.floor(mm)).padStart(2, "0")}:${String(Math.round((mm % 1) * 60)).padStart(2, "0")}`],
            [["时针角 θh", "hour hand θh"], api.fmt(ah, 1) + "°"], [["分针角 θm", "minute hand θm"], api.fmt(am, 1) + "°"],
            [["两针相差", "angle between"], api.fmt(diff, 1) + "°"]];
  },
  draw(api, s) {
    const { w, h } = api, c = api.ctx;
    // 右侧：构型空间正方形
    const S = Math.min(w * 0.42, h * 0.8), x0 = w * 0.54, y0 = (h - S) / 2;
    const P = (a, b) => [x0 + (a + 180) / 360 * S, y0 + S - (b + 180) / 360 * S];
    api.rect(x0, y0, S, S, api.css("--panel"), api.css("--ink"));
    api.line(x0, y0, x0, y0 + S, api.css("--red"), 3); api.line(x0 + S, y0, x0 + S, y0 + S, api.css("--red"), 3);
    api.line(x0, y0, x0 + S, y0, api.css("--blue"), 3); api.line(x0, y0 + S, x0 + S, y0 + S, api.css("--blue"), 3);
    api.label("−180°", x0, y0 + S + 12, api.css("--muted"), 11, "center"); api.label("180°", x0 + S, y0 + S + 12, api.css("--muted"), 11, "center");
    if (api.scene === "arm") {
      api.label("θ₁", x0 + S / 2, y0 + S + 14, api.css("--ink"), 13, "center"); api.label("θ₂", x0 - 14, y0 + S / 2, api.css("--ink"), 13, "center");
      c.fillStyle = api.css("--muted");
      const cs = S / 180;
      this.grid().forEach(([i, j]) => c.fillRect(x0 + i * cs, y0 + S - (j + 1) * cs, cs + 0.5, cs + 0.5));
      const d = Math.PI / 180, t1 = api.p.t1 * d, t2 = api.p.t2 * d, hit = this.hit(t1, t2);
      const q = P(api.p.t1, api.p.t2);
      api.circle(q[0], q[1], 6, hit ? api.css("--red") : api.css("--amber"), api.css("--ink"));
      // 左侧：手臂
      const k = Math.min(w * 0.24, h * 0.5), bx = w * 0.26, by = h * 0.55;
      const X = (p) => [bx + k * p[0], by - k * p[1]];
      const o = X(this.OC);
      api.circle(o[0], o[1], k * this.OR, api.css("--grid"), api.css("--ink"));
      const tg = X(this.TGT);
      api.circle(tg[0], tg[1], 8, null, api.css("--green")); api.circle(tg[0], tg[1], 3, api.css("--green"));
      c.setLineDash([4, 4]); c.strokeStyle = api.css("--grid"); c.beginPath(); c.arc(bx, by, k * (this.L1 + this.L2), 0, 2 * Math.PI); c.stroke(); c.setLineDash([]);
      const [e, tip] = this.fk(t1, t2), b0 = X([0, 0]), b1 = X(e), b2 = X(tip), col = hit ? api.css("--red") : api.css("--blue");
      api.line(b0[0], b0[1], b1[0], b1[1], col, 9); api.line(b1[0], b1[1], b2[0], b2[1], col, 7);
      api.circle(b0[0], b0[1], 5, api.css("--panel"), api.css("--ink")); api.circle(b1[0], b1[1], 5, api.css("--panel"), api.css("--ink"));
      api.circle(b2[0], b2[1], 4, col);
      return;
    }
    // 钟表场景
    api.label(api.lang() === "en" ? "hour θh" : "时针 θh", x0 + S / 2, y0 + S + 14, api.css("--ink"), 13, "center");
    api.label(api.lang() === "en" ? "minute θm" : "分针 θm", x0 - 8, y0 - 10, api.css("--ink"), 13, "left");
    const Q = (a, b) => P(((a + 180) % 360) - 180, ((b + 180) % 360) - 180);
    c.strokeStyle = api.css("--amber"); c.lineWidth = 1.5;
    let prev = null;
    for (let i = 0; i <= 1440; i++) {
      const ah = i * 0.25, am = (12 * ah) % 360, p = Q(ah, am);
      if (prev && Math.abs(p[1] - prev[1]) < S / 2 && Math.abs(p[0] - prev[0]) < S / 2) { c.beginPath(); c.moveTo(prev[0], prev[1]); c.lineTo(p[0], p[1]); c.stroke(); }
      prev = p;
    }
    c.setLineDash([5, 5]); api.line(...P(-180, -180), ...P(180, 180), api.css("--muted"), 1); c.setLineDash([]);
    const [ah, am] = this.hands(api), q = Q(ah, am);
    api.circle(q[0], q[1], 6, api.css("--red"), api.css("--ink"));
    const R = Math.min(w * 0.2, h * 0.38), cx = w * 0.25, cy = h * 0.5;
    api.circle(cx, cy, R, api.css("--panel"), api.css("--ink"));
    for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; api.line(cx + 0.88 * R * Math.sin(a), cy - 0.88 * R * Math.cos(a), cx + R * Math.sin(a), cy - R * Math.cos(a), api.css("--ink"), 2); }
    const hd = ah * Math.PI / 180, md = am * Math.PI / 180;
    api.line(cx, cy, cx + 0.55 * R * Math.sin(hd), cy - 0.55 * R * Math.cos(hd), api.css("--ink"), 6);
    api.line(cx, cy, cx + 0.85 * R * Math.sin(md), cy - 0.85 * R * Math.cos(md), api.css("--blue"), 3);
    api.circle(cx, cy, 4, api.css("--ink"));
  },
});
