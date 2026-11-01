// 实验 19.6 减速器出厂检测的多元控制图（配 19.6 节）。
// 数据与本章程序（ch19/code/_qc.py）相同：六个检测项目，标准化单位下 z = L f + e（三个隐藏因素 + 测量误差），
// 用同一个线性同余发生器（乘数 48271，模 2³¹ − 1）和博克斯–穆勒变换。第一阶段 200 台（种子 20261101）估计均值、
// 标准差和相关矩阵；第二阶段 60 台（种子 20261102），从第 31 台起加上所选的故障偏移。
// 控制限：T² 与 T²ₖ 用式 (19.6.3)（N = 200，α = 0.0027，F 分位数由 scipy.stats.f 算出，列在 UCLK 里）；
// SPE 用杰克逊–穆德霍尔卡近似 (19.6.6)，z_α = 2.78215。
WQ.lab({
  title: ["实验 19.6 减速器出厂检测的多元控制图", "Lab 19.6 Multivariate control charts for gearbox final inspection"],
  goal: ["产品一台接一台下线，同时看 T² 图、主成分的 T²ₖ 与 SPE 图、单变量图；比较它们发现不同故障的能力，用贡献图诊断故障。",
         "Units leave the line one by one; watch the T² chart, the PCA-based T²ₖ and SPE charts and the univariate charts side by side; compare how they detect different faults and diagnose them with contributions."],
  scenes: [
    { id: "line", robot: true, name: ["出厂检测工位", "Final inspection station"],
      problem: { title: ["哪一台减速器不正常？", "Which gearbox is abnormal?"],
                 text: ["每台减速器测六个项目：输出轴直径、齿圈跳动、空载噪声、温升、振动、回差。六张单变量图各管一项，看不到项目之间的相关性；T² 图把六项合成一个数。第 31 台起混入一种故障，看哪张图先发现。",
                        "Each gearbox is tested on six items: shaft diameter, gear runout, noise, temperature rise, vibration, backlash. Six univariate charts each watch one item and miss the correlations; the T² chart combines all six. From unit 31 a fault creeps in: which chart notices first?"] } },
  ],
  params: [
    { id: "fault", name: ["故障（0 无，1 轴承磨损，2 齿轮偏心，3 装配过紧，4 用错润滑油）", "Fault (0 none, 1 bearing wear, 2 gear eccentricity, 3 tight assembly, 4 wrong oil)"], min: 0, max: 4, step: 1, value: 4, digits: 0 },
    { id: "mag", name: ["故障大小（倍数）", "Fault size (multiple)"], min: 0, max: 2, step: 0.1, value: 1, digits: 1 },
    { id: "k", name: ["主成分个数 k", "Number of components k"], min: 1, max: 5, step: 1, value: 3, digits: 0 },
  ],
  buttons: [{ id: "start", name: ["生产 60 台", "Produce 60 units"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "fa", robot: true, text: ["无故障（故障 = 0）时生产 60 台：T² 图和六张单变量图各误报几台？", "With no fault produce 60 units: how many false alarms do the T² and univariate charts give?"],
      demo: { scene: "line", set: { fault: 0, mag: 1, k: 3 }, press: ["start"], wait: 11 } },
    { id: "miss", robot: true, text: ["用错润滑油（故障 = 4，大小 ≥ 0.9）：T² 图比单变量图多发现多少台？", "Wrong oil (fault 4, size ≥ 0.9): how many more units does T² catch than the univariate charts?"],
      demo: { scene: "line", set: { fault: 4, mag: 1, k: 3 }, press: ["start"], wait: 11 } },
    { id: "diag", robot: true, text: ["齿轮偏心（故障 = 2，大小 ≥ 0.8）：贡献最大的项目是哪一个？", "Gear eccentricity (fault 2, size ≥ 0.8): which item contributes most?"],
      demo: { scene: "line", set: { fault: 2, mag: 1, k: 3 }, press: ["start"], wait: 11 } },
    { id: "bearing", robot: true, text: ["轴承磨损（故障 = 1，大小 ≥ 0.8）、k = 3：T²ₖ 与 SPE 哪个报警多？T² 与单变量图呢？与用错润滑油的结果比较。", "Bearing wear (fault 1, size ≥ 0.8), k = 3: does T²ₖ or SPE flag more? And T² versus the univariate charts? Compare with the wrong oil."],
      demo: { scene: "line", set: { fault: 1, mag: 1, k: 3 }, press: ["start"], wait: 11 } },
  ],
  think: ["用错润滑油时，每一项都不到 2σ，T² 却频频报警；轴承磨损的偏移更大，T² 却几乎不报警，单变量图反而报得多。用 (19.6.2) 和“故障方向落在哪几个主成分上”解释。",
          "With the wrong oil every item stays within 2σ yet T² keeps alarming; bearing wear shifts the items more, yet T² hardly reacts while the univariate charts do. Explain with (19.6.2) and which principal components the fault direction falls on."],

  L: [[0, 0, 0.6], [0.8, 0, 0], [0.6, 0.7, 0], [0.1, 0.85, 0.3], [0.5, 0.78, 0], [0.5, 0, -0.45]],
  MU: [0, 12, 60, 15, 1.2, 3], SIG: [3, 3, 1.5, 2, 0.25, 0.4],
  FAULTS: [[0, 0, 0, 0, 0, 0], [0, 0.3, 1.4, 1.1, 1.4, 0.1], [0, 1.6, 1.0, 0.2, 1.1, 0.8], [0, 0, 0.8, 1.6, 0.3, -1.3], [0, 0, -1, 1.8, -1, 0]],
  NAMES: [["无故障", "none"], ["轴承磨损", "bearing wear"], ["齿轮偏心", "gear eccentricity"], ["装配过紧", "tight assembly"], ["用错润滑油", "wrong oil"]],
  ITEMS: [["直径", "diam."], ["跳动", "runout"], ["噪声", "noise"], ["温升", "temp."], ["振动", "vib."], ["回差", "backlash"]],
  UCLK: [9.2762, 12.3123, 14.8616, 17.1987, 19.4161, 21.5579], ZA: 2.78215,
  lcg(seed) {
    let s = seed % 2147483647;
    const u = () => { s = (s * 48271) % 2147483647; return s / 2147483647; };
    return () => { const u1 = u(), u2 = u(); return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2); };
  },
  sample(n, seed, shift, start) {
    const g = this.lcg(seed), psi = this.L.map((r) => Math.sqrt(1 - r.reduce((a, x) => a + x * x, 0))), out = [];
    for (let k = 0; k < n; k++) {
      const f = [g(), g(), g()], e = [0, 1, 2, 3, 4, 5].map((j) => g() * psi[j]);
      const z = this.L.map((r, j) => r[0] * f[0] + r[1] * f[1] + r[2] * f[2] + e[j] + (shift && k >= start ? shift[j] : 0));
      out.push(z.map((v, j) => this.MU[j] + this.SIG[j] * v));
    }
    return out;
  },
  model(api) {
    if (this._m) return this._m;
    const X = this.sample(200, 20261101), n = X.length;
    const m = [0, 1, 2, 3, 4, 5].map((j) => X.reduce((a, r) => a + r[j], 0) / n);
    const sd = m.map((mj, j) => Math.sqrt(X.reduce((a, r) => a + (r[j] - mj) ** 2, 0) / (n - 1)));
    const Z = X.map((r) => r.map((x, j) => (x - m[j]) / sd[j]));
    const R = [0, 1, 2, 3, 4, 5].map((i) => [0, 1, 2, 3, 4, 5].map((j) => Z.reduce((a, r) => a + r[i] * r[j], 0) / (n - 1)));
    const E = api.la.eigSym(R), order = [5, 4, 3, 2, 1, 0];
    const lam = order.map((i) => E.values[i]), V = order.map((i) => E.vectors.map((row) => row[i]));   // V[i] = 第 i 个主成分方向
    this._m = { m, sd, lam, V };
    return this._m;
  },
  run(api) {
    const M = this.model(api), f = this.FAULTS[api.p.fault].map((x) => x * api.p.mag), k = api.p.k;
    const X = this.sample(60, 20261102, f, 30);
    const th = [1, 2, 3].map((q) => M.lam.slice(k).reduce((a, l) => a + l ** q, 0));
    const h0 = 1 - 2 * th[0] * th[2] / (3 * th[1] ** 2);
    const speLim = th[0] * Math.pow(this.ZA * Math.sqrt(2 * th[1] * h0 * h0) / th[0] + 1 + th[1] * h0 * (h0 - 1) / th[0] ** 2, 1 / h0);
    return X.map((x) => {
      const z = x.map((v, j) => (v - M.m[j]) / M.sd[j]);
      const t = M.V.map((v) => v.reduce((a, vi, j) => a + vi * z[j], 0));
      const T2 = t.reduce((a, ti, i) => a + ti * ti / M.lam[i], 0);
      const T2k = t.slice(0, k).reduce((a, ti, i) => a + ti * ti / M.lam[i], 0);
      const spe = t.slice(k).reduce((a, ti) => a + ti * ti, 0);
      const Rz = [0, 1, 2, 3, 4, 5].map((j) => M.V.reduce((a, v, i) => a + v[j] * t[i] / M.lam[i], 0));   // R⁻¹z
      const c = z.map((zj, j) => zj * Rz[j]);
      return { z, T2, T2k, spe, c, ucl: this.UCLK[5], uclk: this.UCLK[k - 1], speLim, ind: z.some((v) => Math.abs(v) > 3) };
    });
  },
  reset(api, s) { s.n = 60; s.ran = false; },
  start(api, s) { s.n = 0; s.ran = true; },
  update(dt, api, s) { s.n = Math.min(60, Math.floor(api.t * 6)); if (s.n >= 60) api.stop(); },
  readouts(api, s) {
    const R = this.run(api), f = api.fmt, n = s.n ?? 60, a = R.slice(0, Math.min(n, 30)), b = R.slice(30, Math.max(n, 30));
    const cnt = (arr, key) => arr.filter((r) => key === "ind" ? r.ind : key === "T2" ? r.T2 > r.ucl : key === "T2k" ? r.T2k > r.uclk : r.spe > r.speLim).length;
    const cb = [0, 1, 2, 3, 4, 5].map((j) => b.length ? b.reduce((acc, r) => acc + r.c[j], 0) / b.length : 0);
    const best = [0, 1, 2, 3, 4, 5].sort((i, j) => cb[j] - cb[i]);
    const nm = (i) => api.T(this.ITEMS[i][0], this.ITEMS[i][1]);
    if (s.ran && n >= 60) {
      if (api.p.fault === 0) api.done("fa");
      if (api.p.fault === 4 && api.p.mag >= 0.9 && cnt(b, "T2") >= cnt(b, "ind") + 8) api.done("miss");
      if (api.p.fault === 2 && api.p.mag >= 0.8 && best[0] === 1) api.done("diag");
      if (api.p.fault === 1 && api.p.k === 3 && api.p.mag >= 0.8 && cnt(b, "T2k") > cnt(b, "spe") && cnt(b, "ind") > cnt(b, "T2")) api.done("bearing");
    }
    const last = n > 0 ? R[n - 1] : null;
    return [[["故障", "Fault"], api.T(this.NAMES[api.p.fault][0], this.NAMES[api.p.fault][1]) + (api.p.fault ? "（" + f(api.p.mag, 1) + " 倍）" : "")],
            [["已生产", "Units produced"], String(n)],
            [["第 1–30 台报警：T² / 单变量", "Alarms, units 1–30: T² / univariate"], cnt(a, "T2") + " / " + cnt(a, "ind")],
            [["第 31–60 台报警：T² / 单变量", "Alarms, units 31–60: T² / univariate"], cnt(b, "T2") + " / " + cnt(b, "ind")],
            [["第 31–60 台报警：T²ₖ / SPE（k = " + api.p.k + "）", "Alarms, units 31–60: T²ₖ / SPE (k = " + api.p.k + ")"], cnt(b, "T2k") + " / " + cnt(b, "spe")],
            [["控制限：T² / T²ₖ / SPE", "Limits: T² / T²ₖ / SPE"], f(R[0].ucl, 2) + " / " + f(R[0].uclk, 2) + " / " + f(R[0].speLim, 2)],
            [["第 31 台起平均贡献最大的三项", "Largest mean contributions from unit 31"], b.length ? best.slice(0, 3).map((i) => nm(i) + " " + f(cb[i], 1)).join("，") : "—"],
            [["最近一台：T²", "Latest unit: T²"], last ? f(last.T2, 1) : "—"]];
  },
  draw(api, s) {
    const R = this.run(api), n = s.n ?? 60, { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink");
    const x0 = 46, x1 = w * 0.66, X = (i) => x0 + (x1 - x0) * (i + 0.5) / 60;
    const panel = (top, ht, title, series, lim, ymax) => {
      api.rect(x0, top, x1 - x0, ht, null, mu);
      const Y = (v) => top + ht - Math.min(v, ymax) / ymax * ht;
      api.line(x0, Y(lim), x1, Y(lim), api.css("--red"), 1, [5, 4]);
      api.line(X(29.5), top, X(29.5), top + ht, api.css("--amber"), 1);
      series.forEach(({ get, color }) => {
        for (let i = 0; i < n; i++) {
          const v = get(R[i]);
          if (i > 0) api.line(X(i - 1), Y(get(R[i - 1])), X(i), Y(v), color, 1);
          api.circle(X(i), Y(v), v > lim ? 4 : 2.5, v > lim ? api.css("--red") : color);
        }
      });
      api.label(title, x0 + 4, top + 12, mu, 11);
    };
    const H = (h - 40) / 3;
    panel(16, H - 8, api.T("T²（六项）与控制限", "T² (all six items) and limit"), [{ get: (r) => r.T2, color: api.css("--blue") }], R[0].ucl, 70);
    panel(16 + H, H - 8, api.T("T²ₖ / 控制限（蓝）与 SPE / 控制限（绿）", "T²ₖ / limit (blue) and SPE / limit (green)"),
          [{ get: (r) => r.T2k / r.uclk, color: api.css("--blue") }, { get: (r) => r.spe / r.speLim, color: api.css("--green") }], 1, 3.5);
    panel(16 + 2 * H, H - 8, api.T("单变量图：六项中最大的 |z|（±3σ）", "Univariate: largest |z| of the six (±3σ)"),
          [{ get: (r) => Math.max(...r.z.map(Math.abs)), color: ink }], 3, 6);
    // 右边：第 31 台起的平均贡献
    const b = R.slice(30, Math.max(n, 30)), bx = w * 0.72, bw = w * 0.25, top = 40, bh = h - 90;
    const cb = [0, 1, 2, 3, 4, 5].map((j) => b.length ? b.reduce((acc, r) => acc + r.c[j], 0) / b.length : 0);
    const cmax = Math.max(4, ...cb.map(Math.abs)), zeroY = top + bh * 0.8;
    api.line(bx, zeroY, bx + bw, zeroY, ink, 1);
    cb.forEach((c, j) => {
      const hh = c / cmax * bh * 0.75, xx = bx + j * bw / 6 + 4;
      api.rect(xx, hh >= 0 ? zeroY - hh : zeroY, bw / 6 - 8, Math.abs(hh), api.css("--amber"));
      api.label(api.T(this.ITEMS[j][0], this.ITEMS[j][1]), xx, zeroY + 16, mu, 10);
    });
    api.label(api.T("第 31 台起的平均贡献 cⱼ", "mean contribution cⱼ from unit 31"), bx, top - 14, mu, 11);
  },
});
