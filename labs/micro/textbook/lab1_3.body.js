// 实验 1.3 尺寸与对称（配 1.3 节）。场景：电机控制芯片的时钟缓冲器。左图是一阶 RC 近似的输入、输出波形，
// 右图是 tPHL、tPLH 与平均延时随 Wp/Wn 的曲线（当前扇出），竖线是当前尺寸。延时按式 (1.3.1)、(1.3.2) 计算，
// 与书中程序 1.3.1 同一模型。任务 3 要求先在扇出 4 下对称、再换到扇出 1 或 8 仍对称；“扇出 4 下对称过”记在闭包里，重置不丢。
const W13 = M1_3.P.Wmin, R13 = M1_3.P.kn / M1_3.P.kp;
const seen13 = { fo4: false };
function d13(ratio, fo) {                                   // 负载为 fo 个同样的反相器
  const Wp = ratio * W13, d = M1_3.delays(W13, Wp, fo * M1_3.cin(W13, Wp));
  return { tphl: d.tphl, tplh: d.tplh, tp: (d.tphl + d.tplh) / 2 };
}
function best13(fo) { let b = 0.5, t = Infinity; for (let x = 0.5; x <= 4.0001; x += 0.005) { const v = d13(x, fo).tp; if (v < t) { t = v; b = x; } } return { ratio: b, tp: t }; }

