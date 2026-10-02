// 实验 2.5 两层网络训练演示台（配 2.4、2.5 节）。
// 网络：输入 2 维 → m 个隐藏单元（ReLU 或 tanh）→ 1 个 logit；损失为交叉熵；全批梯度下降；反向传播按式 (2.5.3)～(2.5.6)。
// “月牙”数据与 code/_ch2.py 的 moons 同一构造（半圆 + 高斯噪声 σ = 0.12），但随机数由本页的确定性生成器产生，点的位置与程序 2.5.2 不同。
WQ.lab({
  title: ["实验 2.5 两层网络训练演示台", "Lab 2.5 Training a two-layer network"],
  goal: ["改变隐藏单元数、激活函数和学习率，观察两层网络怎样学出弯曲的分界线，比较没有隐藏层的逻辑回归。",
         "Vary the hidden units, the activation and the learning rate; watch a two-layer network learn a curved boundary and compare it with logistic regression."],
  scenes: [
    { id: "moons", name: ["月牙", "Moons"],
      problem: { title: ["问题：一条直线分不开两个月牙", "Problem: no straight line separates the moons"],
                 text: ["隐藏单元数为 0 时就是逻辑回归。逐步增加隐藏单元，按“开始”训练，看分界线怎样弯曲。",
                        "With 0 hidden units this is logistic regression. Add hidden units and press Start; watch the boundary bend."] } },
    { id: "xor", name: ["异或", "XOR"],
      problem: { title: ["四团点：异或", "Four clusters: XOR"],
                 text: ["第一、三象限为一类，第二、四象限为另一类。至少要几个隐藏单元？", "Quadrants I and III are one class, II and IV the other. How many hidden units are needed?"] } },
    { id: "target", name: ["靶心", "Target"],
      problem: { title: ["生活中的例子：射击靶纸上的中环", "Everyday example: the rings of a target"],
                 text: ["落在中间圆内的弹孔记为一类，外环的记为另一类。网络要学出一个封闭的圆形分界。",
                        "Holes inside the inner circle are one class, outer ring the other. The network must learn a closed boundary."] } },
  ],
  params: [
    { id: "m", name: ["隐藏单元数 m", "Hidden units m"], min: 0, max: 32, step: 1, value: 8, digits: 0 },
    { id: "act", name: ["激活函数（0 ReLU · 1 tanh）", "Activation (0 ReLU · 1 tanh)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "eta", name: ["学习率 η", "Learning rate η"], min: 0.05, max: 3, step: 0.05, value: 0.5, digits: 2 },
    { id: "speed", name: ["每帧步数", "Steps per frame"], min: 1, max: 50, step: 1, value: 20, digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--blue)", name: ["类别 1", "class 1"] }, { color: "var(--red)", name: ["类别 0", "class 0"] }],
  tasks: [
    { id: "lr", text: ["月牙：隐藏单元数为 0（逻辑回归）时训练 1000 步以上，记下训练准确率。", "Moons: with 0 hidden units (logistic regression) train at least 1000 steps and note the accuracy."],
      demo: { scene: "moons", set: { m: 0, eta: 0.5, speed: 50 }, press: ["start"], wait: 6 } },
    { id: "moons", text: ["月牙：用隐藏层把训练准确率提高到 99% 以上。", "Moons: use a hidden layer to reach more than 99% training accuracy."],
      demo: { scene: "moons", set: { m: 16, act: 0, eta: 0.5, speed: 50 }, press: ["start"], wait: 8 } },
    { id: "xor", text: ["异或：找到能把准确率提高到 100% 的最少隐藏单元数。", "XOR: find the fewest hidden units that reach 100% accuracy."],
      demo: { scene: "xor", set: { m: 4, act: 0, eta: 0.5, speed: 50 }, press: ["start"], wait: 6 } },
    { id: "big", text: ["把学习率调到 3，观察损失曲线，说明发生了什么。", "Set the learning rate to 3, watch the loss curve and explain what happens."],
      demo: { scene: "moons", set: { m: 16, eta: 3, speed: 50 }, press: ["start"], wait: 4 } },
    { id: "target", text: ["生活场景：学出靶心的圆形分界，准确率达到 98% 以上。", "Everyday scene: learn the round boundary of the target with more than 98% accuracy."],
      demo: { scene: "target", set: { m: 12, act: 1, eta: 0.5, speed: 50 }, press: ["start"], wait: 8 } },
  ],
  think: ["隐藏单元为 ReLU 时，学到的分界线由若干段直线组成。段数与隐藏单元数有什么关系？", "With ReLU units the learned boundary is made of straight pieces. How does the number of pieces relate to the number of hidden units?"],

  rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; },
  gauss(r) { const u = Math.max(r(), 1e-12), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  data(scene) {
    const r = this.rng({ moons: 7, xor: 11, target: 5 }[scene]), P = [];
    if (scene === "moons") {
      for (let i = 0; i < 100; i++) { const t = Math.PI * i / 99;
        P.push([Math.cos(t) + 0.12 * this.gauss(r), Math.sin(t) + 0.12 * this.gauss(r), 0]);
        P.push([1 - Math.cos(t) + 0.12 * this.gauss(r), 0.5 - Math.sin(t) + 0.12 * this.gauss(r), 1]); }
    } else if (scene === "xor") {
      for (let i = 0; i < 200; i++) { const sx = r() < 0.5 ? -1 : 1, sy = r() < 0.5 ? -1 : 1;
        P.push([sx * (0.5 + 0.35 * r()) + 0.08 * this.gauss(r), sy * (0.5 + 0.35 * r()) + 0.08 * this.gauss(r), sx * sy > 0 ? 1 : 0]); }
    } else {
      for (let i = 0; i < 220; i++) { const a = 2 * Math.PI * r(), inner = i % 2 === 0, rad = inner ? 0.55 * Math.sqrt(r()) : 0.8 + 0.35 * r();
        P.push([rad * Math.cos(a), rad * Math.sin(a), inner ? 1 : 0]); }
    }
    return P;
  },
  box(scene) { return { moons: [-1.5, 2.5, -1.1, 1.6], xor: [-1.2, 1.2, -1.2, 1.2], target: [-1.3, 1.3, -1.3, 1.3] }[scene]; },
  reset(api, s) {
    s.P = this.data(api.scene);
    const m = api.p.m, r = this.rng(3);
    s.m = m; s.act = api.p.act;
    s.W1 = []; for (let j = 0; j < m; j++) s.W1.push([this.gauss(r), this.gauss(r)]);   // He 初始化：方差 2/d = 1
    s.b1 = new Array(m).fill(0);
    s.W2 = []; for (let j = 0; j < m; j++) s.W2.push(this.gauss(r) * Math.sqrt(2 / Math.max(m, 1)));
    s.w0 = [0, 0]; s.b2 = 0;                                                             // m = 0 时直接从输入到输出
    s.step = 0; s.hist = []; s.loss = this.loss(s); s.acc = this.acc(s);
  },
  phi(s, z) { return s.act === 1 ? Math.tanh(z) : Math.max(z, 0); },
  dphi(s, z, h) { return s.act === 1 ? 1 - h * h : (z > 0 ? 1 : 0); },
  logit(s, x, keep) {
    if (s.m === 0) return s.w0[0] * x[0] + s.w0[1] * x[1] + s.b2;
    let o = s.b2;
    for (let j = 0; j < s.m; j++) { const z = s.W1[j][0] * x[0] + s.W1[j][1] * x[1] + s.b1[j], h = this.phi(s, z);
      if (keep) { keep.z[j] = z; keep.h[j] = h; } o += s.W2[j] * h; }
    return o;
  },
  loss(s) { let L = 0; for (const p of s.P) { const z = this.logit(s, p); L += Math.max(z, 0) - p[2] * z + Math.log1p(Math.exp(-Math.abs(z))); } return L / s.P.length; },
  acc(s) { let c = 0; for (const p of s.P) if ((this.logit(s, p) > 0) === (p[2] > 0.5)) c++; return c / s.P.length; },
  train(api, s) {
    const n = s.P.length, m = s.m, eta = api.p.eta;
    const gW1 = s.W1.map(() => [0, 0]), gb1 = new Array(m).fill(0), gW2 = new Array(m).fill(0), gw0 = [0, 0];
    let gb2 = 0; const keep = { z: new Array(m), h: new Array(m) };
    for (const p of s.P) {
      const z = this.logit(s, p, keep), dz = (1 / (1 + Math.exp(-z)) - p[2]) / n;   // ∂L/∂z
      gb2 += dz;
      if (m === 0) { gw0[0] += dz * p[0]; gw0[1] += dz * p[1]; continue; }
      for (let j = 0; j < m; j++) { gW2[j] += dz * keep.h[j];
        const dzj = dz * s.W2[j] * this.dphi(s, keep.z[j], keep.h[j]);             // 反向经过激活函数
        gW1[j][0] += dzj * p[0]; gW1[j][1] += dzj * p[1]; gb1[j] += dzj; }
    }
    s.b2 -= eta * gb2; s.w0[0] -= eta * gw0[0]; s.w0[1] -= eta * gw0[1];
    for (let j = 0; j < m; j++) { s.W2[j] -= eta * gW2[j]; s.W1[j][0] -= eta * gW1[j][0]; s.W1[j][1] -= eta * gW1[j][1]; s.b1[j] -= eta * gb1[j]; }
    s.step += 1;
  },
  update(dt, api, s) {
    for (let k = 0; k < api.p.speed && s.step < 20000; k++) this.train(api, s);
    s.loss = this.loss(s); s.acc = this.acc(s);
    if (s.step % 20 === 0 || s.hist.length === 0) s.hist.push([s.step, Math.min(s.loss, 3)]);
    if (api.scene === "moons" && s.m === 0 && s.step >= 1000) api.done("lr");
    if (api.scene === "moons" && s.m > 0 && s.acc > 0.99) api.done("moons");
    if (api.scene === "xor" && s.acc >= 0.999) api.done("xor");
    if (api.p.eta >= 2.9 && s.step >= 400) api.done("big");
    if (api.scene === "target" && s.acc > 0.98) api.done("target");
    if (s.step >= 20000 || !isFinite(s.loss)) api.stop();
  },
  readouts(api, s) {
    const np = s.m === 0 ? 3 : 4 * s.m + 1;
    return [[["训练步数", "Steps"], String(s.step)], [["交叉熵损失", "Cross-entropy loss"], isFinite(s.loss) ? api.fmt(s.loss, 4) : "NaN"],
            [["训练准确率", "Training accuracy"], (100 * s.acc).toFixed(1) + "%"], [["参数个数", "Parameters"], String(np)]];
  },
  draw(api, s) {
    const { w, h } = api, m = 12, B = this.box(api.scene), side = Math.min(h - 2 * m, w * 0.6);
    const sx = side * 1.0, sy = side * (B[3] - B[2]) / (B[1] - B[0]), x0 = m, y0 = m + (side - sy) / 2;
    const X = (v) => x0 + (v - B[0]) / (B[1] - B[0]) * sx, Y = (v) => y0 + sy - (v - B[2]) / (B[3] - B[2]) * sy;
    const nx = 60, ny = Math.round(60 * sy / sx), cw = sx / nx, ch = sy / ny;
    for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
      const px = B[0] + (i + 0.5) / nx * (B[1] - B[0]), py = B[3] - (j + 0.5) / ny * (B[3] - B[2]);
      const z = this.logit(s, [px, py]);
      api.rect(x0 + i * cw, y0 + j * ch, cw + 0.6, ch + 0.6, z > 0 ? "rgba(31,111,235,0.16)" : "rgba(207,34,46,0.13)");
    }
    for (const p of s.P) { const c = p[2] > 0.5 ? api.css("--blue") : api.css("--red");
      if (p[2] > 0.5) api.circle(X(p[0]), Y(p[1]), 3.2, api.css("--panel"), c); else api.rect(X(p[0]) - 3, Y(p[1]) - 3, 6, 6, c, c); }
    api.rect(x0, y0, sx, sy, null, api.css("--grid"));
    const px = x0 + sx + 34, pw = w - px - m;
    if (pw > 60) api.plot(px, m + 18, pw, side - 48, [{ pts: s.hist, color: api.css("--accent") }],
                          { xmin: 0, xmax: Math.max(1000, s.step), ymin: 0, ymax: 1, xlabel: api.T("步数", "steps"), ylabel: api.T("损失", "loss") });
  },
});
