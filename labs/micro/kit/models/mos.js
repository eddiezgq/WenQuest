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
    /* ---------- 第 7 章：存储器（与 conventions/mos.py 一一对应） ---------- */
    m.sramHalf = (vin, cr, pr, mode = 'read', vdd = VDD) => {
      let lo = 0, hi = vdd;
      for (let i = 0; i < 60; i++) {
        const mid = (lo + hi) / 2;
        let f = m.idn(vin, mid, cr * Wmin) - m.idp(vdd - vin, vdd - mid, pr * Wmin);
        if (mode === 'read') f -= m.idn(vdd - mid, vdd - mid, Wmin);
        if (f > 0) hi = mid; else lo = mid;
      }
      return (lo + hi) / 2;
    };
    m.sramCurve = (cr, pr, mode = 'read', step = 0.002, vdd = VDD) => {
      const n = Math.round(vdd / step), xs = [], ys = [];
      for (let i = 0; i <= n; i++) { xs.push(i * step); ys.push(m.sramHalf(i * step, cr, pr, mode, vdd)); }
      return { xs, ys };
    };
    m.snmSeevinck = (xs, ys, vdd = VDD) => {
      const s2 = Math.SQRT2, cmp = (p, q) => p[0] - q[0] || p[1] - q[1];
      const a = xs.map((x, i) => [(x - ys[i]) / s2, (x + ys[i]) / s2]).sort(cmp);
      const b = xs.map((x, i) => [(ys[i] - x) / s2, (ys[i] + x) / s2]).sort(cmp);
      const at = (c, u) => {
        if (u <= c[0][0] || u >= c[c.length - 1][0]) return null;
        let lo = 0, hi = c.length - 1;
        while (hi - lo > 1) { const mm = (lo + hi) >> 1; if (c[mm][0] <= u) lo = mm; else hi = mm; }
        const t = c[hi][0] > c[lo][0] ? (u - c[lo][0]) / (c[hi][0] - c[lo][0]) : 0;
        return c[lo][1] + t * (c[hi][1] - c[lo][1]);
      };
      let pos = 0, neg = 0;
      const n = 2000, umax = vdd / s2;
      for (let i = 1; i < n; i++) {
        const u = -umax + 2 * umax * i / n, va = at(a, u), vb = at(b, u);
        if (va === null || vb === null) continue;
        pos = Math.max(pos, va - vb); neg = Math.max(neg, vb - va);
      }
      return Math.min(pos, neg) / s2;
    };
    m.sramSnm = (cr, pr = 1, mode = 'read', vdd = VDD) => { const c = m.sramCurve(cr, pr, mode, 0.002, vdd); return m.snmSeevinck(c.xs, c.ys, vdd); };
    m.sramWriteQ = (qb, vbl, cr, pr, vdd = VDD) => {
      let lo = 0, hi = vdd;
      for (let i = 0; i < 60; i++) {
        const mid = (lo + hi) / 2;
        let f = m.idn(qb, mid, cr * Wmin) - m.idp(vdd - qb, vdd - mid, pr * Wmin);
        if (mid > vbl) f += m.idn(vdd - vbl, mid - vbl, Wmin); else f -= m.idn(vdd - mid, vbl - mid, Wmin);
        if (f > 0) hi = mid; else lo = mid;
      }
      return (lo + hi) / 2;
    };
    m.sramWriteTrip = (cr, pr, vdd = VDD, iters = 120) => {
      const holds = (vbl) => { let q = vdd; for (let i = 0; i < iters; i++) q = m.sramWriteQ(m.sramHalf(q, cr, pr, 'read', vdd), vbl, cr, pr, vdd); return q > vdd / 2; };
      let lo = 0, hi = vdd;
      for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (holds(mid)) hi = mid; else lo = mid; }
      return (lo + hi) / 2;
    };
    const SS = P.sram_sim || { snm_read: [[1, 0]], snm_hold: [[1, 0]], write: [[1, 0]], sa: [[0.1, 1e-11]], i_read: 1e-4, c_cell: 0, t_bl0: 0 };
    m.sramSimSnm = (cr, mode = 'read') => { const t = SS['snm_' + mode]; return interp(t.map((a) => a[0]), t.map((a) => a[1]), cr); };
    m.sramSimWrite = (pr) => interp(SS.write.map((a) => a[0]), SS.write.map((a) => a[1]), pr);
    m.saTime = (dv) => interp(SS.sa.map((a) => a[0]), SS.sa.map((a) => a[1]), dv, true);
    m.sramAccess = (rows, cols, word, dv = 0.1, q = null) => {
      q = q || P.problems.p71;
      const n = Math.max(2, Math.round(Math.log2(rows))), n1 = Math.floor((n + 1) / 2), cw = cols * q.cell_w;
      const w1 = WL.met1.wmin, w2 = WL.met2.wmin;
      const cWl = cols * 2 * Wmin * Cg + m.wireC('met1', w1) * cw, cIn = q.cin_units * m.cin(Wmin, rr * Wmin);
      const B = rows / 2, H = cWl / cIn;
      let best = null;
      for (let N = 4; N <= 12; N += 2) {
        const gs = [m.leG('nand', n1), 1, m.leG('nand', 2)].concat(Array(N - 3).fill(1));
        const ps = [m.leP('nand', n1), m.leP('inv', 1), m.leP('nand', 2)].concat(Array(N - 3).fill(m.leP('inv', 1)));
        const d = m.pathDelay(gs, ps, B, H).D;
        if (best === null || d < best[0]) best = [d, N];
      }
      const tDec = best[0] * m.tau(), rw = m.wireR('met1', w1) * cw, tWl = 0.38 * rw * cWl;
      const cDev = rows * SS.c_cell, cWire = rows * m.wireC('met2', w2) * q.cell_h, cBl = cDev + cWire;
      const tBl = SS.t_bl0 + cBl * dv / SS.i_read, tSa = m.saTime(dv);
      const M = Math.max(1, Math.floor(cols / word)), tOut = m.fo4Tp(rr) * (2 + 0.5 * Math.log2(M));
      const area = rows * cols * q.cell_w * q.cell_h + rows * q.cell_h * q.dec_w + cols * q.cell_w * q.col_h;
      return { dec: tDec, dec_N: best[1], wl: tWl, bl: tBl, sa: tSa, out: tOut, total: tDec + tWl + tBl + tSa + tOut, area,
               c_bl: cBl, c_wl: cWl, mux: M, w_um: cw + q.dec_w, h_um: rows * q.cell_h + q.col_h, c_bl_dev: cDev, c_bl_wire: cWire };
    };
    /* ---------- 第 8 章：时钟与时序分析（与 conventions/mos.py 一一对应） ---------- */
    m.satDelay = (nHi = 16, nOut = 16) => {
      const k = Math.max(1, Math.round(Math.log2(nHi))), gs = [], ps = [];
      for (let i = 0; i < k; i++) { const kind = i % 2 === 0 ? 'nor' : 'nand'; gs.push(m.leG(kind, 2)); ps.push(m.leP(kind, 2)); }
      gs.push(1, m.leG('nand', 2), m.leG('nand', 2)); ps.push(m.leP('inv', 1), m.leP('nand', 2), m.leP('nand', 2));
      return m.pathDelay(gs, ps, nOut, 1).D * m.tau();
    };
    m.ffClkCap = () => (1 + (3 + gam) + (2 + gam)) * m.cin(Wmin, rr * Wmin);
    m.htree = (levels, die, nFf, size, layer = 'met3', imb = 0, vdd = VDD, f = 100e6) => {
      const R0 = (m.reqN(Wmin) + m.reqP(rr * Wmin)) / 2, C0 = m.cin(Wmin, rr * Wmin);
      const Rd = R0 / size, Cself = gam * C0 * size, Cb = C0 * size, w = WL[layer].wmin, rw = m.wireR(layer, w), cw = m.wireC(layer, w);
      const mm = 2 * levels;
      let tTree = 0, cWire = 0, nBuf = 1;
      for (let i = 1; i <= mm; i++) {
        const seg = die / 2 ** (Math.ceil(i / 2) + 1), Rw = rw * seg, Cw = cw * seg;
        tTree += 0.69 * Rd * (Cself + 2 * (Cw + Cb)) + 0.38 * Rw * Cw + 0.69 * Rw * Cb;
        cWire += 2 ** i * Cw; nBuf += 2 ** i;
      }
      const leaves = 4 ** levels, a = die / 2 ** levels, cff = m.ffClkCap();
      const leaf = (n) => { const cl = cw * a * Math.sqrt(n); return [0.69 * Rd * (Cself + cl + n * cff) + 0.38 * rw * a * (cl + n * cff), cl]; };
      const nPer = nFf / leaves, [tLeaf, cLoc] = leaf(nPer), [tImb] = leaf(nPer * (1 + imb));
      const cLocal = leaves * cLoc, cBuf = nBuf * (Cb + Cself), cFfs = nFf * cff, cTot = cWire + cLocal + cBuf + cFfs;
      return { t_tree: tTree, t_leaf: tLeaf, insertion: tTree + tLeaf, skew: tImb - tLeaf, n_buf: nBuf, leaves, n_per: nPer,
               c_wire: cWire, c_local: cLocal, c_buf: cBuf, c_ff: cFfs, c_total: cTot, ratio: (cTot - cFfs) / cFfs,
               power: cTot * vdd * vdd * f, p_ff: cFfs * vdd * vdd * f, wire_um: cWire / cw + cLocal / cw };
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
                  inc16: m.incDelay(16), sc: m.scRatio(2), leak85: m.leakInv(85), leak_v: m.leakInv(27, 1.2), fo4s: m.fo4Scale(0.9),
                  eop: m.energyPerOp(0.8, 1e4, 0.1, 5e-15, 30, 85), ron: m.sleepRon(100), xtalk: m.xtalk('met2', 0.14, 0.14, 500, 1, 100e-12),
                  setup: m.setupSlack(1 / f33, 1e-9, 50e-12), hold: m.holdSlack(0, 150e-12), mtbf: {} };
      for (const n of [1, 2]) out.ch3.mtbf[n] = m.mtbf(m.syncTr(n, f33, q33.slack_ps * 1e-12), f33, fd);
      out.ch7 = { snm_read: {}, snm_hold: {}, write: {}, access: {} };
      for (const cr of [1, 2, 3]) { out.ch7.snm_read[cr] = m.sramSnm(cr, 1, 'read'); out.ch7.snm_hold[cr] = m.sramSnm(cr, 1, 'hold'); }
      for (const pr of [1, 2, 3]) out.ch7.write[pr] = m.sramWriteTrip(2, pr);
      for (const R of [64, 256, 1024]) { const a = m.sramAccess(R, 32768 / R, 32); out.ch7.access[R] = { total: a.total, dec: a.dec, bl: a.bl, area: a.area }; }
      out.ch7.sa = m.saTime(0.07); out.ch7.sim = m.sramSimSnm(1.75);
      out.ch8 = { sat: m.satDelay(), cff: m.ffClkCap(), tree: {} };
      for (const [L, S] of [[2, 8], [3, 16], [4, 32]]) { const h = m.htree(L, 1000, 2000, S, 'met3', 0.2); out.ch8.tree[L + '_' + S] = { ins: h.insertion, skew: h.skew, ratio: h.ratio, power: h.power }; }
      return out;
    };
    return m;
  }
  return { create };
});
