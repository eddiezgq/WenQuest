// 实验 10.4 云台相机跟踪 AGV（配 10.4 节）。零件库差速小车 B-EDU-DIFF 沿直线行驶，车间顶部离地 H 处装一台云台相机。
// 云台坐标系 {g}：原点在相机（两轴交点），z 竖直向上，x 沿小车行驶方向。小车在 {g} 中位于 (x, d, −H)，x 从 −1.5 m 匀速走到 +1.5 m。
// 方位角 φ = atan2(d, x)，极角 θ = atan2(√(x² + d²), −H)；φ̇ = −v d/(x² + d²)（式 (10.4.13)），θ̇ = −H x v / (ρ r²)，ρ = √(x² + d²)。
// 三维场景 y 轴向上：{g} 中的 (x, y, z) 画在 (x, z + H, −y)。
WQ.lab({
  title: ["实验 10.4 云台相机跟踪 AGV", "Lab 10.4 A gimbal camera tracking an AGV"],
  goal: ["让小车从云台下方驶过，读出云台两根轴的角度和角速度；找出水平转动角速度的峰值与偏距的关系，观察锁孔问题。",
         "Drive the cart under the gimbal and read both axes' angles and rates; relate the peak pan rate to the offset and see the keyhole problem."],
  view: "3d",
  models: ["B-EDU-DIFF"],
  scenes: [
    { id: "shop", robot: true, name: ["车间顶部的云台", "Gimbal on the workshop ceiling"],
      problem: { title: ["机器人问题：云台跟得上 AGV 吗", "Robot problem: can the gimbal keep up with the AGV"],
                 text: ["云台离地 3 m，水平转动最高 90°/s。AGV 以 1 m/s 驶过，离正下方最近 0.5 m。",
                        "The gimbal is 3 m up and pans at most 90°/s. The AGV passes at 1 m/s, 0.5 m from straight below at closest."] } },
    { id: "home", name: ["吸顶摄像头看扫地机器人", "Ceiling camera and a robot vacuum"],
      problem: { title: ["生活中的例子：家里的吸顶摄像头", "Everyday example: a home ceiling camera"],
                 text: ["摄像头装在 2.5 m 高的天花板上，跟踪以 0.3 m/s 行驶的扫地机器人。它从摄像头正下方附近经过时会怎样？",
                        "A camera on a 2.5 m ceiling follows a robot vacuum at 0.3 m/s. What happens when it passes almost beneath?"] },
      params: { v: { min: 0.1, max: 0.6, value: 0.3 }, d: { min: 0.05, max: 1.5, value: 0.6 }, H: { min: 2, max: 3, value: 2.5 } } },
  ],
  params: [
    { id: "v", name: ["车速 v", "Speed v"], min: 0.2, max: 2, step: 0.05, value: 1, unit: "m/s", digits: 2 },
    { id: "d", name: ["偏距 d", "Offset d"], min: 0.05, max: 2, step: 0.05, value: 0.5, unit: "m", digits: 2 },
    { id: "H", name: ["相机高度 H", "Camera height H"], min: 1, max: 4, step: 0.5, value: 3, unit: "m", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["行驶", "Drive"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "peak", robot: true, text: ["按算例 10.4.2 设置（v = 1 m/s，d = 0.5 m，H = 3 m），行驶一次，读出水平转动的最大角速度。",
                                      "Set Example 10.4.2 (v = 1 m/s, d = 0.5 m, H = 3 m), drive once and read the largest pan rate."],
      demo: { scene: "shop", set: { v: 1, d: 0.5, H: 3 }, press: ["start"], wait: 40 } },
    { id: "limit", robot: true, text: ["车速 1 m/s 不变，调节偏距（不超过 0.8 m），使最大水平转动角速度不超过 90°/s。",
                                       "Keep 1 m/s and choose an offset (at most 0.8 m) so that the largest pan rate stays within 90°/s."],
      demo: { scene: "shop", set: { v: 1, d: 0.65, H: 3 }, press: ["start"], wait: 40 } },
    { id: "keyhole", robot: true, text: ["把偏距调到 0.1 m 以下再行驶：水平转动角速度的峰值超过 500°/s，这就是锁孔问题。",
                                         "Set the offset to 0.1 m or less and drive: the pan rate peaks above 500°/s, the keyhole problem."],
      demo: { scene: "shop", set: { v: 1, d: 0.1, H: 3 }, press: ["start"], wait: 40 } },
    { id: "height", robot: true, text: ["v = 1 m/s、d = 0.5 m，把相机高度改为 3 m 以外的值再行驶：最大水平转动角速度不变。",
                                        "With v = 1 m/s and d = 0.5 m change the camera height away from 3 m and drive: the largest pan rate stays the same."],
      demo: { scene: "shop", set: { v: 1, d: 0.5, H: 1.5 }, press: ["start"], wait: 40 } },
  ],
  think: ["为什么最大水平转动角速度与相机高度无关，而最大俯仰角速度与高度有关？怎样安装云台才能避开锁孔？",
          "Why is the largest pan rate independent of the camera height while the largest tilt rate is not? How would you mount the gimbal to avoid the keyhole?"],

  X0: 1.5,
  ang(api, x) {
    const d = api.p.d, H = api.p.H, v = api.p.v, rh = Math.hypot(x, d), r = Math.hypot(rh, H);
    return { phi: Math.atan2(d, x), th: Math.atan2(rh, -H), phd: -v * d / (rh * rh), thd: -H * x * v / (rh * r * r) };
  },
  setup3d(api, keep) {
    const T = api.three, st = api.st;
    const g = new T.Group(); st.scene.add(g); keep.g = g;
    const floor = new T.Mesh(new T.BoxGeometry(9, 0.02, 4.4), new T.MeshStandardMaterial({ color: 0xe6e9ec }));
    floor.position.set(0, -0.011, -0.6); g.add(floor);
    keep.lane = new T.Mesh(new T.BoxGeometry(8.4, 0.004, 0.03), new T.MeshStandardMaterial({ color: 0xe07b00 })); g.add(keep.lane);
    keep.post = new T.Mesh(new T.CylinderGeometry(0.03, 0.03, 0.3, 16), new T.MeshStandardMaterial({ color: 0x555555 })); g.add(keep.post);
    keep.pan = new T.Group(); g.add(keep.pan);
    const yoke = new T.Mesh(new T.CylinderGeometry(0.09, 0.09, 0.06, 24), new T.MeshStandardMaterial({ color: 0x4a5560 }));
    keep.pan.add(yoke);
    keep.cam = new T.Group(); g.add(keep.cam);
    const body = new T.Mesh(new T.BoxGeometry(0.12, 0.1, 0.22), new T.MeshStandardMaterial({ color: 0x2b3640 }));
    const lens = new T.Mesh(new T.CylinderGeometry(0.035, 0.035, 0.05, 20), new T.MeshStandardMaterial({ color: 0x111111 }));
    lens.rotation.x = Math.PI / 2; lens.position.z = 0.13;
    keep.cam.add(body, lens);
    const geo = new T.BufferGeometry().setFromPoints([new T.Vector3(), new T.Vector3(1, 0, 0)]);
    keep.sight = new T.Line(geo, new T.LineBasicMaterial({ color: 0xd4a017 })); g.add(keep.sight);
    keep.box = () => new T.Box3(new T.Vector3(-4.3, 0, -2.4), new T.Vector3(4.3, api.p.H + 0.3, 0.6));
    api.m.frameBox = { entry: { robot: {} }, holder: { visible: false }, box: () => keep.box() };
    const car = api.m["B-EDU-DIFF"];
    car.place(-this.X0, 0, 0);
    keep.carY = car.holder.position.y;
    keep.shown = "";
  },
  reset(api, s) { s.x = -this.X0; s.peak = 0; s.thpeak = 0; s.done = false; s.wheel = 0; },
  update(dt, api, s) {
    const x0 = s.x;
    s.x += api.p.v * dt; s.wheel += api.p.v * dt / 0.05;
    const a = this.ang(api, s.x);
    s.peak = Math.max(s.peak, Math.abs(a.phd) * 180 / Math.PI);
    s.thpeak = Math.max(s.thpeak, Math.abs(a.thd) * 180 / Math.PI);
    if (x0 < 0 && s.x >= 0) s.peak = Math.max(s.peak, api.p.v / api.p.d * 180 / Math.PI);   // 恰好经过最近点
    if (s.x >= this.X0) {
      s.done = true; api.stop();
      const v = api.p.v, d = api.p.d, H = api.p.H, P = s.peak, exact = v / d * 180 / Math.PI;
      if (api.scene === "shop" && Math.abs(v - 1) < 1e-9) {
        if (Math.abs(d - 0.5) < 1e-9 && Math.abs(H - 3) < 1e-9 && Math.abs(P - exact) < 1) api.done("peak");
        if (d <= 0.8 + 1e-9 && P <= 90) api.done("limit");
        if (d <= 0.1 + 1e-9 && P > 500) api.done("keyhole");
        if (Math.abs(d - 0.5) < 1e-9 && Math.abs(H - 3) >= 0.5 - 1e-9 && Math.abs(P - exact) < 1) api.done("height");
      }
    }
  },
  readouts(api, s) {
    const xx = s.x == null ? -this.X0 : s.x, a = this.ang(api, xx), D = 180 / Math.PI;
    return [[["小车在 {g} 中", "cart in {g}"], `(${api.fmt(xx, 2)}, ${api.fmt(api.p.d, 2)}, ${api.fmt(-api.p.H, 1)}) m`],
            [["方位角 φ / 极角 θ", "azimuth φ / polar angle θ"], `${api.fmt(a.phi * D, 1)}° / ${api.fmt(a.th * D, 1)}°`],
            [["方位角速度 φ̇", "pan rate φ̇"], api.fmt(a.phd * D, 1) + " °/s"],
            [["俯仰角速度 θ̇", "tilt rate θ̇"], api.fmt(a.thd * D, 1) + " °/s"],
            [["本次最大 |φ̇|", "largest |φ̇| this run"], api.fmt(s.peak || 0, 1) + " °/s"],
            [["本次最大 |θ̇|", "largest |θ̇| this run"], api.fmt(s.thpeak || 0, 1) + " °/s"],
            [["90°/s 限速", "90°/s limit"], (s.peak || 0) <= 90 ? api.T("满足", "met") : api.T("超限，跟丢", "exceeded: target lost")]];
  },
  draw(api, s) {
    const K = api.keep, T = api.three, car = api.m["B-EDU-DIFF"], H = api.p.H, d = api.p.d;
    if (K.shown !== api.scene + H) { K.shown = api.scene + H; api.view(28, 24, 0.95, api.m.frameBox); }
    const x = s.x == null ? -this.X0 : s.x;
    car.holder.position.set(x, K.carY, -d);
    car.holder.rotation.set(0, 0, 0);
    car.set({ left_wheel_joint: s.wheel || 0, right_wheel_joint: s.wheel || 0 });
    K.lane.position.set(0, 0.002, -d);
    K.post.position.set(0, H + 0.2, 0);
    const a = this.ang(api, x);
    K.pan.position.set(0, H + 0.03, 0); K.pan.rotation.set(0, a.phi, 0);
    K.cam.position.set(0, H - 0.05, 0);
    const tgt = new T.Vector3(x, 0.05, -d);
    K.cam.lookAt(tgt);
    const pos = K.sight.geometry.attributes.position;
    pos.setXYZ(0, 0, H - 0.05, 0); pos.setXYZ(1, tgt.x, tgt.y, tgt.z); pos.needsUpdate = true;
    K.sight.geometry.computeBoundingSphere();
  },
});
