// 实验 8.1 浮点格式的精度与范围（配 8.1 节）。各格式的参数与舍入规则与程序 8.1.1（ex8_1.py、_ch8.py）相同：
//   规格化数 (−1)^s · 1.f · 2^(E − bias)，bias = 2^(e−1) − 1；指数全 0 为零与次正规数；就近舍入、平分取偶；
//   IEEE 格式（FP32、TF32、BF16、FP16、E5M2）指数全 1 留给无穷与 NaN，溢出为无穷；E4M3 只把全 1 留给 NaN（最大 448），E2M1 没有无穷与 NaN，二者溢出时饱和。
WQ.lab({
  title: ["实验 8.1 浮点格式的精度与范围", "Lab 8.1 Precision and range of floating-point formats"],
  goal: ["把一个数存进 FP32、TF32、BF16、FP16、FP8（E5M2、E4M3）、FP4（E2M1）中，看它的位怎样分配、存进去变成多少、误差多大；比较各格式的范围与精度；观察“大数吃小数”。",
         "Store a number in FP32, TF32, BF16, FP16, FP8 (E5M2, E4M3) and FP4 (E2M1): see how the bits are split, what is stored and how large the error is; compare ranges and precision; watch large numbers swallow small ones."],
  scenes: [
    { id: "bits", name: ["一个数的位", "The bits of a number"],
      problem: { title: ["问题：0.1 存进去还是 0.1 吗", "Problem: is 0.1 still 0.1 once stored"],
                 text: ["选一种格式，拖动“数值”，看符号、指数、尾数各占几位，存进去的值与原数差多少。超出范围、落进次正规区时会怎样？",
                        "Pick a format and drag the value: see the sign, exponent and mantissa bits, and how far the stored value is from the original. What happens out of range or among the subnormals?"] } },
    { id: "range", name: ["范围与精度", "Range and precision"],
      problem: { title: ["问题：同样 16 位，FP16 和 BF16 差在哪里", "Problem: both 16 bits — how do FP16 and BF16 differ"],
                 text: ["每种格式画一条横带：从最小次正规数到最大值，深色是规格化区。右边列出相对精度。",
                        "Each format is a band from the smallest subnormal to the largest value, the normal range darker. Relative precision is listed on the right."] } },
    { id: "sum", name: ["大数吃小数", "Swamping"],
      problem: { title: ["问题：0.0001 加一万次等于几", "Problem: what is 0.0001 added ten thousand times"],
                 text: ["每加一次都把结果舍入到所选格式。和越大，相邻两个可表示数的间隔越大，小的增量就被舍掉了。",
                        "Each partial sum is rounded to the chosen format. As the sum grows the spacing grows, and small increments are rounded away."] },
      params: { fmt: { value: 3 } } },
  ],
  params: [
    { id: "fmt", name: ["格式（0 FP32 · 1 TF32 · 2 BF16 · 3 FP16 · 4 E5M2 · 5 E4M3 · 6 E2M1）", "Format (0 FP32 · 1 TF32 · 2 BF16 · 3 FP16 · 4 E5M2 · 5 E4M3 · 6 E2M1)"], min: 0, max: 6, step: 1, value: 3, digits: 0 },
    { id: "lgx", name: ["数值 x = 10^…", "Value x = 10^…"], min: -9, max: 6, step: 0.001, value: -1, digits: 3 },
    { id: "neg", name: ["负数（0 否 · 1 是）", "Negative (0 no · 1 yes)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "lgd", name: ["每次加 10^…", "Increment 10^…"], min: -6, max: -1, step: 0.5, value: -4, digits: 1 },
    { id: "n", name: ["加的次数", "Number of additions"], min: 100, max: 20000, step: 100, value: 10000, digits: 0 },
  ],
  legend: [{ color: "var(--red)", name: ["符号", "sign"] }, { color: "var(--blue)", name: ["指数", "exponent"] }, { color: "var(--green)", name: ["尾数", "mantissa"] }],
  tasks: [
    { id: "tenth", text: ["x = 0.1（10^−1）：在 FP16 与 BF16 中各存成多少？相对误差各多大？", "x = 0.1 (10^−1): what is stored in FP16 and in BF16? Relative errors?"],
      demo: { scene: "bits", set: { fmt: 2, lgx: -1, neg: 0 }, press: [] } },
    { id: "over", text: ["x = 70 000（10^4.845）：FP16 里变成什么？换 BF16 呢？", "x = 70,000 (10^4.845): what does FP16 store? And BF16?"],
      demo: { scene: "bits", set: { fmt: 3, lgx: 4.845 }, press: [] } },
    { id: "sub", text: ["x = 10^−6 与 10^−8：在 FP16 中各是规格化数、次正规数还是 0？", "x = 10^−6 and 10^−8: normal, subnormal or zero in FP16?"],
      demo: { scene: "bits", set: { fmt: 3, lgx: -8 }, press: [] } },
    { id: "fp8", text: ["E4M3 能存的最大数是多少？x = 500 时存成多少？E5M2 呢？", "What is the largest E4M3 number? What does x = 500 become? And in E5M2?"],
      demo: { scene: "bits", set: { fmt: 5, lgx: 2.699 }, press: [] } },
    { id: "swamp", text: ["“大数吃小数”：FP16 中 0.0001 加 10 000 次等于几？BF16 呢？FP32 呢？", "Swamping: 0.0001 added 10,000 times in FP16? BF16? FP32?"],
      demo: { scene: "sum", set: { fmt: 3, lgd: -4, n: 10000 }, press: [] } },
  ],
  think: ["为什么深度学习训练更喜欢 BF16 而不是 FP16？各在什么地方吃亏？", "Why does deep-learning training prefer BF16 to FP16? Where does each lose?",],

  F: [["FP32", 8, 23, 1, 0], ["TF32", 8, 10, 1, 0], ["BF16", 8, 7, 1, 0], ["FP16", 5, 10, 1, 0], ["FP8 E5M2", 5, 2, 1, 0], ["FP8 E4M3", 4, 3, 0, 1], ["FP4 E2M1", 2, 1, 0, 0]],
  fmt(i) {
    const [name, e, m, ieee, nanTop] = this.F[i], bias = 2 ** (e - 1) - 1, top = 2 ** e - 1, emax = (ieee ? top - 1 : top) - bias;
    let mant = 2 - 2 ** -m;
    if (nanTop) mant -= 2 ** -m;
    return { name, e, m, ieee, bias, emax, max: mant * 2 ** emax, minN: 2 ** (1 - bias), minS: 2 ** (1 - bias - m), eps: 2 ** -m };
  },
  // 就近舍入、平分取偶（与 _ch8.round_to 相同）
  round(x, f) {
    if (x === 0 || !isFinite(x)) return x;
    const a = Math.abs(x);
    const ex = Math.max(Math.floor(Math.log2(a)), 1 - f.bias), q = 2 ** (ex - f.m);
    let k = a / q, r = Math.round(k);
    if (Math.abs(k - Math.trunc(k) - 0.5) < 1e-12) r = Math.trunc(k) % 2 === 0 ? Math.trunc(k) : Math.trunc(k) + 1;   // 平分取偶
    let v = r * q;
    if (v > f.max) v = f.ieee ? Infinity : f.max;
    return Math.sign(x) * v;
  },
  bits(v, f) {          // 存好的值 → [符号, 指数字段, 尾数字段]（整数）
    const s = v < 0 || Object.is(v, -0) ? 1 : 0, a = Math.abs(v);
    if (!isFinite(a)) return [s, 2 ** f.e - 1, 0];
    if (a === 0) return [s, 0, 0];
    if (a < f.minN) return [s, 0, Math.round(a / f.minS)];
    const ex = Math.floor(Math.log2(a));
    return [s, ex + f.bias, Math.round((a / 2 ** ex - 1) * 2 ** f.m)];
  },
  num(api, v) {
    if (!isFinite(v)) return v > 0 ? "+∞" : "−∞";
    if (v === 0) return "0";
    const a = Math.abs(v);
    return (a >= 1e5 || a < 1e-3) ? v.toExponential(6).replace("e", " × 10^") : String(+v.toPrecision(9));
  },
  reset(api, s) {},
  readouts(api, s) {
    const f = this.fmt(api.p.fmt);
    if (api.scene === "sum") {
      const d = 10 ** api.p.lgd, n = api.p.n;
      let t = 0;
      for (let i = 0; i < n; i++) t = this.round(t + d, f);
      if (api.p.fmt === 3 && api.p.lgd === -4 && n === 10000) api.done("swamp");
      return [[["格式", "Format"], f.name], [["应得的和", "Exact sum"], this.num(api, d * n)], [["实际的和", "Computed sum"], this.num(api, t)],
              [["和为 1 附近时相邻两数的间隔", "Spacing near 1"], this.num(api, f.eps)]];
    }
    const x = (api.p.neg ? -1 : 1) * 10 ** api.p.lgx, v = this.round(x, f), [sg, ef, mf] = this.bits(v, f);
    const kind = !isFinite(v) ? api.T("溢出为无穷", "overflow to ∞") : v === 0 ? api.T("下溢为 0", "underflow to 0") :
      Math.abs(v) < f.minN ? api.T("次正规数", "subnormal") : Math.abs(v) === f.max && Math.abs(x) > f.max ? api.T("饱和到最大值", "saturated to max") : api.T("规格化数", "normal");
    const rel = isFinite(v) ? Math.abs(v - x) / Math.abs(x) : Infinity;
    if (Math.abs(api.p.lgx + 1) < 1e-6 && (api.p.fmt === 2 || api.p.fmt === 3)) api.done("tenth");
    if (api.p.lgx > 4.84 && api.p.lgx < 4.85 && api.p.fmt === 3) api.done("over");
    if (api.p.fmt === 3 && api.p.lgx <= -6 && api.p.lgx >= -8) api.done("sub");
    if (api.p.fmt === 5 && api.p.lgx > 2.69 && api.p.lgx < 2.71) api.done("fp8");
    return [[["格式", "Format"], `${f.name}（1 + ${f.e} + ${f.m} 位）`], [["原数 x", "x"], this.num(api, x)], [["存进去的值", "Stored"], this.num(api, v)],
            [["相对误差", "Relative error"], !isFinite(rel) ? "—" : rel > 0 && rel < 1e-5 ? (rel * 100).toExponential(2) + "%" : api.fmt(rel * 100, 4) + "%"], [["类别", "Kind"], kind],
            [["位：符号 | 指数 | 尾数", "Bits: sign | exponent | mantissa"], `${sg} | ${ef.toString(2).padStart(f.e, "0")} | ${mf.toString(2).padStart(f.m, "0")}`]];
  },
  draw(api, s) {
    const { w, h } = api, m = 16;
    if (api.scene === "range") return this.drawRange(api);
    if (api.scene === "sum") return this.drawSum(api);
    const f = this.fmt(api.p.fmt), x = (api.p.neg ? -1 : 1) * 10 ** api.p.lgx, v = this.round(x, f), [sg, ef, mf] = this.bits(v, f);
    const nb = 1 + f.e + f.m, bw = Math.min(34, (w - 2 * m) / nb), x0 = (w - nb * bw) / 2, y0 = 40;
    const bit = (k, val, col) => { api.rect(x0 + k * bw, y0, bw - 2, 30, api.css(col)); api.label(String(val), x0 + k * bw + bw / 2 - 1, y0 + 20, "#fff", 13, "center"); };
    bit(0, sg, "--red");
    for (let i = 0; i < f.e; i++) bit(1 + i, (ef >> (f.e - 1 - i)) & 1, "--blue");
    for (let i = 0; i < f.m; i++) bit(1 + f.e + i, (mf >> (f.m - 1 - i)) & 1, "--green");
    api.label(api.T(`${f.name}：1 位符号、${f.e} 位指数（偏置 ${f.bias}）、${f.m} 位尾数`, `${f.name}: 1 sign, ${f.e} exponent (bias ${f.bias}), ${f.m} mantissa bits`), w / 2, y0 - 12, api.css("--ink"), 13, "center");
    // 数轴：x 附近的几个可表示数
    const a = Math.abs(x), ex = Math.max(Math.floor(Math.log2(a || 1)), 1 - f.bias), q = 2 ** (ex - f.m);
    const c = Math.round(a / q), ly = h - 70, lx0 = m + 20, lx1 = w - m - 20;
    const lo = (c - 4) * q, hi = (c + 4) * q, X = (t) => lx0 + (t - lo) / (hi - lo) * (lx1 - lx0);
    api.line(lx0, ly, lx1, ly, api.css("--grid"), 2);
    for (let k = c - 4; k <= c + 4; k++) {
      const t = k * q;
      if (t < 0 || t > f.max) continue;
      api.line(X(t), ly - 8, X(t), ly + 8, api.css("--blue"), 2);
    }
    if (isFinite(v)) api.circle(X(Math.abs(v)), ly, 6, api.css("--green"));
    api.line(X(a), ly - 22, X(a), ly + 22, api.css("--red"), 2, [4, 3]);
    api.label(api.T("红线：x；蓝色刻度：附近可表示的数（间隔 ", "red: x; blue ticks: nearby representable numbers (spacing ") + this.num(api, q) + api.T("）；绿点：存进去的值", "); green: stored value"),
              w / 2, ly + 40, api.css("--muted"), 11, "center");
  },
  drawRange(api) {
    const { w, h } = api, m = 16, x0 = 110, x1 = w - 150, lo = -46, hi = 39;
    const X = (lg) => x0 + (lg - lo) / (hi - lo) * (x1 - x0), rowH = (h - 60) / 7;
    for (let e = -40; e <= 35; e += 10) { api.line(X(e), 20, X(e), h - 30, api.css("--grid"), 1); api.label("10^" + e, X(e), h - 14, api.css("--muted"), 10, "center"); }
    for (let i = 0; i < 7; i++) {
      const f = this.fmt(i), y = 26 + i * rowH, on = i === api.p.fmt;
      api.label(f.name, x0 - 8, y + rowH / 2 + 4, api.css(on ? "--ink" : "--muted"), 12, "right");
      api.rect(X(Math.log10(f.minS)), y + rowH * 0.2, X(Math.log10(f.minN)) - X(Math.log10(f.minS)), rowH * 0.6, api.css("--grid"));
      api.rect(X(Math.log10(f.minN)), y + rowH * 0.2, X(Math.log10(f.max)) - X(Math.log10(f.minN)), rowH * 0.6, api.css(on ? "--blue" : "--muted"));
      api.label(api.T("精度 ", "eps ") + this.num(api, f.eps), x1 + 10, y + rowH / 2 + 4, api.css("--muted"), 11);
    }
    const x = 10 ** api.p.lgx;
    api.line(X(Math.log10(x)), 20, X(Math.log10(x)), h - 30, api.css("--red"), 2, [4, 3]);
  },
  drawSum(api) {
    const { w, h } = api, m = 16, f = this.fmt(api.p.fmt), d = 10 ** api.p.lgd, n = api.p.n;
    const x0 = m + 50, y0 = m + 10, pw = w - x0 - m, ph = h - y0 - 40, top = d * n * 1.05;
    const X = (i) => x0 + i / n * pw, Y = (v) => y0 + ph - v / top * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"));
    api.line(X(0), Y(0), X(n), Y(d * n), api.css("--muted"), 1.5, [5, 4]);
    let t = 0, prev = [X(0), Y(0)];
    const stride = Math.max(1, Math.floor(n / 400));
    for (let i = 1; i <= n; i++) {
      t = this.round(t + d, f);
      if (i % stride === 0) { const pt = [X(i), Y(t)]; api.line(prev[0], prev[1], pt[0], pt[1], api.css("--blue"), 2); prev = pt; }
    }
    for (let k = 0; k <= 4; k++) api.label(this.num(api, top * k / 4), x0 - 4, Y(top * k / 4) + 4, api.css("--muted"), 10, "right");
    api.label(api.T("虚线：应得的和；蓝线：每次都舍入到 ", "dashed: exact; blue: rounded to ") + f.name + api.T(" 的和", " every step"), x0 + 8, y0 + 16, api.css("--muted"), 12);
  },
});
