// 实验 50.5 工序卡上的数：切削用量、转速、机动时间、粗糙度与功率（配 50.5 节）。
// 单位切削力取 45 钢的 Kienzle 常数 kc1.1 = 2220 MPa、mc = 0.14（textbook/mfgtech/std/kienzle.yaml，程序 ex50_5 核对）；
// 数控车床 CNC-L01 主电机 11 kW、传动效率 0.8 为数字工厂的教学示意值（factory/digital/hub/process.py，程序 ex50_5 核对）。
const K50 = { KC11: 2220, MC: 0.14 };
const M50 = { P_MOTOR: 11.0, ETA: 0.8 };
const KR50 = 1.5;          // 实际粗糙度与理论值之比（教学取值；积屑瘤、振动、刀尖磨损使实际值更大，见第 41 章）
// ta：本工序其余工步的机动时间加上辅助、布置工作地、休息与准终分摊，= 单件定额 − 本场景这一刀（程序 ex50_5 核对）
const SC50 = {
  rough: { d: 50, d_end: 41.5, L: 130.5, r: 0.8, ta: 16.9, minutes: 18, ra_need: 12.5, card: { vc: 120, f: 0.3, ap: 2.125 },
           name: ["SH-301 粗车齿轮位 Ø50 → Ø41.5", "SH-301 rough turning Ø50 → Ø41.5"] },
  finish: { d: 41.5, d_end: 40.3, L: 121.5, r: 0.4, ta: 14.3, minutes: 15, ra_need: 3.2, card: { vc: 150, f: 0.15, ap: 0.6 },
            name: ["SH-301 精车齿轮位 Ø41.5 → Ø40.3", "SH-301 finish turning Ø41.5 → Ø40.3"] },
  joint: { d: 26.2, d_end: 25.3, L: 150, r: 0.4, ta: 7.0, minutes: 9, ra_need: 1.6, card: { vc: 150, f: 0.15, ap: 0.45 },
           name: ["关节输出轴精车 Ø26.2 → Ø25.3（铝合金壳体内的钢轴）", "joint shaft finish turning Ø26.2 → Ø25.3"] },
};

function eval505(api) {
  const sc = SC50[api.scene] || SC50.rough, p = api.p;
  const stock = (sc.d - sc.d_end) / 2;                         // 单边总余量
  const passes = Math.max(1, Math.ceil(stock / p.ap - 1e-9));
  const ap = stock / passes;                                    // 均分到各刀
  let tb = 0, d = sc.d, nmax = 0;
  for (let i = 0; i < passes; i++) {
    const n = 1000 * p.vc / (Math.PI * d);
    nmax = Math.max(nmax, n);
    tb += sc.L / (n * p.f);
    d -= 2 * ap;
  }
  const n0 = 1000 * p.vc / (Math.PI * sc.d);
  const kc = K50.KC11 * Math.pow(p.f, -K50.MC);                // 主偏角近 90°：h ≈ f，b ≈ a_p
  const Fc = kc * ap * p.f;                                     // N
  const P = Fc * p.vc / 60000;                                   // kW（切削功率）
  const Pm = P / M50.ETA;                                        // 电机要出的功率
  const Ra = 0.0321 * p.f * p.f / sc.r * 1000;                   // 理论 Ra（µm）：Ra ≈ 0.0321 f²/r_ε
  return { sc, stock, passes, ap, tb, n0, nmax, kc, Fc, P, Pm, Ra, okP: Pm <= M50.P_MOTOR, okRa: KR50 * Ra <= sc.ra_need,
    unit: tb + sc.ta };
}

function check505(api, s) {
  const e = eval505(api), c = e.sc.card, p = api.p;
  s.e = e;
  const near = (a, b, t) => Math.abs(a - b) <= t;
  if (api.scene === "rough" && near(p.vc, c.vc, 1) && near(p.f, c.f, 0.005) && e.passes === 2) api.done("card");
  if (!e.okP) api.done("power");
  if (api.scene === "finish" && e.okRa && p.f >= 0.16 - 1e-9) api.done("feed");
  if (api.scene === "joint" && e.okRa && e.okP && e.unit <= e.sc.minutes - 1.5) api.done("robot");
}

