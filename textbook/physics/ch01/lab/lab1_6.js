// 实验 1.6 单摆测重力加速度（配 1.6 节）。摆长 L 量到摆球顶端，真实摆长还要加上摆球半径 r（学生不知道，由截距看出）；
// 周期按任意摆角的精确公式 T = 4√(L/g) K(sin(θ₀/2)) 计算（K 用算术–几何平均求），秒表计时有约 0.1 s 的随机误差（人的反应）。
// 当地的 g 与正文算例不同。记录的数据放在闭包里，重置时不丢。随机误差用带种子的伪随机数，“清空记录”后重新播种，
// 所以同样的操作得到同样的数据（演示可复现）。任务“求出 g”按学生自己的数据拟合判定，不与真实值比较。
const G16 = 9.79, R16 = 0.015;
const rec16 = { pts: [] };                                      // [L, θ₀, t20]
function agm16(a, b) { for (let i = 0; i < 30; i++) { const a1 = (a + b) / 2; b = Math.sqrt(a * b); a = a1; } return a; }
const T16 = (L, th) => { const k = Math.sin(th * Math.PI / 360); return 2 * Math.PI * Math.sqrt((L + R16) / G16) / agm16(1, Math.sqrt(1 - k * k)); };
const rng16 = { s: 16 };
function u16() { rng16.s = (rng16.s * 1664525 + 1013904223) % 4294967296; return (rng16.s + 0.5) / 4294967296; }
function time16(L, th) {
  const gs = Math.sqrt(-2 * Math.log(u16())) * Math.cos(2 * Math.PI * u16());
  return Math.round((20 * T16(L, th) + 0.1 * gs) * 100) / 100;
}
function gfit16() {                                             // 小摆角数据的 T²–L 最小二乘斜率给出的 g
  const q = rec16.pts.filter((p) => p[1] <= 10);
  if (q.length < 2) return null;
  const n = q.length, mx = q.reduce((a, p) => a + p[0], 0) / n, my = q.reduce((a, p) => a + Math.pow(p[2] / 20, 2), 0) / n;
  let sxy = 0, sxx = 0;
  q.forEach((p) => { sxy += (p[0] - mx) * (Math.pow(p[2] / 20, 2) - my); sxx += (p[0] - mx) * (p[0] - mx); });
  return sxx > 0 ? 4 * Math.PI * Math.PI * sxx / sxy : null;
}
const distinct16 = () => new Set(rec16.pts.filter((p) => p[1] <= 10).map((p) => p[0].toFixed(2))).size;

