// 实验 4.8 轴向尺寸链的蒙特卡洛分析（配 4.8 节）。与程序 4.8.1 同一条尺寸链、同样的公差：
// WQR-105 输出轴系两端固定，游隙 = W − c₁ − c₂ − (B + 套筒 + 齿轮毂 + 轴上 25 + B)，要求 0.2–0.4 mm。
// 机加工尺寸取正态（中心在公差带中间，σ = T/6），轴承宽度取正态（均值 −0.05，σ 可调），与程序相同；随机数用固定种子，结果可重复。
function rng4_8(seed) {
  let a = seed >>> 0;
  const u = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  return { u, n: (m, s) => m + s * Math.sqrt(-2 * Math.log(1 - u())) * Math.cos(2 * Math.PI * u()) };
}
// 组成环：[名称, 名义, 下偏差, 上偏差, ±1（增环 / 减环）, 种类]；公差按 GB/T 1800.1（js11、h11）与 GB/T 307.1（轴承宽度）
function links4_8(scene, comp, tol) {
  if (scene === "robot") {
    // 止口长度按各环的中间尺寸定，使平均游隙在 0.3（取到 0.05 mm；公差倍数为 1 时是 10.00，与程序 4.8.1 相同）；用垫片时再加长 0.25 mm（方案二）
    const mid = 152 - (2 * (17 - 0.06) + 18 - 0.055 * tol + 55 - 0.095 * tol + 25);
    const c = Math.round((mid - 0.3) / 2 / 0.05) * 0.05 + (comp ? 0.25 : 0);
    const tc = c > 10 ? 0.055 : 0.045;            // js11：止口 ≤ 10 mm 时 IT11 = 0.09，10–18 mm 时 0.11
    return { req: [0.2, 0.4], target: 0.3, step: 0.05, links: [
      [["箱体两端面 W", "Housing W"], 152, -0.125, 0.125, 1, "m"], [["闷盖止口 c₁", "Blind-cap spigot c₁"], c, -tc, tc, -1, "m"],
      [["透盖止口 c₂", "Through-cap spigot c₂"], c, -tc, tc, -1, "m"], [["左轴承宽", "Left bearing"], 17, -0.12, 0, -1, "b"],
      [["套筒", "Sleeve"], 18, -0.11, 0, -1, "m"], [["齿轮毂", "Gear hub"], 55, -0.19, 0, -1, "m"],
      [["轴上 25", "Shaft 25"], 25, -0.065, 0.065, -1, "m"], [["右轴承宽", "Right bearing"], 17, -0.12, 0, -1, "b"]] };
  }
  // 轮滑鞋的轮子：两个 608 轴承的内圈夹着隔套（螺栓压紧），外圈靠在轮毂中间的凸台两侧。隔套比凸台长，轴承才不被螺栓压死。
  return { req: [0.02, 0.15], target: 0.08, step: 0.05, links: [
    [["隔套长", "Spacer"], 8.0, -0.05, 0.05, 1, "m"], [["轮毂凸台宽（注塑）", "Hub rib (molded)"], 7.92, -0.08, 0.08, -1, "m"]] };
}
function sample4_8(p, scene) {
  const comp = Math.round(p.comp) === 1, L = links4_8(scene, comp, p.tol), r = rng4_8(4801), n = Math.round(p.n);
  let nom = 0, wmax = 0, wmin = 0, mu = 0, v = 0;
  L.links.forEach(([nm, x, lo, hi, k, kind]) => {
    const f = kind === "m" ? p.tol : 1, l = lo * f, h = hi * f;
    nom += k * x; wmax += k > 0 ? h : -l; wmin += k > 0 ? l : -h;
    mu += k * (x + (l + h) / 2); v += ((h - l) / 6) ** 2;
  });
  wmax += nom; wmin += nom;
  const g = new Float64Array(n), shims = [];
  let ok = 0;
  for (let i = 0; i < n; i++) {
    let x = 0;
    L.links.forEach(([nm, x0, lo, hi, k, kind]) => {
      const f = kind === "m" ? p.tol : 1;
      x += k * (kind === "b" ? x0 + r.n(-0.05, p.bsd) : x0 + r.n((lo + hi) * f / 2, (hi - lo) * f / 6));
    });
    if (comp && scene === "robot") {             // 量出游隙（误差 σ 0.01），按 0.05 的台阶加垫片
      const s = Math.max(0, Math.round((L.target - (x + r.n(0, 0.01))) / L.step) * L.step);
      shims.push(s); x += s;
    } else if (comp) {                            // 隔套分三档（−0.05、0、+0.05）：装配前量出凸台宽度和隔套长度，选一档
      const s = Math.max(-0.05, Math.min(0.05, Math.round((L.target - (x + r.n(0, 0.005))) / 0.05) * 0.05));
      shims.push(s); x += s;
    }
    g[i] = x;
    if (x >= L.req[0] && x <= L.req[1]) ok++;
  }
  let m = 0; g.forEach((x) => { m += x; }); m /= n;
  let sd = 0; g.forEach((x) => { sd += (x - m) ** 2; }); sd = Math.sqrt(sd / (n - 1));
  let gmin = Infinity, gmax = -Infinity; g.forEach((x) => { if (x < gmin) gmin = x; if (x > gmax) gmax = x; });
  return { L, g, ok: ok / n, wmin, wmax, gmin, gmax, mu, s3: 3 * Math.sqrt(v), m, sd, shims, comp, n,
    shimMax: shims.length ? Math.max(...shims) : 0, shimMean: shims.length ? shims.reduce((a, b) => a + b, 0) / shims.length : 0 };
}
WQ.lab({
  title: ["实验 4.8 轴向尺寸链的蒙特卡洛分析", "Lab 4.8 Monte Carlo analysis of an axial dimension chain"],
  goal: ["给每个组成环按公差随机抽一个尺寸，算出游隙，重复成千上万次，看游隙的分布、合格率，与极值法、方和根法比较；再试一试用调整垫片（补偿环）。",
         "Draw every link at random within its tolerance, compute the end play, repeat thousands of times; compare the distribution and yield with worst case and RSS; then try a shim pack as compensating link."],
  scenes: [
    { id: "robot", robot: true, name: ["WQR-105 输出轴系", "WQR-105 output shaft"],
      problem: { title: ["工程问题：码垛线减速器输出轴的轴向游隙", "Engineering problem: end play of the palletizing-line reducer's output shaft"],
                 text: ["两个 6207 两端固定，端盖压住外圈。游隙太小，轴受热伸长后把轴承压死；太大，齿轮轴向窜动。要求 0.2–0.4 mm。八个尺寸串成一条链，公差能不能保证？",
                        "Two 6207s, fixed at both ends, the caps pressing the outer rings. Too little play and the warm shaft jams the bearings; too much and the gear shuttles. 0.2–0.4 mm is required. Can the tolerances of eight sizes in one chain guarantee it?"] } },
    { id: "life", name: ["轮滑鞋的轮子", "Inline-skate wheel"],
      problem: { title: ["生活中的例子：轮滑鞋的轮子", "Everyday example: an inline-skate wheel"],
                 text: ["轮子里两个 608 轴承，内圈夹着一根隔套，外圈靠在轮毂中间的凸台上。隔套必须比凸台略长，否则拧紧螺栓时轴承被压死、轮子转不动；长太多，轮子晃。",
                        "Two 608 bearings sit in the wheel; their inner rings clamp a spacer, their outer rings bear on a rib in the hub. The spacer must be a little longer than the rib, or tightening the axle bolt jams the bearings; much longer and the wheel wobbles."] } },
  ],
  params: [
    { id: "tol", name: ["机加工零件的公差（倍数，1 = 正文的公差）", "Machined-part tolerances (× those in the text)"], min: 0.25, max: 2, step: 0.05, value: 1, unit: "", digits: 2 },
    { id: "bsd", name: ["轴承宽度的标准差", "Bearing width standard deviation"], min: 0.005, max: 0.04, step: 0.005, value: 0.015, unit: "mm", digits: 3 },
    { id: "comp", name: ["补偿环（0 = 不用，1 = 垫片 / 隔套选配）", "Compensation (0 = none, 1 = shims / spacer grades)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "n", name: ["抽样次数", "Samples"], min: 1000, max: 50000, step: 1000, value: 20000, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["抽样", "Sample"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "var(--accent)", name: ["游隙的分布（直方图）", "end-play histogram"] }, { color: "var(--ink)", name: ["极值法范围（实线）、方和根 ±3σ（虚线）", "worst case (solid), RSS ±3σ (dashed)"] }],
  tasks: [
    { id: "base", robot: true, text: ["按正文的公差（倍数 1）、不用垫片抽样：合格率多少？极值法的范围比要求宽多少倍？", "Sample with the text's tolerances (× 1) and no shims: what is the yield? How many times wider than required is the worst-case range?"],
      demo: { scene: "robot", set: { tol: 1, bsd: 0.015, comp: 0, n: 20000 }, press: ["start"], wait: 1 } },
    { id: "tight", robot: true, text: ["把机加工零件的公差缩小到一半（0.5，止口长度随之重新对中）：合格率能到 100% 吗？极值法的范围呢？", "Halve the machined-part tolerances (0.5; the spigot is re-centered): does the yield reach 100%? And the worst-case range?"],
      demo: { scene: "robot", set: { tol: 0.5, bsd: 0.015, comp: 0, n: 20000 }, press: ["start"], wait: 1 } },
    { id: "shim", robot: true, text: ["公差放回 1，用调整垫片（补偿环 = 1）：合格率、垫片最厚多少？", "Tolerances back to 1, use shims (compensation = 1): yield and the thickest shim pack?"],
      demo: { scene: "robot", set: { tol: 1, bsd: 0.015, comp: 1, n: 20000 }, press: ["start"], wait: 1 } },
    { id: "life", text: ["轮滑鞋的轮子：先不选配、再选配隔套，各抽样一次，比较合格率。", "Skate wheel: sample without and then with spacer grades; compare the yields."],
      demo: { scene: "life", set: { tol: 1, bsd: 0.015, comp: 1, n: 20000 }, press: ["start"], wait: 1 } },
  ],
  think: ["程序 4.8.1 和这个实验用同一条尺寸链。两个轴承宽度的公差之和已经超过了要求的游隙范围——这时再收紧箱体、套筒的公差有没有用？还有哪些办法？",
          "Program 4.8.1 and this lab use the same chain. The two bearing-width tolerances alone exceed the allowed play range — does tightening the housing and sleeve still help? What else can be done?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    const p = api.p;
    s.r = sample4_8(p, api.scene);
    const comp = Math.round(p.comp) === 1;
    if (api.scene === "robot" && !comp && Math.abs(p.tol - 1) < 0.01) api.done("base");
    if (api.scene === "robot" && !comp && p.tol <= 0.501) api.done("tight");
    if (api.scene === "robot" && comp) api.done("shim");
    if (api.scene === "life" && comp) api.done("life");
    api.stop();
  },
  readouts(api, s) {
    const f = api.fmt, r = s.r;
    if (!r) return [[["状态", "Status"], api.T("按“抽样”开始", "press Sample")]];
    const out = [
      [["要求的游隙", "Required play"], f(r.L.req[0], 2) + "–" + f(r.L.req[1], 2) + " mm"],
      [["极值法", "Worst case"], f(r.wmin, 3) + " … " + f(r.wmax, 3) + " mm"],
      [["方和根法 μ ± 3σ", "RSS μ ± 3σ"], f(r.mu, 3) + " ± " + f(r.s3, 3) + " mm"],
      [["抽样：平均、标准差", "Sampled: mean, s.d."], f(r.m, 3) + "，" + f(r.sd, 3) + " mm"],
      [["抽样：最小、最大", "Sampled: min, max"], f(r.gmin, 3) + " … " + f(r.gmax, 3) + " mm"],
      [["合格率", "Yield"], f(100 * r.ok, 1) + " %"],
    ];
    if (r.comp) out.push([[api.scene === "robot" ? "垫片：平均、最厚" : "隔套调整：平均、最大", api.scene === "robot" ? "Shims: mean, max" : "Spacer change: mean, max"], f(r.shimMean, 3) + "，" + f(r.shimMax, 2) + " mm"]);
    return out;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, r = s.r;
    const x0 = 50, y0 = 30, W = w - 80, H = h - 80;
    api.rect(x0, y0, W, H, null, css("--grid"));
    if (!r) { api.label(api.T("按“抽样”画出游隙的分布", "Press Sample to draw the end-play distribution"), x0 + W / 2, y0 + H / 2, css("--muted"), 14, "center"); return; }
    const lo = Math.min(r.wmin, r.L.req[0]) - 0.05, hi = Math.max(r.wmax, r.L.req[1]) + 0.05;
    const X = (v) => x0 + (v - lo) / (hi - lo) * W;
    api.rect(X(r.L.req[0]), y0, X(r.L.req[1]) - X(r.L.req[0]), H, "rgba(44,160,44,0.15)");
    const nb = 90, cnt = new Array(nb).fill(0);
    r.g.forEach((v) => { const k = Math.floor((v - lo) / (hi - lo) * nb); if (k >= 0 && k < nb) cnt[k]++; });
    const top = Math.max(...cnt) || 1;
    cnt.forEach((c, k) => { const hh = c / top * (H - 20); api.rect(x0 + k * W / nb + 0.5, y0 + H - hh, W / nb - 1, hh, css("--accent")); });
    [[r.wmin, []], [r.wmax, []], [r.mu - r.s3, [6, 4]], [r.mu + r.s3, [6, 4]]].forEach(([v, d]) => api.line(X(v), y0, X(v), y0 + H, css("--ink"), 1.5, d));
    for (let t = Math.ceil(lo * 10) / 10; t <= hi + 1e-9; t += 0.1) {
      api.line(X(t), y0 + H, X(t), y0 + H + 5, css("--muted"), 1);
      api.label(api.fmt(t, 1), X(t), y0 + H + 16, css("--muted"), 11, "center");
    }
    api.label(api.T("游隙 / mm", "End play / mm"), x0 + W, y0 + H + 34, css("--muted"), 12, "right");
    api.label(api.T("绿色：要求的范围", "green: required range"), x0 + 6, y0 + 12, css("--muted"), 12);
  },
});
