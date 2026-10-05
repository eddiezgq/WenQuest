// 实验 52.1 JJ-301-50 拆装与剖切（配 52.1 节）。零件库 E-ASM-JJ30150：模型与书中插图、总图、数字工厂是同一份
// （factory/digital/models3d/jj30150.py）。entry.assembly.parts 给出每个零件的节点、名称、序号、作用和爆炸方向（毫米，模型坐标 Z 向上）。
// 拆开：各零件沿爆炸方向移动 k 倍；剖开：过工件轴线的竖直平面（模型 y = 0）剖切，保留 y ≥ 0 的一半；突出显示：其余零件变成半透明。
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
const ROLES = ["全部", "定位", "夹紧", "对刀导向", "夹具体", "工件"];
const ROLES_EN = ["all", "locating", "clamping", "setting/guiding", "body", "workpiece"];

WQ.lab({
  title: ["实验 52.1 JJ-301-50 的拆装与剖切", "Lab 52.1 Taking JJ-301-50 apart"],
  goal: ["把键槽铣夹具拆开、剖开，按作用认出每个零件：哪些定位、哪些夹紧、哪个对刀、哪个是夹具体。",
         "Explode and section the keyway milling fixture and sort its parts by function: locating, clamping, setting, body."],
  view: "3d",
  models: ["E-ASM-JJ30150"],
  scenes: [
    { id: "jj", name: ["JJ-301-50 键槽铣夹具", "JJ-301-50 keyway milling fixture"],
      problem: { title: ["工程问题：一套夹具由哪几部分组成", "Engineering problem: what a fixture is made of"],
                 text: ["SH-301 在工序 50 铣键槽，用的是专用夹具 JJ-301-50。拿到一套陌生的夹具，先要分清每个零件的作用——定位元件决定工件的位置，夹紧装置保持这个位置，对刀块确定刀具的位置，夹具体把它们连成一个整体并装到机床上。",
                        "SH-301 is keyway-milled in operation 50 on the dedicated fixture JJ-301-50. Faced with an unfamiliar fixture, first sort out what each part does: locators fix the work's position, clamps keep it there, the setting block places the cutter and the body ties them together and mounts on the machine."] } },
  ],
  params: [
    { id: "k", name: ["拆开程度", "Explode"], min: 0, max: 1, step: 0.05, value: 0, unit: "", digits: 2 },
    { id: "cut", name: ["剖开（过工件轴线）", "Section through the work axis"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "role", name: ["突出显示（0 全部、1 定位、2 夹紧、3 对刀导向、4 夹具体、5 工件）", "Highlight (0 all, 1 locating, 2 clamping, 3 setting, 4 body, 5 work)"],
      min: 0, max: 5, step: 1, value: 0, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "apart", text: ["把夹具完全拆开（拆开程度拉到 1），看各零件按什么顺序装上去。", "Explode the fixture fully (1) and see the order the parts go on."],
      demo: { scene: "jj", set: { k: 1, cut: 0, role: 0 }, press: [], wait: 1 } },
    { id: "loc", text: ["只突出定位元件，数一数有几个，各限制几个自由度。", "Highlight the locators only; count them and their constrained degrees of freedom."],
      demo: { scene: "jj", set: { k: 0, cut: 0, role: 1 }, press: [], wait: 1 } },
    { id: "clamp", text: ["只突出夹紧元件：压板、螺柱、压板后端的支承。", "Highlight the clamping parts: straps, studs and the strap heel supports."],
      demo: { scene: "jj", set: { k: 0, cut: 0, role: 2 }, press: [], wait: 1 } },
    { id: "set", text: ["找出对刀块：它的两个工作面分别对键槽的哪一个尺寸？", "Find the setting block: which keyway dimensions do its two faces set?"],
      demo: { scene: "jj", set: { k: 0, cut: 0, role: 3 }, press: [], wait: 1 } },
    { id: "cut", text: ["装好状态下剖开，看工件的齿轮位外圆怎样坐在 V 形块的两个工作面上。", "With everything assembled, section it and see how the gear seat sits on the two V faces."],
      demo: { scene: "jj", set: { k: 0, cut: 1, role: 1 }, press: [], wait: 1 } },
  ],
  think: ["JJ-301-50 的 V 形块和轴向挡板一共限制了 5 个自由度，工件绕自身轴线的转动没有限制。铣键槽为什么可以不限制它？如果键槽要和另一个已有的键槽对齐，该怎么办？",
          "The V-block and the axial stop restrict 5 degrees of freedom; rotation about the work axis is free. Why is that acceptable for this keyway? What if it had to line up with an existing keyway?"],

  setup3d(api, keep) {
    const h = api.m["E-ASM-JJ30150"];
    FX.setup(api, h);
    keep.tags = [];
    keep.key = "";
    api.view(35, 26, 1.15, h);
  },
  readouts(api) {
    const h = api.m["E-ASM-JJ30150"];
    if (!h || !h.parts) return [];
    const r = Math.round(api.p.role);
    const sel = h.parts.filter((p) => r === 0 || p.role === ROLES[r]);
    if (api.p.k >= 0.95) api.done("apart");
    if (r === 1 && api.p.k < 0.05 && !api.p.cut) api.done("loc");
    if (r === 2) api.done("clamp");
    if (r === 3) api.done("set");
    if (api.p.cut && api.p.k < 0.05) api.done("cut");
    const names = [...new Set(sel.map((p) => p.name.replace(/\d+$/, "")))];
    const rows = [[["突出显示", "highlight"], ROLES[r] + " / " + ROLES_EN[r]],
                  [["零件数（共 " + h.parts.length + " 个）", "parts (of " + h.parts.length + ")"], String(sel.length)],
                  [["零件", "parts"], names.join("、")]];
    if (r === 1) rows.push([["限制的自由度", "constrained DOF"], "V 形块两段工作面 4 个 + 轴向挡板 1 个 = 5 个"]);
    if (r === 2) rows.push([["夹紧力", "clamping force"], "两个压板，螺母拧到 5 N·m（52.3 节算出够用）"]);
    if (r === 3) rows.push([["对刀", "setting"], "内角底面对槽底深度，侧面对键槽对称面，都隔 3 mm 塞尺"]);
    return rows;
  },
  draw(api) {
    const h = api.m["E-ASM-JJ30150"];
    if (!h || !h.parts) return;
    const r = Math.round(api.p.role), key = [api.p.k, api.p.cut, r].join("|");
    if (key === api.keep.key) return;
    api.keep.key = key;
    FX.explode(api, h, api.p.k);
    FX.look(h, (p) => (r === 0 || p.role === ROLES[r] ? 1 : 0.15));
    FX.clip(api, h, api.p.cut ? FX.plane(api, h, [0, 0, 0], [0, 1, 0]) : null);
    api.keep.tags.forEach((t) => api.st.scene.remove(t));
    api.keep.tags = [];
    if (r > 0) {
      const T = api.three, seen = new Set();
      h.parts.filter((p) => p.role === ROLES[r] && p.obj).forEach((p) => {
        const base = p.name.replace(/\d+$/, "");
        if (seen.has(base)) return;
        seen.add(base);
        const b = new T.Box3().setFromObject(p.obj), c = b.getCenter(new T.Vector3());
        const t = FX.tag(api, (p.number ? p.number + " " : "") + base, "#0b5cad");
        t.position.set(c.x, b.max.y + 0.012, c.z);
        api.keep.tags.push(t);
      });
    }
  },
});
