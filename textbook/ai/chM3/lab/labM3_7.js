// 实验 M3.7 评测的数字有多靠得住（配 M3.7 节，回扣 13.8 节）。
// 两个场景：
//   ci   ：一个模型测出来的准确率有多大的区间，区间随题数怎样收窄；两个模型的区间什么时候还重叠；
//   pick ：在同一批题上从若干个配置里挑最好的，挑出来的那个在新题上会掉多少（"挑选带来的乐观"）。
// 全部在浏览器里现算（威尔逊区间 + 二项抽样），不需要显卡。
WQ.lab({
  title: ["实验 M3.7 评测的数字有多靠得住", "Lab M3.7 How much to trust an evaluation number"],
  goal: ["自己调题数和两个模型的真实水平，看算出来的准确率带多大的区间、两条区间什么时候还重叠；再看“在同一批题上挑最好的”会把成绩抬高多少，换一批新题又会掉回去多少。做完这两件事，就知道为什么榜单上差一两个百分点往往说明不了什么。",
         "Change the number of questions and the two models' true accuracies: see how wide the intervals are, when they still overlap, and how much picking the best configuration on one set inflates the score — and how much it falls back on fresh questions."],
  scenes: [
    { id: "ci", name: ["一个数字的区间", "The interval around a number"],
      problem: { title: ["问题：76% 和 79%，后者更好吗", "Problem: is 79% better than 76%"],
                 text: ["在 200 道题上测出 76% 与 79%，差 3 个百分点。可是每个数字本身都带着抽样误差：题目换一批，数字就会变。要先知道这个误差有多大，才谈得上比较。",
                        "On 200 questions one model scores 76% and another 79%. Each number carries sampling error: change the questions and both move. You need the size of that error before you can compare."] } },
    { id: "pick", name: ["挑最好的要付的代价", "The cost of picking the best"],
      problem: { title: ["问题：挑出来的那个，真有那么好吗", "Problem: is the winner really that good"],
                 text: ["试了若干个配置，在同一批题上挑分最高的报出去。即使这些配置水平完全一样，挑出来的那个也一定高于真实水平——挑的是运气，不只是本事。换一批新题，它就掉回去了。",
                        "Try several configurations, pick the top scorer on one test set. Even if they are all equally good, the winner scores above the truth — you picked luck as well as skill. On fresh questions it falls back."] } },
  ],
  params: [
    { id: "n", name: ["题数", "questions"], min: 20, max: 4000, step: 20, value: 200, digits: 0 },
    { id: "accA", name: ["模型甲的真实准确率（%）", "model A true accuracy (%)"], min: 30, max: 95, step: 1, value: 76, digits: 0 },
    { id: "accB", name: ["模型乙的真实准确率（%）", "model B true accuracy (%)"], min: 30, max: 95, step: 1, value: 79, digits: 0 },
    { id: "K", name: ["试了几个配置", "configurations tried"], min: 1, max: 50, step: 1, value: 20, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["模型甲", "model A"] }, { color: "var(--amber)", name: ["模型乙", "model B"] },
           { color: "var(--red)", name: ["挑出来的那个", "the picked one"] }],
  tasks: [
    { id: "overlap", text: ["题数 200、甲 76%、乙 79%：两条区间重叠吗？把题数加到多少，区间才刚好分开？",
                            "With 200 questions, 76% vs 79%: do the intervals overlap? How many questions until they just separate?"],
      demo: { scene: "ci", set: { n: 3200, accA: 76, accB: 79 }, press: [] } },
    { id: "width", text: ["把题数从 200 加到 800（四倍）：区间宽度变成原来的几分之几？与 $1/\\sqrt{n}$ 对得上吗？",
                          "Raise the questions from 200 to 800 (four times): by what factor does the width shrink? Does it match 1/sqrt(n)?"],
      demo: { scene: "ci", set: { n: 800 }, press: [] } },
    { id: "pick20", text: ["切到第二个场景：20 个配置、真实水平都一样，挑出来的那个比真实水平高多少？",
                           "Switch to the second scene: with 20 equally good configurations, how far above the truth does the winner score?"],
      demo: { scene: "pick", set: { K: 20, n: 200 }, press: [] } },
    { id: "pickn", text: ["题数加到 2000 再看：“挑选带来的乐观”变小了吗？配置数加到 50 呢？",
                          "Now raise the questions to 2000: does the optimism shrink? What if you try 50 configurations?"],
      demo: { scene: "pick", set: { K: 50, n: 2000 }, press: [] } },
  ],
  think: ["榜单上两个模型差 1 个百分点，你会怎样判断这个差是不是真的？至少要知道哪三件事？",
          "Two models on a leaderboard differ by one point: what three things do you need to know before believing it?"],

  Z: 1.96,
  wilson(k, n) {                                  // 威尔逊区间：小样本、比例接近 0 或 1 时比正态近似可靠
    if (n <= 0) return [0, 1];
    const p = k / n, z = this.Z, d = 1 + z * z / n;
    const c = (p + z * z / (2 * n)) / d;
    const h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d;
    return [Math.max(0, c - h), Math.min(1, c + h)];
  },
  rand(seed) { let t = seed + 0x6d2b79f5; return () => { t += 0x6d2b79f5; let x = Math.imul(t ^ (t >>> 15), 1 | t); x ^= x + Math.imul(x ^ (x >>> 7), 61 | x); return ((x ^ (x >>> 14)) >>> 0) / 4294967296; }; },
  binom(n, p, rnd) { let k = 0; for (let i = 0; i < n; i++) if (rnd() < p) k++; return k; },
  calc(api) {
    const p = api.p, key = [p.n, p.accA, p.accB, p.K].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const n = p.n, a = p.accA / 100, b = p.accB / 100;
    const ciA = this.wilson(Math.round(a * n), n), ciB = this.wilson(Math.round(b * n), n);
    // 换一批题会怎样：各抽 400 次，看两个模型测出来的差
    const rnd = this.rand(99);
    let bWins = 0, diffs = [];
    for (let i = 0; i < 400; i++) {
      const ka = this.binom(n, a, rnd) / n, kb = this.binom(n, b, rnd) / n;
      diffs.push(kb - ka);
      if (kb > ka) bWins++;
    }
    diffs.sort((x, y) => x - y);
    // 挑最好的：K 个水平完全相同的配置，在同一批题上挑分最高的，再在新题上测
    const picked = [], fresh = [];
    for (let t = 0; t < 300; t++) {
      let best = -1;
      for (let j = 0; j < p.K; j++) best = Math.max(best, this.binom(n, a, rnd) / n);
      picked.push(best);
      fresh.push(this.binom(n, a, rnd) / n);                   // 换一批新题，水平回到真实值附近
    }
    const mean = (xs) => xs.reduce((s, x) => s + x, 0) / xs.length;
    const val = { n, a, b, ciA, ciB, overlap: ciB[0] < ciA[1],
                  bWinPct: bWins / 400 * 100, dLo: diffs[10], dHi: diffs[389],
                  pickMean: mean(picked), freshMean: mean(fresh), optimism: mean(picked) - a };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const p = api.p, c = this.calc(api);
    if (api.scene === "ci" && !c.overlap) api.done("overlap");          // 区间刚好分开时才算完成
    if (api.scene === "ci" && p.n >= 800) api.done("width");
    if (api.scene === "pick" && p.K >= 20) api.done("pick20");
    if (api.scene === "pick" && p.n >= 2000) api.done("pickn");
    if (api.scene === "ci") {
      return [[["甲的区间", "interval A"], `${(c.ciA[0] * 100).toFixed(1)}% – ${(c.ciA[1] * 100).toFixed(1)}%`],
              [["乙的区间", "interval B"], `${(c.ciB[0] * 100).toFixed(1)}% – ${(c.ciB[1] * 100).toFixed(1)}%`],
              [["区间宽度（甲）", "width (A)"], api.fmt((c.ciA[1] - c.ciA[0]) * 100, 1) + api.T(" 个百分点", " points")],
              [["两条区间重叠吗", "do they overlap"], c.overlap ? api.T("重叠——说不出谁好", "yes — inconclusive")
                                                               : api.T("分开了", "no")],
              [["换一批题，乙仍然更高的比例", "B still higher on fresh questions"], api.fmt(c.bWinPct, 0) + "%"],
              [["两者之差的 95% 范围", "95% range of the gap"],
               `${(c.dLo * 100).toFixed(1)} – ${(c.dHi * 100).toFixed(1)} ` + api.T("个百分点", "points")]];
    }
    return [[["真实水平（都一样）", "true accuracy (all equal)"], api.fmt(c.a * 100, 0) + "%"],
            [["挑出来的那个在这批题上", "winner on the same questions"], api.fmt(c.pickMean * 100, 1) + "%"],
            [["换一批新题再测", "the same model on fresh questions"], api.fmt(c.freshMean * 100, 1) + "%"],
            [["挑选带来的乐观", "optimism from picking"], "+" + api.fmt(c.optimism * 100, 1) + api.T(" 个百分点", " points")],
            [["试的配置数", "configurations"], String(p.K)],
            [["题数", "questions"], String(p.n)]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api), p = api.p;
    const x0 = 70, y0 = 30, pw = w - x0 - 30, ph = h - y0 - 50;
    const lo = Math.max(0, Math.min(c.ciA[0], c.ciB[0]) - 0.08), hi = Math.min(1, Math.max(c.ciA[1], c.ciB[1]) + 0.08);
    const X = (v) => x0 + (v - lo) / (hi - lo) * pw;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    for (let t = Math.ceil(lo * 20) / 20; t <= hi; t += 0.05) {
      api.line(X(t), y0, X(t), y0 + ph, api.css("--grid"), 1);
      api.label((t * 100).toFixed(0) + "%", X(t) - 12, y0 + ph + 18, api.css("--muted"), 11);
    }
    if (api.scene === "ci") {
      const rows = [[c.ciA, c.a, api.css("--blue"), api.T("模型甲", "model A")],
                    [c.ciB, c.b, api.css("--amber"), api.T("模型乙", "model B")]];
      rows.forEach(([ci, tru, col, name], i) => {
        const y = y0 + ph * (0.33 + 0.34 * i);
        api.line(X(ci[0]), y, X(ci[1]), y, col, 6);
        api.line(X(ci[0]), y - 9, X(ci[0]), y + 9, col, 2);
        api.line(X(ci[1]), y - 9, X(ci[1]), y + 9, col, 2);
        api.circle(X(tru), y, 5, null, api.css("--ink"));
        api.label(name, 14, y + 4, col, 13);
      });
      api.label(api.T("横条是 95% 置信区间，黑点是测出来的准确率；两条重叠就分不出谁好",
                      "bars are 95% intervals, dots the measured accuracy; overlapping bars are inconclusive"),
                x0, h - 14, api.css("--muted"), 12);
      return;
    }
    const y = y0 + ph * 0.45;
    api.line(X(c.a), y0 + 10, X(c.a), y0 + ph - 10, api.css("--ink"), 2, [5, 4]);
    api.label(api.T("真实水平", "truth"), X(c.a) - 24, y0 + 6, api.css("--ink"), 12);
    api.circle(X(c.pickMean), y, 7, null, api.css("--red"));
    api.label(api.T(`挑出来的 ${(c.pickMean * 100).toFixed(1)}%`, `picked ${(c.pickMean * 100).toFixed(1)}%`),
              X(c.pickMean) - 30, y - 14, api.css("--red"), 12);
    api.circle(X(c.freshMean), y + 42, 7, null, api.css("--blue"));
    api.label(api.T(`换新题 ${(c.freshMean * 100).toFixed(1)}%`, `fresh ${(c.freshMean * 100).toFixed(1)}%`),
              X(c.freshMean) - 30, y + 62, api.css("--blue"), 12);
    api.label(api.T(`试了 ${p.K} 个配置、每个测 ${p.n} 道题：挑出来的那个高了 ${(c.optimism * 100).toFixed(1)} 个百分点`,
                    `${p.K} configurations, ${p.n} questions each: the winner is ${(c.optimism * 100).toFixed(1)} points above the truth`),
              x0, h - 14, api.css("--muted"), 12);
  },
});