WQ.lab({
  title: ["实验 1.3 尺寸与对称", "Lab 1.3 Sizing and symmetry"],
  goal: ["调 PMOS 与 NMOS 的宽度比，看上升、下降延时怎样变；分别找到上升下降相等的对称尺寸和平均延时最小的尺寸。",
         "Change the PMOS-to-NMOS width ratio and watch the rise and fall delays; find the symmetric sizing and the sizing with the smallest average delay."],
  scenes: [
    { id: "clk", robot: true, name: ["电机控制芯片的时钟缓冲器", "Clock buffer in the motor controller"], hide: [],
      problem: { title: ["机器人问题：时钟的占空比", "Robot problem: the clock duty cycle"],
                 text: ["500 MHz 的计数时钟经一串反相器分到各计数器，周期只有 2 ns。上升沿比下降沿慢，高电平就被“吃掉”一截，占空比不再是 50 %。PMOS 应该多宽？",
                        "A 500 MHz counting clock passes through a string of inverters to the counters; its period is only 2 ns. If rising edges are slower than falling ones, part of each high phase is lost and the duty cycle drifts from 50 %. How wide should the PMOS be?"] } },
  ],
  params: [
    { id: "ratio", name: ["尺寸比 Wp/Wn", "Size ratio Wp/Wn"], min: 0.5, max: 4, step: 0.05, value: 1, unit: "", digits: 2 },
    { id: "fo", name: ["扇出（驱动几个同样的反相器）", "Fan-out (identical inverters driven)"], min: 1, max: 8, step: 1, value: 4, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "sym", robot: true, text: ["扇出为 4：调 Wp/Wn 使 tPLH 与 tPHL 相差不到 3 %。", "Fan-out 4: make tPLH and tPHL agree within 3 %."],
      demo: { scene: "clk", set: { fo: 4, ratio: 2.45 }, press: [], wait: 1 } },
    { id: "min", text: ["扇出为 4：找到平均延时 tp 最小的尺寸（与最小值相差不到 0.05 %）。它比对称尺寸窄多少？", "Fan-out 4: find the ratio with the smallest average delay tp (within 0.05 % of the minimum). How much narrower is it than the symmetric ratio?"],
      demo: { scene: "clk", set: { fo: 4, ratio: 1.55 }, press: [], wait: 1 } },
    { id: "fo", text: ["先在扇出 4 下调到对称，再把扇出改为 1 或 8：上升下降仍相差不到 3 % 吗？对称尺寸随负载变吗？", "First make the inverter symmetric at fan-out 4, then change the fan-out to 1 or 8: do rise and fall still agree within 3 %? Does the symmetric ratio depend on the load?"],
      demo: { scene: "clk", set: { ratio: 2.45, fo: 1 }, press: [], wait: 1 } },
  ],
  think: ["对称尺寸为什么与负载无关，而平均延时最小的尺寸几乎也与负载无关？如果负载里有一大段与尺寸无关的连线电容，√r 这个结论会怎样变？",
          "Why does the symmetric ratio not depend on the load, and why does the best-average ratio hardly depend on it either? If the load includes a large wire capacitance that does not scale with the gate, how does the √r result change?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["tPHL（下降）", "tPHL (fall)"], color: "#1d6fb8" }, { name: ["tPLH（上升）", "tPLH (rise)"], color: "#c0392b" }, { name: ["平均 tp", "average tp"], color: "#2e7d32" }],
  reset(api, s) { check13(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, d = d13(p.ratio, p.fo), b = best13(p.fo);
    const mis = (d.tplh - d.tphl) / d.tp * 100;
    return [[["tPHL / tPLH", "tPHL / tPLH"], f(d.tphl * 1e12, 1) + " / " + f(d.tplh * 1e12, 1) + " ps"],
            [["平均延时 tp", "Average tp"], f(d.tp * 1e12, 2) + " ps"],
            [["上升比下降慢", "Rise slower than fall by"], f(mis, 1) + " %"],
            [["500 MHz 时钟经一级后的占空比", "Duty cycle after one stage (500 MHz)"], f(50 + (d.tphl - d.tplh) / 2e-9 * 100, 1) + " %"],
            [["r = k′n/k′p", "r = k′n/k′p"], f(R13, 2)],
            [["输入电容", "Input capacitance"], f(M1_3.cin(W13, p.ratio * W13) * 1e15, 2) + " fF"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mu = css("--muted");
    const blue = "#1d6fb8", red = "#c0392b", green = "#2e7d32", amber = "#e67e22";
    const Wp = p.ratio * W13, d = d13(p.ratio, p.fo), VDD = M1_3.P.VDD;
    // left: input square wave and RC output; period chosen so both edges settle
    const T = 12 * Math.max(d.tphl, d.tplh) / 0.69;            // 每半个周期约 6 个时间常数
    const wv = M1_3.rcWave(W13, Wp, p.fo * M1_3.cin(W13, Wp), T, 200);
    const px = w * 0.06, py = h * 0.08, pw = w * 0.4, ph = h * 0.36;
    const ps = (arr) => wv.t.map((t, i) => [t * 1e12, arr[i]]);
    const ax1 = api.plot(px, py, pw, ph, [{ pts: ps(wv.vin), color: amber }], { xmin: 0, xmax: 2 * T * 1e12, ymin: -0.1, ymax: 2, ylabel: "Vin" });
    const ax2 = api.plot(px, py + ph + 24, pw, ph, [{ pts: ps(wv.vo), color: blue }], { xmin: 0, xmax: 2 * T * 1e12, ymin: -0.1, ymax: 2, xlabel: "t / ps", ylabel: "Vout" });
    api.line(px, ax2.Y(VDD / 2), px + pw, ax2.Y(VDD / 2), mu, 1, [4, 4]);
    // mark the two delays on the first period: input rises at 0 (output falls), input falls at T/2 (output rises)
    const tf = d.tphl * 1e12, tr = d.tplh * 1e12, half = T / 2 * 1e12;
    api.line(ax2.X(0), ax2.Y(VDD / 2), ax2.X(tf), ax2.Y(VDD / 2), blue, 3); api.label("tPHL", ax2.X(tf) + 4, ax2.Y(VDD / 2) - 10, blue, 11, "left");
    api.line(ax2.X(half), ax2.Y(VDD / 2), ax2.X(half + tr), ax2.Y(VDD / 2), red, 3); api.label("tPLH", ax2.X(half + tr / 2), ax2.Y(VDD / 2) + 12, red, 11, "center");
    api.label(api.T("周期按延时自动放缩", "time axis scales with the delay"), px, py + 2 * ph + 46 > h - 6 ? h - 6 : py + 2 * ph + 46, mu, 11);
    // right: delays versus ratio at the current fan-out
    const qx = w * 0.56, qy = h * 0.08, qw = w * 0.4, qh = h * 0.76;
    const fall = [], rise = [], avg = [];
    for (let x = 0.5; x <= 4.0001; x += 0.05) { const e = d13(x, p.fo); fall.push([x, e.tphl * 1e12]); rise.push([x, e.tplh * 1e12]); avg.push([x, e.tp * 1e12]); }
    const ymax = Math.min(d13(0.5, p.fo).tplh, 4 * d13(R13, p.fo).tp) * 1e12 * 1.05;
    const ax = api.plot(qx, qy, qw, qh, [{ pts: fall, color: blue }, { pts: rise, color: red }, { pts: avg, color: green }],
      { xmin: 0.5, xmax: 4, ymin: 0, ymax, xlabel: "Wp/Wn", ylabel: "ps" });
    api.line(ax.X(p.ratio), qy, ax.X(p.ratio), qy + qh, ink, 1.5);
    api.line(ax.X(R13), qy + qh - 6, ax.X(R13), qy + qh, mu, 2); api.label("r", ax.X(R13), qy + qh + 12, mu, 11, "center");
    api.line(ax.X(Math.sqrt(R13)), qy + qh - 6, ax.X(Math.sqrt(R13)), qy + qh, mu, 2); api.label("√r", ax.X(Math.sqrt(R13)), qy + qh + 12, mu, 11, "center");
  },
});

function check13(api) {
  const p = api.p, d = d13(p.ratio, p.fo), sym = Math.abs(d.tplh - d.tphl) / d.tphl < 0.03;
  if (p.fo === 4 && sym) api.done("sym");
  if (p.fo === 4 && d.tp <= best13(4).tp * 1.0005) api.done("min");
  if (sym && p.fo === 4) seen13.fo4 = true;
  if (sym && seen13.fo4 && (p.fo === 1 || p.fo === 8)) api.done("fo");
}
