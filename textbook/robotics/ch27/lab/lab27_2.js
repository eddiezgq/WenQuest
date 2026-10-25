// 实验 27.2 调夹紧力抓住零件（配 27.2 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex27_2.py 同一版本、同一模型。
// 模型与程序 _ch27.py 的 gripper_xml 相同：夹爪座由竖直滑动关节带着（转子惯量 1e4，相当于按给定的加速度运动），
//   两个指由水平滑动关节和力电机驱动，电机的力就是夹紧力 F；平口指是一块钢板，V 形指是两块与夹紧方向成 ±45° 的钢板；
//   毛坯是 Ø50 mm 的钢圆柱（SH-301，2.8 kg，长 0.18166 m），夹持点离毛坯上端 0.04 m；指面沿毛坯轴线长 ℓ = 0.04 m。
//   圆锥摩擦锥、impratio = 10、noslip（27.2.3 节）。时间步长 0.5 ms，由本页自己逐步推进（每步更新夹爪座的推力）。
// 过程：开始时指面已贴着毛坯，夹紧力 F 和重力同时加上（ex27_2.py 是先在无重力下夹紧 0.2 s 再加重力，滑移判据为 1 mm）；
//   静置 0.5 s，再以加速度 a 提起 0.4 s、减速 0.4 s，共 1.5 s。毛坯相对夹爪的位移（在夹爪坐标系中）超过 2 mm 判为“滑落”。
// 生活场景“捏起一支笔”：笔 Ø8 mm、长 0.14 m、20 g，手指捏在离上端 0.01 m 处（质心离夹持点 0.06 m），指腹长 0.015 m，μ 默认 0.4（示意值），与习题 27.2.5 相同。
// 公式（27.2 节）：竖直 F = m(𝔤 + a)/(2μ)（平口），V 形再乘 cos 45°；水平、平口 F = m(𝔤 + a)(1/2 + d/ℓ)/μ，d = L/2 − 0.04。
// 阈值：ex27_2.py 中 MuJoCo 平口竖直 a = 3 时 89.7 N（公式 89.67 N），V 形 63.6 N（63.41 N），平口水平静止 243.1 N（243.19 N）；
//   按本页的流程，平口竖直 89.5 N、V 形竖直 63.4 N、平口水平 241.6 N、V 形水平 22.2 N，与之相差不到 1%（审稿时用 Python 复现）。
WQ.lab({
  title: ["实验 27.2 调夹紧力抓住零件", "Lab 27.2 Tune the grip force to hold a part"],
  goal: ["用两指夹爪夹住毛坯提起来：找出刚好不滑的夹紧力，比较平口与 V 形指、毛坯竖直与水平时的差别，与 27.2 节的公式核对。",
         "Lift a blank with a two-finger gripper: find the grip force at which it just holds, compare flat and V-jaws, vertical and horizontal blanks, and check the formulas of Section 27.2."],
  view: "physics",
  scenes: [
    { id: "blank", robot: true, name: ["夹 SH-301 毛坯", "Gripping the SH-301 blank"], hide: [],
      problem: { title: ["机器人问题：夹紧力要多大，毛坯才不会从指间滑落", "Robot problem: how hard must the gripper squeeze so the blank does not slip out"],
                 text: ["上下料工位的夹爪在 A 点竖直地提起毛坯，在 B 点把它横着送进卡盘。按“开始”提起毛坯，看它会不会滑。",
                        "The loading cell's gripper lifts the blank vertically at A and carries it horizontally into the chuck at B. Press Start to lift it and see whether it slips."] } },
    { id: "pen", name: ["生活：捏起一支笔", "Everyday: picking up a pen"], hide: ["jaw"], params: { F: { value: 0.5 }, mu: { value: 0.4 }, a: { value: 2 } },
      problem: { title: ["生活中的例子：两根手指捏起一支笔", "Everyday example: picking up a pen with two fingers"],
                 text: ["笔只有 20 g，捏力要多小才会掉？捏在笔的一端、让笔横着，又要多大的力？",
                        "The pen weighs only 20 g. How light a pinch lets it drop? And how hard must you pinch to hold it sideways by one end?"] } },
  ],
  params: [
    { id: "jaw", name: ["指形：0 平口 / 1 V 形", "Jaws: 0 flat / 1 V"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "orient", name: ["姿态：0 竖直（A 点）/ 1 水平（B 点）", "Pose: 0 vertical (A) / 1 horizontal (B)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "F", name: ["夹紧力 F", "Grip force F"], min: 0.1, max: 400, step: 0.1, value: 100, unit: "N", digits: 1 },
    { id: "mu", name: ["摩擦系数 μ", "Friction coefficient μ"], min: 0.1, max: 0.8, step: 0.05, value: 0.2, unit: "", digits: 2 },
    { id: "a", name: ["提起的加速度 a", "Lift acceleration a"], min: 0, max: 5, step: 0.5, value: 3, unit: "m/s²", digits: 1 },
  ],
  legend: [{ color: "#1f77b4", name: ["毛坯相对夹爪的位移", "displacement of the part in the jaws"] }, { color: "#d62728", name: ["2 mm（判为滑落）", "2 mm (counted as slipping)"] }],
  physics: {
    camera: [35, 15, 0.85],
    rate: 1e-9,                                   // 本页自己逐步推进，套件不再推进
    G: 9.81, DT: 0.0005, ARM: 1e4, GAM: Math.PI / 4,
    part(api) {
      return api.scene === "pen" ? { m: 0.02, r: 0.004, L: 0.14, top: 0.01, half: 0.0075, t: 0.002, w: 0.006 }
        : { m: 2.8, r: 0.025, L: 0.18165965479023977, top: 0.04, half: 0.02, t: 0.005, w: 0.012 };
    },
    xml(api) {
      const P = this.part(api), jaw = api.scene === "pen" ? 0 : Math.round(api.p.jaw), hor = Math.round(api.p.orient) === 1, mu = api.p.mu;
      const quat = hor ? "0.7071068 0.7071068 0 0" : "1 0 0 0", off = P.r + P.t + 0.001;
      let fingers = "";
      [[1, "f1"], [-1, "f2"]].forEach(([s, name]) => {
        let g = "";
        (jaw === 0 ? [0] : [this.GAM, -this.GAM]).forEach((a, k) => {
          const ang = s > 0 ? a : Math.PI - a;
          const cx = (P.r + P.t) * Math.cos(ang) - s * off, cy = (P.r + P.t) * Math.sin(ang);
          g += `<geom name="${name}${k}" type="box" size="${P.t} ${P.w} ${P.half}" pos="${cx.toFixed(6)} ${cy.toFixed(6)} 0" quat="${Math.cos(ang / 2).toFixed(7)} 0 0 ${Math.sin(ang / 2).toFixed(7)}" mass="0.1" rgba="0.3 0.32 0.35 1"/>`;
        });
        fingers += `<body name="${name}" pos="${s * off} 0 0"><joint name="j${name}" type="slide" axis="${-s} 0 0" damping="${api.scene === "pen" ? 0.2 : 20}"/>${g}</body>`;
      });
      return `<mujoco><option timestep="${this.DT}" cone="elliptic" impratio="10" noslip_iterations="10"/>
<default><geom friction="${mu} 0.005 0.0001" solref="0.004 1"/></default>
<worldbody><body name="carriage" pos="0 0 0.5"><joint name="lift" type="slide" axis="0 0 1" armature="${this.ARM}"/>
<geom type="box" size="0.04 0.04 0.02" pos="0 0 ${hor ? 0.06 : 0.12}" mass="1.0" rgba="0.25 0.5 0.75 1"/>
<body name="hand" quat="${quat}">${fingers}</body></body>
<body name="part" pos="0 0 0.5" quat="${quat}"><freejoint/><geom name="pt" type="cylinder" size="${P.r} ${P.L / 2}" pos="0 0 ${-(P.L / 2 - P.top)}" mass="${P.m}" rgba="${api.scene === "pen" ? "0.85 0.2 0.2 1" : "0.62 0.63 0.66 1"}"/></body>
</worldbody><actuator><motor joint="lift"/><motor joint="jf1"/><motor joint="jf2"/></actuator></mujoco>`;
    },
  },
  formula(api) {                                  // 27.2 节的公式；V 形指水平时没有简单公式（27.4 节用线性规划）
    const P = this.physics.part(api), g = this.physics.G, a = api.p.a, mu = api.p.mu;
    const jaw = api.scene === "pen" ? 0 : Math.round(api.p.jaw), hor = Math.round(api.p.orient) === 1;
    const d = P.L / 2 - P.top, ell = 2 * P.half;
    if (!hor) return P.m * (g + a) / (2 * mu) * (jaw === 1 ? Math.cos(this.physics.GAM) : 1);
    return jaw === 0 ? P.m * (g + a) * (0.5 + d / ell) / mu : null;
  },
  reset(api, s) {
    const { mj, m, d } = api.sim;
    s.mt = 0;
    for (let b = 1; b < m.nbody; b++) s.mt += m.body_mass[b];
    s.part = api.id("body", "part"); s.hand = api.id("body", "hand");
    d.ctrl[1] = api.p.F; d.ctrl[2] = api.p.F;
    mj.mj_forward(m, d);
    s.rel0 = this.rel(d, s); s.R0 = this.relR(d, s);
    s.t = 0; s.worst = 0; s.ang = 0; s.hist = []; s.fin = false;
  },
  rel(d, s) {                                     // 零件相对夹爪的位置（夹爪坐标系）
    const h = s.hand, p = s.part, R = d.xmat, x = [d.xpos[3 * p] - d.xpos[3 * h], d.xpos[3 * p + 1] - d.xpos[3 * h + 1], d.xpos[3 * p + 2] - d.xpos[3 * h + 2]];
    return [0, 1, 2].map((i) => R[9 * h + i] * x[0] + R[9 * h + 3 + i] * x[1] + R[9 * h + 6 + i] * x[2]);
  },
  relR(d, s) {                                    // R_h^T R_p
    const h = s.hand, p = s.part, R = d.xmat, out = [];
    for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) out.push(R[9 * h + i] * R[9 * p + j] + R[9 * h + 3 + i] * R[9 * p + 3 + j] + R[9 * h + 6 + i] * R[9 * p + 6 + j]);
    return out;
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim, ph = this.physics, a = api.p.a, TE = 1.5;
    if (s.fin) { api.stop(); return; }
    const n = Math.max(1, Math.round(dt / ph.DT));
    for (let k = 0; k < n && s.t < TE; k++) {
      const acc = s.t >= 0.5 && s.t < 0.9 ? a : (s.t >= 0.9 && s.t < 1.3 ? -a : 0);
      d.ctrl[0] = ph.ARM * acc + s.mt * (ph.G + acc);
      d.ctrl[1] = api.p.F; d.ctrl[2] = api.p.F;
      mj.mj_step(m, d);
      s.t += ph.DT;
      const r = this.rel(d, s), dx = Math.hypot(r[0] - s.rel0[0], r[1] - s.rel0[1], r[2] - s.rel0[2]);
      s.worst = Math.max(s.worst, dx);
      const Rn = this.relR(d, s), R0 = s.R0;
      let tr = 0; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) tr += R0[3 * j + i] * Rn[3 * j + i];
      s.ang = Math.max(s.ang, Math.acos(Math.max(-1, Math.min(1, (tr - 1) / 2))) * 180 / Math.PI);
      if (k % 4 === 0) s.hist.push([s.t, Math.min(dx * 1000, 12)]);
      if (s.worst > 0.03) { s.t = TE; break; }     // 已经掉了，不再算
    }
    if (s.t >= TE) {
      s.fin = true;
      const held = s.worst < 0.002, Ff = this.formula(api), jaw = Math.round(api.p.jaw), hor = Math.round(api.p.orient) === 1;
      if (api.scene === "blank" && held && jaw === 0 && !hor && a >= 2.9 && api.p.mu > 0.19 && api.p.mu < 0.21 && api.p.F <= 1.03 * Ff) api.done("vert");
      if (api.scene === "blank" && held && jaw === 1 && !hor) {
        const flat = this.physics.part(api).m * (this.physics.G + a) / (2 * api.p.mu);
        if (api.p.F < flat) api.done("vjaw");
      }
      if (api.scene === "blank" && held && jaw === 0 && hor && api.p.F <= 1.05 * Ff) api.done("horiz");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    const o = api.cplot(48, 10, w - 60, h - 34, [{ pts: H, color: "#1f77b4" }, { pts: [[0, 2], [1.5, 2]], color: "#d62728" }],
      { xmin: 0, xmax: 1.5, ymin: 0, ymax: 12, xlabel: "t / s", ylabel: "mm" });
    return o;
  },
  readouts(api, s) {
    const f = (v, k = 1) => api.fmt(v, k), Ff = this.formula(api), done = s.fin;
    return [
      [["时间", "Time"], f(s.t || 0, 2) + " s" + ((s.t || 0) < 0.5 ? api.T("（静置）", " (holding still)") : (s.t < 1.3 ? api.T("（提起）", " (lifting)") : ""))],
      [["零件相对夹爪的最大位移 / 转角", "Largest displacement / rotation of the part in the jaws"], `${f((s.worst || 0) * 1000, 2)} mm / ${f(s.ang || 0, 2)}°`],
      [["结果", "Result"], !done ? "—" : (s.worst < 0.002 ? api.T("夹住了", "held") : api.T("滑落了", "slipped out"))],
      [["公式给出的最小夹紧力", "Minimum grip force by the formula"], Ff === null ? api.T("V 形指水平时无简单公式（27.4 节，约 23 N × (𝔤 + a)/𝔤）", "no simple formula for horizontal V-jaws (Section 27.4: about 23 N × (𝔤 + a)/𝔤)") : f(Ff, 1) + " N"],
      [["所用的夹紧力", "Grip force used"], f(api.p.F, 1) + " N"],
    ];
  },
  tasks: [
    { id: "vert", robot: true, text: ["平口夹爪、毛坯竖直、μ = 0.2、a = 3 m/s²：找到刚好不滑的夹紧力（夹住了，且不超过公式值的 1.03 倍）。",
                                     "Flat jaws, vertical blank, μ = 0.2, a = 3 m/s²: find the force that just holds (held, and at most 1.03 times the formula)."],
      demo: { scene: "blank", set: { jaw: 0, orient: 0, mu: 0.2, a: 3, F: 91.5 }, wait: 6 } },
    { id: "vjaw", robot: true, text: ["换成 V 形指，用比平口公式值小的夹紧力把毛坯竖直提起来。", "Switch to V-jaws and lift the vertical blank with less force than the flat-jaw formula."],
      demo: { scene: "blank", set: { jaw: 1, orient: 0, mu: 0.2, a: 3, F: 66 }, wait: 6 } },
    { id: "horiz", robot: true, text: ["平口夹爪、毛坯水平：夹住它所需的力是竖直时的三倍多，用不超过式 (27.2.5) 1.05 倍的力夹住。",
                                      "Flat jaws, horizontal blank: it needs more than three times the vertical force; hold it with at most 1.05 times Eq. (27.2.5)."],
      demo: { scene: "blank", set: { jaw: 0, orient: 1, mu: 0.2, a: 0, F: 250 }, wait: 6 } },
  ],
  think: ["毛坯水平时，V 形指只要二十几牛就夹住了，平口指却要两百多牛。从接触力的方向解释这个差别。如果把平口夹爪绕毛坯轴线转 90°，让夹紧方向竖直，又会怎样？",
          "With the blank horizontal, V-jaws hold it with about twenty newtons, flat jaws need over two hundred. Explain the difference from the directions of the contact forces. What happens if the flat gripper is turned 90° about the blank's axis so that it squeezes vertically?"],
});
