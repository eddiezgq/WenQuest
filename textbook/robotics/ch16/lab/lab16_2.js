// 实验 16.2 欧拉角、旋转矢量与几何雅可比（配 16.2 节）。
// 机器人场景：零件库的 UR5e 从 θ* 出发（算例 16.2.3），法兰盘中心不动，以 ω（°/s）绕一根水平轴转动 180°。
// 转轴为 z_b 向 x_b 偏 δ：δ 越小，ZYX 俯仰角 β 的最大值 90° − δ 越接近万向节锁。控制器用几何雅可比
// J_g θ̇ = (ω_s, ṗ = 0)（定义 16.2.1），列为 (ω_i, ω_i × (p − q_i))。同时按式 (16.2.7) 算出欧拉角速率 η̇ = B⁻¹ω，
// 按定理 16.2.3 算出旋转矢量（UR 示教器上的 Rx、Ry、Rz）的速率 ṙ = A⁻¹ω。
// 生活场景：手机的指南针。航向取手机顶边在水平面上投影的方位，即 ZYX 欧拉角的 α。手机顶边抬起 tilt，
// 再绕正北方向的水平轴向一侧倾斜 lean：顶边接近竖直时，一点侧倾就让航向大幅跳动。
WQ.lab({
  title: ["实验 16.2 欧拉角、旋转矢量与几何雅可比", "Lab 16.2 Euler angles, the rotation vector and the geometric Jacobian"],
  goal: ["让 UR5e 的法兰盘以恒定的角速度转过万向节锁附近，比较关节转速、欧拉角速率和旋转矢量速率，区分“表示奇异”与“运动学奇异”。",
         "Turn the UR5e flange at a constant angular velocity past the gimbal lock and compare joint speeds, Euler-angle rates and rotation-vector rates, telling a representation singularity from a kinematic one."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ur", robot: true, name: ["法兰盘转过万向节锁附近", "Flange turning past gimbal lock"], hide: ["tilt", "lean"],
      problem: { title: ["机器人问题：示教器上的三个姿态角为什么突然狂转", "Robot problem: why the three orientation angles on the pendant suddenly spin"],
                 text: ["法兰盘中心不动，绕水平轴匀速转动 180°。黄线是法兰盘法线端点的轨迹。测量区给出 ZYX 欧拉角、旋转矢量和它们的速率，以及关节转速的最大值。",
                        "The flange centre stays put while the flange turns 180° about a horizontal axis at a constant rate. The yellow line traces the tip of the flange normal. The readouts give the ZYX Euler angles, the rotation vector, their rates and the largest joint speed."] } },
    { id: "phone", name: ["手机指南针", "Phone compass"], hide: ["delta", "wdeg"],
      problem: { title: ["生活中的例子：手机竖起来，指南针乱跳", "Everyday example: hold the phone upright and the compass jumps"],
                 text: ["航向是手机顶边（红色箭头）在水平面上投影的方位。把顶边抬起（tilt），再向一侧倾斜一点（lean），看航向变化多少。",
                        "The heading is the direction of the phone's top edge (red arrow) projected on the horizontal plane. Raise the top edge (tilt), lean it a little sideways (lean), and see how much the heading changes."] } },
  ],
  params: [
    { id: "delta", name: ["转轴偏离 z_b 的角度 δ", "tilt δ of the axis from z_b"], min: 0.5, max: 10, step: 0.5, value: 1, unit: "°", digits: 1 },
    { id: "wdeg", name: ["角速度 |ω|", "angular speed |ω|"], min: 5, max: 30, step: 5, value: 20, unit: "°/s", digits: 0 },
    { id: "tilt", name: ["手机顶边抬起", "top edge raised"], min: 0, max: 90, step: 0.5, value: 30, unit: "°", digits: 1 },
    { id: "lean", name: ["向一侧倾斜", "lean sideways"], min: -5, max: 5, step: 0.5, value: 0, unit: "°", digits: 1 },
  ],
  legend: [{ color: "#c98f00", name: ["法兰盘法线端点的轨迹", "trace of the flange-normal tip"] }],
  tasks: [
    { id: "peak", robot: true, text: ["δ = 1°：欧拉角速率的峰值超过 1000°/s，而关节转速始终低于 40°/s。", "δ = 1°: the Euler-angle rate peaks above 1000°/s while no joint exceeds 40°/s."],
      demo: { scene: "ur", set: { delta: 1, wdeg: 20 }, press: ["start"], wait: 30 } },
    { id: "delta", robot: true, text: ["把 δ 加大到 10°：欧拉角速率的峰值降到 150°/s 以下。", "Increase δ to 10°: the Euler-angle rate peak falls below 150°/s."],
      demo: { scene: "ur", set: { delta: 10, wdeg: 20 }, press: ["start"], wait: 30 } },
    { id: "flip", robot: true, text: ["观察旋转矢量：它的速率始终有限，但在转角经过 180° 时整体跳变到反方向。", "Watch the rotation vector: its rate stays finite, but it jumps to the opposite direction when the angle passes 180°."],
      demo: { scene: "ur", set: { delta: 1, wdeg: 20 }, press: ["start"], wait: 30 } },
    { id: "phone", text: ["生活场景：顶边抬起 89° 以上时，向一侧倾斜 1°，航向变化超过 30°。", "Everyday scene: with the top edge raised above 89°, a 1° sideways lean changes the heading by more than 30°."],
      demo: { scene: "phone", set: { tilt: 89.5, lean: 1 }, press: [], wait: 1 } },
  ],
  think: ["关节转速一直平稳，示教器上的欧拉角却在一瞬间转了将近 180°。机器人此刻是否处于奇异位形？把 16.2.4 节的“表示奇异”和 16.3 节的“运动学奇异”分开说明。",
          "The joint speeds stay smooth while the Euler angles on the pendant swing by nearly 180° in an instant. Is the robot at a singular configuration? Separate the “representation singularity” of Section 16.2.4 from the “kinematic singularity” of Section 16.3."],

  // ---------------- UR5e 几何（表 12.1.1）与 SO(3)、SE(3) 运算（同实验 16.1）
  G: { H1: 0.163, W1: 0.138, L1: 0.425, W2: 0.131, L2: 0.392, W3: 0.127, H2: 0.1, W4: 0.1 },
  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  START: [30, -60, 90, -120, -90, 45],
  DT: 0.005, DUR: 9.0,
  dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  add(a, b) { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; },
  sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; },
  mul(a, s) { return [a[0] * s, a[1] * s, a[2] * s]; },
  norm(a) { return Math.hypot(a[0], a[1], a[2]); },
  mv(R, v) { return [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]); },
  mm(A, B) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j])); },
  tr(A) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[j][i])); },
  rot(w, t) {
    const c = Math.cos(t), s = Math.sin(t), v = 1 - c, [x, y, z] = w;
    return [[c + x * x * v, x * y * v - z * s, x * z * v + y * s], [y * x * v + z * s, c + y * y * v, y * z * v - x * s], [z * x * v - y * s, z * y * v + x * s, c + z * z * v]];
  },
  AX() {
    const g = this.G, Y = [0, -1, 0];
    return [[[0, 0, 1], [0, 0, g.H1]], [Y, [0, -g.W1, g.H1]], [Y, [-g.L1, -g.W1 + g.W2, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2, g.H1]],
            [[0, 0, -1], [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1 - g.H2]]];
  },
  M() { const g = this.G; return { R: [[1, 0, 0], [0, -1, 0], [0, 0, -1]], p: [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3 - g.W4, g.H1 - g.H2] }; },
  E(i, t) { const [w, q] = this.AX()[i], R = this.rot(w, t); return { R, p: this.sub(q, this.mv(R, q)) }; },
  comp(A, B) { return { R: this.mm(A.R, B.R), p: this.add(this.mv(A.R, B.p), A.p) }; },
  act(A, x) { return this.add(this.mv(A.R, x), A.p); },
  fk(th) { let T = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] }; th.forEach((t, i) => { T = this.comp(T, this.E(i, t)); }); return this.comp(T, this.M()); },
  jg(th) {                                        // 几何雅可比的六列：(ω_i, ω_i × (p − q_i))（定义 16.2.1）
    const A = this.AX(), p = this.fk(th).p, cols = [];
    let P = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] };
    for (let i = 0; i < 6; i++) {
      const w = this.mv(P.R, A[i][0]), q = this.act(P, A[i][1]);
      cols.push([...w, ...this.cross(w, this.sub(p, q))]);
      P = this.comp(P, this.E(i, th[i]));
    }
    return cols;
  },
  solve(cols, b) {
    const n = b.length, M = [];
    for (let r = 0; r < n; r++) M.push([...cols.map((c) => c[r]), b[r]]);
    for (let i = 0; i < n; i++) {
      let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(M[j][i]) > Math.abs(M[p][i])) p = j;
      [M[i], M[p]] = [M[p], M[i]];
      for (let j = i + 1; j < n; j++) { const f = M[j][i] / M[i][i]; for (let k = i; k <= n; k++) M[j][k] -= f * M[i][k]; }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let s = M[i][n]; for (let k = i + 1; k < n; k++) s -= M[i][k] * x[k]; x[i] = s / M[i][i]; }
    return x;
  },
  euler(R) { return [Math.atan2(R[1][0], R[0][0]), Math.asin(Math.max(-1, Math.min(1, -R[2][0]))), Math.atan2(R[2][1], R[2][2])]; },
  eulerRate(e, w) {                               // η̇ = B⁻¹ ω（式 (16.2.7)）
    const [a, b] = e, ca = Math.cos(a), sa = Math.sin(a), tb = Math.tan(b), cb = Math.cos(b), h = ca * w[0] + sa * w[1];
    return [w[2] + tb * h, -sa * w[0] + ca * w[1], h / cb];
  },
  logR(R) {
    const c = Math.max(-1, Math.min(1, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)), th = Math.acos(c);
    const d = [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]];
    if (th < 1e-9) return this.mul(d, 0.5);
    if (Math.PI - th < 1e-6) {
      const B = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (R[i][j] + (i === j ? 1 : 0)) / 2)), k = [0, 1, 2].reduce((a, i) => (B[i][i] > B[a][a] ? i : a), 0);
      return this.mul([B[0][k], B[1][k], B[2][k]], th / Math.sqrt(B[k][k]));
    }
    return this.mul(d, th / (2 * Math.sin(th)));
  },
  rvRate(r, w) {                                  // ṙ = A(r)⁻¹ ω：A = I + (1 − cos φ)/φ² [r] + (φ − sin φ)/φ³ [r]²（定理 16.2.3）
    const ph = this.norm(r), K = [[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]], K2 = this.mm(K, K);
    const a = ph < 1e-8 ? 0.5 : (1 - Math.cos(ph)) / (ph * ph), b = ph < 1e-8 ? 1 / 6 : (ph - Math.sin(ph)) / (ph * ph * ph);
    const A = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + a * K[i][j] + b * K2[i][j]));
    return this.solve([0, 1, 2].map((j) => [A[0][j], A[1][j], A[2][j]]), w);
  },
  omega(api, s) {                                 // 转轴：z_b 向 x_b 偏 δ（起始姿态下），大小 |ω|
    const d = api.p.delta * Math.PI / 180, R0 = s.R0, u = this.add(this.mul([R0[0][2], R0[1][2], R0[2][2]], Math.cos(d)), this.mul([R0[0][0], R0[1][0], R0[2][0]], Math.sin(d)));
    return this.mul(u, api.p.wdeg * Math.PI / 180);
  },
  // ---------------- 手机：先把顶边（x 轴，指北）抬起 tilt（绕 −y 转），再绕指北的水平轴侧倾 lean
  phoneR(api) {
    const t = api.p.tilt * Math.PI / 180, l = api.p.lean * Math.PI / 180;
    return this.mm(this.rot([1, 0, 0], -l), this.rot([0, 1, 0], -t));
  },

  reset(api, s) {
    s.t = 0; s.clock = 0; s.done = false;
    s.th = this.START.map((d) => d * Math.PI / 180);
    const T0 = this.fk(s.th);
    s.R0 = T0.R; s.p0 = T0.p;
    s.pkA = 0; s.pkG = 0; s.pkR = 0; s.pkQ = 0; s.bmax = -9; s.jump = 0; s.drift = 0;
    s.e = this.euler(T0.R); s.r = this.logR(T0.R); s.ed = [0, 0, 0]; s.rd = [0, 0, 0];
    s.trace = [this.add(T0.p, this.mul([T0.R[0][1], T0.R[1][1], T0.R[2][1]], 0.15))];
  },
  step(api, s) {
    const h = this.DT, w = this.omega(api, s), f = (q) => this.solve(this.jg(q), [...w, 0, 0, 0]);
    const k1 = f(s.th), k2 = f(s.th.map((x, i) => x + h / 2 * k1[i])), k3 = f(s.th.map((x, i) => x + h / 2 * k2[i])), k4 = f(s.th.map((x, i) => x + h * k3[i]));
    s.th = s.th.map((x, i) => x + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
    const T = this.fk(s.th), r = this.logR(T.R);
    s.pkQ = Math.max(s.pkQ, ...k1.map(Math.abs));
    s.e = this.euler(T.R); s.ed = this.eulerRate(s.e, w); s.rd = this.rvRate(r, w);
    s.pkA = Math.max(s.pkA, Math.abs(s.ed[0])); s.pkG = Math.max(s.pkG, Math.abs(s.ed[2])); s.pkR = Math.max(s.pkR, ...s.rd.map(Math.abs));
    s.bmax = Math.max(s.bmax, s.e[1]);
    s.jump = Math.max(s.jump, this.norm(this.sub(r, s.r))); s.r = r;
    s.drift = Math.max(s.drift, this.norm(this.sub(T.p, s.p0)));
    if (Math.round(s.t / h) % 4 === 0) s.trace.push(this.add(T.p, this.mul([T.R[0][1], T.R[1][1], T.R[2][1]], 0.15)));
    s.t += h;
    if (s.t >= this.DUR - 1e-9) s.done = true;
  },
  // 按“开始”时一次算完整段运动（结果用于检查任务），画面再按时间回放，这样回放快慢不影响结果
  start(api, s) {
    if (api.scene !== "ur") { api.stop(); return; }
    const r = Object.assign({}, s, { th: s.th && s.th.slice(), a: s.a && s.a.slice(), trace: s.trace.slice() }), snaps = [];
    let k = 0;
    while (!r.done) {
      this.step(api, r);
      if (k++ % 5 === 0 || r.done) snaps.push(Object.assign({}, r, { th: r.th && r.th.slice(), a: r.a && r.a.slice(), qd: r.qd && r.qd.slice(),
        peak: r.peak && r.peak.slice(), e: r.e && r.e.slice(), ed: r.ed && r.ed.slice(), rd: r.rd && r.rd.slice(), r: r.r && r.r.slice(), trace: null, n: r.trace.length }));
    }
    s.snaps = snaps; s.fullTrace = r.trace; s.final = r; s.clock = 0;
  },
  update(dt, api, s) {
    if (!s.snaps) return;
    s.clock += dt;
    const keep = { snaps: s.snaps, fullTrace: s.fullTrace, final: s.final, clock: s.clock };
    const i = Math.min(s.snaps.length - 1, Math.floor(s.clock / s.final.t * (s.snaps.length - 1)));
    Object.assign(s, s.snaps[i], keep, { trace: s.fullTrace.slice(0, s.snaps[i].n) });
    if (i === s.snaps.length - 1) { s.done = true; api.stop(); }
  },
  readouts(api, s) {
    const dg = (x) => (x * 180 / Math.PI).toFixed(1), D = 180 / Math.PI;
    if (api.scene === "phone") {
      const R = this.phoneR(api), e = this.euler(R), lean0 = this.mm(this.rot([1, 0, 0], 0), this.rot([0, 1, 0], -api.p.tilt * Math.PI / 180)), e0 = this.euler(lean0);
      let dh = Math.abs(e[0] - e0[0]) * D; if (dh > 180) dh = 360 - dh;
      if (api.p.tilt >= 89 && Math.abs(api.p.lean) >= 1 && dh > 30) api.done("phone");
      return [[["航向（ZYX 的 α）", "heading (α of ZYX)"], dg(e[0]) + "°"], [["俯仰 β", "pitch β"], dg(e[1]) + "°"], [["横滚 γ", "roll γ"], dg(e[2]) + "°"],
              [["与不侧倾时相比，航向变化", "heading change compared with no lean"], dh.toFixed(1) + "°"],
              [["顶边的水平投影长度", "length of the top edge's horizontal projection"], Math.hypot(R[0][0], R[1][0]).toFixed(4)]];
    }
    const F = s.final;
    if (F && F.done) {
      if (Math.abs(api.p.delta - 1) < 1e-9 && F.pkA * D > 1000 && F.pkQ * D < 40) api.done("peak");
      if (api.p.delta >= 10 - 1e-9 && Math.max(F.pkA, F.pkG) * D < 150) api.done("delta");
      if (F.jump > 3 && F.pkR * D < 60) api.done("flip");
    }
    return [[["时间", "time"], s.t.toFixed(2) + " s"], [["ZYX 欧拉角 (α, β, γ)", "ZYX Euler angles (α, β, γ)"], s.e.map(dg).join("°, ") + "°"],
            [["欧拉角速率 (α̇, β̇, γ̇)", "Euler-angle rates (α̇, β̇, γ̇)"], s.ed.map(dg).join(", ") + " °/s"],
            [["旋转矢量 (Rx, Ry, Rz)", "rotation vector (Rx, Ry, Rz)"], s.r.map(dg).join("°, ") + "°"],
            [["峰值：|α̇|、|γ̇|", "peaks: |α̇|, |γ̇|"], dg(s.pkA) + ", " + dg(s.pkG) + " °/s"],
            [["峰值：旋转矢量速率、关节转速", "peaks: rotation-vector rate, joint speed"], dg(s.pkR) + ", " + dg(s.pkQ) + " °/s"],
            [["β 的最大值；旋转矢量最大跳变", "largest β; largest jump of the rotation vector"], (s.bmax > -1 ? dg(s.bmax) : "—") + "°; " + dg(s.jump) + "°"],
            [["法兰盘中心的漂移", "drift of the flange centre"], (s.drift * 1000).toFixed(4) + " mm"],
            [["状态", "status"], s.done ? api.T("结束", "finished") : api.running ? api.T("转动中", "turning") : "—"]];
  },

  // ---------------- 三维
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    arm.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    const g = new T.BufferGeometry(); g.setAttribute("position", new T.BufferAttribute(new Float32Array(3000 * 3), 3)); g.setDrawRange(0, 0);
    keep.trace = new T.Line(g, new T.LineBasicMaterial({ color: 0xc98f00 })); keep.trace.frustumCulled = false; G.add(keep.trace);
    // 手机：放在机器人旁边的桌面上；红色箭头为顶边方向（x），绿色为左边（y），蓝色为屏幕法线（z）
    const P = new T.Group(); P.position.set(0.4, 1.2, 0.3); G.add(P); keep.P = P;
    const body = new T.Group(); P.add(body); keep.body = body;
    const ph = new T.Mesh(new T.BoxGeometry(0.15, 0.072, 0.008), new T.MeshStandardMaterial({ color: 0x1f2328 })); body.add(ph);
    const scr = new T.Mesh(new T.BoxGeometry(0.14, 0.066, 0.001), new T.MeshStandardMaterial({ color: 0x58a6ff })); scr.position.z = 0.0045; body.add(scr);
    body.add(new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(0, 0, 0), 0.16, 0xd62728, 0.03, 0.015));
    body.add(new T.ArrowHelper(new T.Vector3(0, 1, 0), new T.Vector3(0, 0, 0), 0.08, 0x2ca02c, 0.02, 0.012));
    body.add(new T.ArrowHelper(new T.Vector3(0, 0, 1), new T.Vector3(0, 0, 0), 0.08, 0x1f77b4, 0.02, 0.012));
    keep.north = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(0, 0, -0.06), 0.2, 0x7a868d, 0.03, 0.015); P.add(keep.north);
    keep.head = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(0, 0, -0.06), 0.18, 0xc98f00, 0.03, 0.015); P.add(keep.head);
    const ring = new T.Mesh(new T.RingGeometry(0.17, 0.175, 64), new T.MeshBasicMaterial({ color: 0x9aa7b2, side: T.DoubleSide })); ring.position.z = -0.06; P.add(ring);
    api.m.phoneView = { entry: { robot: {} }, holder: { visible: false },
      box: () => { G.updateMatrixWorld(true); return new T.Box3().setFromObject(P).expandByScalar(0.05); } };
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep, ur = api.scene === "ur";
    if (!k.G) return;
    k.P.visible = !ur; k.trace.visible = ur;
    if (k.shown !== api.scene) {
      k.shown = api.scene; arm.holder.visible = true;
      if (ur) api.view(35, 25, 0.6, arm); else api.view(-30, 30, 0.8, api.m.phoneView);
    }
    arm.holder.visible = ur;
    if (ur) {
      const o = {}; this.J.forEach((n, i) => { o[n] = s.th[i]; }); arm.set(o);
      const a = k.trace.geometry.attributes.position, pts = s.trace.slice(-3000);
      pts.forEach((p, i) => a.setXYZ(i, p[0], p[1], p[2])); a.needsUpdate = true; k.trace.geometry.setDrawRange(0, pts.length);
      return;
    }
    const R = this.phoneR(api), m = new api.three.Matrix4();
    m.set(R[0][0], R[0][1], R[0][2], 0, R[1][0], R[1][1], R[1][2], 0, R[2][0], R[2][1], R[2][2], 0, 0, 0, 0, 1);
    k.body.matrixAutoUpdate = false; k.body.matrix.copy(m);
    const hx = R[0][0], hy = R[1][0], n = Math.hypot(hx, hy);
    k.head.visible = n > 1e-6; if (n > 1e-6) k.head.setDirection(new api.three.Vector3(hx / n, hy / n, 0));
  },
});
