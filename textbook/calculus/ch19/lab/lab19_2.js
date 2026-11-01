// 实验 19.2 方向场绘图台（配 19.2、19.6 节）。“方程”场景：y′ = x − y、带收获的逻辑斯谛方程 y′ = y(1 − y) − H、
// y′ = y²、排水方程 y′ = −2√y 的方向场；用滑块或在图上点击选初值，画出积分曲线（细步长 RK4），可叠加欧拉折线。
// “机器人”场景：RE 40 电机带风扇，ω′ = (ω∞ − ω)/τ − (c/J)ω²，(t, ω) 平面上的方向场、转速曲线与欧拉折线。
WQ.lab({
  title: ["实验 19.2 方向场绘图台", "Lab 19.2 Direction-field workbench"],
  goal: ["不解方程，从方向场看出积分曲线的形状：平衡解、稳定与不稳定、直线解、有限时间跑到无穷、解不唯一；再用欧拉折线沿着方向场一步步走，看步长的影响。",
         "Read the shape of solution curves straight from the direction field without solving: equilibria, stability, straight-line solutions, finite-time blow-up, non-uniqueness; then walk along the field with Euler polygons and see the effect of the step size."],
  scenes: [
    { id: "motor", robot: true, name: ["电机带风扇", "Motor with a fan"], hide: ["eq", "x0", "y0", "H"],
      problem: { title: ["机器人问题：电机带上风扇后，转速稳定在多少？", "Robot problem: with a fan on the shaft, where does the motor speed settle?"],
                 text: ["maxon RE 40（48 V，τ = RJ/k² ≈ 4.26 ms）的轴上装一个风扇，阻力矩 c ω²。方程 ω′ = (ω∞ − ω)/τ − (c/J)ω² 在 (t, ω) 平面上每一点给出转速曲线的斜率。不解方程，从方向场找出稳态转速，并看从不同初速出发的曲线怎样趋近它。",
                        "A fan with drag torque c ω² is mounted on a maxon RE 40 (48 V, τ = RJ/k² ≈ 4.26 ms). The equation ω′ = (ω∞ − ω)/τ − (c/J)ω² gives the slope of the speed curve at every point of the (t, ω) plane. Find the steady speed from the field without solving, and see how curves from different initial speeds approach it."] } },
    { id: "field", name: ["方程的方向场", "Direction fields"], hide: ["V", "cf", "w0"],
      problem: { title: ["方向场里藏着解的样子", "The shape of the solutions is hidden in the field"],
                 text: ["方程 y′ = f(x, y) 在每一点规定了积分曲线的斜率。选一个方程，用滑块或在图上点击选初值，看积分曲线怎样顺着短线段走。",
                        "The equation y′ = f(x, y) prescribes the slope of the solution curve at every point. Pick an equation, choose an initial point with the sliders or by clicking, and watch the solution follow the little segments."] } },
  ],
  params: [
    { id: "V", name: ["电源电压 V", "Supply voltage V"], min: 12, max: 48, step: 1, value: 48, unit: "V", digits: 0 },
    { id: "cf", name: ["风扇系数 c（×10⁻⁷ N·m·s²）", "Fan coefficient c (×10⁻⁷ N·m·s²)"], min: 0, max: 10, step: 0.1, value: 3.3, digits: 1 },
    { id: "w0", name: ["初始转速 ω₀", "Initial speed ω₀"], min: 0, max: 1200, step: 1, value: 0, unit: "rad/s", digits: 0 },
    { id: "eq", name: ["方程：1 y′ = x − y，2 y′ = y(1 − y) − H，3 y′ = y²，4 y′ = −2√y", "Equation: 1 y′ = x − y, 2 y′ = y(1 − y) − H, 3 y′ = y², 4 y′ = −2√y"], min: 1, max: 4, step: 1, value: 1, digits: 0 },
    { id: "x0", name: ["初值点 x₀", "Initial x₀"], min: -1, max: 4, step: 0.01, value: 0, digits: 2 },
    { id: "y0", name: ["初值点 y₀", "Initial y₀"], min: -2, max: 4, step: 0.01, value: 2, digits: 2 },
    { id: "H", name: ["收获量 H（方程 2）", "Harvest H (equation 2)"], min: 0, max: 0.4, step: 0.005, value: 0, digits: 3 },
    { id: "h", name: ["欧拉法步长 h（0 = 不画；电机场景单位为 ms）", "Euler step h (0 = off; in ms for the motor)"], min: 0, max: 10, step: 0.05, value: 0, digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["积分曲线", "solution curve"], color: "#1f77b4" }, { name: ["欧拉折线", "Euler polygon"], color: "#d62728" }, { name: ["平衡解 / 特殊解", "equilibrium / special solution"], color: "#b8860b" }],
  tasks: [
    { id: "fan", robot: true, text: ["电机带风扇（c = 3.3×10⁻⁷，48 V）：初始转速取多少，转速曲线成为一条水平线？这就是稳态转速。从更低和更高的初速出发，曲线怎样趋近它？", "Motor with fan (c = 3.3×10⁻⁷, 48 V): which initial speed makes the curve a horizontal line? That is the steady speed. How do curves from lower and higher speeds approach it?"],
      demo: { scene: "motor", set: { V: 48, cf: 3.3, w0: 740, h: 0 }, wait: 1 } },
    { id: "line", text: ["y′ = x − y：初值取在哪里，积分曲线是一条直线？其他曲线怎样靠向它？", "y′ = x − y: which initial point gives a straight-line solution? How do the others approach it?"],
      demo: { scene: "field", set: { eq: 1, x0: 0, y0: -1, h: 0 }, wait: 1 } },
    { id: "harv", text: ["y′ = y(1 − y) − H：收获量 H 加大到多少时，两个平衡解合二为一？再大会怎样？", "y′ = y(1 − y) − H: at what harvest H do the two equilibria merge? What happens beyond that?"],
      demo: { scene: "field", set: { eq: 2, H: 0.25, x0: 0, y0: 0.8, h: 0 }, wait: 1 } },
    { id: "blow", text: ["y′ = y²：取 x₀ = 0、y₀ = 2，积分曲线在哪里跑到无穷？用欧拉法（h = 0.1）能看出来吗？", "y′ = y²: with x₀ = 0, y₀ = 2, where does the solution blow up? Can Euler's method (h = 0.1) see it?"],
      demo: { scene: "field", set: { eq: 3, x0: 0, y0: 2, h: 0.1 }, wait: 1 } },
  ],
  think: ["电机场景中把欧拉步长取到 7.4 ms 以上（平衡点附近有效时间常数的两倍），折线会怎样？把风扇系数调为 0，界限变成多少？这对电机控制器里的“模型仿真”有什么启示？（19.6 节）",
          "In the motor scene, take an Euler step above 7.4 ms (twice the effective time constant near equilibrium). What happens to the polygon? With the fan coefficient at 0, where is the limit? What does that mean for model-based simulation inside a motor controller? (Section 19.6)"],

  R: 1.13, K: 0.0603, J: 137e-7,
  f(eq, x, y, H) {
    if (eq === 1) return x - y;
    if (eq === 2) return y * (1 - y) - H;
    if (eq === 3) return y * y;
    return -2 * Math.sqrt(Math.max(y, 0));
  },
  fm(p, w) { const tau = this.R * this.J / this.K ** 2, wi = p.V / this.K; return (wi - w) / tau - p.cf * 1e-7 / this.J * w * w; },
  ws(p) {   // 平衡转速：(k²/R)(ω∞ − ω) = c ω²
    const a = p.cf * 1e-7, b = this.K * this.K / this.R, c0 = -b * p.V / this.K;
    return a === 0 ? p.V / this.K : (-b + Math.sqrt(b * b - 4 * a * c0)) / (2 * a);
  },
  rk(fn, x0, y0, x1, n, lim) {   // 细步长 RK4 从 x0 积到 x1，越界即停
    const pts = [[x0, y0]], h = (x1 - x0) / n;
    let x = x0, y = y0;
    for (let i = 0; i < n; i++) {
      const k1 = fn(x, y), k2 = fn(x + h / 2, y + h / 2 * k1), k3 = fn(x + h / 2, y + h / 2 * k2), k4 = fn(x + h, y + h * k3);
      y += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); x += h;
      if (!isFinite(y) || Math.abs(y) > lim) break;
      pts.push([x, y]);
    }
    return pts;
  },
  euler(fn, x0, y0, x1, h, lim) {
    const pts = [[x0, y0]];
    let x = x0, y = y0;
    for (let i = 0; i < 4000 && x < x1 - 1e-12; i++) {
      y += h * fn(x, y); x += h;
      if (!isFinite(y) || Math.abs(y) > lim) { pts.push([x, Math.sign(y) * lim]); break; }
      pts.push([x, y]);
    }
    return pts;
  },
  start(p, s) { return s.pt ? s.pt : [p.x0, p.y0]; },
  change(api, s, pid) { if (pid === "x0" || pid === "y0" || pid === "eq") s.pt = null; },
  reset(api, s) { s.pt = null; },
  pointer(kind, px, py, api, s) {
    if (api.scene !== "field" || kind !== "down" || !s.G) return;
    const o = s.G.o, x = o.xmin + (px - o.x) / o.w * (o.xmax - o.xmin), y = o.ymin + (o.y + o.h - py) / o.h * (o.ymax - o.ymin);
    if (x >= o.xmin && x <= o.xmax && y >= o.ymin && y <= o.ymax) s.pt = [Math.round(x * 100) / 100, Math.round(y * 100) / 100];
  },
  readouts(api, s) {
    const p = api.p;
    if (api.scene === "motor") {
      const ws = this.ws(p), tau = this.R * this.J / this.K ** 2, fp = -1 / tau - 2 * p.cf * 1e-7 / this.J * ws;
      if (Math.abs(p.cf - 3.3) < 1e-9 && p.V === 48 && Math.abs(p.w0 - ws) / ws < 0.01) api.done("fan");
      const rows = [[["稳态转速 ω*（f(ω*) = 0）", "steady speed ω* (f(ω*) = 0)"], ws.toFixed(1) + " rad/s"],
                    [["稳态电流", "steady current"], ((p.V - this.K * ws) / this.R).toFixed(2) + " A"],
                    [["初值处的斜率 f(ω₀)", "slope at ω₀, f(ω₀)"], (Math.abs(this.fm(p, p.w0)) < 50 ? "0.0" : (this.fm(p, p.w0) / 1000).toFixed(1)) + " rad/s per ms"],
                    [["空载时间常数 τ = RJ/k²", "no-load time constant τ"], (tau * 1000).toFixed(2) + " ms"],
                    [["平衡点附近的有效时间常数 −1/f′(ω*)", "effective time constant −1/f′(ω*)"], (-1000 / fp).toFixed(2) + " ms"]];
      if (p.h > 0) {
        const r = 1 - p.h / 1000 / (-1 / fp);
        rows.push([["欧拉法：平衡点附近每步的误差放大倍数 1 + h f′(ω*)", "Euler: error factor per step near ω*, 1 + h f′(ω*)"], r.toFixed(3) + (Math.abs(r) > 1 ? api.T("（发散）", " (diverges)") : "")]);
      }
      return rows;
    }
    const [x0, y0] = this.start(p, s), eq = p.eq;
    const rows = [[["初值点 (x₀, y₀)", "initial point (x₀, y₀)"], "(" + x0.toFixed(2) + ", " + y0.toFixed(2) + ")"],
                  [["该点的斜率 f(x₀, y₀)", "slope f(x₀, y₀)"], this.f(eq, x0, y0, p.H).toFixed(3)]];
    if (eq === 1) {
      const C = (y0 - x0 + 1) * Math.exp(x0);
      if (Math.abs(y0 - (x0 - 1)) < 0.02) api.done("line");
      rows.push([["公式解 y = x − 1 + Ce^(−x) 中的 C", "C in y = x − 1 + Ce^(−x)"], C.toFixed(3)]);
    } else if (eq === 2) {
      const d = 1 - 4 * p.H;
      if (p.H >= 0.245 && p.H <= 0.25 + 1e-9) api.done("harv");
      rows.push([["平衡解（y − y² = H 的根）", "equilibria (roots of y − y² = H)"], d > 1e-12 ? ((1 - Math.sqrt(d)) / 2).toFixed(3) + api.T("（不稳定）、", " (unstable), ") + ((1 + Math.sqrt(d)) / 2).toFixed(3) + api.T("（稳定）", " (stable)") : Math.abs(d) <= 1e-12 ? "0.500" + api.T("（半稳定）", " (semi-stable)") : api.T("没有：所有解都跑向 −∞", "none: every solution runs to −∞")]);
    } else if (eq === 3) {
      if (Math.abs(x0) < 0.02 && Math.abs(y0 - 2) < 0.02) api.done("blow");
      rows.push([["公式解 y = 1/(1/y₀ − (x − x₀))", "solution y = 1/(1/y₀ − (x − x₀))"], y0 > 0 ? api.T("x → ", "blows up at x → ") + (x0 + 1 / y0).toFixed(3) + api.T(" 时跑到 +∞", "") : y0 === 0 ? "y ≡ 0" : api.T("向右趋于 0", "tends to 0 to the right")]);
    } else {
      rows.push([["公式解 y = (√y₀ − (x − x₀))²，流空于", "solution y = (√y₀ − (x − x₀))², empty at"], y0 > 0 ? "x = " + (x0 + Math.sqrt(y0)).toFixed(3) : api.T("已经是 0（向左看不唯一）", "already 0 (not unique to the left)")]);
    }
    if (p.h > 0) {
      const E = this.euler((x, y) => this.f(eq, x, y, p.H), x0, y0, 4, p.h, 1e6);
      const R = this.rk((x, y) => this.f(eq, x, y, p.H), x0, y0, E[E.length - 1][0], 2000, 1e6);
      const last = E[E.length - 1], lr = R[R.length - 1];
      rows.push([["欧拉折线的终点", "end of Euler polygon"], "(" + last[0].toFixed(2) + ", " + (Math.abs(last[1]) >= 1e6 ? "∞" : last[1].toFixed(3)) + ")"]);
      if (Math.abs(lr[0] - last[0]) < 1e-6) rows.push([["同一处的积分曲线", "solution at the same x"], lr[1].toFixed(3)]);
    }
    return rows;
  },
  draw(api, s) {
    const p = api.p, w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), amber = api.css("--amber") || "#b8860b", muted = api.css("--muted");
    const motor = api.scene === "motor";
    const G = motor ? api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: 25, ymin: 0, ymax: 1200, xlabel: "t / ms", ylabel: "ω / (rad/s)" })
                    : api.graph({ x: 60, y: 24, w: w - 80, h: h - 74, xmin: -1, xmax: 4, ymin: -2, ymax: 4, xlabel: "x", ylabel: "y" });
    s.G = G;
    G.axes();
    const o = G.o, sx = o.w / (o.xmax - o.xmin), sy = o.h / (o.ymax - o.ymin);
    const fn = motor ? (t, y) => this.fm(p, y) / 1000 : (x, y) => this.f(p.eq, x, y, p.H);   // 电机：t 以 ms 计
    const nx = Math.max(10, Math.round(o.w / 34)), ny = Math.max(8, Math.round(o.h / 30));
    for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
      const x = o.xmin + (i + 0.5) / nx * (o.xmax - o.xmin), y = o.ymin + (j + 0.5) / ny * (o.ymax - o.ymin);
      const m = fn(x, y), dx = sx, dy = m * sy, L = Math.hypot(dx, dy) || 1, r = 10;
      const cx = G.X(x), cy = G.Y(y);
      api.line(cx - dx / L * r, cy + dy / L * r, cx + dx / L * r, cy - dy / L * r, muted, 1.2);
    }
    if (motor) {
      G.hline(this.ws(p), amber, [6, 4]);
      G.pts(this.rk(fn, 0, p.w0, 25, 1000, 1e5), blue, 2.5);
      G.point(0, p.w0, blue);
      if (p.h > 0) { const E = this.euler(fn, 0, p.w0, 25, p.h, 1e5); G.pts(E, red, 2); G.dots(E, red, 3); }
      return;
    }
    const [x0, y0] = this.start(p, s), f = (x, y) => this.f(p.eq, x, y, p.H);
    if (p.eq === 1) G.fn((x) => x - 1, amber, 2, [6, 4]);
    if (p.eq === 2 && 1 - 4 * p.H >= 0) { const d = Math.sqrt(1 - 4 * p.H); G.hline((1 - d) / 2, amber, [6, 4]); G.hline((1 + d) / 2, amber, [6, 4]); }
    if (p.eq === 3 || p.eq === 4) G.hline(0, amber, [6, 4]);
    G.pts(this.rk(f, x0, y0, o.xmax, 1500, 1e3), blue, 2.5);
    if (!(p.eq === 4 && y0 <= 0)) G.pts(this.rk(f, x0, y0, o.xmin, 1500, 1e3), blue, 2.5);
    G.point(x0, y0, blue);
    if (p.h > 0) { const E = this.euler(f, x0, y0, o.xmax, p.h, 1e3); G.pts(E, red, 2); G.dots(E, red, 3); }
  },
});
