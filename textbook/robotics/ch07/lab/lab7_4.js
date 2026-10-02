// 实验 7.4 数值微分与刚性（配 7.4 节）。
// 编码器：θ(t) = 2 sin 2πt rad，每转 2^bits 个计数，1 kHz 采样，读数向下取整；后向差商 (7.4.2) 或中心差商 (7.4.3)，跨度 n ms。
// 电机：电流环 + 速度环，ẋ = Ax + B（式 (7.4.8)），特征值约 −50.7 与 −35283 s⁻¹；显式欧拉法 (7.2.2) 或隐式欧拉法 (7.4.10)。
// 跑步手表：速度 v(t) = 3 + 0.5 sin(2πt/120) m/s，卫星定位每秒一次、带噪声；用跨度 S 秒的后向差商估计速度。
WQ.lab({
  title: ["实验 7.4 数值微分与刚性", "Lab 7.4 Numerical differentiation and stiffness"],
  goal: ["由编码器和卫星定位的读数求速度，找出最佳的差商跨度；用显式和隐式欧拉法仿真刚性的电机电流环。",
         "Get speed from encoder and satellite readings and find the best difference span; simulate a stiff motor current loop with explicit and implicit Euler."],
  scenes: [
    { id: "enc", robot: true, name: ["编码器测速", "Speed from an encoder"], hide: ["meth", "hS", "sigma", "span"],
      problem: { title: ["机器人问题：每毫秒一个计数值，怎样求角速度", "Robot problem: one count reading per millisecond — what is the speed"],
                 text: ["关节按 θ = 2 sin 2πt rad 运动。调节差商的跨度和编码器的分辨率，读出角速度估计的均方根误差。差商：0 后向，1 中心。",
                        "The joint moves as θ = 2 sin 2πt rad. Change the span and the encoder resolution; read the RMS error of the speed estimate. Difference: 0 backward, 1 central."] } },
    { id: "stiff", robot: true, name: ["电流环的刚性", "A stiff current loop"], hide: ["n", "bits", "dm", "sigma", "span"],
      problem: { title: ["机器人问题：仿真步长被电流环卡住", "Robot problem: the current loop limits the step"],
                 text: ["电流的时间常数约 28 µs，转速的时间常数约 20 ms。显式欧拉法要求 h ≤ 2/|λ快| ≈ 56.7 µs。方法：0 显式欧拉，1 隐式欧拉。",
                        "The time constant of the current is about 28 µs, that of the speed about 20 ms. Explicit Euler needs h ≤ 2/|λ_fast| ≈ 56.7 µs. Method: 0 explicit Euler, 1 implicit Euler."] } },
    { id: "watch", name: ["跑步手表测配速", "Pace on a running watch"], hide: ["n", "bits", "dm", "meth", "hS"],
      problem: { title: ["生活中的例子：手表上的配速为什么会乱跳", "Everyday example: why the pace on a watch jumps"],
                 text: ["手表每秒得到一次位置，误差有几米。用过去 S 秒的位置差估计速度：S 小则跳，S 大则慢。",
                        "The watch gets a position every second with an error of a few metres. Estimate the speed from the position change over the last S seconds: short S jumps, long S lags."] } },
  ],
  params: [
    { id: "n", name: ["差商跨度 h", "Span h"], min: 1, max: 60, step: 1, value: 1, unit: "ms", digits: 0 },
    { id: "bits", name: ["编码器分辨率（每转 2^bits 计数）", "Encoder resolution (2^bits counts/rev)"], min: 10, max: 20, step: 1, value: 14, unit: "bit", digits: 0 },
    { id: "dm", name: ["差商：0 后向，1 中心", "Difference: 0 backward, 1 central"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "meth", name: ["方法：0 显式，1 隐式", "Method: 0 explicit, 1 implicit"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "hS", name: ["步长 h", "Step h"], min: 10, max: 2000, step: 1, value: 50, unit: "µs", digits: 0 },
    { id: "sigma", name: ["定位误差 σ", "Position error σ"], min: 0.5, max: 5, step: 0.5, value: 2, unit: "m", digits: 1 },
    { id: "span", name: ["跨度 S", "Span S"], min: 1, max: 60, step: 1, value: 1, unit: "s", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["回放", "Play"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "best", robot: true, text: ["编码器 14 bit、后向差商：找到均方根误差最小的跨度。", "Encoder 14 bit, backward difference: find the span with the smallest RMS error."],
      demo: { scene: "enc", set: { bits: 14, dm: 0, n: 2 }, press: ["start"], wait: 4 } },
    { id: "central", robot: true, text: ["换成中心差商并调跨度，使误差不到后向差商最佳值的一半。", "Switch to the central difference and tune the span until the error is under half the best backward value."],
      demo: { scene: "enc", set: { bits: 14, dm: 1, n: 10 }, press: ["start"], wait: 4 } },
    { id: "explode", robot: true, text: ["显式欧拉法：把步长从 50 µs 加大，找到刚好发散的步长（不超过 70 µs）。", "Explicit Euler: raise the step from 50 µs and find one that just diverges (70 µs or less)."],
      demo: { scene: "stiff", set: { meth: 0, hS: 60 }, press: ["start"], wait: 4 } },
    { id: "implicit", robot: true, text: ["隐式欧拉法、h = 1 ms：仿真稳定，0.1 s 时转速与精确值相差不到 1 rad/s。", "Implicit Euler, h = 1 ms: stable, and at 0.1 s the speed is within 1 rad/s of the exact value."],
      demo: { scene: "stiff", set: { meth: 1, hS: 1000 }, press: ["start"], wait: 4 } },
    { id: "watch", text: ["跑步手表：定位误差 2 m，选一个跨度使速度的均方根误差小于 0.3 m/s。", "Running watch: position error 2 m; choose a span so that the RMS speed error is below 0.3 m/s."],
      demo: { scene: "watch", set: { sigma: 2, span: 15 }, press: ["start"], wait: 4 } },
  ],
  think: ["编码器分辨率提高 64 倍（从 14 bit 到 20 bit），最佳跨度和最小误差各变为多少？用式 (7.4.7) 估计后再验证。",
          "With 64 times the resolution (14 bit to 20 bit), what become the best span and the smallest error? Estimate with Eq. (7.4.7), then check."],

  // ---------- 编码器
  enc(api) {
    const A = 2, Om = 2 * Math.PI, q = 2 * Math.PI / Math.pow(2, api.p.bits), N = 2200;
    const th = [], w = [];
    for (let i = 0; i < N; i++) { const t = i / 1000; th.push(Math.floor(A * Math.sin(Om * t) / q) * q); w.push(A * Om * Math.cos(Om * t)); }
    const est = (n, central, i) => (central ? (th[i + n] - th[i - n]) / (2 * n / 1000) : (th[i] - th[i - n]) / (n / 1000));
    const rms = (n, central) => { let s = 0, c = 0; for (let i = 100; i < N - (central ? 2 * n : 0); i++) { const e = est(n, central, i) - w[i]; s += e * e; c++; } return Math.sqrt(s / c); };
    return { q, th, w, est, rms };
  },
  // ---------- 电机（式 (7.4.8)）
  A: [[-35333.333333, -1416.666667], [1250, -0.5]], B: [133333.333333, 0],
  stiffRun(meth, h, T) {
    const A = this.A, B = this.B, n = Math.round(T / h);
    let x = [0, 0]; const out = [[0, 0, 0]];
    let M = null;
    if (meth === 1) { const a = 1 - h * A[0][0], b = -h * A[0][1], c = -h * A[1][0], d = 1 - h * A[1][1], det = a * d - b * c; M = [[d / det, -b / det], [-c / det, a / det]]; }
    for (let k = 0; k < n; k++) {
      if (meth === 0) x = [x[0] + h * (A[0][0] * x[0] + A[0][1] * x[1] + B[0]), x[1] + h * (A[1][0] * x[0] + A[1][1] * x[1] + B[1])];
      else { const r = [x[0] + h * B[0], x[1] + h * B[1]]; x = [M[0][0] * r[0] + M[0][1] * r[1], M[1][0] * r[0] + M[1][1] * r[1]]; }
      out.push([(k + 1) * h * 1000, x[0], x[1]]);
      if (!isFinite(x[1]) || Math.abs(x[1]) > 1e8) break;
    }
    return out;
  },
  exactStiff() {
    if (!this._ex) {                       // 参照解：RK4，h = 5 µs（远在 RK4 的稳定上限 79 µs 以内）
      const A = this.A, B = this.B, h = 5e-6, f = (x) => [A[0][0] * x[0] + A[0][1] * x[1] + B[0], A[1][0] * x[0] + A[1][1] * x[1] + B[1]];
      let x = [0, 0]; const out = [[0, 0, 0]];
      for (let k = 0; k < 20000; k++) {
        const k1 = f(x), k2 = f([x[0] + h / 2 * k1[0], x[1] + h / 2 * k1[1]]), k3 = f([x[0] + h / 2 * k2[0], x[1] + h / 2 * k2[1]]), k4 = f([x[0] + h * k3[0], x[1] + h * k3[1]]);
        x = [x[0] + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]), x[1] + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])];
        out.push([(k + 1) * h * 1000, x[0], x[1]]);
      }
      this._ex = out;
    }
    return this._ex;
  },
  // ---------- 跑步手表
  gps(api) {
    let seed = 12345; const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };   // 帕克-米勒随机数，结果可重复
    const gauss = () => { const u = Math.max(1e-12, rnd()), v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
    const T = 600, x = [], v = [], z = [];
    for (let t = 0; t <= T; t++) { const xs = 3 * t - 0.5 * 120 / (2 * Math.PI) * (Math.cos(2 * Math.PI * t / 120) - 1); x.push(xs); v.push(3 + 0.5 * Math.sin(2 * Math.PI * t / 120)); z.push(xs + api.p.sigma * gauss()); }
    const S = api.p.span, est = [];
    let s2 = 0, c = 0;
    for (let t = 60; t <= T; t++) { const e = (z[t] - z[t - S]) / S; est.push([t, e]); s2 += (e - v[t]) ** 2; c++; }
    return { v, est, rms: Math.sqrt(s2 / c) };
  },

  reset(api, s) {
    s.play = 1; s.finished = false;
    if (api.scene === "enc") {
      const E = this.enc(api), c = api.p.dm === 1;
      s.E = E; s.rms = E.rms(api.p.n, c);
      let best = Infinity, nb = 1; for (let n = 1; n <= 60; n++) { const r = E.rms(n, false); if (r < best) { best = r; nb = n; } }
      s.bestB = best; s.nBest = nb;
    } else if (api.scene === "stiff") {
      s.run = this.stiffRun(api.p.meth, api.p.hS * 1e-6, 0.1); s.ex = this.exactStiff();
      const last = s.run[s.run.length - 1];
      s.diverged = !isFinite(last[2]) || Math.abs(last[2]) > 1000 || last[0] < 99.9;
      s.wEnd = last[2]; s.wEx = s.ex[s.ex.length - 1][2];
    } else s.G = this.gps(api);
  },
  start(api, s) { s.play = 0; s.finished = false; },
  update(dt, api, s) { s.play = Math.min(1, s.play + dt / 3); if (s.play >= 1) { s.finished = true; api.stop(); } },
  readouts(api, s) {
    if (api.scene === "enc") {
      if (s.finished && api.p.bits === 14 && api.p.dm === 0 && api.p.n === s.nBest) api.done("best");
      if (s.finished && api.p.bits === 14 && api.p.dm === 1 && s.rms < 0.5 * s.bestB) api.done("central");
      return [[["一个计数 q", "one count q"], api.fmt(s.E.q * 1e6, 1) + " µrad"], [["q / 1 ms", "q / 1 ms"], api.fmt(s.E.q * 1000, 3) + " rad/s"],
              [["角速度幅值", "speed amplitude"], "12.57 rad/s"], [["均方根误差", "RMS error"], api.fmt(s.rms, 4) + " rad/s"],
              [["后向差商的最佳跨度", "best backward span"], s.nBest + " ms"], [["后向差商的最小误差", "smallest backward error"], api.fmt(s.bestB, 4) + " rad/s"]];
    }
    if (api.scene === "stiff") {
      const h = api.p.hS;
      if (s.finished && api.p.meth === 0 && s.diverged && h <= 70) api.done("explode");
      if (s.finished && api.p.meth === 1 && h === 1000 && !s.diverged && Math.abs(s.wEnd - s.wEx) < 1) api.done("implicit");
      return [[["方法", "method"], api.p.meth === 0 ? api.T("显式欧拉", "explicit Euler") : api.T("隐式欧拉", "implicit Euler")],
              [["快模态的 h|λ|", "h|λ| of the fast mode"], api.fmt(h * 1e-6 * 35283, 3)],
              [["快模态放大因子", "fast-mode factor"], api.fmt(api.p.meth === 0 ? Math.abs(1 - h * 1e-6 * 35283) : 1 / (1 + h * 1e-6 * 35283), 4)],
              [["0.1 s 时转速", "speed at 0.1 s"], s.diverged ? api.T("发散", "diverged") : api.fmt(s.wEnd, 3) + " rad/s"],
              [["精确值", "exact"], api.fmt(s.wEx, 3) + " rad/s"], [["步数", "steps"], String(Math.round(0.1 / (h * 1e-6)))]];
    }
    if (s.finished && api.p.sigma === 2 && s.G.rms < 0.3) api.done("watch");
    const pace = (v) => { const sec = 1000 / v; return `${Math.floor(sec / 60)}′${String(Math.round(sec % 60)).padStart(2, "0")}″`; };
    return [[["速度的均方根误差", "RMS speed error"], api.fmt(s.G.rms, 3) + " m/s"], [["平均配速", "mean pace"], pace(3) + api.T(" /公里", " /km")],
            [["跨度 S", "span S"], api.p.span + " s"]];
  },
  draw(api, s) {
    const { w, h } = api, P = s.play;
    if (api.scene === "enc") {
      const i0 = 600, i1 = i0 + Math.max(2, Math.round(100 * P)), c = api.p.dm === 1, n = api.p.n;
      const tr = [], es = [];
      for (let i = 600; i < 700; i++) tr.push([i, s.E.w[i]]);
      for (let i = i0; i < i1; i++) es.push([i, s.E.est(n, c, i)]);
      api.plot(50, 16, w - 80, h - 50, [{ pts: tr, color: api.css("--muted") }, { pts: es, color: api.css("--accent") }],
        { xmin: 600, xmax: 700, ymin: -12, ymax: -1, xlabel: "t / ms", ylabel: "dθ/dt / (rad/s)" });
      api.label(api.T("灰线：真实角速度；彩线：差商估计", "grey: true speed; colour: estimate"), 60, h - 16, api.css("--muted"), 12);
      return;
    }
    if (api.scene === "stiff") {
      const k = Math.max(2, Math.round(s.run.length * P)), clip = (v) => Math.max(-50, Math.min(150, v));
      const ex = s.ex.filter((_, i) => i % 100 === 0).map((p) => [p[0], p[2]]);
      const nm = s.run.slice(0, k).map((p) => [p[0], clip(p[2])]);
      api.plot(50, 16, w - 80, h - 50, [{ pts: ex, color: api.css("--muted") }, { pts: nm, color: s.diverged ? api.css("--red") : api.css("--accent") }],
        { xmin: 0, xmax: 100, ymin: -50, ymax: 150, xlabel: "t / ms", ylabel: "ω / (rad/s)" });
      api.label(api.T("灰线：精确解", "grey: exact"), 60, h - 16, api.css("--muted"), 12);
      return;
    }
    const k = Math.max(2, Math.round(s.G.est.length * P)), tr = [];
    for (let t = 60; t <= 600; t += 2) tr.push([t, s.G.v[t]]);
    api.plot(50, 16, w - 80, h - 50, [{ pts: tr, color: api.css("--muted") }, { pts: s.G.est.slice(0, k), color: api.css("--accent") }],
      { xmin: 60, xmax: 600, ymin: 0, ymax: 6, xlabel: "t / s", ylabel: "v / (m/s)" });
    api.label(api.T("灰线：真实速度；彩线：手表估计的速度", "grey: true speed; colour: the watch's estimate"), 60, h - 16, api.css("--muted"), 12);
  },
});
