// 实验 22.4 笛卡尔直线与圆弧（配 22.4 节）。
// 场景 1（机器人）：上下料工位（示意值），零件库的 UR5e 把轴从卡盘前 B 送到 C（TCP 沿 −x_s 移动 0.12 m，算例 22.4.1）。
//   做法 0：关节空间五次多项式，θ_B、θ_C 取程序 22.1.1 的值；做法 1：笛卡尔直线，沿直线用梯形曲线（0.10 m/s、0.5 m/s²），
//   每 10 ms 用 14.5 节的解析逆解（与 15.1 节实验相同的程序）取与上一时刻最近的一组。两种做法的时间都是 1.4 s。
// 场景 2（机器人）：算例 15.3.2、22.4.4 的直线：法兰盘姿态不变，中心沿水平直线移动 0.3 m，中点处 θ₅ = 1°。
//   沿直线每 0.5 mm 求一次解析逆解，差商得 θ′(ℓ)；匀速，或按式 (22.4.9) ℓ̇ = min(v, min_i v_max/|θ_i′|) 自动减速（只管速度）。
// 场景 3（生活）：蛋糕上裱花。三个点 P1 = (−8, 0)、P2 = (x, y)、P3 = (8, 0)（cm，蛋糕顶面上），按定理 22.4.2 求圆，
//   裱花嘴沿圆弧按梯形曲线（0.05 m/s、0.2 m/s²）从 P1 经 P2 走到 P3。
WQ.lab({
  title: ["实验 22.4 笛卡尔直线与圆弧", "Lab 22.4 Cartesian lines and arcs"],
  goal: ["比较关节空间运动与笛卡尔直线：TCP 是否走直线；看笛卡尔直线经过手腕奇异附近时关节怎样超速，怎样按关节限速减速；由三点定出圆弧。",
         "Compare joint-space motion with a Cartesian line — does the TCP go straight; see joints overspeed when a Cartesian line passes near the wrist singularity and how slowing down by the joint limits helps; fix an arc by three points."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ins", robot: true, name: ["送入卡盘", "Into the chuck"], hide: ["v", "mode", "px", "py"],
      problem: { title: ["机器人问题：轴与卡爪之间只有很小的间隙", "Robot problem: little clearance between the shaft and the jaws"],
                 text: ["把轴从卡盘前 0.12 m 处送进卡盘，TCP 必须走直线。比较关节空间运动和笛卡尔直线。",
                        "Push the shaft 0.12 m into the chuck; the TCP must go straight. Compare joint-space motion with a Cartesian line."] } },
    { id: "sing", robot: true, name: ["经过手腕奇异", "Past the wrist singularity"], hide: ["m", "px", "py"],
      problem: { title: ["机器人问题：直线经过手腕奇异附近", "Robot problem: a straight line near the wrist singularity"],
                 text: ["法兰盘沿直线移动 0.3 m，中点处 θ₅ = 1°。各关节限速 180°/s。匀速走能不能行？怎样减速？",
                        "The flange moves 0.3 m along a line with θ₅ = 1° at the middle. Joint speed limit 180°/s. Can it go at constant speed? How should it slow down?"] } },
    { id: "cake", name: ["蛋糕裱花", "Piping a cake"], hide: ["m", "v", "mode"],
      problem: { title: ["生活中的例子：沿着三个点挤出一道圆弧", "Everyday example: pipe an arc through three points"],
                 text: ["在蛋糕顶面上点出三个点，裱花嘴沿过三点的圆弧匀速移动。调节中间那个点。",
                        "Mark three points on the top of the cake; the nozzle moves steadily along the arc through them. Move the middle point."] } },
  ],
  params: [
    { id: "m", name: ["做法：0 关节空间 / 1 笛卡尔直线", "Method: 0 joint space / 1 Cartesian line"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "v", name: ["直线速度", "Line speed"], min: 0.02, max: 0.2, step: 0.005, value: 0.1, unit: "m/s", digits: 3 },
    { id: "mode", name: ["0 匀速 / 1 按关节限速自动减速", "0 constant / 1 slow down by joint limits"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "px", name: ["中间点 P2 的 x", "middle point P2: x"], min: -7, max: 7, step: 0.5, value: 0, unit: "cm", digits: 1 },
    { id: "py", name: ["中间点 P2 的 y", "middle point P2: y"], min: 1, max: 10, step: 0.5, value: 4, unit: "cm", digits: 1 },
  ],
  legend: [{ color: "#c98f00", name: ["TCP 走过的路径", "TCP path"] }, { color: "#cf222e", name: ["要求的直线 / 圆弧", "required line / arc"] }],
  tasks: [
    { id: "joint", robot: true, text: ["用关节空间运动送料（做法 0），读出 TCP 偏离直线的最大距离。", "Push with joint-space motion (method 0) and read the largest deviation of the TCP from the line."],
      demo: { scene: "ins", set: { m: 0 }, press: ["start"], wait: 16 } },
    { id: "cart", robot: true, text: ["改用笛卡尔直线（做法 1），偏离为零，读出关节的最大速度。", "Switch to the Cartesian line (method 1): zero deviation; read the largest joint speed."],
      demo: { scene: "ins", set: { m: 1 }, press: ["start"], wait: 16 } },
    { id: "over", robot: true, text: ["以 0.1 m/s 匀速经过手腕奇异，走完全程，看到关节超速。", "Pass the wrist singularity at a constant 0.1 m/s to the end and see the joints overspeed."],
      demo: { scene: "sing", set: { v: 0.1, mode: 0 }, press: ["start"], wait: 20 } },
    { id: "slow", robot: true, text: ["直线速度 0.1 m/s、按关节限速自动减速，走完全程，所有关节都不超速，读出用时。", "At 0.1 m/s with automatic slowing by the joint limits, go to the end with no joint over its limit; read the time."],
      demo: { scene: "sing", set: { v: 0.1, mode: 1 }, press: ["start"], wait: 22 } },
    { id: "cake", text: ["裱花：调节中间点，使圆弧半径在 8～10 cm 之间，并走完一次。", "Piping: move the middle point so that the arc radius is between 8 and 10 cm, and pipe it once."],
      demo: { scene: "cake", set: { px: 0, py: 6 }, press: ["start"], wait: 30 } },
  ],
  think: ["送料时关节空间运动只偏离了 3 mm 左右，为什么仍不能用？若卡爪与轴的间隙有 10 mm，可以用吗？还要考虑什么？",
          "Joint-space motion strays only about 3 mm while pushing; why is it still unacceptable? With 10 mm of clearance could it be used? What else must be considered?"],

  // ---------------- UR5e 几何（表 12.1.1）与 SE(3) 运算
  G: { H1: 0.163, W1: 0.138, L1: 0.425, W2: 0.131, L2: 0.392, W3: 0.127, H2: 0.1, W4: 0.1 },
  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
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
  wrap(a) { return Math.atan2(Math.sin(a), Math.cos(a)); },
  AX() {
    const g = this.G, Y = [0, -1, 0];
    return [[[0, 0, 1], [0, 0, g.H1]], [Y, [0, -g.W1, g.H1]], [Y, [-g.L1, -g.W1 + g.W2, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2, g.H1]],
            [[0, 0, -1], [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1 - g.H2]]];
  },
  M() { const g = this.G; return { R: [[1, 0, 0], [0, -1, 0], [0, 0, -1]], p: [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3 - g.W4, g.H1 - g.H2] }; },
  E(i, t) { const [w, q] = this.AX()[i], R = this.rot(w, t); return { R, p: this.sub(q, this.mv(R, q)) }; },
  comp(A, B) { return { R: this.mm(A.R, B.R), p: this.add(this.mv(A.R, B.p), A.p) }; },
  inv(A) { const Rt = this.tr(A.R); return { R: Rt, p: this.mul(this.mv(Rt, A.p), -1) }; },
  act(A, x) { return this.add(this.mv(A.R, x), A.p); },
  fk(th) { let T = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] }; th.forEach((t, i) => { T = this.comp(T, this.E(i, t)); }); return this.comp(T, this.M()); },
  logR(R) {                                       // SO(3) 的对数（定理 6.2.2），θ ≈ π 时单独处理
    const c = Math.max(-1, Math.min(1, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)), th = Math.acos(c);
    const d = [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]];
    if (th < 1e-9) return this.mul(d, 0.5);
    if (Math.PI - th < 1e-6) {
      const B = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (R[i][j] + (i === j ? 1 : 0)) / 2)), k = [0, 1, 2].reduce((a, i) => (B[i][i] > B[a][a] ? i : a), 0);
      return this.mul([B[0][k], B[1][k], B[2][k]], th / Math.sqrt(B[k][k]));
    }
    return this.mul(d, th / (2 * Math.sin(th)));
  },
  log6(T) {                                       // SE(3) 的对数（定理 6.4.3），返回 (ω, v)
    const wt = this.logR(T.R), th = this.norm(wt);
    if (th < 1e-12) return [0, 0, 0, ...T.p];
    const w = this.mul(wt, 1 / th), p = T.p, wp = this.cross(w, p), wwp = this.cross(w, wp);
    const k = 1 / th - 0.5 / Math.tan(th / 2);                 // G⁻¹ = I/θ − [ω]/2 + (1/θ − cot(θ/2)/2)[ω]²，式 (6.4.8)
    const v = [0, 1, 2].map((i) => th * (p[i] / th - 0.5 * wp[i] + k * wwp[i]));
    return [...wt, ...v];
  },
  jb(th) {                                        // 物体雅可比：J_s 的各列再乘 [Ad_{T⁻¹}]
    const A = this.AX(), T = this.fk(th), Rt = this.tr(T.R), out = [];
    let P = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] };
    for (let i = 0; i < 6; i++) {
      const w = this.mv(P.R, A[i][0]), q = this.act(P, A[i][1]), v = this.mul(this.cross(w, q), -1);
      out.push([...this.mv(Rt, w), ...this.mv(Rt, this.sub(v, this.cross(T.p, w)))]);
      P = this.comp(P, this.E(i, th[i]));
    }
    return [0, 1, 2, 3, 4, 5].map((r) => out.map((c) => c[r]));     // 6×6，第 i 列为 J_bi
  },
  solve(A, b) {                                   // 列主元高斯消去
    const n = b.length, M = A.map((r, i) => [...r, b[i]]);
    for (let i = 0; i < n; i++) {
      let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(M[j][i]) > Math.abs(M[p][i])) p = j;
      [M[i], M[p]] = [M[p], M[i]];
      for (let j = i + 1; j < n; j++) { const f = M[j][i] / M[i][i]; for (let k = i; k <= n; k++) M[j][k] -= f * M[i][k]; }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let s = M[i][n]; for (let k = i + 1; k < n; k++) s -= M[i][k] * x[k]; x[i] = s / M[i][i]; }
    return x;
  },
  // ---------------- 14.5 节的解析逆解（只用来给数值解编号，次序同表 14.5.1）
  sp1(w, r, p, q) {
    const u = this.sub(p, r), v = this.sub(q, r), up = this.sub(u, this.mul(w, this.dot(w, u))), vp = this.sub(v, this.mul(w, this.dot(w, v)));
    return this.norm(up) < 1e-12 ? 0 : Math.atan2(this.dot(w, this.cross(up, vp)), this.dot(up, vp));
  },
  sp2(w1, w2, r, p, q) {
    const u = this.sub(p, r), v = this.sub(q, r), k = this.dot(w1, w2), den = k * k - 1;
    const a = (k * this.dot(w2, u) - this.dot(w1, v)) / den, b = (k * this.dot(w1, v) - this.dot(w2, u)) / den, n = this.cross(w1, w2);
    const g2 = (this.dot(u, u) - a * a - b * b - 2 * a * b * k) / this.dot(n, n);
    if (g2 < -1e-10) return [];
    const gs = g2 <= 1e-10 ? [0, 0] : [Math.sqrt(g2), -Math.sqrt(g2)];
    return gs.map((g) => { const c = this.add(r, this.add(this.add(this.mul(w1, a), this.mul(w2, b)), this.mul(n, g)));
      return [this.sp1(w1, r, c, q), this.sp1(w2, r, p, c)]; });
  },
  sp3(w, r, p, q, d) {
    const u = this.sub(p, r), v = this.sub(q, r), up = this.sub(u, this.mul(w, this.dot(w, u))), vp = this.sub(v, this.mul(w, this.dot(w, v)));
    const d2 = d * d - Math.pow(this.dot(w, this.sub(p, q)), 2), nu = this.norm(up), nv = this.norm(vp);
    const t0 = Math.atan2(this.dot(w, this.cross(up, vp)), this.dot(up, vp)), c = (nu * nu + nv * nv - d2) / (2 * nu * nv);
    if (d2 < -1e-12 || Math.abs(c) > 1 + 1e-12) return [];
    const ph = Math.atan2(Math.sqrt(Math.max(0, 1 - c * c)), Math.max(-1, Math.min(1, c)));
    return ph < 1e-9 ? [t0] : [t0 + ph, t0 - ph];
  },
  chain(th) {
    const A = this.AX(), g = this.G, Ts = [{ R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] }];
    th.forEach((t, i) => Ts.push(this.comp(Ts[i], this.E(i, t))));
    const q = A.map((x) => x[1]);
    return [[0, [0, 0, 0]], [0, q[0]], [1, q[1]], [2, this.add(q[1], [-g.L1, 0, 0])], [2, q[2]], [3, q[3]], [4, q[4]], [5, q[5]], [6, this.add(q[5], [0, -g.W4, 0])]]
      .map(([k, p]) => this.act(Ts[k], p));
  },
  elbowUp(th) {
    const P = this.chain(th), sh = P[2], el = P[4], wr = P[5], ax = this.mv(this.rot([0, 0, 1], th[0]), [0, -1, 0]);
    let n = this.cross(ax, this.sub(wr, sh));
    if (n[2] < 0) n = this.mul(n, -1);
    return this.dot(this.sub(el, sh), n) > 0;
  },
  ik(Td) {
    const g = this.G, A = this.AX(), Y = [0, -1, 0], d4 = g.W1 - g.W2 + g.W3, out = [];
    const yb = [Td.R[0][1], Td.R[1][1], Td.R[2][1]], pw = this.sub(Td.p, this.mul(yb, g.W4)), rho = Math.hypot(pw[0], pw[1]);
    if (rho < d4 - 1e-12) return out;
    const base = Math.atan2(pw[0], -pw[1]), gam = Math.atan2(Math.sqrt(Math.max(0, rho * rho - d4 * d4)), d4);
    [[1, base + gam], [-1, base - gam]].forEach(([s1, t1]) => {
      const E1i = this.E(0, -t1), Rg = this.mm(this.mm(E1i.R, Td.R), this.tr(this.M().R)), v = this.mv(this.tr(Rg), Y);
      const P56 = A[5][1];
      this.sp2(A[4][0], A[5][0], P56, this.add(P56, v), this.add(P56, Y)).forEach(([t5, t6]) => {
        const gg = this.comp(this.comp(this.comp(this.comp(E1i, Td), this.inv(this.M())), this.E(5, -t6)), this.E(4, -t5));
        const p4 = this.act(gg, A[3][1]);
        this.sp3(A[2][0], A[2][1], A[3][1], A[1][1], this.norm(this.sub(p4, A[1][1]))).forEach((t3) => {
          const t2 = this.sp1(A[1][0], A[1][1], this.act(this.E(2, t3), A[3][1]), p4);
          const h = this.comp(this.inv(this.comp(this.E(1, t2), this.E(2, t3))), gg);
          const t4 = this.sp1(A[3][0], A[3][1], A[5][1], this.act(h, A[5][1]));
          const th = [t1, t2, t3, t4, t5, t6].map((x) => this.wrap(x));
          out.push({ th, sh: s1, nf: t5 > 0, up: this.elbowUp(th) });
        });
      });
    });
    out.sort((a, b) => (b.sh - a.sh) || (Number(b.nf) - Number(a.nf)) || (Number(b.up) - Number(a.up)));
    return out;
  },
  // ---------------- 本章：工具坐标系（TCP 在法兰盘外 0.15 m，z_t 沿法兰盘法线，与第 5 章相同）与逐点逆解
  TBT: { R: [[1, 0, 0], [0, 0, 1], [0, -1, 0]], p: [0, 0.15, 0] },
  tcp(th) { return this.comp(this.fk(th), this.TBT); },
  near(sols, ref) {                               // 取与 ref 最近的一组解，并把各关节角展开到 ref 附近
    let best = null, bd = Infinity;
    sols.forEach((x) => { const th = x.th.map((v, i) => ref[i] + this.wrap(v - ref[i])), d = th.reduce((a, v, i) => a + (v - ref[i]) ** 2, 0);
      if (d < bd) { bd = d; best = th; } });
    return best;
  },
  ikTcp(Td, ref) { return this.near(this.ik(this.comp(Td, this.inv(this.TBT))), ref); },
  pose4(T) {                                      // {R, p} → 三维引擎的 Matrix4（行优先给出）
    const R = T.R, p = T.p, m = new this._T.Matrix4();
    m.set(R[0][0], R[0][1], R[0][2], p[0], R[1][0], R[1][1], R[1][2], p[1], R[2][0], R[2][1], R[2][2], p[2], 0, 0, 0, 1);
    return m;
  },
  // ---------------- 场景数据（程序 22.1.1、22.4.1 的值）
  thB: [3.518579, -0.882143, 1.391494, -0.509351, -1.19381, 0.0],
  thC: [3.605559, -1.075421, 1.724389, -0.648968, -1.10683, 0.0],
  thW0: [0.30697, -0.700943, 1.241445, 2.682123, 0.21732, 2.277061],
  VMAX: Math.PI,
  trapPos(L, v, a, t) {                           // 梯形曲线（式 (22.2.1)、(22.2.2)）走过的距离；返回 [ℓ, T]
    let ta, tc, vp;
    if (L >= v * v / a) { vp = v; ta = v / a; tc = L / v - v / a; } else { vp = Math.sqrt(a * L); ta = vp / a; tc = 0; }
    const T = 2 * ta + tc; t = Math.max(0, Math.min(T, t));
    const l = t < ta ? 0.5 * a * t * t : t < ta + tc ? 0.5 * vp * ta + vp * (t - ta) : L - 0.5 * a * (T - t) ** 2;
    return [l, T];
  },
  // ---- 场景 1：送料
  insPlan(api) {
    const TB = this.tcp(this.thB), TC = this.tcp(this.thC), u = this.mul(this.sub(TC.p, TB.p), 1 / this.norm(this.sub(TC.p, TB.p)));
    const L = this.norm(this.sub(TC.p, TB.p)), T = this.trapPos(L, 0.1, 0.5, 0)[1], N = 140, ths = [], ps = [];
    let th = this.thB.slice();
    for (let k = 0; k <= N; k++) {
      const t = k / N * T;
      if (api.p.m === 0) { const x = t / T, s = 10 * x ** 3 - 15 * x ** 4 + 6 * x ** 5; th = this.thB.map((v, i) => v + s * (this.thC[i] - v)); }
      else { const l = this.trapPos(L, 0.1, 0.5, t)[0]; th = this.ikTcp({ R: TB.R, p: this.add(TB.p, this.mul(u, l)) }, th); }
      ths.push(th); ps.push(this.tcp(th).p);
    }
    const dev = ps.map((p) => { const r = this.sub(p, TB.p); return this.norm(this.sub(r, this.mul(u, this.dot(r, u)))); });
    const vmax = [0, 1, 2, 3, 4, 5].map((i) => Math.max(...ths.slice(1).map((q, k) => Math.abs(q[i] - ths[k][i]) / (T / N))) * 180 / Math.PI);
    return { ths, ps, dev, devMax: Math.max(...dev), vmax, T, N, B: TB.p, C: TC.p };
  },
  // ---- 场景 2：手腕奇异附近的直线
  singPlan() {
    if (this._sing) return this._sing;
    const th0 = this.thW0, T0 = this.fk(th0), mid = this.fk([30, -60, 90, -120, 1, 45].map((d) => d * Math.PI / 180));
    const d = this.mul(this.sub(mid.p, T0.p), 1 / this.norm(this.sub(mid.p, T0.p)));
    const N = 600, L = 0.3, ths = [th0.slice()];
    let th = th0.slice();
    for (let k = 1; k <= N; k++) { th = this.near(this.ik({ R: T0.R, p: this.add(T0.p, this.mul(d, k / N * L)) }), th); ths.push(th); }
    const h = L / N, dth = ths.map((q, k) => { const a = ths[Math.max(0, k - 1)], b = ths[Math.min(N, k + 1)], w = (Math.min(N, k + 1) - Math.max(0, k - 1)) * h;
      return q.map((_, i) => (b[i] - a[i]) / w); });
    const vallow = dth.map((g) => Math.min(...g.map((x) => this.VMAX / Math.max(Math.abs(x), 1e-12))));
    const ps = ths.map((q) => this.fk(q).p);
    this._sing = { ths, dth, vallow, ps, N, L, h };
    return this._sing;
  },
  // ---- 场景 3：过三点的圆（定理 22.4.2，蛋糕顶面上的二维问题）
  cakePlan(api) {
    const p1 = [-0.08, 0], p2 = [api.p.px / 100, api.p.py / 100], p3 = [0.08, 0];
    const a = [p2[0] - p1[0], p2[1] - p1[1]], b = [p3[0] - p1[0], p3[1] - p1[1]], n = a[0] * b[1] - a[1] * b[0];
    const aa = a[0] ** 2 + a[1] ** 2, bb = b[0] ** 2 + b[1] ** 2;
    // 平面上式 (22.4.6) 化为：x = (|b|² (n × a) + |a|² (b × n)) / (2 n²)，n 沿 z
    const x = [(bb * (-n * a[1]) + aa * (b[1] * n)) / (2 * n * n), (bb * (n * a[0]) + aa * (-b[0] * n)) / (2 * n * n)];
    const c = [p1[0] + x[0], p1[1] + x[1]], rho = Math.hypot(x[0], x[1]);
    const ang = (p) => Math.atan2(p[1] - c[1], p[0] - c[0]);
    const a1 = ang(p1), sgn = n > 0 ? 1 : -1;
    let a3 = ang(p3) - a1; a3 = sgn > 0 ? ((a3 % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI) : -((((-a3) % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI));
    const L = rho * Math.abs(a3), T = this.trapPos(L, 0.05, 0.2, 0)[1];
    return { p1, p2, p3, c, rho, a1, a3, L, T, pt: (l) => [c[0] + rho * Math.cos(a1 + sgn * l / rho), c[1] + rho * Math.sin(a1 + sgn * l / rho)] };
  },

  reset(api, s) {
    s.t = 0; s.l = 0; s.end = false; s.max = [0, 0, 0, 0, 0, 0];
    if (api.scene === "ins") s.P = this.insPlan(api);
    if (api.scene === "sing") { s.P = this.singPlan(); s.th = s.P.ths[0]; s.ldot = 0; }
    if (api.scene === "cake") s.P = this.cakePlan(api);
  },
  start(api, s) { this.reset(api, s); },
  update(dt, api, s) {
    if (api.scene === "ins") {
      s.t = Math.min(s.P.T, s.t + 0.5 * dt);
      if (s.t >= s.P.T && !s.end) { s.end = true; api.stop();
        if (api.p.m === 0 && s.P.devMax > 1e-3) api.done("joint");
        if (api.p.m === 1 && s.P.devMax < 1e-5) api.done("cart"); }
    } else if (api.scene === "sing") {
      const P = s.P, k = Math.min(P.N, Math.round(s.l / P.h));
      s.ldot = api.p.mode === 1 ? Math.min(api.p.v, P.vallow[k]) : api.p.v;
      s.l = Math.min(P.L, s.l + s.ldot * dt); s.t += dt;
      const kk = Math.min(P.N, Math.round(s.l / P.h)); s.th = P.ths[kk];
      s.ldot = api.p.mode === 1 ? Math.min(api.p.v, P.vallow[kk]) : api.p.v;      // 到达新位置时的直线速度
      P.dth[kk].forEach((g, i) => { s.max[i] = Math.max(s.max[i], Math.abs(g) * s.ldot * 180 / Math.PI); });
      if (s.l >= P.L && !s.end) { s.end = true; api.stop();
        const mx = Math.max(...s.max);
        if (api.p.mode === 0 && Math.abs(api.p.v - 0.1) < 1e-6 && mx > 180) api.done("over");
        if (api.p.mode === 1 && Math.abs(api.p.v - 0.1) < 1e-6 && mx <= 180 + 1e-6) api.done("slow"); }
    } else {
      s.t = Math.min(s.P.T, s.t + dt);
      if (s.t >= s.P.T && !s.end) { s.end = true; api.stop(); if (s.P.rho >= 0.08 && s.P.rho <= 0.10) api.done("cake"); }
    }
  },
  readouts(api, s) {
    const P = s.P; if (!P) return [];
    const f = (x, d) => api.fmt(x, d);
    if (api.scene === "ins") {
      const k = Math.min(P.N, Math.round(s.t / P.T * P.N));
      return [[["做法", "method"], api.p.m ? api.T("笛卡尔直线", "Cartesian line") : api.T("关节空间五次多项式", "joint-space quintic")],
              [["时刻 / 总时间", "time / total"], `${f(s.t, 2)} / ${f(P.T, 2)} s`],
              [["当前偏离直线", "current deviation"], f(P.dev[k] * 1000, 3) + " mm"],
              [["最大偏离直线", "largest deviation"], f(P.devMax * 1000, 3) + " mm"],
              [["各关节最大速度 / (°/s)", "largest joint speeds / (°/s)"], P.vmax.map((x) => f(x, 1)).join(", ")]];
    }
    if (api.scene === "sing") {
      const k = Math.min(P.N, Math.round(s.l / P.h));
      const mx = Math.max(...s.max);
      return [[["走过 / 全长", "travelled / length"], `${f(s.l, 3)} / 0.300 m`], [["用时", "time"], f(s.t, 2) + " s"],
              [["θ₅", "θ₅"], f(P.ths[k][4] * 180 / Math.PI, 2) + "°"],
              [["当前直线速度 / 允许的速度", "line speed now / admissible"], `${f(s.ldot || 0, 3)} / ${f(P.vallow[k], 3)} m/s`],
              [["关节 4、6 的最大转速", "peak speed of joints 4, 6"], `${f(s.max[3], 0)}, ${f(s.max[5], 0)} °/s`],
              [["状态", "status"], mx > 180 + 1e-6 ? api.T("超速！（限值 180°/s）", "overspeed! (limit 180°/s)") : api.T("都在限值以内", "all within the limit")]];
    }
    return [[["圆心（cm）", "centre (cm)"], `(${f(P.c[0] * 100, 2)}, ${f(P.c[1] * 100, 2)})`], [["半径", "radius"], f(P.rho * 100, 2) + " cm"],
            [["圆心角", "central angle"], f(Math.abs(P.a3) * 180 / Math.PI, 1) + "°"], [["弧长", "arc length"], f(P.L * 100, 2) + " cm"],
            [["匀速段的法向加速度", "normal acceleration while cruising"], f(0.05 * 0.05 / P.rho, 4) + " m/s²"], [["时刻 / 总时间", "time / total"], `${f(s.t, 2)} / ${f(P.T, 2)} s`]];
  },

  // ---------------- 三维
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three; this._T = T;
    arm.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    const mat = (c, o) => new T.MeshStandardMaterial(Object.assign({ color: c }, o || {}));
    const line = (n, c) => { const g = new T.BufferGeometry(); g.setAttribute("position", new T.BufferAttribute(new Float32Array(n * 3), 3)); g.setDrawRange(0, 0);
      const l = new T.Line(g, new T.LineBasicMaterial({ color: c })); l.frustumCulled = false; G.add(l); return l; };
    keep.req = line(800, 0xcf222e); keep.path = line(800, 0xc98f00);
    // 工位：卡盘（主轴沿 x_s，端面朝 +x_s）、床头箱、料架
    const cell = new T.Group(); G.add(cell); keep.cell = cell;
    const chuck = new T.Mesh(new T.CylinderGeometry(0.075, 0.075, 0.1, 32, 1, true), mat(0x6e7681, { side: T.DoubleSide })); chuck.rotation.z = Math.PI / 2; chuck.position.set(0.15 - 0.07, 0.35, 0.2); cell.add(chuck);
    const head = new T.Mesh(new T.BoxGeometry(0.24, 0.2, 0.3), mat(0x5d6b73, { transparent: true, opacity: 0.35 })); head.position.set(0.15 - 0.24, 0.35, 0.19); cell.add(head);
    const rack = new T.Mesh(new T.BoxGeometry(0.2, 0.16, 0.11), mat(0x8c6d1f, { transparent: true, opacity: 0.4 })); rack.position.set(0.2, -0.45, -0.155); cell.add(rack);
    // 夹爪与轴：在工具坐标系中，轴线沿 z_t
    const tool = new T.Group(); tool.matrixAutoUpdate = false; G.add(tool); keep.tool = tool;
    const shaft = new T.Mesh(new T.CylinderGeometry(0.025, 0.025, 0.24, 24), mat(0x8c6d1f)); shaft.rotation.x = Math.PI / 2; shaft.position.set(0, 0, 0.08); tool.add(shaft);
    const fing = new T.Mesh(new T.BoxGeometry(0.07, 0.02, 0.15), mat(0x30363d)); fing.position.set(0, 0, -0.075); tool.add(fing);
    // 蛋糕
    const cake = new T.Group(); cake.position.set(0.6, 0.6, 0); G.add(cake); keep.cake = cake;
    const body = new T.Mesh(new T.CylinderGeometry(0.12, 0.12, 0.08, 48), mat(0xf3e2c7)); body.rotation.x = Math.PI / 2; body.position.set(0, 0, 0.04); cake.add(body);
    const plate = new T.Mesh(new T.CylinderGeometry(0.15, 0.15, 0.01, 48), mat(0xdee2e6)); plate.rotation.x = Math.PI / 2; plate.position.set(0, 0, 0.0); cake.add(plate);
    keep.dots = [0, 1, 2].map(() => { const d = new T.Mesh(new T.SphereGeometry(0.006, 12, 8), mat(0xcf222e)); cake.add(d); return d; });
    const arcG = new T.BufferGeometry(); arcG.setAttribute("position", new T.BufferAttribute(new Float32Array(400 * 3), 3));
    keep.arc = new T.Line(arcG, new T.LineBasicMaterial({ color: 0xcf222e })); keep.arc.frustumCulled = false; cake.add(keep.arc);
    const creamG = new T.BufferGeometry(); creamG.setAttribute("position", new T.BufferAttribute(new Float32Array(400 * 3), 3));
    keep.cream = new T.Line(creamG, new T.LineBasicMaterial({ color: 0xe64980, linewidth: 3 })); keep.cream.frustumCulled = false; cake.add(keep.cream);
    keep.nozzle = new T.Mesh(new T.ConeGeometry(0.012, 0.05, 16), mat(0x1f6feb)); keep.nozzle.rotation.x = -Math.PI / 2; cake.add(keep.nozzle);
    G.updateMatrixWorld(true);
    api.m.cakeView = { entry: { robot: {} }, holder: { visible: false }, box: () => { G.updateMatrixWorld(true); return new T.Box3().setFromObject(plate).expandByScalar(0.06); } };
  },
  setLine(l, pts) { const a = l.geometry.attributes.position; pts.forEach((p, i) => a.setXYZ(i, p[0], p[1], p[2])); a.needsUpdate = true; l.geometry.setDrawRange(0, pts.length); },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep, sc = api.scene, P = s.P;
    if (!k.G || !P) return;
    const robot = sc !== "cake";
    arm.holder.visible = robot; k.cell.visible = sc === "ins"; k.tool.visible = sc === "ins"; k.req.visible = robot; k.path.visible = robot; k.cake.visible = !robot;
    if (k.shown !== sc) { k.shown = sc; arm.holder.visible = true; if (robot) api.view(sc === "ins" ? 20 : 35, 25, 0.62, arm); else api.view(30, 40, 1.0, api.m.cakeView); arm.holder.visible = robot; }
    const set = (th) => { const o = {}; this.J.forEach((n, i) => { o[n] = th[i]; }); arm.set(o); };
    if (sc === "ins") {
      const kk = Math.min(P.N, Math.round(s.t / P.T * P.N)); set(P.ths[kk]);
      k.tool.matrix.copy(this.pose4(this.tcp(P.ths[kk]))); k.tool.matrixWorldNeedsUpdate = true;
      this.setLine(k.req, [P.B, P.C]); this.setLine(k.path, P.ps.slice(0, kk + 1));
    } else if (sc === "sing") {
      set(s.th);
      const kk = Math.min(P.N, Math.round(s.l / P.h));
      this.setLine(k.req, [P.ps[0], P.ps[P.N]]); this.setLine(k.path, P.ps.slice(0, kk + 1));
    } else {
      const pts = []; for (let i = 0; i <= 120; i++) { const q = P.pt(i / 120 * P.L); pts.push([q[0], q[1], 0.081]); }
      const a = k.arc.geometry.attributes.position; pts.forEach((p, i) => a.setXYZ(i, ...p)); a.needsUpdate = true; k.arc.geometry.setDrawRange(0, pts.length);
      [P.p1, P.p2, P.p3].forEach((p, i) => k.dots[i].position.set(p[0], p[1], 0.083));
      const l = this.trapPos(P.L, 0.05, 0.2, s.t)[0], n = Math.max(2, Math.round(l / P.L * 120)), cr = [];
      for (let i = 0; i <= n; i++) { const q = P.pt(i / n * l); cr.push([q[0], q[1], 0.084]); }
      const b = k.cream.geometry.attributes.position; cr.forEach((p, i) => b.setXYZ(i, ...p)); b.needsUpdate = true; k.cream.geometry.setDrawRange(0, cr.length);
      const q = P.pt(l); k.nozzle.position.set(q[0], q[1], 0.115);
    }
  },
});
