// Chapter 1 deck, Chinese–English (中英对照). Each lesson:
// robot problem → concept → animation → virtual lab → back to the problem (5-step model) + everyday example.
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const NAVY = "1E2761", ICE = "EEF3FA", AMBER = "F2B705", INK = "1F2D3A", MUTED = "5B6B75", WHITE = "FFFFFF", NIGHT = "0F1419", PALE = "FFF6DA";
const CN = "Microsoft YaHei", EN = "Calibri";
const VID = "anim/media/videos/ch1/1080p30";
const MEDIA = "fig/media";
const LAB = "https://claude.ai/artifact/Nfs4nPpLHhp3S1mGAXUQKp";
const OUT = "out/大学物理（上）课程资料/第1章 质点运动学/第一章课件.pptx";
const b64 = (f) => "data:image/png;base64," + fs.readFileSync(f).toString("base64");
const T = (o) => Object.assign({ isTextBox: true, margin: 0 }, o);

// bilingual list: each item = [zh, en]
function biList(items, zhSize = 16, enSize = 11, color = INK, enColor = MUTED, numbered = false) {
  const runs = [];
  items.forEach(([zh, en], i) => {
    runs.push({ text: zh, options: { bullet: numbered ? { type: "number" } : true, fontFace: CN, fontSize: zhSize, color, breakLine: true } });
    runs.push({ text: en, options: { fontFace: EN, fontSize: enSize, color: enColor, indentLevel: 0, paraSpaceAfter: 9, breakLine: i < items.length - 1, bullet: false } });
  });
  return runs;
}
function biTitle(s, zh, en, y = 0.62, color = INK, enColor = MUTED) {
  s.addText(zh, T({ x: 0.7, y, w: 12, h: 0.6, fontFace: CN, fontSize: 26, color, bold: true }));
  s.addText(en, T({ x: 0.7, y: y + 0.6, w: 12, h: 0.35, fontFace: EN, fontSize: 14, color: enColor }));
}
function tag(s, text, color = AMBER) { s.addText(text, T({ x: 0.7, y: 0.3, w: 8, h: 0.3, fontFace: CN, fontSize: 12, color, bold: true })); }

