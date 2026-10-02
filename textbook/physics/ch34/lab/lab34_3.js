// 实验 34.3 导轨上的导体棒：动生电动势与电磁阻尼（配 34.3 节）。棒长 L = 0.5 m，质量 m = 0.5 kg，导轨无摩擦；
// 电路总电阻 R。机器人场景：恒力 F 拉棒，速度趋于 v_t = FR/(BL)²；生活场景：过山车的磁力刹车，棒以 5 m/s 冲进磁场后只受安培力。
const L34 = 0.5, M34 = 0.5;
WQ.lab({
  title: ["实验 34.3 导轨上的导体棒：动生电动势", "Lab 34.3 A rod on rails: motional emf"],
  goal: ["看动生电动势、电流和安培力怎样随速度变化，验证机械功率等于电功率；调电阻，让末速度达到要求；再看电磁阻尼怎样让运动停下。",
         "See how the motional emf, current and Ampère force grow with speed, check that mechanical power equals electrical power, set R for a target terminal speed, and watch magnetic damping stop a motion."],
  scenes: [
    { id: "pull", robot: true, name: ["恒力拉动（直线电机反拖）", "Constant pull (linear motor back-driven)"],
      problem: { title: ["机器人问题：直线电机断电后被推动", "Robot problem: a linear motor pushed while unpowered"],
                 text: ["直线电机滑台断电、绕组接一个电阻时，用恒力推动滑台，它会越来越快吗？", "With the stage unpowered and its winding across a resistor, does a constant push make it ever faster?"] } },
    { id: "brake", name: ["磁力刹车", "Magnetic brake"], hide: ["F"],
      problem: { title: ["生活中的例子：过山车的磁力刹车", "Everyday example: a roller coaster's magnetic brake"],
                 text: ["车底的金属板以 5 m/s 冲进磁铁之间，不接触就慢了下来。它在多远内停下？", "A metal fin enters the magnets at 5 m/s and slows without touching anything. How far does it go?"] } },
  ],
  params: [
    { id: "B", name: ["磁感应强度 B", "Field B"], min: 0.4, max: 1.2, step: 0.05, value: 0.8, unit: "T", digits: 2 },
    { id: "R", name: ["电路电阻 R", "Resistance R"], min: 0.02, max: 1, step: 0.01, value: 0.2, unit: "Ω", digits: 2 },
    { id: "F", name: ["拉力 F", "Pull F"], min: 0.5, max: 4, step: 0.1, value: 2, unit: "N", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--ink)", name: ["速度", "speed"] }],
  tasks: [
    { id: "term", robot: true, text: ["B = 0.8 T、R = 0.2 Ω、F = 2 N：运行到速度不再增加，读出末速度和此时的电功率。", "B = 0.8 T, R = 0.2 Ω, F = 2 N: run until the speed stops growing; read the terminal speed and the electrical power."],
      demo: { scene: "pull", set: { B: 0.8, R: 0.2, F: 2 }, press: ["start"], wait: 8 } },
    { id: "target", robot: true, text: ["B = 0.8 T、F = 2 N：调 R，使末速度为 1.0 m/s（误差 5% 以内）。", "B = 0.8 T, F = 2 N: choose R for a terminal speed of 1.0 m/s (within 5%)."],
      demo: { scene: "pull", set: { B: 0.8, R: 0.08, F: 2 }, press: ["start"], wait: 5 } },
    { id: "stop", text: ["磁力刹车：让以 5 m/s 冲入的金属板在 2 m 以内停下（速度降到 0.05 m/s 以下）。", "Magnetic brake: make the fin entering at 5 m/s stop within 2 m (below 0.05 m/s)."],
      demo: { scene: "brake", set: { B: 1.2, R: 0.05 }, press: ["start"], wait: 5 } },
  ],
  think: ["磁力刹车只能让车越来越慢，却永远不能让它完全停住，为什么？实际的过山车怎样解决这个问题？", "Why can a magnetic brake slow the car but never quite stop it? How do real coasters deal with that?"],

  reset(api, s) { s.v = api.scene === "brake" ? 5 : 0; s.x = 0; s.hist = [[0, s.v]]; s.done = false; },
  update(dt, api, s) {
    const BL = api.p.B * L34, R = api.p.R;
    const step = dt * 0.5;                                     // 慢放 2 倍
    const F = api.scene === "pull" ? api.p.F : 0;
    const a = (F - BL * BL * s.v / R) / M34;
    s.v += a * step; s.x += s.v * step;
    if (s.v < 0) s.v = 0;
    s.hist.push([api.t * 0.5, s.v]);
    const tau = M34 * R / (BL * BL);
    if (api.scene === "pull" && api.t * 0.5 > Math.min(Math.max(5 * tau, 0.5), 8)) { api.stop(); fin34_3(api, s); }   // 最长 8 s
    if (api.scene === "brake" && (s.v < 0.05 || api.t * 0.5 > 6)) { api.stop(); fin34_3(api, s); }
  },
  readouts(api, s) {
    const f = api.fmt, BL = api.p.B * L34, emf = BL * s.v, I = emf / api.p.R, FA = BL * I;
    const rows = [[["速度 v", "Speed v"], f(s.v, 3) + " m/s"], [["电动势 BLv", "emf BLv"], f(emf, 3) + " V"],
                  [["电流 I", "Current I"], f(I, 3) + " A"], [["安培力 BIL", "Ampère force BIL"], f(FA, 3) + " N"],
                  [["电功率 εI", "Electrical power εI"], f(emf * I, 3) + " W"]];
    if (api.scene === "pull") rows.push([["末速度 FR/(BL)²", "Terminal FR/(BL)²"], f(api.p.F * api.p.R / (BL * BL), 3) + " m/s"]);
    else rows.push([["滑行距离", "Distance"], f(s.x, 2) + " m"]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, y1 = h * 0.12, y2 = h * 0.42, x0 = w * 0.05, x1 = w * 0.95;
    api.line(x0, y1, x1, y1, css("--ink"), 4); api.line(x0, y2, x1, y2, css("--ink"), 4); api.line(x0, y1, x0, y2, css("--ink"), 4);
    api.rect(x0 - 8, (y1 + y2) / 2 - 18, 16, 36, css("--panel"), css("--ink"));
    for (let x = x0 + 40; x < x1; x += 50) for (let y = y1 + 22; y < y2; y += 30) api.label("×", x, y + 4, css("--blue"), 14, "center");
    const span = api.scene === "brake" ? 3 : 2.5, rx = x0 + 30 + ((s.x % span) / span) * (x1 - x0 - 60);
    api.line(rx, y1 - 10, rx, y2 + 10, "#a8740a", 8);
    const I = api.p.B * L34 * s.v / api.p.R;
    if (I > 0.01) api.arrow(rx + 12, y2 - 8, rx + 12, y2 - 8 - Math.min(80, 8 * I), css("--orange"), 3);
    api.plot(w * 0.08, h * 0.55, w * 0.86, h * 0.38, [{ pts: s.hist, color: css("--ink") }],
             { xmin: 0, xmax: api.scene === "brake" ? 6 : Math.min(8, Math.max(1, 5 * M34 * api.p.R / Math.pow(api.p.B * L34, 2))), ymin: 0, ymax: api.scene === "brake" ? 5.5 : Math.max(1, api.p.F * api.p.R / Math.pow(api.p.B * L34, 2) * 1.2), xlabel: "t / s", ylabel: "v / (m/s)" });
  },
});

function fin34_3(api, s) {
  if (s.done) return; s.done = true;
  const BL = api.p.B * L34;
  if (api.scene === "pull") {
    const vt = api.p.F * api.p.R / (BL * BL);
    if (Math.abs(api.p.B - 0.8) < 1e-6 && Math.abs(api.p.R - 0.2) < 1e-6 && Math.abs(api.p.F - 2) < 1e-6 && Math.abs(s.v - vt) / vt < 0.02) api.done("term");
    if (Math.abs(api.p.B - 0.8) < 1e-6 && Math.abs(api.p.F - 2) < 1e-6 && Math.abs(s.v - 1) < 0.05) api.done("target");
  } else if (s.v < 0.05 && s.x < 2) api.done("stop");
}
