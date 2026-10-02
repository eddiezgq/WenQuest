// 实验 50.6 工序尺寸与余量（配 50.6 节）。从最后一道工序往前推：精车尺寸、粗车尺寸怎么定，余量的最小值、最大值各是多少。
// 标准公差取 GB/T 1800.1-2020 表 1（与 textbook/mfgtech/std/it_grades.yaml 一致，程序 ex50_6 核对）；
// 最小余量 2Z_min = 2(Rz + H_a) + 2ρ（两顶尖装夹 ε = 0），分量为数字工厂企业工艺标准 WQ-PS-01 的教学示意值。
const IT50 = {
  "18-30": { 6: 13, 7: 21, 8: 33, 9: 52, 10: 84, 11: 130, 12: 210, 13: 330 },
  "30-50": { 6: 16, 7: 25, 8: 39, 9: 62, 10: 100, 11: 160, 12: 250, 13: 390 },
};
const SHAFT50 = {
  shaft: { d: 35, es: 0.018, ei: 0.002, range: "30-50", name: ["SH-301 轴承位 Ø35k6", "SH-301 bearing seat Ø35k6"] },
  joint: { d: 25, es: 0.015, ei: 0.002, range: "18-30", name: ["关节输出轴轴承位 Ø25k6", "joint output shaft bearing seat Ø25k6"] },
};
const GRIND50 = { rz: 0.0125, ha: 0.03, rho: 0.03 };   // 精车后铣键槽：上道留下的 Rz、缺陷层、空间偏差
const TURN50 = { rz: 0.05, ha: 0.15 };                  // 粗车后调质：Rz、氧化脱碳层（ρ 由滑块给）
const ECON_FINISH50 = 7;                                 // 精车经济精度 IT7–IT8：比 IT7 更高就超出

function eval50(api) {
  const sh = SHAFT50[api.scene] || SHAFT50.shaft, p = api.p, it = IT50[sh.range];
  const T2 = it[Math.round(p.itf)] / 1000, T1 = it[Math.round(p.itr)] / 1000;
  const dmax = sh.d + sh.es, dmin = sh.d + sh.ei;
  const A2 = sh.d + p.a2, A1 = A2 + p.a1;
  const z3need = 2 * (GRIND50.rz + GRIND50.ha) + 2 * GRIND50.rho;
  const z2need = 2 * (TURN50.rz + TURN50.ha) + 2 * p.rho;
  const z3min = (A2 - T2) - dmax, z3max = A2 - dmin;
  const z2min = (A1 - T1) - A2, z2max = A1 - (A2 - T2);
  const okG = z3min >= z3need - 1e-9, okT = z2min >= z2need - 1e-9, okMax = z3max <= 0.4 + 1e-9, okEcon = Math.round(p.itf) >= ECON_FINISH50;
  return { sh, T1, T2, dmax, dmin, A2, A1, z3need, z2need, z3min, z3max, z2min, z2max, okG, okT, okMax, okEcon,
    all: okG && okT && okMax && okEcon };
}

function check50(api, s) {
  const e = eval50(api);
  s.e = e;
  if (e.z3min < e.z3need) api.done("short");
  if (!e.okEcon) api.done("econ");
  if (api.scene === "shaft" && e.all && Math.round(api.p.itf) === 8) api.done("plan");
  if (api.scene === "joint" && e.all && api.p.rho >= 0.4 - 1e-9) api.done("robot");
}

