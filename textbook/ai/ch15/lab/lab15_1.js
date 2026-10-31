// 实验 15.1 价值从哪里来（配 15.1 节）。
// 两个场景：
//   value ：看每个格子值多少、最优动作往哪走，调折扣因子、滑移概率与每步代价；
//   iter  ：看价值迭代每一轮的误差怎样按 γ 的幂往下掉。
// 全部在浏览器里现算：5×5 的车间、20 个状态、4 个动作，价值迭代十几轮就收敛。
// 与 code/_ch15.py 是同一套做法与同一张图。
WQ.lab({
  title: ["实验 15.1 小车间里的价值与最优路线", "Lab 15.1 Values and the best route in a small shop"],
  goal: ["亲手调折扣因子、滑移概率与每步代价，看价值图与箭头怎样变。做完能回答三个问题：折扣因子到底在折什么、地面一滑最优路线为什么会绕开、为什么“每步都扣一点”比“只在出口给奖励”更好调。",
         "Turn the discount factor, the slip probability and the step cost, and watch the value map and the arrows change: what the discount really discounts, why a slippery cell makes the best route detour, and why a per-step cost is easier to tune than a goal-only reward."],
  scenes: [
    { id: "value", name: ["价值与路线", "Values and route"],
      problem: { title: ["问题：这个格子值多少", "Problem: what is this cell worth"],
                 text: ["一台 AGV 从入口去出口，中间有设备挡路、有一块油污（走上去会打滑）。每走一步扣 1 分，到出口加 20 分。每个格子“值多少”，就是从它出发、照最优走法走下去能拿到的折扣回报——这就是价值。",
                        "An AGV must get from the entrance to the exit past machines and one oily cell where it may slip. Each step costs 1 and reaching the exit pays 20. A cell's value is the discounted return you can still collect from it under the best policy."] } },
    { id: "iter", name: ["一轮一轮算出来", "Iterating to the answer"],
      problem: { title: ["问题：怎么算出来的", "Problem: how the values are computed"],
                 text: ["价值迭代反复用贝尔曼最优方程更新每个格子。每一轮的变化量大约乘以 γ——这是压缩映射的保证，不是经验。γ 越接近 1，收敛越慢、看得越远。",
                        "Value iteration repeatedly applies the Bellman optimality backup. Each round the change shrinks by about a factor of gamma — a guarantee from the contraction property, not an observation. Closer to 1 means slower convergence and a longer horizon."] } },
  ],
  params: [
    { id: "gamma", name: ["折扣因子 γ", "discount factor"], min: 0.5, max: 0.995, step: 0.005, value: 0.95, digits: 3 },
    { id: "slip", name: ["油污格的滑移概率", "slip probability on the oily cell"], min: 0, max: 0.6, step: 0.05, value: 0.1, digits: 2 },
    { id: "cost", name: ["每走一步扣多少", "cost per step"], min: 0, max: 4, step: 0.5, value: 1, digits: 1 },
    { id: "goal", name: ["到出口给多少", "reward at the exit"], min: 5, max: 50, step: 5, value: 20, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["价值低", "low value"] }, { color: "var(--red)", name: ["价值高", "high value"] }],
  tasks: [
    { id: "base", text: ["按默认设置看一遍：入口的价值是多少？照箭头走到出口要几步？油污格旁边的箭头躲不躲它？",
                         "With the default settings: what is the entrance worth, how many steps to the exit, and do the arrows avoid the oily cell?"],
      demo: { scene: "value", set: { gamma: 0.95, slip: 0.1, cost: 1 }, press: [] } },
    { id: "gamma_low", text: ["把 γ 调到 0.6：入口的价值变成多少？为什么会变成负的？（提示：有效视野约 1/(1−γ) 步。）",
                              "Set gamma to 0.6: what is the entrance worth now, and why does it go negative? (The effective horizon is about 1/(1-gamma) steps.)"],
      demo: { scene: "value", set: { gamma: 0.6 }, press: [] } },
    { id: "slip_high", text: ["把滑移概率调到 0.5：最优路线绕开油污了吗？绕路多走几步，为什么还是划算？",
                              "Raise the slip probability to 0.5: does the best route now detour around the oily cell, and why is the longer route still worth it?"],
      demo: { scene: "value", set: { slip: 0.5 }, press: [] } },
    { id: "iters", text: ["切到“一轮一轮算出来”，把 γ 从 0.6 调到 0.99：收敛要几轮？每一轮的变化量大约乘以多少？",
                          "Switch to the iteration scene and sweep gamma from 0.6 to 0.99: how many rounds to converge, and by what factor does the change shrink each round?"],
      demo: { scene: "iter", set: { gamma: 0.99 }, press: [] } },
  ],
  think: ["把“每步扣 1 分”改成 0 分（只有到出口才给奖励），价值图会变成什么样？这时候还看得出“哪条路更短”吗？",
          "Set the per-step cost to zero so that only the exit pays. What happens to the value map, and can you still tell which route is shorter?"],

  SHOP: ["S....", ".##..", "..#o.", ".#...", "..#.G"],
  ACTIONS: [[-1, 0], [1, 0], [0, -1], [0, 1]],
  ARROWS: ["↑", "↓", "←", "→"],
  build(slip, cost, goalR) {
    const g = this.SHOP.map((r) => r.split(""));
    const H = g.length, W = g[0].length, free = [], idx = {};
    for (let i = 0; i < H; i++) for (let j = 0; j < W; j++) if (g[i][j] !== "#") { idx[i + "," + j] = free.length; free.push([i, j]); }
    const n = free.length, na = 4;
    const P = Array.from({ length: n }, () => Array.from({ length: na }, () => new Float64Array(n)));
    const R = Array.from({ length: n }, () => new Float64Array(na));
    const goal = free.findIndex(([i, j]) => g[i][j] === "G");
    free.forEach(([i, j], s) => {
      if (s === goal) { for (let a = 0; a < na; a++) P[s][a][s] = 1; return; }
      const oily = g[i][j] === "o";
      for (let a = 0; a < na; a++) {
        const moves = {};
        moves[a] = 1 - (oily ? slip : 0);
        if (oily) for (let b = 0; b < na; b++) moves[b] = (moves[b] || 0) + slip / na;
        for (const b of Object.keys(moves)) {
          const [di, dj] = this.ACTIONS[+b];
          let ni = i + di, nj = j + dj;
          if (ni < 0 || ni >= H || nj < 0 || nj >= W || g[ni][nj] === "#") { ni = i; nj = j; }
          const s2 = idx[ni + "," + nj];
          P[s][a][s2] += moves[b];
          R[s][a] += moves[b] * (s2 === goal ? goalR : -cost);
        }
      }
    });
    return { P, R, free, idx, g, H, W, goal, n };
  },
  solve(m, gamma) {
    const { P, R, n } = m, na = 4;
    let V = new Float64Array(n);
    const deltas = [];
    for (let k = 0; k < 400; k++) {
      const V2 = new Float64Array(n), pi = new Int32Array(n);
      for (let s = 0; s < n; s++) {
        let best = -Infinity, ba = 0;
        for (let a = 0; a < na; a++) {
          let q = R[s][a];
          for (let s2 = 0; s2 < n; s2++) if (P[s][a][s2]) q += gamma * P[s][a][s2] * V[s2];
          if (q > best) { best = q; ba = a; }
        }
        V2[s] = best; pi[s] = ba;
      }
      let d = 0;
      for (let s = 0; s < n; s++) d = Math.max(d, Math.abs(V2[s] - V[s]));
      V = V2; deltas.push(d);
      if (d < 1e-10) { return { V, pi, deltas, iters: k + 1 }; }
    }
    return { V, pi: new Int32Array(n), deltas, iters: 400 };
  },
  calc(api) {
    const p = api.p, key = [p.gamma, p.slip, p.cost, p.goal].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const m = this.build(p.slip, p.cost, p.goal);
    const sol = this.solve(m, p.gamma);
    // 照最优策略从入口走到出口要几步，路上经不经过油污
    const start = m.free.findIndex(([i, j]) => m.g[i][j] === "S");
    let s = start, steps = 0, oily = false;
    while (s !== m.goal && steps < 200) {
      const a = sol.pi[s];
      let bs = s, bp = -1;
      for (let s2 = 0; s2 < m.n; s2++) if (m.P[s][a][s2] > bp) { bp = m.P[s][a][s2]; bs = s2; }
      s = bs; steps++;
      const [i, j] = m.free[s];
      if (m.g[i][j] === "o") oily = true;
    }
    const ratio = sol.deltas.length > 8 ? sol.deltas[7] / Math.max(sol.deltas[6], 1e-12) : NaN;
    const val = { m, sol, start, steps, oily, ratio, horizon: 1 / (1 - p.gamma) };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const p = api.p, c = this.calc(api);
    if (api.scene === "value" && Math.abs(p.gamma - 0.95) < 1e-9 && Math.abs(p.slip - 0.1) < 1e-9) api.done("base");
    if (api.scene === "value" && p.gamma <= 0.6 + 1e-9) api.done("gamma_low");
    if (api.scene === "value" && p.slip >= 0.5 - 1e-9) api.done("slip_high");
    if (api.scene === "iter" && p.gamma >= 0.99 - 1e-9) api.done("iters");
    if (api.scene === "value") {
      return [[["入口的价值", "value at the entrance"], c.sol.V[c.start].toFixed(2)],
              [["最高的那个格子", "highest cell"], Math.max(...c.sol.V).toFixed(2)],
              [["照箭头走到出口", "steps to the exit"], c.steps + api.T(" 步", " steps")],
              [["路上经过油污吗", "does the route cross the oil?"], c.oily ? api.T("经过", "yes") : api.T("绕开了", "no")],
              [["有效视野 1/(1−γ)", "effective horizon"], c.horizon.toFixed(1) + api.T(" 步", " steps")]];
    }
    return [[["收敛用了几轮", "rounds to converge"], String(c.sol.iters)],
            [["第一轮变了多少", "change in round 1"], c.sol.deltas[0].toFixed(2)],
            [["第八轮比第七轮", "round 8 over round 7"], isFinite(c.ratio) ? c.ratio.toFixed(3) : "—"],
            [["γ", "gamma"], p.gamma.toFixed(3)],
            [["入口的价值", "value at the entrance"], c.sol.V[c.start].toFixed(2)]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api), m = c.m;
    const x0 = 60, y0 = 24, pw = w - x0 - 40, ph = h - y0 - 44;
    if (api.scene === "value") {
      const cell = Math.min(pw / m.W, ph / m.H) * 0.92, ox = x0 + (pw - cell * m.W) / 2, oy = y0;
      const vals = Array.from(c.sol.V), lo = Math.min(...vals), hi = Math.max(...vals);
      for (let i = 0; i < m.H; i++) for (let j = 0; j < m.W; j++) {
        const px = ox + j * cell, py = oy + i * cell;
        if (m.g[i][j] === "#") { api.rect(px, py, cell, cell, api.css("--grid"), null, 0); continue; }
        const sIdx = m.idx[i + "," + j], v = c.sol.V[sIdx];
        const u = (v - lo) / Math.max(hi - lo, 1e-9);
        api.rect(px, py, cell, cell, `rgba(${Math.round(60 + 170 * u)},${Math.round(130 - 70 * u)},${Math.round(200 - 150 * u)},0.85)`, null, 0);
        api.rect(px, py, cell, cell, null, api.css("--grid"), 1);
        api.label(v.toFixed(1), px + 6, py + 16, "#fff", 12);
        if (sIdx === m.goal) { api.label(api.T("出口", "exit"), px + cell / 2 - 14, py + cell / 2 + 6, "#fff", 13); continue; }
        api.label(this.ARROWS[c.sol.pi[sIdx]], px + cell / 2 - 7, py + cell / 2 + 10, "#fff", 22);
        if (m.g[i][j] === "o") api.label(api.T("油污", "oil"), px + cell - 34, py + cell - 6, "#ffe", 11);
        if (m.g[i][j] === "S") api.label(api.T("入口", "start"), px + 4, py + cell - 6, "#ffe", 11);
      }
      return;
    }
    const d = c.sol.deltas, lo = -4, hi = Math.log10(Math.max(d[0], 1));
    const X = (k) => x0 + k / Math.max(d.length - 1, 1) * pw;
    const Y = (v) => y0 + ph - (Math.max(Math.log10(Math.max(v, 1e-12)), lo) - lo) / (hi - lo) * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    for (let e = lo; e <= hi; e++) { api.line(x0, Y(Math.pow(10, e)), x0 + pw, Y(Math.pow(10, e)), api.css("--grid"), 1);
      api.label("1e" + e, 14, Y(Math.pow(10, e)) + 4, api.css("--muted"), 11); }
    let prev = null;
    d.forEach((v, k) => { const cur = [X(k), Y(v)]; if (prev) api.line(prev[0], prev[1], cur[0], cur[1], api.css("--blue"), 2.2);
      api.circle(cur[0], cur[1], 3, null, api.css("--blue")); prev = cur; });
    // 参照线：第一轮的变化量乘以 γ 的 k 次方
    let p2 = null;
    for (let k = 0; k < d.length; k++) { const cur = [X(k), Y(d[0] * Math.pow(api.p.gamma, k))];
      if (p2) api.line(p2[0], p2[1], cur[0], cur[1], api.css("--muted"), 1.4, [5, 4]); p2 = cur; }
    api.label(api.T("每一轮变了多少（对数）", "change per round (log)"), 10, y0 + 12, api.css("--muted"), 12);
    api.label(api.T(`虚线是 ${d[0].toFixed(1)}·γ^k`, `dashed: ${d[0].toFixed(1)}·γ^k`), x0 + pw - 150, y0 + 16, api.css("--muted"), 12);
    api.label(api.T("迭代轮数", "iteration"), x0 + pw / 2 - 24, h - 12, api.css("--muted"), 12);
  },
});
