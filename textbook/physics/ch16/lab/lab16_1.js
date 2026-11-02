// 实验 16.1 液压举升与气动夹爪的力（配 16.1 节）。测量型实验。
// 气动夹爪场景（机器人问题）：夹爪的每个手指由一个双作用气缸推动（这里只用推出的一侧）。气缸 0：缸径 16.0 mm（铭牌）；气缸 1：旧气缸，铭牌看不清，
// 缸径 18.0 mm（学生不知道）。活塞密封有摩擦，推出时损失约 10.0 N（两个气缸相同，学生不知道）。手指上装力传感器，读数 ±0.3 N。
// 输出力 F = pA − f。用两个压强测两次，斜率就是面积 A，截距是摩擦 f。
// 液压千斤顶场景（生活中的例子）：小活塞直径 20 mm，大活塞 200 mm，车和平台共 1800 kg（与算例 16.1.1 一致）。
const D161 = [16.0e-3, 18.0e-3], F161 = 10.0, d1_161 = 0.020, d2_161 = 0.200, M161 = 1800, g161 = 9.81;
function h161(a) { const x = Math.sin(a * 61.73 + 0.19) * 43758.5453; return x - Math.floor(x); }
const area161 = (k) => Math.PI * D161[k] * D161[k] / 4;
const force161 = (p) => Math.max(0, p.p * 1e6 * area161(p.cyl) - F161);
const need161 = 2.0 * 2.0 * (g161 + 3.0) / (2 * 0.40);                     // 每个手指要压的力：2 kg、μ = 0.40、安全系数 2、向上 3 m/s²
const pneed161 = (need161 + F161) / area161(0) / 1e6;
const Fjack161 = M161 * g161 * (d1_161 * d1_161) / (d2_161 * d2_161);
const RUN161 = {};
const key161 = (api) => api.scene === "gripper" ? `g|${api.p.cyl}|${api.p.p}` : `j|${api.p.F}`;

