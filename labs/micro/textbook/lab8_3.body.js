// 实验 8.3 时序分析器（配 8.2、8.3 节）。PI 电流环数据通路：减法 → 乘法（Kp·e、Ki·e 并行）→ 积分加法 → 输出加法 → 饱和。
// 各块的延时与面积取 params.json 的 arith_syn（第 6 章按 SKY130 单元库综合）：低成本用“只求面积”的行波进位、阵列乘法器，
// 快速用“尽量快”的 Kogge–Stone、Dadda 树、Brent–Kung；饱和电路用逻辑努力估算（M8_3.satDelay），不计面积。与书中程序 code/_pi.py 相同。
const Q83 = M8_3.P.problems.p81, S83 = M8_3.P.arith_syn, FF83 = M8_3.ffTiming(), FFA83 = M8_3.P.problems.p73.ff_area;
const NAMES83 = ["sub", "mul", "add1", "add2", "sat"], CNT83 = { sub: 1, mul: 2, add1: 1, add2: 1, sat: 1 };
const WID83 = { sub: 16, mul: 64, add1: 64, add2: 32 };   // 切口要切断所有往前走的边（add1 后面是 s 和 p）
const LAB83 = { sub: ["减法", "sub"], mul: ["乘法 ×2", "mul ×2"], add1: ["积分加法", "integ. add"], add2: ["输出加法", "out add"], sat: ["饱和", "sat"] };
function blocks83(style) {
  const out = {};
  Q83.blocks.forEach(([n, cheap, fast]) => {
    if (n === "sat") { out[n] = [M8_3.satDelay(), 0]; return; }
    const r = S83[style === 1 ? cheap : fast];
    out[n] = style === 1 ? [r.delay_amin * 1e-12, r.area_min * CNT83[n]] : [r.delay * 1e-12, r.area * CNT83[n]];
  });
  return out;
}
function analyse83(p) {
  const b = blocks83(p.style), cuts = ["sub", "mul", "add1", "add2"].filter((n, i) => p["c" + (i + 1)] === 1);
  const st = []; let cur = 0, names = [];
  NAMES83.forEach((n) => { cur += b[n][0]; names.push(n); if (cuts.includes(n)) { st.push([cur, names]); cur = 0; names = []; } });
  st.push([cur, names]);
  const oh = FF83.tcq + FF83.tsu, loop = oh + b.add1[0];
  const tmin = Math.max(Math.max(...st.map((s) => s[0])) + oh, loop);
  let area = 0; Object.values(b).forEach((x) => { area += x[1]; });
  const nreg = cuts.reduce((a, c) => a + WID83[c], 0);
  return { st, oh, loop, tmin, cuts, nreg, area: area + nreg * FFA83, T: 1e-6 / p.f };
}

