// 实验 17.7 若尔当块的扰动（配 17.7 节）。n 阶若尔当块 J_n(λ₀) 的左下角加 ε：J_n(λ₀) + ε e_n e₁ᵀ。
// 特征多项式为 (λ − λ₀)ⁿ − ε，特征值 λ₀ + ε^{1/n}·e^{2πik/n}（k = 0, …, n − 1，ε < 0 时再转 π/n），这里按公式精确计算。
WQ.lab({
  title: ["实验 17.7 若尔当块的扰动", "Lab 17.7 Perturbing a Jordan block"],
  goal: ["给若尔当块加一个极小的扰动，看重特征值怎样散开成一个圆、散开多远；体会为什么数值计算不用若尔当形，以及无差拍控制为什么怕模型误差。",
         "Add a tiny perturbation to a Jordan block and watch the repeated eigenvalue burst into a circle; see how far it moves, why numerical work avoids the Jordan form, and why deadbeat control fears model error."],
  scenes: [
    { id: "jordan", robot: true, name: ["若尔当块 + ε", "Jordan block + ε"],
      problem: { title: ["n 步无差拍控制有多“脆”？", "How fragile is n-step deadbeat control?"],
                 text: ["n 阶积分链的无差拍控制器让闭环特征多项式成为 λⁿ，闭环矩阵相似于 n 阶若尔当块 J_n(0)。模型稍有偏差，特征多项式大致相当于变成 λⁿ − ε，n 重特征值 0 立刻散开。",
                        "A deadbeat controller for an n-integrator chain makes the closed-loop polynomial λⁿ, so the closed loop is similar to the Jordan block J_n(0). A slight model error roughly turns the polynomial into λⁿ − ε and the n-fold eigenvalue 0 bursts apart."] } },
  ],
  params: [
    { id: "n", name: ["块的阶数 n", "Block size n"], min: 1, max: 10, step: 1, value: 4, digits: 0 },
    { id: "le", name: ["扰动 log₁₀ ε", "Perturbation log₁₀ ε"], min: -16, max: 0, step: 0.5, value: -8, digits: 1 },
  ],
  buttons: [{ id: "start", name: ["让 ε 从 10⁻¹⁶ 增大到 1", "Sweep ε from 10⁻¹⁶ to 1"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "n2", robot: true, text: ["n = 2、ε = 10⁻⁸：特征值移动了多少？是 ε 的多少倍？", "n = 2, ε = 10⁻⁸: how far do the eigenvalues move? How many times ε is that?"],
      demo: { scene: "jordan", set: { n: 2, le: -8 }, press: [] } },
    { id: "n8", robot: true, text: ["n = 8、ε = 10⁻¹⁶（双精度的舍入误差）：特征值离开原点多远？", "n = 8, ε = 10⁻¹⁶ (double-precision rounding): how far from the origin are the eigenvalues?"],
      demo: { scene: "jordan", set: { n: 8, le: -16 }, press: [] } },
    { id: "r01", robot: true, text: ["n = 4 时，ε 要多大，特征值才移动 0.1？", "For n = 4, how large must ε be to move the eigenvalues by 0.1?"],
      demo: { scene: "jordan", set: { n: 4, le: -4 }, press: [] } },
    { id: "n1", robot: true, text: ["n = 1（可对角化的情形）时，特征值移动多少？与 ε 比较。", "For n = 1 (the diagonalizable case) how far does the eigenvalue move? Compare with ε."],
      demo: { scene: "jordan", set: { n: 1, le: -8 }, press: [] } },
  ],
  think: ["双精度数的舍入误差约 10⁻¹⁶。一个特征值有 n 阶若尔当块时，计算出的特征值大约只能有几位有效数字？（提示：16/n。）", "Double-precision rounding is about 10⁻¹⁶. With an n×n Jordan block, roughly how many correct digits can a computed eigenvalue have? (Hint: 16/n.)"],

  ev(n, eps) { const r = Math.pow(eps, 1 / n); return Array.from({ length: n }, (_, k) => ({ re: r * Math.cos(2 * Math.PI * k / n), im: r * Math.sin(2 * Math.PI * k / n) })); },
  reset(api, s) { s.sweep = null; },
  start(api, s) { s.sweep = -16; },
  update(dt, api, s) { s.sweep = Math.min(0, -16 + 4 * api.t); if (s.sweep >= 0) api.stop(); },
  le(api, s) { return s.sweep !== null && s.sweep !== undefined ? s.sweep : api.p.le; },
  readouts(api, s) {
    const n = api.p.n, le = this.le(api, s), eps = Math.pow(10, le), r = Math.pow(eps, 1 / n), f = api.fmt;
    const exp = (x) => { const e = Math.floor(Math.log10(x) + 1e-9); return f(x / Math.pow(10, e), 2) + "×10^" + e; };
    if (s.sweep === null || s.sweep === undefined) {
      if (n === 2 && le === -8) api.done("n2");
      if (n === 8 && le === -16) api.done("n8");
      if (n === 4 && Math.abs(r - 0.1) < 1e-9) api.done("r01");
      if (n === 1) api.done("n1");
    }
    return [[["矩阵", "Matrix"], "J" + n + "(0) + ε e" + n + "e₁ᵀ"],
            [["扰动 ε", "Perturbation ε"], exp(eps)],
            [["特征多项式", "Characteristic polynomial"], "λ^" + n + " − ε"],
            [["特征值的模 |λ| = ε^(1/n)", "Eigenvalue modulus |λ| = ε^(1/n)"], exp(r)],
            [["放大倍数 |λ| / ε", "Amplification |λ| / ε"], exp(r / eps)],
            [["大约可信的有效数字", "Roughly trustworthy digits"], n === 1 ? api.T("扰动只改变 ε 量级", "shift only of order ε") : f(Math.max(0, -le / n), 1) + api.T(" 位（若 ε 是舍入误差）", " digits (if ε is rounding)")]];
  },
  draw(api, s) {
    const n = api.p.n, le = this.le(api, s), eps = Math.pow(10, le), { w, h } = api, mu = api.css("--muted"), ctx = api.ctx;
    // left: complex plane, scale chosen so radius 1 fits; log-radius rings
    const cx = w * 0.3, cy = h / 2, R = Math.min(w * 0.27, h * 0.45);
    api.line(cx - R - 10, cy, cx + R + 10, cy, mu, 1); api.line(cx, cy - R - 10, cx, cy + R + 10, mu, 1);
    // log-polar: plot radius ρ = (16 + log₁₀|λ|)/16 so that |λ| = 10⁻¹⁶ … 1 maps to 0 … R
    const rho = (r) => Math.max(0, (16 + Math.log10(r)) / 16) * R;
    for (let k = -16; k <= 0; k += 4) { api.circle(cx, cy, rho(Math.pow(10, k)) || 0.5, null, mu); api.label("10^" + k, cx + rho(Math.pow(10, k)) + 3, cy - 4, mu, 10); }
    const r = Math.pow(eps, 1 / n);
    this.ev(n, eps).forEach((z) => { const a = Math.atan2(z.im, z.re); api.circle(cx + rho(r) * Math.cos(a), cy - rho(r) * Math.sin(a), 7, api.css("--red")); });
    api.label(api.T("特征值（对数半径：圆环为 10⁻¹⁶、10⁻¹²…1）", "eigenvalues (log radius: rings at 10⁻¹⁶, 10⁻¹² … 1)"), 10, 16, mu, 11);
    // right: |λ| versus ε for n = 1, 2, 4, 8 and the current n (log-log)
    const x0 = w * 0.62, x1 = w - 20, y0 = 30, y1 = h - 30;
    const X = (le_) => x0 + (x1 - x0) * (le_ + 16) / 16, Y = (lr) => y1 - (y1 - y0) * (lr + 16) / 16;
    api.rect(x0, y0, x1 - x0, y1 - y0, null, mu);
    [1, 2, 4, 8].forEach((m, i) => {
      const col = m === n ? api.css("--red") : mu;
      api.line(X(-16), Y(-16 / m), X(0), Y(0), col, m === n ? 2.5 : 1);
      api.label("n=" + m, X(-16) + 4, Y(-16 / m) - 4, col, 10);
    });
    if (![1, 2, 4, 8].includes(n)) api.line(X(-16), Y(-16 / n), X(0), Y(0), api.css("--red"), 2.5);
    api.circle(X(le), Y(le / n), 6, api.css("--red"));
    api.label(api.T("log₁₀|λ| 对 log₁₀ε，斜率 1/n", "log₁₀|λ| vs log₁₀ε, slope 1/n"), x0, y0 - 8, mu, 11);
  },
});
