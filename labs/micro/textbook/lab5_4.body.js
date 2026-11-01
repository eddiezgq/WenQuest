// 实验 5.4 电源门控（配 5.4 节）。视觉预处理模块约三万个门（翻转率 0.1、每门 5 fF、100 MHz），由宽 W 的 PMOS 休眠管供电。
// 压降 = 峰值电流（平均的 3 倍）× 休眠管导通电阻（M5_4.sleepRon）；模块漏电 = 门数 × 参考反相器漏电（M5_4.leakInv）；
// 休眠管关断漏电按仿真的 PMOS 关断电流折算到每微米；唤醒能量取模块全部门电容 × VDD²（与书中程序 5.4.1 相同）。
const P54 = M5_4.P, Q54 = P54.problems.p54, PS54 = P54.power_sim, VDD54 = P54.VDD;
const WPREF54 = P54.kn / P54.kp * P54.Wmin;
const IPK54 = Q54.peak * Q54.alpha * Q54.n_gates * Q54.c_gate_fF * 1e-15 * VDD54 * Q54.f_MHz * 1e6;
const EW54 = Q54.n_gates * Q54.c_gate_fF * 1e-15 * VDD54 * VDD54;
function pleak54(temp) {   // PMOS 关断电流（A/μm），温度之间按对数插值
  const ts = Object.keys(PS54.leak_in1).map(Number).sort((a, b) => a - b), ys = ts.map((t) => PS54.leak_in1[String(t)] / WPREF54);
  if (temp <= ts[0]) return ys[0]; if (temp >= ts[ts.length - 1]) return ys[ys.length - 1];
  for (let i = 0; i < ts.length - 1; i++) if (temp <= ts[i + 1]) { const t = (temp - ts[i]) / (ts[i + 1] - ts[i]); return Math.exp(Math.log(ys[i]) + t * (Math.log(ys[i + 1]) - Math.log(ys[i]))); }
}
function gate54(W, temp) {
  const drop = IPK54 * M5_4.sleepRon(W), blk = Q54.n_gates * M5_4.leakInv(temp), hdr = pleak54(temp) * W;
  return { drop, blk, hdr, be: EW54 / ((blk - hdr) * VDD54) };
}
const wneed54 = () => M5_4.sleepRon(1) / (Q54.drop_pct / 100 * VDD54 / IPK54);

