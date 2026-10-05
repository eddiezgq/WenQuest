// 实验 6.4 集合通信的代价（配 6.4 节）。α–β 模型与程序 6.4.2（ex6_4.py）相同：
//   朴素：2(p − 1)(α + n/β)；环形：2(p − 1)α + 2(p − 1)/p · n/β；树形：2·log₂p·α + 2n/β。
// 总线带宽 = 算法带宽 × 2(p − 1)/p（nccl-tests 的定义）。“环形”场景逐步演示 p 块 GPU 的环形全归约：
// 先归约—散播 p − 1 步，再全收集 p − 1 步；每格数字是这一块里已经加进了几块 GPU 的数据。
WQ.lab({
  title: ["实验 6.4 集合通信的代价", "Lab 6.4 The cost of collective communication"],
  goal: ["改变全归约的算法、GPU 数、消息大小和链路的延迟与带宽，读出耗时与总线带宽；逐步观看环形全归约中数据块的流转。",
         "Change the all-reduce algorithm, GPU count, message size and link latency and bandwidth; read the time and bus bandwidth; watch the chunks move in a ring all-reduce."],
  scenes: [
    { id: "cost", name: ["耗时与带宽", "Time and bandwidth"],
      problem: { title: ["问题：梯度要多久才能加起来", "Problem: how long to sum the gradients"],
                 text: ["数据并行训练每一步都要把各块 GPU 的梯度加起来。默认是 8 块 A100（NVSwitch，300 GB/s）、16 GiB 的梯度（与 70 亿参数一级模型的半精度梯度同一量级）。换一种算法、换成 PCIe，或者把 GPU 加到 64 块，会怎样？",
                        "Data-parallel training sums the gradients of all GPUs every step. The default is 8 A100s (NVSwitch, 300 GB/s) and 16 GiB of gradients (the order of a 7B model in FP16). What changes with another algorithm, with PCIe, or with 64 GPUs?"] } },
    { id: "ring", name: ["环形全归约", "Ring all-reduce"],
      problem: { title: ["问题：每块 GPU 只和邻居说话，怎么得到总和", "Problem: talking only to a neighbour, how does everyone get the sum"],
                 text: ["把 GPU 排成一个环，每步每块 GPU 只把一块数据发给右边的邻居。按“开始”，看 2(p − 1) 步之后每块 GPU 怎样都得到了全部的和。",
                        "Put the GPUs in a ring; each step every GPU sends one chunk to its right neighbour. Press Start and watch how after 2(p − 1) steps every GPU holds the full sum."] },
      params: { lgP: { value: 2 } } },
  ],
  params: [
    { id: "alg", name: ["算法（0 朴素 · 1 环形 · 2 树形）", "Algorithm (0 naive · 1 ring · 2 tree)"], min: 0, max: 2, step: 1, value: 1, digits: 0 },
    { id: "lgP", name: ["GPU 数 p = 2^…", "GPUs p = 2^…"], min: 1, max: 7, step: 1, value: 3, digits: 0 },
    { id: "lgN", name: ["消息大小 n = 2^… 字节", "Message n = 2^… bytes"], min: 10, max: 35, step: 1, value: 34, digits: 0 },
    { id: "alpha", name: ["延迟 α（μs）", "Latency α (μs)"], min: 0.5, max: 50, step: 0.5, value: 2, digits: 1 },
    { id: "beta", name: ["链路带宽 β（GB/s，每个方向）", "Link bandwidth β (GB/s, per direction)"], min: 10, max: 900, step: 5, value: 300, digits: 0 },
    { id: "speed", name: ["动画速度（步/秒）", "Animation speed (steps/s)"], min: 0.5, max: 5, step: 0.5, value: 1, digits: 1 },
  ],
  legend: [{ color: "var(--muted)", name: ["朴素", "naive"] }, { color: "var(--blue)", name: ["环形", "ring"] }, { color: "var(--red)", name: ["树形", "tree"] }],
  tasks: [
    { id: "big", text: ["默认设置（8 块，16 GiB，环形）：读出耗时与总线带宽；再换成朴素算法，慢多少倍？", "Defaults (8 GPUs, 16 GiB, ring): read the time and bus bandwidth; switch to naive — how many times slower?"],
      demo: { scene: "cost", set: { alg: 0, lgP: 3, lgN: 34, alpha: 2, beta: 300 }, press: [] } },
    { id: "small", text: ["把消息改成 8 KiB（2^13）：三种算法中哪个最快？为什么？", "Make the message 8 KiB (2^13): which algorithm is fastest and why?"],
      demo: { scene: "cost", set: { alg: 2, lgP: 3, lgN: 13 }, press: [] } },
    { id: "many", text: ["消息 1 MiB（2^20），把 GPU 加到 64 块：环形和树形的耗时各怎样变化？", "Message 1 MiB (2^20), 64 GPUs: how do ring and tree times change?"],
      demo: { scene: "cost", set: { alg: 1, lgP: 6, lgN: 20 }, press: [] } },
    { id: "pcie", text: ["把链路带宽改成 PCIe 4.0（30 GB/s），默认的 16 GiB 梯度要多久？", "Set the link to PCIe 4.0 (30 GB/s): how long for the default 16 GiB?"],
      demo: { scene: "cost", set: { alg: 1, lgP: 3, lgN: 34, beta: 30 }, press: [] } },
    { id: "watch", text: ["“环形全归约”场景，4 块 GPU：按“开始”看完 6 步。", "Ring scene, 4 GPUs: press Start and watch all 6 steps."],
      demo: { scene: "ring", set: { lgP: 2, speed: 1 }, press: ["start"] } },
  ],
  think: ["环形算法的带宽项几乎与 GPU 数无关，延迟项却随 GPU 数线性增长。训练用的 GPU 越来越多时，NCCL 为什么要同时提供树形算法？",
          "The ring's bandwidth term barely depends on the GPU count, but its latency term grows linearly. As training uses ever more GPUs, why does NCCL also offer a tree?"],

  time(alg, p, n, a, b) {
    if (alg === 0) return 2 * (p - 1) * (a + n / b);
    if (alg === 1) return 2 * (p - 1) * a + 2 * (p - 1) / p * n / b;
    return 2 * Math.log2(p) * a + 2 * n / b;
  },
  cfg(api) { const p = api.p; return { alg: p.alg, P: 2 ** p.lgP, n: 2 ** p.lgN, a: p.alpha * 1e-6, b: p.beta * 1e9 }; },
  reset(api, s) { s.step = 0; s.acc = 0; },
  update(dt, api, s) {
    if (api.scene !== "ring") { api.stop(); return; }
    const P = Math.min(8, 2 ** api.p.lgP);
    s.acc += dt * api.p.speed;
    while (s.acc >= 1 && s.step < 2 * (P - 1)) { s.acc -= 1; s.step += 1; }
    if (s.step >= 2 * (P - 1)) { if (P === 4) api.done("watch"); api.stop(); }
  },
  fmtT(api, t) { return t < 1e-3 ? api.fmt(t * 1e6, 1) + " μs" : t < 1 ? api.fmt(t * 1e3, 2) + " ms" : api.fmt(t, 2) + " s"; },
  fmtB(n) { const u = ["B", "KiB", "MiB", "GiB"]; let k = 0; while (n >= 1024 && k < 3) { n /= 1024; k++; } return n + " " + u[k]; },
  readouts(api, s) {
    const { alg, P, n, a, b } = this.cfg(api);
    if (api.scene === "ring") {
      const Pd = Math.min(8, P), st = s.step || 0;
      return [[["GPU 数（画出的）", "GPUs (drawn)"], String(Pd)],
              [["当前步 / 总步数", "Step / steps"], st + " / " + 2 * (Pd - 1)],
              [["阶段", "Phase"], st === 0 ? api.T("开始", "start") : st <= Pd - 1 ? api.T("归约—散播", "reduce-scatter") : api.T("全收集", "all-gather")],
              [["每块 GPU 已发出（数组长度的倍数）", "Sent per GPU (× array)"], api.fmt(st / Pd, 2) + " / " + api.fmt(2 * (Pd - 1) / Pd, 2)]];
    }
    const t = this.time(alg, P, n, a, b), algbw = n / t, busbw = algbw * 2 * (P - 1) / P;
    const lat = alg === 0 ? 2 * (P - 1) * a : alg === 1 ? 2 * (P - 1) * a : 2 * Math.log2(P) * a;
    const tn = this.time(0, P, n, a, b), tr = this.time(1, P, n, a, b);
    if (P === 8 && n === 2 ** 34 && alg === 0) api.done("big");
    if (P === 8 && n === 2 ** 13 && alg === 2) api.done("small");
    if (P === 64 && n === 2 ** 20) api.done("many");
    if (api.p.beta <= 35 && n === 2 ** 34 && alg === 1) api.done("pcie");
    return [[["消息", "Message"], this.fmtB(n)],
            [["耗时", "Time"], this.fmtT(api, t)],
            [["其中延迟项", "Latency part"], api.fmt(100 * lat / t, 1) + "%"],
            [["算法带宽", "Algorithm bandwidth"], api.fmt(algbw / 1e9, 1) + " GB/s"],
            [["总线带宽", "Bus bandwidth"], api.fmt(busbw / 1e9, 1) + " GB/s"],
            [["朴素 ÷ 环形", "Naive ÷ ring"], api.fmt(tn / tr, 2) + " ×"]];
  },
  draw(api, s) {
    const { w, h } = api, m = 16;
    if (api.scene === "ring") return this.drawRing(api, s);
    const { alg, P, n, a, b } = this.cfg(api);
    const x0 = m + 52, y0 = m + 10, pw = w - x0 - m - 10, ph = h - y0 - m - 34;
    const lx0 = 10, lx1 = 35, tmin = this.time(2, P, 2 ** 10, a, b) / 3, tmax = this.time(0, P, 2 ** 35, a, b) * 3;
    const ly0 = Math.log10(tmin), ly1 = Math.log10(tmax);
    const X = (lg) => x0 + (lg - lx0) / (lx1 - lx0) * pw, Y = (t) => y0 + ph - (Math.log10(t) - ly0) / (ly1 - ly0) * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"));
    for (let e = 10; e <= 35; e += 5) api.label(this.fmtB(2 ** e), X(e), y0 + ph + 14, api.css("--muted"), 10, "center");
    for (let e = Math.ceil(ly0); e <= ly1; e++) api.label(this.fmtT(api, 10 ** e), x0 - 4, Y(10 ** e) + 4, api.css("--muted"), 10, "right");
    const cols = [api.css("--muted"), api.css("--blue"), api.css("--red")];
    for (let k = 0; k < 3; k++) {
      let prev = null;
      for (let lg = 10; lg <= 35; lg += 0.25) {
        const pt = [X(lg), Y(this.time(k, P, 2 ** lg, a, b))];
        if (prev) api.line(prev[0], prev[1], pt[0], pt[1], cols[k], k === alg ? 3 : 1.5);
        prev = pt;
      }
    }
    const lg = Math.log2(n);
    api.line(X(lg), y0, X(lg), y0 + ph, api.css("--ink"), 1, [4, 4]);
    api.circle(X(lg), Y(this.time(alg, P, n, a, b)), 6, cols[alg]);
    api.label(api.T(`p = ${P}，α = ${api.p.alpha} μs，β = ${api.p.beta} GB/s`, `p = ${P}, α = ${api.p.alpha} μs, β = ${api.p.beta} GB/s`), x0 + 8, y0 + 16, api.css("--muted"), 12);
    api.label(api.T("消息大小", "message size"), x0 + pw, y0 + ph + 28, api.css("--muted"), 11, "right");
  },
  drawRing(api, s) {
    const { w, h } = api, P = Math.min(8, 2 ** api.p.lgP), step = s.step || 0;
    // 每块 GPU 的每一块里加进了哪些 GPU 的数据（集合用位掩码）
    let have = Array.from({ length: P }, (_, r) => Array.from({ length: P }, () => 1 << r));
    const sends = [];
    for (let t = 0; t < step; t++) {
      const nw = have.map((row) => row.slice());
      const msg = [];
      for (let r = 0; r < P; r++) {
        const c = t < P - 1 ? ((r - t) % P + P) % P : ((r + 1 - (t - (P - 1))) % P + P) % P;
        if (t < P - 1) nw[(r + 1) % P][c] |= have[r][c]; else nw[(r + 1) % P][c] = have[r][c];
        msg.push(c);
      }
      have = nw;
      if (t === step - 1) sends.push(...msg);
    }
    const cx = w / 2, cy = h / 2 + 6, R = Math.min(w, h) * 0.33, cw = Math.min(22, 150 / P);
    const hues = ["--red", "--blue", "--amber", "--green", "--violet", "--orange", "--accent", "--ink"];
    const pop = (x) => { let c = 0; while (x) { c += x & 1; x >>= 1; } return c; };
    for (let r = 0; r < P; r++) {
      const ang = -Math.PI / 2 + 2 * Math.PI * r / P, gx = cx + R * Math.cos(ang), gy = cy + R * Math.sin(ang);
      api.label("GPU " + r, gx, gy - cw * 0.9, api.css("--ink"), 12, "center");
      for (let c = 0; c < P; c++) {
        const x = gx - P * cw / 2 + c * cw, k = pop(have[r][c]);
        api.rect(x, gy - cw / 2, cw - 2, cw - 2, k === P ? api.css(hues[c % hues.length]) : `rgba(110,119,129,${0.12 + 0.6 * k / P})`);
        if (cw >= 16) api.label(String(k), x + cw / 2 - 1, gy + 4, k === P ? "#fff" : api.css("--ink"), 10, "center");
      }
      if (sends.length) {
        const ang2 = -Math.PI / 2 + 2 * Math.PI * ((r + 1) % P) / P;
        const ax = cx + R * 0.72 * Math.cos(ang), ay = cy + R * 0.72 * Math.sin(ang), bx = cx + R * 0.72 * Math.cos(ang2), by = cy + R * 0.72 * Math.sin(ang2);
        api.line(ax, ay, bx, by, api.css("--accent"), 2);
        api.circle(bx, by, 4, api.css("--accent"));
        api.label(api.T("块 ", "chunk ") + sends[r], (ax + bx) / 2, (ay + by) / 2 - 4, api.css("--accent"), 10, "center");
      }
    }
    api.label(api.T("格中数字：这一块里已加进几块 GPU 的数据；彩色 = 完整的和；箭头：这一步每块 GPU 发给右邻的块",
                    "Number: how many GPUs' data a chunk holds; coloured = full sum; arrows: the chunk each GPU sent right this step"),
              16, h - 12, api.css("--muted"), 11);
  },
});
