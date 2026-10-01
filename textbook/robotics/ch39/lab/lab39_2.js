// 实验 39.2 应变片电桥与仪表放大器（配 39.2 节）。电路仿真器 CircuitJS 中搭好整条前端：5 V 激励的电桥（350 Ω 应变片）
// → 三运放仪表放大器（R = 24.7 kΩ，增益 G = 1 + 2R/R_g）→ 输出 Vout。下方虚拟仪表把 Vout 送入 12 位、2.5 V 的 ADC。
// 力 F 改变应变：全桥四片应变片 ±ε，ε = 1000 µε × F/100 N（额定输出 2 mV/V）；单臂电桥只有一片应变片。
WQ.lab({
  title: ["实验 39.2 应变片电桥与仪表放大器", "Lab 39.2 Strain-gauge bridge and instrumentation amplifier"],
  goal: ["给传感器加力，看电桥输出的几毫伏怎样被仪表放大器放大到模数转换器的量程；比较全桥与单臂电桥。",
         "Load the sensor and watch the bridge's few millivolts amplified to the ADC range; compare a full bridge with a quarter bridge."],
  view: "circuit",
  circuit: "",
  scenes: [
    { id: "full", robot: true, name: ["全桥（腕部测力传感器）", "Full bridge (wrist force sensor)"],
      problem: { title: ["机器人问题：夹爪的夹紧力", "Robot problem: the gripper's clamping force"],
                 text: ["腕部测力传感器量程 100 N、额定输出 2 mV/V。要把满量程的 10 mV 放大到 2.5 V，增益电阻取多大？",
                        "The wrist sensor reads up to 100 N at 2 mV/V. What gain resistor turns the 10 mV full-scale signal into 2.5 V?"] } },
    { id: "quarter", name: ["单臂电桥（厨房秤的简化版）", "Quarter bridge (a simplified kitchen scale)"],
      problem: { title: ["生活中的例子：电子秤", "Everyday example: a kitchen scale"],
                 text: ["只用一片应变片也能称重，但输出只有全桥的四分之一，而且不是严格的直线。",
                        "One strain gauge can weigh, but the output is a quarter of a full bridge's and not exactly linear."] } },
  ],
  params: [
    { id: "F", name: ["作用力 F", "Force F"], min: 0, max: 100, step: 1, value: 0, unit: "N", digits: 0 },
    { id: "rg", name: ["增益电阻 R_g", "Gain resistor R_g"], min: 100, max: 1000, step: 1, value: 500, unit: "Ω", digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "zero", robot: true, text: ["全桥、F = 0：电桥平衡，读出 Vp − Vm 和 Vout。", "Full bridge, F = 0: the bridge is balanced; read Vp − Vm and Vout."],
      demo: { scene: "full", set: { F: 0, rg: 500 }, press: [], wait: 3 } },
    { id: "gain", robot: true, text: ["全桥、F = 100 N：调 R_g，使 Vout 在 2.45 V 到 2.50 V 之间（ADC 不溢出）。", "Full bridge, F = 100 N: set R_g so that Vout is 2.45–2.50 V (no ADC overflow)."],
      demo: { scene: "full", set: { F: 100, rg: 200 }, press: [], wait: 3 } },
    { id: "quarter", text: ["单臂电桥、F = 100 N：电桥输出约为全桥的四分之一。", "Quarter bridge, F = 100 N: the bridge output is about a quarter of the full bridge's."],
      demo: { scene: "quarter", set: { F: 100, rg: 200 }, press: [], wait: 3 } },
  ],
  think: ["全桥为什么能自动补偿温度引起的电阻变化？单臂电桥的输出为什么不是严格的直线？",
          "Why does a full bridge cancel temperature-induced resistance changes? Why is a quarter bridge not exactly linear?"],

  R: 350, GF: 2, EPS_FS: 1e-3, R_IA: 24700,
  text(api) {
    const x = this.GF * this.EPS_FS * api.p.F / 100, R = this.R, full = api.scene === "full";
    const Ra = full ? R * (1 + x) : R, Rb = full ? R * (1 - x) : R, Rc = full ? R * (1 - x) : R, Rd = R * (1 + x);
    return [
      "$ 1 0.000005 10.2 50 5 50",
      "v 64 400 64 80 0 0 40 5 0 0 0.5",
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
      "a 608 304 736 304 0 15 -15 1000000", "207 736 304 784 304 0 Vout",
    ].join("\n") + "\n";
  },
  setupCircuit(api) { api.load(this.text(api)); },
  reset(api, s) { api.load(this.text(api)); },          // 拖动滑块或换场景时，按新的力和电阻重建电路
  readouts(api, s) {
    const vp = api.v("Vp"), vm = api.v("Vm"), vo = api.v("Vout"), d = (vp - vm) * 1000;
    const code = Math.max(0, Math.min(4095, Math.floor(vo / 2.5 * 4096)));
    const G = 1 + 2 * this.R_IA / api.p.rg;
    if (api.scene === "full" && api.p.F === 0 && Math.abs(d) < 0.01 && Math.abs(vo) < 0.01) api.done("zero");
    if (api.scene === "full" && api.p.F === 100 && vo >= 2.45 && vo <= 2.5) api.done("gain");
    if (api.scene === "quarter" && api.p.F === 100 && d > 2.3 && d < 2.6) api.done("quarter");
    return [[["电桥输出 Vp − Vm", "bridge output Vp − Vm"], api.fmt(d, 4) + " mV"],
            [["放大器增益（计算）", "amplifier gain (calc.)"], api.fmt(G, 1)],
            [["输出 Vout", "output Vout"], api.fmt(vo, 4) + " V"],
            [["ADC 码值（12 位，2.5 V）", "ADC code (12 bit, 2.5 V)"], String(code) + (vo >= 2.5 ? (api.lang() === "en" ? "  overflow" : "  溢出") : "")],
            [["由码值换算的力", "force from the code"], api.fmt(code / 4096 * 2.5 / (G * 0.1e-3), 2) + " N"]];
  },
  draw(api, s) {
    const { w, h } = api, vo = api.v("Vout"), x0 = 20, x1 = w - 20, y = h * 0.55;
    api.label(api.lang() === "en" ? "ADC input 0 … 2.5 V" : "ADC 输入 0 … 2.5 V", x0, h * 0.18, api.css("--muted"), 13);
    api.rect(x0, y - 12, x1 - x0, 24, api.css("--soft"));
    const f = Math.max(0, Math.min(1, (vo || 0) / 2.5));
    api.rect(x0, y - 12, (x1 - x0) * f, 24, vo >= 2.5 ? api.css("--red") : api.css("--accent"));
    api.label(api.fmt(vo || 0, 3) + " V", x0 + 6, y + 30, api.css("--ink"), 15);
  },
});
