// 实验 33.5 轴的疲劳安全系数（配 33.5 节）。外伸段只受转矩，键槽处应力集中；改材料、直径、表面、转矩，看安全系数和极限应力线图。
// 系数与正文程序相同：q 按 Neuber–Kuhn 式，ε = 1.24 d^−0.107，β = a σb^b，Kτ = kτ/ε + 1/β − 1，ψτ = τ₋₁/(σb/√3)。
const MAT33_5 = [
  { zh: "45 钢调质", en: "45 steel, Q&T", sb: 640, t1: 155 },
  { zh: "40Cr 调质", en: "40Cr, Q&T", sb: 735, t1: 200 },
];
const SURF33_5 = [{ zh: "磨削", en: "ground", a: 1.58, b: -0.085 }, { zh: "精车", en: "machined", a: 4.51, b: -0.265 }];
function calc33_5(api) {
  const p = api.p, m = MAT33_5[Math.round(p.mat)], sf = SURF33_5[Math.round(p.surf)];
  const life = api.scene === "life";
  const d = p.d, T = p.T * 1000;                                  // N·mm
  const Kts = life ? 1.5 : 3.0;                                    // 键槽（端铣，r/d = 0.02）/ 电钻主轴的轴肩（圆角 0.5，估计）
  const r = life ? 0.5 : 0.02 * d;
  const S = m.sb / 6.894757, c = [0.190, -2.51e-3, 1.35e-5, -2.67e-8];
  const sqa = (c[0] + c[1] * S + c[2] * S * S + c[3] * S * S * S) * Math.sqrt(25.4);
  const q = 1 / (1 + sqa / Math.sqrt(r));
  const kt = 1 + q * (Kts - 1), eps = 1.24 * Math.pow(d, -0.107), beta = sf.a * Math.pow(m.sb, sf.b);
  const K = kt / eps + 1 / beta - 1, psi = m.t1 / (m.sb / Math.sqrt(3));
  const tau = 16 * T / (Math.PI * d * d * d), ta = tau / 2;
  const Sf = m.t1 / (K * ta + psi * ta);
  return { m, sf, q, kt, eps, beta, K, psi, tau, ta, S: Sf, tb: m.sb / Math.sqrt(3) };
}
WQ.lab({
  title: ["实验 33.5 轴的疲劳安全系数", "Lab 33.5 Fatigue safety factor of a shaft"],
  goal: ["外伸段只传转矩、开有键槽：改材料、直径、表面加工和转矩，看安全系数怎样变化，找出满足 [S] = 1.5 的方案。",
         "The extension carries torque only and has a keyseat: change material, diameter, finish and torque, watch the safety factor and find a design with [S] = 1.5."],
  scenes: [
    { id: "robot", robot: true, name: ["WQR-105 外伸段", "WQR-105 extension"], hide: [],
      problem: { title: ["工程问题：截面 IV 的疲劳校核", "Engineering problem: fatigue check of section IV"],
                 text: ["Ø30 外伸段、端铣键槽，额定转矩 350 N·m 按脉动循环（每次起停一次）。45 钢调质时 S = 1.38 < 1.5，怎么改？",
                        "Ø30 extension with an end-milled keyseat; 350 N·m, repeated (one cycle per start). With 45 steel S = 1.38 < 1.5 — what would you change?"] } },
    { id: "life", name: ["电钻主轴", "Drill spindle"],
      params: { d: { min: 8, max: 16, step: 1, value: 10 }, T: { min: 5, max: 40, step: 1, value: 25 } },
      problem: { title: ["生活中的例子：电钻拧大螺钉", "Everyday example: driving big screws with a drill"],
                 text: ["电钻的主轴只传转矩。每拧一颗螺钉，转矩从零升到离合器设定的最大值（例如 25 N·m）再回到零，是一次脉动循环。主轴在夹头一端有轴肩（圆角约 0.5 mm）。",
                        "A drill spindle carries torque only. Each screw takes the torque from zero up to the clutch setting (25 N·m, say) and back: one repeated cycle. The spindle has a shoulder (fillet about 0.5 mm) at the chuck end."] } },
  ],
  params: [
    { id: "mat", name: ["材料（0 = 45 钢，1 = 40Cr）", "Material (0 = 45 steel, 1 = 40Cr)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "d", name: ["直径 d", "Diameter d"], min: 26, max: 40, step: 1, value: 30, unit: "mm", digits: 0 },
    { id: "surf", name: ["表面（0 = 磨削，1 = 精车）", "Finish (0 = ground, 1 = machined)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "T", name: ["转矩 T", "Torque T"], min: 200, max: 500, step: 10, value: 350, unit: "N·m", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["校核", "Check"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "var(--red)", name: ["零件极限线", "component limit line"] }, { color: "var(--accent)", name: ["工作点", "operating point"] }],
  tasks: [
    { id: "base", robot: true, text: ["45 钢、Ø30、磨削、350 N·m 校核一次：S 小于 1.5，记下 Kτ 和 S。", "Check 45 steel, Ø30, ground, 350 N·m: S is below 1.5; note Kτ and S."],
      demo: { scene: "robot", set: { mat: 0, d: 30, surf: 0, T: 350 }, press: ["start"], wait: 1 } },
    { id: "fix", robot: true, text: ["只改材料或只改直径，各找一个 S ≥ 1.5 的方案。", "Find a design with S ≥ 1.5 by changing only the material, or only the diameter."],
      demo: { scene: "robot", set: { mat: 1, d: 30, surf: 0, T: 350 }, press: ["start"], wait: 1 } },
    { id: "life", text: ["电钻主轴：25 N·m 下 Ø10 的 45 钢主轴够不够？多粗才够 1.5？", "Drill spindle: is a Ø10, 45-steel spindle enough at 25 N·m? How thick for 1.5?"],
      demo: { scene: "life", set: { mat: 0, d: 11, surf: 0, T: 25 }, press: ["start"], wait: 1 } },
  ],
  think: ["把表面从“磨削”换成“精车”，S 降了多少？为什么高强度钢对表面质量更敏感？",
          "How much does S drop from ground to machined? Why is a stronger steel more sensitive to the finish?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    s.r = calc33_5(api);
    if (api.scene === "robot" && Math.round(api.p.mat) === 0 && api.p.d === 30 && Math.round(api.p.surf) === 0 && api.p.T === 350 && s.r.S < 1.5) api.done("base");
    if (api.scene === "robot" && api.p.T >= 350 && s.r.S >= 1.5 && (Math.round(api.p.mat) === 1 ? api.p.d === 30 : api.p.d > 30)) api.done("fix");
    if (api.scene === "life" && api.p.T >= 25 && s.r.S >= 1.5) api.done("life");
    api.stop();
  },
  readouts(api, s) {
    const r = s.r || calc33_5(api), f = api.fmt;
    return [
      [["名义切应力 τ", "Nominal shear stress τ"], f(r.tau, 1) + " MPa"],
      [["缺口敏感系数 q", "Notch sensitivity q"], f(r.q, 3)],
      [["有效应力集中系数 kτ", "Fatigue factor kτ"], f(r.kt, 3)],
      [["尺寸系数 ε、表面系数 β", "Size ε, surface β"], f(r.eps, 3) + "，" + f(r.beta, 3)],
      [["综合影响系数 Kτ", "Combined factor Kτ"], f(r.K, 3)],
      [["安全系数 S", "Safety factor S"], s.r ? f(r.S, 2) + (r.S >= 1.5 ? " ≥ 1.5 ✓" : " < 1.5 ✗") : api.T("按“校核”", "press Check")],
    ];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, r = s.r || calc33_5(api);
    const life = api.scene === "life";
    // 左：轴段和键槽（或中轴）的示意
    const cx = w * 0.2, cy = h * 0.45, R = Math.min(w * 0.12, h * 0.3) * api.p.d / 40;
    api.circle(cx, cy, R, css("--panel"), css("--ink"));
    if (!life) api.rect(cx - R * 0.27, cy - R, R * 0.54, R * 0.27, css("--bg") || "#fff", css("--ink"));
    else api.rect(cx - R * 0.45, cy - R * 0.45, R * 0.9, R * 0.9, css("--bg") || "#fff", css("--ink"));
    api.label("Ø" + api.p.d, cx, cy + R + 16, css("--ink"), 13, "center");
    api.label(api.T(r.m.zh + "，" + r.sf.zh, r.m.en + ", " + r.sf.en), cx, cy + R + 34, css("--muted"), 12, "center");
    for (let k = 0; k < 3; k++) {
      const a = -Math.PI / 2 + k * 0.5;
      api.arrow(cx + (R + 10) * Math.cos(a), cy + (R + 10) * Math.sin(a), cx + (R + 10) * Math.cos(a + 0.4), cy + (R + 10) * Math.sin(a + 0.4), css("--purple") || css("--accent"), 2);
    }
    // 右：τa–τm 极限线与工作点
    const tA = r.m.t1 / r.K;
    const P = api.plot(w * 0.42, h * 0.08, w * 0.54, h * 0.78, [
      { pts: [[0, tA], [r.tb, 0]], color: css("--red") },
      { pts: [[0, tA / 1.5], [r.tb / 1.5, 0]], color: css("--muted") },          // 许用线：极限线按原点缩小 1/[S]
      { pts: [[0, 0], [Math.max(r.ta * 1.6, 60), Math.max(r.ta * 1.6, 60)]], color: css("--grid") },
    ], { xmin: 0, xmax: 450, ymin: 0, ymax: 90, xlabel: "τm / MPa", ylabel: "τa / MPa" });
    api.circle(P.X(r.ta), P.Y(r.ta), 6, s.r ? css("--accent") : css("--muted"), css("--ink"));
    api.label(api.T("[S] = 1.5", "[S] = 1.5"), P.X(20), P.Y(tA / 1.5) - 10, css("--muted"), 11);
  },
});
