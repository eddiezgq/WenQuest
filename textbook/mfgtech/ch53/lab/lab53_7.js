// 实验 53.7 SH-301 轴向工艺尺寸跟踪图（配 53.7 节）。
// 工序与基准取自数字工厂工艺规程的 tolerance_chart：工序 20 安装 1 从右端面 R 粗车右侧两个轴肩，安装 2 车左端面 L（总长 168）并从 L 粗车左侧两个轴肩；
// 工序 40 从 L 车右端面，从 R 精车 S3、S4，调头从 R 车左端面（总长 167），再从 L 精车 S1、S2。各尺寸链由跟踪图程序（hub/tolerance.py 的 ToleranceChart）
// 求出后化成下面的简化公式，程序 ex53_7 核对两者一致：
//   齿轮位 60 = 167 − 52 − 55：±(2 * p.tfs + p.t40L)；左右轴承位、左轴端长度只经过精车轴肩：±p.tfs 或 ±2 * p.tfs；
//   精车右端面余量 0.5 ±(p.t204 + p.t402)；右侧轴肩余量 a ±(p.trs + p.t204 + p.t402 + p.tfs)；
//   精车左端面余量 0.5 ±(p.t402 + p.t40L)；左侧轴肩余量 a ±(p.trs + p.t402 + p.t40L + p.tfs)。
const DR53 = [
  { id: "40", name: ["左轴端长 40", "left end 40"], tol: 0.3, f: (p) => p.tfs },
  { id: "12", name: ["左轴承位长 12", "left bearing 12"], tol: 0.2, f: (p) => 2 * p.tfs },
  { id: "60", name: ["齿轮位长 60", "gear seat 60"], tol: 0.3, f: (p) => 2 * p.tfs + p.t40L },
  { id: "25", name: ["右轴承位长 25", "right bearing 25"], tol: 0.2, f: (p) => 2 * p.tfs },
  { id: "167", name: ["总长 167", "overall 167"], tol: 0.5, f: (p) => p.t40L },
];
const AL53 = [
  { name: ["精车右端面 R", "finish R"], nom: () => 0.5, f: (p) => p.t204 + p.t402 },
  { name: ["精车右侧轴肩 S3、S4", "finish S3, S4"], nom: (p) => p.a, f: (p) => p.trs + p.t204 + p.t402 + p.tfs },
  { name: ["精车左端面 L", "finish L"], nom: () => 0.5, f: (p) => p.t402 + p.t40L },
  { name: ["精车左侧轴肩 S1、S2", "finish S1, S2"], nom: (p) => p.a, f: (p) => p.trs + p.t402 + p.t40L + p.tfs },
];

function eval53b(api) {
  const p = api.p;
  const dr = DR53.map((d) => ({ ...d, r: d.f(p), ok: d.f(p) <= d.tol + 1e-9 }));
  const al = AL53.map((a) => { const n = a.nom(p), t = a.f(p); return { ...a, n, min: n - t, max: n + t, ok: n - t >= p.zmin - 1e-9 }; });
  return { dr, al, ok: dr.every((d) => d.ok) && al.every((a) => a.ok) };
}

function check53b(api, s) {
  const e = eval53b(api), p = api.p;
  s.e = e;
  const bad60 = !e.dr[2].ok, neg = e.al.some((a) => a.min < 0);
  if (bad60 && neg) api.done("draft");
  const z = p.zmin >= 0.1 - 1e-9;            // 最小余量不得低于 0.1
  if (e.ok && z && p.t40L >= 0.2 - 1e-9) api.done("fix");
  if (e.ok && z && p.tfs >= 0.08 - 1e-9) api.done("trade");
  if (e.ok && z && p.a <= 0.6 + 1e-9) api.done("lean");
}

