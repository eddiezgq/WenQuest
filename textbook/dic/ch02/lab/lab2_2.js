// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/lab2_2.body.js、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M2_2 = (function () {
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
// 实验 2.2 门的尺寸（配 2.2 节）。三个场景：n 输入与非门、n 输入或非门、关节使能的与或非门 EN = ¬(A + B·C)。
// 宽度以最小宽度 Wmin 为单位；电阻以参考反相器（Wn = Wmin、Wp = r·Wmin）的下拉、上拉电阻为 1；
// 输入电容以参考反相器的输入电容 Cinv 为 1（= 逻辑努力）。左图按宽度画出每个管子，右图是最坏情况的上拉、下拉电阻。
const R22 = M2_2.P.kn / M2_2.P.kp;
function gate22(scene, p) {
  if (scene === "nand") return { down: p.n / p.wn, up: R22 / p.wp, cin: [(p.wn + p.wp) / (1 + R22)], area: p.n * (p.wn + p.wp) / (1 + R22) };
  if (scene === "nor") return { down: 1 / p.wn, up: p.n * R22 / p.wp, cin: [(p.wn + p.wp) / (1 + R22)], area: p.n * (p.wn + p.wp) / (1 + R22) };
  // 与或非门：下拉 A 单独一路（宽 wna），B、C 串联（各 wn）；上拉 A 与 (B‖C) 串联（各 wp）
  return { down: Math.max(1 / p.wna, 2 / p.wn), up: 2 * R22 / p.wp, cin: [(p.wna + p.wp) / (1 + R22), (p.wn + p.wp) / (1 + R22)],
           area: (p.wna + 2 * p.wn + 3 * p.wp) / (1 + R22) };
}
const ok22 = (g) => Math.abs(g.down - 1) <= 0.05 && Math.abs(g.up - 1) <= 0.05;

