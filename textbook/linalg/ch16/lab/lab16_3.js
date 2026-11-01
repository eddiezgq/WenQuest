// 实验 16.3 相平面与稳定性（配 16.3 节）。状态 x = (θ, ω)，惯量归一化为 1：θ̈ = aθ − K_pθ − K_dθ̇，
// A = [[0, 1], [a − K_p, −K_d]]。场景“关节”a = 0（PD 控制的关节，13.5 节）；场景“倒立摆”a = 3g/(2l) = 29.43 s⁻²
// （均匀杆 l = 0.5 m 绕底端转，16.3.5 节；实验中的 K_p、K_d 已除以转动惯量 J，即 K_p,实验 = K_p/J）。轨线用解析解 x(t) = e^{At}x₀ 计算（2×2 矩阵指数的闭式）。
WQ.lab({
  title: ["实验 16.3 相平面与稳定性", "Lab 16.3 Phase plane and stability"],
  goal: ["调节 PD 控制器的两个增益，观察系统矩阵 A 的特征值在复平面上的位置、相平面上轨线的形状（结点、焦点、中心、鞍点）与关节角的时间响应之间的对应。",
         "Tune the two PD gains and relate the eigenvalues of the system matrix A in the complex plane to the shape of the phase-plane trajectories (node, focus, center, saddle) and to the joint-angle response."],
  scenes: [
    { id: "joint", robot: true, name: ["PD 控制的关节", "PD-controlled joint"],
      problem: { title: ["增益怎么调，关节回零又快又不晃？", "Which gains bring the joint back fast without ringing?"],
                 text: ["伺服关节用 PD 控制回到零位：u = −K_pθ − K_dθ̇。K_p 像一根弹簧，K_d 像一个阻尼器。增益太小回得慢，K_d 太小会来回晃。",
                        "A servo joint returns to zero under PD control u = −K_pθ − K_dθ̇. K_p acts like a spring and K_d like a damper. Small gains are slow; a small K_d makes the joint ring."] } },
    { id: "inv", robot: true, name: ["倒立摆", "Inverted pendulum"],
      problem: { title: ["倒立的连杆要多大的增益才立得住？", "How much gain keeps an inverted link upright?"],
                 text: ["竖直向上的连杆在重力作用下是一个鞍点：稍有偏离就倒下。PD 控制要先用 K_p 抵消重力的“负刚度”，再用 K_d 提供阻尼。",
                        "An upright link under gravity is a saddle: any deviation makes it fall. The PD controller must first cancel gravity's negative stiffness with K_p, then add damping with K_d."] } },
  ],
  params: [
    { id: "kp", name: ["比例增益 K_p", "Proportional gain K_p"], min: 0, max: 200, step: 1, value: 100, unit: "s⁻²", digits: 0 },
    { id: "kd", name: ["微分增益 K_d", "Derivative gain K_d"], min: 0, max: 40, step: 0.5, value: 4, unit: "s⁻¹", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["从 θ = 1 释放", "Release from θ = 1"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "center", robot: true, text: ["关节场景：让轨线成为闭合的椭圆（中心）。这时特征值在哪里？", "Joint: make the trajectories closed ellipses (a center). Where are the eigenvalues?"],
      demo: { scene: "joint", set: { kp: 100, kd: 0 }, press: [] } },
    { id: "crit", robot: true, text: ["关节场景：K_p = 100，调 K_d 使两个特征值重合（临界阻尼）。", "Joint: with K_p = 100, tune K_d until the two eigenvalues coincide (critical damping)."],
      demo: { scene: "joint", set: { kp: 100, kd: 20 }, press: ["start"], wait: 2 } },
    { id: "zeta", robot: true, text: ["关节场景：K_p ≥ 50，调出阻尼比 ζ = 0.7 左右（0.65～0.75）的稳定焦点，读出超调量。", "Joint: with K_p ≥ 50 make a stable focus with damping ratio near 0.7 (0.65–0.75) and read the overshoot."],
      demo: { scene: "joint", set: { kp: 100, kd: 14 }, press: ["start"], wait: 2 } },
    { id: "saddle", robot: true, text: ["倒立摆场景：取 K_p = 10，看相图是什么类型，释放后会怎样。", "Inverted pendulum: set K_p = 10. What type is the portrait, and what happens after release?"],
      demo: { scene: "inv", set: { kp: 10, kd: 4 }, press: ["start"], wait: 2 } },
    { id: "inv", robot: true, text: ["倒立摆场景：调增益让它立住，且两个特征值的实部都小于 −2。", "Inverted pendulum: tune the gains so it stays up with both eigenvalues' real parts below −2."],
      demo: { scene: "inv", set: { kp: 80, kd: 10 }, press: ["start"], wait: 3 } },
  ],
  think: ["二阶系统 A = [[0, 1], [−q, −p]] 稳定的条件是 p > 0 且 q > 0。用 tr A 与 det A 说明，并解释为什么倒立摆的 K_p 必须超过 29.43。", "The system A = [[0, 1], [−q, −p]] is stable iff p > 0 and q > 0. Explain with tr A and det A, and say why the inverted pendulum needs K_p above 29.43."],

  a: { joint: 0, inv: 29.43 },
  sys(api) {
    const a = this.a[api.scene], q = api.p.kp - a, p = api.p.kd;   // θ̈ + pθ̇ + qθ = 0
    const tr = -p, det = q, disc = tr * tr - 4 * det;
    let ev, kind;
    if (disc >= 0) { const r = Math.sqrt(disc); ev = [{ re: (tr - r) / 2, im: 0 }, { re: (tr + r) / 2, im: 0 }]; }
    else { const r = Math.sqrt(-disc) / 2; ev = [{ re: tr / 2, im: -r }, { re: tr / 2, im: r }]; }
    if (det < -1e-9) kind = ["鞍点（不稳定）", "saddle (unstable)"];
    else if (Math.abs(det) <= 1e-9) kind = ["退化（有零特征值）", "degenerate (a zero eigenvalue)"];
    else if (Math.abs(tr) < 1e-9) kind = ["中心（不收敛也不发散）", "center (neither converges nor diverges)"];
    else if (disc < 0) kind = tr < 0 ? ["稳定焦点", "stable focus"] : ["不稳定焦点", "unstable focus"];
    else if (Math.abs(disc) < 1e-9) kind = tr < 0 ? ["稳定（重特征值，临界阻尼）", "stable (repeated eigenvalue, critical damping)"] : ["不稳定（重特征值）", "unstable (repeated eigenvalue)"];
    else kind = tr < 0 ? ["稳定结点", "stable node"] : ["不稳定结点", "unstable node"];
    return { p, q, tr, det, disc, ev, kind, A: [[0, 1], [-q, -p]] };
  },
  // x(t) = e^{At}x₀ for A = [[0, 1], [−q, −p]] via e^{At} = e^{αt}[cosh/cos…] (closed form, all cases)
  flow(S, x0, t) {
    const al = S.tr / 2, d = S.disc / 4, I = [[1, 0], [0, 1]], B = [[-al, 1], [-S.q, -S.p - al]];   // A = αI + B, B² = d·I
    let c, s;
    if (d > 1e-12) { const r = Math.sqrt(d); c = Math.cosh(r * t); s = Math.sinh(r * t) / r; }
    else if (d < -1e-12) { const r = Math.sqrt(-d); c = Math.cos(r * t); s = Math.sin(r * t) / r; }
    else { c = 1; s = t; }
    const e = Math.exp(al * t), E = [[e * (c * I[0][0] + s * B[0][0]), e * (c * I[0][1] + s * B[0][1])], [e * (c * I[1][0] + s * B[1][0]), e * (c * I[1][1] + s * B[1][1])]];
    return [E[0][0] * x0[0] + E[0][1] * x0[1], E[1][0] * x0[0] + E[1][1] * x0[1]];
  },
  reset(api, s) { s.S = this.sys(api); s.trace = []; s.x = [1, 0]; s.th = []; s.peak = 0; s.stopped = false; },
  start(api, s) { s.x = [1, 0]; s.trace = [[1, 0]]; s.th = [[0, 1]]; s.peak = -Infinity; },
  update(dt, api, s) {
    s.S = this.sys(api);
    const x = this.flow(s.S, [1, 0], api.t);
    s.x = x; s.trace.push(x); s.th.push([api.t, x[0]]);
    if (api.t > 0.05) s.peak = Math.max(s.peak, -x[0]);    // overshoot below zero after release from θ = 1
    if (api.t > 4 || Math.abs(x[0]) > 5) api.stop();
  },
  readouts(api, s) {
    const S = this.sys(api); s.S = S;
    const f = api.fmt, ev = S.ev.map((z) => Math.abs(z.im) < 1e-9 ? f(z.re, 2) : f(z.re, 2) + (z.im > 0 ? " + " : " − ") + f(Math.abs(z.im), 2) + "i").join(", ");
    const zeta = S.q > 0 ? S.p / (2 * Math.sqrt(S.q)) : NaN, stable = S.ev.every((z) => z.re < 0);
    if (api.scene === "joint" && S.p === 0 && S.q > 0) api.done("center");
    if (api.scene === "joint" && api.p.kp === 100 && Math.abs(S.disc) < 1e-6) api.done("crit");
    if (api.scene === "joint" && api.p.kp >= 50 && zeta >= 0.65 && zeta <= 0.75) api.done("zeta");
    if (api.scene === "inv" && api.p.kp === 10 && S.det < 0) api.done("saddle");
    if (api.scene === "inv" && stable && S.ev.every((z) => z.re < -2)) api.done("inv");
    const rows = [[["系统矩阵 A", "System matrix A"], "[[0, 1], [" + f(-S.q, 2) + ", " + f(-S.p, 2) + "]]"],
                  [["迹 tr A、行列式 det A", "tr A, det A"], f(S.tr, 2) + ", " + f(S.det, 2)],
                  [["特征值", "Eigenvalues"], ev],
                  [["相图类型", "Portrait type"], api.T(S.kind[0], S.kind[1])],
                  [["阻尼比 ζ", "Damping ratio ζ"], isFinite(zeta) ? f(zeta, 3) : "—"],
                  [["衰减到 2% 的时间 ≈ 4/|Re λ|（取最慢的）", "Settling time ≈ 4/|Re λ| (slowest)"], stable ? f(4 / Math.min(...S.ev.map((z) => -z.re)), 2) + " s" : "—"]];
    if (isFinite(s.peak) && s.th && s.th.length > 2) rows.push([["超调量（θ 过零后的最大反向值）", "Overshoot (largest swing past zero)"], f(Math.max(0, s.peak) * 100, 1) + "%"]);
    return rows;
  },
  draw(api, s) {
    const S = this.sys(api), { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink"), ctx = api.ctx;
    const stable = S.ev.every((z) => z.re < 0), col = stable ? api.css("--green") : (Math.abs(S.tr) < 1e-9 && S.det > 0 ? api.css("--amber") : api.css("--red"));
    // left: phase plane θ ∈ [−1.5, 1.5], ω scaled to fit
    const R = Math.min(w * 0.55, h) - 30, x0 = 20, y0 = (h - R) / 2, L = 1.5, Wm = Math.max(4, Math.sqrt(Math.max(Math.abs(S.q), 1)) * 1.6);
    const X = (th) => x0 + R * (th + L) / (2 * L), Y = (om) => y0 + R * (Wm - om) / (2 * Wm);
    api.rect(x0, y0, R, R, null, mu);
    api.line(X(-L), Y(0), X(L), Y(0), mu, 1); api.line(X(0), Y(-Wm), X(0), Y(Wm), mu, 1);
    for (let i = -6; i <= 6; i++) for (let j = -6; j <= 6; j++) {     // direction field
      const th = L * i / 6.5, om = Wm * j / 6.5, d = [om, -S.q * th - S.p * om], n = Math.hypot(d[0] / L, d[1] / Wm) || 1;
      const sx = 9 * d[0] / L / n, sy = 9 * d[1] / Wm / n;
      api.line(X(th), Y(om), X(th) + sx, Y(om) - sy, mu, 1);
    }
    for (let k = 0; k < 10; k++) {                                     // trajectories from a ring of starts
      const a = 2 * Math.PI * k / 10, st = [0.9 * L * Math.cos(a), 0.9 * Wm * Math.sin(a)];
      ctx.beginPath();
      for (let i = 0; i <= 160; i++) { const p = this.flow(S, st, 4 * i / 160); if (Math.abs(p[0]) > L * 1.05 || Math.abs(p[1]) > Wm * 1.05) break;
        i ? ctx.lineTo(X(p[0]), Y(p[1])) : ctx.moveTo(X(p[0]), Y(p[1])); }
      ctx.strokeStyle = col; ctx.globalAlpha = 0.55; ctx.lineWidth = 1.5; ctx.stroke(); ctx.globalAlpha = 1;
    }
    if (S.disc > 1e-9) S.ev.forEach((z) => {                          // eigenvector lines (1, λ)
      const v = [1, z.re], n = Math.hypot(v[0] / L, v[1] / Wm);
      api.line(X(-v[0] / n), Y(-v[1] / n), X(v[0] / n), Y(v[1] / n), api.css("--amber"), 1.5, [5, 4]);
    });
    if (s.trace && s.trace.length > 1) {
      ctx.beginPath(); s.trace.forEach(([a, b], i) => { const cl = (z, m) => Math.max(-m, Math.min(m, z)); i ? ctx.lineTo(X(cl(a, L)), Y(cl(b, Wm))) : ctx.moveTo(X(cl(a, L)), Y(cl(b, Wm))); });
      ctx.strokeStyle = api.css("--blue"); ctx.lineWidth = 3; ctx.stroke();
      const p = s.trace[s.trace.length - 1]; if (Math.abs(p[0]) <= L && Math.abs(p[1]) <= Wm) api.circle(X(p[0]), Y(p[1]), 6, api.css("--blue"));
    }
    api.label(api.T("相平面：横轴 θ，纵轴 ω = θ̇", "phase plane: θ across, ω = θ̇ up"), x0, y0 - 6, mu, 12);
    // right top: eigenvalues in the complex plane
    const cx0 = x0 + R + 30, cw = w - cx0 - 15, ch = h * 0.45, ccx = cx0 + cw * 0.7, ccy = 20 + ch / 2;
    const sc = Math.min(cw * 0.65, ch / 2) / Math.max(5, ...S.ev.map((z) => Math.hypot(z.re, z.im)));
    ctx.globalAlpha = 0.12; api.rect(cx0, 20, ccx - cx0, ch, api.css("--green")); ctx.globalAlpha = 1;
    api.line(cx0, ccy, cx0 + cw, ccy, mu, 1); api.line(ccx, 20, ccx, 20 + ch, mu, 1);
    S.ev.forEach((z) => api.circle(Math.max(cx0, Math.min(cx0 + cw, ccx + sc * z.re)), ccy - sc * z.im, 6, col));
    api.label(api.T("复平面上的特征值（绿区：Re λ < 0）", "eigenvalues (green: Re λ < 0)"), cx0, 14, mu, 11);
    // right bottom: θ(t)
    const ty = 20 + ch + 30, th_h = h - ty - 20, T_ = (t) => cx0 + cw * t / 4, Th = (v) => ty + th_h / 2 - th_h / 2 * Math.max(-1.5, Math.min(1.5, v)) / 1.5;
    api.line(cx0, Th(0), cx0 + cw, Th(0), mu, 1);
    ctx.beginPath(); for (let i = 0; i <= 200; i++) { const t = 4 * i / 200, v = this.flow(S, [1, 0], t)[0]; i ? ctx.lineTo(T_(t), Th(v)) : ctx.moveTo(T_(t), Th(v)); }
    ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.stroke();
    api.label(api.T("θ(t)，从 θ = 1 释放，0～4 s", "θ(t) released from θ = 1, 0–4 s"), cx0, ty - 6, mu, 11);
  },
});
