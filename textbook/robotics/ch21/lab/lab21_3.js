// 实验 21.3 欠驱动的代价（配 21.3 节）。
// 场景“横移”：零件库 X2（B-UAV-X2）从悬停出发沿 y_s 横移 d，高度不变。横滚角走对称梯形曲线（算例 21.3.2）：
//   以角速度上限 ω 转到峰值 φ_p，保持 h，转到 −φ_p，保持 h，转回 0；侧向加速度 ÿ = 𝔤 tan φ（式 (21.3.5)）。
//   先取 φ_p = 倾角限制，用二分法求 h 使位移为 d；若 h = 0 时位移已超过 d，则 h = 0 并二分求 φ_p。积分步长 1 ms。
//   全驱动的比较：T = 2√(d/a)，a = 𝔤 tan(倾角限制)（式 (21.3.6)）。动画放慢 2 倍。
// 生活场景“热气球”（示意值）：0～100 m 高度刮西风 4 m/s（向东吹），100～200 m 刮南风 3 m/s（向北吹），200 m 以上刮东风 2 m/s；
//   升降速度 2 m/s。0～250 s 飞向高度 h₁，250～550 s 飞向高度 h₂，之后降落。目标在东 1300 m、北 900 m。
WQ.lab({
  title: ["实验 21.3 欠驱动的代价", "Lab 21.3 The price of underactuation"],
  goal: ["观察四旋翼横移时必须“先倾斜、再反向倾斜、再放平”，测量欠驱动比全驱动多用的时间，以及倾角限制和横滚角速度限制的影响；用热气球体会怎样借助不能直接控制的运动到达目的地。",
         "See that a quadrotor sliding sideways must tilt, tilt back and level out; measure the extra time compared with a fully actuated craft and how the tilt and roll-rate limits change it; with a hot-air balloon, see how motion you cannot command directly still gets you there."],
  view: "3d",
  models: ["B-UAV-X2"],
  scenes: [
    { id: "move", robot: true, name: ["横移", "Sideways move"], hide: ["h1", "h2"],
      problem: { title: ["机器人问题：横移 2 m 最快要多久", "Robot problem: how fast can X2 slide 2 m sideways"],
                 text: ["从机尾看 X2。按“开始”，它按梯形的横滚角曲线横移距离 d（放慢 2 倍播放）。灰色的方块是侧向加速度上限相同、不必倾斜的假想全驱动飞行器。",
                        "X2 seen from behind. Press Start and it slides the distance d with a trapezoidal roll profile (played 2 times slower). The grey block is an imaginary fully actuated craft with the same lateral-acceleration limit that needs no tilt."] } },
    { id: "balloon", name: ["热气球", "Hot-air balloon"], hide: ["d", "tilt", "rate"],
      problem: { title: ["生活中的例子：只能升降的热气球怎样到达目的地", "Everyday example: a balloon that can only climb or sink"],
                 text: ["热气球只能控制高度。0～100 m 的风向东吹 4 m/s，100～200 m 的风向北吹 3 m/s，200 m 以上的风向西吹 2 m/s（示意值）。选择两段高度 h₁（0～250 s）和 h₂（250～550 s），使它降落在目标（东 1300 m、北 900 m）附近。",
                        "The balloon can only change height. Below 100 m the wind blows east at 4 m/s, 100–200 m north at 3 m/s, above 200 m west at 2 m/s (illustrative). Choose heights h₁ (0–250 s) and h₂ (250–550 s) so it lands near the target, 1300 m east and 900 m north."] } },
  ],
  params: [
    { id: "d", name: ["横移距离 d", "distance d"], min: 0.5, max: 4, step: 0.1, value: 2, unit: "m", digits: 1 },
    { id: "tilt", name: ["倾角限制", "tilt limit"], min: 10, max: 45, step: 1, value: 25, unit: "°", digits: 0 },
    { id: "rate", name: ["横滚角速度限制", "roll-rate limit"], min: 0.5, max: 8, step: 0.1, value: 2, unit: "rad/s", digits: 1 },
    { id: "h1", name: ["第一段高度 h₁", "first height h₁"], min: 20, max: 300, step: 10, value: 150, unit: "m", digits: 0 },
    { id: "h2", name: ["第二段高度 h₂", "second height h₂"], min: 20, max: 300, step: 10, value: 250, unit: "m", digits: 0 },
  ],
  tasks: [
    { id: "base", robot: true, text: ["按默认参数（d = 2 m、25°、2 rad/s）横移，读出用时（约 1.57 s）和全驱动的用时。", "Slide with the defaults (d = 2 m, 25°, 2 rad/s); read the time (about 1.57 s) and the fully actuated time."],
      demo: { scene: "move", set: { d: 2, tilt: 25, rate: 2 }, press: ["start"], wait: 20 } },
    { id: "slow", robot: true, text: ["把横滚角速度限制降到 1 rad/s，再横移 2 m，比较用时。", "Lower the roll-rate limit to 1 rad/s, slide 2 m again and compare."],
      demo: { scene: "move", set: { d: 2, tilt: 25, rate: 1 }, press: ["start"], wait: 20 } },
    { id: "tilt40", robot: true, text: ["角速度限制恢复 2 rad/s，把倾角限制加大到 40°，横移 2 m，看用时缩短多少。", "Back to 2 rad/s, raise the tilt limit to 40°, slide 2 m and see how much time is saved."],
      demo: { scene: "move", set: { d: 2, tilt: 40, rate: 2 }, press: ["start"], wait: 20 } },
    { id: "balloon", text: ["选择 h₁、h₂，让热气球降落在离目标 100 m 以内。", "Choose h₁ and h₂ so the balloon lands within 100 m of the target."],
      demo: { scene: "balloon", set: { h1: 50, h2: 150 }, press: ["start"], wait: 90 } },
  ],
  think: ["横移距离很短时（如 0.5 m），横滚角还来不及转到倾角限制。此时用时由什么决定？倾角限制再放宽还有用吗？",
          "For a very short move (say 0.5 m) the roll never reaches the tilt limit. What sets the time then? Would a larger tilt limit still help?"],

  G: 9.81, CZ: 0.053962, Z0: 0.8, SLOW: 2, TGT: [1300, 900],
  // ---------------- 横移的倾角曲线
  phiAt(t, pp, w, h) {
    const tr = pp / w;
    if (t < tr) return w * t;
    if (t < tr + h) return pp;
    if (t < 3 * tr + h) return pp - w * (t - tr - h);
    if (t < 3 * tr + 2 * h) return -pp;
    if (t < 4 * tr + 2 * h) return -pp + w * (t - 3 * tr - 2 * h);
    return 0;
  },
  run(pp, w, h, dt = 1e-3) {   // 积分得到 (时间, 位移, 速度) 的表
    const T = 4 * pp / w + 2 * h, n = Math.ceil(T / dt), tt = [0], yy = [0], vv = [0];
    let y = 0, v = 0, aPrev = 0;
    for (let i = 1; i <= n; i++) {
      const t = Math.min(T, i * dt), a = this.G * Math.tan(this.phiAt(t, pp, w, h)), hh = t - tt[i - 1];
      const vn = v + 0.5 * (a + aPrev) * hh;
      y += 0.5 * (v + vn) * hh; v = vn; aPrev = a;
      tt.push(t); yy.push(y); vv.push(v);
    }
    return { T, tt, yy, vv };
  },
  plan(p) {
    const d = p.d, pm = p.tilt * Math.PI / 180, w = p.rate;
    const dist = (pp, h) => { const r = this.run(pp, w, h, 2e-3); return r.yy[r.yy.length - 1]; };
    let pp = pm, h = 0;
    if (dist(pm, 0) >= d) {   // 来不及转到倾角限制：h = 0，二分求峰值
      let lo = 0, hi = pm;
      for (let k = 0; k < 40; k++) { const mid = 0.5 * (lo + hi); if (dist(mid, 0) < d) lo = mid; else hi = mid; }
      pp = 0.5 * (lo + hi);
    } else {
      let lo = 0, hi = 10;
      for (let k = 0; k < 40; k++) { const mid = 0.5 * (lo + hi); if (dist(pm, mid) < d) lo = mid; else hi = mid; }
      h = 0.5 * (lo + hi);
    }
    const r = this.run(pp, w, h);
    const a = this.G * Math.tan(pm);
    return Object.assign(r, { pp, w, h, Tfull: 2 * Math.sqrt(d / a), a, vmax: Math.max(...r.vv) });
  },
  // ---------------- 三维
  eulRoll(ph) { const c = Math.cos(ph), s = Math.sin(ph); return [[1, 0, 0], [0, c, -s], [0, s, c]]; },
  place(api, R, p) {
    const T = api.three, K = api.keep, h = api.m["B-UAV-X2"];
    const c = [p[0] - R[0][2] * this.CZ, p[1] - R[1][2] * this.CZ, p[2] - R[2][2] * this.CZ];
    const Ts = new T.Matrix4().set(R[0][0], R[0][1], R[0][2], c[0], R[1][0], R[1][1], R[1][2], c[1], R[2][0], R[2][1], R[2][2], c[2], 0, 0, 0, 1);
    K.Cm.clone().multiply(Ts).multiply(K.MhbInv).decompose(h.holder.position, h.holder.quaternion, h.holder.scale);
    h.holder.updateMatrixWorld(true);
  },
  w2t(api, v) { return new api.three.Vector3(v[0], v[2], -v[1]); },
  setup3d(api, keep) {
    const T = api.three, h = api.m["B-UAV-X2"];
    h.place(0, 0);
    h.holder.updateMatrixWorld(true);
    keep.Cm = new T.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1);
    keep.MhbInv = new T.Matrix4().copy(h.holder.matrixWorld).invert().multiply(h.nodes.x2.matrixWorld).invert();
    keep.thrust = new T.ArrowHelper(new T.Vector3(0, 1, 0), new T.Vector3(), 0.45, 0x1f77b4, 0.08, 0.05);
    api.st.scene.add(keep.thrust);
    keep.ghost = new T.Mesh(new T.BoxGeometry(0.4, 0.06, 0.4), new T.MeshStandardMaterial({ color: 0x9aa6ad, transparent: true, opacity: 0.6 }));
    api.st.scene.add(keep.ghost);
    keep.tr = api.trace(0xe8913a);
    keep.goal = new T.Mesh(new T.CylinderGeometry(0.03, 0.03, 1.6, 8), new T.MeshStandardMaterial({ color: 0x2ca02c }));
    api.st.scene.add(keep.goal);
    // 热气球（示意）：球囊、吊篮；场景按 1:200 缩小画出
    const g = new T.Group();
    const env = new T.Mesh(new T.SphereGeometry(0.35, 24, 18), new T.MeshStandardMaterial({ color: 0xd62728 })); env.scale.set(1, 1.2, 1); env.position.y = 0.55; g.add(env);
    const bk = new T.Mesh(new T.BoxGeometry(0.15, 0.12, 0.15), new T.MeshStandardMaterial({ color: 0x8b5a2b })); g.add(bk);
    api.st.scene.add(g);
    keep.balloon = g;
    keep.flag = new T.Mesh(new T.ConeGeometry(0.25, 0.8, 16), new T.MeshStandardMaterial({ color: 0x2ca02c }));
    keep.flag.rotation.x = Math.PI; api.st.scene.add(keep.flag);
    keep.btr = api.trace(0x1f77b4);
    api.m.fMove = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-0.3, 0.3, -0.5), new T.Vector3(0.3, 1.6, 2.5)) };
    api.m.fBal = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-1, 0, -6), new T.Vector3(9, 2, 1)) };
    keep.shown = null;
  },
  SCB: 1 / 200,
  wind(z) { return z < 100 ? [4, 0] : z < 200 ? [0, 3] : [-2, 0]; },
  reset(api, s) {
    const K = api.keep;
    s.t = 0; s.ran = false; s.done = false;
    if (!K.Cm) return;
    K.tr.clear(); K.btr.clear();
    if (api.scene === "move") {
      s.pl = this.plan(api.p);
      this.place(api, this.eulRoll(0), [0, 0, this.Z0]);
      K.goal.position.copy(this.w2t(api, [0, api.p.d, 0.8]));
    } else {
      s.b = [0, 0, 0];
      K.flag.position.copy(this.w2t(api, [this.TGT[0] * this.SCB, this.TGT[1] * this.SCB, 0.4]));
    }
  },
  start(api, s) { s.t = 0; },
  update(dt, api, s) {
    if (api.scene === "move") {
      const pl = s.pl, t = Math.min(pl.T, s.t + dt / this.SLOW);
      s.t = t;
      const i = Math.min(pl.tt.length - 1, Math.round(t / 1e-3));
      const ph = this.phiAt(t, pl.pp, pl.w, pl.h), y = pl.yy[i];
      // 横移沿 −y_s，即机身的右方；φ > 0 向右倾，加速度朝右
      this.place(api, this.eulRoll(ph), [0, -y, this.Z0]);
      api.keep.tr.add(this.w2t(api, [0, -y, this.Z0]));
      s.ghostY = t < pl.Tfull / 2 ? 0.5 * pl.a * t * t : t < pl.Tfull ? api.p.d - 0.5 * pl.a * (pl.Tfull - t) ** 2 : api.p.d;
      if (t >= pl.T - 1e-12) { s.ran = true; api.stop(); }
    } else {
      let left = dt * 60;   // 放快 60 倍
      while (left > 1e-9 && !s.done) {
        const h = Math.min(0.1, left), b = s.b, tgt = s.t < 250 ? api.p.h1 : s.t < 550 ? api.p.h2 : 0;
        const w = this.wind(b[2]);
        b[0] += w[0] * h; b[1] += w[1] * h; b[2] += Math.max(-2 * h, Math.min(2 * h, tgt - b[2]));
        s.t += h; left -= h;
        if (s.t >= 550 && b[2] <= 1e-9) { s.done = true; s.ran = true; }
      }
      api.keep.btr.add(this.w2t(api, s.b.map((x) => x * this.SCB)));
      if (s.done) api.stop();
    }
  },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "move") {
      const pl = s.pl;
      if (!pl) return [];
      if (s.ran) {
        const p = api.p;
        if (Math.abs(p.d - 2) < 1e-9 && Math.abs(p.tilt - 25) < 1e-9 && Math.abs(p.rate - 2) < 1e-9) api.done("base");
        if (Math.abs(p.d - 2) < 1e-9 && Math.abs(p.tilt - 25) < 1e-9 && Math.abs(p.rate - 1) < 1e-9) api.done("slow");
        if (Math.abs(p.d - 2) < 1e-9 && Math.abs(p.tilt - 40) < 1e-9 && Math.abs(p.rate - 2) < 1e-9) api.done("tilt40");
      }
      return [[["X2 用时", "X2 time"], f(pl.T, 3) + " s"],
              [["全驱动用时 2√(d/a)", "fully actuated 2√(d/a)"], f(pl.Tfull, 3) + " s"],
              [["多用的时间", "extra time"], f(pl.T - pl.Tfull, 3) + " s（" + f((pl.T / pl.Tfull - 1) * 100, 1) + "%）"],
              [["峰值横滚角、保持时间 h", "peak roll, hold h"], `${f(pl.pp * 180 / Math.PI, 1)}°, ${f(pl.h, 3)} s`],
              [["最大侧向速度", "top lateral speed"], f(pl.vmax, 2) + " m/s"],
              [["当前时间", "time now"], f(s.t, 2) + " s"]];
    }
    const b = s.b || [0, 0, 0], miss = Math.hypot(b[0] - this.TGT[0], b[1] - this.TGT[1]);
    if (s.ran && miss <= 100) api.done("balloon");
    return [[["时间", "time"], f(s.t || 0, 0) + " s"],
            [["高度", "height"], f(b[2], 0) + " m"],
            [["向东、向北", "east, north"], `${f(b[0], 0)}, ${f(b[1], 0)} m`],
            [["离目标", "distance to target"], f(miss, 0) + " m"]];
  },
  draw(api, s) {
    const K = api.keep, m = api.m, h = m["B-UAV-X2"];
    if (!K || !K.Cm) return;
    const mv = api.scene === "move";
    h.holder.visible = mv; K.thrust.visible = mv; K.ghost.visible = mv; K.goal.visible = mv; K.tr.line.visible = mv;
    K.balloon.visible = !mv; K.flag.visible = !mv; K.btr.line.visible = !mv;
    if (K.shown !== api.scene) { K.shown = api.scene; mv ? api.view(-90, 8, 1.15, m.fMove) : api.view(-60, 35, 0.9, m.fBal); }
    if (mv) {
      h.holder.updateMatrixWorld(true);
      const c = h.point("x2", [0, 0, this.CZ]), z = h.point("x2", [0, 0, this.CZ + 0.1]).sub(c).normalize();
      K.thrust.position.copy(c); K.thrust.setDirection(z);
      K.ghost.position.copy(this.w2t(api, [0, -(s.ghostY || 0), this.Z0 + 0.7]));
      K.goal.position.copy(this.w2t(api, [0, -api.p.d, 0.8]));
    } else if (s.b) {
      K.balloon.position.copy(this.w2t(api, s.b.map((x) => x * this.SCB)));
    }
  },
});
