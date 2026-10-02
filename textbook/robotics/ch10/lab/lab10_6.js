// 实验 10.6 转台上的 AGV（配 10.6 节）。零件库差速小车 B-EDU-DIFF 在半径 1.5 m 的转台上，从中心沿转台上画的一条半径向外行驶。
// 地面坐标系 {s}：原点在转台中心，z 向上。转台转角 ψ = Ω t + α t²/2；小车在转台上离中心 ρ = v_rel t，车头沿这条半径向外。
// “加速度计读数”：由小车在地面上的位置 r_s(t) = Rot(ẑ, ψ)(ρ, 0, 0) 用二阶中心差商数值求导，再投影到车头方向 x 和左侧 y；
// “计算值”：式 (10.6.12)，a_x = v̇_rel − Ω²ρ，a_y = 2Ω v_rel + αρ（Ω 取此刻的值）。
// 场景 ball：小球从转台中心以 0.6 m/s 沿地面上一个固定方向滚出（无摩擦），分别画出它在地面上和在转台上的轨迹。
// 三维场景 y 轴向上：{s} 中的 (x, y, z) 画在 (x, z, −y)。
WQ.lab({
  title: ["实验 10.6 转台上的 AGV", "Lab 10.6 An AGV on a turntable"],
  goal: ["比较加速度计的“测量值”与加速度合成定理的计算值，看清向心加速度、科氏加速度和欧拉加速度各自的来源。",
         "Compare the accelerometer “reading” with the composition theorem, and see where the centripetal, Coriolis and Euler terms come from."],
  view: "3d",
  models: ["B-EDU-DIFF"],
  scenes: [
    { id: "agv", robot: true, name: ["转台上沿半径行驶", "Driving along a radius of the turntable"],
      problem: { title: ["机器人问题：直线匀速行驶，为什么有横向加速度", "Robot problem: driving straight and steady, why a sideways acceleration"],
                 text: ["转台以 0.5 rad/s 转动，小车沿转台上的导引线以 0.4 m/s 匀速向外行驶。离中心 1.0 m 时加速度计读到什么？",
                        "The table turns at 0.5 rad/s and the cart drives out along the guide line at a steady 0.4 m/s. What does its accelerometer read 1.0 m from the centre?"] } },
    { id: "ball", name: ["转盘上滚动的小球", "A ball rolling on a turntable"], hide: ["vr", "al"],
      problem: { title: ["生活中的例子：旋转木马上扔球", "Everyday example: throwing a ball on a merry-go-round"],
                 text: ["小球从中心沿地面上的固定方向匀速滚出。在转盘上的人看来，它走的是什么路线？",
                        "The ball rolls out from the centre along a fixed direction on the ground. What path does someone on the turntable see?"] } },
  ],
  params: [
    { id: "Om", name: ["转台角速度 Ω", "Table rate Ω"], min: -1, max: 1, step: 0.05, value: 0.5, unit: "rad/s", digits: 2 },
    { id: "al", name: ["转台角加速度 α", "Table angular acceleration α"], min: 0, max: 0.4, step: 0.05, value: 0, unit: "rad/s²", digits: 2 },
    { id: "vr", name: ["小车相对转台的速度 v_rel", "Cart speed on the table v_rel"], min: 0.1, max: 0.8, step: 0.05, value: 0.4, unit: "m/s", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["按算例 10.6.1 设置（Ω = 0.5 rad/s，α = 0，v_rel = 0.4 m/s），在离中心 1.0 m 处比较加速度计读数与计算值。",
                                    "Set Example 10.6.1 (Ω = 0.5 rad/s, α = 0, v_rel = 0.4 m/s) and compare the reading with the calculation 1.0 m from the centre."],
      demo: { scene: "agv", set: { Om: 0.5, al: 0, vr: 0.4 }, press: ["start"], wait: 40 } },
    { id: "still", robot: true, text: ["让转台停转（Ω = 0，α = 0）再行驶：横向读数为零。", "Stop the table (Ω = 0, α = 0) and drive: the sideways reading is zero."],
      demo: { scene: "agv", set: { Om: 0, al: 0, vr: 0.4 }, press: ["start"], wait: 40 } },
    { id: "reverse", robot: true, text: ["让转台反向转动（Ω < 0）：横向读数改变符号。", "Turn the table the other way (Ω < 0): the sideways reading changes sign."],
      demo: { scene: "agv", set: { Om: -0.5, al: 0, vr: 0.4 }, press: ["start"], wait: 40 } },
    { id: "ball", text: ["小球场景中让转台逆时针转动，运行到小球滚出盘边：转盘上的轨迹向右弯。", "With the table turning anticlockwise, run the ball to the rim: its path on the table bends right."],
      demo: { scene: "ball", set: { Om: 0.5 }, press: ["start"], wait: 40 } },
  ],
  think: ["小车离中心越远，横向读数会不会变？向后的读数呢？若小车改为向中心行驶，两个读数各怎样变化？",
          "Does the sideways reading change as the cart gets further out? And the backward one? How do both change if the cart drives towards the centre?"],

  RT: 1.5, V0: 0.6,
  tabAng(api, t) { return api.p.Om * t + 0.5 * api.p.al * t * t; },
  posS(api, t) {                // 地面坐标中的位置（二维）
    const psi = this.tabAng(api, t);
    if (api.scene === "ball") return [this.V0 * t, 0];
    const rho = api.p.vr * t;
    return [rho * Math.cos(psi), rho * Math.sin(psi)];
  },
  imu(api, t) {                 // 数值求导的加速度，投影到车头方向与左侧
    const h = 1e-3, p0 = this.posS(api, t - h), p1 = this.posS(api, t), p2 = this.posS(api, t + h);
    const a = [(p2[0] - 2 * p1[0] + p0[0]) / (h * h), (p2[1] - 2 * p1[1] + p0[1]) / (h * h)];
    const psi = this.tabAng(api, t), er = [Math.cos(psi), Math.sin(psi)], ep = [-Math.sin(psi), Math.cos(psi)];
    return [a[0] * er[0] + a[1] * er[1], a[0] * ep[0] + a[1] * ep[1]];
  },
  calc(api, t) {                // 式 (10.6.12)
    const rho = api.p.vr * t, Om = api.p.Om + api.p.al * t;
    return { ax: -Om * Om * rho, ay: 2 * Om * api.p.vr + api.p.al * rho, cent: -Om * Om * rho, cor: 2 * Om * api.p.vr, eul: api.p.al * rho, rho, Om };
  },
  setup3d(api, keep) {
    const T = api.three, st = api.st;
    keep.table = new T.Group(); st.scene.add(keep.table);
    const disk = new T.Mesh(new T.CylinderGeometry(this.RT, this.RT, 0.05, 72), new T.MeshStandardMaterial({ color: 0xc9d1d8 }));
    disk.position.y = 0.025; keep.table.add(disk);
    const line = new T.Mesh(new T.BoxGeometry(this.RT, 0.004, 0.04), new T.MeshStandardMaterial({ color: 0xe07b00 }));
    line.position.set(this.RT / 2, 0.052, 0); keep.table.add(line);
    for (let k = 1; k < 4; k++) {
      const l2 = new T.Mesh(new T.BoxGeometry(this.RT, 0.003, 0.015), new T.MeshStandardMaterial({ color: 0x8a96a0 }));
      l2.position.set(this.RT / 2 * Math.cos(k * Math.PI / 2), 0.051, -this.RT / 2 * Math.sin(k * Math.PI / 2));
      l2.rotation.y = k * Math.PI / 2; keep.table.add(l2);
    }
    const max = 3000, pos = new Float32Array(max * 3), g = new T.BufferGeometry();
    g.setAttribute("position", new T.BufferAttribute(pos, 3)); g.setDrawRange(0, 0);
    keep.rel = new T.Line(g, new T.LineBasicMaterial({ color: 0xc0392b })); keep.rel.frustumCulled = false; keep.table.add(keep.rel);
    keep.relN = 0;
    keep.trace = api.trace(0xe07b00);
    keep.ball = new T.Mesh(new T.SphereGeometry(0.06, 24, 16), new T.MeshStandardMaterial({ color: 0xe07b00 }));
    st.scene.add(keep.ball);
    const car = api.m["B-EDU-DIFF"];
    car.place(0, 0, 0);
    keep.carY = car.holder.position.y + 0.05;
    api.m.frameBox = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-1.7, 0, -1.7), new T.Vector3(1.7, 0.5, 1.7)) };
    keep.shown = "";
  },
  reset(api, s) {
    s.wheel = 0; s.last = null; s.done = false;
    const K = api.keep;
    if (K && K.trace) { K.trace.clear(); K.relN = 0; K.rel.geometry.setDrawRange(0, 0); }
  },
  update(dt, api, s) {
    s.wheel += (api.scene === "ball" ? 0 : api.p.vr) * dt / 0.05;
    const t = api.t, near = (a, b) => Math.abs(a - b) < 1e-9;
    if (api.scene === "agv") {
      const c = this.calc(api, t), m = this.imu(api, t);
      if (c.rho >= 1.0 && c.rho < 1.1 && near(api.p.Om, 0.5) && near(api.p.al, 0) && near(api.p.vr, 0.4) &&
          Math.abs(m[0] + 0.25) < 0.02 && Math.abs(m[1] - 0.4) < 0.01 && Math.abs(m[0] - c.ax) < 1e-3 && Math.abs(m[1] - c.ay) < 1e-3) api.done("ex");
      if (c.rho > 0.5 && near(api.p.Om, 0) && near(api.p.al, 0) && Math.abs(m[1]) < 1e-6) api.done("still");
      if (c.rho > 0.5 && api.p.Om < -0.05 && near(api.p.al, 0) && m[1] < -0.05) api.done("reverse");
      if (c.rho >= this.RT - 0.15) { s.done = true; api.stop(); }
    } else if (this.V0 * t >= this.RT) { s.done = true; if (api.p.Om > 0.1) api.done("ball"); api.stop(); }
  },
  readouts(api, s) {
    const t = api.t;
    if (api.scene === "ball") {
      const p = this.posS(api, t), psi = this.tabAng(api, t);
      return [[["小球在地面上", "ball on the ground"], `(${api.fmt(p[0], 3)}, ${api.fmt(p[1], 3)}) m`],
              [["转台转过", "table turned by"], api.fmt(psi * 180 / Math.PI, 1) + "°"],
              [["小球在转台上的方位", "ball's bearing on the table"], api.fmt(-psi * 180 / Math.PI, 1) + "°"]];
    }
    const c = this.calc(api, t), m = this.imu(api, t);
    return [[["离中心 ρ", "distance from centre ρ"], api.fmt(c.rho, 3) + " m"], [["此刻的 Ω", "Ω now"], api.fmt(c.Om, 3) + " rad/s"],
            [["加速度计读数（向前, 向左）", "accelerometer (forward, left)"], `(${api.fmt(m[0], 4)}, ${api.fmt(m[1], 4)}) m/s²`],
            [["计算值 (10.6.12)", "calculated (10.6.12)"], `(${api.fmt(c.ax, 4)}, ${api.fmt(c.ay, 4)}) m/s²`],
            [["向心 −Ω²ρ", "centripetal −Ω²ρ"], api.fmt(c.cent, 4) + " m/s²"], [["科氏 2Ωv_rel", "Coriolis 2Ωv_rel"], api.fmt(c.cor, 4) + " m/s²"],
            [["欧拉 αρ", "Euler αρ"], api.fmt(c.eul, 4) + " m/s²"]];
  },
  draw(api, s) {
    const K = api.keep, T = api.three, car = api.m["B-EDU-DIFF"], t = api.t;
    if (K.shown !== api.scene) { K.shown = api.scene; api.view(20, 50, 1.0, api.m.frameBox); }
    const psi = this.tabAng(api, t);
    K.table.rotation.y = psi;
    const ball = api.scene === "ball";
    car.holder.visible = !ball; K.ball.visible = ball;
    const p = this.posS(api, t);
    const world = new T.Vector3(p[0], ball ? 0.11 : 0.06, -p[1]);
    if (ball) K.ball.position.copy(world);
    else {
      car.holder.position.set(p[0], K.carY, -p[1]); car.holder.rotation.set(0, psi, 0);
      car.set({ left_wheel_joint: s.wheel, right_wheel_joint: s.wheel });
    }
    if (api.running && (!s.last || world.distanceTo(s.last) > 0.01)) {
      K.trace.add(world.clone().setY(0.07)); s.last = world.clone();
      if (ball) {             // 在转台上的轨迹：把地面位置转回转台坐标，画在随转台转动的组里
        const c = Math.cos(-psi), sn = Math.sin(-psi), lx = c * p[0] - sn * p[1], ly = sn * p[0] + c * p[1];
        const arr = K.rel.geometry.attributes.position;
        if (K.relN < arr.count) { arr.setXYZ(K.relN, lx, 0.06, -ly); K.relN++; K.rel.geometry.setDrawRange(0, K.relN); arr.needsUpdate = true; }
      }
    }
  },
});
