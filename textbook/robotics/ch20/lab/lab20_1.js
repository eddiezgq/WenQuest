// 实验 20.1 一条腿的逆运动学（配 20.1 节）。零件库 Go2 与 G1 三维模型。
// 场景“落脚点”：滑块给出左前脚足端中心在机身坐标系 {b} 中的位置（x 向前、y 向左、z 向上，单位 m），按定理 20.1.2 求逆解：
//   p_h = (a_x, a_y, 0)，r = p − p_h，ρ² = r_y² + r_z²，z′ = −√(ρ² − d²)，θ1 = atan2(r_z, r_y) − atan2(z′, d)，
//   cos θ3 = (D² − l1² − l2²)/(2 l1 l2)，θ3 < 0（膝向后），θ2 = atan2(−x′, −z′) − atan2(l2 sin θ3, l1 + l2 cos θ3)。
//   尺寸：a_x = 0.1934、a_y = 0.0465、d = 0.0955、l1 = l2 = 0.213 m；限位取模型的关节表。
//   站立力矩 τ = Jᵀ f，f = (0, 0, −m𝔤/4)，m = 15.21 kg（式 (20.1.12)）。
// 生活场景“上台阶”：G1 代表人的腿，脚底保持水平（髋俯仰 + 膝 + 踝俯仰 = 0），用牛顿迭代（差商雅可比）求髋俯仰与膝的转角，
//   使踝关节到达台阶上方：前移 sx、抬高 sh（相对站立时的位置）。
// 坐标：模型 Z 向上；三维引擎世界坐标 Y 向上，h.point(连杆, 点) 给出世界坐标。
WQ.lab({
  title: ["实验 20.1 一条腿的逆运动学", "Lab 20.1 Inverse kinematics of one leg"],
  goal: ["给出落脚点，用几何方法求 Go2 一条腿的三个关节角，看关节限位怎样挑出唯一的一组解，读出站立时各关节的力矩；再让仿人机器人把脚放上台阶。",
         "Give a foothold, solve the three joint angles of a Go2 leg geometrically, see how the joint limits pick out a single solution and read the standing joint torques; then put a humanoid's foot on a step."],
  view: "3d",
  models: ["B-LEG-GO2", "B-HUM-G1"],
  scenes: [
    { id: "foot", robot: true, name: ["Go2 落脚点", "Go2 foothold"], hide: ["sx", "sh"],
      problem: { title: ["机器人问题：左前脚踩到指定的石头上", "Robot problem: put the front-left foot on a chosen stone"],
                 text: ["视觉系统给出落脚点在机身坐标系中的位置。三个关节各转多少？有几组解？站上去以后各电机出多大力矩？",
                        "Vision gives the foothold in the body frame. How far does each joint turn? How many solutions? What torque does each motor give once the foot carries load?"] } },
    { id: "stair", name: ["生活：上台阶", "Everyday: stepping up a stair"], hide: ["px", "py", "pz"],
      problem: { title: ["生活中的例子：人把脚放上台阶", "Everyday example: putting a foot on a stair"],
                 text: ["G1 的左腿代表人的腿。脚底保持水平，屈髋、屈膝把脚提上台阶：同样是“先看准落脚点，再求关节角”。",
                        "G1's left leg stands for a human leg. Keeping the sole level, flex hip and knee to lift the foot onto the step: again, foothold first, joint angles next."] } },
  ],
  params: [
    { id: "px", name: ["落脚点 x（向前）", "foothold x (forward)"], min: 0.0, max: 0.55, step: 0.005, value: 0.195, unit: "m", digits: 3 },
    { id: "py", name: ["落脚点 y（向左）", "foothold y (left)"], min: 0.0, max: 0.40, step: 0.005, value: 0.14, unit: "m", digits: 3 },
    { id: "pz", name: ["落脚点 z（向上）", "foothold z (up)"], min: -0.45, max: 0.05, step: 0.005, value: -0.265, unit: "m", digits: 3 },
    { id: "sx", name: ["台阶：脚前移", "stair: foot forward"], min: 0.0, max: 0.40, step: 0.01, value: 0.0, unit: "m", digits: 2 },
    { id: "sh", name: ["台阶：脚抬高", "stair: foot raised"], min: 0.0, max: 0.30, step: 0.01, value: 0.0, unit: "m", digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "target", robot: true, text: ["把左前脚放到算例 20.1.2 的落脚点 (0.28, 0.17, −0.22) m，读出三个关节角。", "Put the front-left foot at the foothold of Example 20.1.2, (0.28, 0.17, −0.22) m, and read the three joint angles."],
      demo: { scene: "foot", set: { px: 0.28, py: 0.17, pz: -0.22 }, press: [], wait: 6 } },
    { id: "far", robot: true, text: ["给出一个够不着的落脚点（例如太远或太近），读出不可达的原因。", "Give a foothold out of reach (too far or too close) and read why it cannot be reached."],
      demo: { scene: "foot", set: { px: 0.50, py: 0.14, pz: -0.30 }, press: [], wait: 6 } },
    { id: "low", robot: true, text: ["把落脚点放在大腿关节正下方 0.15 m 处（相当于机身压低），比较小腿关节的力矩与站立时的大小。", "Put the foothold 0.15 m straight below the thigh joint (body crouched) and compare the calf torque with standing."],
      demo: { scene: "foot", set: { px: 0.195, py: 0.14, pz: -0.15 }, press: [], wait: 6 } },
    { id: "step", text: ["让 G1 把左脚放上 0.15 m 高、前方 0.25 m 处的台阶。", "Let G1 put its left foot on a 0.15 m step 0.25 m ahead."],
      demo: { scene: "stair", set: { sx: 0.25, sh: 0.15 }, press: [], wait: 6 } },
  ],
  think: ["落脚点越靠近机身（ρ 越小），为什么越容易出现两组都在限位内的解？这时机器人应当选哪一组？",
          "Why do two in-limit solutions appear when the foothold comes close to the body (small ρ)? Which one should the robot take then?"],

  AX: 0.1934, AY: 0.0465, DY: 0.0955, L1: 0.213, L2: 0.213, MASS: 15.206, G: 9.81,
  LIM: [[-1.0472, 1.0472], [-1.5708, 3.4907], [-2.7227, -0.83776]],
  REST: [0, 0.9, -1.8],

  // ---------------- Go2 一条腿：定理 20.1.2
  ik(p) {
    const r = [p[0] - this.AX, p[1] - this.AY, p[2]], rho2 = r[1] * r[1] + r[2] * r[2], d = this.DY, l1 = this.L1, l2 = this.L2;
    if (rho2 < d * d) return { ok: false, why: "rho" };
    const zp = -Math.sqrt(rho2 - d * d), xp = r[0], D = Math.hypot(xp, zp);
    const Dmax = 2 * l1 * Math.cos(Math.abs(this.LIM[2][1]) / 2), Dmin = 2 * l1 * Math.cos(Math.abs(this.LIM[2][0]) / 2);
    const t1 = Math.atan2(r[2], r[1]) - Math.atan2(zp, d);
    const out = { rho: Math.sqrt(rho2), D, Dmax, Dmin, zp, xp };
    if (D > l1 + l2) return Object.assign(out, { ok: false, why: "far" });
    if (D > Dmax + 1e-9) return Object.assign(out, { ok: false, why: "straight" });
    if (D < Dmin - 1e-9) return Object.assign(out, { ok: false, why: "near" });
    const c3 = Math.max(-1, Math.min(1, (D * D - l1 * l1 - l2 * l2) / (2 * l1 * l2))), t3 = -Math.acos(c3);
    let t2 = Math.atan2(-xp, -zp) - Math.atan2(l2 * Math.sin(t3), l1 + l2 * Math.cos(t3));
    if (t2 < this.LIM[1][0]) t2 += 2 * Math.PI;
    if (t2 > this.LIM[1][1]) t2 -= 2 * Math.PI;
    const th = [t1, t2, t3];
    const bad = th.findIndex((v, i) => v < this.LIM[i][0] - 1e-9 || v > this.LIM[i][1] + 1e-9);
    if (bad >= 0) return Object.assign(out, { ok: false, why: "limit", th, bad });
    return Object.assign(out, { ok: true, th });
  },
  jac(th) {   // 式 (20.1.12)
    const [t1, t2, t3] = th, l1 = this.L1, l2 = this.L2, d = this.DY;
    const xp = -l1 * Math.sin(t2) - l2 * Math.sin(t2 + t3), zp = -l1 * Math.cos(t2) - l2 * Math.cos(t2 + t3);
    const c = Math.cos(t1), s = Math.sin(t1), rot = (v) => [v[0], c * v[1] - s * v[2], s * v[1] + c * v[2]];
    const cols = [rot([0, -zp, d]), rot([zp, 0, -xp]), rot([-l2 * Math.cos(t2 + t3), 0, l2 * Math.sin(t2 + t3)])];
    return { cols, det: -l1 * l2 * zp * Math.sin(t3) };
  },

  // ---------------- G1 左腿上台阶
  G1L: ["left_hip_pitch_joint", "left_hip_roll_joint", "left_hip_yaw_joint", "left_knee_joint", "left_ankle_pitch_joint", "left_ankle_roll_joint"],
  g1set(g, a, k) { const o = {}; o[this.G1L[0]] = a; o[this.G1L[3]] = k; o[this.G1L[4]] = -(a + k); g.set(o); return g.local("left_ankle_roll_link", [0, 0, 0]); },
  g1ik(g, target, keep) {
    const r = this.g1newton(g, target, keep.ga, keep.gk);
    return r.ok ? r : this.g1newton(g, target, -0.6, 1.0);   // 从伸直的腿出发牛顿法会失败（奇异），换一个屈膝的初值再试
  },
  g1newton(g, target, a, k) {
    for (let it = 0; it < 40; it++) {
      const p = this.g1set(g, a, k), e = [target[0] - p[0], target[2] - p[2]];
      if (Math.hypot(e[0], e[1]) < 1e-7) break;
      const h = 1e-5, pa = this.g1set(g, a + h, k), pk = this.g1set(g, a, k + h);
      const J = [[(pa[0] - p[0]) / h, (pk[0] - p[0]) / h], [(pa[2] - p[2]) / h, (pk[2] - p[2]) / h]];
      const det = J[0][0] * J[1][1] - J[0][1] * J[1][0];
      if (Math.abs(det) < 1e-9) { k += 0.05; continue; }
      a += (J[1][1] * e[0] - J[0][1] * e[1]) / det;
      k += (-J[1][0] * e[0] + J[0][0] * e[1]) / det;
    }
    const p = this.g1set(g, a, k), err = Math.hypot(target[0] - p[0], target[2] - p[2]);
    const lim = (n, v) => { const j = g.joints[n]; return v >= j.lower - 1e-6 && v <= j.upper + 1e-6; };
    const ok = err < 1e-4 && lim(this.G1L[0], a) && lim(this.G1L[3], k) && lim(this.G1L[4], -(a + k));
    return { ok, a, k, err };
  },

  setup3d(api, keep) {
    const T = api.three, go = api.m["B-LEG-GO2"], g1 = api.m["B-HUM-G1"];
    go.place(0, 0);
    g1.place(0, 0);
    keep.mk = new T.Mesh(new T.SphereGeometry(0.016, 18, 12), new T.MeshStandardMaterial({ color: 0x2ca02c }));
    api.st.scene.add(keep.mk);
    keep.hipL = new T.Line(new T.BufferGeometry().setFromPoints([new T.Vector3(), new T.Vector3()]), new T.LineBasicMaterial({ color: 0x9aa6ad }));
    api.st.scene.add(keep.hipL);
    api.axes(go, "base", 0.12);
    // G1 站立时左踝的位置（骨盆坐标系），台阶的位置相对它给出
    g1.set({ left_knee_joint: 0.0 });
    keep.ank0 = g1.local("left_ankle_roll_link", [0, 0, 0]);
    keep.sole0 = g1.point("left_ankle_roll_link", [0.035, 0, -0.035]);
    keep.step = new T.Mesh(new T.BoxGeometry(0.40, 1, 0.5), new T.MeshStandardMaterial({ color: 0xc9b48a, transparent: true, opacity: 0.85 }));
    api.st.scene.add(keep.step);
    keep.ga = -0.3; keep.gk = 0.6;
    keep.shown = null;
  },
  reset(api, s) { },
  pose(api) {
    const go = api.m["B-LEG-GO2"], g1 = api.m["B-HUM-G1"], K = api.keep, p = api.p;
    if (!go || !K.mk) return null;
    if (api.scene === "foot") {
      const res = this.ik([p.px, p.py, p.pz]);
      const th = res.ok ? res.th : this.REST;
      const o = Object.assign({}, go.entry.rest);
      o.FL_hip_joint = th[0]; o.FL_thigh_joint = th[1]; o.FL_calf_joint = th[2];
      go.set(o);
      K.mk.position.copy(go.point("base", [p.px, p.py, p.pz]));
      K.mk.material.color.setHex(res.ok ? 0x2ca02c : 0xd62728);
      K.hipL.geometry.setFromPoints([go.point("base", [this.AX, this.AY + this.DY, 0]), go.point("base", [p.px, p.py, p.pz])]);
      return res;
    }
    const tgt = [K.ank0[0] + p.sx, K.ank0[1], K.ank0[2] + p.sh];
    const r = this.g1ik(g1, tgt, K);
    if (r.ok) { K.ga = r.a; K.gk = r.k; } else this.g1set(g1, K.ga, K.gk);
    const base = K.sole0;
    K.step.scale.set(1, Math.max(0.002, p.sh), 1);
    K.step.position.set(base.x + p.sx + 0.05, Math.max(0.001, p.sh) / 2, base.z);
    K.step.visible = p.sh > 0.005;
    return r;
  },

  readouts(api, s) {
    const go = api.m["B-LEG-GO2"];
    if (!go || !api.keep.mk) return [];
    const r = this.pose(api), f = (x, n) => api.fmt(x, n), deg = 180 / Math.PI, p = api.p;
    if (api.scene === "foot") {
      const rows = [[["落脚点 p（{b}）", "foothold p (in {b})"], `(${f(p.px, 3)}, ${f(p.py, 3)}, ${f(p.pz, 3)}) m`]];
      if (r.rho !== undefined) rows.push([["ρ（到髋外摆轴）与 2d", "ρ (to abduction axis) vs 2d"], `${f(r.rho, 4)} m / ${f(2 * this.DY, 3)} m`]);
      if (r.D !== undefined) rows.push([["D 与 [D_min, D_max]", "D vs [D_min, D_max]"], `${f(r.D, 4)} m / [${f(r.Dmin, 4)}, ${f(r.Dmax, 4)}] m`]);
      if (!r.ok) {
        const why = { rho: api.T("ρ < d：落脚点离髋外摆轴太近", "ρ < d: too close to the abduction axis"),
                      far: api.T("D > l₁ + l₂：腿伸直也够不着", "D > l₁ + l₂: out of reach even with a straight leg"),
                      straight: api.T("D > D_max：小腿关节要伸过 −48° 的限位", "D > D_max: the calf joint would pass its −48° limit"),
                      near: api.T("D < D_min：小腿关节要折过 −156° 的限位", "D < D_min: the calf joint would fold past −156°"),
                      limit: api.T("有解，但关节 " + ((r.bad || 0) + 1) + " 超出限位", "solvable, but joint " + ((r.bad || 0) + 1) + " is out of range") }[r.why];
        api.done("far");
        rows.push([["结果", "result"], api.T("不可达：", "unreachable: ") + why]);
        return rows;
      }
      const J = this.jac(r.th), F = this.MASS * this.G / 4, tau = J.cols.map((c) => -F * c[2]);
      rows.push([["θ₁, θ₂, θ₃", "θ₁, θ₂, θ₃"], `${f(r.th[0] * deg, 2)}°, ${f(r.th[1] * deg, 2)}°, ${f(r.th[2] * deg, 2)}°`]);
      rows.push([["det J（式 (20.1.13)）", "det J (Eq. (20.1.13))"], f(J.det * 1000, 3) + " ×10⁻³ m³"]);
      rows.push([["站立力矩 τ（每脚 m𝔤/4）", "standing torque τ (m𝔤/4 per foot)"], `${f(tau[0], 2)}, ${f(tau[1], 2)}, ${f(tau[2], 2)} N·m`]);
      rows.push([["解的个数（限位内）", "solutions within limits"], r.rho > 2 * this.DY ? api.T("1（ρ > 2d，定理 20.1.3）", "1 (ρ > 2d, Theorem 20.1.3)") : api.T("可能 2（ρ ≤ 2d）", "maybe 2 (ρ ≤ 2d)")]);
      if (Math.abs(p.px - 0.28) < 0.006 && Math.abs(p.py - 0.17) < 0.006 && Math.abs(p.pz + 0.22) < 0.006) api.done("target");
      if (Math.abs(p.px - this.AX) < 0.01 && Math.abs(p.py - this.AY - this.DY) < 0.01 && p.pz > -0.16 && p.pz < -0.14) api.done("low");
      return rows;
    }
    const rows = [[["脚前移、抬高", "foot forward, raised"], `${f(p.sx, 2)} m, ${f(p.sh, 2)} m`]];
    if (!r.ok) { rows.push([["结果", "result"], api.T("够不着或超出关节限位（保持上一个可行姿态）", "out of reach or past a joint limit (last feasible pose kept)")]); return rows; }
    rows.push([["髋俯仰、膝、踝俯仰", "hip pitch, knee, ankle pitch"], `${f(r.a * deg, 1)}°, ${f(r.k * deg, 1)}°, ${f(-(r.a + r.k) * deg, 1)}°`]);
    rows.push([["脚底", "sole"], api.T("保持水平（三个俯仰角之和为零）", "kept level (the three pitch angles sum to zero)")]);
    if (p.sh >= 0.149 && p.sx >= 0.2) api.done("step");
    return rows;
  },

  draw(api, s) {
    const m = api.m, sc = api.scene, K = api.keep;
    if (!K.mk) return;
    m["B-LEG-GO2"].holder.visible = sc === "foot";
    K.mk.visible = sc === "foot";
    K.hipL.visible = sc === "foot";
    m["B-HUM-G1"].holder.visible = sc === "stair";
    if (sc !== "stair") K.step.visible = false;
    if (K.shown !== sc) {
      K.shown = sc;
      api.view(sc === "foot" ? 60 : 75, 15, sc === "foot" ? 0.75 : 0.85, sc === "foot" ? m["B-LEG-GO2"] : m["B-HUM-G1"]);
    }
    this.pose(api);
  },
});
