// 实验 9.4 转动的复合：顺序不同，结果不同（配 9.4 节）。一块扁平的工件（1.6 × 1.0 × 0.4，顶面黄色、+x 端面红色），
// 先绕基座 x 轴转 α 再绕 z 轴转 β，矩阵为 Rz(β)Rx(α)；反过来是 Rx(α)Rz(β)。两者相差的角度 φ 由 cos φ = (tr(A₁ᵀA₂) − 1)/2 求出。
// 画法：正交投影，视线方位角 35°、仰角 22°；按面的深度从远到近填充。
WQ.lab({
  title: ["实验 9.4 转动的复合：顺序不同，结果不同", "Lab 9.4 Composing rotations: order matters"],
  goal: ["给定绕 x 轴、绕 z 轴的两个转角，比较两种顺序得到的姿态和矩阵；找出两种顺序结果相同或几乎相同的情形，理解矩阵乘法不可交换的几何意义。",
         "Given turns about the x and z axes, compare the poses and matrices from the two orders; find when the orders agree or nearly agree, and see what non-commuting matrix products mean geometrically."],
  scenes: [
    { id: "order", robot: true, name: ["两种顺序", "Two orders"],
      problem: { title: ["机器人问题：腕部先翻转再旋转，还是先旋转再翻转？", "Robot problem: flip then turn, or turn then flip?"],
                 text: ["机械臂抓起一块工件，程序要它“绕 x 轴翻 90°、绕 z 轴转 90°”。两步的先后会改变工件最后的朝向吗？左图先绕 x 后绕 z，右图先绕 z 后绕 x。",
                        "A robot picks up a part and is told to 'flip 90° about x and turn 90° about z'. Does the order change where the part ends up? Left: x first, then z; right: z first, then x."] } },
  ],
  params: [
    { id: "a", name: ["绕 x 轴的转角 α", "Turn about x, α"], min: -180, max: 180, step: 5, value: 90, unit: "°", digits: 0 },
    { id: "b", name: ["绕 z 轴的转角 β", "Turn about z, β"], min: -180, max: 180, step: 5, value: 90, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ninety", robot: true, text: ["取 α = β = 90°，读出两种顺序相差的角度，并写出两个矩阵。", "Set α = β = 90°; read the angle between the two results and write down both matrices."],
      demo: { scene: "order", set: { a: 90, b: 90 }, press: [], wait: 0.5 } },
    { id: "same", robot: true, text: ["找两个都不为零的转角，使两种顺序的结果完全相同（相差小于 0.01°）。", "Find two nonzero angles for which both orders give exactly the same result (difference below 0.01°)."],
      demo: { scene: "order", set: { a: 180, b: 180 }, press: [], wait: 0.5 } },
    { id: "small", robot: true, text: ["找两个不相等的非零转角，使两种顺序只相差 0.85°～0.9°；与 α、β（化为弧度）之积比较。", "Find two unequal nonzero angles for which the orders differ by only 0.85°–0.9°; compare with the product of α and β in radians."],
      demo: { scene: "order", set: { a: 10, b: 5 }, press: [], wait: 0.5 } },
  ],
  think: ["平面两连杆臂的姿态角为什么可以直接相加，与关节转动的先后无关？空间中的转动在什么情况下可交换？",
          "Why do the orientation angles of a planar two-link arm simply add, whatever the order? When do rotations in space commute?"],

  Rx(t) { const c = Math.cos(t), s = Math.sin(t); return [[1, 0, 0], [0, c, -s], [0, s, c]]; },
  Rz(t) { const c = Math.cos(t), s = Math.sin(t); return [[c, -s, 0], [s, c, 0], [0, 0, 1]]; },
  angle(A, B) {
    let t = 0;
    for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) t += A[i][j] * B[i][j];
    return Math.acos(Math.max(-1, Math.min(1, (t - 1) / 2))) * 180 / Math.PI;
  },
  mats(api) {
    const a = api.p.a * Math.PI / 180, b = api.p.b * Math.PI / 180, la = api.la;
    return { A1: la.mul(this.Rz(b), this.Rx(a)), A2: la.mul(this.Rx(a), this.Rz(b)) };
  },
  readouts(api) {
    const { A1, A2 } = this.mats(api), phi = this.angle(A1, A2), p = api.p;
    const ab = (p.a * Math.PI / 180) * (p.b * Math.PI / 180) * 180 / Math.PI;
    if (p.a === 90 && p.b === 90) api.done("ninety");
    if (p.a !== 0 && p.b !== 0 && phi < 0.01) api.done("same");
    if (p.a !== 0 && p.b !== 0 && Math.abs(p.a) !== Math.abs(p.b) && phi >= 0.85 && phi <= 0.9) api.done("small");
    return [[["先绕 x 后绕 z：A₁ = Rz(β)Rx(α)", "x first, then z: A₁ = Rz(β)Rx(α)"], api.la.str(A1, 2)],
            [["先绕 z 后绕 x：A₂ = Rx(α)Rz(β)", "z first, then x: A₂ = Rx(α)Rz(β)"], api.la.str(A2, 2)],
            [["两种顺序相差的角度", "Angle between the two results"], api.fmt(phi, 3) + "°"],
            [["α·β（弧度相乘，再化为度）", "α·β (radians multiplied, in degrees)"], api.fmt(ab, 3) + "°"]];
  },
  draw(api) {
    const { w, h } = api, c = api.ctx, { A1, A2 } = this.mats(api), la = api.la;
    const az = 35 * Math.PI / 180, el = 22 * Math.PI / 180;
    // view: x toward the viewer's lower left, z up
    const right = [-Math.sin(az), Math.cos(az), 0], up = [-Math.sin(el) * Math.cos(az), -Math.sin(el) * Math.sin(az), Math.cos(el)];
    const fwd = [Math.cos(el) * Math.cos(az), Math.cos(el) * Math.sin(az), Math.sin(el)];   // toward the viewer
    const dot = (u, v) => u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
    const s = Math.min(w / 2, h) * 0.28;
    const corners = [];
    for (const x of [-0.8, 0.8]) for (const y of [-0.5, 0.5]) for (const z of [-0.2, 0.2]) corners.push([x, y, z]);
    const faces = [{ k: [1, 3, 7, 5], n: [0, 0, 1], col: "rgba(232,180,0,0.9)" }, { k: [0, 4, 6, 2], n: [0, 0, -1], col: "rgba(200,200,205,0.9)" },
                   { k: [4, 5, 7, 6], n: [1, 0, 0], col: "rgba(214,60,50,0.9)" }, { k: [0, 2, 3, 1], n: [-1, 0, 0], col: "rgba(200,200,205,0.9)" },
                   { k: [2, 6, 7, 3], n: [0, 1, 0], col: "rgba(170,175,185,0.9)" }, { k: [0, 1, 5, 4], n: [0, -1, 0], col: "rgba(170,175,185,0.9)" }];
    const panel = (M, cx, title) => {
      const cy = h * 0.58, P = (p) => [cx + s * dot(p, right), cy - s * dot(p, up)];
      // base axes
      [[[1.4, 0, 0], api.css("--red"), "x"], [[0, 1.4, 0], api.css("--green"), "y"], [[0, 0, 1.2], api.css("--blue"), "z"]].forEach(([v, col, nm]) => {
        const e = P(v), o = P([0, 0, 0]);
        api.arrow(o[0], o[1], e[0], e[1], col, 2);
        api.label(nm, e[0] + 6, e[1] - 6, col, 13);
      });
      // ghost of the start pose
      faces.forEach((f) => {
        c.beginPath(); f.k.forEach((i, j) => { const q = P(corners[i]); if (j) c.lineTo(q[0], q[1]); else c.moveTo(q[0], q[1]); }); c.closePath();
        c.strokeStyle = "rgba(140,140,150,0.45)"; c.lineWidth = 1; c.setLineDash([4, 3]); c.stroke(); c.setLineDash([]);
      });
      const pts = corners.map((p) => la.mv(M, p));
      faces.map((f) => ({ f, d: dot(la.mv(M, f.n), fwd), z: f.k.reduce((t, i) => t + dot(pts[i], fwd), 0) }))
        .filter((o) => o.d > 1e-9).sort((a, b) => a.z - b.z)
        .forEach(({ f }) => {
          c.beginPath(); f.k.forEach((i, j) => { const q = P(pts[i]); if (j) c.lineTo(q[0], q[1]); else c.moveTo(q[0], q[1]); }); c.closePath();
          c.fillStyle = f.col; c.fill(); c.strokeStyle = api.css("--ink"); c.lineWidth = 1.2; c.stroke();
        });
      api.label(title, cx, 22, api.css("--ink"), 14, "center");
    };
    panel(A1, w * 0.25, api.T("先绕 x 后绕 z", "x first, then z"));
    panel(A2, w * 0.75, api.T("先绕 z 后绕 x", "z first, then x"));
    api.line(w * 0.5, 30, w * 0.5, h - 10, api.css("--line"), 1);
  },
});
