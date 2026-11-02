// 实验 15.1 卡文迪什扭秤测引力常量（配 15.1 节）。测量型实验。
// 装置（数值取卡文迪什 1798 年装置的量级）：小铅球 m = 0.73 kg，挂在轻杆两端，离悬丝 l = 0.93 m；大铅球 M = 158 kg，
// 放在小球旁边时两球心相距 r = 0.225 m。杆上的小镜子把光点反射到 D = 5.000 m 外的标尺上，光点位移 x = 2Dθ。
// 悬丝的扭转系数 κ = 2.50×10⁻⁴ N·m/rad（这根悬丝的值，学生不知道，由摆动周期求：T = 2π√(I/κ)，I = 2ml²）。
// 引力常量取真值 6.674 30×10⁻¹¹。只计每个小球与靠近它的大球之间的引力（远的那个大球的作用不计）。
// 点“开始”：大球从另一侧移到所选的一侧（t = 0），扭秤开始摆动，衰减时间 40 min；模拟 90 min。
// 扭秤原来并没有完全静止，还带着一点摆动（振幅和相位每次不同），所以 t = 0 时的读数不是原来的平衡位置。
// 标尺零点对应悬丝不扭转（没有大球时）的位置。
// 读数：拖动“读数时刻”，读那一时刻光点在标尺上的位置（±0.05 mm）。
const G151 = 6.6743e-11, m151 = 0.73, l151 = 0.93, M151 = 158, r151 = 0.225, D151 = 5.0, K151 = 2.5e-4, TAU151 = 40 * 60, TEND151 = 90;
const I151 = 2 * m151 * l151 * l151, W151 = Math.sqrt(K151 / I151);
const TH151 = 2 * (G151 * M151 * m151 / (r151 * r151)) * l151 / K151;          // 大球在一侧时的平衡偏转角
function h151(a) { const x = Math.sin(a * 23.177 + 0.61) * 43758.5453; return x - Math.floor(x); }
function spot151(side, tmin) {                                              // 光点位置（mm），side = ±1 为大球现在所在的一侧
  const t = tmin * 60, eq = side * TH151, th0 = -side * TH151, ph = 2 * Math.PI * h151(side + 5), a1 = 0.5 * TH151 * (0.5 + h151(side + 9));
  const th = eq + Math.exp(-t / TAU151) * ((th0 - eq) * Math.cos(W151 * t) + a1 * Math.sin(W151 * t + ph));
  return 2 * D151 * th * 1000;
}
const RUN151 = {};

