// 实验 8.3 关节限位与限速（配 8.3 节）。
// “受限的一步”：平面 2R 臂在 θ = (0°, 90°)，min ½‖JΔ − e‖² s.t. |Δᵢ| ≤ d（式 (8.3.1)）。二维盒约束的凸二次规划：
// 依次检查“无约束点、四条边上的最小点、四个角”，取可行且目标值最小者，就是最优解；乘子由驻点条件 (8.3.3) 求出。
// “电梯”：T = 20 s 内上升 H = 30 m，起止静止，min ∫a²dt，速度不超过 v_max：解析解式 (8.3.10)。
WQ.lab({
  title: ["实验 8.3 关节限位与限速", "Lab 8.3 Joint limits and speed limits"],
  goal: ["在可行域里找二次函数的最小点，读出乘子，检验 KKT 条件；看限速怎样改变最小能量的速度曲线。",
         "Find the minimum of a quadratic inside a feasible set, read the multipliers and check the KKT conditions; see how a speed limit reshapes the minimum-energy speed profile."],
  scenes: [
    { id: "step", robot: true, name: ["受限的一步", "A limited step"], hide: ["vmax"],
      problem: { title: ["机器人问题：每步关节转角有上限", "Robot problem: each step of a joint is limited"],
                 text: ["手臂在 (0°, 90°)，要让末端尽量接近目标，但每个关节这一步最多转 d。截断超限的分量，并不是最好的办法。",
                        "The arm is at (0°, 90°) and should bring the tip as close to the target as possible, but no joint may turn more than d in this step. Clipping is not the best answer."] } },
    { id: "lift", name: ["电梯", "A lift"], hide: ["px", "py", "dmax"],
      problem: { title: ["生活中的例子：电梯的速度曲线", "Everyday example: the speed profile of a lift"],
                 text: ["电梯 20 s 上升 30 m，起止静止。不限速时最省能的速度曲线是抛物线；有额定速度时，中段匀速。",
                        "A lift rises 30 m in 20 s from rest to rest. Without a limit the most economical speed is a parabola; with a rated speed it cruises in the middle."] } },
  ],
  params: [
    { id: "px", name: ["目标 x", "Target x"], min: 0.3, max: 0.7, step: 0.01, value: 0.5, unit: "m", digits: 2 },
    { id: "py", name: ["目标 y", "Target y"], min: 0.1, max: 0.6, step: 0.01, value: 0.4, unit: "m", digits: 2 },
    { id: "dmax", name: ["每步增量上限 d", "Step limit d"], min: 0.02, max: 0.3, step: 0.01, value: 0.1, unit: "rad", digits: 2 },
    { id: "vmax", name: ["额定速度 v_max", "Rated speed v_max"], min: 1.55, max: 2.5, step: 0.01, value: 2.25, unit: "m/s", digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 8.3.1（目标 (0.5, 0.4) m，d = 0.1 rad），读出 μ₄。", "Reproduce Example 8.3.1 (target (0.5, 0.4) m, d = 0.1 rad) and read μ₄."],
      demo: { scene: "step", set: { px: 0.5, py: 0.4, dmax: 0.1 }, press: [] } },
    { id: "free", robot: true, text: ["加大 d，使不加限制的解本身可行：此时所有乘子都为零。", "Raise d until the unconstrained step is feasible: then every multiplier is zero."],
      demo: { scene: "step", set: { px: 0.5, py: 0.4, dmax: 0.25 }, press: [] } },
    { id: "corner", robot: true, text: ["找一组参数，使两个约束同时起作用（解在正方形的角上）。", "Find settings for which two constraints are active at once (the solution sits at a corner)."],
      demo: { scene: "step", set: { px: 0.5, py: 0.4, dmax: 0.05 }, press: [] } },
    { id: "lift", text: ["在“电梯”中降低额定速度，使匀速段超过 6 s。", "In “A lift” lower the rated speed until the cruise lasts more than 6 s."],
      demo: { scene: "lift", set: { vmax: 1.8 }, press: [] } },
  ],
  think: ["截断解和二次规划的解，哪一个让关节 1 转得更多？为什么关节 2 受限时，关节 1 反而应该反向转？",
          "Which turns joint 1 more, the clipped step or the QP step? Why should joint 1 turn the other way when joint 2 is limited?"],

  L1: 0.425, L2: 0.392, T0: [0, Math.PI / 2],
  setup(api) {
    const t = this.T0, s1 = Math.sin(t[0]), s12 = Math.sin(t[0] + t[1]), c1 = Math.cos(t[0]), c12 = Math.cos(t[0] + t[1]);
    const J = [[-this.L1 * s1 - this.L2 * s12, -this.L2 * s12], [this.L1 * c1 + this.L2 * c12, this.L2 * c12]];
    const p = [this.L1 * c1 + this.L2 * c12, this.L1 * s1 + this.L2 * s12], e = [api.p.px - p[0], api.p.py - p[1]];
    const Q = [[J[0][0] ** 2 + J[1][0] ** 2, J[0][0] * J[0][1] + J[1][0] * J[1][1]], [0, J[0][1] ** 2 + J[1][1] ** 2]]; Q[1][0] = Q[0][1];
    const c = [-(J[0][0] * e[0] + J[1][0] * e[1]), -(J[0][1] * e[0] + J[1][1] * e[1])];
    return { J, p, e, Q, c };
  },
  q(P, x) { return 0.5 * (P.Q[0][0] * x[0] * x[0] + 2 * P.Q[0][1] * x[0] * x[1] + P.Q[1][1] * x[1] * x[1]) + P.c[0] * x[0] + P.c[1] * x[1]; },
  qp(api) {                                                 // 盒约束二维凸二次规划：枚举候选点
    const P = this.setup(api), d = api.p.dmax, Q = P.Q, c = P.c, cand = [];
    const det = Q[0][0] * Q[1][1] - Q[0][1] ** 2;
    cand.push({ x: [(-c[0] * Q[1][1] + c[1] * Q[0][1]) / det, (c[0] * Q[0][1] - c[1] * Q[0][0]) / det], act: [] });
    [d, -d].forEach((v, k) => {                             // 边 Δ₁ = ±d：对 Δ₂ 求最小；边 Δ₂ = ±d：对 Δ₁ 求最小
      cand.push({ x: [v, -(c[1] + Q[0][1] * v) / Q[1][1]], act: [k === 0 ? 0 : 2] });
      cand.push({ x: [-(c[0] + Q[0][1] * v) / Q[0][0], v], act: [k === 0 ? 1 : 3] });
    });
    [[d, d, 0, 1], [-d, d, 2, 1], [-d, -d, 2, 3], [d, -d, 0, 3]].forEach((z) => cand.push({ x: [z[0], z[1]], act: [z[2], z[3]] }));
    let best = null;
    cand.forEach((s) => { if (Math.abs(s.x[0]) <= d + 1e-12 && Math.abs(s.x[1]) <= d + 1e-12) { const v = this.q(P, s.x); if (!best || v < best.v - 1e-15) best = { ...s, v }; } });
    const g = [Q[0][0] * best.x[0] + Q[0][1] * best.x[1] + c[0], Q[0][1] * best.x[0] + Q[1][1] * best.x[1] + c[1]];
    const a = [[1, 0], [0, 1], [-1, 0], [0, -1]], mu = [0, 0, 0, 0];
    best.act.forEach((i) => { const comp = i % 2; mu[i] = -g[comp] / a[i][comp]; });   // 驻点条件：g + Σ μᵢ aᵢ = 0
    const free = cand[0].x;
    return { P, x: best.x, mu, act: best.act.filter((i) => mu[i] > 1e-12), free, g };
  },
  lift(api) {
    const T = 20, H = 30, v = api.p.vmax;
    if (v >= 1.5 * H / T) return { T, H, t1: T / 2, cost: 12 * H * H / T ** 3, v: (t) => 6 * H / T ** 2 * t * (1 - t / T), cruise: 0 };
    const t1 = 3 * (v * T - H) / (2 * v);
    return { T, H, t1, cost: 8 * v * v / (3 * t1), cruise: T - 2 * t1,
             v: (t) => { const s = Math.min(t, T - t); return s < t1 ? v * (1 - (1 - s / t1) ** 2) : v; } };
  },

  reset(api, s) {},
  readouts(api, s) {
    const f = (x, n) => api.fmt(x, n);
    if (api.scene === "lift") {
      const L = this.lift(api);
      if (L.cruise > 6) api.done("lift");
      return [[["加速段时长 t₁", "ramp time t₁"], f(L.t1, 2) + " s"], [["匀速段时长", "cruise time"], f(L.cruise, 2) + " s"],
              [["代价 ∫a²dt", "cost ∫a²dt"], f(L.cost, 3) + " m²/s³"], [["不限速时的代价", "cost without a limit"], f(12 * 30 * 30 / 8000, 3) + " m²/s³"]];
    }
    const r = this.qp(api), P = r.P, d = api.p.dmax;
    const clip = r.free.map((v) => Math.max(-d, Math.min(d, v)));
    const err = (x) => Math.hypot(P.J[0][0] * x[0] + P.J[0][1] * x[1] - P.e[0], P.J[1][0] * x[0] + P.J[1][1] * x[1] - P.e[1]);
    const def = Math.abs(api.p.px - 0.5) < 1e-9 && Math.abs(api.p.py - 0.4) < 1e-9;
    if (def && Math.abs(d - 0.1) < 1e-9 && r.act.length === 1 && r.act[0] === 3) api.done("ex");
    if (Math.max(Math.abs(r.free[0]), Math.abs(r.free[1])) <= d && r.mu.every((m) => m === 0)) api.done("free");
    if (r.act.length === 2) api.done("corner");
    const names = ["Δ₁ ≤ d", "Δ₂ ≤ d", "−Δ₁ ≤ d", "−Δ₂ ≤ d"];
    return [[["不加限制的解 Δ_free", "unconstrained Δ_free"], `(${f(r.free[0], 4)}, ${f(r.free[1], 4)}) rad`],
            [["二次规划的解 Δ*", "QP solution Δ*"], `(${f(r.x[0], 4)}, ${f(r.x[1], 4)}) rad`],
            [["起作用的约束", "active constraints"], r.act.length ? r.act.map((i) => names[i]).join(", ") : api.T("无", "none")],
            [["乘子 μ₁…μ₄", "multipliers μ₁…μ₄"], `(${r.mu.map((m) => f(m, 5)).join(", ")})`],
            [["末端误差 ‖JΔ − e‖：二次规划", "tip error ‖JΔ − e‖: QP"], f(err(r.x), 4) + " m"],
            [["末端误差 ‖JΔ − e‖：截断", "tip error ‖JΔ − e‖: clipped"], f(err(clip), 4) + " m"]];
  },
  draw(api, s) {
    const { w, h, ctx } = api;
    if (api.scene === "lift") {
      const L = this.lift(api);
      const pl = api.plot(w * 0.12, h * 0.1, w * 0.62, h * 0.72, [
        { pts: Array.from({ length: 201 }, (_, i) => { const t = i / 10; return [t, 6 * 30 / 400 * t * (1 - t / 20)]; }), color: api.css("--muted") },
        { pts: Array.from({ length: 201 }, (_, i) => [i / 10, L.v(i / 10)]), color: api.css("--blue") }],
        { xmin: 0, xmax: 20, ymin: 0, ymax: 2.6, xlabel: api.T("t / s", "t / s"), ylabel: api.T("速度 / (m/s)", "speed / (m/s)") });
      api.line(pl.X(0), pl.Y(api.p.vmax), pl.X(20), pl.Y(api.p.vmax), api.css("--red"), 1.5, [6, 4]);
      api.label("v_max", pl.X(0.3), pl.Y(api.p.vmax) - 10, api.css("--red"), 12);
      // 电梯轿厢
      const shaftX = w * 0.84, top = h * 0.08, bot = h * 0.86;
      api.rect(shaftX - 28, top, 56, bot - top, null, api.css("--muted"));
      for (let k = 0; k <= 10; k++) api.line(shaftX - 34, bot - k * (bot - top) / 10, shaftX - 28, bot - k * (bot - top) / 10, api.css("--muted"), 1);
      api.rect(shaftX - 22, bot - 34, 44, 30, api.css("--accent"), null, 4);
      api.label(api.T("30 m", "30 m"), shaftX + 34, top + 8, api.css("--muted"), 12);
      return;
    }
    const r = this.qp(api), P = r.P, d = api.p.dmax;
    // 右：Δ 平面
    const side = Math.min(w * 0.48, h * 0.9), x0 = w * 0.98 - side, y0 = (h - side) / 2, R = 0.32;
    const X = (v) => x0 + (v[0] + R) / (2 * R) * side, Y = (v) => y0 + side - (v[1] + R) / (2 * R) * side;
    api.rect(x0, y0, side, side, null, api.css("--grid"));
    api.line(X([-R, 0]), Y([0, 0]), X([R, 0]), Y([0, 0]), api.css("--grid"), 1); api.line(X([0, -R]), Y([0, -R]), X([0, R]), Y([0, R]), api.css("--grid"), 1);
    const a = P.Q[0][0], b = P.Q[0][1], c = P.Q[1][1], tr = (a + c) / 2, df = Math.sqrt(((a - c) / 2) ** 2 + b * b);
    const l1 = tr + df, l2 = tr - df, ang = 0.5 * Math.atan2(2 * b, a - c), qmin = this.q(P, r.free);
    [1e-5, 1e-4, 3e-4, 7e-4, this.q(P, r.x) - qmin].forEach((lv, k) => {
      ctx.strokeStyle = k === 4 ? api.css("--blue") : api.css("--muted"); ctx.lineWidth = k === 4 ? 2 : 1; ctx.beginPath();
      for (let i = 0; i <= 80; i++) {
        const t = 2 * Math.PI * i / 80, u = Math.sqrt(2 * lv / l1) * Math.cos(t), v = Math.sqrt(2 * lv / Math.max(l2, 1e-9)) * Math.sin(t);
        const pt = [r.free[0] + u * Math.cos(ang) - v * Math.sin(ang), r.free[1] + u * Math.sin(ang) + v * Math.cos(ang)];
        const xs = X(pt), ys = Y(pt); if (i) ctx.lineTo(xs, ys); else ctx.moveTo(xs, ys);
      }
      ctx.stroke();
    });
    ctx.fillStyle = "rgba(31,111,235,0.12)"; ctx.fillRect(X([-d, 0]), Y([0, d]), X([d, 0]) - X([-d, 0]), Y([0, -d]) - Y([0, d]));
    api.rect(X([-d, 0]), Y([0, d]), X([d, 0]) - X([-d, 0]), Y([0, -d]) - Y([0, d]), null, api.css("--blue"));
    const fr = [Math.max(-R, Math.min(R, r.free[0])), Math.max(-R, Math.min(R, r.free[1]))];
    api.circle(X(fr), Y(fr), 5, api.css("--ink"));
    const clip = r.free.map((v) => Math.max(-d, Math.min(d, v)));
    api.rect(X(clip) - 5, Y(clip) - 5, 10, 10, api.css("--orange"));
    api.circle(X(r.x), Y(r.x), 7, api.css("--red"), api.css("--ink"));
    api.label("Δ*", X(r.x) - 26, Y(r.x) + 14, api.css("--red"), 13);
    if (r.act.length) { const gn = Math.hypot(r.g[0], r.g[1]); if (gn > 1e-12) api.arrow(X(r.x), Y(r.x), X(r.x) - 40 * r.g[0] / gn, Y(r.x) + 40 * r.g[1] / gn, api.css("--amber"), 2.5); }
    api.label("Δ₁", x0 + side - 6, y0 + side - 10, api.css("--muted"), 12, "right"); api.label("Δ₂", x0 + 6, y0 + 10, api.css("--muted"), 12);
    // 左：机械臂、目标、走完这一步后的末端（线性预计）
    const k = Math.min(w * 0.42, h * 0.9) / 0.95, bx = w * 0.06, by = h * 0.82;
    const Pp = (q) => [bx + k * q[0], by - k * q[1]];
    const B = Pp([0, 0]), E = Pp([this.L1, 0]), T = Pp(P.p), D = Pp([api.p.px, api.p.py]);
    api.line(B[0], B[1], E[0], E[1], api.css("--accent"), 8); api.line(E[0], E[1], T[0], T[1], api.css("--accent"), 6);
    api.circle(B[0], B[1], 6, api.css("--panel"), api.css("--ink")); api.circle(E[0], E[1], 5, api.css("--panel"), api.css("--ink"));
    api.line(D[0] - 6, D[1] - 6, D[0] + 6, D[1] + 6, api.css("--red"), 2.5); api.line(D[0] - 6, D[1] + 6, D[0] + 6, D[1] - 6, api.css("--red"), 2.5);
    const nx = (x) => Pp([P.p[0] + P.J[0][0] * x[0] + P.J[0][1] * x[1], P.p[1] + P.J[1][0] * x[0] + P.J[1][1] * x[1]]);
    const Nq = nx(r.x), Nc = nx(clip);
    api.circle(Nq[0], Nq[1], 5, api.css("--red")); api.rect(Nc[0] - 4, Nc[1] - 4, 8, 8, api.css("--orange"));
    api.label(api.T("红点：二次规划；橙块：截断", "red: QP; orange: clipped"), 12, h - 12, api.css("--muted"), 12);
  },
});
