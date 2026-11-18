// 第 172b 轮：挑线四连杆的供线和判据——和 tools/wqls/g81_takeup.py 的 takeup3d、g4_takeup.Mech2.link_pose 同一套公式。
// 挑线虚拟实验（takeup.html）和测试（factory/digital/tests/test_wqls_spec.py 用 node 跑，结果和 Python 比）共用。
(function (root) {
  const DEG = Math.PI / 180;
  function linkPose(f, lk) {
    const q = (f + lk.d) * DEG;
    const P = [-lk.r * Math.sin(q), -lk.r * Math.cos(q)], Q = [lk.Qz, lk.Qy];
    const dz = Q[0] - P[0], dy = Q[1] - P[1], D = Math.hypot(dz, dy);
    const tt = (lk.a * lk.a - lk.b * lk.b + D * D) / (2 * D), h2 = lk.a * lk.a - tt * tt;
    if (!(h2 > 0)) return null;
    const h = Math.sqrt(h2) * (lk.br === undefined ? 1 : lk.br);
    const mz = P[0] + tt * dz / D, my = P[1] + tt * dy / D;
    const M = [mz - h * dy / D, my + h * dz / D];
    const uz = (M[0] - P[0]) / lk.a, uy = (M[1] - P[1]) / lk.a, ca = Math.cos(lk.al * DEG), sa = Math.sin(lk.al * DEG);
    const E = [P[0] + lk.c * (uz * ca - uy * sa), P[1] + lk.c * (uz * sa + uy * ca)];
    const w1 = [P[0] - M[0], P[1] - M[1]], w2 = [Q[0] - M[0], Q[1] - M[1]];
    const mu = Math.acos(Math.max(-1, Math.min(1, (w1[0] * w2[0] + w1[1] * w2[1]) / lk.a / lk.b)) ) / DEG;
    return { P, M, E, Q, mu };
  }
  // TK：proto.json 的 takeup（导线点 x、各布厚的耗线、phc、fin）；fab：布料键
  function takeup3d(lk, TK, fab) {
    const A = lk.A, B = lk.B, Lp = [], poses = [], mu = [];
    for (let i = 0; i < 360; i++) {
      const p = linkPose(i, lk); if (!p) return null;
      poses.push(p); mu.push(p.mu);
      const e = p.E;
      Lp.push(Math.sqrt((TK.XA - TK.XE) ** 2 + (e[0] - A[0]) ** 2 + (e[1] - A[1]) ** 2) + Math.sqrt((TK.XB - TK.XE) ** 2 + (e[0] - B[0]) ** 2 + (e[1] - B[1]) ** 2));
    }
    const mx = Math.max(...Lp), Sp = Lp.map(v => mx - v);
    let top = 0; for (let i = 1; i < 360; i++) if (Sp[i] < Sp[top]) top = i;
    const t = TK.fabrics[fab], c = TK.s_ref + t, dem = TK.demand[fab];
    const D = Sp.map((_, i) => i < top ? c : dem[i]), sl = Sp.map((v, i) => v - D[i]);
    const phc = TK.phc, fin = TK.fin[fab];
    let margin = Infinity; for (let i = phc; i <= Math.min(359, phc + 135); i++) margin = Math.min(margin, sl[i]);
    let pre = -1e9; if (fin >= top) { pre = -Infinity; for (let i = top; i <= fin; i++) pre = Math.max(pre, sl[i]); }
    let neg = 0; if (phc > fin) { let m = -Infinity; for (let i = fin; i < phc; i++) m = Math.max(m, -sl[i]); neg = Math.max(0, m); }
    let mTop = -99; for (let i = 0; i < 360; i += 2) if (poses[i].M[0] >= 36) mTop = Math.max(mTop, poses[i].M[1]);
    return { Sp, D, sl, top, margin, pre, neg, Smax: Math.max(...Sp), mu: [Math.min(...mu), Math.max(...mu)], mTop, poses };
  }
  const api = { linkPose, takeup3d };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.WQTakeup = api;
})(this);