WQ.lab({
  title: ["实验 53.7 工艺尺寸跟踪图", "Lab 53.7 Tolerance chart"],
  goal: ["多道工序、多次调头加工的轴向尺寸，最容易出两种问题：图纸尺寸间接得到，保证不了；精加工余量变动太大，有的件车不出来。用 SH-301 的轴向跟踪图，调各工序尺寸的公差和粗车余量，看图纸尺寸和余量怎样变化，找出既能保证、又不苛刻的方案。",
         "Axial dimensions made over several operations and set-ups typically go wrong in two ways: a drawing dimension obtained indirectly cannot be held, or a finishing allowance varies so much that some parts do not clean up. With SH-301's axial chart, change the operation tolerances and roughing allowance and find a plan that holds without being harsh."],
  scenes: [
    { id: "chart", name: ["SH-301 轴向", "SH-301 axial"],
      problem: { title: ["工艺初稿的轴向尺寸有问题吗？", "Is the draft plan's axial dimensioning sound?"],
                 text: ["初稿里工序 40 的总长按 ±0.3 控制，轴肩粗车只留 0.5 mm。齿轮位长度 60 ± 0.3 由两个轴肩和总长间接保证，左右轴肩的精车余量又受两次调头的影响。", "In the draft, operation 40 holds the overall length to ±0.3 and roughing leaves only 0.5 mm on the shoulders. The 60 ± 0.3 gear seat comes indirectly from two shoulders and the overall length, and the shoulder allowances depend on two turnarounds."] } },
  ],
  params: [
    { id: "t40L", name: ["工序 40 总长 ±", "Op 40 overall ±"], min: 0.05, max: 0.5, step: 0.01, value: 0.3, unit: "mm", digits: 2 },
    { id: "tfs", name: ["工序 40 精车轴肩 ±", "Op 40 finish shoulders ±"], min: 0.01, max: 0.2, step: 0.01, value: 0.05, unit: "mm", digits: 2 },
    { id: "t402", name: ["工序 40 车右端面 ±", "Op 40 face R ±"], min: 0.02, max: 0.3, step: 0.01, value: 0.1, unit: "mm", digits: 2 },
    { id: "t204", name: ["工序 20 总长 ±", "Op 20 overall ±"], min: 0.05, max: 0.5, step: 0.01, value: 0.2, unit: "mm", digits: 2 },
    { id: "trs", name: ["工序 20 粗车轴肩 ±", "Op 20 rough shoulders ±"], min: 0.02, max: 0.3, step: 0.01, value: 0.1, unit: "mm", digits: 2 },
    { id: "a", name: ["轴肩粗车余量 a", "Shoulder roughing allowance a"], min: 0.2, max: 1.5, step: 0.05, value: 0.5, unit: "mm", digits: 2 },
    { id: "zmin", name: ["最小精车余量", "Minimum finishing allowance"], min: 0, max: 0.3, step: 0.05, value: 0.1, unit: "mm", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--green)", name: ["满足", "holds"] }, { color: "var(--red)", name: ["不满足", "fails"] }],
  tasks: [
    { id: "draft", text: ["初稿：在默认参数下，找出保证不了的图纸尺寸和余量可能为负（车不出来）的面。", "Draft: at the default settings, find the drawing dimension that cannot be held and the faces whose allowance can go negative."],
      demo: { scene: "chart", set: { t40L: 0.3, a: 0.5 } } },
    { id: "fix", text: ["改进：总长公差不小于 ±0.2，调其他参数使全部满足。", "Fix: keep the overall tolerance at ±0.2 or wider and adjust the rest until everything holds."],
      demo: { scene: "chart", set: { t40L: 0.2, tfs: 0.05, a: 0.8 } } },
    { id: "trade", text: ["取舍：精车轴肩的公差放宽到 ±0.08（车床更省事），总长要收紧到多少才行？", "Trade-off: relax the finish-shoulder tolerance to ±0.08 (easier turning); how tight must the overall length be?"],
      demo: { scene: "chart", set: { tfs: 0.08, t40L: 0.14, a: 0.8 } } },
    { id: "lean", text: ["省料：在全部满足的前提下，把轴肩粗车余量减到 0.6 mm 以下，其他公差怎样配合？", "Lean: with everything holding, cut the shoulder roughing allowance to 0.6 mm or less; what must the other tolerances be?"],
      demo: { scene: "chart", set: { t40L: 0.2, tfs: 0.05, t402: 0.05, trs: 0.05, t204: 0.2, a: 0.6 } } },
  ],
  think: ["齿轮位长度 60 为什么不直接从一个轴肩量到另一个轴肩？如果改成“以左轴肩为基准车右轴肩”，跟踪图会怎样变？", "Why not measure the 60 directly from one shoulder to the other? If the right shoulder were turned from the left one, how would the chart change?"],

  reset(api, s) { check53b(api, s); },
  update(dt, api, s) { check53b(api, s); api.stop(); },
  readouts(api, s) {
    const e = s.e || eval53b(api), f = api.fmt, T = api.T;
    return [
      ...e.dr.map((d) => [d.name, `±${f(d.r, 2)} / ±${f(d.tol, 1)} · ${d.ok ? T("满足", "holds") : T("不满足", "fails")}`]),
      ...e.al.map((a) => [a.name, `${f(a.min, 2)}–${f(a.max, 2)} mm · ${a.ok ? T("够", "enough") : T("不够", "short")}`])];
  },
  draw(api, s) {
    const e = s.e || eval53b(api), { w, h } = api, css = api.css;
    const xs = { L: 0, S1: 40, S2: 52, S3: 112, S4: 137, R: 167 }, X = (x) => w * 0.08 + w * 0.84 * x / 167;
    Object.entries(xs).forEach(([k, x]) => { api.line(X(x), h * 0.12, X(x), h * 0.9, css("--muted"), 1); api.label(k, X(x), h * 0.08, css("--ink"), 12, "center"); });
    const rows = [["40", "L", "S1"], ["12", "S1", "S2"], ["60", "S2", "S3"], ["25", "S3", "S4"], ["167", "L", "R"]];
    rows.forEach(([id, a, b], i) => {
      const d = e.dr.find((q) => q.id === id), y = h * (0.2 + 0.1 * i), col = d.ok ? css("--green") : css("--red");
      api.line(X(xs[a]), y, X(xs[b]), y, col, 4);
      api.label(`${id} ±${api.fmt(d.r, 2)}`, (X(xs[a]) + X(xs[b])) / 2, y - 10, col, 12, "center");
    });
    e.al.forEach((a, i) => {
      const y = h * (0.74 + 0.04 * i), col = a.ok ? css("--green") : css("--red");
      api.label(`${api.T(a.name[0], a.name[1])}: ${api.fmt(a.min, 2)}–${api.fmt(a.max, 2)}`, w * 0.1, y, col, 12);
    });
  },
});
