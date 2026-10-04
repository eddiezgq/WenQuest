// 实验 5.3 同一个 LU 分解，解一百个不同的右端（配 5.3.4 节）。系数矩阵是按固定种子生成的稠密、对角占优矩阵，
// 作为车间网架刚度矩阵的示意；k 个右端是 k 种载荷工况。两种做法：每个右端都从头消元；先分解 A = LU，再逐个前代、回代。
WQ.lab({
  title: ["实验 5.3 同一个 LU 分解，解一百个不同的右端", "Lab 5.3 One LU factorization, a hundred right-hand sides"],
  goal: ["比较“每次从头消元”与“分解一次再前代、回代”的乘法次数和实际耗时，确认两者的解相同，查看各个工况的解。",
         "Compare the multiplications and the time of 'eliminate from scratch every time' and 'factor once, then substitute'; check that the solutions agree and look at each load case."],
  scenes: [
    { id: "cases", robot: true, name: ["多工况校核", "Many load cases"],
      problem: { title: ["机器人问题：一百种载荷，要消元一百次吗？", "Robot problem: a hundred loads, a hundred eliminations?"],
                 text: ["AGV 停靠站的钢网架要在 k 种载荷（不同的货物、风向、吊装位置）下校核。系数矩阵只取决于网架本身，右端随工况而变。（矩阵为示意，按固定种子生成。）",
                        "The steel frame of an AGV docking station must be checked under k load cases. The matrix depends only on the frame; the right-hand side changes with the case. (The matrix is illustrative, generated from a fixed seed.)"] } },
  ],
  params: [
    { id: "n", name: ["未知数个数 n", "Unknowns n"], min: 50, max: 300, step: 50, value: 200, digits: 0 },
    { id: "k", name: ["工况个数 k", "Load cases k"], min: 1, max: 100, step: 1, value: 100, digits: 0 },
    { id: "c", name: ["查看第几个工况", "Case shown"], min: 1, max: 100, step: 1, value: 1, digits: 0 },
  ],
  buttons: [{ id: "run", name: ["两种方法各算一遍", "Run both methods"], primary: true },
            { id: "pair", name: ["k = 100，n = 100 与 200 各算一遍", "k = 100, n = 100 and 200"] }, { id: "clear", name: ["清空记录", "Clear the log"] }],
  tasks: [
    { id: "same", text: ["取 k = 100 运行，确认两种方法的解相同（最大差小于 10⁻⁹）。", "Run with k = 100 and check the two methods agree (largest difference below 10⁻⁹)."],
      demo: { scene: "cases", set: { n: 100, k: 100 }, press: ["run"], wait: 3 } },
    { id: "tenth", text: ["n = 200 时，找出使乘法次数之比达到 10 倍以上的最小 k（看读数中的“倍数”），在这个 k 下点“两种方法各算一遍”。", "With n = 200, find the smallest k for which the ratio of multiplications reaches 10 (see the readout) and press Run both methods at that k."],
      demo: { scene: "cases", set: { n: 200, k: 12 }, press: ["run"], wait: 2 } },
    { id: "double", text: ["k = 100 时，分别取 n = 100 和 n = 200 各运行一次（或点“k = 100，n = 100 与 200 各算一遍”），比较两种方法的耗时各增加到几倍。", "With k = 100, run once with n = 100 and once with n = 200 (or press the pair button); by what factor does each method's time grow?"],
      demo: { scene: "cases", set: { n: 200, k: 100 }, press: ["pair"], wait: 5 } },
  ],
  think: ["k 很大时，两种方法的乘法次数之比趋于多少？为什么说 LU 分解是“消元的记录”？",
          "What does the ratio of multiplications tend to for large k? Why is the LU factorization 'a record of elimination'?"],

  mem: null,
  log() { if (!this.mem) this.mem = { runs: [] }; return this.mem; },
  mat(n) {   // dense, diagonally dominant, reproducible
    const A = new Float64Array(n * n); let s = 12345;
    const r = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296 - 0.5; };
    for (let i = 0; i < n; i++) { let sum = 0; for (let j = 0; j < n; j++) if (i !== j) { const v = r() / Math.sqrt(1 + Math.abs(i - j)); A[i * n + j] = v; sum += Math.abs(v); } A[i * n + i] = sum + 1; }
    return A;
  },
  rhs(n, c) {   // load case c: a smooth load with its own shape
    const b = new Float64Array(n);
    for (let i = 0; i < n; i++) { const x = (i + 0.5) / n; b[i] = Math.sin(Math.PI * c * x / 7) + 0.5 * Math.cos(2 * Math.PI * x * (1 + c % 5)); }
    return b;
  },
  gauss(Ain, b, n) {   // eliminate and back-substitute from scratch (no pivoting: A is diagonally dominant)
    const A = Float64Array.from(Ain), x = Float64Array.from(b);
    for (let k = 0; k < n - 1; k++) for (let i = k + 1; i < n; i++) {
      const l = A[i * n + k] / A[k * n + k];
      for (let j = k + 1; j < n; j++) A[i * n + j] -= l * A[k * n + j];
      x[i] -= l * x[k];
    }
    for (let i = n - 1; i >= 0; i--) { let s = x[i]; for (let j = i + 1; j < n; j++) s -= A[i * n + j] * x[j]; x[i] = s / A[i * n + i]; }
    return x;
  },
  factor(Ain, n) {   // L and U stored together
    const A = Float64Array.from(Ain);
    for (let k = 0; k < n - 1; k++) for (let i = k + 1; i < n; i++) {
      const l = (A[i * n + k] /= A[k * n + k]);
      for (let j = k + 1; j < n; j++) A[i * n + j] -= l * A[k * n + j];
    }
    return A;
  },
  subst(LU, b, n) {
    const x = Float64Array.from(b);
    for (let i = 1; i < n; i++) { let s = x[i]; for (let j = 0; j < i; j++) s -= LU[i * n + j] * x[j]; x[i] = s; }
    for (let i = n - 1; i >= 0; i--) { let s = x[i]; for (let j = i + 1; j < n; j++) s -= LU[i * n + j] * x[j]; x[i] = s / LU[i * n + i]; }
    return x;
  },
  counts(n, k) {   // multiplications and divisions (Section 3.8 and (5.3.4))
    const solve = n ** 3 / 3 + n ** 2 / 2 - 5 * n / 6 + n * (n + 1) / 2, lu = (n ** 3 - n) / 3 + k * n ** 2;
    return { sep: k * solve, lu, ratio: k * solve / lu };
  },
  action(id, api) {
    const L = this.log();
    if (id === "clear") { L.runs = []; L.last = null; return; }
    if (id === "pair") { this.solveAll(100, 100); this.solveAll(200, 100); return; }
    if (id === "run") this.solveAll(api.p.n, api.p.k);
  },
  solveAll(n, k) {
    const L = this.log(), A = this.mat(n), B = Array.from({ length: k }, (_, c) => this.rhs(n, c + 1));
    let t0 = performance.now();
    const X1 = B.map((b) => this.gauss(A, b, n));
    const t1 = Math.max(performance.now() - t0, 0.01);
    t0 = performance.now();
    const LU = this.factor(A, n), X2 = B.map((b) => this.subst(LU, b, n));
    const t2 = Math.max(performance.now() - t0, 0.01);
    let diff = 0; X1.forEach((x, c) => x.forEach((v, i) => { diff = Math.max(diff, Math.abs(v - X2[c][i])); }));
    L.last = { n, k, X: X2, diff, t: [t1, t2] };
    L.runs.push({ n, k, t: [t1, t2], diff });
  },
  readouts(api) {
    const L = this.log(), n = api.p.n, k = api.p.k, c = this.counts(n, k), r = L.last;
    let kmin = 1; while (this.counts(200, kmin).ratio < 10 && kmin < 100) kmin++;
    if (r && r.k === 100 && r.diff < 1e-9) api.done("same");
    if (r && r.n === 200 && r.k === kmin && r.diff < 1e-9) api.done("tenth");
    const ok = (nn) => L.runs.some((q) => q.n === nn && q.k === 100 && q.diff < 1e-9);
    if (ok(100) && ok(200)) api.done("double");
    const rows = [[["乘法次数：每次从头消元", "Multiplications: from scratch"], c.sep.toExponential(2)],
                  [["乘法次数：分解一次 + k 次前代、回代", "Multiplications: factor once + k solves"], c.lu.toExponential(2)],
                  [["倍数", "Ratio"], api.fmt(c.ratio, 2)]];
    if (!r) return rows.concat([[["状态", "Status"], api.T("点“两种方法各算一遍”", "press Run both methods")]]);
    return rows.concat([[["上次运行", "Last run"], "n = " + r.n + ", k = " + r.k],
                        [["耗时：从头消元 / 分解后求解", "Time: scratch / factored"], api.fmt(r.t[0], 1) + " / " + api.fmt(r.t[1], 1) + " ms"],
                        [["实测加速倍数", "Measured speed-up"], api.fmt(r.t[0] / r.t[1], 1)],
                        [["两种解的最大差", "Largest difference"], r.diff.toExponential(1)]]);
  },
  draw(api) {
    const { w, h } = api, L = this.log(), r = L.last, muted = api.css("--muted");
    // left: multiplication counts against k (log scale) for the current n, with the current k marked
    const x0 = 46, x1 = w * 0.48, y0 = 30, y1 = h - 40, n = api.p.n;
    const pts1 = [], pts2 = [];
    const lo = Math.log10(this.counts(n, 1).lu) - 0.2, hi = Math.log10(this.counts(n, 100).sep) + 0.2;
    const X = (k) => x0 + (x1 - x0) * Math.log10(k) / 2, Y = (v) => y1 - (y1 - y0) * (Math.log10(v) - lo) / (hi - lo);
    for (let k = 1; k <= 100; k++) { const c = this.counts(n, k); pts1.push([X(k), Y(c.sep)]); pts2.push([X(k), Y(c.lu)]); }
    api.rect(x0, y0, x1 - x0, y1 - y0, null, api.css("--grid"));
    const poly = (pts, col) => { const g = api.ctx; g.beginPath(); pts.forEach((p, i) => (i ? g.lineTo(...p) : g.moveTo(...p))); g.strokeStyle = col; g.lineWidth = 2; g.stroke(); };
    poly(pts1, api.css("--red")); poly(pts2, api.css("--blue"));
    const kc = this.counts(n, api.p.k);
    api.line(X(api.p.k), y0, X(api.p.k), y1, muted, 1);
    api.circle(X(api.p.k), Y(kc.sep), 4, api.css("--red"), null); api.circle(X(api.p.k), Y(kc.lu), 4, api.css("--blue"), null);
    [1, 10, 100].forEach((k) => api.label(String(k), X(k), y1 + 16, muted, 11, "center"));
    api.label(api.T("乘法次数与工况数 k（对数坐标）", "multiplications vs k (log scale)"), x0, 18, muted, 12);
    api.label(api.T("红：从头消元  蓝：分解一次", "red: scratch  blue: factor once"), x0 + 4, y0 + 14, muted, 11);
    // right: the solution of the case shown
    const gx = w * 0.56, gw = w * 0.4;
    api.label(api.T("第 " + api.p.c + " 个工况的解 x", "solution x of case " + api.p.c), gx, 18, muted, 12);
    if (!r) { api.label(api.T("运行后显示", "shown after a run"), gx + gw / 2, h / 2, muted, 13, "center"); return; }
    const c = Math.min(api.p.c, r.k) - 1, x = r.X[c], m = Math.max(...Array.from(x).map(Math.abs)) || 1;
    const midY = (y0 + y1) / 2, sc = (y1 - y0) / 2 / m;
    api.line(gx, midY, gx + gw, midY, muted, 1);
    const g = api.ctx; g.beginPath();
    x.forEach((v, i) => { const px = gx + gw * i / (x.length - 1), py = midY - v * sc; if (i) g.lineTo(px, py); else g.moveTo(px, py); });
    g.strokeStyle = api.css("--green"); g.lineWidth = 2; g.stroke();
    if (api.p.c > r.k) api.label(api.T("只算了 " + r.k + " 个工况", "only " + r.k + " cases solved"), gx, y1 + 16, api.css("--red"), 11);
  },
});
