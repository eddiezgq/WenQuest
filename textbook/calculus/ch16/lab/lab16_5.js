// 实验 16.5 机器人外壳的体积与表面积（配 16.2、16.3、16.5 节）。“机器人”场景：圆柱 + 半椭球顶 + 平底的服务机器人外壳，
// 由轮廓线绕竖直轴旋转而成，计算体积、表面积、壳体质量和喷涂用漆量，并与零件库中三角网格模型（圆周分成 N 份）的数值比对；
// “切片”场景：用 n 个圆盘（每片取中点处的半径）的体积之和逼近外壳体积，看误差怎样随 n 减小。
WQ.lab({
  title: ["实验 16.5 机器人外壳的体积与表面积", "Lab 16.5 Volume and surface area of a robot housing"],
  goal: ["用旋转体的体积公式和旋转曲面的面积公式计算外壳的体积、表面积、质量和用漆量，理解零件库网格模型为什么偏小，以及怎样选择网格的细密程度；再用切片求和体会“体积 = 截面积的积分”。",
         "Use the formulas for solids and surfaces of revolution to compute a housing's volume, area, mass and paint; see why part-library mesh models come out small and how fine the mesh must be; then approximate the volume by slices to see volume as the integral of cross-sectional area."],
  scenes: [
    { id: "housing", robot: true, name: ["服务机器人外壳", "Service-robot housing"], hide: ["n"],
      problem: { title: ["机器人问题：外壳有多大、多重、要多少漆？", "Robot problem: how big and heavy is the housing, and how much paint does it need?"],
                 text: ["服务机器人的外壳是一个圆柱加一个半椭球形的顶，底部是平的。轮廓线绕竖直轴旋转一周就得到外壳。设计时要知道它装得下多少设备（体积）、外壳多重（表面积 × 壁厚 × 密度）、喷涂要多少漆。零件库里的三维模型是三角网格，它的体积和面积与公式算的不完全一样。",
                        "A service robot's housing is a cylinder with a half-ellipsoid top and a flat bottom, obtained by revolving its profile about the vertical axis. The designer needs its volume (what fits inside), its mass (area × wall thickness × density) and the paint it needs. Part-library 3D models are triangle meshes whose volume and area differ slightly from the formulas."] } },
    { id: "slices", name: ["切片求体积", "Volume by slices"], hide: ["t", "N"],
      problem: { title: ["把外壳切成 n 片，体积之和逼近多快？", "Slice the housing into n disks: how fast does the sum converge?"],
                 text: ["每一片近似为一个圆盘，半径取这一片中点高度处轮廓的半径。n 片圆盘的体积之和是 ∫πr(z)²dz 的中点和。",
                        "Each slice is approximated by a disk whose radius is the profile radius at the slice's mid-height. The sum of n disk volumes is the midpoint sum of ∫πr(z)²dz."] } },
  ],
  params: [
    { id: "R", name: ["半径 R", "Radius R"], min: 50, max: 300, step: 1, value: 150, unit: "mm", digits: 0 },
    { id: "H", name: ["圆柱段高度 H", "Cylinder height H"], min: 0, max: 800, step: 1, value: 400, unit: "mm", digits: 0 },
    { id: "c", name: ["顶的高度 c（0 为平顶，c = R 为半球）", "Top height c (0 flat, c = R hemisphere)"], min: 0, max: 300, step: 1, value: 100, unit: "mm", digits: 0 },
    { id: "t", name: ["壁厚（ABS，1.05 g/cm³）", "Wall thickness (ABS, 1.05 g/cm³)"], min: 1, max: 5, step: 0.1, value: 2.5, unit: "mm", digits: 1 },
    { id: "N", name: ["网格模型的圆周分段数 N", "Mesh segments around the circle N"], min: 6, max: 360, step: 2, value: 24, digits: 0 },
    { id: "n", name: ["切片数 n", "Number of slices n"], min: 2, max: 200, step: 1, value: 8, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["轮廓（公式）", "profile (formula)"], color: "#1f77b4" }, { name: ["网格模型 / 切片", "mesh model / slices"], color: "#d62728" }],
  tasks: [
    { id: "mesh", robot: true, text: ["默认外壳（R = 150 mm，H = 400 mm，c = 100 mm）：网格模型的圆周至少分多少段，体积偏差才小于 0.1%？", "Default housing (R = 150 mm, H = 400 mm, c = 100 mm): how many segments must the mesh have for a volume error below 0.1%?"],
      demo: { scene: "housing", set: { R: 150, H: 400, c: 100, N: 82 }, wait: 1 } },
    { id: "hemi", robot: true, text: ["把顶改成半球（c = R）：顶的面积是多少？与 2πR² 比较。", "Make the top a hemisphere (c = R): what is its area? Compare with 2πR²."],
      demo: { scene: "housing", set: { R: 150, c: 150 }, wait: 1 } },
    { id: "opt", robot: true, text: ["半球顶、平底，要装下 30 L（体积 30～30.6 L）：怎样选 R 和 H，外表面积最小？（提示：最优时 H 与 R 有简单的关系。）", "Hemispherical top, flat bottom, volume 30–30.6 L: choose R and H to minimize the outer area. (Hint: at the optimum H and R are simply related.)"],
      demo: { scene: "housing", set: { R: 179, H: 179, c: 179 }, wait: 1 } },
    { id: "slice", text: ["切片场景：默认外壳至少切多少片，体积误差小于 0.1%？", "Slices: how many slices make the volume error of the default housing below 0.1%?"],
      demo: { scene: "slices", set: { R: 150, H: 400, c: 100, n: 21 }, wait: 1 } },
  ],
  think: ["这个外壳的网格模型体积为什么偏小？如果网格的顶点不在曲面上、而是让每个小平面与曲面相切（外切），结果会怎样？3D 打印时，这种偏差会造成什么后果？",
          "Why is the housing's mesh volume too small? What if each facet were tangent to the surface (circumscribed) instead of having its vertices on it? What would the deviation mean for 3D printing?"],

  r(z, p) {   // 轮廓半径（mm）
    if (z < 0 || z > p.H + p.c) return 0;
    if (z <= p.H) return p.R;
    const u = (z - p.H) / p.c;
    return p.R * Math.sqrt(Math.max(1 - u * u, 0));
  },
  calc(p) {
    const R = p.R, H = p.H, c = p.c, PI = Math.PI;
    const V = PI * R * R * H + 2 / 3 * PI * R * R * c;
    const side = 2 * PI * R * H, bottom = PI * R * R;
    let dome = PI * R * R;
    if (c > 0) dome = this.simp((s) => 2 * PI * R * Math.cos(s) * Math.sqrt((R * Math.sin(s)) ** 2 + (c * Math.cos(s)) ** 2), 0, PI / 2, 400);
    const S = side + dome + bottom;
    return { V, side, dome, bottom, S };
  },
  simp(f, a, b, n) { const h = (b - a) / n; let s = f(a) + f(b); for (let k = 1; k < n; k++) s += (k % 2 ? 4 : 2) * f(a + k * h); return s * h / 3; },
  sopt(V) { const Rs = Math.cbrt(3 * V / (5 * Math.PI)); return 2 * V / Rs + 5 / 3 * Math.PI * Rs * Rs; },
  slicesum(p, n) {
    const L = p.H + p.c, dz = L / n;
    let s = 0;
    for (let k = 0; k < n; k++) { const r = this.r((k + 0.5) * dz, p); s += Math.PI * r * r * dz; }
    return s;
  },
  reset() {},
  readouts(api) {
    const p = api.p, C = this.calc(p);
    if (api.scene === "housing") {
      const N = p.N, fv = N * Math.sin(2 * Math.PI / N) / (2 * Math.PI), fa = N * Math.sin(Math.PI / N) / Math.PI;
      const Vm = fv * C.V, Sm = fa * (C.side + C.dome) + fv * C.bottom, St = C.side + C.dome, Stm = fa * St;
      const dV = (Vm - C.V) / C.V * 100, dS = (Stm - St) / St * 100;
      const def = p.R === 150 && p.H === 400 && p.c === 100;
      if (def && Math.abs(dV) < 0.1) api.done("mesh");
      if (p.c === p.R) api.done("hemi");
      const VL = C.V / 1e6;
      if (p.c === p.R && VL >= 30 && VL <= 30.6 && C.S <= 1.002 * this.sopt(C.V) && Math.abs(p.H / p.R - 1) < 0.05) api.done("opt");
      const mass = (C.side + C.dome) * p.t * 1.05e-3 / 1000, paint = (C.side + C.dome) * 0.030 / 0.5 / 1000;
      return [[["体积", "Volume"], VL.toFixed(2) + " L"], [["表面积（侧 + 顶 + 底）", "Area (side + top + bottom)"], (C.S / 1e6).toFixed(4) + " m²"],
              [["其中顶", "of which the top"], (C.dome / 1e6).toFixed(4) + " m²"], [["2πR²（半球面）", "2πR² (hemisphere)"], (2 * Math.PI * p.R * p.R / 1e6).toFixed(4) + " m²"],
              [["壳体质量（侧 + 顶）", "Shell mass (side + top)"], mass.toFixed(3) + " kg"], [["用漆量（干膜 30 μm）", "Paint (30 μm dry film)"], paint.toFixed(1) + " mL"],
              [["网格模型体积偏差", "Mesh volume deviation"], dV.toFixed(3) + " %"], [["网格模型面积偏差（侧 + 顶）", "Mesh area deviation (side + top)"], dS.toFixed(3) + " %"]];
    }
    const Vs = this.slicesum(p, p.n), err = (Vs - C.V) / C.V * 100;
    if (p.R === 150 && p.H === 400 && p.c === 100 && Math.abs(err) < 0.1) api.done("slice");
    return [[["准确体积", "Exact volume"], (C.V / 1e6).toFixed(4) + " L"], [["n 片圆盘之和", "Sum of n disks"], (Vs / 1e6).toFixed(4) + " L"],
            [["相对误差", "Relative error"], err.toFixed(3) + " %"], [["误差 × n²", "Error × n²"], (err * p.n * p.n).toFixed(1)]];
  },
  draw(api) {
    const w = api.w, h = api.h, blue = api.css("--blue"), red = api.css("--red"), muted = api.css("--muted"), ink = api.css("--ink");
    const p = api.p, gw = w - 90, gh = h - 74, top = p.H + p.c;
    const zspan = Math.max(top + 60, 400), xspan = zspan * gw / gh;
    const G = api.graph({ x: 70, y: 24, w: gw, h: gh, xmin: -xspan / 2, xmax: xspan / 2, ymin: -30, ymax: zspan - 30, xlabel: "x / mm", ylabel: "z / mm" });
    G.axes();
    G.vline(0, muted);
    const prof = [];
    for (let i = 0; i <= 200; i++) { const z = top * i / 200; prof.push([this.r(z, p), z]); }
    prof.push([0, top]);
    if (api.scene === "slices") {
      const dz = top / p.n;
      for (let k = 0; k < p.n; k++) {
        const r = this.r((k + 0.5) * dz, p), z0 = k * dz, z1 = (k + 1) * dz;
        G.pts([[-r, z0], [r, z0], [r, z1], [-r, z1], [-r, z0]], red, 1.2);
      }
    }
    G.pts([[0, 0]].concat(prof.map(([r, z]) => [r, z])), blue, 2.5);
    G.pts([[0, 0]].concat(prof.map(([r, z]) => [-r, z])), blue, 2.5);
    G.seg(-p.R, 0, p.R, 0, blue, 2.5);
    if (api.scene === "housing") {
      // 俯视：圆与内接 N 边形（放在外壳上方右侧）
      const s = Math.min(0.55, 0.42 * (xspan / 2 - p.R) / p.R + 0.2), cx = xspan / 2 - p.R * s - 20, cz = zspan - 30 - p.R * s - 20;
      const circ = [], poly = [];
      for (let i = 0; i <= 120; i++) { const a = 2 * Math.PI * i / 120; circ.push([cx + s * p.R * Math.cos(a), cz + s * p.R * Math.sin(a)]); }
      for (let i = 0; i <= p.N; i++) { const a = 2 * Math.PI * i / p.N; poly.push([cx + s * p.R * Math.cos(a), cz + s * p.R * Math.sin(a)]); }
      G.pts(circ, blue, 1.5);
      G.pts(poly, red, 1.5);
      G.text(api.T("俯视：圆与网格的 N 边形", "top view: circle vs N-gon"), cx, cz - s * p.R - 18, ink, 11, "center");
    }
  },
});
