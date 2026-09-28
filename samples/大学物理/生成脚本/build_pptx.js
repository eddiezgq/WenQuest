// Three chapter decks for the sample course. Navy dominant, ice-blue surfaces, amber accent.
const pptxgen = require("pptxgenjs");
const path = require("path");

const NAVY = "1E2761", ICE = "EEF3FA", AMBER = "F2B705", INK = "1F2D3A", MUTED = "5B6B75", WHITE = "FFFFFF";
const CN = "Microsoft YaHei";
const ROOT = "out/大学物理（上）课程资料";

function deck(file, ch) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
  pres.title = ch.title;

  // title slide
  let s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText(ch.no, { x: 0.8, y: 1.6, w: 6, h: 0.6, fontFace: CN, fontSize: 20, color: AMBER, bold: true, isTextBox: true, margin: 0 });
  s.addText(ch.title, { x: 0.8, y: 2.2, w: 11.5, h: 1.3, fontFace: CN, fontSize: 44, color: WHITE, bold: true, isTextBox: true, margin: 0 });
  s.addText(ch.subtitle, { x: 0.8, y: 3.6, w: 11.5, h: 0.6, fontFace: CN, fontSize: 18, color: "CADCFC", isTextBox: true, margin: 0 });
  s.addText("大学物理A（上）  ·  2026 秋", { x: 0.8, y: 6.4, w: 8, h: 0.4, fontFace: CN, fontSize: 12, color: "9FB3D1", isTextBox: true, margin: 0 });
  s.addNotes(ch.notesTitle);

  // outline slide: numbered circles
  s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText("本章内容", { x: 0.7, y: 0.5, w: 8, h: 0.8, fontFace: CN, fontSize: 30, color: INK, bold: true, isTextBox: true, margin: 0 });
  ch.outline.forEach((item, i) => {
    const y = 1.6 + i * 1.1;
    s.addShape(pres.shapes.OVAL, { x: 0.8, y, w: 0.7, h: 0.7, fill: { color: i === 0 ? AMBER : NAVY } });
    s.addText(String(i + 1), { x: 0.8, y, w: 0.7, h: 0.7, fontFace: CN, fontSize: 18, bold: true, color: i === 0 ? INK : WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
    s.addText(item[0], { x: 1.8, y: y - 0.05, w: 10, h: 0.45, fontFace: CN, fontSize: 20, bold: true, color: INK, isTextBox: true, margin: 0 });
    s.addText(item[1], { x: 1.8, y: y + 0.4, w: 10.5, h: 0.4, fontFace: CN, fontSize: 14, color: MUTED, isTextBox: true, margin: 0 });
  });
  s.addNotes("先给学生看本章的地图，每讲完一节回到这一页标记进度。");

  // concept slides
  ch.concepts.forEach((c) => {
    const sl = pres.addSlide();
    sl.background = { color: WHITE };
    sl.addText(c.title, { x: 0.7, y: 0.45, w: 12, h: 0.8, fontFace: CN, fontSize: 28, color: INK, bold: true, isTextBox: true, margin: 0 });
    const textW = c.image ? 6.2 : 11.9;
    const items = c.points.map((p, i) => ({ text: p, options: { bullet: true, breakLine: i < c.points.length - 1, paraSpaceAfter: 10 } }));
    sl.addText(items, { x: 0.7, y: 1.5, w: textW, h: 3.3, fontFace: CN, fontSize: 17, color: INK, valign: "top", isTextBox: true, margin: 0 });
    // formula card
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 5.1, w: textW, h: 1.5, fill: { color: ICE }, line: { color: ICE }, rectRadius: 0.12 });
    sl.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 5.1, w: 0.12, h: 1.5, fill: { color: AMBER }, line: { color: AMBER } });
    sl.addText(c.formula, { x: 1.05, y: 5.2, w: textW - 0.5, h: 1.3, fontFace: "Cambria Math", fontSize: 20, color: NAVY, bold: true, valign: "middle", isTextBox: true, margin: 0 });
    if (c.image) sl.addImage({ path: c.image, x: 7.3, y: 1.4, w: 5.4, h: 5.4 * c.ratio });
    sl.addNotes(c.notes);
  });

  // worked example
  s = pres.addSlide();
  s.background = { color: ICE };
  s.addText("例题", { x: 0.7, y: 0.45, w: 3, h: 0.7, fontFace: CN, fontSize: 16, color: AMBER, bold: true, isTextBox: true, margin: 0 });
  s.addText(ch.example.q, { x: 0.7, y: 1.0, w: 12, h: 1.4, fontFace: CN, fontSize: 20, color: INK, bold: true, valign: "top", isTextBox: true, margin: 0 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 2.6, w: 12, h: 4.1, fill: { color: WHITE }, line: { color: "D5DEE8" }, rectRadius: 0.12 });
  const steps = ch.example.steps.map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: i < ch.example.steps.length - 1, paraSpaceAfter: 12 } }));
  s.addText(steps, { x: 1.0, y: 2.85, w: 11.4, h: 3.7, fontFace: CN, fontSize: 17, color: INK, valign: "top", isTextBox: true, margin: 0 });
  s.addNotes("先让学生独立做 3 分钟，再逐步展开解答。强调受力分析或守恒条件的判断。");

  // summary
  s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("本章小结", { x: 0.8, y: 0.6, w: 8, h: 0.8, fontFace: CN, fontSize: 30, color: WHITE, bold: true, isTextBox: true, margin: 0 });
  const sum = ch.summary.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < ch.summary.length - 1, paraSpaceAfter: 14 } }));
  s.addText(sum, { x: 0.8, y: 1.7, w: 11.8, h: 4.2, fontFace: CN, fontSize: 19, color: "E6EDF7", valign: "top", isTextBox: true, margin: 0 });
  s.addText("课后作业：" + ch.homework, { x: 0.8, y: 6.3, w: 11.8, h: 0.5, fontFace: CN, fontSize: 15, color: AMBER, isTextBox: true, margin: 0 });
  s.addNotes("回顾本章知识结构，提醒作业截止时间，预告下一章。");

  return pres.writeFile({ fileName: path.join(ROOT, file) });
}