const L = [
  {
    no: "1.1", zh: "参考系、坐标系与质点", en: "Reference frames, coordinates and particles", video: "RefFrame", lab: "1-1",
    prob: { zh: "传送带跟踪抓取", en: "Grasping from a moving conveyor",
      text: ["工件在传送带上以 0.50 m/s 运动，机械臂要在运动中抓住它。在哪个参考系里规划抓取最简单？末端对地速度应是多少？",
             "A part rides the belt at 0.50 m/s and the arm must grab it on the move. In which frame is the grasp easiest to plan, and what must the gripper’s ground velocity be?"],
      given: [["传送带速度 u = 0.50 m/s", "belt speed u = 0.50 m/s"], ["末端相对传送带竖直下降 0.25 m/s", "gripper descends at 0.25 m/s relative to the belt"], ["下降距离 0.50 m", "descent 0.50 m"]] },
    concept: { zh: "参考系：运动是相对的", en: "Reference frames: motion is relative",
      pts: [["描述运动必须先选定参考系；同一运动在不同参考系中看来不同", "Choose a frame first; one motion looks different in different frames"],
            ["在参考系上建立坐标系：直角坐标系、自然坐标系", "Set up coordinates: Cartesian or path (natural) coordinates"],
            ["质点：形状和大小可以忽略时，把物体看成有质量的点", "Particle: ignore size and shape when they do not matter"],
            ["速度叠加：v(对地) = v(相对) + v(牵连)", "Velocity addition: v(ground) = v(relative) + v(frame)"]],
      formula: "描述运动 = 参考系 + 坐标系 + 研究对象（质点）\nMotion = frame + coordinates + object (particle)" },
    vq: ["车厢里的人和地面上的人，看到的小球轨迹为什么不同？", "Why do the passenger and the person on the ground see different paths?"],
    tasks: [["传送带参考系：末端竖直落到工件上", "Belt frame: gripper comes straight down"], ["地面参考系：读出末端对地速度和方向", "Ground frame: read the gripper’s ground velocity"], ["列车：找一个观察者看到小球向后抛出", "Train: find an observer who sees the ball go backwards"]],
    model: [["建模", "Model", "工件、末端看成质点；传送带匀速；末端相对传送带竖直下降 0.25 m/s", "Part and gripper as particles; belt at constant speed; gripper descends 0.25 m/s relative to the belt"],
            ["求解", "Solve", "v(对地) = (0.50, −0.25) m/s，大小 0.56 m/s，向下偏 26.6°。若只对地竖直下降，2.0 s 内工件滑过 1.0 m，抓不到", "v(ground) = (0.50, −0.25) m/s: 0.56 m/s, 26.6° below horizontal. Descending straight down relative to the ground, the part slides 1.0 m past in 2.0 s"],
            ["检验", "Check", "虚拟实验 1.1“传送带抓取”：两个参考系中分别观察轨迹、读对地速度", "Lab 1.1 “conveyor grasp”: compare the path in both frames and read the ground velocity"],
            ["修正", "Improve", "传送带速度有波动，要用编码器或视觉实时跟踪；抓取前后的加减速也要规划", "Belt speed varies, so track it with an encoder or camera; plan the acceleration before and after the grasp"]],
    everyday: ["雨天车窗上的雨痕：雨滴下落 7 m/s、车速 20 m/s，雨痕与竖直方向约成 71°（tanα = 20/7）", "Rain streaks on a car window: raindrops at 7 m/s, car at 20 m/s, streaks about 71° from vertical (tanα = 20/7)"],
  },
  {
    no: "1.2", zh: "位矢、位移、速度、加速度", en: "Position, displacement, velocity, acceleration", video: "Derivative", lab: "1-2",
    prob: { zh: "移动机器人的里程计", en: "Odometry of a mobile robot",
      text: ["仓储机器人每隔 T 记录一次自己的位置，用相邻两点的位移除以 T 算速度。采样间隔 T 该怎么选？",
             "A warehouse robot logs its position every T seconds and divides the displacement between samples by T to get speed. How should T be chosen?"],
      given: [["定位误差 σ ≈ 1 cm", "position error σ ≈ 1 cm"], ["行驶速度约 0.5 m/s", "speed about 0.5 m/s"], ["要求速率误差 < 5%", "speed error must be < 5%"]] },
    concept: { zh: "速度与加速度：对位矢求导", en: "Velocity and acceleration: derivatives of position",
      pts: [["位矢 r(t) 完整描述质点的位置", "The position vector r(t) fully describes where the particle is"],
            ["位移 Δr 是矢量，路程 Δs 是标量，一般 |Δr| ≠ Δs", "Displacement Δr is a vector, path length Δs a scalar; in general |Δr| ≠ Δs"],
            ["速度沿轨迹切线方向，速率是 ds/dt", "Velocity is tangent to the path; speed is ds/dt"],
            ["已知加速度求运动方程：积分 + 初始条件", "From acceleration to motion: integrate with initial conditions"]],
      formula: "v = dr/dt        a = dv/dt = d²r/dt²" },
    vq: ["Δt 越来越小时，弦 Δr 怎样变成切线方向的速度？", "As Δt shrinks, how does the chord Δr turn into the tangent velocity?"],
    tasks: [["里程计：σ = 1 cm 时，找出误差 < 5% 的采样间隔", "Odometry: find an interval with < 5% error at σ = 1 cm"], ["里程计：T < 0.05 s，观察噪声放大", "Odometry: T < 0.05 s, watch the noise grow"], ["例1-1：t = 1 s 时验证 v = 2i − 4j", "Example 1-1: check v = 2i − 4j at t = 1 s"]],
    model: [["建模", "Model", "机器人为质点；定位误差 σ ≈ 1 cm，各次独立；v ≈ |Δr| / T", "Robot as a particle; independent position errors σ ≈ 1 cm; v ≈ |Δr| / T"],
            ["求解", "Solve", "噪声引起的速率误差 ≈ √2·σ/T；要小于 5% × 0.5 m/s，得 T ≥ 0.57 s", "Noise error ≈ √2·σ/T; below 5% of 0.5 m/s requires T ≥ 0.57 s"],
            ["检验", "Check", "虚拟实验 1.2“里程计数据”：T 从 0.02 s 调到 1.5 s，误差先降后升", "Lab 1.2 “odometry”: sweep T from 0.02 s to 1.5 s; the error falls, then rises"],
            ["修正", "Improve", "T 太大时以弦代弧、速度滞后；实际用滤波融合轮速计和惯性测量单元，得到又稳又快的速度", "Large T cuts corners and lags; real robots filter and fuse wheel encoders with an IMU"]],
    everyday: ["手机导航每秒一个 GPS 点、误差几米，显示的车速经过平滑滤波，所以比定位点稳定", "Phone navigation gets one GPS fix per second with metres of error; the speed shown is filtered, so it is steadier than the fixes"],
  },
  {
    no: "1.3", zh: "抛体运动", en: "Projectile motion", video: "Projectile", lab: "1-3",
    prob: { zh: "投篮机器人", en: "A basketball-shooting robot",
      text: ["比赛用投篮机器人：出手点高 0.8 m，篮筐高 2.43 m、水平距离 4 m。给定出手角度，出手速度应是多少？角度大一些好还是小一些好？",
             "A competition robot releases the ball at 0.8 m; the hoop is 2.43 m high and 4 m away. For a given angle, what launch speed is needed? Is a steeper or flatter shot better?"],
      given: [["出手高 0.8 m", "release height 0.8 m"], ["篮筐高 2.43 m、距离 4 m", "hoop 2.43 m high, 4 m away"], ["发射速度误差 ±0.1 m/s", "launcher speed error ±0.1 m/s"]] },
    concept: { zh: "抛体运动", en: "Projectile motion",
      pts: [["只受重力：a = −g j（忽略空气阻力）", "Gravity only: a = −g j (no air drag)"],
            ["水平方向匀速，竖直方向匀加速", "Uniform horizontally, uniformly accelerated vertically"],
            ["轨迹是抛物线", "The path is a parabola"],
            ["h₀ = 0 时 45° 射程最大；互余角射程相同", "With h₀ = 0, 45° goes farthest; complementary angles give equal range"]],
      formula: "x = v₀cosθ·t    y = h₀ + v₀sinθ·t − ½gt²\nR = v₀² sin2θ / g   (h₀ = 0)", image: "fig/抛体运动轨迹.png", ratio: 4 / 7 },
    vq: ["把抛体运动投影到两个坐标轴上，你看到了哪两种运动？", "Project the motion onto the two axes: which two motions do you see?"],
    tasks: [["投篮：让球从上方落入篮筐", "Basket: drop the ball through the hoop"], ["投篮：两个角度都投进，比较所需速度", "Basket: score at two angles, compare speeds"], ["打开空气阻力：最佳角度还是 45° 吗？", "With drag on: is 45° still best?"]],
    model: [["建模", "Model", "球为质点，忽略空气阻力和旋转；出手点 (0, 0.8 m)，篮筐 (4 m, 2.43 m)", "Ball as a particle, no drag or spin; release (0, 0.8 m), hoop (4 m, 2.43 m)"],
            ["求解", "Solve", "v₀ = (X/cosθ)·√[g / (2(X tanθ − Δy))]：45° → 8.13 m/s，55° → 7.64 m/s，65° → 7.95 m/s", "v₀ = (X/cosθ)·√[g / (2(X tanθ − Δy))]: 45° → 8.13, 55° → 7.64, 65° → 7.95 m/s"],
            ["检验", "Check", "虚拟实验 1.3“投篮”：按计算值发射；用 v₀ ± 0.1 m/s 再发射，45° 偏差约 ±0.3 m，65° 约 ±0.13 m", "Lab 1.3 “basket”: launch at the computed speed; with v₀ ± 0.1 m/s the miss is about ±0.3 m at 45° but ±0.13 m at 65°"],
            ["修正", "Improve", "高抛对速度误差不敏感、入射角大；还要考虑空气阻力、球的旋转和篮板反弹", "A steep shot tolerates speed error and enters more steeply; drag, spin and the backboard also matter"]],
    everyday: ["铅球：出手高 2 m、速度 13.5 m/s 时，最佳出手角约 42°，射程约 20.5 m，不是 45°", "Shot put: released at 2 m and 13.5 m/s, the best angle is about 42° (range about 20.5 m), not 45°"],
  },
  {
    no: "1.4", zh: "圆周运动", en: "Circular motion", video: "Circular", lab: "1-4",
    prob: { zh: "AGV 转弯限速", en: "AGV cornering speed limit",
      text: ["仓储搬运机器人（AGV）载货后在通道拐弯。最快能开多快，才不会侧翻、不会打滑？",
             "A loaded warehouse AGV turns a corner in an aisle. How fast can it go without tipping over or sliding?"],
      given: [["转弯半径 1.5 m", "turn radius 1.5 m"], ["质心高 0.6 m，轮距 0.5 m", "centre of mass 0.6 m high, track 0.5 m"], ["摩擦因数 μ = 0.6", "friction coefficient μ = 0.6"]] },
    concept: { zh: "圆周运动：两个加速度分量", en: "Circular motion: two components of acceleration",
      pts: [["切向加速度改变速率的大小", "Tangential acceleration changes the speed"],
            ["法向加速度指向圆心，改变速度的方向", "Normal acceleration points to the centre and changes the direction"],
            ["匀速圆周运动：aₜ = 0，aₙ ≠ 0", "Uniform circular motion: aₜ = 0 but aₙ ≠ 0"],
            ["角量与线量：v = Rω，aₜ = Rα，aₙ = Rω²", "Angular and linear: v = Rω, aₜ = Rα, aₙ = Rω²"]],
      formula: "aₜ = dv/dt        aₙ = v²/R", image: "fig/圆周运动加速度.png", ratio: 1 },
    vq: ["速率不变，为什么还有加速度？Δv 最后指向哪里？", "The speed is constant, so why is there an acceleration? Where does Δv point?"],
    tasks: [["AGV：R = 1.5 m 时不侧翻的最大速度", "AGV: highest speed without tipping at R = 1.5 m"], ["AGV：再加速，先侧翻还是先打滑？", "AGV: faster still—tip or slide first?"], ["例1-3：读出 t = 2 s 时的 aₜ、aₙ", "Example 1-3: read aₜ and aₙ at t = 2 s"]],
    model: [["建模", "Model", "AGV 看成刚体做匀速圆周运动；地面摩擦提供向心力", "AGV as a rigid body in uniform circular motion; friction provides the centripetal force"],
            ["求解", "Solve", "不打滑 v ≤ √(μgR) = 2.97 m/s；不侧翻 v ≤ √(g·b/(2h)·R) = 2.47 m/s，先侧翻；若限 0.3g，v ≤ 2.10 m/s", "No sliding: v ≤ √(μgR) = 2.97 m/s; no tipping: v ≤ √(g·b/(2h)·R) = 2.47 m/s, so it tips first; at 0.3g, v ≤ 2.10 m/s"],
            ["检验", "Check", "虚拟实验 1.4“AGV 转弯”：R = 1.5 m 逐渐加速，约 2.47 m/s 时出现“侧翻”", "Lab 1.4 “AGV turning”: at R = 1.5 m, speed up until it shows “tipping” at about 2.47 m/s"],
            ["修正", "Improve", "货物晃动、制动时的切向加速度、地面湿滑都会降低限速；可降低质心、加宽轮距、弯道自动减速", "Load sway, braking and wet floors lower the limit; lower the centre of mass, widen the track, slow down in curves"]],
    everyday: ["高速公路弯道按侧向加速度 ≤ 0.2g 设计：R = 500 m 时 v ≈ 31 m/s ≈ 113 km/h", "Highway curves are designed for ≤ 0.2g sideways: at R = 500 m, v ≈ 31 m/s ≈ 113 km/h"],
  },
  {
    no: "1.5", zh: "相对运动", en: "Relative motion", video: "Relative", lab: "1-5",
    prob: { zh: "无人机侧风航线修正", en: "Drone crosswind correction",
      text: ["巡检无人机要沿直线飞到正北 1 km 的目标，途中遇到东风侧风。机头要偏多少？要飞多久？",
             "An inspection drone must fly straight to a target 1 km north through an easterly crosswind. How far must it turn into the wind, and how long will it take?"],
      given: [["空速 12 m/s", "airspeed 12 m/s"], ["侧风 5 m/s", "crosswind 5 m/s"], ["航程 1 km", "distance 1 km"]] },
    concept: { zh: "相对运动：伽利略速度变换", en: "Relative motion: Galilean velocity addition",
      pts: [["同一质点在两个相对平动的参考系中速度不同", "One particle has different velocities in two frames moving relative to each other"],
            ["A 相对 C 的速度 = A 相对 B + B 相对 C", "A rel. C = A rel. B + B rel. C"],
            ["速度是矢量，按平行四边形（三角形）法则相加", "Velocities add as vectors (parallelogram or triangle rule)"],
            ["只适用于低速情况（远小于光速）", "Valid only at speeds far below the speed of light"]],
      formula: "v_AC = v_AB + v_BC" },
    vq: ["船头垂直河岸，船为什么会被冲到下游？想正对岸靠岸该怎么办？", "Why does the boat drift downstream, and how can it land straight across?"],
    tasks: [["无人机：侧风 5 m/s 直线飞到目标（偏差 ≤ 10 m）", "Drone: fly straight to the target in a 5 m/s wind (within 10 m)"], ["小船：正对岸靠岸（偏差 ≤ 2 m）", "Boat: land straight across (within 2 m)"], ["小船：水速 > 船速时能正对岸吗？", "Boat: current faster than the boat—possible?"]],
    model: [["建模", "Model", "无人机相对空气 12 m/s；风均匀恒定 5 m/s 向东；v(对地) = v(对空气) + v(风)", "Drone at 12 m/s relative to the air; steady 5 m/s wind to the east; v(ground) = v(air) + v(wind)"],
            ["求解", "Solve", "sinφ = 5/12，φ ≈ 24.6°；地速 √(12² − 5²) ≈ 10.9 m/s；用时 ≈ 91.7 s，比无风多 8.4 s", "sinφ = 5/12, φ ≈ 24.6°; ground speed √(12² − 5²) ≈ 10.9 m/s; time ≈ 91.7 s, 8.4 s longer than in still air"],
            ["检验", "Check", "虚拟实验 1.5“无人机侧风”：φ = 25° 时到达点偏差约 6 m", "Lab 1.5 “drone crosswind”: at φ = 25° the miss is about 6 m"],
            ["修正", "Improve", "风会变化，飞控要实时估计风速并修正航向；风速 15 m/s 大于空速时无法保持航线，应返航或改航", "Wind changes, so the flight controller estimates it and corrects continuously; a 15 m/s wind exceeds the airspeed and the drone must return or reroute"]],
    everyday: ["飞机侧风着陆时机头斜对跑道（“蟹行”），和小船过河是同一个速度三角形", "Aircraft land in a crosswind with the nose angled off the runway (“crabbing”): the same velocity triangle as the river crossing"],
  },
];

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "第1章 质点运动学 Chapter 1 Kinematics of a Particle";

