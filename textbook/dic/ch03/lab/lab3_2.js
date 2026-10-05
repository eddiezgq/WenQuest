// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/lab3_2.body.js、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M3_2 = (function () {
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
      m.xtalk = (layer, w, s, Lw, size, tr) => {
        const q = WL[layer], Cc = m.wireCc(layer, s) * Lw, Cg = (q.Carea * w + 2 * q.Cfringe) * 1e-18 * Lw + m.cin(Wmin, rr * Wmin);
        const k = Cc / (Cc + Cg), t = m.reqN(size * Wmin) * (Cc + Cg);
        return [Cc, Cg, VDD * k, VDD * k * t / tr * (1 - Math.exp(-tr / t)), t];
      };
      /* ---------- 第 3 章：时序元件（触发器参数来自 params.json 的 ff_sim，以 FO4 为单位） ---------- */
      m.ffTiming = () => {
        const f4 = m.fo4Tp(rr), F = P.ff_sim || {}, o = {};
        for (const k of ['tcq', 'tsu', 'th', 'tau_m', 'T0']) o[k] = F[k] * f4;
        return o;
      };
      m.setupSlack = (T, tl, skew) => { const t = m.ffTiming(); return T + (skew || 0) - (t.tcq + tl + t.tsu); };
      m.holdSlack = (tl, skew) => { const t = m.ffTiming(); return t.tcq + tl - (t.th + (skew || 0)); };
      m.syncTr = (n, fclk, slack) => { const t = m.ffTiming(); return slack + (n - 1) * (1 / fclk - t.tcq - t.tsu); };
      m.mtbf = (tr, fclk, fdata) => { const t = m.ffTiming(); return Math.exp(tr / t.tau_m) / (t.T0 * fclk * fdata); };
      m.ffTcqLe = () => [gam + 3, gam + 2, 2 * (1 + 2 * gam), gam + 5];
      m.incDelay = (bits) => (bits - 1) * ((1 + 2 * gam) + (m.leG('nand', 2) + 4 + gam)) + (1 + 4 * gam);
      m.tauMEst = () => {
        const v = m.vm(Wmin, rr * Wmin), gm = kn * Wmin / L * (v - VTn) + kp * rr * Wmin / L * (VDD - v - VTp);
        return m.cin(Wmin, rr * Wmin) * (1 + gam) / gm;
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
        const q33 = pr.p33, f33 = q33.f_MHz * 1e6, fd = q33.rpm / 60 * q33.lines * 2;
        out.ch3 = { ff: m.ffTiming(), tcq_le: m.ffTcqLe().reduce((a, b) => a + b, 0), tau_m_est: m.tauMEst(),
                    inc16: m.incDelay(16), xtalk: m.xtalk('met2', 0.14, 0.14, 500, 1, 100e-12),
                    setup: m.setupSlack(1 / f33, 1e-9, 50e-12), hold: m.holdSlack(0, 150e-12), mtbf: {} };
        for (const n of [1, 2]) out.ch3.mtbf[n] = m.mtbf(m.syncTr(n, f33, q33.slack_ps * 1e-12), f33, fd);
        return out;
      };
      return m;
    }
    return { create };
  });
  return self.WQMos.create({"_note":"SKY130 tt 27 °C 校准值（第 17 轮附 3.4，samples/数字集成电路设计/生成脚本/calib/calib.py）：VT 为使传输特性最接近仿真的有效值（线性区外推值见 calib/result.json），k′ 由 IDSAT 反推，Cg、Cd 由输入电容与扇出拟合后按 FO4 延时修正","VDD":1.8,"VTn":0.55,"VTp":0.55,"kn":0.0000845,"kp":0.0000348,"L":0.15,"Wmin":0.42,"Cg":1.25e-15,"Cd":1.97e-15,"problems":{"p11":{"Iload":0.001,"VOLmax":0.2},"p12":{"noise":0.3},"p14":{"CL":1e-11,"tmax":3.5e-10},"p15":{"N":10000,"alpha":0.1,"Cgate":5e-15,"f":100000000,"Vlow":1.2,"fo4max":1e-10},"p23":{"n_addr":3,"Cin_units":2,"Cout_units":32,"branch":4},"p41":{"L_um":3000},"p42":{"layer":"met2","w_um":0.14,"trunk_um":1000,"near_um":400,"far_um":1600,"leaf_load_units":20,"driver_size":20},"p43":{"L_um":3000,"layer":"met1","w_um":0.14,"load_units":20},"p44":{"layer":"met2","w_um":0.14,"len_um":500,"victim_size":1,"tr_ps":100},"p31":{"bits":16,"f_MHz":100},"p32":{"bits":16,"f_MHz":100,"pwm_kHz":20,"gate_fo4":2},"p33":{"rpm":6000,"lines":1024,"f_MHz":100,"slack_ps":200,"robots":1000,"years":10},"p34":{"n_ff":2000,"group":16,"idle":0.9,"f_MHz":100}},"wires":{"_note":"SKY130 导线参数（典型值），由 samples/数字集成电路设计/生成脚本/calib/wires.py 从 open_pdks 的 sky130A.tech 读出：Rsq Ω/□；Carea aF/μm²（对衬底）；Cfringe aF/μm（每条边，对衬底）；同层耦合每微米 Kside/(s+s0) aF；z、t 层底高度与厚度 μm；wmin、smin 最小线宽、间距 μm；via 每个通孔 Ω","layers":{"li1":{"Rsq":12.8,"Carea":36.99,"Cfringe":40.7,"Kside":25.5,"s0":0.14,"z":0.9361,"t":0.1,"wmin":0.17,"smin":0.17},"met1":{"Rsq":0.125,"Carea":25.78,"Cfringe":40.57,"Kside":44,"s0":0.25,"z":1.3761,"t":0.36,"wmin":0.14,"smin":0.14},"met2":{"Rsq":0.125,"Carea":17.5,"Cfringe":37.76,"Kside":50,"s0":0.3,"z":2.0061,"t":0.36,"wmin":0.14,"smin":0.14},"met3":{"Rsq":0.047,"Carea":12.37,"Cfringe":40.99,"Kside":74,"s0":0.4,"z":2.7861,"t":0.845,"wmin":0.3,"smin":0.3},"met4":{"Rsq":0.047,"Carea":8.42,"Cfringe":36.68,"Kside":94,"s0":0.57,"z":4.0211,"t":0.845,"wmin":0.3,"smin":0.3},"met5":{"Rsq":0.029,"Carea":6.32,"Cfringe":38.85,"Kside":155,"s0":0.5,"z":5.3711,"t":1.26,"wmin":1.6,"smin":1.6}},"via":{"li1-met1":9.3,"met1-met2":4.5,"met2-met3":3.41,"met3-met4":3.41,"met4-met5":0.38}},"gates_sim":{"_note":"SKY130 门参数仿真值（samples/数字集成电路设计/生成脚本/calib/calib_gates.py）：g、p 以同一仿真里参考反相器的 τ 为单位；A 为靠近输出的输入，B 为靠近电源轨的输入；pseudo_nmos 为 PMOS 负载取最小宽度时的输出低电平与静态电流；pass 为 10 fF 负载充电 10 ns 后的输出高电平","p_inv":1.559,"gates":{"nand2_A":{"g":1.176,"p":1.944},"nand2_B":{"g":1.166,"p":2.546},"nand3_A":{"g":1.387,"p":2.282},"nand3_B":{"g":1.391,"p":3.963},"nor2_A":{"g":1.68,"p":2.313},"nor2_B":{"g":1.643,"p":3.85},"nor3_A":{"g":2.363,"p":2.726},"nor3_B":{"g":2.342,"p":6.831}},"pseudo_nmos":[{"wn_over_wp":1,"VOL":0.1832,"I":0.0000825},{"wn_over_wp":2,"VOL":0.0788,"I":0.000084},{"wn_over_wp":4,"VOL":0.0332,"I":0.0000847}],"pass":{"nmos":1.089,"tgate":1.8}},"ff_sim":{"_note":"SKY130 传输门主从触发器的时序参数（samples/数字集成电路设计/生成脚本/calib/calib_ff.py），以同一仿真中的 FO4 延时为单位：tcq 时钟到输出、tsu 建立时间、th 保持时间、tau_m 亚稳态时间常数、T0 亚稳态窗口","tcq":3.18,"tsu":1.072,"th":-0.943,"tau_m":0.7284,"T0":0.5983}});
})();
// 实验 3.2 时序预算（配 3.2 节）。触发器参数取自 params.json 的 ff_sim（SKY130 仿真，以 FO4 为单位），乘手算模型的 FO4 换算成秒；
// 加 1 电路的关键路径用 M3_2.incDelay(n)（以 τ 为单位，与书中程序 3.2.1 同一模型）。
// 场景 1：时钟频率可调；场景 2：时钟频率 = PWM 频率 × 2^n；场景 3：保持时间检查，可调时钟偏斜和插入的反相器对数。
const P32 = M3_2.P, Q32 = P32.problems.p32, FF32 = M3_2.ffTiming(), TAU32 = M3_2.tau();
const G32 = P32.Cd / P32.Cg, PAIR32 = 2 * (1 + G32) * TAU32;
const tl32 = (n) => M3_2.incDelay(n) * TAU32;
const f32 = (api) => (api.scene === "pwm" ? api.p.pwm * 1e3 * Math.pow(2, api.p.bits) : api.p.f * 1e6);
const su32 = (n, f) => M3_2.setupSlack(1 / f, tl32(n));
const ho32 = (skew, pairs) => M3_2.holdSlack(pairs * PAIR32, skew * 1e-12);

