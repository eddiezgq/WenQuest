// 实验 5.2 抛掷进箱（配 5.2 节）。
// 抛箱场景：出手点 (0, 1.00) m，料箱口中心在 (1.60, 0.40) m，宽 0.30 m（与算例 5.2.1 相同）。学生选出手速度和出手角，
// 点“抛 10 次”：每次的出手速度有 ±2% 以内、出手角有 ±3° 以内的误差（只按序号确定，所有设置共用同一组误差，前四次是误差范围的四个角），
// 10 次都进箱才算完成。
// 测速场景（测量型）：机械臂以固定的出手角 40°、未知的出手速度（学生不知道）从 1.00 m 高处抛向地面，每次出手速度有约 2% 的随机误差。
// （出手速度的误差为三角分布，在 ±3.5% 以内，标准差约 1.4%；按序号确定的伪随机数，同一序号的落点相同。）
// 学生每点一次“抛一次”记一个落点，至少 10 次，求平均落点及其不确定度，反推出手速度 v₀ 和扩展不确定度 U，提交后按学生自己的记录判定。
// 罚球场景：出手点高 2.10 m，篮筐（内径 0.45 m）中心高 3.05 m、水平距离 4.20 m。球（半径 0.12 m）斜着落下时，篮筐的“有效开口”
// 是 0.45 sin α（α 为入射角，与水平方向的夹角），球心经过篮筐高度时离中心不超过 0.225 sin α − 0.12 才算空心进筐：越陡越容易进。
const G52 = 9.81, H52 = 1.00, BX52 = 1.60, BY52 = 0.40, BW52 = 0.12;   // 小料盒：口宽 0.12 m（比算例 5.2.3 的料箱窄）
function hash52(a, b) { const x = Math.sin(a * 12.9898 + b * 78.233 + 5.21) * 43758.5453; return x - Math.floor(x); }
function landX52(v, thd, y0, yT) {                 // 下落经过高度 yT 时的水平距离（不可能时返回 NaN）
  const th = thd * Math.PI / 180, a = -0.5 * G52, b = v * Math.sin(th), c = y0 - yT, disc = b * b - 4 * a * c;
  if (disc < 0) return NaN; const t = (-b - Math.sqrt(disc)) / (2 * a); return t > 0 ? v * Math.cos(th) * t : NaN;
}
// 10 次抛掷的出手误差：只按序号确定，所有设置共用同一组误差（速度 ±2% 以内，角度 ±3° 以内），这样不同出手角之间可以公平比较。
const ERR52 = Array.from({ length: 10 }, (_, k) => [(hash52(k + 1, 3.1) - 0.5) * 0.04, (hash52(k + 1, 9.7) - 0.5) * 6]);
ERR52[0] = [0.02, 3]; ERR52[1] = [-0.02, -3]; ERR52[2] = [0.02, -3]; ERR52[3] = [-0.02, 3];   // 前四次取误差范围的四个角
function throws52(v, th) {                         // 10 次抛掷的落点（箱口高度处）
  return ERR52.map(([e1, e2]) => landX52(v * (1 + e1), th + e2, H52, BY52));
}
const VT52 = 3.40, TH52 = 40;                      // 测速场景：真实出手速度（学生不知道）与出手角
const rec52 = { xs: [] };                          // 测速记录放在闭包里，重置时不丢
function shot52(k) { const e = (hash52(k, 7.7) + hash52(k, 8.8) - 1) * 0.035; return landX52(VT52 * (1 + e), TH52, H52, 0); }
function fitV52(xs) {                              // 由落点平均值反推 v₀，并按落点的 A 类不确定度传递
  const n = xs.length, m = xs.reduce((s, x) => s + x, 0) / n, sd = Math.sqrt(xs.reduce((s, x) => s + (x - m) ** 2, 0) / (n - 1)), ux = sd / Math.sqrt(n);
  const inv = (X) => { let lo = 0.5, hi = 10; for (let i = 0; i < 60; i++) { const mid = (lo + hi) / 2; if (landX52(mid, TH52, H52, 0) < X) lo = mid; else hi = mid; } return lo; };
  const v = inv(m), dv = (inv(m + 1e-4) - inv(m - 1e-4)) / 2e-4;
  return { n, m, sd, ux, v, u: Math.abs(dv) * ux };
}
const HB52 = 2.10, XB52 = 4.20, YB52 = 3.05;
function entry52(v, thd) {                        // 经过篮筐高度时的入射角（与水平方向的夹角，度）
  const th = thd * Math.PI / 180, x = landX52(v, thd, HB52, YB52); if (!isFinite(x)) return NaN;
  const t = x / (v * Math.cos(th)), vy = v * Math.sin(th) - G52 * t; return Math.atan2(-vy, v * Math.cos(th)) * 180 / Math.PI;
}
const tol52 = (v, th) => 0.225 * Math.sin(entry52(v, th) * Math.PI / 180) - 0.12;
const inHoop52 = (v, th) => { const x = landX52(v, th, HB52, YB52); return isFinite(x) && tol52(v, th) > 0 && Math.abs(x - XB52) <= tol52(v, th); };

