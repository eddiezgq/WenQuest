// 实验 7.2 积分方法与步长（配 7.2 节）。参数一改，程序立即用所选方法把整段过程算完；按“开始”回放。
// 连杆：θ̈ = −ω_n² sin θ，ω_n² = 29.43 s⁻²，从 90° 释放；方法：欧拉 (7.2.2)、RK4 (7.2.6)、辛欧拉 (7.2.9)、施特默-韦莱 (7.2.11)。
// 电机：ω̇ = (ω∞ − ω)/τ，τ = 19.02 ms，ω∞ = 237.7 rad/s；欧拉法 h > 2τ 发散（定理 7.2.2）。
// 陀螺仪：锥形运动 ω_b = (b, a sin bt, a cos bt)，a = 2、b = 3 rad/s（式 (7.2.18)）；欧拉法 (7.2.13)、李-欧拉 (7.2.14)、李-中点 (7.2.15)。
// 地球绕太阳：r̈ = −4π² r/|r|³（天文单位、年），离心率 0.1 的椭圆轨道。
WQ.lab({
  title: ["实验 7.2 积分方法与步长", "Lab 7.2 Integration methods and step size"],
  goal: ["用不同的积分方法和步长仿真同一个系统，看误差、稳定性、能量漂移和姿态的正交性。",
         "Simulate one system with different methods and step sizes; see the error, stability, energy drift and the orthogonality of the attitude."],
  scenes: [
    { id: "link", robot: true, name: ["连杆的长时间仿真", "A long simulation of the link"], hide: ["hM", "hG", "hO"],
      problem: { title: ["机器人问题：仿真软件该用哪种积分方法", "Robot problem: which integrator should the simulator use"],
                 text: ["无摩擦的连杆从水平位置释放，能量应当守恒。比较四种方法在长时间仿真中的能量。方法：0 欧拉，1 RK4，2 辛欧拉，3 施特默-韦莱。",
                        "A frictionless link is released from the horizontal; its energy should be conserved. Compare four methods over a long run. Method: 0 Euler, 1 RK4, 2 symplectic Euler, 3 Störmer–Verlet."] } },
    { id: "motor", robot: true, name: ["电机起动：步长与稳定性", "Motor start-up: step size and stability"], hide: ["hL", "hG", "hO", "dur"],
      params: { method: { min: 0, max: 1, step: 1, value: 0 } },
      problem: { title: ["机器人问题：步长取多大会出错", "Robot problem: how large a step is too large"],
                 text: ["电机起动 τω̇ + ω = Ku，τ = 19.02 ms。逐渐加大步长，找出仿真开始发散的步长。方法：0 欧拉，1 RK4。",
                        "Motor start-up τω̇ + ω = Ku with τ = 19.02 ms. Increase the step until the simulation starts to diverge. Method: 0 Euler, 1 RK4."] } },
    { id: "gyro", robot: true, name: ["由陀螺仪积分姿态", "Attitude from a gyroscope"], hide: ["hL", "hM", "hO", "dur"],
      params: { method: { min: 0, max: 2, step: 1, value: 0 } },
      problem: { title: ["机器人问题：四旋翼的姿态解算", "Robot problem: attitude of a quadrotor"],
                 text: ["四旋翼做锥形运动，陀螺仪给出物体角速度。积分 10 s，看 det R 是否保持为 1。方法：0 欧拉（矩阵元素），1 李-欧拉，2 李-中点。",
                        "A quadrotor moves on a cone; the gyroscope gives the body angular velocity. Integrate for 10 s and check whether det R stays 1. Method: 0 Euler (entries), 1 Lie–Euler, 2 Lie midpoint."] } },
    { id: "orbit", name: ["地球绕太阳", "The Earth around the Sun"], hide: ["hL", "hM", "hG", "dur"],
      problem: { title: ["生活中的例子：行星轨道会不会越飞越远", "Everyday example: does the orbit drift away"],
                 text: ["仿真一个离心率 0.1 的行星轨道 20 年。方法：0 欧拉，1 RK4，2 辛欧拉，3 施特默-韦莱。",
                        "Simulate a planet on an orbit of eccentricity 0.1 for 20 years. Method: 0 Euler, 1 RK4, 2 symplectic Euler, 3 Störmer–Verlet."] } },
  ],
  params: [
    { id: "method", name: ["方法（见场景说明）", "Method (see the scene)"], min: 0, max: 3, step: 1, value: 0, unit: "", digits: 0 },
    { id: "hL", name: ["步长 h", "Step h"], min: 0.005, max: 0.1, step: 0.005, value: 0.02, unit: "s", digits: 3 },
    { id: "dur", name: ["仿真时长", "Duration"], min: 10, max: 200, step: 10, value: 20, unit: "s", digits: 0 },
    { id: "hM", name: ["步长 h", "Step h"], min: 1, max: 60, step: 1, value: 5, unit: "ms", digits: 0 },
    { id: "hG", name: ["步长 h", "Step h"], min: 0.005, max: 0.1, step: 0.005, value: 0.02, unit: "s", digits: 3 },
    { id: "hO", name: ["步长 h", "Step h"], min: 1, max: 30, step: 1, value: 10, unit: "d", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["回放", "Play"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "euler", robot: true, text: ["连杆：欧拉法、h = 0.02 s、20 s，回放后读出能量增长到几倍（超过 2 倍时连杆已越过顶点）。", "Link: Euler, h = 0.02 s, 20 s; after playback read how many times the energy has grown (above 2 the link goes over the top)."],
      demo: { scene: "link", set: { method: 0, hL: 0.02, dur: 20 }, press: ["start"], wait: 8 } },
    { id: "symp", robot: true, text: ["连杆：辛欧拉法、h = 0.02 s、100 s 以上，能量误差始终在 ±5% 以内。", "Link: symplectic Euler, h = 0.02 s, 100 s or more; the energy error stays within ±5%."],
      demo: { scene: "link", set: { method: 2, hL: 0.02, dur: 100 }, press: ["start"], wait: 8 } },
    { id: "diverge", robot: true, text: ["电机：欧拉法，找到刚好发散的步长（不超过 42 ms），与 2τ = 38.0 ms 比较。", "Motor: Euler; find a step that just diverges (42 ms or less) and compare with 2τ = 38.0 ms."],
      demo: { scene: "motor", set: { method: 0, hM: 40 }, press: ["start"], wait: 6 } },
    { id: "gyro", robot: true, text: ["陀螺仪：欧拉法（矩阵元素）、h ≥ 0.02 s 积分 10 s，det R 超过 1.1；换成李-欧拉法，det R 保持为 1。", "Gyro: Euler on the entries, h ≥ 0.02 s for 10 s: det R exceeds 1.1; with Lie–Euler det R stays 1."],
      demo: { scene: "gyro", set: { method: 0, hG: 0.02 }, press: ["start"], wait: 6 } },
    { id: "orbit", text: ["地球轨道：施特默-韦莱法、h ≥ 10 d，20 年后能量误差小于 1%，轨道闭合；欧拉法则螺旋外逃。", "Orbit: Störmer–Verlet with h ≥ 10 d keeps the energy within 1% for 20 years and the orbit closes; Euler spirals out."],
      demo: { scene: "orbit", set: { method: 3, hO: 10 }, press: ["start"], wait: 6 } },
  ],
  think: ["RK4 每步要算 4 次加速度，韦莱法只算 1 次。计算量相同时，哪一个更适合仿真 1 小时？为什么？",
          "RK4 evaluates the acceleration 4 times per step, Verlet once. At equal cost, which suits a 1-hour simulation better, and why?"],

  // ---------- 通用的二阶系统一步：x = [q..., v...]，acc(q) 给出加速度
  step2(meth, acc, x, h) {
    const n = x.length / 2, q = x.slice(0, n), v = x.slice(n);
    const add = (a, b, k) => a.map((ai, i) => ai + k * b[i]);
    const f = (y) => { const yq = y.slice(0, n), yv = y.slice(n); return yv.concat(acc(yq)); };
    if (meth === 0) return add(x, f(x), h);
    if (meth === 1) { const k1 = f(x), k2 = f(add(x, k1, h / 2)), k3 = f(add(x, k2, h / 2)), k4 = f(add(x, k3, h));
      return x.map((xi, i) => xi + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])); }
    if (meth === 2) { const v1 = add(v, acc(q), h), q1 = add(q, v1, h); return q1.concat(v1); }
    const vh = add(v, acc(q), h / 2), q1 = add(q, vh, h), v1 = add(vh, acc(q1), h / 2); return q1.concat(v1);
  },
  // ---------- 3×3 矩阵
  mul(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  tr(A) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[j][i])); },
  det(A) { return A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]); },
  skew(w) { return [[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]]; },
  exp(w) { const t = Math.hypot(...w); if (t < 1e-14) return [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    const K = this.skew(w.map((x) => x / t)), K2 = this.mul(K, K), s = Math.sin(t), c = 1 - Math.cos(t);
    return [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + s * K[i][j] + c * K2[i][j])); },
  wb(t) { return [3, 2 * Math.sin(3 * t), 2 * Math.cos(3 * t)]; },
  truth(t) { return this.mul(this.exp([0, 0, 2 * t]), this.exp([3 * t, 0, 0])); },

  compute(api, s) {
    const meth = Math.round(api.p.method);
    s.series = []; s.frames = []; s.info = {};
    if (api.scene === "link") {
      const wn2 = 29.43, h = api.p.hL, T = api.p.dur, n = Math.round(T / h), acc = (q) => [-wn2 * Math.sin(q[0])];
      let x = [Math.PI / 2, 0]; const E0 = wn2;
      const every = Math.max(1, Math.round(n / 1500));
      let maxErr = 0;
      for (let k = 0; k <= n; k++) {
        const E = 0.5 * x[1] * x[1] + wn2 * (1 - Math.cos(x[0]));
        maxErr = Math.max(maxErr, Math.abs(E / E0 - 1));
        if (k % every === 0 || k === n) { s.series.push([k * h, E / E0]); s.frames.push(x[0]); }
        if (k < n) x = this.step2(meth, acc, x, h);
        if (!isFinite(x[0]) || Math.abs(x[1]) > 1e6) break;
      }
      s.info = { Eend: s.series[s.series.length - 1][1], maxErr, meth, h, T };
    } else if (api.scene === "motor") {
      const tau = 0.019017, winf = 237.72, h = api.p.hM / 1000, n = Math.ceil(0.4 / h), f = (w) => (winf - w) / tau;
      let w = 0; s.series.push([0, 0]);
      for (let k = 0; k < n; k++) {
        if (meth === 0) w = w + h * f(w);
        else { const k1 = f(w), k2 = f(w + h / 2 * k1), k3 = f(w + h / 2 * k2), k4 = f(w + h * k3); w = w + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); }
        s.series.push([(k + 1) * h * 1000, w]);
      }
      const last = s.series.slice(-3).map((p) => Math.abs(p[1] - winf));
      s.info = { diverged: last[2] > 1.5 * winf, factor: meth === 0 ? 1 - h / tau : null, meth, h };
    } else if (api.scene === "gyro") {
      const h = api.p.hG, n = Math.round(10 / h);
      let R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
      for (let k = 0; k <= n; k++) {
        const t = k * h;
        if (k % Math.max(1, Math.round(n / 300)) === 0 || k === n) {
          const RtR = this.mul(this.tr(R), R), D = this.mul(this.tr(R), this.truth(t));
          const orth = Math.sqrt([0, 1, 2].reduce((a, i) => a + [0, 1, 2].reduce((b, j) => b + (RtR[i][j] - (i === j ? 1 : 0)) ** 2, 0), 0));
          s.series.push([t, this.det(R)]); s.frames.push({ R, t, orth, err: Math.acos(Math.max(-1, Math.min(1, ((D[0][0] + D[1][1] + D[2][2]) / Math.cbrt(Math.max(1e-9, this.det(R)) ** 2) - 1) / 2))) * 180 / Math.PI });
        }
        if (k === n) break;
        if (meth === 0) { const W = this.skew(this.wb(t)); R = R.map((r, i) => [0, 1, 2].map((j) => r[j] + h * (R[i][0] * W[0][j] + R[i][1] * W[1][j] + R[i][2] * W[2][j]))); }
        else R = this.mul(R, this.exp(this.wb(meth === 1 ? t : t + h / 2).map((x) => x * h)));
      }
      const fl = s.frames[s.frames.length - 1];
      s.info = { det: this.det(R), orth: fl.orth, err: fl.err, meth, h };
    } else {
      const h = api.p.hO / 365.25, n = Math.round(20 / h), GM = 4 * Math.PI * Math.PI;
      const acc = (q) => { const r3 = Math.pow(Math.hypot(q[0], q[1]), 3); return [-GM * q[0] / r3, -GM * q[1] / r3]; };
      // 近日点 r = 0.9 AU，离心率 0.1：v = √(GM(1+e)/r)
      let x = [0.9, 0, 0, Math.sqrt(GM * 1.1 / 0.9)];
      const En = (y) => 0.5 * (y[2] * y[2] + y[3] * y[3]) - GM / Math.hypot(y[0], y[1]);
      const E0 = En(x); let maxErr = 0;
      const every = Math.max(1, Math.round(n / 2000));
      for (let k = 0; k <= n; k++) {
        maxErr = Math.max(maxErr, Math.abs(En(x) / E0 - 1));
        if (k % every === 0 || k === n) s.series.push([x[0], x[1], k * h]);
        if (k < n) x = this.step2(meth, acc, x, h);
        if (!isFinite(x[0]) || Math.hypot(x[0], x[1]) > 50) break;
      }
      s.info = { Eerr: Math.abs(En(x) / E0 - 1), maxErr, rEnd: Math.hypot(x[0], x[1]), meth, h: api.p.hO };
    }
  },
  reset(api, s) { this.compute(api, s); s.play = s.series.length - 1; s.finished = false; },
  start(api, s) { s.play = 0; s.finished = false; },
  update(dt, api, s) {
    s.play = Math.min(s.series.length - 1, s.play + dt * s.series.length / 4);      // 约 4 s 回放完
    if (s.play >= s.series.length - 1) { s.finished = true; api.stop(); }
  },
  readouts(api, s) {
    const I = s.info, M = ["欧拉", "RK4", "辛欧拉", "韦莱"], ME = ["Euler", "RK4", "symplectic Euler", "Verlet"];
    const GM = ["欧拉（矩阵元素）", "李-欧拉", "李-中点"], GE = ["Euler (entries)", "Lie–Euler", "Lie midpoint"];
    if (api.scene === "link") {
      if (s.finished) {
        if (I.meth === 0 && Math.abs(I.h - 0.02) < 1e-9 && I.T >= 20) api.done("euler");
        if (I.meth === 2 && Math.abs(I.h - 0.02) < 1e-9 && I.T >= 100 && I.maxErr < 0.05) api.done("symp");
      }
      return [[["方法", "method"], api.T(M[I.meth], ME[I.meth])], [["结束时 E/E(0)", "E/E(0) at the end"], api.fmt(I.Eend, 4)],
              [["最大能量误差", "largest energy error"], api.fmt(I.maxErr * 100, 3) + " %"],
              [["每步计算加速度的次数", "accelerations per step"], I.meth === 1 ? "4" : "1"]];
    }
    if (api.scene === "motor") {
      if (s.finished && I.meth === 0 && I.diverged && api.p.hM <= 42) api.done("diverge");
      return [[["方法", "method"], api.T(M[I.meth], ME[I.meth])], [["2τ（欧拉法的上限）", "2τ (Euler's limit)"], "38.03 ms"],
              [["RK4 的上限 2.785τ", "RK4's limit 2.785τ"], "52.97 ms"],
              [["放大因子 1 − h/τ", "factor 1 − h/τ"], I.factor === null ? "—" : api.fmt(I.factor, 3)],
              [["结果", "result"], I.diverged ? api.T("发散", "diverges") : api.T("收敛", "converges")]];
    }
    if (api.scene === "gyro") {
      if (s.finished && I.meth === 0 && I.h >= 0.02 - 1e-9 && I.det > 1.1) api.done("gyro");
      return [[["方法", "method"], api.T(GM[I.meth], GE[I.meth])], [["10 s 后 det R", "det R after 10 s"], I.det.toFixed(I.meth === 0 ? 4 : 12)],
              [["‖RᵀR − I‖", "‖RᵀR − I‖"], I.orth.toExponential(2)], [["姿态误差角", "attitude error"], api.fmt(I.err, 3) + "°"]];
    }
    if (s.finished && I.meth === 3 && I.h >= 10 && I.Eerr < 0.01 && I.maxErr < 0.05) api.done("orbit");
    return [[["方法", "method"], api.T(M[I.meth], ME[I.meth])], [["20 年后能量误差", "energy error after 20 years"], api.fmt(I.Eerr * 100, 3) + " %"],
            [["最大能量误差", "largest energy error"], api.fmt(I.maxErr * 100, 3) + " %"], [["20 年后到太阳的距离", "distance to the Sun after 20 years"], api.fmt(I.rEnd, 3) + " AU"]];
  },
  draw(api, s) {
    const { w, h } = api, k = Math.floor(s.play), I = s.info;
    if (api.scene === "link") {
      const cx = w * 0.17, cy = h * 0.42, L = Math.min(w * 0.13, h * 0.3), th = s.frames[k];
      api.line(cx - 30, cy, cx + 30, cy, api.css("--ground"), 3);
      api.line(cx, cy, cx + L * Math.sin(th), cy + L * Math.cos(th), api.css("--accent"), 10);
      api.circle(cx, cy, 6, api.css("--panel"), api.css("--ink"));
      api.label("t = " + api.fmt(s.series[k][0], 1) + " s", cx, cy + L + 30, api.css("--ink"), 13, "center");
      const ys = s.series.map((p) => p[1]), ymax = Math.max(1.2, Math.min(10, Math.max(...ys) * 1.05)), ymin = Math.min(0.8, Math.min(...ys) * 0.95);
      const P = api.plot(w * 0.36, 16, w * 0.6, h - 50, [{ pts: s.series.slice(0, k + 1), color: api.css("--accent") }],
        { xmin: 0, xmax: I.T, ymin, ymax, xlabel: "t / s", ylabel: "E / E(0)" });
      api.line(w * 0.36, P.Y(1), w * 0.96, P.Y(1), api.css("--muted"), 1, [5, 4]);
      if (ymax > 2) { api.line(w * 0.36, P.Y(2), w * 0.96, P.Y(2), api.css("--red"), 1, [3, 3]); api.label(api.T("越过顶点", "over the top"), w * 0.37, P.Y(2) - 9, api.css("--red"), 12); }
      return;
    }
    if (api.scene === "motor") {
      const tau = 0.019017, winf = 237.72, ex = []; for (let i = 0; i <= 80; i++) { const t = 400 * i / 80; ex.push([t, winf * (1 - Math.exp(-t / 1000 / tau))]); }
      const pts = s.series.slice(0, k + 1).map((p) => [p[0], Math.max(-400, Math.min(900, p[1]))]);
      api.plot(40, 16, w - 70, h - 50, [{ pts: ex, color: api.css("--muted") }, { pts, color: I.diverged ? api.css("--red") : api.css("--accent") }],
        { xmin: 0, xmax: 400, ymin: -400, ymax: 900, xlabel: "t / ms", ylabel: "ω / (rad/s)" });
      api.label(api.T("灰线：精确解", "grey: exact"), 50, h - 16, api.css("--muted"), 12);
      return;
    }
    if (api.scene === "gyro") {
      const fr = s.frames[Math.min(k, s.frames.length - 1)], cx = w * 0.22, cy = h * 0.55, sc = Math.min(w, h) * 0.22;
      const P = ([x, y, z]) => [cx + sc * (y - 0.5 * x), cy - sc * (z - 0.3 * x)];
      const cols = [api.css("--red"), api.css("--green"), api.css("--blue")], Rt = this.truth(fr.t);
      for (let i = 0; i < 3; i++) {
        const q = P([Rt[0][i], Rt[1][i], Rt[2][i]]); api.line(cx, cy, q[0], q[1], cols[i], 1.5, [4, 4]);
        const r = P([fr.R[0][i], fr.R[1][i], fr.R[2][i]]); api.arrow(cx, cy, r[0], r[1], cols[i], 3);
      }
      api.label(api.T("实线：积分结果；虚线：真实姿态", "solid: integrated; dashed: true"), 12, 18, api.css("--muted"), 12);
      api.label("t = " + api.fmt(fr.t, 2) + " s", cx, h - 16, api.css("--ink"), 13, "center");
      const ys = s.series.map((p) => p[1]), ymax = Math.max(1.05, Math.max(...ys) * 1.02);
      const PL = api.plot(w * 0.46, 16, w * 0.5, h - 50, [{ pts: s.series.slice(0, k + 1), color: api.css("--accent") }], { xmin: 0, xmax: 10, ymin: 0.98, ymax, xlabel: "t / s", ylabel: "det R" });
      api.line(w * 0.46, PL.Y(1), w * 0.96, PL.Y(1), api.css("--muted"), 1, [5, 4]);
      return;
    }
    const cx = w * 0.5, cy = h * 0.5, sc = Math.min(w, h) * 0.2;
    api.circle(cx, cy, 10, api.css("--amber"));
    for (let i = 1; i <= k; i++) { const a = s.series[i - 1], b = s.series[i]; api.line(cx + sc * a[0], cy - sc * a[1], cx + sc * b[0], cy - sc * b[1], api.css("--accent"), 1.2); }
    const p = s.series[k]; api.circle(cx + sc * p[0], cy - sc * p[1], 6, api.css("--blue"), api.css("--ink"));
    api.label(api.T("太阳", "Sun"), cx + 14, cy + 14, api.css("--amber"), 12);
    api.label(`t = ${api.fmt(p[2], 1)} ` + api.T("年", "yr"), 14, 18, api.css("--ink"), 13);
  },
});
