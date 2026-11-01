// 实验 11.3 气垫导轨上的碰撞（配 11.3 节）。测量型实验。
// 导轨场景：滑块 1（质量 m₁）由弹射器以 0.400 m/s 推出，撞上静止的滑块 2（质量 m₂）。碰撞处的缓冲：0 弹簧片、1 橡皮圈、2 魔术贴，
// 恢复系数学生不知道。两个光电门：A 在碰撞点之前，B 在之后；挡光片宽 50.0 mm，读数修约到 0.01 ms，带 ±0.05 ms 以内的误差。
// 碰后滑块 1 若反弹，再次通过 A（记“←”）；若继续向前，在滑块 2 之后通过 B。气垫导轨的摩擦不计。
// 交通事故场景（生活中的例子）：A 车撞上停着的 B 车后卡在一起滑行，量出滑行距离，由动量守恒反推 A 车碰前的速度。
const V113 = 0.400, FLAG113 = 0.050, E113 = [0.95, 0.55, 0.0];
const MA113 = 1500, MB113 = 1200, MU113 = 0.70, VA113 = 60 / 3.6, g113 = 9.81;
function h113(a) { const x = Math.sin(a * 91.345 + 2.71) * 43758.5453; return x - Math.floor(x); }
function after113(m1, m2, e) {
  const vc = m1 * V113 / (m1 + m2);
  return [vc - m2 * e * V113 / (m1 + m2), vc + m1 * e * V113 / (m1 + m2)];
}
const tr113 = (v, seed) => Math.abs(v) < 1e-9 ? null : Math.round((FLAG113 / Math.abs(v) * 1000 + (h113(seed) - 0.5) * 0.1) * 100) / 100;   // ms
function readings113(p) {                                                   // 各光电门的读数（ms）与方向
  const [a, b] = after113(p.m1, p.m2, E113[p.bump]), s = p.m1 * 100 + p.m2 * 1000 + p.bump * 7;
  const A = [["→", tr113(V113, s)]], B = [["→", tr113(b, s + 1)]];
  if (a < -1e-9) A.push(["←", tr113(a, s + 2)]);
  else if (a > 1e-9) B.push(["→ " + "①", tr113(a, s + 3)]);
  return { A, B, a, b };
}
const RUN113 = {};                                                         // 已经做过的设置（调“你测得的结果”滑块后读数仍在）
const key113 = (p) => `${p.m1}|${p.m2}|${p.bump}`;
const skid113 = () => { const v = MA113 * VA113 / (MA113 + MB113); return v * v / (2 * MU113 * g113); };

