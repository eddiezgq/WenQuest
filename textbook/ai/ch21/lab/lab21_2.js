// 实验 21.2 不良率、阈值与代价（配 21.2 节）。
// 两个场景：
//   metrics ：拖不良率与阈值，看准确率、查准率、查全率怎么变，并与“全判合格”比；
//   cost    ：拖漏检与误判的代价，看最优阈值往哪边移，以及按“准确率最高”定阈值要多花多少。
// 与 code/_ch21.py 是同一套算法（sample_scores、confusion、metrics、cost_of）。
WQ.lab({
  title: ["实验 21.2 不良率一变，分数就变；代价一变，阈值就得动",
          "Lab 21.2 Change the defect rate and the scores change; change the costs and the threshold must move"],
  goal: ["先把不良率从 20% 拖到 0.05%，盯住一件事：查全率和误判率一动不动，查准率却塌了——变的不是检测器，是基率。再把“全判合格”的准确率放在旁边比一比，你会看到产线上印准确率基本等于什么都没说。第二个场景把漏检与误判的代价分开给，拖一拖就知道：阈值是经济决策，不是统计决策。做完要能回答：验收一个视觉检测，该写哪三个数。",
         "First drag the defect rate from 20% down to 0.05% and watch one thing: recall and false-positive rate do not move, while precision collapses — the detector did not change, the base rate did. Put the accuracy of 'pass everything' beside it and you will see that accuracy says almost nothing on a production line. The second scene separates the cost of a miss from the cost of a false alarm: the threshold is an economic decision, not a statistical one. You should be able to say which three numbers belong in an acceptance clause."],
  scenes: [
    { id: "metrics", name: ["不良率与指标", "Defect rate and the metrics"],
      problem: { title: ["问题：99% 的准确率够不够好", "Problem: is 99% accuracy any good"],
                 text: ["产线的不良率常常是千分之几。这时“全判合格”这个什么也不做的方案，准确率就有 99.5%。所以一个检测器报出来的准确率，必须跟**不良率**一起看；更有用的是**查准率**（报出来的里面有多少真是坏件）与**查全率**（坏件里有多少被抓到）。这个场景让你亲手把不良率拖一遍，看哪几个数变、哪几个数不变。",
                        "Defect rates on a line are often a few per thousand. At that rate, doing nothing and passing everything already scores 99.5% accuracy. A detector's accuracy therefore has to be read together with the defect rate; precision and recall say far more. Drag the defect rate here and see which numbers move and which do not."] } },
    { id: "cost", name: ["代价与阈值", "Costs and the threshold"],
      problem: { title: ["问题：阈值该放哪", "Problem: where should the threshold go"],
                 text: ["漏掉一个坏件，可能是客户退货、召回、甚至安全事故；误判一个好件，多半只是复检或报废一件。两者代价差几十倍到上千倍，**最优阈值就要跟着移**。这个场景把两个代价分开给你，拖一拖看最优阈值往哪走；旁边还放着“按准确率最高”定的阈值，比比两者的总代价差多少。",
                        "A missed defect can mean a return, a recall or a safety incident; a false alarm usually costs one re-inspection or one scrapped part. When the two costs differ by orders of magnitude the optimal threshold moves with them. Drag the costs and watch where the optimum goes, with the accuracy-optimal threshold shown alongside for comparison."] } },
  ],
  params: [
    { id: "rate", name: ["不良率（%）", "defect rate (%)"], min: 0.05, max: 20, step: 0.05, value: 5, digits: 2 },
    { id: "thr", name: ["判定阈值", "decision threshold"], min: -1, max: 5, step: 0.05, value: 1.1, digits: 2 },
    { id: "sep", name: ["检测器的本事（两类分开多远）", "detector separation"], min: 1, max: 4, step: 0.1, value: 2.2, digits: 1 },
    { id: "miss", name: ["漏检一个的代价", "cost of one miss"], min: 1, max: 1000, step: 1, value: 100, digits: 0 },
    { id: "false", name: ["误判一个的代价", "cost of one false alarm"], min: 1, max: 50, step: 1, value: 1, digits: 0 },
    { id: "views", name: ["一个零件拍几张图", "images per part"], min: 1, max: 6, step: 1, value: 1, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["好件的分数分布", "scores of good parts"] },
           { color: "var(--red)", name: ["坏件的分数分布", "scores of defective parts"] },
           { color: "var(--green)", name: ["当前阈值", "current threshold"] },
           { color: "var(--muted)", name: ["代价最低的阈值", "cost-optimal threshold"] }],
  tasks: [
    { id: "base", text: ["不良率 5%、阈值 1.1：记下准确率、查准率、查全率。再把不良率拖到 0.05%，这三个数各变成多少？",
                         "At a 5% defect rate and threshold 1.1, record accuracy, precision and recall; then drag the rate to 0.05% and record them again."],
      demo: { scene: "metrics", set: { rate: 5, thr: 1.1 }, press: [] } },
    { id: "lowrate", text: ["不良率拖到 0.05%：检测器的准确率比“全判合格”高还是低？这说明什么？",
                            "At 0.05%, is the detector's accuracy above or below that of passing everything? What does that tell you?"],
      demo: { scene: "metrics", set: { rate: 0.05, thr: 1.1 }, press: [] } },
    { id: "views", text: ["把“一个零件拍几张图”拖到 5：误判率涨了几倍？查全率涨了多少？报指标时为什么必须写明按图片还是按零件？",
                          "Set images per part to 5: how much does the false-alarm rate grow, and how much does recall gain?"],
      demo: { scene: "metrics", set: { rate: 1, thr: 1.1, views: 5 }, press: [] } },
    { id: "cost", text: ["切到第二个场景，把漏检代价从 1 拖到 1000（误判仍为 1）：代价最低的阈值移到哪了？",
                         "In the second scene drag the cost of a miss from 1 to 1000 with the false-alarm cost at 1: where does the optimal threshold go?"],
      demo: { scene: "cost", set: { miss: 1000, false: 1, rate: 1 }, press: [] } },
    { id: "penalty", text: ["同样的代价比，把阈值拖到“按准确率最高”的那个位置：总代价比最优高多少倍？",
                            "At the same cost ratio, drag the threshold to the accuracy-optimal position: how many times the minimum cost is it?"],
      demo: { scene: "cost", set: { miss: 100, false: 1, rate: 1, thr: 3.7 }, press: [] } },
  ],
  think: ["你们厂的漏检代价与误判代价各是多少？把两个数写下来，再回到这个实验里找最优阈值——它与你们现在用的阈值差多少？如果写不出这两个数，这个实验告诉你的第一件事就是：**先去把它们问出来**。",
          "What do a miss and a false alarm actually cost on your line? Write both numbers down, find the optimal threshold here, and compare it with the threshold you use today. If you cannot write the two numbers down, that is the first thing to go and find out."],

  N: 20000,
  rng(seed) { let x = (seed * 1103515245 + 12345) >>> 0; return () => { x = (x * 1103515245 + 12345) >>> 0; return x / 4294967296; }; },
  gauss(r) { const u = Math.max(r(), 1e-9), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  scores(rate, sep, views) {
    const key = [rate, sep, views].join(",");
    if (this._s && this._s.key === key) return this._s.val;
    const r = this.rng(7), nBad = Math.max(1, Math.round(this.N * rate));
    const good = [], bad = [];
    for (let i = 0; i < this.N - nBad; i++) good.push(this.gauss(r));
    for (let i = 0; i < nBad; i++) bad.push(sep + this.gauss(r));
    let g2 = good, b2 = bad;
    if (views > 1) {                       // 一个零件拍 views 张图，任何一张报警就判不良
      g2 = []; b2 = [];
      for (let i = 0; i + views <= good.length; i += views) {
        let m = -1e9;
        for (let k = 0; k < views; k++) m = Math.max(m, good[i + k]);
        g2.push(m);
      }
      for (let i = 0; i + 2 <= bad.length; i += 2) b2.push(Math.max(bad[i], bad[i + 1]));
    }
    const val = { good: g2, bad: b2 };
    this._s = { key, val };
    return val;
  },
  conf(good, bad, thr) {
    let tp = 0, fn = 0, fp = 0, tn = 0;
    for (const s of bad) (s >= thr ? tp++ : fn++);
    for (const s of good) (s >= thr ? fp++ : tn++);
    return { tp, fn, fp, tn };
  },
  met(c) {
    const n = c.tp + c.fn + c.fp + c.tn;
    const prec = c.tp + c.fp ? c.tp / (c.tp + c.fp) : 0;
    const rec = c.tp + c.fn ? c.tp / (c.tp + c.fn) : 0;
    return { acc: n ? (c.tp + c.tn) / n : 0, prec, rec,
             fpr: c.fp + c.tn ? c.fp / (c.fp + c.tn) : 0 };
  },
  cost(c, miss, fals) { return c.fn * miss + c.fp * fals; },
  bestThr(good, bad, miss, fals) {
    let best = -1, bestC = Infinity;
    for (let t = -1; t <= 5.001; t += 0.05) {
      const cc = this.cost(this.conf(good, bad, t), miss, fals);
      if (cc < bestC) { bestC = cc; best = t; }
    }
    return { thr: best, cost: bestC };
  },
  accThr(good, bad) {
    let best = -1, bestA = -1;
    for (let t = -1; t <= 5.001; t += 0.05) {
      const a = this.met(this.conf(good, bad, t)).acc;
      if (a > bestA) { bestA = a; best = t; }
    }
    return best;
  },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p, rate = q.rate / 100, views = Math.round(q.views);
    const { good, bad } = this.scores(rate, q.sep, views);
    const c = this.conf(good, bad, q.thr);
    const m = this.met(c);
    const allPass = 1 - bad.length / (good.length + bad.length);
    if (api.scene === "metrics") {
      if (q.rate <= 0.06) api.done("lowrate");
      if (Math.abs(q.rate - 5) < 0.3) api.done("base");
      if (views >= 5) api.done("views");
      return [[["不良率", "defect rate"], (bad.length / (good.length + bad.length) * 100).toFixed(2) + "%"],
              [["准确率", "accuracy"], (m.acc * 100).toFixed(2) + "%"],
              [["“全判合格”的准确率", "accuracy of passing everything"], (allPass * 100).toFixed(2) + "%"],
              [["查准率（报出来的里真坏的）", "precision"], (m.prec * 100).toFixed(1) + "%"],
              [["查全率（坏件被抓到的）", "recall"], (m.rec * 100).toFixed(1) + "%"],
              [["误判率", "false-positive rate"], (m.fpr * 100).toFixed(2) + "%"],
              [["按几张图算", "unit of analysis"],
               views > 1 ? api.T(`按零件（${views} 张图）`, `per part (${views} images)`)
                         : api.T("按图片", "per image")]];
    }
    const miss = Math.round(q.miss), fals = Math.round(q.false);
    const best = this.bestThr(good, bad, miss, fals);
    const here = this.cost(c, miss, fals);
    const at = this.accThr(good, bad);
    const atCost = this.cost(this.conf(good, bad, at), miss, fals);
    if (miss >= 900) api.done("cost");
    if (Math.abs(q.thr - at) < 0.12 && miss >= 50) api.done("penalty");
    return [[["漏检:误判", "miss:false ratio"], `${miss}:${fals}`],
            [["当前阈值的总代价", "cost at the current threshold"], here.toFixed(0)],
            [["代价最低的阈值", "cost-optimal threshold"], best.thr.toFixed(2)],
            [["那时的总代价", "cost there"], best.cost.toFixed(0)],
            [["按“准确率最高”定的阈值", "accuracy-optimal threshold"], at.toFixed(2)],
            [["它要多花", "its penalty"], (atCost / Math.max(best.cost, 1e-9)).toFixed(1) + api.T(" 倍", "×")]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p, views = Math.round(q.views);
    const { good, bad } = this.scores(q.rate / 100, q.sep, views);
    const lo = -3.5, hi = 6.5, nb = 56;
    const hg = new Array(nb).fill(0), hb = new Array(nb).fill(0);
    for (const x of good) { const i = Math.floor((x - lo) / (hi - lo) * nb); if (i >= 0 && i < nb) hg[i]++; }
    for (const x of bad) { const i = Math.floor((x - lo) / (hi - lo) * nb); if (i >= 0 && i < nb) hb[i]++; }
    const topG = Math.max(1, ...hg), topB = Math.max(1, ...hb);
    const g = api.graph({ x: 52, y: 28, w: w - 104, h: (h - 96) * 0.56,
                          xmin: lo, xmax: hi, ymin: 0, ymax: 1.15,
                          xlabel: api.T("检测器给的分数", "detector score"),
                          ylabel: api.T("各自归一化的件数", "counts, each normalised") }).axes();
    for (let i = 0; i < nb; i++) {
      const x = lo + (i + 0.5) / nb * (hi - lo), bw = (hi - lo) / nb * 0.42;
      if (hg[i]) g.seg(x - bw * 0.5, 0, x - bw * 0.5, hg[i] / topG, api.css("--blue"), 4);
      if (hb[i]) g.seg(x + bw * 0.5, 0, x + bw * 0.5, hb[i] / topB, api.css("--red"), 4);
    }
    g.vline(q.thr, api.css("--green"));
    g.text(api.T("当前阈值", "threshold"), q.thr + 0.08, 1.05, api.css("--green"), 12);
    if (api.scene === "cost") {
      const best = this.bestThr(good, bad, Math.round(q.miss), Math.round(q.false));
      g.vline(best.thr, api.css("--muted"));
      g.text(api.T("代价最低", "cost optimum"), best.thr + 0.08, 0.92, api.css("--muted"), 12);
    }

    const g2 = api.graph({ x: 52, y: 28 + (h - 96) * 0.64, w: w - 104, h: (h - 96) * 0.36,
                           xmin: lo, xmax: hi, ymin: 0, ymax: 1.1,
                           xlabel: api.T("阈值", "threshold"),
                           ylabel: api.scene === "cost" ? api.T("总代价（归一化）", "cost (normalised)")
                                                        : api.T("百分比", "fraction") }).axes();
    if (api.scene === "cost") {
      const miss = Math.round(q.miss), fals = Math.round(q.false);
      const pts = [];
      let mn = Infinity;
      for (let t = lo; t <= hi; t += 0.1) { const c = this.cost(this.conf(good, bad, t), miss, fals); pts.push([t, c]); mn = Math.min(mn, c); }
      g2.pts(pts.map((p) => [p[0], Math.min(1.05, p[1] / Math.max(mn, 1e-9) / 8)]), api.css("--red"), 2.4);
      g2.text(api.T("（纵轴压缩过，只看形状与最低点）", "(vertical axis compressed)"),
              lo + 0.2, 1.0, api.css("--muted"), 11);
    } else {
      const pr = [], rc = [];
      for (let t = lo; t <= hi; t += 0.1) {
        const m = this.met(this.conf(good, bad, t));
        pr.push([t, m.prec]); rc.push([t, m.rec]);
      }
      g2.pts(pr, api.css("--red"), 2.4);
      g2.pts(rc, api.css("--blue"), 2.0, [5, 4]);
      g2.text(api.T("红：查准率　蓝：查全率", "red: precision, blue: recall"),
              lo + 0.2, 1.02, api.css("--ink"), 12);
    }
    g2.vline(q.thr, api.css("--green"));
  },
});
