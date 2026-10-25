// 实验 27.4 摆手指，判断力封闭（配 27.4 节）。平面问题：物体的截面在纸面内，手指的接触点在截面轮廓上。
// 场景“夹零件”：60 mm × 40 mm 的矩形截面；生活场景“捏硬币”：Ø24 mm 的圆。接触点用轮廓上的弧长参数 s ∈ [0, 1) 表示：
//   矩形从左下角出发逆时针（下边 → 右边 → 上边 → 左边，周长 200 mm）；圆从最右点出发逆时针。
// 每个接触的摩擦锥用两条母线 n ± μt 表示（平面上的摩擦锥就是一个角）；μ = 0 时只有法向 n。
// 平面力旋量 w = (m_z/L, f_x, f_y)，力矩除以特征长度 L（矩形取 30 mm，圆取半径）。
// 力封闭 ⇔ 母线力旋量的凸包以原点为内点（定理 27.4.1 的等价形式），本页对 3 维凸包逐个三点组检查；
// 抓取质量 ε 为凸包内以原点为心的最大球的半径（式 (27.4.5)）。两指时另画出两点的连线，按定理 27.4.2 判断。
// 由 ex27_4.py 核算：上下两边各一个接触、μ = 0.2 时，错开 Δ ≤ μw = 8 mm 为力封闭。
WQ.lab({
  title: ["实验 27.4 摆手指，判断力封闭", "Lab 27.4 Place the fingers: force closure or not"],
  goal: ["在零件截面的轮廓上摆 2～4 个接触点，改变摩擦系数，看哪些摆法能抵抗任意方向的外力和外力矩，并比较抓取质量。",
         "Place 2–4 contacts on the outline of a part, change the friction coefficient, see which placements resist any external force and moment, and compare their grasp quality."],
  scenes: [
    { id: "part", robot: true, name: ["夹零件（矩形截面）", "Gripping a part (rectangular section)"],
      problem: { title: ["机器人问题：指尖放在哪里，零件才夹得牢", "Robot problem: where should the fingertips go for a secure grip"],
                 text: ["夹爪的指尖从上下两面夹住一个 60 mm × 40 mm 的零件。两个指尖错开多少就夹不牢了？没有摩擦时要几个指？",
                        "Fingertips grip a 60 mm × 40 mm part from above and below. How far apart can they be offset before the grip fails? How many fingers are needed without friction?"] } },
    { id: "coin", name: ["生活：捏硬币", "Everyday: pinching a coin"], params: { s1: { value: 0 }, s2: { value: 0.5 }, mu: { value: 0.4 } },
      problem: { title: ["生活中的例子：两根手指捏住一枚硬币", "Everyday example: pinching a coin between two fingers"],
                 text: ["拇指和食指相对时捏得住；如果两个手指不在一条直径上，摩擦够不够？",
                        "Thumb and forefinger opposite each other hold the coin. If they are not on one diameter, is friction enough?"] } },
  ],
  params: [
    { id: "n", name: ["接触点个数", "Number of contacts"], min: 2, max: 4, step: 1, value: 2, unit: "", digits: 0 },
    { id: "mu", name: ["摩擦系数 μ", "Friction coefficient μ"], min: 0, max: 0.8, step: 0.05, value: 0.2, unit: "", digits: 2 },
    { id: "s1", name: ["接触点 1 的位置 s₁", "Position s₁ of contact 1"], min: 0, max: 0.9975, step: 0.0025, value: 0.15, unit: "", digits: 4 },
    { id: "s2", name: ["接触点 2 的位置 s₂", "Position s₂ of contact 2"], min: 0, max: 0.9975, step: 0.0025, value: 0.65, unit: "", digits: 4 },
    { id: "s3", name: ["接触点 3 的位置 s₃", "Position s₃ of contact 3"], min: 0, max: 0.9975, step: 0.0025, value: 0.45, unit: "", digits: 4 },
    { id: "s4", name: ["接触点 4 的位置 s₄", "Position s₄ of contact 4"], min: 0, max: 0.9975, step: 0.0025, value: 0.95, unit: "", digits: 4 },
  ],
  buttons: [{ id: "reset", name: ["重画", "Redraw"] }],
  legend: [{ color: "#1f77b4", name: ["摩擦锥", "friction cone"] }, { color: "#2ca02c", name: ["力封闭", "force closure"] }, { color: "#d62728", name: ["不是力封闭", "no force closure"] }],
  W: 60, H: 40, R: 12,
  contact(api, s) {                               // 轮廓上的点、内法向、所在的边（矩形）
    if (api.scene === "coin") {
      const t = 2 * Math.PI * s;
      return { p: [this.R * Math.cos(t), this.R * Math.sin(t)], n: [-Math.cos(t), -Math.sin(t)], side: -1 };
    }
    const L = s * 200, W = this.W, H = this.H;
    if (L < 60) return { p: [L - W / 2, -H / 2], n: [0, 1], side: 0 };
    if (L < 100) return { p: [W / 2, L - 60 - H / 2], n: [-1, 0], side: 1 };
    if (L < 160) return { p: [W / 2 - (L - 100), H / 2], n: [0, -1], side: 2 };
    return { p: [-W / 2, H / 2 - (L - 160)], n: [1, 0], side: 3 };
  },
  contacts(api) { return [api.p.s1, api.p.s2, api.p.s3, api.p.s4].slice(0, Math.round(api.p.n)).map((s) => this.contact(api, s)); },
  wrenches(api, C) {
    const mu = api.p.mu, Lc = api.scene === "coin" ? this.R : 30, out = [];
    C.forEach(({ p, n }) => {
      const t = [-n[1], n[0]];
      (mu > 0 ? [1, -1] : [0]).forEach((sg) => {
        const f = [n[0] + sg * mu * t[0], n[1] + sg * mu * t[1]];
        out.push([(p[0] * f[1] - p[1] * f[0]) / Lc, f[0], f[1]]);
      });
    });
    return out;
  },
  closure(P) {                                    // 原点是否在凸包内部；ε = 原点到凸包各面的最小距离
    const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], cr = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    let faces = 0, eps = Infinity;
    for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) for (let k = j + 1; k < P.length; k++) {
      const nrm = cr(sub(P[j], P[i]), sub(P[k], P[i])), L = Math.hypot(...nrm);
      if (L < 1e-9) continue;
      const u = nrm.map((x) => x / L), c = dot(u, P[i]);
      let pos = 0, neg = 0;
      P.forEach((q) => { const v = dot(u, q) - c; if (v > 1e-9) pos++; else if (v < -1e-9) neg++; });
      if (!pos && !neg) return { fc: false, eps: 0 };   // 所有点共面：秩不足 3，凸包没有内部
      if (pos && neg) continue;                     // 不是凸包的面
      faces++;
      const side = pos ? 1 : -1, d0 = side * (0 - c);  // 原点在面的内侧时 d0 > 0
      eps = Math.min(eps, d0);
    }
    if (!faces) return { fc: false, eps: 0 };       // 点太少，没有面
    return { fc: eps > 1e-9, eps: Math.max(0, eps) };
  },
  reset(api, s) {
    const C = this.contacts(api), r = this.closure(this.wrenches(api, C));
    s.C = C; s.fc = r.fc; s.eps = r.eps;
    s.delta = null;
    if (api.scene === "part" && C.length === 2 && ((C[0].side === 0 && C[1].side === 2) || (C[0].side === 2 && C[1].side === 0)))
      s.delta = Math.abs(C[0].p[0] - C[1].p[0]);
    const mu = api.p.mu, n = C.length;
    if (api.scene === "part" && n === 2 && Math.abs(mu - 0.2) < 1e-9 && s.fc && s.delta !== null) api.done("anti");
    if (api.scene === "part" && n === 2 && Math.abs(mu - 0.2) < 1e-9 && !s.fc && s.delta !== null && s.delta >= 7.9 && s.delta <= 9.0) api.done("edge");
    if (api.scene === "part" && n === 4 && mu === 0 && s.fc) api.done("form");
  },
  draw(api, s) {
    const { ctx, w, h } = api, sc = Math.min(w, h) / (api.scene === "coin" ? 60 : 110), cx = w * 0.42, cy = h * 0.5;
    const X = (x) => cx + x * sc, Y = (y) => cy - y * sc;
    ctx.lineWidth = 2; ctx.strokeStyle = "#555"; ctx.fillStyle = "#d9dde1";
    ctx.beginPath();
    if (api.scene === "coin") ctx.arc(X(0), Y(0), this.R * sc, 0, 2 * Math.PI);
    else ctx.rect(X(-this.W / 2), Y(this.H / 2), this.W * sc, this.H * sc);
    ctx.fill(); ctx.stroke();
    const C = s.C || [], mu = api.p.mu, a = Math.atan(mu), Lc = 12;
    C.forEach(({ p, n }, i) => {
      ctx.fillStyle = "rgba(31,119,180,0.18)"; ctx.strokeStyle = "#1f77b4"; ctx.lineWidth = 1.5;
      const e = (sg) => [n[0] * Math.cos(a) - sg * n[1] * Math.sin(a), sg * n[0] * Math.sin(a) + n[1] * Math.cos(a)];
      const e1 = e(1), e2 = e(-1);
      ctx.beginPath(); ctx.moveTo(X(p[0]), Y(p[1])); ctx.lineTo(X(p[0] + Lc * e1[0]), Y(p[1] + Lc * e1[1])); ctx.lineTo(X(p[0] + Lc * e2[0]), Y(p[1] + Lc * e2[1])); ctx.closePath();
      ctx.fill(); ctx.stroke();
      // 指尖：从外面指向接触点的三角形
      const q = [p[0] - 6 * n[0], p[1] - 6 * n[1]], t = [-n[1], n[0]];
      ctx.fillStyle = "#4a5560"; ctx.beginPath();
      ctx.moveTo(X(p[0]), Y(p[1])); ctx.lineTo(X(q[0] + 3 * t[0]), Y(q[1] + 3 * t[1])); ctx.lineTo(X(q[0] - 3 * t[0]), Y(q[1] - 3 * t[1])); ctx.closePath(); ctx.fill();
      api.label(String(i + 1), X(q[0] - 3 * n[0]), Y(q[1] - 3 * n[1]), "#222", 13, "center");
    });
    if (C.length === 2) api.line(X(C[0].p[0]), Y(C[0].p[1]), X(C[1].p[0]), Y(C[1].p[1]), s.fc ? "#2ca02c" : "#d62728", 3, s.fc ? [] : [8, 6]);
    api.label(s.fc ? api.T(mu === 0 ? "形封闭 ✓" : "力封闭 ✓", mu === 0 ? "form closure ✓" : "force closure ✓") : api.T("不是力封闭 ✗", "no force closure ✗"),
      w * 0.80, h * 0.12, s.fc ? "#2ca02c" : "#d62728", 18, "center");
  },
  readouts(api, s) {
    const f = (v, k = 3) => api.fmt(v, k), C = s.C || [], mu = api.p.mu;
    return [
      [["结论", "Verdict"], s.fc ? api.T(mu === 0 ? "形封闭" : "力封闭", mu === 0 ? "form closure" : "force closure") : api.T("不是力封闭", "not force closure")],
      [["抓取质量 ε", "Grasp quality ε"], s.fc ? f(s.eps, 4) : "0"],
      [["摩擦锥半顶角 arctan μ", "Cone half-angle arctan μ"], f(Math.atan(mu) * 180 / Math.PI, 1) + "°"],
      [["上下两边的接触错开 Δ（两指时）", "Offset Δ of top and bottom contacts (two fingers)"], s.delta === null ? "—" : f(s.delta, 1) + " mm" + api.T(`（μw = ${f(mu * 40, 1)} mm）`, ` (μw = ${f(mu * 40, 1)} mm)`)],
      [["接触点（mm）", "Contacts (mm)"], C.map((c) => `(${f(c.p[0], 1)}, ${f(c.p[1], 1)})`).join(" ")],
    ];
  },
  tasks: [
    { id: "anti", robot: true, text: ["两个接触分别在上下两面、对径放置，μ = 0.2：力封闭。", "Two contacts on the top and bottom faces, opposite each other, μ = 0.2: force closure."],
      demo: { scene: "part", set: { n: 2, mu: 0.2, s1: 0.15, s2: 0.65 }, press: ["reset"], wait: 1 } },
    { id: "edge", robot: true, text: ["保持 μ = 0.2，把上面的接触点错开，找到刚好失去力封闭的位置（Δ 在 7.9～9 mm 之间），与 μw = 8 mm 比较。",
                                     "Keep μ = 0.2 and shift the top contact until force closure is just lost (Δ between 7.9 and 9 mm); compare with μw = 8 mm."],
      demo: { scene: "part", set: { n: 2, mu: 0.2, s1: 0.15, s2: 0.6925 }, press: ["reset"], wait: 1 } },
    { id: "form", robot: true, text: ["μ = 0（没有摩擦），摆 4 个接触点使零件形封闭。", "With μ = 0 (no friction), place 4 contacts so that the part is in form closure."],
      demo: { scene: "part", set: { n: 4, mu: 0, s1: 0.075, s2: 0.575, s3: 0.45, s4: 0.95 }, press: ["reset"], wait: 1 } },
  ],
  think: ["μ = 0 时，矩形零件用 4 个接触点就能形封闭，圆形硬币却用多少个都不行。为什么？这对夹圆棒、轴类零件的夹爪设计意味着什么？",
          "With μ = 0, four contacts put the rectangular part in form closure, but no number of contacts can do it for the round coin. Why? What does this mean for grippers that hold bars and shafts?"],
});