WQ.lab({
  title: ["实验 1.6 单摆测重力加速度", "Lab 1.6 Measuring g with a pendulum"],
  goal: ["改变摆长，用秒表测 20 个周期，作 T²–L 图并用最小二乘法求 g 及其不确定度；再看摆角太大时会发生什么。",
         "Vary the length, time 20 periods, plot T² against L and find g with its uncertainty by least squares; then see what happens at large amplitude."],
  scenes: [
    { id: "lab", robot: true, name: ["标定加速度计用的 g", "g for calibrating an accelerometer"], hide: [],
      problem: { title: ["机器人问题：巡检机器人加速度计的标定", "Robot problem: calibrating an inspection robot's accelerometer"],
                 text: ["加速度计测的是比力，静止时读数的大小等于当地的 g。用单摆测出 g，作为标定的参考值。摆长用卷尺量到摆球顶端。",
                        "An accelerometer measures specific force; at rest its reading has the magnitude of the local g. Measure g with a pendulum as the reference. The length is measured to the top of the bob."] } },
    { id: "swing", name: ["秋千", "A swing"], hide: ["L", "ghat"],
      params: { amp: { value: 20 } },
      problem: { title: ["生活中的例子：秋千的周期", "Everyday example: the period of a swing"],
                 text: ["绳长 2.5 m 的秋千，测出它摆动 20 次的时间，与 2π√(L/g) 比较。", "Time 20 swings of a swing with 2.5 m ropes and compare with 2π√(L/g)."] } },
  ],
  params: [
    { id: "L", name: ["摆长 L（量到摆球顶端）", "Length L (to the top of the bob)"], min: 0.2, max: 1.2, step: 0.01, value: 0.5, unit: "m", digits: 2 },
    { id: "amp", name: ["摆角 θ₀", "Amplitude θ₀"], min: 3, max: 60, step: 1, value: 5, unit: "°", digits: 0 },
    { id: "ghat", name: ["你算出的 g", "Your g"], min: 9.3, max: 10.3, step: 0.005, value: 9.5, unit: "m/s²", digits: 3 },
  ],
  buttons: [{ id: "start", name: ["放开摆球并计时 20 个周期", "Release and time 20 periods"], primary: true }, { id: "reset", name: ["重置", "Reset"] },
            { id: "sweep", name: ["0.2–1.0 m 依次测一遍", "Measure 0.2–1.0 m in turn"] }, { id: "clear", name: ["清空记录", "Clear records"] }],
  legend: [{ color: "var(--blue)", name: ["记录的数据（θ₀ ≤ 10°）", "data (θ₀ ≤ 10°)"] }, { color: "var(--red)", name: ["大摆角的数据", "large-amplitude data"] }],
  tasks: [
    { id: "five", robot: true, text: ["摆角不超过 10°，至少测 5 个不同的摆长。", "With θ₀ ≤ 10°, measure at least 5 different lengths."],
      demo: { scene: "lab", set: { amp: 5 }, press: ["clear", "sweep"], wait: 1 } },
    { id: "g", robot: true, text: ["用自己记录的小摆角数据作 T²–L 图、拟合斜率求 g，把“你算出的 g”调到你的结果（与程序按同一组数据拟合的结果相差 0.5% 以内）。", "Plot your small-amplitude T² against L, fit the slope, find g and set “Your g” to your result (within 0.5% of the program's fit of the same data)."],
      demo: { scene: "lab", set: { amp: 5, ghat: 9.775 }, press: ["clear", "sweep"], wait: 1 } },
    { id: "big", robot: true, text: ["把摆角加大到 50° 以上测一次，周期比小摆角时长了多少？", "Measure once with θ₀ of 50° or more. How much longer is the period?"],
      demo: { scene: "lab", set: { amp: 55, L: 0.8 }, press: ["start"], wait: 7 } },
    { id: "swing", text: ["秋千：测出 20 次摆动的时间。", "Swing: time 20 swings."],
      demo: { scene: "swing", set: {}, press: ["start"], wait: 10 } },
  ],
  think: ["T²–L 直线的截距为什么不为零？由截距和斜率能求出什么？", "Why does the T²–L line not pass through the origin? What can you get from the intercept and the slope?"],

  reset(api, s) { s.t = 0; s.done = false; s.last = rec16.pts[rec16.pts.length - 1] || null; },
  update(dt, api, s) {
    const L = api.scene === "swing" ? 2.5 : api.p.L, T = T16(L, api.p.amp);
    s.t += dt * (s.t < 1.5 * T ? 1 : 30);                       // 先按真实速度摆一个半周期，其余快进
    s.theta = api.p.amp * Math.cos(2 * Math.PI * s.t / T);
    if (s.t >= 20 * T) {
      const t20 = time16(L, api.p.amp);
      if (api.scene === "lab") rec16.pts.push([L, api.p.amp, t20]);
      s.last = [L, api.p.amp, t20]; api.stop(); fin16(api, s);
    }
  },
  action(id, api, s) {
    if (api.scene !== "lab") return;
    if (id === "clear") { rec16.pts.length = 0; rng16.s = 16; }
    if (id === "sweep") for (let L = 0.2; L <= 1.0001; L += 0.1) rec16.pts.push([Math.round(L * 100) / 100, api.p.amp, time16(L, api.p.amp)]);
    s.last = rec16.pts[rec16.pts.length - 1] || null;
    fin16(api, s);
  },
  change(api, s, pid) { if (pid === "ghat") fin16(api, s); },
  readouts(api, s) {
    const f = api.fmt;
    const rows = [[["20 个周期的时间（秒表）", "Time for 20 periods"], s.last ? f(s.last[2], 2) + " s" : "—"],
                  [["周期 T = t₂₀/20", "Period T = t₂₀/20"], s.last ? f(s.last[2] / 20, 4) + " s" : "—"]];
    if (api.scene === "lab") rows.push([["已记录", "Recorded"], String(rec16.pts.length) + api.T(" 组", " runs")]);
    else rows.push([["2π√(L/g)（取 g = 9.8）", "2π√(L/g) with g = 9.8"], f(2 * Math.PI * Math.sqrt(2.5 / 9.8), 3) + " s"]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, swing = api.scene === "swing";
    const L = swing ? 2.5 : api.p.L, px = swing ? h * 0.3 : h * 0.6, cx = w * 0.2, cy = 20;
    const th = (s.theta == null ? api.p.amp : s.theta) * Math.PI / 180;
    const bx = cx + px * Math.sin(th), by = cy + px * Math.cos(th);
    api.line(cx - 50, cy, cx + 50, cy, css("--ink"), 4);
    api.line(cx, cy, bx, by, css("--ink"), 1.5);
    if (swing) api.rect(bx - 22, by - 4, 44, 8, css("--amber"), css("--ink"));
    else api.circle(bx, by + 8, 8, css("--muted"), css("--ink"));
    api.label(api.T(`摆长 ${L.toFixed(2)} m`, `L = ${L.toFixed(2)} m`), cx - 60, h * 0.9, css("--muted"), 12);
    if (swing) return;
    const P = api.plot(w * 0.45, 20, w * 0.5, h - 60, [{ pts: [], color: css("--blue") }],
                       { xmin: 0, xmax: 1.25, ymin: 0, ymax: 5.4, xlabel: "L / m", ylabel: "T² / s²" });
    rec16.pts.forEach((p) => api.circle(P.X(p[0]), P.Y(Math.pow(p[2] / 20, 2)), 4, p[1] > 10 ? css("--red") : css("--blue"), css("--ink")));
  },
});

function fin16(api, s) {
  if (distinct16() >= 5) api.done("five");
  const gf = gfit16();
  if (distinct16() >= 5 && gf && Math.abs(api.p.ghat - gf) / gf < 0.005) api.done("g");
  if (rec16.pts.some((p) => p[1] >= 50)) api.done("big");
  if (api.scene === "swing" && s.last) api.done("swing");
}
