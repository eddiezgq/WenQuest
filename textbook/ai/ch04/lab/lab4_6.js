// 实验 4.6 合并访问与存储体冲突（配 4.6、4.7 节）。用平台实验工具包的 GPU 执行模拟器 api.gpu 的部分 ③（合并访问）与
// 部分 ④（存储体冲突），它与书中程序用的 conventions/gpusim.py 逐行对应。
// 合并访问：一个线程束 32 个线程各读一个元素，显存按 32 字节扇区搬运，按 128 字节缓存行组织；不模拟缓存命中。
// 存储体冲突：共享内存 32 个存储体，每个 4 字节；同一存储体的不同字要分几次读，同一个字广播。
WQ.lab({
  title: ["实验 4.6 合并访问与存储体冲突", "Lab 4.6 Coalescing and bank conflicts"],
  goal: ["改变一个线程束的访问方式，看全局内存要搬运多少个扇区、共享内存有几路存储体冲突，找出“好”的访问方式。",
         "Change how a warp accesses memory and see how many sectors global memory moves and how many ways shared memory conflicts; find the good patterns."],
  scenes: [
    { id: "glob", name: ["合并访问", "Coalescing"],
      problem: { title: ["问题：同样读 128 字节，为什么有时要搬 1 KB", "Problem: why reading 128 bytes can move 1 KB"],
                 text: ["检测程序里，一个线程束的 32 个线程各读一个像素的值。像素在内存中怎样排、线程怎样取，决定了显存实际要搬多少数据。",
                        "In the inspection code the 32 threads of a warp each read one pixel value. How pixels are laid out and how threads pick them decides how much the memory actually moves."] } },
    { id: "bank", name: ["存储体冲突", "Bank conflicts"],
      problem: { title: ["问题：按列读共享内存为什么慢 32 倍", "Problem: why reading a column of shared memory is 32× slower"],
                 text: ["矩阵转置先把 32×32 的块放进共享内存，再按列读出。按列读时 32 个线程落在同一个存储体上；每行多留一个字就好了。为什么？",
                        "A transpose stores a 32×32 tile in shared memory and reads it by columns. Then all 32 threads hit one bank; one extra word per row fixes it. Why?"] },
      params: { k: { value: 2 } } },
  ],
  params: [
    { id: "mp", name: ["合并：访问方式（0 连续 · 1 错位 · 2 跨步 · 3 结构体数组 · 4 随机）", "Coalescing: pattern (0 contiguous · 1 offset · 2 stride · 3 array of structs · 4 random)"], min: 0, max: 4, step: 1, value: 0, digits: 0 },
    { id: "ms", name: ["合并：跨步（元素）", "Coalescing: stride (elements)"], min: 1, max: 64, step: 1, value: 2, digits: 0 },
    { id: "mo", name: ["合并：错位（字节）", "Coalescing: offset (bytes)"], min: 0, max: 124, step: 4, value: 4, digits: 0 },
    { id: "sz", name: ["合并：每个线程读的字节（0 → 4 · 1 → 8 · 2 → 16，对应 float、float2、float4）", "Coalescing: bytes per thread (0 → 4 · 1 → 8 · 2 → 16: float, float2, float4)"], min: 0, max: 2, step: 1, value: 0, digits: 0 },
    { id: "st", name: ["合并：结构体大小（字节）", "Coalescing: struct size (bytes)"], min: 8, max: 64, step: 4, value: 24, digits: 0 },
    { id: "bp", name: ["冲突：访问方式（0 跨步 · 1 按列读 32×32 块 · 2 同一个字 · 3 随机）", "Banks: pattern (0 stride · 1 column of a 32×32 tile · 2 same word · 3 random)"], min: 0, max: 3, step: 1, value: 0, digits: 0 },
    { id: "k", name: ["冲突：跨步（字）", "Banks: stride (words)"], min: 1, max: 33, step: 1, value: 1, digits: 0 },
    { id: "pad", name: ["冲突：每行填充（字）", "Banks: padding per row (words)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--blue)", name: ["用到的扇区 / 一次读", "sector used / one pass"] }, { color: "var(--amber)", name: ["线程", "thread"] },
           { color: "var(--red)", name: ["冲突（要再读一次）", "conflict (one more pass)"] }],
  tasks: [
    { id: "cont", text: ["合并访问：连续读 4 字节，确认只搬 4 个扇区、有效带宽比 100%。", "Coalescing: contiguous 4-byte reads move only 4 sectors, 100% efficiency."],
      demo: { scene: "glob", set: { mp: 0, sz: 0 }, press: [] } },
    { id: "stride", text: ["改成跨步 2：扇区数变成多少？跨步多大以后不再变？", "Stride 2: how many sectors? Beyond which stride does it stop growing?"],
      demo: { scene: "glob", set: { mp: 2, ms: 2, sz: 0 }, press: [] } },
    { id: "aos", text: ["结构体数组（每个粒子 24 字节，只读 x）：有效带宽比是多少？与数组结构体比较。", "Array of structs (24-byte particles, read x only): what efficiency? Compare with a struct of arrays."],
      demo: { scene: "glob", set: { mp: 3, st: 24, sz: 0 }, press: [] } },
    { id: "vec", text: ["连续访问时把每个线程读的字节改成 16（float4）：扇区数与有效带宽比怎样？", "Contiguous with 16 bytes per thread (float4): sectors and efficiency?"],
      demo: { scene: "glob", set: { mp: 0, sz: 2 }, press: [] } },
    { id: "col", text: ["存储体冲突：按列读 32×32 的块，读出冲突路数；再把填充改成 1。", "Banks: read a column of a 32×32 tile, note the ways, then set padding to 1."],
      demo: { scene: "bank", set: { bp: 1, pad: 1 }, press: [] } },
    { id: "odd", text: ["跨步取 1 到 8，哪些跨步没有冲突？总结规律。", "Try strides 1 to 8: which have no conflict? State the rule."],
      demo: { scene: "bank", set: { bp: 0, k: 3 }, press: [] } },
  ],
  think: ["为什么“奇数跨步没有存储体冲突”，而全局内存的跨步访问不论奇偶都会多搬数据？", "Why do odd strides avoid bank conflicts while strided global access moves extra data whatever the stride?"],

  KINDS: ["contiguous", "offset", "stride", "aos", "random"],
  glob(api) {
    const p = api.p, size = [4, 8, 16][p.sz] || 4;
    const addrs = api.gpu.addresses({ kind: this.KINDS[p.mp], size, k: p.mp === 4 ? 64 : p.ms, offset: p.mo, struct: p.st, seed: 3 });
    return { addrs, size, r: api.gpu.coalesce(addrs, size) };
  },
  bank(api) {
    const p = api.p, kinds = ["stride", "column", "same", "random"];
    const words = api.gpu.bankWords({ kind: kinds[p.bp], k: p.k, pad: p.pad, col: 3, seed: 9 });
    return { words, r: api.gpu.banks(words) };
  },
  readouts(api) {
    const p = api.p;
    if (api.scene === "glob") {
      const { r, size } = this.glob(api);
      if (p.mp === 0 && size === 4 && r.sectors === 4) api.done("cont");
      if (p.mp === 2 && p.ms === 2 && size === 4) api.done("stride");
      if (p.mp === 3 && p.st === 24 && size === 4) api.done("aos");
      if (p.mp === 0 && size === 16) api.done("vec");
      return [[["请求的字节", "Bytes requested"], String(r.requested)],
              [["搬运的扇区（32 字节）", "Sectors moved (32 B)"], String(r.sectors)],
              [["涉及的缓存行（128 字节）", "Cache lines (128 B)"], String(r.lines)],
              [["搬运的字节", "Bytes moved"], String(r.moved)],
              [["有效带宽比", "Efficiency"], (100 * r.eff).toFixed(1) + "%"]];
    }
    const { r } = this.bank(api);
    if (p.bp === 1 && p.pad === 1 && r.ways === 1) api.done("col");
    if (p.bp === 0 && p.k % 2 === 1 && p.k > 1) api.done("odd");
    return [[["冲突路数（要读几次）", "Ways (passes needed)"], String(r.ways)],
            [["用到的存储体", "Banks used"], String(r.load.filter((x) => x > 0).length) + " / 32"],
            [["相对无冲突的时间", "Time vs conflict-free"], r.ways + " ×"]];
  },
  draw(api) {
    const { w, h } = api, m = 16;
    if (api.scene === "glob") {
      const { addrs, size, r } = this.glob(api);
      const lo = Math.floor(Math.min(...addrs) / 128) * 128, hi = Math.ceil((Math.max(...addrs) + size) / 128) * 128;
      const span = Math.min(hi - lo, 4096), x0 = m + 10, bw = w - 2 * m - 20, y0 = h * 0.58, bh = 34;
      const X = (a) => x0 + (a - lo) / span * bw;
      const used = new Set(r.sector_list);
      for (let s = lo / 32; s < (lo + span) / 32; s++) {
        api.rect(X(s * 32), y0, Math.max(1, bw * 32 / span - 1), bh, used.has(s) ? api.css("--blue") : "rgba(110,119,129,0.15)");
      }
      for (let a = lo; a <= lo + span; a += 128) api.line(X(a), y0 - 6, X(a), y0 + bh + 6, api.css("--ink"), 1.5);
      api.label(api.T(`显存地址 ${lo}～${lo + span} 字节（竖线：128 字节缓存行；方格：32 字节扇区，蓝色＝要搬运）`,
                      `addresses ${lo}–${lo + span} bytes (bars: 128-byte lines; boxes: 32-byte sectors, blue = moved)`), x0, y0 + bh + 26, api.css("--muted"), 12);
      const ty = m + 40, tw = bw / 32;
      for (let i = 0; i < 32; i++) {
        const tx = x0 + (i + 0.5) * tw;
        api.circle(tx, ty, Math.min(7, tw * 0.35), api.css("--amber"));
        if (addrs[i] < lo + span) api.line(tx, ty + 8, X(addrs[i] + size / 2), y0 - 2, "rgba(201,143,0,0.55)", 1);
      }
      api.label(api.T("线程束的 32 个线程", "the 32 threads of a warp"), x0, m + 18, api.css("--muted"), 12);
      if (hi - lo > span) api.label(api.T("（只画前 4096 字节）", "(first 4096 bytes shown)"), x0 + bw, m + 18, api.css("--muted"), 12, "right");
      return;
    }
    const { words, r } = this.bank(api);
    const x0 = m + 40, bw = (w - x0 - m) / 32, rowH = Math.min(26, (h - 2 * m - 60) / Math.max(r.ways, 1));
    const passes = Array.from({ length: 32 }, () => []);
    const seen = Array.from({ length: 32 }, () => new Map());
    words.forEach((wd, lane) => {
      const b = wd % 32, map = seen[b];
      if (!map.has(wd)) { map.set(wd, map.size); passes[b].push([wd, [lane]]); } else passes[b][map.get(wd)][1].push(lane);
    });
    for (let b = 0; b < 32; b++) {
      api.label(String(b), x0 + (b + 0.5) * bw, m + 14, api.css("--muted"), 10, "center");
      passes[b].forEach(([wd, lanes], k) => {
        const y = m + 22 + k * rowH;
        api.rect(x0 + b * bw + 1, y, bw - 2, rowH - 2, k === 0 ? api.css("--blue") : api.css("--red"));
        if (bw > 16) api.label(String(lanes[0]) + (lanes.length > 1 ? "+" : ""), x0 + (b + 0.5) * bw, y + rowH * 0.65, "#fff", 9, "center");
      });
    }
    api.label(api.T("存储体", "bank"), m, m + 14, api.css("--muted"), 11);
    api.label(api.T("第 1 次", "pass 1"), m, m + 22 + rowH * 0.65, api.css("--muted"), 11);
    api.label(api.T(`每格是一个线程要的字（格中数字是线程号，“+”表示几个线程读同一个字，广播）；往下每多一行，就要多读一次：共 ${r.ways} 次`,
                    `Each box is a word a thread needs (thread number shown; "+" = several threads share it, broadcast); each extra row is one more pass: ${r.ways} in all`),
              x0, h - m, api.css("--muted"), 12);
  },
});
