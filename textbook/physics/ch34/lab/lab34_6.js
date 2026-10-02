// 实验 34.6 直流电机与反电动势（配 34.6 节）。永磁直流电机：U = IR + Kω，电磁转矩 KI；K = 0.05 V·s/rad，R = 0.5 Ω，
// 转子惯量 J = 2×10⁻⁴ kg·m²，粘性摩擦 b = 5×10⁻⁶ N·m·s。拖动示教场景：电机经 100:1 减速器接关节，用手转动关节。
// “测电机参数”场景：一台参数未知的电机（学生不知道 K、R），稳态读数带随机误差；记录的数据放在闭包里，重置时不丢。
const K_34 = 0.05, RA_34 = 0.5, J_34 = 2e-4, B_34 = 5e-6, GEAR_34 = 100;
const KX_34 = 0.062, RX_34 = 0.42, MF_34 = 0.01, UX_34 = 24;          // 未知电机：K、R、摩擦转矩、电压
const rec34_6 = { pts: [] };                                         // (M_L, 转速读数 r/min, 电流读数 A)
const read34_6 = (ML) => {
  const I = (ML + MF_34) / KX_34, w = (UX_34 - I * RX_34) / KX_34;
  if (w <= 0) return [ML, 0, Math.round(UX_34 / RX_34 * 100) / 100];
  const n = w * 60 / (2 * Math.PI) * (1 + (Math.random() * 2 - 1) * 0.003);  // 转速计 ±0.3%
  const Ir = I + (Math.random() * 2 - 1) * 0.03;                              // 电流表 ±0.03 A
  return [ML, Math.round(n), Math.round(Ir * 100) / 100];
};
const ok34_6 = (api) => rec34_6.pts.length >= 6 && Math.abs(api.p.Khat - KX_34) / KX_34 < 0.02 && Math.abs(api.p.Rhat - RX_34) / RX_34 < 0.05;
WQ.lab({
  title: ["实验 34.6 直流电机与反电动势", "Lab 34.6 DC motor and back emf"],
  goal: ["看电机转起来以后电流为什么变小；测空载转速和堵转电流；再看用手拖动断电的关节时，端子开路与短路有什么不同。",
         "See why the current falls once the motor turns; measure the no-load speed and stall current; then feel the difference between open and shorted terminals when an unpowered joint is turned by hand."],
  scenes: [
    { id: "motor", robot: true, name: ["电机起动与带载", "Starting and loading"], hide: ["hand", "short", "Khat", "Rhat"],
      problem: { title: ["机器人问题：关节电机的电流", "Robot problem: a joint motor's current"],
                 text: ["24 V 直流电机由静止起动。起动瞬间电流多大？转起来以后为什么电流变小？加上负载转矩后转速降到多少？",
                        "A 24 V DC motor starts from rest. How large is the starting current? Why does it fall as it speeds up? How far does the speed drop under load?"] } },
    { id: "hand", robot: true, name: ["拖动示教", "Hand guiding"], hide: ["U", "load", "Khat", "Rhat"],
      problem: { title: ["机器人问题：用手拖动断电的机械臂", "Robot problem: moving an unpowered arm by hand"],
                 text: ["用手以恒定转速转动关节。端子开路时测到电压；端子短接时手上感到很大的阻力，这就是动态制动。",
                        "Turn the joint by hand at a steady speed. With open terminals you measure a voltage; shorting them makes the joint hard to turn: dynamic braking."] } },
    { id: "measure", robot: true, name: ["测电机参数", "Measure a motor"], hide: ["U", "hand", "short"],
      problem: { title: ["机器人问题：手册丢了的关节电机", "Robot problem: a joint motor without its datasheet"],
                 text: ["一台 24 V 电机，参数不知道。在测功机上加不同的负载转矩，读出稳态转速和电流，用最小二乘拟合机械特性，求出电机常数 K 和电枢电阻 R。",
                        "A 24 V motor of unknown parameters sits on a dynamometer. Apply several load torques, read the steady speed and current, fit the characteristic by least squares and find the motor constant K and the armature resistance R."] } },
  ],
  params: [
    { id: "U", name: ["电源电压 U", "Supply U"], min: 0, max: 24, step: 1, value: 24, unit: "V", digits: 0 },
    { id: "load", name: ["负载转矩 M_L", "Load torque M_L"], min: 0, max: 3, step: 0.05, value: 0, unit: "N·m", digits: 2 },
    { id: "hand", name: ["关节转速（手转）", "Joint speed (by hand)"], min: 0, max: 20, step: 1, value: 10, unit: "r/min", digits: 0 },
    { id: "short", name: ["端子：0 开路 / 1 短路", "Terminals: 0 open / 1 shorted"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "Khat", name: ["你算出的 K", "Your K"], min: 0.03, max: 0.09, step: 0.0005, value: 0.05, unit: "V·s/rad", digits: 4 },
    { id: "Rhat", name: ["你算出的 R", "Your R"], min: 0.2, max: 1, step: 0.01, value: 0.5, unit: "Ω", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] },
            { id: "record", name: ["读数并记录", "Read and record"] }, { id: "sweep", name: ["0–2 N·m 依次测一遍", "Sweep 0–2 N·m"] },
            { id: "clear", name: ["清空记录", "Clear records"] }],
  legend: [{ color: "var(--blue)", name: ["转速", "speed"] }, { color: "var(--red)", name: ["电流", "current"] }],
  tasks: [
    { id: "noload", robot: true, text: ["U = 24 V、空载：读出稳定转速，与 U/K 比较。", "U = 24 V, no load: read the steady speed and compare with U/K."],
      demo: { scene: "motor", set: { U: 24, load: 0 }, press: ["start"], wait: 4 } },
    { id: "stall", robot: true, text: ["加大负载转矩直到电机转不动（堵转），读出堵转电流。", "Increase the load until the motor stalls; read the stall current."],
      demo: { scene: "motor", set: { U: 24, load: 2.5 }, press: ["start"], wait: 4 } },
    { id: "brake", robot: true, text: ["拖动示教：关节 10 r/min，端子短路，读出电机轴上的制动转矩和关节上的阻力矩。", "Hand guiding: 10 r/min at the joint with shorted terminals; read the braking torque at the motor and at the joint."],
      demo: { scene: "hand", set: { hand: 10, short: 1 }, press: ["start"], wait: 3 } },
    { id: "meas", robot: true, text: ["测电机参数：至少记录 6 个点，自己拟合求出 K 和 R，把“你算出的 K”调到与真实值相差 2% 以内、“你算出的 R”相差 5% 以内。",
                                       "Measure: record at least 6 points, fit K and R yourself, and set “Your K” within 2% and “Your R” within 5% of the true values."],
      demo: { scene: "measure", set: { Khat: 0.062, Rhat: 0.42 }, press: ["clear", "sweep"], wait: 1 } },
  ],
  think: ["电机堵转时为什么容易烧坏？电机驱动器为什么要限制起动电流？", "Why does a stalled motor burn out easily? Why do drives limit the starting current?"],

  reset(api, s) { s.w = 0; s.I = 0; s.hist = []; s.peakI = 0; s.done = false; },
  update(dt, api, s) {
    if (api.scene === "measure") { api.stop(); return; }
    const step = dt * 0.25;                                   // 慢放 4 倍（机电时间常数约 0.04 s）
    if (api.scene === "motor") {
      for (let i = 0; i < 20; i++) {
        const h = step / 20;
        s.I = (api.p.U - K_34 * s.w) / RA_34;                 // 忽略电感：电流随反电动势即时变化
        let torque = K_34 * s.I - B_34 * s.w;
        if (s.w <= 0 && torque <= api.p.load) { s.w = 0; continue; }   // 负载转矩大于电磁转矩：转不动
        s.w += (torque - api.p.load) / J_34 * h;
        if (s.w < 0) s.w = 0;
      }
      s.peakI = Math.max(s.peakI, s.I);
      s.hist.push([api.t * 0.25, s.w * 60 / (2 * Math.PI), s.I]);
      if (api.t * 0.25 > 0.4) { api.stop(); fin34_6(api, s); }
    } else {
      s.w = api.p.hand * 2 * Math.PI / 60 * GEAR_34;
      s.I = api.p.short ? K_34 * s.w / RA_34 : 0;
      s.hist.push([api.t * 0.25, s.w * 60 / (2 * Math.PI), s.I]);
      if (api.t * 0.25 > 0.2) { api.stop(); fin34_6(api, s); }
    }
  },
  action(id, api, s) {
    if (api.scene !== "measure") return;
    if (id === "clear") rec34_6.pts.length = 0;
    if (id === "record") rec34_6.pts.push(read34_6(api.p.load));
    if (id === "sweep") for (let k = 0; k <= 8; k++) rec34_6.pts.push(read34_6(k * 0.25));
    s.last = rec34_6.pts[rec34_6.pts.length - 1] || null;
    if (ok34_6(api)) api.done("meas");
  },
  change(api, s, pid) {
    if (api.scene === "measure" && (pid === "Khat" || pid === "Rhat") && ok34_6(api)) api.done("meas");
  },
  readouts(api, s) {
    const f = api.fmt, emf = K_34 * s.w;
    if (api.scene === "measure") {
      return [[["电源电压", "Supply"], UX_34 + " V"], [["负载转矩 M_L", "Load torque M_L"], f(api.p.load, 2) + " N·m"],
              [["最近一次转速读数", "Last speed reading"], s.last ? s.last[1] + " r/min" : "—"],
              [["最近一次电流读数", "Last current reading"], s.last ? f(s.last[2], 2) + " A" : "—"],
              [["已记录点数", "Points recorded"], String(rec34_6.pts.length)]];
    }
    if (api.scene === "motor") {
      return [[["转速", "Speed"], f(s.w * 60 / (2 * Math.PI), 0) + " r/min"], [["反电动势 Kω", "Back emf Kω"], f(emf, 2) + " V"],
              [["电流 I", "Current I"], f(s.I, 2) + " A"], [["起动瞬间电流 U/R", "Starting current U/R"], f(api.p.U / RA_34, 1) + " A"],
              [["电磁转矩 KI", "Motor torque KI"], f(K_34 * s.I, 3) + " N·m"]];
    }
    return [[["电机转速", "Motor speed"], f(s.w * 60 / (2 * Math.PI), 0) + " r/min"],
            [["端子电压", "Terminal voltage"], f(api.p.short ? 0 : emf, 2) + " V"],
            [["短路电流", "Short-circuit current"], f(s.I, 2) + " A"],
            [["电机轴上的制动转矩", "Braking torque at the motor"], f(K_34 * s.I, 3) + " N·m"],
            [["关节上的阻力矩（×100）", "Resisting torque at the joint (×100)"], f(K_34 * s.I * GEAR_34, 1) + " N·m"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, cx = w * 0.18, cy = h * 0.3, R = h * 0.17;
    if (api.scene === "measure") {
      api.circle(cx, cy, R, css("--panel"), css("--ink"));
      api.label("M", cx, cy + 5, css("--ink"), 16, "center");
      api.rect(cx + R, cy - 8, 60, 16, css("--muted"));
      api.rect(cx + R + 60, cy - 30, 40, 60, css("--panel"), css("--ink"), 4);
      api.label(api.T("测功机", "dynamometer"), cx + R + 80, cy + 48, css("--muted"), 12, "center");
      const P1 = api.plot(w * 0.38, 20, w * 0.58, h * 0.42, [{ pts: [], color: css("--blue") }],
                          { xmin: 0, xmax: 2.2, ymin: 0, ymax: 4000, xlabel: "M_L / (N·m)", ylabel: "r/min" });
      rec34_6.pts.forEach((p) => api.circle(P1.X(p[0]), P1.Y(p[1]), 4, css("--blue"), css("--ink")));
      const P2 = api.plot(w * 0.38, h * 0.55, w * 0.58, h * 0.38, [{ pts: [], color: css("--red") }],
                          { xmin: 0, xmax: 2.2, ymin: 0, ymax: 40, xlabel: "M_L / (N·m)", ylabel: "I / A" });
      rec34_6.pts.forEach((p) => api.circle(P2.X(p[0]), P2.Y(p[2]), 4, css("--red"), css("--ink")));
      return;
    }
    api.circle(cx, cy, R, css("--panel"), css("--ink"));
    const ang = (s.angle = (s.angle || 0) + s.w * 0.004);
    for (let k = 0; k < 3; k++) { const a = ang + k * 2 * Math.PI / 3; api.line(cx, cy, cx + R * 0.9 * Math.cos(a), cy + R * 0.9 * Math.sin(a), css("--accent"), 4); }
    api.label(api.scene === "motor" ? "M" : api.T("关节", "joint"), cx, cy + R + 18, css("--muted"), 13, "center");
    const P = api.plot(w * 0.38, 20, w * 0.58, h * 0.42, [{ pts: s.hist.map((q) => [q[0], q[1]]), color: css("--blue") }],
                       { xmin: 0, xmax: api.scene === "motor" ? 0.4 : 0.2, ymin: 0, ymax: 5000, xlabel: "t / s", ylabel: "r/min" });
    api.plot(w * 0.38, h * 0.55, w * 0.58, h * 0.38, [{ pts: s.hist.map((q) => [q[0], q[2]]), color: css("--red") }],
             { xmin: 0, xmax: api.scene === "motor" ? 0.4 : 0.2, ymin: 0, ymax: 50, xlabel: "t / s", ylabel: "I / A" });
  },
});

function fin34_6(api, s) {
  if (s.done) return; s.done = true;
  if (api.scene === "motor") {
    const n = s.w * 60 / (2 * Math.PI), n0 = api.p.U / K_34 * 60 / (2 * Math.PI);
    if (api.p.U === 24 && api.p.load === 0 && Math.abs(n - n0) / n0 < 0.01) api.done("noload");
    if (api.p.U === 24 && s.w < 1 && s.I > 47) api.done("stall");
  } else if (api.p.short === 1 && api.p.hand === 10 && K_34 * s.I > 0.5) api.done("brake");
}
