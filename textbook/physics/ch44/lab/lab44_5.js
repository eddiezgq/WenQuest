// 实验 44.5 波包穿越势垒（配 44.5 节）。“波包”场景用工具包的 api.qm.packet 与 api.qm.step（克兰克–尼科尔森法，
// 与程序 44.5.1 同一算法）求解含时薛定谔方程：0–200 nm，格点 4000 个（间距 0.05 nm，势垒宽度恰为格点间距的整数倍），步长 0.5 fs；高斯波包 σ = 6 nm，从 60 nm 出发，
// 势垒的左边在 100 nm。“栅氧化层”场景按式 (44.5.1) 计算透射系数随氧化层厚度的变化。
const C45 = 0.0380998212, HB45 = 0.6582119569, XB45 = 100, X045 = 60, SIG45 = 6;
function T45(E, V0, a, mr) {   // 矩形势垒的精确透射系数，式 (44.5.1)
  const c = C45 / mr;
  if (Math.abs(E - V0) < 1e-9) E += 1e-9;
  if (E < V0) { const k = Math.sqrt((V0 - E) / c), sh = Math.sinh(k * a); return 1 / (1 + V0 * V0 * sh * sh / (4 * E * (V0 - E))); }
  const k = Math.sqrt((E - V0) / c), sn = Math.sin(k * a); return 1 / (1 + V0 * V0 * sn * sn / (4 * E * (E - V0)));
}
function Tavg45(E, V0, a) {    // 按波包的波数分布（高斯，宽 1/(2σ)）平均
  const k0 = Math.sqrt(E / C45), sk = 1 / (2 * SIG45);
  let s = 0, wsum = 0;
  for (let j = -60; j <= 60; j++) { const k = k0 + j * 0.1 * sk, wt = Math.exp(-0.5 * Math.pow(j * 0.1, 2)); if (k <= 0) continue; s += wt * T45(C45 * k * k, V0, a, 1); wsum += wt; }
  return s / wsum;
}

