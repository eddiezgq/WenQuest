// 实验 23.6 级数的部分和：收敛快慢与加速（配 23.1、23.3、23.4、23.6 节）。“零件弹跳”场景：机械臂松开零件，零件在托盘上弹跳，
// 落地时刻是几何级数的部分和；看余项怎样随弹跳次数减小、恢复系数怎样决定停稳的时间。“求 π”场景：莱布尼茨级数、Σ1/k²、梅钦公式的
// 部分和，以及反复平均、艾特肯加速、余项的积分修正（欧拉–麦克劳林）的效果。
WQ.lab({
  title: ["实验 23.6 级数的部分和：收敛快慢与加速", "Lab 23.6 Partial sums: how fast they converge, and how to speed them up"],
  goal: ["由部分和看级数的收敛：几何级数的余项按比例缩小，可以准确算出；慢级数要用加速方法或换一个快级数。用几种办法求 π，比较达到同样精度所需的项数。",
         "Watch convergence through partial sums: a geometric series' remainder shrinks by a fixed ratio and can be computed exactly; a slow series needs acceleration or a faster replacement. Compute π several ways and compare how many terms each needs for the same accuracy."],
  scenes: [
    { id: "bounce", robot: true, name: ["零件弹跳", "Bouncing part"], hide: ["s", "m", "n"],
      problem: { title: ["机器人问题：松开零件后要等多久，它才在托盘上停稳？", "Robot problem: after releasing a part, how long until it settles in the tray?"],
                 text: ["机械臂在高度 h 处松开夹爪，零件落到托盘上弹跳，每次弹起的速度是落下速度的 e 倍（恢复系数）。弹跳无穷多次，各次的飞行时间构成几何级数。下一次抓取要等零件停稳，等多久？",
                        "The arm opens its gripper at height h; the part falls into the tray and bounces, each rebound speed being e times the impact speed (coefficient of restitution). It bounces infinitely often, and the flight times form a geometric series. How long must the next grasp wait?"] } },
    { id: "pi", name: ["求 π", "Computing π"], hide: ["e", "h", "k"],
      problem: { title: ["同样几十项，怎样把 π 算得更准？", "With a few dozen terms, how can π be computed more accurately?"],
                 text: ["级数 1：π = 4(1 − 1/3 + 1/5 − …)（莱布尼茨）；级数 2：π = √(6 Σ1/k²)；级数 3：π = 16 arctan(1/5) − 4 arctan(1/239)（梅钦）。方法 1 直接求和；2 反复取相邻部分和的平均；3 反复用艾特肯 Δ² 加速；4 加上余项的积分修正（只对级数 2）。",
                        "Series 1: π = 4(1 − 1/3 + 1/5 − …) (Leibniz); series 2: π = √(6 Σ1/k²); series 3: π = 16 arctan(1/5) − 4 arctan(1/239) (Machin). Method 1 plain sum; 2 repeatedly average neighbouring partial sums; 3 repeated Aitken Δ²; 4 add the integral correction for the remainder (series 2 only)."] } },
  ],
  params: [
    { id: "h", name: ["松开的高度 h", "Release height h"], min: 50, max: 500, step: 10, value: 200, unit: "mm", digits: 0 },
    { id: "e", name: ["恢复系数 e", "Coefficient of restitution e"], min: 0.1, max: 0.95, step: 0.01, value: 0.6, digits: 2 },
    { id: "k", name: ["已发生的弹跳次数 n（部分和的项数）", "Bounces so far n (terms in the partial sum)"], min: 0, max: 30, step: 1, value: 3, digits: 0 },
    { id: "s", name: ["级数：1 莱布尼茨，2 Σ1/k²，3 梅钦", "Series: 1 Leibniz, 2 Σ1/k², 3 Machin"], min: 1, max: 3, step: 1, value: 1, digits: 0 },
    { id: "m", name: ["方法：1 直接，2 反复平均，3 艾特肯，4 积分修正", "Method: 1 plain, 2 averaging, 3 Aitken, 4 integral correction"], min: 1, max: 4, step: 1, value: 1, digits: 0 },
    { id: "n", name: ["所用的项数 n", "Terms used n"], min: 1, max: 200, step: 1, value: 10, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["零件 / 直接求和", "part / plain sum"], color: "#1f77b4" }, { name: ["余项 / 加速后", "remainder / accelerated"], color: "#d62728" }],
  tasks: [
    { id: "rem", robot: true, text: ["h = 200 mm、e = 0.6：至少要等几次弹跳之后，余下的弹跳时间之和才小于 10 ms？与公式 2t₀eⁿ⁺¹/(1 − e) 核对。",
                                     "h = 200 mm, e = 0.6: after how many bounces is the total remaining bounce time below 10 ms? Check with 2t₀eⁿ⁺¹/(1 − e)."],
      demo: { scene: "bounce", set: { h: 200, e: 0.6, k: 9 }, wait: 1 } },
    { id: "cycle", robot: true, text: ["节拍要求：从松开到停稳不超过 0.5 s（h = 200 mm）。恢复系数最大可以是多少？（托盘要垫多软的材料？）",
                                       "Cycle requirement: from release to rest within 0.5 s (h = 200 mm). What is the largest admissible coefficient of restitution? (How soft must the tray lining be?)"],
      demo: { scene: "bounce", set: { h: 200, e: 0.42, k: 3 }, wait: 1 } },
    { id: "slow", text: ["莱布尼茨级数直接求和：要多少项，π 的误差才小于 0.01？", "Leibniz series, plain sum: how many terms make the error in π below 0.01?"],
      demo: { scene: "pi", set: { s: 1, m: 1, n: 100 }, wait: 1 } },
    { id: "aitken", text: ["莱布尼茨级数用反复艾特肯加速：只用不超过 15 项，使误差小于 10⁻¹⁰。直接求和要多少项才能这样准？",
                           "Leibniz series with repeated Aitken: with at most 15 terms make the error below 10⁻¹⁰. How many plain terms would that take?"],
      demo: { scene: "pi", set: { s: 1, m: 3, n: 15 }, wait: 1 } },
    { id: "tail", text: ["级数 2 加上余项的积分修正：用不超过 30 项，使 π 的误差小于 10⁻⁸。", "Series 2 with the integral correction: with at most 30 terms make the error in π below 10⁻⁸."],
      demo: { scene: "pi", set: { s: 2, m: 4, n: 30 }, wait: 1 } },
    { id: "machin", text: ["梅钦公式直接求和：几项就使误差小于 10⁻¹²？", "Machin's formula, plain sum: how few terms give an error below 10⁻¹²?"],
      demo: { scene: "pi", set: { s: 3, m: 1, n: 9 }, wait: 1 } },
  ],
  think: ["几何级数的余项可以准确算出，所以弹跳的总时间可以“预先知道”。真实的零件弹跳几次后会滚动、晃动，恢复系数也随速度变化。物理引擎遇到很小的弹跳速度时直接让它停下，为什么？",
          "A geometric remainder can be computed exactly, so the total bounce time is 'known in advance'. Real parts start rolling and rocking after a few bounces, and e varies with speed. Why do physics engines simply stop a bounce when the rebound speed is very small?"],

  G: 9.81,
  partial(p) {   // 第 1..n 个部分和（π 的近似）
    const n = p.n, out = [];
    let S = 0;
    for (let k = 1; k <= n; k++) {
      if (p.s === 1) { S += (k % 2 ? 1 : -1) / (2 * k - 1); out.push(4 * S); }
      else if (p.s === 2) { S += 1 / (k * k); out.push(S); }
      else { const j = k - 1, sg = j % 2 ? -1 : 1; S += sg * (16 * Math.pow(0.2, 2 * j + 1) - 4 * Math.pow(1 / 239, 2 * j + 1)) / (2 * j + 1); out.push(S); }
    }
    return out;
  },
  toPi(p, v) { return p.s === 2 ? Math.sqrt(6 * v) : v; },
  accel(p, s) {   // 用前 n 个部分和得到的最好估计（π 的近似）
    const n = s.length;
    if (p.m === 2) { let a = s.slice(); while (a.length > 1) { const b = []; for (let i = 0; i + 1 < a.length; i++) b.push((a[i] + a[i + 1]) / 2); a = b; } return this.toPi(p, a[0]); }
    if (p.m === 3) {
      let a = s.slice();
      while (a.length >= 3) {
        const b = [];
        for (let i = 0; i + 2 < a.length; i++) { const d1 = a[i + 2] - a[i + 1], d2 = a[i + 1] - a[i], den = d1 - d2; b.push(den === 0 ? a[i + 2] : a[i + 2] - d1 * d1 / den); }
        if (b.some((v) => !isFinite(v))) break;
        a = b;
      }
      return this.toPi(p, a[a.length - 1]);
    }
    if (p.m === 4 && p.s === 2) return this.toPi(p, s[n - 1] + 1 / n - 1 / (2 * n * n) + 1 / (6 * n * n * n));
    return this.toPi(p, s[n - 1]);
  },
  bounce(p) {
    const h = p.h / 1000, t0 = Math.sqrt(2 * h / this.G), e = p.e;
    const total = t0 * (1 + e) / (1 - e);
    let S = t0;
    for (let k = 1; k <= p.k; k++) S += 2 * t0 * Math.pow(e, k);
    return { t0, total, S, rem: total - S, remF: 2 * t0 * Math.pow(e, p.k + 1) / (1 - e) };
  },
  reset() {},
  readouts(api) {
    const p = api.p;
    if (api.scene === "bounce") {
      const B = this.bounce(p);
      if (p.h === 200 && Math.abs(p.e - 0.6) < 1e-9 && B.rem < 0.01 && 2 * B.t0 * Math.pow(p.e, p.k) / (1 - p.e) >= 0.01) api.done("rem");
      if (p.h === 200 && B.total <= 0.5 && this.bounce(Object.assign({}, p, { e: p.e + 0.01 })).total > 0.5) api.done("cycle");
      return [[["第一次落地 t₀ = √(2h/g)", "first impact t₀ = √(2h/g)"], (B.t0 * 1000).toFixed(1) + " ms"],
              [["总时间 t₀(1 + e)/(1 − e)", "total time t₀(1 + e)/(1 − e)"], (B.total * 1000).toFixed(1) + " ms"],
              [["前 n 次弹跳后的部分和", "partial sum after n bounces"], (B.S * 1000).toFixed(1) + " ms"],
              [["余项 2t₀eⁿ⁺¹/(1 − e)", "remainder 2t₀eⁿ⁺¹/(1 − e)"], (B.remF * 1000).toFixed(2) + " ms"],
              [["第 n 次弹起的高度", "height of bounce n"], (p.h * Math.pow(p.e, 2 * p.k)).toPrecision(3) + " mm"]];
    }
    const s = this.partial(p), plain = this.toPi(p, s[s.length - 1]), best = this.accel(p, s);
    const e1 = Math.abs(plain - Math.PI), e2 = Math.abs(best - Math.PI);
    if (p.s === 1 && p.m === 1 && e1 < 0.01) api.done("slow");
    if (p.s === 1 && p.m === 3 && p.n <= 15 && e2 < 1e-10) api.done("aitken");
    if (p.s === 2 && p.m === 4 && p.n <= 30 && e2 < 1e-8) api.done("tail");
    if (p.s === 3 && p.m === 1 && e1 < 1e-12) api.done("machin");
    const note = p.m === 4 && p.s !== 2 ? api.T("（积分修正只用于级数 2，这里等于直接求和）", " (integral correction is for series 2 only; same as plain here)") : "";
    return [[["直接求和的 π 近似", "plain estimate of π"], plain.toFixed(15)],
            [["直接求和的误差", "plain error"], e1.toExponential(2)],
            [["所选方法的 π 近似", "chosen method's estimate"], best.toFixed(15) + note],
            [["所选方法的误差", "chosen method's error"], (e2 === 0 ? "< 1e-16" : e2.toExponential(2))]];
  },
  draw(api) {
    const p = api.p, w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), muted = api.css("--muted");
    if (api.scene === "bounce") {
      const B = this.bounce(p), Tm = Math.max(B.total * 1.15, 0.2);
      const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: Tm * 1000, ymin: -20, ymax: p.h * 1.1, xlabel: "t / ms", ylabel: api.T("高度 / mm", "height / mm") });
      G.axes();
      const pts = [];
      for (let i = 0; i <= 60; i++) { const t = B.t0 * i / 60; pts.push([t * 1000, p.h - 0.5 * this.G * t * t * 1000]); }
      let tl = B.t0, v = this.G * B.t0;
      const lands = [[tl * 1000, 0]];
      for (let k = 1; k <= 40; k++) {
        v *= p.e; const tf = 2 * v / this.G;
        for (let i = 0; i <= 40; i++) { const t = tf * i / 40; pts.push([(tl + t) * 1000, (v * t - 0.5 * this.G * t * t) * 1000]); }
        tl += tf; if (k <= p.k) lands.push([tl * 1000, 0]);
        if (tf < 1e-5) break;
      }
      G.pts(pts, blue, 2);
      G.dots(lands, red, 4);
      G.vline(B.total * 1000, red, [5, 4]);
      G.vline(B.S * 1000, muted, [2, 4]);
      G.text(api.T("停稳", "at rest"), B.total * 1000 + 4, p.h * 0.9, red, 12);
      return;
    }
    const all = this.partial(Object.assign({}, p, { n: 200 }));
    const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 1, xmax: Math.max(p.n, 10), ymin: -16, ymax: 1, xlabel: api.T("项数 n", "terms n"), ylabel: "log₁₀|error|" });
    G.axes();
    const lg = (v) => Math.max(-16, Math.log10(Math.max(Math.abs(v - Math.PI), 1e-17)));
    const P = [], A = [];
    for (let n = 1; n <= p.n; n++) {
      const s = all.slice(0, n);
      P.push([n, lg(this.toPi(p, s[n - 1]))]);
      A.push([n, lg(this.accel(p, s))]);
    }
    G.pts(P, blue, 2); G.dots(P, blue, 2.5);
    if (p.m > 1) { G.pts(A, red, 2); G.dots(A, red, 2.5); }
    G.hline(Math.log10(2.2e-16), muted, [3, 4]);
  },
});
