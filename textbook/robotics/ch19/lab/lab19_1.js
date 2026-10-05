// 实验 19.1 车轮布置与瞬心（配 19.1 节）。
// 四种布置（俯视，{b} 的 x 朝车头、y 朝左）：
//   0 差速：B-EDU-DIFF，两驱动轮 (0, ±0.13) m、β = 0，后部脚轮不计；
//   1 三轮车：在差速的基础上加一个前轮 (0.30, 0) m，固定朝前；
//   2 四轮·阿克曼：轴距 L = 1.2 m、轮距 w = 0.8 m，内侧前轮转 δ，外侧按 cot δo − cot δi = w/L；
//   3 四轮·平行转向：两前轮都转 δ。
// 约束矩阵每行 (x_i cos β_i + y_i sin β_i, −sin β_i, cos β_i)（式 (19.1.8)），秩用高斯消元求；车体允许的运动旋量取为
// “指令 (ω, v, 0) 在 C 的零空间上的投影”（差速、三轮车）或由转向决定（四轮）。没有非零解时车不动，标出必须侧滑的车轮。
// 生活场景：购物车，后轮固定 (0, ±0.25) m，前轮是脚轮（转轴在 (0.64, ±0.25) m，偏距 0.04 m）。推车人在车把
// （后轴后方 0.2 m）处以 0.3 m/s 沿方向 ψ 推，由车把速度 = (v, ω·x_h) 解出 v、ω；脚轮按式 (19.1.7) 甩向运动方向。
WQ.lab({
  title: ["实验 19.1 车轮布置与瞬心", "Lab 19.1 Wheel layouts and the instantaneous centre"],
  goal: ["对几种车轮布置算出约束矩阵的秩、可移动度和瞬心，看车实际能怎样动；体会脚轮为什么不加约束。",
         "For several wheel layouts compute the rank of the constraint matrix, the degree of mobility and the ICR, and see how the vehicle can really move; see why a castor adds no constraint."],
  scenes: [
    { id: "agv", robot: true, name: ["AGV 底盘布置", "AGV chassis layouts"], hide: ["psi"],
      problem: { title: ["机器人问题：这样装车轮，车能怎样动", "Robot problem: with these wheels, how can the chassis move"],
                 text: ["选择车轮布置，给出车速 v、角速度指令 ω（差速、三轮车）或转向角 δ（四轮车），按“开始”行驶 4 s。红色虚线是各标准轮的轴线，黄点是瞬心。",
                        "Pick a layout, give the speed v and a turn-rate command ω (differential, tricycle) or the steering angle δ (four wheels), and press Start to drive 4 s. Red dashed lines are the standard wheels' axles, the yellow dot the ICR."] } },
    { id: "cart", name: ["购物车", "Shopping cart"], hide: ["layout", "om", "delta", "v"],
      problem: { title: ["生活中的例子：横着推购物车", "Everyday example: pushing a shopping cart sideways"],
                 text: ["在车把处沿方向 ψ 推车（ψ = 0 向前，90° 向左）。两个前轮是脚轮，会甩向运动的方向；两个后轮固定，瞬心只能在后轴的延长线上。",
                        "Push the handle in direction ψ (0 forward, 90° to the left). The front castors swing towards the motion; the rear wheels are fixed, so the ICR must lie on the rear axle line."] } },
  ],
  params: [
    { id: "layout", name: ["布置：0 差速 1 三轮车 2 阿克曼 3 平行转向", "layout: 0 diff 1 tricycle 2 Ackermann 3 parallel"], min: 0, max: 3, step: 1, value: 0, digits: 0 },
    { id: "v", name: ["车速 v", "speed v"], min: -0.5, max: 0.5, step: 0.05, value: 0.25, unit: "m/s", digits: 2 },
    { id: "om", name: ["角速度指令 ω（差速、三轮车）", "turn-rate command ω (diff, tricycle)"], min: -2, max: 2, step: 0.1, value: 0.5, unit: "rad/s", digits: 1 },
    { id: "delta", name: ["内侧前轮转角 δ（四轮）", "inner front-wheel angle δ (four wheels)"], min: 0, max: 40, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "psi", name: ["推车方向 ψ", "push direction ψ"], min: -90, max: 90, step: 5, value: 90, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "icr", robot: true, text: ["差速底盘：让瞬心落在车体左侧 0.5 m 处（v/ω = 0.5 m），行驶一次。", "Differential chassis: put the ICR 0.5 m to the left (v/ω = 0.5 m) and drive once."],
      demo: { scene: "agv", set: { layout: 0, v: 0.25, om: 0.5 }, press: ["start"], wait: 4 } },
    { id: "tri", robot: true, text: ["三轮车（前轮固定）：给一个不为零的 ω 行驶，读出约束矩阵的秩，说明车为什么只能直行。", "Tricycle with a fixed front wheel: drive with a non-zero ω; read the rank and explain why it only goes straight."],
      demo: { scene: "agv", set: { layout: 1, v: 0.3, om: 1.0 }, press: ["start"], wait: 4 } },
    { id: "ack", robot: true, text: ["四轮·阿克曼，δ = 30°：行驶一次，读出外侧前轮转角（约 22.6°）和转弯半径（约 2.48 m）。", "Four wheels, Ackermann, δ = 30°: drive once; read the outer angle (about 22.6°) and the radius (about 2.48 m)."],
      demo: { scene: "agv", set: { layout: 2, delta: 30, v: 0.4 }, press: ["start"], wait: 4 } },
    { id: "par", robot: true, text: ["四轮·平行转向，δ = 30°：按“开始”，看秩为 3、车动不了，哪个轮子必须侧滑。", "Four wheels, parallel steering, δ = 30°: press Start; the rank is 3, the car cannot move; which wheel must slide?"],
      demo: { scene: "agv", set: { layout: 3, delta: 30, v: 0.4 }, press: ["start"], wait: 2 } },
    { id: "cart", text: ["横着推购物车（ψ = 90°）：看两个脚轮甩过来，车绕后轴中点转，瞬心在后轴上。", "Push the cart sideways (ψ = 90°): the castors swing round and the cart turns about the rear-axle centre."],
      demo: { scene: "cart", set: { psi: 90 }, press: ["start"], wait: 3 } },
  ],
  think: ["三轮车的前轮若改成脚轮，可移动度变为多少？若改成可转向标准轮呢？分别属于表 19.1.1 的哪一类？",
          "If the tricycle's front wheel becomes a castor, what is the degree of mobility? And if it becomes a steerable standard wheel? Which classes of Table 19.1.1 are these?"],

  // ---------------- 几何与约束
  L: 1.2, W: 0.8, B: 0.26,
  wheels(api) {                        // [[x, y, β, 名称]]
    const p = api.p, lay = Math.round(p.layout), d = p.delta * Math.PI / 180;
    if (lay === 0) return [[0, 0.13, 0, "L"], [0, -0.13, 0, "R"]];
    if (lay === 1) return [[0, 0.13, 0, "L"], [0, -0.13, 0, "R"], [0.3, 0, 0, "F"]];
    const di = d, dout = d > 1e-6 ? Math.atan(1 / (1 / Math.tan(d) + this.W / this.L)) : 0;
    return [[0, this.W / 2, 0, "RL"], [0, -this.W / 2, 0, "RR"], [this.L, this.W / 2, di, "FL"], [this.L, -this.W / 2, lay === 2 ? dout : di, "FR"]];
  },
  rows(ws) { return ws.map(([x, y, b]) => [x * Math.cos(b) + y * Math.sin(b), -Math.sin(b), Math.cos(b)]); },
  rank(A) {                            // 高斯消元，主元阈值 1e-9
    const M = A.map((r) => r.slice()); let rk = 0;
    for (let c = 0; c < 3 && rk < M.length; c++) {
      let piv = rk; for (let i = rk; i < M.length; i++) if (Math.abs(M[i][c]) > Math.abs(M[piv][c])) piv = i;
      if (Math.abs(M[piv][c]) < 1e-9) continue;
      [M[rk], M[piv]] = [M[piv], M[rk]];
      for (let i = 0; i < M.length; i++) if (i !== rk) { const f = M[i][c] / M[rk][c]; for (let j = 0; j < 3; j++) M[i][j] -= f * M[rk][j]; }
      rk++;
    }
    return rk;
  },
  twist(api) {                         // 车体允许的运动旋量 (ω, vx, vy)，null 表示没有非零解
    const p = api.p, lay = Math.round(p.layout);
    if (lay === 0) return [p.om, p.v, 0];
    if (lay === 1) return [0, p.v, 0];                         // 零空间只有 (0, 1, 0)
    const d = p.delta * Math.PI / 180;
    if (lay === 2) { const R = d > 1e-6 ? this.L / Math.tan(d) + this.W / 2 : Infinity; return [isFinite(R) ? p.v / R : 0, p.v, 0]; }
    return d > 1e-6 ? null : [0, p.v, 0];                      // 平行转向：δ ≠ 0 时秩为 3
  },
  // ---------------- 购物车
  cartW: 0.25, xh: -0.2, cast: [[0.64, 0.25], [0.64, -0.25]], dc: 0.04,
  cartTwist(api) { const s = 0.3, ps = api.p.psi * Math.PI / 180; return [s * Math.sin(ps) / this.xh, s * Math.cos(ps), 0]; },

  reset(api, s) {
    s.q = [0, 0, 0]; s.t = 0; s.trail = [[0, 0]]; s.done = false; s.ran = false; s.beta = [0, 0]; s.jam = false; s.beta0 = [0, 0];
  },
  start(api, s) {
    if (api.scene === "agv" && !this.twist(api)) { s.jam = true; s.done = true; s.ran = true; api.stop(); }
  },
  update(dt, api, s) {
    if (s.done) { api.stop(); return; }
    const V = api.scene === "cart" ? this.cartTwist(api) : this.twist(api);
    const Tend = api.scene === "cart" ? 2 : 4, h = Math.min(dt, Tend - s.t);
    const [w, vx, vy] = V, f = s.q[2];
    if (Math.abs(w) < 1e-9) { s.q[0] += h * (vx * Math.cos(f) - vy * Math.sin(f)); s.q[1] += h * (vx * Math.sin(f) + vy * Math.cos(f)); }
    else {                                                     // 式 (19.2.6)：一步内运动旋量不变
      const c = Math.cos(w * h), sn = Math.sin(w * h), ax = (sn * vx - (1 - c) * vy) / w, ay = ((1 - c) * vx + sn * vy) / w;
      s.q[0] += Math.cos(f) * ax - Math.sin(f) * ay; s.q[1] += Math.sin(f) * ax + Math.cos(f) * ay;
    }
    s.q[2] += w * h;
    if (api.scene === "cart") {                                // 脚轮：β̇ = n·v_A/d − ω（式 (19.1.7)）
      this.cast.forEach(([xa, ya], i) => {
        const b = s.beta[i], vA = [vx - w * ya, vy + w * xa], n = [-Math.sin(b), Math.cos(b)];
        s.beta[i] += h * ((n[0] * vA[0] + n[1] * vA[1]) / this.dc - w);
      });
    }
    s.t += h; s.trail.push([s.q[0], s.q[1]]);
    if (s.t >= Tend - 1e-9) { s.done = true; s.ran = true; api.stop(); }
  },
  readouts(api, s) {
    if (!s.q) return [];
    const f = api.fmt, rows = [];
    if (api.scene === "cart") {
      const [w, vx] = this.cartTwist(api);
      const icr = Math.abs(w) > 1e-9 ? vx / w : Infinity;
      const turned = s.beta.map((b) => Math.abs(b) * 180 / Math.PI);
      rows.push([["约束矩阵的秩", "rank of C"], "1"], [["可移动度 δm", "mobility δm"], "2"],
                [["车把处的推力方向 ψ", "push direction ψ"], f(api.p.psi, 0) + "°"],
                [["车体 (ω, v_x, v_y)", "body (ω, v_x, v_y)"], `(${f(w, 2)}, ${f(vx, 2)}, 0)`],
                [["瞬心（后轴线上，距后轴中点）", "ICR (on rear axle, from centre)"], isFinite(icr) ? f(icr, 2) + " m" : api.T("无穷远（直行）", "at infinity (straight)")],
                [["两个脚轮转过的角度", "castor swing angles"], turned.map((x) => f(x, 0) + "°").join(", ")]);
      if (s.ran && Math.abs(api.p.psi - 90) < 1e-6 && Math.min(...turned) > 60 && Math.abs(icr) < 1e-6) api.done("cart");
      return rows;
    }
    const ws = this.wheels(api), C = this.rows(ws), rk = this.rank(C), lay = Math.round(api.p.layout), V = this.twist(api);
    const names = [api.T("差速", "differential"), api.T("三轮车（前轮固定）", "tricycle, fixed front wheel"), api.T("四轮·阿克曼", "four wheels, Ackermann"), api.T("四轮·平行转向", "four wheels, parallel")];
    rows.push([["布置", "layout"], names[lay]], [["约束矩阵的秩", "rank of C"], String(rk)], [["可移动度 δm = 3 − rank C", "mobility δm = 3 − rank C"], String(3 - rk)]);
    if (lay >= 2) rows.push([["两前轮转角 δi, δo", "front angles δi, δo"], ws.slice(2).map((w) => f(w[2] * 180 / Math.PI, 1) + "°").join(", ")]);
    if (!V) {
      rows.push([["结果", "result"], api.T("没有不侧滑的运动：至少一个前轮必须侧滑（右前轮的轴线不过后轴与左前轮轴线的交点）", "no motion without sliding: a front wheel must slide (the right front axle misses the point where the others meet)")]);
      if (lay === 3 && api.p.delta >= 5 && s.jam) api.done("par");
      return rows;
    }
    const R = Math.abs(V[0]) > 1e-9 ? V[1] / V[0] : Infinity;
    rows.push([["车体 (ω, v_x, v_y)", "body (ω, v_x, v_y)"], `(${f(V[0], 3)}, ${f(V[1], 2)}, 0)`],
              [["瞬心 (0, R)，R = v/ω", "ICR (0, R), R = v/ω"], isFinite(R) ? f(R, 3) + " m" : api.T("无穷远（直行）", "at infinity (straight)")]);
    if (lay === 1 && Math.abs(api.p.om) > 0.05) rows.push([["注意", "note"], api.T("ω 的指令被约束吃掉了：零空间只有 (0, 1, 0)", "the ω command is lost: the null space is only (0, 1, 0)")]);
    if (s.ran) {
      if (lay === 0 && Math.abs(R - 0.5) < 0.02) api.done("icr");
      if (lay === 1 && Math.abs(api.p.om) > 0.05 && Math.abs(s.q[2]) < 1e-9 && Math.abs(api.p.v) > 0.05) api.done("tri");
      if (lay === 2 && Math.abs(api.p.delta - 30) < 0.5 && Math.abs(api.p.v) > 0.05) api.done("ack");
    }
    return rows;
  },

  // ---------------- 画图
  poly(api, pts, fill, stroke) {
    const c = api.ctx; c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(x, y) : c.moveTo(x, y))); c.closePath();
    if (fill) { c.fillStyle = fill; c.fill(); } if (stroke) { c.strokeStyle = stroke; c.lineWidth = 1.5; c.stroke(); }
  },
  box(api, X, Y, q, cx, cy, ang, L, W, fill, stroke) {          // 车体坐标中的矩形，画在位姿 q 处
    const [x, y, f] = q, pts = [[-L / 2, -W / 2], [L / 2, -W / 2], [L / 2, W / 2], [-L / 2, W / 2]].map(([a, b]) => {
      const u = cx + a * Math.cos(ang) - b * Math.sin(ang), v = cy + a * Math.sin(ang) + b * Math.cos(ang);
      return [X(x + u * Math.cos(f) - v * Math.sin(f)), Y(y + u * Math.sin(f) + v * Math.cos(f))];
    });
    this.poly(api, pts, fill, stroke);
  },
  draw(api, s) {
    if (!s.q) return;
    const W = api.w, H = api.h, cart = api.scene === "cart", lay = Math.round(api.p.layout);
    const big = !cart && lay >= 2, ext = big ? 1.6 : cart ? 0.75 : 0.3;
    // 取景：包住轨迹、车体和（不太远的）瞬心
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    const grow = (x, y, r) => { x0 = Math.min(x0, x - r); x1 = Math.max(x1, x + r); y0 = Math.min(y0, y - r); y1 = Math.max(y1, y + r); };
    s.trail.forEach(([x, y]) => grow(x, y, ext));
    grow(s.q[0], s.q[1], ext); grow(0, 0, ext);
    const Vd = cart ? this.cartTwist(api) : this.twist(api);
    if (Vd && Math.abs(Vd[0]) > 1e-9) {
      const R = Vd[1] / Vd[0];
      if (Math.abs(R) < (big ? 4 : 0.9)) grow(s.q[0] - R * Math.sin(s.q[2]), s.q[1] + R * Math.cos(s.q[2]), 0.1);
    }
    const sx = Math.max(x1 - x0, big ? 4 : 1.0), sy = Math.max(y1 - y0, big ? 2.5 : 0.6);
    const k = 0.9 * Math.min(W / sx, H / sy), ox = W / 2 - k * (x0 + x1) / 2, oy = H / 2 + k * (y0 + y1) / 2 + 8;
    const X = (x) => ox + x * k, Y = (y) => oy - y * k, q = s.q, f = q[2];
    const toW = (u, v) => [q[0] + u * Math.cos(f) - v * Math.sin(f), q[1] + u * Math.sin(f) + v * Math.cos(f)];
    api.grid(W, H, big ? k * 0.5 : k * 0.1 > 12 ? k * 0.1 : k * 0.5);
    for (let i = 1; i < s.trail.length; i++) api.line(X(s.trail[i - 1][0]), Y(s.trail[i - 1][1]), X(s.trail[i][0]), Y(s.trail[i][1]), api.css("--blue"), 2);
    if (cart) {
      this.box(api, X, Y, q, 0.32, 0, 0, 0.8, 0.56, "rgba(160,170,150,0.35)", api.css("--ink"));
      [[0, 0.25], [0, -0.25]].forEach(([u, v]) => this.box(api, X, Y, q, u, v, 0, 0.1, 0.03, api.css("--ink")));
      this.cast.forEach(([u, v], i) => {
        const b = s.beta[i], cu = u - this.dc * Math.cos(b), cv = v - this.dc * Math.sin(b);
        this.box(api, X, Y, q, cu, cv, b, 0.08, 0.025, api.css("--muted"));
        const a = toW(u, v); api.circle(X(a[0]), Y(a[1]), 3, api.css("--amber"));
      });
      const hd = toW(this.xh, 0); api.circle(X(hd[0]), Y(hd[1]), 5, api.css("--violet"));
      const ps = api.p.psi * Math.PI / 180, dir = [Math.cos(f + ps), Math.sin(f + ps)];
      api.arrow(X(hd[0]), Y(hd[1]), X(hd[0] + 0.25 * dir[0]), Y(hd[1] + 0.25 * dir[1]), api.css("--violet"), 2.5);
      const a0 = toW(0, -0.9), a1 = toW(0, 0.9);
      api.line(X(a0[0]), Y(a0[1]), X(a1[0]), Y(a1[1]), api.css("--red"), 1, [5, 4]);
      const [w, vx] = this.cartTwist(api);
      if (Math.abs(w) > 1e-9 && Math.abs(vx / w) < 0.9) { const c = toW(0, vx / w); api.circle(X(c[0]), Y(c[1]), 6, api.css("--amber"), api.css("--ink")); }
      api.label(api.T("紫：车把与推力方向；橙点：脚轮转轴；红虚线：后轴线；黄点：瞬心", "violet: handle and push; amber dots: castor pivots; red dashed: rear axle line; yellow: ICR"), 12, 18, api.css("--muted"), 12);
      return;
    }
    const ws = this.wheels(api), V = this.twist(api);
    if (lay === 0 || lay === 1) this.box(api, X, Y, q, -0.02, 0, 0, 0.32, 0.22, "rgba(90,140,200,0.25)", api.css("--ink"));
    else this.box(api, X, Y, q, 0.6, 0, 0, 1.8, 1.0, "rgba(90,140,200,0.25)", api.css("--ink"));
    if (lay <= 1) { const c = toW(-0.14, 0); api.circle(X(c[0]), Y(c[1]), 0.02 * k, api.css("--muted")); }
    const wr = big ? 0.16 : 0.05, wt = big ? 0.09 : 0.03, Lx = big ? 4 : 0.7;
    ws.forEach(([x, y, b], i) => {
      const slip = !V && lay === 3 && i === 3;
      this.box(api, X, Y, q, x, y, b, 2 * wr, wt, slip ? api.css("--red") : api.css("--ink"));
      const n = [-Math.sin(b), Math.cos(b)], p0 = toW(x - Lx * n[0], y - Lx * n[1]), p1 = toW(x + Lx * n[0], y + Lx * n[1]);
      api.line(X(p0[0]), Y(p0[1]), X(p1[0]), Y(p1[1]), api.css("--red"), 1, [5, 4]);
    });
    if (V && Math.abs(V[0]) > 1e-9) {
      const R = V[1] / V[0];
      if (Math.abs(R) < (big ? 4 : 0.9)) { const c = toW(0, R); api.circle(X(c[0]), Y(c[1]), 6, api.css("--amber"), api.css("--ink")); }
    }
    if (!V) api.label(api.T("动不了：三条轴线不交于一点，红色车轮必须侧滑", "stuck: the axles do not meet; the red wheel must slide"), 12, 40, api.css("--red"), 14);
    api.label(api.T("红虚线：标准轮的轴线；黄点：瞬心；蓝线：车体参考点的轨迹", "red dashed: standard-wheel axles; yellow: ICR; blue: path of the reference point"), 12, 18, api.css("--muted"), 12);
  },
});
