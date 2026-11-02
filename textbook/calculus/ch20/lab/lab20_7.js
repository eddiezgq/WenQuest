// 实验 20.7 PD 控制的关节与受迫振动（配 20.3、20.6、20.7 节）。“机器人”场景：肩关节（上臂 0.5129 kg·m² + RE 40 转子经
// 减速比 101 折算 0.1398 kg·m²，粘性摩擦 0.5 N·m·s/rad）在 PD 控制下的阶跃响应；可加肘端负载、重力；转矩按驱动器限流
// 10 A 限幅（约 60.9 N·m）。“受迫振动”场景：ẍ + 2ζẋ + x = cos(rt)（ω_n = 1）从静止开始的响应与稳态振幅。
WQ.lab({
  title: ["实验 20.7 PD 控制的关节与受迫振动", "Lab 20.7 PD joint control and forced vibration"],
  goal: ["看清 PD 控制怎样把关节变成一个质量–弹簧–阻尼系统：由增益算出固有频率和阻尼比，按超调和调节时间设计增益，看负载、重力和转矩上限的影响；再看受迫振动怎样从暂态过渡到稳态，找出共振峰。",
         "See how PD control turns a joint into a mass–spring–damper: compute the natural frequency and damping ratio from the gains, design gains for overshoot and settling time, and see the effects of payload, gravity and torque limits; then watch forced vibration settle into its steady state and find the resonance peak."],
  scenes: [
    { id: "pd", robot: true, name: ["关节 PD 控制", "Joint PD control"], hide: ["r", "zeta"],
      problem: { title: ["机器人问题：肩关节转 0.5 rad，怎样选 K_p、K_d 才能又快又不超调？", "Robot problem: how to choose K_p and K_d so the shoulder turns 0.5 rad quickly without overshoot?"],
                 text: ["控制律 τ = K_p(q_ref − q) − K_d q̇。关节侧总惯量 0.653 kg·m²（上臂 + 电机转子折算），粘性摩擦 0.5 N·m·s/rad。闭环方程 J q̈ + (b + K_d) q̇ + K_p q = K_p q_ref，ω_n = √(K_p/J)，ζ = (b + K_d)/(2√(K_p J))。",
                        "Control law τ = K_p(q_ref − q) − K_d q̇. Total joint-side inertia 0.653 kg·m² (upper arm + reflected rotor), viscous friction 0.5 N·m·s/rad. Closed loop J q̈ + (b + K_d) q̇ + K_p q = K_p q_ref, ω_n = √(K_p/J), ζ = (b + K_d)/(2√(K_p J))."] } },
    { id: "vib", name: ["受迫振动", "Forced vibration"], hide: ["Kp", "Kd", "load", "step", "grav"],
      problem: { title: ["外力频率接近固有频率时会怎样？", "What happens when the forcing frequency nears the natural frequency?"],
                 text: ["质量–弹簧–阻尼系统 ẍ + 2ζẋ + x = cos(rt)（固有频率取 1），从静止开始。r 是频率比。看暂态怎样衰减、稳态振幅是静态位移的几倍。",
                        "The mass–spring–damper ẍ + 2ζẋ + x = cos(rt) (natural frequency 1) starts from rest; r is the frequency ratio. Watch the transient die out and read how many times the static deflection the steady amplitude is."] } },
  ],
  params: [
    { id: "Kp", name: ["比例增益 K_p", "Proportional gain K_p"], min: 5, max: 500, step: 0.1, value: 30, unit: "N·m/rad", digits: 1 },
    { id: "Kd", name: ["微分增益 K_d", "Derivative gain K_d"], min: 0, max: 40, step: 0.01, value: 2, unit: "N·m·s/rad", digits: 2 },
    { id: "load", name: ["肘端负载（离肩轴 0.425 m）", "Payload at the elbow (0.425 m from the shoulder)"], min: 0, max: 5, step: 0.1, value: 0, unit: "kg", digits: 1 },
    { id: "step", name: ["目标角度（阶跃）", "Target angle (step)"], min: 0.1, max: 1.0, step: 0.01, value: 0.5, unit: "rad", digits: 2 },
    { id: "grav", name: ["重力：0 水平面内转动，1 竖直平面内（从水平量起）", "Gravity: 0 horizontal plane, 1 vertical plane (from horizontal)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "r", name: ["频率比 r = ω/ω_n", "Frequency ratio r = ω/ω_n"], min: 0.1, max: 3, step: 0.005, value: 0.5, digits: 3 },
    { id: "zeta", name: ["阻尼比 ζ", "Damping ratio ζ"], min: 0.01, max: 1, step: 0.01, value: 0.1, digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["关节角 / 位移", "joint angle / displacement"], color: "#1f77b4" }, { name: ["目标 / 外力", "target / force"], color: "#7a868d" }, { name: ["转矩 / 稳态包络", "torque / steady envelope"], color: "#d62728" }],
  tasks: [
    { id: "spec", robot: true, text: ["空载、水平面、目标 0.5 rad：选 K_p、K_d 使超调不超过 5%、2% 调节时间不超过 0.6 s。", "No payload, horizontal plane, 0.5 rad step: choose K_p and K_d for overshoot ≤ 5% and 2% settling time ≤ 0.6 s."],
      demo: { scene: "pd", set: { Kp: 65.3, Kd: 8.64, load: 0, step: 0.5, grav: 0 }, wait: 1 } },
    { id: "crit", robot: true, text: ["保持 K_p = 65.3，K_d 取多少时恰为临界阻尼（ζ = 1）？与 ζ = 0.7 相比，调节时间哪个短？", "Keep K_p = 65.3. Which K_d gives critical damping (ζ = 1)? Which settles faster, this or ζ = 0.7?"],
      demo: { scene: "pd", set: { Kp: 65.3, Kd: 12.56, load: 0, step: 0.5, grav: 0 }, wait: 1 } },
    { id: "load", robot: true, text: ["肘端挂 2 kg：原来的增益超调多少？重新调 K_p、K_d，使超调 ≤ 5%、调节时间 ≤ 0.6 s。", "Put 2 kg at the elbow: how much do the old gains overshoot? Retune K_p and K_d for overshoot ≤ 5% and settling ≤ 0.6 s."],
      demo: { scene: "pd", set: { Kp: 101.4, Kd: 13.7, load: 2, step: 0.5, grav: 0 }, wait: 1 } },
    { id: "grav", robot: true, text: ["打开重力：稳态误差有多大？只靠加大增益，能否把它压到 0.05 rad 以下而阻尼比不低于 0.5？代价是什么？", "Turn gravity on: how large is the steady error? Can larger gains alone push it below 0.05 rad with ζ ≥ 0.5? At what cost?"],
      demo: { scene: "pd", set: { Kp: 320, Kd: 19.9, load: 0, step: 0.5, grav: 1 }, wait: 1 } },
    { id: "res", text: ["受迫振动，ζ = 0.1：找出使稳态振幅最大的频率比，读出最大放大系数，与 1/(2ζ) 比较。", "Forced vibration, ζ = 0.1: find the frequency ratio with the largest steady amplitude and compare the peak magnification with 1/(2ζ)."],
      demo: { scene: "vib", set: { zeta: 0.1, r: 0.99 }, wait: 1 } },
  ],
  think: ["算例 20.3.2 中上臂在减速器上的固有频率约 197 rad/s。把 K_p 加大到使 ω_n 接近它的五分之一，实际的机械臂会出现什么这个模型看不到的问题？",
          "The upper arm's natural frequency on the gearbox is about 197 rad/s (Example 20.3.2). If K_p is raised until ω_n is about a fifth of that, what problem would a real arm show that this model cannot?"],

  JA: 0.5129, JR: 0.13975, B: 0.5, TMAX: 60.9, MGD: 8.393 * 9.81 * 0.2125, L: 0.425,
  sim(p) {
    const key = [p.Kp, p.Kd, p.load, p.step, p.grav].join(",");
    if (this._k === key) return this._r;
    const J = this.JA + this.JR + p.load * this.L * this.L, g = p.grav ? (this.MGD + p.load * 9.81 * this.L) : 0;
    const dt = 0.001, n = 3000, ts = [], qs = [], taus = [];
    let q = 0, w = 0, sat = false, tpk = 0;
    const tau = (q, w) => { let t = p.Kp * (p.step - q) - p.Kd * w; if (t > this.TMAX) { t = this.TMAX; sat = true; } if (t < -this.TMAX) { t = -this.TMAX; sat = true; } return t; };
    const f = (q, w) => [w, (tau(q, w) - this.B * w - g * Math.cos(q)) / J];
    for (let k = 0; k <= n; k++) {
      const tk = tau(q, w);
      ts.push(k * dt); qs.push(q); taus.push(tk); tpk = Math.max(tpk, Math.abs(tk));
      const a = f(q, w), b = f(q + dt / 2 * a[0], w + dt / 2 * a[1]), c = f(q + dt / 2 * b[0], w + dt / 2 * b[1]), d = f(q + dt * c[0], w + dt * c[1]);
      q += dt / 6 * (a[0] + 2 * b[0] + 2 * c[0] + d[0]); w += dt / 6 * (a[1] + 2 * b[1] + 2 * c[1] + d[1]);
    }
    const qend = qs[n], over = (Math.max(...qs) - p.step) / p.step * 100;
    let last = -1;
    for (let k = 0; k <= n; k++) if (Math.abs(qs[k] - qend) > 0.02 * p.step) last = k;
    const tset = (last + 1) * dt;
    this._k = key;
    this._r = { ts, qs, taus, J, over, tset, qend, err: p.step - qend, tpk, sat, wn: Math.sqrt(p.Kp / J), zeta: (this.B + p.Kd) / (2 * Math.sqrt(p.Kp * J)) };
    return this._r;
  },
  vib(p) {
    const key = [p.r, p.zeta].join(",");
    if (this._kv === key) return this._v;
    const z = p.zeta, r = p.r, Tend = Math.max(40, 8 / z), n = 8000, dt = Tend / n, ts = [], xs = [];
    let x = 0, v = 0;
    const f = (t, x, v) => [v, Math.cos(r * t) - 2 * z * v - x];
    for (let k = 0; k <= n; k++) {
      const t = k * dt; ts.push(t); xs.push(x);
      const a = f(t, x, v), b = f(t + dt / 2, x + dt / 2 * a[0], v + dt / 2 * a[1]), c = f(t + dt / 2, x + dt / 2 * b[0], v + dt / 2 * b[1]), d = f(t + dt, x + dt * c[0], v + dt * c[1]);
      x += dt / 6 * (a[0] + 2 * b[0] + 2 * c[0] + d[0]); v += dt / 6 * (a[1] + 2 * b[1] + 2 * c[1] + d[1]);
    }
    const M = 1 / Math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2);
    let mx = 0;
    for (let k = Math.floor(0.8 * n); k <= n; k++) mx = Math.max(mx, Math.abs(xs[k]));
    this._kv = key;
    this._v = { ts, xs, M, mx, Tend, ph: Math.atan2(2 * z * r, 1 - r * r) * 180 / Math.PI };
    return this._v;
  },
  reset() {},
  readouts(api) {
    const p = api.p;
    if (api.scene === "pd") {
      const R = this.sim(p);
      const ok = R.over <= 5 && R.tset <= 0.6 + 1e-9 && Math.abs(p.step - 0.5) < 1e-9 && !p.grav;
      if (ok && p.load === 0) api.done("spec");
      if (p.load === 0 && !p.grav && Math.abs(p.Kp - 65.3) < 0.051 && Math.abs(R.zeta - 1) < 0.01) api.done("crit");
      if (ok && Math.abs(p.load - 2) < 1e-9) api.done("load");
      if (p.grav && p.load === 0 && Math.abs(R.err) < 0.05 && R.zeta >= 0.5) api.done("grav");
      return [[["固有频率 ω_n = √(K_p/J)", "natural frequency ω_n"], R.wn.toFixed(2) + " rad/s"],
              [["阻尼比 ζ = (b + K_d)/(2√(K_p J))", "damping ratio ζ"], R.zeta.toFixed(3)],
              [["超调", "overshoot"], Math.max(R.over, 0).toFixed(2) + " %"],
              [["2% 调节时间", "2% settling time"], R.tset > 2.99 ? api.T("> 3 s", "> 3 s") : R.tset.toFixed(3) + " s"],
              [["稳态误差", "steady-state error"], (Math.abs(R.err) < 5e-5 ? 0 : R.err).toFixed(4) + " rad"],
              [["最大转矩（额定 18.9，限幅 60.9）", "peak torque (rated 18.9, limit 60.9)"], R.tpk.toFixed(1) + " N·m" + (R.sat ? api.T("（已限幅）", " (saturated)") : "")],
              [["关节侧总惯量 J", "total inertia J"], R.J.toFixed(3) + " kg·m²"]];
    }
    const V = this.vib(p);
    if (Math.abs(p.zeta - 0.1) < 1e-9 && V.M > 4.95) api.done("res");
    return [[["放大系数 M(r)（公式）", "magnification M(r) (formula)"], V.M.toFixed(3)],
            [["仿真末段的最大位移", "max displacement near the end"], V.mx.toFixed(3)],
            [["相位滞后 φ", "phase lag φ"], V.ph.toFixed(1) + "°"],
            [["1/(2ζ)", "1/(2ζ)"], (1 / (2 * p.zeta)).toFixed(2)],
            [["峰值频率比 √(1 − 2ζ²)", "peak ratio √(1 − 2ζ²)"], p.zeta < Math.SQRT1_2 ? Math.sqrt(1 - 2 * p.zeta * p.zeta).toFixed(3) : api.T("无峰", "no peak")]];
  },
  draw(api) {
    const p = api.p, w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), muted = api.css("--muted"), green = api.css("--green");
    if (api.scene === "pd") {
      const R = this.sim(p), h1 = (h - 110) * 0.6, h2 = (h - 110) * 0.4;
      const ymax = Math.max(p.step * 1.6, ...R.qs) * 1.05;
      const G = api.graph({ x: 70, y: 20, w: w - 90, h: h1, xmin: 0, xmax: 3, ymin: Math.min(0, ...R.qs), ymax, xlabel: "", ylabel: "q / rad" });
      G.axes();
      G.hline(p.step, muted, [4, 4]);
      G.hline(p.step * 1.02, green, [2, 3]); G.hline(p.step * 0.98, green, [2, 3]);
      G.pts(R.ts.map((t, k) => [t, R.qs[k]]), blue, 2.5);
      if (R.tset < 2.99) G.vline(R.tset, blue, [3, 4]);
      const tmax = Math.max(70, R.tpk * 1.1);
      const H = api.graph({ x: 70, y: 56 + h1, w: w - 90, h: h2, xmin: 0, xmax: 3, ymin: -tmax, ymax: tmax, xlabel: "t / s", ylabel: "τ / (N·m)" });
      H.axes();
      H.hline(18.9, muted, [4, 4]); H.hline(-18.9, muted, [4, 4]);
      H.hline(60.9, red, [2, 3]); H.hline(-60.9, red, [2, 3]);
      H.pts(R.ts.map((t, k) => [t, R.taus[k]]), red, 2);
      return;
    }
    const V = this.vib(p), A = Math.max(V.M, 1.2) * 1.15;
    const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: V.Tend, ymin: -A, ymax: A, xlabel: "t（ω_n t）", ylabel: "x" });
    G.axes();
    G.fn((t) => Math.cos(p.r * t), muted, 1);
    G.hline(V.M, red, [5, 4]); G.hline(-V.M, red, [5, 4]);
    G.pts(V.ts.map((t, k) => [t, V.xs[k]]), blue, 1.8);
  },
});
