// 实验 16.1 示教器点动：空间雅可比与物体雅可比（配 16.1 节）。
// 机器人场景：零件库的 UR5e，起始关节角 θ* = (30°, −60°, 90°, −120°, −90°, 45°)（算例 16.1.1、16.1.2）。
// 旋量轴与零位位姿取表 12.1.1。J_s 的第 i 列 = 关节 i 此刻的旋量轴 (ω_i, −ω_i × q_i)（定理 16.1.1），
// J_b = [Ad_{T⁻¹}] J_s（定理 16.1.2）。三种点动指令，每个控制周期解一次线性方程组，用 RK4 积分 3 s：
//   0 示教器“基座”：(ω_s, ṗ) 给定，ω_s 与 ṗ 都沿 {s} 的轴，转动绕法兰盘中心：V_s = (ω_s, ṗ − ω_s × p)，θ̇ = J_s⁻¹ V_s；
//   1 示教器“工具”：V_b 给定（沿 {b} 的轴，转动绕法兰盘中心），θ̇ = J_b⁻¹ V_b；
//   2 直接给 V_s = (ω, v)：v 是与 {s} 原点重合的那一点的速度，“绕 z 转”就是绕基座轴线转。
// 生活场景：一台 20 吨级挖掘机（大臂 5.7 m、斗杆 2.9 m、铲斗 1.5 m，示意尺寸），“平整模式”让斗尖沿水平线移动：
//   控制器每个周期由斗尖的位置雅可比（2×2，大臂与斗杆）求关节速度，铲斗关节补偿使铲斗对地的角度不变；
//   “手柄模式”只推斗杆，斗尖走圆弧。
WQ.lab({
  title: ["实验 16.1 示教器点动：空间雅可比与物体雅可比", "Lab 16.1 Jogging from the teach pendant: space and body Jacobians"],
  goal: ["用三种坐标系点动 UR5e，看同一个“沿 x 移动”“绕 z 转动”在不同坐标系中是什么运动，控制器怎样用 J_s 或 J_b 把它变成六个关节的转速。",
         "Jog the UR5e in three frames, see what the same “move along x” or “turn about z” means in each, and how the controller turns it into six joint speeds with J_s or J_b."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 点动", "UR5e jogging"], hide: ["exspeed"],
      problem: { title: ["机器人问题：点动指令怎样变成关节转速", "Robot problem: how a jog command becomes joint speeds"],
                 text: ["选择坐标系和方向，按“开始”点动 3 s。黄线是法兰盘中心的轨迹。测量区给出六个关节的转速、法兰盘中心的位移和姿态的变化。",
                        "Choose the frame and direction and press “Start” to jog for 3 s. The yellow line traces the flange centre. The readouts show the six joint speeds, the flange-centre displacement and the change of orientation."] } },
    { id: "dig", name: ["挖掘机平整场地", "Excavator grading"], hide: ["dir", "wang", "vlin"],
      params: { mode: { min: 0, max: 1, value: 1 } },
      problem: { title: ["生活中的例子：让斗尖贴着地面水平移动", "Everyday example: keep the bucket tip level along the ground"],
                 text: ["模式 0：只推斗杆手柄，斗尖走圆弧；模式 1：平整模式，控制器每个周期用雅可比矩阵算出大臂和斗杆的转速，斗尖沿水平线向机身收回。",
                        "Mode 0: push only the stick lever, the tip moves on an arc. Mode 1: grading mode, the controller uses the Jacobian every cycle to find the boom and stick speeds, and the tip moves level towards the machine."] } },
  ],
  params: [
    { id: "mode", name: ["坐标系：0 示教器基座 / 1 示教器工具 / 2 直接给 V_s", "frame: 0 pendant base / 1 pendant tool / 2 raw V_s"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "dir", name: ["方向：0 x / 1 y / 2 z / 3 绕 x / 4 绕 y / 5 绕 z", "direction: 0 x / 1 y / 2 z / 3 about x / 4 about y / 5 about z"], min: 0, max: 5, step: 1, value: 0, unit: "", digits: 0 },
    { id: "vlin", name: ["平移速度", "linear speed"], min: 10, max: 100, step: 5, value: 50, unit: "mm/s", digits: 0 },
    { id: "wang", name: ["转动速度", "angular speed"], min: 2, max: 30, step: 1, value: 10, unit: "°/s", digits: 0 },
    { id: "exspeed", name: ["斗尖速度", "bucket-tip speed"], min: 0.1, max: 0.6, step: 0.05, value: 0.3, unit: "m/s", digits: 2 },
  ],
  legend: [{ color: "#c98f00", name: ["法兰盘中心（斗尖）的轨迹", "trace of the flange centre (bucket tip)"] }],
  tasks: [
    { id: "basex", robot: true, text: ["示教器“基座”坐标系沿 x 点动：法兰盘中心走直线，姿态不变（偏离直线 < 0.1 mm，姿态变化 < 0.01°）。",
                                       "Pendant “base” frame, jog along x: the flange centre moves on a straight line and the orientation stays (off the line < 0.1 mm, orientation change < 0.01°)."],
      demo: { scene: "ur", set: { mode: 0, dir: 0, vlin: 50 }, press: ["start"], wait: 5 } },
    { id: "toolrot", robot: true, text: ["示教器“工具”坐标系绕 z 点动：法兰盘中心不动（< 0.1 mm），姿态转过 20° 以上。",
                                         "Pendant “tool” frame, turn about z: the flange centre stays put (< 0.1 mm) while the tool turns by more than 20°."],
      demo: { scene: "ur", set: { mode: 1, dir: 5, wang: 10 }, press: ["start"], wait: 5 } },
    { id: "wrong", robot: true, text: ["直接给 V_s = (0, 0, ω, 0, 0, 0)：只有关节 1 在转，法兰盘中心绕基座轴线走了 0.1 m 以上。",
                                       "Give V_s = (0, 0, ω, 0, 0, 0) directly: only joint 1 turns, and the flange centre travels more than 0.1 m about the base axis."],
      demo: { scene: "ur", set: { mode: 2, dir: 5, wang: 10 }, press: ["start"], wait: 5 } },
    { id: "only6", robot: true, text: ["找出一个只需要关节 6 转动的工具坐标系点动方向。", "Find a tool-frame jog direction that needs joint 6 only."],
      demo: { scene: "ur", set: { mode: 1, dir: 4, wang: 10 }, press: ["start"], wait: 5 } },
    { id: "dig", text: ["生活场景：用平整模式让斗尖水平收回 1.5 m 以上，高度偏差小于 1 cm。", "Everyday scene: in grading mode bring the tip back level by more than 1.5 m with a height error below 1 cm."],
      demo: { scene: "dig", set: { mode: 1, exspeed: 0.3 }, press: ["start"], wait: 8 } },
  ],
  think: ["示教器“基座”坐标系的转动绕的是法兰盘中心，而 V_s = (ω, 0) 绕的是 {s} 的原点。两者的 V_s 差多少？为什么任务 3 只有关节 1 在转，而任务 4 只有关节 6 在转？",
          "A pendant “base” rotation turns about the flange centre, whereas V_s = (ω, 0) turns about the origin of {s}. How do the two V_s differ? Why does only joint 1 turn in task 3, and only joint 6 in task 4?"],

  // ---------------- UR5e 几何（表 12.1.1）与 SE(3) 运算（同实验 15.1）
  G: { H1: 0.163, W1: 0.138, L1: 0.425, W2: 0.131, L2: 0.392, W3: 0.127, H2: 0.1, W4: 0.1 },
  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  START: [30, -60, 90, -120, -90, 45],
  DUR: 3.0, DT: 0.004,
  dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  add(a, b) { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; },
  sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; },
  mul(a, s) { return [a[0] * s, a[1] * s, a[2] * s]; },
  norm(a) { return Math.hypot(a[0], a[1], a[2]); },
  mv(R, v) { return [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]); },
  mm(A, B) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j])); },
  tr(A) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[j][i])); },
  rot(w, t) {
    const c = Math.cos(t), s = Math.sin(t), v = 1 - c, [x, y, z] = w;
    return [[c + x * x * v, x * y * v - z * s, x * z * v + y * s], [y * x * v + z * s, c + y * y * v, y * z * v - x * s], [z * x * v - y * s, z * y * v + x * s, c + z * z * v]];
  },
  AX() {
    const g = this.G, Y = [0, -1, 0];
    return [[[0, 0, 1], [0, 0, g.H1]], [Y, [0, -g.W1, g.H1]], [Y, [-g.L1, -g.W1 + g.W2, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2, g.H1]],
            [[0, 0, -1], [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1 - g.H2]]];
  },
  M() { const g = this.G; return { R: [[1, 0, 0], [0, -1, 0], [0, 0, -1]], p: [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3 - g.W4, g.H1 - g.H2] }; },
  E(i, t) { const [w, q] = this.AX()[i], R = this.rot(w, t); return { R, p: this.sub(q, this.mv(R, q)) }; },
  comp(A, B) { return { R: this.mm(A.R, B.R), p: this.add(this.mv(A.R, B.p), A.p) }; },
  act(A, x) { return this.add(this.mv(A.R, x), A.p); },
  fk(th) { let T = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] }; th.forEach((t, i) => { T = this.comp(T, this.E(i, t)); }); return this.comp(T, this.M()); },
  js(th) {                                        // 空间雅可比的六列：(ω_i, −ω_i × q_i)，ω_i、q_i 为此刻的轴（定理 16.1.1）
    const A = this.AX(), cols = [];
    let P = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] };
    for (let i = 0; i < 6; i++) {
      const w = this.mv(P.R, A[i][0]), q = this.act(P, A[i][1]);
      cols.push([...w, ...this.mul(this.cross(w, q), -1)]);
      P = this.comp(P, this.E(i, th[i]));
    }
    return cols;
  },
  jb(th, cols) {                                  // J_b = [Ad_{T⁻¹}] J_s：ω_b = Rᵀω_s，v_b = Rᵀ(v_s − p × ω_s)
    const T = this.fk(th), Rt = this.tr(T.R);
    return cols.map((c) => { const w = c.slice(0, 3), v = c.slice(3); return [...this.mv(Rt, w), ...this.mv(Rt, this.sub(v, this.cross(T.p, w)))]; });
  },
  solve(cols, b) {                                // 解 J x = b，J 按列给出；列主元高斯消去
    const n = b.length, M = [];
    for (let r = 0; r < n; r++) M.push([...cols.map((c) => c[r]), b[r]]);
    for (let i = 0; i < n; i++) {
      let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(M[j][i]) > Math.abs(M[p][i])) p = j;
      [M[i], M[p]] = [M[p], M[i]];
      for (let j = i + 1; j < n; j++) { const f = M[j][i] / M[i][i]; for (let k = i; k <= n; k++) M[j][k] -= f * M[i][k]; }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let s = M[i][n]; for (let k = i + 1; k < n; k++) s -= M[i][k] * x[k]; x[i] = s / M[i][i]; }
    return x;
  },
  cmd(api) {                                      // 指令：六维矢量，前三个是角速度（rad/s），后三个是线速度（m/s）
    const d = api.p.dir, e = [[1, 0, 0], [0, 1, 0], [0, 0, 1]][d % 3];
    const w = d >= 3 ? this.mul(e, api.p.wang * Math.PI / 180) : [0, 0, 0], v = d < 3 ? this.mul(e, api.p.vlin / 1000) : [0, 0, 0];
    return { w, v };
  },
  rate(api, th) {
    const c = this.cmd(api), Js = this.js(th), m = api.p.mode;
    if (m === 1) return this.solve(this.jb(th, Js), [...c.w, ...c.v]);
    if (m === 0) { const p = this.fk(th).p; return this.solve(Js, [...c.w, ...this.sub(c.v, this.cross(c.w, p))]); }
    return this.solve(Js, [...c.w, ...c.v]);
  },
  // ---------------- 挖掘机：在回转平面内，大臂角 a1（对水平，向上为正）、斗杆相对角 a2、铲斗相对角 a3
  X: { foot: [0.6, 2.0], L: [5.7, 2.9, 1.5] },
  xfk(a) {
    const [l1, l2, l3] = this.X.L, f = this.X.foot, s1 = a[0], s2 = a[0] + a[1], s3 = s2 + a[2];
    const e = [f[0] + l1 * Math.cos(s1), f[1] + l1 * Math.sin(s1)], w = [e[0] + l2 * Math.cos(s2), e[1] + l2 * Math.sin(s2)];
    return { f, e, w, t: [w[0] + l3 * Math.cos(s3), w[1] + l3 * Math.sin(s3)], s3 };
  },
  xrate(api, a) {
    const v = -api.p.exspeed;                     // 斗尖向机身方向（−x）水平移动
    if (api.p.mode === 0) return [0, 0.25, 0];   // 手柄模式：只推斗杆，0.25 rad/s
    const [l1, l2, l3] = this.X.L, s1 = a[0], s2 = a[0] + a[1], s3 = s2 + a[2];
    // 铲斗对地角 s3 保持不变：ȧ3 = −(ȧ1 + ȧ2)。斗尖速度只由大臂、斗杆决定：J = ∂(x, y)/∂(a1, a2)（铲斗段随 s3 平移）
    const J = [[-l1 * Math.sin(s1) - l2 * Math.sin(s2), -l2 * Math.sin(s2)], [l1 * Math.cos(s1) + l2 * Math.cos(s2), l2 * Math.cos(s2)]];
    const det = J[0][0] * J[1][1] - J[0][1] * J[1][0], b = [v, 0];
    const d1 = (J[1][1] * b[0] - J[0][1] * b[1]) / det, d2 = (-J[1][0] * b[0] + J[0][0] * b[1]) / det;
    return [d1, d2, -(d1 + d2)];
  },

  reset(api, s) {
    s.t = 0; s.clock = 0; s.done = false;
    s.th = this.START.map((d) => d * Math.PI / 180);
    s.a = [0.18, -1.75, -1.2];
    const T0 = this.fk(s.th);
    s.T0 = T0; s.p0 = T0.p; s.peak = [0, 0, 0, 0, 0, 0]; s.dev = 0; s.dmax = 0; s.ang = 0; s.qd = [0, 0, 0, 0, 0, 0];
    s.x0 = this.xfk(s.a).t; s.hdev = 0; s.travel = 0;
    s.trace = [api.scene === "ur" ? T0.p : this.xpt(s.x0)];
  },
  xpt(t2) { return [1.5 + t2[0], 6.0, t2[1]]; },     // 挖掘机在 {s} 中的位置：回转中心 (1.5, 6, 0)，回转平面平行于 xz 平面
  step(api, s) {
    const h = this.DT;
    if (api.scene === "ur") {
      const f = (q) => this.rate(api, q), k1 = f(s.th);
      const k2 = f(s.th.map((x, i) => x + h / 2 * k1[i])), k3 = f(s.th.map((x, i) => x + h / 2 * k2[i])), k4 = f(s.th.map((x, i) => x + h * k3[i]));
      s.qd = k1;
      s.th = s.th.map((x, i) => x + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
      k1.forEach((v, i) => { s.peak[i] = Math.max(s.peak[i], Math.abs(v)); });
      const T = this.fk(s.th), dp = this.sub(T.p, s.p0), c = this.cmd(api);
      s.dmax = Math.max(s.dmax, this.norm(dp));
      const R = this.mm(this.tr(s.T0.R), T.R); s.ang = Math.acos(Math.max(-1, Math.min(1, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)));
      if (api.p.mode === 0 && api.p.dir < 3) { const u = this.mul(c.v, 1 / this.norm(c.v)); s.dev = Math.max(s.dev, this.norm(this.sub(dp, this.mul(u, this.dot(dp, u))))); }
      if (s.trace.length < 2000) s.trace.push(T.p);
    } else {
      const d = this.xrate(api, s.a);
      s.a = s.a.map((x, i) => x + d[i] * h);
      const t2 = this.xfk(s.a).t;
      s.hdev = Math.max(s.hdev, Math.abs(t2[1] - s.x0[1])); s.travel = s.x0[0] - t2[0];
      if (s.trace.length < 2000 && Math.round(s.t / h) % 5 === 0) s.trace.push(this.xpt(t2));
    }
    s.t += h;
    const dur = api.scene === "ur" ? this.DUR : 6.0;
    if (s.t >= dur - 1e-9) s.done = true;
  },
  // 按“开始”时一次算完整段运动（结果用于检查任务），画面再按时间回放，这样回放快慢不影响结果
  start(api, s) {
    const r = Object.assign({}, s, { th: s.th && s.th.slice(), a: s.a && s.a.slice(), trace: s.trace.slice() }), snaps = [];
    let k = 0;
    while (!r.done) {
      this.step(api, r);
      if (k++ % 5 === 0 || r.done) snaps.push(Object.assign({}, r, { th: r.th && r.th.slice(), a: r.a && r.a.slice(), qd: r.qd && r.qd.slice(),
        peak: r.peak && r.peak.slice(), e: r.e && r.e.slice(), ed: r.ed && r.ed.slice(), rd: r.rd && r.rd.slice(), r: r.r && r.r.slice(), trace: null, n: r.trace.length }));
    }
    s.snaps = snaps; s.fullTrace = r.trace; s.final = r; s.clock = 0;
  },
  update(dt, api, s) {
    if (!s.snaps) return;
    s.clock += dt;
    const keep = { snaps: s.snaps, fullTrace: s.fullTrace, final: s.final, clock: s.clock };
    const i = Math.min(s.snaps.length - 1, Math.floor(s.clock / s.final.t * (s.snaps.length - 1)));
    Object.assign(s, s.snaps[i], keep, { trace: s.fullTrace.slice(0, s.snaps[i].n) });
    if (i === s.snaps.length - 1) { s.done = true; api.stop(); }
  },
  readouts(api, s) {
    const dg = (x) => (x * 180 / Math.PI).toFixed(2);
    if (api.scene === "dig") {
      const F = s.final;
      if (F && F.done && api.p.mode === 1 && F.travel > 1.5 && F.hdev < 0.01) api.done("dig");
      return [[["模式", "mode"], api.p.mode === 1 ? api.T("平整模式（雅可比）", "grading (Jacobian)") : api.T("只推斗杆", "stick lever only")],
              [["时间", "time"], s.t.toFixed(2) + " s"], [["斗尖水平收回", "tip drawn in"], s.travel.toFixed(3) + " m"],
              [["斗尖高度的最大偏差", "largest height error of the tip"], (s.hdev * 100).toFixed(2) + " cm"],
              [["大臂、斗杆、铲斗角", "boom, stick, bucket angles"], s.a.map((x) => dg(x) + "°").join(", ")],
              [["状态", "status"], s.done ? api.T("结束", "finished") : api.running ? api.T("运动中", "moving") : "—"]];
    }
    const F = s.final;
    if (F && F.done) {
      const m = api.p.mode, d = api.p.dir, others = Math.max(...F.peak.slice(1)), notsix = Math.max(...F.peak.slice(0, 5));
      if (m === 0 && d === 0 && F.dmax > 0.1 && F.dev < 1e-4 && F.ang * 180 / Math.PI < 0.01) api.done("basex");
      if (m === 1 && d === 5 && F.dmax < 1e-4 && F.ang * 180 / Math.PI > 20) api.done("toolrot");
      if (m === 2 && d === 5 && others < 1e-9 && F.dmax > 0.1) api.done("wrong");
      if (m === 1 && notsix < 1e-9 && F.peak[5] > 1e-3) api.done("only6");
    }
    const frames = [api.T("示教器基座", "pendant base"), api.T("示教器工具", "pendant tool"), api.T("直接给 V_s", "raw V_s")];
    return [[["坐标系", "frame"], frames[api.p.mode]], [["时间", "time"], s.t.toFixed(2) + " s"],
            [["θ̇₁…θ̇₃ / (°/s)", "θ̇₁…θ̇₃ / (°/s)"], s.qd.slice(0, 3).map(dg).join(", ")],
            [["θ̇₄…θ̇₆ / (°/s)", "θ̇₄…θ̇₆ / (°/s)"], s.qd.slice(3).map(dg).join(", ")],
            [["法兰盘中心的最大位移", "largest flange-centre displacement"], (s.dmax * 1000).toFixed(2) + " mm"],
            [["偏离直线（平移点动）", "off the line (linear jog)"], (s.dev * 1000).toFixed(4) + " mm"],
            [["姿态转过的角度", "orientation change"], (s.ang * 180 / Math.PI).toFixed(3) + "°"],
            [["状态", "status"], s.done ? api.T("结束", "finished") : api.running ? api.T("点动中", "jogging") : "—"]];
  },

  // ---------------- 三维
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    arm.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    const g = new T.BufferGeometry(); g.setAttribute("position", new T.BufferAttribute(new Float32Array(2000 * 3), 3)); g.setDrawRange(0, 0);
    keep.trace = new T.Line(g, new T.LineBasicMaterial({ color: 0xc98f00 })); keep.trace.frustumCulled = false; G.add(keep.trace);
    keep.axes = new T.AxesHelper(0.15); G.add(keep.axes);
    // 挖掘机：履带、回转平台、驾驶室，以及大臂、斗杆、铲斗三段（在回转平面内转动）
    const mat = (c) => new T.MeshStandardMaterial({ color: c }), X = new T.Group(); X.position.set(1.5, 6.0, 0); G.add(X); keep.X = X;
    [-1.2, 1.2].forEach((y) => { const tr = new T.Mesh(new T.BoxGeometry(4.4, 0.6, 0.9), mat(0x30363d)); tr.position.set(-0.6, y, 0.45); X.add(tr); });
    const deck = new T.Mesh(new T.BoxGeometry(3.6, 2.6, 0.9), mat(0xe0a400)); deck.position.set(-1.4, 0, 1.4); X.add(deck);
    const cab = new T.Mesh(new T.BoxGeometry(1.2, 1.0, 1.4), mat(0xd29922)); cab.position.set(-0.2, 0.75, 2.5); X.add(cab);
    keep.links = [0, 1, 2].map((k) => { const m = new T.Mesh(new T.BoxGeometry(1, k === 2 ? 0.7 : 0.45, k === 2 ? 0.5 : 0.4), mat(k === 2 ? 0x6e7681 : 0xe0a400)); X.add(m); return m; });
    const ground = new T.Mesh(new T.BoxGeometry(14, 6, 0.02), new T.MeshStandardMaterial({ color: 0xb8a27a, transparent: true, opacity: 0.45 })); ground.position.set(3.0, 0, -0.01); X.add(ground); keep.ground = ground;
    keep.box = () => { G.updateMatrixWorld(true); const b = new T.Box3().setFromObject(X); return b.expandByScalar(0.3); };
    api.m.excView = { entry: { robot: {} }, holder: { visible: false }, box: () => keep.box() };
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep, ur = api.scene === "ur";
    if (!k.G) return;
    k.X.visible = !ur; k.axes.visible = ur;
    if (k.shown !== api.scene) {
      k.shown = api.scene; arm.holder.visible = true;
      if (ur) api.view(35, 25, 0.6, arm); else api.view(10, 12, 0.9, api.m.excView);
    }
    arm.holder.visible = ur;
    if (ur) { const o = {}; this.J.forEach((n, i) => { o[n] = s.th[i]; }); arm.set(o); }
    else {
      const P = this.xfk(s.a), pts = [P.f, P.e, P.w, P.t];
      for (let i = 0; i < 3; i++) {
        const a = pts[i], b = pts[i + 1], m = k.links[i], L = Math.hypot(b[0] - a[0], b[1] - a[1]);
        m.scale.set(L, 1, 1); m.position.set((a[0] + b[0]) / 2, 0, (a[1] + b[1]) / 2); m.rotation.set(0, -Math.atan2(b[1] - a[1], b[0] - a[0]), 0);
      }
    }
    const a = k.trace.geometry.attributes.position, pts = s.trace.slice(-2000);
    pts.forEach((p, i) => a.setXYZ(i, p[0], p[1], p[2])); a.needsUpdate = true; k.trace.geometry.setDrawRange(0, pts.length);
  },
});
