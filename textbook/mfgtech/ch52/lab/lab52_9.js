// 实验 52.9 夹具元件的刚度：V 形块截面的平面应力有限元（配 52.9 节）。
// 与数字工厂的 hub/fe2d.py 用同一种网格和单元（顶边贴合 V 形槽的映射网格、常应变三角形），网格边长 2 mm，
// 底边固定；工件传来的竖直力 W 按两个工作面的法向力 W/(2 sin(α/2)) 分到接触点最近的 3 个节点上；
// 方程用共轭梯度法（对角预处理）求解。轴心下沉 = 接触点沿法向的退让 / sin(α/2)。程序 ex52_9 用同样的网格核对本实验的结果。
const FE52 = { H: 2, NU: 0.3, D: 40.3, TOL_UM: 30 };

function mesh52(B, Hb, ya, alpha) {
  const h = FE52.H, nx = Math.round(B / h), ny = Math.round(Hb / h), a = alpha * Math.PI / 360;
  const ytop = (x) => Math.min(Hb, ya + Math.abs(x) / Math.tan(a));
  const xy = [];
  for (let j = 0; j <= ny; j++) for (let i = 0; i <= nx; i++) { const x = -B / 2 + B * i / nx; xy.push([x, ytop(x) * j / ny]); }
  const id = (i, j) => j * (nx + 1) + i, tri = [];
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    const A = id(i, j), Bn = id(i + 1, j), C = id(i + 1, j + 1), Dn = id(i, j + 1);
    if ((i + j) % 2 === 0) { tri.push([A, Bn, C], [A, C, Dn]); } else { tri.push([A, Bn, Dn], [Bn, C, Dn]); }
  }
  return { xy, tri, nx, ny, a };
}

function solve52(p) {
  const m = mesh52(p.B, p.Hb, p.ya, p.alpha), E = p.E * 1000, nu = FE52.NU, t = p.t, N = 2 * m.xy.length;
  const c = E / (1 - nu * nu), Dm = [[c, c * nu, 0], [c * nu, c, 0], [0, 0, c * (1 - nu) / 2]];
  const K = Array.from({ length: N }, () => new Map());
  for (const tr of m.tri) {
    const [p1, p2, p3] = tr.map((n) => m.xy[n]);
    const A = 0.5 * ((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1]));
    const b = [p2[1] - p3[1], p3[1] - p1[1], p1[1] - p2[1]], cc = [p3[0] - p2[0], p1[0] - p3[0], p2[0] - p1[0]];
    const Bm = [[], [], []];
    for (let k = 0; k < 3; k++) {
      Bm[0].push(b[k] / (2 * A), 0); Bm[1].push(0, cc[k] / (2 * A)); Bm[2].push(cc[k] / (2 * A), b[k] / (2 * A));
    }
    const dof = []; tr.forEach((n) => dof.push(2 * n, 2 * n + 1));
    for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) {
      let s = 0;
      for (let r = 0; r < 3; r++) for (let q = 0; q < 3; q++) s += Bm[r][i] * Dm[r][q] * Bm[q][j];
      const v = t * A * s, row = K[dof[i]];
      row.set(dof[j], (row.get(dof[j]) || 0) + v);
    }
  }
  // 载荷
  const a = m.a, R = FE52.D / 2, yc = p.ya + R / Math.sin(a), Nf = p.W / (2 * Math.sin(a));
  const F = new Float64Array(N), contacts = [], normals = [];
  for (const sx of [-1, 1]) {
    const cxy = [sx * R * Math.cos(a), yc - R * Math.sin(a)], nrm = [-sx * Math.cos(a), Math.sin(a)];
    const near = m.xy.map((q, i) => [Math.hypot(q[0] - cxy[0], q[1] - cxy[1]), i]).sort((u, v) => u[0] - v[0]).slice(0, 3).map((u) => u[1]);
    near.forEach((n) => { F[2 * n] -= Nf / 3 * nrm[0]; F[2 * n + 1] -= Nf / 3 * nrm[1]; });
    contacts.push(near); normals.push(nrm);
  }
  const fixed = new Uint8Array(N);
  m.xy.forEach((q, i) => { if (Math.abs(q[1]) < 1e-9) { fixed[2 * i] = 1; fixed[2 * i + 1] = 1; } });
  // 共轭梯度
  const mul = (x) => { const y = new Float64Array(N); for (let i = 0; i < N; i++) { if (fixed[i]) continue; let s = 0; for (const [j, v] of K[i]) if (!fixed[j]) s += v * x[j]; y[i] = s; } return y; };
  const dg = new Float64Array(N); for (let i = 0; i < N; i++) dg[i] = fixed[i] ? 1 : K[i].get(i);
  const u = new Float64Array(N), r = Float64Array.from(F, (v, i) => (fixed[i] ? 0 : v));
  let z = r.map((v, i) => v / dg[i]), d = Float64Array.from(z), rz = r.reduce((s, v, i) => s + v * z[i], 0);
  const r0 = Math.sqrt(r.reduce((s, v) => s + v * v, 0));
  let it = 0;
  for (; it < 6000; it++) {
    const q = mul(d), al = rz / d.reduce((s, v, i) => s + v * q[i], 0);
    for (let i = 0; i < N; i++) { u[i] += al * d[i]; r[i] -= al * q[i]; }
    if (Math.sqrt(r.reduce((s, v) => s + v * v, 0)) < 1e-10 * r0) break;
    z = r.map((v, i) => v / dg[i]);
    const rz2 = r.reduce((s, v, i) => s + v * z[i], 0), be = rz2 / rz; rz = rz2;
    for (let i = 0; i < N; i++) d[i] = z[i] + be * d[i];
  }
  let un = 0;
  contacts.forEach((near, k) => {
    const ux = near.reduce((s, n) => s + u[2 * n], 0) / 3, uy = near.reduce((s, n) => s + u[2 * n + 1], 0) / 3;
    un += -(ux * normals[k][0] + uy * normals[k][1]);
  });
  const drop = un / 2 / Math.sin(a);
  return { m, u, drop, it, yc };
}

