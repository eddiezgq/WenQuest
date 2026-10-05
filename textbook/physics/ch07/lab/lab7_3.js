// 实验 7.3 夹爪夹零件（配 7.1.4 节、7.3.5 节）。
// 提起场景：两指水平夹紧零件，机械臂以竖直加速度 a_z、沿指面的水平加速度 a_x 加速 0.6 s，匀速 0.6 s，再以同样大小的加速度减速
// 0.6 s 停下。两指的摩擦力合起来最多 2μF_N；加速段需要 m√((g + a_z)² + a_x²)，匀速段 mg，减速段 m√((g − a_z)² + a_x²)，
// 任何一段不够就滑落，所以最小夹紧力按三段中最大的一段算（向下运动时是末尾的减速段，且不低于静止值）。
// 转动场景（俯视）：两指沿切向夹紧，手臂 1 s 内由静止匀加速到 ω 后匀速转动；切向力由两指的支持力之差提供，
// 摩擦力要同时提供向心力 mω²r 和平衡重力 mg，需要 m√(g² + (ω²r)²)。滑脱后零件被两指带着保持横向速度 ωr，沿指面向外滑
// （示意：不计滑动摩擦），离开指尖后沿直线飞出。
// 生活场景：双手从两侧夹住 n 本书举起。手与书之间 μ_h = 0.60，书与书之间 μ_b = 0.35；最外面的接触面各要支撑 nmg/2，
// 第 1、2 本书之间要支撑 (n/2 − 1)mg（越往中间越小）。所以 F ≥ max(nmg/(2μ_h), (n/2 − 1)mg/μ_b)。
// 任务都在“提交”时判定：要求按当前设置不滑落，且不超过最小值的 5%（最后一个任务求最大加速度）。
const g73 = 9.81, MU73 = 0.45, MUH73 = 0.60, MUB73 = 0.35, MB73 = 0.50;
const PH73 = 0.6;                                                   // 提起：加速、匀速、减速各 0.6 s
const phase73 = (t) => (t < PH73 ? 1 : t < 2 * PH73 ? 0 : t < 3 * PH73 ? -1 : 2);   // 1 加速，0 匀速，−1 减速，2 停止
const needLift73 = (p, k) => p.m * Math.hypot(g73 + (k === 2 ? 0 : k) * p.az, (k === 2 ? 0 : k) * p.ax);
const needMax73 = (p) => Math.max(needLift73(p, 1), needLift73(p, 0), needLift73(p, -1));
const fmin73 = (api) => (api.scene === "lift" ? needMax73(api.p) : api.p.m * Math.hypot(g73, api.p.w * api.p.w * api.p.r)) / (2 * MU73);
const z73 = (p, t) => {                                             // 提起：手腕的竖直位移（m）
  const a = p.az, T = PH73, tt = Math.min(t, 3 * T);
  if (tt < T) return 0.5 * a * tt * tt;
  if (tt < 2 * T) return 0.5 * a * T * T + a * T * (tt - T);
  const u = tt - 2 * T; return 1.5 * a * T * T + a * T * u - 0.5 * a * u * u;
};
function books73(n, F) {                                            // 返回 "ok"、"hands"（整摞从手里滑出）或 "middle"（中间的书掉出）
  const hands = n * MB73 * g73 / (2 * MUH73), mid = (n / 2 - 1) * MB73 * g73 / MUB73;
  if (F < hands) return "hands";
  if (F < mid) return "middle";
  return "ok";
}
const bookmin73 = (n) => Math.max(n * MB73 * g73 / (2 * MUH73), (n / 2 - 1) * MB73 * g73 / MUB73);

