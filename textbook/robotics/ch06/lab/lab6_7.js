// 实验 6.7 李括号：交替运动得到侧移（配 6.7 节）。差速 AGV（或轮椅）依次执行：前进 d、左转 a、后退 d、右转 a，
// 重复 n 次。物体运动旋量 V_f = (0,0,0, 1,0,0)（前进）与 V_r = (0,0,1, 0,0,0)（原地左转）的李括号
// [V_f, V_r] = (0,0,0, 0,−1,0)：沿 −y 方向（向右）平移。每做一组，净位移 ≈ d·a·[V_f, V_r]（式 (6.7.8)）。
WQ.lab({
  title: ["实验 6.7 李括号：交替运动得到侧移", "Lab 6.7 The Lie bracket: sideways by alternating motions"],
  goal: ["验证两个运动交替进行的净效果是它们的李括号：差速 AGV 不能侧移，却可以由“前进—转—后退—转回”横向挪动，侧移量约为 d·a。",
         "Check that alternating two motions gives their Lie bracket: a differential AGV cannot slide, yet forward–turn–back–turn-back moves it sideways by about d·a."],
  scenes: [
    { id: "agv", robot: true, name: ["差速 AGV 横向靠站", "Differential AGV docking sideways"],
      problem: { title: ["机器人问题：AGV 怎样横向对准工位", "Robot problem: lining an AGV up sideways"],
                 text: ["AGV 已经停在工位前，但偏左了几厘米。它的两个轮子不能侧滑，不能直接向右平移。怎样用前进、后退和原地转向把它挪过去？",
                        "The AGV stopped at the station a few centimetres too far left. Its wheels cannot slide, so it cannot just move right. How can driving and spinning shift it across?"] } },
    { id: "chair", name: ["轮椅靠近桌边", "A wheelchair edging to a desk"],
      problem: { title: ["生活中的例子：轮椅横向靠桌", "Everyday example: edging a wheelchair to a desk"],
                 text: ["电动轮椅也是差速驱动。坐轮椅的人想向右靠近桌边 0.1 m，就要来回几次“前进—转—后退—转回”。",
                        "A powered wheelchair is differential-drive too. To edge 0.1 m to the right towards a desk, the user goes forward–turn–back–turn-back a few times."] } },
  ],
  params: [
    { id: "d", name: ["每次前进、后退 d", "Drive distance d"], min: 0.05, max: 0.5, step: 0.05, value: 0.2, unit: "m", digits: 2 },
    { id: "a", name: ["每次转角 a", "Turn angle a"], min: 0.05, max: 0.6, step: 0.05, value: 0.2, unit: "rad", digits: 2 },
    { id: "n", name: ["重复次数 n", "Repeats n"], min: 1, max: 6, step: 1, value: 1, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "one", robot: true, text: ["d = 0.2 m、a = 0.2 rad，做一组：朝向复原，向右移了约 0.04 m。", "d = 0.2 m, a = 0.2 rad, one set: heading restored, about 0.04 m to the right."],
      demo: { scene: "agv", set: { d: 0.2, a: 0.2, n: 1 }, press: ["start"], wait: 5 } },
    { id: "half", robot: true, text: ["d、a 都减半（0.1 m、0.1 rad）：侧移约为原来的四分之一。", "Halve both (0.1 m, 0.1 rad): the side shift is about a quarter."],
      demo: { scene: "agv", set: { d: 0.1, a: 0.1, n: 1 }, press: ["start"], wait: 5 } },
    { id: "many", robot: true, text: ["d = 0.2 m、a = 0.2 rad，重复 5 组：侧移约 0.2 m，而朝向始终不变。", "d = 0.2 m, a = 0.2 rad, five sets: about 0.2 m sideways, heading unchanged."],
      demo: { scene: "agv", set: { d: 0.2, a: 0.2, n: 5 }, press: ["start"], wait: 14 } },
    { id: "chair", text: ["轮椅向右靠桌至少 0.1 m（朝向不变）。", "Edge the wheelchair at least 0.1 m right (heading unchanged)."],
      demo: { scene: "chair", set: { d: 0.25, a: 0.25, n: 2 }, press: ["start"], wait: 8 } },
  ],
  think: ["把动作顺序改为“左转—前进—右转—后退”，AGV 会向哪边移动？用 [V_r, V_f] = −[V_f, V_r] 解释。", "Change the order to turn-left, forward, turn-right, back. Which way does the AGV move? Explain with [V_r, V_f] = −[V_f, V_r]."],

  reset(api, s) { s.x = 0; s.y = 0; s.th = 0; s.step = 0; s.u = 0; s.trail = [[0, 0]]; s.finished = false; s.running = false; },
  start(api, s) { s.running = true; },
  update(dt, api, s) {
    if (!s.running || s.finished) return;
    const total = 4 * api.p.n, per = 0.25;          // 每个动作 0.25 s
    let left = dt;
    while (left > 0 && !s.finished) {
      const h = Math.min(left, (1 - s.u) * per), du = h / per, k = s.step % 4;
      if (k === 0 || k === 2) { const sg = k === 0 ? 1 : -1; s.x += sg * api.p.d * du * Math.cos(s.th); s.y += sg * api.p.d * du * Math.sin(s.th); }
      else s.th += (k === 1 ? 1 : -1) * api.p.a * du;
      s.u += du; left -= h;
      if (s.u >= 1 - 1e-12) { s.u = 0; s.step += 1; s.trail.push([s.x, s.y]); if (s.step >= total) { s.finished = true; api.stop(); } }
    }
  },
  readouts(api, s) {
    if (s.x === undefined) return [];
    const pred = -api.p.n * api.p.d * api.p.a, exact1 = -api.p.d * Math.sin(api.p.a);
    if (s.finished) {
      const ok = Math.abs(s.th) < 1e-9;
      if (api.scene === "agv" && ok && api.p.n === 1 && Math.abs(api.p.d - 0.2) < 1e-9 && Math.abs(api.p.a - 0.2) < 1e-9) api.done("one");
      if (api.scene === "agv" && ok && api.p.n === 1 && Math.abs(api.p.d - 0.1) < 1e-9 && Math.abs(api.p.a - 0.1) < 1e-9) api.done("half");
      if (api.scene === "agv" && ok && api.p.n === 5 && Math.abs(api.p.d - 0.2) < 1e-9 && Math.abs(api.p.a - 0.2) < 1e-9) api.done("many");
      if (api.scene === "chair" && ok && s.y <= -0.1) api.done("chair");
    }
    const f = (x) => api.fmt(x, 4);
    return [[["已完成的动作", "moves done"], `${s.step} / ${4 * api.p.n}`],
            [["净位移 (x, y)", "net displacement (x, y)"], `(${f(s.x)}, ${f(s.y)}) m`],
            [["朝向", "heading"], api.fmt(s.th * 180 / Math.PI, 2) + "°"],
            [["李括号的预测 −n·d·a", "bracket prediction −n·d·a"], f(pred) + " m"],
            [["一组的精确侧移 −d sin a", "exact shift per set −d sin a"], f(exact1) + " m"]];
  },
  draw(api, s) {
    if (s.x === undefined) return;
    const W = api.w, H = api.h, chair = api.scene === "chair";
    const k = Math.min(W / 1.6, H / 1.0), ox = W * 0.3, oy = H * 0.3;
    const X = (x) => ox + x * k, Y = (y) => oy - y * k;
    api.grid(W, H, k * 0.1);
    if (chair) { api.rect(X(-0.4), Y(-0.45), 1.2 * k, 0.12 * k, "rgba(201,143,0,0.25)", api.css("--amber"), 4); api.label(api.T("桌边（目标：向右 0.1 m）", "desk edge (goal: 0.1 m right)"), X(-0.38), Y(-0.51), api.css("--amber"), 12); api.line(X(-0.4), Y(-0.1), X(0.8), Y(-0.1), api.css("--amber"), 1, [5, 4]); }
    else { api.line(X(-0.4), Y(-0.04), X(0.8), Y(-0.04), api.css("--blue"), 1, [5, 4]); api.label(api.T("工位基准线（向右 0.04 m）", "station line (0.04 m right)"), X(0.3), Y(-0.04) + 14, api.css("--blue"), 12); }
    for (let i = 1; i < s.trail.length; i++) api.line(X(s.trail[i - 1][0]), Y(s.trail[i - 1][1]), X(s.trail[i][0]), Y(s.trail[i][1]), api.css("--red"), 1.8);
    api.line(X(s.trail[s.trail.length - 1][0]), Y(s.trail[s.trail.length - 1][1]), X(s.x), Y(s.y), api.css("--red"), 1.8);
    const size = (chair ? 0.16 : 0.13) * k;
    api.robot(X(0), Y(0), 0, size, "rgba(150,160,170,0.35)");
    api.robot(X(s.x), Y(s.y), s.th * 180 / Math.PI, size, chair ? api.css("--violet") : api.css("--accent"));
    if (s.finished) { api.arrow(X(0), Y(0), X(s.x), Y(s.y), api.css("--blue"), 2.5); }
    api.label(api.T("灰：起点；红线：车体中心的路径；蓝箭头：净位移", "grey: start; red: path of the centre; blue: net displacement"), 12, 18, api.css("--muted"), 12);
  },
});
