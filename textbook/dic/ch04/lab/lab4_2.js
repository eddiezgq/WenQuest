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
  return self.WQMos.create({"_note":"SKY130 tt 27 °C 校准值（第 17 轮附 3.4，samples/数字集成电路设计/生成脚本/calib/calib.py）：VT 为使传输特性最接近仿真的有效值（线性区外推值见 calib/result.json），k′ 由 IDSAT 反推，Cg、Cd 由输入电容与扇出拟合后按 FO4 延时修正","VDD":1.8,"VTn":0.55,"VTp":0.55,"kn":0.0000845,"kp":0.0000348,"L":0.15,"Wmin":0.42,"Cg":1.25e-15,"Cd":1.97e-15,"problems":{"p11":{"Iload":0.001,"VOLmax":0.2},"p12":{"noise":0.3},"p14":{"CL":1e-11,"tmax":3.5e-10},"p15":{"N":10000,"alpha":0.1,"Cgate":5e-15,"f":100000000,"Vlow":1.2,"fo4max":1e-10},"p23":{"n_addr":3,"Cin_units":2,"Cout_units":32,"branch":4},"p41":{"L_um":3000},"p42":{"layer":"met2","w_um":0.14,"trunk_um":1000,"near_um":400,"far_um":1600,"leaf_load_units":20,"driver_size":20},"p43":{"L_um":3000,"layer":"met1","w_um":0.14,"load_units":20},"p44":{"layer":"met2","w_um":0.14,"len_um":500,"victim_size":1,"tr_ps":100},"p31":{"bits":16,"f_MHz":100},"p32":{"bits":16,"f_MHz":100,"pwm_kHz":20,"gate_fo4":2},"p33":{"rpm":6000,"lines":1024,"f_MHz":100,"slack_ps":200,"robots":1000,"years":10},"p34":{"n_ff":2000,"group":16,"idle":0.9,"f_MHz":100},"p51":{"n_gates":20000,"alpha":0.1,"c_gate_fF":5,"glitch":0.2,"tree_ratio":1.5,"slow_tin_fo4":8},"p52":{"n_equiv":50000,"days":90,"temps":[27,85],"battery_Ah":20},"p53":{"n_gates":20000,"alpha":0.1,"c_gate_fF":5,"depth_fo4":30,"cycles":2000,"loop_kHz":10,"temp":27,"hot":85},"p54":{"n_gates":30000,"alpha":0.1,"c_gate_fF":5,"f_MHz":100,"peak":3,"drop_pct":5,"temp":85,"w_um":[200,500,1000,2000,5000]},"p55":{"bits":16,"f_MHz":100,"rpm":6000,"lines":1024},"p61":{"bits":32,"f_MHz":400},"p63":{"bits":16,"f_MHz":250},"p64":{"bits":16,"f_MHz":500},"p71":{"bits":32768,"word":32,"cell_w":2.4,"cell_h":1.8,"dec_w":15,"col_h":30,"cin_units":4,"dv":0.1},"p72":{"snm_min_frac":0.2,"cr":[1,1.25,1.5,2,2.5,3],"pr":[1,1.5,2,3]},"p73":{"f_in_MHz":8,"t_svc_us":20,"f_rd_MHz":100,"word":16,"ff_area":20.02,"ports":[1,2,3,4],"track_um":0.46},"p74":{"interval_s":10,"endurance":10000,"entries_per_sector":256,"sectors":16,"years":10},"p81":{"f_MHz":50,"jitter_ps":100,"bits_out":16,"blocks":[["sub","add_rca_16","add_ks_16"],["mul","mul_array_16","mul_dadda_16"],["add1","add_rca_32","add_bk_32"],["add2","add_rca_32","add_bk_32"],["sat","",""]]},"p84":{"die_um":1000,"layer":"met3","levels":3,"size":16,"imb":0.2},"p85":{"f_src_MHz":25,"f_dst_MHz":50,"word":16,"loop_kHz":20}},"wires":{"_note":"SKY130 导线参数（典型值），由 samples/数字集成电路设计/生成脚本/calib/wires.py 从 open_pdks 的 sky130A.tech 读出：Rsq Ω/□；Carea aF/μm²（对衬底）；Cfringe aF/μm（每条边，对衬底）；同层耦合每微米 Kside/(s+s0) aF；z、t 层底高度与厚度 μm；wmin、smin 最小线宽、间距 μm；via 每个通孔 Ω","layers":{"li1":{"Rsq":12.8,"Carea":36.99,"Cfringe":40.7,"Kside":25.5,"s0":0.14,"z":0.9361,"t":0.1,"wmin":0.17,"smin":0.17},"met1":{"Rsq":0.125,"Carea":25.78,"Cfringe":40.57,"Kside":44,"s0":0.25,"z":1.3761,"t":0.36,"wmin":0.14,"smin":0.14},"met2":{"Rsq":0.125,"Carea":17.5,"Cfringe":37.76,"Kside":50,"s0":0.3,"z":2.0061,"t":0.36,"wmin":0.14,"smin":0.14},"met3":{"Rsq":0.047,"Carea":12.37,"Cfringe":40.99,"Kside":74,"s0":0.4,"z":2.7861,"t":0.845,"wmin":0.3,"smin":0.3},"met4":{"Rsq":0.047,"Carea":8.42,"Cfringe":36.68,"Kside":94,"s0":0.57,"z":4.0211,"t":0.845,"wmin":0.3,"smin":0.3},"met5":{"Rsq":0.029,"Carea":6.32,"Cfringe":38.85,"Kside":155,"s0":0.5,"z":5.3711,"t":1.26,"wmin":1.6,"smin":1.6}},"via":{"li1-met1":9.3,"met1-met2":4.5,"met2-met3":3.41,"met3-met4":3.41,"met4-met5":0.38}},"gates_sim":{"_note":"SKY130 门参数仿真值（samples/数字集成电路设计/生成脚本/calib/calib_gates.py）：g、p 以同一仿真里参考反相器的 τ 为单位；A 为靠近输出的输入，B 为靠近电源轨的输入；pseudo_nmos 为 PMOS 负载取最小宽度时的输出低电平与静态电流；pass 为 10 fF 负载充电 10 ns 后的输出高电平","p_inv":1.559,"gates":{"nand2_A":{"g":1.176,"p":1.944},"nand2_B":{"g":1.166,"p":2.546},"nand3_A":{"g":1.387,"p":2.282},"nand3_B":{"g":1.391,"p":3.963},"nor2_A":{"g":1.68,"p":2.313},"nor2_B":{"g":1.643,"p":3.85},"nor3_A":{"g":2.363,"p":2.726},"nor3_B":{"g":2.342,"p":6.831}},"pseudo_nmos":[{"wn_over_wp":1,"VOL":0.1832,"I":0.0000825},{"wn_over_wp":2,"VOL":0.0788,"I":0.000084},{"wn_over_wp":4,"VOL":0.0332,"I":0.0000847}],"pass":{"nmos":1.089,"tgate":1.8}},"ff_sim":{"_note":"SKY130 传输门主从触发器的时序参数（samples/数字集成电路设计/生成脚本/calib/calib_ff.py），以同一仿真中的 FO4 延时为单位：tcq 时钟到输出、tsu 建立时间、th 保持时间、tau_m 亚稳态时间常数、T0 亚稳态窗口","tcq":3.18,"tsu":1.072,"th":-0.943,"tau_m":0.7284,"T0":0.5983},"power_sim":{"_note":"SKY130 功耗参数（samples/数字集成电路设计/生成脚本/calib/calib_power.py）：sc 为 [输入转换时间/FO4, 短路能量/电容充电能量]；leak_inv 为参考反相器两种输入的平均漏电（A），leak_in0、leak_in1 分别为输入 0（NMOS 关）、输入 1（PMOS 关）；vt_cc 为 100 nA·W/L 定义的 NMOS 阈值（V）；stack 为二输入或非门两个 PMOS 都关与只关一个的漏电之比；S 亚阈值摆幅（mV/dec）、dibl（mV/V）；vdd 为 [VDD, FO4 相对 1.8 V 的倍数, 漏电相对 1.8 V 的倍数]","sc":[[0.214,0.0057],[0.536,0.0135],[1.072,0.0227],[2.144,0.0334],[3.217,0.0396],[4.289,0.0444],[6.433,0.0535],[8.578,0.0633],[12.866,0.0866]],"S27":87.4,"S85":104.4,"dibl":53.6,"leak_inv":{"27":1.428e-10,"85":2.931e-9,"125":1.364e-8},"leak_in0":{"27":1.845e-12,"85":3.229e-12,"125":1.152e-11},"leak_in1":{"27":2.837e-10,"85":5.86e-9,"125":2.727e-8},"vt_cc":0.606,"stack":{"27":0.023,"85":0.053,"125":0.09},"vdd":[[0.4,46392.726,0.0262],[0.5,3770.3694,0.0355],[0.6,437.1669,0.0475],[0.8,19.5442,0.0833],[1,4.3914,0.1433],[1.2,2.2111,0.2414],[1.4,1.5058,0.3974],[1.6,1.1787,0.6381],[1.8,1,1]]},"arith_syn":{"_note":"第 6 章算术电路按 SKY130 sky130_fd_sc_hd（tt_025C_1v80）综合的面积（μm²）、最长延时（ps，ABC 估算，含插缓冲与尺寸调整）与单元数（samples/数字集成电路设计/生成脚本/calib/arith.py）","add_rca_8":{"area":370.4,"delay":1103.4,"cells":53,"area_min":234,"delay_amin":1733.1},"add_cla_8":{"area":645.6,"delay":707.4,"cells":91,"area_min":355.3,"delay_amin":1273.1},"add_csel_8":{"area":474.2,"delay":804.6,"cells":78,"area_min":347.8,"delay_amin":1463.2},"add_bk_8":{"area":326.6,"delay":897.1,"cells":49,"area_min":270.3,"delay_amin":1462.3},"add_ks_8":{"area":491.7,"delay":730.1,"cells":84,"area_min":354.1,"delay_amin":1037},"add_rca_16":{"area":822,"delay":1847.2,"cells":124,"area_min":437.9,"delay_amin":3478.6},"add_cla_16":{"area":991,"delay":983.1,"cells":143,"area_min":699.4,"delay_amin":2009.2},"add_csel_16":{"area":989.7,"delay":1106.8,"cells":174,"area_min":759.5,"delay_amin":2646.1},"add_bk_16":{"area":679.4,"delay":1188.6,"cells":103,"area_min":579.3,"delay_amin":1836},"add_ks_16":{"area":1255,"delay":833.7,"cells":237,"area_min":884.6,"delay_amin":1302.6},"add_rca_32":{"area":1428.9,"delay":3728.2,"cells":273,"area_min":858.3,"delay_amin":7054.7},"add_cla_32":{"area":1727.9,"delay":1446.4,"cells":289,"area_min":1387.6,"delay_amin":3146.3},"add_csel_32":{"area":1910.6,"delay":1782.6,"cells":333,"area_min":1615.3,"delay_amin":3988.3},"add_bk_32":{"area":1341.3,"delay":1474.8,"cells":216,"area_min":1209.9,"delay_amin":2485.8},"add_ks_32":{"area":2807.7,"delay":1038.6,"cells":507,"area_min":2093.3,"delay_amin":1705.2},"mul_array_8":{"area":2832.7,"delay":2932.9,"cells":441,"area_min":1755.4,"delay_amin":4827.1},"mul_dadda_8":{"area":3310.7,"delay":1889.8,"cells":534,"area_min":2119.5,"delay_amin":2866.7},"mul_booth_8":{"area":3946.3,"delay":2113.8,"cells":623,"area_min":2195.9,"delay_amin":3379.2},"mul_array_16":{"area":13122.6,"delay":6581.2,"cells":2089,"area_min":7493.4,"delay_amin":11005.4},"mul_dadda_16":{"area":13795.7,"delay":2576.9,"cells":2277,"area_min":9080,"delay_amin":3902.8},"mul_booth_16":{"area":13033.8,"delay":2763.7,"cells":2175,"area_min":7608.5,"delay_amin":4504},"shift_16":{"area":694.4,"delay":471.3,"cells":129,"area_min":571.8,"delay_amin":978},"cmp_rca_16":{"area":387.9,"delay":1459.2,"cells":77,"area_min":321.6,"delay_amin":2225.8},"cmp_ks_16":{"area":431.7,"delay":606.9,"cells":85,"area_min":339.1,"delay_amin":901.9},"tgt_add_rca_32":{"area":1428.9,"delay":3728.2,"cells":273,"area_min":1428.9,"delay_amin":3728.2,"target":2285},"tgt_add_cla_32":{"area":1456.4,"delay":2276.6,"cells":246,"area_min":1456.4,"delay_amin":2276.6,"target":2285},"tgt_add_csel_32":{"area":1694.1,"delay":2668.4,"cells":283,"area_min":1694.1,"delay_amin":2668.4,"target":2285},"tgt_add_bk_32":{"area":1226.2,"delay":2259,"cells":204,"area_min":1226.2,"delay_amin":2259,"target":2285},"tgt_add_ks_32":{"area":2082,"delay":1562.9,"cells":398,"area_min":2082,"delay_amin":1562.9,"target":2285},"tgt_mul_array_16":{"area":13122.6,"delay":6581.2,"cells":2089,"area_min":13122.6,"delay_amin":6581.2,"target":3785},"tgt_mul_dadda_16":{"area":9217.6,"delay":3764.8,"cells":1576,"area_min":9217.6,"delay_amin":3764.8,"target":3785},"tgt_mul_booth_16":{"area":7848.8,"delay":3738.6,"cells":1259,"area_min":7848.8,"delay_amin":3738.6,"target":3785}},"sram_sim":{"_note":"第 7 章 6 管 SRAM 单元按 SKY130 tt、27 °C 仿真（samples/数字集成电路设计/生成脚本/calib/calib_sram.py）：SNM 与写入裕量（V），读电流（A），每单元位线电容（F，只含存取管漏极，不含导线），位线的起步时间 t_bl0（s），位线掉 100 mV 的时间与灵敏放大器分辨时间（s）","snm_hold":[[1,0.7259],[1.25,0.7093],[1.5,0.7141],[2,0.7073],[2.5,0.7017],[3,0.6939]],"snm_read":[[1,0.3067],[1.25,0.3456],[1.5,0.375],[2,0.4165],[2.5,0.4528],[3,0.4702]],"snm_vdd":[[0.9,0.2308,0.3828],[1.2,0.2915,0.5238],[1.5,0.3623,0.631],[1.8,0.4165,0.7073]],"write":[[1,0.624],[1.5,0.54],[2,0.47],[3,0.328]],"i_read":0.0001552,"c_cell":2.541e-16,"t_bl0":6.278e-12,"bl_t":[[64,1.678e-11],[128,2.72e-11],[256,4.821e-11]],"sa":[[0.025,5.03e-11],[0.05,3.624e-11],[0.1,2.469e-11],[0.2,1.588e-11]],"curves":{"hold_1":[1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.7999,1.7999,1.7998,1.7997,1.7995,1.7992,1.7986,1.7976,1.796,1.7936,1.7897,1.7838,1.7749,1.7617,1.7423,1.7138,1.6701,1.5945,1.39,1.0408,0.6882,0.3665,0.1394,0.0769,0.0523,0.0377,0.0278,0.0208,0.0156,0.0117,0.0088,0.0066,0.0049,0.0036,0.0027,0.0019,0.0014,0.001,0.0008,0.0006,0.0004,0.0003,0.0002,0.0002,0.0001,0.0001,0.0001,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"read_1":[1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.7999,1.7999,1.7998,1.7997,1.7995,1.7992,1.7986,1.7976,1.796,1.7936,1.7897,1.7838,1.7749,1.7617,1.7423,1.7138,1.6701,1.5945,1.39,1.0562,0.9359,0.8881,0.8552,0.8285,0.8052,0.7839,0.7641,0.7453,0.7273,0.7099,0.6931,0.6767,0.6606,0.645,0.6296,0.6144,0.5995,0.5848,0.5703,0.5561,0.5419,0.528,0.5143,0.5008,0.4876,0.4746,0.4619,0.4495,0.4374,0.4258,0.4146,0.4039,0.3937,0.384,0.3749,0.3665,0.3586,0.3512,0.3444,0.3381,0.3322,0.3267,0.3215,0.3167,0.3122,0.308,0.3039,0.3001,0.2966],"hold_2":[1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.7999,1.7999,1.7998,1.7996,1.7993,1.7988,1.798,1.7966,1.7943,1.7907,1.7849,1.7759,1.7622,1.7415,1.7101,1.6609,1.5751,1.3514,0.9895,0.6355,0.3216,0.113,0.0626,0.0424,0.0306,0.0226,0.017,0.0129,0.0098,0.0074,0.0056,0.0042,0.0032,0.0024,0.0017,0.0013,0.0009,0.0007,0.0005,0.0004,0.0003,0.0002,0.0001,0.0001,0.0001,0.0001,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"read_2":[1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.8,1.7999,1.7999,1.7998,1.7996,1.7993,1.7988,1.798,1.7966,1.7943,1.7907,1.7849,1.7759,1.7622,1.7415,1.7101,1.6609,1.5751,1.3514,1.02,0.9122,0.862,0.8248,0.7929,0.7635,0.7355,0.7084,0.6817,0.6555,0.6295,0.6037,0.5782,0.5529,0.5279,0.5032,0.4788,0.4548,0.4313,0.4084,0.3862,0.3649,0.3448,0.3261,0.3091,0.2938,0.2803,0.2684,0.2578,0.2485,0.2401,0.2325,0.2257,0.2194,0.2136,0.2083,0.2033,0.1987,0.1944,0.1904,0.1866,0.1831,0.1798,0.1766,0.1737,0.1709,0.1682,0.1657,0.1633,0.161,0.1589,0.1568]}}});
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
