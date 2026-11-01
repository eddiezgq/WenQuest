// 实验 17.7 产线日报智能体：工具出毛病时哪一道检查挡得住（配 17.7 节）。
// 两个场景：
//   data   ：看三条线这 28 天的产量，标准答案是算得出来的；
//   agent  ：给工具加上一种毛病，再一道一道打开检查，看日报的结论对不对。
// 三种毛病都不报错，但都会让日报给出一个确信无疑的错结论。
// 与 code/_ch17.py 是同一套数据与同一套检查。
WQ.lab({
  title: ["实验 17.7 日报智能体：哪一道检查挡得住", "Lab 17.7 The daily-report agent: which check catches what"],
  goal: ["给取数工具加上三种真实会遇到的毛病，再一道一道打开检查，看日报的结论从错变对。做完能回答两个问题：一个不报错的工具能把结论带偏到什么程度，以及为什么单开一道检查挡不住全部。",
         "Introduce three realistic faults into the data-reading tool, then switch the checks on one at a time and watch the report's conclusion go from wrong to right. How far can a silently faulty tool push the answer, and why is one check never enough?"],
  scenes: [
    { id: "data", name: ["数据与标准答案", "The data and the ground truth"],
      problem: { title: ["问题：昨天哪条线掉产能了", "Problem: which line lost output"],
                 text: ["三条线、28 天的产量。车间工程师每天早上要回答同一个问题：最近一周比上一周，哪条线掉得最狠、掉了多少。这件事数据里有定论，所以日报的结论对不对是能判的——这正是做这个实验的前提。二号线从第 25 天起悄悄掉了产能。",
                        "Three lines, 28 days of output. Every morning the question is the same: compared with the week before, which line dropped the most, and by how much? The data settles it, so the report's conclusion can be judged right or wrong — which is what makes this lab possible. Line 2 quietly degrades from day 25."] } },
    { id: "agent", name: ["工具出毛病时", "When a tool misbehaves"],
      problem: { title: ["问题：工具不报错，但数是错的", "Problem: the tool does not fail, it just returns the wrong data"],
                 text: ["三种毛病：时间窗口写错了（取成上一周）、分页没翻完（只取回四天）、一条线的数来自另一个系统（单位是箱不是件）。三种都**不报错**，智能体照样把日报写得斩钉截铁。三道检查：查取回来的天数够不够、查量级对不对、换一个口径交叉核对。",
                        "Three faults: the wrong time window (last week instead of this one), an unfinished pagination (only four days came back), and one line whose numbers come from another system in boxes rather than pieces. None of them raises an error, and the agent writes the report just as confidently. Three checks are available: the number of days, the magnitude, and a cross-check against a second source."] } },
  ],
  params: [
    { id: "fault", name: ["工具的毛病（0 无 1 取成上周 2 只取四天 3 单位是箱）", "fault (0 none, 1 stale, 2 partial, 3 boxes)"], min: 0, max: 3, step: 1, value: 0, digits: 0 },
    { id: "clen", name: ["检查一：取回来够几天（0 关 1 开）", "check 1: enough days (0 off, 1 on)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "crng", name: ["检查二：量级对不对（0 关 1 开）", "check 2: magnitude (0 off, 1 on)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "ccross", name: ["检查三：换口径交叉核对（0 关 1 开）", "check 3: cross-check (0 off, 1 on)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "seed", name: ["换一批数据", "another batch of data"], min: 0, max: 19, step: 1, value: 0, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["一号线", "line 1"] },
           { color: "var(--red)", name: ["二号线", "line 2"] },
           { color: "var(--green)", name: ["三号线", "line 3"] }],
  tasks: [
    { id: "truth", text: ["在“数据与标准答案”里看一眼：标准答案是哪条线、掉了百分之几？二号线是从第几天开始掉的？",
                          "In the data scene: which line is the right answer and by how much, and from which day does line 2 start to drop?"],
      demo: { scene: "data", set: { fault: 0, seed: 0 }, press: [] } },
    { id: "stale", text: ["切到“工具出毛病时”，毛病设成 1（取成上周），三道检查全关：日报说哪条线？报警了吗？",
                          "Switch to the agent scene, set the fault to 1 (stale window) with all checks off: which line does the report name, and does it warn?"],
      demo: { scene: "agent", set: { fault: 1, clen: 0, crng: 0, ccross: 0 }, press: [] } },
    { id: "boxes", text: ["毛病设成 3（一条线的单位是箱），仍然全关：这一次的结论离谱到什么程度？",
                          "Set the fault to 3 (one line in boxes), still with all checks off: how far off is the conclusion this time?"],
      demo: { scene: "agent", set: { fault: 3, clen: 0, crng: 0, ccross: 0 }, press: [] } },
    { id: "single", text: ["毛病留在 2（只取回四天），一道一道单独打开三个检查：哪一道挡得住它？另外两道为什么挡不住？",
                           "Keep the fault at 2 (partial data) and switch each check on by itself: which one catches it, and why do the other two miss?"],
      demo: { scene: "agent", set: { fault: 2, clen: 1, crng: 0, ccross: 0 }, press: [] } },
    { id: "all", text: ["三道全开，把毛病从 0 过到 3：每一种都挡住了吗？一切正常时会不会误报？",
                        "Turn all three on and step the fault from 0 to 3: are they all caught, and does the clean case raise a false alarm?"],
      demo: { scene: "agent", set: { fault: 3, clen: 1, crng: 1, ccross: 1 }, press: [] } },
  ],
  think: ["这三道检查都是事前想得到的。再想两种这个脚手架挡不住的毛病，说明为什么光加检查不够，还要配什么（提示：第 17.6 节讲的那道闸）。",
          "All three checks are things you could think of in advance. Name two faults this scaffold would still miss, and say what else is needed besides more checks (hint: the gate in Section 17.6)."],

  LINES: [["一号线", "line 1"], ["二号线", "line 2"], ["三号线", "line 3"]],
  DAYS: 28, BOX: 12,
  rng(seed) { let s = (seed >>> 0) || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; },
  nrm(r) { const u = Math.max(r(), 1e-12); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * r()); },
  expo(r, mean) { return -mean * Math.log(Math.max(r(), 1e-12)); },
  build(seed) {
    const r = this.rng(2400 + seed), out = [];
    for (let li = 0; li < 3; li++) {
      const base = 480 + 40 * li, rate = [], down = [], output = [];
      for (let d = 0; d < this.DAYS; d++) {
        let ra = base + 12 * this.nrm(r);
        let dn = Math.min(300, this.expo(r, 18) + this.expo(r, 18));
        if (li === 1 && d >= 24) { ra *= 0.80; dn += 45; }
        rate.push(ra); down.push(dn); output.push(Math.round(ra * (1 - dn / 1440)));
      }
      out.push({ rate, down, output });
    }
    return out;
  },
  mean(a) { return a.reduce((x, y) => x + y, 0) / a.length; },
  truth(d) {
    const drop = d.map((v) => {
      const a = this.mean(v.output.slice(-7)), b = this.mean(v.output.slice(-14, -7));
      return (a - b) / b * 100;
    });
    let w = 0;
    for (let i = 1; i < 3; i++) if (drop[i] < drop[w]) w = i;
    return { drop, worst: w, worstDrop: drop[w] };
  },
  pull(d, li, fault) {
    const o = d[li].output;
    if (fault === 1) return o.slice(-14, -7);
    if (fault === 2) return o.slice(-7).slice(0, 4);
    if (fault === 3 && li === 0) return o.slice(-7).map((x) => x / this.BOX);
    return o.slice(-7);
  },
  report(d, fault, ck) {
    let warn = 0;
    let drop = d.map((v, li) => {
      let a = this.pull(d, li, fault);
      const b = this.mean(v.output.slice(-14, -7));
      if (ck.len && a.length !== 7) { warn++; a = v.output.slice(-7); }
      if (ck.rng) { const ratio = this.mean(a) / b; if (!(ratio > 0.2 && ratio < 5)) { warn++; a = v.output.slice(-7); } }
      return (this.mean(a) - b) / b * 100;
    });
    if (ck.cross) {
      const alt = d.map((v) => {
        const a = this.mean(v.rate.slice(-7)), b = this.mean(v.rate.slice(-14, -7));
        return (a - b) / b * 100;
      });
      let w1 = 0, w2 = 0;
      for (let i = 1; i < 3; i++) { if (drop[i] < drop[w1]) w1 = i; if (alt[i] < alt[w2]) w2 = i; }
      if (w1 !== w2) { warn++; drop = alt; }
    }
    let w = 0;
    for (let i = 1; i < 3; i++) if (drop[i] < drop[w]) w = i;
    return { drop, worst: w, worstDrop: drop[w], warn };
  },
  calc(api) {
    const q = api.p, key = [q.fault, q.clen, q.crng, q.ccross, q.seed].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const d = this.build(Math.round(q.seed));
    const tru = this.truth(d);
    const ck = { len: q.clen > 0.5, rng: q.crng > 0.5, cross: q.ccross > 0.5 };
    const rep = this.report(d, Math.round(q.fault), ck);
    const ok = rep.worst === tru.worst && Math.abs(rep.worstDrop - tru.worstDrop) < 2;
    const val = { d, tru, rep, ok };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const q = api.p, c = this.calc(api);
    if (api.scene === "data") api.done("truth");
    if (api.scene === "agent" && q.fault === 1 && q.clen + q.crng + q.ccross === 0) api.done("stale");
    if (api.scene === "agent" && q.fault === 3 && q.clen + q.crng + q.ccross === 0) api.done("boxes");
    if (api.scene === "agent" && q.fault === 2 && q.clen > 0.5 && q.crng < 0.5 && q.ccross < 0.5) api.done("single");
    if (api.scene === "agent" && q.fault === 3 && q.clen > 0.5 && q.crng > 0.5 && q.ccross > 0.5) api.done("all");
    const L = (i) => api.T(this.LINES[i][0], this.LINES[i][1]);
    if (api.scene === "data") {
      return [[["标准答案：掉得最狠的", "ground truth: worst line"], L(c.tru.worst)],
              [["掉了多少", "by how much"], c.tru.worstDrop.toFixed(1) + "%"],
              [["一号线", "line 1"], c.tru.drop[0].toFixed(1) + "%"],
              [["二号线", "line 2"], c.tru.drop[1].toFixed(1) + "%"],
              [["三号线", "line 3"], c.tru.drop[2].toFixed(1) + "%"]];
    }
    return [[["日报说：掉得最狠的", "the report says"], L(c.rep.worst)],
            [["日报说掉了多少", "by how much it says"], c.rep.worstDrop.toFixed(1) + "%"],
            [["标准答案", "ground truth"], L(c.tru.worst) + " " + c.tru.worstDrop.toFixed(1) + "%"],
            [["结论对不对", "is the conclusion right"], c.ok ? api.T("对", "right") : api.T("错", "wrong")],
            [["这一轮报了几个警", "warnings raised"], String(c.rep.warn)]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api);
    const x0 = 56, y0 = 22, pw = w - x0 - 160, ph = h - y0 - 44;
    const cols = [api.css("--blue"), api.css("--red"), api.css("--green")];
    let lo = Infinity, hi = -Infinity;
    c.d.forEach((v) => v.output.forEach((o) => { lo = Math.min(lo, o); hi = Math.max(hi, o); }));
    lo = Math.floor(lo * 0.95); hi = Math.ceil(hi * 1.03);
    const X = (d) => x0 + d / (this.DAYS - 1) * pw, Y = (v) => y0 + ph - (v - lo) / (hi - lo) * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    // 最近一周与前一周
    api.rect(X(this.DAYS - 7), y0, X(this.DAYS - 1) - X(this.DAYS - 7), ph, "rgba(184,134,11,0.10)", null, 0);
    api.rect(X(this.DAYS - 14), y0, X(this.DAYS - 7) - X(this.DAYS - 14), ph, "rgba(122,134,141,0.08)", null, 0);
    api.label(api.T("前 7 天", "previous 7"), X(this.DAYS - 11.5) - 18, y0 + 14, api.css("--muted"), 11);
    api.label(api.T("最近 7 天", "last 7"), X(this.DAYS - 4.5) - 18, y0 + 14, api.css("--accent"), 11);
    for (let g = 0; g <= 4; g++) {
      const v = lo + (hi - lo) * g / 4;
      api.line(x0, Y(v), x0 + pw, Y(v), api.css("--grid"), 1);
      api.label(v.toFixed(0), 14, Y(v) + 4, api.css("--muted"), 11);
    }
    c.d.forEach((v, li) => {
      let prev = null;
      v.output.forEach((o, d) => {
        const cur = [X(d), Y(o)];
        if (prev) api.line(prev[0], prev[1], cur[0], cur[1], cols[li], 2.0);
        prev = cur;
      });
    });
    api.line(X(24), y0, X(24), y0 + ph, api.css("--red"), 1.4, [4, 4]);
    api.label(api.T("第 25 天", "day 25"), X(24) - 20, y0 + ph - 6, api.css("--red"), 11);
    api.label(api.T("当日产量（件）", "daily output"), 10, y0 + 12, api.css("--muted"), 12);
    api.label(api.T("第几天", "day"), x0 + pw / 2 - 16, h - 12, api.css("--muted"), 12);

    const bx = x0 + pw + 12;
    const L = (i) => api.T(this.LINES[i][0], this.LINES[i][1]);
    if (api.scene === "data") {
      api.label(api.T("标准答案", "ground truth"), bx, y0 + 16, api.css("--ink"), 13);
      c.tru.drop.forEach((v, i) => api.label(`${L(i)} ${v >= 0 ? "+" : ""}${v.toFixed(1)}%`,
                                             bx, y0 + 40 + i * 20,
                                             i === c.tru.worst ? api.css("--red") : api.css("--muted"), 12));
      return;
    }
    api.label(api.T("日报的结论", "the report"), bx, y0 + 16, api.css("--ink"), 13);
    api.label(`${L(c.rep.worst)} ${c.rep.worstDrop.toFixed(1)}%`, bx, y0 + 40,
              c.ok ? api.css("--green") : api.css("--red"), 14);
    api.label(api.T(c.ok ? "对" : "错", c.ok ? "right" : "wrong"), bx, y0 + 62,
              c.ok ? api.css("--green") : api.css("--red"), 13);
    api.label(api.T(`报警 ${c.rep.warn} 个`, `${c.rep.warn} warning(s)`), bx, y0 + 86, api.css("--muted"), 12);
    if (!c.ok && c.rep.warn === 0) {
      api.label(api.T("错了，而且一个警都没报", "wrong, and it said nothing"), bx, y0 + 110, api.css("--red"), 12);
    }
    api.label(api.T("标准答案", "ground truth"), bx, y0 + 140, api.css("--muted"), 12);
    api.label(`${L(c.tru.worst)} ${c.tru.worstDrop.toFixed(1)}%`, bx, y0 + 162, api.css("--muted"), 12);
  },
});
