// 实验 55.5 磨削温度与烧伤边界（配 55.5 节）。公式与 hub/surface.py 相同：
//   de = dw·ds/(dw + ds)（ds = 400 mm），lc = √(ap·de)，heq = vw·ap/vs，u = 14·heq^−0.35·[1 + 0.3(A − 0.5)]（A：磨粒磨平面积 %），
//   q = ε·u·vw·ap/lc（ε = 0.7），最高温度 θ = 20 + 2qα/(πk·vw)·max_X ∫_{X−L}^{X+L} e^(−u)K₀(|u|)du，L = vw·lc/(4α)（Jaeger 移动带状热源）；
//   回火软化温度按 Hollomon–Jaffe P = T(20 + lg t) 与原回火工艺相等求出（t = lc/vw）；θ ≥ Ac1 为二次淬火烧伤（干磨为退火烧伤），
//   软化温度 ≤ θ < Ac1 为回火烧伤。K₀ 用 Abramowitz–Stegun 9.8 的多项式近似。冷却只改变 θ ≥ Ac1 时的烧伤种类（ε 不变，与 hub/surface.py 相同）。
const MAT5 = {
  "45-QT": { name: ["45 钢（调质）", "45 steel (Q&T)"], k: 49.8, c: 486, rho: 7850, Ac1: 724, tc: 560, th: 2 },
  "20CrMnTi-CQ": { name: ["20CrMnTi（渗碳淬火、低温回火）", "20CrMnTi (case-hardened, low temper)"], k: 46.6, c: 477, rho: 7850, Ac1: 740, tc: 180, th: 2 },
};
const SC5 = { sh301: { mat: "45-QT", dw: 35 }, sh101: { mat: "20CrMnTi-CQ", dw: 25 } };
const DS5 = 400, EPS5 = 0.7;
function i0(x) { const t = x / 3.75, t2 = t * t; return 1 + t2 * (3.5156229 + t2 * (3.0899424 + t2 * (1.2067492 + t2 * (0.2659732 + t2 * (0.0360768 + t2 * 0.0045813))))); }
function k0e(x) {                // e^x·K₀(x)，x > 0
  if (x <= 2) { const y = x * x / 4; return Math.exp(x) * (-Math.log(x / 2) * i0(x) - 0.57721566 + y * (0.42278420 + y * (0.23069756 + y * (0.03488590 + y * (0.00262698 + y * (0.00010750 + y * 0.0000074)))))); }
  const y = 2 / x; return (1.25331414 + y * (-0.07832358 + y * (0.02189568 + y * (-0.01062446 + y * (0.00587872 + y * (-0.00251540 + y * 0.00053208)))))) / Math.sqrt(x);
}
// 累积积分 C(u) = ∫_{−U}^{u} e^(−s)K₀(|s|) ds，一次算好
const JU = 80, JH = 0.002, JN = Math.round(2 * JU / JH), JC = new Float64Array(JN + 1);
(function () {
  const f = (s) => { const a = Math.abs(s); return s < 0 ? k0e(a) : k0e(a) * Math.exp(-2 * a); };
  let prev = f(-JU);
  for (let i = 1; i <= JN; i++) { const s = -JU + i * JH, v = Math.abs(s) < JH / 2 ? f(JH / 4) : f(s); JC[i] = JC[i - 1] + (prev + v) / 2 * JH; prev = v; }
})();
function cumAt(u) { const t = (Math.min(Math.max(u, -JU), JU) + JU) / JH, i = Math.min(Math.floor(t), JN - 1), w = t - i; return JC[i] * (1 - w) + JC[i + 1] * w; }
function jShape(L, X) { return cumAt(X + L) - cumAt(X - L); }
function jPeak(L) {
  let best = -1, bx = 0;
  for (let i = 0; i <= 300; i++) { const X = -L + (2.5 * L + 1) * i / 300, v = jShape(L, X); if (v > best) { best = v; bx = X; } }
  const d = (2.5 * L + 1) / 300;
  for (let i = -20; i <= 20; i++) { const X = bx + d * i / 20, v = jShape(L, X); if (v > best) best = v; }
  return best;
}
function temp5(mat, vs, vwMin, apUm, de, A) {
  const vw = vwMin / 60, ap = apUm / 1000, lc = Math.sqrt(ap * de), heq = vw * ap / vs * 1000;
  const u = 14 * Math.pow(heq, -0.35) * (1 + 0.3 * (A - 0.5)), al = mat.k / (mat.rho * mat.c);
  const q = EPS5 * u * 1e9 * vw * ap * 1e-3 / (lc * 1e-3), L = vw * lc * 1e-3 / (4 * al);
  const rise = 2 * q * al / (Math.PI * mat.k * vw) * jPeak(L);
  return { theta: 20 + rise, lc, heq, u, q: q / 1e6, t: lc / (vw * 1000) * 1000, L, al };
}
function onset5(mat, tMs) { const P = (mat.tc + 273.15) * (20 + Math.log10(mat.th * 3600)); return P / (20 + Math.log10(tMs / 1000)) - 273.15; }
function burn5(mat, g, cool) {
  const on = onset5(mat, g.t);
  const kind = g.theta >= mat.Ac1 ? (cool ? "reh" : "ann") : g.theta >= on ? "tem" : "none";
  return { kind, on, margin: Math.min(on, mat.Ac1) - g.theta };
}
const BN5 = { none: ["不烧伤", "no burn"], tem: ["回火烧伤", "tempering burn"], reh: ["二次淬火烧伤", "re-hardening burn"], ann: ["退火烧伤", "annealing burn"] };
function maxAp5(mat, vs, vw, de, A) {
  const ok = (ap) => burn5(mat, temp5(mat, vs, vw, ap, de, A), true).kind === "none";
  let lo = 0.1, hi = 200;
  if (!ok(lo)) return 0;
  if (ok(hi)) return hi;
  for (let i = 0; i < 40; i++) { const m = Math.sqrt(lo * hi); if (ok(m)) lo = m; else hi = m; }
  return lo;
}
function eval5(api) {
  const p = api.p, sc = SC5[api.scene] || SC5.sh301, mat = MAT5[sc.mat], de = sc.dw * DS5 / (sc.dw + DS5);
  const g = temp5(mat, p.vs, p.vw, p.ap, de, p.A), b = burn5(mat, g, p.cool >= 0.5);
  const vws = [5, 7.5, 10, 15, 20, 25, 30, 35, 40], bd = vws.map((v) => [v, maxAp5(mat, p.vs, v, de, p.A)]);
  return { sc, mat, de, g, b, bd, apMax: maxAp5(mat, p.vs, p.vw, de, p.A), Q: p.vw / 60 * p.ap / 1000 * 1000 };   // Q′：mm³/(s·mm)
}
let BEST5 = null;                 // 刚修整的砂轮（A = 0.5）、SH-101：参数表上不烧伤的最大比磨除率（vs、vw、ap 都按滑块的步长）
function best5() {
  if (BEST5) return BEST5;
  const sc = SC5.sh101, mat = MAT5[sc.mat], de = sc.dw * DS5 / (sc.dw + DS5);
  let best = 0;
  for (let vs = 20; vs <= 60; vs += 5) for (let vw = 5; vw <= 40; vw += 1) {
    const ap = Math.floor(maxAp5(mat, vs, vw, de, 0.5) * 2 + 1e-9) / 2;
    best = Math.max(best, vw / 60 * ap);
  }
  return (BEST5 = best);
}
const near5 = (a, b) => Math.abs(a - b) < 1e-6;