WQ.lab({
  title: ["实验 15.1 卡文迪什扭秤测引力常量", "Lab 15.1 Measuring G with Cavendish's torsion balance"],
  goal: ["由扭秤的摆动周期求悬丝的扭转系数，由大球在两侧时光点平衡位置之差求偏转角，算出引力常量，再“称”出地球的质量和平均密度。",
         "From the balance's swing period find the fibre's torsion constant; from the shift of the light spot's rest position between the two ball positions find the deflection; compute G, then “weigh” the Earth."],
  scenes: [
    { id: "balance", name: ["扭秤", "Torsion balance"], hide: [],
      problem: { title: ["生活中的例子：怎样“称”出地球有多重？", "Everyday example: how do you weigh the Earth?"],
                 text: ["由 g = GM/R² 求地球的质量，要先知道 G。实验室里两个铅球之间的引力只有约 10⁻⁷ N，要用极细的悬丝做成扭秤才测得出。小球 0.73 kg，离悬丝 0.93 m；大球 158 kg，两球心相距 0.225 m；标尺离镜子 5.000 m。选大球移到哪一侧，点“开始”，拖动“读数时刻”读光点位置。",
                        "To get the Earth's mass from g = GM/R² you first need G. The pull between two lead balls in a lab is only about 10⁻⁷ N, so a balance on a very fine fibre is needed. Small balls 0.73 kg, 0.93 m from the fibre; large balls 158 kg, centre distance 0.225 m; scale 5.000 m from the mirror. Choose the side to move the large balls to, press “Start”, and drag “Read time” to read the spot position."] } },
  ],
  params: [
    { id: "side", name: ["大球移到：−1 左侧，1 右侧", "Move large balls to: −1 left, 1 right"], min: -1, max: 1, step: 2, value: 1, unit: "", digits: 0 },
    { id: "tr", name: ["读数时刻", "Read time"], min: 0, max: 90, step: 0.1, value: 0, unit: "min", digits: 1 },
    { id: "ans", name: ["你的结果", "Your result"], min: 0, max: 10, step: 0.001, value: 0, unit: "", digits: 3 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "kappa", text: ["由摆动周期求悬丝的扭转系数 κ（以 10⁻⁴ N·m/rad 为单位），调到“你的结果”，提交（相差 3% 以内）。", "From the swing period find the torsion constant κ in units of 10⁻⁴ N·m/rad, set it as “Your result” and submit (within 3%)."],
      demo: { scene: "balance", set: { side: 1, ans: 2.5 }, press: ["start", "submit"], wait: 2 } },
    { id: "theta", text: ["由光点的平衡位置求大球引起的偏转角 θ（mrad），提交（相差 3% 以内；标尺零点对应悬丝不扭转）。", "From the spot's rest position find the deflection θ caused by the large balls (mrad) and submit (within 3%; the scale zero is the untwisted position)."],
      demo: { scene: "balance", set: { side: -1, ans: 1.131 }, press: ["start", "submit"], wait: 2 } },
    { id: "G", text: ["由 κ 和 θ 求引力常量 G（以 10⁻¹¹ N·m²/kg² 为单位），提交（相差 3% 以内），再求地球的平均密度。", "From κ and θ find G in units of 10⁻¹¹ N·m²/kg², submit (within 3%), then find the Earth's mean density."],
      demo: { scene: "balance", set: { side: 1, ans: 6.674 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["两个大球对小球的引力只相当于小球重量的约一亿分之二，为什么扭秤能测出来？悬丝越细越好吗？如果不计远处那个大球的引力，结果偏大还是偏小？",
          "The pull is only about two hundred-millionths of the small ball's weight: why can the balance detect it? Is a thinner fibre always better? Neglecting the far large ball, is the result too big or too small?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; },
  start(api, s) { s.ran = true; s.k = Object.assign({}, api.p); },
  update(dt, api, s) { if (api.t >= 6) { RUN151[api.p.side] = true; api.stop(); } },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = s.ran && s.k ? Object.assign({}, s.k, { ans: api.p.ans }) : api.p, have = s.ran || RUN151[p.side]; let ok = false;
    if (have && Math.abs(p.ans - K151 * 1e4) <= 0.03 * K151 * 1e4) { api.done("kappa"); ok = true; }
    if (have && Math.abs(p.ans - TH151 * 1e3) <= 0.03 * TH151 * 1e3) { api.done("theta"); ok = true; }
    if (have && Math.abs(p.ans - G151 * 1e11) <= 0.03 * G151 * 1e11) { api.done("G"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"], have = (s.ran && !api.running) || RUN151[p.side];
    const shown = s.ran && api.running ? api.t / 6 * TEND151 : (have ? TEND151 : 0);
    const x = spot151(p.side, p.tr) + (h151(p.tr * 10 + p.side) - 0.5) * 0.1;
    return [[[`t = ${f(p.tr, 1)} min 时光点的位置`, `Spot position at t = ${f(p.tr, 1)} min`], have || (s.ran && p.tr <= shown) ? f(x, 2) + " mm" : "—"],
            [["已做过的一侧", "Sides done"], [RUN151[-1] ? api.T("左", "left") : "", RUN151[1] ? api.T("右", "right") : ""].filter(Boolean).join("、") || "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue"), p = api.p;
    const shown = s.ran && api.running ? api.t / 6 * TEND151 : ((s.ran || RUN151[p.side]) ? TEND151 : 0);
    // 左：俯视的扭秤
    const cx = w * 0.18, cy = h * 0.45, L = Math.min(w * 0.13, h * 0.3), th = shown > 0 ? spot151(p.side, shown) / (2 * D151 * 1000) * 120 : -p.side * TH151 * 120;   // 转角放大画出
    const ux = Math.cos(th), uy = Math.sin(th);
    api.line(cx - ux * L, cy - uy * L, cx + ux * L, cy + uy * L, ink, 3);
    api.circle(cx - ux * L, cy - uy * L, 7, blue, ink); api.circle(cx + ux * L, cy + uy * L, 7, blue, ink);
    api.circle(cx, cy, 3, ink, ink);
    const sd = shown > 0 ? p.side : -p.side;
    api.circle(cx + L, cy + sd * 26, 16, mut, ink); api.circle(cx - L, cy - sd * 26, 16, mut, ink);
    api.label(api.T("俯视（转角放大）", "top view (angle enlarged)"), cx, cy + L + 40, mut, 12, "center");
    // 右：光点位置随时间
    const G = api.graph({ x: w * 0.4, y: h * 0.1, w: w * 0.55, h: h * 0.72, xmin: 0, xmax: TEND151, ymin: -50, ymax: 50,
                          xlabel: "t / min", ylabel: api.T("光点位置 / mm", "spot / mm") }).axes();
    if (shown > 0) { const pts = []; for (let k = 0; k <= 600; k++) { const t = shown * k / 600; pts.push([t, spot151(p.side, t)]); } G.pts(pts, red, 1.6); }
    G.vline(p.tr, ink);
  },
});
