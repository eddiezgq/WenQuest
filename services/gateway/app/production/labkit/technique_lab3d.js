// TECHNIQUE EXAMPLE (3D) — how a 3D lab is written: view: "3d" + models (library ids listed for the course),
// setup3d(api, keep) once the models are loaded (trace, frames, camera; `keep` = api.keep survives reset),
// sliders drive joints in draw(), readouts use the
// robot's own base frame (Z up, metres) via h.toolLocal(). Its texts are placeholders: never copy them.
WQ.lab({
  title: ["（占位）本课三维实验标题", "(placeholder) This lesson's 3D lab title"],
  goal: ["（占位）一句话：学生应该看到什么。", "(placeholder) One sentence: what the student should see."],
  view: "3d",
  models: ["B-ARM-6R-S"],
  scenes: [
    { id: "robot", robot: true, name: ["（占位）机器人场景", "(placeholder) Robot scene"],
      problem: { title: ["机器人问题：（占位）", "Robot problem: (placeholder)"], text: ["（占位）本课的机器人问题。", "(placeholder) This lesson's robot problem."] } },
    { id: "life", name: ["（占位）生活场景", "(placeholder) Everyday scene"],
      problem: { title: ["生活中的例子：（占位）", "Everyday example: (placeholder)"], text: ["（占位）生活中的同类问题。", "(placeholder) The same idea in everyday life."] } },
  ],
  params: [
    { id: "q1", name: ["关节 1 角度 θ₁", "Joint 1 θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "q2", name: ["关节 2 角度 θ₂", "Joint 2 θ₂"], min: -150, max: 0, step: 1, value: -70, unit: "°", digits: 0 },
    { id: "q3", name: ["关节 3 角度 θ₃", "Joint 3 θ₃"], min: 0, max: 160, step: 1, value: 85, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["扫一圈", "Sweep"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "high", robot: true, text: ["（占位）让末端高于 0.60 m。", "(placeholder) Raise the tool above 0.60 m."],
      demo: { scene: "robot", set: { q1: 0, q2: -100, q3: 40 }, press: [], wait: 1 } },
    { id: "far", robot: true, text: ["（占位）让末端离基座轴线超过 0.75 m。", "(placeholder) Reach more than 0.75 m from the base axis."],
      demo: { scene: "robot", set: { q1: 0, q2: -20, q3: 10 }, press: [], wait: 1 } },
    { id: "sweep", text: ["（占位）让关节 1 扫一整圈，看末端轨迹。", "(placeholder) Sweep joint 1 once round and watch the trace."],
      demo: { scene: "life", set: {}, press: ["start"], wait: 7 } },
  ],
  think: ["（占位）一个值得思考的问题。", "(placeholder) A question to think about."],

  setup3d(api, keep) {
    const arm = api.m["B-ARM-6R-S"];
    api.axes(arm, "base", 0.15);                 // base frame
    api.axes(arm, "wrist3", 0.08);               // tool frame
    keep.trace = api.trace(0xe8913a);            // lives in api.keep: reset() starts a fresh state
    api.view(40, 22, 0.9);
  },
  reset(api, s) { s.sweep = 0; if (api.keep.trace) api.keep.trace.clear(); },
  update(dt, api, s) {
    s.sweep += dt * 60;                          // degrees per second
    if (s.sweep >= 360) { api.stop(); api.done("sweep"); }
  },
  pose(api, s) {
    const d = Math.PI / 180;
    return { shoulder_pan: (api.p.q1 + (api.running ? s.sweep : 0)) * d, shoulder_lift: api.p.q2 * d, elbow: api.p.q3 * d, wrist_1: -1.6 };
  },
  readouts(api, s) {
    const arm = api.m["B-ARM-6R-S"];
    if (!arm) return [];
    arm.set(this.pose(api, s));
    const [x, y, z] = arm.toolLocal();
    if (z > 0.6) api.done("high");
    if (Math.hypot(x, y) > 0.75) api.done("far");
    return [[["末端 x", "tool x"], api.fmt(x, 3) + " m"], [["末端 y", "tool y"], api.fmt(y, 3) + " m"],
            [["末端 z", "tool z"], api.fmt(z, 3) + " m"], [["到基座轴线", "from base axis"], api.fmt(Math.hypot(x, y), 3) + " m"]];
  },
  draw(api, s) {
    const arm = api.m["B-ARM-6R-S"];
    arm.set(this.pose(api, s));
    if (api.running) api.keep.trace.add(arm.tool());
  },
});
