// 实验 1.6 UR5e 末端沿向量移动（配 1.6.5 节）。UR5e（零件库 2026.10.9 版），起始姿态
// θ = (0, −60°, 90°, −120°, −90°, 0)；末端点取 wrist_3_link 坐标系原点。移动时末端姿态保持不变，
// 各关节角由程序沿直线一小步一小步求出（每步用伪逆做几次牛顿迭代，第 18、32 章）。
WQ.lab({
  title: ["实验 1.6 UR5e 末端沿向量移动", "Lab 1.6 Moving the UR5e tool along a vector"],
  goal: ["设定一个三维向量，让 UR5e 的末端沿它移动，读出起点、终点和移动的距离；体会“向量就是位移”，以及位移相加就是向量相加。",
         "Set a 3D vector and move the UR5e tool along it; read the start, the end and the distance moved. A vector is a displacement, and displacements add as vectors."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "robot", robot: true, name: ["UR5e 末端平移", "UR5e tool translation"],
      problem: { title: ["机器人问题：把零件向前送 10 cm", "Robot problem: push the part 10 cm forward"],
                 text: ["示教器上常有“沿基座 x 方向移动 10 mm”这样的按钮：末端沿一个向量平移，姿态不变。程序要自动算出六个关节各转多少。",
                        "A teach pendant has buttons such as 'move 10 mm along base x': the tool translates along a vector, orientation unchanged. The controller works out how far each of the six joints must turn."] } },
  ],
  params: [
    { id: "dx", name: ["向量的 x 分量", "x component"], min: -0.15, max: 0.15, step: 0.01, value: 0.1, unit: "m", digits: 2 },
    { id: "dy", name: ["向量的 y 分量", "y component"], min: -0.15, max: 0.15, step: 0.01, value: 0, unit: "m", digits: 2 },
    { id: "dz", name: ["向量的 z 分量", "z component"], min: -0.15, max: 0.15, step: 0.01, value: 0, unit: "m", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["沿向量移动", "Move along the vector"], primary: true }, { id: "home", name: ["回到起始姿态", "Back to the start pose"] }],
  tasks: [
    { id: "fwd", robot: true, text: ["让末端沿基座 x 方向（向外）移动 0.1 m。", "Move the tool 0.1 m along the base x axis (outwards)."],
      demo: { scene: "robot", set: { dx: 0.1, dy: 0, dz: 0 }, press: ["home", "start"], wait: 2 } },
    { id: "up", robot: true, text: ["让末端向上（z 方向）移动 0.05 m。", "Move the tool up (z) by 0.05 m."],
      demo: { scene: "robot", set: { dx: 0, dy: 0, dz: 0.05 }, press: ["home", "start"], wait: 2 } },
    { id: "dist", robot: true, text: ["沿向量 (0.1, 0.1, 0) m 移动，读出移动的距离，与 √(0.1² + 0.1²) 比较。", "Move along (0.1, 0.1, 0) m; compare the distance with √(0.1² + 0.1²)."],
      demo: { scene: "robot", set: { dx: 0.1, dy: 0.1, dz: 0 }, press: ["home", "start"], wait: 2 } },
    { id: "sum", robot: true, text: ["从起始姿态出发连续移动两次，确认总位移等于两个向量之和。", "From the start pose move twice; check the total displacement is the sum of the two vectors."],
      demo: { scene: "robot", set: { dx: 0.05, dy: -0.05, dz: 0.05 }, press: ["home", "start", "start"], wait: 2 } },
  ],
  think: ["分别沿 (0.01, 0, 0) m 和 (0.02, 0, 0) m 移动，各关节转角的改变量是否接近加倍？换成 (0.1, 0, 0) m 和 (0.2, 0, 0) m 呢？为什么？（提示：1.1.3 节的局部线性化。）",
          "Move along (0.01, 0, 0) m and (0.02, 0, 0) m: do the joint changes nearly double? And for (0.1, 0, 0) m and (0.2, 0, 0) m? Why? (Hint: local linearization, Section 1.1.3.)"],

  names: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  q0() { const d = Math.PI / 180; return [0, -60 * d, 90 * d, -120 * d, -90 * d, 0]; },
  pose(q) { const o = {}; this.names.forEach((n, i) => (o[n] = q[i])); return o; },
  // tool point p, tool axes R (columns), 6×6 Jacobian [angular; linear] in the base frame
  kin(api, q) {
    const arm = api.m["B-ARM-UR5E"];
    arm.set(this.pose(q));
    const p = arm.local("wrist_3_link", [0, 0, 0]);
    const ax = [[1, 0, 0], [0, 1, 0], [0, 0, 1]].map((e) => { const a = arm.local("wrist_3_link", e); return [a[0] - p[0], a[1] - p[1], a[2] - p[2]]; });
    const cols = this.names.map((n) => {
      const j = arm.joints[n], o = arm.local(j.child, [0, 0, 0]), e = arm.local(j.child, j.axis);
      const z = [e[0] - o[0], e[1] - o[1], e[2] - o[2]], r = [p[0] - o[0], p[1] - o[1], p[2] - o[2]];
      return [z[0], z[1], z[2], z[1] * r[2] - z[2] * r[1], z[2] * r[0] - z[0] * r[2], z[0] * r[1] - z[1] * r[0]];
    });
    return { p, ax, J: api.la.T(cols) };
  },
  // a few Newton steps towards tool point `target` with tool axes `ax0`
  solve(api, q, target, ax0) {
    for (let it = 0; it < 6; it++) {
      const k = this.kin(api, q);
      const ep = [0, 1, 2].map((i) => target[i] - k.p[i]);
      const er = [0, 0, 0];
      for (let c = 0; c < 3; c++) { const a = k.ax[c], b = ax0[c]; er[0] += 0.5 * (a[1] * b[2] - a[2] * b[1]); er[1] += 0.5 * (a[2] * b[0] - a[0] * b[2]); er[2] += 0.5 * (a[0] * b[1] - a[1] * b[0]); }
      if (Math.hypot(...ep) < 1e-7 && Math.hypot(...er) < 1e-7) break;
      const dq = api.la.mv(api.la.pinv(k.J), [...er, ...ep]);
      q = q.map((x, i) => x + dq[i]);
    }
    return q;
  },
  home(api) {
    const k = api.keep;
    k.q = this.q0(); k.moves = [];
    const s = this.kin(api, k.q); k.p0 = s.p; k.ax0 = s.ax;
    if (k.trace) k.trace.clear();
    if (k.arrow) k.arrow.visible = false;
  },
  setup3d(api, keep) {
    keep.trace = api.trace(0xe8913a);
    keep.arrow = new api.three.ArrowHelper(new api.three.Vector3(1, 0, 0), new api.three.Vector3(), 0.1, 0xd0342c, 0.03, 0.018);
    keep.arrow.visible = false;
    api.st.scene.add(keep.arrow);
    api.axes(api.m["B-ARM-UR5E"], "wrist_3_link", 0.08);
    this.home(api);
    api.view(35, 20, 0.95);
  },
  action(id, api, s) { if (id === "home") { this.home(api); s.path = null; } },
  start(api, s) {   // compute the whole straight-line path now; update() only plays it back
    const k = api.keep, d = [api.p.dx, api.p.dy, api.p.dz];
    if (Math.hypot(...d) < 1e-9) { api.stop(); return; }
    const from = this.kin(api, k.q).p, N = 40, path = [k.q.slice()];
    let q = k.q.slice();
    for (let i = 1; i <= N; i++) { q = this.solve(api, q, from.map((x, j) => x + d[j] * i / N), k.ax0); path.push(q.slice()); }
    const to = this.kin(api, q).p;
    s.path = path; s.from = from; s.to = to; s.d = d;
    k.q = q; k.moves.push({ d, real: to.map((x, j) => x - from[j]) });
    const arm = api.m["B-ARM-UR5E"];
    arm.set(this.pose(path[0])); const w0 = arm.point("wrist_3_link");
    arm.set(this.pose(q)); const w1 = arm.point("wrist_3_link");
    const v = w1.clone().sub(w0), L = v.length();
    if (L > 1e-6) { k.arrow.position.copy(w0); k.arrow.setDirection(v.normalize()); k.arrow.setLength(L, Math.min(0.03, 0.3 * L), Math.min(0.018, 0.18 * L)); k.arrow.visible = true; }
  },
  update(dt, api, s) {
    if (!s.path) { api.stop(); return; }
    if (api.t > 1.2) api.stop();
  },
  readouts(api, s) {
    const k = api.keep;
    if (!k || !k.q) return [];
    const v3 = (a) => api.la.vstr(a, 4) + " m";
    const now = this.kin(api, k.q).p, tot = now.map((x, j) => x - k.p0[j]);
    const sum = [0, 1, 2].map((j) => k.moves.reduce((t, m) => t + m.d[j], 0));
    const last = k.moves[k.moves.length - 1];
    if (last && k.moves.length === 1) {
      const e = Math.hypot(...last.real.map((x, j) => x - last.d[j]));
      const is = (a, b, c) => Math.abs(last.d[0] - a) < 1e-6 && Math.abs(last.d[1] - b) < 1e-6 && Math.abs(last.d[2] - c) < 1e-6 && e < 1e-4;
      if (is(0.1, 0, 0)) api.done("fwd");
      if (is(0, 0, 0.05)) api.done("up");
      if (is(0.1, 0.1, 0)) api.done("dist");
    }
    if (k.moves.length >= 2 && Math.hypot(...tot.map((x, j) => x - sum[j])) < 1e-4) api.done("sum");
    const rows = [[["起始点（基座坐标系）", "Start point (base frame)"], v3(k.p0)],
                  [["当前末端位置", "Current tool position"], v3(now)]];
    if (last) {
      rows.push([["上一次移动：设定的向量", "Last move: vector set"], v3(last.d)]);
      rows.push([["上一次移动：实际位移", "Last move: actual displacement"], v3(last.real)]);
      rows.push([["上一次移动的距离", "Distance of the last move"], api.fmt(Math.hypot(...last.real), 4) + " m"]);
    }
    rows.push([["移动次数 / 各向量之和", "Moves / sum of the vectors"], k.moves.length + " / " + v3(sum)]);
    rows.push([["从起始点算起的总位移", "Total displacement from the start"], v3(tot)]);
    rows.push([["关节角 θ₁ … θ₆ / °", "Joint angles θ₁ … θ₆ / °"], k.q.map((x) => api.fmt(x * 180 / Math.PI, 1)).join(", ")]);
    return rows;
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep;
    if (!arm || !k.q) return;
    let q = k.q;
    if (s.path && api.running) {
      const u = Math.min(1, api.t / 1.2), f = u * (s.path.length - 1), i = Math.min(s.path.length - 2, Math.floor(f)), a = f - i;
      q = s.path[i].map((x, j) => x + a * (s.path[i + 1][j] - x));
    }
    arm.set(this.pose(q));
    if (api.running && k.trace) k.trace.add(arm.point("wrist_3_link"));
  },
});
