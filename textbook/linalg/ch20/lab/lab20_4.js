// 实验 20.4 控制器里的时钟（配 20.4 节）。控制器每个周期把时间增量 dt 加到一个浮点变量上：t ← fl(t + dt)。
// 在同一个二进制数量级 [2ᵉ, 2ᵉ⁺¹) 内，相邻浮点数的间距 ulp = 2^(e − p + 1)（p 为有效位数）不变，
// 每步实际加上的是“dt 舍入到 ulp 的整数倍”，所以可以一个数量级一个数量级地跳着算，不必逐步模拟上亿次。
// 另一种做法：用整数计数器 n 记周期数，需要时间时再算 fl(n·dt)，误差不累积。
// 半精度用舍入函数模拟；单精度用 Math.fround；双精度就是 JavaScript 的数。与程序 20.4.1 的结果一致。
WQ.lab({
  title: ["实验 20.4 控制器里的时钟", "Lab 20.4 The clock inside a controller"],
  goal: ["选择数的格式和控制周期，让控制器“运行”若干小时，看浮点时钟怎样偏慢、走快、停走；再改用整数计数器，看误差怎样消失。",
         "Choose the number format and the control period, let the controller run for hours, and watch the floating-point clock drift, speed up and stall; then switch to an integer counter and watch the error vanish."],
  scenes: [
    { id: "ctrl", robot: true, name: ["机器人控制器", "Robot controller"],
      problem: { title: ["机器人问题：为什么开机七小时后机器人停了？", "Robot problem: why does the robot stop after seven hours?"],
                 text: ["控制器每 1 ms 执行一次 t = t + 0.001。实验室里测试几十分钟没有问题，产线上连续运行，几小时后轨迹异常，七小时左右机器人停在原地。",
                        "Every 1 ms the controller executes t = t + 0.001. Tests of a few dozen minutes in the lab pass; on the production line the trajectory goes wrong after some hours and the robot stops after about seven."] } },
  ],
  params: [
    { id: "fmt", name: ["数的格式（0 半精度，1 单精度，2 双精度）", "Format (0 half, 1 single, 2 double)"], min: 0, max: 2, step: 1, value: 1, digits: 0 },
    { id: "dt", name: ["控制周期 dt", "Control period dt"], min: 1, max: 100, step: 1, value: 1, unit: " ms", digits: 0 },
    { id: "hrs", name: ["运行时间", "Running time"], min: 1, max: 100, step: 1, value: 8, unit: " h", digits: 0 },
    { id: "cnt", name: ["做法（0 浮点累加，1 整数计数 × dt）", "Method (0 float accumulation, 1 integer count × dt)"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "single", robot: true, text: ["单精度、dt = 1 ms、浮点累加：时钟在真实运行多少小时后停走？停走时读数是多少？", "Single, dt = 1 ms, float accumulation: after how many real hours does the clock stall? What does it read?"],
      demo: { scene: "ctrl", set: { fmt: 1, dt: 1, hrs: 8, cnt: 0 }, press: [] } },
    { id: "half", robot: true, text: ["半精度、dt = 1 ms：时钟在什么时候停走？", "Half precision, dt = 1 ms: when does the clock stall?"],
      demo: { scene: "ctrl", set: { fmt: 0, dt: 1, hrs: 1, cnt: 0 }, press: [] } },
    { id: "dt10", robot: true, text: ["单精度、dt = 10 ms：停走的时刻怎样变化？（运行时间要足够长）", "Single, dt = 10 ms: how does the stall time change? (run long enough)"],
      demo: { scene: "ctrl", set: { fmt: 1, dt: 10, hrs: 80, cnt: 0 }, press: [] } },
    { id: "count", robot: true, text: ["单精度、dt = 1 ms，改用整数计数器，运行 8 小时以上：读数误差还有多大？", "Single, dt = 1 ms, integer counter, 8 h or more: how large is the error now?"],
      demo: { scene: "ctrl", set: { fmt: 1, dt: 1, hrs: 8, cnt: 1 }, press: [] } },
  ],
  think: ["双精度、dt = 1 ms 的浮点时钟会停走吗？估计停走的时刻。为什么说“用整数记次数、用时再乘”是更好的习惯？",
          "Will a double-precision clock with dt = 1 ms ever stall? Estimate when. Why is “count in integers, multiply when needed” the better habit?"],

  P: [11, 24, 53], NAMES: [["半精度", "half"], ["单精度", "single"], ["双精度", "double"]],
  fl(x, p) {                                   // 舍入到 p 位有效数字（就近舍入、偶数优先）
    if (p === 53 || x === 0) return x;
    if (p === 24) return Math.fround(x);
    const a = Math.abs(x);
    let e = Math.floor(Math.log2(a));
    if (Math.pow(2, e) > a) e -= 1;
    if (Math.pow(2, e + 1) <= a) e += 1;
    const ulp = Math.pow(2, Math.max(e, -14) - (p - 1));
    const q = a / ulp, fq = Math.floor(q);
    const r = q - fq === 0.5 ? (fq % 2 === 0 ? fq : fq + 1) : Math.round(q);
    const v = r * ulp;
    return v > 65504 ? Infinity : Math.sign(x) * v;
  },
  sim(api) {
    const key = [api.p.fmt, api.p.dt, api.p.hrs, api.p.cnt].join(",");
    if (this._c && this._c.key === key) return this._c;
    const p = this.P[api.p.fmt], dt = api.p.dt / 1000, dtf = this.fl(dt, p);
    const total = Math.round(api.p.hrs * 3600 / dt), pts = [];
    const nS = 400, marks = Array.from({ length: nS + 1 }, (_, i) => Math.round(total * i / nS));
    let stall = null, fast = null;
    if (api.p.cnt === 1) {
      for (const n of marks) { const v = this.fl(n * dtf, p); pts.push([n * dt / 3600, Number.isFinite(v) ? v - n * dt : NaN]); }        // n 是精确的整数，只在相乘时舍入一次
    } else {
      let clock = 0, steps = 0, mi = 0;
      while (mi < marks.length) {
        if (steps >= marks[mi]) { pts.push([marks[mi] * dt / 3600, clock - marks[mi] * dt]); mi++; continue; }
        if (clock === 0) { clock = dtf; steps = 1; continue; }
        let e = Math.floor(Math.log2(clock));
        if (Math.pow(2, e) > clock) e -= 1;
        if (Math.pow(2, e + 1) <= clock) e += 1;
        const ulp = Math.pow(2, e - (p - 1)), inc = Math.round(dtf / ulp) * ulp;
        if (inc === 0) { if (!stall) stall = { real: steps * dt, clock }; steps = marks[mi]; continue; }
        if (inc > 1.5 * dt && !fast) fast = { real: steps * dt, clock, inc };
        const n = Math.min(Math.ceil((Math.pow(2, e + 1) - clock) / inc), marks[mi] - steps);
        clock += n * inc; steps += n;
        if (!Number.isFinite(clock)) { stall = stall || { real: steps * dt, clock: 65504 }; clock = 65504; }
      }
    }
    this._c = { key, pts, stall, fast, dtf, p };
    return this._c;
  },
  reset(api, s) {},
  readouts(api, s) {
    const R = this.sim(api), f = api.fmt, eps = Math.pow(2, 1 - R.p);
    const fin = R.pts.filter((q) => Number.isFinite(q[1])), last = fin.length ? fin[fin.length - 1] : [0, NaN], over = fin.length < R.pts.length;
    const nm = api.T(this.NAMES[api.p.fmt][0], this.NAMES[api.p.fmt][1]);
    if (api.p.cnt === 0 && api.p.fmt === 1 && api.p.dt === 1 && R.stall) api.done("single");
    if (api.p.cnt === 0 && api.p.fmt === 0 && api.p.dt === 1 && R.stall) api.done("half");
    if (api.p.cnt === 0 && api.p.fmt === 1 && api.p.dt === 10 && R.stall) api.done("dt10");
    if (api.p.cnt === 1 && api.p.fmt === 1 && api.p.dt === 1 && api.p.hrs >= 8 && Math.abs(last[1]) < 0.01) api.done("count");
    const fmtT = (sec) => sec >= 3600 ? f(sec / 3600, 2) + " h" : f(sec, 2) + " s";
    return [[["格式与机器精度 ε", "Format and machine epsilon ε"], nm + "，ε = " + eps.toExponential(2)],
            [["实际存的 dt", "dt as stored"], R.dtf.toPrecision(10) + " s"],
            [["做法", "Method"], api.p.cnt ? api.T("整数计数 × dt", "integer count × dt") : api.T("浮点累加 t ← t + dt", "float accumulation t ← t + dt")],
            [["运行结束时：读数 − 真实时间", "At the end: reading − real time"], over ? api.T("读数超出该格式能表示的范围（第 ", "reading exceeds the format’s range (at ") + f(last[0], 2) + api.T(" h 以后）", " h on)") : f(last[1], 4) + " s"],
            [["开始走快（每步多加）", "Starts running fast"], R.fast ? api.T("真实 ", "real ") + fmtT(R.fast.real) + api.T("，每步加 ", ", adds ") + f(R.fast.inc * 1000, 3) + " ms" : "—"],
            [["停走", "Stalls"], R.stall ? api.T("真实 ", "real ") + fmtT(R.stall.real) + api.T("，读数 ", ", reading ") + fmtT(R.stall.clock) : api.T("在运行时间内没有停走", "does not stall within the run")]];
  },
  draw(api, s) {
    const R = this.sim(api), { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink");
    const x0 = 70, x1 = w - 30, y0 = 30, y1 = h - 50;
    const ys = R.pts.map((q) => q[1]).filter(Number.isFinite), lo = Math.min(0, ...ys), hi = Math.max(0, ...ys), span = (hi - lo) || 1e-9;
    const X = (v) => x0 + (x1 - x0) * v / api.p.hrs, Y = (v) => y1 - (y1 - y0) * (v - lo) / span;
    api.rect(x0, y0, x1 - x0, y1 - y0, null, mu);
    api.line(x0, Y(0), x1, Y(0), mu, 1, [4, 4]);
    for (let i = 1; i < R.pts.length; i++) if (Number.isFinite(R.pts[i][1]) && Number.isFinite(R.pts[i - 1][1])) api.line(X(R.pts[i - 1][0]), Y(R.pts[i - 1][1]), X(R.pts[i][0]), Y(R.pts[i][1]), api.css("--red"), 2);
    if (R.stall) { const xs = X(R.stall.real / 3600); api.line(xs, y0, xs, y1, api.css("--amber"), 1.5, [6, 4]); api.label(api.T("停走", "stall"), xs + 4, y0 + 14, api.css("--amber"), 12); }
    api.label(api.T("读数 − 真实时间 / s（纵轴范围 ", "reading − real time / s (range ") + lo.toExponential(1) + " … " + hi.toExponential(1) + ")", x0, y0 - 10, mu, 11);
    api.label(api.T("真实运行时间 / h：0 … ", "real running time / h: 0 … ") + api.p.hrs, x0, y1 + 30, mu, 11);
  },
});
