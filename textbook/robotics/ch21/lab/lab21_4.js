// 实验 21.4 给定航点生成飞行轨迹（配 21.4 节）。
// 场景“数字工厂巡检”：七个航点与程序 21.4.1 相同（本章坐标，x 沿车间长边，y = 28 − y_工厂，z 向上，示意值）；
//   第三个航点 W2（热处理炉顶）的高度可调。最小 k 阶导数样条按定理 21.4.2 的线性方程组求解（每段 2k − 1 次多项式，
//   中间航点 1～2k − 2 阶导数连续，起止点 1～k − 1 阶导数为零）。各段时长 = 总时间 × 程序 21.4.1 优化得到的比例
//   (0.1997, 0.1219, 0.1824, 0.1292, 0.1275, 0.2393)。偏航角保持 0。沿途按定理 21.4.1 求倾角、总推力 f = m‖p̈ + 𝔤ẑ‖、
//   物体角速度（式 (21.4.2)、(21.4.3)）。三维车间与第 19 章实验相同；X2 放大 4 倍画出，按实际速度播放。
// 生活场景“电梯”：1 楼到 10 楼，27 m，起止静止的单段最小 k 阶导数多项式；显示最大加速度和最大加加速度。
WQ.lab({
  title: ["实验 21.4 给定航点生成飞行轨迹", "Lab 21.4 Flight trajectories through waypoints"],
  goal: ["由给定的航点生成最小 snap 轨迹，用微分平坦性求出沿途的倾角、推力和角速度；通过时间缩放找出不超限的最快轨迹；比较不同阶数 k 的轨迹在航点处的光滑程度。",
         "Generate a minimum-snap trajectory through given waypoints and use flatness to get the tilt, thrust and body rates along it; find the fastest trajectory within the limits by time scaling; compare how smooth the paths of different order k are at the waypoints."],
  view: "3d",
  models: ["B-UAV-X2"],
  scenes: [
    { id: "inspect", robot: true, name: ["数字工厂巡检", "Digital-factory inspection"], hide: ["tl"],
      problem: { title: ["机器人问题：七个航点，怎样飞得又快又稳", "Robot problem: seven waypoints, fast and smooth"],
                 text: ["X2 从左侧主通道上方 1 m 起飞，经热处理炉、磨床、检测台的上方，降到第二条主通道上方。调节 k、总时间和炉顶航点的高度，按“开始”飞一遍。限制（示意值）：倾角 ≤ 30°，总推力 ≤ 39 N，角速度 ≤ 2 rad/s。",
                        "X2 takes off 1 m above the left aisle, passes over the furnace, the grinder and the inspection bench, and comes down over the second aisle. Set k, the total time and the furnace waypoint's height and press Start. Limits (illustrative): tilt ≤ 30°, thrust ≤ 39 N, body rate ≤ 2 rad/s."] } },
    { id: "lift", name: ["电梯", "Elevator"], hide: ["T", "h3"],
      problem: { title: ["生活中的例子：电梯怎样起动和停止才平稳", "Everyday example: a smooth elevator ride"],
                 text: ["电梯从 1 楼运行到 10 楼（27 m），起止静止。用同样的最小 k 阶导数多项式规划运行曲线，看最大加速度和加加速度，以及起动瞬间加加速度是否突变。",
                        "The elevator travels from floor 1 to floor 10 (27 m), at rest at both ends. Plan its motion with the same minimum-k polynomials and look at the peak acceleration and jerk, and whether the jerk jumps at the start."] } },
  ],
  params: [
    { id: "k", name: ["阶数 k（2 加速度，3 加加速度，4 snap）", "order k (2 accel., 3 jerk, 4 snap)"], min: 2, max: 4, step: 1, value: 4, digits: 0 },
    { id: "T", name: ["总时间", "total time"], min: 8, max: 30, step: 0.1, value: 20.4, unit: "s", digits: 1 },
    { id: "h3", name: ["炉顶航点 W2 的高度", "height of furnace waypoint W2"], min: 2, max: 5, step: 0.1, value: 3.5, unit: "m", digits: 1 },
    { id: "tl", name: ["电梯运行时间", "elevator travel time"], min: 6, max: 30, step: 0.5, value: 12, unit: "s", digits: 1 },
  ],
  tasks: [
    { id: "fly", robot: true, text: ["按默认参数（k = 4、20.4 s、W2 高 3.5 m）飞完最小 snap 轨迹。", "Fly the minimum-snap trajectory with the defaults (k = 4, 20.4 s, W2 at 3.5 m)."],
      demo: { scene: "inspect", set: { k: 4, T: 20.4, h3: 3.5 }, press: ["start"], wait: 60 } },
    { id: "fast", robot: true, text: ["k = 4、W2 高 3.5 m，缩短总时间，使最大倾角不超过 30°、总时间不超过 12.9 s，飞一遍。", "k = 4, W2 at 3.5 m: shorten the total time so that the peak tilt stays within 30° and the time is at most 12.9 s; fly it."],
      demo: { scene: "inspect", set: { k: 4, T: 12.4, h3: 3.5 }, press: ["start"], wait: 45 } },
    { id: "k2", robot: true, text: ["改用 k = 2（总时间 20.4 s）飞一遍，读出航点处角速度的跳变（超过 0.1 rad/s）。", "Use k = 2 (20.4 s) and fly; read the jump of the body rate at the waypoints (above 0.1 rad/s)."],
      demo: { scene: "inspect", set: { k: 2, T: 20.4, h3: 3.5 }, press: ["start"], wait: 60 } },
    { id: "lift", text: ["电梯取 k = 4，选择运行时间使最大加速度不超过 1 m/s²，运行一次。", "Elevator with k = 4: choose the travel time so the peak acceleration is at most 1 m/s², and run it."],
      demo: { scene: "lift", set: { k: 4, tl: 15 }, press: ["start"], wait: 40 } },
  ],
  think: ["把 W2 的高度从 3.5 m 加到 5 m，不超限的最短时间变长还是变短？哪个限制起作用？",
          "Raise W2 from 3.5 m to 5 m. Does the shortest feasible time grow or shrink? Which limit binds?"],

  M: 1.325, G: 9.81, CZ: 0.053962, SCALE: 4,
  WP: [[7, 19, 1.0], [12, 19, 3.0], [17, 15, 3.5], [24, 19, 3.0], [31, 15, 3.0], [38, 15, 3.0], [38, 9.5, 1.0]],
  RATIO: [0.1997077, 0.1219154, 0.1824121, 0.1291666, 0.1275301, 0.2392681],
  SHOP: [["ht-01", "热处理炉", "furnace", 17, 13, 5, 4], ["grd-01", "磨床", "grinder", 31, 13, 4.5, 2.2], ["qc-01", "检测台", "inspection", 38, 13, 4, 3],
         ["cnc-l01-a", "数控车床 A", "lathe A", 17, 4, 4, 2.2], ["cnc-l01-b", "数控车床 B", "lathe B", 24, 4, 4, 2.2], ["saw-01", "带锯床", "band saw", 10, 4, 4, 2.5],
         ["key-01", "键槽铣床", "keyway miller", 31, 4, 3, 2.2], ["store-01", "原料库", "raw store", 3, 4, 4, 5], ["vmc-01", "立式加工中心", "VMC", 10, 22, 3.5, 3],
         ["hmc-01", "卧式加工中心", "HMC", 17, 22, 4.5, 3.5], ["hob-01", "滚齿机", "gear hobber", 24, 22, 3.5, 2.5], ["asm-01", "装配台", "assembly", 31, 22, 5, 3],
         ["test-01", "试验台", "test bench", 38, 22, 3.5, 2.5], ["store-02", "成品库", "product store", 45, 22, 4, 5]],

  // ---------------- 最小 k 阶导数样条（定理 21.4.2）
  fact(n, r) { if (r > n) return 0; let o = 1; for (let i = 0; i < r; i++) o *= n - i; return o; },
  solveLin(A, B) {   // 高斯消去（部分选主元），B 为若干列
    const n = A.length, m = B[0].length;
    for (let c = 0; c < n; c++) {
      let p = c;
      for (let r = c + 1; r < n; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      [A[c], A[p]] = [A[p], A[c]]; [B[c], B[p]] = [B[p], B[c]];
      for (let r = c + 1; r < n; r++) {
        const f = A[r][c] / A[c][c];
        if (f === 0) continue;
        for (let k = c; k < n; k++) A[r][k] -= f * A[c][k];
        for (let k = 0; k < m; k++) B[r][k] -= f * B[c][k];
      }
    }
    const X = Array.from({ length: n }, () => new Array(m).fill(0));
    for (let r = n - 1; r >= 0; r--) for (let k = 0; k < m; k++) {
      let s = B[r][k];
      for (let c = r + 1; c < n; c++) s -= A[r][c] * X[c][k];
      X[r][k] = s / A[r][r];
    }
    return X;
  },
  spline(W, Ts, k) {
    const M = Ts.length, N = 2 * k, dim = W[0].length, A = [], B = [];
    const put = (j, s, r) => { const v = new Array(N * M).fill(0); for (let n = r; n < N; n++) v[j * N + n] = this.fact(n, r) * Math.pow(s, n - r) / Math.pow(Ts[j], r); return v; };
    const add = (v, b) => { A.push(v); B.push(b ? b.slice() : new Array(dim).fill(0)); };
    add(put(0, 0, 0), W[0]);
    for (let r = 1; r < k; r++) add(put(0, 0, r));
    for (let j = 0; j < M - 1; j++) {
      add(put(j, 1, 0), W[j + 1]); add(put(j + 1, 0, 0), W[j + 1]);
      for (let r = 1; r < 2 * k - 1; r++) { const a = put(j, 1, r), b = put(j + 1, 0, r); add(a.map((x, i) => x - b[i])); }
    }
    add(put(M - 1, 1, 0), W[M - 1 + 1]);
    for (let r = 1; r < k; r++) add(put(M - 1, 1, r));
    const X = this.solveLin(A, B);
    const tt = [0]; Ts.forEach((x) => tt.push(tt[tt.length - 1] + x));
    return { X, Ts, tt, N, dim, k };
  },
  ev(S, t, r) {
    let j = 0;
    while (j < S.Ts.length - 1 && t >= S.tt[j + 1]) j++;
    const s = (Math.min(Math.max(t, 0), S.tt[S.tt.length - 1]) - S.tt[j]) / S.Ts[j], out = new Array(S.dim).fill(0);
    for (let n = r; n < S.N; n++) { const c = this.fact(n, r) * Math.pow(s, n - r); for (let d = 0; d < S.dim; d++) out[d] += S.X[j * S.N + n][d] * c; }
    return out.map((x) => x / Math.pow(S.Ts[j], r));
  },
  // ---------------- 平坦映射（偏航角为 0）
  flat(a, j) {
    const t = [a[0], a[1], a[2] + this.G], nt = Math.hypot(...t), zb = t.map((x) => x / nt);
    const yc = [0, 1, 0];
    let xb = [yc[1] * zb[2] - yc[2] * zb[1], yc[2] * zb[0] - yc[0] * zb[2], yc[0] * zb[1] - yc[1] * zb[0]];
    const nx = Math.hypot(...xb); xb = xb.map((x) => x / nx);
    const yb = [zb[1] * xb[2] - zb[2] * xb[1], zb[2] * xb[0] - zb[0] * xb[2], zb[0] * xb[1] - zb[1] * xb[0]];
    const dot = (u, v) => u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
    const zj = dot(zb, j), h = j.map((x, i) => (x - zj * zb[i]) / nt);
    const wx = -dot(yb, h), wy = dot(xb, h), ph = Math.atan2(-zb[1], Math.hypot(zb[0], zb[2])), th = Math.atan2(zb[0], zb[2]);
    const wz = (-Math.sin(ph) * wy) / Math.cos(ph);
    const R = [[xb[0], yb[0], zb[0]], [xb[1], yb[1], zb[1]], [xb[2], yb[2], zb[2]]];
    return { f: this.M * nt, tilt: Math.acos(zb[2]), w: [wx, wy, wz], R, th, ph };
  },
  build(p) {
    const W = this.WP.map((w) => w.slice()); W[2][2] = p.h3;
    const Ts = this.RATIO.map((r) => r * p.T), S = this.spline(W, Ts, Math.round(p.k));
    let tilt = 0, f = 0, w = 0, v = 0;
    const n = 1500;
    for (let i = 0; i <= n; i++) {
      const t = S.tt[S.tt.length - 1] * i / n, F = this.flat(this.ev(S, t, 2), this.ev(S, t, 3));
      tilt = Math.max(tilt, F.tilt); f = Math.max(f, F.f); w = Math.max(w, Math.hypot(...F.w)); v = Math.max(v, Math.hypot(...this.ev(S, t, 1)));
    }
    let jump = 0;
    for (let j = 1; j < S.tt.length - 1; j++) {
      const e = 1e-7, a = this.flat(this.ev(S, S.tt[j] - e, 2), this.ev(S, S.tt[j] - e, 3)).w, b = this.flat(this.ev(S, S.tt[j] + e, 2), this.ev(S, S.tt[j] + e, 3)).w;
      jump = Math.max(jump, Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]));
    }
    const w0 = Math.hypot(...this.flat(this.ev(S, 0, 2), this.ev(S, 0, 3)).w);
    return { S, W, tilt, f, w, v, jump, w0 };
  },
  lift(k, T) {   // 单段：s(τ) = 27·σ(τ)，σ 由最小 k 阶导数的起止条件定出
    const S = this.spline([[0], [27]], [T], k);
    let a = 0, j = 0;
    for (let i = 0; i <= 2000; i++) { const t = T * i / 2000; a = Math.max(a, Math.abs(this.ev(S, t, 2)[0])); j = Math.max(j, Math.abs(this.ev(S, t, 3)[0])); }
    return { S, a, j, j0: Math.abs(this.ev(S, 0, 3)[0]) };
  },
  // ---------------- 三维
  place(api, R, p, k) {
    const T = api.three, K = api.keep, h = api.m["B-UAV-X2"];
    const c = [p[0] - k * R[0][2] * this.CZ, p[1] - k * R[1][2] * this.CZ, p[2] - k * R[2][2] * this.CZ];
    const Ts = new T.Matrix4().set(R[0][0], R[0][1], R[0][2], c[0], R[1][0], R[1][1], R[1][2], c[1], R[2][0], R[2][1], R[2][2], c[2], 0, 0, 0, 1);
    K.Cm.clone().multiply(Ts).multiply(new T.Matrix4().makeScale(k, k, k)).multiply(K.MhbInv).decompose(h.holder.position, h.holder.quaternion, h.holder.scale);
    h.holder.updateMatrixWorld(true);
  },
  w(api, p) { return new api.three.Vector3(p[0] - 25, p[2], -(p[1] - 14)); },   // 本章坐标 → 三维（车间中心为原点）
  setup3d(api, keep) {
    const T = api.three, h = api.m["B-UAV-X2"];
    h.place(0, 0);
    h.holder.updateMatrixWorld(true);
    keep.Cm = new T.Matrix4().set(1, 0, 0, -25, 0, 0, 1, 0, 0, -1, 0, 14, 0, 0, 0, 1);   // z 向上的本章坐标 → 三维
    keep.MhbInv = new T.Matrix4().copy(h.holder.matrixWorld).invert().multiply(h.nodes.x2.matrixWorld).invert();
    const spec = { floor: { w: 50, d: 28 }, aisles: [{ x: 25, y: 9.0, w: 49, d: 2 }, { x: 25, y: 18.5, w: 49, d: 2 }, { x: 7, y: 13.75, w: 2, d: 9.5 }], units: [], agvs: [] };
    this.SHOP.forEach(([id, z, e, x, y, w, d]) => spec.units.push({ id, name: [z, e], x, y, w, d, h: id.startsWith("store") ? 2.2 : 1.6, store: id.startsWith("store"), highlight: ["ht-01", "grd-01", "qc-01"].includes(id) }));
    keep.shop = WQ3D.workshop(api.st, spec);
    keep.plan = api.trace(0x9aa6ad);
    keep.tr = api.trace(0xe8913a);
    keep.balls = this.WP.map(() => { const b = new T.Mesh(new T.SphereGeometry(0.18, 14, 10), new T.MeshStandardMaterial({ color: 0xd62728 })); api.st.scene.add(b); return b; });
    // 电梯（示意）：井道与轿厢
    const g = new T.Group();
    const shaft = new T.Mesh(new T.BoxGeometry(2.2, 28.5, 2.2), new T.MeshStandardMaterial({ color: 0x9aa6ad, transparent: true, opacity: 0.18 }));
    shaft.position.y = 14.25; g.add(shaft);
    for (let i = 0; i < 10; i++) { const fl = new T.Mesh(new T.BoxGeometry(3.2, 0.06, 3.2), new T.MeshStandardMaterial({ color: 0x5d6b73 })); fl.position.y = 3 * i; g.add(fl); }
    const car = new T.Mesh(new T.BoxGeometry(1.8, 2.4, 1.8), new T.MeshStandardMaterial({ color: 0xe8913a })); car.position.y = 1.2; g.add(car);
    g.position.set(60, 0, 0);
    api.st.scene.add(g);
    keep.lift = g; keep.car = car;
    api.m.fShop = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-20, 0, -8), new T.Vector3(16, 6, 8)) };
    api.m.fLift = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(55, 0, -4), new T.Vector3(65, 29, 4)) };
    keep.shown = null;
  },
  reset(api, s) {
    const K = api.keep;
    s.t = 0; s.ran = false;
    if (!K.Cm) return;
    K.tr.clear(); K.plan.clear();
    if (api.scene === "inspect") {
      s.B = this.build(api.p);
      const S = s.B.S, Tt = S.tt[S.tt.length - 1];
      for (let i = 0; i <= 400; i++) K.plan.add(this.w(api, this.ev(S, Tt * i / 400, 0)));
      s.B.W.forEach((w, i) => K.balls[i].position.copy(this.w(api, w)));
      this.place(api, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], s.B.W[0], this.SCALE);
    } else {
      s.L = this.lift(Math.round(api.p.k), api.p.tl);
      K.car.position.y = 1.2;
    }
  },
  start(api, s) { s.t = 0; },
  update(dt, api, s) {
    if (api.scene === "inspect") {
      const S = s.B.S, Tt = S.tt[S.tt.length - 1];
      s.t = Math.min(Tt, s.t + dt);
      const p = this.ev(S, s.t, 0), F = this.flat(this.ev(S, s.t, 2), this.ev(S, s.t, 3));
      this.place(api, F.R, p, this.SCALE);
      api.keep.tr.add(this.w(api, p));
      s.now = F;
      if (s.t >= Tt - 1e-12) { s.ran = true; api.stop(); }
    } else {
      const T = api.p.tl;
      s.t = Math.min(T, s.t + dt);
      api.keep.car.position.y = 1.2 + this.ev(s.L.S, s.t, 0)[0];
      if (s.t >= T - 1e-12) { s.ran = true; api.stop(); }
    }
  },
  readouts(api, s) {
    const f = api.fmt, d = 180 / Math.PI;
    if (api.scene === "inspect") {
      const B = s.B;
      if (!B) return [];
      const ok = B.tilt * d <= 30 + 1e-9 && B.f <= 39 && B.w <= 2;
      if (s.ran) {
        const p = api.p;
        if (Math.round(p.k) === 4 && Math.abs(p.T - 20.4) < 1e-9 && Math.abs(p.h3 - 3.5) < 1e-9) api.done("fly");
        if (Math.round(p.k) === 4 && Math.abs(p.h3 - 3.5) < 1e-9 && p.T <= 12.9 + 1e-9 && ok) api.done("fast");
        if (Math.round(p.k) === 2 && B.jump > 0.1) api.done("k2");
      }
      return [[["最大倾角（限制 30°）", "peak tilt (limit 30°)"], f(B.tilt * d, 2) + "°"],
              [["最大总推力（限制 39 N）", "peak thrust (limit 39 N)"], f(B.f, 2) + " N"],
              [["最大角速度（限制 2 rad/s）", "peak body rate (limit 2 rad/s)"], f(B.w, 3) + " rad/s"],
              [["航点处角速度的最大跳变", "largest body-rate jump at a waypoint"], f(B.jump, 3) + " rad/s"],
              [["起点的角速度", "body rate at the start"], f(B.w0, 3) + " rad/s"],
              [["最高速度；是否超限", "top speed; within limits"], f(B.v, 2) + " m/s；" + (ok ? api.T("不超限", "yes") : api.T("超限", "no"))],
              [["已飞时间", "time flown"], f(s.t || 0, 1) + " s"]];
    }
    const L = s.L;
    if (!L) return [];
    if (s.ran && Math.round(api.p.k) === 4 && L.a <= 1 + 1e-9) api.done("lift");
    return [[["最大加速度", "peak acceleration"], f(L.a, 3) + " m/s²"],
            [["最大加加速度", "peak jerk"], f(L.j, 3) + " m/s³"],
            [["起动瞬间的加加速度", "jerk at the start"], f(L.j0, 3) + " m/s³"],
            [["当前高度", "height now"], f(this.ev(L.S, s.t || 0, 0)[0], 2) + " m"]];
  },
  draw(api, s) {
    const K = api.keep, m = api.m;
    if (!K || !K.Cm) return;
    const ins = api.scene === "inspect";
    m["B-UAV-X2"].holder.visible = ins; K.shop.group.visible = ins; K.plan.line.visible = ins; K.tr.line.visible = ins;
    K.balls.forEach((b) => { b.visible = ins; });
    K.lift.visible = !ins;
    if (api.st.grid) api.st.grid.visible = !ins;
    if (K.shown !== api.scene) { K.shown = api.scene; ins ? api.view(-10, 55, 1.0, m.fShop) : api.view(30, 15, 0.9, m.fLift); }
  },
});
