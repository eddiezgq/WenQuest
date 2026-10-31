// 实验 30.2 为工位选机器人（配 30.4 节）。
// 场景“部件装配工位”：候选机械臂的厂商参数取自零件库 library/catalog/B/*/vendor.yaml（WQ-CR5 取机器人厂的原件 wqcr5.py），
//   与程序 ex30_4.py、图 30.4.1 同一份数据；SCARA 为零件库自建的 B-SCA-WQ4（默认臂展 0.6 m、竖直行程 0.15 m，负载未定）。
//   零件质量（kg）：棒料零件取物料清单的每件耗料，锻坯齿轮按毛坯尺寸算，都是上限；GR-302 取成品估算（程序 30.4.2）。夹爪 1.0 kg。
//   工位要求：臂展 ≥ 759 mm（算例 30.1.2），高差 0.6 m（算例 30.2.2）。
//   节拍按式 (30.1.2)：一次取放 = J1 转 90° 两次 + 0.1 m 的接近 4 次 + 夹爪开合 2 × 0.3 s。围栏内：关节 180°/s、360°/s²，直线 0.5 m/s、1 m/s²；
//   与人同场：TCP 限速 0.25 m/s（示例），J1 转 90° 走取放点处（r = 0.55 m）的圆弧。程序算出：5.13 s、10.6 s；一套 SA-200 有 7 个零件。
// 场景“搬家选车”：三种车的载重与车厢内高（示例值），三件家具的质量与高度；冰箱要竖着运。
WQ.lab({
  title: ["实验 30.2 为工位选机器人", "Lab 30.2 Choosing a robot for the station"],
  goal: ["为减速器厂部件装配工位从零件库的几台机械臂中选一台：先算最重的零件，再看够不够得着、能否与人同场、节拍够不够；体会 30.4 节“选型先算最重的件”。",
         "Choose a robot for the gearbox plant's sub-assembly station from the library's arms: heaviest part first, then reach, working beside people and cycle time — the selection order of Section 30.4."],
  scenes: [
    { id: "station", robot: true, name: ["部件装配工位", "Assembly station"], hide: ["veh", "item"],
      problem: { title: ["机器人问题：选哪一台", "Robot problem: which robot"],
                 text: ["工位要搬轴、齿轮和轴承，取放点最远的离 J1 轴 0.7 m、在台面以下。工人和机器人在同一个工位上干活。",
                        "The station handles shafts, gears and bearings; the farthest point is 0.7 m from J1's axis, below the bench. Workers and the robot share the station."] } },
    { id: "move", name: ["搬家选车", "Choosing a moving van"], hide: ["robot", "part", "mode"],
      problem: { title: ["生活中的例子：按最重、最高的家具选车", "Everyday example: choose the van by the heaviest and tallest item"],
                 text: ["搬家要运冰箱、洗衣机和沙发。车太小装不下，太大又贵。先看哪件最难运。",
                        "A fridge, a washing machine and a sofa have to move. Too small a vehicle won't take them, too large costs more. Start with the hardest item."] } },
  ],
  params: [
    { id: "robot", name: ["机器人：0 WQ-CR5 / 1 UR5e / 2 UR10e / 3 GoFa / 4 LR Mate 200iD/7L / 5 KR 6 R900 / 6 IRB 1200 / 7 SCARA",
                          "Robot: 0 WQ-CR5 / 1 UR5e / 2 UR10e / 3 GoFa / 4 LR Mate 200iD/7L / 5 KR 6 R900 / 6 IRB 1200 / 7 SCARA"], min: 0, max: 7, step: 1, value: 0, unit: "", digits: 0 },
    { id: "part", name: ["零件：1 SH-201 / 2 SH-301 / 3 GR-203 / 4 GR-202 / 5 SH-101 / 6 GR-302", "Part: 1 SH-201 / 2 SH-301 / 3 GR-203 / 4 GR-202 / 5 SH-101 / 6 GR-302"],
      min: 1, max: 6, step: 1, value: 1, unit: "", digits: 0 },
    { id: "mode", name: ["工作方式：0 与人同场（限速）/ 1 围栏内全速", "Mode: 0 beside people (speed-limited) / 1 guarded, full speed"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "veh", name: ["车：0 小轿车 / 1 面包车 / 2 小货车", "Vehicle: 0 car / 1 minivan / 2 small truck"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
    { id: "item", name: ["家具：0 冰箱 / 1 洗衣机 / 2 沙发", "Item: 0 fridge / 1 washing machine / 2 sofa"], min: 0, max: 2, step: 1, value: 0, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "ok", robot: true, text: ["WQ-CR5 搬中间轴 SH-201：负载、臂展、与人同场全部合格。", "WQ-CR5 handling the intermediate shaft SH-201: payload, reach and sharing all pass."],
      demo: { scene: "station", set: { robot: 0, part: 1, mode: 0 }, press: [] } },
    { id: "heavy", robot: true, text: ["WQ-CR5 搬第二级大齿轮 GR-302：负载不合格。", "WQ-CR5 handling the large second-stage gear GR-302: the payload check fails."],
      demo: { scene: "station", set: { robot: 0, part: 6, mode: 0 }, press: [] } },
    { id: "big", robot: true, text: ["找一台能搬 GR-302 的机器人，读出负载裕量。", "Find a robot that can carry GR-302 and read its payload margin."],
      demo: { scene: "station", set: { robot: 2, part: 6, mode: 0 }, press: [] } },
    { id: "short", robot: true, text: ["选 IRB 1200：负载够，臂展不合格。", "Choose the IRB 1200: enough payload, but the reach fails."],
      demo: { scene: "station", set: { robot: 6, part: 1, mode: 1 }, press: [] } },
    { id: "cycle", robot: true, text: ["WQ-CR5 换成“围栏内全速”，与“与人同场”比较一套 SA-200 的搬运时间。", "Switch the WQ-CR5 to full guarded speed and compare one SA-200's handling time with working beside people."],
      demo: { scene: "station", set: { robot: 0, part: 1, mode: 1 }, press: [] } },
    { id: "van", text: ["搬家：找出能竖着装下冰箱、载重也够的最小的车。", "Moving: find the smallest vehicle that takes the fridge upright and carries its weight."],
      demo: { scene: "move", set: { veh: 2, item: 0 }, press: [] } },
  ],
  think: ["工业机器人负载、速度都有余，为什么在这个工位上反而不是首选？什么样的工位会反过来选它？",
          "Industrial robots have payload and speed to spare; why are they not the first choice at this station, and what kind of station would reverse the choice?"],

  R: [["WQ-CR5", 5, 860, 17.4, true], ["UR5e", 5, 850, 20.6, true], ["UR10e", 12.5, 1300, 33.5, true], ["GoFa CRB 15000-5/0.95", 5, 950, 28, true],
      ["LR Mate 200iD/7L", 7, 911, 27, false], ["KR 6 R900-2", 6, 901, 55, false], ["IRB 1200-7/0.7", 7, 703, 52, false], ["SCARA（问渠）", null, 600, null, false]],
  P: [["SH-201 中间轴", "SH-201 intermediate shaft", 3.3], ["SH-301 输出轴", "SH-301 output shaft", 2.8], ["GR-203 小齿轮", "GR-203 pinion", 1.8],
      ["GR-202 大齿轮", "GR-202 gear", 4.74], ["SH-101 齿轮轴", "SH-101 pinion shaft", 5.2], ["GR-302 大齿轮（成品估算）", "GR-302 gear (estimated finished)", 11.0]],
  GRIP: 1.0, REACH_NEED: 759, SPAN: 0.6, SC_STROKE: 0.15,
  V: [["小轿车", "car", 400, 0.5], ["面包车", "minivan", 800, 1.2], ["小货车", "small truck", 1500, 1.9]],
  I: [["冰箱", "fridge", 85, 1.8], ["洗衣机", "washing machine", 70, 0.85], ["沙发", "sofa", 60, 0.9]],
  mt(s, v, a) { return s >= v * v / a ? s / v + v / a : 2 * Math.sqrt(s / a); },    // 式 (30.1.2)
  cycle(mode) {
    if (mode === 1) return 2 * this.mt(Math.PI / 2, Math.PI, 2 * Math.PI) + 4 * this.mt(0.1, 0.5, 1.0) + 2 * 0.3;
    return 2 * this.mt(Math.PI / 2 * 0.55, 0.25, 1.0) + 4 * this.mt(0.1, 0.25, 1.0) + 2 * 0.3;
  },
  nb(rows) { return rows.map(([k, v]) => [k, String(v).replace(/ /g, "\u00a0")]); },
  readouts(api, s) {
    const f = api.fmt, T = (z, e) => (api.lang() === "en" ? e : z);
    if (api.scene === "move") {
      const v = this.V[Math.round(api.p.veh)], it = this.I[Math.round(api.p.item)];
      const wOk = it[2] <= v[2], hOk = it[3] <= v[3];
      if (Math.round(api.p.item) === 0 && Math.round(api.p.veh) === 2 && wOk && hOk) api.done("van");
      return this.nb([[["车：载重、车厢内高", "Vehicle: load, inside height"], `${T(v[0], v[1])}：${v[2]} kg，${f(v[3], 2)} m`],
              [["家具：质量、高度", "Item: mass, height"], `${T(it[0], it[1])}：${it[2]} kg，${f(it[3], 2)} m`],
              [["载重", "Load"], wOk ? T("够", "OK") : T("超载", "overloaded")],
              [["竖着装得下", "Fits upright"], hOk ? T("装得下", "fits") : T("太高", "too tall")]]);
    }
    const ri = Math.round(api.p.robot), r = this.R[ri], p = this.P[Math.round(api.p.part) - 1], mode = Math.round(api.p.mode);
    const need = p[2] + this.GRIP;
    const pOk = r[1] != null && need <= r[1], reachOk = r[2] >= this.REACH_NEED && (ri !== 7 || this.SC_STROKE >= this.SPAN);
    const share = r[4], shareOk = mode === 1 || share;
    const t1 = this.cycle(mode), tSA = 7 * t1;
    const margin = r[1] != null ? (r[1] - need) / r[1] * 100 : null;
    if (ri === 0 && Math.round(api.p.part) === 1 && pOk && reachOk && shareOk && mode === 0) api.done("ok");
    if (ri === 0 && Math.round(api.p.part) === 6 && !pOk) api.done("heavy");
    if (Math.round(api.p.part) === 6 && pOk && reachOk) api.done("big");
    if (ri === 6 && !reachOk && r[1] >= need) api.done("short");
    if (ri === 0 && mode === 1) api.done("cycle");
    const other = 7 * this.cycle(1 - mode);
    const all = pOk && reachOk && shareOk;
    return this.nb([[["机器人：负载、臂展、自重", "Robot: payload, reach, own mass"], `${r[0]}：${r[1] != null ? r[1] + " kg" : T("未定", "n/a")}，${r[2]} mm，${r[3] != null ? r[3] + " kg" : "—"}`],
            [["负载：零件 + 夹爪", "Payload: part + gripper"], `${T(p[0], p[1])} ${f(p[2], 2)} + ${f(this.GRIP, 1)} = ${f(need, 2)} kg → ${pOk ? T("合格，裕量 ", "OK, margin ") + f(margin, 0) + " %" : T("不合格", "fails")}`],
            [["臂展（工位要 759 mm）", "Reach (station needs 759 mm)"], reachOk ? T("合格", "OK") : (ri === 7 ? T("不合格：臂展和竖直行程都不够", "fails: reach and vertical stroke too short") : T("不合格", "fails"))],
            [["与人同场", "Beside people"], share ? T("可以（协作机器人）", "yes (collaborative)") : (mode === 1 ? T("要围栏或光幕", "needs guarding") : T("不能：选“围栏内全速”", "no: choose guarded mode"))],
            [["一次取放 / 一套 SA-200（7 件）", "One pick and place / one SA-200 (7 parts)"], `${f(t1, 2)} s / ${f(tSA, 1)} s`],
            [["另一种工作方式下一套 SA-200", "One SA-200 in the other mode"], `${f(other, 1)} s（${mode === 1 ? T("与人同场", "beside people") : T("围栏内全速", "guarded, full speed")}）`],
            [["结论", "Verdict"], all ? T("可用", "suitable") : T("不可用", "unsuitable")]]);
  },
  draw(api, s) {
    const { w, h } = api, c = api.ctx;
    if (api.scene === "move") {
      const v = this.V[Math.round(api.p.veh)], it = this.I[Math.round(api.p.item)], k = Math.min(w / 4, h / 2.6), x0 = w * 0.15, y0 = h * 0.82;
      api.rect(x0, y0 - k * v[3], k * 2.6, k * v[3], api.css("--panel"), api.css("--ink"));
      api.label(api.lang() === "en" ? v[1] : v[0], x0 + 6, y0 - k * v[3] - 8, api.css("--ink"), 13, "left");
      const ok = it[3] <= v[3] && it[2] <= v[2];
      api.rect(x0 + k * 0.3, y0 - k * it[3], k * 0.7, k * it[3], ok ? api.css("--green") : api.css("--red"), api.css("--ink"));
      api.label(api.lang() === "en" ? it[1] : it[0], x0 + k * 0.32, y0 - k * it[3] - 8, api.css("--ink"), 12, "left");
      api.line(x0 - 20, y0, x0 + k * 3, y0, api.css("--ink"), 2);
      return;
    }
    // 负载—臂展图：候选机器人、工位的要求、当前零件所需的负载
    const L = w * 0.12, B = h * 0.85, Wd = w * 0.8, Hd = h * 0.72;
    const X = (mm) => L + (mm - 500) / (1400 - 500) * Wd, Y = (kg) => B - kg / 15 * Hd;
    api.line(L, B, L + Wd, B, api.css("--ink"), 1); api.line(L, B, L, B - Hd, api.css("--ink"), 1);
    for (let mm = 600; mm <= 1400; mm += 200) api.label(String(mm), X(mm), B + 14, api.css("--muted"), 11, "center");
    for (let kg = 0; kg <= 15; kg += 5) api.label(String(kg), L - 6, Y(kg) + 4, api.css("--muted"), 11, "right");
    api.label(api.lang() === "en" ? "reach / mm" : "臂展 / mm", L + Wd / 2, B + 30, api.css("--ink"), 12, "center");
    api.label(api.lang() === "en" ? "payload / kg" : "负载 / kg", L + 4, B - Hd - 8, api.css("--ink"), 12, "left");
    c.fillStyle = api.css("--grid");
    c.fillRect(X(this.REACH_NEED), Y(15), X(1400) - X(this.REACH_NEED), Y(0) - Y(15));
    const p = this.P[Math.round(api.p.part) - 1], need = p[2] + this.GRIP;
    c.setLineDash([5, 4]); api.line(L, Y(need), L + Wd, Y(need), api.css("--red"), 1.5); c.setLineDash([]);
    api.label((api.lang() === "en" ? "needed: " : "需要：") + api.fmt(need, 1) + " kg", L + Wd - 4, Y(need) - 6, api.css("--red"), 11, "right");
    const sel = Math.round(api.p.robot);
    this.R.forEach((r, i) => {
      if (r[1] == null) return;
      const x = X(r[2]), y = Y(r[1]);
      if (r[4]) api.circle(x, y, i === sel ? 9 : 6, i === sel ? api.css("--amber") : api.css("--blue"), api.css("--ink"));
      else api.rect(x - (i === sel ? 8 : 5), y - (i === sel ? 8 : 5), i === sel ? 16 : 10, i === sel ? 16 : 10, i === sel ? api.css("--amber") : api.css("--muted"), api.css("--ink"));
      api.label(r[0], x + 10, i === 1 ? y + 14 : y - 6, api.css("--ink"), 11, "left");
    });
  },
});
