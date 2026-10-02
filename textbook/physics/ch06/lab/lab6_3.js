// 实验 6.3 测量牛顿第二定律（配 6.3 节）。AGV 在测试道上由静止起步，两道光电门记下通过的时刻，由此算出加速度。
// 记录的数据放在闭包里，重置时不丢（实验工具包每次重置都会清空 state）。
const rec6_3 = { runs: [] };
const M_AGV = 80, M_UNKNOWN = 53, X1 = 0.5, X2 = 1.5;     // AGV 自身质量、未知货箱质量（kg）；两道光电门的位置（m）
const mass6_3 = (api) => api.scene === "unknown" ? M_AGV + M_UNKNOWN : api.scene === "life" ? 15 + api.p.load : M_AGV + api.p.load;
const check6_3 = (api) => {
  const runs = rec6_3.runs;
  const last = runs[runs.length - 1];
  if (api.scene === "robot" && last && last.load === 40 && last.F === 120 && Math.abs(last.a / (120 / (M_AGV + 40)) - 1) < 0.03) api.done("check");
  if (api.scene === "unknown" && Math.abs(api.p.est - M_UNKNOWN) / M_UNKNOWN < 0.03) api.done("weigh");
  if (api.scene === "life") {
    const full = runs.filter((r) => r.scene === "life" && r.load === 30 && r.F === 30).length;
    if (full) api.done("cart");
  }
};

