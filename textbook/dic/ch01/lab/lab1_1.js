// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/lab1_1.body.js、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M1_1 = (function () {
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
// 实验 1.1 MOSFET 开关与 CMOS 反相器（配 1.1 节）。两个场景：开关路径（输入 0/1 时谁导通、电流怎样走）、
// 光耦输入（NMOS 吸收负载电流时的输出低电平）。右侧小图是 NMOS 在 VGS = VDD 下的输出特性和负载线，交点即 VOL。
const VDD11 = M1_1.P.VDD;
const seen11 = { lo: false, hi: false };
function vol11(Wn, I) {                                   // 解 ID(VDD, VOL) = I；超过饱和电流时返回 null
  if (I >= M1_1.idsatN(Wn)) return null;
  let lo = 0, hi = VDD11 - M1_1.P.VTn;
  for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; if (M1_1.idn(VDD11, m, Wn) > I) hi = m; else lo = m; }
  return (lo + hi) / 2;
}
const WNEED11 = (I) => M1_1.wnForVol(I, 0.2);

WQ.lab({
  title: ["实验 1.1 MOSFET 开关与 CMOS 反相器", "Lab 1.1 MOSFET switches and the CMOS inverter"],
  goal: ["看清 CMOS 反相器两个管子怎样一开一合；用 NMOS 的线性区求满足输出低电平要求的最小管宽。",
         "See how the two transistors of a CMOS inverter switch in turn; use the NMOS linear region to find the smallest width meeting a VOL requirement."],
  scenes: [
    { id: "path", name: ["开关路径", "Switching path"], hide: ["wn", "il"],
      problem: { title: ["电流从哪里走", "Where the current flows"],
                 text: ["输入切到 0 和 1，看哪个管子导通、负载电容怎样充电和放电。稳态时电源到地有没有直流通路？",
                        "Switch the input to 0 and to 1. Which transistor conducts, and how does the load capacitor charge and discharge? Is there a DC path from VDD to ground in steady state?"] } },
    { id: "opto", robot: true, name: ["关节驱动板的光耦输入", "Optocoupler input on the joint driver"], hide: [],
      problem: { title: ["机器人问题：光耦输入", "Robot problem: the optocoupler input"],
                 text: ["芯片输出管脚要吸收 1 mA，输出低电平不超过 0.2 V。NMOS 至少要多宽？",
                        "The output pin must sink 1 mA with the low level at most 0.2 V. How wide must the NMOS be?"] } },
  ],
  params: [
    { id: "vin", name: ["输入（0 = 低，1 = 高）", "Input (0 = low, 1 = high)"], min: 0, max: 1, step: 1, value: 1, unit: "", digits: 0 },
    { id: "wn", name: ["NMOS 宽度 Wn", "NMOS width Wn"], min: 0.42, max: 20, step: 0.02, value: 2, unit: "μm", digits: 2 },
    { id: "il", name: ["负载电流", "Load current"], min: 0.1, max: 3, step: 0.05, value: 1, unit: "mA", digits: 2 },
  ],
  tasks: [
    { id: "both", text: ["把输入分别切到 0 和 1：两种稳态下各有一个管子截止，电源到地没有直流通路。", "Switch the input to 0 and to 1: in each steady state one transistor is off and there is no DC path."],
      demo: { scene: "path", set: { vin: 0 }, press: [], wait: 1 } },
    { id: "size", robot: true, text: ["光耦负载 1 mA：调 Wn 使 VOL ≤ 0.2 V，且 Wn 不超过所需最小值的 1.08 倍（不浪费面积）。", "Optocoupler load 1 mA: choose Wn so that VOL ≤ 0.2 V and Wn is at most 1.08 × the minimum needed."],
      demo: { scene: "opto", set: { vin: 1, il: 1, wn: 7.9 }, press: [], wait: 1 } },
    { id: "twice", text: ["负载加到 2 mA：VOL 是否正好翻倍？再把 Wn 调到刚好满足 VOL ≤ 0.2 V（不超过最小值的 1.08 倍）。", "Raise the load to 2 mA: does VOL exactly double? Then set Wn just wide enough for VOL ≤ 0.2 V (within 1.08 × the minimum)."],
      demo: { scene: "opto", set: { vin: 1, il: 2, wn: 15.5 }, press: [], wait: 1 } },
  ],
  think: ["接了光耦以后，反相器还算“静态功耗为零”吗？芯片的输出管脚为什么要比内部的门大得多？",
          "With the optocoupler attached, is the inverter's static power still zero? Why are output pins so much larger than internal gates?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["NMOS 输出特性", "NMOS output curve"], color: "#1d6fb8" }, { name: ["负载线", "load line"], color: "#e67e22" }],
  reset(api, s) { check11(api); },                       // 换场景、改参数后都会重置，在这里判定任务
  readouts(api, s) {
    const f = api.fmt, p = api.p;
    if (api.scene === "path") {
      return [[["输入", "Input"], p.vin ? "1（1.8 V）" : "0（0 V）"], [["导通的管子", "Conducting"], p.vin ? "NMOS" : "PMOS"],
              [["输出", "Output"], p.vin ? "0 V" : "1.8 V"], [["静态电流", "Static current"], api.T("≈ 0（总有一管截止）", "≈ 0 (one transistor is always off)")]];
    }
    const I = p.il * 1e-3, v = p.vin ? vol11(p.wn, I) : null;
    return [[["输出低电平 VOL", "Output low VOL"], p.vin ? (v === null ? api.T("拉不住（超过饱和电流）", "cannot hold (above IDSAT)") : f(v, 3) + " V") : api.T("输入为 0，输出为高", "input 0: output high")],
            [["工作区", "Region"], v === null ? "—" : api.T("线性区", "linear")],
            [["导通电阻 VOL/I", "On-resistance VOL/I"], v === null ? "—" : f(v / I, 0) + " Ω"],
            [["饱和电流", "Saturation current"], f(M1_1.idsatN(p.wn) * 1e3, 2) + " mA"],
            [["VOL ≤ 0.2 V 所需最小 Wn", "Minimum Wn for VOL ≤ 0.2 V"], f(WNEED11(I), 2) + " μm"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mu = css("--muted");
    const blue = "#1d6fb8", red = "#c0392b", amber = "#e67e22", green = css("--green");
    // left: the inverter as two switches
    const x = w * 0.2, top = h * 0.12, bot = h * 0.88, mid = h * 0.5;
    api.line(x - 40, top, x + 40, top, mu, 2); api.label("VDD", x - 46, top, mu, 12, "right");
    api.line(x - 40, bot, x + 90, bot, mu, 2); api.label("GND", x - 46, bot, mu, 12, "right");
    const sw = (y0, y1, closed, col, name) => {
      const a = y0 + (y1 - y0) * 0.3, b = y0 + (y1 - y0) * 0.7;
      api.line(x, y0, x, a, col, 3); api.line(x, a, closed ? x : x + 18, b, col, 3); api.line(x, b, x, y1, col, 3);
      api.label(name, x - 54, (y0 + y1) / 2, col, 12);
    };
    const on = p.vin === 1 || api.scene === "opto";
    sw(top, mid, !on, on ? mu : green, "PMOS"); sw(mid, bot, on, on ? green : mu, "NMOS");
    api.line(x, mid, x + 110, mid, ink, 2); api.circle(x, mid, 3, ink); api.label(api.T("输出", "out"), x + 116, mid, ink, 12);
    api.line(x + 70, mid, x + 70, mid + 30, ink, 2); api.line(x + 58, mid + 30, x + 82, mid + 30, ink, 2); api.line(x + 58, mid + 38, x + 82, mid + 38, ink, 2);
    api.line(x + 70, mid + 38, x + 70, bot, ink, 2);
    api.label(api.T("输入 = " + (on ? 1 : 0), "input = " + (on ? 1 : 0)), x - 70, h * 0.05, amber, 13);
    if (api.scene === "opto") {
      api.arrow(x + 120, mid - 30, x + 92, mid - 4, amber, 2); api.label(api.T("光耦 " + api.fmt(p.il, 2) + " mA", "opto " + api.fmt(p.il, 2) + " mA"), x + 100, mid - 40, amber, 12);
    } else {
      api.label(api.T(on ? "电容经 NMOS 放电" : "电容经 PMOS 充电", on ? "C discharges through the NMOS" : "C charges through the PMOS"), x - 10, bot + 16 > h - 4 ? h - 6 : bot + 16, ink, 12);
    }
    if (api.scene !== "opto") return;
    // right: NMOS output curve at VGS = VDD and the load line
    const px = w * 0.48, py = h * 0.1, pw = w * 0.48, ph = h * 0.72, I = p.il * 1e-3;
    const pts = []; for (let i = 0; i <= 100; i++) { const v = i / 100; pts.push([v, M1_1.idn(VDD11, v, p.wn) * 1e3]); }
    const ax = api.plot(px, py, pw, ph, [{ pts, color: blue }, { pts: [[0, p.il], [1, p.il]], color: amber }],
      { xmin: 0, xmax: 1, ymin: 0, ymax: 3.2, xlabel: "VDS / V", ylabel: "ID / mA" });
    api.line(ax.X(0.2), py, ax.X(0.2), py + ph, mu, 1, [4, 4]); api.label("0.2 V", ax.X(0.2) + 4, py + 12, mu, 11);
    const v = vol11(p.wn, I);
    if (v !== null) { api.circle(ax.X(v), ax.Y(p.il), 5, amber, ink); api.label("VOL", ax.X(v) + 8, ax.Y(p.il) - 10, ink, 12); }
    if (v !== null && v <= 0.2) api.label("✓", px + pw - 18, py + 14, green, 16); else api.label(api.T("VOL 太高", "VOL too high"), px + pw - 80, py + 14, red, 12);
  },
});

function check11(api) {
  const p = api.p;
  if (api.scene === "path") {
    if (p.vin === 0) seen11.lo = true; else seen11.hi = true;
    if (seen11.lo && seen11.hi) api.done("both");
    return;
  }
  if (p.vin !== 1) return;
  const I = p.il * 1e-3, v = vol11(p.wn, I);
  if (v === null || v > 0.2 + 1e-9) return;
  const need = WNEED11(I);
  if (p.wn > 1.08 * need) return;
  if (Math.abs(p.il - 1) < 1e-9) api.done("size");
  if (Math.abs(p.il - 2) < 1e-9) api.done("twice");
}
