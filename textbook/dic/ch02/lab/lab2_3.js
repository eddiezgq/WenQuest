// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/lab2_3.body.js、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M2_3 = (function () {
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
        return out;
      };
      return m;
    }
    return { create };
  });
  return self.WQMos.create({"_note":"SKY130 tt 27 °C 校准值（第 17 轮附 3.4，samples/数字集成电路设计/生成脚本/calib/calib.py）：VT 为使传输特性最接近仿真的有效值（线性区外推值见 calib/result.json），k′ 由 IDSAT 反推，Cg、Cd 由输入电容与扇出拟合后按 FO4 延时修正","VDD":1.8,"VTn":0.55,"VTp":0.55,"kn":0.0000845,"kp":0.0000348,"L":0.15,"Wmin":0.42,"Cg":1.25e-15,"Cd":1.97e-15,"problems":{"p11":{"Iload":0.001,"VOLmax":0.2},"p12":{"noise":0.3},"p14":{"CL":1e-11,"tmax":3.5e-10},"p15":{"N":10000,"alpha":0.1,"Cgate":5e-15,"f":100000000,"Vlow":1.2,"fo4max":1e-10},"p23":{"n_addr":3,"Cin_units":2,"Cout_units":32,"branch":4},"p41":{"L_um":3000},"p42":{"layer":"met2","w_um":0.14,"trunk_um":1000,"near_um":400,"far_um":1600,"leaf_load_units":20,"driver_size":20},"p43":{"L_um":3000,"layer":"met1","w_um":0.14,"load_units":20},"p44":{"layer":"met2","w_um":0.14,"len_um":500,"victim_size":1,"tr_ps":100}},"wires":{"_note":"SKY130 导线参数（典型值），由 samples/数字集成电路设计/生成脚本/calib/wires.py 从 open_pdks 的 sky130A.tech 读出：Rsq Ω/□；Carea aF/μm²（对衬底）；Cfringe aF/μm（每条边，对衬底）；同层耦合每微米 Kside/(s+s0) aF；z、t 层底高度与厚度 μm；wmin、smin 最小线宽、间距 μm；via 每个通孔 Ω","layers":{"li1":{"Rsq":12.8,"Carea":36.99,"Cfringe":40.7,"Kside":25.5,"s0":0.14,"z":0.9361,"t":0.1,"wmin":0.17,"smin":0.17},"met1":{"Rsq":0.125,"Carea":25.78,"Cfringe":40.57,"Kside":44,"s0":0.25,"z":1.3761,"t":0.36,"wmin":0.14,"smin":0.14},"met2":{"Rsq":0.125,"Carea":17.5,"Cfringe":37.76,"Kside":50,"s0":0.3,"z":2.0061,"t":0.36,"wmin":0.14,"smin":0.14},"met3":{"Rsq":0.047,"Carea":12.37,"Cfringe":40.99,"Kside":74,"s0":0.4,"z":2.7861,"t":0.845,"wmin":0.3,"smin":0.3},"met4":{"Rsq":0.047,"Carea":8.42,"Cfringe":36.68,"Kside":94,"s0":0.57,"z":4.0211,"t":0.845,"wmin":0.3,"smin":0.3},"met5":{"Rsq":0.029,"Carea":6.32,"Cfringe":38.85,"Kside":155,"s0":0.5,"z":5.3711,"t":1.26,"wmin":1.6,"smin":1.6}},"via":{"li1-met1":9.3,"met1-met2":4.5,"met2-met3":3.41,"met3-met4":3.41,"met4-met5":0.38}},"gates_sim":{"_note":"SKY130 门参数仿真值（samples/数字集成电路设计/生成脚本/calib/calib_gates.py）：g、p 以同一仿真里参考反相器的 τ 为单位；A 为靠近输出的输入，B 为靠近电源轨的输入；pseudo_nmos 为 PMOS 负载取最小宽度时的输出低电平与静态电流；pass 为 10 fF 负载充电 10 ns 后的输出高电平","p_inv":1.559,"gates":{"nand2_A":{"g":1.176,"p":1.944},"nand2_B":{"g":1.166,"p":2.546},"nand3_A":{"g":1.387,"p":2.282},"nand3_B":{"g":1.391,"p":3.963},"nor2_A":{"g":1.68,"p":2.313},"nor2_B":{"g":1.643,"p":3.85},"nor3_A":{"g":2.363,"p":2.726},"nor3_B":{"g":2.342,"p":6.831}},"pseudo_nmos":[{"wn_over_wp":1,"VOL":0.1832,"I":0.0000825},{"wn_over_wp":2,"VOL":0.0788,"I":0.000084},{"wn_over_wp":4,"VOL":0.0332,"I":0.0000847}],"pass":{"nmos":1.089,"tgate":1.8}}});
})();
// 实验 2.3 逻辑努力：寄存器地址译码器（配 2.3 节）。三个场景是三种结构：2 级（三输入与非 + 反相器）、
// 3 级（反相器 + 三输入与非 + 反相器）、4 级（两个反相器 + 三输入与非 + 反相器）。电容以参考反相器的输入电容 Cinv 为 1，
// 延时以 τ 为单位：每级 d = g·b·C(下一级)/C(本级) + p。第一级的输入电容由地址线的驱动能力定死，学生调后面各级的输入电容。
// 右侧同时给出各结构在最优尺寸下的手算延时，以及换用 SKY130 仿真 g、p 的延时。
const Q23 = M2_3.P.problems.p23, SIM23 = M2_3.P.gates_sim;
const GN23 = M2_3.leG("nand", Q23.n_addr), PN23 = M2_3.leP("nand", Q23.n_addr), PI23 = M2_3.leP("inv", 1);
const TAU23 = M2_3.tau() * 1e12, H23 = Q23.Cout_units / Q23.Cin_units, B23 = Q23.branch;
const ST23 = {   // 每级：[名称, g, p, 本级输出的分支数, 是否为与非门]
  s2: [["NAND3", GN23, PN23, 1, 1], ["INV", 1, PI23, 1, 0]],
  s3: [["INV", 1, PI23, B23, 0], ["NAND3", GN23, PN23, 1, 1], ["INV", 1, PI23, 1, 0]],
  s4: [["INV", 1, PI23, 1, 0], ["INV", 1, PI23, B23, 0], ["NAND3", GN23, PN23, 1, 1], ["INV", 1, PI23, 1, 0]],
};
const PIDS23 = ["c2", "c3", "c4"];
function path23(scene, p, sim) {
  const st = ST23[scene], caps = [scene === "s2" ? Q23.Cin_units / B23 : Q23.Cin_units];
  for (let i = 1; i < st.length; i++) caps.push(p[PIDS23[i - 1]]);
  caps.push(Q23.Cout_units);
  const gs = st.map((s) => (sim && s[4] ? SIM23.gates["nand" + Q23.n_addr + "_A"].g : s[1]));
  const ps = st.map((s) => (sim ? (s[4] ? SIM23.gates["nand" + Q23.n_addr + "_A"].p : SIM23.p_inv) : s[2]));
  const f = st.map((s, i) => gs[i] * s[3] * caps[i + 1] / caps[i]);
  const D = f.reduce((a, b) => a + b, 0) + ps.reduce((a, b) => a + b, 0);
  return { caps, f, D, P: ps.reduce((a, b) => a + b, 0) };
}
function opt23(scene, sim) {
  const st = ST23[scene];
  const gs = st.map((s) => (sim && s[4] ? SIM23.gates["nand" + Q23.n_addr + "_A"].g : s[1]));
  const ps = st.map((s) => (sim ? (s[4] ? SIM23.gates["nand" + Q23.n_addr + "_A"].p : SIM23.p_inv) : s[2]));
  return M2_3.pathDelay(gs, ps, B23, H23).D;
}

