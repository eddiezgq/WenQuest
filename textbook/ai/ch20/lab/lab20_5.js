// 实验 20.5 自主实验室的闭环：要试多少次，以及什么会把它带进沟里（配 20.5 节）。
// 两个场景：
//   loop  ：在一张二维“性质面”上跑闭环，选策略（网格/随机/代理模型），看它一次次落在哪；
//   sweep ：把系统偏差从负扫到正，看遗憾怎么跳变，以及闭环自己报的分数怎样越来越虚高。
// 与 code/_ch20.py 是同一套算法（response_surface、measure、kernel_ridge、closed_loop）。
WQ.lab({
  title: ["实验 20.5 闭环要试多少次，什么会把它带偏",
          "Lab 20.5 How many experiments the loop needs, and what throws it off"],
  goal: ["先在干净的测量下比三种提议策略：同样的预算，谁离真正的最好点更近。再把随机噪声与系统偏差分别加上去——噪声让闭环多走几步，偏差却是另一回事：小的时候几乎没影响，过了一个门槛整段跑偏，而且往哪个方向偏，后果完全不同。全程注意右上角那两个数：闭环**自己报的分数**与**真值**，偏差越大它们越不是一回事。",
         "First compare three proposal strategies under clean measurements: with the same budget, which one lands closest to the true optimum. Then add random noise and systematic bias separately. Noise merely costs extra experiments; bias is different — below a threshold it barely matters, above it the loop goes badly wrong, and the direction matters too. Watch the two readouts at all times: what the loop believes it found, and the truth."],
  scenes: [
    { id: "loop", name: ["闭环跑一遍", "Run the loop"],
      problem: { title: ["问题：同样的预算，怎么花", "Problem: how to spend the same budget"],
                 text: ["自主实验室的循环是：提议一个成分 → 做出来 → 测一遍 → 把结果填回模型 → 再提议。真实的实验一次要几个小时到几天，所以“要试多少次”就是全部的成本。网格挨个试不动脑子，但覆盖均匀；随机试便宜；代理模型（这里用高斯核岭回归 + 上置信界）拿已测的点拟一个面，再挑“要么看着好、要么没人去过”的点。注意判成绩要用**真值**，不能用闭环自己测到的数。",
                        "The loop is: propose a composition, make it, measure it, feed the result back, propose again. A real experiment takes hours to days, so the number of experiments is the whole cost. A grid is unthinking but uniform; random is cheap; a surrogate model (here kernel ridge regression with an upper confidence bound) fits a surface to what has been measured and proposes points that either look good or have never been tried. Score the run against the truth, never against what the loop measured."] } },
    { id: "sweep", name: ["偏差扫一遍", "Sweep the bias"],
      problem: { title: ["问题：噪声与偏差不是一回事", "Problem: noise and bias are not the same thing"],
                 text: ["随机噪声多测几次就能抹平；**系统偏差抹不平**——它把整张面拧歪，于是闭环一路爬到错的地方，还以为自己找得很好。这个场景把偏差从负扫到正，画两条线：按真值算的遗憾，和闭环自己报的分数减去真正的最优。两条线一起看才是要点：偏差越大，自报的分数越高，而选出来的东西越差。",
                        "Random noise averages out if you measure more; a systematic bias does not. It tilts the whole surface, so the loop climbs to the wrong place while believing it did well. This scene sweeps the bias from negative to positive and draws two curves: regret against the truth, and the loop's self-reported score minus the true optimum. Read them together: as the bias grows, the self-reported score rises while the pick gets worse."] } },
  ],
  params: [
    { id: "strategy", name: ["策略：0 = 网格，1 = 随机，2 = 代理模型", "strategy: 0 = grid, 1 = random, 2 = surrogate"], min: 0, max: 2, step: 1, value: 2, digits: 0 },
    { id: "budget", name: ["预算（做多少次实验）", "budget (number of experiments)"], min: 6, max: 64, step: 2, value: 24, digits: 0 },
    { id: "noise", name: ["随机噪声", "random noise"], min: 0, max: 0.3, step: 0.01, value: 0, digits: 2 },
    { id: "bias", name: ["系统偏差（随成分漂移，可正可负）", "systematic bias (drifts with composition)"], min: -1.2, max: 1.2, step: 0.1, value: 0, digits: 1 },
    { id: "seed", name: ["第几次重复", "repeat number"], min: 0, max: 7, step: 1, value: 0, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["已经做过的点", "experiments already done"] },
           { color: "var(--green)", name: ["真正的最好点", "the true optimum"] },
           { color: "var(--red)", name: ["闭环挑出来的那个", "what the loop picked"] },
           { color: "var(--muted)", name: ["性质面的等高线", "contours of the property surface"] }],
  tasks: [
    { id: "grid24", text: ["干净测量（噪声与偏差都为 0）、预算 24：网格策略的遗憾是多少？换成代理模型再记一次，差几倍？",
                           "With clean measurements and a budget of 24, record the regret for the grid strategy, then for the surrogate. What is the ratio?"],
      demo: { scene: "loop", set: { strategy: 0, budget: 24, noise: 0, bias: 0 }, press: [] } },
    { id: "bayes24", text: ["代理模型、预算 24，把“第几次重复”从 0 拖到 7：遗憾在什么范围里晃？这说明只跑一次能不能下结论。",
                            "Surrogate strategy, budget 24: drag the repeat number from 0 to 7 and see the spread in regret. Can a single run settle anything?"],
      demo: { scene: "loop", set: { strategy: 2, budget: 24, noise: 0, bias: 0 }, press: [] } },
    { id: "noisy", text: ["把随机噪声加到 0.2（偏差仍为 0）：遗憾变大了多少？再把预算加到 48——噪声能不能靠多做实验压下去？",
                          "Raise the noise to 0.2 with no bias: how much does the regret grow? Then raise the budget to 48 — can more experiments absorb noise?"],
      demo: { scene: "loop", set: { strategy: 2, budget: 24, noise: 0.2, bias: 0 }, press: [] } },
    { id: "biased", text: ["噪声调回 0.02，把系统偏差拖到 −1.0：闭环挑在哪？它自己报的分数与真值各是多少？",
                           "Set the noise back to 0.02 and drag the bias to −1.0: where does the loop land, and how do its self-reported score and the truth compare?"],
      demo: { scene: "loop", set: { strategy: 2, budget: 32, noise: 0.02, bias: -1 }, press: [] } },
    { id: "thresh", text: ["切到第二个场景：遗憾从哪个偏差开始跳上去？正负两个方向的门槛一样吗？",
                           "Switch to the second scene: at which bias does the regret jump, and is the threshold the same in both directions?"],
      demo: { scene: "sweep", set: { strategy: 2, budget: 32, noise: 0.02 }, press: [] } },
  ],
  think: ["偏差在这里是“越靠右测得越高”。如果你的表征设备有这种毛病，光看闭环自己报的分数，能不能发现？要加一道什么样的检查才发现得了——想一个花得起的办法（提示：留几个点重复测，或者把已测过的点拿去别的设备上复测）。",
          "The bias here reads high towards one end of the composition range. If your characterisation setup had such a fault, could you detect it from the loop's own scores? What check would reveal it at an affordable cost — for instance repeat measurements, or re-measuring some points on a different instrument?"],

  NG: 33,
  truth(a, b) {
    const main = Math.exp(-(Math.pow((a - 0.72) / 0.18, 2) + Math.pow((b - 0.35) / 0.22, 2)));
    const decoy = 0.72 * Math.exp(-(Math.pow((a - 0.22) / 0.16, 2) + Math.pow((b - 0.78) / 0.18, 2)));
    return main + decoy;
  },
  rng(seed) { let x = seed * 1103515245 + 12345; return () => { x = (x * 1103515245 + 12345) % 2147483648; return x / 2147483648; }; },
  gauss(r) { const u = Math.max(r(), 1e-9), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },

  grid() {
    if (this._cand) return this._cand;
    const c = [];
    for (let i = 0; i < this.NG; i++)
      for (let j = 0; j < this.NG; j++) c.push([i / (this.NG - 1), j / (this.NG - 1)]);
    this._cand = c;
    return c;
  },
  // 高斯核岭回归：均值 + “离已测点有多远”当不确定度（与 _ch20.kernel_ridge 同一套）
  krr(X, y, Q, ls, lam) {
    const n = X.length, K = [];
    const k = (p, q) => Math.exp(-((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) / (2 * ls * ls));
    for (let i = 0; i < n; i++) { K.push([]); for (let j = 0; j < n; j++) K[i].push(k(X[i], X[j]) + (i === j ? lam : 0)); }
    // 高斯消元解 K a = y
    const M = K.map((row, i) => row.concat([y[i]]));
    for (let i = 0; i < n; i++) {
      let p = i;
      for (let r = i + 1; r < n; r++) if (Math.abs(M[r][i]) > Math.abs(M[p][i])) p = r;
      const t = M[i]; M[i] = M[p]; M[p] = t;
      const d = M[i][i] || 1e-12;
      for (let c = i; c <= n; c++) M[i][c] /= d;
      for (let r = 0; r < n; r++) if (r !== i && M[r][i]) {
        const f = M[r][i];
        for (let c = i; c <= n; c++) M[r][c] -= f * M[i][c];
      }
    }
    const al = M.map((row) => row[n]);
    return Q.map((q) => {
      let m = 0, best = 0;
      for (let i = 0; i < n; i++) { const kv = k(q, X[i]); m += kv * al[i]; if (kv > best) best = kv; }
      return [m, Math.sqrt(Math.max(1 - best * best, 0))];
    });
  },
  run(strategy, budget, noise, bias, seed) {
    const key = [strategy, budget, noise, bias, seed].join(",");
    if (this._r && this._r.key === key) return this._r.val;
    const cand = this.grid(), r = this.rng(seed * 977 + 13);
    const tried = [], ys = [];
    for (let t = 0; t < budget; t++) {
      let nxt;
      if (strategy === 0) nxt = (t * Math.max(1, Math.floor(cand.length / budget))) % cand.length;
      else if (strategy === 1) nxt = Math.floor(r() * cand.length);
      else if (tried.length < 3) nxt = Math.floor(r() * cand.length);
      else {
        const X = tried.map((i) => cand[i]);
        const pred = this.krr(X, ys, cand, 0.18, 1e-3);
        let best = -1e9;
        nxt = 0;
        for (let i = 0; i < cand.length; i++) {
          if (tried.indexOf(i) >= 0) continue;
          const sc = pred[i][0] + 1.5 * pred[i][1];
          if (sc > best) { best = sc; nxt = i; }
        }
      }
      if (tried.indexOf(nxt) >= 0) {
        const free = [];
        for (let i = 0; i < cand.length; i++) if (tried.indexOf(i) < 0) free.push(i);
        nxt = free[Math.floor(r() * free.length)];
      }
      tried.push(nxt);
      const p = cand[nxt];
      ys.push(this.truth(p[0], p[1]) + noise * this.gauss(r) + bias * (p[0] - 0.5));
    }
    let bi = 0;
    for (let i = 1; i < ys.length; i++) if (ys[i] > ys[bi]) bi = i;
    const pick = cand[tried[bi]];
    let tbest = -1e9, bp = cand[0];
    for (const c of cand) { const v = this.truth(c[0], c[1]); if (v > tbest) { tbest = v; bp = c; } }
    const val = { tried, ys, pick, believed: ys[bi], truthOfPick: this.truth(pick[0], pick[1]),
                  truthBest: tbest, best: bp, cand };
    val.regret = val.truthBest - val.truthOfPick;
    this._r = { key, val };
    return val;
  },
  sweep(strategy, budget, noise, seed) {
    const key = [strategy, budget, noise, seed].join(",");
    if (this._s && this._s.key === key) return this._s.val;
    const out = [];
    for (let b = -1.2; b <= 1.201; b += 0.2) {
      const bb = +b.toFixed(1);
      let reg = 0, bel = 0;
      for (let j = 0; j < 3; j++) {
        const r = this.run(strategy, budget, noise, bb, seed + j);
        reg += r.regret; bel += r.believed - r.truthBest;
      }
      out.push([bb, reg / 3, bel / 3]);
    }
    this._s = { key, val: out };
    return out;
  },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p;
    const st = Math.round(q.strategy), bud = Math.round(q.budget);
    const noise = +q.noise.toFixed(2), bias = +q.bias.toFixed(1), seed = Math.round(q.seed);
    if (api.scene === "sweep") {
      const sw = this.sweep(st, bud, noise, seed);
      const base = sw.find((v) => Math.abs(v[0]) < 0.05)[1];
      let negThr = null, posThr = null;
      for (const [b, reg] of sw) {
        if (b < 0 && reg > 3 * Math.max(base, 1e-6)) negThr = b;
        if (b > 0 && reg > 3 * Math.max(base, 1e-6) && posThr === null) posThr = b;
      }
      api.done("thresh");
      return [[["无偏差时的遗憾", "regret with no bias"], base.toFixed(3)],
              [["负方向的门槛", "threshold, negative direction"],
               negThr === null ? api.T("扫到头也没塌", "never breaks down") : negThr.toFixed(1)],
              [["正方向的门槛", "threshold, positive direction"],
               posThr === null ? api.T("扫到头也没塌", "never breaks down") : posThr.toFixed(1)],
              [["最坏那一档的遗憾", "worst regret in the sweep"],
               Math.max.apply(null, sw.map((v) => v[1])).toFixed(3)],
              [["同样大小、方向相反，后果一样吗", "same size, opposite sign: same outcome?"],
               api.T("不一样", "no")]];
    }
    const r = this.run(st, bud, noise, bias, seed);
    if (st === 0 && bud >= 24 && noise === 0 && bias === 0) s.gridReg = r.regret;
    if (st === 2 && bud >= 24 && noise === 0 && bias === 0) { if (s.gridReg !== undefined) api.done("grid24"); api.done("bayes24"); }
    if (st === 2 && noise >= 0.19 && Math.abs(bias) < 0.05) api.done("noisy");
    if (Math.abs(bias) >= 0.95) api.done("biased");
    return [[["做了多少次实验", "experiments done"], String(bud)],
            [["挑出来的成分", "the pick"], `(${r.pick[0].toFixed(2)}, ${r.pick[1].toFixed(2)})`],
            [["真正的最好点", "the true optimum"], `(${r.best[0].toFixed(2)}, ${r.best[1].toFixed(2)})`],
            [["闭环自己报的分数", "what the loop believes it found"], r.believed.toFixed(3)],
            [["这一点的真值", "the truth at that point"], r.truthOfPick.toFixed(3)],
            [["遗憾（真值口径）", "regret, measured against the truth"], r.regret.toFixed(3)]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p;
    const st = Math.round(q.strategy), bud = Math.round(q.budget);
    const noise = +q.noise.toFixed(2), bias = +q.bias.toFixed(1), seed = Math.round(q.seed);
    if (api.scene === "sweep") {
      const sw = this.sweep(st, bud, noise, seed);
      const g = api.graph({ x: 52, y: 28, w: w - 100, h: h - 96, xmin: -1.3, xmax: 1.3,
                            ymin: -0.3, ymax: 1.2,
                            xlabel: api.T("系统偏差", "systematic bias"),
                            ylabel: api.T("遗憾 / 自报分数的虚高", "regret / inflation") }).axes();
      g.hline(0, api.css("--muted"));
      g.pts(sw.map((v) => [v[0], v[1]]), api.css("--red"), 2.4);
      g.pts(sw.map((v) => [v[0], v[2]]), api.css("--blue"), 2.0, [5, 4]);
      g.text(api.T("红：按真值算的遗憾", "red: regret against the truth"), -1.25, 1.1, api.css("--red"), 12);
      g.text(api.T("蓝：闭环自己报的分数减去真正的最优",
                   "blue: self-reported score minus the true optimum"), -1.25, 0.98, api.css("--blue"), 12);
      return;
    }
    const r = this.run(st, bud, noise, bias, seed);
    const g = api.graph({ x: 52, y: 28, w: Math.min(h - 96, w * 0.52), h: h - 96,
                          xmin: 0, xmax: 1, ymin: 0, ymax: 1,
                          xlabel: api.T("成分 a", "composition a"),
                          ylabel: api.T("成分 b", "composition b") }).axes();
    for (const lv of [0.2, 0.5, 0.8]) {
      const ring = [];
      for (let t = 0; t <= 60; t++) {
        const th = t / 60 * 2 * Math.PI;
        const rad = Math.sqrt(-Math.log(lv));
        ring.push([0.72 + 0.18 * rad * Math.cos(th), 0.35 + 0.22 * rad * Math.sin(th)]);
      }
      g.pts(ring, api.css("--muted"), 1.2, [3, 3]);
    }
    const cand = r.cand;
    r.tried.forEach((idx, k) => {
      const p = cand[idx];
      g.point(p[0], p[1], k === r.tried.length - 1 ? api.css("--ink") : api.css("--blue"));
    });
    g.point(r.best[0], r.best[1], api.css("--green"));
    g.point(r.pick[0], r.pick[1], api.css("--red"));
    g.text(api.T("绿：真正的最好点　红：闭环挑的", "green: true optimum, red: the pick"),
           0.03, 0.05, api.css("--ink"), 12);
    // 右边：遗憾随预算怎么降（同一策略、同一次重复）
    const g2 = api.graph({ x: 52 + Math.min(h - 96, w * 0.52) + 40, y: 28,
                           w: w - (52 + Math.min(h - 96, w * 0.52) + 80), h: h - 96,
                           xmin: 6, xmax: 64, ymin: 0, ymax: 1.2,
                           xlabel: api.T("预算", "budget"),
                           ylabel: api.T("遗憾", "regret") }).axes();
    const curve = [];
    for (let b = 6; b <= 64; b += 6) curve.push([b, this.run(st, b, noise, bias, seed).regret]);
    g2.pts(curve, api.css("--red"), 2.2);
    g2.vline(bud, api.css("--green"));
  },
});
