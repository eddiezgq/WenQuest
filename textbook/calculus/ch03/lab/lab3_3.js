// 实验 3.3 ε–N 游戏与迭代开方（配 3.3 节）。“ε–N 游戏”：系统给出 ε = 10^(−k)，学生选 N，检查第 N 项以后（直到第 5000 项）
// 是否全部落在 ε 带内。“关节误差”：式 (3.2.1) 的示意模型 e_k = 10°·0.99^k·cos(0.03k)，找 ±2% 带的调节时间。
// “ε–N 游戏”检查到第 20000 项。“迭代开方”：二分法（从 [0, max(1, a)] 出发）与式 (3.1.1)（从 x₁ = max(1, a) 出发）求 √a，比较误差随步数的变化。
WQ.lab({
  title: ["实验 3.3 ε–N 游戏与迭代开方", "Lab 3.3 The ε–N game and iterative square roots"],
  goal: ["对给定的 ε 找出 N，体会数列极限的定义；用调节时间理解 N；比较两种求平方根的迭代，看误差缩小的快慢。",
         "Find N for a given ε to feel the definition of a limit; read N as a settling time; compare two square-root iterations and how fast their errors shrink."],
  scenes: [
    { id: "game", name: ["ε–N 游戏", "The ε–N game"], hide: ["k", "a"],
      problem: { title: ["给我一个 ε，我给你一个 N", "Give me an ε, I give you an N"],
                 text: ["选一个数列，系统给出误差带的半宽 ε。把 N 调到使第 N 项以后的点全部落在带内。ε 缩小时 N 怎样变化？对发散的数列，能找到 N 吗？",
                        "Pick a sequence; the system gives the half-width ε of the band. Move N until every point after the N-th lies in the band. How does N change as ε shrinks? Can you find N for a divergent sequence?"] } },
    { id: "joint", robot: true, name: ["关节误差", "Joint error"], hide: ["s", "e", "k", "a"],
      problem: { title: ["机器人问题：关节什么时候算到位？", "Robot problem: when has the joint arrived?"],
                 text: ["关节转过 10°，每 1 ms 读一次误差。误差先冲过头再来回振荡。找出误差进入 ±2% 带（±0.2°）并且再也不出来的最早步数，这就是调节时间。",
                        "The joint turns 10°, its error read every 1 ms. The error overshoots and oscillates. Find the first step after which it stays inside the ±2% band (±0.2°) for good: the settling time."] } },
    { id: "iter", robot: true, name: ["迭代开方", "Iterative square root"], hide: ["s", "e", "N"],
      problem: { title: ["机器人问题：没有开方指令的芯片怎样算距离？", "Robot problem: distance on a chip without a square-root instruction"],
                 text: ["控制器要算 √a。二分法每步把区间减半；式 (3.1.1) 每步用 (x + a/x)/2 修正。比较两者的误差怎样随步数缩小，各需几步达到 10⁻¹²。",
                        "The controller needs √a. Bisection halves an interval each step; formula (3.1.1) corrects x to (x + a/x)/2. Compare how their errors shrink and how many steps each needs for 10⁻¹²."] } },
  ],
  params: [
    { id: "s", name: ["数列：1 (−1)ⁿ/n，2 (3n+1)/(2n−1)，3 n^(1/n)，4 (−1)ⁿ", "Sequence: 1 (−1)ⁿ/n, 2 (3n+1)/(2n−1), 3 n^(1/n), 4 (−1)ⁿ"], min: 1, max: 4, step: 1, value: 1, digits: 0 },
    { id: "e", name: ["ε = 10^(−k) 中的 k", "k in ε = 10^(−k)"], min: 1, max: 3, step: 1, value: 1, digits: 0 },
    { id: "N", name: ["N", "N"], min: 1, max: 10000, step: 1, value: 5, digits: 0 },
    { id: "a", name: ["被开方数 a", "Radicand a"], min: 2, max: 1000, step: 1, value: 2, digits: 0 },
    { id: "k", name: ["迭代步数", "Iteration steps"], min: 1, max: 60, step: 1, value: 3, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["带内的项；二分法", "inside the band; bisection"], color: "#1f77b4" }, { name: ["带外的项（N 之后）", "outside the band (after N)"], color: "#d62728" }, { name: ["迭代 (3.1.1)", "iteration (3.1.1)"], color: "#2ca02c" }],
  tasks: [
    { id: "eps", text: ["在“ε–N 游戏”中选一个收敛的数列，令 ε = 0.01，找到一个可用的 N。", "In 'The ε–N game' pick a convergent sequence, set ε = 0.01 and find a working N."],
      demo: { scene: "game", set: { s: 1, e: 2, N: 120 }, press: [], wait: 1 } },
    { id: "settle", robot: true, text: ["在“关节误差”场景中，把 N 调到调节时间：误差从第 N 步起永远在 ±0.2° 内，而 N − 1 不行。", "In 'Joint error' set N to the settling time: from step N on the error stays within ±0.2°, but N − 1 does not work."],
      demo: { scene: "joint", set: { N: 344 }, press: [], wait: 1 } },
    { id: "sqrt", robot: true, text: ["在“迭代开方”场景中，把步数调到式 (3.1.1) 的误差刚好小于 10⁻¹² 的最少步数，并读出二分法所需的步数。", "In 'Iterative square root' set the steps to the fewest that bring the error of (3.1.1) below 10⁻¹², and read the steps bisection needs."],
      demo: { scene: "iter", set: { a: 2, k: 5 }, press: [], wait: 1 } },
  ],
  think: ["证明里给出的 N 往往比实际需要的大得多（表 3.3.1），这为什么不影响证明？为什么式 (3.1.1) 的误差每步大约平方一次，二分法却每步只减半？",
          "The N given in a proof is often far larger than needed (Table 3.3.1); why does that not spoil the proof? Why does the error of (3.1.1) roughly square at each step while bisection only halves it?"],

  seq(api) {   // the sequence of the scene: a(n), its limit L (NaN if none), and the band half-width
    if (api.scene === "joint") return { a: (n) => 10 * Math.pow(0.99, n) * Math.cos(0.03 * n), L: 0, eps: 0.2, n0: 0, name: "eₖ / (°)" };
    const eps = Math.pow(10, -api.p.e);
    switch (api.p.s) {
      case 1: return { a: (n) => (n % 2 ? -1 : 1) / n, L: 0, eps, n0: 1, name: "(−1)ⁿ/n" };
      case 2: return { a: (n) => (3 * n + 1) / (2 * n - 1), L: 1.5, eps, n0: 1, name: "(3n+1)/(2n−1)" };
      case 3: return { a: (n) => Math.pow(n, 1 / n), L: 1, eps, n0: 1, name: "n^(1/n)" };
      default: return { a: (n) => (n % 2 ? -1 : 1), L: 0, eps, n0: 1, name: "(−1)ⁿ" };
    }
  },
  check(S, N, upto) {   // the last index n > N (n ≤ upto) outside the band, or 0 if none; for (−1)ⁿ the band is tried around 0
    let last = 0;
    for (let n = Math.max(S.n0, N + 1); n <= upto; n++) if (!(Math.abs(S.a(n) - S.L) < S.eps)) last = n;
    return last;
  },
  roots(api) {   // errors of bisection and of (3.1.1) for √a, steps 1…60
    const a = api.p.a, r = Math.sqrt(a), bis = [], her = [];
    let lo = 0, hi = Math.max(1, a), x = Math.max(1, a);
    for (let k = 1; k <= 60; k++) {
      const m = (lo + hi) / 2; if (m * m < a) lo = m; else hi = m;
      bis.push(Math.abs((lo + hi) / 2 - r));
      x = (x + a / x) / 2; her.push(Math.abs(x - r));
    }
    const need = (E) => { const i = E.findIndex((v) => v < 1e-12 * Math.max(1, r)); return i < 0 ? NaN : i + 1; };
    return { bis, her, kb: need(bis), kh: need(her) };
  },
  readouts(api) {
    if (api.scene === "iter") {
      const R = this.roots(api), k = api.p.k;
      if (k === R.kh) api.done("sqrt");
      return [[["√a", "√a"], api.fmt(Math.sqrt(api.p.a), 12)],
              [["第 k 步的误差：二分法 / (3.1.1)", "Error at step k: bisection / (3.1.1)"], api.fmt(R.bis[k - 1], 3) + " / " + api.fmt(R.her[k - 1], 3)],
              [["达到 10⁻¹²（相对）所需步数：二分法 / (3.1.1)", "Steps to 10⁻¹² (relative): bisection / (3.1.1)"], R.kb + " / " + R.kh]];
    }
    const S = this.seq(api), N = api.p.N, upto = api.scene === "joint" ? 3000 : 20000;
    const from = api.scene === "joint" ? N - 1 : N;   // joint: from step N on (inclusive); game: n > N as in definition 3.3.1
    const last = this.check(S, from, upto), ok = last === 0;
    if (api.scene === "game" && ok && api.p.e === 2 && api.p.s !== 4) api.done("eps");
    if (api.scene === "joint" && ok && this.check(S, N - 2, upto) !== 0) api.done("settle");
    return [[["数列", "Sequence"], S.name + (api.scene === "joint" || api.p.s !== 4 ? api.T("，极限 ", ", limit ") + S.L : "")],
            [["误差带", "Band"], (api.scene === "joint" ? "±0.2°" : "ε = " + api.fmt(S.eps, 3))],
            [["N 之后带外的项", "Terms outside after N"], ok ? api.T("没有（检查到第 ", "none (checked to n = ") + upto + api.T(" 项）", ")") : api.T("最后一个在 n = ", "last at n = ") + last],
            [["结论", "Verdict"], ok ? api.T("这个 N 可用", "this N works") : api.T("N 还不够大", "N is not large enough")]];
  },
  draw(api) {
    const w = api.w, h = api.h, red = api.css("--red"), blue = api.css("--blue"), green = api.css("--green"), mu = api.css("--muted");
    if (api.scene === "iter") {
      const R = this.roots(api), lg = (v) => Math.log10(Math.max(v, 1e-17));
      const G = api.graph({ x: 60, y: 20, w: w - 80, h: h - 70, xmin: 0, xmax: 60, ymin: -17, ymax: 3, xlabel: api.T("步数", "step"), ylabel: "lg |error|" });
      G.axes();
      G.pts(R.bis.map((v, i) => [i + 1, lg(v)]), blue, 2); G.dots(R.bis.map((v, i) => [i + 1, lg(v)]), blue, 2.5);
      G.pts(R.her.map((v, i) => [i + 1, lg(v)]), green, 2); G.dots(R.her.map((v, i) => [i + 1, lg(v)]), green, 2.5);
      G.hline(-12, mu); G.vline(api.p.k, red);
      return;
    }
    const S = this.seq(api), N = api.p.N, show = api.scene === "joint" ? 700 : Math.min(12000, Math.max(60, Math.round(N * 2.5)));
    const vals = []; for (let n = S.n0; n <= show; n++) vals.push([n, S.a(n)]);
    const ys = vals.map((v) => v[1]), span = Math.max(...ys.map((y) => Math.abs(y - S.L)), S.eps * 2);
    const G = api.graph({ x: 60, y: 20, w: w - 80, h: h - 70, xmin: 0, xmax: show, ymin: S.L - span * 1.1, ymax: S.L + span * 1.1, xlabel: "n", ylabel: S.name });
    G.axes();
    G.hline(S.L + S.eps, red); G.hline(S.L - S.eps, red); G.vline(N, mu);
    G.dots(vals.filter((v) => v[0] <= N || Math.abs(v[1] - S.L) < S.eps), blue, 2);
    G.dots(vals.filter((v) => v[0] > N && !(Math.abs(v[1] - S.L) < S.eps)), red, 3);
  },
});
