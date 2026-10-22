// 实验 14.1 把图和文放进同一个空间（配 14.1、14.3 节）。
// 两个场景：
//   space    ：看"图 × 文"的相似度矩阵——训练之前几乎没有结构，训练之后对角线亮起来；
//   retrieve ：看命中率随批大小、温度、噪声怎么变，以及检索池一大命中率怎样掉。
// 全部在浏览器里现算：合成属性 → 两端特征 → 两个线性投影 → InfoNCE 训练 → 命中率。
// 与 code/_ch14.py 是同一套做法，只是规模小一些（图里 600 对，书里 6000 对）。
WQ.lab({
  title: ["实验 14.1 对比学习：把图和文对上", "Lab 14.1 Contrastive learning: aligning images and text"],
  goal: ["亲手调批大小、温度、噪声，看“配对的靠近、不配对的推开”这件事到底被什么决定。做完能回答三个问题：为什么大家都把批开得很大、温度低了会怎样、检索池一大为什么命中率就掉。",
         "Turn the knobs — batch size, temperature, noise — and see what actually drives alignment: why batches are huge, what a low temperature does, and why a larger retrieval pool lowers recall."],
  scenes: [
    { id: "space", name: ["同一个空间", "One shared space"],
      problem: { title: ["问题：两个编码器各说各话", "Problem: two encoders, two unrelated spaces"],
                 text: ["视觉编码器与文本编码器是分别训练的：同一件事（一张缺陷照片与那句检验记录）在两边各是一个向量，彼此毫无关系。对比学习只做一件事——再学两个投影，使配对的那一对靠近、同批里其余的推开。",
                        "The two encoders were trained separately, so the photo and the sentence describing it start out unrelated. Contrastive learning adds two projections trained to pull each pair together and push the rest apart."] } },
    { id: "retrieve", name: ["检索命中率", "Retrieval recall"],
      problem: { title: ["问题：R@1 有多少，离不开池子有多大", "Problem: R@1 means nothing without the pool size"],
                 text: ["以文搜图：给一句话，在候选图里挑最像的。池子里一百张时轻松，两万张时同一个模型就难得多——报成绩必须连池子大小一起报。",
                        "Text-to-image retrieval is easy in a pool of 100 and much harder in a pool of 20,000 — for the same model. A recall number without the pool size is meaningless."] } },
  ],
  params: [
    { id: "batchLog", name: ["批大小（2 的几次方）", "batch size (power of two)"], min: 3, max: 9, step: 1, value: 6, digits: 0 },
    { id: "tempLog", name: ["温度（10 的几次方）", "temperature (power of ten)"], min: -2, max: 0, step: 0.25, value: -1, digits: 2 },
    { id: "noise", name: ["拍摄噪声", "imaging noise"], min: 0.1, max: 1.5, step: 0.1, value: 0.5, digits: 1 },
    { id: "poolLog", name: ["检索池大小（10 的几次方）", "retrieval pool (power of ten)"], min: 2, max: 3, step: 0.25, value: 2.5, digits: 2 },
  ],
  legend: [{ color: "var(--blue)", name: ["配对的（对角线）", "matching pair"] },
           { color: "var(--red)", name: ["不配对的", "non-matching"] }],
  tasks: [
    { id: "align", text: ["在“同一个空间”里把噪声调到 0.5、批调到 64：训练之后相似度矩阵的对角线有多亮？配对与不配对的平均相似度差多少？",
                          "In the shared-space scene with noise 0.5 and batch 64, how bright is the diagonal? What is the gap between matching and non-matching similarity?"],
      demo: { scene: "space", set: { noise: 0.5, batchLog: 6 }, press: [] } },
    { id: "batch", text: ["把批从 8 一档一档加到 512（看过的样本数固定）：命中率先涨后落，最好的那一档是多少？一个批里有多少个“不是它”，这一档又只剩多少训练步？",
                          "Step the batch from 8 up to 512 at a fixed sample budget: recall rises and then falls. Which batch is best? How many negatives per step does it see, and how few steps does it get?"],
      demo: { scene: "retrieve", set: { batchLog: 9 }, press: [] } },
    { id: "temp", text: ["把温度调到 1（10 的 0 次方）再调回 0.01：命中率哪一头高？低温度时梯度压在谁身上？",
                         "Set the temperature to 1, then to 0.01: which end gives better recall, and where does the gradient go when it is low?"],
      demo: { scene: "retrieve", set: { tempLog: 0 }, press: [] } },
    { id: "pool", text: ["把检索池从 100 加到 1000：瞎猜的 R@1 掉了多少倍？“比瞎猜好多少倍”这一行又涨了多少？由此说明：报 R@1 不报池子大小，这个数没有意义。",
                         "Grow the pool from 100 to 1000: how far does the chance R@1 fall, and how far does the times-better-than-chance line rise? A recall number without its pool size means nothing."],
      demo: { scene: "retrieve", set: { poolLog: 3 }, press: [] } },
  ],
  think: ["同样看过的样本数下，大批为什么还是好一些？与“一个批里有多少个不是它”有什么关系？",
          "At the same sample budget, why is a larger batch still better? What does it have to do with the number of negatives per step?"],

  // ---------- 合成数据与训练（与 code/_ch14.py 同一套做法）
  DIM: 16, OUT: 8, NP: 6, NK: 5, NL: 4, NS: 8,
  rand(seed) { let t = seed >>> 0; return () => { t += 0x6d2b79f5; let x = Math.imul(t ^ (t >>> 15), 1 | t); x ^= x + Math.imul(x ^ (x >>> 7), 61 | x); return ((x ^ (x >>> 14)) >>> 0) / 4294967296; }; },
  gauss(rnd) { let u = 0, v = 0; while (u === 0) u = rnd(); while (v === 0) v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  basis() {
    if (this._b) return this._b;
    const rnd = this.rand(777), mk = (k) => Array.from({ length: k }, () => Array.from({ length: this.DIM }, () => this.gauss(rnd)));
    this._b = { ip: mk(this.NP), ik: mk(this.NK), il: mk(this.NL), is: mk(this.NS),
                tp: mk(this.NP), tk: mk(this.NK), tl: mk(this.NL), ts: mk(this.NS) };
    return this._b;
  },
  data(n, noise, seed) {
    const b = this.basis(), rnd = this.rand(seed), a = [], xi = [], xt = [];
    for (let i = 0; i < n; i++) {
      const p = Math.floor(rnd() * this.NP), k = Math.floor(rnd() * this.NK);
      const l = Math.floor(rnd() * this.NL), q = Math.floor(rnd() * this.NS);
      a.push(((p * this.NK + k) * this.NL + l) * this.NS + q);
      const vi = new Float64Array(this.DIM), vt = new Float64Array(this.DIM);
      for (let d = 0; d < this.DIM; d++) {
        vi[d] = b.ip[p][d] + b.ik[k][d] + 0.6 * b.il[l][d] + 0.7 * b.is[q][d] + noise * this.gauss(rnd);
        vt[d] = b.tp[p][d] + b.tk[k][d] + 0.6 * b.tl[l][d] + 0.7 * b.ts[q][d] + 0.1 * this.gauss(rnd);
      }
      xi.push(vi); xt.push(vt);
    }
    return { xi, xt, a };
  },
  norm(v) { let s = 0; for (const x of v) s += x * x; s = Math.sqrt(Math.max(s, 1e-12)); return v.map((x) => x / s); },
  project(X, W) { return X.map((v) => { const o = new Array(this.OUT).fill(0); for (let d = 0; d < this.DIM; d++) { const x = v[d]; for (let j = 0; j < this.OUT; j++) o[j] += x * W[d][j]; } return this.norm(o); }); },
  train(d, batch, temp, steps, seed) {
    const rnd = this.rand(seed + 31);
    const mk = () => Array.from({ length: this.DIM }, () => Array.from({ length: this.OUT }, () => 0.3 * this.gauss(rnd)));
    const Wi = mk(), Wt = mk(), n = d.xi.length, lr = 0.5 * Math.sqrt(batch / 64);
    for (let t = 0; t < steps; t++) {
      const idx = []; for (let i = 0; i < batch; i++) idx.push(Math.floor(rnd() * n));
      const hi = idx.map((i) => { const o = new Array(this.OUT).fill(0); for (let dd = 0; dd < this.DIM; dd++) { const x = d.xi[i][dd]; for (let j = 0; j < this.OUT; j++) o[j] += x * Wi[dd][j]; } return o; });
      const ht = idx.map((i) => { const o = new Array(this.OUT).fill(0); for (let dd = 0; dd < this.DIM; dd++) { const x = d.xt[i][dd]; for (let j = 0; j < this.OUT; j++) o[j] += x * Wt[dd][j]; } return o; });
      const ni = hi.map((v) => Math.sqrt(Math.max(v.reduce((s, x) => s + x * x, 0), 1e-12)));
      const nt = ht.map((v) => Math.sqrt(Math.max(v.reduce((s, x) => s + x * x, 0), 1e-12)));
      const zi = hi.map((v, i) => v.map((x) => x / ni[i])), zt = ht.map((v, i) => v.map((x) => x / nt[i]));
      const B = idx.length, S = [];
      for (let i = 0; i < B; i++) { const row = new Float64Array(B); for (let j = 0; j < B; j++) { let s = 0; for (let k = 0; k < this.OUT; k++) s += zi[i][k] * zt[j][k]; row[j] = s / temp; } S.push(row); }
      const P = S.map((row) => { let m = -Infinity; for (const x of row) m = Math.max(m, x); let s = 0; const e = row.map((x) => { const y = Math.exp(x - m); s += y; return y; }); return e.map((y) => y / s); });
      const Q = []; for (let j = 0; j < B; j++) { let m = -Infinity; for (let i = 0; i < B; i++) m = Math.max(m, S[i][j]); let s = 0; const col = []; for (let i = 0; i < B; i++) { const y = Math.exp(S[i][j] - m); s += y; col.push(y); } Q.push(col.map((y) => y / s)); }
      const G = []; for (let i = 0; i < B; i++) { const row = new Float64Array(B); for (let j = 0; j < B; j++) row[j] = (P[i][j] - (i === j ? 1 : 0) + Q[j][i] - (i === j ? 1 : 0)) / (2 * B * temp); G.push(row); }
      const gzi = [], gzt = [];
      for (let i = 0; i < B; i++) { const o = new Array(this.OUT).fill(0); for (let j = 0; j < B; j++) for (let k = 0; k < this.OUT; k++) o[k] += G[i][j] * zt[j][k]; gzi.push(o); }
      for (let j = 0; j < B; j++) { const o = new Array(this.OUT).fill(0); for (let i = 0; i < B; i++) for (let k = 0; k < this.OUT; k++) o[k] += G[i][j] * zi[i][k]; gzt.push(o); }
      for (let i = 0; i < B; i++) {
        const di = gzi[i].reduce((s, g, k) => s + g * zi[i][k], 0), dt = gzt[i].reduce((s, g, k) => s + g * zt[i][k], 0);
        const ghi = gzi[i].map((g, k) => (g - zi[i][k] * di) / ni[i]), ght = gzt[i].map((g, k) => (g - zt[i][k] * dt) / nt[i]);
        const vi = d.xi[idx[i]], vt = d.xt[idx[i]];
        for (let dd = 0; dd < this.DIM; dd++) for (let k = 0; k < this.OUT; k++) { Wi[dd][k] -= lr * vi[dd] * ghi[k]; Wt[dd][k] -= lr * vt[dd] * ght[k]; }
      }
    }
    return { Wi, Wt };
  },
  recall(zq, zd, lq, ld) {
    let hit1 = 0, hit10 = 0;
    for (let i = 0; i < zq.length; i++) {
      const s = zd.map((z, j) => { let v = 0; for (let k = 0; k < this.OUT; k++) v += zq[i][k] * z[k]; return [v, j]; });
      s.sort((x, y) => y[0] - x[0]);
      if (ld[s[0][1]] === lq[i]) hit1++;
      for (let r = 0; r < 10 && r < s.length; r++) if (ld[s[r][1]] === lq[i]) { hit10++; break; }
    }
    return { r1: hit1 / zq.length * 100, r10: hit10 / zq.length * 100 };
  },
  calc(api) {
    const p = api.p, key = [p.batchLog, p.tempLog, p.noise, p.poolLog, api.scene].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const batch = Math.round(Math.pow(2, p.batchLog)), temp = Math.pow(10, p.tempLog);
    const SEEN = 4000, steps = Math.max(15, Math.min(150, Math.round(SEEN / batch)));
    const train = this.data(400, p.noise, 7);
    const W = this.train(train, batch, temp, steps, 3);
    const pool = Math.round(Math.pow(10, p.poolLog));
    const test = this.data(Math.min(pool, 1500), p.noise, 99);
    const zi = this.project(test.xi, W.Wi), zt = this.project(test.xt, W.Wt);
    const nq = Math.min(80, zi.length);
    const rec = this.recall(zt.slice(0, nq), zi, test.a.slice(0, nq), test.a);
    // 瞎猜的基线：池子里同类的比例
    const cnt = {}; test.a.forEach((c) => { cnt[c] = (cnt[c] || 0) + 1; });
    let chance = 0; for (let i = 0; i < nq; i++) chance += cnt[test.a[i]] / test.a.length;
    chance = chance / nq * 100;
    // 相似度矩阵（取 36 个样本，按类别排序）
    const ord = test.a.map((c, i) => [c, i]).sort((x, y) => x[0] - y[0]).slice(0, 36).map((x) => x[1]);
    const M = ord.map((i) => ord.map((j) => { let v = 0; for (let k = 0; k < this.OUT; k++) v += zi[i][k] * zt[j][k]; return v; }));
    let dia = 0, off = 0, noff = 0;
    for (let i = 0; i < M.length; i++) for (let j = 0; j < M.length; j++) { if (test.a[ord[i]] === test.a[ord[j]]) dia += M[i][j]; else { off += M[i][j]; noff++; } }
    const nd = M.length * M.length - noff;
    const val = { batch, temp, steps, negatives: batch - 1, pool: test.a.length, M, ord, test,
                  r1: rec.r1, r10: rec.r10, chance, cosPair: dia / nd, cosOther: off / Math.max(noff, 1),
                  capBits: Math.log2(batch) };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; this._curve = null; },
  readouts(api, s) {
    const p = api.p, c = this.calc(api);
    if (api.scene === "space" && Math.abs(p.noise - 0.5) < 1e-9 && p.batchLog === 6) api.done("align");
    if (api.scene === "retrieve" && p.batchLog >= 9) api.done("batch");
    if (api.scene === "retrieve" && p.tempLog >= -0.01) api.done("temp");
    if (api.scene === "retrieve" && p.poolLog >= 2.99) api.done("pool");
    if (api.scene === "space") {
      return [[["批大小", "batch size"], String(c.batch)],
              [["一步见到的负样本", "negatives per step"], String(c.negatives)],
              [["训练步数（看过的样本数固定）", "steps (fixed sample budget)"], String(c.steps)],
              [["配对的平均相似度", "matching similarity"], c.cosPair.toFixed(3)],
              [["不配对的平均相似度", "non-matching"], c.cosOther.toFixed(3)],
              [["两者之差", "gap"], (c.cosPair - c.cosOther).toFixed(3)]];
    }
    return [[["批大小", "batch size"], String(c.batch)],
            [["温度", "temperature"], c.temp.toFixed(3)],
            [["检索池", "pool size"], String(c.pool)],
            [["R@1（以文搜图）", "R@1 (text to image)"], c.r1.toFixed(1) + "%"],
            [["R@10", "R@10"], c.r10.toFixed(1) + "%"],
            [["瞎猜的 R@1", "chance R@1"], c.chance.toFixed(2) + "%"],
            [["比瞎猜好多少倍", "times better than chance"], (c.r1 / Math.max(c.chance, 1e-6)).toFixed(0) + "×"]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api);
    const x0 = 70, y0 = 28, pw = w - x0 - 40, ph = h - y0 - 46;
    if (api.scene === "space") {
      const n = c.M.length, cell = Math.min(pw, ph) / n, ox = x0 + (pw - cell * n) / 2, oy = y0;
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
        const v = Math.max(-1, Math.min(1, c.M[i][j]));
        const col = v > 0 ? `rgba(214,69,65,${Math.min(1, v)})` : `rgba(44,110,190,${Math.min(1, -v)})`;
        api.rect(ox + j * cell, oy + i * cell, cell, cell, col, null, 0);
      }
      api.rect(ox, oy, cell * n, cell * n, null, api.css("--grid"), 1);
      api.label(api.T("文本（按零件、缺陷排好序）", "text (sorted by part and defect)"), ox, oy + cell * n + 18, api.css("--muted"), 12);
      api.label(api.T("图像", "image"), 8, oy + 14, api.css("--muted"), 12);
      api.label(api.T(`配对 ${c.cosPair.toFixed(2)} vs 不配对 ${c.cosOther.toFixed(2)}`,
                      `pair ${c.cosPair.toFixed(2)} vs non-pair ${c.cosOther.toFixed(2)}`),
                ox + cell * n - 190, oy - 8, api.css("--ink"), 12);
      return;
    }
    // 命中率随批大小：把几档现算一遍（结果按噪声、温度、池子缓存，免得每次重画都重训）
    const ckey = [api.p.noise, api.p.tempLog, api.p.poolLog].join(",");
    if (!this._curve || this._curve.key !== ckey) {
      const pts0 = [];
      for (let b = 3; b <= 9; b += 2) {
        const batch = Math.pow(2, b), steps = Math.max(15, Math.min(150, Math.round(4000 / batch)));
        const tr = this.data(400, api.p.noise, 7);
        const W = this.train(tr, batch, Math.pow(10, api.p.tempLog), steps, 3);
        const te = this.data(Math.min(Math.round(Math.pow(10, api.p.poolLog)), 1500), api.p.noise, 99);
        const zi = this.project(te.xi, W.Wi), zt = this.project(te.xt, W.Wt);
        const nq = Math.min(60, zi.length);
        pts0.push([b, this.recall(zt.slice(0, nq), zi, te.a.slice(0, nq), te.a).r1]);
      }
      this._curve = { key: ckey, pts: pts0 };
    }
    const pts = this._curve.pts;
    const X = (b) => x0 + (b - 3) / 6 * pw, Y = (r) => y0 + ph - r / 100 * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    for (let r = 0; r <= 100; r += 20) { api.line(x0, Y(r), x0 + pw, Y(r), api.css("--grid"), 1); api.label(r + "%", 28, Y(r) + 4, api.css("--muted"), 11); }
    let prev = null;
    for (const [b, r] of pts) { const cur = [X(b), Y(r)]; if (prev) api.line(prev[0], prev[1], cur[0], cur[1], api.css("--blue"), 2.4); api.circle(cur[0], cur[1], 3.5, null, api.css("--blue")); api.label(String(Math.pow(2, b)), cur[0] - 10, y0 + ph + 16, api.css("--muted"), 11); prev = cur; }
    api.line(x0, Y(c.chance), x0 + pw, Y(c.chance), api.css("--muted"), 1.5, [5, 4]);
    api.label(api.T(`瞎猜 ${c.chance.toFixed(2)}%`, `chance ${c.chance.toFixed(2)}%`), x0 + 6, Y(c.chance) - 6, api.css("--muted"), 11);
    api.line(X(api.p.batchLog), y0, X(api.p.batchLog), y0 + ph, api.css("--ink"), 1.5, [5, 4]);
    api.label(api.T("批大小", "batch size"), x0 + pw / 2 - 20, h - 12, api.css("--muted"), 12);
    api.label(api.T("R@1（以文搜图）", "R@1 (text to image)"), 8, y0 + 12, api.css("--muted"), 12);
  },
});
