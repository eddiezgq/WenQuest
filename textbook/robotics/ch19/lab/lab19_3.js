// 实验 19.3 全向底盘（配 19.3 节）。
// 四轮麦克纳姆 AGV（算例 19.3.1）：r = 0.075 m，l = 0.25 m，w = 0.20 m，轮速上限 20 rad/s；行 FL、FR、RL、RR，
//   θ̇ = H V_b，H = (1/r)[[−k, 1, −1], [k, 1, 1], [−k, 1, 1], [k, 1, −1]]，k = l + w（式 (19.3.5)），列 ω、v_x、v_y。
// 装错的车：四个轮子的辊子同向（γ 都为 +45°），H 的 v_x、v_y 两列相同，秩为 2（算例 19.3.3）。
// 三轮全向底盘（算例 19.3.5）：r = 0.03 m，R_o = 0.12 m，方位角 90°、210°、330°，θ̇_i = (R_o ω − sin α_i v_x + cos α_i v_y)/r。
// 车体按给定的物体运动旋量行驶 3 s，位姿按 SE(2) 的指数精确更新（式 (19.2.6)）。
// 生活场景：平板推车，四角各一个万向脚轮（偏距 0.05 m），沿车身方向 ψ 平推 0.3 m/s，脚轮按式 (19.1.7) 甩向运动方向。
WQ.lab({
  title: ["实验 19.3 全向底盘", "Lab 19.3 Omnidirectional chassis"],
  goal: ["给定车体的运动，求麦克纳姆底盘和三轮全向底盘各轮的转速；看斜行、侧移、原地转时各轮怎样配合，以及辊子装错时哪个方向失去控制。",
         "For a given body motion find the wheel speeds of a mecanum chassis and a three-wheel omni chassis; see how the wheels cooperate for diagonal, sideways and spinning motion, and which direction is lost when the rollers are fitted wrongly."],
  scenes: [
    { id: "mec", robot: true, name: ["麦克纳姆 AGV", "Mecanum AGV"], hide: ["psi"],
      problem: { title: ["机器人问题：要横着走，四个轮子各转多快", "Robot problem: to move sideways, how fast does each wheel turn"],
                 text: ["给定车体的 v_x、v_y、ω，界面按式 (19.3.5) 算出四个轮速（红色向前、蓝色向后），按“开始”让车行驶 3 s。",
                        "Give the body's v_x, v_y, ω; the four wheel speeds follow from Eq. (19.3.5) (red forward, blue backward). Press Start to drive 3 s."] } },
    { id: "bad", robot: true, name: ["装错辊子的车", "Rollers fitted wrongly"], hide: ["psi"],
      problem: { title: ["机器人问题：四个轮子装成了同一种", "Robot problem: all four wheels of the same hand"],
                 text: ["四个轮子的辊子都朝同一方向（γ = +45°）。找一个方向：车沿它运动时四个轮子都不必转，也就是说这个方向不受电机控制。",
                        "All four rollers point the same way (γ = +45°). Find a direction in which the body moves while no wheel turns: that direction is not controlled by the motors."] } },
    { id: "omni", robot: true, name: ["三轮全向底盘", "Three-wheel omni base"], hide: ["psi"],
      problem: { title: ["机器人问题：三个全向轮怎样配合", "Robot problem: how do three omni wheels cooperate"],
                 text: ["三个全向轮相隔 120°，H 是可逆的方阵。给定车体运动，读出三个轮速；或者反过来，找出使车向后平移的车体运动。",
                        "Three omni wheels 120° apart; H is an invertible square matrix. Give a body motion and read the three wheel speeds."] } },
    { id: "cart", name: ["平板推车", "Flat trolley"], hide: ["vx", "vy", "om"],
      problem: { title: ["生活中的例子：四个万向脚轮的推车", "Everyday example: a trolley on four castors"],
                 text: ["沿方向 ψ 平推推车（ψ = 0 向前，90° 向左）。脚轮不加约束，推车可以朝任何方向走；但每个脚轮要先甩到运动方向，才开始滚动。",
                        "Push the trolley in direction ψ (0 forward, 90° left). Castors add no constraint, so it can go any way; but each castor first swings round to the direction of motion."] } },
  ],
  params: [
    { id: "vx", name: ["车体 v_x（向前）", "body v_x (forward)"], min: -0.6, max: 0.6, step: 0.05, value: 0, unit: "m/s", digits: 2 },
    { id: "vy", name: ["车体 v_y（向左）", "body v_y (left)"], min: -0.6, max: 0.6, step: 0.05, value: 0.3, unit: "m/s", digits: 2 },
    { id: "om", name: ["车体 ω（逆时针）", "body ω (anticlockwise)"], min: -2, max: 2, step: 0.1, value: 0, unit: "rad/s", digits: 1 },
    { id: "psi", name: ["推车方向 ψ", "push direction ψ"], min: -90, max: 90, step: 5, value: 90, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "side", robot: true, text: ["让麦克纳姆 AGV 以 0.3 m/s 向左侧移，读出四个轮速（约 −4、4、4、−4 rad/s）。", "Move the mecanum AGV 0.3 m/s to the left; read the four wheel speeds (about −4, 4, 4, −4 rad/s)."],
      demo: { scene: "mec", set: { vx: 0, vy: 0.3, om: 0 }, press: ["start"], wait: 4 } },
    { id: "diag", robot: true, text: ["找一个只有两个轮子转动的斜行方向，行驶一次。", "Find a diagonal direction in which only two wheels turn, and drive it once."],
      demo: { scene: "mec", set: { vx: 0.3, vy: 0.3, om: 0 }, press: ["start"], wait: 4 } },
    { id: "spin", robot: true, text: ["让麦克纳姆 AGV 原地逆时针转 1 rad/s，读出轮速（约 ±6 rad/s）。", "Spin the mecanum AGV at 1 rad/s anticlockwise; read the wheel speeds (about ±6 rad/s)."],
      demo: { scene: "mec", set: { vx: 0, vy: 0, om: 1 }, press: ["start"], wait: 4 } },
    { id: "bad", robot: true, text: ["装错的车：找出四个轮子都不转、车却在动的方向（v_x = −v_y）。", "Wrong rollers: find the direction where the body moves but no wheel turns (v_x = −v_y)."],
      demo: { scene: "bad", set: { vx: 0.3, vy: -0.3, om: 0 }, press: ["start"], wait: 4 } },
    { id: "omni", robot: true, text: ["三轮底盘以 0.3 m/s 向后平移，读出三个轮速（约 10、−5、−5 rad/s）。", "Move the three-wheel base backwards at 0.3 m/s; read the wheel speeds (about 10, −5, −5 rad/s)."],
      demo: { scene: "omni", set: { vx: -0.3, vy: 0, om: 0 }, press: ["start"], wait: 4 } },
    { id: "cart", text: ["横着推平板推车（ψ = 90°），看四个脚轮甩过 90° 后推车平移。", "Push the trolley sideways (ψ = 90°): the four castors swing through 90°, then it slides across."],
      demo: { scene: "cart", set: { psi: 90 }, press: ["start"], wait: 4 } },
  ],
  think: ["四轮麦克纳姆底盘比三轮全向底盘多一个轮子，多出来的是什么？用相容条件 (19.3.6) 说明它的好处和麻烦。",
          "The mecanum base has one wheel more than the three-wheel base. What does the extra wheel bring? Use the compatibility condition (19.3.6) to explain its benefit and its trouble."],

  r: 0.075, l: 0.25, w: 0.2, wmax: 20, r3: 0.03, R3: 0.12, dc: 0.05,
  CAST: [[0.4, 0.25], [0.4, -0.25], [-0.4, 0.25], [-0.4, -0.25]],
  H(api) {                                    // 当前场景的 H（行：各轮），列 (ω, v_x, v_y)
    const r = this.r, k = this.l + this.w;
    if (api.scene === "omni") return [90, 210, 330].map((a) => { const t = a * Math.PI / 180; return [this.R3 / this.r3, -Math.sin(t) / this.r3, Math.cos(t) / this.r3]; });
    if (api.scene === "bad") {                // γ 都为 +45°：θ̇ = (v_x − ω y + v_y + ω x)/r
      return [[this.l, this.w], [this.l, -this.w], [-this.l, this.w], [-this.l, -this.w]].map(([x, y]) => [(x - y) / r, 1 / r, 1 / r]);
    }
    return [[-k / r, 1 / r, -1 / r], [k / r, 1 / r, 1 / r], [-k / r, 1 / r, 1 / r], [k / r, 1 / r, -1 / r]];
  },
  V(api) {
    if (api.scene === "cart") { const ps = api.p.psi * Math.PI / 180; return [0, 0.3 * Math.cos(ps), 0.3 * Math.sin(ps)]; }
    return [api.p.om, api.p.vx, api.p.vy];
  },
  speeds(api) { const H = this.H(api), V = this.V(api); return H.map((h) => h[0] * V[0] + h[1] * V[1] + h[2] * V[2]); },

  reset(api, s) { s.q = [0, 0, 0]; s.t = 0; s.trail = [[0, 0]]; s.ran = false; s.beta = [0, 0, 0, 0]; s.th = [0, 0, 0, 0]; },
  start(api, s) { s.go = true; },
  update(dt, api, s) {
    if (!s.q || s.ran) { api.stop(); return; }
    const Tend = 3, h = Math.min(dt, Tend - s.t), [w, vx, vy] = this.V(api), f = s.q[2];
    if (Math.abs(w) < 1e-9) { s.q[0] += h * (vx * Math.cos(f) - vy * Math.sin(f)); s.q[1] += h * (vx * Math.sin(f) + vy * Math.cos(f)); }
    else {
      const c = Math.cos(w * h), sn = Math.sin(w * h), ax = (sn * vx - (1 - c) * vy) / w, ay = ((1 - c) * vx + sn * vy) / w;
      s.q[0] += Math.cos(f) * ax - Math.sin(f) * ay; s.q[1] += Math.sin(f) * ax + Math.cos(f) * ay;
    }
    s.q[2] += w * h;
    const th = this.speeds(api);
    th.forEach((x, i) => { s.th[i] += x * h; });
    if (api.scene === "cart") {
      this.CAST.forEach(([xa, ya], i) => {
        const b = s.beta[i], vA = [vx - w * ya, vy + w * xa], n = [-Math.sin(b), Math.cos(b)];
        s.beta[i] += h * ((n[0] * vA[0] + n[1] * vA[1]) / this.dc - w);
      });
    }
    s.t += h; s.trail.push([s.q[0], s.q[1]]);
    if (s.t >= Tend - 1e-9) { s.ran = true; api.stop(); }
  },
  readouts(api, s) {
    if (!s.q) return [];
    const f = api.fmt, th = this.speeds(api), p = api.p, rows = [];
    if (api.scene === "cart") {
      const sw = s.beta.map((b) => Math.abs(b) * 180 / Math.PI);
      rows.push([["推车速度（车身坐标）", "trolley velocity (body frame)"], `(${f(0.3 * Math.cos(p.psi * Math.PI / 180), 2)}, ${f(0.3 * Math.sin(p.psi * Math.PI / 180), 2)}) m/s`],
                [["四个脚轮转过的角度", "castor swing angles"], sw.map((x) => f(x, 0) + "°").join(", ")],
                [["约束矩阵的秩", "rank of C"], api.T("0（脚轮不列入）", "0 (castors do not count)")]);
      if (s.ran && Math.abs(p.psi - 90) < 1e-6 && Math.min(...sw) > 80) api.done("cart");
      return rows;
    }
    const names = api.scene === "omni" ? ["1", "2", "3"] : ["FL", "FR", "RL", "RR"];
    const mx = Math.max(...th.map(Math.abs));
    rows.push([["轮速 " + names.join("、"), "wheel speeds " + names.join(", ")], th.map((x) => f(x, 2)).join(", ") + " rad/s"],
              [["最大轮速 / 上限", "largest / limit"], `${f(mx, 2)} / ${this.wmax} rad/s` + (mx > this.wmax ? api.T("（超限）", " (over)") : "")]);
    if (api.scene !== "omni") rows.push([["相容条件 θ̇FL + θ̇FR − θ̇RL − θ̇RR", "compatibility θ̇FL + θ̇FR − θ̇RL − θ̇RR"], f(th[0] + th[1] - th[2] - th[3], 3) + " rad/s"]);
    if (api.scene === "bad") rows.push([["H 的秩", "rank of H"], "2"], [["不受控的方向", "uncontrolled direction"], api.T("(v_x, v_y) ∝ (1, −1)：四个轮子都不必转", "(v_x, v_y) ∝ (1, −1): no wheel needs to turn")]);
    if (!s.ran) return rows;
    const near = (a, b) => Math.abs(a - b) < 1e-6;
    if (api.scene === "mec") {
      if (near(p.vx, 0) && near(p.vy, 0.3) && near(p.om, 0)) api.done("side");
      const zeros = th.filter((x) => Math.abs(x) < 1e-9).length;
      if (zeros === 2 && Math.abs(p.om) < 1e-9 && Math.hypot(p.vx, p.vy) > 0.05) api.done("diag");
      if (near(p.vx, 0) && near(p.vy, 0) && near(p.om, 1)) api.done("spin");
    }
    if (api.scene === "bad" && mx < 1e-9 && Math.hypot(p.vx, p.vy) > 0.05) api.done("bad");
    if (api.scene === "omni" && near(p.vx, -0.3) && near(p.vy, 0) && near(p.om, 0)) api.done("omni");
    return rows;
  },

  poly(api, pts, fill, stroke) {
    const c = api.ctx; c.beginPath(); pts.forEach(([x, y], i) => (i ? c.lineTo(x, y) : c.moveTo(x, y))); c.closePath();
    if (fill) { c.fillStyle = fill; c.fill(); } if (stroke) { c.strokeStyle = stroke; c.lineWidth = 1.5; c.stroke(); }
  },
  draw(api, s) {
    if (!s.q) return;
    const W = api.w, H = api.h, sc = api.scene, small = sc === "omni";
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    const ext = small ? 0.25 : sc === "cart" ? 0.6 : 0.45;
    s.trail.forEach(([x, y]) => { x0 = Math.min(x0, x - ext); x1 = Math.max(x1, x + ext); y0 = Math.min(y0, y - ext); y1 = Math.max(y1, y + ext); });
    const sx = Math.max(x1 - x0, small ? 1.0 : 2.2), sy = Math.max(y1 - y0, small ? 0.6 : 1.3);
    const k = 0.9 * Math.min(W / sx, H / sy), ox = W / 2 - k * (x0 + x1) / 2, oy = H / 2 + k * (y0 + y1) / 2 + 8;
    const q = s.q, f = q[2], X = (x) => ox + x * k, Y = (y) => oy - y * k;
    const P = (u, v) => [X(q[0] + u * Math.cos(f) - v * Math.sin(f)), Y(q[1] + u * Math.sin(f) + v * Math.cos(f))];
    const rect = (cx, cy, ang, L, Wd, fill, stroke) => this.poly(api, [[-L / 2, -Wd / 2], [L / 2, -Wd / 2], [L / 2, Wd / 2], [-L / 2, Wd / 2]].map(([a, b]) =>
      P(cx + a * Math.cos(ang) - b * Math.sin(ang), cy + a * Math.sin(ang) + b * Math.cos(ang))), fill, stroke);
    api.grid(W, H, k * 0.1 > 12 ? k * 0.1 : k * 0.5);
    for (let i = 1; i < s.trail.length; i++) api.line(X(s.trail[i - 1][0]), Y(s.trail[i - 1][1]), X(s.trail[i][0]), Y(s.trail[i][1]), api.css("--blue"), 2);
    const th = this.speeds(api);
    if (sc === "mec" || sc === "bad") {
      rect(0, 0, 0, 2 * this.l + 0.12, 2 * this.w + 0.02, "rgba(90,140,200,0.25)", api.css("--ink"));
      const gam = sc === "bad" ? [1, 1, 1, 1] : [-1, 1, 1, -1];
      [[this.l, this.w], [this.l, -this.w], [-this.l, this.w], [-this.l, -this.w]].forEach(([x, y], i) => {
        const yy = y + (y > 0 ? 0.03 : -0.03);
        rect(x, yy, 0, 2 * this.r, 0.05, api.css("--ink"));
        for (let j = -1; j <= 1; j++) { const a = P(x + j * 0.04 - 0.015, yy - gam[i] * 0.015), b = P(x + j * 0.04 + 0.015, yy + gam[i] * 0.015); api.line(a[0], a[1], b[0], b[1], "#f0f0f0", 2); }
        const t = th[i], yl = y + (y > 0 ? 0.12 : -0.12), a = P(x, yl), b = P(x + 0.012 * t, yl);
        if (Math.abs(t) > 1e-6) api.arrow(a[0], a[1], b[0], b[1], t > 0 ? api.css("--red") : api.css("--blue"), 2.5);
        api.label(api.fmt(t, 1), a[0], a[1] + (y > 0 ? -14 : 14), t > 0 ? api.css("--red") : api.css("--blue"), 12, "center");
      });
    } else if (sc === "omni") {
      const c = P(0, 0); api.circle(c[0], c[1], 0.16 * k, "rgba(90,140,200,0.25)", api.css("--ink"));
      [90, 210, 330].forEach((a, i) => {
        const t = a * Math.PI / 180, x = this.R3 * Math.cos(t), y = this.R3 * Math.sin(t), b = t + Math.PI / 2;
        rect(x, y, b, 2 * this.r3, 0.018, api.css("--ink"));
        const o = P(x + 0.05 * Math.cos(t), y + 0.05 * Math.sin(t)), e = P(x + 0.05 * Math.cos(t) + 0.004 * th[i] * Math.cos(b), y + 0.05 * Math.sin(t) + 0.004 * th[i] * Math.sin(b));
        if (Math.abs(th[i]) > 1e-6) api.arrow(o[0], o[1], e[0], e[1], th[i] > 0 ? api.css("--red") : api.css("--blue"), 2.5);
        const lb = P(x + 0.09 * Math.cos(t), y + 0.09 * Math.sin(t));
        api.label(`${i + 1}: ${api.fmt(th[i], 1)}`, lb[0], lb[1], api.css("--ink"), 12, "center");
      });
      const n = P(0.1, 0); api.circle(n[0], n[1], 4, api.css("--amber"));
    } else {
      rect(0, 0, 0, 1.0, 0.62, "rgba(200,170,100,0.3)", api.css("--ink"));
      this.CAST.forEach(([x, y], i) => {
        const b = s.beta[i], cx = x - this.dc * Math.cos(b), cy = y - this.dc * Math.sin(b);
        rect(cx, cy, b, 0.08, 0.025, api.css("--muted"));
        const a = P(x, y); api.circle(a[0], a[1], 3, api.css("--amber"));
      });
      const ps = api.p.psi * Math.PI / 180, c = P(0, 0), e = P(0.3 * Math.cos(ps), 0.3 * Math.sin(ps));
      api.arrow(c[0], c[1], e[0], e[1], api.css("--violet"), 3);
    }
    const legend = sc === "cart" ? api.T("紫：推动方向；橙点：脚轮转轴；蓝线：轨迹", "violet: push; amber: castor pivots; blue: path")
      : api.T("红箭头向前、蓝箭头向后：车轮转速 rad/s；白线：接地辊子的轴线；蓝线：车体中心的轨迹", "red forward, blue backward: wheel speeds in rad/s; white: floor-roller axes; blue: path of the centre");
    api.label(legend, 12, 18, api.css("--muted"), 12);
  },
});
