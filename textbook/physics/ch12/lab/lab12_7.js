// 实验 12.7 斜面上的滚动（配 12.7 节）。测量型实验。
// 零件滑道场景（机器人问题）：上料机把圆形零件放在倾斜的滑道上让它滚到机器人取料点，沿滑道走 1.000 m，光电门计时（±0.005 s）。
// 可选：0 实心球、1 实心圆柱、2 薄圆筒、3 未知零件（厚壁套筒，内外径之比 0.5，k = J/(MR²) = (1 + 0.5²)/2 = 0.625，学生不知道）。
// 静摩擦因数 μ = 0.35，学生不知道（正文算例用 0.30），薄圆筒不打滑的最大倾角 arctan(0.7) = 35.0°，要靠逐度试出来。倾角超过 arctan(μ(1 + k)/k) 时打滑：此时 a = g(sin θ − μ cos θ)，角加速度由摩擦力矩决定，显示“打滑”。
// 罐头场景（生活中的例子）：一罐汤（液体基本不随罐转，k 取 0.12）、一罐冻实的汤（k = 0.5）、空罐（k ≈ 1，薄壁）在 10° 的坡上比赛。
const L127 = 1.0, MU127 = 0.35, g127 = 9.81, K127 = [0.4, 0.5, 1.0, 0.625], KC127 = [0.12, 0.5, 1.0], TH_C127 = 10;
function h127(a) { const x = Math.sin(a * 63.917 + 0.53) * 43758.5453; return x - Math.floor(x); }
const rad127 = (d) => d * Math.PI / 180;
function motion127(k, thd) {                                              // 返回 {a, slip}：质心加速度，是否打滑
  const th = rad127(thd), lim = Math.atan(MU127 * (1 + k) / k);
  if (th <= lim + 1e-12) return { a: g127 * Math.sin(th) / (1 + k), slip: false };
  return { a: g127 * (Math.sin(th) - MU127 * Math.cos(th)), slip: true };
}
const time127 = (k, thd, seed) => Math.round((Math.sqrt(2 * L127 / motion127(k, thd).a) + (h127(seed) - 0.5) * 0.01) * 1000) / 1000;
const RUN127 = {};                                                        // 已经做过的设置（调“你的结果”滑块后读数仍在）
const kOf127 = (api) => api.scene === "chute" ? K127[api.p.obj] : KC127[api.p.can];
const thOf127 = (api) => api.scene === "chute" ? api.p.th : TH_C127;
const key127 = (api) => api.scene === "chute" ? `c|${api.p.obj}|${api.p.th}` : `k|${api.p.can}`;
const seed127 = (api) => api.scene === "chute" ? api.p.obj * 101 + api.p.th * 7 : 900 + api.p.can * 13;

