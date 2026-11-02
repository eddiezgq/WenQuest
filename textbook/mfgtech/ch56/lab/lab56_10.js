// 实验 56.10 路线方案比较（配 56.10 节）。计算与程序 56.10.1（ex56_10.py，factory/digital/hub/route.py 的 route_cost、cost_line）相同：
//   每道工序每件占用 t = 工时 + 准备时间/批量；热处理炉一炉 20 件，每件 t/20；单件成本 = Σ t/60 × 小时费率；
//   工作中心的负荷 = Σ t / 台数（炉子按每件），最大的是瓶颈；需求节拍 = 有效工作时间 / 年产量（250 天 × 2 班 × 480 min × 0.85）。
// 工作中心的台数与费率取工厂数据（factory/data.py）；普通车床（32 元/h，2 台，工时为数控的 1.9 倍）、车铣复合中心（95 元/h，1 台，27 min/件，
// 准备 45 min）、锻件的加工费（4 元/件）和锻模（36 000 元/年）是示意值。棒料 Ø60 × 142（3.15 kg），锻件毛坯 1.59 kg，材料 2.4 元/kg。
const WS10 = { saw: ["带锯床", 25, 1], cnc: ["数控车床", 48, 2], lathe: ["普通车床", 32, 2], tm: ["车铣复合中心", 95, 1], hob: ["滚齿机", 55, 1],
               key: ["键槽铣床", 36, 1], ht: ["热处理炉", 34, 20], grd: ["外圆磨床", 52, 1], qc: ["检验站", 40, 1] };
const FE10 = 250 * 2 * 480 * 0.85, PRICE10 = 2.4, M_BAR = Math.PI / 4 * 60 * 60 * 142 * 7.85e-6, M_FORG = 1.5916, DIE = 36000;
function ops10(blank, eq) {
  const o = [];
  if (blank === 0) o.push(["下料", "saw", 2, 10]);
  if (eq === 2) o.push(["车铣复合", "tm", 27, 45]);
  else {
    const f = eq === 1 ? 1.9 : 1, ws = eq === 1 ? "lathe" : "cnc", su = eq === 1 ? [10, 10] : [30, 20];
    o.push(["粗车", ws, (blank === 1 ? 7 : 14) * f, su[0]], ["精车", ws, 12 * f, su[1]]);
  }
  o.push(["滚齿", "hob", 22, 40]);
  if (eq !== 2) o.push(["铣键槽", "key", 8, 20]);
  o.push(["渗碳淬火", "ht", 20, 60], ["磨外圆", "grd", 16, 20], ["检验", "qc", 8, 5]);
  return o;
}
function cost10(blank, eq, N, batch) {
  let mach = 0; const load = {};
  ops10(blank, eq).forEach(([name, ws, m, su]) => {
    const [wn, r, n] = WS10[ws], t = m + su / Math.max(batch, 1), furnace = ws === "ht", tu = furnace ? t / n : t;
    mach += tu / 60 * r; load[wn] = (load[wn] || 0) + (furnace ? tu : t / n);
  });
  const neck = Object.entries(load).reduce((a, b) => (b[1] > a[1] ? b : a));
  const bl = blank === 0 ? M_BAR * PRICE10 : M_FORG * PRICE10 + 4 + DIE / N;
  return { mach, blank: bl, total: mach + bl, neck: neck[0], takt: neck[1], need: FE10 / N, setups: eq === 2 ? 4 : 7 };
}
function turn10(eq, batch) { let c = 0; ops10(0, eq).filter((x) => x[0] === "粗车" || x[0] === "精车").forEach(([_, ws, m, su]) => { c += (m + su / batch) / 60 * WS10[ws][1]; }); return c; }
const BL10 = [["棒料 Ø60", "bar Ø60"], ["模锻件", "die forging"]], EQ10 = [["数控车床（分散）", "CNC lathes (dispersed)"], ["普通车床（分散）", "engine lathes (dispersed)"], ["车铣复合中心（集中）", "turn-mill centre (concentrated)"]];

