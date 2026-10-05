// 实验 10.1 同一段矩阵乘法在两种架构上怎样执行（配 10.1、10.2、10.3 节）。两个场景：
//   simt：GPU 的 SIMT 方式——一个线程算一个输出，线程束（32 道）或波前（64 道）一起走；统计一个线程块的波前数、
//         线程束内归约要几层、一条访存指令一次请求多少字节、共享内存允许驻留几块（与程序 10.2.1 的公式相同）；
//   cube：昇腾的立方单元——一次 16×16×16 的矩阵乘加；统计指令条数、片上缓冲要放多少数据、三段流水的时间
//         （与程序 10.3.1 相同：n 块要 n + 2 段）。
// 两个场景用同一个矩阵尺寸，便于对照“同一件事，两种硬件怎样分工”。
WQ.lab({
  title: ["实验 10.1 同一段矩阵乘法在两种架构上", "Lab 10.1 One matrix multiply, two architectures"],
  goal: ["改变矩阵尺寸、线程束宽度、分块大小与数据块数，看同一个矩阵乘法在 SIMT 的 GPU 和昇腾的立方单元上各被拆成什么样，各要搬多少数据。",
         "Change the size, the warp width, the tile size and the number of tiles, and see how the same matrix multiply is split on a SIMT GPU and on a cube unit, and how much data each moves."],
  scenes: [
    { id: "simt", name: ["SIMT（GPU）", "SIMT (GPU)"],
      problem: { title: ["问题：线程束 32 道还是 64 道", "Problem: 32 or 64 lanes per warp"],
                 text: ["同一个核函数搬到 AMD 的卡上，线程束变成 64 道的波前。每块的波前数、归约的层数、一次访存请求的字节数都变了——哪些写法会因此出错？",
                        "Move the same kernel to an AMD GPU and the warp becomes a 64-lane wavefront. Waves per block, reduction steps and bytes per request all change — which habits break?"] } },
    { id: "cube", name: ["立方单元（昇腾）", "Cube unit (Ascend)"],
      problem: { title: ["问题：一次吃下 16×16×16", "Problem: 16×16×16 at a time"],
                 text: ["昇腾的立方单元一条指令做一次 16×16×16 的矩阵乘加，片上缓冲由程序自己搬。同一个矩阵乘法要多少条指令、搬多少数据？三段流水能快多少？",
                        "A cube unit does a 16×16×16 matrix multiply-accumulate per instruction and the buffers are moved by hand. How many instructions and how much traffic? How much does the three-stage pipeline help?"] } },
  ],
  params: [
    { id: "n", name: ["矩阵尺寸 n（n×n×n）", "Size n (n×n×n)"], min: 64, max: 1024, step: 64, value: 256, digits: 0 },
    { id: "warp", name: ["线程束宽度（32 或 64）", "Warp width (32 or 64)"], min: 32, max: 64, step: 32, value: 32, digits: 0 },
    { id: "block", name: ["每个线程块的线程数", "Threads per block"], min: 64, max: 1024, step: 64, value: 256, digits: 0 },
    { id: "tile", name: ["共享内存分块 T（T×T）", "Shared-memory tile T"], min: 8, max: 64, step: 8, value: 32, digits: 0 },
    { id: "smem", name: ["每个 SM / 计算单元的片上存储（KB）", "On-chip memory per SM/CU (KB)"], min: 32, max: 192, step: 4, value: 100, digits: 0 },
    { id: "tiles", name: ["三段流水的数据块数", "Tiles in the pipeline"], min: 1, max: 64, step: 1, value: 16, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["搬入", "CopyIn"] }, { color: "var(--red)", name: ["计算", "Compute"] },
           { color: "var(--green)", name: ["搬出", "CopyOut"] }],
  tasks: [
    { id: "wave", text: ["把线程束宽度从 32 改成 64（每块 256 个线程）：波前数、归约层数、一次访存请求各变成多少？哪一项会让写死 16 的归约出错？",
                         "Switch the warp width from 32 to 64 with 256 threads per block: how do waves, reduction steps and bytes per request change? Which one breaks a reduction hard-coded to 16?"],
      demo: { scene: "simt", set: { warp: 64, block: 256 }, press: [] } },
    { id: "occ", text: ["T = 32，片上存储依次设成 100 KB（A10）、160 KB（CDNA 4），最后停在 64 KB（CDNA 3）：各能驻留几个线程块？",
                        "With T = 32, set the on-chip memory to 100 KB (A10), then 160 KB (CDNA 4), and finally 64 KB (CDNA 3): how many blocks fit in each?"],
      demo: { scene: "simt", set: { smem: 64, tile: 32 }, press: [] } },
    { id: "cube", text: ["切到“立方单元”：n = 256 要多少条立方指令？把 A、B 整块放进片上缓冲，显存读写少多少？",
                         "Switch to the cube unit: how many cube instructions for n = 256? How much traffic is saved by holding A and B on chip?"],
      demo: { scene: "cube", set: { n: 256 }, press: [] } },
    { id: "pipe", text: ["数据块数从 1 加到 64：三段流水比各段串行快多少？什么时候接近 3 倍？与式 (9.4.1) 的气泡对照。",
                         "Raise the tiles from 1 to 64: how much faster is the pipeline than running the stages serially? When does it approach 3×? Compare with the bubble in (9.4.1)."],
      demo: { scene: "cube", set: { tiles: 64 }, press: [] } },
  ],
  think: ["两种架构算的是同一个矩阵乘法。为什么“把数据留在片上多用几次”在两边都是第一位的优化？",
          "Both architectures compute the same product. Why is “keep data on chip and reuse it” the first optimization on both?"],

  simt(api) {
    const p = api.p, waves = Math.ceil(p.block / p.warp), steps = Math.round(Math.log2(p.warp));
    const smemPerBlock = 2 * p.tile * p.tile * 4;                 // As 与 Bs 各 T×T 个单精度数
    return { waves, steps, req: p.warp * 4, lines: p.warp * 4 / 128, smemPerBlock,
             blocks: Math.floor(p.smem * 1024 / smemPerBlock), partials: waves * 4,
             flop: 2 * p.n * p.n * p.n, outTiles: Math.ceil(p.n / p.tile) * Math.ceil(p.n / p.tile) };
  },
  cube(api) {
    const p = api.p, M = 16;
    const insts = (p.n / M) * (p.n / M) * (p.n / M);
    const naive = (p.n / M) * (p.n / M) * (M * p.n + p.n * M) * 2;  // 每个输出块各自去显存读
    const once = (p.n * p.n + p.n * p.n) * 2, wr = p.n * p.n * 4;
    return { insts, flop: 2 * p.n * p.n * p.n, naive, once, wr, save: naive / once,
             ai: 2 * p.n * p.n * p.n / (once + wr), abKB: once / 1024,
             pipe: p.tiles + 2, serial: 3 * p.tiles, speed: 3 * p.tiles / (p.tiles + 2),
             bubble: 2 / (p.tiles + 2) * 100 };
  },
  reset(api, s) {},
  readouts(api, s) {
    const p = api.p;
    if (api.scene === "cube") {
      const r = this.cube(api);
      if (p.n === 256) api.done("cube");
      if (p.tiles >= 64) api.done("pipe");
      return [[["立方指令条数", "Cube instructions"], r.insts.toLocaleString()],
              [["运算量", "FLOP"], r.flop.toExponential(2)],
              [["显存读：每块各读 / 整块驻留片上", "Traffic: per tile / held on chip"], (r.naive / 1e6).toFixed(1) + " MB / " + (r.once / 1e6).toFixed(2) + " MB"],
              [["少读多少倍 / 计算强度", "Saving / intensity"], r.save.toFixed(0) + api.T(" 倍", "×") + " / " + r.ai.toFixed(0) + " FLOP/B"],
              [["A、B 在片上要占", "A and B on chip"], (r.abKB / 1024).toFixed(2) + " MB"],
              [["三段流水 / 各段串行", "Pipelined / serial"], r.pipe + " / " + r.serial + api.T(" 段", " stages")],
              [["加速 / 气泡", "Speedup / bubble"], r.speed.toFixed(2) + api.T(" 倍", "×") + " / " + r.bubble.toFixed(1) + "%"]];
    }
    const r = this.simt(api);
    if (p.warp === 64 && p.block === 256) api.done("wave");
    if (p.tile === 32 && p.smem === 64) api.done("occ");
    return [[["每块的线程束 / 波前数", "Warps or waves per block"], String(r.waves)],
            [["线程束内归约的层数", "In-warp reduction steps"], String(r.steps)],
            [["一条 32 位访存指令", "One 32-bit load per lane"], r.req + " B" + api.T("（" + r.lines + " 个缓存行）", " (" + r.lines + " cache lines)")],
            [["每块的共享内存", "Shared memory per block"], (r.smemPerBlock / 1024).toFixed(0) + " KB"],
            [["片上存储允许驻留", "Blocks allowed by on-chip memory"], r.blocks + api.T(" 块", " blocks")],
            [["输出分块数 / 运算量", "Output tiles / FLOP"], r.outTiles.toLocaleString() + " / " + r.flop.toExponential(2)]];
  },
  draw(api, s) {
    const { w, h } = api, m = 24;
    api.css("--ink");
    if (api.scene === "cube") {
      const r = this.cube(api), n = Math.min(api.p.tiles, 12);
      const cw = Math.min(42, (w - 2 * m) / (n + 2) ), ch = Math.min(22, (h - 90) / Math.max(n, 1));
      api.label(api.T("三段流水（最多画 12 块）", "Three-stage pipeline (first 12 tiles)"), m, 26, api.css("--ink"), 13);
      for (let i = 0; i < n; i++) {
        const y = 40 + i * ch;
        const cols = ["--blue", "--red", "--green"];
        for (let st = 0; st < 3; st++) api.rect(m + (i + st) * cw, y, cw - 3, ch - 3, api.css(cols[st]));
        api.label(api.T("第 " + (i + 1) + " 块", "tile " + (i + 1)), m + (n + 4) * cw + 8, y + ch - 6, api.css("--muted"), 10);
      }
      api.label(api.T("共 " + r.pipe + " 段（串行要 " + r.serial + " 段）", r.pipe + " stages in all (" + r.serial + " if serial)"),
                m, 40 + n * ch + 24, api.css("--ink"), 12);
      return;
    }
    const r = this.simt(api), lanes = api.p.warp, per = Math.min(lanes, 32);
    api.label(api.T("一个波前的 " + lanes + " 道（每行 32 道）", lanes + " lanes of one wave (32 per row)"), m, 26, api.css("--ink"), 13);
    const bw = Math.min(16, (w - 2 * m) / 34);
    for (let i = 0; i < lanes; i++) {
      const row = Math.floor(i / per), col = i % per;
      api.rect(m + col * (bw + 2), 40 + row * (bw + 4), bw, bw, api.css(i < 32 ? "--blue" : "--red"));
    }
    const y0 = 40 + Math.ceil(lanes / per) * (bw + 4) + 16;
    api.label(api.T("归约：每层活动的道数", "Reduction: active lanes per step"), m, y0, api.css("--ink"), 13);
    for (let lv = 0; lv <= r.steps; lv++) {
      const act = lanes >> lv, shown = Math.min(act, 16);
      for (let i = 0; i < shown; i++) api.rect(m + i * (bw + 2), y0 + 10 + lv * (bw + 3), bw, bw - 2, api.css("--blue"));
      api.label(String(act), m + 17 * (bw + 2), y0 + 10 + lv * (bw + 3) + bw - 3, api.css("--muted"), 10);
    }
  },
});
