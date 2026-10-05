// 实验 17.3 保持末端不动，躲开障碍物（配 17.3 节）。
// 机器人场景：平面 3R 臂 0.425、0.392、0.1 m，末端固定在 (0.6, 0.2) m；起始形态取工具朝向 φ₀、θ₂ < 0（肘上）的解（默认 φ₀ = −60°）。
//   主任务：θ̇₁ = J⁺K_p(p_d − p)，K_p = 5 /s；N = I − J⁺J。次要任务四选一（式 (17.3.1)、(17.3.7)）：
//   0 无；1 避障：半径 0.05 m 的圆在 3 s 内从 (0.17, 0.85) m 压到 (0.17, 0.42) m（余弦过渡），d 为手臂到圆周的最短距离，
//     d < d_a 时 θ̇ = θ̇₁ + (aN)ᵀ/((aN)(aN)ᵀ + λ_o²)·(uᵀȯ + K_d(d_a − d) − aθ̇₁)，K_d = 3 /s，λ_o = 0.02 m（算例 17.3.3 的平面部分）；
//   2 避限位：限位 θ₁ ∈ [−30°, 70°]、θ₂ ∈ [−150°, 0°]、θ₃ ∈ [−150°, 150°]，θ̇ = θ̇₁ − k N∇H，H 取式 (15.4.6)；
//   3 提高可操作度：θ̇ = θ̇₁ + k N∇w，∇w 用中心差商。欧拉法积分，步长 4 ms，共 4 s。
// 生活场景：从上往下看，人端着一杯水站在门口（上臂 0.30 m、前臂 0.27 m、手 0.08 m，杯子在 (0.42, 0.05) m 不动），
//   一个路过的人（半径 0.08 m 的圆）在 3 s 内从 (0.12, 0.62) m 走到 (0.12, 0.30) m；起始形态取手朝前、θ₂ < 0 的解。
WQ.lab({
  title: ["实验 17.3 保持末端不动，躲开障碍物", "Lab 17.3 Keeping the tip still while avoiding an obstacle"],
  goal: ["在主任务（末端不动）的零空间里完成次要任务：躲开压下来的障碍物、离开关节限位、提高可操作度；看激活距离、增益怎样影响效果，次要任务为什么不影响末端。",
         "Carry out secondary tasks in the null space of the primary task (tip fixed): dodge an approaching obstacle, move away from a joint limit, raise the manipulability; see how the activation distance and the gain matter and why the secondary task never disturbs the tip."],
  scenes: [
    { id: "arm", robot: true, name: ["平面 3R 臂的次要任务", "Secondary tasks of a planar 3R arm"], hide: [],
      problem: { title: ["机器人问题：末端固定在工件上，障碍物压过来怎么办？", "Robot problem: the tip is fixed on the workpiece; what if an obstacle comes down on the arm?"],
                 text: ["红点是固定的末端位置。选择次要任务，按“开始”运行 4 s。模式 0、1 有一个圆形障碍物从上方压下来，虚线圈是激活距离；模式 2 的浅色扇形是关节 1 的允许范围；模式 3 显示可操作度的变化。",
                        "The red dot is the fixed tip position. Choose a secondary task and press “Start” to run 4 s. In modes 0 and 1 a round obstacle comes down from above, the dashed ring being the activation distance; in mode 2 the pale wedge is joint 1's allowed range; mode 3 shows the manipulability."] } },
    { id: "cup", name: ["端着水杯在门口让路", "Holding a cup in a doorway"], hide: ["k", "phi0"], params: { mode: { min: 0, max: 1, value: 0 }, da: { value: 0.06 } },
      problem: { title: ["生活中的例子：杯子不能动，胳膊让开", "Everyday example: the cup must not move, the arm gives way"],
                 text: ["从上往下看，一个人端着一杯水站在门口，杯子不能动；有人从旁边挤过来。模式 0 胳膊不动，模式 1 在杯子不动的前提下收肘让路。",
                        "Seen from above, a person holds a cup in a doorway and the cup must not move; someone squeezes past. In mode 0 the arm stays put, in mode 1 the elbow tucks in while the cup stays still."] } },
  ],
  params: [
    { id: "mode", name: ["次要任务：0 无 / 1 避障 / 2 避限位 / 3 提高可操作度", "secondary task: 0 none / 1 obstacle / 2 joint limits / 3 manipulability"], min: 0, max: 3, step: 1, value: 1, unit: "", digits: 0 },
    { id: "da", name: ["激活距离 d_a", "activation distance d_a"], min: 0.01, max: 0.2, step: 0.01, value: 0.1, unit: "m", digits: 2 },
    { id: "k", name: ["次要任务的增益 k（模式 2、3）", "secondary gain k (modes 2, 3)"], min: 0, max: 50, step: 1, value: 10, unit: "", digits: 0 },
    { id: "phi0", name: ["起始形态的工具朝向 φ₀", "tool direction φ₀ of the start configuration"], min: -180, max: 180, step: 5, value: -60, unit: "°", digits: 0 },
  ],
  legend: [{ color: "#1f6feb", name: ["手臂", "arm"] }, { color: "#cf222e", name: ["障碍物 / 末端", "obstacle / tip"] }, { color: "#d29922", name: ["肘点的路径", "elbow path"] }],
  tasks: [
    { id: "hit", robot: true, text: ["模式 0（无次要任务）：手臂一动不动，被障碍物压到（最小距离 < 0）。", "Mode 0 (no secondary task): the arm does not move and is hit (minimum distance < 0)."],
      demo: { scene: "arm", set: { mode: 0, phi0: -60 }, press: ["start"], wait: 6 } },
    { id: "avoid", robot: true, text: ["模式 1（避障）、d_a = 0.10 m：最小距离大于 2 cm，末端误差小于 1 mm。", "Mode 1 (obstacle), d_a = 0.10 m: minimum distance above 2 cm, tip error below 1 mm."],
      demo: { scene: "arm", set: { mode: 1, da: 0.1, phi0: -60 }, press: ["start"], wait: 6 } },
    { id: "small", robot: true, text: ["把激活距离减到 0.04 m 以下，仍然碰不到（最小距离 > 0）。", "Reduce the activation distance below 0.04 m and still avoid contact (minimum distance > 0)."],
      demo: { scene: "arm", set: { mode: 1, da: 0.03, phi0: -60 }, press: ["start"], wait: 6 } },
    { id: "lim", robot: true, text: ["模式 2（避限位），φ₀ = −60°：关节 1 离上限 70° 的距离由 3.8° 增大到 6° 以上，末端误差小于 1 mm。", "Mode 2 (joint limits), φ₀ = −60°: joint 1 moves from 3.8° to more than 6° below its upper limit of 70°, tip error below 1 mm."],
      demo: { scene: "arm", set: { mode: 2, k: 10, phi0: -60 }, press: ["start"], wait: 6 } },
    { id: "manip", robot: true, text: ["模式 3（提高可操作度），φ₀ = 150°：可操作度提高 10% 以上，末端误差小于 1 mm。", "Mode 3 (manipulability), φ₀ = 150°: manipulability up by more than 10%, tip error below 1 mm."],
      demo: { scene: "arm", set: { mode: 3, k: 20, phi0: 150 }, press: ["start"], wait: 6 } },
    { id: "cup", text: ["生活场景：模式 1，杯子不动（误差 < 1 mm），胳膊没有被碰到。", "Everyday scene: mode 1, the cup stays (error < 1 mm) and the arm is not touched."],
      demo: { scene: "cup", set: { mode: 1, da: 0.06 }, press: ["start"], wait: 6 } },
  ],
  think: ["激活距离越小，手臂越晚开始让开。为什么 d_a 很小时也碰不到？在什么情况下，即使 d_a 很大，手臂也让不开（提示：aN = 0，即算法奇异）？",
          "The smaller the activation distance, the later the arm starts to give way. Why is there still no contact when d_a is small? When can the arm not give way however large d_a is (hint: aN = 0, an algorithmic singularity)?"],

  DT: 0.004, TEND: 4.0, KP: 5, KD: 3, LAM: 0.02,
  LO: [-30, -150, -150], HI: [70, 0, 150],
  rad: (d) => d * Math.PI / 180, deg: (r) => r * 180 / Math.PI,
  cfg(api) {
    return api.scene === "arm" ? { L: [0.425, 0.392, 0.1], P: [0.6, 0.2], C0: [0.17, 0.85], C1: [0.17, 0.42], R: 0.05, phi0: api.p.phi0 }
      : { L: [0.30, 0.27, 0.08], P: [0.42, 0.05], C0: [0.12, 0.62], C1: [0.12, 0.30], R: 0.08, phi0: 0 };
  },
  pts(th, L) { let a = 0; const P = [[0, 0]]; th.forEach((t, i) => { a += t; P.push([P[i][0] + L[i] * Math.cos(a), P[i][1] + L[i] * Math.sin(a)]); }); return P; },
  jac(th, L) { const P = this.pts(th, L), e = P[3]; return [[0, 1, 2].map((i) => -(e[1] - P[i][1])), [0, 1, 2].map((i) => e[0] - P[i][0])]; },
  pinvTimes(J, v) {
    const a = J[0].reduce((s, x) => s + x * x, 0), b = J[0].reduce((s, x, i) => s + x * J[1][i], 0), d = J[1].reduce((s, x) => s + x * x, 0);
    const det = a * d - b * b, y = [(d * v[0] - b * v[1]) / det, (-b * v[0] + a * v[1]) / det];
    return [0, 1, 2].map((i) => J[0][i] * y[0] + J[1][i] * y[1]);
  },
  proj(J, z) { const r = this.pinvTimes(J, [J[0].reduce((u, x, i) => u + x * z[i], 0), J[1].reduce((u, x, i) => u + x * z[i], 0)]); return z.map((x, i) => x - r[i]); },   // N z
  manip(th, L) { const J = this.jac(th, L), a = J[0].reduce((s, x) => s + x * x, 0), b = J[0].reduce((s, x, i) => s + x * J[1][i], 0), d = J[1].reduce((s, x) => s + x * x, 0); return Math.sqrt(Math.max(0, a * d - b * b)); },
  ik(L, p, phi) {   // θ₂ < 0 的解
    const wx = p[0] - L[2] * Math.cos(phi), wy = p[1] - L[2] * Math.sin(phi);
    const c2 = (wx * wx + wy * wy - L[0] * L[0] - L[1] * L[1]) / (2 * L[0] * L[1]);
    if (Math.abs(c2) > 1) return null;
    const t2 = -Math.acos(c2), t1 = Math.atan2(wy, wx) - Math.atan2(L[1] * Math.sin(t2), L[0] + L[1] * Math.cos(t2));
    return [t1, t2, phi - t1 - t2];
  },
  seg(c, a, b) { const ab = [b[0] - a[0], b[1] - a[1]], L2 = ab[0] * ab[0] + ab[1] * ab[1];
    const s = Math.max(0, Math.min(1, ((c[0] - a[0]) * ab[0] + (c[1] - a[1]) * ab[1]) / L2)), x = [a[0] + s * ab[0], a[1] + s * ab[1]];
    return [Math.hypot(c[0] - x[0], c[1] - x[1]), x]; },
  obstacle(api, t) {
    const g = this.cfg(api), T = 3.0, s = (1 - Math.cos(Math.PI * Math.min(t, T) / T)) / 2, sd = t < T ? Math.PI / T * Math.sin(Math.PI * t / T) / 2 : 0;
    return { c: [g.C0[0] + s * (g.C1[0] - g.C0[0]), g.C0[1] + s * (g.C1[1] - g.C0[1])], cd: [sd * (g.C1[0] - g.C0[0]), sd * (g.C1[1] - g.C0[1])] };
  },
  dist(api, th, t) {
    const g = this.cfg(api), P = this.pts(th, g.L), o = this.obstacle(api, t);
    let best = [1e9, null, 0];
    for (let k = 0; k < 3; k++) { const [d, x] = this.seg(o.c, P[k], P[k + 1]); if (d < best[0]) best = [d, x, k]; }
    return { d: best[0] - g.R, x: best[1], k: best[2], o };
  },
  reset(api, s) {
    const g = this.cfg(api);
    s.t = 0; s.th = this.ik(g.L, g.P, this.rad(g.phi0)); s.ok = !!s.th; if (!s.th) s.th = [0, 0, 0];
    s.th0 = s.th.slice(); s.dmin = 9; s.err = 0; s.trail = []; s.done = false; s.w0 = this.manip(s.th, g.L);
    if (this.obsOn(api)) s.dmin = this.dist(api, s.th, 0).d;
  },
  obsOn(api) { return api.p.mode <= 1; },
  update(dt, api, s) {
    if (!s.ok) { api.stop(); return; }
    const g = this.cfg(api), m = api.p.mode;
    for (let n = 0; n < 25 && !s.done; n++) {
      const th = s.th, J = this.jac(th, g.L), e = this.pts(th, g.L)[3];
      let qd = this.pinvTimes(J, [this.KP * (g.P[0] - e[0]), this.KP * (g.P[1] - e[1])]);
      if (m <= 1) {
        const r = this.dist(api, th, s.t);
        s.dmin = Math.min(s.dmin, r.d);
        if (m === 1 && r.d < api.p.da) {
          const P = this.pts(th, g.L), u0 = [r.x[0] - r.o.c[0], r.x[1] - r.o.c[1]], un = Math.hypot(...u0), u = [u0[0] / un, u0[1] / un];
          const a = [0, 1, 2].map((j) => (j <= r.k ? u[0] * -(r.x[1] - P[j][1]) + u[1] * (r.x[0] - P[j][0]) : 0));
          const A1 = this.proj(J, a), aq = a.reduce((v, x, i) => v + x * qd[i], 0);
          const want = u[0] * r.o.cd[0] + u[1] * r.o.cd[1] + this.KD * (api.p.da - r.d), den = A1.reduce((v, x) => v + x * x, 0) + this.LAM * this.LAM;
          qd = qd.map((x, i) => x + A1[i] / den * (want - aq));
        }
      } else if (m === 2) {
        const gH = th.map((x, i) => { const lo = this.rad(this.LO[i]), hi = this.rad(this.HI[i]); return 2 * (x - (lo + hi) / 2) / ((hi - lo) * (hi - lo)); });
        const z = this.proj(J, gH); qd = qd.map((x, i) => x - api.p.k * z[i]);
      } else {
        const hh = 1e-6, gw = [0, 1, 2].map((j) => { const p = th.slice(), q = th.slice(); p[j] += hh; q[j] -= hh; return (this.manip(p, g.L) - this.manip(q, g.L)) / (2 * hh); });
        const z = this.proj(J, gw); qd = qd.map((x, i) => x + api.p.k * z[i]);
      }
      s.err = Math.max(s.err, Math.hypot(e[0] - g.P[0], e[1] - g.P[1]));
      s.th = th.map((x, i) => x + this.DT * qd[i]); s.t += this.DT;
      if (Math.round(s.t / this.DT) % 10 === 0) s.trail.push(this.pts(s.th, g.L)[1]);
      if (s.t >= this.TEND - 1e-9) { s.done = true; api.stop(); }
    }
  },
  readouts(api, s) {
    const g = this.cfg(api), m = api.p.mode;
    if (!s.ok) return [[["起始形态", "start configuration"], api.T("这个 φ₀ 下够不着，换一个", "unreachable for this φ₀, try another")]];
    const w = this.manip(s.th, g.L), mg1 = this.HI[0] - this.deg(s.th[0]);
    if (api.scene === "arm" && s.done) {
      if (m === 0 && s.dmin < 0) api.done("hit");
      if (m === 1 && Math.abs(api.p.da - 0.1) < 1e-9 && s.dmin > 0.02 && s.err < 1e-3) api.done("avoid");
      if (m === 1 && api.p.da < 0.04 + 1e-9 && s.dmin > 0) api.done("small");
      if (m === 2 && api.p.phi0 === -60 && mg1 > 6 && s.err < 1e-3) api.done("lim");
      if (m === 3 && api.p.phi0 === 150 && w >= 1.1 * s.w0 && s.err < 1e-3) api.done("manip");
    }
    if (api.scene === "cup" && s.done && m === 1 && s.dmin > 0 && s.err < 1e-3) api.done("cup");
    const rows = [[["时间", "time"], s.t.toFixed(2) + " s"], [["末端（杯子）的最大误差", "largest tip (cup) error"], (s.err * 1000).toExponential(2) + " mm"]];
    if (m <= 1) rows.push([["到障碍物的最小距离", "minimum distance to the obstacle"], s.dmin.toFixed(3) + " m" + (s.dmin < 0 ? api.T("（碰到了）", " (contact)") : "")]);
    rows.push([["θ₁, θ₂, θ₃", "θ₁, θ₂, θ₃"], s.th.map((x) => this.deg(x).toFixed(1) + "°").join(", ")]);
    if (api.scene === "arm") {
      rows.push([["关节 1 离上限 70°", "joint 1 below its 70° limit"], mg1.toFixed(1) + "°"]);
      rows.push([["可操作度 w / 起始值", "manipulability w / start value"], `${w.toFixed(4)} m² / ${s.w0.toFixed(4)} m²（${(100 * (w / s.w0 - 1)).toFixed(1)}%）`]);
    }
    rows.push([["状态", "status"], s.done ? api.T("结束", "finished") : api.running ? api.T("运行中", "running") : "—"]);
    return rows;
  },
  draw(api, s) {
    const { w, h, ctx } = api, g = this.cfg(api), arm = api.scene === "arm";
    const sc = arm ? Math.min(w * 0.6 / 0.9, h * 0.85 / 1.0) : Math.min(w * 0.6 / 0.7, h * 0.85 / 0.8);
    const ox = arm ? w * 0.18 : w * 0.25, oy = arm ? h * 0.82 : h * 0.62, X = (q) => [ox + sc * q[0], oy - sc * q[1]];
    if (!arm) {   // 门框与人（俯视）
      api.rect(ox - sc * 0.25, oy - sc * 0.75, sc * 0.06, sc * 0.55, api.css("--line")); api.rect(ox + sc * 0.62, oy - sc * 0.75, sc * 0.06, sc * 0.55, api.css("--line"));
      api.circle(ox - 22, oy + 10, 24, null, api.css("--muted"));
    }
    if (arm && api.p.mode === 2) {   // 关节 1 的允许范围
      ctx.fillStyle = "rgba(31,111,235,0.10)"; ctx.beginPath(); ctx.moveTo(ox, oy); ctx.arc(ox, oy, 60, -this.rad(this.HI[0]), -this.rad(this.LO[0])); ctx.closePath(); ctx.fill();
      api.label(api.T("关节 1 的允许范围", "joint 1 range"), ox + 64, oy - 60, api.css("--muted"), 11);
    }
    const P0 = X(g.P); api.circle(P0[0], P0[1], 6, api.css("--red"));
    if (s.trail.length > 1) { ctx.strokeStyle = api.css("--amber"); ctx.lineWidth = 2; ctx.beginPath();
      s.trail.forEach((q, i) => { const [x, y] = X(q); if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); }); ctx.stroke(); }
    if (s.ok) {
      const P = this.pts(s.th, g.L).map(X), wd = arm ? [11, 9, 5] : [9, 8, 5];
      for (let i = 0; i < 3; i++) api.line(P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], api.css("--blue"), wd[i]);
      for (let i = 0; i < 3; i++) api.circle(P[i][0], P[i][1], 5, api.css("--panel"), api.css("--ink"));
      if (!arm) { api.rect(P[3][0] - 8, P[3][1] - 8, 16, 16, "rgba(88,166,255,0.45)", api.css("--ink"), 4); }
    }
    if (arm) api.rect(ox - 14, oy + 6, 28, 9, api.css("--muted"));
    if (this.obsOn(api)) {
      const o = this.obstacle(api, s.t), C = X(o.c), d = s.ok ? this.dist(api, s.th, s.t).d : 1;
      ctx.fillStyle = d < 0 ? "rgba(207,34,46,0.85)" : "rgba(207,34,46,0.45)"; ctx.beginPath(); ctx.arc(C[0], C[1], sc * g.R, 0, 2 * Math.PI); ctx.fill();
      if (api.p.mode === 1) { ctx.strokeStyle = api.css("--red"); ctx.setLineDash([4, 4]); ctx.beginPath(); ctx.arc(C[0], C[1], sc * (g.R + api.p.da), 0, 2 * Math.PI); ctx.stroke(); ctx.setLineDash([]); }
      if (!arm) api.label(api.T("路过的人", "passer-by"), C[0] + sc * g.R + 6, C[1], api.css("--muted"), 12);
    }
  },
});
