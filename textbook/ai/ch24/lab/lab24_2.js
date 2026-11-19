// 实验 24.2 域随机化的范围（配 24.2、24.5 节；与算例 24.2 同一套玩具）。
// 两个场景：
//   range ：固定仿真与真机的差距，扫随机化范围，看**仿真与真机两列**各怎么走；
//   gap   ：固定随机化范围的扫法，把仿真与真机的差距拉大，看“最好的范围”跟着往右跑。
// 与 code/_ch24.py 同口径：平面二连杆 + 腕关节，成功判据 **位置 2 cm 且 姿态 0.4 rad**，
// 仿真参数 l1 = 35.0 cm、l2 = 30.0 cm、摩擦 0.04、无噪声、无延迟。
// 本实验里“训练”不真的跑，而是按两条**显式假设**把随机化范围折成一条策略（见 yaml 的注意）：
//   ① 范围越宽，策略越不敢靠“按标称连杆长度心算正运动学”这条捷径，越要盯量出来的夹爪位姿；
//   ② 范围越宽，同一个观测对应的专家动作越矛盾，策略只能学个平均——增益偏小、动作带抖动。
WQ.lab({
  title: ["实验 24.2 域随机化的范围：窄了盖不住真机，宽了两列一起掉",
          "Lab 24.2 The randomisation range: too narrow misses the gap, too wide sinks both columns"],
  goal: ["第一个场景里先把随机化范围拖到 0，读两列成绩：仿真那一列很好看，真机那一列掉到谷底——这就是“只有仿真成功率的结果不采信”的样子。然后把范围一点一点拖大，盯住真机那一列什么时候爬到最高；再继续往宽拖，看两列怎么一起往下走。第二个场景把仿真与真机的差距拉大（摩擦、连杆长度、观测噪声、执行延迟），看“最好的范围”往哪边跑。做完要能回答：范围该按什么定，以及为什么验收报表上必须有两列。",
         "In the first scene set the randomisation range to zero and read both columns: the simulation column looks fine while the hardware column bottoms out — this is what 'a simulation-only number is not evidence' looks like. Then widen the range step by step and watch where the hardware column peaks, and keep widening to see both columns fall together. In the second scene widen the gap between simulation and hardware and watch the best range move. You should be able to say what sets the range, and why an acceptance report needs two columns."],
  scenes: [
    { id: "range", name: ["扫随机化范围", "Sweep the range"],
      problem: { title: ["问题：在仿真里训出来的策略，搬到真机上还剩多少", "Problem: how much of a simulator-trained policy survives the move to hardware?"],
                 text: ["车间里这台二连杆机械臂要把夹爪送到工件上，位置差 2 cm 以内、姿态差 0.4 rad 以内闭合夹爪才算抓到。策略在仿真里训，然后搬到真机上——而真机的摩擦更大、连杆长度与图纸差几毫米、观测带噪声、指令还要晚一拍。办法之一是**训练时就把这些参数抖起来**（域随机化）。这个场景让你亲手拖那个“抖多大”的范围，并把仿真与真机两列成绩并排放着看。",
                        "This two-link arm must bring its gripper to the part and close within 2 cm and 0.4 rad. The policy is trained in simulation and then moved to hardware — where friction is higher, the links differ from the drawing by millimetres, the measurements are noisy and commands arrive a tick late. One remedy is to randomise those parameters during training. Drag that range here, with the simulation and hardware columns side by side."] } },
    { id: "gap", name: ["拉大仿真与真机的差距", "Widen the sim-to-real gap"],
      problem: { title: ["问题：范围该照什么定", "Problem: what should set the range?"],
                 text: ["“范围调多少”听起来像个要试出来的超参数，其实它有个可讲的道理：**范围要盖得住你和真机之间那段差距**。这个场景让你把差距本身拖大——摩擦差一倍、连杆差三厘米、噪声更大、延迟更久——然后看读数里“真机那一列最高的范围”往哪边跑。两条真机曲线会同时画出来：虚线是出厂差距下的那条，实线是你现在这套差距下的那条。",
                        "'How wide should the range be' sounds like a hyperparameter to be found by trial, but there is a reason behind it: the range has to cover the gap between you and the hardware. Here you widen the gap itself and watch where the best range goes. Two hardware curves are drawn at once: dashed for the factory gap, solid for the gap you have set."] } },
  ],
  params: [
    { id: "range", name: ["域随机化范围", "randomisation range"], min: 0, max: 1.4, step: 0.05, value: 0.2, digits: 2 },
    { id: "dl", name: ["连杆长度与图纸差（mm）", "link-length error (mm)"], min: 0, max: 30, step: 1, value: 13, digits: 0 },
    { id: "fric", name: ["真机的关节摩擦", "hardware joint friction"], min: 0.04, max: 0.26, step: 0.01, value: 0.11, digits: 2 },
    { id: "noise", name: ["观测噪声（mm）", "observation noise (mm)"], min: 0, max: 11, step: 0.5, value: 4, digits: 1 },
    { id: "delay", name: ["执行延迟（控制周期）", "actuation delay (control steps)"], min: 0, max: 2, step: 1, value: 1, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["仿真成功率", "success in simulation"] },
           { color: "var(--red)", name: ["真机成功率", "success on hardware"] },
           { color: "var(--green)", name: ["你现在这一档", "where you are now"] },
           { color: "var(--muted)", name: ["真机那一列最高的那一档", "the best range for hardware"] }],
  tasks: [
    { id: "zero", text: ["第一个场景，出厂差距（13 mm / 0.11 / 4 mm / 1 拍）：把随机化范围拖到 0，把仿真与真机两列成绩都记下来，差多少个百分点？",
                         "In the first scene with the factory gap, set the range to 0 and record both columns: how many points apart are they?"],
      demo: { scene: "range", set: { range: 0, dl: 13, fric: 0.11, noise: 4, delay: 1 }, press: [] } },
    { id: "best", text: ["把范围一点一点拖大，直到真机那一列明显比范围 0 时高出二十个百分点以上：这时范围是多少？同一版在仿真里的成绩是升了还是降了？",
                         "Widen the range until the hardware column is more than twenty points above its value at range 0: what range is that, and did the simulation column rise or fall?"],
      demo: { scene: "range", set: { range: 0.2, dl: 13, fric: 0.11, noise: 4, delay: 1 }, press: [] } },
    { id: "wide", text: ["继续把范围拖到 1.4（最宽）：两列各变成多少？哪一列掉得更多？为什么“抖得越多越稳”是错的？",
                         "Push the range to 1.4: what happens to each column, which falls further, and why is 'the more randomisation the better' wrong?"],
      demo: { scene: "range", set: { range: 1.4, dl: 13, fric: 0.11, noise: 4, delay: 1 }, press: [] } },
    { id: "wider", text: ["切到第二个场景，把差距拉到最大（连杆差 30 mm、摩擦 0.26、噪声 11 mm、延迟 2 拍）：读数里“真机那一列最高的范围”跑到哪了？比出厂差距时宽了还是窄了？",
                          "In the second scene set the widest gap (30 mm, 0.26, 11 mm, 2 steps): where does the best range go, and is it wider or narrower than at the factory gap?"],
      demo: { scene: "gap", set: { dl: 30, fric: 0.26, noise: 11, delay: 2, range: 0.6 }, press: [] } },
    { id: "narrow", text: ["把差距缩到最小（连杆差 5 mm 以内、摩擦 0.06 以下、噪声 2 mm、延迟 0 拍）：最好的范围缩回哪里？这时范围 0 的真机成绩还差吗？这说明域随机化该按什么定？",
                           "Now shrink the gap (under 5 mm, under 0.06, 2 mm, no delay): where does the best range shrink to, how bad is range 0 now, and what does that say about how the range should be chosen?"],
      demo: { scene: "gap", set: { dl: 4, fric: 0.06, noise: 2, delay: 0, range: 0.1 }, press: [] } },
  ],
  think: ["把你们自己那台设备与仿真模型之间的差距列成一张表：连杆长度的装配公差、减速器的摩擦力矩、相机标定残差、控制链路的延迟各是多少，哪几项你量过、哪几项只是猜的。量过的那几项按实测范围随机化；只是猜的那几项，范围只能往宽留，而本实验告诉你**往宽留是要付钱的**——付在仿真那一列上。写不出这张表，就别先调随机化范围，先去把差距量出来。",
          "List the gap between your own machine and your model: assembly tolerance on the links, friction torque in the gearbox, camera calibration residual, latency in the control path — and mark which you have measured and which you have guessed. Randomise the measured ones over their measured range; for the guessed ones you must leave the range generous, and this lab shows that generosity has a price, paid in the simulation column. Without that table, measure the gap before tuning the range."],

  // ---------------- 同口径的玩具（与 code/_ch24.py 一致）
  L1S: 0.35, L2S: 0.30, DT: 0.05, VMAX: 1.6, GAIN: 3.5, STEPS: 60,
  TOL_P: 0.02, TOL_R: 0.4, CLOSE: 0.012,
  QMIN: [-2.6, -2.5, -2.2], QMAX: [2.6, 2.5, 2.2], QHOME: [0.55, 0.95, -0.30],
  NTEST: 40,                       // 两列各试多少次（**本章口径：真机那一列必须写明次数**）
  GRID: [0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.65, 0.8, 1.0, 1.2, 1.4],
  BASE: { dl: 13, fric: 0.11, noise: 4, delay: 1 },      // 出厂差距（= code/_ch24.py 的 REAL）

  rng(seed) { let x = (seed * 1103515245 + 12345) >>> 0; return () => { x = (x * 1103515245 + 12345) >>> 0; return x / 4294967296; }; },
  gauss(r) { const u = Math.max(r(), 1e-9), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  fk(q, l1, l2) {
    return [l1 * Math.cos(q[0]) + l2 * Math.cos(q[0] + q[1]),
            l1 * Math.sin(q[0]) + l2 * Math.sin(q[0] + q[1]), q[0] + q[1] + q[2]];
  },
  ik(p, l1, l2) {
    const c2 = (p[0] * p[0] + p[1] * p[1] - l1 * l1 - l2 * l2) / (2 * l1 * l2);
    if (c2 < -1 || c2 > 1) return null;
    const q2 = Math.acos(c2);
    const q1 = Math.atan2(p[1], p[0]) - Math.atan2(l2 * Math.sin(q2), l1 + l2 * Math.cos(q2));
    const q = [q1, q2, p[2] - q1 - q2];
    for (let i = 0; i < 3; i++) if (q[i] < this.QMIN[i] || q[i] > this.QMAX[i]) return null;
    return q;
  },
  targets() {                      // 工作空间里采一组工件位姿：两套参数下都够得到
    if (this._tg) return this._tg;
    const r = this.rng(31), out = [];
    while (out.length < this.NTEST) {
      const rad = 0.30 + 0.26 * r(), a = -0.35 + 1.60 * r(), th = -0.9 + 2.8 * r();
      const p = [rad * Math.cos(a), rad * Math.sin(a), th];
      if (this.ik(p, this.L1S, this.L2S) && this.ik(p, 0.38, 0.27)) out.push(p);
    }
    this._tg = out;
    return out;
  },
  world(g) {                       // 一套“真机”参数
    return { l1: this.L1S + g.dl / 1000, l2: this.L2S - g.dl / 1000 * 0.92,
             fric: g.fric, noise: g.noise / 1000, delay: Math.round(g.delay) };
  },
  simWorld() { return { l1: this.L1S, l2: this.L2S, fric: 0.04, noise: 0, delay: 0 }; },
  gapOf(g) {                       // 差距的大小（出厂差距记作 1.00；显式假设的加权）
    return 0.4 * (g.dl / this.BASE.dl) + 0.4 * ((g.fric - 0.04) / (this.BASE.fric - 0.04))
         + 0.1 * (g.noise / this.BASE.noise) + 0.1 * (g.delay / this.BASE.delay);
  },
  // 显式假设：范围 rg 折成的那条策略。rneed 是“盖住这段差距要多宽”。
  policy(rg, rneed) {
    const wm = rneed > 1e-9 ? Math.min(1, (rg / rneed) ** 2) : 1;
    return { wm, gain: this.GAIN * (1 - 0.30 * rg), sig: 0.18 * rg };
  },
  episode(p, W, P, seed) {
    const r = this.rng(seed);
    const q = [this.QHOME[0] + 0.18 * this.gauss(r), this.QHOME[1] + 0.18 * this.gauss(r),
               this.QHOME[2] + 0.18 * this.gauss(r)];
    const queue = [];
    for (let i = 0; i < W.delay; i++) queue.push([0, 0, 0]);
    for (let t = 0; t < this.STEPS; t++) {
      const tt = this.fk(q, W.l1, W.l2);
      const meas = [tt[0] + W.noise * this.gauss(r), tt[1] + W.noise * this.gauss(r)];
      const nom = this.fk(q, this.L1S, this.L2S);
      // 策略以为夹爪在哪：量出来的与心算出来的，按 wm 混
      const hx = P.wm * meas[0] + (1 - P.wm) * nom[0];
      const hy = P.wm * meas[1] + (1 - P.wm) * nom[1];
      const ex = p[0] - hx, ey = p[1] - hy, eth = p[2] - tt[2];
      if (Math.hypot(ex, ey) < this.CLOSE && Math.abs(eth) < 0.2) {       // 它认为到了 → 闭合夹爪
        const dp = Math.hypot(tt[0] - p[0], tt[1] - p[1]), dth = Math.abs(tt[2] - p[2]);
        return { ok: dp < this.TOL_P && dth < this.TOL_R, dp, t };
      }
      const s1 = Math.sin(q[0]), c1 = Math.cos(q[0]);
      const s12 = Math.sin(q[0] + q[1]), c12 = Math.cos(q[0] + q[1]);
      const a = [P.gain * ((-this.L1S * s1 - this.L2S * s12) * ex + (this.L1S * c1 + this.L2S * c12) * ey) / 0.1,
                 P.gain * ((-this.L2S * s12) * ex + (this.L2S * c12) * ey) / 0.1,
                 P.gain * eth];
      for (let i = 0; i < 3; i++) a[i] = Math.max(-1, Math.min(1, a[i] + P.sig * this.gauss(r)));
      queue.push(a);
      const ae = queue.shift();
      for (let i = 0; i < 3; i++) {
        q[i] = Math.max(this.QMIN[i], Math.min(this.QMAX[i], q[i] + (1 - W.fric) * ae[i] * this.VMAX * this.DT));
      }
    }
    const tt = this.fk(q, W.l1, W.l2);
    return { ok: false, dp: Math.hypot(tt[0] - p[0], tt[1] - p[1]), t: this.STEPS };
  },
  score(W, P) {
    const tg = this.targets();
    let n = 0, dp = 0;
    for (let k = 0; k < tg.length; k++) { const r = this.episode(tg[k], W, P, k * 7 + 5); if (r.ok) n++; dp += r.dp; }
    return { pct: n / tg.length * 100, dp: dp / tg.length };
  },
  at(g, rg) {                      // 一个设置下的两列成绩
    const rneed = 0.20 * Math.max(this.gapOf(g), 1e-6);
    const P = this.policy(rg, rneed);
    return { sim: this.score(this.simWorld(), P).pct, real: this.score(this.world(g), P),
             wm: P.wm, rneed };
  },
  sweep(g) {                       // 整条曲线（缓存：扫一遍要跑一千多个回合）
    const key = `${g.dl}|${g.fric}|${g.noise}|${g.delay}`;
    if (!this._sw) this._sw = {};
    if (this._sw[key]) return this._sw[key];
    const pts = this.GRID.map((rg) => { const r = this.at(g, rg); return [rg, r.sim, r.real.pct]; });
    let best = pts[0];
    pts.forEach((x) => { if (x[2] > best[2]) best = x; });
    this._sw[key] = { pts, best, zero: pts[0], gap: this.gapOf(g), rneed: 0.20 * Math.max(this.gapOf(g), 1e-6) };
    return this._sw[key];
  },
  gapOfP(q) { return { dl: q.dl, fric: q.fric, noise: q.noise, delay: Math.round(q.delay) }; },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p, g = this.gapOfP(q);
    const sw = this.sweep(g), now = this.at(g, q.range);
    const base = this.sweep(this.BASE);
    if (api.scene === "range") {
      if (q.range <= 0.001) api.done("zero");
      if (now.real.pct >= sw.zero[2] + 20 && q.range >= 0.05) api.done("best");
      if (q.range >= 1.35) api.done("wide");
    } else {
      if (q.dl >= 28 && q.fric >= 0.24 && q.noise >= 10 && q.delay >= 2) api.done("wider");
      if (q.dl <= 5 && q.fric <= 0.07 && q.noise <= 2.5 && q.delay <= 0) api.done("narrow");
    }
    return [[["随机化范围", "randomisation range"], q.range.toFixed(2)],
            [["仿真成功率", "success in simulation"], now.sim.toFixed(1) + "%"],
            [["真机成功率", "success on hardware"], now.real.pct.toFixed(1) + "%"],
            [["两列各试了多少次", "trials in each column"], String(this.NTEST)],
            [["两列差", "gap between the columns"], (now.sim - now.real.pct).toFixed(1) + api.T(" 个百分点", " points")],
            [["真机平均位置误差", "mean position error on hardware"], (now.real.dp * 100).toFixed(2) + " cm"],
            [["范围 0 时的真机成绩", "hardware at range 0"], sw.zero[2].toFixed(1) + "%"],
            [["真机那一列最高的范围", "best range for hardware"],
             sw.best[0].toFixed(2) + api.T(`（真机 ${sw.best[2].toFixed(1)}%、仿真 ${sw.best[1].toFixed(1)}%）`,
                                           ` (hardware ${sw.best[2].toFixed(1)}%, sim ${sw.best[1].toFixed(1)}%)`)],
            [["仿真与真机的差距", "size of the sim-to-real gap"],
             sw.gap.toFixed(2) + api.T("（出厂差距记作 1.00）", " (factory gap = 1.00)")],
            [["出厂差距下最好的范围", "best range at the factory gap"], base.best[0].toFixed(2)]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p, g = this.gapOfP(q);
    const sw = this.sweep(g), now = this.at(g, q.range);
    // 上图：两列成绩随随机化范围怎么走
    const G = api.graph({ x: 56, y: 28, w: w - 112, h: (h - 96) * 0.56,
                          xmin: 0, xmax: 1.4, ymin: 0, ymax: 100,
                          xlabel: api.T("域随机化范围", "randomisation range"),
                          ylabel: api.T("成功率（%）", "success rate (%)") }).axes();
    G.pts(sw.pts.map((p) => [p[0], p[1]]), api.css("--blue"), 2.4);
    G.pts(sw.pts.map((p) => [p[0], p[2]]), api.css("--red"), 2.8);
    sw.pts.forEach((p) => G.dots([[p[0], p[2]]], api.css("--red"), 3));
    if (api.scene === "gap") {
      const base = this.sweep(this.BASE);
      G.pts(base.pts.map((p) => [p[0], p[2]]), api.css("--muted"), 2, [5, 4]);
      G.text(api.T("灰虚线：出厂差距下的真机那一列", "grey dashed: the hardware column at the factory gap"),
             0.03, 8, api.css("--muted"), 12);
    }
    G.vline(q.range, api.css("--green"));
    G.vline(sw.best[0], api.css("--muted"));
    G.text(api.T("蓝：仿真　红：真机　绿：你现在这一档　灰：最好的那一档",
                 "blue: simulation, red: hardware, green: you are here, grey: the best range"),
           0.03, 96, api.css("--ink"), 12);

    // 下图：当前这一档的两列并排（**本章报表的样子**）
    const y0 = 28 + (h - 96) * 0.66, hh = (h - 96) * 0.34;
    const B = api.graph({ x: 56, y: y0, w: w - 112, h: hh, xmin: 0, xmax: 4, ymin: 0, ymax: 100,
                          xlabel: api.T(`两列各试 ${this.NTEST} 次`, `${this.NTEST} trials in each column`),
                          ylabel: api.T("成功率（%）", "success rate (%)"), ticks: true }).axes();
    const bars = [[1, now.sim, api.css("--blue"), api.T("仿真", "simulation")],
                  [3, now.real.pct, api.css("--red"), api.T("真机", "hardware")]];
    bars.forEach(([x, v, c, name]) => {
      api.rect(B.X(x - 0.55), B.Y(v), B.X(x + 0.55) - B.X(x - 0.55), B.Y(0) - B.Y(v), c);
      B.text(`${v.toFixed(1)}%`, x, Math.min(v + 9, 95), c, 14, "center");
      B.text(name, x, 6, api.css("--ink"), 13, "center");
    });
    B.hline(sw.zero[2], api.css("--muted"));
    B.text(api.T(`灰线：范围 0 时的真机成绩 ${sw.zero[2].toFixed(1)}%`,
                 `grey line: hardware at range 0, ${sw.zero[2].toFixed(1)}%`),
           0.06, 93, api.css("--muted"), 12);
  },
});
