// 实验 3.3 一步一步做消元（配 3.3–3.5 节）。三个方程组：方程组 (3.3.1)（唯一解）、3.5 节的 (乙)（无解）、(丙)（无穷多解）。
// 在增广矩阵上做三种初等行变换，分数精确运算；程序记录每一步，可撤销；“程序走一步”按高斯–若尔当消元的标准次序代做下一步。
WQ.lab({
  title: ["实验 3.3 一步一步做消元", "Lab 3.3 Elimination step by step"],
  goal: ["在增广矩阵上亲手做交换、数乘、倍加三种行变换，把方程组化为上三角形和简化行阶梯形，读出解；体会无解和无穷多解在行阶梯形中的样子。",
         "Do the three row operations on the augmented matrix by hand, reduce the system to triangular and reduced row echelon form, and read off the solution; see what 'no solution' and 'infinitely many' look like."],
  scenes: [
    { id: "uniq", name: ["唯一解：方程组 (3.3.1)", "Unique: system (3.3.1)"],
      problem: { title: ["把它化成三角形，再化成简化行阶梯形", "Make it triangular, then reduced"],
                 text: ["x + 2y − z = 2，2x + 5y + z = 9，−x + y + 4z = 7。先用倍加把主元下方消为零，再把主元化为 1、消去主元上方。",
                        "x + 2y − z = 2, 2x + 5y + z = 9, −x + y + 4z = 7. Clear below the pivots, then scale them to 1 and clear above."] } },
    { id: "none", name: ["无解：方程组 (乙)", "None: system (B)"],
      problem: { title: ["找出矛盾", "Find the contradiction"],
                 text: ["x + y + z = 6，x + 2y + 3z = 14，2x + 3y + 4z = 21。消元到出现 0 = 非零数 的一行。", "x + y + z = 6, x + 2y + 3z = 14, 2x + 3y + 4z = 21. Eliminate until a row reads 0 = nonzero."] } },
    { id: "many", name: ["无穷多解：方程组 (丙)", "Infinitely many: system (C)"],
      problem: { title: ["找出自由变量", "Find the free variable"],
                 text: ["x + y + z = 6，x + 2y + 3z = 14，2x + 3y + 4z = 20。化到简化行阶梯形，看哪一列没有主元。", "x + y + z = 6, x + 2y + 3z = 14, 2x + 3y + 4z = 20. Reduce fully and see which column has no pivot."] } },
  ],
  params: [
    { id: "op", name: ["行变换（1 交换，2 数乘，3 倍加）", "Operation (1 swap, 2 scale, 3 add)"], min: 1, max: 3, step: 1, value: 3, digits: 0 },
    { id: "i", name: ["被改变的行 i", "Row changed, i"], min: 1, max: 3, step: 1, value: 2, digits: 0 },
    { id: "j", name: ["另一行 j（交换、倍加用）", "Other row j (swap, add)"], min: 1, max: 3, step: 1, value: 1, digits: 0 },
    { id: "p", name: ["倍数的分子 p", "Numerator p"], min: -12, max: 12, step: 1, value: -2, digits: 0 },
    { id: "q", name: ["倍数的分母 q", "Denominator q"], min: 1, max: 12, step: 1, value: 1, digits: 0 },
  ],
  buttons: [{ id: "go", name: ["执行", "Apply"], primary: true }, { id: "auto", name: ["程序走一步", "Program's step"] },
            { id: "undo", name: ["撤销", "Undo"] }, { id: "restart", name: ["重新开始", "Start over"] }],
  tasks: [
    { id: "upper", text: ["把方程组 (3.3.1) 化为上三角形（主元下方全为零）。", "Make system (3.3.1) upper triangular."],
      demo: { scene: "uniq", set: {}, press: ["restart", "auto", "auto", "auto", "auto"], wait: 1 } },
    { id: "rref", text: ["把方程组 (3.3.1) 化为简化行阶梯形，读出解。", "Reduce system (3.3.1) completely and read off the solution."],
      demo: { scene: "uniq", set: {}, press: ["restart", "auto", "auto", "auto", "auto", "auto", "auto", "auto", "auto", "auto", "auto"], wait: 1 } },
    { id: "none", text: ["在方程组 (乙) 中消元到出现 0 = 非零数 的一行。", "In system (B) eliminate until a row reads 0 = nonzero."],
      demo: { scene: "none", set: {}, press: ["restart", "auto", "auto", "auto", "auto", "auto", "auto", "auto", "auto"], wait: 1 } },
    { id: "many", text: ["把方程组 (丙) 化为简化行阶梯形，指出自由变量。", "Reduce system (C) completely and name the free variable."],
      demo: { scene: "many", set: {}, press: ["restart", "auto", "auto", "auto", "auto", "auto", "auto", "auto", "auto"], wait: 1 } },
  ],
  think: ["为什么不允许“用 0 乘一行”？为什么倍加要求 i ≠ j？", "Why is 'multiply a row by 0' not allowed? Why must i ≠ j in an add?"],

  systems: { uniq: [[1, 2, -1, 2], [2, 5, 1, 9], [-1, 1, 4, 7]], none: [[1, 1, 1, 6], [1, 2, 3, 14], [2, 3, 4, 21]], many: [[1, 1, 1, 6], [1, 2, 3, 14], [2, 3, 4, 20]] },
  // rationals as [numerator, denominator], denominator > 0
  gcd(a, b) { a = Math.abs(a); b = Math.abs(b); while (b) [a, b] = [b, a % b]; return a || 1; },
  R(n, d = 1) { if (d < 0) { n = -n; d = -d; } const g = this.gcd(n, d); return [n / g, d / g]; },
  add(a, b) { return this.R(a[0] * b[1] + b[0] * a[1], a[1] * b[1]); },
  mul(a, b) { return this.R(a[0] * b[0], a[1] * b[1]); },
  neg(a) { return [-a[0], a[1]]; },
  inv(a) { return this.R(a[1], a[0]); },
  isz(a) { return a[0] === 0; },
  str(a) { return a[1] === 1 ? String(a[0]) : a[0] + "/" + a[1]; },
  st(api) {   // state that survives slider changes: one history per scene
    if (!this.mem) this.mem = {};
    if (!this.mem[api.scene]) this.restart(api);
    return this.mem[api.scene];
  },
  restart(api) {
    this.mem = this.mem || {};
    this.mem[api.scene] = { M: this.systems[api.scene].map((r) => r.map((x) => this.R(x))), hist: [], log: [] };
  },
  apply(api, kind, i, j, c) {
    const s = this.st(api), M = s.M.map((r) => r.slice());
    let text;
    if (kind === 1) { if (i === j) return api.T("交换需要两行不同", "swap needs two different rows"); [M[i], M[j]] = [M[j], M[i]]; text = `R${i + 1} ↔ R${j + 1}`; }
    if (kind === 2) { if (this.isz(c)) return api.T("不能用 0 乘一行", "cannot scale by 0"); M[i] = M[i].map((x) => this.mul(x, c)); text = `R${i + 1} ← (${this.str(c)}) R${i + 1}`; }
    if (kind === 3) { if (i === j) return api.T("倍加要求 i ≠ j", "add needs i ≠ j"); M[i] = M[i].map((x, k) => this.add(x, this.mul(c, M[j][k]))); text = `R${i + 1} ← R${i + 1} + (${this.str(c)}) R${j + 1}`; }
    s.hist.push(s.M); s.log.push(text); s.M = M;
    return null;
  },
  next(api) {   // the next Gauss–Jordan step: swap a nonzero pivot up, clear below, scale to 1, clear above
    const M = this.st(api).M, m = 3, n = 3;
    let r = 0;
    for (let c = 0; c < n && r < m; c++) {
      let p = -1; for (let i = r; i < m; i++) if (!this.isz(M[i][c])) { p = i; break; }
      if (p < 0) continue;
      if (p !== r) return [1, r, p, this.R(1)];
      for (let i = r + 1; i < m; i++) if (!this.isz(M[i][c])) return [3, i, r, this.neg(this.mul(M[i][c], this.inv(M[r][c])))];
      r++;
    }
    r = 0;
    for (let c = 0; c < n && r < m; c++) {
      if (this.isz(M[r][c])) { let any = false; for (let i = r; i < m; i++) if (!this.isz(M[i][c])) any = true; if (!any) continue; }
      if (!(M[r][c][0] === 1 && M[r][c][1] === 1)) return [2, r, r, this.inv(M[r][c])];
      for (let i = 0; i < r; i++) if (!this.isz(M[i][c])) return [3, i, r, this.neg(M[i][c])];
      r++;
    }
    return null;
  },
  action(id, api, s) {
    if (id === "restart") { this.restart(api); this.msg = ""; }
    if (id === "undo") { const t = this.st(api); if (t.hist.length) { t.M = t.hist.pop(); t.log.pop(); } this.msg = ""; }
    if (id === "go") this.msg = this.apply(api, api.p.op, api.p.i - 1, api.p.j - 1, this.R(api.p.p, api.p.q)) || "";
    if (id === "auto") { const st = this.next(api); this.msg = st ? (this.apply(api, ...st) || "") : api.T("已经是简化行阶梯形", "already reduced"); }
  },
  shape(M) {   // pivots, upper-triangular and reduced-echelon tests on the 3×3 coefficient part
    const piv = [];
    let lastc = -1, echelon = true, zeroRowSeen = false;
    for (const row of M) {
      const c = row.slice(0, 3).findIndex((x) => x[0] !== 0);
      if (c < 0) { zeroRowSeen = true; continue; }
      if (zeroRowSeen || c <= lastc) echelon = false;
      lastc = c; piv.push([M.indexOf(row), c]);
    }
    const reduced = echelon && piv.every(([r, c]) => M[r][c][0] === 1 && M[r][c][1] === 1 && M.every((row, k) => k === r || row[c][0] === 0));
    const upper = M.every((row, i) => row.slice(0, Math.min(i, 3)).every((x) => x[0] === 0));
    const contra = M.some((row) => row.slice(0, 3).every((x) => x[0] === 0) && row[3][0] !== 0);
    return { piv, echelon, reduced, upper, contra };
  },
  readouts(api) {
    const s = this.st(api), sh = this.shape(s.M);
    if (api.scene === "uniq" && sh.upper) api.done("upper");
    if (api.scene === "uniq" && sh.reduced) api.done("rref");
    if (api.scene === "none" && sh.contra) api.done("none");
    if (api.scene === "many" && sh.reduced && !sh.contra) api.done("many");
    const pc = sh.piv.map(([, c]) => c + 1), free = [1, 2, 3].filter((c) => !pc.includes(c)).map((c) => ["x", "y", "z"][c - 1]);
    let verdict = api.T("继续消元", "keep going");
    if (sh.contra) verdict = api.T("出现 0 = 非零数：无解", "0 = nonzero: no solution");
    else if (sh.reduced && pc.length === 3) verdict = api.T("唯一解：", "unique: ") + `x = ${this.str(s.M[0][3])}, y = ${this.str(s.M[1][3])}, z = ${this.str(s.M[2][3])}`;
    else if (sh.reduced) verdict = api.T("无穷多解，自由变量：", "infinitely many, free: ") + free.join(", ");
    const c = this.R(api.p.p, api.p.q);
    const plan = api.p.op === 1 ? `R${api.p.i} ↔ R${api.p.j}` : api.p.op === 2 ? `R${api.p.i} ← (${this.str(c)}) R${api.p.i}` : `R${api.p.i} ← R${api.p.i} + (${this.str(c)}) R${api.p.j}`;
    return [[["准备执行", "Ready to apply"], plan], [["已做步数", "Steps done"], String(s.log.length)],
            [["主元列", "Pivot columns"], pc.join(", ") || "—"], [["形状", "Shape"], sh.reduced ? api.T("简化行阶梯形", "reduced echelon") : sh.echelon ? api.T("行阶梯形", "echelon") : sh.upper ? api.T("上三角", "upper triangular") : api.T("尚未成阶梯形", "not yet echelon")],
            [["结论", "Verdict"], verdict], [["提示", "Note"], this.msg || "—"]];
  },
  draw(api) {
    const { w: W, h: H } = api, s = this.st(api), ink = api.css("--ink"), muted = api.css("--muted"), sh = this.shape(s.M);
    const x0 = W * 0.06, y0 = H * 0.16, cw = Math.min(W * 0.11, 90), rh = Math.min(H * 0.17, 56);
    api.label(api.T("增广矩阵 (A | b)", "augmented matrix (A | b)"), x0, y0 - 18, muted, 13);
    const pivSet = new Set(sh.piv.map(([r, c]) => r + "," + c));
    s.M.forEach((row, i) => {
      api.label("R" + (i + 1), x0 - 4, y0 + rh * (i + 0.6), muted, 13, "right");
      row.forEach((x, k) => {
        const cx = x0 + 18 + cw * (k + 0.5) + (k === 3 ? 18 : 0), cy = y0 + rh * (i + 0.6);
        if (pivSet.has(i + "," + k)) api.circle(cx, cy - 5, Math.min(cw, rh) * 0.38, "rgba(201,143,0,0.18)", api.css("--amber"));
        const red = k === 3 && sh.contra && row.slice(0, 3).every((t) => t[0] === 0);
        api.label(this.str(x), cx, cy, red ? api.css("--red") : ink, 18, "center");
      });
    });
    const bx = x0 + 18 + cw * 3 + 9;
    api.line(bx, y0, bx, y0 + rh * 3.1, muted, 1.5);
    api.line(x0 + 10, y0, x0 + 10, y0 + rh * 3.1, ink, 1.5); api.line(x0 + 18 + cw * 4 + 26, y0, x0 + 18 + cw * 4 + 26, y0 + rh * 3.1, ink, 1.5);
    const lx = W * 0.64;
    api.label(api.T("已做的行变换", "operations so far"), lx, y0 - 18, muted, 13);
    s.log.slice(-10).forEach((t, k) => api.label(`${s.log.length - Math.min(10, s.log.length) + k + 1}. ${t}`, lx, y0 + 6 + 20 * k, ink, 13));
    api.label(api.T("橙圈：主元", "orange circles: pivots"), x0, H - 12, api.css("--amber"), 12);
  },
});
