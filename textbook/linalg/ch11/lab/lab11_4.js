// 实验 11.4 一步一步做 QR 分解（配 11.2～11.4 节）。三种方法作用于同一个 5×3 矩阵：豪斯霍尔德（每步一次反射，消去一列对角线以下）、
// 吉文斯（每步一次旋转，消去一个元素）、经典与修正格拉姆–施密特（每步正交化一列）。矩阵 1：一般的矩阵；矩阵 2：列几乎相关的矩阵
// （劳赫利型：[1 1 1; ε 0 0; 0 ε 0; 0 0 ε; 0 0 0]，ε = 10⁻⁸）。读出 ‖QᵀQ − I‖ 与 ‖QR − A‖（均为弗罗贝尼乌斯范数）。
WQ.lab({
  title: ["实验 11.4 一步一步做 QR 分解", "Lab 11.4 QR factorization step by step"],
  goal: ["用豪斯霍尔德反射、吉文斯旋转和两种格拉姆–施密特一步一步把同一个矩阵化为 QR，观察零元怎样出现，数运算的步数，比较各种方法得到的 Q 是否正交。",
         "Factor the same matrix as QR step by step with Householder reflections, Givens rotations and two forms of Gram–Schmidt; watch the zeros appear, count the steps, and compare how orthogonal each Q is."],
  scenes: [
    { id: "hh", name: ["豪斯霍尔德反射", "Householder"],
      problem: { title: ["每一步反射，消去一整列", "One reflection clears a whole column"],
                 text: ["第 k 步用一个反射 H_k 把第 k 列对角线以下的元素一次全部变为零。按“下一步”看矩阵的变化。", "Step k applies one reflection H_k that zeroes everything below the diagonal in column k. Press Next step to watch."] } },
    { id: "giv", name: ["吉文斯旋转", "Givens"],
      problem: { title: ["每一步旋转，消去一个元素", "One rotation clears one entry"],
                 text: ["每一步在两行之间做一次平面旋转，把一个元素变为零。数一数一共要转几次。", "Each step rotates two rows to zero one entry. Count how many rotations it takes."] } },
    { id: "gs", name: ["经典格拉姆–施密特", "Classical Gram–Schmidt"],
      problem: { title: ["逐列正交化", "Orthogonalize column by column"],
                 text: ["每一步把一列减去它在已有 q 上的投影再单位化。对列几乎相关的矩阵 2，看 Q 还正交吗。", "Each step subtracts from a column its projections onto the q's so far and normalizes. For the nearly dependent matrix 2, is Q still orthogonal?"] } },
    { id: "mgs", name: ["修正格拉姆–施密特", "Modified Gram–Schmidt"],
      problem: { title: ["边减边更新", "Update as you subtract"],
                 text: ["与经典法只差一点：每减去一个投影，下一个系数就用已经减过的向量来算。对矩阵 2 比较两者的正交性。", "One small change from the classical form: after each projection is removed, the next coefficient is computed from the updated vector. Compare the orthogonality on matrix 2."] } },
  ],
  params: [{ id: "m", name: ["矩阵编号（1：一般；2：列几乎相关）", "Matrix (1: generic; 2: nearly dependent columns)"], min: 1, max: 2, step: 1, value: 1, digits: 0 }],
  buttons: [{ id: "step", name: ["下一步", "Next step"], primary: true }, { id: "restart", name: ["从头开始", "Start over"] }],
  tasks: [
    { id: "hh", text: ["用豪斯霍尔德反射把矩阵 1 化为上三角，读出用了几次反射。", "Reduce matrix 1 to upper triangular with Householder reflections; how many reflections?"],
      demo: { scene: "hh", set: { m: 1 }, press: ["restart", "step", "step", "step"] } },
    { id: "giv", text: ["用吉文斯旋转把矩阵 1 化为上三角，读出旋转的次数，与反射的次数比较。", "Reduce matrix 1 with Givens rotations; compare the number of rotations with the number of reflections."],
      demo: { scene: "giv", set: { m: 1 }, press: ["restart", "step", "step", "step", "step", "step", "step", "step", "step", "step"] } },
    { id: "loss", text: ["对矩阵 2 用经典格拉姆–施密特做完，读出 ‖QᵀQ − I‖，再与豪斯霍尔德的结果比较。", "Finish classical Gram–Schmidt on matrix 2; read ‖QᵀQ − I‖ and compare with Householder."],
      demo: { scene: "gs", set: { m: 2 }, press: ["restart", "step", "step", "step"] } },
    { id: "mgs", text: ["对矩阵 2 用修正格拉姆–施密特做完，确认 ‖QᵀQ − I‖ 小于 10⁻⁶，与经典法比较。", "Finish modified Gram–Schmidt on matrix 2; check that ‖QᵀQ − I‖ is below 10⁻⁶ and compare with the classical form."],
      demo: { scene: "mgs", set: { m: 2 }, press: ["restart", "step", "step", "step"] } },
  ],
  think: ["吉文斯旋转比豪斯霍尔德反射多用了很多步，它在什么场合更合适？（提示：矩阵已经几乎是上三角，或者新的一行数据到来时。）",
          "Givens needs many more steps than Householder. When is it the better choice? (Hint: a nearly triangular matrix, or one new row of data arriving.)"],

  A(api) {
    if (api.p.m === 1) return [[2, 1, 3], [1, 4, 0], [2, -2, 1], [1, 0, 2], [4, 1, 1]];
    const e = 1e-8;
    return [[1, 1, 1], [e, 0, 0], [0, e, 0], [0, 0, e], [0, 0, 0]];
  },
  reset(api, s) {
    const A = this.A(api), m = A.length, n = A[0].length;
    s.A = A; s.R = A.map((r) => r.slice()); s.Q = api.la.eye(m); s.k = 0; s.done = false; s.count = 0;
    s.gq = []; s.gr = api.la.zeros(n, n);                  // Gram–Schmidt: columns of Q found so far, R
    s.todo = [];                                            // Givens: list of (row i, column j) to zero, column by column, bottom up
    for (let j = 0; j < n; j++) for (let i = m - 1; i > j; i--) s.todo.push([i, j]);
  },
  action(id, api, s) {
    if (id === "restart") { this.reset(api, s); return; }
    if (id !== "step" || s.done) return;
    const m = s.A.length, n = s.A[0].length;
    if (api.scene === "hh") {
      const k = s.k, x = s.R.slice(k).map((r) => r[k]), nx = Math.hypot(...x), v = x.slice();
      v[0] += (x[0] >= 0 ? 1 : -1) * nx;
      const vv = v.reduce((t, a) => t + a * a, 0);
      if (vv > 0) {
        for (let j = 0; j < n; j++) { const d = v.reduce((t, a, i) => t + a * s.R[k + i][j], 0) * 2 / vv; v.forEach((a, i) => { s.R[k + i][j] -= d * a; }); }
        for (let i = 0; i < m; i++) { const d = v.reduce((t, a, l) => t + a * s.Q[i][k + l], 0) * 2 / vv; v.forEach((a, l) => { s.Q[i][k + l] -= d * a; }); }
      }
      s.k++; s.count++; if (s.k >= n) s.done = true;
    } else if (api.scene === "giv") {
      const [i, j] = s.todo[s.k], a = s.R[i - 1][j], b = s.R[i][j], r = Math.hypot(a, b);
      if (r > 0) {
        const c = a / r, sn = b / r;
        for (let l = 0; l < n; l++) { const u = s.R[i - 1][l], w = s.R[i][l]; s.R[i - 1][l] = c * u + sn * w; s.R[i][l] = -sn * u + c * w; }
        for (let l = 0; l < m; l++) { const u = s.Q[l][i - 1], w = s.Q[l][i]; s.Q[l][i - 1] = c * u + sn * w; s.Q[l][i] = -sn * u + c * w; }
      }
      s.R[i][j] = 0; s.k++; s.count++; if (s.k >= s.todo.length) s.done = true;
    } else {
      const j = s.k, a = s.A.map((r) => r[j]), v = a.slice();
      const mod = api.scene === "mgs";
      s.gq.forEach((q, i) => { const rij = api.la.dot(q, mod ? v : a); s.gr[i][j] = rij; q.forEach((x, l) => { v[l] -= rij * x; }); });   // classical: coefficients from the original column; modified: from the updated v
      const nv = api.la.norm(v); s.gr[j][j] = nv; s.gq.push(v.map((x) => x / nv));
      s.k++; s.count++; if (s.k >= n) s.done = true;
    }
  },
  errs(api, s) {
    const la = api.la, m = s.A.length, n = s.A[0].length;
    let Q, R;
    if (api.scene === "gs" || api.scene === "mgs") {
      if (!s.gq.length) return null;
      Q = la.T(s.gq); R = s.gr.slice(0, s.gq.length).map((r) => r.slice());
      const QtQ = la.mul(la.T(Q), Q);
      const oe = Math.sqrt(QtQ.reduce((t, r, i) => t + r.reduce((u, x, j) => u + (x - (i === j ? 1 : 0)) ** 2, 0), 0));
      if (!s.done) return { oe };
      const QR = la.mul(Q, R);
      return { oe, re: la.fro(la.sub(QR, s.A)) };
    }
    const QtQ = la.mul(la.T(s.Q), s.Q);
    const oe = Math.sqrt(QtQ.reduce((t, r, i) => t + r.reduce((u, x, j) => u + (x - (i === j ? 1 : 0)) ** 2, 0), 0));
    return { oe, re: la.fro(la.sub(la.mul(s.Q, s.R), s.A)) };
  },
  readouts(api, s) {
    if (!s.R) return [];
    const e = this.errs(api, s), sc = api.scene;
    if (sc === "hh" && api.p.m === 1 && s.done) api.done("hh");
    if (sc === "giv" && api.p.m === 1 && s.done) api.done("giv");
    if (sc === "gs" && api.p.m === 2 && s.done && e && e.oe > 0.1) api.done("loss");
    if (sc === "mgs" && api.p.m === 2 && s.done && e && e.oe < 1e-6) api.done("mgs");
    const what = sc === "hh" ? api.T("反射", "reflections") : sc === "giv" ? api.T("旋转", "rotations") : api.T("列", "columns");
    const rows = [[["已做步数", "Steps so far"], s.count + " " + what + (s.done ? api.T("（完成）", " (done)") : "")]];
    if (e) {
      rows.push([["‖QᵀQ − I‖_F（正交性）", "‖QᵀQ − I‖_F (orthogonality)"], e.oe.toExponential(1)]);
      if (e.re !== undefined) rows.push([["‖QR − A‖_F", "‖QR − A‖_F"], e.re.toExponential(1)]);
    }
    if (sc === "giv" && !s.done) { const [i, j] = s.todo[s.k]; rows.push([["下一步消去", "Next to zero"], api.T(`第 ${i + 1} 行第 ${j + 1} 列（与第 ${i} 行旋转）`, `row ${i + 1}, column ${j + 1} (rotate with row ${i})`)]); }
    return rows;
  },
  draw(api, s) {
    if (!s.R) return;
    const { w, h } = api, ink = api.css("--ink");
    const n = s.A[0].length, cols = [...s.gq, ...Array.from({ length: n - s.gq.length }, (_, j) => s.A.map((r) => r[s.gq.length + j]))];
    const gs = api.scene === "gs" || api.scene === "mgs";
    const M = gs ? api.la.T(cols) : s.R;
    const title = gs ? api.T("当前的列：已正交化的 q 与尚未处理的 a", "current columns: q's done, a's to go") : api.T("当前的矩阵（红正、蓝负，深浅表示大小）", "current matrix (red +, blue −, shade = size)");
    api.label(title, 16, 22, ink, 13);
    const cw = Math.min(90, (w - 60) / 3), x0 = 30, y0 = 40, hh = Math.min(h - 60, 5 * 54);
    api.heat(x0, y0, cw * 3, hh, M, { numbers: true, digits: api.p.m === 2 ? 2 : 3, max: api.p.m === 2 ? 1 : 5 });
    if (!gs) {
      // mark the entries below the diagonal that are already zero
      for (let i = 0; i < 5; i++) for (let j = 0; j < 3 && j < i; j++) if (Math.abs(s.R[i][j]) < 1e-12) api.label("0", x0 + (j + 0.5) * cw, y0 + (i + 0.5) * hh / 5 + 14, api.css("--green"), 11, "center");
    }
    api.label(api.T("右侧读数：Q 的正交性与分解的误差", "Right: orthogonality of Q and the error of QR"), x0 + cw * 3 + 20, y0 + 20, api.css("--muted"), 12);
  },
});
