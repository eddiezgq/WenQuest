// 实验 1.2 速度表与里程表：AGV 的编码器数据（配 1.2 节）。AGV 匀加速出发，x(t) = 0.25 t²（m），0 ≤ t ≤ 4 s；
// 编码器每 Ts 读一次，读数加 ±e 的均匀误差（随机数种子固定）并取整到 0.1 mm。相邻读数相减再除以 Ts 得平均速度，
// 把速度乘 Ts 累加回去得位置。“汽车行程”场景：一段 10 分钟的行程，速度表与里程表互相恢复。
WQ.lab({
  title: ["实验 1.2 速度表与里程表：AGV 的编码器数据", "Lab 1.2 Speedometer and odometer: AGV encoder data"],
  goal: ["由位置读数相减求速度，再把速度累加回位置；改变采样周期和读数误差，看求出的速度怎样变化。",
         "Subtract position readings to get speed, then add the speeds back to get position; change the sampling period and the reading error and watch the speed estimate."],
  scenes: [
    { id: "agv", robot: true, name: ["AGV 编码器", "AGV encoder"], hide: [],
      problem: { title: ["机器人问题：编码器只报位置，速度从哪里来？", "Robot problem: the encoder reports position only; where does speed come from?"],
                 text: ["AGV 匀加速出发，编码器每隔一个采样周期报告一次走过的距离。用相邻读数求出第 2 秒时的速度，再把速度加回去，看能否恢复出 4 秒走过的距离。",
                        "The AGV starts with constant acceleration; the encoder reports the distance every sampling period. Find the speed at t = 2 s from neighbouring readings, then add the speeds back and recover the distance after 4 s."] } },
    { id: "car", name: ["生活中的例子：汽车行程", "Everyday example: a car trip"], hide: ["e"],
      problem: { title: ["生活中的例子：坏了一个表", "Everyday example: one broken meter"],
                 text: ["一段 10 分钟的行程，速度时快时慢。若里程表坏了，用速度表的记录能算出走了多远吗？若速度表坏了，用里程表能算出速度吗？",
                        "A 10-minute trip at varying speed. If the odometer breaks, can the speedometer record give the distance? If the speedometer breaks, can the odometer give the speed?"] } },
  ],
  params: [
    { id: "Ts", name: ["采样周期 Ts", "Sampling period Ts"], min: 2, max: 200, step: 1, value: 20, unit: "ms", digits: 0 },
    { id: "e", name: ["读数误差 ±e", "Reading error ±e"], min: 0, max: 5, step: 0.1, value: 0.5, unit: "mm", digits: 1 },
    { id: "t0", name: ["查看时刻 t₀（占总时间的比例）", "Time t₀ (fraction of the run)"], min: 0, max: 1, step: 0.005, value: 0.5, digits: 3 },
  ],
  buttons: [{ id: "start", name: ["行驶", "Drive"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["真实值", "true"], color: "#d62728" }, { name: ["由数据求出", "from data"], color: "#1f77b4" }],
  tasks: [
    { id: "speed", robot: true, text: ["把 t₀ 调到 2 s（比例 0.5），读出由数据求出的速度，使它与真实速度相差不到 0.08 m/s。", "Set t₀ to 2 s (fraction 0.5) and read the speed from the data, within 0.08 m/s of the true speed."],
      demo: { scene: "agv", set: { Ts: 20, e: 0.5, t0: 0.5 }, press: [], wait: 1 } },
    { id: "back", robot: true, text: ["按“行驶”跑完 4 s，确认把速度累加回去得到的距离与编码器最后的读数一致（相差小于 1 mm）。", "Press Drive and run the full 4 s; check that the speeds added back give the final encoder reading (within 1 mm)."],
      demo: { scene: "agv", set: { Ts: 20, e: 0.5 }, press: ["start"], wait: 16 } },
    { id: "noise", robot: true, text: ["保持读数误差不小于 0.5 mm，把采样周期调小，使由数据求出的速度最大误差超过 0.15 m/s。误差为什么变大了？", "Keep the reading error at least 0.5 mm and shorten the period until the largest speed error exceeds 0.15 m/s. Why did it grow?"],
      demo: { scene: "agv", set: { e: 1, Ts: 4 }, press: [], wait: 1 } },
  ],
  think: ["采样周期变短，速度估计反而更差；把速度加回位置时，误差却没有被放大。为什么“相减”放大误差，“相加”不放大？", "A shorter period makes the speed estimate worse, yet adding speeds back to position does not magnify the error. Why does subtracting magnify errors while adding does not?"],

  // the true motion of each scene: position x(t) and speed v(t) in SI units; car: km and km/h shown
  truth(api) {
    if (api.scene === "car") {   // 10 min = 600 s; speed in m/s: 0 → 20 → 12 → 25 → 0
      const knots = [[0, 0], [60, 14], [180, 20], [260, 12], [360, 12], [450, 25], [560, 25], [600, 0]];
      const v = (t) => { t = Math.max(0, Math.min(600, t));
        for (let i = 1; i < knots.length; i++) if (t <= knots[i][0]) { const [a, va] = knots[i - 1], [b, vb] = knots[i];
          return va + (vb - va) * (t - a) / (b - a); } return 0; };
      const x = (t) => { t = Math.max(0, Math.min(600, t)); let s = 0;
        for (let i = 1; i < knots.length; i++) { const [a, va] = knots[i - 1], [b, vb] = knots[i]; const e = Math.min(t, b);
          if (e <= a) break; const ve = va + (vb - va) * (e - a) / (b - a); s += (va + ve) / 2 * (e - a); } return s; };
      return { T: 600, x, v, Ts: api.p.Ts * 50 / 1000 };   // car: the period slider reads as 0.1–10 s
    }
    return { T: 4, x: (t) => 0.25 * Math.min(4, Math.max(0, t)) ** 2, v: (t) => 0.5 * Math.min(4, Math.max(0, t)), Ts: api.p.Ts / 1000 };
  },
  data(api, s) {   // readings, difference-quotient speeds and the positions rebuilt from them; cached per parameter set
    const key = api.scene + "|" + api.p.Ts + "|" + api.p.e;
    if (s.key === key) return s.d;
    const M = this.truth(api), n = Math.floor(M.T / M.Ts + 1e-9), rng = api.calc.rng(7), e = api.scene === "agv" ? api.p.e / 1000 : 0;
    const t = [], xm = [];
    for (let k = 0; k <= n; k++) { const tk = k * M.Ts; t.push(tk);
      xm.push(Math.round((M.x(tk) + (2 * rng.u() - 1) * e) * 1e4) / 1e4); }
    const v = [], back = [xm[0]];
    for (let k = 0; k < n; k++) { v.push((xm[k + 1] - xm[k]) / M.Ts); back.push(back[k] + v[k] * M.Ts); }
    let worst = 0;
    for (let k = 0; k < n; k++) worst = Math.max(worst, Math.abs(v[k] - M.v(t[k])));   // compared with the true speed at the start of each interval
    s.key = key; s.d = { t, xm, v, back, n, Ts: M.Ts, T: M.T, worst };
    return s.d;
  },
  reset(api, s) { s.tt = 0; s.ran = false; s.key = null; },
  update(dt, api, s) {
    const M = this.truth(api);
    s.tt += dt * M.T / 4;                    // every run lasts 4 s on screen
    if (s.tt >= M.T) { s.tt = M.T; s.ran = true; api.stop(); }
  },
  readouts(api, s) {
    const M = this.truth(api), D = this.data(api, s), car = api.scene === "car";
    const t0 = api.p.t0 * M.T, k = Math.min(D.n - 1, Math.max(0, Math.floor(t0 / D.Ts)));
    const vEst = D.v[k], vTrue = M.v(t0);
    if (!car && Math.abs(t0 - 2) < 0.011 && Math.abs(vEst - vTrue) < 0.08) api.done("speed");
    if (!car && s.ran && Math.abs(D.back[D.n] - D.xm[D.n]) < 0.001) api.done("back");
    if (!car && api.p.e >= 0.5 && D.worst > 0.15) api.done("noise");
    const sp = car ? (v) => api.fmt(v * 3.6, 1) + " km/h" : (v) => api.fmt(v, 3) + " m/s";
    const ds = car ? (x) => api.fmt(x / 1000, 3) + " km" : (x) => api.fmt(x, 4) + " m";
    return [[["读数个数", "Readings"], String(D.n + 1) + api.T("（每 ", " (every ") + api.fmt(D.Ts * (car ? 1 : 1000), car ? 1 : 0) + (car ? " s）" : " ms）")],
            [["t₀ 时由数据求出的速度", "Speed at t₀ from data"], sp(vEst) + api.T("（真实 ", " (true ") + sp(vTrue) + api.T("）", ")")],
            [["速度的最大误差", "Largest speed error"], sp(D.worst)],
            [["最后一个读数", "Last reading"], ds(D.xm[D.n])],
            [["把速度加回去得到的距离", "Distance from adding speeds back"], ds(D.back[D.n])]];
  },
  draw(api, s) {
    const M = this.truth(api), D = this.data(api, s), car = api.scene === "car", w = api.w, h = api.h;
    const red = api.css("--red"), blue = api.css("--blue"), mu = api.css("--muted");
    const tt = api.running || s.ran ? s.tt : M.T, xs = car ? 1 / 1000 : 1, vs = car ? 3.6 : 1;
    // the vehicle on its track
    const trackY = 34, L = w - 40;
    api.line(20, trackY + 4, 20 + L, trackY + 4, mu, 2);
    const vw = Math.min(70, w * 0.08);
    api.agv(20 + vw / 2 + (L - vw) * M.x(tt) / M.x(M.T), trackY, vw, car ? api.css("--amber") : blue);
    // position (top) and speed (bottom)
    const gx = 60, gw = w - 80, gh = (h - 120) / 2;
    const P = api.graph({ x: gx, y: 70, w: gw, h: gh, xmin: 0, xmax: M.T, ymin: 0, ymax: M.x(M.T) * xs * 1.05,
      ylabel: car ? api.T("里程 / km", "distance / km") : api.T("位置 / m", "position / m") });
    P.axes();
    P.fn((t) => M.x(t) * xs, red, 1.5, [5, 4], 0, M.T);
    const step = Math.max(1, Math.round(D.n / 200));
    P.dots(D.t.filter((_, i) => i % step === 0 && D.t[i] <= tt + 1e-9).map((t, i) => [t, D.xm[i * step] * xs]), blue, 2);
    const vmax = Math.max(...D.v.map(Math.abs), M.v(M.T), 1e-9) * vs;
    const V = api.graph({ x: gx, y: 100 + gh, w: gw, h: gh, xmin: 0, xmax: M.T, ymin: Math.min(0, Math.min(...D.v) * vs) * 1.05, ymax: vmax * 1.08,
      xlabel: car ? "t / s" : "t / s", ylabel: car ? api.T("速度 / (km/h)", "speed / (km/h)") : api.T("速度 / (m/s)", "speed / (m/s)") });
    V.axes();
    const pts = [];
    for (let k = 0; k < D.n && D.t[k + 1] <= tt + 1e-9; k++) { pts.push([D.t[k], D.v[k] * vs]); pts.push([D.t[k + 1], D.v[k] * vs]); }
    if (pts.length) V.pts(pts, blue, 1.2);
    V.fn((t) => M.v(t) * vs, red, 2, null, 0, M.T);
    const t0 = api.p.t0 * M.T;
    P.vline(t0, mu); V.vline(t0, mu);
  },
});
