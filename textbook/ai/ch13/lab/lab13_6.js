// 实验 13.6 切片、召回与代价（配 13.6 节）。三个场景：
//   chunk ：改切片长度与重叠，看召回率与“每个问题送进模型多少词元”同时怎么变；
//   method：三种检索（词频、哈希向量、混合）在两种问法下的召回率；
//   ask   ：逐个问题看取回了哪几条、对不对，以及开同义词表与零件号加权之后的变化。
// 手册由程序按模板生成（与书中 code/_ch13.py 同一套规则，这里规模小一些以便实时重算），
// 不需要联网，也不下载任何模型。向量检索用的是**没有语义**的哈希向量，所以它在口语问法上更差——
// 这正是 13.6 节的结论：向量检索的本事来自模型，不来自“向量”这个形式。
WQ.lab({
  title: ["实验 13.6 切片、召回与代价", "Lab 13.6 Chunking, recall and cost"],
  goal: ["在一份几百条的质量手册上做检索：改切片长度、重叠、取回条数与检索方式，看召回率与代价怎样此消彼长，以及问法一换会掉多少。",
         "Retrieve from a few-hundred-clause quality manual: change the chunk length, overlap, number of chunks and retrieval method, and watch recall trade off against cost — and how far recall falls when the question is reworded."],
  scenes: [
    { id: "chunk", name: ["切片与代价", "Chunking and cost"],
      problem: { title: ["问题：切多长", "Problem: how long a chunk"],
                 text: ["切得短，一条条文可能被切断，编号和数值分到两片里；切得长，召回上去了，但每个问题送进模型的词元数也跟着涨——而钱和延迟都按词元算。",
                        "Short chunks split a clause, separating its number from its value. Long chunks recall better but send far more tokens per question — and both price and latency are per token."] } },
    { id: "method", name: ["三种检索", "Three methods"],
      problem: { title: ["问题：按词还是按向量", "Problem: words or vectors"],
                 text: ["按词频检索（BM25）要求问法与手册用词对得上；这里的向量是没有语义的哈希向量，对不上的问法它也救不了。真正能救的是：一张同义词表、把零件号当作过滤条件，以及一个训练过的句向量模型（那要显卡，见 GPU 实验 13.6）。",
                        "BM25 needs the wording to match the manual. The vectors here are hashed, not semantic, so they cannot bridge a paraphrase. What does help: a synonym list, filtering by part number, and a trained embedding model (which needs a GPU — see GPU lab 13.6)."] } },
    { id: "ask", name: ["逐个问题看", "Question by question"],
      problem: { title: ["问题：错在哪一条", "Problem: which clause came back"],
                 text: ["手册里有几百条字面几乎一样、只是零件号与数值不同的条文。问“301 的同轴度”，取回“308 的同轴度”——分数很高，答案全错。所以要看的不是平均召回率，而是每个问题取回了哪几条。",
                        "The manual holds hundreds of near-identical clauses differing only in part number and value. Ask about part 301 and get part 308: a high score and a wrong answer. Look at which clauses came back, not just the average recall."] } },
  ],
  params: [
    { id: "size", name: ["切片长度（字）", "Chunk length (chars)"], min: 100, max: 1000, step: 50, value: 300, digits: 0 },
    { id: "overlap", name: ["重叠（字）", "Overlap (chars)"], min: 0, max: 300, step: 20, value: 60, digits: 0 },
    { id: "k", name: ["取回几片", "Chunks retrieved"], min: 1, max: 20, step: 1, value: 5, digits: 0 },
    { id: "method", name: ["检索（0 词频 · 1 向量 · 2 混合）", "Method (0 BM25 · 1 vector · 2 hybrid)"], min: 0, max: 2, step: 1, value: 0, digits: 0 },
    { id: "style", name: ["问法（0 手册原词 · 1 工人口语）", "Wording (0 manual · 1 shop floor)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "syn", name: ["同义词表（0 关 · 1 开）", "Synonym list (0 off · 1 on)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "part", name: ["零件号加权（0 关 · 1 开）", "Part-number boost (0 off · 1 on)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "qi", name: ["看第几个问题（“逐个问题看”场景）", "Question index (in the last scene)"], min: 1, max: 10, step: 1, value: 1, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["召回率", "recall"] }, { color: "var(--red)", name: ["词元数（代价）", "tokens (cost)"] },
           { color: "var(--green)", name: ["取回且正确", "retrieved and correct"] }],
  tasks: [
    { id: "cost", text: ["把切片长度从 300 加到 1000：召回率涨了几个点？每个问题的词元数涨了几倍？值不值？",
                         "Raise the chunk length from 300 to 1000: how many points does recall gain, and how many times do the tokens grow? Worth it?"],
      demo: { scene: "chunk", set: { size: 1000 }, press: [] } },
    { id: "reword", text: ["切片回到 300，把问法换成工人口语：召回率掉多少？再把检索换成向量，看是涨还是掉。",
                           "Back to 300, switch to shop-floor wording: how far does recall fall? Then switch to vectors — up or down?"],
      demo: { scene: "method", set: { size: 300, style: 1, method: 1 }, press: [] } },
    { id: "rescue", text: ["在口语问法下，把检索换成混合、再把同义词表与零件号加权都打开：召回率救回多少？",
                           "With shop-floor wording, switch to hybrid and turn on both the synonym list and the part-number boost: how much recall comes back?"],
      demo: { scene: "method", set: { style: 1, method: 2, syn: 1, part: 1 }, press: [] } },
    { id: "k", text: ["把取回条数从 5 加到 20：召回率还涨吗？词元数涨了几倍？（收益递减，代价不递减。）",
                      "Raise the number of chunks from 5 to 20: does recall still improve? How many times do the tokens grow? (Diminishing returns, undiminished cost.)"],
      demo: { scene: "chunk", set: { k: 20 }, press: [] } },
    { id: "wrong", text: ["到“逐个问题看”场景，关掉零件号加权，翻一遍 10 个问题：有没有取回了别的零件的同类条文？",
                          "In the last scene, turn off the part-number boost and page through the ten questions: did any return the same clause for a different part?"],
      demo: { scene: "ask", set: { k: 5, part: 0, style: 1, qi: 1 }, press: [] } },
  ],
  think: ["如果把整本手册直接塞进模型的上下文，召回率就是 100%，为什么大家还要做检索？",
          "Stuffing the whole manual into the context gives 100% recall — so why bother retrieving at all?"],

  // ---- 手册（与书中同一套模板，规模缩小以便实时重算）
  PARTS: [["SH-301 输出轴", 0.02, 28, 0.8], ["SH-302 输入轴", 0.03, 30, 1.6], ["GH-12 主动齿轮", 0.05, 45, 0.4],
          ["XT-5 箱体", 0.10, 0, 3.2], ["ZJ-108 中间轴", 0.04, 33, 1.6], ["CD-115 传动轴", 0.06, 26, 3.2],
          ["FL-121 法兰", 0.08, 0, 6.3], ["DG-133 端盖", 0.12, 0, 6.3], ["GT-140 隔套", 0.09, 0, 3.2],
          ["YG-152 压盖", 0.07, 0, 1.6]],
  PROC: [["粗车", "单边留量"], ["精车", "单边留量"], ["磨削", "单次进刀"], ["清洗与防锈", "清洗液浓度"]],
  GENERAL: [
    ["QM-3.1", "量具校准周期", "卡尺、千分尺与量规每 6 个月校准一次，校准记录由计量室保存 3 年；超期的量具不得用于终检。"],
    ["QM-3.2", "测量不确定度的要求", "终检所用量具的测量不确定度不得大于被测公差带的 10 分之一。"],
    ["QM-3.3", "三坐标测量机的使用", "三坐标测量机的测头每班次开机后做一次校验；测量间温度应控制在 20 ± 2 ℃。"],
    ["QM-4.1", "首件检验", "每批首件必须全尺寸检验并由检验员签字，首件未判合格不得继续加工。"],
    ["QM-5.1", "不合格品的标识与隔离", "发现不合格品应立即挂红牌并移入隔离区，24 小时内填写不合格品评审单。"],
    ["QM-5.2", "超差的判定与审批", "尺寸超差但不影响装配功能的，由质量工程师提出让步接收意见，经质量经理批准后方可放行；影响功能的一律报废。"],
    ["QM-5.3", "返工与返修", "返工后的零件须按原检验项目重新全检，并注明返工次数；同一零件返工不得超过 2 次。"],
    ["QM-6.1", "检验记录的保存", "检验记录与不合格品评审单保存 5 年；电子记录每 7 天备份一次。"],
    ["QM-7.1", "检验员的资格", "检验员须经培训考核合格并取得授权，授权有效期 3 年，到期重新考核。"],
    ["QM-7.2", "签字权限", "让步接收单由质量经理签字；报废单由厂长签字，金额超过 5000 元的另报总经理。"],
  ],
  QUESTIONS: [
    { gold: ["QM-P1-tol"], q: "SH-301 输出轴的同轴度公差是多少？", q2: "301 这个轴，两头转起来晃动卡多少？" },
    { gold: ["QM-P1-hrc"], q: "SH-301 输出轴调质后的硬度范围？", q2: "301 轴热处理完要多硬？" },
    { gold: ["QM-P2-tol"], q: "SH-302 输入轴的同轴度公差呢？", q2: "302 那根轴晃动允许多少？" },
    { gold: ["QM-3.1"], q: "量具多久校准一次？记录保存几年？", q2: "卡尺千分尺多久送一次检？单子留多久？" },
    { gold: ["QM-3.2"], q: "终检用的量具精度要求是怎么规定的？", q2: "量最后一道的尺子要多准才算行？" },
    { gold: ["QM-5.2", "QM-7.2"], q: "超差了谁批？让步接收单谁签字？", q2: "超了还能不能用？那张单子谁签？" },
    { gold: ["QM-5.3"], q: "同一个零件最多返工几次？", q2: "一个件能来回修几遍？" },
    { gold: ["QM-6.1"], q: "检验记录要保存几年？多久备份？", q2: "检验单子存几年？电脑里的多久备份一回？" },
    { gold: ["QM-7.1"], q: "检验员的授权有效期多长？", q2: "检验的本子几年过期？" },
    { gold: ["QM-P3-ra"], q: "GH-12 主动齿轮配合面的粗糙度要求？", q2: "12 那个齿轮配合面要多光？" },
  ],
  SYN: { "晃动": "同轴度", "晃": "同轴度", "多硬": "硬度", "热处理完": "调质", "尺子": "量具", "卡尺": "量具",
         "千分尺": "量具", "送一次检": "校准", "多准": "测量不确定度", "多光": "表面粗糙度", "光洁度": "表面粗糙度",
         "超了": "超差", "单子": "记录", "本子": "授权", "过期": "有效期", "来回修": "返工", "能用": "让步接收" },

  // 车间里还有几十种别的零件，条文字面几乎一样、只是编号与数值不同——手册因此有几百条，检索要在其中挑出问到的那一条
  allParts() {
    if (this._parts) return this._parts;
    const kinds = ["中间轴", "传动轴", "法兰", "端盖", "隔套", "压盖", "齿圈", "拨叉", "连杆", "衬套"];
    const pre = ["ZJ", "CD", "FL", "DG", "GT", "YG", "CQ", "BC", "LG", "CT"];
    const out = this.PARTS.slice();
    for (let i = 0; i < 60; i++) {
      const k = i % kinds.length;
      const tol = +(0.01 + 0.19 * ((i * 37) % 23) / 22).toFixed(2);
      const hrc = (i % 3 === 0) ? 0 : 20 + ((i * 13) % 28);
      const ra = [0.4, 0.8, 1.6, 3.2, 6.3][(i * 7) % 5];
      out.push([`${pre[k]}-${200 + i} ${kinds[k]}`, tol, hrc, ra]);
    }
    this._parts = out;
    return out;
  },
  manual() {
    if (this._man) return this._man;
    const rows = this.GENERAL.map(([id, t, b]) => ({ id, title: t, text: b }));
    this.allParts().forEach(([name, tol, hrc, ra], i) => {
      const n = i + 1;
      rows.push({ id: `QM-P${n}-tol`, title: `${name}的同轴度要求`,
                  text: `${name}两端轴颈对公共基准的同轴度公差为 ${tol} mm；超差的零件按 QM-5.2 条处理。` });
      if (hrc) {
        rows.push({ id: `QM-P${n}-hrc`, title: `${name}的热处理硬度`,
                    text: `${name}调质后表面硬度应为 ${hrc}—${hrc + 4} HRC；每炉抽检 3 件。` });
      }
      rows.push({ id: `QM-P${n}-ra`, title: `${name}的表面粗糙度`,
                  text: `${name}配合面的表面粗糙度 Ra 不大于 ${ra} μm，非配合面不大于 ${Math.max(ra * 4, 3.2)} μm。` });
      this.PROC.forEach(([proc, what], j) => {
        rows.push({ id: `QM-P${n}-${j}`, title: `${name} 的${proc}工艺要求`,
                    text: `${name} ${proc}工序：${what} ${(0.05 + 0.37 * ((i * 7 + j * 3) % 7)).toFixed(2)} mm，` +
                          `转速 ${120 + ((i * 53 + j * 31) % 700)} r/min；加工后按本章检验项目自检一次。` });
      });
    });
    this._man = rows;
    return rows;
  },
  chunks(p) {
    const key = [p.size, p.overlap].join(",");
    if (this._ch && this._ch.key === key) return this._ch.val;
    const man = this.manual();
    let text = "", spans = [];
    for (const c of man) {
      const piece = `${c.id} ${c.title}。${c.text}\n`;
      spans.push([text.length, text.length + piece.length, c.id]);
      text += piece;
    }
    const step = Math.max(1, p.size - p.overlap), out = [];
    for (let i = 0; i < Math.max(1, text.length - p.overlap); i += step) {
      const piece = text.slice(i, i + p.size);
      if (piece.length < p.size / 3 && out.length) break;
      const srcs = spans.filter(([a, b]) => a < i + piece.length && b > i).map(([, , id]) => id);
      out.push({ text: piece, srcs });
    }
    const val = out;
    this._ch = { key, val };
    return val;
  },
  // ---- 分词（中文按字与字二元组）、BM25 与哈希向量
  tokens(s) {
    const out = [];
    const ascii = s.match(/[A-Za-z0-9][A-Za-z0-9.\-/]*/g) || [];
    for (const a of ascii) out.push(a.toLowerCase());
    const han = s.match(/[一-鿿]/g) || [];
    for (const h of han) out.push(h);
    for (let i = 0; i + 1 < han.length; i++) out.push(han[i] + han[i + 1]);
    return out;
  },
  index(docs) {
    if (this._ix && this._ix.docs === docs) return this._ix.val;
    const post = new Map(), lens = new Float64Array(docs.length);
    docs.forEach((d, i) => {
      const t = this.tokens(d.text);
      lens[i] = t.length;
      for (const w of t) {
        let m = post.get(w);
        if (!m) { m = new Map(); post.set(w, m); }
        m.set(i, (m.get(i) || 0) + 1);
      }
    });
    let sum = 0;
    for (const x of lens) sum += x;
    const val = { post, lens, avg: Math.max(sum / docs.length, 1e-9), n: docs.length };
    this._ix = { docs, val };
    return val;
  },
  bm25(query, docs) {
    const idx = this.index(docs), s = new Float64Array(docs.length);
    const k1 = 1.5, b = 0.75;
    for (const w of new Set(this.tokens(query))) {
      const pl = idx.post.get(w);
      if (!pl) continue;
      const iw = Math.log(1 + (idx.n - pl.size + 0.5) / (pl.size + 0.5));
      for (const [i, f] of pl) s[i] += iw * f * (k1 + 1) / (f + k1 * (1 - b + b * idx.lens[i] / idx.avg));
    }
    return s;
  },
  hash(w) {                                                    // 一个便宜的 32 位哈希（FNV 变体）
    let h = 2166136261;
    for (let i = 0; i < w.length; i++) { h ^= w.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  },
  embed(text, dim) {
    const v = new Float64Array(dim);
    for (const w of this.tokens(text)) { const h = this.hash(w); v[h % dim] += (h & 1) ? 1 : -1; }
    let n = 0;
    for (const x of v) n += x * x;
    n = Math.sqrt(n) || 1;
    for (let i = 0; i < dim; i++) v[i] /= n;
    return v;
  },
  vecScores(query, docs) {
    const DIM = 256;
    if (!this._emb || this._emb.docs !== docs) {
      this._emb = { docs, M: docs.map((d) => this.embed(d.text, DIM)) };
    }
    const q = this.embed(query, DIM);
    return this._emb.M.map((m) => { let s = 0; for (let i = 0; i < DIM; i++) s += m[i] * q[i]; return s; });
  },
  expand(q) {
    const extra = [];
    for (const k in this.SYN) if (q.includes(k) && !extra.includes(this.SYN[k])) extra.push(this.SYN[k]);
    return extra.length ? q + "（" + extra.join(" ") + "）" : q;
  },
  hints(q) {
    const m = q.match(/[A-Za-z]{2}-?\d{2,4}|\b\d{2,4}\b/g) || [];
    return m.map((x) => x.toUpperCase().replace("-", ""));
  },
  retrieve(query, docs, p) {
    const q = p.syn ? this.expand(query) : query;
    let s;
    if (p.method === 0) s = this.bm25(q, docs);
    else if (p.method === 1) s = this.vecScores(q, docs);
    else {
      const a = this.bm25(q, docs), b = this.vecScores(q, docs);
      let ma = 1e-9, mb = 1e-9;
      for (const x of a) ma = Math.max(ma, x);
      for (const x of b) mb = Math.max(mb, x);
      s = Array.from(a, (x, i) => 0.5 * x / ma + 0.5 * b[i] / mb);
    }
    s = Array.from(s);
    if (p.part) {
      const hs = this.hints(q);
      if (hs.length) {
        s = s.map((x, i) => {
          const flat = docs[i].text.toUpperCase().replace(/-/g, "");
          return hs.some((h) => flat.includes(h)) ? x * 2 : x;
        });
      }
    }
    return s.map((x, i) => [x, i]).sort((u, v2) => v2[0] - u[0]).slice(0, p.k).map(([, i]) => i);
  },
  evaluate(p) {
    const key = [p.size, p.overlap, p.k, p.method, p.style, p.syn, p.part].join(",");
    if (this._ev && this._ev.key === key) return this._ev.val;
    const ch = this.chunks(p);
    let rec = 0;
    const rows = this.QUESTIONS.map((q) => {
      const query = p.style ? q.q2 : q.q;
      const idx = this.retrieve(query, ch, p);
      const got = new Set();
      for (const i of idx) for (const c of ch[i].srcs) got.add(c);
      const hitN = q.gold.filter((g) => got.has(g)).length;
      rec += hitN / q.gold.length;
      return { query, idx, gold: q.gold, recall: hitN / q.gold.length,
               srcs: idx.map((i) => ch[i].srcs[0] || "") };
    });
    const val = { chunks: ch.length, rows, recall: 100 * rec / this.QUESTIONS.length,
                  tok: p.k * p.size / 1.5 + 200 };
    this._ev = { key, val };
    return val;
  },
  reset(api, s) {},
  readouts(api, s) {
    const p = api.p, e = this.evaluate(p);
    if (p.size >= 1000) api.done("cost");
    if (p.style === 1 && p.method === 1) api.done("reword");
    if (p.style === 1 && p.method === 2 && p.syn === 1 && p.part === 1) api.done("rescue");
    if (p.k >= 20) api.done("k");
    if (api.scene === "ask" && p.part === 0 && p.style === 1) api.done("wrong");
    const PRICE = 2.0;                                          // 美元/百万词元（与书中同一个假设）
    return [[["手册条文 / 切片数", "clauses / chunks"], this.manual().length + " / " + e.chunks],
            [["召回率（10 个问题平均）", "recall (10 questions)"], api.fmt(e.recall, 0) + "%"],
            [["每个问题的词元数", "tokens per question"], api.fmt(e.tok, 0)],
            [["一千个问题的检索上下文费用", "context cost per 1000 questions"], "$" + api.fmt(e.tok * 1000 / 1e6 * PRICE, 2)],
            [["整本手册塞进上下文要", "whole manual in context"], api.fmt(this.manual().reduce((a, c) => a + c.text.length + c.title.length, 0) / 1.5, 0) + api.T(" 词元", " tokens")],
            [["当前问题取回的条文", "clauses returned for this question"], e.rows[Math.min(p.qi, 10) - 1].srcs.join(" ")]];
  },
  draw(api, s) {
    const { w, h } = api, m = 44, p = api.p, e = this.evaluate(p);
    if (api.scene === "chunk") {
      // 召回率与词元数随切片长度变化（当前点标出来）
      const sizes = [100, 200, 300, 500, 700, 1000];
      const pts = sizes.map((sz) => {
        const ev = this.evaluate({ ...p, size: sz, overlap: Math.min(p.overlap, sz - 50) });
        return [sz, ev.recall, ev.tok];
      });
      const maxTok = Math.max(...pts.map((x) => x[2]));
      const X = (sz) => m + (sz - 100) / 900 * (w - 2 * m);
      const Y1 = (r) => h * 0.55 - r / 100 * (h * 0.40);
      const Y2 = (t) => h - m - t / maxTok * (h * 0.30);
      api.label(api.T("召回率（%）", "recall (%)"), m, 18, api.css("--blue"), 12);
      api.label(api.T("每个问题的词元数", "tokens per question"), m, h * 0.60, api.css("--red"), 12);
      for (let i = 1; i < pts.length; i++) {
        api.line(X(pts[i - 1][0]), Y1(pts[i - 1][1]), X(pts[i][0]), Y1(pts[i][1]), api.css("--blue"), 2);
        api.line(X(pts[i - 1][0]), Y2(pts[i - 1][2]), X(pts[i][0]), Y2(pts[i][2]), api.css("--red"), 2);
      }
      for (const [sz, r, t] of pts) {
        api.rect(X(sz) - 3, Y1(r) - 3, 6, 6, api.css("--blue"));
        api.rect(X(sz) - 3, Y2(t) - 3, 6, 6, api.css("--red"));
        api.label(String(sz), X(sz) - 10, h - 12, api.css("--muted"), 10);
      }
      api.line(X(p.size), 24, X(p.size), h - m, api.css("--ink"), 1.2);
      return;
    }
    if (api.scene === "method") {
      // 三种检索 × 两种问法
      const names = [api.T("词频", "BM25"), api.T("哈希向量", "vectors"), api.T("混合", "hybrid")];
      const bw = (w - 2 * m) / 3;
      for (let mi = 0; mi < 3; mi++) {
        for (let st = 0; st < 2; st++) {
          const ev = this.evaluate({ ...p, method: mi, style: st });
          const x0 = m + mi * bw + (st ? bw * 0.52 : bw * 0.10);
          const hh = ev.recall / 100 * (h - 2 * m - 30);
          api.rect(x0, h - m - hh, bw * 0.36, hh, st ? api.css("--red") : api.css("--blue"));
          api.label(api.fmt(ev.recall, 0) + "%", x0 + 2, h - m - hh - 6, api.css("--ink"), 11);
        }
        api.label(names[mi], m + mi * bw + bw * 0.22, h - m + 16, api.css("--muted"), 12);
      }
      api.label(api.T("蓝＝按手册原词问　红＝工人口语问", "blue = manual wording, red = shop-floor wording"),
                m, 20, api.css("--muted"), 11);
      return;
    }
    // ask：当前问题取回的片子，命中的标绿
    const row = e.rows[Math.min(p.qi, 10) - 1];
    api.label(row.query, m, 24, api.css("--ink"), 13);
    api.label(api.T("标准答案：", "gold: ") + row.gold.join(" "), m, 46, api.css("--muted"), 12);
    const ch = this.chunks(p);
    row.idx.forEach((i, r) => {
      const ok = ch[i].srcs.some((c) => row.gold.includes(c));
      const y = 72 + r * Math.min(34, (h - 110) / Math.max(row.idx.length, 1));
      api.rect(m, y - 10, 10, 10, ok ? api.css("--green") : api.css("--muted"));
      api.label((ch[i].srcs[0] || "") + "  " + ch[i].text.slice(0, 44).replace(/\n/g, " "),
                m + 18, y, ok ? api.css("--green") : api.css("--ink"), 11);
    });
  },
});
