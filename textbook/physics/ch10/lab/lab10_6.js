// 实验 10.6 下降负载时回收的能量（配 10.6 节）。
// 堆垛机场景：载货台 500 kg + 货物 m，以速度 v 升高 12 m，停 2 s，再降回原处（加速、减速各 1.0 s）。
// 母线到载货台之间的效率 η = 0.95 × 0.92 × 0.97，双向相同。上升时从电网取用 P/η，下降时载货台拖着电机发电，回馈 ηP。
// 方式 0：回馈的能量全部烧在制动电阻上；方式 1：送回电网。读数是三块“电能表”：电网取用、送回电网、电阻烧掉。
// 动画按 3 倍速播放。任务 1：测回收比例；任务 2：回馈单元额定 10 kW，求下降速度的上限。
// 电梯场景（生活中的例子）：轿厢 1000 kg，对重 1450 kg（轿厢 + 45% 额定载重），1.0 m/s 匀速；找出上行时电机功率为零的载重。
const g106 = 9.81, MC106 = 500, H106 = 12, TA106 = 1.0, ETA106 = 0.95 * 0.92 * 0.97, PAUSE106 = 2, SPEED106 = 3;
const CAR106 = 1000, CW106 = 1450;
const RUN106 = {};                                                         // 跑完的一个来回：各设置下的电能表读数（改滑块后仍记得）
const key106 = (p) => `${p.m}|${p.v}|${p.mode}`;
function plan106(v) {                                                      // 一次单程的时间与 t 时刻的速度、加速度（向上为正）
  const T = H106 / v + TA106;
  return { T, at: (t) => t < TA106 ? [v * t / TA106, v / TA106] : t < T - TA106 ? [v, 0] : t < T ? [v * (T - t) / TA106, -v / TA106] : [0, 0] };
}
function cycle106(m, v, t) {                                               // 循环中 t 时刻：高度、速度（上正）、母线功率（取用为正）
  const M = MC106 + m, pl = plan106(v), T = pl.T;
  let dir = 0, tt = t;
  if (t < T) dir = 1; else if (t < T + PAUSE106) dir = 0; else if (t < 2 * T + PAUSE106) { dir = -1; tt = t - T - PAUSE106; } else return { y: 0, v: 0, P: 0, end: true };
  if (dir === 0) return { y: H106, v: 0, P: 0, end: false };
  const [sp, ac] = pl.at(tt), vv = dir * sp, aa = dir * ac, Pm = M * (g106 + aa) * vv;
  const dist = tt < TA106 ? 0.5 * (v / TA106) * tt * tt : tt < T - TA106 ? v * (tt - TA106 / 2) : H106 - 0.5 * (v / TA106) * (T - tt) ** 2;   // 本程走过的距离
  const y = dir > 0 ? dist : H106 - dist;
  return { y, v: vv, P: Pm >= 0 ? Pm / ETA106 : Pm * ETA106, end: false };
}
const backPeak106 = (m, v) => ETA106 * (MC106 + m) * (g106 + v / TA106) * v;    // 下降末尾减速时回馈功率最大
const lift106 = (load, up) => (CAR106 + load - CW106) * g106 * 1.0 * (up ? 1 : -1);   // 电梯电机的机械功率（正为驱动）

