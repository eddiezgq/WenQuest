// 实验 19.7 电机的时间常数：从数据里读出来（配 19.1、19.4、19.7 节）。“机器人”场景：maxon RE 40（样本参数）通电后的
// 转速数据，由含绕组电感和摩擦的模型（两个一阶方程）生成并加测量噪声；读者调模型 ω∞(1 − e^(−t/τ)) 的 τ 去吻合数据，
// 与理论值 τ = R(J + J_L)/k²、63.2% 法和最小二乘法比较。“RC 低通”场景：正弦输入下输出的幅值比与相位滞后。
WQ.lab({
  title: ["实验 19.7 电机的时间常数：从数据里读出来", "Lab 19.7 A motor's time constant, read from data"],
  goal: ["由一次阶跃响应的测量数据读出一阶系统的时间常数，比较几种读法的稳健性；看负载惯量和电压怎样影响时间常数；再看一阶系统对正弦输入的作用：低通滤波与截止频率。",
         "Read the time constant of a first-order system from measured step-response data and compare how robust different methods are; see how load inertia and voltage affect it; then see what a first-order system does to a sinusoid: low-pass filtering and the cutoff frequency."],
  scenes: [
    { id: "motor", robot: true, name: ["电机阶跃响应", "Motor step response"], hide: ["Rk", "f"],
      problem: { title: ["机器人问题：样本上的“机械时间常数”是怎样测出来的？装上负载后变成多少？", "Robot problem: how is the catalogue's 'mechanical time constant' measured, and what is it with a load?"],
                 text: ["maxon RE 40（R = 1.13 Ω，k = 60.3 mN·m/A，转子 137 g·cm²）接通电压 V，编码器每隔一段时间测一次转速（带噪声）。调整模型 ω∞(1 − e^(−t/τ)) 中的 τ，使曲线穿过数据点；轴上可以加一个飞轮（负载惯量 J_L）。",
                        "A maxon RE 40 (R = 1.13 Ω, k = 60.3 mN·m/A, rotor 137 g·cm²) is switched on at voltage V and an encoder samples its speed (with noise). Adjust τ in the model ω∞(1 − e^(−t/τ)) until the curve runs through the data; a flywheel (load inertia J_L) can be added to the shaft."] } },
    { id: "rc", name: ["RC 低通滤波器", "RC low-pass filter"], hide: ["JL", "V", "noise", "tg"],
      problem: { title: ["一阶系统对正弦信号做了什么？", "What does a first-order system do to a sine wave?"],
                 text: ["电阻 R 与 1 μF 电容组成低通滤波器，τ = RC。输入幅值为 1 的正弦信号，看输出的幅值和相位。频率低时几乎原样通过，频率高时被削弱。",
                        "A resistor R and a 1 μF capacitor form a low-pass filter with τ = RC. Feed in a unit sine wave and watch the output's amplitude and phase: low frequencies pass almost unchanged, high frequencies are attenuated."] } },
  ],
  params: [
    { id: "JL", name: ["负载惯量 J_L（飞轮）", "Load inertia J_L (flywheel)"], min: 0, max: 1500, step: 1, value: 0, unit: "g·cm²", digits: 0 },
    { id: "V", name: ["电压 V", "Voltage V"], min: 12, max: 48, step: 1, value: 48, unit: "V", digits: 0 },
    { id: "noise", name: ["测量噪声（标准差）", "Measurement noise (std. dev.)"], min: 0, max: 20, step: 0.5, value: 5, unit: "rad/s", digits: 1 },
    { id: "tg", name: ["模型的时间常数 τ（你的估计）", "Model time constant τ (your estimate)"], min: 1, max: 60, step: 0.01, value: 10, unit: "ms", digits: 2 },
    { id: "Rk", name: ["电阻 R（C = 1 μF）", "Resistance R (C = 1 μF)"], min: 1, max: 100, step: 0.1, value: 10, unit: "kΩ", digits: 1 },
    { id: "f", name: ["输入频率 f", "Input frequency f"], min: 0.5, max: 200, step: 0.1, value: 5, unit: "Hz", digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["测量数据 / 输入", "data / input"], color: "#7a868d" }, { name: ["模型 / 输出", "model / output"], color: "#1f77b4" }, { name: ["63.2% 线", "63.2% line"], color: "#d62728" }],
  tasks: [
    { id: "read", robot: true, text: ["空载（J_L = 0，48 V）：调 τ 使模型曲线与数据吻合（与最小二乘结果相差 3% 以内）。与样本的 4.28 ms 比较。", "No load (J_L = 0, 48 V): adjust τ until the model fits the data (within 3% of the least-squares value). Compare with the catalogue's 4.28 ms."],
      demo: { scene: "motor", set: { JL: 0, V: 48, noise: 5, tg: 4.27 }, wait: 1 } },
    { id: "load", robot: true, text: ["装上转动惯量为转子 3 倍的飞轮（J_L ≈ 411 g·cm²）：时间常数变为多少？与 R(J + J_L)/k² 比较。", "Add a flywheel of three times the rotor inertia (J_L ≈ 411 g·cm²): what is the time constant now? Compare with R(J + J_L)/k²."],
      demo: { scene: "motor", set: { JL: 411, V: 48, noise: 5, tg: 17.0 }, wait: 1 } },
    { id: "volt", robot: true, text: ["空载，把电压降到 24 V 或更低，再读一次时间常数。它变了吗？稳态转速呢？", "No load, lower the voltage to 24 V or less and read the time constant again. Has it changed? And the steady speed?"],
      demo: { scene: "motor", set: { JL: 0, V: 24, noise: 5, tg: 4.27 }, wait: 1 } },
    { id: "cut", text: ["RC 滤波器（R = 10 kΩ）：输入频率取多少，输出幅值是输入的 0.707 倍？这时相位滞后多少？", "RC filter (R = 10 kΩ): at what input frequency is the output amplitude 0.707 of the input? What is the phase lag then?"],
      demo: { scene: "rc", set: { Rk: 10, f: 15.9 }, wait: 1 } },
  ],
  think: ["把噪声加大到 20 rad/s。63.2% 法、最小二乘法给出的时间常数还可靠吗？如果只用切线法（t = 0 处的斜率）会怎样？",
          "Raise the noise to 20 rad/s. Are the 63.2% and least-squares estimates still reliable? What would the tangent method (the slope at t = 0) give?"],

  R: 1.13, K: 0.0603, J: 137e-7, L: 0.33e-3, I0: 0.0686,
  rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; },
  data(p) {   // 缓存：参数不变就不重算
    const key = [p.JL, p.V, p.noise].join(",");
    if (this._key === key) return this._d;
    const J = this.J + p.JL * 1e-7, tauT = this.R * J / this.K ** 2, Tw = 8 * tauT, n = 120, Ts = Tw / n;
    const Tf = this.K * this.I0, f = (w, i) => [(this.K * i - Tf) / J, (p.V - this.R * i - this.K * w) / this.L];
    let w = 0, i = 0, t = 0;
    const dt = 2e-6, ts = [], ws = [], u = this.rng(19);
    const gauss = () => Math.sqrt(-2 * Math.log(u() + 1e-12)) * Math.cos(2 * Math.PI * u());
    for (let k = 0; k <= n; k++) {
      const tk = k * Ts;
      while (t < tk - 1e-12) {   // RK4
        const h = Math.min(dt, tk - t);
        const a = f(w, i), b = f(w + h / 2 * a[0], i + h / 2 * a[1]), c = f(w + h / 2 * b[0], i + h / 2 * b[1]), d = f(w + h * c[0], i + h * c[1]);
        w += h / 6 * (a[0] + 2 * b[0] + 2 * c[0] + d[0]); i += h / 6 * (a[1] + 2 * b[1] + 2 * c[1] + d[1]); t += h;
        if (w < 0) w = 0;   // 摩擦不会使它倒转
      }
      ts.push(tk); ws.push(w + p.noise * gauss());
    }
    let s = 0, m = 0;
    ts.forEach((tk, k) => { if (tk > 0.8 * Tw) { s += ws[k]; m++; } });
    const wend = s / m;
    let j = ws.findIndex((v) => v > 0.632 * wend);
    if (j < 1) j = 1;
    const t63 = ts[j - 1] + (0.632 * wend - ws[j - 1]) / (ws[j] - ws[j - 1]) * (ts[j] - ts[j - 1]);
    const S = (tau) => ws.reduce((acc, v, k) => acc + (v - wend * (1 - Math.exp(-ts[k] / tau))) ** 2, 0);
    let lo = 0.2 * tauT, hi = 3 * tauT;
    for (let it = 0; it < 80; it++) { const c1 = hi - 0.618 * (hi - lo), c2 = lo + 0.618 * (hi - lo); if (S(c1) < S(c2)) hi = c2; else lo = c1; }
    const tls = (lo + hi) / 2;
    this._key = key;
    this._d = { ts, ws, wend, t63, tls, tauT, Tw, S };
    return this._d;
  },
  reset() {},
  readouts(api) {
    const p = api.p;
    if (api.scene === "motor") {
      const D = this.data(p), tg = p.tg / 1000, ok = Math.abs(tg - D.tls) / D.tls < 0.03;
      if (ok && p.JL === 0 && p.V === 48) api.done("read");
      if (ok && p.JL >= 400 && p.JL <= 420) api.done("load");
      if (ok && p.JL === 0 && p.V <= 24) api.done("volt");
      const rms = (tau) => Math.sqrt(D.S(tau) / D.ts.length);
      return [[["理论值 τ = R(J + J_L)/k²", "theory τ = R(J + J_L)/k²"], (D.tauT * 1000).toFixed(2) + " ms"],
              [["63.2% 法", "63.2% method"], (D.t63 * 1000).toFixed(2) + " ms"],
              [["最小二乘法", "least squares"], (D.tls * 1000).toFixed(2) + " ms"],
              [["你的 τ 与最小二乘之差", "your τ vs least squares"], ((tg / D.tls - 1) * 100).toFixed(1) + " %"],
              [["残差均方根：你的 τ / 最小二乘", "residual RMS: yours / least squares"], rms(tg).toFixed(1) + " / " + rms(D.tls).toFixed(1) + " rad/s"],
              [["稳态转速（数据末尾的平均）", "steady speed (mean of the last data)"], D.wend.toFixed(0) + " rad/s"]];
    }
    const tau = p.Rk * 1e3 * 1e-6, wt = 2 * Math.PI * p.f * tau, amp = 1 / Math.sqrt(1 + wt * wt), ph = Math.atan(wt) * 180 / Math.PI;
    if (Math.abs(p.Rk - 10) < 1e-9 && Math.abs(amp - Math.SQRT1_2) < 0.01) api.done("cut");
    return [[["时间常数 τ = RC", "time constant τ = RC"], (tau * 1000).toFixed(1) + " ms"],
            [["截止频率 f_c = 1/(2πτ)", "cutoff f_c = 1/(2πτ)"], (1 / (2 * Math.PI * tau)).toFixed(2) + " Hz"],
            [["ωτ", "ωτ"], wt.toFixed(3)],
            [["幅值比 1/√(1 + (ωτ)²)", "amplitude ratio 1/√(1 + (ωτ)²)"], amp.toFixed(3)],
            [["相位滞后 arctan(ωτ)", "phase lag arctan(ωτ)"], ph.toFixed(1) + "°"],
            [["时间上落后", "time lag"], (Math.atan(wt) / (2 * Math.PI * p.f) * 1000).toFixed(2) + " ms"]];
  },
  draw(api) {
    const p = api.p, w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), muted = api.css("--muted");
    if (api.scene === "motor") {
      const D = this.data(p), ymax = Math.max(900, D.wend * 1.15);
      const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: D.Tw * 1000, ymin: -60, ymax, xlabel: "t / ms", ylabel: "ω / (rad/s)" });
      G.axes();
      G.hline(0.632 * D.wend, red, [5, 4]);
      G.hline(D.wend, muted, [2, 4]);
      G.dots(D.ts.map((t, k) => [t * 1000, D.ws[k]]), muted, 2.5);
      G.fn((t) => D.wend * (1 - Math.exp(-t / p.tg)), blue, 2.5);
      G.vline(p.tg, blue, [3, 4]);
      G.text("τ", p.tg + 0.01 * D.Tw * 1000, -40, blue, 13);
      return;
    }
    const tau = p.Rk * 1e-3, per = 1 / p.f, T = 4 * per;
    const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: T * 1000, ymin: -1.2, ymax: 1.2, xlabel: "t / ms", ylabel: api.T("电压（归一化）", "voltage (normalized)") });
    G.axes();
    G.fn((t) => Math.sin(2 * Math.PI * p.f * t / 1000), muted, 1.5);
    const pts = [];
    let y = 0, t = 0;
    const n = 2000, dt = T / n;
    for (let k = 0; k <= n; k++) {   // 精确离散化：零阶保持输入的一阶系统
      pts.push([t * 1000, y]);
      const u = Math.sin(2 * Math.PI * p.f * (t + dt / 2)), a = Math.exp(-dt / tau);
      y = a * y + (1 - a) * u; t += dt;
    }
    G.pts(pts, blue, 2.5);
    const amp = 1 / Math.sqrt(1 + (2 * Math.PI * p.f * tau) ** 2);
    G.hline(amp, blue, [3, 4]); G.hline(-amp, blue, [3, 4]);
  },
});
