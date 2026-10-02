// 实验 3.1 同一支箭头，两套坐标系（配 3.1 节）。箭头 d 由长度 L 和方向角 φ（从 x_a 量起）给出；{b} 相对 {a} 绕 z 轴转过 β。
// d 在 {a} 中的分量 (L cos φ, L sin φ)；在 {b} 中的分量 (L cos(φ − β), L sin(φ − β))（式 (3.1.5)，即 3.3 节的 d_b = R_abᵀ d_a）。
WQ.lab({
  title: ["实验 3.1 同一支箭头，两套坐标系", "Lab 3.1 One arrow, two frames"],
  goal: ["转动坐标系 {b}，看同一支箭头的两套分量怎样变化，而长度始终不变。",
         "Turn frame {b} and watch the two sets of components of one arrow change while its length stays the same."],
  scenes: [
    { id: "cam", robot: true, name: ["相机与机械臂", "Camera and arm"],
      problem: { title: ["机器人问题：相机给出的读数怎样交给机械臂", "Robot problem: handing the camera's reading to the arm"],
                 text: ["夹爪到零件的位移 d 在机座坐标系 {a} 和相机坐标系 {b} 中各有一组分量。相机装歪了 β，两组数不同，箭头却是同一支。",
                        "The displacement d from gripper to part has components in the base frame {a} and in the camera frame {b}. The camera is turned by β: two sets of numbers, one arrow."] } },
    { id: "map", name: ["导航地图", "Navigation map"],
      problem: { title: ["生活中的例子：正北朝上与车头朝上", "Everyday example: north-up and heading-up"],
                 text: ["目的地相对汽车的位置不变。地图“正北朝上”时用 {a}（东、北）读数，“车头朝上”时用随车转动的 {b} 读数。",
                        "The destination does not move. A north-up map reads it in {a} (east, north); a heading-up map reads it in {b}, which turns with the car."] },
      params: { L: { min: 0.1, max: 0.6, value: 0.5 }, phi: { value: 53 }, beta: { value: 0 } } },
  ],
  params: [
    { id: "L", name: ["箭头长度 |d|", "Length |d|"], min: 0.1, max: 0.5, step: 0.01, value: 0.36, unit: "m", digits: 2 },
    { id: "phi", name: ["箭头方向角 φ（从 x_a 量起）", "Direction φ (from x_a)"], min: -180, max: 180, step: 1, value: 34, unit: "°", digits: 0 },
    { id: "beta", name: ["{b} 的转角 β", "Turn of {b}, β"], min: -180, max: 180, step: 1, value: 30, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "align", robot: true, text: ["转动 {b}，使它的 x 轴对准箭头：d 在 {b} 中只剩第一个分量，且为正。", "Turn {b} so that its x axis points along the arrow: only the first component in {b} is left, and it is positive."],
      demo: { scene: "cam", set: { L: 0.36, phi: 34, beta: 34 }, press: [] } },
    { id: "equal", robot: true, text: ["使 d 在 {b} 中的两个分量相等且为正。此时 β 与 φ 相差多少？", "Make the two components in {b} equal and positive. How do β and φ differ?"],
      demo: { scene: "cam", set: { L: 0.36, phi: 34, beta: -11 }, press: [] } },
    { id: "minus", robot: true, text: ["使 {b} 的 y 轴与箭头方向相反：d_b = (0, −|d|)。", "Make the y axis of {b} point against the arrow: d_b = (0, −|d|)."],
      demo: { scene: "cam", set: { L: 0.36, phi: 34, beta: 124 }, press: [] } },
    { id: "heading", text: ["导航地图：汽车朝正东行驶，地图切换为“车头朝上”，{b} 的 y 轴（车头）指向正东（β = −90°）。读出目的地在 {b} 中的分量：它在车的前方多远、左侧多远？",
                            "Map: the car heads east and the map turns heading-up, so y_b (the heading) points east (β = −90°). Read the destination in {b}: how far ahead, how far to the left?"],
      demo: { scene: "map", set: { L: 0.5, phi: 53, beta: -90 }, press: [] } },
  ],
  think: ["若 β 增加 360°，两套分量会怎样？若 φ 和 β 同时增加同一个角度呢？", "What happens to the components if β grows by 360°? And if φ and β grow by the same angle?"],

  comps(api) {
    const d = Math.PI / 180, L = api.p.L, f = api.p.phi * d, b = api.p.beta * d;
    return { a: [L * Math.cos(f), L * Math.sin(f)], b: [L * Math.cos(f - b), L * Math.sin(f - b)], L };
  },
  reset(api, s) {},
  readouts(api, s) {
    const c = this.comps(api), map = api.scene === "map", k = map ? 1000 : 1, u = " m", dg = map ? 0 : 4;
    const tol = 1e-3;
    if (api.scene === "cam" && Math.abs(c.b[1]) < tol && c.b[0] > 0) api.done("align");
    if (api.scene === "cam" && Math.abs(c.b[0] - c.b[1]) < 0.003 && c.b[0] > 0) api.done("equal");
    if (api.scene === "cam" && Math.abs(c.b[0]) < tol && c.b[1] < 0) api.done("minus");
    if (map && api.p.beta === -90) api.done("heading");
    const la = Math.hypot(c.a[0], c.a[1]), lb = Math.hypot(c.b[0], c.b[1]);
    return [
      [map ? ["{a}（东, 北）中的分量", "in {a} (east, north)"] : ["d 在 {a}（机座）中", "d in {a} (base)"], `(${api.fmt(k * c.a[0], dg)}, ${api.fmt(k * c.a[1], dg)})${u}`],
      [map ? ["{b}（车头朝上）中的分量", "in {b} (heading-up)"] : ["d 在 {b}（相机）中", "d in {b} (camera)"], `(${api.fmt(k * c.b[0], dg)}, ${api.fmt(k * c.b[1], dg)})${u}`],
      [["由 {a} 中分量算的长度", "length from {a}"], api.fmt(k * la, dg) + u],
      [["由 {b} 中分量算的长度", "length from {b}"], api.fmt(k * lb, dg) + u],
      [["箭头与 x_b 的夹角 φ − β", "angle to x_b, φ − β"], api.fmt(((api.p.phi - api.p.beta + 540) % 360) - 180, 0) + "°"],
    ];
  },
  draw(api, s) {
    const { w, h } = api, map = api.scene === "map";
    const cx = w * 0.42, cy = h * 0.62, k = Math.min(w, h) * (map ? 0.72 : 1.3);
    const X = (x, y) => [cx + k * x, cy - k * y];
    const c = this.comps(api), d = Math.PI / 180, b = api.p.beta * d;
    const ink = api.css("--ink"), muted = api.css("--muted");
    if (map) {   // 街道网格（正东、正北）
      api.ctx.globalAlpha = 0.35;
      for (let i = -6; i <= 6; i++) {
        api.line(...X(i * 0.1, -0.6), ...X(i * 0.1, 0.6), muted, i === 0 ? 3 : 1);
        api.line(...X(-0.6, i * 0.1), ...X(0.6, i * 0.1), muted, i === 0 ? 3 : 1);
      }
      api.ctx.globalAlpha = 1;
    }
    // {a}：固定
    api.frame(cx, cy, 0, k * 0.22, map ? [api.T("东", "E"), api.T("北", "N")] : ["x_a", "y_a"], "{a}");
    // {b}：转过 β
    api.frame(cx, cy, api.p.beta, k * 0.3, map ? ["x_b", api.T("车头 y_b", "heading y_b")] : ["x_b", "y_b"], "", muted);
    api.label("{b}", ...X(0.33 * Math.cos(b) + 0.03, 0.33 * Math.sin(b) - 0.03), muted, 13);
    // 投影到 {b} 两根轴上
    const tip = X(...c.a);
    const f1 = [c.b[0] * Math.cos(b), c.b[0] * Math.sin(b)], f2 = [-c.b[1] * Math.sin(b), c.b[1] * Math.cos(b)];
    api.line(...tip, ...X(...f1), api.css("--red"), 1.5, [5, 4]);
    api.line(...tip, ...X(...f2), api.css("--green"), 1.5, [5, 4]);
    api.line(cx, cy, ...X(...f1), api.css("--red"), 6);
    api.line(cx, cy, ...X(...f2), api.css("--green"), 6);
    // 箭头 d
    api.arrow(cx, cy, ...tip, ink, 4);
    api.label("d", tip[0] + 8, tip[1] - 10, ink, 16);
    if (map) {
      api.robot(cx, cy, api.p.beta + 90, 26, api.css("--accent"));
      api.line(...tip, tip[0], tip[1] - 26, ink, 2); api.rect(tip[0], tip[1] - 26, 16, 10, api.css("--red"));
    } else {
      api.circle(cx, cy, 9, api.css("--panel"), ink);
      api.box(tip[0], tip[1] + 10, 20, api.css("--amber"));
    }
    api.label(api.T(`β = ${api.p.beta}°`, `β = ${api.p.beta}°`), 12, 18, muted, 13);
  },
});
