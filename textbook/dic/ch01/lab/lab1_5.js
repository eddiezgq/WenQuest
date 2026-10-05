// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/lab1_5.body.js、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M1_5 = (function () {
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
  return self.WQMos.create({"_note":"SKY130 tt 27 °C 校准值（第 17 轮附 3.4，samples/数字集成电路设计/生成脚本/calib/calib.py）：VT 为使传输特性最接近仿真的有效值（线性区外推值见 calib/result.json），k′ 由 IDSAT 反推，Cg、Cd 由输入电容与扇出拟合后按 FO4 延时修正","VDD":1.8,"VTn":0.55,"VTp":0.55,"kn":0.0000845,"kp":0.0000348,"L":0.15,"Wmin":0.42,"Cg":1.25e-15,"Cd":1.97e-15,"problems":{"p11":{"Iload":0.001,"VOLmax":0.2},"p12":{"noise":0.3},"p14":{"CL":1e-11,"tmax":3.5e-10},"p15":{"N":10000,"alpha":0.1,"Cgate":5e-15,"f":100000000,"Vlow":1.2,"fo4max":1e-10},"p23":{"n_addr":3,"Cin_units":2,"Cout_units":32,"branch":4},"p41":{"L_um":3000},"p42":{"layer":"met2","w_um":0.14,"trunk_um":1000,"near_um":400,"far_um":1600,"leaf_load_units":20,"driver_size":20},"p43":{"L_um":3000,"layer":"met1","w_um":0.14,"load_units":20},"p44":{"layer":"met2","w_um":0.14,"len_um":500,"victim_size":1,"tr_ps":100}},"wires":{"_note":"SKY130 导线参数（典型值），由 samples/数字集成电路设计/生成脚本/calib/wires.py 从 open_pdks 的 sky130A.tech 读出：Rsq Ω/□；Carea aF/μm²（对衬底）；Cfringe aF/μm（每条边，对衬底）；同层耦合每微米 Kside/(s+s0) aF；z、t 层底高度与厚度 μm；wmin、smin 最小线宽、间距 μm；via 每个通孔 Ω","layers":{"li1":{"Rsq":12.8,"Carea":36.99,"Cfringe":40.7,"Kside":25.5,"s0":0.14,"z":0.9361,"t":0.1,"wmin":0.17,"smin":0.17},"met1":{"Rsq":0.125,"Carea":25.78,"Cfringe":40.57,"Kside":44,"s0":0.25,"z":1.3761,"t":0.36,"wmin":0.14,"smin":0.14},"met2":{"Rsq":0.125,"Carea":17.5,"Cfringe":37.76,"Kside":50,"s0":0.3,"z":2.0061,"t":0.36,"wmin":0.14,"smin":0.14},"met3":{"Rsq":0.047,"Carea":12.37,"Cfringe":40.99,"Kside":74,"s0":0.4,"z":2.7861,"t":0.845,"wmin":0.3,"smin":0.3},"met4":{"Rsq":0.047,"Carea":8.42,"Cfringe":36.68,"Kside":94,"s0":0.57,"z":4.0211,"t":0.845,"wmin":0.3,"smin":0.3},"met5":{"Rsq":0.029,"Carea":6.32,"Cfringe":38.85,"Kside":155,"s0":0.5,"z":5.3711,"t":1.26,"wmin":1.6,"smin":1.6}},"via":{"li1-met1":9.3,"met1-met2":4.5,"met2-met3":3.41,"met3-met4":3.41,"met4-met5":0.38}},"gates_sim":{"_note":"SKY130 门参数仿真值（samples/数字集成电路设计/生成脚本/calib/calib_gates.py）：g、p 以同一仿真里参考反相器的 τ 为单位；A 为靠近输出的输入，B 为靠近电源轨的输入；pseudo_nmos 为 PMOS 负载取最小宽度时的输出低电平与静态电流；pass 为 10 fF 负载充电 10 ns 后的输出高电平","p_inv":1.559,"gates":{"nand2_A":{"g":1.176,"p":1.944},"nand2_B":{"g":1.166,"p":2.546},"nand3_A":{"g":1.387,"p":2.282},"nand3_B":{"g":1.391,"p":3.963},"nor2_A":{"g":1.68,"p":2.313},"nor2_B":{"g":1.643,"p":3.85},"nor3_A":{"g":2.363,"p":2.726},"nor3_B":{"g":2.342,"p":6.831}},"pseudo_nmos":[{"wn_over_wp":1,"VOL":0.1832,"I":0.0000825},{"wn_over_wp":2,"VOL":0.0788,"I":0.000084},{"wn_over_wp":4,"VOL":0.0332,"I":0.0000847}],"pass":{"nmos":1.089,"tgate":1.8}},"ff_sim":{"_note":"SKY130 传输门主从触发器的时序参数（samples/数字集成电路设计/生成脚本/calib/calib_ff.py），以同一仿真中的 FO4 延时为单位：tcq 时钟到输出、tsu 建立时间、th 保持时间、tau_m 亚稳态时间常数、T0 亚稳态窗口","tcq":3.18,"tsu":1.072,"th":-0.943,"tau_m":0.7284,"T0":0.5983}});
})();
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
