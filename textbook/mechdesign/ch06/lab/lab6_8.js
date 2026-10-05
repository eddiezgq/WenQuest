// 实验 6.8 同一个支架的三种做法：成本与工期（配 6.8 节）。与程序 6.8.1 同一套几何与成本模型（_ch6.py）：
// L 形支架（底板 BASE × 宽 W × 立板 UP）；铣削：6061 铝块铣出，壁厚 4 mm；钣金：5052 铝板激光切割后折弯一次；3D 打印：PA12 激光烧结，壁厚 3 mm。
// 铣削费率默认取数字工厂立式加工中心 VMC-01（62 美元/小时）；其余费率、单价、切削参数是本书设定的教学值（美元示意）。
const SCN6_8 = {
  robot: { base: 50, W: 56, up: 58, nUp: 4, dUp: 2.7, nBase: 4, dBase: 4.5 },     // XM540 舵机支架（舵机尺寸取零件库 D-ACT-ROBOTIS-X）
  life: { base: 120, W: 30, up: 120, nUp: 2, dUp: 5.5, nBase: 0, dBase: 0 },       // 墙上的置物架托架（示意）
};
function geo6_8(g) {
  const holes = (t) => (g.nUp * Math.PI * g.dUp ** 2 / 4 + g.nBase * Math.PI * g.dBase ** 2 / 4) * t;
  const tm = 4, rm = 4, blank = (g.base + 2) * (g.W + 2) * (g.up + 2);
  const vm = (g.base * tm + (g.up - tm) * tm + (1 - Math.PI / 4) * rm * rm) * g.W - holes(tm);
  const ts = 2, rs = 2, ba = Math.PI / 2 * (rs + 0.33 * ts), Lf = (g.base - ts - rs) + (g.up - ts - rs) + ba;
  const vs = Lf * g.W * ts - holes(ts);
  const cut = 2 * (Lf + g.W) + Math.PI * (g.nUp * g.dUp + g.nBase * g.dBase);
  const ta = 3, ra = 4, va = (g.base * ta + (g.up - ta) * ta + (1 - Math.PI / 4) * ra * ra) * g.W - holes(ta);
  return { blank, vm, areaFin: 2 * (g.base + g.up) * g.W, nh: g.nUp + g.nBase, vs, cut, pierce: 1 + g.nUp + g.nBase, va };
}
function cost6_8(p, scene, q) {
  const G = geo6_8(SCN6_8[scene]);
  const mill = G.blank * 2.7e-6 * p.pAl + (((G.blank - G.vm) / 1000 / 40 + G.areaFin / 2500 + G.nh * 0.3 + 2 * 2.0) / 60 * p.rMill) + ((60 * 2 + 90) / 60 * p.rMill) / q;
  const lz = G.cut / 3000 + G.pierce * 0.02, br = 0.4 + 0.5;
  const sheet = G.vs * 2.7e-6 / 0.7 * 5.0 + lz / 60 * p.rLaser + br / 60 * 50 + (15 / 60 * p.rLaser + 20 / 60 * 50 + 30 / 60 * p.rLaser) / q;
  const bh = G.va / 1000 / 60;
  const prt = G.va * 1.01e-6 * p.pPA + bh * p.rPrint + 6 / 60 * 30 + (60 / 60 * 30) / q;
  const hours = { mill: (60 * 2 + 90 + (((G.blank - G.vm) / 1000 / 40 + G.areaFin / 2500 + G.nh * 0.3 + 4)) * q) / 60,
    sheet: (15 + 20 + 30 + (lz + br) * q) / 60, print: 1 + bh * q + 6 * q / 60 };
  return { mill, sheet, print: prt, hours, mass: { mill: G.vm * 2.7e-3, sheet: G.vs * 2.7e-3, print: G.va * 1.01e-3 } };
}
WQ.lab({
  title: ["实验 6.8 同一个支架的三种做法：成本与工期", "Lab 6.8 One bracket, three processes: cost and lead time"],
  goal: ["改批量和费率，比较铣削、钣金、3D 打印做同一个支架的单件成本和工时，找出各自划算的批量范围。",
         "Change batch size and rates, compare the cost per part and the hours for one bracket milled, made from sheet or printed, and find where each pays off."],
  scenes: [
    { id: "robot", robot: true, name: ["XM540 舵机支架", "XM540 servo bracket"],
      problem: { title: ["工程问题：机械臂样机的舵机支架", "Engineering problem: servo brackets for a robot-arm prototype"],
                 text: ["实验室做一台小机械臂样机，要几个舵机支架；如果样机成功，还要做 200 台。先做哪种、量产改哪种？",
                        "The lab is building a small robot-arm prototype and needs a few servo brackets; if it works, 200 arms will follow. Which process first, and which for the run?"] } },
    { id: "life", name: ["墙上的置物架托架", "Wall-shelf bracket"],
      problem: { title: ["生活中的例子：置物架托架", "Everyday example: a shelf bracket"],
                 text: ["家里装置物架要一对托架；店里卖的托架都是钣金冲压的，几块钱一个。自己 3D 打印、找人铣一个，各要多少钱？",
                        "A shelf needs a pair of brackets; shop brackets are pressed sheet metal and cost little. What would printing one or having one milled cost?"] } },
  ],
  params: [
    { id: "q", name: ["批量", "Batch size"], min: 1, max: 1000, step: 1, value: 1, unit: "", digits: 0 },
    { id: "rMill", name: ["加工中心费率", "Machining-centre rate"], min: 30, max: 150, step: 1, value: 62, unit: "USD/h", digits: 0 },
    { id: "rLaser", name: ["激光切割费率", "Laser-cutting rate"], min: 30, max: 200, step: 5, value: 80, unit: "USD/h", digits: 0 },
    { id: "rPrint", name: ["打印机费率", "Printer rate"], min: 5, max: 100, step: 1, value: 30, unit: "USD/h", digits: 0 },
    { id: "pAl", name: ["铝块单价", "Aluminium block price"], min: 2, max: 15, step: 0.5, value: 6, unit: "USD/kg", digits: 1 },
    { id: "pPA", name: ["PA12 粉末单价", "PA12 powder price"], min: 20, max: 200, step: 5, value: 80, unit: "USD/kg", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "#1f77b4", name: ["铣削", "milling"] }, { color: "#2ca02c", name: ["钣金", "sheet metal"] }, { color: "#ff7f0e", name: ["3D 打印", "3D printing"] }],
  tasks: [
    { id: "one", robot: true, text: ["样机只要 1 个：哪种最便宜？工时各多少？", "Only one for the prototype: which is cheapest? How many hours each?"],
      demo: { scene: "robot", set: { q: 1, rMill: 62, rLaser: 80, rPrint: 30, pAl: 6, pPA: 80 }, press: ["start"], wait: 1 } },
    { id: "run", robot: true, text: ["量产 200 个：哪种最便宜？3D 打印比钣金贵几倍？", "A run of 200: which is cheapest? How many times dearer is printing than sheet metal?"],
      demo: { scene: "robot", set: { q: 200, rMill: 62, rLaser: 80, rPrint: 30, pAl: 6, pPA: 80 }, press: ["start"], wait: 1 } },
    { id: "rate", robot: true, text: ["把打印机费率降到 10 美元/小时（自己的打印机），1 个和 20 个时的结论变不变？", "Lower the printer rate to 10 USD/h (your own printer): do the answers for 1 and 20 parts change?"],
      demo: { scene: "robot", set: { q: 20, rMill: 62, rLaser: 80, rPrint: 10, pAl: 6, pPA: 80 }, press: ["start"], wait: 1 } },
    { id: "life", text: ["置物架托架：批量 2，比较三种做法，再想想商店的托架为什么那么便宜。", "Shelf bracket: batch of 2, compare the three; then think why shop brackets are so cheap."],
      demo: { scene: "life", set: { q: 2, rMill: 62, rLaser: 80, rPrint: 30, pAl: 6, pPA: 80 }, press: ["start"], wait: 1 } },
  ],
  think: ["程序 6.8.1 和这个实验用同一套模型。模型里没有排队、运输、检验和返工的时间，实际交货期会长得多——哪种做法的“不在模型里的时间”最长？",
          "Program 6.8.1 and this lab share one model. It leaves out queueing, shipping, inspection and rework, so real lead times are much longer — which process has the most time outside the model?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    const p = api.p, q = Math.round(p.q);
    s.r = cost6_8(p, api.scene, q);
    s.qsp = 0;
    for (let k = 1; k <= 1000; k++) { const c = cost6_8(p, api.scene, k); if (c.sheet < c.print) { s.qsp = k; break; } }
    s.curves = [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000].map((k) => [k, cost6_8(p, api.scene, k)]);
    if (api.scene === "robot" && q === 1) api.done("one");
    if (api.scene === "robot" && q >= 200) api.done("run");
    if (api.scene === "robot" && p.rPrint <= 10.5) api.done("rate");
    if (api.scene === "life") api.done("life");
    api.stop();
  },
  readouts(api, s) {
    const f = api.fmt, r = s.r;
    if (!r) return [[["状态", "Status"], api.T("按“计算”开始", "press Compute")]];
    const best = [["mill", api.T("铣削", "milling")], ["sheet", api.T("钣金", "sheet metal")], ["print", api.T("3D 打印", "3D printing")]].sort((a, b) => r[a[0]] - r[b[0]])[0][1];
    return [
      [["单件成本：铣削 / 钣金 / 打印", "Per part: milling / sheet / print"], f(r.mill, 2) + " / " + f(r.sheet, 2) + " / " + f(r.print, 2) + " USD"],
      [["一批的工时：铣削 / 钣金 / 打印", "Batch hours: milling / sheet / print"], f(r.hours.mill, 1) + " / " + f(r.hours.sheet, 1) + " / " + f(r.hours.print, 1) + " h"],
      [["零件质量：铣削 / 钣金 / 打印", "Part mass: milling / sheet / print"], f(r.mass.mill, 0) + " / " + f(r.mass.sheet, 0) + " / " + f(r.mass.print, 0) + " g"],
      [["这个批量最便宜的", "Cheapest at this batch"], best],
      [["钣金比打印便宜的最小批量", "Smallest batch where sheet beats print"], s.qsp ? String(s.qsp) : api.T("1000 件以内没有", "none up to 1000")],
    ];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    if (!s.r) { api.label(api.T("按“计算”比较三种做法", "Press Compute to compare the three processes"), w / 2, h / 2, css("--muted"), 14, "center"); return; }
    const x0 = 60, y0 = 24, W = w - 90, Hh = h - 70, lx = (q) => Math.log10(q) / 3, ly = (c) => (Math.log10(c) + 0.5) / 3.5;
    api.rect(x0, y0, W, Hh, null, css("--grid"));
    const X = (q) => x0 + lx(q) * W, Y = (c) => y0 + Hh - Math.max(0, Math.min(1, ly(c))) * Hh;
    [["mill", "#1f77b4"], ["sheet", "#2ca02c"], ["print", "#ff7f0e"]].forEach(([k, col]) => {
      for (let i = 1; i < s.curves.length; i++) {
        const [q0, a] = s.curves[i - 1], [q1, b] = s.curves[i];
        api.line(X(q0), Y(a[k]), X(q1), Y(b[k]), col, 2.5);
      }
    });
    const q = Math.round(api.p.q);
    api.line(X(q), y0, X(q), y0 + Hh, css("--muted"), 1, [5, 4]);
    [1, 10, 100, 1000].forEach((k) => api.label(String(k), X(k), y0 + Hh + 14, css("--muted"), 11, "center"));
    [1, 10, 100, 1000].forEach((c) => api.label(String(c), x0 - 6, Y(c), css("--muted"), 11, "right"));
    api.label(api.T("批量（对数）", "batch (log)"), x0 + W, y0 + Hh + 30, css("--muted"), 12, "right");
    api.label(api.T("单件成本 / 美元（对数）", "cost per part / USD (log)"), x0 + 4, y0 + 10, css("--muted"), 12);
  },
});
