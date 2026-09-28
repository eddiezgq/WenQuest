// Chapter 1 deck v2: every lesson = concept slide → Manim animation (embedded MP4) → virtual lab.
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const NAVY = "1E2761", ICE = "EEF3FA", AMBER = "F2B705", INK = "1F2D3A", MUTED = "5B6B75", WHITE = "FFFFFF", NIGHT = "0F1419";
const CN = "Microsoft YaHei";
const VID = "anim/media/videos/ch1/1080p30";
const MEDIA = "fig/media";
const LAB = "https://claude.ai/artifact/Nfs4nPpLHhp3S1mGAXUQKp";
const OUT = "out/大学物理（上）课程资料/第1章 质点运动学/第一章课件.pptx";
const b64 = (f) => "data:image/png;base64," + fs.readFileSync(f).toString("base64");

const lessons = [
  {
    no: "1.1", name: "参考系、坐标系与质点", video: "RefFrame", lab: "1-1",
    concept: { title: "参考系：运动是相对的",
      points: ["描述运动必须先选定参考系；同一运动在不同参考系中看来不同", "在参考系上建立坐标系：直角坐标系、自然坐标系", "质点：形状和大小可以忽略时，把物体看成有质量的点", "质点是理想模型：研究地球公转可以，研究自转不行"],
      formula: "描述运动 = 参考系 + 坐标系 + 研究对象（质点）",
      notes: "先问学生：坐在高铁上看窗外，是树在动还是车在动？引出参考系。" },
    vq: "车厢里的人和地面上的人，看到的小球轨迹为什么不同？",
    vnotes: "播放 30 秒动画。暂停在两条轨迹并排的画面，请学生描述各自看到的运动。",
    tasks: ["找到一个观察者，看到小球竖直下落", "找到一个观察者，看到小球“向后”抛出", "地面上看，落地点在松手点前方多远？"],
    lnotes: "课堂上投屏演示：先站在地面看，再切到车厢里看，最后选反向行驶的车。课后学生自己完成三个任务。",
  },
  {
    no: "1.2", name: "位矢、位移、速度、加速度", video: "Derivative", lab: "1-2",
    concept: { title: "速度与加速度：对位矢求导",
      points: ["位矢 r(t) 完整描述质点的位置", "位移 Δr 是矢量，路程 Δs 是标量，一般 |Δr| ≠ Δs", "速度沿轨迹切线方向，速率是 ds/dt", "已知加速度求运动方程：积分 + 初始条件"],
      formula: "v = dr/dt        a = dv/dt = d²r/dt²",
      notes: "重点讲清 |dr| = ds 但 |Δr| ≠ Δs；速率不是 d|r|/dt。" },
    vq: "Δt 越来越小时，弦 Δr 怎样变成切线方向的速度？",
    vnotes: "动画中数字 |Δr| 与 Δs 会逐渐接近，停在 Δt = 0.04 s 的画面，让学生读两个数。",
    tasks: ["把 Δt 调小，直到 |Δr| 与 Δs 相差不到 1%", "例1-1 中 t = 1 s 时，验证 v = 2i − 4j", "匀速圆周：d|r|/dt = 0，但速率不为零，为什么？"],
    lnotes: "可以让学生在“自己写一个”里输入自己的运动方程，观察速度与加速度的方向。",
  },
  {
    no: "1.3", name: "抛体运动", video: "Projectile", lab: "1-3",
    concept: { title: "抛体运动",
      points: ["只受重力：a = −g j（忽略空气阻力）", "水平方向匀速，竖直方向匀加速", "轨迹是抛物线", "45° 射程最大；互余角射程相同"],
      formula: "x = v₀cosθ·t    y = v₀sinθ·t − ½gt²    R = v₀²sin2θ/g", image: "fig/抛体运动轨迹.png", ratio: 4 / 7,
      notes: "先让学生猜哪个角度射程最大，再看动画和虚拟实验验证。" },
    vq: "把抛体运动投影到两个坐标轴上，你看到了哪两种运动？",
    vnotes: "动画前半段看“影子”，后半段比较五个角度。放完后让学生解释 30° 与 60° 为什么落在同一点。",
    tasks: ["命中靶子（落点在靶心 ±1.5 m 以内）", "找出射程最大的抛射角（h₀ = 0，无阻力）", "打开空气阻力：最佳角度还是 45° 吗？"],
    lnotes: "课堂竞赛：每组三次机会命中随机靶子。再到月球上试一次，比较射程。",
  },
  {
    no: "1.4", name: "圆周运动", video: "Circular", lab: "1-4",
    concept: { title: "圆周运动：两个加速度分量",
      points: ["切向加速度改变速率的大小", "法向加速度指向圆心，改变速度的方向", "匀速圆周运动：aₜ = 0，aₙ ≠ 0", "角量与线量：v = Rω，aₜ = Rα，aₙ = Rω²"],
      formula: "aₜ = dv/dt        aₙ = v²/R", image: "fig/圆周运动加速度.png", ratio: 1,
      notes: "用汽车转弯的例子说明法向加速度；提醒一般曲线运动把 R 换成曲率半径。" },
    vq: "速率不变，为什么还有加速度？Δv 最后指向哪里？",
    vnotes: "动画把 v₁、v₂ 平移到同一起点，Δv 逐渐指向圆心。暂停提问：Δv 的方向说明了什么？",
    tasks: ["匀速圆周：让 aₙ 达到 8 m/s²", "匀加速圆周：找到 a 与 v 夹角小于 60° 的时刻", "例1-3：读出 t = 2 s 时的 aₜ 和 aₙ"],
    lnotes: "例1-3 的答案 aₜ = 4.8 m/s²，aₙ ≈ 230 m/s² 可以直接在实验里读出，与板书推导对照。",
  },
  {
    no: "1.5", name: "相对运动", video: "Relative", lab: "1-5",
    concept: { title: "相对运动：伽利略速度变换",
      points: ["同一质点在两个相对平动的参考系中速度不同", "A 相对 C 的速度 = A 相对 B + B 相对 C", "速度是矢量，按平行四边形（三角形）法则相加", "只适用于低速情况（远小于光速）"],
      formula: "v_AC = v_AB + v_BC",
      notes: "雨天坐车：雨滴竖直下落，车里的人看到雨斜着向后落。" },
    vq: "船头垂直河岸，船为什么会被冲到下游？想正对岸靠岸该怎么办？",
    vnotes: "先放前半段，暂停让学生画速度三角形，再放后半段验证。",
    tasks: ["用最短时间渡河", "正对岸靠岸：偏离不超过 2 m", "水速大于船速时，能正对岸靠岸吗？"],
    lnotes: "第三个任务是开放问题：学生会发现做不到，引导他们找航程最短的船头方向。",
  },
];

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "第1章 质点运动学";

