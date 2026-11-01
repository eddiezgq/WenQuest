// 实验 10.4 能量守恒：无动力输送线与过山车（配 10.4、10.5 节）。测量型实验。
// 输送线场景：周转箱从倾角 12° 的无动力滚筒段由静止滑下（起点高度 h 可调），再沿 6.0 m 长的水平滚筒段滑到取货位。
// 滚动阻力系数 μ_r（学生不知道）。水平段上离起点 0.5 m、2.5 m 处各有一个光电门，挡光片宽 0.10 m，读挡光时间（修约到 0.1 ms）。
// 学生由两处速度和距离 2.0 m 求 μ_r；再用能量守恒算出使箱子以 0.50 m/s 到达取货位的高度。到达速度提交后才显示。
// 过山车场景（生活中的例子）：不计摩擦，出发高度 h、圆环半径 R 可调；环内某处支持力变负即脱轨。
// 判定都用解析式算，不依赖动画是否放完。
const g104 = 9.81, MU104 = 0.035, TH104 = 12 * Math.PI / 180, FLAT104 = 6.0, G1_104 = 0.5, G2_104 = 2.5, FLAG104 = 0.10;
const vAt104 = (h, s) => {                                                  // 水平段上 s 处的速度（未到则为 0）
  const E = 2 * g104 * (h - MU104 * (h / Math.tan(TH104) + s));          // v² = 2g(h − μ(h cot θ + s))
  return E > 0 ? Math.sqrt(E) : 0;
};
const RUN104 = {};                                                         // 已经运行过的起点高度（改滑块后仍记得，读数不丢）
const gate104 = (h, s) => { const v = vAt104(h, s + FLAG104 / 2); return v > 0 ? Math.round(FLAG104 / v * 1e4) / 10 : null; };   // ms
function coaster104(h, R) {                                                  // 结果：through 通过 / back 速度先降到零、滑回 / off 支持力先变负、脱轨
  for (let i = 0; i <= 3600; i++) {
    const a = Math.PI * i / 1800, v2 = 2 * g104 * (h - R * (1 - Math.cos(a)));
    if (v2 < 0) return { ok: false, how: "back", a, nbot: 1 + 2 * h / R };
    if (v2 / R + g104 * Math.cos(a) < -1e-9) return { ok: false, how: "off", a, v: Math.sqrt(v2), nbot: 1 + 2 * h / R };   // 刚好为零也算通过
  }
  return { ok: true, how: "through", nbot: 1 + 2 * h / R };
}

