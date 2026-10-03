// 实验 14.4 腕心与解耦（配 14.4 节）。球形手腕六轴臂（表 14.4.1：肩高 0.163、大臂 0.425、小臂 0.392、腕长 0.1 m），
// 零件库里没有这种机械臂，本实验用圆柱和小球搭出它，正运动学按指数积公式（旋量轴同表 14.4.1）计算。
// 目标用“腕心位置 + 末端姿态（ZYX 欧拉角：偏航、俯仰、横滚，式 (4.5.4)）”给出，法兰盘中心 = 腕心 + D₆ x_b。
// 逆解按 14.4.4 节四步：子问题 3 求 θ₃，子问题 2 求 θ₁、θ₂，子问题 2 求 θ₄、θ₅，子问题 1 求 θ₆；8 组解的次序与表 14.4.2 相同
// （肩前在前、肘下在前、腕不翻在前）。测量区的“末端误差”把显示的解代回正运动学，与目标比较。
WQ.lab({
  title: ["实验 14.4 腕心与解耦", "Lab 14.4 The wrist centre and decoupling"],
  goal: ["看球形手腕六轴臂怎样把位置和姿态分开求解：前三个关节只管腕心，后三个关节只管姿态；比较 8 组解。",
         "See how a spherical-wrist arm splits position from orientation: joints 1–3 only place the wrist centre, joints 4–6 only set the orientation; compare the eight solutions."],
  view: "3d",
  models: [],
  scenes: [
    { id: "arm", robot: true, name: ["球形手腕六轴臂", "Six-axis arm with a spherical wrist"], hide: ["tilt"],
      problem: { title: ["机器人问题：位置和姿态能不能分开求", "Robot problem: can position and orientation be solved apart"],
                 text: ["用滑块给出腕心的位置和末端的姿态（虚线坐标系是目标），界面求出 8 组逆解，用“解的编号”选择显示哪一组。金色小球是腕心。",
                        "Sliders give the wrist-centre position and the tool orientation (dashed frame = target). All eight solutions are computed; “solution” picks the one shown. The gold ball is the wrist centre."] } },
    { id: "cup", name: ["端水倒水", "Pouring a glass of water"], hide: ["wx", "wy", "wz", "yaw", "pitch", "roll", "k"],
      problem: { title: ["生活中的例子：手不动，只转手腕", "Everyday example: the hand stays, only the wrist turns"],
                 text: ["手（腕心）停在杯口上方不动，拖动“倾斜角”把杯子转过来倒水。观察哪几个关节在动。",
                        "The hand (wrist centre) stays above the glass; drag “tilt” to turn the cup and pour. Watch which joints move."] } },
  ],
  params: [
    { id: "wx", name: ["腕心 x", "wrist x"], min: -0.8, max: 0.8, step: 0.0001, value: 0.576, unit: "m", digits: 4 },
    { id: "wy", name: ["腕心 y", "wrist y"], min: -0.8, max: 0.8, step: 0.0001, value: 0.3325, unit: "m", digits: 4 },
    { id: "wz", name: ["腕心 z", "wrist z"], min: -0.4, max: 0.9, step: 0.0001, value: 0.2402, unit: "m", digits: 4 },
    { id: "yaw", name: ["偏航 ψ（绕 z）", "yaw ψ (about z)"], min: -180, max: 180, step: 0.01, value: 14.05, unit: "°", digits: 2 },
    { id: "pitch", name: ["俯仰 θ（绕 y）", "pitch θ (about y)"], min: -89, max: 89, step: 0.01, value: -17.58, unit: "°", digits: 2 },
    { id: "roll", name: ["横滚 φ（绕 x）", "roll φ (about x)"], min: -180, max: 180, step: 0.01, value: -11.9, unit: "°", digits: 2 },
    { id: "k", name: ["解的编号（1–8，同表 14.4.2）", "solution (1–8, as Table 14.4.2)"], min: 1, max: 8, step: 1, value: 3, unit: "", digits: 0 },
    { id: "tilt", name: ["杯子倾斜角", "cup tilt"], min: 0, max: 120, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 14.4.1（默认的目标），找到与 θ* = (30°, 40°, −70°, 20°, 50°, −30°) 相同的一组（第 3 组）。",
                                     "Example 14.4.1 (the default target): find the solution equal to θ* = (30°, 40°, −70°, 20°, 50°, −30°) (number 3)."],
      demo: { scene: "arm", set: { wx: 0.576, wy: 0.3325, wz: 0.2402, yaw: 14.05, pitch: -17.58, roll: -11.9, k: 3 }, press: [], wait: 1 } },
    { id: "dec", robot: true, text: ["腕心不动，把姿态改变 20° 以上：θ₁、θ₂、θ₃ 与原来完全相同。", "Keep the wrist centre and change the orientation by more than 20°: θ₁, θ₂, θ₃ stay exactly the same."],
      demo: { scene: "arm", set: { wx: 0.576, wy: 0.3325, wz: 0.2402, yaw: 44.05, pitch: 5, roll: 20, k: 3 }, press: [], wait: 1 } },
    { id: "flip", robot: true, text: ["在算例 14.4.1 的目标下切换到第 4 组：只有手腕在动，θ₅ 变号。", "At the target of Example 14.4.1 switch to solution 4: only the wrist moves and θ₅ changes sign."],
      demo: { scene: "arm", set: { wx: 0.576, wy: 0.3325, wz: 0.2402, yaw: 14.05, pitch: -17.58, roll: -11.9, k: 4 }, press: [], wait: 1 } },
    { id: "sing", robot: true, text: ["调整姿态，让第 3 组解的 |θ₅| 小于 2°（接近手腕奇异），观察 θ₄、θ₆。", "Adjust the orientation so that |θ₅| of solution 3 is under 2° (near the wrist singularity); watch θ₄ and θ₆."],
      demo: { scene: "arm", set: { wx: 0.576, wy: 0.3325, wz: 0.2402, yaw: 30, pitch: 30, roll: -0.36, k: 3 }, press: [], wait: 1 } },
    { id: "cup", text: ["生活场景：把杯子倾斜到 90° 以上倒水，前三个关节始终不动。", "Everyday scene: tilt the cup past 90° to pour; the first three joints never move."],
      demo: { scene: "cup", set: { tilt: 100 }, press: [], wait: 1 } },
  ],
  think: ["球形手腕的手腕翻转为什么不改变前三个关节，而 UR5e 的手腕翻转会改变 θ₂、θ₃、θ₄（表 14.5.1）？",
          "Why does a wrist flip leave joints 1–3 alone on a spherical wrist, but change θ₂, θ₃, θ₄ on the UR5e (Table 14.5.1)?"],

  // ---------------- 小型线性代数
  H1: 0.163, LA: 0.425, LB: 0.392, D6: 0.1,
  dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  add(a, b) { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; },
  sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; },
  mul(a, s) { return [a[0] * s, a[1] * s, a[2] * s]; },
  norm(a) { return Math.hypot(a[0], a[1], a[2]); },
  mv(R, v) { return [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]); },
  mm(A, B) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j])); },
  tr(A) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[j][i])); },
  rot(w, t) {                            // 罗德里格斯公式 (4.4.5)
    const c = Math.cos(t), s = Math.sin(t), v = 1 - c, [x, y, z] = w;
    return [[c + x * x * v, x * y * v - z * s, x * z * v + y * s], [y * x * v + z * s, c + y * y * v, y * z * v - x * s], [z * x * v - y * s, z * y * v + x * s, c + z * z * v]];
  },
  E(i, t) { const [w, q] = this.AX()[i], R = this.rot(w, t); return { R, p: this.sub(q, this.mv(R, q)) }; },   // 绕过 q 的轴转动
  comp(A, B) { return { R: this.mm(A.R, B.R), p: this.add(this.mv(A.R, B.p), A.p) }; },
  inv(A) { const Rt = this.tr(A.R); return { R: Rt, p: this.mul(this.mv(Rt, A.p), -1) }; },
  act(A, x) { return this.add(this.mv(A.R, x), A.p); },
  AX() {
    const PW = [this.LA + this.LB, 0, this.H1], X = [1, 0, 0], Y = [0, -1, 0];
    return [[[0, 0, 1], [0, 0, 0]], [Y, [0, 0, this.H1]], [Y, [this.LA, 0, this.H1]], [X, PW], [Y, PW], [X, PW]];
  },
  M() { return { R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [this.LA + this.LB + this.D6, 0, this.H1] }; },
  fkAll(th) {                            // 每个关节之后的累积变换 T_k（k = 0…6）
    const Ts = [{ R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] }];
    th.forEach((t, i) => Ts.push(this.comp(Ts[i], this.E(i, t))));
    return Ts;
  },
  // ---------------- 帕登-卡汉子问题（14.3 节）
  sp1(w, r, p, q) {
    const u = this.sub(p, r), v = this.sub(q, r), up = this.sub(u, this.mul(w, this.dot(w, u))), vp = this.sub(v, this.mul(w, this.dot(w, v)));
    if (this.norm(up) < 1e-12) return 0;
    return Math.atan2(this.dot(w, this.cross(up, vp)), this.dot(up, vp));
  },
  sp2(w1, w2, r, p, q) {
    const u = this.sub(p, r), v = this.sub(q, r), k = this.dot(w1, w2), den = k * k - 1;
    const a = (k * this.dot(w2, u) - this.dot(w1, v)) / den, b = (k * this.dot(w1, v) - this.dot(w2, u)) / den, n = this.cross(w1, w2);
    const g2 = (this.dot(u, u) - a * a - b * b - 2 * a * b * k) / this.dot(n, n);
    if (g2 < -1e-10) return [];
    const gs = g2 <= 1e-10 ? [0, 0] : [Math.sqrt(g2), -Math.sqrt(g2)];
    return gs.map((g) => { const c = this.add(r, this.add(this.add(this.mul(w1, a), this.mul(w2, b)), this.mul(n, g)));
      return [this.sp1(w1, r, c, q), this.sp1(w2, r, p, c)]; });
  },
  sp3(w, r, p, q, d) {
    const u = this.sub(p, r), v = this.sub(q, r), up = this.sub(u, this.mul(w, this.dot(w, u))), vp = this.sub(v, this.mul(w, this.dot(w, v)));
    const d2 = d * d - Math.pow(this.dot(w, this.sub(p, q)), 2), nu = this.norm(up), nv = this.norm(vp);
    const t0 = Math.atan2(this.dot(w, this.cross(up, vp)), this.dot(up, vp)), c = (nu * nu + nv * nv - d2) / (2 * nu * nv);
    if (d2 < -1e-12 || Math.abs(c) > 1 + 1e-12) return [];
    const ph = Math.atan2(Math.sqrt(Math.max(0, 1 - c * c)), Math.max(-1, Math.min(1, c)));
    return ph < 1e-9 ? [t0, t0] : [t0 + ph, t0 - ph];
  },
  wrap(a) { return Math.atan2(Math.sin(a), Math.cos(a)); },
  // ---------------- 逆解：14.4.4 节四步，排序同表 14.4.2
  ik(Td) {
    const A = this.AX(), PW = A[3][1], q2 = A[1][1], g = this.comp(Td, this.inv(this.M())), pw = this.act(g, PW), out = [];
    for (const t3 of this.sp3(A[2][0], A[2][1], PW, q2, this.norm(this.sub(pw, q2)))) {
      const a = this.act(this.E(2, t3), PW);
      for (const [t1, t2] of this.sp2(A[0][0], A[1][0], q2, a, pw)) {
        const h = this.comp(this.inv(this.comp(this.comp(this.E(0, t1), this.E(1, t2)), this.E(2, t3))), g);
        const p6 = this.add(PW, [0.1, 0, 0]), pt = this.add(PW, [0, 0, 0.1]);
        for (const [t4, t5] of this.sp2(A[3][0], A[4][0], PW, p6, this.act(h, p6))) {
          const k = this.comp(this.inv(this.comp(this.E(3, t4), this.E(4, t5))), h);
          const t6 = this.sp1(A[5][0], PW, pt, this.act(k, pt));
          const th = [t1, t2, t3, t4, t5, t6].map((x) => this.wrap(x));
          out.push({ th, lab: this.labels(th, pw) });
        }
      }
    }
    out.sort((x, y) => (y.lab[0] - x.lab[0]) || (y.lab[1] - x.lab[1]) || (y.lab[2] - x.lab[2]));
    return out;
  },
  labels(th, pw) {
    const sh0 = [0, 0, this.H1], x1 = [Math.cos(th[0]), Math.sin(th[0]), 0];
    const sh = this.dot(x1, this.sub(pw, sh0)) > 0 ? 1 : -1;
    const el = this.act(this.comp(this.E(0, th[0]), this.E(1, th[1])), [this.LA, 0, this.H1]);
    let n = this.cross(this.sub(pw, sh0), [-Math.sin(th[0]), Math.cos(th[0]), 0]);
    if (n[2] < 0) n = this.mul(n, -1);
    return [sh, this.dot(this.sub(el, sh0), n) < 0 ? 1 : -1, th[4] > 0 ? 1 : -1];
  },
  target(api) {                          // 目标：腕心 + 姿态（ZYX 欧拉角）；法兰中心 = 腕心 + D₆ x_b
    if (api.scene === "cup") {
      const R = this.rot([1, 0, 0], api.p.tilt * Math.PI / 180), pw = [0.5, 0, 0.35];
      return { R, p: this.add(pw, this.mul([R[0][0], R[1][0], R[2][0]], this.D6)), pw };
    }
    const d = Math.PI / 180, R = this.mm(this.mm(this.rot([0, 0, 1], api.p.yaw * d), this.rot([0, 1, 0], api.p.pitch * d)), this.rot([1, 0, 0], api.p.roll * d));
    const pw = [api.p.wx, api.p.wy, api.p.wz];
    return { R, p: this.add(pw, this.mul([R[0][0], R[1][0], R[2][0]], this.D6)), pw };
  },
  pick(api, sols) {
    if (!sols.length) return null;
    if (api.scene === "cup") return sols.find((s) => s.lab[0] === 1 && s.lab[1] === -1 && s.lab[2] === 1) || sols[0];
    return sols[Math.min(api.p.k, sols.length) - 1];
  },

  // ---------------- 三维显示
  setup3d(api, keep) {
    const T = api.three, mat = (c) => new T.MeshStandardMaterial({ color: c, metalness: 0.2, roughness: 0.6 });
    const root = new T.Group(); root.rotation.x = -Math.PI / 2; api.st.scene.add(root);     // {s}：z 向上
    keep.root = root;
    keep.cyl = (r, c) => { const m = new T.Mesh(new T.CylinderGeometry(r, r, 1, 20), mat(c)); m.castShadow = true; root.add(m); return m; };
    keep.base = keep.cyl(0.06, 0x6b7780); keep.up = keep.cyl(0.04, 0x58a6ff); keep.fore = keep.cyl(0.033, 0x58a6ff); keep.tool = keep.cyl(0.022, 0x9aa6ad);
    keep.joint = [0, 1].map(() => { const m = new T.Mesh(new T.SphereGeometry(0.045, 20, 14), mat(0xdfe6ea)); root.add(m); return m; });
    keep.wc = new T.Mesh(new T.SphereGeometry(0.05, 20, 14), mat(0xd4a017)); root.add(keep.wc);
    keep.ax = [0xd62728, 0x2ca02c, 0x1f77b4].map((c) => { const a = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(), 0.12, c, 0.03, 0.02); root.add(a); return a; });
    keep.tg = [0xd62728, 0x2ca02c, 0x1f77b4].map((c) => { const a = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(), 0.16, c, 0.025, 0.015);
      a.line.material = new T.LineDashedMaterial({ color: c, dashSize: 0.02, gapSize: 0.015 }); a.line.computeLineDistances(); root.add(a); return a; });
    const cup = new T.Group();
    const glass = new T.Mesh(new T.CylinderGeometry(0.04, 0.032, 0.11, 24, 1, true), new T.MeshStandardMaterial({ color: 0xcfe8ff, transparent: true, opacity: 0.45, side: T.DoubleSide }));
    const water = new T.Mesh(new T.CylinderGeometry(0.036, 0.032, 0.06, 24), new T.MeshStandardMaterial({ color: 0x3b82c4, transparent: true, opacity: 0.8 }));
    glass.rotation.x = Math.PI / 2; water.rotation.x = Math.PI / 2; water.position.z = -0.02;
    cup.add(glass, water); root.add(cup); keep.cup = cup; keep.water = water;
    api.m.frame = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-0.3, 0, -0.7), new T.Vector3(0.9, 0.75, 0.35)) };
    keep.viewed = false;
  },
  seg(m, a, b) {                          // 把单位长度的圆柱放在 a、b 两点之间（{s} 坐标）
    const T = this._T, A = new T.Vector3(...a), B = new T.Vector3(...b), d = new T.Vector3().subVectors(B, A), L = d.length();
    m.position.copy(A).addScaledVector(d, 0.5); m.scale.set(1, Math.max(L, 1e-6), 1);
    m.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), d.normalize());
  },
  reset(api, s) { s.ref = null; },
  current(api) {
    const Td = this.target(api), sols = this.ik(Td), sel = this.pick(api, sols);
    return { Td, sols, sel };
  },
  readouts(api, s) {
    if (!api.keep.root) return [];
    const { Td, sols, sel } = this.current(api), d = (v) => (v * 180 / Math.PI).toFixed(2) + "°";
    if (!sel) return [[["状态", "status"], api.T("无解：腕心够不着", "no solution: wrist centre out of reach")]];
    const Ts = this.fkAll(sel.th), Tb = this.comp(Ts[6], this.M()), err = this.norm(this.sub(Tb.p, Td.p));
    const near = (a, b, t) => Math.abs(a - b) < t, ex = near(api.p.wx, 0.576, 1e-6) && near(api.p.wy, 0.3325, 1e-6) && near(api.p.wz, 0.2402, 1e-6);
    const star = [30, 40, -70, 20, 50, -30].map((v) => v * Math.PI / 180);
    if (api.scene === "arm") {
      const exOri = near(api.p.yaw, 14.05, 1e-6) && near(api.p.pitch, -17.58, 1e-6) && near(api.p.roll, -11.9, 1e-6);
      if (ex && exOri && api.p.k === 3 && sel.th.every((v, i) => Math.abs(this.wrap(v - star[i])) < 0.1 * Math.PI / 180)) api.done("ex");
      if (ex && exOri && api.p.k === 4 && sel.lab[2] === -1 && sel.th.slice(0, 3).every((v, i) => Math.abs(this.wrap(v - star[i])) < 0.1 * Math.PI / 180)) api.done("flip");
      const dOri = Math.abs(api.p.yaw - 14.05) + Math.abs(api.p.pitch + 17.58) + Math.abs(api.p.roll + 11.9);
      if (ex && dOri > 20 && api.p.k === 3 && sel.th.slice(0, 3).every((v, i) => Math.abs(this.wrap(v - star[i])) < 0.1 * Math.PI / 180)) api.done("dec");
      if (api.p.k === 3 && Math.abs(sel.th[4]) < 2 * Math.PI / 180) api.done("sing");
    } else if (api.p.tilt >= 90 && err < 1e-9) api.done("cup");
    const L = (x) => [api.T(["后", "", "前"][x[0] + 1], ["back", "", "front"][x[0] + 1]), api.T(["上", "", "下"][x[1] + 1], ["up", "", "down"][x[1] + 1]), api.T(["翻", "", "不翻"][x[2] + 1], ["flip", "", "no flip"][x[2] + 1])].join(" · ");
    return [[["解的个数", "number of solutions"], String(sols.length)],
            [["显示的解（肩 · 肘 · 腕）", "shown (shoulder · elbow · wrist)"], L(sel.lab)],
            [["θ₁, θ₂, θ₃（腕心）", "θ₁, θ₂, θ₃ (wrist centre)"], sel.th.slice(0, 3).map(d).join(", ")],
            [["θ₄, θ₅, θ₆（姿态）", "θ₄, θ₅, θ₆ (orientation)"], sel.th.slice(3).map(d).join(", ")],
            [["腕心", "wrist centre"], `(${Td.pw.map((v) => api.fmt(v, 3)).join(", ")}) m`],
            [["末端误差（代回正运动学）", "tool error (back through FK)"], err.toExponential(1) + " m"]];
  },
  draw(api, s) {
    const K = api.keep, T = api.three;
    if (!K.root) return;
    this._T = T;
    if (!K.viewed) { K.viewed = true; api.view(35, 22, 1.5); }
    const { Td, sel } = this.current(api), A = this.AX();
    const th = sel ? sel.th : [0, 0, 0, 0, 0, 0], Ts = this.fkAll(th), Tb = this.comp(Ts[6], this.M());
    const sh = [0, 0, this.H1], el = this.act(Ts[2], [this.LA, 0, this.H1]), wc = this.act(Ts[3], A[3][1]);
    this.seg(K.base, [0, 0, 0], sh); this.seg(K.up, sh, el); this.seg(K.fore, el, wc); this.seg(K.tool, wc, Tb.p);
    [sh, el].forEach((p, i) => K.joint[i].position.set(...p));
    K.wc.position.set(...wc);
    for (let i = 0; i < 3; i++) {
      K.ax[i].position.set(...Tb.p); K.ax[i].setDirection(new T.Vector3(Tb.R[0][i], Tb.R[1][i], Tb.R[2][i]));
      K.tg[i].position.set(...Td.p); K.tg[i].setDirection(new T.Vector3(Td.R[0][i], Td.R[1][i], Td.R[2][i]));
      K.tg[i].visible = api.scene === "arm";
    }
    K.cup.visible = api.scene === "cup";
    if (api.scene === "cup") {
      const z = [Tb.R[0][2], Tb.R[1][2], Tb.R[2][2]], c = this.add(Tb.p, this.mul([Tb.R[0][0], Tb.R[1][0], Tb.R[2][0]], 0.045));
      K.cup.position.set(...c);
      K.cup.quaternion.setFromRotationMatrix(new T.Matrix4().set(Tb.R[0][0], Tb.R[0][1], Tb.R[0][2], 0, Tb.R[1][0], Tb.R[1][1], Tb.R[1][2], 0, Tb.R[2][0], Tb.R[2][1], Tb.R[2][2], 0, 0, 0, 0, 1));
      K.water.visible = api.p.tilt < 90 || z[2] > -0.2;
    }
  },
});
