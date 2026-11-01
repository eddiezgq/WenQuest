// 实验 54.4 工艺系统受力变形与误差复映（配 54.4 节）。公式与 hub/accuracy.py 相同：
//   刀具在 x 处的让刀量 y(x) = Fp·[((L − x)/L)²/k头 + (x/L)²/k尾 + 1/k刀 + x²(L − x)²/(3EIL)]（用跟刀架时去掉工件一项），直径误差 2y；
//   形状判别：两端与中间的直径误差比较（锥度 = 右 − 左，中凸 = 中 − 两端平均；锥度占优为锥形，中凸 > 0 鼓形、< 0 鞍形）；
//   误差复映：ε = C/k，k 取刀具在工件中间时的系统刚度；三次走刀的 C（背向力随切深的变化率）按粗车、半精车、精车取 404、270、174 N/mm（算例 54.4.3）。
const E54 = 210000, KK54 = 50000, C54 = [404, 270, 174, 174];
function comp54(p, x) {
  const L = p.L, I = Math.PI * Math.pow(p.d, 4) / 64;
  const head = Math.pow((L - x) / L, 2) / (p.kh * 1000), tail = Math.pow(x / L, 2) / (p.kt * 1000), tool = 1 / KK54;
  const work = p.rest >= 0.5 ? 0 : x * x * Math.pow(L - x, 2) / (3 * E54 * I * L);
  return { head, tail, tool, work, total: head + tail + tool + work };
}
function eval54(p) {
  const n = 41, xs = [], dd = [];
  for (let i = 0; i < n; i++) { const x = p.L * i / (n - 1); xs.push(x); dd.push(2 * p.Fp * comp54(p, x).total); }
  const d1 = dd[0], d2 = dd[(n - 1) / 2], d3 = dd[n - 1];
  const taper = d3 - d1, crown = d2 - (d1 + d3) / 2;
  const shape = Math.abs(taper) >= 1.5 * Math.abs(crown) ? "taper" : crown > 0 ? "drum" : "saddle";
  const k = 1 / comp54(p, p.L / 2).total;
  const err = [p.e0]; let e = p.e0;
  for (let i = 0; i < p.n; i++) { e *= C54[Math.min(i, 3)] / k; err.push(e); }
  return { xs, dd, taper, crown, shape, range: Math.max(...dd) - Math.min(...dd), k, err };
}
const SH54 = { taper: ["锥形", "taper"], drum: ["鼓形（中间大）", "barrel"], saddle: ["鞍形（两头大）", "saddle"] };

