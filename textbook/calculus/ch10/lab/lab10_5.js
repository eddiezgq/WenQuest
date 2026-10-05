// 实验 10.5 曲率与 AGV 过弯（配 10.5 节）。“曲率圆”场景：在曲线上移动探测点，看曲率圆怎样贴合曲线；
// “机器人”场景：AGV 以恒定车速走换道路径，侧向加速度 v²κ 不得超过 1 m/s²，比较三次、余弦、五次三种路径。
WQ.lab({
  title: ["实验 10.5 曲率与 AGV 过弯", "Lab 10.5 Curvature and an AGV taking a bend"],
  goal: ["看清曲率与曲率圆的含义：曲线弯得越急，曲率圆越小；理解路径的最大曲率怎样限制 AGV 的车速（v ≤ √(a/κ)），以及入口处曲率跳变的害处。",
         "See what curvature and the circle of curvature mean: the sharper the bend, the smaller the circle; understand how the largest curvature of a path limits the AGV's speed (v ≤ √(a/κ)) and why a curvature jump at the entry is harmful."],
  scenes: [
    { id: "curve", name: ["曲率圆", "Circle of curvature"], hide: ["p", "L", "v"],
      problem: { title: ["每一点都有一个与曲线贴得最紧的圆", "At each point one circle hugs the curve best"],
                 text: ["κ = |y″|/(1 + y′²)^{3/2}，曲率圆的半径 R = 1/κ，圆心在法线上、曲线弯向的一侧（y″ > 0 时在上方）。在哪里曲线弯得最急？",
                        "κ = |y″|/(1 + y′²)^{3/2}; the circle of curvature has radius R = 1/κ and its centre lies on the normal, on the concave side. Where does the curve bend most sharply?"] } },
    { id: "agv", robot: true, name: ["AGV 换道", "AGV lane change"], hide: ["f", "x"],
      problem: { title: ["机器人问题：换道时能开多快？", "Robot problem: how fast can the AGV change lanes?"],
                 text: ["AGV 在 L 米内横移 1 m，车速 v 不变。侧向加速度 v²κ 超过 1 m/s² 时货物会滑动。三次、余弦、五次多项式三种路径中，哪种允许的车速最高？哪种进入弯道时最平顺？",
                        "The AGV shifts 1 m sideways within L metres at constant speed v. Above 1 m/s² of lateral acceleration v²κ the load slides. Of the cubic, cosine and quintic paths, which allows the highest speed? Which enters the bend most smoothly?"] } },
  ],
  params: [
    { id: "f", name: ["曲线：1 y = x²，2 y = sin x，3 y = eˣ，4 y = x³，5 y = ln x", "Curve: 1 y = x², 2 y = sin x, 3 y = eˣ, 4 y = x³, 5 y = ln x"], min: 1, max: 5, step: 1, value: 1, digits: 0 },
    { id: "x", name: ["探测点 x", "Probe x"], min: -2, max: 3, step: 0.01, value: 0.5, digits: 2 },
    { id: "p", name: ["路径：1 三次多项式，2 余弦，3 五次多项式", "Path: 1 cubic, 2 cosine, 3 quintic"], min: 1, max: 3, step: 1, value: 1, digits: 0 },
    { id: "L", name: ["换道长度 L", "Lane-change length L"], min: 2, max: 8, step: 0.1, value: 4, unit: "m", digits: 1 },
    { id: "v", name: ["车速 v", "Speed v"], min: 0.2, max: 2.5, step: 0.01, value: 1.2, unit: "m/s", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["曲线 / 路径", "curve / path"], color: "#222222" }, { name: ["曲率圆 / 侧向加速度", "circle of curvature / lateral acceleration"], color: "#d62728" }],
  tasks: [
    { id: "exp", text: ["选 y = eˣ，移动探测点，找出曲率最大的点（κ 达到最大值，误差 0.01 以内）。", "Choose y = eˣ and move the probe to the point of largest curvature (within 0.01 of the maximum)."],
      demo: { scene: "curve", set: { f: 3, x: -0.35 }, wait: 1 } },
    { id: "fast", robot: true, text: ["选五次多项式路径，L = 4 m，找出侧向加速度不超过 1 m/s² 的最高车速（误差 0.03 m/s 以内），运行一次。", "Choose the quintic path with L = 4 m, find the highest speed keeping lateral acceleration within 1 m/s² (to 0.03 m/s), and run it."],
      demo: { scene: "agv", set: { p: 3, L: 4, v: 1.70 }, press: ["start"], wait: 8 } },
    { id: "slip", robot: true, text: ["保持 L = 4 m、v = 1.7 m/s，换成三次多项式路径运行一次：侧向加速度超限，货物滑动。", "Keep L = 4 m and v = 1.7 m/s, switch to the cubic path and run: the lateral limit is exceeded and the load slides."],
      demo: { scene: "agv", set: { p: 1, L: 4, v: 1.7 }, press: ["start"], wait: 8 } },
    { id: "long", robot: true, text: ["车速要达到 2 m/s，用五次多项式路径，L 至少要多长？找到并运行一次（不超限）。", "To run at 2 m/s on the quintic path, how long must L be? Find it and run once within the limit."],
      demo: { scene: "agv", set: { p: 3, L: 4.8, v: 2 }, press: ["start"], wait: 8 } },
  ],
  think: ["三次多项式路径的最大曲率在入口处，余弦路径的最大曲率比五次多项式路径还小，为什么工程上仍偏爱五次多项式（或回旋线）？想想转向机构能不能瞬间改变转弯半径。",
          "The cubic path is sharpest at its entry and the cosine path has a smaller peak curvature than the quintic one; why do engineers still prefer the quintic (or a clothoid)? Think about whether the steering can change the turning radius instantly."],

  A: 1.0, B: 0.5,
  F(f) {
    return [
      [(x) => x * x, (x) => 2 * x, () => 2, -2, 2],
      [Math.sin, Math.cos, (x) => -Math.sin(x), -2, 3],
      [Math.exp, Math.exp, Math.exp, -2, 2],
      [(x) => x ** 3, (x) => 3 * x * x, (x) => 6 * x, -1.5, 1.5],
      [Math.log, (x) => 1 / x, (x) => -1 / (x * x), 0.05, 3],
    ][f - 1];
  },
  lane(p, L) {
    const d = 1, s = (x) => x / L;
    if (p === 1) return [(x) => d * (3 * s(x) ** 2 - 2 * s(x) ** 3), (x) => d / L * (6 * s(x) - 6 * s(x) ** 2), (x) => d / L ** 2 * (6 - 12 * s(x))];
    if (p === 2) return [(x) => d * (1 - Math.cos(Math.PI * s(x))) / 2, (x) => d * Math.PI / (2 * L) * Math.sin(Math.PI * s(x)), (x) => d * Math.PI ** 2 / (2 * L * L) * Math.cos(Math.PI * s(x))];
    return [(x) => d * (10 * s(x) ** 3 - 15 * s(x) ** 4 + 6 * s(x) ** 5), (x) => d / L * (30 * s(x) ** 2 - 60 * s(x) ** 3 + 30 * s(x) ** 4),
            (x) => d / L ** 2 * (60 * s(x) - 180 * s(x) ** 2 + 120 * s(x) ** 3)];
  },
  kap(yp, ypp, x) { return Math.abs(ypp(x)) / Math.pow(1 + yp(x) ** 2, 1.5); },
  kmax(p, L) {
    const [, yp, ypp] = this.lane(p, L);
    let m = 0;
    for (let i = 0; i <= 2000; i++) m = Math.max(m, this.kap(yp, ypp, L * i / 2000));
    return m;
  },
  reset(api, s) { s.x = -1.5; s.peak = 0; s.done = false; s.slip = false; s.run = null; },
  update(dt, api, s) {
    if (api.scene !== "agv") { api.stop(); return; }
    const { p, L, v } = api.p, [, yp, ypp] = this.lane(p, L);
    if (!s.run) s.run = { p, L, v };
    if (s.run.p !== p || s.run.L !== L || s.run.v !== v) s.changed = true;
    const k = s.x > 0 && s.x < L ? this.kap(yp, ypp, s.x) : 0;
    s.x += v * dt / Math.sqrt(1 + (s.x > 0 && s.x < L ? yp(s.x) ** 2 : 0));
    s.peak = Math.max(s.peak, v * v * k);
    if (v * v * k > this.A + 1e-9) s.slip = true;
    if (s.x >= L + 1.5) { s.done = true; api.stop(); }
  },
  readouts(api, s) {
    if (api.scene === "curve") {
      const [f, fp, fpp, lo, hi] = this.F(api.p.f), x = api.p.x;
      if (x < lo || x > hi) return [[["提示", "Note"], api.T("探测点超出这条曲线的显示范围", "Probe outside this curve's range")]];
      const k = this.kap(fp, fpp, x);
      let km = 0; for (let i = 0; i <= 4000; i++) km = Math.max(km, this.kap(fp, fpp, lo + (hi - lo) * i / 4000));
      if (api.p.f === 3 && Math.abs(x + Math.LN2 / 2) < 0.02) api.done("exp");
      return [[["y′", "y′"], fp(x).toFixed(4)], [["y″", "y″"], fpp(x).toFixed(4)], [["曲率 κ", "Curvature κ"], k.toFixed(4)],
              [["曲率半径 R = 1/κ", "Radius R = 1/κ"], k > 1e-9 ? (1 / k).toFixed(3) : "∞"], [["本段曲线的最大曲率", "Largest κ on this range"], km.toFixed(4)]];
    }
    const { p, L, v } = api.p, km = this.kmax(p, L), [, yp, ypp] = this.lane(p, L), vmax = Math.sqrt(this.A / km);
    const fair = s.done && !s.changed && s.run && s.run.p === p && s.run.L === L && s.run.v === v;
    if (fair && !s.slip && p === 3 && Math.abs(L - 4) < 0.05 && v > vmax - 0.03) api.done("fast");
    if (fair && s.slip && p === 1 && Math.abs(L - 4) < 0.05 && Math.abs(v - 1.7) < 0.005) api.done("slip");
    if (fair && !s.slip && p === 3 && v >= 1.995) api.done("long");
    return [[["路径的最大曲率 κ_max", "Largest curvature κ_max"], km.toFixed(4) + " 1/m"], [["入口处的曲率", "Curvature at entry"], this.kap(yp, ypp, 0).toFixed(4) + " 1/m"],
            [["允许的最高车速 √(a/κ_max)", "Highest allowed speed √(a/κ_max)"], (Math.floor(vmax * 1000) / 1000).toFixed(3) + " m/s"],
            [["当前车速下的最大侧向加速度", "Peak lateral acceleration at this speed"], (v * v * km).toFixed(2) + " m/s²"],
            [["过最急处的角速度 vκ", "Turn rate at the sharpest point vκ"], (v * km).toFixed(3) + " rad/s"],
            [["运行结果", "Run result"], s.done ? (s.slip ? api.T("超限：货物滑动", "Limit exceeded: load slides") : api.T("通过", "Passed")) : "—"]];
  },
  draw(api, s) {
    const w = api.w, h = api.h, ink = api.css("--ink"), red = api.css("--red"), mu = api.css("--muted"), blue = api.css("--blue");
    const circ = (G, cx, cy, R, c) => { const P = []; for (let i = 0; i <= 200; i++) { const t = 2 * Math.PI * i / 200; P.push([cx + R * Math.cos(t), cy + R * Math.sin(t)]); } G.pts(P, c, 1.5); };
    if (api.scene === "curve") {
      const [f, fp, fpp, lo, hi] = this.F(api.p.f), x = api.p.x;
      const ys = []; for (let i = 0; i <= 200; i++) ys.push(f(lo + (hi - lo) * i / 200));
      const ymin = Math.min(...ys), ymax = Math.max(...ys), span = Math.max(hi - lo, ymax - ymin) * 1.15;
      const cxm = (lo + hi) / 2, cym = (ymin + ymax) / 2, asp = (w - 80) / (h - 74);
      const G = api.graph({ x: 60, y: 24, w: w - 80, h: h - 74, xmin: cxm - span * asp / 2, xmax: cxm + span * asp / 2, ymin: cym - span / 2, ymax: cym + span / 2, xlabel: "x", ylabel: "y" });
      G.axes(); G.fn(f, ink, 2.2, null, lo, hi);
      if (x >= lo && x <= hi) {
        const k = this.kap(fp, fpp, x);
        if (k > 1e-6) { const R = 1 / k, n = Math.hypot(-fp(x), 1), sg = Math.sign(fpp(x)); circ(G, x - sg * R * fp(x) / n, f(x) + sg * R / n, R, red); }
        G.point(x, f(x), blue, "P");
      }
      return;
    }
    const { p, L, v } = api.p, [y, yp, ypp] = this.lane(p, L);
    const gTop = api.graph({ x: 60, y: 24, w: w - 80, h: (h - 110) * 0.5, xmin: -1.5, xmax: L + 1.5, ymin: -0.5, ymax: 1.5, xlabel: "x / m", ylabel: "y / m" });
    gTop.axes();
    const path = (t) => (t <= 0 ? 0 : t >= L ? 1 : y(t));
    gTop.fn(path, ink, 3);
    const X = s.x, Y = path(X);
    gTop.point(X, Y, s.slip ? red : blue, "AGV");
    const gBot = api.graph({ x: 60, y: 24 + (h - 110) * 0.5 + 46, w: w - 80, h: (h - 110) * 0.5, xmin: -1.5, xmax: L + 1.5, ymin: 0, ymax: 2.5, xlabel: "x / m",
      ylabel: api.T("侧向加速度 v²κ / (m/s²)", "lateral acceleration v²κ / (m/s²)") });
    gBot.axes();
    gBot.fn((t) => (t <= 0 || t >= L ? 0 : v * v * this.kap(yp, ypp, t)), red, 2);
    gBot.hline(this.A, mu);
    gBot.vline(X, blue);
  },
});
