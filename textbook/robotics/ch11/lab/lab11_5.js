// 实验 11.5 闭链与约束（配 11.5 节）。
// Delta（零件库 B-PAR-DELTA：Rb 0.15、Rp 0.04、La 0.22、Lb 0.5 m）：模型只有三个主动关节，平行四边形和动平台由本实验按
// 闭环条件 (11.5.6) 摆放——“给平台位置”时按式 (11.5.7) 求三个转角（逆运动学），“给电机转角”时按式 (11.5.8) 三球求交求平台位置
// （正运动学）。从动杆节点的矩阵取：x 列为支链的切向 t_k（平行四边形的横边方向），z 列为杆的方向 (P′−E)/Lb，原点在杆的中点，
// 与模型文件中静止位置的矩阵取法相同。测量区的“闭合误差”从模型上读点：主动臂末端与动平台上球关节中心的距离减去 Lb。
// 差速 AGV（B-EDU-DIFF：r 0.05、b 0.26 m）：按式 (11.5.13) 以 1 ms 步长积分（同程序 11.5.1）。场景“两种轮速过程”依次运行
// 过程 A、B；生活场景“侧方停车”只用“倒车并转向”和“直行”两种动作（像汽车一样不原地转），把车横向挪进车位。
WQ.lab({
  title: ["实验 11.5 闭链与约束", "Lab 11.5 Closed chains and constraints"],
  goal: ["用 Delta 体会闭环约束：给平台位置求电机转角，给电机转角求平台位置；用 AGV 体会非完整约束：车轮转角决定不了车的位置。",
         "Feel loop closure on the Delta (platform position to motor angles and back) and a nonholonomic constraint on the AGV (wheel angles do not fix its position)."],
  view: "3d",
  models: ["B-PAR-DELTA", "B-EDU-DIFF"],
  scenes: [
    { id: "ik", robot: true, name: ["Delta：给平台位置", "Delta: set the platform"], hide: ["a1", "a2", "a3"],
      problem: { title: ["机器人问题：吸盘要到这里，电机各转多少", "Robot problem: the cup must go here; how far does each motor turn?"],
                 text: ["拖动平台中心的 x、y、z，三条支链各按式 (11.5.7) 求出主动臂转角，平行四边形和动平台随之闭合。",
                        "Drag the platform centre x, y, z; each leg solves Eq. (11.5.7) for its arm angle and the parallelograms close up."] } },
    { id: "fk", robot: true, name: ["Delta：给电机转角", "Delta: set the motors"], hide: ["x", "y", "z"],
      problem: { title: ["机器人问题：电机转到这里，平台在哪", "Robot problem: motors here; where is the platform?"],
                 text: ["拖动三个电机的转角，平台位置由三个球面求交得到（式 (11.5.8)）。注意平台怎样动、是否转动。",
                        "Drag the three motor angles; the platform is where three spheres meet (Eq. (11.5.8)). Watch how it moves and whether it turns."] } },
    { id: "agv", robot: true, name: ["AGV：两种轮速过程", "AGV: two wheel programmes"], hide: ["x", "y", "z", "a1", "a2", "a3"],
      problem: { title: ["机器人问题：只看轮转角，能知道车在哪吗", "Robot problem: do the wheel angles tell where the car is?"],
                 text: ["按“运行”：车先按过程 A（两轮同时变速）走 4 s，回到起点后再按过程 B（先右轮、后左轮）走，两轮的总转角与 A 相同。",
                        "Press Run: programme A (both wheels, varying speeds) for 4 s, then back to the start for programme B (right wheel, then left) with the same wheel totals."] } },
    { id: "park", name: ["侧方停车", "Parallel parking"], hide: ["x", "y", "z", "a1", "a2", "a3"],
      problem: { title: ["生活中的例子：车不能横着走，却能停进车位", "Everyday example: a car cannot move sideways, yet it parks"],
                 text: ["小车代替汽车，只做两种动作：倒车并转向、直行。按“运行”，看它怎样横向挪进两辆车之间的车位。",
                        "The small car stands in for a car and only reverses with steering or drives straight. Press Run and watch it slide sideways into the gap."] } },
  ],
  params: [
    { id: "x", name: ["平台中心 x", "platform centre x"], min: -200, max: 200, step: 5, value: 0, unit: "mm", digits: 0 },
    { id: "y", name: ["平台中心 y", "platform centre y"], min: -200, max: 200, step: 5, value: 0, unit: "mm", digits: 0 },
    { id: "z", name: ["平台中心 z", "platform centre z"], min: -800, max: -250, step: 5, value: -420, unit: "mm", digits: 0 },
    { id: "a1", name: ["电机 1 转角 θ₁（向下为正）", "motor 1 angle θ₁ (down +)"], min: -40, max: 90, step: 1, value: 11, unit: "°", digits: 0 },
    { id: "a2", name: ["电机 2 转角 θ₂", "motor 2 angle θ₂"], min: -40, max: 90, step: 1, value: 11, unit: "°", digits: 0 },
    { id: "a3", name: ["电机 3 转角 θ₃", "motor 3 angle θ₃"], min: -40, max: 90, step: 1, value: 11, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["运行", "Run"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ik", robot: true, text: ["给平台位置：把动平台中心送到 (100, 0, −450) mm，读出三个转角（应为约 1.6°、28.9°、28.9°）。",
                                     "Set the platform centre to (100, 0, −450) mm and read the three angles (about 1.6°, 28.9°, 28.9°)."],
      demo: { scene: "ik", set: { x: 100, y: 0, z: -450 }, press: [], wait: 1 } },
    { id: "out", robot: true, text: ["把平台送到工作空间以外，读出是哪条支链装不上、原因是什么。", "Send the platform outside the workspace and read which leg fails, and why."],
      demo: { scene: "ik", set: { x: 0, y: 0, z: -760 }, press: [], wait: 1 } },
    { id: "fk", robot: true, text: ["给电机转角：电机 2、3 保持相同，只把电机 1 改变 20° 以上，看平台平移而不转动。",
                                     "Set the motors: keep motors 2 and 3 equal and change motor 1 by 20° or more; the platform shifts but does not turn."],
      demo: { scene: "fk", set: { a1: 45, a2: 20, a3: 20 }, press: [], wait: 1 } },
    { id: "agv", robot: true, text: ["AGV 依次运行过程 A、B，比较终点：轮转角、车头方向、位置。", "Run programmes A and B and compare the ends: wheel angles, heading, position."],
      demo: { scene: "agv", set: {}, press: ["start"], wait: 12 } },
    { id: "park", text: ["生活场景：完成侧方停车（横向移动 0.3 m 以上，车头方向回正）。", "Everyday scene: park sideways (more than 0.3 m to the side, heading straight again)."],
      demo: { scene: "park", set: {}, press: ["start"], wait: 10 } },
  ],
  think: ["Delta 的逆运动学三条支链互不相干，正运动学却要三个球面联立求交；串联机械臂恰好相反。为什么？",
          "On the Delta the three legs solve the inverse kinematics separately, while the forward kinematics needs all three spheres at once; a serial arm is the other way round. Why?"],

  // ---------------- Delta：几何、逆解 (11.5.7)、正解 (11.5.8)
  D: { Rb: 0.15, Rp: 0.04, La: 0.22, Lb: 0.5, lo: -40, hi: 90 },
  ek(k) { const f = 2 * Math.PI * k / 3; return [Math.cos(f), Math.sin(f), 0]; },
  elbow(k, th) { const e = this.ek(k), D = this.D; return [D.Rb * e[0] + D.La * Math.cos(th) * e[0], D.Rb * e[1] + D.La * Math.cos(th) * e[1], -D.La * Math.sin(th)]; },
  ik(p) {
    const D = this.D, th = [];
    for (let k = 0; k < 3; k++) {
      const e = this.ek(k), q = [p[0] + (D.Rp - D.Rb) * e[0], p[1] + (D.Rp - D.Rb) * e[1], p[2]];
      const u = q[0] * e[0] + q[1] * e[1], v = -q[0] * e[1] + q[1] * e[0], h = q[2];
      const A = -2 * D.La * u, B = 2 * D.La * h, C = D.Lb * D.Lb - D.La * D.La - u * u - v * v - h * h, r = Math.hypot(A, B);
      if (Math.abs(C) > r) return { th, bad: k, why: "reach" };
      let t = Math.atan2(B, A) + Math.acos(C / r);
      t = Math.atan2(Math.sin(t), Math.cos(t));
      const deg = t * 180 / Math.PI;
      if (deg < D.lo || deg > D.hi) return { th, bad: k, why: "limit", deg };
      th.push(t);
    }
    return { th, bad: -1 };
  },
  fk(th) {
    const D = this.D, c = [0, 1, 2].map((k) => { const E = this.elbow(k, th[k]), e = this.ek(k); return [E[0] - D.Rp * e[0], E[1] - D.Rp * e[1], E[2]]; });
    const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    const cr = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    const nrm = (a) => { const n = Math.hypot(...a); return a.map((x) => x / n); };
    const ex = nrm(sub(c[1], c[0])), i = dot(ex, sub(c[2], c[0]));
    const ey = nrm(sub(sub(c[2], c[0]), ex.map((x) => x * i))), ez = cr(ex, ey);
    const d = Math.hypot(...sub(c[1], c[0])), j = dot(ey, sub(c[2], c[0]));
    const x = d / 2, y = (i * i + j * j - 2 * i * x) / (2 * j), z2 = D.Lb * D.Lb - x * x - y * y;
    if (z2 < 0) return null;
    const cand = [1, -1].map((s) => [0, 1, 2].map((m) => c[0][m] + x * ex[m] + y * ey[m] + s * Math.sqrt(z2) * ez[m]));
    return cand[0][2] < cand[1][2] ? cand[0] : cand[1];
  },
  pose(api, th, p) {                         // 主动臂用关节，从动杆和动平台直接设节点矩阵（基座坐标系，Z 向上）
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
  closure(api) {                             // 从模型读点核对闭合：| |P′k − Ek| − Lb |
    const h = api.m["B-PAR-DELTA"], D = this.D;
    let err = 0;
    for (let k = 0; k < 3; k++) {
      const e = this.ek(k), E = h.local("upper" + (k + 1), [D.La, 0, 0]), P = h.local("platform", [D.Rp * e[0], D.Rp * e[1], 0]);
      err = Math.max(err, Math.abs(Math.hypot(P[0] - E[0], P[1] - E[1], P[2] - E[2]) - D.Lb));
    }
    return err;
  },
  delta(api) {                               // 按当前场景和参数求位姿；不能装配时保留上一个可行的位姿
    const K = api.keep, d = Math.PI / 180, p = api.p;
    if (api.scene === "ik") {
      const tgt = [p.x / 1000, p.y / 1000, p.z / 1000], r = this.ik(tgt);
      K.dres = r;
      if (r.bad < 0) { K.dth = r.th; K.dp = tgt; }
    } else if (api.scene === "fk") {
      const th = [p.a1 * d, p.a2 * d, p.a3 * d], q = this.fk(th);
      K.dres = { th, bad: q ? -1 : 0, why: "fk" };
      if (q) { K.dth = th; K.dp = q; }
    }
    if (K.dth) this.pose(api, K.dth, K.dp);
  },

  // ---------------- AGV：式 (11.5.13) 的积分
  R: 0.05, B: 0.26,
  step(q, wR, wL, dt) {
    const v = this.R * (wR + wL) / 2, om = this.R * (wR - wL) / this.B, f = q[2];
    if (Math.abs(om) < 1e-12) { q[0] += v * dt * Math.cos(f); q[1] += v * dt * Math.sin(f); }
    else { q[0] += v / om * (Math.sin(f + om * dt) - Math.sin(f)); q[1] -= v / om * (Math.cos(f + om * dt) - Math.cos(f)); }
    q[2] += om * dt; q[3] += wR * dt; q[4] += wL * dt;
  },
  TR: 40 + 6 * (1 - Math.cos(5.2)) / 1.3, TL: 40 - 4 * Math.sin(2.8) / 0.7,     // 过程 A 4 s 内两轮的总转角
  wheels(prog, t) {                          // 过程 A、B 的轮速 (rad/s)
    if (prog === "A") return [10 + 6 * Math.sin(1.3 * t), 10 - 4 * Math.cos(0.7 * t)];
    return t < 2 ? [this.TR / 2, 0] : [0, this.TL / 2];
  },
  parkWheels(t) {                            // 侧方停车：倒车右转 → 倒车左转（半径 0.6 m）→ 直行；返回 [ωR, ωL] 或 null（结束）
    const v = 0.3, om = 0.5, T1 = Math.PI / 4 / om, wr = (vv, w) => [(vv + w * this.B / 2) / this.R, (vv - w * this.B / 2) / this.R];
    if (t < T1) return wr(-v, om);
    if (t < 2 * T1) return wr(-v, -om);
    if (t < 2 * T1 + 0.8) return wr(v, 0);
    return null;
  },
  car(api, q) {
    const c = api.m["B-EDU-DIFF"], K = api.keep;
    c.holder.position.set(q[0], K.carY, -q[1]);
    c.holder.rotation.set(0, q[2], 0);
    c.holder.updateMatrixWorld(true);         // 立即更新，读点（画轨迹）才是本帧的位置
    c.set({ right_wheel_joint: q[3], left_wheel_joint: q[4] });
  },

  setup3d(api, keep) {
    const T = api.three, dl = api.m["B-PAR-DELTA"], car = api.m["B-EDU-DIFF"];
    dl.place(0, 0);
    car.place(0, 0);
    keep.carY = car.holder.position.y;
    api.axes(dl, "base", 0.12);
    keep.trA = api.trace(0x1f77b4);
    keep.trB = api.trace(0xe8913a);
    keep.trP = api.trace(0x2ca02c);
    // 侧方停车的车位：前后两辆停着的车、路沿（基座坐标 (x, y) → 世界 (x, ·, −y)）
    const g = new T.Group(), mat = new T.MeshStandardMaterial({ color: 0x8a96a0 });
    for (const x of [-0.16, -1.06]) { const b = new T.Mesh(new T.BoxGeometry(0.34, 0.12, 0.24), mat); b.position.set(x, 0.06, 0.35); g.add(b); }
    const curb = new T.Mesh(new T.BoxGeometry(2.4, 0.03, 0.05), new T.MeshStandardMaterial({ color: 0xb8860b }));
    curb.position.set(-0.6, 0.015, 0.55); g.add(curb);
    api.st.scene.add(g);
    keep.slot = g;
    keep.markA = new T.Mesh(new T.SphereGeometry(0.03, 16, 12), new T.MeshStandardMaterial({ color: 0x1f77b4 }));   // 过程 A 的终点
    keep.markA.visible = false;
    api.st.scene.add(keep.markA);
    // 相机取景用的“盒子”（api.view 只对 api.m 中的对象取景，所以放进 api.m，不可见）
    api.m.frameA = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-0.8, 0, -1.5), new T.Vector3(0.6, 0.3, 0.3)) };
    api.m.frameP = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-1.4, 0, -0.3), new T.Vector3(0.4, 0.3, 0.7)) };
    keep.shown = null;
  },
  reset(api, s) {
    const K = api.keep;
    if (!K.trA) return;
    if (api.scene === "agv" || api.scene === "park") {
      K.trA.clear(); K.trB.clear(); K.trP.clear();
      K.q = [0, 0, 0, 0, 0]; K.prog = null; K.t = 0; K.ends = {}; K.parked = false;
      this.car(api, K.q);
    }
  },
  start(api, s) {
    const K = api.keep;
    if (api.scene === "agv") { K.prog = "A"; K.t = 0; K.q = [0, 0, 0, 0, 0]; }
    else if (api.scene === "park") { K.prog = "P"; K.t = 0; K.q = [0, 0, 0, 0, 0]; }
    else api.stop();
  },
  update(dt, api, s) {
    const K = api.keep;
    if (!K.prog) { api.stop(); return; }
    const rate = 2, h = 1e-3;                // 以两倍速度播放；积分步长 1 ms
    let left = dt * rate;
    while (left > 1e-9 && K.prog) {
      const hh = Math.min(h, left);
      let w;
      if (K.prog === "P") { w = this.parkWheels(K.t); if (!w) { K.prog = null; K.parked = true; break; } }
      else w = this.wheels(K.prog, K.t);
      this.step(K.q, w[0], w[1], hh);
      K.t += hh; left -= hh;
      if (K.prog !== "P" && K.t >= 4 - 1e-9) {
        K.ends[K.prog] = K.q.slice();
        if (K.prog === "A") K.markA.position.set(K.q[0], 0.03, -K.q[1]);
        if (K.prog === "A") { K.prog = "B"; K.t = 0; K.q = [0, 0, 0, 0, 0]; }
        else K.prog = null;
      }
    }
    this.car(api, K.q);
    const c = api.m["B-EDU-DIFF"].point("chassis", [0, 0, 0.0]);
    (K.prog === "P" || api.scene === "park" ? K.trP : K.prog === "B" || (!K.prog && K.ends.B) ? K.trB : K.trA).add(c);
    if (!K.prog) api.stop();
  },
  readouts(api, s) {
    const K = api.keep, f = (v, n) => api.fmt(v, n), dg = 180 / Math.PI;
    if (!api.m["B-PAR-DELTA"] || !api.m["B-EDU-DIFF"] || !K.trA) return [];
    if (api.scene === "ik" || api.scene === "fk") {
      this.delta(api);
      const r = K.dres || { bad: -1, th: [] }, rows = [];
      if (r.bad >= 0) {
        const why = r.why === "reach" ? api.T(`支链 ${r.bad + 1} 够不着：|C| > √(A² + B²)，式 (11.5.7) 无解`, `leg ${r.bad + 1} cannot reach: |C| > √(A² + B²), Eq. (11.5.7) has no solution`)
          : r.why === "limit" ? api.T(`支链 ${r.bad + 1} 的转角 ${f(r.deg, 1)}° 超出 −40°～90°`, `leg ${r.bad + 1} needs ${f(r.deg, 1)}°, outside −40° to 90°`)
            : api.T("三个球面不相交，装不起来", "the three spheres do not meet; it cannot be assembled");
        rows.push([["装配", "assembly"], why]);
        if (api.scene === "ik") api.done("out");
      } else rows.push([["装配", "assembly"], api.T("可以装配", "assembles")]);
      if (K.dth) {
        rows.push([["转角 θ₁, θ₂, θ₃", "angles θ₁, θ₂, θ₃"], K.dth.map((t) => f(t * dg, 2) + "°").join(", ")],
                  [["平台中心 p", "platform centre p"], `(${f(K.dp[0] * 1000, 1)}, ${f(K.dp[1] * 1000, 1)}, ${f(K.dp[2] * 1000, 1)}) mm`],
                  [["平台转角", "platform rotation"], api.T("0°（平行四边形使它只平移）", "0° (the parallelograms keep it from turning)")],
                  [["闭合误差（从模型读点）", "closure error (read off the model)"], f(this.closure(api) * 1000, 4) + " mm"]);
      }
      const p = api.p;
      if (api.scene === "ik" && r.bad < 0 && Math.abs(p.x - 100) < 1 && Math.abs(p.y) < 1 && Math.abs(p.z + 450) < 1) api.done("ik");
      if (api.scene === "fk" && r.bad < 0 && p.a2 === p.a3 && Math.abs(p.a1 - p.a2) >= 20) api.done("fk");
      return rows;
    }
    const q = K.q || [0, 0, 0, 0, 0], inv = q[2] - this.R * (q[3] - q[4]) / this.B;
    const rows = [[["右轮、左轮转角", "right, left wheel angle"], `${f(q[3], 2)}, ${f(q[4], 2)} rad`],
                  [["车头方向 φ", "heading φ"], f(Math.atan2(Math.sin(q[2]), Math.cos(q[2])) * dg, 1) + "°"],
                  [["φ − r(θR − θL)/b", "φ − r(θR − θL)/b"], f(inv, 6) + " rad"],
                  [["车体中心 (x, y)", "body centre (x, y)"], `(${f(q[0], 3)}, ${f(q[1], 3)}) m`]];
    if (api.scene === "agv") {
      rows.unshift([["过程", "programme"], K.prog || (K.ends && K.ends.B ? api.T("A、B 都已完成", "A and B done") : "—")]);
      const A = K.ends && K.ends.A, B = K.ends && K.ends.B;
      if (A) rows.push([["A 终点 (x, y)", "end of A (x, y)"], `(${f(A[0], 3)}, ${f(A[1], 3)}) m`]);
      if (A && B) {
        const gap = Math.hypot(A[0] - B[0], A[1] - B[1]);
        rows.push([["B 终点 (x, y)", "end of B (x, y)"], `(${f(B[0], 3)}, ${f(B[1], 3)}) m`], [["两终点相距", "ends apart by"], f(gap, 3) + " m"]);
        if (Math.abs(A[3] - B[3]) < 0.02 && Math.abs(A[4] - B[4]) < 0.02 && gap > 0.5) api.done("agv");
      }
    } else {
      rows.push([["横向移动", "moved sideways"], f(-q[1], 3) + " m"]);
      if (K.parked && -q[1] > 0.3 && Math.abs(q[2]) < 2 / dg) api.done("park");
    }
    return rows;
  },
  draw(api, s) {
    const m = api.m, sc = api.scene, K = api.keep;
    if (!K.trA) return;
    const isD = sc === "ik" || sc === "fk";
    m["B-PAR-DELTA"].holder.visible = isD;
    m["B-EDU-DIFF"].holder.visible = !isD;
    K.slot.visible = sc === "park";
    K.trA.line.visible = K.trB.line.visible = sc === "agv";
    K.trP.line.visible = sc === "park";
    K.markA.visible = sc === "agv" && !!(K.ends && K.ends.A);
    if (K.shown !== sc) {
      K.shown = sc;
      if (isD) api.view(35, 18, 0.8, m["B-PAR-DELTA"]);
      else api.view(sc === "agv" ? 20 : 10, sc === "agv" ? 60 : 50, 0.9, sc === "agv" ? m.frameA : m.frameP);
    }
    if (isD && !api.running) this.delta(api);
  },
});
