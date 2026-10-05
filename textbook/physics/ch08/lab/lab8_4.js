// 实验 8.4 积分器与实测（配 8.2–8.4 节）。
// 发球场景：网球（58 g，直径 6.7 cm）在 1.0 m 高处以 25 m/s、仰角 10° 射出。“实测数据”是频闪照片上每隔 0.05 s 的位置：
// 由真实的 C_d = 0.58（学生不知道）用 RK4、h = 0.1 ms 算出，再加上 ±5 mm 以内的读数误差（按序号确定的伪随机数）。
// 学生选积分方法、步长和 C_d，仿真曲线与数据的均方根偏差显示在“测量”栏，调 C_d 使偏差最小，提交。
// 任务 1：用 RK4 拟合，C_d 与真值相差 0.01 以内。任务 2：用欧拉法、h = 0.05 s 拟合，提交它给出的（有偏的）C_d，
// 与按同样方法和步长求出的最佳值相差 0.01 以内——说明积分误差会混进参数辨识的结果。
// 振子场景：弹簧振子在相平面上，选方法和 ωh，与精确解（单位圆）比较。任务 3：半隐式欧拉法不发散的最大 ωh（0.05 一档）。
const g84 = 9.81, M84 = 0.058, D84 = 0.067, RHO84 = 1.20, CD84 = 0.58, V84 = 25, TH84 = 10 * Math.PI / 180, Y84 = 1.0, DT84 = 0.05;
const HS84 = [0.001, 0.002, 0.005, 0.01, 0.025, 0.05];
function h84(a, b) { const x = Math.sin(a * 12.9898 + b * 78.233 + 4.56) * 43758.5453; return x - Math.floor(x); }
function f84(s, cd) {
  const k = 0.5 * RHO84 * cd * Math.PI * D84 * D84 / 4 / M84, v = Math.hypot(s[2], s[3]);
  return [s[2], s[3], -k * v * s[2], -g84 - k * v * s[3]];
}
const add84 = (a, b, c) => a.map((x, i) => x + c * b[i]);
function step84(s, h, cd, method) {
  if (method === 0) return add84(s, f84(s, cd), h);
  if (method === 1) { const a = f84(s, cd), v = [s[2] + h * a[2], s[3] + h * a[3]]; return [s[0] + h * v[0], s[1] + h * v[1], v[0], v[1]]; }
  const k1 = f84(s, cd), k2 = f84(add84(s, k1, h / 2), cd), k3 = f84(add84(s, k2, h / 2), cd), k4 = f84(add84(s, k3, h), cd);
  return s.map((x, i) => x + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
}
function sim84(cd, h, method) {                                     // 返回每隔 0.05 s 的位置（直到落地）与整条轨迹
  let s = [0, Y84, V84 * Math.cos(TH84), V84 * Math.sin(TH84)];
  const every = Math.round(DT84 / h), samp = [[s[0], s[1]]], path = [[s[0], s[1]]];
  for (let n = 1; n <= 3 / h && s[1] > -0.5; n++) {
    s = step84(s, h, cd, method); path.push([s[0], s[1]]);
    if (n % every === 0) samp.push([s[0], s[1]]);
  }
  return { samp, path };
}
const DATA84 = (() => {                                             // “实测”：真值加读数误差，只保留落地前的点
  const r = sim84(CD84, 0.0001, 2).samp;
  return r.filter((p) => p[1] > 0).map((p, i) => [p[0] + 0.01 * (h84(i, 1) - 0.5), p[1] + 0.01 * (h84(i, 2) - 0.5)]);
})();
function rms84(cd, h, method) {
  const S = sim84(cd, h, method).samp;
  let q = 0; DATA84.forEach((p, i) => { const s = S[i] || S[S.length - 1]; q += (s[0] - p[0]) ** 2 + (s[1] - p[1]) ** 2; });
  return Math.sqrt(q / DATA84.length);
}
function best84(h, method) {                                        // 黄金分割求使偏差最小的 C_d
  let a = 0.3, b = 0.9; const r = 0.618034;
  for (let i = 0; i < 40; i++) { const c = b - r * (b - a), d = a + r * (b - a); if (rms84(c, h, method) < rms84(d, h, method)) b = d; else a = c; }
  return (a + b) / 2;
}
const EULER84 = best84(0.05, 0);
const NAMES84 = [["欧拉法", "Euler"], ["半隐式欧拉法", "semi-implicit Euler"], ["RK4", "RK4"]];
function osc84(method, z, n) {                                      // 弹簧振子，状态 (x, v/ω)，每步 ωh = z
  let x = 1, u = 0; const pts = [[x, u]];
  for (let i = 0; i < n; i++) {
    if (method === 0) { [x, u] = [x + z * u, u - z * x]; }
    else if (method === 1) { u = u - z * x; x = x + z * u; }
    else {
      const F = (p) => [p[1], -p[0]], a = [x, u], k1 = F(a), k2 = F(add84(a, k1, z / 2)), k3 = F(add84(a, k2, z / 2)), k4 = F(add84(a, k3, z));
      x += z / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); u += z / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]);
    }
    pts.push([x, u]);
    if (Math.abs(x) > 50 || Math.abs(u) > 50) break;
  }
  return pts;
}

