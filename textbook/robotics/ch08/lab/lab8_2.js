// 实验 8.2 被手拉住的机械臂（配 8.2 节）。平面 3R 臂，L = (0.425, 0.392, 0.1) m，关节扭簧刚度 k₁, k₂, k₃，自然形态 θ_c = (30°, 60°, −60°)。
// min ½(θ − θ_c)ᵀK(θ − θ_c) s.t. p(θ) = p_d（式 (8.2.12)），用拉格朗日-牛顿法（式 (8.2.10)）求解；手的力 F = −λ，扭簧力矩 τ = −K(θ − θ_c)。
// “晾衣绳”：挂钩 A(0, 2.0)、B(2.0, 2.4) m，绳长 ℓ，衣服重 G；min G·P_y s.t. |PA| + |PB| = ℓ，乘子 = 绳的拉力（算例 8.2.3）。
WQ.lab({
  title: ["实验 8.2 被手拉住的机械臂", "Lab 8.2 An arm held by a hand"],
  goal: ["用拉格朗日-牛顿法求带等式约束的最小势能问题，读出拉格朗日乘子，并验证它就是约束力。",
         "Solve an equality-constrained minimum-energy problem by the Lagrange–Newton method, read the Lagrange multipliers and check that they are the constraint forces."],
  scenes: [
    { id: "arm", robot: true, name: ["扭簧手臂", "Arm with joint springs"], hide: ["ell", "G"],
      problem: { title: ["机器人问题：手把末端拉到 p_d，手臂摆成什么形态", "Robot problem: the hand pulls the tip to p_d; what posture does the arm take?"],
                 text: ["三个关节装有扭簧。末端被固定在 p_d 后，手臂停在扭簧势能最小的形态。乘子 λ 的负值就是手的力。",
                        "Each joint has a torsion spring. With the tip held at p_d, the arm settles where the spring energy is least. Minus the multiplier λ is the hand force."] } },
    { id: "rope", name: ["晾衣绳", "Clothes line"], hide: ["px", "py", "k1", "k2", "k3"],
      problem: { title: ["生活中的例子：衣架滑到哪里", "Everyday example: where does the hanger slide to?"],
                 text: ["衣架停在绳长约束下势能最小的位置。拉格朗日乘子就是绳的拉力。",
                        "The hanger stops at the lowest point the rope allows. The Lagrange multiplier is the rope tension."] } },
  ],
  params: [
    { id: "px", name: ["目标 p_d 的 x", "Target p_d, x"], min: 0.3, max: 0.65, step: 0.01, value: 0.55, unit: "m", digits: 2 },
    { id: "py", name: ["目标 p_d 的 y", "Target p_d, y"], min: 0.2, max: 0.6, step: 0.01, value: 0.45, unit: "m", digits: 2 },
    { id: "k1", name: ["扭簧刚度 k₁", "Spring stiffness k₁"], min: 5, max: 80, step: 1, value: 20, unit: "N·m/rad", digits: 0 },
    { id: "k2", name: ["扭簧刚度 k₂", "Spring stiffness k₂"], min: 5, max: 80, step: 1, value: 10, unit: "N·m/rad", digits: 0 },
    { id: "k3", name: ["扭簧刚度 k₃", "Spring stiffness k₃"], min: 2, max: 50, step: 1, value: 5, unit: "N·m/rad", digits: 0 },
    { id: "ell", name: ["绳长 ℓ", "Rope length ℓ"], min: 2.1, max: 4, step: 0.05, value: 2.6, unit: "m", digits: 2 },
    { id: "G", name: ["衣服重 G", "Weight G"], min: 5, max: 60, step: 1, value: 20, unit: "N", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["求解", "Solve"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["用默认参数求解（算例 8.2.2），读出手的力 F。", "Solve with the default settings (Example 8.2.2) and read the hand force F."],
      demo: { scene: "arm", set: { px: 0.55, py: 0.45, k1: 20, k2: 10, k3: 5 }, press: ["start"], wait: 5 } },
    { id: "stiff", robot: true, text: ["把关节 1 的刚度加大到 60 N·m/rad 以上再求解，看关节 1 转得是否更少。", "Raise joint 1's stiffness to 60 N·m/rad or more and solve: does joint 1 turn less?"],
      demo: { scene: "arm", set: { px: 0.55, py: 0.45, k1: 60, k2: 10, k3: 5 }, press: ["start"], wait: 5 } },
    { id: "move", robot: true, text: ["把目标点挪动 5 cm 以上再求解，验证 τ + JᵀF = 0。", "Move the target by 5 cm or more, solve, and check τ + JᵀF = 0."],
      demo: { scene: "arm", set: { px: 0.45, py: 0.55, k1: 20, k2: 10, k3: 5 }, press: ["start"], wait: 5 } },
    { id: "rope", text: ["在“晾衣绳”中调绳长和重量，使绳的拉力超过 30 N。", "In “Clothes line” adjust the length and the weight so that the tension exceeds 30 N."],
      demo: { scene: "rope", set: { ell: 2.1, G: 20 }, press: [], wait: 1 } },
  ],
  think: ["手的力为什么不与末端的位移同向？在默认参数下，竖直向下压末端，末端会往哪边偏？",
          "Why is the hand force not along the tip displacement? With the default settings, if you press the tip straight down, which way does it also move?"],

  L: [0.425, 0.392, 0.1], TC: [30, 60, -60].map((d) => d * Math.PI / 180),
  pts(t) { const p = [[0, 0]]; let a = 0; t.forEach((q, i) => { a += q; const l = p[p.length - 1]; p.push([l[0] + this.L[i] * Math.cos(a), l[1] + this.L[i] * Math.sin(a)]); }); return p; },
  jac(t) { const p = this.pts(t), e = p[3]; return [[0, 1, 2].map((i) => -(e[1] - p[i][1])), [0, 1, 2].map((i) => e[0] - p[i][0])]; },
  solve(M, b) {                                           // 高斯消元（选主元）
    const n = b.length, A = M.map((r, i) => [...r, b[i]]);
    for (let i = 0; i < n; i++) {
      let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(A[j][i]) > Math.abs(A[p][i])) p = j;
      [A[i], A[p]] = [A[p], A[i]];
      for (let j = i + 1; j < n; j++) { const f = A[j][i] / A[i][i]; for (let k = i; k <= n; k++) A[j][k] -= f * A[i][k]; }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let s = A[i][n]; for (let k = i + 1; k < n; k++) s -= A[i][k] * x[k]; x[i] = s / A[i][i]; }
    return x;
  },
  K(api) { return [api.p.k1, api.p.k2, api.p.k3]; },
  kkt(api, t, lam) {                                       // KKT 残差：K(θ − θ_c) + Jᵀλ 与 p(θ) − p_d
    const K = this.K(api), J = this.jac(t), e = this.pts(t)[3];
    const g = [0, 1, 2].map((i) => K[i] * (t[i] - this.TC[i]) + J[0][i] * lam[0] + J[1][i] * lam[1]);
    return g.concat([e[0] - api.p.px, e[1] - api.p.py]);
  },
  newtonStep(api, s) {
    const t = s.th, lam = s.lam, K = this.K(api), J = this.jac(t), p = this.pts(t), e = p[3];
    const H = [0, 1, 2].map((i) => [0, 1, 2].map((j) => { const q = p[Math.max(i, j)];
      return (i === j ? K[i] : 0) - lam[0] * (e[0] - q[0]) - lam[1] * (e[1] - q[1]); }));
    const M = [[...H[0], J[0][0], J[1][0]], [...H[1], J[0][1], J[1][1]], [...H[2], J[0][2], J[1][2]], [...J[0], 0, 0], [...J[1], 0, 0]];
    const d = this.solve(M, this.kkt(api, t, lam).map((v) => -v));
    s.th = [t[0] + d[0], t[1] + d[1], t[2] + d[2]]; s.lam = [lam[0] + d[3], lam[1] + d[4]];
  },
  rope(api) {                                              // 解析解：两段绳与竖直方向夹角相等
    const A = [0, 2.0], B = [2.0, 2.4], sa = (B[0] - A[0]) / api.p.ell, ca = Math.sqrt(1 - sa * sa);
    // 把 B 关于过 P 的竖直线“展开”：P 的高度由 |PA| + |PB| = ℓ 与等角条件决定
    const la = (A[1] - B[1]) / (2 * ca) + api.p.ell / 2;   // 挂钩 A 一侧绳长
    const P = [A[0] + la * sa, A[1] - la * ca];
    return { A, B, P, T: api.p.G / (2 * ca), alpha: Math.asin(sa) };
  },

  reset(api, s) { s.th = this.TC.slice(); s.lam = [0, 0]; s.k = 0; s.clock = 0; s.res = []; s.done = false; },
  update(dt, api, s) {
    if (api.scene !== "arm") { api.stop(); return; }
    s.clock += dt;
    if (s.clock < 0.35) return;
    s.clock = 0;
    this.newtonStep(api, s); s.k += 1;
    const r = Math.hypot(...this.kkt(api, s.th, s.lam)); s.res.push(r);
    if (r < 1e-12 || s.k >= 25 || !isFinite(r)) { s.done = r < 1e-9; api.stop(); }
  },
  readouts(api, s) {
    const f = (x, n) => api.fmt(x, n), dg = (x) => f(x * 180 / Math.PI, 2);
    if (api.scene === "rope") {
      const r = this.rope(api);
      if (r.T > 30) api.done("rope");
      return [[["衣架位置 P", "hanger position P"], `(${f(r.P[0], 3)}, ${f(r.P[1], 3)}) m`],
              [["绳与竖直方向的夹角 α", "angle α to the vertical"], f(r.alpha * 180 / Math.PI, 1) + "°"],
              [["乘子 λ = 绳的拉力", "multiplier λ = rope tension"], f(r.T, 2) + " N"],
              [["检验 2λ cos α = G", "check 2λ cos α = G"], f(2 * r.T * Math.cos(r.alpha), 2) + " N"]];
    }
    const K = this.K(api), J = this.jac(s.th), F = [-s.lam[0], -s.lam[1]];
    const tau = [0, 1, 2].map((i) => -K[i] * (s.th[i] - this.TC[i]));
    const bal = Math.hypot(...[0, 1, 2].map((i) => tau[i] + J[0][i] * F[0] + J[1][i] * F[1]));
    if (s.done) {
      if (Math.abs(api.p.px - 0.55) < 1e-9 && Math.abs(api.p.py - 0.45) < 1e-9 && K[0] === 20 && K[1] === 10 && K[2] === 5) api.done("ex");
      if (K[0] >= 60) api.done("stiff");
      if (Math.hypot(api.p.px - 0.55, api.p.py - 0.45) >= 0.05 - 1e-9 && bal < 1e-9) api.done("move");
    }
    const rows = [[["迭代次数 k", "iteration k"], String(s.k)],
                  [["KKT 残差", "KKT residual"], s.res.length ? s.res[s.res.length - 1].toExponential(1) : "—"],
                  [["θ", "θ"], `(${dg(s.th[0])}°, ${dg(s.th[1])}°, ${dg(s.th[2])}°)`],
                  [["乘子 λ", "multiplier λ"], `(${f(s.lam[0], 3)}, ${f(s.lam[1], 3)}) N`],
                  [["手的力 F = −λ", "hand force F = −λ"], `(${f(F[0], 3)}, ${f(F[1], 3)}) N`],
                  [["扭簧力矩 τ", "spring torques τ"], `(${f(tau[0], 3)}, ${f(tau[1], 3)}, ${f(tau[2], 3)}) N·m`],
                  [["|τ + JᵀF|", "|τ + JᵀF|"], bal.toExponential(1) + " N·m"],
                  [["势能 U", "energy U"], f(0.5 * [0, 1, 2].reduce((a, i) => a + K[i] * (s.th[i] - this.TC[i]) ** 2, 0), 4) + " J"]];
    if (!s.done && s.k >= 25) rows.push([["状态", "status"], api.T("未收敛", "not converged")]);
    return rows;
  },
  draw(api, s) {
    const { w, h, ctx } = api;
    if (api.scene === "rope") {
      const r = this.rope(api), k = Math.min(w / 3.2, h / 3.0), ox = w * 0.5 - k * 1.0, oy = h * 0.12 + k * 2.6;
      const X = (p) => [ox + k * p[0], oy - k * p[1]];
      const A = X(r.A), B = X(r.B), P = X(r.P);
      api.rect(A[0] - 30, A[1] - 12, 26, 24, api.css("--muted")); api.rect(B[0] + 4, B[1] - 12, 26, 24, api.css("--muted"));
      api.line(A[0], A[1], P[0], P[1], api.css("--ink"), 2); api.line(P[0], P[1], B[0], B[1], api.css("--ink"), 2);
      api.circle(A[0], A[1], 4, api.css("--ink")); api.circle(B[0], B[1], 4, api.css("--ink"));
      api.line(P[0], P[1], P[0], P[1] + 18, api.css("--ink"), 2);
      ctx.fillStyle = api.css("--blue"); ctx.beginPath(); ctx.moveTo(P[0], P[1] + 18); ctx.lineTo(P[0] - 40, P[1] + 34); ctx.lineTo(P[0] - 34, P[1] + 90);
      ctx.lineTo(P[0] + 34, P[1] + 90); ctx.lineTo(P[0] + 40, P[1] + 34); ctx.closePath(); ctx.fill();
      const ua = [(r.A[0] - r.P[0]), (r.A[1] - r.P[1])], ub = [(r.B[0] - r.P[0]), (r.B[1] - r.P[1])];
      const na = Math.hypot(...ua), nb = Math.hypot(...ub), sc = 2.2;
      api.arrow(P[0], P[1], P[0] + sc * r.T * ua[0] / na, P[1] - sc * r.T * ua[1] / na, api.css("--red"), 2.5);
      api.arrow(P[0], P[1], P[0] + sc * r.T * ub[0] / nb, P[1] - sc * r.T * ub[1] / nb, api.css("--red"), 2.5);
      api.arrow(P[0] + 50, P[1] + 40, P[0] + 50, P[1] + 40 + sc * api.p.G, api.css("--amber"), 2.5);
      api.label("λ", P[0] + sc * r.T * ua[0] / na - 14, P[1] - sc * r.T * ua[1] / na, api.css("--red"), 14);
      api.label("G", P[0] + 58, P[1] + 50 + sc * api.p.G / 2, api.css("--amber"), 14);
      api.label("A", A[0] - 18, A[1] - 22, api.css("--ink"), 13); api.label("B", B[0] + 14, B[1] - 22, api.css("--ink"), 13);
      return;
    }
    const k = Math.min(w * 0.55, h * 0.95) / 0.95, bx = w * 0.18, by = h * 0.85;
    const X = (p) => [bx + k * p[0], by - k * p[1]];
    api.line(bx - 0.1 * k, by, bx + 0.8 * k, by, api.css("--grid"), 1);
    const pc = this.pts(this.TC).map(X);
    for (let i = 0; i < 3; i++) api.line(...pc[i], ...pc[i + 1], api.css("--muted"), 3, [6, 5]);
    const p = this.pts(s.th).map(X);
    for (let i = 0; i < 3; i++) api.line(...p[i], ...p[i + 1], api.css("--accent"), 8 - 2 * i);
    const K = this.K(api);
    p.slice(0, 3).forEach((q, i) => {
      api.circle(q[0], q[1], 6, api.css("--panel"), api.css("--ink"));
      const tau = -K[i] * (s.th[i] - this.TC[i]), a0 = Math.PI * 0.9, a1 = a0 + Math.sign(tau) * Math.min(5, 0.35 * Math.abs(tau) + 0.2);
      ctx.strokeStyle = api.css("--red"); ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(q[0], q[1], 16, -a0, -a1, tau > 0); ctx.stroke();
    });
    const D = X([api.p.px, api.p.py]);
    api.line(D[0] - 7, D[1] - 7, D[0] + 7, D[1] + 7, api.css("--red"), 2.5); api.line(D[0] - 7, D[1] + 7, D[0] + 7, D[1] - 7, api.css("--red"), 2.5);
    api.label("p_d", D[0] + 10, D[1] - 12, api.css("--red"), 13);
    if (s.k > 0) {
      const e = p[3], sc = 4;
      api.arrow(e[0], e[1], e[0] - sc * s.lam[0], e[1] + sc * s.lam[1], api.css("--amber"), 3);
      api.label("F = −λ", e[0] - sc * s.lam[0] + 8, e[1] + sc * s.lam[1] + 4, api.css("--amber"), 13);
    }
    api.label(api.T("虚线：自然形态 θ_c；红色弧线：扭簧力矩", "dashed: natural posture θ_c; red arcs: spring torques"), 12, h - 12, api.css("--muted"), 12);
  },
});
