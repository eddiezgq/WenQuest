// 实验 9.3 弹簧的功与动能定理（配 9.3 节）。测量型实验。
// 测弹簧场景：调压缩量 x，读测力计 F（读数带 ±0.25 N 以内的误差，由压缩量确定，修约到 0.1 N）；学生作 F–x 图拟合 k，提交。
// 弹射场景：把滑块压缩 x 后放开，弹簧推滑块，滑块离开弹簧后在导轨上滑过 0.30 m 到光电门；挡光片宽 20 mm，光电门读挡光时间 Δt（修约到 0.01 ms）。
// 导轨有很小的摩擦（μ 学生不知道）。学生由 v = 宽度/Δt 求动能，与 ½kx² 比较，提交到达光电门的能量占弹簧所做功的比例；
// 再选压缩量使滑块以 1.00 m/s 通过光电门。判定都用解析式算，不依赖动画是否放完。
// 弹珠台场景（生活中的例子）：已知柱塞弹簧 k = 400 N/m，球 80 g，台面倾角 6.5°，球道长 1.0 m；选压缩量使球刚好到达顶端。
const g93 = 9.81, K93 = 850, M93 = 0.40, MU93 = 0.04, D93 = 0.30, W93 = 0.020;      // 劲度 N/m、滑块 kg、导轨摩擦因数、到光电门的距离 m、挡光片宽 m
const KP93 = 400, MB93 = 0.080, TH93 = 6.5 * Math.PI / 180, LB93 = 1.0;
const RUN93 = {};                                                                   // 各压缩量是否已经弹射过（重置不清除）
function h93(a) { const x = Math.sin(a * 12.9898 + 4.1414) * 43758.5453; return x - Math.floor(x); }
const gauge93 = (xmm) => xmm <= 0 ? 0 : Math.round((K93 * xmm / 1000 + (h93(xmm) - 0.5) * 0.5) * 10) / 10;
const fric93 = MU93 * M93 * g93;
function vGate93(xmm) {                                                             // 到光电门时的速度（动能定理）
  const x = xmm / 1000, E = 0.5 * K93 * x * x - fric93 * (x + D93);
  return E > 0 ? Math.sqrt(2 * E / M93) : 0;
}
const dtGate93 = (xmm) => { const v = vGate93(xmm); return v > 0 ? Math.round(W93 / v * 1e5) / 100 : null; };   // ms，修约到 0.01 ms
const frac93 = (xmm) => { const x = xmm / 1000; return 0.5 * M93 * vGate93(xmm) ** 2 / (0.5 * K93 * x * x); };
const reach93 = (xmm) => { const x = xmm / 1000; return 0.5 * KP93 * x * x / (MB93 * g93 * Math.sin(TH93)); };      // 球从压缩位置起沿斜面能走多远（m），减去 x 即离开柱塞后的距离
function spring93(ctx, x0, x1, y, col) {                                            // 从 x0 到 x1 的弹簧（锯齿线）
  const n = 12, amp = 9; ctx.beginPath(); ctx.moveTo(x0, y);
  for (let i = 1; i < n; i++) ctx.lineTo(x0 + (x1 - x0) * i / n, y + (i % 2 ? -amp : amp));
  ctx.lineTo(x1, y); ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.stroke();
}

