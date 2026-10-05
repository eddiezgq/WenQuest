// 实验 19.4 阿克曼转向（配 19.4 节）。
// 牵引式 AGV：轴距 L = 1.2 m，前轮距 w = 0.8 m（后轮距相同），车身长 1.8 m、宽 1.0 m，前轴到车头 0.3 m、后轴到车尾 0.3 m，
// 内侧前轮最大转角 40°。车体参考点取后轴中点，按自行车模型 (19.4.4) 积分：φ̇ = v tan δ / L，tan δ = L/R。
// 阿克曼：内侧前轮 δi，外侧 cot δo = cot δi + w/L；平行转向：两前轮都转 δi，外侧前轮的侧偏角 = δi − 阿克曼的 δo。
// 转向梯形（算例 19.4.3）：梯形臂长 0.15 m、底角 λ，横拉杆长 w − 2a sin λ，由闭环条件 (19.4.6) 用二分法求外侧轮转角，
//   内侧轮 0.5°～40° 取 40 个点，与理想值比较。
// 调头：车身右侧离下方墙 0.1 m，以最小转弯半径左转 180°，检查车身轮廓是否碰到上方的墙。
// 生活场景：侧方停车（算例 19.4.4）：倒车右打满转 α、倒车左打满转回 α、前进回到原纵向位置，向右横移 0.6 m。
WQ.lab({
  title: ["实验 19.4 阿克曼转向", "Lab 19.4 Ackermann steering"],
  goal: ["用阿克曼条件和自行车模型计算前轮转角、转弯半径和调头所需的空间，设计转向梯形，体会汽车类车辆怎样横移。",
         "Use the Ackermann condition and the bicycle model to find wheel angles, turning radius and the room to turn round, design a steering trapezoid, and see how a car-like vehicle moves sideways."],
  scenes: [
    { id: "turn", robot: true, name: ["转弯与瞬心", "Turning and the ICR"], hide: ["lam", "aisle"],
      problem: { title: ["机器人问题：两个前轮各转多少", "Robot problem: how far does each front wheel turn"],
                 text: ["调内侧前轮的转角 δi（正为左转）和车速，选择阿克曼转向或平行转向，按“开始”行驶 4 s。红色虚线是四个车轮的轴线，黄点是瞬心。",
                        "Set the inner front-wheel angle δi (positive left) and the speed, choose Ackermann or parallel steering, and press Start to drive 4 s. Red dashed lines are the four wheel axles, the yellow dot the ICR."] } },
    { id: "trap", robot: true, name: ["转向梯形", "Steering trapezoid"], hide: ["delta", "v", "mode", "aisle"],
      problem: { title: ["机器人问题：连杆能做到阿克曼条件吗", "Robot problem: can a linkage give the Ackermann angles"],
                 text: ["调梯形底角 λ，曲线是外侧前轮转角减去阿克曼理想值（内侧轮从 0 转到 40°），读出最大误差。",
                        "Adjust the base angle λ; the curve is the outer-wheel angle minus the Ackermann ideal as the inner wheel goes from 0 to 40°. Read the worst error."] } },
    { id: "uturn", robot: true, name: ["通道调头", "Turning round in an aisle"], hide: ["delta", "v", "mode", "lam"],
      problem: { title: ["机器人问题：这条通道能一次调头吗", "Robot problem: can it turn round in this aisle in one go"],
                 text: ["车贴着下方的墙出发，方向打满左转 180°。调通道宽度，按“开始”，看车身是否碰墙。",
                        "The vehicle starts next to the lower wall and turns left 180° at full lock. Set the aisle width, press Start and see whether the body hits a wall."] } },
    { id: "park", name: ["侧方停车", "Parallel parking"], hide: ["delta", "v", "mode", "lam", "aisle"],
      problem: { title: ["生活中的例子：侧方停车", "Everyday example: parallel parking"],
                 text: ["汽车不能横着走。按“开始”：倒车、方向向右打满；倒车、方向向左打满；最后前进回正，车向右平移 0.6 m。",
                        "A car cannot move sideways. Press Start: reverse at full right lock, reverse at full left lock, then drive forward straight; the car ends 0.6 m to the right."] } },
  ],
  params: [
    { id: "delta", name: ["内侧前轮转角 δi（正为左转）", "inner front angle δi (left +)"], min: -40, max: 40, step: 0.1, value: 30, unit: "°", digits: 1 },
    { id: "v", name: ["车速 v（后轴中点）", "speed v (rear-axle centre)"], min: -1, max: 1, step: 0.1, value: 0.8, unit: "m/s", digits: 1 },
    { id: "mode", name: ["转向方式：0 阿克曼 1 平行", "steering: 0 Ackermann 1 parallel"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "lam", name: ["梯形底角 λ", "trapezoid base angle λ"], min: 0, max: 30, step: 0.5, value: 18.5, unit: "°", digits: 1 },
    { id: "aisle", name: ["通道宽度", "aisle width"], min: 4, max: 8, step: 0.1, value: 5, unit: "m", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "r3", robot: true, text: ["让车以 3 m 的转弯半径（后轴中点）左转，读出两前轮的转角。", "Make the vehicle turn left with a 3 m radius (rear-axle centre) and read both front angles."],
      demo: { scene: "turn", set: { delta: 24.8, v: 0.8, mode: 0 }, press: ["start"], wait: 4 } },
    { id: "par", robot: true, text: ["改为平行转向，δi = 30°，读出外侧前轮的侧偏角（约 7.4°）。", "Switch to parallel steering with δi = 30° and read the outer wheel's slip angle (about 7.4°)."],
      demo: { scene: "turn", set: { delta: 30, v: 0.8, mode: 1 }, press: ["start"], wait: 4 } },
    { id: "trap", robot: true, text: ["调梯形底角，使外侧轮转角的最大误差小于 0.7°。", "Adjust the base angle until the worst outer-angle error is below 0.7°."],
      demo: { scene: "trap", set: { lam: 22.5 }, press: [], wait: 2 } },
    { id: "uturn", robot: true, text: ["在 6 m 宽的通道里一次调头（车身不碰墙）。", "Turn round in a 6 m aisle in one go without touching a wall."],
      demo: { scene: "uturn", set: { aisle: 6 }, press: ["start"], wait: 8 } },
    { id: "park", text: ["完成侧方停车：车向右平移 0.6 m，车头方向回正。", "Park: 0.6 m to the right with the heading straight again."],
      demo: { scene: "park", set: {}, press: ["start"], wait: 10 } },
  ],
  think: ["算例 19.4.2 中调头需要约 5.1 m，差速 AGV 原地转只要 0.4 m。在车间设计中，你会怎样在两种车之间取舍？",
          "In Example 19.4.2 turning round needs about 5.1 m, while the differential AGV spins in 0.4 m. How would you choose between the two for a workshop?"],

  L: 1.2, W: 0.8, OF: 0.3, OR: 0.3, BW: 1.0, DMAX: 40, AK: 0.15,
  rad: (d) => d * Math.PI / 180,
  outerAck(di) { return Math.abs(di) < 1e-9 ? 0 : Math.sign(di) * Math.atan(1 / (1 / Math.tan(Math.abs(di)) + this.W / this.L)); },
  Rmin() { return this.L / Math.tan(this.rad(this.DMAX)) + this.W / 2; },
  outerTrap(di, lam) {                                // 转向梯形：左转、左轮在内侧转 di，求右轮转角（二分法）
    const a = this.AK, W = this.W, rod = W - 2 * a * Math.sin(lam);
    const rot = (t, u) => [u[0] * Math.cos(t) - u[1] * Math.sin(t), u[0] * Math.sin(t) + u[1] * Math.cos(t)];
    const ul = rot(di, [-Math.cos(lam), -Math.sin(lam)]), Al = [a * ul[0], W / 2 + a * ul[1]];
    const g = (t) => { const ur = rot(t, [-Math.cos(lam), Math.sin(lam)]), Ar = [a * ur[0], -W / 2 + a * ur[1]]; return Math.hypot(Al[0] - Ar[0], Al[1] - Ar[1]) - rod; };
    let lo = -0.05, hi = di + 0.05;
    for (let i = 0; i < 50; i++) { const m = (lo + hi) / 2; if (g(lo) * g(m) <= 0) hi = m; else lo = m; }
    return (lo + hi) / 2;
  },
  trapCurve(lam) {
    const pts = [];
    for (let i = 0; i < 40; i++) { const d = this.rad(0.5 + i * 39.5 / 39); pts.push([d * 180 / Math.PI, (this.outerTrap(d, lam) - this.outerAck(d)) * 180 / Math.PI]); }
    return pts;
  },
  bikeStep(q, v, delta, h) {                          // 自行车模型，一步内 v、δ 不变：圆弧精确积分
    const k = Math.tan(delta) / this.L, ds = v * h, dp = k * ds;
    if (Math.abs(dp) < 1e-12) { q[0] += ds * Math.cos(q[2]); q[1] += ds * Math.sin(q[2]); }
    else { q[0] += (Math.sin(q[2] + dp) - Math.sin(q[2])) / k; q[1] -= (Math.cos(q[2] + dp) - Math.cos(q[2])) / k; }
    q[2] += dp;
  },
  outline(q) {                                         // 车身四角（世界坐标）
    return [[-this.OR, -this.BW / 2], [this.L + this.OF, -this.BW / 2], [this.L + this.OF, this.BW / 2], [-this.OR, this.BW / 2]].map(([u, v]) =>
      [q[0] + u * Math.cos(q[2]) - v * Math.sin(q[2]), q[1] + u * Math.sin(q[2]) + v * Math.cos(q[2])]);
  },
  parkPlan() {
    const R = this.Rmin(), a = Math.acos(1 - 0.6 / (2 * R)), db = Math.atan(this.L / R);
    return [[-1, -db, R * a], [-1, db, R * a], [1, 0, 2 * R * Math.sin(a)]];     // (车速符号, 等效转角, 路程)
  },

  reset(api, s) {
    s.q = [0, 0, 0]; s.t = 0; s.trail = [[0, 0]]; s.ran = false; s.hit = false; s.seg = 0; s.segS = 0; s.maxY = -1e9; s.minY = 1e9;
    if (api.scene === "uturn") s.q = [0, -api.p.aisle / 2 + 0.1 + this.BW / 2, 0];
  },
  start(api, s) { s.go = true; },
  update(dt, api, s) {
    if (!s.q || s.ran) { api.stop(); return; }
    const p = api.p;
    if (api.scene === "turn") {
      const di = this.rad(p.delta), R = Math.abs(di) > 1e-9 ? this.L / Math.tan(Math.abs(di)) + this.W / 2 : Infinity;
      const db = isFinite(R) ? Math.sign(di) * Math.atan(this.L / R) : 0;
      const h = Math.min(dt, 4 - s.t);
      this.bikeStep(s.q, p.v, db, h); s.t += h;
      if (s.t >= 4 - 1e-9) { s.ran = true; api.stop(); }
    } else if (api.scene === "uturn") {
      const R = this.Rmin(), db = Math.atan(this.L / R), rate = 3;
      let left = dt * rate;
      while (left > 1e-9 && !s.ran) {
        const h = Math.min(0.01, left);
        this.bikeStep(s.q, 0.5, db, h); left -= h;
        this.outline(s.q).forEach(([, y]) => { s.maxY = Math.max(s.maxY, y); s.minY = Math.min(s.minY, y); });
        if (s.maxY > p.aisle / 2 || s.minY < -p.aisle / 2) s.hit = true;
        if (s.q[2] >= Math.PI - 1e-9) s.ran = true;
      }
      if (s.ran) api.stop();
    } else if (api.scene === "park") {
      const plan = this.parkPlan(), rate = 1.5;
      let left = dt * rate;
      while (left > 1e-9 && s.seg < plan.length) {
        const [sg, db, Ls] = plan[s.seg], ds = Math.min(0.01, Ls - s.segS, left * 0.5);
        this.bikeStep(s.q, sg, db, ds); s.segS += ds; left -= ds / 0.5;
        if (s.segS >= Ls - 1e-9) { s.seg += 1; s.segS = 0; }
      }
      if (s.seg >= plan.length) { s.ran = true; api.stop(); }
    } else { s.ran = true; api.stop(); }
    s.trail.push([s.q[0], s.q[1]]);
  },
  readouts(api, s) {
    if (!s.q) return [];
    const f = api.fmt, p = api.p, rows = [], deg = 180 / Math.PI;
    if (api.scene === "turn") {
      const di = this.rad(p.delta), doA = this.outerAck(di), par = Math.round(p.mode) === 1;
      const R = Math.abs(di) > 1e-9 ? this.L / Math.tan(Math.abs(di)) + this.W / 2 : Infinity;
      rows.push([["内侧前轮 δi、外侧前轮 δo", "inner δi, outer δo"], `${f(Math.abs(p.delta), 1)}°, ${f(Math.abs(par ? di : doA) * deg, 2)}°`],
                [["转弯半径 R（后轴中点）", "radius R (rear-axle centre)"], isFinite(R) ? f(R, 3) + " m" : api.T("无穷大", "infinite")],
                [["自行车模型的等效转角 δ", "bicycle-model angle δ"], isFinite(R) ? f(Math.atan(this.L / R) * deg, 2) + "°" : "0°"],
                [["后轮转速之比（外/内）", "rear wheel ratio (outer/inner)"], isFinite(R) ? f((R + this.W / 2) / (R - this.W / 2), 3) : "1"]);
      if (par && Math.abs(di) > 1e-9) rows.push([["外侧前轮侧偏角", "outer wheel slip angle"], f((Math.abs(di) - Math.abs(doA)) * deg, 2) + "°"]);
      if (s.ran && !par && Math.abs(R - 3) < 0.05 && p.delta > 0) api.done("r3");
      if (s.ran && par && Math.abs(p.delta - 30) < 0.05) api.done("par");
      return rows;
    }
    if (api.scene === "trap") {
      const c = this.trapCurve(this.rad(p.lam)), worst = Math.max(...c.map((x) => Math.abs(x[1])));
      rows.push([["梯形底角 λ", "base angle λ"], f(p.lam, 1) + "°"], [["横拉杆长", "tie-rod length"], f(this.W - 2 * this.AK * Math.sin(this.rad(p.lam)), 3) + " m"],
                [["最大误差（0～40°）", "worst error (0–40°)"], f(worst, 2) + "°"],
                [["经验底角 atan(w/2L)", "rule of thumb atan(w/2L)"], f(Math.atan(this.W / 2 / this.L) * deg, 2) + "°"]);
      if (worst < 0.7) api.done("trap");
      return rows;
    }
    if (api.scene === "uturn") {
      rows.push([["最小转弯半径（后轴中点）", "minimum radius (rear-axle centre)"], f(this.Rmin(), 3) + " m"],
                [["通道宽度", "aisle width"], f(p.aisle, 1) + " m"], [["已转过", "turned"], f(s.q[2] * deg, 0) + "°"],
                [["车身扫过的宽度", "width swept by the body"], s.maxY > -1e8 ? f(s.maxY - s.minY, 2) + " m" : "—"],
                [["结果", "result"], s.hit ? api.T("碰墙：要三点调头", "hits a wall: needs a three-point turn") : s.ran ? api.T("一次调头成功", "turned round in one go") : "—"]);
      if (s.ran && !s.hit && p.aisle <= 6.05) api.done("uturn");
      return rows;
    }
    rows.push([["阶段", "stage"], [api.T("① 倒车、向右打满", "① reverse, full right"), api.T("② 倒车、向左打满", "② reverse, full left"), api.T("③ 前进回正", "③ forward, straight"), api.T("完成", "done")][Math.min(s.seg, 3)]],
              [["横向位置 y", "lateral position y"], f(s.q[1], 3) + " m"], [["车头方向 φ", "heading φ"], f(s.q[2] * deg, 2) + "°"],
              [["纵向位置 x", "position x"], f(s.q[0], 3) + " m"]);
    if (s.ran && Math.abs(s.q[1] + 0.6) < 0.01 && Math.abs(s.q[2]) < 0.01 && Math.abs(s.q[0]) < 0.02) api.done("park");
    return rows;
  },

  poly(api, pts, fill, stroke, lw) {
    const c = api.ctx; c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(x, y) : c.moveTo(x, y))); c.closePath();
    if (fill) { c.fillStyle = fill; c.fill(); } if (stroke) { c.strokeStyle = stroke; c.lineWidth = lw || 1.5; c.stroke(); }
  },
  drawCar(api, X, Y, q, dl, dr, col) {
    const P = (u, v) => [X(q[0] + u * Math.cos(q[2]) - v * Math.sin(q[2])), Y(q[1] + u * Math.sin(q[2]) + v * Math.cos(q[2]))];
    const rect = (cx, cy, ang, L, Wd, fill) => this.poly(api, [[-L / 2, -Wd / 2], [L / 2, -Wd / 2], [L / 2, Wd / 2], [-L / 2, Wd / 2]].map(([a, b]) =>
      P(cx + a * Math.cos(ang) - b * Math.sin(ang), cy + a * Math.sin(ang) + b * Math.cos(ang))), fill, api.css("--ink"), 1);
    rect(this.L / 2, 0, 0, 1.8, 1.0, col || "rgba(90,140,200,0.25)");
    rect(0, this.W / 2, 0, 0.32, 0.1, api.css("--ink")); rect(0, -this.W / 2, 0, 0.32, 0.1, api.css("--ink"));
    rect(this.L, this.W / 2, dl, 0.32, 0.1, api.css("--amber")); rect(this.L, -this.W / 2, dr, 0.32, 0.1, api.css("--amber"));
    return P;
  },
  draw(api, s) {
    if (!s.q) return;
    const W = api.w, H = api.h, p = api.p, sc = api.scene;
    if (sc === "trap") {
      const c = this.trapCurve(this.rad(p.lam)), par = this.trapCurve(0);
      api.plot(60, 30, W - 90, H - 80, [{ pts: c, color: api.css("--blue"), name: api.T("当前底角", "current λ") }, { pts: par, color: api.css("--red"), name: api.T("平行转向 λ = 0", "parallel λ = 0") }],
        { xmin: 0, xmax: 40, ymin: -2, ymax: 12, xlabel: api.T("内侧轮转角 δi / °", "inner angle δi / °"), ylabel: api.T("外侧轮误差 / °", "outer error / °") });
      return;
    }
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    const grow = (x, y, r) => { x0 = Math.min(x0, x - r); x1 = Math.max(x1, x + r); y0 = Math.min(y0, y - r); y1 = Math.max(y1, y + r); };
    s.trail.forEach(([x, y]) => grow(x, y, 1.6)); grow(s.q[0], s.q[1], 1.6);
    if (sc === "uturn") { grow(0, p.aisle / 2, 0.2); grow(0, -p.aisle / 2, 0.2); grow(-1.5, 0, 0); grow(3.5, 0, 0); }
    if (sc === "park") { grow(-5.3, -1.6, 0); grow(4.6, 1.0, 0); }
    if (sc === "turn" && Math.abs(p.delta) > 1) { const R = this.L / Math.tan(this.rad(Math.abs(p.delta))) + this.W / 2; if (R < 5) grow(s.q[0] - Math.sign(p.delta) * R * Math.sin(s.q[2]), s.q[1] + Math.sign(p.delta) * R * Math.cos(s.q[2]), 0.3); }
    const k = 0.9 * Math.min(W / Math.max(x1 - x0, 4), H / Math.max(y1 - y0, 2.5)), ox = W / 2 - k * (x0 + x1) / 2, oy = H / 2 + k * (y0 + y1) / 2 + 8;
    const X = (x) => ox + x * k, Y = (y) => oy - y * k;
    api.grid(W, H, k * 0.5);
    for (let i = 1; i < s.trail.length; i++) api.line(X(s.trail[i - 1][0]), Y(s.trail[i - 1][1]), X(s.trail[i][0]), Y(s.trail[i][1]), api.css("--blue"), 2);
    if (sc === "turn") {
      const di = this.rad(p.delta), par = Math.round(p.mode) === 1;
      const dl = di > 0 ? di : (par ? di : this.outerAck(di)), dr = di > 0 ? (par ? di : this.outerAck(di)) : di;
      const P = this.drawCar(api, X, Y, s.q, dl, dr);
      if (Math.abs(di) > 1e-6) {
        const Rr = this.L / Math.tan(Math.abs(di)) + this.W / 2, sg = Math.sign(di), c = [0, sg * Rr];
        const axle = (x, y, b) => { const n = [-Math.sin(b), Math.cos(b)], len = 8; const a = P(x - len * n[0], y - len * n[1]), e = P(x + len * n[0], y + len * n[1]); api.line(a[0], a[1], e[0], e[1], api.css("--red"), 1, [5, 4]); };
        axle(0, 0, 0); axle(this.L, this.W / 2, dl); axle(this.L, -this.W / 2, dr);
        if (!par) { const cc = P(c[0], c[1]); api.circle(cc[0], cc[1], 6, api.css("--amber"), api.css("--ink")); }
      }
      api.label(api.T("红虚线：车轮的轴线；黄点：瞬心；蓝线：后轴中点的轨迹", "red dashed: wheel axles; yellow: ICR; blue: path of the rear-axle centre"), 12, 18, api.css("--muted"), 12);
    } else if (sc === "uturn") {
      [p.aisle / 2, -p.aisle / 2].forEach((y) => { api.line(0, Y(y), W, Y(y), s.hit ? api.css("--red") : api.css("--ink"), 3); });
      const d = this.rad(this.DMAX);
      this.drawCar(api, X, Y, s.q, d, Math.atan(this.L / (this.Rmin() + this.W / 2)), s.hit ? "rgba(214,39,40,0.3)" : null);
      api.label(api.T("黑线：通道的两侧墙；方向打满左转 180°", "black: the aisle walls; full left lock for 180°"), 12, 18, api.css("--muted"), 12);
    } else {
      const plan = this.parkPlan(), db = s.seg < 2 ? plan[Math.min(s.seg, 2)][1] : 0;
      const kerb = -1.45;
      api.line(0, Y(kerb), W, Y(kerb), api.css("--ink"), 3);
      [[-4.3, -0.6], [3.6, -0.6]].forEach(([x, y]) => this.poly(api, [[X(x - 0.9), Y(y - 0.5)], [X(x + 0.9), Y(y - 0.5)], [X(x + 0.9), Y(y + 0.5)], [X(x - 0.9), Y(y + 0.5)]], "rgba(120,120,120,0.35)", api.css("--muted")));
      const dl = db, dr = db;
      this.drawCar(api, X, Y, s.q, dl, dr, "rgba(232,145,58,0.35)");
      api.label(api.T("灰：前后停着的车；黑线：路沿；蓝线：后轴中点的轨迹", "grey: parked cars; black: kerb; blue: rear-axle centre"), 12, 18, api.css("--muted"), 12);
    }
  },
});
