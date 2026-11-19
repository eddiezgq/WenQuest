// 实验 23.3 规划权重的取舍（配 23.4 节）。
// 两个场景：
//   weight  ：拖跟车距离权重、车速权重、舒适权重与前车的激烈程度，看平均车距、通行效率、
//             急刹次数、最小安全间距被侵犯的次数一起怎么动；
//   latency ：在最好的权重上加时延，看“既不侵犯也不急刹”的权重区间怎样被压窄。
// 与 code/_ch23.py 是同一套算法（cost_planner、follow_sim 的口径）：代价三项、候选加速度 41 档、
// 最小安全间距 = 3.0 m + 0.6 s × 车速、减速度低于 −3.0 m/s² 记一次急刹、
// 流量 q = 3600·v /（车距 + 车长）。
WQ.lab({
  title: ["实验 23.3 跟得紧一点，通得多一点，然后呢",
          "Lab 23.3 Follow a little closer, carry a few more cars — and then?"],
  goal: ["先只拖跟车距离权重：往小拖（跟紧），流量上去了，可是最小安全间距被侵犯的次数也上去了；往大拖（跟远），侵犯归零，急刹却回升。你要自己把两件事找出来：**流量最高的那一档正是侵犯安全间距的那一档**，而**既不侵犯也不急刹的区间只有 0.20—0.57**——权重可以连续调，可用的那一段却窄得只有两三倍宽。再切到第二个场景，在这段区间上加时延，看它怎样再被压窄。做完要能回答：验收一个跟车策略，报表上至少要有哪四列。",
         "Start by dragging the gap weight alone: tighter following raises the flow but also the number of minimum-safe-gap violations, while looser following clears the violations and brings the hard braking back. Two things are yours to find: the highest-flow setting is exactly the one that violates the safe gap, and the band that neither violates nor brakes hard is only 0.20 to 0.57 wide. Then add latency on that band and watch it narrow. You should be able to name the four columns any acceptance report of a following policy needs."],
  scenes: [
    { id: "weight", name: ["调权重", "Tune the weights"],
      problem: { title: ["问题：按哪个指标调，调出来的车就是哪个脾气", "Problem: whichever metric you tune on is the character you get"],
                 text: ["规划器在若干候选加速度里挑代价最低的那一个，代价有三项：跟车距离偏离期望值、车速偏离巡航目标、舒适（加速度平方）。权重一改，车的脾气就改了。这个场景让你亲手调，并把四个指标并排放着看：平均车距、通行效率、急刹次数、**最小安全间距被侵犯的次数**。最后那一列是报表上最容易被漏掉的一列——而它正是前三列换来的东西。",
                        "The planner picks the cheapest of a set of candidate accelerations, with three cost terms: gap error, speed error and comfort. Change the weights and you change the vehicle's character. Four numbers sit side by side here: mean gap, traffic flow, hard-braking events and violations of the minimum safe gap. The last column is the one reports omit — and it is what the first three are bought with."] } },
    { id: "latency", name: ["加上时延", "Add the latency"],
      problem: { title: ["问题：同一套权重，反应慢一点还够用吗", "Problem: does the same tuning survive a slower loop?"],
                 text: ["真车上，规划器看到的是若干拍以前的车距与车速，踩下去的却是现在。时延把“可用的权重”这一段压窄：跟得越紧，被压得越狠。这个场景让你在同一套权重上把时延从 0 加到 400 ms，并把“既不侵犯也不急刹”的档数与 0 时延时的档数放在一起比。要带走的结论是：**调参的结论连着时延预算**，换一块算力更弱的板子，权重要重新定。",
                        "On a real car the planner sees a gap and a speed from several cycles ago but acts now. Latency narrows the band of usable weights, and the tighter you follow, the harder it bites. Raise the latency from 0 to 400 ms on one set of weights and compare the count of clean settings with the count at zero latency. The lesson: a tuning result is tied to a latency budget, so weaker hardware means retuning."] } },
  ],
  params: [
    { id: "wgap", name: ["跟车距离权重", "gap weight"], min: 0.02, max: 3.2, step: 0.01, value: 0.1, digits: 2 },
    { id: "wspeed", name: ["车速权重", "speed weight"], min: 0.2, max: 3, step: 0.1, value: 1, digits: 1 },
    { id: "waccel", name: ["舒适权重（加速度平方）", "comfort weight"], min: 0.1, max: 2, step: 0.1, value: 0.6, digits: 1 },
    { id: "aggr", name: ["前车刹车的激烈程度（倍）", "how hard the lead brakes"], min: 0.5, max: 1.8, step: 0.1, value: 1, digits: 1 },
    { id: "delay", name: ["感知到执行的时延（ms）", "sense-to-act latency (ms)"], min: 0, max: 400, step: 50, value: 100, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["通行效率（辆/小时）", "traffic flow (veh/h)"] },
           { color: "var(--red)", name: ["侵犯最小安全间距的次数", "minimum-safe-gap violations"] },
           { color: "var(--amber)", name: ["急刹次数", "hard-braking events"] },
           { color: "var(--green)", name: ["当前这一档", "where you are now"] },
           { color: "var(--muted)", name: ["既不侵犯也不急刹的区间", "the band that does neither"] }],
  tasks: [
    { id: "tight", text: ["把跟车距离权重拖到 0.02（跟得最紧）：流量是多少？侵犯最小安全间距几次？把这两个数记在一起。",
                          "Drag the gap weight to 0.02 (the tightest following): what is the flow, and how many times is the minimum safe gap violated? Record the two together."],
      demo: { scene: "weight", set: { wgap: 0.02, wspeed: 1, waccel: 0.6, aggr: 1, delay: 100 }, press: [] } },
    { id: "safe", text: ["拖到 0.20：侵犯次数变成多少？流量比 0.02 那一档少了百分之几？那点流量是用什么换的？",
                         "Now 0.20: what happens to the violations, and how much flow do you give up against 0.02? What was that flow bought with?"],
      demo: { scene: "weight", set: { wgap: 0.2, wspeed: 1, waccel: 0.6, aggr: 1, delay: 100 }, press: [] } },
    { id: "edge", text: ["拖到 0.57（区间的上沿）：侵犯与急刹都还是 0 吗？再往上一点点会先出哪一项？",
                         "Go to 0.57, the top of the band: are both counters still zero, and which one breaks first as you go further?"],
      demo: { scene: "weight", set: { wgap: 0.57, wspeed: 1, waccel: 0.6, aggr: 1, delay: 100 }, press: [] } },
    { id: "loose", text: ["拖到 3.2（跟得最远）：侵犯还是 0，急刹几次？为什么跟得越远反而越容易急刹？",
                          "Drag to 3.2 (the loosest): violations stay at zero, but how many hard brakes? Why does following further back bring the hard braking back?"],
      demo: { scene: "weight", set: { wgap: 3.2, wspeed: 1, waccel: 0.6, aggr: 1, delay: 100 }, press: [] } },
    { id: "latency", text: ["切到第二个场景，把时延拖到 400 ms：“既不侵犯也不急刹”的档数从 0 时延的几档变成了几档？再把前车激烈程度拖到 1.2，还剩几档？",
                            "In the second scene raise the latency to 400 ms: how many clean settings are left against the count at zero latency? Then set the lead aggressiveness to 1.2 — how many survive?"],
      demo: { scene: "latency", set: { delay: 400, aggr: 1.2, wgap: 0.2, wspeed: 1, waccel: 0.6 }, press: [] } },
  ],
  think: ["把你们自己的最小安全间距公式抄下来（按路面、能见度、制动能力定的那一条），代进这个实验，可用区间会变宽还是变窄？如果它比本实验的 3.0 m + 0.6 s × 车速更保守，那么你们现在调出来的权重还在区间里吗？写不出这条公式，就先别谈“调到最好”——**没有安全口径的调参，调的是报表不是车**。",
          "Write down your own minimum-safe-gap formula — the one that accounts for surface, visibility and braking capability — and substitute it here: does the usable band widen or narrow? If it is stricter than the 3.0 m + 0.6 s used here, is your current tuning still inside the band? Until that formula exists, tuning optimises the report rather than the vehicle."],

  N: 1600, DT: 0.05,
  VSET: 22, D0: 5, THW: 1.4, TSAFE: 0.6, DSAFE0: 3, AHARD: -3, AMIN: -6, AMAX: 2.5, LEN: 4.8,
  WS: [0.02, 0.035, 0.05, 0.07, 0.1, 0.14, 0.2, 0.28, 0.4, 0.57, 0.8, 1.13, 1.6, 2.26, 3.2],
  // 前车的刹车事件（起始时刻 s、持续 s、减速幅度 m/s）：写死的五次，便于你重复同一条工况
  BRAKES: [[9, 2.2, 8.6], [22, 1.4, 5.8], [36, 3.0, 10.3], [51, 1.8, 7.5], [66, 2.6, 9.2]],
  lead(aggr) {                                 // 前车车速：巡航 + 五次刹车（刹车是一切最坏情形的来源）
    const key = aggr.toFixed(2);
    if (this._l && this._l.key === key) return this._l.val;
    const n = this.N, v = new Array(n);
    for (let i = 0; i < n; i++) v[i] = this.VSET + 1.2 * Math.sin(2 * Math.PI * (i * this.DT) / 23 + 1.1);
    for (const [t0, durS, depth] of this.BRAKES) {
      const k = Math.round(t0 / this.DT), dur = Math.round(durS / this.DT);
      for (let i = 0; i < dur && k + i < n; i++) v[k + i] -= depth * aggr * Math.sin(Math.PI * i / dur);
    }
    const s = new Array(n);
    let acc = 40;
    for (let i = 0; i < n; i++) { v[i] = Math.max(v[i], 1); acc += v[i] * this.DT; s[i] = acc; }
    const val = { s, v };
    this._l = { key, val };
    return val;
  },
  plan(q, gap, vEgo, vLead) {                  // 代价函数式规划：41 档候选加速度里挑最便宜的
    const T = 2, gapDes = this.D0 + this.THW * vEgo;
    let best = 0, bestC = Infinity;
    for (let i = 0; i < 41; i++) {
      const a = this.AMIN + (this.AMAX - this.AMIN) * i / 40;
      const vNext = Math.max(vEgo + a * T, 0);
      const gapNext = gap + vLead * T - (vEgo + vNext) / 2 * T;
      let c = q.wgap * ((gapNext - gapDes) ** 2) + q.wspeed * ((vNext - this.VSET) ** 2)
            + q.waccel * (a ** 2) * T;
      if (gapNext < this.DSAFE0) c += 1e4;     // 撞上去的那一档总是最贵
      if (c < bestC) { bestC = c; best = a; }
    }
    return best;
  },
  sim(q, wgap, delaySteps, aggr) {
    const d = this.lead(aggr), n = this.N, w = { wgap, wspeed: q.wspeed, waccel: q.waccel };
    let sEgo = 0, vEgo = this.VSET, hard = 0, viol = 0, crash = 0, gapSum = 0, vSum = 0;
    let gapMin = Infinity;
    const gaps = [], hits = [], safes = [];
    const hg = [], hv = [], hl = [];
    for (let k = 0; k < n; k++) {
      const gap = d.s[k] - sEgo - this.LEN;
      hg.push(gap); hv.push(vEgo); hl.push(d.v[k]);
      const j = Math.max(0, k - delaySteps);   // 看到的是过去，踩下去的是现在
      let a = this.plan(w, hg[j], hv[j], hl[j]);
      a = Math.min(Math.max(a, this.AMIN), this.AMAX);
      vEgo = Math.max(0, vEgo + a * this.DT);
      sEgo += vEgo * this.DT;
      const safe = this.DSAFE0 + this.TSAFE * vEgo;
      if (a < this.AHARD) hard++;
      if (gap < safe) viol++;
      if (gap <= 0) crash++;
      gapSum += gap; vSum += vEgo; gapMin = Math.min(gapMin, gap);
      gaps.push(gap); safes.push(safe); hits.push(gap < safe);
    }
    const gapMean = gapSum / n, vMean = vSum / n;
    return { gapMean, gapMin, vMean, hard, viol, crash, gaps, safes, hits,
             flow: 3600 * vMean / (gapMean + this.LEN) };
  },
  steps(ms) { return Math.ceil(ms / 1000 / this.DT); },   // 不足一个周期也要占一个
  sweep(q, delaySteps, aggr) {
    const key = [q.wspeed, q.waccel, delaySteps, aggr].join("|");
    this._sw = this._sw || {};
    if (this._sw[key]) return this._sw[key];
    const rows = this.WS.map((w) => {
      const r = this.sim(q, w, delaySteps, aggr);
      return { w, flow: r.flow, viol: r.viol, hard: r.hard, gap: r.gapMean };
    });
    const safe = rows.filter((x) => x.viol === 0);
    const clean = safe.filter((x) => x.hard === 0);
    let bestAny = rows[0];
    for (const x of rows) if (x.flow > bestAny.flow) bestAny = x;
    let bestSafe = safe.length ? safe[0] : null;
    for (const x of safe) if (x.flow > bestSafe.flow) bestSafe = x;
    const res = { rows, safe, clean, bestAny, bestSafe,
                  cleanLo: clean.length ? Math.min(...clean.map((x) => x.w)) : null,
                  cleanHi: clean.length ? Math.max(...clean.map((x) => x.w)) : null,
                  safeLo: safe.length ? Math.min(...safe.map((x) => x.w)) : null };
    this._sw[key] = res;
    return res;
  },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p;
    const ms = api.scene === "latency" ? q.delay : 100;
    const dsteps = this.steps(ms);
    const sw = this.sweep(q, dsteps, q.aggr);
    const r = this.sim(q, q.wgap, dsteps, q.aggr);
    const band = sw.cleanLo === null ? api.T("没有一档干净的", "none")
                                     : `${sw.cleanLo.toFixed(2)}—${sw.cleanHi.toFixed(2)}`;
    if (api.scene === "weight") {
      if (q.wgap <= 0.03) api.done("tight");
      if (Math.abs(q.wgap - 0.2) <= 0.015) api.done("safe");
      if (Math.abs(q.wgap - 0.57) <= 0.02) api.done("edge");
      if (q.wgap >= 2.2) api.done("loose");
      return [[["平均车距", "mean gap"], r.gapMean.toFixed(2) + " m"],
              [["最小车距", "smallest gap"], r.gapMin.toFixed(2) + " m"],
              [["通行效率", "traffic flow"], r.flow.toFixed(0) + api.T(" 辆/小时", " veh/h")],
              [["急刹次数", "hard-braking events"], String(r.hard)],
              [["侵犯最小安全间距的次数", "minimum-safe-gap violations"], String(r.viol)],
              [["流量最高的那一档", "the highest-flow setting"],
               `w=${sw.bestAny.w.toFixed(3)}，${sw.bestAny.flow.toFixed(0)}` +
               api.T(` 辆/小时，侵犯 ${sw.bestAny.viol} 次`, ` veh/h, ${sw.bestAny.viol} violations`)],
              [["安全区间内流量最高的一档", "the highest-flow safe setting"],
               sw.bestSafe ? `w=${sw.bestSafe.w.toFixed(2)}，${sw.bestSafe.flow.toFixed(0)}` +
                 api.T(" 辆/小时", " veh/h") : api.T("没有", "none")],
              [["既不侵犯也不急刹的权重", "the band that does neither"], band]];
    }
    const sw0 = this.sweep(q, 0, q.aggr);
    if (q.delay >= 350 && q.aggr >= 1.15) api.done("latency");
    const band0 = sw0.cleanLo === null ? api.T("没有一档干净的", "none")
                                       : `${sw0.cleanLo.toFixed(2)}—${sw0.cleanHi.toFixed(2)}`;
    return [[["当前时延", "current latency"],
             ms.toFixed(0) + api.T(` ms（${dsteps} 拍）`, ` ms (${dsteps} cycles)`)],
            [["这一档的侵犯次数", "violations at this setting"], String(r.viol)],
            [["这一档的急刹次数", "hard brakes at this setting"], String(r.hard)],
            [["这一档的通行效率", "flow at this setting"], r.flow.toFixed(0) + api.T(" 辆/小时", " veh/h")],
            [["既不侵犯也不急刹的档数", "clean settings now"],
             `${sw.clean.length} / ${this.WS.length}`],
            [["0 时延时的档数", "clean settings at zero latency"],
             `${sw0.clean.length} / ${this.WS.length}`],
            [["现在的区间", "the band now"], band],
            [["0 时延的区间", "the band at zero latency"], band0]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p;
    const ms = api.scene === "latency" ? q.delay : 100;
    const dsteps = this.steps(ms);
    const r = this.sim(q, q.wgap, dsteps, q.aggr);
    const sw = this.sweep(q, dsteps, q.aggr);

    // 上图：这一档权重跑出来的车距，与最小安全间距
    const g = api.graph({ x: 56, y: 28, w: w - 108, h: (h - 96) * 0.52,
                          xmin: 0, xmax: this.N * this.DT, ymin: 0, ymax: 48,
                          xlabel: api.T("时间（s）", "time (s)"),
                          ylabel: api.T("车距（m）", "gap (m)") }).axes();
    const gp = [], sp = [];
    for (let i = 0; i < this.N; i += 2) {
      gp.push([i * this.DT, r.gaps[i]]);
      sp.push([i * this.DT, r.safes[i]]);
    }
    g.pts(gp, api.css("--ink"), 2.2);
    g.pts(sp, api.css("--red"), 1.8, [5, 4]);
    for (let i = 0; i < this.N; i += 2) {
      if (r.hits[i]) g.seg(i * this.DT, 0, i * this.DT, r.gaps[i], api.css("--red"), 1.5);
    }
    g.text(api.T("黑：车距　红虚线：最小安全间距　红竖线：被侵犯的那几拍",
                 "black: gap, red dashed: minimum safe gap, red bars: violated steps"),
           1, 45, api.css("--ink"), 12);

    // 下图：整条权重扫描（对数横轴），三条曲线各自归一化
    const lg = (x) => Math.log(x) / Math.LN10;
    const g2 = api.graph({ x: 56, y: 28 + (h - 96) * 0.62, w: w - 108, h: (h - 96) * 0.38,
                           xmin: lg(0.02), xmax: lg(3.2), ymin: 0, ymax: 1.12,
                           xlabel: api.T("跟车距离权重（对数横轴：−1.7 是 0.02，0.5 是 3.2）",
                                         "gap weight (log axis: -1.7 is 0.02, 0.5 is 3.2)"),
                           ylabel: api.T("归一化（流量÷2600，次数÷200）",
                                         "normalised (flow over 2600, counts over 200)") }).axes();
    g2.pts(sw.rows.map((x) => [lg(x.w), Math.min(1.1, x.flow / 2600)]), api.css("--blue"), 2.6);
    g2.pts(sw.rows.map((x) => [lg(x.w), Math.min(1.1, x.viol / 200)]), api.css("--red"), 2.4);
    g2.pts(sw.rows.map((x) => [lg(x.w), Math.min(1.1, x.hard / 200)]), api.css("--amber"), 2.4, [5, 4]);
    if (sw.cleanLo !== null) {
      g2.vline(lg(sw.cleanLo), api.css("--muted"));
      g2.vline(lg(sw.cleanHi), api.css("--muted"));
    }
    g2.vline(lg(q.wgap), api.css("--green"), []);
    g2.text(api.T("蓝：通行效率　红：侵犯次数　黄虚线：急刹次数　灰：可用区间两头　绿：当前这一档",
                  "blue: flow, red: violations, amber dashed: hard brakes, grey: band edges, green: you"),
            lg(0.021), 1.05, api.css("--ink"), 12);
  },
});
