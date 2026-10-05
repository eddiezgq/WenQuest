// 实验 18.4 Delta 分拣的工作空间与速度（配 18.4 节）。
// 零件库 B-PAR-DELTA：Rb 0.15、Rp 0.04、La 0.22、Lb 0.5 m，主动臂限位 −40°～90°，转速上限 10.47 rad/s。
// 逆解：式 (11.5.7)，肘部朝外；从动杆和动平台按闭环条件摆放，做法与实验 11.5、14.6 相同。
// 速度：A v = B θ̇（式 (18.4.3)），A 的行为杆的单位方向 u_kᵀ，B = diag(u_k·∂E_k/∂θ_k)，J = A⁻¹B。
//   沿方向 d 的最大速度 ω_max / ‖J⁻¹d‖∞（式 (18.4.4)），保证速度 v_g = ω_max / max_k ‖J⁻¹ 的第 k 行‖（式 (18.4.5)）。
// 工作空间截面：当前高度上 2 cm 网格的点，按 v_g 着色（0.6 m/s 浅黄 → 2.3 m/s 深蓝）。
// 拾放节拍：25/305/25 mm 循环，每段按最大匀速走（式 (18.4.6)，每段取 61 个点），放慢 20 倍播放。
// 生活场景：体育场的索拉摄像机，按 1:100 的比例画出：球场 100 m × 70 m，四座塔高 40 m 在四角，绞车收放速度上限设为 10 m/s。
//   绞车速度 = 摄像机速度在钢索方向上的分量（与式 (18.4.2) 同理）；飞行速度取不使任何绞车超速的最大匀速。
WQ.lab({
  title: ["实验 18.4 Delta 分拣的工作空间与速度", "Lab 18.4 Workspace and speed of a Delta picker"],
  goal: ["看 Delta 在工作空间各处、各方向上能动多快，并为 25/305/25 mm 拾放循环找一个节拍最短的位置。",
         "See how fast the Delta can move at each place and in each direction, and find where a 25/305/25 mm pick cycle runs fastest."],
  view: "3d",
  models: ["B-PAR-DELTA"],
  scenes: [
    { id: "ws", robot: true, name: ["工作空间与速度", "Workspace and speed"], hide: ["dir"],
      params: { x: { min: -0.4, max: 0.4, step: 0.005, value: 0 }, y: { min: -0.4, max: 0.4, step: 0.005, value: 0 }, z: { min: -0.72, max: -0.25, step: 0.005, value: -0.42 } },
      problem: { title: ["机器人问题：吸盘在这里能动多快", "Robot problem: how fast can the cup move here"],
                 text: ["用滑块给出平台中心。界面显示三个转角、沿 x、y、z 的最大速度和各方向都能保证的速度 v_g；彩色点是当前高度上的工作空间截面，颜色越深 v_g 越大。",
                        "Set the platform centre. The readouts give the three angles, the top speeds along x, y, z and the speed v_g guaranteed in every direction; the coloured dots are the workspace at this height, darker for larger v_g."] } },
    { id: "pick", robot: true, name: ["拾放节拍", "Pick-cycle time"],
      params: { x: { min: -0.12, max: 0.12, step: 0.01, value: 0 }, y: { min: -0.12, max: 0.12, step: 0.01, value: 0 }, z: { min: -0.62, max: -0.38, step: 0.01, value: -0.45 } },
      problem: { title: ["机器人问题：传送带放在哪里，节拍最短", "Robot problem: where should the conveyors go"],
                 text: ["滑块给出循环的中心、拾放高度和平移方向。按“运行”，平台走一次 25/305/25 mm 循环（放慢 20 倍）；每段按电机不超速的最大匀速走，界面给出节拍下限。",
                        "The sliders set the centre of the cycle, the pick height and the direction of travel. Press Run: the platform does one 25/305/25 mm cycle (20 times slower), each leg at the fastest constant speed the motors allow; the lower bound of the cycle time is shown."] } },
    { id: "cam", name: ["体育场的索拉摄像机", "A cable-suspended stadium camera"], hide: ["x", "y", "z", "dir"],
      problem: { title: ["生活中的例子：四根钢索吊着摄像机飞", "Everyday example: a camera flying on four cables"],
                 text: ["四座塔顶的绞车收放钢索，摄像机在球场上空移动（按 1:100 画出；球场 100 m × 70 m、塔高 40 m、绞车速度上限 10 m/s 都是示意值）。按“运行”，摄像机从一角飞到对角；飞行速度取四台绞车都不超过 10 m/s 的最大值。",
                        "Winches on four towers reel the cables and move the camera over the pitch (drawn at 1:100; the 100 m × 70 m pitch, 40 m towers and 10 m/s winch limit are illustrative values). Press Run: the camera flies corner to corner at the fastest speed with no winch above 10 m/s."] } },
  ],
  params: [
    { id: "x", name: ["x（平台中心或循环中心）", "x (platform or cycle centre)"], min: -0.4, max: 0.4, step: 0.005, value: 0, unit: "m", digits: 3 },
    { id: "y", name: ["y（平台中心或循环中心）", "y (platform or cycle centre)"], min: -0.4, max: 0.4, step: 0.005, value: 0, unit: "m", digits: 3 },
    { id: "z", name: ["z（平台中心或拾放高度）", "z (platform centre or pick height)"], min: -0.72, max: -0.25, step: 0.005, value: -0.42, unit: "m", digits: 3 },
    { id: "dir", name: ["平移方向：0 沿 x，1 沿 y", "travel: 0 along x, 1 along y"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["运行", "Run"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "rest", robot: true, text: ["静止位置 (0, 0, −0.42) m：读出保证速度 v_g（约 2.00 m/s）和沿 z 的最大速度（约 2.63 m/s）。",
                                       "At rest (0, 0, −0.42) m read the guaranteed speed v_g (about 2.00 m/s) and the top speed along z (about 2.63 m/s)."],
      demo: { scene: "ws", set: { x: 0, y: 0, z: -0.42 }, press: [], wait: 2 } },
    { id: "slow", robot: true, text: ["找一个保证速度低于 1 m/s 的位置（提示：沿中心轴往下走），说明为什么这里慢。", "Find a place where v_g is below 1 m/s (hint: go down the central axis) and say why it is slow there."],
      demo: { scene: "ws", set: { x: 0, y: 0, z: -0.7 }, press: [], wait: 2 } },
    { id: "cyc", robot: true, text: ["复现算例 18.4.3：中心 (0, 0)、高度 −0.45 m、沿 x，运行一次，节拍下限约 0.273 s。", "Example 18.4.3: centre (0, 0), height −0.45 m, along x; run once, the bound is about 0.273 s."],
      demo: { scene: "pick", set: { x: 0, y: 0, z: -0.45, dir: 0 }, press: ["start"], wait: 9 } },
    { id: "fast", robot: true, text: ["找一个节拍下限小于 0.23 s 的放置，并运行一次。", "Find a placement with a cycle-time bound under 0.23 s and run it once."],
      demo: { scene: "pick", set: { x: 0.1, y: 0, z: -0.55, dir: 1 }, press: ["start"], wait: 9 } },
    { id: "cam", text: ["生活场景：按“运行”，让摄像机从球场一角飞到对角，四台绞车都不超过 10 m/s。", "Everyday scene: press Run and fly the camera corner to corner with no winch above 10 m/s."],
      demo: { scene: "cam", set: {}, press: ["start"], wait: 9 } },
  ],
  think: ["保证速度在工作空间中部偏下最大，在靠近静平台和靠近下边界处都很小。从式 (18.4.3) 看，这两处分别是 A 还是 B 出了问题？",
          "The guaranteed speed is largest a little below the middle of the workspace and small near the base and near the lower edge. From Eq. (18.4.3), is it A or B that causes trouble at each place?"],

  // ---------------- Delta 的几何、逆解、速度
  D: { Rb: 0.15, Rp: 0.04, La: 0.22, Lb: 0.5, lo: -40 * Math.PI / 180, hi: Math.PI / 2, wmax: 10.471976 },
  ek(k) { const f = 2 * Math.PI * k / 3; return [Math.cos(f), Math.sin(f), 0]; },
  elbow(k, th) { const e = this.ek(k), D = this.D; return [D.Rb * e[0] + D.La * Math.cos(th) * e[0], D.Rb * e[1] + D.La * Math.cos(th) * e[1], -D.La * Math.sin(th)]; },
  legIK(k, p) {
    const D = this.D, e = this.ek(k), q = [p[0] + (D.Rp - D.Rb) * e[0], p[1] + (D.Rp - D.Rb) * e[1], p[2]];
    const u = q[0] * e[0] + q[1] * e[1], h = q[2], A = -2 * D.La * u, B = 2 * D.La * h, C = D.Lb * D.Lb - D.La * D.La - (q[0] * q[0] + q[1] * q[1] + h * h), r = Math.hypot(A, B);
    if (Math.abs(C) > r) return null;
    const t = Math.atan2(B, A) + Math.acos(C / r);
    return Math.atan2(Math.sin(t), Math.cos(t));
  },
  ik(p) {
    const th = [0, 1, 2].map((k) => this.legIK(k, p));
    if (th.some((t) => t === null || t < this.D.lo - 1e-12 || t > this.D.hi + 1e-12)) return null;
    return th;
  },
  J(p, th) {
    const D = this.D, A = [], B = [];
    for (let k = 0; k < 3; k++) {
      const e = this.ek(k), E = this.elbow(k, th[k]), d = [p[0] + D.Rp * e[0] - E[0], p[1] + D.Rp * e[1] - E[1], p[2] - E[2]], L = Math.hypot(...d), u = d.map((v) => v / L);
      const dE = [-D.La * Math.sin(th[k]) * e[0], -D.La * Math.sin(th[k]) * e[1], -D.La * Math.cos(th[k])];
      A.push(u); B.push(u[0] * dE[0] + u[1] * dE[1] + u[2] * dE[2]);
    }
    return { A, B };
  },
  Jinv(p, th) { const { A, B } = this.J(p, th); return [0, 1, 2].map((k) => A[k].map((x) => x / B[k])); },   // J⁻¹ = B⁻¹A：第 k 行为 u_kᵀ / B_kk
  vAlong(p, th, d) { const R = this.Jinv(p, th); return this.D.wmax / Math.max(...R.map((r) => Math.abs(r[0] * d[0] + r[1] * d[1] + r[2] * d[2]))); },
  vg(p, th) { const R = this.Jinv(p, th); return this.D.wmax / Math.max(...R.map((r) => Math.hypot(...r))); },
  // ---------------- 拾放循环
  cycle(c, zp, dir) {
    const a = dir ? [0, 0.1525, 0] : [0.1525, 0, 0], C = [c[0], c[1], zp];
    const P = [[C[0] - a[0], C[1] - a[1], zp], [C[0] - a[0], C[1] - a[1], zp + 0.025], [C[0] + a[0], C[1] + a[1], zp + 0.025], [C[0] + a[0], C[1] + a[1], zp]];
    const segs = [];
    for (let i = 0; i < 3; i++) {
      const S0 = P[i], S1 = P[i + 1], L = Math.hypot(S1[0] - S0[0], S1[1] - S0[1], S1[2] - S0[2]), d = [0, 1, 2].map((j) => (S1[j] - S0[j]) / L);
      let vm = Infinity;
      for (let s = 0; s <= 60; s++) { const p = [0, 1, 2].map((j) => S0[j] + s / 60 * (S1[j] - S0[j])), th = this.ik(p); if (!th) return null; vm = Math.min(vm, this.vAlong(p, th, d)); }
      segs.push({ S0, S1, L, d, v: vm });
    }
    return { segs, T: 2 * segs.reduce((t, g) => t + g.L / g.v, 0) };
  },
  at(cy, t) {   // 循环中 t 时刻的位置（去程后原路返回）
    const half = cy.T / 2, back = t > half;
    let tt = back ? cy.T - t : t;
    for (const g of cy.segs) { if (tt <= g.L / g.v) return [0, 1, 2].map((j) => g.S0[j] + g.d[j] * g.v * tt); tt -= g.L / g.v; }
    return cy.segs[2].S1;
  },
  // ---------------- 索拉摄像机（1:100）
  TOW: [[-50, -35], [50, -35], [50, 35], [-50, 35]].map((c) => [c[0], c[1], 40]),
  camPath(u) { return [-40 + 80 * u, -25 + 50 * u, 15 + 10 * Math.sin(Math.PI * u)]; },
  camSpeed() {   // 不使任何绞车超过 10 m/s 的最大匀速（沿路径取样）
    let vmax = Infinity;
    for (let s = 0; s <= 200; s++) {
      const u = s / 200, p = this.camPath(u), q = this.camPath(Math.min(1, u + 1e-4)), p0 = this.camPath(Math.max(0, u - 1e-4));
      const t = [0, 1, 2].map((j) => q[j] - p0[j]), n = Math.hypot(...t), d = t.map((x) => x / n);
      const m = Math.max(...this.TOW.map((T) => { const c = [0, 1, 2].map((j) => p[j] - T[j]), L = Math.hypot(...c); return Math.abs((c[0] * d[0] + c[1] * d[1] + c[2] * d[2]) / L); }));
      vmax = Math.min(vmax, 10 / m);
    }
    return vmax;
  },

  // ---------------- 三维
  poseDelta(api, th, p) {
    const h = api.m["B-PAR-DELTA"], D = this.D;
    h.set({ J1: th[0], J2: th[1], J3: th[2] });
    for (let k = 0; k < 3; k++) {
      const e = this.ek(k), t = [-e[1], e[0], 0], E = this.elbow(k, th[k]), P = [p[0] + D.Rp * e[0], p[1] + D.Rp * e[1], p[2]];
      const dz = [(P[0] - E[0]) / D.Lb, (P[1] - E[1]) / D.Lb, (P[2] - E[2]) / D.Lb];
      let dy = [dz[1] * t[2] - dz[2] * t[1], dz[2] * t[0] - dz[0] * t[2], dz[0] * t[1] - dz[1] * t[0]];
      const n = Math.hypot(...dy); dy = dy.map((v) => v / n);
      const node = h.nodes["lower" + (k + 1)];
      node.matrixAutoUpdate = false;
      node.matrix.set(t[0], dy[0], dz[0], (E[0] + P[0]) / 2, t[1], dy[1], dz[1], (E[1] + P[1]) / 2, t[2], dy[2], dz[2], (E[2] + P[2]) / 2, 0, 0, 0, 1);
    }
    const pl = h.nodes.platform;
    pl.matrixAutoUpdate = false;
    pl.matrix.makeTranslation(p[0], p[1], p[2]);
    h.root.updateMatrixWorld(true);
  },
  W(api, p) { return api.m["B-PAR-DELTA"].point("base", p); },   // 机器人基座坐标 → 世界坐标
  setup3d(api, keep) {
    const T = api.three, dl = api.m["B-PAR-DELTA"];
    dl.place(0, 0);
    api.axes(dl, "base", 0.12);
    keep.tr = api.trace(0xd62728);
    // 工作空间截面的点云
    const n = 43 * 43, geo = new T.BufferGeometry();
    geo.setAttribute("position", new T.BufferAttribute(new Float32Array(3 * n), 3));
    geo.setAttribute("color", new T.BufferAttribute(new Float32Array(3 * n), 3));
    keep.cloud = new T.Points(geo, new T.PointsMaterial({ size: 0.02, vertexColors: true }));
    api.st.scene.add(keep.cloud);
    keep.cloudZ = null;
    // 索拉摄像机：塔、钢索、摄像机（世界坐标中按 1:100，放在 Delta 旁边的空地上，场景切换时只显示一组）
    const g = new T.Group(), mat = new T.MeshStandardMaterial({ color: 0x8a96a0 });
    const field = new T.Mesh(new T.BoxGeometry(1.0, 0.004, 0.7), new T.MeshStandardMaterial({ color: 0x5c9e5c }));
    field.position.set(0, 0.002, 0); g.add(field);
    keep.cam0 = new T.Vector3(0, 0, 0);
    this.TOW.forEach((P) => { const m = new T.Mesh(new T.CylinderGeometry(0.012, 0.016, 0.4, 12), mat); m.position.set(P[0] / 100, 0.2, -P[1] / 100); g.add(m); });
    keep.cables = this.TOW.map(() => { const lg = new T.BufferGeometry(); lg.setAttribute("position", new T.BufferAttribute(new Float32Array(6), 3)); const ln = new T.Line(lg, new T.LineBasicMaterial({ color: 0x1d2327 })); g.add(ln); return ln; });
    keep.camera = new T.Mesh(new T.SphereGeometry(0.02, 16, 12), new T.MeshStandardMaterial({ color: 0xd62728 }));
    g.add(keep.camera);
    g.position.set(2.0, 0, 0);
    api.st.scene.add(g);
    keep.stadium = g;
    keep.camTr = api.trace(0x1f77b4);
    api.m.frameCam = { entry: { robot: {} }, holder: { visible: false }, box: () => new T.Box3(new T.Vector3(1.45, 0, -0.45), new T.Vector3(2.55, 0.45, 0.45)) };
    keep.shown = null;
  },
  fillCloud(api, z) {
    const K = api.keep, pos = K.cloud.geometry.attributes.position, col = K.cloud.geometry.attributes.color;
    let i = 0;
    for (let a = 0; a < 43; a++) for (let b = 0; b < 43; b++) {
      const p = [-0.42 + 0.02 * a, -0.42 + 0.02 * b, z], th = this.ik(p);
      if (th) {
        const v = this.vg(p, th), s = Math.max(0, Math.min(1, (v - 0.6) / 1.7)), w = this.W(api, p);
        pos.setXYZ(i, w.x, w.y, w.z);
        col.setXYZ(i, 0.98 - 0.9 * s, 0.85 - 0.55 * s, 0.35 + 0.35 * s);
      } else pos.setXYZ(i, 0, -10, 0);
      i++;
    }
    pos.needsUpdate = true; col.needsUpdate = true;
    K.cloudZ = z;
  },
  posCam(api, p) {
    const K = api.keep, w = (P) => [P[0] / 100, P[2] / 100, -P[1] / 100];
    const c = w(p);
    K.camera.position.set(...c);
    K.cables.forEach((ln, i) => { const a = ln.geometry.attributes.position, T = w(this.TOW[i]); a.setXYZ(0, T[0], T[1] - 0.0, T[2]); a.setXYZ(1, ...c); a.needsUpdate = true; });
    K.stadium.updateMatrixWorld(true);
  },
  reset(api, s) {
    s.u = null; s.cy = null; s.result = null;
    const K = api.keep;
    if (!K || !K.tr) return;
    K.tr.clear(); K.camTr.clear();
    if (api.scene === "cam") this.posCam(api, this.camPath(0));
  },
  start(api, s) {
    const K = api.keep;
    K.tr.clear(); K.camTr.clear();
    if (api.scene === "pick") {
      s.cy = this.cycle([api.p.x, api.p.y], api.p.z, api.p.dir);
      if (!s.cy) { api.stop(); return; }
      s.t = 0; s.u = 0; s.cfg = [api.p.x, api.p.y, api.p.z, api.p.dir];
    } else if (api.scene === "cam") { s.vcam = this.camSpeed(); s.u = 0; s.wmax = 0; }
    else api.stop();
  },
  update(dt, api, s) {
    if (s.u == null) { api.stop(); return; }
    if (api.scene === "pick" && s.cy) {
      s.t = Math.min(s.cy.T, s.t + dt / 20);
      const p = this.at(s.cy, s.t), th = this.ik(p);
      if (th) this.poseDelta(api, th, p);
      api.keep.tr.add(api.m["B-PAR-DELTA"].point("platform", [0, 0, 0]));
      if (s.t >= s.cy.T - 1e-12) {
        s.u = null; s.result = s.cy.T; api.stop();
        const c = s.cfg;
        if (Math.abs(c[0]) < 1e-9 && Math.abs(c[1]) < 1e-9 && Math.abs(c[2] + 0.45) < 1e-9 && c[3] === 0 && Math.abs(s.cy.T - 0.273) < 0.002) api.done("cyc");
        if (s.cy.T < 0.23) api.done("fast");
      }
    } else if (api.scene === "cam") {
      const L = Math.hypot(80, 50) * 1.02;           // 路径长度（略大于对角线，有升降）
      s.u = Math.min(1, s.u + 2 * dt * s.vcam / L);   // 以两倍速度播放
      const p = this.camPath(s.u);
      this.posCam(api, p);
      api.keep.camTr.add(api.keep.camera.getWorldPosition(new api.three.Vector3()));
      if (s.u >= 1) { s.u = null; api.stop(); api.done("cam"); }
    } else api.stop();
  },
  readouts(api, s) {
    const f = (v, n) => api.fmt(v, n), K = api.keep;
    if (!K || !K.tr) return [];
    if (api.scene === "cam") {
      const v = s.vcam || this.camSpeed(), p = this.camPath(s.u == null ? 0 : s.u);
      return [[["飞行速度（不使绞车超速的最大匀速）", "flight speed (fastest with no winch over its limit)"], f(v, 2) + " m/s"],
              [["摄像机位置", "camera position"], `(${f(p[0], 1)}, ${f(p[1], 1)}, ${f(p[2], 1)}) m`],
              [["四根钢索长", "cable lengths"], this.TOW.map((T) => f(Math.hypot(p[0] - T[0], p[1] - T[1], p[2] - T[2]), 1)).join(", ") + " m"]];
    }
    if (api.scene === "pick") {
      const cy = s.cy || this.cycle([api.p.x, api.p.y], api.p.z, api.p.dir);
      if (!cy) return [[["循环", "cycle"], api.T("有一部分在工作空间以外", "part of it lies outside the workspace")]];
      const rows = [[["三段的最大匀速", "top constant speeds of the three legs"], cy.segs.map((g) => f(g.v, 3)).join(", ") + " m/s"],
                    [["节拍下限（一次往返）", "cycle-time bound (round trip)"], f(cy.T, 4) + " s"], [["每分钟最多", "at most per minute"], f(60 / cy.T, 0)]];
      if (s.result) rows.push([["已运行一次", "run once"], f(s.result, 4) + " s"]);
      return rows;
    }
    const p = [api.p.x, api.p.y, api.p.z], th = this.ik(p);
    if (!th) return [[["状态", "state"], api.T("不在工作空间内（无解或超出关节限位）", "outside the workspace (no solution or beyond the joint limits)")]];
    const v = this.vg(p, th), vx = this.vAlong(p, th, [1, 0, 0]), vy = this.vAlong(p, th, [0, 1, 0]), vz = this.vAlong(p, th, [0, 0, 1]);
    const near = (a, b) => Math.abs(a - b) < 1e-9;
    if (near(p[0], 0) && near(p[1], 0) && near(p[2], -0.42)) api.done("rest");
    if (v < 1) api.done("slow");
    const R = this.Jinv(p, th);
    return [[["转角 θ₁, θ₂, θ₃", "angles θ₁, θ₂, θ₃"], th.map((t) => f(t * 180 / Math.PI, 2) + "°").join(", ")],
            [["沿 x、y、z 的最大速度", "top speed along x, y, z"], `${f(vx, 3)}, ${f(vy, 3)}, ${f(vz, 3)} m/s`],
            [["保证速度 v_g", "guaranteed speed v_g"], f(v, 3) + " m/s"],
            [["J⁻¹ 各行的长度", "lengths of the rows of J⁻¹"], R.map((r) => f(Math.hypot(...r), 2)).join(", ") + " rad/m"]];
  },
  draw(api, s) {
    const m = api.m, K = api.keep;
    if (!K.tr) return;
    const sc = api.scene, isCam = sc === "cam";
    m["B-PAR-DELTA"].holder.visible = !isCam;
    K.stadium.visible = isCam;
    K.cloud.visible = sc === "ws";
    K.tr.line.visible = sc === "pick";
    K.camTr.line.visible = isCam;
    if (K.shown !== sc) { K.shown = sc; api.view(isCam ? 30 : 35, isCam ? 35 : 18, 0.85, isCam ? m.frameCam : m["B-PAR-DELTA"]); if (isCam) this.posCam(api, this.camPath(s.u == null ? 0 : s.u)); }
    if (sc === "ws") {
      if (K.cloudZ !== api.p.z) this.fillCloud(api, api.p.z);
      const p = [api.p.x, api.p.y, api.p.z], th = this.ik(p);
      if (th) this.poseDelta(api, th, p);
    } else if (sc === "pick" && !api.running) {
      const cy = s.cy || this.cycle([api.p.x, api.p.y], api.p.z, api.p.dir);
      if (cy) { const p = cy.segs[0].S0, th = this.ik(p); if (th) this.poseDelta(api, th, p); }
    }
  },
});
