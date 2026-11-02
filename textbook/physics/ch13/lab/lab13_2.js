// 实验 13.2 四旋翼偏航靠什么（配 13.2 节）。测量型实验。
// 偏航试验台场景（机器人问题）：四旋翼装在只能绕竖直轴转的试验台上，机身连同台子 J_z = 0.012 kg·m²（已测好，显示）。
// 四个螺旋桨悬停转速 ω₀ = 1000 rad/s，两个顺时针、两个逆时针。指令：顺时针一对加 δ、逆时针一对减 δ。
// 每个螺旋桨的反扭矩 Q = k_Q ω²，k_Q = 5.8×10⁻⁸ N·m/(rad/s)²（这架飞机的螺旋桨，与正文算例的 5.0×10⁻⁸ 不同，学生不知道）。
// 偏航力矩 M = 8 k_Q ω₀ δ（与正文式 (13.2.6) 一致）。机头转角读数带 ±0.3% 以内的误差。
// 方式 0：δ 保持 2.000 s，读 2.000 s 时机头转过的角度；方式 1：前 1.0 s 加 δ、后 1.0 s 加 −δ（先加速后减速），读最后的机头方向。
// 判定用点“开始”时的参数（运行中拖动滑块不算数）。
// 转椅场景（生活中的例子）：人坐在转椅上，手握竖直轮轴、轮子自转（俯视逆时针）。把轮轴翻过角度 β，转椅开始转：
// J_c ω_c = J_w ω_w (1 − cos β)。人和转椅 J_c = 2.5 kg·m²（显示），轮子 J_w = 0.11 kg·m²（学生不知道）。
const KQ132 = 5.8e-8, TR132 = 2.0, W0132 = 1000, JZ132 = 0.012, JC132 = 2.5, JW132 = 0.11;
function h132(a) { const x = Math.sin(a * 52.711 + 0.91) * 43758.5453; return x - Math.floor(x); }
const al132 = (dl) => 8 * KQ132 * W0132 * dl / JZ132;
function yaw132(p, t) {                                                   // 机头转角（rad），0 ≤ t ≤ 2
  const a = al132(p.dl);
  if (p.mode === 0) return 0.5 * a * t * t;
  return t < 1 ? 0.5 * a * t * t : 0.5 * a + a * (t - 1) - 0.5 * a * (t - 1) * (t - 1);
}
const noise132 = (seed) => 1 + (h132(seed) - 0.5) * 0.006;
const wc132 = (p) => JW132 * 2 * Math.PI * p.n * (1 - Math.cos(p.beta * Math.PI / 180)) / JC132;
const RUN132 = {};
const key132 = (api) => api.scene === "drone" ? `d|${api.p.mode}|${api.p.dl}` : `c|${api.p.n}|${api.p.beta}`;

