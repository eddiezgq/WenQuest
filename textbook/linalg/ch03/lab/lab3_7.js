// 实验 3.7 AGV 电机驱动电路的节点电压（配 3.7.2 节）。电路仿真器 CircuitJS 中搭好图 3.7.1 的直流稳态电路：
// 电池 24 V、内阻 0.2 Ω → 节点 1（母线），控制板 48 Ω 接地；上管 0.05 Ω → 节点 2；电枢 1.2 Ω 与反电动势 Em → 节点 3；
// 下管 0.05 Ω → 节点 4；采样电阻 Rs 接地。下方同时显示由节点方程组 G V = i 用消元解出的电位，与仿真器的结果比较。
WQ.lab({
  title: ["实验 3.7 AGV 电机驱动电路的节点电压", "Lab 3.7 Node voltages of the AGV motor drive"],
  goal: ["调节电机转速（反电动势）和采样电阻，读出四个节点的电位和电机电流；用节点方程组解出同样的电位，与电路仿真器的结果比较。",
         "Change the motor speed (back-EMF) and the sense resistor; read the four node voltages and the motor current; solve the node equations for the same voltages and compare with the circuit simulator."],
  view: "circuit",
  circuit: "",
  scenes: [
    { id: "drive", robot: true, name: ["电机驱动", "Motor drive"],
      problem: { title: ["机器人问题：电机电流有多大？", "Robot problem: how large is the motor current?"],
                 text: ["电机转得越快，反电动势越大，电流越小；堵转时反电动势为零，电流最大。控制器通过采样电阻上的电压得知电流。",
                        "The faster the motor turns, the larger the back-EMF and the smaller the current; at stall the back-EMF is zero and the current is largest. The controller reads the current from the sense-resistor voltage."] } },
  ],
  params: [
    { id: "em", name: ["反电动势 Em（与转速成正比）", "Back-EMF Em (proportional to speed)"], min: 0, max: 20, step: 0.5, value: 12, unit: "V", digits: 1 },
    { id: "rs", name: ["采样电阻 Rs", "Sense resistor Rs"], min: 0.05, max: 0.5, step: 0.05, value: 0.1, unit: "Ω", digits: 2 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "stall", robot: true, text: ["让电机堵转（Em = 0），读出电机电流。", "Stall the motor (Em = 0) and read the motor current."],
      demo: { scene: "drive", set: { em: 0, rs: 0.1 }, press: [], wait: 3 } },
    { id: "five", robot: true, text: ["找出使电机电流约为 5 A（误差 0.1 A 以内）的反电动势。", "Find the back-EMF giving a motor current of about 5 A (within 0.1 A)."],
      demo: { scene: "drive", set: { em: 16, rs: 0.1 }, press: [], wait: 3 } },
    { id: "rs", text: ["把采样电阻加倍到 0.2 Ω（Em = 12 V），观察哪些节点电位变了、采样电压变了多少。", "Double the sense resistor to 0.2 Ω (Em = 12 V); which node voltages change, and by how much does the sense voltage change?"],
      demo: { scene: "drive", set: { em: 12, rs: 0.2 }, press: [], wait: 3 } },
    { id: "match", text: ["确认仿真器的四个电位与方程组的解相差不到 1 mV。", "Check that the simulator's four voltages agree with the solution of the equations to within 1 mV."],
      demo: { scene: "drive", set: { em: 12, rs: 0.1 }, press: [], wait: 3 } },
  ],
  think: ["为什么节点方程组的系数矩阵 G 关于对角线对称？若电路中有一个受控源（如运放），还对称吗？",
          "Why is the node matrix G symmetric? Would it stay symmetric with a controlled source (such as an op-amp)?"],

  E: 24, rb: 0.2, RL: 48, Rh: 0.05, Ra: 1.2,
  text(api) {
    return [
      "$ 1 0.000005 10.2 50 5 50",
      `v 64 400 64 80 0 0 40 ${this.E} 0 0 0.5`,
      `r 64 80 192 80 0 ${this.rb}`,
      `r 192 80 192 400 0 ${this.RL}`,
      `r 192 80 320 80 0 ${this.Rh}`,
      `r 320 80 320 208 0 ${this.Ra}`,
      `v 320 336 320 208 0 0 40 ${api.p.em} 0 0 0.5`,
      `r 320 336 448 336 0 ${this.Rh}`,
      `r 448 336 448 400 0 ${api.p.rs}`,
      "w 64 400 192 400 0", "w 192 400 448 400 0", "g 64 400 64 432 0",
      "207 192 80 192 48 0 V1", "207 320 80 352 48 0 V2", "207 320 336 288 368 0 V3", "207 448 336 480 304 0 V4",
    ].join("\n") + "\n";
  },
  setupCircuit(api) { api.load(this.text(api)); },
  reset(api) { api.load(this.text(api)); },
  solve(api) {   // node equations G V = i, solved by Gaussian elimination with partial pivoting
    const g = (r) => 1 / r, Em = api.p.em, Rs = api.p.rs;
    const G = [[g(this.rb) + g(this.RL) + g(this.Rh), -g(this.Rh), 0, 0],
               [-g(this.Rh), g(this.Rh) + g(this.Ra), -g(this.Ra), 0],
               [0, -g(this.Ra), g(this.Ra) + g(this.Rh), -g(this.Rh)],
               [0, 0, -g(this.Rh), g(this.Rh) + g(Rs)]];
    const b = [this.E * g(this.rb), Em * g(this.Ra), -Em * g(this.Ra), 0];
    const M = G.map((r, i) => r.concat([b[i]])), n = 4;
    for (let k = 0; k < n; k++) {
      let p = k; for (let i = k + 1; i < n; i++) if (Math.abs(M[i][k]) > Math.abs(M[p][k])) p = i;
      [M[k], M[p]] = [M[p], M[k]];
      for (let i = k + 1; i < n; i++) { const l = M[i][k] / M[k][k]; for (let j = k; j <= n; j++) M[i][j] -= l * M[k][j]; }
    }
    const V = [0, 0, 0, 0];
    for (let i = n - 1; i >= 0; i--) { let s = M[i][n]; for (let j = i + 1; j < n; j++) s -= M[i][j] * V[j]; V[i] = s / M[i][i]; }
    return V;
  },
  readouts(api) {
    const V = this.solve(api), S = ["V1", "V2", "V3", "V4"].map((k) => api.v(k));
    const ok = S.every((x) => isFinite(x));
    const Im = (V[1] - V[2] - api.p.em) / this.Ra, Ib = (this.E - V[0]) / this.rb, IL = V[0] / this.RL;
    const diff = ok ? Math.max(...S.map((x, i) => Math.abs(x - V[i]))) : NaN;
    if (api.p.em === 0 && Math.abs(api.p.rs - 0.1) < 1e-9 && ok && diff < 1e-3) api.done("stall");
    if (Math.abs(Im - 5) < 0.1 && ok && diff < 1e-3) api.done("five");
    if (Math.abs(api.p.rs - 0.2) < 1e-9 && api.p.em === 12 && ok && diff < 1e-3) api.done("rs");
    if (ok && diff < 1e-3) api.done("match");
    const v4 = (a) => a.map((x) => api.fmt(x, 3)).join(", ");
    return [[["仿真器：V1, V2, V3, V4", "Simulator: V1, V2, V3, V4"], ok ? v4(S) + " V" : "…"],
            [["方程组的解：V1, V2, V3, V4", "Equations: V1, V2, V3, V4"], v4(V) + " V"],
            [["两者最大差", "Largest difference"], ok ? api.fmt(1000 * diff, 3) + " mV" : "…"],
            [["电机电流 (V2 − V3 − Em)/1.2", "Motor current (V2 − V3 − Em)/1.2"], api.fmt(Im, 3) + " A"],
            [["采样电压 V4 与 V4/Rs", "Sense voltage V4 and V4/Rs"], api.fmt(V[3], 4) + " V / " + api.fmt(V[3] / api.p.rs, 3) + " A"],
            [["节点 1：电池电流 = 控制板 + 电机", "Node 1: battery = controller + motor"], api.fmt(Ib, 3) + " = " + api.fmt(IL, 3) + " + " + api.fmt(Ib - IL, 3) + " A"]];
  },
  draw(api) {
    const { w, h } = api, V = this.solve(api), Im = (V[1] - V[2] - api.p.em) / this.Ra;
    const x0 = 20, x1 = w - 20, y = h * 0.5, f = Math.max(0, Math.min(1, Im / 16));
    api.label(api.T("电机电流 0 … 16 A", "motor current 0 … 16 A"), x0, h * 0.2, api.css("--muted"), 13);
    api.rect(x0, y - 12, x1 - x0, 24, api.css("--soft"));
    api.rect(x0, y - 12, (x1 - x0) * f, 24, Im > 12 ? api.css("--red") : api.css("--accent"));
    api.label(api.fmt(Im, 2) + " A", x0 + 6, y + 30, api.css("--ink"), 15);
  },
});
