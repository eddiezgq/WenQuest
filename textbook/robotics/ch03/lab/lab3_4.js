// 实验 3.4 转动坐标系：矢量分量与张量分量（配 3.4 节）。平面内的二阶对称张量 A：物体自身主轴方向与 {a} 的 x 轴成 γ，
// A_a = R(γ) diag(λ1, λ2) R(γ)ᵀ。{b} 相对 {a} 转过 β：A_b = R(β)ᵀ A_a R(β)（式 (3.4.4)），矢量 u_b = R(β)ᵀ u_a。
// 场景 plate：算例 3.4.2 的板的惯量张量（平面内两个主惯量，单位 10⁻³ kg·m²），输入角速度 ω（1 rad/s），输出角动量 L = I ω。
// 场景 ski：滑雪板的“推力 → 速度”张量（沿板 0.040、横向 0.004，单位 (m/s)/N），输入推力 F（10 N），输出速度 v。
WQ.lab({
  title: ["实验 3.4 转动坐标系：矢量分量与张量分量", "Lab 3.4 Turning the frame: vector and tensor components"],
  goal: ["转动坐标系 {b}，看矢量的分量和张量的分量矩阵怎样变化，而箭头和椭圆本身不动；找出主轴。",
         "Turn frame {b}: watch the components of a vector and the component matrix of a tensor change while the arrows and the ellipse stay; find the principal axes."],
  scenes: [
    { id: "plate", robot: true, name: ["夹爪中的板状零件", "A plate in the gripper"],
      problem: { title: ["机器人问题：板的角动量为什么不沿转轴", "Robot problem: why the plate's angular momentum leaves the axis"],
                 text: ["板的惯量张量把角速度 ω 变成角动量 L。板相对坐标轴斜放时，惯量的分量矩阵出现非对角元素，L 一般不平行于 ω。（俯视，只看板面内的两个方向）",
                        "The plate's inertia tensor turns the angular velocity ω into the angular momentum L. With the plate askew, the component matrix has off-diagonal entries and L is generally not parallel to ω. (Top view, the two in-plane directions only)"] } },
    { id: "ski", name: ["雪地上的滑雪板", "A ski on snow"],
      problem: { title: ["生活中的例子：斜着推滑雪板", "Everyday example: pushing a ski at an angle"],
                 text: ["顺着板推容易滑走，横着推几乎不动。推力 F 与速度 v 之间是一个对称张量，主轴沿板长和板宽。",
                        "Pushed along its length the ski slides away; pushed sideways it hardly moves. Push F and velocity v are related by a symmetric tensor with principal axes along and across the ski."] },
      params: { gamma: { value: 25 }, beta: { value: 0 }, phi: { value: 60 } } },
  ],
  params: [
    { id: "gamma", name: ["物体主轴的方向 γ", "Object's principal axis γ"], min: -90, max: 90, step: 1, value: 25, unit: "°", digits: 0 },
    { id: "beta", name: ["坐标系 {b} 的转角 β", "Turn of frame {b}, β"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "phi", name: ["输入矢量的方向 φ", "Direction of the input vector φ"], min: -180, max: 180, step: 1, value: 70, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "diag", robot: true, text: ["转动 {b}，使惯量的分量矩阵 I_b 成为对角矩阵（非对角元素为 0）。", "Turn {b} until the component matrix I_b is diagonal (zero off-diagonal entries)."],
      demo: { scene: "plate", set: { gamma: 25, beta: 25, phi: 70 }, press: [] } },
    { id: "par", robot: true, text: ["改变角速度的方向，使角动量 L 与 ω 平行。", "Change the direction of ω until L is parallel to it."],
      demo: { scene: "plate", set: { gamma: 25, beta: 0, phi: 25 }, press: [] } },
    { id: "equal", robot: true, text: ["转动 {b}，使 I_b 的两个对角元素相等。此时 β 与 γ 相差多少？两个对角元素等于什么？", "Turn {b} until the two diagonal entries of I_b are equal. How far apart are β and γ, and what are those entries?"],
      demo: { scene: "plate", set: { gamma: 25, beta: 70, phi: 70 }, press: [] } },
    { id: "ski", text: ["滑雪板：垂直于板长方向推，验证此时运动方向与推力方向一致（只是很慢）。", "Ski: push across the ski and check that it moves in the direction of the push (only slowly)."],
      demo: { scene: "ski", set: { gamma: 25, beta: 0, phi: 115 }, press: [] } },
  ],
  think: ["无论 {b} 怎样转，迹 tr A_b 都不变。用式 (3.4.4) 证明这一点，并说明它对两个对角元素之和意味着什么。",
          "However {b} turns, tr A_b stays the same. Prove it from Eq. (3.4.4) and say what it means for the sum of the diagonal entries."],

  lam(api) { return api.scene === "ski" ? [0.040, 0.004] : [6.7333, 15.0667]; },
  rot(t) { return [[Math.cos(t), -Math.sin(t)], [Math.sin(t), Math.cos(t)]]; },
  mm(A, B) { return [[A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]], [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]]; },
  tr(A) { return [[A[0][0], A[1][0]], [A[0][1], A[1][1]]]; },
  mv(A, v) { return [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]]; },
  calc(api) {
    const d = Math.PI / 180, l = this.lam(api), G = this.rot(api.p.gamma * d), B = this.rot(api.p.beta * d);
    const Aa = this.mm(this.mm(G, [[l[0], 0], [0, l[1]]]), this.tr(G));
    const Ab = this.mm(this.mm(this.tr(B), Aa), B);
    const mag = api.scene === "ski" ? 10 : 1, f = api.p.phi * d;
    const ua = [mag * Math.cos(f), mag * Math.sin(f)], wa = this.mv(Aa, ua);
    const ub = this.mv(this.tr(B), ua), wb = this.mv(this.tr(B), wa);
    const ang = Math.abs(Math.atan2(ua[0] * wa[1] - ua[1] * wa[0], ua[0] * wa[0] + ua[1] * wa[1])) / d;   // atan2(|u×w|, u·w)：夹角接近 0 时也准确
    return { Aa, Ab, ua, wa, ub, wb, ang, l };
  },
  reset(api, s) {},
  readouts(api, s) {
    const c = this.calc(api), ski = api.scene === "ski", sc = Math.max(c.l[0], c.l[1]);
    if (!ski && Math.abs(c.Ab[0][1]) < 1e-9 * sc) api.done("diag");
    if (!ski && (c.ang < 1e-6 || c.ang > 180 - 1e-6)) api.done("par");
    if (!ski && Math.abs(c.Ab[0][0] - c.Ab[1][1]) < 1e-9 * sc) api.done("equal");
    if (ski && c.ang < 1e-6 && Math.abs(Math.cos((api.p.phi - api.p.gamma) * Math.PI / 180)) < 1e-9) api.done("ski");
    const dg = ski ? 4 : 3, M = (A) => `[${api.fmt(A[0][0], dg)}, ${api.fmt(A[0][1], dg)}; ${api.fmt(A[1][0], dg)}, ${api.fmt(A[1][1], dg)}]`;
    const V = (v, k) => `(${api.fmt(v[0], k)}, ${api.fmt(v[1], k)})`;
    const det = (A) => A[0][0] * A[1][1] - A[0][1] * A[1][0];
    const nT = ski ? ["张量 M", "tensor M"] : ["惯量 I（10⁻³ kg·m²）", "inertia I (10⁻³ kg·m²)"];
    return [
      [[nT[0] + " 在 {a} 中", nT[1] + " in {a}"], M(c.Aa)],
      [[nT[0] + " 在 {b} 中", nT[1] + " in {b}"], M(c.Ab)],
      [ski ? ["推力 F 在 {a} / {b} 中（N）", "push F in {a} / {b} (N)"] : ["ω 在 {a} / {b} 中（rad/s）", "ω in {a} / {b} (rad/s)"], V(c.ua, 2) + " / " + V(c.ub, 2)],
      [ski ? ["速度 v 在 {a} / {b} 中（m/s）", "velocity v in {a} / {b} (m/s)"] : ["L 在 {a} / {b} 中（10⁻³ kg·m²/s）", "L in {a} / {b} (10⁻³ kg·m²/s)"], V(c.wa, 3) + " / " + V(c.wb, 3)],
      [["迹：{a} / {b}", "trace: {a} / {b}"], api.fmt(c.Aa[0][0] + c.Aa[1][1], dg) + " / " + api.fmt(c.Ab[0][0] + c.Ab[1][1], dg)],
      [["行列式：{a} / {b}", "determinant: {a} / {b}"], api.fmt(det(c.Aa), ski ? 6 : 2) + " / " + api.fmt(det(c.Ab), ski ? 6 : 2)],
      [["输入与输出的夹角", "angle between input and output"], api.fmt(c.ang, 1) + "°"],
    ];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api), ski = api.scene === "ski", d = Math.PI / 180;
    const cx = w * 0.42, cy = h * 0.52, R = Math.min(w, h) * 0.36;
    const X = (x, y) => [cx + R * x, cy - R * y];
    const g = api.p.gamma * d, sc = 1 / Math.max(c.l[0], c.l[1]);
    // 物体
    const ctx = api.ctx;
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(-g);
    if (ski) api.rect(-R * 0.95, -R * 0.07, R * 1.9, R * 0.14, "rgba(88,140,220,0.35)", api.css("--accent"), 12);
    else api.rect(-R * 0.6, -R * 0.4, R * 1.2, R * 0.8, "rgba(210,153,34,0.25)", api.css("--amber"), 4);
    ctx.restore();
    // 张量的椭圆：单位圆的像（按最大主值归一化）
    ctx.beginPath();
    for (let k = 0; k <= 120; k++) {
      const t = 2 * Math.PI * k / 120, p = this.mv(c.Aa, [Math.cos(t), Math.sin(t)]);
      const q = X(p[0] * sc * 0.85, p[1] * sc * 0.85); k ? ctx.lineTo(...q) : ctx.moveTo(...q);
    }
    ctx.strokeStyle = api.css("--amber"); ctx.lineWidth = 2.5; ctx.stroke();
    // 坐标系 {a}（淡）与 {b}
    ctx.globalAlpha = 0.35; api.frame(cx, cy, 0, R * 1.05, ["x_a", "y_a"], ""); ctx.globalAlpha = 1;
    api.frame(cx, cy, api.p.beta, R * 1.15, ["x_b", "y_b"], "{b}");
    // 输入与输出矢量
    const nu = Math.hypot(...c.ua), nw = Math.hypot(...c.wa);
    const ui = X(c.ua[0] / nu * 0.75, c.ua[1] / nu * 0.75), wi = X(c.wa[0] / nw * 0.9, c.wa[1] / nw * 0.9);
    api.arrow(cx, cy, ...ui, api.css("--ink"), 3);
    api.label(ski ? "F" : "ω", ui[0] + 8, ui[1] - 8, api.css("--ink"), 15);
    api.arrow(cx, cy, ...wi, api.css("--blue"), 3);
    api.label(ski ? "v" : "L", wi[0] + 8, wi[1] + 10, api.css("--blue"), 15);
    api.label(api.T("箭头只画方向；黄色椭圆 = 张量（单位圆的像）", "arrows show directions only; yellow ellipse = the tensor (image of the unit circle)"), 12, h - 14, api.css("--muted"), 12);
  },
});