WQ.lab({
  title: ["实验 5.4 电源门控", "Lab 5.4 Power gating"],
  goal: ["给巡检机器人的视觉预处理模块断电：选休眠管的宽度，使工作时的压降不超过 5 %；算唤醒能量和盈亏平衡时间，判断空闲多久断电才划算。",
         "Power-gate the robot's vision block: choose the sleep transistor width so the drop stays within 5 %; compute the wake-up energy and the break-even time, and judge how long an idle period must be for gating to pay off."],
  scenes: [
    { id: "vision", robot: true, name: ["视觉预处理模块", "Vision block"], hide: [],
      problem: { title: ["机器人问题：拍照间隙断电", "Robot problem: power off between photos"],
                 text: ["模块只在拍照后工作几十毫秒。85 °C 时它的漏电约 90 μA。休眠管要多宽？空闲多久断电才划算？",
                        "The block works only for tens of milliseconds after each photo; at 85 °C it leaks about 90 μA. How wide must the sleep transistor be, and how long must it idle for gating to pay?"] } },
  ],
  params: [
    { id: "W", name: ["休眠管宽度", "Sleep transistor width"], min: 50, max: 3000, step: 10, value: 100, unit: "μm", digits: 0 },
    { id: "idle", name: ["空闲时间", "Idle time"], min: 1, max: 200, step: 1, value: 10, unit: "μs", digits: 0 },
    { id: "T", name: ["芯片温度", "Chip temperature"], min: 25, max: 125, step: 1, value: 85, unit: "°C", digits: 0 },
  ],
  tasks: [
    { id: "width", robot: true, text: ["找到使压降不超过 5 % 的最小宽度（以 10 μm 为步长）。", "Find the smallest width (10 μm steps) that keeps the drop within 5 %."],
      demo: { scene: "vision", set: { W: 320 }, press: [], wait: 1 } },
    { id: "be85", text: ["宽度取上一步的值，85 °C：找到断电开始省电的最短空闲时间（以 1 μs 为步长）。", "With that width at 85 °C, find the shortest idle time (1 μs steps) at which gating starts to save energy."],
      demo: { scene: "vision", set: { W: 320, T: 85, idle: 4 }, press: [], wait: 1 } },
    { id: "be27", text: ["同样的宽度，27 °C：再找一次。", "Same width at 27 °C: find it again."],
      demo: { scene: "vision", set: { W: 320, T: 27, idle: 65 }, press: [], wait: 1 } },
  ],
  think: ["为什么温度越高，盈亏平衡时间越短？休眠管加宽一倍，压降和关断漏电各怎样变？", "Why does the break-even time shrink as the chip gets hotter? Doubling the width changes the drop and the off leakage how?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["断电省下的能量", "energy saved by gating"], color: "#2e7d32" }, { name: ["唤醒能量", "wake-up energy"], color: "#c0392b" }],
  reset(api, s) { check54(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, g = gate54(p.W, p.T), save = (g.blk - g.hdr) * VDD54 * p.idle * 1e-6 - EW54;
    return [[["峰值时的压降", "Drop at peak current"], f(g.drop * 1e3, 0) + " mV（" + f(g.drop / VDD54 * 100, 1) + " %）"],
            [["模块漏电 / 断电后", "Block leakage / gated"], f(g.blk * 1e6, 1) + " / " + f(g.hdr * 1e6, 2) + " μA"],
            [["唤醒能量", "Wake-up energy"], f(EW54 * 1e9, 3) + " nJ"],
            [["盈亏平衡时间", "Break-even time"], f(g.be * 1e6, 1) + " μs"],
            [["这次空闲断电省下", "Saved over this idle period"], f(save * 1e9, 3) + " nJ " + (save > 0 ? api.T("（划算）", "(worth it)") : api.T("（不划算）", "(not worth it)"))]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, mu = css("--muted"), green = "#2e7d32", red = "#c0392b", amber = "#e67e22";
    const p = api.p, g = gate54(p.W, p.T), px = w * 0.1, py = h * 0.1, pw = w * 0.84, ph = h * 0.7, tmax = Math.max(2 * g.be * 1e6, p.idle * 1.2, 10);
    const pts = []; for (let i = 0; i <= 100; i++) { const t = tmax * i / 100; pts.push([t, ((g.blk - g.hdr) * VDD54 * t * 1e-6) * 1e9]); }
    const ymax = Math.max(EW54 * 1e9 * 2.2, pts[100][1]);
    const ax = api.plot(px, py, pw, ph, [{ pts, color: green }, { pts: [[0, EW54 * 1e9], [tmax, EW54 * 1e9]], color: red }],
      { xmin: 0, xmax: tmax, ymin: 0, ymax, xlabel: api.T("空闲时间 / μs", "idle / μs"), ylabel: "nJ" });
    api.line(ax.X(p.idle), py, ax.X(p.idle), py + ph, amber, 2, [5, 4]);
    api.line(ax.X(g.be * 1e6), py + ph - 6, ax.X(g.be * 1e6), py + ph + 6, mu, 2);
    api.label(api.T("盈亏平衡", "break-even") + " " + api.fmt(g.be * 1e6, 1) + " μs", ax.X(g.be * 1e6) + 4, py + ph - 10, mu, 11, "left");
    api.label("0", px, py + ph + 13, mu, 10, "center"); api.label(api.fmt(tmax, 0), px + pw, py + ph + 13, mu, 10, "right");
    const dok = g.drop / VDD54 <= Q54.drop_pct / 100;
    api.label(api.T("压降 ", "drop ") + api.fmt(g.drop / VDD54 * 100, 1) + " %", px + pw - 4, py + 14, dok ? green : red, 12, "right");
  },
});

function check54(api) {
  const p = api.p, wn = wneed54();
  const okw = p.W >= wn && p.W - 10 < wn;
  if (okw) api.done("width");
  const sv = (idle, T) => (gate54(p.W, T).blk - gate54(p.W, T).hdr) * VDD54 * idle * 1e-6 - EW54;
  if (okw && p.T === 85 && sv(p.idle, 85) > 0 && sv(p.idle - 1, 85) <= 0) api.done("be85");
  if (okw && p.T === 27 && sv(p.idle, 27) > 0 && sv(p.idle - 1, 27) <= 0) api.done("be27");
}
