// 实验 53.1 键槽深度尺寸链（配 53.1、53.2 节）。零件库 E-WKP-SH301 的工序 50（铣键槽后）、工序 60（磨外圆后）两个状态，
// 过键槽中部（x = 82 mm）剖开，剖面补画成实体。环的数据取自工艺规程 std/SH-301_process.yaml 的 chains：
// H = 35.15（−0.03/−0.20，增环），精车半径 r1 = 20.15（0/−0.0195，减环），磨削半径 r2 = 20（+0.009/+0.001，增环），
// 封闭环 A0 = d − t1 = H − r1 + r2，图纸要求 35（0/−0.2）。“照图纸尺寸铣”是错误做法：H 取 35（0/−0.2）。
const FX = {
  setup(api, h) {
    h.root.traverse((o) => { if (o.isMesh) { o.material = o.material.clone(); o.material.side = api.three.DoubleSide; } });
    h.parts = ((h.entry.assembly || {}).parts || []).map((p) => Object.assign({}, p));
    h.parts.forEach((p) => { p.obj = h.nodes[p.node]; if (p.obj) p.p0 = p.obj.position.clone(); });
    h.base = h.nodes.root || h.root;
  },
  explode(api, h, k) {
    h.parts.forEach((p) => { if (!p.obj) return; const e = p.explode_mm || [0, 0, 0];
      p.obj.position.copy(p.p0).add(new api.three.Vector3(e[0], e[1], e[2]).multiplyScalar(k / 1000)); });
  },
  look(h, alpha) {       // alpha(p) → 1 实体、0–1 半透明、0 隐藏
    h.parts.forEach((p) => { if (!p.obj) return; const a = alpha(p); p.obj.visible = a > 0;
      p.obj.traverse((o) => { if (o.isMesh) { o.material.opacity = a; o.material.transparent = a < 0.999; o.material.depthWrite = a >= 0.999; } }); });
  },
  world(api, h, mm) { h.base.updateMatrixWorld(true); return new api.three.Vector3(mm[0] / 1000, mm[1] / 1000, mm[2] / 1000).applyMatrix4(h.base.matrixWorld); },
  plane(api, h, pointMm, normal) {     // 模型坐标（毫米）里的点和法向 → 世界坐标的剖切平面（保留法向一侧）
    const n = new api.three.Vector3(...normal).transformDirection(h.base.matrixWorld);
    return new api.three.Plane().setFromNormalAndCoplanarPoint(n, FX.world(api, h, pointMm));
  },
  clip(api, h, plane) { api.st.renderer.localClippingEnabled = true; h.root.traverse((o) => { if (o.isMesh) o.material.clippingPlanes = plane ? [plane] : []; }); },
  tag(api, text, color = "#1d2327") {  // 文字标签（随视角朝向观察者）
    const T = api.three, c = document.createElement("canvas"), g = c.getContext("2d");
    g.font = "bold 30px sans-serif"; const w = Math.ceil(g.measureText(text).width) + 20;
    c.width = w; c.height = 44; g.font = "bold 30px sans-serif";
    g.fillStyle = "rgba(255,255,255,0.85)"; g.fillRect(0, 0, w, 44); g.fillStyle = color; g.textBaseline = "middle"; g.fillText(text, 10, 23);
    const s = new T.Sprite(new T.SpriteMaterial({ map: new T.CanvasTexture(c), depthTest: false }));
    s.scale.set(0.018 * w / 44, 0.018, 1); s.renderOrder = 10; api.st.scene.add(s); return s;
  },
};

function dimArrow(api, a, b, color) {        // 两端带箭头的尺寸线（世界坐标）
  const T = api.three, g = new T.Group(), d = new T.Vector3().subVectors(b, a), L = d.length(), u = d.clone().normalize();
  const hl = Math.min(0.004, L * 0.3);
  g.add(new T.ArrowHelper(u, a.clone().addScaledVector(u, L / 2), L / 2, color, hl, hl * 0.6));
  g.add(new T.ArrowHelper(u.clone().negate(), a.clone().addScaledVector(u, L / 2), L / 2, color, hl, hl * 0.6));
  return g;
}
function clear(api, list) { list.forEach((o) => api.st.scene.remove(o)); list.length = 0; }
const XK = 82, Z_BOT = 15, B = 12;
const A0 = { max: 35.0, min: 34.8 };

