// 实验 4.7 矩阵乘法的速度（配 4.7.2、4.7.3 节）。在浏览器里用 JavaScript 实现三种算法：按定义的 ijk 三重循环、
// 交换循环次序的 ikj（最内层沿行连续访问内存）、分块的 ikj（块大小可调）。同样的 2n³ 次运算，耗时可以差好几倍。
WQ.lab({
  title: ["实验 4.7 矩阵乘法的速度", "Lab 4.7 How fast is matrix multiplication?"],
  goal: ["对同一对随机矩阵用三种算法计算乘积，确认结果相同，比较耗时与每秒浮点运算次数，观察耗时随 n 的增长和块大小的影响。",
         "Multiply the same random matrices with three algorithms, check the results agree, compare times and flop rates, and see how the time grows with n and depends on the block size."],
  scenes: [
    { id: "speed", robot: true, name: ["三种算法", "Three algorithms"],
      problem: { title: ["机器人问题：视觉网络一帧算得完吗？", "Robot problem: can the vision network keep up?"],
                 text: ["机器人的视觉网络处理一帧图像，主要时间花在矩阵乘法上。运算次数由公式决定，可耗时还取决于算法怎样使用内存。点“运行”，三种算法各算一遍。",
                        "Most of a vision network's time per frame goes into matrix multiplication. The operation count is fixed by the formula, but the time also depends on how the algorithm uses memory. Press Run to time three algorithms."] } },
  ],
  params: [
    { id: "n", name: ["矩阵阶数 n", "Matrix size n"], min: 64, max: 768, step: 64, value: 256, digits: 0 },
    { id: "bs", name: ["分块算法的块大小", "Block size"], min: 8, max: 128, step: 8, value: 32, digits: 0 },
  ],
  buttons: [{ id: "run", name: ["运行", "Run"], primary: true }, { id: "sweep", name: ["依次取 n = 64, 128, 256", "Run n = 64, 128, 256"] },
            { id: "bsweep", name: ["比较块大小", "Compare block sizes"] }, { id: "clear", name: ["清空记录", "Clear the log"] }],
  tasks: [
    { id: "same", text: ["取 n = 256 运行一次，确认三种算法的结果相同（最大差小于 10⁻⁹）。", "Run once with n = 256 and check that the three results agree (largest difference below 10⁻⁹)."],
      demo: { scene: "speed", set: { n: 256, bs: 32 }, press: ["run"], wait: 3 } },
    { id: "grow", text: ["至少取三个不同的 n 各运行一次（或点“依次取 n = 64, 128, 256”），看 n 加倍时耗时增加到几倍。", "Run with at least three different n (or press “Run n = 64, 128, 256”); by what factor does the time grow when n doubles?"],
      demo: { scene: "speed", set: { n: 256, bs: 32 }, press: ["sweep"], wait: 3 } },
    { id: "block", text: ["取 n = 512，用至少两个不同的块大小运行分块算法（或点“比较块大小”），找出较快的块大小。", "With n = 512, run the blocked algorithm with at least two block sizes (or press “Compare block sizes”); which is faster?"],
      demo: { scene: "speed", set: { n: 512, bs: 32 }, press: ["bsweep"], wait: 5 } },
  ],
  think: ["ijk 与 ikj 做的乘法和加法完全一样，为什么耗时不同？NumPy 的 A @ B 为什么还要快几十倍？",
          "ijk and ikj do exactly the same multiplications and additions; why do their times differ? Why is NumPy's A @ B still dozens of times faster?"],

  mem: null,
  log() { if (!this.mem) this.mem = { runs: [], blocks: [] }; return this.mem; },
  rand(n, seed) {   // reproducible pseudo-random matrix in a flat row-major array
    const a = new Float64Array(n * n); let s = seed >>> 0;
    for (let i = 0; i < n * n; i++) { s = (s * 1664525 + 1013904223) >>> 0; a[i] = s / 4294967296 - 0.5; }
    return a;
  },
  ijk(A, B, n) { const C = new Float64Array(n * n);
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { let s = 0; for (let k = 0; k < n; k++) s += A[i * n + k] * B[k * n + j]; C[i * n + j] = s; }
    return C; },
  ikj(A, B, n) { const C = new Float64Array(n * n);
    for (let i = 0; i < n; i++) for (let k = 0; k < n; k++) { const a = A[i * n + k], r = k * n, o = i * n; for (let j = 0; j < n; j++) C[o + j] += a * B[r + j]; }
    return C; },
  blocked(A, B, n, b) { const C = new Float64Array(n * n);
    for (let ii = 0; ii < n; ii += b) for (let kk = 0; kk < n; kk += b) for (let jj = 0; jj < n; jj += b) {
      const ie = Math.min(ii + b, n), ke = Math.min(kk + b, n), je = Math.min(jj + b, n);
      for (let i = ii; i < ie; i++) for (let k = kk; k < ke; k++) { const a = A[i * n + k], r = k * n, o = i * n; for (let j = jj; j < je; j++) C[o + j] += a * B[r + j]; }
    }
    return C; },
  action(id, api) {
    const L = this.log();
    if (id === "clear") { L.runs = []; L.blocks = []; return; }
    if (id === "run") this.runOnce(api.p.n, api.p.bs);
    if (id === "sweep") [64, 128, 256].forEach((n) => this.runOnce(n, api.p.bs));
    if (id === "bsweep") {   // blocked algorithm only, every block size, at the current n
      const n = api.p.n, A = this.rand(n, 4), B = this.rand(n, 7), ref = this.ikj(A, B, n);
      L.blocks = [8, 16, 32, 64, 128].map((b) => {
        const t0 = performance.now(), C = this.blocked(A, B, n, b), t = Math.max(performance.now() - t0, 0.01);
        let diff = 0; for (let i = 0; i < n * n; i++) diff = Math.max(diff, Math.abs(C[i] - ref[i]));
        return { n, b, t, diff };
      });
    }
  },
  runOnce(n, bs) {
    const L = this.log(), A = this.rand(n, 4), B = this.rand(n, 7);
    const time = (f) => { const t0 = performance.now(); const C = f(); return [Math.max(performance.now() - t0, 0.01), C]; };
    const [t1, C1] = time(() => this.ijk(A, B, n)), [t2, C2] = time(() => this.ikj(A, B, n)), [t3, C3] = time(() => this.blocked(A, B, n, bs));
    let diff = 0; for (let i = 0; i < n * n; i++) diff = Math.max(diff, Math.abs(C1[i] - C2[i]), Math.abs(C1[i] - C3[i]));
    L.runs.push({ n, bs, t: [t1, t2, t3], diff });
    if (L.runs.length > 30) L.runs.shift();
  },
  readouts(api) {
    const L = this.log(), r = L.runs[L.runs.length - 1];
    const ns = new Set(L.runs.filter((q) => q.diff < 1e-9).map((q) => q.n));
    const bs512 = new Set(L.runs.filter((q) => q.n === 512 && q.diff < 1e-9).map((q) => q.bs));
    (L.blocks || []).filter((q) => q.n === 512 && q.diff < 1e-9).forEach((q) => bs512.add(q.b));
    if (r && r.n === 256 && r.diff < 1e-9) api.done("same");
    if (ns.size >= 3) api.done("grow");
    if (bs512.size >= 2) api.done("block");
    if (!r) return [[["状态", "Status"], api.T("点“运行”开始", "press Run")], [["运算量 2n³", "Flops 2n³"], api.fmt(2 * api.p.n ** 3, 0)]];
    const gf = (t) => api.fmt(2 * r.n ** 3 / (t * 1e6), 2) + " GFLOPS";
    return [[["上次运行", "Last run"], "n = " + r.n + api.T("，块大小 ", ", block ") + r.bs],
            [["运算量 2n³", "Flops 2n³"], api.fmt(2 * r.n ** 3, 0)],
            [["ijk 三重循环", "ijk triple loop"], api.fmt(r.t[0], 1) + " ms, " + gf(r.t[0])],
            [["ikj（行连续）", "ikj (row-contiguous)"], api.fmt(r.t[1], 1) + " ms, " + gf(r.t[1])],
            [["分块 ikj", "Blocked ikj"], api.fmt(r.t[2], 1) + " ms, " + gf(r.t[2])],
            [["三者的最大差", "Largest difference"], r.diff.toExponential(1)],
            [["已记录的 n", "Sizes logged"], [...ns].sort((a, b) => a - b).join(", ") || "—"],
            [["块大小比较（n = " + this.bn(L) + "）", "Block sizes (n = " + this.bn(L) + ")"],
             (L.blocks || []).map((q) => q.b + ": " + api.fmt(q.t, 0) + " ms").join(", ") || "—"]];
  },
  bn(L) { return L.blocks && L.blocks.length ? L.blocks[0].n : "—";
  },
  draw(api) {
    const { w, h } = api, L = this.log(), r = L.runs[L.runs.length - 1], muted = api.css("--muted");
    const cols = [api.css("--blue"), api.css("--green"), api.css("--red")], names = [api.T("ijk", "ijk"), api.T("ikj", "ikj"), api.T("分块", "blocked")];
    if (!r) { api.label(api.T("点“运行”，三种算法各算一遍", "Press Run to time the three algorithms"), w / 2, h / 2, muted, 16, "center"); return; }
    // left: the last run's times as bars
    const x0 = 30, bw = w * 0.38, top = 40, hh = h - 90, tmax = Math.max(...r.t);
    api.label(api.T("上次运行的耗时（ms）", "last run, time (ms)"), x0, 22, muted, 13);
    r.t.forEach((t, i) => {
      const bh = hh * t / tmax, x = x0 + i * bw / 3 + 8;
      api.rect(x, top + hh - bh, bw / 3 - 16, bh, cols[i]);
      api.label(api.fmt(t, 1), x + (bw / 3 - 16) / 2, top + hh - bh - 6, api.css("--ink"), 12, "center");
      api.label(names[i], x + (bw / 3 - 16) / 2, top + hh + 18, muted, 13, "center");
    });
    // right: time against n (log–log) for every run logged, one colour per algorithm, with an n³ guide
    const gx = w * 0.52, gw = w * 0.44, gy = top, gh = hh, runs = L.runs;
    const lx = (n) => Math.log2(n / 64) / Math.log2(12), ts = runs.flatMap((q) => q.t), lo = Math.log10(Math.min(...ts)) - 0.2, hi = Math.log10(Math.max(...ts)) + 0.2;
    const X = (n) => gx + gw * lx(n), Y = (t) => gy + gh * (1 - (Math.log10(t) - lo) / ((hi - lo) || 1));
    api.rect(gx, gy, gw, gh, null, api.css("--grid"));
    [64, 128, 256, 512, 768].forEach((n) => api.label(String(n), X(n), gy + gh + 16, muted, 11, "center"));
    api.label(api.T("耗时与 n（双对数）", "time vs n (log–log)"), gx, 22, muted, 13);
    runs.forEach((q) => q.t.forEach((t, i) => api.circle(X(q.n), Y(t), 3.5, cols[i], null)));
    const ref = runs.find((q) => q.n === Math.min(...runs.map((z) => z.n)));
    const nmax = Math.max(...runs.map((z) => z.n));
    if (ref && nmax > ref.n) { const t0 = ref.t[0], t1 = t0 * (nmax / ref.n) ** 3;
      api.line(X(ref.n), Y(t0), X(nmax), Y(t1), muted, 1);
      api.label(api.T("n³ 参考线（从最小的 n 出发）", "n³ guide (from the smallest n)"), X(nmax) - 4, Math.min(Y(t1) + 14, gy + gh - 4), muted, 11, "right"); }
  },
});
