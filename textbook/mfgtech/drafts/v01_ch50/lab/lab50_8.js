// 实验 50.8 工艺方案的经济比较（配 50.8 节）。方案 A：磨削保证轴承位；方案 B：精细车代替磨削。
// 单件工艺成本 c = V + F/N（式 50.8.2）；工作中心费率取自数字工厂（教学示意值，美元/小时）。
const RATE50 = { saw: 25, cnc: 48, ht: 34, key: 36, grd: 52, qc: 40 };
const ROUTE50 = [["saw", 3], ["cnc", 18], ["ht", 12], ["cnc", 15], ["key", 10], ["grd", 12], ["qc", 6]];   // SH-301 现行工艺路线（min/件）
const CNC_N50 = 2;                                   // 数控车床 CNC-L01 有 2 台

function cost50(api) {
  const p = api.p;
  const VA = ROUTE50.reduce((a, [w, m]) => a + m * RATE50[w] / 60, 0);
  const VB = VA - 12 * RATE50.grd / 60 + p.tf * RATE50.cnc / 60 + p.ins;
  const Nc = VA > VB ? p.F / (VA - VB) : Infinity;
  const cA = VA, cB = VB + p.F / p.N;
  const cncA = (18 + 15) / CNC_N50, cncB = (18 + 15 + p.tf) / CNC_N50;
  const capA = Math.min(480 / cncA, 480 / 12), capB = 480 / cncB;      // 每班产能：A 受数控车床和磨床限制，B 只受数控车床限制
  return { VA, VB, Nc, cA, cB, capA, capB, cheaper: cA <= cB ? "A" : "B", fitsB: capB >= p.dem, fitsA: capA >= p.dem };
}

function check50_8(api, s) {
  const c = cost50(api);
  s.c = c;
  if (isFinite(c.Nc) && Math.abs(api.p.N - c.Nc) <= 60) api.done("even");
  if (api.p.N <= 600 && c.cheaper === "A") api.done("small");
  if (api.p.N >= 3500 && c.cheaper === "B") api.done("large");
  if (api.p.N >= 3500 && c.cheaper === "B" && !c.fitsB && c.fitsA) api.done("cap");
}

