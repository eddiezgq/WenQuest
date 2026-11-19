// 实验 22.1 申报偏置、分位数与偏差成本（配 22.1、22.2 节）。
// 两个场景：
//   bias     ：拖申报偏置与少发的罚金倍数，看偏差成本曲线与均方根误差曲线的最低点怎样分开；
//   quantile ：改用分位数申报（报第 q 分位而不是中位数），看覆盖率、缺口次数与成本一起怎么动。
// 与 code/_ch22.py 是同一套算法（tou_price、imbalance_cost 的口径）。
WQ.lab({
  title: ["实验 22.1 同样的预测，报多少才最省",
          "Lab 22.1 Same forecast: how much should you declare?"],
  goal: ["先把申报偏置从 +40 拖到 −120，盯住两条曲线：均方根误差的最低点一直钉在 0 附近，偏差成本的最低点却跑到左边去了。再把少发的罚金从 1.2 倍拖到 4 倍，看最优偏置继续往左走——模型一个字没改，该报多少却变了。第二个场景把“报哪个分位数”直接交给你：报得越低，缺口越少、成本越低，但贱卖的电越多，到某一档就不划算了。做完要能回答：你们的结算规则下，该报第几分位。",
         "First drag the declaration bias from +40 to −120 and watch two curves: the RMSE optimum stays near zero while the cost optimum walks to the left. Then raise the shortfall penalty from 1.2× to 4× and watch it walk further. The model never changed; what you should declare did. The second scene hands you the quantile directly: declare lower and you have fewer shortfalls and a lower bill, until the power you dump at the cheap price outweighs it. You should be able to say which quantile fits your own settlement rules."],
  scenes: [
    { id: "bias", name: ["申报偏置", "Declaration bias"],
      problem: { title: ["问题：最准的申报是不是最省的申报", "Problem: is the truest declaration the cheapest one?"],
                 text: ["发电计划要提前申报，实际与申报不符就要结算，而**两个方向的价钱不一样**：少发了要按高价买电补上，多发了只能贱卖。于是“把预测原样报上去”未必最省。这个场景让你亲手拖申报偏置，把偏差成本与均方根误差两条曲线放在一起看——它们的最低点不在同一处。",
                        "Generation has to be declared ahead of time and settled against what actually happened, and the two directions carry different prices: a shortfall is bought back dear, a surplus is sold cheap. Declaring the raw forecast is therefore not usually the cheapest thing to do. Drag the bias here and watch the cost curve and the RMSE curve bottom out in different places."] } },
    { id: "quantile", name: ["报哪个分位数", "Which quantile to declare"],
      problem: { title: ["问题：调度要的不是“最可能”，是“有多大把握不低于”", "Problem: dispatch needs a guarantee, not a best guess"],
                 text: ["点预测回答的是“最可能是多少”，调度问的却是“有多大把握不低于多少”。后者要分位数。这个场景把申报改成“报第 q 分位”：q 越低，实际低于申报的次数越少（缺口越少），但平白贱卖的电越多。你要找的是**这套电价规则下**那个最省的 q。",
                        "A point forecast answers 'what is most likely'; dispatch asks 'what can you guarantee'. That calls for quantiles. Here the declaration is the q-th quantile: the lower q is, the fewer shortfalls, but the more power is dumped at the cheap price. Find the q that is cheapest under these rules."] } },
  ],
  params: [
    { id: "bias", name: ["申报偏置（kW，负号 = 往低报）", "declaration bias (kW)"], min: -150, max: 40, step: 5, value: 0, digits: 0 },
    { id: "up", name: ["少发的罚金（倍电价）", "shortfall penalty (× price)"], min: 1, max: 4, step: 0.1, value: 1.6, digits: 1 },
    { id: "down", name: ["多发的贱卖价（倍电价）", "surplus price (× price)"], min: 0.1, max: 1, step: 0.05, value: 0.5, digits: 2 },
    { id: "sigma", name: ["预测误差大小（kW）", "forecast error size (kW)"], min: 5, max: 80, step: 5, value: 35, digits: 0 },
    { id: "q", name: ["报第几分位（%）", "quantile declared (%)"], min: 5, max: 95, step: 5, value: 50, digits: 0 },
  ],
  legend: [{ color: "var(--red)", name: ["偏差成本", "imbalance cost"] },
           { color: "var(--blue)", name: ["均方根误差", "RMSE"] },
           { color: "var(--green)", name: ["当前这一档", "where you are now"] },
           { color: "var(--muted)", name: ["成本最低的那一档", "the cheapest setting"] }],
  tasks: [
    { id: "base", text: ["罚金 1.6 倍、误差 35 kW：把申报偏置拖到 −60，记下偏差成本与均方根误差；再拖回 0，两个数各变成多少？",
                         "At a 1.6× penalty and 35 kW error, drag the bias to −60 and record the cost and the RMSE; then return to 0 and record both again."],
      demo: { scene: "bias", set: { bias: -60, up: 1.6, sigma: 35 }, press: [] } },
    { id: "heavy", text: ["把少发的罚金拖到 4 倍：读数里“成本最低的偏置”移到哪了？比 1.6 倍时左移了多少？",
                          "Raise the shortfall penalty to 4×: where does the cost-optimal bias go, and how far left of its 1.6× position is it?"],
      demo: { scene: "bias", set: { up: 4, sigma: 35, bias: 0 }, press: [] } },
    { id: "noisy", text: ["罚金回到 1.6 倍，把预测误差从 35 kW 拖到 80 kW：最优偏置变大还是变小？为什么预测越差越要保守？",
                          "Back at 1.6×, raise the forecast error from 35 kW to 80 kW: does the optimal bias grow or shrink, and why does a worse forecast call for more caution?"],
      demo: { scene: "bias", set: { up: 1.6, sigma: 80, bias: 0 }, press: [] } },
    { id: "quant", text: ["切到第二个场景，把分位数从 50% 拖到 10%：缺口比例降到多少？总成本降了还是升了？",
                          "In the second scene drag the quantile from 50% down to 10%: what happens to the share of shortfall steps, and to the bill?"],
      demo: { scene: "quantile", set: { q: 10, up: 1.6, down: 0.5, sigma: 35 }, press: [] } },
    { id: "toolow", text: ["继续拖到 5%，再把贱卖价拖到 1.0 倍（多发不吃亏）：最省的分位数往哪边动？这说明最优分位数由什么决定？",
                           "Go to 5% and then raise the surplus price to 1.0× (no loss on surplus): which way does the cheapest quantile move, and what decides it?"],
      demo: { scene: "quantile", set: { q: 5, down: 1.0, up: 1.6, sigma: 35 }, press: [] } },
  ],
  think: ["把你们合同里“少发怎么算、多发怎么算”两条抄下来，换算成这里的两个倍数，再回到实验里找最优偏置与最优分位数。如果这两条写得含糊，那么“预测要多准”这个问题本来就没有答案——先去把规则问清楚。",
          "Copy the two settlement clauses from your own contract, convert them into these two multipliers, and find the optimum here. If the clauses are vague, then 'how accurate must the forecast be' has no answer yet — go and pin the rules down first."],

  N: 96 * 10,
  rng(seed) { let x = (seed * 1103515245 + 12345) >>> 0; return () => { x = (x * 1103515245 + 12345) >>> 0; return x / 4294967296; }; },
  gauss(r) { const u = Math.max(r(), 1e-9), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  data(sigma) {
    const key = String(sigma);
    if (this._d && this._d.key === key) return this._d.val;
    const r = this.rng(11), truth = [], fc = [], price = [];
    for (let i = 0; i < this.N; i++) {
      const h = (i % 96) / 96 * 24;
      let cs = 0;
      if (h >= 6 && h <= 18) cs = 400 * Math.cos((h - 12) / 6 * Math.PI / 2);
      cs = Math.max(cs, 0);
      const cloud = 0.55 + 0.45 * Math.sin(i / 37 + Math.sin(i / 11) * 1.3);
      const tv = Math.max(cs * Math.min(1, Math.max(0.15, cloud)), 0);
      truth.push(tv);
      fc.push(Math.max(tv + sigma * this.gauss(r), 0));
      let p = 0.62;
      if (h >= 8 && h < 11) p = 1.05;
      if (h >= 18 && h < 21) p = 1.05;
      if (h < 7 || h >= 23) p = 0.28;
      price.push(p);
    }
    const val = { truth, fc, price };
    this._d = { key, val };
    return val;
  },
  cost(truth, declared, price, up, down) {
    let c = 0;
    for (let i = 0; i < truth.length; i++) {
      const d = truth[i] - declared[i];
      c += (d < 0 ? -d * price[i] * up : d * price[i] * down) * 0.25;
    }
    return c;
  },
  rmse(truth, declared) {
    let s = 0;
    for (let i = 0; i < truth.length; i++) s += (declared[i] - truth[i]) ** 2;
    return Math.sqrt(s / truth.length);
  },
  shift(fc, b) { return fc.map((x) => Math.max(x + b, 0)); },
  zq(q) {                                   // 正态分位数（有理近似，够画图用）
    const p = Math.min(Math.max(q, 0.001), 0.999);
    const t = Math.sqrt(-2 * Math.log(p < 0.5 ? p : 1 - p));
    const z = t - (2.30753 + 0.27061 * t) / (1 + 0.99229 * t + 0.04481 * t * t);
    return p < 0.5 ? -z : z;
  },
  sweepBias(d, up, down) {
    let best = 0, bestC = Infinity, bestR = 0, bestRv = Infinity;
    const pts = [];
    for (let b = -150; b <= 40.001; b += 5) {
      const dec = this.shift(d.fc, b);
      const c = this.cost(d.truth, dec, d.price, up, down);
      const r = this.rmse(d.truth, dec);
      pts.push([b, c, r]);
      if (c < bestC) { bestC = c; best = b; }
      if (r < bestRv) { bestRv = r; bestR = b; }
    }
    return { pts, best, bestC, bestR, bestRv };
  },
  sweepQ(d, sigma, up, down) {
    let best = 50, bestC = Infinity;
    const pts = [];
    for (let q = 5; q <= 95.001; q += 5) {
      const dec = this.shift(d.fc, sigma * this.zq(q / 100));
      const c = this.cost(d.truth, dec, d.price, up, down);
      pts.push([q, c]);
      if (c < bestC) { bestC = c; best = q; }
    }
    return { pts, best, bestC };
  },
  shortShare(truth, declared) {
    let n = 0;
    for (let i = 0; i < truth.length; i++) if (truth[i] < declared[i] - 1e-9) n++;
    return n / truth.length * 100;
  },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p, d = this.data(Math.round(q.sigma));
    if (api.scene === "bias") {
      const sw = this.sweepBias(d, q.up, q.down);
      const dec = this.shift(d.fc, q.bias);
      if (Math.abs(q.bias + 60) < 2.5) api.done("base");
      if (q.up >= 3.9) api.done("heavy");
      if (q.sigma >= 75) api.done("noisy");
      return [[["当前偏置", "current bias"], q.bias.toFixed(0) + " kW"],
              [["偏差成本", "imbalance cost"], this.cost(d.truth, dec, d.price, q.up, q.down).toFixed(0) + api.T(" 元", " CNY")],
              [["均方根误差", "RMSE"], this.rmse(d.truth, dec).toFixed(1) + " kW"],
              [["缺口时段占比", "share of shortfall steps"], this.shortShare(d.truth, dec).toFixed(1) + "%"],
              [["成本最低的偏置", "cost-optimal bias"], sw.best.toFixed(0) + " kW"],
              [["误差最低的偏置", "RMSE-optimal bias"], sw.bestR.toFixed(0) + " kW"],
              [["照成本调能省", "saving by tuning on cost"],
               ((1 - sw.bestC / this.cost(d.truth, this.shift(d.fc, sw.bestR), d.price, q.up, q.down)) * 100).toFixed(1) + "%"]];
    }
    const sw = this.sweepQ(d, Math.round(q.sigma), q.up, q.down);
    const dec = this.shift(d.fc, q.sigma * this.zq(q.q / 100));
    if (q.q <= 12) api.done("quant");
    if (q.q <= 10 && q.down >= 0.95) api.done("toolow");
    return [[["报第几分位", "quantile declared"], q.q.toFixed(0) + "%"],
            [["申报比点预测低", "below the point forecast by"],
             (-q.sigma * this.zq(q.q / 100)).toFixed(0) + " kW"],
            [["总成本", "total cost"], this.cost(d.truth, dec, d.price, q.up, q.down).toFixed(0) + api.T(" 元", " CNY")],
            [["缺口时段占比", "share of shortfall steps"], this.shortShare(d.truth, dec).toFixed(1) + "%"],
            [["最省的分位数", "cheapest quantile"], sw.best.toFixed(0) + "%"],
            [["那时的成本", "cost there"], sw.bestC.toFixed(0) + api.T(" 元", " CNY")]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p, d = this.data(Math.round(q.sigma));
    const dec = api.scene === "bias" ? this.shift(d.fc, q.bias)
                                     : this.shift(d.fc, q.sigma * this.zq(q.q / 100));
    // 上图：一天的实际出力与申报曲线
    const g = api.graph({ x: 52, y: 28, w: w - 104, h: (h - 96) * 0.5,
                          xmin: 0, xmax: 24, ymin: -20, ymax: 460,
                          xlabel: api.T("时间（小时）", "time of day (h)"),
                          ylabel: api.T("功率（kW）", "power (kW)") }).axes();
    const day = 3, t0 = day * 96;
    const tr = [], de = [];
    for (let i = 0; i < 96; i++) { tr.push([i / 4, d.truth[t0 + i]]); de.push([i / 4, dec[t0 + i]]); }
    g.pts(tr, api.css("--ink"), 2.4);
    g.pts(de, api.css("--red"), 2.2, [5, 4]);
    for (let i = 0; i < 96; i++) {
      if (d.truth[t0 + i] < dec[t0 + i] - 1e-9) {
        g.seg(i / 4, d.truth[t0 + i], i / 4, dec[t0 + i], api.css("--red"), 2);
      }
    }
    g.text(api.T("黑：实际出力　红虚线：申报　红竖线：缺口",
                 "black: actual, red dashed: declared, red bars: shortfall"),
           0.4, 440, api.css("--ink"), 12);

    // 下图：扫描曲线
    const g2 = api.graph({ x: 52, y: 28 + (h - 96) * 0.6, w: w - 104, h: (h - 96) * 0.4,
                           xmin: api.scene === "bias" ? -150 : 5,
                           xmax: api.scene === "bias" ? 40 : 95,
                           ymin: 0, ymax: 1.1,
                           xlabel: api.scene === "bias" ? api.T("申报偏置（kW）", "declaration bias (kW)")
                                                        : api.T("报第几分位（%）", "quantile declared (%)"),
                           ylabel: api.T("归一化（各自除以自己的最小值）", "normalised to its own minimum") }).axes();
    if (api.scene === "bias") {
      const sw = this.sweepBias(d, q.up, q.down);
      let mc = Infinity, mr = Infinity;
      for (const p of sw.pts) { mc = Math.min(mc, p[1]); mr = Math.min(mr, p[2]); }
      g2.pts(sw.pts.map((p) => [p[0], Math.min(1.08, p[1] / mc / 2.2)]), api.css("--red"), 2.6);
      g2.pts(sw.pts.map((p) => [p[0], Math.min(1.08, p[2] / mr / 2.2)]), api.css("--blue"), 2.2, [5, 4]);
      g2.vline(q.bias, api.css("--green"));
      g2.vline(sw.best, api.css("--muted"));
      g2.text(api.T("红：成本　蓝虚线：均方根误差　灰：成本最低处",
                    "red: cost, blue dashed: RMSE, grey: cost optimum"),
              -148, 1.02, api.css("--ink"), 12);
    } else {
      const sw = this.sweepQ(d, Math.round(q.sigma), q.up, q.down);
      let mc = Infinity;
      for (const p of sw.pts) mc = Math.min(mc, p[1]);
      g2.pts(sw.pts.map((p) => [p[0], Math.min(1.08, p[1] / mc / 2.2)]), api.css("--red"), 2.6);
      g2.vline(q.q, api.css("--green"));
      g2.vline(sw.best, api.css("--muted"));
      g2.text(api.T("红：总成本　灰：最省的那一档", "red: total cost, grey: the cheapest quantile"),
              6, 1.02, api.css("--ink"), 12);
    }
  },
});
