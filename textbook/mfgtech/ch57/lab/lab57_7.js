// 实验 57.7 工艺方案的技术经济分析（配 57.7 节）。公式与程序 57.7.1（ex57_7.py）相同：
//   单件工艺成本 C = V + S/N，年工艺成本 E = V·N + S（式 57.7.1），临界年产量 N_c = (S_A − S_B)/(V_B − V_A)（式 57.7.2），
//   投资回收期 τ = (K_A − K_B)/(E_B − E_A)（式 57.7.3，A 多投资时只有 E_A < E_B 才能回收）；
//   可变费用 V：A = 50.79 元/件（ex57_7.py 由 hub/route.py 按工作中心费率算出，批量 200），B 在 A 的基础上：磨削由 16 min 减到 10 min
//   （外圆磨床 52 元/h），数控车床多一道硬车（48 元/h，工时由滑块给，准备 20 min、批量 200），加 CBN 刀片费；
//   磨床每件占用：A 两台分摊（16.1 min / 2），B 一台 10.1 min；需求节拍 Fe/N，Fe = 204 000 min。
const VA7 = 50.7943, GRD_RATE = 52, CNC_RATE = 48, FE7 = 204000, GRD_A = 16.1, GRD_B = 10.1, TURN0 = 4.0;
function eval7(api) {
  const p = api.p, N = p.N;
  const VB = VA7 - 6.0 / 60 * GRD_RATE + (p.tht + 20 / 200) / 60 * CNC_RATE + p.cbn;     // 硬车工序的准备时间 20 min 分摊到批量 200
  const SA = p.KA / 10 + 10000, SB = p.KB / 10 + 4000;           // 不变费用：投资按 10 年折旧 + 维护（A 1 万、B 0.4 万元/年，示意）
  const EA = VA7 * N + SA, EB = VB * N + SB;
  const Nc = VB !== VA7 ? (SA - SB) / (VB - VA7) : Infinity;
  const tau = EA < EB ? (p.KA - p.KB) / (EB - EA) : Infinity;
  const need = FE7 / N, grdA = GRD_A / 2, grdB = GRD_B, cncB = 7.0 + p.tht / 2;
  return { N, VB, SA, SB, EA, EB, Nc, tau, need, grdA, grdB, cncB, okA: grdA <= need, okB: grdB <= need && cncB <= need };
}

