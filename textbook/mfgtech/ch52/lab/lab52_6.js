// 实验 52.6 回转式钻模的分度（配 52.6 节）。零件库 E-ASM-DRILLIDX（factory/digital/models3d/typical.py drill_indexing，与图 52.6.7、动画 52.6.2 同一份）。
// 心轴、分度盘、工件、螺母绕心轴轴线（模型 x 轴，y = 0、z = 80 mm）一起转；对定销沿 −x 拔出 30 mm。分度孔 6 个、在半径 48 mm 处；
// 钻套轴线竖直，在 x = 30 mm 处，钻 Ø10 径向孔。对定销与分度孔的间隙 c 使分度盘可以多转 Δθ ≈ c / R（R = 48 mm），
// 工件外圆（半径 25 mm）上孔位偏移 ≈ 25·Δθ。
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
const AX = [0, 0, 80], R_IDX = 48, R_WORK = 25, N = 6;
const ROT = ["p02", "p03", "p06", "p09"];     // 心轴、分度盘、工件（套筒）、螺母

const station = (a) => Math.abs(a / (360 / N) - Math.round(a / (360 / N))) < 1e-6;
// 分度盘实际所在的转角：对定销插着时锁在插入时的角度（拖动转角滑块也转不动）；拔出时跟着滑块走。
// 对定销带弹簧：插着（推向分度盘）而分度盘转到分度孔上时，自动弹进去锁住。
function lock(api) {
  const k = api.keep, a = k.lockAng != null ? k.lockAng : ((api.p.ang % 360) + 360) % 360;
  return { a, locked: k.lockAng != null, station: station(a), k: Math.round(a / (360 / N)) % N, stuck: k.lockAng != null && Math.abs(api.p.ang - k.lockAng) > 1e-6 };
}

