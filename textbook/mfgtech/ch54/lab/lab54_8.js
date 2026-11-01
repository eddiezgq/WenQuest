// 实验 54.8 误差诊断（配 54.8 节）。四个批次各有一个隐藏的加工问题（批次名不透露），每批 40 件 SH-301；学生看测量数据和放大的工件形状，
// 选一项纠正措施，系统判断是否对症。数据按仿真车间的误差模型（factory/digital/sim/errors.py）生成：
//   轴承位直径 = 35.0065 + 0.0125·磨损 + 热变形 + N(0, 1.2 µm)，磨损 = 修整后件数/30，每 10 件修整；尾座偏移时两处各加 2e·z/167（z = 46、124.5：工件绕头架顶尖偏斜）；
//   圆跳动 = |N(0.004, 1.2 µm)|；键槽对称度 = |N(0.006, 2 µm)|。问题情景与 PROBLEMS 相同：尾座偏移 e = 0.008（第 21 件起）、砂轮磨损加快
//   （2.5 倍）、未预热（−0.010·(1 − e^(−i/6))，从第 1 件起）、中心孔质量差（圆跳动 +0.006、σ = 3 µm，直径分散 ×1.3，第 21 件起）、
//   （键槽夹具定位元件磨损的数据也写在这里，备用：对称度 +0.012、σ = 4 µm）。措施清单与 sim/errors.py 的 FIXES 相同（含几项不对症的）。
const N8 = 40, S8 = 0.0012;
const FIX8 = [
  ["（还没选）", "(none yet)"], ["校正磨床尾座（检验棒和千分表）", "Align the tailstock (test bar and dial gauge)"], ["缩短砂轮修整间隔", "Dress the wheel more often"],
  ["开机空运转预热，首件合格后再批量磨", "Warm up before production"], ["修研中心孔、更换磨损的顶尖", "Lap the centre holes, replace worn centres"],
  ["更换键槽夹具的 V 形块与挡板", "Replace the keyway fixture's V-blocks and stop"], ["更换砂轮牌号（更软的砂轮）", "Use a softer wheel"],
  ["培训操作工，加强自检", "Retrain the operator"], ["更换并重新校准量具", "Replace and recalibrate the gauge"]];
