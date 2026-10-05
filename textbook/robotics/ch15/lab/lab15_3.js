// 实验 15.3 在奇异点附近比较三种方法（配 15.3 节）。
// 机器人场景：平面 2R 臂 0.425、0.392 m（算例 15.2.1）。目标沿水平线 y = 0.25 m 从 x = 0.30 m 移到 0.78 m 再回来（6 s），
// 最远处离基座 0.819 m，略超出臂长之和 0.817 m：手臂经过伸直的奇异位形附近。控制周期 5 ms，关节速度
//   精确求逆：θ̇ = J⁻¹(ṗ_d + K e)；雅可比转置：θ̇ = K_t Jᵀ e；阻尼最小二乘：θ̇ = Jᵀ(JJᵀ + λ²I)⁻¹(ṗ_d + K e)，K = 20 s⁻¹。
// 关节速度上限取 120°/s（只用来判断，不限幅）。
// 生活场景：地平式望远镜（方位轴竖直、俯仰轴水平）跟踪一颗沿大圆匀速（2°/s）飞过天顶附近的卫星，最近天顶距 δ。
//   在指向的切平面内，误差的方位分量与俯仰分量对 (方位角, 俯仰角) 的雅可比矩阵为 diag(cos el, 1)，天顶处奇异。
WQ.lab({
  title: ["实验 15.3 在奇异点附近比较三种方法", "Lab 15.3 Three methods near a singularity"],
  goal: ["让目标经过奇异位形附近，比较精确求逆、雅可比转置和阻尼最小二乘：关节速度会不会失控，跟踪误差有多大，阻尼系数怎样权衡两者。",
         "Send the target past a singular configuration and compare the exact inverse, the Jacobian transpose and damped least squares: do the joint speeds run away, how large is the tracking error, and how does the damping trade one for the other."],
  scenes: [
    { id: "arm", robot: true, name: ["2R 臂经过伸直位形", "2R arm past the straight posture"],
      problem: { title: ["机器人问题：目标从手臂够得着的边缘擦过", "Robot problem: the target grazes the edge of the reach"],
                 text: ["红点沿虚线匀速来回，最远处略超出臂长之和。控制器每 5 ms 算一次关节速度。下方曲线：两个关节的转速（灰线为 120°/s 上限）和跟踪误差。",
                        "The red dot moves back and forth along the dashed line; at its farthest it is just beyond the total reach. The controller computes joint speeds every 5 ms. Curves below: both joint speeds (grey line: 120°/s limit) and the tracking error."] } },
    { id: "scope", name: ["望远镜跟踪卫星", "Telescope tracking a satellite"], hide: ["kt"],
      problem: { title: ["生活中的例子：卫星从头顶附近飞过", "Everyday example: a satellite passes nearly overhead"],
                 text: ["俯视天空：圆周是地平线，圆心是天顶。卫星（红点）沿直线飞过，离天顶最近为 δ。看方位轴转速和指向误差。",
                        "The sky seen from above: the circle is the horizon, its centre the zenith. The satellite (red) flies straight across, nearest the zenith at δ. Watch the azimuth speed and the pointing error."] } },
  ],
  params: [
    { id: "method", name: ["方法：0 精确求逆 / 1 雅可比转置 / 2 阻尼最小二乘", "method: 0 exact inverse / 1 Jacobian transpose / 2 damped least squares"], min: 0, max: 2, step: 1, value: 2, unit: "", digits: 0 },
    { id: "lam", name: ["阻尼系数 λ（臂：m；望远镜：无量纲）", "damping λ (arm: m; telescope: dimensionless)"], min: 0.0, max: 0.2, step: 0.005, value: 0.035, unit: "", digits: 3 },
    { id: "kt", name: ["雅可比转置的增益 K_t", "Jacobian transpose gain K_t"], min: 10, max: 400, step: 10, value: 200, unit: "rad²/(m²·s)", digits: 0 },
    { id: "delta", name: ["望远镜：最近天顶距 δ", "telescope: closest zenith distance δ"], min: 0.5, max: 15, step: 0.5, value: 2, unit: "°", digits: 1 },
  ],
  tasks: [
    { id: "exact", robot: true, text: ["用精确求逆跟踪：关节速度的尖峰超过 300°/s。", "Track with the exact inverse: the joint speed peaks above 300°/s."],
      demo: { scene: "arm", set: { method: 0 }, press: ["start"], wait: 14 } },
    { id: "dls", robot: true, text: ["用阻尼最小二乘跟踪：最大关节速度不超过 120°/s，最大跟踪误差小于 5 mm。", "Track with damped least squares: joint speeds stay within 120°/s and the tracking error within 5 mm."],
      demo: { scene: "arm", set: { method: 2, lam: 0.035 }, press: ["start"], wait: 14 } },
    { id: "jt", robot: true, text: ["用雅可比转置跟踪：关节速度不超限，但跟踪误差超过 5 mm（滞后）。", "Track with the Jacobian transpose: no speed limit is broken, but the error exceeds 5 mm (it lags)."],
      demo: { scene: "arm", set: { method: 1, kt: 200 }, press: ["start"], wait: 14 } },
    { id: "scope", text: ["生活场景：δ = 2° 时用阻尼最小二乘，把方位轴的峰值转速降到精确跟踪所需的一半以下，读出指向误差。", "Everyday scene: with δ = 2°, use damped least squares to bring the peak azimuth speed below half of what exact tracking needs; read the pointing error."],
      demo: { scene: "scope", set: { method: 2, lam: 0.2, delta: 2 }, press: ["start"], wait: 14 } },
  ],
  think: ["阻尼最小二乘在奇异附近“放弃”了哪个方向的误差？对 2R 臂和望远镜分别说明，并解释为什么误差在离开奇异区后会自己消失。",
          "Near the singularity, which direction of the error does damped least squares give up? Say it for the 2R arm and for the telescope, and explain why the error disappears by itself after the singular region."],

  L: [0.425, 0.392], DT: 0.005, K: 20, DUR: 6,
  path(t) { const u = 0.5 - 0.5 * Math.cos(2 * Math.PI * t / this.DUR); return { p: [0.30 + 0.48 * u, 0.25], v: [0.48 * 0.5 * Math.sin(2 * Math.PI * t / this.DUR) * 2 * Math.PI / this.DUR, 0] }; },
  fk(th) { const [a, b] = this.L, e = [a * Math.cos(th[0]), a * Math.sin(th[0])]; return [e, [e[0] + b * Math.cos(th[0] + th[1]), e[1] + b * Math.sin(th[0] + th[1])]]; },
  jac(th) { const [a, b] = this.L, s1 = Math.sin(th[0]), c1 = Math.cos(th[0]), s12 = Math.sin(th[0] + th[1]), c12 = Math.cos(th[0] + th[1]);
    return [[-a * s1 - b * s12, -b * s12], [a * c1 + b * c12, b * c12]]; },
  inv2(A) { const d = A[0][0] * A[1][1] - A[0][1] * A[1][0]; return [[A[1][1] / d, -A[0][1] / d], [-A[1][0] / d, A[0][0] / d]]; },
  mv(A, x) { return [A[0][0] * x[0] + A[0][1] * x[1], A[1][0] * x[0] + A[1][1] * x[1]]; },
  // 望远镜：卫星沿大圆匀速 2°/s 运动，离天顶最近 δ；方向 d = (cos el cos az, cos el sin az, sin el)
  sat(api, t) {
    const dl = api.p.delta * Math.PI / 180, w = 2 * Math.PI / 180, s = w * (t - this.DUR * 2.5);
    const a = [Math.sin(dl), 0, Math.cos(dl)], b = [0, 1, 0];               // 大圆：a cos s + b sin s
    return [a[0] * Math.cos(s), b[1] * Math.sin(s), a[2] * Math.cos(s)];
  },
  dir(q) { return [Math.cos(q[1]) * Math.cos(q[0]), Math.cos(q[1]) * Math.sin(q[0]), Math.sin(q[1])]; },
  reset(api, s) {
    s.t = 0; s.k = 0; s.done = false; s.clock = 0; s.hist = []; s.maxsp = 0; s.maxe = 0;
    if (api.scene === "arm") {
      const p = this.path(0).p, r = Math.hypot(...p), [a, b] = this.L;
      const c2 = (r * r - a * a - b * b) / (2 * a * b), t2 = Math.acos(c2);                 // 肘下的一组（θ₂ > 0）
      s.th = [Math.atan2(p[1], p[0]) - Math.atan2(b * Math.sin(t2), a + b * Math.cos(t2)), t2];
    } else {
      const d = this.sat(api, 0);
      s.q = [Math.atan2(d[1], d[0]), Math.asin(d[2])];
    }
  },
  step(api, s) {
    const dt = this.DT, m = api.p.method, lam = api.p.lam;
    if (api.scene === "arm") {
      const P = this.path(s.t), tip = this.fk(s.th)[1], e = [P.p[0] - tip[0], P.p[1] - tip[1]], J = this.jac(s.th);
      const b = [P.v[0] + this.K * e[0], P.v[1] + this.K * e[1]];
      let dth;
      if (m === 0) dth = this.mv(this.inv2(J), b);
      else if (m === 1) { const g = [J[0][0] * e[0] + J[1][0] * e[1], J[0][1] * e[0] + J[1][1] * e[1]]; dth = [api.p.kt * g[0], api.p.kt * g[1]]; }
      else { const A = [[J[0][0] ** 2 + J[0][1] ** 2 + lam * lam, J[0][0] * J[1][0] + J[0][1] * J[1][1]], [J[0][0] * J[1][0] + J[0][1] * J[1][1], J[1][0] ** 2 + J[1][1] ** 2 + lam * lam]];
        const y = this.mv(this.inv2(A), b); dth = [J[0][0] * y[0] + J[1][0] * y[1], J[0][1] * y[0] + J[1][1] * y[1]]; }
      dth = dth.map((x) => (isFinite(x) ? Math.max(-200, Math.min(200, x)) : 200));     // 只为防止数值溢出
      const sp = Math.max(Math.abs(dth[0]), Math.abs(dth[1])) * 180 / Math.PI, en = Math.hypot(...e);
      s.th = s.th.map((x, i) => x + dth[i] * dt);
      s.maxsp = Math.max(s.maxsp, sp); s.maxe = Math.max(s.maxe, en);
      if (s.k % 4 === 0) s.hist.push([s.t, Math.abs(dth[0]) * 180 / Math.PI, Math.abs(dth[1]) * 180 / Math.PI, en * 1000]);
    } else {
      const dt2 = this.DT, D = this.sat(api, s.t), Dn = this.sat(api, s.t + dt2), [az, el] = s.q;
      const eaz = [-Math.sin(az), Math.cos(az), 0], eel = [-Math.sin(el) * Math.cos(az), -Math.sin(el) * Math.sin(az), Math.cos(el)];
      const d = this.dir(s.q), dd = [D[0] - d[0], D[1] - d[1], D[2] - d[2]], vd = [(Dn[0] - D[0]) / dt2, (Dn[1] - D[1]) / dt2, (Dn[2] - D[2]) / dt2];
      const e = [eaz[0] * dd[0] + eaz[1] * dd[1], eel[0] * dd[0] + eel[1] * dd[1] + eel[2] * dd[2]];
      const v = [eaz[0] * vd[0] + eaz[1] * vd[1], eel[0] * vd[0] + eel[1] * vd[1] + eel[2] * vd[2]];
      const Ks = 3, b = [v[0] + Ks * e[0], v[1] + Ks * e[1]], c = Math.cos(el);
      let rate;
      if (m === 0) rate = [b[0] / c, b[1]];
      else if (m === 1) rate = [5 * c * e[0], 5 * e[1]];
      else rate = [c * b[0] / (c * c + lam * lam), b[1] / (1 + lam * lam)];
      rate = rate.map((x) => (isFinite(x) ? Math.max(-100, Math.min(100, x)) : 100));
      s.q = [s.q[0] + rate[0] * dt2, s.q[1] + rate[1] * dt2];
      const dn = this.dir(s.q), ang = Math.acos(Math.max(-1, Math.min(1, dn[0] * Dn[0] + dn[1] * Dn[1] + dn[2] * Dn[2]))) * 180 / Math.PI;
      const sp = Math.abs(rate[0]) * 180 / Math.PI;
      s.maxsp = Math.max(s.maxsp, sp); s.maxe = Math.max(s.maxe, ang);
      if (s.k % 4 === 0) s.hist.push([s.t, sp, Math.abs(rate[1]) * 180 / Math.PI, ang]);
    }
    s.t += dt; s.k += 1;
    const T = api.scene === "arm" ? this.DUR : this.DUR * 5;
    if (s.t >= T - 1e-9) { s.done = true; api.stop(); }
  },
  update(dt, api, s) {
    s.clock += dt;
    const n = api.scene === "arm" ? 1 : 5;                         // 望远镜过程 30 s，按 5 倍速显示
    while (s.clock >= this.DT && api.running) { s.clock -= this.DT; for (let i = 0; i < n && api.running; i++) this.step(api, s); }
  },
  readouts(api, s) {
    const m = api.p.method, names = [api.T("精确求逆", "exact inverse"), api.T("雅可比转置", "Jacobian transpose"), api.T("阻尼最小二乘", "damped least squares")];
    if (api.scene === "arm" && s.done) {
      if (m === 0 && s.maxsp > 300) api.done("exact");
      if (m === 2 && s.maxsp <= 120 && s.maxe < 0.005) api.done("dls");
      if (m === 1 && s.maxsp <= 120 && s.maxe > 0.005) api.done("jt");
    }
    const need = 2 / Math.sin(api.p.delta * Math.PI / 180);       // 精确跟踪所需的方位轴峰值转速 ω/sin δ（°/s）
    if (api.scene === "scope" && s.done && m === 2 && Math.abs(api.p.delta - 2) < 1e-9 && s.maxsp < 0.5 * need) api.done("scope");
    const arm = api.scene === "arm";
    return [[["方法", "method"], names[m]], [["时间", "time"], s.t.toFixed(2) + " s"],
            [arm ? ["最大关节速度", "peak joint speed"] : ["方位轴最大转速", "peak azimuth speed"], s.maxsp.toFixed(1) + " °/s"],
            [arm ? ["最大跟踪误差", "peak tracking error"] : ["最大指向误差", "peak pointing error"], arm ? (s.maxe * 1000).toFixed(2) + " mm" : s.maxe.toFixed(2) + "°"],
            ...(arm ? [] : [[["精确跟踪所需的峰值 ω/sin δ", "peak needed for exact tracking ω/sin δ"], need.toFixed(1) + " °/s"]]),
            [["状态", "status"], s.done ? api.T("结束", "finished") : api.running ? api.T("跟踪中", "tracking") : "—"]];
  },
  draw(api, s) {
    const { w, h } = api, arm = api.scene === "arm";
    if (arm) {
      const sc = h * 0.62, ox = w * 0.18, oy = h * 0.6, X = (p) => [ox + sc * p[0], oy - sc * p[1]];
      const R = 0.817 * sc; api.ctx.strokeStyle = api.css("--grid"); api.ctx.lineWidth = 1; api.ctx.beginPath(); api.ctx.arc(ox, oy, R, -Math.PI / 2, 0.3); api.ctx.stroke();
      const a = X([0.30, 0.25]), b = X([0.78, 0.25]); api.line(a[0], a[1], b[0], b[1], api.css("--amber"), 1.5, [5, 4]);
      const [e, t] = this.fk(s.th).map(X), O = X([0, 0]);
      api.rect(O[0] - 14, O[1] + 6, 28, 9, api.css("--muted"));
      api.line(O[0], O[1], e[0], e[1], api.css("--blue"), 10); api.line(e[0], e[1], t[0], t[1], api.css("--blue"), 7);
      api.circle(O[0], O[1], 5, api.css("--panel"), api.css("--ink")); api.circle(e[0], e[1], 5, api.css("--panel"), api.css("--ink"));
      const P = X(this.path(s.t).p); api.circle(P[0], P[1], 5, api.css("--red"));
      api.label(api.T("外边界 r = 0.817 m", "outer edge r = 0.817 m"), ox + R * 0.62, oy - R * 0.85, api.css("--muted"), 12);
    } else {
      const cx = w * 0.27, cy = h * 0.42, R = h * 0.36;
      api.circle(cx, cy, R, "rgba(31,111,235,0.06)", api.css("--grid"));
      api.circle(cx, cy, 3, api.css("--muted")); api.label(api.T("天顶", "zenith"), cx + 6, cy - 8, api.css("--muted"), 12);
      const toXY = (d) => { const zen = Math.acos(Math.max(-1, Math.min(1, d[2]))), az = Math.atan2(d[1], d[0]), r = R * zen / (Math.PI / 2); return [cx + r * Math.cos(az), cy - r * Math.sin(az)]; };
      const pts = []; for (let t = 0; t <= this.DUR * 5; t += 0.5) pts.push(toXY(this.sat(api, t)));
      api.ctx.strokeStyle = api.css("--amber"); api.ctx.setLineDash([5, 4]); api.ctx.beginPath(); pts.forEach((p, i) => (i ? api.ctx.lineTo(p[0], p[1]) : api.ctx.moveTo(p[0], p[1]))); api.ctx.stroke(); api.ctx.setLineDash([]);
      const S = toXY(this.sat(api, s.t)), Tl = toXY(this.dir(s.q));
      api.line(cx, cy, Tl[0], Tl[1], api.css("--blue"), 4); api.circle(Tl[0], Tl[1], 6, null, api.css("--blue"));
      api.circle(S[0], S[1], 5, api.css("--red"));
      api.label(api.T("望远镜指向", "telescope"), Tl[0] + 8, Tl[1] + 12, api.css("--blue"), 12);
    }
    // 曲线：转速（两条）与误差
    const H = s.hist, T = arm ? this.DUR : this.DUR * 5, lim = arm ? 120 : 2 / Math.sin(api.p.delta * Math.PI / 180);
    const g = api.graph({ x: w * 0.58, y: h * 0.08, w: w * 0.38, h: h * 0.36, xmin: 0, xmax: T, ymin: 0, ymax: arm ? 400 : 80,
                          xlabel: api.T("时间 / s", "time / s"), ylabel: arm ? api.T("关节转速 / (°/s)", "joint speed / (°/s)") : api.T("方位轴转速 / (°/s)", "azimuth speed / (°/s)") }).axes();
    g.hline(lim, api.css("--muted"));
    g.pts(H.map((r) => [r[0], Math.min(r[1], 1e4)]), api.css("--blue"), 2);
    if (arm) g.pts(H.map((r) => [r[0], Math.min(r[2], 1e4)]), api.css("--accent"), 2);
    const g2 = api.graph({ x: w * 0.58, y: h * 0.56, w: w * 0.38, h: h * 0.3, xmin: 0, xmax: T, ymin: 0, ymax: arm ? 10 : 8,
                           xlabel: api.T("时间 / s", "time / s"), ylabel: arm ? api.T("跟踪误差 / mm", "tracking error / mm") : api.T("指向误差 / (°)", "pointing error / (°)") }).axes();
    g2.pts(H.map((r) => [r[0], Math.min(r[3], 100)]), api.css("--red"), 2);
  },
});