WQ.lab({
  title: ["实验 12.7 斜面上的滚动", "Lab 12.7 Rolling down an incline"],
  goal: ["测量不同物体沿斜面滚下的时间，由加速度求出 k = J/(MR²)，验证滚下的快慢只取决于质量怎样分布；找出不打滑的最大倾角。",
         "Time different bodies rolling down an incline, get k = J/(MR²) from the acceleration, check that the speed depends only on how the mass is distributed, and find the steepest angle that still gives rolling without slipping."],
  scenes: [
    { id: "chute", robot: true, name: ["零件滑道", "Parts chute"], hide: ["can"],
      problem: { title: ["机器人问题：零件滚到取料点要多久？会不会打滑？", "Robot problem: how long does a part take to roll to the pick point, and does it slip?"],
                 text: ["上料机把圆形零件放在倾斜的滑道上，让它自己滚到机器人的取料点（1.000 m 外）。机器人要知道零件什么时候到。选物体和倾角，点“开始”，读光电门测得的时间。滑道与零件之间的摩擦因数没有测过。",
                        "A feeder sets round parts on an inclined chute and lets them roll to the robot's pick point, 1.000 m away. The robot needs to know when a part arrives. Choose the body and the angle, press “Start”, and read the time from the light gate. The chute–part friction coefficient has not been measured."] } },
    { id: "cans", name: ["罐头赛跑", "Can race"], hide: ["obj", "th"],
      problem: { title: ["生活中的例子：一罐汤和一个空罐，谁先滚到底？", "Everyday example: a can of soup or an empty can — which reaches the bottom first?"],
                 text: ["三个大小、外形一样的罐子在 10° 的坡上从静止滚下 1.000 m：一罐汤、一罐冻实的汤、一个空罐。选罐子，点“开始”，读时间，求各自的 k。",
                        "Three cans of the same size and shape roll 1.000 m from rest down a 10° slope: a can of soup, a can of frozen soup, and an empty can. Choose a can, press “Start”, read the time and work out k for each."] } },
  ],
  params: [
    { id: "obj", name: ["物体：0 实心球，1 实心圆柱，2 薄圆筒，3 未知零件", "Body: 0 solid sphere, 1 solid cylinder, 2 thin hoop, 3 unknown part"], min: 0, max: 3, step: 1, value: 0, unit: "", digits: 0 },
    { id: "th", name: ["倾角 θ", "Angle θ"], min: 5, max: 45, step: 1, value: 20, unit: "°", digits: 0 },
    { id: "can", name: ["罐子：0 一罐汤，1 冻实的汤，2 空罐", "Can: 0 soup, 1 frozen soup, 2 empty"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "ans", name: ["你的结果", "Your result"], min: 0, max: 60, step: 0.01, value: 0, unit: "", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "k", robot: true, text: ["零件滑道：测出未知零件的 k = J/(MR²)，调到“你的结果”，提交（相差 0.03 以内；要在不打滑的倾角下测）。", "Chute: measure the unknown part's k = J/(MR²), set it as “Your result” and submit (within 0.03; measure at an angle where it does not slip)."],
      demo: { scene: "chute", set: { obj: 3, th: 20, ans: 0.625 }, press: ["start", "submit"], wait: 3 } },
    { id: "slip", robot: true, text: ["零件滑道：薄圆筒在多陡的滑道上还能纯滚动？逐度试出最大倾角（度），调到“你的结果”，提交（相差 1° 以内）。", "Chute: how steep can the chute be before the thin hoop slips? Find the maximum angle in degrees by trying angle by angle, set it as “Your result” and submit (within 1°)."],
      demo: { scene: "chute", set: { obj: 2, th: 35, ans: 35 }, press: ["start", "submit"], wait: 3 } },
    { id: "soup", text: ["罐头赛跑：测出一罐汤的 k，提交（相差 0.03 以内）。", "Can race: measure k for the can of soup and submit (within 0.03)."],
      demo: { scene: "cans", set: { can: 0, ans: 0.12 }, press: ["start", "submit"], wait: 3 } },
  ],
  think: ["实心球、实心圆柱、薄圆筒的 k 分别是多少？测得的值与理论值差多少？为什么一罐汤滚得比冻实的汤快？倾角超过某个值后，为什么 k 越大越容易打滑？由薄圆筒的最大倾角，滑道的 μ_s 是多少？",
          "What are k for the solid sphere, solid cylinder and thin hoop, and how close are your measurements? Why does the can of soup beat the frozen one? Above a certain angle, why does a larger k make slipping easier? From your maximum angle for the hoop, what is μ_s?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; s.x = 0; },
  start(api, s) { s.ran = true; },
  update(dt, api, s) {
    const k = kOf127(api), thd = thOf127(api), m = motion127(k, thd), T = Math.sqrt(2 * L127 / m.a), t = Math.min(api.t, T);
    s.x = 0.5 * m.a * t * t;
    if (api.t >= T) { RUN127[key127(api)] = true; api.stop(); }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p, have = s.ran || RUN127[key127(api)]; let ok = false;
    if (api.scene === "chute" && have) {
      if (p.obj === 3 && !motion127(K127[3], p.th).slip && Math.abs(p.ans - K127[3]) <= 0.03) { api.done("k"); ok = true; }
      const lim = Math.atan(MU127 * 2) * 180 / Math.PI;                                        // 薄圆筒 k = 1：35.0°
      if (p.obj === 2 && Math.abs(p.ans - lim) <= 1) { api.done("slip"); ok = true; }
    }
    if (api.scene === "cans" && have && p.can === 0 && Math.abs(p.ans - KC127[0]) <= 0.03) { api.done("soup"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, sub = [["提交结果", "Submission"], s.msg || "—"], have = (s.ran && !api.running) || RUN127[key127(api)];
    const m = motion127(kOf127(api), thOf127(api));
    const rows = [[["走 1.000 m 的时间", "Time over 1.000 m"], have ? f(time127(kOf127(api), thOf127(api), seed127(api)), 3) + " s" : "—"]];
    if (api.scene === "chute") rows.push([["是否打滑", "Slipping?"], have ? (m.slip ? api.T("打滑（接触点在滑动）", "slipping (contact point slides)") : api.T("纯滚动", "rolling without slipping")) : "—"]);
    return rows.concat([sub]);
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue");
    const thd = thOf127(api), th = rad127(thd), k = kOf127(api);
    const Lp = Math.min(w * 0.8 / Math.cos(th), h * 0.7 / Math.sin(th)), x0 = w * 0.1, y0 = h * 0.85 - Lp * Math.sin(th);
    const ux = Math.cos(th), uy = Math.sin(th), nx = Math.sin(th), ny = -Math.cos(th);
    api.line(x0, y0, x0 + Lp * ux, y0 + Lp * uy, ink, 3);
    api.line(x0 + Lp * ux, y0 + Lp * uy, x0, y0 + Lp * uy, mut, 1);
    api.label(`${thd}°`, x0 + Lp * ux - 60, y0 + Lp * uy - 8, mut, 13, "center");
    const r = 22, d = s.x / L127 * Lp * 0.92, cx = x0 + d * ux + r * nx, cy = y0 + d * uy + r * ny;
    const col = api.scene === "chute" ? [red, blue, css("--green"), css("--amber")][api.p.obj] : [blue, css("--amber"), mut][api.p.can];
    const solid = k < 0.9;
    api.circle(cx, cy, r, solid ? col : null, col);
    if (k > 0.55 && k < 0.9) api.circle(cx, cy, r * 0.5, css("--panel"), col);                  // 厚壁套筒：画出内孔
    const mo = motion127(k, thd), ph = d / r * (mo.slip ? MU127 * g127 * Math.cos(th) / k / mo.a : 1);   // 纯滚动：转角 = 路程/半径；打滑时角加速度由摩擦力矩决定
    api.line(cx, cy, cx + r * Math.cos(ph + Math.PI / 2), cy + r * Math.sin(ph + Math.PI / 2), ink, 2);
    const gx = x0 + Lp * 0.92 * ux, gy = y0 + Lp * 0.92 * uy;
    api.line(gx + 50 * nx, gy + 50 * ny, gx + 10 * nx, gy + 10 * ny, red, 2);
    api.label(api.T("光电门", "gate"), gx + 56 * nx, gy + 56 * ny, red, 12, "center");
  },
});
