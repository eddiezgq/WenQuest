// 实验 4.2 运动图像（配 4.2 节）。
// 编排场景：目标 x–t 图由 4 段匀速运动组成（每段 3 s，速度学生不知道），学生用 4 个滑块设定各段速度，让 AGV 的 x–t 图与目标重合，
// 点“提交”判定（每段相差 0.05 m/s 以内）。识图场景：给出一幅 v–t 图，从 A～D 四幅 x–t 图中选出对应的一幅。
// 短跑场景：给出博尔特 9.58 s 百米的 10 m 分段时间，学生算出最快一段的平均速度并提交（相差 0.05 m/s 以内）。
const TGT42 = [0.8, 0.0, -0.6, 0.3], X0_42 = 1.0, SEG42 = 3;     // 目标各段速度（m/s）与初始位置
function path42(vs) { const pts = [[0, X0_42]]; let x = X0_42; vs.forEach((v, i) => { x += v * SEG42; pts.push([(i + 1) * SEG42, x]); }); return pts; }
// 识图：两道题。第一题 v–t 图为 +0.5 m/s（0～4 s）、0（4～6 s）、−1.0 m/s（6～8 s）；答错一次就换成第二题（选项顺序也不同），
// 第二题答错再换回第一题，这样不能靠逐个试出答案。题号放在闭包里，重置时不变。
const Q42 = [
  { vt: [[0, 0.5], [4, 0.5], [4, 0], [6, 0], [6, -1], [8, -1]], ans: "C", opt: {
    A: [[0, 0.5], [4, 0.5], [4, 0], [6, 0], [6, -1], [8, -1]],     // 把 v–t 图照搬过来
    B: [[0, 0], [4, -2], [6, -2], [8, 0]],                           // 方向反了
    C: [[0, 0], [4, 2], [6, 2], [8, 0]],                             // 正确
    D: [[0, 0], [4, 2], [6, 2], [8, -2]] } },                        // 第三段的斜率错了
  { vt: [[0, -0.5], [2, -0.5], [2, 1], [6, 1], [6, 0], [8, 0]], ans: "A", opt: {
    A: [[0, 0], [2, -1], [6, 3], [8, 3]],                            // 正确
    B: [[0, -0.5], [2, -0.5], [2, 1], [6, 1], [6, 0], [8, 0]],       // 照搬
    C: [[0, 0], [2, 1], [6, -3], [8, -3]],                           // 方向反了
    D: [[0, 0], [2, -1], [6, 3], [8, 0]] } },                        // 第三段不是静止
];
const st42 = { q: 0 };
const KEYS42 = ["A", "B", "C", "D"];
const BX42 = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], BT42 = [0, 1.89, 2.88, 3.78, 4.64, 5.47, 6.29, 7.10, 7.92, 8.75, 9.58];
const BV42 = BX42.slice(1).map((x, i) => 10 / (BT42[i + 1] - BT42[i])), BMAX42 = Math.max(...BV42);

