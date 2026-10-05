// 实验 11.3 检测器怎样被评分：交并比、非极大值抑制与 PR 曲线（配 11.3、11.8 节）。
// 三个场景：
//   iou  ：拖动预测框，实时看交并比怎样变；什么时候算“命中”（阈值 0.5 / 0.75）；
//   nms  ：同一个缺陷上落了几个框，调抑制阈值，看留下几个、会不会把两个真缺陷合并成一个；
//   pr   ：调检测得分的阈值，看查准率、查全率与漏检、误检的数目怎样此消彼长，并按代价算出总代价
//          （漏检一件的代价由滑块给出）——这正是 11.8 节选阈值的做法。
// 本实验的“检测结果”是固定的一组数（种子固定、可复算），不需要显卡，也不训练模型。
WQ.lab({
  title: ["实验 11.3 交并比、非极大值抑制与 PR 曲线", "Lab 11.3 IoU, NMS and the PR curve"],
  goal: ["亲手调一调预测框的位置、抑制阈值与得分阈值，看三件事怎样联动：交并比决定一个框算不算命中，抑制阈值决定留下几个框，得分阈值决定漏检与误检的比例；最后按代价选出阈值。",
         "Move a predicted box, change the suppression threshold and the score threshold, and watch how IoU decides a hit, how NMS decides how many boxes survive, and how the score threshold trades misses against false alarms — then pick a threshold by cost."],
  scenes: [
    { id: "iou", name: ["交并比", "IoU"],
      problem: { title: ["问题：框到什么程度算“找到了”", "Problem: how close counts as a hit"],
                 text: ["检测器输出的框不会与真值完全重合。交并比把“重合程度”变成一个 0 到 1 的数，再用一个阈值判定命中。阈值取 0.5 还是 0.75，结论会差很多。",
                        "A predicted box never matches the truth exactly. IoU turns overlap into a number in [0,1]; a threshold then decides a hit. Whether that threshold is 0.5 or 0.75 changes the verdict."] } },
    { id: "nms", name: ["非极大值抑制", "NMS"],
      problem: { title: ["问题：同一个缺陷被框了好几次", "Problem: one defect, several boxes"],
                 text: ["检测器在同一个缺陷附近会输出好几个框。按得分从高到低保留，与已保留的框交并比超过阈值的丢掉——阈值太大留下重复的框，太小会把挨得近的两个缺陷并成一个。",
                        "Detectors fire several times near one defect. Keep boxes by score and drop those overlapping a kept box above a threshold — too high keeps duplicates, too low merges neighbouring defects."] } },
    { id: "pr", name: ["阈值与代价", "Threshold and cost"],
      problem: { title: ["问题：阈值该定在哪里", "Problem: where to put the threshold"],
                 text: ["得分阈值定高了漏检，定低了误检。产线上漏检一件缺陷品的代价远高于误判一件合格品——阈值应该按代价选，而不是按准确率选。",
                        "A high threshold misses defects; a low one raises false alarms. On a line, a miss costs far more than a false alarm — so pick the threshold by cost, not by accuracy."] } },
  ],
  params: [
    { id: "dx", name: ["预测框的横向偏移（像素）", "Box offset x (px)"], min: -60, max: 60, step: 1, value: 14, digits: 0 },
    { id: "dy", name: ["预测框的纵向偏移（像素）", "Box offset y (px)"], min: -60, max: 60, step: 1, value: 8, digits: 0 },
    { id: "scale", name: ["预测框的大小（%）", "Box size (%)"], min: 50, max: 160, step: 5, value: 100, digits: 0 },
    { id: "nms", name: ["抑制阈值（%）", "NMS threshold (%)"], min: 10, max: 90, step: 5, value: 50, digits: 0 },
    { id: "thr", name: ["得分阈值（%）", "Score threshold (%)"], min: 1, max: 99, step: 1, value: 50, digits: 0 },
    { id: "cmiss", name: ["漏检一件的代价（元）", "Cost of one miss"], min: 1, max: 200, step: 1, value: 50, digits: 0 },
  ],
  legend: [{ color: "var(--green)", name: ["真值", "ground truth"] }, { color: "var(--blue)", name: ["保留的预测", "kept"] },
           { color: "var(--muted)", name: ["被抑制的预测", "suppressed"] }],
  tasks: [
    { id: "half", text: ["把预测框移到交并比刚好跌破 0.5：偏移多少像素？框的大小不变时，横向与纵向各能容忍多少？",
                         "Move the box until the IoU just drops below 0.5: how many pixels? With the size fixed, how much can x and y each tolerate?"],
      demo: { scene: "iou", set: { dx: 34, dy: 0, scale: 100 }, press: [] } },
    { id: "size", text: ["框的位置不动，只把它放大到 140%：交并比变成多少？为什么“框大了”比“框偏了”更容易丢分？",
                         "Keep the position and enlarge the box to 140%: what is the IoU? Why does an oversized box lose more than a shifted one?"],
      demo: { scene: "iou", set: { dx: 0, dy: 0, scale: 140 }, press: [] } },
    { id: "merge", text: ["切到“非极大值抑制”，把抑制阈值降到 20%：两个挨得近的真缺陷会怎样？抑制阈值取多大最合适？",
                          "Switch to NMS and lower the threshold to 20%: what happens to two nearby defects? What threshold works best?"],
      demo: { scene: "nms", set: { nms: 20 }, press: [] } },
    { id: "cost", text: ["切到“阈值与代价”，把漏检代价设成 100 元、阈值调到代价最小处：这时放过几件、误报几件？再看“漏检与误检同样贵”时的阈值——差多少？",
                         "Switch to threshold and cost, set the miss cost to 100: which threshold minimizes total cost, and how far is it from the one you would pick if a miss cost the same?"],
      demo: { scene: "pr", set: { cmiss: 100, thr: 5 }, press: [] } },
  ],
  think: ["为什么产线上的阈值要按代价定，而不是按准确率定？什么情况下反过来（误检的代价更高）？",
          "Why pick the threshold by cost on a line rather than by accuracy? When would the opposite hold?"],

  // 六个真缺陷：前两个挨得很近（交并比约 0.35，抑制阈值太小会把它们并成一个），其余分散
  GT: [[60, 60, 160, 130], [110, 66, 210, 136], [250, 70, 330, 140],
       [60, 200, 130, 260], [250, 200, 320, 255], [380, 60, 450, 120]],
  // 固定的一组“检测结果”：[x0, y0, x1, y1, 得分]，前几个落在第一个缺陷上，中间几个落在第二个上，最后两个是误检
  // 每行 [x0, y0, x1, y1, 得分]：前六个落在真缺陷上（得分有高有低——轻微的缺陷得分就低），
  // 后四个是误检（落在油污、反光上）。得分交错，所以阈值一动，漏检与误检就同时变。
  DET: [[58, 62, 158, 132, 0.95], [112, 64, 212, 134, 0.88], [246, 74, 326, 144, 0.72],
        [62, 202, 132, 262, 0.55], [252, 198, 322, 253, 0.40], [378, 62, 448, 122, 0.28],
        [400, 180, 470, 240, 0.80], [150, 150, 210, 205, 0.62], [20, 150, 80, 210, 0.45],
        [330, 150, 390, 205, 0.38], [430, 120, 490, 175, 0.36], [180, 250, 240, 300, 0.33]],
  iou(a, b) {
    const ix = Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0]));
    const iy = Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));
    const inter = ix * iy, ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter;
    return ua > 0 ? inter / ua : 0;
  },
  moved(api) {
    const g = this.GT[0], p = api.p, s = p.scale / 100;
    const cx = (g[0] + g[2]) / 2 + p.dx, cy = (g[1] + g[3]) / 2 + p.dy;
    const w = (g[2] - g[0]) * s / 2, h = (g[3] - g[1]) * s / 2;
    return [cx - w, cy - h, cx + w, cy + h];
  },
  keep(api) {
    const thr = api.p.nms / 100, order = this.DET.map((d, i) => i).sort((a, b) => this.DET[b][4] - this.DET[a][4]);
    const kept = [];
    for (const i of order) if (kept.every((j) => this.iou(this.DET[i], this.DET[j]) <= thr)) kept.push(i);
    return kept;
  },
  counts(api) {
    const t = api.p.thr / 100, kept = this.keep(api).filter((i) => this.DET[i][4] >= t);
    const used = this.GT.map(() => false);
    let tp = 0, fp = 0;
    for (const i of kept) {
      let best = 0, bi = -1;
      this.GT.forEach((g, j) => { const v = this.iou(this.DET[i], g); if (v > best) { best = v; bi = j; } });
      if (best >= 0.5 && bi >= 0 && !used[bi]) { used[bi] = true; tp++; } else fp++;
    }
    const fn = used.filter((u) => !u).length;
    return { tp, fp, fn, kept, cost: fn * api.p.cmiss + fp * 1 };
  },
  reset(api, s) {},
  readouts(api, s) {
    const p = api.p;
    if (api.scene === "iou") {
      const v = this.iou(this.moved(api), this.GT[0]);
      if (Math.abs(v - 0.5) < 0.03 && p.scale === 100) api.done("half");
      if (p.scale === 140 && p.dx === 0 && p.dy === 0) api.done("size");
      return [[["交并比", "IoU"], api.fmt(v, 3)],
              [["阈值 0.5 下", "at IoU 0.5"], v >= 0.5 ? api.T("命中", "hit") : api.T("不算命中", "miss")],
              [["阈值 0.75 下", "at IoU 0.75"], v >= 0.75 ? api.T("命中", "hit") : api.T("不算命中", "miss")],
              [["框的面积与真值之比", "area ratio"], api.fmt((p.scale / 100) ** 2, 2)]];
    }
    if (api.scene === "nms") {
      const kept = this.keep(api);
      const covered = this.GT.filter((g) => kept.some((i) => this.iou(this.DET[i], g) >= 0.5)).length;
      if (p.nms <= 0.2 * 100) api.done("merge");
      return [[["预测框总数", "boxes in"], String(this.DET.length)],
              [["抑制后留下", "kept"], String(kept.length)],
              [["被抑制", "suppressed"], String(this.DET.length - kept.length)],
              [["两个真缺陷各有框吗", "both defects covered"], covered + " / " + this.GT.length]];
    }
    const c = this.counts(api);
    let bestT = 1, bestCost = 1e18, fairT = 1, fairCost = 1e18;
    for (let t = 1; t <= 99; t++) {
      const cc = this.counts({ p: { ...p, thr: t }, scene: "pr" });
      if (cc.cost < bestCost) { bestCost = cc.cost; bestT = t; }
      const fair = cc.fn + cc.fp;                       // 漏检与误检同样贵时的最优阈值，用来对照
      if (fair < fairCost) { fairCost = fair; fairT = t; }
    }
    if (p.cmiss >= 100 && Math.abs(p.thr - bestT) <= 8) api.done("cost");
    return [[["命中 / 误检 / 漏检", "TP / FP / FN"], c.tp + " / " + c.fp + " / " + c.fn],
            [["查准率", "precision"], api.fmt(c.tp / Math.max(c.tp + c.fp, 1) * 100, 0) + "%"],
            [["查全率", "recall"], api.fmt(c.tp / Math.max(c.tp + c.fn, 1) * 100, 0) + "%"],
            [["总代价（漏检 " + p.cmiss + " 元、误检 1 元）", "total cost (miss " + p.cmiss + ", false alarm 1)"], String(c.cost)],
            [["代价最小的阈值", "min-cost threshold"], bestT + "%"],
            [["漏检与误检同样贵时", "if a miss cost the same"], fairT + "%"]];
  },
  draw(api, s) {
    const { w, h } = api, sx = w / 520, sy = (h - 40) / 300, k = Math.min(sx, sy);
    const X = (v) => 20 + v * k, Y = (v) => 20 + v * k;
    const rect = (b, col, lw, dash) => api.rect(X(b[0]), Y(b[1]), (b[2] - b[0]) * k, (b[3] - b[1]) * k, col, lw, dash);
    if (api.scene === "iou") {
      const g = this.GT[0], p = this.moved(api);
      api.rect(X(g[0]), Y(g[1]), (g[2] - g[0]) * k, (g[3] - g[1]) * k, api.css("--green"));
      rect(p, api.css("--blue"), 2);
      const ix0 = Math.max(g[0], p[0]), iy0 = Math.max(g[1], p[1]);
      const ix1 = Math.min(g[2], p[2]), iy1 = Math.min(g[3], p[3]);
      if (ix1 > ix0 && iy1 > iy0) api.rect(X(ix0), Y(iy0), (ix1 - ix0) * k, (iy1 - iy0) * k, api.css("--amber"));
      api.label(api.T("绿：真值　蓝：预测　黄：交集", "green: truth, blue: prediction, amber: intersection"),
                20, h - 14, api.css("--muted"), 12);
      return;
    }
    const kept = new Set(api.scene === "nms" ? this.keep(api) : this.counts(api).kept);
    this.GT.forEach((g) => api.rect(X(g[0]), Y(g[1]), (g[2] - g[0]) * k, (g[3] - g[1]) * k, api.css("--green")));
    this.DET.forEach((d, i) => {
      const on = kept.has(i);
      api.rect(X(d[0]), Y(d[1]), (d[2] - d[0]) * k, (d[3] - d[1]) * k, api.css(on ? "--blue" : "--muted"), on ? 2 : 1);
      api.label(d[4].toFixed(2), X(d[2]) + 4, Y(d[1]) + 14, api.css(on ? "--blue" : "--muted"), 11);
    });
    api.label(api.T("绿：真值　蓝：保留　灰：被抑制或低于阈值", "green: truth, blue: kept, grey: suppressed or below threshold"),
              20, h - 14, api.css("--muted"), 12);
  },
});
