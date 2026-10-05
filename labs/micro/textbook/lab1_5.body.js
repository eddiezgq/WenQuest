// 实验 1.5 功耗（配 1.5 节）。场景：巡线小车的控制芯片（一万个门，每门负载 5 fF）。
// 图中蓝线是动态功耗 P = αCV²fN 随电源电压的变化，红线是对称反相器的 FO4 延时，红色虚线是延时上限；
// 竖线是当前电压。两条曲线各用自己的纵轴（左为 mW，右为 ps）。与书中程序 1.5.1 同一模型。
const R15 = M1_5.P.kn / M1_5.P.kp, Q15 = M1_5.P.problems.p15;
const P15 = (p, V) => M1_5.dynPower(Q15.N, p.alpha, Q15.Cgate, V, p.f * 1e6);
const fo415 = (V) => M1_5.fo4Tp(R15, V);
const near15 = (a, b) => Math.abs(a - b) < 1e-6;
function car15(p) { return near15(p.alpha, Q15.alpha) && near15(p.f, Q15.f / 1e6); }

WQ.lab({
  title: ["实验 1.5 功耗", "Lab 1.5 Power"],
  goal: ["改翻转率、频率和电压，读出动态功耗；把电压降到 FO4 延时刚好满足要求，体会功耗与速度的取舍。",
         "Change the activity factor, clock frequency and supply voltage and read the dynamic power; lower the voltage until the FO4 delay just meets the requirement, and see the trade-off between power and speed."],
  scenes: [
    { id: "car", robot: true, name: ["巡线小车的控制芯片", "Line-following robot controller"], hide: [],
      problem: { title: ["机器人问题：电池能撑多久", "Robot problem: how long the battery lasts"],
                 text: ["芯片里约一万个门，翻转率 0.1，时钟 100 MHz，每门负载 5 fF。它耗多少电？把电源从 1.8 V 降下来能省多少？为了时序，FO4 延时不能超过 100 ps，电压最低能降到多少？",
                        "The chip has about ten thousand gates, activity 0.1, a 100 MHz clock and 5 fF per gate. How much power does it use? How much does lowering the supply from 1.8 V save? For timing the FO4 delay must stay within 100 ps: how low can the supply go?"] } },
  ],
  params: [
    { id: "V", name: ["电源电压 VDD", "Supply VDD"], min: 0.9, max: 1.8, step: 0.01, value: 1.8, unit: "V", digits: 2 },
    { id: "f", name: ["时钟频率", "Clock frequency"], min: 10, max: 200, step: 10, value: 50, unit: "MHz", digits: 0 },
    { id: "alpha", name: ["翻转率 α", "Activity α"], min: 0.05, max: 0.5, step: 0.05, value: 0.2, unit: "", digits: 2 },
    { id: "lim", name: ["FO4 延时上限", "FO4 delay limit"], min: 60, max: 150, step: 5, value: 100, unit: "ps", digits: 0 },
  ],
  tasks: [
    { id: "car", robot: true, text: ["按小车芯片的条件设好：α = 0.1，时钟 100 MHz，VDD = 1.8 V，读出动态功耗。", "Set the robot chip's conditions: α = 0.1, 100 MHz, VDD = 1.8 V, and read the dynamic power."],
      demo: { scene: "car", set: { alpha: 0.1, f: 100, V: 1.8 }, press: [], wait: 1 } },
    { id: "low", text: ["同样的 α 和频率，把电压降到 1.2 V：功耗省了多少？FO4 延时还满足 100 ps 吗？", "Same α and frequency, supply lowered to 1.2 V: how much power is saved? Is the FO4 delay still within 100 ps?"],
      demo: { scene: "car", set: { alpha: 0.1, f: 100, V: 1.2 }, press: [], wait: 1 } },
    { id: "vlim", robot: true, text: ["延时上限 100 ps：找到满足上限的最低电压（再降 0.01 V 就不满足），读出这时的功耗。", "Limit 100 ps: find the lowest supply that still meets it (0.01 V lower fails) and read the power there."],
      demo: { scene: "car", set: { alpha: 0.1, f: 100, lim: 100, V: 1.31 }, press: [], wait: 1 } },
  ],
  think: ["功耗与 VDD² 成正比，而延时随电压降低迅速变长。如果芯片只有一小部分时间需要全速，怎样安排电压和频率最省电？",
          "Power scales as VDD² while the delay grows quickly as the supply drops. If the chip needs full speed only part of the time, how should voltage and frequency be scheduled to save the most energy?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["动态功耗（左轴）", "dynamic power (left)"], color: "#1d6fb8" }, { name: ["FO4 延时（右轴）", "FO4 delay (right)"], color: "#c0392b" }],
  reset(api, s) { check15(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, P = P15(p, p.V), P18 = P15(p, 1.8), t = fo415(p.V);
    return [[["每次 0→1 翻转的能量 CV²", "Energy per 0→1 transition CV²"], f(Q15.Cgate * p.V * p.V * 1e15, 2) + " fJ"],
            [["动态功耗", "Dynamic power"], f(P * 1e3, 3) + " mW"],
            [["比 1.8 V 省", "Saved versus 1.8 V"], f((1 - P / P18) * 100, 0) + " %"],
            [["FO4 延时", "FO4 delay"], f(t * 1e12, 1) + " ps"],
            [["是否满足上限", "Meets the limit"], t <= p.lim * 1e-12 ? api.T("满足", "yes") : api.T("不满足", "no")]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mu = css("--muted");
    const blue = "#1d6fb8", red = "#c0392b";
    const px = w * 0.1, py = h * 0.08, pw = w * 0.78, ph = h * 0.78;
    const pw_ = [], dl = [];
    for (let V = 0.9; V <= 1.8001; V += 0.01) { pw_.push([V, P15(p, V) * 1e3]); dl.push([V, fo415(V) * 1e12]); }
    const pmax = P15(p, 1.8) * 1e3 * 1.1, tmax = 300;
    const axP = api.plot(px, py, pw, ph, [{ pts: pw_, color: blue }], { xmin: 0.9, xmax: 1.8, ymin: 0, ymax: pmax, xlabel: "VDD / V", ylabel: "mW" });
    const axT = api.plot(px, py, pw, ph, [{ pts: dl.map(([v, t]) => [v, Math.min(t, tmax)]), color: red }], { xmin: 0.9, xmax: 1.8, ymin: 0, ymax: tmax });
    for (let k = 0; k <= 3; k++) {
      api.label(api.fmt(pmax * k / 3, 2), px - 6, axP.Y(pmax * k / 3), blue, 10, "right");
      api.label(String(k * 100), px + pw + 6, axT.Y(k * 100), red, 10, "left");
    }
    api.label("ps", px + pw + 34, py, red, 11, "left");
    api.line(px, axT.Y(p.lim), px + pw, axT.Y(p.lim), red, 1, [5, 4]);
    api.line(axP.X(p.V), py, axP.X(p.V), py + ph, ink, 1.5);
    api.circle(axP.X(p.V), axP.Y(P15(p, p.V) * 1e3), 5, blue, ink);
    const t = fo415(p.V) * 1e12;
    if (t <= tmax) api.circle(axT.X(p.V), axT.Y(t), 5, red, ink);
  },
});

function check15(api) {
  const p = api.p;
  if (!car15(p)) return;
  if (near15(p.V, 1.8)) api.done("car");
  if (near15(p.V, 1.2)) api.done("low");
  const lim = p.lim * 1e-12;
  if (near15(p.lim, 100) && fo415(p.V) <= lim && fo415(p.V - 0.01) > lim) api.done("vlim");
}
