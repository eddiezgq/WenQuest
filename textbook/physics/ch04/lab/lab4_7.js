// 实验 4.7 运动规划（配 4.7 节）。
// 梯形场景：AGV 走 6 m，要求 8.0 s 内到站，货物允许的加速度不超过 0.60 m/s²，安全限速 1.5 m/s。学生选最大速度和最大加速度，
// 点“开始”看 AGV 跑一趟，点“提交”判定。防摆场景：龙门小车移动 3.0 m（0.80 m/s、0.50 m/s²），绳长 1.2 m，学生选加速度上升时间 a/j，
// 程序用单摆方程（不作小角近似）计算停车后的残余摆幅。电梯场景：上升 30 m，最大速度 2.5 m/s，学生选加速度和加加速度。
// 速度曲线与 _kin.py 的 trapezoid、scurve 相同：加速度为两个对称的梯形（上升时间 a/j），距离不够时降低峰值速度。
function prof47(L, vm, am, tj) {                 // tj = a/j（0 表示梯形曲线）
  const acc = (vp) => { const t1 = Math.min(tj, Math.sqrt(vp * tj / am) || 0), ap = tj > 0 ? am * t1 / tj : am, tca = Math.max(0, vp / ap - t1), ta = 2 * t1 + tca; return { t1, ap, tca, ta, da: vp * ta / 2 }; };
  let vp = vm;
  if (2 * acc(vp).da > L) { let lo = 0, hi = vm; for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; if (2 * acc(m).da <= L) lo = m; else hi = m; } vp = lo; }
  const P = acc(vp), tc = (L - 2 * P.da) / vp, T = 2 * P.ta + tc;
  const bump = (u) => (u < 0 || u > P.ta) ? 0 : (P.t1 > 0 ? Math.max(0, Math.min(P.ap * u / P.t1, P.ap, P.ap * (P.ta - u) / P.t1)) : P.ap);
  const a = (t) => (t < 0 || t > T) ? 0 : bump(t) - bump(t - P.ta - tc);
  return { T, vp, ap: P.ap, a };
}
function run47(P, n = 1500) {                    // 速度、位置的数值积分（画图用）
  const dt = P.T / n, out = [[0, 0, 0, 0]]; let v = 0, x = 0;
  for (let i = 1; i <= n; i++) { const t = i * dt, am = P.a(t - dt / 2); x += v * dt + 0.5 * am * dt * dt; v += am * dt; out.push([t, x, v, P.a(t)]); }
  return out;
}
const LR47 = 1.2, G47 = 9.81, W47 = Math.sqrt(G47 / LR47);
const cache47 = {};
function sway47(tj) {                            // 残余摆幅（mm）与运动时间
  const key = tj.toFixed(2); if (cache47[key]) return cache47[key];
  const P = prof47(3.0, 0.8, 0.5, tj), f = (t, th, om) => [om, -(G47 / LR47) * Math.sin(th) - P.a(t) / LR47 * Math.cos(th)];
  let th = 0, om = 0; const N = Math.ceil(P.T / 0.002), h = P.T / N; const trace = [];
  for (let i = 0; i < N; i++) { const t = i * h;
    const k1 = f(t, th, om), k2 = f(t + h / 2, th + h / 2 * k1[0], om + h / 2 * k1[1]), k3 = f(t + h / 2, th + h / 2 * k2[0], om + h / 2 * k2[1]), k4 = f(t + h, th + h * k3[0], om + h * k3[1]);
    th += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); om += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); if (i % 10 === 0) trace.push([t, 1000 * LR47 * Math.sin(th)]); }
  const amp = 1000 * LR47 * Math.hypot(th, om / W47);
  for (let t = P.T; t < P.T + 6; t += 0.02) trace.push([t, amp * Math.sin(W47 * (t - P.T) + Math.atan2(th * W47, om))]);
  return (cache47[key] = { T: P.T, amp, trace });
}

