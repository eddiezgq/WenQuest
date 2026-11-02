// 实验 21.3 格什戈林圆盘与特征值（配 21.3 节）。
// 矩阵 A(t) = diag(A) + t·(A − diag(A))：t 把所有非对角元一起放大或缩小；再做对角相似变换 D⁻¹A(t)D（特征值不变）。
// 行圆盘：|z − aᵢᵢ| ≤ Σⱼ≠ᵢ |aᵢⱼ| dⱼ/dᵢ；列圆盘对 Aᵀ 同样。特征值用法捷耶夫–勒韦里耶求特征多项式、杜兰德–肯纳迭代求根
// （对称化后可用雅可比法的热模型与 AGV 编队直接用 eigSym），与程序 21.3.1 一致。
// 三个场景：算例 21.3.1（D = diag(1, 1, s)）；三个关节电机的六节点热模型（同 21.3 节，D = diag(1, s, 1, s, 1, s)）；
// 四辆 AGV 纵向编队的速度耦合矩阵 A = −0.5I − tL（相邻两车按速度差互相修正，增益 t 同时出现在对角元和非对角元中，D = diag(1, s, s, 1)）。
WQ.lab({
  title: ["实验 21.3 格什戈林圆盘与特征值", "Lab 21.3 Gershgorin discs and eigenvalues"],
  goal: ["改变非对角元的大小和对角缩放，看行圆盘、列圆盘怎样圈住特征值；不求特征值，就判断热模型和 AGV 编队是否稳定、最慢的模态有多慢。",
         "Change the size of the off-diagonal entries and the diagonal scaling and watch the row and column discs enclose the eigenvalues; decide, without computing eigenvalues, whether the thermal model and the AGV platoon are stable and how slow the slowest mode is."],
  scenes: [
    { id: "ex", name: ["算例 21.3.1", "Example 21.3.1"],
      problem: { title: ["问题：不解三次方程，能说出特征值在哪里吗？", "Problem: where are the eigenvalues, without solving the cubic?"],
                 text: ["A = [[10, 1, −0.5], [0.4, 4, 0.8], [0.6, 0.2, −2]]。对角元很大、非对角元很小。特征值离对角元有多远？",
                        "A = [[10, 1, −0.5], [0.4, 4, 0.8], [0.6, 0.2, −2]]. The diagonal is large, the off-diagonal small. How far are the eigenvalues from the diagonal entries?"] } },
    { id: "heat", robot: true, name: ["关节电机热模型", "Joint-motor thermal model"],
      problem: { title: ["机器人问题：三个关节电机过载后要冷却多久？", "Robot problem: how long do three joint motors take to cool after an overload?"],
                 text: ["肩、肘、腕三台电机各有绕组和外壳两个节点，相邻外壳经连杆导热，ẋ = Ax，A = −C⁻¹G（单位 10⁻³ s⁻¹）。不求特征值，能否证明温度一定回落，并估计最慢的时间常数？",
                        "Shoulder, elbow and wrist motors each have a winding and a housing node; neighbouring housings exchange heat through the links. ẋ = Ax, A = −C⁻¹G (units 10⁻³ s⁻¹). Without eigenvalues, can we prove the temperatures decay and bound the slowest time constant?"] } },
    { id: "agv", robot: true, name: ["AGV 纵向编队", "AGV platoon"],
      problem: { title: ["机器人问题：编队的速度修正会不会越调越乱？", "Robot problem: can platoon speed corrections run away?"],
                 text: ["四辆 AGV 排成一列，每辆车按与前后车的速度差修正自己的速度（增益 t），自身还有 0.5 s⁻¹ 的速度阻尼。速度偏差满足 v̇ = Av。增益加大会失稳吗？",
                        "Four AGVs run in a line; each corrects its speed by the speed difference to its neighbours (gain t) and has 0.5 s⁻¹ of damping. Speed deviations obey v̇ = Av. Can a larger gain destabilize the platoon?"] } },
  ],
  params: [
    { id: "t", name: ["非对角元的倍数 t（AGV 场景为修正增益）", "Off-diagonal factor t (gain in the AGV scene)"], min: 0, max: 3, step: 0.05, value: 1, digits: 2 },
    { id: "s", name: ["对角缩放 s", "Diagonal scaling s"], min: 0.2, max: 1, step: 0.002, value: 1, digits: 3 },
    { id: "col", name: ["圆盘（0 行，1 列，2 两者）", "Discs (0 rows, 1 columns, 2 both)"], min: 0, max: 2, step: 1, value: 0, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "sep", text: ["算例，t = 1、s = 1：三个行圆盘互不相交。读出每个特征值所在的区间。", "Example, t = 1, s = 1: the three row discs are disjoint. Read off an interval for each eigenvalue."],
      demo: { scene: "ex", set: { t: 1, s: 1, col: 0 }, press: [] } },
    { id: "zero", text: ["算例：把 t 调到 0，特征值在哪里？", "Example: set t to 0. Where are the eigenvalues?"],
      demo: { scene: "ex", set: { t: 0, s: 1, col: 0 }, press: [] } },
    { id: "overlap", text: ["算例，s = 1：加大 t，直到有两个圆盘相交。此时还能断定每个圆盘里各有一个特征值吗？", "Example, s = 1: increase t until two discs overlap. Can you still say each disc holds one eigenvalue?"],
      demo: { scene: "ex", set: { t: 2.5, s: 1, col: 0 }, press: [] } },
    { id: "stable", robot: true, text: ["热模型，t = 1：原来的绕组圆盘碰到原点。找一个缩放 s，使所有行圆盘都在左半平面。", "Thermal model, t = 1: the winding discs touch 0. Find a scaling s that puts every row disc in the left half-plane."],
      demo: { scene: "heat", set: { t: 1, s: 0.9, col: 0 }, press: [] } },
    { id: "best", robot: true, text: ["热模型，t = 1：调 s，使圆盘的最右端尽量靠左（小于 −1.80），与最慢的特征值比较，换算成时间常数。", "Thermal model, t = 1: tune s to push the rightmost disc point as far left as possible (below −1.80); compare it with the slowest eigenvalue and convert to a time constant."],
      demo: { scene: "heat", set: { t: 1, s: 0.954, col: 0 }, press: [] } },
    { id: "agv", robot: true, text: ["AGV 编队：把增益 t 加到 3。圆盘还都在左半平面吗？最慢的衰减率由什么决定？", "AGV platoon: raise the gain t to 3. Are all discs still in the left half-plane? What sets the slowest decay rate?"],
      demo: { scene: "agv", set: { t: 3, s: 1, col: 0 }, press: [] } },
  ],
  think: ["热模型中，绕组那一行的对角元与非对角元之和恰为零（热量守恒，绕组只能经外壳散热），圆盘必然经过原点。为什么缩放 s < 1（把外壳温度按比例 s 计）能把它推开？最优的 s 与最慢模态的特征向量有什么关系？",
          "In the thermal model the winding row sums to zero (heat is conserved; the winding loses heat only through the housing), so its disc passes through 0. Why does a scaling s < 1 (measuring housing temperature in units of s) push it away? How is the best s related to the eigenvector of the slowest mode?"],

  EX: [[10, 1, -0.5], [0.4, 4, 0.8], [0.6, 0.2, -2]],
  heatA() {                                       // 单位 10⁻³ s⁻¹
    const CW = 50, CH = 500, gwh = 2, gha = 1, ghh = 0.5, cap = [CW, CH, CW, CH, CW, CH], G = [...Array(6)].map(() => Array(6).fill(0));
    const link = (i, j, g) => { G[i][i] += g; G[j][j] += g; G[i][j] -= g; G[j][i] -= g; };
    for (let k = 0; k < 3; k++) { link(2 * k, 2 * k + 1, gwh); G[2 * k + 1][2 * k + 1] += gha; }
    for (let k = 0; k < 2; k++) link(2 * k + 1, 2 * k + 3, ghh);
    return { A: G.map((r, i) => r.map((g) => -1000 * g / cap[i])), cap };
  },
  agvA(t) {                                       // A = −cI − tL，L 为一列四辆车的拉普拉斯矩阵（相邻两车按速度差互相修正）
    const n = 4, c = 0.5, A = [...Array(n)].map(() => Array(n).fill(0));
    for (let i = 0; i < n; i++) { A[i][i] = -c; if (i > 0) { A[i][i] -= t; A[i][i - 1] = t; } if (i < n - 1) { A[i][i] -= t; A[i][i + 1] = t; } }
    return A; },
  eigGeneral(A) {                                 // 法捷耶夫–勒韦里耶求特征多项式，杜兰德–肯纳迭代求全部根（复数）
    const n = A.length, c = [1]; let M = A.map((r) => r.map(() => 0));
    for (let k = 1; k <= n; k++) {
      const AM = A.map((r, i) => r.map((_, j) => r.reduce((s, a, l) => s + a * (M[l][j] + (l === j ? c[k - 1] : 0)), 0)));
      M = AM.map((r, i) => r.map((x, j) => x));                 // M_k = A(M_{k−1} + c_{k−1} I)
      const tr = M.reduce((s, r, i) => s + r[i], 0);
      c.push(-tr / k);
    }
    const p = (z) => c.reduce((acc, ck) => [acc[0] * z[0] - acc[1] * z[1] + ck, acc[0] * z[1] + acc[1] * z[0]], [0, 0]);
    let R = [...Array(n)].map((_, k) => { const a = 2 * Math.PI * k / n + 0.4; const r = 1 + Math.max(...c.map(Math.abs)); return [r * Math.cos(a), r * Math.sin(a)]; });
    for (let it = 0; it < 500; it++) {
      let mv = 0;
      R = R.map((z, i) => {
        let d = [1, 0];
        R.forEach((w, j) => { if (j !== i) { const q = [z[0] - w[0], z[1] - w[1]]; d = [d[0] * q[0] - d[1] * q[1], d[0] * q[1] + d[1] * q[0]]; } });
        const pz = p(z), den = d[0] * d[0] + d[1] * d[1] || 1e-300, step = [(pz[0] * d[0] + pz[1] * d[1]) / den, (pz[1] * d[0] - pz[0] * d[1]) / den];
        mv = Math.max(mv, Math.hypot(step[0], step[1]));
        return [z[0] - step[0], z[1] - step[1]];
      });
      if (mv < 1e-13) break;
    }
    return R.map((z) => [z[0], Math.abs(z[1]) < 1e-9 ? 0 : z[1]]);
  },
  model(api) {
    const t = api.p.t, s = api.p.s, sc = api.scene;
    let A0, d, eig;
    if (sc === "ex") { A0 = this.EX; d = [1, 1, s]; }
    else if (sc === "heat") { A0 = this.heatA().A; d = [1, s, 1, s, 1, s]; }
    else { A0 = this.agvA(t); d = [1, s, s, 1]; }
    const n = A0.length, At = sc === "agv" ? A0 : A0.map((r, i) => r.map((a, j) => (i === j ? a : t * a)));
    if (sc === "heat") {                          // C^{1/2} A C^{−1/2} 对称
      const cap = this.heatA().cap, S = At.map((r, i) => r.map((a, j) => a * Math.sqrt(cap[i] / cap[j])));
      const Ssym = S.map((r, i) => r.map((a, j) => (a + S[j][i]) / 2));
      eig = api.la.eigSym(Ssym).values.map((v) => [v, 0]);
    } else if (sc === "agv") eig = api.la.eigSym(At).values.map((v) => [v, 0]);
    else eig = this.eigGeneral(At);
    const B = At.map((r, i) => r.map((a, j) => a * d[j] / d[i]));           // D⁻¹ A D
    const ctr = B.map((r, i) => r[i]);
    const rrow = B.map((r, i) => r.reduce((acc, a, j) => acc + (j === i ? 0 : Math.abs(a)), 0));
    const rcol = B.map((_, j) => B.reduce((acc, r, i) => acc + (i === j ? 0 : Math.abs(r[j])), 0));
    const use = api.p.col === 1 ? rcol : rrow;
    const right = Math.max(...ctr.map((c, i) => c + use[i]));
    // 圆盘之间是否两两不相交（按当前选择的行/列圆盘）
    let disjoint = true;
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (Math.abs(ctr[i] - ctr[j]) <= use[i] + use[j]) disjoint = false;
    const inside = eig.every((z) => ctr.some((c, i) => Math.hypot(z[0] - c, z[1]) <= rrow[i] + 1e-9) && ctr.some((c, i) => Math.hypot(z[0] - c, z[1]) <= rcol[i] + 1e-9));
    return { n, ctr, rrow, rcol, use, right, disjoint, eig, inside, slow: Math.max(...eig.map((z) => z[0])) };
  },
  reset(api, s) {},
  readouts(api, s) {
    const m = this.model(api), f = api.fmt, sc = api.scene, unit = sc === "heat" ? " ×10⁻³ s⁻¹" : (sc === "agv" ? " s⁻¹" : "");
    if (sc === "ex" && Math.abs(api.p.t - 1) < 1e-9 && Math.abs(api.p.s - 1) < 1e-9 && api.p.col !== 1 && m.disjoint) api.done("sep");
    if (sc === "ex" && api.p.t === 0) api.done("zero");
    if (sc === "ex" && Math.abs(api.p.s - 1) < 1e-9 && !m.disjoint && api.p.t > 1) api.done("overlap");
    if (sc === "heat" && Math.abs(api.p.t - 1) < 1e-9 && api.p.col !== 1 && m.right < 0) api.done("stable");
    if (sc === "heat" && Math.abs(api.p.t - 1) < 1e-9 && api.p.col !== 1 && m.right < -1.80) api.done("best");
    if (sc === "agv" && api.p.t >= 2.95 && m.right < 0) api.done("agv");
    const eigs = m.eig.slice().sort((a, b) => a[0] - b[0]).map((z) => z[1] ? f(z[0], 3) + (z[1] > 0 ? "+" : "−") + f(Math.abs(z[1]), 3) + "i" : f(z[0], 3)).join(", ");
    const rows = [[["圆心（对角元）", "Centres (diagonal)"], m.ctr.map((c) => f(c, 3)).join(", ") + unit],
                  [["行圆盘半径", "Row-disc radii"], m.rrow.map((r) => f(r, 3)).join(", ")],
                  [["列圆盘半径", "Column-disc radii"], m.rcol.map((r) => f(r, 3)).join(", ")],
                  [["特征值", "Eigenvalues"], eigs + unit],
                  [["所选圆盘的最右端", "Rightmost point of the chosen discs"], f(m.right, 4) + unit + (m.right < 0 ? api.T("（全部在左半平面）", " (all in the left half-plane)") : api.T("（有圆盘碰到或越过虚轴）", " (some disc touches or crosses the imaginary axis)"))],
                  [["所选圆盘两两不相交", "Chosen discs pairwise disjoint"], m.disjoint ? api.T("是：每个圆盘恰含一个特征值", "yes: each disc holds exactly one eigenvalue") : api.T("否", "no")],
                  [["特征值都在行圆盘之并与列圆盘之并中", "Eigenvalues in both unions"], m.inside ? api.T("是", "yes") : api.T("否", "no")]];
    if (sc === "heat") rows.push([["最慢模态的时间常数 / 圆盘给出的上界", "Slowest time constant / disc bound"],
      f(-1000 / m.slow, 0) + " s / " + (m.right < 0 ? f(-1000 / m.right, 0) + " s" : "—")]);
    return rows;
  },
  draw(api, s) {
    const m = this.model(api), { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink"), sc = api.scene;
    const cols = [api.css("--red"), api.css("--green"), api.css("--blue"), api.css("--amber"), api.css("--accent"), api.css("--ink")];
    const panel = (bx, by, bw, bh, xlo, xhi, ylim, title, showAxisLabels) => {
      const k = Math.min(bw / (xhi - xlo), bh / (2 * ylim)), cx = bx + bw / 2 - (xlo + xhi) / 2 * k, cy = by + bh / 2;
      const X = (x) => cx + x * k, Y = (y) => cy - y * k, inBox = (px, py) => px >= bx && px <= bx + bw && py >= by && py <= by + bh;
      api.rect(bx, by, bw, bh, null, mu);
      api.line(bx, cy, bx + bw, cy, mu, 1);
      if (X(0) >= bx && X(0) <= bx + bw) api.line(X(0), by, X(0), by + bh, ink, 1.5);
      const ring = (c, r, col, width, dash) => {
        let prev = null;
        for (let q = 0; q <= 120; q++) {
          const a = 2 * Math.PI * q / 120, p = [X(c + r * Math.cos(a)), Y(r * Math.sin(a))];
          if (prev && inBox(prev[0], prev[1]) && inBox(p[0], p[1])) api.line(prev[0], prev[1], p[0], p[1], col, width, dash);
          prev = p;
        }
      };
      m.ctr.forEach((c, i) => {
        const col = cols[sc === "heat" ? (i % 2) * 2 : i % cols.length];
        if (api.p.col !== 1) ring(c, m.rrow[i], col, 2);
        if (api.p.col !== 0) ring(c, m.rcol[i], col, 1.2, [5, 4]);
        if (inBox(X(c), Y(0))) { api.line(X(c) - 4, Y(0) - 4, X(c) + 4, Y(0) + 4, col, 1.5); api.line(X(c) - 4, Y(0) + 4, X(c) + 4, Y(0) - 4, col, 1.5); }
      });
      m.eig.forEach((z) => { if (inBox(X(z[0]), Y(z[1]))) api.circle(X(z[0]), Y(z[1]), 4.5, api.css("--amber"), ink); });
      api.label(title, bx + 6, by + 14, mu, 11);
      if (showAxisLabels) { api.label(f0(xlo), bx + 2, cy + 14, mu, 10); api.label(f0(xhi), bx + bw - 30, cy + 14, mu, 10); }
    };
    const f0 = (x) => api.fmt(x, Math.abs(x) < 10 ? 1 : 0);
    const lo = Math.min(...m.ctr.map((c, i) => c - Math.max(m.rrow[i], m.rcol[i])), ...m.eig.map((z) => z[0])) - 0.5;
    const hi = Math.max(...m.ctr.map((c, i) => c + Math.max(m.rrow[i], m.rcol[i])), ...m.eig.map((z) => z[0]), 0) + 0.5;
    const yl = Math.max(...m.rrow, ...m.rcol, ...m.eig.map((z) => Math.abs(z[1])), 1) * 1.1;
    if (sc === "heat") {
      panel(10, 10, w * 0.58, h - 40, lo, hi, yl, api.T("复平面（单位 10⁻³ s⁻¹）", "complex plane (10⁻³ s⁻¹)"), true);
      panel(w * 0.6 + 10, 10, w * 0.4 - 20, h - 40, -6, 1, 2.6, api.T("原点附近放大", "zoom near 0"), true);
    } else panel(10, 10, w - 20, h - 40, lo, hi, yl, api.T("复平面：实线为行圆盘，虚线为列圆盘，黄点为特征值", "complex plane: solid row discs, dashed column discs, yellow eigenvalues"), true);
    api.label(api.T("× 圆心（对角元）；t = ", "× centres (diagonal); t = ") + api.fmt(api.p.t, 2) + "，s = " + api.fmt(api.p.s, 3), 10, h - 10, mu, 11);
  },
});
