// 实验 17.3 行车防摆与转动圆环上的珠子（配 17.3 节）。测量型实验。
// 行车场景（机器人问题）：自动化仓库的行车，吊绳长 2.60 m（学生不知道，与算例 17.3.2 的 4.0 m 不同）。
// 方式 0：小车不动，货物拉开 5° 松手，测摆动周期，求绳长。方式 1：小车由静止匀加速到 1.0 m/s，匀速，再匀减速停下，共走 6.0 m；
// 加速和减速的时间都是 t_a。货物的运动方程 lθ̈ + Ẍcosθ + g sinθ = 0（式 (17.3.5)），RK4 积分。t_a 取一个摆动周期时到站后几乎不摆。
// 圆环场景（生活中的例子，离心调速器）：半径 0.20 m 的圆环绕竖直直径转动，珠子带一点摩擦（阻尼 1.0 s⁻¹），由最低点附近出发，停在平衡位置。
const L173 = 2.60, g173 = 9.81, D173 = 6.0, V173 = 1.0, R173 = 0.20, B173 = 1.0;
const T173 = 2 * Math.PI * Math.sqrt(L173 / g173);
const CACHE173 = {};

function crane173(mode, ta) {                                                 // 返回 {dt, th[], x[], tEnd, tArr, cross[], resid}
  const key = mode + "|" + ta; if (CACHE173[key]) return CACHE173[key];
  const h = 0.002, every = 5, a = V173 / ta, tc = (D173 - V173 * ta) / V173, t1 = ta, t2 = ta + tc, t3 = 2 * ta + tc;
  const acc = (t) => mode === 0 ? 0 : (t < t1 ? a : t < t2 ? 0 : t < t3 ? -a : 0);
  const pos = (t) => {
    if (mode === 0) return 0;
    if (t < t1) return 0.5 * a * t * t;
    if (t < t2) return 0.5 * a * t1 * t1 + V173 * (t - t1);
    if (t < t3) { const u = t - t2; return 0.5 * a * t1 * t1 + V173 * tc + V173 * u - 0.5 * a * u * u; }
    return D173;
  };
  const f = (t, th, w) => [w, -(acc(t) * Math.cos(th) + g173 * Math.sin(th)) / L173];
  const tEnd = mode === 0 ? 40 : t3 + 10;
  let th = mode === 0 ? 5 * Math.PI / 180 : 0, w = 0, t = 0, prev = th, resid = 0;
  const TH = [th], X = [0], cross = [];
  const n = Math.round(tEnd / h);
  for (let i = 1; i <= n; i++) {
    const k1 = f(t, th, w), k2 = f(t + h / 2, th + h / 2 * k1[0], w + h / 2 * k1[1]);
    const k3 = f(t + h / 2, th + h / 2 * k2[0], w + h / 2 * k2[1]), k4 = f(t + h, th + h * k3[0], w + h * k3[1]);
    th += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); w += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); t += h;
    if (prev < 0 && th >= 0) cross.push(t - h * th / (th - prev));             // 货物向右越过竖直位置的时刻（线性插值）
    prev = th;
    if (mode === 1 && t > t3) resid = Math.max(resid, Math.abs(th));
    if (i % every === 0) { TH.push(th); X.push(pos(t)); }
  }
  return (CACHE173[key] = { dt: h * every, th: TH, x: X, tEnd, tArr: mode === 0 ? 0 : t3, cross, resid: resid * 180 / Math.PI });
}

function hoop173(w) {                                                         // 珠子：θ̈ = sinθ(ω²cosθ − g/R) − bθ̇
  const key = "h|" + w; if (CACHE173[key]) return CACHE173[key];
  const h = 0.002, every = 5, tEnd = 15, f = (th, v) => [v, Math.sin(th) * (w * w * Math.cos(th) - g173 / R173) - B173 * v];
  let th = 0.10, v = 0; const TH = [th];
  for (let i = 1; i <= Math.round(tEnd / h); i++) {
    const k1 = f(th, v), k2 = f(th + h / 2 * k1[0], v + h / 2 * k1[1]), k3 = f(th + h / 2 * k2[0], v + h / 2 * k2[1]), k4 = f(th + h * k3[0], v + h * k3[1]);
    th += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); v += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]);
    if (i % every === 0) TH.push(th);
  }
  return (CACHE173[key] = { dt: h * every, th: TH, tEnd });
}
const eq173 = (w) => (w * w * R173 > g173 ? Math.acos(g173 / (R173 * w * w)) : 0) * 180 / Math.PI;
const at173 = (r, t) => r.th[Math.min(r.th.length - 1, Math.max(0, Math.round(t / r.dt)))];
const RUN173 = {};
const key173 = (api, p) => { p = p || api.p; return api.scene === "crane" ? `c|${p.mode}|${p.ta}` : `h|${p.w}`; };

