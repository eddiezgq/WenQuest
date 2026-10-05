// 实验 4.3 长线与中继器（配 4.3 节）。长 L 的导线分成 k 段，每段前放一个尺寸为 size（参考反相器的倍数）的中继器，
// 最后一段驱动 20 个参考反相器的负载。每段延时按式 (4.2.4)，总延时为各段之和（与书中程序 4.3.1 同一模型）。
// 右图记录本线长、本金属层下试过的段数与延时；读数给出闭式解的最优段数与尺寸，以及整数网格上的最小延时。
const P43 = M4_3.P, Q43 = P43.problems.p43;
const C0_43 = M4_3.cin(P43.Wmin, P43.kn / P43.kp * P43.Wmin), CL43 = Q43.load_units * C0_43;
const LAY43 = { m1: ["met1", 0.14], m3: ["met3", 0.3] };
const tried43 = { key: null, pts: {} };
const t43 = (scene, L, k, size) => M4_3.repeaterDelay(L, LAY43[scene][0], LAY43[scene][1], k, size, CL43);
const best43 = {};
function grid43(scene, L) {
  const key = scene + L;
  if (!best43[key]) {
    let b = { t: Infinity };
    for (let k = 1; k <= 12; k++) for (let s = 1; s <= 80; s++) { const t = t43(scene, L, k, s); if (t < b.t) b = { t, k, s }; }
    best43[key] = b;
  }
  return best43[key];
}

