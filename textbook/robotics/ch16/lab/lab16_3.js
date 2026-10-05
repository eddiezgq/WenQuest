// 实验 16.3 找出 UR5e 的三类奇异位形（配 16.3 节）。
// 机器人场景：零件库的 UR5e，六个滑块设置关节角（起始为 θ* = (30°, −60°, 90°, −120°, −90°, 45°)）。
//   测量区：空间雅可比 J_s（定理 16.1.1）的行列式、最小奇异值、秩，以及定理 16.3.3 的三个因子
//   sin θ3（肘部）、sin θ5（手腕）、r = −L1 cos θ2 − L2 cos(θ2 + θ3) + H2 sin(θ2 + θ3 + θ4)（肩部），
//   det J = −L1 L2 sin θ3 sin θ5 · r（式 (16.3.3)）。
//   “自运动”按钮：沿 J 的零空间方向 n（最小奇异值对应的右奇异矢量）积分 2 s，使 θ6 以 20°/s 转动；
//   每步用阻尼最小二乘把法兰盘拉回起点，测量法兰盘中心的最大位移和 θ6 转过的角度。只有在奇异位形处，
//   零空间才不为零，法兰盘才能不动。
// 生活场景：三轴云台。偏航轴竖直，俯仰轴水平并随偏航转动，横滚轴沿相机光轴并随俯仰转动。三根轴的方向组成的
//   3×3 矩阵的行列式为 cos(俯仰角)；俯仰角为 90° 时横滚轴与偏航轴共线，失去一个转动方向（万向节锁）。
WQ.lab({
  title: ["实验 16.3 找出 UR5e 的三类奇异位形", "Lab 16.3 Finding the three kinds of singularity of the UR5e"],
  goal: ["拖动六个关节，让雅可比矩阵的行列式为零，找出肘部、手腕、肩部三类奇异；在手腕奇异处让手臂“自运动”，体会奇异的物理意义。",
         "Drag the six joints until the Jacobian's determinant vanishes and find the elbow, wrist and shoulder singularities; at the wrist singularity let the arm move by itself and see what a singularity means physically."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  buttons: [{ id: "start", name: ["自运动 2 s", "Self-motion 2 s"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 的奇异位形", "Singular configurations of the UR5e"], hide: ["gim"],
      problem: { title: ["机器人问题：示教器报警“接近奇异”，到底是哪里奇异", "Robot problem: the pendant warns “near singularity”, but which one"],
                 text: ["用滑块设置六个关节角。测量区给出 det J、最小奇异值和式 (16.3.3) 的三个因子；某个因子为零就是一类奇异。在奇异处按“自运动”，看手臂怎样动而法兰盘不动。",
                        "Set the six joint angles with the sliders. The readouts give det J, the smallest singular value and the three factors of Eq. (16.3.3); each factor that vanishes is one kind of singularity. At a singularity press “Self-motion” and watch the arm move while the flange stays put."] } },
    { id: "gimbal", name: ["三轴云台的万向节锁", "Gimbal lock of a three-axis gimbal"], hide: ["j1", "j2", "j3", "j4", "j5", "j6"],
      problem: { title: ["生活中的例子：云台为什么会“锁住”", "Everyday example: why a gimbal “locks”"],
                 text: ["拖动俯仰角。红、绿、蓝三根线是偏航轴、俯仰轴和横滚轴。测量区给出三根轴组成的矩阵的行列式；它为零时，相机绕某个方向再也转不动。",
                        "Drag the pitch angle. The red, green and blue lines are the yaw, pitch and roll axes. The readouts give the determinant of the matrix of the three axes; when it is zero, the camera can no longer turn about one direction."] } },
  ],
  params: [
    { id: "j1", name: ["θ₁", "θ₁"], min: -180, max: 180, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "j2", name: ["θ₂（0.1° 一格）", "θ₂ (0.1° steps)"], min: -180, max: 0, step: 0.1, value: -60, unit: "°", digits: 1 },
    { id: "j3", name: ["θ₃", "θ₃"], min: -180, max: 180, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "j4", name: ["θ₄", "θ₄"], min: -180, max: 180, step: 1, value: -120, unit: "°", digits: 0 },
    { id: "j5", name: ["θ₅", "θ₅"], min: -180, max: 180, step: 1, value: -90, unit: "°", digits: 0 },
    { id: "j6", name: ["θ₆", "θ₆"], min: -180, max: 180, step: 1, value: 45, unit: "°", digits: 0 },
    { id: "gim", name: ["云台俯仰角", "gimbal pitch angle"], min: 0, max: 90, step: 1, value: 30, unit: "°", digits: 0 },
  ],
  legend: [{ color: "#c98f00", name: ["自运动时法兰盘中心的轨迹", "trace of the flange centre during self-motion"] }],
  tasks: [
    { id: "elbow", robot: true, text: ["找出肘部奇异：|sin θ₃| < 0.005，det J ≈ 0。", "Find the elbow singularity: |sin θ₃| < 0.005, det J ≈ 0."],
      demo: { scene: "ur", set: { j1: 30, j2: -60, j3: 0, j4: -120, j5: -90, j6: 45 }, press: [], wait: 3 } },
    { id: "wrist", robot: true, text: ["找出手腕奇异：|sin θ₅| < 0.005，轴 6 与轴 2、3、4 平行。", "Find the wrist singularity: |sin θ₅| < 0.005, axis 6 parallel to axes 2, 3 and 4."],
      demo: { scene: "ur", set: { j1: 30, j2: -60, j3: 90, j4: -120, j5: 0, j6: 45 }, press: [], wait: 3 } },
    { id: "shoulder", robot: true, text: ["其余关节保持 θ* 的值，只调 θ₂，找出肩部奇异：|r| < 2 mm。", "Keep the other joints at θ* and adjust θ₂ only to find the shoulder singularity: |r| < 2 mm."],
      demo: { scene: "ur", set: { j1: 30, j3: 90, j4: -120, j5: -90, j6: 45, j2: -135.2 }, press: [], wait: 3 } },
    { id: "self", robot: true, text: ["在手腕奇异处按“自运动”：θ₆ 转过 30° 以上，法兰盘中心的位移小于 0.5 mm。", "At the wrist singularity press “Self-motion”: θ₆ turns by more than 30° while the flange centre moves less than 0.5 mm."],
      demo: { scene: "ur", set: { j1: 30, j2: -60, j3: 90, j4: -120, j5: 0, j6: 45 }, press: ["start"], wait: 5 } },
    { id: "lock", text: ["生活场景：让云台进入万向节锁，三根轴的行列式小于 0.01。", "Everyday scene: put the gimbal into gimbal lock, with the determinant of the three axes below 0.01."],
      demo: { scene: "gimbal", set: { gim: 90 }, press: [], wait: 3 } },
  ],
  think: ["在非奇异的形态下按“自运动”，为什么法兰盘会离开原位？肘部奇异和肩部奇异处的自运动，与手腕奇异处的有什么不同？",
          "Why does the flange leave its place when you press “Self-motion” away from a singularity? How does the self-motion at the elbow and shoulder singularities differ from that at the wrist?"],

  // ---------------- UR5e 几何（表 12.1.1）与 SE(3) 运算（同实验 16.1）
  G: { H1: 0.163, W1: 0.138, L1: 0.425, W2: 0.131, L2: 0.392, W3: 0.127, H2: 0.1, W4: 0.1 },
  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  add(a, b) { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; },
  sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; },
  mul(a, s) { return a.map((x) => x * s); },
  norm(a) { return Math.sqrt(a.reduce((s, x) => s + x * x, 0)); },
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
  js(th) {                                        // 空间雅可比（6×6，按行给出）：第 i 列 (ω_i, −ω_i × q_i)
    const A = this.AX(), cols = [];
    let P = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] };
    for (let i = 0; i < 6; i++) {
      const w = this.mv(P.R, A[i][0]), q = this.act(P, A[i][1]);
      cols.push([...w, ...this.mul(this.cross(w, q), -1)]);
      P = this.comp(P, this.E(i, th[i]));
    }
    return [0, 1, 2, 3, 4, 5].map((r) => cols.map((c) => c[r]));
  },
  jg(th) {                                        // 几何雅可比（按行）：(ω_s, 法兰盘中心的速度)
    const Js = this.js(th), p = this.fk(th).p;
    return [Js[0], Js[1], Js[2], ...[0, 1, 2].map((k) => Js[3 + k].map((v, i) => v - (this.cross(p, [Js[0][i], Js[1][i], Js[2][i]]))[k]))];
  },
  logR(R) {
    const c = Math.max(-1, Math.min(1, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)), a = Math.acos(c);
    const v = [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]];
    return a < 1e-9 ? this.mul(v, 0.5) : this.mul(v, a / (2 * Math.sin(a)));
  },
  factors(th) {
    const g = this.G, [, t2, t3, t4] = th;
    return { s3: Math.sin(t3), s5: Math.sin(th[4]), r: -g.L1 * Math.cos(t2) - g.L2 * Math.cos(t2 + t3) + g.H2 * Math.sin(t2 + t3 + t4) };
  },
  thFromParams(api) { return ["j1", "j2", "j3", "j4", "j5", "j6"].map((k) => api.p[k] * Math.PI / 180); },
  analyse(api, s) {
    const Js = this.js(s.th), LA = api.la;
    s.det = LA.det(Js); const sv = LA.svd(Js); s.sv = sv.s; s.V = sv.V; s.f = this.factors(s.th);
    s.rank = LA.rank(Js, 1e-9);
  },

  reset(api, s) {
    s.t = 0; s.done = false; s.clock = 0;
    if (api.scene === "gimbal") { s.p = api.p.gim * Math.PI / 180; s.det = Math.cos(s.p); return; }
    s.th = this.thFromParams(api); s.th0 = s.th.slice();
    s.T0 = this.fk(s.th); s.dmax = 0; s.turn6 = 0; s.nprev = null;
    s.trace = [s.T0.p];
    this.analyse(api, s);
  },
  step(api, s, h) {                               // 沿零空间积分一步，再用阻尼最小二乘把法兰盘拉回起点
    const LA = api.la, V = LA.svd(this.js(s.th)).V;
    let n = [0, 1, 2, 3, 4, 5].map((i) => V[i][5]);
    if (s.nprev && n.reduce((t, x, i) => t + x * s.nprev[i], 0) < 0) n = n.map((x) => -x);
    if (!s.nprev && n[5] < 0) n = n.map((x) => -x);
    s.nprev = n;
    const k = (20 * Math.PI / 180) / Math.max(Math.abs(n[5]), 0.05);
    s.th = s.th.map((x, i) => x + h * k * n[i]);
    for (let it = 0; it < 2; it++) {
      const T = this.fk(s.th), e = [...this.logR(this.mm(s.T0.R, this.tr(T.R))), ...this.sub(s.T0.p, T.p)], Jg = this.jg(s.th);
      const JJt = Jg.map((ri) => Jg.map((rj) => ri.reduce((t, x, c) => t + x * rj[c], 0)));
      for (let i = 0; i < 6; i++) JJt[i][i] += 1e-6;
      const y = LA.mv(LA.pinv(JJt), e), d = [0, 1, 2, 3, 4, 5].map((c) => Jg.reduce((t, row, r) => t + row[c] * y[r], 0));
      s.th = s.th.map((x, i) => x + d[i]);
    }
    const T = this.fk(s.th);
    s.dmax = Math.max(s.dmax, this.norm(this.sub(T.p, s.T0.p)));
    s.turn6 = Math.abs(s.th[5] - s.th0[5]);
    if (s.trace.length < 2000) s.trace.push(T.p);
  },
  update(dt, api, s) {
    if (api.scene !== "ur") { api.stop(); return; }
    const h = 0.01;
    s.clock += dt;
    while (s.clock >= h && api.running) {
      s.clock -= h; this.step(api, s, h); s.t += h;
      if (s.t >= 2 - 1e-9) { s.done = true; this.analyse(api, s); api.stop(); }
    }
  },
  readouts(api, s) {
    if (api.scene === "gimbal") {
      if (s.det < 0.01) api.done("lock");
      return [[["俯仰角", "pitch angle"], api.p.gim.toFixed(0) + "°"],
              [["三根轴的行列式 det = cos(俯仰角)", "determinant of the three axes = cos(pitch)"], s.det.toFixed(4)],
              [["状态", "status"], s.det < 0.01 ? api.T("万向节锁：横滚轴与偏航轴共线", "gimbal lock: roll axis in line with the yaw axis") : api.T("三根轴张成空间", "the three axes span space")]];
    }
    if (!s.sv) return [];
    const f = s.f, deg = (x) => (x * 180 / Math.PI).toFixed(1);
    const atStar = (i) => Math.abs(api.p["j" + i] - [30, -60, 90, -120, -90, 45][i - 1]) < 1e-6;
    if (!api.running) {
      if (Math.abs(f.s3) < 0.005) api.done("elbow");
      if (Math.abs(f.s5) < 0.005) api.done("wrist");
      if ([1, 3, 4, 5, 6].every(atStar) && Math.abs(f.r) < 0.002) api.done("shoulder");
    }
    if (s.done && Math.abs(Math.sin(s.th0[4])) < 0.005 && s.turn6 > 30 * Math.PI / 180 && s.dmax < 5e-4) api.done("self");
    const kinds = [];
    if (Math.abs(f.s3) < 0.01) kinds.push(api.T("肘部", "elbow"));
    if (Math.abs(f.s5) < 0.01) kinds.push(api.T("手腕", "wrist"));
    if (Math.abs(f.r) < 0.004) kinds.push(api.T("肩部", "shoulder"));
    return [[["det J", "det J"], s.det.toFixed(5) + " m³"], [["最小奇异值 σ_min", "smallest singular value σ_min"], s.sv[5].toExponential(3)],
            [["秩（容差 10⁻⁹）", "rank (tolerance 10⁻⁹)"], String(s.rank)],
            [["sin θ₃（肘部）", "sin θ₃ (elbow)"], f.s3.toFixed(4)], [["sin θ₅（手腕）", "sin θ₅ (wrist)"], f.s5.toFixed(4)],
            [["r（肩部）", "r (shoulder)"], (f.r * 1000).toFixed(2) + " mm"],
            [["−L₁L₂ sin θ₃ sin θ₅ · r", "−L₁L₂ sin θ₃ sin θ₅ · r"], (-this.G.L1 * this.G.L2 * f.s3 * f.s5 * f.r).toFixed(5) + " m³"],
            [["奇异类型", "kind of singularity"], kinds.length ? kinds.join(api.T("、", ", ")) : api.T("不奇异", "not singular")],
            [["自运动：θ₆ 转过 / 法兰盘最大位移", "self-motion: θ₆ turned / largest flange displacement"],
             s.t > 0 ? deg(s.turn6) + "° / " + (s.dmax * 1000).toFixed(3) + " mm" : "—"]];
  },

  // ---------------- 三维
  setup3d(api, keep) {
    const arm = api.m["B-ARM-UR5E"], T = api.three;
    arm.root.updateMatrixWorld(true);
    const G = new T.Group(); G.matrixAutoUpdate = false; G.matrix.copy(arm.nodes.root.matrixWorld); api.st.scene.add(G); keep.G = G;
    const g = new T.BufferGeometry(); g.setAttribute("position", new T.BufferAttribute(new Float32Array(2000 * 3), 3)); g.setDrawRange(0, 0);
    keep.trace = new T.Line(g, new T.LineBasicMaterial({ color: 0xc98f00 })); keep.trace.frustumCulled = false; G.add(keep.trace);
    // 六根关节轴（此刻的位置），画成细线
    keep.axes = [0, 1, 2, 3, 4, 5].map(() => { const ge = new T.BufferGeometry(); ge.setAttribute("position", new T.BufferAttribute(new Float32Array(6), 3));
      const l = new T.Line(ge, new T.LineBasicMaterial({ color: 0x1f77b4, transparent: true, opacity: 0.6 })); l.frustumCulled = false; G.add(l); return l; });
    // 云台：偏航（Y，绕 z）→ 俯仰（P，绕 x）→ 横滚（R，绕 y，相机光轴）
    const C = new T.Group(); C.position.set(1.5, 6.0, 0.8); G.add(C); keep.C = C;
    const m = (c) => new T.MeshStandardMaterial({ color: c });
    const base = new T.Mesh(new T.CylinderGeometry(0.12, 0.16, 0.5, 24), m(0x30363d)); base.rotation.x = Math.PI / 2; base.position.set(0, 0, -0.85); C.add(base);
    const Yg = new T.Group(); C.add(Yg); Yg.rotation.z = 0.35; keep.Yg = Yg;
    const r1 = new T.Mesh(new T.TorusGeometry(0.62, 0.025, 12, 64), m(0x8c959f)); r1.rotation.y = Math.PI / 2; Yg.add(r1);   // 外环：在 yz 平面内，俯仰轴（x）穿过它
    const Pg = new T.Group(); Yg.add(Pg); keep.Pg = Pg;
    const r2 = new T.Mesh(new T.TorusGeometry(0.5, 0.025, 12, 64), m(0xb0b7bf)); r2.rotation.x = Math.PI / 2; Pg.add(r2);    // 内环：在 xz 平面内，横滚轴（y）穿过它
    const cam = new T.Mesh(new T.BoxGeometry(0.34, 0.26, 0.22), m(0x1d2327)); Pg.add(cam);
    const lens = new T.Mesh(new T.CylinderGeometry(0.08, 0.08, 0.16, 24), m(0x57606a)); lens.position.set(0, 0.2, 0); Pg.add(lens);
    const line = (c) => { const ge = new T.BufferGeometry(); ge.setAttribute("position", new T.BufferAttribute(new Float32Array(6), 3)); const l = new T.Line(ge, new T.LineBasicMaterial({ color: c })); l.frustumCulled = false; return l; };
    keep.ay = line(0xd62728); C.add(keep.ay); keep.ap = line(0x2ca02c); Yg.add(keep.ap); keep.ar = line(0x1f77b4); Pg.add(keep.ar);
    const set = (l, a, b) => { const p = l.geometry.attributes.position; p.setXYZ(0, ...a); p.setXYZ(1, ...b); p.needsUpdate = true; };
    set(keep.ay, [0, 0, -1.0], [0, 0, 1.0]); set(keep.ap, [-0.9, 0, 0], [0.9, 0, 0]); set(keep.ar, [0, -0.9, 0], [0, 0.9, 0]);
    keep.setLine = set;
    keep.box = () => { G.updateMatrixWorld(true); return new T.Box3().setFromObject(C).expandByScalar(0.3); };
    api.m.gimView = { entry: { robot: {} }, holder: { visible: false }, box: () => keep.box() };
  },
  draw(api, s) {
    const arm = api.m["B-ARM-UR5E"], k = api.keep, ur = api.scene === "ur";
    if (!k.G) return;
    if (k.shown !== api.scene) { k.shown = api.scene; if (ur) api.view(35, 25, 0.5, arm); else api.view(30, 20, 0.8, api.m.gimView); }
    arm.holder.visible = ur; k.C.visible = !ur; k.trace.visible = ur; k.axes.forEach((l) => { l.visible = ur; });
    if (ur && s.th) {
      const o = {}; this.J.forEach((n, i) => { o[n] = s.th[i]; }); arm.set(o);
      // 关节轴此刻的位置：沿轴方向画 ±0.25 m
      const A = this.AX();
      let P = { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] };
      for (let i = 0; i < 6; i++) {
        const w = this.mv(P.R, A[i][0]), q = this.act(P, A[i][1]);
        k.setLine(k.axes[i], this.add(q, this.mul(w, -0.25)), this.add(q, this.mul(w, 0.25)));
        P = this.comp(P, this.E(i, s.th[i]));
      }
      const a = k.trace.geometry.attributes.position, pts = s.trace.slice(-2000);
      pts.forEach((p, i) => a.setXYZ(i, p[0], p[1], p[2])); a.needsUpdate = true; k.trace.geometry.setDrawRange(0, pts.length);
    }
    if (!ur) k.Pg.rotation.x = (s.p || 0);
  },
});
