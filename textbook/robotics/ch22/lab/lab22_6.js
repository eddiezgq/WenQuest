// 实验 22.6 时间最优轨迹（配 22.6 节）。
// 场景 1（机器人）：上下料工位（示意值），零件库的 UR5e 夹着轴从料架 R 经 A、M 到卡盘前 B（算例 22.3.1、22.6.2、22.6.3）。
//   做法 0：每点停下，三段关节空间直线，五次多项式（算例 22.3.1，各段时长取自程序 22.3.1）；
//   做法 1：三次样条整体缩放（算例 22.3.1，总时间 1.774 s）；
//   做法 2：沿同一条样条路径的时间最优参数化（22.6.4 节的算法：先从终点往回求可控集，再从起点往前每步取最大加速度），
//          关节速度、加速度限值都乘以 η；
//   做法 3：做法 2 的 σ(t) 再用宽 t_j 的盒形窗滑动平均（定理 22.2.2）。
//   路径数据：样条路径以关节空间的弧长 σ 为参数，401 个网格点上的 θ(σ)、θ′(σ)、θ″(σ)，以及对应的样条时间 u，由程序 22.6.1 的同一套函数生成。
//   振动：关节 1 的加速度驱动 22.2 节的扭转模态（f_n = 8 Hz、ζ = 0.02，示意值），四阶龙格-库塔法、步长 1 ms；
//   TCP 到关节 1 轴线的距离取 B 处的值。画面中关节 1 的转角加上 30 倍的扭转角，便于看出振动。播放放慢 2 倍。
//   半个循环 = 夹紧 0.3 s + 转移 + 等待振动衰减到 0.05 mm + 送料 1.4 s + 松开 0.3 s（夹紧、松开时间为示意值）。
// 场景 2（生活）：汽车沿 S 形道路行驶（示意值）：直道 80 m、左弯 R = 40 m（90°）、直道 40 m、右弯 R = 25 m（90°）、直道 80 m；
//   限速 16.7 m/s（60 km/h），纵向加速度、减速度不超过 2.5 m/s²，侧向加速度 κv² 不超过所设的值。
//   做法 0：全程以弯道允许的最小速度匀速（起步、停车按梯形曲线）；做法 1：时间最优（前推一遍、后推一遍，19.2 节）。播放加快 4 倍。
WQ.lab({
  title: ["实验 22.6 时间最优轨迹", "Lab 22.6 Time-optimal trajectories"],
  goal: ["为数字工厂上下料设计节拍最短且平稳的转移：比较每点停下、样条缩放、时间最优和时间最优加滤波四种做法的转移时间、残余振动和半个循环的节拍。",
         "Design the shortest and smoothest transfer for the digital-factory loading cell: compare stopping at each point, a scaled spline, time-optimal timing and time-optimal timing with filtering by transfer time, residual vibration and half-cycle time."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "cycle", robot: true, name: ["上下料的节拍", "Loading cycle"], hide: ["ra", "rm"],
      problem: { title: ["机器人问题：从料架到卡盘前，怎样最快又不晃", "Robot problem: from the rack to the chuck, fastest without shaking"],
                 text: ["路径经过 R、A、M、B。转移得快，轴晃得厉害就要等它停下才能送进卡盘。选择做法，调节 η 和 t_j，使半个循环最短。",
                        "The path passes R, A, M, B. A fast transfer that shakes the shaft must wait for it to settle before entering the chuck. Choose a method, tune η and t_j, and make the half cycle shortest."] } },
    { id: "road", name: ["弯道上开车", "Driving through bends"], hide: ["m", "eta", "tj"],
      problem: { title: ["生活中的例子：沿给定的道路，最快能开多快", "Everyday example: how fast can a car go along a given road"],
                 text: ["道路有两个弯。弯道上的侧向加速度 κv² 不能超过所设的值，直道上不能超速。比较全程匀速和时间最优的速度曲线。",
                        "The road has two bends. The lateral acceleration κv² must stay below the set value and the speed limit holds on the straights. Compare a constant speed with the time-optimal speed profile."] } },
  ],
  params: [
    { id: "m", name: ["做法：0 每点停下 / 1 样条缩放 / 2 时间最优 / 3 时间最优 + 滤波", "Method: 0 stop at each point / 1 scaled spline / 2 time-optimal / 3 time-optimal + filter"], min: 0, max: 3, step: 1, value: 0, unit: "", digits: 0 },
    { id: "eta", name: ["限值比例 η（做法 2、3）", "limit ratio η (methods 2, 3)"], min: 0.7, max: 1, step: 0.01, value: 1, unit: "", digits: 2 },
    { id: "tj", name: ["滤波窗宽 t_j（做法 3）", "filter width t_j (method 3)"], min: 0.025, max: 0.25, step: 0.005, value: 0.1, unit: "s", digits: 3 },
    { id: "rm", name: ["0 全程匀速 / 1 时间最优", "0 constant speed / 1 time-optimal"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "ra", name: ["侧向加速度上限", "lateral acceleration limit"], min: 1, max: 8, step: 0.5, value: 4, unit: "m/s²", digits: 1 },
  ],
  legend: [{ color: "#d9730d", name: ["TCP 的路径", "TCP path"] }, { color: "#1f77b4", name: ["车的轨迹 / 道路中线", "car track / road centre line"] }],
  tasks: [
    { id: "stop", robot: true, text: ["做法 0（每点停下）运行一次，读出转移时间、残余振幅和半个循环。", "Run method 0 (stop at each point) and read the transfer time, residual amplitude and half cycle."],
      demo: { scene: "cycle", set: { m: 0 }, press: ["start"], wait: 30 } },
    { id: "opt", robot: true, text: ["做法 2（时间最优，η = 1）运行一次：转移时间最短，读出要等多久。", "Run method 2 (time-optimal, η = 1): the shortest transfer; read how long it must wait."],
      demo: { scene: "cycle", set: { m: 2, eta: 1 }, press: ["start"], wait: 30 } },
    { id: "smooth", robot: true, text: ["做法 3：调节 t_j 和 η，使关节速度、加速度都不超限，残余振幅不超过 0.05 mm，半个循环不超过 3.8 s。",
                                        "Method 3: tune t_j and η so that no joint speed or acceleration exceeds its limit, the residual amplitude is at most 0.05 mm and the half cycle is at most 3.8 s."],
      demo: { scene: "cycle", set: { m: 3, tj: 0.125, eta: 0.92 }, press: ["start"], wait: 30 } },
    { id: "road", text: ["弯道上开车：侧向加速度上限 3 m/s²，用时间最优的速度曲线开完全程，比全程匀速快多少？", "Bends: with a 3 m/s² lateral limit, drive the time-optimal speed profile; how much faster than a constant speed?"],
      demo: { scene: "road", set: { rm: 1, ra: 3 }, press: ["start"], wait: 30 } },
  ],
  think: ["时间最优的转移比每点停下快得多，为什么半个循环只快了一点？滤波让转移变慢了，为什么节拍却最短？",
          "The time-optimal transfer is much faster than stopping at each point; why is its half cycle only a little shorter? Filtering slows the transfer down; why is its cycle the shortest?"],
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
  D: {"segs":[[0.3893443,[[1.713433,-1.341958,2.126399,-2.355238,-1.570796,0.142636],[0.0,0.0,0.0,0.0,0.0,0.0],[-1.056219,-2.39587,-0.161451,1.700593,0.151213,-0.78511],[2.712815,3.44662,-1.744388,0.498205,-0.388379,2.016493]]],[0.7178142,[[1.713433,-1.501725,1.998971,-2.068042,-1.570796,0.142636],[0.411233,-0.298228,-0.91901,1.5508,-0.058874,0.305678],[2.112438,1.629895,-2.198953,2.282514,-0.302427,1.57022],[-1.034005,-0.839643,2.414375,-2.336027,0.609509,-1.846678]]],[0.6671858,[[2.714635,-1.186532,1.099244,-0.642774,-1.543452,0.488114],[1.845574,0.743798,-0.343817,1.216677,0.449115,-0.294611],[-0.114232,-0.178229,3.000266,-2.747986,1.010116,-2.406495],[-1.267884,-0.378891,-2.74047,1.834759,-1.345642,2.625237]]]],"Q":[[1.713433,-1.341958,2.126399,-2.355238,-1.570796,0.142636],[1.713433,-1.501725,1.998971,-2.068042,-1.570796,0.142636],[2.714635,-1.186532,1.099244,-0.642774,-1.543452,0.488114],[3.518579,-0.882143,1.391494,-0.509351,-1.19381,-0.0]],"Tseg":[0.54262,1.000401,0.929841],"U":1.7743443,"rarm":0.442041},
  VMAX: [Math.PI, Math.PI, Math.PI, Math.PI, Math.PI, Math.PI],
  AMAX: [6, 6, 6, 12, 12, 12],
  FN: 8, ZETA: 0.02, TOL: 0.05, GRIP: 0.3, INS: 1.4, DT: 0.001, SLOW: 2, EXAG: 30,
  // ---------------- 二元线性规划：G (x, u)ᵀ ≤ h 中 x 的最大值（枚举顶点，与程序 22.6.1 相同）
  lp2(G, h) {
    let best = -1;
    for (let i = 0; i < G.length; i++) {
      for (let j = i + 1; j < G.length; j++) {
        const det = G[i][0] * G[j][1] - G[j][0] * G[i][1];
        if (Math.abs(det) < 1e-14) continue;
        const x = (h[i] * G[j][1] - h[j] * G[i][1]) / det, u = (G[i][0] * h[j] - G[j][0] * h[i]) / det;
        if (x <= best) continue;
        let ok = true;
        for (let k = 0; k < G.length && ok; k++) ok = G[k][0] * x + G[k][1] * u <= h[k] + 1e-9 * (1 + Math.abs(h[k]));
        if (ok) best = x;
      }
    }
    return Math.max(0, best);
  },
  // ---------------- 样条路径改用关节空间的弧长 σ 作参数（‖θ′(σ)‖ = 1），网格 1000 段（与程序 22.6.1 的 arclength_path 相同）
  path() {
    if (this.PD) return this.PD;
    const D = this.D, U = D.U, N = 1000, nf = N * 20, uf = [], cs = [0];
    for (let i = 0; i <= nf; i++) uf.push((i / nf) * U);
    const sp = uf.map((u) => Math.hypot(...this.segEval(D.segs, u, 1)));
    for (let i = 1; i <= nf; i++) cs.push(cs[i - 1] + 0.5 * (sp[i] + sp[i - 1]) * (uf[i] - uf[i - 1]));
    const L = cs[nf], th = [], d1 = [], d2 = [], ok = [];
    let j = 0;
    for (let k = 0; k <= N; k++) {
      const sg = (k / N) * L;
      while (j < nf - 1 && cs[j + 1] < sg) j++;
      const f = cs[j + 1] > cs[j] ? Math.min(1, Math.max(0, (sg - cs[j]) / (cs[j + 1] - cs[j]))) : 0, u = uf[j] + f * (uf[j + 1] - uf[j]);
      const a = this.segEval(D.segs, u, 1), b = this.segEval(D.segs, u, 2), n2 = a.reduce((x, v) => x + v * v, 0), ab = a.reduce((x, v, i) => x + v * b[i], 0);
      th.push(this.segEval(D.segs, u, 0));
      ok.push(u > 1e-4 * U && u < U * (1 - 1e-4));
      d1.push(a.map((v) => v / Math.sqrt(n2))); d2.push(b.map((v, i) => (v - (ab / n2) * a[i]) / n2));
    }
    for (let k = 0; k <= N; k++) {                             // 两端 θ_u = 0：用最近的两个内部点线性外推
      if (ok[k]) continue;
      const nb = []; for (let i = 0; i <= N && nb.length < 2; i++) { const c = k < N / 2 ? i : N - i; if (ok[c]) nb.push(c); }
      const [p, q] = nb; [d1, d2].forEach((A) => { A[k] = A[p].map((v, i) => v + (v - A[q][i]) * (k - p) / (p - q)); });
    }
    this.PD = { N, L, th, d1, d2 };
    return this.PD;
  },
  // ---------------- 时间最优参数化（22.6.4 节）：x = σ̇²，u = σ̈，每个网格区间内 u 为常数
  topp(eta) {
    const D = this.path(), N = D.N, ds = D.L / N, big = 1e6, V = this.VMAX.map((v) => v * eta), A = this.AMAX.map((a) => a * eta);
    const XV = [], CON = [];
    for (let k = 0; k <= N; k++) {
      const d1 = D.d1[k], d2 = D.d2[k];
      let xv = 1e12; const G = [], h = [];
      for (let i = 0; i < 6; i++) {
        if (Math.abs(d1[i]) > 1e-12) xv = Math.min(xv, (V[i] * V[i]) / (d1[i] * d1[i]));
        G.push([d2[i], d1[i]], [-d2[i], -d1[i]]); h.push(A[i], A[i]);
      }
      XV.push(xv); CON.push([G, h]);
    }
    const K = new Array(N + 1); K[N] = 0;
    for (let k = N - 1; k >= 0; k--) {                         // 第 1 遍：从终点往回，可控集 [0, K_k]
      const [G0, h0] = CON[k];
      const G = G0.concat([[1, 0], [-1, 0], [1, 2 * ds], [-1, -2 * ds], [0, 1], [0, -1]]);
      const h = h0.concat([XV[k], 0, K[k + 1], 0, big, big]);
      K[k] = this.lp2(G, h);
    }
    const x = [0], u = [];
    for (let k = 0; k < N; k++) {                              // 第 2 遍：从起点往前，每步取允许的最大 u
      const [G, h] = CON[k]; let lo = -big, hi = big;
      for (let r = 0; r < G.length; r++) {
        const rhs = h[r] - G[r][0] * x[k];
        if (G[r][1] > 1e-14) hi = Math.min(hi, rhs / G[r][1]); else if (G[r][1] < -1e-14) lo = Math.max(lo, rhs / G[r][1]);
      }
      hi = Math.min(hi, (K[k + 1] - x[k]) / (2 * ds)); lo = Math.max(lo, -x[k] / (2 * ds));
      const uk = Math.max(lo, hi);
      u.push(uk); x.push(Math.max(0, x[k] + 2 * ds * uk));
    }
    const t = [0];
    for (let k = 0; k < N; k++) t.push(t[k] + 2 * ds / Math.max(Math.sqrt(x[k]) + Math.sqrt(x[k + 1]), 1e-300));
    return { x, u, t, ds };
  },
  // 按时间每 1 ms 取样 σ(t)：区间内 σ̈ 为常数
  sample(P) {
    const dt = this.DT, n = Math.floor(P.t[P.t.length - 1] / dt) + 1, sig = [], sd = [], sdd = [];
    let k = 0;
    for (let m = 0; m <= n; m++) {
      const tm = Math.min(m * dt, P.t[P.t.length - 1]);
      while (k < P.u.length - 1 && P.t[k + 1] <= tm) k++;
      const tau = tm - P.t[k];
      sig.push(Math.min(this.PD.L, k * P.ds + Math.sqrt(P.x[k]) * tau + 0.5 * P.u[k] * tau * tau));
      sd.push(Math.sqrt(P.x[k]) + P.u[k] * tau); sdd.push(m === n ? 0 : P.u[k]);
    }
    return { sig, sd, sdd };
  },
  boxf(sig, tj) {                                              // 宽 t_j 的盒形窗滑动平均（定理 22.2.2），末端延长 t_j
    const n = Math.max(1, Math.round(tj / this.DT)), L = this.PD.L, ext = new Array(n).fill(0).concat(sig, new Array(n).fill(L)), c = [0];
    ext.forEach((v, i) => c.push(c[i] + v));
    const out = [];
    for (let i = 0; i < sig.length + n; i++) out.push((c[i + n + 1] - c[i + 1]) / n);
    return out;
  },
  gidx(sig) { const g = (sig / this.PD.L) * this.PD.N, k = Math.min(this.PD.N - 1, Math.max(0, Math.floor(g))); return [k, g - k]; },
  lerp(a, b, f) { return a.map((v, i) => v + (b[i] - v) * f); },
  thAt(sig) { const [k, f] = this.gidx(sig); return this.lerp(this.PD.th[k], this.PD.th[k + 1], f); },
  qd(sig, sd, sdd) {                                           // θ̇ = θ′σ̇，θ̈ = θ′σ̈ + θ″σ̇²
    const [k, f] = this.gidx(sig), d1 = this.lerp(this.PD.d1[k], this.PD.d1[k + 1], f), d2 = this.lerp(this.PD.d2[k], this.PD.d2[k + 1], f);
    return [d1.map((v) => v * sd), d1.map((v, i) => v * sdd + d2[i] * sd * sd)];
  },
  segEval(segs, t, r) {                                        // 分段多项式 Σ c_k τ^k 的 r 阶导数（每段 4×6 的系数）
    let k = 0, t0 = 0;
    while (k < segs.length - 1 && t > t0 + segs[k][0]) { t0 += segs[k][0]; k++; }
    const tau = Math.min(Math.max(t - t0, 0), segs[k][0]), C = segs[k][1];
    return [0, 1, 2, 3, 4, 5].map((i) => {
      let s = 0;
      for (let p = r; p < C.length; p++) { let f = 1; for (let q = 0; q < r; q++) f *= p - q; s += C[p][i] * f * tau ** (p - r); }
      return s;
    });
  },
  quintic(tau, r) {
    if (r === 0) return 10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5;
    if (r === 1) return 30 * tau ** 2 - 60 * tau ** 3 + 30 * tau ** 4;
    return 60 * tau - 180 * tau ** 2 + 120 * tau ** 3;
  },
  // 各做法的轨迹：每 1 ms 的关节角、关节 1 的加速度，以及速度、加速度占限值的最大比例
  build(api) {
    const m = api.p.m, dt = this.DT, D = this.D, ths = [], a1 = [];
    let rv = 0, ra = 0;
    const chk = (v, a) => { for (let i = 0; i < 6; i++) { rv = Math.max(rv, Math.abs(v[i]) / this.VMAX[i]); ra = Math.max(ra, Math.abs(a[i]) / this.AMAX[i]); } };
    if (m === 0) {
      let t0 = 0;
      for (let s = 0; s < 3; s++) {
        const T = D.Tseg[s], q0 = D.Q[s], dq = D.Q[s + 1].map((v, i) => v - q0[i]), n = Math.round(T / dt);
        for (let j = s === 0 ? 0 : 1; j <= n; j++) {
          const tau = j / n, p = this.quintic(tau, 0), v = this.quintic(tau, 1) / T, a = this.quintic(tau, 2) / (T * T);
          ths.push(q0.map((q, i) => q + dq[i] * p)); a1.push(dq[0] * a); chk(dq.map((d) => d * v), dq.map((d) => d * a));
        }
        t0 += T;
      }
    } else if (m === 1) {
      const n = Math.round(D.U / dt);
      for (let j = 0; j <= n; j++) {
        const t = (j / n) * D.U, v = this.segEval(D.segs, t, 1), a = this.segEval(D.segs, t, 2);
        ths.push(this.segEval(D.segs, t, 0)); a1.push(a[0]); chk(v, a);
      }
    } else {
      const P = this.topp(api.p.eta);
      const S = this.sample(P), sig = m === 3 ? this.boxf(S.sig, api.p.tj) : S.sig;
      const n = sig.length;
      for (let j = 0; j < n; j++) {
        const jm = Math.max(0, j - 1), jp = Math.min(n - 1, j + 1);
        // 做法 2 用区间内的精确值；做法 3 滤波后的 σ(t) 光滑，用差商
        const sd = m === 2 ? S.sd[j] : (sig[jp] - sig[jm]) / ((jp - jm) * dt);
        const sdd = m === 2 ? S.sdd[j] : (j === 0 || j === n - 1 ? 0 : (sig[jp] - 2 * sig[j] + sig[jm]) / (dt * dt));
        const [v, a] = this.qd(sig[j], sd, sdd);
        ths.push(this.thAt(sig[j])); a1.push(a[0]);
        if (j > 1 && j < n - 2) chk(v, a);
      }
    }
    // 扭转模态 φ'' + 2ζωφ' + ω²φ = −θ̈₁（式 (22.2.6)），四阶龙格-库塔
    const w = 2 * Math.PI * this.FN, z = this.ZETA, phi = [0];
    let p = 0, q = 0;
    const f = (pp, qq, a) => [qq, -a - 2 * z * w * qq - w * w * pp];
    for (let j = 0; j < a1.length - 1; j++) {
      const a0 = a1[j], am = 0.5 * (a1[j] + a1[j + 1]), ae = a1[j + 1];
      const k1 = f(p, q, a0), k2 = f(p + 0.5 * dt * k1[0], q + 0.5 * dt * k1[1], am), k3 = f(p + 0.5 * dt * k2[0], q + 0.5 * dt * k2[1], am), k4 = f(p + dt * k3[0], q + dt * k3[1], ae);
      p += (dt / 6) * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); q += (dt / 6) * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]);
      phi.push(p);
    }
    const wd = w * Math.sqrt(1 - z * z), amp = Math.hypot(p, (q + z * w * p) / wd), Amm = amp * D.rarm * 1000;
    const T = (ths.length - 1) * dt, wait = Amm > this.TOL ? Math.log(Amm / this.TOL) / (z * w) : 0;
    return { ths, phi, p, q, wd, T, Amm, wait, rv, ra, cyc: this.GRIP + T + wait + this.INS + this.GRIP };
  },
  // ---------------- 生活场景：S 形道路
  road(api) {
    const segs = [[80, 0], [40 * Math.PI / 2, 1 / 40], [40, 0], [25 * Math.PI / 2, -1 / 25], [80, 0]];
    const L = segs.reduce((a, s) => a + s[0], 0), N = 1500, ds = L / N, vr = 16.7, al = 2.5, alat = api.p.ra;
    const pts = [], kap = [];
    let x = 0, y = 0, h = 0, acc = 0, si = 0;
    for (let k = 0; k <= N; k++) {
      const s = k * ds;
      while (si < segs.length - 1 && s > acc + segs[si][0] + 1e-9) { acc += segs[si][0]; si++; }
      kap.push(segs[si][1]); pts.push([x, y, h]);
      const kk = segs[si][1]; x += ds * Math.cos(h + 0.5 * kk * ds); y += ds * Math.sin(h + 0.5 * kk * ds); h += kk * ds;
    }
    const cap = kap.map((k, i) => {                            // 弯道起止处取相邻两段中较严的限值
      const k2 = Math.max(Math.abs(k), Math.abs(kap[Math.max(0, i - 1)]), Math.abs(kap[Math.min(N, i + 1)]));
      return Math.min(vr * vr, k2 > 0 ? alat / k2 : 1e9);
    });
    let X;
    if (api.p.rm === 1) {                                      // 前推一遍、后推一遍，取最小（19.2 节）
      const F = [0], B = new Array(N + 1); B[N] = 0;
      for (let k = 0; k < N; k++) F.push(Math.min(cap[k + 1], F[k] + 2 * al * ds));
      for (let k = N - 1; k >= 0; k--) B[k] = Math.min(cap[k], B[k + 1] + 2 * al * ds);
      X = F.map((v, k) => Math.min(v, B[k]));
    } else {
      const vc2 = Math.min(...cap);
      X = new Array(N + 1).fill(0).map((_, k) => Math.min(vc2, 2 * al * k * ds, 2 * al * (N - k) * ds));
    }
    const t = [0];
    for (let k = 0; k < N; k++) t.push(t[k] + 2 * ds / Math.max(Math.sqrt(X[k]) + Math.sqrt(X[k + 1]), 1e-300));
    let latMax = 0; X.forEach((v, k) => { latMax = Math.max(latMax, Math.abs(kap[k]) * v); });
    const vcon = Math.sqrt(Math.min(...cap)), Tcon = L / vcon + vcon / al;
    return { pts, X, t, kap, N, L, T: t[N], latMax, Tcon, vr, alat };
  },
  plan(api, s) { this.path(); if (api.scene === "cycle") s.P = this.build(api); else s.R = this.road(api); },
  reset(api, s) { s.t = 0; s.end = false; s.run = false; this.plan(api, s); },
  start(api, s) { s.t = 0; s.end = false; s.run = true; this.plan(api, s); },
  tEnd(api, s) {
    if (api.scene === "road") return s.R.T;
    return s.P.T + Math.min(Math.max(s.P.wait, 0.6), 3.0);   // 到 B 以后再看一会儿振动
  },
  update(dt, api, s) {
    if (!s.run) return;
    const sp = api.scene === "road" ? 4 : 1 / this.SLOW;
    s.t = Math.min(this.tEnd(api, s), s.t + dt * sp);
    if (s.t >= this.tEnd(api, s) && !s.end) {
      s.end = true; s.run = false; api.stop();
      if (api.scene === "cycle") {
        const P = s.P, m = api.p.m;
        if (m === 0) api.done("stop");
        if (m === 2 && api.p.eta >= 0.995) api.done("opt");
        if (m === 3 && Math.max(P.rv, P.ra) <= 1.01 && P.Amm <= this.TOL && P.cyc <= 3.8) api.done("smooth");
      } else if (api.p.rm === 1 && api.p.ra <= 3.0001) api.done("road");
    }
  },
  phiAt(P, t) {                                                // 运动中取模拟值；停下以后按自由衰减振动外推
    if (t <= P.T) return P.phi[Math.min(P.phi.length - 1, Math.round(t / this.DT))];
    const w = 2 * Math.PI * this.FN, z = this.ZETA, tt = t - P.T;
    return Math.exp(-z * w * tt) * (P.p * Math.cos(P.wd * tt) + ((P.q + z * w * P.p) / P.wd) * Math.sin(P.wd * tt));
  },
  readouts(api, s) {
    const f = (x, d) => api.fmt(x, d);
    if (api.scene === "cycle") {
      const P = s.P; if (!P) return [];
      const names = [api.T("每点停下（五次多项式）", "stop at each point (quintic)"), api.T("三次样条整体缩放", "scaled cubic spline"),
                     api.T("时间最优", "time-optimal"), api.T("时间最优 + 盒形窗滤波", "time-optimal + box filter")];
      const ph = s.t <= P.T ? api.T("转移", "transfer") : api.T("到达 B，等待振动衰减", "at B, waiting for the vibration to decay");
      const amp = Math.abs(this.phiAt(P, s.t)) * this.D.rarm * 1000;
      return [[["做法", "method"], names[api.p.m]], [["时刻（放慢 2 倍）", "time (2× slower)"], `${f(s.t, 2)} s`], [["阶段", "phase"], ph],
              [["转移时间", "transfer time"], f(P.T, 3) + " s"],
              [["关节速度、加速度占限值的最大比例", "largest share of the joint speed / acceleration limits"], `${f(P.rv * 100, 1)}% / ${f(P.ra * 100, 1)}%`],
              [["TCP 的振动：当前 / 到达时的残余振幅", "TCP vibration: now / residual amplitude on arrival"], `${f(amp, 3)} / ${f(P.Amm, 3)} mm`],
              [["等振动衰减到 0.05 mm", "wait until it decays to 0.05 mm"], f(P.wait, 2) + " s"],
              [["半个循环：夹紧 + 转移 + 等待 + 送料 + 松开", "half cycle: grip + transfer + wait + insert + release"], f(P.cyc, 2) + " s"]];
    }
    const R = s.R; if (!R) return [];
    const k = this.roadK(R, s.t), v = Math.sqrt(R.X[k]);
    return [[["速度曲线", "speed profile"], api.p.rm ? api.T("时间最优", "time-optimal") : api.T("全程匀速", "constant speed")],
            [["时刻", "time"], f(s.t, 1) + " s"], [["车速", "speed"], `${f(v, 1)} m/s（${f(v * 3.6, 0)} km/h）`],
            [["侧向加速度：当前 / 全程最大", "lateral acceleration: now / largest"], `${f(Math.abs(R.kap[k]) * R.X[k], 2)} / ${f(R.latMax, 2)} m/s²`],
            [["全程用时", "total time"], f(R.T, 1) + " s"], [["全程匀速所需时间", "time at constant speed"], f(R.Tcon, 1) + " s"]];
  },
  roadK(R, t) { let k = 0; while (k < R.N && R.t[k + 1] <= t) k++; return k; },
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three; this._T = T;
    arm.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    const mat = (c, o) => new T.MeshStandardMaterial(Object.assign({ color: c }, o || {}));
    const line = (n, c, parent) => { const g = new T.BufferGeometry(); g.setAttribute("position", new T.BufferAttribute(new Float32Array(n * 3), 3)); g.setDrawRange(0, 0);
      const l = new T.Line(g, new T.LineBasicMaterial({ color: c })); l.frustumCulled = false; (parent || G).add(l); return l; };
    keep.ltcp = line(700, 0xd9730d);
    const cell = new T.Group(); G.add(cell); keep.cell = cell;
    const chuck = new T.Mesh(new T.CylinderGeometry(0.075, 0.075, 0.1, 32, 1, true), mat(0x6e7681, { side: T.DoubleSide })); chuck.rotation.z = Math.PI / 2; chuck.position.set(0.08, 0.35, 0.2); cell.add(chuck);
    const head = new T.Mesh(new T.BoxGeometry(0.24, 0.2, 0.3), mat(0x5d6b73, { transparent: true, opacity: 0.35 })); head.position.set(-0.09, 0.35, 0.19); cell.add(head);
    const rack = new T.Mesh(new T.BoxGeometry(0.2, 0.16, 0.11), mat(0x8c6d1f, { transparent: true, opacity: 0.4 })); rack.position.set(0.2, -0.45, -0.155); cell.add(rack);
    const tool = new T.Group(); tool.matrixAutoUpdate = false; G.add(tool); keep.tool = tool;
    const shaft = new T.Mesh(new T.CylinderGeometry(0.025, 0.025, 0.24, 24), mat(0x8c6d1f)); shaft.rotation.x = Math.PI / 2; shaft.position.set(0, 0, 0.08); tool.add(shaft);
    const fing = new T.Mesh(new T.BoxGeometry(0.07, 0.02, 0.15), mat(0x30363d)); fing.position.set(0, 0, -0.075); tool.add(fing);
    // 道路：缩小 100 倍画在地面上（车再放大 4 倍，便于看清）
    const rd = new T.Group(); rd.position.set(1.2, -1.2, -0.3); rd.scale.set(0.01, 0.01, 0.01); G.add(rd); keep.rd = rd;
    keep.rline = line(1600, 0x9aa4ab, rd); keep.rtrack = line(1600, 0x1f77b4, rd);
    const car = new T.Mesh(new T.BoxGeometry(4.5, 1.8, 1.4), mat(0xd62728)); car.position.z = 0.7; car.scale.set(4, 4, 4); const carG = new T.Group(); carG.add(car); rd.add(carG); keep.car = carG;
    G.updateMatrixWorld(true);
    api.m.roadView = { entry: { robot: {} }, holder: { visible: false }, box: () => { G.updateMatrixWorld(true); return new T.Box3().setFromObject(keep.rline).expandByScalar(0.1); } };
  },
  setLine(l, pts, box) {
    const a = l.geometry.attributes.position; pts.forEach((p, i) => a.setXYZ(i, p[0], p[1], p[2])); a.needsUpdate = true; l.geometry.setDrawRange(0, pts.length);
    if (box) {                                                 // 未用的点放在末点，重算包围盒（道路取景要用）
      const fx = pts[pts.length - 1]; for (let i = pts.length; i < a.count; i++) a.setXYZ(i, fx[0], fx[1], fx[2]);
      l.geometry.computeBoundingBox(); l.geometry.computeBoundingSphere();
    }
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep, robot = api.scene === "cycle";
    if (!k.G) return;
    arm.holder.visible = robot; k.cell.visible = robot; k.tool.visible = robot; k.ltcp.visible = robot; k.rd.visible = !robot;
    if (!robot && s.R && k.roadKey !== s.R) { k.roadKey = s.R; this.setLine(k.rline, s.R.pts.map((p) => [p[0], p[1], 0]), true); }
    if (k.shown !== api.scene) { k.shown = api.scene; arm.holder.visible = true; if (robot) api.view(25, 28, 0.62, arm); else api.view(20, 60, 0.85, api.m.roadView); arm.holder.visible = robot; }
    if (robot) {
      const P = s.P; if (!P) return;
      const j = Math.min(P.ths.length - 1, Math.round(Math.min(s.t, P.T) / this.DT)), th = P.ths[j].slice();
      th[0] += this.EXAG * this.phiAt(P, s.t);
      const o = {}; this.J.forEach((n, i) => { o[n] = th[i]; }); arm.set(o);
      k.tool.matrix.copy(this.pose4(this.tcp(th))); k.tool.matrixWorldNeedsUpdate = true;
      if (k.pathKey !== P) { k.pathKey = P; const st = Math.max(1, Math.ceil(P.ths.length / 600)); k.path = P.ths.filter((_, i) => i % st === 0).map((q) => this.tcp(q).p); }
      this.setLine(k.ltcp, k.path.slice(0, Math.max(1, Math.round((k.path.length - 1) * Math.min(1, s.t / P.T))) + 1));
    } else {
      const R = s.R; if (!R) return;
      const kk = this.roadK(R, s.t), p = R.pts[kk];
      k.car.position.set(p[0], p[1], 0); k.car.rotation.z = p[2];
      this.setLine(k.rtrack, R.pts.slice(0, kk + 1).map((q) => [q[0], q[1], 0.3]));
    }
  },
});
