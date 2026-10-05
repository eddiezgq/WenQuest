// 实验 16.4 可操作度椭球：托盘放在哪里（配 16.4 节）。
// 机器人场景：零件库的 UR5e，法兰盘保持 θ* = (30°, −60°, 90°, −120°, −90°, 45°) 处的姿态（竖直朝下）。
// 法兰盘中心放在经过 θ* 的那条竖直半平面内：到基座轴线的水平距离 ρ、高度 z（滑块）。逆解用阻尼牛顿法
// 从 θ* 出发沿直线延拓（与程序 16.4.1 的解析解同一支）。三种椭球（16.4 节）：
//   0 姿态保持的线速度椭球 {ṗ : ‖G ṗ‖ ≤ 1}，G = J_g⁻¹ 的后三列（定理 16.4.2）；
//   1 J_v（J_g 的后三行）的线速度椭球（定理 16.4.1），姿态可以随意变；
//   2 角速度椭球（J_ω = J_g 的前三行）。
// 椭球画在法兰盘中心：线速度椭球 1 m/s（每 rad/s）画成 0.3 m，角速度椭球 1 rad/s（每 rad/s）画成 0.1 m。
// 生活场景：人坐在桌前，上臂 0.30 m、前臂到手 0.32 m 在桌面上方的水平面内转动，肘部弯曲角 θ₂ 可调；
//   手的可操作度 w = L₁ L₂ |sin θ₂|（式 (2.4.8)）。
WQ.lab({
  title: ["实验 16.4 可操作度椭球：托盘放在哪里", "Lab 16.4 The manipulability ellipsoid: where to put the tray"],
  goal: ["把 UR5e 的法兰盘放到不同的位置，比较三种椭球，找出托盘的最佳位置；看清可操作度、最小半轴和条件数各回答什么问题。",
         "Put the UR5e flange at different places, compare the three ellipsoids and find the best place for the tray; see what the manipulability, the smallest semi-axis and the condition number each tell you."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 的可操作度椭球", "Manipulability ellipsoids of the UR5e"], hide: ["elbow"],
      problem: { title: ["机器人问题：工具竖直朝下抓取齿轮，托盘放在哪里最灵活", "Robot problem: picking gears with the tool pointing down, where is the arm most agile"],
                 text: ["拖动 ρ 和 z，法兰盘保持竖直朝下。橙色是所选的椭球。测量区给出三个半轴、可操作度 w、条件数 κ 和 θ₃，以及当前高度上姿态保持椭球的最佳位置。",
                        "Drag ρ and z; the flange keeps pointing down. The orange body is the chosen ellipsoid. The readouts give its three semi-axes, the manipulability w, the condition number κ and θ₃, and the best places at the present height for the orientation-held ellipsoid."] } },
    { id: "arm", name: ["人的手臂在书桌上", "A human arm at a desk"], hide: ["rho", "zh", "kind"],
      problem: { title: ["生活中的例子：写字时肘部弯成什么角度", "Everyday example: how far to bend the elbow when writing"],
                 text: ["上臂 0.30 m、前臂到手 0.32 m，在桌面上方的水平面内转动。拖动肘部弯曲角 θ₂，橙色椭圆是手的可操作度椭圆（单位关节速度能产生的手的速度）。",
                        "Upper arm 0.30 m, forearm to hand 0.32 m, moving in a horizontal plane above the desk. Drag the elbow angle θ₂; the orange ellipse is the hand's manipulability ellipse (the hand velocities from unit joint speed)."] } },
  ],
  params: [
    { id: "rho", name: ["法兰盘中心到基座轴线的水平距离 ρ", "horizontal distance ρ of the flange centre from the base axis"], min: 0.2, max: 0.92, step: 0.005, value: 0.665, unit: "m", digits: 3 },
    { id: "zh", name: ["法兰盘中心的高度 z", "height z of the flange centre"], min: 0.05, max: 0.6, step: 0.005, value: 0.235, unit: "m", digits: 3 },
    { id: "kind", name: ["椭球：0 姿态保持 / 1 J_v（姿态可变）/ 2 角速度", "ellipsoid: 0 orientation held / 1 J_v (orientation free) / 2 angular"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "elbow", name: ["肘部弯曲角 θ₂", "elbow angle θ₂"], min: 10, max: 170, step: 1, value: 40, unit: "°", digits: 0 },
  ],
  legend: [{ color: "#e8912d", name: ["所选的椭球", "the chosen ellipsoid"] }],
  tasks: [
    { id: "angw", robot: true, text: ["在 θ* 处（ρ = 0.665 m、z = 0.235 m）显示角速度椭球，验证三个半轴为 √3、√2、1。",
                                      "At θ* (ρ = 0.665 m, z = 0.235 m) show the angular-velocity ellipsoid and check that its semi-axes are √3, √2 and 1."],
      demo: { scene: "ur", set: { rho: 0.665, zh: 0.235, kind: 2 }, press: [], wait: 3 } },
    { id: "bestw", robot: true, text: ["在 z = 0.235 m 的高度上，找出姿态保持时可操作度最大的 ρ（达到最大值的 99% 以上）。",
                                       "At the height z = 0.235 m, find the ρ where the orientation-held manipulability is largest (within 1% of the maximum)."],
      demo: { scene: "ur", set: { zh: 0.235, kind: 0, rho: 0.75 }, press: [], wait: 3 } },
    { id: "edge", robot: true, text: ["把法兰盘伸到 ρ ≥ 0.9 m：姿态保持的椭球最短半轴小于 0.05，而 J_v 的可操作度仍大于 0.1。",
                                      "Stretch the flange to ρ ≥ 0.9 m: the shortest semi-axis of the orientation-held ellipsoid drops below 0.05 while the J_v manipulability stays above 0.1."],
      demo: { scene: "ur", set: { zh: 0.235, kind: 0, rho: 0.9 }, press: [], wait: 3 } },
    { id: "bestk", robot: true, text: ["在 z = 0.235 m 的高度上，找出姿态保持时条件数最小的 ρ（不超过最小值的 1.01 倍）。",
                                       "At the height z = 0.235 m, find the ρ where the orientation-held condition number is smallest (within 1.01 times the minimum)."],
      demo: { scene: "ur", set: { zh: 0.235, kind: 0, rho: 0.46 }, press: [], wait: 3 } },
    { id: "elbow", text: ["生活场景：找出手的可操作度最大的肘部角度（达到最大值的 99.9% 以上）。", "Everyday scene: find the elbow angle with the largest manipulability of the hand (within 0.1% of the maximum)."],
      demo: { scene: "arm", set: { elbow: 90 }, press: [], wait: 3 } },
  ],
  think: ["在任务 2 和任务 4 中，可操作度最大的位置与条件数最小的位置为什么不同？对“各个方向都要走”的抓取任务，你会选哪一个？",
          "Why are the places of largest manipulability (task 2) and smallest condition number (task 4) different? For a picking task that moves in every direction, which would you choose?"],

  // ---------------- UR5e 几何（表 12.1.1）与 SE(3) 运算（同实验 16.1）
  G: { H1: 0.163, W1: 0.138, L1: 0.425, W2: 0.131, L2: 0.392, W3: 0.127, H2: 0.1, W4: 0.1 },
  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  START: [30, -60, 90, -120, -90, 45],
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
  jg(th) {                                        // 几何雅可比的六列 (ω_i, ω_i × (p − q_i))（式 (16.2.3)），以及末端位姿
    const A = this.AX(), T = this.fk(th), cols = [];
    let P = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] };
    for (let i = 0; i < 6; i++) {
      const w = this.mv(P.R, A[i][0]), q = this.act(P, A[i][1]);
      cols.push([...w, ...this.cross(w, this.sub(T.p, q))]);
      P = this.comp(P, this.E(i, th[i]));
    }
    return { cols, T };
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
  logR(R) {                                       // 旋转矩阵的对数（小角度时足够准确）
    const c = Math.max(-1, Math.min(1, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)), a = Math.acos(c);
    const v = [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]];
    return a < 1e-9 ? this.mul(v, 0.5) : this.mul(v, a / (2 * Math.sin(a)));
  },
  newton(th, R0, p, it) {                         // 阻尼牛顿：姿态 R0、位置 p
    for (let k = 0; k < it; k++) {
      const { cols, T } = this.jg(th);
      const e = [...this.logR(this.mm(R0, this.tr(T.R))), ...this.sub(p, T.p)];
      if (Math.hypot(...e) < 1e-12) break;
      const n = cols.map((c) => c.slice()), lam = 1e-8;                 // (J + 0) 的解；接近奇异时加一点阻尼
      const JJt = [0, 1, 2, 3, 4, 5].map((i) => [0, 1, 2, 3, 4, 5].map((j) => n.reduce((s, c) => s + c[i] * c[j], 0) + (i === j ? lam : 0)));
      const y = this.solve(JJt.map((r, j) => JJt.map((rr) => rr[j])), e);
      const d = n.map((c) => c.reduce((s, x, i) => s + x * y[i], 0));
      th = th.map((x, i) => x + d[i]);
    }
    return th;
  },
  az() { if (!this._az) { const p = this.fk(this.START.map((d) => d * Math.PI / 180)).p; this._az = Math.atan2(p[1], p[0]); this._p0 = p; } return this._az; },
  target(rho, z) { const a = this.az(); return [rho * Math.cos(a), rho * Math.sin(a), z]; },
  reach(rho, z) {                                 // 从 θ* 出发沿 (ρ, z) 平面内的直线延拓；返回关节角与残差
    const a = this.az(), p0 = this._p0, r0 = Math.hypot(p0[0], p0[1]), R0 = this.fk(this.START.map((d) => d * Math.PI / 180)).R;
    let th = this.START.map((d) => d * Math.PI / 180);
    const n = Math.max(4, Math.ceil(Math.hypot(rho - r0, z - p0[2]) / 0.01));
    for (let k = 1; k <= n; k++) th = this.newton(th, R0, this.target(r0 + (rho - r0) * k / n, p0[2] + (z - p0[2]) * k / n), 6);
    th = this.newton(th, R0, this.target(rho, z), 20);
    const T = this.fk(th), res = this.norm(this.sub(T.p, this.target(rho, z))) + this.norm(this.logR(this.mm(R0, this.tr(T.R))));
    return { th, ok: res < 1e-7 };
  },
  ell(api, th, kind) {                            // 椭球的半轴长（从大到小）与方向（列）
    const { cols } = this.jg(th), LA = api.la;
    if (kind === 0) {
      const G = [0, 1, 2, 3, 4, 5].map(() => [0, 0, 0]);
      for (let k = 0; k < 3; k++) {
        const e = [0, 0, 0, 0, 0, 0]; e[3 + k] = 1;
        const x = this.solve(cols, e); x.forEach((v, i) => { G[i][k] = v; });
      }
      const { s, V } = LA.svd(G), ax = s.map((x) => 1 / Math.max(x, 1e-12));
      const order = [0, 1, 2].sort((i, j) => ax[j] - ax[i]);
      return { a: order.map((i) => ax[i]), D: order.map((i) => [V[0][i], V[1][i], V[2][i]]) };
    }
    const rows = kind === 1 ? [3, 4, 5] : [0, 1, 2], Jm = rows.map((r) => cols.map((c) => c[r]));
    const { U, s } = LA.svd(Jm);
    return { a: s, D: [0, 1, 2].map((i) => [U[0][i], U[1][i], U[2][i]]) };
  },
  scan(api, z) {                                  // 当前高度上沿 ρ 扫描：姿态保持椭球的可操作度最大值、条件数最小值
    if (this._scan && this._scan.z === z) return this._scan;
    const a = this.az(), R0 = this.fk(this.START.map((d) => d * Math.PI / 180)).R, r0 = Math.hypot(this._p0[0], this._p0[1]);
    let best = { z, wmax: 0, rw: 0, kmin: Infinity, rk: 0 };
    const start = this.reach(r0, z);
    if (!start.ok) { this._scan = best; return best; }
    [1, -1].forEach((dir) => {
      let th = start.th;
      for (let r = r0; r <= 0.92 && r >= 0.2; r += dir * 0.0025) {
        th = this.newton(th, R0, this.target(r, z), 8);
        const T = this.fk(th);
        if (this.norm(this.sub(T.p, this.target(r, z))) > 1e-7) break;
        const e = this.ell(api, th, 0), w = e.a[0] * e.a[1] * e.a[2], k = e.a[0] / e.a[2];
        if (w > best.wmax) { best.wmax = w; best.rw = r; }
        if (k < best.kmin) { best.kmin = k; best.rk = r; }
      }
    });
    this._scan = best;
    return best;
  },

  reset(api, s) {
    s.ready = false;
    if (api.scene === "arm") {
      s.el = api.p.elbow * Math.PI / 180;
      const l1 = 0.3, l2 = 0.32;
      s.w = l1 * l2 * Math.abs(Math.sin(s.el)); s.wmax = l1 * l2;
      s.ready = true; return;
    }
    const r = this.reach(api.p.rho, api.p.zh);
    s.th = r.th; s.ok = r.ok;
    if (!r.ok) return;
    const e = this.ell(api, s.th, api.p.kind);
    s.e = e; s.w = e.a[0] * e.a[1] * e.a[2]; s.k = e.a[0] / e.a[2];
    s.held = this.ell(api, s.th, 0); s.jv = this.ell(api, s.th, 1);
    s.p = this.fk(s.th).p;
    s.best = this.scan(api, api.p.zh);
    s.ready = true;
  },
  readouts(api, s) {
    if (api.scene === "arm") {
      if (s.ready && s.w >= 0.999 * s.wmax) api.done("elbow");
      const l1 = 0.3, l2 = 0.32, c = Math.cos(s.el || 0), sn = Math.sin(s.el || 0);
      // 2R 臂（肩角取 0）末端雅可比的奇异值：J Jᵀ 的特征值
      const a = l1 * l1 + l2 * l2 + 2 * l1 * l2 * c, b = l2 * l2, d = l2 * (l1 * c + l2);
      const tr = a + b, det = a * b - d * d, disc = Math.sqrt(Math.max(0, tr * tr / 4 - det));
      const s1 = Math.sqrt(tr / 2 + disc), s2 = Math.sqrt(Math.max(0, tr / 2 - disc));
      return [[["肘部弯曲角 θ₂", "elbow angle θ₂"], api.p.elbow.toFixed(0) + "°"],
              [["椭圆的半轴", "semi-axes of the ellipse"], s1.toFixed(4) + ", " + s2.toFixed(4) + " m"],
              [["可操作度 w = L₁L₂|sin θ₂|", "manipulability w = L₁L₂|sin θ₂|"], (s.w || 0).toFixed(5) + " m²"],
              [["w / w_max", "w / w_max"], ((s.w || 0) / 0.096).toFixed(4)],
              [["条件数 κ", "condition number κ"], (s2 > 1e-9 ? s1 / s2 : Infinity).toFixed(3)]];
    }
    if (!s.ok) return [[["状态", "status"], api.T("够不着：减小 ρ 或改变 z", "out of reach: reduce ρ or change z")]];
    const kinds = [api.T("姿态保持的线速度椭球", "orientation-held velocity ellipsoid"), api.T("J_v 的线速度椭球（姿态可变）", "J_v velocity ellipsoid (orientation free)"), api.T("角速度椭球", "angular-velocity ellipsoid")];
    const atStar = Math.abs(api.p.rho - 0.6656) < 0.003 && Math.abs(api.p.zh - 0.2351) < 0.003, z0 = Math.abs(api.p.zh - 0.2351) < 0.006;
    const e = s.e, rt3 = Math.sqrt(3), rt2 = Math.sqrt(2);
    if (api.p.kind === 2 && atStar && Math.abs(e.a[0] - rt3) < 0.01 && Math.abs(e.a[1] - rt2) < 0.01 && Math.abs(e.a[2] - 1) < 0.01) api.done("angw");
    const wh = s.held.a[0] * s.held.a[1] * s.held.a[2], kh = s.held.a[0] / s.held.a[2], wv = s.jv.a[0] * s.jv.a[1] * s.jv.a[2];
    if (api.p.kind === 0 && z0 && s.best.wmax > 0 && wh >= 0.99 * s.best.wmax) api.done("bestw");
    if (api.p.kind === 0 && z0 && s.best.kmin < Infinity && kh <= 1.01 * s.best.kmin) api.done("bestk");
    if (z0 && api.p.rho >= 0.9 && s.held.a[2] < 0.05 && wv > 0.1) api.done("edge");
    const unit = api.p.kind === 2 ? "" : " m";
    return [[["椭球", "ellipsoid"], kinds[api.p.kind]],
            [["三个半轴", "three semi-axes"], e.a.map((x) => x.toFixed(4)).join(", ") + unit],
            [["可操作度 w", "manipulability w"], s.w.toFixed(5) + (api.p.kind === 2 ? "" : " m³")],
            [["条件数 κ", "condition number κ"], s.k.toFixed(3)],
            [["J_v 的可操作度（对照）", "J_v manipulability (for comparison)"], wv.toFixed(4) + " m³"],
            [["θ₃", "θ₃"], (s.th[2] * 180 / Math.PI).toFixed(1) + "°"],
            [["本高度上姿态保持：w 最大 / κ 最小处", "orientation held at this height: largest w / smallest κ at"],
             s.best.wmax > 0 ? "ρ ≈ " + s.best.rw.toFixed(3) + " m / " + s.best.rk.toFixed(3) + " m" : "—"]];
  },

  // ---------------- 三维
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    arm.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    const mat = new T.MeshStandardMaterial({ color: 0xe8912d, transparent: true, opacity: 0.45, depthWrite: false });
    keep.ell = new T.Mesh(new T.SphereGeometry(1, 32, 20), mat); keep.ell.matrixAutoUpdate = false; G.add(keep.ell);
    keep.wire = new T.Mesh(new T.SphereGeometry(1, 16, 10), new T.MeshBasicMaterial({ color: 0xb35f00, wireframe: true, transparent: true, opacity: 0.35 }));
    keep.wire.matrixAutoUpdate = false; G.add(keep.wire);
    keep.axes = new T.AxesHelper(0.15); G.add(keep.axes);
    // 托盘（示意）
    keep.tray = new T.Mesh(new T.BoxGeometry(0.16, 0.12, 0.01), new T.MeshStandardMaterial({ color: 0x8c959f })); G.add(keep.tray);
    // 生活场景：书桌、躯干、上臂、前臂、手（在 {s} 中 (1.6, 6, 0) 处）
    const H = new T.Group(); H.position.set(1.6, 6.0, 0); G.add(H); keep.H = H;
    const m = (c) => new T.MeshStandardMaterial({ color: c });
    const desk = new T.Mesh(new T.BoxGeometry(1.2, 0.8, 0.04), m(0xc9a26b)); desk.position.set(0.3, 0.25, 0.72); H.add(desk);
    const torso = new T.Mesh(new T.BoxGeometry(0.22, 0.36, 0.6), m(0x6e7681)); torso.position.set(0, -0.2, 0.95); H.add(torso);
    keep.ua = new T.Mesh(new T.CylinderGeometry(0.045, 0.045, 1, 16), m(0x3f6fb5)); H.add(keep.ua);
    keep.fa = new T.Mesh(new T.CylinderGeometry(0.035, 0.035, 1, 16), m(0x3f6fb5)); H.add(keep.fa);
    keep.hand = new T.Mesh(new T.SphereGeometry(0.045, 16, 12), m(0xe0b089)); H.add(keep.hand);
    keep.hell = new T.Mesh(new T.SphereGeometry(1, 32, 20), mat); keep.hell.matrixAutoUpdate = false; H.add(keep.hell);
    keep.box = () => { G.updateMatrixWorld(true); return new T.Box3().setFromObject(desk).union(new T.Box3().setFromObject(torso)).expandByScalar(0.15); };
    api.m.deskView = { entry: { robot: {} }, holder: { visible: false }, box: () => keep.box() };
  },
  setMat(mesh, c, A) {                            // 椭球：中心 c，半轴矢量 A[0..2]
    mesh.matrix.set(A[0][0], A[1][0], A[2][0], c[0], A[0][1], A[1][1], A[2][1], c[1], A[0][2], A[1][2], A[2][2], c[2], 0, 0, 0, 1);
    mesh.matrixWorldNeedsUpdate = true;
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep, ur = api.scene === "ur";
    if (!k.G) return;
    if (k.shown !== api.scene) {
      k.shown = api.scene;
      if (ur) api.view(35, 25, 0.6, arm); else api.view(-60, 55, 0.9, api.m.deskView);
    }
    arm.holder.visible = ur; k.H.visible = !ur; k.ell.visible = ur && s.ok; k.wire.visible = ur && s.ok; k.tray.visible = ur && s.ok;
    if (ur && s.ready && s.ok) {
      const o = {}; this.J.forEach((n, i) => { o[n] = s.th[i]; }); arm.set(o);
      const sc = api.p.kind === 2 ? 0.1 : 0.3, A = s.e.D.map((d, i) => this.mul(d, Math.max(s.e.a[i], 1e-3) * sc));
      this.setMat(k.ell, s.p, A); this.setMat(k.wire, s.p, A);
      k.tray.position.set(s.p[0], s.p[1], s.p[2] - 0.11);
    }
    if (!ur && s.ready) {
      const l1 = 0.3, l2 = 0.32, sh = [0.12, 0.0, 0.85], a1 = 0.35, a2 = a1 + s.el;
      const el = [sh[0] + l1 * Math.cos(a1), sh[1] + l1 * Math.sin(a1), sh[2]], hd = [el[0] + l2 * Math.cos(a2), el[1] + l2 * Math.sin(a2), sh[2]];
      const place = (m, a, b) => {
        const d = this.sub(b, a), L = this.norm(d);
        m.scale.set(1, L, 1); m.position.set((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2);
        m.quaternion.setFromUnitVectors(new api.three.Vector3(0, 1, 0), new api.three.Vector3(d[0] / L, d[1] / L, d[2] / L));
      };
      place(k.ua, sh, el); place(k.fa, el, hd); k.hand.position.set(...hd);
      // 2R 臂的雅可比（肩角 a1、肘角 θ₂），在桌面平面内的椭圆；画成很扁的椭球，比例 1 m/s 画成 0.3 m
      const J = [[-l1 * Math.sin(a1) - l2 * Math.sin(a2), -l2 * Math.sin(a2)], [l1 * Math.cos(a1) + l2 * Math.cos(a2), l2 * Math.cos(a2)]];
      const A2 = [[J[0][0] * J[0][0] + J[0][1] * J[0][1], J[0][0] * J[1][0] + J[0][1] * J[1][1]], [0, J[1][0] * J[1][0] + J[1][1] * J[1][1]]];
      A2[1][0] = A2[0][1];
      const tr = A2[0][0] + A2[1][1], det = A2[0][0] * A2[1][1] - A2[0][1] * A2[0][1], disc = Math.sqrt(Math.max(0, tr * tr / 4 - det));
      const l1e = tr / 2 + disc, l2e = Math.max(0, tr / 2 - disc), ang = 0.5 * Math.atan2(2 * A2[0][1], A2[0][0] - A2[1][1]);
      const u = [Math.cos(ang), Math.sin(ang), 0], v = [-Math.sin(ang), Math.cos(ang), 0];
      this.setMat(k.hell, [hd[0], hd[1], hd[2] + 0.02], [this.mul(u, 0.3 * Math.sqrt(l1e)), this.mul(v, 0.3 * Math.max(Math.sqrt(l2e), 1e-3)), [0, 0, 0.004]]);
    }
  },
});
