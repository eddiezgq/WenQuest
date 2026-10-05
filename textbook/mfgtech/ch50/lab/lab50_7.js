// 实验 50.7 按作业指导书装夹 SH-301（配 50.7 节）。零件库 E-ASM-JJ30150（与第 52 章的总图、插图同一份）。
// 夹具已经装在键槽铣床上、对好刀（第 52 章）；这里是操作工每装一件要做的七步。工件先悬在上方，
// 放进 V 形块时离挡板 6 mm，推向挡板后贴紧；压板先抬起 40 mm，推出、压下后拧紧。
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
const STEPS = [
  { zh: "清理 V 形块、挡板和压板上的切屑", en: "Clean chips off the V-block, stop and straps", key: "用毛刷，不许用压缩空气对着 V 形块吹（切屑会吹进缝里）", keyEn: "Use a brush; never blow air at the V-block (chips get into the gaps)", tool: "毛刷 / brush" },
  { zh: "放工件：齿轮位放进 V 形块，键槽位置朝上", en: "Place the work: gear seat in the V, keyway side up", key: "两手托住工件放下，不要在 V 形块上拖动", keyEn: "Lower it with both hands; do not drag it along the V", tool: "—" },
  { zh: "推向挡板：左轴肩贴紧轴向挡板", en: "Push to the stop: left shoulder against the axial stop", key: "关键点：轴肩与挡板之间不许有缝，用 0.03 mm 塞尺检查塞不进", keyEn: "Key point: no gap at the stop; a 0.03 mm feeler must not enter", tool: "0.03 mm 塞尺 / feeler" },
  { zh: "推出两块压板，压在两端的轴颈上", en: "Slide both straps out onto the end journals", key: "压板压在离 V 形块外端约 20 mm 处，不许压在齿轮位上", keyEn: "Straps about 20 mm outside the V lands, never on the gear seat", tool: "—" },
  { zh: "用定扭矩扳手拧紧两个螺母", en: "Tighten both nuts with the torque wrench", key: "关键点：拧到 5 N·m 扳手打滑为止，两边交替拧", keyEn: "Key point: 5 N·m until the wrench slips, alternating sides", tool: "定扭矩扳手 5 N·m / torque wrench" },
  { zh: "启动：铣刀朝挡板方向分层铣键槽", en: "Start: the cutter feeds toward the stop, in layers", key: "安全：主轴旋转时不得测量、不得清理切屑；关好防护门", keyEn: "Safety: no measuring or chip clearing while the spindle turns; close the guard", tool: "键槽铣刀 Ø12 / keyway cutter" },
  { zh: "松开、取件、自检", en: "Release, unload, self-check", key: "自检：键槽宽 12 N9 用塞规 G06 每件；槽底尺寸 H 用专用量规 G07 首件、每 5 件；对称度用检具 G08 首件、每 10 件", keyEn: "Self-check: width 12 N9 with plug gauge G06 every part; depth H with gauge G07 first part and every 5th; symmetry with G08 first part and every 10th", tool: "G06、G07、G08" },
];
const FIX_STRAP = /^(压板|螺柱|垫圈螺母|弹簧)/;

