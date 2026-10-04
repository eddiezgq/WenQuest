// 实验 2.6 产品族选型（配 2.6 节）。WQR-105 两级中心距不变、换齿数组合得到 16 种传动比；按输入功率、转速、工况系数核对
// 输出转矩、轴承寿命和输出轴平键——算式与数字工厂参数配置器（factory/digital/hub/configurator.py）相同。
const ST1_2_6 = [[24, 72], [21, 75], [27, 69], [32, 64]], ST2_2_6 = [[20, 70], [18, 72], [23, 67], [25, 65]];
const RATIOS2_6 = ST1_2_6.flatMap(([a, b]) => ST2_2_6.map(([c, d]) => ({ z: [a, b, c, d], i: Math.round(b / a * d / c * 100) / 100 }))).sort((x, y) => x.i - y.i);
const N1_2_6 = [750, 1000, 1450, 2900];
const ETA2_6 = 0.97 * 0.97 * 0.99 ** 3, T_RATED2_6 = 350, BRG_C2_6 = 25.5e3, M2_2_6 = 3, KEY2_6 = { b: 12, h: 8, l: 45, d: 40, s: 135 };
function calc2_6(api) {
  const p = api.p, r = RATIOS2_6[Math.round(p.ratio) - 1], n1 = N1_2_6[Math.round(p.n1)];
  const iz = r.z[1] / r.z[0] * r.z[3] / r.z[2];            // 与配置器相同：用齿数比，不用圆整后的 i
  const n2 = n1 / iz, t2 = 9550 * p.P / n2 * ETA2_6, t2k = t2 * p.KA;
  const ft = 2000 * t2k / (M2_2_6 * r.z[3]), fr = ft * Math.tan(20 * Math.PI / 180), load = Math.hypot(ft, fr) / 2;
  const L10 = (BRG_C2_6 / load) ** 3 * 1e6 / (60 * n2);
  const sig = 4000 * t2k / (KEY2_6.d * KEY2_6.h * (KEY2_6.l - KEY2_6.b));
  const uT = t2k / T_RATED2_6, uK = sig / KEY2_6.s, uL = p.life / L10;
  // 与配置器相同：转矩或平键超限是错误（不可用）；轴承寿命不足、输入 2900 r/min 只是警告
  return { r, n1, n2, t2k, L10, sig, uT, uK, uL, ok: uT <= 1 && uK <= 1, warn: uL > 1 || n1 === 2900 };
}
WQ.lab({
  title: ["实验 2.6 产品族选型", "Lab 2.6 Choosing from a product family"],
  goal: ["WQR-105 是一个参数化产品族：外形和中心距不变，换齿数得到 16 种传动比。按客户的功率、转速和工况，从产品族里选出合适的型号，看是哪一条约束先“卡住”。",
         "WQR-105 is a parametric family: same housing and centre distances, 16 ratios from different tooth counts. Pick the right variant for a customer's power, speed and duty, and see which constraint binds first."],
  scenes: [
    { id: "robot", robot: true, name: ["码垛工位输送线", "Palletising-cell conveyor"],
      problem: { title: ["工程问题：给机器人码垛工位的输送线选减速器", "Engineering problem: a gearbox for the conveyor of a robot palletising cell"],
                 text: ["码垛机器人旁边的辊道输送线，驱动辊需要约 100 r/min，电机 3 kW、4 极（1450 r/min），中等冲击（KA = 1.25），轴承寿命 10 000 h。产品族里哪一种传动比能用？",
                        "The roller conveyor beside a palletising robot needs about 100 r/min at the drive roller; motor 3 kW, 4-pole (1450 r/min), moderate shock (KA = 1.25), bearing life 10 000 h. Which ratio of the family will do?"] } },
    { id: "life", name: ["车库门开门机", "Garage-door opener"],
      params: { P: { min: 0.37, max: 3, step: 0.01, value: 0.75 }, KA: { min: 1, max: 2, step: 0.05, value: 2 } },
      problem: { title: ["生活中的例子：车库卷帘门", "Everyday example: a roller garage door"],
                 text: ["卷帘门的电机功率不大，但起停频繁、偶尔卡住，工况系数要取大些。看看工况系数怎样改变可选的范围。",
                        "A roller door motor is small, but it starts and stops often and sometimes jams, so the application factor is high. See how that changes the choice."] } },
  ],
  params: [
    { id: "ratio", name: ["传动比序号（1 = 最小，16 = 最大）", "Ratio number (1 = smallest, 16 = largest)"], min: 1, max: 16, step: 1, value: 13, unit: "", digits: 0 },
    { id: "P", name: ["输入功率 P", "Input power P"], min: 0.37, max: 11, step: 0.01, value: 4, unit: "kW", digits: 2 },
    { id: "n1", name: ["输入转速（0 = 750，1 = 1000，2 = 1450，3 = 2900 r/min）", "Input speed (0 = 750, 1 = 1000, 2 = 1450, 3 = 2900 r/min)"], min: 0, max: 3, step: 1, value: 2, unit: "", digits: 0 },
    { id: "KA", name: ["工况系数 KA", "Application factor KA"], min: 1, max: 2, step: 0.05, value: 1.25, unit: "", digits: 2 },
    { id: "life", name: ["要求的轴承寿命", "Required bearing life"], min: 2000, max: 50000, step: 1000, value: 10000, unit: "h", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["核对", "Check"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "var(--blue)", name: ["利用率（≤ 1 可用）", "utilisation (≤ 1 is OK)"] }],
  tasks: [
    { id: "std", robot: true, text: ["标准型（i = 10.5）、4 kW、1450 r/min、KA = 1.25 核对一次，记下输出转矩、轴承寿命、键的挤压应力和三项利用率。",
                                     "Check the standard variant (i = 10.5) at 4 kW, 1450 r/min, KA = 1.25; record output torque, bearing life, key stress and the three utilisations."],
      demo: { scene: "robot", set: { ratio: 13, P: 4, n1: 2, KA: 1.25, life: 10000 }, press: ["start"], wait: 1 } },
    { id: "pick", robot: true, text: ["输送线：3 kW、要求输出约 100 r/min（± 10%），找出能用的传动比。", "Conveyor: 3 kW, output about 100 r/min (± 10%); find the ratio that works."],
      demo: { scene: "robot", set: { ratio: 16, P: 3, n1: 2, KA: 1.25, life: 10000 }, press: ["start"], wait: 1 } },
    { id: "life", text: ["车库门经常卡住，KA = 2.0。用最大的传动比（14.29），最大能配多大功率的电机？", "The garage door often jams: KA = 2.0. With the largest ratio (14.29), how big a motor can it take?"],
      demo: { scene: "life", set: { ratio: 16, P: 2.0, n1: 2, KA: 2, life: 10000 }, press: ["start"], wait: 1 } },
  ],
  think: ["为什么整个产品族都是“额定转矩”先卡住，而轴承寿命在这里几乎不会不够？要让大传动比的型号传更大的功率，该改哪个零件？",
          "Why does the rated torque always bind first, while bearing life is hardly ever short here? To let the high-ratio variants carry more power, which part would you change?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    const r = calc2_6(api), p = api.p;
    s.r = r;
    if (api.scene === "robot" && Math.round(p.ratio) === 13 && Math.abs(p.P - 4) < 0.005 && Math.round(p.n1) === 2 && Math.abs(p.KA - 1.25) < 0.01) api.done("std");
    if (api.scene === "robot" && p.P >= 3 && Math.round(p.n1) === 2 && p.KA >= 1.25 && p.life >= 10000 && Math.abs(r.n2 - 100) <= 10 && r.ok) api.done("pick");
    if (api.scene === "life" && p.P >= 1.95 && p.KA >= 1.95 && Math.round(p.ratio) === 16 && r.ok) api.done("life");
    api.stop();
  },
  readouts(api, s) {
    const r = calc2_6(api), f = api.fmt;
    return [
      [["传动比 i（齿数）", "Ratio i (teeth)"], f(r.r.i, 2) + "（" + r.r.z[1] + "/" + r.r.z[0] + " × " + r.r.z[3] + "/" + r.r.z[2] + "）"],
      [["输出转速", "Output speed"], f(r.n2, 1) + " r/min"],
      [["输出转矩 × KA", "Output torque × KA"], f(r.t2k, 0) + " / 350 N·m"],
      [["轴承 6207 寿命 L10h", "Bearing 6207 life L10h"], f(r.L10, 0) + " h"],
      [["平键挤压应力", "Key bearing stress"], f(r.sig, 0) + " / 135 MPa"],
      [["结论", "Verdict"], !r.ok ? api.T("不可用", "not OK") : r.warn ? api.T("可用（有警告：寿命或高转速）", "OK with a warning (life or high speed)") : api.T("可用", "OK")],
    ];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, r = calc2_6(api);
    const bars = [[api.T("转矩", "torque"), r.uT], [api.T("平键", "key"), r.uK], [api.T("轴承寿命", "bearing life"), r.uL]];
    const x0 = w * 0.1, bw = w * 0.18, base = h * 0.85, top = h * 0.12, ymax = 2;
    api.line(x0 - 10, base, x0 + 3 * bw * 1.4, base, css("--ink"), 1);
    const y1 = base - (base - top) / ymax;
    api.line(x0 - 10, y1, x0 + 3 * bw * 1.4, y1, css("--red"), 1, [5, 4]);
    api.label(api.T("利用率 = 1", "utilisation = 1"), x0 + 3 * bw * 1.4, y1 - 6, css("--red"), 12, "right");
    bars.forEach(([name, u], k) => {
      const x = x0 + k * bw * 1.4, hh = Math.min(u, ymax) / ymax * (base - top);
      api.rect(x, base - hh, bw, hh, u <= 1 ? css("--blue") : css("--red"), css("--ink"), 0);
      api.label(name, x + bw / 2, base + 18, css("--ink"), 13, "center");
      api.label(api.fmt(u, 2), x + bw / 2, base - hh - 6, css("--ink"), 12, "center");
    });
  },
});