WQ.lab({
  title: ["实验 13.2 四旋翼偏航靠什么", "Lab 13.2 How a quadrotor yaws"],
  goal: ["测出螺旋桨的反扭矩系数，用它让四旋翼准确地转过 90°；用转椅和自行车轮体会角动量定理，测出轮子的转动惯量。",
         "Measure the propellers' reaction-torque coefficient and use it to turn a quadrotor through exactly 90°; feel the angular momentum theorem with a swivel chair and a bicycle wheel, and measure the wheel's moment of inertia."],
  scenes: [
    { id: "drone", robot: true, name: ["偏航试验台", "Yaw test stand"], hide: ["n", "beta"],
      problem: { title: ["机器人问题：四旋翼没有“方向舵”，怎么转头？", "Robot problem: a quadrotor has no rudder — how does it turn?"],
                 text: ["四个螺旋桨两个顺时针、两个逆时针转，空气给每个螺旋桨一个反扭矩，两对互相抵消。让顺时针的一对快一点、逆时针的一对慢一点，反扭矩就不再抵消。飞机装在只能绕竖直轴转的试验台上，J_z = 0.012 kg·m²，悬停转速 1000 rad/s。设转速差 δ 和方式，点“开始”。",
                        "Two propellers spin clockwise and two anticlockwise; the air gives each a reaction torque, and the pairs cancel. Speed up the clockwise pair a little and slow the other pair, and they no longer cancel. The drone sits on a stand that only lets it yaw, J_z = 0.012 kg·m², hover speed 1000 rad/s. Set the speed difference δ and the mode, then press “Start”."] } },
    { id: "chair", name: ["转椅与自行车轮", "Swivel chair and bicycle wheel"], hide: ["dl", "mode"],
      problem: { title: ["生活中的例子：翻转轮子，转椅为什么会转？", "Everyday example: why does the chair turn when you flip the wheel?"],
                 text: ["坐在转椅上，双手握住自转的自行车轮的轴，轴竖直。把轮轴翻过一个角度，转椅自己转了起来。人和转椅 J_c = 2.5 kg·m²。选轮子的转速和翻转角度，点“开始”，读转椅的角速度。",
                        "Sit on a swivel chair holding a spinning bicycle wheel by its axle, axle vertical. Tilt the axle over and the chair starts to turn by itself. Person plus chair J_c = 2.5 kg·m². Choose the wheel's spin rate and the tilt angle, press “Start”, and read the chair's angular velocity."] } },
  ],
  params: [
    { id: "dl", name: ["转速差 δ", "Speed difference δ"], min: 0, max: 120, step: 1, value: 30, unit: "rad/s", digits: 0 },
    { id: "mode", name: ["方式：0 保持 2 s，1 先加速 1 s 后减速 1 s", "Mode: 0 hold 2 s, 1 accelerate 1 s then brake 1 s"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "n", name: ["轮子转速", "Wheel spin"], min: 2, max: 8, step: 0.5, value: 4, unit: "r/s", digits: 1 },
    { id: "beta", name: ["轮轴翻转角度 β", "Axle tilt β"], min: 0, max: 180, step: 5, value: 180, unit: "°", digits: 0 },
    { id: "ans", name: ["你的结果", "Your result"], min: 0, max: 10, step: 0.01, value: 0, unit: "", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "kq", robot: true, text: ["偏航试验台：测出反扭矩系数 k_Q（以 10⁻⁸ N·m/(rad/s)² 为单位），调到“你的结果”，提交（相差 5% 以内）。",
                                    "Stand: measure the reaction-torque coefficient k_Q in units of 10⁻⁸ N·m/(rad/s)², set it as “Your result” and submit (within 5%)."],
      demo: { scene: "drone", set: { mode: 0, dl: 40, ans: 5.8 }, press: ["start", "submit"], wait: 2 } },
    { id: "turn", robot: true, text: ["偏航试验台：先用测得的 k_Q 算出 δ，再用方式 1 运行，使机头正好转过 90°（相差 3° 以内），提交。", "Stand: compute δ from your k_Q, then run in mode 1 so the heading turns exactly 90° (within 3°), and submit."],
      demo: { scene: "drone", set: { mode: 1, dl: 41 }, press: ["start", "submit"], wait: 2 } },
    { id: "wheel", text: ["转椅：测出自行车轮的转动惯量（kg·m²），提交（相差 5% 以内）。", "Chair: measure the bicycle wheel's moment of inertia (kg·m²) and submit (within 5%)."],
      demo: { scene: "chair", set: { n: 5, beta: 180, ans: 0.11 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["反扭矩是谁施加给谁的力矩？四个螺旋桨的转速都变了，总升力变了多少？为什么偏航比俯仰、滚转“慢”得多？转椅场景中，轮轴翻过 90° 和 180°，转椅的角速度之比是多少？",
          "Who exerts the reaction torque on whom? All four rotor speeds change: by how much does the total thrust change? Why is yaw so much more sluggish than pitch and roll? In the chair scene, what is the ratio of the chair's angular velocity for tilts of 90° and 180°?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; s.th = 0; s.ph = 0; },
  start(api, s) { s.ran = true; s.k = Object.assign({}, api.p); },
  update(dt, api, s) {
    const p = api.p, T = api.scene === "drone" ? TR132 : 1.0, t = Math.min(api.t, T);
    if (api.scene === "drone") s.th = yaw132(p, t);
    else { s.ph = Math.min(1, t / 0.6); }                                  // 0.6 s 内把轮轴翻过去
    if (api.t >= T) { RUN132[key132(api)] = true; api.stop(); }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = s.ran && s.k ? Object.assign({}, s.k, { ans: api.p.ans }) : api.p, have = s.ran || RUN132[key132(api)]; let ok = false;
    if (api.scene === "drone" && have) {
      if (Math.abs(p.ans - KQ132 * 1e8) <= 0.05 * KQ132 * 1e8) { api.done("kq"); ok = true; }
      if (p.mode === 1 && Math.abs(yaw132(p, TR132) * 180 / Math.PI - 90) <= 3) { api.done("turn"); ok = true; }
    }
    if (api.scene === "chair" && have && Math.abs(p.ans - JW132) <= 0.05 * JW132) { api.done("wheel"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"], have = (s.ran && !api.running) || RUN132[key132(api)];
    if (api.scene === "drone") {
      const deg = yaw132(p, TR132) * 180 / Math.PI * noise132(p.dl * 3 + p.mode * 1000);
      return [[[p.mode ? "2.000 s 后机头转过的角度" : "2.000 s 时机头转过的角度", "Heading change after 2.000 s"], have ? f(deg, 2) + "°" : "—"],
              [["总升力的变化", "Change in total thrust"], f(100 * 4 * p.dl * p.dl / (4 * W0132 * W0132), 2) + "%"], sub];
    }
    return [[["转椅的角速度（逆时针为正）", "Chair angular velocity (anticlockwise +)"], have ? f(wc132(p) * noise132(p.n * 31 + p.beta), 3) + " rad/s" : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue"), p = api.p;
    if (api.scene === "drone") {
      const cx = w * 0.42, cy = h * 0.5, R = Math.min(w, h) * 0.26, th = -s.th;          // 画面 y 向下：逆时针转角取负
      api.circle(cx, cy, R * 1.55, null, mut);
      for (let k = 0; k < 4; k++) {
        const a = th + Math.PI / 4 + k * Math.PI / 2, x = cx + R * Math.cos(a), y = cy + R * Math.sin(a), cw = k % 2 === 0;
        api.line(cx, cy, x, y, ink, 5);
        api.circle(x, y, R * 0.42, null, cw ? red : blue);
        api.label(cw ? api.T("顺", "CW") : api.T("逆", "CCW"), x, y + 5, cw ? red : blue, 13, "center");
      }
      api.arrow(cx, cy, cx + R * 1.3 * Math.cos(th), cy + R * 1.3 * Math.sin(th), css("--amber"), 3);
      api.label(api.T("机头", "nose"), cx + R * 1.45 * Math.cos(th), cy + R * 1.45 * Math.sin(th), css("--amber"), 12, "center");
      return;
    }
    const cx = w * 0.4, cy = h * 0.55, beta = (p.beta * Math.PI / 180) * (s.ph || 0);
    api.rect(cx - 60, cy + 40, 120, 18, mut, ink, 4);
    api.line(cx, cy + 58, cx, cy + 120, ink, 4);
    api.circle(cx, cy - 10, 30, null, ink);
    const L = 110, ax = Math.sin(beta), ay = -Math.cos(beta);
    api.line(cx + 60 - ax * L * 0.5, cy - 60 - ay * L * 0.5, cx + 60 + ax * L * 0.5, cy - 60 + ay * L * 0.5, ink, 3);
    api.line(cx + 60 - Math.cos(beta) * 70, cy - 60 - Math.sin(beta) * 70, cx + 60 + Math.cos(beta) * 70, cy - 60 + Math.sin(beta) * 70, blue, 6);
    api.arrow(cx + 60, cy - 60, cx + 60 + ax * 70, cy - 60 + ay * 70, css("--amber"), 3);
    api.label(api.T("轮子的角动量", "wheel's L"), cx + 70 + ax * 80, cy - 64 + ay * 80, css("--amber"), 12);
    api.label(api.T("侧视：轮轴由竖直向上翻过 β", "side view: axle tilted β from vertical"), cx, cy + 150, mut, 12, "center");
  },
});
