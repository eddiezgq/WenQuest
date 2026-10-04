// 实验 5.8 分块矩阵乘法的数据流（配 5.8、5.9 节）。用平台实验工具包的 GPU 执行模拟器 api.gpu 的部分 ⑤（gemmTiles），
// 它与书中程序用的 conventions/gpusim.py 的 gemm_tiles 逐行对应：C = AB，n×n 单精度，线程块负责 C 的 b×b 块，沿 K 每步 b_k，
// 每个线程算 t×t 个元素；显存读量不计缓存。屋顶线取 A10（单精度 31.2 TFLOP/s，600 GB/s）。
WQ.lab({
  title: ["实验 5.8 分块矩阵乘法的数据流", "Lab 5.8 Data flow of a tiled matrix multiplication"],
  goal: ["改变线程块的块大小、沿 K 的步长和每个线程的寄存器分块，看数据怎样从显存进入共享内存，读出显存读取量、计算强度和每次乘加读共享内存的次数，找出既不受显存限制、也不受共享内存限制的分块。",
         "Change the block tile, the K step and the per-thread register tile; watch data move from memory into shared memory and read off the memory traffic, the intensity and the shared-memory reads per FMA. Find a tiling limited by neither."],
  scenes: [
    { id: "smem", name: ["共享内存分块", "Shared-memory tiles"],
      problem: { title: ["问题：一个数从显存读进来，能用几次", "Problem: how many times is each value used once loaded"],
                 text: ["朴素的矩阵乘法每做一次乘加就从显存读两个数。把 A、B 切成块放进共享内存，块内的线程共用，显存读量能降多少？",
                        "A naive multiplication reads two values from memory per FMA. If A and B are cut into tiles shared by a block, how far does the traffic fall?"] },
      params: { lgB: { value: 5 }, lgK: { value: 5 }, lgT: { value: 0 } } },
    { id: "reg", name: ["寄存器分块", "Register tiles"],
      problem: { title: ["问题：共享内存也有带宽", "Problem: shared memory has a bandwidth too"],
                 text: ["每个 SM 每周期能做 128 次乘加，共享内存却只能供 32 个字。让每个线程算 t×t 个输出，从共享内存取来的数在寄存器里多用几次。",
                        "An SM does 128 FMAs a cycle but shared memory supplies only 32 words. Let each thread compute t×t outputs so every value fetched is reused in registers."] },
      params: { lgB: { value: 7 }, lgK: { value: 3 }, lgT: { value: 3 } } },
  ],
  params: [
    { id: "lgN", name: ["矩阵大小 n = 2^…", "Matrix size n = 2^…"], min: 6, max: 12, step: 1, value: 12, digits: 0 },
    { id: "lgB", name: ["线程块的块 b = 2^…（0 即不分块）", "Block tile b = 2^… (0: no tiling)"], min: 0, max: 8, step: 1, value: 5, digits: 0 },
    { id: "lgK", name: ["沿 K 的步长 b_k = 2^…", "K step b_k = 2^…"], min: 0, max: 6, step: 1, value: 5, digits: 0 },
    { id: "lgT", name: ["每个线程 t×t，t = 2^…", "Per thread t×t, t = 2^…"], min: 0, max: 3, step: 1, value: 0, digits: 0 },
    { id: "stages", name: ["缓冲级数（2 = 双缓冲）", "Buffers (2 = double buffering)"], min: 1, max: 2, step: 1, value: 1, digits: 0 },
    { id: "speed", name: ["动画速度（步/秒）", "Animation speed (steps/s)"], min: 1, max: 30, step: 1, value: 4, digits: 0 },
  ],
  legend: [{ color: "var(--red)", name: ["A 的块", "tile of A"] }, { color: "var(--blue)", name: ["B 的块", "tile of B"] },
           { color: "var(--amber)", name: ["C 的块（这个线程块负责）", "tile of C (this block)"] }],
  tasks: [
    { id: "naive", text: ["把块设为 2^0（不分块）：计算强度是多少？与算例 5.7.2 比较。", "Set the tile to 2^0 (no tiling): what is the intensity? Compare with Example 5.7.2."],
      demo: { scene: "smem", set: { lgN: 12, lgB: 0, lgK: 5, lgT: 0, stages: 1 }, press: [] } },
    { id: "t32", text: ["块 32×32、步长 32：显存读量是不分块时的几分之一？每次乘加读几次共享内存？", "32×32 tiles, K step 32: what fraction of the naive traffic? Shared reads per FMA?"],
      demo: { scene: "smem", set: { lgN: 12, lgB: 5, lgK: 5, lgT: 0, stages: 1 }, press: [] } },
    { id: "watch", text: ["n 取 2^8，按“开始”，看线程块沿 K 一步步装入 A、B 的块，直到最后一步。", "With n = 2^8 press Start and watch the block load tiles of A and B step by step to the end."],
      demo: { scene: "smem", set: { lgN: 8, lgB: 5, lgK: 5, lgT: 0, stages: 1, speed: 4 }, press: ["start"] } },
    { id: "reg", text: ["块 128×128、步长 8、每个线程 8×8：每次乘加读共享内存的次数降到预算（0.25）以内了吗？", "128×128 tiles, K step 8, 8×8 per thread: are shared reads per FMA within the budget (0.25)?"],
      demo: { scene: "reg", set: { lgN: 12, lgB: 7, lgK: 3, lgT: 3, stages: 1 }, press: [] } },
    { id: "ridge", text: ["加大块，直到计算强度越过 A10 单精度的屋脊（52 FLOP/B）。这时线程数与共享内存是否还在上限之内？", "Grow the tile until the intensity passes the A10 FP32 ridge (52 FLOP/B). Are threads and shared memory still within limits?"],
      demo: { scene: "reg", set: { lgN: 12, lgB: 8, lgK: 3, lgT: 3, stages: 1 }, press: [] } },
    { id: "dbuf", text: ["改成双缓冲：哪些读数变了，哪些没变？", "Switch to double buffering: which readouts change and which do not?"],
      demo: { scene: "reg", set: { lgN: 12, lgB: 7, lgK: 3, lgT: 3, stages: 2 }, press: [] } },
  ],
  think: ["算例 5.8.1 说计算强度约为 b/4。为什么与沿 K 的步长 b_k 无关？b_k 影响的是什么？", "Example 5.8.1 says the intensity is about b/4. Why does it not depend on the K step b_k? What does b_k affect?"],

  P: 31.2e12, BW: 600e9, BUDGET: 0.25,
  cfg(api) {
    const n = 2 ** api.p.lgN, b = Math.min(2 ** api.p.lgB, n), bk = Math.min(2 ** api.p.lgK, n), t = Math.min(2 ** api.p.lgT, b);
    const nb = n / b, blk = [Math.min(1, nb - 1), Math.min(2, nb - 1)];
    const r = api.gpu.gemmTiles({ M: n, N: n, K: n, bm: b, bn: b, bk, tm: t, tn: t, stages: api.p.stages, size: 4, block: blk });
    return { n, b, bk, t, nb, blk, r };
  },
  reset(api, s) { s.step = 0; s.acc = 0; },
  update(dt, api, s) {
    const { r } = this.cfg(api);
    s.acc += dt * api.p.speed;
    while (s.acc >= 1 && s.step < r.steps.length - 1) { s.acc -= 1; s.step += 1; }
    if (s.step >= r.steps.length - 1) {
      if (api.scene === "smem" && r.steps.length > 1) api.done("watch");
      api.stop();
    }
  },
  readouts(api, s) {
    const { n, b, bk, t, r } = this.cfg(api), p = api.p;
    if (b === 1) api.done("naive");
    if (b === 32 && bk === 32 && t === 1 && n === 4096) api.done("t32");
    if (b === 128 && bk === 8 && t === 8 && r.smem_per_fma <= this.BUDGET) api.done("reg");
    if (r.intensity >= this.P / this.BW) api.done("ridge");
    if (p.stages === 2 && b >= 32) api.done("dbuf");
    const step = Math.min(s.step || 0, r.steps.length - 1);
    const warn = (ok) => (ok ? "" : api.T("（超过上限）", " (over the limit)"));
    return [[["显存读取量（不计缓存）", "Memory reads (no caches)"], api.fmt(r.g_read * 4 / 1e9, 2) + " GB"],
            [["计算强度", "Intensity"], api.fmt(r.intensity, 2) + " FLOP/B（" + api.T("屋脊 ", "ridge ") + api.fmt(this.P / this.BW, 0) + "）"],
            [["每次乘加读共享内存", "Shared reads per FMA"], api.fmt(r.smem_per_fma, 3) + api.T("（预算 0.25）", " (budget 0.25)")],
            [["每个线程块的线程数", "Threads per block"], String(r.threads) + warn(r.threads <= 1024)],
            [["每个线程块的共享内存", "Shared memory per block"], api.fmt(r.smem_bytes / 1024, 1) + " KB" + warn(r.smem_bytes <= 99 * 1024)],
            [["每个线程的累加寄存器", "Accumulators per thread"], String(r.acc_regs)],
            [["当前步 / 总步数", "Step / steps"], (step + 1) + " / " + r.steps.length],
            [["可达到的算力（屋顶线）", "Attainable (roofline)"], api.fmt(Math.min(this.P, this.BW * r.intensity) / 1e12, 2) + " TFLOP/s"]];
  },
  draw(api, s) {
    const { w, h } = api, m = 14, { n, b, blk, r } = this.cfg(api);
    const step = Math.min(s.step || 0, r.steps.length - 1), st = r.steps[step];
    // 左：A（左下）、B（右上）、C（右下）
    const side = Math.max(40, Math.min((w * 0.55 - 3 * m) / 2, (h - 3 * m - 40) / 2)), ax = m, bx = m * 2 + side, by = m + 16, cy = by + side + m + 6;
    const S = side / n;
    const box = (x, y, rect, rgb, alpha) => {
      const [r0, r1, c0, c1] = rect;
      api.rect(x + c0 * S, y + r0 * S, Math.max(2, (c1 - c0) * S), Math.max(2, (r1 - r0) * S), `rgba(${rgb},${alpha})`);
    };
    for (const [x, y, name] of [[ax, cy, "A"], [bx, by, "B"], [bx, cy, "C"]]) {
      api.rect(x, y, side, side, "rgba(110,119,129,0.10)", api.css("--grid"));
      api.label(name, x + side / 2, y - 4, api.css("--muted"), 12, "center");
    }
    const RED = "207,34,46", BLUE = "31,111,235", AMB = "201,143,0";
    box(ax, cy, [st.a[0], st.a[1], 0, n], RED, 0.12);                  // 这个线程块要用到的 A 的一行块、B 的一列块
    box(bx, by, [0, n, st.b[2], st.b[3]], BLUE, 0.12);
    for (let k = Math.max(0, step - 64); k <= step; k++) {               // 已经用过的块淡一点（只画最近的 64 步）
      const sk = r.steps[k];
      box(ax, cy, sk.a, RED, k === step ? 0.9 : 0.3);
      box(bx, by, sk.b, BLUE, k === step ? 0.9 : 0.3);
    }
    box(bx, cy, [blk[0] * b, blk[0] * b + b, blk[1] * b, blk[1] * b + b], AMB, 0.9);
    api.label(api.T(`线程块 (${blk[0]}, ${blk[1]})：第 ${step + 1} 步，深色两块在共享内存里`, `block (${blk[0]}, ${blk[1]}): step ${step + 1}; the dark tiles are in shared memory`),
              ax, h - m, api.css("--muted"), 12);
    // 右：A10 单精度屋顶线
    const x0 = w * 0.58 + 30, y0 = m + 16, pw = w - x0 - m, ph = h - y0 - m - 34;
    if (pw < 80) return;
    const lx0 = -1, lx1 = 3, ly0 = 10.5, ly1 = 13.8;
    const X = (I) => x0 + (Math.log10(I) - lx0) / (lx1 - lx0) * pw, Y = (p) => y0 + ph - (Math.log10(p) - ly0) / (ly1 - ly0) * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"));
    for (let e = lx0; e <= lx1; e++) api.label("10^" + e, X(10 ** e), y0 + ph + 14, api.css("--muted"), 10, "center");
    for (let e = 11; e <= 13; e++) api.label(api.fmt(10 ** e / 1e12, e < 12 ? 1 : 0) + " T", x0 - 4, Y(10 ** e) + 4, api.css("--muted"), 10, "right");
    const ridge = this.P / this.BW;
    api.line(X(0.1), Y(this.BW * 0.1), X(ridge), Y(this.P), api.css("--ink"), 2.5);
    api.line(X(ridge), Y(this.P), X(1000), Y(this.P), api.css("--ink"), 2.5);
    const I = Math.min(Math.max(r.intensity, 0.1), 1000);
    api.circle(X(I), Y(Math.min(this.P, this.BW * I)), 6, api.css("--accent"));
    api.label(api.T("A10 单精度屋顶线", "A10 FP32 roofline"), x0 + 6, y0 + 14, api.css("--muted"), 11);
    api.label(api.T("计算强度（FLOP/B）", "intensity (FLOP/B)"), x0 + pw, y0 + ph + 28, api.css("--muted"), 11, "right");
  },
});
