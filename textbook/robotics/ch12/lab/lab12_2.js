// 实验 12.2 指数积的空间形式与物体形式（配 12.2 节）。平面 3R 臂，L = (0.425, 0.392, 0.1) m（取 UR5e 大臂、小臂长度）。
// 末端按指数积公式计算：空间形式 T = e^[S1]θ1 e^[S2]θ2 e^[S3]θ3 M，物体形式 T = M e^[B1]θ1 e^[B2]θ2 e^[B3]θ3。
// “逐步演示”：空间形式从关节 3 开始、各轴在零位处；物体形式从关节 1 开始、各轴跟着手臂走。
WQ.lab({
  title: ["实验 12.2 指数积的空间形式与物体形式", "Lab 12.2 Space form and body form of the PoE"],
  goal: ["用指数积公式的两种形式计算平面 3R 臂的末端，并逐步看清每个指数怎样作用。",
         "Compute the tip of a planar 3R arm with both forms of the PoE formula and watch each exponential act in turn."],
  scenes: [
    { id: "arm", robot: true, name: ["平面 3R 臂（UR5e 侧视）", "Planar 3R arm (UR5e side view)"],
      problem: { title: ["机器人问题：控制器怎样算出末端位置", "Robot problem: how the controller finds the tip"],
                 text: ["UR5e 的关节 2、3、4 互相平行，从侧面看就是一台平面 3R 臂。由三个关节角求末端的位置和朝向。",
                        "UR5e joints 2, 3, 4 are parallel: seen from the side it is a planar 3R arm. Find the tip from the three joint angles."] } },
    { id: "lamp", name: ["台灯", "Desk lamp"],
      problem: { title: ["生活中的例子：台灯的灯罩照向哪里", "Everyday example: where the desk lamp points"],
                 text: ["台灯有三个互相平行的铰链。知道三个铰链的角度，灯罩的位置和朝向就确定了。",
                        "A desk lamp has three parallel hinges; their angles fix where the shade is and where it points."] } },
  ],
  params: [
    { id: "t1", name: ["关节角 θ₁", "Joint θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "t2", name: ["关节角 θ₂", "Joint θ₂"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "t3", name: ["关节角 θ₃", "Joint θ₃"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "form", name: ["公式：0 空间形式 / 1 物体形式", "Formula: 0 space / 1 body"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["逐步演示", "Step through"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "ex", robot: true, text: ["复现算例 12.2.1：θ = (30°, 45°, −90°)，用空间形式读出末端位置。", "Example 12.2.1: θ = (30°, 45°, −90°), space form: read the tip."],
      demo: { scene: "arm", set: { t1: 30, t2: 45, t3: -90, form: 0 }, press: [] } },
    { id: "body", robot: true, text: ["同一组关节角换用物体形式，验证末端不变。", "Same angles, body form: the tip is unchanged."],
      demo: { scene: "arm", set: { t1: 30, t2: 45, t3: -90, form: 1 }, press: [] } },
    { id: "steps", text: ["用空间形式“逐步演示”到结束，对照算例 12.2.1 中每一步的末端位置。", "Step through the space form to the end and compare each step with Example 12.2.1."],
      demo: { scene: "lamp", set: { t1: 30, t2: 45, t3: -90, form: 0 }, press: ["start"], wait: 5 } },
  ],
  think: ["空间形式为什么要从最后一个关节开始？如果从关节 1 开始，第二步用的轴错在哪里？",
          "Why does the space form start from the last joint? Starting from joint 1, what is wrong with the axis used next?"],

  L: [0.425, 0.392, 0.1],
  // 4×4 齐次矩阵（平面问题用三维写，z 轴为转轴）
  mul(A, B) { return A.map((r) => [0, 1, 2, 3].map((j) => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j] + r[3] * B[3][j])); },
  // 绕过点 (qx, qy)、方向为 z 的轴转 t：式 (12.1.2)
  turn(qx, qy, t) { const c = Math.cos(t), s = Math.sin(t); return [[c, -s, 0, qx - c * qx + s * qy], [s, c, 0, qy - s * qx - c * qy], [0, 0, 1, 0], [0, 0, 0, 1]]; },
  M() { return [[1, 0, 0, this.L[0] + this.L[1] + this.L[2]], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]; },
  // 关节在零位时的中心（空间形式）和在 {b} 中的位置（物体形式）
  q0() { return [[0, 0], [this.L[0], 0], [this.L[0] + this.L[1], 0]]; },
  qb() { const s = this.L[0] + this.L[1] + this.L[2]; return [[-s, 0], [-(this.L[1] + this.L[2]), 0], [-this.L[2], 0]]; },
  th(api) { const d = Math.PI / 180; return [api.p.t1 * d, api.p.t2 * d, api.p.t3 * d]; },
  // 演示到第 k 步（0…3）时的末端；空间形式先用关节 3，物体形式先用关节 1
  tipAt(api, k) {
    const th = this.th(api), q = this.q0(), b = this.qb();
    if (api.p.form === 0) {
      let T = this.M();
      for (let i = 2; i >= 3 - k; i--) T = this.mul(this.turn(q[i][0], q[i][1], th[i]), T);
      return T;
    }
    let T = this.M();
    for (let i = 0; i < k; i++) T = this.mul(T, this.turn(b[i][0], b[i][1], th[i]));
    return T;
  },
  // 演示到第 k 步时手臂的形态（各段相对角）：空间形式是 [0,0,θ3]→[0,θ2,θ3]→…；物体形式是 [θ1,0,0]→[θ1,θ2,0]→…
  angsAt(api, k) {
    const th = this.th(api);
    return api.p.form === 0 ? th.map((t, i) => (i >= 3 - k ? t : 0)) : th.map((t, i) => (i < k ? t : 0));
  },
  pts(ang) {
    const p = [[0, 0]]; let a = 0;
    ang.forEach((t, i) => { a += t; const l = p[p.length - 1]; p.push([l[0] + this.L[i] * Math.cos(a), l[1] + this.L[i] * Math.sin(a)]); });
    return p;
  },

  reset(api, s) { s.k = 3; s.clock = 0; },
  start(api, s) { s.k = 0; s.clock = 0; s.log = []; },
  update(dt, api, s) {
    s.clock += dt;
    if (s.clock > 1.2) {
      s.clock = 0; s.k += 1;
      const T = this.tipAt(api, s.k); s.log.push([T[0][3], T[1][3]]);
      if (s.k >= 3) {
        api.stop();
        const ex = api.p.t1 === 30 && api.p.t2 === 45 && api.p.t3 === -90;
        if (ex && api.p.form === 0) api.done("steps");
      }
    }
  },
  readouts(api, s) {
    const T = this.tipAt(api, 3), th = this.th(api);
    const ex = api.p.t1 === 30 && api.p.t2 === 45 && api.p.t3 === -90;
    if (ex && api.p.form === 0) api.done("ex");
    if (ex && api.p.form === 1) api.done("body");
    const geo = this.pts(th)[3];
    const rows = [[["公式", "formula"], api.p.form === 0 ? "e^[S₁]θ₁ e^[S₂]θ₂ e^[S₃]θ₃ M" : "M e^[B₁]θ₁ e^[B₂]θ₂ e^[B₃]θ₃"],
                  [["末端位置（指数积）", "tip (PoE)"], `(${api.fmt(T[0][3], 4)}, ${api.fmt(T[1][3], 4)}) m`],
                  [["末端朝向", "tip direction"], api.fmt(Math.atan2(T[1][0], T[0][0]) * 180 / Math.PI, 1) + "°"],
                  [["与几何解法之差", "vs. geometry"], api.fmt(Math.hypot(T[0][3] - geo[0], T[1][3] - geo[1]), 3) + " m"]];
    (s.log || []).forEach((p, i) => rows.push([[`第 ${i + 1} 步后的末端`, `tip after step ${i + 1}`], `(${api.fmt(p[0], 4)}, ${api.fmt(p[1], 4)})`]));
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, k = Math.min(w / 1.5, h / 1.2) * 0.62, cx = w * 0.3, cy = h * 0.62;
    const X = ([x, y]) => [cx + k * x, cy - k * y];
    // 零位（虚线）
    const z = this.pts([0, 0, 0]).map(X);
    for (let i = 0; i < 3; i++) api.line(...z[i], ...z[i + 1], api.css("--muted"), 2, [6, 5]);
    // 当前演示到的形态
    const step = api.running ? s.k : 3;
    const ang = this.angsAt(api, step);
    const p = this.pts(ang).map(X);
    const col = api.scene === "lamp" ? api.css("--amber") : api.css("--accent");
    for (let i = 0; i < 3; i++) api.line(...p[i], ...p[i + 1], col, 9 - 2 * i);
    p.slice(0, 3).forEach((q) => api.circle(q[0], q[1], 7, api.css("--panel"), col));
    if (api.scene === "lamp") {   // 灯罩
      const a = ang[0] + ang[1] + ang[2], e = p[3], c = api.ctx;
      c.beginPath(); c.moveTo(e[0], e[1]);
      c.lineTo(e[0] + 26 * Math.cos(-a + 0.6), e[1] + 26 * Math.sin(-a + 0.6)); c.lineTo(e[0] + 26 * Math.cos(-a - 0.6), e[1] + 26 * Math.sin(-a - 0.6));
      c.closePath(); c.fillStyle = api.css("--amber-soft"); c.fill(); c.strokeStyle = api.css("--amber"); c.stroke();
    }
    // 下一步要绕的点（空间形式：零位处；物体形式：手臂上当前位置）
    if (api.running && s.k < 3) {
      const i = api.p.form === 0 ? 2 - s.k : s.k;
      const c = api.p.form === 0 ? X(this.q0()[i]) : p[i];
      api.circle(c[0], c[1], 11, null, api.css("--red"));
      api.label((api.lang() === "en" ? "next: joint " : "下一步：关节 ") + (i + 1), c[0] + 14, c[1] - 16, api.css("--red"), 13);
    }
    // 指数积算出的末端（红点）
    const T = this.tipAt(api, step), e = X([T[0][3], T[1][3]]);
    api.circle(e[0], e[1], 5, api.css("--red"));
    api.frame(cx, cy, 0, k * 0.12, ["x", "y"], "{s}");
  },
});