WQ.lab({
  title: ["实验 44.5 波包穿越势垒", "Lab 44.5 A wave packet meets a barrier"],
  goal: ["在浏览器里解含时薛定谔方程，看高斯波包怎样被势垒分成反射和透射两部分；读出透射概率，与式 (44.5.1) 比较；再看栅氧化层的厚度怎样决定漏电。",
         "Solve the time-dependent Schrödinger equation in the browser and watch a Gaussian packet split into reflected and transmitted parts; compare the transmitted probability with Eq. (44.5.1); then see how the gate-oxide thickness sets the leakage."],
  scenes: [
    { id: "packet", name: ["波包与势垒", "Packet and barrier"], hide: ["tox"],
      problem: { title: ["生活中的例子：感烟探测器里的 α 衰变", "Everyday example: alpha decay in a smoke detector"],
                 text: ["α 粒子的能量比库仑势垒低得多，却能隧穿出原子核。这里用电子和纳米尺度的势垒看同一个现象。", "Alpha particles have far less energy than the Coulomb barrier, yet tunnel out of the nucleus. Here the same thing happens to an electron and a nanometre barrier."] } },
    { id: "oxide", robot: true, name: ["栅氧化层的漏电", "Gate-oxide leakage"], hide: ["E", "V0", "a"],
      problem: { title: ["机器人问题：控制器芯片的栅极漏电", "Robot problem: gate leakage in the controller chip"],
                 text: ["SiO₂ 势垒高 3.1 eV，电子能量 0.1 eV，有效质量 0.5mₑ。氧化层减薄，漏电（透射系数）怎样变化？", "SiO₂ barrier 3.1 eV, electron energy 0.1 eV, effective mass 0.5 mₑ. How does the leakage (transmission) change as the oxide thins?"] } },
  ],
  params: [
    { id: "E", name: ["波包平均能量 E", "Mean energy E"], min: 0.05, max: 0.6, step: 0.01, value: 0.2, unit: "eV", digits: 2 },
    { id: "V0", name: ["势垒高 V₀", "Barrier height V₀"], min: 0.1, max: 0.6, step: 0.01, value: 0.3, unit: "eV", digits: 2 },
    { id: "a", name: ["势垒宽 a", "Barrier width a"], min: 0.2, max: 3, step: 0.1, value: 1, unit: "nm", digits: 1 },
    { id: "tox", name: ["氧化层厚度", "Oxide thickness"], min: 1, max: 3, step: 0.1, value: 2, unit: "nm", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["发射波包", "Launch"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--violet)", name: ["|Ψ|²", "|Ψ|²"] }, { color: "var(--muted)", name: ["势垒", "barrier"] }],
  tasks: [
    { id: "tunnel", text: ["E < V₀：波包仍有超过 1% 透过势垒。", "E < V₀: more than 1% of the packet still gets through."],
      demo: { scene: "packet", set: { E: 0.2, V0: 0.3, a: 1 }, press: ["start"], wait: 6 } },
    { id: "wide", text: ["E < V₀，势垒宽 2 nm 以上：透射概率降到 1% 以下。", "E < V₀ with a barrier at least 2 nm wide: the transmission falls below 1%."],
      demo: { scene: "packet", set: { E: 0.15, V0: 0.3, a: 2 }, press: ["start"], wait: 7 } },
    { id: "over", text: ["E > V₀：仍有超过 10% 被反射。", "E > V₀: more than 10% is still reflected."],
      demo: { scene: "packet", set: { E: 0.35, V0: 0.3, a: 1 }, press: ["start"], wait: 6 } },
    { id: "oxide", robot: true, text: ["栅氧化层从 2 nm 减到 1.2 nm：读出漏电增加的倍数。", "Thin the gate oxide from 2 nm to 1.2 nm: read how many times the leakage grows."],
      demo: { scene: "oxide", set: { tox: 1.2 }, press: [], wait: 1 } },
  ],
  think: ["E < V₀ 时，实验测得的透射概率为什么比同样能量的平面波的 T 略大？E > V₀ 时又如何？波包越宽（σ 越大），两者是否越接近？",
          "For E < V₀, why is the packet's transmitted probability a little larger than T for a plane wave of the same energy? What about E > V₀? Does a wider packet bring them closer?"],

  reset(api, s) {
    const N = 3999, dx = 200 / (N + 1), x = new Float64Array(N), V = new Float64Array(N);   // dx = 0.05 nm
    const ib = Math.round(XB45 / dx) - 1, nb = Math.round(api.p.a / dx);
    for (let i = 0; i < N; i++) { x[i] = (i + 1) * dx; V[i] = i >= ib && i < ib + nb ? api.p.V0 : 0; }
    s.N = N; s.dx = dx; s.x = x; s.V = V; s.t = 0; s.fin = false;
    s.psi = api.qm.packet(x, X045, SIG45, api.qm.k(api.p.E));
    const vg = 2 * C45 * api.qm.k(api.p.E) / HB45;
    s.tend = 2 * (XB45 - X045) / vg;
    s.iR = ib + nb;
    if (api.scene === "oxide" && api.p.tox <= 1.2 + 1e-9) api.done("oxide");
  },
  update(dt, api, s) {
    if (api.scene !== "packet") { api.stop(); return; }
    for (let k = 0; k < 4 && s.t < s.tend; k++) { api.qm.step(s.psi, s.V, s.dx, 0.5); s.t += 0.5; }
    if (s.t >= s.tend) { s.fin = true; s.Tm = api.qm.prob(s.psi, s.dx, s.iR); s.Rm = api.qm.prob(s.psi, s.dx, 0, Math.floor(XB45 / s.dx)); fin45(api, s); api.stop(); }
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p;
    if (api.scene === "oxide") {
      const T = T45(0.1, 3.1, p.tox, 0.5), T2 = T45(0.1, 3.1, 2, 0.5);
      return [[["透射系数 T", "Transmission T"], T.toExponential(2)], [["与 2 nm 相比", "Relative to 2 nm"], f(T / T2, T / T2 > 100 ? 0 : 2) + " ×"],
              [["厚度每减 0.1 nm", "Per 0.1 nm thinner"], f(Math.exp(0.2 * Math.sqrt(3.0 / (C45 / 0.5))), 2) + " ×"]];
    }
    const Tr = s.psi ? api.qm.prob(s.psi, s.dx, s.iR) : 0;
    const g = (v) => (v < 0.01 ? v.toExponential(2) : f(v, 4));       // 很小的概率用科学计数法，看得出数量级
    return [[["时间 t", "Time t"], f(s.t || 0, 0) + " fs"], [["势垒右侧的概率", "Probability beyond the barrier"], g(Tr)],
            [["透射概率（结束时）", "Transmitted (at the end)"], s.fin ? g(s.Tm) : "—"], [["反射概率（结束时）", "Reflected (at the end)"], s.fin ? g(s.Rm) : "—"],
            [["平面波 T（式 (44.5.1)）", "Plane-wave T (Eq. (44.5.1))"], g(T45(p.E, p.V0, p.a, 1))],
            [["按波包平均的 T", "T averaged over the packet"], g(Tavg45(p.E, p.V0, p.a))]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    if (api.scene === "oxide") {
      const pts = [];
      for (let t = 1; t <= 3.0001; t += 0.02) pts.push([t, Math.log10(T45(0.1, 3.1, t, 0.5))]);
      const P = api.plot(w * 0.1, 20, w * 0.85, h - 60, [{ pts, color: css("--blue") }], { xmin: 1, xmax: 3, ymin: -18, ymax: -4, xlabel: api.T("氧化层厚度 / nm", "oxide thickness / nm"), ylabel: "lg T" });
      const T = Math.log10(T45(0.1, 3.1, api.p.tox, 0.5));
      api.circle(P.X(api.p.tox), P.Y(T), 6, css("--red"), css("--ink"));
      for (let t = 1; t <= 3; t += 0.5) api.label(String(t), P.X(t), P.Y(-18) + 14, css("--muted"), 11, "center");
      for (let y = -18; y <= -4; y += 2) api.label(String(y), P.X(1) - 6, P.Y(y) + 4, css("--muted"), 11, "right");
      return;
    }
    if (!s.psi) return;
    const pts = [];
    let mx = 0;
    for (let i = 0; i < s.N; i += 4) { const d = s.psi.re[i] * s.psi.re[i] + s.psi.im[i] * s.psi.im[i]; pts.push([s.x[i], d]); }
    mx = Math.pow(2 * Math.PI * SIG45 * SIG45, -0.5) * 1.6;
    const P = api.plot(w * 0.05, 20, w * 0.9, h - 60, [{ pts, color: css("--violet") }], { xmin: 0, xmax: 200, ymin: 0, ymax: mx, xlabel: "x / nm", ylabel: "|Ψ|²" });
    const hb = Math.min(1, api.p.V0 / 0.6) * (h - 60);
    api.rect(P.X(XB45), P.Y(0) - hb, Math.max(2, P.X(XB45 + api.p.a) - P.X(XB45)), hb, css("--muted"));
    const he = Math.min(1, api.p.E / 0.6) * (h - 60);
    api.line(P.X(0), P.Y(0) - he, P.X(200), P.Y(0) - he, css("--orange"), 1, [5, 4]);
    api.label(api.T("波包平均能量（与势垒高按同一比例）", "mean energy (same scale as the barrier)"), P.X(2), P.Y(0) - he - 8, css("--orange"), 11);
  },
});

function fin45(api, s) {
  const p = api.p;
  if (p.E < p.V0 && s.Tm > 0.01) api.done("tunnel");
  if (p.E < p.V0 && p.a >= 2 - 1e-9 && s.Tm < 0.01) api.done("wide");
  if (p.E > p.V0 && s.Rm > 0.1) api.done("over");
}
