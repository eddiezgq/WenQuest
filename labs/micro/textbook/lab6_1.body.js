// 实验 6.1 加法器结构比较（配 6.1、6.2 节）。五种加法器按 SKY130 sky130_fd_sc_hd 综合的延时与面积取自 params.json 的 arith_syn
// （calib/arith.py：Yosys + ABC，tt、25 °C、1.8 V，“尽量快”地综合；正文算例 6.1.2 另用“按预算综合”的结果，面积会小一些）；时间预算 = 时钟周期 − 第 3 章触发器的 tcq − tsu（M6_1.ffTiming）。
const P61 = M6_1.P, S61 = P61.arith_syn, FF61 = M6_1.ffTiming();
const KIND61 = ["rca", "cla", "csel", "bk", "ks"], W61 = [8, 16, 32];
const NAME61 = [["行波进位", "ripple carry"], ["超前进位（4 位一组）", "carry lookahead (4-bit)"], ["进位选择（4 位一组）", "carry select (4-bit)"],
                ["Brent–Kung", "Brent–Kung"], ["Kogge–Stone", "Kogge–Stone"]];
const COL61 = ["#c0392b", "#e67e22", "#7a8691", "#2e7d32", "#1d6fb8"];
const syn61 = (k, w) => S61["add_" + KIND61[k] + "_" + w];
const budget61 = (f) => 1e12 / (f * 1e6) - (FF61.tcq + FF61.tsu) * 1e12;
function best61(w, f) {
  let b = -1;
  for (let k = 0; k < 5; k++) { const s = syn61(k, w); if (s.delay <= budget61(f) && (b < 0 || s.area < syn61(b, w).area)) b = k; }
  return b;
}

WQ.lab({
  title: ["实验 6.1 加法器结构比较", "Lab 6.1 Comparing adder structures"],
  goal: ["电机速度控制器的累加器：给定位宽和时钟频率，从五种加法器中找出满足时间预算、面积最小的结构；看位宽、频率变化时选择怎样变。",
         "The motor speed controller's accumulator: for a given width and clock, find the smallest adder among five structures that meets the timing budget; see how the choice moves with width and frequency."],
  scenes: [
    { id: "acc", robot: true, name: ["速度积分累加器", "Speed-integrating accumulator"], hide: [],
      problem: { title: ["机器人问题：高速版本的累加器", "Robot problem: the accumulator of the fast version"],
                 text: ["时钟提高后，留给加法器的时间是周期减去触发器的 tcq 和 tsu。哪种加法器既赶得上又最小？",
                        "At a higher clock the adder gets the period minus the flip-flop's tcq and tsu. Which adder meets it and is smallest?"] } },
  ],
  params: [
    { id: "w", name: ["位宽（1 = 8 位，2 = 16 位，3 = 32 位）", "Width (1 = 8, 2 = 16, 3 = 32 bits)"], min: 1, max: 3, step: 1, value: 3, unit: "", digits: 0 },
    { id: "f", name: ["时钟频率", "Clock frequency"], min: 100, max: 1500, step: 10, value: 400, unit: "MHz", digits: 0 },
    { id: "k", name: ["结构（1 行波 2 超前 3 选择 4 BK 5 KS）", "Structure (1 RCA 2 CLA 3 CSEL 4 BK 5 KS)"], min: 1, max: 5, step: 1, value: 1, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "t32", robot: true, text: ["32 位、400 MHz：选出满足预算、面积最小的结构。", "32 bits, 400 MHz: pick the smallest structure that meets the budget."],
      demo: { scene: "acc", set: { w: 3, f: 400, k: 4 }, press: [], wait: 1 } },
    { id: "t600", text: ["32 位、600 MHz：再选一次。上一题的选择还行吗？", "32 bits, 600 MHz: choose again. Does the previous choice still work?"],
      demo: { scene: "acc", set: { w: 3, f: 600, k: 2 }, press: [], wait: 1 } },
    { id: "t8", text: ["8 位、800 MHz：选出满足预算、面积最小的结构。", "8 bits, 800 MHz: pick the smallest structure that meets the budget."],
      demo: { scene: "acc", set: { w: 1, f: 800, k: 4 }, press: [], wait: 1 } },
  ],
  think: ["为什么行波进位的面积在“追求延时”的综合里反而不是最小？比较不同结构时，怎样才算公平？",
          "Why is the ripple-carry adder not the smallest when synthesised for speed? What makes a comparison of structures fair?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: KIND61.map((_, i) => ({ name: NAME61[i], color: COL61[i] })),
  reset(api, s) { check61(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, w = W61[p.w - 1], s1 = syn61(p.k - 1, w), b = budget61(p.f), bk = best61(w, p.f);
    return [[["结构 / 位宽", "Structure / width"], api.T(NAME61[p.k - 1][0], NAME61[p.k - 1][1]) + " / " + w],
            [["时间预算", "Timing budget"], f(b, 0) + " ps"],
            [["延时 / 面积", "Delay / area"], f(s1.delay, 0) + " ps / " + f(s1.area, 0) + " μm²"],
            [["是否满足", "Meets the budget"], s1.delay <= b ? api.T("满足", "yes") : api.T("不满足", "no")],
            [["满足预算的最小结构", "Smallest that meets it"], bk < 0 ? api.T("没有", "none") : api.T(NAME61[bk][0], NAME61[bk][1])]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, mu = css("--muted"), ink = css("--ink");
    const p = api.p, wd = W61[p.w - 1], pts = KIND61.map((_, k) => syn61(k, wd));
    const dmax = Math.max(...pts.map((q) => q.delay)) * 1.15, amax = Math.max(...pts.map((q) => q.area)) * 1.15;
    const px = w * 0.12, py = h * 0.08, pw = w * 0.82, ph = h * 0.72;
    const ax = api.plot(px, py, pw, ph, [], { xmin: 0, xmax: dmax, ymin: 0, ymax: amax, xlabel: api.T("延时 / ps", "delay / ps"), ylabel: api.T("面积 / μm²", "area / μm²") });
    const b = budget61(p.f);
    if (b > 0 && b < dmax) api.line(ax.X(b), py, ax.X(b), py + ph, ink, 1.5, [6, 4]);
    api.label(api.T("预算", "budget"), Math.min(ax.X(Math.max(b, 0)), px + pw) + 4, py + 14, ink, 11, "left");
    pts.forEach((q, k) => {
      api.circle(ax.X(q.delay), ax.Y(q.area), k === p.k - 1 ? 9 : 6, COL61[k]);
      api.label(["RCA", "CLA", "CSEL", "BK", "KS"][k], ax.X(q.delay) + 10, ax.Y(q.area) + 4, COL61[k], 11, "left");
    });
    api.label("0", px, py + ph + 13, mu, 10, "center"); api.label(api.fmt(dmax, 0), px + pw, py + ph + 13, mu, 10, "right");
  },
});

function check61(api) {
  const p = api.p, w = W61[p.w - 1], b = best61(w, p.f);
  if (b !== p.k - 1) return;
  if (w === 32 && p.f === 400) api.done("t32");
  if (w === 32 && p.f === 600) api.done("t600");
  if (w === 8 && p.f === 800) api.done("t8");
}