WQ.lab({
  title: ["实验 11.3 气垫导轨上的碰撞", "Lab 11.3 Collisions on an air track"],
  goal: ["用光电门测碰撞前后的速度，验证动量守恒，测出恢复系数，计算碰撞中损失的动能；用动量守恒做交通事故的速度反推。",
         "Time the gliders through light gates before and after a collision, check momentum conservation, measure the coefficient of restitution and the kinetic energy lost, and use momentum conservation to reconstruct a crash."],
  scenes: [
    { id: "track", robot: true, name: ["气垫导轨", "Air track"], hide: ["vA"],
      problem: { title: ["机器人问题：分拣机的推杆撞上包裹，包裹弹出去多快？", "Robot problem: how fast does a parcel leave when the sorter's paddle hits it?"],
                 text: ["分拣机的推杆撞击包裹，包裹被弹出的速度取决于两者的质量和碰撞时的“弹性”，即恢复系数。用气垫导轨上的两个滑块来测：选质量和缓冲方式，点“开始”，读两个光电门的挡光时间（挡光片宽 50.0 mm）。",
                        "When a sorter's paddle hits a parcel, the parcel's speed depends on the two masses and how bouncy the impact is: the coefficient of restitution. Measure it with two gliders on an air track: choose masses and the bumper, press “Start”, and read both gates (the flags are 50.0 mm wide)."] } },
    { id: "crash", name: ["追尾事故", "Rear-end crash"], hide: ["m1", "m2", "bump", "e"],
      problem: { title: ["生活中的例子：追尾的车碰前有多快", "Everyday example: how fast was the car that hit"],
                 text: ["1500 kg 的 A 车追尾停着的 1200 kg 的 B 车，两车卡在一起向前滑行后停下。路面与轮胎 μ = 0.70。点“开始”，量出两车一起滑行的距离，用动量守恒求 A 车碰前的速度（km/h），提交。",
                        "Car A (1500 kg) hits the stopped car B (1200 kg); locked together they skid to a halt. Tyre–road μ = 0.70. Press “Start”, measure the joint skid distance, use momentum conservation to find A's speed before impact (km/h), and submit."] } },
  ],
  params: [
    { id: "m1", name: ["滑块 1 的质量 m₁", "Glider 1 mass m₁"], min: 0.10, max: 0.50, step: 0.01, value: 0.20, unit: "kg", digits: 2 },
    { id: "m2", name: ["滑块 2 的质量 m₂", "Glider 2 mass m₂"], min: 0.10, max: 0.50, step: 0.01, value: 0.20, unit: "kg", digits: 2 },
    { id: "bump", name: ["缓冲：0 弹簧片，1 橡皮圈，2 魔术贴", "Bumper: 0 spring, 1 rubber band, 2 Velcro"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "e", name: ["你测得的结果", "Your result"], min: 0, max: 1, step: 0.001, value: 0, unit: "", digits: 3 },
    { id: "vA", name: ["你算的 A 车碰前速度", "Your speed of car A"], min: 20, max: 120, step: 1, value: 20, unit: "km/h", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--blue)", name: ["滑块 1", "glider 1"] }, { color: "var(--red)", name: ["滑块 2", "glider 2"] }],
  tasks: [
    { id: "e", robot: true, text: ["气垫导轨：缓冲用橡皮圈，测出恢复系数 e，调到“你测得的结果”，提交（相差 0.02 以内）。", "Air track: with the rubber band, measure e, set it as “Your result” and submit (within 0.02)."],
      demo: { scene: "track", set: { m1: 0.2, m2: 0.2, bump: 1, e: 0.55 }, press: ["start", "submit"], wait: 3 } },
    { id: "loss", robot: true, text: ["气垫导轨：缓冲用魔术贴，m₁ = 0.20 kg、m₂ = 0.30 kg，由测得的速度算出碰撞中损失的动能占碰前动能的比例，提交（相差 0.02 以内）。", "Air track: with Velcro, m₁ = 0.20 kg and m₂ = 0.30 kg, compute from your measured speeds the fraction of kinetic energy lost and submit (within 0.02)."],
      demo: { scene: "track", set: { m1: 0.2, m2: 0.3, bump: 2, e: 0.6 }, press: ["start", "submit"], wait: 3 } },
    { id: "crash", text: ["追尾事故：量出滑行距离，求 A 车碰前的速度，提交（相差 5% 以内）。", "Crash: measure the skid, find car A's speed before impact and submit (within 5%)."],
      demo: { scene: "crash", set: { vA: 60 }, press: ["start", "submit"], wait: 3 } },
  ],
  think: ["由每一次的读数算出碰前、碰后的总动量，两者差多少？误差从哪里来？用弹簧片时，滑块 2 比滑块 1 重得多，滑块 1 会怎样？用魔术贴时，损失的动能到哪里去了？",
          "From each run, compute the total momentum before and after: how far apart are they, and why? With the spring bumper and a much heavier glider 2, what does glider 1 do? With Velcro, where does the lost kinetic energy go?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; s.x1 = 0; s.x2 = 0; s.t = 0; },
  start(api, s) { s.ran = true; s.k = { m1: api.p.m1, m2: api.p.m2, bump: api.p.bump }; },
  update(dt, api, s) {
    const p = api.p, t = api.t;
    if (api.scene === "crash") { if (t > 2) RUN113.crash = true; if (t > 3) api.stop(); return; }
    const tc = 0.6 / V113, [a, b] = after113(p.m1, p.m2, E113[p.bump]);    // 滑块 1 从 0 出发，碰撞点在 0.6 m
    s.x1 = t < tc ? V113 * t : 0.6 + a * (t - tc); s.x2 = t < tc ? 0.6 : 0.6 + b * (t - tc);
    const done1 = a <= 1e-9 ? s.x1 < 0.25 || t > tc + 3 : s.x1 > 1.1;           // 滑块 1 反弹并过 A、停下，或过 B
    if ((s.x2 > 1.3 && done1) || t > tc + 10) { RUN113[key113(p)] = true; api.stop(); }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "track" && (s.ran || RUN113[key113(p)])) {
      if (p.bump === 1 && Math.abs(p.e - E113[1]) <= 0.02) { api.done("e"); ok = true; }
      if (p.bump === 2 && Math.abs(p.m1 - 0.2) < 1e-9 && Math.abs(p.m2 - 0.3) < 1e-9 && Math.abs(p.e - p.m2 / (p.m1 + p.m2)) <= 0.02) { api.done("loss"); ok = true; }
    }
    if (api.scene === "crash" && (s.ran || RUN113.crash) && Math.abs(p.vA / 3.6 - VA113) <= 0.05 * VA113) { api.done("crash"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "crash") return [[["两车一起滑行的距离", "Joint skid distance"], (s.ran && api.t > 2) || RUN113.crash ? f(skid113(), 2) + " m" : "—"], sub];
    if (!s.ran && !RUN113[key113(p)]) return [[["光电门 A", "Gate A"], "—"], [["光电门 B", "Gate B"], "—"], sub];
    const R = readings113(p), tc = 0.6 / V113, t = s.ran && api.running ? api.t : 1e9;   // 运行结束或已做过的设置：显示全部读数
    if (R.a > 1e-9 && 0.4 / R.a > 10) R.B = R.B.slice(0, 1).concat([["①", null]]);       // 滑块 1 太慢，10 s 内到不了 B
    const A = R.A.filter((q, i) => i === 0 || t > tc + 0.35 / Math.abs(R.a)), B = R.B.filter((q, i) => t > tc + (i === 0 ? 0.3 / R.b : 0.4 / Math.max(R.a, 1e-9)));
    const show = (L) => L.length ? L.map((q) => q[1] === null ? api.T("滑块 1 太慢，10 s 内未到", "glider 1 too slow, not there in 10 s") : `${q[0]} ${f(q[1], 2)} ms`).join("；") : "—";
    return [[["光电门 A", "Gate A"], show(A)], [["光电门 B（碰后）", "Gate B (after)"], show(B)], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue");
    if (api.scene === "crash") {
      const gy = h * 0.65, t = s.ran ? Math.min(api.t, 3) : 0, sc = w * 0.06, x0 = w * 0.1;
      api.line(w * 0.02, gy, w * 0.98, gy, ink, 2);
      const tc = 0.8, sd = skid113(), u = Math.min(1, Math.max(0, (t - tc) / 1.5));
      const xb = sd * (1 - (1 - u) * (1 - u));                                    // 匀减速：位移随时间的抛物线
      const xA = t < tc ? -4 + 4 * t / tc : xb;
      api.rect(x0 + (4 + xA) * sc - 4.2 * sc, gy - 40, 4.2 * sc, 34, blue, ink, 6);
      api.rect(x0 + (4 + xb) * sc, gy - 40, 4.0 * sc, 34, red, ink, 6);
      if ((s.ran && api.t > 2) || RUN113.crash) { api.line(x0 + 4 * sc, gy + 14, x0 + (4 + sd) * sc, gy + 14, mut, 2); api.label(api.T("滑行距离", "skid"), x0 + (4 + sd / 2) * sc, gy + 32, mut, 12, "center"); }
      return;
    }
    const gy = h * 0.6, X = (x) => w * 0.05 + x / 1.4 * w * 0.9;
    api.rect(X(0) - 10, gy, X(1.4) - X(0) + 20, 14, mut, null, 4);
    [[0.3, "A"], [1.0, "B"]].forEach(([x, n]) => { api.rect(X(x) - 3, gy - 70, 6, 24, blue); api.label(api.T("光电门 ", "gate ") + n, X(x), gy - 78, blue, 12, "center"); });
    const g1 = 0.06 + 0.25 * p.m1, g2 = 0.06 + 0.25 * p.m2;
    api.rect(X(s.x1) - X(g1) + X(0), gy - 26, X(g1) - X(0), 26, blue, ink, 4);
    api.rect(X(s.x2), gy - 26, X(g2) - X(0), 26, red, ink, 4);
    api.label(api.T(["弹簧片", "橡皮圈", "魔术贴"][p.bump], ["spring", "rubber band", "Velcro"][p.bump]), X(0.6), gy + 34, mut, 12, "center");
  },
});
