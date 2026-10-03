// 实验 14.3 帕登-卡汉子问题（配 14.3 节）。零件库 UR5e（关节角与第 12 章的指数积公式相同）。
// 场景“手腕：子问题 2”：其余关节为零，求 θ₅、θ₆ 使末端 x 轴指向 d。ω₅ = (0, 0, −1)，ω₆ = (0, −1, 0) 垂直相交于 P56，
//   式 (14.3.7)、(14.3.8) 化为 α = −d_z、β = 0、γ = ±√(1 − α²)，中间点 c = (−γ, 0, d_z)；再各做一次子问题 1：
//   θ₆ = atan2(d_z, −γ)，θ₅ = atan2(γ d_y, −γ d_x)。核对：从模型读出末端 x 轴（wrist_3_link 的 x 轴），与 d 的夹角。
// 场景“肘部：子问题 3”：只转关节 3，使腕部点 q₄ 到肩部点 q₂ 的距离为 δ。由式 (14.3.9)、(14.3.10)：
//   δ′² = δ² − W₂²，θ₃ = ±(π − arccos((L₁² + L₂² − δ′²)/(2L₁L₂)))。核对：从模型读出两点的距离。
// 生活场景“对准星星”：云台的水平转轴（z）与俯仰轴（水平）交于一点，两组解 (方位, 仰角) 与 (方位 + 180°, 180° − 仰角)。
// 模型 base 连杆相对 {s} 绕 z 转了 180°：local() 读出的 (x, y, z) 换成 (−x, −y, z)。
WQ.lab({
  title: ["实验 14.3 帕登-卡汉子问题", "Lab 14.3 The Paden–Kahan subproblems"],
  goal: ["用子问题 2 让 UR5e 的手腕把末端 x 轴转到指定方向，用子问题 3 让肘部把腕点送到指定距离，并比较两组解。",
         "Use Subproblem 2 to turn the UR5e's tool x axis to a given direction with the wrist, Subproblem 3 to set the shoulder–wrist distance with the elbow, and compare the two solutions."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "wrist", robot: true, name: ["手腕：子问题 2", "Wrist: Subproblem 2"], hide: ["delta"],
      problem: { title: ["机器人问题：末端 x 轴要指向这里", "Robot problem: point the tool x axis this way"],
                 text: ["UR5e 处于零位，只转关节 5、6。用方位角和仰角给出目标方向（金色箭头），界面求出两组 (θ₅, θ₆)，红色箭头是模型的末端 x 轴。",
                        "The UR5e is at home and only joints 5 and 6 turn. Azimuth and elevation give the target direction (gold arrow); both (θ₅, θ₆) are computed; the red arrow is the model's tool x axis."] } },
    { id: "elbow", robot: true, name: ["肘部：子问题 3", "Elbow: Subproblem 3"], hide: ["az", "el"],
      problem: { title: ["机器人问题：腕点离肩部要这么远", "Robot problem: put the wrist this far from the shoulder"],
                 text: ["只转关节 3，使关节 4 的中心离关节 2 的中心为 δ。界面按式 (14.3.10) 求出两个 θ₃，金色线段是两点的连线。",
                        "Only joint 3 turns so that the joint-4 centre is δ from the joint-2 centre. Eq. (14.3.10) gives two θ₃; the gold segment joins the two points."] } },
    { id: "cam", name: ["云台对准星星", "A camera mount aimed at a star"], hide: ["delta"],
      problem: { title: ["生活中的例子：云台的两组解", "Everyday example: the two solutions of a pan–tilt mount"],
                 text: ["云台的水平转轴竖直、俯仰轴水平，两轴交于一点。要对准一颗星，可以正着对，也可以多转 180° 再向后仰过头顶，倒着对。",
                        "The pan axis is vertical and the tilt axis horizontal, meeting at one point. A star can be aimed at upright, or by panning 180° more and tilting back over the top, upside down."] } },
  ],
  params: [
    { id: "az", name: ["目标方位角", "target azimuth"], min: -180, max: 180, step: 0.5, value: 45, unit: "°", digits: 1 },
    { id: "el", name: ["目标仰角", "target elevation"], min: -89, max: 89, step: 0.01, value: -35.26, unit: "°", digits: 2 },
    { id: "delta", name: ["肩—腕距离 δ", "shoulder–wrist distance δ"], min: 0.14, max: 0.828, step: 0.0001, value: 0.6, unit: "m", digits: 4 },
    { id: "sol", name: ["选择第几组解（0 或 1）", "which solution (0 or 1)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 14.3.2：目标方向 (1, 1, −1)/√3（方位 45°、仰角 −35.26°），读出两组 (θ₅, θ₆)：(135°, −144.7°) 与 (−45°, −35.3°)。",
                                     "Example 14.3.2: direction (1, 1, −1)/√3 (azimuth 45°, elevation −35.26°); read (135°, −144.7°) and (−45°, −35.3°)."],
      demo: { scene: "wrist", set: { az: 45, el: -35.26, sol: 0 }, press: [], wait: 1 } },
    { id: "flip", robot: true, text: ["同一目标下切换到另一组解：末端 x 轴不变，手腕的形态翻了过来。", "Switch to the other solution at the same target: the tool x axis stays, the wrist flips over."],
      demo: { scene: "wrist", set: { az: 45, el: -35.26, sol: 1 }, press: [], wait: 1 } },
    { id: "elbow", robot: true, text: ["复现算例 14.3.3：δ = 0.6 m，读出两个 θ₃（±88.53°）。", "Example 14.3.3: δ = 0.6 m; read the two θ₃ (±88.53°)."],
      demo: { scene: "elbow", set: { delta: 0.6, sol: 0 }, press: [], wait: 1 } },
    { id: "merge", robot: true, text: ["把 δ 增大到 0.827 m 以上，两个解靠拢到 |θ₃| < 3°（手臂接近伸直）。", "Raise δ above 0.827 m until the two solutions close in to |θ₃| < 3° (arm nearly straight)."],
      demo: { scene: "elbow", set: { delta: 0.8274, sol: 0 }, press: [], wait: 1 } },
    { id: "cam", text: ["生活场景：对准方位 120°、仰角 30° 的星星，用“倒过来”的那组解。", "Everyday scene: aim at the star at azimuth 120°, elevation 30° with the upside-down solution."],
      demo: { scene: "cam", set: { az: 120, el: 30, sol: 1 }, press: [], wait: 1 } },
  ],
  think: ["两根垂直相交的轴能把一个方向转到任何方向吗？在什么方向上两组解会合成一组？",
          "Can two perpendicular intersecting axes turn one direction into any other? For which directions do the two solutions merge?"],

  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  L1: 0.425, L2: 0.392, W2: 0.131,
  dir(api) {
    const a = api.p.az * Math.PI / 180, e = api.p.el * Math.PI / 180;
    return [Math.cos(e) * Math.cos(a), Math.cos(e) * Math.sin(a), Math.sin(e)];
  },
  wristSols(d) {                          // 子问题 2：两组 (θ₅, θ₆)
    const al = -d[2], g = Math.sqrt(Math.max(0, 1 - al * al));
    return [g, -g].map((gg) => ({ t5: Math.atan2(gg * d[1], -gg * d[0]), t6: Math.atan2(d[2], -gg) }));
  },
  elbowSols(delta) {                      // 子问题 3：两个 θ₃
    const dp2 = delta * delta - this.W2 * this.W2, c = (this.L1 * this.L1 + this.L2 * this.L2 - dp2) / (2 * this.L1 * this.L2);
    if (dp2 < 0 || Math.abs(c) > 1 + 1e-12) return [];
    const phi = Math.atan2(Math.sqrt(Math.max(0, 1 - c * c)), c), t = Math.PI - phi;
    return t < 1e-9 ? [0] : [t, -t];
  },
  camSols(d) {                            // 云台：方位 a、仰角 b；d = (cos b cos a, cos b sin a, sin b)
    const a = Math.atan2(d[1], d[0]), b = Math.asin(Math.max(-1, Math.min(1, d[2])));
    return [{ a, b }, { a: Math.atan2(Math.sin(a + Math.PI), Math.cos(a + Math.PI)), b: Math.PI - b }];
  },
  pose(api) {
    const z = [0, 0, 0, 0, 0, 0];
    if (api.scene === "wrist") { const s = this.wristSols(this.dir(api))[api.p.sol]; z[4] = s.t5; z[5] = s.t6; }
    if (api.scene === "elbow") { const s = this.elbowSols(api.p.delta); if (s.length) z[2] = s[Math.min(api.p.sol, s.length - 1)]; }
    const o = {}; this.J.forEach((n, i) => { o[n] = z[i]; }); return o;
  },
  S(arm, link, xyz) { const [x, y, z] = arm.local(link, xyz); return [-x, -y, z]; },

  setup3d(api, keep) {
    const T = api.three, arm = api.m["B-ARM-UR5E"], root = arm.nodes.root;
    root.add(new T.AxesHelper(0.25));
    keep.target = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(), 0.3, 0xc98f00, 0.06, 0.035);
    keep.xb = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(), 0.22, 0xd62728, 0.05, 0.03);
    root.add(keep.target, keep.xb);
    const gm = new T.BufferGeometry().setFromPoints([new T.Vector3(), new T.Vector3()]);
    keep.seg = new T.Line(gm, new T.LineBasicMaterial({ color: 0xc98f00 }));
    root.add(keep.seg);
    // 云台：底座、随方位转动的叉架、随俯仰转动的相机（{s} 坐标，z 向上）
    const mat = (c) => new T.MeshStandardMaterial({ color: c });
    const rig = new T.Group(), pan = new T.Group(), tilt = new T.Group();
    const foot = new T.Mesh(new T.CylinderGeometry(0.06, 0.08, 0.3, 24), mat(0x6b7780)); foot.rotation.x = Math.PI / 2; foot.position.z = 0.15;
    const yoke = new T.Mesh(new T.BoxGeometry(0.06, 0.2, 0.12), mat(0x9aa6ad)); yoke.position.z = 0.06;
    const body = new T.Mesh(new T.BoxGeometry(0.22, 0.09, 0.09), mat(0x1f3a5f)); body.position.x = 0.05;
    const lens = new T.Mesh(new T.CylinderGeometry(0.035, 0.035, 0.06, 24), mat(0x111111)); lens.rotation.z = Math.PI / 2; lens.position.x = 0.19;
    const mark = new T.Mesh(new T.BoxGeometry(0.05, 0.03, 0.02), mat(0xb8860b)); mark.position.set(0.0, 0, 0.055);   // 机身顶部的标记：看出是否倒过来
    tilt.add(body, lens, mark); tilt.position.z = 0.42;
    pan.add(yoke, tilt); pan.position.z = 0.3;
    rig.add(foot, pan); rig.visible = false;
    root.updateMatrixWorld(true);
    const holder = new T.Group();                // 与 {s} 重合、但不随机械臂一起隐藏的坐标系
    holder.applyMatrix4(root.matrixWorld.clone());
    api.st.scene.add(holder);
    holder.add(rig);
    const c0 = new T.Vector3().setFromMatrixPosition(root.matrixWorld);
    api.m.camFrame = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(c0.x - 0.7, 0, c0.z - 0.7), new T.Vector3(c0.x + 0.7, 1.4, c0.z + 0.7)) };
    keep.rig = rig; keep.pan = pan; keep.tilt = tilt;
    keep.star = new T.Mesh(new T.SphereGeometry(0.03, 16, 12), new T.MeshBasicMaterial({ color: 0xffc107 }));
    keep.star.visible = false; holder.add(keep.star);
    keep.viewed = null;
  },
  reset(api, s) {},
  readouts(api, s) {
    const arm = api.m["B-ARM-UR5E"];
    if (!arm) return [];
    arm.set(this.pose(api));
    const d = this.dir(api), deg = (v) => (v * 180 / Math.PI).toFixed(2) + "°";
    if (api.scene === "wrist") {
      const ss = this.wristSols(d), o = this.S(arm, "wrist_3_link", [0, 0, 0]), x = this.S(arm, "wrist_3_link", [1, 0, 0]);
      const xb = [x[0] - o[0], x[1] - o[1], x[2] - o[2]], c = xb[0] * d[0] + xb[1] * d[1] + xb[2] * d[2];
      const err = Math.acos(Math.max(-1, Math.min(1, c))) * 180 / Math.PI;
      const ex = Math.abs(api.p.az - 45) < 0.6 && Math.abs(api.p.el + 35.26) < 0.6;
      if (ex && err < 0.01) { api.done("ex"); if (api.p.sol === 1) api.done("flip"); }
      return [[["目标方向 d", "target direction d"], `(${d.map((v) => api.fmt(v, 3)).join(", ")})`],
              [["解 0 (θ₅, θ₆)", "solution 0 (θ₅, θ₆)"], `(${deg(ss[0].t5)}, ${deg(ss[0].t6)})`],
              [["解 1 (θ₅, θ₆)", "solution 1 (θ₅, θ₆)"], `(${deg(ss[1].t5)}, ${deg(ss[1].t6)})`],
              [["模型末端 x 轴与 d 的夹角", "angle between model x_b and d"], api.fmt(err, 4) + "°"]];
    }
    if (api.scene === "elbow") {
      const ss = this.elbowSols(api.p.delta), a = this.S(arm, "upper_arm_link", [0, 0, 0]), b = this.S(arm, "wrist_1_link", [0, 0, 0]);
      const dist = Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
      if (ss.length && Math.abs(api.p.delta - 0.6) < 1e-9 && Math.abs(dist - 0.6) < 1e-6) api.done("elbow");
      if (ss.length && api.p.delta > 0.827 && Math.abs(ss[0]) < 3 * Math.PI / 180) api.done("merge");
      return [[["解的个数", "number of solutions"], String(ss.length)],
              [["θ₃ 的解", "solutions for θ₃"], ss.length ? ss.map(deg).join(api.T("、", ", ")) : api.T("无解", "none")],
              [["模型上 |q₄ − q₂|", "|q₄ − q₂| on the model"], api.fmt(dist, 4) + " m"]];
    }
    const cs = this.camSols(d), c = cs[api.p.sol];
    if (Math.abs(api.p.az - 120) < 0.6 && Math.abs(api.p.el - 30) < 0.6 && api.p.sol === 1) api.done("cam");
    return [[["解 0（方位, 仰角）", "solution 0 (pan, tilt)"], `(${deg(cs[0].a)}, ${deg(cs[0].b)})`],
            [["解 1（方位, 仰角）", "solution 1 (pan, tilt)"], `(${deg(cs[1].a)}, ${deg(cs[1].b)})`],
            [["当前", "current"], api.p.sol === 1 ? api.T("倒过来", "upside down") : api.T("正着", "upright")],
            [["选中的解", "chosen"], `(${deg(c.a)}, ${deg(c.b)})`]];
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], K = api.keep, T = api.three;
    arm.set(this.pose(api));
    const cam = api.scene === "cam";
    arm.visible(!cam); K.rig.visible = cam; K.star.visible = cam;
    if (K.viewed !== api.scene) { K.viewed = api.scene; if (cam) api.view(50, 18, 1.1, api.m.camFrame); else api.view(35, 22, 0.8, arm); }
    const d = this.dir(api), D = new T.Vector3(d[0], d[1], d[2]);
    K.target.visible = api.scene === "wrist"; K.xb.visible = api.scene === "wrist"; K.seg.visible = api.scene === "elbow";
    if (api.scene === "wrist") {
      const f = this.S(arm, "wrist_3_link", [0, 0.1, 0]), o = this.S(arm, "wrist_3_link", [0, 0, 0]), x = this.S(arm, "wrist_3_link", [1, 0, 0]);
      K.target.position.set(f[0], f[1], f[2]); K.target.setDirection(D);
      K.xb.position.set(f[0], f[1], f[2]); K.xb.setDirection(new T.Vector3(x[0] - o[0], x[1] - o[1], x[2] - o[2]).normalize());
    }
    if (api.scene === "elbow") {
      const a = this.S(arm, "upper_arm_link", [0, 0, 0]), b = this.S(arm, "wrist_1_link", [0, 0, 0]);
      K.seg.geometry.setFromPoints([new T.Vector3(...a), new T.Vector3(...b)]);
    }
    if (cam) {
      const c = this.camSols(d)[api.p.sol];
      K.pan.rotation.z = c.a; K.tilt.rotation.y = -c.b;
      K.star.position.set(0.9 * d[0], 0.9 * d[1], 0.72 + 0.9 * d[2]);
    }
  },
});
