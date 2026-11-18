// 实验 20.2 图是谁定的，以及它看不见什么（配 20.2 节）。
// 两个场景：
//   graph ：拖截断半径，看同一个晶体变成什么样的图（边数、平均配位数、边长种类）；
//   blind ：两个不同的结构，所有原子对的距离完全相同——把直方图调到最细也分不开，
//           打开三体特征才分得开。
// 与 code/_ch20.py 是同一套算法（neighbor_graph、pair_distances、edge_histogram、angle_feature）。
WQ.lab({
  title: ["实验 20.2 晶体变成图：截断半径与看不见的差别",
          "Lab 20.2 Crystal to graph: the cutoff and the difference it cannot see"],
  goal: ["先亲手拖截断半径，看同一个晶体怎样变成完全不同的图——这个数是人定的，不是材料给的。再看一对特意造出来的结构：它们所有原子对的距离一个不差，于是任何只看两体距离的描述子都分不开它们；把直方图调到最细也没用，补上三体信息才分开。做完能回答：模型在这里失败，是算法不好，还是输入里根本没有那条信息。",
         "First drag the cutoff radius and watch one crystal turn into very different graphs — that number is a human choice, not a property of the material. Then look at a pair of structures built so that every pair distance agrees exactly: no descriptor built on pair distances alone can tell them apart, and finer histogram bins do not help. Only three-body information separates them. You should be able to say whether the model fails here because the algorithm is weak or because the information is simply not in the input."],
  scenes: [
    { id: "graph", name: ["截断半径定出一张图", "The cutoff defines the graph"],
      problem: { title: ["问题：边是怎么来的", "Problem: where do the edges come from"],
                 text: ["把晶体喂给图神经网络，第一步是把原子当作节点、把“足够近的一对”连成边。多近算近？由**截断半径**决定，而这个数是人选的。选小了，远处的相互作用一概看不见；选大了，每个原子的邻居数暴涨，算一次的代价跟着涨。周期边界还要算上：最右边那个原子的邻居绕回到最左边。",
                        "To feed a crystal to a graph network you first treat atoms as nodes and connect pairs that are close enough. How close is close enough is set by the cutoff radius — a human choice. Too small and distant interactions are invisible; too large and the neighbour count, and the cost, explode. Periodic boundaries count too: the rightmost atom's neighbour wraps around to the left."] } },
    { id: "blind", name: ["描述子看不见的差别", "What the descriptor cannot see"],
      problem: { title: ["问题：信息在不在输入里", "Problem: is the information in the input at all"],
                 text: ["这里有两个**不同**的一维周期结构，它们所有原子对的距离完全相同（这叫同距结构）。任何只用两体距离的描述子，对这两者给出一模一样的输入——换多大的模型、训多久都没用，因为**要分辨的那条信息根本没进来**。补上三体信息（相邻两段的长短搭配），两者立刻分开。这与 19.4 节“同一个粗场配两个细场”是同一个形状的论证。",
                        "Here are two different one-dimensional periodic structures whose complete sets of pair distances agree exactly (a homometric pair). Any descriptor built only on pair distances gives both the same input — a bigger model or longer training cannot help, because the distinguishing information never entered. Add three-body information and they separate at once."] } },
  ],
  params: [
    { id: "rc", name: ["截断半径", "cutoff radius"], min: 1, max: 9, step: 0.5, value: 2, digits: 1 },
    { id: "which", name: ["看哪个结构：0 = 甲，1 = 乙", "structure: 0 = A, 1 = B"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "nbin", name: ["距离直方图分几格（越大越细）", "histogram bins (larger = finer)"], min: 9, max: 72, step: 9, value: 9, digits: 0 },
    { id: "feat", name: ["0 = 只看两体距离，1 = 补上三体", "0 = pair distances only, 1 = add three-body"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["结构甲", "structure A"] },
           { color: "var(--red)", name: ["结构乙", "structure B"] },
           { color: "var(--muted)", name: ["绕过周期边界的那几条边", "edges that wrap around the cell"] },
           { color: "var(--green)", name: ["三体特征（补上之后才分得开）", "three-body features"] }],
  tasks: [
    { id: "small", text: ["结构甲、截断半径 2：记下边数与平均配位数。再把半径拖到 8，两个数各变成多少倍？",
                          "Structure A with a cutoff of 2: record the edge count and mean coordination. Drag the cutoff to 8 — by what factor does each change?"],
      demo: { scene: "graph", set: { which: 0, rc: 2 }, press: [] } },
    { id: "big", text: ["半径拖到 8，看“绕过周期边界的边”占了多少条——如果有人按非周期的办法建图，他丢掉的正是这些。",
                        "At a cutoff of 8, see how many edges wrap around the cell. Anyone who builds the graph without periodic boundaries loses exactly these."],
      demo: { scene: "graph", set: { which: 0, rc: 8 }, press: [] } },
    { id: "same", text: ["切到第二个场景：两个结构的距离直方图重合吗？把“分几格”拖到最细再看一遍。",
                         "Switch to the second scene: do the two distance histograms coincide? Drag the bin count to its finest and look again."],
      demo: { scene: "blind", set: { nbin: 72, feat: 0 }, press: [] } },
    { id: "sep", text: ["把“补上三体”打开：两者的特征差了多少？记下这个差，它就是“信息进来了”的证据。",
                        "Turn on the three-body features: how far apart are the two now? Record that gap — it is the evidence that the information has entered."],
      demo: { scene: "blind", set: { nbin: 18, feat: 1 }, press: [] } },
  ],
  think: ["如果把截断半径加到比半个周期还大，每一对原子都成了邻居——这时的“图”还带有结构信息吗？代价又是多少？再想一步：真实材料里，把截断半径从 5 Å 加到 8 Å，每个原子的邻居数大致按什么规律涨？",
          "If the cutoff exceeds half the period, every pair becomes a neighbour. Does such a graph still carry structural information, and what does it cost? In a real material, how does the neighbour count grow as the cutoff goes from 5 Å to 8 Å?"],

  L: 18,
  A: [0, 1, 4, 10, 12, 17],
  B: [0, 1, 8, 11, 13, 17],

  sep(i, j) { const d = Math.abs(i - j) % this.L; return Math.min(d, this.L - d); },
  sites(which) { return which ? this.B : this.A; },
  // 截断半径以内的边；wrap 标记这条边是不是绕过了周期边界
  edges(sites, rc) {
    const out = [];
    for (let a = 0; a < sites.length; a++)
      for (let b = a + 1; b < sites.length; b++) {
        const d = this.sep(sites[a], sites[b]);
        if (d <= rc + 1e-9) out.push({ a, b, d, wrap: Math.abs(sites[a] - sites[b]) !== d });
      }
    return out;
  },
  dists(sites) {
    const out = [];
    for (let a = 0; a < sites.length; a++)
      for (let b = a + 1; b < sites.length; b++) out.push(this.sep(sites[a], sites[b]));
    return out.sort((x, y) => x - y);
  },
  hist(sites, nbin) {
    const h = new Array(nbin).fill(0), top = this.L / 2;
    for (const d of this.dists(sites)) h[Math.min(nbin - 1, Math.floor(d / top * nbin))] += 1;
    return h;
  },
  // 三体特征：把“相邻两段的长短搭配”排序后当成一个向量（与 _ch20.angle_feature 同一套）
  angle(sites) {
    const n = sites.length, g = [];
    for (let k = 0; k < n; k++) {
      const p = sites[k], q = sites[(k + 1) % n], r = sites[(k + 2) % n];
      g.push([this.sep(p, q), this.sep(q, r)]);
    }
    return g.map((v) => v[0] * 100 + v[1]).sort((x, y) => x - y);
  },
  gap(u, v) { let m = 0; for (let i = 0; i < u.length; i++) m = Math.max(m, Math.abs(u[i] - v[i])); return m; },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p;
    if (api.scene === "graph") {
      const rc = +q.rc.toFixed(1), which = Math.round(q.which), st = this.sites(which);
      const e = this.edges(st, rc), wrap = e.filter((x) => x.wrap).length;
      const kinds = new Set(e.map((x) => x.d)).size;
      if (rc <= 2.01) s.small = { n: e.length, deg: 2 * e.length / st.length };
      if (rc >= 7.99 && s.small) api.done("small");
      if (rc >= 7.99 && wrap > 0) api.done("big");
      return [[["看的是哪个结构", "which structure"], which ? "乙 / B" : "甲 / A"],
              [["边数", "edges"], String(e.length)],
              [["平均配位数", "mean coordination"], (2 * e.length / st.length).toFixed(2)],
              [["边长有几种", "distinct edge lengths"], String(kinds)],
              [["其中绕过周期边界的", "of which wrap around the cell"], String(wrap)]];
    }
    const nbin = Math.round(q.nbin), feat = Math.round(q.feat);
    const ha = this.hist(this.A, nbin), hb = this.hist(this.B, nbin);
    const same = this.gap(ha, hb) === 0;
    const ga = this.angle(this.A), gb = this.angle(this.B);
    const agap = this.gap(ga, gb);
    if (nbin >= 72 && same) api.done("same");
    if (feat === 1 && agap > 0) api.done("sep");
    return [[["两套距离一样吗", "are the pair distances the same"],
             same ? api.T("完全一样", "identical") : api.T("不一样", "different")],
            [["直方图分了几格", "histogram bins"], String(nbin)],
            [["两条直方图最大差多少", "largest difference between the histograms"],
             this.gap(ha, hb).toFixed(0)],
            [["补上三体之后差多少", "gap once three-body features are added"], agap.toFixed(0)],
            [["结论", "conclusion"],
             feat ? api.T("三体一进来就分开了", "they separate as soon as three-body enters")
                  : api.T("只看两体：分不开", "pair distances alone: indistinguishable")]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p;
    if (api.scene === "graph") {
      const rc = +q.rc.toFixed(1), which = Math.round(q.which), st = this.sites(which);
      const e = this.edges(st, rc);
      const g = api.graph({ x: 46, y: 28, w: w - 92, h: (h - 96) * 0.56,
                            xmin: -1, xmax: this.L, ymin: -1.4, ymax: 1.4,
                            xlabel: api.T("周期坐标（周期 18）", "periodic coordinate (period 18)"),
                            ylabel: "" }).axes();
      g.hline(0, api.css("--muted"));
      const col = which ? api.css("--red") : api.css("--blue");
      for (const edge of e) {
        const x1 = st[edge.a], x2 = st[edge.b];
        if (edge.wrap) {
          g.seg(x1, 0, this.L - 0.6, 0.85, api.css("--muted"), 1.6);
          g.seg(-0.6, 0.85, x2, 0, api.css("--muted"), 1.6);
        } else {
          const mid = (x1 + x2) / 2, hgt = -0.25 - 0.09 * edge.d;
          g.seg(x1, 0, mid, hgt, col, 1.8);
          g.seg(mid, hgt, x2, 0, col, 1.8);
        }
      }
      for (const x of st) g.point(x, 0, col);
      api.label(api.T(`截断半径 ${rc.toFixed(1)}：${e.length} 条边，平均配位数 ` +
                      `${(2 * e.length / st.length).toFixed(2)}`,
                      `cutoff ${rc.toFixed(1)}: ${e.length} edges, coordination ` +
                      `${(2 * e.length / st.length).toFixed(2)}`),
                46, 18, api.css("--ink"), 13);
      // 下半：边数随截断半径怎么长
      const g2 = api.graph({ x: 46, y: 28 + (h - 96) * 0.62, w: w - 92, h: (h - 96) * 0.38,
                             xmin: 1, xmax: 9, ymin: 0, ymax: 16,
                             xlabel: api.T("截断半径", "cutoff radius"),
                             ylabel: api.T("边数", "edges") }).axes();
      const pts = [];
      for (let r = 1; r <= 9.001; r += 0.25) pts.push([r, this.edges(st, r).length]);
      g2.pts(pts, col, 2.2);
      g2.vline(rc, api.css("--green"));
      return;
    }
    const nbin = Math.round(q.nbin), feat = Math.round(q.feat);
    const top = this.L / 2;
    const ha = this.hist(this.A, nbin), hb = this.hist(this.B, nbin);
    const g = api.graph({ x: 46, y: 28, w: (w - 110) * 0.5, h: h - 96,
                          xmin: 0, xmax: top, ymin: 0, ymax: 4,
                          xlabel: api.T("原子对的距离", "pair distance"),
                          ylabel: api.T("有多少对", "how many pairs") }).axes();
    for (let i = 0; i < nbin; i++) {
      const x = (i + 0.5) / nbin * top;
      if (ha[i]) g.seg(x - top / nbin * 0.22, 0, x - top / nbin * 0.22, ha[i], api.css("--blue"), 4);
      if (hb[i]) g.seg(x + top / nbin * 0.22, 0, x + top / nbin * 0.22, hb[i], api.css("--red"), 4);
    }
    api.label(api.T("两条直方图：蓝（甲）与红（乙）永远一样高",
                    "the two histograms: blue (A) and red (B) always agree"),
              46, 18, api.css("--ink"), 13);
    const g2 = api.graph({ x: 46 + (w - 110) * 0.56, y: 28, w: (w - 110) * 0.44, h: h - 96,
                           xmin: 0, xmax: 7, ymin: 0, ymax: 1000,
                           xlabel: api.T("第几个特征（排过序）", "feature index (sorted)"),
                           ylabel: api.T("特征值", "feature value") }).axes();
    if (feat) {
      const ga = this.angle(this.A), gb = this.angle(this.B);
      g2.pts(ga.map((v, i) => [i, v]), api.css("--blue"), 2.4);
      g2.pts(gb.map((v, i) => [i, v]), api.css("--green"), 2.4, [5, 4]);
      g2.text(api.T(`两者的最大差 ${this.gap(ga, gb)}`, `largest gap ${this.gap(ga, gb)}`),
              0.2, 930, api.css("--green"), 12);
    } else {
      g2.text(api.T("只看两体距离：这里没有任何可分辨的东西",
                    "pair distances only: nothing here separates them"),
              0.2, 500, api.css("--muted"), 12);
    }
  },
});
