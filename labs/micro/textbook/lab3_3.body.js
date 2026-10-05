// 实验 3.3 同步器的平均故障间隔（配 3.3 节）。MTBF = e^(tr/τm) / (T0·fclk·fdata)，τm、T0 取自 params.json 的 ff_sim；
// n 级同步器的决断时间 tr = 后级逻辑留下的余量 + (n − 1)(T − tcq − tsu)（M3_3.syncTr，与书中程序 3.3.1 同一模型）。
// 编码器每相每秒的边沿数 = 转速 / 60 × 线数 × 2。要求：robots 台机器人连续工作 years 年，平均不到一次故障。
const P33 = M3_3.P, Q33 = P33.problems.p33, FF33 = M3_3.ffTiming(), YEAR33 = 365 * 24 * 3600;
const NEED33 = Q33.robots * Q33.years * YEAR33;
const fd33 = (rpm) => rpm / 60 * Q33.lines * 2;
const m33 = (n, fMHz, rpm, slackPs) => M3_3.mtbf(M3_3.syncTr(n, fMHz * 1e6, slackPs * 1e-12), fMHz * 1e6, fd33(rpm));
const ok33 = (n, f, rpm, sl) => m33(n, f, rpm, sl) >= NEED33;
function time33(api, s) {
  const T = api.T;
  if (!isFinite(s) || s > 1e6 * YEAR33) return T("10 的 ", "10^") + api.fmt(Math.log10(s / YEAR33), 0) + T(" 次方年", " years");
  if (s < 60) return api.fmt(s, 2) + T(" 秒", " s");
  if (s < 3600) return api.fmt(s / 60, 1) + T(" 分钟", " min");
  if (s < 86400) return api.fmt(s / 3600, 1) + T(" 小时", " h");
  if (s < YEAR33) return api.fmt(s / 86400, 1) + T(" 天", " days");
  return api.fmt(s / YEAR33, 1) + T(" 年", " years");
}

