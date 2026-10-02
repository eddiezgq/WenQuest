// 实验 3.5 指标与求和（配 3.5 节）。场景 proj：表面坐标系 {b} 相对 {a} 绕 x 轴倾斜 θ，P_b = diag(1, 1, 0)，
// (P_a)_ij = r_ik r_jl (P_b)_kl（式 (3.5.3)），逐项列出九项并求和，与矩阵乘法 R P_b Rᵀ 对照。
// 场景 receipt：购物小票，总价 = p_i q_i（式 (3.5.1) 的形式）。
WQ.lab({
  title: ["实验 3.5 指标与求和", "Lab 3.5 Indices and summation"],
  goal: ["按求和约定逐项展开一个张量分量的变换公式，看哪些项不为零；体会“对应相乘再相加”的指标运算。",
         "Expand the transformation of one tensor component term by term with the summation convention and see which terms survive; get used to “multiply matching entries and add”."],
  scenes: [
    { id: "proj", robot: true, name: ["投影张量的分量", "Components of the projection tensor"], hide: ["q1", "q2", "q3"],
      problem: { title: ["机器人问题：倾斜表面上的投影张量", "Robot problem: the projection tensor of a tilted surface"],
                 text: ["抛光时只保留沿表面的速度。投影张量在表面坐标系中是 diag(1, 1, 0)，在机座坐标系中的每个分量都是九项之和。",
                        "Polishing keeps only the velocity along the surface. The projection tensor is diag(1, 1, 0) in the surface frame; in the base frame each component is a sum of nine terms."] } },
    { id: "receipt", name: ["购物小票", "A shopping receipt"], hide: ["i", "j", "theta"],
      problem: { title: ["生活中的例子：总价 = 单价 × 数量，再相加", "Everyday example: total = price × quantity, summed"],
                 text: ["三种商品的单价为 12、8、20 元。总价 p_i q_i 就是一次求和约定。",
                        "Three items cost 12, 8 and 20 yuan. The total p_i q_i is one use of the summation convention."] } },
  ],
  params: [
    { id: "i", name: ["自由指标 i", "Free index i"], min: 1, max: 3, step: 1, value: 1, unit: "", digits: 0 },
    { id: "j", name: ["自由指标 j", "Free index j"], min: 1, max: 3, step: 1, value: 1, unit: "", digits: 0 },
    { id: "theta", name: ["表面倾角 θ", "Surface tilt θ"], min: 0, max: 90, step: 1, value: 20, unit: "°", digits: 0 },
    { id: "q1", name: ["商品 1 的数量 q₁（单价 12 元）", "Quantity q₁ (12 yuan each)"], min: 0, max: 10, step: 1, value: 1, unit: "", digits: 0 },
    { id: "q2", name: ["商品 2 的数量 q₂（单价 8 元）", "Quantity q₂ (8 yuan each)"], min: 0, max: 10, step: 1, value: 1, unit: "", digits: 0 },
    { id: "q3", name: ["商品 3 的数量 q₃（单价 20 元）", "Quantity q₃ (20 yuan each)"], min: 0, max: 10, step: 1, value: 1, unit: "", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "p23", robot: true, text: ["取 θ = 20°，读出 (P_a)₂₃，并指出九项中哪几项不为零。", "With θ = 20°, read (P_a)₂₃ and say which of the nine terms are non-zero."],
      demo: { scene: "proj", set: { i: 2, j: 3, theta: 20 }, press: [] } },
    { id: "half", robot: true, text: ["找出使 (P_a)₃₃ = 0.5 的倾角 θ。", "Find the tilt θ that makes (P_a)₃₃ = 0.5."],
      demo: { scene: "proj", set: { i: 3, j: 3, theta: 45 }, press: [] } },
    { id: "wall", robot: true, text: ["使表面竖直（θ = 90°），观察 P_a 中哪些分量变为零，并用法线方向解释。", "Make the surface vertical (θ = 90°); see which entries of P_a vanish and explain them with the normal."],
      demo: { scene: "proj", set: { i: 2, j: 2, theta: 90 }, press: [] } },
    { id: "buy", text: ["调整数量，使总价恰好为 100 元。", "Choose quantities so that the total is exactly 100 yuan."],
      demo: { scene: "receipt", set: { q1: 5, q2: 0, q3: 2 }, press: [] } },
  ],
  think: ["(P_a)_ij 的九项中，为什么 k ≠ l 的项总是零？如果 P_b 不是对角矩阵，情况会怎样？",
          "Why are the terms with k ≠ l always zero here? What would change if P_b were not diagonal?"],

  R(api) { const t = api.p.theta * Math.PI / 180, c = Math.cos(t), s = Math.sin(t); return [[1, 0, 0], [0, c, -s], [0, s, c]]; },
  Pb: [[1, 0, 0], [0, 1, 0], [0, 0, 0]],
  Pa(api) {
    const R = this.R(api), out = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
    for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) for (let k = 0; k < 3; k++) for (let l = 0; l < 3; l++) out[i][j] += R[i][k] * R[j][l] * this.Pb[k][l];
    return out;
  },
  reset(api, s) {},
  readouts(api, s) {
    if (api.scene === "receipt") {
      const p = [12, 8, 20], q = [api.p.q1, api.p.q2, api.p.q3], tot = p[0] * q[0] + p[1] * q[1] + p[2] * q[2];
      if (tot === 100) api.done("buy");
      return [[["p₁q₁ + p₂q₂ + p₃q₃", "p₁q₁ + p₂q₂ + p₃q₃"], `${p[0]}×${q[0]} + ${p[1]}×${q[1]} + ${p[2]}×${q[2]}`],
              [["总价 p_i q_i", "total p_i q_i"], tot + api.T(" 元", " yuan")]];
    }
    const R = this.R(api), i = api.p.i - 1, j = api.p.j - 1, Pa = this.Pa(api);
    const terms = [];
    let sum = 0;
    for (let k = 0; k < 3; k++) for (let l = 0; l < 3; l++) {
      const v = R[i][k] * R[j][l] * this.Pb[k][l];
      sum += v;
      if (Math.abs(v) > 1e-12) terms.push(`(k,l)=(${k + 1},${l + 1}): ${api.fmt(R[i][k], 4)}×${api.fmt(R[j][l], 4)}×${this.Pb[k][l]}`);
    }
    if (api.p.i === 2 && api.p.j === 3 && api.p.theta === 20) api.done("p23");
    if (api.p.i === 3 && api.p.j === 3 && Math.abs(sum - 0.5) < 1e-9) api.done("half");
    if (api.p.theta === 90) api.done("wall");
    const row = (r) => `[${api.fmt(Pa[r][0], 4)}, ${api.fmt(Pa[r][1], 4)}, ${api.fmt(Pa[r][2], 4)}]`;
    return [
      [["不为零的项", "non-zero terms"], terms.length ? terms.join("；") : api.T("全部为零", "all zero")],
      [[`逐项求和 (P_a)${api.p.i}${api.p.j}`, `sum of terms (P_a)${api.p.i}${api.p.j}`], api.fmt(sum, 4)],
      [["P_a = R P_b Rᵀ 第 1 行", "P_a = R P_b Rᵀ row 1"], row(0)],
      [["第 2 行", "row 2"], row(1)],
      [["第 3 行", "row 3"], row(2)],
      [["迹 (P_a)_ii", "trace (P_a)_ii"], api.fmt(Pa[0][0] + Pa[1][1] + Pa[2][2], 4)],
    ];
  },
  draw(api, s) {
    const { w, h } = api, ink = api.css("--ink"), muted = api.css("--muted");
    if (api.scene === "receipt") {
      const p = [12, 8, 20], q = [api.p.q1, api.p.q2, api.p.q3], names = [api.T("螺丝刀", "screwdriver"), api.T("胶带", "tape"), api.T("扳手", "wrench")];
      const x0 = w * 0.3, y0 = h * 0.18, rw = w * 0.4;
      api.rect(x0, y0, rw, h * 0.66, api.css("--panel"), muted, 6);
      api.label(api.T("购物小票", "Receipt"), x0 + rw / 2, y0 + 24, ink, 16, "center");
      let tot = 0;
      for (let k = 0; k < 3; k++) {
        const y = y0 + 70 + 40 * k, sub = p[k] * q[k]; tot += sub;
        api.label(names[k], x0 + 16, y, ink, 14);
        api.label(`${p[k]} × ${q[k]}`, x0 + rw * 0.55, y, muted, 14, "center");
        api.label(String(sub), x0 + rw - 16, y, ink, 14, "right");
      }
      api.line(x0 + 12, y0 + 70 + 40 * 2.6, x0 + rw - 12, y0 + 70 + 40 * 2.6, muted, 1, [4, 3]);
      api.label(api.T("合计 p_i q_i", "total p_i q_i"), x0 + 16, y0 + 70 + 40 * 3.2, ink, 15);
      api.label(String(tot), x0 + rw - 16, y0 + 70 + 40 * 3.2, tot === 100 ? api.css("--green") : ink, 18, "right");
      return;
    }
    // 侧视：y 向右、z 向上；表面倾斜 θ，法线 n = (0, −sin θ, cos θ)
    const t = api.p.theta * Math.PI / 180, cx = w * 0.42, cy = h * 0.6, L = Math.min(w, h) * 0.42;
    const X = (y, z) => [cx + L * y, cy - L * z];
    api.ctx.beginPath(); api.ctx.moveTo(...X(-Math.cos(t), -Math.sin(t))); api.ctx.lineTo(...X(Math.cos(t), Math.sin(t)));
    api.ctx.lineTo(...X(Math.cos(t), -1.0)); api.ctx.lineTo(...X(-Math.cos(t), -1.0)); api.ctx.closePath();
    api.ctx.fillStyle = "rgba(150,160,170,0.25)"; api.ctx.fill();
    api.line(...X(-Math.cos(t), -Math.sin(t)), ...X(Math.cos(t), Math.sin(t)), muted, 3);
    api.arrow(cx, cy, ...X(-Math.sin(t) * 0.6, Math.cos(t) * 0.6), api.css("--amber"), 3);
    api.label("n", ...X(-Math.sin(t) * 0.68, Math.cos(t) * 0.68), api.css("--amber"), 15);
    const ya = X(0.35, 0), za = X(0, 0.35);                  // 侧视中的两根轴：y 绿、z 蓝（全书配色）
    api.arrow(cx, cy, ...ya, api.css("--green"), 2.5); api.label("y_a", ya[0] + 6, ya[1], api.css("--green"), 13);
    api.arrow(cx, cy, ...za, api.css("--blue"), 2.5); api.label("z_a", za[0] + 6, za[1] - 4, api.css("--blue"), 13);
    api.label("{a}", cx - 26, cy + 14, ink, 13);
    api.label(api.T(`侧视：表面倾角 θ = ${api.p.theta}°；x 轴垂直于屏幕`, `side view: tilt θ = ${api.p.theta}°; x is normal to the screen`), 12, 18, muted, 13);
  },
});
