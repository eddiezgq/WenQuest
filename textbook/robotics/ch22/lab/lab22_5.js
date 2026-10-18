// 实验 22.5 位姿插值（配 22.5 节）。
// 场景 1（机器人）：上下料工位（示意值），零件库的 UR5e 夹着轴从料架上方 A 移到卡盘前 B（算例 22.5.1），TCP 的位姿 T_A、T_B 由
//   程序 22.1.1 的关节角 θ_A、θ_B 正运动学求出。三种插值（s 从 0 到 1，101 个点）：0 解耦插值、参考点为 TCP；1 解耦插值、参考点为
//   法兰盘中心（工具坐标系中 (0, 0, −0.15) m）；2 旋量插值 T_A e^{[V]s}，[V] = log(T_A⁻¹T_B)（定理 6.4.3）。
//   每个点用 14.5 节的解析逆解取与上一点最近的一组，画出 TCP（橙）与法兰盘中心（蓝）的路径；时间规律取五次多项式，2 s。
// 场景 2（生活）：拧瓶盖。瓶盖从转角 0、高度 0 拧到转角 180°、上升 1.5 mm（螺距 3 mm，示意值）。
//   0 解耦插值、参考点为瓶盖边缘上的一点（离轴 2 cm）；1 旋量插值（绕瓶口的轴转动并沿轴移动）。
WQ.lab({
  title: ["实验 22.5 位姿插值", "Lab 22.5 Pose interpolation"],
  goal: ["比较解耦插值（参考点取在不同的位置）与旋量插值：哪一点走直线，路径多长，关节转过多少；看旋量插值为什么与参考点的选取无关。",
         "Compare decoupled interpolation (with different reference points) and screw interpolation: which point goes straight, how long the paths are, how far the joints turn; see why the screw interpolation does not depend on the reference point."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "xfer", robot: true, name: ["从料架上方到卡盘前", "From above the rack to the chuck"], hide: ["cm"],
      problem: { title: ["机器人问题：轴从竖直变为水平，同时转到车床前", "Robot problem: the shaft turns from vertical to horizontal while moving to the lathe"],
                 text: ["两端的位姿相差 120°。选择一种位姿插值，观察 TCP（橙）和法兰盘中心（蓝）走的路径。",
                        "The two end poses differ by 120°. Choose a pose interpolation and watch the paths of the TCP (orange) and the flange centre (blue)."] } },
    { id: "cap", name: ["拧瓶盖", "Screwing a cap"], hide: ["m"],
      problem: { title: ["生活中的例子：瓶盖怎样从一个位姿到另一个位姿", "Everyday example: how a cap goes from one pose to another"],
                 text: ["瓶盖转半圈、沿螺纹上升 1.5 mm。红点是瓶盖边缘上的一点。比较两种插值下瓶盖中心的运动。",
                        "The cap turns half a turn and rises 1.5 mm along the thread. The red dot is a point on its rim. Compare how the cap centre moves under the two interpolations."] } },
  ],
  params: [
    { id: "m", name: ["0 解耦（参考点 TCP）/ 1 解耦（法兰盘中心）/ 2 旋量", "0 decoupled (TCP) / 1 decoupled (flange centre) / 2 screw"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "cm", name: ["0 解耦（参考点在边缘）/ 1 旋量", "0 decoupled (rim point) / 1 screw"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  legend: [{ color: "#d9730d", name: ["TCP 的路径", "TCP path"] }, { color: "#1f77b4", name: ["法兰盘中心的路径", "flange-centre path"] }],
  tasks: [
    { id: "tcp", robot: true, text: ["以 TCP 为参考点运行一次：TCP 走直线。", "Run with the TCP as reference: the TCP goes straight."],
      demo: { scene: "xfer", set: { m: 0 }, press: ["start"], wait: 16 } },
    { id: "fl", robot: true, text: ["以法兰盘中心为参考点运行一次，读出 TCP 在中点偏离直线多少。", "Run with the flange centre as reference and read how far the TCP is off the line at the middle."],
      demo: { scene: "xfer", set: { m: 1 }, press: ["start"], wait: 16 } },
    { id: "screw", robot: true, text: ["用旋量插值运行一次，比较三种做法中关节转过的角度。", "Run the screw interpolation and compare the joint rotations of the three."],
      demo: { scene: "xfer", set: { m: 2 }, press: ["start"], wait: 16 } },
    { id: "capscrew", text: ["拧瓶盖：用旋量插值，瓶盖中心始终在瓶口的轴线上。", "Cap: with the screw interpolation the cap centre stays on the axis of the bottle neck."],
      demo: { scene: "cap", set: { cm: 1 }, press: ["start"], wait: 16 } },
    { id: "caprim", text: ["拧瓶盖：以边缘上的点为参考点作解耦插值，读出瓶盖中心偏离轴线的最大距离。", "Cap: decoupled with the rim point as reference; read the largest distance of the cap centre from the axis."],
      demo: { scene: "cap", set: { cm: 0 }, press: ["start"], wait: 16 } },
  ],
  think: ["以法兰盘中心为参考点时，法兰盘中心走直线，TCP 却走弧线。如果夹爪更长（TCP 离法兰盘更远），TCP 偏离直线会更大还是更小？",
          "With the flange centre as reference the flange centre goes straight but the TCP follows an arc. With a longer gripper (TCP farther from the flange), is the TCP deviation larger or smaller?"],

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
  thA: [1.713433, -1.501725, 1.998971, -2.068042, -1.570796, 0.142636],
  thB: [3.518579, -0.882143, 1.391494, -0.509351, -1.19381, 0.0],
  expT(V) {                                       // 运动旋量的指数（定理 6.4.1）：V = (ω, v)，转角 θ = ‖ω‖
    const w = V.slice(0, 3), v = V.slice(3), th = this.norm(w);
    if (th < 1e-12) return { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: v.slice() };
    const u = this.mul(w, 1 / th), vh = this.mul(v, 1 / th), c = Math.cos(th), s = Math.sin(th);
    const uv = this.cross(u, vh), uuv = this.cross(u, uv);
    return { R: this.rot(u, th), p: [0, 1, 2].map((i) => th * vh[i] + (1 - c) * uv[i] + (th - s) * uuv[i]) };
  },
  interp(TA, TB, s, kind, d) {                    // kind 0：解耦（参考点 d，在物体坐标系中）；kind 2：旋量
    if (kind === 2) { const V = this.log6(this.comp(this.inv(TA), TB)); return this.comp(TA, this.expT(V.map((x) => x * s))); }
    const r = this.logR(this.mm(this.tr(TA.R), TB.R)), R = this.mm(TA.R, this.rot(this.norm(r) > 1e-12 ? this.mul(r, 1 / this.norm(r)) : [0, 0, 1], this.norm(r) * s));
    const pa = this.add(this.mv(TA.R, d), TA.p), pb = this.add(this.mv(TB.R, d), TB.p), pd = this.add(this.mul(pa, 1 - s), this.mul(pb, s));
    return { R, p: this.sub(pd, this.mv(R, d)) };
  },
  plan(api, s) {
    const N = 100;
    if (api.scene === "xfer") {
      const TA = this.tcp(this.thA), TB = this.tcp(this.thB), m = api.p.m, d = m === 1 ? [0, 0, -0.15] : [0, 0, 0];
      const ths = [], tcp = [], fl = [];
      let th = this.thA.slice();
      for (let k = 0; k <= N; k++) {
        const T = this.interp(TA, TB, k / N, m === 2 ? 2 : 0, d);
        th = this.ikTcp(T, th); ths.push(th);
        tcp.push(this.tcp(th).p); fl.push(this.fk(th).p);
      }
      const u = this.mul(this.sub(TB.p, TA.p), 1 / this.norm(this.sub(TB.p, TA.p)));
      const dev = tcp.map((p) => { const r = this.sub(p, TA.p); return this.norm(this.sub(r, this.mul(u, this.dot(r, u)))); });
      const len = (P) => P.slice(1).reduce((a, p, i) => a + this.norm(this.sub(p, P[i])), 0);
      const jt = ths.slice(1).reduce((a, q, k) => a + q.reduce((b, x, i) => b + Math.abs(x - ths[k][i]), 0), 0) * 180 / Math.PI;
      s.P = { ths, tcp, fl, dev, devMax: Math.max(...dev), devMid: dev[N / 2], Ltcp: len(tcp), Lfl: len(fl), jt, N };
    } else {
      const TA = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] }, TB = { R: this.rot([0, 0, 1], Math.PI), p: [0, 0, 0.0015] };
      const kind = api.p.cm === 1 ? 2 : 0, poses = [];
      for (let k = 0; k <= N; k++) poses.push(this.interp(TA, TB, k / N, kind, [0.02, 0, 0]));
      const off = poses.map((T) => Math.hypot(T.p[0], T.p[1]));
      s.P = { poses, off, offMax: Math.max(...off), N };
    }
  },
  reset(api, s) { s.t = 0; s.end = false; this.plan(api, s); },
  start(api, s) { s.t = 0; s.end = false; },
  update(dt, api, s) {
    s.t = Math.min(2, s.t + dt);
    if (s.t >= 2 && !s.end) {
      s.end = true; api.stop();
      if (api.scene === "xfer") {
        if (api.p.m === 0 && s.P.devMax < 1e-4) api.done("tcp");
        if (api.p.m === 1 && s.P.devMid > 0.01) api.done("fl");
        if (api.p.m === 2) api.done("screw");
      } else {
        if (api.p.cm === 1 && s.P.offMax < 1e-9) api.done("capscrew");
        if (api.p.cm === 0 && s.P.offMax > 1e-3) api.done("caprim");
      }
    }
  },
  sk(s) { const x = Math.min(1, s.t / 2), q = 10 * x ** 3 - 15 * x ** 4 + 6 * x ** 5; return Math.round(q * s.P.N); },
  readouts(api, s) {
    const P = s.P; if (!P) return [];
    const f = (x, d) => api.fmt(x, d), k = this.sk(s);
    if (api.scene === "xfer") {
      const names = [api.T("解耦，参考点 TCP", "decoupled, TCP"), api.T("解耦，参考点法兰盘中心", "decoupled, flange centre"), api.T("旋量插值", "screw")];
      return [[["插值", "interpolation"], names[api.p.m]], [["进度 s", "progress s"], f(k / P.N, 2)],
              [["TCP 偏离 A、B 连线：当前 / 中点", "TCP off the line A–B: now / middle"], `${f(P.dev[k] * 1000, 1)} / ${f(P.devMid * 1000, 1)} mm`],
              [["TCP 走过的路程", "TCP distance"], f(P.Ltcp, 3) + " m"], [["法兰盘中心走过的路程", "flange-centre distance"], f(P.Lfl, 3) + " m"],
              [["六个关节转过的角度之和", "sum of joint rotations"], f(P.jt, 0) + "°"]];
    }
    const T = P.poses[k], ang = Math.atan2(T.R[1][0], T.R[0][0]) * 180 / Math.PI;
    return [[["插值", "interpolation"], api.p.cm ? api.T("旋量插值", "screw") : api.T("解耦，参考点在边缘", "decoupled, rim point")],
            [["瓶盖转角", "cap angle"], f(((ang % 360) + 360) % 360, 1) + "°"], [["上升", "rise"], f(T.p[2] * 1000, 3) + " mm"],
            [["瓶盖中心离轴线：当前 / 最大", "cap centre off the axis: now / largest"], `${f(P.off[k] * 1000, 2)} / ${f(P.offMax * 1000, 2)} mm`]];
  },
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three; this._T = T;
    arm.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    const mat = (c, o) => new T.MeshStandardMaterial(Object.assign({ color: c }, o || {}));
    const line = (n, c, parent) => { const g = new T.BufferGeometry(); g.setAttribute("position", new T.BufferAttribute(new Float32Array(n * 3), 3)); g.setDrawRange(0, 0);
      const l = new T.Line(g, new T.LineBasicMaterial({ color: c })); l.frustumCulled = false; (parent || G).add(l); return l; };
    keep.ltcp = line(200, 0xd9730d); keep.lfl = line(200, 0x1f77b4); keep.chord = line(2, 0x9aa4ab);
    const cell = new T.Group(); G.add(cell); keep.cell = cell;
    const chuck = new T.Mesh(new T.CylinderGeometry(0.075, 0.075, 0.1, 32, 1, true), mat(0x6e7681, { side: T.DoubleSide })); chuck.rotation.z = Math.PI / 2; chuck.position.set(0.08, 0.35, 0.2); cell.add(chuck);
    const head = new T.Mesh(new T.BoxGeometry(0.24, 0.2, 0.3), mat(0x5d6b73, { transparent: true, opacity: 0.35 })); head.position.set(-0.09, 0.35, 0.19); cell.add(head);
    const rack = new T.Mesh(new T.BoxGeometry(0.2, 0.16, 0.11), mat(0x8c6d1f, { transparent: true, opacity: 0.4 })); rack.position.set(0.2, -0.45, -0.155); cell.add(rack);
    const tool = new T.Group(); tool.matrixAutoUpdate = false; G.add(tool); keep.tool = tool;
    const shaft = new T.Mesh(new T.CylinderGeometry(0.025, 0.025, 0.24, 24), mat(0x8c6d1f)); shaft.rotation.x = Math.PI / 2; shaft.position.set(0, 0, 0.08); tool.add(shaft);
    const fing = new T.Mesh(new T.BoxGeometry(0.07, 0.02, 0.15), mat(0x30363d)); fing.position.set(0, 0, -0.075); tool.add(fing);
    // 瓶子与瓶盖（放大 4 倍画出，便于观察）
    const bot = new T.Group(); bot.position.set(0.7, 0.7, 0); bot.scale.set(4, 4, 4); G.add(bot); keep.bot = bot;
    const glass = new T.Mesh(new T.CylinderGeometry(0.03, 0.03, 0.12, 32), mat(0x8ecae6, { transparent: true, opacity: 0.45 })); glass.rotation.x = Math.PI / 2; glass.position.set(0, 0, -0.07); bot.add(glass);
    const neck = new T.Mesh(new T.CylinderGeometry(0.014, 0.018, 0.02, 32), mat(0x8ecae6, { transparent: true, opacity: 0.6 })); neck.rotation.x = Math.PI / 2; neck.position.set(0, 0, -0.005); bot.add(neck);
    const capG = new T.Group(); capG.matrixAutoUpdate = false; bot.add(capG); keep.cap = capG;
    const cap = new T.Mesh(new T.CylinderGeometry(0.02, 0.02, 0.016, 32), mat(0xd62728, { transparent: true, opacity: 0.85 })); cap.rotation.x = Math.PI / 2; cap.position.set(0, 0, 0.008); capG.add(cap);
    const dot = new T.Mesh(new T.SphereGeometry(0.003, 12, 8), mat(0xffd43b)); dot.position.set(0.02, 0, 0.017); capG.add(dot);
    const axisL = line(2, 0x30363d, bot); this.setLine(axisL, [[0, 0, -0.04], [0, 0, 0.06]]); keep.axisL = axisL;
    keep.cen = line(200, 0x1f77b4, bot); keep.rim = line(200, 0xd9730d, bot);
    G.updateMatrixWorld(true);
    api.m.capView = { entry: { robot: {} }, holder: { visible: false }, box: () => { G.updateMatrixWorld(true); return new T.Box3().setFromObject(bot).expandByScalar(0.03); } };
  },
  setLine(l, pts) { const a = l.geometry.attributes.position; pts.forEach((p, i) => a.setXYZ(i, p[0], p[1], p[2])); a.needsUpdate = true; l.geometry.setDrawRange(0, pts.length); },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep, P = s.P, robot = api.scene === "xfer";
    if (!k.G || !P) return;
    arm.holder.visible = robot; k.cell.visible = robot; k.tool.visible = robot; k.ltcp.visible = robot; k.lfl.visible = robot; k.chord.visible = robot; k.bot.visible = !robot;
    if (k.shown !== api.scene) { k.shown = api.scene; arm.holder.visible = true; if (robot) api.view(25, 28, 0.62, arm); else api.view(30, 50, 0.9, api.m.capView); arm.holder.visible = robot; }
    const kk = this.sk(s);
    if (robot) {
      const o = {}; this.J.forEach((n, i) => { o[n] = P.ths[kk][i]; }); arm.set(o);
      k.tool.matrix.copy(this.pose4(this.tcp(P.ths[kk]))); k.tool.matrixWorldNeedsUpdate = true;
      this.setLine(k.ltcp, P.tcp.slice(0, kk + 1)); this.setLine(k.lfl, P.fl.slice(0, kk + 1)); this.setLine(k.chord, [P.tcp[0], P.tcp[P.N]]);
    } else {
      k.cap.matrix.copy(this.pose4(P.poses[kk])); k.cap.matrixWorldNeedsUpdate = true;
      this.setLine(k.cen, P.poses.slice(0, kk + 1).map((T) => [T.p[0], T.p[1], T.p[2] + 0.017]));
      this.setLine(k.rim, P.poses.slice(0, kk + 1).map((T) => this.add(this.act(T, [0.02, 0, 0]), [0, 0, 0.017])));
    }
  },
});
