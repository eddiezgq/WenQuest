// 实验 4.7 姿态插值（配 4.7 节）。从 I 转到给定的终止姿态：欧拉角插值、归一化线性插值、Slerp 三种做法同时播放。
WQ.lab({
  title: ["实验 4.7 姿态插值", "Lab 4.7 Orientation interpolation"],
  goal: ["比较三种插值：路径长短、角速度是否均匀；体会“最短路径”与“q 与 −q”的处理。", "Compare three interpolations: path length, evenness of speed; the shortest path and the ±q choice."],
  scenes: [
    { id: "tool", robot: true, name: ["工具换姿态", "Tool reorientation"],
      problem: { title: ["机器人问题：平稳地转过去", "Robot problem: turn smoothly"],
                 text: ["末端要在 1 s 内从起始姿态转到终止姿态，中间不能忽快忽慢，也不能绕远。", "The tool must reach the new attitude in 1 s, neither jerky nor taking a detour."] } },
    { id: "cam", name: ["相机云台", "Camera gimbal"],
      problem: { title: ["生活中的例子：云台转镜头", "Everyday example: a camera gimbal"], text: ["拍摄时镜头从一个方向平滑转到另一个方向。", "The lens swings smoothly from one view to another."] } },
  ],
  params: [
    { id: "yaw", name: ["终止偏航 ψ", "End yaw ψ"], min: -180, max: 180, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "pitch", name: ["终止俯仰 θ", "End pitch θ"], min: -89, max: 89, step: 1, value: 45, unit: "°", digits: 0 },
    { id: "roll", name: ["终止横滚 φ", "End roll φ"], min: -180, max: 180, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "flip", name: ["不做最短路径处理（0 否 / 1 是）", "Skip the shortest-path check (0/1)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["播放", "Play"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--red)", name: ["欧拉角插值", "Euler angles"] }, { color: "var(--accent)", name: ["归一化线性插值", "nlerp"] }, { color: "var(--amber)", name: ["Slerp", "Slerp"] }],
  tasks: [
    { id: "play", robot: true, text: ["播放算例 4.7.1（90°, 45°, 90°），比较三条角速度曲线。", "Play Example 4.7.1 (90°, 45°, 90°) and compare the three speed curves."],
      demo: { scene: "tool", set: { yaw: 90, pitch: 45, roll: 90, flip: 0 }, press: ["start"], wait: 2 } },
    { id: "long", robot: true, text: ["找一个终止姿态，使欧拉角插值的路径比最短路径长 50% 以上。", "Find an end pose where the Euler path is over 50% longer than the shortest."],
      demo: { scene: "tool", set: { yaw: 170, pitch: 80, roll: 170, flip: 0 }, press: [] } },
    { id: "flip", text: ["构造 q_A·q_B < 0 的情形，比较做与不做最短路径处理时 Slerp 转过的角度。", "Make q_A·q_B < 0 and compare Slerp with and without the shortest-path check."],
      demo: { scene: "cam", set: { yaw: 180, pitch: 0, roll: 120, flip: 1 }, press: [] } },
  ],
  think: ["欧拉角插值为什么会依赖于欧拉角的约定？Slerp 为什么不会？", "Why does Euler interpolation depend on the convention, and Slerp not?"],

  reset(api, s) { s.t = 0; s.hist = { e: [], n: [], s: [] }; },
  mul(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  zyx(ps, th, ph) {
    const c = Math.cos, sn = Math.sin;
    const Rz = [[c(ps), -sn(ps), 0], [sn(ps), c(ps), 0], [0, 0, 1]], Ry = [[c(th), 0, sn(th)], [0, 1, 0], [-sn(th), 0, c(th)]], Rx = [[1, 0, 0], [0, c(ph), -sn(ph)], [0, sn(ph), c(ph)]];
    return this.mul(Rz, this.mul(Ry, Rx));
  },
  qOf(R) { const q0 = 0.5 * Math.sqrt(Math.max(1e-12, 1 + R[0][0] + R[1][1] + R[2][2]));
    if (q0 > 0.05) return [q0, (R[2][1] - R[1][2]) / (4 * q0), (R[0][2] - R[2][0]) / (4 * q0), (R[1][0] - R[0][1]) / (4 * q0)];
    const tr = R[0][0] + R[1][1] + R[2][2], c = [1 + tr, 1 + 2 * R[0][0] - tr, 1 + 2 * R[1][1] - tr, 1 + 2 * R[2][2] - tr], i = c.indexOf(Math.max(...c)), s = Math.sqrt(c[i]) / 2, q = [0, 0, 0, 0];
    q[i] = s;
    const o = { 0: [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]], 1: [R[2][1] - R[1][2], R[0][1] + R[1][0], R[0][2] + R[2][0]],
      2: [R[0][2] - R[2][0], R[0][1] + R[1][0], R[1][2] + R[2][1]], 3: [R[1][0] - R[0][1], R[0][2] + R[2][0], R[1][2] + R[2][1]] }[i];
    [0, 1, 2, 3].filter((j) => j !== i).forEach((j, k) => { q[j] = o[k] / (4 * s); });
    return q; },
  RofQ(q) { const n = Math.hypot(...q), [a, b, c, d] = q.map((v) => v / n);
    return [[1 - 2 * (c * c + d * d), 2 * (b * c - a * d), 2 * (b * d + a * c)], [2 * (b * c + a * d), 1 - 2 * (b * b + d * d), 2 * (c * d - a * b)], [2 * (b * d - a * c), 2 * (c * d + a * b), 1 - 2 * (b * b + c * c)]]; },
  ang(A, B) { let t = 0; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) t += A[i][j] * B[i][j]; return Math.acos(Math.max(-1, Math.min(1, (t - 1) / 2))); },
  paths(api) {
    const d = Math.PI / 180, E = [api.p.yaw * d, api.p.pitch * d, api.p.roll * d];
    const RB = this.zyx(...E), qA = [1, 0, 0, 0];
    let qB = this.qOf(RB);
    // the start is q = (1,0,0,0): q_A·q_B = q_B0. Present q_B with a negative real part to see the flip.
    if (qB[0] > 0) qB = qB.map((v) => -v);
    let qS = qB.slice(), c = qA.reduce((a, v, i) => a + v * qS[i], 0);
    if (!api.p.flip && c < 0) { qS = qS.map((v) => -v); c = -c; }
    const om = Math.acos(Math.max(-1, Math.min(1, c)));
    const sl = (t) => om < 1e-9 ? qA : qA.map((v, i) => (Math.sin((1 - t) * om) * v + Math.sin(t * om) * qS[i]) / Math.sin(om));
    const nl = (t) => qA.map((v, i) => (1 - t) * v + t * qS[i]);
    return { E, RB, eul: (t) => this.zyx(E[0] * t, E[1] * t, E[2] * t), sl: (t) => this.RofQ(sl(t)), nl: (t) => this.RofQ(nl(t)), dot: qA.reduce((a, v, i) => a + v * qB[i], 0) };
  },
  lengths(api) {
    const P = this.paths(api), N = 200, L = { e: 0, n: 0, s: 0 };
    for (let i = 0; i < N; i++) { const a = i / N, b = (i + 1) / N;
      L.e += this.ang(P.eul(a), P.eul(b)); L.n += this.ang(P.nl(a), P.nl(b)); L.s += this.ang(P.sl(a), P.sl(b)); }
    return { L, direct: this.ang([[1, 0, 0], [0, 1, 0], [0, 0, 1]], P.RB), dot: P.dot };
  },
  update(dt, api, s) {
    const P = this.paths(api), t0 = s.t; s.t = Math.min(1, s.t + dt);
    const d = (f) => this.ang(f(t0), f(s.t)) / Math.max(1e-6, s.t - t0);
    s.hist.e.push([s.t, d(P.eul)]); s.hist.n.push([s.t, d(P.nl)]); s.hist.s.push([s.t, d(P.sl)]);
    if (s.t >= 1) { api.stop(); if (api.scene === "tool" && api.p.yaw === 90 && api.p.pitch === 45 && api.p.roll === 90) api.done("play"); }
  },
  readouts(api, s) {
    const { L, direct, dot } = this.lengths(api), g = 180 / Math.PI;
    if (api.scene === "tool" && L.e > 1.5 * direct) api.done("long");
    if (api.scene === "cam" && api.p.flip && L.s > direct * 1.01 + 1e-6) api.done("flip");
    return [[["最短转角", "shortest angle"], api.fmt(direct * g, 1) + "°"],
            [["欧拉角插值路径", "Euler path"], api.fmt(L.e * g, 1) + "°（" + api.fmt(L.e / Math.max(direct, 1e-9), 2) + "×）"],
            [["Slerp 路径", "Slerp path"], api.fmt(L.s * g, 1) + "°"],
            [["q_A·q_B（取 q_B₀ < 0）", "q_A·q_B (q_B0 < 0)"], api.fmt(dot, 3)]];
  },
  draw(api, s) {
    const { w, h } = api, m = 14;
    const P = this.paths(api), k = Math.min(w * 0.22, h * 0.36), cx = w * 0.25, cy = h * 0.55, az = -0.6, el = 0.35;
    const Pj = ([x, y, z]) => { const u = x * Math.cos(az) - y * Math.sin(az), v = x * Math.sin(az) + y * Math.cos(az); return [cx + k * u, cy - k * (z * Math.cos(el) - v * Math.sin(el))]; };
    api.circle(cx, cy, k, null, api.css("--grid"));
    const tip = (f, col) => { let prev = null; for (let i = 0; i <= 60; i++) { const R = f(i / 60), p = Pj([R[0][2], R[1][2], R[2][2]]); if (prev) api.line(...prev, ...p, col, 2.5); prev = p; } };
    tip(P.eul, api.css("--red")); tip(P.sl, api.css("--amber"));
    const t = s.t || 0, R = P.sl(t);
    api.arrow(cx, cy, ...Pj([R[0][2], R[1][2], R[2][2]]), api.css("--amber"), 3);
    api.label(api.T("z 轴指向的轨迹", "path of the z axis"), cx, cy + k + 16, api.css("--muted"), 12, "center");
    api.plot(w * 0.52, m + 6, w * 0.45, h - 2 * m - 30, [
      { pts: s.hist.e, color: api.css("--red") }, { pts: s.hist.n, color: api.css("--accent") }, { pts: s.hist.s, color: api.css("--amber") }],
      { xmin: 0, xmax: 1, ymin: 0, xlabel: "t", ylabel: api.T("角速度 / (rad/s)", "angular speed / (rad/s)") });
  },
});
