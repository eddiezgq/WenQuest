// 实验 56.4 选精基准（配 56.4 节）。零件库 E-ACC-CENTERS（两顶尖）；SH-101、V 形块、输出法兰由程序按尺寸生成（std/SH-101_part.yaml）。
// 计算与程序 56.4.1（ex56_4.py，hub/tolerance.py）相同：
//   基准不重合误差：从左端面编程时，8 ± 0.1 由“左端面→齿轮左端面 81”与“左端面→轴肩 73”间接得到，封闭环公差 = 两者公差之和；
//     基准不重合误差 = 联系尺寸 73 的公差 2t；从轴肩编程时 8 由一刀直接保证（公差 2t）。
//   齿顶圆跳动中由基准引起的部分：A 两端中心孔 2·e_c；B 一夹一顶（夹轴伸 x = 18，尾顶尖 x = 136，齿轮 x = 96）TIR·(136−96)/(136−18)；
//     C 卡盘夹轴承位 TIR。卡盘跳动 TIR、中心孔偏移 e_c 为示意值。
//   V 形块（夹角 α）定位外圆（公差 Td）：工序基准在下母线 Td/2·(1/sin(α/2) − 1)，在轴线 Td/(2 sin(α/2))，在上母线 Td/2·(1/sin(α/2) + 1)；
//     对称面上没有对称度的定位误差。
//   输出法兰：内孔 Ø40 H7 与止口 Ø62 h7 的同轴度要求 Ø0.02（示意）；一次装夹车出取主轴回转误差 0.005（示意），分两次装夹取卡盘定心跳动 TIR。
const SEG = [[20, 36, "轴伸"], [24, 20, "密封轴颈"], [25, 17, "左轴承位"], [30, 8, "左轴肩"], [52, 30, "齿轮"], [30, 8, "右轴肩"], [25, 17, "右轴承位"]];
const EC = 0.002;                    // 中心孔引起的轴线偏移（修研后，示意，同 ex56_4.py）
const L56 = 136, X_SH = 73, X_G = 81, XC = 18, XT = 136, XGM = 96, TOL_R = 0.03, TOL_K = 0.1, COAX = 0.02, SPIN = 0.005;
const SCH = [["A 两端中心孔贯穿始终", "A centre holes throughout"], ["B 精车齿顶圆一夹一顶（夹轴伸）", "B chuck on the extension + tail centre"], ["C 调头车，卡盘夹轴承位", "C chucked on a bearing seat"]];
const MEAS = [["下母线（槽深 d − t₁）", "bottom generatrix (depth d − t₁)"], ["轴线", "axis"], ["上母线", "top generatrix"]];

function eval56(p) {
  const s = Math.sin(p.alpha * Math.PI / 360);
  const runout = [2 * EC, p.tir * (XT - XGM) / (XT - XC), p.tir][Math.round(p.sch)];
  const vb = [p.td / 2 * (1 / s - 1), p.td / (2 * s), p.td / 2 * (1 / s + 1)][Math.round(p.meas)];
  const axial = Math.round(p.ax) === 0 ? { T: 4 * p.t, dB: 2 * p.t } : { T: 2 * p.t, dB: 0 };
  const coax = Math.round(p.fl) === 0 ? SPIN : p.tir;
  return { runout, vb, axial, coax };
}

const G56 = {
  mat(api, color) { const T = api.three; return new T.MeshStandardMaterial({ color, roughness: 0.6, metalness: 0.15, side: T.DoubleSide }); },
  lathe(api, prof, color) {          // prof：[[x, r], …]（mm），绕 x 轴回转
    const T = api.three, g = new T.LatheGeometry(prof.map(([x, r]) => new T.Vector2(r, x)), 72);
    const m = new T.Mesh(g, G56.mat(api, color)); m.rotation.z = -Math.PI / 2;
    const grp = new T.Group(); grp.add(m); grp.scale.set(0.001, 0.001, 0.001); return grp;
  },
  tag(api, text, color = "#1d2327") {
    const T = api.three, c = document.createElement("canvas"), g = c.getContext("2d");
    g.font = "bold 30px sans-serif"; const w = Math.ceil(g.measureText(text).width) + 20;
    c.width = w; c.height = 44; g.font = "bold 30px sans-serif";
    g.fillStyle = "rgba(255,255,255,0.88)"; g.fillRect(0, 0, w, 44); g.fillStyle = color; g.textBaseline = "middle"; g.fillText(text, 10, 23);
    const s = new T.Sprite(new T.SpriteMaterial({ map: new T.CanvasTexture(c), depthTest: false }));
    s.scale.set(0.018 * w / 44, 0.018, 1); s.renderOrder = 10; return s;
  },
};

