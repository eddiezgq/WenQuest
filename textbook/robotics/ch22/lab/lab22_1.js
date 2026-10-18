// 实验 22.1 点到点运动的时间标度（配 22.1 节）。
// 场景 1（机器人）：UR5e 的关节 1 从 A 转到 B（俯视），默认转角 103.4°（算例 22.1.1）。时间标度可选直线 s = τ、三次 3τ² − 2τ³、
//   五次 10τ³ − 15τ⁴ + 6τ⁵（式 (22.1.5)、(22.1.8)），τ = t/T。限值：速度 180°/s（厂商资料），加速度 6 rad/s²，加加速度 60 rad/s³（设，示意值）。
//   直线插值在两端速度跳变，加速度为冲激（显示 ∞）；三次多项式在两端加速度跳变，加加速度为冲激（显示 ∞）。
//   最短时间按式 (22.1.11)：T_min = max(c_v Δ/v, √(c_a Δ/a), ∛(c_j Δ/j))，三次 (1.5, 6, ∞)，五次 (15/8, 10/√3, 60)。
// 场景 2（生活）：自动门的门扇平移 1.0 m，限值：速度 0.5 m/s，加速度 0.5 m/s²（示意值），加加速度要求有界。
// 动画按实际时间的一半速度播放。
WQ.lab({
  title: ["实验 22.1 点到点运动的时间标度", "Lab 22.1 Time scalings for point-to-point motion"],
  goal: ["比较直线插值、三次和五次多项式的速度、加速度、加加速度，按限值求出最短的运动时间。",
         "Compare the velocity, acceleration and jerk of linear interpolation and of cubic and quintic polynomials, and find the shortest motion time within the limits."],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 关节 1 点到点", "UR5e joint 1 point to point"],
      problem: { title: ["机器人问题：从料架上方转到卡盘前", "Robot problem: from above the rack to the front of the chuck"],
                 text: ["关节 1 要从静止转过约 103°，再静止停住。速度不超过 180°/s，加速度不超过 6 rad/s²，加加速度不超过 60 rad/s³。选择时间标度和运动时间。",
                        "Joint 1 turns about 103° from rest to rest. Velocity ≤ 180°/s, acceleration ≤ 6 rad/s², jerk ≤ 60 rad/s³. Choose the time scaling and the motion time."] } },
    { id: "door", name: ["自动门", "Automatic door"], hide: ["dq"],
      params: { T: { min: 1, max: 8, value: 5, step: 0.05 } },
      problem: { title: ["生活中的例子：自动门怎样开才平稳", "Everyday example: how a sliding door opens smoothly"],
                 text: ["门扇要平移 1.0 m。为了安全和平稳，速度不超过 0.5 m/s，加速度不超过 0.5 m/s²，加加速度要有界。",
                        "The door leaf slides 1.0 m. For safety and smoothness the speed stays below 0.5 m/s, the acceleration below 0.5 m/s², and the jerk must be bounded."] } },
  ],
  params: [
    { id: "kind", name: ["时间标度：0 直线 / 1 三次 / 2 五次", "Time scaling: 0 linear / 1 cubic / 2 quintic"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "T", name: ["运动时间 T", "Motion time T"], min: 0.5, max: 3, step: 0.01, value: 2, unit: "s", digits: 2 },
    { id: "dq", name: ["关节 1 的转角 Δθ₁", "Joint 1 rotation Δθ₁"], min: 10, max: 180, step: 0.1, value: 103.4, unit: "°", digits: 1 },
  ],
  legend: [{ color: "#1f77b4", name: ["当前曲线", "current curve"] }, { color: "#9aa4ab", name: ["限值", "limits"] }],
  tasks: [
    { id: "lin", robot: true, text: ["用直线插值转过约 103°（运动时间任取），看到起止时速度跳变、加速度为冲激。",
                                      "With linear interpolation turn about 103° (any time) and see the velocity jump and the acceleration impulse at both ends."],
      demo: { scene: "ur", set: { kind: 0, dq: 103.4, T: 1.5 }, press: ["start"], wait: 14 } },
    { id: "cub", robot: true, text: ["三次多项式、转角约 103°：找出不超限的最短时间（不超过最短时间的 1.02 倍）。",
                                      "Cubic, about 103°: find the shortest time within the limits (at most 1.02 times the minimum)."],
      demo: { scene: "ur", set: { kind: 1, dq: 103.4, T: 1.35 }, press: [], wait: 3 } },
    { id: "qui", robot: true, text: ["五次多项式、转角约 103°：找出不超限的最短时间，并与三次比较。",
                                      "Quintic, about 103°: find the shortest time within the limits and compare it with the cubic."],
      demo: { scene: "ur", set: { kind: 2, dq: 103.4, T: 1.33 }, press: [], wait: 3 } },
    { id: "door", text: ["自动门：在 4 s 以内打开，速度、加速度不超限，加加速度有界，并运行一次。",
                         "Automatic door: open within 4 s, with velocity and acceleration within the limits and bounded jerk, and run it once."],
      demo: { scene: "door", set: { kind: 2, T: 3.9 }, press: ["start"], wait: 24 } },
  ],
  think: ["算例 22.1.1 中五次多项式比三次多项式快，可是五次多项式的速度峰值更高。若把加速度上限加大到 20 rad/s²，哪一种更快？为什么？",
          "In Example 22.1.1 the quintic is faster than the cubic although its peak velocity is higher. If the acceleration limit were raised to 20 rad/s², which would be faster, and why?"],

  // ---------------- 时间标度：归一化曲线的 0～3 阶导数（对 τ）
  prof(kind, u) {
    if (kind === 0) return [u, 1, 0, 0];
    if (kind === 1) return [3 * u * u - 2 * u ** 3, 6 * u - 6 * u * u, 6 - 12 * u, -12];
    return [10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5, 30 * u * u * (1 - u) ** 2, 60 * u * (1 - u) * (1 - 2 * u), 60 * (1 - 6 * u + 6 * u * u)];
  },
  peaks: [[1, Infinity, Infinity], [1.5, 6, Infinity], [15 / 8, 10 / Math.sqrt(3), 60]],
  lim(api) { return api.scene === "door" ? { v: 0.5, a: 0.5, j: Infinity, L: 1.0, unit: "m" } : { v: Math.PI, a: 6, j: 60, L: api.p.dq * Math.PI / 180, unit: "rad" }; },
  tmin(api) {
    const k = api.p.kind, c = this.peaks[k], m = this.lim(api);
    if (k === 0) return Infinity;
    const t = [c[0] * m.L / m.v, Math.sqrt(c[1] * m.L / m.a)];
    if (isFinite(c[2]) && isFinite(m.j)) t.push(Math.cbrt(c[2] * m.L / m.j));
    return Math.max(...t);
  },
  stat(api) {
    const k = api.p.kind, c = this.peaks[k], m = this.lim(api), T = api.p.T;
    const v = c[0] * m.L / T, a = c[1] * m.L / T ** 2, j = c[2] * m.L / T ** 3;
    const okv = v <= m.v * (1 + 1e-9), oka = a <= m.a * (1 + 1e-9), okj = !isFinite(m.j) || k !== 2 ? true : j <= m.j * (1 + 1e-9);
    // 三次多项式的加加速度在两端是冲激，本来就无法满足加加速度限值，只检查速度和加速度（与算例 22.1.1 相同）
    return { v, a, j, okv, oka, okj, ok: okv && oka && okj && isFinite(a), tmin: this.tmin(api) };
  },

  reset(api, s) { s.clock = 0; s.done = false; },
  start(api, s) { s.clock = 0; s.done = false; },
  update(dt, api, s) {
    s.clock += 0.5 * dt;                                   // 放慢一半
    if (s.clock >= api.p.T) {
      s.clock = api.p.T; s.done = true; api.stop();
      if (api.scene === "ur" && api.p.kind === 0 && Math.abs(api.p.dq - 103.4) < 1.5) api.done("lin");
      const st = this.stat(api);
      if (api.scene === "door" && api.p.T <= 4 + 1e-9 && st.ok && isFinite(st.j)) api.done("door");
    }
  },
  readouts(api, s) {
    const st = this.stat(api), m = this.lim(api), deg = api.scene === "ur";
    const f = (x, d) => (isFinite(x) ? api.fmt(x, d) : "∞");
    const names = [api.T("直线", "linear"), api.T("三次", "cubic"), api.T("五次", "quintic")];
    const near = Math.abs(api.p.dq - 103.4) < 1.5;
    if (api.scene === "ur" && near && api.p.kind === 1 && st.ok && api.p.T <= 1.02 * st.tmin) api.done("cub");
    if (api.scene === "ur" && near && api.p.kind === 2 && st.ok && api.p.T <= 1.02 * st.tmin) api.done("qui");
    const vu = deg ? "°/s" : " m/s", au = deg ? " rad/s²" : " m/s²", ju = deg ? " rad/s³" : " m/s³";
    const vv = deg ? st.v * 180 / Math.PI : st.v, vl = deg ? 180 : m.v;
    return [[["时间标度", "time scaling"], names[api.p.kind]],
            [["速度峰值 / 限值", "peak velocity / limit"], `${f(vv, 1)} / ${f(vl, 1)}${vu}` + (st.okv ? "" : api.T("  超限", "  over"))],
            [["加速度峰值 / 限值", "peak acceleration / limit"], `${f(st.a, 2)} / ${f(m.a, 1)}${au}` + (st.oka ? "" : api.T("  超限", "  over"))],
            [["加加速度峰值", "peak jerk"], `${f(st.j, 1)}${ju}` + (isFinite(m.j) && api.p.kind === 2 ? ` / ${f(m.j, 0)}` + (st.okj ? "" : api.T("  超限", "  over")) : "")],
            [["这种标度的最短时间", "shortest time for this scaling"], isFinite(st.tmin) ? f(st.tmin, 3) + " s" : api.T("无（加速度为冲激）", "none (impulsive acceleration)")],
            [["状态", "status"], st.ok ? api.T("在限值以内", "within the limits") : api.T("超限", "limits exceeded")],
            [["时刻 t", "time t"], f(s.clock || 0, 2) + " s"]];
  },
  draw(api, s) {
    const { w, h, ctx } = api, T = api.p.T, k = api.p.kind, m = this.lim(api), deg = api.scene === "ur";
    const u = Math.min(1, (s.clock || 0) / T), pr = this.prof(k, u), pos = pr[0];
    // ---- 左：机构
    const cx = w * 0.2, cy = h * 0.55;
    if (api.scene === "ur") {
      const R = Math.min(w * 0.17, h * 0.36), a0 = 98.17 * Math.PI / 180 - Math.PI / 2, dq = m.L;
      ctx.strokeStyle = api.css("--muted"); ctx.setLineDash([5, 5]); ctx.lineWidth = 1.2; ctx.beginPath();
      ctx.arc(cx, cy, R, -a0, -(a0 + dq), true); ctx.stroke(); ctx.setLineDash([]);
      [[a0, "A"], [a0 + dq, "B"]].forEach(([a, n]) => api.label(n, cx + (R + 14) * Math.cos(a), cy - (R + 14) * Math.sin(a), api.css("--muted"), 14, "center"));
      const a = a0 + dq * pos;
      api.circle(cx, cy, 16, api.css("--panel"), api.css("--ink"));
      api.line(cx, cy, cx + R * Math.cos(a), cy - R * Math.sin(a), api.css("--accent"), 10);
      api.circle(cx + R * Math.cos(a), cy - R * Math.sin(a), 6, api.css("--amber"));
      api.label(api.T("俯视：关节 1", "top view: joint 1"), cx - R, cy + R + 26, api.css("--muted"), 12);
    } else {
      const W = Math.min(w * 0.34, h * 0.8), x0 = cx - W / 2, y0 = cy - W * 0.55;
      api.rect(x0, y0, W, W * 1.1, null, api.css("--muted"));
      api.rect(x0, y0, W * 0.5, W * 1.1, "rgba(130,180,220,0.15)", null);
      const off = pos * W * 0.5;
      api.rect(x0 + off, y0 + 4, W * 0.5 - 4, W * 1.1 - 8, "rgba(130,180,220,0.55)", api.css("--ink"), 3);
      api.line(x0 - 10, y0 - 6, x0 + W + 10, y0 - 6, api.css("--ink"), 3);
      api.label(api.T("门扇平移 1.0 m", "door leaf slides 1.0 m"), x0, y0 + W * 1.1 + 18, api.css("--muted"), 12);
    }
    // ---- 右：四条曲线
    const px = w * 0.43, pw = w * 0.53, ph = h * 0.19, gap = h * 0.045;
    const sc = (r) => m.L / T ** r;
    const N = 200, lab = deg ? [api.T("θ₁ − θ₁A / rad", "θ₁ − θ₁A / rad"), "θ̇₁ / (rad/s)", "θ̈₁ / (rad/s²)", api.T("加加速度 / (rad/s³)", "jerk / (rad/s³)")]
      : [api.T("位置 / m", "position / m"), api.T("速度 / (m/s)", "velocity / (m/s)"), api.T("加速度 / (m/s²)", "acceleration / (m/s²)"), api.T("加加速度 / (m/s³)", "jerk / (m/s³)")];
    const lims = [null, m.v, m.a, isFinite(m.j) ? m.j : null];
    for (let r = 0; r < 4; r++) {
      const y = h * 0.04 + r * (ph + gap);
      const pts = Array.from({ length: N + 1 }, (_, i) => [i / N * T, (r === 0 ? m.L : 1) * this.prof(k, i / N)[r] * (r === 0 ? 1 : sc(r))]);
      let ymax = Math.max(1e-6, ...pts.map((p) => Math.abs(p[1])));
      if (lims[r]) ymax = Math.max(ymax, lims[r] * 1.15);
      if (r >= 2 && k === 0) ymax = lims[r] ? lims[r] * 1.15 : 1;
      if (r === 3 && k === 1) ymax = Math.max(ymax, (lims[3] || ymax) * 1.15);
      const lo = r === 0 || r === 1 ? 0 : -ymax;
      const P = api.plot(px, y, pw, ph, [{ pts, color: api.css("--blue") }], { xmin: 0, xmax: Math.max(T, 0.01) * 1.08, ymin: lo, ymax: r === 0 ? m.L * 1.1 : ymax, ylabel: lab[r] });
      if (lims[r]) { api.line(px, P.Y(lims[r]), px + pw, P.Y(lims[r]), api.css("--muted"), 1, [5, 4]); if (r >= 2) api.line(px, P.Y(-lims[r]), px + pw, P.Y(-lims[r]), api.css("--muted"), 1, [5, 4]); }
      // 跳变与冲激
      if (r === 1 && k === 0) { api.line(P.X(0), P.Y(0), P.X(0), P.Y(sc(1)), api.css("--blue"), 2); api.line(P.X(T), P.Y(0), P.X(T), P.Y(sc(1)), api.css("--blue"), 2); }
      if ((r === 2 && k === 0) || (r === 3 && k === 1)) {
        api.arrow(P.X(0), P.Y(0), P.X(0), y + 4, api.css("--red"), 2.5); api.arrow(P.X(T), P.Y(0), P.X(T), r === 2 ? y + ph - 4 : y + 4, api.css("--red"), 2.5);
        api.label("∞", P.X(0) + 8, y + 10, api.css("--red"), 14);
      }
      if (r === 2 && k === 1) { api.line(P.X(0), P.Y(0), P.X(0), P.Y(6 * sc(2)), api.css("--blue"), 2); api.line(P.X(T), P.Y(-6 * sc(2)), P.X(T), P.Y(0), api.css("--blue"), 2); }
      const t = Math.min(s.clock || 0, T);
      api.line(P.X(t), y, P.X(t), y + ph, api.css("--amber"), 1.2);
      const val = (r === 0 ? m.L : 1) * this.prof(k, t / T)[r] * (r === 0 ? 1 : sc(r));
      if (isFinite(val)) api.circle(P.X(t), P.Y(val), 4, api.css("--amber"));
    }
    api.label("t / s", px + pw, h * 0.04 + 4 * (ph + gap) - gap + 10, api.css("--muted"), 12, "right");
  },
});
