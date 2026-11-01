// 实验 17.3 错误怎么累积，又怎么救回来（配 17.3 节）。
// 两个场景：
//   decay  ：调每步出错率与步数，看整件事做成的概率怎么掉；
//   remedy ：三种救法（整件事重试、每步自检、末端校验）各买回多少，以及校验器误判的代价。
// 全部按解析式算，不用采样——这一节的东西本来就是算得出来的。
// 与 code/_ch17.py 是同一套式子。
WQ.lab({
  title: ["实验 17.3 智能体走得了多远", "Lab 17.3 How far an agent can go"],
  goal: ["亲手调每步出错率与步数，看整件事做成的概率怎样掉下去；再把三种救法一个个打开，看各买回多少。做完能回答三个问题：为什么智能体走不长、三种救法分别治什么、以及校验器什么时候开始帮倒忙。",
         "Turn the per-step error rate and the number of steps, and watch the overall success rate fall; then switch on each remedy in turn. You should be able to say why agents cannot run for long, what each remedy fixes, and when a verifier starts doing more harm than good."],
  scenes: [
    { id: "decay", name: ["错误怎么累积", "How errors pile up"],
      problem: { title: ["问题：为什么智能体走不长", "Problem: why agents cannot run for long"],
                 text: ["智能体一圈一圈转：规划、调工具、读结果、修正。转一圈算一步。每一步都可能出错——工具挑错了、参数填错了、结果读歪了。单看一步，出错率也许只有百分之几；可这些小毛病是乘起来的：每步出错率 p、走 n 步，整件事做成的概率就是 (1−p)ⁿ。这不是经验规律，是恒等式。",
                        "An agent loops: plan, act, observe, revise. One lap is one step, and every step can go wrong — wrong tool, wrong argument, misread result. Per step that may be a few percent, but the errors multiply: with error rate p over n steps the whole task succeeds with probability (1-p)^n. That is an identity, not an observation."] } },
    { id: "remedy", name: ["三种救法", "Three remedies"],
      problem: { title: ["问题：怎么救", "Problem: what can be done"],
                 text: ["三种办法：整件事失败了从头再来；每一步做完自检一下，查出错就重做这一步；整件事做完用一个校验器判对错，判错就重做。三种治的不是同一件事，买回来的也不一样多。要当心最后一种：校验器也会把对的判成错——那是要把好结果扔掉的。",
                        "Three options: retry the whole task; check after each step and redo that step when an error is caught; or verify the finished result and redo it if the verifier says no. They fix different things and buy back different amounts. Watch the last one: a verifier also rejects correct results, and that throws good work away."] } },
  ],
  params: [
    { id: "p", name: ["每步出错率（%）", "error rate per step (%)"], min: 0.5, max: 20, step: 0.5, value: 5, digits: 1 },
    { id: "n", name: ["一共走几步", "number of steps"], min: 1, max: 60, step: 1, value: 20, digits: 0 },
    { id: "retry", name: ["整件事重试几次", "retries of the whole task"], min: 1, max: 6, step: 1, value: 1, digits: 0 },
    { id: "detect", name: ["每步自检的查出率", "per-step detection rate"], min: 0, max: 0.99, step: 0.01, value: 0, digits: 2 },
    { id: "tpr", name: ["末端校验的查错能力", "verifier detection rate"], min: 0, max: 1, step: 0.05, value: 0, digits: 2 },
    { id: "fpr", name: ["末端校验把对的判成错", "verifier false-rejection rate"], min: 0, max: 0.9, step: 0.05, value: 0.05, digits: 2 },
  ],
  legend: [{ color: "var(--muted)", name: ["什么都不做", "nothing"] },
           { color: "var(--blue)", name: ["整件事重试", "retry"] },
           { color: "var(--green)", name: ["每步自检", "per-step check"] },
           { color: "var(--accent)", name: ["末端校验", "final verifier"] }],
  tasks: [
    { id: "base", text: ["按默认设置（每步出错 5%、走 20 步）：整件事做成的概率是多少？把步数拖到 40 呢？",
                         "At the defaults (5% per step, 20 steps): what is the overall success rate, and what happens at 40 steps?"],
      demo: { scene: "decay", set: { p: 5, n: 40 }, press: [] } },
    { id: "halve", text: ["把每步出错率从 5% 降到 1%（步数仍是 20）：成功率涨了多少倍？再看读数里能走几步那一行。",
                          "Lower the per-step error from 5% to 1% at 20 steps: how many times higher is the success rate? Then read the 'steps you can afford' line."],
      demo: { scene: "decay", set: { p: 1, n: 20 }, press: [] } },
    { id: "retry", text: ["切到“三种救法”，把“整件事重试”调到 4 次（其余都关着）：买回来多少？它要求什么前提？",
                          "Switch to the remedies scene and set retries to 4 with everything else off: how much does it buy, and what does it assume?"],
      demo: { scene: "remedy", set: { p: 5, n: 20, retry: 4, detect: 0, tpr: 0 }, press: [] } },
    { id: "check", text: ["把重试调回 1，改开“每步自检”，查出率 0.8：这一次买回来多少？与重试四次比哪个多？",
                          "Set retries back to 1 and turn on the per-step check at 0.8: how much now, and how does it compare with four retries?"],
      demo: { scene: "remedy", set: { retry: 1, detect: 0.8, tpr: 0 }, press: [] } },
    { id: "verify", text: ["只开末端校验（查错能力 0.95），把“把对的判成错”从 0 一路拖到 0.9：校验买回来的好处被吃掉了多少？再把查错能力降到 0.8 试一次。",
                           "Turn on only the final verifier (detection 0.95) and drag the false-rejection rate from 0 all the way to 0.9: how much of the gain is eaten up? Then repeat with the detection rate at 0.8."],
      demo: { scene: "remedy", set: { detect: 0, tpr: 0.95, fpr: 0.9 }, press: [] } },
  ],
  think: ["把每步出错率从 5% 降到 2.5%（减一半），与“整件事重试两次”相比，哪一个买回来的多？在什么步数上两者打平？这件事对“该把力气花在哪”有什么提示？",
          "Compare halving the per-step error rate from 5% to 2.5% with retrying the whole task twice. Which buys more, and at what number of steps do they tie? What does that say about where to spend effort?"],

  plain(p, n) { return Math.pow(1 - p, n); },
  withRetry(p, n, t) { return 1 - Math.pow(1 - this.plain(p, n), t); },
  withCheck(p, n, d) { const q = p * (1 - d * (1 - p)); return Math.pow(1 - q, n); },
  withVerifier(p, n, tpr, fpr, tries) {
    const s = this.plain(p, n);
    let ok = 0, alive = 1;
    for (let i = 0; i < tries; i++) { ok += alive * s * (1 - fpr); alive = alive * (s * fpr + (1 - s) * tpr); }
    return ok + alive * s;
  },
  stepsFor(p, target) { return p <= 0 ? Infinity : Math.log(target) / Math.log(1 - p); },
  calc(api) {
    const q = api.p, p = q.p / 100, n = Math.round(q.n);
    const key = [api.scene, q.p, q.n, q.retry, q.detect, q.tpr, q.fpr].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const base = this.plain(p, n);
    const val = {
      p, n, base,
      retry: this.withRetry(p, n, Math.round(q.retry)),
      check: q.detect > 0 ? this.withCheck(p, n, q.detect) : base,
      verify: q.tpr > 0 ? this.withVerifier(p, n, q.tpr, q.fpr, 3) : base,
      n80: this.stepsFor(p, 0.8), n50: this.stepsFor(p, 0.5),
      // 三种救法一起开（先自检，再末端校验，最后整件事重试）
      combo: (() => {
        const pe = q.detect > 0 ? p * (1 - q.detect * (1 - p)) : p;
        const s = q.tpr > 0 ? this.withVerifier(pe, n, q.tpr, q.fpr, 3) : this.plain(pe, n);
        return 1 - Math.pow(1 - s, Math.round(q.retry));
      })(),
    };
    val.effective = 1 - Math.pow(val.check, 1 / n);
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const q = api.p, c = this.calc(api);
    if (api.scene === "decay" && q.n >= 35) api.done("base");
    if (api.scene === "decay" && q.p <= 1.5) api.done("halve");
    if (api.scene === "remedy" && q.retry >= 4 && q.detect < 0.05 && q.tpr < 0.05) api.done("retry");
    if (api.scene === "remedy" && q.detect >= 0.75 && q.retry <= 1) api.done("check");
    if (api.scene === "remedy" && q.tpr >= 0.9 && q.fpr >= 0.85) api.done("verify");
    if (api.scene === "decay") {
      return [[["整件事做成的概率", "probability the whole task succeeds"], c.base.toFixed(4)],
              [["每一步都对的概率", "probability each single step is right"], (1 - c.p).toFixed(3)],
              [["保住 80% 最多能走几步", "steps you can afford at 80%"],
               isFinite(c.n80) ? c.n80.toFixed(1) : "—"],
              [["保住 50% 最多能走几步", "steps you can afford at 50%"],
               isFinite(c.n50) ? c.n50.toFixed(1) : "—"],
              [["走到第几步跌破一半", "where it falls below one half"],
               isFinite(c.n50) ? Math.ceil(c.n50) + api.T(" 步", " steps") : "—"]];
    }
    return [[["什么都不做", "nothing"], c.base.toFixed(3)],
            [["整件事重试", "retry the whole task"], c.retry.toFixed(3)],
            [["每步自检", "per-step check"], c.check.toFixed(3)],
            [["末端校验", "final verifier"], c.verify.toFixed(3)],
            [["自检把每步出错率压到", "effective per-step error after checking"],
             (c.effective * 100).toFixed(2) + "%"]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api);
    const x0 = 58, y0 = 22, pw = w - x0 - 150, ph = h - y0 - 44;
    const NM = 60;
    const X = (n) => x0 + n / NM * pw, Y = (v) => y0 + ph - v * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    for (let g = 0; g <= 1.0001; g += 0.2) {
      api.line(x0, Y(g), x0 + pw, Y(g), api.css("--grid"), 1);
      api.label(g.toFixed(1), 22, Y(g) + 4, api.css("--muted"), 11);
    }
    for (let n = 0; n <= NM; n += 10) {
      api.line(X(n), y0, X(n), y0 + ph, api.css("--grid"), 1);
      api.label(String(n), X(n) - 6, y0 + ph + 16, api.css("--muted"), 11);
    }
    const curve = (fn, col, wd, dash) => {
      let prev = null;
      for (let n = 0; n <= NM; n++) {
        const cur = [X(n), Y(fn(n))];
        if (prev) api.line(prev[0], prev[1], cur[0], cur[1], col, wd, dash);
        prev = cur;
      }
    };
    curve((n) => this.plain(c.p, n), api.css("--muted"), 2.2);
    if (api.scene === "remedy") {
      const q = api.p;
      if (q.retry > 1) curve((n) => this.withRetry(c.p, n, Math.round(q.retry)), api.css("--blue"), 2.4);
      if (q.detect > 0) curve((n) => this.withCheck(c.p, n, q.detect), api.css("--green"), 2.4);
      if (q.tpr > 0) curve((n) => this.withVerifier(c.p, n, q.tpr, q.fpr, 3), api.css("--accent"), 2.4);
    }
    // 当前步数那条竖线
    api.line(X(c.n), y0, X(c.n), y0 + ph, api.css("--ink"), 1.4, [4, 4]);
    api.circle(X(c.n), Y(c.base), 4, null, api.css("--muted"));
    if (api.scene === "decay" && isFinite(c.n80) && c.n80 <= NM) {
      api.line(x0, Y(0.8), x0 + pw, Y(0.8), api.css("--red"), 1.4, [5, 4]);
      api.circle(X(c.n80), Y(0.8), 4, null, api.css("--red"));
      api.label(api.T(`${c.n80.toFixed(1)} 步跌破 80%`, `below 80% after ${c.n80.toFixed(1)} steps`),
                Math.min(X(c.n80) + 8, x0 + pw - 120), Y(0.8) - 8, api.css("--red"), 11);
    }
    api.label(api.T("做成的概率", "success probability"), 10, y0 + 12, api.css("--muted"), 12);
    api.label(api.T("一共走几步", "number of steps"), x0 + pw / 2 - 30, h - 12, api.css("--muted"), 12);
    const bx = x0 + pw + 14;
    api.label(api.T(`走 ${c.n} 步`, `${c.n} steps`), bx, y0 + 16, api.css("--ink"), 13);
    const rows = api.scene === "decay"
      ? [[api.T("做成", "succeeds"), c.base, api.css("--muted")]]
      : [[api.T("什么都不做", "nothing"), c.base, api.css("--muted")],
         [api.T("重试", "retry"), c.retry, api.css("--blue")],
         [api.T("自检", "check"), c.check, api.css("--green")],
         [api.T("校验", "verify"), c.verify, api.css("--accent")],
         [api.T("三个一起", "all three"), c.combo, api.css("--ink")]];
    rows.forEach((r, i) => api.label(`${r[0]} ${r[1].toFixed(3)}`, bx, y0 + 40 + i * 20, r[2], 12));
    if (api.scene === "remedy" && api.p.tpr > 0 && c.verify < c.base) {
      api.label(api.T("校验反而更差了", "the verifier is now hurting"), bx, y0 + 40 + rows.length * 20 + 10,
                api.css("--red"), 12);
    }
  },
});
