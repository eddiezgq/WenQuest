// 实验 3.5 时间常数与欧拉法（配 3.5 节）。
// 停转场景（测量型）：关节断电后靠粘性摩擦停下，编码器每 0.2 s 给一个转速读数（相对误差约 ±3%，另有 ±0.012 rad/s 的零点误差，
// 按序号确定的伪随机数）。真实的时间常数 0.65 s 学生不知道；学生画 ln ω–t 图拟合斜率求 τ，提交结果，与真实值相差 4% 以内算对。
// 欧拉法场景：dω/dt = −ω/τ，τ = 0.8 s，学生选步长 h，看欧拉解与精确解；h > τ 时来回振荡，h > 2τ 时发散。
// 咖啡场景：T = 20 + 70 e^(−t/τ)，有盖 τ = 40 min，无盖 τ = 22 min；学生找到降到 60 °C 的时刻。
const TAU35 = 0.65, W035 = 2.8;
function hash35(a, b) { const x = Math.sin(a * 12.9898 + b * 78.233 + 1.2345) * 43758.5453; return x - Math.floor(x); }
const DATA35 = Array.from({ length: 11 }, (_, k) => { const t = 0.2 * k;
  return [Math.round(t * 10) / 10, Math.round((W035 * Math.exp(-t / TAU35) * (1 + 0.03 * (hash35(k, 5.5) + hash35(k, 6.6) - 1)) + 0.024 * (hash35(k, 7.7) - 0.5)) * 1000) / 1000]; });
const TE35 = 0.8, WE35 = 3.0;
function euler35(h, tend) { const pts = [[0, WE35]]; let w = WE35, t = 0; while (t < tend - 1e-9) { w += h * (-w / TE35); t += h; pts.push([t, w]); } return pts; }
function err35(h) { const n = Math.round(2 / h), wn = WE35 * Math.pow(1 - h / TE35, n), ex = WE35 * Math.exp(-n * h / TE35); return { t: n * h, wn, ex, rel: 100 * Math.abs(wn - ex) / ex }; }
const tauC35 = (lid) => (lid ? 40 : 22), cof35 = (t, lid) => 20 + 70 * Math.exp(-t / tauC35(lid));

