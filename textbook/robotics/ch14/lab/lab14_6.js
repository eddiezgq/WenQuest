// 实验 14.6 SCARA 与 Delta 的逆解（配 14.6 节）。
// SCARA（零件库 B-SCA-WQ4：两臂 0.35、0.25 m，零位工具点高 z₀ = 0.242 m，丝杠向下为正 0–0.15 m，关节 1 ±140°、关节 2 ±145°）：
//   (x, y) 由平面 2R 求 θ₁、θ₂（式 (14.2.4)、(14.2.6)），θ₃ = z₀ − z，θ₄ = φ − θ₁ − θ₂（式 (14.6.1)）。右手构型 θ₂ > 0。
//   模型核对：从模型读出工具连杆原点（{s} 与模型基座坐标系相同）。
// Delta（B-PAR-DELTA：Rb 0.15、Rp 0.04、La 0.22、Lb 0.5 m，主动臂限位 −40°～90°）：每条支链按式 (11.5.7) 求两个解，
//   肘部朝外取 + 号，朝内取 − 号（14.6.3 节：这就是子问题 3）。从动杆和动平台按闭环条件摆放，做法与实验 11.5 相同；
//   “闭合误差”从模型上读点：主动臂末端到动平台上球关节中心的距离减去 Lb。
// 生活场景：SCARA 在桌面上画一个圆（圆心 (0.40, 0)、半径 0.08 m），先用右手构型、再用左手构型各画一圈。
WQ.lab({
  title: ["实验 14.6 SCARA 与 Delta 的逆解", "Lab 14.6 Inverse kinematics of the SCARA and the Delta"],
  goal: ["比较 SCARA 的右手、左手两种构型，看关节限位怎样决定能用哪一种；看 Delta 每条支链的两个解，以及为什么只用其中一个。",
         "Compare the SCARA's right- and left-handed configurations and see how joint limits decide which one can be used; look at the two solutions of each Delta leg and why only one is used."],
  view: "3d",
  models: ["B-SCA-WQ4", "B-PAR-DELTA"],
  scenes: [
    { id: "scara", robot: true, name: ["SCARA：右手与左手", "SCARA: right and left hand"], hide: ["b1"],
      problem: { title: ["机器人问题：拧这颗螺钉，用哪只“手”", "Robot problem: which “hand” drives this screw"],
                 text: ["用滑块给出工具点的位置和工具转角 φ，选择右手或左手构型。界面显示两种构型的关节变量，并标出是否超出关节限位。",
                        "Sliders set the tool point and tool angle φ; choose the right- or left-handed configuration. Both sets of joint variables are shown, with any limit violations marked."] } },
    { id: "delta", robot: true, name: ["Delta：每条支链两个解", "Delta: two solutions per leg"], hide: ["phi", "hand"],
      params: { x: { name: ["平台中心 x", "platform x"], min: -0.2, max: 0.2, step: 0.005, value: 0 },
                y: { name: ["平台中心 y", "platform y"], min: -0.2, max: 0.2, step: 0.005, value: 0 },
                z: { name: ["平台中心 z", "platform z"], min: -0.7, max: -0.3, step: 0.005, value: -0.42 } },
      problem: { title: ["机器人问题：吸盘到这里，三根主动臂各转多少", "Robot problem: suction cup here; how far does each arm turn"],
                 text: ["给出动平台中心的位置，支链 1 可以选肘部朝外或朝内的解（另两条取朝外）。按“运行”，平台沿拾取路径（半径 0.12 m 的水平圆）走一圈。",
                        "Set the platform centre; leg 1 may take the elbow-out or elbow-in solution (the other two stay out). Press Run to send the platform once round the pick path (a level circle of radius 0.12 m)."] } },
    { id: "draw", name: ["在桌上画圆", "Drawing a circle on the desk"], hide: ["x", "y", "z", "phi", "hand", "b1"],
      problem: { title: ["生活中的例子：左手、右手都能画圆", "Everyday example: either hand can draw the circle"],
                 text: ["像人用右手、左手写字一样，SCARA 用两种构型都能在桌上画出同一个圆，手臂的样子互为镜像。按“运行”。",
                        "Like writing with the right or the left hand, the SCARA draws the same circle with either configuration, the arms mirror images. Press Run."] } },
  ],
  params: [
    { id: "x", name: ["工具点 x", "tool x"], min: -0.6, max: 0.6, step: 0.005, value: 0.4, unit: "m", digits: 3 },
    { id: "y", name: ["工具点 y", "tool y"], min: -0.6, max: 0.6, step: 0.005, value: 0.2, unit: "m", digits: 3 },
    { id: "z", name: ["工具点 z", "tool z"], min: 0.092, max: 0.242, step: 0.001, value: 0.15, unit: "m", digits: 3 },
    { id: "phi", name: ["工具转角 φ", "tool angle φ"], min: -180, max: 180, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "hand", name: ["构型：0 右手，1 左手", "hand: 0 right, 1 left"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "b1", name: ["Delta 支链 1：0 朝外，1 朝内（支链 2、3 取朝外）", "Delta leg 1: 0 out, 1 in (legs 2, 3 out)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["运行", "Run"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 14.6.1：工具点 (0.40, 0.20, 0.15) m、φ = 30°，读出右手 (−7.28°, 85.08°) 和左手 (60.41°, −85.08°) 两种构型。",
                                     "Example 14.6.1: tool at (0.40, 0.20, 0.15) m, φ = 30°; read the right-handed (−7.28°, 85.08°) and left-handed (60.41°, −85.08°) configurations."],
      demo: { scene: "scara", set: { x: 0.4, y: 0.2, z: 0.15, phi: 30, hand: 0 }, press: [], wait: 1 } },
    { id: "q", robot: true, text: ["把工具点移到 Q = (−0.30, 0.35) m，选出在限位以内的那种构型。", "Move the tool to Q = (−0.30, 0.35) m and choose the configuration that stays within the limits."],
      demo: { scene: "scara", set: { x: -0.3, y: 0.35, z: 0.15, phi: 30, hand: 0 }, press: [], wait: 1 } },
    { id: "in", robot: true, text: ["Delta 在静止位置 (0, 0, −420) mm，把支链 1 换成朝内的解，读出转角（约 −161°），说明为什么不能用。",
                                     "Delta at rest (0, 0, −420) mm: switch leg 1 to the elbow-in solution, read its angle (about −161°) and say why it cannot be used."],
      demo: { scene: "delta", set: { x: 0, y: 0, z: -0.42, b1: 1 }, press: [], wait: 1 } },
    { id: "path", robot: true, text: ["支链 1 也取朝外的解，按“运行”让平台沿拾取路径走一圈，闭合误差始终小于 0.001 mm。",
                                       "With leg 1 elbow-out as well, press Run: the platform goes once round the pick path with the closure error always below 0.001 mm."],
      demo: { scene: "delta", set: { x: 0, y: 0, z: -0.42, b1: 0 }, press: ["start"], wait: 12 } },
    { id: "draw", text: ["生活场景：按“运行”，SCARA 先用右手、再用左手各画一圈。", "Everyday scene: press Run; the SCARA draws the circle once with the right hand and once with the left."],
      demo: { scene: "draw", set: {}, press: ["start"], wait: 14 } },
  ],
  think: ["为什么 SCARA 在一段连续的路径中不能换手，而 Delta 根本不需要换？", "Why can a SCARA not change hands along a continuous path, while a Delta never needs to?"],

  // ---------------- SCARA
  SC: { L1: 0.35, L2: 0.25, z0: 0.242, lim1: 140, lim2: 145 },
  scaraIK(x, y, z, phi) {
    const { L1, L2, z0 } = this.SC, r = Math.hypot(x, y);
    const om = (L1 + L2 - r) * (L1 + L2 + r) / (2 * L1 * L2), op = (r - Math.abs(L1 - L2)) * (r + Math.abs(L1 - L2)) / (2 * L1 * L2);
    if (om < -1e-12 || op < -1e-12) return [];
    const c = (Math.max(op, 0) - Math.max(om, 0)) / 2, s = Math.sqrt(Math.max(om, 0) * Math.max(op, 0));
    return [1, -1].map((g) => {
      const t2 = Math.atan2(g * s, c), t1 = Math.atan2(y, x) - Math.atan2(L2 * Math.sin(t2), L1 + L2 * Math.cos(t2));
      const w = (a) => Math.atan2(Math.sin(a), Math.cos(a));
      return [w(t1), t2, z0 - z, w(phi - t1 - t2)];
    });
  },
  inLim(q) { return Math.abs(q[0]) <= this.SC.lim1 * Math.PI / 180 + 1e-9 && Math.abs(q[1]) <= this.SC.lim2 * Math.PI / 180 + 1e-9 && q[2] >= -1e-9 && q[2] <= 0.15 + 1e-9; },
  setScara(api, q) { api.m["B-SCA-WQ4"].set({ J1: q[0], J2: q[1], J3: q[2], J4: q[3] }); },
  circle(u) { return [0.4 + 0.08 * Math.cos(2 * Math.PI * u), 0.08 * Math.sin(2 * Math.PI * u)]; },

  // ---------------- Delta（几何、逆解 (11.5.7)、摆放与闭合检查同实验 11.5）
  D: { Rb: 0.15, Rp: 0.04, La: 0.22, Lb: 0.5, lo: -40, hi: 90 },
  ek(k) { const f = 2 * Math.PI * k / 3; return [Math.cos(f), Math.sin(f), 0]; },
  elbow(k, th) { const e = this.ek(k), D = this.D; return [D.Rb * e[0] + D.La * Math.cos(th) * e[0], D.Rb * e[1] + D.La * Math.cos(th) * e[1], -D.La * Math.sin(th)]; },
  legIK(k, p, sign) {
    const D = this.D, e = this.ek(k), q = [p[0] + (D.Rp - D.Rb) * e[0], p[1] + (D.Rp - D.Rb) * e[1], p[2]];
    const u = q[0] * e[0] + q[1] * e[1], v = -q[0] * e[1] + q[1] * e[0], h = q[2];
    const A = -2 * D.La * u, B = 2 * D.La * h, C = D.Lb * D.Lb - D.La * D.La - u * u - v * v - h * h, r = Math.hypot(A, B);
    if (Math.abs(C) > r) return null;
    const t = Math.atan2(B, A) + sign * Math.atan2(Math.sqrt(r * r - C * C), C);
    return Math.atan2(Math.sin(t), Math.cos(t));
  },
  poseDelta(api, th, p) {
    const h = api.m["B-PAR-DELTA"], D = this.D;
    h.set({ J1: th[0], J2: th[1], J3: th[2] });
    for (let k = 0; k < 3; k++) {
      const e = this.ek(k), t = [-e[1], e[0], 0], E = this.elbow(k, th[k]);
      const P = [p[0] + D.Rp * e[0], p[1] + D.Rp * e[1], p[2]];
      const dz = [(P[0] - E[0]) / D.Lb, (P[1] - E[1]) / D.Lb, (P[2] - E[2]) / D.Lb];
      let dy = [dz[1] * t[2] - dz[2] * t[1], dz[2] * t[0] - dz[0] * t[2], dz[0] * t[1] - dz[1] * t[0]];
      const n = Math.hypot(...dy); dy = dy.map((v) => v / n);
      const node = h.nodes["lower" + (k + 1)];
      node.matrixAutoUpdate = false;
      node.matrix.set(t[0], dy[0], dz[0], (E[0] + P[0]) / 2, t[1], dy[1], dz[1], (E[1] + P[1]) / 2, t[2], dy[2], dz[2], (E[2] + P[2]) / 2, 0, 0, 0, 1);
    }
    const pl = h.nodes.platform;
    pl.matrixAutoUpdate = false;
    pl.matrix.makeTranslation(p[0], p[1], p[2]);
    h.root.updateMatrixWorld(true);
  },
  closure(api) {
    const h = api.m["B-PAR-DELTA"], D = this.D;
    let err = 0;
    for (let k = 0; k < 3; k++) {
      const e = this.ek(k), E = h.local("upper" + (k + 1), [D.La, 0, 0]), P = h.local("platform", [D.Rp * e[0], D.Rp * e[1], 0]);
      err = Math.max(err, Math.abs(Math.hypot(P[0] - E[0], P[1] - E[1], P[2] - E[2]) - D.Lb));
    }
    return err;
  },
  deltaTarget(api, s) {
    if (api.running && s.u != null) { const a = 2 * Math.PI * s.u; return [0.12 * Math.cos(a), 0.12 * Math.sin(a), -0.42]; }
    return [api.p.x, api.p.y, api.p.z];
  },

  setup3d(api, keep) {
    const sc = api.m["B-SCA-WQ4"], dl = api.m["B-PAR-DELTA"];
    sc.place(0, 0); dl.place(0, 0);
    api.axes(sc, "base", 0.12); api.axes(dl, "base", 0.12);
    keep.tr = api.trace(0xd62728);
    keep.shown = null;
  },
  reset(api, s) {
    s.u = null; s.phase = 0; s.maxErr = 0;
    if (api.keep && api.keep.tr) api.keep.tr.clear();
  },
  start(api, s) {
    s.u = 0; s.phase = 0; s.maxErr = 0;
    if (api.keep.tr) api.keep.tr.clear();
    if (api.scene === "scara") api.stop();
  },
  update(dt, api, s) {
    if (s.u == null) { api.stop(); return; }
    s.u += dt / (api.scene === "draw" ? 3 : 4);
    if (api.scene === "delta") {
      const p = this.deltaTarget(api, s), th = [0, 1, 2].map((k) => this.legIK(k, p, 1));
      if (th.every((t) => t !== null)) { this.poseDelta(api, th, p); s.maxErr = Math.max(s.maxErr, this.closure(api)); }
      api.keep.tr.add(api.m["B-PAR-DELTA"].point("platform", [0, 0, 0]));
      if (s.u >= 1) { s.u = 1; api.stop(); if (s.maxErr < 1e-6) api.done("path"); }
    } else if (api.scene === "draw") {
      if (s.u >= 1) { s.u -= 1; s.phase += 1; if (s.phase >= 2) { s.u = 1; s.phase = 2; api.stop(); api.done("draw"); return; } }
      const [x, y] = this.circle(s.u), q = this.scaraIK(x, y, 0.15, 0)[s.phase === 0 ? 0 : 1];
      if (q) { this.setScara(api, q); api.keep.tr.add(api.m["B-SCA-WQ4"].point("tool", [0, 0, 0])); }
    } else api.stop();
  },
  readouts(api, s) {
    if (!api.m["B-SCA-WQ4"] || !api.keep.tr) return [];
    const d = (v) => (v * 180 / Math.PI).toFixed(2) + "°", f = (v, n) => api.fmt(v, n);
    if (api.scene === "delta") {
      const p = this.deltaTarget(api, s), sg = [api.p.b1 ? -1 : 1, 1, 1];
      const th = [0, 1, 2].map((k) => this.legIK(k, p, sg[k]));
      if (th.some((t) => t === null)) return [[["装配", "assembly"], api.T("够不着：至少一条支链无解", "out of reach: a leg has no solution")]];
      if (!api.running) this.poseDelta(api, th, p);
      const ok = th.map((t) => t * 180 / Math.PI >= this.D.lo - 1e-9 && t * 180 / Math.PI <= this.D.hi + 1e-9);
      if (!api.running && Math.abs(p[0]) < 1e-9 && Math.abs(p[1]) < 1e-9 && Math.abs(p[2] + 0.42) < 1e-9 && api.p.b1 === 1 && !ok[0]) api.done("in");
      return [[["转角 θ₁, θ₂, θ₃", "angles θ₁, θ₂, θ₃"], th.map(d).join(", ")],
              [["在限位 −40°～90° 以内", "within −40° to 90°"], ok.map((x) => (x ? api.T("是", "yes") : api.T("否", "no"))).join(", ")],
              [["平台中心", "platform centre"], `(${p.map((v) => f(v * 1000, 1)).join(", ")}) mm`],
              [["闭合误差（从模型读点）", "closure error (read off the model)"], f(this.closure(api) * 1000, 6) + " mm"],
              [["一圈中的最大闭合误差", "largest closure error on the loop"], f((s.maxErr || 0) * 1000, 6) + " mm"]];
    }
    if (api.scene === "draw") return [[["正在画", "drawing"], s.phase === 0 ? api.T("右手构型", "right hand") : s.phase === 1 ? api.T("左手构型", "left hand") : api.T("两圈都画完了", "both done")]];
    const sols = this.scaraIK(api.p.x, api.p.y, api.p.z, api.p.phi * Math.PI / 180);
    if (!sols.length) return [[["状态", "status"], api.T("够不着：水平距离超出 0.1～0.6 m", "out of reach: horizontal distance outside 0.1–0.6 m")]];
    const q = sols[api.p.hand];
    this.setScara(api, q);
    const t = api.m["B-SCA-WQ4"].local("tool", [0, 0, 0]), err = Math.hypot(t[0] - api.p.x, t[1] - api.p.y, t[2] - api.p.z);
    const near = (a, b) => Math.abs(a - b) < 1e-9;
    if (near(api.p.x, 0.4) && near(api.p.y, 0.2) && near(api.p.z, 0.15) && api.p.phi === 30 && err < 1e-9) api.done("ex");
    if (near(api.p.x, -0.3) && near(api.p.y, 0.35) && this.inLim(q) && err < 1e-9) api.done("q");
    const row = (qq) => `(${d(qq[0])}, ${d(qq[1])}, ${f(qq[2], 3)} m, ${d(qq[3])})` + (this.inLim(qq) ? "" : api.T("  超限", "  over limit"));
    return [[["右手构型", "right-handed"], row(sols[0])], [["左手构型", "left-handed"], row(sols[1])],
            [["当前构型", "chosen"], api.p.hand ? api.T("左手", "left") : api.T("右手", "right")],
            [["模型核对：工具点误差", "model check: tool point error"], err.toExponential(1) + " m"]];
  },
  draw(api, s) {
    const m = api.m, K = api.keep;
    if (!K.tr) return;
    const isD = api.scene === "delta";
    m["B-PAR-DELTA"].holder.visible = isD;
    m["B-SCA-WQ4"].holder.visible = !isD;
    if (K.shown !== api.scene) { K.shown = api.scene; api.view(isD ? 35 : 30, isD ? 18 : 40, 0.8, isD ? m["B-PAR-DELTA"] : m["B-SCA-WQ4"]); K.tr.clear(); }
    if (isD && !api.running) {
      const p = this.deltaTarget(api, s), sg = [api.p.b1 ? -1 : 1, 1, 1], th = [0, 1, 2].map((k) => this.legIK(k, p, sg[k]));
      if (th.every((t) => t !== null)) this.poseDelta(api, th, p);
    }
    if (api.scene === "scara") { const sols = this.scaraIK(api.p.x, api.p.y, api.p.z, api.p.phi * Math.PI / 180); if (sols.length) this.setScara(api, sols[api.p.hand]); }
  },
});