WQ.lab({
  title: ["实验 50.5 工序卡上的数：切削用量与工时", "Lab 50.5 The numbers on an operation sheet: cutting data and time"],
  goal: ["工序卡上的主轴转速、进给次数、机动时间不是凭经验填的：它们都由切削速度、进给量、背吃刀量和走刀长度算出来。调这几个数，看机动时间、表面粗糙度和切削功率怎样一起变，明白工序卡上每一栏的来历和约束。",
         "The spindle speed, number of passes and machining time on an operation sheet are not guesses: they follow from the cutting speed, feed, depth of cut and length of cut. Change these and see how machining time, surface roughness and cutting power move together."],
  scenes: [
    { id: "rough", name: ["SH-301 粗车", "SH-301 rough turning"],
      params: { vc: { value: 120 }, f: { value: 0.3 }, ap: { value: 2.5 } },
      problem: { title: ["工厂问题：粗车工序卡上的 764 r/min 和两刀是怎么来的？", "Factory problem: where do 764 r/min and two passes on the rough-turning sheet come from?"],
                 text: ["工序 20 第 3 工步的前两刀把齿轮位一带从 Ø50 车到 Ø41.5，走刀长度 130.5 mm。工序卡写 v_c = 120 m/min、f = 0.3 mm/r。核对卡片上的转速和这两刀的机动时间，再看能不能更快。",
                        "The first two passes of step 3 in operation 20 turn the gear-seat region from Ø50 to Ø41.5 over 130.5 mm. The sheet says v_c = 120 m/min, f = 0.3 mm/r. Check the speed and the time of these two passes, then see whether it can go faster."] } },
    { id: "finish", name: ["SH-301 精车", "SH-301 finish turning"],
      params: { vc: { value: 150 }, f: { value: 0.15 }, ap: { value: 0.6 } },
      problem: { title: ["工厂问题：精车的进给量能不能加大？", "Factory problem: can the finishing feed be raised?"],
                 text: ["精车后齿轮位要 Ra 3.2（再磨到 Ra 0.8）。进给量越大越快，但残留面积越高。刀尖圆弧半径 0.4 mm、实际粗糙度按理论值的 1.5 倍估计时，进给量最大能取多少？",
                        "After finish turning the gear seat must be Ra 3.2 (then ground to Ra 0.8). A larger feed is faster but leaves higher cusps. With a 0.4 mm nose radius, how large can the feed be?"] } },
    { id: "joint", robot: true, name: ["关节输出轴精车", "joint shaft finishing"],
      params: { vc: { value: 150 }, f: { value: 0.15 }, ap: { value: 0.45 } },
      problem: { title: ["机器人问题：关节输出轴要 Ra 1.6，单件定额 9 min", "Robot problem: the joint shaft needs Ra 1.6 within 9 min per piece"],
                 text: ["协作机器人关节的输出轴有几段轴颈，精车走刀长度共 150 mm，精车后直接装配，要 Ra 1.6。在功率和粗糙度都满足的前提下，把单件时间压到 7.5 min 以内。",
                        "The cobot joint's output shaft has several journals, 150 mm of finishing cut in all, is assembled straight after finish turning and needs Ra 1.6. Keep power and roughness within limits and get the time per piece below 7.5 min."] } },
  ],
  params: [
    { id: "vc", name: ["切削速度 v_c", "Cutting speed v_c"], min: 40, max: 300, step: 5, value: 120, unit: "m/min", digits: 0 },
    { id: "f", name: ["进给量 f", "Feed f"], min: 0.05, max: 0.6, step: 0.01, value: 0.3, unit: "mm/r", digits: 2 },
    { id: "ap", name: ["每刀最大背吃刀量 a_p", "Max depth of cut per pass a_p"], min: 0.2, max: 5, step: 0.05, value: 2.5, unit: "mm", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--accent)", name: ["机动时间 t_b", "machining time t_b"] }, { color: "var(--muted)", name: ["辅助等其余时间", "handling and other time"] },
           { color: "var(--red)", name: ["超出限制", "over a limit"] }],
  tasks: [
    { id: "card", text: ["粗车：设成工序卡上的 v_c = 120 m/min、f = 0.3 mm/r，每刀不超过 2.5 mm，核对转速、刀数和机动时间与图 50.5.1 一致。",
                         "Rough turning: set the sheet's v_c = 120 m/min, f = 0.3 mm/r and at most 2.5 mm per pass; check the speed, passes and time against Figure 50.5.1."],
      demo: { scene: "rough", set: { vc: 120, f: 0.3, ap: 2.5 } } },
    { id: "power", text: ["粗车：一刀车到底（a_p 调到 4.25 mm）并加大进给，看电机功率什么时候不够。", "Rough turning: take it in one pass (a_p 4.25 mm) and raise the feed; see when the motor runs out of power."],
      demo: { scene: "rough", set: { vc: 120, f: 0.5, ap: 4.3 } } },
    { id: "feed", text: ["精车：在保证 Ra 3.2（理论值的 1.5 倍不超过 3.2 µm）的前提下，把进给量提到 0.16 mm/r 以上。", "Finish turning: raise the feed to at least 0.16 mm/r while keeping Ra 3.2 (1.5 times the theoretical value at most 3.2 µm)."],
      demo: { scene: "finish", set: { vc: 150, f: 0.16, ap: 0.6 } } },
    { id: "robot", robot: true, text: ["关节输出轴：Ra 1.6、功率够，单件时间压到 7.5 min 以内。", "Joint shaft: Ra 1.6, enough power, time per piece below 7.5 min."],
      demo: { scene: "joint", set: { vc: 240, f: 0.11, ap: 0.45 } } },
  ],
  think: ["粗车的机动时间只占单件定额的一小部分。要把单件时间降下来，加大切削用量和缩短辅助时间，哪个更有效？为什么工序卡上要把“机动”和“辅助”分开写？",
          "Machining time is a small part of the rough-turning standard. To cut the time per piece, which helps more: heavier cutting data or less handling time? Why does the sheet list machining and handling time separately?"],

  reset(api, s) { check505(api, s); },
  update(dt, api, s) { check505(api, s); api.stop(); },
  readouts(api, s) {
    const e = s.e || eval505(api), f = api.fmt;
    return [
      [["主轴转速 n（第一刀）", "Spindle speed n (first pass)"], `${f(e.n0, 0)} r/min`],
      [["进给次数 / 每刀 a_p", "Passes / a_p per pass"], `${e.passes} / ${f(e.ap, 3)} mm`],
      [["机动时间 t_b", "Machining time t_b"], `${f(e.tb, 2)} min`],
      [["单件时间（t_b + 辅助等）/ 定额", "Time per piece (t_b + other) / standard"], `${f(e.unit, 1)} / ${e.sc.minutes} min`],
      [["理论粗糙度 Ra（实际按 1.5 倍估计）", "Theoretical Ra (real ≈ 1.5×)"], `${f(e.Ra, 2)} µm · ${api.T("要求", "required")} Ra ${e.sc.ra_need} · ${e.okRa ? api.T("够", "ok") : api.T("不够", "too rough")}`],
      [["主切削力 F_c / 电机功率", "Cutting force F_c / motor power"], `${f(e.Fc, 0)} N / ${f(e.Pm, 1)} kW（${api.T("限", "limit")} ${M50.P_MOTOR} kW）· ${e.okP ? api.T("够", "ok") : api.T("不够", "too much")}`],
    ];
  },
  draw(api, s) {
    const e = s.e || eval505(api), { w, h } = api, css = api.css;
    api.label(api.P(e.sc.name), 12, 18, css("--muted"), 13);
    const X0 = 140, X1 = w - 40, tmax = Math.max(e.sc.minutes, e.unit) * 1.15;
    const X = (t) => X0 + t / tmax * (X1 - X0);
    const y = h * 0.32;
    api.label(api.T("单件时间", "time per piece"), X0 - 10, y + 14, css("--ink"), 13, "right");
    api.rect(X(0), y, X(e.tb) - X(0), 28, css("--accent"), null, 3);
    api.rect(X(e.tb), y, X(e.unit) - X(e.tb), 28, css("--muted"), null, 3);
    api.line(X(e.sc.minutes), y - 8, X(e.sc.minutes), y + 36, css("--ink"), 2);
    api.label(api.T(`定额 ${e.sc.minutes} min`, `standard ${e.sc.minutes} min`), X(e.sc.minutes) + 4, y - 4, css("--ink"), 12);
    const bar = (yy, frac, ok, label) => {
      api.label(label, X0 - 10, yy + 10, css("--ink"), 13, "right");
      api.rect(X0, yy, (X1 - X0) * Math.min(1, frac), 20, ok ? css("--green") : css("--red"), null, 3);
      api.line(X0 + (X1 - X0) * Math.min(1, 1 / 1.25), yy - 4, X0 + (X1 - X0) * Math.min(1, 1 / 1.25), yy + 24, css("--ink"), 1.5);
    };
    bar(h * 0.58, e.Pm / M50.P_MOTOR / 1.25, e.okP, api.T("功率 / 限值", "power / limit"));
    bar(h * 0.76, KR50 * e.Ra / e.sc.ra_need / 1.25, e.okRa, api.T("粗糙度 / 要求", "roughness / required"));
    api.label(api.T("竖线 = 限值", "vertical line = limit"), X1, h * 0.93, css("--muted"), 12, "right");
  },
});
