// 实验 5.4 搭建 UR5e 工作站的坐标系树（配 5.4 节）。零件库 UR5e 模型。
// 三维场景中，组 S 与机器人基座坐标系 {s} 重合（模型 root 节点；base 连杆相对它绕 z 转了 180°，不能用 base 的坐标系）。
// 工作台、相机、料盘、齿轮坯放在组 W 中，W 相对 S 的位姿为 T_sw = T_ws⁻¹，T_ws 由安装参数 (bx, by, yaw) 给出。
// 坐标系树：{w} 为根；{s}、{c} 挂在 {w} 下；{b} 挂在 {s} 下（T_sb(θ) 由第 12 章的指数积公式算出）；{t} 挂在 {b} 下；
// {o} 挂在 {c} 下（T_co = T_wc⁻¹ T_wo，代表相机的测量）。关节角 θ = (j1, j2, 90°, −90°, −90°, 0°)。
WQ.lab({
  title: ["实验 5.4 搭建 UR5e 工作站的坐标系树", "Lab 5.4 Building the frame tree of a UR5e workcell"],
  goal: ["给 UR5e 工作站的每个坐标系找到父坐标系，调整安装位置和关节角，任选两个坐标系，读出它们之间的路径和位姿；体会“只动一条边，只动一棵子树”。",
         "Give every frame of the UR5e workcell a parent, adjust the mounting and joint angles, pick any two frames and read the path and pose between them; see that moving one edge moves only one subtree."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "cell", robot: true, name: ["UR5e 工作站", "UR5e workcell"], hide: ["turn"],
      problem: { title: ["机器人问题：相机看到的夹爪在哪里？", "Robot problem: where does the camera see the gripper?"],
                 text: ["工作站有工作台 {w}、基座 {s}、法兰 {b}、工具 {t}、相机 {c}、齿轮坯 {o}。把它们挂成一棵树，就能求任意两者之间的位姿。",
                        "The workcell has the table {w}, base {s}, flange {b}, tool {t}, camera {c} and gear blank {o}. Hang them on a tree and any pose between two of them follows."] } },
    { id: "susan", name: ["餐桌转盘", "Lazy Susan"], hide: ["bx", "by", "yaw", "j1", "j2", "from", "to"],
      problem: { title: ["生活中的例子：转盘上的菜", "Everyday example: dishes on a turntable"],
                 text: ["餐桌 {d} 上有转盘 {p}，三盘菜挂在转盘上。转动转盘只改变一条边，所有菜一起转。把鱼（红盘）转到你面前。",
                        "The table {d} carries the turntable {p}; three dishes hang on the turntable. Turning it changes one edge and all dishes move. Bring the fish (red plate) in front of you."] } },
  ],
  params: [
    { id: "bx", name: ["基座安装 x", "Base mount x"], min: 0.1, max: 0.6, step: 0.05, value: 0.4, unit: "m", digits: 2 },
    { id: "by", name: ["基座安装 y", "Base mount y"], min: 0.1, max: 0.7, step: 0.05, value: 0.3, unit: "m", digits: 2 },
    { id: "yaw", name: ["基座安装转角", "Base mount yaw"], min: -180, max: 180, step: 15, value: 90, unit: "°", digits: 0 },
    { id: "j1", name: ["关节 1 θ₁", "Joint 1 θ₁"], min: -180, max: 180, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "j2", name: ["关节 2 θ₂", "Joint 2 θ₂"], min: -180, max: 0, step: 5, value: -90, unit: "°", digits: 0 },
    { id: "from", name: ["起点坐标系 0 w 1 s 2 b 3 t 4 c 5 o", "From frame 0 w 1 s 2 b 3 t 4 c 5 o"], min: 0, max: 5, step: 1, value: 0, unit: "", digits: 0 },
    { id: "to", name: ["终点坐标系 0 w 1 s 2 b 3 t 4 c 5 o", "To frame 0 w 1 s 2 b 3 t 4 c 5 o"], min: 0, max: 5, step: 1, value: 1, unit: "", digits: 0 },
    { id: "turn", name: ["转盘转角", "Turntable angle"], min: 0, max: 355, step: 5, value: 0, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "mount", robot: true, text: ["按算例 5.1.1 安装底座：(0.30, 0.40) m，转角 180°。", "Mount the base as in Example 5.1.1: (0.30, 0.40) m, yaw 180°."],
      demo: { scene: "cell", set: { bx: 0.3, by: 0.4, yaw: 180 }, press: [], wait: 1 } },
    { id: "ct", robot: true, text: ["在 θ₁ = 0、θ₂ = −90° 时选择 {c} → {t}，读出相机看到的工具位姿（与算例 5.4.2 比较）。", "With θ₁ = 0, θ₂ = −90°, pick {c} → {t} and read the tool pose seen by the camera (compare Example 5.4.2)."],
      demo: { scene: "cell", set: { bx: 0.3, by: 0.4, yaw: 180, j1: 0, j2: -90, from: 4, to: 3 }, press: [], wait: 1 } },
    { id: "sub", robot: true, text: ["把关节 1 转到 30°：T_wc 不变，T_ct 改变——只有关节 1 以下的子树移动。", "Turn joint 1 to 30°: T_wc stays, T_ct changes — only the subtree below joint 1 moves."],
      demo: { scene: "cell", set: { bx: 0.3, by: 0.4, yaw: 180, j2: -90, from: 4, to: 3, j1: 30 }, press: [], wait: 1 } },
    { id: "susan", text: ["转动转盘，把鱼（红盘）转到你面前（−y_d 方向）。", "Turn the table top so the fish (red plate) is in front of you (the −y_d direction)."],
      demo: { scene: "susan", set: { turn: 30 }, press: [], wait: 1 } },
  ],
  think: ["若把“相机看到的齿轮坯”既挂在 {c} 下，又按图纸挂在 {w} 下，树就有了回路。两条路算出的 T_wo 一般不会完全相同，应当怎样处理？",
          "If the gear blank hangs both under {c} (vision) and under {w} (drawing), the tree has a loop and the two T_wo will differ. What should be done?"],

  // ---------------------------------------------------------------- 4×4 矩阵（按行），与 code/_frames.py 相同的约定
  M: {
    mul(A, B) { const C = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];
      for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { let s = 0; for (let k = 0; k < 4; k++) s += A[i][k] * B[k][j]; C[i][j] = s; } return C; },
    inv(T) { const R = [[T[0][0], T[1][0], T[2][0]], [T[0][1], T[1][1], T[2][1]], [T[0][2], T[1][2], T[2][2]]];
      const p = [0, 1, 2].map((i) => -(R[i][0] * T[0][3] + R[i][1] * T[1][3] + R[i][2] * T[2][3]));
      return [[...R[0], p[0]], [...R[1], p[1]], [...R[2], p[2]], [0, 0, 0, 1]]; },
    rot(w, t) { const [x, y, z] = w, c = Math.cos(t), s = Math.sin(t), v = 1 - c;   // 罗德里格斯公式
      return [[c + x * x * v, x * y * v - z * s, x * z * v + y * s, 0], [y * x * v + z * s, c + y * y * v, y * z * v - x * s, 0],
              [z * x * v - y * s, z * y * v + x * s, c + z * z * v, 0], [0, 0, 0, 1]]; },
    tr(x, y, z) { return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]; },
    exp6(w, q, t) {   // 转动关节 e^{[S]θ} = [R, (I − R) q]（式 (12.1.2)）
      const R = this.rot(w, t), p = [0, 1, 2].map((i) => q[i] - (R[i][0] * q[0] + R[i][1] * q[1] + R[i][2] * q[2]));
      R[0][3] = p[0]; R[1][3] = p[1]; R[2][3] = p[2]; return R; },
  },
  AX: [[[0, 0, 1], [0, 0, 0.163]], [[0, -1, 0], [0, -0.138, 0.163]], [[0, -1, 0], [-0.425, -0.007, 0.163]],
       [[0, -1, 0], [-0.817, -0.007, 0.163]], [[0, 0, -1], [-0.817, -0.134, 0.163]], [[0, -1, 0], [-0.817, -0.134, 0.063]]],
  HOME: [[1, 0, 0, -0.817], [0, -1, 0, -0.234], [0, 0, -1, 0.063], [0, 0, 0, 1]],
  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  NAMES: ["w", "s", "b", "t", "c", "o"],
  theta(api) { const d = Math.PI / 180; return [api.p.j1 * d, api.p.j2 * d, 90 * d, -90 * d, -90 * d, 0]; },
  fk(th) { let T = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
    this.AX.forEach(([w, q], i) => { T = this.M.mul(T, this.M.exp6(w, q, th[i])); }); return this.M.mul(T, this.HOME); },
  Tws(api) { const T = this.M.rot([0, 0, 1], api.p.yaw * Math.PI / 180); T[0][3] = api.p.bx; T[1][3] = api.p.by; return T; },
  Twc() { const c = Math.cos(Math.PI / 12), s = Math.sin(Math.PI / 12); return [[0, c, -s, 1.05], [1, 0, 0, 0.4], [0, -s, -c, 0.9], [0, 0, 0, 1]]; },
  Two() { const T = this.M.rot([0, 0, 1], 25 * Math.PI / 180); T[0][3] = 0.8; T[1][3] = 0.45; T[2][3] = 0.02; return T; },
  Tbt() { return [[1, 0, 0, 0], [0, 0, 1, 0.15], [0, -1, 0, 0], [0, 0, 0, 1]]; },
  tree(api) {   // 每个坐标系：父坐标系与 T_父,子
    return { w: null, s: ["w", this.Tws(api)], b: ["s", this.fk(this.theta(api))], t: ["b", this.Tbt()], c: ["w", this.Twc()],
             o: ["c", this.M.mul(this.M.inv(this.Twc()), this.Two())] };
  },
  up(tr, f) { const out = [f]; while (tr[out[out.length - 1]]) out.push(tr[out[out.length - 1]][0]); return out; },
  path(tr, a, b) {   // 定理 5.4.1：先上到最近公共祖先，再下到 b
    const ua = this.up(tr, a), ub = this.up(tr, b), m = ua.find((x) => ub.includes(x));
    const steps = [];
    ua.slice(0, ua.indexOf(m)).forEach((x) => steps.push([x, tr[x][0], "up"]));
    ub.slice(0, ub.indexOf(m)).reverse().forEach((x) => steps.push([tr[x][0], x, "down"]));
    return steps;
  },
  rel(tr, a, b) { let T = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
    this.path(tr, a, b).forEach(([x, y, d]) => { T = this.M.mul(T, d === "down" ? tr[y][1] : this.M.inv(tr[x][1])); }); return T; },
  near(a, b) { return Math.abs(a - b) < 1e-6; },

  label(api, text, color) {
    const T = api.three, c = document.createElement("canvas");
    c.width = 128; c.height = 64;
    const g = c.getContext("2d");
    g.fillStyle = "rgba(255,255,255,0.85)"; g.fillRect(14, 8, 100, 48);
    g.fillStyle = color || "#1f2a33"; g.textAlign = "center"; g.textBaseline = "middle"; g.font = "bold 34px sans-serif"; g.fillText(text, 64, 33);
    const sp = new T.Sprite(new T.SpriteMaterial({ map: new T.CanvasTexture(c), depthTest: false }));
    sp.scale.set(0.12, 0.06, 1);
    return sp;
  },
  m4(T, A) { return new T.Matrix4().set(...A[0], ...A[1], ...A[2], ...A[3]); },
  frameObj(api, size, text, A, off) {
    const T = api.three, g = new T.Group();
    g.add(new T.AxesHelper(size));
    const sp = this.label(api, text); sp.position.set(...(off || [-0.03, -0.03, -0.04])); g.add(sp);
    if (A) { g.matrixAutoUpdate = false; g.matrix.copy(this.m4(T, A)); }
    return g;
  },
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    arm.root.updateMatrixWorld(true);
    const S = new T.Group(); S.matrixAutoUpdate = false; S.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(S); keep.S = S;
    keep.sAx = this.frameObj(api, 0.15, "{s}"); S.add(keep.sAx);
    const W = new T.Group(); W.matrixAutoUpdate = false; S.add(W); keep.W = W;
    const mat = (c, o) => new T.MeshStandardMaterial({ color: c, transparent: o < 1, opacity: o });
    const slab = new T.Mesh(new T.BoxGeometry(1.2, 0.8, 0.03), mat(0xc8ced3, 0.55)); slab.position.set(0.6, 0.4, -0.016); W.add(slab);
    const tray = new T.Mesh(new T.BoxGeometry(0.2, 0.16, 0.02), mat(0xe7d7a8, 1)); tray.position.set(0.8, 0.45, 0.01); W.add(tray);
    const part = new T.Mesh(new T.CylinderGeometry(0.04, 0.04, 0.03, 32), mat(0xb8860b, 1));
    part.rotation.x = Math.PI / 2; part.position.set(0.8, 0.45, 0.035); W.add(part);
    const pole = new T.Mesh(new T.BoxGeometry(0.03, 0.03, 0.98), mat(0x5b6b75, 1)); pole.position.set(1.17, 0.4, 0.49); W.add(pole);
    const arm2 = new T.Mesh(new T.BoxGeometry(0.15, 0.03, 0.03), mat(0x5b6b75, 1)); arm2.position.set(1.11, 0.4, 0.975); W.add(arm2);
    const cam = new T.Mesh(new T.BoxGeometry(0.06, 0.06, 0.06), mat(0x30363b, 1)); cam.position.set(1.05, 0.4, 0.92); W.add(cam);
    W.add(this.frameObj(api, 0.15, "{w}"));
    W.add(this.frameObj(api, 0.1, "{c}", this.Twc()));
    W.add(this.frameObj(api, 0.08, "{o}", this.Two()));
    const w3 = arm.nodes.wrist_3_link;
    const fb = this.frameObj(api, 0.08, "{b}", this.M.tr(0, 0.1, 0)); w3.add(fb);
    const ft = this.frameObj(api, 0.06, "{t}", this.M.mul(this.M.tr(0, 0.25, 0), this.M.rot([1, 0, 0], -Math.PI / 2))); w3.add(ft);
    const grip = new T.Mesh(new T.BoxGeometry(0.05, 0.15, 0.04), mat(0x5b6b75, 1)); grip.position.set(0, 0.175, 0); w3.add(grip);
    // 餐桌转盘（生活场景）：放在取景中心附近
    const SU = new T.Group(); SU.position.set(-0.35, -0.15, 0.25); S.add(SU); keep.SU = SU;
    const desk = new T.Mesh(new T.CylinderGeometry(0.55, 0.55, 0.03, 64), mat(0x8a6d2b, 1)); desk.rotation.x = Math.PI / 2; desk.position.z = -0.02; SU.add(desk);
    SU.add(this.frameObj(api, 0.2, "{d}"));
    const plate = new T.Group(); SU.add(plate); keep.plate = plate;
    const glass = new T.Mesh(new T.CylinderGeometry(0.33, 0.33, 0.012, 64), mat(0xdfe8ec, 0.8)); glass.rotation.x = Math.PI / 2; glass.position.z = 0.006; plate.add(glass);
    plate.add(this.frameObj(api, 0.14, "{p}", null, [0.08, 0.06, 0.05]));
    [[0, 0x2ca02c], [120, 0xd8c39a], [240, 0xd62728]].forEach(([a, col]) => {
      const d = new T.Mesh(new T.CylinderGeometry(0.07, 0.05, 0.03, 32), mat(col, 1)); d.rotation.x = Math.PI / 2;
      d.position.set(0.22 * Math.cos(a * Math.PI / 180), 0.22 * Math.sin(a * Math.PI / 180), 0.03); plate.add(d);
    });
    const you = this.label(api, api.T("你", "you"), "#d62728"); you.position.set(0, -0.68, 0.05); SU.add(you);
    const box = (f) => ({ entry: { robot: {} }, holder: { visible: false }, box: f });
    api.m.cellView = box(() => new T.Box3().setFromObject(W).union(arm.box()));
    api.m.susanView = box(() => new T.Box3().setFromObject(SU));
    keep.scene = "";
  },
  reset(api, s) {},
  readouts(api, s) {
    const arm = api.m["B-ARM-UR5E"];
    if (!arm) return [];
    if (api.scene === "susan") {
      const a = (240 + api.p.turn) * Math.PI / 180, x = 0.22 * Math.cos(a), y = 0.22 * Math.sin(a);
      if (Math.abs(x) < 1e-6 && y < 0) api.done("susan");
      return [[["T_dp：转盘相对餐桌绕 z 转", "T_dp: turntable about z of the table"], api.fmt(api.p.turn, 0) + "°"],
              [["鱼在转盘 {p} 中", "fish in {p}"], "(−0.110, −0.191) m"],
              [["鱼在餐桌 {d} 中 = T_dp · 鱼在 {p} 中", "fish in {d} = T_dp · fish in {p}"], `(${api.fmt(x, 3)}, ${api.fmt(y, 3)}) m`],
              [["鱼到“你”的距离", "fish to “you”"], api.fmt(Math.hypot(x, y + 0.68), 3) + " m"]];
    }
    const tr = this.tree(api), a = this.NAMES[api.p.from], b = this.NAMES[api.p.to];
    const Tab = this.rel(tr, a, b), steps = this.path(tr, a, b);
    const loop = this.M.mul(this.M.mul(this.rel(tr, "w", a), Tab), this.rel(tr, b, "w"));
    let err = 0; for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) err = Math.max(err, Math.abs(loop[i][j] - (i === j ? 1 : 0)));
    if (api.scene === "cell" && this.near(api.p.bx, 0.3) && this.near(api.p.by, 0.4) && this.near(Math.abs(api.p.yaw), 180)) api.done("mount");
    const mounted = this.near(api.p.bx, 0.3) && this.near(api.p.by, 0.4) && this.near(Math.abs(api.p.yaw), 180);
    if (api.scene === "cell" && mounted && a === "c" && b === "t" && this.near(api.p.j1, 0) && this.near(api.p.j2, -90)) api.done("ct");
    if (api.scene === "cell" && mounted && a === "c" && b === "t" && this.near(api.p.j1, 30) && this.near(api.p.j2, -90)) api.done("sub");
    const pathText = steps.length ? `{${a}} ` + steps.map(([x, y, d]) => (d === "up" ? "↑ " : "↓ ") + `{${y}}`).join(" ") : `{${a}}`;
    const row = (i) => `[${[0, 1, 2].map((j) => api.fmt(Tab[i][j], 3)).join("  ")} | ${api.fmt(Tab[i][3], 4)}]`;
    const Twc = this.Twc();
    return [
      [["路径（↑ 乘逆，↓ 乘边）", "path (↑ inverse, ↓ edge)"], pathText],
      [[`T_${a}${b} 第 1 行`, `T_${a}${b} row 1`], row(0)], [[`T_${a}${b} 第 2 行`, `T_${a}${b} row 2`], row(1)], [[`T_${a}${b} 第 3 行`, `T_${a}${b} row 3`], row(2)],
      [["回路检查 T_w·T_··T_·w 与 I 之差", "loop check: T_w· T_·· T_·w minus I"], err.toExponential(1)],
      [["T_wc 的位置（固定边）", "position of T_wc (fixed edge)"], `(${api.fmt(Twc[0][3], 3)}, ${api.fmt(Twc[1][3], 3)}, ${api.fmt(Twc[2][3], 3)}) m`],
    ];
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], T = api.three, keep = api.keep;
    const cell = api.scene === "cell";
    if (keep.scene !== api.scene) {
      keep.scene = api.scene;
      arm.nodes.base.visible = cell; keep.W.visible = cell; keep.SU.visible = !cell; keep.sAx.visible = cell;
      if (cell) { keep.W.updateMatrixWorld(true); api.view(35, 18, 1.4, api.m.cellView); } else api.view(0, 50, 1.25, api.m.susanView);
    }
    if (cell) {
      const th = this.theta(api), o = {};
      this.J.forEach((n, i) => { o[n] = th[i]; });
      arm.set(o);
      keep.W.matrix.copy(this.m4(T, this.M.inv(this.Tws(api))));
      keep.W.matrixWorldNeedsUpdate = true;
    } else keep.plate.rotation.z = api.p.turn * Math.PI / 180;
  },
});
