// 实验 2.2 矢量的合成：两连杆机械臂（配 2.2 节）。三个场景都是“首尾相接”：SCARA 的两段连杆、AGV 的三段路线、
// 渡河时船相对水的速度加上水流的速度。画面中蓝、绿是两个分矢量，红是合矢量；读数给出各矢量的分量与大小。
// 是否“到过”某个构型记在闭包里，重置时不丢（任务 2 要求先后找到肘朝上和肘朝下两种构型：关节 2 为正或为负）。
const L1_22 = 0.30, L2_22 = 0.25, Q22 = [0.45, 0.30];
const seen22 = { up: false, down: false };
const rad22 = (d) => d * Math.PI / 180;
function scara22(p) {
  const a = [L1_22 * Math.cos(rad22(p.th1)), L1_22 * Math.sin(rad22(p.th1))];
  const b = [L2_22 * Math.cos(rad22(p.th1 + p.th2)), L2_22 * Math.sin(rad22(p.th1 + p.th2))];
  return { a, b, r: [a[0] + b[0], a[1] + b[1]] };
}
function agv22(p) {
  const legs = [[12, 0], [8, 60], [p.L3, p.a3]].map(([L, t]) => [L * Math.cos(rad22(t)), L * Math.sin(rad22(t))]);
  const s = legs.reduce((u, v) => [u[0] + v[0], u[1] + v[1]], [0, 0]);
  return { legs, s };
}
const W22 = 60, VW22 = 1.0;                                        // 河宽 60 m，水流 1.0 m/s（沿 +x）
function river22(p) {
  const vb = [-p.vb * Math.sin(rad22(p.head)), p.vb * Math.cos(rad22(p.head))];   // 船头偏向上游（−x）为正
  const v = [vb[0] + VW22, vb[1]];
  const t = v[1] > 0 ? W22 / v[1] : Infinity;
  return { vb, v, t, drift: v[0] * t };
}

