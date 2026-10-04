// 实验 7.5 哪些检测记录是多余的（配 7.5.4 节）。减速器试验台的六次试验，五个频率处的振动幅值（教学编制的理想数据，见 code/_rec.py）：
// 试验 1–3 各一种激励，试验 4–6 是叠加。选一条目标记录，拖动其余记录的系数去凑它；“程序判断”用消元求秩与极大无关组。
WQ.lab({
  title: ["实验 7.5 哪些检测记录是多余的", "Lab 7.5 Which inspection records are redundant?"],
  goal: ["用其余记录的线性组合去凑一条目标记录，判断它是否多余；用消元求出六条记录的秩和一个极大无关组。",
         "Combine the other records to rebuild a target record and decide whether it is redundant; find the rank and a maximal independent set of the six records by elimination."],
  scenes: [
    { id: "rec", robot: true, name: ["减速器振动记录", "Reducer vibration records"],
      problem: { title: ["机器人问题：六条记录里有几条真正不同？", "Robot problem: how many of the six records really differ?"],
                 text: ["关节减速器在试验台上做了六次试验，每次记录 1×、2×、啮合、轴承、高频五个频率处的振动幅值。在线性范围内振动按叠加原理相加，几种激励同时存在时的记录可能是单一激励记录之和。",
                        "A joint reducer was run six times on the test bench; each run records the vibration amplitude at five frequencies. In the linear range vibrations add, so a run with several excitations may be the sum of single-excitation runs."] } },
  ],
  params: [
    { id: "k", name: ["目标记录", "Target record"], min: 1, max: 6, step: 1, value: 4, digits: 0 },
    { id: "c1", name: ["记录 1 的系数", "Coefficient of record 1"], min: -2, max: 2, step: 0.5, value: 0, digits: 1 },
    { id: "c2", name: ["记录 2 的系数", "Coefficient of record 2"], min: -2, max: 2, step: 0.5, value: 0, digits: 1 },
    { id: "c3", name: ["记录 3 的系数", "Coefficient of record 3"], min: -2, max: 2, step: 0.5, value: 0, digits: 1 },
    { id: "c4", name: ["记录 4 的系数", "Coefficient of record 4"], min: -2, max: 2, step: 0.5, value: 0, digits: 1 },
    { id: "c5", name: ["记录 5 的系数", "Coefficient of record 5"], min: -2, max: 2, step: 0.5, value: 0, digits: 1 },
    { id: "c6", name: ["记录 6 的系数", "Coefficient of record 6"], min: -2, max: 2, step: 0.5, value: 0, digits: 1 },
  ],
  buttons: [{ id: "solve", name: ["程序判断", "Let the program decide"], primary: true }, { id: "zero", name: ["系数清零", "Clear coefficients"] }],
  tasks: [
    { id: "r4", robot: true, text: ["用其余记录凑出记录 4（剩余全为零）。", "Rebuild record 4 from the others (zero remainder)."],
      demo: { scene: "rec", set: { k: 4, c1: 1, c2: 1, c3: 0, c5: 0, c6: 0 }, press: [] } },
    { id: "r6", robot: true, text: ["用其余记录凑出记录 6。", "Rebuild record 6 from the others."],
      demo: { scene: "rec", set: { k: 6, c1: 1, c2: 1, c3: 1, c4: 0, c5: 0 }, press: [] } },
    { id: "r1", robot: true, text: ["用其余记录凑出记录 1：“多余”是相对的。", "Rebuild record 1 from the others: redundancy is relative."],
      demo: { scene: "rec", set: { k: 1, c2: -1, c3: 0, c4: 1, c5: 0, c6: 0 }, press: [] } },
    { id: "rank", text: ["点“程序判断”，把程序给出的秩和极大无关组与你凑出的结果比较。", "Press 'Let the program decide' and compare its rank and maximal independent set with what you found by hand."],
      demo: { scene: "rec", set: {}, press: ["solve"] } },
  ],
  think: ["实际测量有噪声，记录 4 不会恰好等于记录 1 与 2 之和。程序还会说秩是 3 吗？应当怎样判断“几乎多余”？",
          "Real measurements are noisy, so record 4 will not equal records 1 + 2 exactly. Would the program still report rank 3? How should 'almost redundant' be judged?"],

  R: [[4, 1, 0, 0, 1], [0, 2, 3, 1, 0], [1, 0, 0, 3, 2], [4, 3, 3, 1, 1], [1, 2, 3, 4, 2], [5, 3, 3, 4, 3]],
  freqs: [["1×", "1×"], ["2×", "2×"], ["啮合", "mesh"], ["轴承", "bearing"], ["高频", "high"]],
  mem: null,
  solve(id) {
    if (id !== "solve") return;
    const M = this.R[0].map((_, i) => this.R.map((r) => r[i])), m = 5, n = 6, A = M.map((r) => r.slice()), piv = [];
    let row = 0;
    for (let c = 0; c < n && row < m; c++) {
      let p = -1; for (let i = row; i < m; i++) if (Math.abs(A[i][c]) > 1e-12) { p = i; break; }
      if (p < 0) continue;
      [A[row], A[p]] = [A[p], A[row]];
      const d = A[row][c]; A[row] = A[row].map((x) => x / d);
      for (let i = 0; i < m; i++) if (i !== row) { const f = A[i][c]; A[i] = A[i].map((x, j) => x - f * A[row][j]); }
      piv.push(c); row++;
    }
    this.mem = { piv, R: A };
  },
  action(id, api) {
    if (id === "zero") { this.mem = null; ["c1", "c2", "c3", "c4", "c5", "c6"].forEach((k) => { const el = api.canvas.closest("section").querySelector(`[data-param="${k}"]`); if (el) { el.value = 0; el.dispatchEvent(new Event("input")); } }); return; }
    this.solve(id);
  },
  combo(api) {
    const k = api.p.k - 1, c = [api.p.c1, api.p.c2, api.p.c3, api.p.c4, api.p.c5, api.p.c6];
    const sum = [0, 0, 0, 0, 0].map((_, f) => this.R.reduce((s, r, j) => s + (j === k ? 0 : c[j] * r[f]), 0));
    const res = this.R[k].map((x, f) => x - sum[f]);
    return { k, c, sum, res, err: Math.max(...res.map(Math.abs)) };
  },
  readouts(api) {
    const { k, c, sum, res, err } = this.combo(api);
    const used = c.some((x, j) => j !== k && x !== 0);
    if (err < 1e-9 && used && k === 3) api.done("r4");
    if (err < 1e-9 && used && k === 5) api.done("r6");
    if (err < 1e-9 && used && k === 0) api.done("r1");
    if (this.mem) api.done("rank");
    const terms = c.map((x, j) => (j === k || x === 0 ? null : `${api.fmt(x, 1)}·r${j + 1}`)).filter(Boolean).join(" + ") || "0";
    const rows = [[["目标记录", "Target"], "r" + (k + 1) + " = " + api.la.vstr(this.R[k], 0)],
                  [["组合", "Combination"], terms],
                  [["组合的结果", "Its value"], api.la.vstr(sum, 1)],
                  [["剩余 = 目标 − 组合", "Remainder = target − combination"], api.la.vstr(res, 1)],
                  [["结论", "Verdict"], err < 1e-9 && used ? api.T("凑出来了：记录 " + (k + 1) + " 可由其余记录线性表示", "rebuilt: record " + (k + 1) + " is a combination of the others") : api.T("还没有凑出来", "not yet")]];
    if (this.mem) {
      rows.push([["程序：秩", "Program: rank"], String(this.mem.piv.length)],
                [["程序：极大无关组（主元列）", "Program: maximal independent set (pivot columns)"], this.mem.piv.map((j) => "r" + (j + 1)).join(", ")]);
    }
    return rows;
  },
  draw(api) {
    const { w, h } = api, { k, sum, res } = this.combo(api), muted = api.css("--muted");
    const x0 = 50, x1 = w - 20, y0 = 30, y1 = h - 50, bw = (x1 - x0) / 5;
    const all = [...this.R[k], ...sum, ...res], top = Math.max(6, ...all), bot = Math.min(-2, ...all);
    const Y = (v) => y1 - (y1 - y0) * (v - bot) / (top - bot);
    api.line(x0, Y(0), x1, Y(0), muted, 1);
    [bot, 0, top].forEach((v) => api.label(api.fmt(v, 0), x0 - 8, Y(v) + 4, muted, 11, "right"));
    this.freqs.forEach((f, i) => {
      const cx = x0 + bw * (i + 0.5), bar = (v, dx, col) => { const a = Y(Math.max(v, 0)), b = Y(Math.min(v, 0)); api.rect(cx + dx, a, bw * 0.22, Math.max(1, b - a), col); };
      bar(this.R[k][i], -bw * 0.36, api.css("--blue"));
      bar(sum[i], -bw * 0.11, api.css("--amber"));
      bar(res[i], bw * 0.14, Math.abs(res[i]) < 1e-9 ? api.css("--green") : api.css("--red"));
      api.label(api.T(f[0], f[1]), cx, y1 + 18, muted, 12, "center");
    });
    api.label(api.T("蓝：目标记录  黄：其余记录的组合  红/绿：剩余（全绿即凑出）", "blue: target  yellow: combination  red/green: remainder (all green = rebuilt)"), x0, 18, muted, 12);
  },
});
