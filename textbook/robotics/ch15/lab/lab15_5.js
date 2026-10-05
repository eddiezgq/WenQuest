// 实验 15.5 初值与吸引域（配 15.5 节）。
// 机器人场景：UR5e，目标位姿同算例 15.1.2（由 θ* = (30°, −60°, 90°, −120°, −90°, 45°) 算出）。初值平面：起点
//   θ = (θ₁, −60°, θ₃, −120°, −90°, 45°)，θ₁、θ₃ 各取 −180°、−170°、…、170° 共 36 个值（算例 15.5.1 的粗网格）。三种做法：
//   0 牛顿-拉夫森（式 (15.1.8)），至多 60 次；1 限步长的牛顿-拉夫森（每步各关节 ≤ 0.5 rad，式 (15.5.3)），至多 200 次；
//   2 延拓法（式 (15.5.4)）：目标 T₀ e^{(j/10)[V₀]}，j = 1…10，每段至多 8 次牛顿迭代（中间各段到 10⁻⁸），最后一段至多 40 次。
//   收敛判据 ‖ω_b‖、‖v_b‖ < 10⁻¹⁰。终点用 14.5 节的解析逆解编号（同表 14.5.1，肩 A 在前、腕不翻在前、肘上在前），
//   起点的肩、肘、腕标签按 14.5 节的定义判断。“画吸引域”逐格计算整张图（与图 15.5.2 相同的做法，网格粗一些）。
// 生活场景：分水岭。地形 f(x, y) = 0.08(x² + y²) − Σ aᵢ exp(−|p − cᵢ|²/(2sᵢ²))，三个湖；雨滴按梯度下降 p ← p − α∇f 流动。
//   α 小时雨滴沿山坡流进最近的湖；α 大时一步跨过山脊，落进别的湖（与 15.2 节步长过大、15.5 节牛顿法乱跳同理）。
WQ.lab({
  title: ["实验 15.5 初值与吸引域", "Lab 15.5 Starting points and basins of attraction"],
  goal: ["在 UR5e 的初值平面上看三种做法各自收敛到哪一组解：牛顿-拉夫森的吸引域支离破碎，限步长后整齐得多，延拓法只要成功就留在起点的构型上。",
         "On the UR5e's plane of starting points, see which solution each of three methods reaches: Newton-Raphson's basins are fragmented, a step limit makes them much tidier, and continuation, whenever it succeeds, keeps the starting posture."],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 的初值平面", "UR5e starting-point plane"], hide: ["dx", "dy", "alpha"],
      problem: { title: ["机器人问题：从哪里出发，就到哪一组解", "Robot problem: where you start decides the solution you get"],
                 text: ["左图每一格是一个起点（横轴 θ₁，纵轴 θ₃，其余关节同 θ*），颜色是它收敛到的解（编号同表 14.5.1）。用滑块选起点，按“求解”；按“画吸引域”画出整张图。右边灰色为起点的手臂，蓝色为所得的解。",
                        "Each cell of the map is a start (θ₁ across, θ₃ up, other joints as θ*); its colour is the solution reached (numbered as in Table 14.5.1). Choose a start with the sliders and press “Solve”; press “Draw basins” for the whole map. Right: the starting arm (grey) and the solution (blue)."] } },
    { id: "rain", name: ["分水岭", "Watershed"], hide: ["method", "t1", "t3"],
      problem: { title: ["生活中的例子：雨落在山脊附近，流进哪个湖？", "Everyday example: rain near a ridge — which lake does it reach?"],
                 text: ["等高线图上有西、东、南三个湖。雨滴每一步沿最陡的方向走 α 倍梯度。蓝色虚线是小步长（α = 0.05）的路径，橙色是所选步长的路径。",
                        "The contour map has a west, an east and a south lake. Each step the raindrop moves α times the gradient downhill. Blue dashed: small steps (α = 0.05); orange: the chosen step."] } },
  ],
  params: [
    { id: "method", name: ["做法：0 牛顿-拉夫森 / 1 限步长 / 2 延拓法", "method: 0 Newton-Raphson / 1 step-limited / 2 continuation"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "t1", name: ["起点 θ₁", "start θ₁"], min: -180, max: 170, step: 10, value: -160, unit: "°", digits: 0 },
    { id: "t3", name: ["起点 θ₃", "start θ₃"], min: -180, max: 170, step: 10, value: 150, unit: "°", digits: 0 },
    { id: "dx", name: ["雨滴落点 x", "raindrop x"], min: -1.5, max: 1.5, step: 0.1, value: 0.0, unit: "", digits: 1 },
    { id: "dy", name: ["雨滴落点 y", "raindrop y"], min: -1.5, max: 1.5, step: 0.1, value: 0.7, unit: "", digits: 1 },
    { id: "alpha", name: ["步长 α", "step α"], min: 0.05, max: 0.7, step: 0.05, value: 0.05, unit: "", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["求解", "Solve"], primary: true }, { id: "map", name: ["画吸引域", "Draw basins"] }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "#08519c", name: ["肩 A", "shoulder A"] }, { color: "#b8860b", name: ["肩 B", "shoulder B"] }, { color: "#d9d9d9", name: ["不收敛", "not converged"] }],
  tasks: [
    { id: "nr", robot: true, text: ["牛顿-拉夫森从起点 (θ₁, θ₃) = (−160°, 150°) 出发，跳到了肩部另一侧（肩 B）的解。", "Newton-Raphson from (θ₁, θ₃) = (−160°, 150°) jumps to a solution on the other side of the shoulder (shoulder B)."],
      demo: { scene: "ur", set: { method: 0, t1: -160, t3: 150 }, press: ["start"], wait: 4 } },
    { id: "cont", robot: true, text: ["延拓法从同一起点出发，收敛到与起点肩、肘、腕标签相同的解。", "Continuation from the same start converges to the solution with the same shoulder, elbow and wrist labels as the start."],
      demo: { scene: "ur", set: { method: 2, t1: -160, t3: 150 }, press: ["start"], wait: 4 } },
    { id: "map", robot: true, text: ["画出限步长牛顿-拉夫森的吸引域：收敛的起点超过 90%。", "Draw the basins of the step-limited Newton-Raphson: over 90% of the starts converge."],
      demo: { scene: "ur", set: { method: 1 }, press: ["map"], wait: 60 } },
    { id: "rain", text: ["生活场景：雨滴落在 (0.0, 0.7)，把步长加大到 0.6：雨滴跨过山脊，流进了与小步长不同的湖。", "Everyday scene: a raindrop at (0.0, 0.7); raise the step to 0.6: it jumps the ridge into a different lake than with small steps."],
      demo: { scene: "rain", set: { dx: 0.0, dy: 0.7, alpha: 0.6 }, press: ["start"], wait: 4 } },
  ],
  think: ["延拓法在图中有大片不收敛的区域，而限步长的牛顿法几乎处处收敛。延拓法失败时发生了什么（提示：看失败处的最小奇异值）？实用的求解器怎样把两者结合起来？",
          "Continuation leaves large regions unconverged, while the step-limited Newton converges almost everywhere. What happens when continuation fails (hint: look at the smallest singular value there)? How does a practical solver combine the two?"],

  // ---------------- UR5e 几何（表 12.1.1）与 SE(3) 运算（与实验 15.1 相同）
  G: { H1: 0.163, W1: 0.138, L1: 0.425, W2: 0.131, L2: 0.392, W3: 0.127, H2: 0.1, W4: 0.1 },
  STAR: [30, -60, 90, -120, -90, 45], N: 36,
  COLORS: ["#d9d9d9", "#08519c", "#6baed6", "#1f9e89", "#a1d99b", "#b8860b", "#f2c14e", "#d62728", "#fb9a99"],
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
    if (this._ax) return this._ax;
    const g = this.G, Y = [0, -1, 0];
    this._ax = [[[0, 0, 1], [0, 0, g.H1]], [Y, [0, -g.W1, g.H1]], [Y, [-g.L1, -g.W1 + g.W2, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2, g.H1]],
                [[0, 0, -1], [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1 - g.H2]]];
    return this._ax;
  },
  M() { const g = this.G; return { R: [[1, 0, 0], [0, -1, 0], [0, 0, -1]], p: [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3 - g.W4, g.H1 - g.H2] }; },
  E(i, t) { const [w, q] = this.AX()[i], R = this.rot(w, t); return { R, p: this.sub(q, this.mv(R, q)) }; },
  comp(A, B) { return { R: this.mm(A.R, B.R), p: this.add(this.mv(A.R, B.p), A.p) }; },
  inv(A) { const Rt = this.tr(A.R); return { R: Rt, p: this.mul(this.mv(Rt, A.p), -1) }; },
  act(A, x) { return this.add(this.mv(A.R, x), A.p); },
  fk(th) { let T = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] }; th.forEach((t, i) => { T = this.comp(T, this.E(i, t)); }); return this.comp(T, this.M()); },
  logR(R) {
    const c = Math.max(-1, Math.min(1, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)), th = Math.acos(c);
    const d = [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]];
    if (th < 1e-9) return this.mul(d, 0.5);
    if (Math.PI - th < 1e-6) {
      const B = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (R[i][j] + (i === j ? 1 : 0)) / 2)), k = [0, 1, 2].reduce((a, i) => (B[i][i] > B[a][a] ? i : a), 0);
      return this.mul([B[0][k], B[1][k], B[2][k]], th / Math.sqrt(B[k][k]));
    }
    return this.mul(d, th / (2 * Math.sin(th)));
  },
  log6(T) {
    const wt = this.logR(T.R), th = this.norm(wt);
    if (th < 1e-12) return [0, 0, 0, ...T.p];
    const w = this.mul(wt, 1 / th), p = T.p, wp = this.cross(w, p), wwp = this.cross(w, wp);
    const k = 1 / th - 0.5 / Math.tan(th / 2);
    return [...wt, ...[0, 1, 2].map((i) => th * (p[i] / th - 0.5 * wp[i] + k * wwp[i]))];
  },
  exp6(V) {                                       // e^{[V]}，V 不必是单位旋量（定理 6.4.1）
    const w = V.slice(0, 3), v = V.slice(3), th = this.norm(w);
    if (th < 1e-12) return { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: v };
    const u = this.mul(w, 1 / th), vu = this.mul(v, 1 / th), R = this.rot(u, th);
    const uv = this.cross(u, vu), uuv = this.cross(u, uv);
    return { R, p: [0, 1, 2].map((i) => th * vu[i] + (1 - Math.cos(th)) * uv[i] + (th - Math.sin(th)) * uuv[i]) };
  },
  jb(th) {
    const A = this.AX(), T = this.fk(th), Rt = this.tr(T.R), out = [];
    let P = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] };
    for (let i = 0; i < 6; i++) {
      const w = this.mv(P.R, A[i][0]), q = this.act(P, A[i][1]), v = this.mul(this.cross(w, q), -1);
      out.push([...this.mv(Rt, w), ...this.mv(Rt, this.sub(v, this.cross(T.p, w)))]);
      P = this.comp(P, this.E(i, th[i]));
    }
    return [0, 1, 2, 3, 4, 5].map((r) => out.map((c) => c[r]));
  },
  solve(A, b) {                                   // 列主元高斯消去；奇异返回 null
    const n = b.length, M = A.map((r, i) => [...r, b[i]]);
    for (let i = 0; i < n; i++) {
      let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(M[j][i]) > Math.abs(M[p][i])) p = j;
      if (Math.abs(M[p][i]) < 1e-13) return null;
      [M[i], M[p]] = [M[p], M[i]];
      for (let j = i + 1; j < n; j++) { const f = M[j][i] / M[i][i]; for (let k = i; k <= n; k++) M[j][k] -= f * M[i][k]; }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let s = M[i][n]; for (let k = i + 1; k < n; k++) s -= M[i][k] * x[k]; x[i] = s / M[i][i]; }
    return x;
  },
  // ---------------- 14.5 节的解析逆解（给终点编号）与构型标签
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
  theta1(Td) {
    const g = this.G, d4 = g.W1 - g.W2 + g.W3, yb = [Td.R[0][1], Td.R[1][1], Td.R[2][1]], pw = this.sub(Td.p, this.mul(yb, g.W4)), rho = Math.hypot(pw[0], pw[1]);
    if (rho < d4 - 1e-12) return [];
    const base = Math.atan2(pw[0], -pw[1]), gam = Math.atan2(Math.sqrt(Math.max(0, rho * rho - d4 * d4)), d4);
    return [base + gam, base - gam];
  },
  labels(th) {                                    // 任意一组关节角的肩、肘、腕标签（14.5 节）
    const t1 = this.theta1(this.fk(th)), dA = t1.length ? Math.abs(this.wrap(th[0] - t1[0])) : 0, dB = t1.length ? Math.abs(this.wrap(th[0] - t1[1])) : 1;
    return { sh: dA < dB ? "A" : "B", up: this.elbowUp(th), nf: Math.sin(th[4]) > 0 };
  },
  ik(Td) {
    const A = this.AX(), Y = [0, -1, 0], out = [];
    [[1, 0], [-1, 1]].forEach(([s1, j]) => {
      const t1 = this.theta1(Td)[j]; if (t1 === undefined) return;
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
  target() { if (!this._td) this._td = this.fk(this.STAR.map((d) => d * Math.PI / 180)); return this._td; },
  table() { if (!this._tab) this._tab = this.ik(this.target()); return this._tab; },
  classify(th) { const k = this.table().findIndex((x) => x.th.every((v, i) => Math.abs(this.wrap(v - th[i])) < 1e-6)); return k + 1; },
  // ---------------- 三种做法
  newton(th, Td, iters, stepMax, tol) {
    th = th.slice(); tol = tol || 1e-10;
    for (let k = 0; k <= iters; k++) {
      const V = this.log6(this.comp(this.inv(this.fk(th)), Td));
      if (this.norm(V.slice(0, 3)) < tol && this.norm(V.slice(3)) < tol) return { th, ok: true, k };
      if (k === iters) break;
      let d = this.solve(this.jb(th), V);
      if (!d) return { th, ok: false, k };
      if (stepMax) { const m = Math.max(...d.map(Math.abs)); if (m > stepMax) d = d.map((x) => x * stepMax / m); }
      if (d.some((x) => !isFinite(x) || Math.abs(x) > 1e3)) return { th, ok: false, k };
      th = th.map((x, i) => x + d[i]);
    }
    return { th, ok: false, k: iters };
  },
  solveFrom(th0, m) {
    const Td = this.target();
    if (m === 0) return this.newton(th0, Td, 60);
    if (m === 1) return this.newton(th0, Td, 200, 0.5);
    const T0 = this.fk(th0), V0 = this.log6(this.comp(this.inv(T0), Td));
    let th = th0.slice(), tot = 0;
    for (let j = 1; j <= 10; j++) {
      const Tj = this.comp(T0, this.exp6(V0.map((x) => x * j / 10)));
      const r = this.newton(th, Tj, j === 10 ? 40 : 8, null, j === 10 ? 1e-10 : 1e-8);
      tot += r.k;
      if (!r.ok) return { th: r.th, ok: false, k: tot };
      th = r.th;
    }
    return { th, ok: true, k: tot };
  },
  startTh(api) { const r = (d) => d * Math.PI / 180; return [r(api.p.t1), r(this.STAR[1]), r(api.p.t3), r(this.STAR[3]), r(this.STAR[4]), r(this.STAR[5])]; },
  // ---------------- 分水岭
  LAKES: [[-1.2, 0.4, 0.6, 1.0], [1.1, 0.6, 0.55, 0.9], [0.1, -1.1, 0.65, 1.1]],
  height(x, y) { let f = 0.08 * (x * x + y * y); for (const [cx, cy, s, a] of this.LAKES) f -= a * Math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s)); return f; },
  grad(p) { let gx = 0.16 * p[0], gy = 0.16 * p[1];
    for (const [cx, cy, s, a] of this.LAKES) { const dx = p[0] - cx, dy = p[1] - cy, e = a * Math.exp(-(dx * dx + dy * dy) / (2 * s * s)) / (s * s); gx += e * dx; gy += e * dy; }
    return [gx, gy]; },
  flow(p, a, n) { const P = [p.slice()]; for (let i = 0; i < n; i++) { const g = this.grad(p); p = [p[0] - a * g[0], p[1] - a * g[1]]; P.push(p); if (Math.abs(p[0]) > 3 || Math.abs(p[1]) > 3) break; } return P; },
  lake(p) { let b = -1, d = 1e9; this.LAKES.forEach((c, i) => { const q = Math.hypot(p[0] - c[0], p[1] - c[1]); if (q < d) { d = q; b = i; } }); return d < 0.4 ? b : -1; },

  reset(api, s) {
    s.res = null; s.done = false; s.clock = 0;
    s.th0 = this.startTh(api);
    if (api.scene === "ur") s.lab0 = this.labels(s.th0);
    else { s.small = this.flow([api.p.dx, api.p.dy], 0.05, 1500); s.big = null; }
  },
  compute(api, s) {
    if (api.scene === "ur") { s.res = this.solveFrom(s.th0, api.p.method); s.res.idx = s.res.ok ? this.classify(s.res.th) : 0; }
    else { s.big = this.flow([api.p.dx, api.p.dy], api.p.alpha, 300); }
    s.done = true;
  },
  maps: {},                                       // 已画好的吸引域图，按做法保存（改滑块不丢）
  action(id, api, s) { if (id === "map" && api.scene === "ur") { this.maps[api.p.method] = { m: api.p.method, cells: [], next: 0 }; s.done = true; api.running = true; } },
  update(dt, api, s) {
    const map = this.maps[api.p.method];
    if (api.scene === "ur" && map && map.next < this.N * this.N) {
      const r = (d) => d * Math.PI / 180;
      const t0 = performance.now();                 // 每次最多算 25 ms，画面不卡
      for (let c = 0; map.next < this.N * this.N && (c < 4 || performance.now() - t0 < 25); c++) {
        const i = map.next, t1 = -180 + 10 * (i % this.N), t3 = -180 + 10 * Math.floor(i / this.N);
        const th0 = [r(t1), r(this.STAR[1]), r(t3), r(this.STAR[3]), r(this.STAR[4]), r(this.STAR[5])];
        const res = this.solveFrom(th0, map.m), idx = res.ok ? this.classify(res.th) : 0, L0 = this.labels(th0);
        const tb = idx ? this.table()[idx - 1] : null;
        map.cells.push({ idx, same: !!tb && (tb.sh > 0 ? "A" : "B") === L0.sh && tb.up === L0.up && tb.nf === L0.nf });
        map.next += 1;
      }
      if (map.next >= this.N * this.N) api.stop();
      return;
    }
    if (!s.done) { this.compute(api, s); api.stop(); }
  },
  readouts(api, s) {
    if (api.scene === "rain") {
      const ln = [api.T("西湖", "west lake"), api.T("东湖", "east lake"), api.T("南湖", "south lake")];
      const ls = this.lake(s.small[s.small.length - 1]), lb = s.big ? this.lake(s.big[s.big.length - 1]) : null;
      if (s.big && Math.abs(api.p.alpha - 0.6) < 1e-9 && Math.abs(api.p.dx) < 1e-9 && Math.abs(api.p.dy - 0.7) < 1e-9 && ls >= 0 && lb >= 0 && lb !== ls) api.done("rain");
      return [[["小步长（α = 0.05）流进", "small steps (α = 0.05) reach"], ls >= 0 ? ln[ls] : "—"],
              [["所选步长流进", "chosen step reaches"], s.big ? (lb >= 0 ? ln[lb] : api.T("没有停下", "does not settle")) : "—"],
              [["步长 α", "step α"], api.p.alpha.toFixed(2)]];
    }
    const nm = [api.T("牛顿-拉夫森", "Newton-Raphson"), api.T("限步长的牛顿-拉夫森", "step-limited Newton-Raphson"), api.T("延拓法", "continuation")];
    const lb = (o) => `${o.sh} · ${o.up ? api.T("上", "up") : api.T("下", "down")} · ${o.nf ? api.T("不翻", "no flip") : api.T("翻", "flip")}`;
    const rows = [[["做法", "method"], nm[api.p.method]], [["起点 (θ₁, θ₃)", "start (θ₁, θ₃)"], `(${api.p.t1}°, ${api.p.t3}°)`], [["起点的构型（肩 · 肘 · 腕）", "start posture (shoulder · elbow · wrist)"], lb(s.lab0)]];
    if (s.res) {
      const tb = s.res.idx ? this.table()[s.res.idx - 1] : null, same = !!tb && (tb.sh > 0 ? "A" : "B") === s.lab0.sh && tb.up === s.lab0.up && tb.nf === s.lab0.nf;
      rows.push([["结果", "result"], s.res.ok ? `${api.T("第 ", "no. ")}${s.res.idx}${api.T(" 组", "")}（${lb({ sh: tb.sh > 0 ? "A" : "B", up: tb.up, nf: tb.nf })}）` : api.T("不收敛", "not converged")]);
      rows.push([["迭代次数", "iterations"], String(s.res.k)], [["与起点构型相同", "same posture as start"], s.res.ok ? (same ? api.T("是", "yes") : api.T("否", "no")) : "—"]);
      if (api.p.method === 0 && api.p.t1 === -160 && api.p.t3 === 150 && s.res.ok && tb.sh < 0) api.done("nr");
      if (api.p.method === 2 && api.p.t1 === -160 && api.p.t3 === 150 && s.res.ok && same) api.done("cont");
    }
    const map = this.maps[api.p.method];
    if (map) {
      const n = map.cells.length, conv = map.cells.filter((c) => c.idx > 0).length, same = map.cells.filter((c) => c.same).length;
      rows.push([["吸引域图", "basin map"], `${n} / ${this.N * this.N}`], [["收敛的起点", "converged starts"], n ? (100 * conv / n).toFixed(1) + "%" : "—"],
                [["保持起点构型", "kept the starting posture"], n ? (100 * same / n).toFixed(1) + "%" : "—"]);
      if (n === this.N * this.N && map.m === 1 && conv / n > 0.9) api.done("map");
    }
    return rows;
  },
  draw(api, s) {
    const { w, h, ctx } = api;
    if (api.scene === "rain") {
      const sz = Math.min(w * 0.62, h * 0.92), x0 = w * 0.04, y0 = (h - sz) / 2, X = (p) => [x0 + (p[0] + 1.6) / 3.2 * sz, y0 + (1.6 - p[1]) / 3.2 * sz];
      const n = 64, cw = sz / n;
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
        const x = -1.6 + 3.2 * (j + 0.5) / n, y = 1.6 - 3.2 * (i + 0.5) / n, f = this.height(x, y), t = Math.max(0, Math.min(1, (f + 0.9) / 1.3));
        ctx.fillStyle = f < -0.55 ? `rgba(31,111,235,${0.25 + 0.5 * (-0.55 - f)})` : `rgb(${Math.round(150 + 90 * t)},${Math.round(170 + 60 * t)},${Math.round(120 + 70 * t)})`;
        ctx.fillRect(x0 + j * cw, y0 + i * cw, cw + 0.5, cw + 0.5);
      }
      api.rect(x0, y0, sz, sz, null, api.css("--line"));
      [[api.T("西湖", "W"), -1.2, 0.4], [api.T("东湖", "E"), 1.1, 0.6], [api.T("南湖", "S"), 0.1, -1.1]].forEach(([t, x, y]) => { const P = X([x, y]); api.label(t, P[0], P[1] + 4, api.css("--ink"), 13, "center"); });
      const path = (P, col, dash) => { ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.setLineDash(dash || []); ctx.beginPath(); P.forEach((p, i) => { const q = X(p); if (i) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]); }); ctx.stroke(); ctx.setLineDash([]); };
      path(s.small, api.css("--blue"), [5, 4]);
      if (s.big) { path(s.big, api.css("--amber")); s.big.slice(0, 40).forEach((p) => { const q = X(p); api.circle(q[0], q[1], 2.5, api.css("--amber")); }); }
      const D = X([api.p.dx, api.p.dy]); api.circle(D[0], D[1], 5, api.css("--red"));
      return;
    }
    // 吸引域图
    const sz = Math.min(w * 0.45, h * 0.9), x0 = w * 0.06, y0 = (h - sz) / 2, cw = sz / this.N;
    ctx.fillStyle = "#f6f8fa"; ctx.fillRect(x0, y0, sz, sz);
    const map = this.maps[api.p.method];
    if (map) map.cells.forEach((c, i) => { ctx.fillStyle = this.COLORS[c.idx]; ctx.fillRect(x0 + (i % this.N) * cw, y0 + sz - (Math.floor(i / this.N) + 1) * cw, cw + 0.5, cw + 0.5); });
    api.rect(x0, y0, sz, sz, null, api.css("--line"));
    if (!map) api.label(api.T("按“画吸引域”画出这种做法的整张图", "Press “Draw basins” for this method's map"), x0 + sz / 2, y0 + sz / 2, api.css("--muted"), 13, "center");
    const cx = x0 + (api.p.t1 + 180) / 10 * cw + cw / 2, cy = y0 + sz - ((api.p.t3 + 180) / 10 * cw + cw / 2);
    api.circle(cx, cy, 6, null, api.css("--red")); api.circle(cx, cy, 2.5, api.css("--red"));
    const sx = x0 + (30 + 180) / 10 * cw + cw / 2, sy = y0 + sz - ((90 + 180) / 10 * cw + cw / 2);
    api.label("θ*", sx + 6, sy - 6, api.css("--ink"), 12);
    api.label("θ₁ →", x0 + sz - 30, y0 + sz + 16, api.css("--muted"), 12); api.label("θ₃ ↑", x0 - 4, y0 - 6, api.css("--muted"), 12);
    api.label("−180°", x0, y0 + sz + 16, api.css("--muted"), 11); api.label("170°", x0 + sz - 70, y0 + sz + 16, api.css("--muted"), 11);
    // 手臂（斜视投影）：灰色为起点，蓝色为所得的解；红点为目标法兰中心
    const az = -2.4, el = 0.35, sc = h * 0.36, ox = w * 0.76, oy = h * 0.66;   // 视线大致从目标一侧看过去
    const Pj = (p) => { const x = Math.cos(az) * p[0] + Math.sin(az) * p[1], y = -Math.sin(az) * p[0] + Math.cos(az) * p[1];
      return [ox + sc * x, oy - sc * (Math.cos(el) * p[2] - Math.sin(el) * y)]; };
    api.line(...Pj([-0.6, 0, 0]), ...Pj([0.6, 0, 0]), api.css("--grid"), 1); api.line(...Pj([0, -0.6, 0]), ...Pj([0, 0.6, 0]), api.css("--grid"), 1);
    const drawArm = (th, col, wd) => { const P = this.chain(th).map(Pj); for (let i = 0; i + 1 < P.length; i++) api.line(P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], col, wd); };
    drawArm(s.th0, "rgba(110,118,129,0.7)", 4);
    if (s.res && s.res.ok) drawArm(s.res.th, api.css("--blue"), 6);
    const T = Pj(this.target().p); api.circle(T[0], T[1], 5, api.css("--red"));
  },
});
