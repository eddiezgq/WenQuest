// 实验 4.2 RC 线（配 4.2 节）。一个反相器（尺寸可调）经一条导线驱动末端负载（20 个参考反相器的输入电容）。
// 读数给出式 (4.2.4) 的两部分：驱动项 0.69·Rd·(Cself + Cw + CL) 与导线项 0.38·Rw·Cw + 0.69·Rw·CL；
// 图中是把导线切成 40 段、用后向欧拉法解出的始端与末端波形，竖线是数值解的末端 50 % 时刻。
const P42 = M4_2.P, Q42 = P42.problems.p42;
const R0_42 = (M4_2.reqN(P42.Wmin) + M4_2.reqP(P42.kn / P42.kp * P42.Wmin)) / 2, C0_42 = M4_2.cin(P42.Wmin, P42.kn / P42.kp * P42.Wmin);
const CL42 = Q42.leaf_load_units * C0_42, G42 = P42.Cd / P42.Cg;
const LAY42 = { m1: ["met1", 0.14], m3: ["met3", 0.3] };
const seen42 = { a: false, b: false };
function line42(scene, p) {
  const [lay, w] = LAY42[scene];
  const Rd = R0_42 / p.size, Cs = G42 * C0_42 * p.size, Rw = M4_2.wireR(lay, w) * p.L, Cw = M4_2.wireC(lay, w) * p.L;
  const drv = 0.69 * Rd * (Cs + Cw + CL42), wire = 0.38 * Rw * Cw + 0.69 * Rw * CL42;
  return { Rd, Cs, Rw, Cw, drv, wire, total: drv + wire };
}
function sim42(x) {   // 40 段梯形网络的阶跃响应（三对角方程组，后向欧拉）
  const n = 40, N = n + 1, C = new Array(N).fill(x.Cw / n), r = x.Rw / n;
  C[0] = x.Cs + x.Cw / (2 * n); C[n] = x.Cw / (2 * n) + CL42;
  const T = 3 * x.total, steps = 600, dt = T / steps, VDD = P42.VDD;
  let v = new Array(N).fill(0); const t = [0], v0 = [0], vn = [0];
  const a = new Array(N), b = new Array(N), c = new Array(N);
  for (let i = 0; i < N; i++) {
    const gl = i === 0 ? 1 / x.Rd : 1 / r, gr = i === n ? 0 : 1 / r;
    a[i] = i === 0 ? 0 : -1 / r; c[i] = i === n ? 0 : -1 / r; b[i] = C[i] / dt + gl + gr;
  }
  for (let s = 1; s <= steps; s++) {
    const d = v.map((vi, i) => C[i] / dt * vi + (i === 0 ? VDD / x.Rd : 0));
    const cp = new Array(N), dp = new Array(N);
    cp[0] = c[0] / b[0]; dp[0] = d[0] / b[0];
    for (let i = 1; i < N; i++) { const m = b[i] - a[i] * cp[i - 1]; cp[i] = c[i] / m; dp[i] = (d[i] - a[i] * dp[i - 1]) / m; }
    v[n] = dp[n]; for (let i = n - 1; i >= 0; i--) v[i] = dp[i] - cp[i] * v[i + 1];
    t.push(s * dt); v0.push(v[0]); vn.push(v[n]);
  }
  let t50 = null; for (let i = 1; i < vn.length; i++) if (vn[i] >= VDD / 2) { t50 = t[i - 1] + (t[i] - t[i - 1]) * (VDD / 2 - vn[i - 1]) / (vn[i] - vn[i - 1]); break; }
  return { t, v0, vn, t50 };
}

