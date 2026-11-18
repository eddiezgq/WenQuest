// 实验 21.5 控制图能抓什么、抓不到什么（配 21.5 节）。
// 两个场景：
//   chart ：一张均值图 + 极差图，注入三种异常（均值漂移、方差变大、周期性），看各要多久才报警；
//   both  ：把同一段数据交给“控制图”和一个简单的机器学习报警器（多变量距离），比它们各抓到什么。
// 与 code/_ch21.py 是同一套算法（run_chart、xbar_limits、alarms）。
WQ.lab({
  title: ["实验 21.5 控制限不是规格限，控制图不是万能的",
          "Lab 21.5 Control limits are not spec limits, and the chart is not all-seeing"],
  goal: ["先亲手把控制限和规格限放在一张图上，确认一件事：两者没有任何数学关系，一个管“过程有没有变”，一个管“做得出合格品吗”。再往过程里注入三种异常——均值漂移、方差变大、周期性波动——看均值图各要多久才报警，以及哪一种它根本抓不到。最后把同一段数据交给一个简单的机器学习报警器，看它多抓到了什么、又多报了多少。做完要能说出：什么时候该加模型，什么时候老老实实用控制图。",
         "Put the control limits and the specification limits on one chart and confirm that they have no mathematical relationship: one watches whether the process changed, the other whether the part is good. Then inject three kinds of upset — a mean shift, a variance increase and a periodic wobble — and see how long the mean chart takes to react, and which one it misses entirely. Finally hand the same data to a simple machine-learning alarm and compare what it catches and what it over-reports."],
  scenes: [
    { id: "chart", name: ["控制图抓什么", "What the chart catches"],
      problem: { title: ["问题：报警了，是坏了吗", "Problem: an alarm fired — is anything bad?"],
                 text: ["休哈特控制图的控制限是**从过程自己的波动算出来的**（常用子组均值 ± A₂·R̄），规格限是**图纸给的**。两者宽窄没有固定关系：能力很差的过程可以完全“受控”（一个警报不报），能力很好的过程也可以天天报警。这个场景让你注入异常，量一量“平均要多少个子组才发现”。",
                        "The limits on a Shewhart chart are computed from the process's own variation; the specification limits come from the drawing. There is no fixed relationship between the two: a process with poor capability can be perfectly in control, and a highly capable one can alarm every day. Inject upsets here and measure how many subgroups it takes to notice."] } },
    { id: "both", name: ["控制图对机器学习报警", "Chart versus a learned alarm"],
      problem: { title: ["问题：加个模型能多抓到什么", "Problem: what does a model add"],
                 text: ["机器学习报警器在这里是最朴素的一种：用稳定期的数据算出每个变量的均值与标准差，再看新来的子组离中心有多远（多变量距离）。它的长处是**同时看好几个量**，所以方差变大与周期波动这类“均值没动”的异常也能抓；短处是**它不知道什么叫异常**，稳定期挑得不好，它就会把正常波动当异常。两者一起用才是车间里的常态。",
                        "The learned alarm here is the simplest kind: estimate each variable's mean and standard deviation during a stable window, then measure how far each new subgroup sits from the centre. Its strength is watching several quantities at once, so it reacts to upsets where the mean does not move; its weakness is that it has no idea what 'abnormal' means, so a badly chosen stable window makes it cry wolf."] } },
  ],
  params: [
    { id: "kind", name: ["注入哪种异常：0 无，1 均值漂移，2 方差变大，3 周期波动", "upset: 0 none, 1 mean shift, 2 variance, 3 periodic"], min: 0, max: 3, step: 1, value: 1, digits: 0 },
    { id: "size", name: ["异常的大小", "size of the upset"], min: 0, max: 3, step: 0.1, value: 1, digits: 1 },
    { id: "nsub", name: ["子组大小", "subgroup size"], min: 2, max: 6, step: 1, value: 5, digits: 0 },
    { id: "base", name: ["用前多少个子组定控制限", "subgroups used to set the limits"], min: 20, max: 120, step: 5, value: 50, digits: 0 },
    { id: "spec", name: ["规格限（±）", "specification limit (±)"], min: 1, max: 6, step: 0.5, value: 3, digits: 1 },
    { id: "seed", name: ["第几次重复", "repeat"], min: 0, max: 9, step: 1, value: 0, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["子组均值", "subgroup means"] },
           { color: "var(--red)", name: ["控制限（过程算出来的）", "control limits (from the process)"] },
           { color: "var(--muted)", name: ["规格限（图纸给的）", "spec limits (from the drawing)"] },
           { color: "var(--green)", name: ["报警的子组", "alarms"] }],
  tasks: [
    { id: "limits", text: ["异常选 0（什么都不注入）：控制限有多宽？规格限 ±3 有多宽？两者的比值是多少？再把规格限拖到 ±1.5，控制限变了吗？",
                           "With no upset, how wide are the control limits versus the ±3 spec limits? Drag the spec limit to ±1.5 — do the control limits move?"],
      demo: { scene: "chart", set: { kind: 0, spec: 3 }, press: [] } },
    { id: "shift", text: ["注入均值漂移，大小 1.0：平均要多少个子组才报警？再调到 2.0 看一遍。",
                          "Inject a mean shift of 1.0: how many subgroups until the alarm? Then try 2.0."],
      demo: { scene: "chart", set: { kind: 1, size: 1 }, press: [] } },
    { id: "spread", text: ["换成方差变大、大小 1.0（即方差变 2 倍）：均值图要多久才报警？与同样大小的均值漂移比，差几倍？",
                           "Switch to a variance increase of the same size: how much slower is the mean chart?"],
      demo: { scene: "chart", set: { kind: 2, size: 1 }, press: [] } },
    { id: "period", text: ["换成周期波动：均值图抓得到吗？把“用前多少个子组定控制限”从 50 拖到 120，结论变了吗？",
                           "Switch to the periodic upset: does the mean chart see it at all? Does widening the baseline change your answer?"],
      demo: { scene: "chart", set: { kind: 3, size: 1.5 }, press: [] } },
    { id: "ml", text: ["切到第二个场景，三种异常各走一遍：哪几种是机器学习报警器先发现的？它的误报比控制图多多少？",
                       "In the second scene run all three upsets: which does the learned alarm catch first, and how many more false alarms does it raise?"],
      demo: { scene: "both", set: { kind: 2, size: 1 }, press: [] } },
  ],
  think: ["控制图有一条好处是机器学习报警器没有的：**报警之后你知道该去查什么**（均值跑了、还是波动大了）。请想一想，要让模型也具备这条好处，报警信息里至少要带上什么？再想一步：如果稳定期那 50 个子组本身就带着一个没被发现的异常，两种办法各会出什么错？",
          "A control chart tells you what to go and look at — the mean moved, or the spread grew. What would a learned alarm have to report to be equally actionable? And if the 'stable' baseline itself contained an undetected upset, how would each approach fail?"],

  NG: 160,
  A2: { 2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483 },
  D4: { 2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004 },
  D2: { 2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534 },
  SHIFT_AT: 70,

  rng(seed) { let x = (seed * 1103515245 + 12345) >>> 0; return () => { x = (x * 1103515245 + 12345) >>> 0; return x / 4294967296; }; },
  gauss(r) { const u = Math.max(r(), 1e-9), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  data(kind, size, nsub, seed) {
    const key = [kind, size, nsub, seed].join(",");
    if (this._d && this._d.key === key) return this._d.val;
    const r = this.rng(seed * 101 + 7), out = [];
    for (let i = 0; i < this.NG; i++) {
      const on = i >= this.SHIFT_AT;
      let mu = 0, sd = 1;
      if (on && kind === 1) mu = size;
      if (on && kind === 2) sd = 1 + size;
      if (on && kind === 3) mu = size * Math.sin(i / 4);
      const row = [];
      for (let k = 0; k < nsub; k++) row.push(mu + sd * this.gauss(r));
      out.push(row);
    }
    this._d = { key, val: out };
    return out;
  },
  limits(groups, nsub, base) {
    let sm = 0, sr = 0;
    for (let i = 0; i < base; i++) {
      const g = groups[i];
      sm += g.reduce((a, b) => a + b, 0) / nsub;
      sr += Math.max(...g) - Math.min(...g);
    }
    const xbb = sm / base, rb = sr / base;
    return { center: xbb, ucl: xbb + this.A2[nsub] * rb, lcl: xbb - this.A2[nsub] * rb,
             rbar: rb, rucl: this.D4[nsub] * rb, sigma: rb / this.D2[nsub] };
  },
  chartAlarms(groups, lim, nsub) {
    return groups.map((g) => {
      const m = g.reduce((a, b) => a + b, 0) / nsub;
      const rg = Math.max(...g) - Math.min(...g);
      return (m > lim.ucl || m < lim.lcl) ? 1 : (rg > lim.rucl ? 2 : 0);   // 1 均值图，2 极差图
    });
  },
  mlAlarms(groups, nsub, base) {
    // 最朴素的学习式报警：用稳定期估每个特征的均值与标准差，再看新子组的距离
    const feats = groups.map((g) => {
      const m = g.reduce((a, b) => a + b, 0) / nsub;
      const sd = Math.sqrt(g.reduce((a, b) => a + (b - m) * (b - m), 0) / nsub);
      return [m, sd, Math.max(...g) - Math.min(...g)];
    });
    const mu = [0, 0, 0], sg = [0, 0, 0];
    for (let j = 0; j < 3; j++) {
      for (let i = 0; i < base; i++) mu[j] += feats[i][j] / base;
      for (let i = 0; i < base; i++) sg[j] += (feats[i][j] - mu[j]) ** 2 / base;
      sg[j] = Math.sqrt(sg[j]) + 1e-9;
    }
    const d = feats.map((f) => Math.sqrt(f.reduce((a, x, j) => a + ((x - mu[j]) / sg[j]) ** 2, 0)));
    // 阈值取稳定期的 99 分位，和控制图的“三倍标准差”同一个意思
    const ref = d.slice(0, base).slice().sort((a, b) => a - b);
    const thr = ref[Math.min(ref.length - 1, Math.floor(ref.length * 0.99))] * 1.05;
    return { d, thr, alarm: d.map((x) => (x > thr ? 1 : 0)) };
  },
  firstAfter(flags, from) {
    for (let i = from; i < flags.length; i++) if (flags[i]) return i - from + 1;
    return null;
  },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p, nsub = Math.round(q.nsub), base = Math.round(q.base);
    const kind = Math.round(q.kind), seed = Math.round(q.seed);
    const groups = this.data(kind, q.size, nsub, seed);
    const lim = this.limits(groups, nsub, base);
    const ca = this.chartAlarms(groups, lim, nsub);
    const ml = this.mlAlarms(groups, nsub, base);
    const meanFirst = this.firstAfter(ca.map((x) => (x === 1 ? 1 : 0)), this.SHIFT_AT);
    const rangeFirst = this.firstAfter(ca.map((x) => (x === 2 ? 1 : 0)), this.SHIFT_AT);
    const mlFirst = this.firstAfter(ml.alarm, this.SHIFT_AT);
    let falseChart = 0, falseMl = 0;
    for (let i = base; i < this.SHIFT_AT; i++) { if (ca[i]) falseChart++; if (ml.alarm[i]) falseMl++; }
    const name = ["没注入异常", "均值漂移", "方差变大", "周期波动"][kind];
    if (kind === 0) api.done("limits");
    if (kind === 1) api.done("shift");
    if (kind === 2) { api.done("spread"); if (api.scene === "both") api.done("ml"); }
    if (kind === 3) api.done("period");
    const rows = [[["注入的异常", "upset"], api.T(name, ["none", "mean shift", "variance", "periodic"][kind])],
                  [["控制限", "control limits"], `${lim.lcl.toFixed(2)} … ${lim.ucl.toFixed(2)}`],
                  [["规格限", "spec limits"], `${(-q.spec).toFixed(1)} … ${q.spec.toFixed(1)}`],
                  [["规格限比控制限宽", "spec ÷ control width"],
                   (2 * q.spec / (lim.ucl - lim.lcl)).toFixed(2) + api.T(" 倍", "×")],
                  [["过程能力 Cp（按极差估的 σ）", "Cp from the range estimate"],
                   (2 * q.spec / (6 * lim.sigma)).toFixed(2)],
                  [["均值图多久报警", "mean chart: subgroups to alarm"],
                   meanFirst === null ? api.T("一直没报", "never") : String(meanFirst)],
                  [["极差图多久报警", "range chart: subgroups to alarm"],
                   rangeFirst === null ? api.T("一直没报", "never") : String(rangeFirst)]];
    if (api.scene === "both") {
      rows.push([["学习式报警多久报警", "learned alarm: subgroups to alarm"],
                 mlFirst === null ? api.T("一直没报", "never") : String(mlFirst)]);
      rows.push([["稳定期里的误报（控制图 / 学习式）", "false alarms in the stable window"],
                 `${falseChart} / ${falseMl}`]);
    }
    return rows;
  },

  draw(api, s) {
    const { w, h } = api, q = api.p, nsub = Math.round(q.nsub), base = Math.round(q.base);
    const groups = this.data(Math.round(q.kind), q.size, nsub, Math.round(q.seed));
    const lim = this.limits(groups, nsub, base);
    const means = groups.map((g) => g.reduce((a, b) => a + b, 0) / nsub);
    const ca = this.chartAlarms(groups, lim, nsub);
    const span = Math.max(q.spec * 1.2, Math.abs(lim.ucl) * 1.6, ...means.map(Math.abs)) * 1.05;

    const g = api.graph({ x: 52, y: 26, w: w - 104, h: (h - 96) * 0.56,
                          xmin: 0, xmax: this.NG, ymin: -span, ymax: span,
                          xlabel: api.T("第几个子组", "subgroup"),
                          ylabel: api.T("子组均值", "subgroup mean") }).axes();
    g.pts(means.map((m, i) => [i, m]), api.css("--blue"), 1.6);
    for (let i = 0; i < this.NG; i++) if (ca[i] === 1) g.point(i, means[i], api.css("--green"));
    g.hline(lim.center, api.css("--ink"));
    g.hline(lim.ucl, api.css("--red"));
    g.hline(lim.lcl, api.css("--red"));
    g.hline(q.spec, api.css("--muted"));
    g.hline(-q.spec, api.css("--muted"));
    g.vline(this.SHIFT_AT, api.css("--green"));
    g.text(api.T("← 这里开始注入异常", "upset starts here"), this.SHIFT_AT + 2, span * 0.82,
           api.css("--green"), 12);
    g.text(api.T("红：控制限（过程算的）　灰：规格限（图纸给的）",
                 "red: control limits; grey: spec limits"),
           2, -span * 0.9, api.css("--ink"), 12);

    const g2 = api.graph({ x: 52, y: 26 + (h - 96) * 0.63, w: w - 104, h: (h - 96) * 0.37,
                           xmin: 0, xmax: this.NG, ymin: 0,
                           ymax: Math.max(lim.rucl * 1.3, 1),
                           xlabel: api.T("第几个子组", "subgroup"),
                           ylabel: api.scene === "both" ? api.T("学习式报警的距离", "distance")
                                                        : api.T("子组极差", "subgroup range") }).axes();
    if (api.scene === "both") {
      const ml = this.mlAlarms(groups, nsub, base);
      const top = Math.max(...ml.d) * 1.1;
      const g3 = api.graph({ x: 52, y: 26 + (h - 96) * 0.63, w: w - 104, h: (h - 96) * 0.37,
                             xmin: 0, xmax: this.NG, ymin: 0, ymax: top,
                             xlabel: api.T("第几个子组", "subgroup"),
                             ylabel: api.T("离中心有多远", "distance from the centre") }).axes();
      g3.pts(ml.d.map((x, i) => [i, x]), api.css("--red"), 1.8);
      g3.hline(ml.thr, api.css("--muted"));
      g3.vline(this.SHIFT_AT, api.css("--green"));
      g3.text(api.T("灰线 = 稳定期的 99 分位（与三倍标准差同一个意思）",
                    "grey: 99th percentile of the stable window"),
              2, top * 0.9, api.css("--muted"), 11);
    } else {
      const ranges = groups.map((gg) => Math.max(...gg) - Math.min(...gg));
      g2.pts(ranges.map((x, i) => [i, x]), api.css("--blue"), 1.6);
      g2.hline(lim.rucl, api.css("--red"));
      g2.hline(lim.rbar, api.css("--ink"));
      g2.vline(this.SHIFT_AT, api.css("--green"));
      g2.text(api.T("极差图：方差变大要靠它", "the range chart is what sees spread"),
              2, lim.rucl * 1.15, api.css("--ink"), 12);
    }
  },
});