WQ.lab({
  title: ["实验 17.3 行车防摆与转动圆环上的珠子", "Lab 17.3 Anti-sway crane moves and a bead on a spinning hoop"],
  goal: ["由货物的摆动周期测出吊绳长度，安排小车的加速和减速，让货物到站时不再摆动；调圆环的转速，让珠子停在指定的位置。",
         "Measure the rope length from the load's swing period, then plan the trolley's acceleration and braking so the load arrives without swinging; set the hoop's spin so the bead settles where you want."],
  scenes: [
    { id: "crane", robot: true, name: ["自动化仓库的行车", "Warehouse crane"], hide: ["w"],
      problem: { title: ["机器人问题：怎样让吊着的货物到站就不晃？", "Robot problem: how do you make a hanging load arrive without swinging?"],
                 text: ["行车的小车由电机带动，吊绳的长度不知道。方式 0：小车不动，把货物拉开 5° 松手，测摆动的周期。方式 1：小车从静止匀加速到 1.0 m/s，匀速行驶，再匀减速停下，共走 6.0 m，加速和减速的时间都是 t_a。点“开始”，看货物的摆动。",
                        "The trolley is driven by a motor; the rope length is unknown. Mode 0: the trolley stays put; pull the load out 5° and let go, and measure the swing period. Mode 1: the trolley accelerates from rest to 1.0 m/s, cruises, then brakes to a stop after 6.0 m; accelerating and braking both take t_a. Press “Start” and watch the load swing."] } },
    { id: "hoop", name: ["转动圆环上的珠子", "Bead on a spinning hoop"], hide: ["mode", "ta", "ans"],
      problem: { title: ["生活中的例子：离心调速器的飞球为什么会张开？", "Everyday example: why do a governor's flyballs swing out?"],
                 text: ["半径 0.20 m 的竖直圆环由电机带着绕竖直直径转动，环上套着一颗珠子（有一点摩擦）。珠子从最低点附近出发。选圆环的角速度 ω，点“开始”，看珠子最后停在哪里。",
                        "A vertical hoop of radius 0.20 m is spun by a motor about its vertical diameter; a bead slides on it with a little friction. The bead starts near the bottom. Choose the hoop's angular velocity ω, press “Start” and see where the bead settles."] } },
  ],
  params: [
    { id: "mode", name: ["方式：0 摆动测试，1 运送 6.0 m", "Mode: 0 swing test, 1 carry 6.0 m"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "ta", name: ["加速、减速的时间 t_a", "Acceleration and braking time t_a"], min: 1.0, max: 6.0, step: 0.05, value: 2.0, unit: "s", digits: 2 },
    { id: "ans", name: ["你测得的绳长", "Your rope length"], min: 1.00, max: 5.00, step: 0.01, value: 1.00, unit: "m", digits: 2 },
    { id: "w", name: ["圆环的角速度 ω", "Hoop angular velocity ω"], min: 0, max: 15, step: 0.05, value: 5, unit: "rad/s", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "rope", robot: true, text: ["行车：用方式 0 测出摆动周期（多测几个周期取平均），求吊绳的长度，调到“你测得的绳长”，提交（相差 2% 以内）。", "Crane: in mode 0 measure the swing period (time several swings), work out the rope length, set it as “Your rope length” and submit (within 2%)."],
      demo: { scene: "crane", set: { mode: 0, ans: 2.60 }, press: ["start", "submit"], wait: 2 } },
    { id: "nosway", robot: true, text: ["行车：用方式 1 运送货物，选加速、减速的时间，让货物到站后的摆角不超过 0.3°，运行后提交。", "Crane: carry the load in mode 1 and choose the acceleration time so the load swings no more than 0.3° after arriving; run and submit."],
      demo: { scene: "crane", set: { mode: 1, ta: 3.25 }, press: ["start", "submit"], wait: 2 } },
    { id: "bead", text: ["圆环：调圆环的角速度，让珠子停在偏离最低点 60° 的地方（相差 1° 以内），运行后提交。", "Hoop: set the angular velocity so the bead settles 60° from the bottom (within 1°); run and submit."],
      demo: { scene: "hoop", set: { w: 9.9 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["为什么加速时间取一个摆动周期，加速结束时货物就不摆了？到站时的减速也要这样安排吗？如果绳长测错了 5%，残留的摆动大约多大？圆环转得比临界角速度慢时，珠子为什么回到最低点？",
          "Why does accelerating for exactly one swing period leave the load still? Must the braking be planned the same way? If the rope length were off by 5%, roughly how much swing would remain? Below the critical spin rate, why does the bead return to the bottom?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; },
  start(api, s) {
    s.ran = true; s.k = Object.assign({}, api.p);
    s.r = api.scene === "crane" ? crane173(api.p.mode, api.p.ta) : hoop173(api.p.w);
  },
  update(dt, api, s) { if (s.r && api.t >= s.r.tEnd) { RUN173[key173(api, s.k)] = true; api.stop(); } },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = s.ran && s.k ? Object.assign({}, s.k, { ans: api.p.ans }) : api.p, have = s.ran || RUN173[key173(api)]; let ok = false;
    if (api.scene === "crane" && have) {
      if (p.mode === 0 && Math.abs(p.ans - L173) <= 0.02 * L173) { api.done("rope"); ok = true; }
      if (p.mode === 1 && crane173(1, p.ta).resid <= 0.3) { api.done("nosway"); ok = true; }
    }
    if (api.scene === "hoop" && have && Math.abs(eq173(p.w) - 60) <= 1) { api.done("bead"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    const live = s.ran && s.r, t = live ? Math.min(api.t, s.r.tEnd) : 0;
    if (api.scene === "crane") {
      if (!live) return [[["时间", "Time"], "—"], [["摆角", "Swing angle"], "—"], sub];
      const r = s.r, th = at173(r, t) * 180 / Math.PI, rows = [[["时间", "Time"], f(t, 2) + " s"], [["摆角", "Swing angle"], f(th, 2) + "°"]];
      if (s.k.mode === 0) {
        const c = r.cross.filter((x) => x <= t);
        rows.push([["货物向右越过竖直位置的次数", "Times the load has crossed vertical moving right"], String(c.length)]);
        rows.push([["最近一次越过的时刻", "Time of the latest crossing"], c.length ? f(c[c.length - 1], 2) + " s" : "—"]);
      } else {
        rows.push([["小车位置", "Trolley position"], f(r.x[Math.min(r.x.length - 1, Math.round(t / r.dt))], 2) + " m"]);
        rows.push([["到站后的最大摆角", "Largest swing after arrival"], t >= r.tEnd - 1e-9 && !api.running ? f(r.resid, 2) + "°" : (t > r.tArr ? api.T("测量中…", "measuring…") : "—")]);
      }
      return rows.concat([sub]);
    }
    if (!live) return [[["时间", "Time"], "—"], [["珠子偏离最低点的角", "Bead angle from the bottom"], "—"], sub];
    return [[["时间", "Time"], f(t, 2) + " s"], [["珠子偏离最低点的角", "Bead angle from the bottom"], f(at173(s.r, t) * 180 / Math.PI, 1) + "°"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue"), amber = css("--amber");
    const live = s.ran && s.r, t = live ? Math.min(api.t, s.r.tEnd) : 0;
    if (api.scene === "crane") {
      const sc = w * 0.8 / 7.0, x0 = w * 0.1 + 0.5 * sc, y0 = h * 0.12, rope = h * 0.6;   // 绳画成固定的长度，不按比例，绳长要靠测周期
      api.line(w * 0.05, y0, w * 0.95, y0, ink, 4);
      const mode1 = live ? s.k.mode === 1 : api.p.mode === 1;
      if (mode1) { api.line(x0 + D173 * sc, y0 + 8, x0 + D173 * sc, y0 + 22, red, 2); api.label(api.T("终点", "stop"), x0 + D173 * sc, y0 + 36, red, 12, "center"); }
      const X = live ? s.r.x[Math.min(s.r.x.length - 1, Math.round(t / s.r.dt))] : 0;
      const th = live ? at173(s.r, t) : (api.p.mode === 0 ? 5 * Math.PI / 180 : 0);
      const cx = x0 + X * sc, lx = cx + rope * Math.sin(th), ly = y0 + rope * Math.cos(th);
      api.rect(cx - 26, y0 - 12, 52, 20, mut, ink, 4);
      api.line(cx, y0 + 8, lx, ly, ink, 2);
      api.line(cx, y0 + 8, cx, y0 + rope + 10, mut, 1, [4, 4]);
      api.rect(lx - 22, ly, 44, 34, amber, ink, 3);
      return;
    }
    const cx = w * 0.5, cy = h * 0.5, Rp = Math.min(w, h) * 0.32, th = live ? at173(s.r, t) : 0.10;
    const om = live ? s.k.w : api.p.w, ph = om * t, cphi = Math.cos(ph);
    api.line(cx, cy - Rp - 30, cx, cy + Rp + 30, mut, 2, [6, 4]);
    const c = api.ctx; c.save(); c.strokeStyle = blue; c.lineWidth = 3; c.beginPath();
    c.ellipse(cx, cy, Math.max(1, Rp * Math.abs(cphi)), Rp, 0, 0, 2 * Math.PI); c.stroke(); c.restore();
    const bx = cx + Rp * Math.sin(th) * cphi, by = cy + Rp * Math.cos(th);
    api.circle(bx, by, 9, red, ink);
    api.label(api.T("转轴", "axis"), cx + 8, cy - Rp - 18, mut, 12);
  },
});
