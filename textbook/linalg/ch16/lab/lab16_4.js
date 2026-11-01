// 实验 16.4 Go2 腿部的振动模态（配 16.4 节）。参数与 code/_leg.py 相同：竖直方向的三质量链，自上而下为
// 躯干¼ + 髋（6.921/4 + 0.678 kg，可加背负载荷 mb）—k₁,c₁ = 30— 大腿 1.152 kg —k₂,c₂— 小腿 + 足 0.2414 kg —k₃,c₃ = 50— 地面（阻尼单位 N·s/m）。
// 固有频率与振型：Kv = ω²Mv（化为对称矩阵 M^{−1/2}KM^{−1/2} 用 eigSym）；模态阻尼比取近似 ζⱼ ≈ φⱼᵀCφⱼ/(2ωⱼ)（φ 按 M 归一）。
// 运动：Mq̈ + Cq̇ + Kq = 0 用四阶龙格–库塔积分。“落地”：三个质量初速度 −0.3 m/s，弹簧尚未受力（相对静平衡位置有初位移 K⁻¹Mg）；“激发振型 j”：初位移 = 第 j 振型（最大分量 10 mm）。
WQ.lab({
  title: ["实验 16.4 Go2 腿部的振动模态", "Lab 16.4 Vibration modes of a Go2 leg"],
  goal: ["把四足机器人的一条腿简化成质量–弹簧–阻尼链，求它的固有频率、振型和模态阻尼比；分别激发每个振型，再模拟落地，看躯干的振动主要来自哪个模态，怎样调刚度和阻尼让它更快停下来。",
         "Model one leg of a quadruped as a mass–spring–damper chain; find its natural frequencies, mode shapes and modal damping ratios; excite each mode, simulate a landing, see which mode dominates the body motion and how stiffness and damping make it settle faster."],
  scenes: [
    { id: "leg", robot: true, name: ["Go2 的一条腿", "One leg of a Go2"],
      problem: { title: ["四足机器人落地后为什么会“颤”？", "Why does a quadruped shudder after landing?"],
                 text: ["Go2 从台阶上跳下，触地后躯干上下振动。腿上的关节伺服像弹簧和阻尼器，足底橡胶也有弹性。振动由几个模态叠加而成，每个模态有自己的频率和衰减快慢。",
                        "A Go2 jumps off a step and its body bobs after touchdown. The joint servos act like springs and dampers and the rubber foot is elastic too. The vibration is a sum of a few modes, each with its own frequency and decay."] } },
  ],
  params: [
    { id: "k1", name: ["髋–大腿刚度 k₁", "Hip–thigh stiffness k₁"], min: 500, max: 10000, step: 100, value: 3000, unit: "N/m", digits: 0 },
    { id: "k2", name: ["膝关节刚度 k₂", "Knee stiffness k₂"], min: 500, max: 10000, step: 100, value: 2000, unit: "N/m", digits: 0 },
    { id: "k3", name: ["足底接触刚度 k₃", "Foot contact stiffness k₃"], min: 5000, max: 50000, step: 1000, value: 20000, unit: "N/m", digits: 0 },
    { id: "c2", name: ["膝关节阻尼 c₂", "Knee damping c₂"], min: 0, max: 200, step: 1, value: 20, unit: "N·s/m", digits: 0 },
    { id: "mb", name: ["背负载荷（每条腿）mb", "Payload per leg mb"], min: 0, max: 2, step: 0.1, value: 0, unit: "kg", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["落地", "Land"], primary: true }, { id: "m1", name: ["激发振型 1", "Excite mode 1"] },
            { id: "m2", name: ["激发振型 2", "Excite mode 2"] }, { id: "m3", name: ["激发振型 3", "Excite mode 3"] }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "modes", robot: true, text: ["用默认参数依次激发三个振型，读出三个固有频率，确认每次只有一个频率在振。", "With the default values excite the three modes one by one; read the three natural frequencies and check that each time only one frequency appears."],
      demo: { scene: "leg", set: { k1: 3000, k2: 2000, k3: 20000, c2: 20, mb: 0 }, press: ["m1", "m2", "m3"], wait: 1 } },
    { id: "land", robot: true, text: ["点“落地”，读出躯干的最大下沉量。它主要来自哪个振型？", "Press Land and read the largest body sink. Which mode is it mostly made of?"],
      demo: { scene: "leg", set: { k1: 3000, k2: 2000, k3: 20000, c2: 20, mb: 0 }, press: ["start"], wait: 2 } },
    { id: "damp", robot: true, text: ["只调膝关节阻尼 c₂，使第 1 模态的阻尼比超过 0.3，再点“落地”。躯干多快停下来？", "Adjust only the knee damping c₂ until the first modal damping ratio exceeds 0.3, then press Land. How fast does the body settle?"],
      demo: { scene: "leg", set: { k1: 3000, k2: 2000, k3: 20000, c2: 100, mb: 0 }, press: ["start"], wait: 2 } },
    { id: "load", robot: true, text: ["每条腿加 2 kg 背负载荷，调 k₁、k₂ 使第 1 固有频率回到 3.0～3.3 Hz。只加大 k₁ 为什么不够？", "Add a 2 kg payload per leg and adjust k₁ and k₂ until the first natural frequency is back in 3.0–3.3 Hz. Why is raising k₁ alone not enough?"],
      demo: { scene: "leg", set: { k1: 5000, k2: 4000, k3: 20000, c2: 20, mb: 2 }, press: [] } },
  ],
  think: ["第 3 振型几乎只有小腿在动，频率最高。为什么足底刚度 k₃ 对它影响最大，对第 1 振型影响很小？用振型解释。", "Mode 3 is almost only the calf moving and has the highest frequency. Why does the foot stiffness k₃ affect it most and mode 1 hardly at all? Explain with the mode shapes."],

  base: [6.921 / 4 + 0.678, 1.152, 0.2414], c13: [30, 50],
  model(api) {
    const p = api.p, m = [this.base[0] + p.mb, this.base[1], this.base[2]];
    const ch = (a, b, c) => [[a, -a, 0], [-a, a + b, -b], [0, -b, b + c]];
    const K = ch(p.k1, p.k2, p.k3), C = ch(this.c13[0], p.c2, this.c13[1]);
    const S = K.map((r, i) => r.map((x, j) => x / Math.sqrt(m[i] * m[j])));   // M^{-1/2} K M^{-1/2}
    const e = api.la.eigSym(S);
    const w = e.values.map(Math.sqrt);
    const Phi = [0, 1, 2].map((j) => [0, 1, 2].map((i) => e.vectors[i][j] / Math.sqrt(m[i])));   // Phi[j] = φ_j, M-normalized
    const zeta = Phi.map((ph, j) => { let s = 0; for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) s += ph[a] * C[a][b] * ph[b]; return s / (2 * w[j]); });
    return { m, K, C, w, Phi, zeta };
  },
  rhs(md, y) {
    const q = y.slice(0, 3), v = y.slice(3), a = [0, 1, 2].map((i) => -(md.K[i].reduce((s, k, j) => s + k * q[j], 0) + md.C[i].reduce((s, c, j) => s + c * v[j], 0)) / md.m[i]);
    return [...v, ...a];
  },
  reset(api, s) { s.md = this.model(api); s.y = [0, 0, 0, 0, 0, 0]; s.hist = []; s.minb = 0; s.kind = null; },
  start(api, s) {   // 触地瞬间弹簧未受力：相对静平衡位置，各质量高出其下方各弹簧的静压缩量之和
    const md = s.md, g = 9.81, W = [md.m[0] * g, (md.m[0] + md.m[1]) * g, (md.m[0] + md.m[1] + md.m[2]) * g], k = [api.p.k1, api.p.k2, api.p.k3];
    const d = [W[0] / k[0], W[1] / k[1], W[2] / k[2]];
    s.y = [d[0] + d[1] + d[2], d[1] + d[2], d[2], -0.3, -0.3, -0.3]; s.hist = []; s.minb = 0; s.kind = "land";
  },
  action(id, api, s) {
    const j = { m1: 0, m2: 1, m3: 2 }[id];
    if (j === undefined) return;
    s.md = this.model(api);
    const ph = s.md.Phi[j], amax = Math.max(...ph.map(Math.abs)), sc = 0.01 / amax;
    s.y = [...ph.map((x) => x * sc), 0, 0, 0]; s.hist = []; s.minb = 0; s.kind = "m" + (j + 1); this._exc = (this._exc || new Set()).add(j);
    api.t = 0; api.running = true;
  },
  update(dt, api, s) {
    const md = s.md, n = 40, h = dt / n;
    for (let i = 0; i < n; i++) {
      const y = s.y, k1 = this.rhs(md, y), k2 = this.rhs(md, y.map((v, j) => v + h / 2 * k1[j])), k3 = this.rhs(md, y.map((v, j) => v + h / 2 * k2[j])), k4 = this.rhs(md, y.map((v, j) => v + h * k3[j]));
      s.y = y.map((v, j) => v + h / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]));
    }
    s.hist.push([api.t, s.y[0], s.y[1], s.y[2]]);
    s.minb = Math.min(s.minb, s.y[0]);
    if (api.t > 1.2) { s.last = s.kind; api.stop(); }
  },
  readouts(api, s) {
    if (!s.md) return [];
    const md = s.md, f = api.fmt, fr = md.w.map((x) => x / 2 / Math.PI);
    if (this._exc && this._exc.size === 3) api.done("modes");
    if (s.kind === "land" && api.t > 1) api.done("land");
    if (md.zeta[0] > 0.3 && s.kind === "land" && api.t > 1) api.done("damp");
    if (api.p.mb >= 2 - 1e-9 && fr[0] >= 3.0 && fr[0] <= 3.3) api.done("load");
    const shp = md.Phi.map((ph) => { const a = ph.reduce((p, x) => Math.abs(x) > Math.abs(p) ? x : p, 0); return "(" + ph.map((x) => f(x / a, 2)).join(", ") + ")"; });
    const rows = [[["固有频率 f₁、f₂、f₃ / Hz", "Natural frequencies f₁, f₂, f₃ / Hz"], fr.map((x) => f(x, 2)).join(", ")],
                  [["振型 1（躯干, 大腿, 小腿）", "Mode 1 (body, thigh, calf)"], shp[0]],
                  [["振型 2", "Mode 2"], shp[1]],
                  [["振型 3", "Mode 3"], shp[2]],
                  [["模态阻尼比 ζ₁、ζ₂、ζ₃（近似）", "Modal damping ratios ζ₁, ζ₂, ζ₃ (approx.)"], md.zeta.map((x) => f(x, 3)).join(", ")]];
    if (s.kind === "land") rows.push([["落地后躯干最大下沉（相对静平衡）/ mm", "Largest body sink after landing (from equilibrium) / mm"], f(-1000 * s.minb, 1)]);
    return rows;
  },
  change(api, s) { s.md = this.model(api); },
  draw(api, s) {
    if (!s.md) return;
    const { w, h } = api, mu = api.css("--muted"), ink = api.css("--ink"), ctx = api.ctx, md = s.md;
    // left: the chain, displacements magnified ×20
    const gx = w * 0.18, gy = h - 40;
    const yr = [h * 0.2, h * 0.47, h * 0.72], col = [api.css("--blue"), api.css("--green"), api.css("--red")];
    const yy = yr.map((y, i) => y - s.y[i] * 1000 * 3);   // magnified: 1 mm → 3 px
    api.line(gx - 60, gy, gx + 60, gy, ink, 3);
    const spring = (y0, y1) => { ctx.beginPath(); for (let i = 0; i <= 40; i++) { const t = i / 40, x = gx + (t > 0.15 && t < 0.85 ? 10 * Math.sin(2 * Math.PI * 6 * t) : 0); i ? ctx.lineTo(x, y0 + (y1 - y0) * t) : ctx.moveTo(x, y0 + (y1 - y0) * t); } ctx.strokeStyle = ink; ctx.lineWidth = 1.2; ctx.stroke(); };
    spring(yy[0] + 16, yy[1] - 14); spring(yy[1] + 14, yy[2] - 10); spring(yy[2] + 10, gy);
    md.m.forEach((m, i) => { const ww = 26 + 14 * m, hh = 16 + 6 * Math.min(m, 3); api.rect(gx - ww, yy[i] - hh / 2, 2 * ww, hh, col[i], null, 4); });
    [api.T("躯干¼+髋", "¼ body+hip"), api.T("大腿", "thigh"), api.T("小腿+足", "calf+foot")].forEach((t, i) => api.label(t, gx + 70, yy[i] + 4, ink, 12));
    api.label(api.T("位移放大：1 mm = 3 px", "displacement magnified: 1 mm = 3 px"), 10, 18, mu, 11);
    // right: displacement history (mm), 0–1.2 s
    const x0 = w * 0.42, x1 = w - 15, y0 = 30, y1 = h - 30, ym = (y0 + y1) / 2;
    const amp = Math.max(5, ...s.hist.map((r) => Math.max(Math.abs(r[1]), Math.abs(r[2]), Math.abs(r[3])) * 1000));
    api.line(x0, ym, x1, ym, mu, 1); api.line(x0, y0, x0, y1, mu, 1);
    for (let k = 1; k <= 3; k++) {
      if (s.hist.length < 2) break;
      ctx.beginPath(); s.hist.forEach((r, i) => { const X = x0 + (x1 - x0) * r[0] / 1.2, Y = ym - (y1 - ym) * 1000 * r[k] / amp; i ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y); });
      ctx.strokeStyle = col[k - 1]; ctx.lineWidth = k === 1 ? 2.5 : 1.5; ctx.stroke();
    }
    api.label(api.T("位移 / mm（蓝：躯干，绿：大腿，红：小腿），0～1.2 s，纵轴满量程 ±", "displacement / mm (blue body, green thigh, red calf), 0–1.2 s, full scale ±") + api.fmt(amp, 1), x0, y0 - 10, mu, 11);
  },
});
