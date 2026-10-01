// 实验 12.1 UR5e 的关节轴（配 12.1 节）。零件库 UR5e 三维模型；六个滑块控制六个关节，实时画出六根关节轴。
// 末端取法兰盘中心：模型最后一个连杆 wrist_3_link 上的 (0, 0.1, 0)。坐标以机器人基座坐标系 {s} 表示：
// 模型的 base 连杆相对 {s} 绕 z 转了 180°，所以从模型读出的 (x, y, z) 要换成 (−x, −y, z)。
WQ.lab({
  title: ["实验 12.1 UR5e 的关节轴", "Lab 12.1 The joint axes of the UR5e"],
  goal: ["只转动一个关节，看末端绕哪根轴、沿什么圆运动；把读数与表 12.1.1 的尺寸对照。",
         "Turn one joint at a time: see which axis the tool circles and check the readings against the dimensions in Table 12.1.1."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 六个关节", "UR5e, six joints"],
      problem: { title: ["机器人问题：每个关节转动时末端怎样动", "Robot problem: how the tool moves when one joint turns"],
                 text: ["控制器要由关节角算出末端位置。先弄清楚：只转一个关节时，末端绕哪根轴、在什么圆上运动。",
                        "The controller computes the tool position from the joint angles. First: when one joint turns, about which axis and on what circle does the tool move?"] } },
    { id: "lamp", name: ["只用关节 2、3、4（像台灯）", "Joints 2, 3, 4 only (like a desk lamp)"],
      problem: { title: ["生活中的例子：台灯的三个铰链", "Everyday example: the three hinges of a desk lamp"],
                 text: ["关节 2、3、4 的轴互相平行，就像台灯的三个铰链：手臂只在一个竖直平面内俯仰。",
                        "Joints 2, 3, 4 have parallel axes, like the three hinges of a desk lamp: the arm only pitches in one vertical plane."] } },
  ],
  params: [
    { id: "j1", name: ["关节 1 θ₁", "Joint 1 θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j2", name: ["关节 2 θ₂", "Joint 2 θ₂"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j3", name: ["关节 3 θ₃", "Joint 3 θ₃"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j4", name: ["关节 4 θ₄", "Joint 4 θ₄"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j5", name: ["关节 5 θ₅", "Joint 5 θ₅"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j6", name: ["关节 6 θ₆", "Joint 6 θ₆"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "clear", name: ["清除轨迹", "Clear trace"] }],
  tasks: [
    { id: "j1", robot: true, text: ["从零位出发只把关节 1 转到 90°：末端在以竖直轴为中心的圆上运动。", "From home turn only joint 1 to 90°: the tool moves on a circle about the vertical axis."],
      demo: { scene: "ur", set: { j1: 90, j2: 0, j3: 0, j4: 0, j5: 0, j6: 0 }, press: [], wait: 1 } },
    { id: "j6", robot: true, text: ["只转动关节 6：法兰盘中心不动。", "Turn only joint 6: the flange centre does not move."],
      demo: { scene: "ur", set: { j1: 0, j2: 0, j3: 0, j4: 0, j5: 0, j6: 60 }, press: [], wait: 1 } },
    { id: "up", text: ["只把关节 2 转到 −90°，使手臂竖直向上；读出末端高度，与 H₁ + L₁ + L₂ 比较。", "Turn only joint 2 to −90° (arm straight up); compare the tool height with H₁ + L₁ + L₂."],
      demo: { scene: "lamp", set: { j1: 0, j2: -90, j3: 0, j4: 0, j5: 0, j6: 0 }, press: [], wait: 1 } },
  ],
  think: ["关节 6 的轴为什么恰好通过法兰盘中心？如果末端装了一把偏心的工具，只转关节 6 时工具尖端会怎样运动？",
          "Why does joint 6's axis pass through the flange centre? With an off-centre tool, how would its tip move when only joint 6 turns?"],

  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  C: ["shoulder_link", "upper_arm_link", "forearm_link", "wrist_1_link", "wrist_2_link", "wrist_3_link"],
  ang(api) {
    const d = Math.PI / 180, v = [api.p.j1, api.p.j2, api.p.j3, api.p.j4, api.p.j5, api.p.j6].map((x) => x * d);
    return api.scene === "lamp" ? [0, v[1], v[2], v[3], 0, 0] : v;
  },
  pose(api) { const a = this.ang(api), o = {}; this.J.forEach((n, i) => { o[n] = a[i]; }); return o; },
  flange(arm) { const [x, y, z] = arm.local("wrist_3_link", [0, 0.1, 0]); return [-x, -y, z]; },   // 换到 {s}

  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    keep.arrows = this.C.map(() => { const a = new T.ArrowHelper(new T.Vector3(0, 1, 0), new T.Vector3(), 0.3, 0xc98f00, 0.05, 0.03); api.st.scene.add(a); return a; });
    keep.trace = api.trace(0xcf222e);
    arm.nodes.root.add(new T.AxesHelper(0.3));     // 基座坐标系 {s}（模型 base 连杆绕 z 转了 180°，不能用它的坐标系）
    keep.viewed = false;
  },
  reset(api, s) { s.last = null; },          // 拖动滑块时保留轨迹，便于看出末端走过的圆
  action(id, api) { if (id === "clear" && api.keep.trace) api.keep.trace.clear(); },
  readouts(api, s) {
    const arm = api.m["B-ARM-UR5E"];
    if (!arm) return [];
    arm.set(this.pose(api));
    const p = this.flange(arm), a = this.ang(api);
    const only = (k) => a.every((v, i) => (i === k ? Math.abs(v) > 1e-9 : v === 0));
    if (api.scene === "ur" && api.p.j1 === 90 && only(0)) api.done("j1");
    const home = [-0.817, -0.234, 0.063];
    if (api.scene === "ur" && only(5) && Math.hypot(p[0] - home[0], p[1] - home[1], p[2] - home[2]) < 1e-6) api.done("j6");
    if (api.p.j2 === -90 && a.every((v, i) => i === 1 || v === 0) && Math.abs(p[2] - 0.98) < 1e-3) api.done("up");
    return [[["法兰盘中心 x", "flange x"], api.fmt(p[0], 4) + " m"], [["法兰盘中心 y", "flange y"], api.fmt(p[1], 4) + " m"],
            [["法兰盘中心 z", "flange z"], api.fmt(p[2], 4) + " m"], [["到关节 1 轴的距离", "distance from joint-1 axis"], api.fmt(Math.hypot(p[0], p[1]), 4) + " m"]];
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"];
    arm.set(this.pose(api));
    if (!api.keep.viewed) { api.keep.viewed = true; api.view(35, 22, 0.8, arm); }
    const js = arm.entry.joints, T = api.three;
    this.C.forEach((child, i) => {     // 关节 i 的轴：经过子连杆原点，方向为关节表中的 axis（子连杆坐标系）
      const j = js.find((x) => x.child === child);
      const o = arm.point(child, [0, 0, 0]), e = arm.point(child, j.axis);
      const dir = new T.Vector3().subVectors(e, o).normalize();
      api.keep.arrows[i].position.copy(o.clone().addScaledVector(dir, -0.15));
      api.keep.arrows[i].setDirection(dir);
    });
    const tip = arm.point("wrist_3_link", [0, 0.1, 0]);
    if (!s.last || tip.distanceTo(s.last) > 0.002) { api.keep.trace.add(tip); s.last = tip; }
  },
});