WQ.lab({
  title: ["实验 10.4 能量守恒：无动力输送线与过山车", "Lab 10.4 Energy conservation: a gravity conveyor and a roller coaster"],
  goal: ["用两个光电门测出滚动阻力系数，再用能量守恒设计输送线的高度；在过山车上体会机械能守恒和通过圆环的条件。",
         "Measure the rolling-resistance coefficient with two light gates, then use energy conservation to size the conveyor's drop; on a roller coaster, see mechanical energy conserved and what it takes to get round a loop."],
  scenes: [
    { id: "chute", robot: true, name: ["无动力输送线", "Gravity conveyor"], hide: ["hc", "R"],
      problem: { title: ["机器人问题：周转箱要以多大的速度到达取货位？", "Robot problem: how fast should the tote reach the pick station?"],
                 text: ["夹层上的周转箱沿 12° 的无动力滚筒段滑下，再沿 6.0 m 的水平滚筒段滑到机器人的取货位。太慢会停在半路，太快会撞坏挡块。先用两个光电门测出滚动阻力系数，再算出起点高度，使箱子以 0.50 m/s 到达取货位。",
                        "Totes slide down a 12° unpowered roller section from a mezzanine, then along a 6.0 m level section to the robot's pick station. Too slow and they stop halfway; too fast and they hit the stop hard. Measure the rolling-resistance coefficient with the two light gates, then work out the start height for an arrival speed of 0.50 m/s."] } },
    { id: "coaster", name: ["过山车", "Roller coaster"], hide: ["h", "mu"],
      problem: { title: ["生活中的例子：过山车从多高出发才能通过圆环", "Everyday example: how high must the coaster start to get round the loop"],
                 text: ["车从高 h 处由静止滑下，进入半径为 R 的竖直圆环（不计摩擦，车看成质点）。在环里某处轨道对车的支持力如果要变成负的，车就会脱离轨道。调 h 和 R，点“开始”。",
                        "The car starts from rest at height h and enters a vertical loop of radius R (no friction, the car is a point). If anywhere in the loop the track would have to pull rather than push, the car leaves the track. Set h and R and press “Start”."] } },
  ],
  params: [
    { id: "h", name: ["起点高度 h", "Start height h"], min: 0.15, max: 0.40, step: 0.005, value: 0.30, unit: "m", digits: 3 },
    { id: "mu", name: ["你测得的 μ_r", "Your μ_r"], min: 0.0, max: 0.1, step: 0.001, value: 0.0, unit: "", digits: 3 },
    { id: "hc", name: ["出发高度 h", "Start height h"], min: 5, max: 30, step: 0.5, value: 20, unit: "m", digits: 1 },
    { id: "R", name: ["圆环半径 R", "Loop radius R"], min: 3, max: 12, step: 0.5, value: 6, unit: "m", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--amber)", name: ["周转箱", "tote"] }, { color: "var(--red)", name: ["过山车", "coaster car"] }],
  tasks: [
    { id: "mu", robot: true, text: ["输送线：用两个光电门的读数求滚动阻力系数 μ_r，提交（相差 0.003 以内）。", "Conveyor: from the two gate readings find μ_r and submit (within 0.003)."],
      demo: { scene: "chute", set: { h: 0.30, mu: 0.035 }, press: ["start", "submit"], wait: 2 } },
    { id: "h", robot: true, text: ["输送线：算出起点高度，使周转箱以 0.50 m/s（±0.10 m/s）到达取货位，运行后提交。", "Conveyor: compute the start height for an arrival speed of 0.50 m/s (±0.10 m/s); run it, then submit."],
      demo: { scene: "chute", set: { h: 0.265 }, press: ["start", "submit"], wait: 2 } },
    { id: "hmin", text: ["过山车：R = 6 m，找出能通过圆环的最小出发高度（按 0.5 m 一档），运行后提交。", "Coaster: with R = 6 m find the lowest start height (in 0.5 m steps) that gets round the loop; run it, then submit."],
      demo: { scene: "coaster", set: { hc: 15, R: 6 }, press: ["start", "submit"], wait: 3 } },
    { id: "Rmax", text: ["过山车：h = 20 m，找出能通过的最大圆环半径（按 0.5 m 一档），运行后提交。这时乘客在环底受多大的支持力？", "Coaster: with h = 20 m find the largest loop radius (in 0.5 m steps) the car gets round; run it, then submit. How hard does the seat push at the bottom then?"],
      demo: { scene: "coaster", set: { hc: 20, R: 8 }, press: ["start", "submit"], wait: 3 } },
  ],
  think: ["由两个光电门求 μ_r 时，为什么不需要知道箱子的质量？如果只用一个光电门，还缺什么量？过山车刚好通过圆环时，环底的支持力是重力的几倍？真实的过山车为什么把圆环做成上小下大的“水滴形”？",
          "Why don't you need the tote's mass to get μ_r from two gates? With one gate only, what would be missing? When the car just makes it round the loop, how many times its weight is the push at the bottom? Why are real coaster loops teardrop-shaped, tight at the top and wide at the bottom?"],

  reset(api, s) { s.msg = s.msg || ""; s.pos = 0; s.v = 0; s.ran = false; s.end = null; s.shown = false; s.off = false; },
  start(api, s) { s.ran = true; s.pos = 0; s.v = 0; s.end = null; s.off = false; },
  change(api, s) { s.ran = false; s.shown = false; },
  update(dt, api, s) {
    const p = api.p, n = 10, h = dt / n;
    if (api.scene === "chute") {
      const Lr = p.h / Math.sin(TH104);
      for (let i = 0; i < n; i++) {
        const a = s.pos < Lr ? g104 * (Math.sin(TH104) - MU104 * Math.cos(TH104)) : -MU104 * g104;
        s.v = Math.max(0, s.v + a * h); s.pos += s.v * h;
      }
      if (s.pos >= Lr + FLAT104) { s.pos = Lr + FLAT104; s.end = "arrive"; RUN104[p.h] = "arrive"; api.stop(); }
      else if (s.v === 0 && s.pos > Lr) { s.end = "stop"; RUN104[p.h] = "stop"; api.stop(); }
      else if (s.pos > Lr + G2_104 + FLAG104 && !RUN104[p.h]) RUN104[p.h] = "gates";
    } else {
      s.pos += dt * 60; const c = coaster104(p.hc, p.R);
      if (s.pos > 300) { s.end = c.how; api.stop(); }
    }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "chute") {
      s.shown = !!RUN104[p.h];
      if (Object.keys(RUN104).length && Math.abs(p.mu - MU104) <= 0.003) { api.done("mu"); ok = true; }      // 先运行读光电门，再调滑块提交
      if (RUN104[p.h] && Math.abs(vAt104(p.h, FLAT104) - 0.5) <= 0.10) { api.done("h"); ok = true; }
    } else if (s.ran) {
      const c = coaster104(p.hc, p.R);
      if (Math.abs(p.R - 6) < 1e-9 && c.ok && !coaster104(p.hc - 0.5, 6).ok) { api.done("hmin"); ok = true; }
      if (Math.abs(p.hc - 20) < 1e-9 && c.ok && !coaster104(20, p.R + 0.5).ok) { api.done("Rmax"); ok = true; }
    }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "chute") {
      const Lr = p.h / Math.sin(TH104), past = (x) => (s.ran && s.pos >= Lr + x + FLAG104) || (!s.ran && !!RUN104[p.h]);
      const t1 = gate104(p.h, G1_104), t2 = gate104(p.h, G2_104);
      return [[["起点高度 h", "Start height h"], f(p.h, 3) + " m"],
        [["光电门 1（水平段 0.5 m 处）", "Gate 1 (0.5 m along the level)"], past(G1_104) && t1 ? f(t1, 1) + " ms" : "—"],
        [["光电门 2（水平段 2.5 m 处）", "Gate 2 (2.5 m along the level)"], past(G2_104) && t2 ? f(t2, 1) + " ms" : "—"],
        [["到达取货位（提交后显示）", "At the pick station (after Submit)"], RUN104[p.h] === "stop" ? api.T("停在半路", "stopped short") : s.shown && RUN104[p.h] === "arrive" ? f(vAt104(p.h, FLAT104), 2) + " m/s" : RUN104[p.h] === "arrive" ? api.T("已到达", "arrived") : "—"], sub];
    }
    const c = coaster104(p.hc, p.R);
    return [[["出发高度 h", "Start height h"], f(p.hc, 1) + " m"], [["圆环半径 R", "Loop radius R"], f(p.R, 1) + " m"],
      [["结果", "Result"], s.end === "through" ? api.T("通过圆环", "made it round") : s.end === "off" ? api.T("在环里脱轨", "left the track in the loop") : s.end === "back" ? api.T("没上去，滑回", "stalled and slid back") : "—"],
      [["环底支持力 / mg", "Push at the bottom / mg"], s.ran && s.end ? f(c.nbot, 1) : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue");
    if (api.scene === "chute") {
      const Lr = p.h / Math.sin(TH104), tot = Lr * Math.cos(TH104) + FLAT104, sc = (w * 0.86) / tot, ox = w * 0.06, oy = h * 0.62;
      const X = (x) => ox + x * sc, Y = (y) => oy - y * sc * 3;                     // 竖直方向放大 3 倍
      const x0 = Lr * Math.cos(TH104);
      api.line(X(0), Y(p.h), X(x0), Y(0), ink, 3); api.line(X(x0), Y(0), X(tot), Y(0), ink, 3);
      api.rect(X(tot), Y(0) - 30, 6, 30, mut);
      [G1_104, G2_104].forEach((g, i) => { const gx = X(x0 + g); api.rect(gx - 3, Y(0) - 60, 6, 22, blue); api.label(api.T(`光电门 ${i + 1}`, `gate ${i + 1}`), gx, Y(0) - 66, blue, 11, "center"); });
      let bx, by;
      if (s.pos < Lr) { const d = s.pos; bx = X(d * Math.cos(TH104)); by = Y(p.h - d * Math.sin(TH104)); }
      else { bx = X(x0 + s.pos - Lr); by = Y(0); }
      api.rect(bx - 14, by - 22, 28, 20, css("--amber"), ink, 3);
      api.label(api.T("取货位", "pick station"), X(tot) - 6, Y(0) + 22, mut, 12, "right");
      api.label(api.T("（竖直方向放大 3 倍）", "(vertical scale ×3)"), w * 0.5, h * 0.92, mut, 11, "center");
      return;
    }
    const R = p.R, H = p.hc, L = 30, tot = L + 6 + R + 10, sc = Math.min((w * 0.9) / tot, (h * 0.8) / Math.max(H, 2 * R)), ox = w * 0.05, oy = h * 0.88;
    const X = (x) => ox + x * sc, Y = (y) => oy - y * sc;
    const pts = [];
    for (let i = 0; i <= 60; i++) { const x = L * i / 60; pts.push([x, H / 2 * (1 + Math.cos(Math.PI * x / L))]); }
    pts.push([L + 6, 0]);
    for (let i = 0; i <= 120; i++) { const a = -Math.PI / 2 + 2 * Math.PI * i / 120; pts.push([L + 6 + R * Math.cos(a), R + R * Math.sin(a)]); }
    pts.push([L + 6 + R + 10, 0]);
    const ctx = api.ctx; ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y)))); ctx.strokeStyle = ink; ctx.lineWidth = 2.5; ctx.stroke();
    api.line(X(0), Y(H), X(L + 6 + R + 10), Y(H), mut, 1, [4, 4]);
    // 车的位置：0–100 沿下坡，100–120 平段，120–240 环；脱轨后沿抛物线飞出，没上去则停在转折点
    const c = coaster104(H, R), k = s.pos;
    let cx, cy;
    if (k <= 100) { const x = L * k / 100; cx = x; cy = H / 2 * (1 + Math.cos(Math.PI * x / L)); }
    else if (k <= 120) { cx = L + 6 * (k - 100) / 20; cy = 0; }
    else {
      const aRun = 2 * Math.PI * (k - 120) / 120, aEnd = c.ok ? 2 * Math.PI : c.a, a = Math.min(aRun, aEnd);
      cx = L + 6 + R * Math.sin(a); cy = R - R * Math.cos(a);
      if (c.how === "off" && aRun > aEnd) {                                        // 离开轨道：以切向速度做抛体运动
        const vx = c.v * Math.cos(aEnd), vy = c.v * Math.sin(aEnd), tLand = (vy + Math.sqrt(vy * vy + 2 * g104 * cy)) / g104;
        const t = Math.min(tLand, (aRun - aEnd) / (2 * Math.PI) * 2.0);           // 落到地面（环底高度）就停下
        cx += vx * t; cy = Math.max(0, cy + vy * t - 0.5 * g104 * t * t);
      }
    }
    api.circle(X(cx), Y(cy), 8, red, ink);
    if (s.end === "off") api.label(api.T("脱轨！", "off the track!"), X(L + 6), Y(2 * R) - 16, red, 16, "center");
    if (s.end === "back") api.label(api.T("没上去，滑回", "stalled, slides back"), X(L + 6), Y(2 * R) - 16, red, 16, "center");
  },
});
