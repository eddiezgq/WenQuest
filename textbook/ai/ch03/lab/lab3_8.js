// 实验 3.8 屋顶线（配 3.8 节）。规格与 conventions/gpus.py 相同（张量核心取稠密的 FP16 峰值）；
// 各层的运算量与数据量与程序 3.8.1、程序 2.10.1 相同：半精度，每个运算单独执行，不考虑融合与缓存复用；h = d/64，d_ff = 4d。
// 场景“训练前向”：一批 B 条、每条 T 个词元同时计算；场景“逐词生成”：B 条序列各生成 1 个新词元，注意力读入长 T 的键值缓存。
WQ.lab({
  title: ["实验 3.8 屋顶线", "Lab 3.8 The roofline"],
  goal: ["把 Transformer 的各层画到不同 GPU 的屋顶线上，判断每层受算力还是受显存带宽限制，看批大小怎样移动它们的位置。",
         "Place the layers of a Transformer on the roofline of different GPUs, decide whether each is compute- or bandwidth-bound, and see how the batch size moves them."],
  scenes: [
    { id: "fwd", name: ["训练前向", "Training forward"],
      problem: { title: ["问题：哪些层在等显存", "Problem: which layers wait for memory"],
                 text: ["默认是第 2 章的小型 Transformer（d = 384，T = 256，B = 32）在 H100 上。哪些层落在屋顶线的斜坡上？换一块平衡点低的 GPU 又怎样？",
                        "The default is Chapter 2's tiny Transformer (d = 384, T = 256, B = 32) on an H100. Which layers sit on the slope? What changes on a GPU with a lower ridge point?"] } },
    { id: "dec", name: ["逐词生成", "Decoding"],
      problem: { title: ["问题：大模型逐词生成为什么慢", "Problem: why is decoding slow"],
                 text: ["70 亿参数一级的模型（d = 4096）逐词生成，每条序列每次只算一个新词元。把批大小加大，看线性层能不能爬上屋脊。",
                        "A 7-billion-class model (d = 4096) decodes one new token per sequence. Raise the batch and see whether the linear layers reach the ridge."] },
      params: { d: { value: 4096 }, B: { value: 1 }, T: { value: 1024 } } },
  ],
  params: [
    { id: "gpu", name: ["GPU（0 V100 · 1 A100 · 2 RTX 4090 · 3 H100 · 4 B200）", "GPU (0 V100 · 1 A100 · 2 RTX 4090 · 3 H100 · 4 B200)"], min: 0, max: 4, step: 1, value: 3, digits: 0 },
    { id: "d", name: ["模型宽度 d", "Width d"], min: 128, max: 8192, step: 128, value: 384, digits: 0 },
    { id: "T", name: ["序列长度 T", "Sequence length T"], min: 64, max: 8192, step: 64, value: 256, digits: 0 },
    { id: "B", name: ["批大小 B", "Batch size B"], min: 1, max: 512, step: 1, value: 32, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--blue)", name: ["矩阵乘法", "matrix products"] }, { color: "var(--amber)", name: ["逐元素运算", "element-wise"] },
           { color: "var(--ink)", name: ["屋顶线", "roofline"] }],
  tasks: [
    { id: "tiny", text: ["训练前向，H100，默认设置：读出平衡点，数一数有几层受带宽限制。", "Training forward, H100, defaults: read the ridge point and count the bandwidth-bound layers."],
      demo: { scene: "fwd", set: { gpu: 3, d: 384, T: 256, B: 32 }, press: [] } },
    { id: "a100", text: ["换成 A100（平衡点更低），线性层的瓶颈变了吗？", "Switch to an A100 (lower ridge). Do the linear layers change bottleneck?"],
      demo: { scene: "fwd", set: { gpu: 1, d: 384, T: 256, B: 32 }, press: [] } },
    { id: "dec", text: ["逐词生成，H100，B = 1：线性层的计算强度和可达到的算力是多少？", "Decoding, H100, B = 1: what are the intensity and attainable performance of the linear layers?"],
      demo: { scene: "dec", set: { gpu: 3, d: 4096, T: 1024, B: 1 }, press: [] } },
    { id: "batch", text: ["逐词生成：加大批大小，直到线性层受算力限制。与算例 3.8.3 比较。", "Decoding: raise the batch until the linear layers are compute-bound. Compare with Example 3.8.3."],
      demo: { scene: "dec", set: { gpu: 3, d: 4096, T: 1024, B: 360 }, press: [] } },
    { id: "rtx", text: ["逐词生成换成 RTX 4090：需要的批大小是多少？为什么比 H100 小？", "Decoding on an RTX 4090: what batch is needed now, and why less than on an H100?"],
      demo: { scene: "dec", set: { gpu: 2, d: 4096, T: 1024, B: 180 }, press: [] } },
  ],
  think: ["逐词生成时注意力层的计算强度随批大小几乎不变（每条序列有自己的键值缓存）。加大批大小能救线性层，却救不了注意力层。这对长上下文的推理意味着什么？",
          "In decoding, the attention layer's intensity hardly changes with the batch (each sequence has its own key-value cache). A larger batch rescues the linear layers but not attention. What does this mean for long-context inference?"],

  GPUS: [["V100", 125e12, 0.9e12], ["A100", 312e12, 2.039e12], ["RTX 4090", 165.2e12, 1.008e12], ["H100", 989.4e12, 3.35e12], ["B200", 2250e12, 7.7e12]],
  layers(api) {
    const d = api.p.d, T = api.p.T, B = api.p.B, h = Math.max(1, Math.round(d / 64)), f = 4 * d, by = 2;
    const mm = (M, K, N) => [2 * M * K * N, by * (M * K + K * N + M * N)];
    const L = [];
    if (api.scene === "fwd") {
      const n = B * T;
      L.push(["QKV", "mm", ...mm(n, d, 3 * d)], [api.T("输出投影", "out proj"), "mm", ...mm(n, d, d)], ["FF1", "mm", ...mm(n, d, f)], ["FF2", "mm", ...mm(n, f, d)]);
      L.push(["QKᵀ", "mm", 2 * B * h * T * T * (d / h), by * (2 * n * d + B * h * T * T)]);
      L.push(["softmax", "el", 5 * B * h * T * T, by * 2 * B * h * T * T], [api.T("层归一化", "LayerNorm"), "el", 8 * n * d, by * (2 * n * d + 2 * d)],
             ["GELU", "el", 10 * n * f, by * 2 * n * f], [api.T("残差加法", "residual"), "el", n * d, by * 3 * n * d]);
    } else {
      const n = B;                                              // 每条序列一个新词元
      L.push(["QKV", "mm", ...mm(n, d, 3 * d)], [api.T("输出投影", "out proj"), "mm", ...mm(n, d, d)], ["FF1", "mm", ...mm(n, d, f)], ["FF2", "mm", ...mm(n, f, d)]);
      L.push([api.T("注意力（读键值缓存）", "attention (KV cache)"), "mm", 4 * B * T * d, by * (2 * B * T * d + 2 * n * d + 2 * B * h * T)]);
      L.push([api.T("层归一化", "LayerNorm"), "el", 8 * n * d, by * (2 * n * d + 2 * d)], ["GELU", "el", 10 * n * f, by * 2 * n * f]);
    }
    return L.map(([name, kind, W, Q]) => ({ name, kind, W, Q, I: W / Q }));
  },
  readouts(api) {
    const g = this.GPUS[api.p.gpu], P = g[1], bw = g[2], ridge = P / bw, L = this.layers(api);
    const lin = L.slice(0, 4), linI = lin.reduce((a, l) => a + l.W, 0) / lin.reduce((a, l) => a + l.Q, 0);
    const nMem = L.filter((l) => l.I < ridge).length, att = Math.min(P, bw * linI);
    const p = api.p;
    if (api.scene === "fwd" && p.gpu === 3 && p.d === 384 && p.T === 256 && p.B === 32) api.done("tiny");
    if (api.scene === "fwd" && p.gpu === 1 && p.d === 384) api.done("a100");
    if (api.scene === "dec" && p.gpu === 3 && p.B === 1 && p.d === 4096) api.done("dec");
    if (api.scene === "dec" && p.gpu === 3 && p.d === 4096 && linI >= ridge) api.done("batch");
    if (api.scene === "dec" && p.gpu === 2 && p.d === 4096 && linI >= ridge) api.done("rtx");
    return [[["GPU", "GPU"], g[0]],
            [["平衡点 P/β", "Ridge point P/β"], api.fmt(ridge, 0) + " FLOP/B"],
            [["线性层计算强度", "Linear-layer intensity"], api.fmt(linI, 1) + " FLOP/B"],
            [["线性层可达到的算力", "Linear-layer attainable"], api.fmt(att / 1e12, 1) + " TFLOP/s（" + api.fmt(100 * att / P, 1) + "%）"],
            [["受带宽限制的层", "Bandwidth-bound layers"], nMem + " / " + L.length]];
  },
  draw(api) {
    const { w, h } = api, m = 16, g = this.GPUS[api.p.gpu], P = g[1], bw = g[2], L = this.layers(api);
    const x0 = m + 46, y0 = m + 8, pw = w - x0 - m - 190, ph = h - y0 - m - 30;
    const lx0 = -1, lx1 = 3.5, ly0 = 10, ly1 = 15.6;                 // log10 范围：I 0.1–3000 FLOP/B；P 10 G–4 P FLOP/s
    const X = (I) => x0 + (Math.log10(I) - lx0) / (lx1 - lx0) * pw, Y = (p) => y0 + ph - (Math.log10(p) - ly0) / (ly1 - ly0) * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"));
    for (let e = lx0; e <= lx1; e++) { api.line(X(10 ** e), y0, X(10 ** e), y0 + ph, api.css("--grid"), 1); api.label("10^" + e, X(10 ** e), y0 + ph + 14, api.css("--muted"), 10, "center"); }
    for (let e = 11; e <= 15; e++) { api.line(x0, Y(10 ** e), x0 + pw, Y(10 ** e), api.css("--grid"), 1); api.label(api.fmt(10 ** e / 1e12, e < 12 ? 1 : 0) + " T", x0 - 4, Y(10 ** e) + 4, api.css("--muted"), 10, "right"); }
    const ridge = P / bw, Ia = 10 ** lx0, Ib = 10 ** lx1;
    api.line(X(Ia), Y(bw * Ia), X(ridge), Y(P), api.css("--ink"), 2.5);
    api.line(X(ridge), Y(P), X(Ib), Y(P), api.css("--ink"), 2.5);
    api.line(X(ridge), Y(P), X(ridge), y0 + ph, api.css("--muted"), 1, [4, 4]);
    api.label(g[0] + api.T("  平衡点 ", "  ridge ") + api.fmt(ridge, 0), X(ridge) + 6, Y(P) - 8, api.css("--ink"), 12);
    const lx = x0 + pw + 12;
    api.label(api.T("层（计算强度）", "layer (intensity)"), lx, y0 + 12, api.css("--muted"), 11);
    L.forEach((l, i) => {
      const I = Math.min(Math.max(l.I, Ia), Ib), p = Math.min(P, bw * l.I), col = l.kind === "mm" ? api.css("--blue") : api.css("--amber");
      api.circle(X(I), Y(p), 5, col);
      api.label(String(i + 1), X(I) + 6 + (i % 3) * 9, Y(p) + 14 + (i % 2) * 10, col, 11);
      api.label((i + 1) + " " + l.name + "  " + api.fmt(l.I, l.I < 10 ? 2 : 0), lx, y0 + 32 + i * 18, col, 11);
    });
    api.label(api.T("计算强度 I（FLOP/B）", "intensity I (FLOP/B)"), x0 + pw, y0 + ph + 28, api.css("--muted"), 12, "right");
    api.label(api.T("可达到的算力（FLOP/s）", "attainable (FLOP/s)"), x0 + 4, y0 + 12, api.css("--muted"), 12);
  },
});
