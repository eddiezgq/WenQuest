// 实验 3.2 时序预算（配 3.2 节）。触发器参数取自 params.json 的 ff_sim（SKY130 仿真，以 FO4 为单位），乘手算模型的 FO4 换算成秒；
// 加 1 电路的关键路径用 M3_2.incDelay(n)（以 τ 为单位，与书中程序 3.2.1 同一模型）。
// 场景 1：时钟频率可调；场景 2：时钟频率 = PWM 频率 × 2^n；场景 3：保持时间检查，可调时钟偏斜和插入的反相器对数。
const P32 = M3_2.P, Q32 = P32.problems.p32, FF32 = M3_2.ffTiming(), TAU32 = M3_2.tau();
const G32 = P32.Cd / P32.Cg, PAIR32 = 2 * (1 + G32) * TAU32;
const tl32 = (n) => M3_2.incDelay(n) * TAU32;
const f32 = (api) => (api.scene === "pwm" ? api.p.pwm * 1e3 * Math.pow(2, api.p.bits) : api.p.f * 1e6);
const su32 = (n, f) => M3_2.setupSlack(1 / f, tl32(n));
const ho32 = (skew, pairs) => M3_2.holdSlack(pairs * PAIR32, skew * 1e-12);

WQ.lab({
  title: ["实验 3.2 时序预算", "Lab 3.2 Timing budget"],
  goal: ["用建立时间约束求 PWM 计数器的最高时钟频率和可行位数；用保持时间约束检查时钟偏斜，插入反相器对修正违例。",
         "Use the setup constraint to find the PWM counter's maximum clock and feasible width; use the hold constraint to check clock skew and fix a violation with inverter pairs."],
  scenes: [
    { id: "setup", robot: true, name: ["计数器的最高频率", "Counter maximum frequency"], hide: ["pwm", "skew", "pairs"],
      problem: { title: ["机器人问题：PWM 计数器能跑多快", "Robot problem: how fast can the PWM counter run"],
                 text: ["16 位计数器每个周期加 1（行波进位）。时钟最高能到多少？",
                        "A 16-bit counter adds 1 every cycle (ripple carry). How fast can the clock go?"] } },
    { id: "pwm", robot: true, name: ["20 kHz PWM 的位数", "Bits at 20 kHz PWM"], hide: ["f", "skew", "pairs"],
      problem: { title: ["机器人问题：不让电机啸叫", "Robot problem: keep the motor quiet"],
                 text: ["PWM 要在 20 kHz 以上（人耳听不到），时钟 = PWM 频率 × 2ⁿ。最多能做几位？",
                        "The PWM must be above 20 kHz (inaudible); the clock is the PWM frequency × 2ⁿ. How many bits at most?"] } },
    { id: "hold", name: ["保持时间", "Hold check"], hide: ["bits", "f", "pwm"],
      problem: { title: ["编码器滤波器的移位寄存器", "The encoder filter's shift register"],
                 text: ["相邻两级之间没有逻辑。后一级的时钟晚到 δ（跨时钟树分支，再加门控单元）。要插几对反相器？",
                        "No logic between stages. The second stage's clock arrives δ later (across tree branches plus a gating cell). How many inverter pairs are needed?"] } },
  ],
  params: [
    { id: "bits", name: ["计数器位数 n", "Counter bits n"], min: 8, max: 16, step: 1, value: 16, unit: "", digits: 0 },
    { id: "f", name: ["时钟频率", "Clock frequency"], min: 50, max: 1500, step: 10, value: 100, unit: "MHz", digits: 0 },
    { id: "pwm", name: ["PWM 频率", "PWM frequency"], min: 10, max: 40, step: 1, value: 20, unit: "kHz", digits: 0 },
    { id: "skew", name: ["时钟偏斜 δ（接收端晚到为正）", "Clock skew δ (capture later = positive)"], min: -100, max: 400, step: 5, value: 0, unit: "ps", digits: 0 },
    { id: "pairs", name: ["插入的反相器对数", "Inverter pairs inserted"], min: 0, max: 4, step: 1, value: 0, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "fmax", robot: true, text: ["16 位：找到建立时间余量不为负的最高频率（再高 10 MHz 就违例）。", "16 bits: find the highest frequency with non-negative setup slack (10 MHz more violates)."],
      demo: { scene: "setup", set: { bits: 16, f: 560 }, press: [], wait: 1 } },
    { id: "bits", robot: true, text: ["PWM 20 kHz：找到余量不为负的最大位数（再加一位就违例）。", "PWM at 20 kHz: find the largest width with non-negative slack (one more bit violates)."],
      demo: { scene: "pwm", set: { pwm: 20, bits: 14 }, press: [], wait: 1 } },
    { id: "hold", text: ["偏斜设为 240 ps（算例 3.2.2）：插入最少的反相器对，使保持时间余量不为负。", "Set the skew to 240 ps (Example 3.2.2): insert the fewest inverter pairs that make the hold slack non-negative."],
      demo: { scene: "hold", set: { skew: 240, pairs: 1 }, press: [], wait: 1 } },
  ],
  think: ["为什么降低时钟频率能修正建立时间违例，却修正不了保持时间违例？插入的反相器对会不会让建立时间违例？",
          "Why does slowing the clock fix setup violations but not hold violations? Can the inserted inverter pairs cause a setup violation?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["tcq", "tcq"], color: "#7a8691" }, { name: ["组合逻辑 / 插入延时", "logic / inserted delay"], color: "#1d6fb8" }, { name: ["tsu、th + δ", "tsu, th + δ"], color: "#e67e22" }],
  reset(api, s) { check32(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p;
    if (api.scene === "hold") {
      const h = ho32(p.skew, p.pairs);
      return [[["tcq + 插入延时", "tcq + inserted delay"], f((FF32.tcq + p.pairs * PAIR32) * 1e12, 0) + " ps"],
              [["th + δ", "th + δ"], f((FF32.th + p.skew * 1e-12) * 1e12, 0) + " ps"],
              [["保持时间余量", "Hold slack"], f(h * 1e12, 0) + " ps " + (h >= 0 ? api.T("（满足）", "(met)") : api.T("（违例）", "(violated)"))],
              [["每对反相器", "Per inverter pair"], f(PAIR32 * 1e12, 1) + " ps"]];
    }
    const fr = f32(api), sl = su32(p.bits, fr);
    return [[["时钟频率 / 周期", "Clock / period"], f(fr / 1e6, 1) + " MHz / " + f(1e9 / fr, 3) + " ns"],
            [["加 1 电路延时", "Incrementer delay"], f(M3_2.incDelay(p.bits), 0) + " τ = " + f(tl32(p.bits) * 1e9, 3) + " ns"],
            [["tcq + 逻辑 + tsu", "tcq + logic + tsu"], f((FF32.tcq + tl32(p.bits) + FF32.tsu) * 1e9, 3) + " ns"],
            [["建立时间余量", "Setup slack"], f(sl * 1e12, 0) + " ps " + (sl >= 0 ? api.T("（满足）", "(met)") : api.T("（违例）", "(violated)"))],
            [["PWM 频率", "PWM frequency"], f(fr / Math.pow(2, p.bits) / 1e3, 2) + " kHz"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mu = css("--muted"), blue = "#1d6fb8", amber = "#e67e22", grey = "#7a8691", red = "#c0392b", green = "#2e7d32";
    const p = api.p, x0 = w * 0.08, x1 = w * 0.92;
    if (api.scene === "hold") {
      const a = FF32.tcq + p.pairs * PAIR32, b = FF32.th + p.skew * 1e-12, span = 600e-12, X = (t) => x0 + (t + 150e-12) / span * (x1 - x0);
      api.line(X(0), h * 0.12, X(0), h * 0.8, mu, 1, [4, 4]); api.label(api.T("时钟沿", "clock edge"), X(0), h * 0.1, mu, 11, "center");
      api.label(api.T("新数据最早到达", "new data earliest"), x0, h * 0.3, ink, 12, "left");
      api.rect(X(0), h * 0.34, X(FF32.tcq) - X(0), h * 0.1, grey);
      if (p.pairs) api.rect(X(FF32.tcq), h * 0.34, X(a) - X(FF32.tcq), h * 0.1, blue);
      api.label(api.T("旧数据须保持到", "old data must hold until"), x0, h * 0.56, ink, 12, "left");
      api.rect(Math.min(X(0), X(b)), h * 0.6, Math.abs(X(b) - X(0)), h * 0.1, amber);
      api.line(X(b), h * 0.3, X(b), h * 0.75, amber, 2);
      const ok = a >= b; api.label(ok ? api.T("满足", "met") : api.T("违例", "violated"), X(Math.max(a, b)) + 10, h * 0.5, ok ? green : red, 14, "left");
      return;
    }
    const fr = f32(api), T = 1 / fr, need = FF32.tcq + tl32(p.bits) + FF32.tsu, span = Math.max(T, need) * 1.1, X = (t) => x0 + t / span * (x1 - x0), y = h * 0.4, bh = h * 0.16;
    api.rect(X(0), y, X(FF32.tcq) - X(0), bh, grey);
    api.rect(X(FF32.tcq), y, X(FF32.tcq + tl32(p.bits)) - X(FF32.tcq), bh, blue);
    api.rect(X(FF32.tcq + tl32(p.bits)), y, X(need) - X(FF32.tcq + tl32(p.bits)), bh, amber);
    api.line(X(T), h * 0.2, X(T), h * 0.75, need <= T ? green : red, 2.5);
    api.label(api.T("下一个时钟沿", "next clock edge"), X(T), h * 0.17, need <= T ? green : red, 12, "center");
    api.line(X(0), h * 0.2, X(0), h * 0.75, mu, 1, [4, 4]);
    api.label("0", X(0), h * 0.8, mu, 11, "center"); api.label(api.fmt(span * 1e9, 2) + " ns", x1, h * 0.8, mu, 11, "right");
  },
});

function check32(api) {
  const p = api.p;
  if (api.scene === "setup" && p.bits === 16 && su32(16, p.f * 1e6) >= 0 && su32(16, (p.f + 10) * 1e6) < 0) api.done("fmax");
  if (api.scene === "pwm" && p.pwm === 20) {
    const f = (n) => 20e3 * Math.pow(2, n);
    if (su32(p.bits, f(p.bits)) >= 0 && (p.bits === 16 || su32(p.bits + 1, f(p.bits + 1)) < 0)) api.done("bits");
  }
  if (api.scene === "hold" && p.skew === 240 && ho32(240, p.pairs) >= 0 && (p.pairs === 0 || ho32(240, p.pairs - 1) < 0)) api.done("hold");
}
