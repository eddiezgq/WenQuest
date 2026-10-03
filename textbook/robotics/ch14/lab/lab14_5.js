// 实验 14.5 UR5e 的八种构型（配 14.5 节）。零件库 UR5e 复制成 8 台，排成两行，每台显示一组逆解。
// 逆解按 14.5 节三步（旋量轴、零位位姿取表 12.1.1）：
//   θ₁：手腕点 p_w = p − W₄ y_b，x sin θ₁ − y cos θ₁ = d₄（式 (14.5.3)、(14.5.4)）；
//   θ₅、θ₆：R₅R₆ v = ω₂，v = R_gᵀω₂，R_g = R₁ᵀ R_d R_Mᵀ（式 (14.5.5)、(14.5.6)），子问题 2；
//   θ₃、θ₂、θ₄：子问题 3（式 (14.5.9)）、子问题 1、子问题 1（求 θ₄ 用 q₆，q₅ 在轴 4 上）。
// 次序与表 14.5.1 相同：肩 A 在前、腕不翻在前、肘上在前。“模型核对”把选中的解送进零件库模型（与指数积无关的三维引擎算法），
// 读出法兰盘中心与目标之差。模型 base 连杆相对 {s} 绕 z 转了 180°：local() 读出的 (x, y, z) 换成 (−x, −y, z)。
WQ.lab({
  title: ["实验 14.5 UR5e 的八种构型", "Lab 14.5 The eight configurations of the UR5e"],
  goal: ["同时看到 UR5e 到达同一位姿的全部逆解，认识肩、肘、腕三个“二选一”，并按条件挑选一组。",
         "See every UR5e solution for one pose side by side, recognise the three two-way choices (shoulder, elbow, wrist), and pick one that meets the conditions."],
  view: "3d",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "ur", robot: true, name: ["八组逆解", "Eight solutions"],
      problem: { title: ["机器人问题：同一个位姿，选哪一种手臂", "Robot problem: one pose, which arm"],
                 text: ["用滑块给出法兰盘中心的位置和末端姿态（ZYX 欧拉角），八台 UR5e 同时显示全部逆解（红点是目标）。“解的编号”选中的一台不透明，测量区显示它的关节角和模型核对的误差。",
                        "Sliders give the flange position and the tool orientation (ZYX Euler angles); eight UR5e show every solution at once (red dot = target). The one picked by “solution” is opaque; its joint angles and the model check are shown."] } },
    { id: "switch", name: ["按墙上的开关", "Pressing a wall switch"], hide: ["px", "py", "pz", "yaw", "pitch", "roll"],
      problem: { title: ["生活中的例子：伸手按开关，手臂可以怎样摆", "Everyday example: reaching a light switch, how can the arm sit"],
                 text: ["法兰盘要正对墙上的开关按下去，就像人伸手按开关。有的姿势会撞到台面或穿过墙（标红），要从其余的里面挑。",
                        "The flange must press the switch on the wall head-on, as a person reaches for a switch. Some postures hit the table or pass through the wall (shown red); choose among the rest."] } },
  ],
  params: [
    { id: "px", name: ["法兰中心 x", "flange x"], min: -0.85, max: 0.85, step: 0.0001, value: -0.4976, unit: "m", digits: 4 },
    { id: "py", name: ["法兰中心 y", "flange y"], min: -0.85, max: 0.85, step: 0.0001, value: -0.442, unit: "m", digits: 4 },
    { id: "pz", name: ["法兰中心 z", "flange z"], min: -0.4, max: 1.0, step: 0.0001, value: 0.2351, unit: "m", digits: 4 },
    { id: "yaw", name: ["偏航 ψ", "yaw ψ"], min: -180, max: 180, step: 0.01, value: 75, unit: "°", digits: 2 },
    { id: "pitch", name: ["俯仰 θ", "pitch θ"], min: -89, max: 89, step: 0.01, value: 0, unit: "°", digits: 2 },
    { id: "roll", name: ["横滚 φ", "roll φ"], min: -180, max: 180, step: 0.01, value: -90, unit: "°", digits: 2 },
    { id: "k", name: ["解的编号（1–8，同表 14.5.1）", "solution (1–8, as Table 14.5.1)"], min: 1, max: 8, step: 1, value: 1, unit: "", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 14.5.1（默认目标）：找到与 θ* = (30°, −60°, 90°, −120°, −90°, 45°) 相同的一组（第 3 组），模型核对误差小于 10⁻⁹ m。",
                                     "Example 14.5.1 (default target): find the solution equal to θ* = (30°, −60°, 90°, −120°, −90°, 45°) (number 3); the model check is below 10⁻⁹ m."],
      demo: { scene: "ur", set: { px: -0.4976, py: -0.442, pz: 0.2351, yaw: 75, pitch: 0, roll: -90, k: 3 }, press: [], wait: 1 } },
    { id: "down", robot: true, text: ["在同一目标下选一组肘下的解。", "At the same target pick an elbow-down solution."],
      demo: { scene: "ur", set: { px: -0.4976, py: -0.442, pz: 0.2351, yaw: 75, pitch: 0, roll: -90, k: 2 }, press: [], wait: 1 } },
    { id: "flip", robot: true, text: ["选出与 θ* 只差手腕翻转的一组（第 1 组）：θ₅ 变号、θ₆ 相差 180°。", "Pick the solution that differs from θ* only by the wrist flip (number 1): θ₅ changes sign, θ₆ moves by 180°."],
      demo: { scene: "ur", set: { px: -0.4976, py: -0.442, pz: 0.2351, yaw: 75, pitch: 0, roll: -90, k: 1 }, press: [], wait: 1 } },
    { id: "shoulder", robot: true, text: ["把法兰中心移近基座轴线，使肩 A、肩 B 两组的 θ₁ 相差小于 40°（接近肩部奇异）。", "Bring the flange near the base axis until θ₁ of shoulders A and B differ by less than 40° (near the shoulder singularity)."],
      demo: { scene: "ur", set: { px: -0.1047, py: -0.093, pz: 0.2351, yaw: 75, pitch: 0, roll: -90, k: 1 }, press: [], wait: 1 } },
    { id: "switch", text: ["生活场景：选一组肩 B、既不碰台面也不穿墙的解按下开关。", "Everyday scene: press the switch with a shoulder-B solution that neither hits the table nor passes through the wall."],
      demo: { scene: "switch", set: { k: 7 }, press: [], wait: 1 } },
  ],
  think: ["八组解中，为什么手腕翻转的两组 θ₂、θ₃、θ₄ 也不同，而球形手腕的机械臂只变 θ₄、θ₅、θ₆？", "Why do the two wrist-flip solutions also differ in θ₂, θ₃, θ₄ here, while a spherical wrist only changes θ₄, θ₅, θ₆?"],

  // ---------------- UR5e 几何（表 12.1.1）与小型线性代数
  G: { H1: 0.163, W1: 0.138, L1: 0.425, W2: 0.131, L2: 0.392, W3: 0.127, H2: 0.1, W4: 0.1 },
  J: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
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
  wrap(a) { return Math.atan2(Math.sin(a), Math.cos(a)); },
  AX() {
    const g = this.G, Y = [0, -1, 0];
    return [[[0, 0, 1], [0, 0, g.H1]], [Y, [0, -g.W1, g.H1]], [Y, [-g.L1, -g.W1 + g.W2, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2, g.H1]],
            [[0, 0, -1], [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1 - g.H2]]];
  },
  M() { const g = this.G; return { R: [[1, 0, 0], [0, -1, 0], [0, 0, -1]], p: [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3 - g.W4, g.H1 - g.H2] }; },
  E(i, t) { const [w, q] = this.AX()[i], R = this.rot(w, t); return { R, p: this.sub(q, this.mv(R, q)) }; },
  comp(A, B) { return { R: this.mm(A.R, B.R), p: this.add(this.mv(A.R, B.p), A.p) }; },
  inv(A) { const Rt = this.tr(A.R); return { R: Rt, p: this.mul(this.mv(Rt, A.p), -1) }; },
  act(A, x) { return this.add(this.mv(A.R, x), A.p); },
  sp1(w, r, p, q) {
    const u = this.sub(p, r), v = this.sub(q, r), up = this.sub(u, this.mul(w, this.dot(w, u))), vp = this.sub(v, this.mul(w, this.dot(w, v)));
    return this.norm(up) < 1e-12 ? 0 : Math.atan2(this.dot(w, this.cross(up, vp)), this.dot(up, vp));
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
    return ph < 1e-9 ? [t0] : [t0 + ph, t0 - ph];
  },
  // ---------------- 逆解（14.5 节三步）
  ik(Td) {
    const g = this.G, A = this.AX(), Y = [0, -1, 0], d4 = g.W1 - g.W2 + g.W3, out = [];
    const yb = [Td.R[0][1], Td.R[1][1], Td.R[2][1]], pw = this.sub(Td.p, this.mul(yb, g.W4)), rho = Math.hypot(pw[0], pw[1]);
    if (rho < d4 - 1e-12) return out;
    const base = Math.atan2(pw[0], -pw[1]), gam = Math.atan2(Math.sqrt(Math.max(0, rho * rho - d4 * d4)), d4);
    [[1, base + gam], [-1, base - gam]].forEach(([s1, t1]) => {
      const E1i = this.E(0, -t1), Rg = this.mm(this.mm(E1i.R, Td.R), this.tr(this.M().R)), v = this.mv(this.tr(Rg), Y);
      const P56 = A[5][1];
      this.sp2(A[4][0], A[5][0], P56, this.add(P56, v), this.add(P56, Y)).forEach(([t5, t6]) => {
        const gg = this.comp(this.comp(this.comp(this.comp(E1i, Td), this.inv(this.M())), this.E(5, -t6)), this.E(4, -t5));
        const p4 = this.act(gg, A[3][1]);
        this.sp3(A[2][0], A[2][1], A[3][1], A[1][1], this.norm(this.sub(p4, A[1][1]))).forEach((t3) => {
          const t2 = this.sp1(A[1][0], A[1][1], this.act(this.E(2, t3), A[3][1]), p4);
          const h = this.comp(this.inv(this.comp(this.E(1, t2), this.E(2, t3))), gg);
          const t4 = this.sp1(A[3][0], A[3][1], A[5][1], this.act(h, A[5][1]));
          const th = [t1, t2, t3, t4, t5, t6].map((x) => this.wrap(x));
          out.push({ th, sh: s1, nf: t5 > 0, up: this.elbowUp(th) });
        });
      });
    });
    out.sort((a, b) => (b.sh - a.sh) || (Number(b.nf) - Number(a.nf)) || (Number(b.up) - Number(a.up)));
    return out;
  },
  chain(th) {                            // 连杆折线（同程序 14.5.1 的 ur_points）
    const A = this.AX(), g = this.G, Ts = [{ R: [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p: [0, 0, 0] }];
    th.forEach((t, i) => Ts.push(this.comp(Ts[i], this.E(i, t))));
    const q = A.map((x) => x[1]);
    return [[0, [0, 0, 0]], [0, q[0]], [1, q[1]], [2, this.add(q[1], [-g.L1, 0, 0])], [2, q[2]], [3, q[3]], [4, q[4]], [5, q[5]], [6, this.add(q[5], [0, -g.W4, 0])]]
      .map(([k, p]) => this.act(Ts[k], p));
  },
  elbowUp(th) {
    const P = this.chain(th), sh = P[2], el = P[4], wr = P[5], ax = this.mv(this.rot([0, 0, 1], th[0]), [0, -1, 0]);
    let n = this.cross(ax, this.sub(wr, sh));
    if (n[2] < 0) n = this.mul(n, -1);
    return this.dot(this.sub(el, sh), n) > 0;
  },
  target(api) {
    if (api.scene === "switch") return { R: [[0, -1, 0], [0, 0, -1], [1, 0, 0]], p: [-0.55, -0.3, 0.35] };   // x_b 向上、y_b 指向墙（−x）
    const d = Math.PI / 180, R = this.mm(this.mm(this.rot([0, 0, 1], api.p.yaw * d), this.rot([0, 1, 0], api.p.pitch * d)), this.rot([1, 0, 0], api.p.roll * d));
    return { R, p: [api.p.px, api.p.py, api.p.pz] };
  },
  blocked(th) { const P = this.chain(th); return P.slice(2).some((p) => p[2] < -1e-9) || P.some((p) => p[0] < -0.551); },

  // ---------------- 三维：8 台复制的 UR5e
  setup3d(api, keep) {
    const T = api.three, arm = api.m["B-ARM-UR5E"];
    arm.place(0, 0);
    arm.visible(false);                                  // 原模型不显示，只用来做“模型核对”
    const y0 = arm.holder.position.y;
    keep.copies = [];
    for (let i = 0; i < 8; i++) {
      const c = arm.holder.clone(true);
      c.visible = true;
      c.traverse((o) => { if (o.isMesh && o.material) { o.material = o.material.clone(); o.material.transparent = true; } });
      c.position.set(-1.95 + 1.3 * (i % 4), y0, i < 4 ? -0.7 : 0.7);
      api.st.scene.add(c);
      const nodes = {}; c.traverse((o) => { if (o.name) nodes[o.name] = o; });
      const tgt = new T.Mesh(new T.SphereGeometry(0.03, 16, 12), new T.MeshBasicMaterial({ color: 0xd62728 }));
      nodes.root.add(tgt);
      const wall = new T.Mesh(new T.BoxGeometry(0.02, 0.8, 0.6), new T.MeshStandardMaterial({ color: 0xc8b88a, transparent: true, opacity: 0.25 }));
      wall.position.set(-0.57, -0.3, 0.35); nodes.root.add(wall);
      const cv = document.createElement("canvas"); cv.width = 256; cv.height = 64;
      const tex = new T.CanvasTexture(cv), lab = new T.Sprite(new T.SpriteMaterial({ map: tex, transparent: true }));
      lab.scale.set(1.0, 0.25, 1); lab.position.set(c.position.x, 0.05, c.position.z + 0.5); api.st.scene.add(lab);
      keep.copies.push({ c, nodes, tgt, wall, cv, tex, lab, txt: "" });
    }
    api.m.frame = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-2.5, 0, -1.2), new T.Vector3(2.5, 0.9, 1.2)) };
    keep.viewed = false;
  },
  setJoints(cp, th) {
    const arm = this._arm, T = this._T;
    this.J.forEach((n, i) => {
      const j = arm.joints[n], node = cp.nodes[j.child];
      node.quaternion.copy(j.q0).multiply(new T.Quaternion().setFromAxisAngle(j.axisV, th[i]));
    });
    cp.c.updateMatrixWorld(true);
  },
  label(cp, text, bad) {
    if (cp.txt === text + bad) return;
    cp.txt = text + bad;
    const g = cp.cv.getContext("2d");
    g.clearRect(0, 0, 256, 64); g.fillStyle = bad ? "#cf222e" : "#1f2a33"; g.font = "bold 30px sans-serif"; g.textAlign = "center"; g.textBaseline = "middle";
    g.fillText(text, 128, 32); cp.tex.needsUpdate = true;
  },
  reset(api, s) {},
  readouts(api, s) {
    const arm = api.m["B-ARM-UR5E"];
    if (!arm || !api.keep.copies) return [];
    const Td = this.target(api), sols = this.ik(Td), d = (v) => (v * 180 / Math.PI).toFixed(2) + "°";
    if (!sols.length) return [[["状态", "status"], api.T("无解：目标不可达", "no solution: target out of reach")]];
    const k = Math.min(api.p.k, sols.length) - 1, sel = sols[k], o = {};
    this.J.forEach((n, i) => { o[n] = sel.th[i]; });
    arm.set(o);
    const f = arm.local("wrist_3_link", [0, 0.1, 0]), err = Math.hypot(-f[0] - Td.p[0], -f[1] - Td.p[1], f[2] - Td.p[2]);
    const star = [30, -60, 90, -120, -90, 45].map((v) => v * Math.PI / 180), near = (a, b) => Math.abs(a - b) < 1e-6;
    const exT = near(api.p.px, -0.4976) && near(api.p.py, -0.442) && near(api.p.pz, 0.2351) && near(api.p.yaw, 75) && near(api.p.pitch, 0) && near(api.p.roll, -90);
    if (api.scene === "ur") {
      if (exT && api.p.k === 3 && err < 1e-9 && sel.th.every((v, i) => Math.abs(this.wrap(v - star[i])) < 0.05 * Math.PI / 180)) api.done("ex");
      if (exT && !sel.up) api.done("down");
      if (exT && api.p.k === 1 && sel.sh === 1 && sel.up && sel.nf) api.done("flip");
      const A = sols.find((x) => x.sh === 1), B = sols.find((x) => x.sh === -1);
      if (A && B && Math.abs(this.wrap(A.th[0] - B.th[0])) < 40 * Math.PI / 180) api.done("shoulder");
    } else if (sel.sh === -1 && !this.blocked(sel.th)) api.done("switch");
    const lab = `${sel.sh > 0 ? "A" : "B"} · ${sel.up ? api.T("上", "up") : api.T("下", "down")} · ${sel.nf ? api.T("不翻", "no flip") : api.T("翻", "flip")}`;
    const rows = [[["解的个数", "number of solutions"], String(sols.length)],
                  [["选中（肩 · 肘 · 腕）", "picked (shoulder · elbow · wrist)"], `${k + 1}: ${lab}`],
                  [["θ₁, θ₂, θ₃", "θ₁, θ₂, θ₃"], sel.th.slice(0, 3).map(d).join(", ")],
                  [["θ₄, θ₅, θ₆", "θ₄, θ₅, θ₆"], sel.th.slice(3).map(d).join(", ")],
                  [["模型核对：法兰中心误差", "model check: flange error"], err.toExponential(1) + " m"]];
    if (api.scene === "switch") rows.push([["碰台面或穿墙", "hits table or wall"], this.blocked(sel.th) ? api.T("是", "yes") : api.T("否", "no")]);
    const A = sols.find((x) => x.sh === 1), B = sols.find((x) => x.sh === -1);
    if (A && B) rows.push([["肩 A、肩 B 的 θ₁ 之差", "θ₁ of shoulder A minus B"], d(Math.abs(this.wrap(A.th[0] - B.th[0])))]);
    return rows;
  },
  draw(api, s) {
    const K = api.keep, arm = api.m["B-ARM-UR5E"];
    if (!K.copies) return;
    this._arm = arm; this._T = api.three;
    if (!K.viewed) { K.viewed = true; api.view(0, 40, 1.7); }
    const Td = this.target(api), sols = this.ik(Td), k = Math.min(api.p.k, Math.max(sols.length, 1)) - 1;
    K.copies.forEach((cp, i) => {
      const sol = sols[i];
      cp.c.visible = !!sol; cp.lab.visible = !!sol;
      cp.tgt.position.set(...Td.p); cp.wall.visible = api.scene === "switch";
      if (!sol) return;
      this.setJoints(cp, sol.th);
      const bad = api.scene === "switch" && this.blocked(sol.th);
      const op = i === k ? 1 : 0.32;
      cp.c.traverse((o) => { if (o.isMesh && o.material && o !== cp.wall && o !== cp.tgt) { o.material.opacity = op; o.material.color && bad && o.material.emissive && o.material.emissive.setHex(0x550000); if (!bad && o.material.emissive) o.material.emissive.setHex(0x000000); } });
      this.label(cp, `${i + 1}  ${sol.sh > 0 ? "A" : "B"} ${sol.up ? api.T("上", "up") : api.T("下", "dn")} ${sol.nf ? api.T("不翻", "-") : api.T("翻", "flip")}`, bad);
    });
  },
});
