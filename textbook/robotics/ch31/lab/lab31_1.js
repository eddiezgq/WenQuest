// 实验 31.1 改截面看变形和重量（配 31.2、31.4 节）。
// 场景“WQ-CR5 手臂”：手臂水平伸直、工具朝下（与程序 ex31_2.py、ex31_4.py 同一工况），大臂长 0.40 m、小臂 0.36 m。
//   负载引起的 TCP 下沉 = 关节 + 两管弯曲 + 两管扭转（31.2 节“小转角乘力臂”，伸直时化成下面的闭式）：
//     J2：P·r2²/K_L，r2 = 0.86 m（负载点到 J2 的水平距离）；J3：P·r3²/K_M，r3 = 0.46 m；J4、J5：P·(0.10² + 0.05²)/K_S；
//     大臂弯曲 P·(0.86³ − 0.46³)/(3EI_u)，小臂弯曲 P·(0.46³ − 0.10³)/(3EI_f)；扭转：负载横向偏 0.07 m，P·0.07²·L/(G·I_p)。
//   谐波减速器的扭转刚度（零件库 D-RDC-HD-CSF，官网）：K1 32 号 6.7、25 号 3.1、17 号 1.0；K3 12、5.7、1.6（×10⁴ N·m/rad）。
//   标准截面（6061、Ø90×3 / Ø75×3、K1、5 kg）：关节 0.938 mm、大臂 0.165、小臂 0.052、扭转 0.006，共 1.160 mm（程序 31.2.1）。
//   J2 的重力矩：标准 91.30 N·m（5 kg），管子质量变了按质心位置（大臂 0.20 m、小臂 0.58 m）增减，负载按 0.86 m 增减。
//   大臂根部：弯矩 = J2 的重力矩，扭矩 3.59 + 负载 × 9.81 × 0.07 N·m；当量应力 √(σ² + 3τ²)。
//   材料（问渠 CAE 材料表；碳纤维管取 Easy Composites 卷制管的产品页，0/90 铺层）：
//     6061-T6 E 68.9 GPa、ν 0.33、2.70 g/cm³、屈服 276 MPa；7075-T6 71.7、0.33、2.81、503；Q345 206、0.30、7.85、355；
//     碳纤维管 E 90 GPa、G 4.6 GPa、1.60 g/cm³、抗拉 750 MPa（强度按抗拉强度算）。
// 场景“钓鱼竿”：两节碳纤维竿（各长 1.2 m、壁厚 1 mm），竿尖挂 0.3 kg 的鱼；下沉 = P·(4.032/EI_根 + 0.576/EI_梢)（同一积分）。
WQ.lab({
  title: ["实验 31.1 改截面看变形和重量", "Lab 31.1 Change the section: deflection and weight"],
  goal: ["改大臂、小臂铝管的外径、壁厚和材料，看手臂的重量、J2 的力矩、加负载后 TCP 又下沉多少（关节、大臂、小臂各占多少）和管子的强度；体会 31.2 节“刚度的大头在关节”、31.4 节“把材料放到外面”。",
         "Change the tubes' diameters, walls and material; watch the arm's weight, J2's torque, the extra TCP sag under the payload (joints, upper arm, forearm) and the tube strength — Section 31.2's “the joints dominate” and Section 31.4's “put the material outside”."],
  scenes: [
    { id: "arm", robot: true, name: ["WQ-CR5 手臂", "WQ-CR5 arm"], hide: ["db", "dt"],
      problem: { title: ["机器人问题：管子怎么选", "Robot problem: choosing the tubes"],
                 text: ["手臂水平伸直，抓起 5 kg 的零件，TCP 又往下掉一点。换粗管、厚管、钢管还是碳纤维管？手臂重了，J2 的力矩也跟着变。",
                        "Outstretched, the arm picks up 5 kg and the TCP drops a little more. Thicker, wider, steel or carbon tubes? A heavier arm also changes J2's torque."] } },
    { id: "rod", name: ["钓鱼竿", "A fishing rod"], hide: ["d1", "t1", "d2", "t2", "mat", "kj"],
      problem: { title: ["生活中的例子：鱼竿为什么根粗梢细", "Everyday example: why a rod is thick at the butt"],
                 text: ["两节碳纤维竿，竿尖挂一条 0.3 kg 的鱼。同样的重量，粗细怎样搭配，竿尖弯得最少？",
                        "A two-piece carbon rod with a 0.3 kg fish on the tip. For the same weight, which pair of diameters bends the tip least?"] } },
  ],
  params: [
    { id: "d1", name: ["大臂外径", "Upper-arm tube OD"], min: 60, max: 140, step: 1, value: 90, unit: "mm", digits: 0 },
    { id: "t1", name: ["大臂壁厚", "Upper-arm wall"], min: 0.5, max: 8, step: 0.1, value: 3, unit: "mm", digits: 1 },
    { id: "d2", name: ["小臂外径", "Forearm tube OD"], min: 50, max: 120, step: 1, value: 75, unit: "mm", digits: 0 },
    { id: "t2", name: ["小臂壁厚", "Forearm wall"], min: 0.5, max: 8, step: 0.1, value: 3, unit: "mm", digits: 1 },
    { id: "mat", name: ["材料：0 6061 铝 / 1 7075 铝 / 2 Q345 钢 / 3 碳纤维管", "Material: 0 6061 Al / 1 7075 Al / 2 Q345 steel / 3 CFRP tube"], min: 0, max: 3, step: 1, value: 0, unit: "", digits: 0 },
    { id: "kj", name: ["关节刚度：0 按 K1（最软）/ 1 按 K3（最硬）", "Joint stiffness: 0 K1 (softest) / 1 K3 (stiffest)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "db", name: ["竿根外径", "Butt OD"], min: 8, max: 20, step: 0.5, value: 14, unit: "mm", digits: 1 },
    { id: "dt", name: ["竿梢外径", "Tip OD"], min: 8, max: 20, step: 0.5, value: 14, unit: "mm", digits: 1 },
  ],
  tasks: [
    { id: "std", robot: true, text: ["标准截面（6061 铝，Ø90×3、Ø75×3，关节按 K1，5 kg）：读出下沉的组成，关节占多少？",
                                     "Standard tubes (6061 Al, Ø90×3 and Ø75×3, joints at K1, 5 kg): read the parts of the sag. What share is the joints'?"],
      demo: { scene: "arm", set: { d1: 90, t1: 3, d2: 75, t2: 3, mat: 0, kj: 0 }, press: [] } },
    { id: "steel", robot: true, text: ["两根都换成 Q345 钢管（外径不变），调壁厚，让两管弯曲的下沉与标准相差不到 5%：比一比两根管的重量。",
                                       "Switch both tubes to Q345 steel (same ODs) and set the walls so that the tubes' bending sag is within 5 % of the standard: compare the tube weights."],
      demo: { scene: "arm", set: { d1: 90, t1: 0.9, d2: 75, t2: 1.0, mat: 2, kj: 0 }, press: [] } },
    { id: "section", robot: true, text: ["只改截面（6061 铝）：大臂弯曲的下沉减到标准的一半以下，大臂的管子重不超过标准的 1.3 倍。",
                                         "Section only (6061 Al): halve the upper arm's bending sag while its tube weighs at most 1.3 times the standard."],
      demo: { scene: "arm", set: { d1: 130, t1: 2.5, d2: 75, t2: 3, mat: 0, kj: 0 }, press: [] } },
    { id: "cfrp", robot: true, text: ["两根都换成碳纤维管（外径不变），两管弯曲的下沉与标准相差不到 5%：两根管轻了多少？J2 的力矩少了多少？",
                                      "Switch both tubes to carbon (same ODs) with the tubes' bending sag within 5 % of the standard: how much lighter, and how much less J2 torque?"],
      demo: { scene: "arm", set: { d1: 90, t1: 2.2, d2: 75, t2: 2.3, mat: 3, kj: 0 }, press: [] } },
    { id: "rod", text: ["钓鱼竿：两节竿总重不超过 0.16 kg，竿尖下沉不超过 0.14 m。", "Fishing rod: total weight at most 0.16 kg and tip sag at most 0.14 m."],
      demo: { scene: "rod", set: { db: 18, dt: 10 }, press: [] } },
  ],
  think: ["加 5 kg 后的下沉里关节占八成左右。如果客户要求下沉减半，你先改哪里？改管子能做到吗？",
          "The joints make up about four fifths of the extra sag. If a customer asks for half the sag, where do you start? Can tubes alone do it?"],

  G0: 9.81, A2: 0.40, A3: 0.36, LT: 0.86, R3: 0.46, YOFF: 0.07, TAU2: 91.2984, T0: 3.5915,
  MATS: [{ n: ["6061-T6 铝", "6061-T6 Al"], E: 68.9e9, nu: 0.33, rho: 2700, R: 276 }, { n: ["7075-T6 铝", "7075-T6 Al"], E: 71.7e9, nu: 0.33, rho: 2810, R: 503 },
         { n: ["Q345 钢", "Q345 steel"], E: 206e9, nu: 0.30, rho: 7850, R: 355 }, { n: ["碳纤维管", "CFRP tube"], E: 90e9, G: 4.6e9, rho: 1600, R: 750 }],
  K: [[6.7e4, 3.1e4, 1.0e4], [12e4, 5.7e4, 1.6e4]],
  tube(D, t, m) {                            // 截面（m）与材料：面积、I、Ip、G
    const ro = D / 2000, ri = ro - t / 1000, I = Math.PI / 4 * (ro ** 4 - ri ** 4);
    return { ro, A: Math.PI * (ro * ro - ri * ri), I, Ip: 2 * I, G: m.G || m.E / (2 * (1 + m.nu)) };
  },
  calc(p) {
    p = Object.assign({ mp: 5 }, p);                // 负载固定 5 kg（额定负载）
    const m = this.MATS[Math.round(p.mat)], al = this.MATS[0], P = p.mp * this.G0, kk = this.K[Math.round(p.kj)];
    const u = this.tube(p.d1, p.t1, m), f = this.tube(p.d2, p.t2, m);
    const u0 = this.tube(90, 3, al), f0 = this.tube(75, 3, al);
    const mu = m.rho * u.A * this.A2, mf = m.rho * f.A * this.A3, mu0 = al.rho * u0.A * this.A2, mf0 = al.rho * f0.A * this.A3;
    const j = P * this.LT ** 2 / kk[0] + P * this.R3 ** 2 / kk[1] + P * (0.1 ** 2 + 0.05 ** 2) / kk[2];
    const ub = P * (this.LT ** 3 - this.R3 ** 3) / (3 * m.E * u.I), fb = P * (this.R3 ** 3 - 0.1 ** 3) / (3 * m.E * f.I);
    const tr = P * this.YOFF ** 2 * (this.A2 / (u.G * u.Ip) + this.A3 / (f.G * f.Ip));
    const tau2 = this.TAU2 + this.G0 * ((mu - mu0) * this.A2 / 2 + (mf - mf0) * (this.A2 + this.A3 / 2)) + (p.mp - 5) * this.G0 * this.LT;
    const T = this.T0 + P * this.YOFF;
    const sig = tau2 * u.ro / u.I / 1e6, tau = T * u.ro / u.Ip / 1e6, vm = Math.sqrt(sig * sig + 3 * tau * tau);
    return { m, j, ub, fb, tr, tot: j + ub + fb + tr, mu, mf, mu0, mf0, tau2, vm, n: m.R / vm, ok: p.t1 < p.d1 / 2 && p.t2 < p.d2 / 2 };
  },
  std() { return this.calc({ d1: 90, t1: 3, d2: 75, t2: 3, mat: 0, kj: 0 }); },
  rod(db, dt) {
    const E = 90e9, P = 0.3 * this.G0, I = (D) => Math.PI / 64 * ((D / 1000) ** 4 - ((D - 2) / 1000) ** 4);
    const sag = P * (4.032 / (E * I(db)) + 0.576 / (E * I(dt)));
    const mass = 1600 * Math.PI * ((db - 1) + (dt - 1)) * 1e-6 * 1.2;
    return { sag, mass, Ib: I(db), It: I(dt) };
  },
  nb(rows) { return rows.map(([k, v]) => [k, String(v).replace(/ /g, " ")]); },
  readouts(api) {
    const f = api.fmt, T = (z, e) => (api.lang() === "en" ? e : z);
    if (api.scene === "rod") {
      const r = this.rod(api.p.db, api.p.dt);
      if (r.mass <= 0.16 + 1e-9 && r.sag <= 0.14) api.done("rod");
      return this.nb([[["两节竿总重", "Total weight"], f(r.mass, 3) + " kg"], [["竿尖下沉", "Tip sag"], f(r.sag, 3) + " m"],
        [["竿根 EI / 竿梢 EI", "Butt EI / tip EI"], `${f(90e9 * r.Ib, 1)} / ${f(90e9 * r.It, 1)} N·m²`]]);
    }
    const p = api.p, c = this.calc(p), s = this.std();
    const mm = (x) => f(x * 1000, 3);
    const stdset = Math.round(p.mat) === 0 && Math.round(p.kj) === 0;
    if (stdset && p.d1 === 90 && Math.abs(p.t1 - 3) < 1e-9 && p.d2 === 75 && Math.abs(p.t2 - 3) < 1e-9) api.done("std");
    const tb = c.ub + c.fb, tb0 = s.ub + s.fb;
    if (c.ok && Math.round(p.mat) === 2 && p.d1 === 90 && p.d2 === 75 && Math.abs(tb / tb0 - 1) <= 0.05) api.done("steel");
    if (c.ok && Math.round(p.mat) === 0 && c.ub <= 0.5 * s.ub && c.mu <= 1.3 * s.mu) api.done("section");
    if (c.ok && Math.round(p.mat) === 3 && p.d1 === 90 && p.d2 === 75 && Math.abs(tb / tb0 - 1) <= 0.05) api.done("cfrp");
    return this.nb([
      [["材料", "Material"], api.P(c.m.n) + (c.ok ? "" : T("（壁厚超过半径）", " (wall thicker than the radius)"))],
      [["两根管的质量（标准）", "Tube mass (standard)"], `${f(c.mu + c.mf, 3)} kg（${f(c.mu0 + c.mf0, 3)}）`],
      [["J2 的重力矩（标准）", "J2 gravity torque (standard)"], `${f(c.tau2, 2)} N·m（${f(s.tau2, 2)}）`],
      [["加负载后 TCP 又下沉", "Extra TCP sag under the payload"], `${mm(c.tot)} mm`],
      [["　其中关节", "  joints"], `${mm(c.j)} mm（${f(c.j / c.tot * 100, 0)} %）`],
      [["　大臂弯曲 / 小臂弯曲", "  upper / forearm bending"], `${mm(c.ub)} / ${mm(c.fb)} mm`],
      [["　两管扭转", "  tube torsion"], `${mm(c.tr)} mm`],
      [["大臂根部当量应力；安全系数", "Upper-arm root equivalent stress; safety factor"], `${f(c.vm, 2)} MPa；${f(c.n, 0)}`],
    ]);
  },
  draw(api) {
    const { w, h } = api, c = api.ctx, f = api.fmt;
    if (api.scene === "rod") {
      const r = this.rod(api.p.db, api.p.dt), x0 = w * 0.08, y0 = h * 0.3, L = w * 0.8, k = L / 2.4, amp = 1.0;
      api.label(api.lang() === "en" ? "tip sag drawn to scale" : "竿尖下沉按比例画", x0, h * 0.1, api.css("--muted"), 12, "left");
      const P = 0.3 * 9.81, EIb = 90e9 * r.Ib, EIt = 90e9 * r.It;
      // 两段的挠度：w(x) 由弯矩 P(L − x) 积分两次
      const pts = [];
      let th = 0, y = 0;
      const n = 120, dx = 2.4 / n;
      for (let i = 0; i <= n; i++) {
        const x = i * dx;
        pts.push([x, y]);
        const EI = x < 1.2 ? EIb : EIt;
        th += P * (2.4 - x) / EI * dx;
        y += th * dx;
      }
      pts.forEach((q, i) => { if (i) api.line(x0 + k * pts[i - 1][0], y0 + k * amp * pts[i - 1][1], x0 + k * q[0], y0 + k * amp * q[1],
        q[0] <= 1.2 ? api.css("--blue") : api.css("--green"), q[0] <= 1.2 ? 2 + api.p.db / 4 : 2 + api.p.dt / 4); });
      api.line(x0, y0, x0 + L, y0, api.css("--grid"), 1, [4, 4]);
      const tip = pts[pts.length - 1];
      api.line(x0 + k * tip[0], y0 + k * tip[1], x0 + k * tip[0], y0 + k * tip[1] + 30, api.css("--ink"), 1);
      api.circle(x0 + k * tip[0], y0 + k * tip[1] + 38, 8, api.css("--amber"), api.css("--ink"));
      api.label(`${f(r.sag, 3)} m`, x0 + k * tip[0] - 10, y0 + k * tip[1] / 2, api.css("--red"), 13, "right");
      api.rect(x0 - 30, y0 - 8, 30, 16, api.css("--ink"));
      return;
    }
    const p = api.p, cc = this.calc(p), k = Math.min(w / 1.15, h / 0.7), x0 = w * 0.07, y0 = h * 0.30;
    const X = (x) => x0 + k * x;
    const amp = 120;                                       // 下沉放大倍数
    api.label(api.lang() === "en" ? `side view; sag × ${amp}` : `侧视；下沉放大 ${amp} 倍`, x0, h * 0.06, api.css("--muted"), 12, "left");
    // 未变形的手臂（虚线）与变形后（实线）：关节转角 + 管子弯曲，按负载引起的下沉放大
    const P = 5 * 9.81, kk = this.K[Math.round(p.kj)], m = cc.m;
    const u = this.tube(p.d1, p.t1, m), fo = this.tube(p.d2, p.t2, m);
    const n = 80, pts = [];
    let th = P * this.LT / kk[0], y = 0;
    for (let i = 0; i <= n; i++) {
      const x = 0.86 * i / n;
      pts.push([x, y]);
      if (Math.abs(x - this.A2) < 0.86 / n / 2 + 1e-9) th += P * this.R3 / kk[1];
      if (Math.abs(x - 0.76) < 0.86 / n / 2 + 1e-9) th += P * 0.1 / kk[2];
      const EI = x < this.A2 ? m.E * u.I : x < 0.76 ? m.E * fo.I : 1e12;
      th += P * Math.max(0, this.LT - x) / EI * (0.86 / n);
      y += th * (0.86 / n);
    }
    api.line(X(0), y0, X(0.76), y0, api.css("--grid"), 1, [4, 4]);
    const wu = Math.max(3, k * p.d1 / 1000), wf = Math.max(3, k * p.d2 / 1000);
    pts.forEach((q, i) => {
      if (!i || q[0] > 0.76 + 1e-9) return;
      const a = pts[i - 1];
      api.line(X(a[0]), y0 + amp * k * a[1], X(q[0]), y0 + amp * k * q[1], q[0] <= this.A2 ? api.css("--blue") : api.css("--green"), q[0] <= this.A2 ? wu : wf);
    });
    const yj3 = y0 + amp * k * pts[Math.round(this.A2 / 0.86 * n)][1], tip = pts[n];
    api.circle(X(0), y0, k * 0.055, api.css("--panel"), api.css("--ink"));
    api.circle(X(this.A2), yj3, k * 0.045, api.css("--panel"), api.css("--ink"));
    const yw = y0 + amp * k * pts[Math.round(0.76 / 0.86 * n)][1];
    api.line(X(0.76), yw, X(0.86), y0 + amp * k * tip[1], api.css("--amber"), 6);
    api.line(X(0.86), y0 + amp * k * tip[1], X(0.86), y0 + amp * k * tip[1] + k * 0.19, api.css("--ink"), 3);
    const ty = y0 + amp * k * tip[1] + k * 0.19;
    api.rect(X(0.86) - k * 0.04, ty, k * 0.08, k * 0.06, api.css("--amber"), api.css("--ink"));
    api.label("5 kg", X(0.86) + k * 0.05, ty + k * 0.03, api.css("--ink"), 12, "left");
    api.label("J2", X(0), y0 - k * 0.075, api.css("--ink"), 12, "center");
    api.label("J3", X(this.A2), yj3 - k * 0.065, api.css("--ink"), 12, "center");
    // 下沉的组成：横条
    const bx = w * 0.07, by = h * 0.80, bw = w * 0.86, tot = this.std().tot * 1.6, parts = [[cc.j, "--red", ["关节", "joints"]],
      [cc.ub, "--blue", ["大臂弯曲", "upper bending"]], [cc.fb, "--green", ["小臂弯曲", "forearm bending"]], [cc.tr, "--muted", ["扭转", "torsion"]]];
    let x = bx;
    parts.forEach(([v, col, nm]) => {
      const ww = Math.min(bw - (x - bx), bw * v / tot);
      api.rect(x, by, ww, 18, api.css(col));
      if (ww > 50) api.label(api.P(nm), x + 4, by + 9, "#fff", 11, "left");
      x += ww;
    });
    api.rect(bx, by, bw, 18, null, api.css("--ink"));
    api.label((api.lang() === "en" ? "extra TCP sag " : "加负载后 TCP 又下沉 ") + f(cc.tot * 1000, 3) + " mm", bx, by - 10, api.css("--ink"), 12, "left");
  },
});
