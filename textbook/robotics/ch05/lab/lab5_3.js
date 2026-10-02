// 实验 5.3 左乘与右乘（配 5.3 节）。平面位姿 T_st = [[R(a), p], [0, 1]]。
// 右乘（相对自身）：T ← T·Trans(step, 0) 或 T ← T·Rot(turn)；左乘（相对基座 {s}）：T ← Trans(step, 0)·T 或 T ← Rot(turn)·T。
// 夹爪场景：步长 0.1 m、转角 30°，起点 (0.6, 0.3, 0°)，夹具位姿 (1.0, 0.7, 90°)。
// 街区场景：步长 1 m、转角 90°，起点 (0, 0)、面朝北（90°），商店在 (−2, 3)。
WQ.lab({
  title: ["实验 5.3 左乘与右乘", "Lab 5.3 Left- and right-multiplication"],
  goal: ["用四个按钮移动一只夹爪（或一个行人）：两个相对自身（右乘），两个相对基座（左乘）。比较结果，并读出位姿矩阵和它的逆。",
         "Move a gripper (or a walker) with four buttons: two relative to itself (right-multiply), two relative to the base (left-multiply). Compare the results and read the pose and its inverse."],
  scenes: [
    { id: "grip", robot: true, name: ["夹爪进夹具", "Gripper into the fixture"],
      problem: { title: ["机器人问题：只用工具坐标系中的点动", "Robot problem: jog only in the tool frame"],
                 text: ["示教时只允许“沿夹爪前进 0.1 m”和“绕夹爪自身转 30°”。把夹爪从 (0.6, 0.3) m 送进 (1.0, 0.7) m 处朝上的夹具。",
                        "Only “forward 0.1 m along the gripper” and “turn 30° about the gripper” are allowed. Bring it from (0.6, 0.3) m into the upward fixture at (1.0, 0.7) m."] } },
    { id: "walk", name: ["街区里的行人", "A walker in town"],
      problem: { title: ["生活中的例子：“前进、左转”与“向北、向东”", "Everyday example: “ahead, turn left” vs “north, east”"],
                 text: ["行人在 (0, 0) 面朝北。只用“前进 1 格”和“左转 90°”，走到 (−2, 3) 的商店。",
                        "The walker is at (0, 0) facing north. Using only “ahead 1 block” and “turn left 90°”, reach the shop at (−2, 3)."] } },
  ],
  params: [],
  buttons: [
    { id: "fwd", name: ["右乘：沿自身 x 前进", "Right: ahead along own x"], primary: true },
    { id: "rotB", name: ["右乘：绕自身原点左转", "Right: turn left about own origin"], primary: true },
    { id: "movS", name: ["左乘：沿基座 x 平移", "Left: shift along base x"] },
    { id: "rotS", name: ["左乘：绕基座原点左转", "Left: turn left about the base origin"] },
    { id: "reset", name: ["重置", "Reset"] },
  ],
  tasks: [
    { id: "fix", robot: true, text: ["只用两个“右乘”按钮，把夹爪送进夹具。", "Using only the two “right” buttons, bring the gripper into the fixture."],
      demo: { scene: "grip", press: ["reset", "fwd", "fwd", "fwd", "fwd", "rotB", "rotB", "rotB", "fwd", "fwd", "fwd", "fwd"] } },
    { id: "swing", robot: true, text: ["从起点按一次“绕基座原点左转”，读出夹爪被甩出的距离。", "From the start, press “turn left about the base origin” once and read how far the gripper is flung."],
      demo: { scene: "grip", press: ["reset", "rotS"] } },
    { id: "walk", text: ["只用“前进”和“左转”走到商店。", "Reach the shop using only “ahead” and “turn left”."],
      demo: { scene: "walk", press: ["reset", "fwd", "fwd", "fwd", "rotB", "fwd", "fwd"] } },
  ],
  think: ["“绕基座原点左转”与“绕自身原点左转”的转角相同，为什么夹爪的姿态相同、位置却不同？什么情况下两者完全一样？",
          "The two left turns have the same angle: why is the orientation the same but the position different? When are they identical?"],

  cfg(api) {
    return api.scene === "grip" ? { step: 0.1, turn: 30, start: [0.6, 0.3, 0], goal: [1.0, 0.7, 90] }
      : { step: 1, turn: 90, start: [0, 0, 90], goal: [-2, 3, null] };
  },
  reset(api, s) { const c = this.cfg(api); s.T = c.start.slice(); s.base = false; s.n = 0; s.swing = null; },
  action(id, api, s) {
    const c = this.cfg(api), [x, y, a] = s.T, t = a * Math.PI / 180;
    const before = s.T.slice();
    if (id === "fwd") s.T = [x + c.step * Math.cos(t), y + c.step * Math.sin(t), a];
    else if (id === "rotB") s.T = [x, y, a + c.turn];
    else if (id === "movS") { s.T = [x + c.step, y, a]; s.base = true; }
    else if (id === "rotS") { const u = c.turn * Math.PI / 180;
      s.T = [Math.cos(u) * x - Math.sin(u) * y, Math.sin(u) * x + Math.cos(u) * y, a + c.turn]; s.base = true;
      s.swing = Math.hypot(s.T[0] - before[0], s.T[1] - before[1]); }
    s.T[2] = ((s.T[2] % 360) + 540) % 360 - 180;
    s.T[0] = Math.round(s.T[0] * 1e9) / 1e9; s.T[1] = Math.round(s.T[1] * 1e9) / 1e9;
    s.n++;
  },
  readouts(api, s) {
    if (!s.T) this.reset(api, s);
    const c = this.cfg(api), [x, y, a] = s.T, t = a * Math.PI / 180, co = Math.cos(t), si = Math.sin(t);
    const at = (g) => Math.abs(x - g[0]) < 1e-6 && Math.abs(y - g[1]) < 1e-6 && (g[2] === null || Math.abs(((a - g[2]) % 360 + 540) % 360 - 180) < 1e-6);
    if (api.scene === "grip" && !s.base && at(c.goal)) api.done("fix");
    if (api.scene === "grip" && s.swing !== null && s.n === 1) api.done("swing");
    if (api.scene === "walk" && !s.base && at(c.goal)) api.done("walk");
    const ix = -(co * x + si * y), iy = -(-si * x + co * y);
    const r = (v) => `[${v.map((z) => api.fmt(z, 3)).join("  ")}]`;
    return [
      [["T_st 第 1、2 行", "T_st rows 1, 2"], `${r([co, -si, x])} ${r([si, co, y])}`],
      [["T_ts = T_st⁻¹ 第 1、2 行", "T_ts = T_st⁻¹ rows 1, 2"], `${r([co, si, ix])} ${r([-si, co, iy])}`],
      [["工具原点 / 朝向", "tool origin / heading"], `(${api.fmt(x, 3)}, ${api.fmt(y, 3)}) ${api.scene === "grip" ? "m" : ""} / ${api.fmt(a, 0)}°`],
      [["{s} 原点在工具坐标系中 p_ts", "origin of {s} in the tool frame, p_ts"], `(${api.fmt(ix, 3)}, ${api.fmt(iy, 3)})`],
      [["上一次左乘转动甩出的距离", "distance flung by the last left turn"], s.swing === null ? "—" : api.fmt(s.swing, 4) + (api.scene === "grip" ? " m" : "")],
      [["用过左乘按钮", "used a left button"], s.base ? api.T("是", "yes") : api.T("否", "no")],
    ];
  },
  draw(api, s) {
    if (!s.T) this.reset(api, s);
    const { w, h } = api, grip = api.scene === "grip", c = this.cfg(api);
    const k = grip ? Math.min(w / 1.6, h / 1.1) : Math.min(w / 9, h / 6.2);
    const ox = grip ? w * 0.12 : w * 0.62, oy = grip ? h * 0.9 : h * 0.82;
    const X = (x, y) => [ox + k * x, oy - k * y];
    if (!grip) {
      for (let i = -5; i <= 4; i++) api.line(...X(i, -0.6), ...X(i, 4.8), api.css("--grid"), 1);
      for (let j = -0; j <= 4; j++) api.line(...X(-5, j), ...X(4, j), api.css("--grid"), 1);
      api.rect(...X(c.goal[0] - 0.4, c.goal[1] + 0.4), 0.8 * k, 0.8 * k, api.css("--amber"), api.css("--ink"), 4);
      api.label(api.T("商店", "shop"), ...X(c.goal[0] - 0.3, c.goal[1] + 0.6), api.css("--ink"), 13);
      api.label(api.T("北 ↑", "N ↑"), ...X(3.2, 4.5), api.css("--muted"), 13);
    } else {
      const g = c.goal;   // 夹具：开口朝下（夹爪朝上伸入）
      api.rect(...X(g[0] - 0.09, g[1] + 0.16), 0.18 * k, 0.12 * k, null, api.css("--amber"));
      const s0 = c.start; api.circle(...X(s0[0], s0[1]), 4, api.css("--muted"));
      api.label(api.T("起点", "start"), X(s0[0], s0[1])[0] + 6, X(s0[0], s0[1])[1] + 14, api.css("--muted"), 12);
      api.label(api.T("夹具", "fixture"), ...X(g[0] + 0.1, g[1] + 0.12), api.css("--amber"), 13);
    }
    api.frame(...X(0, 0), 0, (grip ? 0.18 : 1.2) * k, ["x", "y"], "{s}");
    const [x, y, a] = s.T;
    if (grip) {
      const t = a * Math.PI / 180, R = (u, v) => X(x + Math.cos(t) * u - Math.sin(t) * v, y + Math.sin(t) * u + Math.cos(t) * v);
      api.line(...R(0, -0.05), ...R(0, 0.05), api.css("--ink"), 6);
      api.line(...R(0, 0.05), ...R(0.09, 0.05), api.css("--ink"), 6);
      api.line(...R(0, -0.05), ...R(0.09, -0.05), api.css("--ink"), 6);
      api.frame(...X(x, y), a, 0.12 * k, ["x", "y"], "{t}", api.css("--blue"));
    } else {
      api.circle(...X(x, y), 0.25 * k, api.css("--accent"), api.css("--ink"));
      api.frame(...X(x, y), a, 0.7 * k, ["x", "y"], "", api.css("--blue"));
    }
  },
});
