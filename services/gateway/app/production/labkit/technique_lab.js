// TECHNIQUE EXAMPLE — shows HOW a WenQuest lab is written: state in reset(), the model in update(),
// measurements in readouts(), the picture in draw(), tasks ticked with api.done(), and a demo per task.
// Its content is a placeholder ("quantity q follows its set-point"): never copy its topic, texts or numbers.
// In a real lab, draw THIS course's robot or platform (api.arm, api.robot, api.frame, api.lidar, api.agv ...)
// and compute THIS lesson's formulas.
WQ.lab({
  title: ["（占位）本课实验标题", "(placeholder) This lesson's lab title"],
  goal: ["（占位）一句话：学生应该看到什么。", "(placeholder) One sentence: what the student should see."],
  scenes: [
    { id: "robot", robot: true, name: ["（占位）机器人场景", "(placeholder) Robot scene"],
      problem: { title: ["机器人问题：（占位）", "Robot problem: (placeholder)"],
                 text: ["（占位）本课的机器人问题，来自课程设计书和课时设计。", "(placeholder) This lesson's robot problem, from the design book and the lesson spec."] } },
    { id: "life", name: ["（占位）生活场景", "(placeholder) Everyday scene"], hide: ["k"],
      params: { target: { min: 0, max: 5, step: 0.1, value: 2 } },
      problem: { title: ["生活中的例子：（占位）", "Everyday example: (placeholder)"],
                 text: ["（占位）一个生活中的同类问题。", "(placeholder) The same idea in everyday life."] } },
  ],
  params: [
    { id: "target", name: ["设定值 q*", "Set-point q*"], min: 0, max: 10, step: 0.1, value: 5, unit: "", digits: 1 },
    { id: "k", name: ["响应速度 k", "Response rate k"], min: 0.2, max: 4, step: 0.1, value: 1, unit: "1/s", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--accent)", name: ["q(t)", "q(t)"] }, { color: "var(--amber)", name: ["设定值", "set-point"] }],
  tasks: [
    { id: "reach", robot: true, text: ["（占位）让 q 在 2 s 内达到设定值的 95%。", "(placeholder) Make q reach 95% of the set-point within 2 s."],
      demo: { scene: "robot", set: { target: 5, k: 2 }, press: ["start"], wait: 3 } },
    { id: "slow", robot: true, text: ["（占位）把 k 调小，观察 q 需要多久。", "(placeholder) Lower k and see how long q takes."],
      demo: { scene: "robot", set: { target: 5, k: 0.4 }, press: ["start"], wait: 3 } },
    { id: "life", text: ["（占位）生活场景：让 q 超过 1.5。", "(placeholder) Everyday scene: get q above 1.5."],
      demo: { scene: "life", set: { target: 3 }, press: ["start"], wait: 3 } },
  ],
  think: ["（占位）一个值得思考的问题。", "(placeholder) A question to think about."],

  reset(api, s) { s.q = 0; s.hist = [[0, 0]]; s.t95 = null; },
  update(dt, api, s) {
    const k = api.scene === "life" ? 1 : api.p.k;
    s.q += k * (api.p.target - s.q) * dt;            // the lesson's model, from its formula, with correct units
    s.hist.push([api.t, s.q]);
    if (s.t95 === null && api.p.target > 0 && s.q >= 0.95 * api.p.target) s.t95 = api.t;
    if (api.scene === "robot" && s.t95 !== null && s.t95 <= 2) api.done("reach");
    if (api.scene === "robot" && api.p.k <= 0.5 && api.t > 2) api.done("slow");
    if (api.scene === "life" && s.q > 1.5) api.done("life");
    if (api.t > 6) api.stop();
  },
  readouts(api, s) {
    return [[["当前 q", "q now"], api.fmt(s.q, 2)],
            [["达到 95% 用时", "Time to 95%"], s.t95 === null ? "—" : api.fmt(s.t95, 2) + " s"]];
  },
  draw(api, s) {
    const { w, h } = api, m = 12;
    // left: the scene (in a real lab: THIS course's robot, drawn from the state)
    const x0 = m + 20, x1 = w * 0.45, y = h * 0.62, span = x1 - x0;
    api.line(x0, y, x1, y, api.css("--ground"), 2);
    const xq = x0 + span * Math.min(1, s.q / 10), xt = x0 + span * Math.min(1, api.p.target / 10);
    api.line(xt, y - 40, xt, y + 10, api.css("--amber"), 2, [5, 4]);
    api.circle(xq, y - 14, 12, api.css("--accent"), api.css("--ink"));
    api.label("q = " + api.fmt(s.q, 2), xq, y - 40, api.css("--ink"), 13, "center");
    // right: the measured curve, with the set-point
    const px = w * 0.52, pw = w - px - m, py = m + 10, ph = h - 2 * m - 30;
    api.plot(px, py, pw, ph, [
      { pts: s.hist, color: api.css("--accent") },
      { pts: [[0, api.p.target], [6, api.p.target]], color: api.css("--amber") },
    ], { xmin: 0, xmax: 6, ymin: 0, ymax: 10, xlabel: "t / s", ylabel: "q" });
  },
});
