// 实验 51.3 六点定位（配 51.3 节）。支承钉取自零件库 E-LOC-SPINA（A 型平头支承钉，factory/digital/models3d/elements.py），
// 每个支承点复制一个；工件（长方体 120 × 80 × 40、轴 Ø40 × 160）在实验里直接画出。坐标按书：x 沿工件长度（轴线），z 向上。
// 支承钉的头部顶面在模型原点、轴线沿模型 z；放置时把模型 z（网页里的 y 向上）转到“从支承钉指向工件”的方向。
const DOF = { tx: "沿 x 移动", ty: "沿 y 移动", tz: "沿 z 移动", rx: "绕 x 转动", ry: "绕 y 转动", rz: "绕 z 转动" };
const DOF_EN = { tx: "x translation", ty: "y translation", tz: "z translation", rx: "x rotation", ry: "y rotation", rz: "z rotation" };
// 书中坐标（毫米）→ 网页世界坐标（米）：x → x，y → −z，z → y；工件整体抬高 30 mm（支承钉在底下）
const W = (x, y, z) => [x / 1000, z / 1000 + 0.03, -y / 1000];
const D = (x, y, z) => [x, z, -y];               // 方向向量同样换算
const SC = {
  box: { pts: [   // 3–2–1：底面三点、侧面（y = 0）两点、端面（x = 0）一点；每点新限制的自由度
    { at: [20, 15, 0], n: [0, 0, 1], adds: ["tz"] }, { at: [100, 15, 0], n: [0, 0, 1], adds: ["ry"] }, { at: [60, 65, 0], n: [0, 0, 1], adds: ["rx"] },
    { at: [25, 0, 20], n: [0, 1, 0], adds: ["ty"] }, { at: [95, 0, 20], n: [0, 1, 0], adds: ["rz"] },
    { at: [0, 40, 20], n: [1, 0, 0], adds: ["tx"] }] },
  shaft: { pts: [   // 两段 V 形块：每段两个点（±45°），轴向挡板一点；绕轴线的转动不限制
    { at: [30, -14.14, 25.86], n: [0, 0.7071, 0.7071], adds: ["tz"] }, { at: [30, 14.14, 25.86], n: [0, -0.7071, 0.7071], adds: ["ty"] },
    { at: [130, -14.14, 25.86], n: [0, 0.7071, 0.7071], adds: ["ry"] }, { at: [130, 14.14, 25.86], n: [0, -0.7071, 0.7071], adds: ["rz"] },
    { at: [0, 0, 40], n: [1, 0, 0], adds: ["tx"] }] },
};

