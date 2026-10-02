// 实验 11.1 关节即旋量（配 11.1 节）。
// 一根竖直的轴，按所选关节类型相对“螺母”运动：转动关节 R（h = 0）、螺旋副 H（h = 导程 / 2π）、移动关节 P（只平移）。
// 机器人场景：SCARA 的滚珠丝杠花键轴，轴线在 (0.6, 0, z) m，ω̂ = (0, 0, −1)（向下为正，与 SCARA 关节 3 一致）。
// 生活场景：拧瓶盖，轴线竖直向上，拧松（逆时针，从上往下看）时瓶盖上升。
WQ.lab({
  title: ["实验 11.1 关节即旋量", "Lab 11.1 Joints as screws"],
  goal: ["比较转动关节、螺旋副和移动关节：同一根轴，节距不同；并读出理想螺旋副中轴向力与扭矩的关系。",
         "Compare a revolute joint, a helical joint and a prismatic joint: one axis, different pitches; and read how axial force and torque are tied in an ideal screw."],
  scenes: [
    { id: "spline", robot: true, name: ["SCARA 的滚珠丝杠花键轴", "SCARA ball-screw spline"],
      problem: { title: ["机器人问题：只转工具，工具为什么会升降", "Robot problem: why the tool moves up when only its rotation is commanded"],
                 text: ["丝杠螺母不动、花键螺母带轴转动时，轴相对丝杠螺母作螺旋运动：转 θ，沿轴移动 hθ。",
                        "With the screw nut held and the spline nut turning the shaft, the shaft makes a screw motion relative to the screw nut: turn θ, advance hθ."] } },
    { id: "cap", name: ["拧瓶盖", "Unscrewing a bottle cap"],
      problem: { title: ["生活中的例子：瓶盖", "Everyday example: a bottle cap"],
                 text: ["瓶盖与瓶口是一个螺旋副。拧松时，瓶盖每转一圈上升一个导程。",
                        "A cap on a bottle neck is a helical joint. Unscrewing, the cap rises one lead per turn."] },
      params: { lead: { value: 3 } } },
  ],
  params: [
    { id: "type", name: ["关节类型：0 转动 R / 1 螺旋 H / 2 移动 P", "Joint type: 0 revolute R / 1 helical H / 2 prismatic P"], min: 0, max: 2, step: 1, value: 1, unit: "", digits: 0 },
    { id: "lead", name: ["导程 2πh", "Lead 2πh"], min: 1, max: 40, step: 0.5, value: 20, unit: "mm", digits: 1 },
    { id: "th", name: ["转角 θ（R、H）", "Turn θ (R, H)"], min: -720, max: 720, step: 5, value: 0, unit: "°", digits: 0 },
    { id: "d", name: ["移动距离 d（P）", "Slide d (P)"], min: -40, max: 40, step: 1, value: 0, unit: "mm", digits: 0 },
    { id: "F", name: ["轴向载荷 F", "Axial load F"], min: 0, max: 200, step: 5, value: 0, unit: "N", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "turn90", robot: true, text: ["螺旋副、导程 20 mm：转 90°，读出轴沿轴线移动了多少（应为 5 mm）。", "Helical, lead 20 mm: turn 90° and read how far the shaft advances (5 mm)."],
      demo: { scene: "spline", set: { type: 1, lead: 20, th: 90, d: 0, F: 0 }, press: [] } },
    { id: "rev", robot: true, text: ["换成转动关节（类型 0），转过 180° 以上，验证点始终在原来的高度。", "Switch to revolute (type 0), turn more than 180°: the point stays at its height."],
      demo: { scene: "spline", set: { type: 0, th: 270, d: 0, F: 0 }, press: [] } },
    { id: "torque", robot: true, text: ["螺旋副、导程 20 mm，加 50 N 轴向载荷，读出保持轴不动所需的扭矩。", "Helical, lead 20 mm, axial load 50 N: read the torque that keeps the shaft still."],
      demo: { scene: "spline", set: { type: 1, lead: 20, th: 0, F: 50 }, press: [] } },
    { id: "cap2", text: ["生活场景：导程 3 mm 的瓶盖拧两圈（720°），读出瓶盖升高多少。", "Everyday scene: a cap with a 3 mm lead turned two turns (720°); read how much it rises."],
      demo: { scene: "cap", set: { type: 1, lead: 3, th: 720, F: 0 }, press: [] } },
  ],
  think: ["导程越大，同样的轴向载荷需要的扭矩越大还是越小？为什么丝杠导程选得大，断电时负载更容易“滑下来”？",
          "With a larger lead, does the same axial load need more or less torque? Why does a load slide down more easily on a large-lead screw when the power is off?"],

  h(api) { return api.p.type === 0 ? 0 : api.p.lead / 1000 / (2 * Math.PI); },          // 节距 (m/rad)
  motion(api) {                      // 返回 {ang (rad), adv (m)}：转角和沿轴前进的距离
    const t = api.p.th * Math.PI / 180;
    if (api.p.type === 2) return { ang: 0, adv: api.p.d / 1000 };
    return { ang: t, adv: this.h(api) * t };
  },
  readouts(api, s) {
    const h = this.h(api), m = this.motion(api), ty = api.p.type;
    const names = [["转动关节 R", "revolute R"], ["螺旋副 H", "helical H"], ["移动关节 P", "prismatic P"]];
    // 旋量轴：机器人场景 ω̂ = (0, 0, −1)、q = (0.6, 0, 0)；生活场景 ω̂ = (0, 0, 1)、q = 0
    const robot = api.scene === "spline", w = robot ? [0, 0, -1] : [0, 0, 1], q = robot ? [0.6, 0, 0] : [0, 0, 0];
    const wxq = [w[1] * q[2] - w[2] * q[1], w[2] * q[0] - w[0] * q[2], w[0] * q[1] - w[1] * q[0]];
    let S;
    if (ty === 2) S = [0, 0, 0, w[0], w[1], w[2]];
    else S = [w[0], w[1], w[2], -wxq[0] + h * w[0], -wxq[1] + h * w[1], -wxq[2] + h * w[2]];
    const f = (x) => api.fmt(x, 4);
    const tau = ty === 1 ? h * api.p.F : 0;
    const adv_mm = m.adv * 1000;
    if (robot && ty === 1 && Math.abs(api.p.lead - 20) < 0.3 && Math.abs(api.p.th - 90) < 1) api.done("turn90");
    if (robot && ty === 0 && Math.abs(api.p.th) >= 180) api.done("rev");
    if (robot && ty === 1 && Math.abs(api.p.lead - 20) < 0.3 && Math.abs(api.p.F - 50) < 1) api.done("torque");
    if (!robot && ty === 1 && Math.abs(api.p.lead - 3) < 0.3 && Math.abs(api.p.th - 720) < 1) api.done("cap2");
    const rows = [
      [["关节", "joint"], api.lang() === "en" ? names[ty][1] : names[ty][0]],
      [["节距 h", "pitch h"], ty === 2 ? "∞" : api.fmt(h * 1000, 4) + " mm/rad"],
      [["旋量轴 𝒮 = (ω; v)", "screw axis 𝒮 = (ω; v)"], `(${S.slice(0, 3).map(f).join(", ")}; ${S.slice(3).map(f).join(", ")})`],
      [[robot ? "轴沿 ω̂ 前进（向下为正）" : "瓶盖上升", robot ? "advance along ω̂ (down positive)" : "cap rises"], api.fmt(adv_mm, 2) + " mm"],
    ];
    if (ty === 1) rows.push([["保持不动所需扭矩 τ = hF", "torque to hold still τ = hF"], api.fmt(tau, 4) + " N·m"]);
    else if (ty === 0) rows.push([["轴向载荷由谁承受", "who carries the axial load"], api.lang() === "en" ? "the bearing (no torque)" : "轴承（不需扭矩）"]);
    else rows.push([["轴向载荷由谁承受", "who carries the axial load"], api.lang() === "en" ? "the drive, as a force" : "驱动器，以力的形式"]);
    return rows;
  },
  draw(api, s) {
    const { w, h: H } = api, c = api.ctx, robot = api.scene === "spline";
    const m = this.motion(api), ty = api.p.type;
    const cx = w * 0.32, top = H * 0.12, bot = H * 0.9, R = Math.min(w, H) * 0.06;
    const k = H * 0.12 / 0.02;                                  // 位移放大显示：20 mm 画成画面高度的 12%
    const sgn = robot ? 1 : -1;                                 // 屏幕上向下为正
    const dy = sgn * Math.max(-H * 0.2, Math.min(H * 0.2, m.adv * k));
    api.label(api.lang() === "en" ? "axis" : "轴线", cx + 6, top - 10, api.css("--muted"), 12);
    api.line(cx, top, cx, bot, api.css("--muted"), 1, [6, 5]);
    if (robot) {
      // 丝杠螺母（不动）和花键螺母
      api.rect(cx - R * 2.1, H * 0.34, R * 4.2, H * 0.09, api.css("--amber"), api.css("--ink"), 4);
      api.label(api.lang() === "en" ? "screw nut (held)" : "丝杠螺母（不动）", cx + R * 2.4, H * 0.385, api.css("--amber"), 13);
      api.rect(cx - R * 2.1, H * 0.62, R * 4.2, H * 0.09, api.css("--blue"), api.css("--ink"), 4);
      api.label(api.lang() === "en" ? "spline nut (turns)" : "花键螺母（转动）", cx + R * 2.4, H * 0.665, api.css("--blue"), 13);
    } else {
      // 瓶身和瓶口
      api.rect(cx - R * 2.6, H * 0.55, R * 5.2, H * 0.4, api.css("--grid"), api.css("--ink"), 10);
      api.rect(cx - R * 1.2, H * 0.38, R * 2.4, H * 0.18, api.css("--grid"), api.css("--ink"), 3);
    }
    // 轴（或瓶盖）：画螺纹线，随转角移动相位
    const y0 = robot ? H * 0.2 + dy : H * 0.3 + dy, y1 = robot ? H * 0.82 + dy : H * 0.42 + dy, rr = robot ? R : R * 1.5;
    api.rect(cx - rr, y0, 2 * rr, y1 - y0, robot ? api.css("--panel") : api.css("--accent"), api.css("--ink"), 4);
    const pitchPx = Math.max(8, (ty === 0 ? 20 : api.p.lead) / 1000 * k * 0.6);
    c.save(); c.beginPath(); c.rect(cx - rr, y0, 2 * rr, y1 - y0); c.clip();
    c.strokeStyle = api.css("--muted"); c.lineWidth = 1;
    const phase = ((m.ang / (2 * Math.PI)) % 1 + 1) % 1;
    for (let yy = y0 - pitchPx * 2 + phase * pitchPx * sgn; yy < y1 + pitchPx; yy += pitchPx) {
      c.beginPath(); c.moveTo(cx - rr, yy); c.lineTo(cx + rr, yy + pitchPx * 0.45); c.stroke();
    }
    c.restore();
    // 轴上一点：绕轴转（侧视为左右摆动），前半圈实心、后半圈空心
    const py = (y0 + y1) / 2, ang = sgn * m.ang;
    const px = cx + rr * Math.sin(ang), front = Math.cos(ang) >= 0;
    api.circle(px, py, 6, front ? api.css("--red") : null, api.css("--red"));
    // 点在侧视图中的轨迹：右侧小图，纵轴为沿轴位移，横轴为 sin θ
    const gx = w * 0.62, gy = H * 0.15, gw = w * 0.32, gh = H * 0.7;
    api.rect(gx, gy, gw, gh, null, api.css("--grid"));
    api.label(api.lang() === "en" ? "side view of the point's path" : "点的轨迹（侧视）", gx + 4, gy - 10, api.css("--muted"), 12);
    const N = 360, th = api.p.th * Math.PI / 180;
    const zmax = Math.max(0.005, 1.15 * Math.abs(m.adv));      // 纵轴自动缩放
    c.strokeStyle = api.css("--red"); c.lineWidth = 2; c.beginPath();
    for (let i = 0; i <= N; i++) {
      const t = (i / N) * (ty === 2 ? 1 : th), adv = ty === 2 ? (i / N) * api.p.d / 1000 : this.h(api) * t;
      const X = gx + gw / 2 + gw * 0.35 * (ty === 2 ? 0 : Math.sin(sgn * t)), Y = gy + gh / 2 + sgn * adv / zmax * gh / 2;
      if (i === 0) c.moveTo(X, Y); else c.lineTo(X, Y);
    }
    c.stroke();
    api.line(gx + gw / 2, gy, gx + gw / 2, gy + gh, api.css("--muted"), 1, [4, 4]);
    api.label("±" + api.fmt(zmax * 1000, 1) + " mm", gx + gw - 4, gy + 10, api.css("--muted"), 11, "right");
    // 位移读数标在轴旁
    api.label((robot ? "↓ " : "↑ ") + api.fmt(Math.abs(m.adv * 1000), 2) + " mm", cx - rr - 8, py, api.css("--ink"), 14, "right");
  },
});