// title
let s = pres.addSlide();
s.background = { color: NAVY };
s.addText("第 1 章", { x: 0.8, y: 1.6, w: 6, h: 0.6, fontFace: CN, fontSize: 20, color: AMBER, bold: true, isTextBox: true, margin: 0 });
s.addText("质点运动学", { x: 0.8, y: 2.2, w: 11.5, h: 1.3, fontFace: CN, fontSize: 44, color: WHITE, bold: true, isTextBox: true, margin: 0 });
s.addText("用矢量和微积分描述运动", { x: 0.8, y: 3.6, w: 11.5, h: 0.6, fontFace: CN, fontSize: 18, color: "CADCFC", isTextBox: true, margin: 0 });
s.addText("每节课：概念 → 动画 → 虚拟实验", { x: 0.8, y: 4.4, w: 11.5, h: 0.5, fontFace: CN, fontSize: 16, color: AMBER, isTextBox: true, margin: 0 });
s.addText("大学物理A（上）  ·  2026 秋", { x: 0.8, y: 6.4, w: 8, h: 0.4, fontFace: CN, fontSize: 12, color: "9FB3D1", isTextBox: true, margin: 0 });
s.addNotes("开场问题：导航软件是怎样知道你的速度和方向的？引出位置矢量。");

// outline
s = pres.addSlide();
s.background = { color: WHITE };
s.addText("本章内容", { x: 0.7, y: 0.5, w: 8, h: 0.8, fontFace: CN, fontSize: 30, color: INK, bold: true, isTextBox: true, margin: 0 });
lessons.forEach((l, i) => {
  const y = 1.6 + i * 1.05;
  s.addShape(pres.shapes.OVAL, { x: 0.8, y, w: 0.7, h: 0.7, fill: { color: NAVY } });
  s.addText(l.no, { x: 0.8, y, w: 0.7, h: 0.7, fontFace: CN, fontSize: 14, bold: true, color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  s.addText(l.name, { x: 1.8, y: y + 0.12, w: 6.5, h: 0.45, fontFace: CN, fontSize: 20, bold: true, color: INK, isTextBox: true, margin: 0 });
  s.addText("概念 · 动画 · 虚拟实验", { x: 8.6, y: y + 0.12, w: 4, h: 0.45, fontFace: CN, fontSize: 14, color: MUTED, isTextBox: true, margin: 0 });
});
s.addNotes("每节课都有一段 30–40 秒的动画和一个虚拟实验。动画课上播放，实验课上演示、课后学生完成任务。");

lessons.forEach((l) => {
  // concept
  const c = l.concept;
  let sl = pres.addSlide();
  sl.background = { color: WHITE };
  sl.addText(l.no, { x: 0.7, y: 0.35, w: 1, h: 0.4, fontFace: CN, fontSize: 14, color: AMBER, bold: true, isTextBox: true, margin: 0 });
  sl.addText(c.title, { x: 0.7, y: 0.7, w: 12, h: 0.8, fontFace: CN, fontSize: 28, color: INK, bold: true, isTextBox: true, margin: 0 });
  const textW = c.image ? 6.2 : 11.9;
  const items = c.points.map((p, i) => ({ text: p, options: { bullet: true, breakLine: i < c.points.length - 1, paraSpaceAfter: 10 } }));
  sl.addText(items, { x: 0.7, y: 1.7, w: textW, h: 3.2, fontFace: CN, fontSize: 17, color: INK, valign: "top", isTextBox: true, margin: 0 });
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 5.1, w: textW, h: 1.5, fill: { color: ICE }, line: { color: ICE }, rectRadius: 0.12 });
  sl.addText(c.formula, { x: 1.05, y: 5.2, w: textW - 0.5, h: 1.3, fontFace: "Cambria Math", fontSize: 20, color: NAVY, bold: true, valign: "middle", isTextBox: true, margin: 0 });
  if (c.image) sl.addImage({ path: c.image, x: 7.3, y: 1.5, w: 5.4, h: 5.4 * c.ratio });
  sl.addNotes(c.notes);

  // animation
  sl = pres.addSlide();
  sl.background = { color: NIGHT };
  sl.addText(`${l.no}  动画`, { x: 0.6, y: 0.3, w: 4, h: 0.4, fontFace: CN, fontSize: 14, color: AMBER, bold: true, isTextBox: true, margin: 0 });
  sl.addText(l.vq, { x: 0.6, y: 0.7, w: 12.1, h: 0.6, fontFace: CN, fontSize: 20, color: WHITE, bold: true, isTextBox: true, margin: 0 });
  const vw = 9.6, vh = vw * 9 / 16, vx = (13.333 - vw) / 2, vy = 1.5;
  sl.addMedia({ type: "video", path: path.join(VID, l.video + ".mp4"), x: vx, y: vy, w: vw, h: vh, cover: b64(path.join(MEDIA, "poster_" + l.video + ".png")) });
  sl.addText("点击画面播放 · 约 30–40 秒 · 无配音，带中文字幕", { x: vx, y: vy + vh + 0.1, w: vw, h: 0.35, fontFace: CN, fontSize: 12, color: "9FB3D1", align: "center", isTextBox: true, margin: 0 });
  sl.addNotes(l.vnotes);

  // virtual lab
  sl = pres.addSlide();
  sl.background = { color: ICE };
  sl.addText(`${l.no}  虚拟实验`, { x: 0.7, y: 0.35, w: 4, h: 0.4, fontFace: CN, fontSize: 14, color: AMBER, bold: true, isTextBox: true, margin: 0 });
  sl.addText("动手试一试：" + l.name, { x: 0.7, y: 0.7, w: 12, h: 0.7, fontFace: CN, fontSize: 26, color: INK, bold: true, isTextBox: true, margin: 0 });
  const iw = 7.4, ih = iw * 10 / 16;
  sl.addImage({ path: path.join(MEDIA, "lab_" + l.lab + ".png"), x: 0.7, y: 1.6, w: iw, h: ih, hyperlink: { url: `${LAB}#lab-${l.lab}`, tooltip: "打开虚拟实验" } });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 1.6, w: iw, h: ih, fill: { type: "none" }, line: { color: "C9D3DD", width: 1 } });
  sl.addText("任务", { x: 8.5, y: 1.6, w: 4.2, h: 0.4, fontFace: CN, fontSize: 16, color: MUTED, bold: true, isTextBox: true, margin: 0 });
  const tk = l.tasks.map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: i < l.tasks.length - 1, paraSpaceAfter: 12 } }));
  sl.addText(tk, { x: 8.5, y: 2.1, w: 4.2, h: 3.0, fontFace: CN, fontSize: 16, color: INK, valign: "top", isTextBox: true, margin: 0 });
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.5, y: 5.35, w: 4.2, h: 0.7, fill: { color: NAVY }, line: { color: NAVY }, rectRadius: 0.1,
    hyperlink: { url: `${LAB}#lab-${l.lab}`, tooltip: "打开虚拟实验" } });
  sl.addText([{ text: "打开虚拟实验 ▶", options: { hyperlink: { url: `${LAB}#lab-${l.lab}` } } }],
    { x: 8.5, y: 5.35, w: 4.2, h: 0.7, fontFace: CN, fontSize: 17, bold: true, color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  sl.addText("任务完成情况会自动打勾", { x: 8.5, y: 6.15, w: 4.2, h: 0.35, fontFace: CN, fontSize: 12, color: MUTED, align: "center", isTextBox: true, margin: 0 });
  sl.addNotes(l.lnotes);
});

