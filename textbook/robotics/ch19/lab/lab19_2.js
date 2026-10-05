// 实验 19.2 差速 AGV 的轮速与路线（配 19.2 节）。
// 零件库差速 AGV（B-EDU-DIFF：r 0.05 m、b 0.26 m、轮速上限 20 rad/s）。车体位姿按式 (19.2.7) 逐步精确积分（步长 1 ms），
// 三维中车体坐标 (x, y) → 世界 (x, ·, −y)，车头方向 φ → 绕竖直轴转 φ（与实验 11.5 相同）。
// 场景“数字工厂路线”：车间布置与实验 1.5 相同（factory/digital/wqbus/layout.py），路线 ht-01 → cnc-l01-b 的转折点
// （本章坐标，y = 28 − y_工厂）为 (17, 12)、(17, 9.5)、(7, 9.5)、(7, 19)、(24, 19)、(24, 21.9) m；拐角用半径 ρ 的圆弧过渡，
// 车速曲线与程序 19.2.1 相同：直线 ≤ 1.0 m/s，圆弧 ≤ min(√(aρ), rω_max/(1 + b/(2ρ)))，|dv/dt| ≤ a，起止静止（弧长步长 5 mm）。
// 生活场景：扫地机器人螺旋清扫，车速 0.25 m/s，转弯半径 R(t) = 0.15 + 0.05 t m，ω = v/R。
WQ.lab({
  title: ["实验 19.2 差速 AGV 的轮速与路线", "Lab 19.2 Wheel speeds and routes of a differential AGV"],
  goal: ["用两轮转速驱动差速 AGV，验证车速、角速度、转弯半径与轮速的关系；在三维车间里让 AGV 沿真实路线行驶，比较不同拐弯半径下的行驶时间。",
         "Drive the differential AGV by its two wheel speeds and check how speed, turn rate and radius follow from them; run it along a real route in the 3D workshop and compare trip times for different corner radii."],
  view: "3d",
  models: ["B-EDU-DIFF"],
  scenes: [
    { id: "wheels", robot: true, name: ["轮速与瞬心", "Wheel speeds and the ICR"], hide: ["rho", "alim"],
      problem: { title: ["机器人问题：两个轮子各转多快，车怎样走", "Robot problem: how does the AGV move for given wheel speeds"],
                 text: ["拖动右轮、左轮的转速，按“开始”让车行驶 4 s。界面按式 (19.2.1)～(19.2.4) 给出车速、角速度和转弯半径，黄色小球是瞬心。",
                        "Set the right and left wheel speeds and press Start to drive 4 s. The readouts give speed, turn rate and radius by Eqs. (19.2.1)–(19.2.4); the yellow ball is the ICR."] } },
    { id: "route", robot: true, name: ["数字工厂路线", "Digital-factory route"], hide: ["wR", "wL"],
      problem: { title: ["机器人问题：从热处理炉到车床 B，实际要走多久", "Robot problem: how long from the furnace to lathe B, really"],
                 text: ["AGV 沿算例 19.2.4 的路线行驶（放快 10 倍）。可以改变拐角圆弧的半径 ρ 和允许的加速度 a（横向、切向相同），界面给出车速、两轮转速和行驶时间。",
                        "The AGV drives the route of Example 19.2.4 (10 times faster). Change the corner radius ρ and the allowed acceleration a (lateral and along the path); speed, wheel speeds and trip time are shown."] } },
    { id: "vac", name: ["扫地机器人", "Robot vacuum"], hide: ["wR", "wL", "rho", "alim"],
      problem: { title: ["生活中的例子：扫地机器人的螺旋清扫", "Everyday example: a robot vacuum's spiral"],
                 text: ["小车代替扫地机器人：车速不变，转弯半径慢慢变大，两轮转速之比趋近于 1，车画出一条向外展开的螺旋线。",
                        "The cart stands in for a robot vacuum: constant speed, the turning radius slowly grows, the wheel-speed ratio tends to 1, and the path spirals outwards."] } },
  ],
  params: [
    { id: "wR", name: ["右轮转速 ω_R", "right wheel ω_R"], min: -20, max: 20, step: 0.1, value: 12.6, unit: "rad/s", digits: 1 },
    { id: "wL", name: ["左轮转速 ω_L", "left wheel ω_L"], min: -20, max: 20, step: 0.1, value: 7.4, unit: "rad/s", digits: 1 },
    { id: "rho", name: ["拐角圆弧半径 ρ", "corner radius ρ"], min: 0.3, max: 1.5, step: 0.1, value: 0.5, unit: "m", digits: 1 },
    { id: "alim", name: ["允许的加速度 a", "allowed acceleration a"], min: 0.2, max: 1.0, step: 0.1, value: 0.5, unit: "m/s²", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "circ", robot: true, text: ["让车绕左侧 0.5 m 处的点转圈（R = 0.5 m），行驶一次。", "Make the AGV circle a point 0.5 m to its left (R = 0.5 m) and drive once."],
      demo: { scene: "wheels", set: { wR: 12.6, wL: 7.4 }, press: ["start"], wait: 20 } },
    { id: "spin", robot: true, text: ["让车原地转（R = 0），行驶一次，读出角速度。", "Make the AGV spin on the spot (R = 0), drive once and read the turn rate."],
      demo: { scene: "wheels", set: { wR: 5, wL: -5 }, press: ["start"], wait: 20 } },
    { id: "route", robot: true, text: ["按默认参数（ρ = 0.5 m、a = 0.5 m/s²）跑完车间路线，读出行驶时间（约 48.2 s）。", "Run the workshop route with the defaults (ρ = 0.5 m, a = 0.5 m/s²) and read the trip time (about 48.2 s)."],
      demo: { scene: "route", set: { rho: 0.5, alim: 0.5 }, press: ["start"], wait: 90 } },
    { id: "rho1", robot: true, text: ["把圆弧半径加大到 1.0 m 再跑一遍，比较行驶时间和路程。", "Increase the corner radius to 1.0 m, run again and compare time and distance."],
      demo: { scene: "route", set: { rho: 1.0, alim: 0.5 }, press: ["start"], wait: 90 } },
    { id: "vac", text: ["扫地机器人走出半径 1 m 以上的螺旋。", "Let the robot vacuum spiral out beyond a radius of 1 m."],
      demo: { scene: "vac", set: {}, press: ["start"], wait: 60 } },
  ],
  think: ["算例 19.2.3 中，圆弧上的车速由横向加速度限制，而不是轮速。什么样的圆弧半径下，两种限制同时起作用？",
          "In Example 19.2.3 the arc speed is set by the lateral acceleration, not the wheel limit. For what corner radius do both limits bind together?"],

  r: 0.05, b: 0.26, wmax: 20,
  PTS: [[17, 12], [17, 9.5], [7, 9.5], [7, 19], [24, 19], [24, 21.9]],
  SHOP: [["ht-01", "热处理炉", "furnace", 17, 13, 5, 4], ["cnc-l01-b", "数控车床 B", "lathe B", 24, 4, 4, 2.2], ["cnc-l01-a", "数控车床 A", "lathe A", 17, 4, 4, 2.2],
         ["saw-01", "带锯床", "band saw", 10, 4, 4, 2.5], ["vmc-01", "立式加工中心", "VMC", 10, 22, 3.5, 3], ["hmc-01", "卧式加工中心", "HMC", 17, 22, 4.5, 3.5],
         ["hob-01", "滚齿机", "gear hobber", 24, 22, 3.5, 2.5], ["key-01", "键槽铣床", "keyway miller", 31, 4, 3, 2.2], ["store-01", "原料库", "raw store", 3, 4, 4, 5]],

  // ---------------- 运动学
  step(q, V, h) {                                // 式 (19.2.7)：一步内运动旋量 (ω, v) 不变
    const [w, v] = V, f = q[2];
    if (Math.abs(w) < 1e-12) { q[0] += v * h * Math.cos(f); q[1] += v * h * Math.sin(f); }
    else { q[0] += v / w * (Math.sin(f + w * h) - Math.sin(f)); q[1] -= v / w * (Math.cos(f + w * h) - Math.cos(f)); }
    q[2] += w * h;
  },
  twistOf(wR, wL) { return [this.r * (wR - wL) / this.b, this.r * (wR + wL) / 2]; },     // (ω, v)，式 (19.2.1)、(19.2.2)
  profile(rho, acc) {                            // 路线的弧长离散、曲率、车速与时刻
    const P = this.PTS.map((p) => p.slice()), segs = [];
    let cur = P[0];
    for (let k = 1; k < P.length - 1; k++) {
      const a = P[k - 1], b = P[k], c = P[k + 1];
      const lu = Math.hypot(b[0] - a[0], b[1] - a[1]), lw = Math.hypot(c[0] - b[0], c[1] - b[1]);
      const u = [(b[0] - a[0]) / lu, (b[1] - a[1]) / lu], w = [(c[0] - b[0]) / lw, (c[1] - b[1]) / lw];
      const turn = Math.atan2(u[0] * w[1] - u[1] * w[0], u[0] * w[0] + u[1] * w[1]), d = rho * Math.tan(Math.abs(turn) / 2);
      const t1 = [b[0] - d * u[0], b[1] - d * u[1]], sg = turn > 0 ? 1 : -1, cen = [t1[0] - sg * rho * u[1], t1[1] + sg * rho * u[0]];
      segs.push({ line: [cur, t1] }, { arc: { cen, a0: Math.atan2(t1[1] - cen[1], t1[0] - cen[0]), turn } });
      cur = [b[0] + d * w[0], b[1] + d * w[1]];
    }
    segs.push({ line: [cur, P[P.length - 1]] });
    const xy = [], kap = [], hd = [], cen = [], S = [], ds = 0.005;   // 与程序 19.2.1 相同：每段 n 等分，取各小段中点
    let s0 = 0;
    segs.forEach((sgm) => {
      if (sgm.line) {
        const [p, q] = sgm.line, L = Math.hypot(q[0] - p[0], q[1] - p[1]), n = Math.max(1, Math.round(L / ds)), h = Math.atan2(q[1] - p[1], q[0] - p[0]);
        for (let i = 0; i < n; i++) { const t = (i + 0.5) / n; xy.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])]); kap.push(0); hd.push(h); cen.push(null); S.push(s0 + t * L); }
        s0 += L;
      } else {
        const { cen: c, a0, turn } = sgm.arc, L = Math.abs(turn) * rho, n = Math.max(1, Math.round(L / ds)), sg = turn > 0 ? 1 : -1;
        for (let i = 0; i < n; i++) { const a = a0 + turn * (i + 0.5) / n; xy.push([c[0] + rho * Math.cos(a), c[1] + rho * Math.sin(a)]); kap.push(sg / rho); hd.push(a + sg * Math.PI / 2); cen.push(c); S.push(s0 + (i + 0.5) / n * L); }
        s0 += L;
      }
    });
    const Ltot = s0;
    const vline = Math.min(1.0, this.r * this.wmax), varc = Math.min(Math.sqrt(acc * rho), this.r * this.wmax / (1 + this.b / (2 * rho)));
    const v = kap.map((k) => (k ? varc : vline)), n = v.length;
    v[0] = Math.min(v[0], Math.sqrt(2 * acc * S[0]));
    for (let i = 1; i < n; i++) v[i] = Math.min(v[i], Math.sqrt(v[i - 1] * v[i - 1] + 2 * acc * (S[i] - S[i - 1])));
    v[n - 1] = Math.min(v[n - 1], Math.sqrt(2 * acc * (Ltot - S[n - 1])));
    for (let i = n - 2; i >= 0; i--) v[i] = Math.min(v[i], Math.sqrt(v[i + 1] * v[i + 1] + 2 * acc * (S[i + 1] - S[i])));
    const t = [2 * S[0] / v[0]];
    for (let i = 1; i < n; i++) t.push(t[i - 1] + 2 * (S[i] - S[i - 1]) / (v[i] + v[i - 1]));
    const T = t[n - 1] + 2 * (Ltot - S[n - 1]) / v[n - 1];
    return { xy, kap, hd, cen, v, t, S, T, L: Ltot, varc };
  },
  at(pr, tq) {                                   // 时刻 tq 的点（二分查找）
    let lo = 0, hi = pr.t.length - 1;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (pr.t[m] <= tq) lo = m; else hi = m; }
    return lo;
  },

  // ---------------- 三维
  car(api, q, th) {
    const c = api.m["B-EDU-DIFF"], K = api.keep, off = api.scene === "route" ? K.off : [0, 0];
    c.holder.position.set(q[0] + off[0], K.carY, -(q[1] + off[1]));
    c.holder.rotation.set(0, q[2], 0);
    c.holder.updateMatrixWorld(true);
    c.set({ right_wheel_joint: th[0], left_wheel_joint: th[1] });
  },
  setup3d(api, keep) {
    const T = api.three, car = api.m["B-EDU-DIFF"];
    car.place(0, 0);
    keep.carY = car.holder.position.y;
    keep.tr = api.trace(0x1f77b4);
    keep.plan = api.trace(0x9aa6ad);
    keep.icr = new T.Mesh(new T.SphereGeometry(0.03, 16, 12), new T.MeshStandardMaterial({ color: 0xf2c200 }));
    api.st.scene.add(keep.icr);
    // 车间（与实验 1.5 相同的 workshop），平面坐标 (x, y_工厂) → 世界 (x − 25, ·, y_工厂 − 14)
    const spec = { floor: { w: 50, d: 28 }, aisles: [{ x: 25, y: 9.0, w: 49, d: 2 }, { x: 25, y: 18.5, w: 49, d: 2 }, { x: 7, y: 13.75, w: 2, d: 9.5 }], units: [], agvs: [] };
    this.SHOP.forEach(([id, z, e, x, y, w, d]) => spec.units.push({ id, name: [z, e], x, y, w, d, h: id.startsWith("store") ? 2.2 : 1.6, store: id.startsWith("store"), highlight: id === "ht-01" || id === "cnc-l01-b" }));
    keep.shop = WQ3D.workshop(api.st, spec);
    keep.off = [-25, -14];                       // 本章坐标 (x, y) → 世界 (x − 25, ·, −(y − 14))
    const pin = new T.Mesh(new T.ConeGeometry(0.35, 1.0, 16), new T.MeshStandardMaterial({ color: 0xe8913a }));
    pin.rotation.x = Math.PI; keep.pin = pin; api.st.scene.add(pin);
    keep.grid = api.st.grid;
    api.m.fWheels = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-0.9, 0, -0.9), new T.Vector3(0.9, 0.3, 0.9)) };
    api.m.fRoute = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-19, 0, -8.5), new T.Vector3(0, 1.5, 4.5)) };
    api.m.fVac = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-1.6, 0, -1.8), new T.Vector3(1.6, 0.3, 1.4)) };
    keep.shown = null;
  },
  reset(api, s) {
    const K = api.keep;
    if (!K.tr) return;
    K.tr.clear(); K.plan.clear();
    s.q = [0, 0, 0]; s.th = [0, 0]; s.t = 0; s.done = false; s.ran = false; s.maxR = 0; s.ws = [0, 0];
    if (api.scene === "route") {
      s.pr = this.profile(api.p.rho, api.p.alim);
      s.q = [s.pr.xy[0][0], s.pr.xy[0][1], s.pr.hd[0]];
      s.pr.xy.forEach((p, i) => { if (i % 20 === 0) K.plan.add(new api.three.Vector3(p[0] + K.off[0], 0.03, -(p[1] + K.off[1]))); });
    }
    this.car(api, s.q, s.th);
  },
  start(api, s) { s.go = true; },
  update(dt, api, s) {
    const K = api.keep;
    if (!s.q || s.done) { api.stop(); return; }
    if (api.scene === "route") {
      const rate = 10, pr = s.pr;
      const t1 = Math.min(pr.T, s.t + dt * rate), i0 = this.at(pr, s.t), i1 = this.at(pr, t1);
      const vv = pr.v[i1], k = pr.kap[i1];
      s.ws = [(vv + vv * k * this.b / 2) / this.r, (vv - vv * k * this.b / 2) / this.r];
      s.th[0] += s.ws[0] * (t1 - s.t); s.th[1] += s.ws[1] * (t1 - s.t);
      s.t = t1; s.i = i1;
      s.q = [pr.xy[i1][0], pr.xy[i1][1], pr.hd[i1]];
      if (i1 > i0 || i1 === 0) K.tr.add(new api.three.Vector3(s.q[0] + K.off[0], 0.05, -(s.q[1] + K.off[1])));
      if (s.t >= pr.T - 1e-9) { s.done = true; s.ran = true; s.q = [this.PTS[5][0], this.PTS[5][1], Math.PI / 2]; api.stop(); }
    } else {
      const Tend = api.scene === "vac" ? 28 : 4, rate = api.scene === "vac" ? 4 : 1;
      let left = Math.min(dt * rate, Tend - s.t);
      while (left > 1e-9) {
        const h = Math.min(1e-3 * rate, left);
        let V;
        if (api.scene === "vac") { const R = 0.15 + 0.05 * s.t, v = 0.25; V = [v / R, v]; s.maxR = R; s.ws = [(v + V[0] * this.b / 2) / this.r, (v - V[0] * this.b / 2) / this.r]; }
        else { V = this.twistOf(api.p.wR, api.p.wL); s.ws = [api.p.wR, api.p.wL]; }
        this.step(s.q, V, h);
        s.th[0] += s.ws[0] * h; s.th[1] += s.ws[1] * h;
        s.t += h; left -= h;
      }
      K.tr.add(new api.three.Vector3(s.q[0], 0.02, -s.q[1]));
      if (s.t >= Tend - 1e-9) { s.done = true; s.ran = true; api.stop(); }
    }
    this.car(api, s.q, s.th);
  },
  readouts(api, s) {
    if (!s.q) return [];
    const f = api.fmt, rows = [];
    if (api.scene === "wheels") {
      const [w, v] = this.twistOf(api.p.wR, api.p.wL), R = Math.abs(w) > 1e-9 ? v / w : Infinity;
      rows.push([["车速 v = r(ω_R + ω_L)/2", "speed v = r(ω_R + ω_L)/2"], f(v, 3) + " m/s"],
                [["角速度 ω = r(ω_R − ω_L)/b", "turn rate ω = r(ω_R − ω_L)/b"], f(w, 3) + " rad/s"],
                [["转弯半径 R = v/ω", "radius R = v/ω"], isFinite(R) ? f(R, 3) + " m" : api.T("无穷大（直行）", "infinite (straight)")],
                [["车头方向 φ", "heading φ"], f(s.q[2] * 180 / Math.PI, 1) + "°"],
                [["车体中心 (x, y)", "centre (x, y)"], `(${f(s.q[0], 3)}, ${f(s.q[1], 3)}) m`]);
      if (s.ran && Math.abs(R - 0.5) < 0.01) api.done("circ");
      if (s.ran && Math.abs(api.p.wR + api.p.wL) < 1e-9 && Math.abs(api.p.wR) > 0.5) api.done("spin");
      return rows;
    }
    if (api.scene === "route") {
      const pr = s.pr;
      if (!pr) return [];
      const i = s.i || 0;
      rows.push([["路线长度（圆弧过渡后）", "route length (rounded)"], f(pr.L, 2) + " m"],
                [["圆弧上的最高车速", "top speed on the arcs"], f(pr.varc, 3) + " m/s"],
                [["时间 / 总时间", "time / total"], `${f(s.t, 1)} / ${f(pr.T, 1)} s`],
                [["车速 v", "speed v"], f(pr.v[i], 2) + " m/s"],
                [["右轮、左轮转速", "right, left wheel speed"], `${f(s.ws[0], 1)}, ${f(s.ws[1], 1)} rad/s`],
                [["按折线估计 L/v", "polyline estimate L/v"], "41.9 s"]);
      if (s.ran && Math.abs(api.p.rho - 0.5) < 1e-6 && Math.abs(api.p.alim - 0.5) < 1e-6) api.done("route");
      if (s.ran && Math.abs(api.p.rho - 1.0) < 1e-6) api.done("rho1");
      return rows;
    }
    const R = 0.15 + 0.05 * s.t;
    rows.push([["时间", "time"], f(s.t, 1) + " s"], [["当前转弯半径 R", "current radius R"], f(R, 2) + " m"],
              [["右轮、左轮转速", "right, left wheel speed"], `${f(s.ws[0], 2)}, ${f(s.ws[1], 2)} rad/s`],
              [["两轮转速之比 ω_L/ω_R", "ratio ω_L/ω_R"], Math.abs(s.ws[0]) > 1e-9 ? f(s.ws[1] / s.ws[0], 3) : "—"]);
    if (s.ran && s.maxR >= 1.0) api.done("vac");
    return rows;
  },
  draw(api, s) {
    const K = api.keep, m = api.m;
    if (!K || !K.tr) return;
    const route = api.scene === "route";
    K.shop.group.visible = route;
    if (K.grid) K.grid.visible = !route;
    K.pin.visible = route;
    K.plan.line.visible = route;
    if (K.shown !== api.scene) {
      K.shown = api.scene;
      if (route) api.view(0, 58, 1.1, m.fRoute);
      else if (api.scene === "vac") api.view(20, 60, 0.9, m.fVac);
      else api.view(20, 55, 0.9, m.fWheels);
    }
    if (route && s.q) K.pin.position.set(s.q[0] + K.off[0], 1.3, -(s.q[1] + K.off[1]));
    const [w, v] = this.twistOf(api.p.wR, api.p.wL);
    const show = api.scene === "wheels" && Math.abs(w) > 1e-9 && Math.abs(v / w) < 1.2 && s.q;
    K.icr.visible = !!show;
    if (show) { const R = v / w; K.icr.position.set(s.q[0] - R * Math.sin(s.q[2]), 0.03, -(s.q[1] + R * Math.cos(s.q[2]))); }
  },
});
