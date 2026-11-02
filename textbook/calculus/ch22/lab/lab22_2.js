// 实验 22.2 自己写 RK4：单关节机械臂的仿真（配 22.1—22.5 节）。“机械臂”场景：UR5e 上臂（8.393 kg，质心 0.2125 m，
// 绕肩轴 0.5129 kg·m²）松开制动后自由摆动，I θ″ = −m g d cos θ；读者选积分方法（欧拉、半隐式欧拉 = MuJoCo 的默认积分器、
// 休恩、RK4）和步长，与细步长参考解比较角度误差和能量误差。“刚性方程”场景：y′ = −λ(y − cos t)，显式欧拉、隐式欧拉、RK4 的稳定性。
WQ.lab({
  title: ["实验 22.2 自己写 RK4：单关节机械臂的仿真", "Lab 22.2 Write your own RK4: simulating a one-joint arm"],
  goal: ["亲手比较几种数值积分方法：误差怎样随步长变化（阶数），同样的计算量谁更准，长时间仿真时能量会不会漂走；再看刚性方程中显式方法的步长限制和隐式方法的优势。",
         "Compare numerical integrators hands-on: how the error scales with the step (the order), which is most accurate for the same work, whether energy drifts in long runs; then see the step limit of explicit methods on stiff equations and the advantage of implicit ones."],
  scenes: [
    { id: "arm", robot: true, name: ["机械臂自由摆动", "Arm swinging freely"], hide: ["lam", "sm", "sh"],
      problem: { title: ["机器人问题：仿真器里的机械臂，步长取多大才可信？", "Robot problem: how large a step can an arm simulator take and still be trusted?"],
                 text: ["UR5e 的上臂（零件库数据：8.393 kg，质心离肩轴 0.2125 m，绕肩轴转动惯量 0.5129 kg·m²）从初始角度松开制动、不计摩擦地自由摆动。选积分方法和步长 h，灰线是细步长参考解。方法 2 的半隐式欧拉法就是 MuJoCo 物理引擎的默认积分器（程序 22.5.1 逐步核对过）。",
                        "The UR5e upper arm (catalogue data: 8.393 kg, centre of mass 0.2125 m from the shoulder axis, 0.5129 kg·m² about it) is released from an initial angle and swings freely without friction. Choose the method and step h; the grey curve is a fine-step reference. Method 2, semi-implicit Euler, is the MuJoCo physics engine's default integrator (checked step by step in Program 22.5.1)."] } },
    { id: "stiff", name: ["刚性方程", "Stiff equation"], hide: ["m", "h", "T", "th0"],
      problem: { title: ["为什么快过程会逼着显式方法用小步长？", "Why does a fast process force explicit methods to take tiny steps?"],
                 text: ["y′ = −λ(y − cos t)，y(0) = 0。解很快（时间常数 1/λ）贴到 cos t 上，之后变化很慢。显式欧拉要求 hλ < 2，RK4 要求 hλ < 2.785；隐式欧拉对任何步长都稳定。",
                        "y′ = −λ(y − cos t), y(0) = 0. The solution quickly (time constant 1/λ) settles onto cos t and then changes slowly. Explicit Euler needs hλ < 2, RK4 needs hλ < 2.785; implicit Euler is stable for any step."] } },
  ],
  params: [
    { id: "m", name: ["方法：1 欧拉，2 半隐式欧拉（MuJoCo 默认），3 休恩，4 RK4", "Method: 1 Euler, 2 semi-implicit Euler (MuJoCo default), 3 Heun, 4 RK4"], min: 1, max: 4, step: 1, value: 4, digits: 0 },
    { id: "h", name: ["步长 h", "Step h"], min: 0.5, max: 100, step: 0.5, value: 20, unit: "ms", digits: 1 },
    { id: "T", name: ["仿真时长", "Simulated time"], min: 1, max: 60, step: 1, value: 2, unit: "s", digits: 0 },
    { id: "th0", name: ["初始角度（从水平向上为正）", "Initial angle (up from horizontal)"], min: -80, max: 80, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "sm", name: ["方法：1 显式欧拉，2 隐式欧拉，3 RK4", "Method: 1 explicit Euler, 2 implicit Euler, 3 RK4"], min: 1, max: 3, step: 1, value: 1, digits: 0 },
    { id: "lam", name: ["λ（快过程的速率）", "λ (rate of the fast process)"], min: 10, max: 5000, step: 10, value: 1000, unit: "1/s", digits: 0 },
    { id: "sh", name: ["步长 h", "Step h"], min: 0.1, max: 100, step: 0.1, value: 1, unit: "ms", digits: 1 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["参考解", "reference"], color: "#7a868d" }, { name: ["所选方法", "chosen method"], color: "#1f77b4" }, { name: ["能量误差", "energy error"], color: "#d62728" }],
  tasks: [
    { id: "rk4", robot: true, text: ["RK4，从水平位置释放，仿真 2 s：找出使全程最大角度误差小于 10⁻⁴ rad 的最大步长（可以取到 35 ms 以上）。同样的步长下欧拉法的误差有多大？",
                                     "RK4, released from horizontal, 2 s: find the largest step that keeps the maximum angle error below 10⁻⁴ rad (it can be 35 ms or more). How large is Euler's error at the same step?"],
      demo: { scene: "arm", set: { m: 4, h: 38, T: 2, th0: 0 }, wait: 1 } },
    { id: "order", text: ["休恩法、仿真 2 s：步长 10 ms 时记下最大误差，再减半到 5 ms。误差缩小到约几分之一？RK4 呢？",
                          "Heun, 2 s: note the maximum error at h = 10 ms, then halve the step to 5 ms. By about what factor does the error shrink? And for RK4?"],
      demo: { scene: "arm", set: { m: 3, h: 5, T: 2, th0: 0 }, wait: 1 } },
    { id: "energy", robot: true, text: ["步长 10 ms，仿真 60 s：欧拉法的能量误差怎样变化？换成半隐式欧拉（MuJoCo 的默认积分器），能量误差能保持在摆动能量的 5% 以内吗？",
                                        "h = 10 ms, 60 s: how does Euler's energy error evolve? Switch to semi-implicit Euler (MuJoCo's default): does the energy error stay within 5% of the swing energy?"],
      demo: { scene: "arm", set: { m: 2, h: 10, T: 60, th0: 0 }, wait: 1 } },
    { id: "stiffeu", text: ["刚性方程，λ = 1000：显式欧拉的步长超过多少就发散？换成隐式欧拉，用 h = 20 ms（hλ = 20）也能使 t = 1 处误差小于 10⁻⁴。",
                            "Stiff equation, λ = 1000: beyond what step does explicit Euler diverge? Switch to implicit Euler: even h = 20 ms (hλ = 20) gives an error below 10⁻⁴ at t = 1."],
      demo: { scene: "stiff", set: { sm: 2, lam: 1000, sh: 20 }, wait: 1 } },
    { id: "stiffrk", text: ["刚性方程，λ = 1000，RK4：找出仍然稳定的最大步长（应在 2.7 ms 以上）。它比显式欧拉大多少？每一步的计算量呢？",
                            "Stiff equation, λ = 1000, RK4: find the largest step that is still stable (above 2.7 ms). How much larger than explicit Euler's? And the work per step?"],
      demo: { scene: "stiff", set: { sm: 3, lam: 1000, sh: 2.7 }, wait: 1 } },
  ],
  think: ["RK4 的误差比半隐式欧拉小几个数量级，为什么 MuJoCo 等物理引擎默认还是用半隐式欧拉？（提示：接触和碰撞使方程不光滑；能量的长期行为；每步的计算量。）",
          "RK4's error is orders of magnitude smaller than semi-implicit Euler's, so why do physics engines such as MuJoCo default to semi-implicit Euler? (Hints: contacts and impacts make the equations non-smooth; long-term energy behaviour; work per step.)"],

  M: 8.393, D: 0.2125, I: 0.5129, G: 9.81,
  NAMES: [["欧拉", "Euler"], ["半隐式欧拉", "semi-implicit Euler"], ["休恩", "Heun"], ["RK4", "RK4"]],
  EVALS: [1, 1, 2, 4],
  step(m, q, v, h) {
    const c = this.M * this.G * this.D / this.I, a = (x) => -c * Math.cos(x);
    if (m === 1) return [q + h * v, v + h * a(q)];
    if (m === 2) { const v1 = v + h * a(q); return [q + h * v1, v1]; }
    if (m === 3) { const k1 = [v, a(q)], k2 = [v + h * k1[1], a(q + h * k1[0])]; return [q + h / 2 * (k1[0] + k2[0]), v + h / 2 * (k1[1] + k2[1])]; }
    const F = (x, y) => [y, a(x)];
    const k1 = F(q, v), k2 = F(q + h / 2 * k1[0], v + h / 2 * k1[1]), k3 = F(q + h / 2 * k2[0], v + h / 2 * k2[1]), k4 = F(q + h * k3[0], v + h * k3[1]);
    return [q + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]), v + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])];
  },
  arm(p) {   // 缓存：参数不变就不重算
    const key = [p.m, p.h, p.T, p.th0].join(",");
    if (this._ak === key) return this._ad;
    const c = this.M * this.G * this.D / this.I, h = p.h / 1000, n = Math.round(p.T / h), sub = Math.max(1, Math.ceil(h / 1e-4)), hr = h / sub;
    const E = (q, v) => (0.5 * v * v + c * Math.sin(q)) / c;   // 以 m g d / I 为单位
    let q = p.th0 * Math.PI / 180, v = 0, qr = q, vr = 0;
    const E0 = E(q, v), ts = [0], qs = [q], qrs = [qr], es = [0];
    let maxerr = 0, maxdE = 0, blown = false;
    for (let k = 1; k <= n; k++) {
      [q, v] = this.step(p.m, q, v, h);
      for (let j = 0; j < sub; j++) [qr, vr] = this.step(4, qr, vr, hr);
      if (!isFinite(q) || Math.abs(v) > 1e4) { blown = true; break; }
      const err = Math.abs(q - qr), dE = E(q, v) - E0;
      maxerr = Math.max(maxerr, err); maxdE = Math.max(maxdE, Math.abs(dE));
      ts.push(k * h); qs.push(q); qrs.push(qr); es.push(dE);
    }
    this._ak = key;
    this._ad = { ts, qs, qrs, es, maxerr, maxdE, endE: es[es.length - 1], n, blown, evals: n * this.EVALS[p.m - 1] };
    return this._ad;
  },
  stiff(p) {
    const lam = p.lam, h = p.sh / 1000, n = Math.round(1 / h);
    const ex = (t) => (lam * lam * Math.cos(t) + lam * Math.sin(t)) / (lam * lam + 1) - lam * lam / (lam * lam + 1) * Math.exp(-lam * t);
    const f = (t, y) => -lam * (y - Math.cos(t));
    let y = 0, t = 0, blown = false;
    const pts = [[0, 0]];
    for (let k = 1; k <= n; k++) {
      if (p.sm === 1) y = y + h * f(t, y);
      else if (p.sm === 2) y = (y + h * lam * Math.cos(t + h)) / (1 + h * lam);
      else {
        const k1 = f(t, y), k2 = f(t + h / 2, y + h / 2 * k1), k3 = f(t + h / 2, y + h / 2 * k2), k4 = f(t + h, y + h * k3);
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4);
      }
      t = k * h;
      if (!isFinite(y) || Math.abs(y) > 1e6) { blown = true; break; }
      pts.push([t, y]);
    }
    const err = blown ? Infinity : Math.abs(y - ex(t));
    return { pts, err, blown: blown || err > 1, ex, n, hl: h * lam, tEnd: t };
  },
  reset() {},
  readouts(api) {
    const p = api.p;
    if (api.scene === "arm") {
      const R = this.arm(p);
      if (p.m === 4 && p.th0 === 0 && p.T === 2 && p.h >= 35 && !R.blown && R.maxerr < 1e-4) api.done("rk4");
      if (p.m === 3 && p.th0 === 0 && p.T === 2 && p.h === 5) api.done("order");
      if (p.m === 2 && p.h === 10 && p.T === 60 && !R.blown && R.maxdE < 0.05) api.done("energy");
      return [[["方法", "method"], api.T(...this.NAMES[p.m - 1]) + api.T("（每步 ", " (") + this.EVALS[p.m - 1] + api.T(" 次求值）", " evaluations per step)")],
              [["步数 / 求值次数", "steps / evaluations"], R.n + " / " + R.evals],
              [["全程最大角度误差", "max angle error"], R.blown ? api.T("发散", "diverged") : R.maxerr.toExponential(2) + " rad"],
              [["末了的角度：所选方法 / 参考", "final angle: method / reference"], R.blown ? "—" : (R.qs[R.qs.length - 1] * 180 / Math.PI).toFixed(3) + "° / " + (R.qrs[R.qrs.length - 1] * 180 / Math.PI).toFixed(3) + "°"],
              [["能量误差：最大 / 末了（单位 m g d）", "energy error: max / final (unit m g d)"], R.blown ? "—" : R.maxdE.toExponential(2) + " / " + R.endE.toExponential(2)]];
    }
    const S = this.stiff(p);
    if (p.sm === 2 && p.lam === 1000 && p.sh >= 20 && S.err < 1e-4) api.done("stiffeu");
    if (p.sm === 3 && p.lam === 1000 && p.sh >= 2.7 && !S.blown && S.err < 0.01) api.done("stiffrk");
    const lim = p.sm === 1 ? 2 : p.sm === 3 ? 2.785 : Infinity;
    return [[["hλ", "hλ"], S.hl.toFixed(3)],
            [["稳定步长上限 h λ <", "stability limit hλ <"], isFinite(lim) ? String(lim) + api.T("（h < ", " (h < ") + (lim / p.lam * 1000).toFixed(3) + api.T(" ms）", " ms)") : api.T("无（任何步长都稳定）", "none (stable for any step)")],
            [["步数", "steps"], String(S.n)],
            [["终点时刻 n h", "final time n h"], S.tEnd.toFixed(3)],
            [["终点处的误差", "error at the final time"], S.blown ? api.T("发散", "diverged") : S.err.toExponential(2)]];
  },
  draw(api) {
    const p = api.p, w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), muted = api.css("--muted");
    if (api.scene === "arm") {
      const R = this.arm(p), H1 = (h - 110) * 0.6, H2 = (h - 110) * 0.4, stride = Math.max(1, Math.floor(R.ts.length / 1500));
      const pick = (a) => a.filter((_, k) => k % stride === 0 || k === a.length - 1);
      const lo = -200 - Math.max(0, p.th0), hi = Math.max(40, Math.abs(p.th0) + 20), cl = (v) => Math.max(lo, Math.min(hi, v));
      const G1 = api.graph({ x: 70, y: 20, w: w - 90, h: H1, xmin: 0, xmax: p.T, ymin: lo, ymax: hi, xlabel: "", ylabel: "θ / °" });
      G1.axes();
      G1.pts(pick(R.ts.map((t, k) => [t, R.qrs[k] * 180 / Math.PI])), muted, 3);
      G1.pts(pick(R.ts.map((t, k) => [t, cl(R.qs[k] * 180 / Math.PI)])), blue, 1.8);
      const em = Math.max(1e-9, ...R.es.map(Math.abs)) * 1.15, eM = Math.min(em, 5);
      const G2 = api.graph({ x: 70, y: 60 + H1, w: w - 90, h: H2, xmin: 0, xmax: p.T, ymin: -eM, ymax: eM, xlabel: "t / s", ylabel: "ΔE / (mgd)" });
      G2.axes();
      G2.pts(pick(R.ts.map((t, k) => [t, Math.max(-eM, Math.min(eM, R.es[k]))])), red, 1.6);
      return;
    }
    const S = this.stiff(p);
    const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: 1, ymin: -1.5, ymax: 2.5, xlabel: "t", ylabel: "y" });
    G.axes();
    G.fn((t) => S.ex(t), muted, 3);
    G.pts(S.pts.map(([t, y]) => [t, Math.max(-1.5, Math.min(2.5, y))]), blue, 1.8);
    if (S.pts.length < 400) G.dots(S.pts.map(([t, y]) => [t, Math.max(-1.5, Math.min(2.5, y))]), blue, 2.5);
  },
});