WQ.lab({
  title: ["实验 9.3 弹簧的功与动能定理", "Lab 9.3 Work done by a spring and the work–energy theorem"],
  goal: ["测出弹簧的劲度系数，用 ½kx² 算弹簧做的功；测出滑块被弹出后的速度，检验动能定理，找出摩擦消耗的那一部分。",
         "Measure the spring constant, compute the spring's work ½kx², time the launched slider and check the work–energy theorem, including what friction takes."],
  scenes: [
    { id: "gauge", robot: true, name: ["测弹簧", "Measure the spring"], hide: ["xl", "eta", "xp"],
      problem: { title: ["机器人问题：送料机构的推杆弹簧有多硬？", "Robot problem: how stiff is the feeder's push spring?"],
                 text: ["送料机构用一根压缩弹簧把零件推出去。先测弹簧：每次把它压缩一个 x，读测力计的示数 F，记下来。作 F–x 图，用最小二乘直线求劲度系数 k，调到“你测得的 k”，点“提交”。",
                        "A feeder pushes parts out with a compressed spring. First measure it: compress it by x, read the force gauge F, write it down. Plot F against x, fit a least-squares line for the spring constant k, set “Your k” and press “Submit”."] } },
    { id: "launch", robot: true, name: ["弹射滑块", "Launch the slider"], hide: ["x", "khat", "xp"],
      problem: { title: ["机器人问题：零件被推出时有多快？", "Robot problem: how fast does the part leave?"],
                 text: ["把滑块（0.40 kg）压缩 x 后放开。弹簧把它推出，滑块在导轨上滑 0.30 m 后通过光电门，挡光片宽 20 mm，读挡光时间 Δt。由 v = 0.020 m / Δt 算动能，与弹簧做的功 ½kx² 比较。",
                        "Compress the 0.40 kg slider by x and let go. The spring pushes it out; it slides 0.30 m along the rail to a light gate. The flag is 20 mm wide; read the blocking time Δt, find v = 0.020 m / Δt and compare the kinetic energy with the spring's work ½kx²."] } },
    { id: "life", name: ["弹珠台", "Pinball plunger"], hide: ["x", "khat", "xl", "eta"],
      problem: { title: ["生活中的例子：弹珠台的柱塞要拉多远", "Everyday example: how far to pull the pinball plunger"],
                 text: ["柱塞弹簧 k = 400 N/m，钢球 80 g，台面倾角 6.5°，球道长 1.0 m（不计摩擦）。拉多远，球刚好到达球道顶端？调压缩量，点“开始”，再点“提交”。",
                        "Plunger spring k = 400 N/m, an 80 g steel ball, a table tilted 6.5°, a 1.0 m lane (no friction). How far must you pull so the ball just reaches the top? Set the pull, press “Start”, then “Submit”."] } },
  ],
  params: [
    { id: "x", name: ["压缩量 x", "Compression x"], min: 0, max: 40, step: 1, value: 0, unit: "mm", digits: 0 },
    { id: "khat", name: ["你测得的 k", "Your k"], min: 200, max: 2000, step: 1, value: 200, unit: "N/m", digits: 0 },
    { id: "xl", name: ["压缩量 x", "Compression x"], min: 5, max: 40, step: 1, value: 20, unit: "mm", digits: 0 },
    { id: "eta", name: ["到达光电门的动能 / ½kx²", "Kinetic energy at the gate / ½kx²"], min: 0.5, max: 1.0, step: 0.001, value: 0.5, unit: "", digits: 3 },
    { id: "xp", name: ["柱塞压缩量", "Plunger pull"], min: 10, max: 40, step: 0.5, value: 15, unit: "mm", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--red)", name: ["弹簧力", "spring force"] }, { color: "var(--blue)", name: ["速度", "velocity"] }],
  tasks: [
    { id: "k", robot: true, text: ["测弹簧：测出劲度系数 k，提交（与真实值相差 2% 以内）。", "Measure the spring: find k and submit (within 2% of the true value)."],
      demo: { scene: "gauge", set: { x: 30, khat: 850 }, press: ["submit"], wait: 1 } },
    { id: "eta", robot: true, text: ["弹射滑块：压缩 30 mm 弹射，求到达光电门时的动能占 ½kx² 的比例，提交（相差 0.02 以内）。其余的能量到哪里去了？", "Launch: compress 30 mm, find the gate's kinetic energy as a fraction of ½kx², and submit (within 0.02). Where did the rest go?"],
      demo: { scene: "launch", set: { xl: 30, eta: 0.865 }, press: ["start", "submit"], wait: 2 } },
    { id: "v1", robot: true, text: ["弹射滑块：选压缩量，使滑块以 1.00 m/s 通过光电门（±0.04 m/s），弹射一次后提交。", "Launch: choose the compression that sends the slider through the gate at 1.00 m/s (±0.04 m/s); launch once, then submit."],
      demo: { scene: "launch", set: { xl: 24 }, press: ["start", "submit"], wait: 2 } },
    { id: "pin", text: ["弹珠台：选柱塞压缩量，使球刚好到达顶端（停在最后 10 cm 内或刚好到顶），提交。", "Pinball: choose the pull so the ball just reaches the top (stops in the last 10 cm or just gets there), and submit."],
      demo: { scene: "life", set: { xp: 21 }, press: ["start", "submit"], wait: 3 } },
  ],
  think: ["F–x 直线的截距为什么不是正好为零？弹簧做的功与 F–x 图下的面积是什么关系？滑块到光电门时少掉的动能，与导轨摩擦力做的功相等吗？",
          "Why is the intercept of the F–x line not exactly zero? How is the spring's work related to the area under the F–x graph? Does the kinetic energy missing at the gate equal the work done by rail friction?"],

  reset(api, s) { s.msg = s.msg || ""; s.pos = 0; s.v = 0; s.ran = false; s.at = null; s.done = false; },
  start(api, s) {
    s.ran = true; s.pos = 0; s.v = 0; s.done = false;
    if (api.scene === "launch") RUN93[api.p.xl] = true;
  },
  update(dt, api, s) {
    const p = api.p, n = 20, h = dt / n;
    if (api.scene === "launch") {
      const x = p.xl / 1000;
      for (let i = 0; i < n; i++) {
        const Fs = s.pos < x ? K93 * (x - s.pos) : 0, a = (Fs - (s.v > 0 || Fs > fric93 ? fric93 : 0)) / M93;
        s.v = Math.max(0, s.v + a * h); s.pos += s.v * h;
      }
      if (s.pos >= x + D93 + 0.1 || (s.v === 0 && s.pos > x)) { s.done = true; api.stop(); }
    }
    if (api.scene === "life") {
      const x = p.xp / 1000;
      for (let i = 0; i < n; i++) {
        const Fs = s.pos < x ? KP93 * (x - s.pos) : 0, a = Fs / MB93 - g93 * Math.sin(TH93);
        s.v += a * h; s.pos += s.v * h;
      }
      if (s.pos - x >= LB93) { s.pos = x + LB93; s.done = true; api.stop(); }
      if (s.v < 0 && s.pos > x) { s.done = true; api.stop(); }
    }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "gauge" && Math.abs(p.khat - K93) <= 0.02 * K93) { api.done("k"); ok = true; }
    if (api.scene === "launch" && RUN93[p.xl]) {
      if (p.xl === 30 && Math.abs(p.eta - frac93(30)) <= 0.02) { api.done("eta"); ok = true; }
      if (Math.abs(vGate93(p.xl) - 1.0) <= 0.04) { api.done("v1"); ok = true; }
    }
    if (api.scene === "life" && s.ran) { const r = reach93(p.xp) - p.xp / 1000; if (r >= LB93 - 0.10 && r <= LB93 + 0.03) { api.done("pin"); ok = true; } }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "gauge") return [[["压缩量 x", "Compression x"], f(p.x, 0) + " mm"], [["测力计示数 F", "Gauge reading F"], f(gauge93(p.x), 1) + " N"], sub];
    if (api.scene === "launch") {
      const x = p.xl / 1000, passed = s.ran && s.pos >= x + D93 + W93, t = dtGate93(p.xl);
      return [[["压缩量 x", "Compression x"], f(p.xl, 0) + " mm"],
        [["挡光时间 Δt", "Blocking time Δt"], passed ? (t ? f(t, 2) + " ms" : "—") : s.ran && s.done ? api.T("滑块没到光电门", "did not reach the gate") : "—"],
        [["滑块位置", "Slider position"], f(Math.max(0, s.pos - x) * 100, 1) + " cm"], sub];
    }
    const x = p.xp / 1000;
    return [[["柱塞压缩量", "Plunger pull"], f(p.xp, 1) + " mm"], [["球沿球道的距离", "Distance along the lane"], f(Math.max(0, s.pos - x) * 100, 1) + " cm"],
      [["球的速度", "Ball speed"], f(Math.max(0, s.v), 2) + " m/s"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ctx = api.ctx, f = api.fmt, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue");
    if (api.scene === "gauge" || api.scene === "launch") {
      const S = Math.min(w / 0.72, 1600), y = h * 0.55, x0 = w * 0.08;                // 画面像素 / m；墙在 x0
      const xc = api.scene === "gauge" ? p.x / 1000 : p.xl / 1000, L0 = 0.08;           // 弹簧自由长度 0.08 m
      const free = x0 + L0 * S;
      const front = api.scene === "gauge" ? free - xc * S : free - xc * S + Math.min(s.pos, xc) * S;
      const blk = api.scene === "gauge" ? front : free - xc * S + s.pos * S;
      api.rect(x0 - 10, y - 50, 10, 70, mut);
      api.line(x0, y + 20, w * 0.97, y + 20, ink, 2);
      spring93(ctx, x0, front, y - 12, red);
      api.rect(blk, y - 34, 0.05 * S, 54, css("--amber"), ink, 4);
      api.rect(blk + 0.05 * S * 0.4, y - 52, 3, 18, ink);                              // 挡光片
      if (api.scene === "gauge") {
        api.line(blk + 0.05 * S, y - 8, blk + 0.05 * S + 50, y - 8, ink, 3);
        api.rect(blk + 0.05 * S + 50, y - 30, 70, 44, css("--panel") || "#fff", ink, 6);
        api.label(f(gauge93(p.x), 1) + " N", blk + 0.05 * S + 85, y - 2, ink, 14, "center");
        api.label(api.T("测力计", "force gauge"), blk + 0.05 * S + 85, y - 40, mut, 12, "center");
        if (p.x > 0) api.arrow(blk + 0.05 * S + 46, y + 40, blk + 0.05 * S + 46 - Math.min(140, gauge93(p.x) * 3), y + 40, red, 2.5);
      } else {
        const gx = free + D93 * S;
        api.rect(gx - 4, y - 90, 8, 40, blue); api.rect(gx - 4, y - 20, 8, 12, blue);
        api.line(gx, y - 50, gx, y - 20, blue, 1, [3, 3]);
        api.label(api.T("光电门", "light gate"), gx, y - 98, blue, 12, "center");
        api.label(api.T("自由长度", "free length"), free, y + 42, mut, 11, "center"); api.line(free, y + 22, free, y + 30, mut, 1);
        if (s.v > 0) api.arrow(blk + 0.025 * S, y - 64, blk + 0.025 * S + Math.min(140, s.v * 70), y - 64, blue, 2.5);
      }
      api.label(api.T("x：压缩量", "x: compression"), x0 + 4, y + 62, mut, 12);
      return;
    }
    // 弹珠台：倾斜球道
    const ox = w * 0.1, oy = h * 0.82, Lpx = Math.min(w * 0.78, h * 0.7 / Math.sin(TH93 * 4)), th = TH93 * 4;   // 画面上把倾角画大 4 倍
    const ux = Math.cos(th), uy = -Math.sin(th), x = p.xp / 1000, sc = Lpx / (LB93 + 0.1);
    api.line(ox, oy, ox + ux * Lpx, oy + uy * Lpx, ink, 2);
    const top = 0.1 + LB93;
    api.line(ox + ux * top * sc - uy * 14, oy + uy * top * sc + ux * 14, ox + ux * top * sc + uy * 0, oy + uy * top * sc, mut, 2);
    const plunger = s.ran ? Math.max(0, Math.min(x, s.pos)) : 0, along = 0.1 - x + (s.ran ? s.pos : 0);
    spring93(ctx, ox, ox + ux * (0.1 - x + plunger) * sc, oy + uy * (0.1 - x + plunger) * sc - 10, red);
    api.circle(ox + ux * along * sc - uy * 0 + 0, oy + uy * along * sc - 12, 10, mut, ink);
    api.label(api.T("球道顶端", "top of the lane"), ox + ux * top * sc, oy + uy * top * sc - 22, mut, 12, "center");
    api.label(api.T("（倾角放大画出）", "(tilt drawn exaggerated)"), w * 0.5, h * 0.95, mut, 11, "center");
  },
});
