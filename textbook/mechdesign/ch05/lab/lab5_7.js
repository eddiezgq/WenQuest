// 实验 5.7 机械臂小臂的轻量化选材（配 5.7 节）。“外径固定”模式与程序 5.7.1 的算法和材料数据相同：
// 薄壁圆管当悬臂梁（I = πD³t/8），末端力 + 管子自重，挠度等于允许值时求壁厚，再取不小于最小壁厚，算质量。
// 材料：E（GPa）、密度（g/cm³）取数字工厂材料库（钢、铝、7075）与本书表（镁、钛、玻纤）；碳纤维层合板的 E 由程序 5.5.1 的经典层合理论算出；
// 最小壁厚是本书设定。小臂长 392 mm、腕部三个连杆共 2.627 kg 取自零件库 UR5e 模型（MJCF）。
// “形状固定”模式（t = 0.05D、不计自重）和自行车场景（简支梁、不计自重）是实验另加的，程序里没有。
const MAT5_7 = [
  ["steel", ["45 钢", "1045 steel"], 210, 7.85, 1.0], ["al6061", ["6061-T6 铝合金", "6061-T6 Al"], 68.9, 2.7, 1.5],
  ["al7075", ["7075-T6 铝合金", "7075-T6 Al"], 71.7, 2.81, 1.5], ["mg", ["AZ31B 镁合金", "AZ31B Mg"], 45, 1.77, 2.0],
  ["ti", ["TC4 钛合金", "Ti-6Al-4V"], 114, 4.43, 1.0], ["cfrp", ["碳纤维层合板", "CFRP laminate"], 52.76, 1.56, 1.0],
  ["gfrp", ["玻璃纤维层合板", "GFRP laminate"], 18, 1.9, 1.0]];
