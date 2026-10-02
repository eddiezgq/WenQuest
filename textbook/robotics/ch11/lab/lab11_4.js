// 实验 11.4 UR5e 与 SCARA 的工作空间对比（配 11.4 节）。
// “扫描”按钮随机抽取关节变量（在限位以内），把末端点画成点云，就是可达工作空间的样本。
// UR5e 场景另外按解析逆运动学（与程序 11.4.1 的 ur_reachable 相同的算法，标准 DH 参数取零件库模型尺寸），
// 检查法兰中心在当前位置时，100 个法兰法线方向（斐波那契球面网格）中有几个能够到达：100 个都行即在灵巧工作空间内。
// 模型的 base 连杆相对 {s} 绕 z 转了 180°，读数 (x, y, z) 换成 (−x, −y, z)（同实验 12.3）。
WQ.lab({
  title: ["实验 11.4 UR5e 与 SCARA 的工作空间", "Lab 11.4 Workspaces of the UR5e and the SCARA"],
  goal: ["扫描两台机器人的可达工作空间，并在 UR5e 上找出灵巧工作空间内和边缘处的点，比较两种结构的工作空间。",
         "Sample the reachable workspaces of both robots, find points inside the UR5e's dexterous workspace and near its edge, and compare the two designs."],
  view: "3d",
  models: ["B-ARM-UR5E", "B-SCA-WQ4", "B-HUM-G1"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e", "UR5e"], hide: ["d3"],
      problem: { title: ["机器人问题：这个工位，UR5e 够得着吗", "Robot problem: can the UR5e serve this station?"],
                 text: ["够得着（可达）还不够：要以需要的姿态够着。测量区显示当前法兰中心能以 100 个方向中的几个到达。",
                        "Reaching is not enough; it must reach in the needed orientation. The readout shows in how many of 100 directions the flange centre can be reached here."] } },
    { id: "scara", robot: true, name: ["SCARA", "SCARA"], hide: ["j3", "j5", "j6"],
      problem: { title: ["机器人问题：SCARA 的工作空间", "Robot problem: the SCARA's workspace"],
                 text: ["两段水平臂决定水平位置，丝杠决定高度，关节 4 决定工具转向。它的工作空间是一个缺了一块的扁圆环柱。",
                        "Two horizontal links set the position, the screw the height, joint 4 the heading. Its workspace is a flat annular slab with a bite taken out."] } },
    { id: "human", name: ["人的手臂（G1）", "A human arm (G1)"], hide: ["d3", "j5", "j6"],
      problem: { title: ["生活中的例子：手能够到哪里", "Everyday example: where can a hand reach?"],
                 text: ["用仿人机器人 G1 的右臂代表人的手臂：肩 3 个关节、肘 1 个。扫描一下手腕能到达的范围。",
                        "The right arm of the G1 humanoid stands for a human arm: 3 shoulder joints and the elbow. Sample where the wrist can go."] } },
  ],
  params: [
    { id: "j1", name: ["关节 1（G1：肩俯仰）", "Joint 1 (G1: shoulder pitch)"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j2", name: ["关节 2（G1：肩横滚）", "Joint 2 (G1: shoulder roll)"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j3", name: ["关节 3（UR5e θ₃；G1：肩偏航）", "Joint 3 (UR5e θ₃; G1: shoulder yaw)"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "d3", name: ["SCARA 丝杠下降量 d₃", "SCARA screw drop d₃"], min: 0, max: 150, step: 1, value: 0, unit: "mm", digits: 0 },
    { id: "j4", name: ["关节 4（G1：肘）", "Joint 4 (G1: elbow)"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j5", name: ["关节 5", "Joint 5"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "j6", name: ["关节 6", "Joint 6"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["扫描工作空间", "Sample the workspace"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "scan_ur", robot: true, text: ["扫描 UR5e 的可达工作空间（2000 个随机构型）。", "Sample the UR5e's reachable workspace (2000 random configurations)."],
      demo: { scene: "ur", set: {}, press: ["start"], wait: 6 } },
    { id: "dex", robot: true, text: ["调关节，使法兰中心处在灵巧工作空间内（100 个方向都能到达）。", "Set the joints so that the flange centre lies in the dexterous workspace (all 100 directions)."],
      demo: { scene: "ur", set: { j1: 0, j2: -90, j3: 90, j4: -90, j5: -90, j6: 0 }, press: [], wait: 1 } },
    { id: "edge", robot: true, text: ["把法兰中心伸到离基座轴线 0.9 m 以外，读出能到达的方向数（应少于 20 个）。", "Stretch the flange centre beyond 0.9 m from the base axis and read how many directions remain (fewer than 20)."],
      demo: { scene: "ur", set: { j1: 0, j2: 0, j3: 0, j4: -45, j5: 90, j6: 0 }, press: [], wait: 1 } },
    { id: "scan_sc", robot: true, text: ["扫描 SCARA 的工作空间，读出样本点离关节 1 轴线的最小距离（约 0.20 m，来自关节 2 的限位）。", "Sample the SCARA's workspace and read the smallest distance of the samples from axis 1 (about 0.20 m, set by joint 2's limit)."],
      demo: { scene: "scara", set: {}, press: ["start"], wait: 6 } },
    { id: "scan_h", text: ["生活场景：扫描手腕能到达的范围，读出离肩部的最大距离。", "Everyday scene: sample where the wrist can go and read its largest distance from the shoulder."],
      demo: { scene: "human", set: {}, press: ["start"], wait: 6 } },
  ],
  think: ["UR5e 的可达工作空间比 SCARA 大二十多倍，为什么分拣线上仍大量使用 SCARA？从任务空间（R³ × S¹）和灵巧性的角度回答。",
          "The UR5e's reachable workspace is over twenty times the SCARA's. Why do sorting lines still use SCARAs so much? Answer in terms of the task space (R³ × S¹) and dexterity."],

  N: 2000,
  // ---------- UR5e：标准 DH（取模型尺寸）与逆解的可解性检查（同 _ch11.ur_reachable）
  DH: [[0, 0.163, Math.PI / 2], [-0.425, 0, 0], [-0.392, 0, 0], [0, 0.134, Math.PI / 2], [0, 0.1, -Math.PI / 2], [0, 0.1, 0]],
  A(i, th) {
    const [a, d, al] = this.DH[i], ct = Math.cos(th), st = Math.sin(th), ca = Math.cos(al), sa = Math.sin(al);
    return [[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d], [0, 0, 0, 1]];
  },
  inv(T) {
    const R = [0, 1, 2].map((i) => [0, 1, 2].map((j) => T[j][i])), p = [0, 1, 2].map((i) => -(R[i][0] * T[0][3] + R[i][1] * T[1][3] + R[i][2] * T[2][3]));
    return [[...R[0], p[0]], [...R[1], p[1]], [...R[2], p[2]], [0, 0, 0, 1]];
  },
  mm(A, B) { return A.map((r) => [0, 1, 2, 3].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j] + r[3] * B[3][j])); },
  dirs() {
    if (this._dirs) return this._dirs;
    const n = 100, out = [];
    for (let k = 0; k < n; k++) {
      const z = 1 - 2 * (k + 0.5) / n, r = Math.sqrt(1 - z * z), ph = Math.PI * (3 - Math.sqrt(5)) * (k + 0.5);
      out.push([r * Math.cos(ph), r * Math.sin(ph), z]);
    }
    this._dirs = out;
    return out;
  },
  reachable(p, a) {
    const D4 = 0.134, D6 = 0.1, A2 = -0.425, A3 = -0.392;
    const h = Math.abs(a[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
    let x = [h[1] * a[2] - h[2] * a[1], h[2] * a[0] - h[0] * a[2], h[0] * a[1] - h[1] * a[0]];
    const nx = Math.hypot(...x); x = x.map((v) => v / nx);
    const y = [a[1] * x[2] - a[2] * x[1], a[2] * x[0] - a[0] * x[2], a[0] * x[1] - a[1] * x[0]];
    const T = [[x[0], y[0], a[0], p[0]], [x[1], y[1], a[1], p[1]], [x[2], y[2], a[2], p[2]], [0, 0, 0, 1]];
    const p05 = [p[0] - D6 * a[0], p[1] - D6 * a[1]], r = Math.hypot(p05[0], p05[1]);
    if (r < D4) return false;
    const psi = Math.atan2(p05[1], p05[0]), phi = Math.acos(D4 / r);
    for (const t1 of [psi + phi + Math.PI / 2, psi - phi + Math.PI / 2]) {
      const T16 = this.mm(this.inv(this.A(0, t1)), T);
      const c5 = Math.max(-1, Math.min(1, (T16[2][3] - D4) / D6));
      for (const t5 of [Math.acos(c5), -Math.acos(c5)]) {
        let s5 = Math.sin(t5); if (Math.abs(s5) < 1e-12) s5 = 1e-12;
        const t6 = Math.atan2(-T16[2][1] / s5, T16[2][0] / s5);
        const T14 = this.mm(this.mm(T16, this.inv(this.A(5, t6))), this.inv(this.A(4, t5)));
        const q = [0, 1, 2].map((i) => T14[i][0] * 0 + T14[i][1] * -D4 + T14[i][3]);
        const c3 = (q[0] * q[0] + q[1] * q[1] + q[2] * q[2] - A2 * A2 - A3 * A3) / (2 * A2 * A3);
        if (Math.abs(c3) <= 1) return true;
      }
    }
    return false;
  },
  // ---------- 三台机器人的关节
  UR: ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"],
  G1: ["right_shoulder_pitch_joint", "right_shoulder_roll_joint", "right_shoulder_yaw_joint", "right_elbow_joint"],
  lim(h, name, lo, hi) {
    const j = ((h.entry.robot || {}).joints || []).find((x) => x.name === name);
    return j && j.limit ? [j.limit.lower, j.limit.upper] : [lo, hi];
  },
  setFrom(api, q) {                    // q：关节变量（弧度；SCARA 第 3 个为米）
    const m = api.m;
    if (api.scene === "ur") { const o = {}; this.UR.forEach((n, i) => { o[n] = q[i]; }); m["B-ARM-UR5E"].set(o); }
    else if (api.scene === "scara") m["B-SCA-WQ4"].set({ J1: q[0], J2: q[1], J3: q[2], J4: q[3] });
    else { const o = {}; this.G1.forEach((n, i) => { o[n] = q[i]; }); m["B-HUM-G1"].set(o); }
  },
  sliders(api) {
    const d = Math.PI / 180, p = api.p;
    if (api.scene === "scara") return [p.j1 * d, p.j2 * d, p.d3 / 1000, p.j4 * d];
    if (api.scene === "human") return [p.j1 * d, p.j2 * d, p.j3 * d, p.j4 * d];
    return [p.j1, p.j2, p.j3, p.j4, p.j5, p.j6].map((x) => x * d);
  },
  sample(api) {                        // 限位以内的随机关节变量
    const R = () => Math.random(), m = api.m, d = Math.PI / 180;
    if (api.scene === "ur") return this.UR.map((n, i) => (i === 2 ? (2 * R() - 1) * Math.PI : (2 * R() - 1) * Math.PI));
    if (api.scene === "scara") return [(2 * R() - 1) * 140 * d, (2 * R() - 1) * 145 * d, 0.15 * R(), (2 * R() - 1) * Math.PI];
    return this.G1.map((n) => { const [lo, hi] = this.lim(m["B-HUM-G1"], n, -1.5, 1.5); return lo + (hi - lo) * R(); });
  },
  tip(api) {                           // 末端点：世界坐标（画点云）
    const m = api.m;
    if (api.scene === "ur") return m["B-ARM-UR5E"].point("wrist_3_link", [0, 0.1, 0]);
    if (api.scene === "scara") return m["B-SCA-WQ4"].point("tool", [0, 0, 0]);
    return m["B-HUM-G1"].point("right_wrist_yaw_link", [0, 0, 0]);
  },
  local(api) {                         // 末端点在机器人基座坐标系 {s} 中的坐标
    const m = api.m;
    if (api.scene === "ur") { const [x, y, z] = m["B-ARM-UR5E"].local("wrist_3_link", [0, 0.1, 0]); return [-x, -y, z]; }
    if (api.scene === "scara") return m["B-SCA-WQ4"].local("tool", [0, 0, 0]);
    return m["B-HUM-G1"].local("right_wrist_yaw_link", [0, 0, 0]);
  },

  setup3d(api, keep) {
    const T = api.three;
    ["B-ARM-UR5E", "B-SCA-WQ4", "B-HUM-G1"].forEach((k) => api.m[k].place(0, 0));
    api.axes(api.m["B-ARM-UR5E"], "base", 0.15);
    api.axes(api.m["B-SCA-WQ4"], "base", 0.15);
    const geo = new T.BufferGeometry(), arr = new Float32Array(3 * (this.N + 10));
    geo.setAttribute("position", new T.BufferAttribute(arr, 3));
    geo.setDrawRange(0, 0);
    const pts = new T.Points(geo, new T.PointsMaterial({ color: 0x2a7fd4, size: 0.012 }));
    pts.frustumCulled = false;
    api.st.scene.add(pts);
    keep.cloud = { geo, arr, n: 0, scene: null, rmin: Infinity, dmax: 0 };
    keep.shown = null;
  },
  clearCloud(api) {
    const c = api.keep.cloud;
    c.n = 0; c.rmin = Infinity; c.dmax = 0; c.scene = api.scene;
    c.geo.setDrawRange(0, 0);
  },
  reset(api, s) {},
  start(api, s) { this.clearCloud(api); },
  update(dt, api, s) {
    const c = api.keep.cloud;
    if (!c) { api.stop(); return; }
    for (let k = 0; k < 50 && c.n < this.N; k++) {
      this.setFrom(api, this.sample(api));
      const w = this.tip(api), l = this.local(api);
      c.arr.set([w.x, w.y, w.z], 3 * c.n);
      c.n++;
      c.rmin = Math.min(c.rmin, Math.hypot(l[0], l[1]));
      if (api.scene === "human") {
        const sh = api.m["B-HUM-G1"].point("right_shoulder_pitch_link", [0, 0, 0]);
        c.dmax = Math.max(c.dmax, w.distanceTo(sh));
      } else c.dmax = Math.max(c.dmax, Math.hypot(l[0], l[1]));
    }
    c.geo.setDrawRange(0, c.n);
    c.geo.attributes.position.needsUpdate = true;
    this.setFrom(api, this.sliders(api));
    if (c.n >= this.N) {
      api.stop();
      api.done(api.scene === "ur" ? "scan_ur" : api.scene === "scara" ? "scan_sc" : "scan_h");
    }
  },
  readouts(api, s) {
    const m = api.m;
    if (!m["B-ARM-UR5E"] || !m["B-SCA-WQ4"] || !m["B-HUM-G1"] || !api.keep.cloud) return [];
    if (!api.running) this.setFrom(api, this.sliders(api));
    const c = api.keep.cloud, [x, y, z] = this.local(api), rho = Math.hypot(x, y), f = (v, n) => api.fmt(v, n);
    const rows = [[["末端 (x, y, z)", "end point (x, y, z)"], `(${f(x, 3)}, ${f(y, 3)}, ${f(z, 3)}) m`],
                  [["离基座轴线", "from the base axis"], f(rho, 3) + " m"],
                  [["点云样本数", "samples in the cloud"], String(c.scene === api.scene ? c.n : 0)]];
    if (api.scene === "ur") {
      const nd = this.dirs().filter((a) => this.reachable([x, y, z], a)).length;
      if (nd === 100) api.done("dex");
      if (rho > 0.9 && nd < 20) api.done("edge");
      const cls = nd === 100 ? api.T("灵巧工作空间内", "in the dexterous workspace") : nd > 0 ? api.T("可达，但不灵巧", "reachable, not dexterous") : "—";
      rows.push([["能到达的法兰方向", "flange directions that work"], `${nd} / 100`], [["判断", "verdict"], cls]);
      if (c.scene === "ur" && c.n) rows.push([["样本离轴线最远", "farthest sample from the axis"], f(c.dmax, 3) + " m"]);
    } else if (api.scene === "scara") {
      rows.push([["工具转向", "tool heading"], api.T("任意（关节 4 可转 ±360°）", "any (joint 4 turns ±360°)")]);
      if (c.scene === "scara" && c.n) rows.push([["样本离轴线最近 / 最远", "nearest / farthest sample"], `${f(c.rmin, 3)} / ${f(c.dmax, 3)} m`]);
    } else if (c.scene === "human" && c.n) {
      rows.push([["手腕离肩部最远", "farthest wrist from shoulder"], f(c.dmax, 3) + " m"]);
    }
    return rows;
  },
  draw(api, s) {
    const m = api.m, sc = api.scene, c = api.keep.cloud;
    m["B-ARM-UR5E"].holder.visible = sc === "ur";
    m["B-SCA-WQ4"].holder.visible = sc === "scara";
    m["B-HUM-G1"].holder.visible = sc === "human";
    if (c && c.scene !== sc) this.clearCloud(api);
    if (api.keep.shown !== sc) {
      api.keep.shown = sc;
      const tgt = sc === "ur" ? m["B-ARM-UR5E"] : sc === "scara" ? m["B-SCA-WQ4"] : m["B-HUM-G1"];
      api.view(35, 24, sc === "human" ? 0.8 : 0.85, tgt);
    }
    if (!api.running) this.setFrom(api, this.sliders(api));
  },
});
