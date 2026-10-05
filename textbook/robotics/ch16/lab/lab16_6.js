// 实验 16.6 灵巧性指标（配 16.6 节）。二维实验。
// 场景 1（机器人）：UR5e 法兰盘竖直朝下（保持 θ* 的姿态），中心在过 θ* 的竖直半平面内，(ρ, z) 由滑块给出。
//   逆解用 16.6 节的闭式解（_jac.ur_down）：θ5 = −90°、θ4 = −90° − θ2 − θ3、θ6 = θ1 + 15°，
//   X − H2 = −√(ρ² − d4²)，(θ2 + π, θ3) 是平面 2R 臂到达 (X, z + W4 − H1) 的解（θ3 > 0）。
//   颜色是姿态保持的线速度椭球（定理 16.4.2）的局部条件指标 LCI = 1/κ；黑线是手臂在 (ρ, z) 平面内的投影，
//   橙色是椭球在这个平面内的截面。
// 场景 2：平面 2R 臂的设计。总长 0.817 m，长度比 λ = L2/L1 与肘角 θ2 可调；右侧画出 κ(θ2) 和全局条件指标 GCI(λ)
//   （GCI = ∫ LCI |sin θ2| dθ2 / ∫ |sin θ2| dθ2，辛普森积分）。
// 场景 3（生活）：俯视书桌，人的右臂（上臂 0.30 m、前臂到手 0.32 m）在桌面上方的水平面内转动，肩在原点；
//   颜色是手的 LCI；滑块把一个零件放到桌面上的 (x, y)。
WQ.lab({
  title: ["实验 16.6 灵巧性指标", "Lab 16.6 Dexterity indices"],
  goal: ["用局部条件指标画出“灵巧性地图”，为 UR5e 找最灵巧的工位；设计一台各向同性的 2R 臂；在书桌上找出手最灵巧的地方。",
         "Draw “dexterity maps” with the local conditioning index, find the most dexterous working place for the UR5e, design an isotropic 2R arm, and find where on a desk the hand is most dexterous."],
  scenes: [
    { id: "ur", robot: true, name: ["UR5e 的灵巧性地图", "Dexterity map of the UR5e"], hide: ["lam", "th2", "dx", "dy"],
      problem: { title: ["机器人问题：工具竖直朝下，工位放在哪里最灵巧", "Robot problem: tool pointing down, which working place is most dexterous"],
                 text: ["颜色是姿态保持时法兰盘中心线速度椭球的 1/κ（越亮越接近各向同性）。拖动 ρ、z 选择位置，黑线是手臂，橙色是椭球的截面。",
                        "The colour is 1/κ of the flange-centre velocity ellipsoid with the orientation held (brighter = closer to isotropic). Drag ρ and z to choose a place; the black line is the arm and orange the section of the ellipsoid."] } },
    { id: "design", name: ["设计 2R 臂", "Designing a 2R arm"], hide: ["rho", "zh", "dx", "dy"],
      problem: { title: ["设计问题：总长一定，两段臂怎样分配", "Design problem: for a fixed total length, how to split the two links"],
                 text: ["调节长度比 λ = L₂/L₁ 和肘角 θ₂。左边是手臂与速度椭圆，右上是 κ 随 θ₂ 的变化，右下是全局条件指标 GCI 随 λ 的变化。",
                        "Set the length ratio λ = L₂/L₁ and the elbow angle θ₂. Left: the arm and its velocity ellipse; top right: κ against θ₂; bottom right: the global conditioning index GCI against λ."] } },
    { id: "desk", name: ["书桌上的灵巧区", "The dexterous area on a desk"], hide: ["rho", "zh", "lam", "th2"],
      problem: { title: ["生活中的例子：常用的东西放在桌上哪里", "Everyday example: where on the desk to keep things you use often"],
                 text: ["俯视书桌，右肩在原点。颜色是手的 1/κ。拖动 x、y 把零件放到桌面上，手臂自动伸过去。",
                        "Desk seen from above, right shoulder at the origin. The colour is 1/κ of the hand. Drag x and y to put a part on the desk; the arm reaches for it."] } },
  ],
  params: [
    { id: "rho", name: ["水平距离 ρ", "horizontal distance ρ"], min: 0.14, max: 0.95, step: 0.005, value: 0.665, unit: "m", digits: 3 },
    { id: "zh", name: ["高度 z", "height z"], min: -0.45, max: 0.95, step: 0.005, value: 0.235, unit: "m", digits: 3 },
    { id: "lam", name: ["长度比 λ = L₂/L₁", "length ratio λ = L₂/L₁"], min: 0.3, max: 1.5, step: 0.005, value: 0.92, unit: "", digits: 3 },
    { id: "th2", name: ["肘角 θ₂", "elbow angle θ₂"], min: 5, max: 175, step: 1, value: 60, unit: "°", digits: 0 },
    { id: "dx", name: ["零件位置 x（向右）", "part position x (to the right)"], min: -0.3, max: 0.62, step: 0.01, value: 0.4, unit: "m", digits: 2 },
    { id: "dy", name: ["零件位置 y（向前）", "part position y (forward)"], min: -0.1, max: 0.62, step: 0.01, value: 0.45, unit: "m", digits: 2 },
  ],
  legend: [{ color: "#fde725", name: ["1/κ 大（灵巧）", "large 1/κ (dexterous)"] }, { color: "#440154", name: ["1/κ 小（接近奇异）", "small 1/κ (near singular)"] }],
  tasks: [
    { id: "star", robot: true, text: ["把法兰盘放回 θ*（ρ = 0.665 m、z = 0.235 m），读出那里的 1/κ。", "Put the flange back at θ* (ρ = 0.665 m, z = 0.235 m) and read its 1/κ."],
      demo: { scene: "ur", set: { rho: 0.665, zh: 0.235 }, press: [], wait: 3 } },
    { id: "best", robot: true, text: ["找出 UR5e 最灵巧的工位：1/κ 达到地图最大值的 97% 以上。", "Find the most dexterous place for the UR5e: 1/κ at least 97% of the map's maximum."],
      demo: { scene: "ur", set: { rho: 0.46, zh: 0.24 }, press: [], wait: 3 } },
    { id: "edge", robot: true, text: ["在 z = 0.235 m 的高度上把手臂伸到快够不着的地方，看到 1/κ 降到 0.06 以下。", "At the height z = 0.235 m, stretch the arm almost to the edge of its reach and see 1/κ fall below 0.06."],
      demo: { scene: "ur", set: { zh: 0.235, rho: 0.905 }, press: [], wait: 3 } },
    { id: "iso", text: ["设计一台各向同性的 2R 臂：找到 κ < 1.01 的长度比和肘角。", "Design an isotropic 2R arm: find a length ratio and elbow angle with κ < 1.01."],
      demo: { scene: "design", set: { lam: 0.705, th2: 135 }, press: [], wait: 3 } },
    { id: "gci", text: ["找出使全局条件指标最大的长度比（达到最大值的 99.9% 以上）。", "Find the length ratio with the largest global conditioning index (within 0.1% of the maximum)."],
      demo: { scene: "design", set: { lam: 0.71, th2: 90 }, press: [], wait: 3 } },
    { id: "desk", text: ["生活场景：把零件放在手最灵巧的地方（1/κ ≥ 0.55）。", "Everyday scene: put the part where the hand is most dexterous (1/κ ≥ 0.55)."],
      demo: { scene: "desk", set: { dx: 0.1, dy: 0.24 }, press: [], wait: 3 } },
  ],
  think: ["UR5e 地图上最灵巧的地方，与 16.4 节姿态保持时可操作度最大的地方是否相同？挑工位时你更看重哪一个指标，为什么？",
          "Is the most dexterous place on the UR5e map the same as where the orientation-held manipulability peaks in Section 16.4? Which index would you weigh more when choosing a working place, and why?"],

  // ---------------- UR5e：闭式逆解、几何雅可比、姿态保持的椭球
  G: { H1: 0.163, W1: 0.138, L1: 0.425, W2: 0.131, L2: 0.392, W3: 0.127, H2: 0.1, W4: 0.1 },
  cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; },
  add(a, b) { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; },
  sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; },
  mv(R, v) { return [0, 1, 2].map((i) => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]); },
  mm(A, B) { return [0, 1, 2].map((i) => [0, 1, 2].map((j) => A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j])); },
  rot(w, t) {
    const c = Math.cos(t), s = Math.sin(t), v = 1 - c, [x, y, z] = w;
    return [[c + x * x * v, x * y * v - z * s, x * z * v + y * s], [y * x * v + z * s, c + y * y * v, y * z * v - x * s], [z * x * v - y * s, z * y * v + x * s, c + z * z * v]];
  },
  AX() {
    const g = this.G, Y = [0, -1, 0];
    return [[[0, 0, 1], [0, 0, g.H1]], [Y, [0, -g.W1, g.H1]], [Y, [-g.L1, -g.W1 + g.W2, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2, g.H1]],
            [[0, 0, -1], [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1]], [Y, [-g.L1 - g.L2, -g.W1 + g.W2 - g.W3, g.H1 - g.H2]]];
  },
  chain(th) {                                     // 各关节此刻的轴、法兰盘中心与连杆折线上的点
    const g = this.G, A = this.AX(), keep = [];
    let R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], p = [0, 0, 0];
    const axes = [];
    keep.push([R, p]);
    A.forEach(([w, q], i) => {
      axes.push([this.mv(R, w), this.add(this.mv(R, q), p)]);
      const Ri = this.rot(w, th[i]); p = this.add(this.mv(R, this.sub(q, this.mv(Ri, q))), p); R = this.mm(R, Ri); keep.push([R, p]);
    });
    const q = A.map((x) => x[1]);
    const pts = [[0, [0, 0, 0]], [0, q[0]], [1, q[1]], [2, this.add(q[1], [-g.L1, 0, 0])], [2, q[2]], [3, q[3]], [4, q[4]], [5, q[5]], [6, this.add(q[5], [0, -g.W4, 0])]]
      .map(([k, x]) => this.add(this.mv(keep[k][0], x), keep[k][1]));
    return { axes, p: pts[pts.length - 1], pts };
  },
  az: Math.atan2(-0.44203838, -0.49763294),       // θ* 处法兰盘中心的方位角（算例 16.1.2 的 p）
  down(rho, z) {
    const g = this.G, d4 = g.W1 - g.W2 + g.W3;
    if (rho < d4) return null;
    const r = -Math.sqrt(rho * rho - d4 * d4), X = r + g.H2, Zr = z + g.W4 - g.H1;
    const c = (X * X + Zr * Zr - g.L1 * g.L1 - g.L2 * g.L2) / (2 * g.L1 * g.L2);
    if (c > 1 || c < -1) return null;
    const t3 = Math.acos(c), t2p = Math.atan2(Zr, X) - Math.atan2(g.L2 * Math.sin(t3), g.L1 + g.L2 * Math.cos(t3));
    const t2 = t2p - Math.PI, t1 = this.az - Math.atan2(-d4, r);
    return [t1, t2, t3, -Math.PI / 2 - t2 - t3, -Math.PI / 2, t1 + Math.PI / 12];
  },
  solve(cols, b) {
    const n = b.length, M = [];
    for (let r = 0; r < n; r++) M.push([...cols.map((c) => c[r]), b[r]]);
    for (let i = 0; i < n; i++) {
      let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(M[j][i]) > Math.abs(M[p][i])) p = j;
      [M[i], M[p]] = [M[p], M[i]];
      for (let j = i + 1; j < n; j++) { const f = M[j][i] / M[i][i]; for (let k = i; k <= n; k++) M[j][k] -= f * M[i][k]; }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let s = M[i][n]; for (let k = i + 1; k < n; k++) s -= M[i][k] * x[k]; x[i] = s / M[i][i]; }
    return x;
  },
  held(api, th) {                                 // 姿态保持的线速度椭球：G = J_g⁻¹ 的后三列，半轴 1/s_i，方向 = G 的右奇异矢量
    const c = this.chain(th), cols = c.axes.map(([w, q]) => [...w, ...this.cross(w, this.sub(c.p, q))]);
    const G = [0, 1, 2, 3, 4, 5].map(() => [0, 0, 0]);
    for (let k = 0; k < 3; k++) { const e = [0, 0, 0, 0, 0, 0]; e[3 + k] = 1; this.solve(cols, e).forEach((v, i) => { G[i][k] = v; }); }
    const { s, V } = api.la.svd(G), a = s.map((x) => 1 / Math.max(x, 1e-12));
    const o = [0, 1, 2].sort((i, j) => a[j] - a[i]);
    return { a: o.map((i) => a[i]), D: o.map((i) => [V[0][i], V[1][i], V[2][i]]), c };
  },
  // ---------------- 2R 臂
  lci2(l1, l2, t2) {                              // 2R 臂的 1/κ：JᵀJ 的两个特征值
    const c = Math.cos(t2), a = l1 * l1 + l2 * l2 + 2 * l1 * l2 * c, b = l2 * l2 + l1 * l2 * c, d = l2 * l2;
    const tr = a + d, det = a * d - b * b, disc = Math.sqrt(Math.max(0, tr * tr / 4 - det));
    return Math.sqrt(Math.max(0, tr / 2 - disc) / (tr / 2 + disc));
  },
  gci(lam) {
    const l1 = 0.817 / (1 + lam), l2 = 0.817 - l1, n = 400, h = Math.PI / n;
    let num = 0, den = 0;
    for (let i = 0; i <= n; i++) { const t = i * h, w = (i === 0 || i === n) ? 1 : (i % 2 ? 4 : 2), s = Math.abs(Math.sin(t)); num += w * this.lci2(l1, l2, t) * s; den += w * s; }
    return num / den;
  },
  viridis(v) {                                    // 0…1 → 颜色（viridis 的五个节点线性插值）
    const P = [[68, 1, 84], [59, 82, 139], [33, 145, 140], [94, 201, 98], [253, 231, 37]];
    const x = Math.max(0, Math.min(1, v)) * 4, i = Math.min(3, Math.floor(x)), f = x - i;
    return P[i].map((c, k) => Math.round(c + f * (P[i + 1][k] - c)));
  },
  mapImage(f, nx, ny, vmax) {                     // f(i, j) → 0…1 或 null；做成一张小图，画时放大
    const cv = document.createElement("canvas"); cv.width = nx; cv.height = ny;
    const g = cv.getContext("2d"), im = g.createImageData(nx, ny);
    let best = 0;
    for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
      const v = f(i, j), k = 4 * ((ny - 1 - j) * nx + i);
      if (v == null) { im.data[k + 3] = 0; continue; }
      best = Math.max(best, v);
      const c = this.viridis(v / vmax); im.data[k] = c[0]; im.data[k + 1] = c[1]; im.data[k + 2] = c[2]; im.data[k + 3] = 255;
    }
    g.putImageData(im, 0, 0);
    return { cv, best };
  },

  reset(api, s) {
    if (api.scene === "ur") {
      if (!this._urMap) {
        const nx = 82, ny = 141;
        this._urMap = this.mapImage((i, j) => {
          const r = 0.14 + 0.81 * i / (nx - 1), z = -0.45 + 1.4 * j / (ny - 1), th = this.down(r, z);
          if (!th) return null; const e = this.held(api, th); return e.a[2] / e.a[0];
        }, nx, ny, 0.75);
      }
      s.th = this.down(api.p.rho, api.p.zh);
      if (s.th) { s.e = this.held(api, s.th); s.lci = s.e.a[2] / s.e.a[0]; s.w = s.e.a[0] * s.e.a[1] * s.e.a[2]; }
    } else if (api.scene === "design") {
      const lam = api.p.lam, l1 = 0.817 / (1 + lam), l2 = 0.817 - l1, t2 = api.p.th2 * Math.PI / 180;
      s.l1 = l1; s.l2 = l2; s.t2 = t2; s.lci = this.lci2(l1, l2, t2); s.g = this.gci(lam);
      if (!this._gmax) { let m = 0; for (let x = 0.3; x <= 1.5 + 1e-9; x += 0.005) m = Math.max(m, this.gci(x)); this._gmax = m; }
    } else {
      const l1 = 0.3, l2 = 0.32;
      if (!this._deskMap) {
        const nx = 92, ny = 72;
        this._deskMap = this.mapImage((i, j) => {
          const x = -0.3 + 0.92 * i / (nx - 1), y = -0.1 + 0.72 * j / (ny - 1), r2 = x * x + y * y, c = (r2 - l1 * l1 - l2 * l2) / (2 * l1 * l2);
          if (c > 1 || c < -1) return null; return this.lci2(l1, l2, Math.acos(c));
        }, nx, ny, 0.6);
      }
      const x = api.p.dx, y = api.p.dy, c = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2);
      s.ok = c <= 1 && c >= -1;
      if (s.ok) { s.t2 = -Math.acos(c); s.t1 = Math.atan2(y, x) - Math.atan2(l2 * Math.sin(s.t2), l1 + l2 * Math.cos(s.t2)); s.lci = this.lci2(l1, l2, s.t2); }
    }
  },
  readouts(api, s) {
    if (api.scene === "ur") {
      if (!s.th) return [[["状态", "status"], api.T("这个位置够不着", "this place is out of reach")]];
      if (Math.abs(api.p.rho - 0.6656) < 0.006 && Math.abs(api.p.zh - 0.2351) < 0.006) api.done("star");
      if (this._urMap && s.lci >= 0.97 * this._urMap.best) api.done("best");
      if (Math.abs(api.p.zh - 0.2351) < 0.006 && s.lci < 0.06) api.done("edge");
      return [[["1/κ（姿态保持）", "1/κ (orientation held)"], s.lci.toFixed(4)], [["地图上的最大值", "largest on the map"], this._urMap.best.toFixed(4)],
              [["三个半轴", "three semi-axes"], s.e.a.map((x) => x.toFixed(4)).join(", ") + " m"], [["可操作度 w", "manipulability w"], s.w.toFixed(5) + " m³"],
              [["θ₂, θ₃", "θ₂, θ₃"], (s.th[1] * 180 / Math.PI).toFixed(1) + "°, " + (s.th[2] * 180 / Math.PI).toFixed(1) + "°"]];
    }
    if (api.scene === "design") {
      if (1 / Math.max(s.lci, 1e-9) < 1.01) api.done("iso");
      if (s.g >= 0.999 * this._gmax) api.done("gci");
      return [[["L₁, L₂", "L₁, L₂"], s.l1.toFixed(4) + " m, " + s.l2.toFixed(4) + " m"], [["条件数 κ", "condition number κ"], (1 / Math.max(s.lci, 1e-9)).toFixed(4)],
              [["1/κ", "1/κ"], s.lci.toFixed(4)], [["全局条件指标 GCI", "global conditioning index GCI"], s.g.toFixed(5)],
              [["GCI 的最大值（λ 网格）", "largest GCI (λ grid)"], this._gmax.toFixed(5)]];
    }
    if (!s.ok) return [[["状态", "status"], api.T("手够不着这里", "the hand cannot reach here")]];
    if (s.lci >= 0.55) api.done("desk");
    return [[["零件位置", "part position"], "(" + api.p.dx.toFixed(2) + ", " + api.p.dy.toFixed(2) + ") m"],
            [["肘部弯曲角", "elbow bend"], Math.abs(s.t2 * 180 / Math.PI).toFixed(1) + "°"], [["1/κ", "1/κ"], s.lci.toFixed(4)],
            [["灵巧区（1/κ ≥ 0.55）", "dexterous area (1/κ ≥ 0.55)"], s.lci >= 0.55 ? api.T("是", "yes") : api.T("否", "no")]];
  },

  // ---------------- 二维画面
  draw(api, s) {
    const ctx = api.ctx, W = api.w, H = api.h, ink = api.css("--ink"), mu = api.css("--muted");
    if (api.scene === "ur") {
      const sc = Math.min(W * 0.62 / 1.0, H * 0.86 / 1.5), ox = 50, oy = H * 0.07 + 0.95 * sc;
      const X = (r) => ox + r * sc, Y = (z) => oy - z * sc;
      if (this._urMap) { ctx.save(); ctx.imageSmoothingEnabled = true; ctx.drawImage(this._urMap.cv, X(0.14), Y(0.95), 0.81 * sc, 1.4 * sc); ctx.restore(); }
      api.line(X(0), Y(0), X(1.0), Y(0), mu, 1); api.line(X(0), Y(-0.45), X(0), Y(0.95), mu, 1);
      api.line(X(0.134), Y(-0.45), X(0.134), Y(0.95), "#ffffff", 1, [4, 4]);
      api.label("ρ = d₄", X(0.134) + 4, Y(0.9), "#ffffff", 11);
      [0.2, 0.4, 0.6, 0.8].forEach((r) => api.label(r.toFixed(1), X(r), Y(-0.45) + 12, mu, 11, "center"));
      [-0.4, 0, 0.4, 0.8].forEach((z) => api.label(z.toFixed(1), X(0) - 6, Y(z), mu, 11, "right"));
      api.label("ρ / m", X(0.95), Y(-0.45) + 26, mu, 12, "right"); api.label("z / m", X(0) + 4, Y(0.95) - 10, mu, 12);
      const p0 = [-0.49763294, -0.44203838], er = [p0[0] / Math.hypot(...p0), p0[1] / Math.hypot(...p0)];
      api.circle(X(Math.hypot(...p0)), Y(0.23506), 4, "#d62728");
      api.label("θ*", X(Math.hypot(...p0)) + 6, Y(0.23506) - 10, "#ffffff", 12);
      if (s.th) {
        const P = s.e.c.pts.map((p) => [p[0] * er[0] + p[1] * er[1], p[2]]);
        ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 6; ctx.lineCap = "round"; ctx.beginPath(); P.forEach((p, i) => (i ? ctx.lineTo(X(p[0]), Y(p[1])) : ctx.moveTo(X(p[0]), Y(p[1])))); ctx.stroke();
        ctx.strokeStyle = "#1d2327"; ctx.lineWidth = 3; ctx.stroke();
        // 椭球在 (e_r, z) 平面内的截面：xᵀ M x ≤ 1，M = D diag(1/a²) Dᵀ
        const D = s.e.D, a = s.e.a, B = [[er[0], er[1], 0], [0, 0, 1]];
        const Mq = (u, v) => [0, 1, 2].reduce((t, k) => { const du = D[k][0] * u[0] + D[k][1] * u[1] + D[k][2] * u[2], dv = D[k][0] * v[0] + D[k][1] * v[1] + D[k][2] * v[2]; return t + du * dv / (a[k] * a[k]); }, 0);
        const m11 = Mq(B[0], B[0]), m12 = Mq(B[0], B[1]), m22 = Mq(B[1], B[1]);
        const c = [api.p.rho, api.p.zh], pts = [];
        for (let k = 0; k <= 72; k++) {
          const t = k * Math.PI / 36, u = [Math.cos(t), Math.sin(t)], q = m11 * u[0] * u[0] + 2 * m12 * u[0] * u[1] + m22 * u[1] * u[1], r = 0.25 / Math.sqrt(q);
          pts.push([c[0] + r * u[0], c[1] + r * u[1]]);
        }
        ctx.strokeStyle = "#e8912d"; ctx.lineWidth = 2.5; ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(X(p[0]), Y(p[1])) : ctx.moveTo(X(p[0]), Y(p[1])))); ctx.stroke();
      }
      // 色标
      const bx = W - 70, by = H * 0.12, bh = H * 0.6;
      for (let k = 0; k < 60; k++) { const c = this.viridis(1 - k / 59); api.rect(bx, by + k * bh / 60, 18, bh / 60 + 1, `rgb(${c[0]},${c[1]},${c[2]})`); }
      api.label("0.75", bx + 22, by, mu, 11); api.label("0", bx + 22, by + bh, mu, 11); api.label("1/κ", bx - 2, by - 14, mu, 12);
      return;
    }
    if (api.scene === "design") {
      const sc = Math.min(W * 0.45, H * 0.8) / 0.9, ox = W * 0.14, oy = H * 0.78;
      const t1 = 0.35, e = [s.l1 * Math.cos(t1), s.l1 * Math.sin(t1)], p = [e[0] + s.l2 * Math.cos(t1 + s.t2), e[1] + s.l2 * Math.sin(t1 + s.t2)];
      const P = (q) => [ox + q[0] * sc, oy - q[1] * sc];
      api.line(...P([0, 0]), ...P(e), api.css("--accent"), 10); api.line(...P(e), ...P(p), api.css("--accent"), 8);
      api.circle(...P([0, 0]), 6, api.css("--panel"), ink); api.circle(...P(e), 5, api.css("--panel"), ink);
      // 速度椭圆：J Jᵀ 的特征分解，比例 0.45
      const a1 = t1, a2 = t1 + s.t2, J = [[-s.l1 * Math.sin(a1) - s.l2 * Math.sin(a2), -s.l2 * Math.sin(a2)], [s.l1 * Math.cos(a1) + s.l2 * Math.cos(a2), s.l2 * Math.cos(a2)]];
      const A = [[J[0][0] ** 2 + J[0][1] ** 2, J[0][0] * J[1][0] + J[0][1] * J[1][1]], [0, J[1][0] ** 2 + J[1][1] ** 2]]; A[1][0] = A[0][1];
      const tr = A[0][0] + A[1][1], det = A[0][0] * A[1][1] - A[0][1] ** 2, disc = Math.sqrt(Math.max(0, tr * tr / 4 - det)), ang = 0.5 * Math.atan2(2 * A[0][1], A[0][0] - A[1][1]);
      const ra = Math.sqrt(tr / 2 + disc) * 0.45, rb = Math.sqrt(Math.max(0, tr / 2 - disc)) * 0.45, pts = [];
      for (let k = 0; k <= 72; k++) { const t = k * Math.PI / 36, u = ra * Math.cos(t), v = rb * Math.sin(t); pts.push(P([p[0] + u * Math.cos(ang) - v * Math.sin(ang), p[1] + u * Math.sin(ang) + v * Math.cos(ang)])); }
      ctx.strokeStyle = 1 / Math.max(s.lci, 1e-9) < 1.01 ? "#2ca02c" : "#e8912d"; ctx.lineWidth = 2.5; ctx.beginPath(); pts.forEach((q, i) => (i ? ctx.lineTo(...q) : ctx.moveTo(...q))); ctx.closePath(); ctx.stroke();
      const g1 = api.graph({ x: W * 0.6, y: H * 0.08, w: W * 0.36, h: H * 0.34, xmin: 0, xmax: 180, ymin: 0, ymax: 1, xlabel: "θ₂ / °", ylabel: "1/κ" }).axes();
      g1.fn((x) => this.lci2(s.l1, s.l2, x * Math.PI / 180), api.css("--accent")); g1.point(api.p.th2, s.lci, "#e8912d");
      const g2 = api.graph({ x: W * 0.6, y: H * 0.56, w: W * 0.36, h: H * 0.32, xmin: 0.3, xmax: 1.5, ymin: 0.25, ymax: 0.45, xlabel: "λ", ylabel: "GCI" }).axes();
      if (!this._gciCurve) { this._gciCurve = []; for (let x = 0.3; x <= 1.5001; x += 0.01) this._gciCurve.push([x, this.gci(x)]); }
      g2.pts(this._gciCurve, api.css("--blue")); g2.point(api.p.lam, s.g, "#e8912d");
      return;
    }
    // 书桌（俯视）
    const sc = Math.min(W * 0.7 / 0.92, H * 0.86 / 0.72), ox = W * 0.08 + 0.3 * sc, oy = H * 0.07 + 0.62 * sc;
    const X = (x) => ox + x * sc, Y = (y) => oy - y * sc;
    api.rect(X(-0.3), Y(0.62), 0.92 * sc, 0.72 * sc, "#e9d8bd");
    if (this._deskMap) { ctx.save(); ctx.globalAlpha = 0.85; ctx.drawImage(this._deskMap.cv, X(-0.3), Y(0.62), 0.92 * sc, 0.72 * sc); ctx.restore(); }
    api.rect(X(-0.32), Y(-0.02), 0.5 * sc, 0.14 * sc, "#6e7681");          // 身体（俯视）
    api.label(api.T("身体", "body"), X(-0.07), Y(-0.09), "#ffffff", 12, "center");
    if (s.ok) {
      const e = [0.3 * Math.cos(s.t1), 0.3 * Math.sin(s.t1)], h = [e[0] + 0.32 * Math.cos(s.t1 + s.t2), e[1] + 0.32 * Math.sin(s.t1 + s.t2)];
      api.line(X(0), Y(0), X(e[0]), Y(e[1]), "#d9a679", 12); api.line(X(e[0]), Y(e[1]), X(h[0]), Y(h[1]), "#d9a679", 10);
      api.circle(X(h[0]), Y(h[1]), 7, "#d9a679", ink);
    }
    api.rect(X(api.p.dx) - 7, Y(api.p.dy) - 7, 14, 14, "#d62728", ink);
    api.label(api.T("零件", "part"), X(api.p.dx) + 10, Y(api.p.dy) - 10, ink, 12);
    api.label(api.T("右肩", "right shoulder"), X(0) + 6, Y(0) + 14, ink, 11);
  },
});