WQ.lab({
  title: ["实验 3.2 时序预算", "Lab 3.2 Timing budget"],
  goal: ["用建立时间约束求 PWM 计数器的最高时钟频率和可行位数；用保持时间约束检查时钟偏斜，插入反相器对修正违例。",
         "Use the setup constraint to find the PWM counter's maximum clock and feasible width; use the hold constraint to check clock skew and fix a violation with inverter pairs."],
  scenes: [
    { id: "setup", robot: true, name: ["计数器的最高频率", "Counter maximum frequency"], hide: ["pwm", "skew", "pairs"],
      problem: { title: ["机器人问题：PWM 计数器能跑多快", "Robot problem: how fast can the PWM counter run"],
                 text: ["16 位计数器每个周期加 1（行波进位）。时钟最高能到多少？",
                        "A 16-bit counter adds 1 every cycle (ripple carry). How fast can the clock go?"] } },
    { id: "pwm", robot: true, name: ["20 kHz PWM 的位数", "Bits at 20 kHz PWM"], hide: ["f", "skew", "pairs"],
      problem: { title: ["机器人问题：不让电机啸叫", "Robot problem: keep the motor quiet"],
                 text: ["PWM 要在 20 kHz 以上（人耳听不到），时钟 = PWM 频率 × 2ⁿ。最多能做几位？",
                        "The PWM must be above 20 kHz (inaudible); the clock is the PWM frequency × 2ⁿ. How many bits at most?"] } },
    { id: "hold", name: ["保持时间", "Hold check"], hide: ["bits", "f", "pwm"],
      problem: { title: ["编码器滤波器的移位寄存器", "The encoder filter's shift register"],
                 text: ["相邻两级之间没有逻辑。后一级的时钟晚到 δ（跨时钟树分支，再加门控单元）。要插几对反相器？",
                        "No logic between stages. The second stage's clock arrives δ later (across tree branches plus a gating cell). How many inverter pairs are needed?"] } },
  ],
  params: [
    { id: "bits", name: ["计数器位数 n", "Counter bits n"], min: 8, max: 16, step: 1, value: 16, unit: "", digits: 0 },
    { id: "f", name: ["时钟频率", "Clock frequency"], min: 50, max: 1500, step: 10, value: 100, unit: "MHz", digits: 0 },
    { id: "pwm", name: ["PWM 频率", "PWM frequency"], min: 10, max: 40, step: 1, value: 20, unit: "kHz", digits: 0 },
    { id: "skew", name: ["时钟偏斜 δ（接收端晚到为正）", "Clock skew δ (capture later = positive)"], min: -100, max: 400, step: 5, value: 0, unit: "ps", digits: 0 },
    { id: "pairs", name: ["插入的反相器对数", "Inverter pairs inserted"], min: 0, max: 4, step: 1, value: 0, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "fmax", robot: true, text: ["16 位：找到建立时间余量不为负的最高频率（再高 10 MHz 就违例）。", "16 bits: find the highest frequency with non-negative setup slack (10 MHz more violates)."],
      demo: { scene: "setup", set: { bits: 16, f: 560 }, press: [], wait: 1 } },
    { id: "bits", robot: true, text: ["PWM 20 kHz：找到余量不为负的最大位数（再加一位就违例）。", "PWM at 20 kHz: find the largest width with non-negative slack (one more bit violates)."],
      demo: { scene: "pwm", set: { pwm: 20, bits: 14 }, press: [], wait: 1 } },
    { id: "hold", text: ["偏斜设为 240 ps（算例 3.2.2）：插入最少的反相器对，使保持时间余量不为负。", "Set the skew to 240 ps (Example 3.2.2): insert the fewest inverter pairs that make the hold slack non-negative."],
      demo: { scene: "hold", set: { skew: 240, pairs: 1 }, press: [], wait: 1 } },
  ],
  think: ["为什么降低时钟频率能修正建立时间违例，却修正不了保持时间违例？插入的反相器对会不会让建立时间违例？",
          "Why does slowing the clock fix setup violations but not hold violations? Can the inserted inverter pairs cause a setup violation?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["tcq", "tcq"], color: "#7a8691" }, { name: ["组合逻辑 / 插入延时", "logic / inserted delay"], color: "#1d6fb8" }, { name: ["tsu、th + δ", "tsu, th + δ"], color: "#e67e22" }],
  reset(api, s) { check32(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p;
    if (api.scene === "hold") {
      const h = ho32(p.skew, p.pairs);
      return [[["tcq + 插入延时", "tcq + inserted delay"], f((FF32.tcq + p.pairs * PAIR32) * 1e12, 0) + " ps"],
              [["th + δ", "th + δ"], f((FF32.th + p.skew * 1e-12) * 1e12, 0) + " ps"],
              [["保持时间余量", "Hold slack"], f(h * 1e12, 0) + " ps " + (h >= 0 ? api.T("（满足）", "(met)") : api.T("（违例）", "(violated)"))],
              [["每对反相器", "Per inverter pair"], f(PAIR32 * 1e12, 1) + " ps"]];
    }
    const fr = f32(api), sl = su32(p.bits, fr);
    return [[["时钟频率 / 周期", "Clock / period"], f(fr / 1e6, 1) + " MHz / " + f(1e9 / fr, 3) + " ns"],
            [["加 1 电路延时", "Incrementer delay"], f(M3_2.incDelay(p.bits), 0) + " τ = " + f(tl32(p.bits) * 1e9, 3) + " ns"],
            [["tcq + 逻辑 + tsu", "tcq + logic + tsu"], f((FF32.tcq + tl32(p.bits) + FF32.tsu) * 1e9, 3) + " ns"],
            [["建立时间余量", "Setup slack"], f(sl * 1e12, 0) + " ps " + (sl >= 0 ? api.T("（满足）", "(met)") : api.T("（违例）", "(violated)"))],
            [["PWM 频率", "PWM frequency"], f(fr / Math.pow(2, p.bits) / 1e3, 2) + " kHz"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mu = css("--muted"), blue = "#1d6fb8", amber = "#e67e22", grey = "#7a8691", red = "#c0392b", green = "#2e7d32";
    const p = api.p, x0 = w * 0.08, x1 = w * 0.92;
    if (api.scene === "hold") {
      const a = FF32.tcq + p.pairs * PAIR32, b = FF32.th + p.skew * 1e-12, span = 600e-12, X = (t) => x0 + (t + 150e-12) / span * (x1 - x0);
      api.line(X(0), h * 0.12, X(0), h * 0.8, mu, 1, [4, 4]); api.label(api.T("时钟沿", "clock edge"), X(0), h * 0.1, mu, 11, "center");
      api.label(api.T("新数据最早到达", "new data earliest"), x0, h * 0.3, ink, 12, "left");
      api.rect(X(0), h * 0.34, X(FF32.tcq) - X(0), h * 0.1, grey);
      if (p.pairs) api.rect(X(FF32.tcq), h * 0.34, X(a) - X(FF32.tcq), h * 0.1, blue);
      api.label(api.T("旧数据须保持到", "old data must hold until"), x0, h * 0.56, ink, 12, "left");
      api.rect(Math.min(X(0), X(b)), h * 0.6, Math.abs(X(b) - X(0)), h * 0.1, amber);
      api.line(X(b), h * 0.3, X(b), h * 0.75, amber, 2);
      const ok = a >= b; api.label(ok ? api.T("满足", "met") : api.T("违例", "violated"), X(Math.max(a, b)) + 10, h * 0.5, ok ? green : red, 14, "left");
      return;
    }
    const fr = f32(api), T = 1 / fr, need = FF32.tcq + tl32(p.bits) + FF32.tsu, span = Math.max(T, need) * 1.1, X = (t) => x0 + t / span * (x1 - x0), y = h * 0.4, bh = h * 0.16;
    api.rect(X(0), y, X(FF32.tcq) - X(0), bh, grey);
    api.rect(X(FF32.tcq), y, X(FF32.tcq + tl32(p.bits)) - X(FF32.tcq), bh, blue);
    api.rect(X(FF32.tcq + tl32(p.bits)), y, X(need) - X(FF32.tcq + tl32(p.bits)), bh, amber);
    api.line(X(T), h * 0.2, X(T), h * 0.75, need <= T ? green : red, 2.5);
    api.label(api.T("下一个时钟沿", "next clock edge"), X(T), h * 0.17, need <= T ? green : red, 12, "center");
    api.line(X(0), h * 0.2, X(0), h * 0.75, mu, 1, [4, 4]);
    api.label("0", X(0), h * 0.8, mu, 11, "center"); api.label(api.fmt(span * 1e9, 2) + " ns", x1, h * 0.8, mu, 11, "right");
  },
});

function check32(api) {
  const p = api.p;
  if (api.scene === "setup" && p.bits === 16 && su32(16, p.f * 1e6) >= 0 && su32(16, (p.f + 10) * 1e6) < 0) api.done("fmax");
  if (api.scene === "pwm" && p.pwm === 20) {
    const f = (n) => 20e3 * Math.pow(2, n);
    if (su32(p.bits, f(p.bits)) >= 0 && (p.bits === 16 || su32(p.bits + 1, f(p.bits + 1)) < 0)) api.done("bits");
  }
  if (api.scene === "hold" && p.skew === 240 && ho32(240, p.pairs) >= 0 && (p.pairs === 0 || ho32(240, p.pairs - 1) < 0)) api.done("hold");
}
