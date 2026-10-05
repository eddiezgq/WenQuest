// 实验 51.5 常用定位元件（配 51.5 节）。八个元件取自零件库 E 部分（模型与书中插图同一份，factory/digital/models3d），
// 原理说明直接读零件库条目的 teaching.principle；“相当于几个支承点、限制哪几个自由度”按表 51.3.1。一次只显示一个元件。
const EL = [
  { id: "E-LOC-SPINA", face: "平面", pts: "1", dof: "一个移动", en: "one translation" },
  { id: "E-LOC-SPLATE", face: "平面", pts: "2（一块窄支承板）", dof: "一个移动、一个转动", en: "one translation, one rotation" },
  { id: "E-LOC-VB", face: "外圆", pts: "2（短 V 形块）；两段或长 V 形块为 4", dof: "两个移动（y、z）；长的再加绕 y、z 的转动", en: "two translations (y, z); long: plus rotations about y, z" },
  { id: "E-LOC-SLEEVE", face: "外圆", pts: "2（短套）；长套为 4", dof: "两个移动；长套再加两个转动", en: "two translations; long sleeve: plus two rotations" },
  { id: "E-LOC-PIN", face: "内孔", pts: "2（短销）", dof: "两个移动", en: "two translations" },
  { id: "E-LOC-DPIN", face: "内孔", pts: "1（与圆柱销、平面组合）", dof: "绕平面法线的转动", en: "rotation about the plane normal" },
  { id: "E-LOC-MANDREL", face: "内孔 + 端面", pts: "4 + 1", dof: "两个移动、两个转动（心轴）+ 一个移动（台肩）", en: "two translations, two rotations (mandrel) + one translation (collar)" },
  { id: "E-ACC-CENTERS", face: "中心孔", pts: "3 + 2", dof: "三个移动（前顶尖）+ 两个转动（后顶尖）", en: "three translations (fixed headstock centre) + two rotations (tailstock centre)" },
];

WQ.lab({
  title: ["实验 51.5 常用定位元件", "Lab 51.5 Common locating elements"],
  goal: ["逐个转动、细看常用定位元件，说出每个元件以工件的什么面定位、相当于几个支承点、限制哪几个自由度。",
         "Turn each common locator over; say which work surface it locates on, how many support points it equals and which freedoms it restricts."],
  view: "3d",
  models: EL.map((e) => e.id),
  scenes: [
    { id: "lib", name: ["零件库 E 部分的定位元件", "Locators from library part E"],
      problem: { title: ["工程问题：给工件的每个定位面挑元件", "Engineering problem: choose an element for each locating surface"],
                 text: ["定位方案定了“用哪几个面、限制哪几个自由度”以后，要给每个面挑一个定位元件：平面用支承钉、支承板，外圆用 V 形块、定位套，孔用定位销、心轴，中心孔用顶尖。挑之前先要认识它们。",
                        "Once the scheme says which surfaces and freedoms, each surface needs an element: rest buttons and plates for planes, V-blocks and sleeves for outside diameters, pins and mandrels for bores, centres for centre holes."] } },
  ],
  params: [{ id: "i", name: ["元件（1–8）", "Element (1–8)"], min: 1, max: 8, step: 1, value: 1, unit: "", digits: 0 }],
  tasks: [
    { id: "vb", text: ["看 V 形块：为什么说它“对中性好”？外圆直径变化时工件轴线往哪里移？", "V-block: why is it self-centring? Where does the axis move when the diameter changes?"],
      demo: { scene: "lib", set: { i: 3 }, press: [], wait: 1 } },
    { id: "pins", text: ["先看圆柱定位销、再看菱形销，比较两者的工作面，说出菱形销削去了哪两边。", "Look at the cylindrical pin, then the diamond pin; compare the working faces and say which sides are cut away."],
      demo: { scene: "lib", set: { i: 6 }, press: [], wait: 1 } },
    { id: "centres", text: ["看两顶尖：前、后顶尖合起来限制几个自由度？哪一个不限制？", "Centres: how many freedoms do the two together restrict, and which is left?"],
      demo: { scene: "lib", set: { i: 8 }, press: [], wait: 1 } },
  ],
  think: ["SH-301 铣键槽用 V 形块，精车、磨削用两顶尖。为什么不都用两顶尖？在键槽铣床上用顶尖会遇到什么困难？",
          "SH-301 is keyway-milled on a V-block but turned and ground between centres. Why not centres for both? What would go wrong on the keyway mill?"],

  setup3d(api, keep) {
    keep.seen = new Set();
    keep.key = "";
    EL.forEach((e) => { const h = api.m[e.id]; h.place(0, 0); h.visible(false); });
  },
  readouts(api) {
    const i = Math.round(api.p.i) - 1, e = EL[i], h = api.m[e.id];
    if (!h) return [];
    api.keep.seen.add(i);
    if (i === 2) api.done("vb");
    if (i === 5) api.done("pins");
    if (i === 7) api.done("centres");
    const T = api.three, sz = h.box().getSize(new T.Vector3());
    return [[["元件", "element"], `${e.id}　${h.entry.name.zh}`], [["Element", "Element"], h.entry.name.en],
            [["工件定位面", "work surface"], e.face], [["相当于支承点数", "support points"], e.pts],
            [["限制的自由度（表 51.3.1）", "restricted (Table 51.3.1)"], e.dof + " / " + e.en],
            [["外形（模型量出）", "size (measured)"], [sz.x, sz.z, sz.y].map((v) => api.fmt(v * 1000, 0)).join(" × ") + " mm"],
            [["原理（零件库条目）", "principle (library entry)"], h.entry.teaching ? h.entry.teaching.principle : ""]];
  },
  draw(api) {
    const i = Math.round(api.p.i) - 1;
    if (String(i) === api.keep.key) return;
    api.keep.key = String(i);
    EL.forEach((e, k) => api.m[e.id] && api.m[e.id].visible(k === i));
    api.view(35, 24, 0.75, api.m[EL[i].id]);
  },
});
