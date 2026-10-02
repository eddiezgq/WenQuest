// 实验 11.2 数自由度（配 11.2 节）。
// 三个平面机构。每一帧都按当前位置建立平面形式的约束方程：未知数为各运动构件的 (ω, vx, vy) 和各关节速度，
// 每个关节给出 3 个方程 V_b − V_a − s θ̇ = 0（转动关节过点 (x, y)：s = (1, y, −x)；移动关节沿 (dx, dy)：s = (0, dx, dy)），
// 用高斯消元求秩，瞬时自由度 = 未知数个数 − 秩（式 (11.2.6) 的一般形式）。格吕布勒公式取 m = 3。
WQ.lab({
  title: ["实验 11.2 数自由度", "Lab 11.2 Counting degrees of freedom"],
  goal: ["对几个平面机构，比较格吕布勒公式与按约束的秩算出的瞬时自由度，看清两者何时不同。",
         "For several planar mechanisms compare Grübler's count with the instantaneous mobility from the rank of the constraints, and see when they differ."],
  scenes: [
    { id: "five", robot: true, name: ["平面五杆机器人", "Planar five-bar robot"], hide: ["extra", "phi"],
      problem: { title: ["机器人问题：两台电机定位一个点", "Robot problem: two motors place a point"],
                 text: ["机架上的两根曲柄各由一台电机驱动，末端（红点）是两根连杆的铰点。M = 2，两个输入一起才能把末端送到指定位置。",
                        "Each grounded crank has a motor; the tip (red) is the joint of the two couplers. M = 2: both inputs are needed to place the tip."] } },
    { id: "para", name: ["平行四边形机构", "Parallelogram linkage"], hide: ["a2", "phi"], params: { a1: { value: 60 } },
      problem: { title: ["机构：平行四边形与第三根曲柄", "Mechanism: a parallelogram and an extra crank"],
                 text: ["机架 0.4 m，两根曲柄 0.2 m，连杆 0.4 m。可以再加一根等长、平行的曲柄（红）。",
                        "Ground 0.4 m, two cranks 0.2 m, coupler 0.4 m. An equal, parallel extra crank (red) can be added."] } },
    { id: "lift", name: ["剪叉式升降台", "Scissor lift"], hide: ["a1", "a2", "extra"],
      problem: { title: ["生活中的例子：两级剪叉升降台", "Everyday example: a two-stage scissor lift"],
                 text: ["杆长 1.2 m，两级。推动底部的滑块，剪叉的夹角 φ 改变，平台升降。",
                        "Bars 1.2 m long, two stages. Pushing the bottom slider changes the angle φ and the platform rises."] } },
  ],
  params: [
    { id: "a1", name: ["输入 1：曲柄 1 转角 θ₁", "Input 1: crank 1 angle θ₁"], min: -180, max: 180, step: 1, value: 110, unit: "°", digits: 0 },
    { id: "a2", name: ["输入 2：曲柄 2 转角 θ₂", "Input 2: crank 2 angle θ₂"], min: -180, max: 180, step: 1, value: 70, unit: "°", digits: 0 },
    { id: "extra", name: ["第三根曲柄：0 不加 / 1 加上", "Extra crank: 0 off / 1 on"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "phi", name: ["剪叉夹角 φ", "Scissor angle φ"], min: 8, max: 60, step: 1, value: 20, unit: "°", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "target", robot: true, text: ["五杆机器人：同时调两个输入，把末端送到绿色目标点（误差小于 5 mm）。", "Five-bar robot: set both inputs so that the tip reaches the green target (within 5 mm)."],
      demo: { scene: "five", set: { a1: 130, a2: 50 }, press: [] } },
    { id: "extra", text: ["平行四边形：加上第三根曲柄，读出公式的结果，再把曲柄从 60° 转动 30° 以上，验证它照样能动。", "Parallelogram: add the extra crank, read the formula, then turn the crank by more than 30°: it still moves."],
      demo: { scene: "para", set: { extra: 1, a1: 110 }, press: [] } },
    { id: "sing", text: ["不加第三根曲柄，把曲柄转到与机架共线（θ₁ = 0° 或 180°），读出此时的瞬时自由度。", "Without the extra crank, turn the crank in line with the ground (θ₁ = 0° or 180°) and read the instantaneous mobility."],
      demo: { scene: "para", set: { extra: 0, a1: 0 }, press: [] } },
    { id: "lift", text: ["生活场景：把平台升到 1.5 m 以上。", "Everyday scene: raise the platform above 1.5 m."],
      demo: { scene: "lift", set: { phi: 45 }, press: [] } },
  ],
  think: ["平行四边形加第三根曲柄时，如果第三根曲柄比另外两根长 1 cm，机构还能转动吗？用“重复的约束”解释。",
          "With the extra crank, if it were 1 cm longer than the other two, could the mechanism still turn? Explain with repeated constraints."],

  // ---------- 几何
  cint(c0, r0, c1, r1, up) {           // 两圆交点，取 y 较大（up = true）或较小的一个
    const dx = c1[0] - c0[0], dy = c1[1] - c0[1], d = Math.hypot(dx, dy);
    if (d > r0 + r1 || d < Math.abs(r0 - r1) || d === 0) return null;
    const a = (r0 * r0 - r1 * r1 + d * d) / (2 * d), h = Math.sqrt(Math.max(r0 * r0 - a * a, 0));
    const mx = c0[0] + a * dx / d, my = c0[1] + a * dy / d;
    const p = [mx - h * dy / d, my + h * dx / d], q = [mx + h * dy / d, my - h * dx / d];
    return (p[1] >= q[1]) === up ? p : q;
  },
  u(deg) { const t = deg * Math.PI / 180; return [Math.cos(t), Math.sin(t)]; },
  // 机构：点、杆（画图用）和关节表 [构件 a, 构件 b, "R" 或 "P", 点或方向]；构件 0 为机架
  mech(api) {
    if (api.scene === "five") {
      const A = [0, 0], E = [0.3, 0], ua = this.u(api.p.a1), ub = this.u(api.p.a2);
      const B = [0.2 * ua[0], 0.2 * ua[1]], D = [E[0] + 0.2 * ub[0], E[1] + 0.2 * ub[1]];
      const C = this.cint(B, 0.3, D, 0.3, true);
      if (!C) return { ok: false, n: 4, joints: [], bars: [[A, B, "blue"], [E, D, "blue"]], grounds: [A, E] };
      return { ok: true, n: 4, tip: C, grounds: [A, E], bars: [[A, B, "blue"], [B, C, "accent"], [C, D, "accent"], [D, E, "blue"]],
        joints: [[0, 1, "R", A], [1, 2, "R", B], [2, 3, "R", C], [3, 4, "R", D], [4, 0, "R", E]] };
    }
    if (api.scene === "para") {
      const e = this.u(api.p.a1).map((x) => 0.2 * x), G = [[0, 0], [0.4, 0], [0.2, 0]];
      const T = G.map((g) => [g[0] + e[0], g[1] + e[1]]);
      const bars = [[G[0], T[0], "blue"], [G[1], T[1], "blue"], [T[0], T[1], "accent"]];
      const joints = [[0, 1, "R", G[0]], [1, 3, "R", T[0]], [3, 2, "R", T[1]], [2, 0, "R", G[1]]];
      const grounds = [G[0], G[1]];
      let n = 3;
      if (api.p.extra === 1) { bars.push([G[2], T[2], "red"]); joints.push([0, 4, "R", G[2]], [4, 3, "R", T[2]]); grounds.push(G[2]); n = 4; }
      return { ok: true, n, bars, joints, grounds };
    }
    // 两级剪叉升降台：杆长 1.2 m（半长 a = 0.6）
    const a = 0.6, f = api.p.phi * Math.PI / 180, W = 2 * a * Math.cos(f), H = 2 * a * Math.sin(f);
    const P = (x, y) => [x, y];
    // 构件：1 A1，2 B1，3 A2，4 B2，5 平台，6 下滑块，7 上滑块
    const joints = [[0, 1, "R", P(0, 0)], [0, 6, "P", [1, 0]], [6, 2, "R", P(W, 0)], [1, 2, "R", P(W / 2, H / 2)],
      [1, 4, "R", P(W, H)], [2, 3, "R", P(0, H)], [3, 4, "R", P(W / 2, 1.5 * H)], [4, 5, "R", P(0, 2 * H)], [3, 7, "R", P(W, 2 * H)], [7, 5, "P", [1, 0]]];
    const bars = [[P(0, 0), P(W, H), "blue"], [P(W, 0), P(0, H), "accent"], [P(0, H), P(W, 2 * H), "blue"], [P(W, H), P(0, 2 * H), "accent"]];
    return { ok: true, n: 7, bars, joints, grounds: [P(0, 0)], W, H: 2 * H, sliders: [P(W, 0), P(W, 2 * H)] };
  },
  rank(M) {                              // 高斯消元求秩
    const A = M.map((r) => r.slice()), m = A.length, n = m ? A[0].length : 0;
    let r = 0;
    for (let c = 0; c < n && r < m; c++) {
      let piv = r;
      for (let i = r + 1; i < m; i++) if (Math.abs(A[i][c]) > Math.abs(A[piv][c])) piv = i;
      if (Math.abs(A[piv][c]) < 1e-9) continue;
      [A[r], A[piv]] = [A[piv], A[r]];
      for (let i = 0; i < m; i++) if (i !== r) { const k = A[i][c] / A[r][c]; for (let j = c; j < n; j++) A[i][j] -= k * A[r][j]; }
      r++;
    }
    return r;
  },
  count(mc) {
    const n = mc.n, J = mc.joints.length, nu = 3 * n + J, rows = [];
    mc.joints.forEach((jt, k) => {
      const [a, b, type, v] = jt, s = type === "R" ? [1, v[1], -v[0]] : [0, v[0], v[1]];
      for (let i = 0; i < 3; i++) {
        const row = new Array(nu).fill(0);
        if (b > 0) row[3 * (b - 1) + i] += 1;
        if (a > 0) row[3 * (a - 1) + i] -= 1;
        row[3 * n + k] = -s[i];
        rows.push(row);
      }
    });
    const rk = this.rank(rows);
    return { N: n + 1, J, sf: J, grubler: 3 * (n + 1 - 1 - J) + J, inst: nu - rk };
  },
  tgt() {                                // 目标点：θ₁ = 130°、θ₂ = 50° 时的末端
    const B = [0.2 * Math.cos(130 * Math.PI / 180), 0.2 * Math.sin(130 * Math.PI / 180)];
    const D = [0.3 + 0.2 * Math.cos(50 * Math.PI / 180), 0.2 * Math.sin(50 * Math.PI / 180)];
    return this.cint(B, 0.3, D, 0.3, true);
  },
  readouts(api, s) {
    const mc = this.mech(api);
    if (!mc.ok) return [[["状态", "status"], api.lang() === "en" ? "cannot be assembled at these inputs" : "这组输入下无法装配"]];
    const c = this.count(mc);
    const rows = [[["构件数 N（含机架）", "links N (with ground)"], String(c.N)], [["关节数 J", "joints J"], String(c.J)],
      [["格吕布勒公式 M", "Grübler M"], String(c.grubler).replace("-", "−")], [["按秩算出的瞬时自由度", "instantaneous mobility (rank)"], String(c.inst)]];
    if (api.scene === "five") {
      const t = this.tgt(), d = Math.hypot(mc.tip[0] - t[0], mc.tip[1] - t[1]);
      rows.push([["末端 (x, y)", "tip (x, y)"], `(${api.fmt(mc.tip[0], 3)}, ${api.fmt(mc.tip[1], 3)}) m`], [["离目标", "to target"], api.fmt(d * 1000, 1) + " mm"]);
      if (d < 0.005) api.done("target");
    }
    if (api.scene === "para") {
      if (api.p.extra === 1 && c.grubler === 0 && c.inst === 1 && Math.abs(api.p.a1 - 60) >= 30) api.done("extra");
      if (api.p.extra === 0 && c.inst === 2) api.done("sing");
    }
    if (api.scene === "lift") {
      rows.push([["平台高度", "platform height"], api.fmt(mc.H, 3) + " m"]);
      if (mc.H > 1.5) api.done("lift");
    }
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, mc = this.mech(api);
    let k, ox, oy;
    if (api.scene === "lift") { k = Math.min(w / 2.2, h / 2.7); ox = w * 0.3; oy = h * 0.9; }
    else if (api.scene === "five") { k = Math.min(w / 1.2, h / 0.75); ox = w * 0.38; oy = h * 0.82; }
    else { k = Math.min(w / 1.1, h / 0.7); ox = w * 0.3; oy = h * 0.62; }
    const X = (p) => [ox + k * p[0], oy - k * p[1]];
    const col = { blue: api.css("--blue"), accent: api.css("--accent"), red: api.css("--red") };
    if (api.scene === "lift") {
      api.ground(oy + 4, w);
      const top = X([0, mc.H]);
      api.rect(top[0] - 10, top[1] - 14, k * mc.W + 30, 12, api.css("--muted"), api.css("--ink"), 3);
      mc.sliders.forEach((p) => { const q = X(p); api.rect(q[0] - 12, q[1] - 8, 24, 16, api.css("--panel"), api.css("--ink"), 3); });
    } else {
      mc.grounds.forEach((g) => { const q = X(g); api.line(q[0] - 14, q[1] + 14, q[0] + 14, q[1] + 14, api.css("--muted"), 2); api.line(q[0], q[1], q[0] - 10, q[1] + 14, api.css("--muted"), 2); api.line(q[0], q[1], q[0] + 10, q[1] + 14, api.css("--muted"), 2); });
    }
    if (api.scene === "five") {
      const t = X(this.tgt());
      api.circle(t[0], t[1], 9, null, api.css("--green"));
      api.circle(t[0], t[1], 3, api.css("--green"));
    }
    mc.bars.forEach(([p, q, c]) => { const a = X(p), b = X(q); api.line(a[0], a[1], b[0], b[1], col[c], 8); });
    mc.joints.forEach((j) => { if (j[2] === "R") { const q = X(j[3]); api.circle(q[0], q[1], 5, api.css("--panel"), api.css("--ink")); } });
    if (api.scene === "five" && mc.ok) { const q = X(mc.tip); api.circle(q[0], q[1], 7, api.css("--red")); }
    if (mc.ok) {
      const c = this.count(mc);
      api.label(`M = 3(${c.N} − 1 − ${c.J}) + ${c.sf} = ${String(c.grubler).replace("-", "−")}`, 16, 22, api.css("--ink"), 15);
      api.label((api.lang() === "en" ? "instantaneous mobility (rank): " : "按秩算出的瞬时自由度：") + c.inst, 16, 44, c.inst !== c.grubler ? api.css("--red") : api.css("--ink"), 15);
    }
  },
});
