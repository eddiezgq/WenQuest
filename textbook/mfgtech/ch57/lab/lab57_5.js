// 实验 57.5 切削用量的选择与校核（配 57.5 节）。公式与程序 57.5.1（ex57_5.py）相同：
//   残留面积 Ra ≈ 0.0321·f²/r·1000（µm，第 55 章 hub/surface.ra_theory）；
//   Kienzle：Fc = kc1.1·b·h^(1−mc)，b = ap/sin κr，h = f·sin κr（κr = 93°），Fp ≈ 0.4·Fc，Pc = Fc·vc/60 000（kc1.1 = 2220、mc = 0.14，按 C45E）；
//   两顶尖让刀：柔度 = ((L−x)/L)²/k头 + (x/L)²/k尾 + 1/k刀 + x²(L−x)²/(3EIL)，直径误差 2·Fp·柔度（第 54 章 hub/accuracy.py）；
//   刀具寿命：vc·T^0.25·f^0.35 = C，C = 150·20^0.25·0.15^0.35（vc 150、f 0.15 时 20 min，示意）；
//   机动时间 tb = L·π·d/(1000·vc·f)（走刀长度 19 mm、直径 26.5，即工序 30 右轴承位那一刀）。
const KC = 2220, MC = 0.14, KR = 93 * Math.PI / 180, PR = 0.4;
const L5 = 136, X5 = 127.5, KH = 20000, KT = 20000, KK = 50000, E5 = 210000;
const CT = 150 * Math.pow(20, 0.25) * Math.pow(0.15, 0.35);
const TOL5 = 0.05, PMAX = 11 * 0.8;
function ra5(f, r) { return 0.0321 * f * f / r * 1000; }
function force5(ap, f) { const s = Math.sin(KR), Fc = KC * (ap / s) * Math.pow(f * s, 1 - MC); return { Fc, Fp: PR * Fc }; }
function comp5(x, d) { const I = Math.PI * Math.pow(d, 4) / 64; return Math.pow((L5 - x) / L5, 2) / KH + Math.pow(x / L5, 2) / KT + 1 / KK + x * x * Math.pow(L5 - x, 2) / (3 * E5 * I * L5); }
function life5(vc, f) { return Math.pow(CT / (vc * Math.pow(f, 0.35)), 4); }
function eval5(api) {
  const p = api.p, rough = api.scene === "rough";
  const d = rough ? 60 : 26.5, Lw = rough ? 84 : 19;
  const F = force5(p.ap, p.f), P = F.Fc * p.vc / 60000;
  const dd = 2 * F.Fp * comp5(X5, 25.4);
  const ra = ra5(p.f, p.r), T = life5(p.vc, p.f), tb = Lw * Math.PI * d / (1000 * p.vc * p.f);
  const raMax = rough ? 12.5 : p.ramax;
  const ok = { ra: ra <= raMax + 1e-9, dd: rough || dd <= TOL5 / 3 + 1e-12, life: T >= 15 - 1e-9, power: P <= PMAX + 1e-9 };
  return { F, P, dd, ra, T, tb, raMax, ok, all: ok.ra && ok.dd && ok.life && ok.power };
}

