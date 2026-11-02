// 实验 19.3 集合预报好不好，要两把尺子（配 19.3 节）。
// 三个场景：
//   spread ：拖离散度与偏差，看 CRPS 与离散度/技巧比怎么动；
//   rel    ：可靠性图——说 70% 的那些次，是不是真有七成发生了；
//   one    ：把同一套集合压成一个确定性预报，看它答不了哪个问题。
// 与 code/_ch19.py 是同一套算法（make_ensemble、crps_ensemble、spread_skill、reliability、brier）。
WQ.lab({
  title: ["实验 19.3 集合预报好不好，要两把尺子", "Lab 19.3 Judging an ensemble takes two rulers"],
  goal: ["亲手把一个集合调得太自信、再调得太含糊，看 CRPS 两头都罚、看可靠性图往哪边歪。然后把同一套集合压成一个数，看 RMSE 怎样把集合的价值整个藏起来。做完能回答：为什么概率预报不能只看 RMSE、离散度/技巧比接近 1 意味着什么。",
         "Make an ensemble over-confident, then too vague, and watch CRPS penalise both while the reliability diagram tilts one way or the other. Then squash the same ensemble into a single number and see how RMSE hides its value entirely. You should be able to say why a probabilistic forecast cannot be judged by RMSE alone, and what a spread/skill ratio near 1 means."],
  scenes: [
    { id: "spread", name: ["离散度调到多少才对", "How much spread is right"],
      problem: { title: ["问题：集合该有多散", "Problem: how spread out should an ensemble be"],
                 text: ["集合预报跑的是同一套方程、略有差别的初值，几十个成员铺开一片可能。成员铺得太窄，预报说得太满、实际常常落在集合外面；铺得太宽，什么都包含在内、等于没说。**离散度/技巧比**把这件事量成一个数：集合的离散度除以集合均值的均方根误差，校准良好时它接近 1。CRPS 是另一把尺子，它两头都罚——太自信和太含糊都会让它变大。",
                        "An ensemble runs the same equations from slightly different initial states, spreading dozens of members across the possibilities. Too narrow and the truth keeps falling outside; too wide and the forecast says nothing. The spread/skill ratio measures this: ensemble spread divided by the RMSE of the ensemble mean, close to 1 when well calibrated. CRPS is the other ruler, and it penalises both ends."] } },
    { id: "rel", name: ["概率说得老实不老实", "Is the stated probability honest"],
      problem: { title: ["问题：说 70% 的那些次，真有七成发生了吗", "Problem: when it says 70%, does it happen 70% of the time"],
                 text: ["把所有“说了 70%”的预报挑出来，数一数其中实际发生了几成。完全可靠的预报，这些点落在 45° 对角线上。点落在线**下方**，说明说得太满；落在**上方**，说明说得太保守。这张图叫可靠性图，它查的不是准不准，而是**老实不老实**——一个永远报气候概率的预报可以完全可靠，却毫无用处，所以可靠性要和 Brier 分数一起看。",
                        "Take every forecast that said 70% and count how often the event actually happened. A perfectly reliable forecast puts those points on the 45° line; below it the forecast claims too much, above it too little. The reliability diagram checks honesty rather than accuracy — a forecast that always states the climatological probability is perfectly reliable and perfectly useless, so read it together with the Brier score."] } },
    { id: "one", name: ["压成一个数会丢掉什么", "What squashing it loses"],
      problem: { title: ["问题：为什么不能只给一个数", "Problem: why a single number will not do"],
                 text: ["把集合的成员平均一下，就得到一个确定性预报。它的均方根误差可能和集合均值一样好看——可电网要问的是“明天风速低于切入的概率是多少”，这个预报只能答“是”或“否”。同一套信息，换个出法，能答的问题完全不同。这正是 19.6 节那笔账的来由。",
                        "Average the members and you have a deterministic forecast whose RMSE can look just as good. But the grid asks for the probability that tomorrow's wind falls below cut-in, and this forecast can only answer yes or no. The same information, presented differently, answers an entirely different set of questions."] } },
  ],
  params: [
    { id: "sf", name: ["离散度倍数（1 = 刚好）", "spread factor (1 = just right)"], min: 0.3, max: 2.0, step: 0.05, value: 1.0, digits: 2 },
    { id: "bias", name: ["系统偏差", "systematic bias"], min: -1, max: 1, step: 0.1, value: 0, digits: 1 },
    { id: "m", name: ["集合有几个成员", "ensemble members"], min: 1, max: 50, step: 1, value: 50, digits: 0 },
    { id: "thresh", name: ["事件门限", "event threshold"], min: -1, max: 2, step: 0.25, value: 1.0, digits: 2 },
    { id: "seed", name: ["换一批天气", "another batch of cases"], min: 0, max: 20, step: 1, value: 1, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["这一套集合", "this ensemble"] },
           { color: "var(--muted)", name: ["完全可靠的 45° 线 / 气候概率", "the 45° line / climatology"] },
           { color: "var(--red)", name: ["确定性预报（只能答是或否）", "deterministic (yes/no only)"] },
           { color: "var(--green)", name: ["校准最好的那一档", "best-calibrated setting"] }],
  tasks: [
    { id: "cal", text: ["离散度倍数 1.0、偏差 0：记下离散度/技巧比与 CRPS。这就是校准良好的样子。",
                        "At spread factor 1.0 and zero bias, record the spread/skill ratio and the CRPS. This is what well calibrated looks like."],
      demo: { scene: "spread", set: { sf: 1.0, bias: 0 }, press: [] } },
    { id: "narrow", text: ["把离散度倍数调到 0.5（太自信）：比变成多少？CRPS 变大还是变小？",
                           "Set the spread factor to 0.5 — over-confident. What does the ratio become, and does CRPS rise or fall?"],
      demo: { scene: "spread", set: { sf: 0.5, bias: 0 }, press: [] } },
    { id: "wide", text: ["再调到 1.6（太含糊）：CRPS 又变大了。两头都罚，说明 CRPS 量的是什么？",
                         "Now set it to 1.6 — too vague. CRPS rises again. What does penalising both ends tell you about what CRPS measures?"],
      demo: { scene: "spread", set: { sf: 1.6, bias: 0 }, press: [] } },
    { id: "diag", text: ["切到可靠性图，离散度倍数 0.5：点落在对角线哪一边？再调回 1.0 对比一下，记下最大偏离。",
                         "Switch to the reliability diagram at spread factor 0.5: which side of the line do the points fall on? Compare with 1.0 and record the largest deviation."],
      demo: { scene: "rel", set: { sf: 0.5, bias: 0 }, press: [] } },
    { id: "member", text: ["离散度调回 1.0，把成员数从 50 一路拖到 1：CRPS 怎么变？成员只剩一个时，它等于哪个常见的误差？",
                           "Back at 1.0, drag the member count from 50 down to 1. What happens to CRPS, and what familiar error does it equal at one member?"],
      demo: { scene: "spread", set: { sf: 1.0, m: 1 }, press: [] } },
    { id: "squash", text: ["切到第三个场景：确定性预报与集合均值的 RMSE 差多少？Brier 分数呢？哪一把尺子看得出集合的价值？",
                           "In the third scene compare the RMSE of the deterministic forecast and the ensemble mean, then compare their Brier scores. Which ruler sees the ensemble's value?"],
      demo: { scene: "one", set: { sf: 1.0, bias: 0 }, press: [] } },
  ],
  think: ["一个永远报气候概率的预报，可靠性图完全落在对角线上，却一点用也没有。请说出一个指标，它能同时惩罚“不可靠”和“没信息量”，并说明本实验里哪个数起了这个作用。",
          "A forecast that always states the climatological probability lands exactly on the 45° line and is useless. Name a measure that penalises both unreliability and lack of information, and say which number in this lab plays that role."],

  N: 3000,
  rng(seed) { let s = (seed + 1) * 2654435761 % 2147483647; return () => { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }; },
  normal(r) { let u = 0, v = 0; while (u === 0) u = r(); while (v === 0) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  // 真值 = 可预报的那部分 + 不可预报的那部分；成员 = 可预报的那部分 + 各自的扰动
  make(sf, bias, m, seed) {
    const key = [sf, bias, m, seed].join(",");
    if (this._e && this._e.key === key) return this._e.val;
    const r = this.rng(seed), n = this.N, sig = [], obs = [], mem = [];
    for (let i = 0; i < n; i++) { const g = this.normal(r); sig.push(g); obs.push(g + this.normal(r)); }
    for (let j = 0; j < m; j++) {
      const row = new Float64Array(n);
      for (let i = 0; i < n; i++) row[i] = sig[i] + bias + sf * this.normal(r);
      mem.push(row);
    }
    const val = { sig, obs, mem, m, n };
    this._e = { key, val };
    return val;
  },
  // 集合 CRPS（无偏估计量，分母 2M(M−1)；M = 1 时退化成平均绝对误差）。
  // 成员两两距离之和用排好序的成员算：∑|x_j−x_k| = 2∑(2j−M+1)·x_(j)，
  // 于是每一次预报只要 M log M，不是 M²——拖滑块才不卡。
  crps(e) {
    const { mem, obs, m, n } = e;
    let s = 0;
    const col = new Float64Array(m);
    for (let i = 0; i < n; i++) {
      let t1 = 0;
      for (let j = 0; j < m; j++) { const v = mem[j][i]; col[j] = v; t1 += Math.abs(v - obs[i]); }
      t1 /= m;
      if (m === 1) { s += t1; continue; }
      col.sort();
      let t2 = 0;
      for (let j = 0; j < m; j++) t2 += (2 * j - m + 1) * col[j];
      s += t1 - t2 / (m * (m - 1));
    }
    return s / n;
  },
  spreadSkill(e) {
    const { mem, obs, m, n } = e;
    let sv = 0, se = 0;
    for (let i = 0; i < n; i++) {
      let mu = 0; for (let j = 0; j < m; j++) mu += mem[j][i]; mu /= m;
      if (m > 1) { let v = 0; for (let j = 0; j < m; j++) v += Math.pow(mem[j][i] - mu, 2); sv += v / (m - 1); }
      se += Math.pow(mu - obs[i], 2);
    }
    const spread = Math.sqrt(sv / n), rmse = Math.sqrt(se / n);
    return { spread, rmse, ratio: rmse > 0 ? spread / rmse : NaN };
  },
  probs(e, th) {
    const { mem, obs, m, n } = e, p = new Float64Array(n), occ = new Uint8Array(n);
    for (let i = 0; i < n; i++) {
      let c = 0; for (let j = 0; j < m; j++) if (mem[j][i] > th) c++;
      p[i] = c / m; occ[i] = obs[i] > th ? 1 : 0;
    }
    return { p, occ };
  },
  brier(p, occ) { let s = 0; for (let i = 0; i < p.length; i++) s += Math.pow(p[i] - occ[i], 2); return s / p.length; },
  bins(p, occ) {
    const rows = [];
    for (let b = 0; b < 10; b++) {
      const lo = b / 10, hi = (b + 1) / 10;
      let c = 0, k = 0;
      for (let i = 0; i < p.length; i++) if (p[i] >= lo && (b === 9 ? p[i] <= hi : p[i] < hi)) { c++; k += occ[i]; }
      rows.push([lo + 0.05, c > 30 ? k / c : null, c]);
    }
    return rows;
  },
  all(api) {
    const q = api.p, sf = +q.sf.toFixed(2), bias = +q.bias.toFixed(1);
    const m = Math.round(q.m), th = +q.thresh.toFixed(2), sd = Math.round(q.seed);
    const key = [sf, bias, m, th, sd].join(",");
    if (this._a && this._a.key === key) return this._a.val;
    const e = this.make(sf, bias, m, sd);
    const ss = this.spreadSkill(e), cr = this.crps(e);
    const { p, occ } = this.probs(e, th);
    let base = 0; for (let i = 0; i < occ.length; i++) base += occ[i]; base /= occ.length;
    const bs = this.brier(p, occ), bclim = this.brier(new Float64Array(occ.length).fill(base), occ);
    const det = new Float64Array(occ.length);
    for (let i = 0; i < occ.length; i++) det[i] = p[i] > 0.5 ? 1 : 0;     // 确定性预报只能答是或否
    const bdet = this.brier(det, occ);
    let se = 0; for (let i = 0; i < e.n; i++) { let mu = 0; for (let j = 0; j < m; j++) mu += e.mem[j][i]; se += Math.pow(mu / m - e.obs[i], 2); }
    const val = { e, sf, bias, m, th, ss, cr, p, occ, rows: this.bins(p, occ), base,
                  bs, bclim, bdet, rmseDet: Math.sqrt(se / e.n) };
    this._a = { key, val };
    return val;
  },
  maxDev(rows) { let d = 0; for (const [c, f] of rows) if (f !== null && Math.abs(c - f) > d) d = Math.abs(c - f); return d; },

  reset(api, s) {},
  readouts(api, s) {
    const a = this.all(api);
    if (api.scene === "spread" && Math.abs(a.sf - 1) < 0.08 && Math.abs(a.bias) < 0.05 && a.m >= 40) api.done("cal");
    if (api.scene === "spread" && a.sf <= 0.55) api.done("narrow");
    if (api.scene === "spread" && a.sf >= 1.55) api.done("wide");
    if (api.scene === "spread" && a.m === 1) api.done("member");
    if (api.scene === "rel" && a.sf <= 0.55) api.done("diag");
    if (api.scene === "one") api.done("squash");
    if (api.scene === "one") {
      return [[["确定性预报的 RMSE", "RMSE of the deterministic forecast"], a.rmseDet.toFixed(4)],
              [["集合均值的 RMSE", "RMSE of the ensemble mean"], a.ss.rmse.toFixed(4)],
              [["集合给的概率，Brier 分数", "Brier score of the ensemble probability"], a.bs.toFixed(4)],
              [["只答是或否，Brier 分数", "Brier score of the yes/no answer"], a.bdet.toFixed(4)],
              [["每次都报气候概率，Brier 分数", "Brier score of climatology"], a.bclim.toFixed(4)],
              [["集合比只答是或否好多少", "how much better the ensemble is"],
               ((1 - a.bs / a.bdet) * 100).toFixed(1) + "%"]];
    }
    if (api.scene === "rel") {
      return [[["事件门限", "event threshold"], a.th.toFixed(2)],
              [["这个事件实际发生的比例", "how often the event actually happens"],
               (a.base * 100).toFixed(1) + "%"],
              [["离开 45° 线最远有多少", "largest departure from the 45° line"], this.maxDev(a.rows).toFixed(3)],
              [["Brier 分数（越小越好）", "Brier score (lower is better)"], a.bs.toFixed(4)],
              [["比气候概率好多少", "skill against climatology"], (1 - a.bs / a.bclim).toFixed(3)]];
    }
    return [[["集合的离散度", "ensemble spread"], a.ss.spread.toFixed(4)],
            [["集合均值的 RMSE", "RMSE of the ensemble mean"], a.ss.rmse.toFixed(4)],
            [["离散度 / 技巧比（该接近 1）", "spread / skill ratio (should be near 1)"],
             a.m === 1 ? "—" : a.ss.ratio.toFixed(3)],
            [["CRPS（越小越好）", "CRPS (lower is better)"], a.cr.toFixed(4)],
            [["成员只剩一个时它等于", "with one member it equals"],
             a.m === 1 ? api.T("平均绝对误差", "the mean absolute error") : "—"]];
  },

  draw(api, s) {
    const { w, h } = api, a = this.all(api);
    if (api.scene === "rel") {
      const g = api.graph({ x: 52, y: 22, w: Math.min(w * 0.46, h - 60), h: h - 64,
                            xmin: 0, xmax: 1, ymin: 0, ymax: 1,
                            xlabel: api.T("预报说的概率", "forecast probability"),
                            ylabel: api.T("实际发生的频率", "observed frequency") }).axes();
      g.seg(0, 0, 1, 1, api.css("--muted"), 1.5, [5, 5]);
      const pts = a.rows.filter((r) => r[1] !== null).map((r) => [r[0], r[1]]);
      g.pts(pts, api.css("--blue"), 2.2);
      g.dots(pts, api.css("--blue"), 4);
      g.text(api.T("线下方 = 说得太满", "below = claims too much"), 0.42, 0.18, api.css("--red"), 12);
      g.text(api.T("线上方 = 说得太保守", "above = too conservative"), 0.04, 0.88, api.css("--muted"), 12);
      // 右边：各档里有多少次预报
      const g2 = api.graph({ x: w * 0.62, y: 22, w: w * 0.34, h: h - 64, xmin: 0, xmax: 1,
                             ymin: 0, ymax: Math.max(10, Math.max.apply(null, a.rows.map((r) => r[2])) * 1.15),
                             xlabel: api.T("预报说的概率", "forecast probability"),
                             ylabel: api.T("这一档有多少次", "cases in this bin") }).axes();
      a.rows.forEach((r) => g2.seg(r[0], 0, r[0], r[2], api.css("--blue"), 7));
      return;
    }
    if (api.scene === "one") {
      const g = api.graph({ x: 52, y: 22, w: w * 0.44, h: h - 64, xmin: -4, xmax: 4,
                            ymin: 0, ymax: 1.05,
                            xlabel: api.T("明天的数值", "tomorrow's value"),
                            ylabel: api.T("集合给的分布", "the ensemble's distribution") }).axes();
      // 第一例：集合成员铺开的样子，与被压成的那一个数
      const col = [];
      for (let j = 0; j < a.m; j++) col.push(a.e.mem[j][0]);
      col.sort((x, y) => x - y);
      col.forEach((v, j) => g.seg(v, 0.08, v, 0.22, api.css("--blue"), 2));
      let mu = 0; for (const v of col) mu += v; mu /= col.length;
      g.vline(mu, api.css("--red"));
      g.vline(a.th, api.css("--green"));
      g.text(api.T("集合：一片可能", "the ensemble: a spread of possibilities"), -3.8, 0.33, api.css("--blue"), 12);
      g.text(api.T("压成一个数", "squashed into one number"), mu + 0.1, 0.62, api.css("--red"), 12);
      g.text(api.T("门限", "threshold"), a.th + 0.1, 0.9, api.css("--green"), 12);
      let above = 0; for (const v of col) if (v > a.th) above++;
      g.text(api.T(`集合能答：超过门限的概率 ${(above / col.length * 100).toFixed(0)}%`,
                   `the ensemble can answer: ${(above / col.length * 100).toFixed(0)}% chance of exceeding`),
             -3.8, 0.46, api.css("--ink"), 12);
      // 右边：三种做法的 Brier 分数
      const names = [api.T("集合概率", "ensemble"), api.T("只答是或否", "yes/no"), api.T("气候概率", "climatology")];
      const vals = [a.bs, a.bdet, a.bclim], cols = ["--blue", "--red", "--muted"];
      const top = Math.max.apply(null, vals) * 1.3;
      const g2 = api.graph({ x: w * 0.64, y: 22, w: w * 0.32, h: h - 64, xmin: -0.5, xmax: 2.5,
                             ymin: 0, ymax: top, ticks: false,
                             ylabel: api.T("Brier 分数（越小越好）", "Brier score (lower is better)") }).axes();
      vals.forEach((v, i) => {
        g2.seg(i, 0, i, v, api.css(cols[i]), 26);
        g2.text(v.toFixed(4), i, v + top * 0.06, api.css("--ink"), 12, "center");
        g2.text(names[i], i, -top * 0.06, api.css("--muted"), 12, "center");
      });
      return;
    }
    // spread 场景：CRPS 随离散度倍数怎么走，外加这一档在哪
    const g = api.graph({ x: 52, y: 22, w: w * 0.44, h: h - 64, xmin: 0.3, xmax: 2.0,
                          ymin: 0, ymax: 1.0,
                          xlabel: api.T("离散度倍数", "spread factor"),
                          ylabel: "CRPS" }).axes();
    const ckey = [a.bias, Math.min(a.m, 20), Math.round(api.p.seed)].join(",");
    if (!this._curve || this._curve.key !== ckey) {        // 这条曲线只随偏差、成员数、天气批次变
      const pts = [];
      for (let f = 0.3; f <= 2.001; f += 0.1) {
        const e = this.make(+f.toFixed(2), a.bias, Math.min(a.m, 20), Math.round(api.p.seed));
        pts.push([+f.toFixed(2), this.crps(e)]);
      }
      this._curve = { key: ckey, pts };
    }
    const curve = this._curve.pts;
    g.pts(curve, api.css("--blue"), 2.2);
    g.vline(1.0, api.css("--green"));
    g.point(a.sf, a.cr, api.css("--red"), api.T("这一档", "you are here"));
    g.text(api.T("太自信", "over-confident"), 0.34, 0.08, api.css("--muted"), 12);
    g.text(api.T("太含糊", "too vague"), 1.66, 0.08, api.css("--muted"), 12);
    // 右边：这一次的集合与实况
    const g2 = api.graph({ x: w * 0.64, y: 22, w: w * 0.32, h: h - 64, xmin: 0, xmax: 24,
                           ymin: -5, ymax: 5,
                           xlabel: api.T("第几次预报", "case number"),
                           ylabel: api.T("数值", "value") }).axes();
    for (let i = 0; i < 24; i++) {
      let lo = Infinity, hi = -Infinity;
      for (let j = 0; j < a.m; j++) { const v = a.e.mem[j][i]; if (v < lo) lo = v; if (v > hi) hi = v; }
      g2.seg(i + 0.5, lo, i + 0.5, hi, api.css("--blue"), 5);
      g2.dots([[i + 0.5, a.e.obs[i]]], api.css("--red"), 3);
    }
    g2.text(api.T("蓝条 = 集合铺开的范围，红点 = 实况",
                  "blue = the ensemble's range, red = what happened"), 0.5, 4.3, api.css("--ink"), 12);
  },
});
