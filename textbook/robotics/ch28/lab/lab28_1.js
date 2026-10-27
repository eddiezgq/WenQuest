// 实验 28.1 过弯：侧滑、侧翻与不足转向（配 28.1 节）。平面问题：车按动力学自行车模型（式 (28.1.8)、(28.1.9)）行驶，
// 轮胎侧向力用刷子模型（Fiala，图 28.1.1a），车速 v_x 保持不变；转向角由一个跟踪弯道的控制器给出：
//   δ = arctan(L/R)（运动学前馈，式 (19.4.4)）− 航向误差 + arctan((1.5e + 0.5∫e)/v_x·2)（e 为离弯道中心线的距离，积分项在转向角
//   到达 ±0.7 rad 的上限时停止累加），使车尽量沿半径 R 的圆走（后轴中点）。
// 侧翻：内侧车轮的法向力 m𝔤/2 − m a_y h/w（式 (28.1.7)）降为零即判为侧翻；侧滑：后轴侧偏角超过刷子模型的饱和角
//   arctan(3μF_zr/C_r) 并持续 0.3 s，或离弯道中心线超过 0.5 m（轿车 3 m），即判为侧滑。
// 场景“牵引式 AGV”：数据与算例 28.1.2 相同（800 kg，L = 1.2 m，w = 0.8 m，l_f = 0.65 m，h 可调，示意值）；
// 生活场景“轿车”：数据与算例 28.1.4 相同（示意值）。
// 由 ex28_1.py 核算：干地面（μ = 0.7）R = 3 m 时式 (28.1.6) 给出 4.22 m/s 侧翻；本页在 4.1～4.2 m/s 之间侧翻（车速升高时实际半径略有变化）。
//   湿地面（μ = 0.4）：式 (28.1.6) 把整车当作一个质点，a_y 最大 μ𝔤 = 3.92 m/s²（3.40 m/s）；本页的自行车模型中前轴只承担 46% 的载荷，
//   转向角又大（约 22°，前轮侧向力的有效部分乘 cos δ），前轴先饱和，约 3.3 m/s 就向外滑，a_y 只到 3.3 m/s² 左右。
//   h = 0.9 m 时 3.59 m/s 侧翻；轿车 100 km/h、R = 200 m 时线性模型的转向角 1.39°（刷子模型稍大），运动学值 0.77°。
WQ.lab({
  title: ["实验 28.1 过弯：侧滑、侧翻与不足转向", "Lab 28.1 Cornering: skid, rollover and understeer"],
  goal: ["让满载的 AGV 和一辆轿车以不同的车速过弯，看车是沿弯道走、向外滑出还是翻倒，读出所需的转向角。",
         "Drive a loaded AGV and a car round a bend at different speeds; see whether they follow the bend, slide out or roll over, and read the steering angle they need."],
  scenes: [
    { id: "agv", robot: true, name: ["牵引式 AGV", "Tow AGV"], hide: [],
      problem: { title: ["机器人问题：满载的 AGV 过弯能开多快", "Robot problem: how fast can the loaded AGV take a bend"],
                 text: ["连车带货 800 kg，货物堆在车厢上。过 3 m 半径的弯，开多快会翻？地面湿了呢？",
                        "Vehicle and load weigh 800 kg, with the load stacked on the deck. How fast can it take a 3 m bend before rolling over? And on a wet floor?"] } },
    { id: "car", name: ["生活：轿车上高速", "Everyday: a car on the motorway"], hide: ["h", "mu", "C"],
      params: { v: { value: 27.8 }, R: { value: 200 } },
      problem: { title: ["生活中的例子：高速转弯为什么要多打方向", "Everyday example: why you steer more in a fast bend"],
                 text: ["同一个弯，车速越高，方向盘要打得越多。看看 100 km/h 过 200 m 的弯要打多少。",
                        "The faster you take the same bend, the more you have to steer. See how much it takes at 100 km/h in a 200 m bend."] } },
  ],
  params: [
    { id: "v", name: ["车速 v", "Speed v"], min: 0.5, max: 45, step: 0.05, value: 2.0, unit: "m/s", digits: 2 },
    { id: "R", name: ["弯道半径 R", "Bend radius R"], min: 2, max: 400, step: 1, value: 3, unit: "m", digits: 0 },
    { id: "h", name: ["质心高度 h", "Height of the centre of mass h"], min: 0.3, max: 1.2, step: 0.01, value: 0.65, unit: "m", digits: 2 },
    { id: "mu", name: ["地面摩擦系数 μ", "Floor friction μ"], min: 0.1, max: 1.0, step: 0.05, value: 0.7, unit: "", digits: 2 },
    { id: "C", name: ["每根轴的侧偏刚度", "Cornering stiffness per axle"], min: 5, max: 60, step: 1, value: 20, unit: "kN/rad", digits: 0 },
  ],
  legend: [{ color: "#888", name: ["弯道中心线", "centre line of the bend"] }, { color: "#1f77b4", name: ["车走过的路线", "path driven"] },
           { color: "#d62728", name: ["地面侧向力", "lateral ground force"] }],
  G: 9.81,
  car(api) {
    if (api.scene === "car") return { m: 1500, L: 2.7, w: 1.55, lf: 1.2, lr: 1.5, Iz: 2500, Cf: 1.0e5, Cr: 1.2e5, h: 0.55, mu: 0.9, len: 4.6, wid: 1.8, tol: 3 };
    const C = api.p.C * 1000;
    return { m: 800, L: 1.2, w: 0.8, lf: 0.65, lr: 0.55, Iz: 800 * (1.8 ** 2 + 1.0 ** 2) / 12, Cf: C, Cr: C, h: api.p.h, mu: api.p.mu, len: 1.8, wid: 1.0, tol: 0.5 };
  },
  fiala(a, C, mu, Fz) {                           // 刷子模型的侧向力（与 _ch28.fiala 相同）
    const t = Math.tan(a), tsl = 3 * mu * Fz / C;
    if (Math.abs(t) >= tsl) return Math.sign(t) * mu * Fz;
    return C * t - C * C * Math.abs(t) * t / (3 * mu * Fz) + C ** 3 * t ** 3 / (27 * mu * mu * Fz * Fz);
  },
  reset(api, s) {
    const P = this.car(api);
    s.v0 = Math.min(api.p.v, api.scene === "car" ? 15 : 1.0);                      // 从较低的车速出发，再慢慢加到 v（避免起步的冲击）
    s.vx = s.v0;
    s.X = 0; s.Y = 0; s.psi = 0; s.vy = P.lr * s.vx / api.p.R; s.w = s.vx / api.p.R;  // 从运动学的稳态出发
    s.t = 0; s.path = [[0, 0]]; s.status = "ok"; s.sat = 0; s.ay = 0; s.af = 0; s.ar = 0; s.delta = Math.atan(P.L / api.p.R); s.inner = P.m * this.G / 2;
    s.dsum = 0; s.dn = 0; s.ayMax = 0; s.fin = false;
  },
  rhs(P, x, delta, vx) {                          // x = (X, Y, ψ, v_y, ω)，参考点为质心
    const [X, Y, psi, vy, w] = x, G = this.G;
    const af = delta - Math.atan2(vy + P.lf * w, vx), ar = -Math.atan2(vy - P.lr * w, vx);
    const Fzf = P.m * G * P.lr / P.L, Fzr = P.m * G * P.lf / P.L;
    const Fyf = this.fiala(af, P.Cf, P.mu, Fzf), Fyr = this.fiala(ar, P.Cr, P.mu, Fzr);
    const vyd = (Fyf * Math.cos(delta) + Fyr) / P.m - vx * w;
    const wd = (P.lf * Fyf * Math.cos(delta) - P.lr * Fyr) / P.Iz;
    const c = Math.cos(psi), sn = Math.sin(psi);
    return { d: [vx * c - vy * sn, vx * sn + vy * c, w, vyd, wd], af, ar, Fyf, Fyr, ay: vyd + vx * w, Fzr };
  },
  update(dt, api, s) {
    if (s.fin) { api.stop(); return; }
    const P = this.car(api), R = api.p.R, h = 0.002, acc = api.scene === "car" ? 2.0 : 0.5;
    const TE = (api.p.v - s.v0) / acc + 5;                                         // 加速到 v 以后再匀速走 5 s
    const n = Math.max(1, Math.round(dt / h));
    for (let k = 0; k < n && !s.fin; k++) {
      // 跟踪弯道：圆心在 (0, R)，后轴中点离圆心的距离与 R 之差为横向误差
      const vx = s.vx = Math.min(api.p.v, s.v0 + acc * s.t);
      const xr = s.X - P.lr * Math.cos(s.psi), yr = s.Y - P.lr * Math.sin(s.psi);
      const e = Math.hypot(xr, yr - R) - R;                                       // 正：在弯道外侧
      const tang = Math.atan2(yr - R, xr) + Math.PI / 2;
      let eh = s.psi - tang; eh = Math.atan2(Math.sin(eh), Math.cos(eh));
      const ei = (s.ei || 0) + e * h;                                              // 积分项：找出稳态所需的转向角
      const raw = Math.atan(P.L / R) - eh + Math.atan((1.5 * e + 0.5 * ei) / vx * 2);
      const delta = Math.max(-0.7, Math.min(0.7, raw));
      if (raw === delta) s.ei = ei;                                                 // 抗饱和：转向角顶到上限时积分项不再累加
      const x = [s.X, s.Y, s.psi, s.vy, s.w];
      const k1 = this.rhs(P, x, delta, vx);
      const xm = x.map((v, i) => v + h / 2 * k1.d[i]);
      const k2 = this.rhs(P, xm, delta, vx);
      [s.X, s.Y, s.psi, s.vy, s.w] = x.map((v, i) => v + h * k2.d[i]);
      s.t += h; s.delta = delta; s.af = k2.af; s.ar = k2.ar; s.ay = k2.ay;
      s.inner = P.m * this.G / 2 - P.m * s.ay * P.h / P.w;
      if (s.t > TE - 2) { s.dsum += delta; s.dn += 1; s.ayMax = Math.max(s.ayMax, s.ay); }
      const asl = Math.atan(3 * P.mu * k2.Fzr / P.Cr);
      s.sat = Math.abs(s.ar) >= asl * 0.999 ? s.sat + h : 0;
      if (s.inner <= 0) { s.status = "tip"; s.fin = true; }
      else if (s.sat > 0.3 || e > P.tol) { s.status = "slide"; s.fin = true; }
      if (Math.round(s.t / h) % 10 === 0) s.path.push([s.X, s.Y]);
      if (s.t >= TE) s.fin = true;
    }
    if (s.fin) {
      const p = api.p, ok = s.status === "ok";
      if (api.scene === "agv" && ok && Math.abs(p.R - 3) < 0.5 && Math.abs(p.h - 0.65) < 0.011 && p.mu >= 0.65 && p.v >= 4.0) api.done("tip");
      if (api.scene === "agv" && s.status === "slide" && p.mu <= 0.45 && Math.abs(p.R - 3) < 0.5) api.done("wet");
      if (api.scene === "agv" && ok && Math.abs(p.R - 3) < 0.5 && Math.abs(p.h - 0.9) < 0.011 && p.mu >= 0.65 && p.v >= 3.4) api.done("high");
      if (api.scene === "car" && ok && Math.abs(p.R - 200) < 1 && p.v >= 27.0 && p.v <= 28.6) api.done("car");
      api.stop();
    }
  },
  draw(api, s) {
    const { w, h } = api, P = this.car(api), R = api.p.R;
    // 俯视：弯道的四分之一圈到半圈
    const span = R * 1.25, sc = Math.min(w * 0.62, h * 0.95) / (2 * span), ox = w * 0.06 + sc * span * 0.1, oy = h * 0.92;
    const X = (x) => ox + x * sc, Y = (y) => oy - y * sc;
    const ctx = api.ctx;
    ctx.strokeStyle = "#888"; ctx.setLineDash([6, 5]); ctx.lineWidth = 1.5; ctx.beginPath();
    for (let a = -Math.PI / 2; a <= Math.PI / 2 + 1e-9; a += 0.02) { const px = R * Math.cos(a), py = R + R * Math.sin(a); if (a === -Math.PI / 2) ctx.moveTo(X(px), Y(py)); else ctx.lineTo(X(px), Y(py)); }
    ctx.stroke(); ctx.setLineDash([]);
    const pth = s.path || [];
    ctx.strokeStyle = "#1f77b4"; ctx.lineWidth = 2.5; ctx.beginPath();
    pth.forEach(([x, y], i) => (i ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y)))); ctx.stroke();
    // 车身
    const c = Math.cos(s.psi || 0), sn = Math.sin(s.psi || 0), L2 = P.len / 2, W2 = P.wid / 2;
    const cx = (s.X || 0) + (P.lf - P.lr) / 2 * c, cy = (s.Y || 0) + (P.lf - P.lr) / 2 * sn;
    const corner = (a, b) => [X(cx + a * c - b * sn), Y(cy + a * sn + b * c)];
    ctx.fillStyle = s.status === "tip" ? "rgba(214,39,40,0.5)" : "rgba(31,119,180,0.35)"; ctx.strokeStyle = "#1f3a5f"; ctx.lineWidth = 1.5;
    ctx.beginPath(); [corner(L2, W2), corner(-L2, W2), corner(-L2, -W2), corner(L2, -W2)].forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
    ctx.closePath(); ctx.fill(); ctx.stroke();
    // 后轴的侧向力（指向圆心为正）
    const km = P.len * 0.8 / (P.m * this.G * 0.5);                                // 箭头长度：每牛多少米
    const rx = (s.X || 0) - P.lr * c, ry = (s.Y || 0) - P.lr * sn, Fyr = P.m * (s.ay || 0) * P.lf / P.L;
    api.arrow(X(rx), Y(ry), X(rx - Fyr * km * sn), Y(ry + Fyr * km * c), "#d62728", 3);
    // 后视小图：内、外侧车轮的法向力
    const bx = w * 0.80, by = h * 0.62, bw = Math.min(w * 0.16, 120), bh = bw * 1.0;
    const tilt = s.status === "tip" ? 0.6 : 0;
    ctx.save(); ctx.translate(bx + bw / 2, by + bh); ctx.rotate(tilt);
    api.rect(-bw, -bh * 1.05, bw, bh * 0.85, "rgba(31,119,180,0.25)", "#1f3a5f", 4);
    api.circle(-bw * 0.85, -bh * 0.1, bh * 0.1, "#555"); api.circle(-bw * 0.15, -bh * 0.1, bh * 0.1, "#555");
    api.circle(-bw / 2, -bh * (0.2 + 0.85 * Math.min(P.h, 1.2) / 1.2), 5, "#b8860b");
    ctx.restore();
    const kN = bh * 0.9 / (P.m * this.G);
    const fin = Math.max(s.inner ?? P.m * this.G / 2, 0), fout = P.m * this.G - fin;
    api.arrow(bx - bw * 0.35, by + bh + 8 + fin * kN, bx - bw * 0.35, by + bh + 8, fin > 1 ? "#2ca02c" : "#d62728", 4);
    api.arrow(bx + bw * 0.35, by + bh + 8 + fout * kN, bx + bw * 0.35, by + bh + 8, "#2ca02c", 4);
    api.label(api.T("后视：内侧 / 外侧的法向力", "rear view: inner / outer normal force"), bx, by - 10, "#555", 12, "center");
    const msg = { ok: api.T("沿弯道行驶", "following the bend"), tip: api.T("侧翻！", "rolled over!"), slide: api.T("侧滑出弯道！", "slid out of the bend!") }[s.status || "ok"];
    api.label(msg, w * 0.80, h * 0.12, s.status === "ok" ? "#2ca02c" : "#d62728", 18, "center");
  },
  readouts(api, s) {
    const f = (v, k = 3) => api.fmt(v, k), P = this.car(api), G = this.G, d = s.dn ? s.dsum / s.dn : s.delta;
    return [
      [["状态", "Status"], { ok: api.T("沿弯道行驶", "following the bend"), tip: api.T("侧翻", "rolled over"), slide: api.T("侧滑", "slid out") }[s.status || "ok"]],
      [["车速", "Speed"], `${f(api.p.v, 2)} m/s（${f(api.p.v * 3.6, 1)} km/h）`],
      [["侧向加速度 a_y", "Lateral acceleration a_y"], f(s.ay, 2) + " m/s²"],
      [["侧翻 / 侧滑的极限", "Rollover / skid limits"], `𝔤w/(2h) = ${f(G * P.w / (2 * P.h), 2)}，μ𝔤 = ${f(P.mu * G, 2)} m/s²`],
      [["内侧车轮的法向力", "Normal force on the inner wheels"], `${f(Math.max(s.inner, 0), 0)} N（${f(Math.max(s.inner, 0) / (P.m * G) * 100, 1)}%）`],
      [["前、后轮侧偏角", "Front and rear slip angles"], `${f(s.af * 180 / Math.PI, 2)}°，${f(s.ar * 180 / Math.PI, 2)}°`],
      [["平均转向角 / 运动学值 arctan(L/R)", "Mean steering angle / kinematic arctan(L/R)"], `${f(d * 180 / Math.PI, 2)}° / ${f(Math.atan(P.L / api.p.R) * 180 / Math.PI, 2)}°`],
    ];
  },
  tasks: [
    { id: "tip", robot: true, text: ["干地面（μ = 0.7）、R = 3 m、质心 0.65 m：找出不翻车的最高车速（不低于 4.0 m/s），与式 (28.1.6) 的 4.22 m/s 比较。",
                                    "Dry floor (μ = 0.7), R = 3 m, CoM at 0.65 m: find the highest speed without rolling over (at least 4.0 m/s) and compare with 4.22 m/s from Eq. (28.1.6)."],
      demo: { scene: "agv", set: { v: 4.1, R: 3, h: 0.65, mu: 0.7, C: 20 }, wait: 4 } },
    { id: "wet", robot: true, text: ["把地面改湿（μ ≤ 0.45），提高车速，看车是先滑还是先翻。", "Make the floor wet (μ ≤ 0.45), raise the speed and see whether the AGV slides or rolls first."],
      demo: { scene: "agv", set: { v: 3.8, R: 3, h: 0.65, mu: 0.4, C: 20 }, wait: 4 } },
    { id: "high", robot: true, text: ["货物堆高，质心升到 0.9 m：在干地面、R = 3 m 的弯道上以不低于 3.4 m/s 的速度不翻车地过弯。",
                                     "Stack the load higher so the CoM is at 0.9 m: take the dry 3 m bend at 3.4 m/s or more without rolling over."],
      demo: { scene: "agv", set: { v: 3.45, R: 3, h: 0.9, mu: 0.7, C: 20 }, wait: 4 } },
    { id: "car", text: ["轿车以约 100 km/h（27～28.6 m/s）过 R = 200 m 的弯，读出平均转向角，与运动学值比较。",
                        "Take the car through a 200 m bend at about 100 km/h (27–28.6 m/s); read the mean steering angle and compare it with the kinematic value."],
      demo: { scene: "car", set: { v: 27.8, R: 200 }, wait: 6 } },
  ],
  think: ["算例 28.1.3 说，AGV 低速过弯时实际的转弯半径与运动学的只差 0.3%，但里程计每过一个 90° 的弯会偏十几厘米。在这个实验里把车速调低、侧偏刚度调小，看后轮的侧偏角怎样变化，并说明里程计的误差从哪里来。",
          "Example 28.1.3 says that at low speed the AGV's turning radius differs from the kinematic one by only 0.3%, yet odometry drifts by over ten centimetres per 90° bend. Lower the speed and the cornering stiffness here, watch the rear slip angle, and explain where the odometry error comes from."],
});
