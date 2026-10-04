// 实验 2.5 叉积与力矩（配 2.5 节）。平面内的 r 和 F，叉积只有垂直于画面的分量：为正画 ⊙（朝外），为负画 ⊗（朝里），
// 符号的大小随 |r × F| 变化；平行四边形的面积就是 |r × F|。UR5e 场景是侧视图：肩关节、大臂 0.425 m、小臂 0.392 m，
// 末端挂 5 kg 负载，肩关节承受的重力力矩等于 mg 乘以负载到肩关节的水平距离（不计手臂自重）。
// “两种符号都见过”记在闭包里，重置时不丢。
const rad25 = (d) => d * Math.PI / 180, G25 = 9.81;
const seen25 = { pos: false, neg: false };
const L2_25 = 0.425, L3_25 = 0.392, M25 = 5;
function cross25(p) {
  const r = [p.rr * Math.cos(rad25(p.ar)), p.rr * Math.sin(rad25(p.ar))], F = [p.Fm * Math.cos(rad25(p.aF)), p.Fm * Math.sin(rad25(p.aF))];
  return { r, F, Mz: r[0] * F[1] - r[1] * F[0] };
}
function arm25(p) {
  const e = [L2_25 * Math.cos(rad25(p.q2)), L2_25 * Math.sin(rad25(p.q2))];
  const t = [e[0] + L3_25 * Math.cos(rad25(p.q2 + p.q3)), e[1] + L3_25 * Math.sin(rad25(p.q2 + p.q3))];
  return { e, t, M: M25 * G25 * Math.abs(t[0]) };
}
const MMAX25 = M25 * G25 * (L2_25 + L3_25);
function wrench25(p) { return { M: 40 * p.d * Math.sin(rad25(p.aw)) }; }

