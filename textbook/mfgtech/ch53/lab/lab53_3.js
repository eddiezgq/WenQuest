// 实验 53.3 尺寸链求解器（配 53.2、53.3、53.6、53.8 节）：极值法、概率法、蒙特卡罗三种算法对比。
// 每个场景是一条有三个组成环的尺寸链：A0 = Σ sense·Ai；参数是三个组成环的公差 T（中间偏差固定，取自数字工厂的工艺规程和尺寸链数据），
// 以及组成环的分布（0 正态、1 均匀、2 偏态）。程序 ex53_3、ex53_6 用 hub/tolerance.py 算出同样的结果。
const SC53 = {
  keyway: { req: [-0.2, 0], unit: "mm", base: 35,
    links: [{ name: ["槽底尺寸 H", "slot-bottom H"], s: 1, mid: -0.115 }, { name: ["精车半径 r1", "turned radius r1"], s: -1, mid: -0.00975 },
            { name: ["磨削半径 r2", "ground radius r2"], s: 1, mid: 0.005 }] },
  axial60: { req: [-0.3, 0.3], unit: "mm", base: 60,
    links: [{ name: ["精车左轴肩 52", "left shoulder 52"], s: -1, mid: 0 }, { name: ["总长 167", "overall 167"], s: 1, mid: 0 },
            { name: ["精车右轴肩 55", "right shoulder 55"], s: -1, mid: 0 }] },
  carb: { req: [-0.2, 0.2], unit: "mm", base: 1.0,
    links: [{ name: ["渗碳层深 t1", "case depth t1"], s: 1, mid: -0.01675 }, { name: ["渗碳前半径 r1", "radius before r1"], s: -1, mid: -0.0125 },
            { name: ["磨后半径 r2", "ground radius r2"], s: 1, mid: 0.00425 }] },
};
const KE53 = [[1.0, 0.0], [1.73, 0.0], [1.17, 0.26]];   // 正态、均匀、偏态（偏向上限）的 k、e

function gamma53(r, a) {                // Marsaglia–Tsang 法抽 Gamma(a, 1)，a ≥ 1
  const d = a - 1 / 3, c = 1 / Math.sqrt(9 * d);
  for (;;) {
    let x, v;
    do { const u1 = r() || 1e-12, u2 = r(); x = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2); v = 1 + c * x; } while (v <= 0);
    v = v * v * v; const u = r();
    if (Math.log(u || 1e-12) < 0.5 * x * x + d - d * v + d * Math.log(v)) return d * v;
  }
}
function beta53(r, a, b) { const x = gamma53(r, a), y = gamma53(r, b); return x / (x + y); }

