// 实验 21.7 最小二乘的梯度与梯度下降（配 21.7 节）。
// 模型 d ≈ θ₁·x + θ₂，x = (r − f·r̄)/S（r 为原始读数，r̄、S 为它的均值和标准差，f 为“去均值的比例”）。
// 目标 F(θ) = ‖Dθ − d‖²，D = (x, 1)；梯度 ∇F = 2Dᵀ(Dθ − d)；黑塞矩阵 2H，H = DᵀD。
// 梯度下降 θ ← θ − η∇F 的误差满足 e ← (I − 2ηH)e：0 < η < 1/λ_max 才收敛，最优固定步长 η = 1/(λ_min + λ_max)，收敛因子 (κ − 1)/(κ + 1)。
// 原始读数（不除以标准差）时 κ ≈ 1.6×10⁷，画不出来，只在读数中给出；这里的 x 总是先除以标准差。
// 标定数据与程序 21.7.1 相同（读数取一位小数）。生活场景：出租车车费 = 单价 × 里程 + 起步价。
WQ.lab({
  title: ["实验 21.7 最小二乘的梯度与梯度下降", "Lab 21.7 The least-squares gradient and gradient descent"],
  goal: ["用矩阵微积分得到最小二乘的梯度 2Aᵀ(Aθ − b)，并用有限差分检验；看梯度下降的步长上限 1/λ_max 和收敛快慢怎样由 AᵀA 的特征值、条件数决定，体会去均值（中心化）的作用。",
         "Get the least-squares gradient 2Aᵀ(Aθ − b) by matrix calculus and check it by finite differences; see how the step-size limit 1/λ_max and the speed of gradient descent are set by the eigenvalues and condition number of AᵀA, and what centering does."],
  scenes: [
    { id: "cal", robot: true, name: ["AGV 测距传感器标定", "AGV range-sensor calibration"],
      problem: { title: ["机器人问题：为什么梯度下降几乎不动？", "Robot problem: why does gradient descent barely move?"],
                 text: ["12 组数据：激光跟踪仪测得的真实距离 d（0.3～3 m）与测距传感器的原始读数 r（计数）。用 d ≈ a·r + c 标定。正规方程一步就能解出，梯度下降却慢得出奇。",
                        "Twelve pairs: true distance d (0.3–3 m, laser tracker) and raw sensor reading r (counts). Calibrate d ≈ a·r + c. The normal equations solve it at once, yet gradient descent is strangely slow."] } },
    { id: "taxi", name: ["生活中的例子：出租车车费", "Everyday example: taxi fares"],
      problem: { title: ["生活中的例子：从车票反推计价规则", "Everyday example: recover the fare rule from receipts"],
                 text: ["8 张出租车票：里程 2～18 km，车费 15～52 元。设车费 ≈ 每公里单价 × 里程 + 起步价，用梯度下降拟合。",
                        "Eight taxi receipts: 2–18 km, 15–52 yuan. Assume fare ≈ price per km × distance + flag fall, and fit it by gradient descent."] } },
  ],
  params: [
    { id: "f", name: ["去均值的比例 f", "Fraction of the mean removed f"], min: 0, max: 1, step: 0.05, value: 0, digits: 2 },
    { id: "eta", name: ["步长 η（以 1/λ_max 为单位）", "Step η (in units of 1/λ_max)"], min: 0.05, max: 1.2, step: 0.01, value: 0.5, digits: 2 },
    { id: "k", name: ["迭代步数", "Iterations"], min: 0, max: 60, step: 1, value: 20, digits: 0 },
    { id: "u", name: ["检验点 θ₁ − θ₁*", "Probe θ₁ − θ₁*"], min: -1.5, max: 1.5, step: 0.05, value: 0.8, digits: 2 },
    { id: "v", name: ["检验点 θ₂ − θ₂*", "Probe θ₂ − θ₂*"], min: -1.5, max: 1.5, step: 0.05, value: -0.6, digits: 2 },
  ],
  buttons: [{ id: "opt", name: ["最优步长（再拖步长滑块即取消）", "Optimal step (moving the step slider cancels it)"] }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "grad", robot: true, text: ["把检验点放到任意位置，比较解析梯度（红）与有限差分（灰）。两者相差多少？", "Put the probe anywhere and compare the analytic gradient (red) with finite differences (grey). How far apart are they?"],
      demo: { scene: "cal", set: { f: 0, eta: 0.5, k: 20, u: 0.8, v: -0.6 }, press: [] } },
    { id: "diverge", robot: true, text: ["f = 0：加大步长，找出梯度下降开始发散的步长（迭代 20 步以上），与 1/λ_max 比较。", "f = 0: increase the step until gradient descent diverges (20 or more iterations); compare with 1/λ_max."],
      demo: { scene: "cal", set: { f: 0, eta: 1.02, k: 30, u: 0.8, v: -0.6 }, press: [] } },
    { id: "slow", robot: true, text: ["f = 0：按“最优步长”，迭代 60 步。目标函数离最小值还差多少？路径是什么样子？", "f = 0: press “Optimal step” and run 60 iterations. How far is the objective from its minimum? What does the path look like?"],
      demo: { scene: "cal", set: { f: 0, k: 60, u: 0.8, v: -0.6 }, press: ["opt"] } },
    { id: "one", robot: true, text: ["f = 1（完全去均值）：按“最优步长”，梯度下降几步收敛？此时条件数是多少？", "f = 1 (fully centred): press “Optimal step”. How many iterations does gradient descent need? What is the condition number?"],
      demo: { scene: "cal", set: { f: 1, k: 1, u: 0.8, v: -0.6 }, press: ["opt"] } },
    { id: "taxi", text: ["出租车场景：去均值后一步求出单价和起步价，换算回原来的变量。", "Taxi scene: centre the data, solve in one step and convert back to price per km and flag fall."],
      demo: { scene: "taxi", set: { f: 1, k: 1, u: 0.8, v: -0.6 }, press: ["opt"] } },
  ],
  think: ["把读数先除以标准差后，κ 从约 1.6×10⁷ 降到约 30；再去均值，κ 降到 1。去均值相当于把 x 和常数 1 这两列“掰正交”。神经网络对输入做标准化、批归一化，道理是不是一样？",
          "Dividing the readings by their standard deviation brings κ from about 1.6×10⁷ down to about 30; removing the mean brings it to 1. Centering makes the column x orthogonal to the constant column. Is that why neural networks standardize their inputs and use batch normalization?"],

  CAL: { r: [274.5, 526.1, 774.3, 1022.3, 1274.5, 1522.8, 1777.5, 2033.1, 2276.2, 2526.2, 2781.1, 3031.0],
         d: [0.3, 0.5455, 0.7909, 1.0364, 1.2818, 1.5273, 1.7727, 2.0182, 2.2636, 2.5091, 2.7545, 3.0] },
  TAXI: { r: [2.0, 3.5, 5.2, 7.8, 10.1, 12.6, 15.3, 18.0], d: [14.9, 18.6, 22.1, 28.3, 33.0, 39.4, 45.0, 51.6] },
  prob(api) {
    const S = api.scene === "taxi" ? this.TAXI : this.CAL, n = S.r.length;
    const rbar = S.r.reduce((a, b) => a + b, 0) / n, sd = Math.sqrt(S.r.reduce((a, b) => a + (b - rbar) ** 2, 0) / n);
    const x = S.r.map((r) => (r - api.p.f * rbar) / sd);
    const sx = x.reduce((a, b) => a + b, 0), sxx = x.reduce((a, b) => a + b * b, 0);
    const sy = S.d.reduce((a, b) => a + b, 0), sxy = x.reduce((a, b, i) => a + b * S.d[i], 0);
    const H = [[sxx, sx], [sx, n]], det = sxx * n - sx * sx;
    const th = [(n * sxy - sx * sy) / det, (sxx * sy - sx * sxy) / det];
    const e = api.la.eigSym(H), lmin = e.values[0], lmax = e.values[1];
    const F = (t) => x.reduce((a, xi, i) => a + (t[0] * xi + t[1] - S.d[i]) ** 2, 0);
    const grad = (t) => { const r = x.map((xi, i) => t[0] * xi + t[1] - S.d[i]); return [2 * r.reduce((a, b, i) => a + b * x[i], 0), 2 * r.reduce((a, b) => a + b, 0)]; };
    // 原始读数（不缩放、不去均值）的条件数
    const R1 = S.r.reduce((a, b) => a + b, 0), R2 = S.r.reduce((a, b) => a + b * b, 0), raw = api.la.eigSym([[R2, R1], [R1, n]]).values;
    return { S, n, rbar, sd, x, H, th, lmin, lmax, F, grad, Fs: F(th), kraw: raw[1] / raw[0] };
  },
  etaOf(api, P) { return this._opt ? 1 / (P.lmin + P.lmax) : api.p.eta / P.lmax; },     // “最优步长”按钮的状态放在 this 上，参数改动重置 state 时不丢
  path(api, P) {
    const eta = this.etaOf(api, P), pts = [[0, 0]];
    let t = [0, 0];
    for (let k = 0; k < api.p.k; k++) { const g = P.grad(t); t = [t[0] - eta * g[0], t[1] - eta * g[1]]; pts.push(t); if (!Number.isFinite(t[0]) || Math.abs(t[0]) > 1e12) break; }
    return pts;
  },
  reset(api, s) {},
  action(id, api, s) { if (id === "opt") this._opt = true; else if (id === "reset") this._opt = false; },
  change(api, s, pid) { if (pid === "eta") this._opt = false; },
  readouts(api, s) {
    const P = this.prob(api), f = api.fmt, pts = this.path(api, P), last = pts[pts.length - 1];
    const kap = P.lmax / P.lmin, eta = this.etaOf(api, P), rho = Math.max(Math.abs(1 - 2 * eta * P.lmin), Math.abs(1 - 2 * eta * P.lmax));
    const gap = P.F(last) - P.Fs, probe = [P.th[0] + api.p.u, P.th[1] + api.p.v], ga = P.grad(probe), h = 1e-6;
    const gn = [0, 1].map((i) => { const a = probe.slice(), b = probe.slice(); a[i] += h; b[i] -= h; return (P.F(a) - P.F(b)) / (2 * h); });
    const rel = Math.hypot(ga[0] - gn[0], ga[1] - gn[1]) / Math.max(Math.hypot(ga[0], ga[1]), 1e-300);
    const diverged = !Number.isFinite(gap) || gap > 10 * P.F([0, 0]);
    const isOpt = this._opt || Math.abs(api.p.eta - P.lmax / (P.lmin + P.lmax)) <= 0.006;
    if (Math.hypot(api.p.u, api.p.v) > 0.1 && rel < 1e-5) api.done("grad");
    if (api.scene === "cal" && api.p.f === 0 && api.p.k >= 20 && diverged && api.p.eta <= 1.05) api.done("diverge");
    if (api.scene === "cal" && api.p.f === 0 && api.p.k >= 60 && isOpt && gap > 1e-6) api.done("slow");
    if (api.scene === "cal" && api.p.f === 1 && isOpt && api.p.k >= 1 && gap < 1e-9) api.done("one");
    if (api.scene === "taxi" && api.p.f === 1 && api.p.k >= 1 && gap < 1e-9) api.done("taxi");
    // 换算回原来的变量：d = θ₁(r − f r̄)/S + θ₂ = (θ₁/S) r + (θ₂ − θ₁ f r̄/S)
    const a = last[0] / P.sd, c = last[1] - last[0] * api.p.f * P.rbar / P.sd;
    const astar = P.th[0] / P.sd, cstar = P.th[1] - P.th[0] * api.p.f * P.rbar / P.sd, taxi = api.scene === "taxi";
    const fmtS = (x) => (Math.abs(x) >= 1e4 || (Math.abs(x) < 1e-3 && x !== 0)) ? x.toExponential(2) : f(x, 4);
    return [[["AᵀA 的特征值 λ_min, λ_max", "Eigenvalues of AᵀA"], f(P.lmin, 3) + ", " + f(P.lmax, 3)],
            [["条件数 κ（括号内为不缩放、不去均值的原始读数）", "Condition number κ (in brackets: raw, unscaled readings)"], f(kap, 2) + api.T("（", " (") + P.kraw.toExponential(1) + api.T("）", ")")],
            [["步长 η、上限 1/λ_max、最优 1/(λ_min + λ_max)", "Step η, limit 1/λ_max, optimum 1/(λ_min + λ_max)"], (this._opt ? api.T("（最优）", "(optimal) ") : "") + fmtS(eta) + ", " + fmtS(1 / P.lmax) + ", " + fmtS(1 / (P.lmin + P.lmax))],
            [["收敛因子 ρ(I − 2ηAᵀA)", "Convergence factor ρ(I − 2ηAᵀA)"], f(rho, 4) + (rho >= 1 ? api.T("（≥ 1，不收敛）", " (≥ 1: no convergence)") : "")],
            [["迭代后 F(θ) − F*", "F(θ) − F* after the iterations"], diverged ? api.T("发散", "diverged") : fmtS(Math.max(gap, 0))],
            [["检验点：解析梯度 / 有限差分", "Probe: analytic / finite-difference gradient"], "(" + f(ga[0], 4) + ", " + f(ga[1], 4) + ") / (" + f(gn[0], 4) + ", " + f(gn[1], 4) + ")"],
            [["两者的相对差", "Relative difference"], rel.toExponential(1)],
            [[taxi ? "当前的单价、起步价（最小二乘解）" : "当前的 a、c（最小二乘解）", taxi ? "Current price per km, flag fall (least squares)" : "Current a, c (least squares)"],
             diverged ? "—" : (taxi ? f(a, 3) + api.T(" 元/km、", " yuan/km, ") + f(c, 2) + api.T(" 元（", " yuan (") + f(astar, 3) + ", " + f(cstar, 2) + api.T("）", ")")
                                    : f(a * 1000, 4) + api.T(" mm/计数、", " mm/count, ") + f(c * 1000, 1) + " mm (" + f(astar * 1000, 4) + ", " + f(cstar * 1000, 1) + ")")]];
  },
  draw(api, s) {
    const P = this.prob(api), { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink");
    const pts = this.path(api, P), probe = [P.th[0] + api.p.u, P.th[1] + api.p.v];
    const R = Math.max(Math.hypot(P.th[0], P.th[1]), Math.hypot(api.p.u, api.p.v)) * 1.25 + 0.2;
    const bx = 10, by = 10, bw = w - 20, bh = h - 40, sc = Math.min(bw, bh) / (2 * R), cx = bx + bw / 2, cy = by + bh / 2;
    const X = (t) => cx + (t[0] - P.th[0]) * sc, Y = (t) => cy - (t[1] - P.th[1]) * sc;
    const inBox = (p) => p[0] >= bx && p[0] <= bx + bw && p[1] >= by && p[1] <= by + bh;
    api.rect(bx, by, bw, bh, null, mu);
    // 等值线：F − F* = (θ − θ*)ᵀH(θ − θ*) = L
    const e = api.la.eigSym(P.H), V = e.vectors, L0 = P.F([0, 0]) - P.Fs;
    [1, 0.5, 0.25, 0.1, 0.03, 0.01, 0.002].forEach((q) => {
      const L = L0 * q, a1 = Math.sqrt(L / e.values[0]), a2 = Math.sqrt(L / e.values[1]);
      let prev = null;
      for (let j = 0; j <= 160; j++) {
        const t = 2 * Math.PI * j / 160, d = [a1 * Math.cos(t) * V[0][0] + a2 * Math.sin(t) * V[0][1], a1 * Math.cos(t) * V[1][0] + a2 * Math.sin(t) * V[1][1]];
        const p = [X([P.th[0] + d[0], P.th[1] + d[1]]), Y([P.th[0] + d[0], P.th[1] + d[1]])];
        if (prev && inBox(prev) && inBox(p)) api.line(prev[0], prev[1], p[0], p[1], mu, 1);
        prev = p;
      }
    });
    // 梯度下降的路径
    for (let i = 1; i < pts.length; i++) {
      const p = [X(pts[i - 1]), Y(pts[i - 1])], q = [X(pts[i]), Y(pts[i])];
      if (inBox(p) && inBox(q)) api.line(p[0], p[1], q[0], q[1], api.css("--blue"), 2);
      if (inBox(q)) api.circle(q[0], q[1], 2.5, api.css("--blue"));
    }
    const s0 = [X([0, 0]), Y([0, 0])];
    if (inBox(s0)) { api.circle(s0[0], s0[1], 4.5, api.css("--blue"), ink); api.label(api.T("起点 θ = 0", "start θ = 0"), s0[0] + 6, s0[1] - 6, api.css("--blue"), 11); }
    api.circle(cx, cy, 5, api.css("--green"), ink);
    api.label("θ*", cx + 7, cy - 7, api.css("--green"), 12);
    // 检验点处的梯度：解析（红，实线）与有限差分（灰，虚线），画的是下降方向 −∇F，长度统一为 60 像素
    const ga = P.grad(probe), hh = 1e-6;
    const gn = [0, 1].map((i) => { const a = probe.slice(), b = probe.slice(); a[i] += hh; b[i] -= hh; return (P.F(a) - P.F(b)) / (2 * hh); });
    const pp = [X(probe), Y(probe)], nrm = Math.hypot(ga[0], ga[1]) || 1;
    api.circle(pp[0], pp[1], 4, api.css("--red"), ink);
    api.line(pp[0], pp[1], pp[0] - 60 * gn[0] / nrm, pp[1] + 60 * gn[1] / nrm, mu, 5);
    api.line(pp[0], pp[1], pp[0] - 60 * ga[0] / nrm, pp[1] + 60 * ga[1] / nrm, api.css("--red"), 2, [6, 3]);
    api.label("−∇F", pp[0] - 60 * ga[0] / nrm + 4, pp[1] + 60 * ga[1] / nrm - 4, api.css("--red"), 12);
    api.label(api.T("横轴 θ₁（斜率），纵轴 θ₂（截距），两轴同比例；灰线为等值线，蓝线为梯度下降的路径",
                    "horizontal θ₁ (slope), vertical θ₂ (intercept), equal scales; grey: level sets, blue: gradient-descent path"), 10, h - 10, mu, 11);
  },
});