WQ.lab({
  title: ["实验 2.5 叉积与力矩", "Lab 2.5 The cross product and torque"],
  goal: ["看 r × F 的大小（平行四边形的面积）和方向（右手定则）怎样随 r、F 的大小和夹角变化；用力臂求机械臂关节承受的力矩。",
         "See how the size (parallelogram area) and direction (right-hand rule) of r × F change with the sizes and angle of r and F; use the lever arm to find the torque on a robot joint."],
  scenes: [
    { id: "rf", name: ["r × F", "r × F"], hide: ["q2", "q3", "d", "aw"],
      problem: { title: ["叉积：有方向的面积", "The cross product: an area with a direction"],
                 text: ["r 和 F 都在画面内，r × F 垂直于画面：⊙ 表示指向你，⊗ 表示背离你。", "r and F lie in the screen; r × F is perpendicular to it: ⊙ points at you, ⊗ points away."] } },
    { id: "arm", robot: true, name: ["UR5e 肩关节的负载力矩", "Load torque on the UR5e shoulder"], hide: ["rr", "Fm", "ar", "aF", "d", "aw"],
      problem: { title: ["机器人问题：什么姿态肩关节最吃力", "Robot problem: which pose loads the shoulder most"],
                 text: ["侧视图。大臂 0.425 m，小臂 0.392 m，末端挂 5 kg。调肩关节和肘关节，看负载重力对肩关节的力矩。",
                        "Side view. Upper arm 0.425 m, forearm 0.392 m, 5 kg at the end. Move the shoulder and elbow and watch the load's torque about the shoulder."] } },
    { id: "wrench", name: ["扳手", "A wrench"], hide: ["rr", "Fm", "ar", "aF", "q2", "q3"],
      problem: { title: ["生活中的例子：手握在哪里", "Everyday example: where to hold the wrench"],
                 text: ["扳手长 0.35 m，手只能用 40 N 的力。调手的位置和用力的方向。", "The wrench is 0.35 m long and the hand can push with only 40 N. Set the grip position and the direction of the push."] } },
  ],
  params: [
    { id: "rr", name: ["|r|", "|r|"], min: 0.05, max: 0.5, step: 0.01, value: 0.3, unit: "m", digits: 2 },
    { id: "Fm", name: ["|F|", "|F|"], min: 5, max: 100, step: 1, value: 50, unit: "N", digits: 0 },
    { id: "ar", name: ["r 的方向", "Direction of r"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "aF", name: ["F 的方向", "Direction of F"], min: -180, max: 180, step: 1, value: 45, unit: "°", digits: 0 },
    { id: "q2", name: ["肩关节：大臂与水平的夹角", "Shoulder: upper arm from horizontal"], min: -90, max: 90, step: 1, value: 60, unit: "°", digits: 0 },
    { id: "q3", name: ["肘关节：小臂相对大臂", "Elbow: forearm relative to upper arm"], min: -160, max: 160, step: 1, value: -90, unit: "°", digits: 0 },
    { id: "d", name: ["手到螺栓的距离", "Grip distance from the bolt"], min: 0.05, max: 0.35, step: 0.01, value: 0.15, unit: "m", digits: 2 },
    { id: "aw", name: ["力与扳手的夹角", "Angle between push and wrench"], min: 0, max: 180, step: 1, value: 45, unit: "°", digits: 0 },
  ],
  tasks: [
    { id: "max", text: ["r × F 场景：保持 |r|、|F| 不变，找到使力矩最大的力的方向（|r × F| 达到 rF 的 99.9%）。", "r × F: keeping |r| and |F|, find the force direction that maximises the torque (|r × F| at 99.9% of rF)."],
      demo: { scene: "rf", set: { ar: 0, aF: 90 }, press: [], wait: 1 } },
    { id: "flip", text: ["让 r × F 反向：⊙ 和 ⊗ 都要出现过。", "Reverse r × F: get both ⊙ and ⊗."],
      demo: { scene: "rf", set: { ar: 0, aF: -90 }, press: [], wait: 1 } },
    { id: "armmax", robot: true, text: ["找到负载力矩最大的手臂姿态（达到最大值的 99%），读出最大力矩。", "Find the arm pose with the largest load torque (within 99% of the maximum) and read it."],
      demo: { scene: "arm", set: { q2: 0, q3: 0 }, press: [], wait: 1 } },
    { id: "bolt", text: ["扳手：用 40 N 拧出至少 12 N·m 的力矩。", "Wrench: get at least 12 N·m with 40 N."],
      demo: { scene: "wrench", set: { d: 0.33, aw: 90 }, press: [], wait: 1 } },
  ],
  think: ["r 和 F 夹角为 30° 和 150° 时，|r × F| 一样大吗？方向呢？机械臂托着负载时，负载举得越高，肩关节越吃力吗？",
          "Is |r × F| the same at 30° and at 150°? And the direction? Does lifting the load higher load the shoulder more?"],

  reset(api, s) {},
  change(api, s, pid) { check25(api); },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "rf") { const C = cross25(api.p), th = ((api.p.aF - api.p.ar) % 360 + 540) % 360 - 180;
      return [[["r", "r"], `(${f(C.r[0], 3)}, ${f(C.r[1], 3)}) m`], [["F", "F"], `(${f(C.F[0], 2)}, ${f(C.F[1], 2)}) N`],
              [["从 r 到 F 转过", "From r to F"], f(th, 0) + "°"], [["(r × F)_z = r_xF_y − r_yF_x", "(r × F)_z = r_xF_y − r_yF_x"], f(C.Mz, 2) + " N·m"],
              [["rF", "rF"], f(api.p.rr * api.p.Fm, 2) + " N·m"]]; }
    if (api.scene === "arm") { const A = arm25(api.p);
      return [[["负载到肩关节的水平距离", "Horizontal distance to the shoulder"], f(Math.abs(A.t[0]), 3) + " m"], [["负载的高度", "Height of the load"], f(A.t[1], 3) + " m"],
              [["肩关节的负载力矩", "Load torque on the shoulder"], f(A.M, 1) + " N·m"]]; }
    const W = wrench25(api.p); return [[["力臂 d sin θ", "Lever arm d sin θ"], f(api.p.d * Math.sin(rad25(api.p.aw)), 3) + " m"], [["力矩", "Torque"], f(W.M, 1) + " N·m"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), blue = css("--blue"), green = css("--green"), red = css("--red");
    const zsym = (x, y, Mz, scale) => {                  // ⊙ / ⊗，大小随 |Mz|
      const R = Math.max(6, Math.min(40, Math.abs(Mz) * scale));
      api.circle(x, y, R, null, red);
      if (Mz > 0) api.circle(x, y, Math.max(3, R * 0.2), red);
      else if (Mz < 0) { api.line(x - R * 0.7, y - R * 0.7, x + R * 0.7, y + R * 0.7, red, 2); api.line(x - R * 0.7, y + R * 0.7, x + R * 0.7, y - R * 0.7, red, 2); }
    };
    if (api.scene === "rf") {
      const C = cross25(api.p), ox = w * 0.4, oy = h * 0.55, Sr = h * 0.7, SF = h * 0.0035;
      const R = [ox + Sr * C.r[0], oy - Sr * C.r[1]], F = [ox + SF * C.F[0], oy - SF * C.F[1]];
      api.ctx.fillStyle = C.Mz >= 0 ? "rgba(201,143,0,0.22)" : "rgba(192,57,43,0.18)";
      api.ctx.beginPath(); api.ctx.moveTo(ox, oy); api.ctx.lineTo(R[0], R[1]); api.ctx.lineTo(R[0] + F[0] - ox, R[1] + F[1] - oy); api.ctx.lineTo(F[0], F[1]); api.ctx.closePath(); api.ctx.fill();
      api.arrow(ox, oy, R[0], R[1], blue, 3); api.arrow(ox, oy, F[0], F[1], green, 3);
      api.label("r", R[0] + 8, R[1], blue, 15); api.label("F", F[0] + 8, F[1], green, 15);
      zsym(w * 0.85, h * 0.25, C.Mz, 1.5);
      api.label("r × F", w * 0.85, h * 0.25 + 52, red, 13, "center");
      api.label(C.Mz > 0 ? api.T("⊙ 指向你（逆时针）", "⊙ towards you (counter-clockwise)") : C.Mz < 0 ? api.T("⊗ 背离你（顺时针）", "⊗ away from you (clockwise)") : "0",
                w * 0.85, h * 0.25 + 72, red, 12, "center");
      api.label(api.T("阴影：平行四边形，面积 = |r × F|（画面中 r、F 的比例尺不同）", "shaded: the parallelogram, area = |r × F| (r and F drawn to different scales)"), 12, h - 12, mut, 11);
      return;
    }
    if (api.scene === "arm") {
      const A = arm25(api.p), S = h * 0.75, ox = w * 0.35, oy = h * 0.55, X = (u) => [ox + S * u[0], oy - S * u[1]];
      api.rect(ox - 18, oy, 36, h * 0.4, mut);
      api.arm(ox, oy, [api.p.q2, api.p.q3], [S * L2_25, S * L3_25], css("--soft"), 14);
      const T = X(A.t); api.line(T[0], T[1], T[0], T[1] + 26, ink, 1.5); api.rect(T[0] - 14, T[1] + 26, 28, 22, css("--amber"), ink, 3);
      api.label("5 kg", T[0], T[1] + 37, ink, 11, "center");
      api.arrow(T[0], T[1] + 52, T[0], T[1] + 100, green, 3); api.label("mg", T[0] + 8, T[1] + 84, green, 13);
      api.line(ox, oy + 12, T[0], oy + 12, red, 3); api.line(T[0], oy + 4, T[0], oy + 20, red, 1);
      api.label(api.T("力臂", "lever arm"), (ox + T[0]) / 2, oy + 28, red, 12, "center");
      zsym(ox, oy, -Math.sign(A.t[0]) * A.M, 0.6);
      api.label(api.T(`最大可能：${api.fmt(MMAX25, 1)} N·m（手臂水平伸直）`, `largest possible: ${api.fmt(MMAX25, 1)} N·m (arm straight out)`), 12, h - 12, mut, 11);
      return;
    }
    const W = wrench25(api.p), bx = w * 0.2, by = h * 0.55, S = w * 1.6;
    api.circle(bx, by, 16, mut, ink); api.rect(bx, by - 8, S * 0.35, 16, css("--soft"), ink, 6);
    const hx = bx + S * api.p.d; api.circle(hx, by, 9, css("--amber"), ink);
    const Fx = 2.2 * 40 * Math.cos(rad25(api.p.aw)), Fy = 2.2 * 40 * Math.sin(rad25(api.p.aw));
    api.arrow(hx, by, hx + Fx, by - Fy, green, 3); api.label("40 N", hx + Fx + 6, by - Fy, green, 12);
    zsym(bx, by, W.M, 1.6);
    api.label(api.fmt(W.M, 1) + " N·m", bx, by + 56, red, 14, "center");
  },
});

function check25(api) {
  if (api.scene === "rf") {
    const C = cross25(api.p);
    if (Math.abs(C.Mz) >= 0.999 * api.p.rr * api.p.Fm) api.done("max");
    if (C.Mz > 1e-9) seen25.pos = true; if (C.Mz < -1e-9) seen25.neg = true;
    if (seen25.pos && seen25.neg) api.done("flip");
  }
  if (api.scene === "arm" && arm25(api.p).M >= 0.99 * MMAX25) api.done("armmax");
  if (api.scene === "wrench" && wrench25(api.p).M >= 12) api.done("bolt");
}
