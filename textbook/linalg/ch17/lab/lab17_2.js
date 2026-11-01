// 实验 17.2 无差拍控制与凯莱–哈密顿定理（配 17.2 节）。位置轴 m ẍ = u，每 T = 10 ms 采样、零阶保持：
// A = [[1, T], [0, 1]]，B = [T²/2, T]ᵀ/m。反馈 u = −(k₁x + k₂v)，用无量纲增益 g₁ = k₁T²/m₀、g₂ = k₂T/m₀（m₀ 为设计质量）。
// 实际质量 m = m₀(1 + δ)，闭环 A_cl = A − B K，特征多项式 λ² + c₁λ + c₀，c₁ = g₁'/2 + g₂' − 2，c₀ = g₁'/2 − g₂' + 1，g' = g/(1 + δ)。
// 无差拍：c₁ = c₀ = 0 ⇔ g₁ = 1、g₂ = 1.5（δ = 0），由凯莱–哈密顿 A_cl² = O，任何初始误差两步归零。
WQ.lab({
  title: ["实验 17.2 无差拍控制与凯莱–哈密顿定理", "Lab 17.2 Deadbeat control and the Cayley–Hamilton theorem"],
  goal: ["调节数字位置控制器的两个增益，使闭环特征多项式成为 λ²，验证 A_cl² = O、误差两步归零；观察重特征值何时形成若尔当块；再加入质量误差，看无差拍对模型误差有多敏感。",
         "Tune the two gains of a digital position controller so the closed-loop characteristic polynomial becomes λ²; check A_cl² = O and that the error vanishes in two steps; see when a repeated eigenvalue forms a Jordan block; then add a mass error and see how sensitive deadbeat control is."],
  scenes: [
    { id: "axis", robot: true, name: ["数控位置轴", "Digital position axis"],
      problem: { title: ["能不能两拍就停准？", "Can the axis settle in exactly two samples?"],
                 text: ["拾放机器人的直线轴每 10 ms 采样一次。连续系统只能无限趋近目标，离散系统却可以在有限步内精确到达：只要闭环矩阵是幂零的。代价是：它对模型误差很敏感。",
                        "A pick-and-place linear axis samples every 10 ms. A continuous system only approaches its target, but a sampled one can reach it exactly in finitely many steps if the closed-loop matrix is nilpotent. The price is sensitivity to model error."] } },
  ],
  params: [
    { id: "g1", name: ["无量纲增益 g₁ = k₁T²/m₀", "Gain g₁ = k₁T²/m₀"], min: 0, max: 2, step: 0.01, value: 0.5, digits: 2 },
    { id: "g2", name: ["无量纲增益 g₂ = k₂T/m₀", "Gain g₂ = k₂T/m₀"], min: 0, max: 2.5, step: 0.01, value: 1.0, digits: 2 },
    { id: "d", name: ["实际质量误差 δ", "Actual mass error δ"], min: -10, max: 10, step: 1, value: 0, unit: "%", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["从 10 mm 误差开始", "Start from a 10 mm error"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "db", robot: true, text: ["δ = 0 时调出无差拍：特征多项式的两个系数都为 0，误差两步归零。", "With δ = 0 achieve deadbeat: both coefficients of the characteristic polynomial zero, error gone in two steps."],
      demo: { scene: "axis", set: { g1: 1, g2: 1.5, d: 0 }, press: ["start"], wait: 1 } },
    { id: "jordan", robot: true, text: ["δ = 0 时调出二重实特征值 λ（0.3 ≤ λ ≤ 0.7）。此时 A_cl 能对角化吗？读出最小多项式。", "With δ = 0 make a double real eigenvalue λ with 0.3 ≤ λ ≤ 0.7. Is A_cl diagonalizable? Read the minimal polynomial."],
      demo: { scene: "axis", set: { g1: 0.36, g2: 1.02, d: 0 }, press: ["start"], wait: 1 } },
    { id: "err", robot: true, text: ["保持无差拍增益，把实际质量改大 5%。特征值离原点多远？误差还两步归零吗？", "Keep the deadbeat gains and make the real mass 5% larger. How far are the eigenvalues from the origin? Is the error still gone in two steps?"],
      demo: { scene: "axis", set: { g1: 1, g2: 1.5, d: 5 }, press: ["start"], wait: 1 } },
    { id: "fix", robot: true, text: ["δ = 5% 时重新调增益，恢复无差拍（两个系数的绝对值都小于 0.01）。", "With δ = 5% retune the gains to recover deadbeat (both coefficients below 0.01 in magnitude)."],
      demo: { scene: "axis", set: { g1: 1.05, g2: 1.58, d: 5 }, press: ["start"], wait: 1 } },
  ],
  think: ["无差拍时 A_cl ≠ O，但 A_cl² = O。用凯莱–哈密顿定理解释；为什么 A_cl 的最小多项式是 λ² 而不是 λ？", "At deadbeat A_cl ≠ O yet A_cl² = O. Explain with the Cayley–Hamilton theorem; why is the minimal polynomial λ² and not λ?"],

  T: 0.01,
  sys(api) {
    const T = this.T, f = 1 / (1 + api.p.d / 100), g1 = api.p.g1 * f, g2 = api.p.g2 * f;
    // u = −(k₁x + k₂v)，k₁ = g₁m₀/T²，k₂ = g₂m₀/T；B/m = [T²/2, T]/m₀ · f
    const A = [[1 - g1 / 2, T - g2 * T / 2], [-g1 / T, 1 - g2]];
    const c1 = g1 / 2 + g2 - 2, c0 = g1 / 2 - g2 + 1, disc = c1 * c1 - 4 * c0;
    let ev;
    if (disc >= 0) { const r = Math.sqrt(disc); ev = [{ re: (-c1 - r) / 2, im: 0 }, { re: (-c1 + r) / 2, im: 0 }]; }
    else { const r = Math.sqrt(-disc) / 2; ev = [{ re: -c1 / 2, im: -r }, { re: -c1 / 2, im: r }]; }
    const A2 = [[A[0][0] * A[0][0] + A[0][1] * A[1][0], A[0][0] * A[0][1] + A[0][1] * A[1][1]], [A[1][0] * A[0][0] + A[1][1] * A[1][0], A[1][0] * A[0][1] + A[1][1] * A[1][1]]];
    return { A, c1, c0, disc, ev, A2 };
  },
  steps(S, n) { let x = [0.01, 0]; const out = [x]; for (let k = 0; k < n; k++) { x = [S.A[0][0] * x[0] + S.A[0][1] * x[1], S.A[1][0] * x[0] + S.A[1][1] * x[1]]; out.push(x); } return out; },
  reset(api, s) { s.k = 13; },
  start(api, s) { s.k = 0; },
  update(dt, api, s) { s.k = Math.min(13, Math.floor(api.t / 0.25)); if (s.k >= 13) api.stop(); },
  readouts(api, s) {
    const S = this.sys(api), f = api.fmt, rho = Math.max(...S.ev.map((z) => Math.hypot(z.re, z.im)));
    const rep = Math.abs(S.disc) < 2e-4, scalar = Math.abs(S.A[0][1]) < 1e-12 && Math.abs(S.A[1][0]) < 1e-12;
    const mp = rep ? (scalar ? "λ − " + f(S.ev[0].re, 3) : "(λ − " + f(S.ev[0].re, 3) + ")²") : api.T("等于特征多项式（两个不同的根）", "equals the characteristic polynomial (distinct roots)");
    if (api.p.d === 0 && Math.abs(S.c1) < 1e-6 && Math.abs(S.c0) < 1e-6) api.done("db");
    if (api.p.d === 0 && rep && S.ev[0].re >= 0.3 && S.ev[0].re <= 0.7) api.done("jordan");
    if (api.p.d >= 5 && Math.abs(api.p.g1 - 1) < 1e-9 && Math.abs(api.p.g2 - 1.5) < 1e-9) api.done("err");
    if (api.p.d === 5 && Math.abs(S.c1) < 0.01 && Math.abs(S.c0) < 0.01) api.done("fix");
    const ev = S.ev.map((z) => Math.abs(z.im) < 1e-12 ? f(z.re, 4) : f(z.re, 4) + (z.im > 0 ? " + " : " − ") + f(Math.abs(z.im), 4) + "i").join(", ");
    const xs = this.steps(S, 4);
    return [[["闭环矩阵 A_cl", "Closed-loop A_cl"], "[[" + f(S.A[0][0], 4) + ", " + f(S.A[0][1], 5) + "], [" + f(S.A[1][0], 2) + ", " + f(S.A[1][1], 4) + "]]"],
            [["特征多项式 λ² + c₁λ + c₀", "Characteristic polynomial λ² + c₁λ + c₀"], "c₁ = " + f(S.c1, 4) + ", c₀ = " + f(S.c0, 4)],
            [["特征值；最大模", "Eigenvalues; largest modulus"], ev + "；" + f(rho, 4)],
            [["A_cl² 的最大元素", "Largest entry of A_cl²"], f(Math.max(...S.A2.flat().map(Math.abs)), 6)],
            [["最小多项式", "Minimal polynomial"], mp],
            [["结构", "Structure"], rep ? (scalar ? api.T("数量矩阵", "scalar matrix") : api.T("二重特征值、只有一个特征向量：若尔当块", "double eigenvalue, one eigenvector: a Jordan block")) : api.T("两个不同的特征值：可对角化", "two distinct eigenvalues: diagonalizable")],
            [["误差 x₀…x₄ / mm", "Errors x₀…x₄ / mm"], xs.map((x) => f(1000 * x[0], 3)).join(", ")]];
  },
  draw(api, s) {
    const S = this.sys(api), { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink");
    // left: errors per step (stems), 0…12, zoomable scale
    const x0 = 40, x1 = w * 0.6, ym = h * 0.5, xs = this.steps(S, 12), kmax = s.k ?? 13;
    const amp = 10;
    api.line(x0, ym, x1, ym, mu, 1); api.line(x0, 20, x0, h - 20, mu, 1);
    xs.forEach((x, k) => {
      if (k > kmax) return;
      const X = x0 + (x1 - x0) * k / 12, Y = ym - (ym - 30) * Math.max(-1.2, Math.min(1.2, 1000 * x[0] / amp));
      api.line(X, ym, X, Y, api.css("--blue"), 2); api.circle(X, Y, 5, api.css("--blue"));
    });
    api.label(api.T("位置误差（mm，满量程 ±10）随采样步 k = 0…12", "position error (mm, full scale ±10) per step k = 0…12"), x0, 16, mu, 11);
    // right: eigenvalues in the unit disk
    const cx = (x1 + w) / 2 + 10, cy = h / 2, R = Math.min(w - x1 - 40, h - 60) / 2;
    api.circle(cx, cy, R, null, mu); api.line(cx - R - 8, cy, cx + R + 8, cy, mu, 1); api.line(cx, cy - R - 8, cx, cy + R + 8, mu, 1);
    S.ev.forEach((z) => api.circle(cx + R * Math.max(-1.3, Math.min(1.3, z.re)), cy - R * Math.max(-1.3, Math.min(1.3, z.im)), 7, api.css("--red")));
    api.label(api.T("闭环特征值与单位圆", "closed-loop eigenvalues and the unit circle"), cx - R, cy - R - 14, mu, 11);
  },
});
