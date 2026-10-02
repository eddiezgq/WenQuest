// 实验 6.4 给定旋量，看刚体运动轨迹（配 6.4 节）。
// 场景一（UR5e）：拖动关节，程序按指数积公式算出法兰盘位姿 T(θ)，求位移 D = T M⁻¹ 的对数（定理 6.4.3），
//   画出螺旋轴；“沿螺旋轴演示”让一个坐标系按 e^{[S]θs} M（s: 0 → 1）从零位拧到当前位姿，留下螺旋线。
// 场景二（旋转楼梯）：给定螺旋轴（楼梯中心柱）、每圈上升的高度和转角，看人沿楼梯走过的螺旋线。
// 所有几何量都在 {s}（基座坐标系）中计算；画图的物体放在一个与 {s} 重合的组里（同实验 3.6 的做法）。
WQ.lab({
  title: ["实验 6.4 给定旋量，看刚体运动轨迹", "Lab 6.4 From a screw to a rigid-body path"],
  goal: ["用对数映射找出 UR5e 一次位移的螺旋轴，再用指数映射沿这根轴把法兰盘“拧”过去；理解任何刚体位移都是一个螺旋运动。",
         "Find the screw axis of a UR5e displacement with the log map, then screw the flange along it with the exp map; see that every rigid displacement is a screw motion."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 一次位移的螺旋轴", "Screw axis of a UR5e move"], hide: ["ang", "lead"],
      problem: { title: ["机器人问题：两个位姿之间最直接的运动", "Robot problem: the most direct motion between two poses"],
                 text: ["法兰盘从零位运动到当前位姿。由沙勒定理，这次位移是绕某根轴的螺旋运动。它是哪根轴？",
                        "The flange moves from home to the current pose. By Chasles' theorem the displacement is a screw motion. About which axis?"] } },
    { id: "stair", name: ["旋转楼梯", "A spiral staircase"], hide: ["j1", "j2", "j3", "j4", "j5", "j6"],
      problem: { title: ["生活中的例子：走旋转楼梯", "Everyday example: climbing a spiral staircase"],
                 text: ["楼梯绕中心柱盘旋而上。人沿楼梯走，就是绕中心柱的螺旋运动：轴是中心柱，节距由每圈上升的高度决定。",
                        "The stairs wind round a central post. Walking up them is a screw motion about the post; the pitch is set by the rise per turn."] } },
  ],
  params: [
    { id: "j1", name: ["关节 1 θ₁", "Joint 1 θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j2", name: ["关节 2 θ₂", "Joint 2 θ₂"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j3", name: ["关节 3 θ₃", "Joint 3 θ₃"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j4", name: ["关节 4 θ₄", "Joint 4 θ₄"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j5", name: ["关节 5 θ₅", "Joint 5 θ₅"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j6", name: ["关节 6 θ₆", "Joint 6 θ₆"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "ang", name: ["转过的角度", "Angle turned"], min: 0, max: 720, step: 15, value: 180, unit: "°", digits: 0 },
    { id: "lead", name: ["每圈上升", "Rise per turn"], min: 0.2, max: 0.8, step: 0.05, value: 0.4, unit: "m", digits: 2 },
  ],
  buttons: [{ id: "demo", name: ["沿螺旋轴演示", "Screw it along the axis"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["设置算例 6.4.2 的关节角 (30°, −45°, 60°, −15°, 90°, 30°)，读出转角和节距。", "Set Example 6.4.2, (30°, −45°, 60°, −15°, 90°, 30°), and read the angle and the pitch."],
      demo: { scene: "ur", set: { j1: 30, j2: -45, j3: 60, j4: -15, j5: 90, j6: 30 }, press: [], wait: 1 } },
    { id: "one", robot: true, text: ["只转动关节 1：节距为零，螺旋轴就是关节 1 的轴。", "Turn joint 1 only: the pitch is zero and the screw axis is joint 1's axis."],
      demo: { scene: "ur", set: { j1: 60, j2: 0, j3: 0, j4: 0, j5: 0, j6: 0 }, press: [], wait: 1 } },
    { id: "demo", robot: true, text: ["任取一组关节角，按“沿螺旋轴演示”：拧到终点的坐标系与法兰盘重合。", "Pick any joint angles and press “Screw it along the axis”: the frame ends exactly on the flange."],
      demo: { scene: "ur", set: { j1: 30, j2: -45, j3: 60, j4: -15, j5: 90, j6: 30 }, press: ["demo"], wait: 5 } },
    { id: "stair", text: ["旋转楼梯每圈上升 0.5 m，走两圈：上升 1 m。", "The stairs rise 0.5 m per turn; walk two turns and rise 1 m."],
      demo: { scene: "stair", set: { ang: 720, lead: 0.5 }, press: [], wait: 1 } },
  ],
  think: ["对数映射给出的转角总在 0 到 180° 之间。楼梯走了两圈，转角却是多少？“走了几圈”的信息到哪里去了？",
          "The log map always returns an angle between 0 and 180°. After two turns of the stairs, what angle does it give? Where did the number of turns go?"],

  // ---- 矩阵与旋量（与程序 6.4.1 相同的公式）
  m3(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  m4(A, B) { return A.map((r) => [0, 1, 2, 3].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j] + r[3] * B[3][j])); },
  sk(w) { return [[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]]; },
  exp6(S, t) {                      // 定理 6.4.1
    const w = S.slice(0, 3), v = S.slice(3), n = Math.hypot(...w);
    if (n < 1e-12) return [[1, 0, 0, v[0] * t], [0, 1, 0, v[1] * t], [0, 0, 1, v[2] * t], [0, 0, 0, 1]];
    const K = this.sk(w), K2 = this.m3(K, K), c = Math.cos(t), s = Math.sin(t);
    const R = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + s * K[i][j] + (1 - c) * K2[i][j]));
    const G = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? t : 0) + (1 - c) * K[i][j] + (t - s) * K2[i][j]));
    const p = [0, 1, 2].map((i) => G[i][0] * v[0] + G[i][1] * v[1] + G[i][2] * v[2]);
    return [[...R[0], p[0]], [...R[1], p[1]], [...R[2], p[2]], [0, 0, 0, 1]];
  },
  log6(T) {                         // 定理 6.4.3（θ 不接近 π 时）
    const R = T.slice(0, 3).map((r) => r.slice(0, 3)), p = [T[0][3], T[1][3], T[2][3]];
    const c = Math.max(-1, Math.min(1, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)), t = Math.acos(c);
    if (t < 1e-9) { const d = Math.hypot(...p); return d < 1e-12 ? { S: [0, 0, 0, 0, 0, 0], t: 0 } : { S: [0, 0, 0, p[0] / d, p[1] / d, p[2] / d], t: d }; }
    let w;
    if (Math.PI - t < 1e-6) { const B = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (R[i][j] + (i === j ? 1 : 0)) / 2)), k = [0, 1, 2].reduce((a, i) => (B[i][i] > B[a][a] ? i : a), 0), n = Math.sqrt(B[k][k]); w = [B[0][k] / n, B[1][k] / n, B[2][k] / n]; }
    else { const s2 = 2 * Math.sin(t); w = [(R[2][1] - R[1][2]) / s2, (R[0][2] - R[2][0]) / s2, (R[1][0] - R[0][1]) / s2]; }
    const K = this.sk(w), K2 = this.m3(K, K), a = 1 / t - 0.5 / Math.tan(t / 2);
    const Gi = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 / t : 0) - 0.5 * K[i][j] + a * K2[i][j]));
    return { S: [...w, ...[0, 1, 2].map((i) => Gi[i][0] * p[0] + Gi[i][1] * p[1] + Gi[i][2] * p[2])], t };
  },
  inv(T) { const Rt = [0, 1, 2].map((i) => [0, 1, 2].map((j) => T[j][i])), p = [T[0][3], T[1][3], T[2][3]];
    const q = Rt.map((r) => -(r[0] * p[0] + r[1] * p[1] + r[2] * p[2])); return [[...Rt[0], q[0]], [...Rt[1], q[1]], [...Rt[2], q[2]], [0, 0, 0, 1]]; },
  rev(w, q) { return [w[0], w[1], w[2], -(w[1] * q[2] - w[2] * q[1]), -(w[2] * q[0] - w[0] * q[2]), -(w[0] * q[1] - w[1] * q[0])]; },
  ur() {
    const H1 = 0.163, W1 = 0.138, L1 = 0.425, W2 = 0.131, L2 = 0.392, W3 = 0.127, H2 = 0.1, W4 = 0.1, yd = [0, -1, 0];
    const S = [this.rev([0, 0, 1], [0, 0, H1]), this.rev(yd, [0, -W1, H1]), this.rev(yd, [-L1, -W1 + W2, H1]), this.rev(yd, [-L1 - L2, -W1 + W2, H1]),
               this.rev([0, 0, -1], [-L1 - L2, -W1 + W2 - W3, H1]), this.rev(yd, [-L1 - L2, -W1 + W2 - W3, H1 - H2])];
    const M = [[1, 0, 0, -L1 - L2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]];
    return { S, M };
  },
  th(api) { const d = Math.PI / 180; return [api.p.j1, api.p.j2, api.p.j3, api.p.j4, api.p.j5, api.p.j6].map((x) => x * d); },
  screw(api) {                      // 当前位姿、位移 D 的对数和几何量
    const { S, M } = this.ur(), th = this.th(api);
    let T = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
    S.forEach((s, i) => { T = this.m4(T, this.exp6(s, th[i])); });
    T = this.m4(T, M);
    const D = this.m4(T, this.inv(M)), L = this.log6(D), w = L.S.slice(0, 3), v = L.S.slice(3);
    const rot = Math.hypot(...w) > 0.5;
    const q = rot ? [w[1] * v[2] - w[2] * v[1], w[2] * v[0] - w[0] * v[2], w[0] * v[1] - w[1] * v[0]] : [0, 0, 0];
    const h = rot ? w[0] * v[0] + w[1] * v[1] + w[2] * v[2] : Infinity;
    return { T, M, S: L.S, t: L.t, w, v, q, h, rot };
  },
  stair(api, a) {                   // 楼梯：轴为 {s} 的 z 轴，起点在 (0.55, 0, 0.05)；转 a（rad）后的位置
    const h = api.p.lead / (2 * Math.PI), r = 0.55;
    return [r * Math.cos(a), r * Math.sin(a), 0.05 + h * a];
  },

  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    arm.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    G.add(new T.AxesHelper(0.2));
    const line = (color, n) => { const g = new T.BufferGeometry(); g.setAttribute("position", new T.BufferAttribute(new Float32Array(n * 3), 3)); g.setDrawRange(0, 0);
      const l = new T.Line(g, new T.LineBasicMaterial({ color })); l.frustumCulled = false; G.add(l); return l; };
    keep.axis = line(0x1d2327, 2);
    keep.arrow = new T.ArrowHelper(new T.Vector3(0, 0, 1), new T.Vector3(), 0.2, 0x1d2327, 0.06, 0.035); G.add(keep.arrow);
    keep.path = line(0xd62728, 400);
    keep.ghost = new T.Group(); keep.ghost.matrixAutoUpdate = false; keep.ghost.add(new T.AxesHelper(0.14)); G.add(keep.ghost);
    keep.stairs = new T.Group(); G.add(keep.stairs);
    keep.post = new T.Mesh(new T.CylinderGeometry(0.04, 0.04, 1.6, 24), new T.MeshStandardMaterial({ color: 0x8a96a0 }));
    keep.post.rotation.x = Math.PI / 2; keep.post.position.set(0, 0, 0.8); keep.stairs.add(keep.post);
    keep.walker = new T.Mesh(new T.BoxGeometry(0.12, 0.08, 0.16), new T.MeshStandardMaterial({ color: 0x0969da })); keep.stairs.add(keep.walker);
    keep.steps = [];
    keep.lastKey = "";
  },
  setLine(l, pts) { const a = l.geometry.attributes.position; pts.forEach((p, i) => a.setXYZ(i, p[0], p[1], p[2])); a.needsUpdate = true; l.geometry.setDrawRange(0, pts.length); },
  buildSteps(api) {                 // 每 22.5° 一级台阶
    const k = api.keep, T = api.three;
    k.steps.forEach((m) => k.stairs.remove(m)); k.steps = [];
    const n = Math.round(720 / 22.5) + 1;
    for (let i = 0; i < n; i++) {
      const a = i * 22.5 * Math.PI / 180, p = this.stair(api, a);
      const m = new T.Mesh(new T.BoxGeometry(0.36, 0.12, 0.02), new T.MeshStandardMaterial({ color: 0xc9b48a, transparent: true, opacity: 0.85 }));
      m.position.set(0.39 * Math.cos(a), 0.39 * Math.sin(a), p[2] - 0.09); m.rotation.z = a; k.stairs.add(m); k.steps.push(m);
    }
  },
  reset(api, s) { s.anim = null; s.done = false; },
  action(id, api, s) { if (id === "demo" && api.scene === "ur") { s.anim = 0; s.done = false; api.t = 0; api.running = true; } },
  update(dt, api, s) {
    if (s.anim === null) return;
    s.anim = Math.min(1, s.anim + dt / 2);
    if (s.anim >= 1) { s.done = true; api.stop(); }
  },
  readouts(api, s) {
    const arm = api.m["B-ARM-UR5E"];
    if (!arm) return [];
    const f = (x, n) => api.fmt(x, n);
    if (api.scene === "stair") {
      const a = api.p.ang * Math.PI / 180, h = api.p.lead / (2 * Math.PI), rise = h * a;
      if (api.p.ang === 720 && Math.abs(api.p.lead - 0.5) < 1e-9) api.done("stair");
      return [[["旋量轴 S（中心柱，过原点、沿 z）", "screw axis S (the post, through 0 along z)"], `(0, 0, 1, 0, 0, ${f(h, 4)})`],
              [["节距 h = 每圈上升 / 2π", "pitch h = rise per turn / 2π"], f(h, 4) + " m/rad"],
              [["转角 θ", "angle θ"], f(a, 3) + " rad"], [["上升 hθ", "rise hθ"], f(rise, 3) + " m"]];
    }
    const g = this.screw(api), dg = 180 / Math.PI;
    const th = [api.p.j1, api.p.j2, api.p.j3, api.p.j4, api.p.j5, api.p.j6];
    if ([30, -45, 60, -15, 90, 30].every((x, i) => Math.abs(th[i] - x) < 0.5)) api.done("ex");
    if (th[0] !== 0 && th.slice(1).every((x) => x === 0) && g.rot && Math.abs(g.h) < 1e-9 && Math.abs(Math.abs(g.w[2]) - 1) < 1e-9 && Math.hypot(...g.q) < 1e-9) api.done("one");
    let gap = null;
    if (s.done) {
      const E = this.m4(this.exp6(g.S, g.t), g.M);
      gap = Math.hypot(E[0][3] - g.T[0][3], E[1][3] - g.T[1][3], E[2][3] - g.T[2][3]);
      if (gap < 1e-6 && th.some((x) => x !== 0)) api.done("demo");
    }
    const v3 = (a, n) => `(${a.map((x) => f(x, n)).join(", ")})`;
    const rows = [[["转角 θ", "angle θ"], f(g.t * dg, 2) + "°"],
                  [["节距 h", "pitch h"], g.rot ? f(g.h, 4) + " m/rad" : "∞"],
                  [["螺旋轴方向 ŝ", "axis direction ŝ"], v3(g.rot ? g.w : g.v, 3)],
                  [["轴上离原点最近的点 q", "point q nearest the origin"], v3(g.q, 3) + " m"]];
    if (gap !== null) rows.push([["演示终点与法兰盘之差", "end of screw vs flange"], gap.toExponential(1) + " m"]);
    return rows;
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep, T = api.three;
    const ur = api.scene === "ur";
    arm.holder.visible = ur; k.stairs.visible = !ur; k.ghost.visible = ur; k.axis.visible = true; k.arrow.visible = true;
    if (k.shown !== api.scene) { k.shown = api.scene; arm.holder.visible = true; if (ur) api.view(35, 22, 0.45, arm); else api.view(35, 14, 0.5, arm); arm.holder.visible = ur; }
    if (!ur) {
      const key = "st" + api.p.lead;
      if (k.lastKey !== key) { k.lastKey = key; this.buildSteps(api); }
      const a = api.p.ang * Math.PI / 180, p = this.stair(api, a);
      k.walker.position.set(p[0], p[1], p[2] + 0.08); k.walker.rotation.z = a;
      const pts = []; for (let i = 0; i <= 200; i++) pts.push(this.stair(api, a * i / 200));
      this.setLine(k.path, pts);
      this.setLine(k.axis, [[0, 0, 0], [0, 0, 1.6]]);
      k.arrow.position.set(0, 0, 1.55); k.arrow.setDirection(new T.Vector3(0, 0, 1));
      return;
    }
    arm.set({ shoulder_pan_joint: this.th(api)[0], shoulder_lift_joint: this.th(api)[1], elbow_joint: this.th(api)[2],
              wrist_1_joint: this.th(api)[3], wrist_2_joint: this.th(api)[4], wrist_3_joint: this.th(api)[5] });
    const g = this.screw(api);
    const dir = g.rot ? g.w : g.v;
    this.setLine(k.axis, [[g.q[0] - 0.8 * dir[0], g.q[1] - 0.8 * dir[1], g.q[2] - 0.8 * dir[2]], [g.q[0] + 0.8 * dir[0], g.q[1] + 0.8 * dir[1], g.q[2] + 0.8 * dir[2]]]);
    k.arrow.position.set(g.q[0] + 0.6 * dir[0], g.q[1] + 0.6 * dir[1], g.q[2] + 0.6 * dir[2]); k.arrow.setDirection(new T.Vector3(...dir));
    const u = s.anim === null ? 0 : s.anim, E = this.m4(this.exp6(g.S, g.t * u), g.M);
    k.ghost.matrix.set(E[0][0], E[0][1], E[0][2], E[0][3], E[1][0], E[1][1], E[1][2], E[1][3], E[2][0], E[2][1], E[2][2], E[2][3], 0, 0, 0, 1);
    k.ghost.matrixWorldNeedsUpdate = true;
    const pts = []; const n = Math.max(2, Math.round(120 * u));
    for (let i = 0; i <= n; i++) { const F = this.m4(this.exp6(g.S, g.t * u * i / n), g.M); pts.push([F[0][3], F[1][3], F[2][3]]); }
    this.setLine(k.path, s.anim === null ? [] : pts);
  },
});
