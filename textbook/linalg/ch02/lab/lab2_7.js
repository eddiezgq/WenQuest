// 实验 2.7 用余弦相似度比较检测记录（配 2.7.3、2.7.4 节）。数据与程序 2.7.1（ex2_7_data.py）相同：
// 减速器出厂检测六项、过程均值与标准差、三种故障的特征方向、八份检测记录（按车间检测项目编制的模拟数据）。
WQ.lab({
  title: ["实验 2.7 用余弦相似度比较检测记录", "Lab 2.7 Comparing inspection records by cosine similarity"],
  goal: ["把减速器的六项检测值看作 R⁶ 中的向量，标准化后用余弦相似度判断它像哪种故障，用长度判断它偏离了多少；体会不标准化会出什么错。",
         "Treat the six inspection values of a gearbox as a vector in R⁶; after standardizing, use cosine similarity to see which fault it resembles and its length to see how far off it is; see what goes wrong without standardizing."],
  scenes: [
    { id: "rec", name: ["检测记录", "Records"], hide: ["k2", "z1", "z2", "z3", "z4", "z5", "z6"],
      problem: { title: ["质量问题：今天抽检的八台，哪几台有问题？", "Quality problem: which of today's eight units are suspect?"],
                 text: ["每份记录是六个数。标准化后的长度超过 2.5 视为异常；再看它与三种故障特征的余弦相似度，最像哪一种就先查哪一种。",
                        "Each record is six numbers. A standardized length above 2.5 is abnormal; then the fault with the highest cosine similarity is checked first."] } },
    { id: "cmp", name: ["对比：标准化与否", "Compare: standardized or not"], hide: ["z1", "z2", "z3", "z4", "z5", "z6"],
      problem: { title: ["单位不同的分量能直接比吗？", "Can components in different units be compared directly?"],
                 text: ["噪声在 60 dB 上下，其余各项的数值都小得多。直接用原始值算余弦相似度，向量的方向几乎只由噪声决定。",
                        "Noise is around 60 dB, the other items are much smaller. With raw values the direction is decided almost entirely by the noise."] } },
    { id: "own", name: ["自己调", "Make your own"], hide: ["k", "k2"],
      problem: { title: ["生活中的例子：体检报告", "Everyday example: a health check report"],
                 text: ["体检报告上每项指标先看“偏离正常值几个标准差”，再看哪几项一起偏离。拖动六项的偏离量，看雷达图、长度和相似度怎样变化。",
                        "A health report is read as 'how many standard deviations off', then which items move together. Drag the six deviations and watch the radar chart, the length and the similarities."] } },
  ],
  params: [
    { id: "k", name: ["记录编号", "Record number"], min: 1, max: 8, step: 1, value: 1, digits: 0 },
    { id: "k2", name: ["第二份记录", "Second record"], min: 1, max: 8, step: 1, value: 5, digits: 0 },
    { id: "z1", name: ["直径偏差（几个 σ）", "Diameter deviation (σ)"], min: -4, max: 4, step: 0.1, value: 0, digits: 1 },
    { id: "z2", name: ["齿圈跳动（几个 σ）", "Gear runout (σ)"], min: -4, max: 4, step: 0.1, value: 0, digits: 1 },
    { id: "z3", name: ["空载噪声（几个 σ）", "Noise (σ)"], min: -4, max: 4, step: 0.1, value: 0, digits: 1 },
    { id: "z4", name: ["温升（几个 σ）", "Temperature rise (σ)"], min: -4, max: 4, step: 0.1, value: 0, digits: 1 },
    { id: "z5", name: ["振动速度（几个 σ）", "Vibration (σ)"], min: -4, max: 4, step: 0.1, value: 0, digits: 1 },
    { id: "z6", name: ["回差（几个 σ）", "Backlash (σ)"], min: -4, max: 4, step: 0.1, value: 0, digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "worst", text: ["找出标准化后长度最大的记录。它最像哪种故障？", "Find the record with the largest standardized length. Which fault does it resemble?"],
      demo: { scene: "rec", set: { k: 6 }, press: [], wait: 1 } },
    { id: "gear", text: ["查看记录 3：它超过报警线了吗？最像哪种故障？", "Look at record 3: is it over the alarm line? Which fault does it resemble?"],
      demo: { scene: "rec", set: { k: 3 }, press: [], wait: 1 } },
    { id: "cmp", text: ["在“对比”场景比较记录 2 与记录 5，说明为什么不标准化时它们“很像”。", "In the compare scene take records 2 and 5; explain why they look 'alike' without standardizing."],
      demo: { scene: "cmp", set: { k: 2, k2: 5 }, press: [], wait: 1 } },
    { id: "own", text: ["调出一份最像“装配过紧”（相似度大于 0.95）、长度超过报警线的记录。", "Make a record that most resembles 'over-tight assembly' (similarity above 0.95) and is over the alarm line."],
      demo: { scene: "own", set: { z1: 0, z2: 0, z3: 1.5, z4: 3, z5: 0.6, z6: -2.4 }, press: [], wait: 1 } },
  ],
  think: ["记录 1 与“齿轮偏心”的余弦相似度有 0.80，为什么不应据此判断它有齿轮偏心？", "Record 1 has similarity 0.80 with 'gear eccentricity'. Why should we not conclude it has that fault?"],

  items: [["直径", "diam."], ["跳动", "runout"], ["噪声", "noise"], ["温升", "temp."], ["振动", "vibr."], ["回差", "backlash"]],
  units: ["μm", "μm", "dB(A)", "K", "mm/s", "arcmin"],
  mu: [0.0, 12.0, 60.0, 15.0, 1.2, 3.0],
  sigma: [3.0, 3.0, 1.5, 2.0, 0.25, 0.4],
  faults: [{ name: ["轴承磨损", "bearing wear"], v: [0.0, 0.2, 1.0, 0.8, 1.0, 0.1] },
           { name: ["齿轮偏心", "gear eccentricity"], v: [0.0, 1.0, 0.6, 0.1, 0.7, 0.5] },
           { name: ["装配过紧", "over-tight assembly"], v: [0.0, 0.0, 0.5, 1.0, 0.2, -0.8] }],
  records: [[1.0, 13.0, 60.5, 15.5, 1.25, 3.1], [-2.0, 12.5, 63.6, 18.6, 1.95, 3.1], [0.5, 19.5, 62.0, 15.6, 1.75, 3.9],
            [3.5, 11.5, 61.2, 19.8, 1.35, 2.3], [-1.0, 11.0, 59.4, 14.2, 1.10, 2.9], [0.0, 13.5, 64.4, 19.0, 2.10, 3.3],
            [-0.5, 18.0, 61.8, 15.0, 1.60, 3.6], [2.5, 12.0, 60.9, 17.4, 1.30, 2.6]],
  alarm: 2.5,
  z(x) { return x.map((v, i) => (v - this.mu[i]) / this.sigma[i]); },
  cos(api, u, v) { const a = api.la.norm(u), b = api.la.norm(v); return a > 1e-12 && b > 1e-12 ? api.la.dot(u, v) / (a * b) : 0; },
  current(api) {
    if (api.scene === "own") { const z = [1, 2, 3, 4, 5, 6].map((i) => api.p["z" + i]); return { z, x: z.map((v, i) => this.mu[i] + v * this.sigma[i]) }; }
    const x = this.records[api.p.k - 1]; return { x, z: this.z(x) };
  },
  readouts(api) {
    const fmtv = (v, d) => "(" + v.map((t) => api.fmt(t, d)).join(", ") + ")";
    if (api.scene === "cmp") {
      const a = this.records[api.p.k - 1], b = this.records[api.p.k2 - 1];
      const raw = this.cos(api, a, b), st = this.cos(api, this.z(a), this.z(b));
      if (api.p.k === 2 && api.p.k2 === 5) api.done("cmp");
      return [[[`记录 ${api.p.k} 原始值`, `Record ${api.p.k} raw`], fmtv(a, 2)], [[`记录 ${api.p.k2} 原始值`, `Record ${api.p.k2} raw`], fmtv(b, 2)],
              [["原始值的余弦相似度", "Cosine, raw values"], api.fmt(raw, 4)],
              [["标准化后的余弦相似度", "Cosine, standardized"], api.fmt(st, 4)],
              [["标准化后的距离", "Distance, standardized"], api.fmt(api.la.norm(this.z(a).map((t, i) => t - this.z(b)[i])), 3)]];
    }
    const { x, z } = this.current(api), n = api.la.norm(z), s = this.faults.map((f) => this.cos(api, z, f.v));
    const best = s.indexOf(Math.max(...s));
    if (api.scene === "rec") {
      const all = this.records.map((r) => api.la.norm(this.z(r)));
      if (api.p.k - 1 === all.indexOf(Math.max(...all))) api.done("worst");
      if (api.p.k === 3) api.done("gear");
    }
    if (api.scene === "own" && best === 2 && s[2] > 0.95 && n > this.alarm) api.done("own");
    const verdict = n > this.alarm ? api.T("异常，先查：", "abnormal, check first: ") + api.T(...this.faults[best].name) : api.T("在正常范围内", "within normal range");
    return [[["原始值", "Raw values"], fmtv(x, 2)], [["标准化 z = (x − μ)/σ", "Standardized z"], fmtv(z, 2)],
            [["长度 ‖z‖", "Length ‖z‖"], api.fmt(n, 2) + (n > this.alarm ? api.T("（超过 2.5）", " (over 2.5)") : "")],
            ...this.faults.map((f, i) => [[`与“${f.name[0]}”的相似度`, `Cosine with '${f.name[1]}'`], api.fmt(s[i], 3)]),
            [["判断", "Verdict"], verdict]];
  },
  draw(api) {
    const { w: W, h: H } = api, muted = api.css("--muted"), ink = api.css("--ink"), red = api.css("--red"), blue = api.css("--blue");
    const barsZ = (z, x0, y0, bw, bh, color, label) => {   // six bars of z (−4…4), zero line in the middle
      api.rect(x0, y0, bw, bh, null, api.css("--grid"));
      const mid = y0 + bh / 2, sc = bh / 8, cw = bw / 6;
      api.line(x0, mid, x0 + bw, mid, muted, 1);
      [2.5, -2.5].forEach((t) => api.line(x0, mid - t * sc, x0 + bw, mid - t * sc, api.css("--grid"), 1, [4, 4]));
      z.forEach((v, i) => {
        const t = Math.max(-4, Math.min(4, v));
        api.rect(x0 + i * cw + cw * 0.18, Math.min(mid, mid - t * sc), cw * 0.64, Math.abs(t) * sc, Math.abs(v) > 2.5 ? red : color);
        api.label(api.T(...this.items[i]), x0 + i * cw + cw / 2, y0 + bh + 14, muted, 11, "center");
      });
      if (label) api.label(label, x0 + 4, y0 + 14, muted, 12);
    };
    if (api.scene === "cmp") {
      const a = this.z(this.records[api.p.k - 1]), b = this.z(this.records[api.p.k2 - 1]);
      barsZ(a, W * 0.06, H * 0.1, W * 0.4, H * 0.7, blue, api.T(`记录 ${api.p.k}（标准化）`, `record ${api.p.k} (standardized)`));
      barsZ(b, W * 0.54, H * 0.1, W * 0.4, H * 0.7, api.css("--green"), api.T(`记录 ${api.p.k2}（标准化）`, `record ${api.p.k2} (standardized)`));
      return;
    }
    const { z } = this.current(api);
    barsZ(z, W * 0.05, H * 0.1, W * 0.42, H * 0.7, blue, api.T("偏离几个标准差（虚线 ±2.5）", "deviation in σ (dashed ±2.5)"));
    // radar: the record and the most similar fault direction (scaled to the same length)
    const cx = W * 0.75, cy = H * 0.47, R = Math.min(W * 0.2, H * 0.38), ang = (i) => -Math.PI / 2 + i * Math.PI / 3;
    const P = (i, r) => [cx + R * (r / 4) * Math.cos(ang(i)), cy + R * (r / 4) * Math.sin(ang(i))];
    [1, 2, 3, 4].forEach((r) => { const c = api.ctx; c.beginPath(); for (let i = 0; i <= 6; i++) { const q = P(i % 6, r); i ? c.lineTo(...q) : c.moveTo(...q); } c.strokeStyle = api.css("--grid"); c.lineWidth = 1; c.stroke(); });
    for (let i = 0; i < 6; i++) { api.line(cx, cy, ...P(i, 4), api.css("--grid"), 1); api.label(api.T(...this.items[i]), ...P(i, 4.7), muted, 11, "center"); }
    const poly = (v, color, fill) => { const c = api.ctx; c.beginPath(); v.forEach((t, i) => { const q = P(i, Math.max(0, t + 2)); i ? c.lineTo(...q) : c.moveTo(...q); }); c.closePath(); if (fill) { c.fillStyle = fill; c.fill(); } c.strokeStyle = color; c.lineWidth = 2; c.stroke(); };
    const s = this.faults.map((f) => this.cos(api, z, f.v)), best = s.indexOf(Math.max(...s)), f = this.faults[best].v;
    const n = api.la.norm(z), fn = api.la.norm(f);
    poly(f.map((t) => (n > 1e-9 ? t * n / fn : 0)), api.css("--amber"));
    poly(z, blue, "rgba(31,111,235,0.15)");
    api.label(api.T("雷达图：中心为 −2σ，外圈为 +2σ", "radar: centre −2σ, outer ring +2σ"), cx, H * 0.93, muted, 11, "center");
    api.label(api.T("橙线：最相似的故障方向（同样长度）", "orange: most similar fault (same length)"), cx, H * 0.98, api.css("--amber"), 11, "center");
    void ink;
  },
});
