// 实验 57.2 工序尺寸与余量（配 57.2 节）。SH-101 的磨削外圆从最后一道往前推：半精车、粗车的尺寸怎么定，余量的最小值、最大值各是多少。
// 标准公差取 GB/T 1800.1-2020 表 1（与 textbook/mfgtech/std/it_grades.yaml 一致，程序 ex57_2 的同一张表）；
// 最小余量 2Z_min = 2(Rz + H_a) + 2ρ（两顶尖装夹 ε = 0），分量为企业工艺标准 WQ-PS-01 的教学示意值（code/_calc57.py）：
// 磨削前（半精车后渗碳淬火）Rz 0.0125、Hₐ 0.05、ρ 由滑块给（默认 0.10）；半精车前（粗车）Rz 0.05、Hₐ 0.05、ρ 0.30。
// 半精车的经济精度 IT8–IT10（std/route_methods.yaml）；渗碳件磨削余量最大不超过 0.5 mm（磨削工时、烧伤与硬化层）。
const IT57 = {
  "18-30": { 6: 13, 7: 21, 8: 33, 9: 52, 10: 84, 11: 130, 12: 210, 13: 330 },
};
const SHAFT57 = {
  bearing: { d: 25, es: 0.015, ei: 0.002, name: ["SH-101 轴承位 Ø25 k6", "SH-101 bearing seat Ø25 k6"] },
  seal: { d: 24, es: 0, ei: -0.033, name: ["SH-101 密封轴颈 Ø24 h8", "SH-101 seal journal Ø24 h8"] },
};
const GRIND57 = { rz: 0.0125, ha: 0.05 };
const TURN57 = { rz: 0.05, ha: 0.05, rho: 0.30 };
const ECON_SEMI57 = 8;                                    // 半精车经济精度 IT8–IT10：比 IT8 更高就超出
const ZMAX57 = 0.5;

function eval57(api) {
  const sh = SHAFT57[api.scene] || SHAFT57.bearing, p = api.p, it = IT57["18-30"];
  const T2 = it[Math.round(p.itf)] / 1000, T1 = it[Math.round(p.itr)] / 1000;
  const dmax = sh.d + sh.es, dmin = sh.d + sh.ei;
  const A2 = sh.d + p.a2, A1 = A2 + p.a1;
  const z3need = 2 * (GRIND57.rz + GRIND57.ha) + 2 * p.rho;
  const z2need = 2 * (TURN57.rz + TURN57.ha) + 2 * TURN57.rho;
  const z3min = (A2 - T2) - dmax, z3max = A2 - dmin;
  const z2min = (A1 - T1) - A2, z2max = A1 - (A2 - T2);
  const okG = z3min >= z3need - 1e-9, okT = z2min >= z2need - 1e-9, okMax = z3max <= ZMAX57 + 1e-9, okEcon = Math.round(p.itf) >= ECON_SEMI57;
  return { sh, T1, T2, dmax, dmin, A2, A1, z3need, z2need, z3min, z3max, z2min, z2max, okG, okT, okMax, okEcon,
    all: okG && okT && okMax && okEcon };
}

function check57(api, s) {
  const e = eval57(api);
  s.e = e;
  if (e.z3min < e.z3need) api.done("short");
  if (!e.okEcon) api.done("econ");
  if (api.scene === "bearing" && e.all && api.p.rho >= 0.15 - 1e-9) api.done("distort");
  if (api.scene === "bearing" && e.all && Math.abs(api.p.rho - 0.1) < 1e-9 && e.z3max <= 0.40 + 1e-9) api.done("best");
}