WQ.lab({
  title: ["实验 51.3 六点定位", "Lab 51.3 The six-point principle"],
  goal: ["一个一个加上支承点，看每个点限制了工件的哪一个自由度，六个点怎样把工件的位置完全确定。",
         "Add the support points one at a time; see which degree of freedom each one takes and how six points fix the work completely."],
  view: "3d",
  models: ["E-LOC-SPINA"],
  scenes: [
    { id: "box", name: ["长方体：3–2–1 定位", "Block: 3–2–1 location"],
      problem: { title: ["工程问题：工件放上夹具，靠什么确定位置", "Engineering problem: what fixes the work's position in a fixture"],
                 text: ["工件放在夹具上，必须每次都落在同一个位置。空间里的工件有六个自由度，夹具用合理分布的支承点一个一个把它们限制住。",
                        "Every workpiece must land in the same place. A body in space has six degrees of freedom; the fixture takes them away one by one with well-placed support points."] } },
    { id: "shaft", name: ["轴：V 形块 + 挡板（SH-301 铣键槽）", "Shaft: V-block + stop (SH-301 keyway)"],
      params: { n: { max: 5 } },
      problem: { title: ["生活中的例子：笔放在书桌的 V 形槽里", "Everyday example: a pen in the groove of a desk"],
                 text: ["笔放在笔槽里不会滚走，推到槽的一端就不能再前后移动，但还能绕自己的轴线转。SH-301 在 JJ-301-50 上也是这样：五个点，绕轴线的转动不限制。",
                        "A pen in a groove cannot roll away and, pushed to one end, cannot slide, but it can still turn about its axis. SH-301 on JJ-301-50 is the same: five points, rotation about the axis left free."] } },
  ],
  params: [{ id: "n", name: ["支承点数", "Support points"], min: 0, max: 6, step: 1, value: 0, unit: "", digits: 0 }],
  tasks: [
    { id: "three", text: ["长方体：底面放三个点，读出限制了哪三个自由度。", "Block: three points under the base; read the three restricted freedoms."],
      demo: { scene: "box", set: { n: 3 }, press: [], wait: 1 } },
    { id: "six", text: ["长方体：放满六个点，确认六个自由度全部限制。", "Block: all six points; confirm all six freedoms are restricted."],
      demo: { scene: "box", set: { n: 6 }, press: [], wait: 1 } },
    { id: "shaft", text: ["轴：放满五个点，找出没有限制的那个自由度，说明铣键槽为什么可以不限制它。", "Shaft: all five points; find the free one and say why the keyway can leave it free."],
      demo: { scene: "shaft", set: { n: 5 }, press: [], wait: 1 } },
  ],
  think: ["如果长方体底面的三个点排在一条直线上，会少限制哪一个自由度？如果侧面的两个点挨得很近，又会怎样？",
          "If the three base points were in a line, which freedom would be lost? What if the two side points were very close together?"],

  setup3d(api, keep) {
    const T = api.three, h = api.m["E-LOC-SPINA"];
    h.holder.position.set(0, 0, 0); h.holder.rotation.set(0, 0, 0);
    const orig = [...h.root.children];            // 零件库的支承钉：藏起原件，按支承点复制
    keep.pins = [];
    for (let i = 0; i < 6; i++) {
      const c = new T.Group();
      orig.forEach((o) => c.add(o.clone(true)));
      c.visible = false; h.root.add(c); keep.pins.push(c);
    }
    orig.forEach((o) => { o.visible = false; });
    const mat = new T.MeshStandardMaterial({ color: 0xe8c39e, roughness: 0.6, transparent: true, opacity: 0.85 });
    keep.box = new T.Mesh(new T.BoxGeometry(0.12, 0.04, 0.08), mat);
    keep.box.position.set(0.06, 0.03 + 0.02, -0.04);
    const cyl = new T.Mesh(new T.CylinderGeometry(0.02, 0.02, 0.16, 48), mat.clone());
    cyl.rotation.z = Math.PI / 2; cyl.position.set(0.08, 0.03 + 0.04, 0);
    keep.shaft = cyl;
    h.root.add(keep.box, cyl);                     // 挂在模型下面，api.view 取景时把工件也算进去
    keep.arrows = {};
    const red = 0xc0504d;
    for (const k of Object.keys(DOF)) {        // 六个自由度的符号：移动画直箭头、转动画带箭头的圆弧；绿 = 自由，灰 = 已限制
      const g = new T.Group(), ax = { x: new T.Vector3(1, 0, 0), y: new T.Vector3(0, 0, -1), z: new T.Vector3(0, 1, 0) }[k[1]];
      if (k[0] === "t") g.add(new T.ArrowHelper(ax, new T.Vector3(0, 0, 0), 0.05, red, 0.014, 0.009));
      else {
        const ring = new T.Mesh(new T.TorusGeometry(0.016, 0.0018, 8, 40, Math.PI * 1.5), new T.MeshBasicMaterial({ color: red }));
        ring.quaternion.setFromUnitVectors(new T.Vector3(0, 0, 1), ax);
        g.add(ring);
      }
      g.userData.k = k; h.root.add(g); keep.arrows[k] = g;
    }
    keep.key = "";
    api.view(35, 28, 0.9, h);
  },
  state(api) {
    const sc = SC[api.scene], n = Math.min(Math.round(api.p.n), sc.pts.length), held = new Set();
    sc.pts.slice(0, n).forEach((p) => p.adds.forEach((d) => held.add(d)));
    return { sc, n, held, free: Object.keys(DOF).filter((d) => !held.has(d)) };
  },
  readouts(api) {
    const s = this.state(api);
    if (api.scene === "box" && s.n >= 3) api.done("three");
    if (api.scene === "box" && s.n === 6) api.done("six");
    if (api.scene === "shaft" && s.n === 5) api.done("shaft");
    const last = s.n ? s.sc.pts[s.n - 1].adds.map((d) => DOF[d]).join("、") : "—";
    return [[["支承点", "support points"], `${s.n} / ${s.sc.pts.length}`],
            [["刚加上的点限制", "the last point restricts"], last],
            [["已限制（灰）", "restricted (grey)"], [...s.held].map((d) => DOF[d]).join("、") || "—"],
            [["还自由（红）", "still free (red)"], s.free.map((d) => DOF[d] + " / " + DOF_EN[d]).join("、") || "无，位置完全确定 / none: fully located"]];
  },
  draw(api) {
    const k = api.keep;
    if (!k.pins) return;
    const key = api.scene + "|" + api.p.n;
    if (key === k.key) return;
    k.key = key;
    const T = api.three, s = this.state(api), box = api.scene === "box";
    k.box.visible = box; k.shaft.visible = !box;
    k.pins.forEach((pin, i) => {
      const p = s.sc.pts[i];
      pin.visible = !!p && i < s.n;
      if (!p) return;
      const at = W(...p.at), n = D(...p.n);
      pin.position.set(...at);
      pin.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), new T.Vector3(...n).normalize());
    });
    const c = box ? new T.Vector3(0.06, 0.05, -0.04) : new T.Vector3(0.08, 0.07, 0);
    const off = { tx: [0.075, 0, 0], ty: [0, 0, -0.065], tz: [0, 0.045, 0], rx: [0.12, 0, 0], ry: [0, 0, -0.1], rz: [0, 0.075, 0] };
    for (const [d, g] of Object.entries(k.arrows)) {
      g.position.copy(c).add(new T.Vector3(...off[d]).multiplyScalar(box ? 1 : 1.1));
      const col = s.held.has(d) ? 0xb0b6bb : 0xc0504d;
      g.traverse((o) => { if (o.material) o.material.color && o.material.color.setHex(col); if (o.line) o.line.material.color.setHex(col); if (o.cone) o.cone.material.color.setHex(col); });
    }
  },
});
