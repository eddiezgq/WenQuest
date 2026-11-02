// 实验 15.5 把卫星送入轨道（配 15.5 节）。
// 火箭的上面级在 400 km 高处水平入轨（不计空气阻力和地球自转），选入轨速度 v₀，看卫星走圆轨道、椭圆轨道还是逃逸。
// 轨道按二体问题的解析公式计算：比能 ε = v²/2 − GM/r，半长轴 a = −GM/(2ε)，近地点、远地点由角动量和能量求出。
// 第二个场景（生活中的例子）：在小行星上扔石头。小行星半径 5.0 km、平均密度 2.0 g/cm³，人在地面上水平扔出。
const GM155 = 3.986004418e14, RE155 = 6.371e6, H155 = 400e3;
const RA155 = 5.0e3, GMA155 = 6.6743e-11 * 2000 * 4 / 3 * Math.PI * Math.pow(5.0e3, 3);
function orbit155(GM, r0, v) {                                              // 返回 {type, rp, ra, T}
  const eps = v * v / 2 - GM / r0, hh = r0 * v;
  if (eps >= 0) return { type: "esc" };
  const a = -GM / (2 * eps), e = Math.sqrt(Math.max(0, 1 + 2 * eps * hh * hh / (GM * GM)));
  return { type: "ell", a, e, rp: a * (1 - e), ra: a * (1 + e), T: 2 * Math.PI * Math.sqrt(a * a * a / GM) };
}
const RUN155 = {};
const key155 = (api) => `${api.scene}|${api.p.v}|${api.p.va}`;

