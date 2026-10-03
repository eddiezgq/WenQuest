// 实验 3.6 角速度与 v = ω × r（配 3.6 节）。零件库 UR5e 模型，零位（各关节角为 0）。
// 选择关节 1（轴 z_s，过 (0, 0, 0.163) m）或关节 2（轴 −y_s，过 (0, −0.138, 0.163) m），按“开始”后以 θ̇ 匀速转动。
// 箭头、读数都在机座坐标系 {s} 中（模型的 root 节点，z 向上；模型 base 连杆相对它绕 z 转了 180°，不能用 base 的坐标系）。
// 法兰盘中心 = wrist_3_link 上的 (0, 0.1, 0)，零位时在 {s} 中为 (−0.817, −0.234, 0.063) m。
// 公式速度 v = ω × r（r 从轴上的参考点量起，参考点可沿轴移动 h）；“由位置求导的速度”= 模型在转角 ±0.2° 处的位置差 / 所用时间。
WQ.lab({
  title: ["实验 3.6 角速度与 v = ω × r", "Lab 3.6 Angular velocity and v = ω × r"],
  goal: ["让 UR5e 的一个关节匀速转动，比较 ω × r 算出的速度与由位置差测得的速度；体会参考点可以取在轴上任意处。",
         "Turn one UR5e joint at a steady rate; compare the velocity from ω × r with the one measured from position differences; see that the reference point may be anywhere on the axis."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 单关节转动", "UR5e, one joint turning"],
      problem: { title: ["机器人问题：关节转多快，末端就有多快", "Robot problem: how fast the end-effector moves when a joint turns"],
                 text: ["示教时末端速度不得超过 250 mm/s。手臂水平伸出时，底座关节转多快才不超限？",
                        "During teaching the end-effector may not exceed 250 mm/s. With the arm stretched out, how fast may the base joint turn?"] } },
    { id: "disk", name: ["唱片机转盘", "Record turntable"], hide: ["joint", "h"],
      problem: { title: ["生活中的例子：唱片外圈为什么转得“快”", "Everyday example: why the outer groove moves faster"],
                 text: ["转盘以 33⅓ r/min（每秒 200°）转动。唱片外缘半径 0.15 m，外缘的线速度是多少？",
                        "The platter turns at 33⅓ r/min (200° per second). The record's rim has radius 0.15 m; how fast does the rim move?"] },
      params: { w: { min: 0, max: 360, value: 200 } } },
  ],
  params: [
    { id: "joint", name: ["转动的关节（1 或 2）", "Joint that turns (1 or 2)"], min: 1, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "w", name: ["转速 θ̇", "Rate θ̇"], min: 0, max: 180, step: 1, value: 60, unit: "°/s", digits: 0 },
    { id: "h", name: ["参考点沿轴移动 h", "Reference point moved along the axis, h"], min: -0.5, max: 0.5, step: 0.05, value: 0, unit: "m", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "j1", robot: true, text: ["关节 1 以 60°/s 转动：公式速度与测量速度相符（相差小于 1%），读出 |v|。", "Joint 1 at 60°/s: the formula and the measurement agree (within 1%); read |v|."],
      demo: { scene: "ur", set: { joint: 1, w: 60, h: 0 }, press: ["start"], wait: 4 } },
    { id: "limit", robot: true, text: ["零位下，找出使法兰盘速度不超过 250 mm/s 的关节 1 最大整数转速。", "In the zero position, find the largest whole-degree rate of joint 1 that keeps the flange at or below 250 mm/s."],
      demo: { scene: "ur", set: { joint: 1, w: 16, h: 0 }, press: [], wait: 1 } },
    { id: "ref", robot: true, text: ["关节 2 转动时，把参考点沿轴移动 0.1 m 以上：r 改变，而 ω × r 不变。", "With joint 2 turning, move the reference point along the axis by 0.1 m or more: r changes, ω × r does not."],
      demo: { scene: "ur", set: { joint: 2, w: 30, h: 0.3 }, press: ["start"], wait: 4 } },
    { id: "disk", text: ["转盘以 33⅓ r/min（200°/s）转动，读出外缘的线速度。", "Turn the platter at 33⅓ r/min (200°/s) and read the rim speed."],
      demo: { scene: "disk", set: { w: 200 }, press: ["start"], wait: 4 } },
  ],
  think: ["为什么参考点必须取在转轴上？若取在轴外，ω × r 还等于该点的速度吗？（提示：第 6 章的运动旋量）",
          "Why must the reference point lie on the axis? If it does not, is ω × r still the point's velocity? (Hint: the twist of Chapter 6)"],

  AX: { 1: { w: [0, 0, 1], q: [0, 0, 0.163], name: "shoulder_pan_joint" }, 2: { w: [0, -1, 0], q: [0, -0.138, 0.163], name: "shoulder_lift_joint" } },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  norm(a) { return Math.hypot(a[0], a[1], a[2]); },
  flangeS(api) {   // 法兰盘中心在 {s} 中的分量
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    const pw = arm.point("wrist_3_link", [0, 0.1, 0]);
    const inv = new T.Matrix4().copy(arm.nodes.root.matrixWorld).invert();
    const p = pw.applyMatrix4(inv);
    return [p.x, p.y, p.z];
  },
  pose(api, s) {
    const o = { shoulder_pan_joint: 0, shoulder_lift_joint: 0, elbow_joint: 0, wrist_1_joint: 0, wrist_2_joint: 0, wrist_3_joint: 0 };
    o[this.AX[api.p.joint].name] = (s.ang || 0) * Math.PI / 180;
    return o;
  },
  kin(api, s) {    // 当前位置、角速度、参考点、公式速度
    const d = Math.PI / 180, wr = api.p.w * d;
    if (api.scene === "disk") {
      const t = (s.ang || 0) * d, R = 0.15, c = api.keep.diskC || [0, 0, 0.45];
      const p = [c[0] + R * Math.cos(t), c[1] + R * Math.sin(t), c[2]], q = c.slice(), om = [0, 0, wr];
      const r = [p[0] - q[0], p[1] - q[1], p[2] - q[2]];
      return { p, q, om, r, v: this.cross(om, r), rho: R };
    }
    const a = this.AX[api.p.joint], p = this.flangeS(api);
    const q = [a.q[0] + api.p.h * a.w[0], a.q[1] + api.p.h * a.w[1], a.q[2] + api.p.h * a.w[2]];
    const om = [wr * a.w[0], wr * a.w[1], wr * a.w[2]];
    const r = [p[0] - q[0], p[1] - q[1], p[2] - q[2]];
    const along = r[0] * a.w[0] + r[1] * a.w[1] + r[2] * a.w[2];
    const rho = this.norm([r[0] - along * a.w[0], r[1] - along * a.w[1], r[2] - along * a.w[2]]);
    return { p, q, om, r, v: this.cross(om, r), rho, q0: a.q };
  },

  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    arm.root.updateMatrixWorld(true);
    // 箭头与转盘放在一个与 {s} 重合的独立组里（不挂在模型下，以免影响取景时的包围盒）
    const S = new T.Group();
    S.matrixAutoUpdate = false;
    S.matrix.copy(arm.nodes.root.matrixWorld);
    api.st.scene.add(S);
    keep.S = S;
    S.add(new T.AxesHelper(0.25));
    const mk = (color) => { const h = new T.ArrowHelper(new T.Vector3(0, 0, 1), new T.Vector3(), 0.3, color, 0.06, 0.035); S.add(h); return h; };
    keep.wA = mk(0x1d2327); keep.rA = mk(0x1f77b4); keep.vA = mk(0xd62728);
    const disk = new T.Group();
    const plat = new T.Mesh(new T.CylinderGeometry(0.15, 0.15, 0.006, 64), new T.MeshStandardMaterial({ color: 0x2b2b2b }));
    plat.rotation.x = Math.PI / 2;                       // 圆柱的轴（局部 y）转到 {s} 的 z
    const label = new T.Mesh(new T.CylinderGeometry(0.045, 0.045, 0.008, 32), new T.MeshStandardMaterial({ color: 0xb8860b }));
    label.rotation.x = Math.PI / 2;
    const mark = new T.Mesh(new T.SphereGeometry(0.008, 16, 12), new T.MeshStandardMaterial({ color: 0xd62728 }));
    mark.position.set(0.15, 0, 0.01);
    disk.add(plat, label, mark);
    S.add(disk);
    keep.disk = disk;
    keep.scene = "";
  },
  reset(api, s) { s.ang = 0; s.prev = null; s.vm = null; s.t = 0; },
  measure(api, s) {   // 由模型位置数值求导：转角 ±δ 处的位置差 ÷ 转过 2δ 所用的时间（与公式 ω × r 无关）
    const arm = api.m["B-ARM-UR5E"], a0 = s.ang || 0, dA = 0.2, ps = [];
    for (const da of [dA, -dA]) {
      s.ang = a0 + da;
      if (api.scene === "ur") arm.set(this.pose(api, s));
      ps.push(this.kin(api, s).p);
    }
    s.ang = a0;
    if (api.scene === "ur") arm.set(this.pose(api, s));
    const f = api.p.w / (2 * dA);     // (m / °) × (°/s)
    return [(ps[0][0] - ps[1][0]) * f, (ps[0][1] - ps[1][1]) * f, (ps[0][2] - ps[1][2]) * f];
  },
  update(dt, api, s) {
    s.ang += api.p.w * dt;
    const arm = api.m["B-ARM-UR5E"];
    if (api.scene === "ur") arm.set(this.pose(api, s));
    const k = this.kin(api, s);
    s.vm = this.measure(api, s);
    s.t += dt;
    const vf = this.norm(k.v), dv = this.norm([s.vm[0] - k.v[0], s.vm[1] - k.v[1], s.vm[2] - k.v[2]]);
    if (api.scene === "ur" && api.p.joint === 1 && api.p.w === 60 && dv < 0.01 * vf) api.done("j1");
    if (api.scene === "ur" && api.p.joint === 2 && Math.abs(api.p.h) >= 0.1 - 1e-9) {
      const r0 = [k.p[0] - k.q0[0], k.p[1] - k.q0[1], k.p[2] - k.q0[2]], v0 = this.cross(k.om, r0);
      if (this.norm([v0[0] - k.v[0], v0[1] - k.v[1], v0[2] - k.v[2]]) < 1e-12) api.done("ref");
    }
    if (api.scene === "disk" && api.p.w === 200) api.done("disk");
    if (s.ang >= 360) s.ang -= 360;
  },
  readouts(api, s) {
    const arm = api.m["B-ARM-UR5E"];
    if (!arm) return [];
    if (api.scene === "ur") arm.set(this.pose(api, s));
    const k = this.kin(api, s), vf = this.norm(k.v);
    if (api.scene === "ur" && api.p.joint === 1 && api.p.w === 16 && !api.running && Math.abs(s.ang) < 1e-9 && vf <= 0.25) api.done("limit");
    const V = (a, n) => `(${api.fmt(a[0], n)}, ${api.fmt(a[1], n)}, ${api.fmt(a[2], n)})`;
    const rows = [
      [["角速度 ω（{s} 中，rad/s）", "ω in {s} (rad/s)"], V(k.om, 4)],
      [["r = 位置 − 参考点（m）", "r = position − reference (m)"], V(k.r, 3)],
      [["公式速度 ω × r（m/s）", "formula ω × r (m/s)"], V(k.v, 4)],
      [["由位置求导的速度（m/s）", "velocity from positions (m/s)"], api.running && s.vm ? V(s.vm, 4) : api.T("按“开始”后显示", "press Start")],
      [["|v|（公式）", "|v| (formula)"], api.fmt(vf * 1000, 1) + " mm/s"],
      [["到转轴的距离 ρ", "distance to the axis ρ"], api.fmt(k.rho, 4) + " m"],
    ];
    if (api.scene === "ur") rows.push([["降速限值 250 mm/s", "reduced-speed limit 250 mm/s"], vf <= 0.25 ? api.T("满足", "met") : api.T("超限", "exceeded")]);
    return rows;
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], T = api.three, keep = api.keep;
    const ur = api.scene === "ur";
    if (keep.scene !== api.scene) {
      keep.scene = api.scene;
      arm.nodes.base.visible = ur;
      keep.disk.visible = !ur;
      if (!ur) {     // 转盘放在取景中心：与实验框架取景的算法相同（模型包围盒并上工作半径的盒子）
        const b = arm.box(), r = ((arm.entry.robot || {}).reach_mm || 0) / 1000, c = arm.point(arm.entry.root);
        if (r > 0) b.union(new T.Box3(new T.Vector3(c.x - r, 0, c.z - r), new T.Vector3(c.x + r, c.y + r, c.z + r)));
        const cw = b.getCenter(new T.Vector3()).applyMatrix4(new T.Matrix4().copy(keep.S.matrix).invert());
        keep.diskC = [cw.x, cw.y, cw.z];
        keep.disk.position.set(cw.x, cw.y, cw.z - 0.01);       // 盘面略低于参考平面，箭头画在盘面之上
      }
      if (ur) api.view(35, 24, 0.85); else api.view(25, 40, 2.4);
    }
    if (ur) arm.set(this.pose(api, s));
    else keep.disk.rotation.z = (s.ang || 0) * Math.PI / 180;
    const k = this.kin(api, s);
    const V3 = (a) => new T.Vector3(a[0], a[1], a[2]);
    const wn = this.norm(k.om) || 1, dir = V3(k.om).multiplyScalar(1 / wn);
    if (this.norm(k.om) < 1e-12) dir.set(0, 0, 1);
    keep.wA.position.copy(V3(k.q)); keep.wA.setDirection(dir); keep.wA.setLength(ur ? 0.35 : 0.2, 0.06, 0.035);
    const rl = this.norm(k.r);
    keep.rA.position.copy(V3(k.q)); keep.rA.setDirection(V3(k.r).normalize()); keep.rA.setLength(rl, Math.min(0.05, rl * 0.2), ur ? 0.03 : 0.015);
    const vl = this.norm(k.v);
    keep.vA.visible = vl > 1e-6;
    if (vl > 1e-6) { keep.vA.position.copy(V3(k.p)); keep.vA.setDirection(V3(k.v).normalize()); keep.vA.setLength(ur ? Math.min(0.5, 0.35 * vl) + 0.05 : 0.2 * vl + 0.03, ur ? 0.05 : 0.025, ur ? 0.03 : 0.015); }
  },
});
