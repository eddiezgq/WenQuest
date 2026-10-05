// 实验 4.5 频闪照片测重力加速度（配 4.5 节）。测量型实验。
// 频闪场景：小球在 1.0 m 高的视野中下落，频闪频率 f 由学生选；第一次闪光时小球已下落了一小段时间（随 f 变化的伪随机值）。
// 每个像的读数带 ±1 mm 以内的误差并修约到 1 mm（按 f 和序号确定的伪随机数，同一个 f 读数不变）。学生拟合 y = y₀ + v₀t + ½gt²
// 求 g 和扩展不确定度 U = 2u(g)，一起提交；与“按这组读数拟合”的结果比较：g 相差不超过 u，U 相差不超过 30%。拟合结果不显示。
// 任务 2 还要求所选频率下 U < 0.03 m/s²。
// 落体比较场景：钢球（d = 20 mm）与乒乓球（d = 40 mm、2.7 g）从高度 H 落下，二次方阻力（C_d = 0.47），按“自由落体”由下落时间
// 算出的“表观 g”。水滴场景：调水龙头的滴水频率，使一滴落到盆底的同时下一滴恰好离开龙头，由 g = 2H·f² 求 g；画面只给出
// 同步提示，g 由学生自己算。
const G45 = 9.803;                                                // 当地的 g（学生不知道）
function hash45(a, b) { const x = Math.sin(a * 12.9898 + b * 78.233 + 7.77) * 43758.5453; return x - Math.floor(x); }
function data45(f) {
  const t0 = 0.03 + 0.05 * hash45(f, 0.5), pts = [];
  for (let k = 0; ; k++) {
    const t = k / f, y = 0.5 * G45 * (t + t0) ** 2 - 0.5 * G45 * t0 * t0;
    if (y > 1.0) break;
    pts.push([t, Math.round((y + 0.001 * (hash45(f, k + 1) - 0.5)) * 1000) / 1000]);   // ±0.5 mm 再修约：总误差在 ±1 mm 以内
  }
  return pts;
}
function fit45(pts) {                                             // 最小二乘：y = c0 + c1 t + c2 t²/2，返回 g 与 u(g)
  const n = pts.length, A = pts.map(([t]) => [1, t, t * t / 2]), y = pts.map((q) => q[1]);
  const M = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], b = [0, 0, 0];
  A.forEach((r, i) => { for (let j = 0; j < 3; j++) { b[j] += r[j] * y[i]; for (let k = 0; k < 3; k++) M[j][k] += r[j] * r[k]; } });
  const inv = inv3(M), c = [0, 1, 2].map((j) => inv[j][0] * b[0] + inv[j][1] * b[1] + inv[j][2] * b[2]);
  let ss = 0; A.forEach((r, i) => { ss += (y[i] - r[0] * c[0] - r[1] * c[1] - r[2] * c[2]) ** 2; });
  const s2 = ss / Math.max(1, n - 3);
  return { c, g: c[2], u: Math.sqrt(s2 * inv[2][2]), n };
}
function inv3(m) {
  const [a, b, c] = m[0], [d, e, f] = m[1], [g, h, i] = m[2];
  const A = e * i - f * h, B = -(d * i - f * g), C = d * h - e * g, det = a * A + b * B + c * C;
  return [[A / det, -(b * i - c * h) / det, (b * f - c * e) / det], [B / det, (a * i - c * g) / det, -(a * f - c * d) / det], [C / det, -(a * h - b * g) / det, (a * e - b * d) / det]];
}
function drop45(H, ball) {                                        // 二次方阻力下从 H 落下的时间，RK4
  const m = ball ? 0.0027 : 7850 * Math.PI / 6 * 0.02 ** 3, dia = ball ? 0.04 : 0.02;
  const k = 0.5 * 1.2 * 0.47 * Math.PI * dia * dia / 4 / m, acc = (v) => 9.81 - k * v * Math.abs(v);
  let y = 0, v = 0, t = 0; const dt = 0.0005;
  while (y < H) {
    const k1v = acc(v), k1y = v, k2v = acc(v + k1v * dt / 2), k2y = v + k1v * dt / 2, k3v = acc(v + k2v * dt / 2), k3y = v + k2v * dt / 2, k4v = acc(v + k3v * dt), k4y = v + k3v * dt;
    const yn = y + dt * (k1y + 2 * k2y + 2 * k3y + k4y) / 6;
    if (yn >= H) { t += dt * (H - y) / (yn - y); break; }
    v += dt * (k1v + 2 * k2v + 2 * k3v + k4v) / 6; y = yn; t += dt;
  }
  return { t, gapp: 2 * H / (t * t) };
}
const HDRIP45 = 0.80, fdrip45 = () => 1 / Math.sqrt(2 * HDRIP45 / G45);   // 水滴：落差 0.80 m，下落时间的倒数

