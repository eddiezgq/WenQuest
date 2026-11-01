// 实验 17.4 UR5e 上臂的质心与转动惯量（配 17.3、17.4 节）。“机器人”场景：把 UR5e 上臂（肩关节到肘关节 0.425 m）
// 建成“均匀实心圆柱”（零件库模型的做法）或“铝管 + 两端关节模块”，算质量、质心、绕质心与绕肩关节轴的转动惯量，
// 与零件库模型（MuJoCo Menagerie：8.393 kg，质心 0.2125 m，I = 0.133886 kg·m²）和厂家手册（8.058 kg）比对；
// “变密度杆”场景：线密度 λ(x) = λ₀(1 + kx/L)，看质心与转动惯量怎样随 k 变化。
WQ.lab({
  title: ["实验 17.4 UR5e 上臂的质心与转动惯量", "Lab 17.4 Centre of mass and inertia of the UR5e upper arm"],
  goal: ["用积分计算一节真实连杆的质量、质心和转动惯量，理解零件库模型的参数是怎样来的、它做了什么近似；用平行轴定理看清“绕质心”和“绕关节轴”的差别，以及质量分布对转动惯量的影响。",
         "Compute the mass, centre of mass and inertia of a real link by integration; see how the part-library parameters were obtained and what they approximate; use the parallel-axis theorem to separate inertia about the centre of mass from inertia about the joint, and see how the mass distribution matters."],
  scenes: [
    { id: "arm", robot: true, name: ["UR5e 上臂", "UR5e upper arm"], hide: ["k"],
      problem: { title: ["机器人问题：零件库里上臂的转动惯量是怎么来的？可信吗？", "Robot problem: where does the library's inertia for the upper arm come from, and can we trust it?"],
                 text: ["零件库的 UR5e 模型给出上臂质量 8.393 kg、质心在两关节正中 0.2125 m 处、绕质心的转动惯量 0.133886 kg·m²；厂家官网给的质量是 8.058 kg。真实的上臂是一根铝管，两端各有一个沉重的关节模块（电机、减速器、编码器）。把它建成不同的模型，看转动惯量差多少。",
                        "The library's UR5e model gives the upper arm a mass of 8.393 kg, its centre of mass midway at 0.2125 m, and an inertia of 0.133886 kg·m² about the centre of mass; the vendor's website gives 8.058 kg. The real upper arm is an aluminium tube with a heavy joint module (motor, gearbox, encoder) at each end. Build different models and compare the inertia."] } },
    { id: "rod", name: ["变密度杆", "Rod of varying density"], hide: ["model", "r", "ro", "t", "m1", "m2"],
      problem: { title: ["线密度不均匀时，质心和转动惯量怎样变？", "How do the centre of mass and inertia change with non-uniform density?"],
                 text: ["杆长 L，线密度 λ(x) = λ₀(1 + kx/L)，总质量保持 1 kg。k > 0 时末端重，k < 0 时根部重。",
                        "A rod of length L with linear density λ(x) = λ₀(1 + kx/L), total mass kept at 1 kg. k > 0 makes the tip heavier, k < 0 the root."] } },
  ],
  params: [
    { id: "model", name: ["模型：1 均匀实心圆柱，2 铝管 + 两端关节模块", "Model: 1 uniform solid cylinder, 2 aluminium tube + joint modules"], min: 1, max: 2, step: 1, value: 1, digits: 0 },
    { id: "r", name: ["实心圆柱半径（模型 1，总质量取 8.393 kg）", "Solid cylinder radius (model 1, mass 8.393 kg)"], min: 20, max: 100, step: 1, value: 40, unit: "mm", digits: 0 },
    { id: "ro", name: ["铝管外半径（模型 2）", "Tube outer radius (model 2)"], min: 25, max: 70, step: 1, value: 45, unit: "mm", digits: 0 },
    { id: "t", name: ["铝管壁厚（模型 2）", "Tube wall (model 2)"], min: 1, max: 10, step: 0.5, value: 4, unit: "mm", digits: 1 },
    { id: "m1", name: ["肩端关节模块质量（模型 2）", "Shoulder-end module mass (model 2)"], min: 0, max: 6, step: 0.05, value: 3, unit: "kg", digits: 2 },
    { id: "m2", name: ["肘端关节模块质量（模型 2）", "Elbow-end module mass (model 2)"], min: 0, max: 6, step: 0.05, value: 3, unit: "kg", digits: 2 },
    { id: "k", name: ["线密度变化 k", "Density slope k"], min: -0.9, max: 3, step: 0.05, value: 0, digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["铝管 / 实心圆柱 / 杆", "tube / solid cylinder / rod"], color: "#1f77b4" }, { name: ["关节模块", "joint modules"], color: "#b8860b" }, { name: ["质心", "centre of mass"], color: "#d62728" }],
  tasks: [
    { id: "lib", robot: true, text: ["模型 1：实心圆柱的半径取多少，绕质心的转动惯量才与零件库的 0.133886 kg·m² 一致？（零件库正是这样算的。）", "Model 1: what radius makes the inertia about the centre of mass equal the library's 0.133886 kg·m²? (That is how the library computed it.)"],
      demo: { scene: "arm", set: { model: 1, r: 60 }, wait: 1 } },
    { id: "match", robot: true, text: ["模型 2：调整铝管和两个关节模块，使总质量与零件库的 8.393 kg 相差不到 1%，质心在 0.2125 m ± 2 mm。", "Model 2: adjust the tube and modules so the mass is within 1% of 8.393 kg and the centre of mass at 0.2125 m ± 2 mm."],
      demo: { scene: "arm", set: { model: 2, ro: 45, t: 4, m1: 3.55, m2: 3.55 }, wait: 1 } },
    { id: "ratio", robot: true, text: ["在任务 2 的模型 2 中，绕质心的转动惯量是零件库值的多少倍？为什么质量集中在两端时转动惯量更大？", "In the model of task 2, how many times the library value is the inertia about the centre of mass? Why does mass at the ends increase it?"],
      demo: { scene: "arm", set: { model: 2, ro: 45, t: 4, m1: 3.55, m2: 3.55 }, wait: 1 } },
    { id: "rod", text: ["变密度杆：k 取多少，质心恰在 0.4L 处？此时绕根部的转动惯量是均匀杆的多少倍？", "Varying-density rod: which k puts the centre of mass at 0.4L? How does the inertia about the root compare with the uniform rod?"],
      demo: { scene: "rod", set: { k: -0.75 }, wait: 1 } },
  ],
  think: ["电机转子的转动惯量很小（约 10⁻⁴ kg·m²），但经过减速比 N = 101 的减速器折算到关节，要乘以 N²。与上臂绕肩关节轴的转动惯量相比，哪个大？这对控制器的设计意味着什么？",
          "A motor rotor's inertia is tiny (about 10⁻⁴ kg·m²), but through a gearbox of ratio N = 101 it appears at the joint multiplied by N². Which is larger, this or the upper arm's inertia about the shoulder? What does that mean for the controller?"],

  L: 0.425, RHO: 2700, RM: 0.06, M_LIB: 8.393, I_LIB: 0.133886, M_UR: 8.058,
  arm(p) {   // 返回 {M, xc, Ish, Icm, parts}
    const L = this.L;
    if (p.model === 1) {
      const M = this.M_LIB, r = p.r / 1000;
      const Icm = M * (3 * r * r + L * L) / 12;
      return { M, xc: L / 2, Icm, Ish: Icm + M * (L / 2) ** 2, mt: M };
    }
    const ro = p.ro / 1000, ri = Math.max(ro - p.t / 1000, 0), lam = this.RHO * Math.PI * (ro * ro - ri * ri), mt = lam * L;
    const M = mt + p.m1 + p.m2, xc = (mt * L / 2 + p.m2 * L) / M, rm = this.RM;
    const Ish = lam * L ** 3 / 3 + mt * (ro * ro + ri * ri) / 4 + 0.5 * p.m1 * rm * rm + p.m2 * (L * L + 0.5 * rm * rm);
    return { M, xc, Icm: Ish - M * xc * xc, Ish, mt };
  },
  rod(k) {   // L = 1、M = 1：λ = (1 + kx)/(1 + k/2)
    const c = 1 + k / 2;
    return { xc: (0.5 + k / 3) / c, Iroot: (1 / 3 + k / 4) / c };
  },
  reset() {},
  readouts(api) {
    const p = api.p;
    if (api.scene === "arm") {
      const A = this.arm(p), ratio = A.Icm / this.I_LIB;
      if (p.model === 1 && Math.abs(A.Icm - this.I_LIB) < 0.0005) api.done("lib");
      const ok = p.model === 2 && Math.abs(A.M - this.M_LIB) / this.M_LIB < 0.01 && Math.abs(A.xc - 0.2125) < 0.002;
      if (ok) { api.done("match"); if (ratio > 1.3) api.done("ratio"); }
      return [[["质量（零件库 8.393，厂家 8.058）", "Mass (library 8.393, vendor 8.058)"], A.M.toFixed(3) + " kg"],
              [["其中铝管 / 圆柱", "of which tube / cylinder"], A.mt.toFixed(3) + " kg"],
              [["质心到肩关节（零件库 0.2125）", "CM from shoulder (library 0.2125)"], A.xc.toFixed(4) + " m"],
              [["绕质心 I_cm（零件库 0.133886）", "I about CM (library 0.133886)"], A.Icm.toFixed(5) + " kg·m²"],
              [["与零件库之比", "ratio to library"], ratio.toFixed(3)],
              [["平行轴项 M·x̄²", "parallel-axis term M·x̄²"], (A.M * A.xc * A.xc).toFixed(4) + " kg·m²"],
              [["绕肩关节轴 I", "I about the shoulder"], A.Ish.toFixed(4) + " kg·m²"],
              [["水平时的重力矩 M g x̄", "gravity torque when horizontal M g x̄"], (A.M * 9.81 * A.xc).toFixed(2) + " N·m"]];
    }
    const R = this.rod(p.k);
    if (Math.abs(R.xc - 0.4) < 0.003) api.done("rod");
    return [[["质心 x̄ / L", "x̄ / L"], R.xc.toFixed(4)], [["绕根部 I / (mL²)", "I about the root / (mL²)"], R.Iroot.toFixed(4)],
            [["均匀杆 1/3 的倍数", "times the uniform 1/3"], (R.Iroot * 3).toFixed(3)],
            [["绕质心 I / (mL²)", "I about CM / (mL²)"], (R.Iroot - R.xc * R.xc).toFixed(4)]];
  },
  draw(api) {
    const w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), amber = api.css("--amber") || "#b8860b", muted = api.css("--muted"), ink = api.css("--ink");
    const p = api.p;
    if (api.scene === "arm") {
      const A = this.arm(p), L = this.L;
      const ys = 0.325 * (h - 74) / (w - 90);
      const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: -0.1, xmax: 0.55, ymin: -ys, ymax: ys, xlabel: "x / m", ylabel: "" });
      G.axes();
      const box = (x0, x1, y0, y1, c, wd) => G.pts([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]], c, wd || 2);
      if (p.model === 1) {
        const r = p.r / 1000;
        box(0, L, -r, r, blue, 2.5);
      } else {
        const ro = p.ro / 1000, ri = Math.max(ro - p.t / 1000, 0);
        box(0, L, -ro, ro, blue, 2.5);
        box(0, L, -ri, ri, blue, 1);
        const rm = this.RM;
        for (const [x, m] of [[0, p.m1], [L, p.m2]]) {
          const pts = [];
          for (let i = 0; i <= 60; i++) { const a = 2 * Math.PI * i / 60; pts.push([x + rm * Math.cos(a), rm * Math.sin(a)]); }
          G.pts(pts, amber, 1 + m);
        }
      }
      G.point(0, 0, ink, api.T("肩", "shoulder"), -10, 22);
      G.point(L, 0, ink, api.T("肘", "elbow"), -6, 22);
      G.vline(A.xc, red, [5, 4]);
      G.point(A.xc, 0, red, api.T("质心", "CM"));
      G.vline(0.2125, muted, [2, 4]);
      return;
    }
    const k = p.k, c = 1 + k / 2, R = this.rod(k);
    const G = api.graph({ x: 70, y: 24, w: w - 90, h: h - 74, xmin: 0, xmax: 1, ymin: 0, ymax: 2.2, xlabel: "x / L", ylabel: api.T("线密度 λ / (m/L)", "density λ / (m/L)") });
    G.axes();
    G.area((x) => (1 + k * x) / c, 0, 1, "rgba(31,119,180,0.25)");
    G.fn((x) => (1 + k * x) / c, blue, 2.5);
    G.vline(R.xc, red, [5, 4]);
    G.point(R.xc, 0.1, red, api.T("质心", "CM"));
    G.vline(0.5, muted, [2, 4]);
  },
});
