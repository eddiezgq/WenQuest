// 实验 13.5 采样 PD 控制的特征值（配 13.5～13.7 节）。单位惯量的关节 θ̈ = u，PD 控制 u = −K_p θ − K_d ω，采样周期 T = 0.05 s，
// 前向欧拉离散化：x_{k+1} = A x_k，x = (θ, ω)，A = [[1, T], [−K_p T, 1 − K_d T]]。特征多项式 λ² − (2 − K_d T)λ + (1 − K_d T + K_p T²)。
// 左：复平面上的两个特征值与单位圆；右：从 θ₀ = 1、ω₀ = 0 出发的 θₖ（60 步，3 s）。
WQ.lab({
  title: ["实验 13.5 采样控制的特征值", "Lab 13.5 Eigenvalues of a sampled controller"],
  goal: ["调整 PD 增益，看离散系统矩阵 A 的特征值在复平面上怎样移动，把特征值的位置与关节角的响应（收敛、振荡、发散、两步归零）对应起来。",
         "Tune the PD gains, watch the eigenvalues of the discrete system matrix A move in the complex plane, and match their position with the joint response (converging, oscillating, diverging, zero in two steps)."],
  scenes: [
    { id: "pd", robot: true, name: ["关节 PD 控制", "Joint PD control"],
      problem: { title: ["每 0.05 s 算一次控制量的关节", "A joint whose controller runs every 0.05 s"],
                 text: ["控制器每个周期读一次角度和角速度，算出力矩。整个闭环就是 x_{k+1} = A x_k，第 k 步的状态是 Aᵏx₀：A 的特征值决定了关节怎样回到零位。",
                        "Each period the controller reads the angle and speed and computes a torque. The closed loop is x_{k+1} = A x_k and step k is Aᵏx₀: the eigenvalues of A decide how the joint returns to zero."] } },
  ],
  params: [
    { id: "kp", name: ["比例增益 K_p", "Proportional gain K_p"], min: 0, max: 1000, step: 10, value: 50, unit: "1/s²", digits: 0 },
    { id: "kd", name: ["微分增益 K_d", "Derivative gain K_d"], min: 0, max: 60, step: 1, value: 6, unit: "1/s", digits: 0 },
  ],
  buttons: [],
  tasks: [
    { id: "osc", robot: true, text: ["调出一对复特征值，模小于 0.9：关节振荡着回到零位。读出每步转过的角度和振荡一周的步数。", "Get a complex pair of modulus below 0.9: the joint oscillates back to zero. Read the angle turned per step and the steps per oscillation."],
      demo: { scene: "pd", set: { kp: 100, kd: 10 }, press: [] } },
    { id: "unst", robot: true, text: ["保持 K_p = 100，减小 K_d，使特征值跑出单位圆（模大于 1），观察发散。连续时间的 PD 控制在这组增益下是稳定的，问题出在哪里？", "Keep K_p = 100 and lower K_d until the eigenvalues leave the unit circle (modulus above 1); watch the divergence. Continuous PD control is stable with these gains: what went wrong?"],
      demo: { scene: "pd", set: { kp: 100, kd: 4 }, press: [] } },
    { id: "crit", robot: true, text: ["找出使两个特征值重合为同一个正实数的增益（临界阻尼，K_p = K_d²/4）：在不振荡的响应中回零最快。", "Find gains that make the two eigenvalues coincide at one positive real number (critical damping, K_p = K_d²/4): the fastest return among non-oscillating responses."],
      demo: { scene: "pd", set: { kp: 100, kd: 20 }, press: [] } },
    { id: "dead", robot: true, text: ["把两个特征值都放到 0（无差拍）：关节两步就回到零位。读出这时的 A²。", "Put both eigenvalues at 0 (deadbeat): the joint is back at zero after two steps. Read A² then."],
      demo: { scene: "pd", set: { kp: 400, kd: 40 }, press: [] } },
  ],
  think: ["无差拍控制两步就归零，为什么实际的关节很少这样调？（提示：看看第一步的角速度和力矩有多大。）", "Deadbeat control is back at zero in two steps; why are real joints rarely tuned this way? (Hint: look at the speed and torque in the first step.)"],

  T: 0.05,
  reset(api, s) {
    const T = this.T, kp = api.p.kp, kd = api.p.kd;
    s.A = [[1, T], [-kp * T, 1 - kd * T]];
    const tr = 2 - kd * T, det = 1 - kd * T + kp * T * T, disc = tr * tr / 4 - det;
    s.tr = tr; s.det = det; s.disc = disc;
    if (disc >= 0) { const r = Math.sqrt(disc); s.ev = [[tr / 2 + r, 0], [tr / 2 - r, 0]]; }
    else { const im = Math.sqrt(-disc); s.ev = [[tr / 2, im], [tr / 2, -im]]; }
    s.rho = Math.max(...s.ev.map((z) => Math.hypot(z[0], z[1])));
    let x = [1, 0]; s.th = [1]; s.om = [0]; s.u = [];
    for (let k = 0; k < 60; k++) { s.u.push(-kp * x[0] - kd * x[1]); x = [x[0] + T * x[1], -kp * T * x[0] + (1 - kd * T) * x[1]]; s.th.push(x[0]); s.om.push(x[1]); }
    s.settle = -1;
    for (let k = 0; k <= 60; k++) { if (s.th.slice(k).every((t) => Math.abs(t) < 0.01)) { s.settle = k; break; } }
    const A = s.A; s.A2 = [[A[0][0] * A[0][0] + A[0][1] * A[1][0], A[0][0] * A[0][1] + A[0][1] * A[1][1]], [A[1][0] * A[0][0] + A[1][1] * A[1][0], A[1][0] * A[0][1] + A[1][1] * A[1][1]]];
  },
  readouts(api, s) {
    if (!s.A) return [];
    const f = api.fmt, cplx = s.disc < -1e-12, dbl = Math.abs(s.disc) <= 1e-12;
    if (cplx && s.rho < 0.9) api.done("osc");
    if (api.p.kp === 100 && s.rho > 1) api.done("unst");
    if (dbl && s.rho > 0.01 && s.rho < 1 && s.ev[0][0] > 0) api.done("crit");
    if (Math.abs(s.tr) < 1e-9 && Math.abs(s.det) < 1e-9) api.done("dead");
    const zs = s.ev.map((z) => (Math.abs(z[1]) < 1e-12 ? f(z[0], 3) : f(z[0], 3) + (z[1] > 0 ? " + " : " − ") + f(Math.abs(z[1]), 3) + "i"));
    const rows = [[["A", "A"], "[[1, " + f(this.T, 2) + "], [" + f(s.A[1][0], 2) + ", " + f(s.A[1][1], 2) + "]]"],
                  [["特征多项式 λ² − tλ + d：t, d", "Characteristic polynomial λ² − tλ + d: t, d"], f(s.tr, 3) + ", " + f(s.det, 4)],
                  [["特征值", "Eigenvalues"], cplx ? zs.join(", ") : (dbl ? api.T("二重 ", "double ") + zs[0] : zs.join(", "))],
                  [["最大的模 ρ", "Largest modulus ρ"], f(s.rho, 4) + (s.rho > 1 ? api.T("（发散）", " (diverges)") : "")]];
    if (cplx) { const a = Math.atan2(s.ev[0][1], s.ev[0][0]) * 180 / Math.PI; rows.push([["每步转过的角度；一周的步数", "Angle per step; steps per cycle"], f(a, 1) + "°; " + f(360 / a, 1)]); }
    rows.push([["|θ| 稳定在 0.01 以内所需步数", "Steps until |θ| stays below 0.01"], s.settle < 0 ? api.T("60 步内未达到", "not within 60") : String(s.settle)]);
    rows.push([["第一步的控制力矩 u₀", "Control torque in step 0, u₀"], f(s.u[0], 0)]);
    rows.push([["A²", "A²"], "[[" + s.A2[0].map((t) => f(t, 3)).join(", ") + "], [" + s.A2[1].map((t) => f(t, 2)).join(", ") + "]]"]);
    return rows;
  },
  draw(api, s) {
    if (!s.A) return;
    const { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink");
    const R = Math.min(w * 0.4, h) * 0.3, cx = R * 1.5 + 10, cy = h / 2;
    api.line(cx - 1.45 * R, cy, cx + 1.45 * R, cy, mu, 1); api.line(cx, cy - 1.45 * R, cx, cy + 1.45 * R, mu, 1);
    const c = api.ctx; c.beginPath(); c.arc(cx, cy, R, 0, 2 * Math.PI); c.strokeStyle = mu; c.lineWidth = 1.5; c.stroke();
    api.label(api.T("单位圆", "unit circle"), cx - R, cy - R - 6, mu, 11);
    api.label("Re", cx + 1.45 * R - 16, cy + 16, mu, 11); api.label("Im", cx + 6, cy - 1.45 * R + 10, mu, 11);
    const col = s.rho > 1 ? api.css("--red") : api.css("--blue");
    s.ev.forEach((z, i) => { const x = cx + R * Math.max(-1.4, Math.min(1.4, z[0])), y = cy - R * Math.max(-1.4, Math.min(1.4, z[1])) + (Math.abs(s.disc) <= 1e-12 ? (i ? 5 : -5) : 0); api.circle(x, y, 6, col, ink); });
    const px = cx + 1.6 * R + 30, pw = w - px - 20, py = 30, ph = h - 70, top = 1.6;
    api.rect(px, py, pw, ph, null, api.css("--grid"));
    const X = (k) => px + pw * k / 60, Y = (v) => py + ph / 2 - Math.max(-top, Math.min(top, v)) / top * (ph / 2 - 4);
    api.line(px, Y(0), px + pw, Y(0), mu, 1);
    for (let k = 1; k <= 60; k++) api.line(X(k - 1), Y(s.th[k - 1]), X(k), Y(s.th[k]), col, 2);
    s.th.forEach((t, k) => api.circle(X(k), Y(t), 2.2, col, null));
    api.label(api.T("θₖ（60 步 = 3 s）", "θₖ (60 steps = 3 s)"), px, py - 8, mu, 12);
    api.label("1", px - 8, Y(1) + 4, mu, 11, "right"); api.label("0", px - 8, Y(0) + 4, mu, 11, "right"); api.label("−1", px - 8, Y(-1) + 4, mu, 11, "right");
  },
});
