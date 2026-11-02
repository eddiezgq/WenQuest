// 实验 16.2 真空吸盘能吸住多重的零件（配 16.2 节）。测量型实验。
// 吸盘场景（机器人问题）：真空发生器把吸盘内抽到比大气压低 Δp（真空度，10–90 kPa）。吸盘的唇边受压会变形，
// 有效直径比名义直径小：Ø40 → 36.0 mm，Ø60 → 55.0 mm，Ø80 → 74.0 mm（学生不知道）。
// “拉脱试验”：用拉力计沿吸盘轴线慢慢拉，读出拉脱的力 F = Δp·A_有效（±1 N）。
// 搬运任务：水平吸起 8.0 kg 的钢板，向上加速 5.0 m/s²，安全系数 2：需要 2m(g + a) ≤ Δp·A_有效。
// 吸盘挂钩场景（生活中的例子）：挂钩贴在竖直的瓷砖墙上，压紧后吸盘内比大气压低 60 kPa，有效直径 45 mm（已知）。
// 挂上物体，挂钩靠摩擦力 μ·Δp·A 承重；μ = 0.55（学生不知道）。
const DEFF162 = [36.0e-3, 55.0e-3, 74.0e-3], DNOM162 = [40, 60, 80], g162 = 9.81, MS162 = 8.0, AS162 = 5.0, SF162 = 2.0;
const DPH162 = 60e3, DH162 = 45e-3, MU162 = 0.55;
function h162(a) { const x = Math.sin(a * 33.71 + 1.47) * 43758.5453; return x - Math.floor(x); }
const A162 = (k) => Math.PI * DEFF162[k] * DEFF162[k] / 4;
const pull162 = (p) => p.dp * 1e3 * A162(p.cup);
const hookMax162 = () => MU162 * DPH162 * Math.PI * DH162 * DH162 / 4 / g162;     // 最大挂重（kg）
const RUN162 = {};
const key162 = (api) => api.scene === "cup" ? `c|${api.p.cup}|${api.p.dp}|${api.p.mode}` : `h|${api.p.mh}`;