// worked example + summary
s = pres.addSlide();
s.background = { color: ICE };
s.addText("例题", { x: 0.7, y: 0.45, w: 3, h: 0.7, fontFace: CN, fontSize: 16, color: AMBER, bold: true, isTextBox: true, margin: 0 });
s.addText("质点沿半径 R = 0.10 m 的圆周运动，θ = 2 + 4t³（rad）。求 t = 2 s 时的切向加速度和法向加速度。", { x: 0.7, y: 1.0, w: 12, h: 1.4, fontFace: CN, fontSize: 20, color: INK, bold: true, valign: "top", isTextBox: true, margin: 0 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 2.6, w: 12, h: 4.1, fill: { color: WHITE }, line: { color: "D5DEE8" }, rectRadius: 0.12 });
const steps = ["ω = dθ/dt = 12t²，α = dω/dt = 24t", "t = 2 s：ω = 48 rad/s，α = 48 rad/s²", "aₜ = Rα = 0.10 × 48 = 4.8 m/s²", "aₙ = Rω² = 0.10 × 48² ≈ 230 m/s²（可在虚拟实验 1.4 中验证）"];
s.addText(steps.map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: i < steps.length - 1, paraSpaceAfter: 12 } })),
  { x: 1.0, y: 2.85, w: 11.4, h: 3.7, fontFace: CN, fontSize: 17, color: INK, valign: "top", isTextBox: true, margin: 0 });
