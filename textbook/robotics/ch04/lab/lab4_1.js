// 实验 4.1 转动零件与转动坐标系（配 4.1 节）。零件 0.4 m × 0.2 m，吸盘中心在 O；托盘边倾斜 30°。
WQ.lab({
  title: ["实验 4.1 转动零件与转动坐标系", "Lab 4.1 Rotating the part vs rotating the frame"],
  goal: ["拖动转角，看零件四个角点的坐标和旋转矩阵怎样变化；比较“零件转”和“坐标系转”。",
         "Drag the angle: watch the corner coordinates and the rotation matrix; compare turning the part with turning the frame."],
  scenes: [
    { id: "part", robot: true, name: ["零件转动（主动）", "Part turns (active)"],
      problem: { title: ["机器人问题：把零件放进倾斜的托盘", "Robot problem: put the part into a tilted tray"],
                 text: ["手腕带着零件绕吸盘中心转动，托盘的边倾斜 30°。零件长边要与托盘边平行才能放进去。",
                        "The wrist turns the part about the suction cup; the tray edge is tilted 30°. The long edge must be parallel to it."] } },
    { id: "frame", name: ["坐标系转动（被动）", "Frame turns (passive)"],
      problem: { title: ["生活中的例子：装歪的相机", "Everyday example: a camera mounted askew"],
                 text: ["零件不动，相机坐标系 {b} 相对 {a} 转过 θ。同一个角点，在 {b} 中读出的分量是多少？",
                        "The part stays; the camera frame {b} is turned by θ from {a}. What are the corner's components in {b}?"] } },
  ],
  params: [{ id: "th", name: ["转角 θ", "Angle θ"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 }],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "tray", robot: true, text: ["把零件长边转到与托盘边平行（30°）。", "Turn the long edge parallel to the tray edge (30°)."],
      demo: { scene: "part", set: { th: 30 }, press: [] } },
    { id: "col", robot: true, text: ["让旋转矩阵的第一列等于 (0, 1)：此时 x 轴转到了哪里？", "Make column 1 of R equal (0, 1): where has the x axis gone?"],
      demo: { scene: "part", set: { th: 90 }, press: [] } },
    { id: "passive", text: ["切换到“坐标系转动”，转 30°，读出 P 在 {b} 中的分量。", "Switch to 'frame turns', set 30°, read P in {b}."],
      demo: { scene: "frame", set: { th: 30 }, press: [] } },
  ],
  think: ["“零件转 θ”与“坐标系转 θ”读出的分量为什么互为转置的关系？", "Why are the two readings related by a transpose?"],

  reset(api, s) {},
  readouts(api, s) {
    const t = api.p.th * Math.PI / 180, c = Math.cos(t), sn = Math.sin(t);
    const P = [0.2, 0.1];
    const act = [c * P[0] - sn * P[1], sn * P[0] + c * P[1]];
    const pas = [c * P[0] + sn * P[1], -sn * P[0] + c * P[1]];
    if (api.scene === "part" && Math.abs(api.p.th - 30) < 0.5) api.done("tray");
    if (api.scene === "part" && Math.abs(c) < 1e-3 && sn > 0.999) api.done("col");
    if (api.scene === "frame" && Math.abs(api.p.th - 30) < 0.5) api.done("passive");
    const R = `[${api.fmt(c, 3)}, ${api.fmt(-sn, 3)}; ${api.fmt(sn, 3)}, ${api.fmt(c, 3)}]`;
    const p = api.scene === "part" ? act : pas;
    return [[["旋转矩阵 R(θ)", "R(θ)"], R],
            [api.scene === "part" ? ["P′ 在 {a} 中", "P′ in {a}"] : ["P 在 {b} 中", "P in {b}"], `(${api.fmt(p[0], 5)}, ${api.fmt(p[1], 5)}) m`],
            [["P 到 O 的距离", "|OP|"], api.fmt(Math.hypot(p[0], p[1]), 5) + " m"]];
  },
  draw(api, s) {
    const { w, h } = api, cx = w * 0.45, cy = h * 0.55, k = Math.min(w, h) * 1.25;
    const t = api.p.th * Math.PI / 180;
    const X = (x, y) => [cx + k * x, cy - k * y];
    const rot = (x, y, a) => [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)];
    // tray (tilted 30°)
    const tr = [[-0.24, -0.12], [0.24, -0.12], [0.24, 0.12], [-0.24, 0.12]].map(([x, y]) => X(...rot(x, y, Math.PI / 6)));
    if (api.scene === "part") { api.ctx.setLineDash([6, 5]); tr.forEach((p, i) => api.line(...p, ...tr[(i + 1) % 4], api.css("--amber"), 2)); api.ctx.setLineDash([]); }
    // fixed frame {a}
    const fa = api.scene === "part" ? 0 : 0;
    api.frame(cx, cy, fa, k * 0.32, ["x", "y"], "{a}");
    // the part
    const a = api.scene === "part" ? t : 0;
    const pts = [[-0.2, -0.1], [0.2, -0.1], [0.2, 0.1], [-0.2, 0.1]].map(([x, y]) => X(...rot(x, y, a)));
    const c = api.ctx; c.beginPath(); pts.forEach((p, i) => (i ? c.lineTo(...p) : c.moveTo(...p))); c.closePath();
    c.fillStyle = "rgba(88,140,220,0.25)"; c.fill(); c.strokeStyle = api.css("--accent"); c.lineWidth = 2; c.stroke();
    const P = X(...rot(0.2, 0.1, a));
    api.circle(P[0], P[1], 6, api.css("--amber"), api.css("--ink"));
    api.label(api.scene === "part" && api.p.th ? "P′" : "P", P[0] + 10, P[1] - 10, api.css("--ink"), 14);
    if (api.scene === "frame") api.frame(cx, cy, api.p.th, k * 0.25, ["x′", "y′"], "{b}", api.css("--muted"));
  },
});
