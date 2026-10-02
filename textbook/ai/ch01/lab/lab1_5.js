// 实验 1.5 运算量与耗时计算器（配 1.5.2–1.5.5 节）。
// 耗时下限 T ≥ max(W/P, Q/β)（式 (1.5.3)），计算强度 I = W/Q（式 (1.5.4)）。
// 硬件参数与 code/_ch1.py 相同：CPU 为教学用的假设值（64 核、3.0 GHz、每核每周期 64 FLOP、8 通道 DDR5-4800）；
// GTX 580 按 512 核 × 1544 MHz × 2 FLOP，显存 192.4 GB/s；A100、H100 取张量核心 FP16 稠密峰值与 HBM 带宽。
// AlexNet 的数据量做了简化：权重读一遍，每张图读入输入、各层输出写一次读一次（FP32 或 FP16），见实验指导书。
WQ.lab({
  title: ["实验 1.5 运算量与耗时计算器", "Lab 1.5 Operations-and-time calculator"],
  goal: ["选择模型、批大小和硬件，算出运算量、数据量和计算强度，判断一项计算受算力限制还是受显存带宽限制。",
         "Choose a model, a batch size and the hardware; compute the operations, the data moved and the intensity, and decide whether the computation is compute-bound or memory-bound."],
  scenes: [
    { id: "cnn", name: ["AlexNet 推理", "AlexNet inference"], hide: ["n", "N", "bits", "teachers", "rate"],
      problem: { title: ["工程问题：一批图片要多久", "Engineering problem: how long does a batch of images take"],
                 text: ["AlexNet 一张图约 7.24 亿次乘加、6100 万个参数。改变批大小和硬件，看每张图的平均耗时和瓶颈。",
                        "AlexNet: about 724 million multiply–adds and 61 million parameters per image. Vary the batch size and the hardware; watch the time per image and the bottleneck."] } },
    { id: "mm", name: ["矩阵乘法", "Matrix multiply"], hide: ["B", "N", "bits", "teachers", "rate"],
      problem: { title: ["两个 n×n 矩阵相乘", "Multiplying two n×n matrices"],
                 text: ["运算量 2n³，至少读两个矩阵、写一个矩阵。n 增大时计算强度怎样变化？",
                        "2n³ operations; at least two matrices read and one written. How does the intensity change with n?"] } },
    { id: "llm", name: ["大模型逐词生成", "LLM token generation"], hide: ["n", "teachers", "rate"],
      problem: { title: ["工程问题：聊天助手每秒能出几个字", "Engineering problem: how many tokens per second"],
                 text: ["生成一个词元，每个参数做一次乘加、从显存读一遍。B 条序列同时生成时，权重读一遍用 B 次。",
                        "Each token: one multiply–add per parameter, every parameter read once. With B sequences together, one read serves B tokens."] } },
    { id: "exam", name: ["阅卷", "Exam marking"], hide: ["B", "hw", "n", "N", "bits"],
      problem: { title: ["生活中的例子：阅卷老师越多越快吗？", "Everyday example: do more markers always help?"],
                 text: ["10 000 份试卷，每份批阅 30 秒；试卷由扫描室分发，每分钟能分发的份数有限。",
                        "10,000 scripts, 30 s each to mark; scripts are handed out by the scanning room at a limited rate per minute."] } },
  ],
  params: [
    { id: "B", name: ["批大小 B", "Batch size B"], min: 1, max: 1024, step: 1, value: 1, digits: 0 },
    { id: "hw", name: ["硬件（0 单核 · 1 CPU · 2 GTX 580 · 3 A100 · 4 H100）", "Hardware (0 core · 1 CPU · 2 GTX 580 · 3 A100 · 4 H100)"], min: 0, max: 4, step: 1, value: 0, digits: 0 },
    { id: "n", name: ["矩阵阶数 n", "Matrix size n"], min: 256, max: 16384, step: 256, value: 1024, digits: 0 },
    { id: "N", name: ["参数量 N（十亿）", "Parameters N (billions)"], min: 1, max: 70, step: 1, value: 7, digits: 0 },
    { id: "bits", name: ["权重位数（0 → 16 · 1 → 8 · 2 → 4）", "Weight bits (0 → 16 · 1 → 8 · 2 → 4)"], min: 0, max: 2, step: 1, value: 0, digits: 0 },
    { id: "teachers", name: ["阅卷老师人数", "Number of markers"], min: 1, max: 400, step: 1, value: 10, digits: 0 },
    { id: "rate", name: ["分发速度（份/分钟）", "Hand-out rate (scripts/min)"], min: 20, max: 400, step: 10, value: 100, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "batch", text: ["AlexNet 场景：在 H100 上把批大小增大到 64 以上，比较每张图的平均耗时与批大小为 1 时。", "AlexNet: on the H100 raise the batch above 64 and compare the time per image with batch 1."],
      demo: { scene: "cnn", set: { hw: 4, B: 128 }, press: [] } },
    { id: "mm", text: ["矩阵乘法场景：确认 n = 4096 时在 H100 上受算力限制。", "Matrix multiply: confirm that n = 4096 is compute-bound on the H100."],
      demo: { scene: "mm", set: { hw: 4, n: 4096 }, press: [] } },
    { id: "llm", text: ["逐词生成：70 亿参数、FP16、H100，增大批大小，直到转为受算力限制。", "Token generation: 7 B parameters, FP16, H100; raise B until it becomes compute-bound."],
      demo: { scene: "llm", set: { hw: 4, N: 7, bits: 0, B: 320 }, press: [] } },
    { id: "q4", text: ["逐词生成：把权重压到 4 位，批大小为 1 时每秒能生成多少个词元？", "Token generation: with 4-bit weights and B = 1, how many tokens per second?"],
      demo: { scene: "llm", set: { hw: 4, N: 7, bits: 2, B: 1 }, press: [] } },
    { id: "exam", text: ["阅卷：找到再加老师也不再变快的人数（瓶颈变为分发）。", "Marking: find the number of markers beyond which adding more no longer helps (the hand-out becomes the bottleneck)."],
      demo: { scene: "exam", set: { teachers: 60, rate: 100 }, press: [] } },
  ],
  think: ["AlexNet 的卷积层和全连接层，哪一类更早从受带宽限制转为受算力限制？为什么？",
          "Which turn compute-bound first as the batch grows, AlexNet's conv layers or its fully connected layers? Why?"],

  HW: [
    { name: ["CPU 单核", "one CPU core"], P: 192e9, bw: 307.2e9, bytes: 4 },
    { name: ["CPU（64 核）", "CPU (64 cores)"], P: 12.288e12, bw: 307.2e9, bytes: 4 },
    { name: ["GTX 580", "GTX 580"], P: 512 * 1544e6 * 2, bw: 192.4e9, bytes: 4 },
    { name: ["A100（FP16 张量核心）", "A100 (FP16 tensor cores)"], P: 312e12, bw: 2039e9, bytes: 2 },
    { name: ["H100（FP16 张量核心）", "H100 (FP16 tensor cores)"], P: 989.4e12, bw: 3.35e12, bytes: 2 },
  ],
  // AlexNet：每层乘加数与参数量（式 (1.5.1)），各层输出的元素数
  ALEX: { mac: 724406816, params: 60965224, input: 224 * 224 * 3,
          outs: [55 * 55 * 96, 27 * 27 * 256, 13 * 13 * 384, 13 * 13 * 384, 13 * 13 * 256, 4096, 4096, 1000] },

  calc(api) {
    if (api.scene === "exam") {
      const papers = 10000, tc = papers * 30 / api.p.teachers, tm = papers / api.p.rate * 60;
      return { exam: true, tc, tm, T: Math.max(tc, tm) };
    }
    const h = this.HW[api.p.hw];
    let W, Q, per = 1, unit = "";
    if (api.scene === "cnn") {
      const A = this.ALEX, B = api.p.B, acts = A.outs.reduce((s, x) => s + x, 0);
      W = 2 * A.mac * B; Q = h.bytes * (A.params + B * (A.input + 2 * acts)); per = B; unit = api.T("张图", "image");
    } else if (api.scene === "mm") {
      const n = api.p.n; W = 2 * n * n * n; Q = 3 * n * n * h.bytes; per = 1;
    } else {
      const N = api.p.N * 1e9, B = api.p.B, bits = [16, 8, 4][api.p.bits];
      W = 2 * N * B; Q = N * bits / 8; per = B; unit = api.T("词元", "token");
    }
    const tc = W / h.P, tm = Q / h.bw;
    return { h, W, Q, I: W / Q, bal: h.P / h.bw, tc, tm, T: Math.max(tc, tm), per, unit, compute: tc >= tm };
  },
  t(s) { return s >= 1 ? s.toFixed(2) + " s" : s >= 1e-3 ? (s * 1e3).toFixed(2) + " ms" : (s * 1e6).toFixed(2) + " μs"; },
  big(x, u) { const k = [[1e12, "T"], [1e9, "G"], [1e6, "M"], [1e3, "k"]].find((q) => x >= q[0]); return k ? (x / k[0]).toFixed(2) + " " + k[1] + u : x.toFixed(0) + " " + u; },
  readouts(api) {
    const r = this.calc(api);
    if (r.exam) {
      if (r.tm >= r.tc) api.done("exam");
      return [[["批阅时间", "Marking time"], (r.tc / 60).toFixed(1) + api.T(" 分钟", " min")],
              [["分发时间", "Hand-out time"], (r.tm / 60).toFixed(1) + api.T(" 分钟", " min")],
              [["总时间（下限）", "Total (lower bound)"], (r.T / 60).toFixed(1) + api.T(" 分钟", " min")],
              [["瓶颈", "Bottleneck"], r.tm >= r.tc ? api.T("分发（“带宽”）", "hand-out (“bandwidth”)") : api.T("批阅（“算力”）", "marking (“compute”)")]];
    }
    if (api.scene === "cnn" && api.p.hw === 4 && api.p.B >= 64) api.done("batch");
    if (api.scene === "mm" && api.p.hw === 4 && api.p.n >= 4096 && r.compute) api.done("mm");
    if (api.scene === "llm" && api.p.hw === 4 && api.p.N === 7 && api.p.bits === 0 && r.compute) api.done("llm");
    if (api.scene === "llm" && api.p.hw === 4 && api.p.bits === 2 && api.p.B === 1) api.done("q4");
    const rows = [[["硬件", "Hardware"], api.T(...r.h.name)],
                  [["运算量 W", "Operations W"], this.big(r.W, "FLOP")],
                  [["数据量 Q", "Data moved Q"], this.big(r.Q, "B")],
                  [["计算强度 I / 硬件 P/β", "Intensity I / hardware P/β"], api.fmt(r.I, 3) + " / " + api.fmt(r.bal, 3) + " FLOP/B"],
                  [["W/P 与 Q/β", "W/P and Q/β"], this.t(r.tc) + " / " + this.t(r.tm)],
                  [["瓶颈", "Bottleneck"], r.compute ? api.T("算力", "compute") : api.T("显存带宽", "memory bandwidth")]];
    if (api.scene === "cnn") rows.push([["每张图平均", "Per image"], this.t(r.T / r.per)]);
    if (api.scene === "llm") rows.push([["每条序列每秒词元数", "Tokens/s per sequence"], api.fmt(1 / r.T, 4)]);
    return rows;
  },
  draw(api) {
    const { w, h } = api, m = 14, r = this.calc(api), muted = api.css("--muted");
    if (r.exam) {
      const x0 = m + 20, x1 = w - m - 20, top = h * 0.25, bh = 34, mx = Math.max(r.tc, r.tm) * 1.15;
      api.label(api.T("批阅：" + api.p.teachers + " 位老师", "Marking: " + api.p.teachers + " markers"), x0, top - 10, muted, 13);
      api.rect(x0, top, (x1 - x0) * r.tc / mx, bh, api.css("--blue"));
      api.label(api.T("分发：每分钟 " + api.p.rate + " 份", "Hand-out: " + api.p.rate + " per min"), x0, top + bh + 30, muted, 13);
      api.rect(x0, top + bh + 40, (x1 - x0) * r.tm / mx, bh, api.css("--red"));
      api.label(api.T("两者中较长的决定总时间", "the longer one sets the total time"), x0, top + 2 * bh + 80, api.css("--ink"), 14);
      for (let i = 0; i < Math.min(api.p.teachers, 60); i++) api.circle(x0 + 8 + (i % 30) * 14, top + 2 * bh + 110 + Math.floor(i / 30) * 14, 5, api.css("--accent"));
      return;
    }
    // roofline on log axes: attainable performance min(P, I·β) against intensity I
    const px = m + 50, py = m + 10, pw = w * 0.62 - px, ph = h - 2 * m - 30;
    const lx = (I) => px + (Math.log10(I) + 1) / 5 * pw;                    // I from 0.1 to 10^4 FLOP/B
    const ly = (P) => py + ph - (Math.log10(P) - 9) / 7 * ph;              // P from 1 G to 10^16 FLOP/s
    api.rect(px, py, pw, ph, null, api.css("--grid"));
    for (let e = -1; e <= 4; e++) { api.line(lx(10 ** e), py + ph, lx(10 ** e), py + ph + 4, muted, 1); api.label("10^" + e, lx(10 ** e), py + ph + 14, muted, 10, "center"); }
    for (let e = 9; e <= 16; e += 1) { api.line(px - 4, ly(10 ** e), px, ly(10 ** e), muted, 1); if (e % 2 === 1) api.label({ 9: "1 G", 11: "100 G", 13: "10 T", 15: "1 P" }[e], px - 6, ly(10 ** e), muted, 10, "right"); }
    this.HW.forEach((hh, k) => {
      const col = k === api.p.hw ? api.css("--accent") : api.css("--grid"), lw = k === api.p.hw ? 3 : 1.2, Ib = hh.P / hh.bw;
      const I0 = 0.1, I1 = 1e4;
      api.line(lx(I0), ly(I0 * hh.bw), lx(Math.min(Ib, I1)), ly(Math.min(Ib, I1) * hh.bw), col, lw);
      if (Ib < I1) api.line(lx(Ib), ly(hh.P), lx(I1), ly(hh.P), col, lw);
    });
    const I = Math.min(Math.max(r.I, 0.1), 1e4), perf = Math.min(r.h.P, r.I * r.h.bw);
    api.circle(lx(I), ly(perf), 7, r.compute ? api.css("--blue") : api.css("--red"), api.css("--ink"));
    api.label(api.T("计算强度 I（FLOP/B）", "intensity I (FLOP/B)"), px + pw, py + ph + 28, muted, 12, "right");
    api.label(api.T("可达性能（FLOP/s）", "attainable performance (FLOP/s)"), px + 4, py + 12, muted, 12);
    // right: the two time bounds
    const bx = w * 0.68, bw = w - bx - m, mx = Math.max(r.tc, r.tm);
    api.label("W/P", bx, h * 0.3 - 8, api.css("--blue"), 13); api.rect(bx, h * 0.3, bw * r.tc / mx, 22, api.css("--blue"));
    api.label("Q/β", bx, h * 0.5 - 8, api.css("--red"), 13); api.rect(bx, h * 0.5, bw * r.tm / mx, 22, api.css("--red"));
    api.label(r.compute ? api.T("受算力限制", "compute-bound") : api.T("受显存带宽限制", "memory-bound"), bx, h * 0.7, api.css("--ink"), 15);
  },
});
