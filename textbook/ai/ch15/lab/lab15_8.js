// 实验 15.8 车间 AGV 调度：奖励怎么写，车就怎么跑（配 15.8 节）。
// 两个场景：
//   compare ：三种调度（最近任务优先、最久等待优先、按权重打分）在同一批订单上的指标对照；
//   tail    ：等待时间的分布——平均数看不见的那条尾巴。
// 订单按泊松过程现生成，整段仿真在浏览器里跑，与 code/_ch15.py 的 AGVShop 同一套规则。
WQ.lab({
  title: ["实验 15.8 AGV 调度：奖励里的那两个权重", "Lab 15.8 AGV dispatching: the two weights in the reward"],
  goal: ["亲手调车数、订单密度与奖励里“已等时间”的权重，看平均等待、95 分位、最久的那一单与空驶距离怎样此消彼长。做完能说清一件事：这类系统里“学出来的策略”往往就是几个权重，难的不是学，是把奖励写对。",
         "Set the fleet size, the order rate and the weight on waiting time, then watch the mean wait, the 95th percentile, the worst case and the empty travel trade off against each other. The lesson: the learned policy here is just a couple of weights — the hard part is writing the reward, not the learning."],
  scenes: [
    { id: "compare", name: ["三种调度", "Three dispatchers"],
      problem: { title: ["问题：下一台空车去接哪一单", "Problem: which order should the next free AGV take"],
                 text: ["车间六个工位、几台 AGV，订单随机来。每当有车空出来，就要决定去接哪一单。最近任务优先省空驶但会把远处的单晾着；最久等待优先听着公平，车却一直在空跑。",
                        "Six stations, a few AGVs and orders arriving at random. Whenever a vehicle frees up, something must decide which order it takes. Nearest-first saves empty travel but starves distant orders; oldest-first sounds fair but keeps the vehicles driving empty."] } },
    { id: "tail", name: ["那条尾巴", "The tail"],
      problem: { title: ["问题：平均数看不见的东西", "Problem: what the average hides"],
                 text: ["平均等待两分钟听着不错，可要是有一单等了十三分钟，车间主任记住的是那一单。调度好不好，要看分布的尾巴，不是看平均数——这与 11.8、12.7、14.6 节看阈值是同一个道理。",
                        "A two-minute average sounds fine until one order waits thirteen minutes — that is the one the shop floor remembers. Judge a dispatcher by the tail of the distribution, not by the mean."] } },
  ],
  params: [
    { id: "agv", name: ["AGV 台数", "number of AGVs"], min: 2, max: 6, step: 1, value: 3, digits: 0 },
    { id: "rate", name: ["每小时来多少单", "orders per hour"], min: 60, max: 180, step: 10, value: 150, digits: 0 },
    { id: "wWait", name: ["奖励里“已等时间”的权重", "weight on waiting time"], min: 0, max: 0.8, step: 0.05, value: 0.1, digits: 2 },
    { id: "hours", name: ["仿真多少小时", "hours simulated"], min: 1, max: 4, step: 1, value: 3, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["最近任务优先", "nearest first"] }, { color: "var(--red)", name: ["最久等待优先", "oldest first"] },
           { color: "var(--green)", name: ["按权重打分", "weighted score"] }],
  tasks: [
    { id: "rules", text: ["按默认设置比一比两条规则：最久等待优先的平均等待是最近任务优先的几倍？空驶距离呢？",
                          "Compare the two rules at the default settings: how many times worse is oldest-first on mean wait, and on empty travel?"],
      demo: { scene: "compare", set: { agv: 3, rate: 150, wWait: 0.1 }, press: [] } },
    { id: "weight", text: ["把权重从 0 调到 0.05、0.1、0.2：平均等待涨了多少？最久的那一单降了多少？哪一档最划算？",
                           "Raise the weight from 0 to 0.05, 0.1 and 0.2: how much does the mean wait rise, how much does the worst case fall, and which setting is the best buy?"],
      demo: { scene: "compare", set: { wWait: 0.2 }, press: [] } },
    { id: "fleet", text: ["把车数加到 5 台：三种调度的差别还明显吗？由此说明“调度能救的，和加车能救的，不是同一类问题”。",
                          "Raise the fleet to five: do the dispatchers still differ much? What does that say about when scheduling helps and when you simply need more vehicles?"],
      demo: { scene: "compare", set: { agv: 5 }, press: [] } },
    { id: "tail", text: ["切到“那条尾巴”：权重 0 与权重 0.05 两条曲线，在 1% 那一行各对应多少秒？",
                         "Switch to the tail scene: at the 1% line, how many seconds do the weight-0 and weight-0.05 curves correspond to?"],
      demo: { scene: "tail", set: { wWait: 0.1 }, press: [] } },
  ],
  think: ["如果奖励只写“少空驶”，学出来的调度会是什么样？车间主任第二天会先抱怨哪一件事？",
          "If the reward only rewards low empty travel, what dispatcher do you get, and what will the shop floor complain about first?"],

  STATIONS: [[0, 0], [12, 0], [24, 0], [0, 18], [12, 18], [24, 18]],
  SPEED: 1.2, LOAD: 20,
  dist(a, b) { const A = this.STATIONS[a], B = this.STATIONS[b]; return Math.abs(A[0] - B[0]) + Math.abs(A[1] - B[1]); },
  rand(seed) { let t = seed >>> 0; return () => { t += 0x6d2b79f5; let x = Math.imul(t ^ (t >>> 15), 1 | t); x ^= x + Math.imul(x ^ (x >>> 7), 61 | x); return ((x ^ (x >>> 14)) >>> 0) / 4294967296; }; },
  orders(rate, horizon, seed) {
    const rnd = this.rand(seed), out = [];
    let t = 0;
    while (true) {
      t += -Math.log(1 - rnd()) / rate;
      if (t >= horizon) break;
      const a = Math.floor(rnd() * 6);
      let b = Math.floor(rnd() * 6);
      if (b === a) b = (b + 1) % 6;
      out.push({ t, from: a, to: b });
    }
    return out;
  },
  run(orders, nAgv, pick) {
    const freeAt = new Float64Array(nAgv), where = new Int32Array(nAgv);
    const pending = [], waits = [];
    let i = 0, t = 0, empty = 0;
    while (i < orders.length || pending.length) {
      let k = 0;
      for (let v = 1; v < nAgv; v++) if (freeAt[v] < freeAt[k]) k = v;
      t = Math.max(freeAt[k], t);
      while (i < orders.length && orders[i].t <= t) pending.push(orders[i++]);
      if (!pending.length) { if (i < orders.length) { t = orders[i].t; continue; } break; }
      const j = pick(where[k], pending, t);
      const o = pending.splice(j, 1)[0];
      const go = this.dist(where[k], o.from) / this.SPEED;
      empty += this.dist(where[k], o.from);
      waits.push(t - o.t + go);
      freeAt[k] = t + go + this.LOAD + this.dist(o.from, o.to) / this.SPEED + this.LOAD;
      where[k] = o.to;
    }
    waits.sort((a, b) => a - b);
    const q = (p) => waits.length ? waits[Math.min(waits.length - 1, Math.floor(p * waits.length))] : 0;
    return { n: waits.length, waits, mean: waits.reduce((s, x) => s + x, 0) / Math.max(waits.length, 1),
             p95: q(0.95), max: waits.length ? waits[waits.length - 1] : 0, emptyPer: empty / Math.max(waits.length, 1) };
  },
  policies(wWait) {
    const self = this;
    return {
      near: (at, pend) => { let b = 0; for (let j = 1; j < pend.length; j++) if (self.dist(at, pend[j].from) < self.dist(at, pend[b].from)) b = j; return b; },
      old: (at, pend, t) => { let b = 0; for (let j = 1; j < pend.length; j++) if (pend[j].t < pend[b].t) b = j; return b; },
      w: (at, pend, t) => { let b = 0, bs = -Infinity;
        for (let j = 0; j < pend.length; j++) { const s = -self.dist(at, pend[j].from) + wWait * (t - pend[j].t); if (s > bs) { bs = s; b = j; } } return b; },
    };
  },
  calc(api) {
    const p = api.p, key = [p.agv, p.rate, p.wWait, p.hours].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const orders = this.orders(p.rate / 3600, p.hours * 3600, 1);
    const pol = this.policies(p.wWait);
    const out = { near: this.run(orders, p.agv, pol.near), old: this.run(orders, p.agv, pol.old),
                  w: this.run(orders, p.agv, pol.w), w0: this.run(orders, p.agv, this.policies(0).w), orders: orders.length };
    this._c = { key, val: out };
    return out;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const p = api.p, c = this.calc(api);
    if (api.scene === "compare" && p.agv === 3 && p.rate === 150) api.done("rules");
    if (api.scene === "compare" && p.wWait >= 0.2 - 1e-9) api.done("weight");
    if (api.scene === "compare" && p.agv >= 5) api.done("fleet");
    if (api.scene === "tail") api.done("tail");
    const f = (x) => x.toFixed(0) + " s";
    if (api.scene === "compare") {
      return [[["这段时间来了多少单", "orders in this period"], String(c.orders)],
              [["最近任务优先：平均 / 95 分位 / 最久", "nearest: mean / p95 / worst"], `${f(c.near.mean)} / ${f(c.near.p95)} / ${f(c.near.max)}`],
              [["最久等待优先：平均 / 95 分位 / 最久", "oldest: mean / p95 / worst"], `${f(c.old.mean)} / ${f(c.old.p95)} / ${f(c.old.max)}`],
              [["按权重打分：平均 / 95 分位 / 最久", "weighted: mean / p95 / worst"], `${f(c.w.mean)} / ${f(c.w.p95)} / ${f(c.w.max)}`],
              [["每单空驶（最近 / 最久 / 加权）", "empty travel per job"],
               `${c.near.emptyPer.toFixed(1)} / ${c.old.emptyPer.toFixed(1)} / ${c.w.emptyPer.toFixed(1)} m`],
              [["加权比最近：平均多等 / 最久少等", "weighted vs nearest: mean / worst"],
               `${(c.w.mean - c.near.mean).toFixed(0)} s / ${(c.near.max - c.w.max).toFixed(0)} s`]];
    }
    const pct = (r, p_) => r.waits.length ? r.waits[Math.min(r.waits.length - 1, Math.floor((1 - p_) * r.waits.length))] : 0;
    return [[["权重 0：1% 的单等过", "weight 0: 1% of orders wait over"], f(pct(c.w0, 0.01))],
            [["当前权重：1% 的单等过", "current weight: 1% wait over"], f(pct(c.w, 0.01))],
            [["权重 0：最久的那一单", "weight 0: worst case"], f(c.w0.max)],
            [["当前权重：最久的那一单", "current weight: worst case"], f(c.w.max)],
            [["平均等待（权重 0 / 当前）", "mean wait (0 / current)"], `${f(c.w0.mean)} / ${f(c.w.mean)}`]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api);
    const x0 = 70, y0 = 26, pw = w - x0 - 40, ph = h - y0 - 46;
    if (api.scene === "compare") {
      const groups = [[api.T("平均", "mean"), "mean"], [api.T("95 分位", "p95"), "p95"], [api.T("最久", "worst"), "max"]];
      const series = [["near", api.css("--blue")], ["old", api.css("--red")], ["w", api.css("--green")]];
      const top = Math.max(c.near.max, c.old.max, c.w.max) * 1.1;
      const gw = pw / groups.length;
      api.line(x0, y0 + ph, x0 + pw, y0 + ph, api.css("--grid"), 1);
      groups.forEach(([name, key], gi) => {
        series.forEach(([sk, col], si) => {
          const v = c[sk][key], hgt = v / top * ph;
          const bx = x0 + gi * gw + 18 + si * (gw - 50) / 3;
          api.rect(bx, y0 + ph - hgt, (gw - 60) / 3, hgt, col, null, 0);
          api.label(v.toFixed(0), bx, y0 + ph - hgt - 6, col, 11);
        });
        api.label(name, x0 + gi * gw + gw / 2 - 18, y0 + ph + 18, api.css("--muted"), 12);
      });
      api.label(api.T("等待时间（秒）", "waiting time (s)"), 8, y0 + 12, api.css("--muted"), 12);
      return;
    }
    const sets = [["w0", api.css("--blue"), api.T("权重 0（= 最近任务优先）", "weight 0 (= nearest first)")],
                  ["w", api.css("--green"), api.T("当前权重", "current weight")],
                  ["old", api.css("--red"), api.T("最久等待优先", "oldest first")]];
    const top = Math.max(c.w0.max, c.w.max, c.old.max) * 1.05;
    const X = (v) => x0 + v / top * pw, Y = (p_) => y0 + ph - (Math.log10(Math.max(p_, 1e-3)) + 3) / 3 * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    for (let e = 0; e >= -3; e--) { api.line(x0, Y(Math.pow(10, e)), x0 + pw, Y(Math.pow(10, e)), api.css("--grid"), 1);
      api.label((Math.pow(10, e) * 100).toFixed(e < -1 ? 1 : 0) + "%", 20, Y(Math.pow(10, e)) + 4, api.css("--muted"), 11); }
    sets.forEach(([k, col, name], i) => {
      const r = c[k];
      let prev = null;
      for (let j = 0; j < r.waits.length; j += Math.max(1, Math.floor(r.waits.length / 200))) {
        const cur = [X(r.waits[j]), Y(1 - j / r.waits.length)];
        if (prev) api.line(prev[0], prev[1], cur[0], cur[1], col, 2);
        prev = cur;
      }
      api.label(name, x0 + 10, y0 + 16 + i * 16, col, 12);
    });
    api.label(api.T("这一单等了多久（秒）", "waiting time of an order (s)"), x0 + pw / 2 - 60, h - 12, api.css("--muted"), 12);
    api.label(api.T("等得比它久的比例", "share waiting longer"), 8, y0 + 12, api.css("--muted"), 12);
  },
});