const SCN5_7 = {
  robot: { L: 0.392, wrist: 2.627, c: 1 / 3, selfw: true },          // 悬臂：末端载荷 + 自重
  life: { L: 0.60, wrist: 0, c: 1 / 48, selfw: false },              // 自行车下管：两端支承、中点受力（示意）
};
function size5_7(p, scene) {
  const S = SCN5_7[scene], g = 9.81, L = S.L, F = scene === "robot" ? (S.wrist + p.pay) * g : p.pay * g;
  const D = p.D / 1000, d = p.delta / 1000, minw = Math.round(p.tmin) === 1, shape = Math.round(p.mode) === 1;
  return MAT5_7.map(([id, name, E0, rho0, tmin]) => {
    const E = E0 * 1e9, rho = rho0 * 1000;
    let Dm = D, t;
    if (!shape) {                                                     // 外径固定、壁厚自由
      // δ = cFL³/(EI) + ρπDt·g·L⁴/(8EI)（悬臂自重），I = πD³t/8 → t = cFL³ / [πD/8 · (δD²E − ρgL⁴)]
      t = (S.c * F * L ** 3) / (Math.PI * D / 8 * (d * D * D * E - (S.selfw ? rho * g * L ** 4 : 0)));
    } else {                                                          // 形状固定（t = 0.05D）、外径自由，不计自重
      const Ireq = S.c * F * L ** 3 / (E * d);
      Dm = Math.pow(8 * Ireq / (Math.PI * 0.05), 0.25);
      t = 0.05 * Dm;
    }
    const treq = t;
    if (minw && t < tmin / 1000) t = tmin / 1000;
    const mass = rho * Math.PI * Dm * t * L;
    return { id, name, E0, rho0, t: t * 1000, treq: treq * 1000, D: Dm * 1000, mass, bad: !(t > 0) || t > Dm / 4 };
  }).sort((a, b) => a.mass - b.mass);
}
WQ.lab({
  title: ["实验 5.7 机械臂小臂的轻量化选材", "Lab 5.7 Lightweight material selection for a robot forearm"],
  goal: ["给定刚度要求和尺寸约束，按性能指数比较几种材料做小臂的质量；看最小壁厚这类工艺约束怎样改变排序，外径能不能变又怎样改变排序。",
         "For a stiffness requirement and size limits, compare the forearm mass in several materials by performance index; see how a manufacturing limit such as minimum wall changes the ranking, and how it changes again when the diameter may vary."],
  scenes: [
    { id: "robot", robot: true, name: ["协作机器人小臂", "Cobot forearm"],
      problem: { title: ["工程问题：协作机器人的小臂用什么材料", "Engineering problem: what to make a cobot forearm from"],
                 text: ["小臂是一根管子，外径受肘、腕关节的尺寸限制。末端挂着腕部和负载，弯曲变形要小（末端精度）。钢、铝、镁、钛、碳纤维，哪种最轻？",
                        "The forearm is a tube whose diameter is set by the elbow and wrist joints. The wrist and payload hang on its end and it must bend very little (accuracy). Steel, aluminum, magnesium, titanium, carbon fiber: which is lightest?"] } },
    { id: "life", name: ["自行车车架的下管", "Bicycle down tube"],
      problem: { title: ["生活中的例子：自行车车架", "Everyday example: a bicycle frame"],
                 text: ["车架下管要有足够的刚度，蹬车时才不“软”。钢车架的管子细，铝车架的管子粗，碳纤维车架形状更自由——为什么？",
                        "A down tube must be stiff so the bike does not feel soft when pedalling. Steel frames have slim tubes, aluminum frames fat ones, carbon frames free shapes — why?"] } },
  ],
  params: [
    { id: "delta", name: ["允许挠度", "Allowed deflection"], min: 0.05, max: 2, step: 0.05, value: 0.1, unit: "mm", digits: 2 },
    { id: "D", name: ["外径（形状固定时不用）", "Outer diameter (unused when shape is fixed)"], min: 30, max: 120, step: 1, value: 75, unit: "mm", digits: 0 },
    { id: "pay", name: ["负载（自行车：中点力 / 9.81）", "Payload (bicycle: midspan force / 9.81)"], min: 0, max: 120, step: 1, value: 4, unit: "kg", digits: 0 },
    { id: "tmin", name: ["最小壁厚约束（1 = 考虑，0 = 不考虑）", "Minimum wall (1 = on, 0 = off)"], min: 0, max: 1, step: 1, value: 1, unit: "", digits: 0 },
    { id: "mode", name: ["0 = 外径固定、壁厚自由；1 = 形状固定、外径自由", "0 = fixed OD, free wall; 1 = fixed shape, free OD"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "var(--accent)", name: ["各材料的质量（最轻的排在最上）", "mass of each material (lightest on top)"] }],
  tasks: [
    { id: "base", robot: true, text: ["默认参数（外径 75 mm，挠度 0.1 mm，负载 4 kg，考虑最小壁厚）：哪种材料最轻？钢为什么比铝合金重？", "Defaults (OD 75 mm, 0.1 mm, 4 kg, minimum wall on): which material is lightest? Why is steel heavier than aluminum?"],
      demo: { scene: "robot", set: { delta: 0.1, D: 75, pay: 4, tmin: 1, mode: 0 }, press: ["start"], wait: 1 } },
    { id: "nomin", robot: true, text: ["去掉最小壁厚约束：钢、铝、镁、钛的质量差不多，为什么？（看 E/ρ）", "Switch the minimum wall off: steel, aluminum, magnesium and titanium weigh about the same. Why? (Look at E/ρ.)"],
      demo: { scene: "robot", set: { delta: 0.1, D: 75, pay: 4, tmin: 0, mode: 0 }, press: ["start"], wait: 1 } },
    { id: "shape", robot: true, text: ["改为“形状固定、外径自由”：排序怎样变？这时的性能指数是什么？", "Switch to “fixed shape, free OD”: how does the ranking change? What is the index now?"],
      demo: { scene: "robot", set: { delta: 0.1, D: 75, pay: 4, tmin: 0, mode: 1 }, press: ["start"], wait: 1 } },
    { id: "life", text: ["自行车下管：外径取 35 mm 和 50 mm 各算一次，比较钢和铝合金。", "Bicycle down tube: compute with 35 mm and 50 mm OD and compare steel and aluminum."],
      demo: { scene: "life", set: { delta: 1, D: 50, pay: 100, tmin: 1, mode: 0 }, press: ["start"], wait: 1 } },
  ],
  think: ["“外径固定”模式与程序 5.7.1 的算法相同。实际的协作机器人小臂多用铝合金，很少用碳纤维——除了质量，还有哪些因素（连接、成本、导热、碰撞）？",
          "The fixed-OD mode uses the method of Program 5.7.1. Real cobot forearms are mostly aluminum, rarely carbon fiber — besides mass, what else matters (joints, cost, heat, impact)?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    const p = api.p, minw = Math.round(p.tmin) === 1, shape = Math.round(p.mode) === 1;
    s.r = size5_7(p, api.scene);
    if (api.scene === "robot" && !shape && minw) api.done("base");
    if (api.scene === "robot" && !shape && !minw) api.done("nomin");
    if (api.scene === "robot" && shape) api.done("shape");
    if (api.scene === "life") api.done("life");
    api.stop();
  },
  readouts(api, s) {
    const f = api.fmt, r = s.r;
    if (!r) return [[["状态", "Status"], api.T("按“计算”开始", "press Compute")]];
    const b = r[0], st = r.find((x) => x.id === "steel"), al = r.find((x) => x.id === "al6061");
    return [
      [["最轻的材料", "Lightest"], api.T(b.name[0], b.name[1]) + "，" + f(b.mass, 3) + " kg"],
      [["最轻者的外径、壁厚", "Its OD and wall"], f(b.D, 1) + " mm，" + f(b.t, 2) + " mm"],
      [["钢：所需壁厚 / 实际壁厚", "Steel: wall needed / used"], f(st.treq, 2) + " / " + f(st.t, 2) + " mm"],
      [["铝合金 6061：质量", "6061 Al: mass"], f(al.mass, 3) + " kg"],
      [["钢与 6061 的质量比", "Steel / 6061 mass"], f(st.mass / al.mass, 2)],
    ];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, r = s.r;
    const x0 = 150, y0 = 24, W = w - x0 - 70, rowH = Math.min(38, (h - 50) / MAT5_7.length);
    if (!r) { api.label(api.T("按“计算”比较各材料的质量", "Press Compute to compare the masses"), w / 2, h / 2, css("--muted"), 14, "center"); return; }
    const top = Math.max(...r.map((x) => x.mass));
    r.forEach((m, i) => {
      const y = y0 + i * rowH, bw = m.mass / top * W;
      api.label(api.T(m.name[0], m.name[1]), x0 - 8, y + rowH / 2, css("--ink"), 12, "right");
      api.rect(x0, y + 5, bw, rowH - 10, i === 0 ? css("--accent") : css("--muted"));
      api.label(api.fmt(m.mass, 3) + " kg  t " + api.fmt(m.t, 2) + "  D " + api.fmt(m.D, 0) + " mm" + (m.bad ? api.T("（壁太厚，薄壁公式不适用）", " (wall too thick for the thin-wall formula)") : ""), x0 + bw + 6, y + rowH / 2, css("--ink"), 11);
    });
    api.label(api.T("E/ρ 越大，外径固定时越轻；形状固定时看 E½/ρ", "Larger E/ρ is lighter at fixed OD; at fixed shape look at E½/ρ"), x0, h - 12, css("--muted"), 12);
  },
});
