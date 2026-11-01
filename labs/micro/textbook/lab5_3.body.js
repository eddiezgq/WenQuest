// 实验 5.3 巡检机器人的续航（配 5.3 节）。控制芯片每 100 μs 要完成 N 个时钟周期的运算（重载 2000、轻载 20），关键路径 30 个 FO4。
// 选定电压后以该电压下的最高频率跑完，余下时间关时钟空闲（只有漏电）。每个控制周期的能量 = 运算的动态 + 运算期间的漏电 + 空闲的漏电；
// 速度与漏电随电压、温度的变化取自 params.json 的 power_sim（SKY130 仿真），算法与书中程序 5.3.1 相同（M5_3.energyPerOp）。
const P53 = M5_3.P, Q53 = P53.problems.p53, PER53 = 1 / (Q53.loop_kHz * 1e3);
const F4_53 = M5_3.fo4Tp(P53.kn / P53.kp);
const CYC53 = { heavy: Q53.cycles, light: 20 };
function plan53(v, temp, cyc) {
  const [ed, el, tc] = M5_3.energyPerOp(v, Q53.n_gates, Q53.alpha, Q53.c_gate_fF * 1e-15, Q53.depth_fo4, temp);
  const busy = cyc * tc, idle = Math.max(0, PER53 - busy);
  return { ed: cyc * ed, el: cyc * el, ei: Q53.n_gates * M5_3.leakInv(temp, v) * v * idle, busy, ok: busy <= PER53, f: 1 / tc };
}
const tot53 = (x) => x.ed + x.el + x.ei;
function best53(temp, cyc) {
  let b = null;
  for (let k = 40; k <= 180; k++) { const v = k / 100, x = plan53(v, temp, cyc); if (x.ok && (!b || tot53(x) < b.e)) b = { v, e: tot53(x) }; }
  return b;
}
const near53 = (a, b) => Math.abs(a - b) < 1e-6;

