// 实验 39.5 测量链的自动标定与检测（配 39.5 节）。电路与实验 39.2 相同（全桥 + 三运放仪表放大器），输出经 12 位、2.5 V 的 ADC 读数
// （超出 0–2.5 V 即溢出）。三种可调的“缺陷”：电桥不平衡 ΔR（R_a 偏大）、增益电阻 R_g、四片应变片中一片的温度系数比其余三片大 Δα（贴片不匹配）。
// 按“自动检测”：程序像测试工位一样依次施加 0→100→0 N（每级 20 N），等电路稳定后读数，最小二乘拟合；再升温 20 K 复测零点，
// 按规格判定满量程输出、零点、线性度、零点温漂（%FS/K），给出报告。
WQ.lab({
  title: ["实验 39.5 测量链的自动标定与检测", "Lab 39.5 Automatic calibration and test of the measuring chain"],
  goal: ["让程序自动加载、读数、拟合和判定，看一台合格的测量链和几种有缺陷的测量链各得到什么报告。",
         "Let the program load, read, fit and judge automatically; compare the reports of a good chain and of faulty ones."],
  view: "circuit",
  circuit: "",
  scenes: [
    { id: "station", robot: true, name: ["出厂检测工位", "End-of-line test station"],
      problem: { title: ["机器人问题：腕部测力传感器的出厂检测", "Robot problem: end-of-line test of a wrist force sensor"],
                 text: ["每个传感器装好后都要在工位上自动加载、读数、判定：满量程输出、零点、线性度、零点温漂都要在规格之内。",
                        "Every sensor is loaded, read and judged automatically: full-scale output, zero, linearity and zero drift must meet the specification."] } },
    { id: "repair", name: ["维修后复检", "Re-test after repair"],
      problem: { title: ["生活中的例子：电子秤为什么要定期校准", "Everyday example: why scales are calibrated regularly"],
                 text: ["超市的电子秤要定期检定。零点、灵敏度会随时间和温度变化，检定就是一次标定加判定。",
                        "Shop scales are verified regularly: zero and sensitivity drift with time and temperature; a verification is a calibration plus a verdict."] } },
  ],
  params: [
    { id: "dR", name: ["电桥不平衡 ΔR（R_a 偏大）", "Bridge imbalance ΔR (R_a high)"], min: 0, max: 0.1, step: 0.01, value: 0, unit: "Ω", digits: 2 },
    { id: "rg", name: ["增益电阻 R_g", "Gain resistor R_g"], min: 180, max: 230, step: 1, value: 200, unit: "Ω", digits: 0 },
    { id: "da", name: ["一片应变片的温度系数失配 Δα", "Temperature-coefficient mismatch of one gauge Δα"], min: 0, max: 2, step: 0.1, value: 0.2, unit: "ppm/K", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["自动检测", "Run test"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "pass", robot: true, text: ["合格品（ΔR = 0、R_g = 200 Ω、Δα = 0.2 ppm/K）：自动检测，结论为合格。", "A good unit (ΔR = 0, R_g = 200 Ω, Δα = 0.2 ppm/K): the verdict is PASS."],
      demo: { scene: "station", set: { dR: 0, rg: 200, da: 0.2 }, press: ["start"], wait: 40 } },
    { id: "zero", robot: true, text: ["电桥不平衡 ΔR = 0.02 Ω：自动检测，只有零点不合格。", "Bridge imbalance ΔR = 0.02 Ω: only the zero fails."],
      demo: { scene: "station", set: { dR: 0.02, rg: 200, da: 0.2 }, press: ["start"], wait: 40 } },
    { id: "drift", text: ["Δα = 1 ppm/K：自动检测，零点温漂不合格；说明为什么其余三项仍然合格。", "Δα = 1 ppm/K: the zero drift fails; explain why the other three items still pass."],
      demo: { scene: "repair", set: { dR: 0, rg: 200, da: 1 }, press: ["start"], wait: 40 } },
  ],
  think: ["零点不合格的传感器，能否通过“去皮”（软件扣除零点）继续使用？零点温漂不合格的呢？",
          "Can a sensor that fails on zero still be used after taring? One that fails on zero drift?"],

  R: 350, GF: 2, EPS_FS: 1e-3, R_IA: 24700, DT: 20, VREF: 2.5, BITS: 12,
  SPEC: { fs: [2.43, 2.50], zero: 0.01, lin: 0.1, drift: 0.005 },      // 满量程输出 V、|零点| V、线性度 %FS、零点温漂 %FS/K
  adc(v) { const q = this.VREF / 2 ** this.BITS; return Math.min(2 ** this.BITS - 1, Math.max(0, Math.floor(v / q))) * q; },
  text(api, F, dT) {
    const x = this.GF * this.EPS_FS * F / 100, R = this.R;
    const Ra = R * (1 + x) + api.p.dR, Rb = R * (1 - x), Rc = R * (1 - x), Rd = R * (1 + x) * (1 + api.p.da * 1e-6 * dT);
    return ["$ 1 0.000005 10.2 50 5 50", "v 64 400 64 80 0 0 40 5 0 0 0.5",
      "w 64 80 160 80 0", "w 160 80 256 80 0", "w 64 400 160 400 0", "w 160 400 256 400 0", "g 64 400 64 432 0",
      `r 160 80 160 240 0 ${Ra}`, `r 160 240 160 400 0 ${Rb}`, `r 256 80 256 240 0 ${Rc}`, `r 256 240 256 400 0 ${Rd}`,
      "207 160 240 112 240 0 Vm", "207 256 240 288 240 0 Vp",
      "a 352 224 480 224 0 15 -15 1000000", "207 352 240 320 240 0 Vm",
      "w 352 208 352 176 0", `r 352 176 480 176 0 ${this.R_IA}`, "w 480 176 480 224 0",
      "a 352 368 480 368 0 15 -15 1000000", "207 352 384 320 384 0 Vp",
      "w 352 352 352 320 0", `r 352 320 480 320 0 ${this.R_IA}`, "w 480 320 480 368 0",
      "w 352 208 304 208 0", `r 304 208 304 352 0 ${api.p.rg}`, "w 304 352 352 352 0",
      "r 480 224 560 224 0 10000", "w 560 224 560 288 0", "w 560 288 608 288 0",
      "w 608 288 608 256 0", "r 608 256 736 256 0 10000", "w 736 256 736 304 0",
      "r 480 368 560 368 0 10000", "w 560 368 560 320 0", "w 560 320 608 320 0",
      "r 608 320 608 400 0 10000", "g 608 400 608 432 0",
      "a 608 304 736 304 0 15 -15 1000000", "207 736 304 784 304 0 Vout"].join("\n") + "\n";
  },
  plan() {   // 检测步骤：[力 N, 温度变化标志]
    const up = [0, 20, 40, 60, 80, 100], steps = up.map((F) => [F, 0]).concat(up.slice(0, -1).reverse().map((F) => [F, 0]));
    return steps.concat([[0, 1]]);
  },
  setupCircuit(api) { api.load(this.text(api, 0, 0)); },
  reset(api, s) { s.i = -1; s.wait = 0; s.data = []; s.report = null; api.load(this.text(api, 0, 0)); },
  start(api, s) { s.i = 0; s.wait = 0; s.ts = null; s.data = []; s.report = null; const [F, t] = this.plan()[0]; api.load(this.text(api, F, t ? this.DT : 0)); },
  update(dt, api, s) {
    if (s.i < 0) return;
    s.wait += dt;
    const ts = api.simTime();
    if (s.ts === null || ts < s.ts) s.ts = ts;
    if (s.wait < 0.25 || ts - s.ts < 0.002) return;   // 等电路稳定后读数（至少 0.25 s，且仿真时间走过 2 ms）
    const plan = this.plan(), [F, t] = plan[s.i];
    const vo = api.v("Vout");
    s.data.push({ F, t, v: this.adc(vo), over: vo >= this.VREF || vo < 0 });
    s.i += 1; s.wait = 0;
    if (s.i < plan.length) { const [F2, t2] = plan[s.i]; s.ts = null; api.load(this.text(api, F2, t2 ? this.DT : 0)); return; }
    s.i = -1; api.stop();
    s.report = this.judge(s.data);
    const r = s.report;
    if (api.scene === "station" && api.p.dR === 0 && api.p.rg === 200 && r.ok) api.done("pass");
    if (api.scene === "station" && api.p.dR > 0 && !r.okZero && r.okFs && r.okLin && r.okDrift) api.done("zero");
    if (api.scene === "repair" && api.p.da >= 1 && !r.okDrift && r.okZero && r.okFs && r.okLin) api.done("drift");
  },
  judge(data) {
    const pts = data.filter((d) => !d.t), n = pts.length;
    const mx = pts.reduce((a, d) => a + d.F, 0) / n, my = pts.reduce((a, d) => a + d.v, 0) / n;
    let sxy = 0, sxx = 0; pts.forEach((d) => { sxy += (d.F - mx) * (d.v - my); sxx += (d.F - mx) ** 2; });
    const b = sxy / sxx, a = my - b * mx, fs = b * 100;
    const lin = Math.max(...pts.map((d) => Math.abs(d.v - (a + b * d.F)))) / fs * 100;
    const z0 = pts[0].v, z1 = data[data.length - 1].v, drift = Math.abs(z1 - z0) / fs * 100 / this.DT, over = data.some((d) => d.over);
    const S = this.SPEC, okFs = fs >= S.fs[0] && fs <= S.fs[1], okZero = Math.abs(a) <= S.zero, okLin = lin <= S.lin, okDrift = drift <= S.drift;
    return { a, b, fs, lin, drift, over, okFs, okZero, okLin, okDrift, ok: okFs && okZero && okLin && okDrift };
  },
  readouts(api, s) {
    const plan = this.plan(), en = api.lang() === "en", P = (ok) => (ok ? (en ? "PASS" : "合格") : (en ? "FAIL" : "不合格"));
    const vo = api.v("Vout");
    const rows = [[["输出 Vout（ADC 读数）", "output Vout (ADC reading)"], api.fmt(this.adc(vo), 4) + " V" + (vo >= this.VREF || vo < 0 ? (en ? " (overflow)" : "（溢出）") : "")]];
    if (s.i >= 0) rows.push([["检测进度", "progress"], `${s.i + 1} / ${plan.length}：F = ${plan[s.i][0]} N${plan[s.i][1] ? (en ? `, +${this.DT} K` : `，升温 ${this.DT} K`) : ""}`]);
    const r = s.report;
    if (r) {
      const S = this.SPEC;
      rows.push([["满量程输出（拟合）", "full-scale output (fit)"], `${api.fmt(r.fs, 4)} V  [${S.fs[0]}–${S.fs[1]}]  ${P(r.okFs)}`],
                [["零点（拟合截距）", "zero (intercept)"], `${api.fmt(r.a * 1000, 2)} mV  [±${S.zero * 1000}]  ${P(r.okZero)}`],
                [["线性度", "linearity"], `${api.fmt(r.lin, 3)} %FS  [≤ ${S.lin}]  ${P(r.okLin)}`],
                [["零点温漂", "zero drift"], `${api.fmt(r.drift, 4)} %FS/K  [≤ ${S.drift}]  ${P(r.okDrift)}`],
                [["结论", "verdict"], (r.ok ? (en ? "PASS" : "合格") : (en ? "FAIL" : "不合格")) + (r.over ? (en ? " (ADC overflow during the test)" : "（检测中 ADC 溢出）") : "")]);
    }
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, x0 = 40, x1 = w - 20, yb = h - 20, yt = 14;
    const X = (F) => x0 + (x1 - x0) * F / 100, Y = (v) => yb - (yb - yt) * v / 2.6;
    api.line(x0, yb, x1, yb, api.css("--line"), 1); api.line(x0, yb, x0, yt, api.css("--line"), 1);
    api.label("F / N", x1 - 30, yb - 8, api.css("--muted"), 11); api.label("Vout", x0 + 4, yt + 4, api.css("--muted"), 11);
    (s.data || []).forEach((d) => api.circle(X(d.F), Y(d.v), d.t ? 5 : 3.5, d.t ? api.css("--red") : api.css("--accent")));
    if (s.report) api.line(X(0), Y(s.report.a), X(100), Y(s.report.a + 100 * s.report.b), api.css("--blue"), 1.5);
  },
});
