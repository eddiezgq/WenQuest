// 实验 9.1 大模型显存与训练时间计算器（配 9.1、9.2、9.7 节）。公式与程序 9.1.1、9.2.1、9.7.1 相同：
//   参数 N ≈ 12·L·d² + 2·V·d（前馈网络 d_ff = 4d，词表 V = 32 000，输入嵌入与输出层不共享）；训练运算量 ≈ 6·N·D；
//   训练时间 = 6ND ÷（GPU 数 × 峰值 × 算力利用率 40%）；序列长度取 4096；模型状态每个参数 16 字节（BF16 参数与梯度、FP32 主权重、两份 AdamW 状态），
//   ZeRO-0/1/2/3 分别切分 无 / 优化器状态 / 再加梯度 / 再加参数；激活值每层 s·b·d·34 字节（用 FlashAttention，b = 1）；
//   推理：权重 N × 位数 / 8；键值缓存每个词元 2·L·d 个数（不分组），半精度。
WQ.lab({
  title: ["实验 9.1 大模型显存与训练时间计算器", "Lab 9.1 Memory and training-time calculator for large models"],
  goal: ["改变模型的层数与宽度、训练的词元数、GPU 的型号与数量、ZeRO 的级别，算出训练要多少天、每块 GPU 要多少显存；部署时权重与键值缓存要多少显存。",
         "Change the depth and width, the training tokens, the GPU type and count and the ZeRO stage; compute training days and memory per GPU; and the memory for weights and the KV cache at inference."],
  scenes: [
    { id: "train", name: ["训练", "Training"],
      problem: { title: ["问题：训练一个 70 亿参数的模型要多久、多少显存", "Problem: how long and how much memory to train a 7B model"],
                 text: ["默认是 32 层、d = 4096（约 67 亿参数），在 2 万亿个词元上训练。按 40% 的算力利用率，用多少块什么 GPU 要训练几天？每块 GPU 放得下吗？",
                        "The default is 32 layers, d = 4096 (about 6.7B parameters), trained on 2 trillion tokens. At 40% utilization, how many days on which GPUs? Does each GPU have room?"] } },
    { id: "infer", name: ["推理", "Inference"],
      problem: { title: ["问题：部署时显存给了谁", "Problem: where does inference memory go"],
                 text: ["权重按 16、8、4 位存放，再加上同时服务的序列（每条 4096 个词元）的键值缓存。一块 GPU 能同时服务多少条长序列？",
                        "Weights at 16, 8 or 4 bits, plus the KV cache of the sequences being served (4096 tokens each). How many long sequences can one GPU serve?"] } },
  ],
  params: [
    { id: "L", name: ["层数 L", "Layers L"], min: 4, max: 128, step: 4, value: 32, digits: 0 },
    { id: "d", name: ["隐藏维度 d", "Hidden size d"], min: 512, max: 16384, step: 256, value: 4096, digits: 0 },
    { id: "D", name: ["训练词元数（十亿）", "Training tokens (billions)"], min: 10, max: 20000, step: 10, value: 2000, digits: 0 },
    { id: "gpu", name: ["GPU（0 A10 · 1 A100 80GB · 2 H100）", "GPU (0 A10 · 1 A100 80GB · 2 H100)"], min: 0, max: 2, step: 1, value: 1, digits: 0 },
    { id: "lgP", name: ["GPU 数 = 2^…", "GPUs = 2^…"], min: 0, max: 14, step: 1, value: 10, digits: 0 },
    { id: "zero", name: ["ZeRO 级别（0—3）", "ZeRO stage (0–3)"], min: 0, max: 3, step: 1, value: 0, digits: 0 },
    { id: "bits", name: ["推理权重位数（16 · 8 · 4）", "Inference weight bits (16 · 8 · 4)"], min: 4, max: 16, step: 4, value: 16, digits: 0 },
    { id: "batch", name: ["同时服务的序列数", "Concurrent sequences"], min: 1, max: 256, step: 1, value: 16, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["参数与梯度", "params & grads"] }, { color: "var(--amber)", name: ["优化器状态", "optimizer"] },
           { color: "var(--red)", name: ["激活值 / 键值缓存", "activations / KV cache"] }],
  tasks: [
    { id: "llama", text: ["默认设置（7B，2 万亿词元，1024 块 A100，利用率 40%）：要训练几天？与 Llama 2 报告的 184 320 GPU 小时对照。",
                          "Defaults (7B, 2T tokens, 1024 A100s, 40% MFU): how many days? Compare with Llama 2's reported 184,320 GPU hours."],
      demo: { scene: "train", set: { L: 32, d: 4096, D: 2000, gpu: 1, lgP: 10, zero: 0 }, press: [] } },
    { id: "zero3", text: ["同一个模型：ZeRO-0 时每块 A100 的模型状态要多少？换成 ZeRO-3、64 块 GPU 呢？", "Same model: model states per A100 with ZeRO-0? With ZeRO-3 on 64 GPUs?"],
      demo: { scene: "train", set: { zero: 3, lgP: 6 }, press: [] } },
    { id: "big", text: ["80 层、d = 8192（约 700 亿参数）按 16 位部署：一块 A100 80GB 放得下权重吗？4 位呢？", "80 layers, d = 8192 (about 70B) at 16 bits: do the weights fit on one A100 80GB? At 4 bits?"],
      demo: { scene: "infer", set: { L: 80, d: 8192, gpu: 1, bits: 4, batch: 1 }, press: [] } },
    { id: "kv", text: ["7B、16 位，16 条长 4096 的序列：键值缓存要多少？比权重还大吗？", "7B at 16 bits, 16 sequences of 4096: how big is the KV cache? Bigger than the weights?"],
      demo: { scene: "infer", set: { L: 32, d: 4096, bits: 16, batch: 16 }, press: [] } },
  ],
  think: ["训练时间与 GPU 数成反比，为什么实际中 GPU 加倍，时间往往不能减半？", "Training time is inversely proportional to the GPU count; why does doubling GPUs rarely halve the time in practice?"],

  G: [["A10", 125e12, 24e9], ["A100 80GB", 312e12, 80e9], ["H100", 989.4e12, 80e9]],
  model(api) { const p = api.p, V = 32000; return { N: 12 * p.L * p.d * p.d + 2 * V * p.d, L: p.L, d: p.d }; },
  gb(x) { return x >= 1e12 ? (x / 1e12).toFixed(2) + " TB" : (x / 1e9).toFixed(1) + " GB"; },
  train(api) {
    const p = api.p, { N, L, d } = this.model(api), [name, peak, mem] = this.G[p.gpu], P = 2 ** p.lgP, D = p.D * 1e9;
    const days = 6 * N * D / (P * peak * 0.4) / 86400;
    const z = p.zero, pg = (z >= 3 ? 4 / P : z === 2 ? 2 + 2 / P : 4) * N, opt = (z >= 1 ? 12 / P : 12) * N;
    const act = L * 4096 * d * 34;
    return { N, days, P, name, mem, pg, opt, act, gpuh: days * 24 * P };
  },
  infer(api) {
    const p = api.p, { N, L, d } = this.model(api), [name, , mem] = this.G[p.gpu];
    const w = N * p.bits / 8 + (p.bits === 4 ? N / 128 * 2 : 0), kv = 2 * L * d * 2 * 4096 * p.batch;
    return { N, w, kv, mem, name, perSeq: 2 * L * d * 2 * 4096 };
  },
  reset(api, s) {},
  readouts(api, s) {
    if (api.scene === "infer") {
      const r = this.infer(api), free = r.mem - r.w;
      if (api.p.L === 80 && api.p.d === 8192 && api.p.bits === 4) api.done("big");
      if (api.p.L === 32 && api.p.d === 4096 && api.p.bits === 16 && api.p.batch === 16) api.done("kv");
      return [[["参数", "Parameters"], (r.N / 1e9).toFixed(2) + api.T(" 十亿", " B")], [["权重", "Weights"], this.gb(r.w)],
              [["键值缓存", "KV cache"], this.gb(r.kv)], [["合计 / 一块 GPU 的显存", "Total / GPU memory"], this.gb(r.w + r.kv) + " / " + this.gb(r.mem)],
              [["放得下几条这样长的序列", "Sequences that fit"], free > 0 ? String(Math.floor(free / r.perSeq)) : api.T("权重都放不下", "weights do not fit")]];
    }
    const r = this.train(api), per = r.pg + r.opt + r.act;
    if (api.p.L === 32 && api.p.d === 4096 && api.p.D === 2000 && api.p.lgP === 10 && api.p.gpu === 1) api.done("llama");
    if (api.p.zero === 3 && r.P === 64) api.done("zero3");
    return [[["参数", "Parameters"], (r.N / 1e9).toFixed(2) + api.T(" 十亿", " B")], [["训练运算量 6ND", "Training FLOP 6ND"], (6 * r.N * api.p.D * 1e9).toExponential(2)],
            [["训练时间", "Training time"], api.fmt(r.days, 1) + api.T(" 天", " days")], [["GPU 小时", "GPU hours"], Math.round(r.gpuh).toLocaleString()],
            [["每块 GPU：模型状态 + 激活值", "Per GPU: states + activations"], this.gb(r.pg + r.opt) + " + " + this.gb(r.act)],
            [["一块 " + r.name + " 的显存", "Memory of one " + r.name], this.gb(r.mem) + (per > r.mem ? api.T("（放不下）", " (does not fit)") : "")]];
  },
  draw(api, s) {
    const { w, h } = api, m = 20;
    const items = api.scene === "infer" ? (() => { const r = this.infer(api); return { mem: r.mem, bars: [[api.T("权重", "weights"), r.w, "--blue"], [api.T("键值缓存", "KV cache"), r.kv, "--red"]] }; })()
      : (() => { const r = this.train(api); return { mem: r.mem, bars: [[api.T("参数与梯度", "params & grads"), r.pg, "--blue"], [api.T("优化器状态", "optimizer"), r.opt, "--amber"], [api.T("激活值", "activations"), r.act, "--red"]] }; })();
    const total = items.bars.reduce((a, b) => a + b[1], 0), top = Math.max(total, items.mem) * 1.1;
    const x0 = m + 60, y0 = h - 50, H = h - 90, bw = 140, X = (w - bw) / 2;
    let y = y0;
    for (const [lab, v, col] of items.bars) {
      const hh = v / top * H;
      api.rect(X, y - hh, bw, hh, api.css(col));
      if (hh > 14) api.label(lab + " " + this.gb(v), X + bw + 10, y - hh / 2 + 4, api.css("--ink"), 12);
      y -= hh;
    }
    const ym = y0 - items.mem / top * H;
    api.line(x0, ym, w - m, ym, api.css("--ink"), 2, [6, 4]);
    api.label(api.T("一块 GPU 的显存 ", "memory of one GPU ") + this.gb(items.mem), x0, ym - 6, api.css("--ink"), 12);
    api.label(api.T("每块 GPU", "per GPU"), X + bw / 2, y0 + 18, api.css("--muted"), 12, "center");
  },
});
