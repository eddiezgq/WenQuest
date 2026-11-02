// 实验 13.3 猫和机器人怎样在空中翻身（配 13.3 节）。
// 机器人场景：小型足式机器人从 0.80 m 高的台子上掉下，离开台面时机头向下倾 35°，总角动量为零。它在空中把尾巴（绕身体质心的俯仰轴）
// 甩过 Δφ，身体就反向转 Δθ = Δφ·J_t/(J_b + J_t)（角动量守恒，相对转角按转动惯量反比分配）。J_t/J_b = 0.35，学生不知道（习题 13.3.4 是 0.30），
// 先用“试摆”（把机器人吊在细线上，只让它俯仰自由，甩尾巴，读身体转过的角度，±0.3% 误差）测出来。尾巴 0.30 s 甩完，下落用时 0.404 s。
// 猫场景（生活中的例子）：把猫看成前、后两半，绕脊柱转。腿收起的一半转动惯量为 1，伸开的一半为 3（相对值）。
// 一个循环 0.20 s：前 0.10 s 前半身收腿、后半身伸腿，两半相对扭过 Δ（前半身转 3Δ/4，后半身反转 Δ/4）；
// 后 0.10 s 前半身伸腿、后半身收腿，再扭回来（前半身反转 Δ/4，后半身转 3Δ/4）。每个循环两半各净转 Δ/2，总角动量始终为零。
// 猫从 1.0 m 高处背朝下掉落，用时 0.452 s，只来得及做两个循环。扭转角 Δ 最大 240°。
const RT133 = 0.35, TH0133 = 35, TF133 = Math.sqrt(2 * 0.8 / 9.81), TS133 = 0.30, TC133 = Math.sqrt(2 * 1.0 / 9.81), CY133 = 0.20;
function h133(a) { const x = Math.sin(a * 37.123 + 2.17) * 43758.5453; return x - Math.floor(x); }
const bodyRot133 = (dphi) => dphi * RT133 / (1 + RT133);
function cat133(D, n, t) {                                               // t 时刻前、后半身转过的角度（°）
  let f = 0, b = 0;
  for (let k = 0; k < n; k++) {
    const t0 = k * CY133;
    const uA = Math.max(0, Math.min(1, (t - t0) / 0.1)), uB = Math.max(0, Math.min(1, (t - t0 - 0.1) / 0.1));
    f += 0.75 * D * uA - 0.25 * D * uB; b += -0.25 * D * uA + 0.75 * D * uB;
  }
  return [f, b];
}
const wrap133 = (a) => { let x = ((a % 360) + 360) % 360; return x > 180 ? x - 360 : x; };
const RUN133 = {};
const key133 = (api) => api.scene === "robot" ? `r|${api.p.mode}|${api.p.dphi}` : `c|${api.p.D}|${api.p.n}`;

