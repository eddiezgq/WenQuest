// 实验 6.5 弹簧与力传感器（配 6.5 节）。三个场景：标定弹簧的劲度系数；机械臂竖直提起零件时腕部力传感器的读数；电梯里的体重秤。
const rec6_5 = { pts: [] };            // 记录的 (F, x) 数据，重置时不丢
const K6_5 = 1650, G6_5 = 9.81;        // 弹簧的真实劲度系数 N/m（学生不知道，与正文算例不同）；g
const read6_5 = (m) => {
  const F = m * G6_5;
  const x = F / K6_5 * 1000 + (Math.random() * 2 - 1) * 0.05;     // 读到 0.05 mm 以内
  return [F, Math.round(x * 100) / 100];
};
const fin6_5 = (api, s) => {
  const m = api.p.mpart;
  if (api.scene === "arm") {
    if (s.maxF > 25) api.done("heavy");
    if (s.minF < 0.5 * m * G6_5) api.done("light");
  }
  if (api.scene === "life" && Math.abs(m - 60) < 0.1 && s.maxF / G6_5 >= 66) api.done("lift");
};

WQ.lab({
  title: ["实验 6.5 弹簧与力传感器", "Lab 6.5 Springs and force sensors"],
  goal: ["用砝码标定弹簧的劲度系数；再看力传感器和体重秤在加速时读出的是什么。",
         "Calibrate a spring with weights; then see what a force sensor and a bathroom scale read while accelerating."],
  scenes: [
    { id: "spring", robot: true, name: ["标定弹簧", "Calibrate a spring"], hide: ["a", "mpart"],
      problem: { title: ["机器人问题：串联弹性驱动器里的弹簧", "Robot problem: the spring in a series elastic actuator"],
                 text: ["关节里串一根弹簧，测出它的伸长就知道传过去的力，前提是知道劲度系数 k。挂砝码、读伸长，用最小二乘求 k。",
                        "A spring in series with a joint turns its extension into a force reading — once its stiffness k is known. Hang weights, read the extension, fit k by least squares."] } },
    { id: "arm", robot: true, name: ["机械臂提零件", "Arm lifts a part"], hide: ["mass", "khat"],
      problem: { title: ["机器人问题：腕部力传感器读到什么", "Robot problem: what the wrist force sensor reads"],
                 text: ["UR5e 夹着零件竖直上提：先以加速度 a 加速 0.2 s，匀速 0.4 s，再以同样大小的加速度减速 0.2 s。传感器读数 F = m(g + a)。",
                        "The UR5e lifts a part vertically: accelerating at a for 0.2 s, steady for 0.4 s, then slowing down at the same rate for 0.2 s. The sensor reads F = m(g + a)."] } },
    { id: "life", name: ["电梯里的体重秤", "A scale in a lift"], hide: ["mass", "khat"],
      params: { mpart: { min: 40, max: 100, step: 5, value: 60 }, a: { min: -3, max: 3, step: 0.1, value: 1 } },
      problem: { title: ["生活中的例子：电梯起动时“变重”", "Everyday example: feeling heavier as the lift starts"],
                 text: ["站在体重秤上坐电梯，起动和停下时秤的读数会变。秤按 mg 标定，读数其实是支持力除以 g。",
                        "Stand on a scale in a lift: the reading changes as it starts and stops. The scale is calibrated for mg, so it shows the normal force divided by g."] } },
  ],
  params: [
    { id: "mass", name: ["砝码质量", "Hanging mass"], min: 0, max: 1, step: 0.1, value: 0.5, unit: "kg", digits: 1 },
    { id: "khat", name: ["你算出的 k", "Your k"], min: 1000, max: 3000, step: 5, value: 1500, unit: "N/m", digits: 0 },
    { id: "mpart", name: ["质量 m（零件或人）", "Mass m (part or person)"], min: 0.5, max: 5, step: 0.5, value: 2, unit: "kg", digits: 1 },
    { id: "a", name: ["加速度大小 a", "Acceleration a"], min: 0, max: 5, step: 0.5, value: 3, unit: "m/s²", digits: 1 },
  ],
  buttons: [{ id: "record", name: ["读数并记录", "Read and record"], primary: true }, { id: "sweep", name: ["0–1 kg 依次挂一遍", "Hang 0–1 kg in turn"] },
            { id: "clear", name: ["清空记录", "Clear records"] }, { id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--accent)", name: ["记录的数据", "recorded data"] }, { color: "var(--red)", name: ["力传感器读数", "sensor reading"] }],
  tasks: [
    { id: "k", robot: true, text: ["至少记录 6 个点，自己用最小二乘算出 k，把“你算出的 k”调到与真实值相差 2% 以内。",
                                    "Record at least 6 points, fit k yourself, and set “your k” within 2% of the true value."],
      demo: { scene: "spring", set: { khat: 1650 }, press: ["clear", "sweep"], wait: 2 } },
    { id: "heavy", robot: true, text: ["机械臂：让力传感器的最大读数超过 25 N。", "Arm: make the largest sensor reading exceed 25 N."],
      demo: { scene: "arm", set: { mpart: 2, a: 3 }, press: ["start"], wait: 2 } },
    { id: "light", robot: true, text: ["机械臂：让减速段的读数小于静止时的一半（零件仍被夹着向上运动）。", "Arm: make the reading while slowing down less than half the reading at rest (the part still moves up)."],
      demo: { scene: "arm", set: { mpart: 2, a: 5 }, press: ["start"], wait: 2 } },
    { id: "lift", text: ["电梯：60 kg 的人，让秤在起动时显示 66 kg 以上。", "Lift: for a 60 kg person, make the scale show at least 66 kg while starting."],
      demo: { scene: "life", set: { mpart: 60, a: 1 }, press: ["start"], wait: 2 } },
  ],
  think: ["力传感器测的是零件的重力吗？零件静止、向上加速、向上减速时，传感器测的分别是什么力？",
          "Does the force sensor measure the part's weight? What force does it measure at rest, speeding up and slowing down?"],

  reset(api, s) { s.hist = []; s.maxF = null; s.minF = null; s.y = 0; s.v = 0; s.last = null; },
  update(dt, api, s) {
    if (api.scene === "spring") { api.stop(); return; }
    const t = api.t, a = api.p.a;
    const acc = t < 0.2 ? a : t < 0.6 ? 0 : t < 0.8 ? -a : 0;
    s.v += acc * dt; s.y += s.v * dt;
    const m = api.p.mpart, F = m * (G6_5 + acc);
    s.hist.push([t, F]);
    if (t > 0.05) { s.maxF = s.maxF === null ? F : Math.max(s.maxF, F); s.minF = s.minF === null ? F : Math.min(s.minF, F); }
    if (t >= 1.0) { api.stop(); fin6_5(api, s); }
  },
  action(id, api, s) {
    if (api.scene !== "spring") return;
    if (id === "clear") rec6_5.pts.length = 0;
    if (id === "record") rec6_5.pts.push(read6_5(api.p.mass));
    if (id === "sweep") for (let k = 0; k <= 10; k++) rec6_5.pts.push(read6_5(k / 10));
    s.last = rec6_5.pts[rec6_5.pts.length - 1] || null;
    if (rec6_5.pts.length >= 6 && Math.abs(api.p.khat - K6_5) / K6_5 < 0.02) api.done("k");
  },
  change(api, s, pid) {
    if (pid === "khat" && rec6_5.pts.length >= 6 && Math.abs(api.p.khat - K6_5) / K6_5 < 0.02) api.done("k");
  },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "spring") {
      return [[["砝码重力 mg", "Weight mg"], f(api.p.mass * G6_5, 3) + " N"],
              [["最近一次读数", "Last reading"], s.last ? f(s.last[1], 2) + " mm" : "—"],
              [["已记录点数", "Points recorded"], String(rec6_5.pts.length)]];
    }
    const m = api.p.mpart, now = s.hist.length ? s.hist[s.hist.length - 1][1] : m * G6_5;
    const rows = [[["静止时 mg", "At rest mg"], f(m * G6_5, 2) + " N"],
                  [["当前读数", "Reading now"], f(now, 2) + " N"],
                  [["最大 / 最小读数", "Largest / smallest"], s.maxF === null ? "—" : f(s.maxF, 2) + " / " + f(s.minF, 2) + " N"]];
    if (api.scene === "life") rows.push([["秤显示（读数 ÷ g）", "Scale shows (reading ÷ g)"], f(now / G6_5, 1) + " kg"]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    if (api.scene === "spring") {
      // 左：竖直的弹簧、砝码和刻度尺；右：记录的 F–x 点
      const top = 30, x0 = w * 0.18, ext = api.p.mass * G6_5 / K6_5 * 1000;     // mm
      const L = h * 0.35 + ext * 12;
      api.line(x0 - 50, top, x0 + 50, top, css("--ink"), 4);
      const n = 14, amp = 12;
      let px = x0, py = top;
      for (let i = 1; i <= n; i++) { const qx = x0 + (i === n ? 0 : (i % 2 ? amp : -amp)), qy = top + L * i / n; api.line(px, py, qx, qy, css("--ink"), 2); px = qx; py = qy; }
      const ms = 20 + api.p.mass * 30;
      api.rect(x0 - ms / 2, top + L, ms, ms * 0.8, css("--amber"), css("--ink"), 3);
      for (let mm = 0; mm <= 7; mm++) { const yy = top + h * 0.35 + mm * 12; api.line(x0 + 60, yy, x0 + 70, yy, css("--muted"), 1); api.label(mm + "", x0 + 74, yy + 4, css("--muted"), 11); }
      api.label("mm", x0 + 70, top + h * 0.35 - 8, css("--muted"), 11);
      const P = api.plot(w * 0.45, 24, w * 0.5, h - 60, [{ pts: [], color: css("--accent") }],
                         { xmin: 0, xmax: 10, ymin: 0, ymax: 6.5, xlabel: "F / N", ylabel: "x / mm" });
      rec6_5.pts.forEach((p) => api.circle(P.X(p[0]), P.Y(p[1]), 4, css("--accent"), css("--ink")));
      return;
    }
    const life = api.scene === "life";
    const x0 = w * 0.22, base = h * 0.85, ppm = h * 0.6;
    if (life) {
      const cy = base - 30 - s.y * ppm * 0.5;
      api.rect(x0 - 70, cy - 170, 140, 170, css("--panel"), css("--ink"), 6);
      api.rect(x0 - 30, cy - 12, 60, 10, css("--ink"));
      api.circle(x0, cy - 140, 14, css("--accent")); api.line(x0, cy - 126, x0, cy - 60, css("--accent"), 6);
      api.line(x0, cy - 60, x0 - 12, cy - 14, css("--accent"), 5); api.line(x0, cy - 60, x0 + 12, cy - 14, css("--accent"), 5);
    } else {
      api.rect(x0 - 40, base - 20, 80, 20, css("--panel"), css("--ink"), 4);
      const gy = base - 160 - s.y * ppm;
      api.line(x0, base - 20, x0, gy, css("--accent"), 12);
      api.rect(x0 - 16, gy - 14, 32, 14, css("--ink"));
      api.label(api.T("力传感器", "F/T sensor"), x0 + 22, gy - 4, css("--muted"), 12);
      api.rect(x0 - 18, gy, 36, 30, css("--amber"), css("--ink"), 3);
      const now = s.hist.length ? s.hist[s.hist.length - 1][1] : api.p.mpart * G6_5;
      api.arrow(x0 + 30, gy + 15, x0 + 30, gy + 15 - now * 3, css("--red"), 3);
    }
    const P = api.plot(w * 0.45, 24, w * 0.5, h - 60, [{ pts: s.hist, color: css("--red") }],
      { xmin: 0, xmax: 1.0, ymin: 0, ymax: Math.max(30, api.p.mpart * (G6_5 + Math.abs(api.p.a)) * 1.15), xlabel: "t / s", ylabel: "F / N" });
    const m = api.p.mpart;
    api.line(P.X(0), P.Y(m * G6_5), P.X(1), P.Y(m * G6_5), css("--muted"), 1, [5, 4]);
  },
});
