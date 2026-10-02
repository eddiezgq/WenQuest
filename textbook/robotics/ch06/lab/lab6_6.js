// 实验 6.6 力旋量与关节力矩（配 6.6 节）。侧视（x–z 平面，从 −y 一侧看），只用轴垂直于纸面的关节。
// 机器人托住负载的力旋量 F = (c × f, f)，f = (0, 0, m𝔤) 竖直向上，c 为负载质心。关节 i 需要的静力矩
//   τ_i = S_iᵀ F = ω̂_i · ((c − q_i) × f)（式 (6.6.6)）；轴为 −ŷ 时化为 τ_i = m𝔤 (c_x − q_ix)。
// 角度约定：轴 −ŷ 指向读者，逆时针为正（与第 12 章表 12.1.1 一致：关节 2 转到 −90° 时手臂竖直向上）。
WQ.lab({
  title: ["实验 6.6 力旋量与关节力矩", "Lab 6.6 Wrenches and joint torques"],
  goal: ["用 τ_i = S_iᵀF 计算托住负载所需的关节力矩，看力矩怎样随姿态变化；体会力臂就是力旋量与关节旋量轴的“互易”关系。",
         "Use τ_i = S_iᵀF for the torques that hold a load and watch them change with posture; see the lever arm as the reciprocal relation between the wrench and the joint screw."],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 托住 5 kg 负载", "UR5e holding 5 kg"],
      problem: { title: ["机器人问题：电机要出多大力矩", "Robot problem: how much torque the motors must give"],
                 text: ["UR5e 的额定负载是 5 kg。手臂水平伸出时，关节 2 要承受多大的静力矩？换一个姿态，力矩怎样变？（只计负载，不计手臂自重。）",
                        "The UR5e is rated for 5 kg. With the arm stretched out, what static torque must joint 2 give? How does it change with posture? (Load only, arm weight ignored.)"] } },
    { id: "human", name: ["手提购物袋", "Holding a shopping bag"], hide: ["j4"],
      problem: { title: ["生活中的例子：伸直手臂提东西为什么累", "Everyday example: why a straight arm tires fast"],
                 text: ["上臂、前臂各长 0.30 m，手里提着购物袋。手臂伸直和屈肘时，肩关节要出的力矩差多少？",
                        "Upper arm and forearm are 0.30 m each, a bag in the hand. How different is the shoulder torque with a straight arm and with a bent elbow?"] } },
  ],
  params: [
    { id: "m", name: ["负载质量 m", "Load mass m"], min: 0, max: 5, step: 0.5, value: 5, unit: "kg", digits: 1 },
    { id: "j2", name: ["关节 2（肩）θ₂", "Joint 2 (shoulder) θ₂"], min: -180, max: 180, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "j3", name: ["关节 3（肘）θ₃", "Joint 3 (elbow) θ₃"], min: -180, max: 180, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "j4", name: ["关节 4（腕）θ₄", "Joint 4 (wrist) θ₄"], min: -180, max: 180, step: 5, value: 0, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "home", robot: true, text: ["零位、负载 5 kg：读出 τ₂、τ₃、τ₄，与算例 6.6.1 比较。", "Home, 5 kg: read τ₂, τ₃, τ₄ and compare with Example 6.6.1."],
      demo: { scene: "ur", set: { m: 5, j2: 0, j3: 0, j4: 0 }, press: [] } },
    { id: "up", robot: true, text: ["负载仍为 5 kg，找一个姿态使 |τ₂| < 1 N·m。", "Still 5 kg: find a posture with |τ₂| < 1 N·m."],
      demo: { scene: "ur", set: { m: 5, j2: -90, j3: 0, j4: 90 }, press: [] } },
    { id: "straight", text: ["手臂水平伸直，提 5 kg：读出肩关节力矩。", "Arm straight out holding 5 kg: read the shoulder torque."],
      demo: { scene: "human", set: { m: 5, j2: 0, j3: 0 }, press: [] } },
    { id: "bent", text: ["上臂下垂、前臂水平（屈肘 90°）：肩关节力矩减半。", "Upper arm down, forearm level (elbow at 90°): the shoulder torque halves."],
      demo: { scene: "human", set: { m: 5, j2: 90, j3: -90 }, press: [] } },
  ],
  think: ["力的作用线经过某个关节的轴时，这个关节的力矩为零。用互易积说明原因。", "When the line of the force passes through a joint axis, that joint needs no torque. Explain with the reciprocal product."],

  rot(a, v) { const c = Math.cos(a), s = Math.sin(a); return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]; },
  add(a, b) { return [a[0] + b[0], a[1] + b[1]]; },
  chain(api) {        // 侧视平面内各关节中心与负载质心 (x, z)
    const d = Math.PI / 180, a2 = api.p.j2 * d, a3 = api.p.j3 * d, a4 = api.scene === "ur" ? api.p.j4 * d : 0;
    if (api.scene === "human") {
      const sh = [0, 0], el = this.add(sh, this.rot(a2, [-0.30, 0])), hd = this.add(el, this.rot(a2 + a3, [-0.30, 0]));
      return { joints: [sh, el], c: hd, pts: [sh, el, hd] };
    }
    const j2 = [0, 0.163], j3 = this.add(j2, this.rot(a2, [-0.425, 0])), j4 = this.add(j3, this.rot(a2 + a3, [-0.392, 0]));
    const fl = this.add(j4, this.rot(a2 + a3 + a4, [0, -0.1]));
    return { joints: [j2, j3, j4], c: fl, pts: [j2, j3, j4, fl] };
  },
  tau(api) { const g = 9.81, ch = this.chain(api); return ch.joints.map((q) => api.p.m * g * (ch.c[0] - q[0])); },
  reset(api, s) {},
  readouts(api, s) {
    const t = this.tau(api), ch = this.chain(api), f = (x) => api.fmt(x, 2);
    if (api.scene === "ur" && api.p.m === 5 && api.p.j2 === 0 && api.p.j3 === 0 && api.p.j4 === 0) api.done("home");
    if (api.scene === "ur" && api.p.m === 5 && Math.abs(t[0]) < 1 && (api.p.j2 !== 0 || api.p.j3 !== 0 || api.p.j4 !== 0)) api.done("up");
    const straight = 5 * 9.81 * 0.6;
    if (api.scene === "human" && api.p.m === 5 && api.p.j2 === 0 && api.p.j3 === 0) api.done("straight");
    if (api.scene === "human" && api.p.m === 5 && Math.abs(t[0]) <= straight / 2 + 1e-6 && Math.abs(t[0]) > 1) api.done("bent");
    const rows = api.scene === "ur"
      ? [[["τ₂ / τ₃ / τ₄", "τ₂ / τ₃ / τ₄"], `${f(t[0])} / ${f(t[1])} / ${f(t[2])} N·m`]]
      : [[["肩关节力矩 / 肘关节力矩", "shoulder / elbow torque"], `${f(t[0])} / ${f(t[1])} N·m`]];
    rows.push([["质心 c 的 (x, z)", "load centre c (x, z)"], `(${api.fmt(ch.c[0], 3)}, ${api.fmt(ch.c[1], 3)}) m`]);
    rows.push([["托举力 f", "lifting force f"], `(0, 0, ${f(api.p.m * 9.81)}) N`]);
    if (api.scene === "ur") {
      const cy = -0.284, fz = api.p.m * 9.81;      // 质心沿 y 偏出纸面（零位时 c_y = −0.284 m，只转关节 2–4 时不变）
      rows.push([["对 {s} 原点的力矩 m_s = c × f", "moment about {s} origin m_s = c × f"], `(${f(cy * fz)}, ${f(-ch.c[0] * fz)}, 0) N·m`]);
    }
    return rows;
  },
  draw(api, s) {
    const W = api.w, H = api.h, human = api.scene === "human";
    const k = human ? Math.min(W / 1.6, H / 1.0) : Math.min(W / 1.45, H / 1.6), ox = W * (human ? 0.62 : 0.8), oy = H * (human ? 0.38 : 0.72);
    const X = (x) => ox + x * k, Y = (z) => oy - z * k;
    api.grid(W, H, k * 0.1);
    const ch = this.chain(api), t = this.tau(api);
    if (human) {    // 躯干与头
      api.rect(X(0.06), Y(0.05), 0.2 * k, 0.6 * k, "rgba(150,160,170,0.35)", api.css("--muted"), 8);
      api.circle(X(0.16), Y(0.17), 0.08 * k, "rgba(150,160,170,0.35)", api.css("--muted"));
    } else {
      api.line(X(-1.1), Y(0), X(0.25), Y(0), api.css("--ground"), 2);
      api.rect(X(-0.06), Y(0.13), 0.12 * k, 0.13 * k, api.css("--panel"), api.css("--ink"), 3);
    }
    for (let i = 0; i < ch.pts.length - 1; i++) api.line(X(ch.pts[i][0]), Y(ch.pts[i][1]), X(ch.pts[i + 1][0]), Y(ch.pts[i + 1][1]), human ? "#c9a27a" : "#9aa5ad", human ? 12 : 10);
    ch.joints.forEach((q, i) => {
      api.circle(X(q[0]), Y(q[1]), 8, api.css("--panel"), api.css("--ink")); api.circle(X(q[0]), Y(q[1]), 2.5, api.css("--ink"));
      const name = human ? [api.T("肩", "shoulder"), api.T("肘", "elbow")][i] : `τ${["₂", "₃", "₄"][i]}`;
      api.label(`${name} = ${api.fmt(t[i], 1)} N·m`, X(q[0]), Y(q[1]) - (i % 2 ? 40 : 22), api.css("--ink"), 12, "center");
      api.line(X(q[0]), Y(q[1]), X(q[0]), Y(Math.min(q[1], ch.c[1]) - 0.35), api.css("--blue"), 1, [3, 4]);
    });
    // 负载与力
    const c = ch.c, sz = 0.06 * (human ? 1.4 : 1);
    if (human) { api.line(X(c[0]), Y(c[1]), X(c[0]), Y(c[1] - 0.08), api.css("--ink"), 1.5); api.rect(X(c[0] - sz), Y(c[1] - 0.08), 2 * sz * k, 0.16 * k, "rgba(201,143,0,0.35)", api.css("--amber"), 4); }
    else api.rect(X(c[0] - sz / 2), Y(c[1]), sz * k, sz * k, "rgba(201,143,0,0.35)", api.css("--amber"), 3);
    api.circle(X(c[0]), Y(c[1]), 4, api.css("--amber"));
    const L = 0.004 * api.p.m * 9.81;
    api.arrow(X(c[0]), Y(c[1]) , X(c[0]), Y(c[1] + L), api.css("--ok"), 3);
    api.label(api.T("托举力 f", "lifting force f"), X(c[0]) - 8, Y(c[1] + L) + 4, api.css("--ok"), 12, "right");
    api.line(X(c[0]), Y(c[1]), X(c[0]), Y(Math.min(c[1], ...ch.joints.map((q) => q[1])) - 0.35), api.css("--blue"), 1, [3, 4]);
    api.label(api.T("蓝色虚线之间的水平距离就是力臂；关节轴垂直于纸面，逆时针为正", "the horizontal gaps between blue dashed lines are the lever arms; joint axes point at you, anticlockwise positive"), 12, 18, api.css("--muted"), 12);
  },
});
