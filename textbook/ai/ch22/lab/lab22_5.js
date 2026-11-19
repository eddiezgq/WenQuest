// 实验 22.5 储能策略：电费与越界要一起看（配 22.3、22.5 节）。
// 两个场景：
//   tune   ：亲手调四个参数的阈值策略，看电费与越界次数一起怎么动；
//   safety ：真设备的效率与可用容量都比标称值差，加一层留余量的安全层，看它花多少钱、挡掉多少次越界。
// 与 code/_ch22.py 是同一套算法（dispatch_cost、safe_layer 的口径）。
WQ.lab({
  title: ["实验 22.5 省下来的那点钱，是不是拿越界换的",
          "Lab 22.5 Is that last bit of saving bought with violations?"],
  goal: ["先在标称电池上把四个参数调一遍，把电费调到最低，顺手记下每一档的越界次数——你会发现不管怎么调，**越界一直在发生**，连默认参数也有一百多次；而且更凶的参数未必更省，却一定更常蹭边界。再切到第二个场景，把效率与可用容量拖到真设备的值，看同一套参数的电费与越界各涨多少。最后把安全层的余量从 0 拖到 10%，量出它的价钱。做完要能回答：验收一个储能控制策略，报表上该有哪两列。",
         "First tune the four parameters on the nominal battery with the bill as your target, noting the violation count at every setting: violations never stop — even the default has over a hundred — and a more aggressive setting is not necessarily cheaper, though it always scrapes the limits more. Then move to the second scene and drag the efficiency and usable capacity down to the real device. Finally raise the safety margin from 0 to 10% and measure what it costs. You should be able to say which two columns belong on the acceptance report."],
  scenes: [
    { id: "tune", name: ["调策略", "Tune the policy"],
      problem: { title: ["问题：只盯电费调，会调出什么", "Problem: what do you get by tuning on the bill alone?"],
                 text: ["车间里有一组储能：谷电价时充、峰电价时放、光伏有余电时也存起来。四个参数决定它的性格。这个场景让你只盯着电费调，并把越界次数放在旁边——**没有安全层时，每一套参数都在越界**，只是次数不同。越界不是免费的：每一次都是电池管理系统把功率压回去，是报警、是寿命损耗。只报电费的报表看不出这件事。",
                        "The workshop has a battery: charge at the valley price, discharge at the peak, store surplus PV. Four parameters decide its character. Tune on the bill with the violation count beside it: without a safety layer every setting violates, only by different amounts. Each violation is the battery management system pushing the power back — an alarm, a bite out of the cell's life — and a report that shows only the bill hides it."] } },
    { id: "safety", name: ["真设备与安全层", "The real device and the safety layer"],
      problem: { title: ["问题：安全层值多少钱", "Problem: what does the safety layer cost?"],
                 text: ["真电池的往返效率比标称值低、可用容量也小一截。在仿真里调好的参数搬过来，电费涨、越界也涨。办法不是回去再调模型，而是在外面套一层**写死的安全层**：按留出的余量把动作投影到一定不会越界的范围里。这个场景让你亲手量出这层的价钱——多花百分之几的电费，换来越界归零。",
                        "A real cell has a lower round-trip efficiency and less usable capacity than the nameplate. Parameters tuned in simulation cost more and violate more once moved across. The fix is not more tuning but a hard-coded safety layer outside the policy, projecting every action into a range that cannot violate. Measure what it costs: a few percent on the bill, and the violations go to zero."] } },
  ],
  params: [
    { id: "plo", name: ["低于这个电价就充（元/kWh）", "charge below this price"], min: 0.25, max: 0.7, step: 0.01, value: 0.35, digits: 2 },
    { id: "phi", name: ["高于这个电价就放（元/kWh）", "discharge above this price"], min: 0.7, max: 1.1, step: 0.01, value: 0.95, digits: 2 },
    { id: "cf", name: ["充电用多大功率（占上限）", "charging power (share of max)"], min: 0.2, max: 1, step: 0.05, value: 0.8, digits: 2 },
    { id: "keep", name: ["放电时留多少不放", "share of power held back"], min: 0, max: 0.8, step: 0.05, value: 0.2, digits: 2 },
    { id: "eta", name: ["电池往返效率", "round-trip efficiency"], min: 0.84, max: 0.95, step: 0.01, value: 0.93, digits: 2 },
    { id: "cap", name: ["可用容量（占标称）", "usable capacity (share of nameplate)"], min: 0.85, max: 1, step: 0.01, value: 1, digits: 2 },
    { id: "margin", name: ["安全层留的余量（%）", "safety margin (%)"], min: 0, max: 10, step: 1, value: 0, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["荷电状态", "state of charge"] },
           { color: "var(--red)", name: ["被压回去的那几步（越界）", "clipped steps (violations)"] },
           { color: "var(--green)", name: ["安全层留的余量", "the safety margin"] },
           { color: "var(--muted)", name: ["荷电状态的上下限", "state-of-charge limits"] }],
  tasks: [
    { id: "base", text: ["默认参数（0.35 / 0.95 / 0.8 / 0.2）、标称电池：记下电费与越界次数。",
                         "With the default parameters on the nominal battery, record the bill and the violation count."],
      demo: { scene: "tune", set: { plo: 0.35, phi: 0.95, cf: 0.8, keep: 0.2, eta: 0.93, cap: 1, margin: 0 }, press: [] } },
    { id: "greedy", text: ["把充电功率拖到 1.0、放电留量拖到 0（更凶的一套）：越界次数涨了多少？电费是降了还是反而涨了？这说明“凶”与“省”是一回事吗？",
                           "Raise the charging power to 1.0 and the held-back share to 0: how many more violations, and does the bill actually go down? Is 'more aggressive' the same thing as 'cheaper'?"],
      demo: { scene: "tune", set: { cf: 1, keep: 0, plo: 0.35, phi: 0.95, eta: 0.93, cap: 1, margin: 0 }, press: [] } },
    { id: "real", text: ["切到第二个场景，把效率拖到 0.87、可用容量拖到 0.92：同一套参数的电费与越界各变成多少？",
                         "In the second scene drag the efficiency to 0.87 and usable capacity to 0.92: what happens to the bill and the violations?"],
      demo: { scene: "safety", set: { eta: 0.87, cap: 0.92, cf: 1, keep: 0, margin: 0 }, press: [] } },
    { id: "safe", text: ["保持真设备的参数，把安全层余量从 0 拖到 5%：越界次数变成多少？电费涨了百分之几？",
                         "Keeping the real device, raise the safety margin from 0 to 5%: what happens to the violations, and what does it cost?"],
      demo: { scene: "safety", set: { eta: 0.87, cap: 0.92, cf: 1, keep: 0, margin: 5 }, press: [] } },
    { id: "toomuch", text: ["把余量继续拖到 10%：越界还是 0，电费又涨了多少？余量留多少才算合适？",
                            "Push the margin to 10%: the violations stay at zero, but what does the extra margin cost? How much margin is enough?"],
      demo: { scene: "safety", set: { eta: 0.87, cap: 0.92, cf: 1, keep: 0, margin: 10 }, press: [] } },
  ],
  think: ["你们那组储能，荷电状态越一次界，运维上实际发生什么？把它折成钱，再回到这个实验里，看看用“电费 + 越界次数×这个钱”做目标，调出来的参数与只盯电费调出来的差多少。写不出这个钱，就先把安全层的余量留足——**不知道代价的时候，保守是对的**。",
          "What actually happens on your site when the state of charge hits a limit? Price it, then retune here with 'bill plus violations times that price' as the objective and see how different the parameters are. If you cannot price it, keep the margin generous: when the cost of a failure is unknown, caution is the right default."],

  DAYS: 6, SPD: 96, DT: 0.25,
  CAP: 600, PMAX: 150, SOC0: 0.5, SOCMIN: 0.15, SOCMAX: 0.95,
  rng(seed) { let x = (seed * 1103515245 + 12345) >>> 0; return () => { x = (x * 1103515245 + 12345) >>> 0; return x / 4294967296; }; },
  data() {
    if (this._d) return this._d;
    const n = this.DAYS * this.SPD, r = this.rng(23);
    const pv = [], load = [], price = [];
    for (let i = 0; i < n; i++) {
      const h = (i % this.SPD) / this.SPD * 24;
      let cs = 0;
      if (h >= 6 && h <= 18) cs = 400 * Math.cos((h - 12) / 6 * Math.PI / 2);
      const cloud = Math.min(1, Math.max(0.15, 0.6 + 0.4 * Math.sin(i / 41 + Math.sin(i / 13) * 1.2)));
      pv.push(Math.max(cs, 0) * cloud);
      const work = (h >= 8 && h < 22) ? 1 : 0;
      const lunch = Math.exp(-(((h - 12) / 0.6) ** 2)) * 0.45;
      load.push(Math.max((120 + 260 * work * (1 - lunch)) * (1 + 0.04 * (r() - 0.5) * 2), 0));
      let p = 0.62;
      if (h >= 8 && h < 11) p = 1.05;
      if (h >= 18 && h < 21) p = 1.05;
      if (h < 7 || h >= 23) p = 0.28;
      price.push(p);
    }
    this._d = { pv, load, price, n };
    return this._d;
  },
  run(q, margin) {
    const d = this.data(), cap = this.CAP * q.cap;
    const lo = this.SOCMIN * cap, hi = this.SOCMAX * cap;
    const mlo = (this.SOCMIN + margin) * cap, mhi = (this.SOCMAX - margin) * cap;
    let soc = Math.min(Math.max(this.SOC0 * cap, mlo), mhi);
    let cost = 0, viol = 0;
    const socs = [], flags = [];
    for (let i = 0; i < d.n; i++) {
      const surplus = d.pv[i] - d.load[i];
      let want = 0;
      if (surplus > 0) want = Math.min(surplus, this.PMAX) * q.cf;
      else if (d.price[i] <= q.plo) want = this.PMAX * q.cf;
      else if (d.price[i] >= q.phi) want = -this.PMAX * (1 - q.keep);
      want = Math.min(Math.max(want, -this.PMAX), this.PMAX);
      // 安全层：按留出的余量，把动作投影到一定不会越界的范围（margin = 0 时就是按标称值投影）
      let sent = want;
      if (margin > 0) {
        const upM = (mhi - soc) / (q.eta * this.DT), dnM = (soc - mlo) * q.eta / this.DT;
        sent = Math.min(Math.max(want, -dnM), upM);
      }
      // 物理极限：没有安全层时，是电池管理系统替你把功率压回去——**被它压回去的那一步就是一次越界**
      const up = (hi - soc) / (q.eta * this.DT), dn = (soc - lo) * q.eta / this.DT;
      let c = Math.min(Math.max(sent, -dn), up);
      const hit = Math.abs(c - sent) > 1e-3;
      if (hit) viol++;
      const grid = d.load[i] - d.pv[i] + c;
      cost += (grid > 0 ? grid * d.price[i] : grid * d.price[i] * 0.35) * this.DT;
      soc += (c > 0 ? c * q.eta : c / q.eta) * this.DT;
      soc = Math.min(Math.max(soc, lo), hi);
      socs.push(soc / cap * 100);
      flags.push(hit);
    }
    return { cost, viol, socs, flags };
  },
  noBattery() {
    const d = this.data();
    let cost = 0;
    for (let i = 0; i < d.n; i++) {
      const grid = d.load[i] - d.pv[i];
      cost += (grid > 0 ? grid * d.price[i] : grid * d.price[i] * 0.35) * this.DT;
    }
    return cost;
  },

  reset(api, s) { },
  update(dt, api, s) { api.stop(); },

  readouts(api, s) {
    const q = api.p;
    const margin = api.scene === "safety" ? q.margin / 100 : 0;
    const r = this.run(q, margin);
    const none = this.noBattery();
    if (api.scene === "tune") {
      if (Math.abs(q.cf - 0.8) < 0.03 && Math.abs(q.keep - 0.2) < 0.03) api.done("base");
      if (q.cf >= 0.98 && q.keep <= 0.02) api.done("greedy");
      return [[["不装储能的电费", "bill without the battery"], none.toFixed(0) + api.T(" 元", " CNY")],
              [["这套参数的电费", "bill with these parameters"], r.cost.toFixed(0) + api.T(" 元", " CNY")],
              [["省了", "saving"], ((1 - r.cost / none) * 100).toFixed(1) + "%"],
              [["越界次数", "violations"], String(r.viol)],
              [["越界时段占比", "share of steps clipped"], (r.viol / this.data().n * 100).toFixed(1) + "%"],
              [["电池", "battery"], api.T(`效率 ${q.eta.toFixed(2)}、可用容量 ${(q.cap * 100).toFixed(0)}%`,
                                          `efficiency ${q.eta.toFixed(2)}, usable capacity ${(q.cap * 100).toFixed(0)}%`)]];
    }
    const bare = this.run(q, 0);
    if (q.eta <= 0.88 && q.cap <= 0.93 && q.margin <= 0.5) api.done("real");
    if (q.eta <= 0.88 && q.cap <= 0.93 && q.margin >= 4.5) api.done("safe");
    if (q.margin >= 9.5) api.done("toomuch");
    return [[["没有安全层：电费", "without the safety layer: bill"], bare.cost.toFixed(0) + api.T(" 元", " CNY")],
            [["没有安全层：越界", "without the safety layer: violations"], String(bare.viol)],
            [["有安全层：电费", "with the safety layer: bill"], r.cost.toFixed(0) + api.T(" 元", " CNY")],
            [["有安全层：越界", "with the safety layer: violations"], String(r.viol)],
            [["安全层的价钱", "what the safety layer costs"],
             ((r.cost / Math.max(bare.cost, 1e-9) - 1) * 100).toFixed(2) + "%"],
            [["挡掉的越界", "violations prevented"], String(bare.viol - r.viol)]];
  },

  draw(api, s) {
    const { w, h } = api, q = api.p;
    const margin = api.scene === "safety" ? q.margin / 100 : 0;
    const r = this.run(q, margin);
    const d = this.data();
    const g = api.graph({ x: 52, y: 28, w: w - 104, h: (h - 96) * 0.56,
                          xmin: 0, xmax: this.DAYS * 24, ymin: 0, ymax: 105,
                          xlabel: api.T("时间（小时）", "time (h)"),
                          ylabel: api.T("荷电状态（%）", "state of charge (%)") }).axes();
    const pts = [];
    for (let i = 0; i < d.n; i++) pts.push([i * this.DT, r.socs[i]]);
    g.pts(pts, api.css("--blue"), 2.2);
    g.hline(this.SOCMIN * 100, api.css("--muted"));
    g.hline(this.SOCMAX * 100, api.css("--muted"));
    if (margin > 0) {
      g.hline((this.SOCMIN + margin) * 100, api.css("--green"));
      g.hline((this.SOCMAX - margin) * 100, api.css("--green"));
    }
    for (let i = 0; i < d.n; i++) {
      if (r.flags[i]) g.seg(i * this.DT, r.socs[i] - 4, i * this.DT, r.socs[i] + 4, api.css("--red"), 2);
    }
    g.text(api.T("灰线：上下限　绿线：安全层留的余量　红竖线：被压回去的那几步",
                 "grey: limits, green: safety margin, red: clipped steps"),
           0.5, 101, api.css("--ink"), 12);

    const g2 = api.graph({ x: 52, y: 28 + (h - 96) * 0.64, w: w - 104, h: (h - 96) * 0.36,
                           xmin: 0, xmax: this.DAYS * 24, ymin: -200, ymax: 460,
                           xlabel: api.T("时间（小时）", "time (h)"),
                           ylabel: api.T("功率（kW）", "power (kW)") }).axes();
    const pvp = [], ldp = [];
    for (let i = 0; i < d.n; i++) { pvp.push([i * this.DT, d.pv[i]]); ldp.push([i * this.DT, d.load[i]]); }
    g2.pts(pvp, api.css("--green"), 1.8);
    g2.pts(ldp, api.css("--ink"), 1.8, [5, 4]);
    g2.text(api.T("绿：光伏出力　黑虚线：车间负荷", "green: PV output, black dashed: workshop load"),
            0.5, 430, api.css("--ink"), 12);
  },
});