WQ.lab({
  title: ["实验 2.3 逻辑努力：地址译码器", "Lab 2.3 Logical effort: an address decoder"],
  goal: ["用逻辑努力给寄存器地址译码器选级数、定尺寸：读出每级的努力和总延时，找到最快的结构，把各级尺寸调到最优。",
         "Use logical effort to choose the number of stages and the sizes of a register address decoder: read each stage effort and the total delay, find the fastest structure and size it optimally."],
  scenes: [
    { id: "s2", robot: true, name: ["2 级：与非 + 反相器", "2 stages: NAND + INV"], hide: ["c3", "c4"], params: { c2: { min: 0.5, max: 20, step: 0.05, value: 8 } },
      problem: { title: ["机器人问题：8 个控制寄存器的地址译码", "Robot problem: decoding 8 control registers"],
                 text: ["每个地址位最多呈现 2 Cinv，每条输出驱动约 32 Cinv，每个地址位接 4 个与非门。先算路径努力 F，再调反相器的尺寸。",
                        "Each address bit may present at most 2 Cinv, each output drives about 32 Cinv, and each address bit feeds 4 NAND gates. Work out the path effort F, then size the inverter."] } },
    { id: "s3", robot: true, name: ["3 级：反相器 + 与非 + 反相器", "3 stages: INV + NAND + INV"], hide: ["c4"],
      params: { c2: { min: 0.5, max: 20, step: 0.05, value: 1 }, c3: { min: 1, max: 32, step: 0.05, value: 16 } },
      problem: { title: ["加一级输入反相器", "Add an input inverter"],
                 text: ["输入反相器产生地址的反码，再送给与非门。路径努力不变，寄生延时多了一个反相器。各级怎样分摊努力最快？",
                        "The input inverter produces the complement of the address bit. The path effort is unchanged but there is one more parasitic delay. How should the effort be shared?"] } },
    { id: "s4", name: ["4 级：两个反相器 + 与非 + 反相器", "4 stages: 2 INV + NAND + INV"], hide: [],
      params: { c2: { min: 0.5, max: 20, step: 0.05, value: 4 }, c3: { min: 0.5, max: 20, step: 0.05, value: 4 }, c4: { min: 1, max: 32, step: 0.05, value: 16 } },
      problem: { title: ["再多一级呢", "And one more stage?"],
                 text: ["4 级时每级努力更小，但寄生延时又多一份。它比 3 级快还是慢？",
                        "With 4 stages each effort is smaller, but there is one more parasitic delay. Is it faster or slower than 3 stages?"] } },
  ],
  params: [
    { id: "c2", name: ["第 2 级输入电容 / Cinv", "Stage 2 input capacitance / Cinv"], min: 0.5, max: 20, step: 0.05, value: 8, unit: "", digits: 2 },
    { id: "c3", name: ["第 3 级输入电容 / Cinv", "Stage 3 input capacitance / Cinv"], min: 0.5, max: 32, step: 0.05, value: 16, unit: "", digits: 2 },
    { id: "c4", name: ["第 4 级输入电容 / Cinv", "Stage 4 input capacitance / Cinv"], min: 1, max: 32, step: 0.05, value: 16, unit: "", digits: 2 },
  ],
  tasks: [
    { id: "two", robot: true, text: ["2 级结构：调反相器尺寸，使总延时不超过这种结构最小延时的 1.01 倍。", "2 stages: size the inverter so the delay is within 1 % of this structure's minimum."],
      demo: { scene: "s2", set: { c2: 3.2 }, press: [], wait: 1 } },
    { id: "three", robot: true, text: ["3 级结构：调两级的尺寸，使总延时不超过最小延时的 1.01 倍。这时三级的努力有什么关系？", "3 stages: size both stages to within 1 % of the minimum delay. How do the three stage efforts compare?"],
      demo: { scene: "s3", set: { c2: 2.35, c3: 6.85 }, press: [], wait: 1 } },
    { id: "four", text: ["4 级结构也调到最优（1 % 以内），和 3 级比较，说明哪种最快、为什么。", "Size the 4-stage structure to within 1 % too, compare with 3 stages, and explain which is fastest."],
      demo: { scene: "s4", set: { c2: 6.35, c3: 5.05, c4: 10.1 }, press: [], wait: 1 } },
  ],
  think: ["换用仿真的 g、p 后，三种结构的延时都变小了，最快的结构变了吗？如果输出还要驱动 300 μm 的连线，H 怎样变，结论会变吗？",
          "With the simulated g and p all three structures get faster; does the fastest one change? If the output also drives a 300 μm wire, how does H change, and does the conclusion?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["每级努力 f", "stage effort f"], color: "#1d6fb8" }, { name: ["最优 F^(1/N)", "optimum F^(1/N)"], color: "#2e7d32" }],
  reset(api, s) { check23(api); },
  readouts(api, s) {
    const f = api.fmt, r = path23(api.scene, api.p, false), N = ST23[api.scene].length, F = GN23 * B23 * H23;
    return [[["路径努力 F = G·B·H", "Path effort F = G·B·H"], f(F, 1)],
            [["每级努力", "Stage efforts"], r.f.map((x) => f(x, 2)).join(" / ")],
            [["最优每级努力 F^(1/N)", "Optimal stage effort"], f(Math.pow(F, 1 / N), 2)],
            [["总延时（手算）", "Total delay (hand model)"], f(r.D, 2) + " τ ≈ " + f(r.D * TAU23, 0) + " ps"],
            [["本结构最小延时", "Minimum for this structure"], f(opt23(api.scene, false), 2) + " τ"],
            [["本尺寸换用仿真 g、p", "These sizes with SPICE g, p"], f(path23(api.scene, api.p, true).D, 2) + " τ"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mu = css("--muted"), blue = "#1d6fb8", green = "#2e7d32", amber = "#e67e22";
    const st = ST23[api.scene], r = path23(api.scene, api.p, false), N = st.length, F = GN23 * B23 * H23, fopt = Math.pow(F, 1 / N);
    // top: the chain, gate size ∝ sqrt(input capacitance)
    const y = h * 0.2, x0 = w * 0.06, x1 = w * 0.86, dx = (x1 - x0) / N;
    api.line(x0 - 16, y, x0, y, ink, 2); api.label(api.T("地址", "addr"), x0 - 18, y - 14, mu, 11);
    st.forEach((g, i) => {
      const c = r.caps[i], sz = Math.max(8, Math.min(dx * 0.35, 9 * Math.sqrt(c))), cx = x0 + dx * (i + 0.5);
      if (g[4]) { api.rect(cx - sz * 0.6, y - sz, sz * 1.0, sz * 2, null, blue); api.circle(cx + sz * 0.5, y, 4, null, blue); api.label("&", cx - sz * 0.1, y, blue, 12, "center"); }
      else { api.line(cx - sz * 0.6, y - sz, cx - sz * 0.6, y + sz, blue, 2); api.line(cx - sz * 0.6, y - sz, cx + sz * 0.4, y, blue, 2); api.line(cx - sz * 0.6, y + sz, cx + sz * 0.4, y, blue, 2); api.circle(cx + sz * 0.5, y, 4, null, blue); }
      api.line(x0 + dx * i, y, cx - sz * 0.6, y, ink, 2); api.line(cx + sz * 0.5 + 4, y, x0 + dx * (i + 1), y, ink, 2);
      api.label(api.fmt(c, 2), cx, y + sz + 14, mu, 11, "center");
      if (g[3] > 1) api.label("×" + g[3], x0 + dx * (i + 1) - 8, y - 12, amber, 11, "center");
    });
    api.rect(x1 + 6, y - 14, 10, 28, amber); api.label(Q23.Cout_units + " Cinv", x1 + 20, y, amber, 11);
    // bottom: stage efforts against the optimum
    const by = h * 0.45, bh = h * 0.42, fmax = Math.max(12, ...r.f) * 1.1, Y = (v) => by + bh - v / fmax * bh;
    api.line(x0, Y(fopt), x1, Y(fopt), green, 1.5, [5, 4]); api.label("F^(1/N) = " + api.fmt(fopt, 2), x1, Y(fopt) - 10, green, 11, "right");
    r.f.forEach((v, i) => {
      const cx = x0 + dx * (i + 0.5);
      api.rect(cx - dx * 0.18, Y(v), dx * 0.36, by + bh - Y(v), blue);
      api.label(api.fmt(v, 2), cx, Y(v) - 10, ink, 11, "center");
      api.label(st[i][0], cx, by + bh + 12, mu, 11, "center");
    });
  },
});

function check23(api) {
  const r = path23(api.scene, api.p, false), ok = r.D <= 1.01 * opt23(api.scene, false);
  if (!ok) return;
  if (api.scene === "s2") api.done("two");
  if (api.scene === "s3") api.done("three");
  if (api.scene === "s4") api.done("four");
}