WQ.lab({
  title: ["实验 54.4 受力变形与误差复映", "Lab 54.4 Deflection and error reflection"],
  goal: ["两顶尖车外圆，调头架、尾座的刚度和工件的直径、长度、背向力，看刀具走过全长时让刀量怎样变化、车出什么形状；再看毛坯误差经几次走刀能降到多少。",
         "Turning between centres: vary the head and tail stiffness, the work's diameter and length and the radial force; see how the deflection changes along the cut and what shape results, then how many passes it takes to shrink the blank's error."],
  scenes: [
    { id: "sh301", name: ["SH-301 精车 Ø40 × 167", "SH-301 finishing Ø40 × 167"],
      params: { d: { value: 40 }, L: { value: 167 }, Fp: { value: 52 } },
      problem: { title: ["工程问题：工件、头架、尾座谁更软", "Engineering problem: which is softer — the work or the centres"],
                 text: ["工序 40 精车 SH-301，背向力只有约 50 N，可是 k6 的公差也只有 16 µm（磨前留量要均匀）。车出的形状取决于工件、头架、尾座、刀架各自的刚度，哪一项最软，形状就由它决定。",
                        "Finish-turning SH-301 in operation 40 the radial force is only about 50 N, yet the grinding allowance must be even. The shape depends on the stiffness of the work, headstock, tailstock and tool post; the softest one decides it."] } },
    { id: "slender", name: ["细长轴 Ø20 × 500", "Slender shaft Ø20 × 500"],
      params: { d: { value: 20 }, L: { value: 500 }, Fp: { value: 111 } },
      problem: { title: ["工程问题：细长轴为什么车成腰鼓", "Engineering problem: why a slender shaft comes out barrel-shaped"],
                 text: ["长径比 25 的轴，工件本身的弯曲远大于机床的变形。机器人的长连杆轴、丝杠都会遇到这个问题。", "With a length-to-diameter ratio of 25 the work bends far more than the machine. Long robot shafts and lead screws meet this problem."] } },
  ],
  params: [
    { id: "kh", name: ["头架刚度", "Headstock stiffness"], min: 2, max: 100, step: 1, value: 20, unit: "kN/mm", digits: 0 },
    { id: "kt", name: ["尾座刚度", "Tailstock stiffness"], min: 2, max: 100, step: 1, value: 20, unit: "kN/mm", digits: 0 },
    { id: "d", name: ["工件直径", "Work diameter"], min: 10, max: 80, step: 1, value: 40, unit: "mm", digits: 0 },
    { id: "L", name: ["两顶尖距离", "Length between centres"], min: 100, max: 800, step: 1, value: 167, unit: "mm", digits: 0 },
    { id: "Fp", name: ["背向力", "Radial force"], min: 20, max: 400, step: 1, value: 52, unit: "N", digits: 0 },
    { id: "rest", name: ["跟刀架（0 不用、1 用）", "Follow rest (0 no, 1 yes)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "e0", name: ["毛坯直径上的跳动", "Blank runout on the diameter"], min: 0.1, max: 2, step: 0.05, value: 1, unit: "mm", digits: 2 },
    { id: "n", name: ["走刀次数", "Number of passes"], min: 1, max: 4, step: 1, value: 1, unit: "", digits: 0 },
  ],
  legend: [{ color: "var(--red)", name: ["直径误差 2y", "diameter error 2y"] }, { color: "var(--accent)", name: ["每次走刀后的误差", "error after each pass"] }],
  tasks: [
    { id: "saddle", text: ["SH-301 精车（默认参数）：车出什么形状？两端与中间的直径误差各多少？", "SH-301 finishing (defaults): what shape, and the diameter errors at the ends and the middle?"],
      demo: { scene: "sh301", set: { kh: 20, kt: 20, rest: 0 }, press: [], wait: 1 } },
    { id: "taper", text: ["把尾座刚度降到头架的 1/4（5 kN/mm）：形状变成什么？哪端大？", "Drop the tailstock to a quarter of the headstock (5 kN/mm): what shape, which end is larger?"],
      demo: { scene: "sh301", set: { kh: 20, kt: 5, rest: 0 }, press: [], wait: 1 } },
    { id: "drum", text: ["细长轴：中间的直径误差有多大？", "Slender shaft: how large is the diameter error in the middle?"],
      demo: { scene: "slender", set: { kh: 20, kt: 20, rest: 0 }, press: [], wait: 1 } },
    { id: "rest", text: ["细长轴加跟刀架：直径误差降到多少？", "Slender shaft with a follow rest: what is the diameter error now?"],
      demo: { scene: "slender", set: { kh: 20, kt: 20, rest: 1 }, press: [], wait: 1 } },
    { id: "passes", text: ["SH-301：毛坯跳动 1 mm，至少几次走刀才能降到 0.01 mm 以下？", "SH-301: from 1 mm of blank runout, how many passes bring it below 0.01 mm?"],
      demo: { scene: "sh301", set: { kh: 20, kt: 20, rest: 0, e0: 1, n: 2 }, press: [], wait: 1 } },
  ],
  think: ["头架、尾座刚度相同时，SH-301 为什么是鞍形而不是圆柱？刀具在头架端时让刀量里有没有尾座的贡献？", "With equal head and tail stiffness, why is SH-301 saddle-shaped rather than cylindrical? Does the tailstock contribute when the tool is at the headstock end?"],

  reset(api, s) { s.r = eval54(api.p); },
  update(dt, api, s) { s.r = eval54(api.p); api.stop(); },
  readouts(api, s) {
    const p = api.p, r = s.r || eval54(p), f = (v) => api.fmt(v * 1000, 1) + " µm", T = api.T, sh = SH54[r.shape];
    if (api.scene === "sh301" && p.kh === 20 && p.kt === 20 && r.shape === "saddle") api.done("saddle");
    if (api.scene === "sh301" && p.kt * 4 <= p.kh + 1e-9 && r.shape === "taper" && r.taper > 0) api.done("taper");
    if (api.scene === "slender" && p.rest < 0.5 && r.shape === "drum") api.done("drum");
    if (api.scene === "slender" && p.rest >= 0.5 && r.range < 0.02) api.done("rest");
    const last = r.err[r.err.length - 1], prev = r.err[r.err.length - 2];
    if (api.scene === "sh301" && p.e0 >= 1 - 1e-9 && last < 0.01 && prev >= 0.01) api.done("passes");
    return [
      [["形状", "shape"], T(sh[0], sh[1])],
      [["直径误差：头架端 / 中间 / 尾座端", "diameter error: head / middle / tail"], f(r.dd[0]) + " / " + f(r.dd[20]) + " / " + f(r.dd[40])],
      [["锥度（尾 − 头） / 中凸", "taper / crown"], f(r.taper) + " / " + f(r.crown)],
      [["系统刚度（刀在中间）", "system stiffness (tool in the middle)"], api.fmt(r.k, 0) + " N/mm"],
      [["每次走刀的复映系数 ε", "reflection coefficient per pass"], r.err.slice(1).map((e, i) => api.fmt(C54[Math.min(i, 3)] / r.k, 4)).join(", ")],
      [["走刀后的跳动", "runout after the passes"], r.err.slice(1).map((e) => api.fmt(e * 1000, 2) + " µm").join(" → ")],
    ];
  },
  draw(api, s) {
    const r = s.r || eval54(api.p), { w, h } = api, css = api.css, p = api.p;
    const ymax = Math.max(...r.dd) * 1.15 * 1000;
    api.plot(w * 0.08, h * 0.08, w * 0.86, h * 0.42, [{ pts: r.xs.map((x, i) => [x, r.dd[i] * 1000]), color: css("--red") }],
             { xmin: 0, xmax: p.L, ymin: 0, ymax: Math.max(ymax, 1), xlabel: api.T("刀具位置 x / mm（左头架、右尾座）", "tool position x / mm"), ylabel: api.T("直径误差 / µm", "diameter error / µm") });
    // 下：误差复映（对数柱）
    const y0 = h * 0.62, hh = h * 0.3, n = r.err.length, bw = w * 0.6 / n, lg = (v) => Math.log10(Math.max(v * 1000, 1e-3));
    api.label(api.T("毛坯误差经走刀复映（对数坐标，µm）", "blank error reflected pass by pass (log, µm)"), w * 0.08, y0 - 10, css("--muted"), 12);
    r.err.forEach((e, i) => {
      const t = (lg(e) + 3) / 7, x = w * 0.12 + i * bw * 1.3;
      api.rect(x, y0 + hh * (1 - t), bw, hh * t, i ? css("--accent") : css("--muted"));
      api.label(api.fmt(e * 1000, e * 1000 >= 10 ? 0 : 3), x + bw / 2, y0 + hh * (1 - t) - 6, css("--ink"), 12, "center");
      api.label(i ? api.T(`第 ${i} 次`, `pass ${i}`) : api.T("毛坯", "blank"), x + bw / 2, y0 + hh + 14, css("--ink"), 12, "center");
    });
    const tl = (lg(0.01) + 3) / 7;
    api.line(w * 0.1, y0 + hh * (1 - tl), w * 0.9, y0 + hh * (1 - tl), css("--red"), 1);
    api.label("10 µm", w * 0.9, y0 + hh * (1 - tl) - 4, css("--red"), 12, "right");
  },
});
