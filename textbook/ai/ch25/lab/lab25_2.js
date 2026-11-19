// 实验 25.2 搬运车数量、吞吐与死锁（配 25.2、25.4 节）。
// 两个场景：
//   fleet  ：扫搬运车数量——不联锁时总吞吐只是涨不动（塌的是单车吞吐）；加了区域联锁才真出现先升后降；
//   charge ：扫充电阈值——阈值提高吞吐降一点，但“半路耗光”那一列归零。
// 与 code/_ch25.py 的 run_fleet 同一套口径：同一座车间网格（窄道只有两个口）、同样的冲突定义
// （第一选择被占算一次冲突，连续被堵 5 步算一次死锁，死锁要停 40 步才解开）、
// 同样的成本定义（吞吐 = 每百步完成的任务数，报成绩必须连死锁、超时、耗光三列一起报）。
// 车队参数（满电 240 步、充电位每步回 10、任务时限 70 步）全部是显式假设，不取自任何厂家样本。
WQ.lab({
  title: ["实验 25.2 车加到多少台才算多",
          "Lab 25.2 How many AGVs is too many?"],
  goal: ["先在不联锁的车间里把搬运车从 2 台拖到 16 台：总吞吐会涨不动，但它不会塌——塌的是单车吞吐，从三十几掉到十几。换句话说，“加车还有没有用”这个问题，只看总吞吐是看不出来的。然后把区域联锁打开（一处卡住，附近这一片一起停），同一条曲线就真的先升后降了：这才是车间里“车加多了反而更慢”的来源。最后切到第二个场景扫充电阈值：阈值提高，吞吐降几个百分点，但“半路耗光”那一列归零。做完要能回答两件事：你们那座车间的车数上限由什么定；以及验收一套搬运系统，报表上必须有哪几列。",
         "First, with no zone interlock, drag the fleet from 2 to 16: total throughput flattens but never collapses — what collapses is throughput per vehicle, from the low thirties to the mid teens. So 'is another vehicle worth it' cannot be answered from the total alone. Then switch the interlock on, so that one jam stops a whole area, and the same curve really does rise and fall: that is where 'more vehicles, slower plant' comes from. Finally sweep the charging threshold: raising it costs a few percent of throughput and takes the stranded column to zero. You should be able to say what sets the fleet limit in your own hall, and which columns belong on the acceptance report."],
  scenes: [
    { id: "fleet", name: ["扫车数", "Sweep the fleet"],
      problem: { title: ["问题：车加到多少台，再加就没用了", "Problem: when does another AGV stop helping?"],
                 text: ["这座车间中间一排货架只留两个口，所有对向的车都要抢这两个口。车少的时候加一台就多一份活；车多了以后，口子前面排队、互相堵、堵久了要重规划，加车就只剩零头。这个场景把搬运车数量交给你拖，四个数一起看：总吞吐、单车吞吐、死锁次数、任务超时数。先在不联锁的车间里拖一遍，再把区域联锁打开拖一遍——两条曲线的形状不一样，这件事比哪个数更大要紧。",
                        "The hall's middle rack leaves only two doorways, and every opposing vehicle has to fight for them. With few vehicles each new one brings a full share of work; with many, they queue, block each other and eventually need replanning, so a new one brings almost nothing. Drag the fleet size and watch four numbers together: total throughput, throughput per vehicle, deadlocks and overdue tasks. Sweep once without the zone interlock and once with it: the two curves have different shapes, and that matters more than which number is bigger."] } },
    { id: "charge", name: ["扫充电阈值", "Sweep the charging threshold"],
      problem: { title: ["问题：电量掉到多少才该去充", "Problem: at what charge should a vehicle go and charge?"],
                 text: ["充电要占时间，占的就是干活的时间，所以阈值定得越低、看上去越划算。可阈值太低，车会在半路把电用光，停在通道里要人去拖——那是一次停线，不只是一次损失。这个场景让你扫一遍阈值，把吞吐与“半路耗光”放在一起看：吞吐最高的那一档不是一次都不耗光的那一档，而把阈值提到耗光归零，吞吐只降几个百分点。这几个百分点就是“保险”的明码标价。",
                        "Charging takes time away from work, so a lower threshold looks cheaper. But too low and vehicles run flat in an aisle and have to be towed — a stoppage, not just a loss. Sweep the threshold with throughput and the stranded count side by side: the throughput-optimal setting is not the one that never strands, and moving to the setting that never strands costs only a few percent. Those few percent are the price of the insurance, stated openly."] } },
  ],
  params: [
    { id: "n", name: ["搬运车数量（台）", "fleet size (AGVs)"], min: 2, max: 16, step: 1, value: 10, digits: 0 },
    { id: "zone", name: ["区域联锁半径（格，0 = 不联锁）", "zone interlock radius (0 = off)"], min: 0, max: 6, step: 1, value: 0, digits: 0 },
    { id: "thr", name: ["充电阈值（电量低于此值就去充）", "charging threshold (share of full)"], min: 0.05, max: 0.8, step: 0.05, value: 0.3, digits: 2 },
    { id: "every", name: ["任务平均每多少步来一个", "mean steps between new tasks"], min: 1, max: 6, step: 1, value: 2, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["总吞吐（每百步完成的任务数）", "total throughput (tasks per 100 steps)"] },
           { color: "var(--green)", name: ["单车吞吐", "throughput per vehicle"] },
           { color: "var(--red)", name: ["死锁次数 / 半路耗光车次", "deadlocks / stranded vehicles"] },
           { color: "var(--muted)", name: ["当前这一档", "where you are now"] },
           { color: "var(--amber)", name: ["充电位", "charging bays"] }],
  tasks: [
    { id: "nolock", text: ["不联锁（半径 0），把搬运车从 2 台拖到 16 台：总吞吐涨不动了，可它塌了吗？再看单车吞吐，从多少掉到多少？",
                           "With the interlock off, drag the fleet from 2 to 16: total throughput flattens — but does it collapse? Now read throughput per vehicle: from what to what?"],
      demo: { scene: "fleet", set: { n: 16, zone: 0, thr: 0.3, every: 2 }, press: [] } },
    { id: "lock", text: ["把区域联锁半径拖到 4（一处卡住停一片），车数留在 16 台：总吞吐这条曲线现在是什么形状？读数里“吞吐最高的车数”是几台？",
                         "Raise the interlock radius to 4, keeping 16 vehicles: what shape does the total-throughput curve have now, and which fleet size is best?"],
      demo: { scene: "fleet", set: { n: 16, zone: 4, thr: 0.3, every: 2 }, press: [] } },
    { id: "peak", text: ["联锁开着，把车数拖回 8—10 台（曲线的最高点那一段）：总吞吐比 16 台时高还是低？多出来的六台车买到了什么？",
                         "With the interlock on, drag the fleet back to 8—10 (the top of the curve): is the total higher or lower than with 16? What did those six extra vehicles buy?"],
      demo: { scene: "fleet", set: { n: 10, zone: 4, thr: 0.3, every: 2 }, press: [] } },
    { id: "flat", text: ["切到第二个场景，把充电阈值拖到 0.05：记下吞吐与“半路耗光”车次。省下来的充电时间换到了什么？",
                         "In the second scene drag the threshold to 0.05: record the throughput and the stranded count. What did the saved charging time buy?"],
      demo: { scene: "charge", set: { thr: 0.05, n: 10, zone: 0, every: 2 }, press: [] } },
    { id: "safe", text: ["把阈值拖到 0.65：耗光归零了吗？吞吐比最高的那一档降了百分之几？这几个百分点你们愿不愿意花？",
                         "Drag the threshold to 0.65: do the strandings stop, and how many percent of throughput does that cost? Would you pay it?"],
      demo: { scene: "charge", set: { thr: 0.65, n: 10, zone: 0, every: 2 }, press: [] } },
  ],
  think: ["把你们那座车间的通道图画出来，数一数“对向车必须抢”的口子有几个。总吞吐涨不动，是因为口子不够，还是因为车不够？这两件事的对策完全相反：前者要改路线或改成单向环流，后者才是加车。再想一层：你们的搬运系统有没有区域联锁？如果有，那么“加车反而更慢”这件事在你们那里是会发生的，台数上限要实测，不能照厂家的推荐值填。",
          "Draw your own aisle plan and count the doorways that opposing vehicles must contest. When the total stops rising, is it because there are too few doorways or too few vehicles? The two call for opposite remedies: one-way circulation versus more vehicles. Then ask whether your system has a zone interlock: if it does, 'more vehicles, slower plant' will happen to you, and the fleet limit has to be measured rather than taken from a vendor's recommendation."],

  // ---------------- 车间网格（与算例同一座车间：`#` 货架、`.` 通道、`C` 充电位；第 5 行只有两个口）
  ROWS: ["#############", "#C.........C#", "#.###.###.#.#", "#.###.###.#.#",
         "#...........#", "###.#####.###", "#...........#", "#.###.###.#.#",
         "#.###.###.#.#", "#C.........C#", "#############"],
  FULL: 240, RATE: 10, DEADLINE: 70, STUCK: 5, RECOVER: 40,
  STEPS: 900, SEEDS: 6,
  FLEETS: [2, 4, 6, 8, 10, 12, 14, 16],
  THRS: [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.65, 0.8],

  map() {
    if (this._m) return this._m;
    const R = this.ROWS, H = R.length, W = R[0].length;
    const free = [], id = new Int32Array(H * W).fill(-1), chargers = [], aisle = [];
    for (let r = 0; r < H; r++) {
      for (let c = 0; c < W; c++) {
        if (R[r][c] === "#") continue;
        id[r * W + c] = free.length;
        free.push([r, c]);
        if (R[r][c] === "C") chargers.push(free.length - 1); else aisle.push(free.length - 1);
      }
    }
    const nb = free.map(([r, c]) => {
      const out = [];
      [[-1, 0], [1, 0], [0, -1], [0, 1]].forEach(([dr, dc]) => {
        const rr = r + dr, cc = c + dc;
        if (rr >= 0 && rr < H && cc >= 0 && cc < W && id[rr * W + cc] >= 0) out.push(id[rr * W + cc]);
      });
      return out;
    });
    this._m = { H, W, free, id, nb, chargers, aisle, N: free.length, fields: new Map() };
    return this._m;
  },
  field(k) {                                  // 广度优先距离场：单机最短步数的真值
    const m = this.map();
    let f = m.fields.get(k);
    if (f) return f;
    f = new Int16Array(m.N).fill(9999);
    f[k] = 0;
    let frontier = [k];
    while (frontier.length) {
      const next = [];
      for (const cur of frontier) {
        for (const q of m.nb[cur]) if (f[q] === 9999) { f[q] = f[cur] + 1; next.push(q); }
      }
      frontier = next;
    }
    m.fields.set(k, f);
    return f;
  },
  dist(a, b) { return this.field(b)[a]; },
  rng(seed) {                                 // mulberry32：整数乘法走 Math.imul，不然 32 位相乘会丢精度
    let a = (seed * 2654435761) >>> 0;
    return () => {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a) >>> 0;
      t = (((t + Math.imul(t ^ (t >>> 7), 61 | t)) >>> 0) ^ t) >>> 0;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  },

  // ---------------- 一次仿真：n 台车跑 steps 步（口径与 _ch25.py 的 run_fleet 相同）
  run(n, zone, thr, every, seed, steps) {
    const m = this.map(), r = this.rng(seed + 9001);
    const pick = (arr) => arr[Math.floor(r() * arr.length) % arr.length];
    const pos = [], batt = [], target = [], phase = [], job = [], stuck = [], recover = [], flat = [];
    for (let i = 0; i < n; i++) {
      let p = Math.floor(r() * m.N) % m.N;    // 不让两台车同格开局
      while (pos.indexOf(p) >= 0) p = Math.floor(r() * m.N) % m.N;
      pos.push(p); batt.push(this.FULL * (0.55 + 0.45 * r()));
      target.push(-1); phase.push("idle"); job.push(null); stuck.push(0); recover.push(0); flat.push(false);
    }
    const pending = [];
    let done = 0, overdue = 0, conflicts = 0, deadlocks = 0, stranded = 0, chargeSteps = 0, waitSum = 0;
    const heat = new Float32Array(m.N);
    for (let t = 0; t < steps; t++) {
      if (r() < 1 / every) {
        const p = pick(m.aisle), d = pick(m.aisle);
        if (p !== d) pending.push([t, p, d]);
      }
      // 派活与充电决策
      for (let i = 0; i < n; i++) {
        if (phase[i] === "charge") continue;
        const frac = batt[i] / this.FULL;
        if (frac < thr && (phase[i] === "idle" || phase[i] === "pick")) {
          if (phase[i] === "pick" && job[i]) { pending.unshift(job[i]); job[i] = null; }
          phase[i] = "charge";
          let best = m.chargers[0];
          for (const c of m.chargers) if (this.dist(pos[i], c) < this.dist(pos[i], best)) best = c;
          target[i] = best;
          continue;
        }
        if (phase[i] === "idle" && pending.length) {
          job[i] = pending.shift(); phase[i] = "pick"; target[i] = job[i][1];
        }
      }
      // 移动：按“先有活的、再按车号”的优先级，先到先占
      const order = [];
      for (let i = 0; i < n; i++) order.push(i);
      order.sort((a, b) => (phase[a] === "idle" ? 1 : 0) - (phase[b] === "idle" ? 1 : 0) || a - b);
      const taken = new Int32Array(m.N).fill(-1), nxt = pos.slice();
      for (const i of order) {
        if (recover[i] > 0) { recover[i] -= 1; taken[pos[i]] = i; continue; }
        if (target[i] < 0 || pos[i] === target[i] || batt[i] <= 0) { taken[pos[i]] = i; continue; }
        const fld = this.field(target[i]);
        const cand = m.nb[pos[i]].slice().sort((a, b) => fld[a] - fld[b]);
        let moved = false;
        for (let k = 0; k < cand.length; k++) {
          const c = cand[k];
          if (taken[c] >= 0) continue;
          let swap = false;
          for (let j = 0; j < n; j++) if (j !== i && nxt[j] === pos[i] && pos[j] === c) swap = true;
          if (swap) continue;                                     // 换位冲突
          if (k > 0) conflicts += 1;                              // 第一选择被占：绕了
          nxt[i] = c; taken[c] = i; batt[i] -= 1; moved = true;
          break;
        }
        if (!moved) {
          conflicts += 1; stuck[i] += 1; taken[pos[i]] = i; heat[pos[i]] += 1;
          if (stuck[i] >= this.STUCK) {
            deadlocks += 1; stuck[i] = 0; recover[i] = this.RECOVER;
            if (zone > 0) {                                       // 区域联锁：一处卡住，这一片一起停
              for (let j = 0; j < n; j++) {
                if (j === i) continue;
                const [r1, c1] = m.free[pos[j]], [r2, c2] = m.free[pos[i]];
                if (Math.abs(r1 - r2) + Math.abs(c1 - c2) <= zone) recover[j] = Math.max(recover[j], this.RECOVER);
              }
            }
          }
        } else stuck[i] = 0;
      }
      for (let i = 0; i < n; i++) pos[i] = nxt[i];
      // 半路耗光：报表上最该有的那一列
      for (let i = 0; i < n; i++) {
        if (batt[i] <= 0 && m.chargers.indexOf(pos[i]) < 0) {
          if (!flat[i]) { stranded += 1; flat[i] = true; }
        } else if (batt[i] > 0) flat[i] = false;
      }
      // 到站
      for (let i = 0; i < n; i++) {
        if (target[i] < 0 || pos[i] !== target[i]) continue;
        if (phase[i] === "pick") { phase[i] = "drop"; target[i] = job[i][2]; }
        else if (phase[i] === "drop") {
          done += 1;
          const w = t - job[i][0];
          waitSum += w;
          if (w > this.DEADLINE) overdue += 1;
          job[i] = null; target[i] = -1; phase[i] = "idle";
        } else if (phase[i] === "charge") {
          batt[i] = Math.min(this.FULL, batt[i] + this.RATE);
          chargeSteps += 1;
          if (batt[i] >= this.FULL - 1e-9) { target[i] = -1; phase[i] = "idle"; }
        }
      }
    }
    for (const [tt] of pending) if (steps - tt > this.DEADLINE) overdue += 1;
    return { n, done, overdue, conflicts, deadlocks, stranded, chargeSteps, backlog: pending.length,
             meanWait: done ? waitSum / done : NaN, thr100: done / this.STEPS * 100,
             per: done / this.STEPS * 100 / n, pos: pos.slice(), heat };
  },
  mean(n, zone, thr, every) {                 // 几个随机种子取平均（单次仿真的噪声不小）
    const key = [n, zone, thr, every].join("|");
    this._c = this._c || new Map();
    if (this._c.has(key)) return this._c.get(key);
    const rs = [];
    for (let s = 0; s < this.SEEDS; s++) rs.push(this.run(n, zone, thr, every, s, this.STEPS));
    const avg = (f) => rs.reduce((a, x) => a + f(x), 0) / rs.length;
    const out = { n, done: avg((x) => x.done), overdue: avg((x) => x.overdue), deadlocks: avg((x) => x.deadlocks),
                  stranded: avg((x) => x.stranded), conflicts: avg((x) => x.conflicts),
                  thr100: avg((x) => x.thr100), per: avg((x) => x.per), backlog: avg((x) => x.backlog),
                  one: rs[0] };
    this._c.set(key, out);
    return out;
  },
  sweepFleet(zone, thr, every) {
    const key = ["F", zone, thr, every].join("|");
    this._sf = this._sf || new Map();
    if (this._sf.has(key)) return this._sf.get(key);
    const rows = this.FLEETS.map((n) => this.mean(n, zone, thr, every));
    let best = rows[0];
    for (const r of rows) if (r.thr100 > best.thr100) best = r;
    const last = rows[rows.length - 1];
    const out = { rows, best, last, dropPct: (1 - last.thr100 / best.thr100) * 100 };
    this._sf.set(key, out);
    return out;
  },
  sweepThr(n, zone, every) {
    const key = ["T", n, zone, every].join("|");
    this._st = this._st || new Map();
    if (this._st.has(key)) return this._st.get(key);
    const rows = this.THRS.map((t) => Object.assign(this.mean(n, zone, t, every), { t }));
    let best = rows[0];
    for (const r of rows) if (r.thr100 > best.thr100) best = r;
    const safe = rows.filter((r) => r.stranded === 0);
    let safeBest = safe.length ? safe[0] : null;
    for (const r of safe) if (r.thr100 > safeBest.thr100) safeBest = r;
    const out = { rows, best, safeBest, pricePct: safeBest ? (1 - safeBest.thr100 / best.thr100) * 100 : NaN };
    this._st.set(key, out);
    return out;
  },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p, n = Math.round(q.n), zone = Math.round(q.zone), every = Math.round(q.every);
    const thr = Math.round(q.thr * 20) / 20;
    const cur = this.mean(n, zone, thr, every);
    if (api.scene === "fleet") {
      const sw = this.sweepFleet(zone, thr, every);
      if (zone < 1 && n >= 14) api.done("nolock");
      if (zone >= 4 && n >= 14) api.done("lock");
      if (zone >= 4 && n >= 8 && n <= 10) api.done("peak");
      return [[["搬运车数量", "fleet size"], n + api.T(" 台", "")],
              [["总吞吐（每百步）", "total throughput (per 100 steps)"], cur.thr100.toFixed(1)],
              [["单车吞吐", "throughput per vehicle"], cur.per.toFixed(2)],
              [["死锁次数", "deadlocks"], cur.deadlocks.toFixed(1)],
              [["任务超时数", "overdue tasks"], cur.overdue.toFixed(0)],
              [["半路耗光车次", "stranded vehicles"], cur.stranded.toFixed(2)],
              [["吞吐最高的车数", "best fleet size"], sw.best.n + api.T(" 台", "")],
              [["16 台比最高点低", "16 vehicles versus the best"], sw.dropPct.toFixed(1) + "%"]];
    }
    const sw = this.sweepThr(n, zone, every);
    if (thr <= 0.06) api.done("flat");
    if (thr >= 0.6) api.done("safe");
    return [[["充电阈值", "charging threshold"], thr.toFixed(2)],
            [["总吞吐（每百步）", "total throughput (per 100 steps)"], cur.thr100.toFixed(1)],
            [["半路耗光车次", "stranded vehicles"], cur.stranded.toFixed(2)],
            [["任务超时数", "overdue tasks"], cur.overdue.toFixed(0)],
            [["死锁次数", "deadlocks"], cur.deadlocks.toFixed(1)],
            [["吞吐最高的阈值", "throughput-optimal threshold"], sw.best.t.toFixed(2)],
            [["一次都不耗光的最好阈值", "best threshold that never strands"],
             sw.safeBest ? sw.safeBest.t.toFixed(2) : api.T("这一组里没有", "none in this sweep")],
            [["安全的价钱", "what that safety costs"],
             isFinite(sw.pricePct) ? sw.pricePct.toFixed(1) + "%" : "—"]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p;
    const n = Math.round(q.n), zone = Math.round(q.zone), every = Math.round(q.every);
    const thr = Math.round(q.thr * 20) / 20;
    const m = this.map(), cur = this.mean(n, zone, thr, every), one = cur.one;
    // 上图：这座车间。深格是货架，黄格是充电位，蓝点是车，红圈是被堵得最多的格子
    const cell = Math.min(26, Math.floor((h - 110) * 0.5 / m.H));
    const gx = 24, gy = 24;
    for (let r = 0; r < m.H; r++) {
      for (let c = 0; c < m.W; c++) {
        const k = m.id[r * m.W + c];
        const x = gx + c * cell, y = gy + r * cell;
        if (k < 0) api.rect(x, y, cell, cell, api.css("--line"), null);
        else api.rect(x, y, cell, cell, null, api.css("--grid"));
        if (k >= 0 && m.chargers.indexOf(k) >= 0) api.rect(x + 2, y + 2, cell - 4, cell - 4, api.css("--amber"), null);
      }
    }
    let hot = 0;
    for (let k = 0; k < m.N; k++) if (one.heat[k] > one.heat[hot]) hot = k;
    if (one.heat[hot] > 0) {
      const [r, c] = m.free[hot];
      api.circle(gx + c * cell + cell / 2, gy + r * cell + cell / 2, cell * 0.46, null, api.css("--red"));
    }
    for (const p of one.pos) {
      const [r, c] = m.free[p];
      api.circle(gx + c * cell + cell / 2, gy + r * cell + cell / 2, cell * 0.3, api.css("--blue"));
    }
    api.label(api.T("一排货架只留两个口：所有对向的车都要抢这两个口",
                    "the middle rack leaves two doorways; all opposing traffic contests them"),
              gx + m.W * cell + 16, gy + 18, api.css("--ink"), 13);
    api.label(api.T(`红圈：被堵得最多的格子　死锁 ${cur.deadlocks.toFixed(1)} 次　超时 ${cur.overdue.toFixed(0)} 个`,
                    `red: the most blocked cell; ${cur.deadlocks.toFixed(1)} deadlocks, ${cur.overdue.toFixed(0)} overdue`),
              gx + m.W * cell + 16, gy + 40, api.css("--muted"), 13);
    // 下图：扫描曲线
    const top = gy + m.H * cell + 34, gh = Math.max(110, h - top - 46);
    if (api.scene === "fleet") {
      const sw = this.sweepFleet(zone, thr, every);
      let ymax = 0;
      for (const r of sw.rows) ymax = Math.max(ymax, r.thr100);
      const g = api.graph({ x: 54, y: top, w: w - 104, h: gh, xmin: 1, xmax: 17, ymin: 0, ymax: ymax * 1.25,
                            xlabel: api.T("搬运车数量（台）", "fleet size"),
                            ylabel: api.T("蓝：总吞吐　绿：单车吞吐×5　红：死锁次数",
                                          "blue: total, green: per vehicle ×5, red: deadlocks") }).axes();
      g.pts(sw.rows.map((r) => [r.n, r.thr100]), api.css("--blue"), 2.6);
      g.dots(sw.rows.map((r) => [r.n, r.thr100]), api.css("--blue"), 3);
      g.pts(sw.rows.map((r) => [r.n, r.per * 5]), api.css("--green"), 2.2, [5, 4]);
      g.pts(sw.rows.map((r) => [r.n, r.deadlocks]), api.css("--red"), 2);
      g.vline(n, api.css("--muted"));
      g.point(sw.best.n, sw.best.thr100, api.css("--blue"),
              api.T(`最高点 ${sw.best.n} 台`, `best: ${sw.best.n}`));
      g.text(zone > 0 ? api.T("联锁开着：先升后降", "interlock on: it rises and falls")
                      : api.T("不联锁：总吞吐只是涨不动，塌的是单车吞吐",
                              "no interlock: the total only flattens; per-vehicle collapses"),
             1.4, ymax * 1.16, api.css("--ink"), 13);
      return;
    }
    const sw = this.sweepThr(n, zone, every);
    let ymax = 0;
    for (const r of sw.rows) ymax = Math.max(ymax, r.thr100);
    const g = api.graph({ x: 54, y: top, w: w - 104, h: gh, xmin: 0, xmax: 0.85, ymin: 0, ymax: ymax * 1.25,
                          xlabel: api.T("充电阈值（电量占满电的比例）", "charging threshold (share of full)"),
                          ylabel: api.T("蓝：总吞吐　红：半路耗光车次×5", "blue: throughput, red: stranded ×5") }).axes();
    g.pts(sw.rows.map((r) => [r.t, r.thr100]), api.css("--blue"), 2.6);
    g.dots(sw.rows.map((r) => [r.t, r.thr100]), api.css("--blue"), 3);
    g.pts(sw.rows.map((r) => [r.t, r.stranded * 5]), api.css("--red"), 2.2);
    g.vline(thr, api.css("--muted"));
    g.point(sw.best.t, sw.best.thr100, api.css("--blue"), api.T("吞吐最高", "throughput-optimal"));
    if (sw.safeBest) g.point(sw.safeBest.t, sw.safeBest.thr100, api.css("--green"),
                             api.T("一次都不耗光", "never strands"));
    g.text(api.T("吞吐最高的那一档会有车耗光；安全的那一档只差几个百分点",
                 "the throughput-optimal setting strands vehicles; the safe one costs a few percent"),
           0.02, ymax * 1.16, api.css("--ink"), 13);
  },
});
