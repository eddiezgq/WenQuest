// 实验 9.3 贝叶斯公式（配 9.3 节）。
// 走廊：20 格，第 2、6、7、15 格有反光标志（算例 9.3.2）。AGV 实际从第 6 格出发。
// “测量”：按 AGV 的真实位置和检测器性能随机产生“有/无”（固定种子），再用贝叶斯公式 (9.3.5) 更新各格概率；
// “前进”：AGV 实际走 0、1、2 格的概率为 slip、1 − 2slip、slip，各格概率按全概率公式 (9.3.6) 更新。
// 质检：1000 个齿轮的自然频数（算例 9.3.1），后验 = 报警且有缺陷 / 报警。
WQ.lab({
  title: ["实验 9.3 贝叶斯公式", "Lab 9.3 Bayes' rule"],
  goal: ["用贝叶斯公式根据带误差的测量更新概率，用全概率公式处理运动，体会先验、似然、后验的作用。",
         "Update probabilities from noisy measurements with Bayes' rule, handle motion with the law of total probability, and see what prior, likelihood and posterior do."],
  scenes: [
    { id: "aisle", robot: true, name: ["走廊里的 AGV", "AGV in an aisle"], hide: ["base"],
      problem: { title: ["机器人问题：AGV 重新上电后在哪一格", "Robot problem: which cell is the AGV in after a restart"],
                 text: ["车底的检测器经过反光标志时报“有”，但会漏报和误报。交替测量和前进，AGV 能认出自己的位置吗？",
                        "A detector under the AGV says “tag” over a reflector, but misses and false alarms happen. Can it find itself by measuring and moving?"] } },
    { id: "qc", name: ["质检报警", "Inspection alarm"], hide: ["slip"],
      problem: { title: ["生活中的例子：报警了，真有缺陷吗", "Everyday example: an alarm, but is the part bad?"],
                 text: ["缺陷很少见时，即使检测很准，报警的零件也多半是好的。",
                        "When defects are rare, most alarmed parts are good even with an accurate tester."] } },
  ],
  params: [
    { id: "hit", name: ["报“有”/报警的概率（在标志上 / 有缺陷时）", "P(“tag”/alarm | on a tag / defective)"], min: 0.5, max: 1, step: 0.01, value: 0.9, unit: "", digits: 2 },
    { id: "fa", name: ["误报的概率（不在标志上 / 无缺陷时）", "P(“tag”/alarm | off a tag / good)"], min: 0, max: 0.5, step: 0.01, value: 0.1, unit: "", digits: 2 },
    { id: "slip", name: ["走格误差：走 0 格、2 格的概率各为", "Slip: P(move 0) = P(move 2) ="], min: 0, max: 0.3, step: 0.01, value: 0.1, unit: "", digits: 2 },
    { id: "base", name: ["缺陷率（先验）", "Defect rate (prior)"], min: 0.001, max: 0.2, step: 0.001, value: 0.01, unit: "", digits: 3 },
  ],
  buttons: [{ id: "measure", name: ["测量", "Measure"], primary: true }, { id: "move", name: ["前进一格", "Move one cell"] }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "one", robot: true, text: ["从均匀的先验出发测量一次（读到“有”），四个标志格的概率之和超过 60%。", "From the uniform prior measure once (“tag”): the four tag cells together exceed 60%."],
      demo: { scene: "aisle", set: { hit: 0.9, fa: 0.1, slip: 0.1 }, press: ["reset", "measure"], wait: 1 } },
    { id: "found", robot: true, text: ["把检测器调准一些（报“有”0.95、误报 0.05、走格误差 0.05），交替测量和前进，直到 AGV 实际所在格的概率超过 0.8。", "With a better detector (0.95 hit, 0.05 false, 0.05 slip) alternate measuring and moving until the AGV's true cell exceeds 0.8."],
      demo: { scene: "aisle", set: { hit: 0.95, fa: 0.05, slip: 0.05 }, press: ["reset", "measure", "move", "measure", "move", "measure", "move", "measure", "move", "measure", "move", "measure", "move", "measure", "move", "measure", "move", "measure"], wait: 1 } },
    { id: "qc", text: ["质检：缺陷率 1%、检出率 0.95、误报率 0.05，读出报警齿轮真有缺陷的概率（约 16%）。", "Inspection: 1% defects, 0.95 detection, 0.05 false alarms; read the chance an alarmed gear is defective (about 16%)."],
      demo: { scene: "qc", set: { base: 0.01, hit: 0.95, fa: 0.05 }, press: [], wait: 1 } },
  ],
  think: ["算例 9.3.2 中第 6、7 格的标志紧挨着，这对 AGV 认出自己的位置有什么帮助？如果四个标志等间距排列，会怎样？",
          "In Example 9.3.2 the tags on cells 6 and 7 are adjacent. How does that help the AGV find itself? What if the four tags were evenly spaced?"],

  N: 20, TAGS: [2, 6, 7, 15],
  rnd(s) { s.seed = (s.seed * 1103515245 + 12345) % 2147483648; return s.seed / 2147483648; },
  isTag(i) { return this.TAGS.includes(i); },
  reset(api, s) { s.seed = 9031; s.x = 6; s.bel = new Array(this.N).fill(1 / this.N); s.log = []; s.nz = 0; s.lastZ = null; },
  action(a, api, s) {
    if (api.scene !== "aisle") return;
    const p = api.p, N = this.N;
    if (a === "measure") {
      const pr = this.isTag(s.x) ? p.hit : p.fa;
      const z = this.rnd(s) < pr ? 1 : 0;
      let tot = 0;
      s.bel = s.bel.map((b, i) => { const l = this.isTag(i) ? p.hit : p.fa; const v = (z ? l : 1 - l) * b; tot += v; return v; });
      s.bel = s.bel.map((b) => b / (tot || 1));
      s.nz += 1; s.lastZ = z; s.log.push(z ? api.T("有", "tag") : api.T("无", "none"));
    } else if (a === "move") {
      const u = this.rnd(s), k = u < p.slip ? 0 : u < 1 - p.slip ? 1 : 2;
      s.x = Math.min(N - 1, s.x + k);
      const nb = new Array(N).fill(0);
      s.bel.forEach((b, i) => { nb[Math.min(N - 1, i)] += p.slip * b; nb[Math.min(N - 1, i + 1)] += (1 - 2 * p.slip) * b; nb[Math.min(N - 1, i + 2)] += p.slip * b; });
      s.bel = nb; s.log.push(api.T("前进", "move"));
    }
  },
  readouts(api, s) {
    const p = api.p;
    if (api.scene === "qc") {
      const al = p.hit * p.base + p.fa * (1 - p.base), post = p.hit * p.base / al;
      if (Math.abs(p.base - 0.01) < 1e-6 && Math.abs(p.hit - 0.95) < 1e-6 && Math.abs(p.fa - 0.05) < 1e-6) api.done("qc");
      return [[["1000 个中有缺陷", "defective of 1000"], api.fmt(1000 * p.base, 1)],
              [["其中报警", "of which alarmed"], api.fmt(1000 * p.base * p.hit, 1)],
              [["无缺陷却报警（误报）", "good but alarmed"], api.fmt(1000 * (1 - p.base) * p.fa, 1)],
              [["报警的概率 Pr(A)", "P(alarm)"], api.fmt(100 * al, 2) + " %"],
              [["报警齿轮真有缺陷 Pr(D | A)", "P(defective | alarm)"], api.fmt(100 * post, 1) + " %"]];
    }
    const tags = this.TAGS.reduce((a, i) => a + s.bel[i], 0);
    let best = 0; s.bel.forEach((b, i) => { if (b > s.bel[best]) best = i; });
    if (s.nz === 1 && s.lastZ === 1 && s.log.length === 1 && tags > 0.6) api.done("one");
    if (s.bel[s.x] > 0.8) api.done("found");
    return [[["操作记录", "log"], s.log.length ? s.log.slice(-8).join(" → ") : "—"],
            [["四个标志格的概率之和", "total on the four tags"], api.fmt(100 * tags, 1) + " %"],
            [["最可能的格（概率）", "most likely cell (prob.)"], `${best} (${api.fmt(s.bel[best], 3)})`],
            [["AGV 实际所在的格（概率）", "true cell (prob.)"], `${s.x} (${api.fmt(s.bel[s.x], 3)})`]];
  },
  draw(api, s) {
    const { w, h } = api, c = api.ctx;
    if (api.scene === "qc") {
      const p = api.p, cols = 50, rows = 20, cw = (w - 40) / cols, ch = (h - 70) / rows;
      const nd = Math.round(1000 * p.base), ndh = Math.round(1000 * p.base * p.hit), nfa = Math.round(1000 * (1 - p.base) * p.fa);
      for (let k = 0; k < 1000; k++) {
        const r = Math.floor(k / cols), q = k % cols, x = 20 + q * cw + cw / 2, y = 30 + r * ch + ch / 2;
        let fill = api.css("--grid"), stroke = null;
        if (k < ndh) fill = api.css("--red");
        else if (k < nd) { fill = api.css("--panel"); stroke = api.css("--red"); }
        else if (k < nd + nfa) fill = api.css("--blue");
        api.circle(x, y, Math.min(cw, ch) * 0.36, fill, stroke);
      }
      api.label(api.T("红：有缺陷且报警　红圈：有缺陷但漏检　蓝：无缺陷却报警　灰：无缺陷不报警",
                      "red: defective, alarmed   red ring: defective, missed   blue: good, alarmed   grey: good, quiet"), 20, 14, api.css("--muted"), 12);
      api.label(api.T("报警的 = 红 + 蓝；其中真有缺陷的只占红色那一部分", "alarmed = red + blue; only the red ones are defective"), 20, h - 20, api.css("--ink"), 13);
      return;
    }
    const N = this.N, x0 = 30, x1 = w - 20, cw = (x1 - x0) / N, yb = h - 70, top = 40;
    const H = (b) => (yb - top) * Math.min(1, b / 0.6);
    for (let i = 0; i < N; i++) {
      const X = x0 + i * cw;
      api.rect(X + 3, yb - H(s.bel[i]), cw - 6, H(s.bel[i]), this.isTag(i) ? api.css("--amber") : api.css("--grid"));
      api.label(String(i), X + cw / 2, yb + 14, api.css("--muted"), 11, "center");
    }
    api.line(x0, yb, x1, yb, api.css("--ink"), 1.5);
    // 地面与反光标志
    api.rect(x0, yb + 26, x1 - x0, 8, api.css("--panel"), api.css("--muted"));
    this.TAGS.forEach((i) => api.rect(x0 + i * cw + cw * 0.2, yb + 26, cw * 0.6, 8, api.css("--amber")));
    // AGV 实际位置
    const ax = x0 + s.x * cw + cw / 2;
    api.agv(ax, yb + 26, Math.max(26, cw * 0.9), api.css("--blue"));
    api.label(api.T("AGV（实际位置）", "AGV (true)"), ax, yb + 46, api.css("--blue"), 11, "center");
    api.label(api.T("各格的概率（金色：有标志的格；柱高满格 = 0.6）", "probability of each cell (gold: tag cells; full height = 0.6)"), x0, 20, api.css("--muted"), 12);
  },
});