WQ.lab({
  title: ["实验 2.2 矢量的合成：两连杆机械臂", "Lab 2.2 Adding vectors: a two-link arm"],
  goal: ["把两个矢量首尾相接，看合矢量怎样随分矢量变化；用分量相加核对作图的结果。",
         "Put two vectors head to tail and watch how the sum follows them; check the picture by adding components."],
  scenes: [
    { id: "scara", robot: true, name: ["SCARA 末端去抓零件", "SCARA end reaching a part"], hide: ["L3", "a3", "vb", "head"],
      problem: { title: ["机器人问题：末端的位置矢量", "Robot problem: the position vector of the end"],
                 text: ["大臂 0.30 m、小臂 0.25 m。末端的位置矢量 r = a + b。零件在 (0.45, 0.30) m，调两个关节角让末端到达它。",
                        "Upper arm 0.30 m, forearm 0.25 m. The end is at r = a + b. The part is at (0.45, 0.30) m: set the two joint angles to reach it."] } },
    { id: "agv", robot: true, name: ["AGV 三段路线回到起点", "AGV back to start in three legs"], hide: ["th1", "th2", "vb", "head"],
      problem: { title: ["机器人问题：巡检路线收尾", "Robot problem: closing a patrol route"],
                 text: ["前两段固定：12 m 朝 0°，8 m 朝 60°。第三段的长度和方向由你定，让三段位移之和为零。",
                        "The first two legs are fixed: 12 m at 0° and 8 m at 60°. Choose the third so that the three displacements add up to zero."] } },
    { id: "river", name: ["渡河", "Crossing a river"], hide: ["th1", "th2", "L3", "a3"],
      problem: { title: ["生活中的例子：船头该朝哪里", "Everyday example: where to point the boat"],
                 text: ["河宽 60 m，水流 1.0 m/s 向右。船相对水的速度加上水流的速度，才是船相对岸的速度。",
                        "The river is 60 m wide and flows at 1.0 m/s to the right. The boat's velocity over the ground is its velocity through the water plus the current."] } },
  ],
  params: [
    { id: "th1", name: ["关节 1：大臂与 x 轴的夹角", "Joint 1: upper arm from x axis"], min: -180, max: 180, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "th2", name: ["关节 2：小臂相对大臂转过", "Joint 2: forearm relative to upper arm"], min: -170, max: 170, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "L3", name: ["第三段的长度", "Length of leg 3"], min: 0, max: 25, step: 0.05, value: 10, unit: "m", digits: 2 },
    { id: "a3", name: ["第三段的方向（从 x 轴量）", "Direction of leg 3 (from x axis)"], min: -180, max: 180, step: 1, value: 180, unit: "°", digits: 0 },
    { id: "vb", name: ["船相对水的速率", "Boat speed through the water"], min: 0.5, max: 3, step: 0.1, value: 2, unit: "m/s", digits: 1 },
    { id: "head", name: ["船头偏向上游的角度", "Heading upstream of straight across"], min: -80, max: 80, step: 1, value: 0, unit: "°", digits: 0 },
  ],
  tasks: [
    { id: "reach", robot: true, text: ["让 SCARA 的末端到达零件，误差 1 cm 以内。", "Bring the SCARA end to the part, within 1 cm."],
      demo: { scene: "scara", set: { th1: 24, th2: 21 }, press: [], wait: 1 } },
    { id: "elbow", robot: true, text: ["找到到达零件的另一组关节角（肘朝上与肘朝下各一次）。", "Find the other set of joint angles that reaches the part (elbow up once and elbow down once)."],
      demo: { scene: "scara", set: { th1: 43, th2: -21 }, press: [], wait: 1 } },
    { id: "close", robot: true, text: ["调第三段，让 AGV 回到起点（离起点 0.25 m 以内）。", "Set leg 3 so that the AGV ends within 0.25 m of the start."],
      demo: { scene: "agv", set: { L3: 17.45, a3: -157 }, press: [], wait: 1 } },
    { id: "cross", text: ["船速 2.0 m/s 时，让船正对着到达对岸（偏离 1 m 以内）。", "With the boat at 2.0 m/s, land directly opposite (within 1 m)."],
      demo: { scene: "river", set: { vb: 2, head: 30 }, press: [], wait: 1 } },
  ],
  think: ["SCARA 的末端能到达的区域是什么形状？为什么两段连杆一样长时，末端可以回到肩关节？水流比船快时，能不能正对着到达对岸？",
          "What region can the SCARA end reach? Why can the end return to the shoulder when both links are equally long? Can the boat land directly opposite if the current is faster than the boat?"],

  reset(api, s) {},
  change(api, s, pid) { check22(api); },
  readouts(api, s) {
    const f = api.fmt, v = (u, d = 3) => `(${f(u[0], d)}, ${f(u[1], d)})`, n = (u) => Math.hypot(u[0], u[1]);
    const ang = (u) => f(Math.atan2(u[1], u[0]) * 180 / Math.PI, 1) + "°";
    if (api.scene === "scara") {
      const { a, b, r } = scara22(api.p);
      return [[["a（大臂）", "a (upper arm)"], v(a) + " m"], [["b（小臂）", "b (forearm)"], v(b) + " m"],
              [["r = a + b", "r = a + b"], v(r) + " m"], [["|r|、方向", "|r|, direction"], f(n(r), 3) + " m, " + ang(r)],
              [["离零件", "Distance to the part"], f(100 * Math.hypot(r[0] - Q22[0], r[1] - Q22[1]), 1) + " cm"]];
    }
    if (api.scene === "agv") {
      const { legs, s: S } = agv22(api.p);
      return [[["第一段", "Leg 1"], v(legs[0], 2) + " m"], [["第二段", "Leg 2"], v(legs[1], 2) + " m"], [["第三段", "Leg 3"], v(legs[2], 2) + " m"],
              [["总位移", "Total displacement"], v(S, 2) + " m"], [["离起点", "From the start"], f(n(S), 2) + " m"]];
    }
    const { vb, v: V, t, drift } = river22(api.p);
    return [[["船相对水", "Boat through water"], v(vb, 2) + " m/s"], [["水流", "Current"], `(${f(VW22, 2)}, 0.00) m/s`],
            [["船相对岸", "Boat over ground"], v(V, 2) + " m/s, " + f(n(V), 2) + " m/s"],
            [["过河时间", "Crossing time"], isFinite(t) ? f(t, 1) + " s" : "—"], [["下游偏离", "Drift downstream"], isFinite(t) ? f(drift, 1) + " m" : api.T("到不了对岸", "never crosses")]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, blue = css("--blue"), green = css("--green"), red = css("--red");
    if (api.scene === "scara") {
      const S = Math.min(w, h) * 0.75, ox = w * 0.42, oy = h * 0.85, X = (u) => [ox + S * u[0], oy - S * u[1]];
      api.ctx.strokeStyle = css("--line"); api.ctx.lineWidth = 1; api.ctx.setLineDash([3, 4]);
      [L1_22 - L2_22, L1_22 + L2_22].forEach((R) => { api.ctx.beginPath(); api.ctx.arc(ox, oy, S * R, Math.PI, 2 * Math.PI); api.ctx.stroke(); });
      api.ctx.setLineDash([]);
      api.line(ox - S * 0.6, oy, ox + S * 0.6, oy, css("--muted"), 1); api.line(ox, oy, ox, oy - S * 0.6, css("--muted"), 1);
      api.label("x", ox + S * 0.6 + 6, oy, css("--muted"), 12); api.label("y", ox + 4, oy - S * 0.6, css("--muted"), 12);
      api.arm(ox, oy, [api.p.th1, api.p.th2], [S * L1_22, S * L2_22], css("--soft"), 14);
      const { a, r } = scara22(api.p), A = X(a), R = X(r), q = X(Q22);
      api.circle(q[0], q[1], 7, css("--amber"), css("--ink")); api.label(api.T("零件", "part"), q[0] + 10, q[1] - 10, css("--ink"), 12);
      api.arrow(ox, oy, A[0], A[1], blue, 3); api.arrow(A[0], A[1], R[0], R[1], green, 3); api.arrow(ox, oy, R[0], R[1], red, 3);
      api.label("a", (ox + A[0]) / 2 - 12, (oy + A[1]) / 2, blue, 15); api.label("b", (A[0] + R[0]) / 2 + 8, (A[1] + R[1]) / 2, green, 15);
      api.label("r", (ox + R[0]) / 2 + 8, (oy + R[1]) / 2 + 12, red, 15);
      api.label(api.T("虚线：末端能到达的最远、最近处", "dashed: farthest and nearest reach"), 12, h - 14, css("--muted"), 11);
      return;
    }
    if (api.scene === "agv") {
      const S = Math.min(w / 26, h / 16), ox = w * 0.2, oy = h * 0.72, X = (u) => [ox + S * u[0], oy - S * u[1]];
      api.grid(w, h, S * 2);
      const { legs, s: Sm } = agv22(api.p), cols = [blue, green, css("--amber")];
      let p = [0, 0];
      legs.forEach((u, i) => { const q = [p[0] + u[0], p[1] + u[1]], P = X(p), Qp = X(q); api.arrow(P[0], P[1], Qp[0], Qp[1], cols[i], 3);
        api.label(String(i + 1), (P[0] + Qp[0]) / 2 + 6, (P[1] + Qp[1]) / 2 - 8, cols[i], 13); p = q; });
      const E = X(Sm);
      if (Math.hypot(Sm[0], Sm[1]) > 0.05) api.arrow(ox, oy, E[0], E[1], red, 2);
      api.circle(ox, oy, 6, css("--ink")); api.label(api.T("起点", "start"), ox - 34, oy + 16, css("--ink"), 12);
      api.agv(E[0], E[1] + 10, 34);
      api.label(api.T("每格 2 m", "grid 2 m"), 12, h - 14, css("--muted"), 11);
      return;
    }
    // 渡河
    const top = h * 0.18, bot = h * 0.82, S = (bot - top) / W22, ox = w * 0.45;
    api.rect(0, top, w, bot - top, "rgba(80,140,200,0.15)");
    api.line(0, top, w, top, css("--ink"), 2); api.line(0, bot, w, bot, css("--ink"), 2);
    api.label(api.T("对岸", "far bank"), 10, top - 12, css("--ink"), 12); api.label(api.T("出发岸", "near bank"), 10, bot + 14, css("--ink"), 12);
    for (let x = 30; x < w; x += 90) api.arrow(x, (top + bot) / 2 + 40, x + 30, (top + bot) / 2 + 40, "rgba(80,140,200,0.6)", 2);
    const { vb, v: V, t, drift } = river22(api.p);
    api.circle(ox, top, 5, css("--muted")); api.label(api.T("正对岸", "opposite"), ox + 8, top + 14, css("--muted"), 11);
    if (isFinite(t)) {
      const ex = ox + S * drift;
      api.line(ox, bot, ex, top, css("--muted"), 1.5, [5, 5]);
    }
    const K = 50, B = [ox, bot - 10];
    api.arrow(B[0], B[1], B[0] + K * vb[0], B[1] - K * vb[1], blue, 3);
    api.arrow(B[0] + K * vb[0], B[1] - K * vb[1], B[0] + K * V[0], B[1] - K * V[1], green, 3);
    api.arrow(B[0], B[1], B[0] + K * V[0], B[1] - K * V[1], red, 3);
    api.label(api.T("船相对水", "boat/water"), B[0] + K * vb[0] - 70, B[1] - K * vb[1] - 6, blue, 12);
    api.label(api.T("水流", "current"), B[0] + K * (vb[0] + V[0]) / 2 + 6, B[1] - K * vb[1] - 10, green, 12);
    api.label(api.T("船相对岸", "boat/ground"), B[0] + K * V[0] + 6, B[1] - K * V[1] + 4, red, 12);
  },
});

function check22(api) {
  if (api.scene === "scara") {
    const { r } = scara22(api.p);
    if (Math.hypot(r[0] - Q22[0], r[1] - Q22[1]) < 0.01) {
      api.done("reach");
      if (api.p.th2 > 0) seen22.up = true; else if (api.p.th2 < 0) seen22.down = true;
      if (seen22.up && seen22.down) api.done("elbow");
    }
  }
  if (api.scene === "agv") { const { s: S } = agv22(api.p); if (Math.hypot(S[0], S[1]) < 0.25) api.done("close"); }
  if (api.scene === "river") { const { t, drift } = river22(api.p); if (Math.abs(api.p.vb - 2) < 1e-9 && isFinite(t) && Math.abs(drift) < 1) api.done("cross"); }
}