WQ.lab({
  title: ["实验 57.5 切削用量的选择与校核", "Lab 57.5 Choosing and checking cutting data"],
  goal: ["调进给量、切削速度、背吃刀量和刀尖圆弧，看粗糙度、让刀、刀具寿命、功率和机动时间怎样变化；在 f–vc 平面上找出可行域和机动时间最短的点。",
         "Vary feed, speed, depth and nose radius; watch roughness, deflection, tool life, power and machining time; find the feasible region and the fastest point in the f–vc plane."],
  scenes: [
    { id: "semi", name: ["工序 30 半精车轴承位", "Op 30 semi-finishing the bearing seat"],
      params: { ap: { value: 0.55 }, f: { value: 0.15 }, vc: { value: 150 }, r: { value: 0.4 }, ramax: { value: 3.2 } },
      problem: { title: ["工程问题：半精车的用量怎样定", "Engineering problem: semi-finishing data"],
                 text: ["SH-101 两顶尖装夹，半精车轴承位 Ø26.5 → Ø25.4（公差 0.05，Ra 3.2），一刀切完。f 和 vc 取多大，既满足粗糙度和精度、刀具寿命不少于 15 min，机动时间又最短？",
                        "SH-101 between centres, Ø26.5 → Ø25.4 (0.05, Ra 3.2) in one pass. Which f and vc meet Ra and accuracy with at least 15 min tool life, in the shortest time?"] } },
    { id: "rough", robot: true, hide: ["ramax"], name: ["工序 20 粗车（Ø60 棒料）", "Op 20 roughing the Ø60 bar"],
      params: { ap: { value: 2.5 }, f: { value: 0.3 }, vc: { value: 120 }, r: { value: 0.8 } },
      problem: { title: ["机器人问题：减速器输入轴扩产，粗车想少走几刀", "Robot problem: fewer roughing passes for the reducer shaft"],
                 text: ["WQR-105 扩产，粗车 Ø60 棒料想少走几刀：背吃刀量加大到多少，数控车床 CNC-L01（11 kW × 0.8）的功率还够？",
                        "With WQR-105 ramping up, how deep can each roughing pass go before the 11 kW × 0.8 lathe runs out of power?"] } },
  ],
  params: [
    { id: "ap", name: ["背吃刀量 ap", "Depth of cut ap"], min: 0.2, max: 8, step: 0.05, value: 0.55, unit: "mm", digits: 2 },
    { id: "f", name: ["进给量 f", "Feed f"], min: 0.05, max: 0.5, step: 0.01, value: 0.15, unit: "mm/r", digits: 2 },
    { id: "vc", name: ["切削速度 vc", "Cutting speed vc"], min: 60, max: 260, step: 5, value: 150, unit: "m/min", digits: 0 },
    { id: "r", name: ["刀尖圆弧半径 r", "Nose radius r"], min: 0.2, max: 1.2, step: 0.2, value: 0.4, unit: "mm", digits: 1 },
    { id: "ramax", name: ["要求的 Ra", "Required Ra"], min: 0.8, max: 6.3, step: 0.1, value: 3.2, unit: "µm", digits: 1 },
  ],
  legend: [{ color: "var(--warm)", name: ["Ra 限制", "Ra limit"] }, { color: "var(--accent)", name: ["让刀限制", "deflection limit"] }, { color: "var(--red)", name: ["刀具寿命 15 min", "tool life 15 min"] }, { color: "var(--green)", name: ["可行域", "feasible"] }],
  tasks: [
    { id: "fast", text: ["半精车：在可行域里找一个比工艺规程（0.070 min）更快、机动时间不超过 0.065 min 的点（vc·f 越大越快）。", "Semi: find a feasible point with machining time ≤ 0.065 min."],
      demo: { scene: "semi", set: { ap: 0.55, f: 0.18, vc: 145, r: 0.4, ramax: 3.2 }, press: [], wait: 1 } },
    { id: "ra16", text: ["把 Ra 要求改为 1.6（半精车后不磨），f 最大取多少？满足后让系统确认可行。", "Set Ra to 1.6 (no grinding after): how large can f be? Make it feasible."],
      demo: { scene: "semi", set: { ap: 0.55, f: 0.14, vc: 150, r: 0.4, ramax: 1.6 }, press: [], wait: 1 } },
    { id: "power", text: ["粗车：背吃刀量加到 6 mm（f 0.3、vc 120），功率还够吗？", "Rough: ap 6 mm (f 0.3, vc 120) — is there enough power?"],
      demo: { scene: "rough", set: { ap: 6, f: 0.3, vc: 120, r: 0.8 }, press: [], wait: 1 } },
    { id: "nose", text: ["半精车换刀尖圆弧 0.8 的刀片，Ra 1.6 时 f 可以加大到 0.19：让系统确认可行。", "Semi with r = 0.8: at Ra 1.6, f = 0.19 is feasible — confirm it."],
      demo: { scene: "semi", set: { ap: 0.55, f: 0.19, vc: 140, r: 0.8, ramax: 1.6 }, press: [], wait: 1 } },
  ],
  think: ["可行域的边界由公式算出，公式本身有多大误差？实际选用量时，为什么要离边界留些余地？", "How accurate are the formulas behind the boundaries? Why stay clear of the edges?"],

  reset(api, s) {},
  update(dt, api, s) { api.stop(); },
  readouts(api) {
    const p = api.p, e = eval5(api), T = api.T, f = api.fmt, sc = api.scene;
    if (sc === "semi" && e.all && e.tb <= 0.065 + 1e-9) api.done("fast");
    if (sc === "semi" && e.all && Math.abs(p.ramax - 1.6) < 1e-9 && Math.abs(p.r - 0.4) < 1e-9) api.done("ra16");
    if (sc === "rough" && p.ap >= 6 - 1e-9 && Math.abs(p.f - 0.3) < 1e-9 && Math.abs(p.vc - 120) < 1e-9) api.done("power");
    if (sc === "semi" && e.all && Math.abs(p.r - 0.8) < 1e-9 && Math.abs(p.ramax - 1.6) < 1e-9 && p.f >= 0.19 - 1e-9) api.done("nose");
    const yn = (b) => (b ? T("满足", "OK") : T("不满足", "fails"));
    return [
      [["理论 Ra", "theoretical Ra"], f(e.ra, 2) + " µm（≤ " + f(e.raMax, 1) + "）" + yn(e.ok.ra)],
      [["主切削力 / 背向力", "Fc / Fp"], f(e.F.Fc, 0) + " / " + f(e.F.Fp, 0) + " N"],
      [["切削功率（可用 8.8 kW）", "power (8.8 kW available)"], f(e.P, 2) + " kW " + yn(e.ok.power)],
      [["让刀引起的直径误差（≤ 公差的 1/3）", "deflection error (≤ tol/3)"], sc === "rough" ? T("粗车不核算", "not checked for roughing") : f(e.dd * 1000, 1) + " µm " + yn(e.ok.dd)],
      [["刀具寿命（≥ 15 min）", "tool life (≥ 15 min)"], f(e.T, 1) + " min " + yn(e.ok.life)],
      [["这一刀的机动时间", "machining time of the pass"], f(e.tb, 3) + " min"],
      [["结论", "result"], e.all ? T("可行", "feasible") : T("不可行", "not feasible")],
    ];
  },
  draw(api) {
    const { w, h } = api, css = api.css, p = api.p, sc = api.scene;
    const P = api.plot(w * 0.1, h * 0.06, w * 0.85, h * 0.8, [], { xmin: 0.05, xmax: 0.5, ymin: 60, ymax: 260, xlabel: api.T("进给量 f / (mm/r)", "feed f / (mm/r)"), ylabel: api.T("切削速度 vc / (m/min)", "vc / (m/min)") });
    const raMax = sc === "rough" ? 12.5 : p.ramax;
    const fRa = Math.sqrt(raMax / 1000 * p.r / 0.0321);
    let fDd = 0.5;
    if (sc !== "rough") { for (let f = 0.05; f <= 0.5; f += 0.001) { if (2 * force5(p.ap, f).Fp * comp5(X5, 25.4) > TOL5 / 3) { fDd = f; break; } } }
    let fPw = 0.5;
    for (let f = 0.05; f <= 0.5; f += 0.002) { if (force5(p.ap, f).Fc * 260 / 60000 > PMAX) { fPw = f; break; } }
    const vLife = (f) => CT / (Math.pow(f, 0.35) * Math.pow(15, 0.25));
    for (let f = 0.05; f <= 0.5; f += 0.005) {
      const vtop = Math.min(260, vLife(f));
      if (f <= Math.min(fRa, fDd) && vtop > 60) api.rect(P.X(f), P.Y(vtop), Math.max(1, P.X(f + 0.005) - P.X(f)), P.Y(60) - P.Y(vtop), "rgba(47,143,91,0.18)", null);
    }
    if (fRa < 0.5) { api.line(P.X(fRa), P.Y(60), P.X(fRa), P.Y(260), css("--warm"), 2); }
    if (sc !== "rough" && fDd < 0.5) api.line(P.X(fDd), P.Y(60), P.X(fDd), P.Y(260), css("--accent"), 2, [6, 4]);
    let prev = null;
    for (let f = 0.05; f <= 0.5; f += 0.01) { const pt = [P.X(f), P.Y(Math.min(260, vLife(f)))]; if (prev) api.line(prev[0], prev[1], pt[0], pt[1], css("--red"), 2); prev = pt; }
    api.circle(P.X(p.f), P.Y(p.vc), 6, eval5(api).all ? css("--green") : css("--red"));
    api.label(api.T("当前用量", "current"), P.X(p.f) + 8, P.Y(p.vc) - 8, css("--ink"), 12);
  },
});
