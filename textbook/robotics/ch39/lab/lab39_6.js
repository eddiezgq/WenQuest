// 实验 39.6 统计过程控制（配 39.6 节）。磨削模型与算例 39.6.2 相同（数字工厂 SH-301 轴承位 Ø35 k6）：
// 直径均值 35.0065 + 0.0125·磨损，标准差 0.0012 mm，砂轮每磨一件磨损 1/30，剩余寿命低于 0.08 时修整；随机数用固定种子，但与程序 39.6.1 不同。
// 可改为每 N 件修整，或打开“磨损补偿”（机床按估计的磨损量自动修正进给，估计有 20% 的误差）。
// 生活场景把同一过程换算成矿泉水灌装量 550 mL ± 5 mL：灌装阀逐渐结垢、灌装量变少，清洗后恢复。
// 控制图按实时使用的方式判异：每完成一组，只用到此为止的数据计算控制限。
WQ.lab({
  title: ["实验 39.6 统计过程控制", "Lab 39.6 Statistical process control"],
  goal: ["让生产线连续生产 100 件，看控制图是否在出现废品之前报警；再改进工艺，让过程既不出废品，过程性能指数又达到 1 以上。",
         "Run 100 parts: does the control chart alarm before the first reject? Then improve the process to have no rejects and a performance index above 1."],
  scenes: [
    { id: "grind", robot: true, name: ["机器人磨削单元", "Robot grinding cell"],
      problem: { title: ["机器人问题：输出轴轴承位的在线检测", "Robot problem: in-line gauging of the bearing seat"],
                 text: ["机器人把磨好的输出轴 SH-301 放上测量工位，测出轴承位直径（Ø35 k6：35.002–35.018 mm）。每 5 件为一组画控制图。",
                        "The robot puts each ground output shaft SH-301 on the gauge, which measures the bearing seat (Ø35 k6: 35.002–35.018 mm). Every 5 parts form a subgroup."] } },
    { id: "bottle", name: ["矿泉水灌装线", "Bottled-water filling line"],
      problem: { title: ["生活中的例子：每瓶水装得一样多吗", "Everyday example: is every bottle filled the same?"],
                 text: ["标注 550 mL 的矿泉水，灌装量规定在 545–555 mL。灌装阀逐渐结垢，流量变小，灌装量慢慢变少，清洗后恢复。",
                        "A 550 mL bottle must hold 545–555 mL. Scale slowly builds up in the valve, the flow drops and the fill shrinks until the valve is cleaned."] } },
  ],
  params: [
    { id: "dress", name: ["修整（清洗）间隔 / 件，0 = 按寿命（约 28 件）", "Dress (clean) every N parts, 0 = by wheel life (about 28)"], min: 0, max: 30, step: 1, value: 0, unit: "", digits: 0 },
    { id: "comp", name: ["磨损（结垢）补偿：0 关 / 1 开", "Wear compensation: 0 off / 1 on"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始生产", "Run"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "alarm", robot: true, text: ["原工艺（按寿命修整、不补偿）：生产 100 件，控制图在第一件废品之前报警。", "Original process: run 100 parts; the chart alarms before the first reject."],
      demo: { scene: "grind", set: { dress: 0, comp: 0 }, press: ["start"], wait: 8 } },
    { id: "dress", robot: true, text: ["改变修整间隔：100 件中没有废品，且过程性能指数 Ppk ≥ 1。", "Change the dressing interval: no rejects in 100 parts and Ppk ≥ 1."],
      demo: { scene: "grind", set: { dress: 14, comp: 0 }, press: ["start"], wait: 8 } },
    { id: "comp", text: ["灌装线：不缩短清洗间隔，改用补偿，做到没有不合格瓶，且 Ppk ≥ 1。", "Filling line: keep the cleaning interval, use compensation instead: no bad bottles and Ppk ≥ 1."],
      demo: { scene: "bottle", set: { dress: 0, comp: 1 }, press: ["start"], wait: 8 } },
  ],
  think: ["控制图报警时，所有零件都还在公差之内。这时该不该停机？如果不停，可能付出什么代价？",
          "When the chart alarms every part is still in tolerance. Should the line stop? What may it cost not to?"],

  N: 100, RATE: 40, A2: 0.577, D3: 0, D4: 2.114, D2: 2.326,
  unit(api) {      // 显示单位：磨削用 mm，灌装把同一过程换算成 mL
    return api.scene === "bottle" ? { k: -625, c: 550, lo: 545, hi: 555, u: "mL", d: 1 } : { k: 1, c: 35.010, lo: 35.002, hi: 35.018, u: "mm", d: 4 };
  },
  make(api) {
    let seed = 3906;
    const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return (seed + 0.5) / 2147483648; };
    const gauss = () => Math.sqrt(-2 * Math.log(rnd())) * Math.cos(2 * Math.PI * rnd());
    const U = this.unit(api), x = [];
    let life = 1;
    for (let i = 0; i < this.N; i++) {
      const wear = 1 - life;
      let mu = 35.0065 + 0.0125 * wear;
      if (api.p.comp) mu = 35.010 + 0.2 * 0.0125 * (wear - 0.45);          // 补偿后残留 20% 的磨损影响
      const d = mu + 0.0012 * gauss();
      x.push(U.c + U.k * (d - 35.010));
      life = Math.max(0, life - 1 / 30);
      if ((api.p.dress === 0 && life < 0.08) || (api.p.dress > 0 && (i + 1) % api.p.dress === 0)) life = 1;
    }
    return x;
  },
  analyse(x, U) {
    const g = [];
    for (let i = 0; i + 5 <= x.length; i += 5) { const s = x.slice(i, i + 5); g.push({ m: s.reduce((a, b) => a + b, 0) / 5, r: Math.max(...s) - Math.min(...s) }); }
    const r = { groups: g, outs: x.map((v, i) => (v < U.lo || v > U.hi ? i + 1 : 0)).filter(Boolean), sig: [] };
    if (g.length < 4) return r;
    // 实时使用：每完成一组，只用到此为止的各组计算控制限，检查这一组（第 4 组起）
    const lim = (k) => { const q = g.slice(0, k), xbb = q.reduce((a, b) => a + b.m, 0) / k, rbar = q.reduce((a, b) => a + b.r, 0) / k;
      return { xbb, rbar, ucl: xbb + this.A2 * rbar, lcl: xbb - this.A2 * rbar, rucl: this.D4 * rbar }; };
    Object.assign(r, lim(g.length));
    const m = g.map((q) => q.m);
    for (let i = 3; i < m.length; i++) {
      const L = lim(i + 1);
      const up6 = i >= 5 && [1, 2, 3, 4, 5].every((k) => m[i - k + 1] > m[i - k]), dn6 = i >= 5 && [1, 2, 3, 4, 5].every((k) => m[i - k + 1] < m[i - k]);
      const side9 = i >= 8 && (m.slice(i - 8, i + 1).every((v) => v > L.xbb) || m.slice(i - 8, i + 1).every((v) => v < L.xbb));
      if (m[i] > L.ucl || m[i] < L.lcl) r.sig.push([i + 1, 0]);
      else if (up6 || dn6) r.sig.push([i + 1, 1]);
      else if (side9) r.sig.push([i + 1, 2]);
    }
    const mu = x.reduce((a, b) => a + b, 0) / x.length, s = Math.sqrt(x.reduce((a, v) => a + (v - mu) ** 2, 0) / (x.length - 1));
    r.cp = (U.hi - U.lo) / (6 * r.rbar / this.D2);
    r.ppk = Math.min(U.hi - mu, mu - U.lo) / (3 * s);
    return r;
  },
  reset(api, s) { s.x = this.make(api); s.n = 0; s.run = false; s.acc = 0; s.res = null; },
  change(api, s) { this.reset(api, s); },
  start(api, s) { this.reset(api, s); s.run = true; },
  update(dt, api, s) {
    if (!s.run) return;
    s.acc += dt * this.RATE;
    while (s.acc >= 1 && s.n < this.N) { s.acc -= 1; s.n += 1; }
    s.res = this.analyse(s.x.slice(0, s.n), this.unit(api));
    if (s.n < this.N) return;
    s.run = false; api.stop();
    const r = s.res, first = r.sig.length ? r.sig[0][0] * 5 : Infinity;
    if (api.scene === "grind" && !api.p.comp && api.p.dress === 0 && r.outs.length && first <= r.outs[0]) api.done("alarm");
    if (api.scene === "grind" && !api.p.comp && api.p.dress > 0 && !r.outs.length && r.ppk >= 1) api.done("dress");
    if (api.scene === "bottle" && api.p.comp && api.p.dress === 0 && !r.outs.length && r.ppk >= 1) api.done("comp");
  },
  readouts(api, s) {
    const en = api.lang() === "en", r = s.res, U = this.unit(api);
    const rules = en ? ["beyond a limit", "6 rising/falling", "9 on one side"] : ["越出控制限", "连续 6 点升或降", "连续 9 点同侧"];
    const rows = [[["已生产", "produced"], `${s.n} / ${this.N}`],
                  [["超差件数", "out of tolerance"], r ? `${r.outs.length}${r.outs.length ? (en ? " (first: no. " : "（第一件：") + r.outs[0] + (en ? ")" : "）") : ""}` : "0"]];
    if (r && r.sig) rows.push([["首次判异", "first signal"], r.sig.length ? `${en ? "subgroup " : "第 "}${r.sig[0][0]}${en ? "" : " 组"}（${rules[r.sig[0][1]]}）` : (en ? "none" : "无")]);
    if (r && r.cp) rows.push([["Cp（组内）", "Cp (within)"], api.fmt(r.cp, 2)], [["Ppk（总体）", "Ppk (overall)"], api.fmt(r.ppk, 2)]);
    rows.push([["公差", "tolerance"], `${U.lo}–${U.hi} ${U.u}`]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, U = this.unit(api), r = s.res, x = s.x.slice(0, s.n), en = api.lang() === "en";
    const x0 = 64, x1 = w - 40, mid = h * 0.5;
    const span = (U.hi - U.lo) * 0.7, ylo = U.lo - span * 0.25, yhi = U.hi + span * 0.25;
    // 上：单件值与公差带
    const Y1 = (v) => mid - 18 - (mid - 36) * (v - ylo) / (yhi - ylo), X1 = (i) => x0 + (x1 - x0) * i / (this.N - 1);
    api.rect(x0, Y1(U.hi), x1 - x0, Y1(U.lo) - Y1(U.hi), "rgba(44,160,44,0.10)");
    api.line(x0, Y1(U.hi), x1, Y1(U.hi), api.css("--ink"), 1); api.line(x0, Y1(U.lo), x1, Y1(U.lo), api.css("--ink"), 1);
    api.label(String(U.hi), 4, Y1(U.hi) + 4, api.css("--muted"), 11); api.label(String(U.lo), 4, Y1(U.lo) + 4, api.css("--muted"), 11);
    x.forEach((v, i) => { const bad = v < U.lo || v > U.hi; api.circle(X1(i), Y1(Math.min(yhi, Math.max(ylo, v))), bad ? 4.5 : 2.5, bad ? api.css("--red") : api.css("--blue")); });
    api.label(en ? `each part / ${U.u}` : `单件值 / ${U.u}`, x0, 14, api.css("--muted"), 12);
    // 下：均值控制图
    const top = mid + 14, bot = h - 22, X2 = (g) => x0 + (x1 - x0) * (g - 1) / 19;
    api.label(en ? "subgroup means (X̄ chart)" : "组均值（均值控制图）", x0, top - 2, api.css("--muted"), 12);
    if (!r || !r.groups.length) return;
    const ms = r.groups.map((q) => q.m), lo2 = Math.min(...ms, r.lcl ?? Infinity), hi2 = Math.max(...ms, r.ucl ?? -Infinity), pad = (hi2 - lo2) * 0.15 || 0.001;
    const Y2 = (v) => bot - (bot - top - 12) * (v - lo2 + pad) / (hi2 - lo2 + 2 * pad);
    if (r.ucl) {
      api.line(x0, Y2(r.xbb), x1, Y2(r.xbb), api.css("--ink"), 1);
      api.line(x0, Y2(r.ucl), x1, Y2(r.ucl), api.css("--amber"), 1.2); api.line(x0, Y2(r.lcl), x1, Y2(r.lcl), api.css("--amber"), 1.2);
      api.label("UCL", x1 + 4, Y2(r.ucl) + 4, api.css("--amber"), 11); api.label("LCL", x1 + 4, Y2(r.lcl) + 4, api.css("--amber"), 11);
    }
    ms.forEach((v, i) => { if (i) api.line(X2(i), Y2(ms[i - 1]), X2(i + 1), Y2(v), api.css("--blue"), 1.2); });
    ms.forEach((v, i) => api.circle(X2(i + 1), Y2(v), 3, api.css("--blue")));
    (r.sig || []).forEach(([g]) => api.circle(X2(g), Y2(ms[g - 1]), 7, null, api.css("--red")));
  },
});
