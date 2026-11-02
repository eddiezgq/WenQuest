// 实验 55.2 表面形貌与粗糙度（配 55.2 节）。模型与 hub/surface.py 相同：
//   残留高度 h = r − √(r² − f²/4)，理论 Ra ≈ 0.0321 f²/r（式 (55.2.1)、(55.2.3)）；
//   合成轮廓（沿进给方向）= 刀尖圆弧残留 + 随机微观不平（0.12 µm，相关长度约 5 µm）+ 积屑瘤（幅值 2·exp(−(ln(vc/25)/0.55)²) µm，相关长度约 20 µm）
//   + 振纹（幅值 a，波长 0.5 mm，同算例 55.2.3）；高斯滤波 λc = 0.8 mm，5 个取样长度，Ra、Rz 取三条轮廓（三个随机种子）的平均。
//   三维表面为 1.2 mm（进给方向）× 2 mm（切削方向）的一块，高度放大画出；振纹画在切削方向（与图 55.2.6 相同）。
//   随机数与 Python 不同，Ra、Rz 与算例 55.2.3 的值相差百分之几。
const LC = 0.8, DX = 0.001, NS = 5;
function rnd(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function gauss(R) { return Math.sqrt(-2 * Math.log(Math.max(R(), 1e-12))) * Math.cos(2 * Math.PI * R()); }
function bue(vc) { return vc <= 0 ? 0 : 2 * Math.exp(-Math.pow(Math.log(vc / 25) / 0.55, 2)); }
function raTheory(f, r) { return 0.0321 * f * f / r * 1000; }   // µm
function hRes(f, r) { return (r - Math.sqrt(Math.max(r * r - f * f / 4, 0))) * 1000; }
function smooth(src, sigma) {             // 与 numpy 的 convolve(…, k/√Σk², "same") 相同：单位方差的相关噪声
  const n = Math.round(4 * sigma / DX), k = [];
  let s2 = 0;
  for (let i = -n; i <= n; i++) { const v = Math.exp(-0.5 * Math.pow(i * DX / sigma, 2)); k.push(v); s2 += v * v; }
  const c = 1 / Math.sqrt(s2), out = new Float64Array(src.length);
  for (let i = 0; i < src.length; i++) { let a = 0; for (let j = -n; j <= n; j++) { const m = i + j; if (m >= 0 && m < src.length) a += src[m] * k[j + n]; } out[i] = a * c; }
  return out;
}
function profile(p, seed) {
  const L = (NS + 2) * LC, n = Math.round(L / DX), R = rnd(seed), x0 = R() * p.f, z = new Float64Array(n);
  for (let i = 0; i < n; i++) { const xc = ((i * DX + x0) % p.f) - p.f / 2; z[i] = p.r - Math.sqrt(Math.max(p.r * p.r - xc * xc, 0)); }
  const w = new Float64Array(n); for (let i = 0; i < n; i++) w[i] = gauss(R);
  const g1 = smooth(w, 0.005); for (let i = 0; i < n; i++) z[i] += g1[i] * 0.12e-3;
  const b = bue(p.vc) / 1000;
  if (b > 0) { const w2 = new Float64Array(n); for (let i = 0; i < n; i++) w2[i] = gauss(R); const g2 = smooth(w2, 0.02); for (let i = 0; i < n; i++) z[i] += b * g2[i]; }
  if (p.vib) for (let i = 0; i < n; i++) z[i] += p.vib / 1000 * Math.sin(2 * Math.PI * i * DX / 0.5 + 0.7);
  return z;
}
function rough(z) {                        // 高斯滤波中线（ISO 16610-21），评定长度 5λc
  const a = Math.sqrt(Math.log(2) / Math.PI), m = Math.round(LC / DX), wts = [];
  let s = 0; for (let j = -m; j <= m; j++) { const v = Math.exp(-Math.PI * Math.pow(j * DX / (a * LC), 2)); wts.push(v); s += v; }
  const r = [];
  for (let i = m; i < m * (NS + 1); i++) { let c = 0; for (let j = -m; j <= m; j++) c += z[i + j] * wts[j + m]; r.push((z[i] - c / s) * 1000); }
  const Ra = r.reduce((q, v) => q + Math.abs(v), 0) / r.length;
  let Rz = 0; for (let k = 0; k < NS; k++) { const seg = r.slice(k * m, (k + 1) * m); Rz += Math.max(...seg) - Math.min(...seg); }
  return { Ra, Rz: Rz / NS };
}
function eval55(p) {
  const rs = [0, 1, 2].map((s) => rough(profile(p, 7 + s)));
  return { Ra: rs.reduce((q, v) => q + v.Ra, 0) / 3, Rz: rs.reduce((q, v) => q + v.Rz, 0) / 3, th: raTheory(p.f, p.r), h: hRes(p.f, p.r), b: bue(p.vc) };
}
const near = (a, b, t = 1e-6) => Math.abs(a - b) < t;

WQ.lab({
  title: ["实验 55.2 表面形貌与粗糙度", "Lab 55.2 Surface topography and roughness"],
  goal: ["调进给量、刀尖圆弧半径、切削速度和振纹的幅值，看车削表面的三维形貌和 Ra、Rz 怎样变化，比较几何残留算出的理论 Ra 与合成轮廓的 Ra。",
         "Vary the feed, nose radius, cutting speed and chatter amplitude; watch the 3D turned surface and Ra, Rz change, and compare the theoretical Ra from the scallops with the Ra of the synthetic profile."],
  view: "3d",
  models: ["E-WKP-SH301"],
  scenes: [
    { id: "op40", name: ["SH-301 工序 40 精车", "SH-301 operation 40 finish turning"],
      params: { f: { value: 0.15 }, r: { value: 0.4 }, vc: { value: 150 }, vib: { value: 0 } },
      problem: { title: ["工程问题：精车能车到多光", "Engineering problem: how smooth can finish turning get"],
                 text: ["工序 40 精车 SH-301 用 DNMG 110404 刀片（r = 0.4 mm），f = 0.15 mm/r、vc = 150 m/min，要求 Ra 3.2，给磨削留量。若想省掉磨削直接车到 Ra 0.8、或至少车到 Ra 1.6，进给量、刀片要怎样选？积屑瘤和振动又会让表面变成什么样？",
                        "Operation 40 finish-turns SH-301 with a DNMG 110404 insert (r = 0.4 mm), f = 0.15 mm/rev and vc = 150 m/min, to Ra 3.2 before grinding. To turn straight to Ra 0.8, or at least Ra 1.6, how should feed and insert be chosen? And what do a built-up edge and chatter do to the surface?"] } },
    { id: "flex", robot: true, name: ["柔轮内孔精车", "Finish-turning a flexspline bore"],
      params: { f: { value: 0.08 }, r: { value: 0.2 }, vc: { value: 180 }, vib: { value: 0 } },
      problem: { title: ["机器人问题：薄壁柔轮的内孔", "Robot problem: the bore of a thin-walled flexspline"],
                 text: ["谐波减速器柔轮的内孔精车后直接使用（55.2 节机器人的例子）。柔轮壁薄，刀尖圆弧大了背向力大、容易振，只能用 r = 0.2 的锋利刀片，靠小进给、高转速保证粗糙度。",
                        "A flexspline bore is used as turned (the robot example in 55.2). The wall is thin, so a large nose radius pushes and chatters; a sharp r = 0.2 insert with a small feed and high speed must give the finish."] } },
  ],
  params: [
    { id: "f", name: ["进给量 f", "Feed f"], min: 0.03, max: 0.40, step: 0.01, value: 0.15, unit: "mm/r", digits: 2 },
    { id: "r", name: ["刀尖圆弧半径 r", "Nose radius r"], min: 0.1, max: 1.6, step: 0.1, value: 0.4, unit: "mm", digits: 1 },
    { id: "vc", name: ["切削速度 vc", "Cutting speed vc"], min: 5, max: 300, step: 5, value: 150, unit: "m/min", digits: 0 },
    { id: "vib", name: ["振纹幅值", "Chatter amplitude"], min: 0, max: 5, step: 0.5, value: 0, unit: "µm", digits: 1 },
  ],
  legend: [{ color: "#4f7fb8", name: ["谷", "valleys"] }, { color: "#e0a030", name: ["峰（高度放大画出）", "peaks (heights exaggerated)"] }],
  tasks: [
    { id: "op40", text: ["工序 40 精车（默认参数）：理论 Ra 和合成轮廓的 Ra、Rz 各多少？满足 Ra 3.2 吗？", "Operation 40 (defaults): the theoretical Ra and the profile's Ra and Rz? Does it meet Ra 3.2?"],
      demo: { scene: "op40", set: { f: 0.15, r: 0.4, vc: 150, vib: 0 }, press: [], wait: 1 } },
    { id: "f08", text: ["保持 r = 0.4，进给量最大取多少，理论 Ra 不超过 0.8 µm？", "Keeping r = 0.4, what is the largest feed that keeps the theoretical Ra within 0.8 µm?"],
      demo: { scene: "op40", set: { f: 0.09, r: 0.4, vc: 150, vib: 0 }, press: [], wait: 1 } },
    { id: "bue", text: ["把切削速度降到积屑瘤区（约 25 m/min）：Ra、Rz 各增大多少？表面变成什么样？", "Drop the speed into the built-up-edge range (about 25 m/min): how much do Ra and Rz grow, and how does the surface look?"],
      demo: { scene: "op40", set: { f: 0.15, r: 0.4, vc: 25, vib: 0 }, press: [], wait: 1 } },
    { id: "vib", text: ["加 3 µm 的振纹：Ra 增大到多少？", "Add 3 µm of chatter: what does Ra become?"],
      demo: { scene: "op40", set: { f: 0.15, r: 0.4, vc: 150, vib: 3 }, press: [], wait: 1 } },
    { id: "r16", text: ["不减小进给量（f = 0.15），也不降低切削速度，怎样让理论 Ra 达到 1.6 µm 以下？", "Without reducing the feed (f = 0.15) or the speed, how can the theoretical Ra get below 1.6 µm?"],
      demo: { scene: "op40", set: { f: 0.15, r: 0.8, vc: 150, vib: 0 }, press: [], wait: 1 } },
  ],
  think: ["理论 Ra 只由 f、r 决定，为什么合成轮廓的 Ra 总比理论值大一点？在积屑瘤区，为什么 Rz 增大得比 Ra 多？",
          "The theoretical Ra depends only on f and r: why is the profile's Ra always a little larger? In the built-up-edge range, why does Rz grow more than Ra?"],

  setup3d(api, keep) {
    const h = api.m["E-WKP-SH301"];
    api.view(35, 35, 0.85, h);
    keep.c = h.box().getCenter(new api.three.Vector3());
    h.root.visible = false;                // 只用它定好视角：画面里是放大的一小块表面
    keep.mesh = null; keep.key = "";
  },
  reset(api, s) { s.r = null; s.key = ""; },
  update(dt, api, s) { api.stop(); },
  result(api, s) {
    const p = api.p, key = [p.f, p.r, p.vc, p.vib].join("|");
    if (s.key !== key) { s.key = key; s.r = eval55(p); }
    return s.r;
  },
  readouts(api, s) {
    const p = api.p, r = this.result(api, s), f2 = (v) => api.fmt(v, 2) + " µm";
    if (api.scene === "op40" && near(p.f, 0.15) && near(p.r, 0.4) && p.vc >= 100 && p.vib === 0) api.done("op40");
    if (near(p.r, 0.4) && p.vib === 0 && r.th <= 0.8 && p.f + 0.01 > 0.0998 + 1e-9 && p.f >= 0.09 - 1e-9) api.done("f08");
    if (r.b >= 1.5 && p.vib === 0) api.done("bue");
    if (p.vib >= 3 - 1e-9 && r.b < 0.2) api.done("vib");
    if (p.f >= 0.15 - 1e-9 && p.vc >= 100 && r.th < 1.6) api.done("r16");
    return [
      [["残留高度 h（式 55.2.1）", "scallop height h (55.2.1)"], api.fmt(r.h, 2) + " µm"],
      [["理论 Ra ≈ 0.0321 f²/r", "theoretical Ra ≈ 0.0321 f²/r"], f2(r.th)],
      [["积屑瘤附加的不平度", "built-up-edge roughness"], r.b < 0.05 ? api.T("无", "none") : api.fmt(r.b, 2) + " µm"],
      [["合成轮廓 Ra / Rz（λc 0.8 mm，三条平均）", "profile Ra / Rz (λc 0.8 mm, mean of 3)"], f2(r.Ra) + " / " + api.fmt(r.Rz, 1) + " µm"],
      [["Ra / 理论 Ra", "Ra / theoretical"], api.fmt(r.Ra / r.th, 2)],
      [["能否达到 Ra 3.2 / 1.6 / 0.8", "meets Ra 3.2 / 1.6 / 0.8"], [3.2, 1.6, 0.8].map((t) => (r.Ra <= t ? "✓" : "✗")).join(" / ")],
    ];
  },
  draw(api, s) {
    const k = api.keep, p = api.p;
    if (!k.c) return;
    const key = [p.f, p.r, p.vc, p.vib].join("|");
    if (k.key === key) return;
    k.key = key;
    const T = api.three;
    if (k.mesh) { api.st.scene.remove(k.mesh); k.mesh.geometry.dispose(); }
    // 1.2 mm（进给，x）× 2 mm（切削方向，z）的一块，与 hub/surface.py 的 surface_map 相同；1 mm 画成 0.15 m，高度 1 µm 画成 1.2 mm（高度约放大 8 倍）
    const N = 120, Lx = 1.2, Lz = 2.0, S = 0.15, H = 0.0012, R = rnd(55), b = bue(p.vc);
    const z = [];
    for (let i = 0; i <= N; i++) { z.push([]); for (let j = 0; j <= N; j++) {
      const x = Lx * i / N, y = Lz * j / N, xc = (x % p.f) - p.f / 2;
      z[i].push((p.r - Math.sqrt(Math.max(p.r * p.r - xc * xc, 0))) * 1000 + 0.12 * gauss(R) + p.vib * Math.sin(2 * Math.PI * y / 0.5)); } }
    if (b > 0) {                         // 积屑瘤：相关长度约 20 µm 的随机起伏（两遍盒式平滑近似高斯）
      let g = z.map((row) => row.map(() => gauss(R)));
      for (let pass = 0; pass < 2; pass++) g = g.map((row, i) => row.map((_, j) => { let a = 0, n = 0; for (let di = -2; di <= 2; di++) for (let dj = -2; dj <= 2; dj++) { const u = g[i + di] && g[i + di][j + dj]; if (u !== undefined) { a += u; n++; } } return a / n; }));
      const sd = Math.sqrt(g.flat().reduce((q, v) => q + v * v, 0) / g.flat().length);
      z.forEach((row, i) => row.forEach((_, j) => { row[j] += b * g[i][j] / sd; }));
    }
    const flat = z.flat(), mean = flat.reduce((q, v) => q + v, 0) / flat.length, lo = Math.min(...flat), hi = Math.max(...flat);
    const geo = new T.PlaneGeometry(Lx * S, Lz * S, N, N), pos = geo.attributes.position, col = [];
    const c0 = new T.Color("#4f7fb8"), c1 = new T.Color("#e0a030");
    for (let v = 0; v < pos.count; v++) {
      const i = v % (N + 1), j = Math.floor(v / (N + 1)), zz = z[i][j];
      pos.setZ(v, (zz - mean) * H);
      const c = c0.clone().lerp(c1, (zz - lo) / Math.max(hi - lo, 1e-9)); col.push(c.r, c.g, c.b);
    }
    geo.setAttribute("color", new T.Float32BufferAttribute(col, 3));
    geo.computeVertexNormals();
    const m = new T.Mesh(geo, new T.MeshStandardMaterial({ vertexColors: true, roughness: 0.6, metalness: 0.2, side: T.DoubleSide }));
    m.rotation.x = -Math.PI / 2;           // 平面放平：高度朝上（y）
    m.position.copy(k.c);
    api.st.scene.add(m);
    k.mesh = m;
  },
});
