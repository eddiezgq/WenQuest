// 实验 12.5 测转动惯量（配 12.5 节）。测量型实验。
// 试验台场景（机器人问题）：UR5e 小臂装在竖直轴的试验台上，在水平面内转动（重力不产生力矩）。电机给恒定力矩 M，
// 编码器读出 t = 2.000 s 时的角速度。轴承有不变的摩擦力矩 0.055 N·m（与算例 12.5.2 的 0.040 不同），学生不知道，要用两个不同的力矩求出 J 和摩擦力矩。
// 零件模型给出小臂绕肘关节 J = 0.1186 kg·m²（算例 12.3.2）；试验台上的“真实”小臂带着线缆、螺栓，J = 0.1250 kg·m²（比模型大约 5%），
// 末端加 1 kg 负载（离轴 0.392 m）后 J = 0.1250 + 0.392² = 0.27866 kg·m²。场景说明里公开的只有模型值。
// 读数带 ±0.3% 以内的误差（同一设置重复做，读数相同）。
// 自行车轮场景（生活中的例子）：落体法。轮子绕水平轴自由转动，轮毂上绕线（半径 5.0 cm），线下挂质量 m 的砝码，
// 从静止下落 1.000 m，光电门测时间（±0.01 s）。轴承摩擦不计。J = m r²(g t²/(2h) − 1)。
const JA125 = 0.1250, DL125 = 0.392, MF125 = 0.055, TR125 = 2.0, JW125 = 0.115, RH125 = 0.050, H125 = 1.0, g125 = 9.81;
function h125(a) { const x = Math.sin(a * 78.233 + 1.37) * 43758.5453; return x - Math.floor(x); }
const J125 = (load) => JA125 + load * DL125 * DL125;
const al125 = (p) => Math.max(0, (p.M - MF125) / J125(p.load));
const om125 = (p) => al125(p) * TR125 * (1 + (h125(p.M * 1000 + p.load * 7) - 0.5) * 0.006);          // t = 2.000 s 时的读数
const aw125 = (m) => m * g125 / (m + JW125 / (RH125 * RH125));
const tw125 = (m) => Math.round((Math.sqrt(2 * H125 / aw125(m)) + (h125(m * 100 + 3) - 0.5) * 0.02) * 100) / 100;
const RUN125 = {};                                                        // 已经做过的设置（调“你测得的 J”滑块后读数仍在）
const key125 = (api) => api.scene === "rig" ? `rig|${api.p.M}|${api.p.load}` : `wheel|${api.p.m}`;

