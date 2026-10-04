// 实验 6.8 两连杆机械臂的雅可比行列式（配 6.8.4 节）。UR5e 的上臂 0.425 m、前臂 0.392 m（零件库 2026.10.9 版关节表）。
// J 的两列是两个关节分别以 1 rad/s 转动时末端的速度；关节角速度取遍单位圆时，末端速度画出一个椭圆，面积为 π|det J|。
WQ.lab({
  title: ["实验 6.8 两连杆机械臂的雅可比行列式", "Lab 6.8 The Jacobian determinant of a two-link arm"],
  goal: ["拖动两个关节角，看雅可比矩阵的两列、速度椭圆和 det J；找出最灵活的位形和奇异位形，观察 det J 变号时经过零。",
         "Drag the two joint angles; watch the columns of the Jacobian, the velocity ellipse and det J; find the most dexterous and the singular configurations, and see det J pass through zero as it changes sign."],
  scenes: [
    { id: "arm", robot: true, name: ["UR5e 肩、肘关节", "UR5e shoulder and elbow"],
      problem: { title: ["机器人问题：手臂伸直时会怎样？", "Robot problem: what happens when the arm straightens?"],
                 text: ["末端速度 v = J θ̇。det J = 0 时，有一个方向上的速度无论关节怎样转都产生不出来。找出这样的位形。",
                        "The tool velocity is v = J θ̇. When det J = 0 some direction of motion cannot be produced by any joint speeds. Find such configurations."] } },
  ],
  params: [
    { id: "t1", name: ["肩关节角 θ₁", "Shoulder angle θ₁"], min: -90, max: 180, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "t2", name: ["肘关节角 θ₂", "Elbow angle θ₂"], min: -180, max: 180, step: 1, value: 20, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "max", robot: true, text: ["找出 det J 最大的肘关节角，读出最大值，与 l₁l₂ 比较。", "Find the elbow angle with the largest det J; compare the maximum with l₁l₂."],
      demo: { scene: "arm", set: { t1: 30, t2: 90 }, press: [] } },
    { id: "near", robot: true, text: ["让手臂接近伸直，使 |det J| 小于最大值的 2%，观察 J 的两列。", "Nearly straighten the arm so that |det J| is below 2% of its maximum; look at the columns of J."],
      demo: { scene: "arm", set: { t1: 30, t2: 1 }, press: [] } },
    { id: "sign", robot: true, text: ["把肘关节从 20° 慢慢转到 −20°（都在 θ₂ = 0 附近），看 det J 怎样经过零并变号。", "Turn the elbow slowly from 20° to −20° (close to θ₂ = 0) and watch det J pass through zero and change sign."],
      demo: { scene: "arm", set: { t1: 30, t2: -10 }, press: [] } },
  ],
  think: ["det J 与肩关节角 θ₁ 无关，为什么？θ₂ = 180° 时手臂完全折叠，末端在哪里？此时哪个方向动不了？",
          "Why is det J independent of the shoulder angle θ₁? At θ₂ = 180° the arm folds back; where is the tool and which direction is lost?"],

  l1: 0.425, l2: 0.392,
  J(api) {
    const t1 = api.p.t1 * Math.PI / 180, t12 = t1 + api.p.t2 * Math.PI / 180, l1 = this.l1, l2 = this.l2;
    return [[-l1 * Math.sin(t1) - l2 * Math.sin(t12), -l2 * Math.sin(t12)], [l1 * Math.cos(t1) + l2 * Math.cos(t12), l2 * Math.cos(t12)]];
  },
  readouts(api, s) {
    const J = this.J(api), d = J[0][0] * J[1][1] - J[0][1] * J[1][0], dmax = this.l1 * this.l2;
    if (d > 0.9999 * dmax) api.done("max");
    if (Math.abs(d) < 0.02 * dmax && Math.abs(api.p.t2) < 90) api.done("near");
    if (!this.mem) this.mem = {};
    const t2 = api.p.t2;   // both sides of θ₂ = 0, close to it (|θ₂| ≤ 30°)
    if (t2 > 0 && t2 <= 30) this.mem.pos = true;
    if (t2 < 0 && t2 >= -30) this.mem.neg = true;
    if (this.mem.pos && this.mem.neg) api.done("sign");
    const ang = Math.abs(Math.atan2(J[0][0] * J[1][1] - J[1][0] * J[0][1], J[0][0] * J[0][1] + J[1][0] * J[1][1])) * 180 / Math.PI;
    return [[["雅可比矩阵 J（m/rad）", "Jacobian J (m/rad)"], api.la.str(J, 3)],
            [["det J（m²）", "det J (m²)"], api.fmt(d, 4)],
            [["l₁l₂ sin θ₂", "l₁l₂ sin θ₂"], api.fmt(dmax * Math.sin(api.p.t2 * Math.PI / 180), 4)],
            [["det J / 最大值 l₁l₂", "det J / max l₁l₂"], api.fmt(100 * d / dmax, 1) + "%"],
            [["两列的夹角", "Angle between the columns"], api.fmt(ang, 1) + "°"],
            [["速度椭圆面积 π|det J|", "Ellipse area π|det J|"], api.fmt(Math.PI * Math.abs(d), 4) + " m²/s²"]];
  },
  draw(api) {
    const { w, h } = api, J = this.J(api), red = api.css("--red"), green = api.css("--green"), muted = api.css("--muted");
    const k = Math.min(w * 0.55, h) * 0.55, ox = w * 0.36, oy = h * 0.62, X = (x, y) => [ox + k * x, oy - k * y];
    const t1 = api.p.t1 * Math.PI / 180, t12 = t1 + api.p.t2 * Math.PI / 180;
    const j = [this.l1 * Math.cos(t1), this.l1 * Math.sin(t1)], p = [j[0] + this.l2 * Math.cos(t12), j[1] + this.l2 * Math.sin(t12)];
    api.line(...X(-0.9, 0), ...X(0.9, 0), muted, 1);
    const g = api.ctx; g.beginPath();
    for (let i = 0; i <= 120; i++) { const a = i * Math.PI / 60, q = X(0.817 * Math.cos(a), 0.817 * Math.sin(a)); if (i) g.lineTo(...q); else g.moveTo(...q); }
    g.strokeStyle = api.css("--grid"); g.setLineDash([4, 4]); g.lineWidth = 1; g.stroke(); g.setLineDash([]);
    api.line(...X(0, 0), ...X(...j), api.css("--blue"), 10); api.line(...X(...j), ...X(...p), api.css("--blue"), 8);
    api.circle(...X(0, 0), 7, api.css("--panel"), api.css("--ink")); api.circle(...X(...j), 6, api.css("--panel"), api.css("--ink"));
    const e = 0.5, pts = [];
    for (let i = 0; i <= 120; i++) { const a = i * Math.PI / 60, v = api.la.mv(J, [Math.cos(a), Math.sin(a)]); pts.push(X(p[0] + e * v[0], p[1] + e * v[1])); }
    g.beginPath(); pts.forEach((q, i) => (i ? g.lineTo(...q) : g.moveTo(...q))); g.closePath();
    g.fillStyle = "rgba(201,143,0,0.25)"; g.fill(); g.strokeStyle = api.css("--amber"); g.lineWidth = 2; g.stroke();
    api.arrow(...X(...p), ...X(p[0] + e * J[0][0], p[1] + e * J[1][0]), red, 3);
    api.arrow(...X(...p), ...X(p[0] + e * J[0][1], p[1] + e * J[1][1]), green, 3);
    api.label(api.T("红：肩关节 1 rad/s 时末端速度；绿：肘关节", "red: tool velocity for 1 rad/s at the shoulder; green: elbow"), 10, 18, muted, 12);
    api.label(api.T("虚线：工作空间外边界（伸直）；黄：速度椭圆（0.5 m 代表 1 m/s）", "dashed: outer workspace (straight arm); yellow: velocity ellipse (0.5 m ≙ 1 m/s)"), 10, 36, muted, 12);
    // det J against θ₂, current point marked
    const gx = w * 0.72, gw = w * 0.25, gy = h * 0.3, gh = h * 0.45, dmax = this.l1 * this.l2;
    api.rect(gx, gy, gw, gh, null, api.css("--grid")); api.line(gx, gy + gh / 2, gx + gw, gy + gh / 2, muted, 1);
    g.beginPath();
    for (let i = 0; i <= 72; i++) { const th = -180 + 5 * i, x = gx + gw * i / 72, y = gy + gh / 2 - gh * 0.45 * Math.sin(th * Math.PI / 180); if (i) g.lineTo(x, y); else g.moveTo(x, y); }
    g.strokeStyle = api.css("--blue"); g.lineWidth = 2; g.stroke();
    const d = J[0][0] * J[1][1] - J[0][1] * J[1][0];
    api.circle(gx + gw * (api.p.t2 + 180) / 360, gy + gh / 2 - gh * 0.45 * d / dmax, 5, red, null);
    api.label("det J", gx, gy - 8, muted, 12); api.label("θ₂: −180° … 180°", gx + gw, gy + gh + 16, muted, 11, "right");
  },
});
