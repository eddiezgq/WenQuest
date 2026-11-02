// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/lab5_4.body.js、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M5_4 = (function () {
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
      /* ---------- 第 5 章：功耗（仿真表 power_sim 插值，与 conventions/mos.py 一一对应） ---------- */
      const PS = P.power_sim || { sc: [[0, 0]], leak_inv: { 27: 0 }, vdd: [[1.8, 1, 1]] };
      const interp = (xs, ys, x, log) => {
        if (x <= xs[0]) return ys[0];
        if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
        for (let i = 0; i < xs.length - 1; i++) if (xs[i] <= x && x <= xs[i + 1]) {
          const t = (x - xs[i]) / (xs[i + 1] - xs[i]);
          return log ? Math.exp(Math.log(ys[i]) + t * (Math.log(ys[i + 1]) - Math.log(ys[i]))) : ys[i] + t * (ys[i + 1] - ys[i]);
        }
      };
      m.scRatio = (t) => Math.max(0, interp(PS.sc.map((a) => a[0]), PS.sc.map((a) => a[1]), t));
      m.leakInv = (temp = 27, vdd = VDD) => {
        const ts = Object.keys(PS.leak_inv).map(Number).sort((a, b) => a - b);
        const i = interp(ts, ts.map((k) => PS.leak_inv[String(k)]), temp, true);
        return i * interp(PS.vdd.map((a) => a[0]), PS.vdd.map((a) => a[2]), vdd, true);
      };
      m.fo4Scale = (vdd) => interp(PS.vdd.map((a) => a[0]), PS.vdd.map((a) => a[1]), vdd, true);
      m.energyPerOp = (vdd, n, alpha, c, depth, temp = 27) => {
        const t = depth * m.fo4Tp(rr) * m.fo4Scale(vdd);
        return [alpha * n * c * vdd * vdd, n * m.leakInv(temp, vdd) * vdd * t, t];
      };
      m.sleepRon = (w, vdd = VDD) => 1 / (kp * w / L * (vdd - VTp));
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
                    inc16: m.incDelay(16), sc: m.scRatio(2), leak85: m.leakInv(85), leak_v: m.leakInv(27, 1.2), fo4s: m.fo4Scale(0.9),
                    eop: m.energyPerOp(0.8, 1e4, 0.1, 5e-15, 30, 85), ron: m.sleepRon(100), xtalk: m.xtalk('met2', 0.14, 0.14, 500, 1, 100e-12),
                    setup: m.setupSlack(1 / f33, 1e-9, 50e-12), hold: m.holdSlack(0, 150e-12), mtbf: {} };
        for (const n of [1, 2]) out.ch3.mtbf[n] = m.mtbf(m.syncTr(n, f33, q33.slack_ps * 1e-12), f33, fd);
        return out;
      };
      return m;
    }
    return { create };
  });
  return self.WQMos.create({"_note":"SKY130 tt 27 °C 校准值（第 17 轮附 3.4，samples/数字集成电路设计/生成脚本/calib/calib.py）：VT 为使传输特性最接近仿真的有效值（线性区外推值见 calib/result.json），k′ 由 IDSAT 反推，Cg、Cd 由输入电容与扇出拟合后按 FO4 延时修正","VDD":1.8,"VTn":0.55,"VTp":0.55,"kn":0.0000845,"kp":0.0000348,"L":0.15,"Wmin":0.42,"Cg":1.25e-15,"Cd":1.97e-15,"problems":{"p11":{"Iload":0.001,"VOLmax":0.2},"p12":{"noise":0.3},"p14":{"CL":1e-11,"tmax":3.5e-10},"p15":{"N":10000,"alpha":0.1,"Cgate":5e-15,"f":100000000,"Vlow":1.2,"fo4max":1e-10},"p23":{"n_addr":3,"Cin_units":2,"Cout_units":32,"branch":4},"p41":{"L_um":3000},"p42":{"layer":"met2","w_um":0.14,"trunk_um":1000,"near_um":400,"far_um":1600,"leaf_load_units":20,"driver_size":20},"p43":{"L_um":3000,"layer":"met1","w_um":0.14,"load_units":20},"p44":{"layer":"met2","w_um":0.14,"len_um":500,"victim_size":1,"tr_ps":100},"p31":{"bits":16,"f_MHz":100},"p32":{"bits":16,"f_MHz":100,"pwm_kHz":20,"gate_fo4":2},"p33":{"rpm":6000,"lines":1024,"f_MHz":100,"slack_ps":200,"robots":1000,"years":10},"p34":{"n_ff":2000,"group":16,"idle":0.9,"f_MHz":100},"p51":{"n_gates":20000,"alpha":0.1,"c_gate_fF":5,"glitch":0.2,"tree_ratio":1.5,"slow_tin_fo4":8},"p52":{"n_equiv":50000,"days":90,"temps":[27,85],"battery_Ah":20},"p53":{"n_gates":20000,"alpha":0.1,"c_gate_fF":5,"depth_fo4":30,"cycles":2000,"loop_kHz":10,"temp":27,"hot":85},"p54":{"n_gates":30000,"alpha":0.1,"c_gate_fF":5,"f_MHz":100,"peak":3,"drop_pct":5,"temp":85,"w_um":[200,500,1000,2000,5000]},"p55":{"bits":16,"f_MHz":100,"rpm":6000,"lines":1024},"p61":{"bits":32,"f_MHz":400},"p63":{"bits":16,"f_MHz":250},"p64":{"bits":16,"f_MHz":500}},"wires":{"_note":"SKY130 导线参数（典型值），由 samples/数字集成电路设计/生成脚本/calib/wires.py 从 open_pdks 的 sky130A.tech 读出：Rsq Ω/□；Carea aF/μm²（对衬底）；Cfringe aF/μm（每条边，对衬底）；同层耦合每微米 Kside/(s+s0) aF；z、t 层底高度与厚度 μm；wmin、smin 最小线宽、间距 μm；via 每个通孔 Ω","layers":{"li1":{"Rsq":12.8,"Carea":36.99,"Cfringe":40.7,"Kside":25.5,"s0":0.14,"z":0.9361,"t":0.1,"wmin":0.17,"smin":0.17},"met1":{"Rsq":0.125,"Carea":25.78,"Cfringe":40.57,"Kside":44,"s0":0.25,"z":1.3761,"t":0.36,"wmin":0.14,"smin":0.14},"met2":{"Rsq":0.125,"Carea":17.5,"Cfringe":37.76,"Kside":50,"s0":0.3,"z":2.0061,"t":0.36,"wmin":0.14,"smin":0.14},"met3":{"Rsq":0.047,"Carea":12.37,"Cfringe":40.99,"Kside":74,"s0":0.4,"z":2.7861,"t":0.845,"wmin":0.3,"smin":0.3},"met4":{"Rsq":0.047,"Carea":8.42,"Cfringe":36.68,"Kside":94,"s0":0.57,"z":4.0211,"t":0.845,"wmin":0.3,"smin":0.3},"met5":{"Rsq":0.029,"Carea":6.32,"Cfringe":38.85,"Kside":155,"s0":0.5,"z":5.3711,"t":1.26,"wmin":1.6,"smin":1.6}},"via":{"li1-met1":9.3,"met1-met2":4.5,"met2-met3":3.41,"met3-met4":3.41,"met4-met5":0.38}},"gates_sim":{"_note":"SKY130 门参数仿真值（samples/数字集成电路设计/生成脚本/calib/calib_gates.py）：g、p 以同一仿真里参考反相器的 τ 为单位；A 为靠近输出的输入，B 为靠近电源轨的输入；pseudo_nmos 为 PMOS 负载取最小宽度时的输出低电平与静态电流；pass 为 10 fF 负载充电 10 ns 后的输出高电平","p_inv":1.559,"gates":{"nand2_A":{"g":1.176,"p":1.944},"nand2_B":{"g":1.166,"p":2.546},"nand3_A":{"g":1.387,"p":2.282},"nand3_B":{"g":1.391,"p":3.963},"nor2_A":{"g":1.68,"p":2.313},"nor2_B":{"g":1.643,"p":3.85},"nor3_A":{"g":2.363,"p":2.726},"nor3_B":{"g":2.342,"p":6.831}},"pseudo_nmos":[{"wn_over_wp":1,"VOL":0.1832,"I":0.0000825},{"wn_over_wp":2,"VOL":0.0788,"I":0.000084},{"wn_over_wp":4,"VOL":0.0332,"I":0.0000847}],"pass":{"nmos":1.089,"tgate":1.8}},"ff_sim":{"_note":"SKY130 传输门主从触发器的时序参数（samples/数字集成电路设计/生成脚本/calib/calib_ff.py），以同一仿真中的 FO4 延时为单位：tcq 时钟到输出、tsu 建立时间、th 保持时间、tau_m 亚稳态时间常数、T0 亚稳态窗口","tcq":3.18,"tsu":1.072,"th":-0.943,"tau_m":0.7284,"T0":0.5983},"power_sim":{"_note":"SKY130 功耗参数（samples/数字集成电路设计/生成脚本/calib/calib_power.py）：sc 为 [输入转换时间/FO4, 短路能量/电容充电能量]；leak_inv 为参考反相器两种输入的平均漏电（A），leak_in0、leak_in1 分别为输入 0（NMOS 关）、输入 1（PMOS 关）；vt_cc 为 100 nA·W/L 定义的 NMOS 阈值（V）；stack 为二输入或非门两个 PMOS 都关与只关一个的漏电之比；S 亚阈值摆幅（mV/dec）、dibl（mV/V）；vdd 为 [VDD, FO4 相对 1.8 V 的倍数, 漏电相对 1.8 V 的倍数]","sc":[[0.214,0.0057],[0.536,0.0135],[1.072,0.0227],[2.144,0.0334],[3.217,0.0396],[4.289,0.0444],[6.433,0.0535],[8.578,0.0633],[12.866,0.0866]],"S27":87.4,"S85":104.4,"dibl":53.6,"leak_inv":{"27":1.428e-10,"85":2.931e-9,"125":1.364e-8},"leak_in0":{"27":1.845e-12,"85":3.229e-12,"125":1.152e-11},"leak_in1":{"27":2.837e-10,"85":5.86e-9,"125":2.727e-8},"vt_cc":0.606,"stack":{"27":0.023,"85":0.053,"125":0.09},"vdd":[[0.4,46392.726,0.0262],[0.5,3770.3694,0.0355],[0.6,437.1669,0.0475],[0.8,19.5442,0.0833],[1,4.3914,0.1433],[1.2,2.2111,0.2414],[1.4,1.5058,0.3974],[1.6,1.1787,0.6381],[1.8,1,1]]},"arith_syn":{"_note":"第 6 章算术电路按 SKY130 sky130_fd_sc_hd（tt_025C_1v80）综合的面积（μm²）、最长延时（ps，ABC 估算，含插缓冲与尺寸调整）与单元数（samples/数字集成电路设计/生成脚本/calib/arith.py）","add_rca_8":{"area":370.4,"delay":1103.4,"cells":53,"area_min":234,"delay_amin":1733.1},"add_cla_8":{"area":645.6,"delay":707.4,"cells":91,"area_min":355.3,"delay_amin":1273.1},"add_csel_8":{"area":474.2,"delay":804.6,"cells":78,"area_min":347.8,"delay_amin":1463.2},"add_bk_8":{"area":326.6,"delay":897.1,"cells":49,"area_min":270.3,"delay_amin":1462.3},"add_ks_8":{"area":491.7,"delay":730.1,"cells":84,"area_min":354.1,"delay_amin":1037},"add_rca_16":{"area":822,"delay":1847.2,"cells":124,"area_min":437.9,"delay_amin":3478.6},"add_cla_16":{"area":991,"delay":983.1,"cells":143,"area_min":699.4,"delay_amin":2009.2},"add_csel_16":{"area":989.7,"delay":1106.8,"cells":174,"area_min":759.5,"delay_amin":2646.1},"add_bk_16":{"area":679.4,"delay":1188.6,"cells":103,"area_min":579.3,"delay_amin":1836},"add_ks_16":{"area":1255,"delay":833.7,"cells":237,"area_min":884.6,"delay_amin":1302.6},"add_rca_32":{"area":1428.9,"delay":3728.2,"cells":273,"area_min":858.3,"delay_amin":7054.7},"add_cla_32":{"area":1727.9,"delay":1446.4,"cells":289,"area_min":1387.6,"delay_amin":3146.3},"add_csel_32":{"area":1910.6,"delay":1782.6,"cells":333,"area_min":1615.3,"delay_amin":3988.3},"add_bk_32":{"area":1341.3,"delay":1474.8,"cells":216,"area_min":1209.9,"delay_amin":2485.8},"add_ks_32":{"area":2807.7,"delay":1038.6,"cells":507,"area_min":2093.3,"delay_amin":1705.2},"mul_array_8":{"area":2832.7,"delay":2932.9,"cells":441,"area_min":1755.4,"delay_amin":4827.1},"mul_dadda_8":{"area":3310.7,"delay":1889.8,"cells":534,"area_min":2119.5,"delay_amin":2866.7},"mul_booth_8":{"area":3946.3,"delay":2113.8,"cells":623,"area_min":2195.9,"delay_amin":3379.2},"mul_array_16":{"area":13122.6,"delay":6581.2,"cells":2089,"area_min":7493.4,"delay_amin":11005.4},"mul_dadda_16":{"area":13795.7,"delay":2576.9,"cells":2277,"area_min":9080,"delay_amin":3902.8},"mul_booth_16":{"area":13033.8,"delay":2763.7,"cells":2175,"area_min":7608.5,"delay_amin":4504},"shift_16":{"area":694.4,"delay":471.3,"cells":129,"area_min":571.8,"delay_amin":978},"cmp_rca_16":{"area":387.9,"delay":1459.2,"cells":77,"area_min":321.6,"delay_amin":2225.8},"cmp_ks_16":{"area":431.7,"delay":606.9,"cells":85,"area_min":339.1,"delay_amin":901.9},"tgt_add_rca_32":{"area":1428.9,"delay":3728.2,"cells":273,"area_min":1428.9,"delay_amin":3728.2,"target":2285},"tgt_add_cla_32":{"area":1456.4,"delay":2276.6,"cells":246,"area_min":1456.4,"delay_amin":2276.6,"target":2285},"tgt_add_csel_32":{"area":1694.1,"delay":2668.4,"cells":283,"area_min":1694.1,"delay_amin":2668.4,"target":2285},"tgt_add_bk_32":{"area":1226.2,"delay":2259,"cells":204,"area_min":1226.2,"delay_amin":2259,"target":2285},"tgt_add_ks_32":{"area":2082,"delay":1562.9,"cells":398,"area_min":2082,"delay_amin":1562.9,"target":2285},"tgt_mul_array_16":{"area":13122.6,"delay":6581.2,"cells":2089,"area_min":13122.6,"delay_amin":6581.2,"target":3785},"tgt_mul_dadda_16":{"area":9217.6,"delay":3764.8,"cells":1576,"area_min":9217.6,"delay_amin":3764.8,"target":3785},"tgt_mul_booth_16":{"area":7848.8,"delay":3738.6,"cells":1259,"area_min":7848.8,"delay_amin":3738.6,"target":3785}}});
})();
// 实验 5.4 电源门控（配 5.4 节）。视觉预处理模块约三万个门（翻转率 0.1、每门 5 fF、100 MHz），由宽 W 的 PMOS 休眠管供电。
// 压降 = 峰值电流（平均的 3 倍）× 休眠管导通电阻（M5_4.sleepRon）；模块漏电 = 门数 × 参考反相器漏电（M5_4.leakInv）；
// 休眠管关断漏电按仿真的 PMOS 关断电流折算到每微米；唤醒能量取模块全部门电容 × VDD²（与书中程序 5.4.1 相同）。
const P54 = M5_4.P, Q54 = P54.problems.p54, PS54 = P54.power_sim, VDD54 = P54.VDD;
const WPREF54 = P54.kn / P54.kp * P54.Wmin;
const IPK54 = Q54.peak * Q54.alpha * Q54.n_gates * Q54.c_gate_fF * 1e-15 * VDD54 * Q54.f_MHz * 1e6;
const EW54 = Q54.n_gates * Q54.c_gate_fF * 1e-15 * VDD54 * VDD54;
function pleak54(temp) {   // PMOS 关断电流（A/μm），温度之间按对数插值
  const ts = Object.keys(PS54.leak_in1).map(Number).sort((a, b) => a - b), ys = ts.map((t) => PS54.leak_in1[String(t)] / WPREF54);
  if (temp <= ts[0]) return ys[0]; if (temp >= ts[ts.length - 1]) return ys[ys.length - 1];
  for (let i = 0; i < ts.length - 1; i++) if (temp <= ts[i + 1]) { const t = (temp - ts[i]) / (ts[i + 1] - ts[i]); return Math.exp(Math.log(ys[i]) + t * (Math.log(ys[i + 1]) - Math.log(ys[i]))); }
}
function gate54(W, temp) {
  const drop = IPK54 * M5_4.sleepRon(W), blk = Q54.n_gates * M5_4.leakInv(temp), hdr = pleak54(temp) * W;
  return { drop, blk, hdr, be: EW54 / ((blk - hdr) * VDD54) };
}
const wneed54 = () => M5_4.sleepRon(1) / (Q54.drop_pct / 100 * VDD54 / IPK54);

