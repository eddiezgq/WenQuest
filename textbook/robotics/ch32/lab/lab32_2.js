// 实验 32.2 谐波减速器的寿命（配 32.2 节）。
// 场景“关节”：一个关节做往返动作——每段 1 s，梯形速度（加减速各占 1/4，平均转速 = 0.75 × 最高转速），段间停顿 t_d；
//   运动时负载力矩恒为 T（停顿时转速为零，不进 T_av 的加权，只进 n_av 的分母）。
//   L10 = 7000 h × (T_r / T_av)³ × (2000 / n_av)（式 (32.2.2)，与 twin/robot.py 的 joint_life 相同）；
//   T_av = T，n_av = 0.75 n_max × 1 / (1 + t_d)（n 为输入转速，r/min）。
//   型号取零件库 D-RDC-HD-CSF（Harmonic Drive 样本，减速比 100）：17 号额定 24、平均允许 39 N·m、0.15 kg；
//   25 号 67、108 N·m、0.42 kg；32 号 137、216 N·m、0.89 kg；平均输入转速允许 3500 r/min（脂润滑）。
// 场景“骑车上坡”：以 12 km/h 上坡（车轮半径 0.34 m，示例值），前链盘 34 齿，后飞轮可选；骑手功率 150 W（示例值）。
//   踏频 = 车轮转速 × z_后 / z_前；链条拉力 ∝ 1 / 踏频（功率一定）；链条速度 ∝ 踏频；
//   仿照式 (32.2.2) 把链条的相对寿命记为 (1 / 拉力)³ × (1 / 链速) ∝ 踏频²。踏频超过 100 r/min 腿就转不过来了。
WQ.lab({
  title: ["实验 32.2 谐波减速器的寿命", "Lab 32.2 Strain wave gear life"],
  goal: ["改负载力矩、最高转速、停顿时间和减速器型号，看平均负载力矩、平均输入转速和 L10 寿命；体会 32.2 节“力矩三次方、转速一次方”。",
         "Change the load torque, top speed, dwell and gear size; watch the average torque, average input speed and L10 life — Section 32.2's “torque cubed, speed to the first power”."],
  scenes: [
    { id: "joint", robot: true, name: ["关节", "A joint"], hide: ["cog"],
      problem: { title: ["机器人问题：这台减速器能用多久", "Robot problem: how long will this gear last"],
                 text: ["机器人的一个关节整天做同一个往返动作。负载重一点、动作快一点、停顿短一点，寿命各掉多少？选小一号的减速器行不行？",
                        "A joint repeats the same back-and-forth all day. How much life is lost to a bit more load, speed or less dwell? Can a smaller gear do?"] } },
    { id: "bike", name: ["骑车上坡", "Cycling uphill"], hide: ["T", "n", "td", "size"],
      problem: { title: ["生活中的例子：挡位与链条的寿命", "Everyday example: gears and chain life"],
                 text: ["同一段坡、同样的速度，挂重挡蹬得慢、蹬得费劲，挂轻挡蹬得快。哪个挡链条和齿轮最耐用？",
                        "Same hill, same speed: a heavy gear means slow, hard pedalling, a light gear fast spinning. Which wears the chain least?"] } },
  ],
  params: [
    { id: "T", name: ["运动时的负载力矩（输出端）", "Load torque while moving (output)"], min: 5, max: 150, step: 1, value: 40, unit: "N·m", digits: 0 },
    { id: "n", name: ["最高输入转速", "Top input speed"], min: 300, max: 3500, step: 100, value: 1500, unit: "r/min", digits: 0 },
    { id: "td", name: ["段间停顿", "Dwell between moves"], min: 0, max: 5, step: 0.5, value: 1, unit: "s", digits: 1 },
    { id: "size", name: ["型号：17 / 25 / 32 号", "Size: 17 / 25 / 32"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "cog", name: ["后飞轮：0 11 齿 … 8 36 齿", "Rear cog: 0 = 11 T … 8 = 36 T"], min: 0, max: 8, step: 1, value: 3, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "std", robot: true, text: ["标准工况（25 号、40 N·m、1500 r/min、停顿 1 s）：读出平均输入转速和 L10 寿命。",
                                     "Standard case (size 25, 40 N·m, 1500 r/min, 1 s dwell): read the average input speed and L10 life."],
      demo: { scene: "joint", set: { T: 40, n: 1500, td: 1, size: 1 }, press: [] } },
    { id: "heavy", robot: true, text: ["力矩加大 20%（48 N·m，其余标准）：寿命变成原来的多少倍？为什么约是 0.58？",
                                       "Raise the torque 20 % (48 N·m, otherwise standard): what fraction of the life is left, and why about 0.58?"],
      demo: { scene: "joint", set: { T: 48, n: 1500, td: 1, size: 1 }, press: [] } },
    { id: "dwell", robot: true, text: ["标准工况下只加长停顿，让寿命翻一倍。", "From the standard case lengthen only the dwell to double the life."],
      demo: { scene: "joint", set: { T: 40, n: 1500, td: 3, size: 1 }, press: [] } },
    { id: "pick", robot: true, text: ["负载力矩 60 N·m（其余标准）：选一个能用 3 万小时以上、又最轻的型号。",
                                      "At 60 N·m (otherwise standard) pick the lightest size that lasts over 30 000 h."],
      demo: { scene: "joint", set: { T: 60, n: 1500, td: 1, size: 1 }, press: [] } },
    { id: "bike", text: ["骑车上坡：踏频不超过 100 r/min，选让链条最耐用的后飞轮。", "Uphill: with cadence at most 100 r/min, pick the rear cog that spares the chain most."],
      demo: { scene: "bike", set: { cog: 8 }, press: [] } },
  ],
  think: ["寿命公式里力矩是三次方、转速只是一次方。设计一个动作时，“慢一点”和“轻一点”哪个对寿命更有用？",
          "In the life formula torque is cubed but speed is to the first power. Designing a motion, which helps life more: slower or lighter?"],

  CSF: [{ n: "17", Tr: 24, Tavg: 39, m: 0.15 }, { n: "25", Tr: 67, Tavg: 108, m: 0.42 }, { n: "32", Tr: 137, Tavg: 216, m: 0.89 }],
  COGS: [11, 13, 15, 18, 21, 24, 28, 32, 36],
  life(p) {
    const g = this.CSF[Math.round(p.size)], nav = 0.75 * p.n / (1 + p.td);
    const L = 7000 * (g.Tr / p.T) ** 3 * (2000 / nav);
    return { g, nav, L, okT: p.T <= g.Tavg, okN: nav <= 3500 };
  },
  bike(p) {
    const zr = this.COGS[Math.round(p.cog)], wheel = (12 / 3.6) / (2 * Math.PI * 0.34) * 60, cad = wheel * zr / 34;
    const torque = 150 / (cad * 2 * Math.PI / 60);
    return { zr, cad, torque, rel: cad * cad / (100 * 100) };
  },
  nb(rows) { return rows.map(([k, v]) => [k, String(v).replace(/ /g, " ")]); },
  readouts(api) {
    const f = api.fmt, p = api.p, T = (z, e) => (api.lang() === "en" ? e : z);
    if (api.scene === "bike") {
      const b = this.bike(p), ok = b.cad <= 100;
      const best = this.COGS.map((_, k) => this.bike({ cog: k })).filter((x) => x.cad <= 100).reduce((a, x) => (x.rel > a.rel ? x : a));
      if (ok && b.zr === best.zr) api.done("bike");
      return this.nb([[["后飞轮", "Rear cog"], `${b.zr} ${T("齿", "T")}`], [["踏频", "Cadence"], f(b.cad, 0) + " r/min" + (ok ? "" : T("（腿转不过来）", " (too fast)"))],
        [["脚踏力矩", "Pedal torque"], f(b.torque, 1) + " N·m"], [["链条相对寿命（踏频 100 时 = 1）", "Relative chain life (= 1 at 100 r/min)"], f(b.rel, 2)]]);
    }
    const r = this.life(p), s = this.life({ T: 40, n: 1500, td: 1, size: 1 });
    if (p.T === 40 && p.n === 1500 && p.td === 1 && Math.round(p.size) === 1) api.done("std");
    if (p.T === 48 && p.n === 1500 && p.td === 1 && Math.round(p.size) === 1) api.done("heavy");
    if (p.T === 40 && p.n === 1500 && Math.round(p.size) === 1 && r.L >= 2 * s.L - 1e-6) api.done("dwell");
    if (p.T === 60 && p.n === 1500 && p.td === 1 && r.L >= 30000 && r.okT && r.okN) {
      const lighter = this.CSF.slice(0, Math.round(p.size)).some((_, k) => { const x = this.life({ ...p, size: k }); return x.L >= 30000 && x.okT; });
      if (!lighter) api.done("pick");
    }
    return this.nb([
      [["型号（质量）", "Size (mass)"], `${r.g.n} ${T("号", "")}（${r.g.m} kg）`],
      [["额定力矩 / 平均允许", "Rated / average limit"], `${r.g.Tr} / ${r.g.Tavg} N·m`],
      [["平均负载力矩 T_av", "Average load torque T_av"], `${f(p.T, 0)} N·m ${r.okT ? "" : T("超平均允许", "above the limit")}`],
      [["平均输入转速 n_av", "Average input speed n_av"], `${f(r.nav, 0)} r/min ${r.okN ? "" : T("超允许", "above the limit")}`],
      [["L10 寿命", "L10 life"], `${f(r.L, 0)} h`],
      [["两班制（每年 4000 h）", "Two shifts (4000 h a year)"], `${f(r.L / 4000, 1)} ${T("年", "years")}`],
      [["与标准工况之比", "Ratio to the standard case"], f(r.L / s.L, 3)],
    ]);
  },
  draw(api) {
    const { w, h } = api, f = api.fmt, p = api.p;
    if (api.scene === "bike") {
      const b = this.bike(p), x0 = w * 0.1, y0 = h * 0.85, bw = w * 0.8 / this.COGS.length;
      api.label(api.lang() === "en" ? "relative chain life for each rear cog (bars), cadence (dots)" : "各后飞轮的链条相对寿命（柱）与踏频（点）", x0, h * 0.08, api.css("--muted"), 12, "left");
      this.COGS.forEach((z, k) => {
        const x = this.bike({ cog: k }), hh = Math.min(1.4, x.rel) * h * 0.45;
        api.rect(x0 + k * bw + 4, y0 - hh, bw - 8, hh, k === Math.round(p.cog) ? api.css("--blue") : api.css("--grid"));
        api.circle(x0 + k * bw + bw / 2, y0 - x.cad / 120 * h * 0.7, 5, x.cad <= 100 ? api.css("--green") : api.css("--red"));
        api.label(String(z), x0 + k * bw + bw / 2, y0 + 14, api.css("--ink"), 12, "center");
      });
      api.line(x0, y0 - 100 / 120 * h * 0.7, x0 + bw * this.COGS.length, y0 - 100 / 120 * h * 0.7, api.css("--red"), 1, [4, 4]);
      api.label(api.lang() === "en" ? "cadence 100 r/min" : "踏频 100 r/min", x0 + bw * this.COGS.length - 4, y0 - 100 / 120 * h * 0.7 - 8, api.css("--red"), 11, "right");
      return;
    }
    // 一个循环的转速与力矩
    const x0 = w * 0.08, gw = w * 0.84, y1 = h * 0.42, y2 = h * 0.88, hh = h * 0.3, Tc = 2 * (1 + p.td);
    const X = (t) => x0 + gw * t / Tc;
    api.line(x0, y1, x0 + gw, y1, api.css("--grid"), 1); api.line(x0, y2, x0 + gw, y2, api.css("--grid"), 1);
    api.label(api.lang() === "en" ? "input speed (two moves and their dwells)" : "输入转速（两段往返与停顿）", x0, y1 - hh - 8, api.css("--muted"), 12, "left");
    api.label(api.lang() === "en" ? "load torque" : "负载力矩", x0, y2 - hh * 0.75 - 8, api.css("--muted"), 12, "left");
    const c = api.ctx;
    c.strokeStyle = api.css("--blue"); c.lineWidth = 2; c.beginPath();
    for (let i = 0; i <= 400; i++) {
      const t = Tc * i / 400, k = Math.floor(t / (1 + p.td)), u = t - k * (1 + p.td);
      let v = 0;
      if (u < 1) v = u < 0.25 ? u / 0.25 : u > 0.75 ? (1 - u) / 0.25 : 1;
      v *= k % 2 ? -1 : 1;
      const y = y1 - v * hh * (p.n / 3500);
      if (i) c.lineTo(X(t), y); else c.moveTo(X(t), y);
    }
    c.stroke();
    c.strokeStyle = api.css("--red"); c.beginPath();
    for (let i = 0; i <= 400; i++) {
      const t = Tc * i / 400, u = t - Math.floor(t / (1 + p.td)) * (1 + p.td);
      const y = y2 - (u < 1 ? p.T / 150 : 0) * hh * 0.75;
      if (i) c.lineTo(X(t), y); else c.moveTo(X(t), y);
    }
    c.stroke();
    const r = this.life(p);
    api.label(`L10 = ${f(r.L, 0)} h`, x0 + gw, h * 0.08, api.css("--ink"), 14, "right");
  },
});
