// 实验 3.6 线程束分化与调度（配 3.6、3.7 节）。用平台实验工具包的 GPU 执行模拟器 api.gpu（第 14 轮细则 2.5 节，部分 ①②），
// 它与书中程序用的 code/_gpusim.py 逐行对应，同一组参数给出相同的结果。
// 场景“分化”：统计 256 个线程束（图中画前 4 个），分支前后各 2 条指令，then、else 两条路径的长度可调。
// 场景“延迟隐藏”：一个调度器，每个线程束重复“读一次显存，再做 k 条算术”，贪心后取最老的调度；利用率取后一半周期（稳态）。
// 带宽限制按 H100：每个调度器平均每 40 个周期才能分到一次 128 字节的读取（3.35 TB/s ÷ 132 个 SM ÷ 4 ÷ 1.98 GHz ≈ 3.2 B/周期）。
WQ.lab({
  title: ["实验 3.6 线程束分化与调度", "Lab 3.6 Warp divergence and scheduling"],
  goal: ["在 GPU 执行模拟器上看两件事：线程束分化浪费了多少算力；要多少个线程束、每次读显存后要做多少算术，才能把显存延迟藏住。",
         "On the GPU execution model, see how much work warp divergence wastes, and how many warps and how much arithmetic per load it takes to hide memory latency."],
  scenes: [
    { id: "div", name: ["分化", "Divergence"],
      problem: { title: ["问题：一个 if 让 GPU 慢了多少", "Problem: how much does one if cost"],
                 text: ["检测工位的程序对每个像素判断“是不是缺陷”，是缺陷的再做一段处理。同一个线程束里有的线程走 then、有的走 else，两条路径要依次执行。选不同的分支条件，看发射的指令数和 SIMT 效率。",
                        "The inspection code tests every pixel for a defect and processes the defective ones. When threads of one warp take different paths, both paths run in turn. Try different branch conditions and read the instructions issued and the SIMT efficiency."] } },
    { id: "lat", name: ["延迟隐藏", "Latency hiding"],
      problem: { title: ["问题：线程束够不够多", "Problem: are there enough warps"],
                 text: ["读显存要等约 700 个周期。一个调度器手里的线程束都在等数据时，它就只能空闲。改变线程束数和每次读后的算术指令数，看发射利用率。",
                        "A load waits about 700 cycles. When all of a scheduler's warps are waiting, it idles. Change the number of warps and the arithmetic per load and read the issue utilization."] },
      params: { L: { value: 700 } } },
  ],
  params: [
    { id: "cond", name: ["分化：条件（0 无分支 · 1 前后半 · 2 奇偶 · 3 按线程束 · 4 按数据）", "Divergence: condition (0 none · 1 halves · 2 odd/even · 3 per warp · 4 data)"], min: 0, max: 4, step: 1, value: 2, digits: 0 },
    { id: "p", name: ["分化：按数据时走 then 的概率", "Divergence: probability of then (data)"], min: 0, max: 1, step: 0.01, value: 0.5, digits: 2 },
    { id: "a", name: ["分化：then 路径的指令数", "Divergence: instructions on then"], min: 1, max: 16, step: 1, value: 4, digits: 0 },
    { id: "b", name: ["分化：else 路径的指令数", "Divergence: instructions on else"], min: 1, max: 16, step: 1, value: 4, digits: 0 },
    { id: "n", name: ["延迟：线程束数 n", "Latency: warps n"], min: 1, max: 32, step: 1, value: 4, digits: 0 },
    { id: "k", name: ["延迟：每次读后的算术指令 k", "Latency: arithmetic per load k"], min: 1, max: 80, step: 1, value: 4, digits: 0 },
    { id: "L", name: ["延迟：显存延迟 L（周期）", "Latency: memory latency L (cycles)"], min: 20, max: 1000, step: 10, value: 700, digits: 0 },
    { id: "bw", name: ["延迟：带宽限制（0 不计 · 1 按 H100）", "Latency: bandwidth limit (0 off · 1 H100)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--blue)", name: ["then / 发射", "then / issue"] }, { color: "var(--amber)", name: ["else / 等显存", "else / waiting for memory"] },
           { color: "var(--muted)", name: ["分支前后 / 准备好没轮到", "before-after / ready, not picked"] }],
  tasks: [
    { id: "odd", text: ["分化：按奇偶分支（条件 2），读出发射的指令数和 SIMT 效率，与无分支（条件 0）比较。", "Divergence: branch on odd/even (condition 2); read the instructions issued and the SIMT efficiency and compare with no branch (condition 0)."],
      demo: { scene: "div", set: { cond: 2, a: 4, b: 4 }, press: [] } },
    { id: "warp", text: ["分化：改成按线程束编号分支（条件 3），效率变成多少？为什么？", "Divergence: branch on the warp number (condition 3). What is the efficiency now, and why?"],
      demo: { scene: "div", set: { cond: 3, a: 4, b: 4 }, press: [] } },
    { id: "data", text: ["分化：按数据分支（条件 4），把概率调到 0.99，效率是多少？调到 0.5 呢？", "Divergence: branch on data (condition 4) with probability 0.99. What is the efficiency? And at 0.5?"],
      demo: { scene: "div", set: { cond: 4, p: 0.99 }, press: [] } },
    { id: "few", text: ["延迟隐藏：16 个线程束、k = 4，读出发射利用率，与式 (3.7.1) 的估计比较。", "Latency: 16 warps and k = 4; read the utilization and compare with Eq. (3.7.1)."],
      demo: { scene: "lat", set: { n: 16, k: 4, L: 700, bw: 0 }, press: [] } },
    { id: "hide", text: ["延迟隐藏：保持 16 个线程束，找出使利用率达到 99% 以上的最小 k。", "Latency: keep 16 warps and find the smallest k that gives more than 99% utilization."],
      demo: { scene: "lat", set: { n: 16, k: 46, L: 700, bw: 0 }, press: [] } },
    { id: "bw", text: ["延迟隐藏：打开带宽限制，k = 4 时把线程束加到 32，利用率还能升高吗？", "Latency: turn on the bandwidth limit; with k = 4 raise the warps to 32. Does the utilization still rise?"],
      demo: { scene: "lat", set: { n: 32, k: 4, L: 700, bw: 1 }, press: [] } },
  ],
  think: ["式 (3.7.1) 与带宽限制合起来说明：要用满算力，每读 128 字节至少要做约 40 条算术指令。这与 3.8 节屋顶线的平衡点 P/β 有什么关系？",
          "Eq. (3.7.1) with the bandwidth limit says that about 40 arithmetic instructions are needed per 128-byte load to keep the ALUs busy. How does this relate to the ridge point P/β of the roofline in Section 3.8?"],

  GAP: 40, CONDS: ["none", "half", "odd", "warp", "data"],
  run(api) {
    const p = api.p;
    if (api.scene === "div") {
      const key = ["div", p.cond, p.p, p.a, p.b].join(",");
      if (this.key !== key) {
        this.key = key;
        // 统计 256 个线程束（按数据分支时样本足够多），画前 4 个
        this.res = api.gpu.diverge({ cond: this.CONDS[p.cond], warps: 256, pre: 2, then: p.a, other: p.b, post: 2, p: p.p, seed: 7 });
      }
    } else {
      const gap = p.bw ? this.GAP : 0, key = ["lat", p.n, p.k, p.L, gap].join(",");
      if (this.key !== key) {
        this.key = key;
        const span = Math.min(3000, 2 * (p.L + p.k + 1) + 40);
        this.res = api.gpu.schedule({ warps: p.n, schedulers: 1, latency: p.L, k: p.k, gap, cycles: Math.max(8000, 6 * (p.L + p.k)), trace: span });
        this.res.span = span;
        this.res.est = api.gpu.little(p.n, p.k, p.L, gap);
      }
    }
    return this.res;
  },
  reset() { this.key = null; },
  readouts(api) {
    const r = this.run(api), p = api.p;
    if (api.scene === "div") {
      const perWarp = r.warps.slice(0, 4).map((w) => w.issued), uniform = r.warps.filter((w) => /^(0+|1+)$/.test(w.mask)).length;
      if (p.cond === 2 && p.a === 4 && p.b === 4) api.done("odd");
      if (p.cond === 3) api.done("warp");
      if (p.cond === 4 && p.p >= 0.985) api.done("data");
      return [[["前 4 个线程束发射的指令", "Issued by the first 4 warps"], perWarp.join(" / ")],
              [["没有分化的线程束", "Warps without divergence"], uniform + " / 256"],
              [["SIMT 效率", "SIMT efficiency"], (100 * r.eff).toFixed(1) + "%"],
              [["空转的线程·指令", "Idle lane-instructions"], String(32 * r.issued - r.active) + " / " + String(32 * r.issued)]];
    }
    if (p.n === 16 && p.k === 4 && !p.bw && p.L === 700) api.done("few");
    if (p.n === 16 && !p.bw && r.util >= 0.99) api.done("hide");
    if (p.bw && p.k === 4 && p.n >= 32) api.done("bw");
    return [[["发射利用率（模拟，稳态）", "Issue utilization (simulated, steady)"], (100 * r.util).toFixed(1) + "%"],
            [["式 (3.7.1) 的估计", "Estimate of Eq. (3.7.1)"], (100 * r.est).toFixed(1) + "%"],
            [["藏住延迟需要的线程束 (L + k)/(k + 1)", "Warps to hide latency (L + k)/(k + 1)"], api.fmt((p.L + p.k) / (p.k + 1), 1)],
            [["计算强度（每读 128 B 做 32k 次乘加）", "Intensity (32k FMAs per 128 B)"], api.fmt(p.k / 2, 1) + " FLOP/B"]];
  },
  draw(api) {
    const r = this.run(api), { w, h } = api, m = 14;
    if (api.scene === "div") {
      const cols = { pre: api.css("--muted"), post: api.css("--muted"), then: api.css("--blue"), else: api.css("--amber") };
      const shown = r.steps.slice(0, 4), total = shown.reduce((a, s) => a + s.length, 0) + 3;
      const cw = Math.min(26, (w - 2 * m - 40) / total), chh = Math.min(7, (h - 2 * m - 40) / 32);
      let x = m + 40;
      shown.forEach((seq, wi) => {
        const mask = r.warps[wi].mask;
        api.label(api.T("线程束 ", "warp ") + wi, x, m + 12, api.css("--ink"), 12);
        seq.forEach((kind, i) => {
          for (let lane = 0; lane < 32; lane++) {
            const on = kind === "pre" || kind === "post" || (kind === "then" && mask[lane] === "1") || (kind === "else" && mask[lane] === "0");
            api.rect(x + i * cw, m + 24 + lane * chh, cw - 1, chh - 1, on ? cols[kind] : null, on ? null : api.css("--grid"));
          }
        });
        x += (seq.length + 1) * cw;
      });
      api.label(api.T("线程 0", "lane 0"), m + 34, m + 30, api.css("--muted"), 10, "right");
      api.label("31", m + 34, m + 24 + 31.5 * chh, api.css("--muted"), 10, "right");
      api.label(api.T("横向：依次发射的指令；白格：空转的线程", "across: instructions in issue order; empty cells: idle lanes"), m + 40, m + 24 + 32 * chh + 18, api.css("--muted"), 12);
      return;
    }
    const cols = { I: api.css("--blue"), M: "rgba(201,143,0,0.45)", R: "rgba(110,119,129,0.30)", B: "rgba(207,34,46,0.35)" };
    const rows = r.trace, n = rows.length, span = r.span, x0 = m + 52, gw = w - x0 - m, gh = Math.min(16, (h * 0.62 - m) / n);
    rows.forEach((row, wi) => {
      let c = 0;
      while (c < span) { let e = c; while (e < span && row[e] === row[c]) e++;
        api.rect(x0 + c / span * gw, m + 18 + wi * gh, Math.max(0.6, (e - c) / span * gw), gh - 1, cols[row[c]]); c = e; }
      if (n <= 16 || wi % 4 === 0) api.label(String(wi), x0 - 6, m + 18 + wi * gh + gh * 0.75, api.css("--muted"), 10, "right");
    });
    api.label(api.T(`前 ${span} 个周期（红：等带宽）`, `first ${span} cycles (red: waiting for bandwidth)`), x0, m + 10, api.css("--muted"), 12);
    const py = m + 30 + n * gh, ph = h - py - m - 22;
    if (ph > 60) {
      const est = [];
      for (let q = 1; q <= 32; q++) est.push([q, 100 * api.gpu.little(q, api.p.k, api.p.L, api.p.bw ? this.GAP : 0)]);
      const ax = api.plot(x0, py, gw, ph, [{ pts: est, color: api.css("--accent") }],
               { xmin: 0, xmax: 32, ymin: 0, ymax: 100, xlabel: api.T("线程束数 n（线：式 (3.7.1)；点：模拟）", "warps n (line: Eq. (3.7.1); dot: simulated)"), ylabel: "%" });
      api.circle(ax.X(api.p.n), ax.Y(100 * r.util), 5, api.css("--blue"));
    }
  },
});
