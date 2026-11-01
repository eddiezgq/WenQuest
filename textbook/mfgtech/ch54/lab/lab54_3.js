// 实验 54.3 机床几何误差与工件形状（配 54.3 节）。零件库 E-ACC-CENTERS（两顶尖，L = 167）；工件由程序按误差模型生成，误差放大显示。
// 约定与 hub/accuracy.py、图 54.3.4–54.3.6 相同：工件轴线沿 x，左端 x = 0（头架），右端 x = L（尾座）；砂轮（刀具）在 +y 一侧，y 是误差敏感方向。
//   尾座偏移 e（> 0 离开砂轮）：半径误差 e·x/L                                        → 锥度，尾座端大（taper_from_offset）
//   导轨水平面中凸 b（> 0 中间向工件靠近）：半径误差 −b·sin(πx/L)                     → 中间小（鞍形）；b < 0 中间大（鼓形）
//   导轨垂直面中凸 c：切向，直径误差 ≈ (c·sin(πx/L))²/R                                 → 几乎为零（diameter_error）
//   主轴颈椭圆（滑动轴承，半径上幅值 a）：车削时截面半径 −a·cos 2ψ                      → 圆度 2a、椭圆（spindle_roundness）
// 左、右轴承位取 x = 46、124.5（与仿真车间 sim/errors.py 的 Z_LEFT、Z_RIGHT 相同）。
const L = 167, R = 17.5, XL = 46, XR = 124.5;
const FX = {
  setup(api, h) {
    h.root.traverse((o) => { if (o.isMesh) { o.material = o.material.clone(); o.material.side = api.three.DoubleSide; } });
    h.parts = ((h.entry.assembly || {}).parts || []).map((p) => Object.assign({}, p));
    h.parts.forEach((p) => { p.obj = h.nodes[p.node]; if (p.obj) p.p0 = p.obj.position.clone(); });
    h.base = h.nodes.root || h.root;
  },
  tag(api, text, color = "#1d2327") {
    const T = api.three, c = document.createElement("canvas"), g = c.getContext("2d");
    g.font = "bold 30px sans-serif"; const w = Math.ceil(g.measureText(text).width) + 20;
    c.width = w; c.height = 44; g.font = "bold 30px sans-serif";
    g.fillStyle = "rgba(255,255,255,0.85)"; g.fillRect(0, 0, w, 44); g.fillStyle = color; g.textBaseline = "middle"; g.fillText(text, 10, 23);
    const s = new T.Sprite(new T.SpriteMaterial({ map: new T.CanvasTexture(c), depthTest: false }));
    s.scale.set(0.018 * w / 44, 0.018, 1); s.renderOrder = 10; return s;
  },
};

// 真实误差（mm）：直径误差沿 x、截面的半径误差
function err54(p) {
  const e = p.e / 1000, b = p.bh / 1000, c = p.bv / 1000, a = p.sp / 1000;
  const dd = (x) => 2 * (e * x / L - b * Math.sin(Math.PI * x / L)) + Math.pow(c * Math.sin(Math.PI * x / L), 2) / R;
  const d1 = dd(10), d2 = dd(L / 2), d3 = dd(L - 10);
  const taper = d3 - d1, crown = d2 - (d1 + d3) / 2;
  let shape = "cyl";
  if (Math.abs(taper) > 1e-4 || Math.abs(crown) > 1e-4) shape = Math.abs(taper) >= 1.5 * Math.abs(crown) ? "taper" : crown > 0 ? "drum" : "saddle";
  return { dd, left: dd(XL), right: dd(XR), taper, crown, shape, round: 2 * a, vert: Math.pow(c, 2) / R };
}
const SHAPE = { cyl: ["圆柱（看不出形状误差）", "cylinder"], taper: ["锥形", "taper"], drum: ["鼓形（中间大）", "barrel (middle larger)"], saddle: ["鞍形（中间小）", "saddle (middle smaller)"] };

