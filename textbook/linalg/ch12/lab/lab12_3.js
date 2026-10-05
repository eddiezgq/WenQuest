// 实验 12.3 冗余臂的最小动能速度与动力学一致的零空间投影（配 12.3.4 节）。平面三连杆臂，连杆为均匀细杆，
// 长度 (0.40, 0.35, 0.25) m，质量 (4, 2.5, m₃) kg，姿态固定为 (30°, 60°, −45°)，与程序 12.3.1（_arm3.py）相同。
// 场景 1：末端以 0.2 m/s 沿方向 φ 运动，比较欧氏最小范数解 J⁺v 与最小动能解 J⁺_M v = M⁻¹Jᵀ(JM⁻¹Jᵀ)⁻¹v。
// 场景 2：把一个关节速度 w 分成“零空间部分 + 其余部分”，比较动能内积下的投影 I − J⁺_M J 与点积下的投影 I − J⁺J。
WQ.lab({
  title: ["实验 12.3 最小动能的关节速度", "Lab 12.3 Joint velocities of least kinetic energy"],
  goal: ["在动能内积下求冗余机械臂的最小范数关节速度，与普通的最小范数解比较；用动能内积下的正交投影把关节速度分解到零空间，检验动能能否相加。",
         "Find the minimum-norm joint velocity of a redundant arm under the kinetic-energy inner product and compare it with the ordinary minimum-norm solution; split a joint velocity onto the null space with the projection that is orthogonal in that inner product, and check whether the kinetic energies add."],
  scenes: [
    { id: "min", name: ["两种最小范数解", "Two minimum-norm solutions"], hide: ["w1", "w2", "w3"],
      problem: { title: ["末端速度给定，关节速度有无穷多种", "One tool velocity, infinitely many joint velocities"],
                 text: ["三个关节、两个末端方向：满足 Jq̇ = v 的关节速度相差零空间中的向量。按点积最短的不一定最省力，按动能最小的才最省力。改变末端运动的方向 φ 比较两者。",
                        "Three joints, two tool directions: joint velocities with Jq̇ = v differ by null-space vectors. The shortest one in the dot product need not be the cheapest; the one with least kinetic energy is. Change the direction φ and compare."] } },
    { id: "null", name: ["零空间投影", "Null-space projection"], hide: ["phi"],
      problem: { title: ["次任务的运动放进零空间", "Put the secondary motion into the null space"],
                 text: ["关节速度 w 来自次任务（例如避障）。把它分成零空间部分（末端不动）与其余部分。在动能内积下正交分解时，两部分的动能相加正好等于总动能；用点积下的投影则多出一个交叉项。",
                        "A joint velocity w comes from a secondary task (say, avoiding an obstacle). Split it into a null-space part (the tool stays still) and the rest. With the split that is orthogonal in the kinetic-energy inner product the two energies add up to the total; with the dot-product projection a cross term is left over."] } },
  ],
  params: [
    { id: "phi", name: ["末端速度方向 φ（与水平方向的夹角）", "Direction φ of the tool velocity (from horizontal)"], min: 0, max: 355, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "m3", name: ["第 3 根连杆的质量 m₃", "Mass m₃ of link 3"], min: 0.5, max: 4, step: 0.5, value: 1, unit: "kg", digits: 1 },
    { id: "w1", name: ["关节速度 w₁", "Joint velocity w₁"], min: -1, max: 1, step: 0.1, value: 0, unit: "rad/s", digits: 1 },
    { id: "w2", name: ["关节速度 w₂", "Joint velocity w₂"], min: -1, max: 1, step: 0.1, value: 0.5, unit: "rad/s", digits: 1 },
    { id: "w3", name: ["关节速度 w₃", "Joint velocity w₃"], min: -1, max: 1, step: 0.1, value: -0.5, unit: "rad/s", digits: 1 },
  ],
  buttons: [],
  tasks: [
    { id: "half", text: ["在“两种最小范数解”场景中改变方向 φ，使最小动能解比欧氏最小范数解省下一半以上的动能。", "In the first scene change φ until the least-energy solution saves more than half of the kinetic energy of the Euclidean minimum-norm one."],
      demo: { scene: "min", set: { phi: 90, m3: 1 }, press: [] } },
    { id: "best", text: ["保持 m₃ = 1 kg，找出省得最多的方向，使省下的动能超过 85%。", "Keep m₃ = 1 kg and find the direction that saves the most, more than 85%."],
      demo: { scene: "min", set: { phi: 125, m3: 1 }, press: [] } },
    { id: "cross", text: ["在“零空间投影”场景中调整 w，使点积投影的交叉项绝对值超过 0.1 J，同时确认动能内积投影的交叉项仍为零。", "In the null-space scene choose w so that the cross term of the dot-product split exceeds 0.1 J in size, and check that the kinetic-energy split still has no cross term."],
      demo: { scene: "null", set: { w1: -1, w2: -1, w3: -1, m3: 1 }, press: [] } },
  ],
  think: ["方向 φ = 0°（水平）附近两种解非常接近（只差约 0.1%），但并不相同：欧氏最小范数解与零空间只是近似 M-正交。为什么水平方向差别小、竖直方向差别大？把 m₃ 加大到 4 kg，最多能省下的动能变多还是变少？",
          "Near φ = 0° (horizontal) the two solutions are very close (about 0.1% apart) but not equal: the Euclidean minimum-norm solution is only nearly M-orthogonal to the null space. Why is the gap small horizontally and large vertically? With m₃ raised to 4 kg, does the largest saving grow or shrink?"],

  L: [0.40, 0.35, 0.25],
  q: [Math.PI / 6, Math.PI / 3, -Math.PI / 4],
  geom(api) {   // end-point Jacobian (2×3) and mass matrix (3×3); the same formulas as _arm3.py
    const la = api.la, l = this.L, m = [4.0, 2.5, api.p.m3], a = [], E = [];
    let s = 0;
    for (let i = 0; i < 3; i++) { s += this.q[i]; a.push(s); E.push([Math.cos(s), Math.sin(s)]); }
    const jp = (i, d) => {   // Jacobian of the point on link i at distance d from its near end
      const J = [[0, 0, 0], [0, 0, 0]];
      for (let k = 0; k <= i; k++) {
        let rx = d * E[i][0], ry = d * E[i][1];
        for (let j = k; j < i; j++) { rx += l[j] * E[j][0]; ry += l[j] * E[j][1]; }
        J[0][k] = -ry; J[1][k] = rx;
      }
      return J;
    };
    let M = la.zeros(3, 3);
    for (let i = 0; i < 3; i++) {
      const Jc = jp(i, l[i] / 2), I = m[i] * l[i] * l[i] / 12, jv = [0, 1, 2].map((k) => (k <= i ? 1 : 0));
      const A = la.mul(la.T(Jc), Jc);
      M = M.map((r, p) => r.map((x, q) => x + m[i] * A[p][q] + I * jv[p] * jv[q]));
    }
    const P = [[0, 0]];
    for (let i = 0; i < 3; i++) P.push([P[i][0] + l[i] * E[i][0], P[i][1] + l[i] * E[i][1]]);
    return { J: jp(2, l[2]), M, P };
  },
  solve(A, b) {   // small dense solve by Gaussian elimination with partial pivoting
    const n = b.length, M = A.map((r, i) => r.concat([b[i]]));
    for (let k = 0; k < n; k++) {
      let p = k; for (let i = k + 1; i < n; i++) if (Math.abs(M[i][k]) > Math.abs(M[p][k])) p = i;
      [M[k], M[p]] = [M[p], M[k]];
      for (let i = k + 1; i < n; i++) { const f = M[i][k] / M[k][k]; for (let j = k; j <= n; j++) M[i][j] -= f * M[k][j]; }
    }
    const x = Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let t = M[i][n]; for (let j = i + 1; j < n; j++) t -= M[i][j] * x[j]; x[i] = t / M[i][i]; }
    return x;
  },
  gpinv(api, J, W) {   // W⁻¹Jᵀ(JW⁻¹Jᵀ)⁻¹ as a 3×2 matrix (W = I gives the ordinary pseudoinverse)
    const la = api.la, X = la.T([0, 1].map((r) => this.solve(W, J[r])));   // columns W⁻¹Jᵀ
    const S = la.mul(J, X), Si = [this.solve(S, [1, 0]), this.solve(S, [0, 1])];   // S⁻¹ columns
    return la.mul(X, la.T(Si));
  },
  reset(api, s) {
    const la = api.la, g = this.geom(api);
    s.g = g;
    const ke = (w) => 0.5 * la.dot(w, la.mv(g.M, w));
    s.ke = ke;
    const Jp = this.gpinv(api, g.J, la.eye(3)), JpM = this.gpinv(api, g.J, g.M);
    if (api.scene === "min") {
      const ph = api.p.phi * Math.PI / 180, v = [0.2 * Math.cos(ph), 0.2 * Math.sin(ph)];
      s.v = v; s.qe = la.mv(Jp, v); s.qm = la.mv(JpM, v);
      s.kee = ke(s.qe); s.kem = ke(s.qm); s.save = 1 - s.kem / s.kee;
    } else {
      const w = [api.p.w1, api.p.w2, api.p.w3];
      const split = (Jg) => { const t = la.mv(la.mul(Jg, g.J), w), n = w.map((x, i) => x - t[i]); return { n, t, cross: la.dot(t, la.mv(g.M, n)) }; };
      s.w = w; s.kw = ke(w); s.sM = split(JpM); s.sE = split(Jp);
    }
  },
  readouts(api, s) {
    if (!s.g) return [];
    const f = api.fmt, v3 = (x) => "(" + x.map((t) => f(t, 3)).join(", ") + ")";
    if (api.scene === "min") {
      if (s.save >= 0.5) api.done("half");
      if (api.p.m3 === 1 && s.save >= 0.85) api.done("best");
      return [[["欧氏最小范数解 J⁺v / (rad/s)", "Euclidean minimum norm J⁺v / (rad/s)"], v3(s.qe)],
              [["  它的长度、动能", "  its length, kinetic energy"], f(api.la.norm(s.qe), 3) + ", " + f(s.kee, 4) + " J"],
              [["最小动能解 J⁺_M v / (rad/s)", "Least kinetic energy J⁺_M v / (rad/s)"], v3(s.qm)],
              [["  它的长度、动能", "  its length, kinetic energy"], f(api.la.norm(s.qm), 3) + ", " + f(s.kem, 4) + " J"],
              [["省下的动能", "Kinetic energy saved"], f(100 * s.save, 1) + "%"]];
    }
    const zero = Math.abs(s.sM.cross) < 1e-12;
    if (Math.abs(s.sE.cross) > 0.1 && zero) api.done("cross");
    const v2 = (x) => "(" + x.map((t) => f(t, 2)).join(", ") + ")";
    return [[["w 的动能", "Kinetic energy of w"], f(s.kw, 4) + " J"],
            [["动能内积投影：零空间部分", "KE projection: null part"], v2(s.sM.n)],
            [["  其余部分", "  the rest"], v2(s.sM.t)],
            [["  两部分动能之和", "  sum of the two energies"], f(s.ke(s.sM.n) + s.ke(s.sM.t), 4) + " J"],
            [["  交叉项", "  cross term"], (zero ? "< 1e-12" : s.sM.cross.toExponential(1)) + " J"],
            [["点积投影：零空间部分", "Dot-product projection: null part"], v2(s.sE.n)],
            [["  其余部分", "  the rest"], v2(s.sE.t)],
            [["  两部分动能之和", "  sum of the two energies"], f(s.ke(s.sE.n) + s.ke(s.sE.t), 4) + " J"],
            [["  交叉项", "  cross term"], f(s.sE.cross, 4) + " J"]];
  },
  bars(api, x, y, w, h, sets, cols, names, top) {   // grouped signed bars for three joints
    const ink = api.css("--ink"), mu = api.css("--muted");
    api.rect(x, y, w, h, null, api.css("--grid"));
    const y0 = y + h / 2, sc = (h / 2 - 8) / top, gw = w / 3, bw = gw * 0.8 / sets.length;
    api.line(x, y0, x + w, y0, mu, 1);
    for (let j = 0; j < 3; j++) {
      sets.forEach((v, k) => { const hh = v[j] * sc, bx = x + j * gw + gw * 0.1 + k * bw;
        api.rect(bx, hh >= 0 ? y0 - hh : y0, bw * 0.9, Math.abs(hh), cols[k]); });
      api.label(api.T(`关节 ${j + 1}`, `joint ${j + 1}`), x + (j + 0.5) * gw, y + h + 16, ink, 12, "center");
    }
    names.forEach((n, k) => { api.rect(x + 8, y + h + 30 + 18 * k, 12, 10, cols[k]); api.label(n, x + 26, y + h + 39 + 18 * k, ink, 12); });
  },
  draw(api, s) {
    if (!s.g) return;
    const { w, h } = api, ink = api.css("--ink"), red = api.css("--red");
    const g = s.g, sc = Math.min(w * 0.42, h * 0.8) / 1.0, ox = 40, oy = h - 40;
    const X = (p) => [ox + sc * p[0], oy - sc * p[1]];
    api.line(ox - 25, oy + 6, ox + 25, oy + 6, ink, 3);
    for (let i = 0; i < 3; i++) { const a = X(g.P[i]), b = X(g.P[i + 1]); api.line(a[0], a[1], b[0], b[1], ink, 7); }
    for (let i = 0; i < 3; i++) { const a = X(g.P[i]); api.circle(a[0], a[1], 5, "#fff", ink); }
    const e = X(g.P[3]);
    const bx = w * 0.52, bw = w * 0.45, by = 40, bh = h - 150;
    if (api.scene === "min") {
      api.arrow(e[0], e[1], e[0] + sc * s.v[0], e[1] - sc * s.v[1], red, 3);
      api.label("v", e[0] + sc * s.v[0] + 6, e[1] - sc * s.v[1], red, 14);
      const top = 1.05 * Math.max(0.5, ...s.qe.map(Math.abs), ...s.qm.map(Math.abs));
      this.bars(api, bx, by, bw, bh, [s.qe, s.qm], [api.css("--blue"), api.css("--accent")],
        [api.T("欧氏最小范数", "Euclidean minimum norm"), api.T("最小动能", "least kinetic energy")], top);
      api.label(api.T("关节速度 / (rad/s)", "joint velocity / (rad/s)"), bx, by - 10, api.css("--muted"), 12);
    } else {
      const top = 1.05 * Math.max(0.5, ...[...s.w, ...s.sM.n, ...s.sE.n].map(Math.abs));
      this.bars(api, bx, by, bw, bh, [s.w, s.sM.n, s.sE.n], [api.css("--muted"), api.css("--accent"), api.css("--blue")],
        [api.T("w", "w"), api.T("零空间部分（动能内积）", "null part (KE inner product)"), api.T("零空间部分（点积）", "null part (dot product)")], top);
      api.label(api.T("关节速度 / (rad/s)", "joint velocity / (rad/s)"), bx, by - 10, api.css("--muted"), 12);
    }
  },
});
