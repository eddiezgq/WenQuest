// 实验 21.2 加速度、倾角与偏航（配 21.2 节）。
// 零件库 X2（B-UAV-X2）：m = 1.325 kg，质心在模型机体坐标系 (0, 0, 0.054) m。
// 场景“加速度与倾角”：t = p̈ + 𝔤ẑ，f = m‖t‖，z_b = t/‖t‖（式 (21.2.3)）；R 由定理 21.2.1 的构造式 (21.2.5) 求出，
//   欧拉角按式 (21.2.6)；加速度计读数（质心处）为 Rᵀt = (0, 0, f/m)（式 (21.2.11)）。“开始”后 1 s 内由水平姿态转到所求姿态。
// 场景“协调转弯”：水平圆周 p = (ρ cos Ωt, ρ sin Ωt, 1.5)，Ω = v/ρ，机头沿切线；物体角速度按式 (21.2.7)：ω_b = Ω(0, sin φ, cos φ)。
// 生活场景：汽车加速度 a 时，后视镜下挂件的偏角 α = atan(a/𝔤)（挂绳沿 p̈ + 𝔤ẑ 的反方向下垂）。
WQ.lab({
  title: ["实验 21.2 加速度、倾角与偏航", "Lab 21.2 Acceleration, tilt and yaw"],
  goal: ["给定想要的加速度和偏航角，求四旋翼的姿态和总推力；观察协调转弯时的坡度和陀螺仪读数；用汽车里的挂件体会“推力方向由加速度决定”。",
         "From a wanted acceleration and yaw, find the quadrotor's attitude and collective thrust; watch the bank and the gyro readings in a coordinated turn; see with a car's hanging ornament that the thrust direction follows the acceleration."],
  view: "3d",
  models: ["B-UAV-X2"],
  scenes: [
    { id: "acc", robot: true, name: ["加速度与倾角", "Acceleration and tilt"], hide: ["v", "rho", "acar"],
      problem: { title: ["机器人问题：要这样加速，机身该怎样倾斜", "Robot problem: how must the body tilt for this acceleration"],
                 text: ["拖动想要的加速度 (a_x, a_y, a_z) 和偏航角 ψ，按“开始”，X2 转到定理 21.2.1 给出的姿态。蓝色箭头是推力，红色箭头是想要的加速度。",
                        "Set the wanted acceleration (a_x, a_y, a_z) and the yaw ψ, press Start, and X2 turns to the attitude of Theorem 21.2.1. Blue arrow: thrust; red arrow: the wanted acceleration."] } },
    { id: "turn", robot: true, name: ["协调转弯", "Coordinated turn"], hide: ["ax", "ay", "az", "psi", "acar"],
      problem: { title: ["机器人问题：绕设备转圈拍照，陀螺仪读到什么", "Robot problem: circling a machine, what do the gyros read"],
                 text: ["X2 在 1.5 m 高处以车速 v 沿半径 ρ 的水平圆逆时针飞一圈，机头沿飞行方向（机身放大 3 倍画出）。界面给出坡度、总推力和陀螺仪三个轴的读数。",
                        "X2 flies one counter-clockwise lap of radius ρ at speed v, 1.5 m up, nose along the path (drawn 3 times larger). The readouts give the bank, the thrust and the three gyro axes."] } },
    { id: "car", name: ["车内挂件", "Car ornament"], hide: ["ax", "ay", "az", "psi", "v", "rho"],
      problem: { title: ["生活中的例子：后视镜下的挂件", "Everyday example: the ornament under the mirror"],
                 text: ["汽车以加速度 a 行驶 3 s。挂件的绳子沿 p̈ + 𝔤ẑ 的方向（向下看），偏角 α 满足 tan α = a/𝔤，与四旋翼保持高度加速时的倾角相同。",
                        "The car accelerates at a for 3 s. The ornament's string lines up with p̈ + gẑ, and its angle obeys tan α = a/g, the same as the quadrotor's tilt when accelerating at constant height."] } },
  ],
  params: [
    { id: "ax", name: ["加速度 a_x", "acceleration a_x"], min: -6, max: 6, step: 0.1, value: 0, unit: "m/s²", digits: 1 },
    { id: "ay", name: ["加速度 a_y", "acceleration a_y"], min: -6, max: 6, step: 0.1, value: 0, unit: "m/s²", digits: 1 },
    { id: "az", name: ["加速度 a_z", "acceleration a_z"], min: -4, max: 6, step: 0.1, value: 0, unit: "m/s²", digits: 1 },
    { id: "psi", name: ["偏航角 ψ", "yaw ψ"], min: -180, max: 180, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "v", name: ["车速 v", "speed v"], min: 1, max: 8, step: 0.5, value: 4, unit: "m/s", digits: 1 },
    { id: "rho", name: ["半径 ρ", "radius ρ"], min: 2, max: 10, step: 0.5, value: 5, unit: "m", digits: 1 },
    { id: "acar", name: ["汽车加速度 a", "car acceleration a"], min: -5, max: 4, step: 0.1, value: 0, unit: "m/s²", digits: 1 },
  ],
  tasks: [
    { id: "fwd", robot: true, text: ["机头朝前（ψ = 0），以 2 m/s² 向前（a_x）加速、高度不变，按“开始”，读出俯仰角（约 11.5°）。", "Nose forward (ψ = 0), accelerate forward (a_x) at 2 m/s² at constant height, press Start and read the pitch (about 11.5°)."],
      demo: { scene: "acc", set: { ax: 2, ay: 0, az: 0, psi: 0 }, press: ["start"], wait: 12 } },
    { id: "yaw90", robot: true, text: ["加速度不变，把偏航角改为 90°，按“开始”：倾斜变成了横滚，读出横滚角。", "Same acceleration, yaw 90°, press Start: the tilt has become a roll. Read the roll angle."],
      demo: { scene: "acc", set: { ax: 2, ay: 0, az: 0, psi: 90 }, press: ["start"], wait: 12 } },
    { id: "turn", robot: true, text: ["以 4 m/s 沿半径 5 m 的圆飞一圈，读出坡度（约 18.1°）和陀螺仪 y 轴的读数。", "Fly one lap at 4 m/s on a 5 m circle; read the bank (about 18.1°) and the gyro's y axis."],
      demo: { scene: "turn", set: { v: 4, rho: 5 }, press: ["start"], wait: 40 } },
    { id: "car", text: ["让汽车以 2 m/s² 加速，按“开始”，读出挂件的偏角。", "Let the car accelerate at 2 m/s², press Start and read the ornament's angle."],
      demo: { scene: "car", set: { acar: 2 }, press: ["start"], wait: 15 } },
  ],
  think: ["算例 21.2.2 中，偏航角从 0 改为 60°，z_b 不变，但俯仰角和横滚角都变了。哪些量与偏航角无关？加速度计的读数与偏航角有关吗？",
          "In Example 21.2.2, changing the yaw from 0 to 60° keeps z_b but changes pitch and roll. Which quantities do not depend on the yaw? Does the accelerometer reading?"],

  M: 1.325, G: 9.81, CZ: 0.053962,
  // ---------------- 转动
  mul3(A, B) { return A.map((r) => [0, 1, 2].map((k) => r[0] * B[0][k] + r[1] * B[1][k] + r[2] * B[2][k])); },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  norm(a) { return Math.hypot(a[0], a[1], a[2]); },
  eul(psi, th, ph) {
    const c = Math.cos, s = Math.sin;
    return [[c(psi) * c(th), c(psi) * s(th) * s(ph) - s(psi) * c(ph), c(psi) * s(th) * c(ph) + s(psi) * s(ph)],
            [s(psi) * c(th), s(psi) * s(th) * s(ph) + c(psi) * c(ph), s(psi) * s(th) * c(ph) - c(psi) * s(ph)],
            [-s(th), c(th) * s(ph), c(th) * c(ph)]];
  },
  attitude(a, psi) {   // 定理 21.2.1
    const t = [a[0], a[1], a[2] + this.G], nt = this.norm(t), zb = t.map((x) => x / nt);
    const yc = [-Math.sin(psi), Math.cos(psi), 0];
    let xb = this.cross(yc, zb); const nx = this.norm(xb); xb = xb.map((x) => x / nx);
    const yb = this.cross(zb, xb);
    const w = [Math.cos(psi) * zb[0] + Math.sin(psi) * zb[1], -Math.sin(psi) * zb[0] + Math.cos(psi) * zb[1], zb[2]];   // Rot(ẑ, ψ)ᵀ z_b
    const ph = Math.atan2(-w[1], Math.hypot(w[0], w[2])), th = Math.atan2(w[0], w[2]);
    return { R: [[xb[0], yb[0], zb[0]], [xb[1], yb[1], zb[1]], [xb[2], yb[2], zb[2]]], th, ph, f: this.M * nt, nt, zb };
  },
  w2t(api, v) { return new api.three.Vector3(v[0], v[2], -v[1]); },
  place(api, R, p, k = 1) {   // k：画图时机身的放大倍数（协调转弯场景中放大 3 倍，否则在 10 m 的圆上看不清）
    const T = api.three, K = api.keep, h = api.m["B-UAV-X2"];
    const c = [p[0] - k * R[0][2] * this.CZ, p[1] - k * R[1][2] * this.CZ, p[2] - k * R[2][2] * this.CZ];
    const Ts = new T.Matrix4().set(R[0][0], R[0][1], R[0][2], c[0], R[1][0], R[1][1], R[1][2], c[1], R[2][0], R[2][1], R[2][2], c[2], 0, 0, 0, 1);
    K.Cm.clone().multiply(Ts).multiply(new T.Matrix4().makeScale(k, k, k)).multiply(K.MhbInv).decompose(h.holder.position, h.holder.quaternion, h.holder.scale);
    h.holder.updateMatrixWorld(true);
  },
  setup3d(api, keep) {
    const T = api.three, h = api.m["B-UAV-X2"];
    h.place(0, 0);
    h.holder.updateMatrixWorld(true);
    keep.Cm = new T.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1);
    keep.MhbInv = new T.Matrix4().copy(h.holder.matrixWorld).invert().multiply(h.nodes.x2.matrixWorld).invert();
    api.axes(h, "x2", 0.15);
    keep.thrust = new T.ArrowHelper(new T.Vector3(0, 1, 0), new T.Vector3(), 0.3, 0x1f77b4, 0.06, 0.035);
    keep.acc = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(), 0.3, 0xd62728, 0.06, 0.035);
    api.st.scene.add(keep.thrust, keep.acc);
    keep.tr = api.trace(0xe8913a);
    // 汽车（示意）：车身、车窗、后视镜、挂件
    const g = new T.Group(), mat = (c, o) => new T.MeshStandardMaterial({ color: c, transparent: o < 1, opacity: o, roughness: 0.6 });
    const body = new T.Mesh(new T.BoxGeometry(4.2, 0.7, 1.8), mat(0x3b82c4, 1)); body.position.set(0, 0.65, 0); g.add(body);
    const cab = new T.Mesh(new T.BoxGeometry(2.2, 0.65, 1.7), mat(0xbfd6ea, 0.35)); cab.position.set(-0.2, 1.32, 0); g.add(cab);
    [[-1.3, 0.9], [1.3, 0.9], [-1.3, -0.9], [1.3, -0.9]].forEach(([x, z]) => {
      const w = new T.Mesh(new T.CylinderGeometry(0.33, 0.33, 0.22, 20), mat(0x222222, 1)); w.rotation.x = Math.PI / 2; w.position.set(x, 0.33, z); g.add(w);
    });
    const mirror = new T.Mesh(new T.BoxGeometry(0.08, 0.08, 0.3), mat(0x333333, 1)); mirror.position.set(0.75, 1.6, 0); g.add(mirror);
    const pend = new T.Group(); pend.position.set(0.75, 1.56, 0);
    const str = new T.Mesh(new T.CylinderGeometry(0.01, 0.01, 0.45, 6), mat(0x555555, 1)); str.position.set(0, -0.225, 0); pend.add(str);
    const bob = new T.Mesh(new T.SphereGeometry(0.09, 16, 12), mat(0xe8913a, 1)); bob.position.set(0, -0.5, 0); pend.add(bob);
    g.add(pend);
    api.st.scene.add(g);
    keep.car = g; keep.pend = pend;
    api.m.fAcc = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-0.6, 0, -0.6), new T.Vector3(0.6, 1.3, 0.6)) };
    api.m.fTurn = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-6, 0, -6), new T.Vector3(6, 2, 6)) };
    api.m.fCar = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-2.4, 0, -1.2), new T.Vector3(2.4, 1.8, 1.2)) };
    keep.shown = null;
  },
  reset(api, s) {
    s.t = 0; s.k = 0; s.ran = false; s.lap = false;
    const K = api.keep;
    if (!K.Cm) return;
    K.tr.clear();
    if (api.scene === "turn") { const r = api.p.rho; this.place(api, this.eul(Math.PI / 2, 0, 0), [r, 0, 1.5], 3); }
    else this.place(api, this.eul(0, 0, 0), [0, 0, 0.6]);
  },
  start(api, s) { s.t = 0; },
  update(dt, api, s) {
    const d = Math.PI / 180;
    if (api.scene === "acc") {
      s.k = Math.min(1, s.k + dt);
      const A = this.attitude([api.p.ax, api.p.ay, api.p.az], api.p.psi * d);
      const k = s.k * s.k * (3 - 2 * s.k);
      this.place(api, this.eul(api.p.psi * d * k, A.th * k, A.ph * k), [0, 0, 0.6]);
      if (s.k >= 1) { s.ran = true; this.place(api, A.R, [0, 0, 0.6]); api.stop(); }
    } else if (api.scene === "turn") {
      const v = api.p.v, r = api.p.rho, Om = v / r, Tl = 2 * Math.PI / Om;
      s.t = Math.min(Tl, s.t + dt);
      const a = Om * s.t, acc = [-v * Om * Math.cos(a), -v * Om * Math.sin(a), 0];
      const A = this.attitude(acc, a + Math.PI / 2);
      const p = [r * Math.cos(a), r * Math.sin(a), 1.5];
      this.place(api, A.R, p, 3);
      api.keep.tr.add(this.w2t(api, p));
      if (s.t >= Tl - 1e-9) { s.ran = true; s.lap = true; api.stop(); }
    } else {
      s.t = Math.min(3, s.t + dt);
      if (s.t >= 3) { s.ran = true; api.stop(); }
    }
  },
  readouts(api, s) {
    const f = api.fmt, d = Math.PI / 180, rows = [];
    if (api.scene === "acc") {
      const A = this.attitude([api.p.ax, api.p.ay, api.p.az], api.p.psi * d), tilt = Math.acos(A.zb[2]) / d;
      rows.push([["总推力 f = m‖p̈ + gẑ‖", "collective f = m‖p̈ + gẑ‖"], f(A.f, 3) + " N"],
                [["倾角（z_b 与竖直方向）", "tilt (z_b from vertical)"], f(tilt, 2) + "°"],
                [["俯仰角 θ、横滚角 φ", "pitch θ, roll φ"], `${f(A.th / d, 2)}°, ${f(A.ph / d, 2)}°`],
                [["偏航角 ψ（由 R 反求）", "yaw ψ (back from R)"], f(Math.atan2(A.R[1][0], A.R[0][0]) / d, 1) + "°"],
                [["加速度计读数（质心处）", "accelerometer (at CoM)"], `(0, 0, ${f(A.nt, 3)}) m/s²`]);
      const fwd = Math.abs(api.p.ax - 2) < 1e-9 && Math.abs(api.p.ay) < 1e-9 && Math.abs(api.p.az) < 1e-9;
      if (s.ran && fwd && Math.abs(api.p.psi) < 1e-9 && Math.abs(A.th / d - 11.52) < 0.05) api.done("fwd");
      if (s.ran && fwd && Math.abs(api.p.psi - 90) < 1e-9 && Math.abs(A.ph / d - 11.52) < 0.05) api.done("yaw90");
      return rows;
    }
    if (api.scene === "turn") {
      const v = api.p.v, r = api.p.rho, Om = v / r, ac = v * v / r, ph = -Math.atan2(ac, this.G);
      rows.push([["向心加速度 v²/ρ", "centripetal v²/ρ"], f(ac, 2) + " m/s²"],
                [["坡度（横滚角 φ，负为向左）", "bank (roll φ, negative = left)"], f(ph / d, 2) + "°"],
                [["总推力 f", "collective f"], f(this.M * Math.hypot(ac, this.G), 3) + " N"],
                [["转一圈的时间 2π/Ω", "lap time 2π/Ω"], f(2 * Math.PI / Om, 2) + " s"],
                [["陀螺仪 ω_b = Ω(0, sin φ, cos φ)", "gyro ω_b = Ω(0, sin φ, cos φ)"], `(0, ${f(Om * Math.sin(ph), 4)}, ${f(Om * Math.cos(ph), 4)}) rad/s`],
                [["已飞时间", "time flown"], f(s.t || 0, 1) + " s"]);
      if (s.lap && Math.abs(v - 4) < 1e-9 && Math.abs(r - 5) < 1e-9) api.done("turn");
      return rows;
    }
    const a = api.p.acar, al = Math.atan2(a, this.G) / d;
    rows.push([["汽车加速度 a", "car acceleration a"], f(a, 1) + " m/s²"],
              [["车速（从 10 m/s 起）", "speed (from 10 m/s)"], f(Math.max(0, 10 + a * (s.t || 0)), 1) + " m/s"],
              [["挂件偏角 α = atan(a/g)（向后为正）", "ornament angle α = atan(a/g) (backwards +)"], f(al, 2) + "°"],
              [["同样加速的四旋翼的俯仰角", "pitch of a quadrotor accelerating alike"], f(al, 2) + "°"]);
    if (s.ran && Math.abs(a - 2) < 1e-9) api.done("car");
    return rows;
  },
  draw(api, s) {
    const K = api.keep, m = api.m, h = m["B-UAV-X2"];
    if (!K || !K.Cm) return;
    const sc = api.scene;
    h.holder.visible = sc !== "car"; K.car.visible = sc === "car";
    K.thrust.visible = sc !== "car"; K.acc.visible = sc === "acc"; K.tr.line.visible = sc === "turn";
    if (K.shown !== sc) { K.shown = sc; api.view(sc === "turn" ? 20 : 35, sc === "turn" ? 40 : 18, 0.85, sc === "acc" ? m.fAcc : sc === "turn" ? m.fTurn : m.fCar); }
    if (sc !== "car") {
      h.holder.updateMatrixWorld(true);
      const c = h.point("x2", [0, 0, this.CZ]), z = h.point("x2", [0, 0, this.CZ + 0.1]).sub(c).normalize();
      K.thrust.position.copy(c); K.thrust.setDirection(z);
      K.thrust.setLength(sc === "turn" ? 1.4 : 0.45, sc === "turn" ? 0.2 : 0.08, sc === "turn" ? 0.12 : 0.05);
      if (sc === "acc") {
        const a = [api.p.ax, api.p.ay, api.p.az], n = this.norm(a);
        K.acc.visible = n > 1e-6;
        if (n > 1e-6) { K.acc.position.copy(c); K.acc.setDirection(this.w2t(api, a).normalize()); K.acc.setLength(0.06 + 0.06 * n, 0.06, 0.035); }
      }
    } else {
      const a = api.p.acar, al = s.ran || s.t > 0 ? Math.atan2(a, this.G) * Math.min(1, (s.t || 0) / 0.5) : 0;
      K.pend.rotation.z = -al;   // 车头朝 +x；加速时挂件向后（−x）摆：绕 +z（三维引擎）转负角
    }
  },
});