WQ.lab({
  title: ["实验 2.2 门的尺寸", "Lab 2.2 Sizing gates"],
  goal: ["调门里 NMOS、PMOS 的宽度，看最坏情况的上拉、下拉电阻和每个输入的电容；按等效反相器定尺寸，比较与非门和或非门。",
         "Change the NMOS and PMOS widths of a gate and watch the worst-case pull-up and pull-down resistance and the input capacitance; size gates as equivalent inverters and compare NAND with NOR."],
  scenes: [
    { id: "nand", name: ["n 输入与非门", "n-input NAND"], hide: ["wna"],
      problem: { title: ["NMOS 串联、PMOS 并联", "Series NMOS, parallel PMOS"],
                 text: ["最坏情况下，下拉要经过全部 n 个串联的 NMOS，上拉只有一个 PMOS 导通。每个管子要多宽，才和参考反相器一样强？",
                        "In the worst case the pull-down goes through all n series NMOS and only one PMOS pulls up. How wide must each transistor be to match the reference inverter?"] } },
    { id: "nor", name: ["n 输入或非门", "n-input NOR"], hide: ["wna"],
      problem: { title: ["NMOS 并联、PMOS 串联", "Parallel NMOS, series PMOS"],
                 text: ["这回串联的是本来就弱的 PMOS。按等效反相器定尺寸后，每个输入的电容是多少？和同样输入数的与非门比一比。",
                        "Now the series devices are the weaker PMOS. After equivalent-inverter sizing, what is the input capacitance? Compare with a NAND of the same fan-in."] } },
    { id: "aoi", robot: true, name: ["关节使能门 EN = ¬(A + B·C)", "Joint enable gate EN = ¬(A + B·C)"], hide: ["n"],
      problem: { title: ["机器人问题：使能门的最坏情况", "Robot problem: the enable gate's worst case"],
                 text: ["A = 急停，B = 限位，C = 方向。下拉：A 单独一路，B、C 串联；上拉：A 与“B、C 并联”串联。让最坏情况的上拉、下拉都和参考反相器一样强，又不浪费面积。",
                        "A = e-stop, B = limit, C = direction. Pull-down: A alone, B and C in series; pull-up: A in series with B‖C. Make the worst-case pull-up and pull-down as strong as the reference inverter without wasting area."] } },
  ],
  params: [
    { id: "n", name: ["输入数 n", "Inputs n"], min: 2, max: 4, step: 1, value: 2, unit: "", digits: 0 },
    { id: "wn", name: ["NMOS 宽度（与或非门为 B、C）/ Wmin", "NMOS width (B, C for the AOI) / Wmin"], min: 1, max: 6, step: 0.25, value: 1, unit: "", digits: 2 },
    { id: "wna", name: ["与或非门 A 的 NMOS 宽度 / Wmin", "AOI: NMOS width of A / Wmin"], min: 1, max: 6, step: 0.25, value: 2, unit: "", digits: 2 },
    { id: "wp", name: ["PMOS 宽度 / Wmin", "PMOS width / Wmin"], min: 1, max: 12, step: 0.05, value: 2, unit: "", digits: 2 },
  ],
  tasks: [
    { id: "nand3", text: ["三输入与非门：调到等效反相器尺寸（最坏上拉、下拉电阻都与参考反相器相差不到 5 %）。", "NAND3: reach equivalent-inverter sizing (worst-case pull-up and pull-down within 5 % of the reference)."],
      demo: { scene: "nand", set: { n: 3, wn: 3, wp: 2.45 }, press: [], wait: 1 } },
    { id: "nor3", text: ["三输入或非门：同样调到等效反相器尺寸，读出每个输入的电容，与三输入与非门比较。", "NOR3: the same sizing; read the input capacitance and compare with the NAND3."],
      demo: { scene: "nor", set: { n: 3, wn: 1, wp: 7.3 }, press: [], wait: 1 } },
    { id: "aoi", robot: true, text: ["使能门：最坏上拉、下拉都与参考反相器相差不到 5 %，且 A 的 NMOS 不超过 1.25 Wmin（不浪费面积）。", "Enable gate: worst-case pull-up and pull-down within 5 % of the reference, with A's NMOS at most 1.25 Wmin."],
      demo: { scene: "aoi", set: { wna: 1, wn: 2, wp: 4.85 }, press: [], wait: 1 } },
  ],
  think: ["为什么并联的管子不能指望“几个一起导通”来降低电阻？如果把最晚到达的信号接到靠近输出的输入上，会快多少——这个实验的模型能回答吗？",
          "Why can't parallel transistors count on conducting together? How much faster is it to connect the latest signal to the input nearest the output — can this lab's model tell?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["NMOS（下拉）", "NMOS (pull-down)"], color: "#1d6fb8" }, { name: ["PMOS（上拉）", "PMOS (pull-up)"], color: "#c0392b" }],
  reset(api, s) { check22(api); },
  readouts(api, s) {
    const f = api.fmt, g = gate22(api.scene, api.p);
    const rows = [[["最坏下拉电阻 / 参考", "Worst pull-down / reference"], f(g.down, 2)],
                  [["最坏上拉电阻 / 参考", "Worst pull-up / reference"], f(g.up, 2)]];
    if (api.scene === "aoi") rows.push([["输入电容 A、B / Cinv", "Input cap A, B / Cinv"], f(g.cin[0], 2) + " / " + f(g.cin[1], 2)]);
    else rows.push([["每个输入的电容 / Cinv", "Input cap per input / Cinv"], f(g.cin[0], 2)]);
    rows.push([["总栅宽 / 参考反相器", "Total width / reference inverter"], f(g.area, 2)], [["r = k′n/k′p", "r = k′n/k′p"], f(R22, 2)]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mu = css("--muted");
    const blue = "#1d6fb8", red = "#c0392b", green = css("--green");
    const g = gate22(api.scene, p);
    // left: transistors as rectangles, width ∝ W
    const x0 = w * 0.06, x1 = w * 0.52, top = h * 0.1, mid = h * 0.5, bot = h * 0.9, unit = Math.min(10, (x1 - x0) / 30);
    api.line(x0, top, x1, top, mu, 2); api.label("VDD", x0, top - 10, mu, 11);
    api.line(x0, bot, x1, bot, mu, 2); api.label("GND", x0, bot + 12, mu, 11);
    api.line(x0, mid, x1 + 20, mid, ink, 2); api.label(api.T("输出", "out"), x1 + 24, mid, ink, 12);
    const box = (cx, y0, y1, wi, col, name) => {
      const ww = Math.max(4, wi * unit);
      api.rect(cx - ww / 2, y0 + 4, ww, y1 - y0 - 8, col);
      api.line(cx, y0, cx, y0 + 4, col, 2); api.line(cx, y1 - 4, cx, y1, col, 2);
      api.label(name, cx, (y0 + y1) / 2, "#fff", 11, "center");
    };
    const series = (cx, y0, y1, k, wi, col, names) => { const dy = (y1 - y0) / k; for (let i = 0; i < k; i++) box(cx, y0 + i * dy, y0 + (i + 1) * dy, wi, col, names[i]); };
    const parallel = (y0, y1, k, wi, col, names) => { for (let i = 0; i < k; i++) { const cx = x0 + (x1 - x0) * (i + 0.5) / k; box(cx, y0, y1, wi, col, names[i]); } };
    const names = ["A", "B", "C", "D"].slice(0, api.scene === "aoi" ? 3 : p.n);
    const cx = (x0 + x1) / 2;
    if (api.scene === "nand") { parallel(top, mid, p.n, p.wp, red, names); series(cx, mid, bot, p.n, p.wn, blue, names); }
    else if (api.scene === "nor") { series(cx, top, mid, p.n, p.wp, red, names); parallel(mid, bot, p.n, p.wn, blue, names); }
    else {
      const ym = (top + mid) / 2;
      box(cx, top, ym, p.wp, red, "A");
      box(x0 + (x1 - x0) * 0.3, ym, mid, p.wp, red, "B"); box(x0 + (x1 - x0) * 0.7, ym, mid, p.wp, red, "C");
      api.line(x0 + (x1 - x0) * 0.3, ym, x0 + (x1 - x0) * 0.7, ym, red, 2);
      box(x0 + (x1 - x0) * 0.3, mid, bot, p.wna, blue, "A");
      series(x0 + (x1 - x0) * 0.7, mid, bot, 2, p.wn, blue, ["B", "C"]);
    }
    // right: worst-case resistances relative to the reference
    const bx = w * 0.66, bw = w * 0.3, by = h * 0.12, bh = h * 0.7, ymax = 3;
    const Y = (v) => by + bh - Math.min(v, ymax) / ymax * bh;
    api.line(bx, Y(1), bx + bw, Y(1), green, 1.5, [5, 4]); api.label(api.T("参考反相器 = 1", "reference = 1"), bx + bw, Y(1) - 26, green, 11, "right");
    [[g.down, blue, api.T("下拉", "down")], [g.up, red, api.T("上拉", "up")]].forEach(([v, col, name], i) => {
      const x = bx + bw * (0.18 + 0.44 * i);
      api.rect(x, Y(v), bw * 0.24, by + bh - Y(v), col);
      api.label(api.fmt(v, 2), x + bw * 0.12, Y(v) - 10, ink, 12, "center");
      api.label(name, x + bw * 0.12, by + bh + 14, mu, 12, "center");
    });
    api.label(api.T("最坏情况电阻 / 参考", "worst-case R / reference"), bx, by - 12, ink, 12);
  },
});

function check22(api) {
  const p = api.p, g = gate22(api.scene, p);
  if (!ok22(g)) return;
  if (api.scene === "nand" && p.n === 3) api.done("nand3");
  if (api.scene === "nor" && p.n === 3) api.done("nor3");
  if (api.scene === "aoi" && p.wna <= 1.25 + 1e-9) api.done("aoi");
}
