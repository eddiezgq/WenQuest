// 实验 33.2 轴的结构设计核对（配 33.2 节）。调各段尺寸和圆角，按“核对”逐条检查结构设计规则，像设计评审一样列出问题。
// 两个场景：WQR-105 输出轴（轴承 6207）；小型减速电机的输出轴（轴承 608）。规则相同，数据不同。
const DATA33_2 = {
  robot: { d: 35, D: 72, B: 17, rs: 1.1, da: 42, hub: 55, dGear: 40, dExt: 30, keyB: 8, keyH: 7, T: 350, cplHub: 70 },
  life: { d: 8, D: 22, B: 7, rs: 0.3, da: 10, hub: 30, dGear: 10, dExt: 8, keyB: 3, keyH: 3, T: 4, cplHub: 20 },
};
const SIGP33_2 = 135;      // 键的许用挤压应力 MPa（与数字工厂参数配置器相同）
function rules33_2(api) {
  const s = DATA33_2[api.scene === "life" ? "life" : "robot"], p = api.p;
  const keyCap = SIGP33_2 * s.dExt * (s.keyH / 2) * (p.key - s.keyB) / 2 / 1000;      // N·m
  return [
    { zh: "轴环定位高度 h ≥ 0.07d", en: "collar height h ≥ 0.07d", ok: (p.collar - s.dGear) / 2 >= 0.07 * s.dGear,
      v: ((p.collar - s.dGear) / 2).toFixed(1) + " ≥ " + (0.07 * s.dGear).toFixed(1) },
    { zh: "轴肩直径 ≥ 轴承安装尺寸 da,min", en: "shoulder ≥ bearing da,min", ok: p.shoulder >= s.da, v: p.shoulder + " ≥ " + s.da },
    { zh: "轴肩直径 ≤ 内圈挡边直径（留拆卸空间）", en: "shoulder ≤ inner-ring land (room for a puller)", ok: p.shoulder <= s.d + 0.33 * (s.D - s.d),
      v: p.shoulder + " ≤ " + (s.d + 0.33 * (s.D - s.d)).toFixed(1) },
    { zh: "圆角 r < 轴承倒角 r_s,min", en: "fillet r < bearing chamfer", ok: p.r < s.rs, v: p.r.toFixed(1) + " < " + s.rs },
    { zh: "齿轮位比轮毂短 2–3 mm", en: "seat 2–3 mm shorter than the hub", ok: s.hub - p.seat >= 2 && s.hub - p.seat <= 3,
      v: s.hub + " − " + p.seat + " = " + (s.hub - p.seat) },
    { zh: "键长 ≤ 轮毂长 − 5", en: "key ≤ hub − 5", ok: p.key <= s.cplHub - 5, v: p.key + " ≤ " + (s.cplHub - 5) },
    { zh: "键的挤压承载 ≥ 转矩", en: "key capacity ≥ torque", ok: keyCap >= s.T, v: keyCap.toFixed(0) + " ≥ " + s.T + " N·m" },
  ];
}
WQ.lab({
  title: ["实验 33.2 轴的结构设计核对", "Lab 33.2 Checking a shaft layout"],
  goal: ["调轴环、轴肩、圆角、齿轮位和键的尺寸，按结构设计规则逐条核对，找出每条规则管的是什么。",
         "Adjust the collar, shoulder, fillet, gear seat and key, check the layout rules one by one, and see what each rule protects."],
  scenes: [
    { id: "robot", robot: true, name: ["WQR-105 输出轴", "WQR-105 output shaft"],
      problem: { title: ["工程问题：输出轴 B 版的结构评审", "Engineering problem: design review of the rev. B output shaft"],
                 text: ["轴承 6207（d35 × D72 × 17，倒角 1.1），齿轮毂宽 55，外伸段 Ø30 装联轴器（轮毂长 70），额定转矩 350 N·m。把尺寸调到七条规则全部通过。",
                        "Bearings 6207 (35 × 72 × 17, chamfer 1.1), gear hub 55, Ø30 extension with a 70 mm coupling hub, rated torque 350 N·m. Make all seven rules pass."] } },
    { id: "life", name: ["小型减速电机输出轴", "Small gearmotor output shaft"],
      params: { collar: { min: 9, max: 14, step: 0.5, value: 11 }, shoulder: { min: 8.5, max: 16, step: 0.5, value: 9 },
                r: { min: 0.1, max: 1.0, step: 0.1, value: 0.5 }, seat: { min: 24, max: 32, step: 1, value: 30 }, key: { min: 8, max: 20, step: 1, value: 10 } },
      problem: { title: ["生活中的例子：电动窗帘、扫地机里的小减速电机", "Everyday example: the gearmotor in a curtain drive or robot vacuum"],
                 text: ["输出轴上装一个小齿轮（毂宽 30）、两个 608 轴承（d8 × D22 × 7，倒角 0.3），外伸端用 3 × 3 的键带动负载，转矩 4 N·m。同样的规则，换一组尺寸再核对一遍。",
                        "A small gear (hub 30) and two 608 bearings (8 × 22 × 7, chamfer 0.3); the extension drives the load with a 3 × 3 key at 4 N·m. Same rules, a different set of sizes."] } },
  ],
  params: [
    { id: "collar", name: ["轴环直径", "Collar diameter"], min: 41, max: 52, step: 1, value: 44, unit: "mm", digits: 0 },
    { id: "shoulder", name: ["右轴承轴肩直径", "Bearing shoulder diameter"], min: 36, max: 56, step: 1, value: 38, unit: "mm", digits: 0 },
    { id: "r", name: ["轴承处圆角 r", "Fillet r at the bearing"], min: 0.4, max: 2.0, step: 0.1, value: 1.6, unit: "mm", digits: 1 },
    { id: "seat", name: ["齿轮位长度", "Gear seat length"], min: 45, max: 58, step: 1, value: 55, unit: "mm", digits: 0 },
    { id: "key", name: ["联轴器键长", "Coupling key length"], min: 36, max: 70, step: 1, value: 36, unit: "mm", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["核对", "Check"], primary: true }, { id: "reset", name: ["清除结果", "Clear"] }],
  legend: [{ color: "var(--green)", name: ["通过", "pass"] }, { color: "var(--red)", name: ["不通过", "fail"] }],
  tasks: [
    { id: "all", robot: true, text: ["把 WQR-105 输出轴调到七条规则全部通过，按“核对”。", "Make all seven rules pass for the WQR-105 shaft and press Check."],
      demo: { scene: "robot", set: { collar: 48, shoulder: 42, r: 1.0, seat: 53, key: 63 }, press: ["start"], wait: 1 } },
    { id: "fillet", robot: true, text: ["其他规则都通过，只把圆角改成 1.6 mm 再核对：哪一条不通过？为什么圆角大了轴承就装不到位？",
                                         "With everything else passing, set the fillet to 1.6 mm and check: which rule fails, and why can the bearing no longer seat?"],
      demo: { scene: "robot", set: { collar: 48, shoulder: 42, r: 1.6, seat: 53, key: 63 }, press: ["start"], wait: 1 } },
    { id: "life", text: ["小型减速电机输出轴：调到七条规则全部通过。", "Gearmotor shaft: make all seven rules pass."],
      demo: { scene: "life", set: { collar: 12, shoulder: 10, r: 0.2, seat: 28, key: 15 }, press: ["start"], wait: 1 } },
  ],
  think: ["“齿轮位比轮毂短 2–3 mm”这条规则如果不遵守，套筒会顶在哪里？齿轮还能被压紧吗？",
          "If the seat were not 2–3 mm shorter than the hub, what would the sleeve press against — would the gear still be clamped?"],

  reset(api, s) { s.res = null; },
  update(dt, api, s) {
    s.res = rules33_2(api);
    const bad = s.res.filter((x) => !x.ok);
    if (api.scene === "robot" && bad.length === 0) api.done("all");
    if (api.scene === "robot" && bad.length === 1 && bad[0].en.startsWith("fillet")) api.done("fillet");
    if (api.scene === "life" && bad.length === 0) api.done("life");
    api.stop();
  },
  readouts(api, s) {
    if (!s.res) return [[["结果", "Result"], api.T("按“核对”", "press Check")]];
    const n = s.res.filter((x) => x.ok).length;
    return [[["通过", "Passed"], n + " / " + s.res.length]].concat(s.res.filter((x) => !x.ok).map((x) => [["不通过", "Fails"], api.T(x.zh, x.en)]));
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    const life = api.scene === "life", D = DATA33_2[life ? "life" : "robot"], p = api.p;
    // 轴的轮廓：左轴承位、齿轮位、轴环、轴肩、右轴承位、密封段、外伸段（长度按比例，直径按比例放大）
    const segs = life ? [[D.d, 14], [D.dGear, p.seat], [p.collar, 4], [p.shoulder, 5], [D.d, D.B], [D.d, 8], [D.dExt, 22]]
                      : [[35, 37], [40, p.seat], [p.collar, 10], [p.shoulder, 15], [35, 17], [35, 40], [30, 72]];
    const L = segs.reduce((a, b) => a + b[1], 0), sx = (w * 0.56) / L, sy = Math.min(sx * 2.2, (h * 0.42) / Math.max(...segs.map((x) => x[0]), life ? 22 : 72));
    const x0 = w * 0.04, yc = h * 0.45;
    let z = 0;
    segs.forEach(([d, l]) => { api.rect(x0 + z * sx, yc - d / 2 * sy, l * sx, d * sy, css("--panel"), css("--ink")); z += l; });
    api.line(x0 - 8, yc, x0 + L * sx + 8, yc, css("--muted"), 1, [6, 3]);
    // 右轴承（与圆角的关系）与齿轮毂
    const zb = segs.slice(0, 4).reduce((a, b) => a + b[1], 0);
    const bw = D.B * sx, bh = (D.D - D.d) / 2 * sy;
    const gap = s.res && !s.res[3].ok ? Math.max(2, (p.r - D.rs) * sx * 2) : 0;          // 圆角太大：轴承贴不上轴肩
    [-1, 1].forEach((k) => api.rect(x0 + zb * sx + gap, yc + (k < 0 ? -D.d / 2 * sy - bh : D.d / 2 * sy), bw, bh, css("--accent"), css("--ink")));
    const zg = segs[0][1] - 2 + (life ? 0 : 0);
    const hubTop = (life ? 16 : 64) / 2 * sy;
    [-1, 1].forEach((k) => api.rect(x0 + zg * sx, k < 0 ? yc - hubTop : yc + (segs[1][0] / 2) * sy, D.hub * sx, hubTop - segs[1][0] / 2 * sy, css("--amber"), css("--ink")));
    api.label(api.T("齿轮毂", "gear hub"), x0 + (zg + D.hub / 2) * sx, yc - hubTop - 10, css("--muted"), 12, "center");
    api.label(api.T("右轴承", "bearing"), x0 + zb * sx + bw / 2, yc - D.d / 2 * sy - bh - 10, css("--muted"), 12, "center");
    // 右侧：规则清单
    const lx = w * 0.64, ly = h * 0.08, lh = Math.min(26, h * 0.11);
    const res = s.res || rules33_2(api);
    res.forEach((x, i) => {
      const col = s.res ? (x.ok ? css("--green") : css("--red")) : css("--muted");
      api.circle(lx, ly + i * lh, 6, col);
      api.label(api.T(x.zh, x.en), lx + 12, ly + i * lh, css("--ink"), 12);
      api.label(x.v, lx + 12, ly + i * lh + lh * 0.45, css("--muted"), 11);
    });
    if (!s.res) api.label(api.T("（按“核对”）", "(press Check)"), lx, ly + res.length * lh + 6, css("--muted"), 12);
  },
});