WQ.lab({
  title: ["实验 56.10 路线方案比较", "Lab 56.10 Comparing process routes"],
  goal: ["改年产量、批量、毛坯和粗车、精车的设备，看 SH-101 各方案的单件成本、瓶颈与节拍怎样变化，找出方案的“转折点”——临界年产量和临界批量。",
         "Change the annual volume, batch, blank and the turning equipment; see SH-101's unit cost, bottleneck and takt move, and find the turning points — the break-even volume and batch."],
  scenes: [
    { id: "sh101", robot: true, name: ["SH-101 输入齿轮轴", "SH-101 input pinion shaft"],
      params: { N: { value: 6000 }, batch: { value: 100 }, blank: { value: 0 }, eq: { value: 0 } },
      problem: { title: ["机器人问题：减速器扩产，SH-101 的路线要不要改", "Robot problem: the reducer line ramps up — should SH-101's route change"],
                 text: ["WQR-105 减速器现在年产 6000 台，SH-101 每批 100 件，用棒料和现有设备分散加工。销量上去以后，要不要改用模锻件？要不要买车铣复合中心？小批试制时又该用什么设备？", "WQR-105 runs 6000 a year; SH-101 is made in batches of 100 from bar on the existing machines. As sales grow, should it move to forgings, or to a turn-mill centre? And what suits small trial batches?"] } },
  ],
  params: [
    { id: "N", name: ["年产量 N", "Annual volume N"], min: 1000, max: 30000, step: 100, value: 6000, unit: "件", digits: 0 },
    { id: "batch", name: ["批量", "Batch size"], min: 1, max: 500, step: 1, value: 100, unit: "件", digits: 0 },
    { id: "blank", name: ["毛坯（0 棒料、1 模锻件）", "Blank (0 bar, 1 forging)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "eq", name: ["粗车、精车的设备（0 数控车床、1 普通车床、2 车铣复合中心）", "Turning (0 CNC, 1 engine lathe, 2 turn-mill)"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
  ],
  legend: [{ color: "var(--accent)", name: ["棒料", "bar"] }, { color: "var(--red)", name: ["模锻件", "forging"] }, { color: "var(--warm)", name: ["数控车床 / 普通车床（下图）", "CNC / engine lathe (lower chart)"] }],
  tasks: [
    { id: "ncrit", text: ["设备用数控车床，批量 100：年产量多大时，棒料和模锻件的单件成本相等（误差在 100 件以内）？", "CNC turning, batch 100: at what annual volume do bar and forging cost the same (within 100 pcs)?"],
      demo: { scene: "sh101", set: { eq: 0, batch: 100, N: 5800 }, press: [], wait: 1 } },
    { id: "bcrit", text: ["粗车、精车用数控车床还是普通车床：批量多大时两者单件成本相等？（把批量调到最接近的整数）", "CNC or engine lathe for turning: at what batch do they cost the same? (nearest whole batch)"],
      demo: { scene: "sh101", set: { batch: 5 }, press: [], wait: 1 } },
    { id: "neck", text: ["方案 A（棒料、数控车床，批量 100）：年产量增加到多少时，瓶颈第一次跟不上需求节拍？瓶颈是哪个工作中心？", "Route A (bar, CNC, batch 100): at what volume does the bottleneck first fall behind the demand takt, and which centre is it?"],
      demo: { scene: "sh101", set: { blank: 0, eq: 0, batch: 100, N: 9200 }, press: [], wait: 1 } },
  ],
  think: ["本实验的成本只算了机床、人工和毛坯。工序集中还减少了在制品、搬运和废品，提高了同轴度；锻件还改善了齿根的金属流线。这些怎样写进方案论证？", "The costs here cover machines, labour and blank only. Concentration also cuts WIP, handling and scrap and improves runout; forgings improve grain flow at the tooth root. How do these enter the justification?"],

  reset(api, s) {},
  update(dt, api, s) { api.stop(); },
  readouts(api) {
    const p = api.p, T = api.T, b = Math.round(p.blank), e = Math.round(p.eq), N = p.N, B = p.batch;
    const r = cost10(b, e, N, B), bar = cost10(0, e, N, B), forg = cost10(1, e, N, B);
    const nc = DIE / (bar.total - (forg.total - DIE / N));
    if (e === 0 && Math.abs(B - 100) < 1e-9 && Math.abs(N - nc) <= 100) api.done("ncrit");
    const cn = turn10(0, B), cl = turn10(1, B);
    const sl = (x) => { const a = ops10(0, x).filter((o) => o[0] === "粗车" || o[0] === "精车"); return [a.reduce((s, o) => s + o[2] / 60 * WS10[o[1]][1], 0), a.reduce((s, o) => s + o[3] / 60 * WS10[o[1]][1], 0)]; };
    const [a1, s1] = sl(0), [a2, s2] = sl(1), bc = (s1 - s2) / (a2 - a1);
    if (Math.abs(B - Math.round(bc)) < 1e-9) api.done("bcrit");
    if (b === 0 && e === 0 && Math.abs(B - 100) < 1e-9 && r.takt > r.need && cost10(0, 0, N - 100, B).takt <= FE10 / (N - 100)) api.done("neck");
    return [
      [["方案", "route"], T(...BL10[b]) + " + " + T(...EQ10[e])],
      [["单件成本（毛坯 + 机床与人工）", "unit cost (blank + machines)"], api.fmt(r.total, 1) + T(" 元", " CNY") + `（${api.fmt(r.blank, 1)} + ${api.fmt(r.mach, 1)}）`],
      [["棒料 / 模锻件（同样设备）", "bar / forging (same equipment)"], api.fmt(bar.total, 1) + " / " + api.fmt(forg.total, 1) + T(" 元；临界年产量 ≈ ", " CNY; break-even ≈ ") + api.fmt(nc, 0)],
      [["瓶颈与每件占用", "bottleneck"], T(r.neck, r.neck) + " " + api.fmt(r.takt, 1) + " min"],
      [["需求节拍 Fe/N", "demand takt Fe/N"], api.fmt(r.need, 1) + " min" + (r.takt > r.need ? T("（瓶颈跟不上！）", " (bottleneck cannot keep up!)") : T("（跟得上）", " (keeps up)"))],
      [["粗车 + 精车：数控 / 普通车床", "turning: CNC / engine lathe"], api.fmt(cn, 2) + " / " + api.fmt(cl, 2) + T(" 元；临界批量 ≈ ", " CNY; break-even batch ≈ ") + api.fmt(bc, 1)],
      [["装夹次数", "set-ups"], String(r.setups)],
    ];
  },
  draw(api) {
    const { w, h } = api, css = api.css, p = api.p, e = Math.round(p.eq), B = p.batch;
    const bar = [], forg = [];
    for (let N = 1000; N <= 30000; N += 250) { bar.push([N / 1000, cost10(0, e, N, B).total]); forg.push([N / 1000, cost10(1, e, N, B).total]); }
    const ymax = Math.max(...bar.map((q) => q[1]), ...forg.slice(4).map((q) => q[1])) * 1.25;
    const P = api.plot(w * 0.08, h * 0.05, w * 0.86, h * 0.36, [{ pts: bar, color: css("--accent") }, { pts: forg, color: css("--red") }],
                       { xmin: 1, xmax: 30, ymin: 0, ymax, xlabel: api.T("年产量 / 千件", "annual volume / 1000"), ylabel: api.T("单件成本 / 元", "unit cost / CNY") });
    api.line(P.X(p.N / 1000), P.Y(0), P.X(p.N / 1000), P.Y(ymax), css("--ink"), 1, [4, 4]);
    const cn = [], cl = [];
    for (let b = 1; b <= 60; b += 1) { cn.push([b, turn10(0, b)]); cl.push([b, turn10(1, b)]); }
    const Q = api.plot(w * 0.08, h * 0.56, w * 0.86, h * 0.32, [{ pts: cn, color: css("--warm") }, { pts: cl, color: css("--muted") }],
                       { xmin: 1, xmax: 60, ymin: 0, ymax: 60, xlabel: api.T("批量 / 件（粗车 + 精车的单件成本；橙：数控车床，灰：普通车床）", "batch (turning cost; orange CNC, grey engine lathe)"), ylabel: api.T("元", "CNY") });
    if (B <= 60) api.line(Q.X(B), Q.Y(0), Q.X(B), Q.Y(60), css("--ink"), 1, [4, 4]);
  },
});