WQ.lab({
  title: ["实验 53.1 键槽深度尺寸链", "Lab 53.1 The keyway-depth chain"],
  goal: ["在 SH-301 的剖面上看清键槽深度尺寸链的三个组成环和封闭环，调各环的实际尺寸，看 d − t₁ 是否合格。",
         "See the three component links and the closing link of the keyway-depth chain on a section of SH-301; vary the actual sizes and check d − t₁."],
  view: "3d",
  models: ["E-WKP-SH301"],
  scenes: [
    { id: "card", name: ["按工序卡：H = 35.15（−0.03/−0.20）", "By the operation sheet: H = 35.15 (−0.03/−0.20)"],
      params: { H: { min: 34.95, max: 35.12, value: 35.035, step: 0.005 } },
      problem: { title: ["工程问题：工序卡上的 H 为什么不等于图纸尺寸", "Engineering problem: why H on the sheet differs from the drawing"],
                 text: ["图纸要求 d − t₁ = 35（0/−0.2），铣键槽时外圆还没磨，d − t₁ 量不出来，只能控制从精车外圆下母线量起的 H；磨削以后 d − t₁ 才形成，是间接得到的封闭环。",
                        "The drawing asks for d − t₁ = 35 (0/−0.2). When the keyway is milled the diameter is not yet ground, so only H from the turned bottom line can be controlled; d − t₁ forms after grinding and is the closing link."] } },
    { id: "drawing", name: ["照图纸尺寸铣：H = 35（0/−0.2）", "Milled to the drawing size: H = 35 (0/−0.2)"],
      params: { H: { min: 34.8, max: 35.0, value: 34.9, step: 0.005 } },
      problem: { title: ["错误做法：照图纸尺寸铣键槽", "The wrong way: milling to the drawing size"],
                 text: ["新来的工艺员把图纸上的 35（0/−0.2）直接写成铣键槽的工序尺寸。磨削使下母线向轴心移动，槽底不动，键槽相对变深。",
                        "A newcomer writes the drawing's 35 (0/−0.2) as the milling size. Grinding moves the bottom line toward the axis while the slot bottom stays, so the keyway gets relatively deeper."] } },
  ],
  params: [
    { id: "H", name: ["铣键槽 H（工序 50）", "Milled H (op 50)"], min: 34.95, max: 35.12, step: 0.005, value: 35.035, unit: "mm", digits: 3 },
    { id: "r1", name: ["精车半径 r₁（工序 40）", "Turned radius r₁ (op 40)"], min: 20.1305, max: 20.15, step: 0.0005, value: 20.14, unit: "mm", digits: 4 },
    { id: "r2", name: ["磨削半径 r₂（工序 60）", "Ground radius r₂ (op 60)"], min: 20.001, max: 20.009, step: 0.001, value: 20.005, unit: "mm", digits: 3 },
    { id: "g", name: ["0 磨削前、1 磨削后", "0 before, 1 after grinding"], min: 0, max: 1, step: 1, value: 1, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "min", text: ["按工序卡：三个环都取使 A₀ 最小的一端，确认 d − t₁ 仍不小于 34.8。", "By the sheet: put all three links at the ends that make A₀ smallest; d − t₁ must still be at least 34.8."],
      demo: { scene: "card", set: { H: 34.95, r1: 20.15, r2: 20.001, g: 1 }, press: [], wait: 1 } },
    { id: "max", text: ["按工序卡：取使 A₀ 最大的一端，确认不超过 35.0。", "By the sheet: the ends that make A₀ largest; it must not exceed 35.0."],
      demo: { scene: "card", set: { H: 35.12, r1: 20.1305, r2: 20.009, g: 1 }, press: [], wait: 1 } },
    { id: "deep", text: ["照图纸尺寸铣：找出一种都在各自公差内、磨后键槽却偏深（d − t₁ < 34.8）的组合。", "Milled to the drawing: find sizes all within their own tolerances that still leave the keyway too deep (d − t₁ < 34.8)."],
      demo: { scene: "drawing", set: { H: 34.85, r1: 20.15, r2: 20.005, g: 1 }, press: [], wait: 1 } },
    { id: "before", text: ["切到“磨削前”：这时 d − t₁ 存在吗？能量的是哪个尺寸？", "Switch to “before grinding”: does d − t₁ exist yet? Which size can you measure?"],
      demo: { scene: "card", set: { g: 0 }, press: [], wait: 1 } },
  ],
  think: ["把工序改成“先磨齿轮位、后铣键槽”，这条尺寸链还在吗？这样改要付出什么代价（53.1.3 题）？",
          "If the gear seat is ground before the keyway is milled, does the chain still exist? What does that change cost (Exercise 53.1.3)?"],

  setup3d(api, keep) {
    const h = api.m["E-WKP-SH301"];
    FX.setup(api, h);
    h.parts.forEach((p, i) => { const m = p.home_mm || [0, 0, 0]; if (p.obj) { p.p0.add(new api.three.Vector3(m[0], m[1], m[2]).multiplyScalar(0.001)); p.obj.position.copy(p.p0); p.obj.visible = false; } });
    FX.clip(api, h, FX.plane(api, h, [XK, 0, 0], [1, 0, 0]));
    keep.objs = [];
    keep.key = "";
    keep.cap = null;
    api.view(-90, 2, 3.4, h);
  },
  a0(api) { return api.p.H - api.p.r1 + api.p.r2; },
  readouts(api) {
    const a = this.a0(api), ok = a >= A0.min - 1e-9 && a <= A0.max + 1e-9, g = api.p.g >= 0.5;
    if (api.scene === "card" && g && Math.abs(a - (34.95 - 20.15 + 20.001)) < 1e-6 && ok) api.done("min");
    if (api.scene === "card" && g && Math.abs(a - (35.12 - 20.1305 + 20.009)) < 1e-6 && ok) api.done("max");
    if (api.scene === "drawing" && g && a < A0.min - 1e-9) api.done("deep");
    if (!g) api.done("before");
    const rows = [[["尺寸链", "chain"], "A₀ = H − r₁ + r₂（H、r₂ 增环，r₁ 减环）"],
                  [["铣键槽 H（从精车外圆下母线量）", "H (from the turned bottom line)"], api.fmt(api.p.H, 3) + " mm"],
                  [["精车半径 r₁ / 磨削半径 r₂", "r₁ / r₂"], api.fmt(api.p.r1, 4) + " / " + api.fmt(api.p.r2, 3) + " mm"]];
    if (!g) return rows.concat([[["d − t₁", "d − t₁"], "还不存在：外圆没磨，只能量 H / not formed yet: only H can be measured"]]);
    return rows.concat([[["封闭环 A₀ = d − t₁", "closing link A₀ = d − t₁"], api.fmt(a, 4) + " mm"],
                        [["图纸要求", "drawing"], "35（0/−0.2），即 34.8 ～ 35.0"],
                        [["结论", "verdict"], ok ? "合格 / within tolerance" : a < A0.min ? "键槽偏深，报废（无法返修）/ too deep: scrap" : "键槽偏浅 / too shallow"]]);
  },
  draw(api) {
    const h = api.m["E-WKP-SH301"];
    if (!h || !h.parts) return;
    const g = api.p.g >= 0.5, key = [api.scene, api.p.H, api.p.r1, api.p.r2, g].join("|");
    if (key === api.keep.key) return;
    api.keep.key = key;
    const T = api.three, k = api.keep;
    h.parts.forEach((p, i) => { if (p.obj) p.obj.visible = i === (g ? 4 : 3); });
    clear(api, k.objs);
    // 剖面：圆（精车或磨后半径，名义）减去键槽；在剖切平面上，朝向观察者（−x）
    const r = g ? 20.0 : 20.15, sh = new T.Shape();
    const zt = Math.sqrt(r * r - (B / 2) * (B / 2)), a0 = Math.asin((B / 2) / r);
    sh.moveTo(B / 2, zt); sh.lineTo(B / 2, Z_BOT); sh.lineTo(-B / 2, Z_BOT); sh.lineTo(-B / 2, zt);
    sh.absarc(0, 0, r, Math.PI / 2 + a0, Math.PI / 2 - a0 + 2 * Math.PI, false);
    const geo = new T.ShapeGeometry(sh, 64), cap = new T.Mesh(geo, new T.MeshBasicMaterial({ color: 0xf4e1d2, side: T.DoubleSide }));
    const o = FX.world(api, h, [XK - 0.05, 0, 0]);
    cap.matrixAutoUpdate = false;
    cap.matrix.makeBasis(new T.Vector3(0, 0, 0.001), new T.Vector3(0, 0.001, 0), new T.Vector3(-0.001, 0, 0)).setPosition(o);
    api.st.scene.add(cap); k.objs.push(cap);
    const P = (y, z) => FX.world(api, h, [XK - 0.3, y, z]);
    const add = (o2) => { api.st.scene.add(o2); k.objs.push(o2); };
    const lab = (txt, col, y, z) => { const t = FX.tag(api, txt, col); t.scale.multiplyScalar(0.3); t.position.copy(P(y, z)); add(t); };
    // 基准线：精车下母线、轴心、磨后下母线、槽底（横线）
    const line = (z, col) => { const m = new T.LineBasicMaterial({ color: col }); add(new T.Line(new T.BufferGeometry().setFromPoints([P(-50, z), P(32, z)]), m)); };
    line(-20.15, 0x4f7fb8); line(0, 0x9aa3ab); line(Z_BOT, 0x1d2327); if (g) line(-20.0, 0xc0504d);
    add(dimArrow(api, P(26, -20.15), P(26, Z_BOT), 0xc0504d)); lab("H", "#c0504d", 30, -2);
    add(dimArrow(api, P(-28, -20.15), P(-28, 0), 0x4f7fb8)); lab("r₁", "#4f7fb8", -24, -10);
    if (g) {
      add(dimArrow(api, P(-36, -20.0), P(-36, 0), 0xc0504d)); lab("r₂", "#c0504d", -33, -10);
      add(dimArrow(api, P(-44, -20.0), P(-44, Z_BOT), 0x1d2327)); lab("A₀", "#1d2327", -48, -2);
    }
  },
});
