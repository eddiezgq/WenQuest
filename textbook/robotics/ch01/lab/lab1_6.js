// 实验 1.6 驱动五台机器人的关节，认识自由度（配 1.6 节，自由度见 1.4 节）。
// 八个滑块在不同场景中含义不同，“测量”栏第一行说明当前各滑块的含义。
// 机械臂：变量 1 选 UR5e/Panda，变量 2–8 为关节 1–7（°）；四足：变量 1 选腿，变量 2–4 为髋、大腿、小腿（°）；
// 移动与空中：变量 1、2 为 AGV 左右轮转速（rad/s，按“开始”行驶），变量 3–8 为四旋翼机体的 x、y、z（m）与横滚、俯仰、偏航（°）；
// 生活场景：G1 右臂的 7 个关节（°），代表人的手臂。
// 坐标：模型的 Z 向上；三维引擎的世界坐标 Y 向上，模型 (x, y, z) 对应世界 (x, z, −y)。
WQ.lab({
  title: ["实验 1.6 驱动五台机器人的关节，认识自由度", "Lab 1.6 Drive the joints of the five robots: degrees of freedom"],
  goal: ["逐一驱动 UR5e、Panda、Go2、AGV 和四旋翼，数一数各需要几个数才能确定它们的位置，体会关节、基座与自由度的关系。",
         "Drive UR5e, Panda, Go2, the AGV and the quadrotor in turn; count how many numbers fix each one's position, and see how joints, base and DOF relate."],
  view: "3d",
  models: ["B-ARM-UR5E", "B-ARM-PANDA", "B-LEG-GO2", "B-EDU-DIFF", "B-UAV-X2", "B-HUM-G1"],
  scenes: [
    { id: "arm", robot: true, name: ["机械臂 UR5e 与 Panda", "Arms UR5e and Panda"],
      problem: { title: ["机器人问题：末端要到任意位置和姿态，要几个关节", "Robot problem: how many joints for any position and orientation"],
                 text: ["末端执行器是空间中的刚体，有 6 个自由度。UR5e 恰好 6 个关节；Panda 有 7 个，多出一个。",
                        "The end-effector is a rigid body with 6 DOF. UR5e has exactly 6 joints; Panda has 7, one more."] },
      params: { s0: { min: 0, max: 1, step: 1, value: 0 }, q1: { min: -180, max: 180, value: -90 }, q2: { min: -180, max: 180, value: -90 },
                q3: { min: -180, max: 180, value: 90 }, q4: { min: -180, max: 180, value: -90 }, q5: { min: -180, max: 180, value: -90 },
                q6: { min: -180, max: 180, value: 0 }, q7: { min: -180, max: 180, value: 0 } } },
    { id: "go2", robot: true, name: ["四足 Go2", "Quadruped Go2"], hide: ["q4", "q5", "q6", "q7"],
      problem: { title: ["机器人问题：抬起一条腿", "Robot problem: lift one leg"],
                 text: ["每条腿 3 个关节，四条腿 12 个；机身是自由刚体，还有 6 个自由度，共 18 个，电机只有 12 台。",
                        "Three joints per leg, 12 in all; the body is a free rigid body with 6 more DOF: 18 in all, with 12 motors."] },
      params: { s0: { min: 0, max: 3, step: 1, value: 0 }, q1: { min: -48, max: 48, value: 0 }, q2: { min: -90, max: 200, value: 52 },
                q3: { min: -156, max: -48, value: -103 } } },
    { id: "mob", robot: true, name: ["移动与空中：AGV 与四旋翼", "Mobile and aerial: AGV and quadrotor"],
      problem: { title: ["机器人问题：没有关节的四旋翼有几个自由度", "Robot problem: how many DOF has a quadrotor with no joints"],
                 text: ["AGV 只有两个车轮，车体在地面上却有 3 个自由度；四旋翼没有关节，机体在空中有 6 个自由度，只有 4 个推力。",
                        "The AGV has two wheels but its body has 3 DOF on the floor; the quadrotor has no joints, 6 DOF in the air and only 4 thrusts."] },
      params: { s0: { min: -20, max: 20, step: 1, value: 0 }, q1: { min: -20, max: 20, step: 1, value: 0 }, q2: { min: -1.5, max: 1.5, step: 0.05, value: 0 },
                q3: { min: -1.5, max: 1.5, step: 0.05, value: 0 }, q4: { min: 0, max: 2, step: 0.05, value: 0.5 },
                q5: { min: -45, max: 45, value: 0 }, q6: { min: -45, max: 45, value: 0 }, q7: { min: -180, max: 180, value: 0 } } },
    { id: "life", name: ["生活：人的手臂", "Everyday: the human arm"],
      problem: { title: ["生活中的例子：人的手臂有几个自由度", "Everyday example: how many DOF has your arm"],
                 text: ["肩 3 个、肘 1 个、腕 3 个，共 7 个，与 Panda 相同。这里用仿人机器人 G1 的右臂代表人的手臂。",
                        "Shoulder 3, elbow 1, wrist 3: 7, like Panda. The right arm of the G1 humanoid stands for a human arm."] },
      hide: ["s0"],
      params: { q1: { min: -177, max: 153, value: 11 }, q2: { min: -129, max: 91, value: -11 }, q3: { min: -150, max: 150, value: 0 },
                q4: { min: -60, max: 120, value: 73 }, q5: { min: -113, max: 113, value: 0 }, q6: { min: -92, max: 92, value: 0 },
                q7: { min: -92, max: 92, value: 0 } } },
  ],
  params: [
    { id: "s0", name: ["变量 1", "Variable 1"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "q1", name: ["变量 2", "Variable 2"], min: -180, max: 180, step: 1, value: 0, digits: 0 },
    { id: "q2", name: ["变量 3", "Variable 3"], min: -180, max: 180, step: 1, value: 0, digits: 2 },
    { id: "q3", name: ["变量 4", "Variable 4"], min: -180, max: 180, step: 1, value: 0, digits: 2 },
    { id: "q4", name: ["变量 5", "Variable 5"], min: -180, max: 180, step: 1, value: 0, digits: 2 },
    { id: "q5", name: ["变量 6", "Variable 6"], min: -180, max: 180, step: 1, value: 0, digits: 0 },
    { id: "q6", name: ["变量 7", "Variable 7"], min: -180, max: 180, step: 1, value: 0, digits: 0 },
    { id: "q7", name: ["变量 8", "Variable 8"], min: -180, max: 180, step: 1, value: 0, digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始（AGV 行驶）", "Start (AGV drives)"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "zero", robot: true, text: ["把 UR5e 的六个关节都设为 0（零位），读出法兰中心到基座轴线的水平距离，与工作半径 850 mm 比较。",
                                      "Set all six UR5e joints to 0 (home); read the horizontal distance from the flange centre to the base axis and compare it with the 850 mm reach."],
      demo: { scene: "arm", set: { s0: 0, q1: 0, q2: 0, q3: 0, q4: 0, q5: 0, q6: 0 }, press: [], wait: 1 } },
    { id: "foot", robot: true, text: ["选择 Go2 的一条腿，把它的足端抬高 5 cm 以上。", "Pick one leg of Go2 and lift its foot by more than 5 cm."],
      demo: { scene: "go2", set: { s0: 0, q1: 0, q2: 100, q3: -120 }, press: [], wait: 1 } },
    { id: "spin", robot: true, text: ["让 AGV 两轮反向转动，原地转一圈（车体中心移动不超过 5 cm）。", "Turn the AGV's wheels in opposite directions so it spins once on the spot (centre moves less than 5 cm)."],
      demo: { scene: "mob", set: { s0: -20, q1: 20 }, press: ["start"], wait: 20 } },
    { id: "fly", robot: true, text: ["用六个变量把四旋翼放到 x = 0.5 m、y = 0、离地 1.0 m 处，并偏航 90°。", "With six variables put the quadrotor at x = 0.5 m, y = 0, 1.0 m up, yawed 90°."],
      demo: { scene: "mob", set: { q2: 0.5, q3: 0, q4: 1.0, q5: 0, q6: 0, q7: 90 }, press: [], wait: 1 } },
    { id: "hand", text: ["用人手臂的七个关节把手举过头顶。", "Use the seven arm joints to raise the hand above the head."],
      demo: { scene: "life", set: { q1: -160 }, press: [], wait: 1 } },
  ],
  think: ["UR5e 有 6 个关节，Go2 有 12 个关节，四旋翼没有关节。它们的自由度分别是多少？执行器的个数与自由度相比，哪些机器人是欠驱动的？",
          "UR5e has 6 joints, Go2 12, the quadrotor none. What are their DOF? Comparing actuators with DOF, which robots are underactuated?"],

  UR: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  PA: ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6", "joint7"],
  LEGS: ["FL", "FR", "RL", "RR"],
  ARM: ["right_shoulder_pitch_joint", "right_shoulder_roll_joint", "right_shoulder_yaw_joint", "right_elbow_joint",
        "right_wrist_roll_joint", "right_wrist_pitch_joint", "right_wrist_yaw_joint"],
  R_W: 0.05, B_W: 0.26, PELVIS: 0.793, HEAD: 1.32,

  clampSet(h, names, degs) {
    const o = {};
    names.forEach((n, i) => {
      const j = h.joints[n];
      let q = (degs[i] || 0) * Math.PI / 180;
      if (j && Number.isFinite(j.lower) && Number.isFinite(j.upper)) q = Math.min(j.upper, Math.max(j.lower, q));
      o[n] = q;
    });
    h.set(o);
    return o;
  },
  // 模型坐标系中的姿态（Z-Y-X：偏航、俯仰、横滚）换到三维引擎的世界坐标（Y 向上）
  worldQuat(api, roll, pitch, yaw) {
    const T = api.three, c = Math.cos, s = Math.sin;
    const R = [[c(yaw) * c(pitch), c(yaw) * s(pitch) * s(roll) - s(yaw) * c(roll), c(yaw) * s(pitch) * c(roll) + s(yaw) * s(roll)],
               [s(yaw) * c(pitch), s(yaw) * s(pitch) * s(roll) + c(yaw) * c(roll), s(yaw) * s(pitch) * c(roll) - c(yaw) * s(roll)],
               [-s(pitch), c(pitch) * s(roll), c(pitch) * c(roll)]];
    const C = [[1, 0, 0], [0, 0, 1], [0, -1, 0]];                    // 模型 → 世界
    const m = (A, B) => A.map((r) => [0, 1, 2].map((k) => r[0] * B[0][k] + r[1] * B[1][k] + r[2] * B[2][k]));
    const Ct = [[1, 0, 0], [0, 0, -1], [0, 1, 0]];
    const W = m(m(C, R), Ct);
    const M = new T.Matrix4().set(W[0][0], W[0][1], W[0][2], 0, W[1][0], W[1][1], W[1][2], 0, W[2][0], W[2][1], W[2][2], 0, 0, 0, 0, 1);
    return new T.Quaternion().setFromRotationMatrix(M);
  },

  setup3d(api, keep) {
    const T = api.three, m = api.m;
    m["B-ARM-UR5E"].place(0, 0);
    m["B-ARM-PANDA"].place(0, 0);
    m["B-LEG-GO2"].place(0, 0);
    m["B-HUM-G1"].place(0, 0);
    m["B-EDU-DIFF"].place(-0.6, 0);
    m["B-UAV-X2"].place(0.6, 0);
    keep.agv0 = m["B-EDU-DIFF"].holder.position.clone();
    keep.x20 = m["B-UAV-X2"].holder.position.clone();
    api.axes(m["B-ARM-UR5E"], "base", 0.15);
    api.axes(m["B-ARM-PANDA"], "link0", 0.15);
    api.axes(m["B-LEG-GO2"], "base", 0.15);
    api.axes(m["B-UAV-X2"], "x2", 0.12);
    api.axes(m["B-EDU-DIFF"], "chassis", 0.12);
    // 移动场景的取景框：AGV 与四旋翼的活动范围
    const box = new T.Box3(new T.Vector3(-1.3, 0, -0.9), new T.Vector3(1.5, 1.2, 0.9));
    m.mobFrame = { entry: { robot: {} }, box: () => box.clone(), holder: { visible: false } };
    const abox = new T.Box3(new T.Vector3(-0.95, 0, -0.95), new T.Vector3(0.95, 1.15, 0.95));    // 机械臂的工作半径约 0.85 m
    m.armFrame = { entry: { robot: {} }, box: () => abox.clone(), holder: { visible: false } };
    keep.shown = null;
    keep.trace = api.trace(0xd9822b);
  },
  reset(api, s) {
    s.agv = { x: 0, y: 0, h: 0, wl: 0, wr: 0, turn: 0 };
    if (api.keep && api.keep.trace) api.keep.trace.clear();
  },
  update(dt, api, s) {
    if (api.scene !== "mob") { api.stop(); return; }
    const a = s.agv, wl = api.p.s0, wr = api.p.q1;
    const v = this.R_W * (wr + wl) / 2, om = this.R_W * (wr - wl) / this.B_W;     // 式 (1.6.3)、(1.6.4)
    a.x += v * Math.cos(a.h) * dt;
    a.y += v * Math.sin(a.h) * dt;
    a.h += om * dt;
    a.turn += om * dt;
    a.wl += wl * dt;
    a.wr += wr * dt;
    if (Math.abs(a.turn) >= 2 * Math.PI && Math.hypot(a.x, a.y) < 0.05) api.done("spin");
    if (api.t > 8 || Math.hypot(a.x, a.y) > 1.6) api.stop();
  },

  pose(api, s) {
    const m = api.m, p = api.p, d = Math.PI / 180;
    if (api.scene === "arm") {
      if (p.s0 < 0.5) this.clampSet(m["B-ARM-UR5E"], this.UR, [p.q1, p.q2, p.q3, p.q4, p.q5, p.q6]);
      else this.clampSet(m["B-ARM-PANDA"], this.PA, [p.q1, p.q2, p.q3, p.q4, p.q5, p.q6, p.q7]);
    } else if (api.scene === "go2") {
      const go = m["B-LEG-GO2"], rest = go.entry.rest, o = {};
      Object.keys(rest).forEach((k) => { o[k] = rest[k]; });
      const leg = this.LEGS[Math.max(0, Math.min(3, Math.round(p.s0)))];
      o[leg + "_hip_joint"] = p.q1 * d; o[leg + "_thigh_joint"] = p.q2 * d; o[leg + "_calf_joint"] = p.q3 * d;
      go.set(o);
      return leg;
    } else if (api.scene === "mob") {
      const a = s.agv || { x: 0, y: 0, h: 0, wl: 0, wr: 0 }, ag = m["B-EDU-DIFF"], x2 = m["B-UAV-X2"];
      ag.set({ left_wheel_joint: a.wl, right_wheel_joint: a.wr });
      ag.holder.position.set(api.keep.agv0.x + a.x, api.keep.agv0.y, api.keep.agv0.z - a.y);
      ag.holder.rotation.set(0, a.h, 0);
      x2.holder.position.set(api.keep.x20.x + p.q2, api.keep.x20.y + p.q4, api.keep.x20.z - p.q3);
      x2.holder.quaternion.copy(this.worldQuat(api, p.q5 * d, p.q6 * d, p.q7 * d));
      x2.holder.updateMatrixWorld(true);
      ag.holder.updateMatrixWorld(true);
    } else {
      this.clampSet(m["B-HUM-G1"], this.ARM, [p.q1, p.q2, p.q3, p.q4, p.q5, p.q6, p.q7]);
    }
    return null;
  },

  readouts(api, s) {
    const m = api.m, p = api.p;
    if (!m["B-ARM-UR5E"] || !m["B-HUM-G1"]) return [];
    const leg = this.pose(api, s), f = (x, n) => api.fmt(x, n);
    if (api.scene === "arm") {
      if (p.s0 < 0.5) {
        const [x, y, z] = m["B-ARM-UR5E"].local("wrist_3_link", [0, 0.1, 0]), r = Math.hypot(x, y);
        if ([p.q1, p.q2, p.q3, p.q4, p.q5, p.q6].every((q) => Math.abs(q) < 0.5)) api.done("zero");
        return [[["滑块", "sliders"], api.T("变量 1：0 = UR5e，1 = Panda；变量 2–7：关节 1–6（°）", "var 1: 0 = UR5e, 1 = Panda; vars 2–7: joints 1–6 (°)")],
                [["UR5e 的自由度", "UR5e DOF"], api.T("6 个转动关节 + 固定基座 0 = 6", "6 revolute joints + fixed base 0 = 6")],
                [["法兰中心 (x, y, z)", "flange centre (x, y, z)"], `(${f(x, 3)}, ${f(y, 3)}, ${f(z, 3)}) m`],
                [["到基座轴线的水平距离", "horizontal distance to the base axis"], f(r, 4) + " m"]];
      }
      const [x, y, z] = m["B-ARM-PANDA"].local("hand", [0, 0, 0.1034]);
      return [[["滑块", "sliders"], api.T("变量 1：0 = UR5e，1 = Panda；变量 2–8：关节 1–7（°），超出限位时停在限位", "var 1: 0 = UR5e, 1 = Panda; vars 2–8: joints 1–7 (°), held at the limits")],
              [["Panda 的自由度", "Panda DOF"], api.T("7 个转动关节 + 手爪 1 = 8；手臂 7，比 6 多 1（冗余）", "7 revolute + gripper 1 = 8; arm 7, one more than 6 (redundant)")],
              [["手爪中心 (x, y, z)", "gripper centre (x, y, z)"], `(${f(x, 3)}, ${f(y, 3)}, ${f(z, 3)}) m`]];
    }
    if (api.scene === "go2") {
      const go = m["B-LEG-GO2"], z = go.local(leg + "_calf", [0, 0, -0.213])[2], lift = z - (-0.2648);
      if (lift > 0.05) api.done("foot");
      return [[["滑块", "sliders"], api.T("变量 1：腿 0 左前、1 右前、2 左后、3 右后；变量 2–4：髋、大腿、小腿（°）", "var 1: leg 0 FL, 1 FR, 2 RL, 3 RR; vars 2–4: hip, thigh, calf (°)")],
              [["Go2 的自由度", "Go2 DOF"], api.T("12 个关节 + 机身 6 = 18；电机 12 台（欠驱动）", "12 joints + body 6 = 18; 12 motors (underactuated)")],
              [["所选的腿", "selected leg"], leg],
              [["足端比站立时抬高", "foot raised above standing"], f(lift * 100, 1) + " cm"]];
    }
    if (api.scene === "mob") {
      const a = s.agv || { x: 0, y: 0, h: 0, turn: 0 }, d = Math.PI / 180;
      if (Math.abs(p.q2 - 0.5) < 0.03 && Math.abs(p.q3) < 0.03 && Math.abs(p.q4 - 1.0) < 0.03 && Math.abs(p.q7 - 90) < 1.5 &&
          Math.abs(p.q5) < 1.5 && Math.abs(p.q6) < 1.5) api.done("fly");
      const v = this.R_W * (p.q1 + p.s0) / 2, om = this.R_W * (p.q1 - p.s0) / this.B_W;
      return [[["滑块", "sliders"], api.T("变量 1、2：AGV 左、右轮转速（rad/s）；变量 3–8：四旋翼 x、y、离地高度（m）与横滚、俯仰、偏航（°）",
                                          "vars 1, 2: AGV left, right wheel speed (rad/s); vars 3–8: quadrotor x, y, height (m), roll, pitch, yaw (°)")],
              [["AGV 的自由度", "AGV DOF"], api.T("2 个车轮 + 车体 3 = 5；电机 2 台", "2 wheels + body 3 = 5; 2 motors")],
              [["AGV 车速 v、角速度 ω", "AGV v, ω"], `${f(v, 2)} m/s, ${f(om, 2)} rad/s`],
              [["AGV 位置与朝向", "AGV position, heading"], `(${f(a.x, 2)}, ${f(a.y, 2)}) m, ${f(a.h / d, 0)}°`],
              [["AGV 累计转过", "AGV total turn"], f(a.turn / d, 0) + "°"],
              [["四旋翼的自由度", "quadrotor DOF"], api.T("没有关节 + 机体 6 = 6；推力 4 个（欠驱动）", "no joints + body 6 = 6; 4 thrusts (underactuated)")]];
    }
    const g1 = m["B-HUM-G1"], hz = g1.local("right_wrist_yaw_link", [0, 0, 0])[2] + this.PELVIS;
    if (hz > this.HEAD) api.done("hand");
    return [[["滑块", "sliders"], api.T("变量 2–8：肩 3 个、肘 1 个、腕 3 个关节（°）", "vars 2–8: shoulder 3, elbow 1, wrist 3 joints (°)")],
            [["手臂的自由度", "arm DOF"], api.T("肩 3 + 肘 1 + 腕 3 = 7，与 Panda 相同", "shoulder 3 + elbow 1 + wrist 3 = 7, like Panda")],
            [["手腕离地高度", "wrist height above floor"], f(hz, 3) + " m"],
            [["身高（头顶）", "height (top of head)"], f(this.HEAD, 2) + " m"]];
  },

  draw(api, s) {
    const m = api.m, sc = api.scene;
    m["B-ARM-UR5E"].holder.visible = sc === "arm" && api.p.s0 < 0.5;
    m["B-ARM-PANDA"].holder.visible = sc === "arm" && api.p.s0 >= 0.5;
    m["B-LEG-GO2"].holder.visible = sc === "go2";
    m["B-EDU-DIFF"].holder.visible = sc === "mob";
    m["B-UAV-X2"].holder.visible = sc === "mob";
    m["B-HUM-G1"].holder.visible = sc === "life";
    const key = sc + (sc === "arm" ? (api.p.s0 < 0.5 ? "u" : "p") : "");
    if (api.keep.shown !== key) {
      api.keep.shown = key;
      const target = sc === "arm" ? m.armFrame : sc === "go2" ? m["B-LEG-GO2"] : sc === "mob" ? m.mobFrame : m["B-HUM-G1"];
      api.view(35, 22, sc === "mob" ? 1.7 : sc === "arm" ? 1.5 : 0.8, target);
    }
    this.pose(api, s);
    if (sc === "mob" && api.running && api.keep.trace) {
      const c = m["B-EDU-DIFF"].holder.position;
      api.keep.trace.add(new api.three.Vector3(c.x, 0.01, c.z));
    }
  },
});
