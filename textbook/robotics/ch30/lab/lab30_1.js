// 实验 30.1 调连杆长度满足工作空间（配 30.3 节）。
// 场景“部件装配工位”：WQ-CR5 式的偏置腕手臂（d1 = 0.15、d4 = 0.12、d5 = 0.10、d6 = 0.09 m，夹爪 TCP 距法兰 0.15 m），工具竖直朝下。
//   取放点与程序 ex30_1.py 的 STATION 相同（r、z，m）：每个点和上方 0.1 m 的接近点，共 12 个。
//   够不够得着按式 (30.3.1)～(30.3.3)：P4 = (√(r² − d4²) ∓ d5, z + 0.15 + d6 − d1)，|a2 − a3| ≤ |P4| ≤ a2 + a3；两种手腕取好的那个。
//   裕量 = 离圆环两端较近的那一端 ÷ (a2 + a3)（与程序 30.1.1 的 reach_margin 相同）。
//   手臂水平伸直时 J2、J3 的重力矩按集中质量算：大臂铝管 2.214 kg/m + 罩壳 0.3 kg（在大臂中点）、J3 中模组 2.0 kg（在肘部）、
//   小臂铝管 1.832 kg/m + 罩壳 0.2 kg（在小臂中点）、J4 模组 1.2 kg 与 J5 模组 + 连接件 1.4 kg（在腕部）、J6 模组 1.2 kg（再外 d5）、
//   连接件 0.2 kg（d5/2）、法兰 0.35 kg（d5）、负载（d5 + 0.1）。与完整模型（wqcr5.worst_case）相差不到 0.5%。
//   模组能力（式 (30.3.5)，示例值）：大模组额定 95.25 N·m、中模组额定 47.775 N·m；“举得住”指伸直的手臂长期不动时重力矩不超过额定能力。
//   标准 WQ-CR5（0.40 / 0.36 m）：5 kg 时 J2 96.2、J3 46.0 N·m；J3 在负载约 5.3 kg 以上超出中模组的额定能力。
// 场景“台灯”：夹在书桌（1.2 m × 0.6 m）后沿中间的摇臂台灯，转轴比桌面高 0.1 m；灯头要停在桌面上方 0.35 m，照到四个角和桌面中心。
WQ.lab({
  title: ["实验 30.1 调连杆长度满足工作空间", "Lab 30.1 Sizing the links to cover the workspace"],
  goal: ["调大臂、小臂的长度和负载，看部件装配工位的取放点够不够得着、肩部死区多大、J2 和 J3 的力矩够不够；体会 30.3 节“够得着”与“拿得动”的权衡。",
         "Adjust the upper-arm and forearm lengths and the payload; see whether the assembly station's points can be reached, how large the shoulder hole is, and whether J2 and J3 have enough torque — the reach-versus-torque trade-off of Section 30.3."],
  scenes: [
    { id: "arm", robot: true, name: ["部件装配工位", "Assembly station"], hide: ["l1", "l2"],
      problem: { title: ["机器人问题：0.86 m 怎样分给大臂和小臂", "Robot problem: how to split 0.86 m between the two arm links"],
                 text: ["工具竖直朝下，夹爪要够到 6 个取放点和它们上方 0.1 m 的接近点。手臂短一点力矩小，可会不会够不着？大臂、小臂谁长一点好？",
                        "With the tool pointing down the gripper must reach six points and the approach point 0.1 m above each. Shorter links need less torque, but can they still reach? Which link should be longer?"] } },
    { id: "lamp", name: ["台灯", "A desk lamp"], hide: ["a2", "a3", "mp", "pt"],
      problem: { title: ["生活中的例子：两节灯臂要多长", "Everyday example: how long should the two lamp arms be"],
                 text: ["台灯夹在书桌后沿中间，灯头要照到桌面的四个角和中心。灯臂太长会碰到人、太重，太短又照不到角。",
                        "The lamp clamps to the middle of the desk's back edge; its head must reach the four corners and the centre. Too long and it is heavy and in the way, too short and the corners stay dark."] } },
  ],
  params: [
    { id: "a2", name: ["大臂长 a2", "Upper arm a2"], min: 0.25, max: 0.55, step: 0.005, value: 0.40, unit: "m", digits: 3 },
    { id: "a3", name: ["小臂长 a3", "Forearm a3"], min: 0.20, max: 0.50, step: 0.005, value: 0.36, unit: "m", digits: 3 },
    { id: "mp", name: ["负载（含夹爪）", "Payload (incl. gripper)"], min: 0, max: 10, step: 0.1, value: 5, unit: "kg", digits: 1 },
    { id: "pt", name: ["画出手臂去第几个点", "Draw the arm at point no."], min: 1, max: 6, step: 1, value: 5, unit: "", digits: 0 },
    { id: "l1", name: ["灯臂 1", "Lamp arm 1"], min: 0.20, max: 0.60, step: 0.01, value: 0.35, unit: "m", digits: 2 },
    { id: "l2", name: ["灯臂 2", "Lamp arm 2"], min: 0.20, max: 0.60, step: 0.01, value: 0.35, unit: "m", digits: 2 },
  ],
  tasks: [
    { id: "std", robot: true, text: ["标准尺寸：大臂 0.40 m、小臂 0.36 m，12 个点全部够得着。", "Standard sizes, upper arm 0.40 m and forearm 0.36 m: all 12 points are reachable."],
      demo: { scene: "arm", set: { a2: 0.40, a3: 0.36, mp: 5 }, press: [] } },
    { id: "short", robot: true, text: ["缩短手臂：两段之和不超过 0.78 m，12 个点仍全部够得着。", "Shorten the arm: with the two links summing to at most 0.78 m all 12 points are still reachable."],
      demo: { scene: "arm", set: { a2: 0.36, a3: 0.32, mp: 5 }, press: [] } },
    { id: "dead", robot: true, text: ["把大臂、小臂之差加大到 0.10 m 以上（两段之和不变）：死区超出 J1 模组的半径，J3 的力矩下降多少？",
                                      "Make the difference between the links at least 0.10 m (same sum): the hole now exceeds the J1 module's radius; how much does J3's torque drop?"],
      demo: { scene: "arm", set: { a2: 0.43, a3: 0.33, mp: 5 }, press: [] } },
    { id: "heavy", robot: true, text: ["回到标准尺寸，从 5 kg 起加大负载：伸直静止时 J2、J3 的重力矩都超出各自模组的额定能力（J3 在约 5.3 kg 以上）。对照 30.3 节想一想：额定负载为什么仍是 5 kg？",
                                       "Back to the standard sizes, raise the payload from 5 kg: with the arm held out still, both J2 and J3 exceed their modules' ratings (J3 above about 5.3 kg). With Section 30.3 in mind, why is the rated payload still 5 kg?"],
      demo: { scene: "arm", set: { a2: 0.40, a3: 0.36, mp: 5.5 }, press: [] } },
    { id: "lamp", text: ["台灯：两节灯臂之和不超过 0.95 m，灯头照到桌面的四个角和中心。", "Lamp: with the two arms summing to at most 0.95 m the head reaches all four corners and the centre."],
      demo: { scene: "lamp", set: { l1: 0.47, l2: 0.45 }, press: [] } },
  ],
  think: ["式 (30.3.3) 只管“够得着”。手臂伸直时是奇异位形，为什么任务书要求每个点都留 5% 以上的裕量？裕量留多了又有什么坏处？",
          "Equation (30.3.3) only says whether a point can be reached. The outstretched arm is singular: why does the brief ask for at least 5 % margin at every point, and what does too much margin cost?"],

  D1: 0.15, D4: 0.12, D5: 0.10, D6: 0.09, TOOL: 0.15, APP: 0.10, RMOD: 0.055, CAP_L: 95.25, CAP_M: 47.775,
  ST: [["轴料架", "shaft rack", 0.55, 0.20], ["轴承料盘", "bearing tray", 0.45, 0.02], ["压装工装", "press fixture", 0.50, 0.10],
       ["齿轮料架", "gear rack", 0.60, 0.05], ["AGV 料箱", "AGV tote", 0.70, -0.30], ["检具", "gauge", 0.35, 0.05]],
  pts() {                                 // 12 个点：[名称, r, z, 是否接近点]
    const out = [];
    this.ST.forEach((s) => { out.push([s, s[2], s[3], false]); out.push([s, s[2], s[3] + this.APP, true]); });
    return out;
  },
  wrist(r, z) {                            // 式 (30.3.1)：两种手腕的 P4（相对 J2）
    if (r < this.D4) return [];
    const rp = Math.sqrt(r * r - this.D4 * this.D4), h = z + this.TOOL + this.D6 - this.D1;
    return [[rp - this.D5, h], [rp + this.D5, h]];
  },
  margin(r, z, a2, a3) {                   // 式 (30.3.3) 的相对裕量；两种手腕取好的
    let best = -Infinity;
    this.wrist(r, z).forEach(([x, y]) => {
      const rho = Math.hypot(x, y);
      best = Math.max(best, Math.min((a2 + a3 - rho) / (a2 + a3), (rho - Math.abs(a2 - a3)) / (a2 + a3)));
    });
    return best;
  },
  torques(a2, a3, mp) {                    // 手臂水平伸直时 J2、J3 的重力矩（集中质量）
    const g = 9.81, d5 = this.D5;
    const it = [[2.214 * a2 + 0.3, a2 / 2], [2.0, a2], [1.832 * a3 + 0.2, a2 + a3 / 2], [1.2, a2 + a3], [1.4, a2 + a3],
                [1.2, a2 + a3 + d5], [0.2, a2 + a3 + d5 / 2], [0.35, a2 + a3 + d5], [mp, a2 + a3 + d5 + 0.1]];
    let t2 = 0, t3 = 0;
    it.forEach(([m, x]) => { t2 += g * m * x; if (x > a2) t3 += g * m * (x - a2); });
    return [t2, t3];
  },
  lampPts() { return [[0.6, 0.6], [-0.6, 0.6], [0.6, 0], [-0.6, 0], [0, 0.3]]; },   // 桌面上的点（x 沿后沿，y 向前），夹子在 (0, 0)
  lampOk(l1, l2, p) {
    const d = Math.hypot(Math.hypot(p[0], p[1]), 0.35 - 0.1);
    return d <= l1 + l2 && d >= Math.abs(l1 - l2);
  },
  state(api) {
    const a2 = api.p.a2, a3 = api.p.a3, P = this.pts();
    const m = P.map((p) => this.margin(p[1], p[2], a2, a3));
    return { a2, a3, P, m, ok: m.filter((x) => x > 0).length, minm: Math.min(...m), tq: this.torques(a2, a3, api.p.mp) };
  },
  nb(rows) { return rows.map(([k, v]) => [k, String(v).replace(/ /g, "\u00a0")]); },
  readouts(api) {
    const f = api.fmt;
    if (api.scene === "lamp") {
      const l1 = api.p.l1, l2 = api.p.l2, P = this.lampPts(), ok = P.filter((p) => this.lampOk(l1, l2, p)).length;
      if (ok === P.length && l1 + l2 <= 0.95 + 1e-9) api.done("lamp");
      return this.nb([[["两节之和", "Sum of the arms"], f(l1 + l2, 2) + " m"], [["照得到的点", "Points reached"], `${ok} / ${P.length}`],
              [["最远的角（离转轴）", "Farthest corner (from the pivot)"], f(Math.hypot(Math.hypot(0.6, 0.6), 0.25), 3) + " m"]]);
    }
    const s = this.state(api), [t2, t3] = s.tq, dz = Math.abs(s.a2 - s.a3);
    const all = s.ok === s.P.length;
    if (all && Math.abs(s.a2 - 0.40) < 0.003 && Math.abs(s.a3 - 0.36) < 0.003) api.done("std");
    if (all && s.a2 + s.a3 <= 0.78 + 1e-9) api.done("short");
    if (s.a2 - s.a3 >= 0.10 - 1e-9) api.done("dead");
    if (Math.abs(s.a2 - 0.40) < 0.003 && Math.abs(s.a3 - 0.36) < 0.003 && t3 > this.CAP_M) api.done("heavy");
    const T = (z, e) => (api.lang() === "en" ? e : z);
    return this.nb([[["大臂 + 小臂；臂展（+ d5）", "Upper arm + forearm; reach (+ d5)"], `${f(s.a2 + s.a3, 3)} / ${f(s.a2 + s.a3 + this.D5, 3)} m`],
            [["够得着的点", "Points reachable"], `${s.ok} / ${s.P.length}`],
            [["最小裕量", "Smallest margin"], f(s.minm * 100, 1) + " %"],
            [["肩部死区 |a2 − a3|（J1 模组半径 5.5 cm）", "Shoulder hole |a2 − a3| (J1 module radius 5.5 cm)"],
             `${f(dz * 100, 1)} cm ${dz > this.RMOD ? T("超出模组", "beyond the module") : T("在模组里", "inside the module")}`],
            [["J2 伸直的重力矩 / 大模组额定", "J2 outstretched gravity torque / large module rating"], `${f(t2, 1)} / ${f(this.CAP_L, 1)} N·m ${t2 > this.CAP_L ? T("超额定", "above rating") : ""}`],
            [["J3 伸直的重力矩 / 中模组额定", "J3 outstretched gravity torque / medium module rating"],
             `${f(t3, 1)} / ${f(this.CAP_M, 1)} N·m ${t3 > this.CAP_M ? T("超额定", "above rating") : ""}`]]);
  },
  draw(api) {
    const { w, h } = api, c = api.ctx;
    if (api.scene === "lamp") {
      const l1 = api.p.l1, l2 = api.p.l2, k = Math.min(w / 1.6, h / 1.1), cx = w / 2, cy = h * 0.15;
      const X = (p) => [cx + k * p[0], cy + k * p[1]];
      const a = X([-0.6, 0]), b = X([0.6, 0.6]);
      api.rect(a[0], a[1], b[0] - a[0], b[1] - a[1], api.css("--panel"), api.css("--ink"));
      api.label(api.lang() === "en" ? "desk (top view)" : "书桌（俯视）", a[0] + 4, b[1] - 6, api.css("--muted"), 12, "left");
      const o = X([0, 0]);
      api.circle(o[0], o[1], 6, api.css("--ink"));
      const R = Math.sqrt(Math.max(0, (l1 + l2) ** 2 - 0.25 ** 2)), Ri = Math.sqrt(Math.max(0, (l1 - l2) ** 2 - 0.25 ** 2));
      c.setLineDash([5, 4]); c.strokeStyle = api.css("--blue"); c.beginPath(); c.arc(o[0], o[1], k * R, 0, Math.PI); c.stroke();
      if (Ri > 0) { c.strokeStyle = api.css("--red"); c.beginPath(); c.arc(o[0], o[1], k * Ri, 0, Math.PI); c.stroke(); }
      c.setLineDash([]);
      this.lampPts().forEach((p) => { const q = X(p); api.circle(q[0], q[1], 7, this.lampOk(l1, l2, p) ? api.css("--green") : api.css("--red"), api.css("--ink")); });
      return;
    }
    const s = this.state(api), k = Math.min(w / 1.2, h / 1.35), x0 = w * 0.06 + 0.1 * k, y0 = h * 0.04 + 0.9 * k;
    const X = (r, z) => [x0 + k * r, y0 - k * z];
    api.line(...X(-0.05, 0), ...X(1.1, 0), api.css("--ink"), 1);
    api.label(api.lang() === "en" ? "bench top z = 0" : "台面 z = 0", ...X(0.82, 0.02), api.css("--muted"), 11, "left");
    const j2 = X(0, this.D1);
    // P4 能到的圆环（相对 J2）：外圈、内圈（死区）
    c.setLineDash([4, 4]); c.strokeStyle = api.css("--blue");
    c.beginPath(); c.arc(j2[0], j2[1], k * (s.a2 + s.a3), -Math.PI / 2 - 0.9, Math.PI / 2 + 0.2); c.stroke(); c.setLineDash([]);
    api.circle(j2[0], j2[1], Math.max(2, k * Math.abs(s.a2 - s.a3)), null, api.css("--red"));
    api.circle(j2[0], j2[1], k * this.RMOD, null, api.css("--muted"));
    api.rect(...X(-0.075, 0.095), k * 0.15, k * 0.095, api.css("--grid"), api.css("--ink"));
    s.P.forEach((p, i) => {
      const q = X(p[1], p[2]), good = s.m[i] > 0;
      if (p[3]) api.circle(q[0], q[1], 4, good ? api.css("--green") : api.css("--red"));
      else { api.circle(q[0], q[1], 7, good ? api.css("--green") : api.css("--red"), api.css("--ink"));
             api.label(api.lang() === "en" ? p[0][1] : p[0][0], q[0] + 9, q[1] + 4, api.css("--ink"), 11, "left"); }
    });
    // 画出手臂去第 pt 个取放点（取裕量好的那种手腕、肘部朝上）
    const st = this.ST[Math.round(api.p.pt) - 1], W = this.wrist(st[2], st[3]);
    let best = null;
    W.forEach((pw, idx) => {
      const rho = Math.hypot(pw[0], pw[1]), mg = Math.min(s.a2 + s.a3 - rho, rho - Math.abs(s.a2 - s.a3));
      if (!best || mg > best.mg) best = { pw, idx, mg };
    });
    if (best && best.mg >= 0) {
      const [px, py] = best.pw, a2 = s.a2, a3 = s.a3, rho2 = px * px + py * py;
      const c3 = Math.max(-1, Math.min(1, (rho2 - a2 * a2 - a3 * a3) / (2 * a2 * a3))), t3 = -Math.acos(c3);
      const t2 = Math.atan2(py, px) - Math.atan2(a3 * Math.sin(t3), a2 + a3 * Math.cos(t3));
      const el = [a2 * Math.cos(t2), this.D1 + a2 * Math.sin(t2)], p4 = [px, this.D1 + py];
      const fl = [best.idx === 0 ? px + this.D5 : px - this.D5, this.D1 + py - this.D6];
      const tcp = [fl[0], fl[1] - this.TOOL];
      const col = api.css("--blue");
      api.line(...j2, ...X(el[0], el[1]), col, 8); api.line(...X(el[0], el[1]), ...X(p4[0], p4[1]), col, 6);
      api.line(...X(p4[0], p4[1]), ...X(fl[0], p4[1]), api.css("--amber"), 5); api.line(...X(fl[0], p4[1]), ...X(fl[0], fl[1]), api.css("--amber"), 5);
      api.line(...X(fl[0], fl[1]), ...X(tcp[0], tcp[1]), api.css("--ink"), 3);
      api.circle(...j2, 5, api.css("--panel"), api.css("--ink")); api.circle(...X(el[0], el[1]), 5, api.css("--panel"), api.css("--ink"));
      api.circle(...X(p4[0], p4[1]), 5, api.css("--panel"), api.css("--ink"));
    } else {
      api.label(api.lang() === "en" ? "this point cannot be reached" : "这个点够不着", ...X(0.3, 0.75), api.css("--red"), 14, "left");
    }
  },
});
