// 实验 6.6 连接体：AGV 牵引料车与阿特伍德机（配 6.6 节）。挂钩额定拉力 150 N，超过就脱钩。
const M0_6 = 80, MC_6 = [50, 30, 40], TMAX_6 = 150, G6_6 = 9.81;
const fin6_6 = (api, s) => {
  if (s.finished) return;
  s.finished = true;
  if (api.scene === "train") {
    const n = Math.round(api.p.n);
    if (n === 2 && Math.abs(api.p.F - 200) < 1 && s.broken < 0) api.done("read");
    if (n === 2 && api.p.F >= 280 && s.broken < 0) api.done("max");
    if (n === 3 && s.broken >= 0) api.done("break");
  } else if (s.tfall !== null && s.tfall > 1.5) {
    api.done("g");
  }
};

WQ.lab({
  title: ["实验 6.6 连接体与隔离法", "Lab 6.6 Connected bodies and the isolation method"],
  goal: ["AGV 牵引一列料车：看每个挂钩的拉力怎样随驱动力和车数变化，找出不脱钩的最大驱动力；再用阿特伍德机测重力加速度。",
         "An AGV tows a train of carts: see how each coupler's tension depends on the driving force and the number of carts, and find the largest force that does not break a coupler; then measure g with an Atwood machine."],
  scenes: [
    { id: "train", robot: true, name: ["AGV 牵引料车", "AGV tows carts"], hide: ["m1", "m2"],
      problem: { title: ["机器人问题：挂钩会不会被拉断", "Robot problem: will a coupler break?"],
                 text: ["AGV（80 kg）依次牵引 50 kg、30 kg、40 kg 的料车。挂钩额定拉力 150 N。驱动力越大起步越快，哪个挂钩最先受不了？",
                        "The AGV (80 kg) tows carts of 50, 30 and 40 kg in turn. Couplers are rated at 150 N. A larger driving force starts faster — which coupler gives first?"] } },
    { id: "atwood", name: ["阿特伍德机", "Atwood machine"], hide: ["F", "n"],
      problem: { title: ["生活中的例子：电梯的配重", "Everyday example: a lift's counterweight"],
                 text: ["绳跨过定滑轮，两边挂 m₁、m₂。两边质量相差不大时加速度很小，便于计时。阿特伍德在 1784 年用它演示匀加速运动，今天的教学实验常用它测 g。",
                        "A string over a pulley carries m₁ and m₂. With nearly equal masses the acceleration is small and easy to time. Atwood used it in 1784 to demonstrate uniformly accelerated motion; teaching labs now use it to measure g."] } },
  ],
  params: [
    { id: "n", name: ["料车数", "Number of carts"], min: 1, max: 3, step: 1, value: 2, digits: 0 },
    { id: "F", name: ["驱动力 F", "Driving force F"], min: 50, max: 500, step: 10, value: 200, unit: "N", digits: 0 },
    { id: "m1", name: ["m₁（上升的一边）", "m₁ (rising side)"], min: 0.5, max: 2, step: 0.05, value: 1.0, unit: "kg", digits: 2 },
    { id: "m2", name: ["m₂（下降的一边）", "m₂ (falling side)"], min: 0.5, max: 2, step: 0.05, value: 1.1, unit: "kg", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--blue)", name: ["挂钩拉力", "coupler tension"] }],
  tasks: [
    { id: "read", robot: true, text: ["两辆料车、驱动力 200 N：跑一次，读出两个挂钩的拉力。", "Two carts, 200 N: run once and read both coupler tensions."],
      demo: { scene: "train", set: { n: 2, F: 200 }, press: ["start"], wait: 3 } },
    { id: "max", robot: true, text: ["两辆料车：用不小于 280 N 的驱动力起步而不脱钩。", "Two carts: start with at least 280 N without breaking a coupler."],
      demo: { scene: "train", set: { n: 2, F: 290 }, press: ["start"], wait: 3 } },
    { id: "break", robot: true, text: ["三辆料车：让一个挂钩脱开，说出是哪一个。", "Three carts: make a coupler break and say which one."],
      demo: { scene: "train", set: { n: 3, F: 400 }, press: ["start"], wait: 3 } },
    { id: "g", text: ["阿特伍德机：让 m₂ 下落 1 m 的时间超过 1.5 s，由时间算出 g。", "Atwood machine: make m₂ take more than 1.5 s to fall 1 m, and work out g from the time."],
      demo: { scene: "atwood", set: { m1: 1.0, m2: 1.1 }, press: ["start"], wait: 4 } },
  ],
  think: ["为什么最靠近 AGV 的挂钩拉力最大？如果把最重的料车挂在最后，第一个挂钩的拉力会变吗？",
          "Why does the coupler next to the AGV carry the most? If the heaviest cart went last, would the first coupler's tension change?"],

  reset(api, s) { s.x = 0; s.v = 0; s.broken = -1; s.xb = 0; s.vb = 0; s.T = []; s.y = 0; s.tfall = null; s.finished = false; },
  update(dt, api, s) {
    if (api.scene === "train") {
      const n = Math.round(api.p.n), carts = MC_6.slice(0, n);
      const pulled = s.broken < 0 ? carts : carts.slice(0, s.broken);       // 脱钩以后，后面的车不再被拉
      const mTot = M0_6 + pulled.reduce((a, b) => a + b, 0);
      const a = api.p.F / mTot;
      // 第 k 个挂钩拉着它后面所有（仍挂着的）车：T_k = (后面车的质量之和) × a
      s.T = pulled.map((_, k) => pulled.slice(k).reduce((p, q) => p + q, 0) * a);
      if (s.broken < 0) {
        const k = s.T.findIndex((T) => T > TMAX_6);
        if (k >= 0) { s.broken = k; s.xb = s.x; s.vb = s.v; s.Tbreak = s.T[k]; }
      }
      s.v += a * dt; s.x += s.v * dt;
      if (s.broken >= 0) s.xb += s.vb * dt;      // 脱开的车靠惯性匀速滑行（本章不计滚动阻力）
      s.a = a;
      if (api.t > 2.0) { api.stop(); fin6_6(api, s); }
    } else {
      const m1 = api.p.m1, m2 = api.p.m2;
      s.a = (m2 - m1) * G6_6 / (m1 + m2);
      s.Trope = 2 * m1 * m2 * G6_6 / (m1 + m2);
      s.v += s.a * dt; s.y += s.v * dt;
      if (s.tfall === null && s.y >= 1.0) { s.tfall = api.t + (Math.random() * 2 - 1) * 0.01; api.stop(); fin6_6(api, s); }   // 计时误差 ±0.01 s
      if (s.a <= 0 && api.t > 3) api.stop();
    }
  },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "train") {
      const rows = [[["加速度", "Acceleration"], s.a === undefined ? "—" : f(s.a, 3) + " m/s²"]];
      const n = Math.round(api.p.n);
      for (let k = 0; k < n; k++) {
        const val = s.broken >= 0 && k >= s.broken ? (k === s.broken ? api.P(["脱钩！", "broken!"]) + "（" + f(s.Tbreak, 0) + " N）" : "—") : s.T[k] === undefined ? "—" : f(s.T[k], 1) + " N";
        rows.push([[`挂钩 ${k + 1} 拉力`, `Coupler ${k + 1}`], val]);
      }
      rows.push([["额定拉力", "Rated"], TMAX_6 + " N"]);
      return rows;
    }
    return [[["加速度（理论）", "Acceleration (theory)"], s.a === undefined ? "—" : f(s.a, 4) + " m/s²"],
            [["绳的拉力", "String tension"], s.Trope === undefined ? "—" : f(s.Trope, 3) + " N"],
            [["下落 1 m 的时间", "Time to fall 1 m"], s.tfall === null ? "—" : f(s.tfall, 3) + " s"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    if (api.scene === "train") {
      const y0 = h * 0.55, ppm = w / 7, n = Math.round(api.p.n);
      const head = w * 0.82;
      api.ground(y0, w, s.x * ppm, 40);
      const aw = 1.0 * ppm, cw = 0.8 * ppm, gap = 0.12 * ppm;
      api.agv(head - aw / 2, y0, aw);
      api.arrow(head, y0 - aw * 0.15, head + api.p.F * 0.25, y0 - aw * 0.15, css("--red"), 3);
      let right = head - aw;
      for (let k = 0; k < n; k++) {
        const off = s.broken >= 0 && k >= s.broken ? (s.x - s.xb) * ppm : 0;
        const x1 = right - gap - off;
        if (!(s.broken >= 0 && k === s.broken)) api.line(x1, y0 - 16, x1 + gap, y0 - 16, css("--ink"), 3);
        api.rect(x1 - cw, y0 - 28, cw, 20, css("--panel"), css("--ink"), 3);
        api.circle(x1 - cw * 0.8, y0 - 5, 5, null, css("--ink")); api.circle(x1 - cw * 0.2, y0 - 5, 5, null, css("--ink"));
        api.label(MC_6[k] + " kg", x1 - cw / 2, y0 - 34, css("--muted"), 12, "center");
        const T = s.T[k];
        if (T !== undefined && !(s.broken >= 0 && k >= s.broken)) {
          api.label(api.fmt(T, 0) + " N", x1 + gap / 2, y0 - 50, T > TMAX_6 * 0.9 ? css("--red") : css("--blue"), 12, "center");
        }
        right = x1 - cw;
      }
      api.label(api.T("挂钩额定拉力 150 N", "couplers rated 150 N"), 12, 18, css("--muted"), 13);
      return;
    }
    // 阿特伍德机
    const cx = w * 0.35, top = 40, R = 30, ppm = h * 0.45;
    api.circle(cx, top + R, R, null, css("--ink")); api.line(cx - 50, top, cx + 50, top, css("--ink"), 4);
    const yl = top + R + h * 0.3 - s.y * ppm, yr = top + R + h * 0.3 + s.y * ppm;
    api.line(cx - R, top + R, cx - R, yl, css("--ink"), 2); api.line(cx + R, top + R, cx + R, yr, css("--ink"), 2);
    api.rect(cx - R - 16, yl, 32, 20 + api.p.m1 * 14, css("--accent"), css("--ink"), 3);
    api.rect(cx + R - 16, yr, 32, 20 + api.p.m2 * 14, css("--amber"), css("--ink"), 3);
    api.label("m₁", cx - R - 40, yl + 14, css("--ink"), 13); api.label("m₂", cx + R + 22, yr + 14, css("--ink"), 13);
    const yEnd = top + R + h * 0.3 + 1.0 * ppm;
    api.line(cx + R - 30, yEnd, cx + R + 30, yEnd, css("--red"), 2, [5, 4]);
    api.label(api.T("下落 1 m", "fallen 1 m"), cx + R + 36, yEnd + 4, css("--red"), 12);
  },
});
