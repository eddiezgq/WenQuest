// 实验 13.1 标准 DH 与改进 DH（配 13.1 节）。平面 3R 臂，L = (0.425, 0.392, 0.1) m（与第 12 章相同）。
// 标准 DH 表（a_i, α_i, d_i, θ_i）：(L1,0,0,θ1) (L2,0,0,θ2) (L3,0,0,θ3)，{3} 在末端。
// 改进 DH 表（a_{i-1}, α_{i-1}, d_i, θ_i）：(0,0,0,θ1) (L1,0,0,θ2) (L2,0,0,θ3)，{3} 在关节 3 上，末端再乘 X_3 = Trans(x, L3)。
// “用错约定”：把另一种约定的表代进本约定的公式（算例 13.1.3）。
WQ.lab({
  title: ["实验 13.1 标准 DH 与改进 DH", "Lab 13.1 Standard and modified DH"],
  goal: ["在平面 3R 臂上比较两种 DH 约定的连杆坐标系，验证它们算出同一个末端，并看看把表套错公式会怎样。",
         "Compare the link frames of the two DH conventions on a planar 3R arm, check that they give the same tip, and see what happens when a table is put into the wrong formula."],
  scenes: [
    { id: "sdh", robot: true, name: ["平面 3R 臂：标准 DH", "Planar 3R arm: standard DH"],
      problem: { title: ["机器人问题：手册上的 DH 表按哪种约定", "Robot problem: which convention is the manual's DH table in?"],
                 text: ["UR 按标准 DH 公布参数，Franka 按 Craig 的改进 DH 公布。先在一台简单的平面臂上看清两种坐标系各放在哪里。",
                        "UR publishes standard DH, Franka publishes Craig's modified DH. First see on a simple planar arm where each puts its frames."] } },
    { id: "mdh", robot: true, name: ["平面 3R 臂：改进 DH", "Planar 3R arm: modified DH"],
      problem: { title: ["机器人问题：坐标系放在连杆的哪一端", "Robot problem: which end of the link carries the frame"],
                 text: ["改进 DH 把 {i} 放在关节 i 的轴上，标准 DH 放在关节 i+1 的轴上。参数的数值相同，所在的行错开一行。",
                        "Modified DH puts {i} on joint i's axis, standard DH on joint i+1's. The numbers are the same, shifted by one row."] } },
    { id: "lamp", name: ["台灯", "Desk lamp"],
      problem: { title: ["生活中的例子：用卷尺描述一盏台灯", "Everyday example: describing a desk lamp with a tape measure"],
                 text: ["台灯的三个铰链互相平行。量出铰链之间的距离、记下每个铰链的角度，就能算出灯罩在哪里、照向哪里。",
                        "A desk lamp has three parallel hinges. Measure the distances between hinges, note each hinge angle, and you can work out where the shade is and where it points."] } },
  ],
  params: [
    { id: "t1", name: ["关节角 θ₁", "Joint θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "t2", name: ["关节角 θ₂", "Joint θ₂"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "t3", name: ["关节角 θ₃", "Joint θ₃"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "wrong", name: ["表套错公式：0 否 / 1 是", "Table in the wrong formula: 0 no / 1 yes"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "ex", robot: true, text: ["场景“标准 DH”，设置 θ = (30°, 45°, −90°)，读出末端位置（算例 13.1.2）。", "Scene “standard DH”: set θ = (30°, 45°, −90°) and read the tip (Example 13.1.2)."],
      demo: { scene: "sdh", set: { t1: 30, t2: 45, t3: -90, wrong: 0 }, press: [] } },
    { id: "mdh", robot: true, text: ["换到场景“改进 DH”，同一组关节角，验证末端位置不变；对照两张 DH 表，说出数值怎样错开一行。", "Switch to “modified DH” with the same angles: the tip is unchanged. Compare the two DH tables: how are the numbers shifted by one row?"],
      demo: { scene: "mdh", set: { t1: 30, t2: 45, t3: -90, wrong: 0 }, press: [] } },
    { id: "wrong", robot: true, text: ["在场景“标准 DH”中把“表套错公式”设为 1：末端偏了多少？与算例 13.1.3 比较。", "In “standard DH” set “wrong formula” to 1: how far off is the tip? Compare with Example 13.1.3."],
      demo: { scene: "sdh", set: { t1: 30, t2: 45, t3: -90, wrong: 1 }, press: [] } },
    { id: "lamp", text: ["台灯：调出一个灯罩竖直朝下（θ₁ + θ₂ + θ₃ = −90°）、灯罩高度在 0.2～0.4 m 之间的姿势。", "Desk lamp: find a pose with the shade pointing straight down (θ₁ + θ₂ + θ₃ = −90°) at a height between 0.2 and 0.4 m."],
      demo: { scene: "lamp", set: { t1: 90, t2: -90, t3: -90, wrong: 0 }, press: [] } },
  ],
  think: ["两种约定的参数数值相同，只是错开一行。为什么把一张表代进另一种公式，结果不是“差一点”，而是完全不对？",
          "The two conventions hold the same numbers, shifted by one row. Why does putting one table into the other formula give a result that is not slightly off but plainly wrong?"],

  L: [0.425, 0.392, 0.1],
  mul(A, B) { return A.map((r) => [0, 1, 2, 3].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j] + r[3] * B[3][j])); },
  Rz(t) { const c = Math.cos(t), s = Math.sin(t); return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]; },
  Rx(t) { const c = Math.cos(t), s = Math.sin(t); return [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]; },
  Tr(x, y, z) { return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]; },
  // 标准 DH：Rot(z,θ) Trans(z,d) Trans(x,a) Rot(x,α)，式 (13.1.4)；改进 DH：Rot(x,α) Trans(x,a) Rot(z,θ) Trans(z,d)，式 (13.1.7)
  sdh(a, al, d, th) { return [this.Rz(th), this.Tr(0, 0, d), this.Tr(a, 0, 0), this.Rx(al)].reduce((A, B) => this.mul(A, B)); },
  mdh(a, al, d, th) { return [this.Rx(al), this.Tr(a, 0, 0), this.Rz(th), this.Tr(0, 0, d)].reduce((A, B) => this.mul(A, B)); },
  th(api) { const d = Math.PI / 180; return [api.p.t1 * d, api.p.t2 * d, api.p.t3 * d]; },
  tabS() { const [L1, L2, L3] = this.L; return [[L1, 0, 0], [L2, 0, 0], [L3, 0, 0]]; },
  tabM() { const [L1, L2] = this.L; return [[0, 0, 0], [L1, 0, 0], [L2, 0, 0]]; },
  // 坐标系 {0}…{3}；kind "S" 或 "M"，tab 为要代入的表
  frames(kind, tab, th) {
    let T = this.Tr(0, 0, 0); const F = [T];
    tab.forEach(([a, al, d], i) => { T = this.mul(T, kind === "S" ? this.sdh(a, al, d, th[i]) : this.mdh(a, al, d, th[i])); F.push(T); });
    return F;
  },
  tip(api) {   // 按当前场景的约定算末端；wrong = 1 时把另一种约定的表代进来
    const th = this.th(api), M = api.scene === "mdh", wrong = api.p.wrong === 1;
    const kind = M ? "M" : "S", tab = wrong ? (M ? this.tabS() : this.tabM()) : (M ? this.tabM() : this.tabS());
    const F = this.frames(kind, tab, th);
    let T = F[3];
    if (M) T = this.mul(T, this.Tr(this.L[2], 0, 0));      // 改进 DH：末端还差 X_3
    return { T, F };
  },
  geo(api) {   // 几何解法：三段连杆矢量之和
    const th = this.th(api); let a = 0, x = 0, y = 0;
    th.forEach((t, i) => { a += t; x += this.L[i] * Math.cos(a); y += this.L[i] * Math.sin(a); });
    return [x, y, a];
  },
  readouts(api, s) {
    const { T } = this.tip(api), g = this.geo(api), err = Math.hypot(T[0][3] - g[0], T[1][3] - g[1]);
    const ex = api.p.t1 === 30 && api.p.t2 === 45 && api.p.t3 === -90;
    if (ex && api.scene === "sdh" && api.p.wrong === 0 && err < 1e-9) api.done("ex");
    if (ex && api.scene === "mdh" && api.p.wrong === 0 && err < 1e-9) api.done("mdh");
    if (ex && api.scene === "sdh" && api.p.wrong === 1 && err > 0.1) api.done("wrong");
    const deg = (api.p.t1 + api.p.t2 + api.p.t3) % 360;
    if (api.scene === "lamp" && Math.abs(((deg + 540) % 360) - 180 - (-90)) < 0.5 && g[1] > 0.2 && g[1] < 0.4) api.done("lamp");
    const M = api.scene === "mdh", wrong = api.p.wrong === 1, tab = (M !== wrong) ? this.tabM() : this.tabS();
    const head = M ? ["表（a_{i−1}, α_{i−1}, d_i, θ_i）", "table (a_{i−1}, α_{i−1}, d_i, θ_i)"] : ["表（a_i, α_i, d_i, θ_i）", "table (a_i, α_i, d_i, θ_i)"];
    const rows = tab.map(([a], i) => `(${api.fmt(a, 3)}, 0, 0, θ${i + 1})`).join("  ");
    return [[head, rows],
            [["公式", "formula"], M ? "Rot(x,α) Trans(x,a) Rot(z,θ) Trans(z,d)" : "Rot(z,θ) Trans(z,d) Trans(x,a) Rot(x,α)"],
            [["末端位置（DH）", "tip (DH)"], `(${api.fmt(T[0][3], 4)}, ${api.fmt(T[1][3], 4)}) m`],
            [["末端位置（几何）", "tip (geometry)"], `(${api.fmt(g[0], 4)}, ${api.fmt(g[1], 4)}) m`],
            [["二者之差", "difference"], api.fmt(err, 4) + " m"]];
  },
  draw(api, s) {
    const { w, h } = api, k = Math.min(w / 1.6, h / 1.25) * 0.62, cx = w * 0.33, cy = h * 0.66;
    const X = (x, y) => [cx + k * x, cy - k * y];
    const th = this.th(api), lamp = api.scene === "lamp";
    let a = 0; const pts = [[0, 0]];
    th.forEach((t, i) => { a += t; const l = pts[pts.length - 1]; pts.push([l[0] + this.L[i] * Math.cos(a), l[1] + this.L[i] * Math.sin(a)]); });
    const P = pts.map(([x, y]) => X(x, y)), col = lamp ? api.css("--amber") : api.css("--muted");
    if (lamp) { api.rect(P[0][0] - 40, P[0][1], 80, 12, api.css("--muted"), null, 4); }
    for (let i = 0; i < 3; i++) api.line(...P[i], ...P[i + 1], col, 10 - 2 * i);
    P.slice(0, 3).forEach((q) => api.circle(q[0], q[1], 7, api.css("--panel"), api.css("--ink")));
    if (lamp) {
      const e = P[3], c = api.ctx;
      c.beginPath(); c.moveTo(e[0], e[1]);
      c.lineTo(e[0] + 30 * Math.cos(-a + 0.6), e[1] + 30 * Math.sin(-a + 0.6)); c.lineTo(e[0] + 30 * Math.cos(-a - 0.6), e[1] + 30 * Math.sin(-a - 0.6));
      c.closePath(); c.fillStyle = api.css("--amber-soft"); c.fill(); c.strokeStyle = api.css("--amber"); c.stroke();
      api.label(api.lang() === "en" ? `shade height ${api.fmt(pts[3][1], 3)} m` : `灯罩高度 ${api.fmt(pts[3][1], 3)} m`, e[0] + 16, e[1] - 22, api.css("--ink"), 13);
    }
    // 连杆坐标系
    const kind = api.scene === "mdh" ? "M" : "S", F = this.frames(kind, kind === "M" ? this.tabM() : this.tabS(), th);
    F.forEach((T, i) => {
      const o = X(T[0][3], T[1][3]), ang = Math.atan2(T[1][0], T[0][0]) * 180 / Math.PI;
      api.frame(o[0] + (i === 1 && kind === "M" ? 0 : 0), o[1], ang, k * 0.1, [`x${i}`, `y${i}`], `{${i}}`, api.css("--blue"));
    });
    // 末端：DH 算出的（红点）
    const { T } = this.tip(api), e = X(T[0][3], T[1][3]);
    api.circle(e[0], e[1], 6, api.css("--red"));
    if (api.p.wrong === 1) api.label(api.lang() === "en" ? "tip from the wrong formula" : "套错公式算出的“末端”", e[0] + 10, e[1] + 16, api.css("--red"), 13);
  },
});
