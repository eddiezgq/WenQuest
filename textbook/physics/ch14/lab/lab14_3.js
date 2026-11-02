// 实验 14.3 机械臂伸出持重：关节静力矩与倾覆条件（配 14.3 节）。
// 移动机械臂场景（机器人问题）：侧视。车轮接地点 x = ±0.30 m（前为正），每个车轮下有称重传感器（读数为前、后两轮之和，±0.5 N）。
// 底盘质量 40 kg、重心 x = −0.040 m（学生不知道，要由称重读数求出）。机械臂简化为一根 12 kg 的均匀杆，肩关节在 x = 0.20 m，
// 水平伸出 r（0.30–1.00 m），肘关节在杆的中点；末端负载 m 在杆端。肩关节额定静力矩 200 N·m。
// 后轮支持力 ≤ 0 时整车绕前轮倾覆。
// 梯子场景（生活中的例子）：长 4.0 m、15 kg 的梯子靠在光滑的墙上，75 kg 的人往上爬到离梯脚 s 处。地面 μ_s = 0.36（学生不知道）。
const G143 = 9.81, XW143 = 0.30, M0143 = 40, X0143 = -0.040, MA143 = 12, XS143 = 0.20, TLIM143 = 200;
const LL143 = 4.0, ML143 = 15, MP143 = 75, MU143 = 0.36;
function h143(a) { const x = Math.sin(a * 41.37 + 1.29) * 43758.5453; return x - Math.floor(x); }
function robot143(p) {                                                     // 前、后轮支持力（N），肩、肘静力矩（N·m）
  const W = (M0143 + MA143 + p.m) * G143;
  const mom = G143 * (M0143 * (X0143 + XW143) + MA143 * (XS143 + p.r / 2 + XW143) + p.m * (XS143 + p.r + XW143));   // 对后轮接地点
  const Nf = mom / (2 * XW143), Nr = W - Nf;
  return { Nf, Nr, Ms: G143 * (MA143 * p.r / 2 + p.m * p.r), Me: G143 * (MA143 / 2 * p.r / 4 + p.m * p.r / 2) };
}
const mtip143 = (r) => (M0143 * (XW143 - X0143) - MA143 * (XS143 + r / 2 - XW143)) / (XS143 + r - XW143);
function ladder143(p) {                                                    // 需要的 μ
  const th = p.th * Math.PI / 180;
  const P = G143 * Math.cos(th) * (ML143 * LL143 / 2 + MP143 * p.s) / (LL143 * Math.sin(th));
  return P / ((ML143 + MP143) * G143);
}
const RUN143 = {};
const key143 = (api) => api.scene === "robot" ? `r|${api.p.r}|${api.p.m}` : `l|${api.p.th}|${api.p.s}`;

