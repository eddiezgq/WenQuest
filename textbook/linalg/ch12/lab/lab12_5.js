// 实验 12.5 柔性关节的振型与质量矩阵内积下的正交（配 12.5.3 节）。电机侧转动惯量 J_m、连杆侧 J_l，减速器扭转刚度 k，
// 位置控制器的等效刚度 k_p = 6×10⁴ N·m/rad。M = diag(J_m, J_l)，K = [[k_p + k, −k], [−k, k]]，A = M⁻¹K 在 M-内积下自伴。
// 初始状态：电机与连杆偏转 q₀ = (cos θ₀, sin θ₀) mrad，静止释放；自由振动 q(t) = Σ c_j v_j cos ω_j t，c_j = ⟨v_j, q₀⟩_M / ⟨v_j, v_j⟩_M。
// 播放时把时间放慢 50 倍（屏幕上 1 s 相当于 20 ms），转角放大显示。
WQ.lab({
  title: ["实验 12.5 柔性关节的振型", "Lab 12.5 Vibration modes of a flexible joint"],
  goal: ["改变转动惯量与刚度，求柔性关节的固有频率与振型，检验振型在质量矩阵的内积下正交而在点积下一般不正交；用 M-内积把初始偏转分解到振型上，让关节只按一个振型振动。",
         "Vary the inertias and the stiffness, find the natural frequencies and modes of a flexible joint, and check that the modes are orthogonal in the mass-matrix inner product but in general not in the dot product; split the initial offset onto the modes with the M-inner product and make the joint vibrate in one mode only."],
  scenes: [
    { id: "joint", name: ["柔性关节", "Flexible joint"],
      problem: { title: ["急停后连杆为什么抖", "Why the link shakes after a sudden stop"],
                 text: ["谐波减速器有弹性，电机与连杆之间像隔着一根扭转弹簧。自由振动 M q̈ + K q = 0，A = M⁻¹K 不对称，可它的特征值是正实数、振型在 M-内积下正交。按“播放”看振动。",
                        "The harmonic drive is elastic, like a torsion spring between motor and link. Free vibration M q̈ + K q = 0: A = M⁻¹K is not symmetric, yet its eigenvalues are positive and its modes are M-orthogonal. Press Play to watch."] } },
  ],
  params: [
    { id: "Jm", name: ["电机侧转动惯量 J_m", "Motor-side inertia J_m"], min: 0.5, max: 4, step: 0.5, value: 2, unit: "kg·m²", digits: 1 },
    { id: "Jl", name: ["连杆侧转动惯量 J_l", "Link-side inertia J_l"], min: 0.5, max: 4, step: 0.5, value: 1, unit: "kg·m²", digits: 1 },
    { id: "k", name: ["减速器扭转刚度 k（×10⁴）", "Gear stiffness k (×10⁴)"], min: 1, max: 6, step: 0.5, value: 3, unit: "N·m/rad", digits: 1 },
    { id: "th", name: ["初始偏转的方向 θ₀：q₀ = (cos θ₀, sin θ₀) mrad", "Direction θ₀ of the initial offset: q₀ = (cos θ₀, sin θ₀) mrad"], min: -90, max: 90, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["播放", "Play"], primary: true }, { id: "reset", name: ["回到初始", "Back to start"] }],
  tasks: [
    { id: "mode1", text: ["取 J_m = 2、J_l = 1、k = 3×10⁴，调整 θ₀ 使关节只按第一振型振动（第二振型的系数不到第一振型的 2%），播放观察。", "With J_m = 2, J_l = 1, k = 3×10⁴ choose θ₀ so that the joint vibrates in the first mode only (the second coefficient is below 2% of the first), and play it."],
      demo: { scene: "joint", set: { Jm: 2, Jl: 1, k: 3, th: 63 }, press: ["start"], wait: 2 } },
    { id: "mode2", text: ["同样的参数下，使关节只按第二振型振动，播放观察，读出它的频率。", "With the same parameters make the joint vibrate in the second mode only, play it and read its frequency."],
      demo: { scene: "joint", set: { Jm: 2, Jl: 1, k: 3, th: -45 }, press: ["start"], wait: 2 } },
    { id: "ortho", text: ["改变两个转动惯量，使两个振型在普通点积下也正交（夹角 90°）。这时质量矩阵是什么样的？", "Change the two inertias until the modes are orthogonal in the ordinary dot product as well (90° apart). What does the mass matrix look like then?"],
      demo: { scene: "joint", set: { Jm: 1, Jl: 1, k: 3, th: 0 }, press: [] } },
  ],
  think: ["把电机侧初始偏转 1 mrad（θ₀ = 0°）分解到两个振型上时，若误用点积公式 vⱼᵀq₀ / vⱼᵀvⱼ，系数是多少？两个振型按这样的系数叠加，还原得出 q₀ 吗？",
          "If the dot-product formula vⱼᵀq₀ / vⱼᵀvⱼ is used by mistake to split a 1 mrad motor offset (θ₀ = 0°), what are the coefficients? Do the two modes with these coefficients add back to q₀?"],

  kp: 6.0e4,
  reset(api, s) {
    const Jm = api.p.Jm, Jl = api.p.Jl, k = api.p.k * 1e4, kp = this.kp;
    const a = (kp + k) / Jm, b = -k / Jm, c = -k / Jl, d = k / Jl;   // A = M⁻¹K
    const tr = a + d, det = a * d - b * c, disc = Math.sqrt(tr * tr - 4 * det);
    s.lam = [(tr - disc) / 2, (tr + disc) / 2];
    s.w = s.lam.map(Math.sqrt);
    s.V = s.lam.map((l) => [1, (l - a) / b]);   // first component 1
    s.M = [Jm, Jl];
    const ipM = (u, v) => Jm * u[0] * v[0] + Jl * u[1] * v[1];
    s.ipM = ipM;
    const th = api.p.th * Math.PI / 180;
    s.q0 = [Math.cos(th), Math.sin(th)];
    s.c = s.V.map((v) => ipM(v, s.q0) / ipM(v, v));
    s.dot = s.V[0][0] * s.V[1][0] + s.V[0][1] * s.V[1][1];
    s.dotM = ipM(s.V[0], s.V[1]);
    s.cosE = s.dot / Math.hypot(...s.V[0]) / Math.hypot(...s.V[1]);
    s.ts = 0; s.played = false;
  },
  q(s, t) { return [0, 1].map((i) => s.c[0] * s.V[0][i] * Math.cos(s.w[0] * t) + s.c[1] * s.V[1][i] * Math.cos(s.w[1] * t)); },
  start(api, s) { s.played = true; },
  update(dt, api, s) {
    s.ts = api.t / 50;
    if (s.ts >= 0.2) { s.ts = 0.2; api.stop(); }
  },
  readouts(api, s) {
    if (!s.V) return [];
    const f = api.fmt, hz = s.w.map((x) => x / (2 * Math.PI));
    const big = Math.max(Math.abs(s.c[0]), Math.abs(s.c[1]));
    const sameP = api.p.Jm === 2 && api.p.Jl === 1 && api.p.k === 3;
    if (sameP && s.played && Math.abs(s.c[1]) < 0.02 * Math.abs(s.c[0])) api.done("mode1");
    if (sameP && s.played && Math.abs(s.c[0]) < 0.02 * Math.abs(s.c[1])) api.done("mode2");
    if (Math.abs(s.cosE) < 1e-9) api.done("ortho");
    const v = (x) => "(" + x.map((t) => f(t, 3)).join(", ") + ")";
    return [[["固有频率 f₁, f₂", "Natural frequencies f₁, f₂"], f(hz[0], 1) + " Hz, " + f(hz[1], 1) + " Hz"],
            [["振型 v₁, v₂", "Modes v₁, v₂"], v(s.V[0]) + ", " + v(s.V[1])],
            [["点积 v₁·v₂（夹角）", "Dot product v₁·v₂ (angle)"], f(s.dot, 3) + "（" + f(Math.acos(Math.max(-1, Math.min(1, s.cosE))) * 180 / Math.PI, 1) + "°）"],
            [["M-内积 v₁ᵀMv₂", "M-inner product v₁ᵀMv₂"], Math.abs(s.dotM) < 1e-12 ? "0" : s.dotM.toExponential(1)],
            [["初始偏转 q₀ / mrad", "Initial offset q₀ / mrad"], v(s.q0)],
            [["振型系数 c₁, c₂（M-内积）", "Mode coefficients c₁, c₂ (M-inner product)"], f(s.c[0], 4) + ", " + f(s.c[1], 4)],
            [["c₂ / c₁", "c₂ / c₁"], Math.abs(s.c[0]) < 1e-12 ? "—" : f(s.c[1] / s.c[0], 3)],
            [["时间（放慢 50 倍）", "Time (slowed 50×)"], f(1000 * s.ts, 1) + " ms"]];
  },
  draw(api, s) {
    if (!s.V) return;
    const { w, h } = api, ink = api.css("--ink"), mu = api.css("--muted"), blue = api.css("--blue"), acc = api.css("--amber");
    const q = this.q(s, s.ts), amp = 0.45;   // rad of drawing per mrad
    const cy = 90, x1 = w * 0.22, x2 = w * 0.62, r1 = 18 + 12 * Math.sqrt(s.M[0]), r2 = 18 + 12 * Math.sqrt(s.M[1]);
    // wall and springs
    api.rect(20, cy - 40, 10, 80, mu);
    const spring = (xa, xb) => { const n = 8; let px = xa, py = cy;
      for (let i = 1; i <= 2 * n; i++) { const x = xa + (xb - xa) * i / (2 * n), y = i === 2 * n ? cy : cy + (i % 2 ? -8 : 8); api.line(px, py, x, y, ink, 1.5); px = x; py = y; } };
    spring(30, x1 - r1); spring(x1 + r1, x2 - r2);
    api.label("k_p", (30 + x1 - r1) / 2, cy - 16, ink, 12, "center"); api.label("k", (x1 + r1 + x2 - r2) / 2, cy - 16, ink, 12, "center");
    [[x1, r1, q[0], blue, api.T("电机 J_m", "motor J_m")], [x2, r2, q[1], acc, api.T("连杆 J_l", "link J_l")]].forEach(([x, r, a, col, name]) => {
      api.circle(x, cy, r, col + "55", col);
      const t = -Math.PI / 2 + amp * a;
      api.line(x, cy, x + r * Math.cos(t), cy + r * Math.sin(t), ink, 3);
      api.label(name, x, cy + r + 18, ink, 12, "center");
    });
    api.label(api.T("转角放大显示", "angles exaggerated"), w - 12, 20, mu, 11, "right");
    // time traces
    const px = 50, py = 170, pw = w - 80, ph = h - py - 40, T = 0.2;
    const top = 1.1 * Math.max(1, ...[0, 1].map((i) => Math.abs(s.c[0] * s.V[0][i]) + Math.abs(s.c[1] * s.V[1][i])));
    api.rect(px, py, pw, ph, null, api.css("--grid"));
    api.line(px, py + ph / 2, px + pw, py + ph / 2, mu, 1);
    const X = (t) => px + pw * t / T, Y = (v) => py + ph / 2 - v / top * (ph / 2 - 6);
    [[0, blue], [1, acc]].forEach(([i, col]) => {
      let prev = null;
      const n = 400;
      for (let j = 0; j <= n; j++) { const t = T * j / n; if (t > s.ts + 1e-12 && s.played) break; const p = [X(t), Y(this.q(s, t)[i])];
        if (prev) api.line(prev[0], prev[1], p[0], p[1], col, 1.8); prev = p; }
    });
    api.label(api.T("转角 / mrad（蓝：电机，黄：连杆）", "angle / mrad (blue: motor, yellow: link)"), px, py - 8, mu, 12);
    api.label("0", px - 8, Y(0) + 4, mu, 11, "right"); api.label("1", px - 8, Y(1) + 4, mu, 11, "right"); api.label("−1", px - 8, Y(-1) + 4, mu, 11, "right");
    api.label(api.T("0.2 s（放慢后 10 s）", "0.2 s (10 s slowed)"), px + pw, py + ph + 16, mu, 11, "right");
  },
});
