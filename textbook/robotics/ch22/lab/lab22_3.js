// 实验 22.3 过路径点的轨迹（配 22.3 节）。
// 场景 1（机器人）：UR5e 的侧视——关节 2、3 构成的平面两连杆（大臂 0.425 m、小臂 0.392 m），依次经过上下料循环中
//   R、A、M、B 四个路径点的关节 2、3 的值（算例 22.3.1，度）：(−76.89, 121.83)、(−86.04, 114.53)、(−67.98, 62.98)、(−50.54, 79.73)。
//   侧视图中大臂与水平线的夹角为 −θ₂，小臂相对大臂转 −θ₃。限值：速度 180°/s，加速度 6 rad/s²，加加速度 60 rad/s³（示意值）。
// 场景 2（生活）：绘图仪的笔经过字母“S”的 8 个点（单位 m），x、y 两轴各自限速 0.2 m/s、加速度 1.5 m/s²（示意值）。
// 四种做法：0 每点停下（每段五次多项式，各取最短时间，定理 22.1.3）；1 经验速度（式 (22.3.2)）；2 三次样条（式 (22.3.4)，追赶法）；
//   3 抛物线过渡（式 (22.3.5)，过渡时长取不超过加速度限值的最小值）。1～3 的各段时长按“每点停下”时的比例分配，总时间可调。
WQ.lab({
  title: ["实验 22.3 过路径点的轨迹", "Lab 22.3 Trajectories through via points"],
  goal: ["比较每点停下、经验速度、三次样条和抛物线过渡四种经过路径点的做法：总时间、加速度是否连续、偏离路径点多少。",
         "Compare four ways of passing via points — stopping at each, heuristic velocities, a cubic spline and parabolic blends — in total time, continuity of acceleration and deviation from the points."],
  scenes: [
    { id: "arm", robot: true, name: ["UR5e 侧视：上下料的前半段", "UR5e side view: first half of the loading cycle"],
      problem: { title: ["机器人问题：A 和 M 只是要经过的点", "Robot problem: A and M only have to be passed"],
                 text: ["手臂从料架里的 R 出发，经过提升后的 A、防护罩上方的 M，到卡盘前的 B。在 A、M 停下浪费时间，怎样不停顿地经过？",
                        "The arm starts at R in the rack, passes A (lifted) and M (above the guard) and reaches B in front of the chuck. Stopping at A and M wastes time; how can it pass them without stopping?"] } },
    { id: "pen", name: ["绘图仪写“S”", "A plotter writes “S”"],
      params: { T: { min: 1, max: 4, value: 3, step: 0.01 } },
      problem: { title: ["生活中的例子：连笔写字", "Everyday example: joined-up writing"],
                 text: ["绘图仪的笔要经过字母“S”上的 8 个点。一笔一画地写（每点停下）很慢，连笔写快得多。",
                        "The plotter pen passes 8 points on the letter “S”. Writing stroke by stroke (stopping at each point) is slow; joined-up writing is much faster."] } },
  ],
  params: [
    { id: "m", name: ["做法：0 停下 / 1 经验速度 / 2 样条 / 3 过渡", "Method: 0 stop / 1 heuristic / 2 spline / 3 blends"], min: 0, max: 3, step: 1, value: 2, unit: "", digits: 0 },
    { id: "T", name: ["总时间（做法 1～3）", "Total time (methods 1–3)"], min: 1, max: 3.5, step: 0.01, value: 2.5, unit: "s", digits: 2 },
  ],
  legend: [{ color: "#1f77b4", name: ["第 1 个坐标", "coordinate 1"] }, { color: "#d9730d", name: ["第 2 个坐标", "coordinate 2"] }, { color: "#9aa4ab", name: ["限值", "limits"] }],
  tasks: [
    { id: "stop", robot: true, text: ["每点停下（做法 0），运行一次，记下总时间。", "Stop at each point (method 0): run it once and note the total time."],
      demo: { scene: "arm", set: { m: 0 }, press: ["start"], wait: 24 } },
    { id: "spline", robot: true, text: ["三次样条（做法 2）：找出不超限的最短总时间（不超过最短值的 1.05 倍）。",
                                         "Cubic spline (method 2): find the shortest total time within the limits (at most 1.05 times the minimum)."],
      demo: { scene: "arm", set: { m: 2, T: 1.86 }, press: [], wait: 3 } },
    { id: "blend", robot: true, text: ["抛物线过渡（做法 3）：两个路径点处的偏离都不超过 3°，不超限，总时间比每点停下短。",
                                        "Parabolic blends (method 3): deviation at both via points at most 3°, within the limits, and faster than stopping at each point."],
      demo: { scene: "arm", set: { m: 3, T: 2.0 }, press: [], wait: 3 } },
    { id: "pen", text: ["绘图仪：用样条写“S”，速度、加速度都不超限，用时比每点停下少两成以上。",
                        "Plotter: write “S” with a spline, within the velocity and acceleration limits, at least 20% faster than stopping at each point."],
      demo: { scene: "pen", set: { m: 2, T: 2.2 }, press: [], wait: 3 } },
  ],
  think: ["做法 1 在路径点处加速度跳变，样条却连续，而两者都经过同样的点、用同样的时长。多出来的“光滑”是从哪里来的？",
          "Method 1 has acceleration jumps at the via points while the spline has none, with the same points and durations. Where does the extra smoothness come from?"],

  data(api) {
    const d = Math.PI / 180;
    if (api.scene === "pen") return { Q: [[0.08, 0.085], [0.03, 0.09], [0.012, 0.065], [0.03, 0.047], [0.07, 0.035], [0.085, 0.012], [0.06, 0], [0.01, 0.008]],
                                      v: [0.2, 0.2], a: [1.5, 1.5], j: [30, 30], unit: "m", k: 1 };
    return { Q: [[-76.89, 121.83], [-86.04, 114.53], [-67.98, 62.98], [-50.54, 79.73]].map((q) => q.map((x) => x * d)),
             v: [Math.PI, Math.PI], a: [6, 6], j: [60, 60], unit: "rad", k: 180 / Math.PI };
  },
  // 每段五次多项式的最短时间（式 (22.1.11)）
  tq(D, dq) { let T = 0; for (let i = 0; i < 2; i++) { const L = Math.abs(dq[i]); T = Math.max(T, 15 / 8 * L / D.v[i], Math.sqrt(10 / Math.sqrt(3) * L / D.a[i]), Math.cbrt(60 * L / D.j[i])); } return T; },
  herm(T, q0, q1, v0, v1) { return [q0, v0, (3 * (q1 - q0) - (2 * v0 + v1) * T) / T / T, (-2 * (q1 - q0) + (v0 + v1) * T) / T ** 3]; },
  build(api, Tot) {
    const D = this.data(api), Q = D.Q, N = Q.length - 1, m = api.p.m;
    const Ts = Q.slice(1).map((q, k) => this.tq(D, [q[0] - Q[k][0], q[1] - Q[k][1]]));
    const Tstop = Ts.reduce((a, b) => a + b, 0);
    const tr = { D, Ts, Tstop, m };
    if (m === 0) {
      const t0 = [0]; Ts.forEach((T) => t0.push(t0[t0.length - 1] + T));
      tr.T = Tstop; tr.knots = t0;
      tr.ev = (t, r) => { t = Math.max(0, Math.min(Tstop, t)); let k = 0; while (k < N - 1 && t > t0[k + 1]) k++;
        const T = Ts[k], u = (t - t0[k]) / T, s = [10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5, 30 * u * u * (1 - u) ** 2 / T, 60 * u * (1 - u) * (1 - 2 * u) / T / T][r];
        return [0, 1].map((i) => (r === 0 ? Q[k][i] : 0) + s * (Q[k + 1][i] - Q[k][i])); };
      return tr;
    }
    const h = Ts.map((T) => T * Tot / Tstop), tk = [0]; h.forEach((x) => tk.push(tk[tk.length - 1] + x));
    tr.knots = tk;
    if (m === 3) {                                               // 抛物线过渡
      const vs = [[0, 0]]; for (let k = 0; k < N; k++) vs.push([0, 1].map((i) => (Q[k + 1][i] - Q[k][i]) / h[k])); vs.push([0, 0]);
      const tb = Q.map((_, k) => Math.max(...[0, 1].map((i) => Math.abs(vs[k + 1][i] - vs[k][i]) / D.a[i])));
      tr.tb = tb; tr.T = tk[N] + (tb[0] + tb[N]) / 2; tr.shift = tb[0] / 2;
      // 定理 22.3.2：中间各路径点处的偏离 (v_out − v_in) t_b/8（取两个坐标中较大的）
      tr.dev = Q.slice(1, N).map((_, kk) => { const k = kk + 1; return Math.max(...[0, 1].map((i) => Math.abs(vs[k + 1][i] - vs[k][i]) * tb[k] / 8)); });
      tr.ev = (tt, r) => {
        const t = tt - tr.shift;
        for (let k = 0; k <= N; k++) if (Math.abs(t - tk[k]) <= tb[k] / 2 + 1e-12) {
          const u = t - tk[k] + tb[k] / 2, vin = vs[k], vout = vs[k + 1];
          return [0, 1].map((i) => { const ac = tb[k] > 0 ? (vout[i] - vin[i]) / tb[k] : 0;
            return [Q[k][i] - vin[i] * tb[k] / 2 + vin[i] * u + ac * u * u / 2, vin[i] + ac * u, ac][r]; });
        }
        if (t < 0) return r ? [0, 0] : Q[0].slice();
        if (t > tk[N]) return r ? [0, 0] : Q[N].slice();
        let k = 0; while (k < N - 1 && t > tk[k + 1]) k++;
        return [0, 1].map((i) => [Q[k][i] + vs[k + 1][i] * (t - tk[k]), vs[k + 1][i], 0][r]);
      };
      return tr;
    }
    // 路径点处的速度：经验做法或样条（追赶法解式 (22.3.4)）
    const V = Q.map(() => [0, 0]);
    for (let i = 0; i < 2; i++) {
      if (m === 1) {
        for (let k = 1; k < N; k++) { const a = (Q[k][i] - Q[k - 1][i]) / h[k - 1], b = (Q[k + 1][i] - Q[k][i]) / h[k]; V[k][i] = a * b > 0 ? (a + b) / 2 : 0; }
      } else {
        const n = N - 1, A = [], B = [], C = [], R = [];
        for (let k = 1; k < N; k++) {
          A.push(1 / h[k - 1]); B.push(2 * (1 / h[k - 1] + 1 / h[k])); C.push(1 / h[k]);
          R.push(3 * ((Q[k][i] - Q[k - 1][i]) / h[k - 1] ** 2 + (Q[k + 1][i] - Q[k][i]) / h[k] ** 2));
        }
        for (let k = 1; k < n; k++) { const w = A[k] / B[k - 1]; B[k] -= w * C[k - 1]; R[k] -= w * R[k - 1]; }
        const x = new Array(n); x[n - 1] = R[n - 1] / B[n - 1];
        for (let k = n - 2; k >= 0; k--) x[k] = (R[k] - C[k] * x[k + 1]) / B[k];
        for (let k = 1; k < N; k++) V[k][i] = x[k - 1];
      }
    }
    const co = h.map((T, k) => [0, 1].map((i) => this.herm(T, Q[k][i], Q[k + 1][i], V[k][i], V[k + 1][i])));
    tr.T = tk[N];
    tr.ev = (t, r) => { t = Math.max(0, Math.min(tk[N], t)); let k = 0; while (k < N - 1 && t > tk[k + 1]) k++;
      const u = t - tk[k];
      return co[k].map((c) => [c[0] + c[1] * u + c[2] * u * u + c[3] * u ** 3, c[1] + 2 * c[2] * u + 3 * c[3] * u * u, 2 * c[2] + 6 * c[3] * u][r]); };
    // 路径点处加速度的跳变
    tr.jump = 0;
    for (let k = 1; k < N; k++) { const l = tr.ev(tk[k] - 1e-9, 2), rr = tr.ev(tk[k] + 1e-9, 2); tr.jump = Math.max(tr.jump, Math.abs(l[0] - rr[0]), Math.abs(l[1] - rr[1])); }
    return tr;
  },
  ratio(tr) {                                                    // 速度、加速度峰值与限值之比
    let rv = 0, ra = 0;
    for (let k = 0; k <= 600; k++) { const t = k / 600 * tr.T, v = tr.ev(t, 1), a = tr.ev(t, 2);
      for (let i = 0; i < 2; i++) { rv = Math.max(rv, Math.abs(v[i]) / tr.D.v[i]); ra = Math.max(ra, Math.abs(a[i]) / tr.D.a[i]); } }
    return [rv, ra];
  },
  tminSpline(api) {
    const save = api.p.m; api.p.m = 2; let lo = 0.3, hi = 6;
    for (let it = 0; it < 40; it++) { const mid = (lo + hi) / 2, r = this.ratio(this.build(api, mid)); if (r[0] <= 1 && r[1] <= 1) hi = mid; else lo = mid; }
    api.p.m = save; return hi;
  },

  reset(api, s) { s.clock = 0; s.tr = this.build(api, api.p.T); s.r = this.ratio(s.tr); s.tmin = this.tminSpline(api); s.ended = false; },
  start(api, s) { s.clock = 0; s.ended = false; },
  update(dt, api, s) {
    s.clock += 0.5 * dt;
    if (s.clock >= s.tr.T) { s.clock = s.tr.T; api.stop();
      if (!s.ended && api.scene === "arm" && api.p.m === 0) api.done("stop");
      s.ended = true; }
  },
  readouts(api, s) {
    const tr = s.tr; if (!tr) return [];
    const f = (x, d) => api.fmt(x, d), ok = s.r[0] <= 1 + 1e-9 && s.r[1] <= 1 + 1e-9, D = tr.D;
    const names = [api.T("每点停下", "stop at each"), api.T("经验速度", "heuristic"), api.T("三次样条", "cubic spline"), api.T("抛物线过渡", "parabolic blends")];
    const devTxt = tr.dev ? tr.dev.map((d) => api.scene === "arm" ? f(d * D.k, 2) + "°" : f(d * 1000, 1) + " mm").join(", ") : "—";
    if (api.scene === "arm" && api.p.m === 2 && ok && tr.T <= 1.05 * s.tmin) api.done("spline");
    if (api.scene === "arm" && api.p.m === 3 && ok && tr.dev.every((d) => d * D.k <= 3) && tr.T < tr.Tstop) api.done("blend");
    if (api.scene === "pen" && api.p.m === 2 && ok && tr.T <= 0.8 * tr.Tstop) api.done("pen");
    return [[["做法", "method"], names[api.p.m]], [["总时间", "total time"], f(tr.T, 3) + " s"],
            [["每点停下的总时间", "total time stopping at each point"], f(tr.Tstop, 3) + " s"],
            [["样条不超限的最短总时间", "shortest spline time within limits"], f(s.tmin, 3) + " s"],
            [["速度峰值 / 限值", "peak velocity / limit"], f(s.r[0], 3)], [["加速度峰值 / 限值", "peak acceleration / limit"], f(s.r[1], 3)],
            [["路径点处加速度的跳变", "acceleration jump at via points"], tr.jump !== undefined ? f(tr.jump, 2) + (api.scene === "arm" ? " rad/s²" : " m/s²") : "—"],
            [["偏离路径点", "deviation from via points"], devTxt],
            [["状态", "status"], ok ? api.T("在限值以内", "within the limits") : api.T("超限", "limits exceeded")]];
  },
  draw(api, s) {
    const { w, h, ctx } = api, tr = s.tr; if (!tr) return;
    const D = tr.D, Q = D.Q, t = Math.min(s.clock || 0, tr.T), q = tr.ev(t, 0);
    // ---- 左：机构
    if (api.scene === "arm") {
      const k = Math.min(w * 0.4, h * 0.85) / 0.95, bx = w * 0.12, by = h * 0.62;
      const a1 = -q[0], a2 = a1 - q[1];
      const E = [bx + k * 0.425 * Math.cos(a1), by - k * 0.425 * Math.sin(a1)], W = [E[0] + k * 0.392 * Math.cos(a2), E[1] - k * 0.392 * Math.sin(a2)];
      ctx.globalAlpha = 0.25;
      Q.forEach((p) => { const b1 = -p[0], b2 = b1 - p[1]; const e = [bx + k * 0.425 * Math.cos(b1), by - k * 0.425 * Math.sin(b1)];
        api.line(bx, by, e[0], e[1], api.css("--muted"), 4); api.line(e[0], e[1], e[0] + k * 0.392 * Math.cos(b2), e[1] - k * 0.392 * Math.sin(b2), api.css("--muted"), 3); });
      ctx.globalAlpha = 1;
      ctx.strokeStyle = api.css("--red"); ctx.lineWidth = 1.5; ctx.beginPath();
      for (let i = 0; i <= 120; i++) { const p = tr.ev(i / 120 * tr.T, 0), b1 = -p[0], b2 = b1 - p[1];
        const x = bx + k * (0.425 * Math.cos(b1) + 0.392 * Math.cos(b2)), y = by - k * (0.425 * Math.sin(b1) + 0.392 * Math.sin(b2)); if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); }
      ctx.stroke();
      api.line(bx, by, E[0], E[1], api.css("--accent"), 10); api.line(E[0], E[1], W[0], W[1], api.css("--accent"), 7);
      api.circle(bx, by, 7, api.css("--panel"), api.css("--ink")); api.circle(E[0], E[1], 6, api.css("--panel"), api.css("--ink"));
      api.label(api.T("侧视：关节 2、3（红线为腕心的路径）", "side view: joints 2, 3 (red: wrist-centre path)"), bx - 10, h * 0.94, api.css("--muted"), 12);
    } else {
      const k = Math.min(w * 0.36, h * 0.8) / 0.1, x0 = w * 0.04, y0 = h * 0.88;
      api.rect(x0 - 6, y0 - k * 0.095, k * 0.1, k * 0.1, "rgba(255,255,255,0.6)", api.css("--muted"));
      ctx.strokeStyle = api.css("--ink"); ctx.lineWidth = 2.5; ctx.beginPath();
      for (let i = 0; i <= 200; i++) { const tt = i / 200 * t, p = tr.ev(tt, 0); const x = x0 + k * p[0], y = y0 - k * p[1]; if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); }
      ctx.stroke();
      Q.forEach((p) => api.circle(x0 + k * p[0], y0 - k * p[1], 3.5, api.css("--red")));
      api.circle(x0 + k * q[0], y0 - k * q[1], 6, api.css("--amber"), api.css("--ink"));
    }
    // ---- 右上：坐标平面中的路径
    const px = w * 0.5, pw = w * 0.47, ph = h * 0.42;
    const xs = Q.map((p) => p[0] * D.k), ys = Q.map((p) => p[1] * D.k);
    const pad = (a, b) => [a - (b - a) * 0.12, b + (b - a) * 0.12];
    const [xmin, xmax] = pad(Math.min(...xs), Math.max(...xs)), [ymin, ymax] = pad(Math.min(...ys), Math.max(...ys));
    const pts = Array.from({ length: 201 }, (_, i) => { const p = tr.ev(i / 200 * tr.T, 0); return [p[0] * D.k, p[1] * D.k]; });
    const P = api.plot(px, h * 0.04, pw, ph, [{ pts, color: api.css("--blue") }], { xmin, xmax, ymin, ymax,
      xlabel: api.scene === "arm" ? "θ₂ / °" : "x / m", ylabel: api.scene === "arm" ? "θ₃ / °" : "y / m" });
    Q.forEach((p, i) => { api.circle(P.X(p[0] * D.k), P.Y(p[1] * D.k), 4, api.css("--ink")); if (api.scene === "arm") api.label("RAMB"[i], P.X(p[0] * D.k) + 6, P.Y(p[1] * D.k) - 8, api.css("--ink"), 12); });
    api.circle(P.X(q[0] * D.k), P.Y(q[1] * D.k), 6, api.css("--amber"), api.css("--ink"));
    // ---- 右下：两个坐标的加速度
    const N = 300, y0 = h * 0.55, ph2 = h * 0.38;
    const A1 = Array.from({ length: N + 1 }, (_, i) => [i / N * tr.T, tr.ev(i / N * tr.T, 2)[0]]), A2 = Array.from({ length: N + 1 }, (_, i) => [i / N * tr.T, tr.ev(i / N * tr.T, 2)[1]]);
    const am = Math.max(D.a[0], ...A1.map((p) => Math.abs(p[1])), ...A2.map((p) => Math.abs(p[1]))) * 1.1;
    const P2 = api.plot(px, y0, pw, ph2, [{ pts: A1, color: "#1f77b4" }, { pts: A2, color: "#d9730d" }],
      { xmin: 0, xmax: tr.T, ymin: -am, ymax: am, ylabel: api.scene === "arm" ? api.T("加速度 / (rad/s²)", "acceleration / (rad/s²)") : api.T("加速度 / (m/s²)", "acceleration / (m/s²)"), xlabel: "t / s" });
    [D.a[0], -D.a[0]].forEach((v) => api.line(px, P2.Y(v), px + pw, P2.Y(v), api.css("--muted"), 1, [5, 4]));
    (tr.knots || []).slice(1, -1).forEach((tk) => api.line(P2.X(tk + (tr.shift || 0)), y0, P2.X(tk + (tr.shift || 0)), y0 + ph2, api.css("--grid"), 1, [2, 3]));
    api.line(P2.X(t), y0, P2.X(t), y0 + ph2, api.css("--amber"), 1.2);
  },
});