// ---- title
let s = pres.addSlide();
s.background = { color: NAVY };
s.addText("第 1 章  Chapter 1", T({ x: 0.8, y: 1.4, w: 8, h: 0.5, fontFace: CN, fontSize: 20, color: AMBER, bold: true }));
s.addText("质点运动学", T({ x: 0.8, y: 2.0, w: 11.5, h: 1.1, fontFace: CN, fontSize: 44, color: WHITE, bold: true }));
s.addText("Kinematics of a Particle", T({ x: 0.8, y: 3.05, w: 11.5, h: 0.6, fontFace: EN, fontSize: 26, color: "CADCFC" }));
s.addText([{ text: "用矢量和微积分描述运动，用模型解决机器人中的实际问题", options: { breakLine: true } },
           { text: "Describing motion with vectors and calculus, and modelling real robot problems", options: { fontFace: EN, fontSize: 14, color: "9FB3D1" } }],
  T({ x: 0.8, y: 4.0, w: 11.5, h: 0.9, fontFace: CN, fontSize: 17, color: "E6EDF7" }));
s.addText("大学物理A（上） University Physics A (I)  ·  2026 秋 Fall 2026", T({ x: 0.8, y: 6.5, w: 10, h: 0.4, fontFace: CN, fontSize: 12, color: "9FB3D1" }));
s.addNotes("开场问题：机器人怎样知道自己跑多快、往哪里走？引出位置矢量。\nOpening question: how does a robot know how fast it is moving and where it is heading?");

