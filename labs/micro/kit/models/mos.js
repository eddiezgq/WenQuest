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