WQ.lab({
  title: ["实验 8.4 积分器与实测", "Lab 8.4 Integrators against measurements"],
  goal: ["用不同的积分方法和步长仿真带空气阻力的网球，与频闪照片的实测数据比较，求出阻力系数；在相平面上比较三种方法计算振动。",
         "Simulate a tennis ball with air drag using different integrators and steps, compare with strobe-photo measurements to find the drag coefficient, and compare three methods on an oscillator in the phase plane."],
  scenes: [
    { id: "serve", robot: true, name: ["发球机器人", "Ball launcher"], hide: ["wh"],
      problem: { title: ["机器人问题：网球的阻力系数是多少？", "Robot problem: what is the ball's drag coefficient?"],
                 text: ["发球机器人在 1.0 m 高处以 25 m/s、仰角 10° 射出网球，频闪照片每隔 0.05 s 记下一个位置（图中的点，误差在 ±5 mm 以内）。选积分方法和步长，调 C_d，使仿真曲线与数据的均方根偏差最小，提交 C_d。",
                        "The launcher fires the ball at 25 m/s, 10° up, from 1.0 m; a strobe photo records its position every 0.05 s (dots, error within ±5 mm). Pick an integrator and a step, tune C_d to minimise the RMS deviation between simulation and data, and submit C_d."] } },
    { id: "osc", name: ["相平面上的振子", "An oscillator in the phase plane"], hide: ["hi", "cd"],
      problem: { title: ["三种方法算同一个振子", "Three methods on one oscillator"],
                 text: ["弹簧振子从 x = 1 静止释放，精确解在相平面（x，v/ω）上是单位圆。选方法和 ωh，点“开始”，看 20 个周期内数值解的轨迹。",
                        "An oscillator is released from x = 1; the exact motion is the unit circle in the (x, v/ω) plane. Pick a method and ωh, press “Start” and watch 20 periods of the numerical solution."] } },
  ],
  params: [
    { id: "method", name: ["方法：0 欧拉，1 半隐式欧拉，2 RK4", "Method: 0 Euler, 1 semi-implicit, 2 RK4"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "hi", name: ["步长 h：0 → 1 ms … 5 → 50 ms", "Step h: 0 → 1 ms … 5 → 50 ms"], min: 0, max: 5, step: 1, value: 5, unit: "", digits: 0 },
    { id: "cd", name: ["阻力系数 C_d", "Drag coefficient C_d"], min: 0.3, max: 0.9, step: 0.001, value: 0.45, unit: "", digits: 3 },
    { id: "wh", name: ["ωh", "ωh"], min: 0.05, max: 3, step: 0.05, value: 0.2, unit: "", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--ink)", name: ["实测数据 / 精确解", "data / exact"] }, { color: "var(--red)", name: ["数值解", "numerical"] }],
  tasks: [
    { id: "fit", robot: true, text: ["发球机器人：用 RK4 拟合，提交 C_d（与真值相差 0.01 以内）。", "Launcher: fit with RK4 and submit C_d (within 0.01 of the true value)."],
      demo: { scene: "serve", set: { method: 2, hi: 3, cd: 0.58 }, press: ["submit"], wait: 1 } },
    { id: "bias", robot: true, text: ["发球机器人：改用欧拉法、步长 50 ms 拟合，提交这样得到的 C_d（与用同样方法求出的最佳值相差 0.01 以内）。它比真值大还是小？为什么？", "Launcher: fit with Euler at a 50 ms step and submit the C_d it gives (within 0.01 of the best value for that method). Is it above or below the true value? Why?"],
      demo: { scene: "serve", set: { method: 0, hi: 5, cd: 0.612 }, press: ["submit"], wait: 1 } },
    { id: "stab", text: ["相平面：半隐式欧拉法不发散的最大 ωh 是多少（0.05 一档）？调到这个值，提交。", "Phase plane: what is the largest ωh (0.05 steps) at which semi-implicit Euler does not blow up? Set it and submit."],
      demo: { scene: "osc", set: { method: 1, wh: 1.95 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["欧拉法步长大时，拟合出的 C_d 为什么偏离真值？如果不知道积分误差有多大，怎样判断拟合结果可信？RK4 在 ωh 稍小于 2.8 时为什么也不发散，但轨迹看起来已经不对了？",
          "Why does a large-step Euler fit give a biased C_d? Without knowing the integration error, how would you tell whether a fit can be trusted? Why does RK4 stay bounded just below ωh = 2.8 even though its path already looks wrong?"],

  reset(api, s) { s.msg = s.msg || ""; s.n = 0; },
  change(api, s) { s.msg = ""; },
  update(dt, api, s) { s.n = Math.min(4000, s.n + 120 * dt * 20); if (s.n >= 4000) api.stop(); },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "serve") {
      if (p.method === 2 && Math.abs(p.cd - CD84) <= 0.01) { api.done("fit"); ok = true; }
      if (p.method === 0 && p.hi === 5 && Math.abs(p.cd - EULER84) <= 0.01) { api.done("bias"); ok = true; }
    }
    if (api.scene === "osc" && p.method === 1 && Math.abs(p.wh - 1.95) < 1e-6) { api.done("stab"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "serve") {
      const h = HS84[p.hi], S = sim84(p.cd, h, p.method).path;
      let land = S[S.length - 1][0];
      for (let i = 1; i < S.length; i++) if (S[i][1] < 0) { const a = S[i - 1][1] / (S[i - 1][1] - S[i][1]); land = S[i - 1][0] + a * (S[i][0] - S[i - 1][0]); break; }
      return [[["方法、步长", "Method, step"], `${api.P(NAMES84[p.method])}, ${f(h * 1000, 0)} ms`], [["与数据的均方根偏差", "RMS deviation from data"], f(rms84(p.cd, h, p.method) * 1000, 1) + " mm"],
        [["仿真的落地点", "Simulated landing"], f(land, 2) + " m"], sub];
    }
    const z = p.wh, n = Math.round(20 * 2 * Math.PI / z), pts = osc84(p.method, z, Math.min(n, Math.floor(s.n)));
    const last = pts[pts.length - 1], r = Math.hypot(last[0], last[1]);
    return [[["方法", "Method"], api.P(NAMES84[p.method])], [["每周期步数", "Steps per period"], f(2 * Math.PI / z, 1)],
      [["此刻离原点的距离（精确解为 1）", "Distance from origin now (exact: 1)"], s.n === 0 ? "—" : r > 50 ? api.T("已发散（> 50）", "diverged (> 50)") : f(r, 3)], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), red = css("--red"), mut = css("--muted");
    if (api.scene === "serve") {
      const G = api.graph({ x: 60, y: 24, w: w - 90, h: h - 70, xmin: 0, xmax: 24, ymin: 0, ymax: 2.5, xlabel: "x / m", ylabel: "y / m" }).axes();
      G.pts(sim84(p.cd, HS84[p.hi], p.method).path.filter((q) => q[1] > -0.05), red, 2);
      G.dots(DATA84, ink, 3);
      G.text(api.T("点：频闪实测（每 0.05 s）；红线：仿真", "dots: strobe data (every 0.05 s); red: simulation"), 1, 0.15, mut, 11);
      return;
    }
    const z = p.wh, n = Math.round(20 * 2 * Math.PI / z), pts = osc84(p.method, z, Math.min(n, Math.floor(s.n)));
    const sz = Math.min(w, h) - 70, G = api.graph({ x: (w - sz) / 2, y: 24, w: sz, h: sz, xmin: -7, xmax: 7, ymin: -7, ymax: 7, xlabel: "x", ylabel: "v/ω" }).axes();
    const c = []; for (let i = 0; i <= 100; i++) c.push([Math.cos(i * Math.PI / 50), Math.sin(i * Math.PI / 50)]);
    G.pts(c, ink, 1.5, [4, 4]);
    if (s.n > 0) { G.pts(pts.map((q) => [Math.max(-7, Math.min(7, q[0])), Math.max(-7, Math.min(7, q[1]))]), red, 1.5); const L = pts[pts.length - 1]; if (Math.abs(L[0]) < 7 && Math.abs(L[1]) < 7) G.point(L[0], L[1], red); }
  },
});
