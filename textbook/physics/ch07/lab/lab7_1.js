// 实验 7.1 斜面测摩擦因数（配 7.1 节）。测量型实验。
// 抬斜面场景：三种材料（摩擦因数学生不知道）；学生调倾角，盒子在 tan θ > μ_s 时滑动，读出刚开始滑动的倾角，求 μ_s，提交。
// 下滑场景：固定倾角和长度，点“开始”放手，盒子滑下；计时读数在放手时就生成：秒表带 ±0.04 s 以内的人手误差（修约到 0.01 s），
// 光电门带 ±0.5 ms 以内的误差（修约到 1 ms）；误差由设置和第几次测量确定（伪随机），同一设置下的各次读数都记在表里。
// 学生由 L、t、θ 算 μ_k，提交。判定：光电门——与真实值相差 0.01 以内；秒表——同一设置至少 5 次，按平均时间算出的值相差 0.005 以内。
// 滑梯场景：孩子被轻推一下沿滑梯下滑，调倾角使他匀速滑下（tan θ = μ_k），提交时判定 |a| ≤ 0.1 m/s²。
const g71 = 9.81;
const MAT71 = [
  { n: ["塑料零件盒—铝板", "plastic tote on aluminium"], s: 0.52, k: 0.41 },
  { n: ["硅胶指垫—铝板", "silicone pad on aluminium"], s: 0.78, k: 0.63 },
  { n: ["钢块—涂油钢板", "steel block on oiled steel"], s: 0.165, k: 0.112 },
];
const KIDK71 = 0.30, SLIDE71 = 3.0;
const REC71 = {}, SEEN71 = {};                                      // 各设置下的计时记录；各材料是否已看到“开始滑动”（重置不清除）
function h71(a, b) { const x = Math.sin(a * 12.9898 + b * 78.233 + 3.21) * 43758.5453; return x - Math.floor(x); }
const key71 = (p) => `${p.mat}|${p.th2}|${p.L}|${p.timer}`;
const acc71 = (th, mk) => g71 * (Math.sin(th) - mk * Math.cos(th));
const rad71 = (d) => d * Math.PI / 180;
function slides71(p) { const m = MAT71[p.mat]; return Math.tan(rad71(p.th2)) > m.s && acc71(rad71(p.th2), m.k) > 0; }
function reading71(p, k) {                                           // 第 k 次（从 0 起）测量的计时读数
  const m = MAT71[p.mat], t = Math.sqrt(2 * p.L / acc71(rad71(p.th2), m.k)), u = h71(k + 1 + 10 * p.timer, p.mat * 100 + p.th2 + p.L * 7);
  return p.timer ? Math.round((t + (u - 0.5) * 0.001) * 1000) / 1000 : Math.round((t + (u - 0.5) * 0.08) * 100) / 100;
}
const mukOf71 = (L, t, thd) => (g71 * Math.sin(rad71(thd)) - 2 * L / (t * t)) / (g71 * Math.cos(rad71(thd)));
function poly71(ctx, pts, fill, stroke) {
  ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1.5; ctx.stroke(); }
}

