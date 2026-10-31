// 实验 15.6 直立两连杆臂的稳定性（配 15.6.3 节）。参数与 code/_arm2m.py 相同：l = 0.4/0.3 m，m = 2/1 kg，均匀细杆，
// 角度从竖直方向量起（θ₂ 为相对角），关节扭簧 k₁、k₂，末端可挂负载 mp（质点）。θ = 0 处势能的黑塞矩阵 H = diag(k₁, k₂) − G，
// G = [[a + b, b], [b, b]]，a = (m₁c₁ + (m₂ + mp)l₁)g，b = (m₂c₂ + mp·l₂)g。“轻推一下”：从 θ = (3°, 3°) 静止释放，
// 按完整的非线性方程 M(θ)θ̈ + C(θ, θ̇)θ̇ + ∇V(θ) + cθ̇ = 0 积分（四阶龙格–库塔，阻尼 c = 0.06 N·m·s）。
WQ.lab({
  title: ["实验 15.6 直立两连杆臂的稳定性", "Lab 15.6 Stability of an upright two-link arm"],
  goal: ["调节两个关节扭簧的刚度和末端负载，看势能的黑塞矩阵何时正定；轻推一下，验证“黑塞矩阵正定 ⇔ 直立稳定”，体会对角元都正为什么不够。",
         "Tune the two joint springs and the tip load, see when the Hessian of the potential energy is positive definite, give the arm a nudge and check that a positive definite Hessian means a stable upright pose, and why a positive diagonal is not enough."],
  scenes: [
    { id: "arm", robot: true, name: ["直立的两连杆臂", "Upright two-link arm"],
      problem: { title: ["扭簧能撑住直立的手臂吗？", "Can the springs hold the arm upright?"],
                 text: ["两连杆臂竖直向上，断电时只靠关节扭簧保持直立。重力总想让它倒下，相当于一个“负刚度”。分别检查每个关节的扭簧够不够，并不能保证整条臂不倒。",
                        "A two-link arm stands upright and, with the power off, only the joint springs hold it. Gravity acts like a negative stiffness. Checking each joint's spring on its own does not guarantee that the whole arm stays up."] } },
  ],
  params: [
    { id: "k1", name: ["关节 1 扭簧 k₁", "Joint 1 spring k₁"], min: 0, max: 40, step: 0.1, value: 20, unit: "N·m/rad", digits: 1 },
    { id: "k2", name: ["关节 2 扭簧 k₂", "Joint 2 spring k₂"], min: 0, max: 15, step: 0.1, value: 5, unit: "N·m/rad", digits: 1 },
    { id: "mp", name: ["末端负载 mp", "Tip load mp"], min: 0, max: 1, step: 0.1, value: 0, unit: "kg", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["轻推一下", "Give it a nudge"], primary: true }, { id: "reset", name: ["扶正", "Set upright"] }],
  tasks: [
    { id: "stable", robot: true, text: ["取 k₁ = 20、k₂ = 5、无负载，轻推一下，确认臂摆几下后回到直立。", "With k₁ = 20, k₂ = 5 and no load, nudge the arm and check that it swings back to upright."],
      demo: { scene: "arm", set: { k1: 20, k2: 5, mp: 0 }, press: ["start"], wait: 6 } },
    { id: "diag", robot: true, text: ["找一组 k₁、k₂，使 H 的两个对角元都为正，但 H 不正定。轻推一下会怎样？", "Find k₁, k₂ with both diagonal entries of H positive but H not positive definite. What happens after a nudge?"],
      demo: { scene: "arm", set: { k1: 9.5, k2: 5, mp: 0 }, press: ["start"], wait: 5 } },
    { id: "crit", robot: true, text: ["固定 k₂ = 5、无负载，找出使直立稳定的最小 k₁（误差 0.3 以内），与式 (15.6.4) 比较。", "With k₂ = 5 and no load, find the smallest k₁ that keeps the arm upright (within 0.3) and compare with (15.6.4)."],
      demo: { scene: "arm", set: { k1: 10, k2: 5, mp: 0 }, press: [] } },
    { id: "load", robot: true, text: ["挂上 0.5 kg 负载，把 k₁ 降到 15：直立还稳定吗？只调 k₂，使它重新稳定。", "Hang a 0.5 kg load and lower k₁ to 15. Is the arm still stable? Adjust only k₂ to make it stable again."],
      demo: { scene: "arm", set: { k1: 15, k2: 8, mp: 0.5 }, press: ["start"], wait: 6 } },
  ],
  think: ["实验中“临界”时的 k₁ 比单看关节 1 时（k₁ > G₁₁）要大。用配方（15.2.6 节）解释多出来的部分是什么。", "At the critical point k₁ is larger than the single-joint estimate k₁ > G₁₁. Use completing the square (Section 15.2.6) to explain the extra amount."],

  L1: 0.4, L2: 0.3, M1: 2, M2: 1, g: 9.81, c: 0.06,
  model(api) {
    const { L1, L2, M1, M2, g } = this, mp = api.p.mp, c1 = L1 / 2, c2 = L2 / 2;
    const a = (M1 * c1 + (M2 + mp) * L1) * g, b = (M2 * c2 + mp * L2) * g;
    const H = [[api.p.k1 - a - b, -b], [-b, api.p.k2 - b]];
    return { a, b, H, mp, c1, c2 };
  },
  mass(th2, mp) {
    const { L1, L2, M1, M2 } = this, c1 = L1 / 2, c2 = L2 / 2, I1 = M1 * L1 * L1 / 12, I2 = M2 * L2 * L2 / 12, cq = Math.cos(th2);
    const m11 = I1 + I2 + M1 * c1 * c1 + M2 * (L1 * L1 + c2 * c2 + 2 * L1 * c2 * cq) + mp * (L1 * L1 + L2 * L2 + 2 * L1 * L2 * cq);
    const m12 = I2 + M2 * (c2 * c2 + L1 * c2 * cq) + mp * (L2 * L2 + L1 * L2 * cq);
    const m22 = I2 + M2 * c2 * c2 + mp * L2 * L2;
    return [[m11, m12], [m12, m22]];
  },
  // state y = [θ₁, θ₂, ω₁, ω₂]
  deriv(api, y) {
    const md = this.model(api), [t1, t2, w1, w2] = y, s12 = Math.sin(t1 + t2);
    const gV = [api.p.k1 * t1 - md.a * Math.sin(t1) - md.b * s12, api.p.k2 * t2 - md.b * s12];
    const h = this.L1 * (this.M2 * md.c2 + md.mp * this.L2) * Math.sin(t2);
    const cor = [-h * (2 * w1 * w2 + w2 * w2), h * w1 * w1];
    const f = [-gV[0] - cor[0] - this.c * w1, -gV[1] - cor[1] - this.c * w2];
    const M = this.mass(t2, md.mp), det = M[0][0] * M[1][1] - M[0][1] * M[0][1];
    return [w1, w2, (M[1][1] * f[0] - M[0][1] * f[1]) / det, (-M[0][1] * f[0] + M[0][0] * f[1]) / det];
  },
  eig(H) {
    const a = H[0][0], b = H[0][1], d = H[1][1], m = (a + d) / 2, r = Math.hypot((a - d) / 2, b);
    const l1 = m - r, l2 = m + r;
    let v = Math.abs(b) > 1e-12 ? [b, l1 - a] : (a <= d ? [1, 0] : [0, 1]);
    const n = Math.hypot(v[0], v[1]); v = [v[0] / n, v[1] / n];
    return { l1, l2, v1: v, v2: [-v[1], v[0]] };
  },
  reset(api, s) {
    const md = this.model(api);
    s.md = md; s.e = this.eig(md.H);
    s.y = [0, 0, 0, 0]; s.trace = []; s.maxlate = 0; s.fell = false;
  },
  start(api, s) {
    const d = Math.PI / 180;
    s.y = [3 * d, 3 * d, 0, 0]; s.trace = [[s.y[0], s.y[1]]];
  },
  update(dt, api, s) {
    const n = 10, h = dt / n;
    for (let i = 0; i < n; i++) {
      const y = s.y, k1 = this.deriv(api, y);
      const k2 = this.deriv(api, y.map((v, j) => v + h / 2 * k1[j]));
      const k3 = this.deriv(api, y.map((v, j) => v + h / 2 * k2[j]));
      const k4 = this.deriv(api, y.map((v, j) => v + h * k3[j]));
      s.y = y.map((v, j) => v + h / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]));
    }
    s.trace.push([s.y[0], s.y[1]]); if (s.trace.length > 600) s.trace.shift();
    const amp = Math.max(Math.abs(s.y[0]), Math.abs(s.y[1])) * 180 / Math.PI;
    if (api.t > 4) s.maxlate = Math.max(s.maxlate, amp);
    if (amp > 30) s.fell = true;
    if (Math.abs(s.y[0]) > 1.6 || api.t > 9) api.stop();
  },
  readouts(api, s) {
    if (!s.y) return [];
    s.md = this.model(api); s.e = this.eig(s.md.H);      // 运行中改了参数也要跟上
    const f = api.fmt, H = s.md.H, d2 = H[0][0] !== 0 ? (H[0][0] * H[1][1] - H[0][1] * H[0][1]) / H[0][0] : NaN;
    const det = H[0][0] * H[1][1] - H[0][1] * H[0][1], pd = s.e.l1 > 0;
    const p = api.p, k1c = s.md.a + s.md.b + s.md.b * s.md.b / (p.k2 - s.md.b);
    if (pd && p.mp === 0 && Math.abs(p.k1 - 20) < 1e-9 && Math.abs(p.k2 - 5) < 1e-9 && api.t > 4 && s.maxlate < 3.5 && !s.fell) api.done("stable");
    if (H[0][0] > 0 && H[1][1] > 0 && !pd) api.done("diag");
    if (Math.abs(p.k2 - 5) < 1e-9 && p.mp === 0 && pd && p.k1 - k1c < 0.3) api.done("crit");
    if (Math.abs(p.mp - 0.5) < 1e-9 && p.k1 <= 15 + 1e-9 && pd) api.done("load");
    const deg = 180 / Math.PI, verdict = pd ? api.T("正定：直立稳定", "positive definite: stable") : (s.e.l1 > -1e-9 ? api.T("半正定：临界", "semidefinite: borderline") : api.T("不正定：直立不稳定", "not positive definite: unstable"));
    return [[["黑塞矩阵 H / N·m·rad⁻¹", "Hessian H / N·m·rad⁻¹"], "[[" + f(H[0][0], 2) + ", " + f(H[0][1], 2) + "], [" + f(H[1][0], 2) + ", " + f(H[1][1], 2) + "]]"],
            [["特征值", "Eigenvalues"], f(s.e.l1, 3) + ", " + f(s.e.l2, 3)],
            [["主元 d₁、d₂", "Pivots d₁, d₂"], f(H[0][0], 3) + ", " + f(d2, 3)],
            [["顺序主子式 H₁₁、det H", "Leading minors H₁₁, det H"], f(H[0][0], 3) + ", " + f(det, 3)],
            [["判断", "Verdict"], verdict],
            [["k₂ 不变时 k₁ 的临界值", "Critical k₁ for this k₂"], p.k2 > s.md.b ? f(k1c, 2) : api.T("k₂ 太小，任何 k₁ 都不够", "k₂ too small, no k₁ suffices")],
            [["当前角度 θ₁、θ₂", "Angles θ₁, θ₂"], f(s.y[0] * deg, 1) + "°, " + f(s.y[1] * deg, 1) + "°"]];
  },
  draw(api, s) {
    if (!s.md) return;
    const { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink"), ctx = api.ctx;
    // left: the arm
    const bx = w * 0.22, by = h * 0.86, sc = Math.min(w * 0.38, h * 0.95) / 0.85;
    api.line(bx - 50, by, bx + 50, by, ink, 3);
    api.line(bx, by, bx, by - sc * 0.75, mu, 1, [4, 4]);
    const [t1, t2] = s.y, p1 = [bx + sc * this.L1 * Math.sin(t1), by - sc * this.L1 * Math.cos(t1)];
    const p2 = [p1[0] + sc * this.L2 * Math.sin(t1 + t2), p1[1] - sc * this.L2 * Math.cos(t1 + t2)];
    api.line(bx, by, p1[0], p1[1], api.css("--blue"), 12); api.line(p1[0], p1[1], p2[0], p2[1], api.css("--green"), 9);
    api.circle(bx, by, 7, ink); api.circle(p1[0], p1[1], 6, ink);
    if (s.md.mp > 0) api.circle(p2[0], p2[1], 6 + 8 * s.md.mp, api.css("--amber"));
    api.label(api.T("轻推后", "after a nudge"), bx - 60, 22, mu, 12);
    if (s.fell) api.label(api.T("倒下了", "it falls"), bx - 30, 42, api.css("--red"), 14);
    // right: ½θᵀHθ over θ ∈ [−30°, 30°]²
    const S = Math.min(w * 0.5, h * 0.86), x0 = w * 0.46, y0 = (h - S) / 2, R = 30 * Math.PI / 180, N = 48, H = s.md.H;
    const q = (a, b) => H[0][0] * a * a + 2 * H[0][1] * a * b + H[1][1] * b * b;
    let qmax = 1e-9;
    for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) { const a = -R + 2 * R * (i + 0.5) / N, b = -R + 2 * R * (j + 0.5) / N; qmax = Math.max(qmax, Math.abs(q(a, b))); }
    for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
      const a = -R + 2 * R * (i + 0.5) / N, b = R - 2 * R * (j + 0.5) / N, v = q(a, b) / qmax;
      ctx.globalAlpha = 0.12 + 0.55 * Math.min(1, Math.abs(v));
      api.rect(x0 + S * i / N, y0 + S * j / N, S / N + 0.5, S / N + 0.5, v >= 0 ? api.css("--blue") : api.css("--red"));
    }
    ctx.globalAlpha = 1;
    const X = (a) => x0 + S * (a + R) / (2 * R), Y = (b) => y0 + S * (R - b) / (2 * R);
    api.line(X(-R), Y(0), X(R), Y(0), mu, 1); api.line(X(0), Y(-R), X(0), Y(R), mu, 1);
    [[s.e.v1, s.e.l1], [s.e.v2, s.e.l2]].forEach(([v, l]) => {
      api.arrow(X(0), Y(0), X(0.8 * R * v[0]), Y(0.8 * R * v[1]), l > 0 ? api.css("--green") : api.css("--red"), 2.5);
      api.label("λ = " + api.fmt(l, 2), X(0.85 * R * v[0]) + 4, Y(0.85 * R * v[1]), l > 0 ? api.css("--green") : api.css("--red"), 12);
    });
    if (s.trace.length > 1) {
      ctx.beginPath(); s.trace.forEach(([a, b], i) => { const cl = (z) => Math.max(-R, Math.min(R, z)); i ? ctx.lineTo(X(cl(a)), Y(cl(b))) : ctx.moveTo(X(cl(a)), Y(cl(b))); });
      ctx.strokeStyle = api.css("--amber"); ctx.lineWidth = 2; ctx.stroke();
    }
    api.label(api.T("θ₁、θ₂ ∈ [−30°, 30°]：蓝 = 势能升高，红 = 势能降低；黄线 = 轨迹", "θ₁, θ₂ in [−30°, 30°]: blue = energy up, red = energy down; amber = trajectory"), x0, y0 - 6, mu, 11);
  },
});
