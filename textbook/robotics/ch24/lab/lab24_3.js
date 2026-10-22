// 实验 24.3 质量矩阵：姿态、负载与转子（配 24.3 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex24_3.py 同一版本。
// 场景 1（机器人，静止）：书中的 UR5e 模型（外观为零件库 glTF），拖滑块摆姿态 θ = (θ₁, θ₂, θ₃, −90°, θ₅, 0)，法兰上可装负载
//   （算例 23.2.2 的夹爪 + 毛坯按质量等比缩放）。质量矩阵 M 由逆动力学按列求出：速度为零时，令加速度为第 j 个单位矢量，
//   mj_inverse 给出的力矩减去重力项，就是 M 的第 j 列（含转子等效惯量 armature = 0.1 kg·m²）。下方画出 |M_ij| 的色块（对数色标）。
//   特征值用雅可比旋转法求。显示不含转子惯量的 M₁₁、负载惯量比 (M₁₁ − armature)/armature、条件数（含与不含转子惯量）。
// 场景 2（机器人，动态）：关节 1 的执行器改为直接给力矩（gainprm = 1，biasprm = 0，ctrlrange ±100），其余关节由模型自带的位置伺服保持；
//   给关节 1 一个 20 N·m、0.1 s 的力矩脉冲，冲量按每一步实际施加的力矩累加；比较 Δθ̇₁ 与 冲量 / M₁₁（含转子）。
//   一次运行里推两下：0～0.1 s 在伸直的姿态 (0, 0, 0, −90°, 0, 0) 推，0.25 s 时换到收拢的姿态 (0, −90°, 150°, −90°, 0, 0)、静止，再推一下。
// 阈值由 ex24_3.py 与 Python 版 MuJoCo 核算：随机姿态下 M₁₁（不含转子）0.238～3.633 kg·m²；推一下的实测与预测相差 0.1% 以内（任务取 2%）。
WQ.lab({
  title: ["实验 24.3 质量矩阵：姿态、负载与转子", "Lab 24.3 The mass matrix: pose, payload and rotors"],
  goal: ["看 UR5e 的质量矩阵怎样随姿态和负载变化，验证它与关节 1 的转角无关，并用“推一下”实测关节 1 推动的惯量。",
         "See how the UR5e's mass matrix changes with pose and payload, check that it does not depend on joint 1's angle, and measure the inertia joint 1 drives with a push."],
  view: "physics",
  models: ["B-ARM-UR5E"],
  scenes: [
    { id: "mass", robot: true, name: ["质量矩阵", "Mass matrix"], hide: [],
      problem: { title: ["机器人问题：同一套伺服参数，为什么有时好用有时不好用", "Robot problem: why does one set of servo gains work in some poses and not in others"],
                 text: ["关节 1 的伺服参数在手臂收拢时整定得很好，手臂一伸直、再夹上工件，就变得又软又晃。电机推动的惯量到底变了多少？",
                        "Joint 1's servo was tuned with the arm folded; with the arm stretched out and holding a part it turns sluggish and wobbly. How much has the inertia the motor drives changed?"] } },
    { id: "push", robot: true, name: ["推一下关节 1", "A push on joint 1"], hide: ["q1", "q2", "q3", "q5", "load"],
      problem: { title: ["机器人问题：M₁₁ 能不能直接测出来", "Robot problem: can M₁₁ be measured directly"],
                 text: ["给关节 1 一个短促的力矩脉冲，其他关节保持不动，关节 1 获得的转速就由它推动的惯量决定。伸直和收拢，差多少？",
                        "Give joint 1 a short torque pulse while the other joints hold still: the speed it gains is set by the inertia it drives. How different is it stretched and folded?"] } },
  ],
  params: [
    { id: "q1", name: ["关节 1 角 θ₁", "Joint 1 angle θ₁"], min: -180, max: 180, step: 1, value: 0, unit: "°", digits: 0 },
    { id: "q2", name: ["关节 2 角 θ₂", "Joint 2 angle θ₂"], min: -180, max: 0, step: 1, value: -90, unit: "°", digits: 0 },
    { id: "q3", name: ["关节 3 角 θ₃", "Joint 3 angle θ₃"], min: -160, max: 160, step: 1, value: 90, unit: "°", digits: 0 },
    { id: "q5", name: ["关节 5 角 θ₅", "Joint 5 angle θ₅"], min: -180, max: 180, step: 1, value: -90, unit: "°", digits: 0 },
    { id: "load", name: ["法兰上的负载", "Payload on the flange"], min: 0, max: 5, step: 0.1, value: 0, unit: "kg", digits: 1 },
  ],
  legend: [{ color: "#1f77b4", name: ["|M_ij|（深 = 大）", "|M_ij| (dark = large)"] }],
  physics: {
    camera: [30, 18, 0.75],
    payload(load) {
      const k = load / 3.8, I = [0.0260338 * k, 0.0017083 * k, 0.0262671 * k];
      return `<body name="payload" pos="0 0.1 0"><inertial pos="0 0.16114 0" mass="${Math.max(load, 1e-6)}" diaginertia="${Math.max(I[0], 1e-9)} ${Math.max(I[1], 1e-9)} ${Math.max(I[2], 1e-9)}"/>
<geom type="box" pos="0 0.05 0" size="0.04 0.05 0.03" rgba="0.36 0.42 0.45 1" mass="0" contype="0" conaffinity="0"/>
<geom type="cylinder" pos="0 0.2008 0" quat="0.7071068 0.7071068 0 0" size="0.025 0.0908" rgba="0.62 0.55 0.35 1" mass="0" contype="0" conaffinity="0"/></body>`;
    },
    xml(api) {
      let t = api.mjcf("ur5e", { option: `<option timestep="0.001"><flag contact="disable"/></option>`,
                                 tool: api.scene === "mass" && api.p.load > 0 ? this.payload(api.p.load) : "" });
      if (api.scene === "push") {
        t = t.replace(`<general class="size3" name="shoulder_pan" joint="shoulder_pan_joint" />`,
                      `<general class="size3" name="shoulder_pan" joint="shoulder_pan_joint" gainprm="1" biasprm="0 0 0" ctrlrange="-100 100" />`);
      }
      return t;
    },
  },
  POSES: [[0, 0, 0, -Math.PI / 2, 0, 0], [0, -Math.PI / 2, 150 * Math.PI / 180, -Math.PI / 2, 0, 0]],   // 推一下：先伸直，再收拢
  pose(api) {
    const r = Math.PI / 180;
    if (api.scene === "push") return this.POSES[0];
    return [api.p.q1 * r, api.p.q2 * r, api.p.q3 * r, -90 * r, api.p.q5 * r, 0];
  },
  massMatrix(api, q) {                            // 逆动力学按列求 M（含转子惯量）
    const { mj, m, d } = api.sim, n = 6, M = [];
    const set = (j) => { for (let i = 0; i < n; i++) { d.qpos[i] = q[i]; d.qvel[i] = 0; d.qacc[i] = i === j ? 1 : 0; } mj.mj_inverse(m, d); return Array.from(d.qfrc_inverse); };
    const g = set(-1);
    for (let j = 0; j < n; j++) { const c = set(j); M.push(c.map((v, i) => v - g[i])); }
    return M.map((_, i) => M.map((col) => col[i]));   // M[i][j]
  },
  eig(A) {                                        // 对称矩阵的特征值（雅可比旋转法）
    const n = A.length, a = A.map((r) => r.slice());
    for (let sweep = 0; sweep < 60; sweep++) {
      let off = 0;
      for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) off += a[p][q] * a[p][q];
      if (off < 1e-30) break;
      for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
        if (Math.abs(a[p][q]) < 1e-300) continue;
        const th = (a[q][q] - a[p][p]) / (2 * a[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1));
        const c = 1 / Math.sqrt(t * t + 1), s = t * c;
        for (let k = 0; k < n; k++) { const akp = a[k][p], akq = a[k][q]; a[k][p] = c * akp - s * akq; a[k][q] = s * akp + c * akq; }
        for (let k = 0; k < n; k++) { const apk = a[p][k], aqk = a[q][k]; a[p][k] = c * apk - s * aqk; a[q][k] = s * apk + c * aqk; }
      }
    }
    return a.map((r, i) => r[i]).sort((x, y) => x - y);
  },
  reset(api, s) {
    const { mj, m, d } = api.sim, q = this.pose(api);
    const arm = Array.from(m.dof_armature);
    s.M = this.massMatrix(api, q);
    const Mx = s.M.map((r, i) => r.map((v, j) => (i === j ? v - arm[i] : v)));
    s.arm = arm; s.Mx = Mx;
    s.ev = this.eig(Mx); s.evA = this.eig(s.M);
    for (let i = 0; i < 6; i++) { d.qpos[i] = q[i]; d.qvel[i] = 0; d.ctrl[i] = q[i]; }
    d.ctrl[0] = api.scene === "push" ? 0 : q[0];
    mj.mj_forward(m, d);
    s.imp = 0; s.tPrev = 0; s.u = 0; s.fin = false;
    if (api.scene === "mass") {
      if (Mx[0][0] < 0.5) api.done("small");
      if (Math.abs(api.p.q1) >= 30) {                 // 与 θ₁ = 0 时比较
        const M0 = this.massMatrix(api, [0, ...q.slice(1)]);
        let dif = 0;
        for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) dif = Math.max(dif, Math.abs(M0[i][j] - s.M[i][j]));
        s.dif = dif;
        if (dif < 1e-9) api.done("theta1");
        this.pose(api).forEach((v, i) => { d.qpos[i] = v; });
        mj.mj_forward(m, d);
      }
      if (api.p.load >= 4.9 && api.p.q2 === 0 && api.p.q3 === 0) api.done("ratio");
    }
  },
  update(dt, api, s) {
    const { mj, m, d } = api.sim;
    if (api.scene !== "push") { api.stop(); return; }
    s.imp += s.u * (d.time - s.tPrev);            // 上一帧给的力矩在这一段时间里一直作用
    s.tPrev = d.time;
    s.phase = s.phase || 0;
    const t0 = 0.25 * s.phase;                    // 第 1 次推：0～0.1 s，伸直；第 2 次推：0.25～0.35 s，收拢
    s.u = d.time - t0 < 0.1 ? 20 : 0;
    d.ctrl[0] = s.u;
    if (d.time >= t0 + 0.25 && !s.fin) {
      s.res = s.res || [];
      s.res.push({ dv: d.qvel[0], imp: s.imp, M11: s.M[0][0] });
      if (s.phase === 0) {                        // 换到收拢的姿态，静止，再推一次
        const q = this.POSES[1];
        s.M = this.massMatrix(api, q);
        for (let i = 0; i < 6; i++) { d.qpos[i] = q[i]; d.qvel[i] = 0; d.ctrl[i] = q[i]; }
        d.ctrl[0] = 0; s.u = 0; s.imp = 0;
        mj.mj_forward(m, d);
        s.phase = 1;
        return;
      }
      s.fin = true;
      const a = s.res[0], b = s.res[1];
      const meas = (b.dv / b.imp) / (a.dv / a.imp), pred = a.M11 / b.M11;
      s.cmp = [meas, pred];
      if (Math.abs(meas / pred - 1) < 0.02) api.done("push");
      api.stop();
    }
  },
  chart(api, s, ctx, w, h) {
    if (!s.M) return;
    const n = 6, size = Math.min((h - 24) / n, (w * 0.45) / n), x0 = 40, y0 = 8;
    ctx.font = "11px sans-serif";
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const v = Math.abs(s.Mx[i][j]), L = Math.log10(Math.max(v, 1e-6));
      const u = Math.min(1, Math.max(0, (L + 6) / 6.5));
      const c = Math.round(245 - 200 * u);
      ctx.fillStyle = `rgb(${c},${Math.round(c * 0.9 + 20)},${Math.round(255 - 60 * u)})`;
      ctx.fillRect(x0 + j * size, y0 + i * size, size - 1, size - 1);
      ctx.fillStyle = u > 0.6 ? "#fff" : "#1d2327";
      const txt = v < 5e-7 ? "0" : v >= 0.01 ? s.Mx[i][j].toFixed(2) : s.Mx[i][j].toExponential(0);
      ctx.fillText(txt, x0 + j * size + 3, y0 + i * size + size / 2 + 4);
    }
    ctx.fillStyle = "#1d2327";
    for (let k = 0; k < n; k++) { ctx.fillText(String(k + 1), x0 + k * size + size / 2 - 3, y0 + n * size + 13); ctx.fillText(String(k + 1), x0 - 14, y0 + k * size + size / 2 + 4); }
    const bx = x0 + n * size + 30, bw = w - bx - 20;
    s.ev.forEach((e, k) => {                       // 特征值（对数刻度，10⁻⁴～10）
      const u = (Math.log10(Math.max(e, 1e-6)) + 4) / 5, yy = y0 + k * (h - 30) / 6;
      ctx.fillStyle = "#1f77b4"; ctx.fillRect(bx + 60, yy, Math.max(2, bw * 0.6 * Math.min(1, Math.max(0, u))), (h - 30) / 6 - 4);
      ctx.fillStyle = "#1d2327"; ctx.fillText(`λ${k + 1} = ${e.toExponential(2)}`, bx - 10, yy + 12);
    });
  },
  readouts(api, s) {
    if (!s.M) return [];
    const f = (v, k = 4) => api.fmt(v, k);
    const rows = [
      [["M₁₁（不含转子惯量）", "M₁₁ (without rotor inertia)"], f(s.Mx[0][0]) + " kg·m²"],
      [["M₂₂、M₆₆（不含转子惯量）", "M₂₂, M₆₆ (without rotor inertia)"], `${f(s.Mx[1][1])}, ${s.Mx[5][5].toExponential(3)} kg·m²`],
      [["关节 1 的负载惯量比 (M₁₁ − 转子)/转子", "Joint 1 load-to-rotor inertia ratio"], f(s.Mx[0][0] / s.arm[0], 2)],
      [["条件数：不含 / 含转子惯量", "Condition number: without / with rotors"], `${api.fmt(s.ev[5] / s.ev[0], 0)} / ${api.fmt(s.evA[5] / s.evA[0], 1)}`],
    ];
    if (api.scene === "mass" && s.dif !== undefined) rows.push([["与 θ₁ = 0 时 M 的最大差别", "Largest difference from M at θ₁ = 0"], s.dif.toExponential(1) + " kg·m²"]);
    if (api.scene === "push") {
      rows.push([["冲量 ∫τ₁dt", "Impulse ∫τ₁dt"], f(s.imp, 4) + " N·m·s"]);
      rows.push([["关节 1 的转速 θ̇₁", "Joint 1 speed θ̇₁"], f(api.sim.d.qvel[0], 4) + " rad/s"]);
      rows.push([["预测 冲量 / M₁₁（含转子）", "Predicted impulse / M₁₁ (with rotor)"], f(s.imp / s.M[0][0], 4) + " rad/s"]);
      if (s.cmp) rows.push([["两种姿态：转速之比 / M₁₁ 之比", "Two poses: speed ratio / M₁₁ ratio"], `${f(s.cmp[0], 3)} / ${f(s.cmp[1], 3)}`]);
    }
    return rows;
  },
  tasks: [
    { id: "small", robot: true, text: ["找一个姿态，使关节 1 推动的连杆惯量（不含转子）小于 0.5 kg·m²。", "Find a pose in which the link inertia joint 1 drives (without the rotor) is below 0.5 kg·m²."],
      demo: { scene: "mass", set: { q1: 0, q2: -90, q3: 150, q5: -90, load: 0 }, press: [], wait: 2 } },
    { id: "theta1", robot: true, text: ["把关节 1 转过 30° 以上：质量矩阵与 θ₁ = 0 时完全相同（定理 24.3.2 (2)）。", "Turn joint 1 by 30° or more: the mass matrix is the same as at θ₁ = 0 (Theorem 24.3.2 (2))."],
      demo: { scene: "mass", set: { q1: 75, q2: -60, q3: 60, q5: -90, load: 0 }, press: [], wait: 2 } },
    { id: "ratio", robot: true, text: ["装 5 kg 负载、大臂小臂伸直（θ₂ = θ₃ = 0），读出关节 1 的负载惯量比。", "With a 5 kg payload and the arm stretched (θ₂ = θ₃ = 0), read joint 1's load-to-rotor inertia ratio."],
      demo: { scene: "mass", set: { q1: 0, q2: 0, q3: 0, q5: -90, load: 5 }, press: [], wait: 2 } },
    { id: "push", robot: true, text: ["运行“推一下”：伸直、收拢两种姿态各推一次，转速之比与 M₁₁ 之比相差不到 2%。", "Run the push: once stretched and once folded; the ratio of the speeds agrees with the ratio of M₁₁ within 2 %."],
      demo: { scene: "push", wait: 4 } },
  ],
  think: ["推一下时其他关节由伺服“保持不动”，并不是真的焊死。为什么测得的仍然几乎就是 M₁₁？什么情况下误差会变大？",
          "During the push the other joints are only held by their servos, not welded. Why is the measured value still almost exactly M₁₁, and when would the error grow?"],
});