WQ.lab({
  title: ["实验 50.6 工序尺寸与余量", "Lab 50.6 Operational dimensions and allowances"],
  goal: ["从最后一道工序往前推，定出精车和粗车的工序尺寸与公差；看清余量的最小值由什么决定，什么时候会“没东西可切”，什么时候又白白多切。",
         "Work back from the last operation to fix the finish- and rough-turning dimensions and tolerances; see what sets the minimum allowance, when an operation has nothing left to cut, and when it cuts too much."],
  scenes: [
    { id: "shaft", name: ["SH-301 输出轴", "SH-301 output shaft"],
      problem: { title: ["工厂问题：SH-301 的轴承位留多少磨量？", "Factory problem: how much grinding stock on the SH-301 bearing seat?"],
                 text: ["轴承位 Ø35k6、Ra 0.8，工艺路线是粗车 → 调质 → 精车 → 铣键槽 → 磨外圆。精车和粗车的尺寸各定多少，磨削和精车才都“有余量可切、又不多切”？",
                        "The bearing seat is Ø35k6, Ra 0.8; the route is rough turn → quench & temper → finish turn → keyway → grind. What finish- and rough-turning sizes leave every operation enough, but not too much, to cut?"] } },
    { id: "joint", robot: true, name: ["关节输出轴", "joint output shaft"],
      params: { rho: { min: 0, max: 0.6, step: 0.01, value: 0.4 } },
      problem: { title: ["机器人问题：关节输出轴调质后弯得更厉害", "Robot problem: the joint shaft bends more in heat treatment"],
                 text: ["协作机器人关节的输出轴轴承位 Ø25k6，细长、调质后弯曲可达 0.4 mm。弯曲越大，精车的余量要留多少？",
                        "The cobot joint's output shaft has a Ø25k6 bearing seat; it is slender and may bend 0.4 mm in quench and temper. With more bending, how much finish-turning stock is needed?"] } },
  ],
  params: [
    { id: "a2", name: ["精车尺寸高出图纸 A₂ − d", "Finish size above nominal A₂ − d"], min: 0.05, max: 0.8, step: 0.01, value: 0.3, unit: "mm", digits: 2 },
    { id: "itf", name: ["精车公差等级 IT", "Finish-turning grade IT"], min: 6, max: 11, step: 1, value: 8, digits: 0 },
    { id: "a1", name: ["粗车尺寸高出精车 A₁ − A₂", "Rough size above finish A₁ − A₂"], min: 0.3, max: 3, step: 0.05, value: 0.8, unit: "mm", digits: 2 },
    { id: "itr", name: ["粗车公差等级 IT", "Rough-turning grade IT"], min: 10, max: 13, step: 1, value: 12, digits: 0 },
    { id: "rho", name: ["调质弯曲 ρ", "Q&T bending ρ"], min: 0, max: 0.5, step: 0.01, value: 0.25, unit: "mm", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["核算", "Check"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--amber)", name: ["粗车", "rough turning"] }, { color: "var(--accent)", name: ["精车", "finish turning"] },
           { color: "var(--green)", name: ["磨削（图纸）", "grinding (drawing)"] }, { color: "var(--red)", name: ["余量不够", "not enough stock"] }],
  tasks: [
    { id: "short", text: ["把精车尺寸定得太小，让磨削余量的最小值小于所需的最小余量，看图上哪里变红。", "Make the finish size too small so the minimum grinding stock is below what is needed; see what turns red."],
      demo: { scene: "shaft", set: { a2: 0.1, itf: 8, a1: 1.2, itr: 12, rho: 0.25 } } },
    { id: "econ", text: ["把精车公差定到 IT6，想省掉磨削——读一读提示为什么不行。", "Set the finish-turning grade to IT6 to skip grinding, and read why it does not work."],
      demo: { scene: "shaft", set: { a2: 0.3, itf: 6, a1: 1.2, itr: 12, rho: 0.25 } } },
    { id: "plan", text: ["SH-301：精车取 IT8，调出一组尺寸，使磨削和精车的最小余量都够、磨削余量最大不超过 0.4 mm。",
                         "SH-301: with IT8 finish turning, find sizes so both minimum allowances are enough and the largest grinding stock is at most 0.4 mm."],
      demo: { scene: "shaft", set: { a2: 0.3, itf: 8, a1: 1.2, itr: 12, rho: 0.25 } } },
    { id: "robot", robot: true, text: ["关节输出轴：调质弯曲 ρ 取 0.40 mm，重新定粗车尺寸，使全部核算通过。", "Joint shaft: with ρ = 0.40 mm, choose a new rough size so every check passes."],
      demo: { scene: "joint", set: { a2: 0.25, itf: 8, a1: 1.5, itr: 12, rho: 0.4 } } },
  ],
  think: ["余量的最小值为什么要加上“上道工序的公差”？如果上道工序做得更准（公差更小），余量能不能少留？",
          "Why does the minimum allowance involve the previous operation's tolerance? If the previous operation were more accurate, could the allowance be smaller?"],

  reset(api, s) { check50(api, s); },
  update(dt, api, s) { check50(api, s); api.stop(); },
  readouts(api, s) {
    const e = s.e || eval50(api), f = api.fmt, ok = (b) => (b ? api.T("够", "ok") : api.T("不够", "too small"));
    return [
      [["图纸", "Drawing"], `${f(e.dmin, 3)}–${f(e.dmax, 3)} mm`],
      [["精车 A₂", "Finish A₂"], `${f(e.A2 - e.T2, 3)}–${f(e.A2, 3)} mm（IT${Math.round(api.p.itf)}）`],
      [["粗车 A₁", "Rough A₁"], `${f(e.A1 - e.T1, 3)}–${f(e.A1, 3)} mm（IT${Math.round(api.p.itr)}）`],
      [["磨削余量（直径）最小 / 最大", "Grinding stock (dia.) min / max"], `${f(e.z3min, 3)} / ${f(e.z3max, 3)} mm`],
      [["磨削所需最小余量", "Grinding stock needed"], `${f(e.z3need, 3)} mm · ${ok(e.okG)}`],
      [["精车余量（直径）最小 / 最大", "Finish stock (dia.) min / max"], `${f(e.z2min, 3)} / ${f(e.z2max, 3)} mm`],
      [["精车所需最小余量", "Finish stock needed"], `${f(e.z2need, 3)} mm · ${ok(e.okT)}`],
      [["核算结论", "Result"], e.all ? api.T("全部通过", "all checks pass")
        : !e.okEcon ? api.T("精车 IT6 超出经济精度 IT7–IT8：要靠磨削", "IT6 is beyond finish turning's IT7–IT8: grinding is needed")
          : !e.okMax ? api.T("磨削余量太大（>0.4 mm）", "too much grinding stock (>0.4 mm)") : api.T("有余量不够", "an allowance is too small")],
    ];
  },
  draw(api, s) {
    const e = s.e || eval50(api), { w, h } = api, css = api.css;
    const lo = e.sh.d - 0.15, hi = Math.max(e.A1 + 0.15, e.sh.d + 1.2);
    const X = (v) => 60 + (v - lo) / (hi - lo) * (w - 120);
    const rows = [
      { y: h * 0.25, a: e.A1 - e.T1, b: e.A1, c: css("--amber"), n: api.T("粗车 A₁", "rough A₁") },
      { y: h * 0.48, a: e.A2 - e.T2, b: e.A2, c: e.okEcon ? css("--accent") : css("--red"), n: api.T("精车 A₂", "finish A₂") },
      { y: h * 0.71, a: e.dmin, b: e.dmax, c: css("--green"), n: api.T("磨削", "grind") },
    ];
    api.label(api.P(e.sh.name), 12, 18, css("--muted"), 13);
    rows.forEach((r) => {
      api.rect(X(r.a), r.y - 12, Math.max(3, X(r.b) - X(r.a)), 24, r.c, null, 3);
      api.label(r.n, X(r.a) - 8, r.y, css("--ink"), 13, "right");
    });
    const gap = (r0, r1, ok, need) => {       // 余量的最小值：上道下限到本道上限
      const y = (r0.y + r1.y) / 2, x0 = X(r1.b), x1 = X(r0.a);
      api.line(x0, y, x1, y, ok ? css("--ink") : css("--red"), ok ? 1.5 : 3);
      api.label(api.T(`最小余量 ${api.fmt(r0.a - r1.b, 3)}（要 ≥ ${api.fmt(need, 3)}）`, `min stock ${api.fmt(r0.a - r1.b, 3)} (need ≥ ${api.fmt(need, 3)})`),
        Math.min(x0, x1) + 6, y - 11, ok ? css("--ink") : css("--red"), 12);
    };
    gap(rows[0], rows[1], e.okT, e.z2need);
    gap(rows[1], rows[2], e.okG, e.z3need);
    for (let v = Math.ceil(lo * 4) / 4; v <= hi; v += 0.25) {
      api.line(X(v), h * 0.86, X(v), h * 0.88, css("--muted"), 1);
      api.label(api.fmt(v, 2), X(v), h * 0.92, css("--muted"), 11, "center");
    }
    api.label(api.T("直径 / mm", "diameter / mm"), w - 60, h * 0.97, css("--muted"), 12, "right");
  },
});
