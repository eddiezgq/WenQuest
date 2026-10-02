// 实验 10.7 六个数确定一个刚体（配 10.7 节）。
// 场景 grip：UR5e 夹爪上贴三个标记点，在夹爪坐标系 {b} 中为 A (0, 0, 0)、B (0.10, 0, 0)、C (0.02, 0.06, 0) m（算例 10.7.1）。
//   夹爪位姿：位置 (x, y, z)，姿态 R = Rot(ẑ, ψ) Rot(ŷ, θ) Rot(x̂, φ)（ZYX 欧拉角，4.5 节）。界面显示三点的 9 个坐标、3 个距离，
//   并按式 (10.7.2) 由三点重建 R，再按式 (4.5.4) 求回三个角。斜投影：x 指向左下，y 向右，z 向上。
// 场景 book：桌面上的一本书（俯视），只有 x、y 和转角 ψ 三个数。
WQ.lab({
  title: ["实验 10.7 六个数确定一个刚体", "Lab 10.7 Six numbers fix a rigid body"],
  goal: ["用六个数摆放夹爪，读出三个标记点的九个坐标；验证三个距离始终不变，并由三个点重建出那六个数。",
         "Place the gripper with six numbers and read the nine coordinates of three markers; check that the three distances never change and rebuild the six numbers from the points."],
  scenes: [
    { id: "grip", robot: true, name: ["夹爪上的三个标记点", "Three markers on a gripper"],
      problem: { title: ["机器人问题：相机怎样从标记点算出夹爪的位姿", "Robot problem: how a camera gets the gripper pose from markers"],
                 text: ["动作捕捉系统测得三个标记点的坐标，共九个数。夹爪的位姿只要六个数，另外三个数去了哪里？",
                        "The motion-capture system measures three markers, nine numbers. The gripper pose needs only six; where did the other three go?"] } },
    { id: "book", name: ["桌上的一本书", "A book on a desk"], hide: ["z", "pitch", "roll"],
      problem: { title: ["生活中的例子：平放的书只有三个自由度", "Everyday example: a book lying flat has three degrees of freedom"],
                 text: ["书只能在桌面上平移和转动。确定它的位置需要几个数？",
                        "The book can only slide and turn on the desk. How many numbers fix its position?"] },
      params: { x: { min: 0.1, max: 0.9, value: 0.3 }, y: { min: 0.1, max: 0.5, value: 0.25 }, yaw: { min: -180, max: 180, value: 0 } } },
  ],
  params: [
    { id: "x", name: ["位置 x", "Position x"], min: -0.7, max: 0.1, step: 0.01, value: -0.4, unit: "m", digits: 2 },
    { id: "y", name: ["位置 y", "Position y"], min: -0.5, max: 0.3, step: 0.01, value: -0.2, unit: "m", digits: 2 },
    { id: "z", name: ["位置 z", "Position z"], min: 0.1, max: 0.6, step: 0.01, value: 0.3, unit: "m", digits: 2 },
    { id: "yaw", name: ["偏航角 ψ（绕 z）", "Yaw ψ (about z)"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "pitch", name: ["俯仰角 θ（绕 y）", "Pitch θ (about y)"], min: -80, max: 80, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "roll", name: ["横滚角 φ（绕 x）", "Roll φ (about x)"], min: -180, max: 180, step: 1, value: 180, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["A", "A"], color: "#d62728" }, { name: ["B", "B"], color: "#2ca02c" }, { name: ["C", "C"], color: "#7b3fa0" }],
  tasks: [
    { id: "ex", robot: true, text: ["设置算例 10.7.1 的位姿：(−0.45, −0.20, 0.30) m，ψ = 30°，θ = 0°，φ = 180°；读出三个标记点的坐标，与书中比较。",
                                    "Set the pose of Example 10.7.1: (−0.45, −0.20, 0.30) m, ψ = 30°, θ = 0°, φ = 180°; compare the marker coordinates with the book."],
      demo: { scene: "grip", set: { x: -0.45, y: -0.2, z: 0.3, yaw: 30, pitch: 0, roll: 180 }, press: [], wait: 1 } },
    { id: "rigid", robot: true, text: ["同时改变至少四个数：九个坐标都变了，三个距离始终不变，重建出的六个数与滑块一致。",
                                       "Change at least four numbers: all nine coordinates change, the three distances do not, and the rebuilt six numbers match the sliders."],
      demo: { scene: "grip", set: { x: -0.3, y: 0.1, z: 0.45, yaw: -60, pitch: 25, roll: 150 }, press: [], wait: 1 } },
    { id: "yaw", robot: true, text: ["只改变偏航角（其余为初始值）：A 的坐标和三点的 z 坐标都不变。", "Change only the yaw (others at their start values): A and the z coordinates of all three points stay put."],
      demo: { scene: "grip", set: { x: -0.4, y: -0.2, z: 0.3, yaw: 75, pitch: 0, roll: 180 }, press: [], wait: 1 } },
    { id: "book", text: ["把书转到 90°，读出确定它位置的三个数。", "Turn the book to 90° and read the three numbers that fix it."],
      demo: { scene: "book", set: { x: 0.4, y: 0.3, yaw: 90 }, press: [], wait: 1 } },
  ],
  think: ["若三个标记点贴得几乎在一条直线上，由它们重建的姿态会怎样？为什么实际系统常贴四到六个点？",
          "If the three markers are almost in a line, what happens to the rebuilt orientation? Why do real systems often use four to six markers?"],

  M: [[0, 0, 0], [0.10, 0, 0], [0.02, 0.06, 0]],
  BOOK: [[0, 0, 0], [0.21, 0, 0], [0, 0.15, 0]],
  rot(api) {
    const d = Math.PI / 180, p = api.scene === "book" ? 0 : api.p.pitch * d, r = api.scene === "book" ? 0 : api.p.roll * d, y = api.p.yaw * d;
    const cz = Math.cos(y), sz = Math.sin(y), cy = Math.cos(p), sy = Math.sin(p), cx = Math.cos(r), sx = Math.sin(r);
    return [[cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
            [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
            [-sy, cy * sx, cy * cx]];
  },
  pts(api) {
    const R = this.rot(api), o = [api.p.x, api.p.y, api.scene === "book" ? 0 : api.p.z], M = api.scene === "book" ? this.BOOK : this.M;
    return M.map((q) => [0, 1, 2].map((i) => o[i] + R[i][0] * q[0] + R[i][1] * q[1] + R[i][2] * q[2]));
  },
  rebuild(P) {                 // 式 (10.7.2)：格拉姆-施密特
    const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    const nrm = (a) => { const n = Math.sqrt(dot(a, a)); return [a[0] / n, a[1] / n, a[2] / n]; };
    const x = nrm(sub(P[1], P[0])), ac = sub(P[2], P[0]), k = dot(ac, x), y = nrm([ac[0] - k * x[0], ac[1] - k * x[1], ac[2] - k * x[2]]);
    const z = [x[1] * y[2] - x[2] * y[1], x[2] * y[0] - x[0] * y[2], x[0] * y[1] - x[1] * y[0]];
    const R = [[x[0], y[0], z[0]], [x[1], y[1], z[1]], [x[2], y[2], z[2]]], D = 180 / Math.PI;
    const th = Math.atan2(-R[2][0], Math.hypot(R[0][0], R[1][0])), ps = Math.atan2(R[1][0], R[0][0]), ph = Math.atan2(R[2][1], R[2][2]);
    return { p: P[0], ang: [ps * D, th * D, ph * D] };
  },
  reset(api, s) {},
  readouts(api, s) {
    const P = this.pts(api), dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
    const d = [dist(P[0], P[1]), dist(P[0], P[2]), dist(P[1], P[2])];
    const V = (a) => `(${api.fmt(a[0], 4)}, ${api.fmt(a[1], 4)}, ${api.fmt(a[2], 4)})`;
    const near = (a, b, e) => Math.abs(a - b) < (e || 1e-9);
    if (api.scene === "book") {
      if (near(api.p.yaw, 90)) api.done("book");
      return [[["三个数 (x, y, ψ)", "three numbers (x, y, ψ)"], `(${api.fmt(api.p.x, 2)} m, ${api.fmt(api.p.y, 2)} m, ${api.fmt(api.p.yaw, 0)}°)`],
              [["角 A", "corner A"], V(P[0]) + " m"], [["角 B", "corner B"], V(P[1]) + " m"], [["角 C", "corner C"], V(P[2]) + " m"],
              [["|AB|、|AC|", "|AB|, |AC|"], `${api.fmt(d[0], 3)}, ${api.fmt(d[1], 3)} m`]];
    }
    const rb = this.rebuild(P);
    const pv = { x: api.p.x, y: api.p.y, z: api.p.z, yaw: api.p.yaw, pitch: api.p.pitch, roll: api.p.roll };
    const def = { x: -0.4, y: -0.2, z: 0.3, yaw: 0, pitch: 0, roll: 180 };
    const changed = Object.keys(def).filter((k) => !near(pv[k], def[k])).length;
    const distOK = near(d[0], 0.1, 1e-12) && near(d[1], Math.hypot(0.02, 0.06), 1e-12) && near(d[2], Math.hypot(0.08, 0.06), 1e-12);
    const wrap = (a) => ((a + 540) % 360) - 180;
    const angOK = Math.abs(api.p.pitch) < 89 && near(wrap(rb.ang[0] - api.p.yaw), 0, 1e-6) && near(rb.ang[1], api.p.pitch, 1e-6) && near(wrap(rb.ang[2] - api.p.roll), 0, 1e-6);
    if (near(api.p.x, -0.45) && near(api.p.y, -0.2) && near(api.p.z, 0.3) && near(api.p.yaw, 30) && near(api.p.pitch, 0) && near(Math.abs(api.p.roll), 180)) api.done("ex");
    if (changed >= 4 && distOK && angOK) api.done("rigid");
    if (changed === 1 && !near(api.p.yaw, 0) && near(P[0][0], -0.4) && near(P[0][1], -0.2) && P.every((q) => near(q[2], 0.3, 1e-12))) api.done("yaw");
    return [[["A（9 个坐标之一组）", "A (one of the nine coordinates)"], V(P[0]) + " m"], [["B", "B"], V(P[1]) + " m"], [["C", "C"], V(P[2]) + " m"],
            [["|AB|、|AC|、|BC|", "|AB|, |AC|, |BC|"], `${api.fmt(d[0], 4)}, ${api.fmt(d[1], 4)}, ${api.fmt(d[2], 4)} m`],
            [["由三点重建的位置", "position rebuilt from the points"], V(rb.p) + " m"],
            [["由三点重建的 (ψ, θ, φ)", "(ψ, θ, φ) rebuilt from the points"], `(${api.fmt(rb.ang[0], 1)}°, ${api.fmt(rb.ang[1], 1)}°, ${api.fmt(rb.ang[2], 1)}°)`]];
  },
  draw(api, s) {
    const { w, h, ctx } = api, P = this.pts(api), cols = ["#d62728", "#2ca02c", "#7b3fa0"];
    if (api.scene === "book") {
      const k = Math.min(w / 1.1, h / 0.7), X = (q) => [w * 0.06 + k * q[0], h * 0.92 - k * q[1]];
      api.rect(w * 0.06, h * 0.92 - k * 0.6, k * 1.0, k * 0.6, "rgba(184,134,11,0.12)", api.css("--muted"), 4);
      api.frame(w * 0.06, h * 0.92, 0, 40, ["x", "y"], api.T("桌面", "desk"));
      const R = this.rot(api), o = [api.p.x, api.p.y];
      const corner = (u, v) => X([o[0] + R[0][0] * u + R[0][1] * v, o[1] + R[1][0] * u + R[1][1] * v]);
      const c4 = [corner(0, 0), corner(0.21, 0), corner(0.21, 0.15), corner(0, 0.15)];
      ctx.beginPath(); c4.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.closePath();
      ctx.fillStyle = "rgba(31,119,180,0.35)"; ctx.fill(); ctx.strokeStyle = "#1f77b4"; ctx.lineWidth = 2; ctx.stroke();
      P.forEach((q, i) => { const p = X(q); api.circle(p[0], p[1], 6, cols[i], api.css("--ink")); api.label("ABC"[i], p[0] + 9, p[1] - 9, cols[i], 13); });
      return;
    }
    const k = Math.min(w / 1.25, h / 0.95), O = [w * 0.62, h * 0.72];
    const X = (q) => [O[0] + k * (q[1] - 0.55 * q[0]), O[1] - k * (q[2] - 0.35 * q[0])];
    const o = X([0, 0, 0]);
    [[0.25, 0, 0], [0, 0.25, 0], [0, 0, 0.25]].forEach((e, i) => { const p = X(e); api.arrow(o[0], o[1], p[0], p[1], [api.css("--red"), api.css("--green"), api.css("--blue")][i], 2); });
    api.label("{s}", o[0] - 18, o[1] + 12, api.css("--muted"), 12);
    const R = this.rot(api), org = [api.p.x, api.p.y, api.p.z];
    const B = (u, v, ww) => X([0, 1, 2].map((i) => org[i] + R[i][0] * u + R[i][1] * v + R[i][2] * ww));
    const plate = [B(-0.02, -0.02, 0), B(0.12, -0.02, 0), B(0.12, 0.08, 0), B(-0.02, 0.08, 0)];
    ctx.beginPath(); plate.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.closePath();
    ctx.fillStyle = "rgba(120,140,160,0.35)"; ctx.fill(); ctx.strokeStyle = api.css("--muted"); ctx.lineWidth = 1.5; ctx.stroke();
    const top = B(0.05, 0.03, -0.12), base = B(0.05, 0.03, 0);
    api.line(base[0], base[1], top[0], top[1], api.css("--muted"), 6);
    const ob = B(0, 0, 0);
    [[0.08, 0, 0], [0, 0.08, 0], [0, 0, 0.08]].forEach((e, i) => { const p = B(...e); api.arrow(ob[0], ob[1], p[0], p[1], [api.css("--red"), api.css("--green"), api.css("--blue")][i], 1.5); });
    for (let i = 0; i < 3; i++) for (let j = i + 1; j < 3; j++) { const a = X(P[i]), b = X(P[j]); api.line(a[0], a[1], b[0], b[1], api.css("--ink"), 1, [3, 3]); }
    P.forEach((q, i) => { const p = X(q); api.circle(p[0], p[1], 6, cols[i], api.css("--ink")); api.label("ABC"[i], p[0] + 9, p[1] - 10, cols[i], 13); });
  },
});
