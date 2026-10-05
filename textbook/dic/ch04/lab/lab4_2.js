// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/lab4_2.body.js、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M4_2 = (function () {
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
// 实验 4.2 RC 线（配 4.2 节）。一个反相器（尺寸可调）经一条导线驱动末端负载（20 个参考反相器的输入电容）。
// 读数给出式 (4.2.4) 的两部分：驱动项 0.69·Rd·(Cself + Cw + CL) 与导线项 0.38·Rw·Cw + 0.69·Rw·CL；
// 图中是把导线切成 40 段、用后向欧拉法解出的始端与末端波形，竖线是数值解的末端 50 % 时刻。
const P42 = M4_2.P, Q42 = P42.problems.p42;
const R0_42 = (M4_2.reqN(P42.Wmin) + M4_2.reqP(P42.kn / P42.kp * P42.Wmin)) / 2, C0_42 = M4_2.cin(P42.Wmin, P42.kn / P42.kp * P42.Wmin);
const CL42 = Q42.leaf_load_units * C0_42, G42 = P42.Cd / P42.Cg;
const LAY42 = { m1: ["met1", 0.14], m3: ["met3", 0.3] };
const seen42 = { a: false, b: false };
function line42(scene, p) {
  const [lay, w] = LAY42[scene];
  const Rd = R0_42 / p.size, Cs = G42 * C0_42 * p.size, Rw = M4_2.wireR(lay, w) * p.L, Cw = M4_2.wireC(lay, w) * p.L;
  const drv = 0.69 * Rd * (Cs + Cw + CL42), wire = 0.38 * Rw * Cw + 0.69 * Rw * CL42;
  return { Rd, Cs, Rw, Cw, drv, wire, total: drv + wire };
}
function sim42(x) {   // 40 段梯形网络的阶跃响应（三对角方程组，后向欧拉）
  const n = 40, N = n + 1, C = new Array(N).fill(x.Cw / n), r = x.Rw / n;
  C[0] = x.Cs + x.Cw / (2 * n); C[n] = x.Cw / (2 * n) + CL42;
  const T = 3 * x.total, steps = 600, dt = T / steps, VDD = P42.VDD;
  let v = new Array(N).fill(0); const t = [0], v0 = [0], vn = [0];
  const a = new Array(N), b = new Array(N), c = new Array(N);
  for (let i = 0; i < N; i++) {
    const gl = i === 0 ? 1 / x.Rd : 1 / r, gr = i === n ? 0 : 1 / r;
    a[i] = i === 0 ? 0 : -1 / r; c[i] = i === n ? 0 : -1 / r; b[i] = C[i] / dt + gl + gr;
  }
  for (let s = 1; s <= steps; s++) {
    const d = v.map((vi, i) => C[i] / dt * vi + (i === 0 ? VDD / x.Rd : 0));
    const cp = new Array(N), dp = new Array(N);
    cp[0] = c[0] / b[0]; dp[0] = d[0] / b[0];
    for (let i = 1; i < N; i++) { const m = b[i] - a[i] * cp[i - 1]; cp[i] = c[i] / m; dp[i] = (d[i] - a[i] * dp[i - 1]) / m; }
    v[n] = dp[n]; for (let i = n - 1; i >= 0; i--) v[i] = dp[i] - cp[i] * v[i + 1];
    t.push(s * dt); v0.push(v[0]); vn.push(v[n]);
  }
  let t50 = null; for (let i = 1; i < vn.length; i++) if (vn[i] >= VDD / 2) { t50 = t[i - 1] + (t[i] - t[i - 1]) * (VDD / 2 - vn[i - 1]) / (vn[i] - vn[i - 1]); break; }
  return { t, v0, vn, t50 };
}

