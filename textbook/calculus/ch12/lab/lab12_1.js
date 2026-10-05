// 实验 12.1 由速度数据求行驶距离（配 12.1、12.2 节）。“机器人”场景：AGV 每隔 Tₛ 秒报告一次速度（带噪声），
// 用左矩形、右矩形或梯形累加求距离，与真实距离比较；“黎曼和”场景：几个函数的左、右、梯形、中点和随 n 的变化。
WQ.lab({
  title: ["实验 12.1 由速度数据求行驶距离", "Lab 12.1 Distance from speed data"],
  goal: ["体会“距离 = 速度曲线下的面积”：用采样数据累加出距离，看采样间隔、累加方法和测量噪声各自怎样影响结果；在“黎曼和”场景中比较几种和的收敛快慢。",
         "Feel 'distance = area under the speed curve': add up sampled data, and see how the sampling interval, the summation rule and the noise each affect the result; compare how fast different sums converge."],
  scenes: [
    { id: "agv", robot: true, name: ["AGV 速度数据", "AGV speed data"], hide: ["f", "n"],
      problem: { title: ["机器人问题：只有速度读数，怎样知道走了多远？", "Robot problem: only speed readings — how far did it go?"],
                 text: ["AGV 加速到 1.2 m/s、匀速、再减速停下，全程 10 m。编码器每 Tₛ 秒报告一次速度。把“速度 × 时间间隔”加起来，就是距离的近似值。",
                        "The AGV accelerates to 1.2 m/s, cruises and stops after 10 m. The encoder reports the speed every Tₛ seconds. Adding 'speed × time step' approximates the distance."] } },
    { id: "fn", name: ["黎曼和", "Riemann sums"], hide: ["Ts", "sig", "te"],
      problem: { title: ["把区间分成 n 份，矩形的高取在哪里？", "Split into n pieces — where to take each height?"],
                 text: ["f(a) ≠ f(b) 时，左、右矩形和的误差约与 1/n 成正比；梯形和与中点和的误差约与 1/n² 成正比。试几个函数看看，sin x 有什么不同？",
                        "When f(a) ≠ f(b), left and right sums err like 1/n; trapezoid and midpoint sums like 1/n². Try a few functions — what is different for sin x?"] } },
  ],
  params: [
    { id: "rule", name: ["累加方法：1 左矩形，2 右矩形，3 梯形，4 中点", "Rule: 1 left, 2 right, 3 trapezoid, 4 midpoint"], min: 1, max: 4, step: 1, value: 1, digits: 0 },
    { id: "Ts", name: ["采样间隔 Tₛ", "Sampling interval Tₛ"], min: 0.05, max: 1, step: 0.05, value: 0.5, unit: "s", digits: 2 },
    { id: "sig", name: ["速度噪声的标准差", "Speed noise (std)"], min: 0, max: 0.1, step: 0.005, value: 0, unit: "m/s", digits: 3 },
    { id: "te", name: ["统计到时刻 t", "Sum up to time t"], min: 1, max: 11, step: 0.1, value: 4, unit: "s", digits: 1 },
    { id: "f", name: ["函数：1 x²（[0, 1]），2 x³（[0, 1]），3 sin x（[0, π]），4 exp(−x²)（[0, 2]）", "Function: 1 x² on [0, 1], 2 x³ on [0, 1], 3 sin x on [0, π], 4 exp(−x²) on [0, 2]"], min: 1, max: 4, step: 1, value: 2, digits: 0 },
    { id: "n", name: ["小区间个数 n", "Number of subintervals n"], min: 1, max: 200, step: 1, value: 8, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["真实曲线", "true curve"], color: "#222222" }, { name: ["读数 / 矩形", "readings / boxes"], color: "#1f77b4" }],
  tasks: [
    { id: "lr", robot: true, text: ["无噪声，Tₛ = 0.5 s，统计前 4 s：比较左矩形和与右矩形和，两者相差多少？（等于 v(4)·Tₛ）", "No noise, Tₛ = 0.5 s, first 4 s: compare the left and right sums. How far apart are they? (v(4)·Tₛ)"],
      demo: { scene: "agv", set: { rule: 2, Ts: 0.5, sig: 0, te: 4 }, wait: 1 } },
    { id: "trap", robot: true, text: ["无噪声，统计前 4 s，用梯形累加：Tₛ 取 0.25、0.4、0.5、0.8、1 s，哪些误差为 0？速度曲线的拐点 t = 2.4 s 恰好是采样时刻时会怎样？", "No noise, first 4 s, trapezoid rule: for Tₛ = 0.25, 0.4, 0.5, 0.8, 1 s, which errors are 0? What happens when the corner t = 2.4 s is a sampling instant?"],
      demo: { scene: "agv", set: { rule: 3, Ts: 0.8, sig: 0, te: 4 }, wait: 1 } },
    { id: "noise", robot: true, text: ["噪声取 0.05 m/s，Tₛ = 0.1 s，统计全程（t = 11 s）：误差有多大？把噪声加到 0.1 m/s 又如何？", "Noise 0.05 m/s, Tₛ = 0.1 s, the whole trip (t = 11 s): how big is the error? And with 0.1 m/s noise?"],
      demo: { scene: "agv", set: { rule: 3, Ts: 0.1, sig: 0.05, te: 11 }, wait: 1 } },
    { id: "mid", text: ["选 x³，用中点和，找出使误差小于 10⁻⁴ 的最小 n。", "For x³ with the midpoint rule, find the smallest n with error below 10⁻⁴."],
      demo: { scene: "fn", set: { f: 2, rule: 4, n: 36 }, wait: 1 } },
  ],
  think: ["噪声是随机的，有正有负。为什么累加很多个读数后，噪声造成的距离误差反而不太大？它大约随读数个数怎样增长？（第 48 章）",
          "Noise is random, positive and negative. Why does the distance error from noise stay fairly small after adding many readings? How does it grow with the number of readings? (Chapter 48)"],

  AGV: { a: 0.5, vm: 1.2, D: 10 },
  vtrue(t) {
    const { a, vm, D } = this.AGV, ta = vm / a, tc = (D - vm * ta) / vm, T = 2 * ta + tc;
    if (t <= 0 || t >= T) return 0;
    if (t < ta) return a * t;
    if (t < ta + tc) return vm;
    return a * (T - t);
  },
  xtrue(t) {   // 真实距离（速度曲线下的面积），分段的解析公式
    const { a, vm, D } = this.AGV, ta = vm / a, tc = (D - vm * ta) / vm, T = 2 * ta + tc;
    if (t <= 0) return 0;
    if (t < ta) return a * t * t / 2;
    if (t < ta + tc) return vm * ta / 2 + vm * (t - ta);
    if (t < T) return D - a * (T - t) ** 2 / 2;
    return D;
  },
  rng(seed) { return () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; },
  data(api) {
    const { Ts, sig, te } = api.p, m = Math.round(te / Ts), r = this.rng(12), out = [];
    for (let k = 0; k <= m; k++) {
      const t = k * Ts, u1 = Math.max(r(), 1e-12), u2 = r(), g = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
      const v = this.vtrue(t);
      out.push([t, v + (v > 0 ? sig * g : 0)]);
    }
    return out;
  },
  agvSum(api, D) {
    const r = api.p.rule === 4 ? 3 : api.p.rule, Ts = api.p.Ts;
    let s = 0;
    for (let k = 0; k + 1 < D.length; k++) s += Ts * (r === 1 ? D[k][1] : r === 2 ? D[k + 1][1] : (D[k][1] + D[k + 1][1]) / 2);
    return s;
  },
  FN(f) {
    return [[(x) => x * x, 0, 1, 1 / 3, "x²"], [(x) => x ** 3, 0, 1, 0.25, "x³"], [Math.sin, 0, Math.PI, 2, "sin x"],
            [(x) => Math.exp(-x * x), 0, 2, 0.8820813907624215, "exp(−x²)"]][f - 1];
  },
  fnSum(api) {
    const [f, a, b] = this.FN(api.p.f), n = api.p.n, h = (b - a) / n, r = api.p.rule;
    let s = 0;
    for (let k = 0; k < n; k++) {
      const x0 = a + k * h, x1 = x0 + h;
      s += h * (r === 1 ? f(x0) : r === 2 ? f(x1) : r === 3 ? (f(x0) + f(x1)) / 2 : f(x0 + h / 2));
    }
    return s;
  },
  reset() {},
  readouts(api) {
    const fe = (v) => (v === 0 ? "0" : Math.abs(v).toExponential(2));
    const rn = [api.T("左矩形", "left"), api.T("右矩形", "right"), api.T("梯形", "trapezoid"), api.T("中点", "midpoint")][api.p.rule - 1];
    if (api.scene === "agv") {
      const D = this.data(api), te = D[D.length - 1][0], est = this.agvSum(api, D), tr = this.xtrue(te), p = api.p;
      if (p.sig === 0 && Math.abs(p.Ts - 0.5) < 1e-9 && Math.abs(te - 4) < 1e-9 && (p.rule === 1 || p.rule === 2)) api.done("lr");
      if (p.sig === 0 && Math.abs(te - 4) < 1e-9 && p.rule === 3 && p.Ts >= 0.39 && Math.abs(2.4 / p.Ts - Math.round(2.4 / p.Ts)) < 1e-6 && Math.abs(est - tr) < 1e-9) api.done("trap");
      if (Math.abs(p.sig - 0.05) < 1e-9 && Math.abs(p.Ts - 0.1) < 1e-9 && te >= 10.95 && Math.abs(est - tr) < 0.1) api.done("noise");
      const L = (() => { let s = 0; for (let k = 0; k + 1 < D.length; k++) s += p.Ts * D[k][1]; return s; })();
      const R = (() => { let s = 0; for (let k = 0; k + 1 < D.length; k++) s += p.Ts * D[k + 1][1]; return s; })();
      return [[["累加方法", "Rule"], p.rule === 4 ? api.T("中点（数据没有中点值，改用梯形）", "midpoint (no midpoint data; trapezoid used)") : rn],
              [["读数个数", "Readings"], String(D.length)], [["统计到", "Up to"], te.toFixed(2) + " s"],
              [["估计的距离", "Estimated distance"], est.toFixed(4) + " m"], [["真实距离", "True distance"], tr.toFixed(4) + " m"],
              [["误差", "Error"], (est - tr).toFixed(4) + " m"], [["右矩形和 − 左矩形和", "Right − left"], (R - L).toFixed(4) + " m"]];
    }
    const [, , , ex, name] = this.FN(api.p.f), s = this.fnSum(api);
    if (api.p.f === 2 && api.p.rule === 4 && Math.abs(s - ex) < 1e-4 && api.p.n <= 36) api.done("mid");
    return [[["函数", "Function"], name], [["方法", "Rule"], rn], [["n", "n"], String(api.p.n)], [["和", "Sum"], s.toPrecision(10)],
            [["积分的准确值", "Exact integral"], ex.toPrecision(10)], [["误差", "Error"], fe(s - ex)], [["误差 × n²", "Error × n²"], (Math.abs(s - ex) * api.p.n ** 2).toPrecision(4)]];
  },
  draw(api) {
    const w = api.w, h = api.h, ink = api.css("--ink"), blue = api.css("--blue"), red = api.css("--red");
    const box = (G, x0, x1, y, col) => G.pts([[x0, 0], [x0, y], [x1, y], [x1, 0]], col, 1.2);
    if (api.scene === "agv") {
      const D = this.data(api), p = api.p, te = D[D.length - 1][0];
      const G = api.graph({ x: 60, y: 24, w: w - 80, h: h - 74, xmin: 0, xmax: 11, ymin: 0, ymax: 1.5, xlabel: "t / s", ylabel: "v / (m/s)" });
      G.axes();
      G.area((t) => this.vtrue(t), 0, te, "rgba(44,160,44,0.15)");
      G.fn((t) => this.vtrue(t), ink, 2);
      for (let k = 0; k + 1 < D.length; k++) {
        const [t0, v0] = D[k], [t1, v1] = D[k + 1];
        if (p.rule === 1) box(G, t0, t1, v0, blue); else if (p.rule === 2) box(G, t0, t1, v1, blue); else G.pts([[t0, 0], [t0, v0], [t1, v1], [t1, 0]], blue, 1.2);
      }
      G.dots(D, red, 3);
      G.vline(te, red);
      return;
    }
    const [f, a, b, , name] = this.FN(api.p.f), n = api.p.n, hh = (b - a) / n, r = api.p.rule;
    let ymax = 0; for (let i = 0; i <= 200; i++) ymax = Math.max(ymax, f(a + (b - a) * i / 200));
    const G = api.graph({ x: 60, y: 24, w: w - 80, h: h - 74, xmin: a, xmax: b, ymin: 0, ymax: ymax * 1.15, xlabel: "x", ylabel: name });
    G.axes();
    if (n <= 100) for (let k = 0; k < n; k++) {
      const x0 = a + k * hh, x1 = x0 + hh;
      if (r === 3) G.pts([[x0, 0], [x0, f(x0)], [x1, f(x1)], [x1, 0]], blue, 1);
      else box(G, x0, x1, r === 1 ? f(x0) : r === 2 ? f(x1) : f(x0 + hh / 2), blue);
    }
    G.fn(f, ink, 2.2);
  },
});
