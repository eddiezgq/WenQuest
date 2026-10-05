// 实验 50.2 SH-301 从毛坯到成品（配 50.2 节）。零件库 E-WKP-SH301：毛坯和工序 20、40、50、60 后的五个状态各一个节点，
// 由工艺规程 std/SH-301_process.yaml 的工序简图数据生成（factory/digital/models3d/workpiece.py，与图 50.2.1、动画 50.2.1 同一份），
// 橙色为该工序加工的面。零件库里五个状态沿 y 排开，这里按 home_mm 移回同一位置，一次只显示一个。
// 总长、最大外圆由显示的模型实时量出（包围盒），不是写死的数。
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
const ST = [
  { op: "10 下料", wc: "带锯床 SAW-01", face: "两端锯切面", zh: "毛坯", en: "blank" },
  { op: "20 粗车", wc: "数控车床 CNC-L01", face: "全部外圆、两端面、两中心孔（两次安装）", zh: "粗车后（调质前）", en: "rough-turned" },
  { op: "40 精车", wc: "数控车床 CNC-L01", face: "全部外圆、轴肩、总长 167（两顶尖）", zh: "精车后（调质后）", en: "finish-turned" },
  { op: "50 铣键槽", wc: "键槽铣床 KEY-01", face: "键槽 12 N9 × 45（夹具 JJ-301-50）", zh: "铣键槽后", en: "keyway milled" },
  { op: "60 磨外圆", wc: "外圆磨床 GRD-01", face: "两轴承位 Ø35 k6、齿轮位 Ø40 k6（两顶尖）", zh: "成品", en: "finished" },
];

WQ.lab({
  title: ["实验 50.2 SH-301 从毛坯到成品", "Lab 50.2 SH-301 from blank to finished part"],
  goal: ["一个状态一个状态地看 SH-301：每道工序加工了哪些面、尺寸怎样一步步接近图纸。",
         "Step through the states of SH-301: which faces each operation machines and how the sizes close in on the drawing."],
  view: "3d",
  models: ["E-WKP-SH301"],
  scenes: [
    { id: "shaft", name: ["SH-301 输出轴", "Output shaft SH-301"],
      problem: { title: ["工程问题：工艺过程怎样把毛坯变成零件", "Engineering problem: how a process turns a blank into a part"],
                 text: ["工序卡一张张看，很难在脑子里拼出零件的变化。把每道工序之后的工件画出来，就看得出哪道工序加工哪些面、留多少余量、哪些面是后面工序的基准。",
                        "Reading sheet after sheet, it is hard to picture the part changing. Drawing the work after each operation shows which faces each one machines, what allowance it leaves and which faces become datums for later operations."] } },
  ],
  params: [
    { id: "s", name: ["状态（0 毛坯、1 工序 20、2 工序 40、3 工序 50、4 工序 60）", "State (0 blank, 1 op 20, 2 op 40, 3 op 50, 4 op 60)"], min: 0, max: 4, step: 1, value: 0, unit: "", digits: 0 },
    { id: "cut", name: ["剖开（过轴线）", "Section through the axis"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "len", text: ["找出总长第一次到 167 mm 的状态，说出是哪道工序车到的。", "Find the first state with the overall length at 167 mm and the operation that made it."],
      demo: { scene: "shaft", set: { s: 2, cut: 0 }, press: [], wait: 1 } },
    { id: "key", text: ["找出键槽在哪道工序出现；它为什么排在精车之后、磨削之前？", "Find where the keyway appears; why after finish-turning and before grinding?"],
      demo: { scene: "shaft", set: { s: 3, cut: 0 }, press: [], wait: 1 } },
    { id: "grind", text: ["比较工序 40 和工序 60 的齿轮位直径，读出直径上的磨削余量。", "Compare the gear-seat diameter after op 40 and op 60; read the grinding allowance on the diameter."],
      demo: { scene: "shaft", set: { s: 4, cut: 0 }, press: [], wait: 1 } },
    { id: "centre", text: ["把成品剖开，看两端的中心孔：精车和磨削都以它们为基准。", "Section the finished shaft and look at the centre holes at both ends: the datum for finish-turning and grinding."],
      demo: { scene: "shaft", set: { s: 4, cut: 1 }, press: [], wait: 1 } },
  ],
  think: ["工序 20 粗车后留下的余量是给什么用的？如果调质后不再精车直接磨削，会有什么问题？",
          "What is the allowance left by op 20 for? What would go wrong if the shaft were ground straight after heat treatment without finish-turning?"],

  setup3d(api, keep) {
    const h = api.m["E-WKP-SH301"];
    FX.setup(api, h);
    h.parts.forEach((p) => { const m = p.home_mm || [0, 0, 0]; if (p.obj) { p.p0.add(new api.three.Vector3(m[0], m[1], m[2]).multiplyScalar(0.001)); p.obj.position.copy(p.p0); } });
    keep.seen = new Set();
    keep.key = "";
    h.parts.forEach((p, i) => { if (p.obj) p.obj.visible = i === 0; });
    api.view(30, 24, 1.05, h);
  },
  measure(api) {
    const h = api.m["E-WKP-SH301"], p = h.parts[Math.round(api.p.s)];
    if (!p || !p.obj) return null;
    const T = api.three, b = new T.Box3().setFromObject(p.obj), sz = b.getSize(new T.Vector3());
    return { L: sz.x * 1000, D: Math.max(sz.y, sz.z) * 1000 };   // 世界 x = 轴线方向；直径取两个横向尺寸中大的（网格顶点不一定落在某一方向的最高点上）
  },
  readouts(api) {
    const h = api.m["E-WKP-SH301"];
    if (!h || !h.parts) return [];
    const s = Math.round(api.p.s), st = ST[s], m = this.measure(api);
    api.keep.seen.add(s);
    if (s === 2) api.done("len");
    if (s === 3) api.done("key");
    if (s === 4 && api.keep.seen.has(2)) api.done("grind");
    if (s === 4 && api.p.cut) api.done("centre");
    return [[["状态", "state"], `${st.zh} / ${st.en}`], [["工序、工作中心", "operation, work centre"], `${st.op}　${st.wc}`],
            [["本工序加工的面（橙色）", "faces machined (orange)"], st.face],
            [["总长（量出）", "overall length (measured)"], m ? api.fmt(m.L, 1) + " mm" : "—"],
            [["最大外圆（量出）", "largest diameter (measured)"], m ? "Ø" + api.fmt(m.D, 2) + " mm" : "—"],
            [["图纸", "drawing"], "总长 167，齿轮位 Ø40 k6，轴承位 Ø35 k6 / length 167, gear seat Ø40 k6, bearing seats Ø35 k6"]];
  },
  draw(api) {
    const h = api.m["E-WKP-SH301"];
    if (!h || !h.parts) return;
    const s = Math.round(api.p.s), key = s + "|" + api.p.cut;
    if (key === api.keep.key) return;
    api.keep.key = key;
    h.parts.forEach((p, i) => { if (p.obj) p.obj.visible = i === s; });
    FX.clip(api, h, api.p.cut ? FX.plane(api, h, [0, 0, 0], [0, 1, 0]) : null);
  },
});
