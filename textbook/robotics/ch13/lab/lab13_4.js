// 实验 13.4 同一台机器人，两种方法（配 13.4 节）。
// 末端位置算三遍：(1) 指数积，旋量轴取第 12 章表 12.1.1（UR5e）或由 Franka 的 Craig 表按推论 13.4.1 换算（Panda）；
// (2) DH 连乘：UR5e 用标准 DH（“表”= 0 时为零件库尺寸，表 13.4.2；= 1 时为 UR 公布的表 13.3.1），Panda 用 Craig 的改进 DH（表 13.4.3）；
// (3) 三维模型读数（三维引擎按模型文件的连杆矩阵累乘）。UR5e 模型 base 连杆绕 z 转了 180°，读数 (x, y, z) 换成 (−x, −y, z)。
WQ.lab({
  title: ["实验 13.4 同一台机器人，两种方法", "Lab 13.4 One robot, two methods"],
  goal: ["对 UR5e 和 Panda 分别用 DH 连乘和指数积计算末端位置，并与三维模型的读数互相核对；再换用厂商参数，看差别从哪里来。",
         "Compute the tool position of the UR5e and the Panda both by DH products and by the PoE formula, check them against the 3D model, then switch to the maker's parameters and see where the difference comes from."],
  view: "3d",
  models: ["B-ARM-UR5E", "B-ARM-PANDA"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e：标准 DH 与指数积", "UR5e: standard DH and PoE"],
      problem: { title: ["机器人问题：两套软件算出的末端对不上", "Robot problem: two programs disagree on the tool position"],
                 text: ["控制器用 DH 表，仿真软件用旋量轴。先确认两种方法本身给出同一个答案，再查参数是否相同。",
                        "The controller uses a DH table, the simulator uses screw axes. First check that the two methods agree, then check whether the parameters are the same."] } },
    { id: "panda", robot: true, name: ["Panda：Craig 表与指数积", "Panda: Craig table and PoE"],
      problem: { title: ["机器人问题：Franka 手册的 Craig 表", "Robot problem: the Craig table in the Franka manual"],
                 text: ["Franka 按 Craig 的改进 DH 公布参数。按推论 13.4.1 把它换成旋量轴，与改进 DH 连乘、与三维模型比较。",
                        "Franka publishes modified (Craig) DH parameters. Convert them to screw axes by Corollary 13.4.1 and compare with the modified-DH product and the 3D model."] } },
    { id: "lamp", name: ["台灯：卷尺与铰链", "Desk lamp: tape measure and hinges"],
      problem: { title: ["生活中的例子：两种方法描述同一盏台灯", "Everyday example: two ways to describe one desk lamp"],
                 text: ["只用 UR5e 的关节 2、3、4，它们像台灯的三个平行铰链。DH 是“沿着灯臂一段一段量”，指数积是“在桌面坐标里标出每个铰链轴”。两种记法应给出同一个灯罩位置。",
                        "Use only joints 2, 3, 4 of the UR5e, like the three parallel hinges of a lamp. DH measures along the arm piece by piece; PoE marks each hinge axis in desk coordinates. Both must put the shade in the same place."] } },
  ],
  params: [
    { id: "j1", name: ["关节 1 θ₁", "Joint 1 θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j2", name: ["关节 2 θ₂", "Joint 2 θ₂"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j3", name: ["关节 3 θ₃", "Joint 3 θ₃"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j4", name: ["关节 4 θ₄", "Joint 4 θ₄"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j5", name: ["关节 5 θ₅", "Joint 5 θ₅"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j6", name: ["关节 6 θ₆", "Joint 6 θ₆"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j7", name: ["关节 7 θ₇（Panda）", "Joint 7 θ₇ (Panda)"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "tbl", name: ["UR5e 的 DH 表：0 零件库尺寸 / 1 厂商表", "UR5e DH table: 0 library model / 1 maker's table"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "ur_ex", robot: true, text: ["UR5e，表取 0，设置算例 12.3.1 的关节角 (30°, −60°, 90°, −120°, −90°, 45°)：DH、指数积、三维模型三者一致。", "UR5e, table 0, Example 12.3.1 (30°, −60°, 90°, −120°, −90°, 45°): DH, PoE and the 3D model agree."],
      demo: { scene: "ur", set: { j1: 30, j2: -60, j3: 90, j4: -120, j5: -90, j6: 45, j7: 0, tbl: 0 }, press: [], wait: 1 } },
    { id: "ur_vendor", robot: true, text: ["同一组关节角，表改为 1（厂商表）：DH 与指数积相差约 0.7 mm。用定理 13.3.1 解释。", "Same angles, table 1 (maker's): DH and PoE now differ by about 0.7 mm. Explain with Theorem 13.3.1."],
      demo: { scene: "ur", set: { j1: 30, j2: -60, j3: 90, j4: -120, j5: -90, j6: 45, j7: 0, tbl: 1 }, press: [], wait: 1 } },
    { id: "panda", robot: true, text: ["Panda：任意转动至少三个关节，Craig 表的 DH 连乘、换算出的指数积和三维模型三者之差都在 10⁻⁶ m 以下。", "Panda: turn at least three joints anyhow; the Craig-table product, the converted PoE and the 3D model agree to 10⁻⁶ m."],
      demo: { scene: "panda", set: { j1: 20, j2: -40, j3: 30, j4: -100, j5: 15, j6: 90, j7: 45, tbl: 0 }, press: [], wait: 1 } },
    { id: "lamp", text: ["台灯：转动关节 2、3、4 中的至少两个，DH 与指数积给出同一个灯罩位置。", "Lamp: turn at least two of joints 2, 3, 4; DH and PoE put the shade in the same place."],
      demo: { scene: "lamp", set: { j1: 0, j2: -70, j3: 60, j4: 40, j5: 0, j6: 0, j7: 0, tbl: 0 }, press: [], wait: 1 } },
  ],
  think: ["换用厂商表以后，差值随关节角变化，但从不超过 2.1 mm。这个上界是怎样得到的？为什么实际上达不到它？",
          "With the maker's table the gap changes with the joint angles but never exceeds 2.1 mm. Where does this bound come from, and why is it never reached?"],

  mul(A, B) { return A.map((r) => [0, 1, 2, 3].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j] + r[3] * B[3][j])); },
  m3(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  sdh(a, al, d, th) {   // 式 (13.1.5)
    const ct = Math.cos(th), st = Math.sin(th), ca = Math.cos(al), sa = Math.sin(al);
    return [[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d], [0, 0, 0, 1]];
  },
  mdh(a, al, d, th) {   // 式 (13.1.8)
    const ct = Math.cos(th), st = Math.sin(th), ca = Math.cos(al), sa = Math.sin(al);
    return [[ct, -st, 0, a], [st * ca, ct * ca, -sa, -sa * d], [st * sa, ct * sa, ca, ca * d], [0, 0, 0, 1]];
  },
  exp6(S, t) {          // 式 (12.1.5)
    const [wx, wy, wz, vx, vy, vz] = S;
    const K = [[0, -wz, wy], [wz, 0, -wx], [-wy, wx, 0]], K2 = this.m3(K, K), c = Math.cos(t), s = Math.sin(t);
    const R = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + s * K[i][j] + (1 - c) * K2[i][j]));
    const G = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? t : 0) + (1 - c) * K[i][j] + (t - s) * K2[i][j]));
    const p = [0, 1, 2].map((i) => G[i][0] * vx + G[i][1] * vy + G[i][2] * vz);
    return [[...R[0], p[0]], [...R[1], p[1]], [...R[2], p[2]], [0, 0, 0, 1]];
  },
  rev(w, q) { return [w[0], w[1], w[2], -(w[1] * q[2] - w[2] * q[1]), -(w[2] * q[0] - w[0] * q[2]), -(w[0] * q[1] - w[1] * q[0])]; },
  I4() { return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]; },
  // UR5e：表 12.1.1 的旋量轴与 M；零件库尺寸的 DH 表（表 13.4.2）与厂商表（表 13.3.1）
  urPoe() {
    const H1 = 0.163, W1 = 0.138, L1 = 0.425, W2 = 0.131, L2 = 0.392, W3 = 0.127, H2 = 0.1, W4 = 0.1, yd = [0, -1, 0];
    const S = [this.rev([0, 0, 1], [0, 0, H1]), this.rev(yd, [0, -W1, H1]), this.rev(yd, [-L1, -W1 + W2, H1]), this.rev(yd, [-L1 - L2, -W1 + W2, H1]),
               this.rev([0, 0, -1], [-L1 - L2, -W1 + W2 - W3, H1]), this.rev(yd, [-L1 - L2, -W1 + W2 - W3, H1 - H2])];
    return { S, M: [[1, 0, 0, -L1 - L2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]] };
  },
  URM: [[0, Math.PI / 2, 0.163], [-0.425, 0, 0], [-0.392, 0, 0], [0, Math.PI / 2, 0.134], [0, -Math.PI / 2, 0.1], [0, 0, 0.1]],
  URV: [[0, Math.PI / 2, 0.1625], [-0.425, 0, 0], [-0.3922, 0, 0], [0, Math.PI / 2, 0.1333], [0, -Math.PI / 2, 0.0997], [0, 0, 0.0996]],
  // Panda：Franka 的 Craig 表 (a_{i-1}, α_{i-1}, d_i)，法兰 d = 0.107 m
  FR: [[0, 0, 0.333], [0, -Math.PI / 2, 0], [0, Math.PI / 2, 0.316], [0.0825, Math.PI / 2, 0], [-0.0825, -Math.PI / 2, 0.384], [0, Math.PI / 2, 0], [0.088, Math.PI / 2, 0]],
  q(api) {
    const d = Math.PI / 180, p = api.p;
    if (api.scene === "lamp") return [0, p.j2, p.j3, p.j4, 0, 0].map((x) => x * d);
    if (api.scene === "panda") return [p.j1, p.j2, p.j3, p.j4, p.j5, p.j6, p.j7].map((x) => x * d);
    return [p.j1, p.j2, p.j3, p.j4, p.j5, p.j6].map((x) => x * d);
  },
  pos(T) { return [T[0][3], T[1][3], T[2][3]]; },
  dhTip(api) {
    const q = this.q(api); let T = this.I4();
    if (api.scene === "panda") { this.FR.forEach(([a, al, d], i) => { T = this.mul(T, this.mdh(a, al, d, q[i])); }); return this.mul(T, this.mdh(0, 0, 0.107, 0)); }
    const tab = api.scene === "ur" && api.p.tbl === 1 ? this.URV : this.URM;
    tab.forEach(([a, al, d], i) => { T = this.mul(T, this.sdh(a, al, d, q[i])); });
    return T;
  },
  poeTip(api) {
    const q = this.q(api); let T = this.I4(), S, M;
    if (api.scene === "panda") {   // 推论 13.4.1：S_i = [Ad_{T_0i(0)}](0,0,1,0,0,0)，即 {i} 在零位时的 z 轴
      S = []; let F = this.I4();
      this.FR.forEach(([a, al, d]) => { F = this.mul(F, this.mdh(a, al, d, 0)); S.push(this.rev([F[0][2], F[1][2], F[2][2]], [F[0][3], F[1][3], F[2][3]])); });
      M = this.mul(F, this.mdh(0, 0, 0.107, 0));
    } else ({ S, M } = this.urPoe());
    S.forEach((s, i) => { T = this.mul(T, this.exp6(s, q[i])); });
    return this.mul(T, M);
  },
  modelTip(api) {
    const q = this.q(api);
    if (api.scene === "panda") {
      const pa = api.m["B-ARM-PANDA"], o = {}; q.forEach((x, i) => { o[`joint${i + 1}`] = x; }); pa.set(o);
      return pa.local("link7", [0, 0, 0.107]);
    }
    const ur = api.m["B-ARM-UR5E"], names = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"], o = {};
    names.forEach((n, i) => { o[n] = q[i]; }); ur.set(o);
    const [x, y, z] = ur.local("wrist_3_link", [0, 0.1, 0]);
    return [-x, -y, z];
  },

  setup3d(api, keep) {
    keep.shown = null;
    api.m["B-ARM-UR5E"].nodes.root.add(new api.three.AxesHelper(0.2));
    api.m["B-ARM-PANDA"].nodes.root.add(new api.three.AxesHelper(0.2));
  },
  reset(api, s) {},
  readouts(api, s) {
    if (!api.m["B-ARM-UR5E"] || !api.m["B-ARM-PANDA"]) return [];
    const a = this.pos(this.dhTip(api)), b = this.pos(this.poeTip(api)), c = this.modelTip(api);
    const d = (u, v) => Math.hypot(u[0] - v[0], u[1] - v[1], u[2] - v[2]);
    const dDP = d(a, b), dPM = d(b, c), p = api.p;
    const ex = [30, -60, 90, -120, -90, 45].every((v, i) => [p.j1, p.j2, p.j3, p.j4, p.j5, p.j6][i] === v);
    if (api.scene === "ur" && ex && p.tbl === 0 && dDP < 1e-9 && dPM < 1e-6) api.done("ur_ex");
    if (api.scene === "ur" && ex && p.tbl === 1 && dDP > 5e-4 && dDP < 1e-3) api.done("ur_vendor");
    const movedP = [p.j1, p.j2, p.j3, p.j4, p.j5, p.j6, p.j7].filter((x) => x !== 0).length;
    if (api.scene === "panda" && movedP >= 3 && dDP < 1e-6 && dPM < 1e-6) api.done("panda");
    const movedL = [p.j2, p.j3, p.j4].filter((x) => x !== 0).length;
    if (api.scene === "lamp" && movedL >= 2 && dDP < 1e-9) api.done("lamp");
    const v = (u) => `(${api.fmt(u[0], 4)}, ${api.fmt(u[1], 4)}, ${api.fmt(u[2], 4)}) m`;
    const dhName = api.scene === "panda" ? ["DH（Craig 表）", "DH (Craig table)"] : (api.scene === "ur" && p.tbl === 1 ? ["DH（厂商表）", "DH (maker's table)"] : ["DH（零件库尺寸）", "DH (library model)"]);
    const gap = (x) => (x < 1e-4 ? x.toExponential(1) + " m" : api.fmt(x * 1000, 2) + " mm");
    return [[dhName, v(a)], [["指数积", "PoE"], v(b)], [["三维模型", "3D model"], v(c)],
            [["DH 与指数积之差", "DH vs PoE"], gap(dDP)], [["指数积与模型之差", "PoE vs model"], gap(dPM)]];
  },
  draw(api, s) {
    const ur = api.m["B-ARM-UR5E"], pa = api.m["B-ARM-PANDA"], P = api.scene === "panda";
    ur.holder.visible = !P; pa.holder.visible = P;
    if (api.keep.shown !== api.scene) { api.keep.shown = api.scene; api.view(35, 22, 0.85, P ? pa : ur); }
    this.modelTip(api);
  },
});
