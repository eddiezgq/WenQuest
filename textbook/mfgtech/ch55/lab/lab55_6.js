// 实验 55.6 表面状态与疲劳寿命（配 55.6 节）。公式与 hub/surface.py 相同（FKM 指南的做法）：
//   K_R = 1 − 0.22·lg Rz·lg(2Rm/400)（Rz ≤ 1 µm 取 1），M = 0.35×10⁻³Rm − 0.1，σD = σ₋₁·K_R − M·σres（式 (55.6.1)、(55.6.2)）；
//   Basquin：σa ≤ σD 无限寿命，否则 N = 10⁷·(σa/σD)^−9。
//   加工方法的预设：Rz 取算例 55.6.1（磨削 Ra 0.8 → Rz 5.43；精车 Ra 3.2 → Rz 12.84；喷丸使磨削表面 Rz 增大到约 2.5 倍；深滚压 Rz 约为磨削的一半，同算例 55.7.2），
//   表层残余应力取 hub/surface.py 的 RESIDUAL 典型分布的表面值；下图的分布按这些点连成折线（示意）。
const MAT6 = { sh101: { name: ["20CrMnTi（渗碳淬火）", "20CrMnTi (case-hardened)"], Rm: 1080, s1: 525 }, sh301: { name: ["45 钢（调质）", "45 steel (Q&T)"], Rm: 640, s1: 275 } };
const RES6 = {
  turned: [[0, 250], [0.02, 150], [0.05, 20], [0.08, -40], [0.15, -10], [0.3, 0]],
  ground: [[0, -150], [0.01, -180], [0.03, -60], [0.06, -10], [0.15, 0], [0.3, 0]],
  ground_burn: [[0, 550], [0.02, 450], [0.05, 180], [0.08, 20], [0.12, -60], [0.2, -20], [0.3, 0]],
  shot_peened: [[0, -450], [0.04, -650], [0.1, -500], [0.2, -150], [0.3, 50], [0.5, 20], [0.8, 0]],
  rolled: [[0, -550], [0.15, -800], [0.4, -600], [0.8, -150], [1.1, 60], [1.6, 0]],
};
const METH6 = [
  { name: ["自定义（用下面两个滑块）", "custom (use the two sliders below)"] },
  { name: ["精车 Ra 3.2", "turned Ra 3.2"], rz: 12.84, res: "turned" },
  { name: ["正常磨削 Ra 0.8", "ground Ra 0.8"], rz: 5.43, res: "ground" },
  { name: ["磨削烧伤（Ra 0.8）", "burnt in grinding (Ra 0.8)"], rz: 5.43, res: "ground_burn" },
  { name: ["磨削后喷丸（表面变粗）", "ground, then shot-peened"], rz: 13.58, res: "shot_peened" },
  { name: ["深滚压（Rz 约为磨削的一半）", "deep rolled (Rz about half of ground)"], rz: 2.72, res: "rolled" },
];
function kr6(rz, rm) { return rz <= 1 ? 1 : 1 - 0.22 * Math.log10(rz) * Math.log10(2 * rm / 400); }
function m6(rm) { return 0.35e-3 * rm - 0.1; }
function life6(sa, sd) { return sa <= sd ? Infinity : 1e7 * Math.pow(sa / sd, -9); }
function eval6(api) {
  const p = api.p, mat = MAT6[api.scene] || MAT6.sh101, me = METH6[Math.round(p.meth)] || METH6[0];
  const rz = me.rz ?? p.rz, sres = me.res ? RES6[me.res][0][1] : p.sres;
  const K = kr6(rz, mat.Rm), M = m6(mat.Rm), sd = Math.max(mat.s1 * K - M * sres, 0);
  return { mat, me, rz, sres, K, M, sd, N: life6(p.sa, sd) };
}
const eq6 = (a, b) => Math.abs(a - b) < 1e-6;

