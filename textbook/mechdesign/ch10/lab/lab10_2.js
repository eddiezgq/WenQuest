// 实验 10.2 同一个点按三种强度理论校核（配 10.2、10.3 节）。平面应力，一点上的正应力 σ 和切应力 τ：
// 主应力 σ1,3 = σ/2 ± √(σ²/4 + τ²)（σ2 = 0）；
// 特雷斯卡 σ_eq = σ1 − σ3（σ1、σ3 异号时）或 max(|σ1|, |σ3|)；冯·米塞斯 σ_eq = √(σ² + 3τ²)；最大正应力 σ1 ≤ σt、−σ3 ≤ σc；
// 库仑–莫尔 σ1/σt − σ3/σc ≤ 1（σ1 ≥ 0 ≥ σ3 时；同号时退化为最大正应力）。与程序 10.2.1、10.3.1 同一组公式（_ch10.py）。
// 材料取数字工厂材料库：40Cr 调质 σs 540、6061-T6 σs 276、HT200 σt 200（σc 取 3.5σt，本书取值）；粉笔的强度是示意值。
// 场景的初值：SH-301 齿轮位（第 8 章）、铸铁轴承座受压最厉害的点（程序 10.3.1）、粉笔纯扭转（示意）。WQ-CR5 大臂的最危险点近似单向拉伸，两种塑性理论几乎一样（程序 10.2.1），没有单列场景。
const MAT10_2 = [
  { name: ["40Cr 调质（塑性）", "40Cr Q&T (ductile)"], st: 540, sc: 540, ductile: true },
  { name: ["6061-T6 铝（塑性）", "6061-T6 Al (ductile)"], st: 276, sc: 276, ductile: true },
  { name: ["HT200 铸铁（脆性）", "HT200 cast iron (brittle)"], st: 200, sc: 700, ductile: false },
  { name: ["粉笔（脆性，示意）", "chalk (brittle, illustrative)"], st: 2, sc: 15, ductile: false },
];
function prin10_2(s, t) { const c = s / 2, r = Math.sqrt(s * s / 4 + t * t); return [c + r, c - r]; }
function eq10_2(s, t, m) {
  const [s1, s3] = prin10_2(s, t);
  const tresca = Math.max(s1, 0) - Math.min(s3, 0);            // σ2 = 0：σ_max − σ_min
  const vm = Math.sqrt(s * s + 3 * t * t);
  const rank = Math.max(s1 > 0 ? s1 / m.st : 0, s3 < 0 ? -s3 / m.sc : 0);
  const cm = s1 >= 0 && s3 <= 0 ? s1 / m.st - s3 / m.sc : rank;
  return { s1, s3, tresca, vm, SFt: m.st / tresca, SFv: m.st / vm, SFr: 1 / rank, SFc: 1 / cm,
           ang: 0.5 * Math.atan2(2 * t, s) * 180 / Math.PI };
}
WQ.lab({
  title: ["实验 10.2 同一个点按三种强度理论校核", "Lab 10.2 One point, three strength theories"],
  goal: ["改一点上的正应力、切应力和材料，比较特雷斯卡、冯·米塞斯、最大正应力、库仑–莫尔给出的安全系数，看清楚塑性材料和脆性材料各该用哪一个。",
         "Change the normal and shear stress at a point and the material; compare the safety factors of Tresca, von Mises, maximum normal stress and Coulomb–Mohr, and see which belongs to ductile and which to brittle materials."],
  scenes: [
    { id: "shaft", robot: true, name: ["SH-301 齿轮位（40Cr）", "SH-301 gear seat (40Cr)"],
      problem: { title: ["工程问题：弯扭组合的轴，按哪个理论", "Engineering problem: which theory for a shaft in bending and torsion"],
                 text: ["减速器输出轴的齿轮位表面一点，弯曲正应力和扭转切应力同时存在。两种塑性理论差多少？哪个偏保守？",
                        "A point on the gear seat of the output shaft carries bending and torsional stress together. How far apart are the two ductile theories, and which is conservative?"] } },
    { id: "iron", robot: true, name: ["铸铁轴承座（HT200）", "Cast-iron bearing seat (HT200)"],
      problem: { title: ["工程问题：铸铁件能不能看冯·米塞斯云图", "Engineering problem: can you read a von Mises plot for cast iron"],
                 text: ["有限元软件默认给冯·米塞斯应力。轴承座孔底受压最厉害的那一点，冯·米塞斯应力不小；按脆性材料的理论，它危险吗？",
                        "FE software shows von Mises by default. At the most compressed point of the bearing bore the von Mises stress is not small; is it dangerous by a brittle-material theory?"] } },
    { id: "chalk", name: ["粉笔扭断", "Twisting chalk"],
      problem: { title: ["生活中的例子：粉笔为什么扭成螺旋面", "Everyday example: why chalk breaks in a spiral"],
                 text: ["两手拧一支粉笔，它断开的面不是横截面，而是一个 45° 的螺旋面。纯扭转时哪个方向的拉应力最大？",
                        "Twist a stick of chalk and it breaks not across but along a 45° spiral. Under pure torsion, in which direction is the tension largest?"] } },
  ],
  params: [
    { id: "s", name: ["正应力 σ", "Normal stress σ"], min: -800, max: 800, step: 0.1, value: 16.2, unit: "MPa", digits: 1 },
    { id: "t", name: ["切应力 τ", "Shear stress τ"], min: 0, max: 500, step: 0.1, value: 27.9, unit: "MPa", digits: 1 },
    { id: "mat", name: ["材料（0 40Cr、1 6061、2 HT200、3 粉笔）", "Material (0 40Cr, 1 6061, 2 HT200, 3 chalk)"], min: 0, max: 3, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "#1f77b4", name: ["冯·米塞斯", "von Mises"] }, { color: "#d62728", name: ["特雷斯卡", "Tresca"] },
           { color: "#2ca02c", name: ["库仑–莫尔", "Coulomb–Mohr"] }, { color: "#ff7f0e", name: ["最大正应力", "max normal stress"] }],
  tasks: [
    { id: "shaft", robot: true, text: ["SH-301 齿轮位（σ = 16.2、τ = 27.9 MPa，40Cr）：读出特雷斯卡和冯·米塞斯的安全系数，相差百分之几？", "SH-301 gear seat (σ = 16.2, τ = 27.9 MPa, 40Cr): read the Tresca and von Mises factors; how many percent apart?"],
      demo: { scene: "shaft", set: { s: 16.2, t: 27.9, mat: 0 }, press: ["start"], wait: 1 } },
    { id: "shear", robot: true, text: ["把 σ 改为 0、τ = 100 MPa（纯剪切，像急停时的 RJ-201）：两种塑性理论差多少？这是它们差得最多的情况。", "Set σ = 0, τ = 100 MPa (pure shear, like RJ-201 at an emergency stop): how far apart are the two ductile theories? This is their largest difference."],
      demo: { scene: "shaft", set: { s: 0, t: 100, mat: 0 }, press: ["start"], wait: 1 } },
    { id: "iron", robot: true, text: ["铸铁轴承座受压最厉害的点（σ = −3.2、τ = 0.3 MPa，HT200）：按冯·米塞斯（强度取 σt）和按库仑–莫尔的安全系数各是多少？", "Most compressed point of the cast-iron seat (σ = −3.2, τ = 0.3 MPa, HT200): the factor by von Mises (strength σt) and by Coulomb–Mohr?"],
      demo: { scene: "iron", set: { s: -3.2, t: 0.3, mat: 2 }, press: ["start"], wait: 1 } },
    { id: "chalk", text: ["粉笔纯扭转（σ = 0、τ = 1 MPa，材料 3）：最大拉应力在哪个方向？哪个理论先判它坏？", "Chalk in pure torsion (σ = 0, τ = 1 MPa, material 3): in which direction is the largest tension, and which theory says it fails first?"],
      demo: { scene: "chalk", set: { s: 0, t: 1, mat: 3 }, press: ["start"], wait: 1 } },
  ],
  think: ["塑性材料用特雷斯卡或冯·米塞斯（屈服由切应力决定，与正应力的正负无关）；脆性材料用最大正应力或库仑–莫尔（断裂由拉应力决定，受压强得多）。有限元软件默认给的冯·米塞斯云图，对铸铁件会把受压的地方标成“危险”。数字工厂的“仿真与分析”目前只给冯·米塞斯，你会怎样从它的结果判断铸铁件？",
          "Ductile materials take Tresca or von Mises (yield is governed by shear, regardless of the sign of the normal stress); brittle materials take maximum normal stress or Coulomb–Mohr (fracture is governed by tension; they are far stronger in compression). The default von Mises plot marks compressed regions of a cast-iron part as 'dangerous'. The factory's Simulation & analysis currently gives only von Mises — how would you judge a cast-iron part from it?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    const p = api.p, m = MAT10_2[Math.round(p.mat)];
    s.r = eq10_2(p.s, p.t, m);
    s.m = m;
    if (api.scene === "shaft" && Math.round(p.mat) === 0 && Math.abs(p.s) > 1) api.done("shaft");
    if (api.scene === "shaft" && Math.abs(p.s) < 0.05 && p.t > 1) api.done("shear");
    if (api.scene === "iron" && Math.round(p.mat) === 2 && p.s < 0) api.done("iron");
    if (api.scene === "chalk" && Math.round(p.mat) === 3) api.done("chalk");
    api.stop();
  },
  readouts(api, s) {
    const f = api.fmt, r = s.r;
    if (!r) return [[["状态", "Status"], api.T("按“计算”开始", "press Compute")]];
    return [
      [["主应力 σ1、σ3", "Principal σ1, σ3"], f(r.s1, 2) + " / " + f(r.s3, 2) + " MPa"],
      [["σ1 与 σ 方向的夹角", "Angle of σ1 from σ"], f(r.ang, 1) + "°"],
      [["特雷斯卡 σ1 − σ3 → 安全系数", "Tresca σ1 − σ3 → factor"], f(r.tresca, 2) + " MPa → " + f(r.SFt, 2)],
      [["冯·米塞斯 → 安全系数", "von Mises → factor"], f(r.vm, 2) + " MPa → " + f(r.SFv, 2)],
      [["最大正应力 → 安全系数", "Max normal stress → factor"], f(r.SFr, 2)],
      [["库仑–莫尔 → 安全系数", "Coulomb–Mohr → factor"], f(r.SFc, 2)],
      [["该用哪个", "Which to use"], s.m.ductile ? api.T("塑性材料：特雷斯卡或冯·米塞斯", "ductile: Tresca or von Mises") : api.T("脆性材料：库仑–莫尔或最大正应力", "brittle: Coulomb–Mohr or max normal")],
    ];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    if (!s.r) { api.label(api.T("按“计算”比较四种判据", "Press Compute to compare the four criteria"), w / 2, h / 2, css("--muted"), 14, "center"); return; }
    const m = s.m, p = api.p, N = 240;
    const curves = { vm: [], tr: [], cm: [], rk: [] };
    for (let i = 0; i <= N; i++) {               // 沿各个方向 (cos φ, sin φ) 放大，碰到判据 = 1 的地方
      const ph = Math.PI * i / N, cs = Math.cos(ph), sn = Math.sin(ph);
      const e = eq10_2(cs, sn, m);
      curves.vm.push([cs * m.st / e.vm, sn * m.st / e.vm]);
      curves.tr.push([cs * m.st / e.tresca, sn * m.st / e.tresca]);
      curves.cm.push([cs * e.SFc, sn * e.SFc]);
      curves.rk.push([cs * e.SFr, sn * e.SFr]);
    }
    const sc = Math.max(m.sc, m.st) * 1.15;
    const pt = [[0, 0], [p.s, p.t]];
    const k = Math.min(s.r.SFv, s.r.SFt, s.r.SFc, s.r.SFr);
    const ray = [[0, 0], [p.s * Math.min(k, 1e6), p.t * Math.min(k, 1e6)]];
    api.plot(60, 20, w - 90, h - 70, [
      { pts: curves.vm, color: "#1f77b4" }, { pts: curves.tr, color: "#d62728" }, { pts: curves.cm, color: "#2ca02c" }, { pts: curves.rk, color: "#ff7f0e" },
      { pts: ray, color: "#888888" }, { pts: pt, color: "#000000" }],
      { xmin: -sc, xmax: m.st * 1.15, ymin: 0, ymax: m.st * 0.9, xlabel: api.T("σ / MPa", "σ / MPa"), ylabel: api.T("τ / MPa", "τ / MPa") });
  },
});
