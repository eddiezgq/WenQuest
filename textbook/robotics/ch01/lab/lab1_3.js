// 实验 1.3 机器人家族三维展示（配 1.3 节）。
// 零件库八个模型按类别分在三个机器人场景中；“选择”滑块挑出一个模型（其余变淡），“摆动”让它的关节在允许范围内来回摆动。
// 读数由模型条目（关节表、连杆质量、厂家参数表）直接算出。生活场景用差速小车代表家里的扫地机器人。
WQ.lab({
  title: ["实验 1.3 机器人家族三维展示", "Lab 1.3 The robot family in 3D"],
  goal: ["逐一查看问渠零件库的八个机器人模型，按用途、基座、结构和关节给它们分类。",
         "Look at the eight robots of the WenQuest library one by one and classify them by use, base, structure and joints."],
  view: "3d",
  models: ["B-ARM-UR5E", "B-ARM-PANDA", "B-SCA-WQ4", "B-PAR-DELTA", "B-LEG-GO2", "B-HUM-G1", "B-EDU-DIFF", "B-UAV-X2"],
  scenes: [
    { id: "arms", robot: true, name: ["工业臂", "Industrial arms"],
      problem: { title: ["机器人问题：四台固定基座的操作臂有什么不同", "Robot problem: how do the four fixed-base arms differ"],
                 text: ["UR5e、Panda 是串联关节型（Panda 手爪的两根手指是移动关节），SCARA 的手臂有一个移动关节，Delta 是并联的。选择 0–3 依次查看。",
                        "UR5e and Panda are articulated serial arms (Panda's two gripper fingers are prismatic), SCARA's arm has a prismatic joint, Delta is parallel. Select 0–3 in turn."] },
      params: { sel: { min: 0, max: 3, step: 1, value: 0 } }, hide: ["wl", "wr"] },
    { id: "legs", robot: true, name: ["足式与仿人", "Legged and humanoid"],
      problem: { title: ["机器人问题：用腿走路要多少个关节", "Robot problem: how many joints does walking take"],
                 text: ["Go2 每条腿 3 个关节；G1 两条腿各 6 个，再加腰和两臂。选择 0 = Go2，1 = G1。",
                        "Go2 has 3 joints per leg; G1 has 6 per leg plus waist and arms. Select 0 = Go2, 1 = G1."] },
      params: { sel: { min: 0, max: 1, step: 1, value: 0 } }, hide: ["wl", "wr"] },
    { id: "air", robot: true, name: ["轮式与空中", "Wheeled and aerial"],
      problem: { title: ["机器人问题：没有关节也能是机器人吗", "Robot problem: can a robot have no joints"],
                 text: ["差速小车只有两个车轮关节；四旋翼一个关节也没有，整个机体在空中运动。选择 0 = 小车，1 = 四旋翼。",
                        "The cart has just two wheel joints; the quadrotor has none and moves as one body. Select 0 = cart, 1 = quadrotor."] },
      params: { sel: { min: 0, max: 1, step: 1, value: 0 } }, hide: ["wl", "wr"] },
    { id: "home", name: ["家里的扫地机器人", "The robot vacuum at home"],
      problem: { title: ["生活中的例子：扫地机器人怎样转身", "Everyday example: how a robot vacuum turns"],
                 text: ["扫地机器人与车间的 AGV 一样是差速驱动：两轮同速直行，反向则原地转。设定两轮转速后按“摆动 / 行驶”。",
                        "A robot vacuum is a differential drive like the factory AGV: equal wheel speeds go straight, opposite ones spin. Set the wheel speeds and press Swing / Drive."] },
      hide: ["sel", "amp"] },
  ],
  params: [
    { id: "sel", name: ["选择模型", "Select model"], min: 0, max: 3, step: 1, value: 0, digits: 0 },
    { id: "amp", name: ["摆动幅度", "Swing amplitude"], min: 0, max: 1, step: 0.05, value: 0.6, digits: 2 },
    { id: "wl", name: ["左轮转速", "Left wheel speed"], min: -20, max: 20, step: 1, value: 10, unit: "rad/s", digits: 0 },
    { id: "wr", name: ["右轮转速", "Right wheel speed"], min: -20, max: 20, step: 1, value: 10, unit: "rad/s", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["摆动 / 行驶", "Swing / Drive"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "prism", robot: true, text: ["在工业臂中找出手臂本身（不算手爪的手指）带有移动关节的模型。", "Among the industrial arms, find the one whose arm itself (not counting gripper fingers) has a prismatic joint."],
      demo: { scene: "arms", set: { sel: 2 }, press: [], wait: 1 } },
    { id: "most", robot: true, text: ["找出关节数最多的模型，读出它的关节数。", "Find the model with the most joints and read how many it has."],
      demo: { scene: "legs", set: { sel: 1 }, press: [], wait: 1 } },
    { id: "none", robot: true, text: ["找出没有关节的模型，看它靠什么运动。", "Find the model with no joints and see how it moves."],
      demo: { scene: "air", set: { sel: 1 }, press: ["start"], wait: 2 } },
    { id: "spin", text: ["让扫地机器人原地转一圈。", "Make the robot vacuum spin once on the spot."],
      demo: { scene: "home", set: { wl: -20, wr: 20 }, press: ["start"], wait: 20 } },
  ],
  think: ["同是“机械臂”，SCARA 与 UR5e 的工作空间为什么形状完全不同？Delta 的模型只列出 3 个关节，它真实的关节数是多少？",
          "Why do SCARA and UR5e, both “arms”, have such different workspaces? Delta's model lists 3 joints; how many joints does it really have?"],

  GROUP: { arms: ["B-ARM-UR5E", "B-ARM-PANDA", "B-SCA-WQ4", "B-PAR-DELTA"], legs: ["B-LEG-GO2", "B-HUM-G1"],
           air: ["B-EDU-DIFF", "B-UAV-X2"], home: ["B-EDU-DIFF"] },
  INFO: {
    "B-ARM-UR5E": [["UR5e 协作机械臂", "UR5e cobot"], ["工业（协作）", "industrial (collaborative)"], ["固定", "fixed"], ["串联，关节型", "serial, articulated"]],
    "B-ARM-PANDA": [["Panda 七轴机械臂", "Panda 7-axis arm"], ["工业（协作）、科研", "industrial (collaborative), research"], ["固定", "fixed"], ["串联，关节型", "serial, articulated"]],
    "B-SCA-WQ4": [["SCARA（问渠）", "SCARA (WenQuest)"], ["工业", "industrial"], ["固定", "fixed"], ["串联，SCARA", "serial, SCARA"]],
    "B-PAR-DELTA": [["Delta 并联机器人（问渠）", "Delta robot (WenQuest)"], ["工业", "industrial"], ["固定", "fixed"], ["并联（闭链）", "parallel (closed chain)"]],
    "B-LEG-GO2": [["Go2 四足机器人", "Go2 quadruped"], ["服务、科研", "service, research"], ["移动（足式），机身 6 个自由度", "mobile (legged), body 6 DOF"], ["树形：四条腿", "tree: four legs"]],
    "B-HUM-G1": [["G1 仿人机器人", "G1 humanoid"], ["科研", "research"], ["移动（足式），机身 6 个自由度", "mobile (legged), body 6 DOF"], ["树形：两腿、腰、两臂", "tree: legs, waist, arms"]],
    "B-EDU-DIFF": [["差速小车（AGV）", "differential cart (AGV)"], ["工业物流", "industrial logistics"], ["移动（轮式），车体 3 个自由度", "mobile (wheeled), body 3 DOF"], ["两个车轮", "two wheels"]],
    "B-UAV-X2": [["四旋翼 X2", "quadrotor X2"], ["服务（巡检、测绘）", "service (inspection, mapping)"], ["移动（空中），机体 6 个自由度", "mobile (aerial), body 6 DOF"], ["单个刚体，4 个旋翼", "one rigid body, 4 rotors"]],
  },
  R_W: 0.05, B_W: 0.26,

  current(api) {
    const g = this.GROUP[api.scene] || [];
    return g[Math.max(0, Math.min(g.length - 1, Math.round(api.p.sel)))];
  },
  setup3d(api, keep) {
    const T = api.three, m = api.m;
    keep.shown = null;
    keep.trace = api.trace(0x2ca02c);
    m.frame = { entry: { robot: {} }, holder: { visible: false },
                box: () => { const b = new T.Box3(); (this.GROUP[api.scene] || []).forEach((id) => b.union(m[id].box()));
                             if (api.scene === "home") b.expandByScalar(0.6); return b; } };
  },
  reset(api, s) {
    s.t = 0; s.x = 0; s.y = 0; s.h = 0; s.wl = 0; s.wr = 0; s.turn = 0;
    if (api.keep && api.keep.trace) api.keep.trace.clear();
  },
  update(dt, api, s) {
    s.t += dt;
    if (api.scene === "home") {
      const v = this.R_W * (api.p.wr + api.p.wl) / 2, om = this.R_W * (api.p.wr - api.p.wl) / this.B_W;
      s.x += v * Math.cos(s.h) * dt; s.y += v * Math.sin(s.h) * dt; s.h += om * dt; s.turn += om * dt;
      s.wl += api.p.wl * dt; s.wr += api.p.wr * dt;
      if (Math.abs(s.turn) >= 2 * Math.PI && Math.hypot(s.x, s.y) < 0.05) api.done("spin");
      if (s.t > 8 || Math.hypot(s.x, s.y) > 1.2) api.stop();
    } else if (s.t > 12) api.stop();
  },
  layout(api) {
    const g = this.GROUP[api.scene] || [], m = api.m, gap = api.scene === "arms" ? 0.9 : 1.0;
    Object.keys(this.INFO).forEach((id) => { m[id].holder.visible = g.includes(id); });
    g.forEach((id, k) => { m[id].place((k - (g.length - 1) / 2) * gap, 0); });
    api.keep.home = m["B-EDU-DIFF"].holder.position.clone();
  },
  animate(api, s) {
    const m = api.m, cur = this.current(api);
    Object.keys(this.INFO).forEach((id) => { const h = m[id]; h.opacity(id === cur || api.scene === "home" ? 1 : 0.3);
      if (id !== "B-EDU-DIFF" && id !== "B-UAV-X2") h.set(h.entry.rest || {}); });
    const h = m[cur];
    if (!h) return;
    if (api.scene === "home") {
      h.set({ left_wheel_joint: s.wl, right_wheel_joint: s.wr });
      h.holder.position.set(api.keep.home.x + s.x, api.keep.home.y, api.keep.home.z - s.y);
      h.holder.rotation.set(0, s.h, 0);
      return;
    }
    const ph = api.running ? s.t : 0;
    if (cur === "B-UAV-X2") {                                 // 没有关节：整个机体上下、转动
      const base = h.userBase || (h.userBase = h.holder.position.clone());
      h.holder.position.set(base.x, base.y + api.p.amp * 0.4 * (1 - Math.cos(ph * 1.5)), base.z);
      h.holder.rotation.set(0, api.p.amp * Math.sin(ph * 0.8), 0);
      return;
    }
    if (cur === "B-PAR-DELTA") return;                        // 闭链：只拖主动臂不能保持闭合，见第 18 章
    if (cur === "B-EDU-DIFF") { h.set({ left_wheel_joint: ph * 6, right_wheel_joint: ph * 6 }); return; }
    const o = {}, demo = h.entry.demo || {}, rest = h.entry.rest || {};
    (h.entry.joints || []).forEach((j, k) => {
      const r = demo[j.name], mid = rest[j.name] || 0;
      if (!r) return;
      o[j.name] = mid + api.p.amp * Math.sin(ph * 1.3 + k * 0.7) * (r[1] - r[0]) / 2;
    });
    h.set(o);
  },
  readouts(api, s) {
    const m = api.m;
    if (!m["B-ARM-UR5E"] || !m["B-UAV-X2"]) return [];
    const cur = this.current(api), h = m[cur], info = this.INFO[cur];
    if (!h || !info) return [];
    if (api.scene === "arms" && cur === "B-SCA-WQ4") api.done("prism");
    if (api.scene === "legs" && cur === "B-HUM-G1") api.done("most");
    if (api.scene === "air" && cur === "B-UAV-X2") api.done("none");
    const js = h.entry.joints || [], nr = js.filter((j) => j.type !== "prismatic").length, np = js.length - nr;
    const mass = ((h.entry.robot || {}).links || []).reduce((a, l) => a + (l.mass_kg || 0), 0);
    const ds = ((h.entry.datasheet || {}).values) || {};
    const rows = [[["模型", "model"], api.P(info[0])], [["用途", "use"], api.P(info[1])], [["基座", "base"], api.P(info[2])],
                  [["结构", "structure"], api.P(info[3])],
                  [["关节表中的关节", "joints in the joint table"], api.T(`${js.length} 个（转动 ${nr}，移动 ${np}）`, `${js.length} (revolute ${nr}, prismatic ${np})`)]];
    if (mass > 0) rows.push([["连杆质量之和（模型）", "sum of link masses (model)"], api.fmt(mass, 2) + " kg"]);
    const sheet = [];
    if (ds.payload_kg) sheet.push(api.T(`负载 ${ds.payload_kg} kg`, `payload ${ds.payload_kg} kg`));
    if (ds.reach_mm) sheet.push(api.T(`工作半径 ${ds.reach_mm} mm`, `reach ${ds.reach_mm} mm`));
    if (ds.weight_kg) sheet.push(api.T(`重量 ${ds.weight_kg} kg`, `weight ${ds.weight_kg} kg`));
    if (ds.dof) sheet.push(api.T(`自由度 ${ds.dof}`, `DOF ${ds.dof}`));
    rows.push([["厂家参数表", "datasheet"], sheet.length ? sheet.join(api.T("，", ", ")) : api.T("（问渠自建或无官方参数）", "(WenQuest-built or none published)")]);
    if (api.scene === "home") rows.push([["累计转过", "total turn"], api.fmt(s.turn * 180 / Math.PI, 0) + "°"]);
    return rows;
  },
  draw(api, s) {
    if (api.keep.shown !== api.scene) {
      api.keep.shown = api.scene;
      this.layout(api);
      api.m["B-UAV-X2"].userBase = null;
      api.view(30, 18, api.scene === "home" ? 0.8 : api.scene === "arms" ? 1.7 : 1.3, api.m.frame);
    }
    this.animate(api, s);
    if (api.scene === "home" && api.running && api.keep.trace) {
      const c = api.m["B-EDU-DIFF"].holder.position;
      api.keep.trace.add(new api.three.Vector3(c.x, 0.01, c.z));
    }
  },
});
