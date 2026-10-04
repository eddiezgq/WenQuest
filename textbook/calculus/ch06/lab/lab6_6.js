// 实验 6.6 有限次检查能否证明安全（配 6.6 节）。两节连杆（UR5e 上臂 0.425 m、前臂 0.392 m，取自问渠零件库）1 s 内关节角匀速变化，
// 安全裕量 g(t) = d(t) − s，d 为末端到障碍点的距离，s = 50 mm；g 的利普希茨常数 K = (l₁ + l₂)|ω₁| + l₂|ω₂|。
WQ.lab({
  title: ["实验 6.6 有限次检查能否证明安全", "Lab 6.6 Can finitely many checks prove safety?"],
  goal: ["看清“采样点都安全”与“处处安全”的区别；用利普希茨常数把有限个采样值变成处处成立的下界；用自适应二分检查以较少的计算得出结论。",
         "See the difference between 'all samples are safe' and 'safe everywhere'; turn finitely many samples into a lower bound valid everywhere with a Lipschitz constant; reach a verdict with few evaluations by adaptive bisection."],
  scenes: [
    { id: "grid", name: ["等距采样", "Uniform sampling"], hide: [],
      problem: { title: ["采样点都离障碍够远，整个运动就安全吗？", "If every sample keeps clear, is the whole motion safe?"],
                 text: ["手臂末端在 1 s 内扫过障碍附近。每隔 h 秒算一次末端到障碍的距离，减去安全距离 50 mm 得到裕量。采样点的裕量都为正，能说明什么？",
                        "The end-effector sweeps past an obstacle in 1 s. Every h seconds compute its distance to the obstacle minus the 50 mm safety distance. What do positive margins at the samples tell you?"] } },
    { id: "adapt", robot: true, name: ["自适应二分检查", "Adaptive bisection check"], hide: ["N"],
      problem: { title: ["机器人问题：用尽量少的计算证明不碰撞，或找出碰撞时刻", "Robot problem: prove no collision with few evaluations, or find when it happens"],
                 text: ["在区间中点算裕量 g(m)：g(m) ≤ 0 即碰撞；g(m) > K·区间长/2 即整个区间安全；否则二等分继续检查。",
                        "Evaluate the margin g(m) at the midpoint: g(m) ≤ 0 means collision; g(m) > K·length/2 means the whole interval is safe; otherwise split in two and continue."] } },
  ],
  params: [
    { id: "o", name: ["障碍：1 较远，2 较近", "Obstacle: 1 farther, 2 nearer"], min: 1, max: 2, step: 1, value: 1, digits: 0 },
    { id: "N", name: ["采样区间数 N（步长 h = 1/N s）", "Number of intervals N (step h = 1/N s)"], min: 4, max: 80, step: 1, value: 10, digits: 0 },
  ],
  buttons: [{ id: "step", name: ["检查一步", "One check"], primary: true }, { id: "run", name: ["检查到底", "Check to the end"] }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["安全裕量 g(t)", "margin g(t)"], color: "#222222" }, { name: ["由采样保证的下界", "guaranteed bound"], color: "#c98f00" },
           { name: ["已证明安全", "proved safe"], color: "#2ca02c" }, { name: ["碰撞", "collision"], color: "#d62728" }],
  tasks: [
    { id: "miss", text: ["选障碍 2、N = 10（步长 0.1 s）：采样点的裕量都为正，下界却跌破 0，不能证明安全。", "Obstacle 2, N = 10 (step 0.1 s): all sample margins are positive, yet the bound drops below 0 — no proof."],
      demo: { scene: "grid", set: { o: 2, N: 10 }, press: [], wait: 1 } },
    { id: "find", text: ["仍选障碍 2，增大 N（减小步长），直到有采样点的裕量为负（发现碰撞）。", "Still obstacle 2: increase N (shrink the step) until some sample margin is negative (collision found)."],
      demo: { scene: "grid", set: { o: 2, N: 40 }, press: [], wait: 1 } },
    { id: "prove", text: ["选障碍 1，找一个 N，使保证的下界为正（证明安全）。", "Obstacle 1: find an N that makes the guaranteed bound positive (safety proved)."],
      demo: { scene: "grid", set: { o: 1, N: 20 }, press: [], wait: 1 } },
    { id: "adapt", robot: true, text: ["在“自适应二分检查”中选障碍 2，检查到底，找出碰撞的时刻。", "In 'Adaptive bisection check' choose obstacle 2, run to the end and find when the collision happens."],
      demo: { scene: "adapt", set: { o: 2 }, press: ["run"], wait: 1 } },
  ],
  think: ["若不知道利普希茨常数 K，只知道 g 连续，还能用有限次计算证明 g > 0 吗？为什么？",
          "Without the Lipschitz constant K, knowing only that g is continuous, can finitely many evaluations prove g > 0? Why?"],

  // geometry
  L1: 0.425, L2: 0.392, A: [10, 100], B: [80, 20], S: 0.05,
  obs(api) { return api.p.o === 2 ? [0.176, 0.634] : [0.36, 0.62]; },
  K() { const d = Math.PI / 180, w1 = (this.B[0] - this.A[0]) * d, w2 = (this.B[1] - this.A[1]) * d; return (this.L1 + this.L2) * Math.abs(w1) + this.L2 * Math.abs(w2); },
  ee(t) {
    const d = Math.PI / 180, t1 = (this.A[0] + (this.B[0] - this.A[0]) * t) * d, t2 = (this.A[1] + (this.B[1] - this.A[1]) * t) * d;
    return [this.L1 * Math.cos(t1) + this.L2 * Math.cos(t1 + t2), this.L1 * Math.sin(t1) + this.L2 * Math.sin(t1 + t2)];
  },
  g(api, t) { const p = this.ee(t), o = this.obs(api); return Math.hypot(p[0] - o[0], p[1] - o[1]) - this.S; },
  grid(api) {
    const n = api.p.N, K = this.K(), ts = [], gs = [];
    for (let i = 0; i <= n; i++) { const t = i / n; ts.push(t); gs.push(this.g(api, t)); }
    // lower bound on each piece between neighbouring samples: max of the two cones' minima there
    let lb = Infinity;
    for (let i = 0; i + 1 < ts.length; i++) {
      const a = ts[i], b = ts[i + 1], ga = gs[i], gb = gs[i + 1];
      const tc = (ga - gb + K * (a + b)) / (2 * K);            // where the two cones meet
      const v = Math.max(ga - K * (Math.min(Math.max(tc, a), b) - a), gb - K * (b - Math.min(Math.max(tc, a), b)));
      lb = Math.min(lb, v);
    }
    return { ts, gs, K, lb, mins: Math.min(...gs) };
  },
  reset(api, s) { Object.assign(s, { stack: [[0, 1]], safe: [], evals: 0, hit: null, done: false, mids: [] }); },
  one(api, s) {
    if (s.done || !s.stack.length) { s.done = true; return false; }
    const [a, b] = s.stack.pop(), m = (a + b) / 2, gm = this.g(api, m), K = this.K();
    s.evals++; s.mids.push([m, gm]);
    if (gm <= 0) { s.hit = m; s.done = true; return false; }
    if (gm > K * (b - a) / 2) s.safe.push([a, b]);
    else if (b - a < 1e-6) { s.done = true; s.stuck = true; return false; }
    else s.stack.push([m, b], [a, m]);
    if (!s.stack.length) s.done = true;
    return !s.done;
  },
  action(id, api, s) {
    if (api.scene !== "adapt") return;
    if (id === "step") this.one(api, s);
    if (id === "run") { let n = 0; while (n++ < 10000 && this.one(api, s)); }
    if (api.p.o === 2 && s.hit !== null) api.done("adapt");
  },
  readouts(api, s) {
    const mm = (v) => (v * 1000).toFixed(2) + " mm", K = this.K();
    if (api.scene === "adapt") {
      const v = s.hit !== null ? api.T("在 t = " + s.hit.toFixed(4) + " s 发现碰撞", "collision at t = " + s.hit.toFixed(4) + " s")
        : s.done ? (s.stuck ? api.T("区间已极小，仍无法判断（擦边）", "interval tiny, still undecided (grazing)") : api.T("已证明整个 [0, 1] 安全", "the whole [0, 1] is proved safe"))
        : api.T("检查中", "checking");
      return [[["利普希茨常数 K", "Lipschitz constant K"], K.toFixed(3) + " m/s"],
              [["已计算 g 的次数", "Evaluations of g"], String(s.evals)],
              [["已证明安全的区间个数", "Intervals proved safe"], String(s.safe.length)],
              [["待检查的区间个数", "Intervals pending"], String(s.stack.length)],
              [["结论", "Verdict"], v]];
    }
    const G = this.grid(api);
    if (api.p.o === 2 && api.p.N === 10 && G.mins > 0 && G.lb < 0) api.done("miss");
    if (api.p.o === 2 && G.mins <= 0) api.done("find");
    if (api.p.o === 1 && G.lb > 0) api.done("prove");
    const v = G.mins <= 0 ? api.T("有采样点裕量 ≤ 0：发现碰撞", "a sample has margin ≤ 0: collision found")
      : G.lb > 0 ? api.T("下界为正：证明了处处安全", "bound positive: safe everywhere, proved")
      : api.T("采样点都安全，但下界 < 0：无法判断，需加密", "samples safe but bound < 0: undecided, refine");
    return [[["采样点个数", "Samples"], String(G.ts.length)],
            [["采样点的最小裕量", "Smallest sample margin"], mm(G.mins)],
            [["由采样保证的下界", "Guaranteed lower bound"], mm(G.lb)],
            [["利普希茨常数 K", "Lipschitz constant K"], K.toFixed(3) + " m/s"],
            [["结论", "Verdict"], v]];
  },
  draw(api, s) {
    const w = api.w, h = api.h, ink = api.css("--ink"), red = api.css("--red"), green = api.css("--green"), blue = api.css("--blue"), amber = "#c98f00";
    const G = api.graph({ x: 64, y: 22, w: w - 84, h: h - 70, xmin: 0, xmax: 1, ymin: -40, ymax: 160, xlabel: "t / s", ylabel: api.T("裕量 / mm", "margin / mm") });
    G.axes();
    const ctx = api.ctx;
    if (api.scene === "adapt") {
      ctx.fillStyle = "rgba(44,160,44,0.18)";
      s.safe.forEach(([a, b]) => ctx.fillRect(G.X(a), G.o.y, Math.max(1, G.X(b) - G.X(a)), G.o.h));
      G.fn((t) => this.g(api, t) * 1000, ink, 2);
      G.dots(s.mids.map(([m, gm]) => [m, gm * 1000]), blue, 3);
      if (s.hit !== null) G.point(s.hit, this.g(api, s.hit) * 1000, red, api.T("碰撞", "collision"));
      G.hline(0, red);
      return;
    }
    const D = this.grid(api), K = this.K();
    G.fn((t) => this.g(api, t) * 1000, ink, 2);
    const pts = [];
    for (let i = 0; i + 1 < D.ts.length; i++) {
      const a = D.ts[i], b = D.ts[i + 1], ga = D.gs[i], gb = D.gs[i + 1];
      for (let k = 0; k <= 20; k++) { const t = a + (b - a) * k / 20; pts.push([t, Math.max(ga - K * (t - a), gb - K * (b - t)) * 1000]); }
    }
    G.pts(pts, amber, 1.5);
    G.dots(D.ts.map((t, i) => [t, D.gs[i] * 1000]), blue, 3.5);
    G.hline(0, red);
  },
});
