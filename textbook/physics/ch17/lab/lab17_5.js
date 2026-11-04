// 实验 17.5 双摆的混沌（配 17.5 节）。
// 双摆场景（生活中的例子，桌上的双摆玩具）：两根长 0.50 m 的轻杆，上摆球 1.0 kg，下摆球 0.50 kg（与习题 17.5.4 的等质量不同）。
// 小角度时同相简正模式的形状 θ₂/θ₁ = √3、周期 1.78 s（学生不知道）；用单摆公式算会得到 1.42 s 或 2.01 s。角度都从竖直向下量起（绝对角）。
// 断电机械臂场景（机器人问题）：参数同算例 17.5.1，从 q = (30°, 0°) 静止释放，τ = 0；另一只臂 q₁ 的初值多 10^k 度（编码器误差）。
// 两只臂都用 RK4（步长 1 ms）积分 10 s，看末端相差超过 10 cm 的时刻。k = −5 时约 6.8 s，k = −4 时约 4.4 s，所以“5 s 内可预测”要 k ≤ −5。
const M1_175 = 1.0, M2_175 = 0.5, L175 = 0.50, g175 = 9.81;
const A175 = { m1: 8.4, c1: 0.21, L1: 0.425, I1: 0.13, m2: 2.3, c2: 0.196, L2: 0.392, I2: 0.031 };
const R175 = Math.sqrt(3);
const TM175 = (() => {                                                         // 同相简正模式的周期（小角度）
  const m1 = M1_175, m2 = M2_175, l = L175, g = g175;
  const a = (m1 + m2) * l * l, b = m2 * l * l, c = m2 * l * l, k1 = (m1 + m2) * g * l, k2 = m2 * g * l;
  const det = a * c - b * b, A = (c * k1) / det, B = (-b * k2) / det, C = (-b * k1) / det, D = (a * k2) / det;   // M⁻¹K
  const tr = A + D, dd = A * D - B * C, w2 = (tr - Math.sqrt(tr * tr - 4 * dd)) / 2;
  return 2 * Math.PI / Math.sqrt(w2);
})();
const CACHE175 = {};

