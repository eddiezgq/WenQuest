// 实验 33.7 临界转速（配 33.7 节）。一根两端简支的轴，中间一个圆盘，质心偏离轴线 e。提高转速，看挠度怎样变化，找出临界转速。
// 一阶临界转速 nc = 60/(2π)·√(k/m)，k = 48EI/L³（跨中刚度，忽略轴的质量）；不平衡响应 y/e = r²/√((1 − r²)² + (2ζr)²)。
const E33_7 = 210000, ZETA33_7 = 0.02;
function nc33_7(api) {
  const I = Math.PI * Math.pow(api.p.d, 4) / 64, k = 48 * E33_7 * I / Math.pow(api.p.L, 3);      // N/mm
  return 60 / (2 * Math.PI) * Math.sqrt(k / (api.p.m / 1000));                                     // r/min
}
const amp33_7 = (r) => r * r / Math.sqrt((1 - r * r) ** 2 + (2 * ZETA33_7 * r) ** 2);
WQ.lab({
  title: ["实验 33.7 临界转速", "Lab 33.7 Critical speed"],
  goal: ["改变跨距、直径、圆盘质量和转速，看轴的弯曲挠度怎样随转速变化，学会判断一根轴是刚性轴还是挠性轴。",
         "Vary the span, diameter, disk mass and speed; see how the shaft's bending changes with speed and tell a rigid shaft from a flexible one."],
  scenes: [
    { id: "robot", robot: true, name: ["风机轴", "Fan shaft"],
      problem: { title: ["工程问题：2900 r/min 的风机轴", "Engineering problem: a fan shaft at 2900 r/min"],
                 text: ["Ø30、跨距 800 mm、叶轮 25 kg，电机 2900 r/min。它的临界转速是多少？工作转速落在哪个区？",
                        "Ø30, 800 mm span, 25 kg impeller, motor at 2900 r/min. What is its critical speed, and which zone does the running speed fall in?"] } },
    { id: "life", name: ["洗衣机脱水", "Washing-machine spin"],
      params: { L: { min: 300, max: 800, step: 10, value: 600 }, d: { min: 12, max: 40, step: 1, value: 15 }, m: { min: 5, max: 40, step: 1, value: 30 },
                n: { min: 100, max: 1400, step: 10, value: 200 } },
      problem: { title: ["生活中的例子：脱水开始时的“咣咣”声", "Everyday example: the thumping at the start of a spin"],
                 text: ["衣物堆在一边就是“不平衡质量”。脱水转速从低升到高的途中，会经过一个转速，机器晃得最厉害。",
                        "Clothes bunched on one side are an unbalanced mass. On the way up to full spin the drum passes a speed where the machine shakes hardest."] } },
  ],
  params: [
    { id: "L", name: ["跨距 L", "Span L"], min: 300, max: 1200, step: 10, value: 800, unit: "mm", digits: 0 },
    { id: "d", name: ["轴径 d", "Diameter d"], min: 20, max: 60, step: 1, value: 30, unit: "mm", digits: 0 },
    { id: "m", name: ["圆盘质量 m", "Disk mass m"], min: 5, max: 60, step: 1, value: 25, unit: "kg", digits: 0 },
    { id: "n", name: ["转速 n", "Speed n"], min: 100, max: 4000, step: 10, value: 500, unit: "r/min", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["升速", "Spin up"], primary: true }, { id: "reset", name: ["停止", "Stop"] }],
  legend: [{ color: "var(--red)", name: ["挠度 y/e", "whirl y/e"] }, { color: "var(--accent)", name: ["当前转速", "current speed"] }],
  tasks: [
    { id: "nc", robot: true, text: ["风机轴（默认参数）：升速到 2900 r/min，读出临界转速 nc 和转速比；判断它是刚性轴还是挠性轴。",
                                     "Fan shaft (defaults): spin up to 2900 r/min, read nc and the speed ratio; rigid or flexible?"],
      demo: { scene: "robot", set: { L: 800, d: 30, m: 25, n: 2900 }, press: ["start"], wait: 4 } },
    { id: "rigid", robot: true, text: ["只改轴径，把这根轴改成刚性轴（2900 r/min ≤ 0.7 nc）。", "Change only the diameter to make it a rigid shaft (2900 r/min ≤ 0.7 nc)."],
      demo: { scene: "robot", set: { L: 800, d: 48, m: 25, n: 2900 }, press: ["start"], wait: 4 } },
    { id: "life", text: ["洗衣机：升速到 1200 r/min，看挠度在哪个转速最大。", "Washer: spin up to 1200 r/min and see at what speed the whirl peaks."],
      demo: { scene: "life", set: { L: 600, d: 15, m: 30, n: 1200 }, press: ["start"], wait: 4 } },
  ],
  think: ["为什么挠性轴在越过临界转速以后挠度反而变小？这时圆盘的质心在轴线的哪一侧？",
          "Why does a flexible shaft bend less once it is past the critical speed? Which side of the axis is the disk's centre of mass then?"],

  reset(api, s) { s.n = 0; s.ph = 0; s.peak = 0; s.nPeak = 0; s.hist = []; },
  update(dt, api, s) {
    const nc = nc33_7(api);
    s.n = Math.min(api.p.n, s.n + Math.max(api.p.n, 600) * dt / 2.5);       // 2.5 s 升到设定转速
    s.ph += s.n / 60 * 2 * Math.PI * dt * 0.05;                                   // 画面上的转动放慢 20 倍
    const a = amp33_7(s.n / nc);
    if (a > s.peak) { s.peak = a; s.nPeak = s.n; }
    s.hist.push([s.n / nc, Math.min(a, 8)]);
    if (s.n >= api.p.n) {
      const r = api.p.n / nc;
      if (api.scene === "robot" && api.p.n >= 2900 && api.p.L === 800 && api.p.d === 30 && api.p.m === 25) api.done("nc");
      if (api.scene === "robot" && api.p.n >= 2900 && api.p.L === 800 && api.p.m === 25 && r <= 0.7) api.done("rigid");
      if (api.scene === "life" && api.p.n >= 1000 && r > 1.3) api.done("life");
      api.stop();
    }
  },
  readouts(api, s) {
    const nc = nc33_7(api), f = api.fmt, r = (s.n || 0) / nc;
    const zone = api.p.n <= 0.7 * nc ? api.T("刚性轴（n ≤ 0.7nc）", "rigid (n ≤ 0.7nc)") : api.p.n >= 1.3 * nc ? api.T("挠性轴（n ≥ 1.3nc）", "flexible (n ≥ 1.3nc)") : api.T("危险区：接近共振", "danger: near resonance");
    return [
      [["一阶临界转速 nc", "First critical speed nc"], f(nc, 0) + " r/min"],
      [["当前转速", "Current speed"], f(s.n || 0, 0) + " r/min"],
      [["转速比 n/nc", "Speed ratio n/nc"], f(r, 2)],
      [["挠度 / 偏心距", "Whirl / eccentricity"], f(amp33_7(r), 2)],
      [["设定转速所在区", "Zone at the set speed"], zone],
      [["升速途中挠度最大处", "Peak on the way up"], s.peak ? f(s.nPeak, 0) + " r/min" : "—"],
    ];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, nc = nc33_7(api);
    const a = amp33_7((s.n || 0) / nc);
    const x0 = w * 0.06, x1 = w * 0.44, yc = h * 0.42, span = x1 - x0;
    const y = Math.min(a, 8) * 6 * Math.cos(s.ph || 0);
    api.line(x0, yc + 26, x0 + 12, yc + 12, css("--ink"), 2); api.line(x0 + 24, yc + 26, x0 + 12, yc + 12, css("--ink"), 2);
    api.line(x1, yc + 26, x1 - 12, yc + 12, css("--ink"), 2); api.line(x1 - 24, yc + 26, x1 - 12, yc + 12, css("--ink"), 2);
    const N = 24;
    for (let i = 0; i < N; i++) {
      const u0 = i / N, u1 = (i + 1) / N;
      api.line(x0 + 12 + u0 * (span - 24), yc - y * Math.sin(Math.PI * u0), x0 + 12 + u1 * (span - 24), yc - y * Math.sin(Math.PI * u1), css("--muted"), Math.max(3, api.p.d / 6));
    }
    api.rect((x0 + x1) / 2 - 7, yc - y - 40, 14, 80, css("--amber"), css("--ink"), 3);
    api.label(api.T("不平衡质量", "unbalance"), (x0 + x1) / 2, yc - y - 52, css("--muted"), 12, "center");
    const rmax = Math.max(2.5, api.p.n / nc * 1.1);
    const P = api.plot(w * 0.52, h * 0.08, w * 0.44, h * 0.78, [
      { pts: Array.from({ length: 200 }, (_, i) => { const r = 0.01 + i / 199 * rmax; return [r, Math.min(amp33_7(r), 8)]; }), color: css("--grid") },
      { pts: s.hist || [], color: css("--red") },
    ], { xmin: 0, xmax: rmax, ymin: 0, ymax: 8, xlabel: "n / nc", ylabel: "y / e" });
    const r = (s.n || 0) / nc;
    api.line(P.X(0.7), P.Y(0), P.X(0.7), P.Y(8), css("--green"), 1, [4, 4]);
    api.line(P.X(1.3), P.Y(0), P.X(1.3), P.Y(8), css("--green"), 1, [4, 4]);
    api.circle(P.X(Math.min(r, rmax)), P.Y(Math.min(a, 8)), 5, css("--accent"), css("--ink"));
  },
});
