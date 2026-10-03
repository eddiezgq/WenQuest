// 实验 51.7 定位误差计算器与仿真（配 51.6–51.9 节）。
// V 形块：ΔY = T_d/(2 sin(α/2))，上母线 +T_d/2，下母线 −T_d/2；心轴：孔心可偏向任意方向，外圆对孔的跳动最大为 X_max；
// 一面两销：连线上离圆柱销 x 处一点，垂直连线方向的变动范围 X1(1 − x/L) + X2·x/L，沿连线方向 X1（tolerance.two_pins_point）。SH-301 槽底尺寸 H 的公差 0.17 mm、精车外圆公差 0.039 mm 取自数字工厂的工艺规程（程序 ex51_7 核对）。
const SH51 = { TH: 0.17, TD_FIN: 0.039 };

function rnd51(i) {                       // 可重复的伪随机数（同一组“工件”每次画法相同）
  const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
}

function eval51(api) {
  const p = api.p, sc = api.scene;
  if (sc === "vblock") {
    const s = Math.sin(p.alpha * Math.PI / 360);
    const c = p.td / (2 * s);
    return { sc, center: c, top: c + p.td / 2, bottom: c - p.td / 2, T: SH51.TH, err: c - p.td / 2, ok: c - p.td / 2 <= SH51.TH / 3 + 1e-12 };
  }
  if (sc === "mandrel") {
    const xmax = p.xmin + p.tdh + p.tdp;
    const T = 0.045;                       // 齿坯外圆对孔的径向跳动要求（教学示意值）
    // 孔心偏心最大 X_max/2，车出的外圆对孔的跳动 = 2 × 偏心，最大为 X_max
    return { sc, xmax, ecc: xmax / 2, T, err: xmax, ok: xmax <= T / 3 + 1e-12 };
  }
  // 一面两销：关节壳体（机器人），电机安装孔在两销连线上、离圆柱销 80 mm
  const x = 80, th = Math.atan((p.x1 + p.x2) / (2 * p.L));
  const perp = p.x1 * Math.abs(1 - x / p.L) + p.x2 * Math.abs(x / p.L), along = p.x1;
  const zone = Math.hypot(perp, along);     // 两个方向合成后占用的位置度公差带直径
  const T = 0.1;                            // 该孔的位置度要求 Ø0.1（教学示意值）
  return { sc, th, perp, along, zone, T, err: zone, ok: zone <= T / 3 + 1e-12 };
}

function check51(api, s) {
  const e = eval51(api), p = api.p;
  s.e = e;
  if (e.sc === "vblock" && !e.ok) api.done("bottom");
  if (e.sc === "vblock" && Math.abs(p.td - SH51.TD_FIN) < 1e-6 && p.alpha >= 120 - 1e-9 && e.ok) api.done("alpha");
  if (e.sc === "mandrel" && e.err <= 0.015 + 1e-12) api.done("mandrel");
  if (e.sc === "pins" && e.ok && p.L <= 120 + 1e-9) api.done("robot");
}

