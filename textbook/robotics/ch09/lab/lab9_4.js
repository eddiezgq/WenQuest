// 实验 9.4 带噪声读数估计真实值（配 9.4 节）。
// 对接：真实距离 150 mm；激光、超声读数为真值加高斯噪声（固定种子）；估计值 = w·激光 + (1 − w)·超声。
//       最优权重 w* = σ₂² / (σ₁² + σ₂²)，最小标准差 1/√(1/σ₁² + 1/σ₂²)（式 (9.4.11)）。
// 评委：9 位评委打分，真实水平 8.0 分，正常评委的误差标准差 0.2 分；每位评委以概率 p 打出离谱分数（偏差 ±1～3 分）。
//       比较平均分、中位数、去掉一个最高分和一个最低分的平均（截尾平均），统计均方根误差。
WQ.lab({
  title: ["实验 9.4 带噪声读数估计真实值", "Lab 9.4 Estimating a true value from noisy readings"],
  goal: ["按精度加权融合两个传感器，找出最优权重；在有野值时比较平均值与稳健估计。",
         "Fuse two sensors with precision weights and find the best weight; compare the mean with robust estimates when outliers occur."],
  scenes: [
    { id: "dock", robot: true, name: ["AGV 对接充电桩", "AGV docking at a charger"], hide: ["pout", "est"],
      problem: { title: ["机器人问题：激光和超声，听谁的", "Robot problem: laser or ultrasonic, which to trust"],
                 text: ["激光准（σ = 3 mm），超声粗（σ = 10 mm）。两个读数怎样合成一个最可信的距离？",
                        "The laser is precise (σ = 3 mm), the ultrasonic coarse (σ = 10 mm). How should the two readings be combined?"] } },
    { id: "judge", name: ["评委打分", "Judges' scores"], hide: ["s1", "s2", "w"],
      problem: { title: ["生活中的例子：为什么去掉最高分和最低分", "Everyday example: why drop the highest and lowest scores"],
                 text: ["9 位评委打分，偶尔有人打出离谱的分数。平均分、中位数、去掉最高最低分的平均，哪个更准？",
                        "Nine judges score; now and then one gives a wild score. Which is closest: mean, median, or the mean without the extremes?"] } },
  ],
  params: [
    { id: "s1", name: ["激光的标准差 σ₁", "Laser std σ₁"], min: 1, max: 20, step: 0.5, value: 3, unit: "mm", digits: 1 },
    { id: "s2", name: ["超声的标准差 σ₂", "Ultrasonic std σ₂"], min: 1, max: 20, step: 0.5, value: 10, unit: "mm", digits: 1 },
    { id: "w", name: ["激光的权重 w", "Laser weight w"], min: 0, max: 1, step: 0.01, value: 0.5, unit: "", digits: 2 },
    { id: "pout", name: ["离谱分数的概率 p", "Probability of a wild score p"], min: 0, max: 0.3, step: 0.01, value: 0.1, unit: "", digits: 2 },
    { id: "est", name: ["估计方法：0 平均 / 1 中位数 / 2 去掉最高最低", "Estimator: 0 mean / 1 median / 2 trimmed"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "avg", robot: true, text: ["w = 0.5（简单平均），模拟 1000 次以上，验证误差的标准差大于只用激光的 3 mm。", "w = 0.5 (plain average), at least 1000 runs: the error std exceeds the laser's 3 mm."],
      demo: { scene: "dock", set: { s1: 3, s2: 10, w: 0.5 }, press: ["start"], wait: 5 } },
    { id: "best", robot: true, text: ["调节 w，使误差的标准差最小；与式 (9.4.11) 的最优权重相差不超过 0.02。", "Tune w to minimize the error std; it should be within 0.02 of the optimum from Eq. (9.4.11)."],
      demo: { scene: "dock", set: { s1: 3, s2: 10, w: 0.92 }, press: ["start"], wait: 5 } },
    { id: "trim", text: ["离谱分数的概率 0.1：选“去掉最高最低”，模拟 1000 次以上，它的均方根误差小于平均分的。", "Wild-score probability 0.1: choose “trimmed”, run 1000+ times; its RMS error is below the mean's."],
      demo: { scene: "judge", set: { pout: 0.1, est: 2 }, press: ["start"], wait: 5 } },
  ],
  think: ["把一个好传感器和一个差传感器简单平均，为什么可能比只用好的还差？两个传感器精度相同时，最优权重是多少？",
          "Why can a plain average of a good and a poor sensor be worse than the good one alone? What is the best weight when both are equally precise?"],

  T0: 150, J0: 8.0,
  gauss(s) {
    s.seed = (s.seed * 1103515245 + 12345) % 2147483648; const u1 = s.seed / 2147483648 + 1e-12;
    s.seed = (s.seed * 1103515245 + 12345) % 2147483648; const u2 = s.seed / 2147483648;
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  },
  uni(s) { s.seed = (s.seed * 1103515245 + 12345) % 2147483648; return s.seed / 2147483648; },
  reset(api, s) { s.seed = 9041; s.e = []; s.eL = []; s.eA = []; s.jm = []; s.jd = []; s.jt = []; s.last = null; },
  update(dt, api, s) {
    const p = api.p;
    for (let k = 0; k < 40 && s.e.length + s.jm.length < 3000; k++) {
      if (api.scene === "dock") {
        const z1 = this.T0 + p.s1 * this.gauss(s), z2 = this.T0 + p.s2 * this.gauss(s);
        s.e.push(p.w * z1 + (1 - p.w) * z2 - this.T0); s.eL.push(z1 - this.T0); s.eA.push((z1 + z2) / 2 - this.T0);
        s.last = [z1, z2];
      } else {
        const sc = [];
        for (let j = 0; j < 9; j++) {
          let v = this.J0 + 0.2 * this.gauss(s);
          if (this.uni(s) < p.pout) v += (this.uni(s) < 0.5 ? -1 : 1) * (1 + 2 * this.uni(s));
          sc.push(Math.min(10, Math.max(0, v)));
        }
        const so = sc.slice().sort((a, b) => a - b), mean = sc.reduce((a, b) => a + b, 0) / 9;
        const trim = so.slice(1, 8).reduce((a, b) => a + b, 0) / 7;
        s.jm.push(mean - this.J0); s.jd.push(so[4] - this.J0); s.jt.push(trim - this.J0); s.last = sc;
      }
    }
    if (s.e.length + s.jm.length >= 3000) api.stop();
  },
  sd(a) { const n = a.length; if (n < 2) return NaN; const m = a.reduce((x, y) => x + y, 0) / n; return Math.sqrt(a.reduce((x, y) => x + (y - m) ** 2, 0) / (n - 1)); },
  rms(a) { return a.length ? Math.sqrt(a.reduce((x, y) => x + y * y, 0) / a.length) : NaN; },
  readouts(api, s) {
    const p = api.p, f = (x, d) => (isNaN(x) ? "—" : api.fmt(x, d));
    if (api.scene === "dock") {
      const wopt = p.s2 ** 2 / (p.s1 ** 2 + p.s2 ** 2), sth = Math.sqrt(p.w ** 2 * p.s1 ** 2 + (1 - p.w) ** 2 * p.s2 ** 2);
      const smin = 1 / Math.sqrt(1 / p.s1 ** 2 + 1 / p.s2 ** 2), sw = this.sd(s.e), n = s.e.length;
      const std3 = Math.abs(p.s1 - 3) < 1e-6 && Math.abs(p.s2 - 10) < 1e-6;
      if (std3 && Math.abs(p.w - 0.5) < 1e-6 && n >= 1000 && sw > 3) api.done("avg");
      if (n >= 1000 && Math.abs(p.w - wopt) <= 0.02) api.done("best");
      return [[["模拟次数", "runs"], String(n)],
              [["误差的标准差（模拟，权重 w）", "error std (simulated, weight w)"], f(sw, 3) + " mm"],
              [["理论值 √(w²σ₁² + (1−w)²σ₂²)", "theory √(w²σ₁² + (1−w)²σ₂²)"], f(sth, 3) + " mm"],
              [["只用激光（模拟）", "laser only (simulated)"], f(this.sd(s.eL), 3) + " mm"],
              [["简单平均（模拟）", "plain average (simulated)"], f(this.sd(s.eA), 3) + " mm"],
              [["最优权重 w* 与最小标准差", "best weight w* and its std"], `${api.fmt(wopt, 3)}，${api.fmt(smin, 3)} mm`]];
    }
    const n = s.jm.length, rm = this.rms(s.jm), rd = this.rms(s.jd), rt = this.rms(s.jt);
    if (p.pout >= 0.1 - 1e-6 && p.est === 2 && n >= 1000 && rt < rm) api.done("trim");
    const name = [api.T("平均分", "mean"), api.T("中位数", "median"), api.T("去掉最高最低", "trimmed")][p.est];
    return [[["模拟次数", "runs"], String(n)],
            [["所选方法", "chosen estimator"], name],
            [["平均分的均方根误差", "RMS error of the mean"], f(rm, 3)],
            [["中位数的均方根误差", "RMS error of the median"], f(rd, 3)],
            [["去掉最高最低的均方根误差", "RMS error of the trimmed mean"], f(rt, 3)]];
  },
  hist(api, arr, x0, x1, y0, y1, lo, hi, col) {
    const nb = 40, cnt = new Array(nb).fill(0), bw = (hi - lo) / nb;
    arr.forEach((v) => { const k = Math.floor((v - lo) / bw); if (k >= 0 && k < nb) cnt[k]++; });
    const mx = Math.max(1, ...cnt);
    cnt.forEach((c, k) => { if (c) { const hh = (y1 - y0) * c / mx; api.rect(x0 + (x1 - x0) * k / nb + 1, y1 - hh, (x1 - x0) / nb - 2, hh, col); } });
    api.line(x0, y1, x1, y1, api.css("--ink"), 1);
  },
  draw(api, s) {
    const { w, h } = api, p = api.p;
    if (api.scene === "dock") {
      // 上：AGV 与充电桩
      const wallX = w - 60, ay = 70, sc = (wallX - 120) / 200;
      api.rect(wallX, 20, 18, 100, api.css("--muted"));
      api.label(api.T("充电桩", "charger"), wallX + 9, 132, api.css("--muted"), 12, "center");
      const carX = wallX - this.T0 * sc;
      api.rect(carX - 120, ay - 20, 120, 40, api.css("--blue"), null, 6);
      if (s.last) {
        api.line(carX, ay - 8, carX + s.last[0] * sc, ay - 8, api.css("--red"), 2, [5, 3]);
        api.line(carX, ay + 8, carX + s.last[1] * sc, ay + 8, api.css("--amber"), 2, [5, 3]);
      }
      api.label(api.T("红：激光读数　金：超声读数", "red: laser   gold: ultrasonic"), 16, 20, api.css("--muted"), 12);
      // 下：误差直方图
      const y0 = 160, y1 = h - 30;
      this.hist(api, s.eA, 40, w / 2 - 10, y0, y1, -25, 25, api.css("--grid"));
      this.hist(api, s.e, w / 2 + 10, w - 20, y0, y1, -25, 25, api.css("--blue"));
      api.label(api.T("简单平均的误差（−25～25 mm）", "plain-average error (−25 to 25 mm)"), 40, y0 - 10, api.css("--muted"), 12);
      api.label(api.T(`权重 w = ${api.fmt(p.w, 2)} 的误差`, `error with weight w = ${api.fmt(p.w, 2)}`), w / 2 + 10, y0 - 10, api.css("--muted"), 12);
      return;
    }
    // 评委：最近一组分数
    const sc = s.last || [];
    sc.forEach((v, j) => {
      const x = 50 + j * (w - 100) / 8, top = 60, bh = 110;
      api.rect(x - 22, top, 44, bh, api.css("--panel"), api.css("--muted"), 6);
      api.label(api.fmt(v, 1), x, top + 40, Math.abs(v - this.J0) > 0.8 ? api.css("--red") : api.css("--ink"), 20, "center");
      api.label(api.T(`评委 ${j + 1}`, `Judge ${j + 1}`), x, top + 85, api.css("--muted"), 11, "center");
    });
    const y0 = 220, y1 = h - 30, arrs = [s.jm, s.jd, s.jt], third = (w - 60) / 3;
    const names = [api.T("平均分", "mean"), api.T("中位数", "median"), api.T("去掉最高最低", "trimmed")];
    arrs.forEach((a, k) => {
      this.hist(api, a, 30 + k * third, 30 + (k + 1) * third - 20, y0, y1, -1, 1, k === p.est ? api.css("--blue") : api.css("--grid"));
      api.label(names[k] + api.T("的误差（−1～1 分）", " error (−1 to 1)"), 30 + k * third, y0 - 10, api.css("--muted"), 12);
    });
    api.label(api.T("红色：离谱分数（偏差超过 0.8 分）", "red: wild scores (off by more than 0.8)"), 16, 20, api.css("--muted"), 12);
  },
});
