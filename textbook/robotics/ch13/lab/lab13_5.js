// 实验 13.5 接近平行的两根轴（配 13.5 节）。
// 轴 i 为 {i−1} 的 z 轴（竖直，过原点）；轴 i+1 名义上与它平行，相距 a，经过 (a, 0, 0)。
// 轴 i+1 偏转 ε：方向 (sin ε cos φ, −sin ε sin φ, cos ε)。φ = 0° 时偏转在两轴所在的平面内，φ = 90° 时垂直于该平面。
// 三种参数化：DH（公垂线，式 (13.1.1)–(13.1.3)；平行时取 d = 0）；哈亚蒂（与 xy 平面的交点，β 为绕 y 的转角）；指数积（旋量轴 S）。
WQ.lab({
  title: ["实验 13.5 接近平行的两根轴", "Lab 13.5 Two nearly parallel axes"],
  goal: ["让一根关节轴偏转一个很小的角度，比较 DH、哈亚蒂参数和旋量轴的变化：哪一种参数随几何连续变化？",
         "Tilt one joint axis by a tiny angle and compare how the DH parameters, the Hayati parameters and the screw axis change: which of them follows the geometry continuously?"],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 关节 2、3 的轴", "UR5e axes 2 and 3"],
      problem: { title: ["机器人问题：标定出的 d 为什么有几百米", "Robot problem: why a calibrated d can be hundreds of metres"],
                 text: ["关节 2、3 的轴名义上平行，相距 0.425 m（大臂长）。真实的机器人总有极小的偏差。看看偏差 0.01° 时 DH 参数变成什么样。",
                        "Axes 2 and 3 are nominally parallel, 0.425 m apart (the upper arm). A real robot always deviates a little. See what the DH parameters become for 0.01°."] } },
    { id: "chop", name: ["两支筷子", "Two chopsticks"],
      problem: { title: ["生活中的例子：两支几乎平行的筷子", "Everyday example: two nearly parallel chopsticks"],
                 text: ["桌上两支筷子相距 3 cm，看上去平行。把它们的延长线画出来，会在很远的地方相交；稍微转动一支，交点就在桌子两端之间来回跑。",
                        "Two chopsticks lie 3 cm apart and look parallel. Their extensions meet far away; turn one slightly and the crossing point races from one end of the table to the other."] } },
  ],
  params: [
    { id: "eps", name: ["偏转角 ε", "Tilt ε"], min: -3, max: 3, step: 0.01, value: 0, unit: "°", digits: 2 },
    { id: "phi", name: ["偏转方向 φ（0° 面内，90° 面外）", "Tilt direction φ (0° in-plane, 90° out-of-plane)"], min: 0, max: 90, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  tasks: [
    { id: "par", robot: true, text: ["UR5e：ε = 0（两轴平行）。读出 DH 的 a、d，以及哈亚蒂的 a、β。", "UR5e: ε = 0 (parallel). Read DH a, d and Hayati a, β."],
      demo: { scene: "ur", set: { eps: 0, phi: 0 }, press: [] } },
    { id: "small", robot: true, text: ["面内偏转 ε = 0.01°（φ = 0°）：DH 的 d 变成多少？与算例 13.5.1 比较。", "In-plane tilt ε = 0.01° (φ = 0°): what does DH d become? Compare with Example 13.5.1."],
      demo: { scene: "ur", set: { eps: 0.01, phi: 0 }, press: [] } },
    { id: "flip", robot: true, text: ["改为 ε = −0.01°：d 的符号怎样变化？几何上只差了 0.02°。", "Now ε = −0.01°: how does the sign of d change? The geometry moved only 0.02°."],
      demo: { scene: "ur", set: { eps: -0.01, phi: 0 }, press: [] } },
    { id: "out", robot: true, text: ["面外偏转 ε = 0.5°（φ = 90°）：DH 参数是否连续？", "Out-of-plane tilt ε = 0.5° (φ = 90°): are the DH parameters continuous?"],
      demo: { scene: "ur", set: { eps: 0.5, phi: 90 }, press: [] } },
    { id: "chop", text: ["两支筷子（相距 3 cm）：调节 ε（φ = 0°），使延长线的交点在 0.9～1.1 m 之外。", "Chopsticks 3 cm apart: adjust ε (φ = 0°) so that the extensions meet 0.9–1.1 m away."],
      demo: { scene: "chop", set: { eps: 1.72, phi: 0 }, press: [] } },
  ],
  think: ["指数积的旋量轴 S 随 ε 的变化量与 ε 成正比，哈亚蒂的 β 等于 ε，而 DH 的 d 与 ε 成反比。做最小二乘标定时，哪一种参数化会出问题？为什么？",
          "The change of the screw axis S is proportional to ε, Hayati's β equals ε, but DH d is inversely proportional to ε. In least-squares calibration, which parameterisation causes trouble, and why?"],

  A(api) { return api.scene === "chop" ? 0.03 : 0.425; },
  geo(api) {
    const e = api.p.eps * Math.PI / 180, f = api.p.phi * Math.PI / 180, a = this.A(api);
    const u = [Math.sin(e) * Math.cos(f), -Math.sin(e) * Math.sin(f), Math.cos(e)];
    // DH：公垂线，式 (13.1.1)；u1 = z，p1 = 0，p2 = (a, 0, 0)
    const n = [-u[1], u[0], 0], nn = Math.hypot(n[0], n[1]);
    let dh;
    if (nn < 1e-12) dh = { a, alpha: 0, d: 0, par: true };
    else {
      const c = u[2], s = a * u[0] / (c * c - 1), t = c * s;          // t − c s = 0，c t − s = a u_x
      const dist = Math.abs(a * n[0] / nn);
      dh = { a: dist, alpha: Math.atan2(nn, c), d: t, par: false };
    }
    // 哈亚蒂：与 z = 0 平面的交点就是 (a, 0, 0)；β = asin(u_x)，α = atan2(−u_y, u_z)
    const hy = { a, beta: Math.asin(u[0]), alpha: Math.atan2(-u[1], u[2]) };
    // 旋量轴 S = (u, −u × p)，p = (a, 0, 0)；与平行时 S₀ = (0, 0, 1, 0, −a, 0) 之差
    const v = [0, -u[2] * a, u[1] * a];
    const dS = Math.hypot(u[0], u[1], u[2] - 1, v[0], v[1] + a, v[2]);
    return { u, dh, hy, dS, a };
  },
  readouts(api, s) {
    const g = this.geo(api), deg = (x) => api.fmt(x * 180 / Math.PI, 3) + "°";
    const close = (x, y) => Math.abs(x - y) < 1e-9;
    if (api.scene === "ur" && close(api.p.eps, 0)) api.done("par");
    if (api.scene === "ur" && close(api.p.eps, 0.01) && api.p.phi === 0) api.done("small");
    if (api.scene === "ur" && close(api.p.eps, -0.01) && api.p.phi === 0) api.done("flip");
    if (api.scene === "ur" && close(api.p.eps, 0.5) && api.p.phi === 90 && Math.abs(g.dh.d) < 1e-9) api.done("out");
    if (api.scene === "chop" && api.p.phi === 0 && Math.abs(g.dh.d) > 0.9 && Math.abs(g.dh.d) < 1.1) api.done("chop");
    const dtext = Math.abs(g.dh.d) >= 100 ? api.fmt(g.dh.d, 0) + " m" : api.fmt(g.dh.d, 4) + " m";
    return [[["DH：a、α、d", "DH: a, α, d"], `${api.fmt(g.dh.a, 4)} m, ${deg(g.dh.alpha)}, ${dtext}`],
            [["哈亚蒂：a、α、β", "Hayati: a, α, β"], `${api.fmt(g.hy.a, 4)} m, ${deg(g.hy.alpha)}, ${deg(g.hy.beta)}`],
            [["旋量轴的变化 |S − S₀|", "change of screw axis |S − S₀|"], g.dS.toExponential(2)],
            [["两轴的关系", "relation of the axes"], g.dh.par ? (api.lang() === "en" ? "parallel" : "平行") : (g.dh.a < 1e-12 ? (api.lang() === "en" ? "intersecting" : "相交") : (api.lang() === "en" ? "skew" : "异面"))]];
  },
  draw(api, s) {
    const { w, h } = api, g = this.geo(api), a = g.a, chop = api.scene === "chop";
    const span = chop ? 1.4 : 1.2, k = Math.min(w * 0.5 / (a * 2.2 + 0.15), h / span) * 0.85;
    const kx = chop ? Math.min(w * 0.35 / a, k * 12) : k;      // 筷子：水平方向放大，便于看清 3 cm 的间距
    const cx = w * 0.32, cy = h * 0.42;
    const X = (x, z) => [cx + kx * x, cy - k * z];
    const top = (cy - 10) / k, bot = -(h - cy - 10) / k;
    // 轴 i
    api.line(...X(0, bot), ...X(0, top), api.css("--muted"), chop ? 8 : 4);
    api.label(api.lang() === "en" ? "axis i" : "轴 i", ...X(0, top - 0.04).map((v, i) => v + (i === 0 ? -50 : 0)), api.css("--muted"), 13);
    // 轴 i+1（侧视：只画 x–z 平面内的分量）
    const ux = g.u[0], uz = g.u[2], len = (top - bot) / Math.max(uz, 0.3);
    const p0 = [a - ux * len, -uz * len], p1 = [a + ux * len, uz * len];
    api.line(...X(...p0), ...X(...p1), chop ? api.css("--amber") : api.css("--ink"), chop ? 8 : 4);
    api.label(api.lang() === "en" ? "axis i+1" : "轴 i+1", ...X(a + ux * top, top - 0.04).map((v, i) => v + (i === 0 ? 10 : 0)), api.css("--ink"), 13);
    // {i−1}
    api.frame(...X(0, 0), 0, 26, ["x", "z"], "{i−1}");
    // 哈亚蒂的点
    const H = X(a, 0); api.circle(H[0], H[1], 6, api.css("--green"));
    api.label(api.lang() === "en" ? "Hayati" : "哈亚蒂", H[0] + 10, H[1] + 14, api.css("--green"), 12);
    // DH 的 {i} 原点：平行时在 (a, 0)，否则在公垂线的垂足（面内偏转时就是交点）
    const d = g.dh.d, inside = d < top && d > bot;
    if (inside) {
      const O = X(g.dh.par ? a : a + ux * d / uz, d); api.circle(O[0], O[1], 7, api.css("--amber"));
      if (!g.dh.par) api.line(...X(0, 0), ...X(0, d), api.css("--blue"), 3);
      api.label(api.lang() === "en" ? "DH origin of {i}" : "DH：{i} 的原点", O[0] + 12, O[1] - 12, api.css("--amber"), 13);
    } else {
      const ye = d < 0 ? h - 18 : 18, xs = X(0, 0)[0];
      api.arrow(xs, cy + (d < 0 ? 30 : -30), xs, ye, api.css("--amber"), 3);
      api.label((api.lang() === "en" ? "DH origin of {i}: d = " : "DH：{i} 的原点在 d = ") + api.fmt(d, 0) + " m", xs + 12, ye + (d < 0 ? -10 : 10), api.css("--amber"), 13);
    }
  },
});
