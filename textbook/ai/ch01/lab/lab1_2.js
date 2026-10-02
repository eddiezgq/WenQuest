// 实验 1.2 感知机学习演示（配 1.2.3–1.2.5 节）。
// 学习规则：判错（y·w·x̃ ≤ 0）时 w ← w + η y x̃，x̃ = (x₁, x₂, 1)；从 w = 0 出发，按数据的固定顺序循环。
// 零件检验数据与 code/_perceptron.py 的 PARTS 相同（x₁ 外径偏差的绝对值、x₂ 圆度误差，单位 10 μm）；
// R 与 γ* 由程序 1.2.1 算出（R = 3.6332，γ* = 0.14725，界 (R/γ*)² ≈ 609）。
WQ.lab({
  title: ["实验 1.2 感知机学习演示", "Lab 1.2 Watching a perceptron learn"],
  goal: ["逐个样本运行感知机学习规则，观察每次判错时权重向量和分界线怎样移动，比较线性可分与不可分两种情形。",
         "Run the perceptron rule sample by sample, watch how the weight vector and the boundary move at each mistake, and compare a separable with a non-separable case."],
  scenes: [
    { id: "parts", name: ["零件检验", "Part inspection"],
      problem: { title: ["工程问题：用一条直线分开合格品与不合格品", "Engineering problem: one line between accepted and rejected parts"],
                 text: ["30 根轴的外径偏差与圆度误差（单位 10 μm），圆点合格、方块不合格。按“开始”，看感知机多少次更新后全部分对。",
                        "Diameter deviation and roundness error of 30 shafts (units of 10 μm); circles accepted, squares rejected. Press Start and see how many updates it takes."] } },
    { id: "xor", name: ["异或", "XOR"],
      problem: { title: ["四个点，一条直线够不够？", "Four points: is one line enough?"],
                 text: ["(0,0)、(1,1) 为一类，(0,1)、(1,0) 为另一类。让感知机学习 20 轮以上，看它能否停下来。",
                        "(0,0), (1,1) form one class, (0,1), (1,0) the other. Let the perceptron run for more than 20 epochs: does it ever stop?"] } },
    { id: "mail", name: ["垃圾邮件", "Spam"],
      problem: { title: ["生活中的例子：两个特征分辨垃圾邮件", "Everyday example: spotting spam with two features"],
                 text: ["横轴是邮件里可疑词的个数，纵轴是链接的个数。圆点是正常邮件，方块是垃圾邮件。",
                        "Horizontal: number of suspicious words; vertical: number of links. Circles are normal mail, squares spam."] } },
  ],
  params: [
    { id: "eta", name: ["学习率 η", "Learning rate η"], min: 0.1, max: 2, step: 0.1, value: 1, digits: 1 },
    { id: "speed", name: ["速度（样本/秒）", "Speed (samples/s)"], min: 1, max: 30, step: 1, value: 6, digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "step", name: ["单步", "One step"] },
            { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--blue)", name: ["y = +1", "y = +1"] }, { color: "var(--red)", name: ["y = −1", "y = −1"] },
           { color: "var(--amber)", name: ["分界线与 w", "boundary and w"] }],
  tasks: [
    { id: "conv", text: ["在零件检验数据上学到全部分对，记下更新次数，与诺维科夫界比较。", "Learn the part data until no mistakes remain; note the number of updates and compare it with Novikoff's bound."],
      demo: { scene: "parts", set: { eta: 1, speed: 30 }, press: ["start"], wait: 9 } },
    { id: "eta", text: ["把学习率改为 0.1 再学一次，更新次数变了吗？", "Set the learning rate to 0.1 and learn again: does the number of updates change?"],
      demo: { scene: "parts", set: { eta: 0.1, speed: 30 }, press: ["start"], wait: 9 } },
    { id: "xor", text: ["让感知机在异或数据上学满 20 轮，确认它停不下来。", "Run 20 epochs on XOR and confirm it never stops."],
      demo: { scene: "xor", set: { speed: 30 }, press: ["start"], wait: 4 } },
    { id: "mail", text: ["生活场景：学到一条分开正常邮件和垃圾邮件的直线。", "Everyday scene: learn a line between normal mail and spam."],
      demo: { scene: "mail", set: { speed: 30 }, press: ["start"], wait: 4 } },
  ],
  think: ["感知机学到的分界线与最大间隔的分界线哪个对测量误差更稳健？在图上找出离感知机分界线最近的零件。",
          "Which is more robust to measurement error, the perceptron's line or the maximum-margin line? Find the part closest to the perceptron's line."],

  DATA: {
    parts: [[0.2, 0.4, 1], [0.6, 0.2, 1], [0.4, 1.2, 1], [1.0, 0.6, 1], [0.2, 1.8, 1], [1.4, 0.2, 1], [0.8, 1.0, 1],
            [0.0, 0.8, 1], [1.2, 1.0, 1], [0.6, 1.6, 1], [1.6, 0.4, 1], [0.2, 2.2, 1], [1.0, 1.2, 1], [0.4, 0.6, 1],
            [1.8, 0.0, 1],
            [2.6, 0.4, -1], [2.2, 1.0, -1], [1.6, 1.6, -1], [1.0, 2.4, -1], [0.4, 3.0, -1], [2.8, 1.8, -1], [1.8, 2.6, -1],
            [0.8, 3.4, -1], [3.0, 0.6, -1], [2.4, 2.4, -1], [1.2, 3.0, -1], [0.0, 3.4, -1], [2.6, 1.2, -1], [1.4, 2.0, -1],
            [2.0, 1.6, -1]],
    xor: [[0, 0, -1], [1, 1, -1], [0, 1, 1], [1, 0, 1]],
    mail: [[0, 0, 1], [1, 0, 1], [0, 1, 1], [2, 1, 1], [1, 2, 1], [3, 0, 1], [0, 2, 1], [2, 0, 1],
           [5, 4, -1], [6, 2, -1], [4, 5, -1], [7, 3, -1], [3, 6, -1], [6, 6, -1], [5, 7, -1], [8, 1, -1]],
  },
  BOX: { parts: [-0.2, 3.4, -0.2, 3.8], xor: [-0.4, 1.4, -0.4, 1.4], mail: [-0.6, 8.6, -0.6, 7.6] },
  BOUND: { parts: 609 },

  data(api) { return this.DATA[api.scene]; },
  reset(api, s) { s.w = [0, 0, 0]; s.i = 0; s.epoch = 1; s.k = 0; s.err = 0; s.acc = 0; s.conv = false; s.cur = -1;
                  s.wrong = false; s.hist = []; s.etaUsed = api.p.eta; },
  step(api, s) {
    const D = this.data(api), d = D[s.i], x = [d[0], d[1], 1], y = d[2];
    const z = s.w[0] * x[0] + s.w[1] * x[1] + s.w[2];
    s.cur = s.i; s.wrong = y * z <= 0;
    if (s.wrong) { for (let j = 0; j < 3; j++) s.w[j] += api.p.eta * y * x[j]; s.k += 1; s.err += 1; }
    s.i += 1;
    if (s.i === D.length) {
      s.hist.push([s.epoch, s.err]);
      if (s.err === 0) s.conv = true;
      s.i = 0; s.epoch += 1; s.err = 0;
    }
  },
  check(api, s) {
    if (api.scene === "parts" && s.conv && s.etaUsed >= 0.95) api.done("conv");
    if (api.scene === "parts" && s.conv && s.etaUsed <= 0.15) api.done("eta");
    if (api.scene === "xor" && s.hist.length >= 20 && s.hist[s.hist.length - 1][1] > 0) api.done("xor");
    if (api.scene === "mail" && s.conv) api.done("mail");
  },
  update(dt, api, s) {
    s.acc += dt * api.p.speed;
    while (s.acc >= 1 && !s.conv) { s.acc -= 1; this.step(api, s); }
    this.check(api, s);
    if (s.conv || s.hist.length >= 60) api.stop();
  },
  action(id, api, s) {
    if (id === "step" && !s.conv) { this.step(api, s); this.check(api, s); }
  },
  change(api, s, pid) { if (pid === "eta") s.etaUsed = api.p.eta; },
  readouts(api, s) {
    const b = this.BOUND[api.scene];
    return [[["轮次 / 本轮已出错", "Epoch / mistakes so far"], (s.conv ? s.epoch - 1 : s.epoch) + " / " + (s.conv ? 0 : s.err)],
            [["更新次数 k", "Updates k"], String(s.k)],
            [["诺维科夫界 (R/γ*)²", "Novikoff bound (R/γ*)²"], b ? "≈ " + b : "—"],
            [["w = (w₁, w₂, b)", "w = (w₁, w₂, b)"], "(" + s.w.map((v) => api.fmt(v, 2)).join(", ") + ")"],
            [["状态", "Status"], s.conv ? api.T("全部分对，停止", "all correct, stopped") : api.T("学习中", "learning")]];
  },
  draw(api, s) {
    const { w, h } = api, m = 14, D = this.data(api), B = this.BOX[api.scene];
    const side = Math.min(h - 2 * m - 16, w * 0.58), x0 = m + 34, y0 = m + 6;
    const X = (v) => x0 + (v - B[0]) / (B[1] - B[0]) * side, Y = (v) => y0 + side - (v - B[2]) / (B[3] - B[2]) * side;
    api.rect(x0, y0, side, side, null, api.css("--grid"));
    const muted = api.css("--muted"), blue = api.css("--blue"), red = api.css("--red"), amber = api.css("--amber");
    if (B[2] < 0) api.line(x0, Y(0), x0 + side, Y(0), api.css("--grid"), 1);
    if (B[0] < 0) api.line(X(0), y0, X(0), y0 + side, api.css("--grid"), 1);
    // the half-plane judged +1 and the boundary w1 x1 + w2 x2 + b = 0
    const [a, c, b] = s.w;
    if (Math.abs(a) + Math.abs(c) > 1e-9) {
      const pts = [];
      const tryX = (xx) => { if (Math.abs(c) > 1e-9) { const yy = -(a * xx + b) / c; if (yy >= B[2] && yy <= B[3]) pts.push([xx, yy]); } };
      const tryY = (yy) => { if (Math.abs(a) > 1e-9) { const xx = -(c * yy + b) / a; if (xx >= B[0] && xx <= B[1]) pts.push([xx, yy]); } };
      tryX(B[0]); tryX(B[1]); tryY(B[2]); tryY(B[3]);
      if (pts.length >= 2) {
        api.line(X(pts[0][0]), Y(pts[0][1]), X(pts[1][0]), Y(pts[1][1]), amber, 3);
        const mx = (pts[0][0] + pts[1][0]) / 2, my = (pts[0][1] + pts[1][1]) / 2, n = Math.hypot(a, c);
        const L = 0.12 * (B[1] - B[0]);
        api.arrow(X(mx), Y(my), X(mx + L * a / n), Y(my + L * c / n), amber, 2.5);
        api.label("w", X(mx + 1.15 * L * a / n), Y(my + 1.15 * L * c / n), amber, 14, "center");
      }
    }
    D.forEach((d, i) => {
      const px = X(d[0]), py = Y(d[1]), col = d[2] > 0 ? blue : red;
      const ok = d[2] * (a * d[0] + c * d[1] + b) > 0;
      if (d[2] > 0) api.circle(px, py, 6, api.css("--panel"), col); else api.rect(px - 5.5, py - 5.5, 11, 11, col, col);
      if (!ok) api.circle(px, py, 10, null, muted);
      if (i === s.cur) api.circle(px, py, 14, null, s.wrong ? red : api.css("--green"));
    });
    const names = { parts: [["x₁（10 μm）", "x₁ (10 μm)"], ["x₂（10 μm）", "x₂ (10 μm)"]], xor: [["x₁", "x₁"], ["x₂", "x₂"]],
                    mail: [["可疑词个数", "suspicious words"], ["链接个数", "links"]] }[api.scene];
    api.label(api.T(...names[0]), x0 + side, y0 + side + 14, muted, 12, "right");
    api.label(api.T(...names[1]), x0 - 30, y0 - 2, muted, 12, "left");
    // right: mistakes per epoch
    const px = x0 + side + 40, pw = w - px - m, py = y0 + 20, ph = side - 40;
    if (pw > 60) {
      const n = Math.max(10, s.hist.length), top = Math.max(4, ...s.hist.map((q) => q[1]));
      api.plot(px, py, pw, ph, [{ pts: s.hist, color: api.css("--accent") }],
               { xmin: 0, xmax: n, ymin: 0, ymax: top, xlabel: api.T("轮次", "epoch"), ylabel: api.T("每轮出错数", "mistakes per epoch") });
    }
  },
});
