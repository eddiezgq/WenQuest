// 实验 32.1 背隙对定位精度的影响（配 32.6 节）。
// 场景“WQ-CR5 手臂”：只看 J2、J3。手臂伸直（大臂 0.40 m、小臂 0.36 m，工具朝下），整条手臂与竖直线成 θ 角；反复去同一个目标点 10 次。
//   每个关节的背隙 b（角分）：齿贴在哪一侧决定输出轴多转或少转 b/2。
//   贴哪一侧：重力矩 τg 大于关节的空载摩擦力矩（机器人厂清单 joint_friction 名义值：J2 大模组 1.2、J3 中模组 0.8 N·m）时，
//     重力一直把齿压在同一侧（重力预紧）；否则由接近方向决定（双向：左右交替；单向：总从同一侧）。
//   重力矩：伸直水平时 J2 = 49.12 + 8.437·m_p、J3 = 18.50 + 4.513·m_p（N·m，WQ-CR5 的 joint_loads），倾斜 θ 时乘 sin θ（近似）。
//   TCP 的偏移 = Σ (±b_j/2)·力臂_j，力臂取伸直时 J2 0.88 m、J3 0.50 m（程序 32.6.1）；再加伺服的定位噪声 ±0.0025 mm（示例值）。
//   散布 = 10 次到达的最大差；重复定位精度 ±0.03 mm → 散布不超过 0.06 mm 为合格。
// 场景“旧自行车的车把”：前叉松旷 θ（度），车把往左打、往右打，前轮接地点相差 θ × 0.6 m（拖距与轮半径合成的示例力臂）。
WQ.lab({
  title: ["实验 32.1 背隙对定位精度的影响", "Lab 32.1 Backlash and positioning accuracy"],
  goal: ["改关节背隙、负载、手臂倾角和接近方式，看机器人反复到同一点时 TCP 的散布；体会 32.6 节“重力预紧、单向接近让背隙不进入重复定位精度”。",
         "Change the joint backlash, payload, arm tilt and approach; watch the spread of the TCP when the robot returns to one point — Section 32.6's “gravity preload and one-way approach keep backlash out of repeatability”."],
  scenes: [
    { id: "arm", robot: true, name: ["WQ-CR5 手臂", "WQ-CR5 arm"], hide: ["play"],
      problem: { title: ["机器人问题：背隙这么大，重复精度怎么做到的", "Robot problem: how is repeatability possible with this backlash"],
                 text: ["J2、J3 各有 0.6 角分的背隙，乘上力臂，TCP 能晃 0.2 mm 多，可 WQ-CR5 的重复定位精度是 ±0.03 mm。什么时候背隙会冒出来？怎样让它不冒出来？",
                        "J2 and J3 each have 0.6 arcmin of backlash; times the levers the TCP can wander over 0.2 mm, yet WQ-CR5 repeats to ±0.03 mm. When does backlash show, and how is it kept out?"] } },
    { id: "bike", name: ["旧自行车的车把", "An old bike's handlebar"], hide: ["b2", "b3", "mp", "th", "mode"],
      problem: { title: ["生活中的例子：车把松旷", "Everyday example: a loose headset"],
                 text: ["骑久了的自行车前叉松了，车把往左打、往右打，前轮的位置差一点，骑起来发飘。松旷多大，前轮就差 1 cm？",
                        "On an old bike the headset works loose: steer left, steer right and the front wheel lands in slightly different places. How much play gives 1 cm?"] } },
  ],
  params: [
    { id: "b2", name: ["J2 背隙", "J2 backlash"], min: 0, max: 2, step: 0.05, value: 0.6, unit: "′", digits: 2 },
    { id: "b3", name: ["J3 背隙", "J3 backlash"], min: 0, max: 2, step: 0.05, value: 0.6, unit: "′", digits: 2 },
    { id: "mp", name: ["负载", "Payload"], min: 0, max: 5, step: 0.5, value: 0, unit: "kg", digits: 1 },
    { id: "th", name: ["手臂与竖直线的夹角（0 竖直，90 水平）", "Arm tilt from vertical (0 up, 90 level)"], min: 0, max: 90, step: 0.5, value: 0, unit: "°", digits: 1 },
    { id: "mode", name: ["接近方式：0 双向 / 1 单向", "Approach: 0 both ways / 1 one way"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "play", name: ["前叉松旷", "Headset play"], min: 0, max: 3, step: 0.1, value: 0.3, unit: "°", digits: 1 },
  ],
  tasks: [
    { id: "std", robot: true, text: ["手臂竖直、空载、双向接近（背隙 0.6′）：读出散布，它是要求的几倍？",
                                     "Arm upright, no payload, both ways (0.6′ backlash): read the spread. How many times the requirement is it?"],
      demo: { scene: "arm", set: { b2: 0.6, b3: 0.6, mp: 0, th: 0, mode: 0 }, press: [] } },
    { id: "load", robot: true, text: ["手臂倾斜 2°、双向接近：空载时散布仍不合格；加负载，让散布合格。为什么倾斜 2° 就够了？",
                                      "Tilt 2°, both ways: unloaded the spread fails; add payload until it passes. Why is 2° enough?"],
      demo: { scene: "arm", set: { b2: 0.6, b3: 0.6, mp: 1.5, th: 2, mode: 0 }, press: [] } },
    { id: "oneway", robot: true, text: ["手臂竖直、空载（重力帮不上），改成单向接近，让散布合格。",
                                        "Upright and unloaded (gravity cannot help): switch to one-way approach and pass."],
      demo: { scene: "arm", set: { b2: 0.6, b3: 0.6, mp: 0, th: 0, mode: 1 }, press: [] } },
    { id: "small", robot: true, text: ["手臂竖直、空载、双向接近：只改两个关节的背隙，让散布合格。背隙要小到多少？",
                                       "Upright, unloaded, both ways: change only the two backlashes until the spread passes. How small must they be?"],
      demo: { scene: "arm", set: { b2: 0.1, b3: 0.1, mp: 0, th: 0, mode: 0 }, press: [] } },
    { id: "bike", text: ["车把：调前叉的松旷，让前轮左右相差约 1 cm（9～11 mm）。", "Handlebar: set the play so the front wheel shifts about 1 cm (9–11 mm)."],
      demo: { scene: "bike", set: { play: 1.0 }, press: [] } },
  ],
  think: ["重复定位精度合格了，机器人走一个整圆（各关节都要换向）时背隙还在吗？这时该怎么办？",
          "Repeatability passes — but on a full circle, where joints reverse, is the backlash still there? What then?"],

  ARCMIN: Math.PI / 180 / 60, LEV: [0.88, 0.50], FR: [1.2, 0.8], TH0: [49.12, 18.50], THP: [8.437, 4.513], N: 10, LIM: 0.06,
  noise(k) { const x = Math.sin(k * 12.9898 + 78.233) * 43758.5453; return (x - Math.floor(x) - 0.5) * 0.005; },
  calc(p) {
    const s = Math.sin(p.th * Math.PI / 180), b = [p.b2, p.b3];
    const tg = [0, 1].map((j) => (this.TH0[j] + this.THP[j] * p.mp) * s);
    const held = tg.map((t, j) => Math.abs(t) > this.FR[j]);
    const arr = [];
    for (let k = 0; k < this.N; k++) {
      const d = Math.round(p.mode) === 1 ? 1 : (k % 2 ? -1 : 1);
      let x = 0;
      for (let j = 0; j < 2; j++) x += (held[j] ? Math.sign(tg[j]) : d) * b[j] / 2 * this.ARCMIN * this.LEV[j] * 1000;
      arr.push(x + this.noise(k));
    }
    const spread = Math.max(...arr) - Math.min(...arr);
    return { tg, held, arr, spread, ok: spread <= this.LIM, dx: b.map((v, j) => v * this.ARCMIN * this.LEV[j] * 1000) };
  },
  nb(rows) { return rows.map(([k, v]) => [k, String(v).replace(/ /g, " ")]); },
  readouts(api) {
    const f = api.fmt, p = api.p, T = (z, e) => (api.lang() === "en" ? e : z);
    if (api.scene === "bike") {
      const diff = p.play * Math.PI / 180 * 600;
      if (diff >= 9 && diff <= 11) api.done("bike");
      return this.nb([[["前叉松旷", "Headset play"], f(p.play, 1) + "°"], [["前轮左右相差", "Front wheel shift"], f(diff, 1) + " mm"]]);
    }
    const c = this.calc(p), std = p.b2 === 0.6 && p.b3 === 0.6, two = Math.round(p.mode) === 0;
    if (std && p.mp === 0 && p.th === 0 && two) api.done("std");
    if (std && p.th === 2 && two && c.ok) api.done("load");
    if (std && p.mp === 0 && p.th === 0 && !two && c.ok) api.done("oneway");
    if (p.mp === 0 && p.th === 0 && two && c.ok) api.done("small");
    const st = (j) => `${f(Math.abs(c.tg[j]), 2)} / ${this.FR[j]} N·m ${c.held[j] ? T("压住", "held") : T("没压住", "free")}`;
    return this.nb([
      [["10 次到达的散布（要求 ≤ 0.06 mm）", "Spread of 10 arrivals (need ≤ 0.06 mm)"], `${f(c.spread, 3)} mm ${c.ok ? T("合格", "pass") : T("不合格", "fail")}`],
      [["散布 / 要求", "Spread / requirement"], f(c.spread / this.LIM, 1)],
      [["J2 重力矩 / 摩擦力矩", "J2 gravity / friction torque"], st(0)],
      [["J3 重力矩 / 摩擦力矩", "J3 gravity / friction torque"], st(1)],
      [["J2、J3 背隙乘力臂", "J2, J3 backlash × lever"], `${f(c.dx[0], 3)}、${f(c.dx[1], 3)} mm`],
    ]);
  },
  draw(api) {
    const { w, h } = api, f = api.fmt, p = api.p, T = (z, e) => (api.lang() === "en" ? e : z);
    if (api.scene === "bike") {
      const cx = w * 0.5, cy = h * 0.55, a = p.play * Math.PI / 180, k = 4;   // 角度放大 4 倍画
      api.label(T(`俯视；前轮偏转放大 ${k} 倍`, `top view; wheel angle × ${k}`), w * 0.05, h * 0.08, api.css("--muted"), 12, "left");
      [-1, 1].forEach((s) => {
        const t = s * a * k, L = h * 0.35;
        api.line(cx - Math.sin(t) * L, cy - Math.cos(t) * L, cx + Math.sin(t) * L, cy + Math.cos(t) * L, s < 0 ? api.css("--blue") : api.css("--green"), 6);
      });
      api.line(cx - w * 0.25, cy - h * 0.38, cx + w * 0.25, cy - h * 0.38, api.css("--ink"), 4);
      api.label(`${f(p.play * Math.PI / 180 * 600, 1)} mm`, cx + w * 0.08, cy + h * 0.38, api.css("--red"), 14, "left");
      return;
    }
    const c = this.calc(p), th = p.th * Math.PI / 180, bx = w * 0.18, by = h * 0.9, L = h * 0.75;
    api.label(T("侧视（背隙放大画）", "side view (backlash exaggerated)"), w * 0.03, h * 0.06, api.css("--muted"), 12, "left");
    const j3 = [bx + Math.sin(th) * L * 0.47, by - Math.cos(th) * L * 0.47], tcp = [bx + Math.sin(th) * L, by - Math.cos(th) * L];
    api.rect(bx - 20, by, 40, 10, api.css("--ink"));
    api.line(bx, by, j3[0], j3[1], api.css("--blue"), 10);
    api.line(j3[0], j3[1], tcp[0], tcp[1], api.css("--blue"), 8);
    [[bx, by, 0], [j3[0], j3[1], 1]].forEach(([x, y, j]) => api.circle(x, y, 9, c.held[j] ? api.css("--green") : api.css("--amber"), api.css("--ink")));
    if (p.mp > 0) api.rect(tcp[0] - 8, tcp[1] - 4, 16, 14, api.css("--amber"));
    // 到达点：横轴 mm
    const x0 = w * 0.5, x1 = w * 0.96, ym = h * 0.5, sc = (x1 - x0) / 0.5, xm = (x0 + x1) / 2;
    api.label(T("10 次到达的位置（mm，绿带 = ±0.03）", "10 arrivals (mm; green = ±0.03)"), x0, h * 0.2, api.css("--muted"), 12, "left");
    api.rect(xm - 0.03 * sc, ym - 30, 0.06 * sc, 60, api.css("--grid"));
    api.line(x0, ym, x1, ym, api.css("--ink"), 1);
    [-0.2, -0.1, 0, 0.1, 0.2].forEach((v) => api.label(f(v, 1), xm + v * sc, ym + 44, api.css("--muted"), 11, "center"));
    const mean = c.arr.reduce((a, b) => a + b, 0) / c.arr.length;
    c.arr.forEach((x, k) => api.circle(xm + (x - mean) * sc, ym - 20 + (k % 5) * 10, 4, c.ok ? api.css("--green") : api.css("--red")));
    api.label(`${f(c.spread, 3)} mm`, x1, h * 0.75, c.ok ? api.css("--green") : api.css("--red"), 14, "right");
  },
});
