// 实验 13.2 逐个建立 UR5e 的连杆坐标系（配 13.2 节）。
// DH 表取零件库模型的尺寸（表 13.3.2，标准 DH，θ 偏置全为 0）：
//   (a, α, d) = (0, 90°, 0.163) (−0.425, 0, 0) (−0.392, 0, 0) (0, 90°, 0.134) (0, −90°, 0.1) (0, 0, 0.1)
// 坐标系 {0}…{6} 按 DH 正运动学算出，挂在模型的基座坐标系 {s} 上；“显示到第 k 个”逐个显示。
// 法兰盘中心算两遍：DH 的 {6} 原点，以及三维模型读数（模型 base 连杆绕 z 转了 180°，读数 (x, y, z) 换成 (−x, −y, z)）。
WQ.lab({
  title: ["实验 13.2 逐个建立 UR5e 的连杆坐标系", "Lab 13.2 Building the UR5e link frames one by one"],
  goal: ["在 UR5e 三维模型上逐个显示按标准 DH 建立的连杆坐标系，读出每一行 DH 参数，并验证 {6} 的原点就是法兰盘中心。",
         "Show the standard-DH link frames of the UR5e one at a time on the 3D model, read each DH row, and check that the origin of {6} is the flange centre."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 连杆坐标系", "UR5e link frames"],
      problem: { title: ["机器人问题：厂商的 DH 表是怎样量出来的", "Robot problem: how the maker's DH table is measured"],
                 text: ["按 13.2 节的步骤，从基座到法兰盘逐个建立 {0}…{6}。每建一个坐标系，就读出一行 a、α、d、θ。",
                        "Following Section 13.2, build {0}…{6} from the base to the flange. Each new frame gives one row a, α, d, θ."] } },
    { id: "lamp", name: ["只用关节 2、3、4（像台灯）", "Joints 2, 3, 4 only (like a desk lamp)"],
      problem: { title: ["生活中的例子：台灯的三个平行铰链", "Everyday example: the three parallel hinges of a desk lamp"],
                 text: ["关节 2、3、4 的轴互相平行，像台灯的三个铰链。平行轴的公垂线有无穷多条，DH 取 d = 0 的那一条，于是 {1}、{2}、{3} 的原点落在同一个竖直平面内。",
                        "Joints 2, 3, 4 have parallel axes, like the hinges of a desk lamp. Parallel axes have infinitely many common normals; DH takes the one with d = 0, so the origins of {1}, {2}, {3} lie in one vertical plane."] } },
  ],
  params: [
    { id: "k", name: ["显示到第 k 个坐标系", "Show frames up to k"], min: 0, max: 6, step: 1, value: 0, unit: "", digits: 0 },
    { id: "j1", name: ["关节 1 θ₁", "Joint 1 θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j2", name: ["关节 2 θ₂", "Joint 2 θ₂"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j3", name: ["关节 3 θ₃", "Joint 3 θ₃"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j4", name: ["关节 4 θ₄", "Joint 4 θ₄"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j5", name: ["关节 5 θ₅", "Joint 5 θ₅"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j6", name: ["关节 6 θ₆", "Joint 6 θ₆"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  tasks: [
    { id: "build", robot: true, text: ["零位下把 k 从 0 调到 6，逐个读出六行 DH 参数；确认 {6} 的原点就是法兰盘中心。", "At home step k from 0 to 6, read the six DH rows, and confirm that the origin of {6} is the flange centre."],
      demo: { scene: "ur", set: { k: 6, j1: 0, j2: 0, j3: 0, j4: 0, j5: 0, j6: 0 }, press: [], wait: 1 } },
    { id: "follow", robot: true, text: ["k = 6 时只转动关节 2：{0}、{1} 不动，{2}…{6} 跟着大臂转。说明 {i} 固定在哪个连杆上。", "With k = 6 turn only joint 2: {0} and {1} stay, {2}…{6} turn with the upper arm. Which link carries {i}?"],
      demo: { scene: "ur", set: { k: 6, j1: 0, j2: -45, j3: 0, j4: 0, j5: 0, j6: 0 }, press: [], wait: 1 } },
    { id: "ex", robot: true, text: ["设置算例 12.3.1 的关节角 (30°, −60°, 90°, −120°, −90°, 45°)：DH 的 {6} 原点与三维模型读出的法兰盘中心相差不到 10⁻⁶ m。", "Set Example 12.3.1, (30°, −60°, 90°, −120°, −90°, 45°): the DH origin of {6} and the model's flange centre agree to 10⁻⁶ m."],
      demo: { scene: "ur", set: { k: 6, j1: 30, j2: -60, j3: 90, j4: -120, j5: -90, j6: 45 }, press: [], wait: 1 } },
    { id: "lamp", text: ["场景“台灯”：k 取 3，任意转动关节 2、3、4 中的两个：{1}、{2}、{3} 的原点始终在 y = 0 的平面内。", "Scene “lamp”: with k = 3 turn two of joints 2, 3, 4: the origins of {1}, {2}, {3} stay in the plane y = 0."],
      demo: { scene: "lamp", set: { k: 3, j1: 0, j2: -60, j3: 50, j4: 30, j5: 0, j6: 0 }, press: [], wait: 1 } },
  ],
  think: ["{2} 和 {3} 的原点并不在关节 3、关节 4 的实物中心，而在 y = 0 的平面内。这会不会让正运动学算错？为什么？",
          "The origins of {2} and {3} are not at the centres of joints 3 and 4 but in the plane y = 0. Does this spoil the forward kinematics? Why not?"],

  TAB: [[0, Math.PI / 2, 0.163], [-0.425, 0, 0], [-0.392, 0, 0], [0, Math.PI / 2, 0.134], [0, -Math.PI / 2, 0.1], [0, 0, 0.1]],
  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  mul(A, B) { return A.map((r) => [0, 1, 2, 3].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j] + r[3] * B[3][j])); },
  // 标准 DH 一步：式 (13.1.5)
  sdh(a, al, d, th) {
    const ct = Math.cos(th), st = Math.sin(th), ca = Math.cos(al), sa = Math.sin(al);
    return [[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d], [0, 0, 0, 1]];
  },
  q(api) {
    const d = Math.PI / 180, lamp = api.scene === "lamp";
    return [lamp ? 0 : api.p.j1, api.p.j2, api.p.j3, api.p.j4, lamp ? 0 : api.p.j5, lamp ? 0 : api.p.j6].map((x) => x * d);
  },
  frames(api) {
    const q = this.q(api); let T = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]; const F = [T];
    this.TAB.forEach(([a, al, d], i) => { T = this.mul(T, this.sdh(a, al, d, q[i])); F.push(T); });
    return F;
  },
  flange(api) {
    const arm = api.m["B-ARM-UR5E"], q = this.q(api), o = {};
    this.J.forEach((n, i) => { o[n] = q[i]; }); arm.set(o);
    const [x, y, z] = arm.local("wrist_3_link", [0, 0.1, 0]);
    return [-x, -y, z];
  },

  setup3d(api, keep) {
    const T = api.three, root = api.m["B-ARM-UR5E"].nodes.root;
    keep.frames = [0, 1, 2, 3, 4, 5, 6].map(() => {
      const g = new T.Group(); g.matrixAutoUpdate = false;
      [[1, 0, 0, 0xd62728], [0, 1, 0, 0x2ca02c], [0, 0, 1, 0x1f77b4]].forEach(([x, y, z, c]) =>
        g.add(new T.ArrowHelper(new T.Vector3(x, y, z), new T.Vector3(), 0.09, c, 0.025, 0.014)));
      root.add(g); return g;
    });
    keep.viewed = false;
  },
  reset(api, s) {},
  readouts(api, s) {
    if (!api.m["B-ARM-UR5E"]) return [];
    const F = this.frames(api), k = api.p.k, f = this.flange(api), o6 = [F[6][0][3], F[6][1][3], F[6][2][3]];
    const gap = Math.hypot(o6[0] - f[0], o6[1] - f[1], o6[2] - f[2]), a = [api.p.j1, api.p.j2, api.p.j3, api.p.j4, api.p.j5, api.p.j6];
    const zero = a.every((v) => v === 0);
    if (api.scene === "ur" && k === 6 && zero && gap < 1e-6) api.done("build");
    if (api.scene === "ur" && k === 6 && a[1] !== 0 && a.every((v, i) => i === 1 || v === 0)) api.done("follow");
    const ex = [30, -60, 90, -120, -90, 45].every((v, i) => a[i] === v);
    if (api.scene === "ur" && k === 6 && ex && gap < 1e-6) api.done("ex");
    const moved = [a[1], a[2], a[3]].filter((v) => v !== 0).length;
    const flat = [1, 2, 3].every((i) => Math.abs(F[i][1][3]) < 1e-9);
    if (api.scene === "lamp" && k >= 3 && moved >= 2 && flat) api.done("lamp");
    const v = (p, n) => `(${api.fmt(p[0], n)}, ${api.fmt(p[1], n)}, ${api.fmt(p[2], n)})`;
    const rows = [];
    if (k >= 1) {
      const [aa, al, d] = this.TAB[k - 1], deg = (x) => api.fmt(x * 180 / Math.PI, 0) + "°";
      rows.push([[`第 ${k} 行 (a, α, d, θ)`, `row ${k} (a, α, d, θ)`], `(${api.fmt(aa, 3)} m, ${deg(al)}, ${api.fmt(d, 3)} m, θ${k} = ${deg(this.q(api)[k - 1])})`]);
    } else rows.push([["{0}", "{0}"], api.lang() === "en" ? "base frame: z₀ along axis 1" : "基座坐标系：z₀ 沿轴 1"]);
    rows.push([[`{${k}} 的原点（DH）`, `origin of {${k}} (DH)`], v([F[k][0][3], F[k][1][3], F[k][2][3]], 4) + " m"]);
    rows.push([[`{${k}} 的 z 轴`, `z axis of {${k}}`], v([F[k][0][2], F[k][1][2], F[k][2][2]], 3)]);
    rows.push([["法兰盘中心（三维模型）", "flange centre (3D model)"], v(f, 4) + " m"]);
    rows.push([["{6} 原点与模型之差", "{6} origin vs model"], gap.toExponential(1) + " m"]);
    return rows;
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"];
    this.flange(api);
    if (!api.keep.viewed) { api.keep.viewed = true; api.view(35, 22, 0.8, arm); }
    const F = this.frames(api), k = api.p.k;
    api.keep.frames.forEach((g, i) => {
      const M = F[i]; g.visible = i <= k;
      const sc = i === k ? 1.6 : 1;
      g.matrix.set(M[0][0] * sc, M[0][1] * sc, M[0][2] * sc, M[0][3], M[1][0] * sc, M[1][1] * sc, M[1][2] * sc, M[1][3],
                   M[2][0] * sc, M[2][1] * sc, M[2][2] * sc, M[2][3], 0, 0, 0, 1);
      g.matrixWorldNeedsUpdate = true;
    });
    arm.nodes.root.updateMatrixWorld(true);
  },
});
