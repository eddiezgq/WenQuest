// 实验 17.4 七轴 Panda 的协作搬运（配 17.4 节）。
// 机器人场景：零件库的 Panda（旋量轴见表 12.3.1）。手竖直向下（姿态同 ready），3 s 内从 A = (0.40, 0.35, 0.30) m 沿直线到
//   B = (0.40, −0.35, 0.30) m，位置按余弦规律过渡。工人的手（半径 0.06 m 的球）在前 1.8 s 从 (−0.45, 0.35, 0.60) m 伸到
//   (−0.05, 0.12, 0.60) m 后停住（算例 17.4.1）。
//   起始形态：页面载入后先由 ready 用牛顿法求 A 点的一个逆解，再沿 A 的自运动闭曲线追踪一整圈（广义叉积 + 中点预测 + 牛顿校正，
//   17.2.4 节）；θ₃ 沿这条闭曲线单调地转一圈（定理 17.4.1），所以用滑块给出 θ₃ 就确定了起始形态。
//   控制方式（积分步长 4 ms，K_p = 5 /s）：0 锁住关节 3（起始形态取 θ₃ = 0 的那一点，θ̇ = J₍₃₎⁻¹(𝒱 + K_p e)）；
//   1 最小范数解 θ̇ = J⁺(𝒱 + K_p e)；2 三层优先级（式 (17.4.1)：手 > 离开工人的手，激活距离 0.14 m、K_d = 3 /s、λ_o = 0.03 m > 避限位，k_H = 2）。
//   手臂用 17.2 节的连杆折线近似；距离为折线到球面的最短距离。关节速度上限 2.175（关节 1～4）、2.61 rad/s（关节 5～7）。
// 生活场景：人站在车外，伸手进车窗取副驾驶座上的包。肩 S = (−0.30, 0, 1.15) m、手 W = (0.20, 0.05, 0.98) m 固定，上臂、前臂各 0.30 m；
//   车窗在 x = 0 的竖直平面内，开口 y ∈ [−0.25, 0.25] m、z ∈ [1.00, 1.32] m。肘点在以 S、W 连线为轴的圆上，ψ 为摆角（ψ = 0 时肘朝下）。
//   手臂（看作半径 0.04 m 的圆柱）穿过窗口的那一点要离窗框至少 0.04 m。
WQ.lab({
  title: ["实验 17.4 七轴 Panda 的协作搬运", "Lab 17.4 Collaborative transfer with the seven-axis Panda"],
  goal: ["在协作工位上比较锁住一个关节、最小范数解和局部优先级控制，体会起始形态的选择：沿自运动闭曲线挑一个好的起点，比运动中拼命修正更有效。",
         "On a collaborative cell compare locking one joint, the minimum-norm solution and local priority control, and see what the choice of the start configuration does: picking a good start on the self-motion curve works better than desperate corrections during the motion."],
  view: "3d",
  models: ["B-ARM-PANDA"],
  scenes: [
    { id: "cell", robot: true, name: ["协作工位搬运", "Transfer on a collaborative cell"], hide: ["psi"],
      problem: { title: ["机器人问题：工人伸手进来时，手臂怎样既不碰人、又不耽误搬运？", "Robot problem: when the worker reaches in, how can the arm keep clear without spoiling the transfer?"],
                 text: ["用 θ₃ 滑块沿 A 点的自运动闭曲线选择起始形态（手在 A 不动），选择控制方式，按“开始”完成搬运。要求：手的路径不变；离工人的手（红球）至少 0.10 m；关节不超限；关节速度不超过上限。",
                        "Use the θ₃ slider to choose the start on the self-motion curve of A (the hand stays at A), choose the control and press “Start”. Requirements: the hand path is unchanged; at least 0.10 m from the worker's hand (red ball); joints within limits; joint speeds within their limits."] } },
    { id: "car", name: ["伸手进车窗取包", "Reaching through a car window"], hide: ["t3", "ctrl"],
      problem: { title: ["生活中的例子：手要到的地方定了，肘部从哪里进去？", "Everyday example: the hand's target is fixed; where should the elbow go?"],
                 text: ["肩和手的位置都不变，肘部只能绕肩到手的连线转动（摆角 ψ）。选一个 ψ，使手臂从窗口中间穿过，不碰窗框。",
                        "Shoulder and hand stay where they are; the elbow can only swing about the shoulder–hand line (angle ψ). Choose ψ so that the arm passes through the middle of the window without touching the frame."] } },
  ],
  params: [
    { id: "t3", name: ["起始形态的 θ₃（A 点的自运动闭曲线上）", "θ₃ of the start (on A's self-motion curve)"], min: -100, max: 100, step: 1, value: 33, unit: "°", digits: 0 },
    { id: "ctrl", name: ["控制：0 锁住关节 3 / 1 最小范数 / 2 局部优先级", "control: 0 joint 3 locked / 1 minimum norm / 2 local priority"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "psi", name: ["肘部摆角 ψ", "elbow swing angle ψ"], min: -180, max: 180, step: 5, value: 0, unit: "°", digits: 0 },
  ],
  legend: [{ color: "#cf222e", name: ["工人的手", "worker's hand"] }, { color: "#d29922", name: ["肘点的路径", "elbow path"] }, { color: "#1f6feb", name: ["手的直线路径", "straight hand path"] }],
  tasks: [
    { id: "min", robot: true, text: ["最小范数解（控制 1），θ₃ = 33°（离 ready 最近的起点）：最小距离不到 0.10 m。", "Minimum norm (control 1) from θ₃ = 33° (the start nearest to ready): the minimum distance is below 0.10 m."],
      demo: { scene: "cell", set: { t3: 33, ctrl: 1 }, press: ["start"], wait: 8 } },
    { id: "pri", robot: true, text: ["局部优先级（控制 2），θ₃ = 33°：距离提高到 0.10 m 以上，但关节速度超过上限。", "Local priority (control 2) from θ₃ = 33°: the distance rises above 0.10 m, but a joint speed exceeds its limit."],
      demo: { scene: "cell", set: { t3: 33, ctrl: 2 }, press: ["start"], wait: 8 } },
    { id: "all", robot: true, text: ["挑一个起始形态，用局部优先级完成搬运，四条要求全部满足。", "Choose a start so that local priority control meets all four requirements."],
      demo: { scene: "cell", set: { t3: 95, ctrl: 2 }, press: ["start"], wait: 8 } },
    { id: "plain", robot: true, text: ["只用最小范数解（控制 1），挑一个起始形态使四条要求全部满足，且最小距离超过 0.2 m。", "With the minimum norm alone (control 1), choose a start that meets all four requirements with a minimum distance above 0.2 m."],
      demo: { scene: "cell", set: { t3: 95, ctrl: 1 }, press: ["start"], wait: 8 } },
    { id: "car", text: ["生活场景：选一个肘部摆角，手臂从窗口穿过，离窗框至少 4 cm。", "Everyday scene: choose an elbow angle so the arm passes through the window at least 4 cm from the frame."],
      demo: { scene: "car", set: { psi: 150 }, press: [], wait: 2 } },
  ],
  think: ["θ₃ = 33° 与 θ₃ = 95° 的两个起始形态，手的位姿完全相同。为什么后者能轻松避开工人的手，而前者即使加了避障控制也来不及？这说明全局规划与局部控制各起什么作用？",
          "The starts at θ₃ = 33° and θ₃ = 95° have exactly the same hand pose. Why does the latter keep clear of the worker easily while the former cannot react in time even with avoidance control? What does this say about the roles of global planning and local control?"],

  // ---------------- Panda 的运动学（表 12.3.1）
  AX: [[[0, 0, 1], [0, 0, 0.333]], [[0, 1, 0], [0, 0, 0.333]], [[0, 0, 1], [0, 0, 0.649]], [[0, -1, 0], [0.0825, 0, 0.649]],
       [[0, 0, 1], [0, 0, 1.033]], [[0, -1, 0], [0, 0, 1.033]], [[0, 0, -1], [0.088, 0, 1.033]]],
  FL: [0.088, 0, 0.926], READY: [0, -45, 0, -135, 0, 90, 45].map((d) => d * Math.PI / 180),
  LO: [-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973], HI: [2.8973, 1.7628, 2.8973, -0.0698, 2.8973, 3.7525, 2.8973],
  QDMAX: [2.175, 2.175, 2.175, 2.175, 2.61, 2.61, 2.61],
  A: [0.40, 0.35, 0.30], B: [0.40, -0.35, 0.30], C0: [-0.45, 0.35, 0.60], C1: [-0.05, 0.12, 0.60], RAD: 0.06, TT: 3.0, DT: 0.004,
  SEGLINK: [0, 3, 3, 4, 4, 6, 7],
  add(a, b) { return a.map((x, i) => x + b[i]); }, sub(a, b) { return a.map((x, i) => x - b[i]); }, mul(a, s) { return a.map((x) => x * s); },
  dot(a, b) { return a.reduce((s, x, i) => s + x * b[i], 0); }, norm(a) { return Math.sqrt(this.dot(a, a)); },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  mv(R, v) { return [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]); },
  mm(A, B) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j])); },
  tr(R) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => R[j][i])); },
  rot(w, t) { const c = Math.cos(t), s = Math.sin(t), v = 1 - c, [x, y, z] = w;
    return [[c + x * x * v, x * y * v - z * s, x * z * v + y * s], [y * x * v + z * s, c + y * y * v, y * z * v - x * s], [z * x * v - y * s, z * y * v + x * s, c + z * z * v]]; },
  chain(th) {   // 各段的累积变换 E_k = e^{[S1]θ1}⋯e^{[Sk]θk}（k = 0…7），以 (R, p) 表示
    let R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p = [0, 0, 0];
    const out = [{ R, p }];
    this.AX.forEach(([w, q], i) => { const Ri = this.rot(w, th[i]), pi = this.sub(q, this.mv(Ri, q)); p = this.add(this.mv(R, pi), p); R = this.mm(R, Ri); out.push({ R, p }); });
    return out;
  },
  act(E, x) { return this.add(this.mv(E.R, x), E.p); },
  axesNow(Es) { return this.AX.map(([w, q], i) => [this.mv(Es[i].R, w), this.act(Es[i], q)]); },
  jg(th) {   // 几何雅可比（法兰中心），6×7，按列存放：[ω; ω × (F − q)]
    const Es = this.chain(th), F = this.act(Es[7], this.FL), ax = this.axesNow(Es);
    return { cols: ax.map(([w, q]) => [...w, ...this.cross(w, this.sub(F, q))]), Es, F, ax };
  },
  logR(R) { const c = Math.max(-1, Math.min(1, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)), a = Math.acos(c);
    const v = [(R[2][1] - R[1][2]) / 2, (R[0][2] - R[2][0]) / 2, (R[1][0] - R[0][1]) / 2]; return a < 1e-9 ? v : this.mul(v, a / Math.sin(a)); },
  solve(M, b) {   // 方阵线性方程组（列主元高斯消去）
    const n = b.length, A = M.map((r, i) => [...r, b[i]]);
    for (let c = 0; c < n; c++) { let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r; [A[c], A[p]] = [A[p], A[c]];
      for (let r = c + 1; r < n; r++) { const f = A[r][c] / A[c][c]; for (let k = c; k <= n; k++) A[r][k] -= f * A[c][k]; } }
    const x = new Array(n).fill(0); for (let i = n - 1; i >= 0; i--) { let s = A[i][n]; for (let k = i + 1; k < n; k++) s -= A[i][k] * x[k]; x[i] = s / A[i][i]; }
    return x;
  },
  det(M) { const n = M.length, A = M.map((r) => r.slice()); let d = 1;
    for (let c = 0; c < n; c++) { let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      if (Math.abs(A[p][c]) < 1e-300) return 0; if (p !== c) { [A[c], A[p]] = [A[p], A[c]]; d = -d; } d *= A[c][c];
      for (let r = c + 1; r < n; r++) { const f = A[r][c] / A[c][c]; for (let k = c; k < n; k++) A[r][k] -= f * A[c][k]; } }
    return d; },
  rowsOf(cols) { return [0, 1, 2, 3, 4, 5].map((r) => cols.map((c) => c[r])); },
  pinvTimes(cols, v) {   // Jᵀ(JJᵀ)⁻¹ v
    const JJt = [0, 1, 2, 3, 4, 5].map((i) => [0, 1, 2, 3, 4, 5].map((j) => cols.reduce((s, c) => s + c[i] * c[j], 0)));
    const y = this.solve(JJt, v); return cols.map((c) => this.dot(c, y));
  },
  nullVec(cols) { return cols.map((_, i) => ((i % 2 === 0) ? 1 : -1) * this.det(this.rowsOf(cols.filter((__, k) => k !== i)))); },   // 式 (17.2.2)，m = 6
  manip(cols) { const JJt = [0, 1, 2, 3, 4, 5].map((i) => [0, 1, 2, 3, 4, 5].map((j) => cols.reduce((s, c) => s + c[i] * c[j], 0))); return Math.sqrt(Math.max(0, this.det(JJt))); },
  err(J, Rd, pd) { return [...this.logR(this.mm(Rd, this.tr(J.Es[7].R))), ...this.sub(pd, J.F)]; },
  newton(th, Rd, pd) { for (let k = 0; k < 30; k++) { const J = this.jg(th), e = this.err(J, Rd, pd); if (this.norm(e) < 1e-12) break; th = this.add(th, this.pinvTimes(J.cols, e)); } return th; },
  into(q) { return q.map((x, i) => this.LO[i] + (((x - this.LO[i]) % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI)); },
  inLim(q) { return this.into(q).every((x, i) => x <= this.HI[i]); },
  margin(q) { const r = this.into(q); return Math.min(...r.map((x, i) => Math.min(x - this.LO[i], this.HI[i] - x) / (this.HI[i] - this.LO[i]))); },
  points(Es) { return [[0, 0, 0], [0, 0, 0.333], this.act(Es[3], [0, 0, 0.649]), this.act(Es[3], [0.0825, 0, 0.649]), this.act(Es[4], [0, 0, 0.649]),
                       this.act(Es[4], [0, 0, 1.033]), this.act(Es[6], [0.088, 0, 1.033]), this.act(Es[7], this.FL)]; },
  // A 点的自运动闭曲线：θ₃ 单调增加一整圈
  loopA() {
    if (this._loop) return this._loop;
    const Rd = this.chain(this.READY)[7].R, unit = (th) => { const c = this.nullVec(this.jg(th).cols), n = this.norm(c); return this.mul(c, Math.sign(c[2]) / n); };
    let th = this.newton(this.READY.slice(), Rd, this.A);
    const t30 = th[2], loop = [];
    for (let k = 0; k < 4000; k++) {
      loop.push(th.slice());
      const h = 0.01, mid = this.add(th, this.mul(unit(th), h / 2));
      th = this.newton(this.add(th, this.mul(unit(mid), h)), Rd, this.A);
      if (th[2] - t30 >= 2 * Math.PI) break;
    }
    this._loop = { loop, Rd };
    return this._loop;
  },
  startConfig(api) {   // θ₃（化到 ±180°）最接近滑块值的那一点
    const { loop } = this.loopA(), want = (api.p.ctrl === 0 ? 0 : api.p.t3) * Math.PI / 180;
    let best = null, bd = 1e9;
    loop.forEach((q) => { const d = Math.abs(Math.atan2(Math.sin(q[2] - want), Math.cos(q[2] - want))); if (d < bd) { bd = d; best = q; } });
    return best.slice();
  },
  human(t) {
    const Th = 0.6 * this.TT;
    if (t >= Th) return { c: this.C1.slice(), cd: [0, 0, 0] };
    const s = (1 - Math.cos(Math.PI * t / Th)) / 2, sd = Math.PI / Th * Math.sin(Math.PI * t / Th) / 2;
    return { c: this.add(this.C0, this.mul(this.sub(this.C1, this.C0), s)), cd: this.mul(this.sub(this.C1, this.C0), sd) };
  },
  closest(Es, c) {
    const P = this.points(Es); let best = null;
    for (let i = 1; i < 7; i++) { const ab = this.sub(P[i + 1], P[i]), s = Math.max(0, Math.min(1, this.dot(this.sub(c, P[i]), ab) / this.dot(ab, ab))), x = this.add(P[i], this.mul(ab, s)), d = this.norm(this.sub(c, x));
      if (!best || d < best.d) best = { d, x, i }; }
    return best;
  },
  step(api, s) {   // 一个控制周期
    const t = s.t, TT = this.TT, sv = (1 - Math.cos(Math.PI * t / TT)) / 2, sd = Math.PI / TT * Math.sin(Math.PI * t / TT) / 2;
    const pd = this.add(this.A, this.mul(this.sub(this.B, this.A), sv)), V = [0, 0, 0, ...this.mul(this.sub(this.B, this.A), sd)];
    const J = this.jg(s.th), e = this.err(J, this.loopA().Rd, pd), rhs = V.map((x, i) => x + 5 * e[i]);
    const hm = this.human(t), cl = this.closest(J.Es, hm.c), d = cl.d - this.RAD;
    let qd, w;
    if (api.p.ctrl === 0) {
      const cols = J.cols.filter((_, k) => k !== 2), q6 = this.solve(this.rowsOf(cols), rhs);
      qd = [q6[0], q6[1], 0, q6[2], q6[3], q6[4], q6[5]]; w = Math.abs(this.det(this.rowsOf(cols)));
    } else {
      const q1 = this.pinvTimes(J.cols, rhs); qd = q1; w = this.manip(J.cols);
      if (api.p.ctrl === 2) {
        const nproj = (z) => { const r = this.pinvTimes(J.cols, J.cols[0].map((_, row) => J.cols.reduce((u, c, k) => u + c[row] * z[k], 0))); return this.sub(z, r); };
        let G = null, A1 = null;
        if (d < 0.14) {
          const u = this.mul(this.sub(cl.x, hm.c), 1 / this.norm(this.sub(cl.x, hm.c)));
          const a = J.ax.map(([wv, q], k) => (k < this.SEGLINK[cl.i] ? this.dot(u, this.cross(wv, this.sub(cl.x, q))) : 0));
          A1 = nproj(a); const den = this.dot(A1, A1) + 0.03 * 0.03; G = this.mul(A1, 1 / den);
          qd = this.add(qd, this.mul(G, this.dot(u, hm.cd) + 3 * (0.14 - d) - this.dot(a, qd)));
        }
        const gH = s.th.map((x, i) => 2 * (x - (this.LO[i] + this.HI[i]) / 2) / ((this.HI[i] - this.LO[i]) ** 2));
        let z = nproj(gH); if (G) z = this.sub(z, this.mul(G, this.dot(A1, gH)));
        qd = this.sub(qd, this.mul(z, 2));
      }
    }
    s.dmin = Math.min(s.dmin, d); s.mg = Math.min(s.mg, this.margin(s.th)); s.wmin = Math.min(s.wmin, w);
    s.vmax = Math.max(s.vmax, ...qd.map((x, i) => Math.abs(x) / this.QDMAX[i])); s.emax = Math.max(s.emax, this.norm(e.slice(3)));
    s.th = this.add(s.th, this.mul(qd, this.DT)); s.t += this.DT; s.d = d; s.c = hm.c;
    s.elbow.push(this.points(this.chain(s.th))[3]);
  },
  // ---------------- 生活场景：车窗
  S: [-0.30, 0, 1.15], W: [0.20, 0.05, 0.98], LA: 0.30, LB: 0.30, WIN: [-0.25, 0.25, 1.00, 1.32], ARM_R: 0.04,
  elbowCar(psi) {
    const S = this.S, Wp = this.W, D = this.norm(this.sub(Wp, S)), u = this.mul(this.sub(Wp, S), 1 / D);
    const h = (this.LA * this.LA - this.LB * this.LB + D * D) / (2 * D), r = Math.sqrt(this.LA * this.LA - h * h), C = this.add(S, this.mul(u, h));
    let e1 = this.sub([0, 0, -1], this.mul(u, -u[2])); e1 = this.mul(e1, 1 / this.norm(e1)); const e2 = this.cross(u, e1);
    return this.add(C, this.add(this.mul(e1, r * Math.cos(psi)), this.mul(e2, r * Math.sin(psi))));
  },
  carClear(E) {   // 手臂穿过 x = 0 平面的那一点离窗框的距离（减去手臂半径）
    const segs = [[this.S, E], [E, this.W]];
    for (const [P, Q] of segs) if (P[0] <= 0 && Q[0] >= 0) { const t = -P[0] / (Q[0] - P[0]), X = this.add(P, this.mul(this.sub(Q, P), t));
      return { X, m: Math.min(X[1] - this.WIN[0], this.WIN[1] - X[1], X[2] - this.WIN[2], this.WIN[3] - X[2]) - this.ARM_R }; }
    return { X: null, m: -1 };
  },

  reset(api, s) {
    s.t = 0; s.dmin = 9; s.mg = 9; s.wmin = 9; s.vmax = 0; s.emax = 0; s.done = false; s.elbow = []; s.d = NaN; s.c = this.C0.slice();
    if (api.scene === "cell") { s.th = this.startConfig(api); s.ok = this.inLim(s.th); }
  },
  start(api, s) { if (api.scene === "cell" && !s.ok) api.stop(); },
  update(dt, api, s) {
    if (api.scene !== "cell") { api.stop(); return; }
    for (let k = 0; k < 15 && !s.done; k++) { this.step(api, s); if (s.t >= this.TT - 1e-9) { s.done = true; api.stop(); } }
  },
  readouts(api, s) {
    if (api.scene === "car") {
      const E = this.elbowCar(api.p.psi * Math.PI / 180), cc = this.carClear(E);
      if (cc.m >= 0) api.done("car");
      return [[["肘部摆角 ψ", "elbow angle ψ"], api.p.psi + "°"], [["肘点", "elbow point"], "(" + E.map((x) => x.toFixed(3)).join(", ") + ") m"],
              [["手臂穿过窗口处离窗框", "clearance where the arm passes the window"], (cc.m * 100).toFixed(1) + " cm"],
              [["状态", "status"], cc.m >= 0 ? api.T("顺利穿过窗口", "passes the window") : api.T("碰到窗框！", "hits the frame!")]];
    }
    if (!s.th) return [];
    const st = this.startConfig(api);
    const rows = [[["起始形态 θ / (°)", "start θ / (°)"], st.map((x) => (Math.atan2(Math.sin(x), Math.cos(x)) * 180 / Math.PI).toFixed(1)).join(", ")],
                  [["起始形态是否在限位以内", "start within limits"], s.ok ? api.T("是", "yes") : api.T("否，换一个 θ₃", "no, try another θ₃")]];
    if (s.t > 0) {
      rows.push([["时间", "time"], s.t.toFixed(2) + " s"], [["离工人的手的最小距离", "minimum distance to the worker's hand"], s.dmin.toFixed(3) + " m"],
                [["限位余量（最小）", "limit margin (minimum)"], s.mg.toFixed(3)], [["速度比（最大）", "speed ratio (maximum)"], s.vmax.toFixed(2)],
                [[api.p.ctrl === 0 ? "|det J₍₃₎|（最小）" : "可操作度（最小）", api.p.ctrl === 0 ? "|det J₍₃₎| (minimum)" : "manipulability (minimum)"], s.wmin.toFixed(4)],
                [["手的位置误差（最大）", "hand position error (maximum)"], (s.emax * 1000).toFixed(2) + " mm"]);
      const ok = s.dmin >= 0.10 && s.mg > 0 && s.vmax <= 1 && s.emax < 1e-3;
      rows.push([["四条要求", "four requirements"], s.done ? (ok ? api.T("全部满足", "all met") : api.T("没有全部满足", "not all met")) : "—"]);
      if (s.done) {
        if (api.p.ctrl === 1 && Math.abs(api.p.t3 - 33) < 0.5 && s.dmin < 0.10) api.done("min");
        if (api.p.ctrl === 2 && Math.abs(api.p.t3 - 33) < 0.5 && s.dmin > 0.10 && s.vmax > 1) api.done("pri");
        if (api.p.ctrl === 2 && ok) api.done("all");
        if (api.p.ctrl === 1 && ok && s.dmin > 0.2) api.done("plain");
      }
    }
    return rows;
  },
  // ---------------- 三维
  setup3d(api, keep) {
    const T = api.three, pa = api.m["B-ARM-PANDA"];
    pa.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(pa.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    const m = (c, o) => new T.MeshStandardMaterial(Object.assign({ color: c }, o || {}));
    keep.hand = new T.Mesh(new T.SphereGeometry(this.RAD, 24, 16), m(0xcf222e, { transparent: true, opacity: 0.8 })); G.add(keep.hand);
    const lineOf = (pts, color) => { const g = new T.BufferGeometry().setFromPoints(pts.map((p) => new T.Vector3(...p))); return new T.Line(g, new T.LineBasicMaterial({ color })); };
    keep.path = lineOf([this.A, this.B], 0x1f6feb); G.add(keep.path);
    [this.A, this.B].forEach((p) => { const b = new T.Mesh(new T.SphereGeometry(0.015, 12, 8), m(0x1f6feb)); b.position.set(...p); G.add(b); });
    keep.trailGeo = new T.BufferGeometry(); keep.trailGeo.setAttribute("position", new T.BufferAttribute(new Float32Array(3 * 1000), 3)); keep.trailGeo.setDrawRange(0, 0);
    keep.trail = new T.Line(keep.trailGeo, new T.LineBasicMaterial({ color: 0xd29922 })); G.add(keep.trail);
    keep.cellObjs = [keep.hand, keep.path, keep.trail];
    // 车窗场景（放在机器人旁边 (2.5, 3, 0) 处）
    const Cg = new T.Group(); Cg.position.set(2.5, 3.0, 0); G.add(Cg); keep.Cg = Cg;
    const box = (sx, sy, sz, x, y, z, c, o) => { const b = new T.Mesh(new T.BoxGeometry(sx, sy, sz), m(c, o)); b.position.set(x, y, z); Cg.add(b); return b; };
    const [y0, y1, z0, z1] = this.WIN;
    box(0.04, 1.4, z0 - 0.1, 0, 0, (z0 - 0.1) / 2 + 0.05, 0x6e7681);                     // 车门下部
    box(0.04, 1.4, 0.06, 0, 0, z0 - 0.03, 0x8b949e);                                       // 窗台
    box(0.04, 1.4, 0.06, 0, 0, z1 + 0.03, 0x8b949e);                                       // 窗框上沿
    box(0.04, 0.45, z1 - z0, 0, y0 - 0.225, (z0 + z1) / 2, 0x8b949e);                      // 两侧立柱
    box(0.04, 0.45, z1 - z0, 0, y1 + 0.225, (z0 + z1) / 2, 0x8b949e);
    box(0.5, 0.5, 0.12, 0.35, 0.05, 0.62, 0x57606a);                                       // 座椅
    box(0.16, 0.10, 0.12, this.W[0], this.W[1], this.W[2] - 0.08, 0x9a6b3a);               // 包
    const torso = new T.Mesh(new T.CylinderGeometry(0.16, 0.14, 0.6, 20), m(0x3d6fb6)); torso.rotation.x = Math.PI / 2; torso.position.set(-0.42, 0.18, 0.95); Cg.add(torso);
    const head = new T.Mesh(new T.SphereGeometry(0.11, 20, 14), m(0xd9a679)); head.position.set(-0.42, 0.18, 1.38); Cg.add(head);
    keep.upper = new T.Mesh(new T.CylinderGeometry(this.ARM_R, this.ARM_R, 1, 14), m(0xd9a679)); Cg.add(keep.upper);
    keep.fore = new T.Mesh(new T.CylinderGeometry(this.ARM_R, this.ARM_R, 1, 14), m(0xd9a679)); Cg.add(keep.fore);
    keep.joint = new T.Mesh(new T.SphereGeometry(0.05, 16, 12), m(0xd29922)); Cg.add(keep.joint);
    const gr = new T.Mesh(new T.BoxGeometry(2.0, 2.0, 0.02), m(0xb8a27a)); gr.position.set(0, 0, -0.01); Cg.add(gr);
    keep.carBox = () => { G.updateMatrixWorld(true); return new T.Box3().setFromObject(Cg).expandByScalar(0.1); };
    api.m.carView = { entry: { robot: {} }, holder: { visible: false }, box: () => keep.carBox() };
  },
  link(T, mesh, a, b) {   // 圆柱从 a 到 b
    const d = this.sub(b, a), L = this.norm(d);
    mesh.position.set(...this.add(a, this.mul(d, 0.5))); mesh.scale.set(1, L, 1);
    mesh.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), new T.Vector3(...this.mul(d, 1 / L)));
  },
  draw(api, s) {
    const k = api.keep, pa = api.m["B-ARM-PANDA"], T = api.three;
    if (!k.G) return;
    const sc = api.scene;
    if (k.shown !== sc) { k.shown = sc; if (sc === "cell") api.view(-145, 22, 0.75, pa); else api.view(-30, 18, 0.9, api.m.carView); }
    pa.holder.visible = sc === "cell"; k.cellObjs.forEach((o) => { o.visible = sc === "cell"; }); k.Cg.visible = sc === "car";
    if (sc === "cell" && s.th) {
      const o = {}; s.th.forEach((x, i) => { o[`joint${i + 1}`] = x; }); pa.set(o);
      k.hand.position.set(...s.c);
      const n = Math.min(1000, s.elbow.length), arr = k.trailGeo.attributes.position.array;
      for (let i = 0; i < n; i++) { arr[3 * i] = s.elbow[i][0]; arr[3 * i + 1] = s.elbow[i][1]; arr[3 * i + 2] = s.elbow[i][2]; }
      k.trailGeo.attributes.position.needsUpdate = true; k.trailGeo.setDrawRange(0, n);
    }
    if (sc === "car") {
      const E = this.elbowCar(api.p.psi * Math.PI / 180), cc = this.carClear(E);
      this.link(T, k.upper, this.S, E); this.link(T, k.fore, E, this.W); k.joint.position.set(...E);
      const col = cc.m >= 0 ? 0xd9a679 : 0xcf222e; k.upper.material.color.setHex(col); k.fore.material.color.setHex(col);
    }
  },
});