function rk4_175(f, y, h) {
  const k1 = f(y), k2 = f(y.map((v, i) => v + h / 2 * k1[i])), k3 = f(y.map((v, i) => v + h / 2 * k2[i])), k4 = f(y.map((v, i) => v + h * k3[i]));
  return y.map((v, i) => v + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
}
function dp175(y) {                                                          // y = [θ₁, θ₂, ω₁, ω₂]，质点双摆
  const [t1, t2, w1, w2] = y, m1 = M1_175, m2 = M2_175, l = L175, g = g175, d = t1 - t2, den = m1 + m2 * Math.sin(d) ** 2;
  const a1 = (m2 * g * Math.sin(t2) * Math.cos(d) - m2 * Math.sin(d) * (l * w1 * w1 * Math.cos(d) + l * w2 * w2) - (m1 + m2) * g * Math.sin(t1)) / (l * den);
  const a2 = ((m1 + m2) * (l * w1 * w1 * Math.sin(d) - g * Math.sin(t2) + g * Math.sin(t1) * Math.cos(d)) + m2 * l * w2 * w2 * Math.sin(d) * Math.cos(d)) / (l * den);
  return [w1, w2, a1, a2];
}
function arm175(y) {                                                         // y = [q₁, q₂, q̇₁, q̇₂]，式 (17.5.2)，τ = 0
  const { m1, c1, L1, I1, m2, c2, I2 } = A175, [q1, q2, d1, d2] = y;
  const M11 = I1 + I2 + m1 * c1 * c1 + m2 * (L1 * L1 + c2 * c2 + 2 * L1 * c2 * Math.cos(q2));
  const M12 = I2 + m2 * (c2 * c2 + L1 * c2 * Math.cos(q2)), M22 = I2 + m2 * c2 * c2, h = m2 * L1 * c2 * Math.sin(q2);
  const g1 = g175 * ((m1 * c1 + m2 * L1) * Math.cos(q1) + m2 * c2 * Math.cos(q1 + q2)), g2 = g175 * m2 * c2 * Math.cos(q1 + q2);
  const b1 = h * (2 * d1 * d2 + d2 * d2) - g1, b2 = -h * d1 * d1 - g2, det = M11 * M22 - M12 * M12;
  return [d1, d2, (M22 * b1 - M12 * b2) / det, (M11 * b2 - M12 * b1) / det];
}
const end175 = (q) => [A175.L1 * Math.cos(q[0]) + A175.L2 * Math.cos(q[0] + q[1]), A175.L1 * Math.sin(q[0]) + A175.L2 * Math.sin(q[0] + q[1])];

function runDP175(th1, th2) {
  const key = `d|${th1}|${th2}`; if (CACHE175[key]) return CACHE175[key];
  const h = 0.001, every = 10, tEnd = 30, r = Math.PI / 180;
  let y = [th1 * r, th2 * r, 0, 0], prev = y[0]; const Y = [y.slice(0, 2)], cross = [];
  for (let i = 1; i <= Math.round(tEnd / h); i++) {
    y = rk4_175(dp175, y, h);
    if (prev < 0 && y[0] >= 0) cross.push(i * h - h * y[0] / (y[0] - prev));
    prev = y[0];
    if (i % every === 0) Y.push(y.slice(0, 2));
  }
  return (CACHE175[key] = { dt: h * every, Y, tEnd, cross });
}
function runArm175(k) {
  const key = `a|${k}`; if (CACHE175[key]) return CACHE175[key];
  const h = 0.001, every = 10, tEnd = 10, r = Math.PI / 180;
  let a = [30 * r, 0, 0, 0], b = [30 * r + Math.pow(10, k) * r, 0, 0, 0], tsep = null;
  const A = [a.slice(0, 2)], B = [b.slice(0, 2)], S = [0];
  for (let i = 1; i <= Math.round(tEnd / h); i++) {
    a = rk4_175(arm175, a, h); b = rk4_175(arm175, b, h);
    const ea = end175(a), eb = end175(b), dist = Math.hypot(ea[0] - eb[0], ea[1] - eb[1]);
    if (tsep === null && dist > 0.10) tsep = i * h;
    if (i % every === 0) { A.push(a.slice(0, 2)); B.push(b.slice(0, 2)); S.push(dist); }
  }
  return (CACHE175[key] = { dt: h * every, A, B, S, tEnd, tsep });
}
const tsep175 = (k) => { const t = runArm175(k).tsep; return t === null ? Infinity : t; };
const idx175 = (r, t) => Math.min(r.tEnd / r.dt, Math.max(0, Math.round(t / r.dt)));
const RUN175 = {};
const key175 = (api, p) => { p = p || api.p; return api.scene === "dp" ? `d|${p.th1}|${p.th2}` : `a|${p.k}`; };
const pow175 = (k) => "1×10" + String(k).replace("-", "⁻").replace(/\d/g, (c) => "⁰¹²³⁴⁵⁶⁷⁸⁹"[+c]) + "°";

WQ.lab({
  title: ["实验 17.5 双摆的混沌", "Lab 17.5 Chaos in the double pendulum"],
  goal: ["找出双摆的同相简正模式，测出它的周期；看断电的两连杆机械臂对初始误差有多敏感，求在 5 s 内预测末端位置所需的初始精度。",
         "Find the double pendulum's in-phase normal mode and measure its period; see how sensitive an unpowered two-link arm is to its starting error, and find the starting accuracy needed to predict the end effector for 5 s."],
  scenes: [
    { id: "arm", robot: true, name: ["断电的机械臂", "Unpowered robot arm"], hide: ["th1", "th2", "ans"],
      problem: { title: ["机器人问题：断电后的机械臂会落到哪里，能预测吗？", "Robot problem: can we predict where an unpowered arm will swing?"],
                 text: ["两连杆机械臂（参数同算例 17.5.1）断电、抱闸失灵，从大臂向上 30°、小臂伸直的姿态静止释放，不计摩擦。旁边一只一模一样的臂，只是大臂的初始角度多了一点点（编码器的误差 10^k 度）。选 k，点“开始”，看两只臂什么时候分开。",
                        "A two-link arm (parameters as in Example 17.5.1) loses power and its brakes fail; it is released from rest with the upper arm 30° up and the forearm straight, with no friction. Beside it is an identical arm whose upper-arm angle starts a tiny bit larger (an encoder error of 10^k degrees). Choose k, press “Start” and see when the two arms part ways."] } },
    { id: "dp", name: ["双摆", "Double pendulum"], hide: ["k"],
      problem: { title: ["生活中的例子：桌上的双摆玩具", "Everyday example: a desktop double pendulum"],
                 text: ["两根长 0.50 m 的轻杆，上摆球 1.0 kg，下摆球 0.50 kg，不计摩擦。θ₁、θ₂ 是两根杆与竖直向下方向的夹角（逆时针为正）。设定两个初始角度，从静止释放，点“开始”。",
                        "Two light rods 0.50 m long; the upper bob is 1.0 kg, the lower 0.50 kg; no friction. θ₁ and θ₂ are the rods' angles from straight down (anticlockwise positive). Set both starting angles, release from rest, and press “Start”."] } },
  ],
  params: [
    { id: "k", name: ["编码器误差 10^k 度：k", "Encoder error 10^k degrees: k"], min: -9, max: -1, step: 1, value: -2, unit: "", digits: 0 },
    { id: "th1", name: ["上杆的初始角 θ₁", "Upper rod starting angle θ₁"], min: -180, max: 180, step: 0.5, value: 90, unit: "°", digits: 1 },
    { id: "th2", name: ["下杆的初始角 θ₂", "Lower rod starting angle θ₂"], min: -180, max: 180, step: 0.05, value: 90, unit: "°", digits: 2 },
    { id: "ans", name: ["你测得的周期", "Your period"], min: 0.50, max: 3.00, step: 0.005, value: 0.50, unit: "s", digits: 3 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "predict", robot: true, text: ["断电的机械臂：要在释放后 5 s 内预测末端的位置（误差不超过 10 cm），编码器的误差最大允许多大？选出满足要求的最大的 10^k，运行后提交。", "Unpowered arm: to predict the end effector for 5 s after release (within 10 cm), how large may the encoder error be? Choose the largest 10^k that works, run and submit."],
      demo: { scene: "arm", set: { k: -5 }, press: ["start", "submit"], wait: 2 } },
    { id: "mode", text: ["双摆：θ₁ 取 2°～10° 之间的一个值，调 θ₂，使两根杆始终同方向摆动、形状不变（简正模式，θ₂/θ₁ 相差 0.03 以内），运行后提交。", "Double pendulum: with θ₁ between 2° and 10°, adjust θ₂ so the two rods always swing together without changing shape (a normal mode, θ₂/θ₁ within 0.03), run and submit."],
      demo: { scene: "dp", set: { th1: 5, th2: 8.65 }, press: ["start", "submit"], wait: 2 } },
    { id: "period", text: ["双摆：在简正模式下测出周期（多测几个周期），调到“你测得的周期”，与简正模式的设定一起运行后提交（相差 0.02 s 以内）。", "Double pendulum: in the normal mode, measure the period (time several swings), set it as “Your period”, and submit after a run in the normal mode (within 0.02 s)."],
      demo: { scene: "dp", set: { th1: 5, th2: 8.65, ans: 1.78 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["初始误差每缩小 10 倍，可预测的时间大约增加多少？要多预测 10 s，编码器要精确多少倍？把同相模式的 θ₂ 改成相反的符号会怎样？双摆从 θ₁ = θ₂ = 90° 释放，与小角度时有什么不同？",
          "Each time the starting error shrinks tenfold, how much longer can you predict? To predict 10 s more, how much more precise must the encoder be? What happens if you flip the sign of θ₂ from the in-phase mode? Released from θ₁ = θ₂ = 90°, how does the double pendulum differ from small swings?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; },
  start(api, s) {
    s.ran = true; s.k = Object.assign({}, api.p);
    s.r = api.scene === "dp" ? runDP175(api.p.th1, api.p.th2) : runArm175(api.p.k);
  },
  update(dt, api, s) { if (s.r && api.t >= s.r.tEnd) { RUN175[key175(api, s.k)] = true; api.stop(); } },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = s.ran && s.k ? Object.assign({}, s.k, { ans: api.p.ans }) : api.p, have = s.ran || RUN175[key175(api)]; let ok = false;
    if (api.scene === "arm" && have && tsep175(p.k) >= 5 && (p.k === -1 || tsep175(p.k + 1) < 5)) { api.done("predict"); ok = true; }
    if (api.scene === "dp" && have) {
      const inMode = Math.abs(p.th1) >= 2 && Math.abs(p.th1) <= 10 && Math.abs(p.th2 / p.th1 - R175) <= 0.03;
      if (inMode) { api.done("mode"); ok = true; }
      if (inMode && Math.abs(p.ans - TM175) <= 0.02) { api.done("period"); ok = true; }
    }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, sub = [["提交结果", "Submission"], s.msg || "—"], live = s.ran && s.r, t = live ? Math.min(api.t, s.r.tEnd) : 0;
    if (api.scene === "arm") {
      const k = live ? s.k.k : api.p.k, rows = [[["编码器误差", "Encoder error"], pow175(k)]];
      if (!live) return rows.concat([[["时间", "Time"], "—"], [["两只臂末端的距离", "Distance between the two end effectors"], "—"], sub]);
      const r = s.r, i = idx175(r, t);
      rows.push([["时间", "Time"], f(t, 2) + " s"], [["两只臂末端的距离", "Distance between the two end effectors"], r.S[i] < 1e-3 ? f(r.S[i] * 1e6, 1) + " μm" : f(r.S[i] * 1000, 1) + " mm"]);
      rows.push([["末端相差超过 10 cm 的时刻", "Time the ends are 10 cm apart"], r.tsep !== null && r.tsep <= t ? f(r.tsep, 2) + " s" : (t >= r.tEnd - 1e-9 ? api.T("10 s 内没有", "not within 10 s") : "—")]);
      return rows.concat([sub]);
    }
    if (!live) return [[["时间", "Time"], "—"], [["θ₁、θ₂", "θ₁, θ₂"], "—"], sub];
    const r = s.r, q = r.Y[idx175(r, t)], c = r.cross.filter((x) => x <= t);
    return [[["时间", "Time"], f(t, 2) + " s"], [["θ₁、θ₂", "θ₁, θ₂"], f(q[0] * 180 / Math.PI, 2) + "°，" + f(q[1] * 180 / Math.PI, 2) + "°"],
            [["上杆由左向右越过竖直的次数", "Times the upper rod has crossed vertical moving right"], String(c.length)],
            [["最近一次越过的时刻", "Time of the latest crossing"], c.length ? f(c[c.length - 1], 3) + " s" : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue");
    const live = s.ran && s.r, t = live ? Math.min(api.t, s.r.tEnd) : 0, r = Math.PI / 180;
    if (api.scene === "arm") {
      const sc = Math.min(w, h) * 0.5 / 0.85, cx = w * 0.5, cy = h * 0.5;
      const k = live ? s.k.k : api.p.k, i = live ? idx175(s.r, t) : 0;
      const qa = live ? s.r.A[i] : [30 * r, 0], qb = live ? s.r.B[i] : [30 * r + Math.pow(10, k) * r, 0];
      const draw = (q, col, wd) => {
        const ex = cx + A175.L1 * sc * Math.cos(q[0]), ey = cy - A175.L1 * sc * Math.sin(q[0]), e = end175(q);
        api.line(cx, cy, ex, ey, col, wd); api.line(ex, ey, cx + e[0] * sc, cy - e[1] * sc, col, wd * 0.7);
        api.circle(ex, ey, 5, col, ink); api.circle(cx + e[0] * sc, cy - e[1] * sc, 6, col, ink);
      };
      draw(qb, red, 12); draw(qa, blue, 8);
      api.rect(cx - 14, cy - 14, 28, 28, mut, ink, 4);
      api.label(api.T("蓝：标称；红：初始角多 " + pow175(k), "blue: nominal; red: starts " + pow175(k) + " higher"), 12, 20, mut, 12);
      return;
    }
    const sc = Math.min(w, h) * 0.45 / (2 * L175), cx = w * 0.5, cy = h * 0.42;
    const q = live ? s.r.Y[idx175(s.r, t)] : [api.p.th1 * r, api.p.th2 * r];
    const x1 = cx + L175 * sc * Math.sin(q[0]), y1 = cy + L175 * sc * Math.cos(q[0]);
    const x2 = x1 + L175 * sc * Math.sin(q[1]), y2 = y1 + L175 * sc * Math.cos(q[1]);
    if (live) {                                                                 // 下摆球最近 3 s 的轨迹
      const i1 = idx175(s.r, t), i0 = Math.max(0, i1 - Math.round(3 / s.r.dt)); let pv = null;
      for (let i = i0; i <= i1; i += 2) {
        const a = s.r.Y[i], px = cx + L175 * sc * (Math.sin(a[0]) + Math.sin(a[1])), py = cy + L175 * sc * (Math.cos(a[0]) + Math.cos(a[1]));
        if (pv) api.line(pv[0], pv[1], px, py, mut, 1); pv = [px, py];
      }
    }
    api.line(cx, cy, cx, cy + 2 * L175 * sc + 20, mut, 1, [4, 4]);
    api.line(cx, cy, x1, y1, ink, 4); api.line(x1, y1, x2, y2, ink, 4);
    api.circle(cx, cy, 5, mut, ink); api.circle(x1, y1, 13, blue, ink); api.circle(x2, y2, 9, red, ink);
  },
});