WQ.lab({
  title: ["实验 12.5 测转动惯量", "Lab 12.5 Measuring a moment of inertia"],
  goal: ["用恒定力矩让物体转起来，由角加速度求转动惯量；用两个力矩消去未知的摩擦力矩；与零件模型的计算值和平行轴定理的预测比较。",
         "Spin a body up with a constant torque and get its moment of inertia from the angular acceleration; use two torques to eliminate the unknown friction torque; compare with the value computed from the part model and with the parallel-axis prediction."],
  scenes: [
    { id: "rig", robot: true, name: ["小臂试验台", "Forearm test rig"], hide: ["m"],
      problem: { title: ["机器人问题：零件模型里的转动惯量准不准？", "Robot problem: is the moment of inertia in the part model right?"],
                 text: ["控制器要用关节负载的转动惯量来算前馈力矩。UR5e 的模型给出小臂绕肘关节 J = 0.1186 kg·m²。把小臂装在竖直轴的试验台上，让它在水平面内转动：设电机力矩 M，点“开始”，编码器读出 2.000 s 时的角速度。轴承有摩擦力矩，大小不知道。",
                        "The controller needs the joint load's moment of inertia for its feed-forward torque. The UR5e model gives the forearm J = 0.1186 kg·m² about the elbow. Mount the forearm on a vertical-axis rig so it turns in a horizontal plane: set the motor torque M, press “Start”, and the encoder reports the angular velocity at 2.000 s. The bearing has a friction torque of unknown size."] } },
    { id: "wheel", name: ["自行车轮", "Bicycle wheel"], hide: ["M", "load"],
      problem: { title: ["生活中的例子：自行车轮的转动惯量", "Everyday example: a bicycle wheel's moment of inertia"],
                 text: ["自行车轮绕水平轴转动，轮毂上绕着线（绕线半径 5.0 cm），线下挂砝码。选砝码质量，点“开始”，砝码从静止下落 1.000 m，读光电门测得的时间，求轮子的转动惯量。轴承摩擦不计。",
                        "A bicycle wheel turns on a horizontal axle; a string wound on the hub (radius 5.0 cm) carries a hanging mass. Choose the mass, press “Start”: the mass falls 1.000 m from rest; read the time from the light gate and find the wheel's moment of inertia. Ignore bearing friction."] } },
  ],
  params: [
    { id: "M", name: ["电机力矩 M", "Motor torque M"], min: 0.10, max: 0.80, step: 0.01, value: 0.30, unit: "N·m", digits: 2 },
    { id: "load", name: ["末端负载：0 不加，1 加 1 kg", "End load: 0 none, 1 add 1 kg"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "m", name: ["砝码质量 m", "Hanging mass m"], min: 0.20, max: 1.00, step: 0.05, value: 0.50, unit: "kg", digits: 2 },
    { id: "J", name: ["你测得的 J", "Your J"], min: 0, max: 0.4, step: 0.001, value: 0, unit: "kg·m²", digits: 3 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "arm", robot: true, text: ["试验台：不加负载，测出小臂的 J，调到“你测得的 J”，提交（与真值相差 3% 以内；只用一个力矩、不扣摩擦力矩，会差 7% 以上）。再与零件模型的 0.1186 比较。",
                                     "Rig: without the load, measure the forearm's J, set it as “Your J” and submit (within 3% of the true value; one torque without allowing for friction misses by more than 7%). Then compare with the part-model value 0.1186."],
      demo: { scene: "rig", set: { M: 0.6, load: 0, J: 0.125 }, press: ["start", "submit"], wait: 3 } },
    { id: "load", robot: true, text: ["试验台：加上 1 kg 负载，先用任务 1 测得的 J 和平行轴定理预测，再测出 J，提交（相差 3% 以内）。", "Rig: add the 1 kg load, predict J from your task-1 result and the parallel-axis theorem, then measure it and submit (within 3%)."],
      demo: { scene: "rig", set: { M: 0.6, load: 1, J: 0.279 }, press: ["start", "submit"], wait: 3 } },
    { id: "wheel", text: ["自行车轮：测出轮子的转动惯量，提交（相差 3% 以内）。", "Bicycle wheel: measure the wheel's moment of inertia and submit (within 3%)."],
      demo: { scene: "wheel", set: { m: 0.5, J: 0.115 }, press: ["start", "submit"], wait: 3 } },
  ],
  think: ["只用一个力矩、直接用 J = M/α，结果偏大还是偏小？力矩越大，这个误差越大还是越小？为什么？落体法里，砝码越重，测得的时间越短，对测量精度有什么影响？",
          "Using one torque and J = M/α directly, is the result too big or too small? Does the error grow or shrink with a larger torque, and why? In the falling-mass method a heavier mass gives a shorter time: how does that affect the precision?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; s.th = 0; s.y = 0; },
  start(api, s) { s.ran = true; },
  update(dt, api, s) {
    const p = api.p, t = api.t;
    if (api.scene === "rig") {
      const tt = Math.min(t, TR125); s.th = 0.5 * al125(p) * tt * tt;
      if (t >= TR125) { RUN125[key125(api)] = true; api.stop(); }
      return;
    }
    const a = aw125(p.m), T = Math.sqrt(2 * H125 / a), tt = Math.min(t, T);
    s.y = 0.5 * a * tt * tt;
    if (t >= T) { RUN125[key125(api)] = true; api.stop(); }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    const have = s.ran || RUN125[key125(api)];
    if (api.scene === "rig" && have && Math.abs(p.J - J125(p.load)) <= 0.03 * J125(p.load)) { api.done(p.load ? "load" : "arm"); ok = true; }
    if (api.scene === "wheel" && have && Math.abs(p.J - JW125) <= 0.03 * JW125) { api.done("wheel"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"], have = (s.ran && !api.running) || RUN125[key125(api)];
    if (api.scene === "rig") {
      const done = Object.keys(RUN125).filter((q) => q.startsWith("rig|")).map((q) => q.split("|")).filter((q) => +q[2] === p.load).map((q) => f(+q[1], 2)).join(", ");
      return [[["2.000 s 时的角速度", "Angular velocity at 2.000 s"], have ? (al125(p) > 0 ? f(om125(p), 3) + " rad/s" : api.T("没有转动", "did not turn")) : "—"],
              [["这个负载下已测过的力矩 / (N·m)", "Torques measured with this load / (N·m)"], done || "—"], sub];
    }
    return [[["下落 1.000 m 的时间", "Time to fall 1.000 m"], have ? f(tw125(p.m), 2) + " s" : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue");
    if (api.scene === "rig") {
      const cx = w * 0.32, cy = h * 0.47, L = Math.min(w * 0.22, h * 0.33), th = s.th, u = [Math.cos(th), -Math.sin(th)];
      api.circle(cx, cy, L * 1.12, null, mut);
      api.line(cx, cy, cx + u[0] * L, cy + u[1] * L, blue, 14);
      api.circle(cx, cy, 16, css("--amber"), ink);
      if (p.load) api.circle(cx + u[0] * L, cy + u[1] * L, 12, red, ink);
      api.label(api.T("俯视：小臂在水平面内转", "top view: forearm turns in a horizontal plane"), cx, cy + L * 1.12 + 26, mut, 12, "center");
      const G = api.graph({ x: w * 0.62, y: h * 0.12, w: w * 0.34, h: h * 0.66, xmin: 0, xmax: 0.8, ymin: 0, ymax: 7,
                            xlabel: api.T("M / (N·m)", "M / (N·m)"), ylabel: api.T("α = ω/t / (rad/s²)", "α = ω/t / (rad/s²)") }).axes();
      Object.keys(RUN125).filter((q) => q.startsWith("rig|")).map((q) => q.split("|")).forEach((q) => {
        const pp = { M: +q[1], load: +q[2] }; G.point(pp.M, om125(pp) / TR125, pp.load ? red : blue);
      });
      return;
    }
    const cx = w * 0.4, cy = h * 0.3, R = Math.min(w, h) * 0.2, rh = R * 0.16, ph = s.y / RH125;
    api.circle(cx, cy, R, null, ink);
    for (let k = 0; k < 12; k++) { const a = ph + k * Math.PI / 6; api.line(cx, cy, cx + R * Math.cos(a), cy + R * Math.sin(a), mut, 1); }
    api.circle(cx, cy, rh, css("--amber"), ink);
    const top = cy, yb = top + h * 0.3 + s.y * h * 0.35;
    api.line(cx + rh, top, cx + rh, yb, ink, 1.5);
    api.rect(cx + rh - 14, yb, 28, 22 + 18 * p.m, blue, ink, 3);
    api.line(cx + rh - 40, top + h * 0.3 + h * 0.35 + 12, cx + rh + 40, top + h * 0.3 + h * 0.35 + 12, red, 2);
    api.label(api.T("光电门（下落 1.000 m 处）", "gate (1.000 m below)"), cx + rh + 48, top + h * 0.3 + h * 0.35 + 16, red, 12);
  },
});