WQ.lab({
  title: ["实验 50.8 工艺方案的经济比较", "Lab 50.8 Comparing process alternatives"],
  goal: ["比较两种工艺方案的单件工艺成本，找出临界产量；再看便宜的方案能不能按时交货——成本最低不等于方案最好。",
         "Compare the process cost per piece of two alternatives and find the break-even volume; then check whether the cheaper one can deliver on time — lowest cost is not always best."],
  scenes: [
    { id: "shaft", name: ["SH-301 输出轴", "SH-301 output shaft"],
      problem: { title: ["工厂问题：轴承位还要不要磨？", "Factory problem: keep grinding the bearing seats?"],
                 text: ["精细车能把调质的 SH-301 轴承位直接做到 Ø35k6、Ra 0.8，省掉磨削这道工序；但要买在机测头、管好精密刀片，每年多花一笔固定费用，还多占了数控车床。年产量多少时值得改？",
                        "Fine turning can take the Q&T SH-301 bearing seats straight to Ø35k6, Ra 0.8 and drop grinding, but it needs an on-machine probe and precision inserts — a fixed yearly cost — and more lathe time. At what annual volume does it pay?"] } },
    { id: "joint", robot: true, name: ["关节输出轴", "joint output shaft"],
      params: { N: { min: 100, max: 5000, step: 50, value: 1500 }, dem: { min: 5, max: 40, step: 1, value: 8 } },
      problem: { title: ["机器人问题：关节模组小批量试产", "Robot problem: a small pilot run of joint modules"],
                 text: ["关节模组先试产每年 300 套，输出轴的工艺与 SH-301 相近。小批量时该选哪个方案？", "The joint module starts with 300 sets a year; its output shaft is made much like SH-301. Which alternative suits a small volume?"] } },
  ],
  params: [
    { id: "N", name: ["年产量 N", "Annual volume N"], min: 100, max: 5000, step: 50, value: 1000, unit: "", digits: 0 },
    { id: "F", name: ["方案 B 年固定费用 F", "Alternative B fixed cost F"], min: 0, max: 12000, step: 500, value: 6000, unit: "USD", digits: 0 },
    { id: "tf", name: ["精细车工时", "Fine-turning time"], min: 4, max: 14, step: 0.5, value: 8, unit: "min", digits: 1 },
    { id: "ins", name: ["刀片费用", "Insert cost"], min: 0, max: 2, step: 0.05, value: 0.6, unit: "USD", digits: 2 },
    { id: "dem", name: ["每班需求", "Demand per shift"], min: 5, max: 40, step: 1, value: 20, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["核算", "Check"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--green)", name: ["方案 A：磨削", "A: grinding"] }, { color: "var(--accent)", name: ["方案 B：精细车", "B: fine turning"] }],
  tasks: [
    { id: "even", text: ["调年产量，找到两个方案单件成本相等的临界产量（误差 60 件以内）。", "Adjust the volume to find the break-even point (within 60 pieces)."],
      demo: { scene: "shaft", set: { N: 1750, F: 6000, tf: 8, ins: 0.6, dem: 20 } } },
    { id: "small", robot: true, text: ["年产量 600 件以下时，说明哪个方案便宜。", "Below 600 pieces a year, show which alternative is cheaper."],
      demo: { scene: "joint", set: { N: 300, F: 6000, tf: 8, ins: 0.6, dem: 8 } } },
    { id: "large", text: ["年产量 3500 件以上时，让方案 B 更便宜。", "Above 3500 pieces a year, make alternative B the cheaper one."],
      demo: { scene: "shaft", set: { N: 4000, F: 6000, tf: 8, ins: 0.6, dem: 20 } } },
    { id: "cap", text: ["在方案 B 更便宜的产量下，提高每班需求，找到方案 B 已经做不出来、方案 A 还能做出来的情形。", "At a volume where B is cheaper, raise the demand per shift until B can no longer keep up while A still can."],
      demo: { scene: "shaft", set: { N: 4000, F: 6000, tf: 8, ins: 0.6, dem: 26 } } },
  ],
  think: ["方案 B 省掉了一道工序，为什么反而可能交不了货？瓶颈在哪里？", "Alternative B drops an operation; why might it still fail to deliver? Where is the bottleneck?"],

  reset(api, s) { check50_8(api, s); },
  update(dt, api, s) { check50_8(api, s); api.stop(); },
  readouts(api, s) {
    const c = s.c || cost50(api), f = api.fmt;
    return [
      [["方案 A 单件工艺成本", "A: cost per piece"], `${f(c.cA, 2)} USD`],
      [["方案 B 单件工艺成本", "B: cost per piece"], `${f(c.cB, 2)} USD`],
      [["临界产量", "Break-even volume"], isFinite(c.Nc) ? `${f(c.Nc, 0)} ${api.T("件/年", "pcs/yr")}` : api.T("方案 B 的可变费用不低于 A，没有临界产量", "B's variable cost is not lower: no break-even")],
      [["较便宜的方案", "Cheaper alternative"], c.cheaper],
      [["每班产能 A / B", "Capacity per shift A / B"], `${f(c.capA, 1)} / ${f(c.capB, 1)}`],
      [["能否满足每班需求", "Meets the demand?"], `A ${c.fitsA ? "✓" : "✗"}　B ${c.fitsB ? "✓" : "✗"}`],
    ];
  },
  draw(api, s) {
    const c = s.c || cost50(api), { w, h } = api, css = api.css, p = api.p;
    const pts = (fn) => { const a = []; for (let n = 100; n <= 5000; n += 50) a.push([n, fn(n)]); return a; };
    const top = Math.max(c.VA, c.VB) + 30;
    const ax = api.plot(56, 30, w - 90, h - 90, [
      { pts: pts(() => c.VA), color: css("--green") },
      { pts: pts((n) => Math.min(top, c.VB + p.F / n)), color: css("--accent") },
    ], { xmin: 0, xmax: 5000, ymin: Math.min(c.VA, c.VB) - 8, ymax: top, xlabel: api.T("年产量 N / 件", "annual volume N"), ylabel: api.T("单件工艺成本 / USD", "cost per piece / USD") });
    api.line(ax.X(p.N), 30, ax.X(p.N), h - 60, css("--orange"), 2, [6, 4]);
    api.circle(ax.X(p.N), ax.Y(c.cA), 5, css("--green"));
    api.circle(ax.X(p.N), ax.Y(Math.min(top, c.cB)), 5, css("--accent"));
    if (isFinite(c.Nc) && c.Nc <= 5000) api.line(ax.X(c.Nc), 30, ax.X(c.Nc), h - 60, css("--muted"), 1, [3, 3]);
    api.label(api.T("当前产量", "current volume"), ax.X(p.N) + 6, 44, css("--orange"), 12);
    const y0 = Math.min(c.VA, c.VB) - 8;
    api.label("A", w - 30, ax.Y(c.VA) - 10, css("--green"), 14);
    api.label("B", w - 30, ax.Y(c.VB + p.F / 5000) + 12, css("--accent"), 14);
    [0, 1000, 2000, 3000, 4000, 5000].forEach((n) => api.label(String(n), ax.X(n), h - 48, css("--muted"), 11, "center"));
    [y0, (y0 + top) / 2, top].forEach((v) => api.label(api.fmt(v, 0), 50, ax.Y(v), css("--muted"), 11, "right"));
  },
});
