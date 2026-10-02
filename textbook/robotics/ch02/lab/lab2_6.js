// 实验 2.6 自运动与零空间（配 2.6 节）。平面 3R 臂 L = (0.425, 0.392, 0.1) m，末端固定在目标点；
// 给定 θ1，用 2R 逆解（θ3 < 0 的一支）求 θ2、θ3，使末端停在目标点。生活场景：手按桌面，肘部上下。
WQ.lab({
  title: ["实验 2.6 自运动与零空间", "Lab 2.6 Self-motion and the null space"],
  goal: ["在末端不动的前提下改变手臂的形态，读出雅可比矩阵的秩和零空间方向；看手臂伸直时秩怎样下降。",
         "Change the arm's shape while the tip stays put; read the rank of the Jacobian and the null-space direction; see the rank drop when the arm is straight."],
  scenes: [
    { id: "arm", robot: true, name: ["平面 3R 臂", "Planar 3R arm"], hide: ["sh"],
      problem: { title: ["机器人问题：末端不动，手臂还能动吗", "Robot problem: can the arm move while the tip stays?"],
                 text: ["三个关节，任务只要求末端的两个坐标：多出一个自由度。目标点在 55° 方向上，距基座 d。",
                        "Three joints, a task of two coordinates: one joint to spare. The target lies in the 55° direction at distance d from the base."] } },
    { id: "human", name: ["手按桌面", "Hand on the table"], hide: ["th1", "d"],
      problem: { title: ["生活中的例子：手不动，肘在动", "Everyday example: the hand stays, the elbow moves"],
                 text: ["肩在桌面上方 0.35 m；上臂 0.30 m、前臂 0.25 m、手 0.08 m；手按在离肩水平 0.5 m 处。转动肩部，肘部上下移动。",
                        "Shoulder 0.35 m above the table; upper arm 0.30 m, forearm 0.25 m, hand 0.08 m; the hand presses 0.5 m out. Turn the shoulder: the elbow moves up and down."] } },
  ],
  params: [
    { id: "th1", name: ["自运动：关节 1 的角 θ₁", "Self-motion: joint 1 angle θ₁"], min: 0, max: 90, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "d", name: ["目标点到基座的距离 d", "Target distance d"], min: 500, max: 917, step: 1, value: 797, unit: "mm", digits: 0 },
    { id: "sh", name: ["肩部的角", "Shoulder angle"], min: -80, max: 0, step: 1, value: -60, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "self", robot: true, text: ["把 θ₁ 调到 50°，确认末端偏差小于 0.1 mm。", "Set θ₁ to 50° and check that the tip error is below 0.1 mm."],
      demo: { scene: "arm", set: { d: 797, th1: 50 }, press: [] } },
    { id: "rank1", robot: true, text: ["把目标点移到手臂刚好伸直的位置，读出秩降为 1。", "Move the target to where the arm is just straight; the rank drops to 1."],
      demo: { scene: "arm", set: { d: 917, th1: 55 }, press: [] } },
    { id: "elbow", text: ["手按在桌上不动，把肘部抬到离桌面 0.20 m 以上。", "Keep the hand on the table and lift the elbow 0.20 m or more above it."],
      demo: { scene: "human", set: { sh: -30 }, press: [] } },
  ],
  think: ["θ₁ 能调的范围由什么决定？目标点越远，这个范围怎样变化？", "What limits the range of θ₁? How does it change as the target moves further away?"],

  dims(api) { return api.scene === "arm" ? { L: [0.425, 0.392, 0.1], base: [0, 0] } : { L: [0.30, 0.25, 0.08], base: [0, 0.35] }; },
  target(api) {
    if (api.scene === "human") return [0.5, 0];
    const a = 55 * Math.PI / 180, d = api.p.d / 1000; return [d * Math.cos(a), d * Math.sin(a)];
  },
  ik(api) {
    const { L, base } = this.dims(api), p = this.target(api), t1 = (api.scene === "arm" ? api.p.th1 : api.p.sh) * Math.PI / 180;
    const e = [base[0] + L[0] * Math.cos(t1), base[1] + L[0] * Math.sin(t1)], q = [p[0] - e[0], p[1] - e[1]];
    const c3 = (q[0] ** 2 + q[1] ** 2 - L[1] ** 2 - L[2] ** 2) / (2 * L[1] * L[2]);
    const reach = c3 <= 1 + 1e-9 && c3 >= -1 - 1e-9;
    const t3 = -Math.acos(Math.max(-1, Math.min(1, c3)));
    const a = Math.atan2(q[1], q[0]) - Math.atan2(L[2] * Math.sin(t3), L[1] + L[2] * Math.cos(t3));
    return { th: [t1, a - t1, t3], reach };
  },
  fk(th, L, base) {
    const pts = [base.slice()]; let a = 0;
    th.forEach((t, i) => { a += t; const q = pts[pts.length - 1]; pts.push([q[0] + L[i] * Math.cos(a), q[1] + L[i] * Math.sin(a)]); });
    return pts;
  },
  jac(pts) {   // 2×3：第 i 列 = 关节 i 指向末端的向量逆时针转 90°
    const tip = pts[3]; return [0, 1, 2].map((i) => [-(tip[1] - pts[i][1]), tip[0] - pts[i][0]]);
  },
  analyse(api) {
    const { L, base } = this.dims(api), r = this.ik(api), pts = this.fk(r.th, L, base), p = this.target(api);
    const cols = this.jac(pts), J = [[cols[0][0], cols[1][0], cols[2][0]], [cols[0][1], cols[1][1], cols[2][1]]];
    const g = [[0, 0], [0, 0]];   // J Jᵀ
    for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) g[i][j] = J[i][0] * J[j][0] + J[i][1] * J[j][1] + J[i][2] * J[j][2];
    const m = (g[0][0] + g[1][1]) / 2, rr = Math.hypot((g[0][0] - g[1][1]) / 2, g[0][1]);
    const s2 = Math.sqrt(Math.max(0, m - rr)), s1 = Math.sqrt(m + rr);
    let n = [J[0][1] * J[1][2] - J[0][2] * J[1][1], J[0][2] * J[1][0] - J[0][0] * J[1][2], J[0][0] * J[1][1] - J[0][1] * J[1][0]];
    const nn = Math.hypot(...n); n = nn > 1e-12 ? n.map((x) => x / nn) : null;
    return { r, pts, p, J, s1, s2, rank: s2 < 1e-6 * Math.max(1, s1) ? 1 : 2, n, err: Math.hypot(pts[3][0] - p[0], pts[3][1] - p[1]) };
  },
  reset(api, s) {},
  readouts(api, s) {
    const a = this.analyse(api), f = api.fmt, deg = (x) => f(x * 180 / Math.PI, 1);
    if (api.scene === "arm" && a.r.reach && Math.abs(api.p.th1 - 50) < 0.5 && a.err < 1e-4) api.done("self");
    if (api.scene === "arm" && a.r.reach && api.p.d >= 917 && a.rank === 1 && a.err < 1e-4) api.done("rank1");
    if (api.scene === "human" && a.r.reach && a.err < 1e-4 && a.pts[1][1] >= 0.2 - 1e-9) api.done("elbow");
    const rows = [[["关节角 θ", "joint angles θ"], a.r.reach ? `(${deg(a.r.th[0])}°, ${deg(a.r.th[1])}°, ${deg(a.r.th[2])}°)` : api.T("够不到", "out of reach")],
                  [["末端偏差", "tip error"], a.r.reach ? f(a.err * 1000, 4) + " mm" : "—"],
                  [["J 的秩", "rank of J"], String(a.rank)],
                  [["零空间方向 n", "null-space direction n"], a.rank === 2 && a.n ? `(${f(a.n[0], 3)}, ${f(a.n[1], 3)}, ${f(a.n[2], 3)})` : api.T("二维（秩为 1）", "two-dimensional (rank 1)")]];
    if (api.scene === "human") rows.push([["肘部离桌面的高度", "elbow height above the table"], f(a.pts[1][1], 3) + " m"]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, a = this.analyse(api), human = api.scene === "human";
    api.grid(w, h, 40);
    const k = human ? Math.min(w, h) * 1.3 : Math.min(w, h) * 0.85, ox = human ? w * 0.25 : w * 0.3, oy = human ? h * 0.85 : h * 0.9;
    const X = (p) => [ox + k * p[0], oy - k * p[1]];
    if (human) { api.line(0, oy, w, oy, api.css("--ground"), 3); api.rect(...X([-0.13, 0.42]), k * 0.1, k * 0.42, api.css("--muted"), null, 8);
      api.circle(...X([-0.08, 0.5]), k * 0.05, api.css("--muted"));
      api.label(api.T("桌面", "table"), w - 50, oy + 16, api.css("--muted"), 12); }
    const P = a.pts.map(X), tgt = X(a.p);
    if (!human) api.rect(P[0][0] - 18, P[0][1], 36, 12, api.css("--muted"), null, 3);
    api.circle(...tgt, 9, null, api.css("--amber"));
    if (!a.r.reach) api.label(api.T("够不到：换一个 θ₁", "out of reach: try another θ₁"), w / 2, 24, api.css("--red"), 14, "center");
    const ctx = api.ctx; ctx.lineCap = "round";
    [0, 1, 2].forEach((i) => api.line(...P[i], ...P[i + 1], human ? api.css("--orange") : api.css("--muted"), [12, 9, 6][i]));
    P.slice(0, 3).forEach((q) => api.circle(...q, 6, api.css("--panel"), api.css("--ink")));
    api.circle(...P[3], 4, api.css("--ink"));
    if (!human) api.label(api.T("目标点", "target"), tgt[0] + 12, tgt[1] - 12, api.css("--amber"), 13);
    if (a.n && a.rank === 2) {   // 零空间方向：三个关节速度的比例，画成三根柱
      const bx = w * 0.72, by = h * 0.3, bw = 26;
      api.label(api.T("零空间方向 n", "null-space direction n"), bx - 10, by - 70, api.css("--ink"), 13);
      a.n.forEach((v, i) => { api.rect(bx + i * (bw + 10), by - Math.max(0, v) * 60, bw, Math.abs(v) * 60, api.css("--accent"));
        api.label(`θ̇${["₁", "₂", "₃"][i]}`, bx + i * (bw + 10) + bw / 2, by + 70, api.css("--muted"), 12, "center"); });
      api.line(bx - 6, by, bx + 3 * (bw + 10), by, api.css("--ink"), 1);
    }
  },
});
