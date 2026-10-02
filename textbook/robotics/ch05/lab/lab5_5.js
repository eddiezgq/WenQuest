// 实验 5.5 相机-机械臂-工件的坐标链（配 5.5 节）。零件库 UR5e 模型。
// 工作站与 5.5 节相同：T_ws = (Rot(z, 180°), (0.30, 0.40, 0))，T_wc 为高 0.90 m、光轴偏离竖直 15° 的固定相机，
// T_bt = (Rot(x, −90°), (0, 0.15, 0))，T_og = (Rot(x, 180°), (0, 0, 0.015))。齿轮坯在料盘上的位姿由滑块给出（这是“真实世界”）。
// 相机实际安装姿态 = T_wc · Rot(x_c, δ)；它测得 T_co = (T_wc Rot(x_c, δ))⁻¹ T_wo。程序却按标定值 T_wc 计算目标：
// T_sb* = T_sw T_wc T_co T_og T_tb（式 (5.5.2)），用数值逆运动学求关节角，机械臂先到预抓取位姿（上方 50 mm），再下降。
// 偏差 = 夹爪指尖中心（模型 wrist_3_link 上的 (0, 0.25, 0)，由三维模型独立算出）与真实抓取点之间的距离。
WQ.lab({
  title: ["实验 5.5 相机-机械臂-工件的坐标链", "Lab 5.5 The camera-arm-part chain"],
  goal: ["相机看到齿轮坯，程序沿坐标链算出法兰的目标位姿，机械臂伸过去夹取。改变工件位置和相机安装误差，看偏差怎样变化。",
         "The camera sees the gear blank, the program follows the chain to the flange target, and the arm reaches for it. Move the part and add a camera mounting error to see how the miss changes."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "cell", robot: true, name: ["视觉引导抓取", "Vision-guided pick"], hide: ["cerr"],
      problem: { title: ["机器人问题：由相机读数求机械臂的目标", "Robot problem: from the camera reading to the arm's target"],
                 text: ["齿轮坯在料盘里的位置和转角每次不同。相机报告 T_co，机械臂要从正上方夹住它厚度的一半处。",
                        "The gear blank lands differently each time. The camera reports T_co; the arm must grip it from above at half its thickness."] } },
    { id: "car", name: ["倒车影像", "Reversing camera"], hide: ["ox", "oy", "oyaw", "err"],
      problem: { title: ["生活中的例子：倒车影像测距", "Everyday example: distance from a reversing camera"],
                 text: ["车尾相机高 1.0 m，看地面上车后 3.0 m 处的路锥。相机若装歪（俯仰），算出的距离就不对。图中按 1:4 缩小。",
                        "The rear camera is 1.0 m high and sees a cone 3.0 m behind. If it is tilted wrongly, the distance is wrong. Drawn at 1:4."] } },
  ],
  params: [
    { id: "ox", name: ["齿轮坯 x（{w} 中）", "Gear blank x (in {w})"], min: 0.7, max: 0.9, step: 0.01, value: 0.8, unit: "m", digits: 2 },
    { id: "oy", name: ["齿轮坯 y（{w} 中）", "Gear blank y (in {w})"], min: 0.38, max: 0.52, step: 0.01, value: 0.45, unit: "m", digits: 2 },
    { id: "oyaw", name: ["齿轮坯转角", "Gear blank angle"], min: -180, max: 180, step: 5, value: 25, unit: "°", digits: 0 },
    { id: "err", name: ["相机安装误差 δ（绕 x_c）", "Camera mounting error δ (about x_c)"], min: 0, max: 1, step: 0.1, value: 0, unit: "°", digits: 1 },
    { id: "cerr", name: ["倒车相机俯仰误差", "Reversing camera pitch error"], min: 0, max: 3, step: 0.5, value: 0, unit: "°", digits: 1 },
  ],
  buttons: [{ id: "grasp", name: ["抓取", "Pick"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "nom", robot: true, text: ["无误差时（δ = 0）抓取默认位置的齿轮坯：偏差小于 0.1 mm。", "With δ = 0, pick the gear blank at its default place: miss below 0.1 mm."],
      demo: { scene: "cell", set: { ox: 0.8, oy: 0.45, oyaw: 25, err: 0 }, press: ["grasp"], wait: 6 } },
    { id: "err", robot: true, text: ["把相机安装误差设为 0.5° 再抓取：偏差约 8 mm（与表 5.5.2 比较）。", "Set the mounting error to 0.5° and pick again: the miss is about 8 mm (compare Table 5.5.2)."],
      demo: { scene: "cell", set: { ox: 0.8, oy: 0.45, oyaw: 25, err: 0.5 }, press: ["grasp"], wait: 6 } },
    { id: "move", robot: true, text: ["δ = 0 时把齿轮坯挪动 5 cm 以上、转角改变 30° 以上，再抓取成功。", "With δ = 0, move the blank by 5 cm or more and turn it by 30° or more, then pick it successfully."],
      demo: { scene: "cell", set: { ox: 0.72, oy: 0.5, oyaw: 70, err: 0 }, press: ["grasp"], wait: 6 } },
    { id: "car", text: ["倒车相机俯仰装歪 1° 时，读出 3 m 处路锥的测距误差。", "With a 1° pitch error, read the distance error for the cone 3 m behind."],
      demo: { scene: "car", set: { cerr: 1 }, press: [], wait: 1 } },
  ],
  think: ["同样 0.5° 的误差，若绕相机光轴，偏差只有零点几毫米。为什么？若把相机降低一半高度，绕 x_c 的偏差会变成多少？",
          "The same 0.5° about the optical axis gives a fraction of a millimetre. Why? If the camera is mounted at half the height, what becomes of the miss about x_c?"],

  // ---------------------------------------------------------------- 4×4 矩阵（按行）
  M: {
    I() { return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]; },
    mul(A, B) { const C = this.I().map((r) => r.map(() => 0));
      for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { let s = 0; for (let k = 0; k < 4; k++) s += A[i][k] * B[k][j]; C[i][j] = s; } return C; },
    inv(T) { const R = [[T[0][0], T[1][0], T[2][0]], [T[0][1], T[1][1], T[2][1]], [T[0][2], T[1][2], T[2][2]]];
      const p = [0, 1, 2].map((i) => -(R[i][0] * T[0][3] + R[i][1] * T[1][3] + R[i][2] * T[2][3]));
      return [[...R[0], p[0]], [...R[1], p[1]], [...R[2], p[2]], [0, 0, 0, 1]]; },
    rot(w, t) { const [x, y, z] = w, c = Math.cos(t), s = Math.sin(t), v = 1 - c;
      return [[c + x * x * v, x * y * v - z * s, x * z * v + y * s, 0], [y * x * v + z * s, c + y * y * v, y * z * v - x * s, 0],
              [z * x * v - y * s, z * y * v + x * s, c + z * z * v, 0], [0, 0, 0, 1]]; },
    tr(x, y, z) { return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]; },
    exp6(w, q, t) { const R = this.rot(w, t), p = [0, 1, 2].map((i) => q[i] - (R[i][0] * q[0] + R[i][1] * q[1] + R[i][2] * q[2]));
      R[0][3] = p[0]; R[1][3] = p[1]; R[2][3] = p[2]; return R; },
    logR(A) {   // 姿态差的转动矢量（4.4 节的对数映射，小角度时准确）
      const a = [(A[2][1] - A[1][2]) / 2, (A[0][2] - A[2][0]) / 2, (A[1][0] - A[0][1]) / 2], n = Math.hypot(...a);
      const th = Math.atan2(n, (A[0][0] + A[1][1] + A[2][2] - 1) / 2);
      if (n < 1e-15) return [0, 0, 0];
      return a.map((x) => x / n * th); },
  },
  AX: [[[0, 0, 1], [0, 0, 0.163]], [[0, -1, 0], [0, -0.138, 0.163]], [[0, -1, 0], [-0.425, -0.007, 0.163]],
       [[0, -1, 0], [-0.817, -0.007, 0.163]], [[0, 0, -1], [-0.817, -0.134, 0.163]], [[0, -1, 0], [-0.817, -0.134, 0.063]]],
  HOME: [[1, 0, 0, -0.817], [0, -1, 0, -0.234], [0, 0, -1, 0.063], [0, 0, 0, 1]],
  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  READY: [0, -60, 100, -130, -90, 0].map((x) => x * Math.PI / 180),
  fk(th) { let T = this.M.I(); this.AX.forEach(([w, q], i) => { T = this.M.mul(T, this.M.exp6(w, q, th[i])); }); return this.M.mul(T, this.HOME); },
  err6(G, th) { const C = this.fk(th), Rd = this.M.mul(G, this.M.inv(C)), r = this.M.logR(Rd);
    return [...r, G[0][3] - C[0][3], G[1][3] - C[1][3], G[2][3] - C[2][3]]; },
  solve(A, b) {   // 6×6 高斯消元（列主元）
    const n = b.length, M = A.map((r, i) => [...r, b[i]]);
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      [M[c], M[p]] = [M[p], M[c]];
      for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c] / M[c][c]; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; }
    }
    return M.map((r, i) => r[n] / r[i]);
  },
  ik(G, seed) {   // 数值逆运动学（第 15 章）：牛顿迭代，雅可比用差分
    let th = seed.slice();
    for (let it = 0; it < 60; it++) {
      const e = this.err6(G, th);
      if (Math.hypot(...e) < 1e-12) break;
      const J = [0, 1, 2, 3, 4, 5].map(() => [0, 0, 0, 0, 0, 0]), h = 1e-7, C = this.fk(th);
      for (let i = 0; i < 6; i++) { const d = th.slice(); d[i] += h; const D = this.fk(d), r = this.M.logR(this.M.mul(D, this.M.inv(C)));
        const col = [...r, D[0][3] - C[0][3], D[1][3] - C[1][3], D[2][3] - C[2][3]]; for (let k = 0; k < 6; k++) J[k][i] = col[k] / h; }
      const dth = this.solve(J, e); th = th.map((x, i) => x + dth[i]);
    }
    return { th, res: Math.hypot(...this.err6(G, th)) };
  },
  Tws() { return [[-1, 0, 0, 0.3], [0, -1, 0, 0.4], [0, 0, 1, 0], [0, 0, 0, 1]]; },
  Twc() { const c = Math.cos(Math.PI / 12), s = Math.sin(Math.PI / 12); return [[0, c, -s, 1.05], [1, 0, 0, 0.4], [0, -s, -c, 0.9], [0, 0, 0, 1]]; },
  Two(api) { const T = this.M.rot([0, 0, 1], api.p.oyaw * Math.PI / 180); T[0][3] = api.p.ox; T[1][3] = api.p.oy; T[2][3] = 0.02; return T; },
  Tbt() { return [[1, 0, 0, 0], [0, 0, 1, 0.15], [0, -1, 0, 0], [0, 0, 0, 1]]; },
  Tog() { return [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0.015], [0, 0, 0, 1]]; },
  chain(api) {
    const M = this.M, actual = M.mul(this.Twc(), M.rot([1, 0, 0], api.p.err * Math.PI / 180));
    const Tco = M.mul(M.inv(actual), this.Two(api));                                  // 相机的测量（相对实际相机）
    const Tsg = M.mul(M.mul(M.mul(M.inv(this.Tws()), this.Twc()), Tco), this.Tog());  // 程序按标定值 T_wc 计算
    const Tsb = M.mul(Tsg, M.inv(this.Tbt()));
    const Tpre = M.mul(M.mul(Tsg, M.tr(0, 0, -0.05)), M.inv(this.Tbt()));
    const gw = M.mul(this.Two(api), M.tr(0, 0, 0.015));                               // 真实的抓取点（{w} 中）
    return { Tco, Tsg, Tsb, Tpre, gw: [gw[0][3], gw[1][3], gw[2][3]] };
  },
  tcpW(api) {   // 由三维模型独立算出的指尖中心，换到 {w}
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    const p = arm.point("wrist_3_link", [0, 0.25, 0]).applyMatrix4(new T.Matrix4().copy(arm.nodes.root.matrixWorld).invert());
    const W = this.Tws();
    return [0, 1, 2].map((i) => W[i][0] * p.x + W[i][1] * p.y + W[i][2] * p.z + W[i][3]);
  },
  pose(th) { const o = {}; this.J.forEach((n, i) => { o[n] = th[i]; }); return o; },

  m4(T, A) { return new T.Matrix4().set(...A[0], ...A[1], ...A[2], ...A[3]); },
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    arm.root.updateMatrixWorld(true);
    const S = new T.Group(); S.matrixAutoUpdate = false; S.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(S); keep.S = S;
    keep.sAx = new T.AxesHelper(0.15); S.add(keep.sAx);
    const W = new T.Group(); W.matrixAutoUpdate = false; W.matrix.copy(this.m4(T, this.M.inv(this.Tws()))); S.add(W); keep.W = W;
    const mat = (c, o) => new T.MeshStandardMaterial({ color: c, transparent: o < 1, opacity: o });
    const slab = new T.Mesh(new T.BoxGeometry(1.2, 0.8, 0.03), mat(0xc8ced3, 0.55)); slab.position.set(0.6, 0.4, -0.016); W.add(slab);
    const tray = new T.Mesh(new T.BoxGeometry(0.2, 0.16, 0.02), mat(0xe7d7a8, 1)); tray.position.set(0.8, 0.45, 0.01); W.add(tray);
    const part = new T.Group(); part.matrixAutoUpdate = false; W.add(part); keep.part = part;
    const cyl = new T.Mesh(new T.CylinderGeometry(0.04, 0.04, 0.03, 32), mat(0xb8860b, 1)); cyl.rotation.x = Math.PI / 2; cyl.position.z = 0.015; part.add(cyl);
    part.add(new T.AxesHelper(0.07));
    const pole = new T.Mesh(new T.BoxGeometry(0.03, 0.03, 0.98), mat(0x5b6b75, 1)); pole.position.set(1.17, 0.4, 0.49); W.add(pole);
    const bar = new T.Mesh(new T.BoxGeometry(0.15, 0.03, 0.03), mat(0x5b6b75, 1)); bar.position.set(1.11, 0.4, 0.975); W.add(bar);
    const camG = new T.Group(); camG.matrixAutoUpdate = false; W.add(camG); keep.cam = camG;
    const body = new T.Mesh(new T.BoxGeometry(0.06, 0.05, 0.08), mat(0x30363b, 1)); body.position.z = -0.03; camG.add(body);
    camG.add(new T.AxesHelper(0.1));
    const ray = new T.Line(new T.BufferGeometry().setFromPoints([new T.Vector3(), new T.Vector3()]), new T.LineBasicMaterial({ color: 0xd62728 }));
    W.add(ray); keep.ray = ray;
    const w3 = arm.nodes.wrist_3_link;
    const grip = new T.Mesh(new T.BoxGeometry(0.05, 0.15, 0.04), mat(0x5b6b75, 1)); grip.position.set(0, 0.175, 0); w3.add(grip);
    const tcp = new T.Group(); tcp.matrixAutoUpdate = false; tcp.matrix.copy(this.m4(T, this.M.mul(this.M.tr(0, 0.25, 0), this.M.rot([1, 0, 0], -Math.PI / 2)))); tcp.add(new T.AxesHelper(0.06)); w3.add(tcp);
    // 倒车影像（1:4 缩小）：地面、车身、相机、路锥、名义光线与实际光线
    const CAR = new T.Group(); CAR.position.set(-0.6, -0.2, 0.0); S.add(CAR); keep.car = CAR;
    const ground = new T.Mesh(new T.BoxGeometry(2.0, 0.5, 0.01), mat(0x9aa6ad, 0.5)); ground.position.set(0.3, 0, -0.005); CAR.add(ground);
    const carB = new T.Mesh(new T.BoxGeometry(1.1, 0.45, 0.36), mat(0x1f77b4, 1)); carB.position.set(-0.55, 0, 0.18); CAR.add(carB);
    const cone = new T.Mesh(new T.ConeGeometry(0.04, 0.12, 24), mat(0xf28c28, 1)); cone.rotation.x = Math.PI / 2; cone.position.set(0.75, 0, 0.06); CAR.add(cone);
    const mk = (c) => { const l = new T.Line(new T.BufferGeometry().setFromPoints([new T.Vector3(), new T.Vector3()]), new T.LineBasicMaterial({ color: c })); CAR.add(l); return l; };
    keep.rayN = mk(0x2ca02c); keep.rayA = mk(0xd62728);
    const box = (f) => ({ entry: { robot: {} }, holder: { visible: false }, box: f });
    api.m.cellView = box(() => new T.Box3().setFromObject(W).union(arm.box()));
    api.m.carView = box(() => new T.Box3().setFromObject(CAR));
    keep.scene = "";
  },
  reset(api, s) { s.th = this.READY.slice(); s.anim = null; s.done = false; s.miss = null; s.res = null; s.phase = ""; },
  action(id, api, s) {
    if (id !== "grasp" || api.scene !== "cell") return;
    const c = this.chain(api);
    const a = this.ik(c.Tpre, this.READY), b = this.ik(c.Tsb, a.th);
    s.res = Math.max(a.res, b.res);
    if (s.res > 1e-6) { s.phase = "fail"; return; }
    s.anim = { legs: [[s.th.slice(), a.th], [a.th, b.th]], k: 0, t: 0 }; s.done = false; s.miss = null; s.phase = "move";
    api.running = true;
  },
  update(dt, api, s) {
    if (!s.anim) { api.stop(); return; }
    const A = s.anim, L = A.legs[A.k], dur = 1.2;
    A.t = Math.min(dur, A.t + dt);
    const u = A.t / dur, e = u * u * (3 - 2 * u);
    s.th = L[0].map((x, i) => x + (L[1][i] - x) * e);
    if (A.t >= dur) {
      if (A.k + 1 < A.legs.length) { A.k++; A.t = 0; }
      else {
        s.th = L[1].slice(); api.m["B-ARM-UR5E"].set(this.pose(s.th));
        const c = this.chain(api), p = this.tcpW(api);
        s.miss = Math.hypot(p[0] - c.gw[0], p[1] - c.gw[1], p[2] - c.gw[2]); s.done = true; s.anim = null; s.phase = "done";
        const moved = Math.hypot(api.p.ox - 0.8, api.p.oy - 0.45) >= 0.05 - 1e-9 && Math.abs(api.p.oyaw - 25) >= 30 - 1e-9;
        if (api.p.err === 0 && s.miss < 1e-4 && !moved && api.p.oyaw === 25) api.done("nom");
        if (Math.abs(api.p.err - 0.5) < 1e-9 && s.miss > 0.006 && s.miss < 0.01) api.done("err");
        if (api.p.err === 0 && s.miss < 1e-4 && moved) api.done("move");
        api.stop();
      }
    }
  },
  readouts(api, s) {
    const arm = api.m["B-ARM-UR5E"];
    if (!arm) return [];
    if (!s.th) this.reset(api, s);
    if (api.scene === "car") {
      const h = 1.0, D = 3.0, b = Math.atan2(h, D), e = api.p.cerr * Math.PI / 180, Dp = h / Math.tan(b - e);
      if (Math.abs(api.p.cerr - 1) < 1e-9) api.done("car");
      return [[["路锥的真实距离", "true distance to the cone"], "3.000 m"],
              [["光线俯角（真实）", "ray depression angle (true)"], api.fmt(b * 180 / Math.PI, 2) + "°"],
              [["相机按名义安装角算出的距离", "distance computed with the nominal mounting"], api.fmt(Dp, 3) + " m"],
              [["测距误差", "distance error"], api.fmt((Dp - D) * 100, 1) + " cm"]];
    }
    const c = this.chain(api), r = (A, i) => `[${[0, 1, 2].map((j) => api.fmt(A[i][j], 3)).join("  ")} | ${api.fmt(A[i][3], 4)}]`;
    const deg = s.th.map((x) => api.fmt(x * 180 / Math.PI, 1)).join(", ");
    return [
      [["相机读数 T_co 第 4 列", "camera reading T_co, column 4"], `(${api.fmt(c.Tco[0][3], 4)}, ${api.fmt(c.Tco[1][3], 4)}, ${api.fmt(c.Tco[2][3], 4)}) m`],
      [["法兰目标 T_sb* 第 1 行", "flange target T_sb*, row 1"], r(c.Tsb, 0)], [["第 2 行", "row 2"], r(c.Tsb, 1)], [["第 3 行", "row 3"], r(c.Tsb, 2)],
      [["关节角 θ / °", "joint angles θ / °"], deg],
      [["夹爪偏差（三维模型测得）", "gripper miss (measured on the 3D model)"],
        s.phase === "fail" ? api.T("够不到", "out of reach") : s.miss === null ? api.T("按“抓取”", "press Pick") : api.fmt(s.miss * 1000, 3) + " mm"],
    ];
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], T = api.three, keep = api.keep;
    if (!s.th) this.reset(api, s);
    const cell = api.scene === "cell";
    if (keep.scene !== api.scene) {
      keep.scene = api.scene;
      arm.nodes.base.visible = cell; keep.W.visible = cell; keep.car.visible = !cell; keep.sAx.visible = cell;
      if (cell) api.view(35, 18, 1.4, api.m.cellView); else api.view(0, 15, 1.7, api.m.carView);
    }
    if (cell) {
      arm.set(this.pose(s.th));
      keep.part.matrix.copy(this.m4(T, this.Two(api)));
      const act = this.M.mul(this.Twc(), this.M.rot([1, 0, 0], api.p.err * Math.PI / 180));
      keep.cam.matrix.copy(this.m4(T, act));
      const g = this.Two(api), pts = [new T.Vector3(act[0][3], act[1][3], act[2][3]), new T.Vector3(g[0][3], g[1][3], g[2][3] + 0.03)];
      keep.ray.geometry.setFromPoints(pts);
    } else {
      const h = 0.25, cam = new T.Vector3(0, 0, h), D = 0.75, e = api.p.cerr * Math.PI / 180, b = Math.atan2(h, D);
      keep.rayN.geometry.setFromPoints([cam, new T.Vector3(D, 0, 0)]);
      keep.rayA.geometry.setFromPoints([cam, new T.Vector3(h / Math.tan(b - e), 0, 0)]);
    }
  },
});