WQ.lab({
  title: ["实验 57.7 工艺方案的技术经济分析", "Lab 57.7 Technical-economic comparison of process routes"],
  goal: ["SH-101 扩产时外圆磨床是瓶颈：比较 A 再买一台磨床与 B 用 CBN 硬车密封轴颈和轴伸两个方案。改年产量、投资、CBN 刀片费和硬车工时，看单件成本、年成本、临界年产量、回收期和瓶颈的负荷。",
         "With the grinder as SH-101's bottleneck, compare A (second grinder) with B (CBN hard turning of two diameters): vary volume, investment, insert cost and hard-turning time; see unit and annual cost, break-even, payback and bottleneck load."],
  scenes: [
    { id: "sh101", robot: true, name: ["SH-101 扩产", "SH-101 ramp-up"],
      params: { N: { value: 20000 }, KA: { value: 350000 }, KB: { value: 40000 }, cbn: { value: 3 }, tht: { value: 4 } },
      problem: { title: ["机器人问题：减速器订单翻了三倍，磨床排不过来", "Robot problem: reducer orders tripled, the grinder cannot keep up"],
                 text: ["WQR-105 减速器年产量要到 2 万台，SH-101 的外圆磨床每件 16 min，跟不上 10.2 min 的需求节拍。买一台磨床还是改成硬车？投资、成本、能力和风险都要比。",
                        "WQR-105 goes to 20 000 a year; SH-101's grinder needs 16 min per part against a 10.2 min takt. Buy a grinder or hard-turn? Compare investment, cost, capacity and risk."] } },
  ],
  params: [
    { id: "N", name: ["年产量 N", "Annual volume N"], min: 5000, max: 40000, step: 500, value: 20000, unit: "件", digits: 0 },
    { id: "KA", name: ["A 的投资 K_A（第二台磨床，示意）", "Investment A"], min: 100000, max: 600000, step: 10000, value: 350000, unit: "元", digits: 0 },
    { id: "KB", name: ["B 的投资 K_B（CBN 刀具、测头，示意）", "Investment B"], min: 0, max: 200000, step: 5000, value: 40000, unit: "元", digits: 0 },
    { id: "cbn", name: ["CBN 刀片费（每件）", "CBN insert cost per part"], min: 0.5, max: 8, step: 0.1, value: 3, unit: "元", digits: 1 },
    { id: "tht", name: ["硬车工时（每件）", "Hard-turning time"], min: 2, max: 8, step: 0.5, value: 4, unit: "min", digits: 1 },
  ],
  legend: [{ color: "var(--accent)", name: ["A 单件成本", "A unit cost"] }, { color: "var(--warm)", name: ["B 单件成本", "B unit cost"] }],
  tasks: [
    { id: "nc", text: ["其余不变，找出两方案年工艺成本相等的年产量（把 N 调到离临界年产量 500 件以内）。", "Find the break-even volume (N within 500 of it)."],
      demo: { scene: "sh101", set: { N: 34000, KA: 350000, KB: 40000, cbn: 3, tht: 4 }, press: [], wait: 1 } },
    { id: "pay", text: ["年产 3.5 万件时，A 的投资多少才能在 5 年内收回（与 B 比）？调出回收期不超过 5 年的投资。", "At 35 000/yr, what investment lets A pay back within 5 years?"],
      demo: { scene: "sh101", set: { N: 35000, KA: 120000, KB: 40000, cbn: 3, tht: 4 }, press: [], wait: 1 } },
    { id: "cap", text: ["增大年产量，找出 B 的磨床第一次跟不上需求节拍的年产量（误差 500 件以内）。", "Raise the volume until B's grinder first falls behind (within 500)."],
      demo: { scene: "sh101", set: { N: 20500, KA: 350000, KB: 40000, cbn: 3, tht: 4 }, press: [], wait: 1 } },
  ],
  think: ["算例里没有计入：硬车的试切验证费用、废品风险、磨床的占地和操作工、以后再扩产的余地。它们怎样影响选择？", "What the numbers leave out: trials, scrap risk, floor space and operators, future headroom — how do they change the choice?"],

  reset(api, s) {},
  update(dt, api, s) { api.stop(); },
  readouts(api) {
    const p = api.p, e = eval7(api), T = api.T, f = api.fmt;
    if (isFinite(e.Nc) && Math.abs(p.N - e.Nc) <= 500 && Math.abs(p.cbn - 3) < 1e-9 && Math.abs(p.tht - 4) < 1e-9) api.done("nc");
    if (Math.abs(p.N - 35000) < 1e-9 && isFinite(e.tau) && e.tau <= 5) api.done("pay");
    if (!e.okB && FE7 / (p.N - 500) >= e.grdB && Math.abs(p.tht - 4) < 1e-9) api.done("cap");
    return [
      [["可变费用 V：A / B", "variable V: A / B"], f(VA7, 2) + " / " + f(e.VB, 2) + T(" 元/件", " CNY/part")],
      [["不变费用 S：A / B", "fixed S: A / B"], f(e.SA, 0) + " / " + f(e.SB, 0) + T(" 元/年", " CNY/yr")],
      [["单件工艺成本 C：A / B", "unit cost: A / B"], f(VA7 + e.SA / e.N, 2) + " / " + f(e.VB + e.SB / e.N, 2) + T(" 元", " CNY")],
      [["年工艺成本 E：A / B", "annual cost: A / B"], f(e.EA, 0) + " / " + f(e.EB, 0) + T(" 元", " CNY")],
      [["临界年产量 N_c", "break-even N_c"], isFinite(e.Nc) && e.Nc > 0 ? f(e.Nc, 0) + T(" 件（高于它 A 更省）", " (A cheaper above)") : T("没有", "none")],
      [["A 的投资回收期 τ", "payback of A"], isFinite(e.tau) ? f(e.tau, 1) + T(" 年", " yr") : T("A 年成本不低于 B，收不回", "A never pays back")],
      [["磨床每件占用（需求节拍）", "grinder min/part (takt)"], T("A ", "A ") + f(e.grdA, 2) + T("，B ", ", B ") + f(e.grdB, 2) + "（" + f(e.need, 1) + "）" + (e.okB ? "" : T(" B 跟不上", " B falls behind"))],
    ];
  },
  draw(api) {
    const { w, h } = api, css = api.css, p = api.p;
    const pa = [], pb = [];
    for (let N = 5000; N <= 40000; N += 500) {
      const e = eval7({ p: Object.assign({}, p, { N }) });
      pa.push([N / 1000, VA7 + e.SA / N]); pb.push([N / 1000, e.VB + e.SB / N]);
    }
    const lo = Math.min(...pa.map((q) => q[1]), ...pb.map((q) => q[1])) - 1, hi = Math.min(Math.max(...pa.map((q) => q[1]), ...pb.map((q) => q[1])), lo + 20) + 1;
    const P = api.plot(w * 0.1, h * 0.06, w * 0.85, h * 0.8, [{ pts: pa, color: css("--accent") }, { pts: pb, color: css("--warm") }],
                       { xmin: 5, xmax: 40, ymin: lo, ymax: hi, xlabel: api.T("年产量 / 千件", "annual volume / 1000"), ylabel: api.T("单件工艺成本 / 元", "unit cost / CNY") });
    api.line(P.X(p.N / 1000), P.Y(lo), P.X(p.N / 1000), P.Y(hi), css("--ink"), 1, [4, 4]);
    const capB = FE7 / GRD_B / 1000;
    if (capB < 40) { api.line(P.X(capB), P.Y(lo), P.X(capB), P.Y(hi), css("--red"), 1.5, [6, 3]); api.label(api.T("B 的磨床到顶", "B grinder limit"), P.X(capB) + 4, P.Y(hi) + 14, css("--red"), 12); }
  },
});
