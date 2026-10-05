// 实验 5.6 相对运动（配 5.6 节）。
// 传送带场景：传送带以 0.30 m/s 向 +x 运动，零件 t = 0 时在 x = −0.60 m。夹爪停在 x = 0、带面以上 0.15 m 处，学生选开始下降的时刻 t₀
// 和下降过程中夹爪的水平速度；下降速度固定为 0.30 m/s（0.50 s 到达带面）。到达带面时与零件的水平距离不超过 0.02 m、
// 且水平速度与传送带相差不超过 0.03 m/s 才算抓稳。可在地面参考系和传送带参考系之间切换观察。
// 无人机场景：空速 8.0 m/s，西风 4.0 m/s（向东吹），目标在正北 1.2 km；学生选机头方向，飞到北向 1.2 km 时东西偏差不超过 30 m 才算到达。
// 雨场景：雨滴竖直下落，速度学生不知道；学生选车速，读侧窗上雨痕与竖直方向的夹角，算出雨滴下落速度并提交（3% 以内）。
const U56 = 0.30, XP0_56 = -0.60, H56 = 0.15, VD56 = 0.30, TD56 = H56 / VD56;
function grip56(p) {                               // 夹爪与零件在地面系中的位置随时间
  const t1 = p.t0 + TD56, xg1 = p.vgx * TD56, xp1 = XP0_56 + U56 * t1;
  return { t1, xg1, xp1, miss: xg1 - xp1, dv: p.vgx - U56 };
}
const VA56 = 8.0, W56 = 4.0, D56 = 1200;
function fly56(phiDeg) { const ph = phiDeg * Math.PI / 180, vn = VA56 * Math.cos(ph), ve = VA56 * Math.sin(ph) + W56;
  if (vn <= 0) return { ok: false, t: Infinity, east: Infinity, vn, ve }; const t = D56 / vn; return { t, east: ve * t, vn, ve }; }
const VR56 = 7.2;                                  // 雨滴下落速度（学生不知道）
const rainDeg56 = (vc) => Math.atan2(vc, VR56) * 180 / Math.PI;

