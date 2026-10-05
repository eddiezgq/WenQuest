// 实验 1.4 传播延时与反相器链（配 1.4 节）。场景：采样时钟经引脚送给板上的电流采样 ADC，负载约 10 pF。
// 上图画出逐级放大的反相器链（三角形大小按每级扇出 f 放大，超出画面时压缩显示），下图记录学生试过的级数与总延时，
// 换负载时清空。总延时按式 (1.4.3)：t(N) = N·0.69R·C1(γ + F^(1/N))，与书中程序 1.4.1 同一模型。
const W14 = M1_4.P.Wmin, R14 = M1_4.P.kn / M1_4.P.kp, TMAX14 = M1_4.P.problems.p14.tmax;
const tried14 = { CL: null, pts: {} };
const t14 = (N, CLpf) => M1_4.chainDelay(N, CLpf * 1e-12, R14);
function best14(CLpf) { let b = 1; for (let N = 2; N <= 10; N++) if (t14(N, CLpf) < t14(b, CLpf)) b = N; return b; }
function few14(CLpf) { for (let N = 1; N <= 10; N++) if (t14(N, CLpf) < TMAX14) return N; return null; }

WQ.lab({
  title: ["实验 1.4 传播延时与反相器链", "Lab 1.4 Propagation delay and inverter chains"],
  goal: ["用逐级放大的反相器链驱动大电容：改级数和负载，找到最快的级数，与 ln F / ln 4 比较；找出满足延时要求的最少级数。",
         "Drive a large capacitance with a tapered inverter chain: vary the number of stages and the load, find the fastest chain and compare it with ln F / ln 4; find the fewest stages that meet the delay requirement."],
  scenes: [
    { id: "gate", robot: true, name: ["采样时钟送给电流采样 ADC", "Sampling clock to the current ADC"], hide: [],
      problem: { title: ["机器人问题：在 PWM 中点采样电机电流", "Robot problem: sampling motor current at mid-PWM"],
                 text: ["芯片把采样时钟送出引脚，接到板上电流采样 ADC。引脚、封装、走线和 ADC 输入端合计约 10 pF。采样时刻要与 PWM 计数对齐，时序预算给这个输出缓冲器的延时不超过 0.35 ns。最小反相器直接驱动不了，要几级？",
                        "The chip sends the sampling clock off-chip to the current-sensing ADC. Pin, package, trace and ADC input add up to about 10 pF. The sampling instant must line up with the PWM counter, and the timing budget allows this output buffer at most 0.35 ns. A minimum inverter cannot drive it alone: how many stages are needed?"] } },
  ],
  params: [
    { id: "N", name: ["级数 N", "Stages N"], min: 1, max: 10, step: 1, value: 1, unit: "", digits: 0 },
    { id: "CL", name: ["负载电容 CL", "Load capacitance CL"], min: 0.5, max: 20, step: 0.5, value: 10, unit: "pF", digits: 1 },
  ],
  tasks: [
    { id: "best", robot: true, text: ["负载 10 pF：找到总延时最小的级数。", "Load 10 pF: find the number of stages with the smallest total delay."],
      demo: { scene: "gate", set: { CL: 10, N: 6 }, press: [], wait: 1 } },
    { id: "few", robot: true, text: ["负载 10 pF：找到总延时小于 0.35 ns 的最少级数。它比最快的级数省了什么？", "Load 10 pF: find the fewest stages with total delay below 0.35 ns. What does it save compared with the fastest chain?"],
      demo: { scene: "gate", set: { CL: 10, N: 5 }, press: [], wait: 1 } },
    { id: "small", text: ["负载改为 2 pF：再找最快的级数，与 ln F / ln 4 比较。", "Change the load to 2 pF: find the fastest chain again and compare with ln F / ln 4."],
      demo: { scene: "gate", set: { CL: 2, N: 5 }, press: [], wait: 1 } },
  ],
  think: ["最快级数附近曲线很平，少用一级只慢几个百分点，却能省下哪些东西？若要求输出与输入同相，级数该怎么取？",
          "The curve is flat near the optimum: one stage fewer costs only a few per cent of delay. What does it save? If the output must be in phase with the input, how should the stage count be chosen?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["试过的级数", "stages tried"], color: "#1d6fb8" }, { name: ["延时要求 0.35 ns", "requirement 0.35 ns"], color: "#c0392b" }],
  reset(api, s) { check14(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, C1 = M1_4.cin(W14, R14 * W14), F = p.CL * 1e-12 / C1, t = t14(p.N, p.CL);
    return [[["总扇出 F = CL/C1", "Total fan-out F = CL/C1"], f(F, 0)],
            [["每级扇出 f = F^(1/N)", "Stage fan-out f = F^(1/N)"], f(Math.pow(F, 1 / p.N), 2)],
            [["总延时", "Total delay"], t >= 1e-9 ? f(t * 1e9, 2) + " ns" : f(t * 1e12, 0) + " ps"],
            [["ln F / ln 4", "ln F / ln 4"], f(Math.log(F) / Math.log(4), 2)],
            [["是否满足 0.35 ns", "Meets 0.35 ns"], t < TMAX14 ? api.T("满足", "yes") : api.T("不满足", "no")],
            [["输出相位", "Output phase"], p.N % 2 ? api.T("反相（奇数级）", "inverted (odd)") : api.T("同相（偶数级）", "in phase (even)")]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mu = css("--muted");
    const blue = "#1d6fb8", red = "#c0392b", amber = "#e67e22";
    const C1 = M1_4.cin(W14, R14 * W14), F = p.CL * 1e-12 / C1, f = Math.pow(F, 1 / p.N);
    // top: the chain; triangle height grows as f^i, compressed logarithmically so the last stage fits
    const top = h * 0.06, band = h * 0.3, x0 = w * 0.06, x1 = w * 0.82, step = (x1 - x0) / p.N;
    const hmax = band * 0.9, hmin = band * 0.18, lmax = Math.log(F);
    let xa = x0;
    api.line(x0 - 20, top + band / 2, x0, top + band / 2, ink, 2); api.label("in", x0 - 22, top + band / 2 - 10, mu, 11);
    for (let i = 0; i < p.N; i++) {
      const hi = hmin + (hmax - hmin) * (i * Math.log(f)) / (lmax || 1), wi = Math.min(step * 0.6, hi * 0.9), cy = top + band / 2;
      const xs = xa + (step - wi) / 2;
      api.line(xa, cy, xs, cy, ink, 2);
      api.line(xs, cy - hi / 2, xs, cy + hi / 2, blue, 2); api.line(xs, cy - hi / 2, xs + wi, cy, blue, 2); api.line(xs, cy + hi / 2, xs + wi, cy, blue, 2);
      api.circle(xs + wi + 3, cy, 3, null, blue);
      if (p.N <= 7) api.label("×" + api.fmt(Math.pow(f, i), Math.pow(f, i) < 10 ? 1 : 0), xs + wi / 2 - 4, cy + hi / 2 + 12, mu, 10, "center");
      api.line(xs + wi + 6, cy, xa + step, cy, ink, 2);
      xa += step;
    }
    const cy = top + band / 2;
    api.line(x1, cy, x1 + 14, cy, ink, 2); api.line(x1 + 14, cy, x1 + 14, cy + 14, ink, 2);
    api.line(x1 + 4, cy + 14, x1 + 24, cy + 14, amber, 3); api.line(x1 + 4, cy + 20, x1 + 24, cy + 20, amber, 3);
    api.label(api.fmt(p.CL, 1) + " pF", x1 + 30, cy + 17, amber, 12);
    // bottom: the stages tried at this load
    const key = p.CL.toFixed(1);
    if (tried14.CL !== key) { tried14.CL = key; tried14.pts = {}; }
    tried14.pts[p.N] = t14(p.N, p.CL) * 1e12;
    const px = w * 0.1, py = top + band + h * 0.08, pw = w * 0.84, ph = h - py - h * 0.1;
    const ns = Object.keys(tried14.pts).map(Number).sort((a, b) => a - b), ymax = Math.max(600, ...ns.map((n) => Math.min(tried14.pts[n], 3000))) * 1.1;
    const ax = api.plot(px, py, pw, ph, [{ pts: [[0.5, TMAX14 * 1e12], [10.5, TMAX14 * 1e12]], color: red }], { xmin: 0.5, xmax: 10.5, ymin: 0, ymax, xlabel: "N", ylabel: "t / ps" });
    for (let n = 1; n <= 10; n++) api.label(String(n), ax.X(n), py + ph + 10, mu, 10, "center");
    api.label("350", px - 4, ax.Y(TMAX14 * 1e12), red, 10, "right");
    ns.forEach((n) => {
      const v = tried14.pts[n], y = ax.Y(Math.min(v, ymax));
      api.rect(ax.X(n) - 8, y, 16, py + ph - y, n === p.N ? blue : "rgba(29,111,184,0.4)");
      api.label(v >= 1000 ? api.fmt(v / 1000, 1) + " ns" : api.fmt(v, 0), ax.X(n) + 10, y - 9, ink, 10, "left");
    });
  },
});

function check14(api) {
  const p = api.p;
  if (Math.abs(p.CL - 10) < 1e-9 && p.N === best14(10)) api.done("best");
  if (Math.abs(p.CL - 10) < 1e-9 && p.N === few14(10)) api.done("few");
  if (Math.abs(p.CL - 2) < 1e-9 && p.N === best14(2)) api.done("small");
}
