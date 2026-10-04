// 实验 3.1 数值求导与数值积分：AGV 的速度和电量记录（配 3.1、3.3、3.4 节）。
// 编码器场景：AGV 车轮编码器每 10 ms 给一次位置，分辨率 1 mm（读数是向下取整的整毫米数）；学生选步长 h = n × 10 ms 和差分方法，
// 看由读数算出的速度与实际速度（仿真中已知）的方均根误差：步长太小，量化误差被放大；步长太大，截断误差变大。
// 电量场景：电池管理系统按采样间隔 Δt 记录放电电流，用左矩形和或梯形法求 120 s 内放出的电荷量，与 0.01 s 高速记录的参考值比较。
// 手机场景：手机 GPS 每秒给一次位置（标准偏差约 2 m 的随机误差，按序号确定的伪随机数），途中在路口停了 20 s；学生选中心差分的半窗口。
const DT31 = 0.01, Q31 = 0.001, N31 = 401;                         // 编码器：采样周期 s、分辨率 m、读数个数（0～4 s）
const xt31 = (t) => 0.8 * t - 0.2 * Math.cos(1.5 * t) + 0.2, vt31 = (t) => 0.8 + 0.3 * Math.sin(1.5 * t);
const X31 = Array.from({ length: N31 }, (_, k) => Math.floor(xt31(k * DT31) / Q31 + 1e-9) * Q31);
function enc31(n, meth) {                                        // 0.6～3.4 s 内每个读数处的速度估计及方均根误差
  const pts = []; let s = 0;
  for (let k = 60; k <= 340; k++) {
    const v = meth ? (X31[k + n] - X31[k - n]) / (2 * n * DT31) : (X31[k + n] - X31[k]) / (n * DT31);
    pts.push([k * DT31, v]); s += (v - vt31(k * DT31)) ** 2;
  }
  return { pts, rms: Math.sqrt(s / pts.length) };
}
const I31 = (t) => 8 + 22 * (1 - Math.exp(-t / 25)) + 5 * Math.sin(1.3 * t) * Math.exp(-t / 200), T31 = 120;
const QREF31 = (() => { let s = 0; const h = 0.01, n = Math.round(T31 / h); for (let i = 0; i < n; i++) s += (I31(i * h) + I31((i + 1) * h)) / 2 * h; return s; })();
function bat31(dt, rule) {
  const n = Math.floor(T31 / dt + 1e-9); let s = 0;
  for (let i = 0; i < n; i++) s += rule ? (I31(i * dt) + I31((i + 1) * dt)) / 2 * dt : I31(i * dt) * dt;
  return { Q: s, err: 100 * (s - QREF31) / QREF31, n: n + 1 };
}
function hash31(a, b) { const x = Math.sin(a * 12.9898 + b * 78.233 + 1.2345) * 43758.5453; return x - Math.floor(x); }
const gn31 = (k) => (hash31(k, 1.1) + hash31(k, 2.2) + hash31(k, 3.3) + hash31(k, 4.4) - 2) * Math.sqrt(3) * 2.0;   // 近似正态，σ = 2 m
const vw31 = (t) => (t < 50 ? 1.4 : t < 55 ? 1.4 * (55 - t) / 5 : t < 75 ? 0 : t < 80 ? 1.4 * (t - 75) / 5 : 1.4);
const XW31 = (() => { const x = [0]; for (let k = 1; k <= 130; k++) x.push(x[k - 1] + (vw31(k - 1) + vw31(k)) / 2); return x.map((v, k) => v + gn31(k)); })();
function gps31(w) {
  const pts = []; let s = 0;
  for (let k = 20; k <= 110; k++) { const v = (XW31[k + w] - XW31[k - w]) / (2 * w); pts.push([k, v]); s += (v - vw31(k)) ** 2; }
  return { pts, rms: Math.sqrt(s / pts.length) };
}