WQ.lab({
  title: ["实验 5.3 巡检机器人的续航", "Lab 5.3 Battery life of an inspection robot"],
  goal: ["关节控制芯片每 100 μs 要算完一次控制。选电压（频率随之取最高），比较全速跑完再空闲与降压慢跑，找出每个控制周期能量最少的电压；看温度和负载怎样改变结论。",
         "The joint controller must finish a control computation every 100 μs. Pick the supply (the clock follows at its maximum), compare racing to idle with slowing down, and find the voltage with the least energy per control period; see how temperature and load change the answer."],
  scenes: [
    { id: "heavy", robot: true, name: ["巡逻：每周期 2000 个时钟", "Patrol: 2000 clocks per period"], hide: [],
      problem: { title: ["机器人问题：电流环和速度环", "Robot problem: current and speed loops"],
                 text: ["巡逻时每 100 μs 要完成 2000 个时钟周期的运算。1.8 V 全速 3 μs 就算完了。电压降到多少最省电？",
                        "While patrolling, 2000 clock cycles of work are due every 100 μs; at 1.8 V full speed they take 3 μs. Which voltage uses the least energy?"] } },
    { id: "light", name: ["停靠：每周期 20 个时钟", "Docked: 20 clocks per period"], hide: [], params: { V: { value: 1.2 } },
      problem: { title: ["停在充电桩上", "Parked on the charger"],
                 text: ["停靠时只需监视电机，每 100 μs 20 个时钟周期。电压还能降多少？", "When docked only monitoring remains: 20 clocks per 100 μs. How low can the supply go?"] } },
  ],
  params: [
    { id: "V", name: ["电源电压", "Supply voltage"], min: 0.4, max: 1.8, step: 0.01, value: 1.8, unit: "V", digits: 2 },
    { id: "T", name: ["芯片温度", "Chip temperature"], min: 25, max: 125, step: 1, value: 27, unit: "°C", digits: 0 },
  ],
  tasks: [
    { id: "min27", robot: true, text: ["巡逻，27 °C：找到每个控制周期能量最少的电压（以 0.01 V 为步长）。", "Patrol, 27 °C: find the voltage with the least energy per control period (0.01 V steps)."],
      demo: { scene: "heavy", set: { T: 27, V: 0.77 }, press: [], wait: 1 } },
    { id: "hot", text: ["巡逻，125 °C：再找一次。最优电压变了吗？与 1.8 V 相比省了多少？", "Patrol, 125 °C: find it again. Did the optimum move? How much does it save against 1.8 V?"],
      demo: { scene: "heavy", set: { T: 125, V: 0.77 }, press: [], wait: 1 } },
    { id: "light", text: ["停靠，27 °C：找到能量最少的电压。", "Docked, 27 °C: find the voltage with the least energy."],
      demo: { scene: "light", set: { T: 27, V: 0.51 }, press: [], wait: 1 } },
  ],
  think: ["为什么在这块芯片上，降压慢跑比全速跑完再空闲省电？什么样的芯片上结论会反过来？",
          "Why does slowing down beat racing to idle on this chip? On what kind of chip would the answer flip?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["运算的动态能量", "dynamic energy of the work"], color: "#1d6fb8" }, { name: ["运算期间的漏电", "leakage while working"], color: "#c0392b" },
           { name: ["空闲的漏电", "leakage while idle"], color: "#e67e22" }],
  reset(api, s) { check53(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, x = plan53(p.V, p.T, CYC53[api.scene]), e = tot53(x);
    return [[["最高频率", "Maximum clock"], f(x.f / 1e6, 2) + " MHz"],
            [["运算时间 / 截止时间", "Busy time / deadline"], f(x.busy * 1e6, 2) + " / " + f(PER53 * 1e6, 0) + " μs " + (x.ok ? api.T("（赶得上）", "(met)") : api.T("（赶不上）", "(missed)"))],
            [["每个控制周期的能量", "Energy per control period"], f(e * 1e9, 3) + " nJ"],
            [["平均功耗", "Average power"], f(e / PER53 * 1e6, 1) + " μW"],
            [["1 Wh 电量够芯片用", "1 Wh lasts the chip"], f(3600 / (e / PER53) / 86400, 1) + api.T(" 天", " days")]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, mu = css("--muted"), ink = css("--ink"), blue = "#1d6fb8", red = "#c0392b", amber = "#e67e22", green = "#2e7d32";
    const p = api.p, cyc = CYC53[api.scene], px = w * 0.1, py = h * 0.08, pw = w * 0.84, ph = h * 0.72;
    const pts = [], lg = (v) => Math.log10(v);
    for (let k = 40; k <= 180; k++) { const v = k / 100, x = plan53(v, p.T, cyc); if (x.ok) pts.push([v, lg(tot53(x) * 1e9)]); }
    const ys = pts.map((q) => q[1]), ymin = Math.floor(Math.min(...ys)) - 0.2, ymax = Math.ceil(Math.max(...ys)) + 0.2;
    const ax = api.plot(px, py, pw, ph, [{ pts, color: ink }], { xmin: 0.4, xmax: 1.8, ymin, ymax, xlabel: "VDD / V", ylabel: "lg(E / nJ)" });
    for (let v = 0.4; v <= 1.81; v += 0.2) api.label(api.fmt(v, 1), ax.X(v), py + ph + 13, mu, 10, "center");
    for (let y = Math.ceil(ymin); y <= ymax; y++) api.label(String(y), px - 4, ax.Y(y) + 4, mu, 10, "right");
    const x = plan53(p.V, p.T, cyc);
    if (x.ok) {
      api.circle(ax.X(p.V), ax.Y(lg(tot53(x) * 1e9)), 6, blue);
      const b = best53(p.T, cyc); api.circle(ax.X(b.v), ax.Y(lg(b.e * 1e9)), 4, green);
      // stacked bar of the three parts
      const bx = px + pw * 0.62, by = py + 8, bw = pw * 0.34, e = tot53(x);
      [[x.ed, blue], [x.el, red], [x.ei, amber]].reduce((acc, [v, c]) => { const ww = bw * v / e; api.rect(bx + acc, by, ww, 12, c); return acc + ww; }, 0);
    } else api.label(api.T("赶不上截止时间", "deadline missed"), px + pw / 2, py + ph / 2, red, 14, "center");
  },
});

function check53(api) {
  const p = api.p, cyc = CYC53[api.scene], b = best53(p.T, cyc);
  if (!b || !plan53(p.V, p.T, cyc).ok || !near53(p.V, b.v)) return;
  if (api.scene === "heavy" && p.T === 27) api.done("min27");
  if (api.scene === "heavy" && p.T === 125) api.done("hot");
  if (api.scene === "light" && p.T === 27) api.done("light");
}
