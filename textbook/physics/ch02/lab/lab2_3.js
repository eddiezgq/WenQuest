// 实验 2.3 力的合成与分解：测量（配 2.2、2.3 节）。测量型实验：读数带误差，学生自己按分量计算。
// 吊索场景：两只拉力传感器的读数含约 ±0.9% 以内的随机误差（按角度确定的伪随机数，同样的角度读数相同），由 T₁cos α + T₂cos β
// 求出未知壳体的重力。坡道场景：拖车绳上的拉力计读出把 AGV 拉住的力 F = mg sin α（含误差），记录几组，作 F–sin α 图拟合
// 斜率求出总质量；判定按学生自己的数据拟合，不与真实值比较。力学台：两个力固定，学生调第三个力使圆环居中；
// 滑轮有摩擦，合力小于 0.03 N 时圆环不动（这就是力学台的“不灵敏区”）。记录放在闭包里，重置时不丢。
const G23 = 9.81, M_SL = 31.4, M_AGV = 420;              // 壳体质量与 AGV 总质量（学生不知道）
const rec23 = { pts: [], pairs: new Set() };               // 坡道：[α, F]；吊索：看过的角度组合
const rad23 = (d) => d * Math.PI / 180;
function hash23(a, b) { let x = Math.sin(a * 12.9898 + b * 78.233 + 1.2345) * 43758.5453; return x - Math.floor(x); }
function noise23(a, b) { return (hash23(a, b) + hash23(b + 3.1, a + 7.7) - 1) * 0.0087; }   // 相对误差在 ±0.9% 以内（三角分布，标准偏差约 0.35%）
function slings23(p) {
  const W = M_SL * G23, s = Math.sin(rad23(p.al + p.be));
  const T1 = W * Math.sin(rad23(p.be)) / s, T2 = W * Math.sin(rad23(p.al)) / s;
  return { T1, T2, r1: Math.round(T1 * (1 + noise23(p.al, p.be)) * 10) / 10, r2: Math.round(T2 * (1 + noise23(p.be + 0.5, p.al)) * 10) / 10 };
}
function ramp23(a) { const F = M_AGV * G23 * Math.sin(rad23(a)); return Math.round((F * (1 + noise23(a, 1.7)) + 4 * (hash23(a, 9) - 0.5)) * 10) / 10; }
function fit23() {
  const q = rec23.pts; if (new Set(q.map((p) => p[0])).size < 2) return null;
  const xs = q.map((p) => Math.sin(rad23(p[0]))), n = q.length, mx = xs.reduce((s, x) => s + x, 0) / n, my = q.reduce((s, p) => s + p[1], 0) / n;
  let sxy = 0, sxx = 0; q.forEach((p, i) => { sxy += (xs[i] - mx) * (p[1] - my); sxx += (xs[i] - mx) ** 2; });
  return sxy / sxx / G23;                                  // 斜率 mg → m
}
const F1_23 = [0.100, 0], F2_23 = [0.150, 90], FRIC23 = 0.03;   // 力学台：质量 kg、方向
function table23(p) {
  const F = [[...F1_23], [...F2_23], [p.m3 / 1000, p.th3]].map(([m, t]) => [m * G23 * Math.cos(rad23(t)), m * G23 * Math.sin(rad23(t))]);
  const net = F.reduce((u, v) => [u[0] + v[0], u[1] + v[1]], [0, 0]), N = Math.hypot(net[0], net[1]);
  return { F, net, N, off: N < FRIC23 ? 0 : Math.min(1, (N - FRIC23) / 0.3) };
}
function line23(p) { const half = 1.5, sinp = p.sag / Math.hypot(p.sag, half), W = 2 * G23; return { T: W / (2 * sinp), W, phi: Math.asin(sinp) * 180 / Math.PI }; }