WQ.lab({
  title: ["实验 5.2 抛掷进箱", "Lab 5.2 Throwing into a bin"],
  goal: ["选出手速度和出手角，在有误差的情况下把零件抛进料箱；由多次抛掷的落点测出出手速度及其不确定度；罚球。",
         "Choose the release speed and angle so that parts land in the bin despite release errors; measure a release speed and its uncertainty from repeated landings; a basketball free throw."],
  scenes: [
    { id: "bin", robot: true, name: ["抛进料盒", "Into the tote"], hide: ["vm", "Um", "vb", "thb"],
      problem: { title: ["机器人问题：10 次都要抛进去", "Robot problem: all ten must go in"],
                 text: ["机械臂在 1.00 m 高处出手，小料盒口的中心在 1.60 m 远、0.40 m 高处，口宽只有 0.12 m。每次出手速度有 ±2% 以内、出手角有 ±3° 以内的误差。选出手速度和角度，点“抛 10 次”，10 次都进盒算完成。",
                        "The arm releases at 1.00 m; the small tote's mouth is centred 1.60 m away and 0.40 m high, only 0.12 m wide. Each release has up to ±2% speed error and ±3° angle error. Choose speed and angle and press “Throw 10 times”; all ten must land in the tote."] } },
    { id: "meas", robot: true, name: ["由落点测出手速度", "Release speed from landings"], hide: ["v", "th", "vb", "thb"],
      problem: { title: ["机器人问题：标定机械臂的出手速度", "Robot problem: calibrate the release speed"],
                 text: ["机械臂以 40° 的出手角从 1.00 m 高处把零件抛到地面上，出手速度未知，每次略有不同。点“抛一次”记下落点，至少 10 次。求平均落点及其不确定度，反推出手速度 v₀ 和扩展不确定度 U，提交。",
                        "The arm throws parts from 1.00 m at 40° onto the floor; the release speed is unknown and varies slightly. Press “Throw once” to record landings, at least ten. Find the mean landing distance and its uncertainty, work back to v₀ and its expanded uncertainty U, and submit."] } },
    { id: "hoop", name: ["罚球", "Free throw"], hide: ["v", "th", "vm", "Um"],
      problem: { title: ["生活中的例子：罚球怎样出手", "Everyday example: how to shoot a free throw"],
                 text: ["出手点高 2.10 m，篮筐中心高 3.05 m、水平距离 4.20 m。球斜着落下，入射角越陡，篮筐的有效开口越大，越容易空心进筐。选出手速度和角度投进，速度越小越好。",
                        "The ball leaves at 2.10 m; the rim centre is 3.05 m high and 4.20 m away. The steeper the ball comes down, the larger the effective opening of the rim and the easier a clean swish. Choose speed and angle; the lower the speed the better."] } },
  ],
  params: [
    { id: "v", name: ["出手速度", "Release speed"], min: 2.0, max: 5.0, step: 0.01, value: 2.6, unit: "m/s", digits: 2 },
    { id: "th", name: ["出手角", "Release angle"], min: 5, max: 80, step: 0.5, value: 20, unit: "°", digits: 1 },
    { id: "vm", name: ["你算出的出手速度 v₀", "Your v₀"], min: 2.5, max: 4.5, step: 0.001, value: 3.0, unit: "m/s", digits: 3 },
    { id: "Um", name: ["你算出的扩展不确定度 U（k = 2）", "Your expanded uncertainty U (k = 2)"], min: 0.001, max: 0.2, step: 0.001, value: 0.1, unit: "m/s", digits: 3 },
    { id: "vb", name: ["罚球出手速度", "Shot speed"], min: 6.0, max: 9.0, step: 0.01, value: 8.0, unit: "m/s", digits: 2 },
    { id: "thb", name: ["罚球出手角", "Shot angle"], min: 30, max: 75, step: 0.5, value: 35, unit: "°", digits: 1 },
  ],
  buttons: [{ id: "t10", name: ["抛 10 次（料盒）", "Throw 10 times (tote)"] }, { id: "t1", name: ["抛一次（测速）", "Throw once (speed)"] }, { id: "clear", name: ["清空记录", "Clear records"] },
            { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "bin", robot: true, text: ["料盒：选出手速度和角度，点“抛 10 次”，10 次都进盒。哪些出手角能做到？", "Tote: choose speed and angle and press “Throw 10 times”; all ten must go in. Which angles can do it?"],
      demo: { scene: "bin", set: { v: 3.30, th: 35 }, press: ["t10"], wait: 1 } },
    { id: "meas", robot: true, text: ["测速：至少抛 10 次，由落点求 v₀ 和 U，提交（v₀ 与按你的记录算出的值相差不超过其标准不确定度，U 相差不超过 35%）。", "Speed: throw at least ten times, work out v₀ and U from the landings and submit (v₀ within one standard uncertainty of the value from your records, U within 35%)."],
      demo: { scene: "meas", set: { vm: 3.383, Um: 0.028 }, press: ["clear", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "submit"], wait: 1 } },
    { id: "hoop", text: ["罚球：用不超过 7.25 m/s 的出手速度投进，提交。这时出手角大约多少？入射角呢？", "Free throw: score with a speed of at most 7.25 m/s and submit. What is the release angle then, and the entry angle?"],
      demo: { scene: "hoop", set: { vb: 7.17, thb: 52 }, press: ["submit"], wait: 1 } },
  ],
  think: ["抛箱场景中，出手角取多少时，角度误差对落点的影响最小？为什么它正是所需速度最小的角度？测速场景中，落点的分散来自什么？抛的次数加倍，U 大约变为多少？",
          "In the bin scene, at which angle does the angle error matter least, and why is that the angle needing the least speed? In the speed scene, what makes the landings scatter? How does U change if you double the number of throws?"],

  reset(api, s) {},
  change(api, s, pid) { s.msg = ""; if (pid === "v" || pid === "th") s.shots = null; },
  action(id, api, s) {
    const p = api.p;
    if (id === "clear") rec52.xs.length = 0;
    if (id === "t1" && api.scene === "meas") rec52.xs.push(shot52(rec52.xs.length + 1));
    if (id === "t10" && api.scene === "bin") { s.shots = throws52(p.v, p.th); if (s.shots.every((x) => Math.abs(x - BX52) <= BW52 / 2)) api.done("bin"); }
    if (id === "submit") {
      let ok = false;
      if (api.scene === "meas" && rec52.xs.length >= 10) { const F = fitV52(rec52.xs); ok = Math.abs(p.vm - F.v) <= Math.max(F.u, 0.002) && Math.abs(p.Um - 2 * F.u) <= 0.35 * 2 * F.u; if (ok) api.done("meas"); }
      if (api.scene === "hoop") { ok = inHoop52(p.vb, p.thb) && p.vb <= 7.25 + 1e-9; if (ok) api.done("hoop"); }
      if (api.scene === "bin") { ok = !!s.shots && s.shots.every((x) => Math.abs(x - BX52) <= BW52 / 2); }
      s.msg = ok ? api.T("对了", "correct") : api.scene === "meas" && rec52.xs.length < 10 ? api.T("至少抛 10 次", "throw at least ten times") : api.T("还不满足任务要求", "not yet");
    }
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "bin") { const n = s.shots ? s.shots.filter((x) => Math.abs(x - BX52) <= BW52 / 2).length : 0;
      return [[["10 次中进盒", "In the tote (of 10)"], s.shots ? String(n) : "—"],
        [["10 次落点的范围", "Spread of ten"], s.shots ? f(Math.min(...s.shots), 3) + "～" + f(Math.max(...s.shots), 3) + " m" : "—"]]; }
    if (api.scene === "meas") { const xs = rec52.xs;
      return [[["已抛次数", "Throws"], String(xs.length)], [["最近一次落点", "Last landing"], xs.length ? f(xs[xs.length - 1], 3) + " m" : "—"],
        [["你提交的", "Your result"], `v₀ = ${f(p.vm, 3)}, U = ${f(p.Um, 3)} m/s`], sub]; }
    const x = landX52(p.vb, p.thb, HB52, YB52);
    return [[["球心经过篮筐高度时", "Ball centre at rim height"], isFinite(x) ? f(x - XB52, 2) + " m " + api.T("（相对篮筐中心）", "(from rim centre)") : api.T("够不到", "too low")],
      [["入射角（与水平方向）", "Entry angle (from horizontal)"], isFinite(x) ? f(entry52(p.vb, p.thb), 0) + "°" : "—"], [["允许的偏差", "Allowed offset"], isFinite(x) ? "±" + f(Math.max(0, tol52(p.vb, p.thb)), 3) + " m" : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, blue = css("--blue"), mut = css("--muted"), ink = css("--ink"), red = css("--red"), green = css("--green");
    const path = (G, v, thd, y0, tmax, col, lw) => { const th = thd * Math.PI / 180, pts = [];
      for (let t = 0; t <= tmax; t += 0.005) { const y = y0 + v * Math.sin(th) * t - 0.5 * G52 * t * t; if (y < -0.05) break; pts.push([v * Math.cos(th) * t, y]); } G.pts(pts, col, lw); };
    if (api.scene === "bin") {
      const sc = Math.min((w - 80) / 2.2, (h - 60) / 1.7), G = api.graph({ x: 50, y: 20, w: 2.2 * sc, h: 1.7 * sc, xmin: 0, xmax: 2.2, ymin: 0, ymax: 1.7, xlabel: "x / m", ylabel: "y / m" }).axes();
      api.rect(G.X(BX52 - BW52 / 2), G.Y(BY52), BW52 * sc, BY52 * sc, "#e6eaec", mut);
      path(G, p.v, p.th, H52, 2, blue, 2.5); api.circle(G.X(0), G.Y(H52), 6, ink);
      if (s.shots) s.shots.forEach((x) => api.circle(G.X(x), G.Y(BY52), 4, Math.abs(x - BX52) <= BW52 / 2 ? green : red));
      return;
    }
    if (api.scene === "meas") {
      const G = api.graph({ x: 50, y: 20, w: w - 90, h: h * 0.45, xmin: 0, xmax: 2.0, ymin: 0, ymax: 1.6, xlabel: "x / m", ylabel: "y / m" }).axes();
      api.circle(G.X(0), G.Y(H52), 6, ink);
      rec52.xs.forEach((x) => api.circle(G.X(x), G.Y(0) - 4, 4, blue));
      const cx = 50; api.label(api.T("落点记录（m）", "landings (m)"), cx, h * 0.45 + 70, mut, 12);
      rec52.xs.forEach((x, i) => api.label(`${i + 1}: ${x.toFixed(3)}`, cx + (i % 6) * 110, h * 0.45 + 92 + Math.floor(i / 6) * 18, ink, 12));
      return;
    }
    const G = api.graph({ x: 50, y: 20, w: w - 90, h: h - 70, xmin: 0, xmax: 5.0, ymin: 0, ymax: 5.0, xlabel: "x / m", ylabel: "y / m" }).axes();
    api.line(G.X(XB52 - 0.225), G.Y(YB52), G.X(XB52 + 0.225), G.Y(YB52), css("--amber"), 4); api.line(G.X(XB52 + 0.225), G.Y(YB52), G.X(4.5), G.Y(YB52 + 0.9), mut, 3);
    path(G, p.vb, p.thb, HB52, 2, inHoop52(p.vb, p.thb) ? green : blue, 2.5); api.circle(G.X(0), G.Y(HB52), 8, css("--amber"));
  },
});
