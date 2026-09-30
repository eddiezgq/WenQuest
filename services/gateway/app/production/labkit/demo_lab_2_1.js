// Lesson 2.1 Newton's first law and inertia — AGV emergency stop (robot) and a braking bus (everyday).
// The house example for the lab engineer: physics in update(), pictures in draw(), tasks ticked with api.done().
const g = 9.8;
WQ.lab({
  title: ["惯性与急停", "Inertia and emergency stops"],
  goal: ["看清惯性：车停下时，车上的物体为什么会“往前冲”，什么条件下货箱会在 AGV 上滑动。",
         "See inertia at work: why things on a braking vehicle “lurch forward”, and when a crate slides on a braking AGV."],
  scenes: [
    { id: "robot", robot: true, name: ["AGV 急停", "AGV emergency stop"],
      problem: { title: ["机器人问题：AGV 急停时货箱会不会滑？", "Robot problem: will the crate slide when the AGV stops hard?"],
                 text: ["仓库 AGV 以 v₀ 行驶，前方突然有人，AGV 以减速度 a 刹车。货箱与车板之间的摩擦系数为 μ。刹多猛货箱才不滑？",
                        "A warehouse AGV runs at v₀ when someone steps out; it brakes at a. The crate–deck friction coefficient is μ. How hard can it brake without the crate sliding?"] } },
    { id: "life", name: ["公交车急刹", "A bus brakes"], hide: ["mu"],
      params: { v0: { min: 5, max: 15, step: 0.5, value: 10 }, a: { min: 0.5, max: 6, step: 0.1, value: 2 } },
      problem: { title: ["生活中的例子：", "Everyday example: "],
                 text: ["公交车急刹车时，站着的乘客往前倾，吊环也向前摆。刹得越猛，吊环摆得越大吗？",
                        "When a bus brakes hard, standing passengers lean forward and the hand straps swing forward. Does a harder stop swing them further?"] } },
  ],
  params: [
    { id: "v0", name: ["初速度 v₀", "Initial speed v₀"], min: 0.5, max: 2, step: 0.1, value: 1.5, unit: "m/s", digits: 1 },
    { id: "a", name: ["刹车减速度 a", "Braking deceleration a"], min: 0.5, max: 6, step: 0.1, value: 2, unit: "m/s²", digits: 1 },
    { id: "mu", name: ["货箱与车板的摩擦系数 μ", "Crate–deck friction μ"], min: 0.1, max: 0.8, step: 0.01, value: 0.3, digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始刹车", "Brake now"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--orange)", name: ["速度", "velocity"] }, { color: "var(--red)", name: ["摩擦力", "friction"] }],
  tasks: [
    { id: "slide", robot: true, text: ["让货箱在 AGV 刹车时滑动起来。", "Make the crate slide when the AGV brakes."],
      demo: { scene: "robot", set: { v0: 1.5, a: 5, mu: 0.3 }, press: ["start"], wait: 3 } },
    { id: "safe", robot: true, text: ["μ = 0.3 时，用尽量大的减速度（不小于 0.8μg）停车而货箱不滑。", "With μ = 0.3, stop as hard as you can (at least 0.8μg) without the crate sliding."],
      demo: { scene: "robot", set: { v0: 1.5, a: 2.6, mu: 0.3 }, press: ["start"], wait: 3 } },
    { id: "strap", text: ["公交车：让吊环前倾超过 20°，读出这时的减速度。", "Bus: make the hand strap swing forward past 20° and read the deceleration."],
      demo: { scene: "life", set: { v0: 10, a: 4 }, press: ["start"], wait: 4 } },
  ],
  think: ["思考：货箱“往前冲”，是有一个向前的力推它吗？在地面上看，货箱其实在做什么？",
          "Think: is there a force pushing the crate forward? Seen from the ground, what is the crate actually doing?"],

  reset(api, s) {
    s.xa = 0; s.va = api.p.v0; s.xb = 0; s.vb = api.p.v0; s.rel = 0; s.maxRel = 0; s.fell = false;
    s.theta = 0; s.omega = 0; s.maxTheta = 0; s.finished = false;
  },
  update(dt, api, s) {
    const a = api.p.a, mu = api.p.mu;
    s.va = Math.max(0, s.va - a * dt);
    s.xa += s.va * dt;
    if (api.scene === "robot") {
      // The crate moves with the deck while static friction can give it the AGV's deceleration (a ≤ μg);
      // otherwise it slides and kinetic friction μg slows it until it moves with the deck again.
      if (s.vb > s.va + 1e-9 || a > mu * g) {
        if (s.va > 0 || s.vb > 0) s.vb = Math.max(s.va, s.vb - mu * g * dt);
      } else {
        s.vb = s.va;
      }
      if (!s.fell) s.xb += s.vb * dt;
      s.rel = s.xb - s.xa; s.maxRel = Math.max(s.maxRel, s.rel);
      if (s.rel > 0.35) s.fell = true;
      if (s.va === 0 && s.vb <= s.va + 1e-9) finish(api, s);
    } else {
      // Hand strap: while braking it settles at tanθ = a/g (seen in the bus), then swings back.
      const target = s.va > 0 ? Math.atan(a / g) : 0;
      s.omega += (30 * (target - s.theta) - 5 * s.omega) * dt;
      s.theta += s.omega * dt;
      s.maxTheta = Math.max(s.maxTheta, s.theta);
      if (s.va === 0 && Math.abs(s.theta) < 0.01 && Math.abs(s.omega) < 0.05) finish(api, s);
    }
  },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "robot") {
      const verdict = s.fell ? ["货箱掉下车板", "crate fell off"] : s.maxRel > 0.005 ? ["滑动", "slid"] : ["没有滑动", "no sliding"];
      return [
        [["AGV 速度", "AGV speed"], f(s.va, 2) + " m/s"],
        [["货箱速度（对地）", "Crate speed (ground)"], f(s.vb, 2) + " m/s"],
        [["μg（不滑的最大减速度）", "μg (largest stop without sliding)"], f(api.p.mu * g, 2) + " m/s²"],
        [["货箱相对车板滑动", "Crate slide on the deck"], f(s.maxRel * 100, 1) + " cm"],
        [["结论", "Result"], s.finished || s.fell ? api.P(verdict) : "—"],
      ];
    }
    return [
      [["车速", "Bus speed"], f(s.va * 3.6, 1) + " km/h"],
      [["吊环前倾角", "Strap angle"], f(s.theta * 180 / Math.PI, 1) + "°"],
      [["最大前倾角", "Largest angle"], f(s.maxTheta * 180 / Math.PI, 1) + "°"],
      [["理论值 arctan(a/g)", "Theory arctan(a/g)"], f(Math.atan(api.p.a / g) * 180 / Math.PI, 1) + "°"],
    ];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    const y0 = h * 0.78;
    if (api.scene === "robot") {
      const ppm = w / 3.2, ax = w * 0.42;
      api.grid(w, y0, 40);
      api.ground(y0, w, s.xa * ppm, 40);
      const aw = 1.0 * ppm, deck = y0 - aw * 0.33;
      api.agv(ax, y0, aw);
      const bs = 0.3 * ppm, bx = ax - 0.1 * ppm + Math.min(s.rel, 0.5) * ppm;
      const by = s.fell ? y0 : deck;
      api.box(bx, by, bs, css("--amber"));
      if (s.va > 0) api.arrow(ax - aw * 0.1, y0 - aw * 0.6, ax - aw * 0.1 + s.va * 60, y0 - aw * 0.6, css("--orange"), 3);
      if (s.vb > s.va + 1e-6) {
        api.arrow(bx, by - bs - 12, bx + s.vb * 60, by - bs - 12, css("--orange"), 3);
        api.arrow(bx, by - bs / 2, bx - 40, by - bs / 2, css("--red"), 3);
      }
      api.label(api.T("地面参考系（镜头跟随 AGV）", "Ground frame (camera follows the AGV)"), 12, 18, css("--muted"), 13);
      api.label(`a = ${api.fmt(api.p.a, 1)} m/s²   μg = ${api.fmt(api.p.mu * g, 2)} m/s²`, w - 12, 18,
                api.p.a > api.p.mu * g ? css("--red") : css("--green"), 13, "right");
    } else {
      const ppm = w / 16, bx0 = w * 0.18, bl = 11 * ppm, bh = 3.0 * ppm;
      api.ground(y0, w, s.xa * ppm, 60);
      api.rect(bx0, y0 - bh - 0.5 * ppm, bl, bh, css("--panel"), css("--ink"), 10);
      for (let i = 0; i < 5; i++) api.rect(bx0 + 0.6 * ppm + i * 2.1 * ppm, y0 - bh - 0.2 * ppm, 1.6 * ppm, 1.1 * ppm, css("--water"), css("--water-line"), 4);
      api.circle(bx0 + 2 * ppm, y0 - 0.45 * ppm, 0.45 * ppm, css("--ink")); api.circle(bx0 + 9 * ppm, y0 - 0.45 * ppm, 0.45 * ppm, css("--ink"));
      // a hand strap and a standing passenger inside, both tilted by theta
      const px = bx0 + 6 * ppm, py = y0 - bh - 0.3 * ppm, len = 1.2 * ppm, th = s.theta;
      const sx = px + Math.sin(th) * len, sy = py + Math.cos(th) * len;
      api.line(px, py, sx, sy, css("--ink"), 2); api.circle(sx, sy + 6, 7, null, css("--ink"));
      const fx = bx0 + 4 * ppm, fy = y0 - 0.6 * ppm, bodyL = 1.4 * ppm, lean = th * 0.8;
      const hx = fx + Math.sin(lean) * bodyL, hy = fy - Math.cos(lean) * bodyL;
      api.line(fx, fy, hx, hy, css("--accent"), 5); api.circle(hx + Math.sin(lean) * 10, hy - 10, 9, css("--accent"));
      api.label(api.T("在车厢里看：吊环向前摆", "Seen inside the bus: the strap swings forward"), 12, 18, css("--muted"), 13);
      if (s.va > 0) api.arrow(bx0 + bl * 0.5, y0 - bh - 0.9 * ppm, bx0 + bl * 0.5 + s.va * 8, y0 - bh - 0.9 * ppm, css("--orange"), 3);
      api.label(`θ = ${api.fmt(th * 180 / Math.PI, 1)}°`, px + 18, py + len * 0.5, css("--red"), 14);
    }
  },
});

function finish(api, s) {
  if (s.finished) return;
  s.finished = true;
  api.stop();
  if (api.scene === "robot") {
    if (s.maxRel > 0.02) api.done("slide");
    if (s.maxRel < 0.005 && Math.abs(api.p.mu - 0.3) < 0.011 && api.p.a >= 0.8 * api.p.mu * g) api.done("safe");
  } else if (s.maxTheta * 180 / Math.PI > 20) {
    api.done("strap");
  }
}
