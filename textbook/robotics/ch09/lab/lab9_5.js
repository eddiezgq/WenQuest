// 实验 9.5 一维卡尔曼滤波（配 9.5 节）。
// AGV：Δt = 0.1 s，里程计速度 u = 0.5 m/s，真实起点 0.15 m，初始估计 0（算例 9.5.1、9.5.2）。
// 步行：Δt = 1 s，计步器速度 1.4 m/s，GPS 每秒一次，第 40～59 步在隧道里（没有测量，只做预测）。
// 每步：预测 x̂⁻ = x̂ + uΔt，P⁻ = P + σ_w²（式 (9.5.3)、(9.5.4)）；有测量时 K = P⁻/(P⁻ + σ_v²)，更新（式 (9.5.5)～(9.5.7)）。
// 噪声用固定种子生成。稳态增益 K∞ 按式 (9.5.8)、(9.5.9)。
WQ.lab({
  title: ["实验 9.5 一维卡尔曼滤波", "Lab 9.5 A one-dimensional Kalman filter"],
  goal: ["用里程计预测、用定位测量更新，观察卡尔曼增益和估计的不确定度怎样变化，并与只用一种信息比较。",
         "Predict with odometry and update with position fixes; watch the gain and the uncertainty evolve, and compare with using one source alone."],
  scenes: [
    { id: "agv", robot: true, name: ["AGV 沿通道行驶", "AGV along an aisle"],
      params: { sw: { min: 0.001, max: 0.1, step: 0.001, value: 0.01 }, sv: { min: 0.01, max: 1, step: 0.01, value: 0.05 }, p0: { min: 0.01, max: 1, step: 0.01, value: 0.2 } },
      problem: { title: ["机器人问题：里程计与定位测量怎样结合", "Robot problem: combining odometry and position fixes"],
                 text: ["里程计平滑但误差累积，UWB 定位不累积但每次都跳。每 0.1 s 怎样给出最好的位置？",
                        "Odometry is smooth but drifts; UWB fixes do not drift but jump. What is the best position every 0.1 s?"] } },
    { id: "walk", name: ["手机步行导航", "Phone navigation on foot"],
      params: { sw: { min: 0.05, max: 2, step: 0.05, value: 0.3 }, sv: { min: 1, max: 20, step: 0.5, value: 5 }, p0: { min: 1, max: 30, step: 1, value: 10 } },
      problem: { title: ["生活中的例子：走进隧道，蓝点周围的圆圈变大", "Everyday example: in a tunnel the circle round the blue dot grows"],
                 text: ["计步器推算位置，GPS 每秒修正一次；第 40～59 s 在隧道里，没有 GPS。",
                        "The step counter dead-reckons, GPS corrects each second; from 40 s to 59 s you are in a tunnel without GPS."] } },
  ],
  params: [
    { id: "sw", name: ["每步里程计（计步器）误差 σ_w", "Per-step odometry error σ_w"], min: 0.001, max: 0.1, step: 0.001, value: 0.01, unit: "m", digits: 3 },
    { id: "sv", name: ["定位测量误差 σ_v", "Position-fix error σ_v"], min: 0.01, max: 1, step: 0.01, value: 0.05, unit: "m", digits: 2 },
    { id: "p0", name: ["初始估计的标准差 √P₀", "Initial std √P₀"], min: 0.01, max: 1, step: 0.01, value: 0.2, unit: "m", digits: 2 },
  ],
  tasks: [
    { id: "ex", robot: true, text: ["用算例 9.5.1 的参数（0.01、0.05、0.2 m）运行 100 步，滤波的误差小于只用测量和只用里程计。", "With Example 9.5.1's values (0.01, 0.05, 0.2 m) run 100 steps: the filter beats both measurements alone and odometry alone."],
      demo: { scene: "agv", set: { sw: 0.01, sv: 0.05, p0: 0.2 }, press: ["start"], wait: 8 } },
    { id: "kinf", robot: true, text: ["把 σ_v 改为 0.02 m 运行到底，读出最后的增益，与式 (9.5.9) 的 K∞ 相差小于 0.001。", "Set σ_v = 0.02 m and run to the end; the final gain is within 0.001 of K∞ from Eq. (9.5.9)."],
      demo: { scene: "agv", set: { sw: 0.01, sv: 0.02, p0: 0.2 }, press: ["start"], wait: 8 } },
    { id: "blind", robot: true, text: ["把 σ_v 加大到 1 m（定位几乎失效），运行到底，增益降到 0.02 以下，估计几乎只跟着里程计。", "Raise σ_v to 1 m (fixes almost useless) and run: the gain drops below 0.02 and the estimate follows odometry."],
      demo: { scene: "agv", set: { sw: 0.01, sv: 1, p0: 0.2 }, press: ["start"], wait: 8 } },
    { id: "tunnel", text: ["步行场景运行到底，比较进隧道前与出隧道前的 √P：隧道里只预测、不更新，√P 增大到 1.4 倍以上。", "Run the walking scene: with prediction only in the tunnel, √P at the exit exceeds 1.4 times its value at the entrance."],
      demo: { scene: "walk", set: { sw: 0.3, sv: 5, p0: 10 }, press: ["start"], wait: 8 } },
  ],
  think: ["稳态增益只取决于 σ_w 与 σ_v 之比。为什么？里程计越可靠，增益越大还是越小？",
          "Why does the steady-state gain depend only on the ratio σ_w/σ_v? Does a more reliable odometry raise or lower it?"],

  N: 100,
  cfg(api) { return api.scene === "agv" ? { dt: 0.1, u: 0.5, x0: 0.15, gap: [-1, -1] } : { dt: 1, u: 1.4, x0: 6, gap: [40, 59] }; },
  gauss(s) {
    s.seed = (s.seed * 1103515245 + 12345) % 2147483648; const u1 = s.seed / 2147483648 + 1e-12;
    s.seed = (s.seed * 1103515245 + 12345) % 2147483648; const u2 = s.seed / 2147483648;
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  },
  kinf(api) { const q = api.p.sw ** 2, r = api.p.sv ** 2, Pm = (q + Math.sqrt(q * q + 4 * q * r)) / 2; return Pm / (Pm + r); },
  reset(api, s) {
    s.seed = 9051; s.k = 0; s.clock = 0;
    s.x = this.cfg(api).x0; s.xh = 0; s.P = api.p.p0 ** 2; s.odo = 0;
    s.rows = [];        // [k, 真实, 测量或 null, 里程计推算, 估计, √P, K]
  },
  update(dt, api, s) {
    s.clock += dt;
    const c = this.cfg(api), p = api.p;
    while (s.clock > 0.04 && s.k < this.N) {
      s.clock -= 0.04; s.k += 1;
      s.x += c.u * c.dt + p.sw * this.gauss(s);
      const noise = p.sv * this.gauss(s);
      const inGap = s.k >= c.gap[0] && s.k <= c.gap[1];
      const z = inGap ? null : s.x + noise;
      s.odo += c.u * c.dt;
      const xm = s.xh + c.u * c.dt, Pm = s.P + p.sw ** 2;
      let K = 0;
      if (z !== null) { K = Pm / (Pm + p.sv ** 2); s.xh = xm + K * (z - xm); s.P = (1 - K) * Pm; } else { s.xh = xm; s.P = Pm; }
      s.rows.push([s.k, s.x, z, s.odo, s.xh, Math.sqrt(s.P), K]);
    }
    if (s.k >= this.N) api.stop();
  },
  rms(rows, col) {
    const half = rows.filter((r) => r[0] > this.N / 2 && r[col] !== null);
    return half.length ? Math.sqrt(half.reduce((a, r) => a + (r[col] - r[1]) ** 2, 0) / half.length) : NaN;
  },
  readouts(api, s) {
    const last = s.rows[s.rows.length - 1], f = (x, d) => (x === undefined || isNaN(x) ? "—" : api.fmt(x, d));
    const done = s.k >= this.N, ki = this.kinf(api), rz = this.rms(s.rows, 2), ro = this.rms(s.rows, 3), rk = this.rms(s.rows, 4);
    const lastK = (s.rows.filter((r) => r[6] > 0).pop() || [])[6];
    if (api.scene === "agv" && done) {
      const p = api.p, ex = Math.abs(p.sw - 0.01) < 1e-9 && Math.abs(p.sv - 0.05) < 1e-9 && Math.abs(p.p0 - 0.2) < 1e-9;
      if (ex && rk < rz && rk < ro) api.done("ex");
      if (Math.abs(p.sv - 0.02) < 1e-9 && Math.abs(lastK - ki) < 0.001) api.done("kinf");
      if (p.sv >= 0.9 && lastK < 0.02) api.done("blind");
    }
    let before = NaN, after = NaN;
    if (api.scene === "walk") {
      const r39 = s.rows.find((r) => r[0] === 39), r59 = s.rows.find((r) => r[0] === 59);
      before = r39 ? r39[5] : NaN; after = r59 ? r59[5] : NaN;
      if (done && after > 1.4 * before) api.done("tunnel");
    }
    const rows = [[["步数 k", "step k"], String(s.k)],
                  [["卡尔曼增益（最近一次更新）", "Kalman gain (last update)"], f(lastK, 4)],
                  [["稳态增益 K∞（式 (9.5.9)）", "steady-state gain K∞ (Eq. (9.5.9))"], f(ki, 4)],
                  [["估计的标准差 √P", "estimate std √P"], last ? f(last[5], 3) + " m" : "—"],
                  [["后 50 步均方根误差：只用测量", "RMS error (last 50): fixes only"], f(rz, 3) + " m"],
                  [["后 50 步均方根误差：只用里程计", "RMS error (last 50): odometry only"], f(ro, 3) + " m"],
                  [["后 50 步均方根误差：卡尔曼滤波", "RMS error (last 50): Kalman filter"], f(rk, 3) + " m"]];
    if (api.scene === "walk") rows.push([["√P：进隧道前 / 出隧道前", "√P: entering / leaving the tunnel"], `${f(before, 2)} / ${f(after, 2)}`]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, c = this.cfg(api), rows = s.rows;
    const x0 = 56, x1 = w - 16, yt = 26, yb = h * 0.66, scale = api.scene === "agv" ? 0.2 : 20;
    const X = (k) => x0 + (x1 - x0) * k / this.N, Y = (e) => (yt + yb) / 2 - (yb - yt) / 2 * Math.max(-1, Math.min(1, e / scale));
    api.rect(x0, yt, x1 - x0, yb - yt, null, api.css("--grid"));
    api.line(x0, Y(0), x1, Y(0), api.css("--muted"), 1);
    if (c.gap[0] > 0) { const ctx = api.ctx; ctx.globalAlpha = 0.25; api.rect(X(c.gap[0]), yt, X(c.gap[1]) - X(c.gap[0]), yb - yt, api.css("--muted")); ctx.globalAlpha = 1;
      api.label(api.T("隧道（无 GPS）", "tunnel (no GPS)"), (X(c.gap[0]) + X(c.gap[1])) / 2, yt + 12, api.css("--muted"), 11, "center"); }
    const ctx = api.ctx;
    // ±2√P 带
    if (rows.length > 1) {
      ctx.beginPath(); rows.forEach((r, i) => { const yy = Y(2 * r[5]); i ? ctx.lineTo(X(r[0]), yy) : ctx.moveTo(X(r[0]), yy); });
      for (let i = rows.length - 1; i >= 0; i--) ctx.lineTo(X(rows[i][0]), Y(-2 * rows[i][5]));
      ctx.closePath(); ctx.globalAlpha = 0.15; ctx.fillStyle = api.css("--blue"); ctx.fill(); ctx.globalAlpha = 1;
    }
    rows.forEach((r) => { if (r[2] !== null) api.circle(X(r[0]), Y(r[2] - r[1]), 2.2, api.css("--amber")); });
    const poly = (col, colr, dash) => { ctx.beginPath(); rows.forEach((r, i) => { const yy = Y(r[col] - r[1]); i ? ctx.lineTo(X(r[0]), yy) : ctx.moveTo(X(r[0]), yy); });
      ctx.strokeStyle = colr; ctx.lineWidth = 2; ctx.setLineDash(dash || []); ctx.stroke(); ctx.setLineDash([]); };
    poly(3, api.css("--muted"), [6, 4]);
    poly(4, api.css("--blue"));
    api.label(api.T(`误差 = 估计 − 真实位置（纵轴 ±${scale} m）　金点：测量　灰虚线：只用里程计　蓝：卡尔曼滤波　浅蓝带：±2√P`,
                    `error = estimate − truth (axis ±${scale} m)   gold: fixes   grey dashed: odometry only   blue: Kalman   band: ±2√P`), x0, 12, api.css("--muted"), 11);
    // 增益
    const gy0 = h * 0.74, gy1 = h - 18;
    api.rect(x0, gy0, x1 - x0, gy1 - gy0, null, api.css("--grid"));
    ctx.beginPath(); rows.forEach((r, i) => { const yy = gy1 - (gy1 - gy0) * r[6]; i ? ctx.lineTo(X(r[0]), yy) : ctx.moveTo(X(r[0]), yy); });
    ctx.strokeStyle = api.css("--red"); ctx.lineWidth = 1.8; ctx.stroke();
    const ki = this.kinf(api);
    api.line(x0, gy1 - (gy1 - gy0) * ki, x1, gy1 - (gy1 - gy0) * ki, api.css("--muted"), 1, [4, 4]);
    api.label(api.T("增益 K（0～1），虚线为 K∞", "gain K (0 to 1), dashed: K∞"), x0 + 4, gy0 + 10, api.css("--red"), 11);
  },
});