WQ.lab({
  title: ["实验 15.5 把卫星送入轨道", "Lab 15.5 Putting a satellite into orbit"],
  goal: ["改变入轨速度，看卫星走圆轨道、椭圆轨道还是逃逸；找出圆轨道速度、到达地球静止轨道高度的转移轨道速度和逃逸速度，与公式比较。",
         "Change the injection speed and see whether the satellite circles, follows an ellipse or escapes; find the circular speed, the speed for a transfer orbit reaching geostationary height, and the escape speed, and compare with the formulas."],
  scenes: [
    { id: "launch", robot: true, name: ["卫星入轨", "Orbit injection"], hide: ["va"],
      problem: { title: ["航天器问题：上面级关机时速度要多大？", "Spacecraft problem: how fast at engine cut-off?"],
                 text: ["火箭的上面级把卫星送到 400 km 高处，沿水平方向关机入轨。关机时的速度决定了卫星的轨道。选入轨速度，点“开始”，看轨道，读近地点、远地点高度和周期。",
                        "The rocket's upper stage takes the satellite to 400 km and cuts off moving horizontally. The speed at cut-off decides the orbit. Choose the injection speed, press “Start”, watch the orbit and read the perigee and apogee heights and the period."] } },
    { id: "asteroid", name: ["小行星上扔石头", "Throwing a stone on an asteroid"], hide: ["v"],
      problem: { title: ["生活中的例子：在小行星上能把石头扔进轨道吗？", "Everyday example: can you throw a stone into orbit on an asteroid?"],
                 text: ["一颗半径 5.0 km、平均密度 2.0 g/cm³ 的小行星。站在它的地面上水平扔出石头（不计地形），扔多快石头会绕它转？多快会飞走？",
                        "An asteroid of radius 5.0 km and mean density 2.0 g/cm³. Standing on its surface, throw a stone horizontally (ignore the terrain). How fast for the stone to orbit it, and how fast to fly away?"] } },
  ],
  params: [
    { id: "v", name: ["入轨速度 v₀", "Injection speed v₀"], min: 6.0, max: 12.0, step: 0.01, value: 7.50, unit: "km/s", digits: 2 },
    { id: "va", name: ["扔出的速度", "Throw speed"], min: 0.50, max: 8.00, step: 0.01, value: 2.00, unit: "m/s", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  tasks: [
    { id: "circ", robot: true, text: ["卫星入轨：调入轨速度，使轨道成为圆轨道（远地点与近地点高度相差不超过 20 km），运行后提交。", "Orbit injection: adjust the speed for a circular orbit (apogee and perigee heights within 20 km), run and submit."],
      demo: { scene: "launch", set: { v: 7.67 }, press: ["start", "submit"], wait: 2 } },
    { id: "gto", robot: true, text: ["卫星入轨：调入轨速度，使远地点到达地球静止轨道的高度 35 786 km（相差 500 km 以内），运行后提交。", "Orbit injection: adjust the speed so the apogee reaches geostationary height, 35 786 km (within 500 km), run and submit."],
      demo: { scene: "launch", set: { v: 10.07 }, press: ["start", "submit"], wait: 2 } },
    { id: "rock", text: ["小行星：找出石头恰好绕小行星转圈的扔出速度（圆轨道，相差 0.05 m/s 以内），运行后提交。", "Asteroid: find the throw speed that just puts the stone in a circular orbit (within 0.05 m/s), run and submit."],
      demo: { scene: "asteroid", set: { va: 3.74 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["入轨速度比圆轨道速度大 10%，远地点为什么会高出几千千米？逃逸速度是圆轨道速度的几倍？在小行星上，人跳起来会不会飞走？",
          "Why does a speed 10% above circular raise the apogee by thousands of kilometres? How many times the circular speed is the escape speed? On the asteroid, could you jump off it?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; },
  start(api, s) { s.ran = true; s.k = Object.assign({}, api.p); },
  update(dt, api, s) { if (api.t >= 3) { RUN155[key155(api)] = true; api.stop(); } },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = s.ran && s.k ? s.k : api.p, have = s.ran || RUN155[key155(api)]; let ok = false;
    if (api.scene === "launch" && have) {
      const o = orbit155(GM155, RE155 + H155, p.v * 1000);
      if (o.type === "ell" && o.rp > RE155 && Math.abs(o.ra - o.rp) <= 20e3) { api.done("circ"); ok = true; }
      if (o.type === "ell" && Math.abs(o.ra - RE155 - 35786e3) <= 500e3) { api.done("gto"); ok = true; }
    }
    if (api.scene === "asteroid" && have && Math.abs(p.va - Math.sqrt(GMA155 / RA155)) <= 0.05) { api.done("rock"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"], have = (s.ran && !api.running) || RUN155[key155(api)];
    const ast = api.scene === "asteroid", GM = ast ? GMA155 : GM155, R = ast ? RA155 : RE155, r0 = ast ? RA155 : RE155 + H155;
    const o = orbit155(GM, r0, ast ? p.va : p.v * 1000);
    if (!have) return [[["轨道", "Orbit"], "—"], sub];
    if (o.type === "esc") return [[["轨道", "Orbit"], api.T("逃逸（不再回来）", "escape (never returns)")], sub];
    if (o.rp < R) return [[["轨道", "Orbit"], api.T("落回地面", "falls back to the ground")], [["落地前飞过的最高点（离地）", "Highest point before landing"], f((o.ra - R) / (ast ? 1 : 1000), ast ? 0 : 0) + (ast ? " m" : " km")], sub];
    const u = ast ? 1 : 1000, un = ast ? " m" : " km";
    return [[[ast ? "最低高度" : "近地点高度", ast ? "Lowest height" : "Perigee height"], f((o.rp - R) / u, 0) + un], [[ast ? "最高高度" : "远地点高度", ast ? "Highest height" : "Apogee height"], f((o.ra - R) / u, 0) + un],
            [["周期", "Period"], f(o.T / 60, 1) + " min"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue"), p = api.p;
    const ast = api.scene === "asteroid", GM = ast ? GMA155 : GM155, R = ast ? RA155 : RE155, r0 = ast ? RA155 : RE155 + H155;
    const have = s.ran || RUN155[key155(api)], v = ast ? p.va : p.v * 1000, o = orbit155(GM, r0, v);
    const span = !have ? 2 * R : (o.type === "esc" ? 8 * R : Math.min(8 * R, Math.max(2 * R, o.ra * 1.1)));
    const sc = Math.min(w, h) * 0.45 / span, cx = w * 0.5, cy = h * 0.5;
    api.circle(cx, cy, R * sc, ast ? mut : blue, ink);
    api.circle(cx, cy - r0 * sc, 4, red, ink);
    if (!have) return;
    const frac = s.ran && api.running ? api.t / 3 : 1;
    let x = 0, y = r0, vx = v, vy = 0, prev = null;
    const dt = (o.type === "ell" ? o.T : 4 * span / v) / 3000;
    for (let k = 0; k < 3000 * frac; k++) {                                   // 速度韦尔莱法，只用于画图
      const r3 = Math.pow(x * x + y * y, 1.5), ax = -GM * x / r3, ay = -GM * y / r3;
      vx += 0.5 * dt * ax; vy += 0.5 * dt * ay; x += dt * vx; y += dt * vy;
      const r3b = Math.pow(x * x + y * y, 1.5); vx += -0.5 * dt * GM * x / r3b; vy += -0.5 * dt * GM * y / r3b;
      if (Math.hypot(x, y) < R) break;
      const P = [cx + x * sc, cy - y * sc]; if (prev) api.line(prev[0], prev[1], P[0], P[1], red, 2); prev = P;
      if (Math.hypot(x, y) > span * 1.2) break;
    }
  },
});
