// 实验 M2.5 学习率、条件数与动量（配 M2.3、M2.5 节）。
// 两个场景：
//   bowl ：一个二次损失（条件数可调）上的梯度下降：调学习率、动量与初值，看轨迹、收敛还是发散、用几步；
//   rate ：同一个问题，横扫学习率，看"降到千分之一所需步数"随学习率变化的那条 U 形曲线，以及 2/λmax 这条墙。
// 全部在浏览器里现算，不需要显卡；用的公式与算例 M2.3.1、M2.5.1 完全相同。
WQ.lab({
  title: ["实验 M2.5 学习率、条件数与动量", "Lab M2.5 Learning rate, condition number, momentum"],
  goal: ["自己把学习率推到发散的那条线上，看它是不是正好在 2/λmax；再把条件数从 2 调到 1000，看所需步数怎样跟着涨；最后加动量，看步数从与 κ 成正比变成与 √κ 成正比。",
         "Push the learning rate up to the point where it diverges and check that the line sits at 2/lambda_max; raise the condition number from 2 to 1000 and watch the step count follow; then add momentum and see the count drop from order kappa to order sqrt(kappa)."],
  scenes: [
    { id: "bowl", name: ["碗里的轨迹", "Trajectory in the bowl"],
      problem: { title: ["问题：步子迈多大", "Problem: how big a step"],
                 text: ["损失的等高线是一族扁椭圆，越扁条件数越大。步子小了慢，大了会沿着陡的方向来回跨，再大就冲出碗外。这条分界线不是调出来的，是算出来的：η = 2/λmax。",
                        "The contours are flat ellipses — the flatter, the larger the condition number. Small steps crawl; large ones zig-zag across the steep direction; larger still and the iterate flies out. That boundary is computed, not tuned: eta = 2/lambda_max."] } },
    { id: "rate", name: ["步数随学习率", "Steps vs learning rate"],
      problem: { title: ["问题：最快的学习率在哪里", "Problem: where is the fastest rate"],
                 text: ["把学习率从很小扫到发散，所需步数先降后升，最低点在 2/(λmin + λmax)。这条 U 形曲线解释了为什么调学习率要按数量级扫，也解释了为什么“再大一点点”会突然炸。",
                        "Sweep the learning rate from tiny to divergent: the step count falls, then rises, with the minimum at 2/(lambda_min + lambda_max). This U-shape is why you sweep by orders of magnitude — and why one notch too far blows up."] } },
  ],
  params: [
    { id: "kappa", name: ["条件数 κ", "condition number"], min: 2, max: 1000, step: 2, value: 20, digits: 0 },
    { id: "eta", name: ["学习率 η（占 2/λmax 的 %）", "learning rate (% of 2/lambda_max)"], min: 2, max: 140, step: 2, value: 50, digits: 0 },
    { id: "beta", name: ["动量系数 β", "momentum"], min: 0, max: 0.98, step: 0.02, value: 0, digits: 2 },
    { id: "th1", name: ["初值 θ₁", "initial theta1"], min: -1.5, max: 1.5, step: 0.1, value: 1, digits: 1 },
    { id: "th2", name: ["初值 θ₂", "initial theta2"], min: -1.5, max: 1.5, step: 0.1, value: 1, digits: 1 },
  ],
  legend: [{ color: "var(--blue)", name: ["轨迹", "trajectory"] }, { color: "var(--muted)", name: ["等高线", "contours"] },
           { color: "var(--red)", name: ["发散", "diverging"] }],
  tasks: [
    { id: "wall", text: ["把学习率调到 100%（即 η = 2/λmax）再往上推一格：轨迹什么时候开始不收敛？这条墙与公式对得上吗？",
                         "Raise the learning rate to 100% (eta = 2/lambda_max) and one notch beyond: when does it stop converging? Does the wall match the formula?"],
      demo: { scene: "bowl", set: { eta: 102 }, press: [] } },
    { id: "zig", text: ["把 η 调到 99%、条件数调到 100：轨迹为什么是之字形？之字出现在陡的方向还是平的方向？",
                        "Set eta to 99% and the condition number to 100: why does the path zig-zag, and along which direction?"],
      demo: { scene: "bowl", set: { eta: 99, kappa: 100 }, press: [] } },
    { id: "kappa", text: ["保持最优学习率，把条件数从 20 调到 200、再到 1000：所需步数大约按什么关系涨？",
                          "Keep the optimal rate and raise the condition number from 20 to 200 to 1000: how does the step count grow?"],
      demo: { scene: "rate", set: { kappa: 1000 }, press: [] } },
    { id: "mom", text: ["条件数仍取 1000，把动量从 0 调到 0.9 以上：步数降到原来的几分之一？与 √κ 的预测对得上吗？",
                        "Keep kappa at 1000 and raise the momentum above 0.9: by what factor does the step count fall, and does it match the sqrt(kappa) prediction?"],
      demo: { scene: "rate", set: { kappa: 1000, beta: 0.9 }, press: [] } },
  ],
  think: ["为什么“把所有特征标准化”能让训练快很多？（提示：标准化改变的是这张图的哪个量？）",
          "Why does standardising the features speed up training so much? (Hint: which quantity in this picture does it change?)"],

  MAXK: 30000,
  etaMax(p) { return 2 / p.kappa; },                       // λmax = κ（本实验取 λmin = 1）
  run(p, etaFrac, beta, maxk) {
    const lam = [1, p.kappa], eta = etaFrac * this.etaMax(p);
    let t = [p.th1, p.th2], v = [0, 0];
    const tr = [[t[0], t[1]]];
    const d0 = Math.hypot(p.th1, p.th2) || 1;
    let k = -1;
    for (let i = 1; i <= (maxk || this.MAXK); i++) {
      for (let j = 0; j < 2; j++) { v[j] = beta * v[j] - eta * lam[j] * t[j]; t[j] += v[j]; }
      if (tr.length < 400) tr.push([t[0], t[1]]);
      const d = Math.hypot(t[0], t[1]);
      if (k < 0 && d < d0 * 1e-3) k = i;
      if (!isFinite(d) || d > 1e6) return { tr, k: -1, blown: true };
    }
    return { tr, k, blown: false };
  },
  calc(api) {
    const p = api.p, key = [p.kappa, p.eta, p.beta, p.th1, p.th2].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const r = this.run(p, p.eta / 100, p.beta);
    // 扫一遍学习率：步数随 η 的 U 形曲线
    const sweep = [];
    for (let f = 2; f <= 140; f += 2) sweep.push([f, this.run(p, f / 100, p.beta, 30000).k]);
    const ok = sweep.filter((s) => s[1] > 0);
    const best = ok.length ? ok.reduce((a, b) => (b[1] < a[1] ? b : a)) : null;
    const val = { r, sweep, best, etaMax: this.etaMax(p),
                  etaOpt: 2 / (1 + p.kappa),
                  // 预测：最优学习率下每步收缩 (κ−1)/(κ+1)，降到千分之一要 ln(1000)/|ln r| 步；
                  // 带最优动量时收缩因子是 (√κ−1)/(√κ+1)
                  predict: Math.round(Math.log(1000) / -Math.log((p.kappa - 1) / (p.kappa + 1))),
                  predictMom: Math.round(Math.log(1000) / -Math.log((Math.sqrt(p.kappa) - 1) / (Math.sqrt(p.kappa) + 1))) };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const p = api.p, c = this.calc(api);
    if (p.eta > 100 && c.r.k < 0) api.done("wall");
    if (p.eta >= 95 && p.eta <= 100 && p.kappa >= 100) api.done("zig");
    if (api.scene === "rate" && p.kappa >= 1000 && p.beta < 0.1) api.done("kappa");
    if (api.scene === "rate" && p.kappa >= 1000 && p.beta >= 0.9) api.done("mom");
    return [[["学习率 η", "learning rate"], api.fmt(p.eta / 100 * c.etaMax, 4)],
            [["发散的那条线 2/λmax", "the wall 2/lambda_max"], api.fmt(c.etaMax, 4)],
            [["最优学习率 2/(λmin+λmax)", "optimal rate"], api.fmt(c.etaOpt, 4)],
            [["降到千分之一用的步数", "steps to 1/1000"], c.r.k > 0 ? String(c.r.k) : api.T("没收敛", "did not converge")],
            [["这条曲线上最快的 η（% of 2/λmax）", "fastest eta on the sweep"], c.best ? c.best[0] + "%" : "—"],
            [["预测步数：无动量 / 带最优动量", "predicted steps: plain / with momentum"],
             c.predict + " / " + c.predictMom]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api), p = api.p;
    if (api.scene === "bowl") {
      const sx = (w - 60) / 3.4, sy = (h - 70) / 3.4, cx = w / 2, cy = (h - 20) / 2;
      const X = (a) => cx + a * sx, Y = (b) => cy - b * sy;
      api.line(X(-1.7), Y(0), X(1.7), Y(0), api.css("--grid"), 1);
      api.line(X(0), Y(-1.7), X(0), Y(1.7), api.css("--grid"), 1);
      for (const lev of [0.05, 0.2, 0.5, 1.0, 1.6]) {       // 等高线 ½(θ₁² + κθ₂²) = lev
        let prev = null;
        for (let i = 0; i <= 180; i++) {
          const t = i / 180 * 2 * Math.PI;
          const q = [Math.sqrt(2 * lev) * Math.cos(t), Math.sqrt(2 * lev / p.kappa) * Math.sin(t)];
          const cur = [X(q[0]), Y(q[1])];
          if (prev) api.line(prev[0], prev[1], cur[0], cur[1], api.css("--muted"), 1);
          prev = cur;
        }
      }
      const col = c.r.blown || c.r.k < 0 ? api.css("--red") : api.css("--blue");
      for (let i = 1; i < c.r.tr.length; i++) {
        const a = c.r.tr[i - 1], b = c.r.tr[i];
        api.line(X(a[0]), Y(a[1]), X(b[0]), Y(b[1]), col, 1.8);
      }
      api.circle(X(c.r.tr[0][0]), Y(c.r.tr[0][1]), 5, null, api.css("--ink"));
      api.label(api.T(`κ = ${p.kappa}，η = ${(p.eta / 100 * c.etaMax).toFixed(4)}，β = ${p.beta}`,
                      `kappa = ${p.kappa}, eta = ${(p.eta / 100 * c.etaMax).toFixed(4)}, beta = ${p.beta}`),
                20, h - 14, api.css("--muted"), 12);
      return;
    }
    // 步数随学习率：U 形曲线
    const x0 = 56, y0 = 24, pw = w - x0 - 24, ph = h - y0 - 46;
    const ks = c.sweep.filter((q) => q[1] > 0).map((q) => q[1]);
    const kmax = Math.max(10, ...ks), kmin = Math.max(1, Math.min(...ks));
    const X = (f) => x0 + (f - 2) / 138 * pw;
    const Y = (k) => y0 + ph - (Math.log(k) - Math.log(kmin)) / Math.max(Math.log(kmax) - Math.log(kmin), 1e-9) * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    let prev = null;
    for (const [f, k] of c.sweep) {
      if (k <= 0) { prev = null; continue; }
      const cur = [X(f), Y(k)];
      if (prev) api.line(prev[0], prev[1], cur[0], cur[1], api.css("--blue"), 2);
      prev = cur;
    }
    if (c.best) {
      api.circle(X(c.best[0]), Y(c.best[1]), 5, null, api.css("--green"));
      api.label(api.T(`最快：${c.best[0]}%，${c.best[1]} 步`, `fastest: ${c.best[0]}%, ${c.best[1]} steps`),
                X(c.best[0]) + 8, Y(c.best[1]) - 6, api.css("--green"), 12);
    }
    api.line(X(100), y0, X(100), y0 + ph, api.css("--red"), 1.5, [5, 4]);
    api.label(api.T("100% = 2/λmax：过了这条线就发散", "100% = 2/lambda_max: beyond this it diverges"),
              X(100) - 230, y0 + 14, api.css("--red"), 12);
    api.label(api.T("学习率（占 2/λmax 的 %）", "learning rate (% of 2/lambda_max)"), x0, h - 14, api.css("--muted"), 12);
    api.label(api.T("步数（对数）", "steps (log)"), 8, y0 + 12, api.css("--muted"), 12);
  },
});
