// 实验 10.5 切向加速度、法向加速度与曲率（配 10.5 节）。
// 场景 deburr：UR5e 工具尖沿半径 R 的圆去毛刺，从静止以切向加速度 a_t 加速到 v_max 后匀速（算例 10.5.1）；a_n = v²/R。
// 场景 glue：工具尖以恒定速率 v0 沿涂胶椭圆（a = 0.12 m，b = 0.08 m）运动，按弧长推进：du/dt = v0 / √(a² sin²u + b² cos²u)；
//   曲率 κ(u) = ab / (a² sin²u + b² cos²u)^{3/2}（式 (10.5.10)），a_n = κ v0²。
// 场景 road：汽车以车速 v 通过半径 R 的弯道，a_n = v²/R。
WQ.lab({
  title: ["实验 10.5 切向加速度、法向加速度与曲率", "Lab 10.5 Tangential and normal acceleration, curvature"],
  goal: ["沿轨迹的切线和法线分解加速度：切向部分改变速率，法向部分改变方向、等于曲率乘速率的平方。",
         "Split the acceleration along the tangent and normal of the path: the tangential part changes the speed, the normal part turns the direction and equals curvature times speed squared."],
  scenes: [
    { id: "deburr", robot: true, name: ["UR5e 去毛刺（圆）", "UR5e deburring (circle)"], hide: ["v0", "Rr", "vc"],
      problem: { title: ["机器人问题：起步时加速度有多大", "Robot problem: how large is the acceleration while speeding up"],
                 text: ["工具尖沿半径 0.1 m 的圆，从静止以 0.5 m/s² 加速到 0.25 m/s。加速结束时总加速度是多少？会不会突变？",
                        "The tool speeds up on a 0.1 m circle from rest at 0.5 m/s² to 0.25 m/s. What is the total acceleration when the speed-up ends? Does it jump?"] } },
    { id: "glue", robot: true, name: ["匀速涂胶（椭圆）", "Constant-speed gluing (ellipse)"], hide: ["R", "at", "vmax", "Rr", "vc"],
      problem: { title: ["机器人问题：匀速涂胶最快能多快", "Robot problem: how fast can the glue run at constant speed"],
                 text: ["工具尖以恒定速率沿椭圆涂胶，加速度不得超过 1.0 m/s²。最大加速度出现在哪里？",
                        "The tool glues the ellipse at constant speed; the acceleration may not exceed 1.0 m/s². Where is it largest?"] } },
    { id: "road", name: ["汽车过弯", "A car on a bend"], hide: ["R", "at", "vmax", "v0"],
      problem: { title: ["生活中的例子：高速公路的弯道", "Everyday example: a motorway bend"],
                 text: ["汽车匀速通过弯道，乘客为什么被推向外侧？车速与弯道半径怎样决定这个加速度？",
                        "Why are passengers pushed outward on a bend at steady speed? How do the speed and the radius set this acceleration?"] } },
  ],
  params: [
    { id: "R", name: ["圆的半径 R", "Circle radius R"], min: 0.05, max: 0.2, step: 0.01, value: 0.1, unit: "m", digits: 2 },
    { id: "at", name: ["切向加速度 a_t", "Tangential acceleration a_t"], min: 0.1, max: 1, step: 0.05, value: 0.5, unit: "m/s²", digits: 2 },
    { id: "vmax", name: ["最高速率 v_max", "Top speed v_max"], min: 0.05, max: 0.5, step: 0.01, value: 0.25, unit: "m/s", digits: 2 },
    { id: "v0", name: ["涂胶速率 v₀", "Gluing speed v₀"], min: 0.05, max: 0.4, step: 0.01, value: 0.2, unit: "m/s", digits: 2 },
    { id: "Rr", name: ["弯道半径", "Bend radius"], min: 100, max: 1000, step: 50, value: 500, unit: "m", digits: 0 },
    { id: "vc", name: ["车速", "Car speed"], min: 5, max: 40, step: 1, value: 30, unit: "m/s", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["切向 a_t", "tangential a_t"], color: "#1f77b4" }, { name: ["法向 a_n", "normal a_n"], color: "#2ca02c" }, { name: ["总加速度 |a|", "total |a|"], color: "#c0392b" }],
  tasks: [
    { id: "ex", robot: true, text: ["按算例 10.5.1 设置（R = 0.1 m，a_t = 0.5 m/s²，v_max = 0.25 m/s），运行，读出加速结束时的总加速度。",
                                    "Set Example 10.5.1 (R = 0.1 m, a_t = 0.5 m/s², v_max = 0.25 m/s), run, and read the total acceleration when the speed-up ends."],
      demo: { scene: "deburr", set: { R: 0.1, at: 0.5, vmax: 0.25 }, press: ["start"], wait: 4 } },
    { id: "limit", robot: true, text: ["半径 0.1 m 时，找一个不低于 0.2 m/s 的最高速率，使匀速段的法向加速度不超过 0.5 m/s²。",
                                       "With R = 0.1 m find a top speed of at least 0.2 m/s that keeps the normal acceleration of the steady part within 0.5 m/s²."],
      demo: { scene: "deburr", set: { R: 0.1, at: 0.5, vmax: 0.22 }, press: ["start"], wait: 4 } },
    { id: "glue", robot: true, text: ["匀速涂胶：找一个不低于 0.22 m/s 的速率，使走完一圈的最大加速度不超过 1.0 m/s²。",
                                      "Constant-speed gluing: find a speed of at least 0.22 m/s for which the largest acceleration over a loop stays within 1.0 m/s²."],
      demo: { scene: "glue", set: { v0: 0.23 }, press: ["start"], wait: 14 } },
    { id: "road", text: ["汽车以 30 m/s 通过半径 500 m 的弯道，读出法向加速度。", "A car at 30 m/s on a 500 m bend: read the normal acceleration."],
      demo: { scene: "road", set: { Rr: 500, vc: 30 }, press: [], wait: 1 } },
  ],
  think: ["算例 10.5.1 中，加速结束的瞬间总加速度为什么会突变？怎样修改速度规律才能避免（第 22 章的 S 形速度曲线）？",
          "In Example 10.5.1 why does the total acceleration jump the moment the speed-up ends? How could the speed law be changed to avoid it (the S-curve of Chapter 22)?"],

  A: 0.12, B: 0.08,
  kap(u) { const q = this.A * this.A * Math.sin(u) ** 2 + this.B * this.B * Math.cos(u) ** 2; return this.A * this.B / Math.pow(q, 1.5); },
  reset(api, s) { s.s = 0; s.v = 0; s.u = 0; s.hist = []; s.maxan = 0; s.aEnd = null; s.loop = false; },
  now(api, s) {               // 当前的 a_t、a_n 与位置（局部基）
    if (api.scene === "deburr") {
      const acc = s.v < api.p.vmax - 1e-12 ? api.p.at : 0;
      const th = s.s / api.p.R;
      return { at: acc, an: s.v * s.v / api.p.R, v: s.v, pos: [api.p.R * Math.cos(th), api.p.R * Math.sin(th)], et: [-Math.sin(th), Math.cos(th)] };
    }
    if (api.scene === "glue") {
      const u = s.u, A = this.A, B = this.B, tx = -A * Math.sin(u), ty = B * Math.cos(u), n = Math.hypot(tx, ty);
      return { at: 0, an: this.kap(u) * api.p.v0 * api.p.v0, v: api.p.v0, pos: [A * Math.cos(u), B * Math.sin(u)], et: [tx / n, ty / n] };
    }
    const R = api.p.Rr, v = api.p.vc, th = s.s / R;
    return { at: 0, an: v * v / R, v, pos: [R * Math.cos(th), R * Math.sin(th)], et: [-Math.sin(th), Math.cos(th)] };
  },
  update(dt, api, s) {
    const n = 20, h = dt / n;
    for (let i = 0; i < n; i++) {
      if (api.scene === "deburr") {
        const v1 = Math.min(api.p.vmax, s.v + api.p.at * h);
        if (s.v < api.p.vmax - 1e-12 && v1 >= api.p.vmax - 1e-12) s.aEnd = Math.hypot(api.p.at, api.p.vmax * api.p.vmax / api.p.R);
        s.s += 0.5 * (s.v + v1) * h; s.v = v1;
      } else if (api.scene === "glue") {
        const q = Math.sqrt(this.A * this.A * Math.sin(s.u) ** 2 + this.B * this.B * Math.cos(s.u) ** 2);
        s.u += api.p.v0 / q * h;
        s.maxan = Math.max(s.maxan, this.kap(s.u) * api.p.v0 * api.p.v0);
        if (s.u >= 2 * Math.PI) s.loop = true;
      } else { s.s += api.p.vc * h; }
    }
    const k = this.now(api, s);
    s.hist.push([api.t, k.at, k.an, Math.hypot(k.at, k.an)]);
    if (s.hist.length > 1500) s.hist.shift();
    const near = (a, b) => Math.abs(a - b) < 1e-9;
    if (api.scene === "deburr") {
      if (s.aEnd !== null && near(api.p.R, 0.1) && near(api.p.at, 0.5) && near(api.p.vmax, 0.25) && Math.abs(s.aEnd - 0.80039) < 1e-4) api.done("ex");
      if (s.v >= api.p.vmax - 1e-12 && near(api.p.R, 0.1) && api.p.vmax >= 0.2 - 1e-9 && api.p.vmax * api.p.vmax / api.p.R <= 0.5 + 1e-12) api.done("limit");
      if (api.t > 6) api.stop();
    } else if (api.scene === "glue") {
      if (s.loop) { if (s.maxan <= 1.0 && api.p.v0 >= 0.22 - 1e-9) api.done("glue"); api.stop(); }
    } else if (api.t > 20) api.stop();
  },
  readouts(api, s) {
    const k = this.now(api, s);
    if (api.scene === "road" && Math.abs(api.p.Rr - 500) < 1e-9 && Math.abs(api.p.vc - 30) < 1e-9) api.done("road");
    const rows = [[["速率 v", "speed v"], api.fmt(k.v, 4) + " m/s"], [["切向加速度 a_t", "tangential a_t"], api.fmt(k.at, 4) + " m/s²"],
                  [["法向加速度 a_n = κv²", "normal a_n = κv²"], api.fmt(k.an, 4) + " m/s²"], [["总加速度 |a|", "total |a|"], api.fmt(Math.hypot(k.at, k.an), 4) + " m/s²"]];
    if (api.scene === "deburr") rows.push([["加速结束时的 |a|", "|a| at the end of the speed-up"], s.aEnd === null ? "—" : api.fmt(s.aEnd, 5) + " m/s²"]);
    if (api.scene === "glue") rows.push([["本圈最大加速度", "largest acceleration this loop"], api.fmt(s.maxan, 4) + " m/s²"], [["此处曲率 κ", "curvature κ here"], api.fmt(this.kap(s.u), 3) + " 1/m"]);
    if (api.scene === "road") rows.push([["约为重力加速度的", "fraction of g"], api.fmt(k.an / 9.81 * 100, 1) + " %"]);
    return rows;
  },
  draw(api, s) {
    const { w, h, ctx } = api, top = h * 0.62;
    const k = this.now(api, s);
    let scale, ctr = [w * 0.5, top * 0.52];
    if (api.scene === "deburr") scale = top * 0.4 / api.p.R;
    else if (api.scene === "glue") scale = Math.min(w * 0.35 / this.A, top * 0.4 / this.B);
    else { scale = top * 0.4 / api.p.Rr; }
    const X = (p) => [ctr[0] + scale * p[0], ctr[1] - scale * p[1]];
    ctx.strokeStyle = api.css("--muted"); ctx.lineWidth = 1.5; ctx.beginPath();
    for (let i = 0; i <= 120; i++) {
      const u = 2 * Math.PI * i / 120;
      const p = api.scene === "glue" ? [this.A * Math.cos(u), this.B * Math.sin(u)] : [Math.cos(u) * (api.scene === "deburr" ? api.p.R : api.p.Rr), Math.sin(u) * (api.scene === "deburr" ? api.p.R : api.p.Rr)];
      const q = X(p); if (i) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]);
    }
    ctx.stroke();
    const P = X(k.pos), en = [-k.et[1], k.et[0]];       // 主法线：切线逆时针转 90°（本实验中都向左转弯）
    api.line(P[0] - 60 * k.et[0], P[1] + 60 * k.et[1], P[0] + 60 * k.et[0], P[1] - 60 * k.et[1], api.css("--grid"), 1, [4, 4]);
    api.arrow(P[0], P[1], P[0] + 30 * k.et[0], P[1] - 30 * k.et[1], api.css("--red"), 1.5);
    api.arrow(P[0], P[1], P[0] + 30 * en[0], P[1] - 30 * en[1], api.css("--green"), 1.5);
    api.label("e_t", P[0] + 40 * k.et[0], P[1] - 40 * k.et[1], api.css("--red"), 12, "center");
    api.label("e_n", P[0] + 40 * en[0], P[1] - 40 * en[1], api.css("--green"), 12, "center");
    const sa = api.scene === "road" ? 40 : 90;
    const av = [k.at * k.et[0] + k.an * en[0], k.at * k.et[1] + k.an * en[1]];
    api.arrow(P[0], P[1], P[0] + sa * k.at * k.et[0], P[1] - sa * k.at * k.et[1], "#1f77b4", 2);
    api.arrow(P[0], P[1], P[0] + sa * k.an * en[0], P[1] - sa * k.an * en[1], "#2ca02c", 2);
    api.arrow(P[0], P[1], P[0] + sa * av[0], P[1] - sa * av[1], "#c0392b", 3);
    if (api.scene === "road") api.robot(P[0], P[1], Math.atan2(k.et[1], k.et[0]) * 180 / Math.PI, 18, "#1f77b4");
    else api.circle(P[0], P[1], 5, api.css("--ink"));
    const ymax = Math.max(1, ...s.hist.map((q) => q[3])) * 1.1;
    const tmax = Math.max(1, s.hist.length ? s.hist[s.hist.length - 1][0] : 1);
    api.plot(40, top + 10, w - 60, h - top - 30, [
      { pts: s.hist.map((q) => [q[0], q[1]]), color: "#1f77b4" }, { pts: s.hist.map((q) => [q[0], q[2]]), color: "#2ca02c" },
      { pts: s.hist.map((q) => [q[0], q[3]]), color: "#c0392b" }], { xmin: 0, xmax: tmax, ymin: 0, ymax, xlabel: "t / s", ylabel: "m/s²" });
  },
});
