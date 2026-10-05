// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/lab1_3.body.js、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M1_3 = (function () {
  var module, self = {};
  /* 问渠微电子实验 · MOSFET 与 CMOS 反相器模型（长沟道平方律＋有效参数）
   * 与 samples/数字集成电路设计/生成脚本/model.py 算法一一对应（第 17 轮 RM2）。
   * 用法：浏览器 WQMos.create(params)；Node require('./mos.js').create(params)
   */
  (function (root, factory) {
    if (typeof module === 'object' && module.exports) module.exports = factory();
    else root.WQMos = factory();
  })(typeof self !== 'undefined' ? self : this, function () {
    function create(P) {
      const { VDD, VTn, VTp, kn, kp, L, Wmin, Cg, Cd } = P;
      const m = { P };
  
      m.idn = (vgs, vds, W, l = L) => {
        const vov = vgs - VTn;
        if (vov <= 0 || vds <= 0) return 0;
        const k = kn * W / l;
        return vds < vov ? k * (vov * vds - vds * vds / 2) : k / 2 * vov * vov;
      };
      m.idp = (vsg, vsd, W, l = L) => {
        const vov = vsg - VTp;
        if (vov <= 0 || vsd <= 0) return 0;
        const k = kp * W / l;
        return vsd < vov ? k * (vov * vsd - vsd * vsd / 2) : k / 2 * vov * vov;
      };
      m.region = (vgs, vds, VT) => (vgs - VT <= 0 ? 'off' : vds < vgs - VT ? 'lin' : 'sat');
  
      m.vout = (vin, Wn, Wp, vdd = VDD) => {
        let lo = 0, hi = vdd;
        for (let i = 0; i < 60; i++) {
          const mid = (lo + hi) / 2;
          const f = m.idn(vin, mid, Wn) - m.idp(vdd - vin, vdd - mid, Wp);
          if (f > 0) hi = mid; else lo = mid;
        }
        return (lo + hi) / 2;
      };
      m.vm = (Wn, Wp, vdd = VDD) => {
        const r = Math.sqrt(kp * Wp / (kn * Wn));
        return (VTn + r * (vdd - VTp)) / (1 + r);
      };
      m.vtc = (Wn, Wp, vdd = VDD, step = 0.0005) => {
        const n = Math.round(vdd / step), vs = [], vo = [];
        for (let i = 0; i <= n; i++) { vs.push(i * step); vo.push(m.vout(i * step, Wn, Wp, vdd)); }
        return { vs, vo, step };
      };
      m.noiseMargins = (Wn, Wp, vdd = VDD, step = 0.0005) => {
        const { vs, vo } = m.vtc(Wn, Wp, vdd, step);
        let first = -1, last = -1;
        for (let i = 1; i < vs.length - 1; i++) {
          const g = (vo[i + 1] - vo[i - 1]) / (2 * step);
          if (g < -1) { if (first < 0) first = i; last = i; }
        }
        const VIL = vs[first], VIH = vs[last];
        const VOH = m.vout(VIL, Wn, Wp, vdd), VOL = m.vout(VIH, Wn, Wp, vdd);
        return { VIL, VIH, VOH, VOL, NML: VIL - VOL, NMH: VOH - VIH };
      };
  
      m.idsatN = (W, vdd = VDD) => kn / 2 * W / L * (vdd - VTn) ** 2;
      m.idsatP = (W, vdd = VDD) => kp / 2 * W / L * (vdd - VTp) ** 2;
      m.reqN = (W, vdd = VDD) => 0.75 * vdd / m.idsatN(W, vdd);
      m.reqP = (W, vdd = VDD) => 0.75 * vdd / m.idsatP(W, vdd);
      m.cin = (Wn, Wp) => (Wn + Wp) * Cg;
      m.delays = (Wn, Wp, CL, vdd = VDD) => {
        const Cself = (Wn + Wp) * Cd;
        return { tphl: 0.69 * m.reqN(Wn, vdd) * (Cself + CL), tplh: 0.69 * m.reqP(Wp, vdd) * (Cself + CL) };
      };
      m.fo4 = (Wn, Wp, vdd = VDD) => m.delays(Wn, Wp, 4 * m.cin(Wn, Wp), vdd);
      m.chainDelay = (N, CL, ratio, vdd = VDD) => {
        const Wn = Wmin, Wp = ratio * Wmin, C1 = m.cin(Wn, Wp);
        const f = Math.pow(CL / C1, 1 / N);
        const R = (m.reqN(Wn, vdd) + m.reqP(Wp, vdd)) / 2;
        return N * 0.69 * R * C1 * (Cd / Cg + f);
      };
      m.wnForVol = (I, VOLmax, vdd = VDD) => I / (kn / L * ((vdd - VTn) * VOLmax - VOLmax * VOLmax / 2));
      m.dynPower = (N, alpha, C, V, f) => alpha * C * V * V * f * N;
      /* 给实验动画用：一阶 RC 近似的输出波形（输入理想方波，周期 T） */
      m.rcWave = (Wn, Wp, CL, T, npts = 400, vdd = VDD) => {
        const Cself = (Wn + Wp) * Cd, C = Cself + CL;
        const tauF = m.reqN(Wn, vdd) * C, tauR = m.reqP(Wp, vdd) * C;
        const t = [], vin = [], vo = [];
        let v = vdd;
        const dt = T / npts;
        for (let i = 0; i <= 2 * npts; i++) {
          const ti = i * dt, high = (ti % T) < T / 2;
          // 输入高 → 输出向 0 放电；输入低 → 向 VDD 充电
          if (i > 0) v = high ? v * Math.exp(-dt / tauF) : vdd - (vdd - v) * Math.exp(-dt / tauR);
          t.push(ti); vin.push(high ? vdd : 0); vo.push(v);
        }
        return { t, vin, vo };
      };
  
      m.fopt = (gamma) => {
        let lo = Math.E, hi = 10;
        for (let i = 0; i < 80; i++) { const mid = (lo + hi) / 2; if (mid * (Math.log(mid) - 1) < gamma) lo = mid; else hi = mid; }
        return (lo + hi) / 2;
      };
      m.fo4Tp = (ratio, vdd = VDD) => { const d = m.fo4(Wmin, ratio * Wmin, vdd); return (d.tphl + d.tplh) / 2; };
      m.vddForFo4 = (limit, ratio, lo = 0.9, hi = VDD) => {
        for (let i = 0; i < 80; i++) { const mid = (lo + hi) / 2; if (m.fo4Tp(ratio, mid) > limit) lo = mid; else hi = mid; }
        return hi;
      };
      m.reference = () => {
        const r = kn / kp, pr = P.problems, out = { r, idsat_n_per_um: m.idsatN(1), idsat_p_per_um: m.idsatP(1) };
        const w = m.wnForVol(pr.p11.Iload, pr.p11.VOLmax);
        out.p11 = { Wn: w, WnL: w / L, Ron: pr.p11.VOLmax / pr.p11.Iload };
        out.p12 = {};
        for (const [key, ratio] of [['ratio1', 1], ['ratio_r', r]]) {
          const nm = m.noiseMargins(Wmin, ratio * Wmin); nm.VM = m.vm(Wmin, ratio * Wmin); out.p12[key] = nm;
        }
        out.p13 = {};
        for (const [key, ratio] of [['ratio1', 1], ['ratio_sqrt', Math.sqrt(r)], ['ratio_r', r]]) {
          const d = m.fo4(Wmin, ratio * Wmin), tp = (d.tphl + d.tplh) / 2;
          out.p13[key] = { ratio, tphl: d.tphl, tplh: d.tplh, tp, mismatch: (d.tplh - d.tphl) / tp };
        }
        const CL = pr.p14.CL, C1 = m.cin(Wmin, r * Wmin), t = {};
        for (let N = 1; N <= 10; N++) t[N] = m.chainDelay(N, CL, r);
        let Nbest = 1; for (let N = 2; N <= 10; N++) if (t[N] < t[Nbest]) Nbest = N;
        let Nfew = 0; for (let N = 1; N <= 10; N++) if (t[N] < pr.p14.tmax) { Nfew = N; break; }
        const gamma = Cd / Cg;
        out.p14 = { Cin: C1, F: CL / C1, Nopt4: Math.log(CL / C1) / Math.log(4), t, gamma, fopt: m.fopt(gamma), Nbest, Nfew };
        const q = pr.p15;
        out.p15 = { P_VDD: m.dynPower(q.N, q.alpha, q.Cgate, VDD, q.f), P_low: m.dynPower(q.N, q.alpha, q.Cgate, q.Vlow, q.f),
                    Vlim: m.vddForFo4(q.fo4max, r), fo4_low: m.fo4Tp(r, q.Vlow) };
        out.r_lab = Math.round(r * 20) / 20;
        return out;
      };
      return m;
    }
    return { create };
  });
  return self.WQMos.create({"_note":"SKY130 tt 27 °C 校准值（第 17 轮附 3.4，samples/数字集成电路设计/生成脚本/calib/calib.py）：VT 为使传输特性最接近仿真的有效值（线性区外推值见 calib/result.json），k′ 由 IDSAT 反推，Cg、Cd 由输入电容与扇出拟合后按 FO4 延时修正","VDD":1.8,"VTn":0.55,"VTp":0.55,"kn":0.0000845,"kp":0.0000348,"L":0.15,"Wmin":0.42,"Cg":1.25e-15,"Cd":1.97e-15,"problems":{"p11":{"Iload":0.001,"VOLmax":0.2},"p12":{"noise":0.3},"p14":{"CL":1e-11,"tmax":3.5e-10},"p15":{"N":10000,"alpha":0.1,"Cgate":5e-15,"f":100000000,"Vlow":1.2,"fo4max":1e-10}},"wires":{"_note":"SKY130 导线参数（典型值），由 samples/数字集成电路设计/生成脚本/calib/wires.py 从 open_pdks 的 sky130A.tech 读出：Rsq Ω/□；Carea aF/μm²（对衬底）；Cfringe aF/μm（每条边，对衬底）；同层耦合每微米 Kside/(s+s0) aF；z、t 层底高度与厚度 μm；wmin、smin 最小线宽、间距 μm；via 每个通孔 Ω","layers":{"li1":{"Rsq":12.8,"Carea":36.99,"Cfringe":40.7,"Kside":25.5,"s0":0.14,"z":0.9361,"t":0.1,"wmin":0.17,"smin":0.17},"met1":{"Rsq":0.125,"Carea":25.78,"Cfringe":40.57,"Kside":44,"s0":0.25,"z":1.3761,"t":0.36,"wmin":0.14,"smin":0.14},"met2":{"Rsq":0.125,"Carea":17.5,"Cfringe":37.76,"Kside":50,"s0":0.3,"z":2.0061,"t":0.36,"wmin":0.14,"smin":0.14},"met3":{"Rsq":0.047,"Carea":12.37,"Cfringe":40.99,"Kside":74,"s0":0.4,"z":2.7861,"t":0.845,"wmin":0.3,"smin":0.3},"met4":{"Rsq":0.047,"Carea":8.42,"Cfringe":36.68,"Kside":94,"s0":0.57,"z":4.0211,"t":0.845,"wmin":0.3,"smin":0.3},"met5":{"Rsq":0.029,"Carea":6.32,"Cfringe":38.85,"Kside":155,"s0":0.5,"z":5.3711,"t":1.26,"wmin":1.6,"smin":1.6}},"via":{"li1-met1":9.3,"met1-met2":4.5,"met2-met3":3.41,"met3-met4":3.41,"met4-met5":0.38}},"gates_sim":{"_note":"SKY130 门参数仿真值（samples/数字集成电路设计/生成脚本/calib/calib_gates.py）：g、p 以同一仿真里参考反相器的 τ 为单位；A 为靠近输出的输入，B 为靠近电源轨的输入；pseudo_nmos 为 PMOS 负载取最小宽度时的输出低电平与静态电流；pass 为 10 fF 负载充电 10 ns 后的输出高电平","p_inv":1.559,"gates":{"nand2_A":{"g":1.176,"p":1.944},"nand2_B":{"g":1.166,"p":2.546},"nand3_A":{"g":1.387,"p":2.282},"nand3_B":{"g":1.391,"p":3.963},"nor2_A":{"g":1.68,"p":2.313},"nor2_B":{"g":1.643,"p":3.85},"nor3_A":{"g":2.363,"p":2.726},"nor3_B":{"g":2.342,"p":6.831}},"pseudo_nmos":[{"wn_over_wp":1,"VOL":0.1832,"I":0.0000825},{"wn_over_wp":2,"VOL":0.0788,"I":0.000084},{"wn_over_wp":4,"VOL":0.0332,"I":0.0000847}],"pass":{"nmos":1.089,"tgate":1.8}}});
})();
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
