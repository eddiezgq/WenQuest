// 实验 18.2 上和、下和与可积性（配 18.1–18.4 节）。“机器人”场景：AGV 制动，按采样间隔取速度，速度单调时左右端点矩形给出
// 制动距离的有保证的上下界；速度有周期性波动时，端点值不再是每段的上下确界，“界”可能失效。“函数”场景：x²、阶梯函数、
// 托马伊函数、狄利克雷函数、sin(1/x) 在 [0, 1] 上 n 等分的达布上和与下和。
WQ.lab({
  title: ["实验 18.2 上和、下和与可积性", "Lab 18.2 Upper sums, lower sums and integrability"],
  goal: ["看清达布上和与下和怎样从两边夹住积分：可积的函数，分割加密时两者之差趋于零；狄利克雷函数夹不住。再用它给 AGV 的制动距离一个有保证的上下界，并认识这个保证需要什么前提。",
         "See how upper and lower Darboux sums squeeze the integral: for integrable functions the gap closes as the partition is refined, for the Dirichlet function it never does. Then use them to give guaranteed bounds on an AGV's braking distance and see what the guarantee requires."],
  scenes: [
    { id: "brake", robot: true, name: ["AGV 制动距离", "AGV braking distance"], hide: ["f", "n"],
      problem: { title: ["机器人问题：只知道采样的速度，能保证制动距离不超过多少？", "Robot problem: from sampled speeds alone, what braking distance can we guarantee?"],
                 text: ["AGV 从 1.5 m/s 制动，控制器每隔 Δt 读一次速度。安全评估要的不是“大约多远”，而是“最远不超过多远”。速度单调减小时，每段的最大值就是段首的读数，左端点矩形和是距离的上界，右端点矩形和是下界。",
                        "An AGV brakes from 1.5 m/s and the controller reads the speed every Δt. A safety case needs not 'about how far' but 'never further than'. While the speed decreases, the maximum on each interval is the reading at its start, so the left-endpoint sum is an upper bound and the right-endpoint sum a lower bound."] } },
    { id: "fn", name: ["函数的达布和", "Darboux sums of functions"], hide: ["dt", "prof"],
      problem: { title: ["哪些函数的上和与下和能夹紧？", "Which functions let the upper and lower sums squeeze together?"],
                 text: ["在 [0, 1] 上 n 等分，每段取上确界得上和 U，取下确界得下和 L。U − L 能任意小，函数就可积。",
                        "Divide [0, 1] into n equal pieces; the supremum on each piece gives the upper sum U, the infimum the lower sum L. The function is integrable exactly when U − L can be made arbitrarily small."] } },
  ],
  params: [
    { id: "dt", name: ["采样间隔 Δt", "Sampling interval Δt"], min: 2, max: 200, step: 1, value: 100, unit: "ms", digits: 0 },
    { id: "prof", name: ["速度曲线：1 平稳制动，2 有周期性波动（周期 50 ms）", "Speed profile: 1 smooth braking, 2 with a periodic ripple (period 50 ms)"], min: 1, max: 2, step: 1, value: 1, digits: 0 },
    { id: "f", name: ["函数：1 x²，2 阶梯，3 托马伊，4 狄利克雷，5 sin(1/x)", "Function: 1 x², 2 step, 3 Thomae, 4 Dirichlet, 5 sin(1/x)"], min: 1, max: 5, step: 1, value: 1, digits: 0 },
    { id: "n", name: ["等分数 n", "Number of pieces n"], min: 1, max: 400, step: 1, value: 8, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["上和（每段上确界）", "upper sum (sup on each piece)"], color: "#d62728" }, { name: ["下和（每段下确界）", "lower sum (inf on each piece)"], color: "#1f77b4" }],
  tasks: [
    { id: "cert", robot: true, text: ["平稳制动：采样间隔取多大，制动距离的上界与下界之差小于 1 cm？", "Smooth braking: what sampling interval makes the gap between the upper and lower bounds less than 1 cm?"],
      demo: { scene: "brake", set: { prof: 1, dt: 6 }, wait: 1 } },
    { id: "fail", robot: true, text: ["改为有周期性波动的曲线，采样间隔取 100 ms：端点矩形和还是真实距离的上下界吗？为什么？再试 50、25、20 ms：哪些采样间隔恰好使界失效？“真值在界内”是否就等于“有保证”？", "Switch to the rippled profile at 100 ms: are the endpoint sums still bounds on the true distance? Why not? Try 50, 25, 20 ms: which intervals make the bounds fail? Does 'true value inside' mean 'guaranteed'?"],
      demo: { scene: "brake", set: { prof: 2, dt: 100 }, wait: 1 } },
    { id: "sq", text: ["x²：n 取多少，U − L 不超过 0.01？", "x²: what n makes U − L at most 0.01?"],
      demo: { scene: "fn", set: { f: 1, n: 100 }, wait: 1 } },
    { id: "dir", text: ["狄利克雷函数：n 取 50 以上，U − L 是多少？托马伊函数呢？", "Dirichlet function: with n ≥ 50, what is U − L? And for Thomae's function?"],
      demo: { scene: "fn", set: { f: 4, n: 60 }, wait: 1 } },
  ],
  think: ["“速度单调减小”这个前提在安全评估中能不能保证？如果只知道加速度的绝对值不超过 a_max，怎样由采样值给出有保证的上下界？", "Can 'the speed decreases' be guaranteed in a safety case? If you only know |acceleration| ≤ a_max, how can sampled values still give guaranteed bounds?"],

  V0: 1.5, T: 1.2,
  v(t, prof) {
    const base = this.V0 * Math.pow(Math.max(1 - t / this.T, 0), 1.5);
    if (prof === 1) return base;
    return t < this.T ? base + 0.3 * Math.abs(Math.sin(2 * Math.PI * 10 * t)) * (1 - t / this.T) : 0;   // 周期 50 ms 的波动（车体振动）
  },
  exact(prof) { let s = 0; const n = 20000, h = this.T / n; for (let k = 0; k < n; k++) s += this.v((k + 0.5) * h, prof) * h; return s; },
  brake(p) {
    const dt = p.dt / 1000, n = Math.ceil(this.T / dt - 1e-9);
    let L = 0, U = 0;
    for (let k = 0; k < n; k++) {
      const a = k * dt, b = Math.min((k + 1) * dt, this.T), w = b - a;
      const va = this.v(a, p.prof), vb = this.v(b, p.prof);
      U += va * w; L += vb * w;   // 按“速度单调减小”的假设：段首是最大值，段尾是最小值
    }
    return { L, U, D: this.exact(p.prof), n: n + 1 };
  },
  thomaeSup(a, b) { // [a, b] ⊂ [0, 1] 中有理数的最小分母
    for (let q = 1; q <= 4000; q++) if (Math.ceil(a * q - 1e-12) <= Math.floor(b * q + 1e-12)) return 1 / q;
    return 0;
  },
  supinf(f, a, b) {
    if (f === 1) return [b * b, a * a];
    if (f === 2) { const s = (x) => 0.2 * Math.floor(5 * x + 1e-12); return [s(b), s(a)]; }
    if (f === 3) return [this.thomaeSup(a, b), 0];
    if (f === 4) return [1, 0];
    // sin(1/x)，f(0) = 0
    if (a <= 0) return [1, -1];
    const u0 = 1 / b, u1 = 1 / a;
    const has = (c) => Math.ceil((u0 - c) / (2 * Math.PI) - 1e-12) <= Math.floor((u1 - c) / (2 * Math.PI) + 1e-12);
    const e0 = Math.sin(u0), e1 = Math.sin(u1);
    return [has(Math.PI / 2) ? 1 : Math.max(e0, e1), has(-Math.PI / 2) ? -1 : Math.min(e0, e1)];
  },
  sums(p) {
    let U = 0, L = 0; const h = 1 / p.n;
    for (let k = 0; k < p.n; k++) { const [s, i] = this.supinf(p.f, k * h, (k + 1) * h); U += s * h; L += i * h; }
    return { U, L };
  },
  reset() {},
  readouts(api) {
    const p = api.p;
    if (api.scene === "brake") {
      const B = this.brake(p), gap = (B.U - B.L) * 100, inside = B.D >= B.L - 1e-9 && B.D <= B.U + 1e-9;
      if (p.prof === 1 && gap < 1) api.done("cert");
      if (p.prof === 2 && p.dt >= 80 && !inside) api.done("fail");
      return [[["采样点数", "Samples"], String(B.n)], [["下界（右端点矩形和）", "Lower (right-endpoint sum)"], (B.L * 100).toFixed(2) + " cm"],
              [["上界（左端点矩形和）", "Upper (left-endpoint sum)"], (B.U * 100).toFixed(2) + " cm"], [["上界 − 下界", "Upper − lower"], gap.toFixed(2) + " cm"],
              [["真实制动距离", "True braking distance"], (B.D * 100).toFixed(2) + " cm"],
              [["真值在界内？", "True value inside?"], inside ? api.T("是", "yes") : api.T("否：端点值不是每段的最值", "no: endpoint values are not the extremes")]];
    }
    const S = this.sums(p);
    if (p.f === 1 && S.U - S.L < 0.01 + 1e-12) api.done("sq");
    if (p.f === 4 && p.n >= 50) api.done("dir");
    const names = ["x²", api.T("阶梯函数", "step function"), api.T("托马伊函数", "Thomae's function"), api.T("狄利克雷函数", "Dirichlet function"), "sin(1/x)"];
    return [[["函数", "Function"], names[p.f - 1]], [["上和 U", "Upper sum U"], S.U.toFixed(5)], [["下和 L", "Lower sum L"], S.L.toFixed(5)],
            [["U − L", "U − L"], (S.U - S.L).toFixed(5)], [["可积？", "Integrable?"], p.f === 4 ? api.T("否", "no") : api.T("是", "yes")]];
  },
  draw(api) {
    const w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), ink = api.css("--ink"), muted = api.css("--muted");
    const p = api.p;
    const box = (G, x0, x1, y0, y1, c, wd) => G.pts([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]], c, wd);
    if (api.scene === "brake") {
      const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: 1.25, ymin: 0, ymax: 1.75, xlabel: "t / s", ylabel: "v / (m/s)" });
      G.axes();
      const dt = p.dt / 1000, n = Math.ceil(this.T / dt - 1e-9);
      for (let k = 0; k < n && k < 700; k++) {
        const a = k * dt, b = Math.min((k + 1) * dt, this.T), va = this.v(a, p.prof), vb = this.v(b, p.prof);
        box(G, a, b, 0, va, red, 1);
        box(G, a, b, 0, vb, blue, 1);
      }
      G.fn((t) => (t <= this.T ? this.v(t, p.prof) : 0), ink, 2.2, null, 0, this.T);
      return;
    }
    const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: 1, ymin: p.f === 5 ? -1.15 : 0, ymax: 1.15, xlabel: "x", ylabel: "" });
    G.axes();
    const hh = 1 / p.n;
    for (let k = 0; k < p.n; k++) {
      const [s, i] = this.supinf(p.f, k * hh, (k + 1) * hh);
      box(G, k * hh, (k + 1) * hh, 0, s, red, 1);
      box(G, k * hh, (k + 1) * hh, 0, i, blue, 1.4);
    }
    if (p.f === 1) G.fn((x) => x * x, ink, 2);
    if (p.f === 2) G.fn((x) => 0.2 * Math.floor(5 * x + 1e-12), ink, 2);
    if (p.f === 5) G.fn((x) => (x > 0 ? Math.sin(1 / x) : 0), ink, 1, null, 0.002, 1);
    if (p.f === 3) { const pts = []; for (let q = 1; q <= 40; q++) for (let r = 0; r <= q; r++) { let a = r, b = q; while (b) [a, b] = [b, a % b]; if (a === 1) pts.push([r / q, 1 / q]); } G.dots(pts, ink, 2); }
    if (p.f === 4) { const a = [], b = []; for (let k = 0; k <= 80; k++) { a.push([k / 80, 1]); b.push([(k + 0.5) / 80, 0]); } G.dots(a, ink, 1.6); G.dots(b, muted, 1.6); }
  },
});