WQ.lab({
  title: ["实验 52.6 回转式钻模的分度", "Lab 52.6 Indexing on a rotary drill jig"],
  goal: ["按“拔销—转位—插销—钻孔”的顺序在套筒上钻出圆周均布的孔，再看对定销间隙怎样变成孔位误差。",
         "Drill equally spaced radial holes in a sleeve by withdraw–turn–insert–drill, then see how the index-pin clearance becomes a hole position error."],
  view: "3d",
  models: ["E-ASM-DRILLIDX"],
  scenes: [
    { id: "jig", name: ["回转式钻模，6 等分", "Rotary drill jig, 6 divisions"],
      problem: { title: ["工程问题：一次装夹钻出 6 个均布孔", "Engineering problem: six equally spaced holes in one set-up"],
                 text: ["套筒上要钻 6 个均布的径向孔。逐个划线找正太慢，也保证不了孔距；回转式钻模把工件连同分度盘一起转，对定销插进分度孔就确定了转角，钻套引导钻头，一次装夹钻完。",
                        "Six equally spaced radial holes are needed in a sleeve. Marking out each one is slow and inaccurate; the rotary jig turns the work with an index plate, the index pin fixes the angle and the bushing guides the drill, all in one set-up."] } },
  ],
  params: [
    { id: "ang", name: ["分度盘转角", "Index plate angle"], min: 0, max: 330, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "pin", name: ["对定销（0 拔出、1 插入）", "Index pin (0 out, 1 in)"], min: 0, max: 1, step: 1, value: 1, unit: "", digits: 0 },
    { id: "c", name: ["对定销与分度孔的间隙 c", "Pin-to-hole clearance c"], min: 0, max: 0.05, step: 0.005, value: 0.01, unit: "mm", digits: 3 },
  ],
  buttons: [{ id: "drill", name: ["钻孔", "Drill"], primary: true }, { id: "new", name: ["换一件新工件", "New workpiece"] }],
  tasks: [
    { id: "first", text: ["对定销插入、转角 0°，钻第一个孔。", "With the pin in at 0°, drill the first hole."],
      demo: { scene: "jig", set: { ang: 0, pin: 1, c: 0.01 }, press: ["drill"], wait: 1 } },
    { id: "blocked", text: ["把分度盘转到 30° 再插对定销：插不进去，钻孔也不允许。", "Turn to 30° and try the pin: it will not go in, and drilling is refused."],
      demo: { scene: "jig", set: { ang: 30, pin: 1 }, press: ["drill"], wait: 1 } },
    { id: "second", text: ["拔出对定销，转到 60°，插入对定销，钻第二个孔。", "Withdraw the pin, turn to 60°, insert it and drill the second hole."],
      demo: { scene: "jig", set: { ang: 60, pin: 1 }, press: ["drill"], wait: 1 } },
    { id: "err", text: ["把间隙调到 0.04 mm，读出孔位误差（本模型只算间隙一项，与 52.6 节例子的参数不同）。", "Set the clearance to 0.04 mm and read the hole position error (clearance only; the example in Section 52.6 uses other radii)."],
      demo: { scene: "jig", set: { c: 0.04 }, press: [], wait: 1 } },
  ],
  think: ["为什么分度孔要尽量布置在大半径上？如果改用圆锥对定销，间隙一项会变成多少？还剩下哪些误差？",
          "Why put the index holes on as large a radius as possible? With a taper pin, what happens to the clearance term, and which errors remain?"],

  change(api, s, pid) {
    const k = api.keep, a = ((api.p.ang % 360) + 360) % 360;
    if (pid === "pin") k.lockAng = api.p.pin && station(a) ? a : null;
    if (pid === "ang" && k.lockAng == null && api.p.pin && station(a)) k.lockAng = a;
  },
  setup3d(api, keep) {
    const h = api.m["E-ASM-DRILLIDX"];
    FX.setup(api, h);
    keep.holes = keep.holes || new Set();
    keep.lockAng = 0;                         // 开始时对定销插在 0° 的分度孔里
    keep.marks = [];
    keep.msg = "";
    keep.key = "";
    api.view(-40, 28, 1.25, h);
  },
  action(id, api) {
    const k = api.keep, L = lock(api);
    if (id === "new") { k.holes.clear(); k.msg = ""; k.key = ""; return; }
    if (id === "drill") {
      if (!api.p.pin) { k.msg = "对定销没有插入，分度盘会转动，不能钻 / pin out: the plate is free, do not drill"; return; }
      if (!L.locked) { k.msg = "对定销插不进分度孔，没有对定，不能钻 / the pin will not enter: not indexed, do not drill"; api.done("blocked"); return; }
      if (k.holes.has(L.k)) { k.msg = "这个位置已经钻过 / already drilled here"; return; }
      k.holes.add(L.k); k.msg = "钻好第 " + k.holes.size + " 个孔 / hole drilled"; k.key = "";
      if (L.k === 0) api.done("first");
      if (L.k === 1) api.done("second");
    }
  },
  readouts(api) {
    const L = lock(api), k = api.keep;
    if (api.p.c >= 0.04 - 1e-9) api.done("err");
    const dth = api.p.c / R_IDX, e = R_WORK * dth;
    const pinTxt = !api.p.pin ? "拔出 / out" : L.locked ? "插入，已对定 / in, indexed" : "顶在分度盘上，插不进（不在分度孔上）/ pressing on the plate, not in a hole";
    return [[["分度位置", "station"], L.station ? `第 ${L.k + 1} 个（${L.a}°）` : `${L.a}°（不在分度位置）`],
            [["对定销", "index pin"], pinTxt],
            [["已钻孔", "holes drilled"], k.holes ? `${k.holes.size} / ${N}：` + [...k.holes].sort((a, b) => a - b).map((i) => i * 60 + "°").join("、") : "0"],
            [["间隙引起的转角误差 Δθ ≈ c/R", "angle error Δθ ≈ c/R"], api.fmt(dth * 206265, 0) + "″"],
            [["工件外圆上的孔位误差 ≈ 25·Δθ", "hole position error ≈ 25·Δθ"], api.fmt(e * 1000, 1) + " µm"],
            [["提示", "note"], L.stuck ? "对定销插着，分度盘转不动：先拔出对定销 / the pin is in: withdraw it before turning" :
              (k.msg || "先插对定销再钻孔；换位时先拔销 / insert the pin before drilling; withdraw it to index")]];
  },
  draw(api) {
    const h = api.m["E-ASM-DRILLIDX"];
    if (!h || !h.parts) return;
    const L = lock(api), key = [L.a, L.locked, api.keep.holes ? api.keep.holes.size : 0].join("|");
    if (key === api.keep.key) return;
    api.keep.key = key;
    const T = api.three, th = L.a * Math.PI / 180;
    const q = new T.Quaternion().setFromAxisAngle(new T.Vector3(1, 0, 0), th);
    const c = new T.Vector3(AX[0], AX[1], AX[2]).multiplyScalar(0.001);
    ROT.forEach((n) => { const o = h.nodes[n]; if (!o) return; o.quaternion.copy(q); o.position.copy(c.clone().sub(c.clone().applyQuaternion(q))); });
    const pin = h.nodes.p05;
    if (pin) pin.position.set(L.locked ? 0 : -0.03, 0, 0);
    const work = h.nodes.p06;
    api.keep.marks.forEach((m) => { if (work) work.remove(m); });
    api.keep.marks = [];
    if (work && api.keep.holes) {
      api.keep.holes.forEach((i) => {     // 钻过的孔：在工件自己的坐标里，转到第 i 个分度位置时正对钻套（顶部）
        const a = -i * 2 * Math.PI / N, m = new T.Mesh(new T.CylinderGeometry(0.005, 0.005, 0.0105, 24), new T.MeshStandardMaterial({ color: 0x33363a }));
        const r = (R_WORK - 5) / 1000;
        m.position.set(0.03, -r * Math.sin(a), 0.08 + r * Math.cos(a));
        m.quaternion.setFromAxisAngle(new T.Vector3(1, 0, 0), a).multiply(new T.Quaternion().setFromAxisAngle(new T.Vector3(1, 0, 0), Math.PI / 2));
        work.add(m); api.keep.marks.push(m);
      });
    }
  },
});
