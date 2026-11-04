// 实验 11.6 载荷谱、平均应力修正与迈因纳累积（配 11.4、11.6 节）。
// 一个“块”（重复的载荷单元）里有两档循环：应力幅 σa1、σa2 MPa，各 n1、n2 次；平均应力 = 应力幅 × 平均/幅值之比 r（两档相同）；
// 全部应力乘载荷系数 λ。每档：平均应力修正（古德曼 σa/(1 − |σm|/R_m)、格伯 σa/(1 − (σm/R_m)²)、SWT √(σmax·σa)、不修正），
// S–N 曲线：S_D = σ₋₁·β·ε（本章取精车 β = 0.85，网页默认为磨削 0.92；ε = 0.85 与网页默认相同），N_D、斜率 k 取数字工厂材料库；
// N < N_D 时 N = N_D (S_D/σa,eq)^k，N > N_D 时按海巴赫修正斜率 2k − 1。与 cae/fatigue.py（程序 11.10.1）同一组公式。
// 一块的运行时长随场景：WQ-CR5 4.8 s（一个节拍），WQR-105 一年（两班 4 000 h），回形针 2 s。
// 场景初值：WQ-CR5 大臂根部内角（程序 11.6.1 最大的两个循环，r = 1.7）；WQR-105 在矿山现场的输出轴外伸段，
// 每天起停一次，一年 365 块，卡料日 49 天（第 10 章 10.7 节的名义当量应力的一半作应力幅，R = 0 即 r = 1，不计键槽）；
// 回形针：弯折时表面的弹性计算应力 E·ε，远超抗拉强度——应力–寿命法在这里不能用（11.7 节用应变–寿命法）。回形针钢丝的 σ₋₁ 取 0.45 R_m（本书取值）。
const MAT11_6 = [
  { name: ["6061-T6 铝合金", "6061-T6 aluminum"], s1: 96.5, ND: 5e8, k: 8, Rm: 310 },
  { name: ["45 钢调质", "1045 Q&T"], s1: 275, ND: 1e7, k: 9, Rm: 640 },
  { name: ["40Cr 调质", "40Cr Q&T"], s1: 355, ND: 1e7, k: 9, Rm: 735 },
  { name: ["回形针钢丝（示意）", "paper-clip wire (illustrative)"], s1: 270, ND: 1e7, k: 9, Rm: 600 },
];
const BLOCK11_6 = { arm: 4.8, mine: 4000 * 3600, clip: 2 };   // 一块的运行时长 s
function eq11_6(sa, sm, m, meth) {
  if (meth === 0) return sa / (1 - Math.min(Math.abs(sm) / m.Rm, 0.999));
  if (meth === 1) return sa / (1 - Math.min((sm / m.Rm) ** 2, 0.999));
  if (meth === 2) return Math.sqrt(Math.max(sm + sa, 0) * sa);
  return sa;
}
function life11_6(saeq, m, SD) {
  if (saeq >= m.Rm) return 0;                                 // 超出应力–寿命法的范围
  if (saeq >= SD) return m.ND * Math.pow(SD / saeq, m.k);
  return m.ND * Math.pow(SD / saeq, 2 * m.k - 1);
}
function calc11_6(p) {
  const m = MAT11_6[Math.round(p.mat)], SD = m.s1 * 0.85 * 0.85;
  const lv = [[p.sa1, p.n1], [p.sa2, p.n2]];
  let D = 0, bad = false;
  const rows = lv.map(([sa0, n]) => {
    const sa = sa0 * p.lam, sm = sa * p.r, saeq = eq11_6(sa, sm, m, Math.round(p.meth)), N = life11_6(saeq, m, SD);
    if (N === 0 && n > 0) bad = true;
    const d = n > 0 && N > 0 && isFinite(N) ? n / N : 0;
    D += d;
    return { sa, sm, saeq, N, n, d };
  });
  return { m, SD, rows, D, bad, blocks: bad ? 0 : (D > 0 ? 1 / D : Infinity) };
}
WQ.lab({
  title: ["实验 11.6 载荷谱、平均应力修正与迈因纳累积", "Lab 11.6 Load spectrum, mean-stress correction and Miner's rule"],
  goal: ["改一个载荷块里两档循环的应力幅和次数、平均应力、材料和修正方法，看每档的损伤、整块的损伤和寿命；体会“大循环说了算”、平均应力修正的差别，以及应力–寿命法在什么时候不能用。",
         "Change the amplitudes and counts of two cycle levels in a load block, the mean stress, material and correction; read the damage per level, per block and the life. See that the big cycles dominate, how the mean-stress corrections differ, and when stress–life no longer applies."],
  scenes: [
    { id: "arm", robot: true, name: ["WQ-CR5 大臂根部内角", "WQ-CR5 arm root corner"],
      problem: { title: ["工程问题：大臂的疲劳寿命够不够，还能放大多少", "Engineering problem: is the arm's fatigue life enough, and by how much could loads grow"],
                 text: ["标准动作每 4.8 s 一个节拍，两班 5 年约 1.5 × 10⁷ 个节拍。大臂根部内角每个节拍里有一个大循环和几个小循环，平均应力是应力幅的 1.7 倍。寿命够吗？载荷放大几倍时 5 年刚好用完？",
                        "The standard motion repeats every 4.8 s: about 1.5 × 10⁷ cycles in 5 years of two shifts. The arm's root corner sees one big cycle and a few small ones per motion cycle, with a mean 1.7 times the amplitude. Is the life enough? By what factor could the loads grow before 5 years are used up?"] } },
    { id: "mine", robot: true, name: ["WQR-105 矿山现场（输出轴）", "WQR-105 at the mine (output shaft)"],
      problem: { title: ["工程问题：每天一次起停，卡料的日子伤害多大", "Engineering problem: one start-stop a day — how much do the jam days cost"],
                 text: ["矿山皮带机每天起停一次，转矩 0 → 当天最大值 → 0。一年 365 天里有 49 天卡料，转矩更大。按应力–寿命法，卡料日占了一年损伤的多少？",
                        "The mine conveyor starts and stops once a day: torque 0 → the day's maximum → 0. On 49 of 365 days the belt jams and the torque is higher. By stress–life, what share of a year's damage comes from the jam days?"] } },
    { id: "clip", name: ["反复弯折回形针", "Bending a paper clip back and forth"],
      problem: { title: ["生活中的例子：回形针弯几下就断", "Everyday example: a paper clip breaks after a few bends"],
                 text: ["把回形针来回弯折，几个来回就断了。按弹性公式算出的表面应力 σ = E·ε 有几万 MPa，远超抗拉强度。应力–寿命法还能用吗？",
                        "Bend a paper clip back and forth and it breaks within a few bends. The elastic surface stress σ = E·ε is tens of thousands of MPa, far above the tensile strength. Can stress–life still be used?"] } },
  ],
  params: [
    { id: "sa1", name: ["第 1 档应力幅 σa1", "Level 1 amplitude σa1"], min: 0, max: 40000, step: 0.1, value: 6.1, unit: "MPa", digits: 1 },
    { id: "n1", name: ["第 1 档每块次数 n1", "Level 1 count n1"], min: 0, max: 1000, step: 1, value: 1, unit: "", digits: 0 },
    { id: "sa2", name: ["第 2 档应力幅 σa2", "Level 2 amplitude σa2"], min: 0, max: 1000, step: 0.1, value: 3.1, unit: "MPa", digits: 1 },
    { id: "n2", name: ["第 2 档每块次数 n2", "Level 2 count n2"], min: 0, max: 1000, step: 1, value: 1, unit: "", digits: 0 },
    { id: "r", name: ["平均应力 / 应力幅 r", "Mean / amplitude r"], min: -3, max: 10, step: 0.1, value: 1.7, unit: "", digits: 1 },
    { id: "lam", name: ["载荷系数 λ", "Load factor λ"], min: 0.1, max: 30, step: 0.1, value: 1, unit: "", digits: 1 },
    { id: "mat", name: ["材料（0 6061、1 45、2 40Cr、3 钢丝）", "Material (0 6061, 1 1045, 2 40Cr, 3 wire)"], min: 0, max: 3, step: 1, value: 0, unit: "", digits: 0 },
    { id: "meth", name: ["修正（0 古德曼、1 格伯、2 SWT、3 不修正）", "Correction (0 Goodman, 1 Gerber, 2 SWT, 3 none)"], min: 0, max: 3, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "#1f77b4", name: ["S–N 曲线（S_D 修正后，海巴赫）", "S–N curve (corrected S_D, Haibach)"] }, { color: "#d62728", name: ["各档的等效应力幅", "equivalent amplitude per level"] }],
  tasks: [
    { id: "arm", robot: true, text: ["WQ-CR5 大臂（初值，λ = 1）：读出整块的损伤和寿命；两档里哪一档的损伤最大？", "WQ-CR5 arm (initial values, λ = 1): read the damage per block and the life; which of the two levels does the most damage?"],
      demo: { scene: "arm", set: { sa1: 6.1, n1: 1, sa2: 3.1, n2: 1, r: 1.7, lam: 1, mat: 0, meth: 0 }, press: ["start"], wait: 1 } },
    { id: "lam", robot: true, text: ["把 λ 慢慢加大，找出寿命刚好等于 5 年两班（1.5 × 10⁷ 块）的 λ，与程序 11.6.1 比较。这时第 1 档的等效应力幅是 S_D 的几倍？", "Raise λ until the life equals 5 years of two shifts (1.5 × 10⁷ blocks); compare with Program 11.6.1. How many times S_D is the level-1 equivalent amplitude then?"],
      demo: { scene: "arm", set: { lam: 11.1 }, press: ["start"], wait: 1 } },
    { id: "mine", robot: true, text: ["WQR-105 矿山现场：卡料日 σa = 122 MPa、49 次，正常日 σa = 100 MPa、316 次，45 钢、R = 0（r = 1）、一块 = 一年（两班 4 000 h）。改用格伯、SWT，寿命怎样变？", "WQR-105 at the mine: jam days σa = 122 MPa, 49 times; normal days σa = 100 MPa, 316 times; 1045, R = 0 (r = 1), one block = one year (4000 h of two-shift running). How does the life change with Gerber or SWT?"],
      demo: { scene: "mine", set: { sa1: 122, n1: 49, sa2: 100, n2: 316, r: 1, lam: 1, mat: 1, meth: 0 }, press: ["start"], wait: 1 } },
    { id: "clip", text: ["回形针：Ø1 mm 钢丝绕 3 mm 半径弯折，εa ≈ 0.17，弹性应力 E·ε ≈ 34 500 MPa（材料 3，r = 0）。程序给出什么？为什么要改用应变–寿命法？", "Paper clip: Ø1 mm wire bent round a 3 mm radius, εa ≈ 0.17, elastic stress E·ε ≈ 34 500 MPa (material 3, r = 0). What does the lab say, and why switch to strain–life?"],
      demo: { scene: "clip", set: { sa1: 34500, n1: 1, sa2: 0, n2: 0, r: 0, lam: 1, mat: 3, meth: 3 }, press: ["start"], wait: 1 } },
  ],
  think: ["迈因纳法则把每个循环的损伤简单相加，不管先后顺序；而 S–N 曲线的斜率 k = 8–9，应力幅大 10%，损伤就大一倍多——所以载荷谱的“头”（少数大循环）几乎决定了寿命，测载荷时最要紧的是别漏掉大的。海巴赫修正让低于 S_D 的小循环也有一点损伤；什么时候它要紧，什么时候不要紧？",
          "Miner's rule just adds the damage of each cycle, ignoring order; with an S–N slope k = 8–9, a 10% larger amplitude more than doubles the damage — so the 'head' of the spectrum (the few big cycles) nearly decides the life, and a load measurement must not miss the big ones. Haibach gives a little damage to cycles below S_D: when does that matter and when not?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    const p = api.p;
    s.r = calc11_6(p);
    if (api.scene === "arm" && Math.round(p.mat) === 0 && Math.abs(p.lam - 1) < 0.05) api.done("arm");
    if (api.scene === "arm" && p.lam > 5) api.done("lam");
    if (api.scene === "mine" && Math.round(p.mat) === 1) api.done("mine");
    if (api.scene === "clip" && s.r.bad) api.done("clip");
    api.stop();
  },
  readouts(api, s) {
    const f = api.fmt, r = s.r;
    if (!r) return [[["状态", "Status"], api.T("按“计算”开始", "press Compute")]];
    const e = (x) => (isFinite(x) ? x.toExponential(2) : "∞");
    const out = [[["修正后的疲劳极限 S_D", "Corrected fatigue limit S_D"], f(r.SD, 1) + " MPa"]];
    r.rows.forEach((w, i) => {
      if (w.n > 0) out.push([[`第 ${i + 1} 档：σa,eq → N → 每块损伤`, `Level ${i + 1}: σa,eq → N → damage per block`],
        f(w.saeq, 1) + " MPa → " + (w.N === 0 ? api.T("超出范围", "out of range") : e(w.N)) + " → " + e(w.d)]);
    });
    out.push([["每块损伤 D", "Damage per block D"], e(r.D)]);
    if (r.bad) out.push([["寿命", "Life"], api.T("σa,eq ≥ R_m：应力–寿命法不适用，用应变–寿命法（11.7 节）", "σa,eq ≥ R_m: stress–life does not apply; use strain–life (11.7)")]);
    else {
      out.push([["寿命（块）", "Life (blocks)"], e(r.blocks)]);
      const yrs = r.blocks * (BLOCK11_6[api.scene] || 4.8) / 3600 / 4000;      // 两班：每年 250 天 × 16 h
      out.push([["寿命（两班的年数）", "Life (years of two shifts)"], isFinite(yrs) ? (yrs > 1e6 ? e(yrs) : f(yrs, 2)) : "∞"]);
      const tot = r.rows.reduce((a, w) => a + w.d, 0);
      if (tot > 0) out.push([["第 1 档占的损伤", "Share of level 1"], f(r.rows[0].d / tot * 100, 2) + "%"]);
    }
    return out;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    if (!s.r) { api.label(api.T("按“计算”看 S–N 曲线上的各档", "Press Compute to place the levels on the S–N curve"), w / 2, h / 2, css("--muted"), 14, "center"); return; }
    const m = s.r.m, SD = s.r.SD, curve = [];
    for (let lg = 3; lg <= 10.001; lg += 0.05) {
      const N = Math.pow(10, lg);
      let sa = N <= m.ND ? SD * Math.pow(m.ND / N, 1 / m.k) : SD * Math.pow(m.ND / N, 1 / (2 * m.k - 1));
      sa = Math.min(sa, m.Rm);
      curve.push([lg, Math.log10(sa)]);
    }
    const pts = [];
    s.r.rows.forEach((wv) => { if (wv.n > 0 && wv.saeq > 0) pts.push([wv.N > 0 && isFinite(wv.N) ? Math.min(Math.log10(wv.N), 10) : (wv.N === 0 ? 3 : 10), Math.log10(wv.saeq)]); });
    const series = [{ pts: curve, color: "#1f77b4" }];
    pts.forEach((q) => series.push({ pts: [[q[0] - 0.05, q[1]], [q[0] + 0.05, q[1]]], color: "#d62728" }));
    const ys = curve.map((q) => q[1]).concat(pts.map((q) => q[1]));
    api.plot(60, 20, w - 90, h - 70, series, { xmin: 3, xmax: 10, ymin: Math.min(...ys) - 0.2, ymax: Math.max(...ys) + 0.2,
      xlabel: api.T("lg N（循环次数的常用对数）", "lg N (log of cycles)"), ylabel: api.T("lg σa,eq（MPa）", "lg σa,eq (MPa)") });
  },
});
