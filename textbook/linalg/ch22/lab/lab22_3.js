// 实验 22.3 稀疏矩阵的排序与填充（配 22.3 节）。
// 消元博弈：按某个顺序依次消去顶点，消去时它尚未消去的邻居两两连边；新连的边就是填充，L 的非零元个数 = n + Σ（消去时的邻居数）。
// 排序：自然、卡思尔–麦基的逆序（RCM，从度最小的顶点出发做广度优先，邻居按度从小到大，最后倒过来）、最小度（度相同取编号小的，
// 与程序 22.3.1 相同）、嵌套剖分（只对网格：先递归排两半，最后排分隔线，与程序 22.3.1 相同）。
// 场景：仓库地面网格（m × m）；AGV 位姿图（跑 4 圈、每圈 25 个位姿，每隔 5 个位姿一条回环约束）；调度中心与 m 个工位的星形图。
WQ.lab({
  title: ["实验 22.3 稀疏矩阵的排序与填充", "Lab 22.3 Orderings and fill-in of sparse matrices"],
  goal: ["换一种消元顺序，看乔列斯基因子 L 的非零元（填充）和运算量怎样变化；用滑块一步步消元，看填充是在哪里、怎样产生的。",
         "Change the elimination order and watch the nonzeros of the Cholesky factor L (fill-in) and the work change; step through the elimination to see where and how fill appears."],
  scenes: [
    { id: "grid", robot: true, name: ["仓库地面网格", "Warehouse floor grid"],
      problem: { title: ["机器人问题：地面温度场的方程组怎样解得快？", "Robot problem: how to solve the floor-temperature system fast?"],
                 text: ["把仓库地面分成 m × m 个格子，每个格子的温度与上下左右四个邻居相关，方程组的矩阵是二维拉普拉斯矩阵：每行至多 5 个非零元。消元时会产生多少新的非零元？",
                        "Divide the warehouse floor into m × m cells; each cell's temperature couples to its four neighbours, giving the 2D Laplacian with at most 5 nonzeros per row. How many new nonzeros does elimination create?"] } },
    { id: "pose", robot: true, name: ["AGV 位姿图", "AGV pose graph"], hide: ["m"],
      problem: { title: ["机器人问题：建图时回环约束让矩阵变稠了吗？", "Robot problem: do loop closures make the mapping system dense?"],
                 text: ["AGV 沿同一条环形路线跑 4 圈，每圈记录 25 个位姿。相邻位姿之间有里程计约束；回到同一位置时（每隔 5 个位姿）还有一条回环约束。信息矩阵是稀疏的，但回环让它不再是窄带。",
                        "An AGV drives four laps of the same loop, recording 25 poses per lap. Consecutive poses share an odometry constraint; returning to the same place (every 5 poses) adds a loop closure. The information matrix is sparse but no longer narrow-banded."] } },
    { id: "star", robot: true, name: ["调度中心与工位", "Dispatcher and stations"],
      problem: { title: ["机器人问题：中心节点该排在前面还是后面？", "Robot problem: should the hub be numbered first or last?"],
                 text: ["调度中心与 m 个工位双向通信，工位之间不直接相连。矩阵是“箭形”的：第一行、第一列满，其余只有对角元。",
                        "A dispatcher talks to m stations, which do not talk to each other. The matrix is an arrow: full first row and column, otherwise diagonal."] } },
  ],
  params: [
    { id: "m", name: ["规模 m", "Size m"], min: 4, max: 20, step: 1, value: 10, digits: 0 },
    { id: "ord", name: ["排序（0 自然，1 RCM，2 最小度，3 嵌套剖分）", "Order (0 natural, 1 RCM, 2 minimum degree, 3 nested dissection)"], min: 0, max: 3, step: 1, value: 0, digits: 0 },
    { id: "k", name: ["已消元的比例", "Fraction eliminated"], min: 0, max: 100, step: 1, value: 100, unit: "%", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "nat", robot: true, text: ["网格 m = 10，自然排序：L 有多少非零元？是 A 的下三角的几倍？", "Grid m = 10, natural order: how many nonzeros does L have? How many times the lower triangle of A?"],
      demo: { scene: "grid", set: { m: 10, ord: 0, k: 100 }, press: [] } },
    { id: "better", robot: true, text: ["网格 m = 10：找一种排序，使 nnz(L) 不到自然排序的 70%。", "Grid m = 10: find an order with nnz(L) below 70% of the natural order's."],
      demo: { scene: "grid", set: { m: 10, ord: 2, k: 100 }, press: [] } },
    { id: "nd", robot: true, text: ["网格 m ≥ 16：比较最小度与嵌套剖分的填充和运算量。", "Grid m ≥ 16: compare minimum degree and nested dissection in fill and work."],
      demo: { scene: "grid", set: { m: 16, ord: 3, k: 100 }, press: [] } },
    { id: "pose", robot: true, text: ["位姿图：哪种排序填充最少？RCM 为什么反而比自然排序差？", "Pose graph: which order gives the least fill? Why is RCM worse than the natural order?"],
      demo: { scene: "pose", set: { ord: 2, k: 100 }, press: [] } },
    { id: "star", robot: true, text: ["星形图：自然排序（中心在前）填满整个矩阵；换成最小度排序，填充是多少？", "Star graph: the natural order (hub first) fills the whole matrix; with minimum degree, how much fill is there?"],
      demo: { scene: "star", set: { m: 12, ord: 2, k: 100 }, press: [] } },
  ],
  think: ["最小度排序每一步只看眼前（消去当前度最小的顶点），嵌套剖分则从整体出发（先切开、最后排分隔线）。网格很大时，哪一种的填充增长得慢？为什么大型有限元软件常把两者结合起来？",
          "Minimum degree is greedy (eliminate the currently lowest-degree vertex); nested dissection is global (cut first, separators last). For very large grids, whose fill grows more slowly? Why do large finite-element codes often combine the two?"],

  graph(api) {
    const sc = api.scene, adj = [], pos = [];
    const add = (i, j) => { adj[i].add(j); adj[j].add(i); };
    if (sc === "grid") {
      const m = api.p.m, n = m * m;
      for (let i = 0; i < n; i++) { adj.push(new Set()); pos.push([(i % m) / (m - 1), Math.floor(i / m) / (m - 1)]); }
      for (let r = 0; r < m; r++) for (let c = 0; c < m; c++) { const i = r * m + c; if (c + 1 < m) add(i, i + 1); if (r + 1 < m) add(i, i + m); }
      return { n, adj, pos, m };
    }
    if (sc === "pose") {
      const laps = 4, per = 25, n = laps * per;
      for (let i = 0; i < n; i++) { adj.push(new Set()); const a = 2 * Math.PI * (i % per) / per, r = 0.25 + 0.06 * Math.floor(i / per); pos.push([0.5 + r * Math.cos(a), 0.5 + r * Math.sin(a)]); }
      for (let i = 0; i < n - 1; i++) add(i, i + 1);
      for (let i = per; i < n; i++) if (i % 5 === 0) add(i - per, i);
      return { n, adj, pos };
    }
    const n = api.p.m + 1;
    for (let i = 0; i < n; i++) { adj.push(new Set()); const a = 2 * Math.PI * (i - 1) / (n - 1); pos.push(i === 0 ? [0.5, 0.5] : [0.5 + 0.42 * Math.cos(a), 0.5 + 0.42 * Math.sin(a)]); }
    for (let i = 1; i < n; i++) add(0, i);
    return { n, adj, pos };
  },
  order(api, g) {
    const n = g.n, o = api.p.ord;
    if (o === 1) {                                            // RCM
      const deg = g.adj.map((s) => s.size), seen = new Array(n).fill(false), res = [];
      while (res.length < n) {
        let start = -1;
        for (let i = 0; i < n; i++) if (!seen[i] && (start < 0 || deg[i] < deg[start])) start = i;
        const q = [start]; seen[start] = true;
        while (q.length) { const v = q.shift(); res.push(v); [...g.adj[v]].filter((u) => !seen[u]).sort((a, b) => deg[a] - deg[b] || a - b).forEach((u) => { seen[u] = true; q.push(u); }); }
      }
      return res.reverse();
    }
    if (o === 2) {                                            // 最小度
      const G = g.adj.map((s) => new Set(s)), alive = new Set([...Array(n).keys()]), res = [];
      while (alive.size) {
        let v = -1;
        alive.forEach((u) => { if (v < 0 || G[u].size < G[v].size || (G[u].size === G[v].size && u < v)) v = u; });
        const nb = [...G[v]];
        nb.forEach((a) => { G[a].delete(v); nb.forEach((b) => { if (a !== b) G[a].add(b); }); });
        alive.delete(v); res.push(v);
      }
      return res;
    }
    if (o === 3 && g.m) {                                     // 嵌套剖分（网格）
      const m = g.m;
      const rec = (r0, r1, c0, c1) => {
        if ((r1 - r0) * (c1 - c0) <= 4) { const a = []; for (let i = r0; i < r1; i++) for (let j = c0; j < c1; j++) a.push(i * m + j); return a; }
        if (r1 - r0 >= c1 - c0) { const mid = Math.floor((r0 + r1) / 2), sep = []; for (let j = c0; j < c1; j++) sep.push(mid * m + j); return [...rec(r0, mid, c0, c1), ...rec(mid + 1, r1, c0, c1), ...sep]; }
        const mid = Math.floor((c0 + c1) / 2), sep = []; for (let i = r0; i < r1; i++) sep.push(i * m + mid);
        return [...rec(r0, r1, c0, mid), ...rec(r0, r1, mid + 1, c1), ...sep];
      };
      return rec(0, m, 0, m);
    }
    return [...Array(n).keys()];
  },
  run(api) {
    const key = [api.scene, api.p.m, api.p.ord].join(",");
    if (this._c && this._c.key === key) return this._c;
    const g = this.graph(api), o = this.order(api, g), n = g.n, posIn = new Array(n);
    o.forEach((v, k) => { posIn[v] = k; });
    const G = g.adj.map((s) => new Set(s)), done = new Array(n).fill(false), cols = [];
    let nnz = n, fl = 0;
    for (let k = 0; k < n; k++) {
      const v = o[k], nb = [...G[v]].filter((u) => !done[u]);
      const orig = new Set([...g.adj[v]]);
      cols.push(nb.map((u) => [posIn[u], orig.has(u)]));
      nnz += nb.length; fl += nb.length * nb.length;
      nb.forEach((a) => nb.forEach((b) => { if (a !== b) G[a].add(b); }));
      done[v] = true;
    }
    let lowA = n; g.adj.forEach((s) => { lowA += s.size; }); lowA = n + (lowA - n) / 2;
    let bw = 0; g.adj.forEach((s, i) => s.forEach((j) => { bw = Math.max(bw, Math.abs(posIn[i] - posIn[j])); }));
    this._c = { key, g, o, posIn, cols, nnz, fl, lowA, bw, nat: null };
    return this._c;
  },
  natural(api) {                                               // 自然排序的 nnz(L)，作为比较的基准
    const key = [api.scene, api.p.m].join(",");
    if (this._n && this._n.key === key) return this._n.v;
    const save = api.p.ord; api.p.ord = 0; const c = this.run(api); const v = c.nnz; api.p.ord = save; this._c = null;
    this._n = { key, v }; return v;
  },
  reset(api, s) {},
  readouts(api, s) {
    const nat = this.natural(api), R = this.run(api), f = api.fmt, sc = api.scene;
    const names = [["自然", "natural"], ["RCM", "RCM"], ["最小度", "minimum degree"], [sc === "grid" ? "嵌套剖分" : "嵌套剖分（只用于网格，这里按自然排序）", sc === "grid" ? "nested dissection" : "nested dissection (grids only; natural used here)"]][api.p.ord];
    if (sc === "grid" && api.p.m === 10 && api.p.ord === 0) api.done("nat");
    if (sc === "grid" && api.p.m === 10 && R.nnz < 0.7 * nat) api.done("better");
    if (sc === "grid" && api.p.m >= 16 && api.p.ord === 3) api.done("nd");
    if (sc === "pose" && api.p.ord === 2) api.done("pose");
    if (sc === "star" && api.p.ord === 2 && R.nnz === R.lowA) api.done("star");
    return [[["阶数 n", "Order n"], String(R.g.n)],
            [["A 的下三角非零元（含对角）", "Nonzeros in lower triangle of A"], String(R.lowA)],
            [["排序", "Order"], api.T(names[0], names[1])],
            [["nnz(L)", "nnz(L)"], R.nnz + api.T("（A 的 ", " (") + f(R.nnz / R.lowA, 2) + api.T(" 倍）", "× A)")],
            [["填充（新产生的非零元）", "Fill (new nonzeros)"], String(R.nnz - R.lowA)],
            [["与自然排序相比", "Relative to natural order"], f(100 * R.nnz / nat, 1) + "%"],
            [["运算量 Σ cₖ²（乘法与加法）", "Work Σ cₖ² (multiplies and adds)"], String(R.fl)],
            [["带宽（按此排序）", "Bandwidth (this order)"], String(R.bw)]];
  },
  draw(api, s) {
    const R = this.run(api), { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink");
    const n = R.g.n, kDone = Math.round(n * api.p.k / 100);
    // 左：图（已消去的顶点变灰）
    const gx = 10, gy = 20, gs = Math.min(w * 0.42, h - 50);
    const P = (i) => [gx + 10 + R.g.pos[i][0] * (gs - 20), gy + 10 + R.g.pos[i][1] * (gs - 20)];
    R.g.adj.forEach((set, i) => set.forEach((j) => { if (j > i) { const a = P(i), b = P(j); api.line(a[0], a[1], b[0], b[1], mu, 1); } }));
    for (let i = 0; i < n; i++) { const p = P(i), dn = R.posIn[i] < kDone; api.circle(p[0], p[1], n > 150 ? 2.5 : 4, dn ? mu : api.css("--accent")); }
    api.label(api.T("图：灰色为已消去的顶点", "graph: grey vertices eliminated"), gx, gy - 6, mu, 11);
    // 右：按新编号的矩阵：蓝 = A 的非零元，红 = 填充（只画已消去的列）
    const mx = w * 0.47, my = 20, ms = Math.min(w - mx - 10, h - 50), c = ms / n;
    api.rect(mx, my, ms, ms, null, mu);
    for (let k = 0; k < n; k++) api.rect(mx + k * c, my + k * c, Math.max(c, 1), Math.max(c, 1), ink);
    for (let k = 0; k < kDone; k++) R.cols[k].forEach(([i, orig]) => {
      const col = orig ? api.css("--blue") : api.css("--red");
      api.rect(mx + k * c, my + i * c, Math.max(c, 1), Math.max(c, 1), col);
      api.rect(mx + i * c, my + k * c, Math.max(c, 1), Math.max(c, 1), col);
    });
    api.label(api.T("L + Lᵀ 的非零元：蓝为原有，红为填充（已消去 ", "nonzeros of L + Lᵀ: blue original, red fill (eliminated ") + kDone + " / " + n + api.T("）", ")"), mx, my - 6, mu, 11);
  },
});