WQ.lab({
  title: ["实验 3.5 时间常数与欧拉法", "Lab 3.5 Time constants and Euler's method"],
  goal: ["由关节停转的转速记录测出时间常数；用欧拉法一步步解微分方程，看步长的影响；算一杯咖啡什么时候能喝。",
         "Measure a time constant from a joint's coast-down record; solve a differential equation step by step with Euler's method and see the effect of the step; find when a coffee is ready to drink."],
  scenes: [
    { id: "coast", robot: true, name: ["关节停转测 τ", "Measuring τ from a coast-down"], hide: ["h", "lid", "tw"],
      problem: { title: ["机器人问题：断电的关节多快停下", "Robot problem: how fast does an unpowered joint stop"],
                 text: ["关节断电后靠粘性摩擦停下，ω = ω₀ e^(−t/τ)。编码器每 0.2 s 给一个转速读数（有误差）。把纵轴换成 ln ω，拟合直线的斜率求 τ，把“你测得的 τ”调到你的结果，点“提交”。",
                        "The unpowered joint stops under viscous friction, ω = ω₀ e^(−t/τ). The encoder gives a speed every 0.2 s (with errors). Switch the vertical axis to ln ω, fit the slope to find τ, set “Your τ” and press “Submit”."] } },
    { id: "euler", name: ["欧拉法", "Euler's method"], hide: ["yax", "tauhat", "lid", "tw"],
      problem: { title: ["数值方法：一步一步算", "Numerical method: one step at a time"],
                 text: ["解 dω/dt = −ω/τ，τ = 0.8 s，ω₀ = 3.0 rad/s。欧拉法每一步按这一步开始时的变化率走 h 秒。改变步长，与精确解比较。",
                        "Solve dω/dt = −ω/τ with τ = 0.8 s and ω₀ = 3.0 rad/s. Each Euler step moves h seconds at the rate found at the start of the step. Change h and compare with the exact solution."] } },
    { id: "coffee", name: ["咖啡变凉", "A cooling coffee"], hide: ["yax", "tauhat", "h"],
      problem: { title: ["生活中的例子：咖啡什么时候能喝", "Everyday example: when can you drink the coffee"],
                 text: ["一杯 90 °C 的咖啡放在 20 °C 的房间里，T = 20 + 70 e^(−t/τ)。有盖时 τ 大，无盖时 τ 小。等多久才降到 60 °C？",
                        "A 90 °C coffee in a 20 °C room cools as T = 20 + 70 e^(−t/τ); a lid makes τ larger. How long until it reaches 60 °C?"] } },
  ],
  params: [
    { id: "yax", name: ["纵轴：0 为 ω，1 为 ln ω", "Vertical axis: 0 ω, 1 ln ω"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "tauhat", name: ["你测得的 τ", "Your τ"], min: 0.3, max: 1.2, step: 0.005, value: 0.5, unit: "s", digits: 3 },
    { id: "h", name: ["步长 h", "Step h"], min: 0.01, max: 2, step: 0.01, value: 0.4, unit: "s", digits: 2 },
    { id: "lid", name: ["杯盖：0 无盖，1 有盖", "Lid: 0 off, 1 on"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "tw", name: ["等待时间", "Waiting time"], min: 0, max: 60, step: 0.5, value: 5, unit: "min", digits: 1 },
  ],
  buttons: [{ id: "submit", name: ["提交 τ（停转）", "Submit τ (coast-down)"], primary: true }],
  tasks: [
    { id: "tau", robot: true, text: ["停转：由读数拟合求出时间常数，提交（与真实值相差 4% 以内）。用 ln ω–t 图为什么比 ω–t 图好？",
                                    "Coast-down: fit the readings for the time constant and submit it (within 4% of the true value). Why is the ln ω–t plot better than the ω–t plot?"],
      demo: { scene: "coast", set: { yax: 1, tauhat: 0.645 }, press: ["submit"], wait: 1 } },
    { id: "e5", text: ["欧拉法：选步长，使 t ≈ 2 s 处的相对误差小于 5%。", "Euler: choose h so that the relative error near t = 2 s is below 5%."],
      demo: { scene: "euler", set: { h: 0.03 }, press: [], wait: 1 } },
    { id: "osc", text: ["欧拉法：加大步长，找出欧拉解开始正负来回跳的范围（仍然逐渐变小）。", "Euler: increase h until the Euler solution flips sign every step (while still shrinking)."],
      demo: { scene: "euler", set: { h: 1.2 }, press: [], wait: 1 } },
    { id: "div", text: ["欧拉法：步长再大，解会越跳越大（发散）。这个临界步长与 τ 是什么关系？", "Euler: with a still larger step the solution grows without bound. How does this critical step relate to τ?"],
      demo: { scene: "euler", set: { h: 1.8 }, press: [], wait: 1 } },
    { id: "cof", text: ["咖啡：无盖时，找到温度降到 60 °C 的时刻（相差 1 °C 以内）。有盖时要多等多久？", "Coffee: without the lid, find when the temperature reaches 60 °C (within 1 °C). How much longer with the lid?"],
      demo: { scene: "coffee", set: { lid: 0, tw: 12.5 }, press: [], wait: 1 } },
  ],
  think: ["停转实验中，尾部的读数（ω 很小时）在 ln ω 图上为什么比前面的分散得多？拟合时应当怎样对待它们？欧拉法发散的临界步长为什么正好是 2τ？",
          "Why are the late readings (small ω) much more scattered on the ln ω plot, and how should the fit treat them? Why is the critical Euler step exactly 2τ?"],

  reset(api, s) {},
  action(id, api, s) {
    if (id === "submit" && api.scene === "coast") {
      const ok = Math.abs(api.p.tauhat - TAU35) / TAU35 < 0.04;
      s.msg = ok ? api.T("对了", "correct") : api.T("不对，再检查拟合", "not yet, check your fit");
      if (ok) api.done("tau");
    }
  },
  change(api, s, pid) {
    const p = api.p;
    if (api.scene === "euler") { const E = err35(p.h); if (E.rel < 5) api.done("e5"); if (p.h > TE35 && p.h < 2 * TE35) api.done("osc"); if (p.h > 2 * TE35) api.done("div"); }
    if (api.scene === "coffee" && !p.lid && Math.abs(cof35(p.tw, 0) - 60) <= 1) api.done("cof");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p;
    if (api.scene === "coast") return [[["读数个数", "Readings"], String(DATA35.length)], [["ω₀（第一个读数）", "ω₀ (first reading)"], f(DATA35[0][1], 3) + " rad/s"],
      [["你测得的 τ", "Your τ"], f(p.tauhat, 3) + " s"], [["提交结果", "Submission"], s.msg || "—"]];
    if (api.scene === "euler") { const E = err35(p.h); return [[["步长 h / τ", "h / τ"], f(p.h / TE35, 2)], [["t ≈ 2 s 处（实际 t）", "near t = 2 s (actual t)"], f(E.t, 2) + " s"],
      [["欧拉解", "Euler"], f(E.wn, 4) + " rad/s"], [["精确解", "Exact"], f(E.ex, 4) + " rad/s"], [["相对误差", "Relative error"], f(E.rel, 1) + "%"]]; }
    return [[["时间常数 τ", "Time constant τ"], tauC35(p.lid) + " min"], [["等待时间", "Waiting time"], f(p.tw, 1) + " min"], [["咖啡温度", "Coffee temperature"], f(cof35(p.tw, p.lid), 1) + " °C"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, blue = css("--blue"), mut = css("--muted"), ink = css("--ink"), red = css("--red");
    if (api.scene === "coast") {
      api.arm(w * 0.12, h * 0.62, [35, -50], [70, 60], ink, 10);
      api.label(api.T("断电后靠摩擦停下", "coasting to a stop"), w * 0.12, h * 0.62 + 30, mut, 11, "center");
      DATA35.forEach(([t, v], i) => { api.label(api.fmt(t, 1) + " s", w * 0.03, 28 + i * 16, mut, 11); api.label(api.fmt(v, 3), w * 0.13, 28 + i * 16, ink, 11); });
      api.label(api.T("t　　ω / (rad/s)", "t      ω / (rad/s)"), w * 0.03, 14, mut, 11);
      const lg = !!p.yax;
      const G = api.graph({ x: w * 0.3, y: 26, w: w * 0.66, h: h - 80, xmin: 0, xmax: 2.2, ymin: lg ? -2.5 : 0, ymax: lg ? 1.5 : 3.2, xlabel: "t / s", ylabel: lg ? "ln(ω / (rad/s))" : "ω / (rad/s)" }).axes();
      DATA35.forEach(([t, v]) => G.point(t, lg ? Math.log(v) : v, blue));
      if (lg) G.line(0, Math.log(DATA35[0][1]), -1 / p.tauhat, red, 1.5, [6, 4]);
      else G.fn((t) => DATA35[0][1] * Math.exp(-t / p.tauhat), red, 1.5, [6, 4]);
      G.text(api.T("红虚线：按你的 τ 画出", "red dashed: drawn with your τ"), 1.0, lg ? 1.2 : 3.0, red, 11);
      return;
    }
    if (api.scene === "euler") {
      const big = p.h > 1.2 * TE35, G = api.graph({ x: 56, y: 26, w: w - 90, h: h - 80, xmin: 0, xmax: 6, ymin: big ? -6 : -1.5, ymax: big ? 6 : 3.5, xlabel: "t / s", ylabel: "ω / (rad/s)" }).axes();
      G.fn((t) => WE35 * Math.exp(-t / TE35), ink, 2.5);
      const E = euler35(p.h, 6); G.pts(E, red, 1.5).dots(E, red, 3);
      G.text(api.T("黑：精确解　红：欧拉法", "black: exact   red: Euler"), 3.2, big ? 5.2 : 3.1, mut, 11);
      return;
    }
    const G = api.graph({ x: 56, y: 26, w: w - 90, h: h - 80, xmin: 0, xmax: 60, ymin: 15, ymax: 95, xlabel: "t / min", ylabel: "T / °C" }).axes();
    G.fn((t) => cof35(t, 0), css("--amber"), 2).fn((t) => cof35(t, 1), blue, 2).hline(60, mut).hline(20, mut);
    G.point(p.tw, cof35(p.tw, p.lid), p.lid ? blue : css("--amber"), api.fmt(cof35(p.tw, p.lid), 1) + " °C");
    G.text(api.T("橙：无盖　蓝：有盖　虚线：60 °C 与室温", "orange: no lid   blue: lid   dashed: 60 °C and room"), 18, 92, mut, 11);
  },
});
