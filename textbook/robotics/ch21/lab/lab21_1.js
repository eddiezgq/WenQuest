// 实验 21.1 四个旋翼的推力与机身受力（配 21.1 节）。
// 零件库 X2（B-UAV-X2）：质量 1.325 kg，质心在模型机体坐标系 (0, 0, 0.054) m；旋翼中心 (±0.14, ±0.18) m（MJCF），
// 推力 0～13 N，反扭矩系数 c_τ = 0.0201 m，σ = (−1, +1, −1, +1)。总推力与力矩按式 (21.1.6)。
// “开始”后机身示意地运动 2 s：物体角速度 ω_b = K m_b（K = 0.6 rad/(s·N·m)，偏航 K_z = 6），竖直速度 0.15(f − mg) m/s。
// 这只是为了看出力矩的方向，不是动力学仿真（四旋翼的动力学见第 28 章）。
// 生活场景：直升机主旋翼的反扭矩 12 N·m（示意），尾桨到主旋翼轴 1.5 m（示意），机身偏航角速度 0.15 × 净力矩 rad/s（示意）。
WQ.lab({
  title: ["实验 21.1 四个旋翼的推力与机身受力", "Lab 21.1 Rotor thrusts and the forces on the body"],
  goal: ["调节四个旋翼的推力，验证推力分配矩阵：总推力、横滚、俯仰、偏航四个通道各由哪种推力组合产生；体会偏航通道为什么最弱，直升机为什么需要尾桨。",
         "Set the four rotor thrusts and check the allocation matrix: which thrust pattern makes the collective thrust and the roll, pitch and yaw moments; see why yaw is the weakest channel and why a helicopter needs a tail rotor."],
  view: "3d",
  models: ["B-UAV-X2"],
  scenes: [
    { id: "thrust", robot: true, name: ["推力与力矩", "Thrusts and moments"], hide: ["tail"],
      problem: { title: ["机器人问题：四个都向上的推力，怎样让机身倾斜和转向", "Robot problem: four upward thrusts, yet the body must tilt and turn"],
                 text: ["拖动四个滑块改变各旋翼的推力（蓝色箭头）。界面按式 (21.1.6) 给出总推力和三个力矩（紫色箭头为力矩）。按“开始”，机身按力矩的方向示意地转动 2 s。",
                        "Drag the four sliders to set each rotor's thrust (blue arrows). The readouts give the collective thrust and the three moments by Eq. (21.1.6) (purple arrow: moment). Press Start and the body turns, for illustration, along the moment for 2 s."] } },
    { id: "heli", name: ["直升机尾桨", "Helicopter tail rotor"], hide: ["f1", "f2", "f3", "f4"],
      problem: { title: ["生活中的例子：直升机为什么要有尾桨", "Everyday example: why a helicopter has a tail rotor"],
                 text: ["主旋翼逆时针转，给机身一个顺时针 12 N·m 的反扭矩（示意）。尾桨装在 1.5 m 长的尾梁末端，调节它的推力，使机身不再打转。",
                        "The main rotor turns counter-clockwise and gives the body a clockwise reaction torque of 12 N·m (illustrative). The tail rotor sits at the end of a 1.5 m boom; set its thrust so the body stops spinning."] } },
  ],
  params: [
    { id: "f1", name: ["旋翼 1（右后）推力 f₁", "rotor 1 (rear right) f₁"], min: 0, max: 13, step: 0.05, value: 3.25, unit: "N", digits: 2 },
    { id: "f2", name: ["旋翼 2（左后）推力 f₂", "rotor 2 (rear left) f₂"], min: 0, max: 13, step: 0.05, value: 3.25, unit: "N", digits: 2 },
    { id: "f3", name: ["旋翼 3（左前）推力 f₃", "rotor 3 (front left) f₃"], min: 0, max: 13, step: 0.05, value: 3.25, unit: "N", digits: 2 },
    { id: "f4", name: ["旋翼 4（右前）推力 f₄", "rotor 4 (front right) f₄"], min: 0, max: 13, step: 0.05, value: 3.25, unit: "N", digits: 2 },
    { id: "tail", name: ["尾桨推力", "tail-rotor thrust"], min: 0, max: 15, step: 0.1, value: 4, unit: "N", digits: 1 },
  ],
  tasks: [
    { id: "hover", robot: true, text: ["让 X2 悬停：总推力等于重力（误差 0.1 N 以内），三个力矩为零，按“开始”。", "Make X2 hover: collective thrust equal to its weight (within 0.1 N), all three moments zero; press Start."],
      demo: { scene: "thrust", set: { f1: 3.25, f2: 3.25, f3: 3.25, f4: 3.25 }, press: ["start"], wait: 12 } },
    { id: "yaw", robot: true, text: ["总推力仍等于重力，只产生偏航力矩（m_z ≥ 0.03 N·m，m_x、m_y 为零），按“开始”。", "Keep the collective thrust at the weight and make only a yaw moment (m_z ≥ 0.03 N·m, m_x = m_y = 0); press Start."],
      demo: { scene: "thrust", set: { f1: 2.5, f2: 4.0, f3: 2.5, f4: 4.0 }, press: ["start"], wait: 12 } },
    { id: "pitch", robot: true, text: ["总推力仍等于重力，只产生使机头向下的俯仰力矩（m_y ≥ 0.1 N·m），按“开始”。", "Keep the collective thrust at the weight and make only a nose-down pitch moment (m_y ≥ 0.1 N·m); press Start."],
      demo: { scene: "thrust", set: { f1: 3.75, f2: 3.75, f3: 2.75, f4: 2.75 }, press: ["start"], wait: 12 } },
    { id: "heli", text: ["调节尾桨推力，使直升机的净偏航力矩不超过 0.2 N·m，按“开始”。", "Set the tail-rotor thrust so the helicopter's net yaw moment is at most 0.2 N·m; press Start."],
      demo: { scene: "heli", set: { tail: 8.0 }, press: ["start"], wait: 14 } },
  ],
  think: ["算例 21.1.2 中，产生同样大的力矩，偏航需要的推力差约是横滚的 9 倍。如果把 X2 的机臂加长一倍，横滚和偏航的这个比例怎样变化？",
          "In Example 21.1.2, yaw needs about 9 times the thrust difference of roll for the same moment. If X2's arms were twice as long, how would this ratio change?"],

  M: 1.325, G: 9.81, CZ: 0.053962, C: 0.0201,
  ROT: [[-0.14, -0.18, 0.05], [-0.14, 0.18, 0.05], [0.14, 0.18, 0.08], [0.14, -0.18, 0.08]],
  SIG: [-1, 1, -1, 1],
  QMAIN: 12, ARM: 1.5,

  wrench(p) {   // 式 (21.1.6)：(f, m_x, m_y, m_z)
    const f = [p.f1, p.f2, p.f3, p.f4];
    let F = 0, mx = 0, my = 0, mz = 0;
    f.forEach((fi, i) => { F += fi; mx += this.ROT[i][1] * fi; my -= this.ROT[i][0] * fi; mz += this.SIG[i] * this.C * fi; });
    return { F, mx, my, mz, f };
  },
  mul3(A, B) { return A.map((r) => [0, 1, 2].map((k) => r[0] * B[0][k] + r[1] * B[1][k] + r[2] * B[2][k])); },
  exp3(w) {
    const t = Math.hypot(w[0], w[1], w[2]);
    if (t < 1e-12) return [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    const k = w.map((x) => x / t), K = [[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]], KK = this.mul3(K, K), s = Math.sin(t), c = 1 - Math.cos(t);
    return [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + s * K[i][j] + c * KK[i][j]));
  },
  // 机身（MJCF 机体坐标系 x2）在 {s} 中的姿态 R、质心位置 p（z 向上）→ 三维引擎（y 向上）
  place(api, R, p) {
    const T = api.three, K = api.keep, h = api.m["B-UAV-X2"];
    const c = [p[0] - (R[0][2] * this.CZ), p[1] - (R[1][2] * this.CZ), p[2] - (R[2][2] * this.CZ)];
    const Ts = new T.Matrix4().set(R[0][0], R[0][1], R[0][2], c[0], R[1][0], R[1][1], R[1][2], c[1], R[2][0], R[2][1], R[2][2], c[2], 0, 0, 0, 1);
    const W = K.Cm.clone().multiply(Ts).multiply(K.MhbInv);
    W.decompose(h.holder.position, h.holder.quaternion, h.holder.scale);
    h.holder.updateMatrixWorld(true);
  },
  w2t(api, v) { return new api.three.Vector3(v[0], v[2], -v[1]); },   // z 向上的坐标 → 三维引擎
  setup3d(api, keep) {
    const T = api.three, h = api.m["B-UAV-X2"];
    h.place(0, 0);
    h.holder.updateMatrixWorld(true);
    keep.Cm = new T.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1);
    const Mhb = new T.Matrix4().copy(h.holder.matrixWorld).invert().multiply(h.nodes.x2.matrixWorld);
    keep.MhbInv = Mhb.clone().invert();
    api.axes(h, "x2", 0.12);
    keep.arrows = this.ROT.map(() => { const a = new T.ArrowHelper(new T.Vector3(0, 1, 0), new T.Vector3(), 0.1, 0x1f77b4, 0.04, 0.025); api.st.scene.add(a); return a; });
    keep.mom = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(), 0.1, 0x8e6bbf, 0.05, 0.03);
    api.st.scene.add(keep.mom);
    // 直升机（示意，几何体拼成）：机身、尾梁、主旋翼、尾桨
    const g = new T.Group(), mat = (c) => new T.MeshStandardMaterial({ color: c, roughness: 0.6 });
    const body = new T.Mesh(new T.SphereGeometry(0.35, 24, 16), mat(0xd9822b)); body.scale.set(1.4, 0.9, 0.9); g.add(body);
    const boom = new T.Mesh(new T.CylinderGeometry(0.05, 0.08, 1.5, 12), mat(0x5d6b73)); boom.rotation.z = Math.PI / 2; boom.position.set(-1.0, 0.1, 0); g.add(boom);
    const mast = new T.Mesh(new T.CylinderGeometry(0.03, 0.03, 0.3, 8), mat(0x333333)); mast.position.set(0, 0.45, 0); g.add(mast);
    const disk = new T.Mesh(new T.CylinderGeometry(1.6, 1.6, 0.01, 48), new T.MeshStandardMaterial({ color: 0x9aa6ad, transparent: true, opacity: 0.35 })); disk.position.set(0, 0.6, 0); g.add(disk);
    const tail = new T.Mesh(new T.CylinderGeometry(0.25, 0.25, 0.01, 24), new T.MeshStandardMaterial({ color: 0x9aa6ad, transparent: true, opacity: 0.5 }));
    tail.rotation.x = Math.PI / 2; tail.position.set(-1.75, 0.2, 0.06); g.add(tail);
    g.position.set(0, 0.5, 0);
    api.st.scene.add(g);
    keep.heli = g;
    keep.tailArrow = new T.ArrowHelper(new T.Vector3(0, 0, 1), new T.Vector3(-1.75, 0.7, 0.08), 0.5, 0x1f77b4, 0.12, 0.08);
    g.add(keep.tailArrow);
    api.m.fX2 = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-0.45, 0, -0.45), new T.Vector3(0.45, 0.9, 0.45)) };
    api.m.fHeli = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-2.2, 0, -1.7), new T.Vector3(1.7, 1.2, 1.7)) };
    keep.shown = null;
  },
  reset(api, s) {
    s.R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; s.p = [0, 0, 0.35]; s.t = 0; s.ran = false; s.psi = 0;
    if (api.keep.Cm) this.place(api, s.R, s.p);
  },
  start(api, s) { s.t = 0; },
  update(dt, api, s) {
    const T = 2.0;
    s.t = Math.min(T, s.t + dt);
    if (api.scene === "thrust") {
      const w = this.wrench(api.p), wb = [0.6 * w.mx, 0.6 * w.my, 6 * w.mz];
      s.R = this.mul3(s.R, this.exp3(wb.map((x) => x * dt)));
      s.p[2] = Math.max(0.05, Math.min(1.2, s.p[2] + 0.15 * (w.F - this.M * this.G) * dt));
      this.place(api, s.R, s.p);
    } else {
      const net = api.p.tail * this.ARM - this.QMAIN;   // 尾桨推力对主旋翼轴的力矩（逆时针为正）+ 反扭矩（顺时针）
      s.psi += 0.15 * net * dt;
    }
    if (s.t >= T) { s.ran = true; api.stop(); }
  },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "heli") {
      const net = api.p.tail * this.ARM - this.QMAIN;
      if (s.ran && Math.abs(net) <= 0.2) api.done("heli");
      return [[["主旋翼反扭矩（顺时针）", "main-rotor reaction (clockwise)"], f(this.QMAIN, 1) + " N·m"],
              [["尾桨力矩 = 推力 × 1.5 m", "tail moment = thrust × 1.5 m"], f(api.p.tail * this.ARM, 2) + " N·m"],
              [["净偏航力矩（逆时针为正）", "net yaw moment (CCW +)"], f(net, 2) + " N·m"],
              [["机身转过的角度", "body heading change"], f(s.psi * 180 / Math.PI, 1) + "°"]];
    }
    const w = this.wrench(api.p), W = this.M * this.G;
    const lvl = Math.abs(w.F - W) < 0.1, z = (x) => Math.abs(x) < 0.005;
    if (s.ran && lvl && z(w.mx) && z(w.my) && z(w.mz)) api.done("hover");
    if (s.ran && lvl && z(w.mx) && z(w.my) && w.mz >= 0.03) api.done("yaw");
    if (s.ran && lvl && z(w.mx) && z(w.mz) && w.my >= 0.1) api.done("pitch");
    return [[["总推力 f（重力 mg = 13.00 N）", "collective f (weight mg = 13.00 N)"], f(w.F, 2) + " N"],
            [["横滚力矩 m_x = Σ y_i f_i", "roll m_x = Σ y_i f_i"], f(w.mx, 3) + " N·m"],
            [["俯仰力矩 m_y = −Σ x_i f_i", "pitch m_y = −Σ x_i f_i"], f(w.my, 3) + " N·m"],
            [["偏航力矩 m_z = Σ σ_i c_τ f_i", "yaw m_z = Σ σ_i c_τ f_i"], f(w.mz, 4) + " N·m"],
            [["推力最小、最大的旋翼", "smallest, largest rotor"], `${f(Math.min(...w.f), 2)}, ${f(Math.max(...w.f), 2)} N`]];
  },
  draw(api, s) {
    const K = api.keep, m = api.m, h = m["B-UAV-X2"];
    if (!K || !K.arrows) return;
    const thr = api.scene === "thrust";
    h.holder.visible = thr; K.heli.visible = !thr; K.mom.visible = false;
    K.arrows.forEach((a) => { a.visible = thr; });
    if (K.shown !== api.scene) { K.shown = api.scene; api.view(thr ? 30 : 35, thr ? 28 : 30, thr ? 0.85 : 0.8, thr ? m.fX2 : m.fHeli); }
    if (thr && s.R) {
      const p = api.p, f = [p.f1, p.f2, p.f3, p.f4], R = s.R, T = api.three;
      const zb = this.w2t(api, [R[0][2], R[1][2], R[2][2]]).normalize();
      this.ROT.forEach((r, i) => {
        const o = h.point("x2", r);
        K.arrows[i].position.copy(o);
        K.arrows[i].setDirection(zb);
        K.arrows[i].setLength(Math.max(0.02, 0.05 * f[i]), 0.04, 0.025);
      });
      const w = this.wrench(p), mb = [w.mx, w.my, w.mz * 9];   // 偏航力矩放大 9 倍画，便于看见
      const mw = [0, 1, 2].map((i) => R[i][0] * mb[0] + R[i][1] * mb[1] + R[i][2] * mb[2]), n = Math.hypot(...mw);
      if (n > 1e-3) {
        K.mom.visible = true;
        K.mom.position.copy(h.point("x2", [0, 0, this.CZ]));
        K.mom.setDirection(this.w2t(api, mw).normalize());
        K.mom.setLength(Math.min(0.4, 0.08 + 0.5 * n), 0.05, 0.03);
      }
    }
    if (!thr) {
      K.heli.rotation.y = s.psi || 0;
      K.tailArrow.setLength(Math.max(0.02, 0.06 * api.p.tail), 0.12, 0.08);
    }
  },
});
