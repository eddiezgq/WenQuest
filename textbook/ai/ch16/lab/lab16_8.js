// 实验 16.8 合成数据掺多少、偏了会怎样（配 16.8 节）。
// 两个场景：
//   mix  ：真实图只有几十张，往里掺不同数量的合成图，看检出成绩怎么走；
//   bias ：把合成器弄偏（底纹朝向固定、漏掉一类、只合成偏重的缺陷），看成绩怎样反过来掉。
// 缺陷图在浏览器里现画（24×24，磨削底纹 + 划痕/压痕/锈斑），检测器用最近邻——
// 它吃数据，所以补数据有没有用问得出来。与 code/_ch16.py 是同一套做法，只是图小一些。
WQ.lab({
  title: ["实验 16.8 合成缺陷图能不能补上训练集", "Lab 16.8 Can synthetic defects fill in for real ones"],
  goal: ["真实缺陷图只有几十张，往训练集里掺合成图，看查出率怎么走；再把合成器一样一样弄偏，看成绩从哪一档开始反过来掉。做完能回答两个问题：合成数据补的到底是什么，以及什么时候补了还不如不补。",
         "With only a few dozen real defect images, add synthetic ones and watch the detection rate; then introduce one flaw at a time into the generator and see when the gain turns into a loss. What exactly does synthetic data supply, and when is it worse than nothing?"],
  scenes: [
    { id: "mix", name: ["掺多少合成图", "How much synthetic data"],
      problem: { title: ["问题：补数据到底补了什么", "Problem: what does extra data buy"],
                 text: ["产线上七成的件是合格的，缺陷大多很轻微，起伏常比磨削刀纹还小。真实标注只有几十张，检测器学不扎实。往里掺同一个分布的合成图，看曲线下面积与“误报压到 5% 时的查出率”怎样往上走，到哪一档不再涨。",
                        "Seven parts in ten are fine, and the defects are faint — often fainter than the machining texture. With only a few dozen labelled images the detector is weak. Add synthetic images from the same distribution and watch the AUC and the recall at a 5% false-alarm rate climb, then level off."] } },
    { id: "bias", name: ["合成器偏了会怎样", "When the generator is off"],
      problem: { title: ["问题：补错了会怎样", "Problem: what if the synthetic data is off"],
                 text: ["真实的生成器不会刚好学对。这里把三种常见的偏差拆开来开关：底纹的朝向与照明固定（生成器没学会这部分变化）、整类“压痕”没合成、只合成偏重的缺陷。一样一样打开，看成绩怎样掉——掉到比完全不掺还低的那一档，就是“补了不如不补”。",
                        "A real generator never gets it exactly right. Three common flaws can be switched on here: a frozen texture orientation and lighting, a whole class never synthesized, and only severe defects. Turn them on one at a time and watch the score fall — past the no-synthetic baseline, adding data has made things worse."] } },
  ],
  params: [
    { id: "nreal", name: ["真实图有几张", "real images"], min: 20, max: 200, step: 20, value: 60, digits: 0 },
    { id: "nsyn", name: ["掺几张合成图", "synthetic images added"], min: 0, max: 1200, step: 100, value: 0, digits: 0 },
    { id: "flat", name: ["底纹朝向固定（0 否 1 是）", "frozen texture (0 no, 1 yes)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "miss", name: ["压痕这一类不合成（0 否 1 是）", "skip the dent class (0 no, 1 yes)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "sevlo", name: ["合成的最轻缺陷有多重", "lightest synthetic defect"], min: 0.08, max: 0.3, step: 0.02, value: 0.08, digits: 2 },
  ],
  legend: [{ color: "var(--red)", name: ["只用真实图", "real only"] },
           { color: "var(--green)", name: ["真实 + 合成", "real + synthetic"] },
           { color: "var(--muted)", name: ["误报 5% 处", "5% false alarms"] }],
  tasks: [
    { id: "base", text: ["先把合成图调到 0：只有 60 张真实图时，曲线下面积与误报 5% 处的查出率各是多少？",
                         "Set the synthetic count to 0: with 60 real images, what are the AUC and the recall at a 5% false-alarm rate?"],
      demo: { scene: "mix", set: { nreal: 60, nsyn: 0, flat: 0, miss: 0 }, press: [] } },
    { id: "add", text: ["把合成图加到 800 张（其余不动）：两个数各涨了多少？与把真实图加到 200 张比，哪个更划算？",
                        "Raise the synthetic count to 800: how much do both numbers improve, and how does that compare with raising the real count to 200?"],
      demo: { scene: "mix", set: { nreal: 60, nsyn: 800, flat: 0, miss: 0 }, press: [] } },
    { id: "plateau", text: ["从 800 继续加到 1200：还在涨吗？说明合成数据补的是什么、补不了什么。",
                            "Go on from 800 to 1200: is it still climbing? Say what synthetic data supplies and what it cannot."],
      demo: { scene: "mix", set: { nsyn: 1200 }, press: [] } },
    { id: "flatbg", text: ["切到第二个场景，把“底纹朝向固定”打开：成绩掉到多少？掉破“只用真实图”那条线了吗？",
                           "Switch to the second scene and freeze the texture: how far does the score fall, and does it drop below the real-only baseline?"],
      demo: { scene: "bias", set: { nsyn: 800, flat: 1, miss: 0 }, press: [] } },
    { id: "missing", text: ["再把“压痕这一类不合成”也打开：哪一类的查出率掉得最狠？其余两类呢？",
                            "Now also skip the dent class: which class loses the most, and what happens to the other two?"],
      demo: { scene: "bias", set: { nsyn: 800, flat: 1, miss: 1 }, press: [] } },
  ],
  think: ["把“底纹朝向固定”单独打开（其余两项关掉），合成图里一个缺陷都没少，成绩为什么还是掉？这件事和第 11 章讲的“捷径”是同一回事吗？",
          "Freeze only the texture, leaving every defect class and severity intact. Why does the score still fall? Is this the same thing as the shortcut problem in Chapter 11?"],

  N: 24, NTEST: 800, KNN: 7,
  rng(seed) { let s = (seed >>> 0) || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; },
  nrm(r) { const u = Math.max(r(), 1e-12), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  image(kind, sev, r, flat) {
    const N = this.N, img = new Float64Array(N * N);
    const ang = flat ? 0 : r() * Math.PI, lam = flat ? 1.9 : 1.3 + r() * 1.2;
    const ph1 = r() * 2 * Math.PI, ph2 = r() * 2 * Math.PI, sh = flat ? 0 : (r() - 0.5) * 0.8;
    const ca = Math.cos(ang), sa = Math.sin(ang);
    for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
      const u = j * ca + i * sa;
      let v = 0.50 + 0.050 * Math.sin(2 * Math.PI * u / lam + ph1) + 0.018 * Math.sin(2 * Math.PI * u / (lam * 2.3) + ph2);
      if (!flat) v += 0.060 * Math.cos((j / N - 0.5) * 2.0 + sh) + 0.040 * (i / N - 0.5);
      img[i * N + j] = v + 0.012 * this.nrm(r);
    }
    if (kind === 1) {                                    // 划痕
      const x0 = 3 + r() * (N - 6), y0 = 3 + r() * (N - 6), a = r() * Math.PI, ln = 5 + r() * 8;
      for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
        const t = Math.max(0, Math.min(1, ((j - x0) * Math.cos(a) + (i - y0) * Math.sin(a)) / ln));
        const dx = j - (x0 + t * ln * Math.cos(a)), dy = i - (y0 + t * ln * Math.sin(a));
        img[i * N + j] -= 0.45 * sev * Math.exp(-Math.pow(Math.hypot(dx, dy) / 0.6, 2));
      }
    } else if (kind === 2) {                             // 压痕
      const x0 = 4 + r() * (N - 8), y0 = 4 + r() * (N - 8), rad = 1.5 + r() * 1.5;
      for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
        const d = Math.hypot(j - x0, i - y0);
        img[i * N + j] += -0.40 * sev * Math.exp(-Math.pow(d / rad, 2)) + 0.20 * sev * Math.exp(-Math.pow((d - rad) / 0.7, 2));
      }
    } else if (kind === 3) {                             // 锈斑
      const x0 = 4 + r() * (N - 8), y0 = 4 + r() * (N - 8), rad = 2 + r() * 2;
      for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
        const d = Math.hypot(j - x0, i - y0);
        img[i * N + j] += 0.35 * sev * Math.exp(-Math.pow(d / rad, 2)) * (1 + 0.5 * this.nrm(r));
      }
    }
    return img;
  },
  feats(img) {
    const N = this.N;
    let m = 0;
    for (let i = 0; i < img.length; i++) m += img[i];
    m /= img.length;
    let sd = 0;
    for (let i = 0; i < img.length; i++) sd += (img[i] - m) * (img[i] - m);
    sd = Math.sqrt(sd / img.length);
    let gm = 0, gmax = 0, agx = 0, agy = 0;
    const mags = [];
    for (let i = 1; i < N - 1; i++) for (let j = 1; j < N - 1; j++) {
      const gx = (img[i * N + j + 1] - img[i * N + j - 1]) / 2, gy = (img[(i + 1) * N + j] - img[(i - 1) * N + j]) / 2;
      const g = Math.hypot(gx, gy);
      mags.push(g); gm += g; gmax = Math.max(gmax, g); agx += Math.abs(gx); agy += Math.abs(gy);
    }
    gm /= mags.length;
    mags.sort((a, b) => a - b);
    const p99 = mags[Math.floor(mags.length * 0.99)];
    let bmin = 1e9, bmax = -1e9;                          // 4×4 小块的最暗与最亮
    for (let bi = 0; bi + 4 <= N; bi += 4) for (let bj = 0; bj + 4 <= N; bj += 4) {
      let s = 0;
      for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) s += img[(bi + i) * N + bj + j];
      s /= 16; bmin = Math.min(bmin, s); bmax = Math.max(bmax, s);
    }
    return [m, sd, bmin, bmax, gm, gmax, p99, agx / (agy + 1e-9)];
  },
  set(n, seed, opt) {
    const r = this.rng(seed), X = [], y = [], k = [];
    const kinds = opt.miss ? [0, 1, 3] : [0, 1, 2, 3];
    const pk = opt.miss ? [0.7, 0.15, 0.15] : [0.7, 0.1, 0.1, 0.1];
    for (let i = 0; i < n; i++) {
      let u = r(), a = 0, idx = 0;
      for (; idx < kinds.length; idx++) { a += pk[idx]; if (u <= a) break; }
      idx = Math.min(idx, kinds.length - 1);
      const kind = kinds[idx];
      const sev = opt.lo + r() * (0.35 - opt.lo);
      X.push(this.feats(this.image(kind, sev, r, opt.flat)));
      y.push(kind > 0 ? 1 : 0); k.push(kind);
    }
    return { X, y, k };
  },
  score(train, Xte) {                                    // 最近邻打分（标准化之后）
    const d = train.X[0].length, mu = new Float64Array(d), sd = new Float64Array(d);
    for (const row of train.X) for (let j = 0; j < d; j++) mu[j] += row[j];
    for (let j = 0; j < d; j++) mu[j] /= train.X.length;
    for (const row of train.X) for (let j = 0; j < d; j++) sd[j] += (row[j] - mu[j]) ** 2;
    for (let j = 0; j < d; j++) sd[j] = Math.sqrt(sd[j] / train.X.length) + 1e-9;
    const A = train.X.map((row) => row.map((v, j) => (v - mu[j]) / sd[j]));
    const K = Math.min(this.KNN, A.length);
    return Xte.map((row) => {
      const z = row.map((v, j) => (v - mu[j]) / sd[j]);
      const best = new Float64Array(K).fill(Infinity), lab = new Float64Array(K);
      for (let a = 0; a < A.length; a++) {
        let s = 0;
        for (let j = 0; j < z.length; j++) { const t = z[j] - A[a][j]; s += t * t; if (s > best[K - 1]) break; }
        if (s >= best[K - 1]) continue;
        let p = K - 1;
        while (p > 0 && best[p - 1] > s) { best[p] = best[p - 1]; lab[p] = lab[p - 1]; p--; }
        best[p] = s; lab[p] = train.y[a];
      }
      let s = 0;
      for (let i = 0; i < K; i++) s += lab[i];
      return s / K;
    });
  },
  roc(sc, y) {
    const idx = sc.map((v, i) => i).sort((a, b) => sc[b] - sc[a]);
    const P = y.reduce((a, b) => a + b, 0), Nn = y.length - P;
    const pts = [[0, 0]];
    let tp = 0, fp = 0, auc = 0, prevF = 0;
    for (const i of idx) {
      if (y[i]) tp++; else { fp++; auc += tp; }
      pts.push([fp / Nn, tp / P]);
    }
    void prevF;
    return { pts, auc: auc / (P * Nn) };
  },
  recAt(pts, f) {
    let best = 0;
    for (const [x, t] of pts) if (x <= f) best = Math.max(best, t);
    return best;
  },
  calc(api) {
    const p = api.p;
    const key = [p.nreal, p.nsyn, p.flat, p.miss, p.sevlo].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    if (!this._te) {
      const te = this.set(this.NTEST, 99, { flat: 0, miss: 0, lo: 0.08 });
      this._te = te;
    }
    const te = this._te;
    const nreal = Math.round(p.nreal);
    if (!this._re || this._re.n !== nreal) {            // 只用真实图的那条线只随真实图数量变，缓存下来
      const set = this.set(nreal, 1234, { flat: 0, miss: 0, lo: 0.08 });
      this._re = { n: nreal, set, roc: this.roc(this.score(set, te.X), te.y) };
    }
    const real = this._re.set;
    const nsyn = Math.round(p.nsyn);
    const skey = [nsyn, p.flat, p.miss, p.sevlo].join(",");
    if (!this._syn || this._syn.key !== skey) {
      this._syn = { key: skey, val: nsyn ? this.set(nsyn, 777, { flat: p.flat > 0.5, miss: p.miss > 0.5, lo: p.sevlo }) : { X: [], y: [], k: [] } };
    }
    const syn = this._syn.val;
    const mix = { X: real.X.concat(syn.X), y: real.y.concat(syn.y) };
    const s2 = this.score(mix, te.X);
    const r1 = this._re.roc, r2 = this.roc(s2, te.y);
    const per = [1, 2, 3].map((kk) => {
      const sel = te.y.map((_, i) => te.k[i] === 0 || te.k[i] === kk);
      const sub = s2.filter((_, i) => sel[i]), lab = te.k.filter((_, i) => sel[i]).map((v) => (v === kk ? 1 : 0));
      return this.recAt(this.roc(sub, lab).pts, 0.05);
    });
    const val = { r1, r2, per, rec1: this.recAt(r1.pts, 0.05), rec2: this.recAt(r2.pts, 0.05), nsyn };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; this._syn = null; this._re = null; },
  readouts(api, s) {
    const p = api.p, c = this.calc(api);
    if (api.scene === "mix" && p.nsyn <= 0 && p.nreal >= 50 && p.nreal <= 70) api.done("base");
    if (api.scene === "mix" && p.nsyn >= 700 && p.nsyn <= 900 && p.flat < 0.5 && p.miss < 0.5) api.done("add");
    if (api.scene === "mix" && p.nsyn >= 1100 && p.flat < 0.5 && p.miss < 0.5) api.done("plateau");
    if (api.scene === "bias" && p.nsyn >= 400 && p.flat > 0.5) api.done("flatbg");
    if (api.scene === "bias" && p.nsyn >= 400 && p.flat > 0.5 && p.miss > 0.5) api.done("missing");
    const names = [["划痕", "scratch"], ["压痕", "dent"], ["锈斑", "rust"]];
    return [[["只用真实图：曲线下面积", "real only: AUC"], c.r1.auc.toFixed(3)],
            [["掺了合成图：曲线下面积", "with synthetic: AUC"], c.r2.auc.toFixed(3)],
            [["只用真实图：误报 5% 处查出", "real only: recall at 5%"], (c.rec1 * 100).toFixed(1) + "%"],
            [["掺了合成图：误报 5% 处查出", "with synthetic: recall at 5%"], (c.rec2 * 100).toFixed(1) + "%"],
            [names[1], (c.per[1] * 100).toFixed(1) + "%"]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api);
    const x0 = 54, y0 = 22, pw = w - x0 - 150, ph = h - y0 - 44;
    const X = (v) => x0 + v * pw, Y = (v) => y0 + ph - v * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    for (let g = 0; g <= 1.0001; g += 0.25) {
      api.line(x0, Y(g), x0 + pw, Y(g), api.css("--grid"), 1);
      api.label((g * 100).toFixed(0) + "%", 12, Y(g) + 4, api.css("--muted"), 11);
      api.line(X(g), y0, X(g), y0 + ph, api.css("--grid"), 1);
      api.label((g * 100).toFixed(0) + "%", X(g) - 10, y0 + ph + 16, api.css("--muted"), 11);
    }
    api.line(X(0.05), y0, X(0.05), y0 + ph, api.css("--muted"), 1.4, [5, 4]);
    const curve = (pts, col, wd) => {
      let prev = null;
      for (const [fx, ty] of pts) { const cur = [X(fx), Y(ty)]; if (prev) api.line(prev[0], prev[1], cur[0], cur[1], col, wd); prev = cur; }
    };
    curve(c.r1.pts, api.css("--red"), 2.0);
    if (c.nsyn > 0) curve(c.r2.pts, api.css("--green"), 2.4);
    api.label(api.T("查出的缺陷比例", "defects caught"), 10, y0 + 12, api.css("--muted"), 12);
    api.label(api.T("误报率", "false-alarm rate"), x0 + pw / 2 - 26, h - 12, api.css("--muted"), 12);
    const bx = x0 + pw + 14;
    api.label(api.T("误报 5% 处", "at 5% false alarms"), bx, y0 + 14, api.css("--muted"), 12);
    api.label(api.T(`只用真实：${(c.rec1 * 100).toFixed(1)}%`, `real only: ${(c.rec1 * 100).toFixed(1)}%`), bx, y0 + 34, api.css("--red"), 13);
    if (c.nsyn > 0) {
      api.label(api.T(`掺合成：${(c.rec2 * 100).toFixed(1)}%`, `with synth: ${(c.rec2 * 100).toFixed(1)}%`), bx, y0 + 54,
                c.rec2 >= c.rec1 ? api.css("--green") : api.css("--red"), 13);
      api.label(api.T(c.rec2 >= c.rec1 ? "补对了" : "补了还不如不补", c.rec2 >= c.rec1 ? "it helped" : "worse than nothing"),
                bx, y0 + 76, api.css("--ink"), 12);
      const names = [api.T("划痕", "scratch"), api.T("压痕", "dent"), api.T("锈斑", "rust")];
      api.label(api.T("分类看（掺合成后）", "by class (with synthetic)"), bx, y0 + 108, api.css("--muted"), 12);
      c.per.forEach((v, i) => api.label(`${names[i]} ${(v * 100).toFixed(1)}%`, bx, y0 + 128 + i * 19, api.css("--ink"), 12));
    }
  },
});