WQ.lab({
  title: ["实验 56.4 选精基准", "Lab 56.4 Choosing the finishing datums"],
  goal: ["在 SH-101 和机器人关节输出法兰上，为几道工序选定位基准（编程原点、装夹方式），看基准不重合误差、定位误差，判断能不能保证图纸的位置和尺寸要求。",
         "On SH-101 and a robot-joint output flange, choose the datums (programming origin, work holding) for several operations; see the datum-mismatch and locating errors and judge whether the drawing's requirements can be held."],
  view: "3d",
  models: ["E-ACC-CENTERS"],
  scenes: [
    { id: "shaft", hide: ["alpha", "td", "meas", "fl"], name: ["SH-101：精车与滚齿", "SH-101: finish turning and hobbing"],
      params: { ax: { value: 0 }, t: { value: 0.1 }, sch: { value: 1 }, tir: { value: 0.03 } },
      problem: { title: ["工程问题：齿轮端面的位置和齿顶圆跳动靠什么保证", "Engineering problem: what holds the gear face position and the tip runout"],
                 text: ["SH-101 图纸：轴承定位轴肩到齿轮左端面 8 ± 0.1；齿顶圆对两轴承位公共轴线 A–B 的径向圆跳动 0.03。数控车程序从哪里编？精车、滚齿用什么装夹？",
                        "SH-101's drawing: shoulder to gear face 8 ± 0.1; tip-circle runout to the common bearing axis A–B 0.03. Where does the CNC program start, and how is the work held for turning and hobbing?"] } },
    { id: "key", hide: ["ax", "t", "sch", "tir", "fl"], name: ["SH-101：铣键槽（V 形块）", "SH-101: keyway on a V-block"],
      params: { alpha: { value: 90 }, td: { value: 0.05 }, meas: { value: 0 } },
      problem: { title: ["工程问题：V 形块定位铣键槽，槽深的定位误差多大", "Engineering problem: the depth error of a keyway milled on a V-block"],
                 text: ["轴伸精车到 Ø20.4（0/−0.05）后放在 V 形块上铣键槽 6 N9，槽深 d − t₁ 的公差 0.1。槽深从哪里量、V 形块取多大夹角，定位误差最小？",
                        "The extension, finish-turned to Ø20.4 (0/−0.05), sits on a V-block for the 6 N9 keyway; the depth d − t₁ has 0.1 tolerance. Which reference and which V angle give the least locating error?"] } },
    { id: "flange", robot: true, hide: ["ax", "t", "sch", "alpha", "td", "meas"], name: ["机器人关节输出法兰", "Robot-joint output flange"],
      params: { fl: { value: 1 }, tir: { value: 0.03 } },
      problem: { title: ["机器人问题：内孔与止口的同轴度", "Robot problem: coaxiality of the bore and the spigot"],
                 text: ["协作机器人关节的空心输出法兰：内孔 Ø40 H7 接谐波减速器，止口 Ø62 h7 定位下一节臂杆，两者同轴度 Ø0.02（示意）。一次装夹车出，还是分两次装夹？",
                        "A cobot joint's hollow output flange: bore Ø40 H7 to the harmonic drive, spigot Ø62 h7 to the next link, coaxial within Ø0.02 (illustrative). One set-up or two?"] } },
  ],
  params: [
    { id: "ax", name: ["轴向编程原点（0 左端面、1 轴承定位轴肩）", "Axial origin (0 left end face, 1 bearing shoulder)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "t", name: ["一个车削轴向尺寸的经济公差 ±t", "Economic tolerance of one turned length ±t"], min: 0.02, max: 0.2, step: 0.01, value: 0.1, unit: "mm", digits: 2 },
    { id: "sch", name: ["精车齿顶圆的基准（0 A 中心孔、1 B 一夹一顶、2 C 夹轴承位）", "Datum for the tip circle (0 A, 1 B, 2 C)"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "tir", name: ["三爪卡盘定心跳动 TIR（示意）", "Chuck centring runout TIR (illustr.)"], min: 0.01, max: 0.08, step: 0.005, value: 0.03, unit: "mm", digits: 3 },
    { id: "alpha", name: ["V 形块夹角 α", "V-block angle α"], min: 60, max: 120, step: 30, value: 90, unit: "°", digits: 0 },
    { id: "td", name: ["定位外圆的公差 Td", "Tolerance of the located diameter Td"], min: 0.01, max: 0.1, step: 0.01, value: 0.05, unit: "mm", digits: 2 },
    { id: "meas", name: ["槽深的工序基准（0 下母线、1 轴线、2 上母线）", "Depth reference (0 bottom, 1 axis, 2 top)"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "fl", name: ["法兰的装夹（0 一次装夹车内孔、止口、端面；1 分两次装夹）", "Flange set-up (0 one set-up; 1 two set-ups)"], min: 0, max: 1, step: 1, value: 1, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "axial", text: ["SH-101：8 ± 0.1 在从左端面编程时能不能保证？基准不重合误差多大？改成从轴肩编程呢？", "SH-101: can 8 ± 0.1 be held programming from the left end? How big is the mismatch? And from the shoulder?"],
      demo: { scene: "shaft", set: { ax: 1, t: 0.1 }, press: [], wait: 1 } },
    { id: "runout", text: ["齿顶圆跳动：三种基准方案中，由基准引起的部分哪一种不超过公差 0.03 的 1/3？", "Tip runout: which datum scheme keeps the datum part within 1/3 of the 0.03 tolerance?"],
      demo: { scene: "shaft", set: { sch: 0, tir: 0.03 }, press: [], wait: 1 } },
    { id: "vblock", text: ["铣键槽：α = 90°、Td = 0.05，槽深从哪里量定位误差最小？是否小于槽深公差的 1/3？", "Keyway: α = 90°, Td = 0.05 — which depth reference gives the least error? Is it below 1/3 of 0.1?"],
      demo: { scene: "key", set: { alpha: 90, td: 0.05, meas: 0 }, press: [], wait: 1 } },
    { id: "flange", text: ["输出法兰：分两次装夹（卡盘跳动 0.03）和一次装夹，同轴度各能做到多少？哪一种满足 Ø0.02？", "Flange: coaxiality with two set-ups (chuck 0.03) and with one? Which meets Ø0.02?"],
      demo: { scene: "flange", set: { fl: 0 }, press: [], wait: 1 } },
  ],
  think: ["基准重合原则说“尽量以设计基准为定位基准”。SH-101 的轴肩作为编程原点时，测量也要从轴肩量——车间的检具怎样配合？如果设计基准是一个不便装夹的面，还有什么办法？",
          "Datum coincidence says locate from the design datum. With the shoulder as origin, the measuring must start there too — how should the shop gauges suit it? What if the design datum is awkward to hold?"],

  setup3d(api, keep) {
    const h = api.m["E-ACC-CENTERS"];
    h.root.traverse((o) => { if (o.isMesh) { o.material = o.material.clone(); o.material.side = api.three.DoubleSide; } });
    keep.h = h;
    keep.base = h.nodes.root || h.root;
    keep.parts = ((h.entry.assembly || {}).parts || []).map((p) => ({ name: p.name, obj: h.nodes[p.node] }));
    keep.parts.forEach((p) => { if (p.obj) p.p0 = p.obj.position.clone(); });
    keep.tail = keep.parts.filter((p) => p.name === "尾座" || p.name === "后顶尖");
    keep.objs = [];
    keep.key = "";
    api.view(-20, 22, 1.25, h);
  },
  readouts(api) {
    const p = api.p, r = eval56(p), T = api.T, mm = (x, d = 3) => api.fmt(x, d) + " mm", sc = api.scene;
    if (sc === "shaft" && Math.round(p.ax) === 1 && r.axial.T <= 0.2 + 1e-9) api.done("axial");      // 左端面编程的结果在读数里一并给出
    if (sc === "shaft" && Math.round(p.sch) === 0 && r.runout <= TOL_R / 3 + 1e-9) api.done("runout");
    if (sc === "key" && Math.round(p.meas) === 0 && Math.abs(p.alpha - 90) < 1e-9 && Math.abs(p.td - 0.05) < 1e-9 && r.vb <= TOL_K / 3) api.done("vblock");
    if (sc === "flange" && Math.round(p.fl) === 0 && r.coax <= COAX) api.done("flange");
    if (sc === "shaft") {
      const other = Math.round(p.ax) === 0 ? 2 * p.t : 4 * p.t;
      return [
        [["轴向编程原点", "axial origin"], Math.round(p.ax) === 0 ? T("左端面（基准不重合）", "left end (mismatch)") : T("轴承定位轴肩（基准重合）", "bearing shoulder (coincident)")],
        [["8 ± 0.1 的实际公差", "tolerance obtained on 8"], mm(r.axial.T, 2) + (r.axial.T > 0.2 + 1e-9 ? T("（超过 0.2，保证不了）", " (over 0.2 — fails)") : T("（≤ 0.2，能保证）", " (≤ 0.2 — holds)"))],
        [["基准不重合误差（尺寸 73 的公差）", "datum-mismatch error (tol. of 73)"], mm(r.axial.dB, 2)],
        [["另一种编程原点的结果", "with the other origin"], mm(other, 2)],
        [["齿顶圆跳动中由基准引起的部分", "datum part of the tip runout"], T(...SCH[Math.round(p.sch)]) + "：" + api.fmt(r.runout * 1000, 1) + " µm" +
          (r.runout <= TOL_R / 3 + 1e-9 ? T("（≤ 公差的 1/3）", " (≤ 1/3 tol.)") : r.runout <= TOL_R + 1e-9 ? T("（超过 1/3，余下的给加工误差不多了）", " (> 1/3)") : T("（用完公差）", " (uses up the tolerance)"))],
        [["三种方案（µm）", "all three (µm)"], [2 * EC, p.tir * (XT - XGM) / (XT - XC), p.tir].map((x) => api.fmt(x * 1000, 1)).join(" / ")],
      ];
    }
    if (sc === "key") {
      const s = Math.sin(p.alpha * Math.PI / 360), all = [p.td / 2 * (1 / s - 1), p.td / (2 * s), p.td / 2 * (1 / s + 1)];
      return [
        [["槽深的工序基准", "depth reference"], T(...MEAS[Math.round(p.meas)])],
        [["槽深的定位误差", "locating error of the depth"], mm(r.vb, 4) + (r.vb <= TOL_K / 3 ? T("（< 公差 0.1 的 1/3）", " (< 1/3 of 0.1)") : T("（超过 1/3）", " (> 1/3)"))],
        [["下母线 / 轴线 / 上母线", "bottom / axis / top"], all.map((x) => api.fmt(x, 4)).join(" / ") + " mm"],
        [["对称度的定位误差", "symmetry locating error"], T("0（工件轴线始终在 V 形块的对称面上）", "0 (the axis stays in the V's plane of symmetry)")],
      ];
    }
    return [
      [["装夹", "set-up"], Math.round(p.fl) === 0 ? T("一次装夹车内孔、止口、端面", "one set-up for bore, spigot, face") : T("先车内孔，调头卡盘夹外圆车止口", "bore first, then re-chucked for the spigot")],
      [["同轴度（由装夹引起）", "coaxiality from the set-up"], "Ø" + api.fmt(r.coax, 3) + (r.coax <= COAX ? T("（满足 Ø0.02）", " (meets Ø0.02)") : T("（超过 Ø0.02）", " (exceeds Ø0.02)"))],
      [["说明", "note"], T("一次装夹时同轴度取主轴回转误差 0.005（示意）；钻端面螺孔再以内孔和端面定位（基准重合）", "one set-up: spindle error 0.005 (illustr.); the face holes are then drilled locating on bore and face")],
    ];
  },
  draw(api) {
    const k = api.keep;
    if (!k.base) return;
    const p = api.p, sc = api.scene, key = [sc, p.ax, p.sch, p.alpha, p.meas, p.fl].join("|");
    if (key === k.key) return;
    k.key = key;
    k.objs.forEach((o) => k.base.remove(o)); k.objs = [];
    const add = (o) => { k.base.add(o); k.objs.push(o); return o; };
    const tg = (txt, x, y, z, col) => { const s = G56.tag(api, txt, col); s.position.set(x / 1000, y / 1000, z / 1000); add(s); };
    const T = api.T, RED = "#c0392b", BLUE = "#2f6ea5";
    const centres = sc === "shaft";
    k.parts.forEach((q) => { if (q.obj) q.obj.visible = centres; });
    k.tail.forEach((q) => { if (q.obj) { q.obj.position.copy(q.p0); q.obj.position.x -= (167 - L56) / 1000; } });
    if (sc === "shaft") {
      let x = 0;
      SEG.forEach(([d, L, n]) => {
        const hot = (Math.round(p.ax) === 1 && n === "左轴肩") || (Math.round(p.sch) === 1 && n === "轴伸") || (Math.round(p.sch) === 2 && n === "左轴承位");
        add(G56.lathe(api, [[x, 0], [x, d / 2], [x + L, d / 2], [x + L, 0]], hot ? "#e0806e" : n === "齿轮" ? "#d7b48d" : "#e8c39e"));
        x += L;
      });
      const xo = Math.round(p.ax) === 0 ? 0 : X_SH;
      add(G56.lathe(api, [[xo - 0.6, 0], [xo - 0.6, 34], [xo + 0.6, 34], [xo + 0.6, 0]], "#2f6ea5")).children[0].material.opacity = 0.35;
      k.objs[k.objs.length - 1].children[0].material.transparent = true;
      tg(T("编程原点：", "origin: ") + (Math.round(p.ax) === 0 ? T("左端面", "left end") : T("轴肩", "shoulder")), xo, 0, 48, BLUE);
      tg("8 ± 0.1", (X_SH + X_G) / 2, 0, 36, "#1d2327");
      const sch = Math.round(p.sch);
      if (sch === 0) { tg(T("中心孔", "centre hole"), 0, 0, -26, RED); tg(T("中心孔", "centre hole"), L56, 0, -26, RED); }
      if (sch === 1) { add(G56.lathe(api, [[XC - 10, 10.5], [XC - 10, 22], [XC + 10, 22], [XC + 10, 10.5]], "#7a8089")); tg(T("卡盘夹轴伸", "chuck on extension"), XC, 0, -30, RED); }
      if (sch === 2) { add(G56.lathe(api, [[56 + 8.5 - 8, 12.9], [56 + 8.5 - 8, 24], [56 + 8.5 + 8, 24], [56 + 8.5 + 8, 12.9]], "#7a8089")); tg(T("卡盘夹轴承位", "chuck on bearing seat"), 64.5, 0, -32, RED); }
      tg(T("齿顶圆跳动 0.03（对 A–B）", "tip runout 0.03 to A–B"), XGM, 0, 40, "#1d2327");
    } else if (sc === "key") {
      const r0 = 10.2, s = Math.sin(p.alpha * Math.PI / 360), zA = -r0 / s, H = 22, half = (H) * Math.tan(p.alpha * Math.PI / 360);
      let x = 0;
      SEG.forEach(([d, L, n]) => { add(G56.lathe(api, [[x, 0], [x, n === "轴伸" ? r0 : d / 2], [x + L, n === "轴伸" ? r0 : d / 2], [x + L, 0]], n === "轴伸" ? "#e0806e" : "#e8c39e")); x += L; });
      const TH = api.three, sh = new TH.Shape();
      const W = half + 14;
      sh.moveTo(-W, zA - 14); sh.lineTo(W, zA - 14); sh.lineTo(W, zA + H); sh.lineTo(half, zA + H); sh.lineTo(0, zA); sh.lineTo(-half, zA + H); sh.lineTo(-W, zA + H); sh.lineTo(-W, zA - 14);
      const g = new TH.ExtrudeGeometry(sh, { depth: 30, bevelEnabled: false });
      const m = new TH.Mesh(g, G56.mat(api, "#8f9aa5"));
      m.rotation.y = Math.PI / 2;                    // 拉伸方向 z → x；截面在 y–z 平面
      m.position.set(3, 0, 0);
      const grp = new TH.Group(); grp.add(m); grp.scale.set(0.001, 0.001, 0.001); add(grp);
      tg(T("V 形块 α = ", "V-block α = ") + api.fmt(p.alpha, 0) + "°", 18, 0, zA - 22, BLUE);
      const zr = [-r0, 0, r0][Math.round(p.meas)];
      tg(T("工序基准：", "reference: ") + T(...MEAS[Math.round(p.meas)]).split("（")[0], 18, 0, zr + 30, RED);
    } else {
      add(G56.lathe(api, [[0, 20], [0, 45], [10, 45], [10, 31], [18, 31], [18, 20]], "#c9cfd6"));
      add(G56.lathe(api, [[-0.3, 19.6], [18.3, 19.6], [18.3, 20.2], [-0.3, 20.2]], Math.round(p.fl) === 0 ? "#e0806e" : "#e0806e"));
      add(G56.lathe(api, [[10, 31.1], [18.3, 31.1], [18.3, 31.6], [10, 31.6]], Math.round(p.fl) === 0 ? "#e0806e" : "#6f9fd0"));
      if (Math.round(p.fl) === 0) tg(T("一次装夹：内孔、止口、端面", "one set-up: bore, spigot, face"), 9, 0, 62, RED);
      else { tg(T("第一次：车内孔 Ø40 H7", "1st: bore Ø40 H7"), 9, 0, 66, RED); tg(T("调头第二次：车止口 Ø62 h7", "2nd: spigot Ø62 h7"), 14, 0, 52, BLUE); }
    }
  },
});
