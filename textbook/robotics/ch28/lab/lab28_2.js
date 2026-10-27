// 实验 28.2 推一下、走几步：线性倒立摆（配 28.2 节）。平面问题，质心保持高度 z_c，ẍ = ω₀²(x − x_Z)，ω₀ = √(𝔤/z_c)（式 (28.2.4)）。
// 场景“推一下”（G1）：脚掌在踝关节前 125 mm、后 55 mm（与算例 28.2.1 相同），质心起初在踝关节前 3.3 mm，被推到速度 v。
//   平衡策略：零力矩点放到捕获点 ξ = x + ẋ/ω₀（式 (28.2.7)）上，但不能超出脚掌；选“迈步”时，0.2 s 后把新的脚放到
//   离原来的脚 d 处（踝关节到踝关节），之后零力矩点在新脚的脚掌内。3 s 后质心速度小于 0.02 m/s 判为站住，质心离支撑脚超过 0.6 m 判为摔倒。
// 生活场景“人被推了一下”：质心高 1.0 m，脚掌在踝前 0.20 m、后 0.05 m（示意值）。
// 场景“步行”（G1）：俯视。零力矩点在两脚中线（离身体中线 118.5 mm）之间左右换，双脚支撑时直线移动；质心取有界解（式 (28.2.8)），
//   用一个周期的零力矩点重复多次后与核 (ω₀/2)e^{−ω₀|t|} 卷积求出。
// 由 ex28_2.py 核算：G1 ω₀ = 3.766 rad/s，不迈步能承受 0.458 m/s；每步 0.6 s、双脚支撑 0.1 s 时侧向摆幅 48.9 mm，每步 0.4 s（不计双脚支撑）27.2 mm。
WQ.lab({
  title: ["实验 28.2 推一下、走几步：线性倒立摆", "Lab 28.2 A push and a few steps: the linear inverted pendulum"],
  goal: ["用线性倒立摆研究平衡：被推以后什么时候站得住、什么时候必须迈步、迈到哪里；走路时质心怎样随零力矩点左右摆。",
         "Use the linear inverted pendulum to study balance: when a robot can stand after a push, when it must step and where to, and how the CoM sways with the ZMP while walking."],
  scenes: [
    { id: "push", robot: true, name: ["G1 被推了一下", "G1 is pushed"], hide: ["T", "TD"],
      problem: { title: ["机器人问题：G1 被人碰了一下，会不会倒", "Robot problem: G1 gets bumped—does it fall"],
                 text: ["G1 站在装配线旁，被路过的小车碰了一下。不迈步能承受多大的推力？推得更重时，脚要迈到哪里？",
                        "G1 stands by the assembly line and a passing trolley bumps it. How hard a push can it take without stepping? If pushed harder, where must it step?"] } },
    { id: "person", name: ["生活：人被推了一下", "Everyday: a person is pushed"], hide: ["T", "TD"], params: { zc: { value: 1.0 } },
      problem: { title: ["生活中的例子：被推了一下，踉跄一步", "Everyday example: pushed, you stagger a step"],
                 text: ["人被从背后推了一下，轻的站得住，重的要往前迈一步。迈多远才站得住？",
                        "Pushed from behind, a person stands firm after a light push but must step after a harder one. How far must the step be?"] } },
    { id: "walk", robot: true, name: ["G1 步行（俯视）", "G1 walking (top view)"], hide: ["v", "step", "d", "zc"],
      problem: { title: ["机器人问题：走路时身体要左右晃多少", "Robot problem: how much must the body sway while walking"],
                 text: ["G1 搬着零件走路，晃得太厉害零件会掉。怎样选每步的时间和双脚支撑的时间，让身体少晃？",
                        "G1 walks carrying parts; too much sway and the parts fall. How should the step time and double-support time be chosen to sway less?"] } },
  ],
  params: [
    { id: "v", name: ["被推后的速度 v", "Speed after the push v"], min: 0, max: 1.2, step: 0.01, value: 0.3, unit: "m/s", digits: 2 },
    { id: "step", name: ["迈步（0 不迈，1 迈）", "Step (0 no, 1 yes)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "d", name: ["迈步距离 d（踝到踝）", "Step length d (ankle to ankle)"], min: 0, max: 0.6, step: 0.01, value: 0.25, unit: "m", digits: 2 },
    { id: "zc", name: ["质心高度 z_c", "CoM height z_c"], min: 0.4, max: 1.2, step: 0.001, value: 0.692, unit: "m", digits: 3 },
    { id: "T", name: ["每步时间", "Step time"], min: 0.3, max: 1.2, step: 0.05, value: 0.6, unit: "s", digits: 2 },
    { id: "TD", name: ["双脚支撑时间", "Double-support time"], min: 0, max: 0.3, step: 0.02, value: 0.1, unit: "s", digits: 2 },
  ],
  legend: [{ color: "#2ca02c", name: ["零力矩点", "ZMP"] }, { color: "#d62728", name: ["捕获点", "capture point"] }, { color: "#b8860b", name: ["质心", "centre of mass"] }],
  G: 9.81, YF: 0.1185,
  foot(api) { return api.scene === "person" ? { toe: 0.20, heel: -0.05, x0: 0.03 } : { toe: 0.125, heel: -0.055, x0: 0.0033 }; },
  reset(api, s) {
    const w0 = Math.sqrt(this.G / api.p.zc);
    s.w0 = w0; s.t = 0; s.fin = false; s.res = "";
    if (api.scene === "walk") { this.walk(api, s); return; }
    const F = this.foot(api);
    s.x = F.x0; s.v = api.p.v; s.foot = 0; s.stepped = false; s.hist = []; s.p = s.x; s.xi = s.x + s.v / w0;
  },
  walk(api, s) {                                  // 一个周期（两步）的零力矩点，重复 9 个周期后卷积，取中间一个周期
    const T = api.p.T, TD = Math.min(api.p.TD, T * 0.9), dt = 0.002, YF = this.YF, w0 = s.w0;
    const n = Math.round(2 * T / dt), py = [];
    for (let k = 0; k < n; k++) {
      const t = k * dt, j = Math.floor(t / T), tau = t - j * T, side = j % 2 === 0 ? 1 : -1;
      py.push(tau < TD ? -side * YF + (tau / TD) * 2 * side * YF : side * YF);
    }
    const rep = 9, all = []; for (let r = 0; r < rep; r++) all.push(...py);
    const e = Math.exp(-w0 * dt), c0 = 1 - (1 - e) / (w0 * dt), c1 = (1 - e) / (w0 * dt) - e;
    const N = all.length, fw = new Array(N), bw = new Array(N);
    fw[0] = all[0]; for (let k = 1; k < N; k++) fw[k] = e * fw[k - 1] + c1 * all[k - 1] + c0 * all[k];
    bw[N - 1] = all[N - 1]; for (let k = N - 2; k >= 0; k--) bw[k] = e * bw[k + 1] + c1 * all[k + 1] + c0 * all[k];
    const mid = Math.floor(rep / 2) * n;
    s.py = py; s.yc = []; for (let k = 0; k < n; k++) s.yc.push((fw[mid + k] + bw[mid + k]) / 2);
    s.sway = Math.max(...s.yc.map(Math.abs)); s.dtw = dt;
    s.formula = YF * (1 - 1 / Math.cosh(w0 * T / 2));
    if (s.sway < 0.040) api.done("sway");
  },
  update(dt, api, s) {
    if (api.scene === "walk") { s.t += dt; return; }
    if (s.fin) { api.stop(); return; }
    const F = this.foot(api), h = 0.001, n = Math.max(1, Math.round(dt / h)), w0 = s.w0;
    for (let k = 0; k < n && !s.fin; k++) {
      if (api.p.step > 0.5 && !s.stepped && s.t >= 0.2) { s.foot += api.p.d; s.stepped = true; }
      s.xi = s.x + s.v / w0;
      s.p = Math.min(Math.max(s.xi, s.foot + F.heel), s.foot + F.toe);
      s.v += w0 * w0 * (s.x - s.p) * h;
      s.x += s.v * h;
      s.t += h;
      if (Math.round(s.t / h) % 10 === 0) s.hist.push([s.t, s.x, s.p, s.xi, s.v]);
      if (Math.abs(s.x - s.foot) > 0.6) { s.fin = true; s.res = "fall"; }
      else if (s.t >= 3.0) { s.fin = true; s.res = Math.abs(s.v) < 0.02 ? "stand" : "fall"; }
    }
    if (s.fin) {
      if (s.res === "stand" && api.scene === "push" && api.p.step < 0.5 && api.p.v >= 0.42 && Math.abs(api.p.zc - 0.692) < 0.002) api.done("nostep");
      if (s.res === "stand" && api.scene === "push" && api.p.step > 0.5 && api.p.v >= 0.8 && Math.abs(api.p.zc - 0.692) < 0.002) api.done("step");
      api.stop();
    }
  },
  draw(api, s) {
    const { w, h } = api, ctx = api.ctx;
    if (api.scene === "walk") {
      // 上：侧向位置随时间（两个周期）；下：俯视路线
      const T = api.p.T, n = (s.py || []).length, dt = s.dtw || 0.002, YF = this.YF;
      const x0 = 50, x1 = w - 20, y0 = 20, y1 = h * 0.5;
      const X = (t) => x0 + (t / (2 * T * 2)) * (x1 - x0), Y = (y) => (y0 + y1) / 2 - y / (YF * 1.3) * (y1 - y0) / 2;
      api.line(x0, Y(0), x1, Y(0), "#bbb", 1);
      [[s.py, "#2ca02c"], [s.yc, "#b8860b"]].forEach(([arr, col]) => {
        if (!arr) return;
        ctx.strokeStyle = col; ctx.lineWidth = 2.5; ctx.beginPath();
        for (let r = 0; r < 2; r++) arr.forEach((y, k) => { const t = (r * n + k) * dt; (r === 0 && k === 0) ? ctx.moveTo(X(t), Y(y)) : ctx.lineTo(X(t), Y(y)); });
        ctx.stroke();
      });
      const tt = (s.t || 0) % (2 * T), k = Math.min(n - 1, Math.floor(tt / dt));
      if (s.yc) { api.circle(X(tt), Y(s.yc[k]), 6, "#b8860b"); api.circle(X(tt), Y(s.py[k]), 5, "#2ca02c"); }
      api.label(api.T("侧向位置随时间（两步一个周期）", "sideways position against time (two steps per cycle)"), x0, y0 - 6, "#555", 12);
      // 俯视：脚印、零力矩点与质心
      const SL = 0.2, vx = SL / T, sc = (x1 - x0) / (4 * SL + 0.3), oy = h * 0.78;
      const Xs = (x) => x0 + x * sc, Ys = (y) => oy - y * sc;
      for (let j = 0; j < 4; j++) { const side = j % 2 === 0 ? 1 : -1; api.rect(Xs(j * SL - 0.055), Ys(side * YF + 0.03), 0.18 * sc, 0.06 * sc, side > 0 ? "rgba(31,119,180,0.25)" : "rgba(214,39,40,0.25)"); }
      ctx.strokeStyle = "#b8860b"; ctx.lineWidth = 2.5; ctx.beginPath();
      if (s.yc) for (let r = 0; r < 2; r++) s.yc.forEach((y, k) => { const t = (r * n + k) * dt, x = vx * t; (r === 0 && k === 0) ? ctx.moveTo(Xs(x), Ys(y)) : ctx.lineTo(Xs(x), Ys(y)); });
      ctx.stroke();
      api.label(api.T(`侧向摆幅 ±${api.fmt((s.sway || 0) * 1000, 1)} mm`, `sideways sway ±${api.fmt((s.sway || 0) * 1000, 1)} mm`), w * 0.98, h * 0.55, s.sway < 0.04 ? "#2ca02c" : "#d62728", 16, "right");
      return;
    }
    const F = this.foot(api), zc = api.p.zc, gy = h * 0.82, sc = Math.min(h * 0.65 / zc, w / 2.2), ox = w * 0.25;
    const X = (x) => ox + x * sc;
    api.ground(gy, w);
    const drawFoot = (fx, col) => api.rect(X(fx + F.heel), gy - 8, (F.toe - F.heel) * sc, 8, col, "#1f3a5f", 2);
    if (s.stepped) drawFoot(0, "rgba(150,150,150,0.25)");
    drawFoot(s.foot || 0, "rgba(31,119,180,0.5)");
    const cx = X(s.x ?? 0), cy = gy - zc * sc;
    api.line(X(s.p ?? 0), gy, cx, cy, "#666", 3);
    api.circle(cx, cy, 12, "#b8860b");
    api.circle(X(s.p ?? 0), gy + 6, 5, "#2ca02c");
    api.circle(X(s.xi ?? 0), gy + 16, 5, "#d62728");
    api.label(api.T("零力矩点", "ZMP"), X(s.p ?? 0), gy + 30, "#2ca02c", 12, "center");
    api.label(api.T("捕获点", "capture pt"), X(s.xi ?? 0), gy + 44, "#d62728", 12, "center");
    const msg = s.res === "stand" ? api.T("站住了", "stands") : s.res === "fall" ? api.T("摔倒了", "falls") : "";
    if (msg) api.label(msg, w * 0.8, h * 0.12, s.res === "stand" ? "#2ca02c" : "#d62728", 20, "center");
    // 相平面小图
    const H = s.hist || [], px = w * 0.62, py = h * 0.18, pw = w * 0.34, ph = h * 0.36;
    api.plot(px, py, pw, ph, [{ pts: H.map((r) => [r[1] - r[2], r[4]]), color: "#1f77b4" },
      { pts: [[-0.3, 0.3 * s.w0], [0.1, -0.1 * s.w0]], color: "#bbb" }, { pts: [[-0.3, -0.3 * s.w0], [0.1, 0.1 * s.w0]], color: "#bbb" }],
      { xmin: -0.3, xmax: 0.1, ymin: -0.5, ymax: 1.3, xlabel: "x − x_Z / m", ylabel: "ẋ / (m/s)" });
  },
  readouts(api, s) {
    const f = (v, k = 3) => api.fmt(v, k);
    if (api.scene === "walk")
      return [
        [["ω₀ = √(𝔤/z_c)", "ω₀ = √(𝔤/z_c)"], f(s.w0, 3) + " rad/s"],
        [["质心的侧向摆幅", "Sideways sway of the CoM"], `±${f(s.sway * 1000, 1)} mm`],
        [["不计双脚支撑的公式 y_f(1 − 1/cosh(ω₀T/2))", "Formula without double support y_f(1 − 1/cosh(ω₀T/2))"], `±${f(s.formula * 1000, 1)} mm`],
        [["零力矩点的侧向位置", "Sideways ZMP position"], `±${f(this.YF * 1000, 1)} mm`],
      ];
    const F = this.foot(api);
    return [
      [["结果", "Result"], s.res === "stand" ? api.T("站住了", "stands") : s.res === "fall" ? api.T("摔倒了", "falls") : "—"],
      [["ω₀ 与时间常数 1/ω₀", "ω₀ and time constant 1/ω₀"], `${f(s.w0, 3)} rad/s，${f(1000 / s.w0, 0)} ms`],
      [["推后瞬间的捕获点（相对踝关节）", "Capture point right after the push (from the ankle)"], f((F.x0 + api.p.v / s.w0) * 1000, 0) + " mm"],
      [["脚尖 / 脚跟（相对踝关节）", "Toe / heel (from the ankle)"], `${f(F.toe * 1000, 0)} / ${f(F.heel * 1000, 0)} mm`],
      [["不迈步能承受的最大速度 ω₀(脚尖 − x₀)", "Largest push without a step ω₀(toe − x₀)"], f(s.w0 * (F.toe - F.x0), 3) + " m/s"],
      [["质心、零力矩点、捕获点", "CoM, ZMP, capture point"], `${f(s.x, 3)}，${f(s.p, 3)}，${f(s.xi, 3)} m`],
    ];
  },
  tasks: [
    { id: "nostep", robot: true, text: ["不迈步，找出 G1 能站住的最大推后速度（不低于 0.42 m/s），与算例 28.2.3 的 0.458 m/s 比较。",
                                       "Without stepping, find the largest push G1 survives (at least 0.42 m/s) and compare with 0.458 m/s from Example 28.2.3."],
      demo: { scene: "push", set: { v: 0.44, step: 0, d: 0.25, zc: 0.692 }, wait: 4 } },
    { id: "step", robot: true, text: ["G1 被推到 0.8 m/s（或更快）：打开迈步，调迈步距离，让它站住。", "G1 is pushed to 0.8 m/s or more: switch on stepping and choose the step length so that it stands."],
      demo: { scene: "push", set: { v: 0.8, step: 1, d: 0.3, zc: 0.692 }, wait: 4 } },
    { id: "sway", robot: true, text: ["步行场景：调每步时间和双脚支撑时间，使质心的侧向摆幅小于 40 mm。", "Walking scene: choose the step time and the double-support time so that the CoM sways less than 40 mm sideways."],
      demo: { scene: "walk", set: { T: 0.45, TD: 0.1 }, press: ["reset"], wait: 1 } },
  ],
  think: ["线性倒立摆假定零力矩点可以瞬间移到脚掌内任何地方，迈步也是瞬间完成的。实际的机器人哪些地方做不到？这会让能承受的推力变大还是变小？",
          "The linear inverted pendulum assumes the ZMP can jump anywhere in the foot instantly and a step takes no time. What can a real robot not do here, and does that make the survivable push larger or smaller?"],
});
