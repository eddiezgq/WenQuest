// 实验 18.2 并联机构的奇异（配 18.2 节）。
// 机器人场景：平面五杆（电机在 (∓0.15, 0) m，主动杆 0.20 m，从动杆 0.30 m）。滑块直接给两台电机的转角（正运动学）：
//   肘点 Eᵢ = Aᵢ + l₁ e(θᵢ)；末端是以两个肘点为圆心、半径 l₂ 的两圆之交，两个交点就是两种装配模式；
//   “装配模式 0”取 E₁ → E₂ 连线左侧（det A > 0）的交点，“1”取另一个。
//   速度关系 A ẋ = B θ̇（式 (18.1.5)），末端对外施加 f = (0, −20) N 时电机力矩 τ = Jᵀ f = Bᵀ A⁻ᵀ f（式 (18.2.7)）。
//   逆运动学奇异：det B = 0（某条支链伸直或折叠）；正运动学奇异：det A = 0（两根从动杆共线，两圆相切，|E₁E₂| = 2 l₂）。
// 生活场景：晾衣绳。两根柱子相距 4 m、同高，绳子中点挂 2 kg 的湿衣服，下垂量 s；绳与水平线的夹角 α = atan(2s/L)，
//   拉力 T = m𝔤 / (2 sin α)（𝔤 = 9.81 m/s²）。
WQ.lab({
  title: ["实验 18.2 并联机构的奇异", "Lab 18.2 Singularities of a parallel mechanism"],
  goal: ["转动五杆的两台电机，找出逆运动学奇异和正运动学奇异，看两种装配模式怎样合一、电机力矩怎样急剧增大。",
         "Turn the five-bar's two motors, find its inverse and direct singularities, and watch the two assembly modes merge and the motor torques soar."],
  scenes: [
    { id: "five", robot: true, name: ["五杆的奇异", "Five-bar singularities"], hide: ["sag"],
      problem: { title: ["机器人问题：电机锁死了，末端为什么还能动", "Robot problem: the motors are locked, so why can the end point move"],
                 text: ["用滑块给出两台电机的转角。两个灰色圆以肘点为圆心、半径 0.30 m，它们的两个交点是两种装配模式（实线是选中的一种）。末端对外施加 20 N 向下的力，界面显示两台电机的力矩。",
                        "Set the two motor angles. The grey circles of radius 0.30 m about the elbows meet at the two assembly modes (the chosen one solid). The end point pushes down with 20 N; the motor torques are shown."] } },
    { id: "line", name: ["晾衣绳", "A clothesline"], hide: ["t1", "t2", "mode"],
      problem: { title: ["生活中的例子：晾衣绳为什么不能拉直", "Everyday example: why a clothesline cannot be pulled straight"],
                 text: ["绳子两端系在相距 4 m 的两根柱子上，中间挂一件 2 kg 的湿衣服。减小下垂量，看绳中的拉力怎样变化。",
                        "A cord is tied between two posts 4 m apart with a 2 kg wet shirt in the middle. Reduce the sag and watch the tension."] } },
  ],
  params: [
    { id: "t1", name: ["电机 1 转角 θ₁", "motor 1 angle θ₁"], min: 40, max: 180, step: 0.01, value: 118.21, unit: "°", digits: 2 },
    { id: "t2", name: ["电机 2 转角 θ₂", "motor 2 angle θ₂"], min: 0, max: 140, step: 0.01, value: 61.79, unit: "°", digits: 2 },
    { id: "mode", name: ["装配模式：0 在 E₁E₂ 左侧（上方），1 在另一侧", "assembly mode: 0 left of E₁E₂ (above), 1 the other side"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "sag", name: ["晾衣绳的下垂量 s", "clothesline sag s"], min: 0.01, max: 1.0, step: 0.01, value: 0.5, unit: "m", digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 18.1.1：θ = (118.21°, 61.79°)，末端在 (0, 0.35) m，读出 det A 与 det B。",
                                     "Example 18.1.1: θ = (118.21°, 61.79°) puts the end point at (0, 0.35) m; read det A and det B."],
      demo: { scene: "five", set: { t1: 118.21, t2: 61.79, mode: 0 }, press: [], wait: 1 } },
    { id: "typeI", robot: true, text: ["调出逆运动学奇异：让两条支链都伸直（|det B| < 2 × 10⁻⁴ m⁴）。", "Reach an inverse singularity: stretch both legs (|det B| < 2 × 10⁻⁴ m⁴)."],
      demo: { scene: "five", set: { t1: 72.54, t2: 107.46, mode: 0 }, press: [], wait: 1 } },
    { id: "big", robot: true, text: ["接近正运动学奇异：使最大电机力矩超过 40 N·m（提示：θ₁ ≈ 138.5°，θ₂ = 180° − θ₁）。",
                                      "Approach the direct singularity: make the larger motor torque exceed 40 N·m (hint: θ₁ ≈ 138.5°, θ₂ = 180° − θ₁)."],
      demo: { scene: "five", set: { t1: 138.55, t2: 41.45, mode: 0 }, press: [], wait: 1 } },
    { id: "merge", robot: true, text: ["把两种装配模式调到合一：两个圆几乎相切（两肘点相距 0.598～0.600 m），两根从动杆连成一条直线。",
                                        "Make the two assembly modes merge: the circles almost touch (elbows 0.598–0.600 m apart) and the forearms line up."],
      demo: { scene: "five", set: { t1: 138.59, t2: 41.41, mode: 0 }, press: [], wait: 1 } },
    { id: "line", text: ["生活场景：把晾衣绳拉直，使拉力超过衣服重量的 5 倍。", "Everyday scene: pull the line so straight that the tension exceeds 5 times the shirt's weight."],
      demo: { scene: "line", set: { sag: 0.1 }, press: [], wait: 1 } },
  ],
  think: ["正运动学奇异附近，电机转角改变 0.04°，末端就移动了约 8 mm（从 y = 0.140 m 到 0.132 m）。这对定位精度和控制意味着什么？",
          "Near the direct singularity a 0.04° change of motor angle moves the end point about 8 mm (from y = 0.140 m to 0.132 m). What does that mean for accuracy and control?"],

  C: 0.15, L1: 0.20, L2: 0.30,
  solve(api) {
    const r = Math.PI / 180, t = [api.p.t1 * r, api.p.t2 * r], A = [[-this.C, 0], [this.C, 0]];
    const B = A.map((a, i) => [a[0] + this.L1 * Math.cos(t[i]), a[1] + this.L1 * Math.sin(t[i])]);
    const d = [B[1][0] - B[0][0], B[1][1] - B[0][1]], L = Math.hypot(...d);
    const out = { t, A, B, L, ok: L <= 2 * this.L2 + 1e-12 };
    if (!out.ok) return out;
    const h = Math.sqrt(Math.max(this.L2 * this.L2 - L * L / 4, 0)), n = [-d[1] / L, d[0] / L], m = [(B[0][0] + B[1][0]) / 2, (B[0][1] + B[1][1]) / 2];
    out.P = [[m[0] + h * n[0], m[1] + h * n[1]], [m[0] - h * n[0], m[1] - h * n[1]]];
    const P = out.P[api.p.mode];
    const a1 = [P[0] - B[0][0], P[1] - B[0][1]], a2 = [P[0] - B[1][0], P[1] - B[1][1]];
    out.detA = a1[0] * a2[1] - a1[1] * a2[0];
    const b = [this.L1 * (-a1[0] * Math.sin(t[0]) + a1[1] * Math.cos(t[0])), this.L1 * (-a2[0] * Math.sin(t[1]) + a2[1] * Math.cos(t[1]))];
    out.detB = b[0] * b[1];
    // τ = Bᵀ A⁻ᵀ f：先解 Aᵀ g = f，再 τᵢ = bᵢ gᵢ
    const f = [0, -20];
    if (Math.abs(out.detA) > 1e-12) {
      const g0 = (f[0] * a2[1] - f[1] * a2[0]) / out.detA, g1 = (a1[0] * f[1] - a1[1] * f[0]) / out.detA;   // [a1 a2] g = f
      out.tau = [b[0] * g0, b[1] * g1];
    } else out.tau = [Infinity, Infinity];
    return out;
  },
  T(s) { return 2 * 9.81 / (2 * Math.sin(Math.atan(2 * s / 4))); },
  reset(api, s) { },
  readouts(api, s) {
    const f = (v, n) => api.fmt(v, n);
    if (api.scene === "line") {
      const W = 2 * 9.81, T = this.T(api.p.sag), a = Math.atan(2 * api.p.sag / 4) * 180 / Math.PI;
      if (T > 5 * W) api.done("line");
      return [[["绳与水平线的夹角 α", "cord angle α"], f(a, 2) + "°"], [["拉力 T = m𝔤 / (2 sin α)", "tension T = m𝔤 / (2 sin α)"], f(T, 1) + " N"],
              [["拉力 / 衣服重量", "tension / weight"], f(T / W, 2)]];
    }
    const o = this.solve(api);
    if (!o.ok) return [[["装配", "assembly"], api.T(`装不起来：两肘点相距 ${f(o.L, 4)} m > 0.6 m，两圆不相交`, `cannot assemble: elbows ${f(o.L, 4)} m apart > 0.6 m, the circles do not meet`)]];
    const P = o.P[api.p.mode], tmax = Math.max(Math.abs(o.tau[0]), Math.abs(o.tau[1]));
    const near = (a, b) => Math.abs(a - b) < 1e-6;
    if (near(api.p.t1, 118.21) && near(api.p.t2, 61.79) && api.p.mode === 0 && Math.hypot(P[0], P[1] - 0.35) < 1e-3) api.done("ex");
    if (Math.abs(o.detB) < 2e-4) api.done("typeI");
    if (tmax > 40 && isFinite(tmax)) api.done("big");
    if (o.L >= 0.598 && o.L <= 0.6 + 1e-12) api.done("merge");
    let kind = api.T("一般位形", "regular");
    if (Math.abs(o.detB) < 2e-4) kind = api.T("接近逆运动学奇异（支链伸直或折叠）", "near an inverse singularity (a leg straight or folded)");
    if (Math.abs(o.detA) < 5e-3) kind = api.T("接近正运动学奇异（两根从动杆共线）", "near a direct singularity (forearms in line)");
    return [[["末端 P", "end point P"], `(${f(P[0], 4)}, ${f(P[1], 4)}) m`],
            [["另一种装配模式", "other assembly mode"], `(${f(o.P[1 - api.p.mode][0], 4)}, ${f(o.P[1 - api.p.mode][1], 4)}) m`],
            [["两肘点的距离", "distance between elbows"], f(o.L, 4) + " m"],
            [["det A", "det A"], f(o.detA, 5) + " m²"], [["det B", "det B"], o.detB.toExponential(3) + " m⁴"],
            [["电机力矩 τ₁, τ₂（末端施加 20 N 向下）", "motor torques τ₁, τ₂ (20 N down)"], isFinite(tmax) ? `${f(o.tau[0], 2)}, ${f(o.tau[1], 2)} N·m` : "∞"],
            [["状态", "state"], kind]];
  },
  draw(api, s) {
    const { w: W, h: H } = api, css = api.css;
    if (api.scene === "line") {
      const sc = Math.min(W / 5, H / 1.9), ox = W / 2, oy = H * 0.3, P = (x, y) => [ox + sc * x, oy - sc * y];
      api.ground(H * 0.9, W);
      [-2, 2].forEach((x) => api.rect(...P(x - 0.05, 0.05), sc * 0.1, H * 0.9 - P(0, 0.05)[1], css("--muted")));
      const m = [0, -api.p.sag];
      api.line(...P(-2, 0), ...P(...m), css("--ink"), 2); api.line(...P(2, 0), ...P(...m), css("--ink"), 2);
      const q = P(...m);
      api.rect(q[0] - sc * 0.25, q[1] + 2, sc * 0.5, sc * 0.45, css("--blue"), css("--ink"), 4);
      const T = this.T(api.p.sag), a = Math.atan(2 * api.p.sag / 4);
      api.arrow(q[0], q[1], q[0] - Math.min(150, T * 0.8) * Math.cos(a), q[1] - Math.min(150, T * 0.8) * Math.sin(a), css("--red"), 3);
      api.arrow(q[0], q[1], q[0] + Math.min(150, T * 0.8) * Math.cos(a), q[1] - Math.min(150, T * 0.8) * Math.sin(a), css("--red"), 3);
      api.label(`T = ${api.fmt(T, 1)} N`, q[0] + 20, q[1] - 40, css("--red"), 14);
      api.label(api.T("箭头长度与拉力成正比（超过 190 N 不再加长）", "arrow length ∝ tension (capped above 190 N)"), 12, 18, css("--muted"), 12);
      return;
    }
    const sc = Math.min(W / 1.5, H / 1.05), ox = W * 0.45, oy = H * 0.74, P = (x, y) => [ox + sc * x, oy - sc * y];
    const o = this.solve(api);
    o.B.forEach((b) => { const q = P(...b); api.circle(q[0], q[1], sc * this.L2, null, css("--grid")); });
    o.A.forEach((a, i) => { const q = P(...a); api.rect(q[0] - 7, q[1] - 7, 14, 14, css("--ink")); api.line(...q, ...P(...o.B[i]), css("--accent"), 8); api.circle(...P(...o.B[i]), 5, css("--panel"), css("--ink")); });
    if (!o.ok) return;
    [1 - api.p.mode, api.p.mode].forEach((k) => {
      const Pk = o.P[k], sel = k === api.p.mode, col = sel ? css("--amber") : css("--muted");
      o.B.forEach((b) => api.line(...P(...b), ...P(...Pk), col, sel ? 5 : 2, sel ? null : [6, 5]));
      api.circle(...P(...Pk), sel ? 7 : 5, sel ? css("--red") : css("--panel"), css("--ink"));
    });
    const Pk = o.P[api.p.mode], q = P(...Pk);
    api.arrow(q[0], q[1], q[0], q[1] + 40, css("--red"), 2.5);
    api.label("20 N", q[0] + 8, q[1] + 32, css("--red"), 12);
    const tm = Math.max(Math.abs(o.tau[0]), Math.abs(o.tau[1]));
    const hb = (v) => Math.min(H * 0.6, 40 * Math.max(0, Math.log10(Math.max(1, Math.abs(v))) + 0.02) * 2.2);
    o.tau.forEach((v, i) => { const x = W - 90 + 40 * i, hh = isFinite(v) ? hb(v) : H * 0.6; api.rect(x, H * 0.85 - hh, 26, hh, tm > 40 ? css("--red") : css("--amber")); api.label(`τ${i + 1}`, x + 13, H * 0.85 + 12, css("--ink"), 12, "center"); });
    api.label(api.T("电机力矩（对数刻度）", "motor torques (log scale)"), W - 12, H * 0.85 + 30, css("--muted"), 11, "right");
  },
});