WQ.lab({
  title: ["实验 5.6 相对运动", "Lab 5.6 Relative motion"],
  goal: ["从移动的传送带上抓取零件；让无人机在侧风中飞到目标；由车窗上雨痕的倾角求雨滴下落的速度。",
         "Pick a part off a moving belt; fly a drone to a target in a crosswind; find how fast rain falls from the slant of streaks on a car window."],
  scenes: [
    { id: "belt", robot: true, name: ["传送带抓取", "Picking from a belt"], hide: ["phi", "vc", "vrhat"],
      problem: { title: ["机器人问题：在零件经过时抓住它", "Robot problem: catch the part as it passes"],
                 text: ["传送带以 0.30 m/s 向右运动，零件开始时在 x = −0.60 m。夹爪停在 x = 0 上方 0.15 m 处，以 0.30 m/s 下降，0.50 s 到达带面。选开始下降的时刻和下降时夹爪的水平速度，使夹爪落到零件上、且水平速度与零件相同。",
                        "The belt moves right at 0.30 m/s; the part starts at x = −0.60 m. The gripper waits 0.15 m above x = 0 and descends at 0.30 m/s, reaching the belt in 0.50 s. Choose when to start and the gripper's horizontal speed during the descent so that it lands on the part moving with it."] } },
    { id: "drone", robot: true, name: ["侧风中的无人机", "Drone in a crosswind"], hide: ["vgx", "t0", "view", "vc", "vrhat"],
      problem: { title: ["机器人问题：对准正北的目标", "Robot problem: reach a target due north"],
                 text: ["无人机相对空气的速度为 8.0 m/s，风从西向东吹，风速 4.0 m/s。目标在正北 1.2 km。选机头方向（从正北量起，向西为负），使它到达北向 1.2 km 时东西偏差不超过 30 m。",
                        "The drone's airspeed is 8.0 m/s; the wind blows from west to east at 4.0 m/s. The target is 1.2 km due north. Choose the heading (from north, west negative) so that it is within 30 m east–west when it has flown 1.2 km north."] } },
    { id: "rain", name: ["车窗上的雨", "Rain on a car window"], hide: ["vgx", "t0", "view", "phi"],
      problem: { title: ["生活中的例子：雨滴下落多快", "Everyday example: how fast does rain fall"],
                 text: ["无风，雨滴竖直下落。坐在车里，侧窗上的雨痕是斜的。选车速，读出雨痕与竖直方向的夹角，算出雨滴的下落速度，提交。",
                        "No wind; the rain falls vertically. From inside the car the streaks on the side window slant. Choose the car speed, read the angle of the streaks from the vertical, work out how fast the rain falls and submit."] } },
  ],
  params: [
    { id: "vgx", name: ["下降时夹爪的水平速度", "Gripper horizontal speed while descending"], min: 0, max: 0.6, step: 0.01, value: 0, unit: "m/s", digits: 2 },
    { id: "t0", name: ["开始下降的时刻 t₀", "Start of descent t₀"], min: 0, max: 3, step: 0.05, value: 1.0, unit: "s", digits: 2 },
    { id: "view", name: ["观察参考系：0 地面，1 传送带", "Frame: 0 ground, 1 belt"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "phi", name: ["机头方向（从正北量起，向西为负）", "Heading (from north, west negative)"], min: -60, max: 60, step: 0.5, value: 0, unit: "°", digits: 1 },
    { id: "vc", name: ["车速", "Car speed"], min: 2, max: 30, step: 0.5, value: 10, unit: "m/s", digits: 1 },
    { id: "vrhat", name: ["你算出的雨滴下落速度", "Your rain speed"], min: 2, max: 12, step: 0.05, value: 5, unit: "m/s", digits: 2 },
  ],
  buttons: [{ id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "belt", robot: true, text: ["传送带：选下降时刻和水平速度，让夹爪稳稳地落在零件上，提交。在传送带参考系中看，夹爪是怎样运动的？", "Belt: choose the start time and horizontal speed so the gripper lands squarely on the part, and submit. How does the gripper move in the belt frame?"],
      demo: { scene: "belt", set: { vgx: 0.30, t0: 2.0 }, press: ["submit"], wait: 1 } },
    { id: "drone", robot: true, text: ["无人机：选机头方向，让它飞到目标（东西偏差 30 m 以内），提交。对地速度是多少？", "Drone: choose the heading that reaches the target (within 30 m east–west) and submit. What is the ground speed?"],
      demo: { scene: "drone", set: { phi: -30 }, press: ["submit"], wait: 1 } },
    { id: "rain", text: ["雨：用量角器读出雨痕的倾角，算出雨滴的下落速度，提交（3% 以内）。", "Rain: read the streak angle on the protractor, work out the rain's speed and submit (within 3%)."],
      demo: { scene: "rain", set: { vc: 15, vrhat: 7.2 }, press: ["submit"], wait: 1 } },
  ],
  think: ["传送带场景中，夹爪落到零件上时的水平速度为什么必须等于传送带的速度？在两个参考系中，夹爪的加速度相同吗？无人机机头偏向上风时，对地速度为什么比空速小？",
          "Why must the gripper's horizontal speed equal the belt's when it touches the part? Is the gripper's acceleration the same in both frames? Why is the ground speed less than the airspeed when the drone heads into the wind?"],

  reset(api, s) {},
  change(api, s, pid) { s.msg = ""; s.shown = false; },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "belt") { const R = grip56(p); ok = Math.abs(R.miss) <= 0.02 && Math.abs(R.dv) <= 0.03; if (ok) api.done("belt"); }
    if (api.scene === "drone") { const F = fly56(p.phi); ok = isFinite(F.east) && Math.abs(F.east) <= 30; if (ok) api.done("drone"); }
    if (api.scene === "rain") { ok = Math.abs(p.vrhat - VR56) / VR56 <= 0.03; if (ok) api.done("rain"); }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet"); s.shown = true;
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "belt") { const R = grip56(p);
      return [[["到达带面的时刻", "Reaches the belt at"], f(R.t1, 2) + " s"], [["零件与夹爪的位置（提交后显示）", "Part and gripper positions (after submitting)"], s.shown ? f(R.xp1, 3) + ", " + f(R.xg1, 3) + " m" : "—"], sub]; }
    if (api.scene === "drone") { const F = fly56(p.phi);
      return [[["机头方向", "Heading"], f(p.phi, 1) + "°"], [["北向 1.2 km 时东西偏差（提交后显示）", "East–west offset at 1.2 km north (after submitting)"], s.shown && isFinite(F.east) ? f(F.east, 0) + " m" : "—"], sub]; }
    return [[["车速", "Car speed"], f(p.vc, 1) + " m/s"], [["雨痕的夹角", "Streak angle"], api.T("用右边的量角器读", "read it on the protractor at the right")], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, blue = css("--blue"), mut = css("--muted"), ink = css("--ink"), red = css("--red"), green = css("--green");
    if (api.scene === "belt") {
      const R = grip56(p), belt = p.view === 1;
      const G = api.graph({ x: 50, y: 30, w: w - 90, h: h * 0.55, xmin: -0.7, xmax: 0.5, ymin: -0.05, ymax: 0.25, xlabel: belt ? api.T("x′（传送带系）/ m", "x′ (belt frame) / m") : api.T("x（地面系）/ m", "x (ground frame) / m"), ylabel: api.T("高度 / m", "height / m") }).axes();
      G.hline(0, mut, []);
      const sh = (x, t) => (belt ? x - U56 * t : x);                 // 伽利略变换 x′ = x − ut
      const gp = [], pp = [];
      for (let t = 0; t <= R.t1 + 1e-9; t += 0.02) { const xg = t < p.t0 ? 0 : p.vgx * (t - p.t0), yg = t < p.t0 ? H56 : H56 - VD56 * (t - p.t0);
        gp.push([sh(xg, t), yg]); pp.push([sh(XP0_56 + U56 * t, t), 0.01]); }
      G.pts(pp, blue, 3);
      if (s.shown) { G.pts(gp, red, 2.5); G.point(sh(R.xp1, R.t1), 0.01, blue, api.T("零件", "part")).point(sh(R.xg1, R.t1), 0, red, api.T("夹爪落点", "gripper lands"), 8, 18); }
      api.label(api.T("蓝：零件的轨迹　红：夹爪的轨迹（提交后画出）", "blue: part   red: gripper (drawn after submitting)"), 50, h * 0.55 + 70, mut, 11);
      return;
    }
    if (api.scene === "drone") {
      const F = fly56(p.phi), sc = (h - 60) / 1300, cx = w * 0.45, by = h - 30;
      api.line(cx, by, cx, by - D56 * sc, mut, 1, [4, 4]); api.circle(cx, by - D56 * sc, 7, null, green); api.label(api.T("目标", "target"), cx + 10, by - D56 * sc, green, 12);
      if (isFinite(F.t) && s.shown) { const n = 60, pts = []; for (let i = 0; i <= n; i++) { const t = F.t * i / n; pts.push([cx + F.ve * t * sc, by - F.vn * t * sc]); }
        for (let i = 1; i < pts.length; i++) api.line(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], red, 2.5); }
      const vx0 = w * 0.78, vy0 = h * 0.6, k = 14, ph = p.phi * Math.PI / 180;
      api.arrow(vx0, vy0, vx0 + VA56 * Math.sin(ph) * k, vy0 - VA56 * Math.cos(ph) * k, blue, 3);
      api.arrow(vx0 + VA56 * Math.sin(ph) * k, vy0 - VA56 * Math.cos(ph) * k, vx0 + (VA56 * Math.sin(ph) + W56) * k, vy0 - VA56 * Math.cos(ph) * k, green, 3);
      api.arrow(vx0, vy0, vx0 + F.ve * k, vy0 - F.vn * k, red, 3);
      api.label(api.T("蓝：相对空气　绿：风　红：对地", "blue: air  green: wind  red: ground"), vx0 - 80, vy0 + 30, mut, 11);
      api.label(api.T("北 ↑", "N ↑"), 20, 30, mut, 13); api.label(api.T("风 →", "wind →"), 20, 52, green, 13);
      return;
    }
    const ang = rainDeg56(p.vc) * Math.PI / 180, x0 = w * 0.25, y0 = 40, W = w * 0.5, Hh = h * 0.6;
    api.rect(x0, y0, W, Hh, "#e9f1f6", ink, 6);
    for (let i = 0; i < 9; i++) { const L = 60, sx = x0 + 20 + L * Math.sin(ang) + i * (W - 40 - L * Math.sin(ang)) / 8; api.line(sx, y0 + 30 + (i % 3) * 50, sx - L * Math.sin(ang), y0 + 30 + (i % 3) * 50 + L * Math.cos(ang), blue, 2); }
    const px = x0 + W + 110, py = y0 + 30, Rq = 90;           // 量角器：每 5° 一个刻度，每 10° 标数；雨痕平移到这里
    for (let dg = 0; dg <= 90; dg += 5) { const q = dg * Math.PI / 180, L = dg % 10 ? 6 : 12;
      api.line(px - (Rq - L) * Math.sin(q), py + (Rq - L) * Math.cos(q), px - Rq * Math.sin(q), py + Rq * Math.cos(q), mut, 1);
      if (dg % 10 === 0) api.label(String(dg), px - (Rq + 14) * Math.sin(q), py + (Rq + 14) * Math.cos(q) + 4, mut, 10, "center"); }
    api.line(px, py, px, py + Rq, mut, 1, [3, 3]); api.line(px, py, px - Rq * Math.sin(ang), py + Rq * Math.cos(ang), blue, 2);
    api.label(api.T("量角器（从竖直方向量起）", "protractor (from the vertical)"), px - 90, py + Rq + 40, mut, 11);
    api.label(api.T("侧窗（车向右开）", "side window (car moving right)"), x0, y0 + Hh + 24, mut, 12);
  },
});