// ---- how each lesson works
s = pres.addSlide();
s.background = { color: WHITE };
biTitle(s, "本章内容与每节课的结构", "Chapter map and how each lesson works", 0.45);
L.forEach((l, i) => {
  const y = 1.75 + i * 0.95;
  s.addShape(pres.shapes.OVAL, { x: 0.8, y, w: 0.62, h: 0.62, fill: { color: NAVY } });
  s.addText(l.no, T({ x: 0.8, y, w: 0.62, h: 0.62, fontFace: CN, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle" }));
  s.addText([{ text: l.zh, options: { breakLine: true } }, { text: l.en, options: { fontFace: EN, fontSize: 11, color: MUTED, bold: false } }],
    T({ x: 1.6, y: y - 0.04, w: 4.6, h: 0.72, fontFace: CN, fontSize: 16, bold: true, color: INK, valign: "middle" }));
  s.addText([{ text: "机器人问题：" + l.prob.zh, options: { breakLine: true } }, { text: "Robot: " + l.prob.en, options: { fontFace: EN, fontSize: 10, color: MUTED } }],
    T({ x: 6.3, y: y - 0.04, w: 6.4, h: 0.72, fontFace: CN, fontSize: 13, color: INK, valign: "middle" }));
});
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.8, y: 6.55, w: 11.9, h: 0.6, fill: { color: ICE }, line: { color: ICE }, rectRadius: 0.1 });
s.addText("每节课：实际问题 → 概念 → 动画 → 虚拟实验 → 建模求解    Each lesson: problem → concept → animation → virtual lab → modelling",
  T({ x: 1.0, y: 6.55, w: 11.5, h: 0.6, fontFace: CN, fontSize: 13, color: NAVY, bold: true, valign: "middle" }));
s.addNotes("物理学通过建立模型来观察和描述世界。本章每节课都从一个机器人实际问题出发，最后回到这个问题，用本节的模型解决它。\nPhysics describes the world through models. Each lesson starts from a robot problem and returns to solve it with that lesson’s model.");

L.forEach((l) => {
  // ---- A. the real problem
  let sl = pres.addSlide();
  sl.background = { color: PALE };
  tag(sl, `${l.no}  机器人问题  Robot problem`);
  biTitle(sl, l.prob.zh, l.prob.en);
  sl.addText([{ text: l.prob.text[0], options: { breakLine: true, paraSpaceAfter: 8 } }, { text: l.prob.text[1], options: { fontFace: EN, fontSize: 12, color: MUTED } }],
    T({ x: 0.7, y: 1.8, w: 5.6, h: 2.4, fontFace: CN, fontSize: 16, color: INK, valign: "top" }));
  sl.addText("已知  Given", T({ x: 0.7, y: 4.35, w: 5, h: 0.35, fontFace: CN, fontSize: 13, color: MUTED, bold: true }));
  sl.addText(biList(l.prob.given, 14, 10.5), T({ x: 0.7, y: 4.75, w: 5.6, h: 2.3, fontFace: CN, valign: "top" }));
  const iw = 6.3, ih = iw * 10 / 16;
  sl.addImage({ path: path.join(MEDIA, `robot_${l.lab}.png`), x: 6.6, y: 1.8, w: iw, h: ih });
  sl.addShape(pres.shapes.RECTANGLE, { x: 6.6, y: 1.8, w: iw, h: ih, fill: { type: "none" }, line: { color: "D9CFA8", width: 1 } });
  sl.addText("本节结束时，我们用建立的模型回答这个问题。  We will answer it with this lesson’s model at the end.",
    T({ x: 6.6, y: 1.8 + ih + 0.15, w: iw, h: 0.6, fontFace: CN, fontSize: 11, color: MUTED }));
  sl.addNotes("先让学生猜一猜、讨论 2 分钟，不急于给答案。本节最后回到这一页。\nLet students guess and discuss for two minutes; do not give the answer yet. Return to this problem at the end of the lesson.");

  // ---- B. concept
  const c = l.concept;
  sl = pres.addSlide();
  sl.background = { color: WHITE };
  tag(sl, `${l.no}  概念  Concept`);
  biTitle(sl, c.zh, c.en);
  const textW = c.image ? 6.3 : 11.9;
  sl.addText(biList(c.pts), T({ x: 0.7, y: 1.8, w: textW, h: 3.3, fontFace: CN, valign: "top" }));
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 5.35, w: textW, h: 1.4, fill: { color: ICE }, line: { color: ICE }, rectRadius: 0.12 });
  sl.addText(c.formula, T({ x: 1.0, y: 5.4, w: textW - 0.5, h: 1.3, fontFace: "Cambria Math", fontSize: 18, color: NAVY, bold: true, valign: "middle" }));
  if (c.image) { const ih = Math.min(4.9, 5.4 * c.ratio), iw = ih / c.ratio; sl.addImage({ path: c.image, x: 7.3 + (5.4 - iw) / 2, y: 1.8, w: iw, h: ih }); }
  sl.addNotes("讲清公式的物理意义，再进入动画。\nExplain the physical meaning of each formula before the animation.");

  // ---- C. animation
  sl = pres.addSlide();
  sl.background = { color: NIGHT };
  tag(sl, `${l.no}  动画  Animation`);
  sl.addText([{ text: l.vq[0], options: { breakLine: true } }, { text: l.vq[1], options: { fontFace: EN, fontSize: 13, color: "9FB3D1", bold: false } }],
    T({ x: 0.7, y: 0.6, w: 12, h: 0.85, fontFace: CN, fontSize: 19, color: WHITE, bold: true }));
  const vw = 9.3, vh = vw * 9 / 16, vx = (13.333 - vw) / 2, vy = 1.6;
  sl.addMedia({ type: "video", path: path.join(VID, l.video + ".mp4"), x: vx, y: vy, w: vw, h: vh, cover: b64(path.join(MEDIA, "poster_" + l.video + ".png")) });
  sl.addText("点击画面播放 · 中英字幕 · Click to play · bilingual captions", T({ x: vx, y: vy + vh + 0.08, w: vw, h: 0.3, fontFace: CN, fontSize: 11, color: "9FB3D1", align: "center" }));
  sl.addNotes("播放动画，在关键画面暂停提问。\nPlay the clip and pause at the key frame to ask the question on the slide.");

  // ---- D. virtual lab
  sl = pres.addSlide();
  sl.background = { color: ICE };
  tag(sl, `${l.no}  虚拟实验  Virtual lab`);
  biTitle(sl, "动手试一试：" + l.zh, "Try it: " + l.en);
  const iw2 = 7.3, ih2 = iw2 * 10 / 16, url = `${LAB}#lab-${l.lab}`;
  sl.addImage({ path: path.join(MEDIA, "lab_" + l.lab + ".png"), x: 0.7, y: 1.8, w: iw2, h: ih2, hyperlink: { url, tooltip: "打开虚拟实验 Open the virtual lab" } });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 1.8, w: iw2, h: ih2, fill: { type: "none" }, line: { color: "C9D3DD", width: 1 } });
  sl.addText("任务  Tasks", T({ x: 8.4, y: 1.8, w: 4.3, h: 0.35, fontFace: CN, fontSize: 14, color: MUTED, bold: true }));
  sl.addText(biList(l.tasks, 14, 10.5, INK, MUTED, true), T({ x: 8.4, y: 2.2, w: 4.3, h: 3.0, fontFace: CN, valign: "top" }));
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.4, y: 5.35, w: 4.3, h: 0.65, fill: { color: NAVY }, line: { color: NAVY }, rectRadius: 0.1, hyperlink: { url, tooltip: "打开虚拟实验" } });
  sl.addText([{ text: "打开虚拟实验  Open lab ▶", options: { hyperlink: { url } } }], T({ x: 8.4, y: 5.35, w: 4.3, h: 0.65, fontFace: CN, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle" }));
  sl.addText("课后按实验指导书完成实验报告 · Write the lab report using the lab guide", T({ x: 8.4, y: 6.1, w: 4.3, h: 0.5, fontFace: CN, fontSize: 11, color: MUTED, align: "center" }));
  sl.addNotes("课堂投屏演示一遍机器人场景，其余任务课后完成，并按实验指导书写实验报告。\nDemonstrate the robot scene in class; students finish the tasks and the lab report after class.");

  // ---- E. back to the problem: the 5-step model
  sl = pres.addSlide();
  sl.background = { color: WHITE };
  tag(sl, `${l.no}  回到实际问题  Back to the problem`);
  biTitle(sl, "建模求解：" + l.prob.zh, "Modelling: " + l.prob.en);
  const rows = [[
    { text: "步骤 Step", options: { bold: true, fill: { color: ICE }, color: INK } },
    { text: "内容 What we do", options: { bold: true, fill: { color: ICE }, color: INK } },
  ]];
  rows.push([{ text: "① 问题\nProblem", options: { bold: true } }, { text: [{ text: l.prob.text[0], options: { breakLine: true } }, { text: l.prob.text[1], options: { fontFace: EN, fontSize: 10.5, color: MUTED } }] }]);
  l.model.forEach(([zh, en, a, b], i) => {
    rows.push([{ text: `${"②③④⑤"[i]} ${zh}\n${en}`, options: { bold: true } }, { text: [{ text: a, options: { breakLine: true } }, { text: b, options: { fontFace: EN, fontSize: 10.5, color: MUTED } }] }]);
  });
  sl.addTable(rows, { x: 0.7, y: 1.75, w: 8.4, colW: [1.35, 7.05], fontFace: CN, fontSize: 13.5, color: INK, border: { type: "solid", pt: 0.75, color: "D5DEE8" }, valign: "middle", margin: 0.06 });
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.4, y: 1.75, w: 3.3, h: 3.6, fill: { color: PALE }, line: { color: PALE }, rectRadius: 0.12 });
  sl.addText([{ text: "生活中的例子", options: { bold: true, breakLine: true } }, { text: "Everyday example", options: { fontFace: EN, fontSize: 11, color: MUTED, breakLine: true } },
              { text: l.everyday[0], options: { fontSize: 13, breakLine: true, paraSpaceBefore: 8 } }, { text: l.everyday[1], options: { fontFace: EN, fontSize: 10, color: MUTED } }],
    T({ x: 9.6, y: 1.9, w: 2.9, h: 3.3, fontFace: CN, fontSize: 15, color: INK, valign: "top" }));
  sl.addText("物理学通过建立模型来观察和描述世界：先简化，再求解，再用实验检验，最后找出模型的局限。\nPhysics describes the world through models: simplify, solve, test, then find where the model breaks.",
    T({ x: 9.4, y: 5.5, w: 3.3, h: 1.4, fontFace: CN, fontSize: 10.5, color: MUTED, valign: "top" }));
  sl.addNotes("对照五步讲解，强调第⑤步：模型在哪里失效。实验报告第六部分按这五步写。\nWalk through the five steps and stress step ⑤, where the model fails. Section 6 of the lab report follows the same steps.");
});