WQ.lab({
  title: ["实验 10.6 下降负载时回收的能量", "Lab 10.6 Recovering energy when a load comes down"],
  goal: ["看堆垛机升降一个来回时母线功率的正负，读电能表求出能量回收的比例；按回馈单元的额定功率限制下降速度；看电梯的对重怎样省电。",
         "Watch the sign of the bus power as a stacker crane lifts and lowers, read the energy meters to find the recovered fraction, limit the lowering speed to the regeneration unit's rating, and see how an elevator's counterweight saves energy."],
  scenes: [
    { id: "crane", robot: true, name: ["堆垛机", "Stacker crane"], hide: ["load", "dir"],
      problem: { title: ["机器人问题：货物降下来时，势能到哪里去了？", "Robot problem: where does the potential energy go when the load comes down?"],
                 text: ["立体仓库的堆垛机把货物升到 12 m 高的货位，再空着或带着货降下来。下降时载货台拖着电机转，电机变成发电机。选“方式 0”，这些电能烧在制动电阻上；选“方式 1”，送回电网。点“开始”看一个来回（3 倍速）。",
                        "A stacker crane lifts a load 12 m to a rack slot and brings the carriage back down. Coming down, the carriage drives the motor, which becomes a generator. In mode 0 that energy is burnt in a braking resistor; in mode 1 it goes back to the grid. Press “Start” to watch one cycle (3× speed)."] } },
    { id: "lift", name: ["电梯的对重", "Elevator counterweight"], hide: ["m", "v", "mode", "ratio"],
      problem: { title: ["生活中的例子：电梯为什么要挂对重", "Everyday example: why elevators carry a counterweight"],
                 text: ["轿厢 1000 kg，额定载重 1000 kg；钢丝绳绕过顶上的曳引轮，另一头挂 1450 kg 的对重。轿厢以 1.0 m/s 匀速运行时，电机要出多大的功率？什么时候电机反而在发电？",
                        "Car 1000 kg, rated load 1000 kg; the ropes run over the traction sheave to a 1450 kg counterweight. At a steady 1.0 m/s, how much power must the motor give? When is it generating instead?"] } },
  ],
  params: [
    { id: "m", name: ["货物质量 m", "Load mass m"], min: 0, max: 1500, step: 50, value: 1000, unit: "kg", digits: 0 },
    { id: "v", name: ["升降速度 v", "Hoisting speed v"], min: 0.3, max: 1.5, step: 0.1, value: 1.0, unit: "m/s", digits: 1 },
    { id: "mode", name: ["方式：0 制动电阻，1 回馈电网", "Mode: 0 braking resistor, 1 regenerate to grid"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "ratio", name: ["你测得的回收比例", "Your recovered fraction"], min: 0, max: 1, step: 0.001, value: 0, unit: "", digits: 3 },
    { id: "load", name: ["电梯载重", "Elevator load"], min: 0, max: 1000, step: 50, value: 0, unit: "kg", digits: 0 },
    { id: "dir", name: ["方向：0 上行，1 下行", "Direction: 0 up, 1 down"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--red)", name: ["从电网取用", "drawn from the grid"] }, { color: "var(--blue)", name: ["回馈 / 发电", "fed back / generating"] }],
  tasks: [
    { id: "ratio", robot: true, text: ["堆垛机：货物 1000 kg、1.0 m/s、方式 1，运行一个来回，求“送回电网”与“电网取用”之比，提交（相差 0.01 以内）。它与效率 η 有什么关系？", "Crane: 1000 kg, 1.0 m/s, mode 1; run one cycle, find “fed back” ÷ “drawn from the grid” and submit (within 0.01). How is it related to the efficiency η?"],
      demo: { scene: "crane", set: { m: 1000, v: 1.0, mode: 1, ratio: 0.719 }, press: ["start", "submit"], wait: 2 } },
    { id: "vmax", robot: true, text: ["堆垛机：回馈单元最大只能送回 10 kW。货物 1000 kg、方式 1，找出回馈功率不超过 10 kW 的最大下降速度（按 0.1 m/s 一档），运行后提交。", "Crane: the regeneration unit can return at most 10 kW. With 1000 kg in mode 1, find the highest speed (in 0.1 m/s steps) whose feedback stays at or below 10 kW; run it, then submit."],
      demo: { scene: "crane", set: { m: 1000, v: 0.7, mode: 1 }, press: ["start", "submit"], wait: 2 } },
    { id: "cw", text: ["电梯：找出上行时电机功率为零的载重，运行后提交。空轿厢上行时，电机在驱动还是在发电？", "Elevator: find the load for which going up needs zero motor power; run it, then submit. With an empty car going up, is the motor driving or generating?"],
      demo: { scene: "lift", set: { load: 450, dir: 0 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["回收比例为什么约等于 η²，而与货物质量、速度几乎无关？真实堆垛机还要水平行走，水平行走的制动能量能回收吗？对重为什么取轿厢加额定载重的 45% 左右，而不是加 100%？",
          "Why is the recovered fraction about η², nearly independent of mass and speed? A real crane also travels horizontally; can braking energy from that be recovered? Why is the counterweight the car plus about 45% of the rated load, not 100%?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; s.hist = []; s.Ein = 0; s.Eback = 0; s.Eres = 0; s.pk = 0; s.y = 0; s.done = false; s.last = 0; },
  start(api, s) { s.ran = true; s.m0 = api.p.m; s.v0 = api.p.v; s.mode0 = api.p.mode; s.hist = [[0, 0]]; },
  change(api, s) { s.ran = false; },
  update(dt, api, s) {
    const p = api.p;
    if (api.scene === "lift") { s.y = Math.min(1, api.t / 4); if (api.t > 4) api.stop(); return; }
    const t = api.t * SPEED106, n = 20;
    for (let i = 1; i <= n; i++) {
      const ti = s.last + (t - s.last) * i / n, q = cycle106(p.m, p.v, ti), dtt = (t - s.last) / n;
      if (q.P >= 0) s.Ein += q.P * dtt; else if (p.mode === 1) s.Eback -= q.P * dtt; else s.Eres -= q.P * dtt;
      s.pk = Math.max(s.pk, -q.P);
    }
    s.last = t;
    const q = cycle106(p.m, p.v, t);
    s.y = q.y; s.hist.push([t, q.P / 1000]);
    if (q.end) { s.done = true; RUN106[key106(p)] = { Ein: s.Ein, Eback: s.Eback, Eres: s.Eres, pk: s.pk }; api.stop(); }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "crane") {
      const done1 = RUN106[key106({ m: 1000, v: 1, mode: 1 })] || (s.ran && p.m === 1000 && Math.abs(p.v - 1.0) < 1e-9 && p.mode === 1);
      if (done1 && Math.abs(p.ratio - ETA106 * ETA106) <= 0.01) { api.done("ratio"); ok = true; }        // 跑完一个来回后再调“回收比例”提交
      if ((s.ran || RUN106[key106(p)]) && p.m === 1000 && p.mode === 1 && backPeak106(1000, p.v) <= 10000 && backPeak106(1000, p.v + 0.1) > 10000) { api.done("vmax"); ok = true; }
    }
    if (api.scene === "lift" && s.ran && p.dir === 0 && Math.abs(lift106(p.load, true)) < 1e-6) { api.done("cw"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "lift") {
      const P = lift106(p.load, p.dir === 0);
      return [[["载重", "Load"], f(p.load, 0) + " kg"], [["方向", "Direction"], p.dir === 0 ? api.T("上行", "up") : api.T("下行", "down")],
        [["电机的机械功率", "Motor mechanical power"], s.ran ? f(Math.abs(P) / 1000, 2) + " kW" : "—"],
        [["电机状态", "Motor is"], !s.ran ? "—" : Math.abs(P) < 1e-6 ? api.T("几乎不出力", "doing almost nothing") : P > 0 ? api.T("驱动", "driving") : api.T("发电", "generating")], sub];
    }
    const last = s.hist.length ? s.hist[s.hist.length - 1] : [0, 0], R = !s.ran && RUN106[key106(p)];
    if (R) return [[["上一次运行（这个设置）", "Last run (these settings)"], api.T("一个来回已完成", "one cycle done")],
      [["电网取用", "Drawn from the grid"], f(R.Ein / 1000, 1) + " kJ"], [["送回电网", "Fed back to the grid"], f(R.Eback / 1000, 1) + " kJ"],
      [["制动电阻烧掉", "Burnt in the resistor"], f(R.Eres / 1000, 1) + " kJ"], [["回馈功率的最大值", "Largest feedback power"], f(R.pk / 1000, 2) + " kW"], sub];
    return [[["载货台高度", "Carriage height"], f(s.y, 2) + " m"], [["母线功率", "Bus power"], s.ran ? f(last[1], 2) + " kW" : "—"],
      [["电网取用", "Drawn from the grid"], f(s.Ein / 1000, 1) + " kJ"], [["送回电网", "Fed back to the grid"], f(s.Eback / 1000, 1) + " kJ"],
      [["制动电阻烧掉", "Burnt in the resistor"], f(s.Eres / 1000, 1) + " kJ"], [["回馈功率的最大值", "Largest feedback power"], s.ran ? f(s.pk / 1000, 2) + " kW" : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue");
    if (api.scene === "lift") {
      const cx = w * 0.35, top = h * 0.12, bot = h * 0.85, span = bot - top - 120, up = p.dir === 0;
      const yc = up ? bot - 60 - span * s.y : top + 60 + span * s.y, yw = up ? top + 60 + span * s.y : bot - 60 - span * s.y;
      api.circle(cx + 40, top, 22, null, ink);
      api.line(cx, top, cx, yc - 40, ink, 2); api.line(cx + 80, top, cx + 80, yw - 30, ink, 2);
      api.rect(cx - 40, yc - 40, 80, 80, css("--amber"), ink, 4); api.label(api.T("轿厢", "car"), cx, yc + 4, ink, 13, "center");
      api.rect(cx + 64, yw - 30, 32, 60, mut, ink, 3); api.label(api.T("对重", "counterweight"), cx + 110, yw + 4, mut, 12);
      const P = lift106(p.load, up);
      if (s.ran) api.label(Math.abs(P) < 1e-6 ? api.T("电机几乎不出力", "motor nearly idle") : P > 0 ? api.T("电机驱动", "motor driving") : api.T("电机发电", "motor generating"),
        w * 0.72, h * 0.3, Math.abs(P) < 1e-6 ? mut : P > 0 ? red : blue, 18, "center");
      return;
    }
    // 左：立柱与载货台
    const mx = w * 0.12, top = h * 0.1, bot = h * 0.88, yy = bot - (bot - top - 50) * s.y / H106;
    api.rect(mx - 6, top, 12, bot - top, mut); api.line(mx - 50, bot, mx + 90, bot, ink, 3);
    api.rect(mx + 8, yy - 40, 60, 40, css("--amber"), ink, 4);
    api.label(api.T(`货物 ${f0(p.m)} kg`, `load ${f0(p.m)} kg`), mx + 38, yy - 48, ink, 12, "center");
    function f0(x) { return api.fmt(x, 0); }
    // 右：母线功率
    const pl = plan106(p.v), Tc = 2 * pl.T + PAUSE106, Pmax = (MC106 + p.m) * (g106 + p.v / TA106) * p.v / ETA106 / 1000;
    const G = api.graph({ x: w * 0.32, y: h * 0.1, w: w * 0.63, h: h * 0.75, xmin: 0, xmax: Tc, ymin: -Math.ceil(Pmax), ymax: Math.ceil(Pmax * 1.1),
      xlabel: api.T("t / s", "t / s"), ylabel: api.T("母线功率 / kW（正：取用；负：回馈）", "bus power / kW (+ drawn, − fed back)") }).axes();
    if (s.hist.length > 1) {
      G.pts(s.hist.filter((q) => q[0] <= pl.T + PAUSE106), red, 2);                     // 上升和停顿
      const dn = s.hist.filter((q) => q[0] >= pl.T + PAUSE106); if (dn.length > 1) G.pts(dn, p.mode === 1 ? blue : mut, 2);   // 下降
    }
  },
});
