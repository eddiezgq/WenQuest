// 实验 10.3 径向分量与横向分量（配 10.3 节）。
// 场景 scara：零件库 SCARA 俯视，l1 = 0.35 m、l2 = 0.25 m；θ1 从 30° 起以 θ̇1 匀速转动，θ2 从设定值起以 θ̇2 匀速转动。
//   末端的 ρ、φ 及其导数按式 (10.3.11)–(10.3.13)，速度、加速度的径向、横向分量按式 (10.3.8)、(10.3.9)。
// 场景 walk：半径 2 m 的转盘以 φ̇ 匀速转动，人从离中心 0.3 m 处沿半径以 ρ̇ 匀速向外走（相对地面看：ρ̇、φ̇ 都不变）。
WQ.lab({
  title: ["实验 10.3 径向分量与横向分量", "Lab 10.3 Radial and transverse components"],
  goal: ["把 SCARA 末端的速度和加速度沿随手臂转动的径向、横向分解，找出边转边伸时出现的 2ρ̇φ̇ 项。",
         "Split the SCARA tool's velocity and acceleration along the radial and transverse directions that turn with the arm, and find the 2ρ̇φ̇ term."],
  scenes: [
    { id: "scara", robot: true, name: ["SCARA 边转边伸", "SCARA turning and extending"], hide: ["rd", "om"],
      problem: { title: ["机器人问题：夹爪要承受多大的横向加速度", "Robot problem: how much sideways acceleration must the gripper take"],
                 text: ["关节 1 以 1 rad/s 转动，同时关节 2 伸直手臂。两个关节都匀速，末端的横向加速度是多少？",
                        "Joint 1 turns at 1 rad/s while joint 2 straightens the arm, both steadily. What is the tool's transverse acceleration?"] } },
    { id: "walk", name: ["转盘上向外走", "Walking out on a turntable"], hide: ["th2", "w1", "w2"],
      problem: { title: ["生活中的例子：在转盘上沿半径行走", "Everyday example: walking along a radius of a turntable"],
                 text: ["转盘匀速转动，人沿半径匀速向外走。人的脚要向哪个方向用力？",
                        "The turntable turns steadily and a person walks steadily outward along a radius. Which way must the feet push?"] } },
  ],
  params: [
    { id: "th2", name: ["关节 2 的初始角 θ₂", "Initial joint-2 angle θ₂"], min: 20, max: 160, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "w1", name: ["关节 1 角速度 θ̇₁", "Joint-1 rate θ̇₁"], min: -2, max: 2, step: 0.1, value: 1, unit: "rad/s", digits: 1 },
    { id: "w2", name: ["关节 2 角速度 θ̇₂", "Joint-2 rate θ̇₂"], min: -2, max: 2, step: 0.1, value: -1.5, unit: "rad/s", digits: 1 },
    { id: "rd", name: ["行走速度 ρ̇", "Walking speed ρ̇"], min: 0, max: 2, step: 0.1, value: 1, unit: "m/s", digits: 1 },
    { id: "om", name: ["转盘角速度 φ̇", "Turntable rate φ̇"], min: 0, max: 2, step: 0.1, value: 1, unit: "rad/s", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["e_ρ", "e_ρ"], color: "#d62728" }, { name: ["e_φ", "e_φ"], color: "#2ca02c" }, { name: ["速度", "velocity"], color: "#e07b00" }, { name: ["加速度", "acceleration"], color: "#c0392b" }],
  tasks: [
    { id: "ex", robot: true, text: ["设置算例 10.3.1：θ₂ = 90°，θ̇₁ = 1.0 rad/s，θ̇₂ = −1.5 rad/s，读出横向加速度 a_φ 及其两项。",
                                    "Set Example 10.3.1: θ₂ = 90°, θ̇₁ = 1.0 rad/s, θ̇₂ = −1.5 rad/s; read a_φ and its two terms."],
      demo: { scene: "scara", set: { th2: 90, w1: 1, w2: -1.5 }, press: [], wait: 1 } },
    { id: "only1", robot: true, text: ["让关节 2 不动（θ̇₂ = 0）、关节 1 转动：横向加速度为零，径向加速度只剩向心项 −ρφ̇²。",
                                       "Keep joint 2 still (θ̇₂ = 0) and turn joint 1: the transverse acceleration vanishes, the radial one is only −ρφ̇²."],
      demo: { scene: "scara", set: { th2: 90, w1: 1, w2: 0 }, press: [], wait: 1 } },
    { id: "walk", text: ["转盘场景：人以 1 m/s 向外走、转盘以 1 rad/s 转动，读出横向加速度。",
                         "Turntable: walking out at 1 m/s on a turntable at 1 rad/s; read the transverse acceleration."],
      demo: { scene: "walk", set: { rd: 1, om: 1 }, press: [], wait: 1 } },
  ],
  think: ["两个关节都匀速转动，末端的 ρ̈、φ̈ 为什么不为零？这对“关节匀速运动时末端没有加速度”的直觉说明了什么？",
          "Both joints turn steadily; why are ρ̈ and φ̈ of the tool not zero? What does this say about the idea that steady joints give no tool acceleration?"],

  L1: 0.35, L2: 0.25,
  state(api, t) {             // ρ, φ, ρ̇, ρ̈, φ̇, φ̈（θ̈ = 0）
    if (api.scene === "walk") {
      const rd = api.p.rd, om = api.p.om;
      return { q1: 0, q2: 0, rho: 0.3 + rd * t, phi: om * t, rd, rdd: 0, pd: om, pdd: 0 };
    }
    const L1 = this.L1, L2 = this.L2, d = Math.PI / 180, w1 = api.p.w1, w2 = api.p.w2;
    const q1 = 30 * d + w1 * t, q2 = api.p.th2 * d + w2 * t;
    const rho = Math.sqrt(L1 * L1 + L2 * L2 + 2 * L1 * L2 * Math.cos(q2));
    const beta = Math.atan2(L2 * Math.sin(q2), L1 + L2 * Math.cos(q2));
    const rd = -L1 * L2 * Math.sin(q2) * w2 / rho;
    const rdd = (-L1 * L2 * Math.cos(q2) * w2 * w2 - rd * rd) / rho;
    const db = (L2 * L2 + L1 * L2 * Math.cos(q2)) / (rho * rho);
    const d2b = -L1 * L2 * Math.sin(q2) * (L1 * L1 - L2 * L2) / Math.pow(rho, 4);
    return { q1, q2, rho, phi: q1 + beta, rd, rdd, pd: w1 + db * w2, pdd: d2b * w2 * w2 };
  },
  reset(api, s) { s.trail = []; },
  update(dt, api, s) {
    const k = this.state(api, api.t);
    s.trail.push([k.rho * Math.cos(k.phi), k.rho * Math.sin(k.phi)]);
    if (s.trail.length > 3000) s.trail.shift();
    if (api.scene === "walk" && k.rho > 2) api.stop();
    if (api.scene === "scara" && (k.q2 < 5 * Math.PI / 180 || k.q2 > 175 * Math.PI / 180 || api.t > 12)) api.stop();
  },
  readouts(api, s) {
    const k = this.state(api, api.t);
    const aR = k.rdd - k.rho * k.pd * k.pd, aP = k.rho * k.pdd + 2 * k.rd * k.pd;
    const near = (a, b) => Math.abs(a - b) < 1e-9;
    if (api.scene === "scara" && api.t === 0 && near(api.p.th2, 90) && near(api.p.w1, 1) && near(api.p.w2, -1.5) && Math.abs(aP - 0.15258) < 5e-5) api.done("ex");
    if (api.scene === "scara" && near(api.p.w2, 0) && Math.abs(api.p.w1) > 0.05 && Math.abs(aP) < 1e-12 && Math.abs(aR + k.rho * k.pd * k.pd) < 1e-12) api.done("only1");
    if (api.scene === "walk" && near(api.p.rd, 1) && near(api.p.om, 1) && Math.abs(aP - 2) < 1e-9) api.done("walk");
    const f = (x, n) => api.fmt(x, n == null ? 4 : n);
    return [[["ρ, φ", "ρ, φ"], `${f(k.rho)} m, ${f(k.phi * 180 / Math.PI, 2)}°`],
            [["ρ̇, φ̇", "ρ̇, φ̇"], `${f(k.rd)} m/s, ${f(k.pd)} rad/s`],
            [["速度 v_ρ, v_φ", "velocity v_ρ, v_φ"], `${f(k.rd)}, ${f(k.rho * k.pd)} m/s`],
            [["a_ρ = ρ̈ − ρφ̇²", "a_ρ = ρ̈ − ρφ̇²"], `${f(k.rdd)} ${k.rho * k.pd * k.pd >= 0 ? "−" : "+"} ${f(Math.abs(k.rho * k.pd * k.pd))} = ${f(aR)} m/s²`],
            [["a_φ = ρφ̈ + 2ρ̇φ̇", "a_φ = ρφ̈ + 2ρ̇φ̇"], `${f(k.rho * k.pdd)} + ${f(2 * k.rd * k.pd)} = ${f(aP)} m/s²`],
            [["|a|", "|a|"], f(Math.hypot(aR, aP)) + " m/s²"]];
  },
  draw(api, s) {
    const { w, h, ctx } = api, walk = api.scene === "walk";
    const k = walk ? Math.min(w, h) / 4.8 : Math.min(w, h) / 0.75, O = walk ? [w * 0.42, h * 0.5] : [w * 0.3, h * 0.82];
    const X = (x, y) => [O[0] + k * x, O[1] - k * y];
    const st = this.state(api, api.t);
    if (walk) {
      api.circle(O[0], O[1], 2 * k, "rgba(120,140,160,0.12)", api.css("--muted"));
      for (let i = 0; i < 4; i++) { const a = st.phi + i * Math.PI / 2; api.line(O[0], O[1], ...X(2 * Math.cos(a), 2 * Math.sin(a)), api.css("--grid"), 1, [5, 4]); }
    } else {
      api.frame(O[0], O[1], 0, 30, ["x", "y"], "{s}");
      api.arm(O[0], O[1], [st.q1 * 180 / Math.PI, st.q2 * 180 / Math.PI], [this.L1 * k, this.L2 * k], "#8fa3b5", 10);
    }
    ctx.strokeStyle = api.css("--amber"); ctx.lineWidth = 1.5; ctx.beginPath();
    s.trail.forEach((p, i) => { const q = X(p[0], p[1]); if (i) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]); });
    ctx.stroke();
    const E = X(st.rho * Math.cos(st.phi), st.rho * Math.sin(st.phi));
    api.line(O[0], O[1], E[0], E[1], api.css("--muted"), 1, [4, 4]);
    const er = [Math.cos(st.phi), Math.sin(st.phi)], ep = [-Math.sin(st.phi), Math.cos(st.phi)];
    const L = walk ? 40 : 45;
    api.arrow(E[0], E[1], E[0] + L * er[0], E[1] - L * er[1], api.css("--red"), 2);
    api.arrow(E[0], E[1], E[0] + L * ep[0], E[1] - L * ep[1], api.css("--green"), 2);
    api.label("e_ρ", E[0] + 1.25 * L * er[0], E[1] - 1.25 * L * er[1], api.css("--red"), 13, "center");
    api.label("e_φ", E[0] + 1.25 * L * ep[0], E[1] - 1.25 * L * ep[1], api.css("--green"), 13, "center");
    const sv = walk ? 50 : 160, sa = walk ? 25 : 160;
    const v = [st.rd * er[0] + st.rho * st.pd * ep[0], st.rd * er[1] + st.rho * st.pd * ep[1]];
    const aR = st.rdd - st.rho * st.pd * st.pd, aP = st.rho * st.pdd + 2 * st.rd * st.pd;
    const a = [aR * er[0] + aP * ep[0], aR * er[1] + aP * ep[1]];
    api.arrow(E[0], E[1], E[0] + sv * v[0], E[1] - sv * v[1], "#e07b00", 3);
    api.arrow(E[0], E[1], E[0] + sa * a[0], E[1] - sa * a[1], "#c0392b", 3);
    if (walk) api.circle(E[0], E[1], 7, "#1f77b4", api.css("--ink")); else api.circle(E[0], E[1], 4, api.css("--ink"));
  },
});
