// 实验 18.2 接触信息值多少（配 18.2 节）。
// 两个场景：
//   space ：把链长从 8 拖到 14，看折法的数目怎么涨；
//   clue  ：给 k 条正确的接触、w 条错的，看还剩多少种折法、基态还在不在。
// 全部在浏览器里现枚举现算（链长不超过 14，二十几万条走法，瞬时出结果）。
// 与 code/_ch18.py 是同一套算法。
WQ.lab({
  title: ["实验 18.2 接触信息值多少", "Lab 18.2 What a contact restraint is worth"],
  goal: ["亲手把一条链的所有折法枚举一遍，再一条条加上“已知接触”，看搜索空间怎样被砍掉。做完能回答三个问题：为什么“全都试一遍”行不通、一条正确的接触值多少、一条错的接触有多贵。",
         "Enumerate every way a chain can fold, then add known contacts one at a time and watch the search space collapse. You should be able to say why enumeration is hopeless, what one correct contact is worth, and what one wrong contact costs."],
  scenes: [
    { id: "space", name: ["折法有多少种", "How many ways to fold"],
      problem: { title: ["问题：为什么不能全都试一遍", "Problem: why enumeration is hopeless"],
                 text: ["把一条链放在二维方格上，每一步往上下左右走一格、不能走回已经占过的格子。这样的走法叫“自回避走”，每一条就是一种折法。链长每多两个残基，折法的数目就乘好几倍。真蛋白是三维的、几百个残基，所以“全都试一遍”从一开始就不是办法。",
                        "Put the chain on a square lattice: each step goes up, down, left or right and may not revisit a cell. Each such self-avoiding walk is one way to fold. Add two residues and the count multiplies several times over. A real protein is three-dimensional and hundreds of residues long, so enumeration was never an option."] } },
    { id: "clue", name: ["给几条接触", "Give it some contacts"],
      problem: { title: ["问题：接触信息能买回多少", "Problem: what contacts buy"],
                 text: ["共进化分析能告诉我们“这两个残基大概挨着”。把这样的接触当成约束加进来，只保留满足全部约束的折法。每加一条正确的接触，还剩的折法就少一个量级。但要当心最后一个旋钮：加一条**错**的接触，正确答案会被直接排除在外——剩下的折法再少也没用了。",
                        "Co-evolution tells us that two residues are probably in contact. Treat that as a restraint and keep only the folds that satisfy all of them: each correct contact removes about an order of magnitude. Watch the last control, though: one wrong contact removes the right answer altogether, and no amount of further narrowing brings it back."] } },
  ],
  params: [
    { id: "n", name: ["链有多长（残基）", "chain length (residues)"], min: 8, max: 13, step: 1, value: 12, digits: 0 },
    { id: "k", name: ["给几条正确的接触", "correct contacts given"], min: 0, max: 6, step: 1, value: 0, digits: 0 },
    { id: "w", name: ["其中混进几条错的", "wrong contacts mixed in"], min: 0, max: 3, step: 1, value: 0, digits: 0 },
    { id: "seed", name: ["换一组接触", "another set of contacts"], min: 0, max: 20, step: 1, value: 0, digits: 0 },
  ],
  legend: [{ color: "var(--muted)", name: ["全部折法", "all folds"] },
           { color: "var(--blue)", name: ["满足约束的折法", "folds satisfying the restraints"] },
           { color: "var(--green)", name: ["基态（能量最低）", "ground state"] },
           { color: "var(--red)", name: ["基态被排除了", "ground state excluded"] }],
  tasks: [
    { id: "grow", text: ["把链长从 8 一路拖到 13：折法的数目涨了多少倍？每多一个残基大约乘几？",
                         "Drag the chain length from 8 to 13: how many times more folds are there, and roughly what factor does each extra residue cost?"],
      demo: { scene: "space", set: { n: 13 }, press: [] } },
    { id: "one", text: ["链长 12、切到“给几条接触”，把正确接触从 0 加到 1：还剩的折法少了多少？",
                        "At length 12, switch to the restraints scene and go from 0 to 1 correct contact: how much of the search space is gone?"],
      demo: { scene: "clue", set: { n: 12, k: 1, w: 0 }, press: [] } },
    { id: "four", text: ["继续加到 4 条正确接触：还剩几种折法？其中基态占多大比例？",
                         "Keep going to four correct contacts: how many folds are left, and what share of them is the ground state?"],
      demo: { scene: "clue", set: { n: 12, k: 4, w: 0 }, press: [] } },
    { id: "wrong", text: ["保持 4 条，把“混进几条错的”调到 1：还剩多少种？基态还在不在？再按“换一组接触”试三次，看结论稳不稳。",
                          "Keep four and set the wrong-contact count to 1: how many are left, and is the ground state still among them? Change the contact set three times and see whether the answer holds."],
      demo: { scene: "clue", set: { n: 12, k: 4, w: 1 }, press: [] } },
    { id: "rescue", text: ["错一条之后，把正确接触加到 6：多给正确的接触能不能把基态救回来？这件事说明什么？",
                           "With one wrong contact still in, raise the correct ones to 6: can more correct restraints bring the ground state back? What does that tell you?"],
      demo: { scene: "clue", set: { n: 12, k: 6, w: 1 }, press: [] } },
  ],
  think: ["真实方法拿到的接触不是“对”或“错”两种，而是带着一个分数。如果让你用这个分数，你会怎样把“可能是错的那一条”造成的损失降下来？写出一条具体的规则，并说明它的代价。",
          "Real methods get contacts with a score attached, not a clean right/wrong label. How would you use that score to limit the damage from a possibly wrong contact? Write down a concrete rule and say what it costs."],

  SEQS: { 8: "HPHPPHPH", 9: "HPHPPHPHH", 10: "HPHPPHPHPH", 11: "HPHPHHPHPPH",
          12: "HPHPHHPHPPHH", 13: "HPHPHHPHPPHHP" },
  MOVES: [[1, 0], [-1, 0], [0, 1], [0, -1]],

  enumerate(n) {
    const out = [], seen = new Map();
    seen.set("0,0", true); seen.set("1,0", true);
    const path = [[0, 0], [1, 0]];
    const rec = () => {
      if (path.length === n) { out.push(path.map((p) => [p[0], p[1]])); return; }
      const [x, y] = path[path.length - 1];
      for (const [dx, dy] of this.MOVES) {
        const key = (x + dx) + "," + (y + dy);
        if (seen.get(key)) continue;
        seen.set(key, true); path.push([x + dx, y + dy]);
        rec();
        path.pop(); seen.set(key, false);
      }
    };
    rec();
    return out;
  },
  contacts(path) {
    const pos = new Map();
    path.forEach((p, i) => pos.set(p[0] + "," + p[1], i));
    const out = [];
    path.forEach((p, i) => {
      for (const [dx, dy] of [[1, 0], [0, 1]]) {
        const j = pos.get((p[0] + dx) + "," + (p[1] + dy));
        if (j !== undefined && Math.abs(j - i) > 1) out.push([Math.min(i, j), Math.max(i, j)]);
      }
    });
    return out;
  },
  energy(path, seq) {
    return -this.contacts(path).filter(([i, j]) => seq[i] === "H" && seq[j] === "H").length;
  },
  minOf(a) { let m = Infinity; for (const v of a) if (v < m) m = v; return m; },
  rng(seed) { let s = seed * 2654435761 + 12345; return () => { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }; },

  build(n) {
    this._cache = this._cache || new Map();     // 每个链长只枚举一次，拖滑块不会重算
    if (this._cache.has(n)) return this._cache.get(n);
    const seq = this.SEQS[n];
    const folds = this.enumerate(n);
    const cs = folds.map((f) => this.contacts(f).map((p) => p[0] + "-" + p[1]));
    const es = folds.map((f) => this.energy(f, seq));
    const lo = this.minOf(es);
    const natIdx = es.indexOf(lo);
    const b = { n, seq, folds, cs, es, lo, natIdx, nat: cs[natIdx] };
    this._cache.set(n, b);
    return b;
  },
  calc(api) {
    const q = api.p, n = Math.round(q.n), k = Math.round(q.k), w = Math.round(q.w), sd = Math.round(q.seed);
    const key = [n, k, w, sd].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const b = this.build(n);
    const r = this.rng(sd + 1);
    // k 条正确接触（按种子打乱后取前 k 条）
    const nat = b.nat.slice();
    for (let i = nat.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [nat[i], nat[j]] = [nat[j], nat[i]]; }
    const known = nat.slice(0, Math.min(k, nat.length));
    // w 条错的：在不是真接触的对里挑，优先挑“留下折法最多”的那种——它最不容易被发现
    const all = [];
    for (let i = 0; i < n; i++) for (let j = i + 2; j < n; j++) all.push(i + "-" + j);
    const fake = all.filter((p) => b.nat.indexOf(p) < 0);
    for (let t = 0; t < w; t++) known.push(fake[Math.floor(r() * fake.length)]);
    const keep = [];
    for (let i = 0; i < b.folds.length; i++) {
      let ok = true;
      for (const p of known) if (b.cs[i].indexOf(p) < 0) { ok = false; break; }
      if (ok) keep.push(i);
    }
    const bestE = keep.length ? this.minOf(keep.map((i) => b.es[i])) : null;
    const nNat = keep.filter((i) => b.es[i] === b.lo).length;
    const val = { b, n, k, w, known, keep, bestE, nNat,
                  total: b.folds.length, hasNative: nNat > 0 };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const c = this.calc(api), q = api.p;
    if (api.scene === "space" && q.n >= 13) api.done("grow");
    if (api.scene === "clue" && c.k >= 1 && c.w === 0) api.done("one");
    if (api.scene === "clue" && c.k >= 4 && c.w === 0) api.done("four");
    if (api.scene === "clue" && c.k >= 4 && c.w >= 1) api.done("wrong");
    if (api.scene === "clue" && c.k >= 6 && c.w >= 1) api.done("rescue");
    if (api.scene === "space") {
      const prev = this.build(Math.max(8, c.n - 1));
      return [[["这条链有多少种折法", "ways this chain can fold"], c.total.toLocaleString()],
              [["比短一个残基时多几倍", "times more than one residue shorter"],
               (c.total / prev.folds.length).toFixed(2)],
              [["基态的能量（H—H 接触数的相反数）", "ground-state energy (minus the H–H contacts)"],
               String(c.b.lo)],
              [["能量最低的折法有几条", "how many folds reach it"],
               String(c.b.es.filter((e) => e === c.b.lo).length)]];
    }
    return [[["给了几条约束（其中错的）", "restraints given (wrong ones)"],
             `${c.known.length}（${c.w}）`],
            [["还剩多少种折法", "folds still allowed"], c.keep.length.toLocaleString()],
            [["占全部折法的", "share of all folds"],
             (c.keep.length / c.total * 100).toFixed(3) + "%"],
            [["剩下的里最低能量", "lowest energy among them"],
             c.bestE === null ? "—" : String(c.bestE)],
            [["基态还在不在", "is the ground state still there"],
             c.hasNative ? api.T(`在（${c.nNat} 条）`, `yes (${c.nNat})`) : api.T("不在了", "no")]];
  },
  drawFold(api, path, x, y, cell, col, hiPairs) {
    const xs = path.map((p) => p[0]), ys = path.map((p) => p[1]);
    const cx = (Math.min(...xs) + Math.max(...xs)) / 2, cy = (Math.min(...ys) + Math.max(...ys)) / 2;
    const P = (i) => [x + (path[i][0] - cx) * cell, y - (path[i][1] - cy) * cell];
    for (let i = 0; i + 1 < path.length; i++) {
      const a = P(i), b = P(i + 1);
      api.line(a[0], a[1], b[0], b[1], api.css("--grid"), 2);
    }
    (hiPairs || []).forEach((p) => {
      const [i, j] = p.split("-").map(Number);
      const a = P(i), b = P(j);
      api.line(a[0], a[1], b[0], b[1], api.css("--accent"), 2, [3, 3]);
    });
    const seq = this.SEQS[path.length];
    for (let i = 0; i < path.length; i++) {
      const a = P(i);
      api.circle(a[0], a[1], cell * 0.22, null, seq[i] === "H" ? col : api.css("--blue"));
    }
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api);
    if (api.scene === "space") {
      // 画几条随便挑的折法，外加基态
      const cols = 4, rows = 2, cw = (w - 40) / cols, ch = (h - 60) / rows;
      const picks = [];
      for (let t = 0; t < cols * rows - 1; t++) {
        picks.push(c.b.folds[Math.floor(c.total * (t + 1) / (cols * rows))]);
      }
      picks.push(c.b.folds[c.b.natIdx]);
      picks.forEach((f, t) => {
        const cx = 20 + cw * (t % cols) + cw / 2, cy = 34 + ch * Math.floor(t / cols) + ch / 2;
        const last = t === picks.length - 1;
        this.drawFold(api, f, cx, cy, Math.min(cw, ch) * 0.16,
                      last ? api.css("--green") : api.css("--muted"));
        if (last) api.label(api.T("基态", "ground state"), cx - 16, cy + ch * 0.42,
                            api.css("--green"), 12);
      });
      api.label(api.T(`${c.n} 个残基，一共 ${c.total.toLocaleString()} 种折法（这里只画了 8 条）`,
                      `${c.n} residues, ${c.total.toLocaleString()} folds in all (eight shown)`),
                20, 20, api.css("--ink"), 13);
      return;
    }
    // clue 场景：左边柱状图，右边画几条还剩的折法
    const x0 = 56, y0 = 30, pw = Math.min(330, w * 0.42), ph = h - y0 - 46;
    const maxLog = Math.log10(c.total);
    const bars = [];
    for (let kk = 0; kk <= 6; kk++) {
      const nat = c.b.nat.slice(0, Math.min(kk, c.b.nat.length));
      let cnt = 0;
      for (let i = 0; i < c.b.folds.length; i++) {
        let ok = true;
        for (const p of nat) if (c.b.cs[i].indexOf(p) < 0) { ok = false; break; }
        if (ok) cnt++;
      }
      bars.push(cnt);
    }
    const bw = pw / 7 * 0.68;
    bars.forEach((cnt, kk) => {
      const hgt = Math.max(2, ph * Math.log10(Math.max(cnt, 1.05)) / maxLog);
      const bx = x0 + pw * kk / 7 + (pw / 7 - bw) / 2;
      api.rect(bx, y0 + ph - hgt, bw, hgt, api.css(kk === c.k && c.w === 0 ? "--blue" : "--grid"));
      api.label(String(kk), bx + bw / 2 - 3, y0 + ph + 15, api.css("--muted"), 11);
      if (kk % 2 === 0) api.label(cnt.toLocaleString(), bx - 4, y0 + ph - hgt - 5, api.css("--muted"), 10);
    });
    api.label(api.T("给了几条正确的接触 →", "correct contacts given →"), x0, h - 12, api.css("--muted"), 12);
    api.label(api.T("还剩多少种折法（对数高度）", "folds left (log height)"), 10, y0 - 10, api.css("--muted"), 12);
    if (c.w > 0) {
      api.rect(x0 + pw * c.k / 7 + (pw / 7 - bw) / 2, y0 + ph - 6, bw, 6, api.css("--red"));
      api.label(api.T(`混进 ${c.w} 条错的：只剩 ${c.keep.length} 种`,
                      `${c.w} wrong: only ${c.keep.length} left`),
                x0, y0 - 10, api.css("--red"), 12);
    }
    const rx = x0 + pw + 26, rw = w - rx - 16;
    const show = c.keep.slice(0, 6);
    const cols = 3, cw = rw / cols, ch2 = (h - y0 - 40) / 2;
    show.forEach((idx, t) => {
      const cx = rx + cw * (t % cols) + cw / 2, cy = y0 + 14 + ch2 * Math.floor(t / cols) + ch2 / 2;
      const isNat = c.b.es[idx] === c.b.lo;
      this.drawFold(api, c.b.folds[idx], cx, cy, Math.min(cw, ch2) * 0.15,
                    isNat ? api.css("--green") : api.css("--muted"), c.known);
    });
    api.label(c.keep.length
      ? api.T(`满足全部约束的折法（画前 ${show.length} 条，绿点是基态，虚线是给的接触）`,
              `folds satisfying every restraint (first ${show.length}; green = ground state, dashed = the restraints)`)
      : api.T("一条折法都不剩——给的约束互相矛盾", "nothing satisfies all of them: the restraints contradict each other"),
      rx, y0 - 10, c.keep.length ? api.css("--muted") : api.css("--red"), 11.5);
    if (c.keep.length && !c.hasNative) {
      api.label(api.T("剩下的里一条基态都没有——正确答案被错接触排除了",
                      "none of them is the ground state: the wrong contact removed the right answer"),
                rx, h - 12, api.css("--red"), 12);
    }
  },
});
