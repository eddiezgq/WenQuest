// 实验 5.6 关节轨迹的三次样条与追赶法（配 5.6.3 节）。一个关节在 t = 0, h, 2h, …, 5h 经过 6 个路点（首末两点固定为 0° 与 40°），
// 自然三次样条的内点二阶导数 M₁…M₄ 满足三对角方程组 M_{i−1} + 4M_i + M_{i+1} = 6(θ_{i+1} − 2θ_i + θ_{i−1})/h²，用追赶法求解。
WQ.lab({
  title: ["实验 5.6 关节轨迹的三次样条与追赶法", "Lab 5.6 Cubic-spline joint trajectories and the tridiagonal solver"],
  goal: ["拖动中间四个路点和每段的时长，看三对角方程组、样条轨迹、角速度和角加速度怎样变化；让轨迹满足关节的加速度限制。",
         "Drag the four middle waypoints and the segment time; watch the tridiagonal system, the spline, the velocity and the acceleration change; make the trajectory respect the joint's acceleration limit."],
  scenes: [
    { id: "joint", robot: true, name: ["UR5e 肩关节", "UR5e shoulder joint"],
      problem: { title: ["机器人问题：平滑地经过每个路点", "Robot problem: pass every waypoint smoothly"],
                 text: ["示教时记下了 6 个路点。控制器要生成一条经过全部路点、位置、速度和加速度都连续的轨迹，而且角加速度不能超过电机的能力（本实验取 50°/s²）。",
                        "Six waypoints were taught. The controller needs a trajectory through all of them with continuous position, velocity and acceleration, and the angular acceleration must stay within the motor's limit (50°/s² here)."] } },
  ],
  params: [
    { id: "q1", name: ["路点 θ₁", "Waypoint θ₁"], min: -60, max: 120, step: 5, value: 20, unit: "°", digits: 0 },
    { id: "q2", name: ["路点 θ₂", "Waypoint θ₂"], min: -60, max: 120, step: 5, value: 60, unit: "°", digits: 0 },
    { id: "q3", name: ["路点 θ₃", "Waypoint θ₃"], min: -60, max: 120, step: 5, value: 90, unit: "°", digits: 0 },
    { id: "q4", name: ["路点 θ₄", "Waypoint θ₄"], min: -60, max: 120, step: 5, value: 70, unit: "°", digits: 0 },
    { id: "h", name: ["每段时长 h", "Segment time h"], min: 0.5, max: 3, step: 0.1, value: 1, unit: "s", digits: 1 },
  ],
  buttons: [{ id: "book", name: ["与书中结果对照", "Compare with the book"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "book", text: ["保持默认路点和 h = 1 s，读出 M₁…M₄，点“与书中结果对照”。", "Keep the default waypoints and h = 1 s, read M₁…M₄ and press Compare with the book."],
      demo: { scene: "joint", set: { q1: 20, q2: 60, q3: 90, q4: 70, h: 1 }, press: ["book"], wait: 2 } },
    { id: "slow", text: ["路点不变，只加大 h，使最大角加速度不超过 50°/s²。h 至少要多大？", "Keep the waypoints and increase h until the peak acceleration is at most 50°/s². How large must h be?"],
      demo: { scene: "joint", set: { q1: 20, q2: 60, q3: 90, q4: 70, h: 1.3 }, press: [], wait: 2 } },
    { id: "shape", text: ["h = 1 s 不变，只改中间路点（θ₃ 不低于 70°），使最大角加速度不超过 50°/s²。", "Keep h = 1 s and change only the middle waypoints (θ₃ at least 70°) so that the peak acceleration is at most 50°/s²."],
      demo: { scene: "joint", set: { q1: 25, q2: 55, q3: 70, q4: 60, h: 1 }, press: [], wait: 2 } },
    { id: "check", text: ["改变路点或时长后，确认追赶法与一般的高斯消元给出的 M₁…M₄ 相差小于 10⁻⁹。", "After changing the waypoints or the segment time, check that the tridiagonal solver and general Gaussian elimination give M₁…M₄ within 10⁻⁹."],
      demo: { scene: "joint", set: { q1: 0, q2: 30, q3: 100, q4: 50, h: 0.8 }, press: [], wait: 2 } },
  ],
  think: ["为什么把每段时长 h 加倍，角加速度变为原来的四分之一？若只允许改变某一段的时长，方程组还是这个形式吗？",
          "Why does doubling h divide the acceleration by four? If only one segment's duration could change, would the system keep this form?"],

  action(id, api) { if (id === "book") this.booked = true; },
  pts(api) { return [0, api.p.q1, api.p.q2, api.p.q3, api.p.q4, 40]; },
  system(api) {   // the 4×4 tridiagonal system for M₁…M₄
    const q = this.pts(api), h = api.p.h, d = [];
    for (let i = 1; i <= 4; i++) d.push(6 * (q[i + 1] - 2 * q[i] + q[i - 1]) / (h * h));
    return { a: [0, 1, 1, 1], b: [4, 4, 4, 4], c: [1, 1, 1, 0], d };
  },
  thomas({ a, b, c, d }) {
    const n = b.length, cp = [], dp = [];
    cp[0] = c[0] / b[0]; dp[0] = d[0] / b[0];
    for (let i = 1; i < n; i++) { const m = b[i] - a[i] * cp[i - 1]; cp[i] = c[i] / m; dp[i] = (d[i] - a[i] * dp[i - 1]) / m; }
    const x = new Array(n); x[n - 1] = dp[n - 1];
    for (let i = n - 2; i >= 0; i--) x[i] = dp[i] - cp[i] * x[i + 1];
    return x;
  },
  dense({ a, b, c, d }) {   // the same system by general elimination with partial pivoting
    const n = b.length, M = Array.from({ length: n }, (_, i) => Array.from({ length: n + 1 }, (_, j) => (j === n ? d[i] : j === i ? b[i] : j === i - 1 ? a[i] : j === i + 1 ? c[i] : 0)));
    for (let k = 0; k < n; k++) {
      let p = k; for (let i = k + 1; i < n; i++) if (Math.abs(M[i][k]) > Math.abs(M[p][k])) p = i;
      [M[k], M[p]] = [M[p], M[k]];
      for (let i = k + 1; i < n; i++) { const l = M[i][k] / M[k][k]; for (let j = k; j <= n; j++) M[i][j] -= l * M[k][j]; }
    }
    const x = new Array(n);
    for (let i = n - 1; i >= 0; i--) { let s = M[i][n]; for (let j = i + 1; j < n; j++) s -= M[i][j] * x[j]; x[i] = s / M[i][i]; }
    return x;
  },
  spline(api) {   // samples of θ, θ', θ'' over [0, 5h]
    const q = this.pts(api), h = api.p.h, Mi = this.thomas(this.system(api)), M = [0, ...Mi, 0], out = [];
    for (let s = 0; s <= 500; s++) {
      const t = 5 * h * s / 500, i = Math.min(4, Math.floor(t / h)), u = t - i * h, v = h - u;
      const th = M[i] * v ** 3 / (6 * h) + M[i + 1] * u ** 3 / (6 * h) + (q[i] / h - M[i] * h / 6) * v + (q[i + 1] / h - M[i + 1] * h / 6) * u;
      const dth = -M[i] * v * v / (2 * h) + M[i + 1] * u * u / (2 * h) - (q[i] / h - M[i] * h / 6) + (q[i + 1] / h - M[i + 1] * h / 6);
      const ddth = M[i] * v / h + M[i + 1] * u / h;
      out.push([t, th, dth, ddth]);
    }
    return { M: Mi, out };
  },
  readouts(api) {
    const sys = this.system(api), { M, out } = this.spline(api), Md = this.dense(sys);
    const amax = Math.max(...out.map((r) => Math.abs(r[3]))), vmax = Math.max(...out.map((r) => Math.abs(r[2])));
    const diff = Math.max(...M.map((x, i) => Math.abs(x - Md[i])));
    const p = api.p, dflt = p.q1 === 20 && p.q2 === 60 && p.q3 === 90 && p.q4 === 70;
    if (this.booked && dflt && p.h === 1) api.done("book");
    if (dflt && amax <= 50) api.done("slow");
    if (p.h === 1 && p.q3 >= 70 && amax <= 50) api.done("shape");
    if (!(dflt && p.h === 1) && diff < 1e-9) api.done("check");
    return [[["右端 6(θᵢ₊₁ − 2θᵢ + θᵢ₋₁)/h²", "Right side 6(θᵢ₊₁ − 2θᵢ + θᵢ₋₁)/h²"], api.la.vstr(sys.d, 2)],
            [["追赶法：M₁…M₄（°/s²）", "Tridiagonal solver: M₁…M₄ (°/s²)"], api.la.vstr(M, 2)],
            [["一般消元：M₁…M₄", "General elimination: M₁…M₄"], api.la.vstr(Md, 2)],
            [["两者最大差", "Largest difference"], diff.toExponential(1)],
            [["最大角速度", "Peak velocity"], api.fmt(vmax, 1) + " °/s"],
            [["最大角加速度（限 50）", "Peak acceleration (limit 50)"], api.fmt(amax, 1) + " °/s²"],
            [["总时长", "Total time"], api.fmt(5 * p.h, 1) + " s"]];
  },
  draw(api) {
    const { w, h } = api, { out } = this.spline(api), q = this.pts(api), H = api.p.h, muted = api.css("--muted");
    const T = 5 * H, panels = [[1, api.css("--blue"), api.T("关节角 / °", "angle / °"), [-80, 140]], [2, api.css("--green"), api.T("角速度 / (°/s)", "velocity / (°/s)"), null],
                                [3, api.css("--red"), api.T("角加速度 / (°/s²)", "acceleration / (°/s²)"), null]];
    const ph = (h - 30) / 3;
    panels.forEach(([k, col, name, rng], j) => {
      const y0 = 10 + j * ph, y1 = y0 + ph - 18, x0 = 60, x1 = w - 20;
      const vals = out.map((r) => r[k]);
      let lo = rng ? rng[0] : Math.min(...vals, k === 3 ? -60 : 0), hi = rng ? rng[1] : Math.max(...vals, k === 3 ? 60 : 0);
      if (hi - lo < 1e-9) { lo -= 1; hi += 1; }
      const X = (t) => x0 + (x1 - x0) * t / T, Y = (v) => y1 - (y1 - y0) * (v - lo) / (hi - lo);
      api.rect(x0, y0, x1 - x0, y1 - y0, null, api.css("--grid"));
      if (lo < 0 && hi > 0) api.line(x0, Y(0), x1, Y(0), muted, 1);
      if (k === 3) [50, -50].forEach((v) => { if (v > lo && v < hi) api.line(x0, Y(v), x1, Y(v), api.css("--amber"), 1); });
      const g = api.ctx; g.beginPath(); out.forEach((r, i) => (i ? g.lineTo(X(r[0]), Y(r[k])) : g.moveTo(X(r[0]), Y(r[k])))); g.strokeStyle = col; g.lineWidth = 2; g.stroke();
      if (k === 1) q.forEach((v, i) => api.circle(X(i * H), Y(v), 4.5, api.css("--ink"), null));
      api.label(name, x0 + 6, y0 + 14, muted, 12);
      api.label(api.fmt(hi, 0), x0 - 6, y0 + 10, muted, 10, "right"); api.label(api.fmt(lo, 0), x0 - 6, y1, muted, 10, "right");
    });
    api.label("t / s: 0 … " + api.fmt(5 * H, 1), w - 20, h - 6, muted, 11, "right");
  },
});
