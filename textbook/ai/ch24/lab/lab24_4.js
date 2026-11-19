// 实验 24.4 奖励塑形的副作用（配 24.4 节；与算例 24.4 同一套玩具，是第 20、21 章那条规矩的回声）。
// 两个场景：
//   shaping ：扫塑形权重，看**累计奖励一路升、真实成功率跳到 0** 这条背离；
//   fix     ：把“贴着工件转、永不闭合夹爪”这个动作**禁掉**，同样扫一遍权重。
// 与 code/_ch24.py 同口径：平面二连杆 + 腕关节，成功判据 **位置 2 cm 且 姿态 0.4 rad**，
// 成功的那一刻是**夹爪闭合的那一刻**——走到位不闭合不算，闭合了没到位也不算。
// 策略族只有两个参数（触发闭合的半径 close_at，取 0 就是永不闭合；绕着工件打转的幅度 hover），
// 每个权重下都把**累计奖励最高**的那一版挑出来——这就是“优化器会做的事”。
// 本章硬口径：凡报成绩都分**仿真**与**真机**两列，并写明真机试了多少次。
WQ.lab({
  title: ["实验 24.4 奖励一路上升，机器人却一次也没抓住",
          "Lab 24.4 The reward keeps climbing while the robot stops grasping altogether"],
  goal: ["第一个场景里把塑形权重从 0 一点一点拖大。一开始它只是让学习快一点：奖励升、成功率不动。拖过某个值之后，“累计奖励最高的那一版”忽然换了行为——它贴着工件来回转，**永远不闭合夹爪**，因为闭合会结束回合，等于主动放弃后面每一步的塑形奖励。这时奖励曲线还在往上走，真实成功率已经掉到 0。你要找出这个临界权重，并把它和读数里“任务分摊到每步”那个数比一比。然后改任务奖励、改回合步数，看临界权重跟着谁动。第二个场景把刷分的那个动作禁掉，再扫一遍同样的权重，看成功率还掉不掉。做完要能回答：验收一个强化学习策略，该看哪条曲线。",
         "In the first scene widen the shaping weight from zero. At first it only speeds learning up: the reward rises and the success rate does not move. Past a certain value the reward-maximising policy changes behaviour altogether — it circles the part and never closes the gripper, because closing ends the episode and gives up every later step of shaping reward. The reward curve is still climbing while the true success rate has fallen to zero. Find that critical weight and compare it with the 'task bonus per step' readout, then change the bonus and the episode length and see which one it tracks. In the second scene the reward-farming action is forbidden and the same sweep is run again. You should be able to say which curve belongs on an acceptance report."],
  scenes: [
    { id: "shaping", name: ["扫塑形权重", "Sweep the shaping weight"],
      problem: { title: ["问题：加一点“离得越近给越多”，会出什么事", "Problem: what happens when you reward getting closer?"],
                 text: ["到达并抓取这个任务，真实目标只有一个：**夹爪闭合的那一刻落在双阈值里**（位置 2 cm、姿态 0.4 rad），抓成一次给任务分。可只给这一个分，学起来太慢——工程上常加一个塑形项：离目标越近，每一步都给一点奖励。塑形项本身没错，错在**它会改变最优行为**。这个场景让你亲手把权重拖大，并把“累计奖励最高的那一版”的奖励与它的真实成功率并排放着看。",
                        "The real goal of this reach-and-grasp task is single: at the instant the gripper closes, be within 2 cm and 0.4 rad. But that one sparse bonus learns slowly, so engineers add a shaping term that pays a little every step for being closer. The shaping term is not wrong in itself; what is wrong is that it changes which behaviour is optimal. Drag the weight here and watch the reward of the best-scoring policy next to its true success rate."] } },
    { id: "fix", name: ["禁掉刷分的动作", "Forbid the reward-farming action"],
      problem: { title: ["问题：怎么防", "Problem: how do you stop it?"],
                 text: ["发现刷奖励之后，第一反应往往是回去调权重。可权重是调不干净的：换个任务、换条生产线，临界值就变了。真正管用的是另外两件事：**验收看真实任务判据，不看奖励**；**把“必须完成”写成硬约束或终止条件，别只写在奖励里**。这个场景就做第二件事——把“永不闭合夹爪”这个动作从策略族里去掉（本场景强制禁掉，上面那个开关不起作用），然后把同样的权重再扫一遍。",
                        "The first instinct after spotting reward farming is to go back and retune the weight, but weights cannot be tuned clean: change the task or the line and the critical value moves. Two other things work: judge acceptance on the real task criterion rather than the reward, and write 'must finish' into a hard constraint or a termination condition instead of only into the reward. This scene does the second: the never-close action is removed from the policy family (forced off here, whatever the switch says) and the same sweep is run again."] } },
  ],
  params: [
    { id: "w", name: ["塑形权重", "shaping weight"], min: 0, max: 2.4, step: 0.05, value: 0.4, digits: 2 },
    { id: "bonus", name: ["抓成一次的任务分", "task bonus for one grasp"], min: 5, max: 60, step: 5, value: 20, digits: 0 },
    { id: "d0", name: ["塑形项的尺度（cm）", "shaping length scale (cm)"], min: 1, max: 8, step: 0.5, value: 3, digits: 1 },
    { id: "steps", name: ["一回合最多多少步", "steps allowed in one episode"], min: 30, max: 90, step: 10, value: 60, digits: 0 },
    { id: "allow", name: ["允许“贴着工件转、永不闭合”（0/1）", "allow the never-close action (0/1)"], min: 0, max: 1, step: 1, value: 1, digits: 0 },
  ],
  legend: [{ color: "var(--amber)", name: ["累计奖励（归一化）", "cumulative reward (normalised)"] },
           { color: "var(--blue)", name: ["仿真成功率", "success in simulation"] },
           { color: "var(--red)", name: ["真机成功率", "success on hardware"] },
           { color: "var(--green)", name: ["你现在这一档", "where you are now"] }],
  tasks: [
    { id: "base", text: ["第一个场景，权重 0（只有任务分）：读数里“奖励最高的那一版”选的是什么参数？它的仿真与真机成功率各是多少？",
                         "In the first scene with weight 0, what parameters does the reward-maximising policy use, and what are its two success rates?"],
      demo: { scene: "shaping", set: { w: 0, bonus: 20, d0: 3, steps: 60, allow: 1 }, press: [] } },
    { id: "rise", text: ["把权重拖到 0.8：累计奖励涨了多少？成功率动了吗？这一段里塑形项干的是“好事”还是“坏事”？",
                         "Raise the weight to 0.8: how much has the reward grown, has the success rate moved, and is the shaping term helping or hurting here?"],
      demo: { scene: "shaping", set: { w: 0.8, bonus: 20, d0: 3, steps: 60, allow: 1 }, press: [] } },
    { id: "farm", text: ["继续拖到 1.2：奖励最高的那一版的触发半径变成多少？两列成功率各是多少？只看奖励曲线验收，你会得出什么结论？",
                         "Push to 1.2: what is the winning policy's closing radius now, what are the two success rates, and what would an acceptance test based on the reward curve conclude?"],
      demo: { scene: "shaping", set: { w: 1.2, bonus: 20, d0: 3, steps: 60, allow: 1 }, press: [] } },
    { id: "scale", text: ["把任务分从 20 改到 40（权重先放回 0.4 再往上找）：临界权重跟着变成多少？它和读数里“任务分摊到每步”差多少？",
                          "Change the task bonus from 20 to 40 and find the critical weight again: what is it now, and how does it compare with the 'bonus per step' readout?"],
      demo: { scene: "shaping", set: { bonus: 40, w: 1.6, d0: 3, steps: 60, allow: 1 }, press: [] } },
    { id: "fixed", text: ["切到第二个场景（刷分动作被禁掉），把权重一直拖到 2.4：成功率还掉吗？读数里“各权重里成功率最低的一档”是多少？",
                          "Move to the second scene, where the farming action is forbidden, and push the weight to 2.4: does the success rate still collapse, and what is the worst weight's success rate?"],
      demo: { scene: "fix", set: { w: 2.4, bonus: 20, d0: 3, steps: 60, allow: 1 }, press: [] } },
  ],
  think: ["把你们自己那条产线上的“完成”写成一句可以验收的话：什么位置、什么姿态、什么力、保持多久。写完再回头看你们的奖励函数或考核指标里有没有一条路，能在不满足这句话的前提下把分刷高。有就把那条路堵死（硬约束、终止条件、或者干脆从动作空间里去掉），而不是去调权重——本实验第二个场景告诉你，堵死之后权重再怎么调都不至于归零。",
          "Write down what 'finished' means on your own line as a sentence you could accept against: what position, what orientation, what force, held for how long. Then look at your reward function or your KPI and ask whether there is a way to score high without satisfying that sentence. If there is, block it — a hard constraint, a termination condition, or removing it from the action space — rather than retuning the weight. The second scene shows that once it is blocked, no weight drives the success rate to zero."],

  // ---------------- 同口径的玩具（与 code/_ch24.py 一致）
  L1S: 0.35, L2S: 0.30, DT: 0.05, VMAX: 1.6, GAIN: 3.5, TOLP: 0.02, TOLR: 0.4,
  QMIN: [-2.6, -2.5, -2.2], QMAX: [2.6, 2.5, 2.2], QHOME: [0.55, 0.95, -0.30],
  SIMW: { l1: 0.35, l2: 0.30, fric: 0.04, noise: 0, delay: 0 },
  REALW: { l1: 0.363, l2: 0.288, fric: 0.11, noise: 0.004, delay: 1 },
  CLOSE_AT: [0, 0.006, 0.012, 0.020],     // 触发闭合的半径（m）；**0 = 永不闭合，就是刷奖励那一版**
  HOVER: [0, 0.4, 0.9],                   // 绕着工件打转的幅度
  NEP: 20,                                // 每一版试多少回合（两列都是这个数）
  WGRID: [0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.6, 2.0, 2.4],

  rng(seed) { let x = (seed * 1103515245 + 12345) >>> 0; return () => { x = (x * 1103515245 + 12345) >>> 0; return x / 4294967296; }; },
  gauss(r) { const u = Math.max(r(), 1e-9), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  fk(q, l1, l2) {
    return [l1 * Math.cos(q[0]) + l2 * Math.cos(q[0] + q[1]),
            l1 * Math.sin(q[0]) + l2 * Math.sin(q[0] + q[1]), q[0] + q[1] + q[2]];
  },
  ik(p, l1, l2) {
    const c2 = (p[0] * p[0] + p[1] * p[1] - l1 * l1 - l2 * l2) / (2 * l1 * l2);
    if (c2 < -1 || c2 > 1) return null;
    const q2 = Math.acos(c2);
    const q1 = Math.atan2(p[1], p[0]) - Math.atan2(l2 * Math.sin(q2), l1 + l2 * Math.cos(q2));
    const q = [q1, q2, p[2] - q1 - q2];
    for (let i = 0; i < 3; i++) if (q[i] < this.QMIN[i] || q[i] > this.QMAX[i]) return null;
    return q;
  },
  targets() {
    if (this._tg) return this._tg;
    const r = this.rng(21), out = [];
    while (out.length < this.NEP) {
      const rad = 0.30 + 0.26 * r(), a = -0.35 + 1.60 * r(), th = -0.9 + 2.8 * r();
      const p = [rad * Math.cos(a), rad * Math.sin(a), th];
      if (this.ik(p, this.L1S, this.L2S) && this.ik(p, this.REALW.l1, this.REALW.l2)) out.push(p);
    }
    this._tg = out;
    return out;
  },
  episode(p, W, closeAt, hover, steps, seed) {
    const r = this.rng(seed);
    const q = [this.QHOME[0] + 0.25 * this.gauss(r), this.QHOME[1] + 0.25 * this.gauss(r),
               this.QHOME[2] + 0.25 * this.gauss(r)];
    const queue = [];
    for (let i = 0; i < W.delay; i++) queue.push([0, 0, 0, 0]);
    const dists = [], path = [];
    let ok = false;
    for (let t = 0; t < steps; t++) {
      const tt = this.fk(q, W.l1, W.l2);
      const tip = [tt[0] + W.noise * this.gauss(r), tt[1] + W.noise * this.gauss(r),
                   tt[2] + W.noise * 2 * this.gauss(r)];
      const ex = p[0] - tip[0], ey = p[1] - tip[1], eth = p[2] - tip[2];
      const d = Math.hypot(ex, ey);
      let vx = ex, vy = ey;
      if (hover > 0 && d > 1e-9) {           // 贴着工件打转：切向绕着走，离近了才明显
        const k = hover * Math.exp(-((d / 0.03) ** 2));
        vx += k * (-ey);
        vy += k * ex;
      }
      const s1 = Math.sin(q[0]), c1 = Math.cos(q[0]);
      const s12 = Math.sin(q[0] + q[1]), c12 = Math.cos(q[0] + q[1]);
      const a = [this.GAIN * ((-this.L1S * s1 - this.L2S * s12) * vx + (this.L1S * c1 + this.L2S * c12) * vy) / 0.1,
                 this.GAIN * ((-this.L2S * s12) * vx + (this.L2S * c12) * vy) / 0.1,
                 this.GAIN * eth,
                 (closeAt > 0 && d < closeAt && Math.abs(eth) < 0.2) ? 1 : -1];
      for (let i = 0; i < 4; i++) a[i] = Math.max(-1, Math.min(1, a[i]));
      queue.push(a);
      const ae = queue.shift();
      for (let i = 0; i < 3; i++) {
        q[i] = Math.max(this.QMIN[i], Math.min(this.QMAX[i], q[i] + (1 - W.fric) * ae[i] * this.VMAX * this.DT));
      }
      const nt = this.fk(q, W.l1, W.l2);
      dists.push(Math.hypot(nt[0] - p[0], nt[1] - p[1]));
      path.push([nt[0], nt[1]]);
      if (ae[3] > 0.5) {                     // 夹爪闭合：这一刻定成败，回合结束
        ok = Math.hypot(nt[0] - p[0], nt[1] - p[1]) < this.TOLP && Math.abs(nt[2] - p[2]) < this.TOLR;
        break;
      }
    }
    return { dists, path, ok, n: dists.length };
  },
  // 把全部候选策略各跑一遍（两套物理）。轨迹与权重无关，所以只按“回合步数”缓存一次。
  family(steps) {
    const key = String(steps);
    if (!this._fam) this._fam = {};
    if (this._fam[key]) return this._fam[key];
    const tg = this.targets(), out = [];
    this.CLOSE_AT.forEach((c) => this.HOVER.forEach((hv) => {
      const eps = [], epsR = [];
      for (let k = 0; k < this.NEP; k++) {
        eps.push(this.episode(tg[k], this.SIMW, c, hv, steps, k * 7 + 5));
        epsR.push(this.episode(tg[k], this.REALW, c, hv, steps, k * 7 + 5));
      }
      out.push({ c, hv, eps, epsR, shaped: {} });
    }));
    this._fam[key] = out;
    return out;
  },
  shapedSum(cd, d0) {                        // Σ exp(−d / d0)，按 d0 缓存
    const key = d0.toFixed(4);
    if (cd.shaped[key] == null) {
      let s = 0;
      for (let k = 0; k < cd.eps.length; k++) for (const d of cd.eps[k].dists) s += Math.exp(-d / d0);
      cd.shaped[key] = s / cd.eps.length;
    }
    return cd.shaped[key];
  },
  // 这个权重下“累计奖励最高的那一版”：奖励在**仿真**里算（训练就在那里），成绩两列都报
  pick(steps, w, d0, bonus, allow) {
    const fam = this.family(steps);
    let best = null;
    fam.forEach((cd) => {
      if (!allow && cd.c <= 0) return;
      let S = 0, SR = 0;
      for (let k = 0; k < cd.eps.length; k++) { if (cd.eps[k].ok) S++; if (cd.epsR[k].ok) SR++; }
      const okRate = S / cd.eps.length;
      const R = w * this.shapedSum(cd, d0) + bonus * okRate;
      const o = { R, sim: okRate * 100, real: SR / cd.epsR.length * 100, c: cd.c, hv: cd.hv,
                  farming: cd.c <= 0, cd };
      if (!best || o.R > best.R) best = o;
    });
    return best;
  },
  sweep(steps, d0, bonus, allow) {
    const key = `${steps}|${d0}|${bonus}|${allow}`;
    if (!this._sw) this._sw = {};
    if (this._sw[key]) return this._sw[key];
    const pts = this.WGRID.map((w) => { const b = this.pick(steps, w, d0, bonus, allow); return [w, b.R, b.sim, b.real, b.farming]; });
    let crit = null, worst = 100;
    pts.forEach((p) => { if (crit === null && p[4]) crit = p[0]; worst = Math.min(worst, p[2]); });
    let rmax = 1e-9;
    pts.forEach((p) => { rmax = Math.max(rmax, p[1]); });
    this._sw[key] = { pts, crit, worst, rmax };
    return this._sw[key];
  },
  allowed(api) { return api.scene === "fix" ? 0 : Math.round(api.p.allow); },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p, d0 = q.d0 / 100, steps = Math.round(q.steps), allow = this.allowed(api);
    const sw = this.sweep(steps, d0, q.bonus, allow);
    const now = this.pick(steps, q.w, d0, q.bonus, allow);
    const zero = this.pick(steps, 0, d0, q.bonus, allow);
    if (api.scene === "shaping") {
      if (q.w <= 0.001) api.done("base");
      if (q.w >= 0.6 && q.w <= 0.95 && now.sim > 0.1) api.done("rise");
      if (now.farming && now.sim <= 0.001) api.done("farm");
      if (q.bonus >= 40 && sw.crit !== null && sw.crit > 1.0) api.done("scale");
    } else if (q.w >= 2.35 && sw.worst > 50) {
      api.done("fixed");
    }
    return [[["塑形权重", "shaping weight"], q.w.toFixed(2)],
            [["奖励最高那一版的累计奖励", "reward of the winning policy"], now.R.toFixed(2)],
            [["它比权重 0 那一版高", "above the weight-0 policy by"],
             (now.R / Math.max(zero.R, 1e-9)).toFixed(2) + api.T(" 倍", "×")],
            [["它的仿真成功率", "its success in simulation"], now.sim.toFixed(1) + "%"],
            [["它的真机成功率", "its success on hardware"], now.real.toFixed(1) + "%"],
            [["两列各试了多少次", "trials in each column"], String(this.NEP)],
            [["它选的触发半径", "its closing radius"],
             now.c <= 0 ? api.T("0（永不闭合夹爪）", "0 (never closes the gripper)") : (now.c * 100).toFixed(1) + " cm"],
            [["它选的打转幅度", "its circling amplitude"], now.hv.toFixed(1)],
            [["在刷奖励吗", "is it farming the reward?"],
             now.farming ? api.T("是——奖励高、任务没完成", "yes: high reward, task not done") : api.T("没有", "no")],
            [["临界权重（本设置下）", "critical weight here"],
             sw.crit === null ? api.T("扫到 2.4 都没出现", "none up to 2.4") : sw.crit.toFixed(2)],
            [["任务分摊到每步", "task bonus per step"], (q.bonus / steps).toFixed(2)],
            [["各权重里成功率最低的一档（仿真）", "worst weight's success (simulation)"], sw.worst.toFixed(1) + "%"],
            [["刷分动作", "the never-close action"],
             allow ? api.T("允许", "allowed") : api.T("禁掉了", "forbidden")]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p;
    const d0 = q.d0 / 100, steps = Math.round(q.steps), allow = this.allowed(api);
    const sw = this.sweep(steps, d0, q.bonus, allow);
    const now = this.pick(steps, q.w, d0, q.bonus, allow);
    // 上图：奖励（归一化）与两列成功率，画在同一张图上——**背离就在这里**
    const G = api.graph({ x: 56, y: 28, w: w - 112, h: (h - 96) * 0.54,
                          xmin: 0, xmax: 2.4, ymin: 0, ymax: 105,
                          xlabel: api.T("塑形权重", "shaping weight"),
                          ylabel: api.T("成功率（%）／奖励（归一化到 100）", "success (%) / reward (scaled to 100)") }).axes();
    G.pts(sw.pts.map((p) => [p[0], p[1] / sw.rmax * 100]), api.css("--amber"), 2.6);
    G.pts(sw.pts.map((p) => [p[0], p[2]]), api.css("--blue"), 2.6);
    G.pts(sw.pts.map((p) => [p[0], p[3]]), api.css("--red"), 2.2, [5, 4]);
    sw.pts.forEach((p) => G.dots([[p[0], p[2]]], api.css("--blue"), 3));
    G.vline(q.w, api.css("--green"));
    if (sw.crit !== null) G.vline(sw.crit, api.css("--muted"));
    G.text(api.T("黄：累计奖励　蓝：仿真成功率　红虚线：真机成功率　灰：临界权重",
                 "amber: reward, blue: success in simulation, red dashed: on hardware, grey: critical weight"),
           0.03, 101, api.css("--ink"), 12);

    // 下图：奖励最高那一版走的是什么路——抓住的那一版走过去就停，刷分的那一版贴着工件绕圈
    const y0 = 28 + (h - 96) * 0.64, hh = (h - 96) * 0.36;
    const tg = this.targets(), p0 = tg[0];
    const ep = now.cd.eps[0];
    const G2 = api.graph({ x: 56, y: y0, w: (w - 136) * 0.52, h: hh,
                           xmin: (p0[0] - 0.10), xmax: (p0[0] + 0.10),
                           ymin: (p0[1] - 0.10), ymax: (p0[1] + 0.10),
                           xlabel: api.T("工件附近（m）", "near the part (m)"), ticks: false }).axes();
    G2.pts(ep.path, api.css("--amber"), 2.2);
    G2.dots([[p0[0], p0[1]]], api.css("--ink"), 4);
    G2.text(api.T(`它走了 ${ep.n} 步，${ep.ok ? "闭合时抓住了" : "没有抓住"}`,
                  `${ep.n} steps, ${ep.ok ? "grasped at the close" : "no grasp"}`),
            p0[0] - 0.095, p0[1] + 0.085, api.css("--ink"), 12);

    // 右下：两列成绩并排（**本章报表的样子**）
    const bx = 56 + (w - 136) * 0.52 + 40;
    const B = api.graph({ x: bx, y: y0, w: w - bx - 20, h: hh, xmin: 0, xmax: 4, ymin: 0, ymax: 100,
                          xlabel: api.T(`两列各试 ${this.NEP} 次`, `${this.NEP} trials each`),
                          ylabel: api.T("成功率（%）", "success (%)") }).axes();
    [[1, now.sim, api.css("--blue"), api.T("仿真", "sim")],
     [3, now.real, api.css("--red"), api.T("真机", "hardware")]].forEach(([x, v, c, name]) => {
      api.rect(B.X(x - 0.55), B.Y(v), B.X(x + 0.55) - B.X(x - 0.55), B.Y(0) - B.Y(v), c);
      B.text(`${v.toFixed(1)}%`, x, Math.min(v + 8, 94), c, 13, "center");
      B.text(name, x, 5, api.css("--ink"), 12, "center");
    });
  },
});