s.addNotes("先让学生独立做 3 分钟，再逐步展开解答；最后打开虚拟实验 1.4 的“例1-3”模式对照答案。");

s = pres.addSlide();
s.background = { color: NAVY };
s.addText("本章小结", { x: 0.8, y: 0.6, w: 8, h: 0.8, fontFace: CN, fontSize: 30, color: WHITE, bold: true, isTextBox: true, margin: 0 });
const sum = ["求导：r → v → a；积分：a → v → r（需要初始条件）", "|Δr| ≠ Δs，速率 = ds/dt", "抛体：R = v₀² sin2θ / g，45° 最远", "圆周：aₜ 改变快慢，aₙ = v²/R 改变方向", "相对运动：v_AC = v_AB + v_BC"];
s.addText(sum.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < sum.length - 1, paraSpaceAfter: 14 } })),
  { x: 0.8, y: 1.7, w: 11.8, h: 4.2, fontFace: CN, fontSize: 19, color: "E6EDF7", valign: "top", isTextBox: true, margin: 0 });
s.addText("课后作业：习题1 第1–6题 ＋ 完成 5 个虚拟实验的全部任务", { x: 0.8, y: 6.3, w: 11.8, h: 0.5, fontFace: CN, fontSize: 15, color: AMBER, isTextBox: true, margin: 0 });
s.addNotes("回顾本章知识结构，提醒作业截止时间，预告下一章。");

pres.writeFile({ fileName: OUT }).then(() => console.log("deck written", OUT));