WQ.lab({
  title: ["实验 55.6 表面状态与疲劳寿命", "Lab 55.6 Surface condition and fatigue life"],
  goal: ["选材料，调表面粗糙度、表层残余应力（或直接选加工方法）和应力幅，看疲劳极限和 S–N 曲线怎样变化，体会表面完整性对疲劳的影响。",
         "Choose the material, set the roughness and surface residual stress (or pick a process) and the stress amplitude; see the fatigue limit and the S–N curve change, and feel how surface integrity governs fatigue."],
  scenes: [
    { id: "sh101", robot: true, name: ["SH-101 轴承位（20CrMnTi）", "SH-101 bearing seat (20CrMnTi)"],
      params: { meth: { value: 2 }, rz: { value: 5.4 }, sres: { value: -150 }, sa: { value: 480 } },
      problem: { title: ["机器人问题：那一批齿轮轴为什么早期开裂", "Robot problem: why did that batch of gear shafts crack early"],
                 text: ["SH-101 齿轮轴在台架上承受约 480 MPa 的弯曲应力幅（示意）。正常磨削的轴不会疲劳破坏，磨削烧伤的那一批却在几十万次循环时就开裂了。尺寸、粗糙度都合格，差别在表层的残余应力。",
                        "The SH-101 shaft sees a bending stress amplitude of about 480 MPa on the rig (illustrative). Normally ground shafts never fail; the burnt batch cracked after a few hundred thousand cycles. Size and Ra were fine — the difference is the residual stress in the surface layer."] } },
    { id: "sh301", name: ["SH-301 轴承位（45 钢调质）", "SH-301 bearing seat (45 Q&T)"],
      params: { meth: { value: 2 }, rz: { value: 5.4 }, sres: { value: -150 }, sa: { value: 250 } },
      problem: { title: ["工程问题：调质钢对表面的敏感程度", "Engineering problem: how sensitive is a Q&T steel to its surface"],
                 text: ["SH-301 用 45 钢调质，强度比渗碳层低得多。同样精车或磨削的表面，它的疲劳极限下降多少？和 SH-101 比一比。", "SH-301 is 45 steel, Q&T, far weaker than a carburized case. How much does the same turned or ground surface lower its fatigue limit? Compare with SH-101."] } },
  ],
  params: [
    { id: "meth", name: ["加工方法（0 自定义、1 精车、2 磨削、3 烧伤、4 喷丸、5 滚压）", "Process (0 custom, 1 turned, 2 ground, 3 burnt, 4 peened, 5 rolled)"], min: 0, max: 5, step: 1, value: 2, unit: "", digits: 0 },
    { id: "rz", name: ["表面粗糙度 Rz（自定义时）", "Roughness Rz (custom)"], min: 1, max: 100, step: 0.1, value: 5.4, unit: "µm", digits: 1 },
    { id: "sres", name: ["表层残余应力（自定义时，拉为正）", "Surface residual stress (custom, tension +)"], min: -500, max: 800, step: 10, value: -150, unit: "MPa", digits: 0 },
    { id: "sa", name: ["弯曲应力幅 σa", "Bending stress amplitude σa"], min: 100, max: 700, step: 10, value: 480, unit: "MPa", digits: 0 },
  ],
  legend: [{ color: "var(--red)", name: ["当前表面的 S–N 曲线", "S–N curve of this surface"] }, { color: "var(--muted)", name: ["参照：正常磨削", "reference: normal grinding"] }, { color: "var(--accent)", name: ["表层残余应力分布", "residual stress profile"] }],
  tasks: [
    { id: "burn", text: ["SH-101：正常磨削和磨削烧伤的疲劳极限各多少？烧伤使它下降百分之几？", "SH-101: the fatigue limits for normal grinding and for burn? By what percentage does burn lower it?"],
      demo: { scene: "sh101", set: { meth: 3, sa: 480 }, press: [], wait: 1 } },
    { id: "save", text: ["σa = 480 MPa：让烧伤的轴恢复无限寿命，可以怎么办？（换一种表面处理或自定义表层应力）", "At σa = 480 MPa, how can a burnt shaft get back to infinite life? (another surface treatment, or a custom residual stress)"],
      demo: { scene: "sh101", set: { meth: 4, sa: 480 }, press: [], wait: 1 } },
    { id: "sens", text: ["精车 Ra 3.2 的表面：45 钢和 20CrMnTi 的粗糙度系数 K_R 各多少？哪种钢对粗糙度更敏感？", "A turned Ra 3.2 surface: K_R for 45 steel and for 20CrMnTi? Which is more sensitive to roughness?"],
      demo: { scene: "sh301", set: { meth: 1 }, press: [], wait: 1 } },
    { id: "n6", text: ["SH-101 自定义（Rz 5.4 µm、σa = 480 MPa）：要求寿命不少于 10⁶ 次，表层允许的最大拉应力是多少？", "SH-101 custom (Rz 5.4 µm, σa = 480 MPa): for at least 10⁶ cycles, what is the largest allowable surface tension?"],
      demo: { scene: "sh101", set: { meth: 0, rz: 5.4, sres: 320, sa: 480 }, press: [], wait: 1 } },
  ],
  think: ["式 (55.6.2) 只按表面的残余应力计算。喷丸的最大压应力在表面下几十微米处，而疲劳裂纹萌生在表面——这样算偏于保守还是偏于危险？残余应力在交变载荷下会松弛，又会怎样？",
          "Eq. (55.6.2) uses only the surface value. Peening's peak compression lies tens of microns below the surface where cracks do not start — is this conservative or not? And what if the residual stress relaxes under cyclic load?"],

  reset(api, s) {},
  update(dt, api, s) { api.stop(); },
  readouts(api, s) {
    const p = api.p, r = eval6(api), T = api.T, m = Math.round(p.meth);
    if (api.scene === "sh101" && m === 3) api.done("burn");          // 正常磨削的疲劳极限在读数里一并给出
    if (api.scene === "sh101" && p.sa >= 480 - 1e-9 && r.N === Infinity && (m === 4 || m === 5 || (m === 0 && p.sres <= 0 && p.rz >= 5.4 - 1e-9))) api.done("save");
    if (m === 1 && api.scene === "sh301") api.done("sens");          // 另一种钢同样表面的 K_R 在读数里一并给出
    if (api.scene === "sh101" && m === 0 && eq6(p.rz, 5.4) && eq6(p.sa, 480) && r.N >= 1e6) {
      const nx = Math.max(r.mat.s1 * r.K - r.M * (p.sres + 10), 0);
      if (life6(p.sa, nx) < 1e6) api.done("n6");
    }
    const ref = Math.max(r.mat.s1 * kr6(5.43, r.mat.Rm) - r.M * -150, 0);
    return [
      [["材料（Rm / σ₋₁）", "material (Rm / σ₋₁)"], T(...r.mat.name) + `（${r.mat.Rm} / ${r.mat.s1} MPa）`],
      [["表面", "surface"], T(...r.me.name) + `：Rz ${api.fmt(r.rz, 1)} µm，σres ${r.sres > 0 ? "+" : ""}${api.fmt(r.sres, 0)} MPa`],
      [["粗糙度系数 K_R / 平均应力敏感系数 M", "K_R / mean-stress sensitivity M"], api.fmt(r.K, 3) + " / " + api.fmt(r.M, 3)],
      [["同样表面另一种钢的 K_R", "K_R of the other steel, same surface"], (() => { const o = MAT6[api.scene === "sh101" ? "sh301" : "sh101"]; return T(...o.name) + " " + api.fmt(kr6(r.rz, o.Rm), 3); })()],
      [["疲劳极限 σD = σ₋₁K_R − M·σres", "fatigue limit σD"], api.fmt(r.sd, 0) + " MPa" + T(`（正常磨削 ${api.fmt(ref, 0)} MPa 的 ${api.fmt(r.sd / ref * 100, 0)}%）`, ` (${api.fmt(r.sd / ref * 100, 0)}% of normal grinding)`)],
      [["σa 下的寿命", "life at σa"], r.N === Infinity ? T("无限寿命（σa ≤ σD）", "infinite (σa ≤ σD)") : api.fmt(r.N / 1e5, 2) + " × 10⁵" + T(" 次", " cycles")],
    ];
  },
  draw(api, s) {
    const r = eval6(api), { w, h } = api, css = api.css, p = api.p;
    // 上：S–N 曲线（双对数）
    const lx = (n) => Math.log10(n), ref = Math.max(r.mat.s1 * kr6(5.43, r.mat.Rm) - r.M * -150, 1);
    const sn = (sd) => { const pts = []; for (let e = 4; e <= 8.01; e += 0.05) { const n = Math.pow(10, e); pts.push([e, n < 1e7 ? sd * Math.pow(n / 1e7, -1 / 9) : sd]); } return pts; };
    const ymax = Math.max(ref * 2.3, r.sd * 2.3, p.sa * 1.2);
    const P = api.plot(w * 0.08, h * 0.06, w * 0.86, h * 0.4, [{ pts: sn(ref), color: css("--muted") }, { pts: sn(Math.max(r.sd, 1)), color: css("--red") }],
                       { xmin: 4, xmax: 8, ymin: 0, ymax, xlabel: api.T("循环次数 N（对数坐标；虚线 N_D = 10⁷）", "cycles N (log; dashed N_D = 10⁷)"), ylabel: api.T("应力幅 / MPa", "stress amplitude / MPa") });
    for (let e = 4; e <= 7; e++) api.label("10" + "⁴⁵⁶⁷⁸"[e - 4], P.X(e), P.Y(0) + 12, css("--muted"), 11, "center");
    api.line(P.X(7), P.Y(0), P.X(7), P.Y(ymax), css("--grid"), 1, [3, 3]);
    api.line(P.X(4), P.Y(p.sa), P.X(8), P.Y(p.sa), css("--ink"), 1, [5, 4]);
    api.label("σa " + api.fmt(p.sa, 0), P.X(8) - 4, P.Y(p.sa) - 8, css("--ink"), 12, "right");
    if (r.N !== Infinity && r.N > 1e4) { api.circle(P.X(lx(r.N)), P.Y(p.sa), 5, css("--red")); api.label(api.fmt(r.N / 1e5, 1) + "×10⁵", P.X(lx(r.N)) + 7, P.Y(p.sa) + 12, css("--red"), 12); }
    // 下：表层残余应力沿深度（加工方法的典型分布；自定义时只有表面值）
    const pts = r.me.res ? RES6[r.me.res] : [[0, r.sres], [0.05, r.sres]];
    const zmax = r.me.res ? pts[pts.length - 1][0] : 0.3;
    const Q = api.plot(w * 0.08, h * 0.6, w * 0.86, h * 0.3, [{ pts, color: css("--accent") }],
                       { xmin: 0, xmax: zmax, ymin: -850, ymax: 850, xlabel: api.T("离表面的深度 / mm", "depth / mm"), ylabel: api.T("残余应力 / MPa（拉为正；典型分布，折线示意）", "residual stress / MPa (tension +; typical, polyline)") });
    api.circle(Q.X(0), Q.Y(r.sres), 5, r.sres > 0 ? css("--red") : css("--accent"));
  },
});