WQ.lab({
  title: ["实验 51.7 定位误差", "Lab 51.7 Locating error"],
  goal: ["定位误差来自两处：工序基准与定位基准不重合，以及定位基准本身在定位元件上的位移。调工件和定位元件的公差、V 形块的角度、两销的距离，看工序基准怎样随工件尺寸变化而移动，判断定位方案能不能用。",
         "Locating error comes from two places: the operation datum not coinciding with the locating datum, and the locating datum itself moving on the locator. Change the tolerances, the V-block angle and the pin spacing, watch how the operation datum moves with workpiece size, and judge whether a locating scheme will do."],
  scenes: [
    { id: "vblock", name: ["SH-301 铣键槽：V 形块", "SH-301 keyway: V-block"],
      params: { alpha: { value: 90 }, td: { value: 0.039 } },
      problem: { title: ["工厂问题：V 形块定位，槽底尺寸 H 保证得了吗？", "Factory problem: can a V-block hold the keyway depth H?"],
                 text: ["精车后的齿轮位 Ø40.3（0/−0.039）放在 90° V 形块上铣键槽，工序尺寸 H 从外圆下母线量起，公差 0.17 mm。工件直径在公差内变化时，下母线上下移动多少？如果改用粗车后的外圆（Ø41.5，公差 0.25）定位，还够不够？公差再大到多少就不行了？",
                        "The finish-turned gear seat Ø40.3 (0/−0.039) sits in a 90° V-block for keyway milling; H is measured from the bottom generatrix, tolerance 0.17 mm. How far does the bottom line move as the diameter varies? Would the rough-turned OD (Ø41.5, tolerance 0.25) still do? How wide can the tolerance get before it fails?"] } },
    { id: "mandrel", name: ["GR-302 齿坯：心轴", "GR-302 blank: mandrel"],
      params: { tdh: { value: 0.025 }, tdp: { value: 0.016 }, xmin: { value: 0.009 } },
      problem: { title: ["工厂问题：齿坯套在心轴上精车外圆，跳动超差", "Factory problem: blanks turned on a mandrel run out too much"],
                 text: ["大齿轮 GR-302 的齿坯孔 Ø35 H7 套在 g6 心轴上精车外圆和端面，外圆对孔的径向跳动要求 0.045 mm（教学示意值）。孔与心轴的间隙让孔心可以偏到任意方向。间隙要多小，定位误差才不超过要求的三分之一？（你会发现要用到 IT4–IT5 级的配合——这正是生产中改用无间隙心轴的原因。）",
                        "Gear blank GR-302 (bore Ø35 H7) is turned on a g6 mandrel; the OD runout to the bore must be within 0.045 mm (teaching value). The clearance lets the bore centre shift any way. How small must the clearance be for the locating error to stay within a third of that? (You will find it takes IT4–IT5 fits, which is why clearance-free mandrels are used.)"] } },
    { id: "pins", robot: true, name: ["关节壳体：一面两销", "joint housing: plane + two pins"],
      params: { L: { value: 200 }, x1: { value: 0.025 }, x2: { value: 0.03 } },
      problem: { title: ["机器人问题：小型关节壳体的两个销孔离得很近", "Robot problem: a small joint housing has its pin holes close together"],
                 text: ["协作机器人关节壳体用底面和两个 Ø6 销孔定位镗电机安装孔，孔在两销连线上、离圆柱销 80 mm，位置度要求 Ø0.1 mm（教学示意值）。壳体小，两销孔距离只能做到 120 mm 以内。怎样选两个销的间隙，才能保证？",
                        "A cobot joint housing is located by its base and two Ø6 pin holes to bore a motor seat on the pin line 80 mm from the round pin, position tolerance Ø0.1 mm (teaching value). The housing is small: the pin holes can be at most 120 mm apart. What pin clearances will do?"] } },
  ],
  params: [
    { id: "alpha", name: ["V 形块夹角 α", "V-block angle α"], min: 60, max: 150, step: 5, value: 90, unit: "°", digits: 0 },
    { id: "td", name: ["定位外圆的直径公差 T_d", "Locating OD tolerance T_d"], min: 0.005, max: 0.5, step: 0.001, value: 0.039, unit: "mm", digits: 3 },
    { id: "tdh", name: ["孔的公差 T_D", "Bore tolerance T_D"], min: 0.005, max: 0.06, step: 0.001, value: 0.025, unit: "mm", digits: 3 },
    { id: "tdp", name: ["心轴的公差 T_d", "Mandrel tolerance T_d"], min: 0.003, max: 0.04, step: 0.001, value: 0.016, unit: "mm", digits: 3 },
    { id: "xmin", name: ["最小间隙 X_min", "Minimum clearance X_min"], min: 0, max: 0.03, step: 0.001, value: 0.009, unit: "mm", digits: 3 },
    { id: "L", name: ["两销孔距离 L", "Pin spacing L"], min: 40, max: 300, step: 5, value: 200, unit: "mm", digits: 0 },
    { id: "x1", name: ["圆柱销最大间隙 X1max", "Round-pin clearance X1max"], min: 0.003, max: 0.06, step: 0.001, value: 0.025, unit: "mm", digits: 3 },
    { id: "x2", name: ["削边销最大间隙 X2max", "Diamond-pin clearance X2max"], min: 0.003, max: 0.08, step: 0.001, value: 0.03, unit: "mm", digits: 3 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--accent)", name: ["一批工件的工序基准位置", "datum positions of a batch"] }, { color: "var(--red)", name: ["公差的 1/3", "a third of the tolerance"] }],
  tasks: [
    { id: "bottom", text: ["V 形块：把 T_d 调大（相当于用粗车后的外圆定位），找到下母线的定位误差超过 H 公差三分之一的时候。", "V-block: widen T_d (as if locating on the rough-turned OD) until the bottom-generatrix error exceeds a third of H's tolerance."],
      demo: { scene: "vblock", set: { alpha: 90, td: 0.5 } } },
    { id: "alpha", text: ["V 形块：T_d 回到 0.039，把夹角加大到 120°，看轴心和下母线的误差怎样变化。", "V-block: back to T_d = 0.039, open the angle to 120°, and see how the axis and bottom errors change."],
      demo: { scene: "vblock", set: { alpha: 120, td: 0.039 } } },
    { id: "mandrel", text: ["心轴：调孔和心轴的公差、最小间隙，使任意方向靠紧时的定位误差不超过 0.015 mm。", "Mandrel: adjust the tolerances and minimum clearance so the any-direction error is at most 0.015 mm."],
      demo: { scene: "mandrel", set: { tdh: 0.008, tdp: 0.006, xmin: 0 } } },
    { id: "robot", robot: true, text: ["关节壳体：两销孔距离不超过 120 mm，选两销的间隙使位置误差不超过要求的三分之一。", "Joint housing: with the pins at most 120 mm apart, choose the clearances so the position error is within a third of the tolerance."],
      demo: { scene: "pins", set: { L: 120, x1: 0.013, x2: 0.02 } } },
  ],
  think: ["V 形块定位时，工序尺寸从上母线、轴心、下母线量起，定位误差为什么差别这么大？设计夹具时，工序基准应当尽量选哪一个？",
          "With a V-block, why does the locating error differ so much depending on whether the dimension is measured from the top, the axis or the bottom? Which should the operation datum be when designing a fixture?"],

  reset(api, s) { check51(api, s); },
  update(dt, api, s) { check51(api, s); api.stop(); },
  readouts(api, s) {
    const e = s.e || eval51(api), f = api.fmt, ok = e.ok ? api.T("可用（≤ 公差的 1/3）", "acceptable (≤ 1/3 of tolerance)") : api.T("不可用", "not acceptable");
    if (e.sc === "vblock") return [
      [["轴心的位移 ΔY", "Axis shift ΔY"], `${f(e.center * 1000, 1)} µm`],
      [["上母线的定位误差", "Error at top generatrix"], `${f(e.top * 1000, 1)} µm`],
      [["下母线的定位误差（H 的工序基准）", "Error at bottom generatrix (H datum)"], `${f(e.bottom * 1000, 1)} µm`],
      [["H 的公差 / 1/3", "H tolerance / one third"], `${f(e.T * 1000, 0)} / ${f(e.T / 3 * 1000, 1)} µm · ${ok}`]];
    if (e.sc === "mandrel") return [
      [["最大间隙 X_max（= 外圆对孔的最大跳动）", "Max clearance X_max (= largest OD runout to bore)"], `${f(e.xmax * 1000, 1)} µm`],
      [["孔心的最大偏心 X_max/2", "Largest bore-centre offset X_max/2"], `${f(e.ecc * 1000, 1)} µm`],
      [["跳动要求 / 1/3", "Runout tolerance / one third"], `${f(e.T * 1000, 0)} / ${f(e.T / 3 * 1000, 1)} µm · ${ok}`]];
    return [
      [["转角误差 Δθ", "Angular error Δθ"], `${f(e.th * 180 / Math.PI * 3600, 1)}″`],
      [["孔位变动：垂直连线 / 沿连线", "Bore scatter: across / along the pin line"], `${f(e.perp * 1000, 1)} / ${f(e.along * 1000, 1)} µm`],
      [["占用的位置度公差带直径", "Position zone used (diameter)"], `${f(e.zone * 1000, 1)} µm`],
      [["位置度要求 / 1/3", "Tolerance / one third"], `${f(e.T * 1000, 0)} / ${f(e.T / 3 * 1000, 1)} µm · ${ok}`]];
  },
  draw(api, s) {
    const e = s.e || eval51(api), { w, h } = api, css = api.css, p = api.p;
    if (e.sc === "vblock") {
      const cx = w * 0.32, apex = h * 0.85, half = p.alpha * Math.PI / 360;
      const R = Math.min(w, h) * 0.22, ry = (r) => apex - r / Math.sin(half);
      api.line(cx - Math.tan(half) * h * 0.7, apex - h * 0.7, cx, apex, css("--ink"), 2);
      api.line(cx, apex, cx + Math.tan(half) * h * 0.7, apex - h * 0.7, css("--ink"), 2);
      const m = 400;                                  // 直径的变化放大 400 倍画出
      for (let i = 0; i < 40; i++) {                 // 一批工件：直径在公差内变化
        const d = R - m * p.td * rnd51(i) / 2;   // 半径的变化是直径变化的一半
        const yc = ry(d);
        api.circle(cx - 24, yc, 2.5, css("--accent"));
        api.circle(cx + 24, yc + d, 2.5, css("--red"));
      }
      api.circle(cx, ry(R), R, null, css("--muted"), 1);
      api.label(api.T("轴心（蓝）与下母线（红）在一批工件上的位置", "axis (blue) and bottom line (red) over a batch"), cx, h * 0.08, css("--muted"), 12, "center");
    } else if (e.sc === "mandrel") {
      const cx = w * 0.32, cy = h * 0.5, sc = Math.min(w, h) * 0.35 / Math.max(e.xmax, 0.01);
      api.circle(cx, cy, Math.max(e.xmax, 0.01) * sc / 2, null, css("--muted"), 1);
      for (let i = 0; i < 300; i++) {
        const r = (p.xmin + p.tdh * rnd51(i) + p.tdp * rnd51(i + 500)) / 2, th = 2 * Math.PI * rnd51(i + 1000);
        api.circle(cx + r * sc * Math.cos(th), cy + r * sc * Math.sin(th), 1.5, css("--accent"));
      }
      api.label(api.T("孔心相对心轴中心的位置（放大）", "bore centre relative to mandrel (magnified)"), cx, h * 0.08, css("--muted"), 12, "center");
    } else {
      const x0 = w * 0.1, x1 = w * 0.1 + (w * 0.5) * p.L / 300, y = h * 0.5;
      api.rect(x0 - 20, y - 50, x1 - x0 + 120, 100, null, css("--ink"), 4);
      api.circle(x0, y, 8, css("--accent"));
      const ctx = api.ctx, rp = 9, fl = 4;   // 削边销：圆柱两侧沿连线方向削去，只留垂直连线方向的两段圆弧
      ctx.save(); ctx.beginPath(); ctx.rect(x1 - fl, y - rp - 1, 2 * fl, 2 * rp + 2); ctx.clip();
      api.circle(x1, y, rp, css("--amber")); ctx.restore();
      const xb = x0 + (w * 0.5) * 80 / 300;
      api.circle(xb, y, 6, null, css("--red"), 2);   // 被镗孔在两销连线上
      api.label(api.T(`L = ${p.L} mm`, `L = ${p.L} mm`), (x0 + x1) / 2, y + 70, css("--ink"), 12, "center");
    }
    // 右侧：误差与 1/3 公差的比较条
    const bx = w * 0.62, bw = w * 0.33, by = h * 0.4;
    const frac = Math.min(1, e.err / e.T);
    api.rect(bx, by, bw, 24, null, css("--muted"), 3);
    api.rect(bx, by, bw * frac, 24, e.ok ? css("--green") : css("--red"), null, 3);
    api.line(bx + bw / 3, by - 6, bx + bw / 3, by + 30, css("--red"), 2);
    api.label(api.T("定位误差 / 公差", "locating error / tolerance"), bx, by - 12, css("--ink"), 12);
    api.label(api.T("1/3", "1/3"), bx + bw / 3, by + 44, css("--red"), 12, "center");
  },
});
