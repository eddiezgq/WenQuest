// 实验 11.6 用正交函数逼近（配 11.6 节）。三个场景：方波 sign(x) 在 [−π, π] 上的傅里叶部分和；编码器偏心误差的傅里叶拟合
// （360 个等距角度，e = 40 sin θ + 15 cos θ − 12 sin 2θ + 6 cos 3θ + 噪声 2 角秒，固定种子）；|x| 在 [−1, 1] 上的勒让德级数。
// 系数都是投影：c_k = ⟨f, φ_k⟩/⟨φ_k, φ_k⟩，基函数两两正交，所以加一项不改变前面的系数。
WQ.lab({
  title: ["实验 11.6 用正交函数逼近", "Lab 11.6 Approximation by orthogonal functions"],
  goal: ["增加傅里叶级数或勒让德级数的项数，读出逼近误差；观察方波间断点附近的过冲；找出编码器误差需要几阶谐波；体会正交基下“系数一旦算出就不再改变”。",
         "Add terms to a Fourier or Legendre series and read the approximation error; watch the overshoot near the jump of a square wave; find how many harmonics the encoder error needs; see that with an orthogonal basis the coefficients, once computed, never change."],
  scenes: [
    { id: "square", name: ["方波的傅里叶级数", "Fourier series of a square wave"], hide: ["K", "d"],
      problem: { title: ["生活中的例子：开关信号", "Everyday example: an on–off signal"],
                 text: ["电机驱动器的 PWM 信号是方波。用正弦波去叠加它，需要多少项？间断处会发生什么？", "A motor driver's PWM signal is a square wave. How many sine waves does it take to build one, and what happens at the jumps?"] } },
    { id: "enc", robot: true, name: ["编码器误差的补偿", "Encoder error compensation"], hide: ["N", "d"],
      problem: { title: ["机器人问题：关节编码器的偏心误差", "Robot problem: eccentricity error of a joint encoder"],
                 text: ["码盘装得稍有偏心，读数误差随转角周期变化。用高精度编码器比对测了 360 个角度，要用几阶谐波来补偿？", "A slightly off-centre code disc gives an error that repeats every turn. 360 angles were compared with a reference encoder. How many harmonics are needed to compensate?"] } },
    { id: "leg", name: ["勒让德级数", "Legendre series"], hide: ["N", "K"],
      problem: { title: ["用多项式逼近有尖点的函数", "Polynomials for a function with a corner"],
                 text: ["|x| 在 x = 0 处有尖点。勒让德级数要多少项才能使最大误差小于 0.05？奇数次的项为什么都是零？", "|x| has a corner at 0. How many Legendre terms make the maximum error below 0.05? Why are all the odd terms zero?"] } },
  ],
  params: [
    { id: "N", name: ["最高谐波次数 N", "Highest harmonic N"], min: 1, max: 61, step: 2, value: 1, digits: 0 },
    { id: "K", name: ["谐波阶数 K", "Harmonics K"], min: 0, max: 8, step: 1, value: 0, digits: 0 },
    { id: "d", name: ["勒让德级数的最高次数 d", "Highest Legendre degree d"], min: 0, max: 40, step: 1, value: 0, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "gibbs", text: ["让方波逼近的均方根误差小于 0.1，读出此时间断点附近的过冲，与 N = 1 时比较。", "Make the RMS error of the square-wave approximation below 0.1; read the overshoot near the jump and compare with N = 1."],
      demo: { scene: "square", set: { N: 45 }, press: [] } },
    { id: "enc", robot: true, text: ["找出使补偿后的残差降到噪声水平（不超过 2.1 角秒）的最小谐波阶数 K。", "Find the smallest K that brings the residual down to the noise level (at most 2.1 arcsec)."],
      demo: { scene: "enc", set: { K: 3 }, press: [] } },
    { id: "leg", text: ["找出使 |x| 的勒让德级数最大误差小于 0.05 的最小次数 d。", "Find the smallest degree d for which the Legendre series of |x| has maximum error below 0.05."],
      demo: { scene: "leg", set: { d: 12 }, press: [] } },
  ],
  think: ["在编码器场景中，K 从 3 增大到 8，前三阶的系数变了吗？如果用的不是正交基（例如 θ 的多项式），增加项数时前面的系数会变吗？",
          "In the encoder scene, do the first three harmonics' coefficients change as K goes from 3 to 8? With a non-orthogonal basis (say, polynomials in θ) would earlier coefficients change when terms are added?"],

  P(k, x) { let p0 = 1, p1 = x; if (k === 0) return 1; for (let n = 1; n < k; n++) { const p2 = ((2 * n + 1) * x * p1 - n * p0) / (n + 1); p0 = p1; p1 = p2; } return p1; },
  reset(api, s) {
    if (api.scene === "square") {
      const N = api.p.N, xs = Array.from({ length: 2001 }, (_, i) => -Math.PI + 2 * Math.PI * i / 2000);
      s.pts = xs.map((x) => { let S = 0; for (let k = 1; k <= N; k += 2) S += 4 / (k * Math.PI) * Math.sin(k * x); return [x, S]; });
      s.rms = Math.sqrt(s.pts.reduce((t, [x, y]) => t + (Math.sign(x) - y) ** 2, 0) / s.pts.length);
      s.over = Math.max(...s.pts.map((p) => p[1])) - 1;
    } else if (api.scene === "enc") {
      if (!this.enc) {
        const r = api.calc.rng(116);
        this.enc = Array.from({ length: 360 }, (_, i) => { const t = i * Math.PI / 180; return [t, 40 * Math.sin(t) + 15 * Math.cos(t) - 12 * Math.sin(2 * t) + 6 * Math.cos(3 * t) + 2 * r.gauss()]; });
      }
      const K = api.p.K, D = this.enc, n = D.length;
      s.a0 = D.reduce((t, p) => t + p[1], 0) / n; s.ab = [];
      for (let k = 1; k <= K; k++) s.ab.push([2 / n * D.reduce((t, [th, e]) => t + e * Math.cos(k * th), 0), 2 / n * D.reduce((t, [th, e]) => t + e * Math.sin(k * th), 0)]);
      s.fit = D.map(([th]) => [th, s.ab.reduce((t, [a, b], i) => t + a * Math.cos((i + 1) * th) + b * Math.sin((i + 1) * th), s.a0)]);
      s.res = Math.sqrt(D.reduce((t, [, e], i) => t + (e - s.fit[i][1]) ** 2, 0) / n);
      s.raw = Math.sqrt(D.reduce((t, [, e]) => t + e * e, 0) / n);
      s.Kmin = null;
      for (let k = 0; k <= 8; k++) {
        let a0 = D.reduce((t, p) => t + p[1], 0) / n, ab = [];
        for (let j = 1; j <= k; j++) ab.push([2 / n * D.reduce((t, [th, e]) => t + e * Math.cos(j * th), 0), 2 / n * D.reduce((t, [th, e]) => t + e * Math.sin(j * th), 0)]);
        const rr = Math.sqrt(D.reduce((t, [th, e]) => t + (e - ab.reduce((u, [a, b], i) => u + a * Math.cos((i + 1) * th) + b * Math.sin((i + 1) * th), a0)) ** 2, 0) / n);
        if (rr <= 2.1) { s.Kmin = k; break; }
      }
    } else {
      const d = api.p.d, xs = Array.from({ length: 4001 }, (_, i) => -1 + i / 2000), h = 1 / 2000;
      s.c = [];
      for (let k = 0; k <= d; k++) {   // c_k = (2k + 1)/2 ∫ |x| P_k dx, Simpson's rule
        let I = 0; xs.forEach((x, i) => { const wgt = i === 0 || i === xs.length - 1 ? 1 : i % 2 ? 4 : 2; I += wgt * Math.abs(x) * this.P(k, x); });
        s.c.push((2 * k + 1) / 2 * I * h / 3);
      }
      s.pts = xs.filter((_, i) => i % 4 === 0).map((x) => [x, s.c.reduce((t, ck, k) => t + ck * this.P(k, x), 0)]);
      s.maxerr = Math.max(...s.pts.map(([x, y]) => Math.abs(y - Math.abs(x))));
      s.dmin = null;
      let cs = [];
      for (let k = 0; k <= 40 && s.dmin === null; k++) {
        let I = 0; xs.forEach((x, i) => { const wgt = i === 0 || i === xs.length - 1 ? 1 : i % 2 ? 4 : 2; I += wgt * Math.abs(x) * this.P(k, x); });
        cs.push((2 * k + 1) / 2 * I * h / 3);
        const err = Math.max(...xs.filter((_, i) => i % 4 === 0).map((x) => Math.abs(cs.reduce((t, ck, j) => t + ck * this.P(j, x), 0) - Math.abs(x))));
        if (err < 0.05) s.dmin = k;
      }
    }
  },
  readouts(api, s) {
    const sc = api.scene;
    if (sc === "square" && s.pts) {
      if (s.rms < 0.1) api.done("gibbs");
      return [[["项数（奇次谐波 1, 3, …, N）", "Terms (odd harmonics 1, 3, …, N)"], String((api.p.N + 1) / 2)],
              [["均方根误差", "RMS error"], api.fmt(s.rms, 4)], [["间断点附近的过冲", "Overshoot near the jump"], api.fmt(s.over, 4)],
              [["N = 1 时的过冲", "Overshoot at N = 1"], "0.2732"]];
    }
    if (sc === "enc" && s.fit) {
      if (api.p.K === s.Kmin) api.done("enc");
      const amp = s.ab.map(([a, b], i) => `${i + 1}: ${api.fmt(Math.hypot(a, b), 2)}`).join(", ");
      return [[["补偿前的误差（均方根）", "Error before (RMS)"], api.fmt(s.raw, 2) + api.T(" 角秒", " arcsec")],
              [["补偿后的残差（均方根）", "Residual after (RMS)"], api.fmt(s.res, 2) + api.T(" 角秒", " arcsec")],
              [["各阶谐波的幅值", "Amplitude of each harmonic"], amp || "—"],
              [["系数 a₁, b₁（不随 K 改变）", "a₁, b₁ (do not change with K)"], s.ab.length ? api.fmt(s.ab[0][0], 3) + ", " + api.fmt(s.ab[0][1], 3) : "—"]];
    }
    if (sc === "leg" && s.c) {
      if (api.p.d === s.dmin) api.done("leg");
      return [[["最大误差", "Maximum error"], api.fmt(s.maxerr, 4)],
              [["系数 c₀ … c₄", "Coefficients c₀ … c₄"], s.c.slice(0, 5).map((x) => api.fmt(x, 4)).join(", ")],
              [["奇数次系数的最大绝对值", "Largest odd coefficient"], api.fmt(Math.max(0, ...s.c.filter((_, k) => k % 2).map(Math.abs)), 6)]];
    }
    return [];
  },
  draw(api, s) {
    const { w, h } = api, ink = api.css("--ink"), red = api.css("--red"), muted = api.css("--muted"), blue = api.css("--blue");
    if (api.scene === "square" && s.pts) {
      const P = api.plot(40, 30, w - 70, h - 70, [{ pts: [[-Math.PI, -1], [0, -1], [0, 1], [Math.PI, 1]], color: muted }, { pts: s.pts, color: red }],
                         { xmin: -Math.PI, xmax: Math.PI, ymin: -1.4, ymax: 1.4, xlabel: "x", ylabel: "f(x)" });
      api.label(api.T("灰：方波  红：傅里叶部分和", "grey: square wave  red: partial sum"), 44, 22, ink, 12);
      return;
    }
    if (api.scene === "enc" && s.fit) {
      const P = api.plot(50, 30, w - 80, h - 70, [{ pts: s.fit.map(([t, y]) => [t * 180 / Math.PI, y]), color: red }],
                         { xmin: 0, xmax: 360, ymin: -60, ymax: 60, xlabel: api.T("转角 / °", "angle / °"), ylabel: api.T("误差 / 角秒", "error / arcsec") });
      this.enc.forEach(([t, e], i) => { if (i % 2 === 0) api.circle(P.X(t * 180 / Math.PI), P.Y(e), 2, muted); });
      this.enc.forEach(([t, e], i) => { if (i % 2 === 0) api.circle(P.X(t * 180 / Math.PI), P.Y(e - s.fit[i][1]), 1.6, blue); });
      api.label(api.T("灰点：测量  红：K 阶拟合  蓝点：补偿后的残差", "grey: measured  red: fit with K harmonics  blue: residual"), 54, 22, ink, 12);
      return;
    }
    if (api.scene === "leg" && s.pts) {
      api.plot(40, 30, w - 70, h - 70, [{ pts: [[-1, 1], [0, 0], [1, 1]], color: muted }, { pts: s.pts, color: red }],
               { xmin: -1, xmax: 1, ymin: -0.2, ymax: 1.1, xlabel: "x", ylabel: "f(x)" });
      api.label(api.T("灰：|x|  红：勒让德级数", "grey: |x|  red: Legendre series"), 44, 22, ink, 12);
    }
  },
});
