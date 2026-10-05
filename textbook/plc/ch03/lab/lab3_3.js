// 实验 3.3 PLC 输入输出的接线（配 3.3–3.5 节）。电路仿真器 CircuitJS 里搭好三段电路，学生改参数、量电压电流：
// （1）三线制传感器接 PLC 数字量输入：PNP / NPN 传感器 × 公共端接 M / 接 L+（输入光耦简化成 4.7 kΩ 电阻加一只发光二极管）；
// （2）继电器输出断开电磁阀线圈（0.2 A、120 Ω、0.5 H）：没有吸收电路时触点两端的电压尖峰，加续流二极管后衔铁释放变慢；
// （3）两线制 4–20 mA 液位计接模拟量输入（250 Ω），量程与断线。
// 换参数时电路按新参数重建；断开的那一刻用“电感里还有 0.2 A 电流、开关已经断开”的初始状态表示。
const H = "$ 1 0.000005 2 50 5 50";              // 时间步 5 µs；仿真放慢，便于看清毫秒级的过程
function rail(y, xs) {                           // a supply line through the given points (CircuitJS joins wires only at their ends)
  const p = [...new Set(xs)].sort((a, b) => a - b), out = [];
  for (let i = 0; i + 1 < p.length; i++) out.push(`w ${p[i]} ${y} ${p[i + 1]} ${y} 0`);
  return out;
}
const SUPPLY = ["v 64 352 64 96 0 0 40 24 0 0 0.5", "g 64 352 64 384 0"];
function inputCircuit(p) {
  const pnp = p.sensor === 0, into = p.common === 0, on = p.on === 1;
  const sw = pnp ? `s 192 96 192 224 0 ${on ? 0 : 1} false` : `s 192 224 192 352 0 ${on ? 0 : 1} false`;
  const comTo = into ? "w 464 224 464 352 0" : "w 464 224 464 96 0";
  const top = [64, 192].concat(into ? [] : [464]), bot = [64, 192].concat(into ? [464] : []);
  return [H, ...SUPPLY, ...rail(96, top), ...rail(352, bot), sw,
    "w 192 224 320 224 0", "r 320 224 400 224 0 4700",
    into ? "d 400 224 464 224 2 default" : "d 464 224 400 224 2 default", comTo,
    "207 320 224 320 176 0 I0", "207 400 224 400 176 0 IR", "207 464 224 512 224 0 COM", "207 192 224 144 224 0 Q"].join("\n") + "\n";
}
function outputCircuit(p) {
  const on = p.out === 1, diode = p.supp === 1;
  const head = diode ? "$ 1 0.000005 6 50 5 50" : H;   // with the diode nothing fast happens: run the slow decay quicker
  const lines = [head, ...SUPPLY, ...rail(96, [64, 192, 256]), ...rail(352, diode ? [64, 128, 192] : [64, 192]),
    `s 192 96 192 224 0 ${on ? 0 : 1} false`, "r 256 96 256 224 0 2000", "w 256 224 192 224 0",   // 2 kΩ: the open contact's leakage and stray paths
    "r 192 224 192 288 0 120", "l 192 288 192 352 0 0.5 0.2",
    "207 192 224 144 224 0 Q0", "207 192 288 240 288 0 QL"];
  if (diode) lines.push("d 128 352 128 224 2 default", "w 128 224 192 224 0");
  return lines.join("\n") + "\n";
}
function analogCircuit(p) {
  const lines = [H, ...SUPPLY, ...rail(96, [64, 192]), ...rail(352, [64, 192]), "r 192 224 192 352 0 250", "207 192 224 240 224 0 AI"];
  if (p.wire === 0) lines.push(`i 192 96 192 224 0 ${(4 + 16 * p.level / 100) / 1000}`);
  return lines.join("\n") + "\n";
}
WQ.lab({
  title: ["实验 3.3 PLC 输入输出的接线", "Lab 3.3 Wiring PLC inputs and outputs"],
  goal: ["在电路仿真里把传感器、电磁阀和液位计接到 PLC 上：看清电流从哪里来、流到哪里去；接错时为什么传感器亮了 PLC 却收不到；断开线圈时的电压尖峰和续流二极管的代价；4–20 mA 回路怎样发现断线。",
         "Wire a sensor, a solenoid valve and a level transmitter to a PLC in a circuit simulator: see where the current comes from and where it goes; why a wrongly wired sensor lights up yet the PLC sees nothing; the voltage spike when a coil is switched off and the price of a freewheeling diode; how a 4–20 mA loop reveals a broken wire."],
  view: "circuit",
  circuit: "",
  scenes: [
    { id: "input", name: ["传感器接数字量输入", "Sensor to a digital input"], hide: ["out", "supp", "level", "wire"],
      problem: { title: ["车间问题：换了一个传感器，PLC 收不到信号", "Shop-floor problem: a new sensor, and the PLC sees nothing"],
                 text: ["一条进口装配线的末端光电开关坏了（3.8 节），电工从库房拿了一个外形一样的换上：传感器上的指示灯会亮，PLC 的输入却一直是 0。",
                        "On an imported assembly line the end sensor failed (Section 3.8); the electrician fitted one that looks the same from the store: its lamp lights, yet the PLC input stays 0."] } },
    { id: "output", name: ["输出断开电磁阀线圈", "Switching off a valve coil"], hide: ["sensor", "common", "on", "level", "wire"],
      problem: { title: ["车间问题：继电器输出的触点烧黑了", "Shop-floor problem: the relay output's contact is burnt"],
                 text: ["一台设备的电磁阀由 PLC 的继电器输出控制，用了半年，输出触点就烧黑、接触不良。线圈断开的那一刻发生了什么？",
                        "A valve driven by a PLC relay output: after six months the contact is black and unreliable. What happens the instant the coil is switched off?"] } },
    { id: "analog", name: ["4–20 mA 液位计", "4–20 mA level transmitter"], hide: ["sensor", "common", "on", "out", "supp"],
      problem: { title: ["车间问题：水箱液位", "Shop-floor problem: a tank level"],
                 text: ["两线制液位计的量程 0–2000 mm，输出 4–20 mA，接到 PLC 模拟量输入的 250 Ω 电阻上。PLC 怎样把电流变成液位？电缆断了怎样发现？",
                        "A two-wire level transmitter, 0–2000 mm, 4–20 mA, into the PLC's 250 Ω analog input. How does the PLC turn current into level? How does it notice a cut cable?"] } },
  ],
  params: [
    { id: "sensor", name: ["传感器：0 = PNP，1 = NPN", "Sensor: 0 = PNP, 1 = NPN"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "common", name: ["输入公共端：0 = 接 M，1 = 接 L+", "Input common: 0 = to M, 1 = to L+"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "on", name: ["传感器：0 = 无料，1 = 有料（动作）", "Sensor: 0 = no part, 1 = part (on)"], min: 0, max: 1, step: 1, value: 1, digits: 0 },
    { id: "out", name: ["输出：0 = 刚断开，1 = 接通", "Output: 0 = just switched off, 1 = on"], min: 0, max: 1, step: 1, value: 1, digits: 0 },
    { id: "supp", name: ["吸收：0 = 没有，1 = 续流二极管", "Suppressor: 0 = none, 1 = freewheeling diode"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
    { id: "level", name: ["液位", "Level"], min: 0, max: 100, step: 1, value: 50, unit: "%", digits: 0 },
    { id: "wire", name: ["电缆：0 = 完好，1 = 断线", "Cable: 0 = intact, 1 = cut"], min: 0, max: 1, step: 1, value: 0, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重新开始", "Restart"] }],
  tasks: [
    { id: "pnp", text: ["PNP 传感器、公共端接 M、有料：输入电流 2 mA 以上，PLC 读到 1。", "PNP sensor, common to M, part present: input current above 2 mA, the PLC reads 1."],
      demo: { scene: "input", set: { sensor: 0, common: 0, on: 1 }, press: [], wait: 3 } },
    { id: "wrong", text: ["PNP 传感器、公共端接 L+、有料：传感器动作了，PLC 却读到 0。记下各点电压，解释原因。", "PNP sensor, common to L+, part present: the sensor is on, yet the PLC reads 0. Record the voltages and explain."],
      demo: { scene: "input", set: { sensor: 0, common: 1, on: 1 }, press: [], wait: 3 } },
    { id: "spike", text: ["没有吸收电路，线圈刚断开：触点断开处出现上百伏的电压。", "No suppressor, coil just switched off: hundreds of volts across the opening contact."],
      demo: { scene: "output", set: { out: 0, supp: 0 }, press: [], wait: 4 } },
    { id: "diode", text: ["加续流二极管再断开：电压不超过 1 V 左右，但线圈电流衰减变慢，记下降到 30 % 的时间。", "With a freewheeling diode: the voltage stays near 1 V, but the current decays slowly; record the time to 30 %."],
      demo: { scene: "output", set: { out: 0, supp: 1 }, press: [], wait: 14 } },
    { id: "loop", text: ["液位 50 %：回路电流 12 mA，输入电压 3 V，PLC 读到 13824。", "Level 50 %: 12 mA, 3 V across the input, the PLC reads 13824."],
      demo: { scene: "analog", set: { level: 50, wire: 0 }, press: [], wait: 3 } },
    { id: "cut", text: ["电缆断线：电流低于 3.6 mA，PLC 判为断线（而不是“水箱空了”）。", "Cut cable: below 3.6 mA, the PLC reports a broken wire (not an empty tank)."],
      demo: { scene: "analog", set: { level: 50, wire: 1 }, press: [], wait: 3 } },
  ],
  think: ["续流二极管保护了输出，却让线圈释放变慢。在只靠按钮互锁、或者靠程序里固定延时换向的正反转电路里（2.3 节），这会带来什么危险？", "A freewheeling diode protects the output but slows the release. In a reversing circuit that relies only on the button interlock, or on a fixed delay in the program (Section 2.3), what danger does that bring?"],

  text(api) {
    if (api.scene === "input") return inputCircuit(api.p);
    if (api.scene === "output") return outputCircuit(api.p);
    return analogCircuit(api.p);
  },
  setupCircuit(api) { this.restart(api); },
  reset(api) { this.restart(api); },
  restart(api) { api.load(this.text(api)); this.minV = 0; this.tRel = null; this.t0 = null; this.armed = false; },
  // the canvas under the circuit: what the PLC sees (a lamp for the digital input, a bar for the coil current or the loop current)
  draw(api) {
    const { w, h } = api, en = api.lang() === "en", x0 = 20, x1 = w - 20, y = h * 0.55;
    if (api.scene === "input") {
      const one = Math.abs((api.v("I0") - api.v("IR")) / 4700 * 1000) >= 2 && Math.abs(api.v("I0") - api.v("COM")) >= 11;
      api.label(en ? "PLC input I0.0" : "PLC 输入 I0.0", x0, h * 0.25, api.css("--muted"), 13);
      api.rect(x0, y - 14, 28, 28, one ? api.css("--green") : api.css("--soft"));
      api.label(one ? "1" : "0", x0 + 40, y + 6, api.css("--ink"), 18);
      return;
    }
    const full = api.scene === "output" ? 200 : 20, val = api.scene === "output" ? (api.v("Q0") - api.v("QL")) / 120 * 1000 : api.v("AI") / 250 * 1000;
    api.label(api.scene === "output" ? (en ? "coil current 0 … 200 mA" : "线圈电流 0 … 200 mA") : (en ? "loop current 0 … 20 mA" : "回路电流 0 … 20 mA"), x0, h * 0.25, api.css("--muted"), 13);
    api.rect(x0, y - 12, x1 - x0, 24, api.css("--soft"));
    api.rect(x0, y - 12, (x1 - x0) * Math.max(0, Math.min(1, (val || 0) / full)), 24, api.css("--accent"));
  },
  readouts(api) {
    const en = api.lang() === "en";
    if (api.scene === "input") {
      const v0 = api.v("I0"), vr = api.v("IR"), vc = api.v("COM"), q = api.v("Q");
      const i = (v0 - vr) / 4700 * 1000, u = Math.abs(v0 - vc), one = Math.abs(i) >= 2 && u >= 11;
      const p = api.p;
      if (one && p.sensor === 0 && p.common === 0 && p.on === 1) api.done("pnp");
      if (!one && p.sensor === 0 && p.common === 1 && p.on === 1 && q > 20) api.done("wrong");
      return [[["传感器输出 Q 的电压", "sensor output Q"], api.fmt(q, 1) + " V"], [["输入端子 I0.0 的电压", "input terminal I0.0"], api.fmt(v0, 1) + " V"],
              [["公共端的电压", "common"], api.fmt(vc, 1) + " V"],
              [["输入电流（流入端子为正）", "input current (into the terminal +)"], api.fmt(i, 2) + " mA"],
              [["PLC 读到", "the PLC reads"], one ? "1" : "0"]];
    }
    if (api.scene === "output") {
      const q0 = api.v("Q0"), ql = api.v("QL"), i = (q0 - ql) / 120 * 1000, t = api.simTime();
      if (!this.armed && i > 150) { this.armed = true; this.t0 = t; }   // the new circuit is running (the coil still carries its current)
      if (this.armed) this.minV = Math.min(this.minV, q0);
      if (this.armed && this.tRel === null && api.p.out === 0 && i <= 60) this.tRel = (t - this.t0) * 1000;
      if (api.p.out === 0 && api.p.supp === 0 && this.minV < -100) api.done("spike");
      if (api.p.out === 0 && api.p.supp === 1 && this.minV > -2 && this.tRel !== null && this.tRel > 2) api.done("diode");
      return [[["输出端 Q0 的电压", "output Q0"], api.fmt(q0, 1) + " V"], [["断开以来的最低电压", "lowest since switch-off"], api.fmt(this.minV, 0) + " V"],
              [["线圈电流", "coil current"], api.fmt(i, 0) + " mA"],
              [["降到 30 %（60 mA）用时", "time to 30 % (60 mA)"], this.tRel === null ? "—" : api.fmt(this.tRel, 1) + " ms"]];
    }
    const v = api.v("AI"), ma = v / 250 * 1000, raw = Math.round((ma - 4) / 16 * 27648), cut = ma < 3.6;
    if (api.p.wire === 0 && api.p.level === 50 && Math.abs(ma - 12) < 0.05) api.done("loop");
    if (api.p.wire === 1 && cut) api.done("cut");
    return [[["输入电阻上的电压", "voltage across 250 Ω"], api.fmt(v, 3) + " V"], [["回路电流", "loop current"], api.fmt(ma, 2) + " mA"],
            [["PLC 读到的数", "value read"], String(raw)], [["液位", "level"], cut ? (en ? "— (broken wire)" : "—（断线）") : api.fmt(raw / 27648 * 2000, 0) + " mm"]];
  },
});
