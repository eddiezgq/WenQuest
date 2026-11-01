// 实验 9.5 关节的功与功率，选电机（配 9.4、9.5 节）。
// 单关节机械臂在竖直面内从 −30° 转到 +60°：连杆 4.0 kg、质心离轴 0.25 m，末端负载 m_p 离轴 0.50 m；梯形角速度曲线，加速、减速各占用时的 1/4。
// 关节转矩 τ = J α + G cos θ，J = Σ m r²，G = (m_L r_L + m_p L) g；功率 P = τ ω。点“开始”画出 τ、ω、P 随时间的变化，并累计 ∫P dt。
// 任务 1：先由升高所需的功算出总功（m_p = 8 kg），提交；任务 2：峰值功率不超过 100 W 的最短用时（m_p = 8 kg），运行后提交；
// 任务 3：m_p = 8 kg、用时 1.0 s，从三种伺服电机和五种传动比中选，要求峰值、持续（水平静止保持）、转速三项都满足，且电机最小。
// 自行车场景：骑行功率 150 W，坡度可调，选后飞轮使踏频在 70–90 r/min。判定都用解析式算。
const g95 = 9.81, ML95 = 4.0, RL95 = 0.25, LP95 = 0.5, TA95 = -30 * Math.PI / 180, TB95 = 60 * Math.PI / 180, EG95 = 0.75;
const MOT95 = [{ n: "A 100 W", r: 0.32, pk: 0.95 }, { n: "B 200 W", r: 0.64, pk: 1.91 }, { n: "C 400 W", r: 1.27, pk: 3.82 }];
const NMAX95 = 5000 * 2 * Math.PI / 60, RAT95 = [50, 80, 100, 120, 160];
const REAR95 = [11, 13, 15, 17, 19, 21, 24, 28, 32, 36, 42], FRONT95 = 34, RW95 = 0.34, PB95 = 150, MB95 = 85;
function arm95(mp, T, t) {                                                        // 时刻 t 的 θ、ω、α、τ、P
  const ta = T / 4, wm = (TB95 - TA95) / (T - ta), al = wm / ta, J = ML95 * RL95 ** 2 + mp * LP95 ** 2, G = (ML95 * RL95 + mp * LP95) * g95;
  let th, om, a;
  if (t < ta) { th = TA95 + 0.5 * al * t * t; om = al * t; a = al; }
  else if (t < T - ta) { th = TA95 + 0.5 * al * ta * ta + wm * (t - ta); om = wm; a = 0; }
  else { const r = Math.max(0, T - t); th = TB95 - 0.5 * al * r * r; om = al * r; a = -al; }
  const tq = J * a + G * Math.cos(th);
  return { th, om, a, tq, P: tq * om, G, wm };
}
function peak95(mp, T) {                                                          // 峰值功率、峰值转矩（取样）
  let P = 0, tq = 0;
  const ts = [T / 4 - 1e-9, 3 * T / 4 - 1e-9];                                   // 加速段、匀速段末尾（功率和转矩在这里跳变）
  for (let i = 0; i <= 1200; i++) ts.push(T * i / 1200);
  ts.forEach((t) => { const q = arm95(mp, T, t); P = Math.max(P, q.P); tq = Math.max(tq, Math.abs(q.tq)); });
  return { P, tq };
}
const work95 = (mp) => (ML95 * RL95 + mp * LP95) * g95 * (Math.sin(TB95) - Math.sin(TA95));
function fits95(mp, T, mi, ri) {
  const m = MOT95[mi], i = RAT95[ri], q = arm95(mp, T, T / 2), pk = peak95(mp, T);
  return pk.tq / (i * EG95) <= m.pk && q.G / (i * EG95) <= m.r && i * q.wm <= NMAX95;
}
function bike95(slope, rear) {                                                    // 速度（m/s）与踏频（r/min）
  const th = Math.atan(slope / 100), F0 = MB95 * g95 * (Math.sin(th) + 0.006 * Math.cos(th)), P = PB95 * 0.95;
  let lo = 0.1, hi = 30;
  for (let k = 0; k < 60; k++) { const v = (lo + hi) / 2; if ((F0 + 0.24 * v * v) * v > P) hi = v; else lo = v; }
  const v = (lo + hi) / 2;
  return { v, cad: v / (2 * Math.PI * RW95) * 60 * rear / FRONT95 };
}