WQ.lab({
  title: ["实验 3.1 数值求导与数值积分", "Lab 3.1 Numerical differentiation and integration"],
  goal: ["由编码器读数求 AGV 的速度，由电流记录求电池放出的电荷量；找出合适的步长，比较不同方法的误差。",
         "Find an AGV's speed from encoder readings and the charge drawn from a current log; choose a good step and compare the errors of different methods."],
  scenes: [
    { id: "enc", robot: true, name: ["编码器求速度", "Speed from the encoder"], hide: ["dt", "rule", "w"],
      problem: { title: ["机器人问题：由编码器读数求速度", "Robot problem: speed from encoder readings"],
                 text: ["AGV 车轮编码器每 10 ms 报告一次走过的距离，分辨率 1 mm。用相隔 h = n × 10 ms 的两个读数相减再除以时间，得到速度。选差分方法和 n，使算出的速度最接近实际速度（灰线）。",
                        "The wheel encoder reports the distance every 10 ms with 1 mm resolution. Subtract two readings h = n × 10 ms apart and divide by the time. Choose the method and n so that the computed speed is closest to the true speed (grey)."] } },
    { id: "bat", robot: true, name: ["安时积分", "Coulomb counting"], hide: ["n", "meth", "w"],
      problem: { title: ["机器人问题：电池放出了多少电", "Robot problem: how much charge has the battery delivered"],
                 text: ["AGV 起步载货时，放电电流在变化。电池管理系统每隔 Δt 记录一次电流，用矩形和或梯形法求 120 s 内放出的电荷量，与高速记录得到的参考值比较。",
                        "As the AGV starts with a load, the battery current varies. The battery management system logs it every Δt; find the charge over 120 s with the rectangle rule or the trapezoid rule and compare with the reference from a fast log."] } },
    { id: "gps", name: ["手机测步行速度", "Walking speed from a phone"], hide: ["n", "meth", "dt", "rule"],
      problem: { title: ["生活中的例子：手机怎样算出你走多快", "Everyday example: how a phone works out your walking speed"],
                 text: ["手机 GPS 每秒给一次位置，误差约 2 m。你以 1.4 m/s 步行，途中在路口停了 20 s。用中心差分求速度，选半窗口 w（用 t − w 和 t + w 两个位置）。",
                        "The phone's GPS gives a position every second with an error of about 2 m. You walk at 1.4 m/s and stop 20 s at a crossing. Use central differences over a half-window w (positions at t − w and t + w)."] } },
  ],
  params: [
    { id: "n", name: ["步长 h = n × 10 ms 中的 n", "n in the step h = n × 10 ms"], min: 1, max: 60, step: 1, value: 1, unit: "", digits: 0 },
    { id: "meth", name: ["方法：0 前向差分，1 中心差分", "Method: 0 forward, 1 central"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "dt", name: ["采样间隔 Δt", "Sampling interval Δt"], min: 0.5, max: 15, step: 0.5, value: 5, unit: "s", digits: 1 },
    { id: "rule", name: ["方法：0 左矩形和，1 梯形法", "Rule: 0 left rectangles, 1 trapezoid"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "w", name: ["半窗口 w", "Half-window w"], min: 1, max: 20, step: 1, value: 1, unit: "s", digits: 0 },
  ],
  buttons: [],
  tasks: [
    { id: "encF", robot: true, text: ["编码器：用前向差分，找一个 n 使速度的方均根误差小于 0.012 m/s。n 比这大或小，误差为什么都变大？",
                                     "Encoder: with forward differences, find n that brings the RMS speed error below 0.012 m/s. Why does the error grow when n is larger or smaller?"],
      demo: { scene: "enc", set: { meth: 0, n: 5 }, press: [], wait: 1 } },
    { id: "encC", robot: true, text: ["编码器：改用中心差分，找一个 n 使方均根误差小于 0.0025 m/s。最佳的 h 比前向差分大还是小？",
                                     "Encoder: switch to central differences and find n that brings the RMS error below 0.0025 m/s. Is the best h larger or smaller than for forward differences?"],
      demo: { scene: "enc", set: { meth: 1, n: 10 }, press: [], wait: 1 } },
    { id: "batT", robot: true, text: ["安时积分：用梯形法，找出误差不超过 0.1% 的最大采样间隔。",
                                     "Coulomb counting: with the trapezoid rule, find the largest sampling interval whose error is within 0.1%."],
      demo: { scene: "bat", set: { rule: 1, dt: 2 }, press: [], wait: 1 } },
    { id: "batL", robot: true, text: ["安时积分：同样的采样间隔改用左矩形和，误差是梯形法的多少倍？为什么左矩形和总是偏小？",
                                     "Coulomb counting: at the same interval use left rectangles. How many times larger is the error, and why is it always low?"],
      demo: { scene: "bat", set: { rule: 0, dt: 2 }, press: [], wait: 1 } },
    { id: "gps", text: ["手机：选半窗口 w，使速度的方均根误差小于 0.26 m/s。窗口太大时，停下和起步的时刻看起来怎样？",
                        "Phone: choose w so that the RMS speed error is below 0.26 m/s. With a large window, what do the stop and the restart look like?"],
      demo: { scene: "gps", set: { w: 8 }, press: [], wait: 1 } },
  ],
  think: ["三个场景里，步长（窗口）都不是越小越好。误差由哪两部分组成？各自怎样随步长变化？电量场景中 Δt = 5 s、10 s 时误差忽大忽小，说明了什么？",
          "In all three scenes a smaller step is not always better. Which two parts make up the error, and how does each depend on the step? What do the erratic errors at Δt = 5 s and 10 s in the battery scene tell you?"],

  reset(api, s) {},
  change(api, s, pid) { check31(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p;
    if (api.scene === "enc") {
      const E = enc31(p.n, p.meth);
      return [[["方法", "Method"], p.meth ? api.T("中心差分", "central") : api.T("前向差分", "forward")], [["步长 h", "Step h"], f(p.n * 10, 0) + " ms"],
        [["速度的方均根误差", "RMS speed error"], f(E.rms, 4) + " m/s"], [["读数分辨率造成的误差约", "Error from the resolution, about"], f(Q31 / (p.n * DT31) / (p.meth ? 2 : 1), 4) + " m/s"]];
    }
    if (api.scene === "bat") {
      const B = bat31(p.dt, p.rule);
      return [[["方法", "Rule"], p.rule ? api.T("梯形法", "trapezoid") : api.T("左矩形和", "left rectangles")], [["采样点数", "Samples"], String(B.n)],
        [["算出的电荷量", "Computed charge"], f(B.Q, 1) + " C"], [["参考值（0.01 s 记录）", "Reference (0.01 s log)"], f(QREF31, 1) + " C"], [["相对误差", "Relative error"], f(B.err, 3) + "%"]];
    }
    const G = gps31(p.w);
    return [[["半窗口 w", "Half-window w"], p.w + " s"], [["速度的方均根误差", "RMS speed error"], f(G.rms, 2) + " m/s"],
      [["位置误差造成的速度误差约", "Speed error from position noise, about"], f(2 * Math.SQRT2 / (2 * p.w), 2) + " m/s"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, blue = css("--blue"), mut = css("--muted"), red = css("--red");
    if (api.scene === "enc") {
      const E = enc31(p.n, p.meth);
      const G = api.graph({ x: 56, y: 26, w: w * 0.58 - 56, h: h - 80, xmin: 0.6, xmax: 3.4, ymin: 0.3, ymax: 1.3, xlabel: "t / s", ylabel: "v / (m/s)" }).axes();
      G.fn(vt31, mut, 3).pts(E.pts, blue, 1.5);
      G.text(api.T("灰：实际速度　蓝：由读数算出", "grey: true speed   blue: from readings"), 0.65, 1.25, mut, 11);
      // 右：误差与步长（双对数），当前步长用红点标出
      const lg = (v) => Math.log10(v), Z = api.graph({ x: w * 0.68, y: 26, w: w * 0.28, h: h * 0.55, xmin: 1, xmax: lg(600), ymin: -3, ymax: -1, ticks: false,
        xlabel: api.T("步长 h（对数）", "step h (log)"), ylabel: api.T("误差（对数）", "error (log)") }).axes();
      const curve = []; for (let n = 1; n <= 60; n++) curve.push([lg(n * 10), lg(Math.max(1e-4, enc31(n, p.meth).rms))]);
      Z.pts(curve, blue, 2).point(lg(p.n * 10), lg(Math.max(1e-4, E.rms)), red);
      [10, 100].forEach((v) => api.label(v + " ms", Z.X(lg(v)), Z.o.y + Z.o.h + 14, mut, 11, "center"));
      [0.001, 0.01, 0.1].forEach((v) => api.label(String(v), Z.o.x - 4, Z.Y(lg(v)) + 4, mut, 11, "right"));
      api.label(api.T("误差先随 h 减小、后随 h 增大", "the error first falls, then rises with h"), w * 0.66, h * 0.55 + 70, mut, 11);
      api.label(api.T("单位：m/s", "unit: m/s"), w * 0.66, h * 0.55 + 88, mut, 11);
      return;
    }
    if (api.scene === "bat") {
      const G = api.graph({ x: 56, y: 26, w: w - 90, h: h - 80, xmin: 0, xmax: T31, ymin: 0, ymax: 40, xlabel: "t / s", ylabel: "I / A" }).axes();
      const n = Math.floor(T31 / p.dt + 1e-9);
      if (p.rule) {
        api.ctx.fillStyle = "rgba(31,119,180,0.18)"; api.ctx.beginPath(); api.ctx.moveTo(G.X(0), G.Y(0));
        for (let i = 0; i <= n; i++) api.ctx.lineTo(G.X(i * p.dt), G.Y(I31(i * p.dt)));
        api.ctx.lineTo(G.X(n * p.dt), G.Y(0)); api.ctx.closePath(); api.ctx.fill();
        G.pts(Array.from({ length: n + 1 }, (_, i) => [i * p.dt, I31(i * p.dt)]), blue, 1.5);
      } else G.riemann(I31, 0, n * p.dt, n, "left");
      G.fn(I31, css("--ink"), 1.5).dots(Array.from({ length: n + 1 }, (_, i) => [i * p.dt, I31(i * p.dt)]), red, 3);
      G.text(api.T("黑：实际电流　红点：记录的采样值", "black: true current   red: logged samples"), 3, 38, mut, 11);
      return;
    }
    const Gp = gps31(p.w);
    const G = api.graph({ x: 56, y: 26, w: w - 90, h: h - 80, xmin: 20, xmax: 110, ymin: -1, ymax: 3, xlabel: "t / s", ylabel: "v / (m/s)" }).axes();
    G.fn(vw31, mut, 3).pts(Gp.pts, blue, 1.5);
    G.text(api.T("灰：实际步行速度　蓝：由 GPS 位置算出", "grey: true walking speed   blue: from GPS positions"), 22, 2.8, mut, 11);
    G.text(api.T("路口停下", "stopped at the crossing"), 58, -0.6, mut, 11);
  },
});

function check31(api) {
  const p = api.p;
  if (api.scene === "enc") { const E = enc31(p.n, p.meth); if (!p.meth && E.rms < 0.012) api.done("encF"); if (p.meth && E.rms < 0.0025) api.done("encC"); }
  if (api.scene === "bat") {
    const B = bat31(p.dt, p.rule);
    if (p.rule && Math.abs(B.err) <= 0.1 && p.dt === 2) api.done("batT");
    if (!p.rule && p.dt === 2) api.done("batL");
  }
  if (api.scene === "gps" && gps31(p.w).rms < 0.26) api.done("gps");
}
