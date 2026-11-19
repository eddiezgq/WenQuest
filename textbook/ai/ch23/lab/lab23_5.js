// 实验 23.5 两种加数据策略（配 23.6 节）。
// 两个场景：
//   budget ：固定标注预算，比两种策略的误差——随机加数据，还是按不确定性（杠杆值）挑数据；
//   target ：固定一个误差目标，比两种策略各要标多少条。
// 与 code/_ch23.py 是同一套算法（lane_obs、poly_features、true_steer、leverage 的口径）：
// 车道线在三个前视距离上的像素横坐标当观测，噪声加在**像素**上；标签是专家方向盘角；
// 验收口径是**难例与易例等权重**——换成按回传数据的自然分布算，结论会反。
WQ.lab({
  title: ["实验 23.5 同一笔标注预算，花在哪一批数据上",
          "Lab 23.5 One labelling budget: which data should it buy?"],
  goal: ["车队每天跑回来几万段数据，**绝大部分是你已经会的那一种**——直道、好天气、车在车道中间。预算有限，标哪一批？先在固定预算下比两种策略：随机抽一批，还是按杠杆值（模型对它越没把握越大）挑一批。你会看到挑数据的那条曲线一上来就压下去，而且标注集里难例的占比被富集了好几倍。再切到第二个场景，固定一个误差目标，看两种策略各要标多少条（算例里是 420 对 120）。最后一定要做一件事：把误差口径从“难例易例等权重”换成“按回传数据的自然分布”，看结论会不会反过来。",
         "A fleet returns tens of thousands of clips a day, and most of them are the kind the model already handles. With a limited budget, which batch do you label? First compare the two strategies at a fixed budget: a random batch, or the batch with the highest leverage (the model's own measure of what it is unsure about). The active curve drops immediately and its labelled set is several times richer in hard cases. Then fix an error target and read off how many labels each strategy needs. Finally switch the error convention from equal weighting to the natural distribution of returned data and watch the conclusion flip."],
  scenes: [
    { id: "budget", name: ["固定预算比误差", "Fixed budget, compare the error"],
      problem: { title: ["问题：预算一样，误差差多少", "Problem: same budget, how different is the error?"],
                 text: ["这个场景把标注预算交给你：同样标这么多条，随机加数据与按不确定性挑数据各能把误差压到多少。旁边两列更要紧——**标注集里难例占了多少**。杠杆值不需要有人告诉它“弯道是难例”，它自己就把那一片挑出来了；也正因如此，它会把预算都花在只占百分之几的那一片上。划不划算，要看你按哪个口径验收。",
                        "Here the budget is yours: with the same number of labels, how far does each strategy push the error down? The two columns beside it matter more — what share of the labelled set is hard cases. Leverage needs nobody to tell it that curves are hard; it finds them. And for the same reason it spends the whole budget on a few per cent of the data, which may or may not be a bargain depending on the convention you accept it under."] } },
    { id: "target", name: ["固定误差比预算", "Fixed error, compare the budget"],
      problem: { title: ["问题：要达到同一个误差，各要标多少条", "Problem: how many labels does each strategy need?"],
                 text: ["采购和排期要的不是曲线，是一个数：**要达到这个误差，得标多少条**。这个场景让你把误差目标定下来，再读两个数。目标定得松，两种策略差不多；目标一紧，差距就拉开——因为随机加数据的曲线早早就平了，再标多少条都压不下去，而它平在哪里是由池子里难例的比例决定的，不是由预算决定的。",
                        "Procurement does not want a curve, it wants a number: how many labels to reach this error. Set the target and read two numbers. A loose target makes the strategies look alike; a tight one pulls them apart, because the random curve flattens early and no budget pushes it further — where it flattens is set by the share of hard cases in the pool, not by the budget."] } },
  ],
  params: [
    { id: "budget", name: ["标注预算（条）", "labelling budget (clips)"], min: 60, max: 900, step: 60, value: 300, digits: 0 },
    { id: "hardfrac", name: ["难例在回传数据里的占比（%）", "share of hard cases in the pool (%)"], min: 2, max: 30, step: 1, value: 7, digits: 0 },
    { id: "thresh", name: ["挑数据的阈值（只在杠杆值最高的前 100−阈值 % 里挑）", "selection threshold (percentile)"], min: 0, max: 95, step: 5, value: 95, digits: 0 },
    { id: "target", name: ["误差目标（°）", "error target (deg)"], min: 0.6, max: 1.6, step: 0.05, value: 1, digits: 2 },
  ],
  legend: [{ color: "var(--blue)", name: ["随机加数据", "random batches"] },
           { color: "var(--red)", name: ["按不确定性挑数据", "picked by uncertainty"] },
           { color: "var(--amber)", name: ["标注集里难例的占比", "hard-case share of the labelled set"] },
           { color: "var(--green)", name: ["当前这一档（预算或误差目标）", "where you are now"] },
           { color: "var(--muted)", name: ["池子里难例的自然比例", "the pool's natural share"] }],
  tasks: [
    { id: "base", text: ["默认设置（难例占 7%、阈值 95）、预算 300 条：两种策略的误差各是多少？标注集里难例占比各是多少？差几倍？",
                         "With the defaults (7% hard cases, threshold 95) and a budget of 300: what is each strategy's error, what share of each labelled set is hard, and by what factor do they differ?"],
      demo: { scene: "budget", set: { budget: 300, hardfrac: 7, thresh: 95, target: 1 }, press: [] } },
    { id: "rich", text: ["把难例占比拖到 30%（回传数据里难例多得多）：两种策略的差距变大还是变小？为什么挑数据的价值跟着池子变？",
                         "Raise the hard-case share to 30%: does the gap between the strategies grow or shrink, and why does the value of active selection depend on the pool?"],
      demo: { scene: "budget", set: { hardfrac: 30, budget: 300, thresh: 95, target: 1 }, press: [] } },
    { id: "rare", text: ["把难例占比拖到 2%（难例极少）：随机加数据的误差变成多少？它平在哪里，是预算决定的还是池子决定的？",
                         "Drop the hard-case share to 2%: what does the random strategy's error become? Where it flattens — is that set by the budget or by the pool?"],
      demo: { scene: "budget", set: { hardfrac: 2, budget: 300, thresh: 95, target: 1 }, press: [] } },
    { id: "loose", text: ["难例占比回到 7%，把挑数据的阈值拖到 0（等于在整个池子里随机挑）：挑数据这条曲线变成什么样？这说明省下来的样本是靠什么省的？",
                          "Back at 7%, drag the selection threshold to 0, which is the same as picking at random from the whole pool: what happens to the active curve, and what does that say about where the saving comes from?"],
      demo: { scene: "budget", set: { thresh: 0, hardfrac: 7, budget: 300, target: 1 }, press: [] } },
    { id: "goal", text: ["切到第二个场景，阈值回到 95，把误差目标定在 1.00°：两种策略各要标多少条？省了百分之几？再把目标收紧到 0.80°，随机加数据还达得到吗？",
                         "In the second scene, with the threshold back at 95, set the target to 1.00°: how many labels does each strategy need, and what is the saving? Then tighten the target to 0.80° — can the random strategy still reach it?"],
      demo: { scene: "target", set: { target: 1, thresh: 95, hardfrac: 7, budget: 300 }, press: [] } },
  ],
  think: ["把你们自己回传数据里“难例”的定义写下来——是按什么判的（横向偏差超过多少、曲率超过多少、还是靠人工看）？再估一估它在回传数据里占多少。把这两个数代进本实验，挑数据还省得下来吗？如果“难例”这个词在你们那里还没有定义，那么**先定口径，再谈挑数据**——本实验里只要把误差口径从等权重换成自然分布，结论就反了。",
          "Write down your own definition of a hard case — by lateral error, by curvature, or by a human looking at it — and estimate its share of the returned data. Substitute both into this lab: does active selection still pay? If 'hard case' is not yet defined where you work, define the convention first: in this lab, simply switching the error convention from equal weighting to the natural distribution reverses the answer."],

  NPOOL: 2000, NTEST: 400, SEEDN: 60, BATCH: 60, NF: 10,
  CX: 960, F: 1200, PITCH: 0.04, HEIGHT: 1.42,
  XS: [8, 16, 28], PIXSIGMA: 1.6,
  KE: 0.16, KPSI: 0.95, KKAPPA: 1, LOOK: 12, RATIO: 15,
  rng(seed) { let x = (seed * 1103515245 + 12345) >>> 0; return () => { x = (x * 1103515245 + 12345) >>> 0; return x / 4294967296; }; },
  gauss(r) { const u = Math.max(r(), 1e-9), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  scene1(n, r, kmax, esig) {                   // 一段车道保持数据：横向偏差、航向偏差、曲率
    const e = [], psi = [], kap = [];
    for (let i = 0; i < n; i++) {
      const k = (r() * 2 - 1) * kmax;
      kap.push(k);
      e.push(this.gauss(r) * esig);
      psi.push(this.gauss(r) * 0.025 - 0.4 * k * this.LOOK);
    }
    return { e, psi, kap };
  },
  steer(sc, i) {                               // 专家方向盘角（deg）：本实验的真值
    const d = this.KE * sc.e[i] + this.KPSI * sc.psi[i]
            + this.KKAPPA * Math.atan(this.LOOK * sc.kap[i]);
    return d * 180 / Math.PI * this.RATIO / 10;
  },
  feat(sc, i, r) {                             // 观测 → 特征：三列像素的一次项与二次项
    const u = [];
    for (const X of this.XS) {
      const Y = sc.e[i] + sc.psi[i] * X + 0.5 * sc.kap[i] * X * X;
      // 小孔模型：横向位置折成像素横坐标（与 _ch23.ground_to_pixel 同一套）
      const sp = Math.sin(this.PITCH), cp = Math.cos(this.PITCH);
      const zc = X * cp + this.HEIGHT * sp;
      const px = this.CX + this.F * (-Y) / zc + this.PIXSIGMA * this.gauss(r);
      u.push((px - this.CX) / 100);
    }
    const f = [1, u[0], u[1], u[2]];
    for (let a = 0; a < 3; a++) for (let b = a; b < 3; b++) f.push(u[a] * u[b]);
    return f;
  },
  dataset(n, r, kmax, esig) {
    const sc = this.scene1(n, r, kmax, esig);
    const X = [], y = [];
    for (let i = 0; i < n; i++) { X.push(this.feat(sc, i, r)); y.push(this.steer(sc, i)); }
    return { X, y };
  },
  pool(hardfrac) {
    const key = String(hardfrac);
    if (this._p && this._p.key === key) return this._p.val;
    const r = this.rng(1301), n = this.NPOOL, nh = Math.round(n * hardfrac / 100);
    const easy = this.dataset(n - nh, r, 0.0004, 0.1);
    const hard = this.dataset(nh, r, 0.009, 1.1);
    const X = easy.X.concat(hard.X), y = easy.y.concat(hard.y);
    const isHard = easy.X.map(() => 0).concat(hard.X.map(() => 1));
    const idx = X.map((_, i) => i);
    for (let i = idx.length - 1; i > 0; i--) {  // 洗一遍：回传数据不会按难易排好队
      const j = Math.floor(r() * (i + 1));
      const t = idx[i]; idx[i] = idx[j]; idx[j] = t;
    }
    const val = { X: idx.map((i) => X[i]), y: idx.map((i) => y[i]), hard: idx.map((i) => isHard[i]) };
    this._p = { key, val };
    return val;
  },
  tests() {
    if (this._t) return this._t;
    const r = this.rng(617);
    this._t = { easy: this.dataset(this.NTEST, r, 0.0004, 0.1),
                hard: this.dataset(this.NTEST, r, 0.009, 1.1) };
    return this._t;
  },
  gram(X, idx, lam) {                          // XᵀX + λI 与 Xᵀy 要用的上三角部分
    const p = this.NF, A = [];
    for (let i = 0; i < p; i++) { A.push(new Array(p).fill(0)); A[i][i] = lam; }
    for (const k of idx) {
      const x = X[k];
      for (let i = 0; i < p; i++) for (let j = 0; j < p; j++) A[i][j] += x[i] * x[j];
    }
    return A;
  },
  solve(A, b) {                                // 高斯消元（部分选主元）
    const p = b.length, M = A.map((row, i) => row.concat([b[i]]));
    for (let c = 0; c < p; c++) {
      let piv = c;
      for (let i = c + 1; i < p; i++) if (Math.abs(M[i][c]) > Math.abs(M[piv][c])) piv = i;
      const t = M[c]; M[c] = M[piv]; M[piv] = t;
      const d = M[c][c] || 1e-12;
      for (let j = c; j <= p; j++) M[c][j] /= d;
      for (let i = 0; i < p; i++) {
        if (i === c) continue;
        const f = M[i][c];
        if (f === 0) continue;
        for (let j = c; j <= p; j++) M[i][j] -= f * M[c][j];
      }
    }
    return M.map((row) => row[p]);
  },
  inv(A) {
    const p = A.length, out = [];
    for (let c = 0; c < p; c++) {
      const e = new Array(p).fill(0);
      e[c] = 1;
      out.push(this.solve(A.map((row) => row.slice()), e));
    }
    const T = [];                              // out 是按列装的，转回来
    for (let i = 0; i < p; i++) { T.push([]); for (let j = 0; j < p; j++) T[i].push(out[j][i]); }
    return T;
  },
  fit(pool, idx) {
    const A = this.gram(pool.X, idx, 1e-3), b = new Array(this.NF).fill(0);
    for (const k of idx) { const x = pool.X[k]; for (let i = 0; i < this.NF; i++) b[i] += x[i] * pool.y[k]; }
    return this.solve(A, b);
  },
  rmse(set, w) {
    let s = 0;
    for (let i = 0; i < set.y.length; i++) {
      let p = 0;
      for (let j = 0; j < this.NF; j++) p += set.X[i][j] * w[j];
      s += (p - set.y[i]) ** 2;
    }
    return Math.sqrt(s / set.y.length);
  },
  lev(pool, rest, idx) {                       // 杠杆值 xᵀ(XᵀX+λI)⁻¹x：模型对它越没把握越大
    const Ai = this.inv(this.gram(pool.X, idx, 1e-3));
    return rest.map((k) => {
      const x = pool.X[k];
      let s = 0;
      for (let i = 0; i < this.NF; i++) {
        let t = 0;
        for (let j = 0; j < this.NF; j++) t += Ai[i][j] * x[j];
        s += x[i] * t;
      }
      return s;
    });
  },
  run(hardfrac, thresh, how, maxN) {
    const key = [hardfrac, thresh, how, maxN].join("|");
    this._r = this._r || {};
    if (this._r[key]) return this._r[key];
    const pool = this.pool(hardfrac), t = this.tests(), r = this.rng(how === "random" ? 404 : 909);
    let rest = pool.X.map((_, i) => i);
    const idx = [];
    for (let i = 0; i < this.SEEDN; i++) idx.push(rest.splice(Math.floor(r() * rest.length), 1)[0]);
    const curve = [];
    for (;;) {
      const w = this.fit(pool, idx);
      let nh = 0;
      for (const k of idx) nh += pool.hard[k];
      curve.push({ n: idx.length,
                   bal: Math.sqrt(0.5 * this.rmse(t.easy, w) ** 2 + 0.5 * this.rmse(t.hard, w) ** 2),
                   nat: Math.sqrt((1 - hardfrac / 100) * this.rmse(t.easy, w) ** 2
                                  + hardfrac / 100 * this.rmse(t.hard, w) ** 2),
                   easy: this.rmse(t.easy, w), hardErr: this.rmse(t.hard, w),
                   hardPct: nh / idx.length * 100 });
      if (idx.length >= maxN || rest.length < this.BATCH) break;
      let head = rest;
      if (how !== "random") {
        const lv = this.lev(pool, rest, idx);
        const order = rest.map((k, i) => [k, lv[i]]).sort((a, b) => b[1] - a[1]).map((p) => p[0]);
        const keep = Math.max(this.BATCH, Math.round(order.length * (100 - thresh) / 100));
        head = order.slice(0, keep);
      }
      const taken = [];
      const headSet = head.slice();
      for (let i = 0; i < this.BATCH; i++) taken.push(headSet.splice(Math.floor(r() * headSet.length), 1)[0]);
      for (const k of taken) { idx.push(k); rest = rest.filter((x) => x !== k); }
    }
    this._r[key] = curve;
    return curve;
  },
  at(curve, n) {
    let best = curve[0];
    for (const p of curve) if (Math.abs(p.n - n) < Math.abs(best.n - n)) best = p;
    return best;
  },
  needed(curve, target) {
    for (const p of curve) if (p.bal <= target) return p.n;
    return null;
  },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p, pool = this.pool(q.hardfrac);
    const maxN = api.scene === "target" ? 900 : q.budget;
    const rnd = this.run(q.hardfrac, q.thresh, "random", maxN);
    const act = this.run(q.hardfrac, q.thresh, "active", maxN);
    let natural = 0;
    for (const x of pool.hard) natural += x;
    natural = natural / pool.hard.length * 100;
    if (api.scene === "budget") {
      const a = this.at(rnd, q.budget), b = this.at(act, q.budget);
      if (Math.abs(q.budget - 300) <= 15) api.done("base");
      if (q.hardfrac >= 28) api.done("rich");
      if (q.hardfrac <= 3) api.done("rare");
      if (q.thresh <= 5) api.done("loose");
      return [[["标注预算", "labelling budget"], `${a.n}` + api.T(" 条", " clips")],
              [["随机加数据的误差", "error, random batches"], a.bal.toFixed(4) + "°"],
              [["按不确定性挑的误差", "error, picked by uncertainty"], b.bal.toFixed(4) + "°"],
              [["挑数据好几倍", "active is better by"], (a.bal / Math.max(b.bal, 1e-9)).toFixed(2) + api.T(" 倍", "×")],
              [["池子里难例的自然比例", "the pool's natural hard share"], natural.toFixed(1) + "%"],
              [["标注集里难例占比（随机）", "hard share of the labelled set (random)"], a.hardPct.toFixed(1) + "%"],
              [["标注集里难例占比（挑）", "hard share of the labelled set (active)"], b.hardPct.toFixed(1) + "%"],
              [["难例那一列的误差（随机 / 挑）", "error on hard cases (random / active)"],
               `${a.hardErr.toFixed(3)}° / ${b.hardErr.toFixed(3)}°`]];
    }
    const nr = this.needed(rnd, q.target), na = this.needed(act, q.target);
    if (Math.abs(q.target - 1) <= 0.03) api.done("goal");
    const last_r = rnd[rnd.length - 1], last_a = act[act.length - 1];
    return [[["误差目标（难例易例等权重）", "target (equal weighting)"], q.target.toFixed(2) + "°"],
            [["随机加数据要标", "labels needed, random"],
             nr === null ? api.T("900 条都没达到", "not reached within 900") : `${nr}` + api.T(" 条", " clips")],
            [["按不确定性挑要标", "labels needed, active"],
             na === null ? api.T("900 条都没达到", "not reached within 900") : `${na}` + api.T(" 条", " clips")],
            [["省了", "saving"],
             nr !== null && na !== null ? `${((1 - na / nr) * 100).toFixed(0)}%（${(nr / na).toFixed(1)}` + api.T(" 倍）", "×)")
                                        : api.T("没法比", "not comparable")],
            [["标满 900 条：随机 / 挑", "at 900 labels: random / active"],
             `${last_r.bal.toFixed(4)}° / ${last_a.bal.toFixed(4)}°`],
            [["换成自然分布口径：随机 / 挑", "under the natural convention: random / active"],
             `${last_r.nat.toFixed(4)}° / ${last_a.nat.toFixed(4)}°`],
            [["口径一换，挑数据", "under that convention, active is"],
             last_a.nat > last_r.nat
               ? api.T(`反而差 ${((last_a.nat / last_r.nat - 1) * 100).toFixed(0)}%`,
                       `worse by ${((last_a.nat / last_r.nat - 1) * 100).toFixed(0)}%`)
               : api.T(`仍好 ${((1 - last_a.nat / last_r.nat) * 100).toFixed(0)}%`,
                       `still better by ${((1 - last_a.nat / last_r.nat) * 100).toFixed(0)}%`)]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p;
    const maxN = api.scene === "target" ? 900 : Math.max(q.budget, 300);
    const rnd = this.run(q.hardfrac, q.thresh, "random", maxN);
    const act = this.run(q.hardfrac, q.thresh, "active", maxN);
    let ymax = 0;
    for (const p of rnd.concat(act)) ymax = Math.max(ymax, p.bal);
    const g = api.graph({ x: 56, y: 28, w: w - 108, h: (h - 96) * 0.56,
                          xmin: 0, xmax: maxN, ymin: 0, ymax: Math.min(4, ymax * 1.1),
                          xlabel: api.T("标注量（条）", "labels (clips)"),
                          ylabel: api.T("误差（°，难例易例等权重）", "error (deg, equal weighting)") }).axes();
    g.pts(rnd.map((p) => [p.n, p.bal]), api.css("--blue"), 2.6);
    g.pts(act.map((p) => [p.n, p.bal]), api.css("--red"), 2.6);
    if (api.scene === "target") {
      g.hline(q.target, api.css("--green"), []);
      const nr = this.needed(rnd, q.target), na = this.needed(act, q.target);
      if (nr !== null) g.vline(nr, api.css("--blue"));
      if (na !== null) g.vline(na, api.css("--red"));
    } else {
      g.vline(q.budget, api.css("--green"), []);
    }
    g.text(api.T("蓝：随机加数据　红：按不确定性挑　绿：当前这一档",
                 "blue: random, red: picked by uncertainty, green: where you are"),
           maxN * 0.02, Math.min(4, ymax * 1.1) * 0.95, api.css("--ink"), 12);

    const g2 = api.graph({ x: 56, y: 28 + (h - 96) * 0.66, w: w - 108, h: (h - 96) * 0.34,
                           xmin: 0, xmax: maxN, ymin: 0, ymax: 100,
                           xlabel: api.T("标注量（条）", "labels (clips)"),
                           ylabel: api.T("标注集里难例占比（%）", "hard share of the labelled set (%)") }).axes();
    g2.pts(rnd.map((p) => [p.n, p.hardPct]), api.css("--blue"), 2.4);
    g2.pts(act.map((p) => [p.n, p.hardPct]), api.css("--amber"), 2.6);
    g2.hline(q.hardfrac, api.css("--muted"));
    g2.text(api.T("蓝：随机抽到的难例比例（≈池子的自然比例）　黄：挑出来的　灰：池子的自然比例",
                  "blue: random (tracks the pool), amber: active, grey: the pool's natural share"),
            maxN * 0.02, 94, api.css("--ink"), 12);
  },
});