WQ.lab({
  title: ["实验 6.3 测量牛顿第二定律", "Lab 6.3 Measuring Newton's second law"],
  goal: ["改变驱动力和载货，用光电门测加速度，找出 a 与 F、m 的关系；再用它称出一个未知货箱的质量。",
         "Vary the driving force and the load, measure the acceleration with light gates, find how a depends on F and m — then weigh an unknown crate with it."],
  scenes: [
    { id: "robot", robot: true, name: ["AGV 测试道", "AGV test track"], hide: ["est"],
      problem: { title: ["机器人问题：驱动力、载货与加速度", "Robot problem: driving force, load and acceleration"],
                 text: ["AGV 由静止起步，驱动力恒定。光电门 1、2 分别在 0.5 m 和 1.5 m 处。由两次通过的时刻求加速度：x = at²/2。",
                        "The AGV starts from rest with a constant driving force. Light gates 1 and 2 are at 0.5 m and 1.5 m. From the two passing times, find a using x = at²/2."] } },
    { id: "unknown", robot: true, name: ["称未知货箱", "Weigh an unknown crate"], hide: ["load"],
      problem: { title: ["机器人问题：不用秤，称出货箱的质量", "Robot problem: weigh a crate without scales"],
                 text: ["AGV（80 kg）载着一个不知道质量的货箱。用已知的驱动力测出加速度，算出总质量，再把“质量估计”调到你算出的货箱质量。",
                        "The AGV (80 kg) carries a crate of unknown mass. Measure the acceleration under a known force, work out the total mass, and set “mass estimate” to the crate's mass."] } },
    { id: "life", name: ["推购物车", "Pushing a shopping cart"], hide: ["est"],
      params: { F: { min: 10, max: 60, step: 5, value: 30 }, load: { min: 0, max: 40, step: 5, value: 0 } },
      problem: { title: ["生活中的例子：空车和满车", "Everyday example: empty and full cart"],
                 text: ["同样用力推购物车（空车 15 kg），装满东西以后为什么起步慢得多？",
                        "Push a shopping cart (15 kg empty) equally hard: why does it start so much more slowly when full?"] } },
  ],
  params: [
    { id: "F", name: ["驱动力 F", "Driving force F"], min: 20, max: 200, step: 10, value: 120, unit: "N", digits: 0 },
    { id: "load", name: ["货物质量", "Load mass"], min: 0, max: 80, step: 10, value: 40, unit: "kg", digits: 0 },
    { id: "est", name: ["质量估计（货箱）", "Mass estimate (crate)"], min: 0, max: 100, step: 0.5, value: 30, unit: "kg", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["起步", "Go"], primary: true }, { id: "reset", name: ["重置", "Reset"] }, { id: "clear", name: ["清空记录", "Clear records"] }],
  legend: [{ color: "var(--accent)", name: ["测得的 a", "measured a"] }],
  tasks: [
    { id: "check", robot: true, text: ["载货 40 kg、驱动力 120 N 跑一次：测得的 a 与 F/m 相差不到 3%。再换 60 N、换载货各跑几次，填写数据表。",
                                        "Run once with a 40 kg load at 120 N: the measured a is within 3% of F/m. Then vary F and the load and fill in the data table."],
      demo: { scene: "robot", set: { load: 40, F: 120 }, press: ["start"], wait: 4 } },
    { id: "weigh", robot: true, text: ["称未知货箱：把质量估计调到与真实值相差 3% 以内，再跑一次核对。",
                                        "Weigh the unknown crate: set the estimate within 3% of the true value, then run once to check."],
      demo: { scene: "unknown", set: { F: 120, est: 53 }, press: ["start"], wait: 4 } },
    { id: "cart", text: ["购物车：装 30 kg 东西、用 30 N 推一次，读出加速度，与空车（15 kg）的 F/m 比较。",
                         "Shopping cart: push it with 30 kg inside at 30 N, read the acceleration and compare it with F/m for the empty cart (15 kg)."],
      demo: { scene: "life", set: { F: 30, load: 30 }, press: ["start"], wait: 4 } },
  ],
  think: ["光电门的计时误差是 ±2 ms。离起点近的门，时刻小，相对误差大还是小？为什么第二道门放远一些更好？",
          "The gates time to ±2 ms. Is the relative error larger or smaller at the gate near the start? Why is a far second gate better?"],

  reset(api, s) { s.x = 0; s.v = 0; s.t1 = null; s.t2 = null; s.done = false; },
  update(dt, api, s) {
    const m = mass6_3(api);
    const a = api.p.F / m;
    s.v += a * dt; s.x += s.v * dt;
    const noise = () => (Math.random() * 2 - 1) * 0.002;          // 计时误差 ±2 ms
    if (s.t1 === null && s.x >= X1) s.t1 = api.t + noise();
    if (s.t2 === null && s.x >= X2) {
      s.t2 = api.t + noise();
      s.aMeas = 2 * (X2 - X1) / (s.t2 * s.t2 - s.t1 * s.t1);      // 由 x = at²/2 在两道门处相减
      rec6_3.runs.push({ scene: api.scene, F: api.p.F, m: api.scene === "unknown" ? null : m, a: s.aMeas, load: api.p.load });
      if (rec6_3.runs.length > 12) rec6_3.runs.shift();
      s.done = true; api.stop();
      check6_3(api);
    }
  },
  action(id, api, s) { if (id === "clear") rec6_3.runs.length = 0; },
  readouts(api, s) {
    const f = api.fmt, m = mass6_3(api);
    const rows = [
      [["光电门 1 时刻", "Gate 1 time"], s.t1 === null ? "—" : f(s.t1, 3) + " s"],
      [["光电门 2 时刻", "Gate 2 time"], s.t2 === null ? "—" : f(s.t2, 3) + " s"],
      [["测得的加速度", "Measured acceleration"], s.done ? f(s.aMeas, 3) + " m/s²" : "—"],
    ];
    if (api.scene !== "unknown") rows.push([["总质量 m", "Total mass m"], f(m, 0) + " kg"]);
    const mine = rec6_3.runs.filter((r) => r.scene === api.scene).slice(-5);
    mine.forEach((r, i) => rows.push([[`记录 ${i + 1}`, `Run ${i + 1}`],
      `F = ${f(r.F, 0)} N, ${r.m === null ? "" : "m = " + f(r.m, 0) + " kg, "}a = ${f(r.a, 3)} m/s²`]));
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    const y0 = h * 0.45, x0 = w * 0.06, ppm = (w * 0.86) / 2.0;
    api.line(x0 - 10, y0, x0 + 2.0 * ppm + 10, y0, css("--ground"), 2);
    [X1, X2].forEach((xg, i) => {
      const gx = x0 + xg * ppm;
      api.line(gx, y0 - 70, gx, y0, css("--muted"), 2, [4, 4]);
      api.rect(gx - 6, y0 - 80, 12, 12, (i === 0 ? s.t1 : s.t2) === null ? css("--panel") : css("--green"), css("--ink"), 2);
      api.label(api.T(`光电门 ${i + 1}`, `gate ${i + 1}`), gx, y0 - 88, css("--muted"), 12, "center");
    });
    const life = api.scene === "life";
    const bw = (life ? 0.45 : 0.5) * ppm, bx = x0 + s.x * ppm + bw / 2;
    if (life) {
      api.rect(bx - bw / 2, y0 - bw * 0.7, bw, bw * 0.55, null, css("--ink"), 4);
      api.circle(bx - bw * 0.35, y0 - 6, 6, css("--ink")); api.circle(bx + bw * 0.35, y0 - 6, 6, css("--ink"));
      for (let k = 0; k < Math.round(api.p.load / 10); k++) api.box(bx - bw * 0.3 + k * bw * 0.2, y0 - bw * 0.16, bw * 0.18, css("--amber"));
    } else {
      api.agv(bx, y0, bw);
      const n = api.scene === "unknown" ? 1 : Math.round(api.p.load / 20);
      for (let k = 0; k < n; k++) api.box(bx - bw * 0.3 + k * bw * 0.22, y0 - bw * 0.33, bw * 0.2, api.scene === "unknown" ? css("--red") : css("--amber"));
    }
    api.arrow(bx + bw / 2 + 4, y0 - bw * 0.2, bx + bw / 2 + 4 + api.p.F * 0.35, y0 - bw * 0.2, css("--red"), 3);
    api.label("F", bx + bw / 2 + 10 + api.p.F * 0.35, y0 - bw * 0.2 + 4, css("--red"), 14);
    // 下方：本场景记录的 a—F 点
    const mine = rec6_3.runs.filter((r) => r.scene === api.scene);
    const fmax = life ? 60 : 200;
    const P = api.plot(w * 0.1, h * 0.58, w * 0.8, h * 0.36, [{ pts: [], color: css("--accent") }],
                       { xmin: 0, xmax: fmax, ymin: 0, ymax: life ? 4 : 2.6, xlabel: "F / N", ylabel: "a / (m/s²)" });
    mine.forEach((r) => api.circle(P.X(r.F), P.Y(r.a), 4, css("--accent"), css("--ink")));
  },
});