WQ.lab({
  title: ["实验 50.7 按作业指导书装夹 SH-301", "Lab 50.7 Loading SH-301 by the work instruction"],
  goal: ["一步一步照作业指导书在 JJ-301-50 上装夹 SH-301，认清每一步的关键点、工具和自检项目。",
         "Follow the work instruction step by step to load SH-301 on JJ-301-50 and see each step's key point, tool and self-check."],
  view: "3d",
  models: ["E-ASM-JJ30150"],
  scenes: [
    { id: "op50", name: ["工序 50 铣键槽", "Op 50 keyway milling"],
      problem: { title: ["工程问题：让新员工看了就会做", "Engineering problem: a newcomer must be able to do it from the sheet"],
                 text: ["工序卡写的是“以齿轮位外圆和左轴肩定位，压板夹紧”。操作工要知道的是：工件怎么放、推到哪里算到位、拧多紧、做完量什么。作业指导书把这些写成一步一张图。",
                        "The operation sheet says “locate on the gear seat and left shoulder, clamp with straps”. The operator needs to know how to place the work, when it is home, how tight to clamp and what to check. The work instruction gives one picture per step."] } },
  ],
  params: [{ id: "step", name: ["步骤", "Step"], min: 1, max: 7, step: 1, value: 1, unit: "", digits: 0 }],
  tasks: [
    { id: "home", text: ["做到第 3 步：工件推到位，说出怎样确认轴肩贴紧了挡板。", "Go to step 3: the work is home; how do you confirm the shoulder is against the stop?"],
      demo: { scene: "op50", set: { step: 3 }, press: [], wait: 1 } },
    { id: "torque", text: ["做到第 5 步：拧紧扭矩是多少？为什么要用定扭矩扳手？", "Go to step 5: what torque, and why a torque wrench?"],
      demo: { scene: "op50", set: { step: 5 }, press: [], wait: 1 } },
    { id: "check", text: ["做完第 7 步，列出自检项目和用的量具。", "Finish step 7 and list the self-checks and their gauges."],
      demo: { scene: "op50", set: { step: 7 }, press: [], wait: 1 } },
  ],
  think: ["如果第 3 步漏做（工件离挡板还有 0.5 mm），键槽的哪个尺寸会超差？工序卡上的“铣刀朝挡板方向进给”能不能补救？",
          "If step 3 is skipped (the work 0.5 mm off the stop), which keyway dimension goes wrong? Does “feed toward the stop” on the operation sheet save it?"],

  setup3d(api, keep) {
    const h = api.m["E-ASM-JJ30150"], T = api.three;
    FX.setup(api, h);
    keep.key = "";
    keep.tags = [];
    h.root.updateMatrixWorld(true);
    const body = h.parts.find((p) => p.name === "夹具体"), bb = new T.Box3().setFromObject(body.obj);
    const table = new T.Mesh(new T.BoxGeometry(0.62, 0.03, 0.32), new T.MeshStandardMaterial({ color: 0x9aa3ab, roughness: 0.7 }));
    table.position.set((bb.min.x + bb.max.x) / 2, bb.min.y - 0.016, (bb.min.z + bb.max.z) / 2);   // 工作台（示意），夹具体底面落在台面上
    api.st.scene.add(table);
    const T2 = new T.Mesh(new T.CylinderGeometry(0.006, 0.006, 0.03, 24), new T.MeshStandardMaterial({ color: 0xe0b84f, metalness: 0.4 }));
    keep.cutter = T2; T2.visible = false; api.st.scene.add(T2);
    api.view(30, 30, 1.15, h);
  },
  readouts(api) {
    const n = Math.round(api.p.step), s = STEPS[n - 1];
    if (n === 3) api.done("home");
    if (n === 5) api.done("torque");
    if (n === 7) api.done("check");
    return [[["步骤", "step"], `${n} / ${STEPS.length}`], [["操作", "action"], s.zh + " / " + s.en],
            [["要点", "key point"], s.key + " / " + s.keyEn], [["工具、量具", "tools, gauges"], s.tool]];
  },
  draw(api) {
    const h = api.m["E-ASM-JJ30150"];
    if (!h || !h.parts) return;
    const n = Math.round(api.p.step);
    if (String(n) === api.keep.key) return;
    api.keep.key = String(n);
    const T = api.three, V = (x, y, z) => new T.Vector3(x, y, z).multiplyScalar(0.001);
    const work = h.parts.find((p) => p.name.startsWith("工件"));
    h.parts.forEach((p) => { if (p.obj) p.obj.position.copy(p.p0); });
    if (work) {
      if (n <= 1 || n >= 7) work.obj.position.copy(work.p0).add(V(0, 0, 90));     // 悬在上方：放之前、取出之后
      else if (n === 2) work.obj.position.copy(work.p0).add(V(6, 0, 0));          // 放进 V 形块，离挡板 6 mm
    }
    // 压板退回：沿压板长度方向（模型 y）向外退 25 mm、被弹簧顶起 8 mm；第 4 步推出、压下
    h.parts.filter((p) => FIX_STRAP.test(p.name)).forEach((p) => { if (n <= 3 || n >= 7) {
      if (p.name.startsWith("压板")) p.obj.position.copy(p.p0).add(V(0, 25, 8));
      else if (p.name.startsWith("垫圈螺母")) p.obj.position.copy(p.p0).add(V(0, 0, 8)); } });
    const hot = { 1: /^(V 形块|轴向挡板|压板)/, 2: /^(工件|V 形块)/, 3: /^(工件|轴向挡板)/, 4: /^压板/, 5: /^垫圈螺母/, 6: /^工件/, 7: /^工件/ }[n];
    FX.look(h, (p) => (hot.test(p.name) ? 1 : 0.35));
    h.parts.forEach((p) => { if (!p.obj) return; p.obj.traverse((o) => { if (o.isMesh) o.material.emissive && o.material.emissive.setHex(hot.test(p.name) ? 0x1a3a66 : 0x000000); }); });
    const c = api.keep.cutter;
    c.visible = n === 6;
    if (work && n === 6) { const b = new T.Box3().setFromObject(work.obj), m = b.getCenter(new T.Vector3()); c.position.set(b.min.x + 0.082, b.max.y + 0.016, m.z); }
  },
});
