// 实验 22.2 梯形与 S 形速度曲线（配 22.2 节）。
// 场景 1（机器人）：UR5e 的关节 1 带着弹性末端（俯视）。梯形曲线按式 (22.2.2)、(22.2.3)；S 形曲线按定理 22.2.2：
//   同一 v′、a 的梯形曲线用宽 t_j 的盒形窗滑动平均，v′ 由式 (22.2.10) 求出（j = a/t_j），T_S = L/v′ + v′/a + t_j。
//   末端的扭转模态 φ'' + 2ζωφ' + ω²φ = −θ̈（式 (22.2.6)），f_n = 8 Hz、ζ = 0.02，TCP 离轴 0.442 m（算例 22.2.2，示意值）；
//   用 0.5 ms 步长的经典龙格-库塔法积分，运动结束后的振幅 A = √(x² + ((ẋ + ζωx)/ω_d)²)，衰减到 0.05 mm 的等待时间 ln(A/0.05)/(ζω)。
// 场景 2（生活）：电梯上升 30 m，速度、加速度上限可调，加加速度 j = a/t_j。
// 手臂按实际时间的一半速度播放（运动后再演示 2.5 s 的振动）；电梯快放 3 倍。
WQ.lab({
  title: ["实验 22.2 梯形与 S 形速度曲线", "Lab 22.2 Trapezoidal and S-curve velocity profiles"],
  goal: ["用梯形和 S 形速度曲线规划点到点运动，比较运动时间和停下后的残余振动，学会按固有频率选择 t_j。",
         "Plan point-to-point motions with trapezoidal and S-curve profiles, compare the motion time and the residual vibration after stopping, and learn to choose t_j from the natural frequency."],
  scenes: [
    { id: "arm", robot: true, name: ["关节 1 带弹性末端", "Joint 1 with a flexible tip"], hide: ["lv", "la"],
      problem: { title: ["机器人问题：停在卡盘前，轴还在晃", "Robot problem: stopped in front of the chuck, the shaft still shakes"],
                 text: ["关节 1 转过约 103°。末端有一个 8 Hz 的弹性模态（示意值）。振幅降到 0.05 mm 以下才能把轴送进卡盘。",
                        "Joint 1 turns about 103°. The tip has an 8 Hz flexible mode (illustrative). The shaft may enter the chuck only when the vibration is below 0.05 mm."] } },
    { id: "lift", name: ["电梯", "Lift"], hide: ["dq", "vmax", "amax"],
      params: { tj: { min: 0.1, max: 2, value: 0.5, step: 0.05 } },
      problem: { title: ["生活中的例子：电梯怎样起动才舒服", "Everyday example: a comfortable start for a lift"],
                 text: ["电梯上升 30 m。乘客对加速度的突变很敏感，加加速度 j = a/t_j 不宜超过 1.5 m/s³（示意值）。",
                        "The lift rises 30 m. Passengers feel sudden changes of acceleration; the jerk j = a/t_j should stay below 1.5 m/s³ (illustrative)."] } },
  ],
  params: [
    { id: "prof", name: ["曲线：0 梯形 / 1 S 形", "Profile: 0 trapezoid / 1 S-curve"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "dq", name: ["转角 Δθ₁", "Rotation Δθ₁"], min: 5, max: 180, step: 0.1, value: 103.4, unit: "°", digits: 1 },
    { id: "vmax", name: ["速度上限", "Velocity limit"], min: 30, max: 180, step: 1, value: 180, unit: "°/s", digits: 0 },
    { id: "amax", name: ["加速度上限", "Acceleration limit"], min: 1, max: 12, step: 0.1, value: 6, unit: "rad/s²", digits: 1 },
    { id: "tj", name: ["加加速度段时长 t_j", "Jerk time t_j"], min: 0.02, max: 0.3, step: 0.005, value: 0.1, unit: "s", digits: 3 },
    { id: "lv", name: ["电梯额定速度", "Lift rated speed"], min: 0.5, max: 3, step: 0.1, value: 2.5, unit: "m/s", digits: 1 },
    { id: "la", name: ["电梯加速度上限", "Lift acceleration limit"], min: 0.3, max: 1.5, step: 0.05, value: 1.0, unit: "m/s²", digits: 2 },
  ],
  legend: [{ color: "#2ca02c", name: ["梯形", "trapezoid"] }, { color: "#8e6bbf", name: ["S 形", "S-curve"] }],
  tasks: [
    { id: "trap", robot: true, text: ["梯形曲线转过约 103°（限值取默认），运行一次，读出运动时间和残余振幅。",
                                       "Trapezoid, about 103° (default limits): run it once and read the motion time and the residual amplitude."],
      demo: { scene: "arm", set: { prof: 0, dq: 103.4, vmax: 180, amax: 6 }, press: ["start"], wait: 20 } },
    { id: "tri", robot: true, text: ["减小转角，使梯形曲线变成三角形（达不到速度上限）。", "Reduce the rotation until the trapezoid becomes a triangle (the velocity limit is not reached)."],
      demo: { scene: "arm", set: { prof: 0, dq: 30 }, press: [], wait: 3 } },
    { id: "scurve", robot: true, text: ["S 形曲线、转角约 103°、限值默认：残余振幅小于 0.05 mm，运动时间不超过 1.3 s。",
                                         "S-curve, about 103°, default limits: residual amplitude below 0.05 mm with a motion time of at most 1.3 s."],
      demo: { scene: "arm", set: { prof: 1, dq: 103.4, vmax: 180, amax: 6, tj: 0.125 }, press: [], wait: 3 } },
    { id: "lift", text: ["电梯：S 形曲线，加速度不超过 1.0 m/s²、加加速度不超过 1.5 m/s³，在 16 s 以内到达，并运行一次。",
                         "Lift: S-curve with acceleration ≤ 1.0 m/s² and jerk ≤ 1.5 m/s³, arriving within 16 s; run it once."],
      demo: { scene: "lift", set: { prof: 1, lv: 2.5, la: 1.0, tj: 0.7 }, press: ["start"], wait: 14 } },
  ],
  think: ["任务 3 中把 t_j 从 0.125 s 加大到 0.18 s，残余振幅变大了。可是加加速度更小了，为什么振动反而更大？",
          "In task 3, raising t_j from 0.125 s to 0.18 s makes the residual amplitude larger although the jerk is smaller. Why?"],

  FN: 8, ZETA: 0.02, R: 0.442, TOL: 0.05, MAG: 150,
  // 一个坐标从 0 到 L 的运动：返回 {T, acc(t), vel(t), pos(t), vp}
  plan(L, v, a, prof, tj) {
    const trap = (vv) => {
      let ta, tc, vp;
      if (L >= vv * vv / a) { vp = vv; ta = vv / a; tc = L / vv - vv / a; } else { vp = Math.sqrt(a * L); ta = vp / a; tc = 0; }
      const T = 2 * ta + tc;
      const acc = (t) => (t < 0 || t > T ? 0 : t < ta ? a : t < ta + tc ? 0 : -a);
      const vel = (t) => (t <= 0 ? 0 : t >= T ? 0 : t < ta ? a * t : t < ta + tc ? vp : a * (T - t));
      const pos = (t) => (t <= 0 ? 0 : t >= T ? L : t < ta ? 0.5 * a * t * t : t < ta + tc ? 0.5 * vp * ta + vp * (t - ta) : L - 0.5 * a * (T - t) ** 2);
      return { T, ta, tc, vp, acc, vel, pos };
    };
    if (prof === 0) return Object.assign(trap(v), { j: Infinity });
    // S 形：v′ 满足 v′²/a + v′ t_j = L（达不到 v 时），否则 v′ = v；再检查 v′ ≥ a t_j（能达到 a）
    let vp = v;
    if (L < v * (v / a + tj)) vp = (-tj + Math.sqrt(tj * tj + 4 * L / a)) / (2 / a);
    const P = trap(vp), n = 24;
    const avg = (f, t) => { let s = 0; for (let i = 0; i <= n; i++) s += f(t - tj * i / n) * (i === 0 || i === n ? 0.5 : 1); return s / n; };
    const pos = (t) => { if (t <= 0) return 0; if (t >= P.T + tj) return L; return avg(P.pos, t); };
    return { T: P.T + tj, vp: P.vp, j: a / tj, ta: P.ta, tc: P.tc, acc: (t) => (P.vel(t) - P.vel(t - tj)) / tj,
             vel: (t) => (P.pos(t) - P.pos(t - tj)) / tj, pos, jerk: (t) => (P.acc(t) - P.acc(t - tj)) / tj };
  },
  current(api) {
    if (api.scene === "lift") return this.plan(30, api.p.lv, api.p.la, api.p.prof, api.p.tj);
    return this.plan(api.p.dq * Math.PI / 180, api.p.vmax * Math.PI / 180, api.p.amax, api.p.prof, api.p.tj);
  },
  vibrate(P, extra) {                                  // φ'' + 2ζωφ' + ω²φ = −θ̈，RK4，步长 0.5 ms；返回采样与运动结束时的振幅
    const w = 2 * Math.PI * this.FN, z = this.ZETA, dt = 0.0005, n = Math.ceil((P.T + extra) / dt);
    let x = 0, v = 0, amp = null;
    const ts = [0], xs = [0];
    const f = (t, X, V) => [V, -P.acc(t) - 2 * z * w * V - w * w * X];
    for (let k = 0; k < n; k++) {
      const t = k * dt;
      if (amp === null && t >= P.T) { const wd = w * Math.sqrt(1 - z * z); amp = Math.hypot(x, (v + z * w * x) / wd) * this.R * 1000; }
      const k1 = f(t, x, v), k2 = f(t + dt / 2, x + dt / 2 * k1[0], v + dt / 2 * k1[1]);
      const k3 = f(t + dt / 2, x + dt / 2 * k2[0], v + dt / 2 * k2[1]), k4 = f(t + dt, x + dt * k3[0], v + dt * k3[1]);
      x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); v += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]);
      if ((k + 1) % 8 === 0) { ts.push(t + dt); xs.push(x * this.R * 1000); }
    }
    return { ts, xs, amp: amp === null ? 0 : amp };
  },

  reset(api, s) {
    s.clock = 0; s.ticked = false; s.P = this.current(api);
    if (api.scene === "arm") { s.V = this.vibrate(s.P, 2.5); s.settle = Math.max(0, Math.log(s.V.amp / this.TOL) / (this.ZETA * 2 * Math.PI * this.FN)); }
  },
  start(api, s) { s.clock = 0; s.ticked = false; },
  update(dt, api, s) {
    const P = s.P;
    if (api.scene === "arm") {
      s.clock += 0.5 * dt;
      if (s.clock >= P.T && !s.ticked) {
        s.ticked = true;
        if (api.p.prof === 0 && Math.abs(api.p.dq - 103.4) < 1.5 && api.p.vmax === 180 && Math.abs(api.p.amax - 6) < 1e-9) api.done("trap");
      }
      if (s.clock >= P.T + 2.5) { s.clock = P.T + 2.5; api.stop(); }
    } else {
      s.clock += 3 * dt;
      if (s.clock >= P.T) {
        s.clock = P.T; api.stop();
        if (api.p.prof === 1 && api.p.la <= 1.0 + 1e-9 && P.j <= 1.5 + 1e-9 && P.T <= 16 + 1e-9) api.done("lift");
      }
    }
  },
  readouts(api, s) {
    const P = s.P;
    if (!P) return [];
    const f = (x, d) => api.fmt(x, d);
    if (api.scene === "lift") {
      return [[["曲线", "profile"], api.p.prof ? api.T("S 形", "S-curve") : api.T("梯形", "trapezoid")],
              [["运行时间", "travel time"], f(P.T, 2) + " s"], [["最高速度", "top speed"], f(P.vp, 2) + " m/s"],
              [["加加速度 j = a/t_j", "jerk j = a/t_j"], api.p.prof ? f(P.j, 2) + " m/s³" : "∞"],
              [["高度", "height"], f(P.pos(Math.min(s.clock || 0, P.T)), 2) + " m"]];
    }
    const near = Math.abs(api.p.dq - 103.4) < 1.5 && api.p.vmax === 180 && Math.abs(api.p.amax - 6) < 1e-9;
    const L = api.p.dq * Math.PI / 180, v = api.p.vmax * Math.PI / 180;
    if (api.p.prof === 0 && L < v * v / api.p.amax) api.done("tri");
    if (api.p.prof === 1 && near && s.V.amp < this.TOL && P.T <= 1.3) api.done("scurve");
    return [[["曲线", "profile"], api.p.prof ? api.T("S 形", "S-curve") : (P.tc > 0 ? api.T("梯形", "trapezoid") : api.T("三角形", "triangle"))],
            [["运动时间", "motion time"], f(P.T, 4) + " s"],
            [["最高速度", "top speed"], f(P.vp * 180 / Math.PI, 1) + " °/s"],
            [["加加速度", "jerk"], api.p.prof ? f(P.j, 1) + " rad/s³" : "∞"],
            [["残余振幅", "residual amplitude"], f(s.V.amp, 4) + " mm"],
            [["等到 0.05 mm 还要", "wait until 0.05 mm"], f(s.settle, 2) + " s"],
            [["从起动到可以送料", "start to ready"], f(P.T + s.settle, 2) + " s"]];
  },
  draw(api, s) {
    const { w, h, ctx } = api, P = s.P;
    if (!P) return;
    const col = api.p.prof ? "#8e6bbf" : "#2ca02c", t = s.clock || 0;
    const px = w * 0.42, pw = w * 0.55;
    if (api.scene === "arm") {
      // 左：俯视的手臂与弹性末端（振动放大 150 倍）
      const cx = w * 0.17, cy = h * 0.6, R = Math.min(w * 0.17, h * 0.33), L = api.p.dq * Math.PI / 180;
      const a0 = -L / 2, ang = a0 + P.pos(Math.min(t, P.T));
      const k = Math.min(s.V.xs.length - 1, Math.round(t / 0.004)), x = s.V.xs[k] || 0;
      const tip = [cx + R * Math.cos(ang), cy - R * Math.sin(ang)];
      const m = [tip[0] + 26 * Math.cos(ang) - x / 1000 * this.MAG * R / 0.442 * Math.sin(ang), tip[1] - 26 * Math.sin(ang) - x / 1000 * this.MAG * R / 0.442 * Math.cos(ang)];
      ctx.strokeStyle = api.css("--muted"); ctx.setLineDash([4, 4]); ctx.beginPath(); ctx.arc(cx, cy, R, -a0, -(a0 + L), true); ctx.stroke(); ctx.setLineDash([]);
      api.circle(cx, cy, 14, api.css("--panel"), api.css("--ink"));
      api.line(cx, cy, tip[0], tip[1], col, 9);
      api.line(tip[0], tip[1], m[0], m[1], api.css("--muted"), 2);
      api.circle(m[0], m[1], 8, api.css("--amber"), api.css("--ink"));
      api.label(api.T("振动放大 150 倍", "vibration ×150"), cx - R * 0.6, cy + R * 0.95, api.css("--muted"), 12);
      api.label(t < P.T ? api.T("运动中", "moving") : api.T("已停下", "stopped"), cx - R * 0.6, h * 0.12, api.css("--ink"), 13);
    } else {
      const sx = w * 0.18, top = h * 0.08, bot = h * 0.9, H = 30;
      api.rect(sx - 34, top, 68, bot - top, null, api.css("--muted"));
      for (let k = 0; k <= 10; k++) api.line(sx - 42, bot - k * (bot - top) / 10, sx - 34, bot - k * (bot - top) / 10, api.css("--muted"), 1);
      const y = bot - P.pos(Math.min(t, P.T)) / H * (bot - top - 40);
      api.rect(sx - 26, y - 38, 52, 34, api.css("--accent"), null, 4);
      api.label("30 m", sx + 44, top + 8, api.css("--muted"), 12);
    }
    // 右：速度、加速度、加加速度、振动
    const T = P.T, Tp = api.scene === "arm" ? T + 2.5 : T, N = 240;
    const sc = api.scene === "arm" ? 180 / Math.PI : 1;
    const rows = [
      { f: (tt) => P.vel(tt) * sc, name: api.scene === "arm" ? api.T("速度 / (°/s)", "velocity / (°/s)") : api.T("速度 / (m/s)", "speed / (m/s)") },
      { f: (tt) => P.acc(tt), name: api.scene === "arm" ? api.T("加速度 / (rad/s²)", "acceleration / (rad/s²)") : api.T("加速度 / (m/s²)", "acceleration / (m/s²)") },
    ];
    if (api.scene === "arm") rows.push({ vib: true, name: api.T("末端振动 / mm（虚线 ±0.05）", "tip vibration / mm (dashed ±0.05)") });
    const ph = h * (api.scene === "arm" ? 0.26 : 0.4), gap = h * 0.05;
    rows.forEach((r, i) => {
      const y = h * 0.04 + i * (ph + gap);
      let pts;
      if (r.vib) { pts = s.V.ts.map((tt, k) => [tt, s.V.xs[k]]); } else pts = Array.from({ length: N + 1 }, (_, k) => [k / N * Tp, r.f(k / N * Tp)]);
      const ymax = Math.max(1e-6, ...pts.map((p) => Math.abs(p[1]))) * 1.15;
      const lo = i === 0 ? 0 : -ymax;
      const Pl = api.plot(px, y, pw, ph, [{ pts, color: col }], { xmin: 0, xmax: Tp, ymin: lo, ymax, ylabel: r.name });
      if (r.vib) { [0.05, -0.05].forEach((v) => api.line(px, Pl.Y(v), px + pw, Pl.Y(v), api.css("--muted"), 1, [4, 4])); }
      api.line(Pl.X(Math.min(t, Tp)), y, Pl.X(Math.min(t, Tp)), y + ph, api.css("--amber"), 1.2);
      if (!r.vib) api.line(Pl.X(T), y, Pl.X(T), y + ph, api.css("--muted"), 1, [2, 3]);
    });
  },
});