// ---- worked example
s = pres.addSlide();
s.background = { color: ICE };
tag(s, "例题  Worked example");
s.addText([{ text: "质点沿半径 R = 0.10 m 的圆周运动，θ = 2 + 4t³（rad）。求 t = 2 s 时的切向加速度和法向加速度。", options: { breakLine: true } },
           { text: "A particle moves on a circle of radius R = 0.10 m with θ = 2 + 4t³ (rad). Find aₜ and aₙ at t = 2 s.", options: { fontFace: EN, fontSize: 13, color: MUTED, bold: false } }],
  T({ x: 0.7, y: 0.75, w: 12, h: 1.4, fontFace: CN, fontSize: 20, color: INK, bold: true, valign: "top" }));
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 2.4, w: 12, h: 4.3, fill: { color: WHITE }, line: { color: "D5DEE8" }, rectRadius: 0.12 });
s.addText(biList([["ω = dθ/dt = 12t²，α = dω/dt = 24t", "ω = dθ/dt = 12t², α = dω/dt = 24t"], ["t = 2 s：ω = 48 rad/s，α = 48 rad/s²", "At t = 2 s: ω = 48 rad/s, α = 48 rad/s²"],
                  ["aₜ = Rα = 0.10 × 48 = 4.8 m/s²", "aₜ = Rα = 4.8 m/s²"], ["aₙ = Rω² = 0.10 × 48² ≈ 230 m/s²（可在虚拟实验 1.4 中验证）", "aₙ = Rω² ≈ 230 m/s² (check it in lab 1.4)"]], 17, 12, INK, MUTED, true),
  T({ x: 1.0, y: 2.65, w: 11.4, h: 3.9, fontFace: CN, valign: "top" }));
