// 实验 31.2 手臂的振动（配 31.5 节）。
// 场景“WQ-CR5 手臂”：侧视平面模型，广义坐标是 J2、J3 两个关节的小转角；关节是扭簧（谐波减速器的扭转刚度，零件库 D-RDC-HD-CSF：
//   32 号 K1 6.7、K3 12；25 号 K1 3.1、K3 5.7，×10⁴ N·m/rad），连杆、手腕当作刚体（J4–J6 不转、铝管不弯，所以频率比 31.5 节的六关节模型高一些）。
//   质量（kg，与 wqcr5.py 的零件相同）：大臂铝管 0.886（沿管均布）+ 罩壳 0.3（中点）；J3 模组 2.0（肘部）；小臂铝管 0.660（均布）+ 罩壳 0.2（中点）；
//   J4 模组 1.2、J5 模组 + 连接件 1.4（腕部点）；连接件 0.2（再外 0.05 m）；J6 模组 1.2、法兰 0.35（再外 0.10 m）；负载在 TCP（再外 0.10 m、低 0.19 m）。
//   手臂伸出的远近：大臂抬起 α、小臂折回 2α（与程序 ex31_5.py 相同），手腕保持工具朝下。
//   质量矩阵 M_ab = Σ m_i (e_a × r_i)·(e_b × r_i)（平面里绕 J2、J3 转动时各质点的速度）；K = diag(K_J2, K_J3)；det(K − ω²M) = 0。
//   “敲一下”：TCP 受一个向下的冲量 1 N·s，按振型叠加、每阶阻尼比 ζ 衰减。
// 场景“跳水板”：板是悬臂弹簧 k = 3EI/L³（EI = 1.057×10⁵ N·m²，示例值：长 4.8 m、站 60 kg 时约 1.1 Hz），人是板端的质量（板自重折算 0.2357 m_板，板 25 kg）。
WQ.lab({
  title: ["实验 31.2 手臂的振动", "Lab 31.2 The vibrating arm"],
  goal: ["改负载、关节刚度、阻尼和手臂伸出的远近，敲一下伸直的手臂，看它以什么频率振动、多久停下来；体会 31.5 节“频率由关节刚度和负载决定”。",
         "Change the payload, joint stiffness, damping and reach, then knock the arm and see at what frequency it vibrates and how soon it settles — Section 31.5's “joint stiffness and payload set the frequency”."],
  scenes: [
    { id: "arm", robot: true, name: ["WQ-CR5 手臂", "WQ-CR5 arm"], hide: ["bl", "bm"],
      problem: { title: ["机器人问题：停下来以后还在晃", "Robot problem: still shaking after it stops"],
                 text: ["机器人带着 5 kg 伸直到位，末端还要晃一会儿才稳。它晃多快、晃多久？换更硬的减速器能好多少？",
                        "Arriving outstretched with 5 kg, the tip keeps shaking for a while. How fast, how long? How much does a stiffer gear help?"] } },
    { id: "board", name: ["跳水板", "A springboard"], hide: ["mp", "kj", "k2x", "zeta", "fold"],
      problem: { title: ["生活中的例子：跳水板的节奏", "Everyday example: the springboard's rhythm"],
                 text: ["运动员站在板端一压一放，板子上下弹。人越重、站得越靠外，弹得越慢。教练希望板的节奏在 1 Hz 左右。",
                        "A diver bounces at the end of the board. Heavier divers and longer boards bounce slower. The coach wants about 1 Hz."] } },
  ],
  buttons: [{ id: "start", name: ["敲一下", "Knock"], primary: true }, { id: "reset", name: ["停住", "Stop"] }],
  params: [
    { id: "mp", name: ["负载", "Payload"], min: 0, max: 8, step: 0.5, value: 5, unit: "kg", digits: 1 },
    { id: "kj", name: ["关节刚度：0 按 K1（最软）/ 1 按 K3（最硬）", "Joint stiffness: 0 K1 (softest) / 1 K3 (stiffest)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "k2x", name: ["J2 减速器刚度的倍数", "J2 gear stiffness multiplier"], min: 0.5, max: 3, step: 0.1, value: 1, unit: "×", digits: 1 },
    { id: "zeta", name: ["阻尼比 ζ", "Damping ratio ζ"], min: 0.005, max: 0.2, step: 0.005, value: 0.02, unit: "", digits: 3 },
    { id: "fold", name: ["手臂收回：大臂抬起角 α", "Fold: upper-arm raise α"], min: 0, max: 60, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "bl", name: ["板长", "Board length"], min: 3, max: 5.5, step: 0.1, value: 4.8, unit: "m", digits: 1 },
    { id: "bm", name: ["人的体重", "Diver's mass"], min: 30, max: 100, step: 1, value: 60, unit: "kg", digits: 0 },
  ],
  tasks: [
    { id: "std", robot: true, text: ["标准参数（5 kg、K1、ζ = 0.02、伸直）：敲一下，读出第一阶固有频率和第一阶振型。",
                                     "Standard settings (5 kg, K1, ζ = 0.02, outstretched): knock and read the first natural frequency and mode shape."],
      demo: { scene: "arm", set: { mp: 5, kj: 0, k2x: 1, zeta: 0.02, fold: 0 }, press: ["start"] } },
    { id: "empty", robot: true, text: ["负载改为 0（其余标准）：第一阶频率升到多少？与 5 kg 时比，是质量比的平方根吗？",
                                       "Payload 0 (otherwise standard): what is the first frequency now? Is the ratio the square root of the mass ratio?"],
      demo: { scene: "arm", set: { mp: 0, kj: 0, k2x: 1, zeta: 0.02, fold: 0 }, press: ["start"] } },
    { id: "stiff", robot: true, text: ["只把 J2 减速器的刚度提高到 2 倍（5 kg、K1、伸直）：第一阶频率提高多少？为什么不到 41%？",
                                       "Double only J2's gear stiffness (5 kg, K1, outstretched): how much does the first frequency rise? Why less than 41 %?"],
      demo: { scene: "arm", set: { mp: 5, kj: 0, k2x: 2, zeta: 0.02, fold: 0 }, press: ["start"] } },
    { id: "damp", robot: true, text: ["5 kg、K1、伸直：只改阻尼比，让敲一下后 1 s 内第一阶的振幅降到 5% 以下。",
                                      "5 kg, K1, outstretched: change only the damping so that the first mode decays below 5 % within 1 s of the knock."],
      demo: { scene: "arm", set: { mp: 5, kj: 0, k2x: 1, zeta: 0.05, fold: 0 }, press: ["start"] } },
    { id: "board", text: ["跳水板：调板长和体重，让板的弹跳频率在 0.95～1.05 Hz。", "Springboard: set the length and the diver's mass for a bounce frequency of 0.95–1.05 Hz."],
      demo: { scene: "board", set: { bl: 4.9, bm: 65 }, press: ["start"] } },
  ],
  think: ["第一阶固有频率约十几赫兹，出厂位置环的自然频率约 2.6 Hz。如果把位置环的增益加大十倍，会发生什么？",
          "The first natural frequency is a dozen or so hertz and the factory position loop's natural frequency about 2.6 Hz. What happens if the loop gain is raised tenfold?"],

  KL: [6.7e4, 12e4], KM: [3.1e4, 5.7e4], A2: 0.40, A3: 0.36, EIB: 1.057e5, MB: 25,
  masses(p) {                                   // [m, x, z, 过了 J3 吗]（J2 在原点；侧视，x 向外、z 向上）
    const al = p.fold * Math.PI / 180, c = Math.cos(al), s = Math.sin(al);
    const E = [this.A2 * c, this.A2 * s], Wr = [E[0] + this.A3 * c, E[1] - this.A3 * s];
    const out = [];
    for (let i = 0; i < 8; i++) { const u = (i + 0.5) / 8; out.push([(0.886 + 0.3) / 8, this.A2 * c * u, this.A2 * s * u, false]); }
    out.push([2.0, E[0], E[1], false]);
    for (let i = 0; i < 8; i++) { const u = (i + 0.5) / 8; out.push([(0.660 + 0.2) / 8, E[0] + this.A3 * c * u, E[1] - this.A3 * s * u, true]); }
    out.push([2.6, Wr[0], Wr[1], true], [0.2, Wr[0] + 0.05, Wr[1], true], [1.55, Wr[0] + 0.10, Wr[1], true]);
    if (p.mp > 0) out.push([p.mp, Wr[0] + 0.10, Wr[1] - 0.19, true]);
    return { list: out, E, Wr, tcp: [Wr[0] + 0.10, Wr[1] - 0.19] };
  },
  model(p) {
    const g = this.masses(p), E = g.E;
    let m11 = 0, m12 = 0, m22 = 0;
    g.list.forEach(([m, x, z, b]) => {
      m11 += m * (x * x + z * z);
      if (b) { const dx = x - E[0], dz = z - E[1]; m12 += m * (x * dx + z * dz); m22 += m * (dx * dx + dz * dz); }
    });
    const k = Math.round(p.kj), K1 = this.KL[k] * p.k2x, K2 = this.KM[k];
    // det(K − λM) = 0：a λ² + b λ + c = 0
    const a = m11 * m22 - m12 * m12, b = -(K1 * m22 + K2 * m11), cc = K1 * K2;
    const disc = Math.sqrt(Math.max(0, b * b - 4 * a * cc));
    const lam = [(-b - disc) / (2 * a), (-b + disc) / (2 * a)];
    const modes = lam.map((l) => {                 // (K − λM) v = 0：v = (λ m12, K1 − λ m11) 归一化到 vᵀMv = 1
      let v = [l * m12, K1 - l * m11];
      if (Math.abs(v[0]) + Math.abs(v[1]) < 1e-12) v = [1, 0];
      const n = Math.sqrt(m11 * v[0] * v[0] + 2 * m12 * v[0] * v[1] + m22 * v[1] * v[1]);
      return [v[0] / n, v[1] / n];
    });
    const J = [g.tcp[0], g.tcp[0] - E[0]];          // TCP 竖直速度 = J · q̇
    return { M: [[m11, m12], [m12, m22]], K: [K1, K2], w: lam.map(Math.sqrt), f: lam.map((l) => Math.sqrt(l) / (2 * Math.PI)), modes, J, g };
  },
  board(p) {
    const k = 3 * this.EIB / p.bl ** 3, m = p.bm + 0.2357 * this.MB;
    return { k, m, f: Math.sqrt(k / m) / (2 * Math.PI) };
  },
  std() { return this.model({ mp: 5, kj: 0, k2x: 1, zeta: 0.02, fold: 0 }); },
  reset(api, st) { st.t0 = null; st.hist = []; },
  start(api, st) { st.t0 = 0; st.hist = []; },
  resp(api, t) {                                     // 敲一下以后 TCP 的竖直位移（m）与两个关节的转角
    const p = api.p;
    if (api.scene === "board") {
      const b = this.board(p), w = 2 * Math.PI * b.f, z = 0.03, wd = w * Math.sqrt(1 - z * z);
      return { y: 0.25 * Math.exp(-z * w * t) * Math.sin(wd * t), q: [0, 0] };
    }
    const md = this.model(p), z = p.zeta, I0 = 1.0;
    let y = 0;
    const q = [0, 0];
    md.modes.forEach((v, k) => {
      const w = md.w[k], wd = w * Math.sqrt(1 - z * z), eta0 = (v[0] * md.J[0] + v[1] * md.J[1]) * -I0;   // 向下的冲量
      const eta = eta0 / wd * Math.exp(-z * w * t) * Math.sin(wd * t);
      q[0] += v[0] * eta; q[1] += v[1] * eta;
    });
    y = md.J[0] * q[0] + md.J[1] * q[1];
    return { y, q };
  },
  update(dt, api, st) {
    if (st.t0 === null) return;
    st.t0 += dt;
    const r = this.resp(api, st.t0);
    st.hist.push([st.t0, r.y]);
    if (st.hist.length > 600) st.hist.shift();
    st.q = r.q; st.y = r.y;
    if (st.t0 > (api.scene === "board" ? 8 : 3)) api.stop();
  },
  nb(rows) { return rows.map(([k, v]) => [k, String(v).replace(/ /g, " ")]); },
  readouts(api) {
    const f = api.fmt, p = api.p;
    if (api.scene === "board") {
      const b = this.board(p);
      if (b.f >= 0.95 && b.f <= 1.05) api.done("board");
      return this.nb([[["板端刚度 k = 3EI/L³", "Board-end stiffness k = 3EI/L³"], f(b.k, 0) + " N/m"], [["人 + 板的等效质量", "Diver + board effective mass"], f(b.m, 1) + " kg"],
        [["弹跳频率", "Bounce frequency"], f(b.f, 3) + " Hz"]]);
    }
    const md = this.model(p), s = this.std(), v = md.modes[0];
    const std = Math.abs(p.mp - 5) < 1e-9 && Math.round(p.kj) === 0 && Math.abs(p.fold) < 1e-9;
    if (std && Math.abs(p.k2x - 1) < 1e-9 && Math.abs(p.zeta - 0.02) < 1e-9) api.done("std");
    if (p.mp === 0 && Math.round(p.kj) === 0 && Math.abs(p.k2x - 1) < 1e-9 && Math.abs(p.fold) < 1e-9) api.done("empty");
    if (std && p.k2x >= 2 - 1e-9) api.done("stiff");
    const t5 = Math.log(20) / (p.zeta * md.w[0]);
    if (std && Math.abs(p.k2x - 1) < 1e-9 && t5 <= 1.0) api.done("damp");
    const n_half = Math.log(2) / (2 * Math.PI * p.zeta);
    return this.nb([
      [["第一阶、第二阶固有频率", "First and second natural frequencies"], `${f(md.f[0], 2)} / ${f(md.f[1], 1)} Hz`],
      [["第一阶与标准之比", "First frequency vs standard"], f(md.f[0] / s.f[0], 3)],
      [["第一阶振型 θ3 : θ2", "First mode θ3 : θ2"], f(v[1] / v[0], 2)],
      [["振幅减半要几个周期", "Cycles to halve the amplitude"], f(n_half, 1)],
      [["第一阶降到 5% 的时间", "Time for the first mode to fall to 5 %"], f(t5, 2) + " s"],
      [["等效：TCP 竖直刚度 / 质量矩阵 M11", "TCP vertical stiffness / mass-matrix M11"], `${f(1 / (md.J[0] ** 2 / md.K[0] + md.J[1] ** 2 / md.K[1]) / 1000, 1)} N/mm / ${f(md.M[0][0], 2)} kg·m²`],
    ]);
  },
  draw(api, st) {
    const { w, h } = api, c = api.ctx, f = api.fmt;
    const hist = st.hist || [];
    // 下方：TCP 竖直位移随时间（最后 3 s）
    const gx = w * 0.08, gy = h * 0.66, gw = w * 0.86, gh = h * 0.28;
    api.rect(gx, gy, gw, gh, null, api.css("--grid"));
    api.line(gx, gy + gh / 2, gx + gw, gy + gh / 2, api.css("--grid"), 1);
    const T = api.scene === "board" ? 8 : 3;
    const ymax = Math.max(1e-9, ...hist.map((q) => Math.abs(q[1])));
    c.strokeStyle = api.css("--blue"); c.lineWidth = 1.6; c.beginPath();
    hist.forEach(([t, y], i) => { const X = gx + gw * t / T, Y = gy + gh / 2 - (gh / 2 - 6) * y / ymax; if (i) c.lineTo(X, Y); else c.moveTo(X, Y); });
    c.stroke();
    api.label(api.lang() === "en" ? `TCP vertical displacement after the knock (0–${T} s)` : `敲一下以后的竖直位移（0～${T} s）`, gx + 4, gy - 10, api.css("--muted"), 12, "left");
    if (api.scene === "board") {
      const b = this.board(api.p), y = st.y || 0, x0 = w * 0.12, y0 = h * 0.32, k = w * 0.6 / 5.5;
      api.rect(x0 - 40, y0, 40, h * 0.25, api.css("--grid"), api.css("--ink"));
      const L = api.p.bl, tipY = y0 + 60 * y / 0.25;
      c.strokeStyle = api.css("--amber"); c.lineWidth = 8; c.beginPath(); c.moveTo(x0, y0);
      for (let i = 1; i <= 20; i++) { const u = i / 20; c.lineTo(x0 + k * L * u, y0 + (tipY - y0) * u * u * (3 - u) / 2); }
      c.stroke();
      api.circle(x0 + k * L, tipY - 22, 10, api.css("--blue"), api.css("--ink"));
      api.label(`${f(b.f, 2)} Hz`, x0 + k * L + 18, tipY - 22, api.css("--ink"), 13, "left");
      return;
    }
    const md = this.model(api.p), g = md.g, k = Math.min(w / 1.2, h / 1.0), x0 = w * 0.1, y0 = h * 0.30;
    const amp = 0.06 / Math.max(1e-9, ...hist.map((q) => Math.abs(q[1])), 1e-4);   // 振动放大到看得见
    const q = st.q || [0, 0];
    const rot = (P, O, a) => [O[0] + (P[0] - O[0]) * Math.cos(a) - (P[1] - O[1]) * Math.sin(a), O[1] + (P[0] - O[0]) * Math.sin(a) + (P[1] - O[1]) * Math.cos(a)];
    const a2 = -q[0] * amp, a3 = -q[1] * amp;
    const E = rot(g.E, [0, 0], a2), Wr = rot(rot(g.Wr, g.E, a3), [0, 0], a2), Tc = rot(rot(g.tcp, g.E, a3), [0, 0], a2);
    const X = (P) => [x0 + k * P[0], y0 - k * P[1]];
    api.line(...X([0, 0]), ...X(E), api.css("--blue"), 10);
    api.line(...X(E), ...X(Wr), api.css("--green"), 8);
    const Fl = rot(rot([g.Wr[0] + 0.1, g.Wr[1]], g.E, a3), [0, 0], a2);
    api.line(...X(Wr), ...X(Fl), api.css("--amber"), 6);
    api.line(...X(Fl), ...X(Tc), api.css("--ink"), 3);
    if (api.p.mp > 0) { const t = X(Tc); api.rect(t[0] - 10, t[1], 20, 14, api.css("--amber"), api.css("--ink")); }
    api.circle(...X([0, 0]), k * 0.05, api.css("--panel"), api.css("--ink"));
    api.circle(...X(E), k * 0.04, api.css("--panel"), api.css("--ink"));
    api.label("J2", ...X([0, 0.09]), api.css("--ink"), 12, "center");
    api.label("J3", ...X([E[0], E[1] + 0.08]), api.css("--ink"), 12, "center");
    api.label(api.lang() === "en" ? `f₁ = ${f(md.f[0], 2)} Hz (motion exaggerated)` : `f₁ = ${f(md.f[0], 2)} Hz（振动放大画）`, w * 0.62, h * 0.08, api.css("--ink"), 13, "left");
  },
});
