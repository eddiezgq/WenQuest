// 实验 44.7 扫描隧道显微镜（配 44.7 节）。隧穿电流 I = I₀ e^{−2κd}，κ = √(2mₑφ)/ħ（式 (44.7.1)、(44.7.2)）。
// “逼近曲线”场景：未知样品的逸出功（学生不知道，与正文算例不同），电流读数有 3% 的随机误差；记录的数据放在闭包里，重置时不丢。
// “恒流扫描”场景：针尖在积分反馈下扫过 3 nm 的石墨表面（原子起伏 0.02 nm、晶格 0.246 nm，1.6 nm 处一个 0.335 nm 的台阶）。
const C47 = 0.0380998212, PHI47 = 4.8, I047 = 1.0e4;           // eV·nm²；未知样品的逸出功 eV；nA
const K47 = Math.sqrt(PHI47 / C47);
const rec47 = { pts: [] };                                     // (d, I 读数)
const read47 = (d) => {
  const g = Math.sqrt(-2 * Math.log(1 - Math.random())) * Math.cos(2 * Math.PI * Math.random());
  const I = I047 * Math.exp(-2 * K47 * d) * (1 + 0.03 * g);
  return [d, Number(I.toPrecision(3))];
};
const ok47 = (api) => rec47.pts.length >= 8 && new Set(rec47.pts.map((p) => p[0].toFixed(2))).size >= 5 && Math.abs(api.p.phihat - PHI47) / PHI47 < 0.05;   // 至少 5 个不同的间隙
const surf47 = (x) => 0.02 * Math.cos(2 * Math.PI * x / 0.246) + (x > 1.6 ? 0.335 : 0);
const KS47 = Math.sqrt(4.5 / C47), D047 = 0.6;                 // 扫描用的针尖与样品（逸出功 4.5 eV），设定间隙 0.6 nm

