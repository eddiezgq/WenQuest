// 实验 3.7 梯度与势场导航（配 3.7 节）。
// 土丘场景：H = 3.0 − 0.02x² − 0.05y²（与算例 3.7.1 相同），学生移动机器人、选行驶方向 φ，读出方向导数（坡度）；等高线是椭圆。
// 势场场景：AGV 从 (1, 2.4) m 出发去目标 (9, y_g)；x = 5 m 处有三根立柱排成一道墙（间隙太窄，过不去）。势 U = ½|r − g|² + 斥力项
// （斥力作用范围 1.2 m，强度 k_r），AGV 每步沿 −∇U 走 5 cm。目标在墙后时 AGV 停在墙前的局部极小；斥力加切向分量（绕行）可以绕出来。
// 雨水场景：地形有两个洼地，雨滴沿 −∇z 流下；学生找让雨水流进东边小水塘的落点。
const H37 = (x, y) => 3 - 0.02 * x * x - 0.05 * y * y, GH37 = (x, y) => [-0.04 * x, -0.10 * y];
const OBS37 = [[5, 1.7], [5, 2.4], [5, 3.1]], RHO37 = 1.2, ST37 = [1, 2.4];
function apf37(gy, kr, vort) {
  let p = [...ST37]; const path = [[...p]]; let dmin = 9;
  for (let i = 0; i < 1200; i++) {
    if (Math.hypot(p[0] - 9, p[1] - gy) < 0.05) return { path, ok: true, steps: i, dmin };
    let G = [p[0] - 9, p[1] - gy];
    OBS37.forEach(([ox, oy]) => { const dx = p[0] - ox, dy = p[1] - oy, r = Math.hypot(dx, dy);
      if (r < RHO37) { const m = kr * (1 / r - 1 / RHO37) / (r * r); G = [G[0] - m * dx / r + vort * m * dy / r, G[1] - m * dy / r - vort * m * dx / r]; } });
    const n = Math.hypot(G[0], G[1]) || 1; p = [p[0] - 0.05 * G[0] / n, p[1] - 0.05 * G[1] / n]; path.push([...p]);
    OBS37.forEach(([ox, oy]) => { dmin = Math.min(dmin, Math.hypot(p[0] - ox, p[1] - oy)); });
  }
  return { path, ok: false, steps: 1200, dmin };
}
const Z37 = (x, y) => -1.5 * Math.exp(-((x - 3) ** 2 + (y - 2.5) ** 2) / 5) - 0.9 * Math.exp(-((x - 8) ** 2 + (y - 2) ** 2) / 1.5);
const LAKES37 = [[3, 2.5], [8, 2]];
function rain37(x, y) {
  const path = [[x, y]], e = 1e-5;
  for (let i = 0; i < 800; i++) {
    const gx = (Z37(x + e, y) - Z37(x - e, y)) / (2 * e), gy = (Z37(x, y + e) - Z37(x, y - e)) / (2 * e), n = Math.hypot(gx, gy) || 1;
    x -= 0.04 * gx / n; y -= 0.04 * gy / n; path.push([x, y]);
    for (let k = 0; k < 2; k++) if (Math.hypot(x - LAKES37[k][0], y - LAKES37[k][1]) < 0.2) return { path, lake: k };
  }
  return { path, lake: -1 };
}
const rad37 = (d) => d * Math.PI / 180;
function slope37(p) { const g = GH37(p.px, p.py), D = g[0] * Math.cos(rad37(p.phi)) + g[1] * Math.sin(rad37(p.phi)); return { g, D, deg: Math.atan(D) * 180 / Math.PI, gmax: Math.atan(Math.hypot(g[0], g[1])) * 180 / Math.PI }; }

