// 实验 17.1 冗余度与自运动流形（配 17.1 节）。
// 机器人场景：平面 3R 臂 0.425、0.392、0.1 m（14.2.5 节），只管末端位置（m = 2，n = 3，冗余度 1）。
//   以工具朝向 φ 为参数：腕点 w = p − l₃(cos φ, sin φ)（式 (14.2.9)），2R 臂的两组解析解给出 θ₁、θ₂，θ₃ = φ − θ₁ − θ₂。
//   “分支”0 为 θ₂ > 0（14.2.2 节称为肘下），1 为 θ₂ < 0（肘上）。右侧画出目标的自运动流形在 (θ₁, θ₂) 平面上的投影：
//   对 φ 的 720 个取值逐个求两组解。闭曲线的条数：φ 全周都有解时为 2，否则等于有解的 φ 区间个数（算例 17.1.1）。
//   按“开始”：手臂沿自运动流形走一圈（φ 全周可行时沿当前分支转 360°；否则沿当前分支从区间一端走到另一端，在 θ₂ = 0 处换到另一分支走回来）。
// 生活场景：人的手臂（上臂 0.30 m、前臂 0.27 m、手指 0.08 m），肩在原点，手指按住门铃按钮 (0.45, −0.05) m 不动；
//   调节手的朝向 φ，肘部的高度随之变化。肘部最高约比肩高 0.21 m（φ ≈ −48°、θ₂ < 0 的一支）。
WQ.lab({
  title: ["实验 17.1 冗余度与自运动流形", "Lab 17.1 Redundancy and the self-motion manifold"],
  goal: ["只给末端位置时，平面 3R 臂多出一个自由度：末端不动，手臂可以沿自运动流形运动。看这个流形在 (θ₁, θ₂) 平面上是什么形状，有几条闭曲线，怎样随目标变化。",
         "With only the tip position given, a planar 3R arm has one spare freedom: the tip stays and the arm moves along the self-motion manifold. See its shape in the (θ₁, θ₂) plane, how many closed curves it has and how this changes with the goal."],
  scenes: [
    { id: "arm", robot: true, name: ["平面 3R 臂只管位置", "Planar 3R arm, position only"], hide: [],
      problem: { title: ["机器人问题：末端位置给定，手臂还能怎样动？", "Robot problem: with the tip position fixed, how can the arm still move?"],
                 text: ["红点是目标。腕点只能在以目标为圆心、半径 0.1 m 的小圆上（虚线），还要在 2R 臂的圆环以内。拖动工具朝向 φ 或按“开始”，手臂沿自运动流形运动；右图是流形在 (θ₁, θ₂) 平面上的投影，蓝色为 θ₂ > 0 的一族，金色为 θ₂ < 0 的一族。",
                        "The red dot is the goal. The wrist must lie on the small dashed circle of radius 0.1 m around it and inside the 2R annulus. Drag the tool direction φ or press “Start”: the arm moves along the self-motion manifold; the right plot shows the manifold in the (θ₁, θ₂) plane, blue for θ₂ > 0 and gold for θ₂ < 0."] } },
    { id: "bell", name: ["手指按住门铃", "A finger on a doorbell"], hide: ["tx", "ty"],
      problem: { title: ["生活中的例子：按住门铃不放，肘部能抬多高？", "Everyday example: keeping a finger on the doorbell, how high can the elbow go?"],
                 text: ["手指尖按在按钮上不动（只管指尖的位置），肩、肘、腕三个关节多出一个自由度。转动手的朝向 φ、换一个分支，看肘部的高度怎样变化。",
                        "The fingertip stays on the button (only its position matters), so shoulder, elbow and wrist have one spare freedom. Turn the hand direction φ and switch branches to see how the elbow height changes."] } },
  ],
  params: [
    { id: "tx", name: ["目标 x", "goal x"], min: -0.9, max: 0.95, step: 0.005, value: 0.5, unit: "m", digits: 3 },
    { id: "ty", name: ["目标 y", "goal y"], min: -0.6, max: 0.9, step: 0.005, value: 0.3, unit: "m", digits: 3 },
    { id: "phi", name: ["工具（手）的朝向 φ", "tool (hand) direction φ"], min: -180, max: 180, step: 0.5, value: 30, unit: "°", digits: 1 },
    { id: "br", name: ["分支：0 θ₂ > 0（肘下） / 1 θ₂ < 0（肘上）", "branch: 0 θ₂ > 0 (elbow down) / 1 θ₂ < 0 (elbow up)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  legend: [{ color: "#1f6feb", name: ["θ₂ > 0 的一族", "θ₂ > 0 family"] }, { color: "#d29922", name: ["θ₂ < 0 的一族", "θ₂ < 0 family"] }, { color: "#cf222e", name: ["目标", "goal"] }],
  tasks: [
    { id: "loopA", robot: true, text: ["目标 A = (0.5, 0.3) m：按“开始”，沿 θ₂ > 0 的一族走完一整圈，末端始终在 A（两条闭曲线）。",
                                       "Goal A = (0.5, 0.3) m: press “Start” and go once round the θ₂ > 0 family with the tip always at A (two closed curves)."],
      demo: { scene: "arm", set: { tx: 0.5, ty: 0.3, br: 0 }, press: ["start"], wait: 9 } },
    { id: "joinB", robot: true, text: ["目标 B = (0.75, 0.10) m：按“开始”，手臂经过 |θ₂| < 0.5° 的形态，从一族连续地走到另一族（只有一条闭曲线）。",
                                       "Goal B = (0.75, 0.10) m: press “Start”; the arm passes a configuration with |θ₂| < 0.5° and moves on continuously into the other family (one closed curve only)."],
      demo: { scene: "arm", set: { tx: 0.75, ty: 0.1, br: 0 }, press: ["start"], wait: 9 } },
    { id: "near", robot: true, text: ["把目标放到离基座很近的地方（d < 0.2 m），找到一个只有一条闭曲线的目标。",
                                      "Put the goal close to the base (d < 0.2 m) and find one whose manifold is a single closed curve."],
      demo: { scene: "arm", set: { tx: 0.1, ty: 0.0 }, press: [], wait: 2 } },
    { id: "far", robot: true, text: ["找一个够不着的目标（d > 0.917 m），自运动流形是空集。", "Find a goal out of reach (d > 0.917 m): the manifold is empty."],
      demo: { scene: "arm", set: { tx: 0.9, ty: 0.3 }, press: [], wait: 2 } },
    { id: "bell", text: ["生活场景：指尖按住门铃不动，把肘部抬到最高（达到最大高度的 98% 以上）。",
                         "Everyday scene: with the fingertip on the bell, raise the elbow as high as it goes (at least 98% of the maximum)."],
      demo: { scene: "bell", set: { br: 1, phi: -48 }, press: [], wait: 2 } },
  ],
  think: ["目标 B 处两族在 θ₂ = 0 相接，此时 2R 部分伸直，可 3R 臂对位置任务并不奇异，为什么？在这一点，φ 为什么不能再作流形的参数？",
          "At goal B the families join at θ₂ = 0, where the 2R part is straight; yet the 3R arm is not singular for the position task. Why? Why can φ no longer serve as the parameter there?"],

  LR: [0.425, 0.392, 0.1], LH: [0.30, 0.27, 0.08], BELL: [0.45, -0.05], NPHI: 720,
  rad: (d) => d * Math.PI / 180, deg: (r) => r * 180 / Math.PI,
  wrap(a) { return Math.atan2(Math.sin(a), Math.cos(a)); },
  L(api) { return api.scene === "arm" ? this.LR : this.LH; },
  target(api) { return api.scene === "arm" ? [api.p.tx, api.p.ty] : this.BELL; },
  ik(L, p, phi, br) {   // 一个 φ、一个分支的解；无解返回 null
    const wx = p[0] - L[2] * Math.cos(phi), wy = p[1] - L[2] * Math.sin(phi);
    const c2 = (wx * wx + wy * wy - L[0] * L[0] - L[1] * L[1]) / (2 * L[0] * L[1]);
    if (c2 > 1 + 1e-12 || c2 < -1 - 1e-12) return null;
    const t2 = Math.acos(Math.max(-1, Math.min(1, c2))) * (br === 0 ? 1 : -1);
    const t1 = Math.atan2(wy, wx) - Math.atan2(L[1] * Math.sin(t2), L[0] + L[1] * Math.cos(t2));
    return [this.wrap(t1), t2, this.wrap(phi - t1 - t2)];
  },
  pts(th, L) { let a = 0; const P = [[0, 0]]; th.forEach((t, i) => { a += t; P.push([P[i][0] + L[i] * Math.cos(a), P[i][1] + L[i] * Math.sin(a)]); }); return P; },
  // 可行的 φ 区间：腕点到基座的距离 ρ(φ) 在 [|l₁ − l₂|, l₁ + l₂] 之内
  feasible(L, p) {
    const N = this.NPHI, ok = [];
    for (let k = 0; k < N; k++) { const f = -Math.PI + 2 * Math.PI * k / N; ok.push(!!this.ik(L, p, f, 0)); }
    return ok;
  },
  loops(ok) { if (ok.every((x) => x)) return 2; let n = 0; for (let k = 0; k < ok.length; k++) if (ok[k] && !ok[(k - 1 + ok.length) % ok.length]) n++; return n; },
  // 可行区间端点的精确值（只有一个区间时）：|w| = l₁ + l₂ 或 |l₁ − l₂|
  interval(L, p, ok) {
    if (this.loops(ok) !== 1 || ok.every((x) => x)) return null;
    const N = ok.length; let k0 = 0; while (!(ok[k0] && !ok[(k0 - 1 + N) % N])) k0++;
    let k1 = k0; while (ok[(k1 + 1) % N]) k1++;
    const f = (k) => -Math.PI + 2 * Math.PI * k / N;
    const refine = (a, c) => { for (let i = 0; i < 60; i++) { const m = (a + c) / 2; if (this.ik(L, p, m, 0)) c = m; else a = m; } return c; };
    const refine2 = (a, c) => { for (let i = 0; i < 60; i++) { const m = (a + c) / 2; if (this.ik(L, p, m, 0)) a = m; else c = m; } return a; };
    return [refine(f(k0 - 1), f(k0)), refine2(f(k1), f(k1 + 1))];
  },
  manifold(api, s) {   // 当前目标的流形（每次改参数时重算）
    const L = this.L(api), p = this.target(api), key = [api.scene, p[0], p[1]].join(",");
    if (s.mkey === key) return;
    s.mkey = key; s.ok = this.feasible(L, p); s.nl = this.loops(s.ok); s.iv = this.interval(L, p, s.ok);
    s.cloud = [[], []];
    for (let k = 0; k < this.NPHI; k++) {
      const f = -Math.PI + 2 * Math.PI * k / this.NPHI;
      for (const br of [0, 1]) { const th = this.ik(L, p, f, br); if (th) s.cloud[br].push([this.deg(th[0]), this.deg(th[1])]); }
    }
    if (api.scene === "bell") {   // 肘部能达到的最大高度
      let hmax = -1; for (let k = 0; k < 3600; k++) { const f = -Math.PI + 2 * Math.PI * k / 3600;
        for (const br of [0, 1]) { const th = this.ik(L, p, f, br); if (th) hmax = Math.max(hmax, L[0] * Math.sin(th[0])); } }
      s.hmax = hmax;
    }
  },
  pose(api, s) {   // 当前形态：沿“开始”的轨迹时取轨迹上的点，否则取滑块
    if (s.path) return s.path[Math.min(s.path.length - 1, Math.floor(s.u))];
    const th = this.ik(this.L(api), this.target(api), this.rad(api.p.phi), api.p.br);
    return th ? { th, phi: this.rad(api.p.phi), br: api.p.br } : null;
  },
  reset(api, s) { s.path = null; s.u = 0; s.minT2 = 99; s.lapDone = false; s.mkey = null; this.manifold(api, s); },
  start(api, s) {
    const L = this.L(api), p = this.target(api);
    this.manifold(api, s);
    s.path = []; s.u = 0; s.minT2 = 99; s.lapDone = false; s.maxErr = 0;
    const br = api.p.br, n = 360;
    if (s.nl === 2) {
      const f0 = this.rad(api.p.phi);
      for (let k = 0; k <= n; k++) { const f = f0 + 2 * Math.PI * k / n, th = this.ik(L, p, f, br); if (th) s.path.push({ th, phi: f, br }); }
    } else if (s.iv) {
      const [a, b] = s.iv, half = n / 2;
      for (let k = 0; k <= half; k++) { const f = a + (b - a) * k / half, th = this.ik(L, p, f, br); if (th) s.path.push({ th, phi: f, br }); }
      for (let k = 0; k <= half; k++) { const f = b - (b - a) * k / half, th = this.ik(L, p, f, 1 - br); if (th) s.path.push({ th, phi: f, br: 1 - br }); }
    }
    if (!s.path.length) { s.path = null; api.stop(); }
  },
  update(dt, api, s) {
    if (!s.path) { api.stop(); return; }
    const k0 = Math.min(s.path.length - 1, Math.floor(s.u));
    s.u += dt * 60;
    const k1 = Math.min(s.path.length - 1, Math.floor(s.u)), p = this.target(api);
    for (let k = k0; k <= k1; k++) {   // 一帧可能跨过几个点（帧率低时），逐点检查，不漏掉 θ₂ = 0 的接头
      const q = s.path[k], P = this.pts(q.th, this.L(api));
      s.minT2 = Math.min(s.minT2, Math.abs(this.deg(q.th[1])));
      s.maxErr = Math.max(s.maxErr || 0, Math.hypot(P[3][0] - p[0], P[3][1] - p[1]));
    }
    if (s.u >= s.path.length - 1) { s.lapDone = true; api.stop(); }
  },
  readouts(api, s) {
    this.manifold(api, s);
    const p = this.target(api), d = Math.hypot(p[0], p[1]), q = this.pose(api, s), L = this.L(api);
    const rows = [[["目标到基座（肩）的距离 d", "goal distance d from the base (shoulder)"], d.toFixed(3) + " m"]];
    rows.push([["自运动闭曲线的条数", "closed curves of the manifold"], String(s.nl)]);
    rows.push([["可行的 φ 范围", "feasible φ"], s.nl === 2 ? api.T("全周", "the whole circle") : s.iv ? `${this.deg(s.iv[0]).toFixed(1)}° … ${this.deg(s.iv[1]).toFixed(1)}°` : s.nl === 0 ? api.T("够不着", "out of reach") : api.T("几段", "several arcs")]);
    if (q) {
      const P = this.pts(q.th, L), e = Math.hypot(P[3][0] - p[0], P[3][1] - p[1]);
      rows.push([["θ₁, θ₂, θ₃", "θ₁, θ₂, θ₃"], q.th.map((t) => this.deg(t).toFixed(1) + "°").join(", ")]);
      rows.push([["末端（指尖）离目标", "tip to goal"], (e * 1000).toExponential(1) + " mm"]);
      if (api.scene === "bell") rows.push([["肘部比肩高 / 最大值", "elbow above shoulder / maximum"], `${(L[0] * Math.sin(q.th[0])).toFixed(3)} m / ${s.hmax.toFixed(3)} m`]);
    } else rows.push([["当前 φ、分支", "current φ and branch"], api.T("无解", "no solution")]);
    if (api.scene === "arm") {
      const at = (x, y) => Math.abs(api.p.tx - x) < 1e-6 && Math.abs(api.p.ty - y) < 1e-6;
      if (s.lapDone && at(0.5, 0.3) && s.nl === 2 && api.p.br === 0 && (s.maxErr || 0) < 1e-9) api.done("loopA");
      if (s.lapDone && at(0.75, 0.1) && s.nl === 1 && s.minT2 < 0.5 && (s.maxErr || 0) < 1e-9) api.done("joinB");
      if (d < 0.2 && s.nl === 1) api.done("near");
      if (d > 0.917 && s.nl === 0) api.done("far");
    } else if (q && L[0] * Math.sin(q.th[0]) >= 0.98 * s.hmax) api.done("bell");
    if (s.path) rows.push([["沿流形走过的进度", "progress along the manifold"], Math.min(100, 100 * s.u / Math.max(1, s.path.length - 1)).toFixed(0) + "%"]);
    return rows;
  },
  draw(api, s) {
    const { w, h, ctx } = api, arm = api.scene === "arm", L = this.L(api), p = this.target(api);
    this.manifold(api, s);
    const sc = arm ? Math.min(w * 0.52 / 1.9, h * 0.8 / 1.6) : Math.min(w * 0.5 / 0.75, h * 0.8 / 0.8);
    const ox = arm ? w * 0.27 : w * 0.18, oy = arm ? h * 0.55 : h * 0.45, X = (q) => [ox + sc * q[0], oy - sc * q[1]];
    const R2 = L[0] + L[1], r1 = Math.abs(L[0] - L[1]);
    ctx.fillStyle = "rgba(31,111,235,0.06)"; ctx.beginPath(); ctx.arc(ox, oy, sc * R2, 0, 2 * Math.PI); ctx.arc(ox, oy, sc * r1, 0, 2 * Math.PI, true); ctx.fill();
    ctx.strokeStyle = api.css("--grid"); ctx.setLineDash([4, 4]); ctx.beginPath(); ctx.arc(ox, oy, sc * R2, 0, 2 * Math.PI); ctx.stroke();
    ctx.beginPath(); const G = X(p); ctx.arc(G[0], G[1], sc * L[2], 0, 2 * Math.PI); ctx.stroke(); ctx.setLineDash([]);
    if (arm) api.label(api.T("2R 圆环（腕点能到的范围）", "2R annulus (where the wrist can be)"), ox - sc * R2 * 0.7, oy - sc * R2 * 0.75, api.css("--muted"), 11);
    else {   // 人和门
      api.circle(ox - 18, oy - 50, 18, null, api.css("--muted")); api.line(ox - 18, oy - 30, ox - 18, oy + 110, api.css("--muted"), 4);
      api.rect(G[0] + 6, G[1] - 70, 10, 160, api.css("--line")); api.rect(G[0] + 2, G[1] - 7, 6, 14, api.css("--amber"));
      api.label(api.T("门铃", "bell"), G[0] + 22, G[1] - 20, api.css("--muted"), 12);
    }
    api.circle(G[0], G[1], 6, api.css("--red"));
    const q = this.pose(api, s);
    if (q) {
      const P = this.pts(q.th, L).map(X), col = q.br === 0 ? api.css("--blue") : api.css("--amber");
      for (let i = 0; i < 3; i++) api.line(P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], col, [10, 8, 5][i]);
      for (let i = 0; i < 3; i++) api.circle(P[i][0], P[i][1], 5, api.css("--panel"), api.css("--ink"));
      if (!arm) { api.line(ox - 30, P[1][1], ox + 30, P[1][1], api.css("--grid"), 1, [3, 3]); api.label(api.T("肘高", "elbow height"), ox + 34, P[1][1], api.css("--muted"), 11); }
    }
    api.rect(ox - 14, oy + 6, 28, 9, api.css("--muted"));
    // 右图：(θ₁, θ₂) 平面
    const g = api.graph({ x: w * 0.64, y: h * 0.08, w: w * 0.32, h: h * 0.72, xmin: -180, xmax: 180, ymin: -180, ymax: 180,
                          xlabel: "θ₁ / (°)", ylabel: "θ₂ / (°)" }).axes();
    g.dots(s.cloud[0], api.css("--blue"), 1.4); g.dots(s.cloud[1], api.css("--amber"), 1.4);
    if (q) g.dots([[this.deg(q.th[0]), this.deg(q.th[1])]], api.css("--red"), 5);
  },
});