const BATCH8 = { A: { fix: 1 }, B: { fix: 2 }, C: { fix: 3 }, D: { fix: 4 }, E: { fix: 5 } };
const CH8 = [["左轴承位直径", "left bearing seat"], ["右轴承位直径", "right bearing seat"], ["右减左", "right − left"], ["轴承位圆跳动", "bearing-seat runout"], ["键槽对称度", "keyway symmetry"]];
function rnd8(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function data8(batch) {
  const R = rnd8({ A: 11, B: 22, C: 33, D: 44, E: 55 }[batch]), g = () => Math.sqrt(-2 * Math.log(Math.max(R(), 1e-12))) * Math.cos(2 * Math.PI * R());
  const out = { L: [], R: [], D: [], run: [], sym: [] };
  for (let i = 0; i < N8; i++) {
    const on = i >= 20, wear = (i % 10) / 30, slope = 0.0125 * (batch === "B" ? 2.5 : 1);
    const th = batch === "C" ? -0.010 * (1 - Math.exp(-i / 6)) : 0, sd = S8 * (batch === "D" && on ? 1.3 : 1);
    const base = 35.0065 + slope * wear + th, tp = batch === "A" && on ? 2 * 0.008 / 167 : 0;
    const l = base + tp * 46 + sd * g(), r = base + tp * 124.5 + sd * g();
    out.L.push(l); out.R.push(r); out.D.push(r - l);
    out.run.push(Math.abs(batch === "D" && on ? 0.010 + 0.003 * g() : 0.004 + S8 * g()));
    out.sym.push(Math.abs(batch === "E" && on ? 0.018 + 0.004 * g() : 0.006 + 0.002 * g()));
  }
  return out;
}
const mean8 = (a) => a.reduce((x, y) => x + y, 0) / a.length;
const sd8 = (a) => { const m = mean8(a); return Math.sqrt(a.reduce((x, y) => x + (y - m) * (y - m), 0) / (a.length - 1)); };
function series8(d, k) { return [d.L, d.R, d.D, d.run, d.sym][k]; }
function tol8(k) { return [[35.002, 35.018], [35.002, 35.018], [-0.016, 0.016], [0, 0.012], [0, 0.020]][k]; }

const FX8 = {
  setup(api, h) {
    h.parts = ((h.entry.assembly || {}).parts || []).map((p) => Object.assign({}, p));
    h.parts.forEach((p) => { p.obj = h.nodes[p.node]; if (p.obj) p.p0 = p.obj.position.clone(); });
    h.base = h.nodes.root || h.root;
  },
};

WQ.lab({
  title: ["实验 54.8 误差诊断", "Lab 54.8 Diagnosing machining errors"],
  goal: ["四个批次的 SH-301 各有一个隐藏的加工问题。看各项特性的逐件数据和放大的工件形状，找出误差的形态，推断原因，选一项纠正措施；系统告诉你措施是否对症。",
         "Each of four batches of SH-301 hides one machining problem. Look at the part-by-part data of each characteristic and the exaggerated shape of the work, find the pattern, infer the cause and choose a corrective action; the system tells you whether it addresses the cause."],
  view: "3d",
  models: ["E-ACC-CENTERS"],
  scenes: ["A", "B", "C", "D"].map((b) => ({ id: b, name: [`批次 ${b}`, `Batch ${b}`],
    problem: { title: [`批次 ${b}：40 件里出了问题`, `Batch ${b}: something went wrong in 40 parts`],
               text: ["质检员报告这一批有问题（或者 Cpk 降了）。先别急着选措施：逐项看数据——哪个特性变了？从第几件开始？是整体偏移、逐件漂移、跳变还是分散变大？左右两处一起变还是只变一处？",
                      "The inspector reports trouble in this batch (or a drop in Cpk). Don't pick an action yet: go through the data — which characteristic changed, from which part, is it a shift, a drift, a jump or a wider spread, and do both seats change or only one?"] } })),
  params: [
    { id: "show", name: ["看哪个特性（0 左轴承位、1 右轴承位、2 右减左、3 圆跳动、4 键槽对称度）", "Characteristic (0 left, 1 right, 2 right − left, 3 runout, 4 keyway symmetry)"], min: 0, max: 4, step: 1, value: 0, unit: "", digits: 0 },
    { id: "cause", name: ["纠正措施（编号见右栏“措施清单”）", "Corrective action (numbers in the list)"], min: 0, max: 8, step: 1, value: 0, unit: "", digits: 0 },
    { id: "k", name: ["工件形状放大倍数", "Shape magnification"], min: 100, max: 2000, step: 50, value: 800, unit: "×", digits: 0 },
  ],
  tasks: ["A", "B", "C", "D"].map((b, i) => ({ id: "b" + b, text: [`批次 ${b}：找出原因，选对纠正措施。`, `Batch ${b}: find the cause and choose the right action.`],
    demo: { scene: b, set: { show: [2, 0, 0, 3][i], cause: BATCH8[b].fix }, press: [], wait: 1 } })),
  think: ["批次 B 和正常状态都是锯齿，怎样区分？如果把“缩短修整间隔”用在批次 A 上，数据会怎样？为什么说“措施要用数据验证”？", "Batch B and the normal process both show a saw: how do you tell them apart? What would the data do if you applied 'dress more often' to batch A? Why must every action be verified with data?"],

  setup3d(api, keep) {
    const h = api.m["E-ACC-CENTERS"];
    FX8.setup(api, h);
    const T = api.three;
    keep.mat = new T.MeshStandardMaterial({ color: 0xe8c39e, roughness: 0.6, metalness: 0.1, side: T.DoubleSide });
    keep.cv = document.createElement("canvas"); keep.cv.width = 1024; keep.cv.height = 512;
    keep.tex = new T.CanvasTexture(keep.cv);
    keep.board = new T.Mesh(new T.PlaneGeometry(0.30, 0.15), new T.MeshBasicMaterial({ map: keep.tex, side: T.DoubleSide }));
    h.base.add(keep.board);
    keep.board.position.set(0.0835, 0.0, 0.125);       // 工件上方（模型坐标：x 沿轴，z 向上）
    keep.board.rotation.set(Math.PI / 2, 0, 0);
    keep.key = "";
    api.view(-15, 20, 1.1, h);
  },
  readouts(api) {
    const p = api.p, d = data8(api.scene), k = Math.round(p.show), s = series8(d, k), T = api.T, c = Math.round(p.cause);
    const a = s.slice(0, 20), b = s.slice(20), f = (v) => api.fmt(v * 1000, 2) + " µm";
    const fix = BATCH8[api.scene].fix, ok = c === fix;
    if (ok) api.done("b" + api.scene);
    const segSlope = (arr) => { const n = 10, xs = [...Array(n).keys()]; let sxy = 0, sxx = 0, cnt = 0;
      for (let g = 0; g + n <= arr.length; g += n) { const seg = arr.slice(g, g + n), m = mean8(seg); xs.forEach((x) => { sxy += (x - 4.5) * (seg[x] - m); sxx += (x - 4.5) ** 2; }); cnt++; } return sxy / sxx; };
    return [
      [["特性", "characteristic"], T(CH8[k][0], CH8[k][1])],
      [["前 20 件 / 后 20 件的均值", "mean of parts 1–20 / 21–40"], (k <= 1 ? api.fmt(mean8(a), 4) + " / " + api.fmt(mean8(b), 4) + " mm" : f(mean8(a)) + " / " + f(mean8(b)))],
      [["前 20 件 / 后 20 件的标准差", "std dev 1–20 / 21–40"], f(sd8(a)) + " / " + f(sd8(b))],
      [["每个修整周期内的斜率", "slope within a dressing cycle"], api.fmt(segSlope(s) * 1000, 2) + T(" µm/件（正常约 0.42）", " µm/part (normal ≈ 0.42)")],
      [["前 3 件 / 第 8–10 件的均值", "mean of parts 1–3 / 8–10"], (k <= 1 ? api.fmt(mean8(s.slice(0, 3)), 4) + " / " + api.fmt(mean8(s.slice(7, 10)), 4) : f(mean8(s.slice(0, 3))) + " / " + f(mean8(s.slice(7, 10))))],
      [["措施清单", "actions"], FIX8.slice(1).map((x, i) => `${i + 1} ${T(x[0], x[1])}`).join("；")],
      [["你选的措施", "your action"], c ? `${c} ${T(FIX8[c][0], FIX8[c][1])}` + " → " + (ok ? T("对症：下发以后数据恢复正常", "addresses the cause: the data recover") : T("不对症：下发以后数据不会恢复，再看看数据", "does not address the cause: the data won't recover")) : T("还没选", "none yet")],
    ];
  },
  draw(api) {
    const h = api.m["E-ACC-CENTERS"];
    if (!h || !h.parts) return;
    const p = api.p, k = api.keep, key = [api.scene, p.show, p.k].join("|");
    if (key === k.key) return;
    k.key = key;
    const T = api.three, d = data8(api.scene), K = p.k, show = Math.round(p.show);
    // 工件：两个轴承位按后 20 件比前 20 件的变化放大（锥度只在批次 A 出现）
    const dL = mean8(d.L.slice(20)) - mean8(d.L.slice(0, 20)), dR = mean8(d.R.slice(20)) - mean8(d.R.slice(0, 20));
    const nx = 48, nt = 60, pos = [], idx = [], L = 167, R0 = 17.5;
    for (let i = 0; i <= nx; i++) {
      const x = L * i / nx, dd = dL + (dR - dL) * (x - 46) / (124.5 - 46);
      for (let j = 0; j <= nt; j++) { const t = 2 * Math.PI * j / nt, rr = R0 + K * dd / 2; pos.push(x, rr * Math.cos(t), rr * Math.sin(t)); }
    }
    for (let i = 0; i < nx; i++) for (let j = 0; j < nt; j++) { const a = i * (nt + 1) + j, b = a + nt + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
    const g = new T.BufferGeometry(); g.setAttribute("position", new T.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
    if (k.mesh) { h.base.remove(k.mesh); k.mesh.geometry.dispose(); }
    k.mesh = new T.Mesh(g, k.mat); k.mesh.scale.set(0.001, 0.001, 0.001); h.base.add(k.mesh);
    // 数据板：逐件测得值、公差线、第 20/21 件之间的分界
    const c = k.cv.getContext("2d"), W = k.cv.width, H = k.cv.height, s = series8(d, show), [lo, hi] = tol8(show);
    c.fillStyle = "#ffffff"; c.fillRect(0, 0, W, H);
    const ymin = Math.min(lo, ...s), ymax = Math.max(hi, ...s), pad = (ymax - ymin) * 0.08;
    const X = (i) => 70 + (W - 100) * i / (N8 - 1), Y = (v) => H - 50 - (v - ymin + pad) / (ymax - ymin + 2 * pad) * (H - 110);
    c.strokeStyle = "#c0504d"; c.setLineDash([10, 8]); c.lineWidth = 2;
    [lo, hi].forEach((v) => { c.beginPath(); c.moveTo(X(0), Y(v)); c.lineTo(X(N8 - 1), Y(v)); c.stroke(); });
    c.setLineDash([4, 6]); c.strokeStyle = "#9aa3ab";
    for (let r = 10; r < N8; r += 10) { c.beginPath(); c.moveTo((X(r - 1) + X(r)) / 2, 60); c.lineTo((X(r - 1) + X(r)) / 2, H - 50); c.stroke(); }
    c.setLineDash([]); c.strokeStyle = "#3a7dc9"; c.lineWidth = 3; c.beginPath();
    s.forEach((v, i) => (i ? c.lineTo(X(i), Y(v)) : c.moveTo(X(i), Y(v)))); c.stroke();
    c.fillStyle = "#3a7dc9"; s.forEach((v, i) => { c.beginPath(); c.arc(X(i), Y(v), 6, 0, 2 * Math.PI); c.fill(); });
    c.fillStyle = "#1d2327"; c.font = "bold 34px sans-serif";
    c.fillText(api.T(CH8[show][0], CH8[show][1]) + api.T("（逐件，点线为修整砂轮，红线为公差）", " (dotted: dressing; red: tolerance)"), 20, 44);
    c.font = "26px sans-serif"; c.fillText("1", X(0) - 6, H - 15); c.fillText("40", X(N8 - 1) - 14, H - 15);
    k.tex.needsUpdate = true;
  },
});
