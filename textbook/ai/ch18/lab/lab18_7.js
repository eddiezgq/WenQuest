// 实验 18.7 读懂预测结构的可信度（配 18.7 节）。
// 两个场景：
//   track  ：沿着序列看自评分数与真实误差，三段（核心域、连接段、尾巴）各是什么样；
//   decide ：定一条分数门限，看”收下的残基里有多少其实是错的”与”扔掉的里有多少本来是对的“。
// 全部按解析式与同一个随机模型现算，瞬时出结果。与 code/_ch18.py 是同一套做法。
WQ.lab({
  title: ["实验 18.7 读懂预测结构的可信度", "Lab 18.7 Reading the confidence of a predicted structure"],
  goal: ["拿到一个预测结构和一张逐残基的自评分数图，判断哪几段能信、能拿去做什么。做完能回答三个问题：自评 90 分以上到底意味着什么、为什么没有一条门限能做到万无一失、相关性变差时这些结论怎么变。",
         "Given a predicted structure and its per-residue self-score, decide which parts to trust and what they can be used for. You should be able to say what a score above 90 actually means, why no threshold is watertight, and how the picture changes when the correlation gets worse."],
  scenes: [
    { id: "track", name: ["沿着序列看", "Along the sequence"],
      problem: { title: ["问题：这张图在说什么", "Problem: what the plot is telling you"],
                 text: ["预测工具会给每个残基一个自评分数（0—100）。这条蛋白有三段：紧实的核心域、柔性的连接段、末端的尾巴。分数在三段上的样子完全不同。要紧的是：**这个分数是模型对自己的估计，不是“对的概率”**。它与真实误差只是相关——公开论文给的相关系数是 0.76。",
                        "The predictor gives every residue a self-score from 0 to 100. This protein has three parts: a compact core domain, a flexible linker and a tail, and the score looks quite different on each. The key point: the score is the model's estimate of itself, not a probability of being right. It is merely correlated with the true error — the published correlation is 0.76."] } },
    { id: "decide", name: ["定一条门限", "Pick a threshold"],
      problem: { title: ["问题：收下哪些残基", "Problem: which residues do you keep"],
                 text: ["要拿这个结构做事，就得划一条线：分数高于门限的收下，低于的不用。两种代价同时存在——收下的里有一部分其实错得离谱（白用了），扔掉的里有一部分本来是对的（白扔了）。门限往上调，第一种少、第二种多；往下调反过来。**没有哪条门限能把两种代价同时清零**，这正是第 17.6 节那道人工确认闸的同一笔账。",
                        "To use the structure you must draw a line: keep residues above the threshold, drop the rest. Two costs exist at once — some of what you keep is badly wrong, and some of what you drop was fine. Raising the threshold trades one for the other, and no threshold drives both to zero. It is the same arithmetic as the human-approval gate of Section 17.6."] } },
  ],
  params: [
    { id: "cut", name: ["分数门限", "score threshold"], min: 40, max: 95, step: 1, value: 70, digits: 0 },
    { id: "r", name: ["分数与误差的相关系数", "score–error correlation"], min: 0.2, max: 0.95, step: 0.01, value: 0.76, digits: 2 },
    { id: "bad", name: ["错多少算不能用（Å）", "error that counts as unusable (Å)"], min: 1, max: 5, step: 0.5, value: 2, digits: 1 },
    { id: "seed", name: ["换一条蛋白", "another protein"], min: 0, max: 20, step: 1, value: 0, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["自评分数", "self-score"] },
           { color: "var(--red)", name: ["真实误差", "true error"] },
           { color: "var(--green)", name: ["收下且确实好", "kept and really good"] },
           { color: "var(--accent)", name: ["收下却错得离谱", "kept but badly wrong"] }],
  tasks: [
    { id: "regions", text: ["在”沿着序列看”里记下三段各自的分数中位数与误差中位数。哪一段的分数最低？它低是因为”预测错了”还是因为”那里本来就没有固定结构“？",
                            "In the first scene, record the median score and median error for each of the three parts. Which part scores lowest, and is that because the prediction failed or because there is no fixed structure there?"],
      demo: { scene: "track", set: { r: 0.76, seed: 0 }, press: [] } },
    { id: "top", text: ["切到”定一条门限“，把门限设到 90：收下的残基里，仍然错超过 2 Å 的占多少？这个数是零吗？",
                        "Switch to the threshold scene and set it to 90: among the residues you keep, what share is still off by more than 2 Å? Is it zero?"],
      demo: { scene: "decide", set: { cut: 90, r: 0.76, bad: 2 }, press: [] } },
    { id: "low", text: ["把门限降到 50：收下的多了多少，错得离谱的又多了多少？两条代价是怎么换的？",
                        "Lower the threshold to 50: how many more residues do you keep, and how many more of them are badly wrong? How do the two costs trade off?"],
      demo: { scene: "decide", set: { cut: 50 }, press: [] } },
    { id: "sweep", text: ["把门限从 40 一路拖到 95，找出”收下的里错得离谱的比例低于 5%”的那一档。此时你扔掉了多少本来是对的残基？",
                          "Drag the threshold from 40 to 95 and find where the share of badly-wrong kept residues falls below 5%. How many good residues did you throw away to get there?"],
      demo: { scene: "decide", set: { cut: 95 }, press: [] } },
    { id: "worse", text: ["把相关系数从 0.76 降到 0.4（门限仍放在 90）：同一条门限现在收下的东西有多脏？这说明”门限要定在哪”取决于什么？",
                          "Drop the correlation from 0.76 to 0.4 with the threshold still at 90: how much dirtier is what you keep? What does that say about where the threshold should sit?"],
      demo: { scene: "decide", set: { cut: 90, r: 0.4 }, press: [] } },
  ],
  think: ["本实验里”真实误差”是知道的，现实里不知道。如果只有自评分数，你怎样判断这一次的相关性是好是坏？写出一条能在真实项目里执行的检查，并说明它要花什么代价。",
          "Here the true error is known; in a real project it is not. With only the self-score in hand, how would you tell whether the correlation holds this time? Write down a check you could actually run, and say what it costs."],

  N_CORE: 150, N_LINK: 40, N_TAIL: 30, SMOOTH: 3,
  rng(seed) { let s = seed * 2654435761 + 97; return () => { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }; },
  gauss(r) { const u = Math.max(1e-9, r()), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  part(n, r, rnd, shift) {
    const m = this.SMOOTH, raw = [];
    for (let i = 0; i < n + 2 * m; i++) raw.push(this.gauss(rnd));
    const sm = [];
    for (let i = 0; i < n; i++) {
      let s = 0;
      for (let d = -m; d <= m; d++) s += raw[i + m + d];
      sm.push(s / (2 * m + 1));
    }
    const mean = sm.reduce((a, b) => a + b, 0) / n;
    const sd = Math.sqrt(sm.reduce((a, b) => a + (b - mean) * (b - mean), 0) / n) || 1;
    const out = [];
    for (let i = 0; i < n; i++) {
      const z1 = sm[i] / sd + shift;
      const z2 = r * z1 + Math.sqrt(Math.max(0, 1 - r * r)) * this.gauss(rnd);
      out.push([Math.min(99, Math.max(1, 70 + 17 * z1)), Math.exp(0.75 - 0.75 * z2)]);
    }
    return out;
  },
  calc(api) {
    const q = api.p, key = [q.r, q.seed, q.cut, q.bad].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const rnd = this.rng(Math.round(q.seed) + 1);
    const parts = [[this.N_CORE, 0.95], [this.N_LINK, -0.60], [this.N_TAIL, -1.55]];
    const score = [], err = [], reg = [];
    parts.forEach(([n, sh], k) => {
      this.part(n, q.r, rnd, sh).forEach(([s, e]) => { score.push(s); err.push(e); reg.push(k); });
    });
    const n = score.length, cut = q.cut, bad = q.bad;
    let kept = 0, keptBad = 0, dropped = 0, droppedGood = 0, allBad = 0;
    for (let i = 0; i < n; i++) {
      const isBad = err[i] > bad;
      if (isBad) allBad++;
      if (score[i] >= cut) { kept++; if (isBad) keptBad++; }
      else { dropped++; if (!isBad) droppedGood++; }
    }
    const med = (a) => { const b = a.slice().sort((x, y) => x - y); return b[Math.floor(b.length / 2)]; };
    const regions = [0, 1, 2].map((k) => {
      const s = [], e = [];
      for (let i = 0; i < n; i++) if (reg[i] === k) { s.push(score[i]); e.push(err[i]); }
      return { n: s.length, score: med(s), err: med(e) };
    });
    const val = { score, err, reg, n, cut, bad, kept, keptBad, dropped, droppedGood, allBad, regions,
                  dirty: kept ? keptBad / kept * 100 : 0,
                  waste: dropped ? droppedGood / dropped * 100 : 0 };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const c = this.calc(api), q = api.p;
    if (api.scene === "track") api.done("regions");
    if (api.scene === "decide" && q.cut >= 89 && q.r >= 0.7) api.done("top");
    if (api.scene === "decide" && q.cut <= 52) api.done("low");
    if (api.scene === "decide" && q.cut >= 94) api.done("sweep");
    if (api.scene === "decide" && q.r <= 0.45 && q.cut >= 85) api.done("worse");
    if (api.scene === "track") {
      const nm = [["核心域", "core"], ["连接段", "linker"], ["末端尾巴", "tail"]];
      return c.regions.map((g, k) => [[`${nm[k][0]}：分数中位 / 误差中位`, `${nm[k][1]}: median score / error`],
                                      `${g.score.toFixed(0)} / ${g.err.toFixed(2)} Å`])
        .concat([[["整条蛋白错超过门限的残基占", "residues off by more than the cut-off"],
                  (c.allBad / c.n * 100).toFixed(1) + "%"]]);
    }
    return [[["收下了多少残基", "residues kept"], `${c.kept} / ${c.n}`],
            [["收下的里错得离谱的占", "share of kept residues that are badly wrong"],
             c.dirty.toFixed(1) + "%"],
            [["扔掉的里本来是对的占", "share of dropped residues that were fine"],
             c.waste.toFixed(1) + "%"],
            [["白扔了多少个好残基", "good residues thrown away"], String(c.droppedGood)],
            [["收下却不能用的有几个", "kept but unusable"], String(c.keptBad)]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api);
    const x0 = 52, y0 = 26, pw = w - x0 - 150, ph = h - y0 - 46;
    const X = (i) => x0 + i / (c.n - 1) * pw;
    const Y = (v) => y0 + ph - v / 100 * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    const bounds = [0, this.N_CORE, this.N_CORE + this.N_LINK, c.n];
    const names = [["核心域", "core domain"], ["连接段", "linker"], ["末端尾巴", "tail"]];
    for (let k = 0; k < 3; k++) {
      if (k) api.line(X(bounds[k]), y0, X(bounds[k]), y0 + ph, api.css("--grid"), 1, [3, 3]);
      api.label(api.T(names[k][0], names[k][1]),
                (X(bounds[k]) + X(bounds[k + 1])) / 2 - 24, y0 - 8, api.css("--muted"), 11);
    }
    for (const g of [50, 70, 90]) {
      api.line(x0, Y(g), x0 + pw, Y(g), api.css("--grid"), 1);
      api.label(String(g), 26, Y(g) + 4, api.css("--muted"), 10);
    }
    let prev = null;
    for (let i = 0; i < c.n; i++) {
      const cur = [X(i), Y(c.score[i])];
      if (prev) api.line(prev[0], prev[1], cur[0], cur[1], api.css("--blue"), 1.6);
      prev = cur;
    }
    // 误差用对数高度画成点
    const EY = (e) => y0 + ph - Math.min(1, Math.max(0, (Math.log10(e) + 1) / 1.7)) * ph;
    for (let i = 0; i < c.n; i++) {
      const bad = c.err[i] > c.bad, kept = c.score[i] >= c.cut;
      let col = api.css("--red");
      if (api.scene === "decide") col = kept ? (bad ? api.css("--accent") : api.css("--green"))
                                             : api.css("--grid");
      api.circle(X(i), EY(c.err[i]), bad && kept ? 3.4 : 2.0, null, col);
    }
    if (api.scene === "decide") {
      api.line(x0, Y(c.cut), x0 + pw, Y(c.cut), api.css("--ink"), 1.6, [5, 4]);
      api.label(api.T(`门限 ${c.cut}`, `cut-off ${c.cut}`), x0 + 4, Y(c.cut) - 6, api.css("--ink"), 11);
    }
    api.label(api.T("自评分数", "self-score"), 8, y0 + 10, api.css("--blue"), 11);
    api.label(api.T("真实误差（对数）", "true error (log)"), 8, y0 + ph - 2, api.css("--red"), 11);
    api.label(api.T("第几个残基", "residue index"), x0 + pw / 2 - 28, h - 12, api.css("--muted"), 12);

    const bx = x0 + pw + 12;
    if (api.scene === "decide") {
      const rows = [[api.T("收下", "kept"), `${c.kept}`, api.css("--green")],
                    [api.T("其中错得离谱", "of them badly wrong"), `${c.keptBad}`, api.css("--accent")],
                    [api.T("收下的脏成数", "dirty share"), c.dirty.toFixed(1) + "%", api.css("--accent")],
                    [api.T("白扔的好残基", "good ones wasted"), `${c.droppedGood}`, api.css("--muted")]];
      rows.forEach((r, i) => api.label(`${r[0]} ${r[1]}`, bx, y0 + 18 + i * 22, r[2], 12));
      if (c.dirty > 0 && c.cut >= 90) {
        api.label(api.T("门限拉到最高，脏的也没清零", "even at the top the kept set is not clean"),
                  bx, y0 + 18 + 4 * 22 + 8, api.css("--red"), 11);
      }
    } else {
      const nm = [["核心域", "core"], ["连接段", "linker"], ["尾巴", "tail"]];
      c.regions.forEach((g, k) => {
        api.label(`${api.T(nm[k][0], nm[k][1])}  ${g.score.toFixed(0)} / ${g.err.toFixed(2)} Å`,
                  bx, y0 + 18 + k * 22, api.css("--ink"), 12);
      });
      api.label(api.T("分数中位 / 误差中位", "median score / median error"),
                bx, y0 + 18 + 3 * 22 + 6, api.css("--muted"), 11);
    }
  },
});
