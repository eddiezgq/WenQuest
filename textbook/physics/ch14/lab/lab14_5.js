// 实验 14.5 虚拟拉伸试验机：测钢和铝的弹性模量（配 14.5 节）。测量型实验。
// 材料的典型值取自数字工厂的材料库 factory/digital/cae/materials.py（出处见该文件），这一批试样的实测值与典型值略有不同（学生不知道）：
//   Q235：E = 201 GPa（典型值 206），σs = 235 MPa，σb = 440 MPa；6061-T6：E = 70.5 GPa（典型值 68.9），Rp0.2 = 276 MPa，Rm = 310 MPa；
//   未知材料（40Cr 调质，正文没有出现）：E = 210 GPa，Rp0.2 = 540 MPa，Rm = 735 MPa。
// 曲线形状与程序 14.5.1 相同：Q235 有屈服平台；6061-T6、40Cr 用 Ramberg–Osgood 模型 ε = σ/E + 0.002(σ/Rp0.2)ⁿ。
// 试样：直径 10.00 mm，引伸计标距 50.00 mm。读数：力（±5 N）、引伸计伸长量（±0.0005 mm）。
// 方式 0：加载到设定的力 F 并保持，读伸长量；方式 1：一直拉到断，画出 σ–ε 曲线，用“查看应变”读曲线上的应力。
const D145 = 10.0, L145 = 50.0, A145 = Math.PI * D145 * D145 / 4;          // mm, mm²
const MAT145 = [
  { E: 201000, sy: 235, su: 440, eu: 0.20, ef: 0.30, plateau: true },
  { E: 70500, sy: 276, su: 310, eu: 0.080, ef: 0.12 },
  { E: 210000, sy: 540, su: 735, eu: 0.10, ef: 0.16 },
];
MAT145.forEach((m) => { if (!m.plateau) m.n = Math.log((m.eu - m.su / m.E) / 0.002) / Math.log(m.su / m.sy); });
function h145(a) { const x = Math.sin(a * 17.913 + 0.77) * 43758.5453; return x - Math.floor(x); }
function sigma145(m, e) {                                                   // 工程应力（MPa）
  if (m.plateau) {
    const ey = 1.04 * m.sy / m.E;
    if (e <= ey) return m.E * e;
    if (e <= ey + 0.001) return 1.04 * m.sy - 0.04 * m.sy * (e - ey) / 0.001;
    if (e <= 0.018) return m.sy;
    if (e <= m.eu) { const u = (e - 0.018) / (m.eu - 0.018); return m.sy + (m.su - m.sy) * (1 - (1 - u) * (1 - u)); }
    return m.su - 0.20 * m.su * Math.pow((e - m.eu) / (m.ef - m.eu), 2);
  }
  if (e > m.eu) return m.su - 0.15 * m.su * Math.pow((e - m.eu) / (m.ef - m.eu), 2);
  let lo = 0, hi = m.su;                                                    // 由 ε(σ) 反解 σ
  for (let k = 0; k < 60; k++) { const mid = (lo + hi) / 2; (mid / m.E + 0.002 * Math.pow(mid / m.sy, m.n) < e) ? lo = mid : hi = mid; }
  return (lo + hi) / 2;
}
function strainAt145(m, s) {                                                // 加载到应力 s 时的应变（只用于弹性段附近）
  let lo = 0, hi = 0.05;
  for (let k = 0; k < 60; k++) { const mid = (lo + hi) / 2; sigma145(m, mid) < s ? lo = mid : hi = mid; }
  return (lo + hi) / 2;
}
const RUN145 = {};
const key145 = (p) => p.mode === 1 ? `${p.mat}|1` : `${p.mat}|0|${p.F}`;

