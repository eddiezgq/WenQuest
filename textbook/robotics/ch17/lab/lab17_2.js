// 实验 17.2 零空间运动（配 17.2 节）。
// 场景 1（机器人）：平面 3R 臂 0.425、0.392、0.1 m，末端停在 A = (0.5, 0.3) m，起始形态取工具朝向 30°、θ₂ > 0 的解。
//   零空间矢量用广义叉积 c = (det J₍₁₎, −det J₍₂₎, det J₍₃₎)（式 (17.2.2)），dθ/ds = c/‖c‖（式 (17.2.4)）。
//   每步用中点法预测一步 h；“校正”为 1 时再做三次牛顿迭代 θ ← θ + J⁺(p_d − p)（17.2.4 节）。走满 20 rad 的弧长（约三圈）停止。
// 场景 2（机器人）：末端沿圆周（圆心 (0.5, 0.2) m，半径 0.15 m，4 s 一圈）运动，起始形态取工具朝向 −30°、θ₂ > 0 的解，
//   θ̇ = J⁺(ṗ_d + K_p(p_d − p)) + k_N(I − J⁺J)(θ₀ − θ)，K_p = 10 /s（式 (17.2.6)、(17.2.7)），四阶龙格-库塔法，步长 4 ms（算例 17.2.2）。
// 场景 3（生活）：从上往下看擦桌子：上臂 0.30 m、前臂 0.27 m、手 0.08 m，肩在原点，手沿圆心 (0.35, 0.15) m、半径 0.08 m 的圆
//   3 s 一圈，与场景 2 同一公式；k_N 表示“把胳膊放回舒服姿势”的倾向。
WQ.lab({
  title: ["实验 17.2 零空间运动", "Lab 17.2 Null-space motion"],
  goal: ["用广义叉积求零空间方向，让手臂沿自运动流形走，看预测-校正怎样防止末端漂离；再看伪逆控制为什么“手走一圈，手臂回不到原处”，以及零空间项怎样把它拉住。",
         "Use the generalized cross product for the null-space direction and move the arm along its self-motion manifold, seeing how prediction and correction keep the tip from drifting; then see why pseudoinverse control does not bring the arm back after a closed hand path, and how a null-space term holds it."],
  scenes: [
    { id: "self", robot: true, name: ["沿自运动流形走", "Walking along the self-motion manifold"], hide: ["kN", "nloops"],
      problem: { title: ["机器人问题：末端不动，怎样让手臂沿流形一直走下去而不偏离？", "Robot problem: with the tip fixed, how can the arm keep moving along the manifold without drifting off?"],
                 text: ["红点是固定的目标。按“开始”，手臂沿零空间矢量 c 走 20 rad 的弧长（约三圈）。选择步长 h 和是否校正，测量区给出末端离目标的最大漂移。",
                        "The red dot is the fixed goal. Press “Start”: the arm walks 20 rad of arc length (about three laps) along the null vector c. Choose the step h and whether to correct; the readouts give the largest drift of the tip from the goal."] } },
    { id: "circle", robot: true, name: ["末端画圆：伪逆的漂移", "Tip on a circle: pseudoinverse drift"], hide: ["h", "corr"],
      problem: { title: ["机器人问题：喷涂、打磨周而复始，手臂会不会越跑越偏？", "Robot problem: in repeated spraying or grinding, does the arm wander further and further?"],
                 text: ["末端一圈一圈地沿圆周运动。k_N = 0 时只用伪逆；k_N > 0 时加上把关节拉回起始形态的零空间项。测量区给出每圈结束时关节角相对起点的变化。",
                        "The tip goes round and round a circle. With k_N = 0 only the pseudoinverse is used; with k_N > 0 a null-space term pulls the joints back toward the start. The readouts give the change of the joint angles at the end of each lap."] } },
    { id: "wipe", name: ["擦桌子画圈", "Wiping a table in circles"], hide: ["h", "corr"],
      problem: { title: ["生活中的例子：反复画圈擦桌子，胳膊会慢慢变别扭", "Everyday example: wiping in circles, the arm slowly ends up in an awkward pose"],
                 text: ["从上往下看，手拿抹布沿同一个圆擦。k_N 是“把胳膊放回舒服姿势”的倾向。比较 k_N = 0 与 k_N > 0 时肩、肘每圈的变化。",
                        "Seen from above, the hand wipes round the same circle. k_N is the tendency to put the arm back into a comfortable pose. Compare the change of shoulder and elbow per lap for k_N = 0 and k_N > 0."] } },
  ],
  params: [
    { id: "h", name: ["步长 h", "step h"], min: 0.02, max: 0.3, step: 0.01, value: 0.1, unit: "rad", digits: 2 },
    { id: "corr", name: ["牛顿校正：0 不校正 / 1 校正", "Newton correction: 0 off / 1 on"], min: 0, max: 1, step: 1, value: 1, unit: "", digits: 0 },
    { id: "kN", name: ["零空间项的增益 k_N", "null-space gain k_N"], min: 0, max: 4, step: 0.5, value: 0, unit: "1/s", digits: 1 },
    { id: "nloops", name: ["圈数", "laps"], min: 1, max: 10, step: 1, value: 3, unit: "", digits: 0 },
  ],
  legend: [{ color: "#1f6feb", name: ["当前形态", "current configuration"] }, { color: "#8b949e", name: ["起始形态", "start configuration"] }, { color: "#cf222e", name: ["目标 / 路径", "goal / path"] }],
  tasks: [
    { id: "drift", robot: true, text: ["不校正、步长 h = 0.3 rad：走完 20 rad 后，末端最大漂移超过 2 mm。", "No correction, step h = 0.3 rad: after 20 rad the tip has drifted more than 2 mm."],
      demo: { scene: "self", set: { h: 0.3, corr: 0 }, press: ["start"], wait: 6 } },
    { id: "corr", robot: true, text: ["加校正：走完 20 rad，末端最大漂移小于 0.01 mm。", "With correction: after 20 rad the tip has drifted less than 0.01 mm."],
      demo: { scene: "self", set: { h: 0.1, corr: 1 }, press: ["start"], wait: 8 } },
    { id: "pinv", robot: true, text: ["只用伪逆（k_N = 0）转 3 圈：关节 3 累计变化超过 1.5°，末端误差小于 0.01 mm。", "Pseudoinverse only (k_N = 0), 3 laps: joint 3 has changed by more than 1.5° in total while the tip error stays below 0.01 mm."],
      demo: { scene: "circle", set: { kN: 0, nloops: 3 }, press: ["start"], wait: 8 } },
    { id: "rep", robot: true, text: ["加零空间项（k_N ≥ 1）转 6 圈以上：最后一圈关节角的变化小于 0.01°。", "With the null-space term (k_N ≥ 1), 6 laps or more: the joints change by less than 0.01° in the last lap."],
      demo: { scene: "circle", set: { kN: 2, nloops: 8 }, press: ["start"], wait: 12 } },
    { id: "wipe", text: ["擦桌子：k_N ≥ 1 擦 5 圈以上，最后一圈肩、肘的变化都小于 0.05°。", "Wiping: with k_N ≥ 1 for 5 laps or more, shoulder and elbow change by less than 0.05° in the last lap."],
      demo: { scene: "wipe", set: { kN: 2, nloops: 6 }, press: ["start"], wait: 10 } },
  ],
  think: ["只用伪逆时，关节为什么每圈都朝同一个方向漂？把圆的方向反过来，漂移的方向会怎样？用 c · (∇ × c) ≠ 0 解释。",
          "With the pseudoinverse alone, why do the joints drift the same way every lap? What happens to the drift if the circle is traversed the other way? Explain with c · (∇ × c) ≠ 0."],

  LR: [0.425, 0.392, 0.1], LH: [0.30, 0.27, 0.08],
  rad: (d) => d * Math.PI / 180, deg: (r) => r * 180 / Math.PI,
  wrap(a) { return Math.atan2(Math.sin(a), Math.cos(a)); },
  pts(th, L) { let a = 0; const P = [[0, 0]]; th.forEach((t, i) => { a += t; P.push([P[i][0] + L[i] * Math.cos(a), P[i][1] + L[i] * Math.sin(a)]); }); return P; },
  jac(th, L) { const P = this.pts(th, L), e = P[3]; return [[0, 1, 2].map((i) => -(e[1] - P[i][1])), [0, 1, 2].map((i) => e[0] - P[i][0])]; },
  cvec(J) { const d = (a, b) => J[0][a] * J[1][b] - J[0][b] * J[1][a]; return [d(1, 2), -d(0, 2), d(0, 1)]; },   // 广义叉积（式 (17.2.2)）
  pinvTimes(J, v) {   // Jᵀ(JJᵀ)⁻¹ v
    const a = J[0].reduce((s, x) => s + x * x, 0), b = J[0].reduce((s, x, i) => s + x * J[1][i], 0), d = J[1].reduce((s, x) => s + x * x, 0);
    const det = a * d - b * b, y = [(d * v[0] - b * v[1]) / det, (-b * v[0] + a * v[1]) / det];
    return [0, 1, 2].map((i) => J[0][i] * y[0] + J[1][i] * y[1]);
  },
  ik(L, p, phi, br) {
    const wx = p[0] - L[2] * Math.cos(phi), wy = p[1] - L[2] * Math.sin(phi);
    const c2 = (wx * wx + wy * wy - L[0] * L[0] - L[1] * L[1]) / (2 * L[0] * L[1]);
    const t2 = Math.acos(Math.max(-1, Math.min(1, c2))) * (br === 0 ? 1 : -1);
    const t1 = Math.atan2(wy, wx) - Math.atan2(L[1] * Math.sin(t2), L[0] + L[1] * Math.cos(t2));
    return [t1, t2, phi - t1 - t2];
  },
  cfg(api) {   // 各场景的数据
    if (api.scene === "self") return { L: this.LR, P: [0.5, 0.3] };
    if (api.scene === "circle") return { L: this.LR, C: [0.5, 0.2], R: 0.15, TP: 4.0, phi0: -30, br: 0 };
    return { L: this.LH, C: [0.35, 0.15], R: 0.08, TP: 3.0, phi0: 20, br: 1 };
  },
  unitC(th, L) { const c = this.cvec(this.jac(th, L)), n = Math.hypot(...c); return c.map((x) => x / n); },
  reset(api, s) {
    const g = this.cfg(api);
    s.t = 0; s.s = 0; s.lap = 0; s.ends = []; s.drift = 0; s.tipErr = 0; s.done = false; s.trail = [];
    if (api.scene === "self") s.th = this.ik(g.L, g.P, this.rad(30), 0);
    else s.th = this.ik(g.L, [g.C[0] + g.R, g.C[1]], this.rad(g.phi0), g.br);
    s.th0 = s.th.slice(); s.ends.push(s.th.slice());
  },
  f(api, s, th, t) {   // 场景 2、3 的关节速度 θ̇ = J⁺(ṗ_d + K_p(p_d − p)) + k_N (I − J⁺J)(θ₀ − θ)
    const g = this.cfg(api), a = 2 * Math.PI * t / g.TP, w = 2 * Math.PI / g.TP;
    const pd = [g.C[0] + g.R * Math.cos(a), g.C[1] + g.R * Math.sin(a)], vd = [-g.R * w * Math.sin(a), g.R * w * Math.cos(a)];
    const J = this.jac(th, g.L), e = this.pts(th, g.L)[3];
    let qd = this.pinvTimes(J, [vd[0] + 10 * (pd[0] - e[0]), vd[1] + 10 * (pd[1] - e[1])]);
    if (api.p.kN > 0) {   // 零空间投影：z 减去 J⁺Jz
      const z = th.map((x, i) => api.p.kN * (s.th0[i] - x));
      const r = this.pinvTimes(J, [J[0].reduce((u, x, i) => u + x * z[i], 0), J[1].reduce((u, x, i) => u + x * z[i], 0)]);
      qd = qd.map((x, i) => x + z[i] - r[i]);
    }
    return qd;
  },
  update(dt, api, s) {
    const g = this.cfg(api);
    if (api.scene === "self") {
      const h = api.p.h;
      for (let k = 0; k < 2 && s.s < 20 - 1e-9; k++) {
        const c1 = this.unitC(s.th, g.L), mid = s.th.map((x, i) => x + 0.5 * h * c1[i]), c2 = this.unitC(mid, g.L);
        s.th = s.th.map((x, i) => x + h * c2[i]); s.s += h;
        if (api.p.corr === 1) for (let it = 0; it < 3; it++) {
          const e = this.pts(s.th, g.L)[3], d = this.pinvTimes(this.jac(s.th, g.L), [g.P[0] - e[0], g.P[1] - e[1]]);
          s.th = s.th.map((x, i) => x + d[i]);
        }
        const e = this.pts(s.th, g.L)[3];
        s.drift = Math.max(s.drift, Math.hypot(e[0] - g.P[0], e[1] - g.P[1]));
        s.trail.push(this.pts(s.th, g.L)[1]);
      }
      if (s.s >= 20 - 1e-9) { s.done = true; api.stop(); }
      return;
    }
    const DT = 0.004, nPerLap = Math.round(g.TP / DT);
    for (let k = 0; k < 60 && !s.done; k++) {
      const t = s.t, th = s.th;
      const k1 = this.f(api, s, th, t), k2 = this.f(api, s, th.map((x, i) => x + DT / 2 * k1[i]), t + DT / 2);
      const k3 = this.f(api, s, th.map((x, i) => x + DT / 2 * k2[i]), t + DT / 2), k4 = this.f(api, s, th.map((x, i) => x + DT * k3[i]), t + DT);
      s.th = th.map((x, i) => x + DT / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
      s.t = t + DT;
      const a = 2 * Math.PI * s.t / g.TP, e = this.pts(s.th, g.L)[3];
      s.tipErr = Math.max(s.tipErr, Math.hypot(e[0] - g.C[0] - g.R * Math.cos(a), e[1] - g.C[1] - g.R * Math.sin(a)));
      if (Math.round(s.t / DT) % 25 === 0) s.trail.push(this.pts(s.th, g.L)[1]);
      if (Math.round(s.t / DT) % nPerLap === 0) { s.lap += 1; s.ends.push(s.th.slice()); if (s.lap >= api.p.nloops) { s.done = true; api.stop(); } }
    }
  },
  readouts(api, s) {
    const dg = (x) => this.deg(x).toFixed(3) + "°";
    if (api.scene === "self") {
      if (s.done && api.p.corr === 0 && Math.abs(api.p.h - 0.3) < 1e-9 && s.drift > 0.002) api.done("drift");
      if (s.done && api.p.corr === 1 && s.drift < 1e-5) api.done("corr");
      return [[["走过的弧长 s", "arc length s"], s.s.toFixed(2) + " rad"], [["末端最大漂移", "largest tip drift"], (s.drift * 1000).toExponential(2) + " mm"],
              [["θ₁, θ₂, θ₃", "θ₁, θ₂, θ₃"], s.th.map((x) => this.deg(this.wrap(x)).toFixed(1) + "°").join(", ")],
              [["零空间矢量的长度 ‖c‖ = w", "length of the null vector ‖c‖ = w"], Math.hypot(...this.cvec(this.jac(s.th, this.LR))).toFixed(4) + " m²"],
              [["状态", "status"], s.done ? api.T("走完 20 rad", "20 rad done") : api.running ? api.T("运动中", "moving") : "—"]];
    }
    const n = s.ends.length - 1, tot = s.th0.map((x, i) => s.ends[n][i] - x);
    const last = n >= 1 ? s.ends[n].map((x, i) => x - s.ends[n - 1][i]) : [NaN, NaN, NaN];
    const lastMax = Math.max(...last.map((x) => Math.abs(this.deg(x))));
    if (api.scene === "circle") {
      if (s.done && api.p.kN === 0 && n >= 3 && Math.abs(this.deg(tot[2])) > 1.5 && s.tipErr < 1e-5) api.done("pinv");
      if (s.done && api.p.kN >= 1 && n >= 6 && lastMax < 0.01) api.done("rep");
    } else if (s.done && api.p.kN >= 1 && n >= 5 && Math.abs(this.deg(last[0])) < 0.05 && Math.abs(this.deg(last[1])) < 0.05) api.done("wipe");
    return [[["完成的圈数", "laps done"], String(n)], [["末端（手）的最大误差", "largest tip (hand) error"], (s.tipErr * 1000).toExponential(2) + " mm"],
            [["关节角相对起点的变化", "change of the joints since the start"], n ? tot.map(dg).join(", ") : "—"],
            [["最后一圈的变化", "change during the last lap"], n ? last.map(dg).join(", ") : "—"],
            [["状态", "status"], s.done ? api.T("结束", "finished") : api.running ? api.T("运动中", "moving") : "—"]];
  },
  draw(api, s) {
    const { w, h, ctx } = api, g = this.cfg(api), human = api.scene === "wipe";
    const sc = human ? Math.min(w * 0.42 / 0.62, h * 0.78 / 0.62) : Math.min(w * 0.55 / 1.0, h * 0.85 / 0.95);
    const ox = human ? w * 0.22 : w * 0.12, oy = human ? h * 0.7 : h * 0.68, X = (q) => [ox + sc * q[0], oy - sc * q[1]];
    if (human) {   // 桌面和人（从上往下看）
      api.rect(ox - sc * 0.05, oy - sc * 0.5, sc * 0.6, sc * 0.55, "rgba(210,153,34,0.12)", api.css("--line"), 6);
      api.circle(ox - 20, oy + 22, 26, null, api.css("--muted")); api.label(api.T("人（俯视）", "person (top view)"), ox - 20, oy + 62, api.css("--muted"), 11, "center");
    }
    if (api.scene === "self") { const G = X(g.P); api.circle(G[0], G[1], 6, api.css("--red")); }
    else { ctx.strokeStyle = api.css("--red"); ctx.setLineDash([4, 4]); ctx.beginPath(); const C = X(g.C); ctx.arc(C[0], C[1], sc * g.R, 0, 2 * Math.PI); ctx.stroke(); ctx.setLineDash([]); }
    const draw = (th, col, wd) => { const P = this.pts(th, g.L).map(X);
      for (let i = 0; i < 3; i++) api.line(P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], col, wd[i]);
      for (let i = 0; i < 3; i++) api.circle(P[i][0], P[i][1], 4, api.css("--panel"), api.css("--ink")); };
    draw(s.th0, api.css("--muted"), [6, 5, 3]);
    if (s.trail.length > 1) { ctx.strokeStyle = api.css("--amber"); ctx.lineWidth = 1.5; ctx.beginPath();
      s.trail.forEach((q, i) => { const [x, y] = X(q); if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); }); ctx.stroke(); }
    draw(s.th, api.css("--blue"), [10, 8, 5]);
    if (!human) api.rect(ox - 14, oy + 6, 28, 9, api.css("--muted"));
    if (api.scene !== "self") {   // 右图：每圈结束时关节角相对起点的变化
      const n = s.ends.length - 1, pts = [0, 1, 2].map((j) => s.ends.map((q, k) => [k, this.deg(q[j] - s.th0[j])]));
      const lim = Math.max(1, ...pts.flat().map((p) => Math.abs(p[1]))) * 1.15;
      const gr = api.graph({ x: w * 0.66, y: h * 0.1, w: w * 0.3, h: h * 0.6, xmin: 0, xmax: Math.max(3, api.p.nloops), ymin: -lim, ymax: lim,
                             xlabel: api.T("圈数", "laps"), ylabel: api.T("Δθ / (°)", "Δθ / (°)") }).axes();
      [api.css("--red"), api.css("--green"), api.css("--blue")].forEach((c, j) => { if (n) gr.pts(pts[j], c, 2); gr.dots(pts[j], c, 3); });
      api.label("θ₁", w * 0.67, h * 0.76, api.css("--red"), 12); api.label("θ₂", w * 0.72, h * 0.76, api.css("--green"), 12); api.label("θ₃", w * 0.77, h * 0.76, api.css("--blue"), 12);
    }
  },
});