WQ.lab({
  title: ["实验 4.7 运动规划", "Lab 4.7 Motion planning"],
  goal: ["为 AGV 设计满足时间与加速度限制的梯形速度曲线；用 S 形曲线减小吊挂货物的摆动；为电梯选择舒适又不太慢的运动参数。",
         "Design a trapezoidal profile for an AGV that meets time and acceleration limits; reduce the swing of a hanging load with an S-curve; choose comfortable but not too slow settings for a lift."],
  scenes: [
    { id: "trap", robot: true, name: ["AGV 到站", "AGV station run"], hide: ["tj", "la", "lj"],
      problem: { title: ["机器人问题：8 s 内开到 6 m 外的站点", "Robot problem: reach a station 6 m away within 8 s"],
                 text: ["AGV 载着货物，加速度不能超过 0.60 m/s²（否则货物会滑动），速度不能超过 1.5 m/s（安全限速）。选最大速度和最大加速度，使它在 8.0 s 内到站。点“开始”看它跑一趟，满意后点“提交”。",
                        "The loaded AGV must not accelerate faster than 0.60 m/s² (the load would slide) nor exceed 1.5 m/s (safety limit). Choose the top speed and acceleration so that it arrives within 8.0 s. Press “Start” to watch a run and “Submit” when satisfied."] } },
    { id: "sway", robot: true, name: ["龙门机器人防摆", "Anti-sway gantry"], hide: ["vm", "am", "la", "lj"],
      problem: { title: ["机器人问题：停车后货物不要晃", "Robot problem: no swinging after the stop"],
                 text: ["龙门小车吊着壳体移动 3.0 m（最大速度 0.80 m/s、最大加速度 0.50 m/s²），绳长 1.2 m。名义上升时间 a_m/j_m = 0 是梯形曲线。加大它（即减小加加速度），看停车后的摆幅和运动时间怎样变化。距离较短，上升时间较长时加速度来不及升到 0.50 m/s²，测量栏给出实际的峰值加速度。",
                        "The gantry trolley carries a hanging housing 3.0 m (0.80 m/s, 0.50 m/s²) on a 1.2 m rope. A nominal rise time a_m/j_m = 0 is the trapezoidal profile. Increase it (lower the jerk) and watch the residual swing and the move time. On this short move a long rise time keeps the acceleration below 0.50 m/s²; the readout shows the actual peak."] } },
    { id: "lift", name: ["电梯", "Lift"], hide: ["vm", "am", "tj"],
      problem: { title: ["生活中的例子：又快又舒服的电梯", "Everyday example: a quick but comfortable lift"],
                 text: ["电梯从 1 层到 11 层，上升 30 m，最大速度 2.5 m/s。乘客感到舒适要求加速度不超过 1.0 m/s²、加加速度不超过 1.0 m/s³，同时要求 16 s 内到达。选加速度和加加速度。",
                        "The lift rises 30 m from floor 1 to floor 11 at up to 2.5 m/s. Comfort needs acceleration ≤ 1.0 m/s² and jerk ≤ 1.0 m/s³, and the trip must take at most 16 s. Choose the acceleration and the jerk."] } },
  ],
  params: [
    { id: "vm", name: ["最大速度", "Top speed"], min: 0.2, max: 2.0, step: 0.05, value: 0.8, unit: "m/s", digits: 2 },
    { id: "am", name: ["最大加速度", "Maximum acceleration"], min: 0.1, max: 1.5, step: 0.05, value: 0.3, unit: "m/s²", digits: 2 },
    { id: "tj", name: ["名义上升时间 a_m/j_m（0 为梯形）", "Nominal rise time a_m/j_m (0 = trapezoidal)"], min: 0, max: 3, step: 0.1, value: 0, unit: "s", digits: 1 },
    { id: "la", name: ["电梯加速度", "Lift acceleration"], min: 0.3, max: 2.0, step: 0.05, value: 1.5, unit: "m/s²", digits: 2 },
    { id: "lj", name: ["电梯加加速度", "Lift jerk"], min: 0.3, max: 3.0, step: 0.05, value: 2.0, unit: "m/s³", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "trap", robot: true, text: ["AGV：选速度和加速度，使 8.0 s 内到站且不超过两个限制，提交。", "AGV: choose speed and acceleration so that it arrives within 8.0 s without breaking either limit, and submit."],
      demo: { scene: "trap", set: { vm: 1.2, am: 0.5 }, press: ["submit"], wait: 1 } },
    { id: "fast", robot: true, text: ["AGV：在两个限制之内，让到站时间尽量短（不超过最短时间 1%），提交。这时速度曲线是什么形状？", "AGV: within both limits make the trip as short as possible (within 1% of the minimum) and submit. What shape is the velocity profile?"],
      demo: { scene: "trap", set: { vm: 1.5, am: 0.6 }, press: ["submit"], wait: 1 } },
    { id: "sway", robot: true, text: ["防摆：选上升时间，使残余摆幅小于 30 mm，且运动时间不超过 7.5 s，提交。", "Anti-sway: choose a rise time giving a residual swing below 30 mm and a move time of at most 7.5 s, and submit."],
      demo: { scene: "sway", set: { tj: 2.0 }, press: ["submit"], wait: 1 } },
    { id: "lift", text: ["电梯：选加速度和加加速度，满足舒适要求且 16 s 内到达，提交。", "Lift: choose acceleration and jerk that are comfortable and still arrive within 16 s, and submit."],
      demo: { scene: "lift", set: { la: 1.0, lj: 1.0 }, press: ["submit"], wait: 1 } },
  ],
  think: ["由式 (4.7.1)，提高最大速度和提高加速度各在什么情况下更有效？防摆场景中，残余摆幅怎样随上升时间变化？上升时间要和摆动周期（约 2.2 s）相比多长，摆幅才明显减小？",
          "From Eq. (4.7.1), when does raising the top speed help more, and when does raising the acceleration? In the anti-sway scene, how does the residual swing change with the rise time, and how long must the rise time be compared with the swing period (about 2.2 s) before the swing drops markedly?"],

  reset(api, s) { s.x = 0; },
  change(api, s, pid) { s.msg = ""; },
  start(api, s) { s.x = 0; },
  update(dt, api, s) {
    const P = api.scene === "trap" ? prof47(6, api.p.vm, api.p.am, 0) : api.scene === "lift" ? prof47(30, 2.5, api.p.la, api.p.la / api.p.lj) : prof47(3, 0.8, 0.5, api.p.tj);
    if (api.t > P.T + 1) api.stop();
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "trap") {
      const P = prof47(6, p.vm, p.am, 0), Tmin = prof47(6, 1.5, 0.6, 0).T, legal = p.vm <= 1.5 + 1e-9 && p.am <= 0.6 + 1e-9;
      if (legal && P.T <= 8.0) { api.done("trap"); ok = true; }
      if (legal && P.T <= Tmin * 1.01) { api.done("fast"); ok = true; }
    }
    if (api.scene === "sway") { const S = sway47(p.tj); if (S.amp < 30 && S.T <= 7.5 + 1e-3) { api.done("sway"); ok = true; } }
    if (api.scene === "lift") { const P = prof47(30, 2.5, p.la, p.la / p.lj); if (p.la <= 1.0 + 1e-9 && p.lj <= 1.0 + 1e-9 && P.T <= 16) { api.done("lift"); ok = true; } }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "trap") { const P = prof47(6, p.vm, p.am, 0);
      return [[["到站时间", "Trip time"], f(P.T, 2) + " s"], [["实际峰值速度", "Peak speed reached"], f(P.vp, 2) + " m/s"],
        [["是否超限", "Limits"], p.vm > 1.5 || p.am > 0.6 ? api.T("超限", "exceeded") : api.T("未超限", "respected")], sub]; }
    if (api.scene === "sway") { const S = sway47(p.tj); return [[["运动时间", "Move time"], f(S.T, 2) + " s"], [["实际峰值加速度", "Actual peak acceleration"], f(prof47(3, 0.8, 0.5, p.tj).ap, 2) + " m/s²"], [["停车后的摆幅", "Residual swing"], f(S.amp, 0) + " mm"], [["摆动周期", "Swing period"], f(2 * Math.PI / W47, 2) + " s"], sub]; }
    const P = prof47(30, 2.5, p.la, p.la / p.lj);
    return [[["到达时间", "Trip time"], f(P.T, 2) + " s"], [["加速度、加加速度", "Acceleration, jerk"], `${f(p.la, 2)} m/s², ${f(p.lj, 2)} m/s³`],
      [["舒适", "Comfort"], p.la <= 1.0 && p.lj <= 1.0 ? api.T("舒适", "comfortable") : api.T("不舒适", "uncomfortable")], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, blue = css("--blue"), mut = css("--muted"), ink = css("--ink"), red = css("--red");
    if (api.scene === "trap" || api.scene === "lift") {
      const L = api.scene === "trap" ? 6 : 30, P = api.scene === "trap" ? prof47(6, p.vm, p.am, 0) : prof47(30, 2.5, p.la, p.la / p.lj), R = run47(P);
      const tmax = api.scene === "trap" ? 14 : 30, vmax = api.scene === "trap" ? 2.0 : 3.0;
      const G = api.graph({ x: 56, y: 22, w: w * 0.6, h: h * 0.42, xmin: 0, xmax: tmax, ymin: 0, ymax: vmax, xlabel: "t / s", ylabel: "v / (m/s)" }).axes();
      G.pts(R.map((q) => [q[0], q[2]]), blue, 2.5).vline(api.scene === "trap" ? 8 : 16, red);
      const A = api.graph({ x: 56, y: h * 0.42 + 70, w: w * 0.6, h: h * 0.3, xmin: 0, xmax: tmax, ymin: -2, ymax: 2, xlabel: "t / s", ylabel: "a / (m/s²)" }).axes();
      A.pts(R.map((q) => [q[0], q[3]]), red, 2);
      if (api.scene === "trap") A.hline(0.6, mut).hline(-0.6, mut); else A.hline(1.0, mut).hline(-1.0, mut);
      const t = Math.min(api.t || 0, P.T), k = Math.min(R.length - 1, Math.round(t / P.T * (R.length - 1))), xnow = R[k][1];
      const bx = w * 0.72, bw = w * 0.24;
      if (api.scene === "trap") { api.line(bx, h * 0.5, bx + bw, h * 0.5, mut, 2); api.agv(bx + 10 + xnow / L * (bw - 20), h * 0.5 - 2, 40);
        api.label(api.T("站点 A", "station A"), bx, h * 0.5 + 22, mut, 11); api.label(api.T("站点 B（6 m）", "station B (6 m)"), bx + bw, h * 0.5 + 22, mut, 11, "right"); }
      else { const topY = 30, bot = h - 40; api.rect(bx + bw / 2 - 30, topY, 60, bot - topY, null, mut); api.rect(bx + bw / 2 - 24, bot - 30 - xnow / L * (bot - topY - 40), 48, 30, blue);
        api.label(api.T("11 层", "floor 11"), bx + bw / 2 + 36, topY + 10, mut, 11); api.label(api.T("1 层", "floor 1"), bx + bw / 2 + 36, bot - 8, mut, 11); }
      return;
    }
    const S = sway47(p.tj), P = prof47(3, 0.8, 0.5, p.tj), R = run47(P);
    const G = api.graph({ x: 56, y: 22, w: w - 90, h: h * 0.38, xmin: 0, xmax: 14, ymin: 0, ymax: 1.0, xlabel: "t / s", ylabel: api.T("小车速度 / (m/s)", "trolley speed / (m/s)") }).axes();
    G.pts(R.map((q) => [q[0], q[2]]), blue, 2.5);
    const Z = api.graph({ x: 56, y: h * 0.38 + 70, w: w - 90, h: h * 0.38, xmin: 0, xmax: 14, ymin: -200, ymax: 200, xlabel: "t / s", ylabel: api.T("货物的水平摆动 / mm", "load swing / mm") }).axes();
    Z.pts(S.trace, red, 1.8).vline(S.T, mut);
    Z.text(api.T("竖线：小车停下", "line: trolley stops"), S.T + 0.2, 180, mut, 11);
  },
});
