// 实验 22.1 选主元与增长因子（配 22.1 节）。
// 用 d 位十进制有效数字做高斯消元：每次乘、除、减之后都舍入到 d 位（d = 16 时就是双精度，不再另外舍入）。
// 选主元：不选、部分（列中最大）、车式（交替在列、行中找，直到它同时是所在行、列的最大者）、完全（剩余子矩阵中最大），与程序 22.1.1 的 _ge.py 相同。
// 增长因子 ρ = 消元过程中出现的最大元素 / 原矩阵的最大元素。真解取全 1 向量，右端用双精度算出。
// 场景：生活中的例子（4 位计算器解 2 阶方程组，福赛思–莫勒的例子）；两点边值问题的多重打靶矩阵（22.1.4 节）；威尔金森矩阵。
WQ.lab({
  title: ["实验 22.1 选主元与增长因子", "Lab 22.1 Pivoting and the growth factor"],
  goal: ["换不同的选主元策略、不同的有效位数，看消元中的元素会不会“长大”、解的误差有多大；体会“良态的问题 + 不稳定的算法 = 错误的结果”。",
         "Switch pivoting strategies and working precision; watch whether entries grow during elimination and how large the error is: a well-conditioned problem plus an unstable algorithm gives a wrong answer."],
  scenes: [
    { id: "calc", name: ["生活中的例子：4 位计算器", "Everyday example: a 4-digit calculator"], hide: ["N"],
      problem: { title: ["生活中的例子：计算器为什么算错？", "Everyday example: why does the calculator get it wrong?"],
                 text: ["用只能保留 4 位有效数字的计算器解 0.0003x + 3y = 2.0001，x + y = 1（真解 x = 1/3，y = 2/3）。按课本上的步骤消元，x 却算成了别的数。",
                        "Solve 0.0003x + 3y = 2.0001, x + y = 1 (exact x = 1/3, y = 2/3) on a calculator that keeps 4 significant digits. Following the textbook elimination gives the wrong x."] } },
    { id: "shoot", robot: true, name: ["轨迹的两点边值问题", "Two-point boundary-value problem"],
      problem: { title: ["机器人问题：条件数只有 8，解怎么会不准？", "Robot problem: the condition number is only 8, so why is the answer inaccurate?"],
                 text: ["规划一段轨迹，系统 y′ = My 有一个增长模态、一个衰减模态，条件同时涉及起点和终点的状态（y₀ + y_N = c）。把时间分成 N 段用多重打靶法离散，得到 2N + 2 阶方程组。它的条件数始终约为 8。",
                        "Planning a trajectory: y′ = My has one growing and one decaying mode, with a condition coupling both ends (y₀ + y_N = c). Multiple shooting on N subintervals gives a system of order 2N + 2 whose condition number stays near 8."] } },
    { id: "wilk", name: ["威尔金森矩阵", "Wilkinson's matrix"],
      problem: { title: ["问题：部分选主元最坏能有多坏？", "Problem: how bad can partial pivoting get?"],
                 text: ["对角线为 1、对角线以下为 −1、最后一列为 1 的 n 阶矩阵。部分选主元时不换行，最后一列每消一步翻一倍。",
                        "Order n, ones on the diagonal, −1 below it, last column all ones. Partial pivoting never swaps, and the last column doubles at every step."] } },
  ],
  params: [
    { id: "piv", name: ["选主元（0 不选，1 部分，2 车式，3 完全）", "Pivoting (0 none, 1 partial, 2 rook, 3 complete)"], min: 0, max: 3, step: 1, value: 1, digits: 0 },
    { id: "d", name: ["有效数字位数（16 = 双精度）", "Significant digits (16 = double)"], min: 3, max: 16, step: 1, value: 16, digits: 0 },
    { id: "N", name: ["规模（打靶段数 N 或阶数 n）", "Size (subintervals N or order n)"], min: 4, max: 60, step: 1, value: 20, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "calc0", text: ["计算器场景，4 位有效数字、不选主元：x 算成了多少？", "Calculator, 4 digits, no pivoting: what x do you get?"],
      demo: { scene: "calc", set: { piv: 0, d: 4 }, press: [] } },
    { id: "calc1", text: ["同样 4 位，改用部分选主元：误差变成多少？", "Same 4 digits with partial pivoting: what is the error now?"],
      demo: { scene: "calc", set: { piv: 1, d: 4 }, press: [] } },
    { id: "wilk", text: ["威尔金森矩阵 n ≥ 50、双精度、部分选主元：增长因子和误差各是多少？", "Wilkinson n ≥ 50, double precision, partial pivoting: growth factor and error?"],
      demo: { scene: "wilk", set: { piv: 1, d: 16, N: 55 }, press: [] } },
    { id: "wilkfix", text: ["同一个矩阵改用车式或完全选主元：误差回到多少？", "Same matrix with rook or complete pivoting: how small is the error now?"],
      demo: { scene: "wilk", set: { piv: 2, d: 16, N: 55 }, press: [] } },
    { id: "shoot", robot: true, text: ["两点边值问题，N ≥ 50、双精度、部分选主元：增长因子超过 10⁵ 了吗？再换完全选主元比较。", "Boundary-value problem, N ≥ 50, double, partial pivoting: does the growth factor exceed 10⁵? Then compare complete pivoting."],
      demo: { scene: "shoot", set: { piv: 1, d: 16, N: 55 }, press: [] } },
  ],
  think: ["多重打靶矩阵的条件数一直约为 8，部分选主元的增长因子却指数增长。增长因子大，说明算法的后向误差大，还是问题病态？为什么 LAPACK 仍然默认用部分选主元？",
          "The multiple-shooting matrix keeps κ ≈ 8 while partial pivoting's growth explodes. Does large growth mean a large backward error of the algorithm or an ill-conditioned problem? Why does LAPACK still default to partial pivoting?"],

  matrix(api) {
    const sc = api.scene;
    if (sc === "calc") return [[0.0003, 3], [1, 1]];
    if (sc === "wilk") { const n = api.p.N; return [...Array(n)].map((_, i) => [...Array(n)].map((_, j) => (j === n - 1 ? 1 : i === j ? 1 : i > j ? -1 : 0))); }
    const N = api.p.N, h = 0.3, a = -1 / 6, b = 1, e = Math.exp(a * h), ch = e * Math.cosh(b * h), sh = e * Math.sinh(b * h);
    const n = 2 * (N + 1), A = [...Array(n)].map(() => Array(n).fill(0));
    for (let i = 0; i < N; i++) {
      A[2 * i][2 * i] = -ch; A[2 * i][2 * i + 1] = -sh; A[2 * i + 1][2 * i] = -sh; A[2 * i + 1][2 * i + 1] = -ch;
      A[2 * i][2 * i + 2] = 1; A[2 * i + 1][2 * i + 3] = 1;
    }
    A[2 * N][0] = 1; A[2 * N + 1][1] = 1; A[2 * N][2 * N] = 1; A[2 * N + 1][2 * N + 1] = 1;
    return A;
  },
  run(api) {
    const key = [api.scene, api.p.piv, api.p.d, api.p.N].join(",");
    if (this._c && this._c.key === key) return this._c;
    const d = api.p.d, rd = d >= 16 ? (x) => x : (x) => (x === 0 ? 0 : Number(x.toPrecision(d)));
    const A0 = this.matrix(api), n = A0.length, A = A0.map((r) => r.map(rd));
    const xt = api.scene === "calc" ? [1 / 3, 2 / 3] : Array(n).fill(1);
    const b0 = api.scene === "calc" ? [2.0001, 1] : A0.map((r) => r.reduce((s, a, j) => s + a * xt[j], 0));
    const b = b0.map(rd), cols = [...Array(n).keys()];
    const amax = Math.max(...A.map((r) => Math.max(...r.map(Math.abs))));
    let g = amax; const hist = [amax];
    for (let k = 0; k < n - 1; k++) {
      let pi = k, pj = k;
      const piv = api.p.piv;
      if (piv === 1) { for (let i = k; i < n; i++) if (Math.abs(A[i][k]) > Math.abs(A[pi][k])) pi = i; }
      else if (piv === 3) { for (let i = k; i < n; i++) for (let j = k; j < n; j++) if (Math.abs(A[i][j]) > Math.abs(A[pi][pj])) { pi = i; pj = j; } }
      else if (piv === 2) {
        for (let i = k; i < n; i++) if (Math.abs(A[i][k]) > Math.abs(A[pi][k])) pi = i;
        for (let guard = 0; guard < 4 * n; guard++) {
          let j2 = pj; for (let j = k; j < n; j++) if (Math.abs(A[pi][j]) > Math.abs(A[pi][j2])) j2 = j;
          if (Math.abs(A[pi][j2]) <= Math.abs(A[pi][pj])) break;
          pj = j2;
          let i2 = pi; for (let i = k; i < n; i++) if (Math.abs(A[i][pj]) > Math.abs(A[i2][pj])) i2 = i;
          if (Math.abs(A[i2][pj]) <= Math.abs(A[pi][pj])) break;
          pi = i2;
        }
      }
      [A[k], A[pi]] = [A[pi], A[k]]; [b[k], b[pi]] = [b[pi], b[k]];
      if (pj !== k) { A.forEach((r) => { [r[k], r[pj]] = [r[pj], r[k]]; }); [cols[k], cols[pj]] = [cols[pj], cols[k]]; }
      if (A[k][k] === 0) { hist.push(g); continue; }
      let mx = 0;
      for (let i = k + 1; i < n; i++) {
        const l = rd(A[i][k] / A[k][k]);
        if (l === 0) { for (let j = k + 1; j < n; j++) mx = Math.max(mx, Math.abs(A[i][j])); continue; }
        for (let j = k + 1; j < n; j++) { A[i][j] = rd(A[i][j] - rd(l * A[k][j])); mx = Math.max(mx, Math.abs(A[i][j])); }
        b[i] = rd(b[i] - rd(l * b[k])); A[i][k] = 0;
      }
      g = Math.max(g, mx); hist.push(Math.max(mx, 1e-300));
    }
    const z = Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let s = b[i]; for (let j = i + 1; j < n; j++) s = rd(s - rd(A[i][j] * z[j])); z[i] = rd(s / A[i][i]); }
    const x = Array(n); cols.forEach((c, k) => { x[c] = z[k]; });
    const nrm = (v) => Math.sqrt(v.reduce((s, t) => s + t * t, 0));
    const err = nrm(x.map((v, i) => v - xt[i])) / nrm(xt);
    const r = A0.map((row, i) => row.reduce((s, a, j) => s + a * x[j], 0) - b0[i]);
    const nA = api.la.svd(A0).s, kap = nA[0] / nA[nA.length - 1];
    const eta = nrm(r) / (nA[0] * nrm(x) + nrm(b0));
    this._c = { key, n, x, err, eta, kap, rho: g / amax, hist, U: A };
    return this._c;
  },
  reset(api, s) {},
  readouts(api, s) {
    const R = this.run(api), f = api.fmt, sc = api.scene, e = (v) => (v === 0 ? "0" : v.toExponential(1));
    if (sc === "calc" && api.p.d === 4 && api.p.piv === 0) api.done("calc0");
    if (sc === "calc" && api.p.d === 4 && api.p.piv === 1 && R.err < 1e-3) api.done("calc1");
    if (sc === "wilk" && api.p.N >= 50 && api.p.d === 16 && api.p.piv === 1) api.done("wilk");
    if (sc === "wilk" && api.p.N >= 50 && api.p.d === 16 && api.p.piv >= 2 && R.err < 1e-12) api.done("wilkfix");
    if (sc === "shoot" && api.p.N >= 50 && api.p.d === 16 && api.p.piv === 1 && R.rho > 1e5) api.done("shoot");
    const rows = [[["阶数", "Order"], String(R.n)],
                  [["条件数 κ₂(A)", "Condition number κ₂(A)"], f(R.kap, 2)],
                  [["增长因子 ρ", "Growth factor ρ"], R.rho >= 1e4 ? e(R.rho) : f(R.rho, 3)],
                  [["解的相对误差", "Relative error of the solution"], e(R.err)],
                  [["后向误差 ‖r‖/(‖A‖‖x‖ + ‖b‖)", "Backward error ‖r‖/(‖A‖‖x‖ + ‖b‖)"], e(R.eta)],
                  [["机器精度（单位舍入）", "Unit roundoff"], api.p.d >= 16 ? "1.1e-16" : e(0.5 * Math.pow(10, 1 - api.p.d))]];
    if (sc === "calc") rows.unshift([["算出的 x, y", "Computed x, y"], R.x.map((v) => v.toPrecision(Math.min(api.p.d, 8))).join(", ") + api.T("（真解 0.3333…, 0.6667…）", " (exact 0.3333…, 0.6667…)")]);
    return rows;
  },
  draw(api, s) {
    const R = this.run(api), { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink");
    // 左：各步剩余子矩阵中的最大元素（对数坐标）
    const x0 = 60, x1 = w * 0.55, y0 = 30, y1 = h - 40, H = R.hist, lo = 0, hi = Math.max(1, Math.log10(Math.max(...H) / H[0]) + 0.5);
    api.rect(x0, y0, x1 - x0, y1 - y0, null, mu);
    const X = (k) => x0 + (x1 - x0) * k / Math.max(H.length - 1, 1), Y = (v) => y1 - (y1 - y0) * (Math.log10(Math.max(v / H[0], 1e-3)) - lo) / (hi - lo);
    for (let k = 1; k < H.length; k++) api.line(X(k - 1), Y(H[k - 1]), X(k), Y(H[k]), api.css("--red"), 2);
    api.label(api.T("每一步剩余子矩阵中的最大元素 / 原矩阵最大元素（对数坐标，上限 10^", "largest remaining entry / largest original entry at each step (log scale, top 10^") + api.fmt(hi, 1) + ")", x0, y0 - 10, mu, 11);
    api.label(api.T("消元步数", "elimination step"), x0, y1 + 24, mu, 11);
    // 右：U 的元素大小（颜色深浅表示 log10|uᵢⱼ|）
    const n = R.n, mx = w * 0.6, my = 30, ms = Math.min(w - mx - 10, h - 70), c = ms / n;
    let big = 1e-300; R.U.forEach((r, i) => r.forEach((v, j) => { if (j >= i) big = Math.max(big, Math.abs(v)); }));
    const lb = Math.log10(big);
    for (let i = 0; i < n; i++) for (let j = i; j < n; j++) {
      const v = Math.abs(R.U[i][j]); if (v === 0) continue;
      const t = Math.max(0, Math.min(1, 1 - (lb - Math.log10(v)) / 16));
      api.rect(mx + j * c, my + i * c, Math.max(c, 1), Math.max(c, 1), `rgba(200, 40, 40, ${0.08 + 0.92 * t})`);
    }
    api.rect(mx, my, ms, ms, null, mu);
    api.label(api.T("U 的元素：颜色越深越大（跨 16 个数量级）", "entries of U: darker = larger (16 decades)"), mx, my - 10, mu, 11);
  },
});