WQ.lab({
  title: ["实验 4.2 RC 线", "Lab 4.2 RC wires"],
  goal: ["看一个反相器经长导线驱动负载时，延时怎样随线长、金属层和驱动强弱变化；比较式 (4.2.4) 的估算与分段数值解。",
         "See how the delay of an inverter driving a load through a long wire depends on wire length, metal layer and driver strength; compare Eq. (4.2.4) with a segmented numerical solution."],
  scenes: [
    { id: "m1", robot: true, name: ["met1 最小线宽", "met1, minimum width"], hide: [], params: { L: { value: 1000 } },
      problem: { title: ["机器人问题：时钟线走哪一层", "Robot problem: which layer for the clock"],
                 text: ["时钟缓冲器经一条 met1 线把时钟送到计数器（20 Cinv）。线有多长时，导线本身的延时开始超过驱动器的延时？",
                        "The clock buffer drives a counter (20 Cinv) through a met1 wire. At what length does the wire's own delay overtake the driver's?"] } },
    { id: "m3", name: ["met3 最小线宽", "met3, minimum width"], hide: [],
      problem: { title: ["换到厚金属", "Move to a thick metal"],
                 text: ["met3 的方块电阻只有 met1 的约三分之一，最小线宽又宽一倍。同样的驱动，能走多长？",
                        "met3 has about a third of met1's sheet resistance and twice the minimum width. How far can the same driver go?"] } },
  ],
  params: [
    { id: "L", name: ["线长", "Wire length"], min: 100, max: 6000, step: 100, value: 500, unit: "μm", digits: 0 },
    { id: "size", name: ["驱动器尺寸（参考反相器的倍数）", "Driver size (× reference inverter)"], min: 1, max: 60, step: 1, value: 20, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "square", robot: true, text: ["met1，驱动器 40 倍：把线长分别设为 1000 μm 和 2000 μm，比较导线项——线长加倍，它变成几倍？", "met1, 40× driver: set the length to 1000 μm and then 2000 μm and compare the wire term. Doubling the length multiplies it by what?"],
      demo: { scene: "m1", set: { size: 40, L: 2000 }, press: [], wait: 1 } },
    { id: "equal", robot: true, text: ["met1，驱动器 20 倍：找到导线项与驱动项相差不到 10 % 的线长。", "met1, 20× driver: find the length where the wire term and the driver term agree within 10 %."],
      demo: { scene: "m1", set: { size: 20, L: 900 }, press: [], wait: 1 } },
    { id: "far", text: ["met3，驱动器 20 倍：找到总延时（估算）不超过 100 ps 的最长线长（再长 100 μm 就超过）。", "met3, 20× driver: find the longest wire whose estimated delay stays within 100 ps (100 μm more exceeds it)."],
      demo: { scene: "m3", set: { size: 20, L: 2100 }, press: [], wait: 1 } },
  ],
  think: ["驱动器加大能减小哪一项，不能减小哪一项？线很长时，为什么只加大驱动器不够？",
          "Which term does a stronger driver reduce, and which not? For a very long wire, why is a stronger driver alone not enough?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["始端", "near end"], color: "#e67e22" }, { name: ["末端", "far end"], color: "#1d6fb8" }],
  reset(api, s) { check42(api); },
  readouts(api, s) {
    const f = api.fmt, x = line42(api.scene, api.p), sm = sim42(x);
    return [[["导线电阻 Rw / 电容 Cw", "Wire Rw / Cw"], f(x.Rw, 0) + " Ω / " + f(x.Cw * 1e15, 1) + " fF"],
            [["驱动项 0.69Rd(Cself+Cw+CL)", "Driver term"], f(x.drv * 1e12, 1) + " ps"],
            [["导线项 0.38RwCw + 0.69RwCL", "Wire term"], f(x.wire * 1e12, 1) + " ps"],
            [["估算总延时", "Estimated delay"], f(x.total * 1e12, 1) + " ps"],
            [["数值解（40 段）", "Numerical (40 sections)"], sm.t50 == null ? "—" : f(sm.t50 * 1e12, 1) + " ps"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mu = css("--muted"), blue = "#1d6fb8", amber = "#e67e22";
    const x = line42(api.scene, api.p), sm = sim42(x), T = sm.t[sm.t.length - 1] * 1e12;
    const px = w * 0.08, py = h * 0.08, pw = w * 0.88, ph = h * 0.62;
    const ax = api.plot(px, py, pw, ph, [{ pts: sm.t.map((t, i) => [t * 1e12, sm.v0[i]]), color: amber }, { pts: sm.t.map((t, i) => [t * 1e12, sm.vn[i]]), color: blue }],
      { xmin: 0, xmax: T, ymin: 0, ymax: 1.9, xlabel: "t / ps", ylabel: "V" });
    api.line(px, ax.Y(0.9), px + pw, ax.Y(0.9), mu, 1, [3, 4]);
    if (sm.t50) { api.line(ax.X(sm.t50 * 1e12), py, ax.X(sm.t50 * 1e12), py + ph, ink, 1.2); api.label("t50", ax.X(sm.t50 * 1e12) + 4, py + 12, ink, 11); }
    api.label(api.fmt(T, 0) + " ps", px + pw, py + ph + 24, mu, 11, "right");
    // bottom: the two terms as stacked bar
    const by = py + ph + 40, bw = pw, bh = 16, tot = x.total;
    api.rect(px, by, bw * x.drv / tot, bh, amber); api.rect(px + bw * x.drv / tot, by, bw * x.wire / tot, bh, blue);
    api.label(api.T("驱动项", "driver"), px + 4, by + bh + 12, amber, 11);
    api.label(api.T("导线项", "wire"), px + bw - 4, by + bh + 12, blue, 11, "right");
  },
});

function check42(api) {
  const p = api.p, x = line42(api.scene, p);
  if (api.scene === "m1" && p.size === 40) {
    if (p.L === 1000) seen42.a = true;
    if (p.L === 2000) seen42.b = true;
    if (seen42.a && seen42.b) api.done("square");
  }
  if (api.scene === "m1" && p.size === 20 && Math.abs(x.wire - x.drv) <= 0.1 * x.drv) api.done("equal");
  if (api.scene === "m3" && p.size === 20) {
    const nxt = line42("m3", { L: p.L + 100, size: 20 });
    if (x.total <= 100e-12 && nxt.total > 100e-12) api.done("far");
  }
}