WQ.lab({
  title: ["实验 8.3 时序分析器", "Lab 8.3 Timing analyser"],
  goal: ["关节电机 PI 电流环的数据通路：选结构、选在哪里插寄存器、调时钟频率，看各级延时、余量和关键路径，用最小的代价满足 50 MHz。",
         "The PI current-loop datapath of a joint motor: choose structures, where to insert registers and the clock, watch stage delays, slack and the critical path, and meet 50 MHz at the least cost."],
  scenes: [
    { id: "pi", robot: true, name: ["PI 电流环数据通路", "PI current-loop datapath"], hide: [],
      problem: { title: ["机器人问题：低成本版本赶不上 50 MHz", "Robot problem: the low-cost version misses 50 MHz"],
                 text: ["行波进位加法器和阵列乘法器面积小但慢。换快结构，还是插一级寄存器？",
                        "Ripple adders and an array multiplier are small but slow. Faster structures, or one pipeline register?"] } },
  ],
  params: [
    { id: "style", name: ["结构（1 低成本，2 快速）", "Structures (1 low-cost, 2 fast)"], min: 1, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "f", name: ["时钟频率", "Clock frequency"], min: 20, max: 150, step: 5, value: 50, unit: "MHz", digits: 0 },
    { id: "c1", name: ["减法后插寄存器（0/1）", "Register after sub (0/1)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "c2", name: ["乘法后插寄存器（0/1）", "Register after mul (0/1)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "c3", name: ["积分加法与输出加法之间插寄存器（0/1）", "Register between the two adders (0/1)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "c4", name: ["输出加法后插寄存器（0/1）", "Register after out add (0/1)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "crit", robot: true, text: ["低成本、不插寄存器、50 MHz：读出关键路径所在的一级和最高频率。", "Low-cost, no registers, 50 MHz: read the critical stage and the maximum frequency."],
      demo: { scene: "pi", set: { style: 1, f: 50, c1: 0, c2: 0, c3: 0, c4: 0 }, press: [], wait: 1 } },
    { id: "pipe", text: ["低成本、50 MHz：只插一级寄存器，让余量变为正。插在哪里？", "Low-cost, 50 MHz: insert just one register so the slack becomes positive. Where?"],
      demo: { scene: "pi", set: { style: 1, f: 50, c1: 0, c2: 1, c3: 0, c4: 0 }, press: [], wait: 1 } },
    { id: "fast", text: ["换成快速结构、不插寄存器、50 MHz：满足吗？面积是多少？", "Fast structures, no registers, 50 MHz: does it meet? What is the area?"],
      demo: { scene: "pi", set: { style: 2, f: 50, c1: 0, c2: 0, c3: 0, c4: 0 }, press: [], wait: 1 } },
  ],
  think: ["为什么插在乘法器后面最好，而插在减法器后面不行？积分加法和积分寄存器之间为什么不能插？",
          "Why is after the multipliers the best place and after the subtractor not enough? Why can no register go between the integrator adder and its register?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["满足的一级", "stage that meets"], color: "#2e8b57" }, { name: ["违例的一级", "violating stage"], color: "#c0392b" }],
  reset(api, s) { s.a = analyse83(api.p); check83(api, s.a); },
  readouts(api, s) {
    const a = s.a, f = api.fmt, worst = a.st.reduce((b, x) => (x[0] > b[0] ? x : b));
    return [[["各级逻辑（ns）", "Stage logic (ns)"], a.st.map((x) => f(x[0] * 1e9, 1)).join(" / ")],
            [["关键的一级", "Critical stage"], worst[1].map((n) => api.T(LAB83[n][0], LAB83[n][1])).join(" → ")],
            [["最小周期 / 最高频率", "Min period / max frequency"], f(a.tmin * 1e9, 1) + " ns / " + f(1e-6 / a.tmin, 0) + " MHz"],
            [["最差余量", "Worst slack"], f((a.T - a.tmin) * 1e9, 2) + " ns" + (a.T >= a.tmin ? api.T("（满足）", " (meets)") : api.T("（违例）", " (fails)"))],
            [["多出的延迟 / 触发器 / 面积", "Extra latency / flip-flops / area"], a.cuts.length + api.T(" 拍 / ", " cycles / ") + a.nreg + " / " + f(a.area, 0) + " μm²"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, mu = css("--muted"), ink = css("--ink"), a = s.a;
    const px = w * 0.1, py = h * 0.1, pw = w * 0.82, ph = h * 0.56, n = a.st.length;
    const ymax = Math.max(32, a.T * 1e9 * 1.1);
    const ax = api.plot(px, py, pw, ph, [], { xmin: 0, xmax: n, ymin: 0, ymax, ylabel: api.T("每一级 / ns", "per stage / ns") });
    a.st.forEach((x, i) => {
      const t = (x[0] + a.oh) * 1e9, col = x[0] + a.oh <= a.T ? "#2e8b57" : "#c0392b";
      api.rect(ax.X(i + 0.2), ax.Y(t), ax.X(i + 0.8) - ax.X(i + 0.2), ax.Y(0) - ax.Y(t), col);
      api.label(api.fmt(t, 1), ax.X(i + 0.5), ax.Y(t) - 4, ink, 11, "center");
      api.label(x[1].map((nm) => api.T(LAB83[nm][0], LAB83[nm][1])).join("+"), ax.X(i + 0.5), py + ph + 14, mu, 10, "center");
    });
    const yT = ax.Y(a.T * 1e9);
    api.line(px, yT, px + pw, yT, "#e67e22", 1.5, [6, 4]);
    api.label(api.T("时钟周期 ", "period ") + api.fmt(a.T * 1e9, 1) + " ns", px + pw - 4, yT - 5, "#e67e22", 11, "right");
    // 数据通路示意：块与寄存器
    const y0 = h * 0.86, bw = pw / 5.6;
    NAMES83.forEach((nm, i) => {
      const x = px + i * bw * 1.12;
      api.rect(x, y0 - 12, bw, 24, "#9fb7cc");
      api.label(api.T(LAB83[nm][0], LAB83[nm][1]), x + bw / 2, y0 + 4, ink, 10, "center");
      if (a.cuts.includes(nm)) api.rect(x + bw + 2, y0 - 16, 6, 32, "#2e8b57");
    });
  },
});

function check83(api, a) {
  const p = api.p, nc = p.c1 + p.c2 + p.c3 + p.c4;
  if (p.style === 1 && nc === 0 && p.f === 50) api.done("crit");
  if (p.style === 1 && nc === 1 && p.f === 50 && a.T >= a.tmin) api.done("pipe");
  if (p.style === 2 && nc === 0 && p.f === 50 && a.T >= a.tmin) api.done("fast");
}