function rng53(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

function eval53(api) {
  const p = api.p, sc = SC53[api.scene], T = [p.ta, p.tb, p.tc], d = Math.round(p.dist);
  let es = 0, ei = 0, mid = 0, var2 = 0;
  sc.links.forEach((l, i) => {
    const hi = l.mid + T[i] / 2, lo = l.mid - T[i] / 2;
    es += l.s > 0 ? hi : -lo; ei += l.s > 0 ? lo : -hi;
    const [k, e] = KE53[d];
    mid += l.s * (l.mid + e * T[i] / 2); var2 += (k * T[i]) ** 2;
  });
  const st = Math.sqrt(var2), ses = mid + st / 2, sei = mid - st / 2;
  // 蒙特卡罗：20000 件
  const r = rng53(7), n = 20000, vals = new Float64Array(n);
  let out = 0;
  for (let j = 0; j < n; j++) {
    let s = 0;
    sc.links.forEach((l, i) => {
      let u;
      if (d === 1) u = r();
      else if (d === 2) u = beta53(r, 3.23, 1.90);   // 偏向上限：beta(3.23, 1.90)，k ≈ 1.17、e ≈ +0.26，与表 53.3.1 和 hub/tolerance.py 一致
      else { do { let g = 0; for (let q = 0; q < 12; q++) g += r(); u = (g - 6) / 6 + 0.5; } while (u < 0 || u > 1); }       // 正态 ±3σ 截尾
      s += l.s * (l.mid - T[i] / 2 + u * T[i]);
    });
    vals[j] = s;
    if (s < sc.req[0] - 1e-12 || s > sc.req[1] + 1e-12) out++;
  }
  const ok = (a, b) => a >= sc.req[0] - 1e-9 && b <= sc.req[1] + 1e-9;
  return { sc, es, ei, ses, sei, vals, frac: out / n, extOK: ok(ei, es), statOK: ok(sei, ses), d };
}

function check53(api, s) {
  const e = eval53(api), p = api.p;
  s.e = e;
  if (api.scene === "keyway" && e.extOK && p.ta >= 0.17 - 1e-9) api.done("keyway");
  if (api.scene === "axial60" && !e.extOK && e.statOK && e.d === 0) api.done("axial");
  if (api.scene === "axial60" && e.d === 1) api.done("dist");
  if (api.scene === "carb" && e.extOK && p.ta >= 0.36 - 1e-9) api.done("carb");
}

WQ.lab({
  title: ["实验 53.3 尺寸链求解器", "Lab 53.3 Dimension-chain solver"],
  goal: ["同一条尺寸链，用极值法、概率法和蒙特卡罗模拟算出的封闭环往往不同。调组成环的公差和分布，看三种算法的结果和一批零件的实际分散，理解什么时候必须用极值法、什么时候可以用概率法。",
         "The same chain gives different closing tolerances by worst case, statistical method and Monte Carlo. Change the link tolerances and distributions, compare the three results with the scatter of a batch, and see when worst case is required and when the statistical method will do."],
  scenes: [
    { id: "keyway", name: ["SH-301 键槽深度 d − t₁", "SH-301 keyway depth d − t₁"], params: { ta: { value: 0.12 }, tb: { value: 0.0195 }, tc: { value: 0.008 }, dist: { value: 0 } },
      problem: { title: ["铣键槽的工序尺寸 H 能给多大公差？", "How much tolerance can the slot-bottom dimension H have?"],
                 text: ["键槽深 d − t₁ = 35（0/−0.2）不是直接铣出来的：先按精车外圆铣到 H，再磨外圆。H 的公差越大越好铣，可它和精车、磨削的公差一起决定 d − t₁。", "The keyway depth d − t₁ = 35 (0/−0.2) is not milled directly: the slot is milled to H from the turned OD, then the OD is ground. A wider H tolerance is easier to mill, but H, turning and grinding together decide d − t₁."] } },
    { id: "axial60", name: ["SH-301 齿轮位长度 60", "SH-301 gear-seat length 60"], params: { ta: { value: 0.1 }, tb: { value: 0.6 }, tc: { value: 0.1 }, dist: { value: 0 } },
      problem: { title: ["总长控制 ±0.3，齿轮位长度保得住吗？", "With overall length held to ±0.3, is the gear-seat length safe?"],
                 text: ["齿轮位长度 60 ± 0.3 由工序 40 的左轴肩 52、总长 167、右轴肩 55 三个工序尺寸间接保证。极值法说不行，概率法呢？一批零件里实际超差多少？", "The gear-seat length 60 ± 0.3 results from three operation-40 dimensions: left shoulder 52, overall 167, right shoulder 55. Worst case says no; what does the statistical method say, and how many parts really fail?"] } },
    { id: "carb", name: ["SH-101 渗碳层深度", "SH-101 case depth"], params: { ta: { value: 0.3 }, tb: { value: 0.025 }, tc: { value: 0.0065 }, dist: { value: 0 } },
      problem: { title: ["渗碳炉要保证多深的层？", "What case depth must the furnace give?"],
                 text: ["SH-101 轴承位磨后渗碳层深要 1.0 ± 0.2 mm。渗碳以后还要磨掉一层，热处理车间能控制的层深公差有限。层深的公差最多能放到多少？", "SH-101's bearing seat needs a case depth of 1.0 ± 0.2 mm after grinding. Grinding removes a layer after carburizing, and the heat-treatment shop can only hold the depth so closely. How wide can the depth tolerance be?"] } },
  ],
  params: [
    { id: "ta", name: ["组成环 1 的公差", "Tolerance of link 1"], min: 0.005, max: 0.8, step: 0.0005, value: 0.17, unit: "mm", digits: 4 },
    { id: "tb", name: ["组成环 2 的公差", "Tolerance of link 2"], min: 0.002, max: 0.8, step: 0.0005, value: 0.0195, unit: "mm", digits: 4 },
    { id: "tc", name: ["组成环 3 的公差", "Tolerance of link 3"], min: 0.002, max: 0.4, step: 0.0005, value: 0.008, unit: "mm", digits: 4 },
    { id: "dist", name: ["分布（0 正态、1 均匀、2 偏态）", "Distribution (0 normal, 1 uniform, 2 skewed)"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--accent)", name: ["蒙特卡罗：一批零件的封闭环", "Monte Carlo: closing link of a batch"] }, { color: "var(--red)", name: ["极值法界限", "worst-case limits"] }],
  tasks: [
    { id: "keyway", text: ["键槽：把 H 的公差加到 0.17 mm 以上，仍保证极值法满足要求。", "Keyway: widen H's tolerance to 0.17 mm or more while worst case still holds."],
      demo: { scene: "keyway", set: { ta: 0.17, tb: 0.0195, tc: 0.008, dist: 0 } } },
    { id: "axial", text: ["齿轮位：找一个总长公差，使极值法不满足、概率法满足，读出蒙特卡罗的超差率。", "Gear seat: find an overall-length tolerance where worst case fails but the statistical method holds; read the Monte Carlo reject rate."],
      demo: { scene: "axial60", set: { ta: 0.1, tb: 0.5, tc: 0.1, dist: 0 } } },
    { id: "dist", text: ["齿轮位：把分布改为均匀分布（例如操作工只求“在公差内”就停手），看超差率怎样变化。", "Gear seat: switch to uniform distributions (as when operators stop anywhere inside the tolerance) and see the reject rate."],
      demo: { scene: "axial60", set: { ta: 0.1, tb: 0.5, tc: 0.1, dist: 1 } } },
    { id: "carb", text: ["渗碳：把层深公差放到 0.36 mm 以上，仍保证磨后层深 1.0 ± 0.2。", "Case depth: widen the depth tolerance to 0.36 mm or more and still keep 1.0 ± 0.2 after grinding."],
      demo: { scene: "carb", set: { ta: 0.365, tb: 0.025, tc: 0.0065, dist: 0 } } },
  ],
  think: ["概率法算出的公差比极值法小，代价是什么？在什么生产条件下才能放心用概率法？", "The statistical method gives a smaller closing tolerance. What is the price, and under what production conditions can it be trusted?"],

  reset(api, s) { check53(api, s); },
  update(dt, api, s) { check53(api, s); api.stop(); },
  readouts(api, s) {
    const e = s.e || eval53(api), f = api.fmt, T = api.T, sc = e.sc;
    const yn = (b) => (b ? T("满足", "holds") : T("不满足", "fails"));
    return [
      [["要求", "Requirement"], `${sc.base}（${f(sc.req[1], 3)}/${f(sc.req[0], 3)}）`],
      [["极值法", "Worst case"], `${f(e.es, 4)} / ${f(e.ei, 4)} · ${yn(e.extOK)}`],
      [["概率法", "Statistical"], `${f(e.ses, 4)} / ${f(e.sei, 4)} · ${yn(e.statOK)}`],
      [["蒙特卡罗超差率", "Monte Carlo reject rate"], `${f(e.frac * 100, 2)} %`]];
  },
  draw(api, s) {
    const e = s.e || eval53(api), { w, h } = api, css = api.css, sc = e.sc;
    const lo = Math.min(e.ei, sc.req[0]) * 1.15, hi = Math.max(e.es, sc.req[1]) * 1.15 + 1e-9, span = hi - lo || 1;
    const X = (v) => w * 0.06 + (w * 0.88) * (v - lo) / span, nb = 60, bins = new Array(nb).fill(0);
    for (const v of e.vals) { const k = Math.floor((v - lo) / span * nb); if (k >= 0 && k < nb) bins[k]++; }
    const m = Math.max(...bins), y0 = h * 0.85;
    bins.forEach((b, k) => api.rect(X(lo + k * span / nb), y0 - (h * 0.6) * b / m, (w * 0.88) / nb - 1, (h * 0.6) * b / m, css("--accent"), null));
    api.line(X(e.ei), h * 0.15, X(e.ei), y0, css("--red"), 2, [6, 4]); api.line(X(e.es), h * 0.15, X(e.es), y0, css("--red"), 2, [6, 4]);
    api.line(X(sc.req[0]), h * 0.1, X(sc.req[0]), y0, css("--ink"), 2); api.line(X(sc.req[1]), h * 0.1, X(sc.req[1]), y0, css("--ink"), 2);
    api.label(api.T("黑线：要求；红虚线：极值法", "black: requirement; red dashed: worst case"), w * 0.06, h * 0.06, css("--muted"), 12);
  },
});
