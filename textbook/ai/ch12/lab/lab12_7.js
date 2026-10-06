// 实验 12.7 语音指令与拒识阈值（配 12.7 节）。三个场景：
//   score ：十条指令在给定信噪比下的匹配得分分布——正确的一堆与认错的一堆有多少重叠；
//   thresh：拉动阈值，看误执行与拒识此消彼长，以及总代价（误执行 × 代价 + 拒识 × 代价）的最低点在哪；
//   cost  ：改两种错误的代价之比，看最优阈值怎样往上走——这正是 11.8 节代价敏感阈值的同一套做法。
// 指令的“声音”由程序按固定公式合成（与书中 _ch12.py 的办法同源，这里为了在浏览器里实时算而简化成
// 低维特征向量 + 发音变异 + 噪声），不需要麦克风，也不上传任何录音。
WQ.lab({
  title: ["实验 12.7 语音指令与拒识阈值", "Lab 12.7 Voice commands and the rejection threshold"],
  goal: ["在车间噪声下识别十条 AGV 指令，用代价（误执行比拒识贵得多）定出拒识阈值，看清一件事：最糟的那一档信噪比上，调阈值救不了场，得先治声音。",
         "Recognize ten AGV commands under workshop noise, set the rejection threshold from costs (a wrong execution is far more expensive than a re-ask), and see that at the worst SNR no threshold saves you — you have to fix the audio first."],
  scenes: [
    { id: "score", name: ["得分分布", "Score distributions"],
      problem: { title: ["问题：认对与认错的得分分得开吗", "Problem: do right and wrong scores separate"],
                 text: ["每次识别都给出一个匹配得分。信噪比高时，认对的得分明显高于认错的，两堆分得开；信噪比一掉，两堆重叠——这时无论阈值定在哪，都既会放过误执行，又会拒掉正确的。",
                        "Every recognition yields a match score. At a high SNR the correct hits score well above the mistakes; as the SNR drops the two piles overlap, and then no threshold can avoid both wrong executions and needless rejections."] } },
    { id: "thresh", name: ["阈值与代价", "Threshold and cost"],
      problem: { title: ["问题：阈值定在哪", "Problem: where to put the threshold"],
                 text: ["阈值高了，误执行少、拒识多；低了反过来。把两种错误各乘上自己的代价加起来，总代价有一个最低点——那就是该定的阈值，而不是“准确率最高”的那个。",
                        "A high threshold means fewer wrong executions and more rejections; a low one the opposite. Weight each error by its cost and the total has a minimum — that, not the most accurate point, is where the threshold belongs."] } },
    { id: "cost", name: ["代价之比", "Cost ratio"],
      problem: { title: ["问题：代价之比决定什么", "Problem: what the cost ratio decides"],
                 text: ["误执行一条“前进”可能撞到人，拒识只是让人再说一遍。比值从 1 涨到 100，最优阈值一路往上，直到所有还会认错的那几次得分已经比一部分正确的还高——再提高比值也没用了。",
                        "A wrong “forward” can hit someone; a rejection only costs a repeat. As the ratio grows from 1 to 100 the best threshold rises, until the remaining mistakes already outscore some correct hits — past that, a higher ratio changes nothing."] } },
  ],
  params: [
    { id: "snr", name: ["信噪比（dB）", "SNR (dB)"], min: -15, max: 20, step: 1, value: 5, digits: 0 },
    { id: "nrep", name: ["每条指令说几遍", "Repeats per command"], min: 2, max: 12, step: 1, value: 8, digits: 0 },
    { id: "vary", name: ["发音变异（%）", "Pronunciation variation (%)"], min: 0, max: 60, step: 5, value: 25, digits: 0 },
    { id: "thr", name: ["判定阈值", "Decision threshold"], min: 0, max: 1, step: 0.01, value: 0.5, digits: 2 },
    { id: "cwrong", name: ["误执行的代价", "Cost of a wrong execution"], min: 1, max: 200, step: 1, value: 100, digits: 0 },
    { id: "creject", name: ["拒识的代价", "Cost of a rejection"], min: 1, max: 20, step: 1, value: 1, digits: 0 },
    { id: "confirm", name: ["危险指令要确认（0 关 · 1 开）", "Confirm risky commands (0 off · 1 on)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
  ],
  legend: [{ color: "var(--green)", name: ["认对", "correct"] }, { color: "var(--red)", name: ["认错", "mistake"] },
           { color: "var(--blue)", name: ["总代价", "total cost"] }],
  tasks: [
    { id: "drop", text: ["把信噪比从 20 dB 降到 −10 dB：准确率掉到多少？两堆得分还分得开吗？",
                         "Drop the SNR from 20 dB to −10 dB: how far does accuracy fall, and do the two score piles still separate?"],
      demo: { scene: "score", set: { snr: -10 }, press: [] } },
    { id: "tune", text: ["把阈值拉到 0.80 以上：误执行降到几次、拒识涨到几次？与读数里“代价最低的阈值”比，你定高了还是低了？",
                         "Raise the threshold above 0.80: how far do the wrong executions fall and the rejections rise? Compare with the minimum-cost threshold in the readout — did you go too high or too low?"],
      demo: { scene: "thresh", set: { snr: 5, thr: 0.85 }, press: [] } },
    { id: "ratio", text: ["把误执行的代价改成 200、拒识改成 1（比值 200）：最优阈值变成多少？拒识的比例涨到多少？",
                          "Set the wrong-execution cost to 200 and the rejection cost to 1 (ratio 200): what is the best threshold now, and what fraction gets rejected?"],
      demo: { scene: "cost", set: { cwrong: 200, creject: 1 }, press: [] } },
    { id: "equal", text: ["再把两种代价改成一样（都取 1）：最优阈值掉到哪里？这说明阈值是代价定的，不是准确率定的。",
                          "Now make both costs equal (1 and 1): where does the best threshold go? The threshold is set by costs, not by accuracy."],
      demo: { scene: "cost", set: { cwrong: 1, creject: 1 }, press: [] } },
    { id: "guard", text: ["打开“危险指令要确认”：误执行的次数和总代价各变成多少？代价为什么比调阈值降得更干脆？",
                          "Turn on “confirm risky commands”: what happens to the wrong executions and the total cost, and why does it drop more cleanly than any threshold?"],
      demo: { scene: "thresh", set: { confirm: 1 }, press: [] } },
  ],
  think: ["如果把“停止”单独拿出来：它听错的方向是安全的（本该动却停下），要不要给它一个更低的阈值？",
          "Consider “stop” on its own: mistaking it fails safe (stopping when it should move). Should it get a lower threshold than the others?"],

  // 十条指令：名字 + 是否危险（会让车动起来的算危险）
  CMD: [["前进", "forward", 1], ["后退", "back", 1], ["左转", "left", 1], ["右转", "right", 1],
        ["停止", "stop", 0], ["暂停", "pause", 0], ["继续", "resume", 1],
        ["去一号工位", "to station 1", 1], ["去三号工位", "to station 3", 1], ["回充电桩", "to charger", 1]],
  DIM: 12,
  // 确定性的伪随机：同样的参数永远给同样的结果，学生记下的数字可复算
  rand(i) { const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); },
  gauss(i) {
    const u = Math.max(1e-9, this.rand(i)), v = this.rand(i + 7919);
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  },
  templates() {
    if (this._tpl) return this._tpl;
    const T = [];
    for (let c = 0; c < this.CMD.length; c++) {
      const t = new Float64Array(this.DIM);
      let n = 0;
      for (let d = 0; d < this.DIM; d++) { t[d] = this.gauss(c * 101 + d * 13 + 1); n += t[d] * t[d]; }
      n = Math.sqrt(n);
      for (let d = 0; d < this.DIM; d++) t[d] /= n;
      // 相邻的两条指令故意做得像一些（“去一号工位”与“去三号工位”只差一个字）
      T.push(t);
    }
    for (const pair of [[7, 8], [0, 6]]) {                       // 把这两对拉近，模拟易混指令
      const a = T[pair[0]], b = T[pair[1]];
      let n = 0;
      for (let d = 0; d < this.DIM; d++) { b[d] = 0.75 * a[d] + 0.25 * b[d]; n += b[d] * b[d]; }
      n = Math.sqrt(n);
      for (let d = 0; d < this.DIM; d++) b[d] /= n;
    }
    this._tpl = T;
    return T;
  },
  trials(api) {
    const p = api.p;
    const key = [p.snr, p.nrep, p.vary].join(",");
    if (this._tr && this._tr.key === key) return this._tr.val;    // 得分只随这三个参数变，阈值与代价不用重算
    // 噪声幅度按信噪比折算，再按特征维数归一：这样 20 dB 几乎全对、5 dB 掉到八成上下、−10 dB 基本认不出
    const T = this.templates(), sigma = 0.9 * Math.pow(10, -p.snr / 20) / Math.sqrt(this.DIM);
    const out = [];
    for (let c = 0; c < this.CMD.length; c++) {
      for (let r = 0; r < p.nrep; r++) {
        const seed = (c * 977 + r * 31 + 5) * 3;
        const x = new Float64Array(this.DIM);
        let n = 0;
        for (let d = 0; d < this.DIM; d++) {
          // 一遍发音 = 模板 + 发音变异（同一个人说两遍也不一样）+ 噪声
          x[d] = T[c][d] * (1 + p.vary / 100 * this.gauss(seed + d)) + sigma * this.gauss(seed + d + 613);
          n += x[d] * x[d];
        }
        n = Math.sqrt(n) || 1;
        let best = -2, second = -2, arg = 0;
        for (let k = 0; k < T.length; k++) {
          let s = 0;
          for (let d = 0; d < this.DIM; d++) s += x[d] / n * T[k][d];
          if (s > best) { second = best; best = s; arg = k; } else if (s > second) { second = s; }
        }
        // 得分取“最佳与次佳之差”折进相似度：两条指令难分时得分自然就低
        const score = Math.max(0, Math.min(1, 0.5 * (best + 1) * (0.6 + 0.4 * Math.min(1, (best - second) / 0.25))));
        out.push({ cmd: c, pred: arg, ok: arg === c, score, risky: this.CMD[c][2] === 1 });
      }
    }
    this._tr = { key, val: out };
    return out;
  },
  // 给定阈值，算出误执行、拒识与总代价；确认回路会把“危险指令的误执行”变成一次确认（代价按拒识算）
  evalAt(api, tr, t) {
    const p = api.p;
    let wrong = 0, rej = 0, caught = 0;
    for (const z of tr) {
      if (z.score < t) { rej++; continue; }
      if (z.ok) continue;
      if (p.confirm === 1 && z.risky) { caught++; continue; }      // 人在确认时发现不对，等于多说一遍
      wrong++;
    }
    return { wrong, rej, caught, cost: wrong * p.cwrong + (rej + caught) * p.creject };
  },
  best(api, tr) {
    let bt = 0, bc = Infinity;
    for (let i = 0; i <= 100; i++) {
      const t = i / 100, e = this.evalAt(api, tr, t);
      if (e.cost < bc - 1e-9) { bc = e.cost; bt = t; }             // 同代价时取最低的阈值（少拒一点）
    }
    return { t: bt, cost: bc };
  },
  reset(api, s) {},
  readouts(api, s) {
    const p = api.p, tr = this.trials(api);
    const acc = 100 * tr.filter((z) => z.ok).length / tr.length;
    const now = this.evalAt(api, tr, p.thr), bst = this.best(api, tr), none = this.evalAt(api, tr, 0);
    if (p.snr <= -10) api.done("drop");
    if (p.thr >= 0.8 && now.rej > 0) api.done("tune");
    if (p.cwrong / p.creject >= 100) api.done("ratio");
    if (p.cwrong === p.creject) api.done("equal");
    if (p.confirm === 1) api.done("guard");
    return [[["试验次数 / 不拒识时的准确率", "trials / accuracy without rejection"], tr.length + " / " + api.fmt(acc, 1) + "%"],
            [["当前阈值下：误执行 / 拒识", "at this threshold: wrong / rejected"], now.wrong + " / " + now.rej],
            [["当前总代价（不拒识时）", "total cost (vs no rejection)"], api.fmt(now.cost, 0) + " (" + api.fmt(none.cost, 0) + ")"],
            [["代价最低的阈值 / 那里的代价", "best threshold / its cost"], api.fmt(bst.t, 2) + " / " + api.fmt(bst.cost, 0)],
            [["被拒的比例", "rejected share"], api.fmt(100 * now.rej / tr.length, 0) + "%"],
            [["确认回路挡下的误执行", "wrong executions caught by confirmation"], now.caught]];
  },
  draw(api, s) {
    const { w, h } = api, m = 34, tr = this.trials(api), p = api.p;
    const top = h * 0.46, bot = h - top - 30;
    // 上半：得分分布（认对一堆、认错一堆），竖线是当前阈值
    api.label(api.T("得分分布（上：认对，下：认错）", "score distributions (top: correct, bottom: mistakes)"), m, 16, api.css("--ink"), 12);
    const NB = 25, hi = new Array(NB).fill(0), lo = new Array(NB).fill(0);
    for (const z of tr) {
      const b = Math.min(NB - 1, Math.floor(z.score * NB));
      if (z.ok) hi[b]++; else lo[b]++;
    }
    const mx = Math.max(1, ...hi, ...lo), bw = (w - 2 * m) / NB;
    for (let b = 0; b < NB; b++) {
      const x0 = m + b * bw, mid = 24 + (top - 34) / 2;
      api.rect(x0, mid - (top - 34) / 2 * hi[b] / mx, Math.max(1, bw - 1), (top - 34) / 2 * hi[b] / mx, api.css("--green"));
      api.rect(x0, mid, Math.max(1, bw - 1), (top - 34) / 2 * lo[b] / mx, api.css("--red"));
    }
    const tx = m + p.thr * (w - 2 * m);
    api.line(tx, 20, tx, top, api.css("--ink"), 1.5);
    api.label(api.T("阈值 ", "threshold ") + api.fmt(p.thr, 2), Math.min(tx + 4, w - m - 70), 30, api.css("--ink"), 11);
    // 下半：总代价随阈值的曲线，标出最低点
    api.label(api.T("总代价随阈值变化", "total cost vs threshold"), m, top + 24, api.css("--blue"), 12);
    const cs = [];
    for (let i = 0; i <= 100; i++) cs.push(this.evalAt(api, tr, i / 100).cost);
    const cmax = Math.max(...cs, 1);
    let px = m, py = top + 34 + bot * (1 - cs[0] / cmax);
    for (let i = 1; i <= 100; i++) {
      const x1 = m + i / 100 * (w - 2 * m), y1 = top + 34 + bot * (1 - cs[i] / cmax);
      api.line(px, py, x1, y1, api.css("--blue"), 1.6);
      px = x1; py = y1;
    }
    const bst = this.best(api, tr);
    const bx = m + bst.t * (w - 2 * m), by = top + 34 + bot * (1 - bst.cost / cmax);
    api.rect(bx - 3, by - 3, 6, 6, api.css("--ink"));
    api.label(api.T("最低 ", "min ") + api.fmt(bst.cost, 0) + api.T(" @ 阈值 ", " @ ") + api.fmt(bst.t, 2),
              Math.min(bx + 6, w - m - 110), Math.max(top + 44, by - 6), api.css("--ink"), 11);
    api.line(m, top + 34 + bot, w - m, top + 34 + bot, api.css("--grid"), 1);
  },
});