WQ.lab({
  title: ["实验 16.1 液压举升与气动夹爪的力", "Lab 16.1 Hydraulic lifting and pneumatic gripper force"],
  goal: ["由气缸在两个压强下的输出力求活塞面积和密封摩擦，测出旧气缸的缸径，定出夹爪需要的气压；用液压千斤顶体会帕斯卡原理。",
         "From a cylinder's output force at two pressures find the piston area and seal friction, measure an old cylinder's bore, and set the gripper pressure; feel Pascal's principle with a hydraulic jack."],
  scenes: [
    { id: "gripper", robot: true, name: ["气动夹爪", "Pneumatic gripper"], hide: ["F"],
      problem: { title: ["机器人问题：气压调多大，夹爪才夹得住？", "Robot problem: what air pressure makes the gripper hold?"],
                 text: ["夹爪的每个手指由一个气缸推动，手指上的力传感器读出夹紧力。气缸 0 的缸径是 16.0 mm；气缸 1 是一个铭牌看不清的旧气缸。活塞密封有摩擦，大小不知道。选气缸和气源表压，点“开始”，读夹紧力。",
                        "Each finger is pushed by an air cylinder, and a force sensor on the finger reads the clamping force. Cylinder 0 has a 16.0 mm bore; cylinder 1 is an old one with an unreadable plate. The seals have friction of unknown size. Choose the cylinder and the gauge pressure, press “Start”, and read the clamping force."] } },
    { id: "jack", name: ["液压千斤顶", "Hydraulic jack"], hide: ["p", "cyl"],
      problem: { title: ["生活中的例子：用一只手顶起一辆车", "Everyday example: lifting a car with one hand"],
                 text: ["液压举升机的小活塞直径 20 mm，大活塞 200 mm，大活塞上的平台连同汽车共 1800 kg。在小活塞上加力 F，点“开始”，看车能不能升起来，读油压。",
                        "A hydraulic lift has a 20 mm small piston and a 200 mm large one; the platform and car on the large piston weigh 1800 kg. Apply a force F to the small piston, press “Start”, see whether the car rises, and read the oil pressure."] } },
  ],
  params: [
    { id: "cyl", name: ["气缸：0 缸径 16.0 mm，1 旧气缸", "Cylinder: 0 bore 16.0 mm, 1 old cylinder"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "p", name: ["气源表压", "Supply gauge pressure"], min: 0.10, max: 0.80, step: 0.005, value: 0.30, unit: "MPa", digits: 3 },
    { id: "F", name: ["加在小活塞上的力 F", "Force on the small piston F"], min: 50, max: 300, step: 0.5, value: 100, unit: "N", digits: 1 },
    { id: "ans", name: ["你测得的缸径", "Your bore"], min: 10, max: 25, step: 0.1, value: 10, unit: "mm", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "bore", robot: true, text: ["气动夹爪：用旧气缸在两个不同的压强下测夹紧力，求它的缸径，调到“你测得的缸径”，提交（相差 0.3 mm 以内）。", "Gripper: measure the old cylinder's force at two pressures, find its bore, set it as “Your bore” and submit (within 0.3 mm)."],
      demo: { scene: "gripper", set: { cyl: 1, p: 0.5, ans: 18.0 }, press: ["start", "submit"], wait: 2 } },
    { id: "grip", robot: true, text: ["气动夹爪：用气缸 0 夹 2.0 kg 的盒子，指面 μ = 0.40，安全系数 2，机械臂向上加速 3.0 m/s²。每个手指要压 S·m(g + a)/(2μ)。先测出密封摩擦，再把气压调到刚好够用（按滑块刻度取，多出不超过 0.02 MPa），运行后提交。",
                                     "Gripper: cylinder 0 holds a 2.0 kg box, μ = 0.40 at the fingers, safety factor 2, the arm accelerating up at 3.0 m/s². Each finger must press S·m(g + a)/(2μ). Measure the seal friction first, then set the pressure just high enough (no more than 0.02 MPa over), run and submit."],
      demo: { scene: "gripper", set: { cyl: 0, p: 0.37 }, press: ["start", "submit"], wait: 2 } },
    { id: "jack", text: ["液压千斤顶：找出刚好能把车顶起来的力（多出不超过 2%），运行后提交。", "Jack: find the force that just lifts the car (no more than 2% over), run and submit."],
      demo: { scene: "jack", set: { F: 177 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["为什么用两个压强测量就能把摩擦“消掉”？只用一个压强、不管摩擦，求出的缸径偏大还是偏小？千斤顶的小活塞要压下多少，车才升高 1 cm？省了力，省了功吗？",
          "Why do two pressures cancel the friction? With one pressure and friction ignored, is the bore too big or too small? How far must the small piston go down to raise the car 1 cm? You save force, but do you save work?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; },
  start(api, s) { s.ran = true; s.k = Object.assign({}, api.p); },
  update(dt, api, s) { if (api.t >= 1.5) { RUN161[key161(api)] = true; api.stop(); } },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = s.ran && s.k ? Object.assign({}, s.k, { ans: api.p.ans }) : api.p, have = s.ran || RUN161[key161(api)]; let ok = false;
    if (api.scene === "gripper" && have) {
      if (p.cyl === 1 && Math.abs(p.ans - D161[1] * 1000) <= 0.3) { api.done("bore"); ok = true; }
      if (p.cyl === 0 && p.p >= pneed161 - 0.005 && p.p <= pneed161 + 0.02) { api.done("grip"); ok = true; }
    }
    if (api.scene === "jack" && have && p.F >= Fjack161 && p.F <= 1.02 * Fjack161) { api.done("jack"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"], have = (s.ran && !api.running) || RUN161[key161(api)];
    if (api.scene === "gripper")
      return [[["夹紧力（力传感器）", "Clamping force (sensor)"], have ? f(force161(p) + (h161(p.p * 1000 + p.cyl * 7) - 0.5) * 0.6, 1) + " N" : "—"], sub];
    const pr = p.F / (Math.PI * d1_161 * d1_161 / 4);
    return [[["油压（表压）", "Oil pressure (gauge)"], have ? f(pr / 1e6, 3) + " MPa" : "—"],
            [["车", "Car"], have ? (p.F >= Fjack161 ? api.T("升起来了", "rises") : api.T("不动", "does not move")) : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue"), p = api.p;
    const u = s.ran ? Math.min(1, api.t / 1.5) : ((RUN161[key161(api)]) ? 1 : 0);
    if (api.scene === "gripper") {
      const cy = h * 0.5, bore = (p.cyl ? 18 : 16) * 3.2, x0 = w * 0.15, L = w * 0.3, ext = u * 30;
      api.rect(x0, cy - bore / 2 - 8, L, bore + 16, null, ink, 4);
      api.rect(x0 + L * 0.35 + ext, cy - bore / 2, 14, bore, mut, ink, 2);
      api.line(x0 + L * 0.35 + 14 + ext, cy, x0 + L + 60 + ext, cy, ink, 6);
      api.rect(x0 + L + 60 + ext, cy - 50, 16, 100, blue, ink, 3);
      api.rect(x0 + L + 80 + ext * 0, cy - 30, 70, 60, css("--amber"), ink, 4);
      api.label(api.T("压缩空气", "air"), x0 + L * 0.15, cy - bore / 2 - 18, blue, 12, "center");
      api.label(api.T("手指 + 力传感器", "finger + force sensor"), x0 + L + 70, cy + 72, mut, 12, "center");
      return;
    }
    const gy = h * 0.8, rise = (p.F >= Fjack161 ? u : 0) * 30;
    api.rect(w * 0.15, gy - 120, 30, 120, null, ink, 2); api.rect(w * 0.15 + 2, gy - 120 + 40, 26, 80, blue, null, 0);
    api.rect(w * 0.45, gy - 120, 160, 120, null, ink, 2); api.rect(w * 0.45 + 2, gy - 120 + 40 - rise, 156, 80 + rise, blue, null, 0);
    api.rect(w * 0.15 + 30, gy - 20, w * 0.3 - 30, 14, blue, ink, 0);
    api.rect(w * 0.45 - 10, gy - 160 - rise + 40, 180, 16, mut, ink, 2);
    api.rect(w * 0.45 + 20, gy - 210 - rise + 40, 120, 50, red, ink, 8);
    api.arrow(w * 0.15 + 15, gy - 200, w * 0.15 + 15, gy - 130, ink, 3);
    api.label("F", w * 0.15 + 30, gy - 180, ink, 14);
  },
});