WQ.lab({
  title: ["实验 55.5 磨削温度与烧伤边界", "Lab 55.5 Grinding temperature and the burn boundary"],
  goal: ["调砂轮速度、工件速度、切深、砂轮的锋利程度和冷却，看磨削区表面温度的分布、最高温度和是否烧伤；在工件速度—切深图上找烧伤边界，比较调质钢和渗碳淬火钢。",
         "Vary the wheel speed, work speed, infeed, wheel sharpness and coolant; see the surface temperature across the contact zone, its peak and whether the work burns; find the burn boundary on the work-speed–infeed chart and compare a Q&T steel with a case-hardened one."],
  scenes: [
    { id: "sh301", name: ["SH-301 轴承位（45 钢调质，Ø35）", "SH-301 bearing seat (45 Q&T, Ø35)"],
      params: { vs: { value: 35 }, vw: { value: 20 }, ap: { value: 10 }, A: { value: 0.5 }, cool: { value: 1 } },
      problem: { title: ["工程问题：工序 60 的粗磨、精磨会不会烧伤", "Engineering problem: will operation 60 burn the work"],
                 text: ["SH-301 工序 60 粗磨切深 0.01 mm、精磨 0.005 mm，砂轮 Ø400、35 m/s，工件 20 m/min。磨削区每一点只受热一毫秒多，温度却有几百摄氏度。调质钢要到多少度才烧伤？",
                        "Operation 60 roughs SH-301 at 0.01 mm and finishes at 0.005 mm per pass with a Ø400 wheel at 35 m/s and the work at 20 m/min. Each point is heated for about a millisecond, yet to several hundred degrees. How hot must a Q&T steel get before it burns?"] } },
    { id: "sh101", robot: true, name: ["SH-101 轴承位（20CrMnTi 渗碳淬火，Ø25）", "SH-101 bearing seat (20CrMnTi case-hardened, Ø25)"],
      params: { vs: { value: 35 }, vw: { value: 20 }, ap: { value: 5 }, A: { value: 0.5 }, cool: { value: 1 } },
      problem: { title: ["机器人问题：减速器齿轮轴为什么早期开裂", "Robot problem: why did the reducer gear shafts crack early"],
                 text: ["关节减速器的 SH-101 齿轮轴渗碳淬火、180 ℃ 低温回火。一批轴把精磨切深从 0.002 mm 加到 0.005 mm 以后，台架试验早期开裂（本章提要）。低温回火的钢三百多摄氏度就开始软化，精磨切深最大能取多少？",
                        "The SH-101 reducer shaft is case-hardened and tempered at 180 °C. After the finishing infeed was raised from 0.002 to 0.005 mm a batch cracked early on the test rig (chapter opener). A low-tempered steel softens above about 360 °C: how large may the finishing infeed be?"] } },
  ],
  params: [
    { id: "vs", name: ["砂轮速度 vs", "Wheel speed vs"], min: 20, max: 60, step: 5, value: 35, unit: "m/s", digits: 0 },
    { id: "vw", name: ["工件速度 vw", "Work speed vw"], min: 5, max: 40, step: 1, value: 20, unit: "m/min", digits: 0 },
    { id: "ap", name: ["切深 ap", "Infeed ap"], min: 0.5, max: 30, step: 0.5, value: 10, unit: "µm", digits: 1 },
    { id: "A", name: ["磨粒磨平面积（刚修整约 0.5）", "Wear flat area (freshly dressed ≈ 0.5)"], min: 0.5, max: 6, step: 0.5, value: 0.5, unit: "%", digits: 1 },
    { id: "cool", name: ["冷却液（0 干磨、1 湿磨）", "Coolant (0 dry, 1 wet)"], min: 0, max: 1, step: 1, value: 1, unit: "", digits: 0 },
  ],
  legend: [{ color: "var(--red)", name: ["表面温度", "surface temperature"] }, { color: "var(--accent)", name: ["烧伤边界", "burn boundary"] }],
  tasks: [
    { id: "sh301", text: ["SH-301 工序 60：粗磨（默认 10 µm）和精磨（改为 5 µm）的最高温度各多少？会不会烧伤？", "SH-301 operation 60: the peak temperature for roughing (default 10 µm) and finishing (set 5 µm)? Any burn?"],
      demo: { scene: "sh301", set: { vs: 35, vw: 20, ap: 5, A: 0.5, cool: 1 }, press: [], wait: 1 } },
    { id: "max101", text: ["SH-101（vw = 20 m/min、刚修整的砂轮）：精磨切深最大取多少不烧伤？", "SH-101 (vw = 20 m/min, freshly dressed): the largest finishing infeed without burn?"],
      demo: { scene: "sh101", set: { vs: 35, vw: 20, ap: 4.5, A: 0.5, cool: 1 }, press: [], wait: 1 } },
    { id: "dull", text: ["SH-101 砂轮变钝（磨平面积 4%），切深只有 2 µm：还烧伤吗？", "SH-101 with a dull wheel (4% wear flat) at only 2 µm: does it still burn?"],
      demo: { scene: "sh101", set: { vs: 35, vw: 20, ap: 2, A: 4, cool: 1 }, press: [], wait: 1 } },
    { id: "slow", text: ["SH-101：把工件速度降到 10 m/min，用比 vw = 20 时的最大切深更大的切深（如 5.5 µm）磨，还烧伤吗？为什么？", "SH-101: drop the work speed to 10 m/min and use a larger infeed than the vw = 20 limit (say 5.5 µm): does it burn? Why?"],
      demo: { scene: "sh101", set: { vs: 35, vw: 10, ap: 5.5, A: 0.5, cool: 1 }, press: [], wait: 1 } },
    { id: "fast", text: ["SH-101、刚修整的砂轮：找一组 vs、vw、ap，不烧伤而比磨除率 Q′ = vw·ap 尽量大（达到可能的最大值的 90% 以上）。", "SH-101, freshly dressed: find vs, vw, ap that do not burn with the removal rate Q′ = vw·ap as large as possible (at least 90% of the best)."],
      demo: { scene: "sh101", set: { vs: 20, vw: 40, ap: 5.5, A: 0.5, cool: 1 }, press: [], wait: 1 } },
  ],
  think: ["为什么调质钢的烧伤是二次淬火烧伤，而渗碳淬火、低温回火的钢先出现回火烧伤？降低工件速度为什么反而允许更大的切深？",
          "Why does a Q&T steel burn by re-hardening while a case-hardened, low-tempered steel first suffers tempering burn? Why does a lower work speed allow a larger infeed?"],

  reset(api, s) { s.key = ""; },
  update(dt, api, s) { api.stop(); },
  res(api, s) {
    const p = api.p, key = [api.scene, p.vs, p.vw, p.ap, p.A, p.cool].join("|");
    if (s.key !== key) { s.key = key; s.r = eval5(api); }
    return s.r;
  },
  readouts(api, s) {
    const p = api.p, r = this.res(api, s), T = api.T, std = near5(p.vs, 35) && near5(p.vw, 20) && near5(p.A, 0.5);
    if (api.scene === "sh301" && std && p.cool >= 0.5 && near5(p.ap, 5)) api.done("sh301");   // 粗磨 10 µm 是场景的默认值，读数里同时给出
    if (api.scene === "sh101" && std && r.b.kind === "none" && p.ap + 0.5 > r.apMax) api.done("max101");
    if (api.scene === "sh101" && p.A >= 4 - 1e-9 && near5(p.ap, 2) && r.b.kind !== "none") api.done("dull");
    if (api.scene === "sh101" && p.vw <= 10 && near5(p.A, 0.5) && p.ap > 4.69 && r.b.kind === "none") api.done("slow");
    if (api.scene === "sh101" && near5(p.A, 0.5) && r.b.kind === "none" && r.Q >= 0.9 * best5()) api.done("fast");
    const g = r.g, bn = BN5[r.b.kind];
    return [
      [["材料", "material"], T(...r.mat.name) + T(`；de = ${api.fmt(r.de, 1)} mm`, `; de = ${api.fmt(r.de, 1)} mm`)],
      [["接触弧长 lc / 受热时间", "contact length lc / heating time"], api.fmt(g.lc, 3) + " mm / " + api.fmt(g.t, 2) + " ms"],
      [["当量磨削厚度 heq / 比磨削能 u", "heq / specific energy u"], api.fmt(g.heq, 3) + " µm / " + api.fmt(g.u, 1) + " J/mm³"],
      [["热流密度 q / Peclet 数 L", "heat flux q / Peclet L"], api.fmt(g.q, 0) + " W/mm² / " + api.fmt(g.L, 2)],
      [["最高温度 θmax", "peak temperature θmax"], api.fmt(g.theta, 0) + " ℃" + (api.scene === "sh301" && near5(p.ap, 5) ? T(`（同样条件粗磨 10 µm：${api.fmt(temp5(r.mat, p.vs, p.vw, 10, r.de, p.A).theta, 0)} ℃）`, ` (roughing at 10 µm: ${api.fmt(temp5(r.mat, p.vs, p.vw, 10, r.de, p.A).theta, 0)} °C)`) : "")],
      [["回火软化温度 / Ac1", "softening onset / Ac1"], api.fmt(r.b.on, 0) + " ℃ / " + r.mat.Ac1 + " ℃"],
      [["判别", "verdict"], T(bn[0], bn[1]) + (r.b.kind === "none" ? T(`（还差 ${api.fmt(r.b.margin, 0)} ℃）`, ` (${api.fmt(r.b.margin, 0)} °C to spare)`) : "")],
      [["本组 vs、vw 下不烧伤的最大切深", "largest infeed without burn here"], api.fmt(r.apMax, 2) + " µm"],
      [["比磨除率 Q′ = vw·ap", "removal rate Q′ = vw·ap"], api.fmt(r.Q, 3) + " mm³/(s·mm)"],
    ];
  },
  draw(api, s) {
    const r = this.res(api, s), { w, h } = api, css = api.css, p = api.p, g = r.g;
    // 上：沿接触区的表面温度（Jaeger 曲线形状；横坐标以半接触长 l 为单位，工件向左移动、热源相对向右）
    const L = g.L, pk = jPeak(L), pts = [];
    for (let i = 0; i <= 200; i++) { const xi = -4 + 7 * i / 200, X = xi * L; pts.push([xi, 20 + (g.theta - 20) * jShape(L, X) / pk]); }
    const ymax = Math.max(g.theta, r.mat.Ac1) * 1.12;
    api.plot(w * 0.08, h * 0.06, w * 0.86, h * 0.38, [{ pts, color: css("--red") }],
             { xmin: -4, xmax: 3, ymin: 0, ymax, xlabel: api.T("位置 / 半接触长（−1 到 1 为接触区；工件向左移动）", "position / half contact length (contact −1 … 1; work moves left)"), ylabel: api.T("温度 / ℃", "temperature / °C") });
    const yT = (t) => h * 0.06 + h * 0.38 * (1 - t / ymax), xP = (x) => w * 0.08 + w * 0.86 * (x + 4) / 7;
    api.rect(xP(-1), h * 0.06, xP(1) - xP(-1), h * 0.38, "rgba(224,160,48,0.12)");
    [[r.mat.Ac1, "Ac1"], [r.b.on, api.T("回火软化", "softening")]].forEach(([t, n]) => { if (t < ymax) { api.line(w * 0.08, yT(t), w * 0.94, yT(t), css("--muted"), 1); api.label(n + " " + api.fmt(t, 0), w * 0.93, yT(t) - 4, css("--muted"), 12, "right"); } });
    // 下：烧伤边界（工件速度—切深），当前点
    const y0 = h * 0.58, hh = h * 0.32, apTop = Math.min(80, Math.max(20, p.ap * 1.2, ...r.bd.map(([, a]) => a * 1.15)));
    api.plot(w * 0.08, y0, w * 0.86, hh, [{ pts: r.bd.map(([v, a]) => [v, Math.min(a, apTop)]), color: css("--accent") }],
             { xmin: 0, xmax: 42, ymin: 0, ymax: apTop, xlabel: api.T("工件速度 vw / (m/min)", "work speed vw / (m/min)"), ylabel: api.T("切深 ap / µm", "infeed ap / µm") });
    const X = w * 0.08 + w * 0.86 * p.vw / 42, Y = y0 + hh * (1 - p.ap / apTop), bad = r.b.kind !== "none";
    api.circle(X, Y, 6, bad ? css("--red") : css("--green"));
    api.label(api.T(bad ? "烧伤" : "不烧伤", bad ? "burn" : "no burn"), X + 9, Y - 6, bad ? css("--red") : css("--green"), 12);
    api.label(api.T("边界以上烧伤", "burn above the line"), w * 0.9, y0 + 14, css("--muted"), 12, "right");
  },
});