WQ.lab({
  title: ["实验 3.3 同步器的平均故障间隔", "Lab 3.3 Synchronizer MTBF"],
  goal: ["编码器信号进入控制芯片的时钟域：选同步级数，使 1000 台机器人连续工作 10 年平均不到一次故障；看决断时间、时钟频率、转速各自的影响。",
         "Encoder signals enter the controller's clock domain: choose the number of synchronizer stages so that 1000 robots run 10 years with less than one failure on average; see how resolution time, clock and speed matter."],
  scenes: [
    { id: "enc", robot: true, name: ["100 MHz 控制芯片", "100 MHz controller"], hide: [],
      problem: { title: ["机器人问题：编码器 A 相进入时钟域", "Robot problem: encoder phase A enters the clock domain"],
                 text: ["电机 6000 r/min、编码器 1024 线、时钟 100 MHz。只打一拍时，后面的逻辑要留下多少余量？打两拍呢？",
                        "Motor at 6000 rpm, 1024-line encoder, 100 MHz clock. With one flip-flop, how much slack must the logic leave? With two?"] } },
    { id: "fast", name: ["1 GHz 时钟域", "1 GHz domain"], hide: [], params: { f: { value: 1000 }, slack: { value: 0 } },
      problem: { title: ["更快的时钟", "A faster clock"],
                 text: ["同一个信号送进 1 GHz 的时钟域，同步器后面不留余量。要几级？",
                        "The same signal enters a 1 GHz domain with no slack after the synchronizer. How many stages?"] } },
  ],
  params: [
    { id: "n", name: ["同步级数", "Synchronizer stages"], min: 1, max: 3, step: 1, value: 1, unit: "", digits: 0 },
    { id: "f", name: ["时钟频率", "Clock frequency"], min: 50, max: 1000, step: 50, value: 100, unit: "MHz", digits: 0 },
    { id: "rpm", name: ["电机转速", "Motor speed"], min: 1000, max: 10000, step: 500, value: 6000, unit: "r/min", digits: 0 },
    { id: "slack", name: ["最后一级之后逻辑留下的余量", "Slack left by the logic after the last stage"], min: 0, max: 2000, step: 50, value: 200, unit: "ps", digits: 0 },
  ],
  tasks: [
    { id: "one", robot: true, text: ["打一拍、100 MHz、6000 r/min：找到达标所需的最小余量（以 50 ps 为步长）。", "One stage, 100 MHz, 6000 rpm: find the smallest slack that meets the target (50 ps steps)."],
      demo: { scene: "enc", set: { n: 1, f: 100, rpm: 6000, slack: 1250 }, press: [], wait: 1 } },
    { id: "two", robot: true, text: ["打两拍、100 MHz、6000 r/min，余量为 0：确认达标。", "Two stages, 100 MHz, 6000 rpm, zero slack: confirm the target is met."],
      demo: { scene: "enc", set: { n: 2, f: 100, rpm: 6000, slack: 0 }, press: [], wait: 1 } },
    { id: "fast", text: ["1 GHz、6000 r/min、余量为 0：找到达标所需的最少级数。", "1 GHz, 6000 rpm, zero slack: find the fewest stages that meet the target."],
      demo: { scene: "fast", set: { f: 1000, rpm: 6000, slack: 0, n: 3 }, press: [], wait: 1 } },
  ],
  think: ["余量每增加 100 ps，MTBF 乘多少？转速加倍呢？为什么说决断时间是唯一真正有效的“旋钮”？",
          "By how much does the MTBF grow for each extra 100 ps of slack? And when the speed doubles? Why is resolution time the only knob that really matters?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["MTBF 随决断时间", "MTBF vs resolution time"], color: "#1d6fb8" }, { name: ["机队要求", "fleet target"], color: "#e67e22" }],
  reset(api, s) { check33(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, tr = M3_3.syncTr(p.n, p.f * 1e6, p.slack * 1e-12), m = m33(p.n, p.f, p.rpm, p.slack), ok = m >= NEED33;
    return [[["每相每秒的边沿", "Edges per second per phase"], f(fd33(p.rpm) / 1e3, 1) + " k"],
            [["每秒落进亚稳窗口", "Window hits per second"], f(FF33.T0 * p.f * 1e6 * fd33(p.rpm), 0)],
            [["决断时间 tr", "Resolution time tr"], f(tr * 1e12, 0) + " ps"],
            [["一路信号的 MTBF", "MTBF of one signal"], time33(api, m)],
            [["机队（" + Q33.robots + " 台，每台一路）的 MTBF", "Fleet MTBF (" + Q33.robots + " robots, one signal each)"], time33(api, m / Q33.robots) + (ok ? api.T("（达标）", " (met)") : api.T("（不达标）", " (not met)"))]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, mu = css("--muted"), blue = "#1d6fb8", amber = "#e67e22", red = "#c0392b", green = "#2e7d32";
    const p = api.p, fd = fd33(p.rpm), px = w * 0.1, py = h * 0.08, pw = w * 0.84, ph = h * 0.76;
    const lg = (tr) => Math.log10(M3_3.mtbf(tr, p.f * 1e6, fd)), pts = [];
    for (let i = 0; i <= 60; i++) { const tr = i * 50e-12; pts.push([tr * 1e12, Math.max(-4, Math.min(40, lg(tr)))]); }
    const ax = api.plot(px, py, pw, ph, [{ pts, color: blue }, { pts: [[0, Math.log10(NEED33)], [3000, Math.log10(NEED33)]], color: amber }],
      { xmin: 0, xmax: 3000, ymin: -4, ymax: 40, xlabel: "tr / ps", ylabel: "lg(MTBF / s)" });
    for (let v = 0; v <= 40; v += 10) api.label(String(v), px - 4, ax.Y(v) + 4, mu, 10, "right");
    for (let t = 0; t <= 3000; t += 1000) api.label(String(t), ax.X(t), py + ph + 13, mu, 10, "center");
    const tr = M3_3.syncTr(p.n, p.f * 1e6, p.slack * 1e-12), y = lg(tr), ok = y >= Math.log10(NEED33);
    if (tr * 1e12 <= 3000) api.circle(ax.X(tr * 1e12), ax.Y(Math.min(40, y)), 6, ok ? green : red);
    else api.label("→ " + api.fmt(tr * 1e12, 0) + " ps", px + pw - 4, ax.Y(38), ok ? green : red, 12, "right");
  },
});

function check33(api) {
  const p = api.p;
  if (p.n === 1 && p.f === 100 && p.rpm === 6000 && ok33(1, 100, 6000, p.slack) && (p.slack === 0 || !ok33(1, 100, 6000, p.slack - 50))) api.done("one");
  if (p.n === 2 && p.f === 100 && p.rpm === 6000 && p.slack === 0 && ok33(2, 100, 6000, 0)) api.done("two");
  if (p.f === 1000 && p.rpm === 6000 && p.slack === 0 && ok33(p.n, 1000, 6000, 0) && (p.n === 1 || !ok33(p.n - 1, 1000, 6000, 0))) api.done("fast");
}
