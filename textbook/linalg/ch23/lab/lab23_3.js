// 实验 23.3 正则化：由位置求速度（配 23.3 节）。
// 位置是速度的积分：b = A v + 噪声，A = h × 下三角全 1 矩阵。直接求解 v = A⁻¹b 等于逐点差分，噪声被放大约 √2·σ/h 倍。
// 吉洪诺夫正则化：min ‖Av − b‖² + λ²‖Lv‖²，L = I（岭回归）或 L = 一阶差分 / h（惩罚加速度），解 (AᵀA + λ²LᵀL) v = Aᵀb（乔列斯基分解）。
// 读数给出残差、‖Lv‖、与真实速度的误差；右图为 L 曲线（31 个 λ），当前 λ 用红点标出；偏差原理：残差 ≈ σ√n。
// 场景：关节编码器（200 个点，采样 10 ms）；生活中的例子：跑步手表由 GPS 位置算速度（300 个点，每秒一个，噪声以 m 计）。
WQ.lab({
  title: ["实验 23.3 正则化：由位置求速度", "Lab 23.3 Regularization: velocity from position"],
  goal: ["调节正则化参数 λ、选择惩罚项，看速度估计怎样从“全是噪声”变成“过度平滑”；用 L 曲线和偏差原理找合适的 λ。",
         "Tune the regularization parameter λ and the penalty, and watch the velocity estimate go from pure noise to over-smoothed; find a good λ with the L-curve and the discrepancy principle."],
  scenes: [
    { id: "joint", robot: true, name: ["关节编码器", "Joint encoder"],
      problem: { title: ["机器人问题：编码器读数一差分，速度全是毛刺", "Robot problem: differencing encoder readings gives spiky velocity"],
                 text: ["关节编码器每 10 ms 给出一个角度读数，误差约 0.1 mrad。速度控制需要角速度，可逐点差分得到的速度满是毛刺。能不能既不丢掉真实的变化，又压住噪声？",
                        "A joint encoder gives an angle every 10 ms with about 0.1 mrad of error. The velocity loop needs angular velocity, but point-by-point differencing is full of spikes. Can we suppress the noise without losing the real motion?"] } },
    { id: "run", name: ["生活中的例子：跑步手表", "Everyday example: a running watch"],
      problem: { title: ["生活中的例子：手表上的配速为什么跳来跳去？", "Everyday example: why does the watch's pace jump around?"],
                 text: ["跑步手表每秒记录一个 GPS 位置（沿路线的距离），误差约 2 m。用相邻两秒的位置相减算速度，误差高达约 3 m/s，与跑步速度本身相当。手表是怎样算出平稳的配速的？",
                        "A running watch records a GPS position (distance along the route) every second with about 2 m of error. Differencing consecutive seconds gives a speed error of about 3 m/s, about as large as the running speed itself. How does the watch show a steady pace?"] } },
  ],
  params: [
    { id: "lg", name: ["log₁₀ λ", "log₁₀ λ"], min: -7, max: 2, step: 0.05, value: -3, digits: 2 },
    { id: "L", name: ["惩罚项（0：‖v‖，1：‖加速度‖）", "Penalty (0: ‖v‖, 1: ‖acceleration‖)"], min: 0, max: 1, step: 1, value: 1, digits: 0 },
    { id: "sig", name: ["噪声倍数", "Noise factor"], min: 0.5, max: 4, step: 0.5, value: 1, digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "naive", robot: true, text: ["编码器：把 λ 调到最小（log₁₀ λ = −7），速度误差有多大？与 √2·σ/h 比较。", "Encoder: set λ to its minimum (log₁₀ λ = −7). How large is the velocity error? Compare with √2·σ/h."],
      demo: { scene: "joint", set: { lg: -7, L: 1, sig: 1 }, press: [] } },
    { id: "dp", robot: true, text: ["编码器、惩罚加速度：调 λ，使残差等于噪声水平 σ√n（偏差原理，相差 10% 以内）。速度误差是多少？", "Encoder, acceleration penalty: tune λ until the residual equals the noise level σ√n (within 10%). What is the velocity error?"],
      demo: { scene: "joint", set: { lg: -3.35, L: 1, sig: 1 }, press: [] } },
    { id: "over", robot: true, text: ["把 λ 调得很大（log₁₀ λ ≥ 0），两种惩罚项下速度各变成什么样？", "Make λ very large (log₁₀ λ ≥ 0). What does the velocity become with each penalty?"],
      demo: { scene: "joint", set: { lg: 0.5, L: 0, sig: 1 }, press: [] } },
    { id: "run", text: ["跑步手表：用偏差原理选 λ（惩罚加速度），速度误差降到多少？", "Running watch: choose λ by the discrepancy principle (acceleration penalty). How small is the speed error?"],
      demo: { scene: "run", set: { lg: 1.6, L: 1, sig: 1 }, press: [] } },
  ],
  think: ["惩罚 ‖v‖（岭回归）为什么会把整条速度曲线往零压，而惩罚加速度不会？在你的应用里，“先验地认为什么样的解是合理的”应当怎样写进 L？",
          "Why does penalizing ‖v‖ (ridge) pull the whole velocity curve toward zero while penalizing acceleration does not? In your own application, how should “what a reasonable solution looks like” be written into L?"],

  setup(api) {
    const key = [api.scene, api.p.sig].join(",");
    if (this._s && this._s.key === key) return this._s;
    const run = api.scene === "run", n = run ? 300 : 200, h = run ? 1 : 0.01, sigma = (run ? 2 : 1e-4) * api.p.sig;
    const t = [...Array(n)].map((_, i) => h * (i + 1));
    const vt = t.map((x) => run ? 2.8 + 0.4 * Math.tanh((x - 60) / 20) + 1.2 * Math.exp(-(((x - 240) / 18) ** 2)) - 2.4 * Math.exp(-x / 8)
                                : 1.2 * (Math.tanh((x - 0.4) / 0.12) - Math.tanh((x - 1.5) / 0.15)) / 2);
    const g = api.calc.rng(run ? 23032 : 23031);
    let acc = 0; const b = vt.map((v) => { acc += h * v; return acc + sigma * g.gauss(); });
    // AᵀA 与 Aᵀb（A = h·下三角全 1）：(AᵀA)ᵢⱼ = h²·(n − max(i, j))
    const AtA = [...Array(n)].map((_, i) => [...Array(n)].map((_, j) => h * h * (n - Math.max(i, j))));
    const Atb = [...Array(n)].map((_, j) => { let s = 0; for (let i = j; i < n; i++) s += h * b[i]; return s; });
    this._s = { key, n, h, sigma, t, vt, b, AtA, Atb, curve: {} };
    return this._s;
  },
  solve(S, lam, Ltype) {
    const n = S.n, M = S.AtA.map((r) => r.slice()), l2 = lam * lam;
    if (Ltype === 0) for (let i = 0; i < n; i++) M[i][i] += l2;
    else { const c = l2 / (S.h * S.h); for (let i = 0; i < n - 1; i++) { M[i][i] += c; M[i + 1][i + 1] += c; M[i][i + 1] -= c; M[i + 1][i] -= c; } }
    for (let j = 0; j < n; j++) {                       // 乔列斯基分解（原地，下三角）
      let s = M[j][j]; for (let k = 0; k < j; k++) s -= M[j][k] * M[j][k];
      const d = Math.sqrt(Math.max(s, 1e-300)); M[j][j] = d;
      for (let i = j + 1; i < n; i++) { let t = M[i][j]; for (let k = 0; k < j; k++) t -= M[i][k] * M[j][k]; M[i][j] = t / d; }
    }
    const y = S.Atb.slice();
    for (let i = 0; i < n; i++) { let s = y[i]; for (let k = 0; k < i; k++) s -= M[i][k] * y[k]; y[i] = s / M[i][i]; }
    for (let i = n - 1; i >= 0; i--) { let s = y[i]; for (let k = i + 1; k < n; k++) s -= M[k][i] * y[k]; y[i] = s / M[i][i]; }
    return y;
  },
  stats(S, v, Ltype) {
    let acc = 0, r = 0;
    for (let i = 0; i < S.n; i++) { acc += S.h * v[i]; r += (acc - S.b[i]) ** 2; }
    let lv = 0;
    if (Ltype === 0) v.forEach((x) => { lv += x * x; }); else for (let i = 0; i < S.n - 1; i++) lv += ((v[i + 1] - v[i]) / S.h) ** 2;
    let e = 0; v.forEach((x, i) => { e += (x - S.vt[i]) ** 2; });
    return { res: Math.sqrt(r), lv: Math.sqrt(lv), err: Math.sqrt(e / S.n) };
  },
  curve(S, Ltype) {
    if (S.curve[Ltype]) return S.curve[Ltype];
    const pts = [];
    for (let k = 0; k <= 30; k++) { const lg = -7 + 9 * k / 30, v = this.solve(S, Math.pow(10, lg), Ltype); pts.push({ lg, ...this.stats(S, v, Ltype) }); }
    S.curve[Ltype] = pts; return pts;
  },
  reset(api, s) {},
  readouts(api, s) {
    const S = this.setup(api), v = this.solve(S, Math.pow(10, api.p.lg), api.p.L), st = this.stats(S, v, api.p.L), f = api.fmt;
    const target = S.sigma * Math.sqrt(S.n), unit = api.scene === "run" ? " m/s" : " rad/s", punit = api.scene === "run" ? " m" : " rad";
    const naiveAmp = Math.SQRT2 * S.sigma / S.h;
    if (api.scene === "joint" && api.p.lg <= -6.99) api.done("naive");
    if (api.scene === "joint" && api.p.L === 1 && Math.abs(st.res / target - 1) < 0.1) api.done("dp");
    if (api.scene === "joint" && api.p.lg >= 0) api.done("over");
    if (api.scene === "run" && api.p.L === 1 && Math.abs(st.res / target - 1) < 0.1) api.done("run");
    return [[["点数 n、采样周期 h", "Points n, step h"], S.n + ", " + S.h + " s"],
            [["λ", "λ"], Math.pow(10, api.p.lg).toExponential(2)],
            [["残差 ‖Av − b‖", "Residual ‖Av − b‖"], st.res.toExponential(2) + punit],
            [["噪声水平 σ√n（偏差原理的目标）", "Noise level σ√n (discrepancy target)"], target.toExponential(2) + punit + "（" + f(st.res / target, 2) + api.T(" 倍）", "×)")],
            [["‖Lv‖", "‖Lv‖"], st.lv.toExponential(2)],
            [["速度误差（均方根）", "Velocity error (RMS)"], f(st.err, 4) + unit],
            [["逐点差分的噪声量级 √2·σ/h", "Differencing noise √2·σ/h"], f(naiveAmp, 4) + unit]];
  },
  draw(api, s) {
    const S = this.setup(api), v = this.solve(S, Math.pow(10, api.p.lg), api.p.L), { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink");
    const x0 = 46, x1 = w * 0.6, y0 = 24, y1 = h - 34;
    const vmax = Math.max(...S.vt) * 1.4, vmin = Math.min(0, Math.min(...S.vt)) - 0.2 * vmax;
    const X = (t) => x0 + (x1 - x0) * t / S.t[S.n - 1], Y = (y) => y1 - (y1 - y0) * (Math.min(Math.max(y, vmin), vmax) - vmin) / (vmax - vmin);
    api.rect(x0, y0, x1 - x0, y1 - y0, null, mu);
    api.line(x0, Y(0), x1, Y(0), mu, 0.5, [3, 3]);
    for (let i = 1; i < S.n; i++) {
      api.line(X(S.t[i - 1]), Y(S.vt[i - 1]), X(S.t[i]), Y(S.vt[i]), ink, 1.2, [4, 3]);
      api.line(X(S.t[i - 1]), Y(v[i - 1]), X(S.t[i]), Y(v[i]), api.css("--red"), 1.8);
    }
    api.label(api.T("速度：红为估计，黑虚线为真实", "velocity: red estimate, black dashed truth"), x0, y0 - 8, mu, 11);
    const C = this.curve(S, api.p.L), u0 = w * 0.66, u1 = w - 12;
    const lr = C.map((p) => Math.log10(p.res)), ll = C.map((p) => Math.log10(Math.max(p.lv, 1e-300)));
    const rlo = Math.min(...lr), rhi = Math.max(...lr), llo = Math.min(...ll), lhi = Math.max(...ll);
    const U = (x) => u0 + (u1 - u0) * (x - rlo) / (rhi - rlo || 1), V = (y) => y1 - (y1 - y0) * (y - llo) / (lhi - llo || 1);
    api.rect(u0, y0, u1 - u0, y1 - y0, null, mu);
    for (let k = 1; k < C.length; k++) api.line(U(lr[k - 1]), V(ll[k - 1]), U(lr[k]), V(ll[k]), api.css("--blue"), 2);
    const st = this.stats(S, v, api.p.L);
    api.circle(U(Math.log10(st.res)), V(Math.log10(Math.max(st.lv, 1e-300))), 5, api.css("--red"), ink);
    const xt = U(Math.log10(S.sigma * Math.sqrt(S.n)));
    if (xt >= u0 && xt <= u1) api.line(xt, y0, xt, y1, mu, 1, [5, 4]);
    api.label(api.T("L 曲线（双对数）：横轴残差，纵轴 ‖Lv‖；虚线为 σ√n", "L-curve (log–log): residual vs ‖Lv‖; dashed: σ√n"), u0, y0 - 8, mu, 11);
  },
});