function check52b(api, s) {
  const p = api.p, sc = api.scene;
  s.r = solve52(p);
  s.e = { drop: s.r.drop, ok: s.r.drop * 1000 <= FE52.TOL_UM };
  const um = s.r.drop * 1000;
  if (sc === "steel" && p.ya <= 6 + 1e-9) api.done("thin");
  if (sc === "alu" && p.E <= 70 && p.B <= 60 + 1e-9 && p.Hb <= 40 + 1e-9) api.done("alu");
  if (sc === "print" && p.E <= 2 && um <= 30) api.done("print");
  if (sc === "steel" && p.alpha >= 120 - 1e-9) api.done("alpha");
}

WQ.lab({
  title: ["实验 52.9 V 形块的刚度", "Lab 52.9 Stiffness of a V-block"],
  goal: ["夹紧力和切削力会使夹具元件变形，工件跟着移动。用平面应力有限元算出 V 形块截面在夹紧力下的变形和工件轴心的下沉，比较钢、铝合金和 3D 打印尼龙做的 V 形块，看形状尺寸怎样影响刚度。",
         "Clamping and cutting forces deform fixture elements, and the work moves with them. A plane-stress finite element model of a V-block section gives its deformation and how far the work's axis sinks; compare steel, aluminium and 3D-printed nylon, and see how shape and size matter."],
  scenes: [
    { id: "steel", name: ["钢 V 形块", "Steel V-block"], params: { E: { value: 210 } },
      problem: { title: ["V 形块做薄一点行不行？", "Can the V-block be made thinner?"],
                 text: ["JJ-301-50 的 V 形块（宽 80、高 50，V 形槽顶点离底面 20 mm）每段工作面长 18 mm，承受约 1800 N。为了降低夹具高度，想把顶点到底面的厚度减到 5 mm（V 形槽相应加深），工件下沉会怎样变化？", "JJ-301-50's V-block (80 wide, 50 high, apex 20 mm above the base) carries about 1800 N per 18 mm land. To lower the fixture, the material under the apex might be cut to 5 mm (the V gets deeper). How will the sink change?"] } },
    { id: "alu", name: ["铝合金 V 形块", "Aluminium V-block"], params: { E: { value: 69 } },
      problem: { title: ["小批量试制用铝合金夹具", "An aluminium fixture for a pilot run"],
                 text: ["试制阶段想用铝合金快速做一套夹具。刚度够不够？", "For the pilot run an aluminium fixture would be quick to make. Is it stiff enough?"] } },
    { id: "print", name: ["3D 打印尼龙", "3D-printed nylon"], params: { E: { value: 1.7 }, W: { value: 1800 } },
      problem: { title: ["3D 打印的 V 形块能用吗？", "Will a 3D-printed V-block do?"],
                 text: ["机器人单元要换型，想用 3D 打印的尼龙 PA12 做 V 形块，当天就能换。要让工件下沉不超过 0.03 mm，夹紧力和工作面长度要怎样改？", "The robot cell changes over often; a PA12 V-block could be printed the same day. To keep the work's sink within 0.03 mm, how must the clamping force and land length change?"] } },
  ],
  params: [
    { id: "E", name: ["弹性模量 E", "Young's modulus E"], min: 1, max: 220, step: 0.1, value: 210, unit: "GPa", digits: 1 },
    { id: "W", name: ["每段工作面上的竖直力 W", "Vertical force per land W"], min: 100, max: 5000, step: 50, value: 1800, unit: "N", digits: 0 },
    { id: "t", name: ["工作面长度 t", "Land length t"], min: 6, max: 60, step: 1, value: 18, unit: "mm", digits: 0 },
    { id: "B", name: ["V 形块宽度 B", "Block width B"], min: 60, max: 120, step: 2, value: 80, unit: "mm", digits: 0 },
    { id: "Hb", name: ["V 形块高度", "Block height"], min: 36, max: 80, step: 2, value: 50, unit: "mm", digits: 0 },
    { id: "ya", name: ["V 形槽顶点离底面", "Apex above base"], min: 4, max: 30, step: 1, value: 20, unit: "mm", digits: 0 },
    { id: "alpha", name: ["V 形块夹角 α", "V angle α"], min: 60, max: 120, step: 5, value: 90, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--accent)", name: ["变形后的截面（放大）", "deformed section (magnified)"] }],
  tasks: [
    { id: "thin", text: ["钢：把顶点离底面的厚度减到 6 mm 以下，比较工件下沉的变化，解释结果为什么和直觉相反。", "Steel: cut the material under the apex to 6 mm or less, compare the sink, and explain why the result runs against intuition."],
      demo: { scene: "steel", set: { ya: 5 } } },
    { id: "alpha", text: ["钢：把夹角改为 120°，看下沉怎样变化，想一想为什么。", "Steel: open the angle to 120°, see how the sink changes, and think why."],
      demo: { scene: "steel", set: { alpha: 120, ya: 20 } } },
    { id: "alu", text: ["铝合金：读出工件下沉，判断是否不超过 5 µm；再把宽度减到 60 mm、高度减到 40 mm，下沉还在 5 µm 以内吗？", "Aluminium: read the sink and check it is within 5 µm; then cut the width to 60 mm and the height to 40 mm — is it still within 5 µm?"],
      demo: { scene: "alu", set: { E: 69, ya: 20, B: 60, Hb: 40 } } },
    { id: "print", text: ["3D 打印尼龙：调夹紧力和工作面长度，使工件下沉不超过 0.03 mm。", "Printed nylon: adjust force and land length so the sink is within 0.03 mm."],
      demo: { scene: "print", set: { E: 1.7, W: 500, t: 30 } } },
  ],
  think: ["工件下沉本身是一个常值，对刀时可以“吃掉”；真正影响一批工件尺寸的是什么？（提示：夹紧力的分散、材料的蠕变与温度。）",
          "The sink itself is a constant that tool setting can absorb. What really affects a batch? (Hint: scatter of the clamping force, creep and temperature of the material.)"],

  reset(api, s) { check52b(api, s); },
  update(dt, api, s) { check52b(api, s); api.stop(); },
  readouts(api, s) {
    const r = s.r || solve52(api.p), f = api.fmt, T = api.T, um = r.drop * 1000;
    return [
      [["工件轴心下沉", "Axis sink"], `${f(um, um < 10 ? 2 : 1)} µm`],
      [["与 30 µm 比较", "Against 30 µm"], um <= FE52.TOL_UM ? T("满足", "within") : T("超过", "exceeds")],
      [["节点 / 单元 / 迭代次数", "Nodes / elements / iterations"], `${r.m.xy.length} / ${r.m.tri.length} / ${r.it}`]];
  },
  draw(api, s) {
    const r = s.r || solve52(api.p), { w, h } = api, css = api.css, p = api.p, ctx = api.ctx;
    let umax = 0; for (let i = 0; i < r.u.length; i++) umax = Math.max(umax, Math.abs(r.u[i]));
    const sc = Math.min(w * 0.55 / p.B, h * 0.75 / (p.Hb + 25)), ox = w * 0.32, oy = h * 0.9, mag = (p.B * 0.06) / Math.max(umax, 1e-12);
    const X = (q, i) => ox + sc * (q[0] + mag * r.u[2 * i]), Y = (q, i) => oy - sc * (q[1] + mag * r.u[2 * i + 1]);
    ctx.lineWidth = 0.5;
    for (const tr of r.m.tri) {
      ctx.beginPath();
      tr.forEach((n, k) => { const q = r.m.xy[n]; if (k) ctx.lineTo(X(q, n), Y(q, n)); else ctx.moveTo(X(q, n), Y(q, n)); });
      ctx.closePath(); ctx.fillStyle = "rgba(58,125,201,0.18)"; ctx.fill(); ctx.strokeStyle = "rgba(58,125,201,0.5)"; ctx.stroke();
    }
    api.circle(ox, oy - sc * r.yc, sc * FE52.D / 2, null, css("--muted"));
    api.line(ox - sc * p.B * 0.6, oy, ox + sc * p.B * 0.6, oy, css("--ink"), 2);
    api.label(api.T(`位移放大 ${api.fmt(mag, 0)} 倍`, `displacement × ${api.fmt(mag, 0)}`), w * 0.06, h * 0.08, css("--muted"), 12);
  },
});
