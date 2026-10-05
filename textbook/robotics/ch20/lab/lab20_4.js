// 实验 20.4 调步态参数，看是否静态稳定（配 20.4 节）。零件库 Go2 与 G1 三维模型。
// 场景“Go2 爬行”：机身以 v 前进（三维中机身不动、地面上的足迹与支撑多边形向后移动），t_c = 2 s，落脚点为中性点；
//   步态 0 = 爬行（左后、左前、右后、右前，相位 0、1/4、1/2、3/4），1 = 小跑。机身侧摆 y_b = −A cos(2πt/t_c)。
//   各腿由侧视平面两连杆求关节角（足端的侧向位置随机身侧摆变化时，用实验 20.1 的完整逆解）。
//   质心：按 MJCF 的连杆质量与连杆坐标系中的质心位置（程序 20.4.1 的 GO2_INERTIAL），由模型各连杆的世界矩阵算出；
//   支撑多边形为着地足端的凸包，静态稳定裕度按定义 20.4.4（内为正、外为负，退化时为负）。
// 生活场景“单脚站立”：G1 两脚不动，骨盆左移 dy、下降 0.03 m（数值逆解同实验 20.2）；“抬起右脚”滑块为 1 时只剩左脚支撑。
//   质心按 G1 各连杆的质量与质心位置（程序 20.4.1 的 G1_INERTIAL）。
WQ.lab({
  title: ["实验 20.4 调步态参数，看是否静态稳定", "Lab 20.4 Tune the gait: is it statically stable?"],
  goal: ["让 Go2 爬行，改变占地系数和机身侧摆，看质心的投影是否始终留在支撑多边形内、裕度最小是多少；再让仿人机器人单脚站立，看骨盆要移多远。",
         "Let Go2 crawl and change the duty factor and body sway; see whether the CoM projection stays inside the support polygon and how small the margin gets; then make the humanoid stand on one foot and see how far the pelvis must move."],
  view: "3d",
  models: ["B-LEG-GO2", "B-HUM-G1"],
  scenes: [
    { id: "crawl", robot: true, name: ["Go2 爬行", "Go2 crawling"], hide: ["dy", "lift"],
      problem: { title: ["机器人问题：一次抬一条腿，会不会倒", "Robot problem: lifting one leg at a time, does it tip over"],
                 text: ["按“开始”走一个周期。绿色多边形是支撑多边形，红球是质心的投影；测量区给出此刻的裕度和一个周期中的最小裕度。",
                        "Press Start for one cycle. The green polygon is the support polygon, the red ball the CoM projection; the readouts give the margin now and its minimum over the cycle."] } },
    { id: "one", name: ["生活：单脚站立", "Everyday: standing on one foot"], hide: ["gait", "beta", "A"],
      problem: { title: ["生活中的例子：人怎样单脚站稳", "Everyday example: how a person stands on one foot"],
                 text: ["G1 代表人。先把骨盆向左移，再抬起右脚：质心的投影必须已经在左脚底上方。",
                        "G1 stands for a person. Move the pelvis left first, then lift the right foot: the CoM must already be above the left sole."] } },
  ],
  params: [
    { id: "gait", name: ["步态：0 爬行 1 小跑", "gait: 0 crawl 1 trot"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "beta", name: ["占地系数 β", "duty factor β"], min: 0.5, max: 0.95, step: 0.01, value: 0.85, digits: 2 },
    { id: "A", name: ["机身侧摆幅度 A", "body sway A"], min: 0, max: 0.05, step: 0.005, value: 0.02, unit: "m", digits: 3 },
    { id: "dy", name: ["G1 骨盆左移", "G1 pelvis left"], min: 0, max: 0.16, step: 0.005, value: 0, unit: "m", digits: 3 },
    { id: "lift", name: ["抬起右脚（0/1）", "lift right foot (0/1)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始（走一个周期）", "Start (one cycle)"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "edge", robot: true, text: ["取 β = 0.75 走一个周期：换腿的瞬间裕度降到零附近（不大于 1 mm）。", "Walk one cycle with β = 0.75: at a leg change the margin drops to about zero (at most 1 mm)."],
      demo: { scene: "crawl", set: { gait: 0, beta: 0.75, A: 0 }, press: ["start"], wait: 80 } },
    { id: "safe", robot: true, text: ["调 β 和 A，使一个周期中的最小裕度不小于 5 mm。", "Tune β and A so that the smallest margin over a cycle is at least 5 mm."],
      demo: { scene: "crawl", set: { gait: 0, beta: 0.9, A: 0.02 }, press: ["start"], wait: 80 } },
    { id: "trot", robot: true, text: ["改为小跑走一个周期：支撑多边形退化为线段，静态稳定裕度始终不大于零。", "Switch to trotting for a cycle: the support polygon collapses to a segment and the margin is never positive."],
      demo: { scene: "crawl", set: { gait: 1, beta: 0.5, A: 0 }, press: ["start"], wait: 80 } },
    { id: "one", text: ["先把 G1 的骨盆左移，再抬起右脚，单脚站稳（裕度大于 1 cm）。", "Move G1's pelvis left first, then lift the right foot and stand on one foot (margin above 1 cm)."],
      demo: { scene: "one", set: { dy: 0.145, lift: 1 }, press: [], wait: 8 } },
  ],
  think: ["为什么 β = 0.75 时，无论机身怎样侧摆，最小裕度都不可能大于零？",
          "Why can the smallest margin never be positive at β = 0.75, however the body sways?"],

  AX: 0.1934, AY: 0.0465, DY: 0.0955, L1: 0.213, L2: 0.213, HH: 0.2648, RF: 0.022, V: 0.1, TC: 2.0, HS: 0.05,
  LEGS: ["FL", "FR", "RL", "RR"],
  PH: [{ RL: 0, FL: 0.25, RR: 0.5, FR: 0.75 }, { RL: 0, FR: 0, FL: 0.5, RR: 0.5 }],
  GO2M: { base: [[0.021112, 0, -0.005366], 6.921], FL_hip: [[-0.0054, 0.00194, -0.000105], 0.678], FL_thigh: [[-0.00374, -0.0223, -0.0327], 1.152], FL_calf: [[0.00629595, -0.000622121, -0.141417], 0.241352],
    FR_hip: [[-0.0054, -0.00194, -0.000105], 0.678], FR_thigh: [[-0.00374, 0.0223, -0.0327], 1.152], FR_calf: [[0.00629595, 0.000622121, -0.141417], 0.241352],
    RL_hip: [[0.0054, 0.00194, -0.000105], 0.678], RL_thigh: [[-0.00374, -0.0223, -0.0327], 1.152], RL_calf: [[0.00629595, -0.000622121, -0.141417], 0.241352],
    RR_hip: [[0.0054, -0.00194, -0.000105], 0.678], RR_thigh: [[-0.00374, 0.0223, -0.0327], 1.152], RR_calf: [[0.00629595, 0.000622121, -0.141417], 0.241352] },
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

  // ---------------- 几何
  hull(P) {
    const pts = P.map((p) => [p[0], p[1]]).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    if (pts.length < 3) return pts;
    const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]), lo = [], up = [];
    pts.forEach((p) => { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); });
    pts.slice().reverse().forEach((p) => { while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], p) <= 0) up.pop(); up.push(p); });
    return lo.slice(0, -1).concat(up.slice(0, -1));
  },
  margin(poly, c) {
    const segd = (a, b) => { const e = [b[0] - a[0], b[1] - a[1]], L2 = e[0] * e[0] + e[1] * e[1] || 1e-12, t = Math.max(0, Math.min(1, ((c[0] - a[0]) * e[0] + (c[1] - a[1]) * e[1]) / L2));
      return Math.hypot(c[0] - a[0] - t * e[0], c[1] - a[1] - t * e[1]); };
    if (poly.length === 1) return -Math.hypot(c[0] - poly[0][0], c[1] - poly[0][1]);
    if (poly.length === 2) return -segd(poly[0], poly[1]);
    let inside = true, dmin = 1e9;
    for (let k = 0; k < poly.length; k++) {
      const a = poly[k], b = poly[(k + 1) % poly.length], e = [b[0] - a[0], b[1] - a[1]], L = Math.hypot(e[0], e[1]);
      const s = ((c[0] - a[0]) * e[1] - (c[1] - a[1]) * e[0]) / L;   // 外法向上的分量（逆时针多边形）
      if (s > 0) inside = false;
      dmin = Math.min(dmin, segd(a, b));
    }
    return inside ? dmin : -dmin;
  },
  com(api, h, table) {   // 质心（世界坐标 → 模型坐标：(x, −z, y)）
    const T = api.three;
    let m = 0, x = 0, y = 0, z = 0;
    h.root.updateMatrixWorld(true);
    Object.entries(table).forEach(([name, [c, mk]]) => {
      const n = h.nodes[name];
      if (!n) return;
      const p = new T.Vector3(c[0], c[1], c[2]).applyMatrix4(n.matrixWorld);
      x += mk * p.x; y += mk * p.y; z += mk * p.z; m += mk;
    });
    return [x / m, -z / m, y / m];
  },

  // ---------------- Go2 爬行
  ik(leg, p) {   // 实验 20.1 的逆解，p 为足端在 {b} 中的位置
    const sx = leg[0] === "F" ? 1 : -1, sy = leg[1] === "L" ? 1 : -1, d = sy * this.DY, l1 = this.L1, l2 = this.L2;
    const r = [p[0] - sx * this.AX, p[1] - sy * this.AY, p[2]], rho2 = r[1] * r[1] + r[2] * r[2];
    if (rho2 < this.DY * this.DY) return null;
    const zp = -Math.sqrt(rho2 - this.DY * this.DY), xp = r[0], D = Math.hypot(xp, zp), c3 = (D * D - l1 * l1 - l2 * l2) / (2 * l1 * l2);
    if (c3 > 1 || c3 < -1) return null;
    const t3 = -Math.acos(c3), t2 = Math.atan2(-xp, -zp) - Math.atan2(l2 * Math.sin(t3), l1 + l2 * Math.cos(t3)), t1 = Math.atan2(r[2], r[1]) - Math.atan2(zp, d);
    return [t1, t2, t3];
  },
  state(api, t) {
    const p = api.p, g = Math.round(p.gait), beta = g === 1 ? 0.5 : p.beta, A = g === 1 ? 0 : p.A, tc = g === 1 ? 0.5 : this.TC, v = g === 1 ? 0.5 : this.V;
    const ell = v * beta * tc, Ls = v * tc, body = [v * t, -A * Math.cos(2 * Math.PI * t / tc)], feet = {}, stance = [];
    this.LEGS.forEach((leg) => {
      const ph = this.PH[g][leg], u = (((t / tc - ph) % 1) + 1) % 1, ttd = t - u * tc, hx = (leg[0] === "F" ? 1 : -1) * this.AX, hy = (leg[1] === "L" ? 1 : -1) * (this.AY + this.DY);
      const x0 = hx + v * ttd + ell / 2;
      if (u < beta) { feet[leg] = [x0, hy, this.RF]; stance.push(leg); }
      else {
        const tau = (u - beta) / (1 - beta), s = tau - Math.sin(2 * Math.PI * tau) / (2 * Math.PI);
        feet[leg] = [x0 + Ls * s, hy, this.RF + this.HS * (1 - Math.cos(2 * Math.PI * tau)) / 2];
      }
    });
    return { feet, stance, body, tc };
  },

  setup3d(api, keep) {
    const T = api.three, go = api.m["B-LEG-GO2"], g1 = api.m["B-HUM-G1"];
    go.place(0, 0);
    g1.place(0, 0);
    keep.goPos = go.holder.position.clone();
    keep.poly = new T.LineLoop(new T.BufferGeometry().setFromPoints([new T.Vector3(), new T.Vector3(), new T.Vector3()]), new T.LineBasicMaterial({ color: 0x2ca02c }));
    api.st.scene.add(keep.poly);
    keep.ball = new T.Mesh(new T.SphereGeometry(0.018, 16, 12), new T.MeshStandardMaterial({ color: 0xd62728 }));
    api.st.scene.add(keep.ball);
    keep.trail = api.trace(0xd62728);
    // G1：站立时两脚相对骨盆的位姿；初值膝稍弯
    g1.set({ left_knee_joint: 0, right_knee_joint: 0 });
    keep.g1pos = g1.holder.position.clone();
    keep.g1t = { left: this.relPose(api, g1, "left"), right: this.relPose(api, g1, "right") };
    keep.g1q = { left: [-0.2, 0, 0, 0.4, -0.2, 0], right: [-0.2, 0, 0, 0.4, -0.2, 0] };
    keep.sole0 = { left: this.SOLE.map((q) => g1.point("left_ankle_roll_link", q)), right: this.SOLE.map((q) => g1.point("right_ankle_roll_link", q)) };
    keep.shown = null;
  },
  reset(api, s) { s.t = 0; s.min = null; if (api.keep && api.keep.trail) api.keep.trail.clear(); },
  update(dt, api, s) {
    if (api.scene !== "crawl") { api.stop(); return; }
    const tc = Math.round(api.p.gait) === 1 ? 0.5 : this.TC;
    s.t += dt;
    if (s.t >= tc) {
      // 走完一个周期：按 240 个等间隔时刻重算一遍裕度，取最小值（与帧率无关）
      let mn = 1e9;
      for (let k = 0; k < 240; k++) mn = Math.min(mn, this.poseGo2(api, { t: tc * k / 240 }).mg);
      s.t = tc;
      s.min = mn;
      api.stop();
      const p = api.p, g = Math.round(p.gait);
      if (g === 0 && p.beta <= 0.755 && mn !== null && mn <= 0.001) api.done("edge");
      if (g === 0 && mn !== null && mn >= 0.005) api.done("safe");
      if (g === 1 && mn !== null && mn <= 0) api.done("trot");
    }
  },

  poseGo2(api, s) {
    const go = api.m["B-LEG-GO2"], K = api.keep, T = api.three, st = this.state(api, s.t || 0), o = Object.assign({}, go.entry.rest);
    this.LEGS.forEach((leg) => {
      const f = st.feet[leg], pb = [f[0] - st.body[0], f[1] - st.body[1], f[2] - (this.HH + this.RF)], q = this.ik(leg, pb);
      if (q) { o[leg + "_hip_joint"] = q[0]; o[leg + "_thigh_joint"] = q[1]; o[leg + "_calf_joint"] = q[2]; }
    });
    go.set(o);
    // 机身在三维中不前进（“跑步机”），只侧摆；足迹与多边形相对机身画出
    go.holder.position.set(K.goPos.x, K.goPos.y, K.goPos.z - st.body[1]);
    go.holder.updateMatrixWorld(true);
    const c = this.com(api, go, this.GO2M);               // 质心（模型坐标，含侧摆）
    const poly = this.hull(st.stance.map((l) => st.feet[l]).map((f) => [f[0] - st.body[0], f[1]]));
    const cxy = [c[0] - K.goPos.x, c[1]];
    const mg = this.margin(poly, cxy);
    const pts = (poly.length >= 2 ? poly : [[0, 0], [0, 0]]).map((p) => new T.Vector3(p[0] + K.goPos.x, 0.004, -p[1]));
    K.poly.geometry.dispose();
    K.poly.geometry = new T.BufferGeometry().setFromPoints(pts);       // 顶点数会变（三角形、四边形），每次换一个几何体
    K.poly.material.color.setHex(mg > 0.001 ? 0x2ca02c : mg > -0.001 ? 0xe8b400 : 0xd62728);
    K.ball.position.set(c[0], 0.01, -c[1]);
    return { mg, st };
  },
  // ---------------- G1（与实验 20.2 相同的数值逆解）
  G1L: { left: ["left_hip_pitch_joint", "left_hip_roll_joint", "left_hip_yaw_joint", "left_knee_joint", "left_ankle_pitch_joint", "left_ankle_roll_joint"],
         right: ["right_hip_pitch_joint", "right_hip_roll_joint", "right_hip_yaw_joint", "right_knee_joint", "right_ankle_pitch_joint", "right_ankle_roll_joint"] },
  relPose(api, g, side) {
    const T = api.three, pel = g.nodes.pelvis, an = g.nodes[side + "_ankle_roll_link"];
    g.root.updateMatrixWorld(true);
    const e = new T.Matrix4().copy(pel.matrixWorld).invert().multiply(an.matrixWorld).elements;
    return { R: [[e[0], e[4], e[8]], [e[1], e[5], e[9]], [e[2], e[6], e[10]]], p: [e[12], e[13], e[14]] };
  },
  err6(cur, tgt) {
    const A = tgt.R, B = cur.R, E = [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[i][0] * B[j][0] + A[i][1] * B[j][1] + A[i][2] * B[j][2]));
    return [(E[2][1] - E[1][2]) / 2, (E[0][2] - E[2][0]) / 2, (E[1][0] - E[0][1]) / 2, tgt.p[0] - cur.p[0], tgt.p[1] - cur.p[1], tgt.p[2] - cur.p[2]];
  },
  g1leg(api, g, side, tgt, q) {
    const names = this.G1L[side], set = () => { const o = {}; names.forEach((n, i) => { o[n] = q[i]; }); g.set(o); };
    for (let it = 0; it < 30; it++) {
      set();
      const e = this.err6(this.relPose(api, g, side), tgt);
      if (Math.hypot(...e) < 1e-8) break;
      const J = [[], [], [], [], [], []], h = 1e-5;
      for (let k = 0; k < 6; k++) { q[k] += h; set(); const ek = this.err6(this.relPose(api, g, side), tgt); for (let i = 0; i < 6; i++) J[i][k] = (e[i] - ek[i]) / h; q[k] -= h; }
      const dq = api.la.mv(api.la.pinv(J, 1e-9), e);
      for (let k = 0; k < 6; k++) q[k] += dq[k];
    }
    set();
    const e = this.err6(this.relPose(api, g, side), tgt);
    return { ok: Math.hypot(...e) < 1e-5 && names.every((n, i) => q[i] >= g.joints[n].lower - 1e-6 && q[i] <= g.joints[n].upper + 1e-6), q };
  },
  poseG1(api) {
    const g = api.m["B-HUM-G1"], K = api.keep, p = api.p, T = api.three, dz = 0.03, tgt = {};
    ["left", "right"].forEach((side) => { const t0 = K.g1t[side]; tgt[side] = { R: t0.R, p: [t0.p[0], t0.p[1] - p.dy, t0.p[2] + dz] }; });
    const rl = this.g1leg(api, g, "left", tgt.left, K.g1q.left.slice());
    if (rl.ok) K.g1q.left = rl.q;
    const lifted = p.lift > 0.5;
    if (lifted) { tgt.right.p[2] += 0.06; tgt.right.p[0] += 0.03; }
    const rr = this.g1leg(api, g, "right", tgt.right, K.g1q.right.slice());
    if (rr.ok) K.g1q.right = rr.q;
    const o = {};
    ["left", "right"].forEach((side) => this.G1L[side].forEach((n, i) => { o[n] = K.g1q[side][i]; }));
    g.set(o);
    g.holder.position.set(K.g1pos.x, K.g1pos.y - dz, K.g1pos.z - p.dy);
    g.holder.updateMatrixWorld(true);
    const c = this.com(api, g, this.G1M);
    const feet = lifted ? K.sole0.left : K.sole0.left.concat(K.sole0.right);
    const poly = this.hull(feet.map((v) => [v.x, -v.z]));
    const mg = this.margin(poly, [c[0], c[1]]);
    K.poly.geometry.dispose();
    K.poly.geometry = new T.BufferGeometry().setFromPoints(poly.map((q) => new T.Vector3(q[0], 0.004, -q[1])));
    K.poly.material.color.setHex(mg > 0.001 ? 0x2ca02c : 0xd62728);
    K.ball.position.set(c[0], 0.01, -c[1]);
    return { mg, ok: rl.ok && rr.ok, lifted };
  },

  readouts(api, s) {
    const K = api.keep, f = (x, n) => api.fmt(x, n);
    if (!K.poly) return [];
    if (api.scene === "crawl") {
      const r = this.poseGo2(api, s);
      if (api.running) s.min = s.min === null ? r.mg : Math.min(s.min, r.mg);
      return [[["时间 t", "time t"], f(s.t || 0, 2) + " s"],
              [["着地的脚", "feet down"], r.st.stance.join(" ")],
              [["此刻的稳定裕度 S", "margin S now"], f(r.mg * 1000, 1) + " mm"],
              [["本周期最小裕度", "smallest margin this cycle"], s.min === null ? api.T("按“开始”", "press Start") : f(s.min * 1000, 1) + " mm"],
              [["判断", "verdict"], r.mg > 0.001 ? api.T("静态稳定", "statically stable") : r.mg > -0.001 ? api.T("临界（在边界上）", "marginal (on the edge)") : api.T("此刻若停下会倒", "would tip over if frozen now")]];
    }
    const r = this.poseG1(api);
    if (r.ok && r.lifted && r.mg > 0.01) api.done("one");
    return [[["骨盆左移", "pelvis moved left"], f(api.p.dy, 3) + " m"],
            [["支撑", "support"], r.lifted ? api.T("左脚单脚", "left foot only") : api.T("双脚", "both feet")],
            [["稳定裕度 S", "margin S"], f(r.mg * 1000, 1) + " mm"],
            [["判断", "verdict"], !r.ok ? api.T("关节超限", "joint limit reached") : r.mg > 0 ? api.T("站得住", "stands") : api.T("会倒（质心在支撑多边形外）", "falls (CoM outside the support polygon)")]];
  },

  draw(api, s) {
    const m = api.m, sc = api.scene, K = api.keep;
    if (!K.poly) return;
    m["B-LEG-GO2"].holder.visible = sc === "crawl";
    m["B-HUM-G1"].holder.visible = sc === "one";
    if (K.shown !== sc) { K.shown = sc; api.view(sc === "crawl" ? 25 : 30, sc === "crawl" ? 55 : 35, 0.8, sc === "crawl" ? m["B-LEG-GO2"] : m["B-HUM-G1"]); }
    if (api.running) { api.readout(); if (sc === "crawl") K.trail.add(K.ball.position.clone()); }
  },
});
