// 实验 39.4 数字滤波（配 39.4 节）。信号与算例 39.4.1 相同：0.2 s 内平滑升到 30 N 的夹紧力 + 50 Hz、2 N 的工频干扰
// + 标准差 0.3 N 的随机噪声，采样 1 kHz（噪声用固定种子生成，每次相同）。滤波器：滑动平均（式 (39.4.1)）或一阶低通（式 (39.4.3)）。
WQ.lab({
  title: ["实验 39.4 数字滤波", "Lab 39.4 Digital filtering"],
  goal: ["调节滤波器，看残余波动和延迟怎样此消彼长，并找出能完全消除 50 Hz 干扰的滑动平均。",
         "Tune the filters, watch residual ripple trade against delay, and find the moving average that removes 50 Hz completely."],
  scenes: [
    { id: "grip", robot: true, name: ["夹爪夹紧力", "Gripper clamping force"],
      problem: { title: ["机器人问题：稳而不慢的力读数", "Robot problem: a force reading that is steady but quick"],
                 text: ["夹紧力的读数在跳。滤波能让它稳定，但滤得太狠，控制器就跟不上力的变化。",
                        "The clamping-force reading jumps. Filtering steadies it, but too much and the controller lags behind."] } },
    { id: "scale", name: ["电子秤的显示", "A kitchen scale's display"],
      problem: { title: ["生活中的例子：电子秤为什么要等一下", "Everyday example: why a scale takes a moment"],
                 text: ["放上东西，数字跳几下才稳定：秤宁可慢一点，也要给出稳定的读数。",
                        "Put something on and the digits settle after a moment: the scale prefers steady to fast."] } },
  ],
  params: [
    { id: "kind", name: ["滤波器：0 滑动平均 / 1 一阶低通", "Filter: 0 moving average / 1 first-order low-pass"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "N", name: ["滑动平均点数 N", "Moving-average length N"], min: 1, max: 60, step: 1, value: 5, unit: "", digits: 0 },
    { id: "fc", name: ["一阶低通截止频率 f_c", "Low-pass cut-off f_c"], min: 1, max: 100, step: 1, value: 30, unit: "Hz", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "n20", robot: true, text: ["滑动平均：找出能完全消除 50 Hz 干扰的最小 N。", "Moving average: the smallest N that removes 50 Hz completely."],
      demo: { scene: "grip", set: { kind: 0, N: 20 }, press: [] } },
    { id: "lp", robot: true, text: ["一阶低通：把残余波动降到 0.5 N 以下，读出此时的延迟。", "Low-pass: bring the residual ripple below 0.5 N and read the delay."],
      demo: { scene: "grip", set: { kind: 1, fc: 15 }, press: [] } },
    { id: "slow", text: ["一阶低通：截止频率降到 2 Hz，延迟超过 50 ms。", "Low-pass at 2 Hz: the delay exceeds 50 ms."],
      demo: { scene: "scale", set: { kind: 1, fc: 2 }, press: [] } },
  ],
  think: ["同样把残余波动降到 0.3 N 以下，哪种滤波器的延迟更短？为什么？", "To get the ripple below 0.3 N, which filter has the shorter delay, and why?"],

  fs: 1000,
  signal() {
    if (this._sig) return this._sig;
    let seed = 39;
    const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
    const n = 600, t = [], clean = [], x = [];
    for (let k = 0; k < n; k++) {
      const tt = k / this.fs, u = Math.min(1, tt / 0.2), f = 30 * u * u * (3 - 2 * u);
      const g = Math.sqrt(-2 * Math.log(rnd() + 1e-12)) * Math.cos(2 * Math.PI * rnd());
      t.push(tt); clean.push(f); x.push(f + 2 * Math.sin(2 * Math.PI * 50 * tt) + 0.3 * g);
    }
    this._sig = { t, clean, x };
    return this._sig;
  },
  filtered(api) {
    const { x } = this.signal(), y = [];
    if (api.p.kind === 0) {
      const N = api.p.N; let acc = 0;
      for (let k = 0; k < x.length; k++) { acc += x[k] - (k >= N ? x[k - N] : 0); y.push(acc / N); }
    } else {
      const a = 1 - Math.exp(-2 * Math.PI * api.p.fc / this.fs); let v = 0;
      for (let k = 0; k < x.length; k++) { v += a * (x[k] - v); y.push(v); }
    }
    return y;
  },
  stats(api, y) {
    const { t, clean } = this.signal();
    let s = 0, m = 0;
    for (let k = 350; k < y.length; k++) { const e = y[k] - clean[k]; s += e; m++; }
    const mean = s / m; let v = 0;
    for (let k = 350; k < y.length; k++) { const e = y[k] - clean[k] - mean; v += e * e; }
    const res = Math.sqrt(v / (m - 1));
    const k15 = clean.findIndex((c) => c >= 15), j15 = y.findIndex((c) => c >= 15);
    return { res, lag: (j15 - k15) / this.fs * 1000 };
  },
  reset(api, s) {},
  readouts(api, s) {
    const y = this.filtered(api), st = this.stats(api, y);
    if (api.scene === "grip" && api.p.kind === 0 && api.p.N === 20) api.done("n20");
    if (api.scene === "grip" && api.p.kind === 1 && st.res < 0.5) api.done("lp");
    if (api.scene === "scale" && api.p.kind === 1 && api.p.fc <= 2 && st.lag > 50) api.done("slow");
    return [[["滤波器", "filter"], api.p.kind === 0 ? `N = ${api.p.N}` : `f_c = ${api.p.fc} Hz`],
            [["残余波动（稳定段）", "residual ripple (steady part)"], api.fmt(st.res, 3) + " N"],
            [["上升段延迟（到 15 N）", "delay on the rise (at 15 N)"], api.fmt(st.lag, 0) + " ms"]];
  },
  draw(api, s) {
    const { w, h } = api, { t, clean, x } = this.signal(), y = this.filtered(api);
    const x0 = 40, x1 = w - 16, yb = h - 26, yt = 16;
    const X = (tt) => x0 + (x1 - x0) * tt / 0.6, Y = (v) => yb - (yb - yt) * (v + 3) / 37;
    api.line(x0, Y(0), x1, Y(0), api.css("--line"), 1);
    const c = api.ctx, poly = (arr, col, lw) => { c.beginPath(); arr.forEach((v, k) => (k ? c.lineTo(X(t[k]), Y(v)) : c.moveTo(X(t[k]), Y(v)))); c.strokeStyle = col; c.lineWidth = lw; c.stroke(); };
    poly(x, api.css("--muted"), 0.8);
    poly(clean, api.css("--ink"), 1);
    poly(y, api.scene === "scale" ? api.css("--amber") : api.css("--blue"), 2.4);
    api.label("0", 22, Y(0), api.css("--muted"), 11); api.label("30 N", 6, Y(30), api.css("--muted"), 11);
    api.label(api.lang() === "en" ? "grey: readings  black: true force  colour: filtered" : "灰：原始读数  黑：真实的力  彩色：滤波后", x0, h - 8, api.css("--muted"), 12);
  },
});
