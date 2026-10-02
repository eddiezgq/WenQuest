// 实验 9.1 噪声读数的统计（配 9.1 节）。读数 = 真实值 + 高斯噪声（固定种子，Box–Muller 法生成），每 N 个读数取一次平均。
// 测力传感器：真实值 15 N（算例 9.1.2）；厨房秤：真实值 250 g。读数到齐 max(2000, 300N) 个后自动停止。
WQ.lab({
  title: ["实验 9.1 噪声读数的统计", "Lab 9.1 Statistics of noisy readings"],
  goal: ["收集带噪声的读数，计算样本均值和样本标准差，检验 68–95–99.7 规则，并验证平均 N 个读数使标准差缩小为 1/√N。",
         "Collect noisy readings, compute the sample mean and standard deviation, check the 68–95–99.7 rule, and verify that averaging N readings shrinks the spread by 1/√N."],
  scenes: [
    { id: "force", robot: true, name: ["夹爪测力传感器", "Gripper force sensor"],
      params: { sig: { min: 0.01, max: 0.3, step: 0.01, value: 0.08 } },
      problem: { title: ["机器人问题：夹紧力的读数在跳", "Robot problem: the clamping-force reading jumps"],
                 text: ["夹紧力恒为 15 N，读数却在 15 N 上下跳动。用多少个读数、怎样平均，才能得到稳定可信的力？",
                        "The clamping force is a steady 15 N, yet the reading jumps around it. How many readings, averaged how, give a trustworthy force?"] } },
    { id: "scale", name: ["厨房秤", "Kitchen scale"],
      params: { sig: { min: 0.1, max: 2, step: 0.05, value: 0.5 } },
      problem: { title: ["生活中的例子：称 250 g 面粉", "Everyday example: weighing 250 g of flour"],
                 text: ["秤的读数每次差零点几克。平均几次，才能把波动降到 0.1 g 以下？",
                        "The scale differs by a few tenths of a gram each time. How many readings must be averaged to get below 0.1 g?"] } },
  ],
  params: [
    { id: "sig", name: ["噪声标准差 σ", "Noise standard deviation σ"], min: 0.01, max: 0.3, step: 0.01, value: 0.08, unit: "", digits: 2 },
    { id: "N", name: ["每次平均的读数个数 N", "Readings per average N"], min: 1, max: 64, step: 1, value: 1, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "rule", robot: true, text: ["N = 1，收集 2000 个读数，验证落在 x̄ ± s 内的读数约占 68%。", "With N = 1 collect 2000 readings; about 68% lie within x̄ ± s."],
      demo: { scene: "force", set: { sig: 0.08, N: 1 }, press: ["start"], wait: 8 } },
    { id: "avg", robot: true, text: ["N = 16，验证平均值的标准差约为单个读数的 1/4。", "With N = 16 the averages spread about 1/4 as much as single readings."],
      demo: { scene: "force", set: { sig: 0.08, N: 16 }, press: ["start"], wait: 10 } },
    { id: "flour", text: ["厨房秤，σ = 0.5 g：找出使平均值的标准差不超过 0.1 g 的最小 N，并收集读数验证。", "Kitchen scale, σ = 0.5 g: find the smallest N that brings the averages to 0.1 g or less, and collect readings to check."],
      demo: { scene: "scale", set: { sig: 0.5, N: 25 }, press: ["start"], wait: 12 } },
  ],
  think: ["为什么要把标准差减小到 1/10，需要平均 100 个读数，而不是 10 个？如果相邻读数不独立（例如都偏高），平均的效果会怎样？",
          "Why does cutting the spread to 1/10 need 100 readings, not 10? What happens to averaging if neighbouring readings are not independent?"],

  truth(api) { return api.scene === "force" ? 15 : 250; },
  unit(api) { return api.scene === "force" ? "N" : "g"; },
  gauss(s) {   // 线性同余 + Box–Muller，种子固定，每次重置后序列相同
    s.seed = (s.seed * 1103515245 + 12345) % 2147483648; const u1 = s.seed / 2147483648 + 1e-12;
    s.seed = (s.seed * 1103515245 + 12345) % 2147483648; const u2 = s.seed / 2147483648;
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  },
  stats(a) {
    const n = a.length; if (n < 2) return { n, m: n ? a[0] : 0, s: 0 };
    let m = 0; a.forEach((v) => { m += v; }); m /= n;
    let q = 0; a.forEach((v) => { q += (v - m) * (v - m); });
    return { n, m, s: Math.sqrt(q / (n - 1)) };
  },
  target(api) { return Math.max(2000, 300 * api.p.N); },

  reset(api, s) { s.seed = 9011; s.x = []; s.avg = []; s.acc = 0; s.k = 0; },
  update(dt, api, s) {
    const T = this.truth(api), sig = api.p.sig, N = api.p.N;
    for (let i = 0; i < 60 && s.x.length < this.target(api); i++) {
      const v = T + sig * this.gauss(s);
      s.x.push(v); s.acc += v; s.k += 1;
      if (s.k === N) { s.avg.push(s.acc / N); s.acc = 0; s.k = 0; }
    }
    if (s.x.length >= this.target(api)) api.stop();
  },
  readouts(api, s) {
    const u = this.unit(api), st = this.stats(s.x), sa = this.stats(s.avg), N = api.p.N;
    let inside = 0; s.x.forEach((v) => { if (Math.abs(v - st.m) < st.s) inside++; });
    const frac = st.n ? inside / st.n : 0;
    if (api.scene === "force" && N === 1 && st.n >= 2000 && frac > 0.65 && frac < 0.71) api.done("rule");
    if (api.scene === "force" && N === 16 && sa.n >= 150 && Math.abs(sa.s / (st.s / 4) - 1) < 0.2) api.done("avg");
    if (api.scene === "scale" && Math.abs(api.p.sig - 0.5) < 0.01 && N === 25 && sa.n >= 100 && sa.s < 0.12) api.done("flour");
    const d = api.scene === "force" ? 4 : 3;
    return [[["读数个数 n", "readings n"], String(st.n)],
            [["样本均值 x̄", "sample mean x̄"], api.fmt(st.m, d) + " " + u],
            [["样本标准差 s", "sample std s"], api.fmt(st.s, d) + " " + u],
            [["落在 x̄ ± s 内", "within x̄ ± s"], api.fmt(100 * frac, 1) + " %"],
            [["平均值的个数", "number of averages"], String(sa.n)],
            [["平均值的样本标准差", "sample std of the averages"], api.fmt(sa.s, d) + " " + u],
            [["理论值 σ/√N", "theory σ/√N"], api.fmt(api.p.sig / Math.sqrt(N), d) + " " + u]];
  },
  draw(api, s) {
    const { w, h } = api, T = this.truth(api), sig = api.p.sig, u = this.unit(api);
    const half = 4 * sig, lo = T - half, hi = T + half;
    // 左：最近 200 个读数（灰）与平均值（彩色）
    const x0 = 46, x1 = w * 0.48, yt = 28, yb = h - 40;
    const Y = (v) => yb - (yb - yt) * (v - lo) / (hi - lo);
    api.rect(x0, yt, x1 - x0, yb - yt, null, api.css("--grid"));
    api.line(x0, Y(T), x1, Y(T), api.css("--muted"), 1, [5, 4]);
    const m = Math.max(0, s.x.length - 200), seg = s.x.slice(m), c = api.ctx;
    c.beginPath(); seg.forEach((v, i) => { const X = x0 + (x1 - x0) * i / 199, yy = Math.min(yb, Math.max(yt, Y(v))); i ? c.lineTo(X, yy) : c.moveTo(X, yy); });
    c.strokeStyle = api.css("--muted"); c.lineWidth = 1; c.stroke();
    if (api.p.N > 1) {
      const N = api.p.N;
      s.avg.forEach((v, j) => { const idx = (j + 1) * N - 1 - m; if (idx >= 0 && idx < 200) api.circle(x0 + (x1 - x0) * idx / 199, Y(v), 3.5, api.css("--blue")); });
    }
    api.label(api.T("最近 200 个读数（灰），平均值（蓝点）", "last 200 readings (grey), averages (blue dots)"), x0, yt - 12, api.css("--muted"), 12);
    api.label(api.fmt(hi, 2) + " " + u, x0 + 4, yt + 9, api.css("--muted"), 11, "left");
    api.label(api.fmt(lo, 2) + " " + u, x0 + 4, yb - 9, api.css("--muted"), 11, "left");
    // 右：直方图（读数：灰；平均值：蓝），化为密度；虚线为高斯曲线
    const hx0 = w * 0.55, hx1 = w - 18, hy0 = yb, hy1 = yt;
    const X = (v) => hx0 + (hx1 - hx0) * (v - lo) / (hi - lo);
    const nb = 32, bw = (hi - lo) / nb;
    const dens = (arr) => { const cnt = new Array(nb).fill(0); arr.forEach((v) => { const k = Math.floor((v - lo) / bw); if (k >= 0 && k < nb) cnt[k]++; });
      return cnt.map((k) => (arr.length ? k / (arr.length * bw) : 0)); };
    const peakA = 1 / (sig / Math.sqrt(api.p.N) * Math.sqrt(2 * Math.PI)), peak1 = 1 / (sig * Math.sqrt(2 * Math.PI));
    const top = Math.max(peak1, api.p.N > 1 ? peakA : 0) * 1.1;
    const H = (d) => hy0 - (hy0 - hy1) * Math.min(1, d / top);
    api.line(hx0, hy0, hx1, hy0, api.css("--ink"), 1);
    dens(s.x).forEach((d, k) => { if (d > 0) api.rect(X(lo + k * bw) + 1, H(d), (hx1 - hx0) / nb - 2, hy0 - H(d), api.css("--grid")); });
    if (api.p.N > 1) dens(s.avg).forEach((d, k) => { if (d > 0) { c.globalAlpha = 0.55; api.rect(X(lo + k * bw) + 1, H(d), (hx1 - hx0) / nb - 2, hy0 - H(d), api.css("--blue")); c.globalAlpha = 1; } });
    const curve = (sd, col) => { c.beginPath(); for (let i = 0; i <= 120; i++) { const v = lo + (hi - lo) * i / 120, d = Math.exp(-0.5 * ((v - T) / sd) ** 2) / (sd * Math.sqrt(2 * Math.PI)); i ? c.lineTo(X(v), H(d)) : c.moveTo(X(v), H(d)); }
      c.strokeStyle = col; c.lineWidth = 1.8; c.setLineDash([5, 4]); c.stroke(); c.setLineDash([]); };
    curve(sig, api.css("--ink"));
    if (api.p.N > 1) curve(sig / Math.sqrt(api.p.N), api.css("--blue"));
    api.line(X(T), hy0, X(T), hy0 + 6, api.css("--ink"), 1.5);
    api.label(api.fmt(T, 0) + " " + u, X(T), hy0 + 16, api.css("--ink"), 11, "center");
    api.label(api.T("直方图（化为密度）与高斯曲线", "histogram (as density) and Gaussian"), hx0, yt - 12, api.css("--muted"), 12);
    if (api.scene === "scale") {   // 一台秤与一碗面粉
      api.rect(14, h - 30, 70, 10, api.css("--panel"), api.css("--ink"), 3);
      api.circle(49, h - 37, 9, api.css("--amber-soft"), api.css("--amber"));
    }
  },
});
