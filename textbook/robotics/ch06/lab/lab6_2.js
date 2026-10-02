// 实验 6.2 陀螺仪积分：物体角速度要右乘（配 6.2 节）。物体先绕自身 x 轴转 a₁，再绕自身 y 轴转 a₂；
// 陀螺仪测得的是物体角速度 ω_b。按 Ṙ = R[ω_b]（式 (6.2.5)）逐步右乘 e^{[ω_b]Δt} 得到正确姿态；
// 误把 ω_b 当成空间角速度左乘，结果相当于绕固定轴依次转动，一般是错的。
WQ.lab({
  title: ["实验 6.2 陀螺仪积分：物体角速度要右乘", "Lab 6.2 Integrating a gyroscope: body rates multiply on the right"],
  goal: ["用陀螺仪读数（物体角速度）积分姿态，比较右乘与左乘两种做法，理解 Ṙ = R[ω_b] = [ω_s]R。",
         "Integrate the attitude from gyroscope readings (body angular velocity); compare right and left multiplication and see why Ṙ = R[ω_b] = [ω_s]R."],
  scenes: [
    { id: "quad", robot: true, name: ["四旋翼的姿态解算", "Quadrotor attitude estimation"],
      problem: { title: ["机器人问题：飞控怎样由陀螺仪算姿态", "Robot problem: attitude from the gyroscope"],
                 text: ["四旋翼先横滚 a₁（绕自身 x 轴），再俯仰 a₂（绕自身 y 轴）。机载陀螺仪每个周期给出物体角速度 ω_b，飞控要由它积分出姿态 R。",
                        "The quadrotor first rolls a₁ (own x axis), then pitches a₂ (own y axis). The gyroscope gives the body angular velocity ω_b each cycle; the flight controller integrates it into the attitude R."] } },
    { id: "phone", name: ["转动手机", "Turning a phone"],
      problem: { title: ["生活中的例子：手机的屏幕方向", "Everyday example: a phone's screen orientation"],
                 text: ["手机里也有陀螺仪。把手机先绕长边转、再绕短边转，它要算出屏幕现在朝哪里。",
                        "Phones carry gyroscopes too. Turn the phone about its long edge, then its short edge; it must work out where the screen now faces."] } },
  ],
  params: [
    { id: "a1", name: ["第一段：绕自身 x 轴转 a₁", "Stage 1: a₁ about own x"], min: -180, max: 180, step: 5, value: 90, unit: "°", digits: 0 },
    { id: "a2", name: ["第二段：绕自身 y 轴转 a₂", "Stage 2: a₂ about own y"], min: -180, max: 180, step: 5, value: 90, unit: "°", digits: 0 },
  ],
  buttons: [
    { id: "start", name: ["开始：右乘（R ← R e^[ω_b]Δt）", "Start: right (R ← R e^[ω_b]Δt)"], primary: true },
    { id: "wrong", name: ["开始：左乘（R ← e^[ω_b]Δt R）", "Start: left (R ← e^[ω_b]Δt R)"] },
    { id: "reset", name: ["重置", "Reset"] },
  ],
  tasks: [
    { id: "right", robot: true, text: ["a₁ = a₂ = 90°，按右乘积分：结束时与真实姿态的误差小于 0.5°。", "a₁ = a₂ = 90°, integrate by right multiplication: final error below 0.5°."],
      demo: { scene: "quad", set: { a1: 90, a2: 90 }, press: ["start"], wait: 4 } },
    { id: "left", robot: true, text: ["同样的动作改用左乘：误差很大。读出误差角。", "Same motion, left multiplication: a large error. Read the error angle."],
      demo: { scene: "quad", set: { a1: 90, a2: 90 }, press: ["wrong"], wait: 4 } },
    { id: "one", robot: true, text: ["令 a₂ = 0（只绕一根轴转）：左乘也没有误差。", "Set a₂ = 0 (one axis only): left multiplication is then error-free too."],
      demo: { scene: "quad", set: { a1: 90, a2: 0 }, press: ["wrong"], wait: 4 } },
    { id: "phone", text: ["手机先绕长边转 90°、再绕短边转 90°，用右乘算出屏幕方向。", "Turn the phone 90° about its long edge, then 90° about its short edge; get the screen direction by right multiplication."],
      demo: { scene: "phone", set: { a1: 90, a2: 90 }, press: ["start"], wait: 4 } },
  ],
  think: ["两段转动的次序对调（先绕 y、再绕 x），右乘的结果会变吗？左乘呢？", "Swap the two stages (y first, then x). Does the right-multiplication result change? And the left one?"],

  // ---- 3×3 矩阵工具
  mul(A, B) { return A.map((r) => [0, 1, 2].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); },
  mv(A, v) { return A.map((r) => r[0] * v[0] + r[1] * v[1] + r[2] * v[2]); },
  tr(A) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[j][i])); },
  exp(w) {            // 罗德里格斯公式，w 为指数坐标
    const t = Math.hypot(...w); if (t < 1e-12) return [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    const k = w.map((x) => x / t), K = [[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]], K2 = this.mul(K, K), s = Math.sin(t), c = 1 - Math.cos(t);
    return [0, 1, 2].map((i) => [0, 1, 2].map((j) => (i === j ? 1 : 0) + s * K[i][j] + c * K2[i][j]));
  },
  errDeg(A, B) { const M = this.mul(this.tr(A), B), c = Math.max(-1, Math.min(1, (M[0][0] + M[1][1] + M[2][2] - 1) / 2)); return Math.acos(c) * 180 / Math.PI; },
  truth(api) { const d = Math.PI / 180; return this.mul(this.exp([api.p.a1 * d, 0, 0]), this.exp([0, api.p.a2 * d, 0])); },
  wb(api, t) { const d = Math.PI / 180; return t < 1 ? [api.p.a1 * d, 0, 0] : [0, api.p.a2 * d, 0]; },   // 每段 1 s

  reset(api, s) { s.R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; s.time = 0; s.method = null; s.finished = false; },
  start(api, s) { s.method = "right"; },
  action(id, api, s) { if (id === "wrong") { this.reset(api, s); s.method = "left"; api.t = 0; api.running = true; } },
  update(dt, api, s) {
    if (!s.method || s.finished) return;
    let left = Math.min(dt, 2 - s.time);
    while (left > 1e-12) {           // 不跨越两段的分界
      const h = s.time < 1 ? Math.min(left, 1 - s.time) : left;
      const E = this.exp(this.wb(api, s.time + 1e-9).map((x) => x * h));
      s.R = s.method === "right" ? this.mul(s.R, E) : this.mul(E, s.R);
      s.time += h; left -= h;
    }
    if (s.time >= 2 - 1e-9) { s.finished = true; api.stop(); }
  },
  readouts(api, s) {
    if (!s.R) return [];
    const e = this.errDeg(s.R, this.truth(api)), w = s.method ? this.wb(api, Math.min(s.time, 1.999)) : [0, 0, 0], ws = this.mv(s.R, w);
    if (s.finished) {
      if (api.scene === "quad" && s.method === "right" && api.p.a1 === 90 && api.p.a2 === 90 && e < 0.5) api.done("right");
      if (api.scene === "quad" && s.method === "left" && api.p.a1 === 90 && api.p.a2 === 90 && e > 10) api.done("left");
      if (api.scene === "quad" && s.method === "left" && api.p.a2 === 0 && api.p.a1 !== 0 && e < 0.5) api.done("one");
      if (api.scene === "phone" && s.method === "right" && api.p.a1 === 90 && api.p.a2 === 90 && e < 0.5) api.done("phone");
    }
    const v = (x) => `(${x.map((y) => api.fmt(y, 2)).join(", ")})`;
    return [[["时间", "time"], api.fmt(s.time, 2) + " s"],
            [["陀螺仪读数 ω_b", "gyro reading ω_b"], v(w) + " rad/s"],
            [["空间角速度 ω_s = Rω_b", "spatial ω_s = Rω_b"], v(ws) + " rad/s"],
            [["与真实姿态的误差角", "error from the true attitude"], api.fmt(e, 2) + "°"]];
  },
  draw(api, s) {
    if (!s.R) return;
    const { w, h } = api, cx = w / 2, cy = h * 0.55, k = Math.min(w, h) * 0.3, az = -0.7, el = 0.4;
    const P = ([x, y, z]) => { const u = x * Math.cos(az) - y * Math.sin(az), v = x * Math.sin(az) + y * Math.cos(az); return [cx + k * u, cy - k * (z * Math.cos(el) - v * Math.sin(el))]; };
    const cols = [api.css("--red"), api.css("--green"), api.css("--blue")];
    for (let i = 0; i < 3; i++) { const e = [0, 0, 0]; e[i] = 1.3; api.line(cx, cy, ...P(e), cols[i], 1, [3, 4]); }
    api.label("{s}", cx - 30, cy + 14, api.css("--muted"), 13);
    const dims = api.scene === "phone" ? [0.45, 0.9, 0.06] : [0.7, 0.7, 0.12];
    const drawBox = (R, color, dash, width) => {
      const V = []; for (const a of [-1, 1]) for (const b of [-1, 1]) for (const c of [-1, 1]) V.push(P(this.mv(R, [a * dims[0] / 2, b * dims[1] / 2, c * dims[2] / 2])));
      [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7], [0, 4], [1, 5], [2, 6], [3, 7]].forEach(([i, j]) => api.line(...V[i], ...V[j], color, width, dash));
    };
    drawBox(this.truth(api), api.css("--muted"), [5, 4], 1);
    drawBox(s.R, api.css("--accent"), null, 2.2);
    if (api.scene === "quad") {         // 四个旋翼
      for (const [a, b] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) {
        const n = 24, pts = [];
        for (let i = 0; i <= n; i++) { const t = 2 * Math.PI * i / n; pts.push(P(this.mv(s.R, [a * 0.45 + 0.2 * Math.cos(t), b * 0.45 + 0.2 * Math.sin(t), 0.08]))); }
        for (let i = 0; i < n; i++) api.line(...pts[i], ...pts[i + 1], api.css("--amber"), 1.5);
      }
    } else {                            // 屏幕面（+z 一侧）
      const sc = [[-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1]].map(([a, b]) => P(this.mv(s.R, [a * 0.19, b * 0.4, 0.031])));
      for (let i = 0; i < 4; i++) api.line(...sc[i], ...sc[i + 1], api.css("--blue"), 2);
    }
    for (let i = 0; i < 3; i++) { const e = [0, 0, 0]; e[i] = 0.75; const q = P(this.mv(s.R, e)); api.arrow(cx, cy, q[0], q[1], cols[i], 3); api.label(["x_b", "y_b", "z_b"][i], q[0] + 6, q[1] - 8, cols[i], 13); }
    api.label(api.T("虚线：真实的最终姿态", "dashed: the true final attitude"), 12, 18, api.css("--muted"), 12);
    if (s.method) api.label(s.method === "right" ? api.T("正在右乘积分", "integrating: right") : api.T("正在左乘积分", "integrating: left"), 12, 38, s.method === "right" ? api.css("--ok") : api.css("--red"), 13);
  },
});