WQ.lab({
  title: ["实验 4.2 RC 线", "Lab 4.2 RC wires"],
  goal: ["看一个反相器经长导线驱动负载时，延时怎样随线长、金属层和驱动强弱变化；比较式 (4.2.4) 的估算与分段数值解。",
         "See how the delay of an inverter driving a load through a long wire depends on wire length, metal layer and driver strength; compare Eq. (4.2.4) with a segmented numerical solution."],
  scenes: [
    { id: "m1", robot: true, name: ["met1 最小线宽", "met1, minimum width"], hide: [], params: { L: { value: 1000 } },
      problem: { title: ["机器人问题：时钟线走哪一层", "Robot problem: which layer for the clock"],
                 text: ["时钟缓冲器经一条 met1 线把时钟送到计数器（20 Cinv）。线有多长时，导线本身的延时开始超过驱动器的延时？",
                        "The clock buffer drives a counter (20 Cinv) through a met1 wire. At what length does the wire's own delay overtake the driver's?"] } },
    { id: "m3", name: ["met3 最小线宽", "met3, minimum width"], hide: [],
      problem: { title: ["换到厚金属", "Move to a thick metal"],
                 text: ["met3 的方块电阻只有 met1 的约三分之一，最小线宽又宽一倍。同样的驱动，能走多长？",
                        "met3 has about a third of met1's sheet resistance and twice the minimum width. How far can the same driver go?"] } },
  ],
  params: [
    { id: "L", name: ["线长", "Wire length"], min: 100, max: 6000, step: 100, value: 500, unit: "μm", digits: 0 },
    { id: "size", name: ["驱动器尺寸（参考反相器的倍数）", "Driver size (× reference inverter)"], min: 1, max: 60, step: 1, value: 20, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "square", robot: true, text: ["met1，驱动器 40 倍：把线长分别设为 1000 μm 和 2000 μm，比较导线项——线长加倍，它变成几倍？", "met1, 40× driver: set the length to 1000 μm and then 2000 μm and compare the wire term. Doubling the length multiplies it by what?"],
      demo: { scene: "m1", set: { size: 40, L: 2000 }, press: [], wait: 1 } },
    { id: "equal", robot: true, text: ["met1，驱动器 20 倍：找到导线项与驱动项相差不到 10 % 的线长。", "met1, 20× driver: find the length where the wire term and the driver term agree within 10 %."],
      demo: { scene: "m1", set: { size: 20, L: 900 }, press: [], wait: 1 } },
    { id: "far", text: ["met3，驱动器 20 倍：找到总延时（估算）不超过 100 ps 的最长线长（再长 100 μm 就超过）。", "met3, 20× driver: find the longest wire whose estimated delay stays within 100 ps (100 μm more exceeds it)."],
      demo: { scene: "m3", set: { size: 20, L: 2100 }, press: [], wait: 1 } },
  ],
  think: ["驱动器加大能减小哪一项，不能减小哪一项？线很长时，为什么只加大驱动器不够？",
          "Which term does a stronger driver reduce, and which not? For a very long wire, why is a stronger driver alone not enough?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["始端", "near end"], color: "#e67e22" }, { name: ["末端", "far end"], color: "#1d6fb8" }],
  reset(api, s) { check42(api); },
  readouts(api, s) {
    const f = api.fmt, x = line42(api.scene, api.p), sm = sim42(x);
    return [[["导线电阻 Rw / 电容 Cw", "Wire Rw / Cw"], f(x.Rw, 0) + " Ω / " + f(x.Cw * 1e15, 1) + " fF"],
            [["驱动项 0.69Rd(Cself+Cw+CL)", "Driver term"], f(x.drv * 1e12, 1) + " ps"],
            [["导线项 0.38RwCw + 0.69RwCL", "Wire term"], f(x.wire * 1e12, 1) + " ps"],
            [["估算总延时", "Estimated delay"], f(x.total * 1e12, 1) + " ps"],
            [["数值解（40 段）", "Numerical (40 sections)"], sm.t50 == null ? "—" : f(sm.t50 * 1e12, 1) + " ps"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mu = css("--muted"), blue = "#1d6fb8", amber = "#e67e22";
    const x = line42(api.scene, api.p), sm = sim42(x), T = sm.t[sm.t.length - 1] * 1e12;
    const px = w * 0.08, py = h * 0.08, pw = w * 0.88, ph = h * 0.62;
    const ax = api.plot(px, py, pw, ph, [{ pts: sm.t.map((t, i) => [t * 1e12, sm.v0[i]]), color: amber }, { pts: sm.t.map((t, i) => [t * 1e12, sm.vn[i]]), color: blue }],
      { xmin: 0, xmax: T, ymin: 0, ymax: 1.9, xlabel: "t / ps", ylabel: "V" });
    api.line(px, ax.Y(0.9), px + pw, ax.Y(0.9), mu, 1, [3, 4]);
    if (sm.t50) { api.line(ax.X(sm.t50 * 1e12), py, ax.X(sm.t50 * 1e12), py + ph, ink, 1.2); api.label("t50", ax.X(sm.t50 * 1e12) + 4, py + 12, ink, 11); }
    api.label(api.fmt(T, 0) + " ps", px + pw, py + ph + 24, mu, 11, "right");
    // bottom: the two terms as stacked bar
    const by = py + ph + 40, bw = pw, bh = 16, tot = x.total;
    api.rect(px, by, bw * x.drv / tot, bh, amber); api.rect(px + bw * x.drv / tot, by, bw * x.wire / tot, bh, blue);
    api.label(api.T("驱动项", "driver"), px + 4, by + bh + 12, amber, 11);
    api.label(api.T("导线项", "wire"), px + bw - 4, by + bh + 12, blue, 11, "right");
  },
});

function check42(api) {
  const p = api.p, x = line42(api.scene, p);
  if (api.scene === "m1" && p.size === 40) {
    if (p.L === 1000) seen42.a = true;
    if (p.L === 2000) seen42.b = true;
    if (seen42.a && seen42.b) api.done("square");
  }
  if (api.scene === "m1" && p.size === 20 && Math.abs(x.wire - x.drv) <= 0.1 * x.drv) api.done("equal");
  if (api.scene === "m3" && p.size === 20) {
    const nxt = line42("m3", { L: p.L + 100, size: 20 });
    if (x.total <= 100e-12 && nxt.total > 100e-12) api.done("far");
  }
}
