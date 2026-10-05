// 实验 53.2 轴向尺寸链的极值法（配 53.1、53.2 节）。零件库 E-WKP-SH301 的工序 40（精车后）状态。
// 环的数据取自工艺规程 tolerance_chart 的工序 40：总长 167 ± 0.2（增环）、左端面到左轴肩 52 ± 0.05（减环）、
// 右轴肩到右端面 55 ± 0.05（减环）；封闭环齿轮位长度 A0 = 167 − 52 − 55 = 60，图纸 60 ± 0.3。
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
WQ.lab({
  title: ["实验 53.2 齿轮位长度的极值法", "Lab 53.2 Worst-case analysis of the gear-seat length"],
  goal: ["在 SH-301 上调总长和两个轴肩尺寸，看封闭环齿轮位长度怎样变化，找出它的极限值，与极值法公式比较。",
         "Vary the overall length and the two shoulder sizes on SH-301, watch the closing gear-seat length and find its limits; compare with the worst-case formula."],
  view: "3d",
  models: ["E-WKP-SH301"],
  scenes: [
    { id: "op40", name: ["工序 40 精车后的 SH-301", "SH-301 after op 40"],
      problem: { title: ["工程问题：齿轮位长度 60 不是直接车出来的", "Engineering problem: the 60 gear seat is not turned directly"],
                 text: ["工序 40 从右端面车右轴肩（55），调头车左端面保证总长（167），再从左端面车左轴肩（52）。齿轮位长度是这三个尺寸间接得到的，三个尺寸的误差全都落到它上面。",
                        "Op 40 turns the right shoulder from the right face (55), turns round for the left face and the overall length (167), then the left shoulder from the left face (52). The gear-seat length follows from these three and collects all their errors."] } },
  ],
  params: [
    { id: "L", name: ["总长（增环）", "Overall length (increasing)"], min: 166.8, max: 167.2, step: 0.01, value: 167, unit: "mm", digits: 2 },
    { id: "a", name: ["左端面到左轴肩（减环）", "Left face to left shoulder (decreasing)"], min: 51.95, max: 52.05, step: 0.01, value: 52, unit: "mm", digits: 2 },
    { id: "b", name: ["右轴肩到右端面（减环）", "Right shoulder to right face (decreasing)"], min: 54.95, max: 55.05, step: 0.01, value: 55, unit: "mm", digits: 2 },
  ],
  tasks: [
    { id: "dec", text: ["只把 52 调到上偏差 52.05、其余取名义值：A₀ 变大还是变小？这就是“减环”的意思。", "Only set 52 to its upper limit 52.05: does A₀ grow or shrink? That is what “decreasing link” means."],
      demo: { scene: "op40", set: { L: 167, a: 52.05, b: 55 }, press: [], wait: 1 } },
    { id: "max", text: ["找出使 A₀ 最大的组合，读出 A₀max。", "Find the combination giving the largest A₀ and read A₀max."],
      demo: { scene: "op40", set: { L: 167.2, a: 51.95, b: 54.95 }, press: [], wait: 1 } },
    { id: "min", text: ["找出使 A₀ 最小的组合，读出 A₀min，与 60 ± 0.3 比较。", "Find the smallest A₀ and compare with 60 ± 0.3."],
      demo: { scene: "op40", set: { L: 166.8, a: 52.05, b: 55.05 }, press: [], wait: 1 } },
  ],
  think: ["极值法算出的齿轮位长度公差正好用满 ±0.3。如果总长只能保证 ±0.3，该怎样改工艺才能保住齿轮位长度（53.7 节）？",
          "The worst case uses up exactly ±0.3. If the overall length could only be held to ±0.3, how would you change the process to keep the gear seat (Section 53.7)?"],

  setup3d(api, keep) {
    const h = api.m["E-WKP-SH301"];
    FX.setup(api, h);
    h.parts.forEach((p, i) => { const m = p.home_mm || [0, 0, 0]; if (p.obj) { p.p0.add(new api.three.Vector3(m[0], m[1], m[2]).multiplyScalar(0.001)); p.obj.position.copy(p.p0); p.obj.visible = i === 2; } });
    keep.objs = [];
    keep.key = "";
    api.view(0, 18, 1.3, h);
  },
  a0(api) { return api.p.L - api.p.a - api.p.b; },
  readouts(api) {
    const A = this.a0(api), near = (x, y) => Math.abs(x - y) < 1e-6;
    if (near(api.p.L, 167) && near(api.p.a, 52.05) && near(api.p.b, 55)) api.done("dec");
    if (near(A, 60.3)) api.done("max");
    if (near(A, 59.7)) api.done("min");
    return [[["尺寸链", "chain"], "A₀ = 167 − 52 − 55（167 增环，52、55 减环）"],
            [["封闭环 A₀（齿轮位长度）", "closing link A₀ (gear seat)"], api.fmt(A, 2) + " mm"],
            [["偏离名义 60", "deviation from 60"], (A - 60 >= 0 ? "+" : "") + api.fmt(A - 60, 2) + " mm"],
            [["极值法", "worst case"], "A₀max = 167.2 − 51.95 − 54.95 = 60.30；A₀min = 166.8 − 52.05 − 55.05 = 59.70；T₀ = 0.4 + 0.1 + 0.1 = 0.6"],
            [["图纸 60 ± 0.3", "drawing 60 ± 0.3"], Math.abs(A - 60) <= 0.3 + 1e-9 ? "合格 / within" : "超差 / out"]];
  },
  draw(api) {
    const h = api.m["E-WKP-SH301"];
    if (!h || !h.parts) return;
    const key = [api.p.L, api.p.a, api.p.b].join("|");
    if (key === api.keep.key) return;
    api.keep.key = key;
    const T = api.three, k = api.keep;
    clear(api, k.objs);
    const add = (o) => { api.st.scene.add(o); k.objs.push(o); };
    // 实际尺寸只差零点几毫米，模型看不出来；尺寸线按名义位置画，标注写实际值
    const P = (x, z) => FX.world(api, h, [x, -26, z]);
    const lab = (txt, col, x, z) => { const t = FX.tag(api, txt, col); t.scale.multiplyScalar(0.6); t.position.copy(P(x, z)); add(t); };
    [[0, "L"], [52, "S2"], [112, "S3"], [167, "R"]].forEach(([x, n]) => {
      add(new T.Line(new T.BufferGeometry().setFromPoints([P(x, -30), P(x, 56)]), new T.LineBasicMaterial({ color: 0x9aa3ab })));
      lab(n, "#5b6770", x, 62);
    });
    add(dimArrow(api, P(0, 46), P(167, 46), 0x4f7fb8)); lab("167 增环 " + api.fmt(api.p.L, 2), "#4f7fb8", 83.5, 51);
    add(dimArrow(api, P(0, 30), P(52, 30), 0x5a9e6f)); lab("52 减环 " + api.fmt(api.p.a, 2), "#2f7a4a", 26, 35);
    add(dimArrow(api, P(112, 30), P(167, 30), 0x5a9e6f)); lab("55 减环 " + api.fmt(api.p.b, 2), "#2f7a4a", 139.5, 35);
    add(dimArrow(api, P(52, -26), P(112, -26), 0xc0504d)); lab("A₀ = " + api.fmt(this.a0(api), 2), "#c0504d", 82, -33);
  },
});
