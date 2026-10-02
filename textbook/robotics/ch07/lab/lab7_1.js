// 实验 7.1 状态与相平面（配 7.1 节）。
// 电机：一阶模型 τω̇ + ω = Ku（式 (7.1.4)），τ = J_m R/(Rb + K_tK_e)，K = K_t/(Rb + K_tK_e)；仿真时间放慢 30 倍显示。
// 连杆：θ̈ = −ω_n² sin θ − (b/J_o)θ̇（式 (7.1.11)），ω_n² = 3𝔤/(2L)，L = 0.5 m；左边画连杆，右边画相平面上的轨线。
// 秋千：同一方程，ω_n² = 𝔤/l（把人和秋千看作点质量）。
WQ.lab({
  title: ["实验 7.1 状态与相平面", "Lab 7.1 State and the phase plane"],
  goal: ["把电机和连杆写成状态方程，看时间常数、相平面上的轨线、平衡点和分界线。",
         "Write a motor and a link as state equations; see the time constant, phase-plane trajectories, equilibria and the separatrix."],
  scenes: [
    { id: "motor", robot: true, name: ["关节电机的阶跃响应", "Step response of a joint motor"], hide: ["th0", "damp", "len"],
      problem: { title: ["机器人问题：加上电压后，转速多快升上去", "Robot problem: how fast does the speed rise"],
                 text: ["关节电机在 t = 0 加上电压 u。转速 ω 满足 τω̇ + ω = Ku。改变电压和转动惯量，读出转速升到 63.2% 所用的时间，与 τ 比较。",
                        "A voltage u is applied at t = 0. The speed obeys τω̇ + ω = Ku. Change the voltage and the inertia; read the time to 63.2% and compare it with τ."] } },
    { id: "link", robot: true, name: ["自由摆动的连杆", "A freely swinging link"], hide: ["u", "jm", "len"],
      problem: { title: ["机器人问题：刹车松开后，连杆怎样摆", "Robot problem: how does the link swing once the brake is off"],
                 text: ["长 0.5 m 的均匀连杆从角度 θ₀ 静止释放。状态是 (θ, θ̇)，右边的相平面上画出它的轨线。",
                        "A uniform 0.5 m link is released at rest from θ₀. The state is (θ, θ̇); its trajectory is drawn in the phase plane on the right."] } },
    { id: "swing", name: ["荡秋千", "A playground swing"], hide: ["u", "jm", "damp"],
      params: { th0: { min: 5, max: 80, step: 1, value: 10 } },
      problem: { title: ["生活中的例子：秋千荡得越高，周期越长吗", "Everyday example: does a higher swing take longer"],
                 text: ["把人和秋千看作挂在绳长 l 下的点质量。比较小摆幅和大摆幅的周期。",
                        "Treat the child and the seat as a point mass on a rope of length l. Compare the period for small and large swings."] } },
  ],
  params: [
    { id: "u", name: ["电压 u", "Voltage u"], min: 2, max: 24, step: 1, value: 12, unit: "V", digits: 0 },
    { id: "jm", name: ["转动惯量 J_m（×10⁻⁵）", "Inertia J_m (×10⁻⁵)"], min: 1, max: 20, step: 0.5, value: 4, unit: "kg·m²", digits: 1 },
    { id: "th0", name: ["释放角 θ₀", "Release angle θ₀"], min: 5, max: 179, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "damp", name: ["摩擦 b/J_o", "Friction b/J_o"], min: 0, max: 2, step: 0.1, value: 0, unit: "1/s", digits: 1 },
    { id: "len", name: ["绳长 l", "Rope length l"], min: 1, max: 4, step: 0.1, value: 2.5, unit: "m", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "tau", robot: true, text: ["电机：运行到稳定，读出升到 63.2% 的时间，与 τ 相差不到 2%。", "Motor: run to steady state; the time to 63.2% is within 2% of τ."],
      demo: { scene: "motor", set: { u: 12, jm: 4 }, press: ["start"], wait: 5 } },
    { id: "p90", robot: true, text: ["连杆：从 90° 无摩擦释放，测出周期，与算例 7.1.4 的 1.367 s 比较。", "Link: release from 90° without friction; measure the period and compare with 1.367 s (Example 7.1.4)."],
      demo: { scene: "link", set: { th0: 90, damp: 0 }, press: ["start"], wait: 6 } },
    { id: "spiral", robot: true, text: ["连杆：摩擦取 0.5 1/s 以上，看轨线盘旋进原点，直到摆幅小于初始的 20%。", "Link: friction 0.5 1/s or more; watch the spiral into the origin until the swing is below 20% of the start."],
      demo: { scene: "link", set: { th0: 60, damp: 1.5 }, press: ["start"], wait: 8 } },
    { id: "sep", robot: true, text: ["连杆：从 175° 以上无摩擦释放，测得的周期超过小摆幅周期的 2 倍。", "Link: release from 175° or more without friction; the measured period exceeds twice the small-swing period."],
      demo: { scene: "link", set: { th0: 177, damp: 0 }, press: ["start"], wait: 14 } },
    { id: "swing", text: ["秋千：摆幅 60° 以上，测得的周期比小摆幅周期长 7% 以上。", "Swing: amplitude 60° or more; the period is over 7% longer than for small swings."],
      demo: { scene: "swing", set: { th0: 70, len: 2.5 }, press: ["start"], wait: 10 } },
  ],
  think: ["相平面上两条轨线为什么不会相交？这与 7.1.3 节解的唯一性有什么关系？",
          "Why can two trajectories in the phase plane never cross? How is this related to the uniqueness of solutions in Section 7.1.3?"],

  M: { R: 1.2, Kt: 0.05, Ke: 0.05, b: 2e-5 },
  motorTK(api) { const m = this.M, den = m.R * m.b + m.Kt * m.Ke; return [api.p.jm * 1e-5 * m.R / den, m.Kt / den]; },
  wn2(api) { return api.scene === "swing" ? 9.81 / api.p.len : 3 * 9.81 / (2 * 0.5); },
  f(api, x) { const c = api.scene === "link" ? api.p.damp : 0; return [x[1], -this.wn2(api) * Math.sin(x[0]) - c * x[1]]; },
  rk4(api, x, h) {
    const add = (a, b, k) => [a[0] + k * b[0], a[1] + k * b[1]];
    const k1 = this.f(api, x), k2 = this.f(api, add(x, k1, h / 2)), k3 = this.f(api, add(x, k2, h / 2)), k4 = this.f(api, add(x, k3, h));
    return [x[0] + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]), x[1] + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])];
  },

  reset(api, s) {
    s.time = 0; s.w = 0; s.hist = [[0, 0]]; s.t63 = null;
    s.x = [api.p.th0 * Math.PI / 180, 0]; s.trace = [s.x.slice()]; s.turns = []; s.period = null; s.amp = Math.abs(s.x[0]);
  },
  update(dt, api, s) {
    if (api.scene === "motor") {
      const [tau, K] = this.motorTK(api), winf = K * api.p.u, hsim = dt / 30;     // 放慢 30 倍
      const n = 20;
      for (let i = 0; i < n; i++) s.w += (hsim / n) * (winf - s.w) / tau;          // 小步长欧拉，足够精确
      s.time += hsim;
      s.hist.push([s.time * 1000, s.w]);
      if (s.t63 === null && s.w >= (1 - Math.exp(-1)) * winf) {
        const [t0, w0] = s.hist[s.hist.length - 2], [t1, w1] = s.hist[s.hist.length - 1], target = (1 - Math.exp(-1)) * winf;
        s.t63 = (t0 + (t1 - t0) * (target - w0) / (w1 - w0)) / 1000;               // 线性插值
      }
      if (s.time > 5 * tau) {
        api.stop();
        if (s.t63 !== null && Math.abs(s.t63 - tau) / tau < 0.02) api.done("tau");
      }
      return;
    }
    const n = Math.max(1, Math.round(dt / 0.001)), h = dt / n;
    for (let i = 0; i < n; i++) {
      const prev = s.x;
      s.x = this.rk4(api, s.x, h);
      s.time += h;
      if (prev[1] < 0 && s.x[1] >= 0) {                 // θ̇ 由负变正：到达左端，记下时刻
        const a = prev[1] / (prev[1] - s.x[1]);
        s.turns.push(s.time - h + a * h);
        if (s.turns.length >= 2) s.period = s.turns[s.turns.length - 1] - s.turns[s.turns.length - 2];
      }
    }
    s.trace.push(s.x.slice());
    if (s.trace.length > 4000) s.trace.shift();
    const T0 = 2 * Math.PI / Math.sqrt(this.wn2(api));
    const th = Math.abs(s.x[0]);
    if (api.scene === "link") {
      if (s.period && api.p.damp === 0 && api.p.th0 === 90 && Math.abs(s.period - 1.3671) < 0.014) api.done("p90");
      if (s.period && api.p.damp === 0 && api.p.th0 >= 175 && s.period > 2 * T0) api.done("sep");
      if (api.p.damp >= 0.5 && s.time > 1 && Math.hypot(s.x[0], s.x[1] / Math.sqrt(this.wn2(api))) < 0.2 * s.amp) api.done("spiral");
    } else if (s.period && api.p.th0 >= 60 && s.period > 1.07 * T0) api.done("swing");
    if (s.time > 40) api.stop();
  },
  readouts(api, s) {
    if (api.scene === "motor") {
      const [tau, K] = this.motorTK(api);
      return [[["时间常数 τ（公式）", "time constant τ (formula)"], api.fmt(tau * 1000, 2) + " ms"],
              [["最终转速 Ku", "final speed Ku"], api.fmt(K * api.p.u, 1) + " rad/s"],
              [["当前时间", "time"], api.fmt(s.time * 1000, 1) + " ms"],
              [["当前转速 ω", "speed ω"], api.fmt(s.w, 1) + " rad/s"],
              [["测得的 63.2% 时刻", "measured time to 63.2%"], s.t63 === null ? "—" : api.fmt(s.t63 * 1000, 2) + " ms"]];
    }
    const wn2 = this.wn2(api), T0 = 2 * Math.PI / Math.sqrt(wn2);
    const E = 0.5 * s.x[1] * s.x[1] + wn2 * (1 - Math.cos(s.x[0]));
    return [[["时间", "time"], api.fmt(s.time, 2) + " s"],
            [["状态 (θ, θ̇)", "state (θ, θ̇)"], `(${api.fmt(s.x[0] * 180 / Math.PI, 1)}°, ${api.fmt(s.x[1], 2)} rad/s)`],
            [["小摆幅周期 2π/ω_n", "small-swing period 2π/ω_n"], api.fmt(T0, 3) + " s"],
            [["测得的周期", "measured period"], s.period ? api.fmt(s.period, 3) + " s" : "—"],
            [["周期之比", "period ratio"], s.period ? api.fmt(s.period / T0, 3) : "—"],
            [["能量 E/J（每单位转动惯量）", "energy E/J per unit inertia"], api.fmt(E, 2) + " 1/s²"]];
  },
  draw(api, s) {
    const { w, h } = api;
    if (api.scene === "motor") {
      const [tau, K] = this.motorTK(api), winf = K * api.p.u;
      // 左：电机与负载（转盘的转角按转速积分）
      const cx = w * 0.18, cy = h * 0.5, r = Math.min(w, h) * 0.16;
      api.rect(cx - r * 1.5, cy - r * 0.6, r * 1.1, r * 1.2, api.css("--soft"), api.css("--ink"), 6);
      api.label(api.T("电机", "motor"), cx - r * 0.95, cy, api.css("--ink"), 13, "center");
      api.line(cx - r * 0.4, cy, cx - r * 0.1, cy, api.css("--ink"), 4);
      api.circle(cx + r * 0.4, cy, r * 0.55, api.css("--panel"), api.css("--ink"));
      const ang = s.hist.reduce((a, p, i) => (i ? a + (p[0] - s.hist[i - 1][0]) / 1000 * p[1] : 0), 0) / 30;
      api.line(cx + r * 0.4, cy, cx + r * 0.4 + r * 0.5 * Math.cos(ang), cy - r * 0.5 * Math.sin(ang), api.css("--accent"), 3);
      api.label(`u = ${api.fmt(api.p.u, 0)} V`, cx - r * 0.95, cy + r * 0.9, api.css("--amber"), 13, "center");
      // 右：ω(t)
      const px = w * 0.38, pw = w * 0.58, py = 20, ph = h - 60, tmax = 6 * tau * 1000;
      const exact = []; for (let i = 0; i <= 60; i++) { const t = tmax * i / 60; exact.push([t, winf * (1 - Math.exp(-t / 1000 / tau))]); }
      const P = api.plot(px, py, pw, ph, [{ pts: exact, color: api.css("--muted") }, { pts: s.hist, color: api.css("--accent") }],
        { xmin: 0, xmax: tmax, ymin: 0, ymax: Math.max(50, winf * 1.15), xlabel: "t / ms", ylabel: "ω / (rad/s)" });
      const y63 = P.Y((1 - Math.exp(-1)) * winf);
      api.line(px, y63, px + pw, y63, api.css("--amber"), 1, [5, 4]);
      api.label("63.2%", px + pw - 4, y63 - 9, api.css("--amber"), 12, "right");
      api.line(P.X(tau * 1000), py, P.X(tau * 1000), py + ph, api.css("--amber"), 1, [5, 4]);
      api.label("τ", P.X(tau * 1000) + 5, py + 12, api.css("--amber"), 13);
      return;
    }
    // 左：连杆或秋千
    const cx = w * 0.22, cy = h * 0.35, L = Math.min(w * 0.18, h * 0.32);
    api.line(cx - 40, cy, cx + 40, cy, api.css("--ground"), 3);
    api.line(cx, cy, cx, cy + L * 1.15, api.css("--grid"), 1, [4, 4]);
    const th = s.x[0], ex = cx + L * Math.sin(th), ey = cy + L * Math.cos(th);
    if (api.scene === "link") {
      api.line(cx, cy, ex, ey, api.css("--accent"), 10);
      api.circle(cx, cy, 6, api.css("--panel"), api.css("--ink"));
      api.circle((cx + ex) / 2, (cy + ey) / 2, 4, api.css("--amber"));
    } else {
      api.line(cx, cy, ex, ey, api.css("--ink"), 2);
      api.rect(ex - 16, ey - 4, 32, 8, api.css("--amber"), api.css("--ink"), 3);
      api.circle(ex, ey - 16, 9, api.css("--accent"));
    }
    api.label("θ = " + api.fmt(th * 180 / Math.PI, 1) + "°", cx, cy + L * 1.3, api.css("--ink"), 13, "center");
    // 右：相平面
    const wn = Math.sqrt(this.wn2(api)), vmax = 2.3 * wn;
    const px = w * 0.45, pw = w * 0.52, py = 16, ph = h - 50;
    const X = (a) => px + (a + Math.PI * 1.15) / (2.3 * Math.PI) * pw, Y = (v) => py + ph / 2 - v / vmax * ph / 2;
    api.rect(px, py, pw, ph, null, api.css("--grid"));
    api.line(px, Y(0), px + pw, Y(0), api.css("--grid"), 1);
    api.line(X(0), py, X(0), py + ph, api.css("--grid"), 1);
    const sep = (sg) => { const pts = []; for (let i = 0; i <= 80; i++) { const a = -Math.PI + 2 * Math.PI * i / 80; pts.push([X(a), Y(sg * 2 * wn * Math.cos(a / 2))]); } return pts; };
    [1, -1].forEach((sg) => { const p = sep(sg); for (let i = 0; i < p.length - 1; i++) api.line(...p[i], ...p[i + 1], api.css("--red"), 1, [3, 3]); });
    const wrap = (a) => ((a + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
    for (let i = 1; i < s.trace.length; i++) {
      const a = s.trace[i - 1], b = s.trace[i];
      if (Math.abs(wrap(a[0]) - wrap(b[0])) > Math.PI) continue;
      api.line(X(wrap(a[0])), Y(a[1]), X(wrap(b[0])), Y(b[1]), api.css("--accent"), 2);
    }
    api.circle(X(wrap(s.x[0])), Y(s.x[1]), 5, api.css("--amber"), api.css("--ink"));
    api.circle(X(0), Y(0), 4, api.css("--ink"));
    api.circle(X(Math.PI), Y(0), 4, api.css("--panel"), api.css("--ink"));
    api.circle(X(-Math.PI), Y(0), 4, api.css("--panel"), api.css("--ink"));
    api.label("θ", px + pw - 10, Y(0) - 10, api.css("--muted"), 13);
    api.label("dθ/dt", X(0) + 6, py + 10, api.css("--muted"), 13);
    api.label(api.T("红虚线：分界线", "red dashed: separatrix"), px + 6, py + ph + 16, api.css("--red"), 12);
  },
});
