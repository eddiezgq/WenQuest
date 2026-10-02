// 实验 2.10 Transformer 运算量计算器（配 2.9.6、2.10 节）。
// 计数与 code/ex2_10.py 相同：矩阵乘法 2MNK；逐元素运算按每个元素 层归一化 8、softmax 5、GELU 10、加法 1 FLOP；
// 数据量为每个运算单独执行时读入与写出的字节（半精度，不考虑融合）。d_ff = 4d，h = d/64；参数量按每层 12d² + 13d、加嵌入层计。
// H100：989.4 TFLOP/s（FP16 张量核心，稠密），3.35 TB/s。
WQ.lab({
  title: ["实验 2.10 Transformer 运算量计算器", "Lab 2.10 Transformer operation counter"],
  goal: ["改变模型宽度、层数、序列长度和批大小，统计一次前向计算中各类运算的浮点运算量和数据搬运量，判断它们在 H100 上受什么限制。",
         "Vary width, depth, sequence length and batch size; count the FLOPs and bytes of each kind of operation in one forward pass and decide what limits each on an H100."],
  scenes: [
    { id: "tiny", name: ["小型 Transformer", "Tiny Transformer"],
      problem: { title: ["问题：时间花在了哪里", "Problem: where does the time go"],
                 text: ["默认是本书的小型 Transformer（d = 384，6 层，T = 256，B = 32）。矩阵乘法占了几乎全部运算，耗时却只占一半左右。为什么？",
                        "The default is the book's tiny Transformer (d = 384, 6 layers, T = 256, B = 32). Matrix products are almost all the arithmetic yet only about half of the time. Why?"] } },
    { id: "big", name: ["大模型", "Large model"],
      problem: { title: ["把模型放大", "Scale the model up"],
                 text: ["把宽度加到 4096、层数 32（约 70 亿参数），看矩阵乘法的计算强度和耗时占比怎样变化。", "Raise the width to 4096 and depth to 32 (about 7 B parameters) and watch the intensity and time share of the matrix products change."] } },
    { id: "life", name: ["厨房备菜", "Kitchen prep"],
      problem: { title: ["生活中的例子：切菜与跑腿", "Everyday example: chopping and fetching"],
                 text: ["厨师切一样菜很快，但每样菜都要去冷库取一趟。菜的分量（相当于计算量）越大，跑腿（相当于搬数据）占的时间比例越小。",
                        "Chopping is quick but each ingredient needs a trip to the cold store. The larger each batch (the arithmetic), the smaller the share of time spent fetching (moving data)."] } },
  ],
  params: [
    { id: "d", name: ["模型宽度 d", "Width d"], min: 128, max: 8192, step: 128, value: 384, digits: 0 },
    { id: "L", name: ["层数 L", "Layers L"], min: 1, max: 96, step: 1, value: 6, digits: 0 },
    { id: "T", name: ["序列长度 T", "Sequence length T"], min: 64, max: 8192, step: 64, value: 256, digits: 0 },
    { id: "B", name: ["批大小 B", "Batch size B"], min: 1, max: 256, step: 1, value: 32, digits: 0 },
    { id: "V", name: ["词表大小 V", "Vocabulary V"], min: 2048, max: 131072, step: 2048, value: 2048, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--blue)", name: ["浮点运算量", "FLOPs"] }, { color: "var(--red)", name: ["数据搬运量", "bytes"] },
           { color: "var(--amber)", name: ["耗时下限", "time bound"] }],
  tasks: [
    { id: "tiny", text: ["保持默认的小型 Transformer，读出一次前向的总运算量和矩阵乘法所占的百分比。", "Keep the tiny Transformer and read the total FLOPs and the matrix-product share."],
      demo: { scene: "tiny", set: { d: 384, L: 6, T: 256, B: 32, V: 2048 }, press: [] } },
    { id: "attn", text: ["只增大序列长度 T，找到注意力矩阵乘的运算量超过线性层的 T（与 6d 比较；输出层也算在线性层里，所以略大于 6d）。", "Increase only T and find where the attention matmuls exceed the linear layers in FLOPs (compare with 6d; the output layer counts as linear, so slightly above 6d)."],
      demo: { scene: "tiny", set: { d: 384, L: 6, T: 2560, B: 32, V: 2048 }, press: [] } },
    { id: "big", text: ["大模型场景：d = 4096、L = 32，读出参数量，并确认线性层受算力限制。", "Large model: d = 4096, L = 32; read the parameter count and confirm the linear layers are compute-bound."],
      demo: { scene: "big", set: { d: 4096, L: 32, T: 2048, B: 8, V: 32768 }, press: [] } },
    { id: "b1", text: ["大模型场景把批大小和序列长度都调到最小（B = 1，T = 64），线性层还受算力限制吗？", "In the large-model scene set B = 1 and T = 64. Are the linear layers still compute-bound?"],
      demo: { scene: "big", set: { d: 4096, L: 32, T: 64, B: 1, V: 32768 }, press: [] } },
  ],
  think: ["逐元素运算的计算强度与模型大小几乎无关，而矩阵乘法的计算强度随 d 和 BT 增大。这对“融合”逐元素运算的价值意味着什么？",
          "The intensity of element-wise ops hardly depends on model size, while that of matrix products grows with d and BT. What does this imply for fusing element-wise ops?"],

  P: 989.4e12, BW: 3.35e12,
  calc(api) {
    const d = api.p.d, L = api.p.L, T = api.p.T, B = api.p.B, V = api.p.V, f = 4 * d, h = Math.max(1, Math.round(d / 64)), n = B * T, by = 2;
    const mm = (M, K, N) => [2 * M * K * N, by * (M * K + K * N + M * N)];
    const ops = [];
    for (let l = 0; l < L; l++) {
      ops.push(["norm", 8 * n * d, by * (2 * n * d + 2 * d)], ["linear", ...mm(n, d, 3 * d)]);
      const s = 2 * B * h * T * T * (d / h);
      ops.push(["attn", s, by * (2 * n * d + B * h * T * T)], ["softmax", 5 * B * h * T * T, by * 2 * B * h * T * T]);
      ops.push(["attn", s, by * (B * h * T * T + 2 * n * d)], ["linear", ...mm(n, d, d)], ["add", n * d, by * 3 * n * d]);
      ops.push(["norm", 8 * n * d, by * (2 * n * d + 2 * d)], ["linear", ...mm(n, d, f)], ["gelu", 10 * n * f, by * 2 * n * f]);
      ops.push(["linear", ...mm(n, f, d)], ["add", n * d, by * 3 * n * d]);
    }
    ops.push(["norm", 8 * n * d, by * (2 * n * d + 2 * d)], ["linear", ...mm(n, d, V)]);
    const cats = ["linear", "attn", "softmax", "norm", "gelu", "add"], R = {};
    cats.forEach((c) => (R[c] = { W: 0, Q: 0, t: 0 }));
    for (const [c, W, Q] of ops) { R[c].W += W; R[c].Q += Q; R[c].t += Math.max(W / this.P, Q / this.BW); }
    const tot = { W: 0, Q: 0, t: 0 };
    cats.forEach((c) => { tot.W += R[c].W; tot.Q += R[c].Q; tot.t += R[c].t; });
    const params = L * (12 * d * d + 13 * d) + V * d + T * d + 2 * d;
    return { R, tot, cats, params };
  },
  big(x, u) { const k = [[1e15, "P"], [1e12, "T"], [1e9, "G"], [1e6, "M"], [1e3, "k"]].find((q) => x >= q[0]); return k ? (x / k[0]).toFixed(2) + " " + k[1] + u : x.toFixed(0) + " " + u; },
  readouts(api) {
    const r = this.calc(api), lin = r.R.linear, at = r.R.attn;
    const mmShare = (lin.W + at.W) / r.tot.W, linI = lin.W / lin.Q, linCompute = lin.W / this.P >= lin.Q / this.BW;
    if (api.scene === "tiny" && api.p.d === 384 && api.p.L === 6 && api.p.T === 256 && api.p.B === 32 && api.p.V === 2048) api.done("tiny");
    if (api.p.d === 384 && at.W > lin.W) api.done("attn");
    if (api.scene === "big" && api.p.d === 4096 && api.p.L === 32 && linCompute) api.done("big");
    if (api.scene === "big" && api.p.d === 4096 && api.p.B === 1 && api.p.T === 64) api.done("b1");
    return [[["参数量", "Parameters"], this.big(r.params, "")],
            [["一次前向的运算量", "FLOPs per forward"], this.big(r.tot.W, "FLOP")],
            [["矩阵乘法所占运算", "Matrix-product share of FLOPs"], (100 * mmShare).toFixed(2) + "%"],
            [["数据搬运量", "Bytes moved"], this.big(r.tot.Q, "B")],
            [["线性层计算强度 / H100 P/β", "Linear intensity / H100 P/β"], api.fmt(linI, 3) + " / 295 FLOP/B"],
            [["线性层的瓶颈", "Linear-layer bottleneck"], linCompute ? api.T("算力", "compute") : api.T("显存带宽", "bandwidth")],
            [["耗时下限（H100，不融合）", "Time bound (H100, unfused)"], (r.tot.t * 1e3).toFixed(3) + " ms"]];
  },
  draw(api) {
    const { w, h } = api, m = 16, r = this.calc(api);
    const names = { linear: ["线性层", "linear"], attn: ["注意力矩阵乘", "attn matmul"], softmax: ["softmax", "softmax"],
                    norm: ["层归一化", "LayerNorm"], gelu: ["GELU", "GELU"], add: ["残差加法", "residual"] };
    const x0 = m + 90, bw = w - x0 - m - 40, rowH = (h - 2 * m - 20) / r.cats.length;
    r.cats.forEach((c, i) => {
      const y = m + 20 + i * rowH, R = r.R[c];
      api.label(api.T(...names[c]), x0 - 8, y + rowH * 0.42, api.css("--ink"), 12, "right");
      [[R.W / r.tot.W, "--blue"], [R.Q / r.tot.Q, "--red"], [R.t / r.tot.t, "--amber"]].forEach(([v, col], k) => {
        const yy = y + k * rowH * 0.27 + 2, hh = rowH * 0.24;
        api.rect(x0, yy, Math.max(1, bw * v), hh, api.css(col));
        api.label((100 * v).toFixed(1) + "%", x0 + Math.max(1, bw * v) + 4, yy + hh * 0.75, api.css("--muted"), 10);
      });
    });
    api.label(api.T("各类运算占全部的比例", "share of each kind of operation"), x0, m + 8, api.css("--muted"), 12);
  },
});
