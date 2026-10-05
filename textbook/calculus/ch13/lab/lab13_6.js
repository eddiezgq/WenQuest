// 实验 13.6 陀螺仪积分与航向漂移（配 13.1、13.6 节）。“机器人”场景：AGV 的陀螺仪读数带零偏和噪声，积分成航向角，
// 看误差怎样随时间增长、静止标定零偏能消掉多少；“变上限积分”场景：Φ(x) = ∫₀ˣ f(t) dt 的图像与切线斜率。
WQ.lab({
  title: ["实验 13.6 陀螺仪积分与航向漂移", "Lab 13.6 Gyro integration and heading drift"],
  goal: ["把角速度积分成角度，体会“积分会把小的常值误差累积成大的偏差”：零偏使航向误差线性增长，随机噪声的误差约按 √t 增长；静止时标定零偏可以消掉大部分漂移。在“变上限积分”场景中验证 Φ′(x) = f(x)。",
         "Integrate angular rate into angle and see how integration accumulates small constant errors: a bias makes the heading error grow linearly, random noise roughly like √t; calibrating the bias at rest removes most of the drift. In the second scene, check Φ′(x) = f(x)."],
  scenes: [
    { id: "gyro", robot: true, name: ["AGV 陀螺仪", "AGV gyro"], hide: ["f", "x"],
      problem: { title: ["机器人问题：陀螺仪积分出的航向为什么越来越偏？", "Robot problem: why does the integrated heading drift?"],
                 text: ["AGV 用陀螺仪测转动的角速度，每 0.02 s 读一次，用梯形累加积分成航向角。它先静止若干秒（可用来标定零偏），然后行驶，每 20 s 转弯 90°。读数里有零偏（常值误差）和随机噪声。",
                        "The AGV's gyro reads the turn rate every 0.02 s; the readings are integrated (trapezoid rule) into heading. It first stands still (time usable for bias calibration), then drives, turning 90° every 20 s. Readings carry a bias and random noise."] } },
    { id: "phi", name: ["变上限积分", "Integral with variable upper limit"], hide: ["bias", "sig", "cal", "Tend"],
      problem: { title: ["面积对上限的变化率是什么？", "How fast does the area grow with the upper limit?"],
                 text: ["上图阴影是 Φ(x) = ∫₀ˣ f(t) dt，下图是 Φ 的图像和 x 处的切线。比较切线的斜率与 f(x)。",
                        "Top: the shaded area Φ(x) = ∫₀ˣ f(t) dt. Bottom: the graph of Φ with its tangent at x. Compare the slope with f(x)."] } },
  ],
  params: [
    { id: "bias", name: ["陀螺仪零偏", "Gyro bias"], min: 0, max: 0.2, step: 0.01, value: 0.05, unit: "°/s", digits: 2 },
    { id: "sig", name: ["噪声的标准差", "Noise (std)"], min: 0, max: 0.5, step: 0.05, value: 0, unit: "°/s", digits: 2 },
    { id: "cal", name: ["静止标定时间（0 表示不标定）", "Calibration time at rest (0 = none)"], min: 0, max: 10, step: 1, value: 0, unit: "s", digits: 0 },
    { id: "Tend", name: ["运行总时间", "Total time"], min: 20, max: 600, step: 10, value: 60, unit: "s", digits: 0 },
    { id: "f", name: ["函数：1 e^(−t²)，2 sin t，3 阶跃（t < 1 时为 1，之后为 2），4 t² − 2t", "Function: 1 e^(−t²), 2 sin t, 3 step (1 for t < 1, then 2), 4 t² − 2t"], min: 1, max: 4, step: 1, value: 2, digits: 0 },
    { id: "x", name: ["上限 x", "Upper limit x"], min: 0, max: 6, step: 0.05, value: 1, digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["未标定", "uncalibrated"], color: "#d62728" }, { name: ["标定后", "calibrated"], color: "#1f77b4" }],
  tasks: [
    { id: "bias", robot: true, text: ["零偏 0.05°/s，无噪声，不标定，运行 60 s：航向误差是多少度？它等于零偏 × 时间吗？", "Bias 0.05°/s, no noise, no calibration, 60 s: what is the heading error? Is it bias × time?"],
      demo: { scene: "gyro", set: { bias: 0.05, sig: 0, cal: 0, Tend: 60 }, wait: 1 } },
    { id: "cal", robot: true, text: ["零偏 0.05°/s，噪声 0.1°/s，运行 60 s：静止标定多久，能使标定后的航向误差小于 0.5°？", "Bias 0.05°/s, noise 0.1°/s, 60 s: how long a calibration at rest brings the calibrated heading error below 0.5°?"],
      demo: { scene: "gyro", set: { bias: 0.05, sig: 0.1, cal: 5, Tend: 60 }, wait: 1 } },
    { id: "walk", robot: true, text: ["零偏取 0，噪声 0.2°/s，运行时间取 150 s 和 600 s：误差是否按时间成正比增长？与 σ√(Tₛt) 比较。", "Zero bias, noise 0.2°/s, run 150 s and 600 s: does the error grow in proportion to time? Compare with σ√(Tₛt)."],
      demo: { scene: "gyro", set: { bias: 0, sig: 0.2, cal: 0, Tend: 600 }, wait: 1 } },
    { id: "max", text: ["选 sin t，移动上限 x，找出 Φ(x) 最大的位置。那里 f(x) 等于多少？", "Choose sin t and move x to where Φ(x) is largest. What is f(x) there?"],
      demo: { scene: "phi", set: { f: 2, x: 3.15 }, wait: 1 } },
  ],
  think: ["加速度计的零偏 b 使位置误差按 bt²/2 增长，比陀螺仪的航向误差增长得更快。为什么只靠惯性测量的导航系统必须定期用外部参照（GPS、二维码、激光雷达地图）校正？",
          "An accelerometer bias b makes the position error grow like bt²/2, faster than the gyro heading error. Why must a purely inertial navigation system be corrected regularly by external references (GPS, markers, lidar maps)?"],

  TS: 0.02,
  rng(seed) { return () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; },
  rate(t, cal) {   // 真实角速度（°/s）：静止 cal 秒后，每 20 s 转弯 90°，历时 2 s
    if (t < cal) return 0;
    const u = (t - cal) % 20;
    return u < 2 ? 45 * (1 - Math.cos(Math.PI * u)) : 0;
  },
  sim(api) {
    const p = api.p, key = [p.bias, p.sig, p.cal, p.Tend].join(",");
    if (this._key === key) return this._res;
    const Ts = this.TS, n = Math.round(p.Tend / Ts), r = this.rng(21);
    const t = [], th = [0], raw = [0], m = [];
    for (let k = 0; k <= n; k++) {
      const u1 = Math.max(r(), 1e-12), u2 = r(), g = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
      t.push(k * Ts);
      m.push(this.rate(k * Ts, p.cal) + p.bias + p.sig * g);
    }
    for (let k = 0; k < n; k++) {
      th.push(th[k] + (this.rate(t[k], p.cal) + this.rate(t[k + 1], p.cal)) / 2 * Ts);
      raw.push(raw[k] + (m[k] + m[k + 1]) / 2 * Ts);
    }
    const kc = Math.round(p.cal / Ts);
    let bh = 0;
    if (kc > 0) { for (let k = 0; k < kc; k++) bh += m[k]; bh /= kc; }
    const cal = raw.map((v, k) => v - bh * t[k]);
    this._key = key;
    this._res = { t, th, raw, cal, bh, kc };
    return this._res;
  },
  F(f) {
    return [[(t) => Math.exp(-t * t), "e^(−t²)"], [Math.sin, "sin t"], [(t) => (t < 1 ? 1 : 2), "step"], [(t) => t * t - 2 * t, "t² − 2t"]][f - 1];
  },
  Phi(f, x) {   // 中点和，n = 600
    const n = 600, h = x / n;
    let s = 0;
    for (let k = 0; k < n; k++) s += f((k + 0.5) * h);
    return s * h;
  },
  reset() { this._key = null; },
  readouts(api) {
    if (api.scene === "gyro") {
      const p = api.p, S = this.sim(api), N = S.t.length - 1;
      const eRaw = S.raw[N] - S.th[N], eCal = S.cal[N] - S.th[N];
      if (Math.abs(p.bias - 0.05) < 1e-9 && p.sig === 0 && p.cal === 0 && p.Tend === 60) api.done("bias");
      if (Math.abs(p.bias - 0.05) < 1e-9 && Math.abs(p.sig - 0.1) < 1e-9 && p.Tend === 60 && p.cal > 0 && Math.abs(eCal) < 0.5) api.done("cal");
      if (p.bias === 0 && p.sig >= 0.199 && p.Tend >= 600) api.done("walk");
      return [[["真实航向（终点）", "True heading (end)"], S.th[N].toFixed(2) + "°"],
              [["未标定的航向误差", "Error, uncalibrated"], eRaw.toFixed(3) + "°"],
              [["零偏 × 时间", "Bias × time"], (p.bias * p.Tend).toFixed(3) + "°"],
              [["标定得到的零偏", "Estimated bias"], S.kc > 0 ? S.bh.toFixed(4) + " °/s" : api.T("未标定", "none")],
              [["标定后的航向误差", "Error, calibrated"], S.kc > 0 ? eCal.toFixed(3) + "°" : "—"],
              [["噪声的随机游走 σ√(Tₛt)", "Noise random walk σ√(Tₛt)"], (p.sig * Math.sqrt(this.TS * p.Tend)).toFixed(3) + "°"]];
    }
    const [f, name] = this.F(api.p.f), x = api.p.x, ph = this.Phi(f, x), h = 1e-3;
    const slope = (this.Phi(f, x + h) - this.Phi(f, Math.max(x - h, 0))) / (x + h - Math.max(x - h, 0));
    if (api.p.f === 2 && Math.abs(x - Math.PI) < 0.06) api.done("max");
    return [[["函数", "Function"], api.p.f === 3 ? api.T("阶跃", "step") : name], [["x", "x"], x.toFixed(2)], [["Φ(x)", "Φ(x)"], ph.toFixed(4)],
            [["Φ 在 x 处的斜率（数值）", "Slope of Φ at x (numerical)"], slope.toFixed(4)], [["f(x)", "f(x)"], f(x).toFixed(4)]];
  },
  draw(api) {
    const w = api.w, h = api.h, ink = api.css("--ink"), blue = api.css("--blue"), red = api.css("--red"), muted = api.css("--muted");
    if (api.scene === "gyro") {
      const p = api.p, S = this.sim(api), N = S.t.length, step = Math.max(1, Math.floor(N / 1500));
      const er = [], ec = [];
      let lo = 0, hi = 0;
      for (let k = 0; k < N; k += step) {
        er.push([S.t[k], S.raw[k] - S.th[k]]);
        lo = Math.min(lo, er[er.length - 1][1]); hi = Math.max(hi, er[er.length - 1][1]);
        if (S.kc > 0) { ec.push([S.t[k], S.cal[k] - S.th[k]]); lo = Math.min(lo, ec[ec.length - 1][1]); hi = Math.max(hi, ec[ec.length - 1][1]); }
      }
      const pad = Math.max(0.2, (hi - lo) * 0.1);
      const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: p.Tend, ymin: lo - pad, ymax: hi + pad, xlabel: "t / s", ylabel: api.T("航向误差 / (°)", "heading error / (°)") });
      G.axes();
      G.hline(0, muted);
      G.fn((t) => p.bias * t, muted, 1, [4, 4]);
      G.pts(er, red, 1.6);
      if (S.kc > 0) { G.pts(ec, blue, 1.6); G.vline(p.cal, muted); }
      return;
    }
    const [f] = this.F(api.p.f), x = api.p.x, X1 = 6;
    let flo = 0, fhi = 0, plo = 0, phi = 0;
    const PH = [];
    for (let i = 0; i <= 120; i++) {
      const t = X1 * i / 120, v = f(t), q = this.Phi(f, t);
      flo = Math.min(flo, v); fhi = Math.max(fhi, v); plo = Math.min(plo, q); phi = Math.max(phi, q); PH.push([t, q]);
    }
    const H = (h - 90) / 2;
    const gTop = api.graph({ x: 70, y: 20, w: w - 90, h: H, xmin: 0, xmax: X1, ymin: flo - 0.1 * (fhi - flo + 0.1), ymax: fhi + 0.1 * (fhi - flo + 0.1), xlabel: "", ylabel: "f(t)" });
    gTop.axes();
    gTop.area(f, 0, Math.max(x, 1e-6), "rgba(31,119,180,0.25)");
    gTop.fn(f, ink, 2);
    gTop.vline(x, red);
    const gBot = api.graph({ x: 70, y: 50 + H, w: w - 90, h: H, xmin: 0, xmax: X1, ymin: plo - 0.1 * (phi - plo + 0.1), ymax: phi + 0.1 * (phi - plo + 0.1), xlabel: "x", ylabel: "Φ(x)" });
    gBot.axes();
    gBot.pts(PH, blue, 2);
    const p0 = this.Phi(f, x), k = f(x);
    gBot.seg(x - 0.8, p0 - 0.8 * k, x + 0.8, p0 + 0.8 * k, red, 1.6);
    gBot.point(x, p0, red);
  },
});
