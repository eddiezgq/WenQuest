// 实验 18.3 Stewart 平台的逆解与正解（配 18.3 节）。
// 几何同算例 11.5.4：万向节 aᵢ 在半径 0.5 m 的圆上（方位角 −10°、10°、110°、130°、230°、250°），球关节 bᵢ 在平台坐标系中
//   半径 0.3 m 的圆上（−50°、50°、70°、170°、190°、290°）；原点位姿平台中心高 0.6 m；电动缸行程 0.55～0.85 m。
// 姿态 R = Rot(z, 偏航) Rot(y, 俯仰) Rot(x, 横滚)（RPY，4.5 节）。逆解 lᵢ = |p + R bᵢ − aᵢ|（式 (11.5.9)）。
// A 的第 i 行是沿腿的单位力旋量 (aᵢ × ŝᵢ, ŝᵢ)（式 (18.2.5)），l̇ = A𝒱_s（式 (18.3.3)）。
// “正解”按钮：从原点位姿出发做牛顿法 (18.3.5)：A Δ𝒱 = l − l(T)，T ← exp([Δ𝒱]) T，一步不超过 0.5，残差 < 1e-12 m 停止。
// 生活场景：三条腿可以伸缩的桌子放在不平的地上。三条腿竖直，位于半径 0.5 m 的圆上（方位角 90°、210°、330°），
//   三处地面高度 0、+0.03、−0.02 m；腿 1 长 0.70 m 不变，调腿 2、腿 3，使桌面水平（三条腿顶端确定桌面）。
WQ.lab({
  title: ["实验 18.3 Stewart 平台的逆解与正解", "Lab 18.3 Inverse and forward kinematics of the Stewart platform"],
  goal: ["给定动平台的位姿，算出六条腿长；再只用六条腿长，用牛顿法把位姿求回来，看几步收敛；找出平台绕竖直轴转 90° 时的奇异。",
         "Give the platform a pose and get the six leg lengths; then recover the pose from the lengths alone by Newton's method and count the steps; find the singularity when the platform turns 90° about the vertical."],
  scenes: [
    { id: "st", robot: true, name: ["Stewart 平台", "Stewart platform"], hide: ["l2", "l3"],
      problem: { title: ["机器人问题：座舱要摆到这个姿态，六根缸各伸多长", "Robot problem: how long must each cylinder be for this cabin attitude"],
                 text: ["用滑块给出动平台中心的位置和横滚、俯仰、偏航角。腿超出 0.55～0.85 m 的行程（示意值）时变红。按“正解”，只用六条腿长从原点位姿出发迭代，界面列出每一步的残差。",
                        "Set the platform centre and the roll, pitch and yaw. A leg turns red when it leaves the 0.55–0.85 m stroke (an illustrative value). Press Forward to iterate from the home pose using only the six lengths; each step's residual is listed."] } },
    { id: "table", name: ["调平三脚桌", "Levelling a three-legged table"], hide: ["x", "y", "z", "roll", "pitch", "yaw"],
      problem: { title: ["生活中的例子：在不平的地上把桌面调平", "Everyday example: levelling a table on an uneven floor"],
                 text: ["桌子的三条腿可以伸缩，地面三处高低不同。腿 1 不动，调节腿 2、腿 3 的长度，使桌面水平。三条腿的顶端决定桌面，这就是一个三条腿的并联机构。",
                        "The table's three legs telescope and the floor is uneven. Keep leg 1, adjust legs 2 and 3 until the top is level. The tops of the three legs fix the table top: a three-legged parallel mechanism."] } },
  ],
  params: [
    { id: "x", name: ["平台中心 x", "centre x"], min: -0.1, max: 0.1, step: 0.005, value: 0, unit: "m", digits: 3 },
    { id: "y", name: ["平台中心 y", "centre y"], min: -0.1, max: 0.1, step: 0.005, value: 0, unit: "m", digits: 3 },
    { id: "z", name: ["平台中心 z", "centre z"], min: 0.4, max: 0.8, step: 0.005, value: 0.6, unit: "m", digits: 3 },
    { id: "roll", name: ["横滚（绕 x）", "roll (about x)"], min: -40, max: 40, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "pitch", name: ["俯仰（绕 y）", "pitch (about y)"], min: -40, max: 40, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "yaw", name: ["偏航（绕 z）", "yaw (about z)"], min: -100, max: 100, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "l2", name: ["桌腿 2 的长度", "table leg 2"], min: 0.6, max: 0.8, step: 0.001, value: 0.7, unit: "m", digits: 3 },
    { id: "l3", name: ["桌腿 3 的长度", "table leg 3"], min: 0.6, max: 0.8, step: 0.001, value: 0.7, unit: "m", digits: 3 },
  ],
  buttons: [{ id: "fk", name: ["正解（牛顿法）", "Forward (Newton)"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 18.3.1：中心 (0.05, −0.03, 0.62) m，横滚 6°、俯仰 −8°、偏航 12°，读出六条腿长（最短约 0.630 m，最长约 0.752 m）。",
                                     "Example 18.3.1: centre (0.05, −0.03, 0.62) m, roll 6°, pitch −8°, yaw 12°; read the six lengths (shortest about 0.630 m, longest about 0.752 m)."],
      demo: { scene: "st", set: { x: 0.05, y: -0.03, z: 0.62, roll: 6, pitch: -8, yaw: 12 }, press: [], wait: 1 } },
    { id: "fk", robot: true, text: ["在这个位姿按“正解”：牛顿法从原点位姿出发，6 步以内收敛，求回的位姿与给定的一致。",
                                     "At this pose press Forward: Newton's method from the home pose converges within 6 steps and recovers the given pose."],
      demo: { scene: "st", set: { x: 0.05, y: -0.03, z: 0.62, roll: 6, pitch: -8, yaw: 12 }, press: ["fk"], wait: 1 } },
    { id: "stroke", robot: true, text: ["让某条腿超出 0.55～0.85 m 的行程（例如横滚 40°），记下是哪条腿。", "Push a leg out of the 0.55–0.85 m stroke (e.g. roll 40°) and note which one."],
      demo: { scene: "st", set: { x: 0, y: 0, z: 0.6, roll: 40, pitch: 0, yaw: 0 }, press: [], wait: 1 } },
    { id: "sing", robot: true, text: ["平台中心在 (0, 0, 0.6) m，只改偏航角，找到 det A 变号的地方（|det A| < 0.002）。", "With the centre at (0, 0, 0.6) m change only the yaw and find where det A changes sign (|det A| < 0.002)."],
      demo: { scene: "st", set: { x: 0, y: 0, z: 0.6, roll: 0, pitch: 0, yaw: 90 }, press: [], wait: 1 } },
    { id: "table", text: ["生活场景：调节桌腿 2、3，使桌面倾斜不到 0.2°。", "Everyday scene: adjust legs 2 and 3 until the top tilts by less than 0.2°."],
      demo: { scene: "table", set: { l2: 0.67, l3: 0.72 }, press: [], wait: 1 } },
  ],
  think: ["“正解”从原点位姿出发时一般要 4～5 步；实际控制器用上一个周期的位姿作初值，只要 2 步。为什么？从一个很远的初值出发，可能得到什么？",
          "From the home pose Forward takes 4–5 steps; a real controller starts from the previous cycle's pose and needs only 2. Why? What might you get from a far-off starting guess?"],

  // ---------------- 几何与运算
  A: [-10, 10, 110, 130, 230, 250].map((d) => [0.5 * Math.cos(d * Math.PI / 180), 0.5 * Math.sin(d * Math.PI / 180), 0]),
  Bp: [-50, 50, 70, 170, 190, 290].map((d) => [0.3 * Math.cos(d * Math.PI / 180), 0.3 * Math.sin(d * Math.PI / 180), 0]),
  LMIN: 0.55, LMAX: 0.85,
  COL: ["#d62728", "#e8a33d", "#2ca02c", "#17becf", "#1f77b4", "#9467bd"],
  mul(A, B) { return A.map((r) => B[0].map((_, j) => r.reduce((s, a, k) => s + a * B[k][j], 0))); },
  mv(A, x) { return A.map((r) => r[0] * x[0] + r[1] * x[1] + r[2] * x[2]); },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  rot(ax, t) {
    const c = Math.cos(t), s = Math.sin(t);
    if (ax === 0) return [[1, 0, 0], [0, c, -s], [0, s, c]];
    if (ax === 1) return [[c, 0, s], [0, 1, 0], [-s, 0, c]];
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]];
  },
  target(api) {
    const r = Math.PI / 180, p = api.p;
    return { R: this.mul(this.rot(2, p.yaw * r), this.mul(this.rot(1, p.pitch * r), this.rot(0, p.roll * r))), p: [p.x, p.y, p.z] };
  },
  pts(T) { return this.Bp.map((b) => { const v = this.mv(T.R, b); return [v[0] + T.p[0], v[1] + T.p[1], v[2] + T.p[2]]; }); },
  legs(T) { return this.pts(T).map((q, i) => Math.hypot(q[0] - this.A[i][0], q[1] - this.A[i][1], q[2] - this.A[i][2])); },
  Wt(T) {   // 6×6，第 i 行是 ℱᵢᵀ = (aᵢ × ŝᵢ, ŝᵢ)
    return this.pts(T).map((q, i) => { const a = this.A[i], d = [q[0] - a[0], q[1] - a[1], q[2] - a[2]], L = Math.hypot(...d), s = d.map((v) => v / L);
      return [...this.cross(a, s), ...s]; });
  },
  exp6(V) {   // 运动旋量的矩阵指数：返回 {R, p}
    const w = V.slice(0, 3), v = V.slice(3), th = Math.hypot(...w);
    if (th < 1e-12) return { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: v.slice() };
    const k = w.map((x) => x / th), K = [[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]], K2 = this.mul(K, K);
    const R = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + Math.sin(th) * K[i][j] + (1 - Math.cos(th)) * K2[i][j]));
    const G = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? th : 0) + (1 - Math.cos(th)) * K[i][j] + (th - Math.sin(th)) * K2[i][j]));
    return { R, p: this.mv(G, v.map((x) => x / th)) };
  },
  newton(api, Lm) {
    let T = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0.6] };
    const res = [];
    for (let k = 0; k < 30; k++) {
      const L = this.legs(T), r = Lm.map((x, i) => x - L[i]), e = Math.max(...r.map(Math.abs));
      res.push(e);
      if (e < 1e-12) return { T, res, ok: true };
      const W = this.Wt(T);
      let dV = api.la.mv(api.la.pinv(W), r);
      const n = Math.hypot(...dV);
      if (n > 0.5) dV = dV.map((x) => x * 0.5 / n);
      const E = this.exp6(dV);
      T = { R: this.mul(E.R, T.R), p: this.mv(E.R, T.p).map((x, i) => x + E.p[i]) };
    }
    return { T, res, ok: false };
  },
  // 三脚桌
  TA: [90, 210, 330].map((d) => [0.5 * Math.cos(d * Math.PI / 180), 0.5 * Math.sin(d * Math.PI / 180)]),
  FLOOR: [0, 0.03, -0.02],
  table(api) {
    const l = [0.7, api.p.l2, api.p.l3], tops = this.TA.map((c, i) => [c[0], c[1], this.FLOOR[i] + l[i]]);
    const u = [0, 1, 2].map((j) => tops[1][j] - tops[0][j]), v = [0, 1, 2].map((j) => tops[2][j] - tops[0][j]);
    let n = this.cross(u, v); const nn = Math.hypot(...n); n = n.map((x) => x / nn);
    return { tops, n, tilt: Math.acos(Math.min(1, Math.abs(n[2]))) * 180 / Math.PI };
  },
  // 投影（与动画 18.3.1 相同的正交投影）
  proj(v, ox, oy, sc) {
    const az = -55 * Math.PI / 180, el = 17 * Math.PI / 180;
    const rx = -Math.sin(az) * v[0] + Math.cos(az) * v[1], uy = -Math.sin(el) * Math.cos(az) * v[0] - Math.sin(el) * Math.sin(az) * v[1] + Math.cos(el) * v[2];
    return [ox + sc * rx, oy - sc * uy];
  },

  reset(api, s) { s.fk = null; },
  action(id, api, s) {
    if (id !== "fk" || api.scene !== "st") return;
    const T = this.target(api), L = this.legs(T), r = this.newton(api, L);
    const err = Math.max(...T.p.map((x, i) => Math.abs(x - r.T.p[i])), ...T.R.flatMap((row, i) => row.map((x, j) => Math.abs(x - r.T.R[i][j]))));
    s.fk = { res: r.res, ok: r.ok, err, key: JSON.stringify(api.p) };
    if (r.ok && r.res.length - 1 <= 6 && err < 1e-9) api.done("fk");
  },
  readouts(api, s) {
    const f = (v, n) => api.fmt(v, n);
    if (api.scene === "table") {
      const t = this.table(api);
      if (t.tilt < 0.2) api.done("table");
      return [[["三条腿长", "leg lengths"], `0.700, ${f(api.p.l2, 3)}, ${f(api.p.l3, 3)} m`], [["地面高度", "floor heights"], "0, +0.030, −0.020 m"],
              [["桌面倾斜", "table tilt"], f(t.tilt, 2) + "°"], [["桌面中心高度", "top centre height"], f((t.tops[0][2] + t.tops[1][2] + t.tops[2][2]) / 3, 3) + " m"]];
    }
    const T = this.target(api), L = this.legs(T), W = this.Wt(T), det = api.la.det(W);
    const out = L.map((x) => x < this.LMIN - 1e-9 || x > this.LMAX + 1e-9);
    const p = api.p, near = (a, b) => Math.abs(a - b) < 1e-9;
    if (near(p.x, 0.05) && near(p.y, -0.03) && near(p.z, 0.62) && p.roll === 6 && p.pitch === -8 && p.yaw === 12) api.done("ex");
    if (out.some((x) => x)) api.done("stroke");
    if (near(p.x, 0) && near(p.y, 0) && near(p.z, 0.6) && p.roll === 0 && p.pitch === 0 && Math.abs(det) < 0.002) api.done("sing");
    const rows = [[["腿长 l₁～l₃", "legs l₁–l₃"], L.slice(0, 3).map((x) => f(x, 4)).join(", ") + " m"],
                  [["腿长 l₄～l₆", "legs l₄–l₆"], L.slice(3).map((x) => f(x, 4)).join(", ") + " m"],
                  [["行程", "stroke"], out.some((x) => x) ? api.T("超出：腿 ", "out: leg ") + out.map((x, i) => (x ? i + 1 : null)).filter((x) => x).join(", ") : api.T("六条腿都在 0.55～0.85 m 以内", "all six within 0.55–0.85 m")],
                  [["det A", "det A"], f(det, 4)]];
    if (s.fk && s.fk.key === JSON.stringify(api.p)) {
      rows.push([["正解：每步的残差", "forward: residual per step"], s.fk.res.map((e) => e.toExponential(1)).join(", ") + " m"],
                [["正解：迭代次数、与给定位姿之差", "forward: steps, difference from the pose"], `${s.fk.res.length - 1}, ${s.fk.err.toExponential(1)}`]);
    }
    return rows;
  },
  draw(api, s) {
    const { w: W, h: H } = api, css = api.css;
    if (api.scene === "table") {
      const sc = Math.min(W * 0.75, H * 0.85) / 1.3, ox = W * 0.42, oy = H * 0.8, P = (v) => this.proj(v, ox, oy, sc);
      const t = this.table(api);
      this.TA.forEach((c, i) => {
        const fz = this.FLOOR[i], q = [[-0.12, -0.12], [0.12, -0.12], [0.12, 0.12], [-0.12, 0.12]].map((d) => P([c[0] + d[0], c[1] + d[1], fz]));
        const ctx = api.ctx; ctx.fillStyle = css("--grid"); ctx.beginPath(); q.forEach((p, k) => (k ? ctx.lineTo(...p) : ctx.moveTo(...p))); ctx.closePath(); ctx.fill();
        api.line(...P([c[0], c[1], fz]), ...P(t.tops[i]), css("--accent"), 6);
        api.label(api.T(`腿 ${i + 1}`, `leg ${i + 1}`), ...P([c[0], c[1], fz - 0.06]), css("--ink"), 12, "center");
      });
      const ctx = api.ctx; ctx.fillStyle = css("--amber"); ctx.globalAlpha = 0.6; ctx.beginPath(); t.tops.forEach((p, k) => (k ? ctx.lineTo(...P(p)) : ctx.moveTo(...P(p)))); ctx.closePath(); ctx.fill(); ctx.globalAlpha = 1;
      // 水平泡
      const bx = W - 80, by = 80, R = 46;
      api.circle(bx, by, R, css("--panel"), css("--ink")); api.circle(bx, by, 8, null, css("--muted"));
      const k = Math.min(R - 8, 10 * t.tilt);
      const d = Math.hypot(t.n[0], t.n[1]) || 1;
      api.circle(bx - k * t.n[0] / d, by + k * t.n[1] / d, 7, t.tilt < 0.2 ? css("--green") : css("--red"));
      api.label(api.T("水平泡", "spirit level"), bx, by + R + 14, css("--muted"), 12, "center");
      return;
    }
    const sc = Math.min(W * 0.55, H * 0.9) / 1.15, ox = W * 0.36, oy = H * 0.86, P = (v) => this.proj(v, ox, oy, sc);
    const T = this.target(api), q = this.pts(T), L = this.legs(T), ctx = api.ctx;
    const hex = (pts) => { const c = pts.reduce((a, b) => [a[0] + b[0] / pts.length, a[1] + b[1] / pts.length, a[2] + b[2] / pts.length], [0, 0, 0]);
      return pts.map((p, i) => [Math.atan2(p[1] - c[1], p[0] - c[0]), i]).sort((a, b) => a[0] - b[0]).map((x) => pts[x[1]]); };
    ctx.fillStyle = css("--grid"); ctx.beginPath(); hex(this.A).forEach((p, k) => (k ? ctx.lineTo(...P(p)) : ctx.moveTo(...P(p)))); ctx.closePath(); ctx.fill();
    q.forEach((qq, i) => {
      const bad = L[i] < this.LMIN || L[i] > this.LMAX;
      api.line(...P(this.A[i]), ...P(qq), bad ? css("--red") : this.COL[i], bad ? 7 : 5);
      api.label(String(i + 1), ...P(this.A[i].map((x, k) => (k < 2 ? x * 1.15 : x))), this.COL[i], 13, "center");
    });
    ctx.fillStyle = css("--blue"); ctx.globalAlpha = 0.35; ctx.beginPath(); hex(q).forEach((p, k) => (k ? ctx.lineTo(...P(p)) : ctx.moveTo(...P(p)))); ctx.closePath(); ctx.fill(); ctx.globalAlpha = 1;
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]].forEach((e, k) => { const d = this.mv(T.R, e); api.arrow(...P(T.p), ...P(T.p.map((x, j) => x + 0.12 * d[j])), [css("--red"), css("--green"), css("--blue")][k], 2); });
    // 腿长柱条
    const bx = W * 0.72, by = H * 0.82, bh = H * 0.6, Y = (l) => by - bh * (l - 0.5) / 0.4;
    [this.LMIN, this.LMAX].forEach((l) => { api.line(bx - 10, Y(l), bx + 6 * 34, Y(l), css("--muted"), 1, [5, 4]); api.label(api.fmt(l, 2) + " m", bx - 14, Y(l), css("--muted"), 11, "right"); });
    L.forEach((l, i) => { const top = Y(Math.max(0.5, Math.min(0.9, l))); api.rect(bx + 34 * i, top, 24, by - top, this.COL[i]); api.label(String(i + 1), bx + 34 * i + 12, by + 12, css("--ink"), 12, "center"); });
    api.label(api.T("腿长", "leg lengths"), bx + 90, by - bh - 14, css("--ink"), 13, "center");
  },
});
