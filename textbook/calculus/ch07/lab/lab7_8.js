// 实验 7.8 运动曲线：位置、速度、加速度、加加速度（配 7.8 节）。三种“静止到静止”的运动规律（式 (7.8.1)、(7.1.9) 与梯形速度，
// 梯形的匀加速时间 t_a = T/4）；“编码器数据”场景：17 位编码器、1 ms 采样，读数取整到刻度，用二阶差商估计角加速度（式 (7.8.6)）。
WQ.lab({
  title: ["实验 7.8 运动曲线：位置、速度、加速度、加加速度", "Lab 7.8 Motion profiles: position, velocity, acceleration, jerk"],
  goal: ["比较三种运动规律的角度、角速度、角加速度和加加速度曲线，按限速和限加速度选择运动时间；用编码器读数估计角加速度，体会求导对误差的放大。",
         "Compare the angle, velocity, acceleration and jerk of three motion laws, choose a move time under speed and acceleration limits, and estimate acceleration from encoder counts to see how differentiation magnifies errors."],
  scenes: [
    { id: "cubic", robot: true, name: ["三次多项式", "Cubic"], hide: ["k"],
      problem: { title: ["机器人问题：哪种运动规律对机械更“友好”？", "Robot problem: which motion law is kinder to the machine?"],
                 text: ["三种规律都在 T 秒内转过 Δ，起点终点都静止。看角加速度在起点是否跳跃：跳跃意味着电机力矩突变，会激起振动。",
                        "All three laws turn through Δ in T seconds from rest to rest. Watch whether the acceleration jumps at the start: a jump is a sudden torque step that shakes the arm."] } },
    { id: "quintic", robot: true, name: ["五次多项式", "Quintic"], hide: ["k"],
      problem: { title: ["机器人问题：多付出一点速度，换来平顺", "Robot problem: a little more speed for smoothness"],
                 text: ["五次多项式在两端让角度、角速度、角加速度都与静止状态连续衔接，加加速度有限；代价是峰值角速度和角加速度都比梯形速度大。",
                        "The quintic joins angle, velocity and acceleration smoothly to rest at both ends, so the jerk stays finite; the price is a larger peak velocity and acceleration than the trapezoid."] } },
    { id: "trap", robot: true, name: ["梯形速度", "Trapezoidal"], hide: ["k"],
      problem: { title: ["机器人问题：最快，但不平顺", "Robot problem: fastest, but not smooth"],
                 text: ["梯形速度先匀加速、再匀速、后匀减速，峰值最小，把电机用得最充分；但角加速度在四处跳跃。",
                        "The trapezoid accelerates, cruises and decelerates: the smallest peaks and the fullest use of the motor, but the acceleration jumps four times."] } },
    { id: "data", name: ["编码器数据", "Encoder data"], hide: ["T", "D"],
      problem: { title: ["由数据求加速度", "Acceleration from data"],
                 text: ["五次多项式运动（T = 2 s，Δ = 90°），17 位编码器每 1 ms 读一次。用步长 h = k ms 的二阶差商估计角加速度。k 取多大，误差才小于 0.1 rad/s²？",
                        "Quintic move (T = 2 s, Δ = 90°), a 17-bit encoder read every 1 ms. Estimate the acceleration with a second difference of step h = k ms. How large must k be for an error below 0.1 rad/s²?"] } },
  ],
  params: [
    { id: "T", name: ["运动时间 T", "Move time T"], min: 0.8, max: 3, step: 0.005, value: 2, unit: "s", digits: 3 },
    { id: "D", name: ["转角 Δ", "Angle Δ"], min: 10, max: 180, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "k", name: ["差商步长 k（采样周期的倍数）", "Difference step k (in samples)"], min: 1, max: 50, step: 1, value: 1, digits: 0 },
  ],
  buttons: [{ id: "start", name: ["运动", "Run"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["θ", "θ"], color: "#1d2327" }, { name: ["ω", "ω"], color: "#1f77b4" }, { name: ["α", "α"], color: "#2ca02c" }, { name: ["j", "j"], color: "#d62728" }],
  tasks: [
    { id: "smooth", robot: true, text: ["运行三种规律，找出角加速度在起点和终点都不跳跃的那一种，并让它完整运动一次。", "Run the three laws, find the one whose acceleration does not jump at either end, and run it once to the end."],
      demo: { scene: "quintic", set: { T: 1.0 }, press: ["start"], wait: 2 } },
    { id: "fastest", robot: true, text: ["限速 180°/s、限角加速度 5 rad/s²：用五次多项式转过 90°，把 T 调到满足限制的最短时间（误差 0.01 s 以内）。", "With 180°/s and 5 rad/s² limits, set the shortest T for a 90° quintic move (within 0.01 s)."],
      demo: { scene: "quintic", set: { D: 90, T: 1.35 }, press: [], wait: 1 } },
    { id: "data", text: ["在“编码器数据”场景中，找出使角加速度估计的均方根误差小于 0.1 rad/s² 的步长 k。", "In 'Encoder data' find a step k that brings the RMS acceleration error below 0.1 rad/s²."],
      demo: { scene: "data", set: { k: 20 }, press: [], wait: 1 } },
  ],
  think: ["运动时间缩短一半，峰值角速度、角加速度、加加速度各变为几倍？用图验证。", "If the move time is halved, by what factors do the peak velocity, acceleration and jerk change? Check on the plots."],

  law(api) { return api.scene === "data" ? "quintic" : api.scene; },
  TD(api) { return api.scene === "data" ? [2, Math.PI / 2] : [api.p.T, api.p.D * Math.PI / 180]; },
  at(law, t, T, D) {   // [θ, ω, α, j] at time t (rad, rad/s, rad/s², rad/s³); outside [0, T] the joint is at rest
    if (t <= 0) return [0, 0, 0, 0];
    if (t >= T) return [D, 0, 0, 0];
    const s = t / T;
    if (law === "cubic") return [D * (3 * s * s - 2 * s ** 3), 6 * D / T * s * (1 - s), 6 * D / T ** 2 * (1 - 2 * s), -12 * D / T ** 3];
    if (law === "quintic") return [D * (10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5), 30 * D / T * s * s * (1 - s) ** 2,
      60 * D / T ** 2 * s * (1 - s) * (1 - 2 * s), 60 * D / T ** 3 * (1 - 6 * s + 6 * s * s)];
    const ta = T / 4, wc = D / (T - ta), a0 = wc / ta;
    if (t < ta) return [0.5 * a0 * t * t, a0 * t, a0, 0];
    if (t < T - ta) return [0.5 * a0 * ta * ta + wc * (t - ta), wc, 0, 0];
    return [D - 0.5 * a0 * (T - t) ** 2, a0 * (T - t), -a0, 0];
  },
  peaks(law, T, D) {
    if (law === "cubic") return { w: 1.5 * D / T, a: 6 * D / T ** 2, j: Infinity };
    if (law === "quintic") return { w: 15 * D / (8 * T), a: 10 * D / (Math.sqrt(3) * T * T), j: 60 * D / T ** 3 };
    const ta = T / 4, wc = D / (T - ta); return { w: wc, a: wc / ta, j: Infinity };
  },
  encoder(api, s) {   // RMS error of the second-difference acceleration estimate, cached per k
    const k = api.p.k;
    if (s.encK === k) return s.encRms;
    const T = 2, D = Math.PI / 2, q = 2 * Math.PI / 131072, Ts = 0.001, n = Math.round(T / Ts);
    const th = [], est = [];
    for (let i = 0; i <= n; i++) th.push(Math.round(this.at("quintic", i * Ts, T, D)[0] / q) * q);
    let sum = 0, cnt = 0;
    for (let i = k; i <= n - k; i++) {
      const a = (th[i + k] - 2 * th[i] + th[i - k]) / (k * Ts) ** 2;
      est.push([i * Ts, a]); sum += (a - this.at("quintic", i * Ts, T, D)[2]) ** 2; cnt++;
    }
    s.encK = k; s.encRms = Math.sqrt(sum / cnt); s.encEst = est;
    return s.encRms;
  },
  reset(api, s) { s.t = 0; s.ran = false; },
  update(dt, api, s) {
    const [T] = this.TD(api);
    s.t += dt;
    if (s.t >= T + 0.3) { s.t = T + 0.3; s.ran = true; api.stop(); }
  },
  readouts(api, s) {
    const law = this.law(api), [T, D] = this.TD(api), P = this.peaks(law, T, D), now = this.at(law, s.t || 0, T, D);
    if (api.scene === "quintic" && s.ran) api.done("smooth");
    if (api.scene === "quintic" && Math.abs(api.p.D - 90) < 0.5 && P.w <= Math.PI + 1e-9 && P.a <= 5 + 1e-9 && T <= 1.357) api.done("fastest");
    const rows = [[["时刻 t", "Time t"], api.fmt(s.t || 0, 3) + " s"],
                  [["θ, ω, α", "θ, ω, α"], api.fmt(now[0] * 180 / Math.PI, 2) + "°, " + api.fmt(now[1], 3) + " rad/s, " + api.fmt(now[2], 3) + " rad/s²"],
                  [["峰值角速度", "Peak velocity"], api.fmt(P.w, 4) + " rad/s（" + api.fmt(P.w * 180 / Math.PI, 1) + "°/s）"],
                  [["峰值角加速度", "Peak acceleration"], api.fmt(P.a, 4) + " rad/s²"],
                  [["峰值加加速度", "Peak jerk"], isFinite(P.j) ? api.fmt(P.j, 3) + " rad/s³" : api.T("无穷大（冲激）", "infinite (impulse)")]];
    if (api.scene === "data") {
      const rms = this.encoder(api, s);
      if (rms < 0.1) api.done("data");
      rows.splice(1, 4, [["编码器一个刻度", "One encoder count"], api.fmt(2 * Math.PI / 131072 * 1e6, 1) + " μrad"],
        [["步长 h", "Step h"], api.p.k + " ms"], [["角加速度估计的均方根误差", "RMS acceleration error"], api.fmt(rms, 4) + " rad/s²"]);
    }
    return rows;
  },
  draw(api, s) {
    const law = this.law(api), [T, D] = this.TD(api), w = api.w, h = api.h, t = s.t || 0;
    const ink = api.css("--ink"), blue = api.css("--blue"), green = api.css("--green"), red = api.css("--red"), mu = api.css("--muted");
    // left: the arm (upper arm turns by θ, forearm fixed), side view
    const now = this.at(law, t, T, D), L = Math.min(w * 0.12, h * 0.3);
    api.ground(h * 0.85, w * 0.32);
    api.arm(w * 0.07, h * 0.85, [now[0] * 180 / Math.PI, 60], [L, L * 0.92], blue, 10);
    api.label(api.T("θ = ", "θ = ") + api.fmt(now[0] * 180 / Math.PI, 1) + "°", w * 0.04, h * 0.95, ink, 13);
    // right: four plots sharing the time axis
    const x0 = w * 0.36, pw = w * 0.6, ph = (h - 40) / 4 - 14, tmin = -0.2, tmax = T + 0.3;
    const names = ["θ / °", "ω / (rad/s)", "α / (rad/s²)", "j / (rad/s³)"], cols = [ink, blue, green, red];
    const P = this.peaks(law, T, D), lim = [D * 180 / Math.PI, P.w, P.a, isFinite(P.j) ? P.j : 12 * D / T ** 3];
    for (let r = 0; r < 4; r++) {
      const top = 10 + r * (ph + 14), big = Math.max(1e-9, lim[r]) * 1.25;
      const G = api.graph({ x: x0, y: top, w: pw, h: ph, xmin: tmin, xmax: tmax, ymin: r === 0 ? -0.1 * big : -big, ymax: big, ticks: false });
      G.axes();
      api.label(names[r], x0 + 4, top + 12, cols[r], 12);
      const f = (tt) => { const v = this.at(law, tt, T, D)[r]; return r === 0 ? v * 180 / Math.PI : v; };
      if (api.scene === "data" && r === 2 && s.encEst) G.pts(s.encEst.filter((p, i) => i % 2 === 0), mu, 1);
      G.fn(f, cols[r], 2);
      if (r === 3 && !isFinite(P.j)) {   // impulses at the jumps of α
        const at = law === "cubic" ? [0, T] : [0, T / 4, 3 * T / 4, T];
        at.forEach((ta, i) => { const up = law === "cubic" ? 1 : (i === 0 || i === 3 ? 1 : -1);
          api.arrow(G.X(ta), G.Y(0), G.X(ta), G.Y(up * big * 0.85), red, 2); });
      }
      G.vline(Math.min(t, tmax), mu, [3, 3]);
    }
    api.label("t / s", x0 + pw, h - 6, mu, 12, "right");
    if (api.scene === "data") this.encoder(api, s);
  },
});
