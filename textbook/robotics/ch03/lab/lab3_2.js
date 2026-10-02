// 实验 3.2 点积、叉积与力矩（配 3.2 节）。平面内：r 从转动中心 O 指向力的作用点（长度 L、方向角 α），力 F（大小 f、方向角 β）。
// r·F = L f cos(β − α)；r×F 只有垂直于屏幕的分量 m_z = L f sin(β − α)（式 (3.2.9) 的第三个分量），正值指向屏幕外。
WQ.lab({
  title: ["实验 3.2 点积、叉积与力矩", "Lab 3.2 Dot product, cross product and moment"],
  goal: ["改变 r 和 F 的长度与方向，看点积、叉积和平行四边形面积怎样变化，体会力矩 m = r × F 的大小与方向。",
         "Change the lengths and directions of r and F; watch the dot product, the cross product and the parallelogram area, and get a feel for the moment m = r × F."],
  scenes: [
    { id: "sensor", robot: true, name: ["力传感器与零件", "F/T sensor and part"],
      problem: { title: ["机器人问题：力传感器读到的力矩", "Robot problem: the moment read by the F/T sensor"],
                 text: ["夹爪夹着一根长零件，有人在零件端部推了一下。腕部力传感器中心 O 受到的力矩是多少、绕哪个方向？（俯视图）",
                        "The gripper holds a long part and someone pushes its end. What moment acts at the sensor centre O, and about which direction? (top view)"] } },
    { id: "wrench", name: ["扳手拧螺栓", "Wrench on a bolt"],
      problem: { title: ["生活中的例子：怎样拧最省力", "Everyday example: the easiest way to turn a bolt"],
                 text: ["手离螺栓越远、用力方向越接近垂直于扳手柄，拧动螺栓的力矩越大。顺着扳手柄推拉则拧不动。",
                        "The farther the hand from the bolt and the closer the push is to perpendicular, the larger the moment. Pushing along the handle turns nothing."] },
      params: { L: { value: 0.25 }, alpha: { value: 0 }, f: { value: 50 }, beta: { value: 60 } } },
  ],
  params: [
    { id: "L", name: ["r 的长度", "Length of r"], min: 0.05, max: 0.5, step: 0.01, value: 0.3, unit: "m", digits: 2 },
    { id: "alpha", name: ["r 的方向角 α", "Direction of r, α"], min: -180, max: 180, step: 1, value: 20, unit: "°", digits: 0 },
    { id: "f", name: ["力的大小 |F|", "Force |F|"], min: 0, max: 100, step: 1, value: 40, unit: "N", digits: 0 },
    { id: "beta", name: ["力的方向角 β", "Direction of F, β"], min: -180, max: 180, step: 1, value: 80, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "zero", robot: true, text: ["力不为零，却使力矩为零：力的方向应当怎样？", "Make the moment zero with a non-zero force: how must the force point?"],
      demo: { scene: "sensor", set: { L: 0.3, alpha: 20, f: 40, beta: 200 - 360 }, press: [] } },
    { id: "max", robot: true, text: ["保持 |F| = 40 N、|r| = 0.3 m，使力矩最大，读出最大值。", "Keep |F| = 40 N and |r| = 0.3 m; make the moment largest and read it."],
      demo: { scene: "sensor", set: { L: 0.3, alpha: 20, f: 40, beta: 110 }, press: [] } },
    { id: "half", robot: true, text: ["使力矩指向屏幕里（⊗），且大小为同样 |r|、|F| 下最大值的一半。", "Make the moment point into the screen (⊗) with half the largest magnitude for the same |r| and |F|."],
      demo: { scene: "sensor", set: { L: 0.3, alpha: 20, f: 40, beta: -10 }, press: [] } },
    { id: "bolt", text: ["扳手：只用 50 N 的力，拧出至少 20 N·m 的力矩。", "Wrench: produce at least 20 N·m with a 50 N force."],
      demo: { scene: "wrench", set: { L: 0.4, alpha: 0, f: 50, beta: 90 }, press: [] } },
  ],
  think: ["力矩为零时，点积 r·F 有什么特点？力矩最大时呢？两者能否同时为零？", "When the moment is zero, what is special about r·F? And when the moment is largest? Can both be zero?"],

  vals(api) {
    const d = Math.PI / 180, a = api.p.alpha * d, b = api.p.beta * d, L = api.p.L, f = api.p.f;
    const r = [L * Math.cos(a), L * Math.sin(a)], F = [f * Math.cos(b), f * Math.sin(b)];
    return { r, F, dot: r[0] * F[0] + r[1] * F[1], mz: r[0] * F[1] - r[1] * F[0], L, f };
  },
  reset(api, s) {},
  readouts(api, s) {
    const v = this.vals(api), mmax = v.L * v.f;
    if (api.scene === "sensor" && v.f > 0 && Math.abs(v.mz) < 1e-6) api.done("zero");
    if (api.scene === "sensor" && Math.abs(v.L - 0.3) < 1e-9 && v.f === 40 && Math.abs(Math.abs(v.mz) - mmax) < 1e-6) api.done("max");
    if (api.scene === "sensor" && v.f > 0 && v.mz < 0 && Math.abs(-v.mz - 0.5 * mmax) < 1e-6) api.done("half");
    if (api.scene === "wrench" && v.f === 50 && Math.abs(v.mz) >= 20 - 1e-9) api.done("bolt");
    const dir = Math.abs(v.mz) < 1e-9 ? api.T("无", "none") : v.mz > 0 ? api.T("⊙ 指向屏幕外", "⊙ out of the screen") : api.T("⊗ 指向屏幕里", "⊗ into the screen");
    return [
      [["r 的分量", "r components"], `(${api.fmt(v.r[0], 3)}, ${api.fmt(v.r[1], 3)}, 0) m`],
      [["F 的分量", "F components"], `(${api.fmt(v.F[0], 2)}, ${api.fmt(v.F[1], 2)}, 0) N`],
      [["点积 r·F", "dot product r·F"], api.fmt(v.dot, 3) + " N·m"],
      [["叉积 m = r×F", "cross product m = r×F"], `(0, 0, ${api.fmt(v.mz, 3)}) N·m`],
      [["力矩方向", "moment direction"], dir],
      [["|r||F|（最大可能值）", "|r||F| (largest possible)"], api.fmt(v.L * v.f, 3) + " N·m"],
    ];
  },
  draw(api, s) {
    const { w, h } = api, v = this.vals(api), wr = api.scene === "wrench";
    const cx = w * 0.4, cy = h * 0.55, k = Math.min(w, h) * 1.15, kf = k * 0.004;   // 1 N 画成 kf 像素
    const X = (x, y) => [cx + k * x, cy - k * y];
    const ink = api.css("--ink"), c = api.ctx;
    const tip = X(...v.r);
    // 物体：长零件 / 扳手
    c.save(); c.translate(cx, cy); c.rotate(-Math.atan2(v.r[1], v.r[0]));
    const len = k * v.L;
    if (wr) {
      api.rect(-18, -12, len + 30, 24, api.css("--muted"), null, 10);
      c.beginPath(); for (let i = 0; i < 6; i++) { const t = i * Math.PI / 3; c.lineTo(16 * Math.cos(t), 16 * Math.sin(t)); } c.closePath();
      c.fillStyle = api.css("--panel"); c.fill(); c.strokeStyle = ink; c.stroke();
    } else {
      api.rect(-10, -9, len + 30, 18, "rgba(210,153,34,0.35)", api.css("--amber"), 4);
    }
    c.restore();
    api.circle(cx, cy, 6, api.css("--panel"), ink);
    api.label("O", cx - 18, cy + 14, ink, 14);
    // 平行四边形（F 按比例缩放后与 r 张成）
    const Fs = [v.F[0] * kf, v.F[1] * kf];
    const p1 = [cx, cy], p2 = tip, p3 = [tip[0] + Fs[0], tip[1] - Fs[1]], p4 = [cx + Fs[0], cy - Fs[1]];
    c.beginPath(); [p1, p2, p3, p4].forEach((p, i) => (i ? c.lineTo(...p) : c.moveTo(...p))); c.closePath();
    c.fillStyle = "rgba(219,171,9,0.18)"; c.fill();
    c.setLineDash([5, 4]); c.strokeStyle = api.css("--amber"); c.lineWidth = 1; c.stroke(); c.setLineDash([]);
    api.arrow(cx, cy, ...tip, api.css("--blue"), 3.5);
    api.label("r", (cx + tip[0]) / 2 - 4, (cy + tip[1]) / 2 - 14, api.css("--blue"), 16);
    if (v.f > 0) { api.arrow(...tip, ...p3, api.css("--red"), 3.5); api.label("F", p3[0] + 8, p3[1] - 8, api.css("--red"), 16); }
    // 力矩符号：⊙ 或 ⊗，大小随 |m|
    const R = 8 + 26 * Math.min(1, Math.abs(v.mz) / 20), mx = w * 0.82, my = h * 0.25;
    if (Math.abs(v.mz) > 1e-9) {
      api.circle(mx, my, R, null, api.css("--green"));
      if (v.mz > 0) api.circle(mx, my, 4, api.css("--green"));
      else { api.line(mx - R * 0.6, my - R * 0.6, mx + R * 0.6, my + R * 0.6, api.css("--green"), 2); api.line(mx - R * 0.6, my + R * 0.6, mx + R * 0.6, my - R * 0.6, api.css("--green"), 2); }
    }
    api.label(api.T("力矩 m = r×F", "moment m = r×F"), mx, my + 46, api.css("--green"), 13, "center");
    api.label(api.T("虚线平行四边形面积 ∝ |m|", "dashed parallelogram area ∝ |m|"), 12, h - 16, api.css("--muted"), 12);
  },
});
