// 实验 3.3 方向余弦矩阵与分量变换（配 3.3 节）。{b} 相对 {a}：先绕 z_a 转 ψ，再绕自身 x 轴转 φ，R_ab = Rot(z, ψ) Rot(x, φ)。
// 箭头在 {a} 中固定：相机场景为算例 3.3.2 的 d_a，手机场景为静止时加速度计感受到的 (0, 0, 9.81) m/s²。
// 读数：R_ab（各列 = {b} 的轴在 {a} 中的分量），p_a，p_b = R_abᵀ p_a（式 (3.3.4)），det R_ab，RᵀR 与 I 的最大偏差。
WQ.lab({
  title: ["实验 3.3 方向余弦矩阵与分量变换", "Lab 3.3 Direction cosine matrix and change of components"],
  goal: ["转动坐标系 {b}，看方向余弦矩阵的九个数怎样变化，并用它把同一支箭头的分量从 {a} 换到 {b}。",
         "Turn frame {b}, watch the nine direction cosines change, and use them to carry one arrow's components from {a} to {b}."],
  scenes: [
    { id: "cam", robot: true, name: ["俯视传送带的相机", "Camera above the conveyor"],
      problem: { title: ["机器人问题：相机装歪了以后", "Robot problem: a tilted camera"],
                 text: ["相机经支架安装，先绕竖直轴转 ψ，再绕自身 x 轴翻转 φ。从相机到零件的位移在机座坐标系中已知，相机读到的分量是多少？",
                        "The camera is mounted on a bracket: turned by ψ about the vertical, then tipped by φ about its own x axis. The displacement from camera to part is known in the base frame; what does the camera read?"] } },
    { id: "phone", name: ["手机的加速度传感器", "A phone's accelerometer"],
      problem: { title: ["生活中的例子：手机怎样知道自己竖着还是平放", "Everyday example: how a phone knows it is upright"],
                 text: ["静止时加速度计感受到一支竖直向上、大小 9.81 m/s² 的箭头。手机转动时箭头不变，它在手机坐标系中的分量在变。",
                        "At rest the accelerometer senses an arrow pointing up, 9.81 m/s² long. When the phone turns, the arrow stays; its components in the phone frame change."] },
      params: { psi: { value: 0 }, phi: { value: 0 } } },
  ],
  params: [
    { id: "psi", name: ["绕竖直轴 z_a 转 ψ", "Turn ψ about z_a"], min: -180, max: 180, step: 1, value: -90, unit: "°", digits: 0 },
    { id: "phi", name: ["再绕自身 x 轴转 φ", "then φ about its own x"], min: -180, max: 180, step: 1, value: 120, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "cam", robot: true, text: ["复现算例 3.3.2 的相机（ψ = −90°，φ = 160°），读出 d_b，与 (0.12, −0.05, 0.60) m 比较。", "Rebuild the camera of Example 3.3.2 (ψ = −90°, φ = 160°); read d_b and compare with (0.12, −0.05, 0.60) m."],
      demo: { scene: "cam", set: { psi: -90, phi: 160 }, press: [] } },
    { id: "down", robot: true, text: ["使相机光轴 z_b 竖直向下：R_ab 的第三列应是什么？", "Point the optical axis z_b straight down: what must column 3 of R_ab be?"],
      demo: { scene: "cam", set: { psi: 30, phi: 180 }, press: [] } },
    { id: "col", robot: true, text: ["使 R_ab 的第一列为 (0, 1, 0)ᵀ：此时 x_b 指向哪里？", "Make column 1 of R_ab equal (0, 1, 0)ᵀ: where does x_b point?"],
      demo: { scene: "cam", set: { psi: 90, phi: 45 }, press: [] } },
    { id: "phone", text: ["把手机竖起来，使加速度读数完全落在屏幕平面内（垂直于屏幕的分量为 0）。", "Stand the phone up so that the reading lies entirely in the screen plane (zero component normal to the screen)."],
      demo: { scene: "phone", set: { psi: 0, phi: 90 }, press: [] } },
  ],
  think: ["为什么无论怎样转动，R_ab 的行列式总是 1、RᵀR 总是 I？如果某次读数的行列式变成了 −1，说明什么？",
          "Why is det R_ab always 1 and RᵀR always I, however you turn? What would a determinant of −1 tell you?"],

  R(api) {
    const d = Math.PI / 180, a = api.p.psi * d, b = api.p.phi * d, ca = Math.cos(a), sa = Math.sin(a), cb = Math.cos(b), sb = Math.sin(b);
    return [[ca, -sa * cb, sa * sb], [sa, ca * cb, -ca * sb], [0, sb, cb]];        // Rot(z, ψ) Rot(x, φ)
  },
  arrowA(api) { return api.scene === "phone" ? [0, 0, 9.81] : [-0.158227, -0.12, -0.580917]; },
  mulT(R, v) { return [0, 1, 2].map((j) => R[0][j] * v[0] + R[1][j] * v[1] + R[2][j] * v[2]); },
  reset(api, s) {},
  readouts(api, s) {
    const R = this.R(api), pa = this.arrowA(api), pb = this.mulT(R, pa), ph = api.scene === "phone";
    const det = R[0][0] * (R[1][1] * R[2][2] - R[1][2] * R[2][1]) - R[0][1] * (R[1][0] * R[2][2] - R[1][2] * R[2][0]) + R[0][2] * (R[1][0] * R[2][1] - R[1][1] * R[2][0]);
    let dev = 0;
    for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
      const v = R[0][i] * R[0][j] + R[1][i] * R[1][j] + R[2][i] * R[2][j] - (i === j ? 1 : 0); dev = Math.max(dev, Math.abs(v));
    }
    if (!ph && api.p.psi === -90 && api.p.phi === 160) api.done("cam");
    if (!ph && Math.abs(R[2][2] + 1) < 1e-9) api.done("down");
    if (!ph && Math.abs(R[0][0]) < 1e-9 && Math.abs(R[1][0] - 1) < 1e-9) api.done("col");
    if (ph && Math.abs(pb[2]) < 1e-6) api.done("phone");
    const row = (i) => `[${api.fmt(R[i][0], 3)}, ${api.fmt(R[i][1], 3)}, ${api.fmt(R[i][2], 3)}]`;
    const u = ph ? " m/s²" : " m", dg = ph ? 2 : 4;
    const vec = (v) => `(${api.fmt(v[0], dg)}, ${api.fmt(v[1], dg)}, ${api.fmt(v[2], dg)})${u}`;
    return [
      [["R_ab 第 1 行", "R_ab row 1"], row(0)], [["R_ab 第 2 行", "R_ab row 2"], row(1)], [["R_ab 第 3 行", "R_ab row 3"], row(2)],
      [ph ? ["加速度读数在 {a}（地面）中", "reading in {a} (ground)"] : ["d 在 {a}（机座）中", "d in {a} (base)"], vec(pa)],
      [ph ? ["加速度读数在 {b}（手机）中", "reading in {b} (phone)"] : ["d 在 {b}（相机）中", "d in {b} (camera)"], vec(pb)],
      [["det R_ab", "det R_ab"], api.fmt(det, 6)],
      [["RᵀR 与 I 的最大偏差", "largest entry of RᵀR − I"], dev.toExponential(1)],
    ];
  },
  draw(api, s) {
    const { w, h } = api, R = this.R(api), ph = api.scene === "phone";
    const cx = w * 0.45, cy = h * 0.55, k = Math.min(w, h) * 0.33;
    const P = (p) => [cx + k * (p[1] - 0.5 * p[0]), cy - k * (p[2] - 0.32 * p[0])];     // 斜二测：x 向左下，y 向右，z 向上
    const cols = [api.css("--red"), api.css("--green"), api.css("--blue")], names = ["x", "y", "z"];
    const O = P([0, 0, 0]);
    api.ctx.globalAlpha = 0.4;
    for (let i = 0; i < 3; i++) { const e = [0, 0, 0]; e[i] = 1.25; const q = P(e); api.arrow(...O, ...q, cols[i], 2); api.label(names[i] + "_a", q[0] + 6, q[1] - 6, cols[i], 13); }
    api.ctx.globalAlpha = 1;
    if (ph) {    // 手机：屏幕在 {b} 的 xy 平面内
      const c = api.ctx, corners = [[-0.35, -0.65], [0.35, -0.65], [0.35, 0.65], [-0.35, 0.65]].map(([x, y]) => P([R[0][0] * x + R[0][1] * y, R[1][0] * x + R[1][1] * y, R[2][0] * x + R[2][1] * y]));
      c.beginPath(); corners.forEach((p, i) => (i ? c.lineTo(...p) : c.moveTo(...p))); c.closePath();
      c.fillStyle = "rgba(60,90,140,0.25)"; c.fill(); c.strokeStyle = api.css("--ink"); c.lineWidth = 2; c.stroke();
    } else {     // 相机：沿光轴 z_b 的视锥
      const z = [R[0][2], R[1][2], R[2][2]];
      for (const [x, y] of [[-0.25, -0.18], [0.25, -0.18], [0.25, 0.18], [-0.25, 0.18]]) {
        const q = P([0.9 * z[0] + R[0][0] * x + R[0][1] * y, 0.9 * z[1] + R[1][0] * x + R[1][1] * y, 0.9 * z[2] + R[2][0] * x + R[2][1] * y]);
        api.line(...O, ...q, api.css("--muted"), 1, [4, 4]);
      }
    }
    for (let j = 0; j < 3; j++) { const q = P([R[0][j], R[1][j], R[2][j]]); api.arrow(...O, ...q, cols[j], 4); api.label(names[j] + "_b", q[0] + 6, q[1] + 12, cols[j], 14); }
    const pa = this.arrowA(api), sc = ph ? 1.2 / 9.81 : 1.6;
    const t = P([pa[0] * sc, pa[1] * sc, pa[2] * sc]);
    api.arrow(...O, ...t, api.css("--ink"), 3);
    api.label(ph ? api.T("加速度读数", "reading") : "d", t[0] + 8, t[1], api.css("--ink"), 14);
    api.label(api.T("箭头在 {a} 中固定不动；转动的是 {b}", "the arrow is fixed in {a}; {b} turns"), 12, 18, api.css("--muted"), 13);
  },
});
