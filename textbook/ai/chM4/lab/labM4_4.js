// 实验 M4.4 同一个式子，换个精度、换个数量级，算出来的就不一样（配 M4.4、M4.5、M4.6 节）。
// 两个场景：
//   round ：看一个数在 FP64 / FP32 / FP16 里分别被存成什么、误差多大，以及"大数吃小数"从哪个数量级开始；
//   sum   ：同一批数求和，顺序 / 成对 / 补偿三种写法的误差随项数怎样涨，精度一降差别有多大。
// 全部在浏览器里现算：JS 的数是双精度，用 Math.fround 得到单精度，半精度按位手工舍入。
WQ.lab({
  title: ["实验 M4.4 精度、数量级与求和的写法", "Lab M4.4 Precision, magnitude and how you sum"],
  goal: ["亲手看一个数在三种精度里变成什么、误差多大；再看“把一百万个数加起来”这件最普通的事，三种写法能差出两个数量级。做完就知道为什么混合精度训练要把求和留在高精度里（第 8 章），也知道为什么同一份代码在不同设备上结果会有微小差别。",
         "See what a number becomes in three precisions, then watch three ways of summing a million numbers differ by two orders of magnitude — which is why mixed-precision training keeps reductions in higher precision."],
  scenes: [
    { id: "round", name: ["一个数被存成什么", "What a number becomes"],
      problem: { title: ["问题：0.1 存进去还是 0.1 吗", "Problem: is 0.1 still 0.1"],
                 text: ["十进制的 0.1 在二进制下是无限循环小数，任何有限位的浮点格式都存不下它。位数越少，差得越远；而且相邻两个可表示数之间的间隔随数值大小跳变——数越大，间隔越大。",
                        "0.1 is a repeating fraction in binary, so no finite float stores it exactly. Fewer bits, larger error — and the gap between neighbouring representable numbers grows with the magnitude."] } },
    { id: "sum", name: ["一百万个数怎么加", "How to add a million numbers"],
      problem: { title: ["问题：加法的次序会改变结果", "Problem: the order of addition changes the result"],
                 text: ["浮点加法不满足结合律。一个一个顺着加，前面的和越来越大，后面的小数被“吃掉”，误差随项数线性涨；成对相加（分治）让每次相加的两个数大小相当，误差慢得多；补偿求和把每次丢掉的低位记下来补回去，几乎不涨。",
                        "Floating-point addition is not associative. Adding one by one lets a growing partial sum swallow small terms; pairwise summation keeps addends comparable; compensated summation carries the lost low bits forward."] } },
  ],
  params: [
    { id: "value", name: ["要存的数（10 的几次方）", "value (power of ten)"], min: -6, max: 8, step: 0.5, value: -1, digits: 1 },
    { id: "small", name: ["再加上的小数（10 的几次方）", "small addend (power of ten)"], min: -8, max: 2, step: 0.5, value: 0, digits: 1 },
    { id: "n", name: ["求和的项数（10 的几次方）", "terms to sum (power of ten)"], min: 2, max: 6, step: 0.5, value: 5, digits: 1 },
    { id: "prec", name: ["求和用的精度：0 = 单精度，1 = 双精度", "precision: 0 = single, 1 = double"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
  ],
  legend: [{ color: "var(--red)", name: ["顺序求和", "sequential"] }, { color: "var(--blue)", name: ["成对求和", "pairwise"] },
           { color: "var(--green)", name: ["补偿求和", "compensated"] }],
  tasks: [
    { id: "zero1", text: ["把要存的数调到 $10^{-1}$（0.1）：三种精度各存成什么？FP16 的相对误差是多少？",
                          "Set the value to 0.1: what does each precision store, and what is FP16's relative error?"],
      demo: { scene: "round", set: { value: -1 }, press: [] } },
    { id: "swallow", text: ["把再加上的小数固定为 $10^{0}$（1），要存的数从 $10^{6}$ 一路加到 $10^{8}$：这个 1 从哪个数量级开始被单精度吃掉？与“单精度能精确表示的最大整数是 $2^{24}$”对得上吗？",
                            "Keep the addend at 1 and raise the value from 1e6 to 1e8: from which magnitude does single precision swallow it? Does that match 2^24?"],
      demo: { scene: "round", set: { value: 8, small: 0 }, press: [] } },
    { id: "sum5", text: ["切到求和场景，项数 $10^{5}$、单精度：三种写法的误差各是多少？顺序比成对差几倍？",
                         "Switch to summation with 1e5 terms in single precision: what are the three errors, and how many times worse is sequential?"],
      demo: { scene: "sum", set: { n: 5, prec: 0 }, press: [] } },
    { id: "sum6", text: ["项数加到 $10^{6}$：顺序求和的误差涨了几倍？与“最坏按 $n$、随机按 $\\sqrt{n}$”哪个更接近？",
                         "Raise the terms to 1e6: how much does the sequential error grow — closer to n or to sqrt(n)?"],
      demo: { scene: "sum", set: { n: 6, prec: 0 }, press: [] } },
  ],
  think: ["为什么混合精度训练里，矩阵乘法可以用 FP16，但累加必须用 FP32？（提示：看本实验的第二个场景。）",
          "Why can mixed precision multiply in FP16 but must accumulate in FP32?"],

  // ---------- 半精度：按 IEEE 754 binary16 就近偶数舍入
  toFP16(x) {
    if (!isFinite(x) || x === 0) return x;
    const s = Math.sign(x);
    x = Math.abs(x);
    if (x >= 65520) return s * Infinity;
    const MINSUB = Math.pow(2, -24);
    if (x < MINSUB / 2) return 0;
    let e = Math.floor(Math.log2(x));
    if (e < -14) e = -14;                       // 次正规数
    const step = Math.pow(2, e - 10);
    const q = Math.round(x / step) * step;      // 就近舍入
    return s * q;
  },
  relErr(approx, exact) { return exact === 0 ? 0 : Math.abs(approx - exact) / Math.abs(exact); },
  rand(seed) { let t = seed + 0x6d2b79f5; return () => { t += 0x6d2b79f5; let x = Math.imul(t ^ (t >>> 15), 1 | t); x ^= x + Math.imul(x ^ (x >>> 7), 61 | x); return ((x ^ (x >>> 14)) >>> 0) / 4294967296; }; },
  sums(n, single) {
    const rnd = this.rand(7), f = single ? Math.fround : (z) => z;
    const xs = new Float64Array(n);
    for (let i = 0; i < n; i++) xs[i] = f(0.5 + rnd());
    let exact = 0;                               // 双精度逐个加（当作真值；项数不大时足够准）
    for (let i = 0; i < n; i++) exact += xs[i];
    let seq = 0;
    for (let i = 0; i < n; i++) seq = f(seq + xs[i]);
    const pairwise = (lo, hi) => {               // 成对（分治）求和
      if (hi - lo <= 8) { let s = 0; for (let i = lo; i < hi; i++) s = f(s + xs[i]); return s; }
      const mid = (lo + hi) >> 1;
      return f(pairwise(lo, mid) + pairwise(mid, hi));
    };
    const pair = pairwise(0, n);
    let s = 0, c = 0;
    for (let i = 0; i < n; i++) { const y = f(xs[i] - c); const t = f(s + y); c = f(f(t - s) - y); s = t; }
    return { exact, seq, pair, kahan: s };
  },
  calc(api) {
    const p = api.p, key = [p.value, p.small, p.n, p.prec].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const x = Math.pow(10, p.value), small = Math.pow(10, p.small);
    const x32 = Math.fround(x), x16 = this.toFP16(x);
    const sum64 = x + small, sum32 = Math.fround(Math.fround(x) + Math.fround(small));
    const n = Math.round(Math.pow(10, p.n));
    const s = this.sums(n, p.prec === 0);
    const val = { x, x32, x16, e32: this.relErr(x32, x), e16: this.relErr(x16, x),
                  small, sum64, sum32, swallowed: Math.fround(sum32) === Math.fround(x),
                  n, errSeq: this.relErr(s.seq, s.exact), errPair: this.relErr(s.pair, s.exact),
                  errKahan: this.relErr(s.kahan, s.exact),
                  eps: p.prec === 0 ? Math.pow(2, -23) : Math.pow(2, -52) };
    val.ratio = val.errSeq / Math.max(val.errPair, 1e-18);
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const p = api.p, c = this.calc(api);
    if (api.scene === "round" && Math.abs(p.value + 1) < 1e-9) api.done("zero1");
    if (api.scene === "round" && c.swallowed) api.done("swallow");
    if (api.scene === "sum" && p.n >= 5) api.done("sum5");
    if (api.scene === "sum" && p.n >= 6) api.done("sum6");
    if (api.scene === "round") {
      return [[["要存的数", "the value"], c.x.toPrecision(12)],
              [["单精度存成", "as FP32"], c.x32.toPrecision(12)],
              [["半精度存成", "as FP16"], isFinite(c.x16) ? c.x16.toPrecision(12) : api.T("溢出（∞）", "overflow")],
              [["单精度的相对误差", "FP32 relative error"], (c.e32 * 100).toExponential(2) + "%"],
              [["半精度的相对误差", "FP16 relative error"], isFinite(c.x16) ? (c.e16 * 100).toExponential(2) + "%" : "—"],
              [["加上小数后（单精度）", "value + addend (FP32)"],
               c.swallowed ? api.T("没变——小数被吃掉了", "unchanged — the addend was swallowed")
                           : c.sum32.toPrecision(12)]];
    }
    return [[["项数", "terms"], String(c.n)],
            [["精度", "precision"], p.prec === 0 ? api.T("单精度", "single") : api.T("双精度", "double")],
            [["顺序求和的相对误差", "sequential"], c.errSeq.toExponential(2)],
            [["成对求和", "pairwise"], c.errPair.toExponential(2)],
            [["补偿求和", "compensated"], c.errKahan.toExponential(2)],
            [["顺序比成对差几倍", "sequential / pairwise"], c.ratio.toFixed(1) + "×"]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api), p = api.p;
    const x0 = 80, y0 = 30, pw = w - x0 - 30, ph = h - y0 - 48;
    if (api.scene === "round") {
      // 数轴：画出该数量级附近的可表示数的间隔
      const rows = [[api.T("FP64（双精度）", "FP64"), Math.pow(2, -52), api.css("--green")],
                    [api.T("FP32（单精度）", "FP32"), Math.pow(2, -23), api.css("--blue")],
                    [api.T("FP16（半精度）", "FP16"), Math.pow(2, -10), api.css("--red")]];
      rows.forEach(([name, eps, col], i) => {
        const y = y0 + ph * (0.2 + 0.3 * i);
        api.line(x0, y, x0 + pw, y, api.css("--grid"), 1);
        const gap = Math.pow(2, Math.floor(Math.log2(Math.abs(c.x)))) * eps;   // 这个数量级上的间隔
        const show = Math.min(40, Math.max(2, Math.round(pw / 18)));
        for (let k = -show; k <= show; k++) {
          const px = x0 + pw / 2 + k * (pw / (2 * show));
          api.line(px, y - 7, px, y + 7, col, k === 0 ? 2.5 : 1);
        }
        api.label(name, 8, y + 4, col, 12);
        api.label(api.T(`间隔 ${gap.toExponential(1)}`, `gap ${gap.toExponential(1)}`), x0 + pw - 150, y - 12, col, 11);
      });
      api.label(api.T(`要存的数 ${c.x.toExponential(2)}：位数越少，刻度越稀，存进去的误差越大`,
                      `value ${c.x.toExponential(2)}: fewer bits, coarser ticks, larger error`),
                x0, h - 14, api.css("--muted"), 12);
      return;
    }
    // 误差随项数：对数坐标
    const pts = [];
    for (let e = 2; e <= 6; e += 0.5) {
      const r = this.sums(Math.round(Math.pow(10, e)), p.prec === 0);
      pts.push([e, this.relErr(r.seq, r.exact), this.relErr(r.pair, r.exact), this.relErr(r.kahan, r.exact)]);
    }
    const lo = -11, hi = -3;
    const X = (e) => x0 + (e - 2) / 4 * pw;
    const Y = (v) => y0 + ph - (Math.max(Math.log10(Math.max(v, 1e-12)), lo) - lo) / (hi - lo) * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    for (let e = -11; e <= -3; e += 2) { api.line(x0, Y(Math.pow(10, e)), x0 + pw, Y(Math.pow(10, e)), api.css("--grid"), 1);
      api.label("1e" + e, 20, Y(Math.pow(10, e)) + 4, api.css("--muted"), 11); }
    [[1, api.css("--red")], [2, api.css("--blue")], [3, api.css("--green")]].forEach(([k, col]) => {
      let prev = null;
      for (const row of pts) {
        const cur = [X(row[0]), Y(row[k])];
        if (prev) api.line(prev[0], prev[1], cur[0], cur[1], col, 2);
        api.circle(cur[0], cur[1], 3, null, col);
        prev = cur;
      }
    });
    api.line(X(p.n), y0, X(p.n), y0 + ph, api.css("--ink"), 1.5, [5, 4]);
    api.label(api.T("项数（10 的几次方）", "terms (power of ten)"), x0, h - 14, api.css("--muted"), 12);
    api.label(api.T("相对误差", "relative error"), 8, y0 + 12, api.css("--muted"), 12);
  },
});