WQ.lab({
  title: ["实验 16.2 真空吸盘能吸住多重的零件", "Lab 16.2 How heavy a part can a suction cup hold?"],
  goal: ["由拉脱力和真空度测出吸盘的有效直径，选吸盘和真空度搬运钢板；由吸盘挂钩开始滑动时的挂重测出摩擦因数。",
         "Find a suction cup's effective diameter from its pull-off force and vacuum level, choose the cup and vacuum to handle a steel sheet, and find the friction coefficient from the load at which a suction hook starts to slide."],
  scenes: [
    { id: "cup", robot: true, name: ["真空吸盘", "Vacuum cup"], hide: ["mh"],
      problem: { title: ["机器人问题：吸盘能吸住多重的钢板？", "Robot problem: how heavy a steel sheet can the cup hold?"],
                 text: ["机械臂用真空吸盘搬运钢板。吸盘被大气压“压”在工件上，能吸住多重，取决于真空度和吸盘的有效面积——唇边受压变形，有效直径比名义直径小，要测出来。方式 0 做拉脱试验，读拉脱的力；方式 1 吸起 8.0 kg 的钢板，以 5.0 m/s² 向上加速。",
                        "The arm moves steel sheets with a vacuum cup. Atmospheric pressure presses the cup onto the part; how much it holds depends on the vacuum level and the cup's effective area — the lip deforms, so the effective diameter is smaller than nominal and must be measured. Mode 0 is a pull-off test that reads the pull-off force; mode 1 lifts an 8.0 kg sheet, accelerating up at 5.0 m/s²."] } },
    { id: "hook", name: ["吸盘挂钩", "Suction hook"], hide: ["cup", "dp", "mode"],
      problem: { title: ["生活中的例子：吸盘挂钩能挂多重？", "Everyday example: how much will a suction hook hold?"],
                 text: ["吸盘挂钩压在竖直的瓷砖墙上，吸盘内比大气压低 60 kPa，有效直径 45 mm。挂钩不是被“吸”着往上的，它靠吸盘与墙之间的摩擦力承重。逐渐增加挂的质量，看什么时候滑下来。",
                        "A suction hook is pressed onto a vertical tiled wall: 60 kPa below atmospheric inside, effective diameter 45 mm. Nothing pulls it upward; friction between cup and wall holds the load. Increase the hanging mass and see when it slides."] } },
  ],
  params: [
    { id: "cup", name: ["吸盘名义直径：0 Ø40，1 Ø60，2 Ø80", "Cup: 0 Ø40, 1 Ø60, 2 Ø80"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "dp", name: ["真空度 Δp（比大气压低）", "Vacuum Δp (below atmospheric)"], min: 10, max: 90, step: 1, value: 50, unit: "kPa", digits: 0 },
    { id: "mode", name: ["方式：0 拉脱试验，1 搬运钢板", "Mode: 0 pull-off test, 1 lift the sheet"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "mh", name: ["挂的质量", "Hanging mass"], min: 0.5, max: 10, step: 0.05, value: 2, unit: "kg", digits: 2 },
    { id: "ans", name: ["你的结果", "Your result"], min: 0, max: 100, step: 0.01, value: 0, unit: "", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "deff", robot: true, text: ["真空吸盘：测出 Ø60 吸盘的有效直径（mm），调到“你的结果”，提交（相差 1 mm 以内）。", "Vacuum cup: measure the effective diameter of the Ø60 cup (mm), set it as “Your result” and submit (within 1 mm)."],
      demo: { scene: "cup", set: { cup: 1, dp: 50, mode: 0, ans: 55 }, press: ["start", "submit"], wait: 2 } },
    { id: "lift", robot: true, text: ["真空吸盘：真空度不能超过 70 kPa。选吸盘，按安全系数 2 把真空度调到刚好够用（多出不超过 3 kPa），搬运钢板（方式 1），运行后提交。", "Vacuum cup: the vacuum may not exceed 70 kPa. Choose the cup and set the vacuum just high enough for a safety factor of 2 (no more than 3 kPa over), lift the sheet (mode 1), run and submit."],
      demo: { scene: "cup", set: { cup: 2, dp: 56, mode: 1 }, press: ["start", "submit"], wait: 2 } },
    { id: "mu", text: ["吸盘挂钩：找出挂钩开始滑动的挂重，求吸盘与瓷砖之间的静摩擦因数，调到“你的结果”，提交（相差 0.03 以内）。", "Suction hook: find the load at which the hook starts to slide, work out the static friction coefficient, set it as “Your result” and submit (within 0.03)."],
      demo: { scene: "hook", set: { mh: 5, ans: 0.55 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["吸盘“吸”住工件的力是谁施加的？在高原上（大气压只有 60 kPa）用同样的真空发生器，吸盘还能吸住多重？为什么吸盘挂钩要贴在光滑的瓷砖上，而不能贴在墙纸上？",
          "Who actually exerts the holding force? On a high plateau (60 kPa air pressure), how much could the same cup hold? Why must a suction hook go on smooth tiles, not wallpaper?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; },
  start(api, s) { s.ran = true; s.k = Object.assign({}, api.p); },
  update(dt, api, s) { if (api.t >= 1.5) { RUN162[key162(api)] = true; api.stop(); } },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = s.ran && s.k ? Object.assign({}, s.k, { ans: api.p.ans }) : api.p, have = s.ran || RUN162[key162(api)]; let ok = false;
    if (api.scene === "cup" && have) {
      if (p.cup === 1 && Math.abs(p.ans - DEFF162[1] * 1000) <= 1.0) { api.done("deff"); ok = true; }
      if (p.mode === 1 && p.dp <= 70 && pull162(p) >= SF162 * MS162 * (g162 + AS162) && (p.dp - 3) * 1e3 * A162(p.cup) < SF162 * MS162 * (g162 + AS162)) { api.done("lift"); ok = true; }
    }
    if (api.scene === "hook" && have && Math.abs(p.ans - MU162) <= 0.03) { api.done("mu"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"], have = (s.ran && !api.running) || RUN162[key162(api)];
    if (api.scene === "cup") {
      if (p.mode === 0) return [[["拉脱力", "Pull-off force"], have ? f(pull162(p) + (h162(p.cup * 100 + p.dp) - 0.5) * 2, 1) + " N" : "—"], sub];
      const hold = pull162(p) >= MS162 * (g162 + AS162);
      return [[["钢板", "Sheet"], have ? (hold ? api.T("吸住了", "held") : api.T("掉了", "dropped")) : "—"], sub];
    }
    return [[["挂钩", "Hook"], have ? (p.mh <= hookMax162() ? api.T("挂住了", "holds") : api.T("滑下来了", "slides down")) : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue"), p = api.p;
    const have = (s.ran && !api.running) || RUN162[key162(api)], u = s.ran ? Math.min(1, api.t / 1.5) : (have ? 1 : 0);
    if (api.scene === "cup") {
      const cx = w * 0.45, top = h * 0.2, wcup = DNOM162[p.cup] * 1.6;
      const lift = p.mode === 1 ? u * 80 : u * 20, hold = p.mode === 1 ? pull162(p) >= MS162 * (g162 + AS162) : false;
      api.line(cx, top - 40 - lift, cx, top - lift, ink, 6);
      api.line(cx - wcup / 2, top + 30 - lift, cx, top - lift, blue, 4); api.line(cx + wcup / 2, top + 30 - lift, cx, top - lift, blue, 4);
      const drop = p.mode === 1 && have && !hold ? 60 : 0;
      api.rect(cx - 120, top + 30 - lift + drop + (p.mode === 0 ? lift : 0), 240, 14, mut, ink, 2);
      api.label(api.T(`Ø${DNOM162[p.cup]} 吸盘，真空度 ${p.dp} kPa`, `Ø${DNOM162[p.cup]} cup, vacuum ${p.dp} kPa`), cx, h * 0.85, mut, 12, "center");
      if (p.mode === 0 && have) api.label(api.T("拉脱！", "pulled off!"), cx + 140, top + 20, red, 13);
      return;
    }
    const wx = w * 0.3, cy = h * 0.4, slide = have && p.mh > hookMax162() ? u * 80 : 0;
    api.rect(wx - 12, h * 0.05, 12, h * 0.9, mut, ink, 0);
    api.line(wx, cy - 36 + slide, wx + 20, cy + slide, blue, 4); api.line(wx, cy + 36 + slide, wx + 20, cy + slide, blue, 4);
    api.line(wx + 20, cy + slide, wx + 50, cy + 30 + slide, ink, 3);
    api.line(wx + 50, cy + 30 + slide, wx + 50, cy + 90 + slide, ink, 1.5);
    api.rect(wx + 30, cy + 90 + slide, 40, 20 + p.mh * 4, red, ink, 4);
    api.label(api.T("瓷砖墙（侧视）", "tiled wall (side view)"), wx - 6, h * 0.97, mut, 12, "center");
  },
});
