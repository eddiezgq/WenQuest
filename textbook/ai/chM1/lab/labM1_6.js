// 实验 M1.6 矩阵把圆变成椭圆；低秩近似留几个奇异值（配 M1.6、M1.7 节）。
// 两个场景：
//   ellipse ：自己调 2×2 矩阵的四个元素，看单位圆被它变成什么样的椭圆，读出两个奇异值与条件数；
//   lowrank ：一张程序画出来的零件表面图，调“保留几个奇异值”与噪声大小，看重建误差与要存多少数。
// 全部在浏览器里现算（雅可比法求 2×2 的奇异值，幂迭代求图的前几个奇异向量），不需要显卡。
WQ.lab({
  title: ["实验 M1.6 奇异值分解：椭圆与低秩近似", "Lab M1.6 SVD: the ellipse and low-rank approximation"],
  goal: ["先用一个 2×2 的矩阵把“奇异值是什么”看明白：矩阵把单位圆变成椭圆，两个半轴就是两个奇异值，它们的比就是条件数。再用一张零件表面图看低秩近似：保留前 k 个奇异值能留住多少、省掉多少，以及为什么 k 加到一定程度就不该再加。",
         "First see what singular values are: a 2×2 matrix turns the unit circle into an ellipse whose semi-axes are the singular values, and their ratio is the condition number. Then use a surface image to see what keeping the first k singular values preserves, what it saves, and why adding more k stops helping."],
  scenes: [
    { id: "ellipse", name: ["圆变椭圆", "Circle to ellipse"],
      problem: { title: ["问题：一个矩阵到底把空间怎么样了", "Problem: what does a matrix do to space"],
                 text: ["矩阵乘法写出来是一堆数，看不出几何含义。把它作用在单位圆上就看清楚了：结果永远是一个椭圆——先转一下、再沿两个互相垂直的方向拉伸、再转一下。两个拉伸倍数就是奇异值。",
                        "A matrix is just a table of numbers until you apply it to the unit circle: the result is always an ellipse — rotate, stretch along two orthogonal directions, rotate again. The two stretch factors are the singular values."] } },
    { id: "lowrank", name: ["低秩近似", "Low-rank approximation"],
      problem: { title: ["问题：一张图要存多少数才够", "Problem: how many numbers does an image need"],
                 text: ["这张磨削表面图的结构只有 3 层（明暗 1 层、粗磨与精磨的纹理各 1 层），其余都是测量噪声。保留前 k 个奇异值，就只需存 k(m+n+1) 个数。k 取多少合适？再往上加，降下去的是误差还是噪声？",
                        "This ground-surface image has only three structural layers (shading, coarse and fine grinding marks); the rest is noise. Keeping k singular values stores k(m+n+1) numbers. How large should k be, and past that, are you fitting signal or noise?"] } },
  ],
  params: [
    { id: "a11", name: ["矩阵 a₁₁", "a11"], min: -2, max: 2, step: 0.1, value: 1.6, digits: 1 },
    { id: "a12", name: ["矩阵 a₁₂", "a12"], min: -2, max: 2, step: 0.1, value: 0.9, digits: 1 },
    { id: "a21", name: ["矩阵 a₂₁", "a21"], min: -2, max: 2, step: 0.1, value: 0.2, digits: 1 },
    { id: "a22", name: ["矩阵 a₂₂", "a22"], min: -2, max: 2, step: 0.1, value: 1.1, digits: 1 },
    { id: "k", name: ["保留前几个奇异值", "rank k"], min: 1, max: 24, step: 1, value: 1, digits: 0 },
    { id: "noise", name: ["测量噪声（%）", "noise (%)"], min: 0, max: 5, step: 0.5, value: 1, digits: 1 },
  ],
  legend: [{ color: "var(--blue)", name: ["单位圆 / 原图", "unit circle / original"] },
           { color: "var(--amber)", name: ["变换后 / 重建", "transformed / reconstruction"] },
           { color: "var(--red)", name: ["第一个奇异方向", "first singular direction"] }],
  tasks: [
    { id: "equal", text: ["把矩阵调成 a₁₁ = a₂₂ = 1、a₁₂ = a₂₁ = 0：椭圆变成什么？两个奇异值各是多少，条件数是多少？",
                          "Set a11 = a22 = 1 and a12 = a21 = 0: what shape is it now? What are the two singular values and the condition number?"],
      demo: { scene: "ellipse", set: { a11: 1, a12: 0, a21: 0, a22: 1 }, press: [] } },
    { id: "singular", text: ["把第二行调成第一行的一半（a₂₁ = 0.8、a₂₂ = 0.45，a₁₁ = 1.6、a₁₂ = 0.9）：椭圆塌成了什么？这时条件数是多少，意味着什么？",
                             "Make the second row half the first (a21 = 0.8, a22 = 0.45 with a11 = 1.6, a12 = 0.9): what does the ellipse collapse into, and what does the condition number say?"],
      demo: { scene: "ellipse", set: { a11: 1.6, a12: 0.9, a21: 0.8, a22: 0.45 }, press: [] } },
    { id: "k3", text: ["切到“低秩近似”，噪声保持 1%，把 k 从 1 加到 3：相对误差降到多少？再加到 10 呢——降下去的是结构还是噪声？",
                       "Switch to low-rank, keep the noise at 1% and raise k from 1 to 3: how far does the error fall? Then try 10 — is it still removing structure, or fitting noise?"],
      demo: { scene: "lowrank", set: { k: 3, noise: 1 }, press: [] } },
    { id: "clean", text: ["把噪声调成 0，再把 k 调到 3：相对误差变成多少？这说明这张图“真正的秩”是几？",
                          "Set the noise to 0 and k to 3: what is the error now, and what does that say about the true rank of this image?"],
      demo: { scene: "lowrank", set: { k: 3, noise: 0 }, press: [] } },
    { id: "store", text: ["在噪声 1% 下找出“误差已经降到噪声水平”的那个 k：这时要存的数占原来的百分之几？",
                          "With 1% noise, find the k at which the error reaches the noise level: what share of the original numbers do you store then?"],
      demo: { scene: "lowrank", set: { k: 6, noise: 1 }, press: [] } },
  ],
  think: ["条件数很大的矩阵，用单精度解方程会丢几位有效数字？（提示：条件数每大十倍，丢一位）",
          "With a large condition number, how many significant digits does a single-precision solve lose? (Hint: one digit per factor of ten.)"],

  N: 48,                                     // 图的大小（浏览器里现算，取小一些）
  // ---------- 2×2 的奇异值：AᵀA 的特征值开根号
  svd2(p) {
    const a = p.a11, b = p.a12, c = p.a21, d = p.a22;
    const m11 = a * a + c * c, m12 = a * b + c * d, m22 = b * b + d * d;
    const tr = m11 + m22, det = m11 * m22 - m12 * m12;
    const disc = Math.max(0, tr * tr / 4 - det);
    const l1 = tr / 2 + Math.sqrt(disc), l2 = Math.max(0, tr / 2 - Math.sqrt(disc));
    const s1 = Math.sqrt(l1), s2 = Math.sqrt(l2);
    // 右奇异向量 v1：(AᵀA − l2 I) 的列方向
    let vx = m11 - l2, vy = m12;
    if (Math.abs(vx) + Math.abs(vy) < 1e-12) { vx = 1; vy = 0; }
    const nv = Math.hypot(vx, vy);
    return { s1, s2, v1: [vx / nv, vy / nv], kappa: s2 > 1e-9 ? s1 / s2 : Infinity };
  },
  // ---------- 一张零件表面图：明暗 + 粗磨 + 精磨 + 噪声（与 _chM1.surface 同一套公式）
  rand(seed) { let t = seed + 0x6d2b79f5; return () => { t += 0x6d2b79f5; let x = Math.imul(t ^ (t >>> 15), 1 | t); x ^= x + Math.imul(x ^ (x >>> 7), 61 | x); return ((x ^ (x >>> 14)) >>> 0) / 4294967296; }; },
  image(noisePct) {
    const n = this.N, rnd = this.rand(7), A = [];
    for (let i = 0; i < n; i++) {
      const r = i / (n - 1), row = new Float64Array(n);
      for (let j = 0; j < n; j++) {
        const c = j / (n - 1);
        const shade = 0.55 + 0.32 * Math.cos((c - 0.5) * 2.2);
        const g1 = 0.05 * Math.sin(2 * Math.PI * 6 * r) * (0.6 + 0.4 * c);
        const g2 = 0.02 * Math.sin(2 * Math.PI * 17 * r) * (1.0 - 0.5 * c);
        const z = Math.sqrt(-2 * Math.log(rnd() + 1e-12)) * Math.cos(2 * Math.PI * rnd());   // 标准正态
        row[j] = Math.min(1, Math.max(0, shade + g1 + g2 + (noisePct / 100) * z));
      }
      A.push(row);
    }
    return A;
  },
  // 幂迭代逐个取出奇异三元组（教学用：矩阵小，够快也够准）
  svdK(A, k) {
    const n = this.N, R = A.map((r) => Float64Array.from(r)), out = [];
    for (let t = 0; t < k; t++) {
      let v = new Float64Array(n);
      const rnd = this.rand(100 + t);
      for (let j = 0; j < n; j++) v[j] = rnd() - 0.5;
      let s = 0, u = new Float64Array(n);
      for (let it = 0; it < 80; it++) {
        u = new Float64Array(n);
        for (let i = 0; i < n; i++) { let acc = 0; for (let j = 0; j < n; j++) acc += R[i][j] * v[j]; u[i] = acc; }
        let nu = Math.hypot(...u); if (nu < 1e-14) break;
        for (let i = 0; i < n; i++) u[i] /= nu;
        const w = new Float64Array(n);
        for (let j = 0; j < n; j++) { let acc = 0; for (let i = 0; i < n; i++) acc += R[i][j] * u[i]; w[j] = acc; }
        s = Math.hypot(...w); if (s < 1e-14) break;
        for (let j = 0; j < n; j++) w[j] /= s;
        v = w;
      }
      out.push({ s, u, v });
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) R[i][j] -= s * u[i] * v[j];   // 去掉这一层，接着找下一层
    }
    return out;
  },
  calc(api) {
    const p = api.p, key = p.k + "|" + p.noise;
    if (this._c && this._c.key === key) return this._c.val;
    const n = this.N, A = this.image(p.noise), comp = this.svdK(A, Math.max(p.k, 24));
    const Ak = [];
    for (let i = 0; i < n; i++) {
      const row = new Float64Array(n);
      for (let t = 0; t < p.k; t++) for (let j = 0; j < n; j++) row[j] += comp[t].s * comp[t].u[i] * comp[t].v[j];
      Ak.push(row);
    }
    let num = 0, den = 0, worst = 0;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const d = A[i][j] - Ak[i][j];
      num += d * d; den += A[i][j] * A[i][j]; worst = Math.max(worst, Math.abs(d));
    }
    // 噪声本身有多大（与无噪声的同一张图比）
    const A0 = this.image(0);
    let nn = 0;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) nn += (A[i][j] - A0[i][j]) ** 2;
    const val = { A, Ak, err: Math.sqrt(num / den) * 100, worst, noise: Math.sqrt(nn / den) * 100,
                  s: comp.map((c) => c.s), keep: p.k * (2 * n + 1) / (n * n) * 100 };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const p = api.p;
    if (api.scene === "ellipse") {
      const r = this.svd2(p);
      if (p.a11 === 1 && p.a22 === 1 && p.a12 === 0 && p.a21 === 0) api.done("equal");
      if (r.kappa > 50) api.done("singular");
      return [[["σ₁（长半轴）", "sigma1 (major semi-axis)"], api.fmt(r.s1, 3)],
              [["σ₂（短半轴）", "sigma2 (minor semi-axis)"], api.fmt(r.s2, 3)],
              [["条件数 σ₁/σ₂", "condition number"], r.kappa > 1e6 ? "∞" : api.fmt(r.kappa, 2)],
              [["行列式（面积放大倍数）", "determinant (area factor)"], api.fmt(p.a11 * p.a22 - p.a12 * p.a21, 3)],
              [["单精度大约丢几位有效数字", "digits lost in float32"],
               r.kappa > 1e6 ? "≥ 6" : api.fmt(Math.log10(Math.max(r.kappa, 1)), 1)]];
    }
    const c = this.calc(api);
    if (p.k >= 3 && p.noise >= 1) api.done("k3");
    if (p.k >= 3 && p.noise === 0 && c.err < 0.05) api.done("clean");
    if (p.noise >= 1 && c.err <= c.noise * 1.05) api.done("store");
    return [[["相对误差", "relative error"], api.fmt(c.err, 2) + "%"],
            [["图里噪声本身", "the noise itself"], api.fmt(c.noise, 2) + "%"],
            [["单点最大误差", "largest pixel error"], api.fmt(c.worst, 3)],
            [["要存的数占原来的", "numbers kept"], api.fmt(c.keep, 1) + "%"],
            [["前三个奇异值", "first three singular values"],
             c.s.slice(0, 3).map((x) => api.fmt(x, 2)).join(" / ")]];
  },
  draw(api, s) {
    const { w, h } = api;
    if (api.scene === "ellipse") {
      const k = Math.min(w, h - 40) / 6.4, cx = w / 2, cy = (h - 20) / 2;
      const X = (x) => cx + x * k, Y = (y) => cy - y * k;
      api.line(X(-3), Y(0), X(3), Y(0), api.css("--grid"), 1);
      api.line(X(0), Y(-3), X(0), Y(3), api.css("--grid"), 1);
      const p = api.p, r = this.svd2(p);
      let px = null, qx = null;
      for (let i = 0; i <= 180; i++) {
        const t = i / 180 * 2 * Math.PI, x = Math.cos(t), y = Math.sin(t);
        const u = [X(x), Y(y)], v = [X(p.a11 * x + p.a12 * y), Y(p.a21 * x + p.a22 * y)];
        if (px) { api.line(px[0], px[1], u[0], u[1], api.css("--blue"), 2); api.line(qx[0], qx[1], v[0], v[1], api.css("--amber"), 2.4); }
        px = u; qx = v;
      }
      const v1 = r.v1, img = [p.a11 * v1[0] + p.a12 * v1[1], p.a21 * v1[0] + p.a22 * v1[1]];
      api.line(X(0), Y(0), X(img[0]), Y(img[1]), api.css("--red"), 3);
      api.label(api.T("蓝：单位圆　橙：变换后的椭圆　红：最长的那个方向（σ₁）",
                      "blue: unit circle, amber: the ellipse, red: the longest direction (sigma1)"),
                12, h - 12, api.css("--muted"), 12);
      return;
    }
    const c = this.calc(api), n = this.N;
    const side = Math.min((w - 60) / 2, h - 60), px = side / n;
    const show = (A, x0, title) => {
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
        const g = Math.round(Math.min(1, Math.max(0, A[i][j])) * 255);
        api.rect(x0 + j * px, 24 + i * px, px + 0.6, px + 0.6, `rgb(${g},${g},${g})`, `rgb(${g},${g},${g})`);
      }
      api.label(title, x0, 18, api.css("--ink"), 12);
    };
    show(c.A, 20, api.T("原图（含噪声）", "original (with noise)"));
    show(c.Ak, 40 + side, api.T(`保留前 ${api.p.k} 个奇异值`, `rank ${api.p.k} reconstruction`));
    api.label(api.T(`相对误差 ${c.err.toFixed(2)}%　要存的数 ${c.keep.toFixed(1)}%`,
                    `relative error ${c.err.toFixed(2)}%, numbers kept ${c.keep.toFixed(1)}%`),
              20, h - 12, api.css("--muted"), 12);
  },
});
