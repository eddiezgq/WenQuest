// 实验 23.6 UR5e 的 DH 参数标定（配 23.6 节，模拟测量数据带噪声）。
// 名义 DH 参数（优傲公布）：d = (0.1625, 0, 0, 0.1333, 0.0997, 0.0996) m，a = (0, −0.425, −0.3922, 0, 0, 0) m，α = (π/2, 0, 0, π/2, −π/2, 0)。
// 每个关节 4 个参数 (θ₀, d, a, α)，共 24 个；“真实”机器人在每个参数上加 1 mm、1 mrad 量级的随机误差（种子固定）。
// 激光跟踪仪测 N 个随机位姿下法兰中心的位置（噪声可调）。按“标定”键做 8 步高斯–牛顿迭代：每步在当前参数处用中心差分求雅可比矩阵，
// 只保留前 k 个奇异值（截断 SVD）求修正量；使残差变大的一步不接受。程序 23.6.1 另加了列文伯格–马夸特阻尼。另取 30 个位姿与真实位置比较，作为验证。与程序 23.6.1 的做法相同（随机数不同，数值略有差别）。
WQ.lab({
  title: ["实验 23.6 UR5e 的 DH 参数标定", "Lab 23.6 DH-parameter calibration of a UR5e"],
  goal: ["用带噪声的激光跟踪仪数据标定 UR5e 的 24 个 DH 参数：看雅可比矩阵的奇异值怎样揭示“看不见”的参数组合，截断 SVD 怎样避免荒谬的修正，位姿个数和测量噪声怎样决定标定后的精度。",
         "Calibrate the 24 DH parameters of a UR5e from noisy laser-tracker data: see how the singular values of the Jacobian reveal unobservable parameter combinations, how truncated SVD avoids absurd corrections, and how pose count and noise set the final accuracy."],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 与激光跟踪仪", "UR5e and laser tracker"],
      problem: { title: ["机器人问题：图纸参数差 1 mm，末端差多少？", "Robot problem: drawing parameters off by 1 mm—how far off is the tool?"],
                 text: ["机器人出厂时零件尺寸、装配都有误差，控制器按名义 DH 参数算出的末端位置与实际相差几毫米。用激光跟踪仪测几十个位姿下的末端位置，反推出真实的参数，再写回控制器，就是运动学标定。",
                        "Manufacturing and assembly errors make the nominal DH parameters slightly wrong, so the computed tool position is off by millimetres. Measuring the tool at dozens of poses with a laser tracker and solving for the true parameters is kinematic calibration."] } },
  ],
  params: [
    { id: "N", name: ["标定位姿个数 N", "Calibration poses N"], min: 8, max: 100, step: 1, value: 50, digits: 0 },
    { id: "noise", name: ["测量噪声（标准差）", "Measurement noise (std. dev.)"], min: 0.01, max: 0.3, step: 0.01, value: 0.05, unit: " mm", digits: 2 },
    { id: "k", name: ["保留的奇异值个数 k", "Singular values kept k"], min: 6, max: 24, step: 1, value: 18, digits: 0 },
  ],
  buttons: [{ id: "cal", name: ["标定", "Calibrate"] }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "rank", robot: true, text: ["看奇异值图：有几个奇异值明显不为零？取 k 等于它，按“标定”。", "Look at the singular values: how many are clearly nonzero? Set k to that number and calibrate."],
      demo: { scene: "ur", set: { N: 50, noise: 0.05, k: 18 }, press: ["cal"] } },
    { id: "good", robot: true, text: ["N = 50、噪声 0.05 mm、k = 18：验证误差的均方根降到多少？比标定前小了多少倍？", "N = 50, noise 0.05 mm, k = 18: how small is the validation RMS error? By what factor did it shrink?"],
      demo: { scene: "ur", set: { N: 50, noise: 0.05, k: 18 }, press: ["cal"] } },
    { id: "over", robot: true, text: ["把 k 加到 20 以上再标定：修正量和验证误差怎样？", "Calibrate with k above 20: what happens to the correction and the validation error?"],
      demo: { scene: "ur", set: { N: 50, noise: 0.05, k: 22 }, press: ["cal"] } },
    { id: "few", robot: true, text: ["只用 N ≤ 12 个位姿标定（k = 18）：验证误差与 N = 50 时比较，第 18 个奇异值怎样变化？", "Calibrate with N ≤ 12 poses (k = 18): compare the validation error with N = 50; how does the 18th singular value change?"],
      demo: { scene: "ur", set: { N: 10, noise: 0.05, k: 18 }, press: ["cal"] } },
    { id: "noisy", robot: true, text: ["把噪声加到 0.2 mm 以上（N = 50，k = 18）：标定后的精度受什么限制？", "Raise the noise above 0.2 mm (N = 50, k = 18): what limits the accuracy after calibration?"],
      demo: { scene: "ur", set: { N: 50, noise: 0.25, k: 18 }, press: ["cal"] } },
  ],
  think: ["只测末端位置时，第 6 关节的零点 θ₀₆ 和扭角 α₆ 为什么完全“看不见”？若跟踪仪还能测末端的姿态（用三个靶球），雅可比矩阵的秩会怎样变化？",
          "With position-only measurements, why are the sixth joint's zero offset θ₀₆ and twist α₆ completely invisible? If the tracker also measured orientation (three target balls), how would the rank of the Jacobian change?"],

  NOM: [0, 0, 0, 0, 0, 0, 0.1625, 0, 0, 0.1333, 0.0997, 0.0996, 0, -0.425, -0.3922, 0, 0, 0, Math.PI / 2, 0, 0, Math.PI / 2, -Math.PI / 2, 0],
  NAMES: ["θ01", "θ02", "θ03", "θ04", "θ05", "θ06", "d1", "d2", "d3", "d4", "d5", "d6", "a1", "a2", "a3", "a4", "a5", "a6", "α1", "α2", "α3", "α4", "α5", "α6"],
  fk(p, q) {
    let T = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
    for (let i = 0; i < 6; i++) {
      const ct = Math.cos(q[i] + p[i]), st = Math.sin(q[i] + p[i]), ca = Math.cos(p[18 + i]), sa = Math.sin(p[18 + i]), d = p[6 + i], a = p[12 + i];
      const Ti = [[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d], [0, 0, 0, 1]];
      const R = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
      for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) { let s = 0; for (let k = 0; k < 4; k++) s += T[r][k] * Ti[k][c]; R[r][c] = s; }
      T = R;
    }
    return [T[0][3], T[1][3], T[2][3]];
  },
  fkAll(p, Q) { const out = []; Q.forEach((q) => out.push(...this.fk(p, q))); return out; },
  poses(api, n, seed) {
    const g = api.calc.rng(seed), lo = [-170, -150, -150, -170, -170, -170], hi = [170, -30, 150, 170, 170, 170];
    return [...Array(n)].map(() => lo.map((l, j) => (l + (hi[j] - l) * g.u()) * Math.PI / 180));
  },
  truth(api) {
    if (this._truth) return this._truth;
    const g = api.calc.rng(23061);
    this._truth = this.NOM.map((v) => v + 1e-3 * g.gauss());
    return this._truth;
  },
  data(api) {
    const key = [api.p.N, api.p.noise].join(",");
    if (this._d && this._d.key === key) return this._d;
    const pt = this.truth(api), Q = this.poses(api, api.p.N, 23062), g = api.calc.rng(23063 + api.p.N);
    const y = this.fkAll(pt, Q).map((v) => v + api.p.noise * 1e-3 * g.gauss());
    const Qv = this.poses(api, 30, 23064), yv = this.fkAll(pt, Qv);
    this._d = { key, Q, y, Qv, yv };
    return this._d;
  },
  jac(p, Q) {
    const h = 1e-7, m = 3 * Q.length, J = [...Array(m)].map(() => Array(24).fill(0));
    for (let k = 0; k < 24; k++) {
      const pp = p.slice(), pm = p.slice(); pp[k] += h; pm[k] -= h;
      const fp = this.fkAll(pp, Q), fm = this.fkAll(pm, Q);
      for (let i = 0; i < m; i++) J[i][k] = (fp[i] - fm[i]) / (2 * h);
    }
    return J;
  },
  rms(a, b) { let s = 0; for (let i = 0; i < a.length; i++) s += (a[i] - b[i]) ** 2; return Math.sqrt(s / a.length); },
  calibrate(api) {
    const D = this.data(api), k = api.p.k;
    let p = this.NOM.slice(), F = this.rms(this.fkAll(p, D.Q), D.y), maxCorr = 0, acc = 0, rej = 0;
    for (let it = 0; it < 8; it++) {
      const J = this.jac(p, D.Q), fp = this.fkAll(p, D.Q), r = D.y.map((v, i) => v - fp[i]);
      const sv = api.la.svd(J), U = sv.U, s = sv.s, V = sv.V;
      const dp = Array(24).fill(0);
      for (let j = 0; j < k; j++) {
        if (s[j] <= 0) continue;
        let c = 0; for (let i = 0; i < r.length; i++) c += U[i][j] * r[i];
        const f = 1 / s[j];                                    // 截断 SVD：保留的奇异值直接求逆，不加阻尼
        for (let q = 0; q < 24; q++) dp[q] += V[q][j] * f * c;
      }
      const pn = p.map((v, i) => v + dp[i]), Fn = this.rms(this.fkAll(pn, D.Q), D.y);
      maxCorr = Math.max(maxCorr, Math.sqrt(dp.reduce((a, b) => a + b * b, 0)));
      if (Fn < F) { p = pn; F = Fn; acc++; } else rej++;    // 使残差变大的一步不接受
    }
    this._cal = { key: [api.p.N, api.p.noise, api.p.k].join(","), p, F, maxCorr, acc, rej };
  },
  action(id, api, s) { if (id === "cal") this.calibrate(api); },
  svals(api) {
    const key = api.p.N;
    if (this._s && this._s.key === key) return this._s.s;
    const D = this.data(api), s = api.la.svd(this.jac(this.NOM, D.Q)).s;
    this._s = { key, s }; return s;
  },
  reset(api, s) {},
  readouts(api, s) {
    const D = this.data(api), f = api.fmt, sv = this.svals(api), pt = this.truth(api);
    const before = this.rms(this.fkAll(this.NOM, D.Qv), D.yv) * 1000;
    const cal = this._cal && this._cal.key === [api.p.N, api.p.noise, api.p.k].join(",") ? this._cal : null;
    const after = cal ? this.rms(this.fkAll(cal.p, D.Qv), D.yv) * 1000 : NaN;
    if (cal && api.p.k === 18) api.done("rank");
    if (cal && api.p.k === 18 && api.p.N >= 50 && Math.abs(api.p.noise - 0.05) < 1e-9 && after < 0.03) api.done("good");
    if (cal && api.p.k >= 20 && (!(after < 1) || cal.maxCorr > 1)) api.done("over");
    if (cal && api.p.k === 18 && api.p.N <= 12) api.done("few");
    if (cal && api.p.k === 18 && api.p.N >= 50 && api.p.noise >= 0.2) api.done("noisy");
    const rows = [[["测量个数 × 参数个数", "Measurements × parameters"], 3 * api.p.N + " × 24"],
                  [["奇异值 σ₁、σ₁₈、σ₁₉", "Singular values σ₁, σ₁₈, σ₁₉"], f(sv[0], 2) + ", " + f(sv[17], 3) + ", " + sv[18].toExponential(1)],
                  [["标定前的验证误差（均方根）", "Validation RMS before"], f(before, 3) + " mm"]];
    if (cal) {
      rows.push([["标定后的验证误差（均方根）", "Validation RMS after"], Number.isFinite(after) && after < 1e6 ? f(after, 4) + " mm" : api.T("发散", "diverged")]);
      rows.push([["8 步迭代：接受 / 拒绝", "8 iterations: accepted / rejected"], cal.acc + " / " + cal.rej +
        (cal.acc === 0 ? api.T("（每一步都使残差变大，参数停在名义值）", " (every step increased the residual; parameters stayed nominal)") : "")]);
      rows.push([["标定数据的残差（均方根）", "Calibration residual RMS"], f(cal.F * 1000, 4) + " mm"]);
      rows.push([["单步修正量的最大范数", "Largest correction step"], cal.maxCorr > 1 ? cal.maxCorr.toExponential(1) + api.T("（荒谬）", " (absurd)") : cal.maxCorr.toExponential(1)]);
      [13, 14, 6].forEach((i) => rows.push([[this.NAMES[i] + " 的估计误差", "Estimation error of " + this.NAMES[i]], f((cal.p[i] - pt[i]) * 1000, 3) + " mm"]));
    } else rows.push([["标定后", "After calibration"], api.T("按“标定”开始", "press “Calibrate”")]);
    return rows;
  },
  draw(api, s) {
    const D = this.data(api), { w, h } = api, mu = api.css("--muted"), sv = this.svals(api);
    // 左：验证位姿上的误差（对数坐标，0.001～10 mm）
    const x0 = 50, x1 = w * 0.58, y0 = 24, y1 = h - 36;
    const Y = (v) => y1 - (y1 - y0) * (Math.log10(Math.max(v, 1e-3)) + 3) / 4;
    api.rect(x0, y0, x1 - x0, y1 - y0, null, mu);
    [0.001, 0.01, 0.1, 1, 10].forEach((v) => { api.line(x0, Y(v), x1, Y(v), mu, 0.5, [3, 3]); api.label(String(v), 6, Y(v) + 4, mu, 10); });
    const cal = this._cal && this._cal.key === [api.p.N, api.p.noise, api.p.k].join(",") ? this._cal : null;
    const eb = [], ea = [];
    const fb = this.fkAll(this.NOM, D.Qv), fa = cal ? this.fkAll(cal.p, D.Qv) : null;
    for (let i = 0; i < 30; i++) {
      eb.push(Math.hypot(fb[3 * i] - D.yv[3 * i], fb[3 * i + 1] - D.yv[3 * i + 1], fb[3 * i + 2] - D.yv[3 * i + 2]) * 1000);
      if (fa) ea.push(Math.hypot(fa[3 * i] - D.yv[3 * i], fa[3 * i + 1] - D.yv[3 * i + 1], fa[3 * i + 2] - D.yv[3 * i + 2]) * 1000);
    }
    const bw = (x1 - x0) / 30;
    for (let i = 0; i < 30; i++) {
      api.rect(x0 + i * bw + 1, Y(eb[i]), bw * 0.42, y1 - Y(eb[i]), mu);
      if (fa && Number.isFinite(ea[i])) api.rect(x0 + i * bw + bw * 0.48, Y(Math.min(ea[i], 10)), bw * 0.42, y1 - Y(Math.min(ea[i], 10)), api.css("--red"));
    }
    api.label(api.T("30 个验证位姿的末端误差 / mm（灰：标定前，红：标定后）", "tool error at 30 validation poses / mm (grey before, red after)"), x0, y0 - 8, mu, 11);
    // 右：奇异值（对数坐标 10⁻¹⁸～10²）
    const u0 = w * 0.64, u1 = w - 14;
    const Ys = (v) => y1 - (y1 - y0) * (Math.log10(Math.max(v, 1e-18)) + 18) / 20;
    api.rect(u0, y0, u1 - u0, y1 - y0, null, mu);
    [[0, "1"], [-6, "10⁻⁶"], [-12, "10⁻¹²"], [-18, "10⁻¹⁸"]].forEach(([e, t]) => {
      api.line(u0, Ys(10 ** e), u1, Ys(10 ** e), mu, 0.5, [3, 3]); api.label(t, u0 - 34, Ys(10 ** e) + 4, mu, 10);
    });
    sv.forEach((v, i) => api.circle(u0 + (i + 0.5) * (u1 - u0) / 24, Ys(v), 3.5, i < api.p.k ? api.css("--blue") : mu));
    const xc = u0 + api.p.k * (u1 - u0) / 24;
    api.line(xc, y0, xc, y1, api.css("--red"), 1.5, [5, 4]);
    api.label(api.T("雅可比矩阵的 24 个奇异值（蓝：保留）", "24 singular values (blue: kept)"), u0, y0 - 8, mu, 11);
  },
});