WQ.lab({
  title: ["实验 2.3 力的合成与分解：测量", "Lab 2.3 Adding and resolving forces: measurements"],
  goal: ["读出力传感器和角度，按分量算出未知的力或质量；在力学台上用第三个力平衡另外两个力。",
         "Read force sensors and angles, and find an unknown force or mass from components; balance two forces with a third on a force table."],
  scenes: [
    { id: "slings", robot: true, name: ["吊索称重", "Weighing with two slings"], hide: ["ang", "mhat", "m3", "th3", "sag"],
      problem: { title: ["机器人问题：吊起的壳体有多重", "Robot problem: how heavy is the hanging housing"],
                 text: ["两根吊索上各有一只拉力传感器（误差在 ±0.9% 以内）。调两根吊索与竖直方向的夹角，读出拉力，用竖直分量之和求壳体的重力，再点“提交我的结果”。",
                        "Each sling carries a load cell (error within ±0.9%). Set the sling angles from the vertical, read the tensions and find the housing's weight from the sum of vertical components, then press “Submit my result”."] } },
    { id: "ramp", robot: true, name: ["坡道上称 AGV", "Weighing an AGV on a ramp"], hide: ["al", "be", "What", "m3", "th3", "sag"],
      problem: { title: ["机器人问题：载货 AGV 的总质量", "Robot problem: the total mass of a loaded AGV"],
                 text: ["AGV 松开刹车停在可调的坡道上，一根平行于坡面的绳子经拉力计拉住它。拉力等于重力沿坡面的分量 mg sin α。改变倾角记录几组读数，拟合求出总质量。",
                        "The AGV, brakes off, is held on an adjustable ramp by a rope parallel to the slope through a force gauge. The pull equals the along-slope component mg sin α. Record several angles and fit to find the total mass."] } },
    { id: "table", name: ["力学台", "Force table"], hide: ["al", "be", "What", "ang", "mhat", "sag"],
      problem: { title: ["经典实验：力学台", "Classic experiment: the force table"],
                 text: ["两根线挂着 100 g 和 150 g 的砝码，方向分别为 0° 和 90°。调第三根线的方向和砝码，让中心的圆环不碰中心柱。",
                        "Two strings carry 100 g at 0° and 150 g at 90°. Set the direction and mass on the third string so that the ring stays clear of the centre pin."] } },
    { id: "line", name: ["晾衣绳", "Clothesline"], hide: ["al", "be", "What", "ang", "mhat", "m3", "th3"],
      problem: { title: ["生活中的例子：绳子绷得越直，拉力越大", "Everyday example: the straighter the line, the larger the tension"],
                 text: ["晾衣绳拴在相距 3 m 的两根柱子上，中间挂一件 2 kg 的湿外套。调下垂量，看绳上的拉力。",
                        "A 2 kg wet coat hangs at the middle of a line between two posts 3 m apart. Change the sag and watch the tension."] } },
  ],
  params: [
    { id: "al", name: ["吊索 1 与竖直方向的夹角 α", "Sling 1 from vertical α"], min: 10, max: 70, step: 1, value: 30, unit: "°", digits: 0 },
    { id: "be", name: ["吊索 2 与竖直方向的夹角 β", "Sling 2 from vertical β"], min: 10, max: 70, step: 1, value: 45, unit: "°", digits: 0 },
    { id: "What", name: ["你算出的壳体重力 F_g", "Your weight F_g"], min: 100, max: 500, step: 0.5, value: 200, unit: "N", digits: 1 },
    { id: "ang", name: ["坡道倾角 α", "Ramp angle α"], min: 1, max: 15, step: 0.5, value: 3, unit: "°", digits: 1 },
    { id: "mhat", name: ["你算出的 AGV 总质量", "Your AGV mass"], min: 200, max: 700, step: 1, value: 300, unit: "kg", digits: 0 },
    { id: "m3", name: ["第三根线的砝码", "Mass on string 3"], min: 0, max: 300, step: 5, value: 100, unit: "g", digits: 0 },
    { id: "th3", name: ["第三根线的方向", "Direction of string 3"], min: 0, max: 359, step: 1, value: 180, unit: "°", digits: 0 },
    { id: "sag", name: ["绳子中点的下垂量", "Sag at the middle"], min: 0.02, max: 1, step: 0.01, value: 0.4, unit: "m", digits: 2 },
  ],
  buttons: [{ id: "submit", name: ["提交我的结果（吊索）", "Submit my result (slings)"] }, { id: "rec", name: ["记录这一组（坡道）", "Record this angle (ramp)"], primary: true }, { id: "sweep", name: ["依次在 3°、6°、9°、12° 记录（坡道）", "Record at 3°, 6°, 9°, 12° (ramp)"] },
            { id: "clear", name: ["清空记录", "Clear records"] }],
  tasks: [
    { id: "W", robot: true, text: ["吊索称重：至少换两组角度读数，算出壳体的重力，把“你算出的壳体重力”调到你的结果，点“提交我的结果”（与真实值相差 1.5% 以内才算对）。",
                                  "Slings: read at least two pairs of angles, compute the weight, set “Your weight” and press “Submit my result” (within 1.5% of the true value)."],
      demo: { scene: "slings", set: { al: 20, be: 40, What: 308 }, press: ["submit"], wait: 1 } },
    { id: "m", robot: true, text: ["坡道：至少记录 4 个不同的倾角，拟合 F–sin α 的斜率，把“你算出的 AGV 总质量”调到你的拟合结果（相差 1% 以内）。",
                                  "Ramp: record at least 4 angles, fit the slope of F against sin α and set “Your AGV mass” to your fit (within 1%)."],
      demo: { scene: "ramp", set: { ang: 3, mhat: 418 }, press: ["clear", "sweep"], wait: 1 } },
    { id: "bal", text: ["力学台：调第三个力，让圆环居中不动。", "Force table: set the third force so that the ring sits in the middle."],
      demo: { scene: "table", set: { m3: 180, th3: 236 }, press: [], wait: 1 } },
    { id: "taut", text: ["晾衣绳：把绳子拉到拉力超过外套重力的 5 倍，这时下垂量是多少？", "Clothesline: pull the line until the tension exceeds 5 times the coat's weight. What is the sag then?"],
      demo: { scene: "line", set: { sag: 0.14 }, press: [], wait: 1 } },
  ],
  think: ["吊索称重时，α、β 取多大，算出的重力误差最小？力学台上第三个力的方向在多大范围内圆环都不动？这个范围对测量结果意味着什么？",
          "Which sling angles give the smallest error in the weight? Over what range of directions does the ring stay put on the force table, and what does that range mean for the result?"],

  reset(api, s) {},
  action(id, api, s) {
    if (id === "clear") rec23.pts.length = 0;
    if (id === "submit" && api.scene === "slings") {
      s.sub = rec23.pairs.size >= 2 && Math.abs(api.p.What - M_SL * G23) / (M_SL * G23) < 0.015;
      s.msg = rec23.pairs.size < 2 ? api.T("先换至少两组角度读数", "read at least two pairs of angles first")
            : s.sub ? api.T("对了", "correct") : api.T("不对，再检查计算", "not yet, check your working");
      if (s.sub) api.done("W");
    }
    if (api.scene === "ramp") {
      const add = (a) => rec23.pts.push([a, ramp23(a)]);
      if (id === "rec") add(api.p.ang);
      if (id === "sweep") [3, 6, 9, 12].forEach(add);
    }
    check23(api);
  },
  change(api, s, pid) { if (api.scene === "slings") rec23.pairs.add(api.p.al + "," + api.p.be); check23(api); },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "slings") { const S = slings23(api.p); return [[["传感器 1 读数 F_T1", "Load cell 1, F_T1"], f(S.r1, 1) + " N"], [["传感器 2 读数 F_T2", "Load cell 2, F_T2"], f(S.r2, 1) + " N"],
      [["α、β", "α, β"], `${api.p.al}°, ${api.p.be}°`], [["看过的角度组合", "Angle pairs read"], String(rec23.pairs.size)], [["提交结果", "Submission"], s.msg || "—"]]; }
    if (api.scene === "ramp") { return [[["拉力计读数 F", "Gauge reading F"], f(ramp23(api.p.ang), 1) + " N"], [["sin α", "sin α"], f(Math.sin(rad23(api.p.ang)), 4)],
      [["已记录", "Recorded"], String(rec23.pts.length) + api.T(" 组", " points")]]; }
    if (api.scene === "table") { const T = table23(api.p); return [[["圆环偏离中心", "Ring off centre"], T.off ? f(T.off * 30, 0) + " mm" : api.T("居中", "centred")],
      [["第三个力", "Third force"], f(api.p.m3 / 1000 * G23, 3) + " N, " + api.p.th3 + "°"]]; }
    const L = line23(api.p); return [[["绳与水平的夹角", "Line angle from horizontal"], f(L.phi, 1) + "°"], [["绳上的拉力", "Tension"], f(L.T, 0) + " N"], [["拉力 / 外套重力", "Tension / weight"], f(L.T / L.W, 1)]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted");
    if (api.scene === "slings") {
      const S = slings23(api.p), cx = w * 0.45, hy = h * 0.68, Lr = h * 0.55;
      const A1 = [cx - Lr * Math.sin(rad23(api.p.al)), hy - Lr * Math.cos(rad23(api.p.al))], A2 = [cx + Lr * Math.sin(rad23(api.p.be)), hy - Lr * Math.cos(rad23(api.p.be))];
      const top = Math.min(A1[1], A2[1]);
      api.rect(A1[0] - 30, top - 14, A2[0] - A1[0] + 60, 10, mut);
      [[A1, S.r1, "1"], [A2, S.r2, "2"]].forEach(([A, r, n]) => {
        api.line(A[0], top - 4, A[0], A[1], ink, 2); api.line(A[0], A[1], cx, hy, ink, 2);
        const mx = (A[0] + cx) / 2, my = (A[1] + hy) / 2; api.rect(mx - 30, my - 12, 60, 24, css("--panel"), ink, 4);
        api.label(api.fmt(r, 1) + " N", mx, my, css("--blue"), 12, "center"); api.label(n, mx, my - 22, mut, 11, "center"); });
      api.line(cx, hy, cx, hy - h * 0.3, mut, 1, [4, 4]);
      api.label(`α = ${api.p.al}°`, cx - 70, hy - 40, mut, 12); api.label(`β = ${api.p.be}°`, cx + 14, hy - 40, mut, 12);
      api.rect(cx - 50, hy, 100, 60, "#c8d0d4", ink, 4); api.label(api.T("壳体", "housing"), cx, hy + 30, ink, 13, "center");
      return;
    }
    if (api.scene === "ramp") {
      const a = rad23(api.p.ang * 2.5), x0 = w * 0.06, y0 = h * 0.82, L = w * 0.44;   // 画面中的坡度放大 2.5 倍
      api.ctx.fillStyle = "#e6eaec"; api.ctx.beginPath(); api.ctx.moveTo(x0, y0); api.ctx.lineTo(x0 + L * Math.cos(a), y0); api.ctx.lineTo(x0 + L * Math.cos(a), y0 - L * Math.sin(a)); api.ctx.closePath(); api.ctx.fill();
      const px = x0 + 0.5 * L * Math.cos(a), py = y0 - 0.5 * L * Math.sin(a);
      api.ctx.save(); api.ctx.translate(px, py); api.ctx.rotate(-a); api.agv(0, 0, 70); api.ctx.restore();
      const ax = x0 + L * Math.cos(a), ay = y0 - L * Math.sin(a) - 12;
      api.line(px + 35 * Math.cos(a), py - 35 * Math.sin(a) - 12, ax, ay, ink, 1.5); api.rect(ax - 4, ay - 30, 8, 40, mut);
      api.label(api.fmt(ramp23(api.p.ang), 1) + " N", ax - 10, ay - 40, css("--blue"), 13, "right");
      api.label(api.T("坡度在画面中放大了", "slope exaggerated"), x0, h - 12, mut, 11);
      const P = api.plot(w * 0.58, 24, w * 0.38, h - 80, [], { xmin: 0, xmax: 0.27, ymin: 0, ymax: 1100, xlabel: "sin α", ylabel: "F / N" });
      rec23.pts.forEach((q) => api.circle(P.X(Math.sin(rad23(q[0]))), P.Y(q[1]), 4, css("--blue"), ink));
      // 只画数据点，不画拟合线：拟合由学生自己做
      return;
    }
    if (api.scene === "table") {
      const T = table23(api.p), cx = w * 0.42, cy = h * 0.5, R = Math.min(w, h) * 0.38;
      api.circle(cx, cy, R, css("--panel"), ink);
      for (let d = 0; d < 360; d += 10) { const c = Math.cos(rad23(d)), sn = Math.sin(rad23(d)), l = d % 30 ? 6 : 12;
        api.line(cx + (R - l) * c, cy - (R - l) * sn, cx + R * c, cy - R * sn, mut, 1); if (d % 30 === 0) api.label(String(d), cx + (R + 16) * c, cy - (R + 16) * sn, mut, 11, "center"); }
      const k = T.off * R * 0.25, dir = T.N > 0 ? [T.net[0] / T.N, T.net[1] / T.N] : [0, 0];
      const rx = cx + k * dir[0], ry = cy - k * dir[1];
      [[...F1_23], [...F2_23], [api.p.m3 / 1000, api.p.th3]].forEach(([m, t], i) => {
        const c = Math.cos(rad23(t)), sn = Math.sin(rad23(t)); api.line(rx, ry, cx + R * c, cy - R * sn, ink, 1.5);
        api.circle(cx + R * c, cy - R * sn, 6, mut, ink); api.label(api.fmt(m * 1000, 0) + " g", cx + (R + 46) * c, cy - (R + 46) * sn, [css("--blue"), css("--green"), css("--red")][i], 12, "center"); });
      api.circle(cx, cy, 4, ink); api.circle(rx, ry, 11, null, T.off ? css("--red") : css("--green"));
      api.label(T.off ? api.T("圆环被拉偏了", "ring pulled aside") : api.T("圆环居中", "ring centred"), cx, cy + R + 36, T.off ? css("--red") : css("--green"), 13, "center");
      return;
    }
    const L = line23(api.p), x1 = w * 0.15, x2 = w * 0.85, yt = h * 0.25, S = (x2 - x1) / 3, mx = (x1 + x2) / 2, my = yt + S * api.p.sag;
    api.rect(x1 - 6, yt - 10, 8, h * 0.7, mut); api.rect(x2 - 2, yt - 10, 8, h * 0.7, mut);
    api.line(x1, yt, mx, my, ink, 2); api.line(mx, my, x2, yt, ink, 2);
    api.rect(mx - 22, my, 44, 50, css("--amber"), ink, 6);
    api.label(`${api.fmt(L.T, 0)} N`, (x1 + mx) / 2, (yt + my) / 2 - 16, css("--red"), 13, "center");
    api.label(api.T("外套 2 kg", "coat 2 kg"), mx, my + 64, ink, 12, "center");
  },
});

function check23(api) {
  const m = fit23();
  if (m && new Set(rec23.pts.map((p) => p[0])).size >= 4 && Math.abs(api.p.mhat - m) / m < 0.01) api.done("m");
  if (api.scene === "table" && table23(api.p).off === 0) api.done("bal");
  if (api.scene === "line" && line23(api.p).T > 5 * line23(api.p).W) api.done("taut");
}
