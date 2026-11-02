// 实验 19.1 格子跟不跟得上、初值差一点点（配 19.1 节）。
// 两个场景：
//   grid  ：一维平流。拖库朗数、换格式，看显式格式在哪一步炸、半拉格朗日为什么不炸；
//   chaos ：两条只差一点点的轨迹，看“还能信多久”随初值精度怎么长。
// 与 code/_ch19.py 是同一套算法（advect_upwind、advect_semilagrangian、lorenz_run）。
WQ.lab({
  title: ["实验 19.1 两道硬墙：格子与混沌", "Lab 19.1 Two hard walls: the grid and chaos"],
  goal: ["亲手把时间步调大，看显式格式在第几步炸；再把同一个库朗数交给业务模式用的那种格式，看它为什么不炸、换来的是什么。然后把初值误差缩小一千倍，看“还能信多久”只多出几个时间单位。做完能回答：CFL 约束是谁的约束、提高初值精度的回报为什么是对数的。",
         "Push the timestep up and watch an explicit scheme blow up, then hand the same Courant number to the kind of scheme operational models use. Then shrink the initial error a thousandfold and see how little extra lead time it buys. You should be able to say whose constraint CFL is, and why better initial data pays off only logarithmically."],
  scenes: [
    { id: "grid", name: ["格子跟不跟得上", "Can the grid keep up"],
      problem: { title: ["问题：时间步能调多大", "Problem: how long can a timestep be"],
                 text: ["把大气切成格子，一个时间步把信息往前送 uΔt。显式格式算新值时只看自己和邻居，所以信息一步**不能跨过一个格距**：库朗数 C = uΔt/Δx 一旦超过 1，解就指数放大。想把时间步调大一倍，格距也得跟着减半，三维再加上时间，总开销涨十几倍——这就是“算得慢”的真正来由。半拉格朗日格式换了个做法：沿轨迹回溯到上游点再插值，回溯多远都行，于是它不受这条约束。",
                        "Cut the atmosphere into cells: one timestep carries information a distance uΔt. An explicit scheme looks only at a cell and its neighbours, so information may not cross more than one cell per step — once the Courant number C = uΔt/Δx passes 1, the solution amplifies exponentially. Doubling the timestep means halving the spacing, and in three dimensions plus time the total cost rises by more than an order of magnitude. A semi-Lagrangian scheme traces back along the trajectory and interpolates instead, so no such limit applies."] } },
    { id: "chaos", name: ["初值差一点点", "A tiny difference in the initial state"],
      problem: { title: ["问题：提高初值精度能多买回多少时间", "Problem: what better initial data buys"],
                 text: ["大气是混沌的：两个几乎一样的初值，误差按指数增长。于是“还能信多久”与初值精度的**对数**成正比——精度提高十倍，只多买回一个翻倍时间。观测再密、同化再好，这条墙也只能往后挪一点点，挪不掉。这就是为什么中期预报到了某个天数之后，谁做都做不准。",
                        "The atmosphere is chaotic: two nearly identical initial states diverge exponentially. Useful lead time therefore grows with the logarithm of initial accuracy — ten times better data buys one more doubling time. Denser observations and better assimilation push the wall back a little; they cannot remove it."] } },
  ],
  params: [
    { id: "c", name: ["库朗数 C = uΔt/Δx", "Courant number C = uΔt/Δx"], min: 0.2, max: 2.5, step: 0.05, value: 0.8, digits: 2 },
    { id: "scheme", name: ["0 = 显式迎风，1 = 半拉格朗日", "0 = explicit upwind, 1 = semi-Lagrangian"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "nstep", name: ["走了多少步", "steps taken"], min: 0, max: 60, step: 1, value: 20, digits: 0 },
    { id: "eexp", name: ["初值误差 = 10 的几次方", "initial error = 10 to the power"], min: -5, max: -1, step: 1, value: -2, digits: 0 },
    { id: "tmax", name: ["往前推多久（无量纲）", "how far ahead (dimensionless)"], min: 2, max: 20, step: 1, value: 12, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["这一步的场 / 轨迹甲", "field now / trajectory A"] },
           { color: "var(--muted)", name: ["出发时的场", "the field we started from"] },
           { color: "var(--red)", name: ["已经炸了 / 轨迹乙", "blown up / trajectory B"] },
           { color: "var(--green)", name: ["还能信的那一段", "the stretch still worth trusting"] }],
  tasks: [
    { id: "stable", text: ["显式格式、库朗数 0.9，走满 60 步：峰值掉到了多少？它没炸，可形状也不对了——这叫数值耗散，记下峰值。",
                           "Explicit scheme at Courant 0.9, 60 steps: how far has the peak fallen? It did not blow up, but the shape is wrong — that is numerical dissipation. Record the peak."],
      demo: { scene: "grid", set: { scheme: 0, c: 0.9, nstep: 60 }, press: [] } },
    { id: "blow", text: ["把库朗数调到 1.2：从第几步起峰值超过 10？再调到 1.5 试一次，是晚了还是早了？",
                         "Raise it to 1.2: at which step does the peak pass 10? Try 1.5 — sooner or later?"],
      demo: { scene: "grid", set: { scheme: 0, c: 1.2, nstep: 40 }, press: [] } },
    { id: "semi", text: ["库朗数不动（1.2 或更大），把格式换成半拉格朗日：还炸吗？它付出的是什么代价——比一比峰值。",
                         "Keep the Courant number and switch to semi-Lagrangian: does it blow up? Compare the peaks to see what it pays instead."],
      demo: { scene: "grid", set: { scheme: 1, c: 1.2, nstep: 40 }, press: [] } },
    { id: "lead1", text: ["切到第二个场景，初值误差 10⁻²，按“开始”看两条轨迹分开：记下“还能信多久”。",
                          "Switch to the second scene with an initial error of 10⁻², press start and record the useful lead time."],
      demo: { scene: "chaos", set: { eexp: -2, tmax: 14 }, press: ["start"] } },
    { id: "lead2", text: ["把初值误差缩到 10⁻⁵（小一千倍）：还能信多久变成了几倍？一千倍精度换来几个时间单位？",
                          "Shrink the error to 10⁻⁵ — a thousandfold — and see what the lead time becomes. How many time units did a factor of a thousand buy?"],
      demo: { scene: "chaos", set: { eexp: -5, tmax: 16 }, press: ["start"] } },
  ],
  think: ["把观测加密一倍，初值误差大致能小一半。按本实验量到的增长速度，这能让“还能信多久”多出多少？如果有人说“再加一倍观测就能把预报做到两周”，你用哪个数反驳他？",
          "Doubling the observing network roughly halves the initial error. Using the growth rate you measured, how much lead time does that add? If someone claims that twice the observations would push forecasts to two weeks, which number refutes them?"],

  NX: 160,
  bump() { const u = []; for (let i = 0; i < this.NX; i++) u.push(Math.exp(-Math.pow(i - 40, 2) / 2.5)); return u; },
  upwind(u, c) { const n = u.length, o = new Array(n); for (let i = 0; i < n; i++) o[i] = u[i] - c * (u[i] - u[(i - 1 + n) % n]); return o; },
  semi(u, c) {
    const n = u.length, o = new Array(n);
    for (let i = 0; i < n; i++) {
      const src = i - c, lo = Math.floor(src), w = src - lo;
      o[i] = (1 - w) * u[((lo % n) + n) % n] + w * u[(((lo + 1) % n) + n) % n];
    }
    return o;
  },
  maxAbs(a) { let m = 0; for (const v of a) { const x = Math.abs(v); if (x > m) m = x; } return m; },

  lorenz(s, dt) {
    const f = (v) => [10 * (v[1] - v[0]), v[0] * (28 - v[2]) - v[1], v[0] * v[1] - 8 / 3 * v[2]];
    const add = (a, b, k) => [a[0] + k * b[0], a[1] + k * b[1], a[2] + k * b[2]];
    const k1 = f(s), k2 = f(add(s, k1, dt / 2)), k3 = f(add(s, k2, dt / 2)), k4 = f(add(s, k3, dt));
    return [0, 1, 2].map((i) => s[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + 2 * k4[i]));
  },
  DT: 0.01, TOL: 2.0,

  // 平流：算到第 nstep 步，并记下第一次峰值过 10 的那一步
  runGrid(c, scheme, nstep) {
    const key = [c, scheme, nstep].join(",");
    if (this._g && this._g.key === key) return this._g.val;
    let u = this.bump(); const peaks = [this.maxAbs(u)]; let first = null;
    for (let k = 1; k <= nstep; k++) {
      u = scheme ? this.semi(u, c) : this.upwind(u, c);
      const pk = this.maxAbs(u);
      peaks.push(Math.min(pk, 1e30));
      if (first === null && pk > 10) first = k;
    }
    const val = { u, peaks, first, blown: this.maxAbs(u) > 10 };
    this._g = { key, val };
    return val;
  },
  // 混沌：两条轨迹与它们的距离
  // 一条轨迹对：起点由 j 决定（j = 0 是画出来的那一条）
  pair(eps, n, j) {
    let s = [1 + 0.37 * j, 1 - 0.21 * j, 25 + 0.11 * j];
    for (let i = 0; i < 2000; i++) s = this.lorenz(s, this.DT);
    const d0 = [Math.cos(j), Math.sin(j), Math.cos(2 * j)];
    const nn = Math.sqrt(d0[0] * d0[0] + d0[1] * d0[1] + d0[2] * d0[2]);
    let a = s.slice(), b = [0, 1, 2].map((i) => s[i] + eps * d0[i] / nn);
    const A = [a.slice()], B = [b.slice()], E = [eps];
    let lead = null;
    for (let i = 1; i <= n; i++) {
      a = this.lorenz(a, this.DT); b = this.lorenz(b, this.DT);
      A.push(a.slice()); B.push(b.slice());
      const d = Math.sqrt(Math.pow(a[0] - b[0], 2) + Math.pow(a[1] - b[1], 2) + Math.pow(a[2] - b[2], 2));
      E.push(d);
      if (lead === null && d > this.TOL) lead = i * this.DT;
    }
    return { A, B, E, lead };
  },
  // 画第一对，"还能信多久"取 12 对的平均——单看一对太抖，看不出"一个数量级买回两个时间单位"
  runChaos(eps, tmax) {
    const key = [eps, tmax].join(",");
    if (this._h && this._h.key === key) return this._h.val;
    const n = Math.round(tmax / this.DT);
    const first = this.pair(eps, n, 0);
    let sum = 0;
    for (let j = 0; j < 12; j++) { const r = this.pair(eps, n, j); sum += r.lead === null ? n * this.DT : r.lead; }
    const val = { A: first.A, B: first.B, E: first.E, n, lead: first.lead, mean: sum / 12 };
    this._h = { key, val };
    return val;
  },

  reset(api, s) { s.frame = 0; },
  update(dt, api, s) {
    const r = this.runChaos(Math.pow(10, Math.round(api.p.eexp)), Math.round(api.p.tmax));
    if (api.scene !== "chaos") { api.stop(); return; }
    s.frame = (s.frame || 0) + dt * r.n / 6;         // 六秒走完全程
    if (s.frame >= r.n) { s.frame = r.n; api.stop(); }
  },
  readouts(api, s) {
    const q = api.p;
    if (api.scene === "grid") {
      const c = +q.c.toFixed(2), sc = Math.round(q.scheme), ns = Math.round(q.nstep);
      const r = this.runGrid(c, sc, ns);
      if (sc === 0 && c <= 0.95 && ns >= 60 && !r.blown) api.done("stable");
      if (sc === 0 && c >= 1.15 && r.blown) api.done("blow");
      if (sc === 1 && c >= 1.15 && ns >= 30 && !r.blown) api.done("semi");
      return [[["用的是哪种格式", "which scheme"],
               sc ? api.T("半拉格朗日", "semi-Lagrangian") : api.T("显式迎风", "explicit upwind")],
              [["这一步的峰值（出发时是 1）", "peak now (it started at 1)"],
               r.peaks[ns] >= 1e6 ? r.peaks[ns].toExponential(2) : r.peaks[ns].toFixed(4)],
              [["第几步峰值过 10", "step at which the peak passes 10"],
               r.first === null ? api.T("一直没过", "never") : String(r.first)],
              [["稳不稳", "stable?"],
               r.blown ? api.T("已经炸了", "blown up") : api.T("有界", "bounded")]];
    }
    const eps = Math.pow(10, Math.round(q.eexp)), r = this.runChaos(eps, Math.round(q.tmax));
    const i = Math.min(r.n, Math.round(s.frame || r.n));
    if (eps >= 0.01 && (s.frame || 0) >= r.n * 0.9) api.done("lead1");
    if (eps <= 1e-5 && (s.frame || 0) >= r.n * 0.9) api.done("lead2");
    return [[["初值误差", "initial error"], eps.toExponential(0)],
            [["现在推到了", "now at"], (i * this.DT).toFixed(2)],
            [["两条轨迹差多少", "distance between the two"], r.E[i].toExponential(2)],
            [["这一对还能信多久（误差到 2 为止）", "this pair: lead time until the error reaches 2"],
             r.lead === null ? api.T(`超过 ${(r.n * this.DT).toFixed(0)}`, `beyond ${(r.n * this.DT).toFixed(0)}`)
                             : r.lead.toFixed(2)],
            [["12 对的平均", "averaged over 12 pairs"], r.mean.toFixed(2)]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p;
    if (api.scene === "grid") {
      const c = +q.c.toFixed(2), sc = Math.round(q.scheme), ns = Math.round(q.nstep);
      const r = this.runGrid(c, sc, ns);
      const pk = Math.max(1.2, Math.min(r.peaks[ns] * 1.15, 1e6));
      const g = api.graph({ x: 46, y: 24, w: w * 0.54, h: h - 72, xmin: 0, xmax: this.NX,
                            ymin: -pk, ymax: pk,
                            xlabel: api.T("格点", "grid point"), ylabel: api.T("场的数值", "field value") }).axes();
      const base = this.bump();
      g.pts(base.map((v, i) => [i, v]), api.css("--muted"), 1.5, [4, 4]);
      g.pts(r.u.map((v, i) => [i, Math.max(-pk, Math.min(pk, v))]),
            api.css(r.blown ? "--red" : "--blue"), 2.4);
      api.label(api.T(`${sc ? "半拉格朗日" : "显式迎风"}，C = ${c.toFixed(2)}，第 ${ns} 步`,
                      `${sc ? "semi-Lagrangian" : "explicit upwind"}, C = ${c.toFixed(2)}, step ${ns}`),
                46, 16, api.css("--ink"), 13);
      // 右边：峰值随步数怎么走（对数）
      const lg = (v) => Math.log10(Math.max(v, 1e-6));
      const top = Math.max(1, lg(this.maxAbs(r.peaks)));
      const g2 = api.graph({ x: w * 0.64, y: 24, w: w * 0.32, h: h - 72, xmin: 0, xmax: Math.max(10, ns),
                             ymin: -2, ymax: Math.max(1, top + 0.5),
                             xlabel: api.T("步数", "steps"),
                             ylabel: api.T("峰值（10 的几次方）", "peak (powers of 10)") }).axes();
      g2.hline(1, api.css("--muted"));
      g2.pts(r.peaks.map((v, i) => [i, lg(v)]), api.css(r.blown ? "--red" : "--blue"), 2.2);
      if (r.first !== null) g2.vline(r.first, api.css("--red"));
      return;
    }
    const eps = Math.pow(10, Math.round(q.eexp)), r = this.runChaos(eps, Math.round(q.tmax));
    const i = Math.min(r.n, Math.round(s.frame || r.n));
    const g = api.graph({ x: 46, y: 24, w: w * 0.5, h: h - 72, xmin: -22, xmax: 22, ymin: 0, ymax: 50,
                          xlabel: "x", ylabel: "z" }).axes();
    const sub = (P) => { const o = []; for (let k = 0; k <= i; k += 4) o.push([P[k][0], P[k][2]]); return o; };
    g.pts(sub(r.A), api.css("--blue"), 1.6);
    g.pts(sub(r.B), api.css("--red"), 1.6);
    g.point(r.A[i][0], r.A[i][2], api.css("--blue"));
    g.point(r.B[i][0], r.B[i][2], api.css("--red"));
    const g2 = api.graph({ x: w * 0.62, y: 24, w: w * 0.34, h: h - 72, xmin: 0, xmax: r.n * this.DT,
                           ymin: -6, ymax: 2,
                           xlabel: api.T("时间", "time"),
                           ylabel: api.T("两条轨迹差多少（10 的几次方）", "separation (powers of 10)") }).axes();
    g2.hline(Math.log10(this.TOL), api.css("--red"));
    const pts = [];
    for (let k = 0; k <= i; k++) pts.push([k * this.DT, Math.log10(Math.max(r.E[k], 1e-9))]);
    g2.pts(pts, api.css("--blue"), 2.0);
    if (r.lead !== null) {
      g2.vline(r.lead, api.css("--green"));
      g2.seg(0, -5.6, Math.min(r.lead, i * this.DT), -5.6, api.css("--green"), 4);
      g2.text(api.T(`还能信到 ${r.lead.toFixed(2)}`, `trustworthy to ${r.lead.toFixed(2)}`),
              0.2, -5.0, api.css("--green"), 12);
    }
  },
});
