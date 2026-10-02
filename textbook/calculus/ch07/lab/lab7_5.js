// 实验 7.5 链式法则：电机、减速器与 UR5e 的上臂（配 7.5 节）。UR5e（零件库 2026.10.9 版），
// 上臂与水平面的夹角 θ = −(shoulder_lift_joint)，肘关节固定为 90°；“测得”的上升速度由模型中肘关节中心的高度差分得到。
WQ.lab({
  title: ["实验 7.5 链式法则：电机、减速器与 UR5e 的上臂", "Lab 7.5 The chain rule: motor, reducer and the UR5e upper arm"],
  goal: ["改变电机转速、减速比和上臂角度，比较从模型测得的肘关节中心上升速度与三级变化率之积 l₁cos θ · (1/N) · ω_m。",
         "Change the motor speed, the reduction ratio and the upper-arm angle; compare the elbow's rising speed measured on the model with the product of the three rates l₁cos θ · (1/N) · ω_m."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "robot", robot: true, name: ["UR5e 肩关节", "UR5e shoulder"],
      problem: { title: ["机器人问题：肘关节中心上升得多快？", "Robot problem: how fast does the elbow rise?"],
                 text: ["电机经减速器带动肩关节，上臂长 0.425 m。电机转速、减速比、上臂角度各自怎样影响肘关节中心的上升速度？",
                        "The motor drives the shoulder through a reducer; the upper arm is 0.425 m long. How do motor speed, ratio and arm angle each affect how fast the elbow rises?"] } },
    { id: "life", name: ["生活中的例子：登山时的气温", "Everyday example: temperature on a climb"],
      problem: { title: ["生活中的例子：登山时的气温", "Everyday example: temperature on a climb"],
                 text: ["气温随海拔每升高 1 km 下降约 6 °C。爬升得越快，感到的降温越快：降温速度 = (dT/dH)·(dH/dt)。在本场景中，把电机转速看作爬升速度的类比，体会“变化率相乘”。",
                        "Air cools by about 6 °C per km of height. The faster you climb, the faster it cools: (dT/dH)·(dH/dt). Here, read the motor speed as the climbing rate and feel how rates multiply."] } },
  ],
  params: [
    { id: "rpm", name: ["电机转速 n", "Motor speed n"], min: 0, max: 3000, step: 10, value: 1500, unit: "r/min", digits: 0 },
    { id: "N", name: ["减速比 N", "Reduction ratio N"], min: 30, max: 160, step: 1, value: 60, digits: 0 },
    { id: "th", name: ["上臂与水平面的夹角 θ", "Upper-arm elevation θ"], min: -10, max: 100, step: 0.5, value: 30, unit: "°", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["转动（慢放 5 倍）", "Turn (5× slow motion)"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "limit", robot: true, text: ["电机以 3000 r/min 转动时，选择减速比，使关节角速度不超过 180°/s。", "With the motor at 3000 r/min, choose a ratio so the joint stays within 180°/s."],
      demo: { scene: "robot", set: { rpm: 3000, N: 101 }, press: [], wait: 1 } },
    { id: "zero", robot: true, text: ["找出上臂在什么角度时，肘关节中心的上升速度为零。", "Find the arm angle at which the elbow does not rise at all."],
      demo: { scene: "robot", set: { th: 90 }, press: [], wait: 1 } },
    { id: "one", robot: true, text: ["让肘关节中心的上升速度达到 1 m/s。", "Make the elbow rise at 1 m/s."],
      demo: { scene: "robot", set: { rpm: 3000, N: 101, th: 20 }, press: [], wait: 1 } },
  ],
  think: ["减速比加倍时，关节转速减半；若电机力矩不变，关节力矩会怎样？功率呢？", "Doubling the ratio halves the joint speed; with the same motor torque, what happens to the joint torque? And the power?"],

  names: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  pose(api, th) { const d = Math.PI / 180; return [0, -th * d, Math.PI / 2, -Math.PI / 2, -Math.PI / 2, 0]; },
  put(arm, q) { const o = {}; this.names.forEach((n, i) => (o[n] = q[i])); arm.set(o); },
  elbowZ(api, th) { const arm = api.m["B-ARM-UR5E"]; this.put(arm, this.pose(api, th)); return arm.local("forearm_link", [0, 0, 0])[2]; },
  angle(api, s) { return api.p.th + (s.dth || 0); },
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"];
    api.axes(arm, "forearm_link", 0.08);
    keep.trace = api.trace(0xe8913a);
    api.view(35, 16, 0.6);
  },
  reset(api, s) { s.dth = 0; if (api.keep.trace) api.keep.trace.clear(); },
  update(dt, api, s) {
    const wj = api.p.rpm * 2 * Math.PI / 60 / api.p.N;          // rad/s
    s.dth += wj * 180 / Math.PI * dt * 0.2;                      // slow motion: 1/5 of real speed
    if (api.p.th + s.dth >= 100) api.stop();
  },
  readouts(api, s) {
    if (!api.m || !api.m["B-ARM-UR5E"]) return [];
    const th = this.angle(api, s), wm = api.p.rpm * 2 * Math.PI / 60, wj = wm / api.p.N, d = 0.01;
    const dzdth = (this.elbowZ(api, th + d) - this.elbowZ(api, th - d)) / (2 * d * Math.PI / 180);   // m/rad, from the model
    const l1 = 0.425, chain = l1 * Math.cos(th * Math.PI / 180) * wj, measured = dzdth * wj;
    if (api.p.rpm >= 2990 && wj <= Math.PI + 1e-9) api.done("limit");
    if (Math.abs(th - 90) < 0.6) api.done("zero");
    if (measured >= 1) api.done("one");
    return [[["电机角速度 ω_m", "Motor speed ω_m"], api.fmt(wm, 2) + " rad/s"],
            [["关节角速度 ω_m/N", "Joint speed ω_m/N"], api.fmt(wj, 4) + " rad/s（" + api.fmt(wj * 180 / Math.PI, 1) + "°/s）"],
            [["dy/dθ = l₁cos θ", "dy/dθ = l₁cos θ"], api.fmt(l1 * Math.cos(th * Math.PI / 180), 4) + " m/rad"],
            [["三级变化率之积", "Product of the three rates"], api.fmt(chain, 4) + " m/s"],
            [["由模型测得的上升速度", "Rising speed measured on the model"], api.fmt(measured, 4) + " m/s"]];
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"];
    this.put(arm, this.pose(api, this.angle(api, s)));
    if (api.running) api.keep.trace.add(arm.point("forearm_link"));
  },
});