WQ.lab({
  title: ["实验 4.3 长线与中继器", "Lab 4.3 Long wires and repeaters"],
  goal: ["把横跨芯片的时钟线分成几段、每段前加一个中继器：找出最快的段数和中继器尺寸，与闭式解比较；看线长加倍时延时怎样变，厚金属上还要不要中继器。",
         "Split a cross-chip clock wire into segments with a repeater before each: find the fastest number of segments and repeater size and compare with the closed form; see how the delay grows when the wire doubles, and whether thick metal still needs repeaters."],
  scenes: [
    { id: "m1", robot: true, name: ["met1 最小线宽", "met1, minimum width"], hide: [],
      problem: { title: ["机器人问题：横跨芯片的时钟线", "Robot problem: a cross-chip clock wire"],
                 text: ["时钟缓冲器到对角的编码器计数器约 3 mm，只能走 met1。一个 20 倍反相器直接驱动要 400 多 ps。分几段、中继器多大最快？",
                        "The clock buffer is about 3 mm from the encoder counter and the wire must use met1. A 20× inverter driving it directly takes over 400 ps. How many segments and how large repeaters are fastest?"] } },
    { id: "m3", name: ["met3 最小线宽", "met3, minimum width"], hide: [],
      problem: { title: ["换到厚金属", "On thick metal"],
                 text: ["同一条线如果能走 met3，电阻小得多。中继器还有用吗？",
                        "If the same wire can use met3, its resistance is far lower. Do repeaters still help?"] } },
  ],
  params: [
    { id: "L", name: ["线长", "Wire length"], min: 1000, max: 6000, step: 500, value: 3000, unit: "μm", digits: 0 },
    { id: "k", name: ["段数 k（中继器个数）", "Segments k (repeaters)"], min: 1, max: 12, step: 1, value: 1, unit: "", digits: 0 },
    { id: "size", name: ["中继器尺寸（参考反相器的倍数）", "Repeater size (× reference inverter)"], min: 1, max: 80, step: 1, value: 20, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "best", robot: true, text: ["met1，3 mm：调段数和尺寸，使总延时不超过网格最小值的 1.02 倍。", "met1, 3 mm: tune segments and size to within 2 % of the grid minimum."],
      demo: { scene: "m1", set: { L: 3000, k: 3, size: 26 }, press: [], wait: 1 } },
    { id: "double", text: ["met1，线长加到 6 mm，再调到最优（1.02 倍以内）。与 3 mm 比，最优延时变成几倍？", "met1 at 6 mm: tune to within 2 % again. How does the optimal delay compare with 3 mm?"],
      demo: { scene: "m1", set: { L: 6000, k: 7, size: 26 }, press: [], wait: 1 } },
    { id: "thick", text: ["met3，3 mm，中继器 20 倍：找出最快的段数。", "met3, 3 mm, 20× repeaters: find the fastest number of segments."],
      demo: { scene: "m3", set: { L: 3000, size: 20, k: 1 }, press: [], wait: 1 } },
  ],
  think: ["实验里第一个中继器“免费”——它的输入电容要由前一级逻辑驱动，这一份没有计入。如果计入，最优尺寸会怎样变？为什么中继后的延时与线长成正比，而不再与线长的平方成正比？",
          "In this lab the first repeater comes for free: the logic before it must drive its input, which is not counted. If it were, how would the optimal size change? Why does the repeated wire's delay grow linearly with length instead of quadratically?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["试过的段数", "segments tried"], color: "#1d6fb8" }],
  reset(api, s) { check43(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, [lay, w] = LAY43[api.scene], t = t43(api.scene, p.L, p.k, p.size), opt = M4_3.repeaterOpt(p.L, lay, w), b = grid43(api.scene, p.L);
    return [[["总延时", "Total delay"], f(t * 1e12, 1) + " ps"],
            [["每段长度", "Segment length"], f(p.L / p.k, 0) + " μm"],
            [["闭式解：段数 / 尺寸", "Closed form: k / size"], f(opt.k, 2) + " / " + f(opt.size, 1)],
            [["网格最小：延时（k，尺寸）", "Grid minimum: delay (k, size)"], f(b.t * 1e12, 1) + " ps（" + b.k + "，" + b.s + "）"],
            [["每毫米延时", "Delay per mm"], f(t * 1e12 / (p.L / 1000), 1) + " ps/mm"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mu = css("--muted"), blue = "#1d6fb8", amber = "#e67e22";
    const p = api.p;
    // top: the wire with repeaters
    const y = h * 0.16, x0 = w * 0.05, x1 = w * 0.9, sz = Math.max(5, Math.min(18, 3 * Math.sqrt(p.size)));
    api.line(x0, y, x1, y, api.scene === "m1" ? blue : "#2e7d32", 3);
    for (let i = 0; i < p.k; i++) {
      const x = x0 + (x1 - x0) * i / p.k;
      api.line(x, y - sz, x, y + sz, ink, 2); api.line(x, y - sz, x + sz * 1.4, y, ink, 2); api.line(x, y + sz, x + sz * 1.4, y, ink, 2);
    }
    api.rect(x1, y - 10, 10, 20, amber); api.label(api.fmt(p.L / 1000, 1) + " mm", (x0 + x1) / 2, y + sz + 14, mu, 11, "center");
    // bottom: delays tried at this length/layer
    const key = api.scene + p.L + "_" + p.size;
    if (tried43.key !== key) { tried43.key = key; tried43.pts = {}; }
    tried43.pts[p.k] = t43(api.scene, p.L, p.k, p.size) * 1e12;
    const px = w * 0.1, py = h * 0.36, pw = w * 0.84, ph = h * 0.5;
    const ks = Object.keys(tried43.pts).map(Number), ymax = Math.max(200, ...ks.map((k) => tried43.pts[k])) * 1.15;
    const b = grid43(api.scene, p.L);
    const ax = api.plot(px, py, pw, ph, [{ pts: [[0.5, b.t * 1e12], [12.5, b.t * 1e12]], color: "#2e7d32" }], { xmin: 0.5, xmax: 12.5, ymin: 0, ymax, xlabel: "k", ylabel: "ps" });
    for (let k = 1; k <= 12; k++) api.label(String(k), ax.X(k), py + ph + 10, mu, 10, "center");
    ks.forEach((k) => { const v = tried43.pts[k], yy = ax.Y(v); api.rect(ax.X(k) - 7, yy, 14, py + ph - yy, k === p.k ? blue : "rgba(29,111,184,0.4)"); api.label(api.fmt(v, 0), ax.X(k), yy - 9, ink, 10, "center"); });
    api.label(api.T("网格最小", "grid min"), px + pw - 4, ax.Y(b.t * 1e12) - 9, "#2e7d32", 10, "right");
  },
});

function check43(api) {
  const p = api.p, t = t43(api.scene, p.L, p.k, p.size);
  if (api.scene === "m1" && p.L === 3000 && t <= 1.02 * grid43("m1", 3000).t) api.done("best");
  if (api.scene === "m1" && p.L === 6000 && t <= 1.02 * grid43("m1", 6000).t) api.done("double");
  if (api.scene === "m3" && p.L === 3000 && p.size === 20) {
    let bk = 1; for (let k = 2; k <= 12; k++) if (t43("m3", 3000, k, 20) < t43("m3", 3000, bk, 20)) bk = k;
    if (p.k === bk) api.done("thick");
  }
}
