// 实验 7.9 相关变化率：云台相机跟踪 AGV（配 7.9 节）。相机在路线旁距离 d 处，θ = arctan(x/d)，所需角速度 vd/(d² + x²)（式 (7.9.1)）；
// 云台以不超过限速的转速转向目标方向。“生活中的例子”：路灯下行走的人与影子（7.9.4 节）。
WQ.lab({
  title: ["实验 7.9 相关变化率：云台相机跟踪 AGV", "Lab 7.9 Related rates: a pan camera tracking an AGV"],
  goal: ["改变相机到路线的距离、AGV 的速度和云台的限速，看云台能否全程跟住 AGV；在影子场景中验证影子顶端的速度。",
         "Change the camera's distance from the route, the AGV speed and the pan limit, and see whether the camera keeps the AGV centred; in the shadow scene check the speed of the shadow's tip."],
  scenes: [
    { id: "camera", robot: true, name: ["云台相机与 AGV", "Pan camera and AGV"], hide: ["H", "hp", "u"],
      problem: { title: ["机器人问题：云台跟得上吗？", "Robot problem: can the camera keep up?"],
                 text: ["AGV 经过相机正前方时，视线转得最快，所需角速度为 v/d。超过云台的限速，AGV 就会滑出画面中央。",
                        "The line of sight turns fastest as the AGV passes closest, at v/d. Above the pan limit the AGV slips out of the centre of the picture."] } },
    { id: "shadow", name: ["路灯下的影子", "Shadow under a street lamp"], hide: ["d", "v", "lim"],
      problem: { title: ["生活中的例子：影子的顶端", "Everyday example: the tip of a shadow"],
                 text: ["人从路灯下匀速走开，影子越来越长。影子的顶端移动得多快？它与人离路灯的远近有关吗？",
                        "A person walks steadily away from a lamp and the shadow grows. How fast does its tip move? Does that depend on how far the person is?"] } },
  ],
  params: [
    { id: "d", name: ["相机到路线的距离 d", "Camera distance d"], min: 1, max: 5, step: 0.1, value: 2, unit: "m", digits: 1 },
    { id: "v", name: ["AGV 速度 v", "AGV speed v"], min: 0.5, max: 3, step: 0.1, value: 1.5, unit: "m/s", digits: 1 },
    { id: "lim", name: ["云台限速", "Pan speed limit"], min: 0.2, max: 1.5, step: 0.05, value: 0.5, unit: "rad/s", digits: 2 },
    { id: "H", name: ["路灯高度 H", "Lamp height H"], min: 3, max: 8, step: 0.1, value: 6, unit: "m", digits: 1 },
    { id: "hp", name: ["人的身高", "Person's height"], min: 1.2, max: 2, step: 0.05, value: 1.8, unit: "m", digits: 2 },
    { id: "u", name: ["步速", "Walking speed"], min: 0.5, max: 2, step: 0.1, value: 1.4, unit: "m/s", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "lost", robot: true, text: ["按默认参数（d = 2 m，v = 1.5 m/s，限速 0.5 rad/s）运行一次，看云台在哪一段跟不上（最大偏差超过 5°）。", "Run once with the defaults (d = 2 m, v = 1.5 m/s, limit 0.5 rad/s) and see where the camera falls behind (largest lag above 5°)."],
      demo: { scene: "camera", set: { d: 2, v: 1.5, lim: 0.5 }, press: ["start"], wait: 10 } },
    { id: "track", robot: true, text: ["保持 v = 1.5 m/s、限速 0.5 rad/s，改变 d，使云台全程跟住 AGV（最大偏差小于 1°）。最小的 d 是多少？", "Keep v = 1.5 m/s and the 0.5 rad/s limit; change d until the camera tracks all the way (largest lag below 1°). What is the smallest d?"],
      demo: { scene: "camera", set: { d: 3.2, v: 1.5, lim: 0.5 }, press: ["start"], wait: 10 } },
    { id: "tip", text: ["取路灯高 6 m、人高 1.8 m、步速 1.4 m/s，走一趟，确认影子顶端的速度始终是 2 m/s。", "With a 6 m lamp, a 1.8 m person and 1.4 m/s, walk once and check that the shadow's tip always moves at 2 m/s."],
      demo: { scene: "shadow", set: { H: 6, hp: 1.8, u: 1.4 }, press: ["start"], wait: 6 } },
  ],
  think: ["为什么所需的转动角速度在正前方最大，而 AGV 在远处时很小？用 arctan 的导数 1/(1 + x²) 解释。", "Why is the required turning rate largest straight ahead and small far away? Explain with the derivative 1/(1 + x²) of arctan."],

  reset(api, s) {
    s.x = api.scene === "camera" ? -6 : 1; s.phi = Math.atan(s.x / api.p.d); s.err = 0; s.maxErr = 0; s.done = false;
    s.tipMin = Infinity; s.tipMax = -Infinity; s.tipV = NaN;
  },
  update(dt, api, s) {
    if (api.scene === "camera") {
      const { d, v, lim } = api.p;
      s.x += v * dt;
      const th = Math.atan(s.x / d);                                    // the pan turns towards the target as fast as its limit allows
      s.phi += Math.max(-lim * dt, Math.min(lim * dt, th - s.phi));
      s.err = Math.abs(th - s.phi) * 180 / Math.PI; s.maxErr = Math.max(s.maxErr, s.err);
      if (s.x >= 6) { s.done = true; api.stop(); }
    } else {
      const { H, hp, u } = api.p, k = hp / (H - hp), tip0 = s.x * (1 + k);
      s.x += u * dt;
      s.tipV = (s.x * (1 + k) - tip0) / dt;
      s.tipMin = Math.min(s.tipMin, s.tipV); s.tipMax = Math.max(s.tipMax, s.tipV);
      if (s.x >= 8) { s.done = true; api.stop(); }
    }
  },
  readouts(api, s) {
    if (api.scene === "camera") {
      const { d, v, lim } = api.p, need = v * d / (d * d + s.x * s.x);
      if (s.done && s.maxErr > 5) api.done("lost");
      if (s.done && s.maxErr < 1 && Math.abs(v - 1.5) < 0.01 && Math.abs(lim - 0.5) < 0.01) api.done("track");
      return [[["AGV 位置 x", "AGV position x"], api.fmt(s.x, 2) + " m"],
              [["所需角速度 vd/(d² + x²)", "Required rate vd/(d² + x²)"], api.fmt(need, 4) + " rad/s"],
              [["正前方所需的最大角速度 v/d", "Largest required rate v/d"], api.fmt(v / d, 4) + " rad/s"],
              [["云台偏差（当前 / 最大）", "Camera lag (now / largest)"], api.fmt(s.err, 2) + "° / " + api.fmt(s.maxErr, 2) + "°"]];
    }
    const { H, hp, u } = api.p, k = hp / (H - hp);
    if (s.done && Math.abs(H - 6) < 0.01 && Math.abs(hp - 1.8) < 0.01 && Math.abs(u - 1.4) < 0.01 && Math.abs(s.tipMax - 2) < 0.01 && Math.abs(s.tipMin - 2) < 0.01) api.done("tip");
    return [[["人离灯杆 x", "Distance from the lamp x"], api.fmt(s.x, 2) + " m"],
            [["影长 s", "Shadow length s"], api.fmt(k * s.x, 3) + " m"],
            [["影子顶端的速度（测得）", "Tip speed (measured)"], isFinite(s.tipV) ? api.fmt(s.tipV, 4) + " m/s" : "—"],
            [["公式 Hu/(H − h)", "Formula Hu/(H − h)"], api.fmt(H * u / (H - hp), 4) + " m/s"]];
  },
  draw(api, s) {
    const { w, h } = api, ink = api.css("--ink"), mu = api.css("--muted"), red = api.css("--red"), blue = api.css("--blue");
    if (api.scene === "camera") {
      const { d, v, lim } = api.p, sc = Math.min(w * 0.55 / 13, h * 0.75 / (d + 1.5)), ox = w * 0.3, oy = h * 0.18;
      const X = (x) => ox + sc * x, Y = (y) => oy + sc * y;
      api.line(X(-6.5), Y(0), X(6.5), Y(0), mu, 8);
      api.agv(X(s.x), Y(0) + 6, sc * 0.9, blue);
      const cx = X(0), cy = Y(d);
      api.rect(cx - 8, cy - 8, 16, 16, ink, null, 3);
      const len = sc * (d + 1), ex = cx + len * Math.sin(s.phi), ey = cy - len * Math.cos(s.phi);
      api.line(cx, cy, ex, ey, red, 2);
      api.line(cx, cy, X(s.x), Y(0), mu, 1, [4, 4]);
      api.label(api.T("相机", "camera"), cx + 12, cy + 4, ink, 12);
      const G = api.graph({ x: w * 0.64, y: h * 0.12, w: w * 0.33, h: h * 0.62, xmin: -6, xmax: 6, ymin: 0, ymax: Math.max(1.2 * v / d, 1.2 * lim),
        xlabel: "x / m", ylabel: api.T("所需角速度 / (rad/s)", "required rate / (rad/s)") });
      G.axes().fn((x) => v * d / (d * d + x * x), ink, 2).hline(lim, red, [6, 4]).vline(s.x, blue, [3, 3]);
      return;
    }
    const { H, hp } = api.p, sc = Math.min(w / 14, h * 0.8 / H), gx = w * 0.06, gy = h * 0.9, k = hp / (H - hp);
    api.ground(gy, w);
    api.line(gx, gy, gx, gy - sc * H, ink, 4);
    api.circle(gx + 6, gy - sc * H, 7, api.css("--amber"));
    const px = gx + sc * s.x, tip = gx + sc * s.x * (1 + k);
    api.line(px, gy, tip, gy, ink, 6);
    api.line(px, gy, px, gy - sc * hp, blue, 6);
    api.circle(px, gy - sc * hp - 6, 6, blue);
    api.line(gx + 6, gy - sc * H, tip, gy, api.css("--amber"), 1, [5, 4]);
    api.circle(tip, gy, 4, red);
    api.label(api.T("影子顶端", "shadow tip"), tip, gy + 16, red, 12, "center");
  },
});
