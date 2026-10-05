// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/lab1_4.body.js、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M1_4 = (function () {
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
  return self.WQMos.create({"_note":"SKY130 tt 27 °C 校准值（第 17 轮附 3.4，samples/数字集成电路设计/生成脚本/calib/calib.py）：VT 为使传输特性最接近仿真的有效值（线性区外推值见 calib/result.json），k′ 由 IDSAT 反推，Cg、Cd 由输入电容与扇出拟合后按 FO4 延时修正","VDD":1.8,"VTn":0.55,"VTp":0.55,"kn":0.0000845,"kp":0.0000348,"L":0.15,"Wmin":0.42,"Cg":1.25e-15,"Cd":1.97e-15,"problems":{"p11":{"Iload":0.001,"VOLmax":0.2},"p12":{"noise":0.3},"p14":{"CL":1e-11,"tmax":3.5e-10},"p15":{"N":10000,"alpha":0.1,"Cgate":5e-15,"f":100000000,"Vlow":1.2,"fo4max":1e-10}}});
})();
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
