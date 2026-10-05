// 实验 15.2 雅可比转置法：用虚拟弹簧拉手臂（配 15.2 节）。
// 机器人场景：平面 3R 臂 0.425、0.392、0.1 m（UR5e 侧视，14.2.5 节），只要求末端位置（三个关节、两个方程）。
// 每一步 Δθ = α Jᵀ e（式 (15.2.4)），e = p_d − p(θ)；α 固定，或按式 (15.2.8) 每步取 α = eᵀJJᵀe / ‖JJᵀe‖²。
// 关节上的绿色弧线是弹簧（kₛ = 100 N/m）在各关节产生的力矩 τ = Jᵀ F（式 (15.2.1)）。
// 生活场景：五节折叠尺（每节 0.16 m），左端按在桌上，手拉住尺端拖向记号；铰链有摩擦，各节转速与力矩成正比（式 (15.2.2)）。
WQ.lab({
  title: ["实验 15.2 雅可比转置法：用虚拟弹簧拉手臂", "Lab 15.2 The Jacobian transpose method: pulling an arm with a virtual spring"],
  goal: ["看雅可比转置法怎样把末端的误差变成关节的转动：误差从不增大，但收敛是线性的；步长过大会失稳；目标够不着时手臂伸直指向目标。",
         "See how the Jacobian transpose method turns the tip error into joint motion: the error never grows, but convergence is linear; too large a step is unstable; an unreachable target leaves the arm straight and pointing at it."],
  scenes: [
    { id: "arm", robot: true, name: ["平面 3R 臂", "Planar 3R arm"],
      problem: { title: ["机器人问题：不解方程，让末端到达目标", "Robot problem: reach the target without solving equations"],
                 text: ["末端与目标之间挂一根弹簧，绿色弧线是弹簧在各关节产生的力矩 τ = Jᵀ F。按“开始”迭代，右下角是误差 ‖e‖ 的对数随迭代次数的变化。",
                        "A spring joins the tip to the target; green arcs are the joint torques τ = Jᵀ F it causes. Press “Start” to iterate; the lower right shows log ‖e‖ against the iteration."] } },
    { id: "ruler", name: ["折叠尺", "Folding ruler"], hide: ["mode", "alpha"],
      problem: { title: ["生活中的例子：拉着折叠尺的一端拖向记号", "Everyday example: drag a folding ruler by its end to a mark"],
                 text: ["五节折叠尺的左端按在桌上，手捏住右端向红色记号拉。铰链有摩擦，尺子不会甩动，各节一点一点地转过去。",
                        "The left end of a five-part folding ruler is held on the table; a hand pulls the right end toward the red mark. The hinges have friction, so the ruler does not swing; each part turns little by little."] } },
  ],
  params: [
    { id: "x", name: ["目标 x", "target x"], min: -0.9, max: 1.0, step: 0.01, value: 0.45, unit: "m", digits: 2 },
    { id: "y", name: ["目标 y", "target y"], min: -0.6, max: 0.9, step: 0.01, value: 0.35, unit: "m", digits: 2 },
    { id: "mode", name: ["步长：0 固定 α / 1 每步最优（式 (15.2.8)）", "step: 0 fixed α / 1 optimal each step (Eq. (15.2.8))"], min: 0, max: 1, step: 1, value: 1, unit: "", digits: 0 },
    { id: "alpha", name: ["固定步长 α", "fixed step α"], min: 0.5, max: 12, step: 0.5, value: 3, unit: "rad²/m²", digits: 1 },
  ],
  tasks: [
    { id: "opt", robot: true, text: ["用每步最优步长把末端送到 (0.45, 0.35) m，误差小于 1 µm。", "With the optimal step each time, bring the tip to (0.45, 0.35) m to within 1 µm."],
      demo: { scene: "arm", set: { x: 0.45, y: 0.35, mode: 1 }, press: ["start"], wait: 8 } },
    { id: "fixed", robot: true, text: ["改用固定步长 α = 3 求同一目标，比较迭代次数。", "Use the fixed step α = 3 for the same target and compare the iterations."],
      demo: { scene: "arm", set: { x: 0.45, y: 0.35, mode: 0, alpha: 3 }, press: ["start"], wait: 12 } },
    { id: "big", robot: true, text: ["把固定步长加大到超过上限 2/σ₁²，迭代 300 次后误差仍大于 1 mm。", "Raise the fixed step above the limit 2/σ₁²; after 300 iterations the error is still above 1 mm."],
      demo: { scene: "arm", set: { x: 0.45, y: 0.35, mode: 0, alpha: 11 }, press: ["start"], wait: 12 } },
    { id: "far", robot: true, text: ["把目标移到够不着的 (0.95, 0.30) m：手臂停在伸直、指向目标的形态，Jᵀe 趋于零而 e 不为零。",
                                      "Move the target out of reach to (0.95, 0.30) m: the arm stops straight and pointing at it, Jᵀe tends to zero while e does not."],
      demo: { scene: "arm", set: { x: 0.95, y: 0.3, mode: 1 }, press: ["start"], wait: 10 } },
    { id: "ruler", text: ["生活场景：把折叠尺的尺端拖到记号上，误差小于 1 mm。", "Everyday scene: drag the end of the ruler onto the mark, within 1 mm."],
      demo: { scene: "ruler", set: { x: 0.45, y: 0.3 }, press: ["start"], wait: 10 } },
  ],
  think: ["同一个目标，3R 臂有无穷多组解（三个关节、两个方程）。雅可比转置法停在哪一组？换一个初值会怎样？",
          "For one target the 3R arm has infinitely many solutions (three joints, two equations). Which one does the Jacobian transpose method stop at? What changes with another start?"],

  geo(api) { return api.scene === "ruler" ? [0.16, 0.16, 0.16, 0.16, 0.16] : [0.425, 0.392, 0.1]; },
  start0(api) { return api.scene === "ruler" ? [0.3, -0.6, 0.9, -0.7, 0.5] : [0, 1, -0.5]; },
  pts(th, L) { const P = [[0, 0]]; let a = 0; th.forEach((t, i) => { a += t; const q = P[P.length - 1]; P.push([q[0] + L[i] * Math.cos(a), q[1] + L[i] * Math.sin(a)]); }); return P; },
  jac(th, L) { const P = this.pts(th, L), p = P[P.length - 1]; return [th.map((_, i) => -(p[1] - P[i][1])), th.map((_, i) => p[0] - P[i][0])]; },
  err(api, th, L) { const P = this.pts(th, L), p = P[P.length - 1]; return [api.p.x - p[0], api.p.y - p[1]]; },
  reset(api, s) {
    s.th = this.start0(api); s.k = 0; s.done = false; s.clock = 0; s.hist = [];
    const L = this.geo(api), e = this.err(api, s.th, L); s.e = Math.hypot(...e); s.hist.push(s.e); s.g = 1;
  },
  step(api, s) {
    const L = this.geo(api), e = this.err(api, s.th, L), J = this.jac(s.th, L);
    const g = s.th.map((_, i) => J[0][i] * e[0] + J[1][i] * e[1]);
    let a;
    if (api.scene === "ruler") a = 0.6;                          // 连续时间的近似：小步长（摩擦使转速与力矩成正比）
    else if (api.p.mode === 1) {
      const Jg = [J[0].reduce((t, v, i) => t + v * g[i], 0), J[1].reduce((t, v, i) => t + v * g[i], 0)];
      const d = Jg[0] * Jg[0] + Jg[1] * Jg[1];
      a = d > 0 ? (e[0] * Jg[0] + e[1] * Jg[1]) / d : 0;
    } else a = api.p.alpha;
    s.th = s.th.map((t, i) => t + a * g[i]);
    s.k += 1;
    const e2 = this.err(api, s.th, L);
    s.e = Math.hypot(...e2); s.hist.push(s.e);
    const J2 = this.jac(s.th, L);
    s.g = Math.hypot(...s.th.map((_, i) => J2[0][i] * e2[0] + J2[1][i] * e2[1]));
    if (s.e < 1e-7 || s.g < 1e-10 || s.k >= 3000 || !isFinite(s.e) || s.e > 10) { s.done = true; api.stop(); }
  },
  update(dt, api, s) {
    s.clock += dt;
    const per = api.scene === "ruler" ? 0.004 : s.k < 100 ? 0.02 : 0.002;
    while (s.clock >= per && api.running) { s.clock -= per; this.step(api, s); }
  },
  readouts(api, s) {
    const L = this.geo(api), J = this.jac(s.th, L), sv = api.la.svd(J).s, dg = (x) => (x * 180 / Math.PI).toFixed(1) + "°";
    const fixed = api.scene === "arm" && api.p.mode === 0, near = (a, b) => Math.abs(a - b) < 1e-9;
    if (api.scene === "arm") {
      const def = near(api.p.x, 0.45) && near(api.p.y, 0.35);
      if (def && api.p.mode === 1 && s.done && s.e < 1e-6) api.done("opt");
      if (def && fixed && near(api.p.alpha, 3) && s.done && s.e < 1e-6) api.done("fixed");
      if (def && fixed && api.p.alpha > 2 / (sv[0] * sv[0]) && s.k >= 300 && s.e > 1e-3) api.done("big");
      if (near(api.p.x, 0.95) && near(api.p.y, 0.3) && s.done && s.e > 0.05 && s.g < 1e-9) api.done("far");
    } else if (s.done && s.e < 1e-3) api.done("ruler");
    const rows = [[["迭代次数 k", "iteration k"], String(s.k)], [["误差 ‖e‖", "error ‖e‖"], s.e < 1e-3 ? (s.e * 1e6).toFixed(2) + " µm" : (s.e * 1000).toFixed(2) + " mm"],
                  [["‖Jᵀe‖", "‖Jᵀe‖"], s.g.toExponential(1) + " m²"], [["关节角", "joint angles"], s.th.map(dg).join(", ")]];
    if (api.scene === "arm") rows.push([["J 的奇异值 σ₁、σ₂", "singular values σ₁, σ₂"], sv.map((x) => x.toFixed(3)).join(", ") + " m"],
                                       [["步长上限 2/σ₁²", "step limit 2/σ₁²"], (2 / (sv[0] * sv[0])).toFixed(2) + " rad²/m²"]);
    rows.push([["状态", "status"], s.done ? (s.e < 1e-6 ? api.T("已到达", "reached") : s.g < 1e-9 ? api.T("停在 Jᵀe = 0 处", "stopped where Jᵀe = 0") : api.T("未收敛", "not converged")) : api.running ? api.T("迭代中", "iterating") : "—"]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, L = this.geo(api), ruler = api.scene === "ruler", sc = h / 1.35, ox = w * 0.3, oy = h * (ruler ? 0.62 : 0.68);
    const X = (p) => [ox + sc * p[0], oy - sc * p[1]];
    if (ruler) api.rect(0, oy - sc * 0.55, w, sc * 1.0, "rgba(201,143,0,0.10)");
    else { const b = X([0, 0]); api.rect(b[0] - 16, b[1] + 6, 32, 10, api.css("--muted")); }
    const P = this.pts(s.th, L).map(X), tgt = X([api.p.x, api.p.y]);
    if (ruler) {
      for (let i = 0; i < L.length; i++) { api.line(P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], "#d29922", 12); }
      for (let i = 0; i < L.length; i++) { const a = P[i], b = P[i + 1]; for (let t = 1; t < 8; t++) { const m = [a[0] + (b[0] - a[0]) * t / 8, a[1] + (b[1] - a[1]) * t / 8]; api.circle(m[0], m[1], 1, "#5a3d0a"); } }
      P.slice(1, -1).forEach((p) => api.circle(p[0], p[1], 4, "#fff", "#5a3d0a"));
      api.circle(P[0][0], P[0][1], 8, "rgba(110,118,129,0.6)");
      api.label(api.T("手指按住", "held here"), P[0][0] - 20, P[0][1] + 22, api.css("--muted"), 12);
    } else {
      api.circle(P[0][0], P[0][1], 7, api.css("--muted"));
      for (let i = 0; i < L.length; i++) api.line(P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], api.css("--blue"), [10, 8, 5][i]);
      P.slice(0, -1).forEach((p) => api.circle(p[0], p[1], 5, api.css("--panel"), api.css("--ink")));
      // 关节力矩 τ = Jᵀ F（kₛ = 100 N/m），弧长与力矩成正比
      const e = this.err(api, s.th, L), J = this.jac(s.th, L);
      s.th.forEach((_, i) => {
        const tq = 100 * (J[0][i] * e[0] + J[1][i] * e[1]), ang = Math.max(-2.6, Math.min(2.6, tq / 4));
        if (Math.abs(ang) < 0.08) return;
        const c = api.ctx, r = 18 + 4 * i, p = P[i];
        c.strokeStyle = api.css("--green"); c.lineWidth = 2.5; c.beginPath(); c.arc(p[0], p[1], r, -0.4, -0.4 - ang, ang > 0); c.stroke();
        const ea = -0.4 - ang, tip = [p[0] + r * Math.cos(ea), p[1] + r * Math.sin(ea)], dir = ang > 0 ? -1 : 1;
        api.arrow(tip[0] - dir * 6 * Math.sin(ea), tip[1] + dir * 6 * Math.cos(ea), tip[0], tip[1], api.css("--green"), 2.5);
      });
    }
    const tip = P[P.length - 1];
    api.line(tip[0], tip[1], tgt[0], tgt[1], api.css("--amber"), 1.5, [5, 4]);
    api.circle(tgt[0], tgt[1], 6, api.css("--red"));
    if (ruler) api.label(api.T("记号", "mark"), tgt[0] + 9, tgt[1] - 10, api.css("--red"), 13);
    else api.label(api.T("目标", "target"), tgt[0] + 9, tgt[1] - 10, api.css("--red"), 13);
    // 误差曲线（对数坐标）
    const pts = s.hist.map((v, i) => [i, Math.log10(Math.max(v, 1e-12))]);
    api.plot(w * 0.62, h * 0.06, w * 0.34, h * 0.28, [{ pts, color: api.css("--accent") }],
             { xmin: 0, xmax: Math.max(20, s.hist.length), ymin: -8, ymax: 0, xlabel: api.T("迭代次数 k", "iteration k"), ylabel: "log₁₀ ‖e‖" });
  },
});
