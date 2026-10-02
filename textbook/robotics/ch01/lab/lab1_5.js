// 实验 1.5 数字工厂车间三维（配 1.5 节）。
// 车间布置、上下料点和路线规则与数字工厂仿真相同（factory/digital/wqbus/layout.py：LAYOUT、dock、route），AGV 车速 1.0 m/s、
// 装卸各 30 s（factory/digital/sim/engine.py）。三维车间用问渠三维引擎的 workshop()；平面坐标 (x, y) 的 y 轴向下，对应三维的 z。
// 仿真时钟比真实时间快：单次行驶 40 倍，SH-301 全程 80 倍。生活场景：医院里从药房到病房送药，用同样的“通道 + 装卸”算法。
WQ.lab({
  title: ["实验 1.5 数字工厂车间三维", "Lab 1.5 The digital factory workshop in 3D"],
  goal: ["在数字工厂的三维车间里为 AGV 规划路线，计算搬运距离和时间，体会装卸时间在搬运中所占的分量。",
         "Plan AGV routes in the 3D digital-factory workshop, compute transport distance and time, and see how much of it is loading and unloading."],
  view: "3d",
  models: ["B-EDU-DIFF"],
  scenes: [
    { id: "shop", robot: true, name: ["数字工厂车间", "Digital factory workshop"],
      problem: { title: ["机器人问题：一根输出轴在车间里要走多远", "Robot problem: how far does one output shaft travel"],
                 text: ["SH-301 经带锯、车、热处理、车、键槽、磨、检验七道工序，每道之间由 AGV 搬运（表 1.5.1）。",
                        "SH-301 passes saw, lathe, furnace, lathe, keyway, grinder and inspection; the AGV moves it between them (Table 1.5.1)."] },
      params: { from: { min: 0, max: 13, value: 1 }, to: { min: 0, max: 13, value: 2 } } },
    { id: "hosp", name: ["医院送药", "Hospital delivery"],
      problem: { title: ["生活中的例子：医院里的送药机器人", "Everyday example: a medicine-delivery robot in a hospital"],
                 text: ["药房在走廊一端，病房分布在走廊两侧。路线同样是“进走廊—沿走廊—进门”，时间同样是行驶加交接。",
                        "The pharmacy is at one end of the corridor, wards on both sides. The route is again aisle–along–in, the time again driving plus hand-over."] },
      params: { from: { min: 0, max: 6, value: 0 }, to: { min: 0, max: 6, value: 3 } } },
  ],
  params: [
    { id: "from", name: ["起点（编号）", "From (number)"], min: 0, max: 13, step: 1, value: 1, digits: 0 },
    { id: "to", name: ["终点（编号）", "To (number)"], min: 0, max: 13, step: 1, value: 2, digits: 0 },
    { id: "v", name: ["AGV 车速", "AGV speed"], min: 0.5, max: 1.5, step: 0.1, value: 1.0, unit: "m/s", digits: 1 },
    { id: "tlu", name: ["每次装或卸的时间", "Loading or unloading time"], min: 5, max: 60, step: 5, value: 30, unit: "s", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["行驶", "Drive"], primary: true }, { id: "sh301", name: ["SH-301 全程", "Whole SH-301 route"] },
            { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "first", robot: true, text: ["规划从带锯床（1）到数控车床 A（2）的路线，读出路线长度，与表 1.5.1 比较。", "Plan the route from the saw (1) to lathe A (2); read its length and compare with Table 1.5.1."],
      demo: { scene: "shop", set: { from: 1, to: 2 }, press: [], wait: 1 } },
    { id: "whole", robot: true, text: ["按“SH-301 全程”，让 AGV 依次完成七次搬运，读出总路程和总时间。", "Press “Whole SH-301 route”: the AGV makes the seven moves; read the total distance and time."],
      demo: { scene: "shop", set: { v: 1.0, tlu: 30 }, press: ["sh301"], wait: 80 } },
    { id: "half", robot: true, text: ["把装卸时间缩短到 15 s，再跑一遍全程，看总时间减少了多少。", "Cut the loading time to 15 s and run the whole route again; how much time is saved?"],
      demo: { scene: "shop", set: { v: 1.0, tlu: 15 }, press: ["sh301"], wait: 80 } },
    { id: "ward", text: ["在医院场景中，从药房（0）送药到任一病房，完成一次配送。", "In the hospital, deliver from the pharmacy (0) to any ward."],
      demo: { scene: "hosp", set: { from: 0, to: 3 }, press: ["start"], wait: 30 } },
  ],
  think: ["表 1.5.1 中七次搬运共约 10 min，其中装卸约 7 min。若要把搬运时间减半，提高车速和缩短装卸，哪个更有效？提高车速还有什么代价（1.1 节）？",
          "The seven moves of Table 1.5.1 take about 10 min, about 7 of it loading and unloading. To halve it, is a faster AGV or a quicker hand-over better? What else does a higher speed cost (Section 1.1)?"],

  // ---- 数字工厂的布置（m），与 layout.py 相同：编号, 代号, 中文, 英文, x, y, 宽, 深
  SHOP: [["store-01", "原料库", "raw store", 3, 4, 4, 5], ["saw-01", "带锯床", "band saw", 10, 4, 4, 2.5],
         ["cnc-l01-a", "数控车床 A", "CNC lathe A", 17, 4, 4, 2.2], ["cnc-l01-b", "数控车床 B", "CNC lathe B", 24, 4, 4, 2.2],
         ["key-01", "键槽铣床", "keyway miller", 31, 4, 3, 2.2], ["ht-01", "热处理炉", "furnace", 17, 13, 5, 4],
         ["grd-01", "外圆磨床", "grinder", 31, 13, 4.5, 2.2], ["qc-01", "检验站", "inspection", 38, 13, 4, 3],
         ["vmc-01", "立式加工中心", "VMC", 10, 22, 3.5, 3], ["hmc-01", "卧式加工中心", "HMC", 17, 22, 4.5, 3.5],
         ["hob-01", "滚齿机", "gear hobber", 24, 22, 3.5, 2.5], ["asm-01", "装配工位", "assembly", 31, 22, 5, 3],
         ["test-01", "跑合试验台", "run-in rig", 38, 22, 3.5, 2.5], ["store-02", "成品库", "finished store", 45, 22, 4, 5]],
  SH301: [1, 2, 5, 3, 4, 6, 7, 13],                // 带锯 → 车 A → 热处理 → 车 B → 键槽 → 磨 → 检验 → 成品库
  HOSP: [["ph", "药房", "pharmacy", 3, 4, 5, 4], ["w1", "病房 1", "ward 1", 10, 3, 5, 4], ["w2", "病房 2", "ward 2", 17, 3, 5, 4],
         ["w3", "病房 3", "ward 3", 24, 3, 5, 4], ["w4", "病房 4", "ward 4", 10, 13, 5, 4], ["w5", "病房 5", "ward 5", 17, 13, 5, 4],
         ["w6", "护士站", "nurses' station", 24, 13, 5, 4]],
  SCALE: 40, FAST: 80,

  units(api) { return api.scene === "hosp" ? this.HOSP : this.SHOP; },
  dock(api, u) {
    const [, , , x, y, , d] = u;
    if (api.scene === "hosp") return y < 8 ? [x, y + d / 2 + 1.0] : [x, y - d / 2 - 1.0];
    const A0 = 9.0, A1 = 18.5;
    return (y < A0 || (A0 < y && y < A1 && y < 13.5)) ? [x, y + d / 2 + 1.0] : [x, y - d / 2 - 1.0];
  },
  route(api, a, b) {
    const aisles = api.scene === "hosp" ? [8.0] : [9.0, 18.5], cross = 7.0;
    const near = (p) => aisles.reduce((m, y) => (Math.abs(y - p[1]) < Math.abs(m - p[1]) ? y : m), aisles[0]);
    const a0 = near(a), a1 = near(b);
    let pts = [a, [a[0], a0]];
    if (a0 !== a1) pts = pts.concat([[cross, a0], [cross, a1]]);
    pts = pts.concat([[b[0], a1], b]);
    const out = [pts[0]];
    pts.slice(1).forEach((p) => { const q = out[out.length - 1]; if (Math.abs(p[0] - q[0]) > 1e-6 || Math.abs(p[1] - q[1]) > 1e-6) out.push(p); });
    return out;
  },
  len(path) { let L = 0; for (let i = 1; i < path.length; i++) L += Math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]); return L; },
  at(path, dist) {
    for (let i = 1; i < path.length; i++) {
      const p = path[i - 1], q = path[i], L = Math.hypot(q[0] - p[0], q[1] - p[1]);
      if (dist <= L || i === path.length - 1) { const f = L > 0 ? Math.min(1, dist / L) : 0; return [p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f, Math.atan2(q[1] - p[1], q[0] - p[0])]; }
      dist -= L;
    }
    return [path[0][0], path[0][1], 0];
  },
  legs(api, idx) {
    const U = this.units(api), out = [];
    for (let k = 1; k < idx.length; k++) { const a = this.dock(api, U[idx[k - 1]]), b = this.dock(api, U[idx[k]]); const p = this.route(api, a, b); out.push({ path: p, L: this.len(p) }); }
    return out;
  },

  label(api, zhText, enText, color) {
    const T = api.three, c = document.createElement("canvas");
    c.width = 256; c.height = 96;
    const g = c.getContext("2d");
    g.fillStyle = "rgba(255,255,255,0.85)"; g.fillRect(0, 0, 256, 96);
    g.fillStyle = color || "#1f2a33"; g.textAlign = "center"; g.font = "bold 34px sans-serif"; g.fillText(zhText, 128, 42);
    g.font = "24px sans-serif"; g.fillStyle = "#5b6b75"; g.fillText(enText, 128, 80);
    const sp = new T.Sprite(new T.SpriteMaterial({ map: new T.CanvasTexture(c), depthTest: false }));
    sp.scale.set(4.4, 1.65, 1);
    return sp;
  },
  build(api, list, W, D, aisles, cross) {
    const T = api.three, spec = { floor: { w: W, d: D }, aisles: [], units: [], agvs: [], labels: false };
    aisles.forEach((y) => spec.aisles.push({ x: W / 2, y, w: W - 1, d: 2 }));
    if (cross) spec.aisles.push({ x: cross[0], y: (cross[1] + cross[2]) / 2, w: 2, d: cross[2] - cross[1] });
    list.forEach(([id, z, e, x, y, w, d]) => spec.units.push({ id, name: [z, e], x, y, w, d, h: id.startsWith("store") || id === "ph" ? 2.2 : 1.6, store: id.startsWith("store") || id === "ph" }));
    const shop = WQ3D.workshop(api.st, spec);
    list.forEach(([id, z, e, x, y], k) => { const sp = this.label(api, `${k}  ${z}`, e); sp.position.set(x - W / 2, 3.4, y - D / 2); shop.group.add(sp); });
    const agv = new T.Mesh(new T.BoxGeometry(1.3, 0.35, 0.85), new T.MeshStandardMaterial({ color: 0xf28c28 }));
    agv.position.y = 0.25;
    const load = new T.Mesh(new T.BoxGeometry(0.6, 0.35, 0.5), new T.MeshStandardMaterial({ color: 0xd8c39a }));
    load.position.y = 0.6;
    const car = new T.Group(); car.add(agv, load); shop.group.add(car);
    const pin = (col) => { const m = new T.Mesh(new T.ConeGeometry(0.5, 1.2, 16), new T.MeshStandardMaterial({ color: col })); m.rotation.x = Math.PI; shop.group.add(m); return m; };
    return { shop, car, load, W, D, pinA: pin(0x2ca02c), pinB: pin(0xd62728), line: null };
  },
  setup3d(api, keep) {
    const T = api.three;
    api.m["B-EDU-DIFF"].holder.visible = false;
    keep.f = this.build(api, this.SHOP, 50, 28, [9.0, 18.5], [7.0, 9.0, 18.5]);
    keep.h = this.build(api, this.HOSP, 30, 17, [8.0], null);
    keep.h.shop.group.position.x = 60;                           // 医院放在车间旁边，场景切换时只看其中一个
    keep.f.shop.seek(0); keep.h.shop.seek(0);
    const mk = (L) => ({ entry: { robot: {} }, holder: { visible: false }, box: () => L.shop.boxOf("workshop") });
    api.m.fFrame = mk(keep.f); api.m.hFrame = mk(keep.h);
    keep.shown = null;
  },
  reset(api, s) {
    s.mode = "one"; s.legs = []; s.k = 0; s.phase = "idle"; s.tp = 0; s.dist = 0; s.simT = 0; s.totL = 0; s.done = false;
  },
  begin(api, s, idx, mode) {
    s.mode = mode; s.legs = this.legs(api, idx); s.k = 0; s.phase = "load"; s.tp = 0; s.dist = 0; s.simT = 0; s.totL = 0; s.done = false;
    s.tlu = api.p.tlu; s.v = api.p.v;
  },
  start(api, s) {
    const U = this.units(api), a = Math.round(api.p.from), b = Math.round(api.p.to);
    if (a === b || !U[a] || !U[b]) { api.stop(); return; }
    this.begin(api, s, [a, b], "one");
  },
  action(id, api, s) {
    if (id !== "sh301" || api.scene !== "shop") return;
    this.begin(api, s, this.SH301, "sh301");
    api.running = true; api.t = 0;
  },
  update(dt, api, s) {
    if (!s.legs || !s.legs.length || s.done) { api.stop(); return; }
    let h = dt * (s.mode === "sh301" ? this.FAST : this.SCALE);
    while (h > 0 && !s.done) {
      const leg = s.legs[s.k];
      if (s.phase === "load" || s.phase === "unload") {
        const need = s.tlu - s.tp, step = Math.min(h, need);
        s.tp += step; s.simT += step; h -= step;
        if (s.tp >= s.tlu - 1e-9) {
          s.tp = 0;
          if (s.phase === "load") s.phase = "drive";
          else { s.totL += leg.L; s.k += 1; s.dist = 0; s.phase = "load"; if (s.k >= s.legs.length) { s.done = true; s.k = s.legs.length - 1; s.phase = "idle"; } }
        }
      } else {
        const need = (leg.L - s.dist) / s.v, step = Math.min(h, need);
        s.dist += step * s.v; s.simT += step; h -= step;
        if (s.dist >= leg.L - 1e-9) { s.dist = leg.L; s.phase = "unload"; }
      }
    }
    if (s.done) {
      if (s.mode === "sh301" && api.scene === "shop") { api.done("whole"); if (s.tlu <= 15) api.done("half"); }
      if (s.mode === "one" && api.scene === "hosp" && Math.round(api.p.from) === 0) api.done("ward");
      api.stop();
    }
  },
  readouts(api, s) {
    const K = api.keep;
    if (!K || !K.f) return [];
    const U = this.units(api), a = Math.round(api.p.from), b = Math.round(api.p.to), f = api.fmt;
    const rows = [];
    if (U[a] && U[b]) {
      const L = a === b ? 0 : this.len(this.route(api, this.dock(api, U[a]), this.dock(api, U[b])));
      rows.push([["起点 → 终点", "from → to"], api.T(`${U[a][1]} → ${U[b][1]}`, `${U[a][2]} → ${U[b][2]}`)]);
      rows.push([["路线长度 L", "route length L"], f(L, 2) + " m"]);
      rows.push([["一次搬运时间 L/v + 2·装卸", "one move L/v + 2·load"], f(L / api.p.v + 2 * api.p.tlu, 1) + " s"]);
      if (api.scene === "shop" && a === 1 && b === 2) api.done("first");
    }
    if (s.legs && s.legs.length) {
      const total = s.legs.reduce((x, l) => x + l.L, 0);
      rows.push([["进度", "progress"], api.T(`第 ${s.k + 1} / ${s.legs.length} 次`, `move ${s.k + 1} / ${s.legs.length}`) + (s.done ? api.T("，完成", ", done") : "")]);
      rows.push([["累计路程", "distance so far"], f(s.totL + (s.done ? 0 : s.dist), 1) + " / " + f(total, 1) + " m"]);
      rows.push([["累计时间（仿真）", "time so far (simulated)"], f(s.simT, 0) + " s = " + f(s.simT / 60, 1) + " min"]);
      rows.push([["其中装卸", "of which loading"], f(s.legs.length * 2 * s.tlu, 0) + " s"]);
    }
    return rows;
  },
  draw(api, s) {
    const K = api.keep, T = api.three;
    if (!K || !K.f) return;
    const hosp = api.scene === "hosp", L = hosp ? K.h : K.f;
    K.f.shop.group.visible = !hosp; K.h.shop.group.visible = hosp;
    if (K.shown !== api.scene) { K.shown = api.scene; api.view(0, 60, hosp ? 1.3 : 1.55, hosp ? api.m.hFrame : api.m.fFrame); }
    const U = this.units(api), P = (x, y) => new T.Vector3(x - L.W / 2, 0, y - L.D / 2);
    const a = U[Math.round(api.p.from)], b = U[Math.round(api.p.to)];
    if (a) { const d = this.dock(api, a), p = P(d[0], d[1]); L.pinA.position.set(p.x, 2.2, p.z); }
    if (b) { const d = this.dock(api, b), p = P(d[0], d[1]); L.pinB.position.set(p.x, 2.2, p.z); }
    const key = [api.scene, Math.round(api.p.from), Math.round(api.p.to), s.mode, (s.legs || []).length].join("/");
    if (K.lineKey !== key) {
      K.lineKey = key;
      if (L.line) { L.shop.group.remove(L.line); L.line = null; }
      const legs = s.legs && s.legs.length ? s.legs : (a && b && a !== b ? [{ path: this.route(api, this.dock(api, a), this.dock(api, b)) }] : []);
      const pts = [];
      legs.forEach((g) => g.path.forEach((q) => { const v = P(q[0], q[1]); v.y = 0.08; pts.push(v); }));
      if (pts.length > 1) { L.line = new T.Line(new T.BufferGeometry().setFromPoints(pts), new T.LineBasicMaterial({ color: 0x1f77b4 })); L.shop.group.add(L.line); }
    }
    let pos = a ? this.dock(api, a) : [0, 0], hd = 0;
    if (s.legs && s.legs.length) { const g = s.legs[s.k], q = this.at(g.path, s.dist); pos = [q[0], q[1]]; hd = q[2]; }
    const p = P(pos[0], pos[1]);
    L.car.position.set(p.x, 0, p.z);
    L.car.rotation.y = -hd;
    L.load.visible = !!(s.legs && s.legs.length && (s.phase === "drive" || s.phase === "unload"));
  },
});
