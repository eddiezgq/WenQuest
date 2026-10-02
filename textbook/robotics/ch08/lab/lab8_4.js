// 实验 8.4 凸与非凸（配 8.4 节）。
// “凸走廊”：与算例 8.4.3 相同的车间：R₁ = 下方走廊（上边倾斜），R₂ = 右侧走廊；航点 x₁…x₅ ∈ R₁，x₅…x₉ ∈ R₂；
// min Σ‖x_{k+1} − x_k‖²，对数障碍函数法（式 (8.4.8)）：t 从 1 起每次乘 10 定心，直到当前的 t。对偶间隙上界 m/t（式 (8.4.9)）。
// “碗与蛋托”：小球沿负梯度滚动（梯度下降）。碗 f = 0.2(x² + xy + 2y²) 是凸函数；蛋托 f = 0.06(x² + y²) − 0.5cos(2x)cos(2y) 不是。
WQ.lab({
  title: ["实验 8.4 凸与非凸", "Lab 8.4 Convex and non-convex"],
  goal: ["用障碍函数法在凸走廊中规划 AGV 的路径，看中心路径与对偶间隙；比较小球在凸的碗和非凸的蛋托里滚到哪里。",
         "Plan an AGV path in convex corridors with the barrier method and watch the central path and the duality gap; compare where a ball rolls in a convex bowl and in a non-convex egg tray."],
  scenes: [
    { id: "corr", robot: true, name: ["凸走廊中的 AGV", "AGV in convex corridors"], hide: ["shape", "bx", "by"],
      problem: { title: ["机器人问题：AGV 绕过货架", "Robot problem: an AGV drives around the shelves"],
                 text: ["可通行区域是 L 形的，不是凸集；拆成两个凸区域后，路径规划成了一个凸二次规划，最优解有保证。",
                        "The free space is L-shaped and not convex; split into two convex regions, path planning becomes a convex QP with a guaranteed optimum."] } },
    { id: "bowl", name: ["碗与蛋托", "Bowl and egg tray"], hide: ["sx", "sy", "gx", "gy", "logt"],
      problem: { title: ["生活中的例子：小球滚到哪里", "Everyday example: where does the ball roll?"],
                 text: ["在碗里，小球无论从哪里放下都滚到同一个最低点；在蛋托里，它落进最近的凹坑。",
                        "In a bowl the ball always rolls to the same lowest point; in an egg tray it drops into the nearest dimple."] } },
  ],
  params: [
    { id: "sx", name: ["起点 x", "Start x"], min: 0.3, max: 3, step: 0.1, value: 0.5, unit: "m", digits: 1 },
    { id: "sy", name: ["起点 y", "Start y"], min: 0.2, max: 1.4, step: 0.1, value: 0.9, unit: "m", digits: 1 },
    { id: "gx", name: ["终点 x", "Goal x"], min: 4.7, max: 5.9, step: 0.1, value: 5.3, unit: "m", digits: 1 },
    { id: "gy", name: ["终点 y", "Goal y"], min: 0.3, max: 3.9, step: 0.1, value: 3.5, unit: "m", digits: 1 },
    { id: "logt", name: ["障碍参数 lg t", "Barrier parameter lg t"], min: 0, max: 5, step: 1, value: 0, unit: "", digits: 0 },
    { id: "shape", name: ["形状：0 碗 / 1 蛋托", "Shape: 0 bowl / 1 egg tray"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "bx", name: ["放球位置 x", "Drop position x"], min: -4, max: 4, step: 0.1, value: 3, unit: "", digits: 1 },
    { id: "by", name: ["放球位置 y", "Drop position y"], min: -4, max: 4, step: 0.1, value: 2, unit: "", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["放球", "Drop the ball"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "gap", robot: true, text: ["把 t 加大，使对偶间隙上界 m/t 小于 0.01。", "Raise t until the duality-gap bound m/t is below 0.01."],
      demo: { scene: "corr", set: { logt: 4 }, press: [] } },
    { id: "goal", robot: true, text: ["t ≥ 10⁴ 时把终点移到右侧走廊顶部附近（y ≥ 3.8 m）：拐角航点仍在 (4.6, 1.34) m。", "With t ≥ 10⁴ move the goal near the top of the right corridor (y ≥ 3.8 m): the corner waypoint stays at (4.6, 1.34) m."],
      demo: { scene: "corr", set: { logt: 5, gy: 3.9, gx: 5.0 }, press: [] } },
    { id: "bowl", text: ["在碗中放球，它滚到最低点 (0, 0)。", "Drop the ball in the bowl: it rolls to the lowest point (0, 0)."],
      demo: { scene: "bowl", set: { shape: 0, bx: -3, by: 3 }, press: ["start"], wait: 6 } },
    { id: "egg", text: ["在蛋托中找一个放球位置，使小球停在不是最低的凹坑里。", "In the egg tray find a drop position where the ball stops in a dimple that is not the lowest."],
      demo: { scene: "bowl", set: { shape: 1, bx: 3, by: 2 }, press: ["start"], wait: 6 } },
  ],
  think: ["若把 9 个航点都只限制在 R₁ ∪ R₂（两个区域的并集）中，问题还是凸的吗？为什么要事先规定每个航点属于哪个区域？",
          "If the 9 waypoints were only required to lie in R₁ ∪ R₂ (the union), would the problem still be convex? Why must each waypoint be assigned to a region beforehand?"],

  R1: [[0, 0], [6, 0], [6, 1.2], [0, 1.8]], R2: [[4.6, 0], [6, 0], [6, 4], [4.6, 4]], N: 10, KX: 5,
  half(P) { return P.map((p, i) => { const q = P[(i + 1) % P.length], t = [q[0] - p[0], q[1] - p[1]], L = Math.hypot(...t), n = [t[1] / L, -t[0] / L]; return [n, n[0] * p[0] + n[1] * p[1]]; }); },
  solve(M, b) {
    const n = b.length, A = M.map((r, i) => [...r, b[i]]);
    for (let i = 0; i < n; i++) {
      let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(A[j][i]) > Math.abs(A[p][i])) p = j;
      [A[i], A[p]] = [A[p], A[i]];
      for (let j = i + 1; j < n; j++) { const f = A[j][i] / A[i][i]; if (f) for (let k = i; k <= n; k++) A[j][k] -= f * A[i][k]; }
    }
    const x = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) { let s = A[i][n]; for (let k = i + 1; k < n; k++) s -= A[i][k] * x[k]; x[i] = s / A[i][i]; }
    return x;
  },
  plan(api) {                                          // 中心路径：t = 1, 10, …, 10^logt
    const key = [api.p.sx, api.p.sy, api.p.gx, api.p.gy, api.p.logt].join("|");
    if (this._plan && this._plan.key === key) return this._plan;
    const S = [api.p.sx, api.p.sy], G = [api.p.gx, api.p.gy], N = this.N, nv = 2 * (N - 1), C0 = [5.3, 0.6];
    const rows = [];                                   // [航点序号 i (1…9), 法向 a, b]
    const h1 = this.half(this.R1), h2 = this.half(this.R2);
    for (let i = 1; i < N; i++) { if (i <= this.KX) h1.forEach(([a, b]) => rows.push([i, a, b])); if (i >= this.KX) h2.forEach(([a, b]) => rows.push([i, a, b])); }
    let x = [];
    for (let i = 1; i < N; i++) { const p = i <= this.KX ? [S[0] + (C0[0] - S[0]) * i / this.KX, S[1] + (C0[1] - S[1]) * i / this.KX]
      : [C0[0] + (G[0] - C0[0]) * (i - this.KX) / (N - this.KX), C0[1] + (G[1] - C0[1]) * (i - this.KX) / (N - this.KX)]; x.push(p[0], p[1]); }
    const pt = (z, i) => (i === 0 ? S : i === N ? G : [z[2 * (i - 1)], z[2 * i - 1]]);
    const fval = (z) => { let s = 0; for (let i = 0; i < N; i++) { const a = pt(z, i), b = pt(z, i + 1); s += (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2; } return s; };
    const slack = (z) => rows.map(([i, a, b]) => b - a[0] * z[2 * (i - 1)] - a[1] * z[2 * i - 1]);
    const phi = (z, t) => { const s = slack(z); if (s.some((v) => v <= 0)) return Infinity; return t * fval(z) - s.reduce((u, v) => u + Math.log(v), 0); };
    const centers = [], m = rows.length;
    for (let e = 0; e <= api.p.logt; e++) {
      const t = 10 ** e;
      for (let it = 0; it < 80; it++) {
        const s = slack(x), g = new Array(nv).fill(0), H = Array.from({ length: nv }, () => new Array(nv).fill(0));
        for (let i = 1; i < N; i++) for (let c = 0; c < 2; c++) {     // ∇ Σ‖x_{k+1} − x_k‖² 与它的黑塞矩阵（2 和 −2 的三对角）
          const k = 2 * (i - 1) + c, here = pt(x, i)[c];
          g[k] += t * 2 * (2 * here - pt(x, i - 1)[c] - pt(x, i + 1)[c]); H[k][k] += 4 * t;
          if (i > 1) H[k][k - 2] -= 2 * t; if (i < N - 1) H[k][k + 2] -= 2 * t;
        }
        rows.forEach(([i, a], r) => { const k = 2 * (i - 1);
          g[k] += a[0] / s[r]; g[k + 1] += a[1] / s[r];
          const w = 1 / (s[r] * s[r]); H[k][k] += w * a[0] * a[0]; H[k][k + 1] += w * a[0] * a[1]; H[k + 1][k] += w * a[0] * a[1]; H[k + 1][k + 1] += w * a[1] * a[1]; });
        const dx = this.solve(H, g.map((v) => -v)), dec = -g.reduce((u, v, k) => u + v * dx[k], 0);
        if (dec / 2 < 1e-10) break;
        let st = 1; const f0 = phi(x, t);
        while (phi(x.map((v, k) => v + st * dx[k]), t) > f0 - 0.25 * st * dec && st > 1e-10) st *= 0.5;
        x = x.map((v, k) => v + st * dx[k]);
      }
      centers.push({ t, P: Array.from({ length: N + 1 }, (_, i) => pt(x, i)) });
    }
    const Pf = centers[centers.length - 1].P;
    let len = 0;
    for (let i = 0; i < N; i++) len += Math.hypot(Pf[i + 1][0] - Pf[i][0], Pf[i + 1][1] - Pf[i][1]);
    this._plan = { key, centers, m, P: Pf, len };
    return this._plan;
  },
  f(api, x, y) { return api.p.shape === 0 ? 0.2 * (x * x + x * y + 2 * y * y) : 0.06 * (x * x + y * y) - 0.5 * Math.cos(2 * x) * Math.cos(2 * y); },
  grad(api, x, y) { return api.p.shape === 0 ? [0.2 * (2 * x + y), 0.2 * (x + 4 * y)]
    : [0.12 * x + Math.sin(2 * x) * Math.cos(2 * y), 0.12 * y + Math.cos(2 * x) * Math.sin(2 * y)]; },

  reset(api, s) { s.b = [api.p.bx, api.p.by]; s.path = [s.b.slice()]; s.clock = 0; s.stop = false; },
  update(dt, api, s) {
    if (api.scene !== "bowl") { api.stop(); return; }
    s.clock += dt;
    while (s.clock >= 0.02 && api.running) {
      s.clock -= 0.02;
      const g = this.grad(api, s.b[0], s.b[1]);
      s.b = [s.b[0] - 0.25 * g[0], s.b[1] - 0.25 * g[1]]; s.path.push(s.b.slice());
      if (Math.hypot(...g) < 1e-6 || s.path.length > 2000) { s.stop = true; api.stop(); }
    }
  },
  readouts(api, s) {
    const f = (x, n) => api.fmt(x, n);
    if (api.scene === "bowl") {
      const fv = this.f(api, s.b[0], s.b[1]), fmin = api.p.shape === 0 ? 0 : -0.5;
      if (s.stop && api.p.shape === 0 && Math.hypot(...s.b) < 1e-3) api.done("bowl");
      if (s.stop && api.p.shape === 1 && fv > fmin + 0.05) api.done("egg");
      return [[["形状", "shape"], api.p.shape === 0 ? api.T("碗（凸函数）", "bowl (convex)") : api.T("蛋托（非凸）", "egg tray (non-convex)")],
              [["小球位置", "ball position"], `(${f(s.b[0], 3)}, ${f(s.b[1], 3)})`], [["高度 f", "height f"], f(fv, 4)],
              [["全局最低高度", "global minimum"], f(fmin, 4)], [["步数", "steps"], String(s.path.length - 1)]];
    }
    const pl = this.plan(api), t = 10 ** api.p.logt, c = pl.P[this.KX];
    if (pl.m / t < 0.01) api.done("gap");
    if (t >= 1e4 && api.p.gy >= 3.8 && Math.hypot(c[0] - 4.6, c[1] - 1.34) < 0.01) api.done("goal");
    return [[["障碍参数 t", "barrier parameter t"], t >= 1000 ? t.toExponential(0) : String(t)],
            [["不等式约束个数 m", "number of inequalities m"], String(pl.m)],
            [["对偶间隙上界 m/t", "duality-gap bound m/t"], (pl.m / t).toPrecision(2)],
            [["拐角航点 x₅", "corner waypoint x₅"], `(${f(c[0], 3)}, ${f(c[1], 3)}) m`],
            [["路径长度", "path length"], f(pl.len, 4) + " m"]];
  },
  draw(api, s) {
    const { w, h, ctx } = api;
    if (api.scene === "bowl") {
      const side = Math.min(w * 0.62, h * 0.92), x0 = (w - side) / 2, y0 = (h - side) / 2, R = 4.5;
      const X = (v) => x0 + (v + R) / (2 * R) * side, Y = (v) => y0 + side - (v + R) / (2 * R) * side;
      const n = 90, dark = parseInt(api.css("--stage").slice(1, 3), 16) < 128, key = api.p.shape + "|" + dark;
      if (!this._bg || this._bg.key !== key) {                 // 背景（等高线分层）画在缓存的小画布上
        const cv = document.createElement("canvas"); cv.width = n; cv.height = n;
        const c2 = cv.getContext("2d"), img = c2.createImageData(n, n);
        for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
          const v = this.f(api, -R + (i + 0.5) * 2 * R / n, -R + (j + 0.5) * 2 * R / n), lv = Math.floor(v / (api.p.shape === 0 ? 0.4 : 0.12));
          const band = ((lv % 2) + 2) % 2, shade = dark ? 40 + band * 14 : 205 + band * 16, o = 4 * ((n - 1 - j) * n + i);
          img.data[o] = shade; img.data[o + 1] = shade - 8; img.data[o + 2] = shade - 30; img.data[o + 3] = 255;
        }
        c2.putImageData(img, 0, 0);
        this._bg = { key, cv };
      }
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(this._bg.cv, x0, y0, side, side);
      api.rect(x0, y0, side, side, null, api.css("--ink"));
      ctx.strokeStyle = api.css("--blue"); ctx.lineWidth = 2; ctx.beginPath();
      s.path.forEach((p, i) => (i ? ctx.lineTo(X(p[0]), Y(p[1])) : ctx.moveTo(X(p[0]), Y(p[1])))); ctx.stroke();
      api.circle(X(s.b[0]), Y(s.b[1]), 7, api.css("--red"), api.css("--ink"));
      api.circle(X(0), Y(0), 4, api.css("--ink"));
      return;
    }
    const k = Math.min(w / 6.6, h / 4.4), ox = (w - 6 * k) / 2, oy = h - (h - 4 * k) / 2;
    const P = (p) => [ox + k * p[0], oy - k * p[1]];
    const poly = (pts, fill, stroke) => { ctx.beginPath(); pts.forEach((p, i) => { const q = P(p); if (i) ctx.lineTo(...q); else ctx.moveTo(...q); }); ctx.closePath();
      if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 2; ctx.stroke(); } };
    poly([[0, 0], [6, 0], [6, 4], [0, 4]], api.css("--soft"));
    poly([[0, 1.8], [4.6, 1.34], [4.6, 4], [0, 4]], api.css("--muted"));
    api.label(api.T("货架（已膨胀）", "shelves (inflated)"), P([1.6, 3])[0], P([1.6, 3])[1], api.css("--panel"), 14);
    poly(this.R1, "rgba(31,111,235,0.10)", api.css("--blue"));
    poly(this.R2, "rgba(130,80,223,0.10)", api.css("--violet"));
    api.label("R₁", P([0.15, 0.2])[0], P([0.15, 0.2])[1], api.css("--blue"), 14);
    api.label("R₂", P([5.6, 3.75])[0], P([5.6, 3.75])[1], api.css("--violet"), 14);
    const pl = this.plan(api);
    pl.centers.forEach((c, idx) => {
      const last = idx === pl.centers.length - 1;
      ctx.strokeStyle = last ? api.css("--red") : api.css("--amber"); ctx.lineWidth = last ? 3 : 1.2; ctx.globalAlpha = last ? 1 : 0.6;
      ctx.beginPath(); c.P.forEach((p, i) => { const q = P(p); if (i) ctx.lineTo(...q); else ctx.moveTo(...q); }); ctx.stroke(); ctx.globalAlpha = 1;
      if (last) c.P.forEach((p) => api.circle(...P(p), 4, api.css("--red")));
    });
    api.rect(P([api.p.sx, 0])[0] - 7, P([0, api.p.sy])[1] - 7, 14, 14, api.css("--ink"));
    api.circle(...P([api.p.gx, api.p.gy]), 8, api.css("--ink"));
    api.label(api.T("细线：较小 t 的中心路径", "thin lines: central path for smaller t"), 12, 16, api.css("--muted"), 12);
  },
});
