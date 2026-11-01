// 实验 9.4 机械臂末端在负载下的下垂（配 9.4 节）。与程序 9.4.1 同一个模型（_ch9.arm_sag）：手臂水平伸直，各环叠加——
// 底座轴承倾斜 θ1 = T2/K_tilt、肩关节 J2 和肘关节 J3 的谐波减速器扭转（三段折线 K1–K3，分段点 T1、T2）、上臂管和小臂管当作悬臂梁弯曲
// （自重均布，端部受外侧的力和力矩）、肩关节输出轴 RJ-201 的扭转（第 33 章，线性）。转动环节对末端的贡献 = 转角 × 到末端的距离。
// 改管子截面或减速器规格时，自重的变化一并计入：管子的质量差按管长均布（铝 2.7 g/cm³），肘关节减速器部件的质量差加在肘关节处。
// UR5e 的连杆长度和质量取自零件库模型（程序 9.4.1 读出的值写在下面）；管子截面、底座轴承刚度是本书设定。
// 生活场景“伸缩自拍杆”：两节铝管，伸缩接头和手腕当作扭转弹簧（刚度是本书设定的示意值），没有减速器。
const UR9_4 = { L1: 425, L2: 392, LW: 100, mUA: 8.393, mFA: 2.275, mW: 2.6269, D1: 85, t1: 2.5, D2: 75, t2: 2, kRJ: 5.4829e5 };   // kRJ：程序 9.4.1 的 k_rj201()，N·m/rad
const STICK9_4 = { L1: 400, L2: 400, LW: 50, mUA: 0.060, mFA: 0.040, mW: 0.010, kJoint: 200, kHand: 30 };   // 简化为两节；质量按给定截面，不随参数变
const CSF9_4 = [ // 零件库 D-RDC-HD-CSF（K1–K3，10⁴ N·m/rad）；T1、T2 取样本值
  { name: "CSF-17-100", K: [1.0e4, 1.4e4, 1.6e4], T1: 3.9, T2: 12, m: 0.15 },
  { name: "CSF-25-100", K: [3.1e4, 5.0e4, 5.7e4], T1: 14, T2: 48, m: 0.42 },
  { name: "CSF-32-100", K: [6.7e4, 11e4, 12e4], T1: 29, T2: 108, m: 0.89 },
];
const E_AL9_4 = 68900, G9_4 = 9.81;
function windup9_4(T, k) {
  T = Math.abs(T);
  if (T <= k.T1) return T / k.K[0];
  if (T <= k.T2) return k.T1 / k.K[0] + (T - k.T1) / k.K[1];
  return k.T1 / k.K[0] + (k.T2 - k.T1) / k.K[1] + (T - k.T2) / k.K[2];
}
function Itube9_4(D, t) { return Math.PI / 64 * (D ** 4 - (D - 2 * t) ** 4); }
function Atube9_4(D, t) { return Math.PI / 4 * (D ** 2 - (D - 2 * t) ** 2); }
function cant9_4(L, EI, w, P, M) {
  return [w * L ** 4 / (8 * EI) + P * L ** 3 / (3 * EI) + M * L ** 2 / (2 * EI), w * L ** 3 / (6 * EI) + P * L ** 2 / (2 * EI) + M * L / EI];
}
function sag9_4(p, scene, m) {
  const A = scene === "stick" ? STICK9_4 : UR9_4, x = A.L1 + A.L2 + A.LW;
  const EI1 = E_AL9_4 * Itube9_4(p.D1, p.t1), EI2 = E_AL9_4 * Itube9_4(p.D2, p.t2);
  let mUA = A.mUA, mFA = A.mFA, mEl = 0;
  if (scene !== "stick") {
    mUA += (Atube9_4(p.D1, p.t1) - Atube9_4(A.D1, A.t1)) * A.L1 * 2.7e-6;
    mFA += (Atube9_4(p.D2, p.t2) - Atube9_4(A.D2, A.t2)) * A.L2 * 2.7e-6;
    mEl = CSF9_4[Math.round(p.size)].m - CSF9_4[1].m;
  }
  const Wp = m * G9_4, Ww = A.mW * G9_4, Wf = mFA * G9_4, Wu = mUA * G9_4, We = mEl * G9_4;
  const T3 = (Wf * A.L2 / 2 + Ww * A.L2 + Wp * (A.L2 + A.LW)) / 1e3;
  const T2 = (Wu * A.L1 / 2 + We * A.L1 + Wf * (A.L1 + A.L2 / 2) + Ww * (A.L1 + A.L2) + Wp * x) / 1e3;
  const fa = cant9_4(A.L2, EI2, Wf / A.L2, Ww + Wp, Wp * A.LW), ua = cant9_4(A.L1, EI1, Wu / A.L1, We + Wf + Ww + Wp, T3 * 1e3);
  let th1, th2, th3, thr = 0;
  if (scene === "stick") { th1 = T2 / A.kHand; th2 = 0; th3 = T3 / A.kJoint; }
  else { const k = CSF9_4[Math.round(p.size)]; th1 = T2 / (p.kt * 1e4); th2 = windup9_4(T2, k); th3 = windup9_4(T3, k); thr = T2 / A.kRJ; }
  const parts = { tilt: th1 * x, j2: th2 * x, rj: thr * x, ua: ua[0] + ua[1] * (A.L2 + A.LW), j3: th3 * (A.L2 + A.LW), fa: fa[0] + fa[1] * A.LW };
  const t0 = th1 + th2 + thr, yE = t0 * A.L1 + ua[0], sl = t0 + ua[1] + th3, yW = yE + sl * A.L2 + fa[0];
  return { parts, total: Object.values(parts).reduce((s, v) => s + v, 0), T2, T3, x, A, shape: [[0, 0], [A.L1, yE], [A.L1 + A.L2, yW]] };
}
const NAMES9_4 = {
  robot: { tilt: ["底座轴承倾斜", "base bearing tilt"], j2: ["肩关节减速器", "shoulder reducer"], rj: ["肩关节输出轴 RJ-201", "shoulder shaft RJ-201"], ua: ["上臂管弯曲", "upper-arm tube"], j3: ["肘关节减速器", "elbow reducer"], fa: ["小臂管弯曲", "forearm tube"] },
  stick: { tilt: ["手腕（握持）", "wrist (grip)"], j2: ["—", "—"], rj: ["—", "—"], ua: ["下节管弯曲", "lower tube"], j3: ["伸缩接头", "telescoping joint"], fa: ["上节管弯曲", "upper tube"] },
};
const COLORS9_4 = { tilt: "#9467bd", j2: "#d62728", rj: "#8c564b", ua: "#1f77b4", j3: "#ff7f0e", fa: "#2ca02c" };
WQ.lab({
  title: ["实验 9.4 机械臂末端在负载下的下垂", "Lab 9.4 Tip sag of a robot arm under load"],
  goal: ["改负载、管子截面、减速器规格和底座轴承刚度，看连杆、关节、轴承各贡献多少下垂，找出最弱的一环。",
         "Change the payload, tube sections, reducer size and base bearing stiffness; see how much each link, joint and bearing contributes to the sag and find the weakest link."],
  scenes: [
    { id: "ur5e", robot: true, name: ["UR5e 水平伸直", "UR5e stretched horizontally"],
      problem: { title: ["工程问题：手臂为什么会“低头”", "Engineering problem: why the arm droops"],
                 text: ["协作机器人末端装上 5 kg 的工具，手臂伸直时末端会往下沉几毫米，远大于它的定位精度要求。下沉是连杆弯的、关节扭的，还是底座歪的？想让它少沉，改哪里最划算？",
                        "With a 5 kg tool at the tip, a stretched cobot arm sinks by millimeters — far beyond its accuracy requirement. Is it the links bending, the joints twisting or the base tilting? Where is it cheapest to stiffen?"] } },
    { id: "stick", name: ["伸缩自拍杆", "Telescoping selfie stick"],
      problem: { title: ["生活中的例子：自拍杆为什么晃", "Everyday example: why a selfie stick wobbles"],
                 text: ["自拍杆伸长到 80 多厘米，端上一部手机，末端明显往下沉，一碰就晃。杆子本身是铝管（这里简化为两节），最软的一环在哪里？",
                        "A selfie stick stretched to over 80 cm with a phone at the end visibly droops and wobbles at a touch. The stick is aluminum tube (simplified to two sections) — where is the softest link?"] } },
  ],
  params: [
    { id: "m", name: ["末端负载 m", "Tip payload m"], min: 0, max: 10, step: 0.1, value: 5, unit: "kg", digits: 1 },
    { id: "size", name: ["减速器规格（0 CSF-17、1 CSF-25、2 CSF-32）", "Reducer size (0 CSF-17, 1 CSF-25, 2 CSF-32)"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "kt", name: ["底座轴承的倾覆刚度", "Base bearing tilt stiffness"], min: 2, max: 100, step: 1, value: 20, unit: "×10⁴ N·m/rad", digits: 0 },
    { id: "D1", name: ["上臂管外径 D1", "Upper-arm tube OD D1"], min: 10, max: 120, step: 1, value: 85, unit: "mm", digits: 0 },
    { id: "t1", name: ["上臂管壁厚 t1", "Upper-arm tube wall t1"], min: 0.5, max: 10, step: 0.1, value: 2.5, unit: "mm", digits: 1 },
    { id: "D2", name: ["小臂管外径 D2", "Forearm tube OD D2"], min: 10, max: 120, step: 1, value: 75, unit: "mm", digits: 0 },
    { id: "t2", name: ["小臂管壁厚 t2", "Forearm tube wall t2"], min: 0.5, max: 10, step: 0.1, value: 2, unit: "mm", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "#d62728", name: ["肩关节（自拍杆没有）", "shoulder (none on the stick)"] }, { color: "#1f77b4", name: ["上臂管 / 下节管", "upper-arm / lower tube"] },
           { color: "#ff7f0e", name: ["肘关节 / 伸缩接头", "elbow / telescoping joint"] }, { color: "#9467bd", name: ["底座轴承 / 手腕", "base bearing / wrist"] }, { color: "#8c564b", name: ["肩关节输出轴 RJ-201", "shoulder shaft RJ-201"] },
           { color: "#2ca02c", name: ["小臂管 / 上节管", "forearm / upper tube"] }],
  tasks: [
    { id: "ur5e", robot: true, text: ["UR5e 带 5 kg（默认参数）：读出末端下垂和每一环的贡献，哪一环最大？再把负载改为 0，算出 5 kg 引起的增量。", "UR5e with 5 kg (defaults): read the tip sag and each contribution — which is largest? Then set the payload to 0 and find the increment due to 5 kg."],
      demo: { scene: "ur5e", set: { m: 5, size: 1, kt: 20, D1: 85, t1: 2.5, D2: 75, t2: 2 }, press: ["start"], wait: 1 } },
    { id: "reducer", robot: true, text: ["把减速器换成 CSF-32（规格 2），下垂减少多少？", "Switch to CSF-32 (size 2): how much does the sag drop?"],
      demo: { scene: "ur5e", set: { m: 5, size: 2, kt: 20, D1: 85, t1: 2.5, D2: 75, t2: 2 }, press: ["start"], wait: 1 } },
    { id: "tube", robot: true, text: ["减速器改回 CSF-25，把两根管的壁厚都加倍（5 mm、4 mm），下垂减少多少？与上一个任务比较。", "Back to CSF-25 and double both walls (5 mm, 4 mm): how much does the sag drop? Compare with the previous task."],
      demo: { scene: "ur5e", set: { m: 5, size: 1, kt: 20, D1: 85, t1: 5, D2: 75, t2: 4 }, press: ["start"], wait: 1 } },
    { id: "stick", text: ["伸缩自拍杆（下节 Ø20 × 1、上节 Ø16 × 1，手机 0.2 kg）：最软的是哪一环？", "Selfie stick (lower Ø20 × 1, upper Ø16 × 1, 0.2 kg phone): which link is the softest?"],
      demo: { scene: "stick", set: { m: 0.2, D1: 20, t1: 1, D2: 16, t2: 1 }, press: ["start"], wait: 1 } },
  ],
  think: ["程序 9.4.1 和本实验用同一个模型。串联时柔度相加，最弱的一环决定整体；离末端越远的转动环节，折算到末端的刚度 K/x² 越小。为什么机械臂的肩关节常用比肘关节大一号的减速器？",
          "Program 9.4.1 and this lab share one model. In series the compliances add and the weakest link governs; the farther a rotary link is from the tip, the smaller its stiffness K/x² referred to the tip. Why do robot shoulders often use a reducer one size larger than the elbow?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    const p = api.p, sc = api.scene === "stick" ? "stick" : "robot";
    s.r = sag9_4(p, sc, p.m);
    s.r0 = sag9_4(p, sc, 0);
    s.sc = sc;
    if (sc === "robot") {
      if (Math.round(p.size) === 1 && p.t1 < 3 && p.t2 < 3 && Math.abs(p.m - 5) < 0.05) api.done("ur5e");
      if (Math.round(p.size) === 2) api.done("reducer");
      if (Math.round(p.size) === 1 && p.t1 >= 4.9 && p.t2 >= 3.9) api.done("tube");
    } else api.done("stick");
    api.stop();
  },
  readouts(api, s) {
    const f = api.fmt, r = s.r;
    if (!r) return [[["状态", "Status"], api.T("按“计算”开始", "press Compute")]];
    const N = NAMES9_4[s.sc], rows = [];
    for (const k of ["j2", "ua", "j3", "tilt", "rj", "fa"]) if (!(s.sc === "stick" && (k === "j2" || k === "rj")))
      rows.push([N[k], f(r.parts[k], 3) + " mm" + api.T("（", " (") + f(r.parts[k] / r.total * 100, 0) + api.T("%）", "%)")]);
    rows.push([["末端下垂（合计）", "Tip sag (total)"], f(r.total, 3) + " mm"]);
    rows.push([["负载引起的增量", "Increment due to payload"], f(r.total - s.r0.total, 3) + " mm"]);
    if (s.sc === "robot") {
      rows.push([["肩关节转矩", "Shoulder torque"], f(r.T2, 1) + " N·m"]);
      rows.push([["肘关节转矩", "Elbow torque"], f(r.T3, 1) + " N·m"]);
    }
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    if (!s.r) { api.label(api.T("按“计算”算末端下垂", "Press Compute for the tip sag"), w / 2, h / 2, css("--muted"), 14, "center"); return; }
    const r = s.r, A = r.A, keys = ["j2", "ua", "j3", "tilt", "rj", "fa"].filter((k) => !(s.sc === "stick" && (k === "j2" || k === "rj")));
    // 左：手臂的变形（放大）
    const x0 = 40, y0 = h * 0.35, sx = (w * 0.55 - 70) / r.x, amp = Math.min(60 / Math.max(r.total, 1e-6), 400);
    api.line(x0, y0, x0 + r.x * sx, y0, css("--muted"), 1, [4, 4]);
    const pts = r.shape.concat([[r.x, r.total]]);
    for (let i = 0; i < pts.length - 1; i++)
      api.line(x0 + pts[i][0] * sx, y0 + pts[i][1] * amp, x0 + pts[i + 1][0] * sx, y0 + pts[i + 1][1] * amp, css("--accent"), i === 2 ? 4 : 7);
    pts.slice(0, 3).forEach((q) => api.circle(x0 + q[0] * sx, y0 + q[1] * amp, 7, css("--ink")));
    api.rect(x0 + r.x * sx - 9, y0 + r.total * amp, 18, 18, css("--amber"));
    api.label(api.T(`变形放大 ${amp.toFixed(0)} 倍`, `deformation ×${amp.toFixed(0)}`), x0, y0 - 24, css("--muted"), 12);
    api.label(api.fmt(r.total, 2) + " mm", x0 + r.x * sx - 20, y0 + r.total * amp + 34, css("--ink"), 13);
    // 右：各环的贡献
    const bx = w * 0.6, bw = w * 0.36, bh = 22, mx = Math.max(...keys.map((k) => r.parts[k]));
    keys.forEach((k, i) => {
      const y = 40 + i * (bh + 14);
      api.label(api.T(...NAMES9_4[s.sc][k]), bx, y - 2, css("--ink"), 12);
      api.rect(bx, y + 6, bw * r.parts[k] / mx, bh - 8, COLORS9_4[k]);
    });
  },
});