WQ.lab({
  title: ["实验 7.1 斜面测摩擦因数", "Lab 7.1 Measuring friction coefficients on an incline"],
  goal: ["用摩擦角测静摩擦因数，用下滑时间测动摩擦因数；比较秒表与光电门，体会计时误差怎样传到结果里。",
         "Measure the static coefficient from the angle of friction and the kinetic one from the sliding time; compare a stopwatch with light gates and see how timing errors reach the result."],
  scenes: [
    { id: "tilt", robot: true, name: ["抬高斜面", "Raise the incline"], hide: ["th2", "L", "timer", "mkhat", "ths"],
      problem: { title: ["机器人问题：夹爪的指垫与零件之间 μ_s 多大？", "Robot problem: what is μ_s between a gripper pad and a part?"],
                 text: ["按式 (7.1.5) 计算夹紧力，先要知道摩擦因数。把零件放在可调倾角的板上，慢慢抬高，读出刚开始滑动的倾角 θ_c，由 tan θ_c = μ_s 求 μ_s，调到滑块上，点“提交”。",
                        "Eq. (7.1.5) needs the friction coefficient. Put the part on a tilting plate, raise it slowly, read the angle θ_c at which it starts to slide, find μ_s = tan θ_c, set it and press “Submit”."] } },
    { id: "slide", robot: true, name: ["测下滑时间", "Time the slide"], hide: ["th", "mshat", "ths"],
      problem: { title: ["机器人问题：滑动时的 μ_k 多大？", "Robot problem: what is μ_k while sliding?"],
                 text: ["倾角大于摩擦角时零件加速滑下。点“开始”放手，读出滑过长度 L 的时间 t，由 a = 2L/t² 和式 (7.1.4) 求 μ_k。可以多测几次，比较秒表与光电门。",
                        "Above the angle of friction the part accelerates down. Press “Start” to release it, read the time t over length L, and get μ_k from a = 2L/t² and Eq. (7.1.4). Repeat as often as you like and compare the stopwatch with light gates."] } },
    { id: "life", name: ["滑梯", "Playground slide"], hide: ["th", "mat", "mshat", "th2", "L", "timer", "mkhat"],
      problem: { title: ["生活中的例子：滑梯多陡才能匀速滑下", "Everyday example: how steep for a steady ride"],
                 text: ["孩子坐在滑梯顶上，大人轻推一下。滑梯太平，孩子滑一段就停；太陡，越滑越快。调倾角，使孩子匀速滑下，点“提交”。",
                        "A child at the top of the slide gets a gentle push. Too shallow and the child stops; too steep and the child speeds up. Adjust the angle for a steady ride and press “Submit”."] } },
  ],
  params: [
    { id: "mat", name: ["材料", "Materials"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "th", name: ["斜面倾角 θ", "Incline angle θ"], min: 0, max: 45, step: 0.5, value: 10, unit: "°", digits: 1 },
    { id: "mshat", name: ["你测得的 μ_s", "Your μ_s"], min: 0.05, max: 1.0, step: 0.001, value: 0.05, unit: "", digits: 3 },
    { id: "th2", name: ["斜面倾角 θ", "Incline angle θ"], min: 20, max: 50, step: 1, value: 35, unit: "°", digits: 0 },
    { id: "L", name: ["滑过的长度 L", "Sliding length L"], min: 0.3, max: 1.2, step: 0.1, value: 0.6, unit: "m", digits: 1 },
    { id: "timer", name: ["计时：0 秒表，1 光电门", "Timer: 0 stopwatch, 1 light gates"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "mkhat", name: ["你测得的 μ_k", "Your μ_k"], min: 0.05, max: 1.0, step: 0.001, value: 0.05, unit: "", digits: 3 },
    { id: "ths", name: ["滑梯倾角", "Slide angle"], min: 10, max: 30, step: 0.5, value: 25, unit: "°", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--red)", name: ["摩擦力", "friction"] }, { color: "var(--blue)", name: ["重力沿斜面的分量", "weight along the incline"] }],
  tasks: [
    { id: "ms", robot: true, text: ["抬高斜面：选一种材料，测出 μ_s，提交（误差不超过倾角读数 0.5° 所对应的范围）。", "Raise the incline: pick a material, measure μ_s and submit (within what a 0.5° angle reading allows)."],
      demo: { scene: "tilt", set: { mat: 0, th: 28, mshat: 0.52 }, press: ["submit"], wait: 1 } },
    { id: "gate", robot: true, text: ["测下滑时间：用光电门测出 μ_k，提交（与真实值相差 0.01 以内）。", "Time the slide: measure μ_k with the light gates and submit (within 0.01 of the true value)."],
      demo: { scene: "slide", set: { mat: 0, th2: 35, L: 0.6, timer: 1, mkhat: 0.41 }, press: ["start", "submit"], wait: 2 } },
    { id: "watch", robot: true, text: ["测下滑时间：用秒表在同一设置下至少测 5 次，用平均时间算出 μ_k，提交（与按平均时间算出的值相差 0.005 以内）。比较单次测量的结果相差多大。", "Time the slide: with the stopwatch, time at least 5 runs at one setting, compute μ_k from the mean time and submit (within 0.005 of the value from the mean). How far apart are single runs?"],
      demo: { scene: "slide", set: { mat: 0, th2: 35, L: 0.6, timer: 0, mkhat: 0.401 }, press: ["start", "start", "start", "start", "start", "submit"], wait: 2 } },
    { id: "kid", text: ["滑梯：调倾角，使孩子被轻推后匀速滑下，提交。这时 tan θ 等于什么？", "Slide: set the angle for a steady ride after the push and submit. What does tan θ equal then?"],
      demo: { scene: "life", set: { ths: 17 }, press: ["start", "submit"], wait: 3 } },
  ],
  think: ["倾角读数误差 0.5° 对 μ_s 的影响，在摩擦角大时大还是小？秒表测 5 次取平均，随机误差大约减小到几分之一？为什么加长斜面也能减小 μ_k 的误差？",
          "Does a 0.5° angle error matter more for large or small angles of friction? Averaging 5 stopwatch runs shrinks the error by roughly what factor? Why does a longer incline also help?"],

  reset(api, s) { s.msg = s.msg || ""; s.x = 0; s.v = 0; s.ran = false; s.hist = []; },
  change(api, s) {
    s.msg = "";
    if (api.scene === "tilt" && Math.tan(rad71(api.p.th)) > MAT71[api.p.mat].s) SEEN71[api.p.mat] = true;
  },
  start(api, s) {
    const p = api.p;
    if (api.scene === "slide") {
      s.ran = true;
      if (!slides71(p)) { s.stuck = true; api.stop(); return; }
      const R = (REC71[key71(p)] = REC71[key71(p)] || []);
      R.push(reading71(p, R.length));
    }
    if (api.scene === "life") { s.v = 0.5; s.x = 0; s.hist = [[0, 0.5]]; s.ran = true; }
  },
  update(dt, api, s) {
    const p = api.p;
    if (api.scene === "slide") {
      const a = acc71(rad71(p.th2), MAT71[p.mat].k);
      s.v += a * dt; s.x += s.v * dt;
      if (s.x >= p.L + 0.08) { s.x = p.L + 0.08; api.stop(); }
    }
    if (api.scene === "life") {
      const th = rad71(p.ths), a = s.v > 0 ? acc71(th, KIDK71) : 0;
      s.v = Math.max(0, s.v + a * dt); s.x += s.v * dt;
      if (s.hist.length < 1500) s.hist.push([api.t, s.v]);
      if (s.x >= SLIDE71 || (s.v === 0 && api.t > 0.2) || api.t > 12) api.stop();
    }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "tilt") {
      const m = MAT71[p.mat], thc = Math.atan(m.s), tol = 1.2 * rad71(0.5) / Math.cos(thc) ** 2 + 0.003;
      if (SEEN71[p.mat] && Math.abs(p.mshat - m.s) <= tol) { api.done("ms"); ok = true; }
    }
    if (api.scene === "slide") {
      const R = REC71[key71(p)] || [], m = MAT71[p.mat];
      if (p.timer === 1 && R.length >= 1 && Math.abs(p.mkhat - m.k) <= 0.01) { api.done("gate"); ok = true; }
      if (p.timer === 0 && R.length >= 5) {
        const tm = R.reduce((q, t) => q + t, 0) / R.length;
        if (Math.abs(p.mkhat - mukOf71(p.L, tm, p.th2)) <= 0.005) { api.done("watch"); ok = true; }
      }
    }
    if (api.scene === "life" && s.ran && Math.abs(acc71(rad71(p.ths), KIDK71)) <= 0.1) { api.done("kid"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "tilt") {
      const slip = Math.tan(rad71(p.th)) > MAT71[p.mat].s;
      return [[["材料", "Materials"], api.P(MAT71[p.mat].n)], [["倾角", "Angle"], f(p.th, 1) + "°"], [["tan θ", "tan θ"], f(Math.tan(rad71(p.th)), 3)],
        [["零件", "Part"], slip ? api.T("开始滑动", "slides") : api.T("静止", "at rest")], sub];
    }
    if (api.scene === "slide") {
      const R = REC71[key71(p)] || [];
      return [[["材料", "Materials"], api.P(MAT71[p.mat].n)], [["计时方式", "Timer"], p.timer ? api.T("光电门", "light gates") : api.T("秒表", "stopwatch")],
        [["本次读数 t", "This reading t"], s.stuck && s.ran ? api.T("零件不动，加大倾角", "the part stays put: steepen") : R.length && s.ran ? (p.timer ? f(R[R.length - 1], 3) : f(R[R.length - 1], 2)) + " s" : "—"],
        [["这个设置已测次数", "Runs at this setting"], String(R.length)], sub];
    }
    return [[["滑梯倾角", "Slide angle"], f(p.ths, 1) + "°"], [["孩子的速度", "Child's speed"], f(s.v, 2) + " m/s"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ctx = api.ctx, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue");
    const scene = api.scene;
    if (scene === "tilt" || scene === "slide") {
      const thd = scene === "tilt" ? p.th : p.th2, th = rad71(thd);
      const x0 = w * 0.08, y0 = h * 0.82, Lpx = Math.min(w * 0.55, h * 0.95);
      const ex = x0 + Lpx * Math.cos(th), ey = y0 - Lpx * Math.sin(th);
      poly71(ctx, [[x0, y0], [ex, ey], [ex, y0]], css("--panel"), ink);
      api.label(`${api.fmt(thd, scene === "tilt" ? 1 : 0)}°`, x0 + 48, y0 - 8, ink, 13);
      const ux = -Math.cos(th), uy = Math.sin(th), nx = -Math.sin(th), ny = -Math.cos(th);    // 沿斜面向下、垂直斜面向上
      let d;                                                          // 盒子底边中点离斜面顶端的距离（像素）
      if (scene === "tilt") d = Math.tan(th) > MAT71[p.mat].s ? Lpx * 0.45 : Lpx * 0.15;
      else d = Lpx * 0.12 + Math.min(s.x, p.L + 0.08) / 1.3 * Lpx * 0.8;
      const bw = 46, bh = 30, cx = ex + ux * d, cy = ey + uy * d;
      poly71(ctx, [[cx - ux * bw / 2, cy - uy * bw / 2], [cx + ux * bw / 2, cy + uy * bw / 2],
        [cx + ux * bw / 2 + nx * bh, cy + uy * bw / 2 + ny * bh], [cx - ux * bw / 2 + nx * bh, cy - uy * bw / 2 + ny * bh]], css("--amber"), ink);
      const mx = cx + nx * bh / 2, my = cy + ny * bh / 2, Lg = 50 * Math.sin(th);
      if (Lg > 3) api.arrow(mx, my, mx + ux * Lg, my + uy * Lg, blue, 3);
      const slip = scene === "tilt" ? Math.tan(th) > MAT71[p.mat].s : s.x > 0;
      const Ff = scene === "tilt" ? (slip ? 50 * MAT71[p.mat].k * Math.cos(th) : Lg) : 50 * MAT71[p.mat].k * Math.cos(th);
      if (Ff > 3) api.arrow(cx, cy, cx - ux * Ff, cy - uy * Ff, red, 3);
      if (scene === "slide") {
        const g0 = Lpx * 0.12 + 0.0, g1 = Lpx * 0.12 + p.L / 1.3 * Lpx * 0.8;
        [g0, g1].forEach((q) => { const gx = ex + ux * q, gy = ey + uy * q; api.line(gx, gy, gx + nx * 60, gy + ny * 60, p.timer ? css("--green") : mut, p.timer ? 3 : 1, p.timer ? undefined : [3, 4]); });
        api.label(p.timer ? api.T("光电门", "light gates") : api.T("起点与终点标记", "start and finish marks"), ex + ux * g1 + nx * 66, ey + uy * g1 + ny * 66, mut, 11);
        const R = REC71[key71(p)] || [], tx = w * 0.7;
        api.label(api.T("这个设置下的读数 t / s", "readings at this setting, t / s"), tx, 22, mut, 12);
        R.slice(-14).forEach((t, i) => api.label(`${R.length - Math.min(14, R.length) + i + 1}　${p.timer ? t.toFixed(3) : t.toFixed(2)}`, tx, 44 + i * 17, ink, 12));
        if (R.length > 14) api.label(api.T("（只显示最后 14 次）", "(last 14 shown)"), tx, 44 + 14 * 17, mut, 11);
      }
      api.label(api.P(MAT71[p.mat].n), 12, 20, mut, 13);
      return;
    }
    // 滑梯：左边画滑梯和孩子，右边画速度—时间图
    const th = rad71(p.ths), x0 = w * 0.05, y0 = h * 0.85, Lpx = Math.min(w * 0.5, h * 1.4);
    const tx = x0 + Lpx * Math.cos(th), ty = y0 - Lpx * Math.sin(th);
    api.line(tx, ty, x0, y0, css("--accent"), 6); api.line(tx, ty, tx, y0, mut, 3);
    const q = Math.min(s.x, SLIDE71) / SLIDE71, kx = tx - (tx - x0) * q, ky = ty + (y0 - ty) * q;
    api.circle(kx, ky - 22, 9, css("--amber"), ink); api.line(kx, ky - 13, kx + 10, ky - 2, ink, 3);
    api.label(`${api.fmt(p.ths, 1)}°`, x0 + 50, y0 - 6, ink, 13);
    const G = api.graph({ x: w * 0.6, y: 24, w: w * 0.36, h: h - 70, xmin: 0, xmax: 8, ymin: 0, ymax: 3, xlabel: "t / s", ylabel: "v / (m/s)" }).axes();
    if (s.hist.length > 1) G.pts(s.hist, css("--orange"), 2);
  },
});