WQ.lab({
  title: ["实验 14.3 机械臂伸出持重：关节静力矩与倾覆条件", "Lab 14.3 An arm holding a load: joint torques and tipping"],
  goal: ["用力的平衡和力矩的平衡求车轮的支持力、关节的静力矩；由称重读数求重心位置；找出不倾覆、不超关节力矩的最大负载；由梯子开始滑动的位置测地面的摩擦因数。",
         "Use the balance of forces and torques to find wheel loads and joint torques; locate the centre of gravity from scale readings; find the largest payload that neither tips the robot nor overloads the joint; measure floor friction from where a ladder starts to slip."],
  scenes: [
    { id: "robot", robot: true, name: ["移动机械臂", "Mobile manipulator"], hide: ["th", "s"],
      problem: { title: ["机器人问题：机械臂伸出去，能拿多重的东西？", "Robot problem: with the arm reaching out, how heavy a load can it hold?"],
                 text: ["小型移动机械臂：车轮接地点在 x = ±0.30 m，每个车轮下有称重传感器。机械臂看成一根 12 kg 的均匀杆，肩关节在 x = 0.20 m，水平伸出 r，末端拿着负载 m。肩关节额定静力矩 200 N·m。底盘的质量和重心位置不知道。设 r 和 m，点“开始”，读前、后轮的支持力和两个关节的静力矩。",
                        "A small mobile manipulator: wheel contacts at x = ±0.30 m, with a scale under each wheel. Treat the arm as a uniform 12 kg rod; the shoulder is at x = 0.20 m, the arm reaches out horizontally a distance r and holds a load m at its end. Shoulder rating: 200 N·m static. The base's mass and centre of gravity are unknown. Set r and m, press “Start”, and read the front and rear wheel loads and the two joint torques."] } },
    { id: "ladder", name: ["梯子", "Ladder"], hide: ["r", "m"],
      problem: { title: ["生活中的例子：爬到哪里梯子会滑？", "Everyday example: how high can you climb before the ladder slips?"],
                 text: ["4.0 m 长、15 kg 的梯子靠在光滑的墙上，与地面成 θ 角，75 kg 的人往上爬。地面的摩擦因数不知道。设 θ 和爬到的位置 s，点“开始”，看梯子滑不滑。",
                        "A 4.0 m, 15 kg ladder leans on a smooth wall at angle θ to the floor, and a 75 kg person climbs it. The floor friction coefficient is unknown. Set θ and the position s, press “Start”, and see whether the ladder slips."] } },
  ],
  params: [
    { id: "r", name: ["机械臂伸出 r", "Arm reach r"], min: 0.30, max: 1.00, step: 0.05, value: 0.50, unit: "m", digits: 2 },
    { id: "m", name: ["末端负载 m", "Payload m"], min: 0, max: 30, step: 0.1, value: 5, unit: "kg", digits: 1 },
    { id: "th", name: ["梯子与地面的夹角 θ", "Ladder angle θ"], min: 55, max: 80, step: 1, value: 70, unit: "°", digits: 0 },
    { id: "s", name: ["人离梯脚 s", "Climber position s"], min: 0, max: 4, step: 0.05, value: 2, unit: "m", digits: 2 },
    { id: "ans", name: ["你的结果", "Your result"], min: -20, max: 40, step: 0.01, value: 0, unit: "", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "cg", robot: true, text: ["移动机械臂：由称重读数求底盘重心的 x 坐标（cm，前为正），调到“你的结果”，提交（相差 0.5 cm 以内）。", "Mobile manipulator: from the scale readings find the x coordinate of the base's centre of gravity (cm, forward positive), set it as “Your result” and submit (within 0.5 cm)."],
      demo: { scene: "robot", set: { r: 0.5, m: 0, ans: -4.0 }, press: ["start", "submit"], wait: 2 } },
    { id: "max", robot: true, text: ["移动机械臂：伸出 r = 0.90 m 时，既不倾覆、肩关节也不超过 200 N·m 的最大负载是多少 kg？调到“你的结果”，提交（相差 0.3 kg 以内）。", "Mobile manipulator: at reach r = 0.90 m, what is the largest payload (kg) that neither tips the robot nor exceeds 200 N·m at the shoulder? Set it as “Your result” and submit (within 0.3 kg)."],
      demo: { scene: "robot", set: { r: 0.9, m: 5, ans: 11.75 }, press: ["start", "submit"], wait: 2 } },
    { id: "mu", text: ["梯子：找出梯子开始滑动的位置，求地面的静摩擦因数，调到“你的结果”，提交（相差 0.02 以内）。", "Ladder: find where the ladder starts to slip, work out the floor's static friction coefficient, set it as “Your result” and submit (within 0.02)."],
      demo: { scene: "ladder", set: { th: 70, s: 3, ans: 0.36 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["车轮的支持力随负载怎样变？为什么后轮的读数先到零？伸得越远，先限制负载的是倾覆还是关节力矩？梯子越陡越安全吗？人站在梯子底部时需要的摩擦为什么很小？",
          "How do the wheel loads change with the payload, and why does the rear reading reach zero first? At long reach, which limit bites first: tipping or joint torque? Is a steeper ladder always safer? Why is so little friction needed with the climber at the bottom?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; },
  start(api, s) { s.ran = true; s.k = Object.assign({}, api.p); },
  update(dt, api, s) { if (api.t >= 1.2) { RUN143[key143(api)] = true; api.stop(); } },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = s.ran && s.k ? Object.assign({}, s.k, { ans: api.p.ans }) : api.p, have = s.ran || RUN143[key143(api)]; let ok = false;
    if (api.scene === "robot" && have) {
      if (Math.abs(p.ans - X0143 * 100) <= 0.5) { api.done("cg"); ok = true; }
      const mt = Math.min(mtip143(0.9), (TLIM143 / G143 - MA143 * 0.45) / 0.9);
      if (Math.abs(p.r - 0.9) < 1e-9 && Math.abs(p.ans - mt) <= 0.3) { api.done("max"); ok = true; }
    }
    if (api.scene === "ladder" && have && Math.abs(p.ans - MU143) <= 0.02) { api.done("mu"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"], have = (s.ran && !api.running) || RUN143[key143(api)];
    if (api.scene === "robot") {
      const R = robot143(p), nz = (k) => (h143(p.r * 100 + p.m * 7 + k) - 0.5);
      const tip = R.Nr <= 0;
      return [[["前轮支持力（两轮之和）", "Front wheels (sum)"], have ? (tip ? api.T("倾覆", "tipped") : f(R.Nf + nz(1), 1) + " N") : "—"],
              [["后轮支持力（两轮之和）", "Rear wheels (sum)"], have ? (tip ? api.T("离地", "lifted") : f(R.Nr + nz(2), 1) + " N") : "—"],
              [["肩关节静力矩", "Shoulder torque"], have ? f(R.Ms, 1) + " N·m" + (R.Ms > TLIM143 ? api.T("（超过额定）", " (over rating)") : "") : "—"],
              [["肘关节静力矩", "Elbow torque"], have ? f(R.Me, 1) + " N·m" : "—"], sub];
    }
    return [[["梯子", "Ladder"], have ? (ladder143(p) > MU143 ? api.T("滑了", "slipped") : api.T("稳住了", "holds")) : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue"), p = api.p;
    const have = (s.ran && !api.running) || RUN143[key143(api)];
    if (api.scene === "robot") {
      const gy = h * 0.78, X = (x) => w * 0.35 + x * w * 0.42, R = robot143(p), tip = have && R.Nr <= 0;
      api.line(0, gy, w, gy, ink, 2);
      const ang = tip ? -0.12 : 0, px = X(XW143), py = gy;                                         // 倾覆时绕前轮转一点示意
      const rot = (x, y) => [px + (x - px) * Math.cos(ang) - (y - py) * Math.sin(ang), py + (x - px) * Math.sin(ang) + (y - py) * Math.cos(ang)];
      const poly = (pts, col) => { for (let i = 0; i < pts.length; i++) { const a = rot(...pts[i]), b = rot(...pts[(i + 1) % pts.length]); api.line(a[0], a[1], b[0], b[1], col, 2); } };
      poly([[X(-0.36), gy - 28], [X(0.36), gy - 28], [X(0.36), gy - 70], [X(-0.36), gy - 70]], blue);
      [[X(-XW143), gy - 14], [X(XW143), gy - 14]].forEach(([x, y]) => { const c = rot(x, y); api.circle(c[0], c[1], 14, null, ink); });
      const s0 = rot(X(XS143), gy - 70), s1 = rot(X(XS143), gy - 110), e1 = rot(X(XS143 + p.r), gy - 110);
      api.line(s0[0], s0[1], s1[0], s1[1], ink, 6); api.line(s1[0], s1[1], e1[0], e1[1], ink, 8);
      api.circle(s1[0], s1[1], 7, css("--amber"), ink);
      const em = rot(X(XS143 + p.r / 2), gy - 110); api.circle(em[0], em[1], 6, css("--amber"), ink);
      if (p.m > 0) { const b = rot(X(XS143 + p.r), gy - 96); api.rect(b[0] - 12, b[1], 24, 10 + p.m, red, ink, 3); }
      if (have && !tip) {
        api.arrow(X(XW143), gy + 50, X(XW143), gy + 50 - Math.min(120, R.Nf / 8), css("--green"), 3);
        api.arrow(X(-XW143), gy + 50, X(-XW143), gy + 50 - Math.min(120, R.Nr / 8), css("--green"), 3);
      }
      api.label(api.T("侧视（前方在右）", "side view (front to the right)"), w * 0.5, h * 0.08, mut, 12, "center");
      return;
    }
    const th = p.th * Math.PI / 180, gy = h * 0.85, wx = w * 0.75, sc = Math.min(w * 0.5, h * 0.75) / LL143;
    const slipped = have && ladder143(p) > MU143, slide = slipped ? Math.min(1, (api.running ? api.t : 1.2) / 1.2) * 0.4 : 0;
    const th2 = th - slide * 0.6, bx = wx - LL143 * sc * Math.cos(th2), ty = gy - LL143 * sc * Math.sin(th2);
    api.line(0, gy, w, gy, ink, 2); api.line(wx, gy, wx, h * 0.05, ink, 3);
    api.line(bx, gy, wx, ty, css("--amber"), 6);
    const fr = p.s / LL143, mx = bx + (wx - bx) * fr, my = gy + (ty - gy) * fr;
    api.circle(mx - 10, my - 22, 10, blue, ink); api.line(mx - 10, my - 12, mx - 10, my + 4, blue, 4);
    api.label(`${p.th}°`, bx + 40, gy - 8, mut, 12);
    if (slipped) api.label(api.T("滑了！", "slipped!"), bx, gy + 22, red, 14, "center");
  },
});
