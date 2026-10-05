// 实验 8.4 牛顿法：沿切线找根（配 8.4 节）。一步步迭代，看切线、误差的平方递减与几种失效；
// “机器人”场景：关节阶跃响应到达 95% 的时刻 t₉₅（与 5.5 节的二分法比较）。
WQ.lab({
  title: ["实验 8.4 牛顿法：沿切线找根", "Lab 8.4 Newton's method: follow the tangent"],
  goal: ["看清牛顿法每一步在做什么（用切线代替曲线），体会误差的平方递减（有效数字每步约翻一番）；找出它失效的几种情形：初值太远发散、循环、重根时变慢。",
         "See what each Newton step does (replace the curve by its tangent), watch the error square at each step (digits roughly double), and find how it fails: divergence from a far start, cycling, and slow convergence at a double root."],
  scenes: [
    { id: "fn", name: ["函数的根", "Roots of functions"], hide: ["z"],
      problem: { title: ["用切线代替曲线，一步跳到切线与横轴的交点", "Replace the curve by its tangent and jump to where the tangent meets the axis"],
                 text: ["xₖ₊₁ = xₖ − f(xₖ)/f′(xₖ)。离根足够近时，每一步的误差约为上一步误差的平方乘以 |f″/(2f′)|。离根远时呢？",
                        "xₖ₊₁ = xₖ − f(xₖ)/f′(xₖ). Close to a root, each error is about the square of the previous one times |f″/(2f′)|. And far from it?"] } },
    { id: "rise", robot: true, name: ["关节到达 95% 的时间", "Joint time to 95%"], hide: ["f", "x0"],
      problem: { title: ["机器人问题：比二分法快多少？", "Robot problem: how much faster than bisection?"],
                 text: ["关节阶跃响应 q(t)（ωₙ = 10 rad/s）。解 q(t) = 0.95，从 t₀ = 0.2 s 出发用牛顿法。5.5 节的二分法要几十步才到机器精度。",
                        "Joint step response q(t) (ωₙ = 10 rad/s). Solve q(t) = 0.95 by Newton's method from t₀ = 0.2 s. Bisection (Section 5.5) needs dozens of steps to reach machine precision."] } },
  ],
  params: [
    { id: "f", name: ["函数：1 x² − 2，2 arctan x，3 x³ − 2x + 2，4 (x − 1)²，5 cos x − x", "Function: 1 x² − 2, 2 arctan x, 3 x³ − 2x + 2, 4 (x − 1)², 5 cos x − x"], min: 1, max: 5, step: 1, value: 5, digits: 0 },
    { id: "x0", name: ["初值 x₀", "Initial guess x₀"], min: -3, max: 3, step: 0.05, value: 2, digits: 2 },
    { id: "z", name: ["阻尼比 ζ", "Damping ratio ζ"], min: 0.3, max: 0.9, step: 0.05, value: 0.6, digits: 2 },
  ],
  buttons: [{ id: "step", name: ["迭代一步", "One step"], primary: true }, { id: "run", name: ["连续 10 步", "Ten steps"] }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["函数", "function"], color: "#222222" }, { name: ["切线", "tangent"], color: "#d62728" }],
  tasks: [
    { id: "sqrt", text: ["选 x² − 2，从 x₀ = 1 出发，6 步以内把 √2 算到误差小于 10⁻¹²。", "Choose x² − 2 from x₀ = 1: reach √2 within 10⁻¹² in at most 6 steps."],
      demo: { scene: "fn", set: { f: 1, x0: 1 }, press: ["run"], wait: 1 } },
    { id: "diverge", text: ["选 arctan x，找一个使迭代发散（|x| 超过 100）的初值。", "Choose arctan x and find a start that diverges (|x| exceeds 100)."],
      demo: { scene: "fn", set: { f: 2, x0: 1.5 }, press: ["run"], wait: 1 } },
    { id: "cycle", text: ["选 x³ − 2x + 2，从 x₀ = 0 出发，看迭代在 0 与 1 之间循环。", "Choose x³ − 2x + 2 from x₀ = 0 and watch the iteration cycle between 0 and 1."],
      demo: { scene: "fn", set: { f: 3, x0: 0 }, press: ["run"], wait: 1 } },
    { id: "double", text: ["选 (x − 1)²（重根），迭代 10 步，读出误差：每步只减半。", "Choose (x − 1)² (a double root), do 10 steps and read the error: it only halves each step."],
      demo: { scene: "fn", set: { f: 4, x0: 2 }, press: ["run"], wait: 1 } },
    { id: "rise", robot: true, text: ["在“关节到达 95% 的时间”中取 ζ = 0.6，用牛顿法把 t₉₅ 算到 |q(t) − 0.95| < 10⁻¹²，最多 6 步。", "In 'Joint time to 95%' take ζ = 0.6 and get |q(t) − 0.95| < 10⁻¹² in at most 6 steps."],
      demo: { scene: "rise", set: { z: 0.6 }, press: ["run"], wait: 1 } },
  ],
  think: ["牛顿法用了 f′，二分法只用了 f 的符号。在什么情况下你宁可用二分法？能不能把两者结合起来？",
          "Newton uses f′; bisection only uses the sign of f. When would you prefer bisection? Can the two be combined?"],

  F(api) {
    if (api.scene === "rise") {
      const z = api.p.z, wn = 10, wd = wn * Math.sqrt(1 - z * z), c = z / Math.sqrt(1 - z * z);
      const q = (t) => 1 - Math.exp(-z * wn * t) * (Math.cos(wd * t) + c * Math.sin(wd * t));
      return { f: (t) => q(t) - 0.95, d: (t) => Math.exp(-z * wn * t) * (wn * wn / wd) * Math.sin(wd * t), x0: 0.2, lo: 0, hi: 0.6, ylo: -1, yhi: 0.3, name: "q(t) − 0.95", root: null, unit: " s" };
    }
    switch (api.p.f) {
      case 1: return { f: (x) => x * x - 2, d: (x) => 2 * x, lo: -3, hi: 3, ylo: -3, yhi: 7, name: "x² − 2", root: Math.SQRT2 };
      case 2: return { f: Math.atan, d: (x) => 1 / (1 + x * x), lo: -6, hi: 6, ylo: -1.7, yhi: 1.7, name: "arctan x", root: 0 };
      case 3: return { f: (x) => x * x * x - 2 * x + 2, d: (x) => 3 * x * x - 2, lo: -2.5, hi: 2, ylo: -4, yhi: 6, name: "x³ − 2x + 2", root: -1.7692923542386314 };
      case 4: return { f: (x) => (x - 1) * (x - 1), d: (x) => 2 * (x - 1), lo: -1, hi: 3, ylo: -0.5, yhi: 4, name: "(x − 1)²", root: 1 };
      default: return { f: (x) => Math.cos(x) - x, d: (x) => -Math.sin(x) - 1, lo: -1, hi: 2.5, ylo: -2.5, yhi: 1.5, name: "cos x − x", root: 0.7390851332151607 };
    }
  },
  reset(api, s) {
    const F = this.F(api), x0 = api.scene === "rise" ? F.x0 : api.p.x0;
    Object.assign(s, { xs: [x0], msg: "" });
  },
  one(F, s) {
    const x = s.xs[s.xs.length - 1], fx = F.f(x), dx = F.d(x);
    if (!isFinite(x) || Math.abs(x) > 1e8) { s.msg = "big"; return false; }
    if (fx === 0) { s.msg = "root"; return false; }
    if (dx === 0) { s.msg = "flat"; return false; }
    s.xs.push(x - fx / dx);
    return true;
  },
  action(id, api, s) {
    const F = this.F(api);
    if (id === "step") this.one(F, s);
    if (id === "run") for (let i = 0; i < 10 && this.one(F, s); i++);
    const k = s.xs.length - 1, x = s.xs[k];
    if (api.scene === "rise") {
      if (Math.abs(api.p.z - 0.6) < 0.01 && Math.abs(F.f(x)) < 1e-12 && s.xs.slice(0, 7).some((v) => Math.abs(F.f(v)) < 1e-12)) api.done("rise");
      return;
    }
    if (api.p.f === 1 && s.xs.slice(0, 7).some((v) => Math.abs(v - Math.SQRT2) < 1e-12)) api.done("sqrt");
    if (api.p.f === 2 && s.xs.some((v) => Math.abs(v) > 100)) api.done("diverge");
    if (api.p.f === 3 && k >= 4 && s.xs.slice(-4).every((v, i, a) => i < 2 || Math.abs(v - a[i - 2]) < 1e-12) && Math.abs(F.f(x)) > 0.5) api.done("cycle");
    if (api.p.f === 4 && k >= 10) api.done("double");
  },
  readouts(api, s) {
    const F = this.F(api), k = s.xs.length - 1, x = s.xs[k], u = F.unit || "";
    const rows = [[["函数", "Function"], F.name], [["迭代次数 k", "Step k"], String(k)],
                  [["xₖ", "xₖ"], (isFinite(x) ? x.toPrecision(16) : "—") + u], [["f(xₖ)", "f(xₖ)"], isFinite(x) ? F.f(x).toExponential(3) : "—"]];
    if (F.root !== null) {
      const e = s.xs.map((v) => Math.abs(v - F.root));
      rows.push([["误差 |xₖ − 根|", "Error |xₖ − root|"], e[k].toExponential(3)]);
      const q2 = (j) => e[j] / (e[j - 1] * e[j - 1]), q1 = (j) => e[j] / e[j - 1];
      const ok = (j) => j >= 1 && e[j - 1] > 0 && e[j] > 0;
      if (k >= 2 && ok(k)) {
        const steady2 = ok(k - 1) && e[k - 1] < 1e-2 && Math.abs(q2(k) / q2(k - 1) - 1) < 0.1;
        rows.push([["eₖ / eₖ₋₁²", "eₖ / eₖ₋₁²"], q2(k).toPrecision(4) + (steady2 ? api.T("（比值趋于稳定：二次收敛）", " (ratio settling: quadratic convergence)") : "")]);
      }
      if (ok(k)) {
        const steady1 = k >= 3 && ok(k - 1) && q1(k) < 0.95 && Math.abs(q1(k) / q1(k - 1) - 1) < 0.02;
        rows.push([["eₖ / eₖ₋₁", "eₖ / eₖ₋₁"], q1(k).toPrecision(4) + (steady1 ? api.T("（eₖ/eₖ₋₁ → " + q1(k).toFixed(2) + "：线性收敛）", " (eₖ/eₖ₋₁ → " + q1(k).toFixed(2) + ": linear convergence)") : "")]);
      }
    }
    const msg = { big: api.T("|x| 已超过 10⁸：发散", "|x| exceeds 10⁸: diverged"), root: api.T("f(xₖ) = 0：已到根", "f(xₖ) = 0: at the root"), flat: api.T("f′(xₖ) = 0：切线水平，无法继续", "f′(xₖ) = 0: horizontal tangent, cannot continue") }[s.msg];
    if (msg) rows.push([["提示", "Note"], msg]);
    return rows;
  },
  draw(api, s) {
    const F = this.F(api), w = api.w, h = api.h, ink = api.css("--ink"), red = api.css("--red"), mu = api.css("--muted");
    const G = api.graph({ x: 60, y: 24, w: w - 80, h: h - 74, xmin: F.lo, xmax: F.hi, ymin: F.ylo, ymax: F.yhi,
      xlabel: api.scene === "rise" ? "t / s" : "x", ylabel: F.name });
    G.axes();
    G.fn(F.f, ink, 2);
    for (let i = 0; i + 1 < s.xs.length; i++) {
      const x = s.xs[i], y = F.f(x), xn = s.xs[i + 1];
      if (!isFinite(xn)) break;
      G.seg(x, 0, x, y, mu, 1, [3, 3]);
      G.seg(x, y, xn, 0, red, 1.6);
    }
    s.xs.forEach((x, i) => { if (isFinite(x)) G.point(x, 0, red, i < 6 ? "x" + "₀₁₂₃₄₅"[i] : null); });
  },
});
