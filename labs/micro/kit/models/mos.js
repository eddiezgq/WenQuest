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
      for (let N = 1; N <= 8; N++) t[N] = m.chainDelay(N, CL, r);
      out.p14 = { Cin: C1, F: CL / C1, Nopt4: Math.log(CL / C1) / Math.log(4), t };
      const q = pr.p15;
      out.p15 = { P_VDD: m.dynPower(q.N, q.alpha, q.Cgate, VDD, q.f), P_low: m.dynPower(q.N, q.alpha, q.Cgate, q.Vlow, q.f) };
      return out;
    };
    return m;
  }
  return { create };
});
