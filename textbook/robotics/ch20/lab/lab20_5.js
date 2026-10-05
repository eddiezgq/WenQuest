// 实验 20.5 Go2 转弯与仿人弯腰取物（配 20.5 节）。零件库 Go2 与 G1 三维模型。
// 场景“Go2 转弯”：机身以 (v, ω) 在水平面内运动（瞬心在 {b} 的 (0, v/ω)），小跑 t_c = 0.5 s、β = 0.5、抬脚 0.08 m。
//   按 20.5.2 节五步：支撑脚在 {b} 中绕瞬心以 −ω 转，落脚点使支撑段关于站立位置对称（式 (20.5.2)）；摆动脚在 {s} 中沿摆线
//   从抬脚点到下一个落脚点（机身在摆动期间的位移按 SE(2) 的指数）；各腿用实验 20.1 的逆解。机身位姿按 SE(2) 积分，
//   三维中 holder 平移、绕竖直轴转动（模型 (x, y) → 世界 (x, ·, −y)）。
// 生活场景“弯腰取物”：G1 两脚不动，右手心（右腕偏航连杆上的 (0.08, 0, 0) m）伸向 (fx, −0.20, fz) m；
//   变量：骨盆的 6 个自由度（绕骨盆原点的角速度 ω 与原点速度 v_o，{s} 中）+ 29 个关节。任务按优先级：两脚位姿 > 质心水平投影
//   （在双脚支撑多边形的中心；可关闭）> 手心位置；最后一级“姿势”用零空间中的梯度投影把关节拉回站姿（17.3 节）。
//   各级用阻尼最小二乘（式 (20.5.3)、(20.5.4)），关节到限位时锁住重解。每帧迭代几步，模型随之运动。
//   质心按 MJCF 的连杆质量与质心位置（同实验 20.4）。
WQ.lab({
  title: ["实验 20.5 Go2 转弯与仿人弯腰取物", "Lab 20.5 Go2 turning and a humanoid reaching down"],
  goal: ["让 Go2 边走边转，看内外侧各脚的支撑行程怎样随瞬心变化；让仿人机器人两脚不动去拿低处的盒子，比较有无质心任务时全身姿态和质心的位置。",
         "Let Go2 trot through a turn and see how each foot's stance stroke follows the ICR; let a humanoid reach for a low box with its feet planted, and compare the whole-body posture and the CoM with and without the CoM task."],
  view: "3d",
  models: ["B-LEG-GO2", "B-HUM-G1"],
  scenes: [
    { id: "turn", robot: true, name: ["Go2 转弯", "Go2 turning"], hide: ["fx", "fz", "comt"],
      problem: { title: ["机器人问题：小跑着拐过半径 1 m 的弯", "Robot problem: trot round a 1 m corner"],
                 text: ["给定车速 v 和角速度 ω，按“开始”让 Go2 小跑 1.5 s。黄色小球是瞬心，地面上的点是各脚的落脚点；测量区给出各脚的支撑行程。",
                        "Set the speed v and turn rate ω and press Start to trot for 1.5 s. The yellow ball is the ICR, the dots on the floor are the footholds; the readouts give each foot's stance stroke."] } },
    { id: "reach", name: ["生活：弯腰取物", "Everyday: reaching down"], hide: ["v", "om"],
      problem: { title: ["生活中的例子：弯腰捡东西时臀部为什么向后", "Everyday example: why the hips go back when you bend to pick something up"],
                 text: ["G1 代表人。两脚不动，右手伸向身前低处的盒子。打开质心任务，臀部后移、腰前弯；关掉它，全身前倾，质心越过脚尖。",
                        "G1 stands for a person. Feet planted, the right hand reaches for a low box ahead. With the CoM task the hips go back and the waist bends; without it the whole body tips forward and the CoM passes the toes."] } },
  ],
  params: [
    { id: "v", name: ["车速 v", "speed v"], min: 0, max: 0.8, step: 0.05, value: 0.5, unit: "m/s", digits: 2 },
    { id: "om", name: ["角速度 ω（左转为正）", "turn rate ω (left positive)"], min: -1.0, max: 1.0, step: 0.05, value: 0.5, unit: "rad/s", digits: 2 },
    { id: "fx", name: ["盒子前方距离", "box distance ahead"], min: 0.2, max: 0.6, step: 0.01, value: 0.4, unit: "m", digits: 2 },
    { id: "fz", name: ["盒子离地高度", "box height"], min: 0.3, max: 0.9, step: 0.01, value: 0.6, unit: "m", digits: 2 },
    { id: "comt", name: ["质心任务（1 开 / 0 关）", "CoM task (1 on / 0 off)"], min: 0, max: 1, step: 1, value: 1, digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "r1", robot: true, text: ["让 Go2 以 1 m 的转弯半径左转（v = 0.5 m/s、ω = 0.5 rad/s）小跑一个周期以上。", "Make Go2 trot a left turn of radius 1 m (v = 0.5 m/s, ω = 0.5 rad/s) for more than one cycle."],
      demo: { scene: "turn", set: { v: 0.5, om: 0.5 }, press: ["start"], wait: 60 } },
    { id: "spin", robot: true, text: ["让 Go2 原地转身（v = 0），比较四只脚的支撑行程。", "Make Go2 turn on the spot (v = 0) and compare the four stance strokes."],
      demo: { scene: "turn", set: { v: 0, om: 0.8 }, press: ["start"], wait: 60 } },
    { id: "reach", text: ["打开质心任务，让 G1 的右手拿到前方 0.40 m、离地 0.35 m 的盒子，质心留在支撑区内（裕度大于 3 cm）。", "With the CoM task on, let G1's right hand reach the box 0.40 m ahead and 0.35 m high, the CoM staying inside the support (margin above 3 cm)."],
      demo: { scene: "reach", set: { comt: 1, fx: 0.4, fz: 0.35 }, press: [], wait: 120 } },
    { id: "fall", text: ["关掉质心任务再拿同一个盒子：手到了，但质心移出了支撑区。", "Switch the CoM task off and reach the same box: the hand gets there but the CoM leaves the support."],
      demo: { scene: "reach", set: { comt: 0, fx: 0.4, fz: 0.35 }, press: [], wait: 120 } },
  ],
  think: ["为什么转弯时外侧的脚迈得更远？转弯半径小于多少时，内侧的脚会在支撑相中向前移动？",
          "Why do the outer feet step further in a turn? Below what radius do the inner feet move forward during stance?"],

  AX: 0.1934, AY: 0.0465, DY: 0.0955, L1: 0.213, L2: 0.213, HH: 0.2648, TC: 0.5, BETA: 0.5, HS: 0.08,
  LEGS: ["FL", "FR", "RL", "RR"], PH: { RL: 0, FR: 0, FL: 0.5, RR: 0.5 },

  // ---------------- Go2：20.5.2 节的五步
  nominal(leg) { return [(leg[0] === "F" ? 1 : -1) * this.AX, (leg[1] === "L" ? 1 : -1) * (this.AY + this.DY)]; },
  rotAbout(p, c, a) { const x = p[0] - c[0], y = p[1] - c[1]; return [c[0] + Math.cos(a) * x - Math.sin(a) * y, c[1] + Math.sin(a) * x + Math.cos(a) * y]; },
  stancePos(leg, s, v, om) {
    const p0 = this.nominal(leg), Tst = this.BETA * this.TC;
    if (Math.abs(om) < 1e-9) return [p0[0] + v * Tst * (0.5 - s), p0[1]];
    return this.rotAbout(p0, [0, v / om], -om * Tst * (s - 0.5));
  },
  bodyDisp(v, om, t) { if (Math.abs(om) < 1e-9) return [v * t, 0, 0]; return [v / om * Math.sin(om * t), v / om * (1 - Math.cos(om * t)), om * t]; },
  footB(leg, t, v, om) {
    const u = (((t / this.TC - this.PH[leg]) % 1) + 1) % 1;
    if (u < this.BETA) { const p = this.stancePos(leg, u / this.BETA, v, om); return [p[0], p[1], -this.HH, true]; }
    const tau = (u - this.BETA) / (1 - this.BETA), Tsw = (1 - this.BETA) * this.TC, sp = tau - Math.sin(2 * Math.PI * tau) / (2 * Math.PI);
    const lift = this.stancePos(leg, 1, v, om), land = this.stancePos(leg, 0, v, om), [ex, ey, ea] = this.bodyDisp(v, om, Tsw);
    const ls = [ex + Math.cos(ea) * land[0] - Math.sin(ea) * land[1], ey + Math.sin(ea) * land[0] + Math.cos(ea) * land[1]];
    const w = [lift[0] + sp * (ls[0] - lift[0]), lift[1] + sp * (ls[1] - lift[1])], [px, py, pa] = this.bodyDisp(v, om, tau * Tsw);
    const dx = w[0] - px, dy = w[1] - py;
    return [Math.cos(pa) * dx + Math.sin(pa) * dy, -Math.sin(pa) * dx + Math.cos(pa) * dy, -this.HH + this.HS * (1 - Math.cos(2 * Math.PI * tau)) / 2, false];
  },
  ik(leg, p) {
    const sx = leg[0] === "F" ? 1 : -1, sy = leg[1] === "L" ? 1 : -1, l1 = this.L1, l2 = this.L2;
    const r = [p[0] - sx * this.AX, p[1] - sy * this.AY, p[2]], rho2 = r[1] * r[1] + r[2] * r[2];
    if (rho2 < this.DY * this.DY) return null;
    const zp = -Math.sqrt(rho2 - this.DY * this.DY), xp = r[0], D = Math.hypot(xp, zp), c3 = (D * D - l1 * l1 - l2 * l2) / (2 * l1 * l2);
    if (c3 > 1 || c3 < -1) return null;
    const t3 = -Math.acos(c3), t2 = Math.atan2(-xp, -zp) - Math.atan2(l2 * Math.sin(t3), l1 + l2 * Math.cos(t3)), t1 = Math.atan2(r[2], r[1]) - Math.atan2(zp, sy * this.DY);
    return [t1, t2, t3];
  },

  // ---------------- G1 全身逆运动学
  G1M: { pelvis: [[0, 0, -0.07605], 3.813], left_hip_pitch_link: [[0.002741, 0.047791, -0.02606], 1.35], left_hip_roll_link: [[0.029812, -0.001045, -0.087934], 1.52],
    left_hip_yaw_link: [[-0.057709, -0.010981, -0.15078], 1.702], left_knee_link: [[0.005457, 0.003964, -0.12074], 1.932], left_ankle_pitch_link: [[-0.007269, 0, 0.011137], 0.074],
    left_ankle_roll_link: [[0.026505, 0, -0.016425], 0.608], right_hip_pitch_link: [[0.002741, -0.047791, -0.02606], 1.35], right_hip_roll_link: [[0.029812, 0.001045, -0.087934], 1.52],
    right_hip_yaw_link: [[-0.057709, 0.010981, -0.15078], 1.702], right_knee_link: [[0.005457, -0.003964, -0.12074], 1.932], right_ankle_pitch_link: [[-0.007269, 0, 0.011137], 0.074],
    right_ankle_roll_link: [[0.026505, 0, -0.016425], 0.608], waist_yaw_link: [[0.003494, 0.000233, 0.018034], 0.214], waist_roll_link: [[0, 0.000023, 0], 0.086],
    torso_link: [[0.00203158, 0.000339683, 0.184568], 7.818], left_shoulder_pitch_link: [[0, 0.035892, -0.011628], 0.718], left_shoulder_roll_link: [[-0.000227, 0.00727, -0.063243], 0.643],
    left_shoulder_yaw_link: [[0.010773, -0.002949, -0.072009], 0.734], left_elbow_link: [[0.064956, 0.004454, -0.010062], 0.6], left_wrist_roll_link: [[0.0171394, 0.000537591, 0], 0.085445],
    left_wrist_pitch_link: [[0.0229999, -0.00111685, -0.00111658], 0.48405], left_wrist_yaw_link: [[0.0708244, 0.000191745, 0.00161742], 0.254576],
    right_shoulder_pitch_link: [[0, -0.035892, -0.011628], 0.718], right_shoulder_roll_link: [[-0.000227, -0.00727, -0.063243], 0.643], right_shoulder_yaw_link: [[0.010773, 0.002949, -0.072009], 0.734],
    right_elbow_link: [[0.064956, -0.004454, -0.010062], 0.6], right_wrist_roll_link: [[0.0171394, -0.000537591, 0], 0.085445], right_wrist_pitch_link: [[0.0229999, 0.00111685, -0.00111658], 0.48405],
    right_wrist_yaw_link: [[0.0708244, -0.000191745, 0.00161742], 0.254576] },
  SOLE: [[-0.05, 0.025, -0.035], [-0.05, -0.025, -0.035], [0.12, -0.03, -0.035], [0.12, 0.03, -0.035]],
  // 世界（Y 向上）→ 模型（Z 向上）
  toM(api, M4) { const e = new api.three.Matrix4().copy(api.keep.Cinv).multiply(M4).elements; return { R: [[e[0], e[4], e[8]], [e[1], e[5], e[9]], [e[2], e[6], e[10]]], p: [e[12], e[13], e[14]] }; },
  ptM(api, node, xyz) { const T = api.three, v = new T.Vector3(xyz[0], xyz[1], xyz[2]).applyMatrix4(node.matrixWorld); return [v.x, -v.z, v.y]; },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  placeG1(api) {
    const T = api.three, K = api.keep, g = api.m["B-HUM-G1"], R = K.Rb, p = K.pb;
    const Ts = new T.Matrix4().set(R[0][0], R[0][1], R[0][2], p[0], R[1][0], R[1][1], R[1][2], p[1], R[2][0], R[2][1], R[2][2], p[2], 0, 0, 0, 1);
    new T.Matrix4().copy(K.C).multiply(Ts).multiply(K.MhpInv).decompose(g.holder.position, g.holder.quaternion, g.holder.scale);
    g.holder.updateMatrixWorld(true);
    const o = {};
    K.J.forEach((n, i) => { o[n] = K.q[i]; });
    g.set(o);
  },
  wbStep(api) {   // 一步全身逆运动学（式 (20.5.3)、(20.5.4)）
    const K = api.keep, g = api.m["B-HUM-G1"], la = api.la, nq = K.J.length, n = 6 + nq;
    this.placeG1(api);
    const axes = K.J.map((name) => { const j = g.joints[name], node = j.node, w = node.matrixWorld.elements;
      const Rm = this.toM(api, node.matrixWorld).R, a = j.axisV, ax = [0, 1, 2].map((i) => Rm[i][0] * a.x + Rm[i][1] * a.y + Rm[i][2] * a.z);
      return { w: ax, o: this.ptM(api, node, [0, 0, 0]) }; });
    const pb = K.pb;
    const pointJ = (p, link) => { const rows = [[], [], []], anc = K.anc[link];
      const d = [p[0] - pb[0], p[1] - pb[1], p[2] - pb[2]];
      // 机身列：v_o + ω × (p − p_sb)
      const cw = [[0, d[2], -d[1]], [-d[2], 0, d[0]], [d[1], -d[0], 0]];
      for (let i = 0; i < 3; i++) { for (let k = 0; k < 3; k++) rows[i].push(cw[i][k]); for (let k = 0; k < 3; k++) rows[i].push(i === k ? 1 : 0); }
      K.J.forEach((nm, j) => { const c = anc.has(nm) ? this.cross(axes[j].w, [p[0] - axes[j].o[0], p[1] - axes[j].o[1], p[2] - axes[j].o[2]]) : [0, 0, 0]; for (let i = 0; i < 3; i++) rows[i].push(c[i]); });
      return rows; };
    const frameJ = (link) => { const node = g.nodes[link], P = this.toM(api, node.matrixWorld), rows = pointJ(P.p, link), wr = [[], [], []], anc = K.anc[link];
      for (let i = 0; i < 3; i++) { for (let k = 0; k < 3; k++) wr[i].push(i === k ? 1 : 0); for (let k = 0; k < 3; k++) wr[i].push(0); }
      K.J.forEach((nm, j) => { for (let i = 0; i < 3; i++) wr[i].push(anc.has(nm) ? axes[j].w[i] : 0); });
      return { J: wr.concat(rows), P }; };
    const errPose = (P, T0) => { const A = T0.R, B = P.R, E = [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[i][0] * B[j][0] + A[i][1] * B[j][1] + A[i][2] * B[j][2]));
      return [(E[2][1] - E[1][2]) / 2, (E[0][2] - E[2][0]) / 2, (E[1][0] - E[0][1]) / 2, T0.p[0] - P.p[0], T0.p[1] - P.p[1], T0.p[2] - P.p[2]]; };
    const fl = frameJ("left_ankle_roll_link"), fr = frameJ("right_ankle_roll_link");
    const J1 = fl.J.concat(fr.J), e1 = errPose(fl.P, K.TfL).concat(errPose(fr.P, K.TfR));
    let m = 0, c = [0, 0, 0];
    const Jc = [new Array(n).fill(0), new Array(n).fill(0), new Array(n).fill(0)];
    Object.entries(this.G1M).forEach(([name, [cc, mk]]) => { const pc = this.ptM(api, g.nodes[name], cc), Jp = pointJ(pc, name);
      for (let i = 0; i < 3; i++) { c[i] += mk * pc[i]; for (let k = 0; k < n; k++) Jc[i][k] += mk * Jp[i][k]; } m += mk; });
    c = c.map((x) => x / m);
    for (let i = 0; i < 3; i++) for (let k = 0; k < n; k++) Jc[i][k] /= m;
    const hand = this.ptM(api, g.nodes.right_wrist_yaw_link, [0.08, 0, 0]), Jh = pointJ(hand, "right_wrist_yaw_link");
    const tgt = [api.p.fx, -0.2, api.p.fz], e3 = tgt.map((x, i) => x - hand[i]), e2 = [K.cgoal[0] - c[0], K.cgoal[1] - c[1]];
    const tasks = [[J1, e1, 1e-4]];
    if (api.p.comt > 0.5) tasks.push([Jc.slice(0, 2), e2, 1e-4]);
    const h3 = Math.min(1, 0.08 / (Math.hypot(...e3) + 1e-12));      // 手的误差大时限制步长
    tasks.push([Jh, e3.map((x) => 0.5 * h3 * x), 1e-3]);
    const solve = (A, b) => { const M = A.map((r, i) => r.concat([b[i]])), N = M.length;     // 高斯消去
      for (let k = 0; k < N; k++) { let pv = k; for (let i = k + 1; i < N; i++) if (Math.abs(M[i][k]) > Math.abs(M[pv][k])) pv = i; [M[k], M[pv]] = [M[pv], M[k]];
        for (let i = k + 1; i < N; i++) { const f = M[i][k] / M[k][k]; for (let j = k; j <= N; j++) M[i][j] -= f * M[k][j]; } }
      const x = new Array(N).fill(0); for (let i = N - 1; i >= 0; i--) { let s = M[i][N]; for (let j = i + 1; j < N; j++) s -= M[i][j] * x[j]; x[i] = s / M[i][i]; } return x; };
    const lock = new Array(n).fill(false);
    let dx = null;
    for (let rep = 0; rep < 6; rep++) {
      let N = la.eye(n).map((r, i) => r.map((v) => (lock[i] ? 0 : v)));
      dx = new Array(n).fill(0);
      tasks.forEach(([J, e, lam]) => {
        const JN = la.mul(J, N), r = e.map((v, i) => v - J[i].reduce((s, a, k) => s + a * dx[k], 0));
        const G = la.mul(JN, la.T(JN)).map((row, i) => row.map((v, j) => v + (i === j ? lam * lam : 0)));
        const y = solve(G, r), step = la.mv(la.T(JN), y);
        dx = dx.map((v, k) => v + step[k]);
        // N ← N − (JN)ᵀ (JN (JN)ᵀ + εI)⁻¹ JN，ε 很小时就是 N − (JN)⁺ JN（式 (20.5.4)）
        const G0 = la.mul(JN, la.T(JN)).map((row, i) => row.map((v, j) => v + (i === j ? 1e-10 : 0)));
        const X = la.T(JN[0].map((_, k) => solve(G0, JN.map((r) => r[k]))));
        N = la.sub(N, la.mul(la.T(JN), X));
      });
      const qr = K.qrest.map((v, i) => 0.1 * (v - K.q[i])), z = new Array(6).fill(0).concat(qr);       // 姿势：零空间中的梯度投影
      const pz = la.mv(N, z);
      dx = dx.map((v, k) => v + pz[k]);
      let again = false;
      K.J.forEach((nm, i) => { const j = g.joints[nm], qn = K.q[i] + dx[6 + i]; if (!lock[6 + i] && (qn < j.lower - 1e-9 || qn > j.upper + 1e-9)) { lock[6 + i] = true; again = true; } });
      if (!again) break;
    }
    const w = dx.slice(0, 3), th = Math.hypot(...w);
    if (th > 1e-15) { const k = w.map((x) => x / th), Kx = [[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]], K2 = la.mul(Kx, Kx);
      const Rw = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + Math.sin(th) * Kx[i][j] + (1 - Math.cos(th)) * K2[i][j]));
      K.Rb = la.mul(Rw, K.Rb); }
    K.pb = K.pb.map((v, i) => v + dx[3 + i]);
    K.J.forEach((nm, i) => { const j = g.joints[nm]; K.q[i] = Math.min(j.upper, Math.max(j.lower, K.q[i] + dx[6 + i])); });
    const poly = K.poly2, mg = this.margin(poly, c);
    return { ef: Math.hypot(...e1), ec: Math.hypot(...e2), eh: Math.hypot(...e3), c, mg, hand };
  },
  hull(P) {
    const pts = P.map((p) => [p[0], p[1]]).sort((a, b) => a[0] - b[0] || a[1] - b[1]), cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]), lo = [], up = [];
    pts.forEach((p) => { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); });
    pts.slice().reverse().forEach((p) => { while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], p) <= 0) up.pop(); up.push(p); });
    return lo.slice(0, -1).concat(up.slice(0, -1));
  },
  margin(poly, c) {
    let inside = true, dmin = 1e9;
    for (let k = 0; k < poly.length; k++) {
      const a = poly[k], b = poly[(k + 1) % poly.length], e = [b[0] - a[0], b[1] - a[1]], L2 = e[0] * e[0] + e[1] * e[1];
      if ((c[0] - a[0]) * e[1] - (c[1] - a[1]) * e[0] > 0) inside = false;
      const t = Math.max(0, Math.min(1, ((c[0] - a[0]) * e[0] + (c[1] - a[1]) * e[1]) / L2));
      dmin = Math.min(dmin, Math.hypot(c[0] - a[0] - t * e[0], c[1] - a[1] - t * e[1]));
    }
    return inside ? dmin : -dmin;
  },

  setup3d(api, keep) {
    const T = api.three, go = api.m["B-LEG-GO2"], g = api.m["B-HUM-G1"];
    go.place(0, 0);
    g.place(0, 0);
    keep.goPos = go.holder.position.clone();
    keep.icr = new T.Mesh(new T.SphereGeometry(0.03, 16, 12), new T.MeshStandardMaterial({ color: 0xf2c200 }));
    api.st.scene.add(keep.icr);
    keep.prints = [];
    for (let k = 0; k < 24; k++) { const d = new T.Mesh(new T.CylinderGeometry(0.022, 0.022, 0.004, 16), new T.MeshStandardMaterial({ color: 0x1f77b4 })); d.visible = false; api.st.scene.add(d); keep.prints.push(d); }
    keep.path = api.trace(0x9aa6ad);
    // G1：模型坐标与世界坐标的换算、站立时两脚的位姿、骨盆在 holder 中的矩阵
    keep.C = new T.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1);
    keep.Cinv = keep.C.clone().invert();
    g.holder.updateMatrixWorld(true);
    const pel = g.nodes.pelvis;
    keep.MhpInv = new T.Matrix4().copy(g.holder.matrixWorld).invert().multiply(pel.matrixWorld).invert();
    const P0 = this.toM(api, pel.matrixWorld);
    keep.Rb0 = P0.R; keep.pb0 = P0.p;
    keep.TfL = this.toM(api, g.nodes.left_ankle_roll_link.matrixWorld);
    keep.TfR = this.toM(api, g.nodes.right_ankle_roll_link.matrixWorld);
    const soles = [];
    ["left", "right"].forEach((s) => this.SOLE.forEach((q) => soles.push(this.ptM(api, g.nodes[s + "_ankle_roll_link"], q))));
    keep.poly2 = this.hull(soles);
    keep.cgoal = [keep.poly2.reduce((s, p) => s + p[0], 0) / keep.poly2.length, keep.poly2.reduce((s, p) => s + p[1], 0) / keep.poly2.length];
    keep.J = g.entry.joints.map((j) => j.name);
    keep.qrest = keep.J.map((n) => (g.entry.rest || {})[n] || 0);
    const par = {};
    g.entry.joints.forEach((j) => { par[j.child] = [j.parent, j.name]; });
    keep.anc = {};
    Object.keys(this.G1M).concat(["left_ankle_roll_link", "right_ankle_roll_link", "right_wrist_yaw_link"]).forEach((l) => {
      const s = new Set(); let nd = l; while (par[nd]) { s.add(par[nd][1]); nd = par[nd][0]; } keep.anc[l] = s; });
    keep.box = new T.Mesh(new T.BoxGeometry(0.2, 1, 0.25), new T.MeshStandardMaterial({ color: 0xc9b48a, transparent: true, opacity: 0.8 }));
    api.st.scene.add(keep.box);
    keep.cball = new T.Mesh(new T.SphereGeometry(0.02, 16, 12), new T.MeshStandardMaterial({ color: 0x2ca02c }));
    api.st.scene.add(keep.cball);
    keep.supp = new T.LineLoop(new T.BufferGeometry().setFromPoints(keep.poly2.map((p) => new T.Vector3(p[0], 0.004, -p[1]))), new T.LineBasicMaterial({ color: 0x2ca02c }));
    api.st.scene.add(keep.supp);
    this.resetG1(api);
    keep.shown = null;
  },
  resetG1(api) { const K = api.keep; K.Rb = K.Rb0.map((r) => r.slice()); K.pb = K.pb0.slice(); K.q = K.qrest.slice(); K.res = null; K.key = null; },
  reset(api, s) {
    s.t = 0; s.x = [0, 0, 0];
    const K = api.keep;
    if (!K.prints) return;
    K.prints.forEach((d) => { d.visible = false; }); K.path.clear();
    if (api.scene === "reach") {
      const key = `${api.p.comt}`;
      if (K.key !== key) { this.resetG1(api); K.key = key; }    // 打开或关闭质心任务时从站姿重新开始
    }
  },
  update(dt, api, s) {
    if (api.scene !== "turn") { api.stop(); return; }
    const v = api.p.v, om = api.p.om, h = Math.min(dt, 0.02);
    s.t += h;
    const [dx, dy, da] = this.bodyDisp(v, om, h), c = Math.cos(s.x[2]), sn = Math.sin(s.x[2]);
    s.x = [s.x[0] + c * dx - sn * dy, s.x[1] + sn * dx + c * dy, s.x[2] + da];
    if (s.t >= 1.5) {
      api.stop();
      if (Math.abs(v - 0.5) < 0.03 && Math.abs(om - 0.5) < 0.03) api.done("r1");
      if (v < 0.01 && Math.abs(om) >= 0.3) api.done("spin");
    }
  },

  poseGo2(api, s) {
    const go = api.m["B-LEG-GO2"], K = api.keep, v = api.p.v, om = api.p.om, t = s.t || 0, x = s.x || [0, 0, 0], o = Object.assign({}, go.entry.rest);
    this.LEGS.forEach((leg) => {
      const f = this.footB(leg, t, v, om), q = this.ik(leg, f);
      if (q) { o[leg + "_hip_joint"] = q[0]; o[leg + "_thigh_joint"] = q[1]; o[leg + "_calf_joint"] = q[2]; }
      if (f[3] && api.running) {        // 落脚点：每条腿每次支撑一个圆点
        const k = Math.floor(t / this.TC - this.PH[leg] + 1e-9), slot = this.LEGS.indexOf(leg) * 6 + (((k % 6) + 6) % 6), d = K.prints[slot];
        const wx = K.goPos.x + x[0] + Math.cos(x[2]) * f[0] - Math.sin(x[2]) * f[1], wy = x[1] + Math.sin(x[2]) * f[0] + Math.cos(x[2]) * f[1];
        d.position.set(wx, 0.004, K.goPos.z - wy); d.visible = true;
      }
    });
    go.set(o);
    go.holder.position.set(K.goPos.x + x[0], K.goPos.y, K.goPos.z - x[1]);
    go.holder.rotation.set(0, x[2], 0);
    go.holder.updateMatrixWorld(true);
    if (Math.abs(om) > 1e-6) {
      const ix = x[0] - Math.sin(x[2]) * v / om, iy = x[1] + Math.cos(x[2]) * v / om;
      K.icr.position.set(K.goPos.x + ix, 0.03, K.goPos.z - iy);
      K.icr.visible = Math.hypot(v / om) < 3;
    } else K.icr.visible = false;
    if (api.running) K.path.add(new api.three.Vector3(K.goPos.x + x[0], 0.004, K.goPos.z - x[1]));
  },

  readouts(api, s) {
    const K = api.keep, f = (x, n) => api.fmt(x, n);
    if (!K.prints) return [];
    if (api.scene === "turn") {
      this.poseGo2(api, s);
      const v = api.p.v, om = api.p.om, Tst = this.BETA * this.TC;
      const st = this.LEGS.map((leg) => { const a = this.stancePos(leg, 0, v, om), b = this.stancePos(leg, 1, v, om); return Math.hypot(b[0] - a[0], b[1] - a[1]); });
      const R = Math.abs(om) > 1e-6 ? v / om : Infinity;
      return [[["转弯半径 R = v/ω", "turn radius R = v/ω"], Number.isFinite(R) ? f(R, 3) + " m" : api.T("直行", "straight")],
              [["支撑行程 FL, FR, RL, RR", "stance strokes FL, FR, RL, RR"], st.map((x) => f(x, 3)).join(", ") + " m"],
              [["直行时的支撑行程 vβt_c", "straight-line stroke vβt_c"], f(v * Tst, 3) + " m"],
              [["时间", "time"], f(s.t || 0, 2) + " s"]];
    }
    const r = K.res;
    if (!r) return [[["全身逆运动学", "whole-body IK"], api.T("求解中…", "solving…")]];
    if (r.ef < 1e-4 && r.eh < 0.005) {
      if (api.p.comt > 0.5 && r.mg > 0.03 && Math.abs(api.p.fx - 0.4) < 0.015 && Math.abs(api.p.fz - 0.35) < 0.015) api.done("reach");
      if (api.p.comt < 0.5 && r.mg < 0) api.done("fall");
    }
    return [[["质心任务", "CoM task"], api.p.comt > 0.5 ? api.T("开", "on") : api.T("关", "off")],
            [["脚的误差、手的误差", "foot error, hand error"], `${f(r.ef * 1000, 2)}, ${f(r.eh * 1000, 1)} mm`],
            [["质心 (x, y, z)", "CoM (x, y, z)"], `(${f(r.c[0], 3)}, ${f(r.c[1], 3)}, ${f(r.c[2], 3)}) m`],
            [["稳定裕度 S", "margin S"], f(r.mg * 1000, 0) + " mm" + (r.mg > 0 ? "" : api.T("（质心在支撑区外：会倒）", " (CoM outside the support: falls)"))],
            [["骨盆位置", "pelvis position"], `(${f(K.pb[0], 3)}, ${f(K.pb[1], 3)}, ${f(K.pb[2], 3)}) m`]];
  },

  draw(api, s) {
    const m = api.m, sc = api.scene, K = api.keep;
    if (!K.prints) return;
    m["B-LEG-GO2"].holder.visible = sc === "turn";
    K.icr.visible = K.icr.visible && sc === "turn";
    m["B-HUM-G1"].holder.visible = sc === "reach";
    [K.box, K.cball, K.supp].forEach((o) => { o.visible = sc === "reach"; });
    if (sc !== "turn") K.prints.forEach((d) => { d.visible = false; });
    if (K.shown !== sc) {
      K.shown = sc;
      if (sc === "turn") { const T = api.three, b = new T.Box3(new T.Vector3(-0.5, 0, -1.2), new T.Vector3(1.0, 0.4, 0.5)); m.fTurn = { entry: { robot: {} }, holder: { visible: false }, box: () => b.clone() }; api.view(20, 50, 0.9, m.fTurn); }
      else api.view(70, 12, 0.85, m["B-HUM-G1"]);
    }
    if (sc === "turn") { this.poseGo2(api, s); return; }
    const key = `${api.p.comt}`;
    if (K.key !== key) { this.resetG1(api); K.key = key; }
    const done = K.res && K.res.ef < 1e-8 && K.res.eh < 1e-6 && (api.p.comt < 0.5 || K.res.ec < 1e-6);
    for (let i = 0; i < (done ? 1 : 4); i++) K.res = this.wbStep(api);
    this.placeG1(api);
    K.box.scale.set(1, Math.max(0.01, api.p.fz - 0.02), 1);
    K.box.position.set(api.p.fx + 0.02, (api.p.fz - 0.02) / 2, 0.2);
    K.cball.position.set(K.res.c[0], 0.01, -K.res.c[1]);
    K.cball.material.color.setHex(K.res.mg > 0 ? 0x2ca02c : 0xd62728);
    api.readout();
  },
});
