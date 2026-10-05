// 实验 15.4 关节限位与多目标（配 15.4 节）。
// 机器人场景：平面 3R 臂 0.425、0.392、0.1 m（14.2.5 节，UR5e 的侧视）。关节限位：θ₁ ∈ [−60°, 150°]，θ₂ ∈ [0°, 150°]（肘只能向一侧弯，
//   与 Panda 关节 4 相同），θ₃ ∈ [−150°, 150°]。目标位姿 (x, y, φ_d)，误差 e = (x_d − x, y_d − y, L_c·wrap(φ_d − φ))，L_c = 0.3 m，
//   雅可比 J = [J_p; L_c (1 1 1)]。起点 θ⁽⁰⁾ = (60°, 40°, −100°)。四种做法：
//   0 不管限位：Δθ = Jᵀ(JJᵀ + 10⁻¹⁰I)⁻¹e（式 (15.1.8)，加一点点阻尼只为防止除以零）；
//   1 每步截断：同上，再把 θ 截断到限位（式 (15.4.2)）；
//   2 有界的一步：min ‖JΔ − e‖² + λ²‖Δ‖²，θ_min − θ ≤ Δ ≤ θ_max − θ，λ = 10⁻³（式 (15.4.3)）；三个变量的有界最小二乘，
//     逐一试 27 种“自由 / 在下限 / 在上限”的组合，取满足 KKT 条件的一组（定理 8.3.1），即精确解；
//   3 任务优先级（不管限位）：主任务为位置，次任务为朝向：Δθ = J₁⁺e₁ + (J₂N₁)#(k_p e₂ − J₂J₁⁺e₁)，
//     (J₂N₁)# 为阻尼 λ₂ = 0.3 的伪逆，k_p = 0.1，两部分各自限幅 0.2 rad（式 (15.4.10)，算例 15.4.2）。
// 生活场景：人的手臂（上臂 0.30 m、前臂 0.27 m、手 0.08 m）端一杯水放到架子上。主任务可选“杯子竖直”（手的朝向 φ = 0）或“手到架子”，
//   另一个为次任务，同一个优先级公式（λ₂ = 0.1，k_p = 0.3）。
WQ.lab({
  title: ["实验 15.4 关节限位与多目标", "Lab 15.4 Joint limits and several goals"],
  goal: ["看不管限位的迭代怎样给出超限的解，截断法怎样卡在限位上，每步解一个有界最小二乘怎样既守住限位又收敛；再看两个任务冲突时，优先级怎样保住主任务。",
         "See how ignoring the limits gives a solution beyond them, how clipping gets stuck at a limit, and how a bounded least-squares step keeps the limits and still converges; then see how a priority keeps the primary task when two tasks conflict."],
  scenes: [
    { id: "arm", robot: true, name: ["平面 3R 臂的关节限位", "Joint limits of a planar 3R arm"], hide: ["prim", "sx", "sy"],
      problem: { title: ["机器人问题：解出来了，关节却转不到", "Robot problem: a solution the joints cannot reach"],
                 text: ["浅色扇形是各关节允许的范围（肘只能向一侧弯）。红点和红色箭头是目标位置和工具朝向。选做法，按“求解”或“迭代一步”。",
                        "Pale wedges are the allowed joint ranges (the elbow bends one way only). The red dot and arrow are the goal position and tool direction. Choose a method and press “Solve” or “One step”."] } },
    { id: "cup", name: ["端一杯水放上架子", "Putting a full cup on a shelf"], hide: ["method", "x", "y", "phi"],
      problem: { title: ["生活中的例子：先保杯子不洒，还是先保够到架子？", "Everyday example: keep the cup level first, or reach the shelf first?"],
                 text: ["手臂由肩、肘、腕三个关节组成，手里端着一杯满水。架子太高太远时，两个要求不能同时满足，看优先级决定牺牲哪一个。",
                        "The arm has shoulder, elbow and wrist joints and holds a full cup. When the shelf is too high or far, both wishes cannot be met; the priority decides which one gives way."] } },
  ],
  params: [
    { id: "method", name: ["做法：0 不管限位 / 1 截断 / 2 有界的一步 / 3 任务优先级", "method: 0 ignore limits / 1 clip / 2 bounded step / 3 task priority"], min: 0, max: 3, step: 1, value: 2, unit: "", digits: 0 },
    { id: "x", name: ["目标 x", "goal x"], min: 0.3, max: 0.85, step: 0.01, value: 0.55, unit: "m", digits: 2 },
    { id: "y", name: ["目标 y", "goal y"], min: -0.4, max: 0.5, step: 0.01, value: -0.2, unit: "m", digits: 2 },
    { id: "phi", name: ["工具朝向 φ_d", "tool direction φ_d"], min: -180, max: 180, step: 1, value: 150, unit: "°", digits: 0 },
    { id: "prim", name: ["主任务：0 杯子竖直 / 1 手到架子", "primary: 0 cup level / 1 hand on shelf"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "sx", name: ["架子 x", "shelf x"], min: 0.2, max: 0.8, step: 0.01, value: 0.45, unit: "m", digits: 2 },
    { id: "sy", name: ["架子 y", "shelf y"], min: 0.0, max: 0.8, step: 0.01, value: 0.35, unit: "m", digits: 2 },
  ],
  buttons: [{ id: "step", name: ["迭代一步", "One step"] }, { id: "start", name: ["求解", "Solve"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "#cf222e", name: ["目标 / 超限的关节", "goal / joint beyond its limit"] }, { color: "#1f6feb", name: ["手臂", "arm"] }],
  tasks: [
    { id: "free", robot: true, text: ["不管限位（做法 0）：迭代收敛了，但解超出了关节限位。", "Ignore the limits (method 0): the iteration converges, but the solution is beyond the joint limits."],
      demo: { scene: "arm", set: { method: 0, x: 0.55, y: -0.2, phi: 150 }, press: ["start"], wait: 5 } },
    { id: "clamp", robot: true, text: ["每步截断（做法 1）：150 次以后仍未收敛，末端离目标超过 50 mm，有关节停在限位上。", "Clip each step (method 1): after 150 iterations it has not converged, the tip is over 50 mm away, and a joint sits at its limit."],
      demo: { scene: "arm", set: { method: 1, x: 0.55, y: -0.2, phi: 150 }, press: ["start"], wait: 8 } },
    { id: "box", robot: true, text: ["有界的一步（做法 2）：收敛，且三个关节都在限位以内。", "Bounded step (method 2): converges with all three joints within their limits."],
      demo: { scene: "arm", set: { method: 2, x: 0.55, y: -0.2, phi: 150 }, press: ["start"], wait: 5 } },
    { id: "prio", robot: true, text: ["任务优先级（做法 3）：目标 (0.75, 0.10) m、φ_d = 160°。位置误差小于 10⁻⁶ mm，朝向停在可行范围的端点（误差 0.05° 以内）。", "Task priority (method 3): goal (0.75, 0.10) m, φ_d = 160°. Position error below 10⁻⁶ mm, the tool angle stops at the end of its feasible range (within 0.05°)."],
      demo: { scene: "arm", set: { method: 3, x: 0.75, y: 0.1, phi: 160 }, press: ["start"], wait: 8 } },
    { id: "cup", text: ["生活场景：架子放到够不着的地方，以“杯子竖直”为主任务：杯子始终不倾斜（0.01° 以内），手停在离架子最近处。", "Everyday scene: put the shelf out of reach with “cup level” as the primary task: the cup never tilts (within 0.01°) and the hand stops as close as it can."],
      demo: { scene: "cup", set: { prim: 0, sx: 0.55, sy: 0.5 }, press: ["start"], wait: 8 } },
  ],
  think: ["做法 2 每一步都守住限位，为什么还可能停在离目标很远的地方？这时迭代满足什么条件（定理 15.4.1）？怎样补救？",
          "Method 2 keeps the limits at every step; why can it still stop far from the goal? What condition holds there (Theorem 15.4.1)? How would you recover?"],

  L: [0.425, 0.392, 0.1], LO: [-60, 0, -150], HI: [150, 150, 150], TH0: [60, 40, -100], LC: 0.3,
  LH: [0.30, 0.27, 0.08], THH0: [-70, 100, -30], DT: 0.03,
  rad: (d) => d * Math.PI / 180, deg: (r) => r * 180 / Math.PI,
  wrap(a) { return Math.atan2(Math.sin(a), Math.cos(a)); },
  pts(th, L) { let a = 0; const P = [[0, 0]]; th.forEach((t, i) => { a += t; P.push([P[i][0] + L[i] * Math.cos(a), P[i][1] + L[i] * Math.sin(a)]); }); return P; },
  jp(th, L) { const P = this.pts(th, L), e = P[3]; return [0, 1].map((r) => [0, 1, 2].map((i) => (r === 0 ? -(e[1] - P[i][1]) : e[0] - P[i][0]))); },
  inv(A) {   // 小方阵求逆（高斯-约当，列主元）
    const n = A.length, M = A.map((r, i) => [...r, ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      [M[c], M[p]] = [M[p], M[c]];
      const d = M[c][c]; for (let k = 0; k < 2 * n; k++) M[c][k] /= d;
      for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c]; for (let k = 0; k < 2 * n; k++) M[r][k] -= f * M[c][k]; }
    }
    return M.map((r) => r.slice(n));
  },
  T(A) { return A[0].map((_, j) => A.map((r) => r[j])); },
  mm(A, B) { return A.map((r) => B[0].map((_, j) => r.reduce((s, a, k) => s + a * B[k][j], 0))); },
  mv(A, x) { return A.map((r) => r.reduce((s, a, k) => s + a * x[k], 0)); },
  dampedPinvTimes(A, b, mu) {   // Aᵀ(AAᵀ + λ²I)⁻¹ b，λ = mu
    const AAt = this.mm(A, this.T(A)).map((r, i) => r.map((x, j) => x + (i === j ? mu * mu : 0)));
    return this.mv(this.T(A), this.mv(this.inv(AAt), b));
  },
  boxLS(A, b, lam, lo, hi) {   // min ‖AΔ − b‖² + λ²‖Δ‖²，lo ≤ Δ ≤ hi（3 个变量：枚举起作用约束，取满足 KKT 条件的一组）
    const n = 3;
    for (let code = 0; code < 27; code++) {
      const st = [code % 3, Math.floor(code / 3) % 3, Math.floor(code / 9)], d = [0, 0, 0], free = [];
      for (let i = 0; i < n; i++) { if (st[i] === 1) d[i] = lo[i]; else if (st[i] === 2) d[i] = hi[i]; else free.push(i); }
      if (free.length) {
        const r = b.map((bi, k) => bi - A[k].reduce((s, a, j) => s + a * d[j], 0));
        const Af = A.map((row) => free.map((j) => row[j]));
        const H = this.mm(this.T(Af), Af).map((row, i) => row.map((x, j) => x + (i === j ? lam * lam : 0)));
        const x = this.mv(this.inv(H), this.mv(this.T(Af), r));
        free.forEach((j, k) => { d[j] = x[k]; });
      }
      if (d.some((v, i) => v < lo[i] - 1e-12 || v > hi[i] + 1e-12)) continue;
      const res = A.map((row, k) => row.reduce((s, a, j) => s + a * d[j], 0) - b[k]);
      const g = [0, 1, 2].map((i) => A.reduce((s, row, k) => s + row[i] * res[k], 0) + lam * lam * d[i]);
      if (st.every((s, i) => s === 0 || (s === 1 && g[i] >= -1e-12) || (s === 2 && g[i] <= 1e-12))) return d;
    }
    return [0, 0, 0];
  },
  prioStep(J1, e1, J2, e2, mu, kp) {   // Δθ = J₁⁺e₁ + (J₂N₁)#(k_p e₂ − J₂J₁⁺e₁)，两部分各自限幅 0.2 rad
    const J1p = this.T(this.mm(this.inv(this.mm(J1, this.T(J1)).map((r, i) => r.map((x, j) => x + (i === j ? 1e-14 : 0)))), J1));
    const d1 = this.mv(J1p, e1);
    const N1 = [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) - J1p[i].reduce((s, a, k) => s + a * J1[k][j], 0)));
    const B = this.mm(J2, N1), rhs = e2.map((x, k) => kp * x - J2[k].reduce((s, a, j) => s + a * d1[j], 0));
    const d2 = this.dampedPinvTimes(B, rhs, mu);
    const lim = (v) => { const m = Math.max(...v.map(Math.abs)); return m > 0.2 ? v.map((x) => x * 0.2 / m) : v; };
    const a = lim(d1), c = lim(d2);
    return [0, 1, 2].map((i) => a[i] + c[i]);
  },
  // ---------------- 机器人场景
  goalPose(api) { return [api.p.x, api.p.y, this.rad(api.p.phi)]; },
  err(api, th) { const P = this.pts(th, this.L), g = this.goalPose(api), phi = th[0] + th[1] + th[2];
    return [g[0] - P[3][0], g[1] - P[3][1], this.LC * this.wrap(g[2] - phi)]; },
  J3(th) { const J = this.jp(th, this.L); return [J[0], J[1], [this.LC, this.LC, this.LC]]; },
  inLimits(th) { return th.every((t, i) => { const d = this.deg(this.wrap(t)); return d >= this.LO[i] - 1e-7 && d <= this.HI[i] + 1e-7; }); },
  atLimit(th) { return th.some((t, i) => { const d = this.deg(t); return Math.abs(d - this.LO[i]) < 1e-6 || Math.abs(d - this.HI[i]) < 1e-6; }); },
  // 位置任务能达到的朝向范围（式 (14.2.10)）
  phiRange(api) { const [x, y] = [api.p.x, api.p.y], r = Math.hypot(x, y), b = Math.atan2(y, x), L = this.L;
    const c = (r * r + L[2] * L[2] - (L[0] + L[1]) ** 2) / (2 * r * L[2]); if (c > 1) return "none"; if (c <= -1) return "all"; const h = Math.acos(c); return [b - h, b + h]; },
  // ---------------- 生活场景
  cupErr(api, th) { const P = this.pts(th, this.LH); return { pos: [api.p.sx - P[3][0], api.p.sy - P[3][1]], ang: this.wrap(-(th[0] + th[1] + th[2])) }; },

  reset(api, s) {
    s.k = 0; s.clock = 0; s.done = false; s.hist = []; s.stopped = false;
    s.th = (api.scene === "arm" ? this.TH0 : this.THH0).map(this.rad);
    this.measure(api, s);
  },
  measure(api, s) {
    if (api.scene === "arm") {
      const e = this.err(api, s.th);
      s.ep = Math.hypot(e[0], e[1]); s.eo = Math.abs(e[2]) / this.LC; s.en = Math.hypot(...e);
      if (api.p.method !== 3 && s.en < 1e-10) s.done = true;
    } else {
      const c = this.cupErr(api, s.th); s.ep = Math.hypot(...c.pos); s.eo = Math.abs(c.ang); s.en = s.ep;
    }
    s.hist.push([s.k, Math.max(s.ep, 1e-16)]);
  },
  step(api, s) {
    if (s.done) return;
    let d;
    if (api.scene === "arm") {
      const m = api.p.method;
      if (m === 3) {
        const P = this.pts(s.th, this.L), g = this.goalPose(api);
        d = this.prioStep(this.jp(s.th, this.L), [g[0] - P[3][0], g[1] - P[3][1]], [[1, 1, 1]], [this.wrap(g[2] - (s.th[0] + s.th[1] + s.th[2]))], 0.3, 0.1);
      } else {
        const J = this.J3(s.th), e = this.err(api, s.th);
        if (m === 2) d = this.boxLS(J, e, 1e-3, this.LO.map((v, i) => this.rad(v) - s.th[i]), this.HI.map((v, i) => this.rad(v) - s.th[i]));
        else d = this.dampedPinvTimes(J, e, 1e-5);
      }
      s.th = s.th.map((t, i) => t + d[i]);
      if (m === 1) s.th = s.th.map((t, i) => Math.max(this.rad(this.LO[i]), Math.min(this.rad(this.HI[i]), t)));
      if (m === 2) s.th = s.th.map((t, i) => Math.max(this.rad(this.LO[i]), Math.min(this.rad(this.HI[i]), t)));
    } else {
      const c = this.cupErr(api, s.th), Jp = this.jp(s.th, this.LH), Jo = [[1, 1, 1]];
      d = api.p.prim === 0 ? this.prioStep(Jo, [c.ang], Jp, c.pos, 0.1, 0.3) : this.prioStep(Jp, c.pos, Jo, [c.ang], 0.1, 0.3);
      s.th = s.th.map((t, i) => t + d[i]);
    }
    s.k += 1;
    this.measure(api, s);
    if ((api.scene === "cup" || api.p.method === 3) && Math.hypot(...d) < 1e-13) s.done = true;
    if (s.k >= 400) s.done = true;
  },
  action(id, api, s) { if (id === "step") this.step(api, s); },
  update(dt, api, s) {
    s.clock += dt;
    while (s.clock >= this.DT && api.running) { s.clock -= this.DT; this.step(api, s); if (s.done) api.stop(); }
  },
  readouts(api, s) {
    const dg = (t) => this.deg(t).toFixed(1) + "°";
    if (api.scene === "arm") {
      const m = api.p.method, names = [api.T("不管限位", "ignore limits"), api.T("每步截断", "clip each step"), api.T("有界的一步", "bounded step"), api.T("任务优先级", "task priority")];
      const inl = this.inLimits(s.th), phi = this.deg(s.th[0] + s.th[1] + s.th[2]);
      const viol = s.th.map((t, i) => [i + 1, this.deg(this.wrap(t))]).filter(([i, d]) => d < this.LO[i - 1] - 1e-7 || d > this.HI[i - 1] + 1e-7).map(([i]) => i);
      const rg = this.phiRange(api), rgOk = Array.isArray(rg);
      if (s.done && m === 0 && !inl) api.done("free");
      if (m === 1 && s.k >= 150 && !s.done && s.ep > 0.05 && this.atLimit(s.th)) api.done("clamp");
      if (s.done && m === 2 && inl && s.en < 1e-10) api.done("box");
      const gd = this.rad(api.p.phi);
      if (s.done && m === 3 && rgOk && s.ep < 1e-9 && (gd > rg[1] || gd < rg[0])) {
        const near = Math.abs(gd - rg[1]) < Math.abs(gd - rg[0]) ? rg[1] : rg[0];
        if (Math.abs(this.wrap(this.rad(phi) - near)) < this.rad(0.05)) api.done("prio");
      }
      const status = s.done ? (s.en < 1e-10 || m === 3 ? api.T("结束", "finished") : api.T("到达次数上限", "iteration limit")) : api.running ? api.T("迭代中", "iterating") : "—";
      return [[["做法", "method"], names[m]], [["迭代次数 k", "iteration k"], String(s.k)],
              [["位置误差", "position error"], (s.ep * 1000).toExponential(2) + " mm"], [["工具朝向 φ", "tool angle φ"], phi.toFixed(2) + "°"],
              [["θ₁, θ₂, θ₃（化到 ±180° 以内）", "θ₁, θ₂, θ₃ (within ±180°)"], s.th.map((t) => dg(this.wrap(t))).join(", ")],
              [["超出限位的关节", "joints beyond limits"], viol.length ? viol.join(", ") : api.T("无", "none")],
              [["可行的朝向范围（只给位置时）", "feasible tool angles (position only)"], rgOk ? `${this.deg(rg[0]).toFixed(1)}° … ${this.deg(rg[1]).toFixed(1)}°` : rg === "all" ? api.T("任意", "any") : api.T("够不着", "out of reach")],
              [["状态", "status"], status]];
    }
    const tilt = this.deg(s.eo);
    if (s.done && api.p.prim === 0 && tilt < 0.01 && s.ep > 0.05) api.done("cup");
    return [[["主任务", "primary task"], api.p.prim === 0 ? api.T("杯子竖直", "cup level") : api.T("手到架子", "hand on shelf")], [["迭代次数 k", "iteration k"], String(s.k)],
            [["杯子倾斜", "cup tilt"], tilt.toFixed(3) + "°"], [["手离架子", "hand to shelf"], (s.ep * 1000).toFixed(1) + " mm"],
            [["肩、肘、腕", "shoulder, elbow, wrist"], s.th.map(dg).join(", ")], [["状态", "status"], s.done ? api.T("结束", "finished") : api.running ? api.T("迭代中", "iterating") : "—"]];
  },
  draw(api, s) {
    const { w, h, ctx } = api, arm = api.scene === "arm";
    const sc = arm ? Math.min(w * 0.5 / 1.0, h * 0.85 / 1.0) : Math.min(w * 0.5 / 0.75, h * 0.8 / 0.95);
    const ox = arm ? w * 0.1 : w * 0.18, oy = arm ? h * 0.55 : h * 0.8, X = (p) => [ox + sc * p[0], oy - sc * p[1]];
    const L = arm ? this.L : this.LH, P = this.pts(s.th, L).map(X);
    if (arm) {
      // 关节限位扇形（相对前一连杆的方向）
      let a = 0;
      for (let i = 0; i < 3; i++) {
        const lo = a + this.rad(this.LO[i]), hi = a + this.rad(this.HI[i]), r = i === 0 ? 46 : i === 1 ? 36 : 22;
        ctx.fillStyle = "rgba(31,111,235,0.10)"; ctx.beginPath(); ctx.moveTo(P[i][0], P[i][1]); ctx.arc(P[i][0], P[i][1], r, -hi, -lo); ctx.closePath(); ctx.fill();
        a += s.th[i];
      }
      const g = this.goalPose(api), G = X(g);
      api.circle(G[0], G[1], 6, api.css("--red"));
      api.arrow(G[0], G[1], G[0] + 50 * Math.cos(g[2]), G[1] - 50 * Math.sin(g[2]), api.css("--red"), 2);
      ctx.strokeStyle = api.css("--grid"); ctx.setLineDash([4, 4]); ctx.beginPath(); ctx.arc(ox, oy, sc * (L[0] + L[1]), -1.2, 1.2); ctx.stroke(); ctx.setLineDash([]);
    } else {
      const S = X([api.p.sx, api.p.sy]);
      api.rect(S[0] - 6, S[1] + 2, 90, 7, api.css("--amber"));
      api.label(api.T("架子", "shelf"), S[0] + 10, S[1] + 22, api.css("--muted"), 12);
      api.circle(ox - 22, oy - 46, 18, null, api.css("--muted"));                    // 人：头和躯干（肩在 P[0]）
      api.line(ox - 22, oy - 26, ox - 22, oy + 80, api.css("--muted"), 4); api.line(ox - 22, oy - 4, ox, oy, api.css("--muted"), 3);
    }
    if (arm) api.rect(P[0][0] - 14, P[0][1] + 6, 28, 9, api.css("--muted"));
    const viol = arm ? s.th.map((t, i) => { const d = this.deg(this.wrap(t)); return d < this.LO[i] - 1e-7 || d > this.HI[i] + 1e-7; }) : [false, false, false];
    for (let i = 0; i < 3; i++) api.line(P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], api.css("--blue"), [10, 8, 5][i]);
    for (let i = 0; i < 3; i++) api.circle(P[i][0], P[i][1], 5, viol[i] ? api.css("--red") : api.css("--panel"), api.css("--ink"));
    if (!arm) {   // 杯子：画在手上，杯口与手的方向垂直
      const a = s.th[0] + s.th[1] + s.th[2], e = P[3], u = [Math.cos(a), -Math.sin(a)], n = [-u[1], u[0]];
      const q = (t, k) => [e[0] + u[0] * t + n[0] * k, e[1] + u[1] * t + n[1] * k];
      ctx.fillStyle = "rgba(88,166,255,0.35)"; ctx.strokeStyle = api.css("--ink"); ctx.lineWidth = 1.5; ctx.beginPath();
      [q(-12, 0), q(12, 0), q(14, -34), q(-14, -34)].forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.closePath(); ctx.fill(); ctx.stroke();
    }
    const g = api.graph({ x: w * 0.66, y: h * 0.1, w: w * 0.3, h: h * 0.42, xmin: 0, xmax: Math.max(20, s.k), ymin: -16, ymax: 0,
                          xlabel: api.T("迭代次数 k", "iteration k"), ylabel: api.T("lg（位置误差 / m）", "lg(position error / m)") }).axes();
    g.pts(s.hist.map(([k, e]) => [k, Math.log10(e)]), api.css("--accent"), 2);
  },
});
