// 实验 27.3 碰撞与恢复系数（配 27.3 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex27_3.py 同一版本。
// 场景“毛坯掉在料台上”：SH-301 毛坯（Ø50 mm、长 0.1817 m、2.8 kg）水平地从高 h 处落到钢制料台（0.5 m × 0.4 m 的平板，台面高 0.8 m）上；
// 生活场景“皮球落地”：Ø0.24 m、0.6 kg 的球落到地面上（示意值）。
// 接触按 MuJoCo 的软接触（式 (27.1.6)）：两个几何体用同一个 solref = (τ, ζ)，solimp 取默认值。时间步长 0.1 ms，本页自己逐步推进。
// 每次碰撞（从出现接触到接触消失）记录：撞入的竖直速度 v⁻、离开的速度 v⁺、恢复系数 e = v⁺/v⁻、接触持续时间、
// 峰值接触力（由零件的竖直加速度算出：λ = m(z̈ + 𝔤)）。式 (27.3.4) 的线性预测 e = exp(−πζ/√(1 − ζ²)) 一并显示。
// 按本页的流程在 Python 中核算（毛坯从 0.3 m 落下）：τ = 0.02 s 时 ζ = 0.25 → e = 0.496；ζ = 1 → 不反弹；τ 减半，接触时间约减半、峰值力约加倍。
WQ.lab({
  title: ["实验 27.3 碰撞与恢复系数", "Lab 27.3 Impact and the coefficient of restitution"],
  goal: ["让零件落到料台上，测出每次碰撞的恢复系数、接触时间和峰值力，看 MuJoCo 的接触参数怎样决定它们。",
         "Drop a part onto the table, measure the restitution, contact time and peak force of each impact, and see how MuJoCo's contact parameters set them."],
  view: "physics",
  scenes: [
    { id: "drop", robot: true, name: ["毛坯掉在料台上", "Blank dropped on the table"],
      problem: { title: ["机器人问题：毛坯从夹爪里滑落，会弹多高、撞多重", "Robot problem: a blank slips out of the gripper—how high does it bounce, how hard does it hit"],
                 text: ["在仿真里研究这类问题，结果取决于接触模型的参数。调 solref 的时间常数和阻尼比，看毛坯怎样反弹。",
                        "In simulation the answer depends on the contact parameters. Change solref's time constant and damping ratio and watch the blank bounce."] } },
    { id: "ball", name: ["生活：皮球落地", "Everyday: a ball dropped on the floor"], params: { h: { value: 0.8 }, zeta: { value: 0.1 } },
      problem: { title: ["生活中的例子：皮球为什么越弹越低", "Everyday example: why a ball bounces lower each time"],
                 text: ["每次弹起的高度是上一次的 e² 倍。调阻尼比，让皮球弹得高一些或低一些。",
                        "Each bounce reaches e² of the previous height. Change the damping ratio to make the ball bounce higher or lower."] } },
  ],
  params: [
    { id: "h", name: ["落下高度 h", "Drop height h"], min: 0.05, max: 1.0, step: 0.05, value: 0.3, unit: "m", digits: 2 },
    { id: "tau", name: ["时间常数 τ（solref 第一个数）", "Time constant τ (first number of solref)"], min: 0.005, max: 0.05, step: 0.005, value: 0.02, unit: "s", digits: 3 },
    { id: "zeta", name: ["阻尼比 ζ（solref 第二个数）", "Damping ratio ζ (second number of solref)"], min: 0.05, max: 1.0, step: 0.01, value: 1.0, unit: "", digits: 2 },
  ],
  legend: [{ color: "#1f77b4", name: ["零件的高度", "height of the part"] }, { color: "#d62728", name: ["接触力（右轴）", "contact force (right axis)"] }],
  physics: {
    camera: [30, 12, 0.85],
    rate: 1e-9,                                   // 本页自己逐步推进
    DT: 0.0001, G: 9.81,
    part(api) { return api.scene === "ball" ? { m: 0.6, base: 0.0, r: 0.12 } : { m: 2.8, base: 0.8, r: 0.025 }; },
    xml(api) {
      const P = this.part(api), sr = `${api.p.tau} ${api.p.zeta}`;
      const floor = api.scene === "ball" ? '<geom type="plane" size="3 3 0.1" rgba="0.8 0.8 0.8 1"/>'
        : '<geom type="box" size="0.25 0.2 0.05" pos="0 0 0.75" rgba="0.45 0.47 0.5 1"/>';
      const body = api.scene === "ball"
        ? `<body name="part" pos="0 0 ${P.r + api.p.h}"><freejoint/><geom type="sphere" size="${P.r}" mass="${P.m}" rgba="0.9 0.45 0.15 1"/></body>`
        : `<body name="part" pos="0 0 ${P.base + P.r + api.p.h}" quat="0.7071068 0.7071068 0 0"><freejoint/><geom type="cylinder" size="${P.r} 0.0908" mass="${P.m}" rgba="0.62 0.63 0.66 1"/></body>`;
      return `<mujoco><option timestep="${this.DT}"/><default><geom solref="${sr}"/></default><worldbody>${floor}${body}</worldbody></mujoco>`;
    },
  },
  reset(api, s) {
    s.t = 0; s.hits = []; s.cur = null; s.hist = []; s.fin = false;
    s.base = this.physics.part(api).base + this.physics.part(api).r;
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim, ph = this.physics, P = ph.part(api), TE = 3.0;
    if (s.fin) { api.stop(); return; }
    const n = Math.max(1, Math.round(dt / ph.DT));
    for (let k = 0; k < n && s.t < TE; k++) {
      mj.mj_step(m, d);
      s.t += ph.DT;
      const vz = d.qvel[2];
      if (d.ncon > 0) {
        const lam = P.m * (d.qacc[2] + ph.G);
        if (!s.cur) s.cur = { vin: -vz, t0: s.t, F: 0 };
        s.cur.F = Math.max(s.cur.F, lam);
      } else if (s.cur) {
        s.cur.e = s.cur.vin > 1e-3 ? vz / s.cur.vin : 0; s.cur.tc = s.t - s.cur.t0;
        if (s.cur.vin > 0.05) s.hits.push(s.cur);
        s.cur = null;
      }
      if (k % 20 === 0) s.hist.push([s.t, d.qpos[2] - s.base, d.ncon > 0 ? P.m * (d.qacc[2] + ph.G) : 0]);
    }
    if (s.t >= TE) {
      s.fin = true;
      const h1 = s.hits[0], e1 = h1 ? h1.e : 0;
      if (api.scene === "drop" && api.p.zeta >= 0.95 && (!h1 || e1 < 0.05)) api.done("nobounce");
      if (api.scene === "drop" && h1 && e1 >= 0.45 && e1 <= 0.55) api.done("half");
      const prev = api.keep.last;
      if (api.scene === "drop" && h1 && prev && Math.abs(prev.zeta - api.p.zeta) < 1e-9 && Math.abs(prev.h - api.p.h) < 1e-9) {
        const rt = api.p.tau / prev.tau, rc = h1.tc / prev.tc, rf = h1.F / prev.F;
        if (rt > 0.45 && rt < 0.55 && rc > 0.4 && rc < 0.6 && rf > 1.6 && rf < 2.4) api.done("tau");
      }
      if (api.scene === "drop" && h1) api.keep.last = { tau: api.p.tau, zeta: api.p.zeta, h: api.p.h, tc: h1.tc, F: h1.F };
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [], Fm = Math.max(10, ...H.map((r) => r[2]));
    const ymax = api.p.h * 1.1 + 0.01;
    api.cplot(48, 10, w - 60, h - 34, [{ pts: H.map((r) => [r[0], r[1]]), color: "#1f77b4" }, { pts: H.map((r) => [r[0], r[2] / Fm * ymax]), color: "#d62728" }],
      { xmin: 0, xmax: 3, ymin: -0.02 * ymax, ymax, xlabel: "t / s", ylabel: "z / m" });
    ctx.fillStyle = "#d62728"; ctx.font = "12px sans-serif"; ctx.textAlign = "right"; ctx.textBaseline = "middle";
    ctx.fillText(api.T("力的满刻度 ", "force full scale ") + api.fmt(Fm, 0) + " N", w - 12, 18);
  },
  readouts(api, s) {
    const f = (v, k = 3) => api.fmt(v, k), H = s.hits || [], z = api.p.zeta;
    const lin = z < 1 ? Math.exp(-Math.PI * z / Math.sqrt(1 - z * z)) : 0;
    const h1 = H[0];
    return [
      [["碰撞次数", "Impacts"], String(H.length)],
      [["第一次碰撞的恢复系数 e", "Restitution e of the first impact"], h1 ? f(h1.e, 3) : (s.fin ? api.T("0（不反弹）", "0 (no bounce)") : "—")],
      [["式 (27.3.4) 的线性预测", "Linear prediction by Eq. (27.3.4)"], f(lin, 3)],
      [["第一次碰撞：接触时间 / 峰值力", "First impact: contact time / peak force"], h1 ? `${f(h1.tc * 1000, 1)} ms / ${f(h1.F, 0)} N` : "—"],
      [["各次碰撞的 e", "e of each impact"], H.length ? H.slice(0, 6).map((x) => f(x.e, 2)).join(", ") : "—"],
    ];
  },
  tasks: [
    { id: "nobounce", robot: true, text: ["取 MuJoCo 的默认阻尼比 ζ = 1：毛坯落到料台上不反弹。", "Use MuJoCo's default damping ratio ζ = 1: the blank lands without bouncing."],
      demo: { scene: "drop", set: { h: 0.3, tau: 0.02, zeta: 1.0 }, wait: 5 } },
    { id: "half", robot: true, text: ["调阻尼比，使第一次碰撞的恢复系数在 0.45～0.55 之间。", "Tune the damping ratio so that the first impact has a restitution between 0.45 and 0.55."],
      demo: { scene: "drop", set: { h: 0.3, tau: 0.02, zeta: 0.25 }, wait: 5 } },
    { id: "tau", robot: true, text: ["阻尼比和高度不变，把时间常数减半再做一次：接触时间约减半，峰值力约加倍。", "Keep the damping ratio and height, halve the time constant and drop again: the contact time roughly halves and the peak force roughly doubles."],
      demo: { scene: "drop", set: { h: 0.3, tau: 0.01, zeta: 0.25 }, wait: 5 } },
  ],
  think: ["真实的钢件相撞，接触只持续几十微秒，峰值力比这里大得多（27.3.3 节）。用 MuJoCo 研究“毛坯会不会被撞坏”时，应该怎样看待它算出的峰值力？",
          "Real steel parts touch for only tens of microseconds and the peak force is far larger than here (Section 27.3.3). How should you read MuJoCo's peak force when asking whether the blank would be damaged?"],
});
