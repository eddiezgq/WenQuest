/* 首页首屏：立体的厂情中枢（第 91 轮）。三层——设备、数据、事件——叠成一座立体网络，不连续旋转，按镜头设计换方向和远近：每条事件链“远景→近景→中景”，平滑过去后静止；也可以拖动换方向；
   数据包从设备往上流，每隔几秒走一条真实的“事件链”：一个数据异常如何一路映射到工单、质量、采购、交期和决策。
   对象名取自问渠数字工厂（减速器厂 WQR-105、机器人厂 WQ-CR5、实验 7 情景）。纯 Canvas，不依赖外部库。
   用法：WQHub3D.start(canvas, {chain: 元素, count: 元素, rate: 元素}) */
(function () {
  const LAYERS = [
    { y: -1, zh: "设备层 · 车间实况", en: "ASSETS · shop floor" },
    { y: 0, zh: "数据层 · 实时数据", en: "DATA · live signals" },
    { y: 1, zh: "事件层 · 业务与决策", en: "EVENTS · business & decisions" },
  ];
  // 设备（第 0 层）：[编号, 中文, 英文, x, z]
  const ASSETS = [
    ["CNC-L01", "数控车床 L01", "CNC lathe L01", -1.5, -1.1], ["CNC-L02", "数控车床 L02", "CNC lathe L02", -0.75, -1.25],
    ["MC-03", "加工中心 03", "Machining ctr 03", 0.0, -1.3], ["HT-01", "热处理炉", "Heat-treat furnace", 0.8, -1.15],
    ["GR-01", "磨齿机", "Gear grinder", 1.5, -0.9], ["ASM-01", "减速器装配线", "Reducer assembly", 1.55, -0.05],
    ["TB-01", "出厂试验台", "End-of-line test", 1.4, 0.75], ["AS-WH", "立体仓库", "Automated store", -1.6, -0.2],
    ["AGV-1", "AGV 1", "AGV 1", -0.9, -0.35], ["AGV-2", "AGV 2", "AGV 2", 0.3, -0.45], ["AGV-3", "AGV 3", "AGV 3", 0.85, 0.35],
    ["JT-01", "关节测试台", "Joint test bench", -1.35, 0.75], ["RI-01", "负载跑合台", "Load run-in bench", -0.6, 1.0],
    ["CR5-L", "协作机器人总装", "Cobot final assembly", 0.2, 1.2], ["EM-01", "总电表", "Main meter", 1.0, 1.2],
    ["F-002", "客户现场机器人 F002", "Field robot F002", -1.6, 1.35], ["CMM", "三坐标测量机", "CMM", 0.1, 0.35],
  ];
  // 数据（第 1 层）：[编号, 所属设备, 中文, 英文, 单位, 基准值, 波动]
  const TAGS = [
    ["vib2", "CNC-L02", "主轴振动", "spindle vibration", "mm/s", 2.1, 0.3], ["load1", "CNC-L01", "主轴负载", "spindle load", "%", 62, 6],
    ["tool1", "CNC-L01", "刀具寿命", "tool life", "%", 71, 1], ["oee3", "MC-03", "OEE", "OEE", "%", 78, 3],
    ["temp", "HT-01", "炉温", "furnace temp", "°C", 860, 4], ["cp", "HT-01", "碳势", "carbon potential", "%C", 0.82, 0.01],
    ["fpe", "GR-01", "齿形误差", "profile error", "µm", 4.2, 0.4], ["spc", "GR-01", "SPC 控制图", "SPC chart", "σ", 0.9, 0.2],
    ["takt", "ASM-01", "节拍", "takt", "s", 96, 3], ["torq", "ASM-01", "拧紧扭矩", "bolt torque", "N·m", 24.5, 0.4],
    ["noise", "TB-01", "噪声", "noise", "dB", 62, 1.2], ["eff", "TB-01", "传动效率", "efficiency", "%", 94.6, 0.4],
    ["stock", "AS-WH", "RM-45-D50 库存", "RM-45-D50 stock", "pcs", 420, 6], ["loc", "AS-WH", "库位占用", "bin use", "%", 81, 1],
    ["bat1", "AGV-1", "电量", "battery", "%", 76, 1], ["bat2", "AGV-2", "电量", "battery", "%", 64, 1], ["pos3", "AGV-3", "位置", "position", "", 0, 0],
    ["blash", "JT-01", "J2 背隙", "J2 backlash", "′", 0.9, 0.05], ["stiff", "JT-01", "扭转刚度", "torsional stiffness", "kN·m/rad", 12.4, 0.2],
    ["simr", "RI-01", "仿真/实测偏差", "sim vs measured", "%", 3.1, 0.4], ["cycle", "CR5-L", "总装节拍", "assembly cycle", "min", 42, 1],
    ["kwh", "EM-01", "峰时功率", "peak power", "kW", 312, 8], ["fbl", "F-002", "现场背隙", "field backlash", "′", 1.1, 0.04],
    ["fhr", "F-002", "运行小时", "run hours", "h", 3120, 1], ["dim", "CMM", "孔径 Ø50 H7", "bore Ø50 H7", "mm", 50.012, 0.002],
  ];
  // 事件（第 2 层）：[编号, 中文, 英文, x, z]
  const EVENTS = [
    ["SO", "订单 SO-2045 · 交期", "Order SO-2045 · due date", -0.2, -1.2], ["SCHED", "APS 排产", "APS schedule", -1.2, -0.8],
    ["WO", "工单 WO-5521", "Work order WO-5521", -1.55, 0.1], ["MAINT", "预测性维护 MO-1182", "Predictive maint. MO-1182", -0.9, -0.05],
    ["QA", "质量预警", "Quality alert", 0.9, -0.55], ["8D", "8D-0117 追因", "8D-0117 root cause", 1.5, 0.15],
    ["LOT", "批次追溯 B-1036", "Lot trace B-1036", 0.85, 0.75], ["MRP", "MRP 缺料", "MRP shortage", -0.15, 0.45],
    ["PR", "采购申请 PR-332", "Purchase req. PR-332", -0.95, 1.0], ["SUP", "供应商交期", "Supplier lead time", -0.1, 1.35],
    ["SVC", "售后工单 SV-087", "Service ticket SV-087", 0.65, 1.4], ["ENERGY", "能耗异常", "Energy anomaly", 1.55, -0.85],
    ["AI", "AI 简报", "AI briefing", 0.25, -0.3], ["GM", "厂长决策", "Plant manager decides", 0.0, -0.75],
  ];
  // 事件链：数据异常 → 一路映射到业务事件
  const CHAINS = [
    { zh: "主轴振动超限 → 维护 → 重排产 → 交期风险", en: "Vibration spike → maintenance → reschedule → due-date risk",
      steps: [["CNC-L02", "数控车床 L02 运行中", "CNC lathe L02 running"], ["vib2", "主轴振动 7.8 mm/s ↑（阈值 4.5）", "spindle vibration 7.8 mm/s ↑ (limit 4.5)", 7.8],
        ["MAINT", "自动开预测性维护 MO-1182", "predictive maintenance MO-1182 opened"], ["SCHED", "APS 重排 3 张工单", "APS reschedules 3 work orders"],
        ["SO", "SO-2045 交期风险 −0.5 天", "SO-2045 due date at risk, −0.5 day"], ["AI", "AI 简报：附数据来源", "AI briefing, with data sources"], ["GM", "厂长决定：加一班", "Plant manager: add a shift"]] },
    { zh: "齿形误差连升 7 点 → 质量预警 → 8D → 批次隔离", en: "Profile error trend → quality alert → 8D → lot hold",
      steps: [["GR-01", "磨齿机 GR-01", "Gear grinder GR-01"], ["fpe", "齿形误差 6.1 µm，连升 7 点", "profile error 6.1 µm, 7 points rising", 6.1],
        ["spc", "SPC 判异：规则 3", "SPC rule 3 violated", 2.6], ["QA", "质量预警，停机确认", "quality alert, stop and verify"], ["8D", "开 8D-0117 追因：砂轮修整周期", "8D-0117: dressing interval"],
        ["LOT", "追溯批次 B-1036，隔离 120 件", "trace lot B-1036, hold 120 pcs"], ["AI", "AI 简报", "AI briefing"]] },
    { zh: "库存低于安全线 → MRP 缺料 → 采购 → 工单延后", en: "Stock below safety level → shortage → purchase → WO delayed",
      steps: [["AS-WH", "立体仓库", "Automated store"], ["stock", "RM-45-D50 库存 180（安全线 300）", "RM-45-D50 stock 180 (safety 300)", 180],
        ["MRP", "MRP 算出缺料 640 件", "MRP: short 640 pcs"], ["PR", "自动起草采购申请 PR-332", "purchase requisition PR-332 drafted"], ["SUP", "供应商交期 5 天", "supplier lead time 5 days"],
        ["WO", "WO-5521 延后 1 天", "WO-5521 slips 1 day"], ["SO", "SO-2045 交期复核", "SO-2045 due date re-checked"]] },
    { zh: "现场机器人背隙超限 → 售后 → 追到减速器批次 → 复测", en: "Field backlash drift → service → reducer lot → retest",
      steps: [["F-002", "客户现场机器人 F002", "Field robot F002"], ["fbl", "J2 背隙 1.42′ ↑（限值 1.3′）", "J2 backlash 1.42′ ↑ (limit 1.3′)", 1.42],
        ["SVC", "售后工单 SV-087", "service ticket SV-087"], ["LOT", "追到减速器批次 B-1036", "traced to reducer lot B-1036"], ["JT-01", "关节测试台复测同批 6 台", "joint bench retests 6 units"],
        ["blash", "复测背隙 1.35′", "retest backlash 1.35′", 1.35], ["8D", "供应商 8D", "supplier 8D"], ["AI", "AI 简报", "AI briefing"]] },
    { zh: "峰时功率超限 → 能耗异常 → 排产错峰", en: "Peak power over → energy anomaly → shift the load",
      steps: [["EM-01", "总电表", "Main meter"], ["kwh", "峰时功率 388 kW ↑", "peak power 388 kW ↑", 388], ["temp", "热处理炉正在升温", "furnace ramping up", 905],
        ["ENERGY", "能耗异常", "energy anomaly"], ["SCHED", "APS 把热处理移到谷时", "APS moves heat-treat off-peak"], ["GM", "厂长确认", "plant manager confirms"]] },
    { zh: "孔径偏大 → 质量预警 → 刀具寿命 → 换刀", en: "Bore oversize → alert → tool life → tool change",
      steps: [["CMM", "三坐标抽检", "CMM sampling"], ["dim", "Ø50 H7 实测 50.029（上限 50.025）", "Ø50 H7 measured 50.029 (max 50.025)", 50.029],
        ["QA", "质量预警", "quality alert"], ["tool1", "追到刀具寿命 4%", "traced to tool life 4%", 4], ["CNC-L01", "数控车床 L01 换刀", "CNC lathe L01 tool change"],
        ["WO", "WO-5521 补做 3 件", "WO-5521 rework 3 pcs"], ["AI", "AI 简报", "AI briefing"]] },
  ];

  function start(cv, ui) {
    const ctx = cv.getContext("2d");
    const lang = () => (document.documentElement.lang || "zh").startsWith("en") ? "en" : "zh";
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    // ---- 节点 ----
    const N = [], byId = {};
    const add = (n) => { n.i = N.length; N.push(n); byId[n.id] = n; return n; };
    ASSETS.forEach(([id, zh, en, x, z]) => add({ id, zh, en, L: 0, x, y: -1, z, kind: "asset" }));
    TAGS.forEach(([id, a, zh, en, unit, v0, dv], k) => {
      const A = byId[a], ang = k * 2.39996, r = 0.18 + (k % 3) * 0.07;
      add({ id, zh, en, unit, v0, dv, v: v0, L: 1, x: A.x + Math.cos(ang) * r, y: 0, z: A.z + Math.sin(ang) * r, kind: "tag", parent: A });
    });
    // 每台设备再带几路常规信号（状态、电流、温度……），让数据层像真实的点表一样密
    const MINOR = [["状态", "state", ""], ["电流", "current", "A"], ["温度", "temp", "°C"], ["计数", "count", "pcs"], ["报警码", "alarm code", ""]];
    ASSETS.forEach(([a], k) => MINOR.slice(0, 2 + (k % 3)).forEach(([zh, en, unit], j) => {
      const A = byId[a], ang = k * 1.3 + j * 2.1 + 0.6, r = 0.12 + j * 0.05, v0 = unit === "A" ? 12 + k : unit === "°C" ? 38 + k : unit === "pcs" ? 1200 + k * 37 : 0;
      add({ id: `${a}-m${j}`, zh: `${A.zh} ${zh}`, en: `${A.en} ${en}`, unit, v0, dv: v0 ? v0 * 0.02 : 0, v: v0, L: 1, x: A.x + Math.cos(ang) * r, y: 0, z: A.z + Math.sin(ang) * r, kind: "tag", minor: true, parent: A });
    }));
    EVENTS.forEach(([id, zh, en, x, z]) => add({ id, zh, en, L: 2, x, y: 1, z, kind: "event" }));
    // ---- 边：设备→数据（竖线）、数据→事件（规则）、事件→事件（因果） ----
    const E = [];
    const link = (a, b, k) => { if (byId[a] && byId[b] && !E.some((e) => e.a === byId[a] && e.b === byId[b])) E.push({ a: byId[a], b: byId[b], k, hot: 0 }); };
    TAGS.forEach(([id, a]) => link(a, id, "phys"));
    N.filter((x) => x.minor).forEach((x) => link(x.parent.id, x.id, "phys"));
    CHAINS.forEach((c) => c.steps.forEach((s, i) => { if (i) link(c.steps[i - 1][0], s[0], "map"); }));
    [["load1", "SCHED"], ["oee3", "SCHED"], ["takt", "WO"], ["torq", "QA"], ["noise", "QA"], ["eff", "QA"], ["loc", "MRP"], ["bat1", "SCHED"],
      ["bat2", "SCHED"], ["stiff", "QA"], ["simr", "AI"], ["cycle", "WO"], ["fhr", "SVC"], ["cp", "QA"], ["QA", "AI"], ["MAINT", "AI"], ["ENERGY", "AI"],
      ["SVC", "AI"], ["WO", "SO"], ["MRP", "SCHED"], ["AI", "GM"], ["SO", "GM"], ["8D", "AI"], ["LOT", "SO"]].forEach(([a, b]) => link(a, b, "map"));
    const deg = {}; E.forEach((e) => { deg[e.a.id] = (deg[e.a.id] || 0) + 1; deg[e.b.id] = (deg[e.b.id] || 0) + 1; });
    if (ui.count) ui.count.textContent = `${N.length} / ${E.length}`;
    // ---- 视角 ----
    let W = 0, H = 0, dpr = 1, yaw = -0.6, pitch = 0.52, spin = 0,   /* 不连续旋转（Eddie 11-05：转起来晃眼）；每换一条事件链换一个观察方向，平滑过去后静止 */ drag = null, hover = null;
    function fit() {
      dpr = Math.min(devicePixelRatio || 1, 2); const r = cv.getBoundingClientRect(); W = r.width; H = r.height;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function view() {
      const wide = W > 900, H = ui.area ? Math.min(cv.clientHeight, ui.area.offsetTop + ui.area.offsetHeight) : cv.clientHeight;  // 只在首屏文字那一块里摆
      return { cx: wide ? W * 0.72 : W * 0.5, cy: wide ? H * (ui.area ? 0.52 : 0.47) : Math.min(H * 0.3, innerHeight * 0.27), s: wide ? Math.min(W * 0.125, H * 0.165) : Math.min(W * 0.21, innerHeight * 0.1), wide };
    }
    let zoom = 1, fx = 0, fy = 0, fz = 0;   // 镜头：远近（zoom）和对准的点（fx, fy, fz）
    function P(x, y, z, V) {           // 先移到镜头对准的点，绕竖轴转 yaw，再俯仰 pitch，透视投影，按远近缩放
      x -= fx; z -= fz; y -= fy / 1.2;
      const cy = Math.cos(yaw), sy = Math.sin(yaw), x1 = x * cy - z * sy, z1 = x * sy + z * cy;
      const yy = y * 1.2, cp = Math.cos(pitch), sp = Math.sin(pitch), y2 = yy * cp - z1 * sp, z2 = yy * sp + z1 * cp;
      const f = 4.2 / (4.2 + z2);
      return { X: V.cx + x1 * V.s * zoom * f, Y: V.cy - y2 * V.s * zoom * f, f: f * Math.sqrt(zoom), d: z2 };
    }
    // ---- 数据包 ----
    const packets = [];
    function emit(e, col, speed, big) { packets.push({ e, t: 0, col, sp: speed || 0.012 + Math.random() * 0.01, big }); }
    // ---- 事件链 ----
    let chainIdx = -1, chain = null, stepT = 0, stepI = 0, since = 0, n = 0;
    // 几个固定的观察方向：每条事件链换一个，用 1.8 秒缓过去，然后静止
    // 镜头设计：每条事件链 = 远景（换一个观察方向看全厂）→ 近景（推到这条链上，看清数据和事件）→ 中景（拉开一点看它牵动了哪些事）
    // 每次换镜头用 1.8 秒缓过去，然后静止；不连续旋转
    const VIEWS = [[-0.6, 0.52], [0.35, 0.62], [-1.35, 0.45], [0.95, 0.5], [-0.15, 0.78], [-2.0, 0.55]];
    let aim = null;
    function shot(y1, p1, z1, f1) {
      aim = { t: 0, from: [yaw, pitch, zoom, fx, fy, fz], to: [y1, p1, z1, f1[0], f1[1], f1[2]] };
    }
    function centroid() {
      const ns = chain.steps.map((s) => byId[s[0]]).filter(Boolean);
      return [0, 1, 2].map((k) => ns.reduce((a, x) => a + [x.x, x.y * 1.2, x.z][k], 0) / ns.length);
    }
    function nextChain() {
      chainIdx = (chainIdx + 1) % CHAINS.length;
      if (n > 0) { const v = VIEWS[n % VIEWS.length]; shot(v[0], v[1], 1, [0, 0, 0]); } chain = CHAINS[chainIdx]; stepI = 0; stepT = 0; n++;
      N.forEach((x) => { x.hl = 0; }); E.forEach((e) => { e.hot = 0; });
      showChain();
    }
    function showChain() {
      if (!ui.chain || !chain) return;
      const L = lang();
      ui.chain.innerHTML = `<b>#${String(n).padStart(3, "0")}</b> ` + chain[L].replace(/&/g, "&amp;").replace(/</g, "&lt;");
      if (ui.steps) {
        ui.steps.innerHTML = chain.steps.slice(0, stepI + 1).map((s, i) => `<li class="${i === stepI ? "now" : ""}">${(L === "zh" ? s[1] : s[2]).replace(/</g, "&lt;")}</li>`).join("");
      }
    }
    new MutationObserver(showChain).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
    // ---- 交互：拖动旋转、悬停看标签 ----
    cv.addEventListener("pointerdown", (e) => { drag = { x: e.clientX, y: e.clientY, yaw, pitch }; aim = null; cv.setPointerCapture(e.pointerId); });
    cv.addEventListener("pointermove", (e) => {
      if (drag) { yaw = drag.yaw + (e.clientX - drag.x) * 0.006; pitch = Math.max(0.15, Math.min(1.1, drag.pitch + (e.clientY - drag.y) * 0.004)); return; }
      const r = cv.getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top, V = view();
      let best = null, bd = 14 * 14;
      N.forEach((x) => { const p = P(x.x, x.y, x.z, V), d = (p.X - mx) ** 2 + (p.Y - my) ** 2; if (d < bd) { bd = d; best = x; } });
      hover = best;
    });
    cv.addEventListener("pointerup", () => { drag = null; });
    cv.addEventListener("pointerleave", () => { drag = null; hover = null; });
    // ---- 画 ----
    const COL = { asset: "#5cb8d6", tag: "#9fe3c4", event: "#f2b705", hot: "#ffcf3a", alarm: "#ff5d5d" };
    function plane(Ly, V, title) {
      const c = [[-1.85, -1.5], [1.85, -1.5], [1.85, 1.55], [-1.85, 1.55]].map(([x, z]) => P(x, Ly, z, V));
      ctx.beginPath(); c.forEach((p, i) => (i ? ctx.lineTo(p.X, p.Y) : ctx.moveTo(p.X, p.Y))); ctx.closePath();
      const g = ctx.createLinearGradient(c[0].X, c[0].Y, c[2].X, c[2].Y);
      g.addColorStop(0, "rgba(92,184,214,0.07)"); g.addColorStop(1, "rgba(242,183,5,0.04)");
      ctx.fillStyle = g; ctx.fill(); ctx.strokeStyle = "rgba(143,161,168,0.22)"; ctx.lineWidth = 1; ctx.stroke();
      // 网格
      ctx.strokeStyle = "rgba(143,161,168,0.06)";
      for (let i = -1.5; i <= 1.56; i += 0.34) { const a = P(-1.85, Ly, i, V), b = P(1.85, Ly, i, V); ctx.beginPath(); ctx.moveTo(a.X, a.Y); ctx.lineTo(b.X, b.Y); ctx.stroke(); }
      for (let i = -1.85; i <= 1.86; i += 0.37) { const a = P(i, Ly, -1.5, V), b = P(i, Ly, 1.55, V); ctx.beginPath(); ctx.moveTo(a.X, a.Y); ctx.lineTo(b.X, b.Y); ctx.stroke(); }
      // 层名放在最左边的角上
      const right = c.reduce((m, p) => (p.X > m.X ? p : m), c[0]);
      ctx.fillStyle = "rgba(233,238,240,0.6)"; ctx.font = `600 ${V.wide ? 12 : 10}px ui-monospace, Menlo, monospace`;
      ctx.textAlign = right.X + 10 + ctx.measureText(title).width > W ? "right" : "left";
      ctx.fillText(title, ctx.textAlign === "right" ? Math.min(right.X, W - 8) : right.X + 10, right.Y + (ctx.textAlign === "right" ? -10 : 4));
    }
    function veil(V) {                  // 宽屏：左边留给标题，镜头推近时网络在那里淡出
      if (!V.wide) return;
      const g = ctx.createLinearGradient(W * 0.36, 0, W * 0.52, 0);
      g.addColorStop(0, "rgba(10,18,22,0.92)"); g.addColorStop(1, "rgba(10,18,22,0)");
      ctx.fillStyle = g; ctx.fillRect(0, 0, W * 0.52, H);
    }
    function frame(dt) {
      const V = view(), L = lang();
      ctx.clearRect(0, 0, W, H);
      if (!drag) yaw += spin * dt;
      if (aim && !drag) { aim.t = Math.min(1, aim.t + dt / 1800); const k = aim.t < 0.5 ? 2 * aim.t * aim.t : 1 - Math.pow(-2 * aim.t + 2, 2) / 2;
        [yaw, pitch, zoom, fx, fy, fz] = aim.from.map((a, i) => a + (aim.to[i] - a) * k); if (aim.t >= 1) aim = null; }
      [2, 1, 0].forEach((k) => plane(LAYERS[k].y, V, LAYERS[k][L]));
      const pts = N.map((x) => P(x.x, x.y, x.z, V));
      // 边
      E.forEach((e) => {
        const a = pts[e.a.i], b = pts[e.b.i];
        const hot = e.hot > 0.01, phys = e.k === "phys";
        ctx.strokeStyle = hot ? `rgba(255,207,58,${0.35 + 0.65 * e.hot})` : phys ? "rgba(92,184,214,0.18)" : "rgba(242,183,5,0.12)";
        ctx.lineWidth = hot ? 2.2 : 1;
        ctx.beginPath(); ctx.moveTo(a.X, a.Y);
        if (phys) ctx.lineTo(b.X, b.Y);
        else { const mx = (a.X + b.X) / 2, my = Math.min(a.Y, b.Y) - 18 * V.s / 200; ctx.quadraticCurveTo(mx, my, b.X, b.Y); }
        ctx.stroke();
        e.hot *= 0.995;
      });
      // 数据包
      for (let i = packets.length - 1; i >= 0; i--) {
        const p = packets[i]; p.t += p.sp * dt / 16;
        if (p.t >= 1) { packets.splice(i, 1); continue; }
        const a = pts[p.e.a.i], b = pts[p.e.b.i], t = p.t;
        let X, Y;
        if (p.e.k === "phys") { X = a.X + (b.X - a.X) * t; Y = a.Y + (b.Y - a.Y) * t; }
        else { const mx = (a.X + b.X) / 2, my = Math.min(a.Y, b.Y) - 18 * V.s / 200; X = (1 - t) ** 2 * a.X + 2 * (1 - t) * t * mx + t * t * b.X; Y = (1 - t) ** 2 * a.Y + 2 * (1 - t) * t * my + t * t * b.Y; }
        ctx.fillStyle = p.col; ctx.globalAlpha = p.big ? 1 : 0.8;
        ctx.beginPath(); ctx.arc(X, Y, p.big ? 3.6 : 1.8, 0, 7); ctx.fill();
        if (p.big) { ctx.globalAlpha = 0.25; ctx.beginPath(); ctx.arc(X, Y, 9, 0, 7); ctx.fill(); }
        ctx.globalAlpha = 1;
      }
      // 节点（远的先画）
      const order = N.map((x) => x.i).sort((i, j) => pts[j].d - pts[i].d);
      ctx.textAlign = "left";
      order.forEach((i) => {
        const x = N[i], p = pts[i], hl = x.hl || 0;
        const base = x.kind === "asset" ? 4.2 : x.kind === "event" ? 4.8 : 2.4;
        const r = (base + Math.min(3, (deg[x.id] || 0) * 0.25)) * p.f * (1 + hl * 0.6);
        const col = hl > 0.05 ? (x.alarm ? COL.alarm : COL.hot) : COL[x.kind];
        if (hl > 0.05) { ctx.fillStyle = col; ctx.globalAlpha = 0.18 * hl; ctx.beginPath(); ctx.arc(p.X, p.Y, r * 3.2, 0, 7); ctx.fill(); ctx.globalAlpha = 1; }
        ctx.fillStyle = col;
        if (x.kind === "asset") { ctx.fillRect(p.X - r, p.Y - r * 0.7, r * 2, r * 1.4); }
        else if (x.kind === "event") { ctx.beginPath(); ctx.moveTo(p.X, p.Y - r); ctx.lineTo(p.X + r, p.Y); ctx.lineTo(p.X, p.Y + r); ctx.lineTo(p.X - r, p.Y); ctx.closePath(); ctx.fill(); }
        else { ctx.beginPath(); ctx.arc(p.X, p.Y, r, 0, 7); ctx.fill(); }
        // 标签：设备、事件常显（淡），数据只在高亮或悬停时显示
        const show = hl > 0.05 || x === hover || (x.kind !== "tag" && V.wide);
        if (show) {
          let txt = L === "zh" ? x.zh : x.en;
          if (x.kind === "tag") txt += ` ${fmt(x.v)}${x.unit ? " " + x.unit : ""}`;
          if (hl > 0.05 && x.note) txt = x.note;
          ctx.font = hl > 0.05 || x === hover ? `600 ${V.wide ? 13 : 11}px "Noto Sans SC","PingFang SC",system-ui,sans-serif` : `400 ${V.wide ? 11 : 9}px "Noto Sans SC","PingFang SC",system-ui,sans-serif`;
          if (hl > 0.05 || x === hover) {           // 高亮标签加底，免得压在网上看不清
            const w = ctx.measureText(txt).width;
            ctx.fillStyle = "rgba(10,18,22,0.82)"; ctx.fillRect(p.X + r + 2, p.Y - 10, w + 8, 19);
            ctx.strokeStyle = x.alarm ? "rgba(255,93,93,0.7)" : "rgba(242,183,5,0.55)"; ctx.lineWidth = 1; ctx.strokeRect(p.X + r + 2, p.Y - 10, w + 8, 19);
          }
          ctx.fillStyle = hl > 0.05 || x === hover ? "rgba(255,244,214,0.98)" : "rgba(233,238,240,0.32)";
          ctx.fillText(txt, p.X + r + 6, p.Y + 4);
        }
        x.hl = hl * 0.996;
      });
    }
    const _frame = frame; frame = (dt) => { _frame(dt); veil(view()); };
    const fmt = (v) => (Math.abs(v) >= 100 ? v.toFixed(0) : Math.abs(v) >= 10 ? v.toFixed(1) : Math.abs(v) >= 1 ? v.toFixed(2) : v.toFixed(3));
    // ---- 时间推进：数据跳动、数据包、事件链 ----
    let rate = 0, rateT = 0;
    function tick(dt) {
      // 数据跳动 + 背景数据包（设备→数据，数据→事件）
      N.forEach((x) => { if (x.kind === "tag" && !x.hold) x.v = x.v0 + (Math.random() - 0.5) * 2 * x.dv; });
      if (Math.random() < 0.55) { const e = E[(Math.random() * E.length) | 0]; emit(e, e.k === "phys" ? "#5cb8d6" : "#9fe3c4"); rate++; }
      rateT += dt; if (rateT > 1000) { if (ui.rate) ui.rate.textContent = String(rate * 60); rate = 0; rateT = 0; }
      // 事件链：每 1.6 秒走一步
      since += dt;
      if (!chain || (stepI >= chain.steps.length - 1 && since > 4200)) { nextChain(); since = 0; light(0); return; }
      if (since > 1600 && stepI < chain.steps.length - 1) {
        stepI++; since = 0; light(stepI);
        if (stepI === 2) { const c = centroid(); shot(yaw + 0.4, 0.62, 1.75, c); }                       // 近景
        if (stepI === chain.steps.length - 1) { const c = centroid(); shot(yaw - 0.25, 0.5, 1.3, c.map((v) => v * 0.6)); } // 中景
      }
    }
    function light(i) {
      const s = chain.steps[i], x = byId[s[0]]; if (!x) return;
      x.hl = 1; x.note = (lang() === "zh" ? s[1] : s[2]); x.alarm = s.length > 3;
      if (s.length > 3 && x.kind === "tag") { x.v = s[3]; x.hold = true; setTimeout(() => { x.hold = false; }, 6000); }
      if (i) { const prev = byId[chain.steps[i - 1][0]], e = E.find((e) => (e.a === prev && e.b === x) || (e.b === prev && e.a === x)); if (e) { e.hot = 1; for (let k = 0; k < 5; k++) setTimeout(() => emit(e, "#ffcf3a", 0.035, true), k * 120); } }
      showChain();
    }
    fit(); addEventListener("resize", fit);
    if (reduce) { nextChain(); for (let i = 0; i < chain.steps.length; i++) light(i); frame(16); return; }
    let visible = true, last = performance.now();
    new IntersectionObserver((e) => { visible = e[0].isIntersecting; }).observe(cv);
    (function loop(now) {
      const dt = Math.min(50, (now || performance.now()) - last); last = now || performance.now();
      if (visible && !document.hidden) { tick(dt); frame(dt); }
      requestAnimationFrame(loop);
    })();
  }
  window.WQHub3D = { start };
})();