WQ.lab({
  title: ["实验 13.3 猫和机器人怎样在空中翻身", "Lab 13.3 How cats and robots turn over in mid-air"],
  goal: ["体会总角动量为零时物体仍能改变朝向：机器人甩尾巴、猫先后收腿扭腰；测出尾巴与身体的转动惯量之比，用它让机器人平着落地。",
         "See how a body with zero angular momentum can still change its orientation: a robot swings its tail, a cat tucks its legs and twists in turn. Measure the tail-to-body moment of inertia ratio and use it to make the robot land level."],
  scenes: [
    { id: "robot", robot: true, name: ["甩尾巴的机器人", "Robot with a tail"], hide: ["D", "n"],
      problem: { title: ["机器人问题：从台子上掉下去时，怎样在空中把身体摆平？", "Robot problem: falling off a ledge, how does the robot level itself in the air?"],
                 text: ["小型足式机器人从 0.80 m 高的台子上掉下，离开台面时机头向下倾了 35°，没有转动（角动量为零）。它没有东西可推，只能在空中甩尾巴。先用“试摆”测出甩尾巴时身体转多少，再选甩尾巴的角度，让它平着落地。",
                        "A small legged robot falls off a 0.80 m ledge, pitched 35° nose-down but not rotating (zero angular momentum). There is nothing to push against; it can only swing its tail. First use the “test swing” to find how much the body turns, then choose the swing angle so that it lands level."] } },
    { id: "cat", name: ["猫", "Cat"], hide: ["dphi", "mode"],
      problem: { title: ["生活中的例子：猫背朝下掉下来，为什么总能四脚着地？", "Everyday example: a cat dropped upside down lands on its feet — how?"],
                 text: ["猫掉下时没有转动，角动量为零。它先收起前腿、伸开后腿，把前半身扭过来；再伸开前腿、收起后腿，把后半身扭过来。腿收起的一半转动惯量小（相对值 1），伸开的一半大（3）。从 1.0 m 高处背朝下掉落，选每次的扭转角 Δ 和循环次数，点“开始”。",
                        "The cat falls without rotation: zero angular momentum. It tucks its front legs and stretches its hind legs, twisting the front half round; then stretches the front legs and tucks the hind legs, twisting the back half round. The tucked half has the small moment of inertia (relative value 1), the stretched half the large one (3). Dropped upside down from 1.0 m, choose the twist Δ per stroke and the number of cycles, then press “Start”."] } },
  ],
  params: [
    { id: "mode", name: ["方式：0 试摆（吊在线上），1 从台子上掉下", "Mode: 0 test swing (hanging), 1 fall off the ledge"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "dphi", name: ["尾巴甩过的角度 Δφ", "Tail swing Δφ"], min: 0, max: 180, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "D", name: ["每次的扭转角 Δ", "Twist per stroke Δ"], min: 0, max: 240, step: 5, value: 120, unit: "°", digits: 0 },
    { id: "n", name: ["循环次数", "Cycles"], min: 1, max: 3, step: 1, value: 1, unit: "", digits: 0 },
    { id: "ans", name: ["你测得的 J_t/J_b", "Your J_t/J_b"], min: 0, max: 1, step: 0.01, value: 0, unit: "", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "ratio", robot: true, text: ["机器人：用“试摆”测出尾巴与身体的转动惯量之比 J_t/J_b，调到“你测得的 J_t/J_b”，提交（相差 0.02 以内）。",
                                       "Robot: use the test swing to measure the ratio J_t/J_b, set it as “Your J_t/J_b” and submit (within 0.02)."],
      demo: { scene: "robot", set: { mode: 0, dphi: 90, ans: 0.35 }, press: ["start", "submit"], wait: 2 } },
    { id: "level", robot: true, text: ["机器人：从台子上掉下，选甩尾巴的角度，使它落地时身体的倾角在 ±2° 以内，运行后提交。", "Robot: falling off the ledge, choose the tail swing so the body is within ±2° of level at touchdown; run it, then submit."],
      demo: { scene: "robot", set: { mode: 1, dphi: 135 }, press: ["start", "submit"], wait: 2 } },
    { id: "cat", text: ["猫：选扭转角和循环次数，使猫落地时前、后半身都在四脚朝下 ±10° 以内，运行后提交。", "Cat: choose the twist and number of cycles so that both halves are within ±10° of feet-down at touchdown; run it, then submit."],
      demo: { scene: "cat", set: { D: 180, n: 2 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["整个过程中机器人（或猫）的总角动量是多少？为什么身体还能转过一个角度？尾巴越长越重越好吗？猫为什么要“先收前腿、再收后腿”，两半同时收腿、同时伸腿行不行？",
          "What is the total angular momentum throughout? Why can the body still turn? Is a longer, heavier tail always better? Why does the cat tuck the front legs first and then the hind legs — would tucking both at once work?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; s.k = 0; },
  start(api, s) { s.ran = true; s.k = Object.assign({}, api.p); },
  update(dt, api, s) {
    const tend = api.scene === "robot" ? (api.p.mode ? TF133 : 0.6) : TC133;
    if (api.t >= tend) { RUN133[key133(api)] = true; api.stop(); }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = s.ran && s.k ? Object.assign({}, s.k, { ans: api.p.ans }) : api.p, have = s.ran || RUN133[key133(api)]; let ok = false;
    if (api.scene === "robot" && have) {
      if (Math.abs(p.ans - RT133) <= 0.02) { api.done("ratio"); ok = true; }
      if (p.mode === 1 && Math.abs(TH0133 - bodyRot133(p.dphi)) <= 2) { api.done("level"); ok = true; }
    }
    if (api.scene === "cat" && have) {
      const [f, b] = cat133(p.D, p.n, TC133);
      if (Math.abs(wrap133(180 + f)) <= 10 && Math.abs(wrap133(180 + b)) <= 10) { api.done("cat"); ok = true; }
    }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"], have = (s.ran && !api.running) || RUN133[key133(api)];
    if (api.scene === "robot") {
      if (p.mode === 0) return [[["身体反向转过的角度", "Body turned (opposite way)"], have ? f(bodyRot133(p.dphi) * (1 + (h133(p.dphi) - 0.5) * 0.006), 2) + "°" : "—"], sub];
      const pitch = TH0133 - bodyRot133(p.dphi);
      return [[["落地时机头向下的倾角", "Nose-down pitch at touchdown"], have ? f(pitch, 1) + "°" : "—"], [["下落时间", "Fall time"], f(TF133, 3) + " s"], sub];
    }
    const [fr, bk] = cat133(p.D, p.n, TC133), unfinished = p.n * CY133 > TC133;
    return [[["落地时前半身离“四脚朝下”", "Front half from feet-down at touchdown"], have ? f(Math.abs(wrap133(180 + fr)), 0) + "°" : "—"],
            [["落地时后半身离“四脚朝下”", "Back half from feet-down at touchdown"], have ? f(Math.abs(wrap133(180 + bk)), 0) + "°" : "—"],
            [["动作", "Moves"], have ? (unfinished ? api.T("没做完就落地了", "touched down before finishing") : api.T("做完了", "finished")) : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue"), p = api.p;
    const t = s.ran ? api.t : 0, D2R = Math.PI / 180;
    if (api.scene === "robot") {
      const u = Math.min(1, t / TS133), body = p.mode ? TH0133 - bodyRot133(p.dphi) * u : -bodyRot133(p.dphi) * u, tail = body + p.dphi * u;
      const cx = w * 0.45, gy = h * 0.85, yTop = h * 0.2;
      const cy = p.mode ? yTop + (gy - 40 - yTop) * Math.min(1, (t / TF133) ** 2) : h * 0.45;
      if (p.mode) { api.line(0, gy, w, gy, ink, 2); api.rect(0, yTop + 28, w * 0.2, gy - yTop - 28, mut, null, 0); }
      else api.line(cx, h * 0.05, cx, cy, mut, 1);
      const b = body * D2R, bl = 70, ux = Math.cos(b), uy = Math.sin(b);                       // 机头在右，向下倾为正（画面 y 向下）
      api.line(cx - ux * bl, cy - uy * bl, cx + ux * bl, cy + uy * bl, blue, 18);
      api.circle(cx + ux * bl, cy + uy * bl, 10, css("--amber"), ink);
      const tb = Math.PI + tail * D2R;                                                        // 尾巴从身体后端伸出
      api.line(cx - ux * bl, cy - uy * bl, cx - ux * bl + 80 * Math.cos(tb), cy - uy * bl + 80 * Math.sin(tb), red, 5);
      api.label(api.T(p.mode ? "侧视：从台子上掉下" : "侧视：吊在线上试摆", p.mode ? "side view: falling" : "side view: test swing on a thread"), w * 0.75, h * 0.1, mut, 12, "center");
      return;
    }
    const [fr, bk] = cat133(p.D, p.n, Math.min(t, TC133));
    const phase = s.ran ? ((t % CY133) < 0.1 ? 0 : 1) : 0;
    [[w * 0.3, fr, api.T("前半身", "front half"), phase === 0], [w * 0.62, bk, api.T("后半身", "back half"), phase === 1]].forEach(([x, a, name, tucked]) => {
      const y = h * 0.45, ang = (180 + a) * D2R, L = tucked ? 30 : 70;                         // 0° = 四脚朝下（腿指向画面下方）
      api.circle(x, y, 38, mut, ink);
      const dx = -Math.sin(ang), dy = Math.cos(ang);
      api.line(x + dx * 30 - dy * 14, y + dy * 30 + dx * 14, x + dx * (30 + L) - dy * 14, y + dy * (30 + L) + dx * 14, ink, 5);
      api.line(x + dx * 30 + dy * 14, y + dy * 30 - dx * 14, x + dx * (30 + L) + dy * 14, y + dy * (30 + L) - dx * 14, ink, 5);
      api.label(name + (s.ran ? (tucked ? api.T("（收腿）", " (tucked)") : api.T("（伸腿）", " (stretched)")) : ""), x, y - 70, ink, 12, "center");
    });
    api.label(api.T("沿脊柱方向看：腿指向下方就是四脚朝下", "looking along the spine: legs pointing down = feet-down"), w * 0.46, h * 0.88, mut, 12, "center");
  },
});
