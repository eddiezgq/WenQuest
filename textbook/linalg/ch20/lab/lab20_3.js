// 实验 20.3 AGV 用两个路标定位：交会角与条件数（配 20.3 节）。
// 两个路标 L₁、L₂ 的位置已知。AGV 在 P 处测出到两个路标的方位（已知车体朝向，方位是绝对方向），每个方位确定一条
// 过路标的直线：nᵢᵀx = nᵢᵀLᵢ，nᵢ 是垂直于方位的单位向量。两式联立 N x = c 就是 2 阶方程组，P 是它的解。
// 方位误差 δθᵢ 使第 i 条直线平移 rᵢδθᵢ（rᵢ 为到路标的距离），即 δcᵢ = rᵢδθᵢ，定位误差 δx = N⁻¹δc。
// 生活场景：野外用两座山头的方位交会，确定自己在地图上的位置（距离以 km 计，指北针误差约 0.5°）。
WQ.lab({
  title: ["实验 20.3 两个路标定位：交会角与条件数", "Lab 20.3 Two-landmark positioning: intersection angle and condition number"],
  goal: ["移动 AGV，看两条方位线的夹角、方程组的条件数和定位误差怎样一起变化；体会“直线几乎平行 = 矩阵接近奇异 = 误差被放大”。",
         "Move the AGV and watch the angle between the bearing lines, the condition number and the position error change together: nearly parallel lines = nearly singular matrix = amplified error."],
  scenes: [
    { id: "agv", robot: true, name: ["AGV 与两个路标", "AGV and two landmarks"],
      problem: { title: ["机器人问题：在哪里定位最准？", "Robot problem: where is positioning most accurate?"],
                 text: ["仓库墙上有两个反光路标，相距 4 m。AGV 的激光扫描仪测出它们的方位，两条方位线的交点就是 AGV 的位置。方位测量有几毫弧度的误差，在不同位置，定位误差差别很大。",
                        "Two reflectors 4 m apart hang on the warehouse wall. The AGV's laser scanner measures their bearings; the bearing lines intersect at the AGV. Bearings carry a few milliradians of error, and the position error differs greatly from place to place."] } },
    { id: "hike", name: ["生活中的例子：两座山头交会", "Everyday example: two summits"], hide: ["sb"],
      problem: { title: ["生活中的例子：我在地图上的哪里？", "Everyday example: where am I on the map?"],
                 text: ["徒步时用指北针分别对准两座认得出的山头，在地图上从山头沿反方向画线，两线的交点就是自己的位置。指北针读数有约 0.5° 的误差。两座山头该怎么选？",
                        "On a hike, take compass bearings to two recognizable summits and draw back-bearings on the map; they cross where you stand. The compass reads within about 0.5°. How should the summits be chosen?"] } },
  ],
  params: [
    { id: "px", name: ["位置 x", "Position x"], min: -4, max: 4, step: 0.1, value: 1.5, digits: 1 },
    { id: "py", name: ["位置 y", "Position y"], min: -1, max: 3.9, step: 0.1, value: 1.0, digits: 1 },
    { id: "sb", name: ["方位误差（标准差）", "Bearing error (std. dev.)"], min: 1, max: 20, step: 1, value: 5, unit: " mrad", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "good", robot: true, text: ["找一个条件数 κ₂ < 1.5 的位置。两条方位线的夹角是多少？", "Find a position with κ₂ < 1.5. What is the angle between the bearing lines?"],
      demo: { scene: "agv", set: { px: 0, py: 2, sb: 5 }, press: [] } },
    { id: "bad", robot: true, text: ["找一个条件数 κ₂ > 20 的位置，读出误差椭圆的长半轴。", "Find a position with κ₂ > 20 and read the long semi-axis of the error ellipse."],
      demo: { scene: "agv", set: { px: 3.5, py: 3.8, sb: 5 }, press: [] } },
    { id: "between", robot: true, text: ["站到两个路标之间、靠近路标连线的地方（y ≥ 3.5，|x| < 1）。离路标很近，定位却不准，为什么？", "Stand between the landmarks close to their line (y ≥ 3.5, |x| < 1). The landmarks are near, yet positioning is poor. Why?"],
      demo: { scene: "agv", set: { px: 0, py: 3.8, sb: 5 }, press: [] } },
    { id: "ratio", robot: true, text: ["在对称位置（x = 0）找一个条件数在 2 与 3 之间的点，比较误差椭圆的长短轴之比与 κ₂。", "On the symmetry line (x = 0) find a point with 2 < κ₂ < 3 and compare the axis ratio of the error ellipse with κ₂."],
      demo: { scene: "agv", set: { px: 0, py: -0.5, sb: 5 }, press: [] } },
    { id: "hike", text: ["山头场景：找一个条件数 κ₂ < 1.2 的位置。", "Summits: find a position with κ₂ < 1.2."],
      demo: { scene: "hike", set: { px: 0, py: 2, sb: 5 }, press: [] } },
  ],
  think: ["条件数只由两条方位线的夹角决定，与到路标的距离无关；可定位误差还与距离成正比。若想让定位误差最小，AGV 离两个路标多远、夹角多大最好？",
          "The condition number depends only on the angle between the bearing lines, not on the distances; the position error is also proportional to the distances. For the smallest error, how far from the landmarks and at what angle should the AGV be?"],

  L1: [-2, 4], L2: [2, 4],
  geo(api) {
    const P = [api.p.px, api.p.py], hike = api.scene === "hike";
    const sig = (hike ? 8.7 : api.p.sb) * 1e-3;                       // rad；指北针约 0.5° = 8.7 mrad
    const lines = [this.L1, this.L2].map((L) => {
      const d = [L[0] - P[0], L[1] - P[1]], r = Math.hypot(d[0], d[1]);
      return { L, r, d: [d[0] / r, d[1] / r], n: [-d[1] / r, d[0] / r] };
    });
    const N = lines.map((l) => l.n), det = N[0][0] * N[1][1] - N[0][1] * N[1][0];
    const Ni = [[N[1][1] / det, -N[0][1] / det], [-N[1][0] / det, N[0][0] / det]];
    const sv = api.la.svd(N).s, kap = sv[0] / sv[1];
    const cosang = Math.abs(lines[0].d[0] * lines[1].d[0] + lines[0].d[1] * lines[1].d[1]);
    const ang = Math.acos(Math.min(1, cosang)) * 180 / Math.PI;      // 两条直线的锐夹角
    // 定位误差的协方差 Σ = N⁻¹ diag((rᵢσ)²) N⁻ᵀ（单位：m²）
    const D = lines.map((l) => (l.r * sig) ** 2);
    const S = [[0, 0], [0, 0]];
    for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) S[i][j] = Ni[i][0] * Ni[j][0] * D[0] + Ni[i][1] * Ni[j][1] * D[1];
    const tr = S[0][0] + S[1][1], df = Math.sqrt(((S[0][0] - S[1][1]) / 2) ** 2 + S[0][1] ** 2);
    const a = Math.sqrt(tr / 2 + df), b = Math.sqrt(Math.max(tr / 2 - df, 0));
    const th = 0.5 * Math.atan2(2 * S[0][1], S[0][0] - S[1][1]);
    return { P, lines, kap, ang, a, b, th, sig, hike };
  },
  reset(api, s) {},
  readouts(api, s) {
    const g = this.geo(api), f = api.fmt, u = g.hike ? 1000 : 1000, unit = g.hike ? " m" : " mm";   // 山头场景 1 格 = 1 km，误差以 m 计
    if (!g.hike && g.kap < 1.5) api.done("good");
    if (!g.hike && g.kap > 20) api.done("bad");
    if (!g.hike && api.p.py >= 3.5 && Math.abs(api.p.px) < 1) api.done("between");
    if (!g.hike && Math.abs(api.p.px) < 0.05 && g.kap > 2 && g.kap < 3) api.done("ratio");
    if (g.hike && g.kap < 1.2) api.done("hike");
    return [[["两条方位线的夹角", "Angle between bearing lines"], f(g.ang, 1) + "°"],
            [["条件数 κ₂(N)", "Condition number κ₂(N)"], f(g.kap, 2)],
            [["到两个路标的距离", "Distances to the landmarks"], f(g.lines[0].r, 2) + ", " + f(g.lines[1].r, 2) + (g.hike ? " km" : " m")],
            [["方位误差", "Bearing error"], f(g.sig * 1000, 1) + " mrad"],
            [["误差椭圆的半轴（1 倍标准差）", "Error ellipse semi-axes (1σ)"], f(g.a * u, 1) + ", " + f(g.b * u, 1) + unit],
            [["长短轴之比", "Axis ratio"], f(g.a / Math.max(g.b, 1e-12), 2)],
            [["方位线平移的量 rᵢσ", "Line offsets rᵢσ"], f(g.lines[0].r * g.sig * u, 1) + ", " + f(g.lines[1].r * g.sig * u, 1) + unit]];
  },
  draw(api, s) {
    const g = this.geo(api), { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink");
    const x0 = -5, x1 = 5, y0 = -1.6, y1 = 5.2, sc = Math.min(w / (x1 - x0), h / (y1 - y0)) * 0.95;
    const ox = w / 2 - (x0 + x1) / 2 * sc, oy = h / 2 + (y0 + y1) / 2 * sc;
    const X = (x) => ox + x * sc, Y = (y) => oy - y * sc;
    if (!g.hike) { api.line(X(-4.8), Y(4.3), X(4.8), Y(4.3), ink, 3); api.label(api.T("仓库墙", "warehouse wall"), X(-4.8), Y(4.3) - 8, mu, 11); }
    // 方位线（延长）与 ±1σ 的平移带
    g.lines.forEach((l, i) => {
      const col = i ? api.css("--blue") : api.css("--red");
      api.line(X(l.L[0] - 12 * l.d[0]), Y(l.L[1] - 12 * l.d[1]), X(l.L[0] + 2 * l.d[0]), Y(l.L[1] + 2 * l.d[1]), col, 2);
      const off = l.r * g.sig * 20;                       // 平移带放大 20 倍画出
      [-1, 1].forEach((sgn) => api.line(X(l.L[0] - 12 * l.d[0] + sgn * off * l.n[0]), Y(l.L[1] - 12 * l.d[1] + sgn * off * l.n[1]),
                                        X(l.L[0] + 2 * l.d[0] + sgn * off * l.n[0]), Y(l.L[1] + 2 * l.d[1] + sgn * off * l.n[1]), col, 1, [4, 4]));
    });
    [this.L1, this.L2].forEach((L, i) => {
      if (g.hike) { api.line(X(L[0]) - 10, Y(L[1]) + 8, X(L[0]), Y(L[1]) - 10, ink, 2); api.line(X(L[0]), Y(L[1]) - 10, X(L[0]) + 10, Y(L[1]) + 8, ink, 2); }
      else api.rect(X(L[0]) - 6, Y(L[1]) - 6, 12, 12, api.css("--amber"), ink);
      api.label((g.hike ? api.T("山头 ", "summit ") : api.T("路标 ", "landmark ")) + (i + 1), X(L[0]) + 8, Y(L[1]) - 10, ink, 12);
    });
    if (g.hike) api.circle(X(g.P[0]), Y(g.P[1]), 6, api.css("--green"), ink);
    else api.robot(X(g.P[0]), Y(g.P[1]), 90, 20, api.css("--accent"));
    // 误差椭圆（放大 20 倍画出，画在车的上面）
    let prev = null;
    for (let k = 0; k <= 72; k++) {
      const t = 2 * Math.PI * k / 72, ex = 20 * (g.a * Math.cos(t) * Math.cos(g.th) - g.b * Math.sin(t) * Math.sin(g.th)),
            ey = 20 * (g.a * Math.cos(t) * Math.sin(g.th) + g.b * Math.sin(t) * Math.cos(g.th));
      const q = [X(g.P[0] + ex), Y(g.P[1] + ey)];
      if (prev) api.line(prev[0], prev[1], q[0], q[1], api.css("--green"), 2.5);
      prev = q;
    }
    api.label(api.T("方位误差带与误差椭圆都放大 20 倍画出" + (g.hike ? "（1 格 = 1 km）" : "（1 格 = 1 m）"), "error bands and ellipse drawn ×20" + (g.hike ? " (1 unit = 1 km)" : " (1 unit = 1 m)")), 10, h - 10, mu, 11);
  },
});
