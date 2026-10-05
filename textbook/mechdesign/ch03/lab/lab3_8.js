// 实验 3.8 参数化轴承座（配 3.8 节）。与程序 3.8.1 相同的设计规则：选轴承型号，全部尺寸跟着推出来，三视图（第一角画法）同时重画。
// 轴承尺寸取本书标准表 std/gbt276_6200.yaml（GB/T 276）；R20 优先数；地脚螺栓通孔按 GB/T 5277 中等装配。
const BRG3_8 = [["6204", 20, 47, 14], ["6205", 25, 52, 15], ["6206", 30, 62, 16], ["6207", 35, 72, 17], ["6208", 40, 80, 18],
  ["6209", 45, 85, 19], ["6210", 50, 90, 20], ["6211", 55, 100, 21], ["6212", 60, 110, 22]];
const R20_3_8 = [10, 11.2, 12.5, 14, 16, 18, 20, 22.4, 25, 28, 31.5, 35.5, 40, 45, 50, 56, 63, 71, 80, 90, 100, 112, 125];
function geo3_8(p) {
  const b = BRG3_8[Math.round(p.brg)], D = b[2], B = b[3];
  const wall = Math.round(p.kw * D + 3);
  const RoRule = D / 2 + wall;
  const Ro = Math.round(p.intent) === 1 ? 48 : RoRule;                   // 1 = 圆弧半径写死为 6207 时的 48 mm（设计意图不对）
  const H = R20_3_8.find((v) => v >= RoRule + 2);
  const [bolt, dh] = D <= 52 ? ["M8", 9] : D <= 72 ? ["M10", 11] : ["M12", 13.5];
  const W = B + 14, Wb = W + 12, tb = Math.round(p.kt * H), Lh = 2 * (RoRule + dh + 2), L = Math.ceil(Lh + 3 * dh);   // 底板按规则（与程序 3.7.1 的草图相同，只有圆弧半径写死）
  const D2 = D - 8, seat = B + 4, Lr = Lh - 2 * dh - 10, hr = 2, dg = 6;
  // 体积（mm³）：底板 + 立板 + 半圆 − 孔 − 地脚孔 − 挖空 − 注油孔（近似，用来估质量）
  const vol = L * Wb * tb + 2 * Ro * W * (H - tb) + Math.PI * Ro * Ro / 2 * W - Math.PI * D * D / 4 * seat - Math.PI * D2 * D2 / 4 * (W - seat)
    - 2 * Math.PI * dh * dh / 4 * tb - Lr * Wb * hr - Math.PI * dg * dg / 4 * (Ro - D / 2);
  return { code: b[0], d: b[1], D, B, wall: Ro - D / 2, Ro, H, bolt, dh, W, Wb, tb, Lh, L, D2, seat, Lr, hr, dg, mass: vol * 7.2e-6, under: tb - (H - D / 2) };
}
WQ.lab({
  title: ["实验 3.8 参数化轴承座", "Lab 3.8 A parametric pillow block"],
  goal: ["选一个轴承型号，轴承座的全部尺寸按设计规则推出来，三视图同时重画——模型、图纸、BOM 里的规格都从同一组参数来。再试一试“设计意图不对”的模型改参数以后会怎样。",
         "Pick a bearing; every size of the pillow block follows from the design rules and the three views redraw — model, drawing and BOM all come from one set of parameters. Then see what happens when the design intent is wrong."],
  scenes: [
    { id: "robot", robot: true, name: ["码垛输送线的滚筒", "Palletizing conveyor roller"],
      problem: { title: ["工程问题：码垛工位输送线滚筒的轴承座", "Engineering problem: pillow blocks for a palletizing conveyor roller"],
                 text: ["码垛机器人旁边的辊道输送线，滚筒轴 Ø35，两端各用一个轴承座支承，装在机架的横梁上。按轴承型号生成轴承座，读出中心高、底板长和地脚螺栓，交给机架设计。",
                        "The roller conveyor beside a palletizing robot has Ø35 roller shafts, each end in a pillow block bolted to the frame. Generate the block from the bearing and hand the center height, base length and bolts to the frame designer."] } },
    { id: "life", name: ["跑步机的滚筒", "Treadmill roller"],
      problem: { title: ["生活中的例子：家用跑步机", "Everyday example: a home treadmill"],
                 text: ["跑步机前后两根滚筒带着跑带转，滚筒轴两端也是轴承座。轴细、载荷小，看看规格小一号时，底板厚度的系数怎样影响尺寸和质量。",
                        "A treadmill's two rollers drive the belt; their shafts also run in pillow blocks. With a thin shaft and light load, see how the base-thickness factor changes size and mass."] } },
  ],
  params: [
    { id: "brg", name: ["轴承型号（0 = 6204 … 8 = 6212）", "Bearing (0 = 6204 … 8 = 6212)"], min: 0, max: 8, step: 1, value: 3, unit: "", digits: 0 },
    { id: "kw", name: ["壁厚系数（壁厚 = 系数 × D + 3）", "Wall factor (wall = factor × D + 3)"], min: 0.08, max: 0.2, step: 0.01, value: 0.12, unit: "", digits: 2 },
    { id: "kt", name: ["底板厚系数（底板厚 = 系数 × 中心高）", "Base factor (base = factor × center height)"], min: 0.15, max: 0.35, step: 0.01, value: 0.25, unit: "", digits: 2 },
    { id: "intent", name: ["圆弧半径（0 = 随轴承外径，1 = 写死 48 mm）", "Arc radius (0 = follows bearing OD, 1 = fixed 48 mm)"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["生成", "Generate"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "var(--ink)", name: ["可见轮廓（粗实线）", "visible outline (thick)"] }, { color: "var(--muted)", name: ["不可见轮廓（虚线）、中心线（点画线）", "hidden (dashed), center lines (chain)"] }],
  tasks: [
    { id: "std", robot: true, text: ["滚筒轴 Ø35 用 6207：生成轴承座，读出中心高 H、底板长 L、地脚螺栓规格。", "A Ø35 roller shaft takes a 6207: generate the block and read the center height H, base length L and bolt size."],
      demo: { scene: "robot", set: { brg: 3, kw: 0.12, kt: 0.25, intent: 0 }, press: ["start"], wait: 1 } },
    { id: "intent", robot: true, text: ["载荷加大，改用 6209。先按“圆弧半径写死 48 mm”生成，看壁厚剩多少；再改回“随轴承外径”。", "The load grows; use a 6209. First generate with the arc radius fixed at 48 mm and read the wall; then switch back to “follows bearing OD”."],
      demo: { scene: "robot", set: { brg: 5, kw: 0.12, kt: 0.25, intent: 1 }, press: ["start"], wait: 1 } },
    { id: "life", text: ["跑步机滚筒用 6205，把底板厚系数从 0.25 改到 0.35，记下底板厚和质量的变化。", "A treadmill roller takes a 6205; raise the base factor from 0.25 to 0.35 and note how base thickness and mass change."],
      demo: { scene: "life", set: { brg: 1, kw: 0.12, kt: 0.35, intent: 0 }, press: ["start"], wait: 1 } },
  ],
  think: ["程序 3.8.1 和这个实验用的是同一套设计规则。如果规则里“中心高取 R20 优先数”改成“中心高 = 圆弧半径 + 2”，产品系列会有什么变化？哪一种更好？",
          "Program 3.8.1 and this lab share the same design rules. If “center height from R20” became “center height = arc radius + 2”, how would the product series change? Which is better?"],

  reset(api, s) { s.g = null; },
  update(dt, api, s) {
    const p = api.p, g = geo3_8(p);
    s.g = g;
    if (api.scene === "robot" && g.code === "6207" && Math.round(p.intent) === 0) api.done("std");
    if (api.scene === "robot" && g.code === "6209" && Math.round(p.intent) === 1) api.done("intent");
    if (api.scene === "life" && g.code === "6205" && p.kt >= 0.345 && Math.round(p.intent) === 0) api.done("life");
    api.stop();
  },
  readouts(api, s) {
    const g = geo3_8(api.p), f = api.fmt;
    return [
      [["轴承 d × D × B", "Bearing d × D × B"], g.code + "：" + g.d + " × " + g.D + " × " + g.B + " mm"],
      [["中心高 H（R20）", "Center height H (R20)"], f(g.H, 1) + " mm"],
      [["壁厚", "Wall"], f(g.wall, 1) + " mm" + (g.wall < 8 ? api.T("（太薄！）", " (too thin!)") : "")],
      [["底板 L × 宽 × 厚", "Base L × width × thickness"], g.L + " × " + g.Wb + " × " + g.tb + " mm"],
      [["地脚螺栓、孔距", "Bolts, spacing"], "2 × " + g.bolt + "，" + f(g.Lh, 0) + " mm"],
      [["质量（HT200）", "Mass (HT200)"], f(g.mass, 2) + " kg"],
    ];
  },
  draw(api, s) {
    const { w, h, ctx } = api, css = api.css, g = geo3_8(api.p);
    const ink = css("--ink"), mut = css("--muted"), red = css("--red");
    const gap = 26, totW = g.L + gap + g.Wb, totH = g.H + g.Ro + gap + g.Wb;
    const k = Math.min((w - 60) / totW, (h - 50) / totH);
    const fx = 30 + g.L / 2 * k, fy = 20 + (g.H + g.Ro) * k;                 // 主视图原点（底面中点）
    const tx = fx, ty = fy + gap * k + g.Wb / 2 * k;                          // 俯视图原点（中心）
    const lx = fx + (g.L / 2 + gap + g.Wb / 2) * k, ly = fy;                  // 左视图原点
    const VIS = [2.2, []], HID = [1, [6, 4]], CEN = [1, [14, 3, 2, 3]];
    const seg = (x0, y0, x1, y1, st, col) => api.line(x0, y0, x1, y1, col || (st === VIS ? ink : mut), st[0], st[1]);
    const F = (x, z) => [fx + x * k, fy - z * k], Tp = (x, y) => [tx + x * k, ty - y * k], Lf = (u, z) => [lx + u * k, ly - z * k];
    const L2 = (P, a, b, c, d, st, col) => { const p = P(a, b), q = P(c, d); seg(p[0], p[1], q[0], q[1], st, col); };
    const arc = (cx, cy, r, a0, a1, st, col) => { ctx.save(); ctx.strokeStyle = col || (st === VIS ? ink : mut); ctx.lineWidth = st[0]; ctx.setLineDash(st[1]);
      ctx.beginPath(); ctx.arc(cx, cy, r, a0, a1); ctx.stroke(); ctx.restore(); };
    const wallCol = g.wall < 8 ? red : null;
    // ---- 主视图
    const { L, Wb, W, tb, H, Ro, D, D2, Lh, dh, Lr, hr, seat, dg } = g;
    [[-L / 2, 0, -L / 2, tb], [L / 2, 0, L / 2, tb], [-L / 2, tb, -Ro, tb], [Ro, tb, L / 2, tb], [-L / 2, 0, -Lr / 2, 0], [Lr / 2, 0, L / 2, 0],
      [-Lr / 2, 0, -Lr / 2, hr], [Lr / 2, 0, Lr / 2, hr], [-Lr / 2, hr, Lr / 2, hr], [-Ro, tb, -Ro, H], [Ro, tb, Ro, H]].forEach((a) => L2(F, ...a, VIS, a[0] === Ro || a[0] === -Ro ? wallCol : null));
    const c = F(0, H);
    arc(c[0], c[1], Ro * k, Math.PI, 2 * Math.PI, VIS, wallCol);
    arc(c[0], c[1], D / 2 * k, 0, 2 * Math.PI, VIS, wallCol);
    arc(c[0], c[1], D2 / 2 * k, 0, 2 * Math.PI, VIS);
    [-1, 1].forEach((sg) => { [-dh / 2, dh / 2].forEach((e) => L2(F, sg * Lh / 2 + e, 0, sg * Lh / 2 + e, tb, HID)); L2(F, sg * Lh / 2, -3, sg * Lh / 2, tb + 3, CEN); });
    [-dg / 2, dg / 2].forEach((e) => L2(F, e, H + D / 2, e, H + Ro, HID));
    L2(F, -Ro - 5, H, Ro + 5, H, CEN); L2(F, 0, H - Ro - 5, 0, H + Ro + 5, CEN);
    // ---- 俯视图（Y 向上 = 向后）
    [[-L / 2, -Wb / 2, L / 2, -Wb / 2], [L / 2, -Wb / 2, L / 2, Wb / 2], [L / 2, Wb / 2, -L / 2, Wb / 2], [-L / 2, Wb / 2, -L / 2, -Wb / 2],
      [-Ro, -W / 2, Ro, -W / 2], [Ro, -W / 2, Ro, W / 2], [Ro, W / 2, -Ro, W / 2], [-Ro, W / 2, -Ro, -W / 2]].forEach((a) => L2(Tp, ...a, VIS));
    [-1, 1].forEach((sg) => { const q = Tp(sg * Lh / 2, 0); arc(q[0], q[1], dh / 2 * k, 0, 2 * Math.PI, VIS); L2(Tp, sg * Lh / 2 - dh, 0, sg * Lh / 2 + dh, 0, CEN); L2(Tp, sg * Lh / 2, -dh, sg * Lh / 2, dh, CEN);
      L2(Tp, sg * D / 2, -W / 2, sg * D / 2, -W / 2 + seat, HID); L2(Tp, sg * D2 / 2, -W / 2 + seat, sg * D2 / 2, W / 2, HID); L2(Tp, sg * Lr / 2, -Wb / 2, sg * Lr / 2, Wb / 2, HID); });
    L2(Tp, -D / 2, -W / 2 + seat, D / 2, -W / 2 + seat, HID);
    const gq = Tp(0, 0); arc(gq[0], gq[1], dg / 2 * k, 0, 2 * Math.PI, VIS);
    L2(Tp, 0, -Wb / 2 - 4, 0, Wb / 2 + 4, CEN);
    // ---- 左视图（u = −Y：前面在右）
    [[-Wb / 2, hr, -Wb / 2, tb], [Wb / 2, hr, Wb / 2, tb], [-Wb / 2, tb, -W / 2, tb], [W / 2, tb, Wb / 2, tb], [-W / 2, tb, -W / 2, H + Ro], [W / 2, tb, W / 2, H + Ro],
      [-W / 2, H + Ro, W / 2, H + Ro], [-Wb / 2, 0, Wb / 2, 0], [-Wb / 2, 0, -Wb / 2, hr], [Wb / 2, 0, Wb / 2, hr]].forEach((a) => L2(Lf, ...a, VIS));
    [-1, 1].forEach((sg) => { L2(Lf, W / 2, H + sg * D / 2, W / 2 - seat, H + sg * D / 2, HID); L2(Lf, W / 2 - seat, H + sg * D2 / 2, -W / 2, H + sg * D2 / 2, HID);
      L2(Lf, sg * dh / 2, 0, sg * dh / 2, tb, HID); L2(Lf, sg * dg / 2, H + D / 2, sg * dg / 2, H + Ro, HID); });
    L2(Lf, W / 2 - seat, H - D / 2, W / 2 - seat, H + D / 2, HID); L2(Lf, -Wb / 2, hr, Wb / 2, hr, HID);
    L2(Lf, -Wb / 2 - 5, H, Wb / 2 + 5, H, CEN);
    // ---- 视图名称与几个主要尺寸
    const lab = (t, x, y) => api.label(t, x, y, mut, 12, "center");
    lab(api.T("主视图", "Front"), fx, fy + 14);
    lab(api.T("俯视图", "Top"), tx, ty + (Wb / 2) * k + 14);
    lab(api.T("左视图", "Left"), lx, ly + 14);
    api.label("H = " + api.fmt(H, 1), F(Ro, H)[0] + 8, F(0, H)[1] - 8, ink, 12, "left");
    api.label("L = " + L, F(-L / 2, 0)[0], F(0, tb)[1] - 10, ink, 12, "left");
    if (g.wall < 8) api.label(api.T("壁厚只剩 ", "wall only ") + api.fmt(g.wall, 1) + " mm", c[0], c[1] - Ro * k - 10, red, 13, "center");
  },
});