s.addNotes("先让学生独立做 3 分钟，再展开解答；最后打开虚拟实验 1.4 的“例1-3”模式对照。\nGive students three minutes, then work through it and check with lab 1.4.");

// ---- summary
s = pres.addSlide();
s.background = { color: NAVY };
s.addText("本章小结", T({ x: 0.8, y: 0.5, w: 8, h: 0.7, fontFace: CN, fontSize: 30, color: WHITE, bold: true }));
s.addText("Chapter summary", T({ x: 0.8, y: 1.15, w: 8, h: 0.4, fontFace: EN, fontSize: 16, color: "9FB3D1" }));
s.addText(biList([["求导：r → v → a；积分：a → v → r（需要初始条件）", "Differentiate r → v → a; integrate a → v → r with initial conditions"],
                  ["|Δr| ≠ Δs，速率 = ds/dt；采样定速度要权衡噪声与间隔", "|Δr| ≠ Δs, speed = ds/dt; sampled speed trades noise against interval"],
                  ["抛体：x、y 分解；过定点求出手速度", "Projectiles: split into x and y; solve for the launch speed through a point"],
                  ["圆周：aₙ = v²/R 决定转弯限速", "Circles: aₙ = v²/R sets the cornering speed limit"],
                  ["相对运动：v_AC = v_AB + v_BC，用于跟踪抓取和航向修正", "Relative motion: v_AC = v_AB + v_BC, for conveyor tracking and heading correction"]], 17, 11.5, "E6EDF7", "9FB3D1"),
  T({ x: 0.8, y: 1.8, w: 11.8, h: 4.3, fontFace: CN, valign: "top" }));
s.addText("课后作业：习题1 第1–6题 ＋ 5 个虚拟实验任务 ＋ 实验报告（任选一个机器人问题）\nHomework: Problems 1–6 + the five virtual labs + one lab report on a robot problem",
  T({ x: 0.8, y: 6.2, w: 11.8, h: 0.8, fontFace: CN, fontSize: 14, color: AMBER }));
s.addNotes("回顾本章知识结构，提醒作业与实验报告的截止时间，预告下一章。\nReview the chapter, remind students of the deadlines, and preview Chapter 2.");

pres.writeFile({ fileName: OUT }).then(() => console.log("deck written", OUT));
