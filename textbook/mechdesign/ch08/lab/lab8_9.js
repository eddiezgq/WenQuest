// 实验 8.9 两个曲面接触的赫兹应力（配 8.9 节）。线接触（两个平行圆柱，或圆柱压在平面上），与程序 8.9.1 同一组公式（_ch8.hertz_line、line_subsurface）：
// R = 1/(1/R1 + 1/R2)，1/E* = (1 − ν1²)/E1 + (1 − ν2²)/E2，半宽 a = √(4F′R/(πE*))，最大压力 p0 = 2F′/(πa)，F′ = F/b；
// 对称轴下的主切应力 τ1 = |σx − σz|/2（McEwen），最大约 0.30 p0、深度约 0.78a。
// 齿轮场景取 WQR-105 第二级在节点（程序 8.9.1）；AGV 轮和火车轮轨的尺寸、载荷是本书设定的示意值，火车轮轨实际是椭圆接触，这里按线接触示意。
const MAT8_9 = [{ E: 210000, nu: 0.3, name: ["钢", "steel"] }, { E: 3000, nu: 0.4, name: ["MC 尼龙", "MC nylon"] }];
function hertz8_9(p) {
  const m1 = MAT8_9[Math.round(p.mat)], m2 = MAT8_9[0];
  const Es = 1 / ((1 - m1.nu ** 2) / m1.E + (1 - m2.nu ** 2) / m2.E);
  const inv = 1 / p.R1 + (p.R2 > 0 ? 1 / p.R2 : 0);                 // R2 = 0 表示平面
  const R = 1 / inv, Fp = p.F / p.b;
  const a = Math.sqrt(4 * Fp * R / (Math.PI * Es)), p0 = 2 * Fp / (Math.PI * a);
  return { Es, R, Fp, a, p0, tmax: 0.300 * p0, zmax: 0.786 * a, m1 };
}
function sub8_9(z) { const s = Math.sqrt(1 + z * z), sx = -((1 + 2 * z * z) / s - 2 * z), sz = -1 / s; return [sx, sz, Math.abs(sx - sz) / 2]; }
WQ.lab({
  title: ["实验 8.9 两个曲面接触的赫兹应力", "Lab 8.9 Hertz stresses between two curved surfaces"],
  goal: ["改载荷、曲率半径、宽度和材料，看接触宽度、最大接触压力和表面下的切应力怎样变化，理解为什么齿面、轴承、车轮的损坏常从表面以下开始。",
         "Change the load, radii, width and materials and see how the contact width, peak pressure and subsurface shear change — and why tooth flanks, bearings and wheels often fail from below the surface."],
  scenes: [
    { id: "gear", robot: true, name: ["WQR-105 第二级齿面", "WQR-105 stage-2 tooth flanks"],
      problem: { title: ["工程问题：齿面为什么会点蚀", "Engineering problem: why tooth flanks pit"],
                 text: ["减速器的小齿轮每转一圈，每个齿面被压一次。两个齿面在节点接触，像两个圆柱压在一起。接触区只有零点几毫米宽，压力有多大？最危险的地方在表面还是在里面？",
                        "Each pinion flank is pressed once per revolution. At the pitch point two flanks touch like two cylinders. The contact is a fraction of a millimeter wide — how high is the pressure, and is the worst place at or below the surface?"] } },
    { id: "agv", robot: true, name: ["AGV 驱动轮", "AGV drive wheel"],
      problem: { title: ["工程问题：AGV 轮子用什么材料", "Engineering problem: what material for an AGV wheel"],
                 text: ["仓库里的 AGV 每个驱动轮压着 1500 N。钢轮硬、寿命长，但对地面不友好、噪声大；尼龙轮软一些。换材料，接触压力差多少？",
                        "Each AGV drive wheel carries 1500 N. A steel wheel is hard and lasts, but is hard on the floor and noisy; nylon is softer. How much does the contact pressure change?"] } },
    { id: "rail", name: ["火车车轮与钢轨", "Train wheel on rail"],
      problem: { title: ["生活中的例子：车轮与钢轨", "Everyday example: wheel and rail"],
                 text: ["一个火车车轮压在钢轨上的力有几十千牛，接触面只有指甲盖大小。这里按线接触粗略估一下接触压力（实际是椭圆接触）。",
                        "A train wheel presses on the rail with tens of kilonewtons over a patch the size of a fingernail. Here we estimate the pressure roughly as a line contact (it is really elliptical)."] } },
  ],
  params: [
    { id: "F", name: ["法向力 F", "Normal force F"], min: 100, max: 100000, step: 1, value: 3694, unit: "N", digits: 0 },
    { id: "b", name: ["接触长度（齿宽、轮宽）b", "Contact length (face or wheel width) b"], min: 5, max: 100, step: 1, value: 40, unit: "mm", digits: 0 },
    { id: "R1", name: ["曲率半径 R1", "Radius R1"], min: 2, max: 600, step: 0.01, value: 10.26, unit: "mm", digits: 2 },
    { id: "R2", name: ["曲率半径 R2（0 = 平面）", "Radius R2 (0 = flat)"], min: 0, max: 600, step: 0.01, value: 35.91, unit: "mm", digits: 2 },
    { id: "mat", name: ["第一个物体的材料（0 钢，1 尼龙）", "Material of body 1 (0 steel, 1 nylon)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "#d62728", name: ["表面接触压力", "surface pressure"] }, { color: "#1f77b4", name: ["中线下的主切应力 τ1", "principal shear τ1 below the centerline"] }],
  tasks: [
    { id: "gear", robot: true, text: ["WQR-105 第二级齿面（额定转矩，默认参数）：读出接触半宽、最大接触压力、最大切应力和它的深度。", "WQR-105 stage-2 flanks (rated torque, defaults): read the half-width, peak pressure, maximum shear and its depth."],
      demo: { scene: "gear", set: { F: 3694, b: 40, R1: 10.26, R2: 35.91, mat: 0 }, press: ["start"], wait: 1 } },
    { id: "load", robot: true, text: ["把载荷加倍（7388 N）：最大压力变成原来的几倍？为什么不是 2 倍？", "Double the load (7388 N): by what factor does the peak pressure grow, and why not 2?"],
      demo: { scene: "gear", set: { F: 7388, b: 40, R1: 10.26, R2: 35.91, mat: 0 }, press: ["start"], wait: 1 } },
    { id: "agv", robot: true, text: ["AGV 驱动轮（R1 = 75 mm、地面平、宽 50 mm、1500 N）：钢轮和尼龙轮各算一次，比较接触压力和接触宽度。", "AGV wheel (R1 = 75 mm, flat floor, 50 mm wide, 1500 N): compute for steel and for nylon and compare pressure and width."],
      demo: { scene: "agv", set: { F: 1500, b: 50, R1: 75, R2: 0, mat: 1 }, press: ["start"], wait: 1 } },
    { id: "rail", text: ["火车轮轨（R1 = 460 mm、钢轨顶面看作平面、接触长度 12 mm、80 kN）：最大接触压力是多少？", "Wheel on rail (R1 = 460 mm, rail head flat, 12 mm contact length, 80 kN): what is the peak pressure?"],
      demo: { scene: "rail", set: { F: 80000, b: 12, R1: 460, R2: 0, mat: 0 }, press: ["start"], wait: 1 } },
  ],
  think: ["程序 8.9.1 和本实验用同一组公式。最大切应力在表面以下约 0.78a 处，所以接触疲劳的裂纹常从表面以下开始，长到表面掉下一小块——这就是点蚀和剥落。表面硬化层（第 5 章的渗碳）至少要多深？",
          "Program 8.9.1 and this lab use the same formulas. The maximum shear lies about 0.78a below the surface, so contact-fatigue cracks often start below and grow up until a flake falls out — pitting and spalling. How deep must a hardened case (carburizing, Chapter 5) be at least?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    const p = api.p;
    s.r = hertz8_9(p);
    if (api.scene === "gear" && p.F < 5000) api.done("gear");
    if (api.scene === "gear" && p.F >= 7000) api.done("load");
    if (api.scene === "agv") api.done("agv");
    if (api.scene === "rail") api.done("rail");
    api.stop();
  },
  readouts(api, s) {
    const f = api.fmt, r = s.r;
    if (!r) return [[["状态", "Status"], api.T("按“计算”开始", "press Compute")]];
    return [
      [["当量曲率半径 R", "Equivalent radius R"], f(r.R, 2) + " mm"],
      [["当量弹性模量 E*", "Contact modulus E*"], f(r.Es, 0) + " MPa"],
      [["单位长度的力 F′", "Load per length F′"], f(r.Fp, 1) + " N/mm"],
      [["接触半宽 a", "Half-width a"], f(r.a, 3) + " mm"],
      [["最大接触压力 p0", "Peak pressure p0"], f(r.p0, 0) + " MPa"],
      [["最大主切应力 τ1（≈ 0.30 p0）", "Max principal shear τ1 (≈ 0.30 p0)"], f(r.tmax, 0) + " MPa"],
      [["它的深度（≈ 0.78 a）", "Its depth (≈ 0.78 a)"], f(r.zmax, 3) + " mm"],
    ];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    if (!s.r) { api.label(api.T("按“计算”算接触应力", "Press Compute for the contact stresses"), w / 2, h / 2, css("--muted"), 14, "center"); return; }
    const r = s.r, pts = [], sub = [];
    for (let i = 0; i <= 100; i++) { const x = -1.5 + 3 * i / 100; pts.push([x * r.a, Math.abs(x) < 1 ? r.p0 * Math.sqrt(1 - x * x) : 0]); }
    api.plot(50, 20, w * 0.48 - 60, h - 70, [{ pts, color: "#d62728" }], { ymin: 0, ymax: r.p0 * 1.15, xlabel: api.T("x / mm", "x / mm"), ylabel: api.T("压力 / MPa", "pressure / MPa") });
    for (let i = 0; i <= 100; i++) { const z = 3 * i / 100; sub.push([sub8_9(z)[2] * r.p0, -z * r.a]); }
    api.plot(w * 0.52 + 20, 20, w * 0.48 - 50, h - 70, [{ pts: sub, color: "#1f77b4" }],
      { xmin: 0, xmax: r.p0 * 0.35, ymin: -3 * r.a, ymax: 0, xlabel: api.T("τ1 / MPa", "τ1 / MPa"), ylabel: api.T("深度（向下）", "depth (down)") });
  },
});