WQ.lab({
  title: ["实验 9.5 关节的功与功率，选电机", "Lab 9.5 Work and power at a joint; choosing a motor"],
  goal: ["看关节转矩、角速度和功率随时间怎样变化，验证功率曲线下的面积等于升高所需的功；按峰值、持续和转速三项要求选电机和减速器。",
         "Watch how joint torque, angular speed and power change in time, check that the area under the power curve equals the work to raise the load, and pick a motor and gearbox for peak, continuous and speed limits."],
  scenes: [
    { id: "power", robot: true, name: ["功与功率", "Work and power"], hide: ["mot", "rat", "slope", "rear"],
      problem: { title: ["机器人问题：关节做了多少功，峰值功率多大？", "Robot problem: how much work does the joint do, and what is the peak power?"],
                 text: ["机械臂的一个关节带着连杆和末端负载，在竖直面内从 −30° 转到 +60°。先算出关节做的总功，调到“你算的功”，提交；再点“开始”，看功率曲线和累计的功。改变用时，看峰值功率怎样变。",
                        "One joint swings the link and its end load in a vertical plane from −30° to +60°. Work out the total work, set “Your work” and submit; then press “Start” and watch the power curve and the work adding up. Change the move time and see what the peak does."] } },
    { id: "select", robot: true, name: ["选电机", "Choose a motor"], hide: ["What", "slope", "rear"],
      problem: { title: ["机器人问题：用哪台电机、多大的传动比？", "Robot problem: which motor and which gear ratio?"],
                 text: ["关节由伺服电机经谐波减速器（效率按 0.75）驱动。电机的峰值转矩要大于运动中的最大转矩折算值，额定转矩要大于水平静止时的保持转矩折算值，最高转速 5000 r/min 要大于折算后的转速。点“开始”测出转矩和角速度，选出满足要求的最小电机和一个传动比，提交。",
                        "A servo motor drives the joint through a harmonic gearbox (efficiency taken as 0.75). The motor's peak torque must cover the largest torque during the move, its rated torque the holding torque with the arm horizontal, and its 5000 r/min the joint speed, all referred to the motor. Press “Start” to measure torque and speed, pick the smallest motor that works with some ratio, and submit."] } },
    { id: "life", name: ["自行车变速", "Bicycle gears"], hide: ["mp", "Tm", "What", "mot", "rat"],
      problem: { title: ["生活中的例子：上坡换哪个飞轮", "Everyday example: which sprocket for the climb"],
                 text: ["骑车人能持续输出约 150 W，踏频在 70–90 r/min 时最舒服。坡度 6% 时，前牙盘 34 齿，车轮半径 0.34 m，后飞轮选哪一个？读出车速，算出踏频，再提交核对。",
                        "A rider can keep up about 150 W and is most comfortable at 70–90 r/min. On a 6% grade with a 34-tooth chainring and 0.34 m wheels, which rear sprocket? Read the speed, work out the cadence, then submit to check."] } },
  ],
  params: [
    { id: "mp", name: ["末端负载 m_p", "End load m_p"], min: 0, max: 10, step: 0.5, value: 5, unit: "kg", digits: 1 },
    { id: "Tm", name: ["用时 T", "Move time T"], min: 0.6, max: 3.0, step: 0.05, value: 1.5, unit: "s", digits: 2 },
    { id: "What", name: ["你算的功", "Your work"], min: 0, max: 150, step: 0.1, value: 0, unit: "J", digits: 1 },
    { id: "mot", name: ["电机：0 A，1 B，2 C", "Motor: 0 A, 1 B, 2 C"], min: 0, max: 2, step: 1, value: 2, unit: "", digits: 0 },
    { id: "rat", name: ["传动比：0→50，1→80，2→100，3→120，4→160", "Ratio: 0→50, 1→80, 2→100, 3→120, 4→160"], min: 0, max: 4, step: 1, value: 0, unit: "", digits: 0 },
    { id: "slope", name: ["坡度", "Grade"], min: 0, max: 10, step: 0.5, value: 0, unit: "%", digits: 1 },
    { id: "rear", name: ["后飞轮（序号 0–10：11…42 齿）", "Rear sprocket (index 0–10: 11…42 teeth)"], min: 0, max: 10, step: 1, value: 3, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--red)", name: ["功率 P", "power P"] }, { color: "var(--green)", name: ["关节转矩 τ", "joint torque τ"] }, { color: "var(--blue)", name: ["角速度 ω", "angular speed ω"] }],
  tasks: [
    { id: "W", robot: true, text: ["功与功率：末端负载 8 kg，算出关节做的总功，提交（相差 0.5 J 以内）。再运行，对照功率曲线下的面积。", "Work and power: with an 8 kg end load, compute the joint's total work and submit (within 0.5 J). Then run it and compare with the area under the power curve."],
      demo: { scene: "power", set: { mp: 8, What: 67.0 }, press: ["submit"], wait: 1 } },
    { id: "Tmin", robot: true, text: ["功与功率：末端负载 8 kg，找出峰值功率不超过 100 W 的最短用时（按 0.05 s 一档），运行后提交。", "Work and power: with 8 kg, find the shortest move time (in 0.05 s steps) that keeps the peak power at or below 100 W; run it, then submit."],
      demo: { scene: "power", set: { mp: 8, Tm: 1.25 }, press: ["start", "submit"], wait: 2 } },
    { id: "pick", robot: true, text: ["选电机：末端负载 8 kg、用时 1.0 s，选出能满足三项要求的最小电机和一个传动比，运行后提交。", "Choose a motor: 8 kg, 1.0 s; pick the smallest motor that meets all three limits with some ratio; run it, then submit."],
      demo: { scene: "select", set: { mp: 8, Tm: 1.0, mot: 1, rat: 3 }, press: ["start", "submit"], wait: 2 } },
    { id: "bike", text: ["自行车：坡度 6%，选后飞轮使踏频在 70–90 r/min，提交。", "Bicycle: at a 6% grade, pick a rear sprocket for a cadence of 70–90 r/min and submit."],
      demo: { scene: "life", set: { slope: 6, rear: 9 }, press: ["submit"], wait: 1 } },
  ],
  think: ["为什么峰值功率出现在加速段的末尾附近？用时减半，峰值转矩和峰值功率大约变成几倍？为什么选电机时持续转矩要按机械臂水平静止来核算？",
          "Why does the peak power come near the end of the speed-up? Halve the move time: roughly how do the peak torque and the peak power change? Why is the continuous torque checked with the arm held still and horizontal?"],

  reset(api, s) { s.msg = s.msg || ""; s.hist = []; s.W = 0; s.ran = false; s.pkP = 0; s.pkT = 0; s.shown = false; },
  start(api, s) { s.ran = true; s.T0 = api.p.Tm; s.mp0 = api.p.mp; s.hist = [[0, arm95(api.p.mp, api.p.Tm, 0)]]; },
  change(api, s) { s.ran = false; },                                              // 改了参数，要重新运行才算数
  update(dt, api, s) {
    if (api.scene === "life") { api.stop(); return; }
    const p = api.p, t = Math.min(api.t, p.Tm), q = arm95(p.mp, p.Tm, t), last = s.hist[s.hist.length - 1];
    [p.Tm / 4, 3 * p.Tm / 4].forEach((tj) => {                                    // 这一步跨过跳变点：补上跳变前的那一点，峰值不会漏掉
      if (last[0] < tj && t >= tj) { const qj = arm95(p.mp, p.Tm, tj - 1e-9); s.pkP = Math.max(s.pkP, qj.P); s.pkT = Math.max(s.pkT, Math.abs(qj.tq)); }
    });
    s.W += (q.P + last[1].P) / 2 * (t - last[0]);
    s.pkP = Math.max(s.pkP, q.P); s.pkT = Math.max(s.pkT, Math.abs(q.tq));
    s.hist.push([t, q]);
    if (api.t >= p.Tm) api.stop();
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "power" && p.mp === 8) {
      if (!s.ran && Math.abs(p.What - work95(8)) <= 0.5) { api.done("W"); ok = true; }      // 先算后运行：运行后读数里有累计的功
      if (s.ran && s.T0 === p.Tm && s.mp0 === 8 && peak95(8, p.Tm).P <= 100 && peak95(8, p.Tm - 0.05).P > 100) { api.done("Tmin"); ok = true; }
    }
    if (api.scene === "select" && s.ran && s.mp0 === 8 && s.T0 === p.Tm && p.mp === 8 && Math.abs(p.Tm - 1.0) < 1e-9) {
      const best = [0, 1, 2].find((mi) => RAT95.some((_, ri) => fits95(8, 1.0, mi, ri)));
      if (p.mot === best && fits95(8, 1.0, p.mot, p.rat)) { api.done("pick"); ok = true; }
    }
    if (api.scene === "life") { s.shown = true; if (p.slope === 6) { const c = bike95(6, REAR95[p.rear]).cad; if (c >= 70 && c <= 90) { api.done("bike"); ok = true; } } }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "life") {
      const b = bike95(p.slope, REAR95[p.rear]);
      return [[["后飞轮", "Rear sprocket"], REAR95[p.rear] + api.T(" 齿", " teeth")], [["车速", "Speed"], f(b.v * 3.6, 1) + " km/h"], [["踏频（提交后显示）", "Cadence (shown after Submit)"], s.shown ? f(b.cad, 0) + " r/min" : "—"], sub];
    }
    const last = s.hist.length ? s.hist[s.hist.length - 1] : null, q = last ? last[1] : null;
    const rows = [[["时间", "Time"], last ? f(last[0], 2) + " s" : "—"], [["关节转矩 τ", "Joint torque τ"], q ? f(q.tq, 1) + " N·m" : "—"],
      [["角速度 ω", "Angular speed ω"], q ? f(q.om, 2) + " rad/s" : "—"], [["功率 P", "Power P"], q ? f(q.P, 1) + " W" : "—"],
      [["累计的功 ∫P dt", "Work so far ∫P dt"], s.ran ? f(s.W, 1) + " J" : "—"], [["已出现的最大功率", "Largest power so far"], s.ran ? f(s.pkP, 1) + " W" : "—"]];
    if (api.scene === "select") rows.push([["已出现的最大转矩", "Largest torque so far"], s.ran ? f(s.pkT, 1) + " N·m" : "—"],
      [["所选", "Chosen"], MOT95[p.mot].n + " · i = " + RAT95[p.rat]]);
    rows.push(sub);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue"), green = css("--green");
    if (api.scene === "life") {
      const b = bike95(p.slope, REAR95[p.rear]), th = Math.atan(p.slope / 100) * 3, ox = w * 0.08, oy = h * 0.8, L = w * 0.84;
      api.line(ox, oy, ox + L * Math.cos(th), oy - L * Math.sin(th), ink, 2);
      const cx = ox + L * 0.45 * Math.cos(th), cy = oy - L * 0.45 * Math.sin(th), r = Math.min(w, h) * 0.08;
      const ux = Math.cos(th), uy = -Math.sin(th), nx = -uy, ny = -ux;
      const w1 = [cx - ux * r * 1.4 + nx * r, cy - uy * r * 1.4 + ny * r], w2 = [cx + ux * r * 1.4 + nx * r, cy + uy * r * 1.4 + ny * r];
      api.circle(w1[0], w1[1], r, null, ink); api.circle(w2[0], w2[1], r, null, ink);
      api.line(w1[0], w1[1], cx + nx * r * 2.2, cy + ny * r * 2.2, ink, 3); api.line(w2[0], w2[1], cx + nx * r * 2.2, cy + ny * r * 2.2, ink, 3);
      api.line(cx + nx * r, cy + ny * r, cx + nx * r * 2.2, cy + ny * r * 2.2, ink, 3); api.line(cx + nx * r, cy + ny * r, w1[0], w1[1], ink, 3);
      if (s.shown) api.label(api.T(`踏频 ${api.fmt(b.cad, 0)} r/min`, `cadence ${api.fmt(b.cad, 0)} r/min`), w * 0.5, h * 0.18, b.cad >= 70 && b.cad <= 90 ? green : red, 18, "center");
      api.label(api.T("（坡度放大画出）", "(grade drawn exaggerated)"), w * 0.5, h * 0.95, mut, 11, "center");
      return;
    }
    // 左：机械臂
    const ox = w * 0.16, oy = h * 0.55, Ls = Math.min(w * 0.24, h * 0.5), last = s.hist.length ? s.hist[s.hist.length - 1] : null;
    const th = last ? last[1].th : TA95;
    api.line(ox - 40, oy + 60, ox + 40, oy + 60, mut, 3); api.line(ox, oy, ox, oy + 60, mut, 6);
    const ex = ox + Ls * Math.cos(th), ey = oy - Ls * Math.sin(th);
    api.line(ox, oy, ex, ey, ink, 8);
    api.circle(ox + Ls * 0.5 * Math.cos(th), oy - Ls * 0.5 * Math.sin(th), 7, mut, ink);
    api.rect(ex - 12, ey - 12, 24, 24, css("--amber"), ink, 3);
    api.circle(ox, oy, 9, css("--accent"), ink);
    api.line(ox, oy, ox + Ls * 1.05, oy, mut, 1, [4, 4]);
    api.label(api.T(`负载 ${api.fmt(p.mp, 1)} kg`, `load ${api.fmt(p.mp, 1)} kg`), ex, ey - 22, ink, 12, "center");
    // 右：τ、ω、P 随时间（纵轴按这组参数的最大值定）
    const pk = peak95(p.mp, p.Tm), ymax = Math.ceil(Math.max(pk.P, pk.tq, arm95(p.mp, p.Tm, p.Tm / 2).wm * 20) * 1.15 / 20) * 20;
    const G = api.graph({ x: w * 0.52, y: h * 0.1, w: w * 0.44, h: h * 0.72, xmin: 0, xmax: p.Tm, ymin: 0, ymax: ymax,
      xlabel: api.T("t / s", "t / s"), ylabel: api.T("P / W　τ / (N·m)　ω × 20 / (rad/s)", "P / W　τ / (N·m)　ω × 20 / (rad/s)") }).axes();
    if (s.hist.length > 1) {
      G.pts(s.hist.map(([t, q]) => [t, q.P]), red, 2.2);
      G.pts(s.hist.map(([t, q]) => [t, q.tq]), green, 1.6);
      G.pts(s.hist.map(([t, q]) => [t, q.om * 20]), blue, 1.6, [5, 4]);
    }
    if (api.scene === "select") {
      const y0 = h * 0.9;
      MOT95.forEach((m, i) => api.label(`${m.n}: ${api.T("额定", "rated")} ${m.r} N·m, ${api.T("峰值", "peak")} ${m.pk} N·m, 5000 r/min`, w * 0.04, y0 - (2 - i) * 16, i === p.mot ? ink : mut, 12));
    }
  },
});
