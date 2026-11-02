// 实验 21.4 相平面绘图台：单摆与倒立摆（配 21.2、21.4、21.5 节）。“机器人”场景：自平衡机器人简化为绕支点转动的倒立摆
// （m = 5 kg，质心高 0.4 m，I = mh²），支点转矩 τ = −K_p θ − K_d θ′，限幅 15 N·m；相平面上的向量场、轨线与线性化特征值。
// “系统”场景：有阻尼单摆（l = 0.5 m）、捕食者–猎物方程、范德波尔振子的相图，点击选初值。
WQ.lab({
  title: ["实验 21.4 相平面绘图台：单摆与倒立摆", "Lab 21.4 Phase-plane workbench: pendulum and inverted pendulum"],
  goal: ["在相平面上看非线性系统的全部运动：平衡点、分界线、极限环；用线性化判断平衡点的稳定性，再看转矩限幅下线性化保证不了的“吸引域”有多大。",
         "See all the motions of a nonlinear system in the phase plane—equilibria, separatrices, limit cycles; judge stability by linearization, then see how large the basin of attraction is when torque is limited, which linearization cannot tell."],
  scenes: [
    { id: "bal", robot: true, name: ["自平衡机器人", "Balancing robot"], hide: ["sys", "x0", "y0", "p"],
      problem: { title: ["机器人问题：控制增益多大才能扶住它？倾斜多少就救不回来了？", "Robot problem: how much gain holds it up, and how far can it tilt before it cannot be saved?"],
                 text: ["把自平衡机器人看作绕车轮轴转动的倒立摆：I θ̈ = m g h sin θ + τ，m = 5 kg，h = 0.4 m，I = m h² = 0.8 kg·m²。控制器 τ = −K_p θ − K_d θ̇，电机转矩不超过 15 N·m。相平面横轴是倾角，纵轴是倾角速度。",
                        "Treat the balancing robot as an inverted pendulum about the wheel axle: I θ̈ = m g h sin θ + τ with m = 5 kg, h = 0.4 m, I = m h² = 0.8 kg·m². The controller is τ = −K_p θ − K_d θ̇, limited to 15 N·m. The phase plane shows tilt against tilt rate."] } },
    { id: "sys", name: ["系统的相图", "Phase portraits"], hide: ["Kp", "Kd", "th0", "w0"],
      problem: { title: ["非线性系统特有的现象", "Phenomena only nonlinear systems show"],
                 text: ["选一个系统，在图上点击或用滑块选初值，画出轨线：单摆的分界线、捕食者–猎物的闭轨、范德波尔振子的极限环。",
                        "Pick a system and choose an initial point by clicking or with the sliders: the pendulum's separatrix, predator–prey closed orbits, the van der Pol limit cycle."] } },
  ],
  params: [
    { id: "Kp", name: ["比例增益 K_p", "Proportional gain K_p"], min: 0, max: 150, step: 0.01, value: 40, unit: "N·m/rad", digits: 2 },
    { id: "Kd", name: ["微分增益 K_d", "Derivative gain K_d"], min: 0, max: 30, step: 0.01, value: 3, unit: "N·m·s/rad", digits: 2 },
    { id: "th0", name: ["初始倾角 θ₀", "Initial tilt θ₀"], min: -80, max: 80, step: 0.5, value: 10, unit: "°", digits: 1 },
    { id: "w0", name: ["初始倾角速度", "Initial tilt rate"], min: -5, max: 5, step: 0.05, value: 0, unit: "rad/s", digits: 2 },
    { id: "sys", name: ["系统：1 有阻尼单摆，2 捕食者–猎物，3 范德波尔振子", "System: 1 damped pendulum, 2 predator–prey, 3 van der Pol"], min: 1, max: 3, step: 1, value: 1, digits: 0 },
    { id: "x0", name: ["初值 x₀（单摆为 θ₀/rad）", "Initial x₀ (θ₀/rad for the pendulum)"], min: -4, max: 50, step: 0.01, value: 0, digits: 2 },
    { id: "y0", name: ["初值 y₀（单摆为 ω₀/(rad/s)）", "Initial y₀ (ω₀/(rad/s) for the pendulum)"], min: -12, max: 30, step: 0.01, value: 5, digits: 2 },
    { id: "p", name: ["参数：单摆的阻尼 c / 范德波尔的 μ", "Parameter: pendulum damping c / van der Pol μ"], min: 0, max: 5, step: 0.01, value: 0, digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["轨线", "trajectory"], color: "#1f77b4" }, { name: ["倒下 / 分界线", "falls / separatrix"], color: "#d62728" }, { name: ["平衡点", "equilibria"], color: "#2ca02c" }],
  tasks: [
    { id: "min", robot: true, text: ["K_d = 3、初始倾角 10°：K_p 至少多大，机器人才不倒、并且 5 s 内倾角至少减半？与 m g h 比较。", "With K_d = 3 and 10° initial tilt, what is the least K_p that keeps the robot up and at least halves the tilt within 5 s? Compare with m g h."],
      demo: { scene: "bal", set: { Kp: 20.5, Kd: 3, th0: 10, w0: 0 }, wait: 1 } },
    { id: "crit", robot: true, text: ["K_p = 70.82：K_d 取多少时，线性化恰为临界阻尼（两个相等的负实根）？", "With K_p = 70.82, which K_d makes the linearization critically damped (a double negative root)?"],
      demo: { scene: "bal", set: { Kp: 70.82, Kd: 12.8, th0: 10, w0: 0 }, wait: 1 } },
    { id: "basin", robot: true, text: ["K_p = 70.82、K_d = 8.96、从静止释放：初始倾角最大取多少还能救回来？与 arcsin(15/(m g h)) 比较。", "With K_p = 70.82, K_d = 8.96, released from rest: what is the largest initial tilt that can still be saved? Compare with arcsin(15/(m g h))."],
      demo: { scene: "bal", set: { Kp: 70.82, Kd: 8.96, th0: 49, w0: 0 }, wait: 1 } },
    { id: "sep", text: ["无阻尼单摆（c = 0）从最低点出发：初角速度至少多大才能越过最高点？（略高于分界线的值即可）", "Undamped pendulum (c = 0) from the bottom: what least initial speed carries it over the top? (just above the separatrix)"],
      demo: { scene: "sys", set: { sys: 1, p: 0, x0: 0, y0: 8.9 }, wait: 1 } },
    { id: "lc", text: ["范德波尔振子（μ = 1）：从离原点很远（|x₀| ≥ 3）的地方出发，最后的振幅是多少？再从原点附近出发试试。", "Van der Pol (μ = 1): start far out (|x₀| ≥ 3). What is the final amplitude? Then start near the origin."],
      demo: { scene: "sys", set: { sys: 3, p: 1, x0: 3.5, y0: 0 }, wait: 1 } },
  ],
  think: ["线性化说只要 K_p > m g h、K_d > 0 就稳定。为什么实际的自平衡机器人还要限制倾角、限制速度？吸引域和哪些参数有关？",
          "Linearization says K_p > m g h and K_d > 0 are enough. Why do real balancing robots still limit tilt and speed? Which parameters set the basin of attraction?"],

  M: 5, H: 0.4, G: 9.81, TMAX: 15,
  bal(p) {
    const I = this.M * this.H * this.H, mgl = this.M * this.G * this.H;
    const f = (th, w) => { let tau = -p.Kp * th - p.Kd * w; tau = Math.max(-this.TMAX, Math.min(this.TMAX, tau)); return [w, (mgl * Math.sin(th) + tau) / I]; };
    return { I, mgl, f };
  },
  run(f, x0, y0, T, dt, lim) {
    const pts = [[x0, y0]];
    let x = x0, y = y0;
    for (let t = 0; t < T; t += dt) {
      const a = f(x, y), b = f(x + dt / 2 * a[0], y + dt / 2 * a[1]), c = f(x + dt / 2 * b[0], y + dt / 2 * b[1]), d = f(x + dt * c[0], y + dt * c[1]);
      x += dt / 6 * (a[0] + 2 * b[0] + 2 * c[0] + d[0]); y += dt / 6 * (a[1] + 2 * b[1] + 2 * c[1] + d[1]);
      pts.push([x, y]);
      if (lim && lim(x, y)) break;
    }
    return pts;
  },
  sysf(p) {
    if (p.sys === 1) { const k = this.G / 0.5; return (x, y) => [y, -k * Math.sin(x) - p.p * y]; }
    if (p.sys === 2) return (x, y) => [x - 0.1 * x * y, -1.5 * y + 0.075 * x * y];
    return (x, y) => [y, p.p * (1 - x * x) * y - x];
  },
  box(p) {
    if (p.sys === 1) return { xmin: -Math.PI, xmax: 3 * Math.PI, ymin: -12, ymax: 12, xl: "θ / rad", yl: "ω / (rad/s)" };
    if (p.sys === 2) return { xmin: 0, xmax: 50, ymin: 0, ymax: 30, xl: "x", yl: "y" };
    return { xmin: -4, xmax: 4, ymin: -4, ymax: 4, xl: "x", yl: "ẋ" };
  },
  held(tr, th0) { const last = tr[tr.length - 1]; return tr.every((q) => Math.abs(q[0]) <= 1.6) && Math.abs(last[0]) < Math.max(0.01, 0.5 * Math.abs(th0)); },   // 没倒，且倾角在 5 s 内至少减半
  start(p, s) { return s.pt ? s.pt : [p.x0, p.y0]; },
  change(api, s, pid) { if (pid === "x0" || pid === "y0" || pid === "sys") s.pt = null; },
  reset(api, s) { s.pt = null; },
  pointer(kind, px, py, api, s) {
    if (api.scene !== "sys" || kind !== "down" || !s.G) return;
    const o = s.G.o, x = o.xmin + (px - o.x) / o.w * (o.xmax - o.xmin), y = o.ymin + (o.y + o.h - py) / o.h * (o.ymax - o.ymin);
    if (x >= o.xmin && x <= o.xmax && y >= o.ymin && y <= o.ymax) s.pt = [Math.round(x * 100) / 100, Math.round(y * 100) / 100];
  },
  readouts(api, s) {
    const p = api.p;
    if (api.scene === "bal") {
      const B = this.bal(p), kk = (p.Kp - B.mgl) / B.I, cc = p.Kd / B.I, disc = cc * cc - 4 * kk;
      const ev = disc >= 0 ? [(-cc + Math.sqrt(disc)) / 2, (-cc - Math.sqrt(disc)) / 2] : null;
      const evs = ev ? ev[0].toFixed(2) + ", " + ev[1].toFixed(2) : (-cc / 2).toFixed(2) + " ± " + (Math.sqrt(-disc) / 2).toFixed(2) + "i";
      const tr = this.run(B.f, p.th0 * Math.PI / 180, p.w0, 5, 0.002, (x) => Math.abs(x) > 1.6);
      const last = tr[tr.length - 1], ok = this.held(tr, p.th0 * Math.PI / 180);
      const zeta = kk > 0 ? cc / (2 * Math.sqrt(kk)) : NaN;
      if (ok && p.Kd === 3 && Math.abs(p.th0 - 10) < 1e-9 && p.w0 === 0 && p.Kp <= 21) api.done("min");
      if (Math.abs(p.Kp - 70.82) < 0.006 && Math.abs(zeta - 1) < 0.02) api.done("crit");
      if (ok && Math.abs(p.Kp - 70.82) < 0.006 && Math.abs(p.Kd - 8.96) < 0.006 && p.w0 === 0 && Math.abs(p.th0) >= 48) api.done("basin");
      return [[["重力的“负刚度” m g h", "gravity's negative stiffness m g h"], B.mgl.toFixed(2) + " N·m/rad"],
              [["线性化的特征值", "linearized eigenvalues"], evs + " s⁻¹"],
              [["线性化判断", "linearization says"], kk > 0 && cc > 0 ? api.T("渐近稳定", "asymptotically stable") : api.T("不稳定（或临界）", "unstable (or marginal)")],
              [["阻尼比 ζ（K_p > m g h 时）", "damping ratio ζ (if K_p > m g h)"], isNaN(zeta) ? "—" : zeta.toFixed(3)],
              [["静力极限 arcsin(15/(m g h))", "static limit arcsin(15/(m g h))"], (Math.asin(this.TMAX / B.mgl) * 180 / Math.PI).toFixed(1) + "°"],
              [["这次仿真的结果（5 s）", "this run (5 s)"], ok ? api.T("扶住了", "held up") : tr.every((q) => Math.abs(q[0]) <= 1.6) ? api.T("没倒，但恢复得很慢", "upright but recovering very slowly") : api.T("倒下了", "fell over")]];
    }
    const [x0, y0] = this.start(p, s), f = this.sysf(p);
    const tr = this.run(f, x0, y0, p.sys === 2 ? 15 : 40, 0.005, (x, y) => !isFinite(x) || Math.abs(x) > 1e4 || Math.abs(y) > 1e4);
    const rows = [[["初值", "initial point"], "(" + x0.toFixed(2) + ", " + y0.toFixed(2) + ")"]];
    if (p.sys === 1) {
      const k = this.G / 0.5, E = y0 * y0 / 2 - k * Math.cos(x0), over = Math.max(...tr.map((q) => q[0])) > Math.PI;
      if (p.p === 0 && Math.abs(x0) < 0.01 && y0 > 2 * Math.sqrt(k) && y0 <= 2 * Math.sqrt(k) * 1.02) api.done("sep");
      rows.push([["能量 E = ω²/2 − (g/l) cos θ（分界线 E = g/l = 19.62）", "energy E (separatrix at g/l = 19.62)"], E.toFixed(3)],
                [["分界线上最低点的角速度 2√(g/l)", "separatrix speed at the bottom 2√(g/l)"], (2 * Math.sqrt(k)).toFixed(3) + " rad/s"],
                [["是否越过最高点", "goes over the top"], over ? api.T("是", "yes") : api.T("否", "no")]);
    } else if (p.sys === 2) {
      const H = (x, y) => 0.075 * x - 1.5 * Math.log(x) + 0.1 * y - Math.log(y);
      rows.push([["平衡点", "equilibrium"], "(20, 10)"],
                [["守恒量 H 的变化（数值误差）", "change of H (numerical error)"], x0 > 0 && y0 > 0 ? Math.abs(H(tr[tr.length - 1][0], tr[tr.length - 1][1]) - H(x0, y0)).toExponential(1) : "—"]);
    } else {
      const tail = tr.slice(Math.floor(tr.length * 0.75)), amp = Math.max(...tail.map((q) => Math.abs(q[0])));
      if (Math.abs(p.p - 1) < 1e-9 && Math.abs(x0) >= 3 && Math.abs(amp - 2.0086) < 0.04) api.done("lc");
      rows.push([["末段的最大 |x|（极限环振幅）", "max |x| near the end (limit-cycle amplitude)"], amp.toFixed(4)]);
    }
    return rows;
  },
  draw(api, s) {
    const p = api.p, w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), green = api.css("--green"), muted = api.css("--muted");
    const bal = api.scene === "bal";
    const bx = bal ? { xmin: -1.6, xmax: 1.6, ymin: -6, ymax: 6, xl: "θ / rad", yl: "θ̇ / (rad/s)" } : this.box(p);
    const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: bx.xmin, xmax: bx.xmax, ymin: bx.ymin, ymax: bx.ymax, xlabel: bx.xl, ylabel: bx.yl });
    s.G = G;
    G.axes();
    const f = bal ? this.bal(p).f : this.sysf(p), o = G.o, sx = o.w / (o.xmax - o.xmin), sy = o.h / (o.ymax - o.ymin);
    const nx = Math.round(o.w / 34), ny = Math.round(o.h / 30);
    for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
      const x = o.xmin + (i + 0.5) / nx * (o.xmax - o.xmin), y = o.ymin + (j + 0.5) / ny * (o.ymax - o.ymin);
      const v = f(x, y), dx = v[0] * sx, dy = v[1] * sy, L = Math.hypot(dx, dy);
      if (!(L > 0)) continue;
      const cx = G.X(x), cy = G.Y(y);
      api.arrow(cx - dx / L * 8, cy + dy / L * 8, cx + dx / L * 8, cy - dy / L * 8, muted, 1);
    }
    if (bal) {
      const B = this.bal(p), lim = Math.asin(Math.min(1, this.TMAX / B.mgl));
      G.vline(lim, red, [3, 4]); G.vline(-lim, red, [3, 4]);
      const tr = this.run(B.f, p.th0 * Math.PI / 180, p.w0, 5, 0.002, (x) => Math.abs(x) > 1.6);
      const ok = this.held(tr, p.th0 * Math.PI / 180);
      G.pts(tr, ok ? blue : red, 2.5);
      G.point(p.th0 * Math.PI / 180, p.w0, ok ? blue : red);
      G.point(0, 0, green);
      return;
    }
    if (p.sys === 1) {
      const k = this.G / 0.5;
      G.fn((x) => 2 * Math.sqrt(k) * Math.abs(Math.cos(x / 2)), red, 1.5, [5, 4]);
      G.fn((x) => -2 * Math.sqrt(k) * Math.abs(Math.cos(x / 2)), red, 1.5, [5, 4]);
      [0, 2 * Math.PI].forEach((q) => G.point(q, 0, green));
      [-Math.PI, Math.PI, 3 * Math.PI].forEach((q) => G.point(q, 0, red));
    } else if (p.sys === 2) G.point(20, 10, green);
    else G.point(0, 0, red);
    const [x0, y0] = this.start(p, s);
    G.pts(this.run(this.sysf(p), x0, y0, p.sys === 2 ? 15 : 40, 0.005, (x, y) => !isFinite(x) || Math.abs(x) > 1e4 || Math.abs(y) > 1e4), blue, 2);
    G.point(x0, y0, blue);
  },
});