WQ.lab({
  title: ["实验 57.2 工序尺寸与余量", "Lab 57.2 Operation sizes and stock"],
  goal: ["从最后一道磨削往前推，定出 SH-101 半精车和粗车的工序尺寸与公差；看清渗碳淬火的变形怎样决定磨削余量，什么时候会“没东西可磨”，什么时候又白白多磨。",
         "Work back from grinding to fix SH-101's semi-finish and rough sizes; see how carburizing distortion sets the grinding stock, when there is nothing left to grind and when too much is ground."],
  scenes: [
    { id: "bearing", name: ["SH-101 轴承位", "SH-101 bearing seat"],
      problem: { title: ["工厂问题：渗碳件的轴承位留多少磨量？", "Factory problem: how much grinding stock on a carburized bearing seat?"],
                 text: ["轴承位 Ø25 k6、Ra 0.8，路线是粗车 → 半精车 → 滚齿、铣键槽 → 渗碳淬火 → 粗磨、精磨。半精车和粗车的尺寸各定多少，磨削和半精车才都“有余量可切、又不多切”？磨多了还会磨掉硬化层。",
                        "Ø25 k6, Ra 0.8; route: rough → semi → hob, keyway → carburize → grind. What semi and rough sizes leave each operation enough but not too much — grinding too much also removes the case?"] } },
    { id: "seal", robot: true, name: ["SH-101 密封轴颈", "SH-101 seal journal"],
      params: { a2: { value: 0.4 } },
      problem: { title: ["机器人问题：减速器油封靠它不漏油", "Robot problem: the reducer's oil seal runs here"],
                 text: ["机器人关节减速器的输入轴密封轴颈 Ø24 h8、Ra 0.8，油封唇口压在它上面。它的公差带在公称尺寸以下，推算时要用最大尺寸 24.000。",
                        "The seal journal Ø24 h8, Ra 0.8 carries the reducer's oil-seal lip; its zone lies below nominal, so work from 24.000."] } },
  ],
  params: [
    { id: "a2", name: ["半精车尺寸高出公称尺寸 A₂ − d", "Semi size above nominal A₂ − d"], min: 0.05, max: 0.8, step: 0.05, value: 0.4, unit: "mm", digits: 2 },
    { id: "itf", name: ["半精车公差等级 IT", "Semi-finishing grade IT"], min: 6, max: 11, step: 1, value: 9, digits: 0 },
    { id: "a1", name: ["粗车尺寸高出半精车 A₁ − A₂", "Rough size above semi A₁ − A₂"], min: 0.3, max: 3, step: 0.1, value: 1.1, unit: "mm", digits: 2 },
    { id: "itr", name: ["粗车公差等级 IT", "Rough grade IT"], min: 10, max: 13, step: 1, value: 12, digits: 0 },
    { id: "rho", name: ["渗碳淬火变形 ρ", "Carburizing distortion ρ"], min: 0, max: 0.3, step: 0.01, value: 0.1, unit: "mm", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["核算", "Check"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--amber)", name: ["粗车", "rough turning"] }, { color: "var(--accent)", name: ["半精车", "semi-finishing"] },
           { color: "var(--green)", name: ["磨削（图纸）", "grinding (drawing)"] }, { color: "var(--red)", name: ["余量不够", "not enough stock"] }],
  tasks: [
    { id: "short", text: ["把半精车尺寸定得太小，让磨削余量的最小值小于所需的最小余量，看图上哪里变红。", "Make the semi size too small so the minimum grinding stock is below the need; see what turns red."],
      demo: { scene: "bearing", set: { a2: 0.25, itf: 9, a1: 1.1, itr: 12, rho: 0.1 } } },
    { id: "econ", text: ["把半精车公差定到 IT7——读一读提示为什么不行（要做到 IT7 得换精车）。", "Set the semi grade to IT7 and read why it does not work (IT7 needs finish turning)."],
      demo: { scene: "bearing", set: { a2: 0.4, itf: 7, a1: 1.1, itr: 12, rho: 0.1 } } },
    { id: "distort", text: ["渗碳淬火变形 ρ 增大到 0.15 mm：重新定半精车、粗车的尺寸，使全部核算通过。", "Distortion ρ = 0.15 mm: choose new semi and rough sizes so every check passes."],
      demo: { scene: "bearing", set: { a2: 0.5, itf: 9, a1: 1.1, itr: 12, rho: 0.15 } } },
    { id: "best", text: ["ρ = 0.10 mm：调出一组全部核算通过、磨削余量最大值不超过 0.40 mm 的尺寸（与工艺规程比较）。", "ρ = 0.10: all checks pass with at most 0.40 mm grinding stock (compare with the plan)."],
      demo: { scene: "bearing", set: { a2: 0.4, itf: 9, a1: 1.1, itr: 12, rho: 0.1 } } },
  ],
  think: ["渗碳淬火的变形很分散。若一批零件里有 5% 变形超过 0.15 mm，按 0.10 定的磨削余量会出什么问题？除了加大余量，还能怎样处理？",
          "Carburizing distortion scatters. If 5% of a batch distort over 0.15 mm, what happens with stock set for 0.10? Besides more stock, what else can be done?"],

  reset(api, s) { check57(api, s); },
  update(dt, api, s) { check57(api, s); api.stop(); },
  readouts(api, s) {
    const e = s.e || eval57(api), f = api.fmt, ok = (b) => (b ? api.T("够", "ok") : api.T("不够", "too small"));
    return [
      [["图纸", "Drawing"], `${f(e.dmin, 3)}–${f(e.dmax, 3)} mm`],
      [["半精车 A₂", "Semi A₂"], `${f(e.A2 - e.T2, 3)}–${f(e.A2, 3)} mm（IT${Math.round(api.p.itf)}）`],
      [["粗车 A₁", "Rough A₁"], `${f(e.A1 - e.T1, 3)}–${f(e.A1, 3)} mm（IT${Math.round(api.p.itr)}）`],
      [["磨削余量（直径）最小 / 最大", "Grinding stock (dia.) min / max"], `${f(e.z3min, 3)} / ${f(e.z3max, 3)} mm`],
      [["磨削所需最小余量", "Grinding stock needed"], `${f(e.z3need, 3)} mm · ${ok(e.okG)}`],
      [["半精车余量（直径）最小 / 最大", "Semi stock (dia.) min / max"], `${f(e.z2min, 3)} / ${f(e.z2max, 3)} mm`],
      [["半精车所需最小余量", "Semi stock needed"], `${f(e.z2need, 3)} mm · ${ok(e.okT)}`],
      [["核算结论", "Result"], e.all ? api.T("全部通过", "all checks pass")
        : !e.okEcon ? api.T("半精车 IT7 超出经济精度 IT8–IT10：要做到 IT7 得换成精车", "IT7 is beyond semi-finishing's IT8–IT10")
          : !e.okMax ? api.T("磨削余量太大（>0.5 mm）", "too much grinding stock (>0.5 mm)") : api.T("有余量不够", "an allowance is too small")],
    ];
  },
  draw(api, s) {
    const e = s.e || eval57(api), { w, h } = api, css = api.css;
    const lo = e.sh.d - 0.15, hi = Math.max(e.A1 + 0.15, e.sh.d + 1.2);
    const X = (v) => 60 + (v - lo) / (hi - lo) * (w - 120);
    const rows = [
      { y: h * 0.25, a: e.A1 - e.T1, b: e.A1, c: css("--amber"), n: api.T("粗车 A₁", "rough A₁") },
      { y: h * 0.48, a: e.A2 - e.T2, b: e.A2, c: e.okEcon ? css("--accent") : css("--red"), n: api.T("半精车 A₂", "semi A₂") },
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
