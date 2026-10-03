// 实验 2.2 两连杆机械臂：末端位置是两个连杆向量之和（配 2.2 节）。
// UR5e 上臂 0.425 m、前臂 0.392 m（零件库 2026.10.9 版关节表）；肩关节为原点，θ₂ 为前臂相对上臂的转角。
WQ.lab({
  title: ["实验 2.2 两连杆机械臂：末端位置是两个连杆向量之和", "Lab 2.2 Two-link arm: the tool position is the sum of two link vectors"],
  goal: ["拖动两个关节角，看上臂向量、前臂向量和它们的和怎样变化；体会平行四边形法则；调节两个系数，用线性组合凑出目标向量。",
         "Drag the two joint angles and watch the upper-arm vector, the forearm vector and their sum; see the parallelogram rule; tune two coefficients to reach a target as a linear combination."],
  scenes: [
    { id: "arm", robot: true, name: ["两连杆臂", "Two-link arm"], hide: ["c1", "c2"],
      problem: { title: ["机器人问题：腕心在哪里？", "Robot problem: where is the wrist centre?"],
                 text: ["UR5e 只转肩关节和肘关节时，手臂相当于平面里的两连杆。从肩关节出发先走上臂向量 r₁，再走前臂向量 r₂，就到了腕心：p = r₁ + r₂。",
                        "Turning only the shoulder and elbow, the UR5e is a planar two-link arm. Walk the upper-arm vector r₁, then the forearm vector r₂: you reach the wrist centre, p = r₁ + r₂."] } },
    { id: "para", name: ["平行四边形", "Parallelogram"], hide: ["c1", "c2"],
      problem: { title: ["先走哪一段都一样", "The order does not matter"],
                 text: ["先走 r₁ 再走 r₂，与先走 r₂ 再走 r₁，到达同一点。两条路径围成一个平行四边形，对角线就是 r₁ + r₂。",
                        "r₁ then r₂, or r₂ then r₁: the same end point. The two paths bound a parallelogram whose diagonal is r₁ + r₂."] } },
    { id: "combo", name: ["线性组合", "Linear combination"], hide: ["t1", "t2"],
      problem: { title: ["用 u、w 凑出 b", "Reach b with u and w"],
                 text: ["u = (2, 1)ᵀ，w = (1, 3)ᵀ。调节系数 c₁、c₂，使 c₁u + c₂w 等于目标 b = (7, 11)ᵀ。斜网格的格点是整数系数的组合。",
                        "u = (2, 1)ᵀ, w = (1, 3)ᵀ. Tune c₁, c₂ so that c₁u + c₂w equals the target b = (7, 11)ᵀ. The skew grid points are integer combinations."] } },
  ],
  params: [
    { id: "t1", name: ["肩关节角 θ₁", "Shoulder angle θ₁"], min: -180, max: 180, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "t2", name: ["肘关节角 θ₂（相对上臂）", "Elbow angle θ₂ (relative)"], min: -180, max: 180, step: 0.5, value: 45, unit: "°", digits: 1 },
    { id: "c1", name: ["系数 c₁", "Coefficient c₁"], min: -3, max: 5, step: 0.1, value: 1, digits: 1 },
    { id: "c2", name: ["系数 c₂", "Coefficient c₂"], min: -3, max: 5, step: 0.1, value: 1, digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "far", robot: true, text: ["让腕心离肩关节最远（距离大于 0.816 m）。此时两个连杆向量有什么关系？", "Put the wrist as far from the shoulder as possible (over 0.816 m). How are the link vectors related?"],
      demo: { scene: "arm", set: { t1: 30, t2: 0 }, press: [], wait: 1 } },
    { id: "near", robot: true, text: ["让腕心离肩关节最近（距离小于 0.035 m）。", "Bring the wrist closest to the shoulder (under 0.035 m)."],
      demo: { scene: "arm", set: { t1: 30, t2: 180 }, press: [], wait: 1 } },
    { id: "swap", text: ["在“平行四边形”场景把平行四边形调成矩形（r₁ ⟂ r₂，读数 r₁·r₂ 的绝对值小于 0.001），此时 ‖p‖² 与 l₁² + l₂² 有什么关系？", "In the parallelogram scene make the parallelogram a rectangle (r₁ ⟂ r₂, |r₁·r₂| < 0.001). How is ‖p‖² related to l₁² + l₂² then?"],
      demo: { scene: "para", set: { t1: 60, t2: -90 }, press: [], wait: 1 } },
    { id: "combo", text: ["在“线性组合”场景凑出 b = (7, 11)ᵀ。系数是多少？", "In the combination scene reach b = (7, 11)ᵀ. What are the coefficients?"],
      demo: { scene: "combo", set: { c1: 2, c2: 3 }, press: [], wait: 1 } },
  ],
  think: ["两个关节角取遍一切值时，腕心能到达的区域是什么形状？用三角不等式说明它的内外边界。",
          "As both joint angles vary, what region can the wrist reach? Explain its inner and outer boundaries with the triangle inequality."],

  l1: 0.425, l2: 0.392,
  links(api) {
    const d = Math.PI / 180, a = api.p.t1 * d, b = (api.p.t1 + api.p.t2) * d;
    return [[this.l1 * Math.cos(a), this.l1 * Math.sin(a)], [this.l2 * Math.cos(b), this.l2 * Math.sin(b)]];
  },
  readouts(api) {
    const v3 = (v, k) => api.la.vstr(v, k);
    if (api.scene === "combo") {
      const u = [2, 1], w = [1, 3], c1 = api.p.c1, c2 = api.p.c2, x = [c1 * u[0] + c2 * w[0], c1 * u[1] + c2 * w[1]];
      const err = Math.hypot(x[0] - 7, x[1] - 11);
      if (err < 0.05) api.done("combo");
      return [[["c₁u", "c₁u"], v3([c1 * u[0], c1 * u[1]], 1)], [["c₂w", "c₂w"], v3([c2 * w[0], c2 * w[1]], 1)],
              [["c₁u + c₂w", "c₁u + c₂w"], v3(x, 1)], [["到目标 b 的距离", "Distance to b"], api.fmt(err, 3)]];
    }
    const [r1, r2] = this.links(api), p = [r1[0] + r2[0], r1[1] + r2[1]], L = Math.hypot(...p);
    if (api.scene === "arm" && L > 0.816) api.done("far");
    if (api.scene === "arm" && L < 0.035) api.done("near");
    const rows = [[["上臂向量 r₁", "Upper arm r₁"], v3(r1, 4) + " m"], [["前臂向量 r₂", "Forearm r₂"], v3(r2, 4) + " m"],
                  [["腕心 p = r₁ + r₂", "Wrist p = r₁ + r₂"], v3(p, 4) + " m"], [["‖p‖（到肩关节的距离）", "‖p‖ (distance)"], api.fmt(L, 4) + " m"],
                  [["‖r₁‖ + ‖r₂‖ 与 |‖r₁‖ − ‖r₂‖|", "‖r₁‖ + ‖r₂‖ and |‖r₁‖ − ‖r₂‖|"], "0.817 / 0.033 m"]];
    if (api.scene === "para") {
      const q = [r2[0] + r1[0], r2[1] + r1[1]], diff = Math.hypot(q[0] - p[0], q[1] - p[1]);
      const dot = r1[0] * r2[0] + r1[1] * r2[1];
      if (Math.abs(dot) < 0.001) api.done("swap");
      rows.push([["r₂ + r₁", "r₂ + r₁"], v3(q, 4) + " m"], [["两条路径终点之差", "Difference of end points"], api.fmt(diff, 6) + " m"],
                [["r₁·r₂", "r₁·r₂"], api.fmt(dot, 4) + " m²"], [["‖p‖² 与 l₁² + l₂²", "‖p‖² and l₁² + l₂²"], api.fmt(L * L, 4) + " / " + api.fmt(this.l1 ** 2 + this.l2 ** 2, 4) + " m²"]);
    }
    return rows;
  },
  draw(api) {
    const { w: W, h: H } = api, red = api.css("--red"), green = api.css("--green"), blue = api.css("--blue"), muted = api.css("--muted");
    if (api.scene === "combo") {
      const P = api.plane({ cx: W * 0.3, cy: H * 0.82, s: Math.min(W, H) * 0.055, w: W, h: H });
      P.grid([[2, 1], [1, 3]], { n: 6, alpha: 0.25 });
      const u = [2, 1], w = [1, 3], c1 = api.p.c1, c2 = api.p.c2, a = [c1 * u[0], c1 * u[1]], x = [a[0] + c2 * w[0], a[1] + c2 * w[1]];
      P.point([7, 11], api.css("--amber"), "b = (7, 11)");
      P.vec(a, blue, "c₁u");
      const s = P.X(...a), e = P.X(...x);
      api.arrow(s[0], s[1], e[0], e[1], green, 3);
      api.label("c₂w", (s[0] + e[0]) / 2 + 8, (s[1] + e[1]) / 2, green, 14);
      P.vec(x, red, null, 2);
      P.vec(u, blue, "u", 4); P.vec(w, green, "w", 4);
      api.label(api.T("斜网格：整数系数的组合", "skew grid: integer combinations"), W - 10, 18, muted, 12, "right");
      return;
    }
    const k = Math.min(W, H) * 0.5, P = api.plane({ cx: W * 0.45, cy: H * 0.55, s: k, w: W, h: H });
    P.axes();
    const ring = (r, dash) => { const c = api.ctx; c.beginPath(); c.arc(W * 0.45, H * 0.55, r * k, 0, 2 * Math.PI); c.setLineDash(dash); c.strokeStyle = muted; c.lineWidth = 1; c.stroke(); c.setLineDash([]); };
    ring(0.817, [5, 5]); ring(0.033, [3, 3]);
    const [r1, r2] = this.links(api), p = [r1[0] + r2[0], r1[1] + r2[1]];
    const O = P.X(0, 0), E = P.X(...r1), T = P.X(...p);
    api.line(...O, ...E, "#9db4c8", 12); api.line(...E, ...T, "#9db4c8", 10);
    if (api.scene === "para") {
      const A = P.X(...r2);
      api.arrow(...O, ...A, green, 2.5); api.arrow(...A, ...T, blue, 2.5);
      api.line(...E, ...T, muted, 1); api.line(...A, ...T, muted, 1);
    }
    api.arrow(...O, ...E, blue, 3); api.arrow(...E, ...T, green, 3); api.arrow(...O, ...T, red, 2.5);
    api.circle(...O, 6, api.css("--panel"), api.css("--ink")); api.circle(...E, 5, api.css("--panel"), api.css("--ink"));
    api.label("r₁", (O[0] + E[0]) / 2 + 6, (O[1] + E[1]) / 2 + 14, blue, 14);
    api.label("r₂", (E[0] + T[0]) / 2 + 8, (E[1] + T[1]) / 2, green, 14);
    api.label("p", T[0] + 8, T[1] - 8, red, 15);
    api.label(api.T("虚线圆：半径 0.817 m 与 0.033 m", "dashed circles: radii 0.817 m and 0.033 m"), W - 10, 18, muted, 12, "right");
  },
});