WQ.lab({
  title: ["实验 5.4 电源门控", "Lab 5.4 Power gating"],
  goal: ["给巡检机器人的视觉预处理模块断电：选休眠管的宽度，使工作时的压降不超过 5 %；算唤醒能量和盈亏平衡时间，判断空闲多久断电才划算。",
         "Power-gate the robot's vision block: choose the sleep transistor width so the drop stays within 5 %; compute the wake-up energy and the break-even time, and judge how long an idle period must be for gating to pay off."],
  scenes: [
    { id: "vision", robot: true, name: ["视觉预处理模块", "Vision block"], hide: [],
      problem: { title: ["机器人问题：拍照间隙断电", "Robot problem: power off between photos"],
                 text: ["模块只在拍照后工作几十毫秒。85 °C 时它的漏电约 90 μA。休眠管要多宽？空闲多久断电才划算？",
                        "The block works only for tens of milliseconds after each photo; at 85 °C it leaks about 90 μA. How wide must the sleep transistor be, and how long must it idle for gating to pay?"] } },
  ],
  params: [
    { id: "W", name: ["休眠管宽度", "Sleep transistor width"], min: 50, max: 3000, step: 10, value: 100, unit: "μm", digits: 0 },
    { id: "idle", name: ["空闲时间", "Idle time"], min: 1, max: 200, step: 1, value: 10, unit: "μs", digits: 0 },
    { id: "T", name: ["芯片温度", "Chip temperature"], min: 25, max: 125, step: 1, value: 85, unit: "°C", digits: 0 },
  ],
  tasks: [
    { id: "width", robot: true, text: ["找到使压降不超过 5 % 的最小宽度（以 10 μm 为步长）。", "Find the smallest width (10 μm steps) that keeps the drop within 5 %."],
      demo: { scene: "vision", set: { W: 320 }, press: [], wait: 1 } },
    { id: "be85", text: ["宽度取上一步的值，85 °C：找到断电开始省电的最短空闲时间（以 1 μs 为步长）。", "With that width at 85 °C, find the shortest idle time (1 μs steps) at which gating starts to save energy."],
      demo: { scene: "vision", set: { W: 320, T: 85, idle: 4 }, press: [], wait: 1 } },
    { id: "be27", text: ["同样的宽度，27 °C：再找一次。", "Same width at 27 °C: find it again."],
      demo: { scene: "vision", set: { W: 320, T: 27, idle: 65 }, press: [], wait: 1 } },
  ],
  think: ["为什么温度越高，盈亏平衡时间越短？休眠管加宽一倍，压降和关断漏电各怎样变？", "Why does the break-even time shrink as the chip gets hotter? Doubling the width changes the drop and the off leakage how?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["断电省下的能量", "energy saved by gating"], color: "#2e7d32" }, { name: ["唤醒能量", "wake-up energy"], color: "#c0392b" }],
  reset(api, s) { check54(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, g = gate54(p.W, p.T), save = (g.blk - g.hdr) * VDD54 * p.idle * 1e-6 - EW54;
    return [[["峰值时的压降", "Drop at peak current"], f(g.drop * 1e3, 0) + " mV（" + f(g.drop / VDD54 * 100, 1) + " %）"],
            [["模块漏电 / 断电后", "Block leakage / gated"], f(g.blk * 1e6, 1) + " / " + f(g.hdr * 1e6, 2) + " μA"],
            [["唤醒能量", "Wake-up energy"], f(EW54 * 1e9, 3) + " nJ"],
            [["盈亏平衡时间", "Break-even time"], f(g.be * 1e6, 1) + " μs"],
            [["这次空闲断电省下", "Saved over this idle period"], f(save * 1e9, 3) + " nJ " + (save > 0 ? api.T("（划算）", "(worth it)") : api.T("（不划算）", "(not worth it)"))]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, mu = css("--muted"), green = "#2e7d32", red = "#c0392b", amber = "#e67e22";
    const p = api.p, g = gate54(p.W, p.T), px = w * 0.1, py = h * 0.1, pw = w * 0.84, ph = h * 0.7, tmax = Math.max(2 * g.be * 1e6, p.idle * 1.2, 10);
    const pts = []; for (let i = 0; i <= 100; i++) { const t = tmax * i / 100; pts.push([t, ((g.blk - g.hdr) * VDD54 * t * 1e-6) * 1e9]); }
    const ymax = Math.max(EW54 * 1e9 * 2.2, pts[100][1]);
    const ax = api.plot(px, py, pw, ph, [{ pts, color: green }, { pts: [[0, EW54 * 1e9], [tmax, EW54 * 1e9]], color: red }],
      { xmin: 0, xmax: tmax, ymin: 0, ymax, xlabel: api.T("空闲时间 / μs", "idle / μs"), ylabel: "nJ" });
    api.line(ax.X(p.idle), py, ax.X(p.idle), py + ph, amber, 2, [5, 4]);
    api.line(ax.X(g.be * 1e6), py + ph - 6, ax.X(g.be * 1e6), py + ph + 6, mu, 2);
    api.label(api.T("盈亏平衡", "break-even") + " " + api.fmt(g.be * 1e6, 1) + " μs", ax.X(g.be * 1e6) + 4, py + ph - 10, mu, 11, "left");
    api.label("0", px, py + ph + 13, mu, 10, "center"); api.label(api.fmt(tmax, 0), px + pw, py + ph + 13, mu, 10, "right");
    const dok = g.drop / VDD54 <= Q54.drop_pct / 100;
    api.label(api.T("压降 ", "drop ") + api.fmt(g.drop / VDD54 * 100, 1) + " %", px + pw - 4, py + 14, dok ? green : red, 12, "right");
  },
});

function check54(api) {
  const p = api.p, wn = wneed54();
  const okw = p.W >= wn && p.W - 10 < wn;
  if (okw) api.done("width");
  const sv = (idle, T) => (gate54(p.W, T).blk - gate54(p.W, T).hdr) * VDD54 * idle * 1e-6 - EW54;
  if (okw && p.T === 85 && sv(p.idle, 85) > 0 && sv(p.idle - 1, 85) <= 0) api.done("be85");
  if (okw && p.T === 27 && sv(p.idle, 27) > 0 && sv(p.idle - 1, 27) <= 0) api.done("be27");
}
