// 实验 8.1 在等高线上下山（配 8.1 节）。平面 2R 臂，L = (0.425, 0.392) m，目标 p_d = (0.5, 0.4) m，
// 目标函数 f(θ) = ½‖p(θ) − p_d‖²（式 (8.1.2)），梯度 Jᵀr（式 (8.1.6)），黑塞矩阵 JᵀJ + Σ r_c ∇²p_c（式 (8.1.9)）。
// “雾中下山”：二次函数 f = ½xᵀQx，Q 的特征值为 1 和 κ（条件数），梯度下降取最优固定步长 2/(1 + κ)（定理 8.1.6）。
WQ.lab({
  title: ["实验 8.1 在等高线上下山", "Lab 8.1 Walking downhill on the level curves"],
  goal: ["用梯度下降和牛顿法求平面 2R 臂的逆运动学，在等高线图上看迭代路径；体会步长上限和条件数的作用。",
         "Solve the inverse kinematics of a planar 2R arm by gradient descent and by Newton's method, watch the iterates on the level curves, and see what the step-size limit and the condition number do."],
  scenes: [
    { id: "arm", robot: true, name: ["2R 臂的逆运动学", "Inverse kinematics of a 2R arm"], hide: ["kappa"],
      problem: { title: ["机器人问题：关节转到多少度，末端才能到达目标", "Robot problem: which joint angles bring the tip to the target?"],
                 text: ["把逆运动学写成 min f(θ) = ½‖p(θ) − p_d‖²，从起始形态出发一步步下山。右图是 f 的等高线，横轴 θ₁、纵轴 θ₂。",
                        "Write the inverse kinematics as min f(θ) = ½‖p(θ) − p_d‖² and walk downhill from the start. Right: level curves of f, θ₁ across, θ₂ up."] } },
    { id: "fog", name: ["雾中下山", "Downhill in fog"], hide: ["alpha", "t1", "t2"],
      problem: { title: ["生活中的例子：狭长的山谷", "Everyday example: a long narrow valley"],
                 text: ["在雾中只能感觉脚下最陡的方向。山谷越狭长（条件数 κ 越大），沿最陡方向走就越要来回折返。",
                        "In fog you only feel the steepest slope underfoot. The narrower the valley (the larger κ), the more the steepest path zig-zags."] } },
  ],
  params: [
    { id: "method", name: ["方法：0 梯度下降 / 1 牛顿法", "Method: 0 gradient descent / 1 Newton"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "alpha", name: ["步长 α（梯度下降）", "Step α (gradient descent)"], min: 0.5, max: 5, step: 0.1, value: 3, unit: "rad²/m²", digits: 1 },
    { id: "t1", name: ["起始 θ₁", "Start θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "t2", name: ["起始 θ₂", "Start θ₂"], min: -180, max: 180, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "kappa", name: ["山谷的条件数 κ", "Condition number κ of the valley"], min: 1, max: 50, step: 1, value: 10, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["迭代", "Iterate"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "gd", robot: true, text: ["梯度下降取 α = 3，从默认起点 (0°, 90°) 收敛到逆解。", "Gradient descent with α = 3 from the default start (0°, 90°) converges to a solution."],
      demo: { scene: "arm", set: { method: 0, alpha: 3, t1: 0, t2: 90 }, press: ["start"], wait: 8 } },
    { id: "big", robot: true, text: ["把步长加大到超过 2/λ_max ≈ 3.9，迭代 60 步后仍不收敛。", "Raise the step above 2/λ_max ≈ 3.9: after 60 steps it still has not converged."],
      demo: { scene: "arm", set: { method: 0, alpha: 4.5, t1: 0, t2: 90 }, press: ["start"], wait: 8 } },
    { id: "newton", robot: true, text: ["用牛顿法从默认起点出发，5 步以内收敛。", "Newton's method from the default start converges within 5 steps."],
      demo: { scene: "arm", set: { method: 1, t1: 0, t2: 90 }, press: ["start"], wait: 4 } },
    { id: "fog", text: ["在“雾中下山”中把 κ 调到 20 以上，用梯度下降走到谷底，记下步数，再换牛顿法比较。", "In “Downhill in fog” set κ ≥ 20, reach the bottom by gradient descent, note the steps, then compare with Newton."],
      demo: { scene: "fog", set: { kappa: 25, method: 0 }, press: ["start"], wait: 15 } },
  ],
  think: ["从 (0°, 17°) 出发用牛顿法，迭代收敛到 θ₂ = 0 的形态，梯度确实为零，末端却没有到达目标。这是什么点？为什么牛顿法分辨不出来？",
          "Start Newton's method at (0°, 17°): it converges to θ₂ = 0 with zero gradient, yet the tip misses the target. What kind of point is it, and why can't Newton's method tell?"],

  L1: 0.425, L2: 0.392, PD: [0.5, 0.4],
  tip(t) { return [this.L1 * Math.cos(t[0]) + this.L2 * Math.cos(t[0] + t[1]), this.L1 * Math.sin(t[0]) + this.L2 * Math.sin(t[0] + t[1])]; },
  jac(t) {
    const s1 = Math.sin(t[0]), s12 = Math.sin(t[0] + t[1]), c1 = Math.cos(t[0]), c12 = Math.cos(t[0] + t[1]);
    return [[-this.L1 * s1 - this.L2 * s12, -this.L2 * s12], [this.L1 * c1 + this.L2 * c12, this.L2 * c12]];
  },
  fval(api, x) {
    if (api.scene === "fog") { const Q = this.Q(api); return 0.5 * (Q[0][0] * x[0] * x[0] + 2 * Q[0][1] * x[0] * x[1] + Q[1][1] * x[1] * x[1]); }
    const p = this.tip(x); return 0.5 * ((p[0] - this.PD[0]) ** 2 + (p[1] - this.PD[1]) ** 2);
  },
  grad(api, x) {
    if (api.scene === "fog") { const Q = this.Q(api); return [Q[0][0] * x[0] + Q[0][1] * x[1], Q[0][1] * x[0] + Q[1][1] * x[1]]; }
    const p = this.tip(x), r = [p[0] - this.PD[0], p[1] - this.PD[1]], J = this.jac(x);
    return [J[0][0] * r[0] + J[1][0] * r[1], J[0][1] * r[0] + J[1][1] * r[1]];
  },
  hess(api, x) {
    if (api.scene === "fog") return this.Q(api);
    const p = this.tip(x), r = [p[0] - this.PD[0], p[1] - this.PD[1]], J = this.jac(x);
    const e2 = [p[0] - this.L1 * Math.cos(x[0]), p[1] - this.L1 * Math.sin(x[0])];          // 关节 2 指向末端
    const a = -(r[0] * p[0] + r[1] * p[1]), b = -(r[0] * e2[0] + r[1] * e2[1]);
    const H = [[J[0][0] ** 2 + J[1][0] ** 2 + a, J[0][0] * J[0][1] + J[1][0] * J[1][1] + b], [0, J[0][1] ** 2 + J[1][1] ** 2 + b]];
    H[1][0] = H[0][1];
    return H;
  },
  Q(api) {                                // 特征值 1 和 κ，主轴转 30°
    const k = api.p.kappa, c = Math.cos(Math.PI / 6), s = Math.sin(Math.PI / 6);
    return [[c * c + k * s * s, (1 - k) * c * s], [(1 - k) * c * s, s * s + k * c * c]];
  },
  sols() {                                // 两组解析逆解（余弦定理）
    const d2 = this.PD[0] ** 2 + this.PD[1] ** 2, c2 = (d2 - this.L1 ** 2 - this.L2 ** 2) / (2 * this.L1 * this.L2);
    return [1, -1].map((e) => { const t2 = e * Math.acos(c2); return [Math.atan2(this.PD[1], this.PD[0]) - Math.atan2(this.L2 * Math.sin(t2), this.L1 + this.L2 * Math.cos(t2)), t2]; });
  },
  wrap(a) { return Math.atan2(Math.sin(a), Math.cos(a)); },
  err(api, x) {
    if (api.scene === "fog") return Math.hypot(x[0], x[1]);
    return Math.min(...this.sols().map((s) => Math.hypot(this.wrap(x[0] - s[0]), this.wrap(x[1] - s[1]))));
  },
  start0(api) { return api.scene === "fog" ? [-2.6, 0.9] : [api.p.t1 * Math.PI / 180, api.p.t2 * Math.PI / 180]; },

  reset(api, s) { s.x = this.start0(api); s.path = [s.x.slice()]; s.k = 0; s.clock = 0; s.done = false; s.diverged = false; },
  update(dt, api, s) {
    s.clock += dt;
    while (s.clock >= 0.04 && api.running) { s.clock -= 0.04; this.step(api, s); }
  },
  step(api, s) {
    const g = this.grad(api, s.x);
    if (Math.hypot(g[0], g[1]) < 1e-8) { s.done = true; api.stop(); return; }   // 与算例 8.1.3 相同的停止条件
    let d;
    if (api.p.method === 1) {
      const H = this.hess(api, s.x), det = H[0][0] * H[1][1] - H[0][1] * H[1][0];
      d = [-(H[1][1] * g[0] - H[0][1] * g[1]) / det, -(-H[1][0] * g[0] + H[0][0] * g[1]) / det];
    } else {
      const a = api.scene === "fog" ? 2 / (1 + api.p.kappa) : api.p.alpha;
      d = [-a * g[0], -a * g[1]];
    }
    s.x = [s.x[0] + d[0], s.x[1] + d[1]];
    s.k += 1;
    s.path.push(s.x.slice());
    if (!isFinite(s.x[0]) || Math.hypot(s.x[0], s.x[1]) > 1e3) { s.diverged = true; api.stop(); }
    if (s.k >= 600) api.stop();
  },
  readouts(api, s) {
    const e = this.err(api, s.x), conv = s.done || e < 1e-8;
    if (api.scene === "arm") {
      if (conv && api.p.method === 0 && Math.abs(api.p.alpha - 3) < 0.05 && api.p.t1 === 0 && api.p.t2 === 90) api.done("gd");
      if (api.p.method === 0 && api.p.alpha > 3.9 && s.k >= 60 && e > 1e-3) api.done("big");
      if (conv && api.p.method === 1 && s.k <= 5 && api.p.t1 === 0 && api.p.t2 === 90) api.done("newton");
    } else if (conv && api.p.method === 0 && api.p.kappa >= 20) api.done("fog");
    const f = this.fval(api, s.x), deg = (a) => api.fmt(a * 180 / Math.PI, 2);
    const rows = [[["方法", "method"], api.p.method === 1 ? api.T("牛顿法", "Newton") : api.T("梯度下降", "gradient descent")],
                  [["迭代次数 k", "iteration k"], String(s.k)],
                  [["f", "f"], f < 1e-3 ? f.toExponential(2) : api.fmt(f, 4)],
                  [["与最近的极小点之差", "distance to the nearest minimum"], e < 1e-3 ? e.toExponential(1) : api.fmt(e, 4)]];
    if (api.scene === "arm") {
      rows.push([["当前 θ", "current θ"], `(${deg(this.wrap(s.x[0]))}°, ${deg(this.wrap(s.x[1]))}°)`]);
      rows.push([["解处的步长上限 2/λ_max", "step limit 2/λ_max at the solution"], "3.90 rad²/m²"]);
    } else {
      rows.push([["梯度下降的步长 2/(1 + κ)", "gradient step 2/(1 + κ)"], api.fmt(2 / (1 + api.p.kappa), 3)]);
    }
    if (s.diverged) rows.push([["状态", "status"], api.T("发散", "diverged")]);
    return rows;
  },
  draw(api, s) {
    const { w, h, ctx } = api;
    const fog = api.scene === "fog";
    const side = Math.min(fog ? w * 0.9 : w * 0.5, h * 0.88), x0 = fog ? (w - side) / 2 : w * 0.97 - side, y0 = (h - side) / 2;
    const rng = fog ? [-3, 3] : [-Math.PI, Math.PI];
    const X = (a) => x0 + (a - rng[0]) / (rng[1] - rng[0]) * side, Y = (b) => y0 + side - (b - rng[0]) / (rng[1] - rng[0]) * side;
    // 等高线：按 log f 分层着色（画在一张缓存的小画布上，参数不变就不重画）
    const n = 96, bg = api.css("--stage"), dark = parseInt(bg.slice(1, 3), 16) < 128;
    const key = [api.scene, api.p.kappa, dark].join("|");
    if (!this._bg || this._bg.key !== key) {
      const cv = document.createElement("canvas"); cv.width = n; cv.height = n;
      const c2 = cv.getContext("2d"), img = c2.createImageData(n, n);
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
        const a = rng[0] + (i + 0.5) / n * (rng[1] - rng[0]), b = rng[0] + (j + 0.5) / n * (rng[1] - rng[0]);
        const lv = Math.floor(Math.log(this.fval(api, [a, b]) + 1e-9) / Math.log(fog ? 2 : 1.8));
        const band = ((lv % 2) + 2) % 2, tone = Math.max(-40, Math.min(25, lv * 3));
        const shade = dark ? 40 + band * 14 + tone / 2 : 200 + band * 18 + tone;
        const o = 4 * ((n - 1 - j) * n + i);
        img.data[o] = shade - 20; img.data[o + 1] = shade; img.data[o + 2] = Math.min(255, shade + 25); img.data[o + 3] = 255;
      }
      c2.putImageData(img, 0, 0);
      this._bg = { key, cv };
    }
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(this._bg.cv, x0, y0, side, side);
    api.rect(x0, y0, side, side, null, api.css("--ink"));
    api.label(fog ? "x₁" : "θ₁", x0 + side - 4, y0 + side + 12, api.css("--muted"), 12, "right");
    api.label(fog ? "x₂" : "θ₂", x0 - 6, y0 + 8, api.css("--muted"), 12, "right");
    if (!fog) this.sols().forEach((sl) => api.circle(X(sl[0]), Y(sl[1]), 6, api.css("--red"), api.css("--ink")));
    else api.circle(X(0), Y(0), 6, api.css("--red"), api.css("--ink"));
    // 迭代路径（角度化到 (−180°, 180°]）
    const pts = s.path.map((p) => (fog ? p : [this.wrap(p[0]), this.wrap(p[1])]));
    ctx.strokeStyle = api.p.method === 1 ? api.css("--blue") : api.css("--amber"); ctx.lineWidth = 2;
    ctx.beginPath();
    pts.forEach((p, i) => { const q = [X(Math.max(rng[0], Math.min(rng[1], p[0]))), Y(Math.max(rng[0], Math.min(rng[1], p[1])))]; if (i && Math.abs(p[0] - pts[i - 1][0]) < 3 && Math.abs(p[1] - pts[i - 1][1]) < 3) ctx.lineTo(...q); else ctx.moveTo(...q); });
    ctx.stroke();
    const cur = pts[pts.length - 1];
    api.circle(X(Math.max(rng[0], Math.min(rng[1], cur[0]))), Y(Math.max(rng[0], Math.min(rng[1], cur[1]))), 5, api.css("--ink"));
    if (fog) return;
    // 左：机械臂
    const k = Math.min(w * 0.4, h * 0.9) / 1.1, bx = w * 0.12, by = h * 0.62;
    const P = (q) => [bx + k * q[0], by - k * q[1]];
    api.line(bx - 0.1 * k, by, bx + 0.9 * k, by, api.css("--grid"), 1);
    const t = s.x, e = [this.L1 * Math.cos(t[0]), this.L1 * Math.sin(t[0])], p = this.tip(t);
    const B = P([0, 0]), E = P(e), T = P(p), D = P(this.PD);
    api.line(D[0] - 6, D[1] - 6, D[0] + 6, D[1] + 6, api.css("--red"), 2.5); api.line(D[0] - 6, D[1] + 6, D[0] + 6, D[1] - 6, api.css("--red"), 2.5);
    api.label("p_d", D[0] + 8, D[1] - 10, api.css("--red"), 13);
    api.line(B[0], B[1], E[0], E[1], api.css("--accent"), 8); api.line(E[0], E[1], T[0], T[1], api.css("--accent"), 6);
    api.circle(B[0], B[1], 6, api.css("--panel"), api.css("--ink")); api.circle(E[0], E[1], 5, api.css("--panel"), api.css("--ink"));
    api.circle(T[0], T[1], 4, api.css("--ink"));
  },
});