WQ.lab({
  title: ["实验 44.7 扫描隧道显微镜", "Lab 44.7 The scanning tunnelling microscope"],
  goal: ["测一条逼近曲线，用最小二乘拟合求未知样品的逸出功及其不确定度；再调恒流扫描的反馈增益，看针尖怎样描出原子和原子台阶。",
         "Measure an approach curve and fit the unknown sample's work function with its uncertainty; then tune the constant-current feedback gain and watch the tip trace atoms and an atomic step."],
  scenes: [
    { id: "approach", robot: true, name: ["逼近曲线（测逸出功）", "Approach curve (work function)"], hide: ["gain", "speed"],
      problem: { title: ["机器人问题：纳米尺度的“位置传感器”", "Robot problem: a position sensor at the nanometre scale"],
                 text: ["STM 用隧穿电流感知针尖与表面的距离。先标定这个“传感器”：电流怎样随间隙变化？由此求出样品的逸出功。",
                        "The STM senses the tip–surface distance through the tunnelling current. Calibrate this sensor first: how does the current depend on the gap? Find the sample's work function from it."] } },
    { id: "scan", robot: true, name: ["恒流扫描（反馈控制）", "Constant-current scan (feedback)"], hide: ["d", "phihat"],
      problem: { title: ["机器人问题：最精密的位置闭环", "Robot problem: the finest position loop"],
                 text: ["积分反馈控制器按 ln(I/I_set) 调节压电陶瓷，使电流不变，针尖就描出表面的起伏。增益太小跟不上，太大会振荡。",
                        "The controller drives the piezo by ln(I/I_set) to hold the current constant, so the tip traces the surface. Too little gain lags; too much oscillates."] } },
  ],
  params: [
    { id: "d", name: ["间隙 d", "Gap d"], min: 0.3, max: 1.0, step: 0.01, value: 0.6, unit: "nm", digits: 2 },
    { id: "phihat", name: ["你算出的 φ", "Your φ"], min: 3, max: 6, step: 0.01, value: 4.0, unit: "eV", digits: 2 },
    { id: "gain", name: ["积分增益", "Integral gain"], min: 0.02, max: 2.4, step: 0.02, value: 0.1, digits: 2 },
    { id: "speed", name: ["动画速度（每帧采样点数，不影响结果）", "Animation speed (samples per frame; does not change the result)"], min: 1, max: 20, step: 1, value: 6, digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始扫描", "Scan"], primary: true }, { id: "reset", name: ["重置", "Reset"] },
            { id: "record", name: ["读数并记录", "Read and record"] }, { id: "sweep", name: ["0.40–0.70 nm 依次测一遍", "Sweep 0.40–0.70 nm"] },
            { id: "clear", name: ["清空记录", "Clear records"] }],
  legend: [{ color: "var(--blue)", name: ["记录的数据 / 表面", "recorded data / surface"] }, { color: "var(--red)", name: ["针尖高度", "tip height"] }],
  tasks: [
    { id: "phi", robot: true, text: ["逼近曲线：至少记录 8 个点，自己拟合 ln I–d 直线求出逸出功（至少 5 个不同的间隙），把“你算出的 φ”调到与真实值相差 5% 以内。",
                                      "Approach curve: record at least 8 points, fit ln I against d yourself, and set “Your φ” within 5% of the true value."],
      demo: { scene: "approach", set: { phihat: 4.8 }, press: ["clear", "sweep"], wait: 1 } },
    { id: "step", robot: true, text: ["恒流扫描：扫完一行，针尖高度在台阶两侧相差约 0.335 nm（误差 0.03 nm 以内）。", "Scan a line: the tip height differs by about 0.335 nm across the step (within 0.03 nm)."],
      demo: { scene: "scan", set: { gain: 0.5, speed: 20 }, press: ["start"], wait: 4 } },
    { id: "tune", robot: true, text: ["调增益，使跟踪误差的均方根小于 5 pm（台阶后 0.05 nm 内不计）：既跟得上原子起伏和台阶，又不振荡。", "Tune the gain so that the RMS tracking error is below 5 pm (the first 0.05 nm after the step excluded): fast enough for the atoms and the step, without oscillating."],
      demo: { scene: "scan", set: { gain: 0.8, speed: 20 }, press: ["start"], wait: 4 } },
  ],
  think: ["逼近曲线为什么要在对数坐标上拟合？如果直接对 I–d 作最小二乘拟合会有什么问题？",
          "Why fit the approach curve on a logarithmic scale? What goes wrong if you fit I against d directly?"],

  reset(api, s) { s.i = 0; s.xs = []; s.zs = []; s.err2 = 0; s.n = 0; s.z = surf47(0) + D047; s.last = rec47.pts[rec47.pts.length - 1] || null; },
  update(dt, api, s) {
    if (api.scene !== "scan") { api.stop(); return; }
    const M = 600, Iset = Math.exp(-2 * KS47 * D047);
    for (let k = 0; k < api.p.speed && s.i < M; k++, s.i++) {
      const x = 3 * s.i / (M - 1), sx = surf47(x);
      const g = Math.sqrt(-2 * Math.log(1 - Math.random())) * Math.cos(2 * Math.PI * Math.random());
      const I = Math.exp(-2 * KS47 * Math.max(0.05, s.z - sx)) * (1 + 0.01 * g);
      s.z += api.p.gain * Math.log(I / Iset) / (2 * KS47);           // 积分反馈
      s.z = Math.max(sx + 0.05, Math.min(sx + 1.5, s.z));            // 压电陶瓷的行程有限；针尖不能撞进样品
      s.xs.push(x); s.zs.push(s.z);
      if (!(x > 1.6 && x < 1.65)) { const e = s.z - sx - D047; s.err2 += e * e; s.n++; }   // 台阶后 0.05 nm 内的过渡不计
    }
    if (s.i >= M) { api.stop(); fin47(api, s); }
  },
  action(id, api, s) {
    if (api.scene !== "approach") return;
    if (id === "clear") rec47.pts.length = 0;
    if (id === "record") rec47.pts.push(read47(api.p.d));
    if (id === "sweep") for (let k = 0; k <= 10; k++) rec47.pts.push(read47(Math.round((0.4 + 0.03 * k) * 100) / 100));
    s.last = rec47.pts[rec47.pts.length - 1] || null;
    if (ok47(api)) api.done("phi");
  },
  change(api, s, pid) { if (pid === "phihat" && ok47(api)) api.done("phi"); },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "approach") {
      return [[["偏压", "Bias"], "0.1 V"], [["间隙 d", "Gap d"], f(api.p.d, 2) + " nm"],
              [["最近一次电流读数", "Last current reading"], s.last ? s.last[1] + " nA" : "—"],
              [["已记录点数", "Points recorded"], String(rec47.pts.length)]];
    }
    const rms = s.n ? Math.sqrt(s.err2 / s.n) * 1000 : 0;
    return [[["扫描位置", "Position"], f(s.xs.length ? s.xs[s.xs.length - 1] : 0, 2) + " nm"],
            [["针尖高度", "Tip height"], f(s.z, 3) + " nm"], [["跟踪误差均方根（台阶处除外）", "RMS tracking error (step excluded)"], s.n ? f(rms, 1) + " pm" : "—"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    if (api.scene === "approach") {
      // 左：针尖与样品；右：记录的 ln I–d 点
      const cx = w * 0.18, base = h * 0.75, ppn = h * 0.5;            // 1 nm = ppn 像素
      api.rect(cx - 90, base, 180, 20, css("--blue"));
      for (let i = -4; i <= 4; i++) api.circle(cx + i * 20, base, 8, css("--blue"), css("--ink"));
      const ty = base - 8 - api.p.d * ppn;
      api.ctx.fillStyle = css("--muted"); api.ctx.beginPath(); api.ctx.moveTo(cx - 30, ty - 120); api.ctx.lineTo(cx + 30, ty - 120); api.ctx.lineTo(cx, ty); api.ctx.closePath(); api.ctx.fill();
      api.circle(cx, ty - 8, 8, css("--muted"), css("--ink"));
      api.line(cx + 40, ty, cx + 40, base - 8, css("--orange"), 1, [4, 3]);
      api.label("d", cx + 46, (ty + base) / 2, css("--orange"), 13);
      const P = api.plot(w * 0.42, 24, w * 0.54, h - 64, [{ pts: [], color: css("--blue") }],
                         { xmin: 0.3, xmax: 1.0, ymin: -9, ymax: 3, xlabel: "d / nm", ylabel: "ln(I / nA)" });
      rec47.pts.forEach((p) => api.circle(P.X(p[0]), P.Y(Math.log(p[1])), 4, css("--blue"), css("--ink")));
      return;
    }
    const surf = [];
    for (let i = 0; i <= 300; i++) { const x = 3 * i / 300; surf.push([x, surf47(x)]); }
    const P = api.plot(w * 0.06, 20, w * 0.9, h - 60, [{ pts: surf, color: css("--blue") }, { pts: s.xs.map((x, i) => [x, s.zs[i]]), color: css("--red") }],
                       { xmin: 0, xmax: 3, ymin: -0.1, ymax: 1.3, xlabel: "x / nm", ylabel: api.T("高度 / nm", "height / nm") });
    if (s.xs.length) { const i = s.xs.length - 1; api.circle(P.X(s.xs[i]), P.Y(s.zs[i]), 5, css("--red"), css("--ink")); }
  },
});

function fin47(api, s) {
  const M = s.zs.length, a = s.zs.slice(20, 200), b = s.zs.slice(M - 180, M - 20);
  const mean = (v) => v.reduce((t, x) => t + x, 0) / v.length;
  if (Math.abs(mean(b) - mean(a) - 0.335) < 0.03) api.done("step");
  if (Math.sqrt(s.err2 / s.n) < 0.005) api.done("tune");
}