WQ.lab({
  title: ["实验 54.3 机床几何误差与工件形状", "Lab 54.3 Machine geometric errors and the shape of the work"],
  goal: ["在两顶尖装夹的外圆磨床（车床）上，分别加入尾座偏移、导轨在水平面和垂直面内的直线度误差、主轴颈的椭圆，看磨（车）出的工件变成什么形状、左右轴承位差多少，体会误差敏感方向。",
         "On a grinder (or lathe) with the work between centres, add a tailstock offset, horizontal and vertical straightness errors of the guideways and an oval spindle journal one at a time; see what shape the work takes, how far apart the two bearing seats end up, and what the error-sensitive direction means."],
  view: "3d",
  models: ["E-ACC-CENTERS"],
  scenes: [
    { id: "machine", name: ["SH-301 磨轴承位", "Grinding SH-301's bearing seats"],
      problem: { title: ["工程问题：机床的哪项几何误差会留下什么形状", "Engineering problem: which machine error leaves which shape"],
                 text: ["SH-301 两个轴承位 Ø35 k6 在两顶尖上磨出，公差只有 16 µm。机床各部件的几何误差（尾座偏、导轨弯、主轴不圆）都会传到工件上，但影响大小差别很大，形状也各不相同——记住这些“指纹”，54.8 节就能反过来从工件形状找原因。",
                        "SH-301's two Ø35 k6 bearing seats are ground between centres to a 16 µm tolerance. Each geometric error of the machine — an offset tailstock, bent guideways, an oval spindle — reaches the work, but with very different size and shape. Remember these fingerprints: in 54.8 you will work back from the shape to the cause."] } },
  ],
  params: [
    { id: "e", name: ["尾座偏移 e（> 0 离开砂轮）", "Tailstock offset e (> 0 away from the wheel)"], min: -15, max: 15, step: 0.5, value: 0, unit: "µm", digits: 1 },
    { id: "bh", name: ["导轨水平面中凸 b（> 0 中间向工件靠近）", "Guideway bow in the horizontal plane b"], min: -15, max: 15, step: 0.5, value: 0, unit: "µm", digits: 1 },
    { id: "bv", name: ["导轨垂直面中凸 c", "Guideway bow in the vertical plane c"], min: -15, max: 15, step: 0.5, value: 0, unit: "µm", digits: 1 },
    { id: "sp", name: ["主轴颈椭圆（半径上的幅值 a）", "Oval spindle journal (amplitude a on the radius)"], min: 0, max: 5, step: 0.25, value: 0, unit: "µm", digits: 2 },
    { id: "k", name: ["显示放大倍数", "Display magnification"], min: 100, max: 2000, step: 50, value: 800, unit: "×", digits: 0 },
  ],
  tasks: [
    { id: "tail", text: ["只加尾座偏移 8 µm：工件是什么形状？右轴承位比左大多少？与图 54.3.6 和仿真车间的数据比较。", "Tailstock offset 8 µm only: what shape? How much larger is the right seat than the left? Compare with Fig. 54.3.6 and the shop data."],
      demo: { scene: "machine", set: { e: 8, bh: 0, bv: 0, sp: 0 }, press: [], wait: 1 } },
    { id: "horiz", text: ["只加导轨水平面中凸 10 µm：形状和中间的直径误差？", "Horizontal guideway bow 10 µm only: shape and the diameter error in the middle?"],
      demo: { scene: "machine", set: { e: 0, bh: 10, bv: 0, sp: 0 }, press: [], wait: 1 } },
    { id: "vert", text: ["只加导轨垂直面中凸 10 µm：直径误差有多大？为什么？", "Vertical guideway bow 10 µm only: how big is the diameter error, and why?"],
      demo: { scene: "machine", set: { e: 0, bh: 0, bv: 10, sp: 0 }, press: [], wait: 1 } },
    { id: "oval", text: ["只加主轴颈椭圆 3 µm：截面形状和圆度？", "Oval journal 3 µm only: cross-section and roundness?"],
      demo: { scene: "machine", set: { e: 0, bh: 0, bv: 0, sp: 3 }, press: [], wait: 1 } },
    { id: "mix", text: ["尾座偏移 −6 µm 与导轨水平面中凸 4 µm 同时存在：工件是什么形状？左右轴承位还合格吗（按两轴承位用同一次调整磨出算）？", "Tailstock −6 µm and a horizontal bow of 4 µm together: what shape? Are both seats still in tolerance (one setting for both)?"],
      demo: { scene: "machine", set: { e: -6, bh: 4, bv: 0, sp: 0 }, press: [], wait: 1 } },
  ],
  think: ["把同样的尾座偏移放到车床上（车刀在 −y 一侧），锥度的方向会变吗？导轨在水平面内中凸，车床车出的工件是什么形状？", "Put the same tailstock offset on a lathe with the tool on the −y side: does the taper change direction? What shape does a lathe give with a horizontally bowed guideway?"],

  setup3d(api, keep) {
    const h = api.m["E-ACC-CENTERS"];
    FX.setup(api, h);
    keep.tail = h.parts.filter((p) => p.name === "尾座" || p.name === "后顶尖");
    const T = api.three;
    keep.mat = new T.MeshStandardMaterial({ color: 0xe8c39e, roughness: 0.6, metalness: 0.1, side: T.DoubleSide });
    keep.mesh = null;
    keep.key = "";
    keep.tags = [];
    api.view(-15, 25, 1.3, h);
  },
  readouts(api) {
    const p = api.p, r = err54(p), f = (x) => api.fmt(x * 1000, 2) + " µm", T = api.T;
    const only = (k) => ["e", "bh", "bv", "sp"].every((q) => q === k || Math.abs(p[q]) < 1e-9);
    if (only("e") && Math.abs(p.e - 8) < 0.26 && r.shape === "taper") api.done("tail");
    if (only("bh") && p.bh >= 10 - 1e-9 && r.shape === "saddle") api.done("horiz");
    if (only("bv") && Math.abs(p.bv) >= 10 - 1e-9) api.done("vert");
    if (only("sp") && Math.abs(p.sp - 3) < 0.13) api.done("oval");
    if (Math.abs(p.e + 6) < 0.26 && Math.abs(p.bh - 4) < 0.26 && Math.abs(p.bv) < 1e-9 && Math.abs(p.sp) < 1e-9) api.done("mix");
    const sh = SHAPE[r.shape];
    return [
      [["左轴承位直径误差（x = 46）", "left seat (x = 46)"], f(r.left)],
      [["右轴承位直径误差（x = 124.5）", "right seat (x = 124.5)"], f(r.right)],
      [["右减左", "right − left"], f(r.right - r.left) + (Math.abs(r.right - r.left) > 0.016 ? T("（超过公差 16 µm）", " (exceeds 16 µm)") : "")],
      [["沿轴向的形状", "shape along the axis"], T(sh[0], sh[1]) + " · " + T("锥度 ", "taper ") + f(r.taper) + T("，中凸 ", ", crown ") + f(r.crown)],
      [["垂直面误差造成的直径变化", "from the vertical bow"], api.fmt(r.vert * 1e6, 2) + " nm"],
      [["截面圆度", "roundness"], f(r.round) + (r.round > 0 ? T("（椭圆）", " (oval)") : "")],
    ];
  },
  draw(api) {
    const h = api.m["E-ACC-CENTERS"];
    if (!h || !h.parts) return;
    const p = api.p, k = api.keep, key = [p.e, p.bh, p.bv, p.sp, p.k].join("|");
    if (key === k.key) return;
    k.key = key;
    const T = api.three, r = err54(p), K = p.k;
    // 尾座、后顶尖按放大后的偏移移动（模型坐标 y）
    k.tail.forEach((q) => { if (q.obj) { q.obj.position.copy(q.p0); q.obj.position.y -= K * p.e / 1e6; } });   // 毫米 → 米
    // 工件网格：x 方向 60 段、圆周 72 段；半径 = R + K·（半径误差）
    const nx = 60, nt = 72, pos = [], idx = [];
    for (let i = 0; i <= nx; i++) {
      const x = L * i / nx, dr = r.dd(x) / 2;
      for (let j = 0; j <= nt; j++) {
        const t = 2 * Math.PI * j / nt, rr = R + K * (dr - p.sp / 1000 * Math.cos(2 * t));
        pos.push(x, -K * p.e / 1000 * x / L + rr * Math.cos(t), rr * Math.sin(t));   // 工件轴线随尾座顶尖倾斜
      }
    }
    for (let i = 0; i < nx; i++) for (let j = 0; j < nt; j++) {
      const a = i * (nt + 1) + j, b = a + nt + 1;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
    for (const x of [0, L]) {                       // 两端面
      const c = pos.length / 3; pos.push(x, -K * p.e / 1000 * x / L, 0);
      const i0 = x === 0 ? 0 : nx * (nt + 1);
      for (let j = 0; j < nt; j++) idx.push(c, i0 + j, i0 + j + 1);
    }
    const g = new T.BufferGeometry();
    g.setAttribute("position", new T.Float32BufferAttribute(pos, 3));
    g.setIndex(idx); g.computeVertexNormals();
    if (k.mesh) { h.base.remove(k.mesh); k.mesh.geometry.dispose(); }
    k.mesh = new T.Mesh(g, k.mat);
    k.mesh.scale.set(0.001, 0.001, 0.001);
    h.base.add(k.mesh);
    k.tags.forEach((s) => h.base.remove(s)); k.tags = [];
    const tg = (txt, x, y, z, col) => { const s = FX.tag(api, txt, col); s.position.set(x / 1000, y / 1000, z / 1000); h.base.add(s); k.tags.push(s); };
    tg(api.T("左轴承位 ", "left ") + api.fmt(r.left * 1000, 1), XL, -10, R + 22, "#4f7fb8");
    tg(api.T("右轴承位 ", "right ") + api.fmt(r.right * 1000, 1), XR, -10, R + 22, "#d98c3a");
  },
});
