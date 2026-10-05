// 实验 19.5 里程计误差累积（配 19.5 节）。
// 零件库差速 AGV（B-EDU-DIFF：名义 r = 0.05 m、b = 0.26 m）。三维中车体坐标 (x, y) → 世界 (x, ·, −y)。
// 场景“正方形双向测试”（UMBmark 的做法，19.5.5 节）：控制器按“标定参数”让车直行 4 m（两轮转角 4/r_R、4/r_L）、原地转 90°
//   （两轮滚过 ±b·(π/2)/2），重复四次，先逆时针一圈、再顺时针一圈。真车按真实参数 r_R = r(1 + ε/2)、r_L = r(1 − ε/2)、
//   b(1 + ε_b) 积分（式 (19.5.5)），可加随机打滑。里程计以为自己走的是理想的正方形（橙线），真实路径为蓝线。
//   “使用标定”= 1 时，控制器用真实参数（标定完美），系统误差消失。
// 场景“更新公式”：车沿半径 0.5 m 的圆以 0.5 m/s 走一圈（真实轨迹精确已知），里程计每隔 T 读一次两轮转角增量，
//   用欧拉 (19.5.3)、中点 (19.5.4) 或圆弧精确 (19.5.5) 更新；显示里程计轨迹与真实轨迹的最大偏差。
// 场景“随机打滑”：直行 10 m，每步（1 cm）两轮滚过的距离各有方差 k·Δs 的随机误差（式 (19.5.9)），做 20 次，统计终点的横向标准差，
//   与式 (19.5.12) 比较。k 的单位为 10⁻⁶ m。
// 生活场景：蒙眼走正方形：步长 0.7 m、每步步长误差 3%（随机）、每次转身误差标准差 5°，边长 4 m，看终点离起点多远。
WQ.lab({
  title: ["实验 19.5 里程计误差累积", "Lab 19.5 How odometry errors build up"],
  goal: ["看里程计的三类误差怎样产生、怎样累积：更新公式的离散化误差、轮径和轮距的系统误差、车轮打滑的随机误差；用双向正方形测试发现系统误差并检验标定。",
         "See how the three kinds of odometry error arise and build up: discretisation in the update formula, systematic wheel-radius and track errors, and random slip; use the two-way square test to expose systematic errors and check a calibration."],
  view: "3d",
  models: ["B-EDU-DIFF"],
  scenes: [
    { id: "square", robot: true, name: ["正方形双向测试", "Two-way square test"], hide: ["method", "T"],
      problem: { title: ["机器人问题：AGV 走一圈正方形，能回到起点吗", "Robot problem: can the AGV drive a square and get back to the start"],
                 text: ["按“开始”：车先逆时针、再顺时针各走一圈 4 m 的正方形（直行 + 原地转 90°）。橙线是里程计以为的路径，蓝线是真实路径。调两轮半径差、轮距误差和打滑，看两个方向的终点误差。",
                        "Press Start: the AGV drives a 4 m square anticlockwise, then clockwise (straight runs and 90° spins). Orange is the path odometry believes, blue the real one. Change the radius difference, the track error and the slip, and compare the end errors in both directions."] } },
    { id: "circle", robot: true, name: ["更新公式", "Update formula"], hide: ["eps", "epsb", "k", "cal"],
      problem: { title: ["机器人问题：每一步怎样更新位姿", "Robot problem: how should each step update the pose"],
                 text: ["车沿半径 0.5 m 的圆走一圈，车轮没有误差。里程计每隔 T 读一次编码器，用所选的公式更新。比较里程计（橙）与真实（蓝）的最大偏差。",
                        "The AGV drives once round a 0.5 m circle with perfect wheels. Odometry reads the encoders every T and updates with the chosen formula. Compare the largest gap between odometry (orange) and truth (blue)."] } },
    { id: "noise", robot: true, name: ["随机打滑", "Random slip"], hide: ["eps", "epsb", "cal", "method", "T"],
      problem: { title: ["机器人问题：打滑造成的误差怎样随距离增长", "Robot problem: how does slip error grow with distance"],
                 text: ["车按编码器直行 10 m，重复 20 次，每次车轮随机打滑。里程计每次都以为走的是同一条直线，真实的终点却散开了。",
                        "The AGV drives 10 m straight by its encoders, 20 times, with random slip each time. Odometry always believes the same straight line; the real end points spread."] } },
    { id: "walk", name: ["蒙眼走正方形", "Blindfold square walk"], hide: ["eps", "epsb", "cal", "method", "T"],
      problem: { title: ["生活中的例子：数着步子、凭感觉转身", "Everyday example: counting steps and guessing the turns"],
                 text: ["小车代替一个蒙着眼睛的人：每边数 6 步左右（步长 0.7 m）、凭感觉左转 90°，走四条边。步长和转身都有随机误差。看终点离起点多远。",
                        "The cart stands in for a blindfolded walker: about 6 steps a side (0.7 m each), a guessed 90° left turn, four sides. Steps and turns carry random errors. How far from the start does it end?"] } },
  ],
  params: [
    { id: "eps", name: ["两轮半径差 ε", "radius difference ε"], min: 0, max: 0.5, step: 0.05, value: 0.3, unit: "%", digits: 2 },
    { id: "epsb", name: ["轮距误差 ε_b", "track error ε_b"], min: -2, max: 2, step: 0.1, value: 1.0, unit: "%", digits: 1 },
    { id: "k", name: ["打滑强度 k（×10⁻⁶ m）", "slip strength k (×10⁻⁶ m)"], min: 0, max: 100, step: 1, value: 0, unit: "", digits: 0 },
    { id: "cal", name: ["使用标定：0 否 1 是", "use calibration: 0 no 1 yes"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "method", name: ["更新公式：0 欧拉 1 中点 2 圆弧", "update: 0 Euler 1 midpoint 2 arc"], min: 0, max: 2, step: 1, value: 2, digits: 0 },
    { id: "T", name: ["采样周期 T", "sampling period T"], min: 0.01, max: 0.2, step: 0.01, value: 0.1, unit: "s", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "exact", robot: true, text: ["更新公式：圆弧精确更新、T = 0.1 s，里程计与真实轨迹重合（偏差小于 1 mm）。", "Update formula: exact arc update with T = 0.1 s; odometry lies on the true path (gap below 1 mm)."],
      demo: { scene: "circle", set: { method: 2, T: 0.1 }, press: ["start"], wait: 12 } },
    { id: "euler", robot: true, text: ["改用欧拉法、T = 0.1 s，读出最大偏差（应超过 1 cm）。", "Use Euler with T = 0.1 s and read the largest gap (more than 1 cm)."],
      demo: { scene: "circle", set: { method: 0, T: 0.1 }, press: ["start"], wait: 12 } },
    { id: "ccwcw", robot: true, text: ["正方形测试：半径差 0.3%、轮距误差 1%、不标定，读出逆时针和顺时针两个方向的终点误差。", "Square test: radius difference 0.3%, track error 1%, no calibration; read the end errors in both directions."],
      demo: { scene: "square", set: { eps: 0.3, epsb: 1.0, k: 0, cal: 0 }, press: ["start"], wait: 40 } },
    { id: "cal", robot: true, text: ["打开“使用标定”再测一次，使两个方向的终点误差都小于 2 cm。", "Switch calibration on and test again: both end errors below 2 cm."],
      demo: { scene: "square", set: { eps: 0.3, epsb: 1.0, k: 0, cal: 1 }, press: ["start"], wait: 40 } },
    { id: "noise", robot: true, text: ["随机打滑：k = 20×10⁻⁶ m，做 20 次直行 10 m，比较终点横向标准差与式 (19.5.12) 的预测。", "Random slip: k = 20×10⁻⁶ m, 20 runs of 10 m; compare the cross-track spread with Eq. (19.5.12)."],
      demo: { scene: "noise", set: { k: 20 }, press: ["start"], wait: 20 } },
    { id: "walk", text: ["蒙眼走一圈正方形，读出终点离起点的距离。", "Walk the square blindfold and read how far from the start you end."],
      demo: { scene: "walk", set: {}, press: ["start"], wait: 20 } },
  ],
  think: ["正方形测试中，为什么一个方向的误差小、另一个方向大？如果只沿一个方向测，会得出什么错误的结论？", "In the square test, why is one direction much better than the other? What wrong conclusion would a one-way test give?"],

  r: 0.05, b: 0.26,
  rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; },
  gauss(rnd) { let u = 0, v = 0; while (u === 0) u = rnd(); v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  upd(q, dsR, dsL, bb, m) {                     // 三种更新公式；m：0 欧拉，1 中点，2 圆弧精确
    const ds = (dsR + dsL) / 2, dp = (dsR - dsL) / bb, f = q[2];
    if (m === 0) return [q[0] + ds * Math.cos(f), q[1] + ds * Math.sin(f), f + dp];
    if (m === 1 || Math.abs(dp) < 1e-12) return [q[0] + ds * Math.cos(f + dp / 2), q[1] + ds * Math.sin(f + dp / 2), f + dp];
    return [q[0] + ds / dp * (Math.sin(f + dp) - Math.sin(f)), q[1] - ds / dp * (Math.cos(f + dp) - Math.cos(f)), f + dp];
  },
  squarePaths(p, rnd) {                         // 逆时针、顺时针各一圈；返回 [{truth: [[x,y,φ,θR,θL]...], odo: [...], err}]
    const r = this.r, b = this.b, eps = p.eps / 100, rR = r * (1 + eps / 2), rL = r * (1 - eps / 2), bt = b * (1 + p.epsb / 100);
    const cal = Math.round(p.cal) === 1, cR = cal ? rR : r, cL = cal ? rL : r, cb = cal ? bt : b, k = p.k * 1e-6;
    return [1, -1].map((sg) => {
      let q = [0, 0, 0], o = [0, 0, 0], th = [0, 0];
      const truth = [[0, 0, 0, 0, 0]], odo = [[0, 0, 0]];
      for (let side = 0; side < 4; side++) {
        for (const [dR, dL, n] of [[4 / cR, 4 / cL, 400], [sg * cb * Math.PI / 4 / cR, -sg * cb * Math.PI / 4 / cL, 40]]) {
          for (let i = 0; i < n; i++) {
            let sR = rR * dR / n, sL = rL * dL / n;
            if (k > 0) { sR += Math.sqrt(k * Math.abs(sR)) * this.gauss(rnd); sL += Math.sqrt(k * Math.abs(sL)) * this.gauss(rnd); }
            q = this.upd(q, sR, sL, bt, 2); th[0] += dR / n; th[1] += dL / n;
            o = this.upd(o, cR * dR / n, cL * dL / n, cb, 2);
            truth.push([q[0], q[1], q[2], th[0], th[1]]); odo.push(o.slice());
          }
        }
      }
      return { truth, odo, err: Math.hypot(q[0], q[1]) };
    });
  },
  circlePaths(p) {                              // 真实：精确的圆；里程计：每隔 T 用所选公式更新
    const v = 0.5, w = 1.0, Tl = 2 * Math.PI, n = 2000, truth = [], odo = [[0, 0, 0]];
    for (let i = 0; i <= n; i++) { const t = Tl * i / n, f = w * t; truth.push([0.5 * Math.sin(f), 0.5 * (1 - Math.cos(f)), f, (v + w * this.b / 2) / this.r * t, (v - w * this.b / 2) / this.r * t]); }
    const m = Math.round(p.method), N = Math.round(Tl / p.T), h = Tl / N;
    let o = [0, 0, 0], dev = 0;
    for (let j = 1; j <= N; j++) {
      o = this.upd(o, (v + w * this.b / 2) * h, (v - w * this.b / 2) * h, this.b, m);
      odo.push(o.slice());
      const f = w * h * j; dev = Math.max(dev, Math.hypot(o[0] - 0.5 * Math.sin(f), o[1] - 0.5 * (1 - Math.cos(f))));
    }
    return { truth, odo, dev };
  },
  noisePaths(p, rnd) {
    const k = p.k * 1e-6, n = 1000, ds = 10 / n, runs = [];
    for (let j = 0; j < 20; j++) {
      let q = [0, 0, 0]; const path = [[0, 0, 0, 0, 0]];
      for (let i = 0; i < n; i++) {
        const sR = ds + Math.sqrt(k * ds) * this.gauss(rnd), sL = ds + Math.sqrt(k * ds) * this.gauss(rnd);
        q = this.upd(q, sR, sL, this.b, 1);
        path.push([q[0], q[1], q[2], (i + 1) * ds / this.r, (i + 1) * ds / this.r]);
      }
      runs.push(path);
    }
    const ys = runs.map((r) => r[n][1]), m = ys.reduce((a, c) => a + c, 0) / ys.length;
    const sy = Math.sqrt(ys.reduce((a, c) => a + (c - m) * (c - m), 0) / (ys.length - 1));
    return { runs, sy, pred: Math.sqrt(2 * k * 1000 / (3 * this.b * this.b)) };
  },
  walkPath(rnd) {
    let q = [0, 0, 0]; const path = [[0, 0, 0, 0, 0]], step = 0.7, nStep = Math.round(4 / step);
    for (let side = 0; side < 4; side++) {
      for (let i = 0; i < nStep; i++) {
        const L = step * (1 + 0.03 * this.gauss(rnd)), m = 10;
        for (let j = 0; j < m; j++) { q = [q[0] + L / m * Math.cos(q[2]), q[1] + L / m * Math.sin(q[2]), q[2]]; path.push([q[0], q[1], q[2], 0, 0]); }
      }
      const turn = Math.PI / 2 + 5 * Math.PI / 180 * this.gauss(rnd);
      for (let j = 0; j < 10; j++) { q = [q[0], q[1], q[2] + turn / 10]; path.push([q[0], q[1], q[2], 0, 0]); }
    }
    return { path, err: Math.hypot(q[0], q[1]) };
  },

  car(api, q) {
    const c = api.m["B-EDU-DIFF"], K = api.keep;
    c.holder.position.set(q[0], K.carY, -q[1]);
    c.holder.rotation.set(0, q[2], 0);
    c.holder.updateMatrixWorld(true);
    c.set({ right_wheel_joint: q[3] || 0, left_wheel_joint: q[4] || 0 });
  },
  V3(api, x, y, h) { return new api.three.Vector3(x, h || 0.02, -y); },
  setup3d(api, keep) {
    const T = api.three, car = api.m["B-EDU-DIFF"];
    car.place(0, 0);
    keep.carY = car.holder.position.y;
    keep.tr = []; for (let i = 0; i < 20; i++) keep.tr.push(api.trace(i === 0 ? 0x1f77b4 : 0x6fa8dc));
    keep.odo = api.trace(0xe8913a);
    keep.odo2 = api.trace(0xe8913a);
    keep.tr2 = api.trace(0xd62728);
    api.m.fSq = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-0.8, 0, -4.8), new T.Vector3(4.8, 0.3, 4.8)) };
    api.m.fCi = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-0.8, 0, -1.3), new T.Vector3(0.8, 0.3, 0.3)) };
    api.m.fNo = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-0.5, 0, -2.0), new T.Vector3(10.5, 0.3, 2.0)) };
    api.m.fWa = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(-1.0, 0, -5.0), new T.Vector3(5.0, 0.3, 1.0)) };
    keep.shown = null;
  },
  clearAll(K) { K.tr.forEach((t) => t.clear()); K.odo.clear(); K.odo2.clear(); K.tr2.clear(); },
  reset(api, s) {
    const K = api.keep;
    if (!K.tr) return;
    this.clearAll(K);
    s.plan = null; s.k = 0; s.done = false; s.ran = false;
    this.car(api, [0, 0, 0, 0, 0]);
  },
  start(api, s) {
    const K = api.keep, rnd = this.rng(19 + Math.round(api.p.k));
    if (api.scene === "square") {
      const [a, b] = this.squarePaths(api.p, rnd);
      s.plan = a.truth.concat(b.truth.slice(1)); s.res = [a.err, b.err];
      a.odo.forEach((o, i) => { if (i % 10 === 0) K.odo.add(this.V3(api, o[0], o[1], 0.03)); });
      b.odo.forEach((o, i) => { if (i % 10 === 0) K.odo2.add(this.V3(api, o[0], o[1], 0.03)); });
      s.split = a.truth.length; s.rate = 200;
    } else if (api.scene === "circle") {
      const c = this.circlePaths(api.p);
      s.plan = c.truth; s.dev = c.dev; s.rate = 300;
      c.odo.forEach((o) => K.odo.add(this.V3(api, o[0], o[1], 0.03)));
    } else if (api.scene === "noise") {
      const nz = this.noisePaths(api.p, rnd);
      s.runs = nz.runs; s.sy = nz.sy; s.pred = nz.pred; s.plan = nz.runs[0]; s.rate = 250;
      K.odo.add(this.V3(api, 0, 0, 0.03)); K.odo.add(this.V3(api, 10, 0, 0.03));
      nz.runs.forEach((r, j) => { if (j > 0) r.forEach((pp, i) => { if (i % 20 === 0) K.tr[j].add(this.V3(api, pp[0], pp[1])); }); });
    } else {
      const w = this.walkPath(rnd);
      s.plan = w.path; s.werr = w.err; s.rate = 60;
      [[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]].forEach(([x, y]) => K.odo.add(this.V3(api, x, y, 0.03)));
    }
  },
  update(dt, api, s) {
    const K = api.keep;
    if (!s.plan || s.done) { api.stop(); return; }
    const k1 = Math.min(s.plan.length - 1, s.k + Math.max(1, Math.round(dt * s.rate)));
    for (let i = s.k + 1; i <= k1; i++) {
      if (i % 4 === 0 || i === k1) {
        const pp = s.plan[i], tr = api.scene === "square" && i >= (s.split || 1e9) ? K.tr2 : K.tr[0];
        tr.add(this.V3(api, pp[0], pp[1]));
      }
    }
    s.k = k1;
    this.car(api, s.plan[s.k]);
    if (s.k >= s.plan.length - 1) { s.done = true; s.ran = true; api.stop(); }
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, rows = [];
    if (!api.keep || !api.keep.tr) return rows;
    if (api.scene === "square") {
      rows.push([["真实参数 r_R, r_L, b", "true r_R, r_L, b"], `${f(this.r * (1 + p.eps / 200) * 1000, 3)}, ${f(this.r * (1 - p.eps / 200) * 1000, 3)}, ${f(this.b * (1 + p.epsb / 100) * 1000, 1)} mm`],
                [["控制器用的参数", "parameters used"], Math.round(p.cal) === 1 ? api.T("标定值（等于真实值）", "calibrated (equal to the true values)") : api.T("名义值 50、50、260 mm", "nominal 50, 50, 260 mm")]);
      if (s.res) {
        rows.push([["逆时针一圈的终点误差", "end error, anticlockwise"], f(s.res[0] * 100, 2) + " cm"], [["顺时针一圈的终点误差", "end error, clockwise"], f(s.res[1] * 100, 2) + " cm"]);
        if (s.ran && Math.round(p.cal) === 0 && p.eps >= 0.25 && Math.abs(p.epsb) >= 0.5) api.done("ccwcw");
        if (s.ran && Math.round(p.cal) === 1 && Math.max(...s.res) < 0.02 && (p.eps >= 0.25 || Math.abs(p.epsb) >= 0.5)) api.done("cal");
      }
      return rows;
    }
    if (api.scene === "circle") {
      const names = [api.T("欧拉", "Euler"), api.T("中点", "midpoint"), api.T("圆弧精确", "exact arc")];
      rows.push([["更新公式", "update formula"], names[Math.round(p.method)]], [["采样周期 T", "period T"], f(p.T, 2) + " s"],
                [["每个周期车头转过 Δφ", "heading change per period Δφ"], f(p.T * 1.0, 3) + " rad"]);
      if (s.dev !== undefined) {
        rows.push([["里程计与真实轨迹的最大偏差", "largest gap odometry–truth"], s.dev < 1e-6 ? api.T("小于 1 μm", "below 1 μm") : f(s.dev * 1000, 3) + " mm"]);
        if (s.ran && Math.round(p.method) === 2 && s.dev < 1e-3) api.done("exact");
        if (s.ran && Math.round(p.method) === 0 && p.T >= 0.05 && s.dev > 0.01) api.done("euler");
      }
      return rows;
    }
    if (api.scene === "noise") {
      rows.push([["打滑强度 k", "slip strength k"], f(p.k, 0) + " ×10⁻⁶ m"]);
      if (s.sy !== undefined) {
        rows.push([["20 次终点的横向标准差", "cross-track s.d. of 20 ends"], f(s.sy * 1000, 1) + " mm"], [["式 (19.5.12) 的预测", "prediction of Eq. (19.5.12)"], f(s.pred * 1000, 1) + " mm"]);
        if (s.ran && p.k >= 10) api.done("noise");
      }
      return rows;
    }
    if (s.werr !== undefined) {
      rows.push([["每边步数、步长", "steps per side, step length"], api.T("6 步，0.7 m（误差 3%）", "6 steps, 0.7 m (3% error)")], [["转身误差（标准差）", "turn error (s.d.)"], "5°"],
                [["终点离起点", "end from start"], f(s.werr, 2) + " m"]);
      if (s.ran) api.done("walk");
    }
    return rows;
  },
  draw(api, s) {
    const K = api.keep, m = api.m;
    if (!K || !K.tr) return;
    if (K.shown !== api.scene) {
      K.shown = api.scene;
      const fr = { square: m.fSq, circle: m.fCi, noise: m.fNo, walk: m.fWa }[api.scene];
      api.view(0, 62, 0.95, fr);
    }
  },
});