WQ.lab({
  title: ["实验 4.5 频闪照片测重力加速度", "Lab 4.5 Measuring g with strobe photos"],
  goal: ["读出频闪照片上小球的位置，拟合求 g 及其不确定度；看空气阻力何时不能忽略；用水滴测 g。",
         "Read the ball's positions on strobe photos and fit g with its uncertainty; see when air drag matters; measure g with water drops."],
  scenes: [
    { id: "strobe", robot: true, name: ["频闪照片", "Strobe photo"], hide: ["H", "ball", "fd", "gd"],
      problem: { title: ["机器人问题：标定加速度计之前，先测出当地的 g", "Robot problem: measure the local g before calibrating an accelerometer"],
                 text: ["巡检机器人的加速度计要用当地的 g 标定。让小球在 1 m 高的视野里下落，频闪灯每秒闪 f 次，表中是从照片上读出的每个像的位置（读到 1 mm，误差在 ±1 mm 以内）。拟合求 g 和扩展不确定度 U，调到滑块上，点“提交”。",
                        "The robot's accelerometer is calibrated against the local g. A ball falls through a 1 m field of view under a strobe flashing f times a second; the table lists each image read off the photo (to 1 mm, error within ±1 mm). Fit g and its expanded uncertainty U, set them and press “Submit”."] } },
    { id: "drag", name: ["钢球与乒乓球", "Steel ball and table-tennis ball"], hide: ["f", "ghat", "Uhat", "fd", "gd"],
      problem: { title: ["什么时候可以不计空气阻力", "When can air drag be ignored"],
                 text: ["钢球和乒乓球从高度 H 同时落下。按自由落体公式由下落时间算出“表观 g” = 2H/t²。改变高度，看乒乓球的表观 g 怎样偏离。",
                        "A steel ball and a table-tennis ball are dropped together from height H. The “apparent g” = 2H/t² is computed from the fall time as if there were no drag. Change H and watch the table-tennis ball's apparent g drift."] } },
    { id: "drip", name: ["水龙头的水滴", "Dripping tap"], hide: ["f", "ghat", "Uhat", "H", "ball"],
      problem: { title: ["生活中的例子：用水滴测 g", "Everyday example: measuring g with drops"],
                 text: ["水龙头离盆底 0.80 m。点“开始”，调节滴水的快慢，使一滴落到盆底“嗒”的一声时，下一滴恰好离开龙头。这时滴水的间隔就是下落时间，由 H = ½gt² 算出 g，调到滑块上，提交。",
                        "The tap is 0.80 m above the basin. Press “Start” and adjust the dripping so that each drop hits the basin just as the next one leaves the tap. Then the interval equals the fall time; work out g from H = ½gt², set it and submit."] } },
  ],
  params: [
    { id: "f", name: ["频闪频率 f", "Strobe frequency f"], min: 10, max: 60, step: 5, value: 20, unit: "Hz", digits: 0 },
    { id: "ghat", name: ["你测得的 g", "Your g"], min: 9.5, max: 10.1, step: 0.001, value: 9.5, unit: "m/s²", digits: 3 },
    { id: "Uhat", name: ["你算出的扩展不确定度 U（k = 2）", "Your expanded uncertainty U (k = 2)"], min: 0.005, max: 0.2, step: 0.001, value: 0.1, unit: "m/s²", digits: 3 },
    { id: "H", name: ["下落高度 H", "Drop height H"], min: 0.5, max: 10, step: 0.5, value: 3.0, unit: "m", digits: 1 },
    { id: "ball", name: ["看哪个球：0 钢球，1 乒乓球", "Ball: 0 steel, 1 table-tennis"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "fd", name: ["每秒滴几滴 f", "Drops per second f"], min: 1.5, max: 3.5, step: 0.01, value: 2.0, unit: "Hz", digits: 2 },
    { id: "gd", name: ["你算出的 g（水滴）", "Your g (drops)"], min: 9.0, max: 10.6, step: 0.01, value: 9.0, unit: "m/s²", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "g1", robot: true, text: ["频闪：选一个频率，拟合求 g 和 U，提交（g 与这组读数的拟合结果相差不超过标准不确定度，U 相差不超过 30%）。", "Strobe: pick a frequency, fit g and U, and submit (g within one standard uncertainty of the fit to those readings, U within 30%)."],
      demo: { scene: "strobe", set: { f: 20, ghat: 9.795, Uhat: 0.051 }, press: ["submit"], wait: 1 } },
    { id: "g2", robot: true, text: ["频闪：找一个频率，使扩展不确定度 U 小于 0.03 m/s²，按这个频率的读数拟合，提交 g 和 U。频率越高越好吗？", "Strobe: find a frequency at which the expanded uncertainty U is below 0.03 m/s², fit those readings and submit g and U. Is a higher frequency always better?"],
      demo: { scene: "strobe", set: { f: 45, ghat: 9.798, Uhat: 0.021 }, press: ["submit"], wait: 1 } },
    { id: "drag", text: ["落体：找出乒乓球的表观 g 仍在 9.81 m/s² 的 5% 以内的最大高度（0.5 m 一档），提交。钢球呢？", "Drop: find the largest height (in 0.5 m steps) at which the table-tennis ball's apparent g is still within 5% of 9.81 m/s², and submit. What about the steel ball?"],
      demo: { scene: "drag", set: { ball: 1, H: 1.0 }, press: ["submit"], wait: 1 } },
    { id: "drip", text: ["水滴：调到“落地声与下一滴离开同时”，算出 g，提交（与按你的滴水频率算出的值相差 0.05 m/s² 以内，且与当地 g 相差 1.5% 以内）。", "Drops: tune the tap until the splash and the next drop coincide, compute g and submit (within 0.05 m/s² of the value from your drip rate, and within 1.5% of the local g)."],
      demo: { scene: "drip", set: { fd: 2.47, gd: 9.76 }, press: ["submit"], wait: 1 } },
  ],
  think: ["频闪频率加倍，读数个数约加倍，g 的不确定度大约减小多少？为什么照片上像太密时反而难读？乒乓球的表观 g 为什么总是偏小？",
          "Doubling the strobe frequency roughly doubles the number of readings: how much does the uncertainty of g shrink? Why are photos with crowded images harder to read? Why is the table-tennis ball's apparent g always too small?"],

  reset(api, s) {},
  change(api, s, pid) { s.msg = ""; },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "strobe") {
      const F = fit45(data45(p.f)), near = Math.abs(p.ghat - F.g) <= Math.max(F.u, 0.005) && Math.abs(p.Uhat - 2 * F.u) <= 0.3 * 2 * F.u;
      if (near) { api.done("g1"); ok = true; if (2 * F.u < 0.03) api.done("g2"); }
    }
    if (api.scene === "drag" && p.ball === 1) {
      const okH = (H) => Math.abs(drop45(H, 1).gapp - 9.81) / 9.81 <= 0.05;
      if (okH(p.H) && !okH(p.H + 0.5)) { api.done("drag"); ok = true; }
    }
    if (api.scene === "drip") {
      const match = Math.abs(p.fd - fdrip45()) / fdrip45() < 0.01, gd = 2 * HDRIP45 * p.fd * p.fd;
      if (match && Math.abs(p.gd - gd) <= 0.05 && Math.abs(p.gd - G45) / G45 < 0.015) { api.done("drip"); ok = true; }
    }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "strobe") {
      const D = data45(p.f), F = fit45(D);
      return [[["像的个数", "Images"], String(D.length)], [["相邻两像的时间间隔", "Interval between images"], f(1000 / p.f, 1) + " ms"],
        [["你提交的", "Your result"], `g = ${f(p.ghat, 3)}, U = ${f(p.Uhat, 3)} m/s²`], sub];
    }
    if (api.scene === "drag") {
      const A = drop45(p.H, 0), B = drop45(p.H, 1), t0 = Math.sqrt(2 * p.H / 9.81);
      return [[["自由落体的时间", "Free-fall time"], f(t0, 3) + " s"], [["钢球：时间、表观 g", "Steel: time, apparent g"], `${f(A.t, 3)} s, ${f(A.gapp, 2)} m/s²`],
        [["乒乓球：时间、表观 g", "Table-tennis: time, apparent g"], `${f(B.t, 3)} s, ${f(B.gapp, 2)} m/s²`], sub];
    }
    const tf = Math.sqrt(2 * HDRIP45 / G45), off = 1 / p.fd - tf;
    return [[["滴水间隔 1/f", "Interval 1/f"], f(1000 / p.fd, 0) + " ms"], [["落地声与下一滴离开", "Splash vs next drop"],
      Math.abs(off) < 0.004 ? api.T("几乎同时", "almost together") : off > 0 ? api.T("落地声在前", "splash first") : api.T("下一滴先离开", "next drop first")],
      [["你算出的 g", "Your g"], f(p.gd, 2) + " m/s²"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, blue = css("--blue"), mut = css("--muted"), ink = css("--ink"), red = css("--red");
    if (api.scene === "strobe") {
      const D = data45(p.f), topY = 24, H = h - 60, sc = H / 1.02, x0 = 70;
      api.rect(x0 - 40, topY - 8, 110, H + 16, "#10161b");
      for (let mm = 0; mm <= 1000; mm += 10) { const yy = topY + mm / 1000 * sc, L = mm % 100 === 0 ? 14 : mm % 50 === 0 ? 9 : 5;
        api.line(x0 + 40, yy, x0 + 40 + L, yy, "#c8d0d4", 1); if (mm % 100 === 0) api.label(String(mm / 10), x0 + 58, yy + 4, "#c8d0d4", 10); }
      D.forEach(([, y]) => api.circle(x0, topY + y * sc, 5, "#f2f4f5"));
      api.label("cm", x0 + 50, topY - 12, mut, 10);
      api.label(api.T("频闪照片（示意）", "strobe photo (sketch)"), x0 - 36, h - 14, mut, 11);
      const cx = w * 0.36; api.label(api.T("k　t / s　　y / mm（读数）", "k   t / s     y / mm (reading)"), cx, 20, mut, 12);
      const lines = Math.max(1, Math.ceil(D.length / 20));
      D.forEach(([t, y], i) => { const col = Math.floor(i / 20), row = i % 20;
        api.label(`${i}　${t.toFixed(4)}　${Math.round(y * 1000)}`, cx + col * 190, 40 + row * 17, ink, 12); });
      if (lines > 1) api.label(api.T("（读数分两列）", "(two columns)"), cx, 40 + 20 * 17 + 6, mut, 11);
      return;
    }
    if (api.scene === "drag") {
      const A = drop45(p.H, 0), B = drop45(p.H, 1);
      const G = api.graph({ x: 70, y: 24, w: w - 110, h: h - 80, xmin: 0.5, xmax: 10, ymin: 6.4, ymax: 10.0, xlabel: api.T("下落高度 H / m", "drop height H / m"), ylabel: api.T("表观 g / (m/s²)", "apparent g / (m/s²)") }).axes();
      const hs = []; for (let H = 0.5; H <= 10.001; H += 0.25) hs.push(H);
      G.pts(hs.map((H) => [H, drop45(H, 0).gapp]), ink, 2).pts(hs.map((H) => [H, drop45(H, 1).gapp]), red, 2).hline(9.81).hline(9.81 * 0.95, mut, [2, 4]);
      G.point(p.H, p.ball ? B.gapp : A.gapp, p.ball ? red : ink);
      G.text(api.T("黑：钢球　红：乒乓球　虚线：9.81 与低 5%", "black: steel  red: table-tennis  dashed: 9.81 and 5% below"), 2.0, 6.7, mut, 11);
      return;
    }
    const tf = Math.sqrt(2 * HDRIP45 / G45), per = 1 / p.fd, tx = w * 0.3, ty = 50, by = h - 50, sc = (by - ty) / HDRIP45;
    api.rect(tx - 40, ty - 24, 60, 14, mut); api.rect(tx - 6, ty - 12, 12, 12, mut);
    api.rect(tx - 70, by, 140, 18, "#9fb8d9");
    for (let k = 0; k < 6; k++) { const age = ((api.t || 0) % per) + k * per; if (age > tf + 0.05) continue;
      const y = Math.min(HDRIP45, 0.5 * G45 * age * age); api.circle(tx, ty + y * sc, 4, blue); }
    api.label(api.T("点“开始”看水滴下落", "press Start to watch the drops"), w * 0.5, 60, mut, 12);
    api.label(api.T("右边“测量”栏告诉你落地声与下一滴离开的先后", "the readout tells you which comes first: splash or next drop"), w * 0.5, 82, mut, 12);
  },
  update(dt, api, s) {},
});
