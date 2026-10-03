// 实验 14.2 平面两连杆、三连杆的逆解（配 14.2 节）。
// 机器人场景：平面 2R 臂 l₁ = 0.425 m、l₂ = 0.392 m（UR5e 的大臂、小臂），可加 l₃ = 0.1 m 的工具成为 3R。
// θ₂ 用式 (14.2.6) 的因式分解求 1 ∓ cos θ₂，再用 atan2；θ₁ 用式 (14.2.4)；3R 先由式 (14.2.9) 求腕点，θ₃ = φ − θ₁ − θ₂。
// 生活场景：折臂台灯（两段灯臂 0.30 m、0.28 m，灯罩 0.08 m 竖直向下），灯罩的位置由目标点给出。
WQ.lab({
  title: ["实验 14.2 平面两连杆、三连杆的逆解", "Lab 14.2 Inverse kinematics of planar 2R and 3R arms"],
  goal: ["拖动目标点，看逆解有几组、各是什么样子；体会肘上与肘下、边界附近两解合一、以及先定腕点再解 2R 的做法。",
         "Drag the target and see how many solutions there are and what they look like: elbow up and down, two solutions merging at the edge, and fixing the wrist first for a 3R arm."],
  scenes: [
    { id: "arm", robot: true, name: ["平面 2R/3R 臂", "Planar 2R/3R arm"],
      problem: { title: ["机器人问题：末端要到这里，关节角是多少", "Robot problem: which joint angles put the tip here"],
                 text: ["拖动目标 (x, y)，选择 2R 或 3R（3R 还要给工具朝向 φ）。界面列出全部逆解，实线是选中的构型，虚线是另一组。",
                        "Drag the target (x, y); choose 2R or 3R (3R also needs the tool angle φ). All solutions are listed; the chosen one is solid, the other dashed."] } },
    { id: "lamp", name: ["台灯照到书上", "A desk lamp over a book"], hide: ["phi", "n3"],
      problem: { title: ["生活中的例子：台灯的两种摆法", "Everyday example: two ways to set a desk lamp"],
                 text: ["灯罩要停在书本正上方、竖直向下照。灯罩的方向定了，连接灯罩的铰链位置也就定了；两段灯臂可以向上拱起，也可以向下垂。",
                        "The shade must sit right above the book, pointing down. That fixes the hinge at the shade; the two arms may arch up or sag down."] } },
  ],
  params: [
    { id: "x", name: ["目标 x", "target x"], min: -0.9, max: 0.9, step: 0.01, value: 0.45, unit: "m", digits: 2 },
    { id: "y", name: ["目标 y", "target y"], min: -0.9, max: 0.9, step: 0.01, value: 0.35, unit: "m", digits: 2 },
    { id: "n3", name: ["连杆数：0 为 2R，1 为 3R", "links: 0 = 2R, 1 = 3R"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "phi", name: ["3R 的工具朝向 φ", "3R tool angle φ"], min: -180, max: 180, step: 1, value: -90, unit: "°", digits: 0 },
    { id: "up", name: ["构型：0 为 θ₂ > 0，1 为 θ₂ < 0", "branch: 0 = θ₂ > 0, 1 = θ₂ < 0"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 14.2.1：2R 臂，目标 (0.45, 0.35) m，读出两组解 (−5.55°, 91.60°) 和 (81.30°, −91.60°)。",
                                     "Example 14.2.1: 2R, target (0.45, 0.35) m; read the two solutions (−5.55°, 91.60°) and (81.30°, −91.60°)."],
      demo: { scene: "arm", set: { x: 0.45, y: 0.35, n3: 0, up: 0 }, press: [], wait: 1 } },
    { id: "up", robot: true, text: ["在同一目标下选择肘上构型（θ₂ < 0）。", "At the same target choose the elbow-up branch (θ₂ < 0)."],
      demo: { scene: "arm", set: { x: 0.45, y: 0.35, n3: 0, up: 1 }, press: [], wait: 1 } },
    { id: "edge", robot: true, text: ["2R：把目标移到外边界附近（离基座 0.80 m 以上），使两组解的 θ₂ 都小于 12°。",
                                       "2R: move the target near the outer edge (over 0.80 m from the base) so that both solutions have |θ₂| under 12°."],
      demo: { scene: "arm", set: { x: 0.81, y: 0.1, n3: 0, up: 0 }, press: [], wait: 1 } },
    { id: "tool", robot: true, text: ["切换到 3R，复现算例 14.2.2：目标 (0.6, 0.05) m，工具朝下（φ = −90°），读出腕点和两组解。",
                                       "Switch to 3R, Example 14.2.2: target (0.6, 0.05) m with the tool down (φ = −90°); read the wrist point and both solutions."],
      demo: { scene: "arm", set: { x: 0.6, y: 0.05, n3: 1, phi: -90, up: 0 }, press: [], wait: 1 } },
    { id: "lamp", text: ["生活场景：把灯罩移到书本正上方 (0.35, 0.25) m，并让灯臂向上拱起。",
                         "Everyday scene: put the shade above the book at (0.35, 0.25) m with the arms arching up."],
      demo: { scene: "lamp", set: { x: 0.35, y: 0.25, up: 1 }, press: [], wait: 1 } },
  ],
  think: ["目标在外边界上时，arccos 写法为什么有时报告“够不着”？式 (14.2.6) 的写法为什么不会？",
          "Why does the arccos formula sometimes call a target on the outer edge unreachable, while Eq. (14.2.6) does not?"],

  // 平面 2R 逆解：返回 [{t1, t2}]，θ₂ > 0 的在前
  ik2(x, y, l1, l2) {
    const r = Math.hypot(x, y), om = (l1 + l2 - r) * (l1 + l2 + r) / (2 * l1 * l2), op = (r - Math.abs(l1 - l2)) * (r + Math.abs(l1 - l2)) / (2 * l1 * l2);
    if (om < -1e-12 || op < -1e-12) return [];
    const c = (Math.max(op, 0) - Math.max(om, 0)) / 2, s = Math.sqrt(Math.max(om, 0) * Math.max(op, 0));
    return (s < 1e-12 ? [1] : [1, -1]).map((g) => {
      const t2 = Math.atan2(g * s, c);
      return { t1: Math.atan2(y, x) - Math.atan2(l2 * Math.sin(t2), l1 + l2 * Math.cos(t2)), t2 };
    });
  },
  wrap(a) { return Math.atan2(Math.sin(a), Math.cos(a)); },
  geo(api) {
    if (api.scene === "lamp") return { L: [0.30, 0.28, 0.08], three: true, phi: -Math.PI / 2 };
    return { L: [0.425, 0.392, 0.1], three: api.p.n3 === 1, phi: api.p.phi * Math.PI / 180 };
  },
  solve(api) {
    const g = this.geo(api), x = api.p.x, y = api.p.y;
    const w = g.three ? [x - g.L[2] * Math.cos(g.phi), y - g.L[2] * Math.sin(g.phi)] : [x, y];
    const s = this.ik2(w[0], w[1], g.L[0], g.L[1]).map((q) => ({ t1: this.wrap(q.t1), t2: q.t2, t3: g.three ? this.wrap(g.phi - q.t1 - q.t2) : null }));
    return { g, w, s };
  },
  deg(a) { return (a * 180 / Math.PI).toFixed(2) + "°"; },

  reset(api, s) { s.ok = true; },
  readouts(api, s) {
    const { g, w, s: sol } = this.solve(api), d = (v) => this.deg(v), r = Math.hypot(w[0], w[1]);
    const near = (a, b) => Math.abs(a - b) < 1e-9;
    if (api.scene === "arm" && !g.three && near(api.p.x, 0.45) && near(api.p.y, 0.35) && sol.length === 2) {
      api.done("ex");
      if (api.p.up === 1) api.done("up");
    }
    if (api.scene === "arm" && !g.three && r > 0.8 && sol.length === 2 && sol.every((q) => Math.abs(q.t2) < 12 * Math.PI / 180)) api.done("edge");
    if (api.scene === "arm" && g.three && near(api.p.x, 0.6) && near(api.p.y, 0.05) && api.p.phi === -90 && sol.length === 2) api.done("tool");
    if (api.scene === "lamp" && near(api.p.x, 0.35) && near(api.p.y, 0.25) && api.p.up === 1 && sol.length === 2) api.done("lamp");
    const rows = [[["解的个数", "number of solutions"], String(sol.length)],
                  [[g.three ? "腕点到基座的距离" : "目标到基座的距离", g.three ? "wrist distance from base" : "target distance from base"], api.fmt(r, 4) + " m"]];
    if (g.three) rows.push([["腕点 W", "wrist point W"], `(${api.fmt(w[0], 3)}, ${api.fmt(w[1], 3)}) m`]);
    sol.forEach((q, i) => rows.push([[`解 ${i + 1}（θ₂ ${q.t2 >= 0 ? ">" : "<"} 0）`, `solution ${i + 1} (θ₂ ${q.t2 >= 0 ? ">" : "<"} 0)`],
      `(${d(q.t1)}, ${d(q.t2)}${g.three ? ", " + d(q.t3) : ""})`]));
    if (!sol.length) rows.push([["状态", "status"], api.T("够不着：目标在圆环之外", "out of reach: outside the ring")]);
    return rows;
  },
  draw(api, s) {
    const { w: W, h: H } = api, { g, w, s: sol } = this.solve(api), lamp = api.scene === "lamp";
    const reach = g.L[0] + g.L[1] + (g.three ? g.L[2] : 0);
    const sc = lamp ? Math.min(W * 0.7, H * 0.75) / 0.7 : Math.min(W * 0.42, H * 0.46) / reach;
    const bx = lamp ? W * 0.3 : W * 0.48, by = lamp ? H * 0.85 : H * 0.52;
    const P = (x, y) => [bx + sc * x, by - sc * y];
    if (lamp) {
      api.rect(0, by, W, 10, api.css("--grid"));
      const bk = P(0.27, 0.0);
      api.rect(bk[0], bk[1] - 8, sc * 0.16, 8, api.css("--amber"));
      api.label(api.T("书", "book"), ...P(0.35, -0.04), api.css("--ink"), 13, "center");
    } else {
      api.circle(bx, by, sc * (g.L[0] + g.L[1]), null, api.css("--grid"));
      api.circle(bx, by, sc * Math.abs(g.L[0] - g.L[1]), null, api.css("--grid"));
      api.label(api.T("灰圆：2R 的内外边界", "grey circles: 2R inner and outer edges"), 12, 18, api.css("--muted"), 12);
    }
    const sel = sol.length === 2 ? (api.p.up === 1 ? 1 : 0) : 0;
    sol.forEach((q, i) => {
      const e = [g.L[0] * Math.cos(q.t1), g.L[0] * Math.sin(q.t1)];
      const pts = [[0, 0], e, w];
      if (g.three) pts.push([api.p.x, api.p.y]);
      const col = i === sel ? (lamp ? api.css("--accent") : (q.t2 >= 0 ? api.css("--accent") : api.css("--blue"))) : api.css("--muted");
      for (let k = 0; k + 1 < pts.length; k++) api.line(...P(...pts[k]), ...P(...pts[k + 1]), col, i === sel ? (k < 2 ? 8 : 5) : 3, i === sel ? null : [6, 5]);
      pts.slice(0, -1).forEach((p) => api.circle(...P(...p), i === sel ? 5 : 3, api.css("--panel"), col));
      if (lamp && i === sel) { const c = P(api.p.x, api.p.y); api.circle(c[0], c[1] + 6, 14, api.css("--amber"), api.css("--ink")); }
    });
    const tg = P(api.p.x, api.p.y);
    api.line(tg[0] - 9, tg[1], tg[0] + 9, tg[1], api.css("--red"), 2); api.line(tg[0], tg[1] - 9, tg[0], tg[1] + 9, api.css("--red"), 2);
    if (g.three && !lamp) { const c = P(...w); api.circle(c[0], c[1], 5, api.css("--ink")); api.label("W", c[0] + 8, c[1] - 10, api.css("--ink"), 13); }
    api.circle(bx, by, 6, api.css("--ink"));
  },
});
