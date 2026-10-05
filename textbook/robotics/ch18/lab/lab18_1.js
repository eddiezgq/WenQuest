// 实验 18.1 串联与并联：工作空间与误差（配 18.1 节）。
// 机器人场景：左边 2R 串联臂（基座在原点，大臂 0.20 m、小臂 0.30 m，取 θ₂ > 0 的解）；
//   右边平面五杆机器人（电机在 (∓0.15, 0) m，主动杆 0.20 m、从动杆 0.30 m，肘部朝外：左支链 σ = +1，右支链 σ = −1，式 (18.1.3)）。
//   五杆的速度关系 A ẋ = B θ̇（式 (18.1.5)），J = A⁻¹B；2R 臂的 J 见 14.2、16.1 节。
//   编码器误差 ±0.01°：末端误差取误差矩形四个角点的最大值（算例 18.1.3）。误差椭圆：单位电机转速经 J 映射，图上 1 m/s 画成 0.3 m。
//   五杆的正解取 E₁ → E₂ 连线左侧（上方）的交点，与逆解核对，确认在同一装配模式中。
// 生活场景：墙上的绳吊笔（拉线绘图仪）。两个滑轮在 (∓0.6, 0.5) m，绳长 ρᵢ = |P − Cᵢ|（逆解）；
//   正解：两圆求交，取下方的点（笔挂在滑轮下方，靠重力拉直绳子）。“运行”画一个圆心 (0, 0)、半径 0.15 m 的圆。
WQ.lab({
  title: ["实验 18.1 串联与并联：工作空间与误差", "Lab 18.1 Serial versus parallel: workspace and error"],
  goal: ["用同样长的杆搭成 2R 串联臂和平面五杆机器人，比较它们能到达的范围、到达同一点时电机误差引起的末端误差和速度椭圆。",
         "Build a 2R serial arm and a planar five-bar from the same links; compare where they can reach and, at a common point, the end-point error caused by motor errors and the velocity ellipses."],
  scenes: [
    { id: "cmp", robot: true, name: ["2R 臂与五杆", "2R arm and five-bar"],
      problem: { title: ["机器人问题：同样的杆，串起来还是并起来", "Robot problem: the same links, in series or in parallel"],
                 text: ["用滑块给出目标点，左边的 2R 臂和右边的五杆同时去够。浅色是工作空间：左边是圆环（“和”），右边是两个圆环的交。椭圆是单位电机转速对应的末端速度，也是误差放大的样子。",
                        "Set the target with the sliders; the 2R arm (left) and the five-bar (right) both reach for it. Shaded: the workspaces, a ring on the left (a sum) and the intersection of two rings on the right. The ellipses are the end-point velocities for unit motor speeds, which is also how errors are magnified."] } },
    { id: "pen", name: ["墙上的绳吊笔", "A pen hung by two cords"], hide: [],
      params: { x: { min: -0.45, max: 0.45, step: 0.01, value: 0.0 }, y: { min: -0.45, max: 0.35, step: 0.01, value: 0.0 } },
      problem: { title: ["生活中的例子：两根绳子吊着一支笔", "Everyday example: a pen hung from two cords"],
                 text: ["墙上方两个滑轮各收放一根绳子，绳子的下端系在同一支笔上。给出笔的位置，界面算出两根绳长（逆解），再由绳长两圆求交得到笔的位置（正解）。按“运行”，笔画一个圆。",
                        "Two pulleys at the top of the wall each wind a cord tied to the same pen. Set the pen position: the two cord lengths follow (inverse kinematics), and two circles meeting give the pen back (forward kinematics). Press Run and the pen draws a circle."] } },
  ],
  params: [
    { id: "x", name: ["目标 x", "target x"], min: -0.6, max: 0.6, step: 0.01, value: 0.0, unit: "m", digits: 2 },
    { id: "y", name: ["目标 y", "target y"], min: -0.6, max: 0.6, step: 0.01, value: 0.35, unit: "m", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["运行", "Run"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 18.1.1 与 18.1.3：目标 (0, 0.35) m，读出两台机器人的关节角和 ±0.01° 引起的末端误差（约 0.108 mm 与 0.060 mm）。",
                                     "Examples 18.1.1 and 18.1.3: target (0, 0.35) m; read both sets of joint angles and the end errors from ±0.01° (about 0.108 mm and 0.060 mm)."],
      demo: { scene: "cmp", set: { x: 0.0, y: 0.35 }, press: [], wait: 1 } },
    { id: "only", robot: true, text: ["找一个 2R 臂能到、五杆到不了的点。", "Find a point the 2R arm reaches and the five-bar does not."],
      demo: { scene: "cmp", set: { x: 0.4, y: -0.1 }, press: [], wait: 1 } },
    { id: "half", robot: true, text: ["找一个两台机器人都能到、而五杆的末端误差不到 2R 臂一半的点。", "Find a point both reach where the five-bar's end error is less than half the 2R arm's."],
      demo: { scene: "cmp", set: { x: 0.0, y: 0.42 }, press: [], wait: 1 } },
    { id: "pen", text: ["生活场景：把笔移到 (0.20, 0.00) m，读出两根绳长（约 0.94 m 和 0.64 m）。", "Everyday scene: move the pen to (0.20, 0.00) m and read both cord lengths (about 0.94 m and 0.64 m)."],
      demo: { scene: "pen", set: { x: 0.2, y: 0.0 }, press: [], wait: 1 } },
    { id: "circle", text: ["生活场景：按“运行”，让笔画一个半径 0.15 m 的圆，观察两根绳长怎样变化。", "Everyday scene: press Run and let the pen draw a circle of radius 0.15 m; watch how the cord lengths change."],
      demo: { scene: "pen", set: { x: 0.0, y: 0.0 }, press: ["start"], wait: 8 } },
  ],
  think: ["五杆的误差椭圆普遍比 2R 臂的小，这对末端的最高速度意味着什么？Delta 为什么仍然比 UR5e 快？",
          "The five-bar's ellipses are generally smaller than the 2R arm's. What does that mean for its top speed? Why is a Delta still faster than a UR5e?"],

  // ---------------- 几何
  L1: 0.20, L2: 0.30, C: 0.15, EPS: 0.01 * Math.PI / 180, SC: 0.3,
  arm2(x, y) {
    const { L1, L2 } = this, c2 = (x * x + y * y - L1 * L1 - L2 * L2) / (2 * L1 * L2);
    if (Math.abs(c2) > 1) return null;
    const t2 = Math.acos(c2), t1 = Math.atan2(y, x) - Math.atan2(L2 * Math.sin(t2), L1 + L2 * Math.cos(t2));
    const s1 = Math.sin(t1), s12 = Math.sin(t1 + t2), c1 = Math.cos(t1), c12 = Math.cos(t1 + t2);
    return { th: [t1, t2], E: [L1 * c1, L1 * s1], J: [[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]] };
  },
  leg(x, y, ax, sg) {
    const dx = x - ax, dy = y, d = Math.hypot(dx, dy), c = (this.L1 * this.L1 + d * d - this.L2 * this.L2) / (2 * this.L1 * d);
    if (!(Math.abs(c) <= 1)) return null;
    return Math.atan2(dy, dx) + sg * Math.acos(c);
  },
  five(x, y) {
    const t1 = this.leg(x, y, -this.C, 1), t2 = this.leg(x, y, this.C, -1);
    if (t1 === null || t2 === null) return null;
    const B1 = [-this.C + this.L1 * Math.cos(t1), this.L1 * Math.sin(t1)], B2 = [this.C + this.L1 * Math.cos(t2), this.L1 * Math.sin(t2)];
    // 正解（两圆求交，取 E₁ → E₂ 左侧）应回到 (x, y)，否则这一点属于另一种装配模式
    const d = [B2[0] - B1[0], B2[1] - B1[1]], Ld = Math.hypot(...d);
    if (Ld > 2 * this.L2) return null;
    const hh = Math.sqrt(this.L2 * this.L2 - Ld * Ld / 4), n = [-d[1] / Ld, d[0] / Ld];
    const P = [(B1[0] + B2[0]) / 2 + hh * n[0], (B1[1] + B2[1]) / 2 + hh * n[1]];
    if (Math.hypot(P[0] - x, P[1] - y) > 1e-9) return null;
    const a1 = [x - B1[0], y - B1[1]], a2 = [x - B2[0], y - B2[1]];
    const A = [a1, a2], b1 = this.L1 * (-a1[0] * Math.sin(t1) + a1[1] * Math.cos(t1)), b2 = this.L1 * (-a2[0] * Math.sin(t2) + a2[1] * Math.cos(t2));
    const det = A[0][0] * A[1][1] - A[0][1] * A[1][0];
    if (Math.abs(det) < 1e-12) return null;
    const Ai = [[A[1][1] / det, -A[0][1] / det], [-A[1][0] / det, A[0][0] / det]];
    const J = [[Ai[0][0] * b1, Ai[0][1] * b2], [Ai[1][0] * b1, Ai[1][1] * b2]];
    return { th: [t1, t2], B1, B2, J };
  },
  err(J) { let m = 0; for (const a of [-1, 1]) for (const b of [-1, 1]) m = Math.max(m, Math.hypot(J[0][0] * a + J[0][1] * b, J[1][0] * a + J[1][1] * b) * this.EPS); return m; },
  lci(api, J) { const s = api.la.svd(J).s; return s[1] / s[0]; },
  // 绳吊笔
  PUL: [[-0.6, 0.5], [0.6, 0.5]],
  cords(x, y) { return this.PUL.map((c) => Math.hypot(x - c[0], y - c[1])); },
  penFK(r) {
    const [C1, C2] = this.PUL, d = C2[0] - C1[0], a = (r[0] * r[0] - r[1] * r[1] + d * d) / (2 * d), h2 = r[0] * r[0] - a * a;
    if (h2 < 0) return null;
    return [C1[0] + a, C1[1] - Math.sqrt(h2)];
  },
  penAt(api, s) {
    if (s.u != null) { const t = 2 * Math.PI * s.u; return [0.15 * Math.cos(t), 0.15 * Math.sin(t)]; }
    return [api.p.x, api.p.y];
  },

  reset(api, s) { s.u = null; s.trace = []; },
  start(api, s) { s.u = 0; s.trace = []; if (api.scene !== "pen") api.stop(); },
  update(dt, api, s) {
    if (api.scene !== "pen" || s.u == null) { api.stop(); return; }
    s.u = Math.min(1, s.u + dt / 5);
    s.trace.push(this.penAt(api, s));
    if (s.u >= 1) { api.stop(); api.done("circle"); }
  },
  readouts(api, s) {
    const f = (v, n) => api.fmt(v, n), d = (v) => (v * 180 / Math.PI).toFixed(2) + "°", x = api.p.x, y = api.p.y;
    const near = (a, b) => Math.abs(a - b) < 1e-9;
    if (api.scene === "pen") {
      const P = this.penAt(api, s), r = this.cords(...P), Q = this.penFK(r);
      if (!api.running && near(x, 0.2) && near(y, 0) && Q) api.done("pen");
      return [[["绳长 ρ₁、ρ₂（逆解）", "cord lengths ρ₁, ρ₂ (inverse)"], `${f(r[0], 4)} m, ${f(r[1], 4)} m`],
              [["由绳长求出的笔位置（正解）", "pen from the cords (forward)"], Q ? `(${f(Q[0], 4)}, ${f(Q[1], 4)}) m` : "—"],
              [["两者之差", "difference"], Q ? (Math.hypot(Q[0] - P[0], Q[1] - P[1]) * 1000).toExponential(1) + " mm" : "—"]];
    }
    const a = this.arm2(x, y), b = this.five(x, y), rows = [];
    rows.push([["2R 臂：θ₁, θ₂", "2R arm: θ₁, θ₂"], a ? `${d(a.th[0])}, ${d(a.th[1])}` : api.T("够不着", "out of reach")]);
    rows.push([["五杆：θ₁, θ₂", "five-bar: θ₁, θ₂"], b ? `${d(b.th[0])}, ${d(b.th[1])}` : api.T("够不着（或不在这一装配模式里）", "out of reach (or not in this assembly mode)")]);
    if (a) rows.push([["2R 臂：±0.01° 引起的末端误差", "2R arm: end error from ±0.01°"], f(this.err(a.J) * 1000, 4) + " mm"]);
    if (b) rows.push([["五杆：±0.01° 引起的末端误差", "five-bar: end error from ±0.01°"], f(this.err(b.J) * 1000, 4) + " mm"]);
    if (a) rows.push([["2R 臂：LCI", "2R arm: LCI"], f(this.lci(api, a.J), 3)]);
    if (b) rows.push([["五杆：LCI", "five-bar: LCI"], f(this.lci(api, b.J), 3)]);
    if (a && b) rows.push([["误差之比（五杆 / 2R）", "error ratio (five-bar / 2R)"], f(this.err(b.J) / this.err(a.J), 3)]);
    if (near(x, 0) && near(y, 0.35) && a && b) api.done("ex");
    const d1 = Math.hypot(x + this.C, y), d2 = Math.hypot(x - this.C, y);
    if (a && !b && (d1 > 0.5 + 1e-9 || d2 > 0.5 + 1e-9 || d1 < 0.1 - 1e-9 || d2 < 0.1 - 1e-9)) api.done("only");
    if (a && b && this.err(b.J) < 0.5 * this.err(a.J)) api.done("half");
    return rows;
  },
  draw(api, s) {
    const { w: W, h: H } = api, ctx = api.ctx, css = api.css;
    if (api.scene === "pen") {
      const sc = Math.min(W / 1.5, H / 1.3), ox = W / 2, oy = H * 0.56;
      const P = (x, y) => [ox + sc * x, oy - sc * y];
      api.rect(...P(-0.72, 0.62), sc * 1.44, sc * 1.12, css("--panel"), css("--grid"), 4);
      const pen = this.penAt(api, s);
      this.PUL.forEach((c) => { const q = P(...c); api.circle(q[0], q[1], 9, css("--muted"), css("--ink")); api.line(...q, ...P(...pen), css("--ink"), 2); });
      if (s.trace && s.trace.length > 1) { ctx.strokeStyle = css("--blue"); ctx.lineWidth = 2.5; ctx.beginPath(); s.trace.forEach((p, i) => { const q = P(...p); i ? ctx.lineTo(...q) : ctx.moveTo(...q); }); ctx.stroke(); }
      const q = P(...pen);
      api.rect(q[0] - 4, q[1] - 2, 8, 22, css("--accent"), css("--ink"), 2);
      const r = this.cords(...pen);
      api.label(`ρ₁ = ${api.fmt(r[0], 3)} m`, ...P(-0.58, 0.4), css("--ink"), 13);
      api.label(`ρ₂ = ${api.fmt(r[1], 3)} m`, ...P(0.32, 0.4), css("--ink"), 13);
      api.label(api.T("滑轮", "pulley"), ...P(-0.6, 0.58), css("--muted"), 12, "center");
      api.label(api.T("滑轮", "pulley"), ...P(0.6, 0.58), css("--muted"), 12, "center");
      return;
    }
    const sc = Math.min(W * 0.23, H * 0.44) / 0.62, oy = H * 0.56;
    const OL = [W * 0.25, oy], OR = [W * 0.75, oy];
    const PL = (x, y) => [OL[0] + sc * x, OL[1] - sc * y], PR = (x, y) => [OR[0] + sc * x, OR[1] - sc * y];
    const panel = css("--panel");
    // 2R：圆环
    ctx.globalAlpha = 0.35; api.circle(...OL, sc * 0.5, css("--blue")); ctx.globalAlpha = 1; api.circle(...OL, sc * 0.1, panel);
    api.circle(...OL, sc * 0.5, null, css("--blue")); api.circle(...OL, sc * 0.1, null, css("--blue"));
    // 五杆：两个圆环之交（外圆裁剪两次，再挖掉两个内圆）
    ctx.save();
    ctx.beginPath(); ctx.arc(...PR(-this.C, 0), sc * 0.5, 0, 2 * Math.PI); ctx.clip();
    ctx.beginPath(); ctx.arc(...PR(this.C, 0), sc * 0.5, 0, 2 * Math.PI); ctx.clip();
    ctx.globalAlpha = 0.35; ctx.fillStyle = css("--amber"); ctx.fillRect(0, 0, W, H); ctx.globalAlpha = 1;
    ctx.restore();
    [-this.C, this.C].forEach((cx) => { api.circle(...PR(cx, 0), sc * 0.1, panel); api.circle(...PR(cx, 0), sc * 0.5, null, css("--grid")); api.circle(...PR(cx, 0), sc * 0.1, null, css("--grid")); });
    api.label(api.T("2R 串联臂：工作空间是“和”", "2R serial arm: the workspace is a sum"), W * 0.25, 18, css("--blue"), 13, "center");
    api.label(api.T("五杆：工作空间是“交”", "five-bar: the workspace is an intersection"), W * 0.75, 18, css("--accent"), 13, "center");
    const x = api.p.x, y = api.p.y, a = this.arm2(x, y), b = this.five(x, y);
    const ell = (Pf, J, col) => {
      ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.beginPath();
      for (let k = 0; k <= 60; k++) { const t = 2 * Math.PI * k / 60, u = [Math.cos(t), Math.sin(t)];
        const v = [x + this.SC * (J[0][0] * u[0] + J[0][1] * u[1]), y + this.SC * (J[1][0] * u[0] + J[1][1] * u[1])], q = Pf(...v);
        k ? ctx.lineTo(...q) : ctx.moveTo(...q); }
      ctx.stroke();
    };
    if (a) {
      api.line(...PL(0, 0), ...PL(...a.E), css("--blue"), 7); api.line(...PL(...a.E), ...PL(x, y), css("--blue"), 5);
      api.circle(...PL(...a.E), 4, panel, css("--ink")); ell(PL, a.J, css("--blue"));
    }
    api.circle(...PL(0, 0), 6, css("--ink"));
    [-this.C, this.C].forEach((cx) => { const q = PR(cx, 0); api.rect(q[0] - 6, q[1] - 6, 12, 12, css("--ink")); });
    if (b) {
      [[-this.C, b.B1], [this.C, b.B2]].forEach(([cx, B]) => { api.line(...PR(cx, 0), ...PR(...B), css("--accent"), 7); api.line(...PR(...B), ...PR(x, y), css("--accent"), 4); api.circle(...PR(...B), 4, panel, css("--ink")); });
      ell(PR, b.J, css("--accent"));
    }
    [PL, PR].forEach((Pf) => { const q = Pf(x, y); api.line(q[0] - 8, q[1], q[0] + 8, q[1], css("--red"), 2); api.line(q[0], q[1] - 8, q[0], q[1] + 8, css("--red"), 2); });
    api.label(api.T("椭圆：单位电机转速的末端速度（1 m/s 画成 0.3 m）", "ellipse: end velocity for unit motor speeds (1 m/s drawn as 0.3 m)"), 12, H - 14, css("--muted"), 12);
  },
});
