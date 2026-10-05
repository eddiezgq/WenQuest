// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/lab1_2.body.js、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M1_2 = (function () {
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
  
      /* ---------- 第 2 章：门与逻辑努力（与 conventions/mos.py 一一对应） ---------- */
      const rr = kn / kp, gam = Cd / Cg;
      m.tau = () => 0.69 * (m.reqN(Wmin) + m.reqP(rr * Wmin)) / 2 * m.cin(Wmin, rr * Wmin);
      m.leG = (kind, n) => (kind === 'inv' ? 1 : kind === 'nand' ? (n + rr) / (1 + rr) : (1 + n * rr) / (1 + rr));
      m.leP = (kind, n) => (kind === 'inv' ? 1 : n) * gam;
      m.gateWidths = (kind, n) => (kind === 'inv' ? [Wmin, rr * Wmin] : kind === 'nand' ? [n * Wmin, rr * Wmin] : [Wmin, n * rr * Wmin]);
      m.pathDelay = (gs, ps, B, H) => {
        const G = gs.reduce((a, b) => a * b, 1), N = gs.length, F = G * B * H;
        return { D: N * Math.pow(F, 1 / N) + ps.reduce((a, b) => a + b, 0), F };
      };
      m.stageSizes = (gs, bs, Cin0, Cout) => {
        let G = 1, B = 1; gs.forEach((g, i) => { G *= g; B *= bs[i]; });
        const N = gs.length, f = Math.pow(G * B * Cout / Cin0, 1 / N), caps = [];
        let c = Cout;
        for (let i = N - 1; i >= 0; i--) { c = gs[i] * bs[i] * c / f; caps.unshift(c); }
        return { caps, f };
      };
      /* ---------- 第 4 章：导线 ---------- */
      const WL = (P.wires || {}).layers || {};
      m.wireR = (layer, w) => WL[layer].Rsq / w;
      m.wireC = (layer, w, s) => { const q = WL[layer]; let c = q.Carea * w + 2 * q.Cfringe; if (s != null) c += 2 * q.Kside / (s + q.s0); return c * 1e-18; };
      m.wireCc = (layer, s) => WL[layer].Kside / (s + WL[layer].s0) * 1e-18;
      m.wireDelay = (Rd, Cself, Rw, Cw, CL) => 0.69 * Rd * (Cself + Cw + CL) + 0.38 * Rw * Cw + 0.69 * Rw * CL;
      m.repeaterDelay = (Lw, layer, w, k, size, CL, s) => {
        const R0 = (m.reqN(Wmin) + m.reqP(rr * Wmin)) / 2, C0 = m.cin(Wmin, rr * Wmin);
        const Rd = R0 / size, Cself = gam * C0 * size, Cin = C0 * size, seg = Lw / k;
        const Rw = m.wireR(layer, w) * seg, Cw = m.wireC(layer, w, s) * seg, last = CL == null ? Cin : CL;
        let t = 0; for (let i = 0; i < k; i++) t += m.wireDelay(Rd, Cself, Rw, Cw, i < k - 1 ? Cin : last);
        return t;
      };
      m.repeaterOpt = (Lw, layer, w, s) => {
        const R0 = (m.reqN(Wmin) + m.reqP(rr * Wmin)) / 2, C0 = m.cin(Wmin, rr * Wmin), rw = m.wireR(layer, w), cw = m.wireC(layer, w, s);
        return { k: Lw * Math.sqrt(0.38 * rw * cw / (0.69 * R0 * C0 * (1 + gam))), size: Math.sqrt(R0 * cw / (rw * C0)) };
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
        const q23 = pr.p23, gn = m.leG('nand', q23.n_addr), H23 = q23.Cout_units / q23.Cin_units;
        out.ch2 = { tau: m.tau(), g: {}, p: {} };
        for (const [k, n] of [['nand', 2], ['nand', 3], ['nor', 2], ['nor', 3]]) { out.ch2.g[k + n] = m.leG(k, n); out.ch2.p[k + n] = m.leP(k, n); }
        out.ch2.dec = {};
        for (const N of [2, 3, 4]) {
          const gs = [gn].concat(Array(N - 1).fill(1)), ps = [m.leP('nand', q23.n_addr)].concat(Array(N - 1).fill(m.leP('inv', 1)));
          out.ch2.dec[N] = m.pathDelay(gs, ps, q23.branch, H23).D;
        }
        out.ch4 = { r: {}, c: {}, cn: {}, rep: {} };
        for (const [l, q] of Object.entries(WL)) { out.ch4.r[l] = m.wireR(l, q.wmin); out.ch4.c[l] = m.wireC(l, q.wmin); out.ch4.cn[l] = m.wireC(l, q.wmin, q.smin); }
        const q43 = pr.p43, CL43 = q43.load_units * m.cin(Wmin, r * Wmin);
        for (let k = 1; k <= 5; k++) out.ch4.rep[k] = m.repeaterDelay(q43.L_um, q43.layer, q43.w_um, k, 20, CL43);
        out.ch4.opt = m.repeaterOpt(q43.L_um, q43.layer, q43.w_um);
        return out;
      };
      return m;
    }
    return { create };
  });
  return self.WQMos.create({"_note":"SKY130 tt 27 °C 校准值（第 17 轮附 3.4，samples/数字集成电路设计/生成脚本/calib/calib.py）：VT 为使传输特性最接近仿真的有效值（线性区外推值见 calib/result.json），k′ 由 IDSAT 反推，Cg、Cd 由输入电容与扇出拟合后按 FO4 延时修正","VDD":1.8,"VTn":0.55,"VTp":0.55,"kn":0.0000845,"kp":0.0000348,"L":0.15,"Wmin":0.42,"Cg":1.25e-15,"Cd":1.97e-15,"problems":{"p11":{"Iload":0.001,"VOLmax":0.2},"p12":{"noise":0.3},"p14":{"CL":1e-11,"tmax":3.5e-10},"p15":{"N":10000,"alpha":0.1,"Cgate":5e-15,"f":100000000,"Vlow":1.2,"fo4max":1e-10},"p23":{"n_addr":3,"Cin_units":2,"Cout_units":32,"branch":4},"p41":{"L_um":3000},"p42":{"layer":"met2","w_um":0.14,"trunk_um":1000,"near_um":400,"far_um":1600,"leaf_load_units":20,"driver_size":20},"p43":{"L_um":3000,"layer":"met1","w_um":0.14,"load_units":20},"p44":{"layer":"met2","w_um":0.14,"len_um":500,"victim_size":1,"tr_ps":100}},"wires":{"_note":"SKY130 导线参数（典型值），由 samples/数字集成电路设计/生成脚本/calib/wires.py 从 open_pdks 的 sky130A.tech 读出：Rsq Ω/□；Carea aF/μm²（对衬底）；Cfringe aF/μm（每条边，对衬底）；同层耦合每微米 Kside/(s+s0) aF；z、t 层底高度与厚度 μm；wmin、smin 最小线宽、间距 μm；via 每个通孔 Ω","layers":{"li1":{"Rsq":12.8,"Carea":36.99,"Cfringe":40.7,"Kside":25.5,"s0":0.14,"z":0.9361,"t":0.1,"wmin":0.17,"smin":0.17},"met1":{"Rsq":0.125,"Carea":25.78,"Cfringe":40.57,"Kside":44,"s0":0.25,"z":1.3761,"t":0.36,"wmin":0.14,"smin":0.14},"met2":{"Rsq":0.125,"Carea":17.5,"Cfringe":37.76,"Kside":50,"s0":0.3,"z":2.0061,"t":0.36,"wmin":0.14,"smin":0.14},"met3":{"Rsq":0.047,"Carea":12.37,"Cfringe":40.99,"Kside":74,"s0":0.4,"z":2.7861,"t":0.845,"wmin":0.3,"smin":0.3},"met4":{"Rsq":0.047,"Carea":8.42,"Cfringe":36.68,"Kside":94,"s0":0.57,"z":4.0211,"t":0.845,"wmin":0.3,"smin":0.3},"met5":{"Rsq":0.029,"Carea":6.32,"Cfringe":38.85,"Kside":155,"s0":0.5,"z":5.3711,"t":1.26,"wmin":1.6,"smin":1.6}},"via":{"li1-met1":9.3,"met1-met2":4.5,"met2-met3":3.41,"met3-met4":3.41,"met4-met5":0.38}},"gates_sim":{"_note":"SKY130 门参数仿真值（samples/数字集成电路设计/生成脚本/calib/calib_gates.py）：g、p 以同一仿真里参考反相器的 τ 为单位；A 为靠近输出的输入，B 为靠近电源轨的输入；pseudo_nmos 为 PMOS 负载取最小宽度时的输出低电平与静态电流；pass 为 10 fF 负载充电 10 ns 后的输出高电平","p_inv":1.559,"gates":{"nand2_A":{"g":1.176,"p":1.944},"nand2_B":{"g":1.166,"p":2.546},"nand3_A":{"g":1.387,"p":2.282},"nand3_B":{"g":1.391,"p":3.963},"nor2_A":{"g":1.68,"p":2.313},"nor2_B":{"g":1.643,"p":3.85},"nor3_A":{"g":2.363,"p":2.726},"nor3_B":{"g":2.342,"p":6.831}},"pseudo_nmos":[{"wn_over_wp":1,"VOL":0.1832,"I":0.0000825},{"wn_over_wp":2,"VOL":0.0788,"I":0.000084},{"wn_over_wp":4,"VOL":0.0332,"I":0.0000847}],"pass":{"nmos":1.089,"tgate":1.8}}});
})();
// 实验 1.2 电压传输特性与噪声容限（配 1.2 节）。两个场景：传输特性（调尺寸比、移动输入看工作点）、
// 编码器输入（把 ±干扰叠加到 0 和 1 上，看会不会越过 VIL、VIH）。传输特性按式 (1.2.1) 逐点二分求解，
// VIL、VIH 取斜率为 −1 的两点，与书中程序 1.2.1 同一算法；按尺寸比缓存，拖动输入时不重算。
const VDD12 = M1_2.P.VDD, W12 = M1_2.P.Wmin, R12 = M1_2.P.kn / M1_2.P.kp;
const cache12 = {};
function vtc12(ratio) {
  const key = ratio.toFixed(3);
  if (!cache12[key]) {
    const nm = M1_2.noiseMargins(W12, ratio * W12), pts = [];
    for (let i = 0; i <= 180; i++) { const v = i * VDD12 / 180; pts.push([v, M1_2.vout(v, W12, ratio * W12)]); }
    cache12[key] = { nm, pts, vm: M1_2.vm(W12, ratio * W12) };
  }
  return cache12[key];
}
function gain12(vi, ratio) { const d = 0.002; return (M1_2.vout(vi + d, W12, ratio * W12) - M1_2.vout(vi - d, W12, ratio * W12)) / (2 * d); }