WQ.lab({
  title: ["实验 3.7 梯度与势场导航", "Lab 3.7 Gradients and potential-field navigation"],
  goal: ["在等高线地图上看梯度和方向导数，选一个坡度合适的方向；用人工势场让 AGV 绕开障碍，找出会卡住的局部极小；看雨水沿负梯度流向哪里。",
         "See gradients and directional derivatives on a contour map and pick a direction of suitable slope; steer an AGV round obstacles with a potential field and find where it gets stuck; follow rain down the negative gradient."],
  scenes: [
    { id: "hill", robot: true, name: ["土丘上的坡度", "Slopes on a hill"], hide: ["kr", "gy", "vort", "rx", "ry"],
      problem: { title: ["机器人问题：朝哪个方向能开上去", "Robot problem: which way can the robot climb"],
                 text: ["巡检机器人在土丘上，地面高度 H = 3.0 − 0.02x² − 0.05y²（m），最多能爬 15° 的坡。红箭头是梯度 ∇H，蓝箭头是行驶方向 φ。转动 φ，读出这个方向的坡度 = arctan(∇H·û)。",
                        "The inspection robot is on a hill H = 3.0 − 0.02x² − 0.05y² (m) and can climb at most 15°. The red arrow is ∇H, the blue arrow the heading φ. Turn φ and read the slope arctan(∇H·û) in that direction."] } },
    { id: "apf", robot: true, name: ["势场导航", "Potential-field navigation"], hide: ["px", "py", "phi", "rx", "ry"],
      problem: { title: ["机器人问题：沿负梯度开到目标", "Robot problem: driving down the gradient to the goal"],
                 text: ["AGV 从左边出发去右边的目标（绿星），中间三根立柱排成一道过不去的墙。AGV 每一步沿势的负梯度走 5 cm。改变目标的位置、斥力强度和绕行（切向）分量。",
                        "The AGV starts on the left and heads for the goal (green star); three pillars form an impassable wall in between. Each step it moves 5 cm down the negative gradient of the potential. Change the goal position, the repulsion and the swirl (tangential) part."] } },
    { id: "rain", name: ["雨水往哪里流", "Where does the rain flow"], hide: ["px", "py", "phi", "kr", "gy", "vort"],
      problem: { title: ["生活中的例子：分水岭", "Everyday example: watersheds"],
                 text: ["一片山坡上有两个水塘。雨滴总是沿负梯度（最陡的下坡）流动。移动雨滴的落点，看它流进哪个水塘。",
                        "A hillside has two ponds. A raindrop always runs down the negative gradient (steepest descent). Move where it lands and see which pond it reaches."] } },
  ],
  params: [
    { id: "px", name: ["机器人位置 x", "Robot x"], min: -7, max: 7, step: 0.5, value: 5, unit: "m", digits: 1 },
    { id: "py", name: ["机器人位置 y", "Robot y"], min: -5, max: 5, step: 0.5, value: 3, unit: "m", digits: 1 },
    { id: "phi", name: ["行驶方向 φ（从 x 轴逆时针）", "Heading φ (from x, anticlockwise)"], min: 0, max: 359, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "kr", name: ["斥力强度 k_r", "Repulsion k_r"], min: 0.2, max: 4, step: 0.1, value: 1, unit: "", digits: 1 },
    { id: "gy", name: ["目标位置 y_g", "Goal y_g"], min: 0.3, max: 4.6, step: 0.1, value: 0.5, unit: "m", digits: 1 },
    { id: "vort", name: ["绕行（切向）分量", "Swirl (tangential) part"], min: 0, max: 1, step: 0.1, value: 0, unit: "", digits: 1 },
    { id: "rx", name: ["雨滴落点 x", "Raindrop x"], min: 0.2, max: 9.8, step: 0.1, value: 5, unit: "m", digits: 1 },
    { id: "ry", name: ["雨滴落点 y", "Raindrop y"], min: 0.2, max: 4.8, step: 0.1, value: 4, unit: "m", digits: 1 },
  ],
  buttons: [],
  tasks: [
    { id: "up", robot: true, text: ["土丘：在 (5, 3) 处找一个上坡方向，坡度在 5°～15° 之间。它与梯度的夹角大约是多少？",
                                   "Hill: at (5, 3) find an uphill heading with a slope between 5° and 15°. Roughly what angle does it make with the gradient?"],
      demo: { scene: "hill", set: { px: 5, py: 3, phi: 296 }, press: [], wait: 1 } },
    { id: "lev", robot: true, text: ["土丘：找一个坡度几乎为零（小于 0.5°）的方向。它与等高线、与梯度各是什么关系？",
                                    "Hill: find a heading with almost no slope (below 0.5°). How does it relate to the contour and to the gradient?"],
      demo: { scene: "hill", set: { px: 5, py: 3, phi: 326 }, press: [], wait: 1 } },
    { id: "arr", robot: true, text: ["势场：让 AGV 绕过立柱墙到达目标。", "Potential field: get the AGV round the wall to the goal."],
      demo: { scene: "apf", set: { gy: 0.5, kr: 1, vort: 0 }, press: [], wait: 1 } },
    { id: "stuck", robot: true, text: ["势场：没有绕行分量时，把目标移到墙的正后方附近，AGV 停在哪里？那里的 ∇U 等于多少？",
                                      "Potential field: with no swirl, move the goal to just behind the wall. Where does the AGV stop, and what is ∇U there?"],
      demo: { scene: "apf", set: { gy: 2.4, kr: 1, vort: 0 }, press: [], wait: 1 } },
    { id: "esc", robot: true, text: ["势场：目标仍在墙后（y_g 在 1.5～2.8 m 之间），加一点绕行分量，让 AGV 绕出来到达目标。",
                                    "Potential field: with the goal still behind the wall (y_g between 1.5 and 2.8 m), add some swirl so the AGV escapes and reaches the goal."],
      demo: { scene: "apf", set: { gy: 2.4, kr: 1, vort: 0.6 }, press: [], wait: 1 } },
    { id: "rain", text: ["雨水：找一个落点，让雨水流进东边（右边）的小水塘。在两个落点之间的分界线（分水岭）上，梯度是什么样的？",
                         "Rain: find a landing point from which the water reaches the small pond on the east (right). What does the gradient look like on the dividing line (watershed)?"],
      demo: { scene: "rain", set: { rx: 8.5, ry: 4 }, press: [], wait: 1 } },
  ],
  think: ["势场导航为什么会卡住？卡住的点上吸引力和斥力是什么关系？绕行分量为什么有时能帮忙、有时反而让 AGV 卡在别处（试试 y_g = 4.2 m）？",
          "Why does potential-field navigation get stuck, and how do the attraction and repulsion compare there? Why does the swirl sometimes help and sometimes trap the AGV elsewhere (try y_g = 4.2 m)?"],

  reset(api, s) {},
  change(api, s, pid) {
    const p = api.p;
    if (api.scene === "hill") { const S = slope37(p); if (p.px === 5 && p.py === 3) { if (S.deg >= 5 && S.deg <= 15) api.done("up"); if (Math.abs(S.deg) < 0.5) api.done("lev"); } }
    if (api.scene === "apf") { const A = apf37(p.gy, p.kr, p.vort); if (A.ok && A.dmin > 0.25) api.done("arr");
      if (!A.ok && !p.vort) api.done("stuck"); if (A.ok && p.vort > 0 && p.gy >= 1.5 && p.gy <= 2.8) api.done("esc"); }
    if (api.scene === "rain" && rain37(p.rx, p.ry).lake === 1) api.done("rain");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p;
    if (api.scene === "hill") { const S = slope37(p);
      return [[["高度 H", "Height H"], f(H37(p.px, p.py), 2) + " m"], [["梯度 ∇H", "Gradient ∇H"], `(${f(S.g[0], 2)}, ${f(S.g[1], 2)})`], [["最陡的坡度", "Steepest slope"], f(S.gmax, 1) + "°"],
        [["方向导数 ∇H·û", "Directional derivative ∇H·û"], f(S.D, 3)], [["这个方向的坡度", "Slope this way"], f(S.deg, 1) + "°" + (S.deg > 15 ? api.T("（太陡）", " (too steep)") : S.deg < 0 ? api.T("（下坡）", " (downhill)") : "")]]; }
    if (api.scene === "apf") { const A = apf37(p.gy, p.kr, p.vort), e = A.path[A.path.length - 1];
      return [[["结果", "Result"], A.ok ? api.T("到达目标", "reached the goal") : api.T("卡住了", "stuck")], [["步数", "Steps"], String(A.steps)],
        [["离立柱中心最近", "Closest to a pillar"], f(A.dmin, 2) + " m"], [["终点", "End point"], `(${f(e[0], 2)}, ${f(e[1], 2)}) m`]]; }
    const R = rain37(p.rx, p.ry);
    return [[["落点高度", "Height where it lands"], f(Z37(p.rx, p.ry), 2) + " m"], [["流进", "Ends in"], R.lake === 0 ? api.T("西边的大水塘", "the big west pond") : R.lake === 1 ? api.T("东边的小水塘", "the small east pond") : "—"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, mut = css("--muted"), ink = css("--ink"), red = css("--red"), blue = css("--blue"), green = css("--green");
    if (api.scene === "hill") {
      const sc = Math.min((w - 80) / 16, (h - 80) / 12), G = api.graph({ x: 50, y: 20, w: 16 * sc, h: 12 * sc, xmin: -8, xmax: 8, ymin: -6, ymax: 6, xlabel: "x / m", ylabel: "y / m" }).axes();
      const c = api.ctx; c.save(); c.beginPath(); c.rect(G.o.x, G.o.y, G.o.w, G.o.h); c.clip(); c.strokeStyle = mut; c.lineWidth = 0.8;
      for (let lv = 0.25; lv < 3; lv += 0.25) { c.beginPath(); c.ellipse(G.X(0), G.Y(0), Math.sqrt(50 * (3 - lv)) * sc, Math.sqrt(20 * (3 - lv)) * sc, 0, 0, 2 * Math.PI); c.stroke(); }
      c.restore();
      const S = slope37(p), x0 = G.X(p.px), y0 = G.Y(p.py), L = 60 / Math.hypot(S.g[0], S.g[1] || 1e-9);
      api.circle(x0, y0, 6, ink);
      if (Math.hypot(S.g[0], S.g[1]) > 1e-9) { api.arrow(x0, y0, x0 + S.g[0] * L, y0 - S.g[1] * L, red, 3); api.label("∇H", x0 + S.g[0] * L * 1.25, y0 - S.g[1] * L * 1.25, red, 14, "center"); }
      api.arrow(x0, y0, x0 + 55 * Math.cos(rad37(p.phi)), y0 - 55 * Math.sin(rad37(p.phi)), blue, 3);
      api.label("û", x0 + 70 * Math.cos(rad37(p.phi)), y0 - 70 * Math.sin(rad37(p.phi)) + 5, blue, 14, "center");
      api.label(api.T("等高线每 0.25 m 一条，中心最高（3 m）", "contours every 0.25 m; summit 3 m at the centre"), G.o.x, G.o.y + G.o.h + 34, mut, 11);
      return;
    }
    if (api.scene === "apf") {
      const sc = Math.min((w - 80) / 10, (h - 60) / 5), G = api.graph({ x: 50, y: 20, w: 10 * sc, h: 5 * sc, xmin: 0, xmax: 10, ymin: 0, ymax: 5, xlabel: "x / m", ylabel: "y / m" }).axes();
      OBS37.forEach(([ox, oy]) => { api.circle(G.X(ox), G.Y(oy), RHO37 * sc, null, mut); api.circle(G.X(ox), G.Y(oy), 0.2 * sc, ink); });
      const A = apf37(p.gy, p.kr, p.vort); G.pts(A.path, A.ok ? green : red, 2.5);
      const e = A.path[A.path.length - 1]; api.agv(G.X(e[0]), G.Y(e[1]), 30);
      G.point(ST37[0], ST37[1], blue, api.T("起点", "start")); api.label("★", G.X(9), G.Y(p.gy) + 7, green, 22, "center");
      api.label(api.T("灰圈：斥力作用范围", "grey circles: reach of the repulsion"), G.o.x, G.o.y + G.o.h + 40, mut, 11);
      return;
    }
    const sc = Math.min((w - 80) / 10, (h - 60) / 5), G = api.graph({ x: 50, y: 20, w: 10 * sc, h: 5 * sc, xmin: 0, xmax: 10, ymin: 0, ymax: 5, xlabel: "x / m", ylabel: "y / m" }).axes();
    for (let i = 0; i < 50; i++) for (let j = 0; j < 25; j++) { const x = (i + 0.5) / 5, y = (j + 0.5) / 5, z = Z37(x, y);
      api.rect(G.X(x - 0.1), G.Y(y + 0.1), 0.2 * sc + 1, 0.2 * sc + 1, `rgba(31,119,180,${Math.min(0.55, -z / 3).toFixed(3)})`); }
    LAKES37.forEach(([x, y], k) => api.circle(G.X(x), G.Y(y), (k ? 0.3 : 0.5) * sc, "rgba(31,119,180,0.6)", ink));
    const R = rain37(p.rx, p.ry); G.pts(R.path, red, 2.5); G.point(p.rx, p.ry, red, api.T("落点", "lands here"));
    api.label(api.T("颜色越深越低", "darker is lower"), G.o.x, G.o.y + G.o.h + 40, mut, 11);
  },
});