WQ.lab({
  title: ["实验 4.2 运动图像", "Lab 4.2 Motion graphs"],
  goal: ["由 x–t 图读速度，由速度画出 x–t 图；从 v–t 图找出对应的 x–t 图；由分段时间算出平均速度。",
         "Read velocities from an x–t graph and build an x–t graph from velocities; match a v–t graph to its x–t graph; compute mean speeds from split times."],
  scenes: [
    { id: "match", robot: true, name: ["编排 AGV 的运动", "Programming the AGV"], hide: ["pick", "vb"],
      problem: { title: ["机器人问题：让 AGV 走出指定的 x–t 图", "Robot problem: make the AGV follow a given x–t graph"],
                 text: ["灰线是调度系统要求的 x–t 图，由 4 段匀速运动组成，每段 3 s。从灰线读出每段的速度（斜率），用滑块设定，点“提交”。提交后才画出 AGV 实际走出的 x–t 图（蓝线）。",
                        "The grey line is the x–t graph the dispatcher wants: four 3 s stretches at constant velocity. Read each velocity (slope) from it, set the sliders and press “Submit”; only then is the AGV's actual x–t graph (blue) drawn."] } },
    { id: "pick", name: ["识图", "Reading graphs"], hide: ["v1", "v2", "v3", "v4", "vb"],
      problem: { title: ["哪一幅 x–t 图对应这幅 v–t 图", "Which x–t graph goes with this v–t graph"],
                 text: ["上面是一个物体的 v–t 图（t = 0 时位于 x = 0）。下面 A～D 四幅 x–t 图中，只有一幅是它的。选出来，点“提交”。",
                        "Above is the v–t graph of a body that starts at x = 0. Only one of the x–t graphs A–D below belongs to it. Pick it and press “Submit”."] } },
    { id: "bolt", name: ["百米赛跑", "The 100 m sprint"], hide: ["v1", "v2", "v3", "v4", "pick"],
      problem: { title: ["生活中的例子：博尔特什么时候跑得最快", "Everyday example: when was Bolt fastest"],
                 text: ["表中是博尔特 2009 年 9.58 s 百米世界纪录的分段时间（从发令枪响起算）。算出每 10 m 的平均速度，找出最快的一段，把它的平均速度调到滑块上，点“提交”。",
                        "The table gives the split times of Bolt’s 9.58 s world record in 2009 (from the gun). Work out the mean speed of each 10 m, find the fastest stretch, set its mean speed and press “Submit”."] } },
  ],
  params: [
    { id: "v1", name: ["第 1 段速度（0～3 s）", "Velocity, stretch 1 (0–3 s)"], min: -1.5, max: 1.5, step: 0.05, value: 0, unit: "m/s", digits: 2 },
    { id: "v2", name: ["第 2 段速度（3～6 s）", "Velocity, stretch 2 (3–6 s)"], min: -1.5, max: 1.5, step: 0.05, value: 0, unit: "m/s", digits: 2 },
    { id: "v3", name: ["第 3 段速度（6～9 s）", "Velocity, stretch 3 (6–9 s)"], min: -1.5, max: 1.5, step: 0.05, value: 0, unit: "m/s", digits: 2 },
    { id: "v4", name: ["第 4 段速度（9～12 s）", "Velocity, stretch 4 (9–12 s)"], min: -1.5, max: 1.5, step: 0.05, value: 0, unit: "m/s", digits: 2 },
    { id: "pick", name: ["你选的 x–t 图：1 为 A，2 为 B，3 为 C，4 为 D", "Your choice: 1 A, 2 B, 3 C, 4 D"], min: 1, max: 4, step: 1, value: 1, unit: "", digits: 0 },
    { id: "vb", name: ["最快一段的平均速度", "Mean speed of the fastest stretch"], min: 8, max: 14, step: 0.01, value: 10, unit: "m/s", digits: 2 },
  ],
  buttons: [{ id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "match", robot: true, text: ["编排：从灰线读出 4 段速度，设好后提交，让 AGV 的 x–t 图与目标重合。哪一段 AGV 在倒车？",
                                      "Programming: read the four velocities off the grey line so that the AGV's x–t graph matches, and submit. In which stretch is the AGV reversing?"],
      demo: { scene: "match", set: { v1: 0.8, v2: 0, v3: -0.6, v4: 0.3 }, press: ["submit"], wait: 1 } },
    { id: "pick", text: ["识图：选出与 v–t 图对应的 x–t 图，提交。其余三幅各错在哪里？", "Graphs: pick the x–t graph that matches the v–t graph and submit. What is wrong with each of the other three?"],
      demo: { scene: "pick", set: { pick: 3 }, press: ["submit"], wait: 1 } },
    { id: "bolt", text: ["百米：算出最快一段 10 m 的平均速度，提交（相差 0.05 m/s 以内）。它在哪一段？", "Sprint: work out the mean speed of the fastest 10 m and submit it (within 0.05 m/s). Which stretch is it?"],
      demo: { scene: "bolt", set: { vb: 12.35 }, press: ["submit"], wait: 1 } },
  ],
  think: ["x–t 图的斜率是速度，v–t 图下的面积是位移。识图场景中，A 图错在哪里？为什么“照搬形状”是读图时最常见的错误？",
          "The slope of an x–t graph is the velocity and the area under a v–t graph is the displacement. What is wrong with graph A, and why is copying the shape the most common mistake?"],

  reset(api, s) {},
  change(api, s, pid) { s.msg = ""; if (/^v\d$/.test(pid)) s.shown = false; },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "match") ok = TGT42.every((v, i) => Math.abs(p["v" + (i + 1)] - v) < 0.05);
    if (api.scene === "pick") { ok = KEYS42[p.pick - 1] === Q42[st42.q].ans; if (!ok) st42.q = 1 - st42.q; }
    if (api.scene === "bolt") ok = Math.abs(p.vb - BMAX42) < 0.05;
    if (ok) api.done(api.scene);
    s.msg = ok ? api.T("对了", "correct") : api.scene === "pick" ? api.T("不对，换一道题再试", "wrong; here is another graph") : api.T("还不对", "not yet");
    if (api.scene === "match") s.shown = true;
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "match") {
      const mine = path42([p.v1, p.v2, p.v3, p.v4]), tgt = path42(TGT42);
      const dev = Math.max(...mine.map((q, i) => Math.abs(q[1] - tgt[i][1])));
      return s.shown ? [[["AGV 的终点", "AGV end point"], f(mine[4][1], 2) + " m"], [["与目标的最大偏差", "Largest deviation"], f(dev, 2) + " m"], sub]
        : [[["AGV 的 x–t 图", "AGV's x–t graph"], api.T("提交后显示", "shown after submitting")], sub];
    }
    if (api.scene === "pick") return [[["你选的", "Your choice"], KEYS42[p.pick - 1]], sub];
    return [[["全程平均速度", "Mean speed over 100 m"], f(100 / 9.58, 2) + " m/s"], [["你填的最快一段", "Your fastest stretch"], f(p.vb, 2) + " m/s"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, blue = css("--blue"), mut = css("--muted"), ink = css("--ink"), red = css("--red");
    if (api.scene === "match") {
      const G = api.graph({ x: 56, y: 22, w: w - 90, h: h - 120, xmin: 0, xmax: 12, ymin: -2, ymax: 6, xlabel: "t / s", ylabel: "x / m" }).axes();
      G.pts(path42(TGT42), "#b8c2c8", 7);
      if (s.shown) G.pts(path42([p.v1, p.v2, p.v3, p.v4]), blue, 2.5);
      [1, 2, 3].forEach((k) => G.vline(k * SEG42));
      const xn = path42([p.v1, p.v2, p.v3, p.v4]);
      const X = (x) => 56 + (x + 2) / 8 * (w - 90);                 // 下方的通道示意：AGV 在终点的位置
      api.line(56, h - 40, w - 34, h - 40, mut, 2); if (s.shown) api.agv(Math.max(60, Math.min(w - 40, X(xn[4][1]))), h - 42, 44);
      api.label(api.T("通道（x 从 −2 m 到 6 m），AGV 停在终点", "aisle (x from −2 m to 6 m), AGV at its end point"), 56, h - 12, mut, 11);
      return;
    }
    if (api.scene === "pick") {
      const vtG = api.graph({ x: 56, y: 20, w: w * 0.5, h: h * 0.3, xmin: 0, xmax: 8, ymin: -1.2, ymax: 1.2, xlabel: "t / s", ylabel: "v / (m/s)" }).axes();
      vtG.pts(Q42[st42.q].vt, red, 2.5);
      const gw = (w - 100) / 4 - 14;
      KEYS42.forEach((k, i) => {
        const G = api.graph({ x: 56 + i * (gw + 22), y: h * 0.3 + 76, w: gw, h: h * 0.4, xmin: 0, xmax: 8, ymin: -2.5, ymax: 2.5, xlabel: "t", ylabel: "x", ticks: false }).axes();
        G.pts(Q42[st42.q].opt[k], KEYS42[p.pick - 1] === k ? blue : ink, KEYS42[p.pick - 1] === k ? 3 : 1.8);
        api.label(k, G.o.x + gw / 2, G.o.y - 8, KEYS42[p.pick - 1] === k ? blue : ink, 15, "center");
      });
      return;
    }
    api.label(api.T("距离 / m", "distance / m"), 30, 24, mut, 12); api.label(api.T("时刻 / s", "time / s"), 140, 24, mut, 12);
    BX42.slice(1).forEach((x, i) => { api.label(String(x), 30, 44 + i * 19, ink, 12); api.label(BT42[i + 1].toFixed(2), 140, 44 + i * 19, ink, 12); });
    api.label(api.T("起跑反应时间 0.146 s，已含在第一段中", "reaction time 0.146 s, included in the first split"), 30, 44 + 10 * 19 + 6, mut, 11);
    const G = api.graph({ x: w * 0.42, y: 24, w: w * 0.54, h: h - 90, xmin: 0, xmax: 10, ymin: 0, ymax: 100, xlabel: "t / s", ylabel: "x / m" }).axes();
    G.dots(BX42.map((x, i) => [BT42[i], x]), blue, 4).pts(BX42.map((x, i) => [BT42[i], x]), blue, 1.2);
  },
});
