// 实验 13.1 从共现到类比（配 13.1 节）。三个场景：
//   cooccur：看共现矩阵——“精轴”与“终检”“精加工”一起出现，与“车床”“顶尖”也一起出现；
//   train  ：在浏览器里真的训一个 skip-gram（负采样），看向量在两个主方向上怎样分开；
//   analogy：检验类比关系 精X − 粗X + 粗Y ≈ 精Y 在当前设置下成立几次。
// 语料由程序按模板生成（与书中 code/_ch13.py 的 corpus() 同一套规则），不需要联网，也不下载任何模型。
WQ.lab({
  title: ["实验 13.1 从共现到类比", "Lab 13.1 From co-occurrence to analogy"],
  goal: ["自己训一个词向量：改维数、窗口、负样本个数与训练轮数，看什么时候“精轴 − 粗轴 + 粗齿轮 ≈ 精齿轮”这类类比才成立，什么时候不成立。",
         "Train your own word vectors: change the dimension, window, number of negative samples and epochs, and see when analogies like “fine shaft − rough shaft + rough gear ≈ fine gear” hold — and when they don't."],
  scenes: [
    { id: "cooccur", name: ["共现", "Co-occurrence"],
      problem: { title: ["问题：词的意思从哪里来", "Problem: where meaning comes from"],
                 text: ["词向量不懂零件，它只看见“谁和谁一起出现”。“精轴”旁边常有“终检”“精加工”，也常有“车床”“顶尖”——前者来自等级，后者来自零件。两件事混在一句话里，模型要自己把它们分到不同的方向上去。",
                        "A word vector knows nothing about parts; it only sees what co-occurs with what. “fine shaft” sits next to both grade words and shaft words — the model has to separate those two things into different directions by itself."] } },
    { id: "train", name: ["训练", "Training"],
      problem: { title: ["问题：几维够用", "Problem: how many dimensions"],
                 text: ["维数太小，五类零件与两个等级挤在一起，什么方向都分不开；维数够了，零件聚成簇、等级成了簇间一致的方向。训练轮数与负样本个数也一样：不够就学不出结构。",
                        "Too few dimensions and the parts and grades are crammed together; with enough, parts form clusters and the grade becomes a consistent direction between them. Too few epochs or negative samples and nothing separates either."] } },
    { id: "analogy", name: ["类比", "Analogy"],
      problem: { title: ["问题：类比为什么是加减法", "Problem: why analogy is arithmetic"],
                 text: ["如果“粗 → 精”在每一簇里都是同一个位移，那么把这个位移加到另一类零件的“粗”上，自然落在它的“精”附近。类比做得对，说明向量空间里真的有一个“等级”方向；做不对，往往是维数、轮数或语料不够。",
                        "If “rough → fine” is the same displacement in every cluster, adding it to another part's “rough” lands near that part's “fine”. Analogies working means the space really has a grade direction; failing usually means too few dimensions, epochs or data."] } },
  ],
  params: [
    { id: "dim", name: ["向量维数", "Dimensions"], min: 2, max: 32, step: 2, value: 24, digits: 0 },
    { id: "epochs", name: ["训练轮数", "Epochs"], min: 1, max: 20, step: 1, value: 10, digits: 0 },
    { id: "neg", name: ["每对的负样本个数", "Negative samples"], min: 1, max: 10, step: 1, value: 5, digits: 0 },
    { id: "window", name: ["窗口（左右各几个词）", "Window"], min: 1, max: 3, step: 1, value: 2, digits: 0 },
    { id: "lr", name: ["步长", "Learning rate"], min: 0.005, max: 0.1, step: 0.005, value: 0.025, digits: 3 },
    { id: "sent", name: ["语料句数", "Sentences"], min: 200, max: 4000, step: 200, value: 2000, digits: 0 },
    { id: "seed", name: ["随机种子", "Seed"], min: 0, max: 9, step: 1, value: 0, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["精（细加工）", "fine"] }, { color: "var(--red)", name: ["粗（粗加工）", "rough"] },
           { color: "var(--green)", name: ["类比落点", "analogy target"] }],
  tasks: [
    { id: "small", text: ["把维数降到 2：类比还成立几对？同一零件（粗与精）的余弦与同一等级（不同零件）的余弦，哪个反而更大？",
                          "Drop to 2 dimensions: do the analogies still hold? How far apart are the within-kind and across-kind similarities?"],
      demo: { scene: "train", set: { dim: 2 }, press: [] } },
    { id: "epoch", text: ["维数回到 24，把语料降到 200 句、轮数降到 1（即“只看过很少的词对”）：类比正确率变成多少？这说明能不能做类比是训练出来的，不是向量天生的。",
                          "Back to 24 dimensions, cut the corpus to 200 sentences and the epochs to 1 — very few training pairs. What is the analogy accuracy? Analogy is produced by training, not inherent to vectors."],
      demo: { scene: "analogy", set: { dim: 24, sent: 200, epochs: 1 }, press: [] } },
    { id: "neg1", text: ["把负样本个数降到 1、步长加到 0.1：同类词的余弦变大还是变小？训练还稳吗（看“是否发散”）？",
                         "Cut the negative samples to 1 and raise the learning rate to 0.1: does the within-kind cosine go up or down, and is training still stable (see “diverged”)?"],
      demo: { scene: "train", set: { sent: 2000, epochs: 10, neg: 1, lr: 0.1 }, press: [] } },
    { id: "data", text: ["把维数降到 4（语料与轮数回到默认）：20 对类比里错几对？错的是哪几类零件？",
                         "Set the dimension to 4 (corpus and epochs back to default): how many of the 20 analogies fail, and for which kinds of part?"],
      demo: { scene: "analogy", set: { dim: 4, neg: 5, lr: 0.025, sent: 2000, epochs: 10 }, press: [] } },
    { id: "ok", text: ["回到默认设置：类比应当全对（20 对里 20 对）。记下此时的同类与异类余弦，填进表 1。",
                       "Back to the defaults: all 20 analogies should hold. Record the within-kind and across-kind cosines in Table 1."],
      demo: { scene: "analogy", set: { dim: 24, epochs: 10, neg: 5, lr: 0.025, sent: 2000 }, press: [] } },
  ],
  think: ["如果语料里“精”只跟某一种零件一起出现，类比还会成立吗？这对“用网络日志训出来的词向量会学到什么”意味着什么？",
          "If “fine” only ever co-occurred with one kind of part, would the analogy still hold? What does that imply about vectors trained on web text?"],

  BASE: ["轴", "齿轮", "轴承", "箱体", "螺栓"],
  GRADE: ["粗", "精"],
  CTX_BASE: { "轴": ["车床", "顶尖", "轴颈"], "齿轮": ["滚齿", "齿形", "模数"], "轴承": ["压装", "游隙", "内圈"],
              "箱体": ["镗孔", "结合面", "铸件"], "螺栓": ["扭矩", "螺纹", "垫片"] },
  CTX_GRADE: { "粗": ["留量", "粗加工", "大进给"], "精": ["终检", "精加工", "小进给"] },

  // 确定性的随机数（线性同余）：同一组参数永远给同一个结果，学生记下的数字可复算
  rng(seed) {
    let s = (seed * 2654435761 + 1013904223) >>> 0;
    return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  },
  gauss(r) {
    const u = Math.max(1e-9, r()), v = r();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  },
  corpus(p) {
    const r = this.rng(p.seed + 13), out = [];
    for (let i = 0; i < p.sent; i++) {
      const b = this.BASE[Math.floor(r() * this.BASE.length)];
      const g = this.GRADE[Math.floor(r() * this.GRADE.length)];
      const cb = this.CTX_BASE[b].slice(), cg = this.CTX_GRADE[g].slice();
      const pick = (arr) => arr.splice(Math.floor(r() * arr.length), 1)[0];
      out.push([pick(cb), pick(cb), g + b, pick(cg), pick(cg)]);
    }
    return out;
  },
  train(p) {
    const key = [p.dim, p.epochs, p.neg, p.window, p.lr, p.sent, p.seed].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const t0 = Date.now();
    const sents = this.corpus(p), ix = {}, vocab = [];
    for (const s of sents) for (const w of s) if (!(w in ix)) { ix[w] = vocab.length; vocab.push(w); }
    const V = vocab.length, D = p.dim, r = this.rng(p.seed + 7);
    const W = new Float64Array(V * D), C = new Float64Array(V * D);
    for (let i = 0; i < V * D; i++) { W[i] = 0.1 * this.gauss(r); C[i] = 0.1 * this.gauss(r); }
    const freq = new Float64Array(V);
    for (const s of sents) for (const w of s) freq[ix[w]]++;
    const cum = new Float64Array(V);
    let tot = 0;
    for (let i = 0; i < V; i++) { tot += Math.pow(freq[i], 0.75); cum[i] = tot; }
    const sampleNeg = () => {                                   // 按词频的 0.75 次方抽负样本
      const x = r() * tot;
      let lo = 0, hi = V - 1;
      while (lo < hi) { const m = (lo + hi) >> 1; if (cum[m] < x) lo = m + 1; else hi = m; }
      return lo;
    };
    const pairs = [];
    for (const s of sents) {
      for (let i = 0; i < s.length; i++) {
        for (let j = Math.max(0, i - p.window); j < Math.min(s.length, i + p.window + 1); j++) {
          if (i !== j) pairs.push([ix[s[i]], ix[s[j]]]);
        }
      }
    }
    for (let e = 0; e < p.epochs; e++) {
      for (let n = pairs.length - 1; n > 0; n--) {              // 每轮打乱
        const m = Math.floor(r() * (n + 1));
        const t = pairs[n]; pairs[n] = pairs[m]; pairs[m] = t;
      }
      for (const [a, b] of pairs) {
        const aw = a * D, grad = new Float64Array(D);
        for (let s = 0; s <= p.neg; s++) {
          const c = s === 0 ? b : sampleNeg(), cw = c * D, lab = s === 0 ? 1 : 0;
          let z = 0;
          for (let d = 0; d < D; d++) z += C[cw + d] * W[aw + d];
          z = Math.max(-30, Math.min(30, z));
          const g = p.lr * (lab - 1 / (1 + Math.exp(-z)));
          for (let d = 0; d < D; d++) { grad[d] += g * C[cw + d]; C[cw + d] += g * W[aw + d]; }
        }
        for (let d = 0; d < D; d++) W[aw + d] += grad[d];
      }
    }
    const val = { ix, vocab, W, D, ms: Date.now() - t0, pairs: pairs.length, finite: W.every(Number.isFinite) };
    Object.assign(val, this.measure(val));
    this._c = { key, val };
    return val;
  },
  vec(t, w) { const i = t.ix[w] * t.D; return t.W.slice(i, i + t.D); },
  cos(a, b) {
    let d = 0, na = 0, nb = 0;
    for (let i = 0; i < a.length; i++) { d += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
    return d / Math.max(Math.sqrt(na * nb), 1e-12);
  },
  measure(t) {
    const words = [];
    for (const b of this.BASE) for (const g of this.GRADE) words.push(g + b);
    let sameP = 0, nSameP = 0, sameG = 0, nSameG = 0;
    for (const b of this.BASE) { sameP += this.cos(this.vec(t, "粗" + b), this.vec(t, "精" + b)); nSameP++; }
    for (const g of this.GRADE) {
      for (let i = 0; i < this.BASE.length; i++) {
        for (let j = i + 1; j < this.BASE.length; j++) { sameG += this.cos(this.vec(t, g + this.BASE[i]), this.vec(t, g + this.BASE[j])); nSameG++; }
      }
    }
    let ok = 0, tot = 0, example = "";
    for (const b1 of this.BASE) {
      for (const b2 of this.BASE) {
        if (b1 === b2) continue;
        tot++;
        const a = this.vec(t, "精" + b1), c = this.vec(t, "粗" + b1), d = this.vec(t, "粗" + b2);
        const q = a.map((x, i) => x - c[i] + d[i]);
        let best = "", bs = -2;
        for (const w of t.vocab) {
          if (w === "精" + b1 || w === "粗" + b1 || w === "粗" + b2) continue;
          const s = this.cos(q, this.vec(t, w));
          if (s > bs) { bs = s; best = w; }
        }
        if (best === "精" + b2) ok++;
        if (!example) example = `精${b1} − 粗${b1} + 粗${b2} → ${best}`;
      }
    }
    return { cosSamePart: sameP / nSameP, cosSameGrade: sameG / nSameG, anaOk: ok, anaTot: tot, example, words };
  },
  reset(api, s) {},
  readouts(api, s) {
    const p = api.p, t = this.train(p);
    if (p.dim <= 2) api.done("small");
    if (p.epochs <= 1 && p.sent <= 200) api.done("epoch");
    if (p.neg <= 1 && p.lr >= 0.1) api.done("neg1");
    if (p.dim <= 4) api.done("data");
    if (t.anaOk === t.anaTot && p.sent >= 2000) api.done("ok");
    return [[["词表 / 训练对数", "vocabulary / training pairs"], t.vocab.length + " / " + t.pairs],
            [["类比正确", "analogies correct"], t.anaOk + " / " + t.anaTot],
            [["一个例子", "one example"], t.example],
            [["同一零件（粗与精）的余弦", "same part, rough vs fine"], api.fmt(t.cosSamePart, 2)],
            [["同一等级（不同零件）的余弦", "same grade, different parts"], api.fmt(t.cosSameGrade, 2)],
            [["训练用时 / 是否发散", "training time / diverged"], t.ms + " ms / " + (t.finite ? api.T("否", "no") : api.T("是", "yes"))]];
  },
  draw(api, s) {
    const { w, h } = api, m = 40, p = api.p, t = this.train(p);
    if (api.scene === "cooccur") {                              // 共现矩阵：行是复合词，列是上下文词
      const ctx = [];
      for (const b of this.BASE) for (const c of this.CTX_BASE[b]) ctx.push(c);
      for (const g of this.GRADE) for (const c of this.CTX_GRADE[g]) ctx.push(c);
      const rows = t.words, co = rows.map(() => new Float64Array(ctx.length));
      for (const s2 of this.corpus(p)) {
        const wi = rows.indexOf(s2[2]);
        if (wi < 0) continue;
        for (const c of s2) { const ci = ctx.indexOf(c); if (ci >= 0) co[wi][ci]++; }
      }
      let mx = 1;
      for (const r of co) for (const x of r) mx = Math.max(mx, x);
      const cw = (w - 2 * m - 70) / ctx.length, chh = (h - 2 * m) / rows.length;
      rows.forEach((rw, i) => {
        api.label(rw, m, m + i * chh + chh * 0.7, rw[0] === "精" ? api.css("--blue") : api.css("--red"), 11);
        co[i].forEach((x, j) => {
          const a = x / mx;
          if (a > 0.01) api.rect(m + 70 + j * cw, m + i * chh, Math.max(1, cw - 1), chh - 2,
                                 rw[0] === "精" ? api.css("--blue") : api.css("--red"));
        });
      });
      api.label(api.T("列＝上下文词（前 15 个来自零件，后 6 个来自等级）", "columns = context words (15 part, 6 grade)"),
                m + 70, h - 12, api.css("--muted"), 11);
      return;
    }
    // train / analogy：把向量投到两个主方向上（幂迭代求前两个方向，够画图用）
    const words = t.words, X = words.map((wd) => Array.from(this.vec(t, wd)));
    const mean = new Float64Array(t.D);
    X.forEach((r) => r.forEach((x, d) => { mean[d] += x / X.length; }));
    const Xc = X.map((r) => r.map((x, d) => x - mean[d]));
    const dir = (skip) => {
      let u = new Float64Array(t.D).fill(1 / Math.sqrt(t.D));
      for (let it = 0; it < 60; it++) {
        const nu = new Float64Array(t.D);
        for (const r of Xc) {
          let dot = 0;
          for (let d = 0; d < t.D; d++) dot += r[d] * u[d];
          for (let d = 0; d < t.D; d++) nu[d] += dot * r[d];
        }
        if (skip) { let dot = 0; for (let d = 0; d < t.D; d++) dot += nu[d] * skip[d]; for (let d = 0; d < t.D; d++) nu[d] -= dot * skip[d]; }
        let n = 0;
        for (let d = 0; d < t.D; d++) n += nu[d] * nu[d];
        n = Math.sqrt(n) || 1;
        for (let d = 0; d < t.D; d++) u[d] = nu[d] / n;
      }
      return u;
    };
    const u1 = dir(null), u2 = dir(u1);
    const proj = Xc.map((r) => {
      let a = 0, b = 0;
      for (let d = 0; d < t.D; d++) { a += r[d] * u1[d]; b += r[d] * u2[d]; }
      return [a, b];
    });
    let mx = 1e-9;
    for (const [a, b] of proj) mx = Math.max(mx, Math.abs(a), Math.abs(b));
    const X0 = (a) => w / 2 + a / mx * (w / 2 - m - 50), Y0 = (b) => h / 2 - b / mx * (h / 2 - m);
    words.forEach((wd, i) => {
      const col = wd[0] === "精" ? api.css("--blue") : api.css("--red");
      api.rect(X0(proj[i][0]) - 3, Y0(proj[i][1]) - 3, 6, 6, col);
      api.label(wd, X0(proj[i][0]) + 6, Y0(proj[i][1]) - 4, col, 11);
    });
    for (const b of this.BASE) {                                // 粗 → 精 的箭头：方向一致才能做类比
      const i = words.indexOf("粗" + b), j = words.indexOf("精" + b);
      api.line(X0(proj[i][0]), Y0(proj[i][1]), X0(proj[j][0]), Y0(proj[j][1]), api.css("--muted"), 1.2);
    }
    if (api.scene === "analogy") {
      const i1 = words.indexOf("精轴"), i0 = words.indexOf("粗轴"), i2 = words.indexOf("粗齿轮");
      const q = [proj[i1][0] - proj[i0][0] + proj[i2][0], proj[i1][1] - proj[i0][1] + proj[i2][1]];
      api.line(X0(proj[i2][0]), Y0(proj[i2][1]), X0(q[0]), Y0(q[1]), api.css("--green"), 2);
      api.rect(X0(q[0]) - 4, Y0(q[1]) - 4, 8, 8, api.css("--green"));
      api.label(api.T("精轴 − 粗轴 + 粗齿轮", "fine shaft − rough shaft + rough gear"),
                Math.min(X0(q[0]) + 8, w - m - 150), Y0(q[1]) + 14, api.css("--green"), 11);
    }
  },
});