WQ.lab({
  title: ["实验 14.5 虚拟拉伸试验机：测钢和铝的弹性模量", "Lab 14.5 Virtual tensile tester: Young's modulus of steel and aluminium"],
  goal: ["在弹性范围内测几组力和伸长量，求弹性模量；把试样拉断，读应力—应变曲线，用 0.2% 偏移法求未知材料的屈服强度。",
         "Measure several force–extension pairs in the elastic range to find Young's modulus; pull a specimen to fracture, read its stress–strain curve and find an unknown material's yield strength by the 0.2% offset method."],
  scenes: [
    { id: "tester", robot: true, name: ["拉伸试验机", "Tensile tester"], hide: [],
      problem: { title: ["机器人问题：连杆用钢还是用铝，先要知道它们有多“硬”", "Robot problem: steel or aluminium for a link? First find how stiff they are"],
                 text: ["机械臂连杆的变形取决于材料的弹性模量。试样直径 10.00 mm，引伸计标距 50.00 mm。方式 0：加载到设定的力并保持，读伸长量（只在弹性范围内做）；方式 1：一直拉到断，画出应力—应变曲线，拖动“查看应变”读曲线上的应力。材料 2 是一种未知的金属。",
                        "How much a robot link deforms depends on the material's Young's modulus. Specimen diameter 10.00 mm, extensometer gauge length 50.00 mm. Mode 0: load to the set force and hold, then read the extension (stay in the elastic range). Mode 1: pull to fracture, plot the stress–strain curve, and drag “Read strain” to read the stress on the curve. Material 2 is an unknown metal."] } },
  ],
  params: [
    { id: "mat", name: ["材料：0 Q235 钢，1 6061-T6 铝，2 未知", "Material: 0 Q235 steel, 1 6061-T6 aluminium, 2 unknown"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "mode", name: ["方式：0 加载到 F 并保持，1 拉到断", "Mode: 0 load to F and hold, 1 pull to fracture"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "F", name: ["设定的力 F", "Set force F"], min: 0, max: 20, step: 0.5, value: 5, unit: "kN", digits: 1 },
    { id: "er", name: ["查看应变（方式 1）", "Read strain (mode 1)"], min: 0, max: 1.0, step: 0.005, value: 0.4, unit: "%", digits: 3 },
    { id: "ans", name: ["你的结果", "Your result"], min: 0, max: 800, step: 0.1, value: 0, unit: "", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "Es", robot: true, text: ["测出这批 Q235 钢试样的弹性模量（GPa），调到“你的结果”，提交（相差 3% 以内）。", "Measure Young's modulus of this batch of Q235 steel (GPa), set it as “Your result” and submit (within 3%)."],
      demo: { scene: "tester", set: { mat: 0, mode: 0, F: 10, ans: 201 }, press: ["start", "submit"], wait: 2 } },
    { id: "Ea", robot: true, text: ["测出这批 6061-T6 铝合金试样的弹性模量（GPa），提交（相差 3% 以内）。", "Measure Young's modulus of this batch of 6061-T6 aluminium (GPa) and submit (within 3%)."],
      demo: { scene: "tester", set: { mat: 1, mode: 0, F: 10, ans: 70.5 }, press: ["start", "submit"], wait: 2 } },
    { id: "ys", robot: true, text: ["把未知材料拉断，用 0.2% 偏移法求它的屈服强度（MPa），提交（相差 5% 以内）。", "Pull the unknown material to fracture, find its yield strength by the 0.2% offset method (MPa) and submit (within 5%)."],
      demo: { scene: "tester", set: { mat: 2, mode: 1, ans: 540 }, press: ["start", "submit"], wait: 3 } },
  ],
  think: ["钢和铝的弹性模量差 3 倍，密度也差约 3 倍：同样重的拉杆，哪个伸长得少？未知材料的弹性模量与 Q235 相同，屈服强度和抗拉强度却高得多，伸长率较小，它可能是什么钢？加载时力超过多少，就不能再用方式 0 测弹性模量了？",
          "Steel and aluminium differ by about 3 in Young's modulus and also about 3 in density: for tie rods of equal weight, which stretches less? The unknown has the same modulus as Q235 but far higher yield and tensile strengths and less elongation: what kind of steel might it be? Above what force does mode 0 stop being valid for measuring E?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; s.e = 0; },
  start(api, s) { s.ran = true; s.k = Object.assign({}, api.p); },
  update(dt, api, s) {
    const p = api.p, m = MAT145[p.mat];
    if (p.mode === 0) { if (api.t >= 1.0) { RUN145[key145(p)] = true; api.stop(); } return; }
    const T = 4.0, u = Math.min(1, api.t / T);
    s.e = m.ef * Math.pow(u, 2.5);                                           // 开头慢，便于看清弹性段
    if (api.t >= T) { RUN145[key145(p)] = true; api.stop(); }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = s.ran && s.k ? Object.assign({}, s.k, { ans: api.p.ans }) : api.p, have = s.ran || RUN145[key145(p)]; let ok = false;
    if (have && p.mode === 0 && p.mat === 0 && Math.abs(p.ans - MAT145[0].E / 1000) <= 0.03 * MAT145[0].E / 1000) { api.done("Es"); ok = true; }
    if (have && p.mode === 0 && p.mat === 1 && Math.abs(p.ans - MAT145[1].E / 1000) <= 0.03 * MAT145[1].E / 1000) { api.done("Ea"); ok = true; }
    if (have && p.mode === 1 && p.mat === 2 && Math.abs(p.ans - MAT145[2].sy) <= 0.05 * MAT145[2].sy) { api.done("ys"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, m = MAT145[p.mat], sub = [["提交结果", "Submission"], s.msg || "—"], have = (s.ran && !api.running) || RUN145[key145(p)];
    if (p.mode === 0) {
      const sig = p.F * 1000 / A145, e = strainAt145(m, sig), broke = sig > m.su;
      const dL = e * L145 + (h145(p.mat * 100 + p.F * 3) - 0.5) * 0.001, Fr = p.F * 1000 + (h145(p.F * 7 + p.mat) - 0.5) * 10;
      return [[["力", "Force"], have ? (broke ? api.T("试样断了", "specimen broke") : f(Fr / 1000, 3) + " kN") : "—"],
              [["引伸计伸长量", "Extensometer reading"], have && !broke ? f(dL, 4) + " mm" : "—"], sub];
    }
    const er = p.er / 100, sr = sigma145(m, er), done = have;
    return [[["最大力", "Maximum force"], done ? f(m.su * A145 / 1000, 2) + " kN" : "—"],
            [["断后伸长率", "Elongation at break"], done ? f(m.ef * 100, 0) + "%" : "—"],
            [[`查看：ε = ${f(p.er, 3)}% 处的应力`, `Read: stress at ε = ${f(p.er, 3)}%`], done || (s.ran && s.e >= er) ? f(sr, 1) + " MPa" : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue"), p = api.p, m = MAT145[p.mat];
    const have = (s.ran && !api.running) || RUN145[key145(p)];
    const col = [red, blue, css("--green")][p.mat];
    const eNow = p.mode === 1 ? (have ? m.ef : s.e || 0) : (have || s.ran ? strainAt145(m, Math.min(p.F * 1000 / A145, m.su)) : 0);
    // 左：试样（伸长放大画出）
    const cx = w * 0.12, top = h * 0.15, L0 = h * 0.45, Lx = L0 * (1 + Math.min(eNow, 0.6) * 1.5);
    api.rect(cx - 30, top - 26, 60, 26, mut, ink, 3); api.rect(cx - 30, top + Lx, 60, 26, mut, ink, 3);
    api.rect(cx - 12, top, 24, Lx, col, ink, 2);
    api.label(api.T("试样", "specimen"), cx, top + Lx + 48, mut, 12, "center");
    // 右：σ–ε 曲线（方式 1）
    if (p.mode === 1) {
      const zoom = p.er <= 1.0;
      const G = api.graph({ x: w * 0.3, y: h * 0.1, w: w * 0.62, h: h * 0.72, xmin: 0, xmax: m.ef * 100 * 1.05, ymin: 0, ymax: 800,
                            xlabel: "ε / %", ylabel: "σ / MPa" }).axes();
      const pts = []; const eMax = have ? m.ef : (s.e || 0);
      for (let k = 0; k <= 400; k++) { const e = eMax * k / 400; pts.push([e * 100, sigma145(m, e)]); }
      if (pts.length > 1) G.pts(pts, col, 2);
      // 小图：开头 1% 放大
      const g2 = api.graph({ x: w * 0.62, y: h * 0.16, w: w * 0.26, h: h * 0.3, xmin: 0, xmax: 1.0, ymin: 0, ymax: 800, xlabel: "", ylabel: "" }).axes();
      const pz = []; for (let k = 0; k <= 200; k++) { const e = Math.min(eMax, 0.01) * k / 200; pz.push([e * 100, sigma145(m, e)]); }
      if (pz.length > 1) g2.pts(pz, col, 2);
      if (zoom && (have || (s.e || 0) >= p.er / 100)) g2.point(p.er, sigma145(m, p.er / 100), ink);
      api.label(api.T("开头 1% 放大", "first 1% enlarged"), w * 0.75, h * 0.14, mut, 11, "center");
      return;
    }
    api.label(api.T("方式 0：加载到设定的力后保持", "mode 0: load to the set force and hold"), w * 0.6, h * 0.5, mut, 13, "center");
  },
});