WQ.lab({
  title: ["实验 1.2 电压传输特性与噪声容限", "Lab 1.2 Voltage transfer characteristic and noise margins"],
  goal: ["扫描输入看输出，找到开关阈值 VM 和斜率为 −1 的两点；调尺寸比使 VM = VDD/2；用噪声容限判断干扰下会不会误判。",
         "Sweep the input and watch the output; find the switching threshold VM and the two unity-gain points; size the inverter for VM = VDD/2; use the noise margins to judge whether noise causes errors."],
  scenes: [
    { id: "vtc", name: ["传输特性", "Transfer curve"], hide: ["noise"],
      problem: { title: ["输入慢慢升高，输出怎样变", "How the output follows a slowly rising input"],
                 text: ["拖动输入电压，看工作点沿传输特性移动；中间那段几乎竖直，两个管子同时饱和。调 Wp/Wn，看 VM 怎样移动。",
                        "Drag the input and watch the operating point move along the curve; in the nearly vertical middle both transistors are saturated. Change Wp/Wn and watch VM move."] } },
    { id: "enc", robot: true, name: ["编码器信号进入控制芯片", "Encoder signal entering the controller"], hide: ["vi"],
      problem: { title: ["机器人问题：电缆上的干扰", "Robot problem: noise on the cable"],
                 text: ["编码器信号经 2 m 电缆进入芯片，叠加了约 ±0.3 V 的干扰：0 变成 0.3 V，1 变成 1.5 V。反相器还能判断对吗？它最多能承受多大的干扰？",
                        "The encoder signal reaches the chip through 2 m of cable with about ±0.3 V of noise: 0 becomes 0.3 V and 1 becomes 1.5 V. Does the inverter still decide correctly? How much noise can it take?"] } },
  ],
  params: [
    { id: "ratio", name: ["尺寸比 Wp/Wn", "Size ratio Wp/Wn"], min: 0.5, max: 5, step: 0.05, value: 1, unit: "", digits: 2 },
    { id: "vi", name: ["输入电压 Vin", "Input voltage Vin"], min: 0, max: 1.8, step: 0.01, value: 0.4, unit: "V", digits: 2 },
    { id: "noise", name: ["干扰幅度", "Noise amplitude"], min: 0, max: 1, step: 0.05, value: 0.3, unit: "V", digits: 2 },
  ],
  tasks: [
    { id: "vm", text: ["调 Wp/Wn，使开关阈值 VM 与 VDD/2 = 0.9 V 相差不到 0.01 V。这时的尺寸比和 r = k′n/k′p 有什么关系？", "Adjust Wp/Wn so that VM is within 0.01 V of VDD/2 = 0.9 V. How does this ratio relate to r = k′n/k′p?"],
      demo: { scene: "vtc", set: { ratio: 2.45 }, press: [], wait: 1 } },
    { id: "vil", text: ["Wp/Wn = 1 时，把输入移到 VIL（斜率为 −1 的左侧点，误差不超过 0.015 V），读出这时的增益。", "With Wp/Wn = 1, move the input to VIL (the left unity-gain point, within 0.015 V) and read the gain there."],
      demo: { scene: "vtc", set: { ratio: 1, vi: 0.72 }, press: [], wait: 1 } },
    { id: "noise", robot: true, text: ["编码器输入用对称尺寸（Wp/Wn 与 r 相差不到 0.1）：把干扰加大到刚好不超过较小的噪声容限（相差不到 0.05 V）。", "Encoder input with symmetric sizing (Wp/Wn within 0.1 of r): raise the noise until it just stays within the smaller noise margin (within 0.05 V)."],
      demo: { scene: "enc", set: { ratio: 2.45, noise: 0.7 }, press: [], wait: 1 } },
  ],
  think: ["干扰越过了 VIL 并不等于一定出错，但为什么设计时仍以噪声容限为界？如果把两个反相器串起来，第二级看到的干扰会变大还是变小？",
          "Crossing VIL does not always cause an error, so why do designers still treat the noise margin as the limit? With two inverters in series, does the second stage see more or less noise?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["传输特性", "transfer curve"], color: "#1d6fb8" }, { name: ["干扰后的输入范围", "input range with noise"], color: "#e67e22" }],
  reset(api, s) { check12(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, c = vtc12(p.ratio), nm = c.nm;
    const rows = [[["开关阈值 VM", "Switching threshold VM"], f(c.vm, 3) + " V"],
                  [["VIL / VIH", "VIL / VIH"], f(nm.VIL, 3) + " / " + f(nm.VIH, 3) + " V"],
                  [["NML / NMH", "NML / NMH"], f(nm.NML, 3) + " / " + f(nm.NMH, 3) + " V"],
                  [["r = k′n/k′p", "r = k′n/k′p"], f(R12, 2)]];
    if (api.scene === "vtc") {
      rows.push([["输出 Vout", "Output Vout"], f(M1_2.vout(p.vi, W12, p.ratio * W12), 3) + " V"], [["增益 dVout/dVin", "Gain dVout/dVin"], f(gain12(p.vi, p.ratio), 2)]);
    } else {
      const ok = p.noise <= Math.min(nm.NML, nm.NMH) + 1e-9;
      rows.push([["0 → 输入最高", "0 → worst input"], f(p.noise, 2) + " V"], [["1 → 输入最低", "1 → worst input"], f(VDD12 - p.noise, 2) + " V"],
                [["判断", "Verdict"], ok ? api.T("在噪声容限之内", "within the noise margins") : api.T("超出噪声容限，可能误判", "beyond the noise margins: may be misread")]);
    }
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mu = css("--muted");
    const blue = "#1d6fb8", amber = "#e67e22", red = "#c0392b", green = css("--green");
    const c = vtc12(p.ratio), nm = c.nm, side = Math.min(w * 0.62, h * 0.82);
    const px = w * 0.08, py = h * 0.06;
    const ax = api.plot(px, py, side, side, [{ pts: c.pts, color: blue }, { pts: [[0, 0], [VDD12, VDD12]], color: css("--grid") }],
      { xmin: 0, xmax: VDD12, ymin: 0, ymax: VDD12, xlabel: "Vin / V", ylabel: "Vout / V" });
    // VIL, VIH, VM
    [[nm.VIL, "VIL"], [nm.VIH, "VIH"]].forEach(([v, n], i) => {
      api.line(ax.X(v), py, ax.X(v), py + side, mu, 1, [4, 4]); api.label(n, ax.X(v) + (i ? 4 : -4), py + side + 12, mu, 11, i ? "left" : "right");
      api.circle(ax.X(v), ax.Y(M1_2.vout(v, W12, p.ratio * W12)), 4, mu);
    });
    api.circle(ax.X(c.vm), ax.Y(c.vm), 4, ink); api.label("VM", ax.X(c.vm) + 8, ax.Y(c.vm) - 2, ink, 12);
    if (api.scene === "vtc") {
      const vo = M1_2.vout(p.vi, W12, p.ratio * W12);
      api.line(ax.X(p.vi), py + side, ax.X(p.vi), ax.Y(vo), amber, 1.5, [2, 3]);
      api.circle(ax.X(p.vi), ax.Y(vo), 6, amber, ink);
    } else {
      // noisy low input [0, noise] and noisy high input [VDD - noise, VDD] on the x axis
      const lowOk = p.noise <= nm.VIL - nm.VOL + 1e-9, highOk = p.noise <= nm.VOH - nm.VIH + 1e-9;
      api.rect(ax.X(0), py + side - 8, ax.X(p.noise) - ax.X(0), 8, lowOk ? amber : red);
      api.rect(ax.X(VDD12 - p.noise), py + side - 8, ax.X(VDD12) - ax.X(VDD12 - p.noise), 8, highOk ? amber : red);
      // what the next stage sees
      const yL = M1_2.vout(p.noise, W12, p.ratio * W12), yH = M1_2.vout(VDD12 - p.noise, W12, p.ratio * W12);
      api.circle(ax.X(p.noise), ax.Y(yL), 5, lowOk ? amber : red); api.circle(ax.X(VDD12 - p.noise), ax.Y(yH), 5, highOk ? amber : red);
    }
    // right: the margin bars
    const bx = px + side + w * 0.07, bw = Math.max(40, w - bx - 20), by = py + 10, bh = side - 20, Y = (v) => by + bh - v / VDD12 * bh;
    api.label(api.T("电平与噪声容限", "Levels and margins"), bx, by - 2, ink, 12);
    const col = (x0, top, bot, color, text) => { api.rect(x0, Y(top), bw * 0.4, Y(bot) - Y(top), color); api.label(text, x0 + bw * 0.2, (Y(top) + Y(bot)) / 2, "#fff", 11, "center"); };
    col(bx, nm.VOH, nm.VIH, green, "NMH"); col(bx, nm.VIL, nm.VOL, green, "NML");
    [[nm.VOH, "VOH"], [nm.VIH, "VIH"], [nm.VIL, "VIL"], [nm.VOL, "VOL"]].forEach(([v, n]) => api.label(n + " " + api.fmt(v, 2), bx + bw * 0.45, Y(v), mu, 11));
    if (api.scene === "enc") {
      api.line(bx - 6, Y(p.noise), bx + bw * 0.4 + 6, Y(p.noise), amber, 2);
      api.line(bx - 6, Y(VDD12 - p.noise), bx + bw * 0.4 + 6, Y(VDD12 - p.noise), amber, 2);
    }
  },
});

function check12(api) {
  const p = api.p, c = vtc12(p.ratio), nm = c.nm;
  if (api.scene === "vtc") {
    if (Math.abs(c.vm - VDD12 / 2) < 0.01) api.done("vm");
    if (Math.abs(p.ratio - 1) < 1e-9 && Math.abs(p.vi - nm.VIL) <= 0.015) api.done("vil");
    return;
  }
  const m = Math.min(nm.NML, nm.NMH);
  if (Math.abs(p.ratio - R12) < 0.1 && p.noise <= m + 1e-9 && p.noise >= m - 0.05) api.done("noise");
}
