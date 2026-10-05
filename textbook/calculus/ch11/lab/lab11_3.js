// 实验 11.3 运动规划：梯形与 S 形速度曲线（配 11.3 节）。给定位移和速度、加速度、加加速度的上限，
// 求最短时间的运动；比较梯形、S 形与五次多项式三种曲线的时间和平顺程度。“机器人”场景是 UR5e 的一个关节，另一个场景是电梯。
WQ.lab({
  title: ["实验 11.3 运动规划：梯形与 S 形速度曲线", "Lab 11.3 Motion planning: trapezoidal and S-curve profiles"],
  goal: ["在速度、加速度（和加加速度）的限制下，让关节最快地完成一次运动；看清梯形曲线何时退化成三角形，S 形曲线用多少时间换来了有限的加加速度，五次多项式为什么慢。",
         "Move a joint as fast as the speed, acceleration (and jerk) limits allow; see when the trapezoid degenerates into a triangle, how much time the S-curve spends to keep the jerk finite, and why the quintic is slower."],
  scenes: [
    { id: "joint", robot: true, name: ["机械臂关节", "Robot joint"], hide: ["Dl", "Vl", "Jl"],
      problem: { title: ["机器人问题：这一次转动最快要多久？", "Robot problem: how fast can this move be?"],
                 text: ["UR5e 的关节最大角速度 180°/s；加速度、加加速度的上限由减速器和结构的承受能力决定。选择曲线和限值，求最短时间，并比较峰值加加速度。",
                        "UR5e joints turn at up to 180°/s; the acceleration and jerk limits come from the gearbox and the structure. Choose the profile and limits, find the minimum time and compare the peak jerk."] } },
    { id: "lift", name: ["电梯", "Elevator"], hide: ["D", "V", "A", "J"],
      problem: { title: ["生活中的例子：电梯为什么起停都很柔和？", "Everyday example: why does a lift start and stop so gently?"],
                 text: ["乘客对加速度的突变（加加速度）很敏感。电梯的速度曲线就是 S 形曲线：额定速度、加速度（这里固定为 1 m/s²）和加加速度都有舒适性的限制。",
                        "Passengers are sensitive to sudden changes of acceleration (jerk). Lift speed profiles are S-curves, with comfort limits on speed, acceleration (fixed here at 1 m/s²) and jerk."] } },
  ],
  params: [
    { id: "p", name: ["曲线：1 梯形，2 S 形，3 五次多项式", "Profile: 1 trapezoid, 2 S-curve, 3 quintic"], min: 1, max: 3, step: 1, value: 1, digits: 0 },
    { id: "D", name: ["转角 D", "Angle D"], min: 5, max: 180, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "V", name: ["角速度上限 V", "Speed limit V"], min: 30, max: 180, step: 1, value: 180, unit: "°/s", digits: 0 },
    { id: "A", name: ["角加速度上限 A", "Acceleration limit A"], min: 100, max: 1000, step: 10, value: 400, unit: "°/s²", digits: 0 },
    { id: "J", name: ["角加加速度上限 J", "Jerk limit J"], min: 500, max: 20000, step: 100, value: 4000, unit: "°/s³", digits: 0 },
    { id: "Dl", name: ["运行距离 D", "Travel D"], min: 3, max: 60, step: 0.5, value: 30, unit: "m", digits: 1 },
    { id: "Vl", name: ["额定速度 V", "Rated speed V"], min: 1, max: 4, step: 0.1, value: 2.5, unit: "m/s", digits: 1 },
    { id: "Jl", name: ["加加速度上限 J", "Jerk limit J"], min: 0.3, max: 3, step: 0.05, value: 1, unit: "m/s³", digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["角速度 / 速度", "speed"], color: "#1f77b4" }, { name: ["角加速度 / 加速度", "acceleration"], color: "#d62728" }, { name: ["加加速度", "jerk"], color: "#2ca02c" }],
  tasks: [
    { id: "trap", robot: true, text: ["选梯形曲线，D = 90°，V = 180°/s，A = 400°/s²，读出最短时间（应为 0.95 s）。", "Choose the trapezoid with D = 90°, V = 180°/s, A = 400°/s² and read the minimum time (0.95 s)."],
      demo: { scene: "joint", set: { p: 1, D: 90, V: 180, A: 400 }, wait: 1 } },
    { id: "tri", robot: true, text: ["保持 V = 180°/s、A = 400°/s²，把转角减小到梯形退化成三角形（达不到 V）。临界转角是多少？", "Keep V = 180°/s and A = 400°/s² and reduce the angle until the trapezoid becomes a triangle (V not reached). What is the critical angle?"],
      demo: { scene: "joint", set: { p: 1, D: 60, V: 180, A: 400 }, wait: 1 } },
    { id: "scurve", robot: true, text: ["选 S 形曲线，D = 90°，V = 180°/s，A = 400°/s²，调整 J，使总时间不超过 1.0 s。J 至少多大？", "Choose the S-curve with D = 90°, V = 180°/s, A = 400°/s²; adjust J so the time is at most 1.0 s. How large must J be?"],
      demo: { scene: "joint", set: { p: 2, D: 90, V: 180, A: 400, J: 8000 }, wait: 1 } },
    { id: "quintic", robot: true, text: ["同样的限值（D = 90°，V = 180°/s，A = 400°/s²，J = 4000°/s³）换成五次多项式，比梯形多用多少时间？", "With the same limits (D = 90°, V = 180°/s, A = 400°/s², J = 4000°/s³) switch to the quintic: how much longer than the trapezoid?"],
      demo: { scene: "joint", set: { p: 3, D: 90, V: 180, A: 400, J: 4000 }, wait: 1 } },
    { id: "lift", text: ["电梯运行 30 m，额定速度 2.5 m/s，加速度 1 m/s²，加加速度 1 m/s³，用 S 形曲线，读出运行时间。", "A lift travels 30 m at 2.5 m/s rated speed, 1 m/s² acceleration and 1 m/s³ jerk on an S-curve: read the travel time."],
      demo: { scene: "lift", set: { p: 2, Dl: 30, Vl: 2.5, Jl: 1 }, wait: 1 } },
  ],
  think: ["梯形曲线时间最短，为什么工业机器人和电梯仍普遍用 S 形曲线？加加速度为无穷大意味着什么？", "The trapezoid is fastest; why do industrial robots and lifts still use S-curves? What does infinite jerk mean physically?"],

  lim(api) {
    const p = api.p;
    return api.scene === "lift" ? { D: p.Dl, V: p.Vl, A: 1.0, J: p.Jl, u: "m", us: "m/s" } : { D: p.D, V: p.V, A: p.A, J: p.J, u: "°", us: "°/s" };
  },
  // 返回分段常值的段列表 [时长, 值, "a" 加速度 或 "j" 加加速度] 以及说明
  plan(kind, D, V, A, J) {
    if (kind === 1) {
      const Vr = Math.min(V, Math.sqrt(A * D)), ta = Vr / A, tv = D / Vr - Vr / A;
      return { segs: [[ta, A, "a"], [tv, 0, "a"], [ta, -A, "a"]], Vr, Ar: A, tri: Vr < V - 1e-9 };
    }
    if (kind === 2) {
      const dist = (v) => { const a = Math.min(A, Math.sqrt(v * J)); return v * (v / a + a / J); };
      let Vr = V;
      if (dist(V) > D) { let lo = 0, hi = V; for (let i = 0; i < 80; i++) { const m = (lo + hi) / 2; if (dist(m) > D) hi = m; else lo = m; } Vr = lo; }
      const Ar = Math.min(A, Math.sqrt(Vr * J)), tj = Ar / J, ta = Math.max(0, Vr / Ar - Ar / J), tv = Math.max(0, (D - dist(Vr)) / Vr);
      return { segs: [[tj, J, "j"], [ta, 0, "j"], [tj, -J, "j"], [tv, 0, "j"], [tj, -J, "j"], [ta, 0, "j"], [tj, J, "j"]], Vr, Ar, tri: Vr < V - 1e-9 };
    }
    const T = Math.max(15 * D / (8 * V), Math.sqrt(10 * D / (Math.sqrt(3) * A)), Math.cbrt(60 * D / J));
    return { quintic: true, T, Vr: 15 * D / (8 * T), Ar: 10 * D / (Math.sqrt(3) * T * T), Jr: 60 * D / T ** 3 };
  },
  curves(api) {
    const L = this.lim(api), P = this.plan(api.p.p, L.D, L.V, L.A, L.J), out = { t: [], w: [], a: [], j: [], spikes: [] };
    if (P.quintic) {
      const T = P.T, D = L.D;
      for (let i = 0; i <= 400; i++) {
        const t = T * i / 400, s = t / T;
        out.t.push(t); out.w.push(D / T * (30 * s * s - 60 * s ** 3 + 30 * s ** 4)); out.a.push(D / T ** 2 * (60 * s - 180 * s * s + 120 * s ** 3)); out.j.push(D / T ** 3 * (60 - 360 * s + 360 * s * s));
      }
      return { ...out, T, P, L };
    }
    let t = 0, w = 0, a = 0, prevA = 0;
    out.t.push(0); out.w.push(0); out.a.push(0); out.j.push(0);
    P.segs.forEach(([dur, val, kind]) => {
      if (kind === "a" && val !== prevA && dur > 0) out.spikes.push([t, val - prevA]);
      const n = Math.max(1, Math.ceil(dur / 0.002));
      for (let i = 0; i < n; i++) {
        const h = dur / n;
        if (kind === "j") { w += a * h + val * h * h / 2; a += val * h; } else { a = val; w += val * h; }
        t += h; out.t.push(t); out.w.push(w); out.a.push(a); out.j.push(kind === "j" ? val : 0);
      }
      if (kind === "a" && dur > 0) prevA = val;
    });
    if (api.p.p === 1) out.spikes.push([t, -prevA]);
    return { ...out, T: t, P, L };
  },
  reset() {},
  readouts(api) {
    const C = this.curves(api), L = C.L, P = C.P, p = api.p;
    const jpk = p.p === 1 ? "∞" : (p.p === 2 ? L.J : P.Jr).toFixed(1);
    if (api.scene === "joint") {
      if (p.p === 1 && p.D === 90 && p.V === 180 && p.A === 400 && Math.abs(C.T - 0.95) < 1e-3) api.done("trap");
      if (p.p === 1 && p.V === 180 && p.A === 400 && P.tri) api.done("tri");
      if (p.p === 2 && p.D === 90 && p.V === 180 && p.A === 400 && C.T <= 1.0 + 1e-6) api.done("scurve");
      if (p.p === 3 && p.D === 90 && p.V === 180 && p.A === 400 && p.J === 4000) api.done("quintic");
    } else if (p.p === 2 && Math.abs(p.Dl - 30) < 1e-9 && Math.abs(p.Vl - 2.5) < 1e-9 && Math.abs(p.Jl - 1) < 1e-9) api.done("lift");
    return [[["曲线", "Profile"], [api.T("梯形", "trapezoid"), api.T("S 形", "S-curve"), api.T("五次多项式", "quintic")][p.p - 1]],
            [["最短时间", "Minimum time"], C.T.toFixed(3) + " s"],
            [["实际最高速度", "Peak speed"], P.Vr.toFixed(1) + " " + L.us + (P.tri ? api.T("（达不到上限）", " (limit not reached)") : "")],
            [["实际最大加速度", "Peak acceleration"], P.Ar.toFixed(1) + " " + L.us + "²"],
            [["最大加加速度", "Peak jerk"], jpk + (jpk === "∞" ? "" : " " + L.us + "³")]];
  },
  draw(api) {
    const C = this.curves(api), L = C.L, w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), green = api.css("--green");
    const H = (h - 120) / 3, T = Math.max(C.T, 0.01) * 1.05, jt = api.p.p !== 1;
    const rows = [[C.w, L.V * 1.15, blue, api.T("速度", "speed")], [C.a, L.A * 1.25, red, api.T("加速度", "acceleration")], [C.j, (api.p.p === 1 ? 1 : Math.max(...C.j.map(Math.abs))) * 1.3, green, api.T("加加速度", "jerk")]];
    rows.forEach(([ys, m, col, name], r) => {
      const G = api.graph({ x: 70, y: 20 + r * (H + 34), w: w - 90, h: H, xmin: 0, xmax: T, ymin: r === 0 ? 0 : -m, ymax: m, xlabel: r === 2 ? "t / s" : "", ylabel: name, ticks: r < 2 || jt });
      G.axes();
      G.pts(C.t.map((t, i) => [t, ys[i]]), col, 2);
      if (r === 2 && api.p.p === 1) C.spikes.forEach(([t, d]) => G.seg(t, 0, t, Math.sign(d) * m * 0.85, col, 3));
    });
  },
});