WQ.lab({
  title: ["实验 7.3 夹爪夹零件", "Lab 7.3 A gripper holding a part"],
  goal: ["二指夹爪靠摩擦夹住零件：提起、平移和转动时，零件需要的摩擦力各是多少？找出每种运动下的最小夹紧力。",
         "A two-finger gripper holds a part by friction. How much friction does the part need while being lifted, moved sideways or swung round? Find the smallest grip for each motion."],
  scenes: [
    { id: "lift", robot: true, name: ["提起与平移", "Lift and move"], hide: ["w", "r", "n", "Fp"],
      problem: { title: ["机器人问题：快速搬运时要夹多紧？", "Robot problem: how hard to grip for a fast move?"],
                 text: ["两指从两侧水平夹住零件，指垫与零件之间 μ_s = 0.45。机械臂以竖直加速度 a_z（向上为正）、沿指面方向的加速度 a_x 加速 0.6 s，匀速 0.6 s，再减速 0.6 s 停下。选每个指面的夹紧力 F_N，点“开始”，看零件是否滑落。",
                        "The fingers clamp the part horizontally from both sides; μ_s = 0.45 between pads and part. The arm accelerates for 0.6 s at a_z vertically (up +) and a_x along the finger faces, cruises for 0.6 s, then decelerates for 0.6 s to a stop. Choose the grip F_N of each finger, press “Start” and see whether the part slips."] } },
    { id: "rotate", robot: true, name: ["手臂转动（俯视）", "Arm swinging (top view)"], hide: ["az", "ax", "n", "Fp"],
      problem: { title: ["机器人问题：手臂转动时零件会被“甩”出去吗？", "Robot problem: will the part fly out when the arm swings?"],
                 text: ["SCARA 机器人的手臂在 1 s 内加速到角速度 ω，然后匀速转动，零件离转轴 r。两指沿切向夹紧，μ_s = 0.45。向心力由谁提供？选夹紧力，点“开始”。",
                        "The SCARA arm speeds up to ω in 1 s and then turns steadily; the part is r from the axis. The fingers clamp along the tangent, μ_s = 0.45. What provides the centripetal force? Choose the grip and press “Start”."] } },
    { id: "life", name: ["双手夹书", "Lifting a row of books"], hide: ["FN", "m", "az", "ax", "w", "r"],
      problem: { title: ["生活中的例子：双手夹起一排书", "Everyday example: lifting a row of books between your hands"],
                 text: ["书立在桌上排成一排，每本 0.50 kg。双手从两端压住，往上一提。手与书之间 μ = 0.60，书与书之间 μ = 0.35。要压多大的力？掉下来的会是哪几本？",
                        "A row of books, 0.50 kg each, stands on a table. Press the ends with both hands and lift. μ = 0.60 between hand and book, 0.35 between books. How hard must you press, and which books drop if you do not?"] } },
  ],
  params: [
    { id: "FN", name: ["每个指面的夹紧力 F_N", "Grip per finger F_N"], min: 0, max: 40, step: 0.1, value: 5, unit: "N", digits: 1 },
    { id: "m", name: ["零件质量 m", "Part mass m"], min: 0.2, max: 1.5, step: 0.05, value: 0.6, unit: "kg", digits: 2 },
    { id: "az", name: ["竖直加速度 a_z（向上为正）", "Vertical acceleration a_z (up +)"], min: -5, max: 10, step: 0.5, value: 0, unit: "m/s²", digits: 1 },
    { id: "ax", name: ["沿指面的水平加速度 a_x", "Acceleration along the faces a_x"], min: 0, max: 6, step: 0.5, value: 0, unit: "m/s²", digits: 1 },
    { id: "w", name: ["角速度 ω", "Angular speed ω"], min: 0, max: 8, step: 0.1, value: 3, unit: "rad/s", digits: 1 },
    { id: "r", name: ["零件离转轴 r", "Part radius r"], min: 0.2, max: 0.6, step: 0.05, value: 0.4, unit: "m", digits: 2 },
    { id: "n", name: ["书的本数 n", "Number of books n"], min: 2, max: 12, step: 2, value: 4, unit: "", digits: 0 },
    { id: "Fp", name: ["每只手的压力 F", "Press of each hand F"], min: 0, max: 120, step: 0.5, value: 20, unit: "N", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--red)", name: ["需要的摩擦力", "friction needed"] }, { color: "var(--green)", name: ["最大静摩擦力 2μF_N", "largest static friction 2μF_N"] }],
  tasks: [
    { id: "lift", robot: true, text: ["提起与平移：m = 0.60 kg，a_z = 5.0 m/s²，a_x = 2.0 m/s²。找出不滑落的最小夹紧力（不超过最小值的 5%），提交。", "Lift and move: m = 0.60 kg, a_z = 5.0 m/s², a_x = 2.0 m/s². Find the smallest grip that holds (within 5% of the minimum) and submit."],
      demo: { scene: "lift", set: { m: 0.6, az: 5, ax: 2, FN: 10.1 }, press: ["start", "submit"], wait: 2 } },
    { id: "rot", robot: true, text: ["手臂转动：m = 0.60 kg，r = 0.40 m，ω = 6.0 rad/s。找出零件不被甩出的最小夹紧力（不超过最小值的 5%），提交。", "Arm swinging: m = 0.60 kg, r = 0.40 m, ω = 6.0 rad/s. Find the smallest grip that keeps the part (within 5% of the minimum) and submit."],
      demo: { scene: "rotate", set: { m: 0.6, r: 0.4, w: 6, FN: 11.8 }, press: ["start", "submit"], wait: 3 } },
    { id: "max", robot: true, text: ["提起与平移：夹爪最大只能夹 15 N，m = 0.80 kg，a_x = 3.0 m/s²。向上加速度最大能取多少（0.5 m/s² 一档）？调到这个值，夹紧力取 15 N，提交。", "Lift and move: the gripper manages at most 15 N, m = 0.80 kg, a_x = 3.0 m/s². What is the largest upward acceleration (in 0.5 m/s² steps)? Set it, with a 15 N grip, and submit."],
      demo: { scene: "lift", set: { m: 0.8, ax: 3, az: 6.5, FN: 15 }, press: ["submit"], wait: 1 } },
    { id: "books", text: ["双手夹书：8 本书，找出能把整排书提起来的最小压力（不超过最小值的 5%），提交。先算一算，再试。", "Books: with 8 books, find the smallest press that lifts the whole row (within 5% of the minimum) and submit. Work it out first, then try."],
      demo: { scene: "life", set: { n: 8, Fp: 42.5 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["为什么向上加速时所需的夹紧力最大？转动时向心力和重力相互垂直，合起来为什么只比重力大一点？夹书时为什么掉下来的往往是中间的几本，而不是整排书？",
          "Why does accelerating upward need the most grip? In the swing, why do the centripetal force and gravity, being perpendicular, add up to only a little more than gravity? Why do the middle books tend to drop rather than the whole row?"],

  reset(api, s) { s.needNow = 0; s.rr = 0; s.vr = 0; s.slip = false; s.tslip = 0; s.dy = 0; s.vy = 0; s.phi = 0; s.om = 0; s.fly = null; s.msg = ""; s.res = ""; },
  change(api, s) { s.msg = ""; },
  start(api, s) {
    if (api.scene === "life") s.res = books73(api.p.n, api.p.Fp);
  },
  update(dt, api, s) {
    const p = api.p, t = api.t;
    if (api.scene === "lift") {
      const k = phase73(t);
      s.needNow = needLift73(p, k);
      if (!s.slip && s.needNow > 2 * MU73 * p.FN + 1e-9) { s.slip = true; s.tslip = t; }
      if (s.slip) { s.vy += g73 * dt; s.dy += s.vy * dt; }             // 滑脱后零件下落（示意）
      if (t > 3 * PH73 + 0.6) api.stop();
    } else if (api.scene === "rotate") {
      s.om = Math.min(p.w, p.w * t);
      s.phi += s.om * dt;
      s.needNow = p.m * Math.hypot(g73, s.om * s.om * p.r);
      if (!s.slip && s.needNow > 2 * MU73 * p.FN + 1e-9) { s.slip = true; s.tslip = t; s.rr = p.r; s.vr = 0; }
      if (s.slip && !s.fly) {                                        // 沿指面向外滑，横向速度由两指保持为 ωr
        s.vr += s.om * s.om * s.rr * dt; s.rr += s.vr * dt;
        if (s.rr > p.r + 0.06) {
          const c = Math.cos(s.phi), sn = Math.sin(s.phi), vt = s.om * s.rr;
          s.fly = { x: s.rr * c, y: s.rr * sn, vx: s.vr * c - vt * sn, vy: s.vr * sn + vt * c };
        }
      }
      if (s.fly) { s.fly.x += s.fly.vx * dt; s.fly.y += s.fly.vy * dt; }
      if (t > 4) api.stop();
    } else {
      s.dy = Math.min(0.25, 0.25 * t);
      if (t > 1.6) api.stop();
    }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p, near = (a, b) => Math.abs(a - b) < 1e-6; let ok = false;
    if (api.scene === "lift") {
      const fm = fmin73(api);
      if (near(p.m, 0.6) && near(p.az, 5) && near(p.ax, 2) && p.FN >= fm && p.FN <= 1.05 * fm) { api.done("lift"); ok = true; }
      if (near(p.m, 0.8) && near(p.ax, 3) && near(p.FN, 15)) {
        const holds = (az) => needMax73({ m: p.m, ax: p.ax, az }) <= 2 * MU73 * 15;
        if (holds(p.az) && !holds(p.az + 0.5)) { api.done("max"); ok = true; }
      }
    }
    if (api.scene === "rotate") {
      const fm = fmin73(api);
      if (near(p.m, 0.6) && near(p.r, 0.4) && near(p.w, 6) && p.FN >= fm && p.FN <= 1.05 * fm) { api.done("rot"); ok = true; }
    }
    if (api.scene === "life" && p.n === 8) {
      const fm = bookmin73(8);
      if (p.Fp >= fm && p.Fp <= 1.05 * fm) { api.done("books"); ok = true; }
    }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "life") {
      const R = { ok: ["整排书提起来了", "the whole row lifts"], hands: ["整排书从手里滑出", "the row slips out of your hands"], middle: ["中间的书掉了出来", "the middle books drop out"] };
      return [[["书的总质量", "Total mass"], f(p.n * MB73, 1) + " kg"], [["每只手的压力", "Press of each hand"], f(p.Fp, 1) + " N"],
        [["结果", "Result"], s.res ? api.P(R[s.res]) : "—"], sub];
    }
    const state = s.slip ? api.T(`滑落（t = ${f(s.tslip, 2)} s）`, `slips (t = ${f(s.tslip, 2)} s)`) : api.running || api.t > 0 ? api.T("夹住了", "held") : "—";
    const rows = [[["零件", "Part"], state], [["两指最大静摩擦力 2μF_N", "Largest friction 2μF_N"], f(2 * MU73 * p.FN, 1) + " N"]];
    if (api.scene === "rotate") rows.push([["此刻的角速度", "Angular speed now"], f(s.om, 2) + " rad/s"]);
    rows.push(sub);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mut = css("--muted"), red = css("--red"), green = css("--green"), amber = css("--amber");
    if (api.scene === "lift") {
      const cx = w * 0.32, zs = 90 / Math.max(0.01, 2 * Math.abs(p.az) * PH73 * PH73), top = h * 0.42 - z73(p, api.t) * zs;   // 位移按比例缩放到 ±90 像素
      api.rect(cx - 6, top - 120, 12, 120, mut);                                        // 手腕
      api.rect(cx - 60, top - 14, 120, 14, ink);
      const pw = 56, ph = 56, py = top + 10 + s.dy * 200;
      api.rect(cx - pw / 2, py, pw, ph, amber, ink, 4);
      const fy = top;
      api.rect(cx - pw / 2 - 14, fy, 14, 80, css("--panel"), ink, 3); api.rect(cx + pw / 2, fy, 14, 80, css("--panel"), ink, 3);
      const fl = Math.min(120, 4 * p.FN);
      api.arrow(cx - pw / 2 - 14 - fl * 0.3, fy + 40, cx - pw / 2 - 14, fy + 40, ink, 2); api.arrow(cx + pw / 2 + 14 + fl * 0.3, fy + 40, cx + pw / 2 + 14, fy + 40, ink, 2);
      api.label(api.T("夹紧力", "grip"), cx + pw / 2 + 20, fy + 30, mut, 11);
      // 右侧：需要的摩擦力与最大静摩擦力
      const bx = w * 0.62, by = h - 40, sc = (h - 90) / 30, need = s.needNow || 0, cap = 2 * MU73 * p.FN;
      if (api.t > 0) api.rect(bx, by - Math.min(30, need) * sc, 40, Math.min(30, need) * sc, red);   // 运行后才显示此刻需要的摩擦力
      api.rect(bx + 60, by - Math.min(30, cap) * sc, 40, Math.min(30, cap) * sc, green);
      api.line(bx - 10, by, bx + 120, by, ink, 1);
      api.label(api.T("需要", "needed"), bx, by + 16, ink, 12); api.label(api.T("最大", "largest"), bx + 60, by + 16, ink, 12);
      api.label(api.T("摩擦力 / N（满格 30 N）", "friction / N (full scale 30 N)"), bx - 10, 20, mut, 12);
      api.label(api.T("μ_s = 0.45", "μ_s = 0.45"), 12, 20, mut, 13);
      return;
    }
    if (api.scene === "rotate") {
      const cx = w * 0.34, cy = h * 0.52, sc = Math.min(w * 0.5, h * 0.85) / 1.5;
      api.circle(cx, cy, 10, ink);
      const R = p.r * sc, ex = cx + R * Math.cos(s.phi), ey = cy - R * Math.sin(s.phi);
      api.line(cx, cy, ex, ey, css("--accent"), 12);
      if (!s.fly) { const q = s.slip ? s.rr * sc : R; api.rect(cx + q * Math.cos(s.phi) - 12, cy - q * Math.sin(s.phi) - 12, 24, 24, amber, ink, 3); }
      else api.rect(cx + s.fly.x * sc - 12, cy - s.fly.y * sc - 12, 24, 24, amber, ink, 3);
      api.circle(cx, cy, p.r * sc, null, mut);
      api.label(api.T("俯视；手臂逆时针转动", "top view; the arm turns anticlockwise"), 12, 20, mut, 13);
      const bx = w * 0.66, by = h - 40, scb = (h - 90) / 30, need = s.needNow || 0, cap = 2 * MU73 * p.FN;
      if (api.t > 0) api.rect(bx, by - Math.min(30, need) * scb, 40, Math.min(30, need) * scb, red);
      api.rect(bx + 60, by - Math.min(30, cap) * scb, 40, Math.min(30, cap) * scb, green);
      api.line(bx - 10, by, bx + 120, by, ink, 1);
      api.label(api.T("需要", "needed"), bx, by + 16, ink, 12); api.label(api.T("最大", "largest"), bx + 60, by + 16, ink, 12);
      api.label(api.T("摩擦力 / N（满格 30 N）", "friction / N (full scale 30 N)"), bx - 10, 20, mut, 12);
      return;
    }
    // 双手夹书
    const n = p.n, bw = Math.min(34, (w * 0.6) / n), bh = 120, x0 = w * 0.5 - n * bw / 2, base = h * 0.8, lift = s.dy * 300;
    for (let i = 0; i < n; i++) {
      const mid = s.res === "middle" && i > 0 && i < n - 1, drop = s.res === "hands" || mid ? 0 : lift;
      api.rect(x0 + i * bw, base - bh - drop, bw - 2, bh, i % 2 ? css("--accent") : amber, ink, 2);
    }
    const hy = base - bh / 2 - (s.res === "hands" ? 0 : lift);
    api.rect(x0 - 40, hy - 30, 36, 60, css("--panel"), ink, 10); api.rect(x0 + n * bw + 2, hy - 30, 36, 60, css("--panel"), ink, 10);
    api.line(0, base, w, base, ink, 1);
    api.label(api.T("每本 0.50 kg；手—书 μ = 0.60，书—书 μ = 0.35", "0.50 kg each; hand–book μ = 0.60, book–book μ = 0.35"), 12, 20, mut, 13);
  },
});