const ch1 = {
  no: "第 1 章", title: "质点运动学", subtitle: "用矢量和微积分描述运动",
  notesTitle: "开场问题：导航软件是怎样知道你的速度和方向的？引出位置矢量。",
  outline: [["参考系、坐标系与质点", "理想模型的思想"], ["位矢、位移、速度、加速度", "求导链：r → v → a"],
            ["抛体运动", "水平匀速 + 竖直匀加速"], ["圆周运动", "切向加速度与法向加速度"], ["相对运动", "伽利略速度变换"]],
  concepts: [
    { title: "速度与加速度：对位矢求导", points: ["位矢 r(t) 完整描述质点的位置", "位移 Δr 是矢量，路程 Δs 是标量，一般 |Δr| ≠ Δs", "速度沿轨迹切线方向，速率是 ds/dt", "已知加速度求运动方程：积分 + 初始条件"],
      formula: "v = dr/dt        a = dv/dt = d²r/dt²", notes: "重点讲清 |dr| = ds 但 |Δr| ≠ Δs；速率不是 d|r|/dt。" },
    { title: "抛体运动", points: ["只受重力：a = −g j（忽略空气阻力）", "水平方向匀速，竖直方向匀加速", "轨迹是抛物线", "45° 射程最大；互余角射程相同"],
      formula: "x = v₀cosθ·t    y = v₀sinθ·t − ½gt²    R = v₀²sin2θ/g", image: "fig/抛体运动轨迹.png", ratio: 4 / 7,
      notes: "先让学生猜哪个角度射程最大，再看图验证；随后打开问渠虚拟实验演示。" },
    { title: "圆周运动：两个加速度分量", points: ["切向加速度改变速率的大小", "法向加速度指向圆心，改变速度的方向", "匀速圆周运动：aₜ = 0，aₙ ≠ 0", "角量与线量：v = Rω，aₜ = Rα，aₙ = Rω²"],
      formula: "aₜ = dv/dt        aₙ = v²/R", image: "fig/圆周运动加速度.png", ratio: 1,
      notes: "用汽车转弯的例子说明法向加速度；提醒一般曲线运动把 R 换成曲率半径。" },
  ],
  example: { q: "质点沿半径 R = 0.10 m 的圆周运动，θ = 2 + 4t³（rad）。求 t = 2 s 时的切向加速度和法向加速度。",
    steps: ["ω = dθ/dt = 12t²，α = dω/dt = 24t", "t = 2 s：ω = 48 rad/s，α = 48 rad/s²", "aₜ = Rα = 0.10 × 48 = 4.8 m/s²", "aₙ = Rω² = 0.10 × 48² ≈ 230 m/s²"] },
  summary: ["求导：r → v → a；积分：a → v → r（需要初始条件）", "|Δr| ≠ Δs，速率 = ds/dt", "抛体：R = v₀² sin2θ / g，45° 最远", "圆周：aₜ 改变快慢，aₙ = v²/R 改变方向", "相对运动：v_AC = v_AB + v_BC"],
  homework: "习题1 第1–6题，第3周周二前在问渠平台提交",
};
const ch2 = {
  no: "第 2 章", title: "牛顿运动定律", subtitle: "力如何改变运动",
  notesTitle: "开场问题：电梯加速上升时，体重秤的读数为什么变大？",
  outline: [["牛顿三定律", "惯性系与适用范围"], ["常见的力", "重力、弹力、摩擦力"], ["隔离法解题五步骤", "斜面与连接体"],
            ["变力问题", "阻力与终极速度"], ["非惯性系", "惯性力 −m a₀"]],
  concepts: [
    { title: "牛顿第二定律与隔离法", points: ["F 是研究对象所受的合力", "只在惯性系中成立", "五步骤：选对象 → 画受力图 → 建坐标 → 列方程 → 求解讨论", "连接体问题补充约束关系（绳长不变）"],
      formula: "F = dp/dt = ma", notes: "完整示范一道题的五个步骤，要求学生之后每题都按这个顺序写。" },
    { title: "斜面问题", points: ["受力：重力 mg、支持力 N、摩擦力 f", "垂直斜面：N = mg cosθ", "沿斜面：mg sinθ − μN = ma", "讨论：tanθ ≤ μ 时静止物体保持静止"],
      formula: "a = g (sinθ − μ cosθ)", image: "fig/斜面受力分析.png", ratio: 2 / 3,
      notes: "常见错误：同时画“下滑力”和重力。让学生互评受力图。" },
    { title: "变力：终极速度", points: ["阻力 f = −kv，方向与速度相反", "牛顿第二定律化为微分方程", "分离变量积分，t = 0 时 v = 0", "t → ∞ 时趋近终极速度"],
      formula: "v = (mg/k)(1 − e^(−kt/m))    v_T = mg/k", notes: "展示虚拟实验中速度曲线趋近 v_T，改变 k 观察时间常量 m/k 的作用。" },
  ],
  example: { q: "阿特伍德机：m₁ > m₂，滑轮和绳的质量及摩擦不计。求加速度和绳中张力。",
    steps: ["隔离 m₁：m₁g − T = m₁a", "隔离 m₂：T − m₂g = m₂a", "a = (m₁ − m₂)g / (m₁ + m₂)", "T = 2m₁m₂g / (m₁ + m₂)；检验 m₁ = m₂ 时 a = 0"] },
  summary: ["F = ma 只在惯性系成立，F 是合力", "隔离法五步骤，受力图不多画不漏画", "静摩擦力由平衡条件或运动方程确定", "变力问题：列微分方程，分离变量积分", "非惯性系：附加惯性力 −m a₀"],
  homework: "第二章作业 第1–5题，第5周周二前提交",
};
const ch3 = {
  no: "第 3 章", title: "动量守恒定律和能量守恒定律", subtitle: "力的时间积累与空间积累",
  notesTitle: "开场问题：鸡蛋掉在海绵上为什么不碎？引出冲量与动量定理。",
  outline: [["冲量与动量定理", "力的时间积累"], ["动量守恒定律", "合外力为零"], ["功与动能定理", "力的空间积累"],
            ["势能与机械能守恒", "保守力"], ["碰撞", "弹性与完全非弹性"]],
  concepts: [
    { title: "动量定理与动量守恒", points: ["冲量是力对时间的积累", "合外力的冲量等于动量的增量", "合外力为零时系统总动量守恒", "某方向合外力为零，该方向动量守恒"],
      formula: "I = ∫F dt = p₂ − p₁        Σmᵢvᵢ = 常矢量", image: "fig/动量守恒-碰撞示意.png", ratio: 3.2 / 6.5,
      notes: "碰撞、爆炸时间极短，内力远大于外力，可近似认为动量守恒。" },
    { title: "动能定理与机械能守恒", points: ["功是力对空间的积累：W = ∫F·dr", "合力的功等于动能的增量", "保守力做功与路径无关，可以定义势能", "外力和非保守内力不做功时，机械能守恒"],
      formula: "W = ½mv₂² − ½mv₁²        E_k + E_p = 常量", notes: "对比三种势能的零点：重力任选、弹性取原长、引力取无穷远。" },
    { title: "碰撞", points: ["所有碰撞：动量守恒", "完全弹性碰撞：动能也守恒", "质量相等的弹性碰撞：交换速度", "完全非弹性碰撞：碰后共速，动能损失最大"],
      formula: "完全非弹性：v = (m₁v₁₀ + m₂v₂₀)/(m₁ + m₂)", notes: "用问渠虚拟实验调节质量比，观察碰后速度，验证公式。" },
  ],
  example: { q: "冲击摆：m = 10 g 的子弹射入 M = 1.99 kg 的木块，木块摆起 h = 5.0 cm。求子弹速度。",
    steps: ["碰撞瞬间：动量守恒 m v₀ = (m + M) V", "摆动过程：机械能守恒 V = √(2gh) ≈ 0.99 m/s", "v₀ = (m + M)V / m ≈ 198 m/s", "碰撞中动能损失约 99.5%，不能全过程用机械能守恒"] },
  summary: ["动量定理：冲量 = 动量增量；守恒条件看合外力", "动能定理：合力的功 = 动能增量", "机械能守恒条件：外力和非保守内力不做功", "多过程问题：分段处理，每段判断守恒量", "碰撞：动量一定守恒，动能不一定"],
  homework: "作业3 第1–5题，第8周周二前提交",
};

(async () => {
  await deck("第1章 质点运动学/第一章课件.pptx", ch1);
  await deck("第2章 牛顿定律/第2章 牛顿运动定律.pptx", ch2);
  await deck("第3章 动量与能量/Ch3 slides.pptx", ch3);
  console.log("decks done");
})();
