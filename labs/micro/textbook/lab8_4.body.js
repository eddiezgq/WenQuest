// 实验 8.4 时钟树（配 8.4 节）。第 3 章那块 2000 个触发器、100 MHz 的电机控制芯片，核心区 1 mm × 1 mm（教学设定），
// H 形树 L 层（4^L 个叶子），每个分叉一个 size 倍参考反相器的缓冲器，导线 met3；某区触发器多 imb 时的偏斜。模型 M8_4.htree，
// 与书中程序 conventions/mos.py 的 htree 一致。
const Q84 = M8_4.P.problems.p84, N84 = M8_4.P.problems.p34.n_ff, F84 = M8_4.P.problems.p34.f_MHz * 1e6;

WQ.lab({
  title: ["实验 8.4 时钟树", "Lab 8.4 Clock tree"],
  goal: ["把时钟送到 2000 个触发器：调 H 树的层数、缓冲器尺寸和负载不均，看插入延时、偏斜、时钟功耗，找出偏斜小又不太费电的方案。",
         "Deliver the clock to 2000 flip-flops: vary the H-tree levels, buffer size and load imbalance; watch insertion delay, skew and clock power; find a tree with small skew that does not waste power."],
  scenes: [
    { id: "chip", robot: true, name: ["电机控制芯片的时钟", "Clock of the motor-control chip"], hide: [],
      problem: { title: ["机器人问题：时钟树要多大", "Robot problem: how big a clock tree"],
                 text: ["偏斜要小于 50 ps，时钟功耗又不能太大。H 树分几层？缓冲器多大？", "Skew must stay under 50 ps without wasting clock power. How many levels, how big the buffers?"] } },
  ],
  params: [
    { id: "L", name: ["H 树层数 L（4^L 个叶子）", "H-tree levels L (4^L leaves)"], min: 1, max: 4, step: 1, value: 1, unit: "", digits: 0 },
    { id: "size", name: ["缓冲器尺寸（参考反相器的倍数）", "Buffer size (× reference inverter)"], min: 4, max: 32, step: 4, value: 16, unit: "", digits: 0 },
    { id: "imb", name: ["某区触发器多出", "Extra flip-flops in one region"], min: 0, max: 50, step: 5, value: 20, unit: "%", digits: 0 },
  ],
  tasks: [
    { id: "skew50", robot: true, text: ["缓冲器 16 倍、负载不均 20 %：偏斜小于 50 ps 最少要几层？", "Buffers 16×, imbalance 20 %: how many levels at least for skew below 50 ps?"],
      demo: { scene: "chip", set: { L: 3, size: 16, imb: 20 }, press: [], wait: 1 } },
    { id: "l1", text: ["只用 1 层、缓冲器加到 32 倍：插入延时和偏斜是多少？", "One level with 32× buffers: what are the insertion delay and skew?"],
      demo: { scene: "chip", set: { L: 1, size: 32, imb: 20 }, press: [], wait: 1 } },
    { id: "ratio", text: ["找一个方案，使导线和缓冲器的电容超过触发器自身的时钟电容。", "Find a tree whose wires and buffers have more capacitance than the flip-flops themselves."],
      demo: { scene: "chip", set: { L: 4, size: 16, imb: 20 }, press: [], wait: 1 } },
  ],
  think: ["为什么层数越多偏斜越小？只加大缓冲器为什么不够？", "Why does skew fall with more levels? Why are bigger buffers alone not enough?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["时钟树", "clock tree"], color: "#1d6fb8" }, { name: ["叶子（每区一个缓冲器）", "leaves (one buffer per region)"], color: "#2e8b57" }],
  reset(api, s) { const p = api.p; s.h = M8_4.htree(p.L, Q84.die_um, N84, p.size, Q84.layer, p.imb / 100, M8_4.P.VDD, F84); check84(api, s.h); },
  readouts(api, s) {
    const hh = s.h, f = api.fmt;
    return [[["叶子数 / 每区触发器 / 缓冲器数", "Leaves / FFs per region / buffers"], hh.leaves + " / " + f(hh.n_per, 0) + " / " + hh.n_buf],
            [["插入延时（树 + 叶子）", "Insertion delay (tree + leaf)"], f(hh.insertion * 1e12, 0) + " ps（" + f(hh.t_tree * 1e12, 0) + " + " + f(hh.t_leaf * 1e12, 0) + "）"],
            [["偏斜", "Skew"], f(hh.skew * 1e12, 1) + " ps"],
            [["时钟功耗：总 / 触发器", "Clock power: total / flip-flops"], f(hh.power * 1e3, 1) + " / " + f(hh.p_ff * 1e3, 1) + " mW"],
            [["导线与缓冲器 ÷ 触发器电容", "Wires+buffers ÷ FF capacitance"], f(hh.ratio, 2)]];
  },
  draw(api, s) {
    const { w, h } = api, L = api.p.L, sz = Math.min(w * 0.55, h * 0.86), cx = w * 0.32, cy = h * 0.5, blue = "#1d6fb8", green = "#2e8b57";
    api.rect(cx - sz / 2, cy - sz / 2, sz, sz, null, api.css("--muted"));
    const hd = (x, y, half, lev) => {
      if (lev > L) { api.rect(x - 2.5, y - 2.5, 5, 5, green); return; }
      const lw = Math.max(1, 3.5 - 0.7 * lev);
      api.line(x - half, y, x + half, y, blue, lw);
      for (const xx of [x - half, x + half]) {
        api.line(xx, y - half, xx, y + half, blue, lw);
        for (const yy of [y - half, y + half]) hd(xx, yy, half / 2, lev + 1);
      }
    };
    hd(cx, cy, sz / 4, 1);
    api.circle(cx, cy, 5, "#c0392b");
    const hh = s.h, bx = w * 0.68, bw = w * 0.26, by = h * 0.2, bh = h * 0.5, pmax = 40;
    const ff = hh.p_ff * 1e3, tot = hh.power * 1e3;
    api.label(api.T("时钟功耗 / mW", "clock power / mW"), bx, by - 10, api.css("--muted"), 12, "left");
    api.rect(bx, by + bh - ff / pmax * bh, bw * 0.4, ff / pmax * bh, "#7a8691");
    api.rect(bx + bw * 0.5, by + bh - Math.min(tot, pmax) / pmax * bh, bw * 0.4, Math.min(tot, pmax) / pmax * bh, "#e67e22");
    api.label(api.T("触发器", "FFs"), bx + bw * 0.2, by + bh + 14, api.css("--muted"), 10, "center");
    api.label(api.T("总计", "total"), bx + bw * 0.7, by + bh + 14, api.css("--muted"), 10, "center");
    api.label(api.fmt(tot, 1), bx + bw * 0.7, by + bh - Math.min(tot, pmax) / pmax * bh - 5, api.css("--ink"), 11, "center");
  },
});

function check84(api, hh) {
  const p = api.p;
  if (p.size === 16 && p.imb === 20 && hh.skew < 50e-12 && (p.L === 1 || M8_4.htree(p.L - 1, Q84.die_um, N84, 16, Q84.layer, 0.2).skew >= 50e-12)) api.done("skew50");
  if (p.L === 1 && p.size === 32) api.done("l1");
  if (hh.ratio > 1) api.done("ratio");
}
