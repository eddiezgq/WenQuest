// 实验 18.4 低秩逼近：用 k 层重建一张图像（配 18.4 节；图像与 18.7 节、code/_img.py 相同，逐像素一致）。
WQ.lab({
  title: ["实验 18.4 低秩逼近：用 k 层重建一张图像", "Lab 18.4 Low-rank approximation: rebuilding an image from k layers"],
  goal: ["对 120×160 的齿轮图像做奇异值分解，拖动 k 看截断重建、误差和存储量；与“按行抽样”的压缩方法比较。",
         "Take the SVD of a 120×160 gear image; drag k to see the truncated reconstruction, its error and storage; compare with keeping sampled rows."],
  scenes: [
    { id: "svd", name: ["截断奇异值分解", "Truncated SVD"],
      problem: { title: ["工程问题：检测照片存档", "Engineering problem: archiving inspection photos"],
                 text: ["检测工位为每个齿轮拍一张照片。用前 k 层 σᵢuᵢvᵢᵀ 近似，存 k(m + n + 1) 个数代替 m n 个数，误差有多大？",
                        "Each gear is photographed at inspection. Keeping the first k layers σᵢuᵢvᵢᵀ stores k(m + n + 1) numbers instead of mn. How large is the error?"] } },
    { id: "rows", name: ["对照：按行抽样", "Compare: sampled rows"],
      problem: { title: ["生活中的例子：隔行存图", "Everyday example: keeping every few rows"],
                 text: ["用同样多的数，只存均匀抽取的若干整行，其余各行用最近的已存行代替。哪一种方法误差小？",
                        "With the same number of values, keep some evenly spaced full rows and copy the nearest kept row into the others. Which method is better?"] } },
  ],
  params: [{ id: "k", name: ["保留的层数 k", "Layers kept k"], min: 1, max: 60, step: 1, value: 1, digits: 0 }],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ten", text: ["找出相对误差首次低于 10% 的 k。", "Find the first k with relative error below 10%."], demo: { scene: "svd", set: { k: 5 }, press: [] } },
    { id: "spec", text: ["把 k 调到 20，比较 ‖A − A_k‖₂（独立计算）与 σ₂₁。", "Set k = 20 and compare ‖A − A_k‖₂ (computed separately) with σ₂₁."], demo: { scene: "svd", set: { k: 20 }, press: [] } },
    { id: "cmp", text: ["切换到“按行抽样”，k = 10 时比较两种方法在同样存储量下的误差。", "Switch to sampled rows; at k = 10 compare both errors at equal storage."], demo: { scene: "rows", set: { k: 10 }, press: [] } },
  ],
  think: ["为什么第一层就占了总能量的九成以上？", "Why does the first layer alone carry over ninety percent of the energy?"],

  image() {   // the same drawing as code/_img.py, pixel for pixel (integer LCG for the noise)
    const M = 120, N = 160, A = [], cx = 80, cy = 60;
    const gear = (x, y) => {
      const r = Math.hypot(x - cx, y - cy), a = Math.atan2(y - cy, x - cx);
      const ph = (((a * 18 / (2 * Math.PI)) % 1) + 1) % 1;
      const tooth = ph > 0.18 && ph < 0.62 ? 1 : ph <= 0.18 ? Math.max(0, 1 - Math.abs(ph - 0.18) / 0.08) : Math.max(0, 1 - Math.abs(ph - 0.62) / 0.08);
      return [r <= 40 + 6 * Math.min(1, tooth * 1.6), r, a];
    };
    let seed = 20261002n;
    for (let i = 0; i < M; i++) {
      const row = [];
      for (let j = 0; j < N; j++) {
        const x = j + 0.5, y = i + 0.5;
        let v = 0.80 + 0.14 * i / (M - 1);
        if (gear(x - 4, y - 4)[0]) v -= 0.18;
        const [inside, r, a] = gear(x, y);
        if (inside) {
          v = 0.30 + 0.12 * Math.cos(a - 0.8);
          if (r < 15) v = 0.62;
          let bolt = false;
          for (let k = 0; k < 4; k++) if (Math.hypot(x - (cx + 26 * Math.cos(k * Math.PI / 2 + Math.PI / 4)), y - (cy + 26 * Math.sin(k * Math.PI / 2 + Math.PI / 4))) < 3.6) bolt = true;
          const key = Math.abs(x - cx) < 2.2 && y > cy - 9.5 && y < cy;
          if (r < 7 || bolt || key) v = 0.80 + 0.14 * i / (M - 1) - 0.18;
        }
        seed = (1103515245n * seed + 12345n) % 2147483648n;
        v += 0.04 * (Number(seed) / 2147483648 - 0.5);
        row.push(Math.min(1, Math.max(0, v)));
      }
      A.push(row);
    }
    return A;
  },
  prepare(s, api) {   // the image and its SVD are computed once and kept on the lab (not in the state, which resets)
    if (!this.data) {
      const A = this.image(), svd = api.la.svd(A), tot = svd.s.reduce((t, x) => t + x * x, 0);
      this.data = { A, svd, tot, norm: Math.sqrt(tot) };
    }
    Object.assign(s, this.data);
  },
  reset(api, s) { this.prepare(s, api); },
  spec2(E, api) {   // ‖E‖₂ by power iteration on EᵀE (independent of the SVD above)
    const Et = api.la.T(E);
    let x = E[0].map((_, j) => Math.cos(j + 1)), lam = 0;
    for (let it = 0; it < 200; it++) {
      const y = api.la.mv(Et, api.la.mv(E, x)), n = api.la.norm(y);
      if (n === 0) return 0;
      x = y.map((t) => t / n); lam = n;
    }
    return Math.sqrt(lam);
  },
  approx(api, s) {
    const k = Math.round(api.p.k), m = s.A.length, n = s.A[0].length;
    if (s.key === api.scene + k) return s.cur;
    let B;
    if (api.scene === "svd") B = api.la.lowrank(s.svd, k);
    else {
      const rows = Math.max(1, Math.round(k * (m + n + 1) / n));
      const kept = Array.from({ length: rows }, (_, i) => Math.min(m - 1, Math.round((i + 0.5) * m / rows - 0.5)));
      B = s.A.map((_, i) => s.A[kept.reduce((b, r) => (Math.abs(r - i) < Math.abs(b - i) ? r : b), kept[0])].slice());
    }
    const E = api.la.sub(s.A, B);
    s.cur = { k, B, E, rel: api.la.fro(E) / s.norm, e2: k === 20 || api.scene === "rows" ? this.spec2(E, api) : null };
    s.key = api.scene + k;
    return s.cur;
  },
  readouts(api, s) {
    this.prepare(s, api);
    const c = this.approx(api, s), m = s.A.length, n = s.A[0].length, k = c.k, sv = s.svd.s;
    const kmin = sv.findIndex((_, i) => Math.sqrt(sv.slice(i + 1).reduce((t, x) => t + x * x, 0) / s.tot) < 0.1) + 1;
    if (api.scene === "svd" && k === kmin) api.done("ten");
    if (api.scene === "svd" && k === 20 && c.e2 != null && Math.abs(c.e2 - sv[20]) < 1e-6 * sv[0]) api.done("spec");
    if (api.scene === "rows" && k === 10) api.done("cmp");
    const store = k * (m + n + 1), svdRel = Math.sqrt(sv.slice(k).reduce((t, x) => t + x * x, 0) / s.tot);
    const rows = [[["存储量", "Storage"], `${store} / ${m * n} = ${api.fmt(100 * store / (m * n), 1)}%`],
                  [["相对误差 ‖A−B‖_F/‖A‖_F", "Relative error ‖A−B‖_F/‖A‖_F"], api.fmt(100 * c.rel, 2) + "%"],
                  [["σ₁ 所占能量", "Energy of σ₁"], api.fmt(100 * sv[0] * sv[0] / s.tot, 1) + "%"],
                  [["σₖ₊₁", "σₖ₊₁"], api.fmt(sv[k], 4)]];
    if (c.e2 != null) rows.push([["‖A − B‖₂（幂法）", "‖A − B‖₂ (power method)"], api.fmt(c.e2, 4)]);
    if (api.scene === "rows") rows.push([["同样存储量下 SVD 的误差", "SVD error at equal storage"], api.fmt(100 * svdRel, 2) + "%"]);
    return rows;
  },
  draw(api, s) {
    this.prepare(s, api);
    const c = this.approx(api, s), { w, h } = api, muted = api.css("--muted");
    const iw = w * 0.36, ih = iw * 0.75, y0 = h * 0.12;
    api.image(w * 0.03, y0, iw, ih, c.B);
    api.label(api.scene === "svd" ? api.T(`A_k，k = ${c.k}`, `A_k, k = ${c.k}`) : api.T("按行抽样的重建", "sampled-row rebuild"), w * 0.03 + iw / 2, y0 - 12, muted, 13, "center");
    api.heat(w * 0.42, y0, iw * 0.7, ih * 0.7, c.E, { max: 0.3 });
    api.label(api.T("误差 A − B（红正蓝负）", "error A − B (red +, blue −)"), w * 0.42 + iw * 0.35, y0 - 12, muted, 13, "center");
    api.bars(w * 0.42, y0 + ih * 0.8, w * 0.55, h * 0.3, s.svd.s.slice(0, 60), { log: true, mark: c.k, label: api.T("σ₁…σ₆₀（对数）", "σ₁…σ₆₀ (log)") });
    api.image(w * 0.03, y0 + ih + 14, iw * 0.4, ih * 0.4, s.A);
    api.label(api.T("原图", "original"), w * 0.03 + iw * 0.45, y0 + ih + 14 + ih * 0.2, muted, 12);
  },
});
