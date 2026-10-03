// 数字集成电路设计 第 1 章 CMOS 反相器 · 双语课件（中英对照，R9）
// 结构沿用大学物理第 1 章：每节 机器人问题 → 概念 → 动画 → 虚拟实验 → 建模求解（含生活例子）。
// 数值一律由共享模型计算（labs/micro/kit/models，第 17 轮 RM2）。运行：node build_ch1_deck_bi.js
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const HERE = __dirname;
const ROOT = path.resolve(HERE, "../../..");
const P = JSON.parse(fs.readFileSync(path.join(ROOT, "labs/micro/kit/models/params.json"), "utf8"));
const M = require(path.join(ROOT, "labs/micro/kit/models/mos.js")).create(P);
const R = M.reference();
const r = R.r;

const NAVY = "1E2761", ICE = "EEF3FA", AMBER = "F2B705", INK = "1F2D3A", MUTED = "5B6B75", WHITE = "FFFFFF", NIGHT = "0F1419", PALE = "FFF6DA";
const CN = "Microsoft YaHei", EN = "Calibri";
const CH = path.join(HERE, "../课程资料/第1章 CMOS反相器");
const VID = path.join(CH, "动画");
const MEDIA = path.join(HERE, "fig/media");
const LAB = "虚拟实验/第1章虚拟实验（中英）.html";
const OUT = path.join(CH, "第一章课件.pptx");
const b64 = (f) => "data:image/png;base64," + fs.readFileSync(f).toString("base64");
const T = (o) => Object.assign({ isTextBox: true, margin: 0 }, o);
const f2 = (x, d = 2) => x.toFixed(d);

function biList(items, zhSize = 16, enSize = 11, color = INK, enColor = MUTED, numbered = false) {
  const runs = [];
  items.forEach(([zh, en], i) => {
    runs.push({ text: zh, options: { bullet: numbered ? { type: "number" } : true, fontFace: CN, fontSize: zhSize, color, breakLine: true } });
    runs.push({ text: en, options: { fontFace: EN, fontSize: enSize, color: enColor, indentLevel: 0, paraSpaceAfter: 9, breakLine: i < items.length - 1, bullet: false } });
  });
  return runs;
}
function biTitle(s, zh, en, y = 0.62, color = INK, enColor = MUTED) {
  s.addText(zh, T({ x: 0.7, y, w: 12, h: 0.6, fontFace: CN, fontSize: 26, color, bold: true }));
  s.addText(en, T({ x: 0.7, y: y + 0.6, w: 12, h: 0.35, fontFace: EN, fontSize: 14, color: enColor }));
}
function tag(s, text, color = AMBER) { s.addText(text, T({ x: 0.7, y: 0.3, w: 8, h: 0.3, fontFace: CN, fontSize: 12, color, bold: true })); }

// ---------- 由模型算出的数值 ----------
const W11 = R.p11.Wn;
const vol2 = (() => { let lo = 0, hi = P.VDD - P.VTn; for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; if (M.idn(P.VDD, m, W11) > 2e-3) hi = m; else lo = m; } return (lo + hi) / 2; })();
const N1 = R.p12.ratio1, NR = R.p12.ratio_r;
const T1 = R.p13.ratio1, TS = R.p13.ratio_sqrt, TR = R.p13.ratio_r;
const C14 = R.p14, f6 = Math.pow(C14.F, 1 / 6);
const P15 = R.p15;
const ps = (x) => (x * 1e12).toFixed(0);
let vLim = 1.8; for (let v = 1.8; v >= 0.9; v -= 0.01) { const d = M.fo4(P.Wmin, r * P.Wmin, v); if ((d.tphl + d.tplh) / 2 <= 100e-12) vLim = v; }

const L = [
  {
    no: "1.1", zh: "MOSFET 开关与 CMOS 反相器", en: "MOSFET switches and the CMOS inverter", video: "SwitchPath", lab: "1",
    prob: { zh: "关节驱动板的光耦输入", en: "Optocoupler input on a joint driver",
      text: ["关节驱动板用光耦隔离控制芯片与功率电路。芯片输出管脚要吸收 1 mA 点亮光耦，低电平不能超过 0.2 V。输出级的 NMOS 至少要多宽？",
             "The joint driver isolates the control chip from the power stage with an optocoupler. The output pin must sink 1 mA with a low level of at most 0.2 V. How wide must the output NMOS be?"],
      given: [["负载电流 I = 1 mA", "load current I = 1 mA"], ["VOL ≤ 0.2 V，VDD = 1.8 V", "VOL ≤ 0.2 V, VDD = 1.8 V"], ["L = 0.15 μm，k′n = 90 μA/V²（示意值）", "L = 0.15 μm, k′n = 90 μA/V² (illustrative)"]] },
    concept: { zh: "开关模型与互补结构", en: "Switch model and complementary structure",
      pts: [["MOSFET 是电压控制的开关：VGS > VT 导通，VGS < VT 截止", "A MOSFET is a voltage-controlled switch: on for VGS > VT, off below"],
            ["CMOS 反相器：PMOS 上拉、NMOS 下拉，栅极接在一起", "CMOS inverter: PMOS pull-up, NMOS pull-down, gates tied together"],
            ["稳态时总有一个管子截止：没有静态直流通路", "One transistor is always off in steady state: no static DC path"],
            ["导通的管子工作在线性区，相当于电阻 Ron", "The on transistor sits in the linear region and acts as a resistor Ron"]],
      formula: "线性区 ID = k′n(W/L)[(VGS−VT)VDS − VDS²/2]\nRon ≈ 1 / [k′n(W/L)(VDD − VT)]" },
    vq: ["输入从 0 变到 1，电流走哪条路？稳态时还有电流吗？", "When the input goes from 0 to 1, where does the current flow? Is there any current in steady state?"],
    tasks: [["切换输入高低，观察哪个管子导通", "Toggle the input and see which transistor conducts"], ["光耦 1 mA：找出 VOL ≤ 0.2 V 的最小 Wn", "Optocoupler 1 mA: find the smallest Wn with VOL ≤ 0.2 V"], ["负载加到 2 mA，VOL 正好翻倍吗？", "At 2 mA, does VOL exactly double?"]],
    model: [["建模", "Model", "输入为高，NMOS 栅压 1.8 V，工作在线性区；平方律模型，忽略沟道长度调制", "Input high, NMOS gate at 1.8 V in the linear region; square law, no channel-length modulation"],
            ["求解", "Solve", `W ≥ I·L / {k′n[(VDD−VT)VOL − VOL²/2]} = ${f2(W11)} μm（W/L ≈ ${R.p11.WnL.toFixed(0)}）；2 mA 时 VOL ≈ ${f2(vol2)} V，不止翻倍`, `W ≥ I·L / {k′n[(VDD−VT)VOL − VOL²/2]} = ${f2(W11)} μm (W/L ≈ ${R.p11.WnL.toFixed(0)}); at 2 mA VOL ≈ ${f2(vol2)} V, more than double`],
            ["检验", "Check", "虚拟实验 1.1：负载 1 mA，调 Wn 读 VOL；负载线与输出特性的交点", "Lab 1.1: load 1 mA, adjust Wn and read VOL where the load line meets the curve"],
            ["修正", "Improve", "实际要按 SKY130 模型和温度、工艺角留余量；电流更大时改用专门的输出驱动或外接三极管", "Use SKY130 models with margin for temperature and corners; for larger currents use a dedicated driver or an external transistor"]],
    everyday: ["楼梯间双控开关：两个开关互补，灯只有亮、灭两种状态", "Two-way stair switches are complementary: the light is either on or off"],
  },
  {
    no: "1.2", zh: "电压传输特性与噪声容限", en: "Voltage transfer characteristic and noise margins", video: "VtcSweep", lab: "2",
    prob: { zh: "编码器信号的抗干扰", en: "Noise immunity of an encoder signal",
      text: ["关节编码器的信号经 2 m 电缆进入控制芯片，电机工作时叠加约 ±0.3 V 干扰。接收端的反相器会不会误翻转？",
             "The joint encoder signal travels 2 m of cable into the control chip and picks up about ±0.3 V of motor noise. Will the receiving inverter switch falsely?"],
      given: [["干扰幅度 ±0.3 V", "noise ±0.3 V"], ["VDD = 1.8 V，|VT| = 0.45 V", "VDD = 1.8 V, |VT| = 0.45 V"], [`迁移率比 r = k′n/k′p = ${f2(r)}`, `mobility ratio r = k′n/k′p = ${f2(r)}`]] },
    concept: { zh: "传输特性：阈值与噪声容限", en: "Transfer curve: threshold and noise margins",
      pts: [["两管电流相等决定输出电压，逐点画出 Vout(Vin)", "Equal currents set Vout; plot Vout(Vin) point by point"],
            ["两管都饱和处曲线最陡：开关阈值 VM", "The curve is steepest where both saturate: the threshold VM"],
            ["斜率为 −1 的两点定出 VIL、VIH", "The two slope = −1 points define VIL and VIH"],
            ["NML = VIL − VOL，NMH = VOH − VIH", "NML = VIL − VOL, NMH = VOH − VIH"]],
      formula: "VM = [VTn + r′(VDD − |VTp|)] / (1 + r′)\nr′ = √(k′pWp / k′nWn)" },
    vq: ["输入慢慢增大，两个管子的工作区怎样变化？曲线为什么在中间几乎竖直？", "As the input rises, how do the two transistors change region? Why is the curve almost vertical in the middle?"],
    tasks: [["调尺寸比使 VM = 0.90 V", "Adjust the ratio until VM = 0.90 V"], ["尺寸比 1：读出 NML", "Ratio 1: read NML"], ["干扰 0.30 V：两个容限都 ≥ 0.6 V", "Noise 0.30 V: both margins ≥ 0.6 V"]],
    model: [["建模", "Model", "接收端为最小反相器；干扰叠加在输入电平上；容限至少为干扰的 2 倍", "The receiver is a minimum inverter; noise adds to the input level; margins should be at least twice the noise"],
            ["求解", "Solve", `Wp/Wn = 1：VM ≈ ${f2(N1.VM)} V，NML ≈ ${f2(N1.NML)}、NMH ≈ ${f2(N1.NMH)} V；Wp/Wn = ${f2(r)}：VM = 0.90 V，NML = NMH ≈ ${f2(NR.NML)} V`, `Wp/Wn = 1: VM ≈ ${f2(N1.VM)} V, NML ≈ ${f2(N1.NML)}, NMH ≈ ${f2(N1.NMH)} V; Wp/Wn = ${f2(r)}: VM = 0.90 V, NML = NMH ≈ ${f2(NR.NML)} V`],
            ["检验", "Check", "虚拟实验 1.2：干扰幅度设为 0.30 V，比较不同尺寸比下的两个容限", "Lab 1.2: set the noise to 0.30 V and compare both margins for different ratios"],
            ["修正", "Improve", "干扰更大时用施密特触发器（有回差）或差分信号（如 RS-422 编码器接口）", "For larger noise use a Schmitt trigger (hysteresis) or differential signalling (e.g. an RS-422 encoder interface)"]],
    everyday: ["声控楼道灯的阈值：太低会被杂音触发，太高叫不亮", "A sound-activated stair light: too low a threshold triggers on noise, too high won’t respond"],
  },
  {
    no: "1.3", zh: "尺寸与对称", en: "Sizing and symmetry", video: "Sizing", lab: "3",
    prob: { zh: "电机控制芯片的时钟缓冲", en: "The clock buffer of a motor-control chip",
      text: ["电机控制芯片的时钟经缓冲器分发到 PWM 计数器。缓冲器上升、下降延时不同，时钟占空比就会走样。尺寸比怎样取才能让两种延时接近？",
             "The motor-control chip distributes its clock through buffers to the PWM counter. Unequal rise and fall delays distort the duty cycle. Which size ratio matches them?"],
      given: [["负载：4 个相同反相器（FO4）", "load: four identical inverters (FO4)"], ["Wn = 0.42 μm（最小）", "Wn = 0.42 μm (minimum)"], ["Req ≈ ¾·VDD/IDSAT", "Req ≈ ¾·VDD/IDSAT"]] },
    concept: { zh: "RC 延时与对称尺寸", en: "RC delay and symmetric sizing",
      pts: [["导通管看成等效电阻 Req，负载看成电容 CL", "Treat the on transistor as Req and the load as CL"],
            ["tPHL = 0.69·Req,n·CL，tPLH = 0.69·Req,p·CL", "tPHL = 0.69·Req,n·CL, tPLH = 0.69·Req,p·CL"],
            [`PMOS 迁移率低：同尺寸时 Req,p ≈ ${f2(r)} × Req,n`, `Lower PMOS mobility: at equal size Req,p ≈ ${f2(r)} × Req,n`],
            ["Wp/Wn = r：上升下降相等；Wp/Wn ≈ √r：平均延时最小", "Wp/Wn = r equalises edges; Wp/Wn ≈ √r minimises average delay"]],
      formula: "tp = (tPHL + tPLH) / 2 = 0.69 · CL · (Req,n + Req,p) / 2" },
    vq: ["加宽 PMOS 以后，传输特性和输出波形各发生了什么变化？", "After widening the PMOS, what changes in the transfer curve and the output waveform?"],
    tasks: [["FO4：使上升下降相差 ≤ 5%", "FO4: make rise and fall differ by ≤ 5%"], ["FO4：找出平均延时最小的尺寸比", "FO4: find the ratio with the smallest average delay"], ["Wp/Wn = 1 时延时差多少？", "How large is the mismatch at Wp/Wn = 1?"]],
    model: [["建模", "Model", "一阶 RC 模型；负载 = 4 × 输入电容 + 自载；忽略输入边沿斜率", "First-order RC model; load = 4 × input capacitance + self-load; input slope ignored"],
            ["求解", "Solve", `Wp/Wn = 1：tPHL ≈ ${ps(T1.tphl)}、tPLH ≈ ${ps(T1.tplh)} ps（差 ${(T1.mismatch * 100).toFixed(0)}%）；Wp/Wn = ${f2(r)}：两者 ≈ ${ps(TR.tp)} ps；Wp/Wn ≈ ${f2(Math.sqrt(r))}：tp ≈ ${ps(TS.tp)} ps 最小`, `Wp/Wn = 1: tPHL ≈ ${ps(T1.tphl)}, tPLH ≈ ${ps(T1.tplh)} ps (${(T1.mismatch * 100).toFixed(0)}% apart); Wp/Wn = ${f2(r)}: both ≈ ${ps(TR.tp)} ps; Wp/Wn ≈ ${f2(Math.sqrt(r))}: smallest tp ≈ ${ps(TS.tp)} ps`],
            ["检验", "Check", "虚拟实验 1.3：FO4 下扫描尺寸比，读波形和下方延时曲线", "Lab 1.3: sweep the ratio at FO4, read the waveform and the delay plot"],
            ["修正", "Improve", "时钟缓冲选对称尺寸；普通逻辑取 √r 附近省面积；实际还要考虑输入斜率和工艺角", "Use symmetric sizing for clock buffers and about √r for ordinary logic; real designs also account for input slope and corners"]],
    everyday: ["跷跷板两边体重不同，要挪支点才能平衡", "On a seesaw with unequal weights, move the pivot to balance it"],
  },
  {
    no: "1.4", zh: "传播延时与反相器链", en: "Propagation delay and the inverter chain", video: "Chain", lab: "4",
    prob: { zh: "驱动板上的栅极驱动器", en: "Driving the gate driver on the board",
      text: ["芯片的 PWM 输出要经焊盘、走线驱动电路板上的栅极驱动器输入，总负载约 10 pF。最小反相器直接驱动要几十纳秒，PWM 边沿被拖慢。插几级缓冲最快？",
             "The chip’s PWM output drives pad, trace and gate-driver input, about 10 pF in all. A minimum inverter takes tens of nanoseconds, smearing the PWM edges. How many buffer stages are fastest?"],
      given: [["负载 CL = 10 pF", "load CL = 10 pF"], [`第一级输入电容 Cin ≈ ${f2(C14.Cin * 1e15)} fF`, `first-stage Cin ≈ ${f2(C14.Cin * 1e15)} fF`], ["边沿延时要求 < 0.3 ns", "edge delay must be < 0.3 ns"]] },
    concept: { zh: "反相器链：逐级放大", en: "Inverter chain: grow stage by stage",
      pts: [["总扇出 F = CL / Cin，N 级等比链每级扇出 f = F^(1/N)", "Total fan-out F = CL / Cin; each of N stages has f = F^(1/N)"],
            ["总延时 t = N · tp0 · (γ + f)，γ 为自载与输入电容之比", "Total delay t = N · tp0 · (γ + f), γ = self-load / input capacitance"],
            ["最优每级扇出约 4（不计自载时为 e ≈ 2.7）", "Optimum fan-out about 4 per stage (e ≈ 2.7 without self-load)"],
            ["级数奇偶决定输出是否反相", "An odd or even number of stages decides whether the output is inverted"]],
      formula: "N ≈ ln F / ln 4        f = F^(1/N)" },
    vq: ["一级驱动和六级驱动，延时为什么能差一百多倍？", "Why can one stage and six stages differ in delay by more than a hundred times?"],
    tasks: [["CL = 10 pF：找出延时最小的级数", "CL = 10 pF: find the number of stages with the smallest delay"], ["6 级时每级扇出 f 是多少？", "What is f with 6 stages?"], ["延时 < 0.3 ns 的最少级数", "Fewest stages for a delay under 0.3 ns"]],
    model: [["建模", "Model", "等比反相器链，第一级为最小对称反相器；负载集中为 10 pF；每级 RC 模型", "Tapered chain starting from a minimum symmetric inverter; 10 pF lumped load; RC model per stage"],
            ["求解", "Solve", `F ≈ ${C14.F.toFixed(0)}，ln F / ln 4 ≈ ${f2(C14.Nopt4)}；单级 ≈ ${(C14.t[1] * 1e9).toFixed(0)} ns；6 级 f ≈ ${f6.toFixed(1)}、t ≈ ${ps(C14.t[6])} ps；5 级 ≈ ${ps(C14.t[5])} ps 即满足 < 0.3 ns`, `F ≈ ${C14.F.toFixed(0)}, ln F / ln 4 ≈ ${f2(C14.Nopt4)}; one stage ≈ ${(C14.t[1] * 1e9).toFixed(0)} ns; 6 stages f ≈ ${f6.toFixed(1)}, t ≈ ${ps(C14.t[6])} ps; 5 stages ≈ ${ps(C14.t[5])} ps already meets < 0.3 ns`],
            ["检验", "Check", "虚拟实验 1.4：CL = 10 pF，级数 1–10 扫描，对照 0.3 ns 线", "Lab 1.4: CL = 10 pF, sweep 1–10 stages against the 0.3 ns line"],
            ["修正", "Improve", "最优附近曲线很平：可少用一级省面积和功耗；要同相输出取偶数级；焊盘和走线电感还会带来振铃", "The optimum is flat: drop a stage to save area and power; use an even count for a non-inverted output; pad and trace inductance add ringing"]],
    everyday: ["搬重物接力：一人搬太慢，分几段逐级加人更快，但人太多交接也费时", "Relay carrying: one person is slow, adding people stage by stage is faster, but too many hand-offs waste time"],
  },
  {
    no: "1.5", zh: "功耗", en: "Power", video: "Power", lab: "5",
    prob: { zh: "巡线小车控制芯片的功耗预算", en: "Power budget of a line-following car controller",
      text: ["巡线小车的控制芯片约 1 万个门，平均每个时钟有 10% 的门翻转，时钟 100 MHz。动态功耗多大？把电压从 1.8 V 降到 1.2 V 能省多少，又要付出什么代价？",
             "The line-following car’s controller has about 10 000 gates, 10% switching each cycle at 100 MHz. What is the dynamic power? How much does dropping from 1.8 V to 1.2 V save, and at what cost?"],
      given: [["门数 N = 10 000，翻转率 α = 0.1", "N = 10 000 gates, activity α = 0.1"], ["时钟 f = 100 MHz", "clock f = 100 MHz"], ["每门负载 C = 5 fF", "load per gate C = 5 fF"]] },
    concept: { zh: "动态功耗：每次翻转的能量", en: "Dynamic power: the energy per transition",
      pts: [["0→1：电源送出 CV²，一半存进电容，一半在 PMOS 上变成热", "0→1: the supply delivers CV², half stored, half burnt in the PMOS"],
            ["1→0：电容里的 ½CV² 在 NMOS 上变成热", "1→0: the stored ½CV² is burnt in the NMOS"],
            ["动态功耗与电压平方成正比", "Dynamic power scales with the square of the supply"],
            ["降压使电流变小、门变慢：tp ∝ VDD / (VDD − VT)²", "Lower supply means less current and slower gates: tp ∝ VDD / (VDD − VT)²"]],
      formula: "P = α · C · VDD² · f · N" },
    vq: ["电容充一次电、放一次电，电源一共送出多少能量？都去哪里了？", "One charge and one discharge: how much energy does the supply deliver, and where does it go?"],
    tasks: [["读出默认设置下的动态功耗", "Read the dynamic power at the default settings"], ["电压降到 1.20 V，功耗降多少？", "Lower the supply to 1.20 V: how much is saved?"], ["FO4 ≤ 100 ps 的最低电压", "Lowest supply with FO4 ≤ 100 ps"]],
    model: [["建模", "Model", "只计动态功耗，不计漏电与短路电流；所有门负载相同；翻转率取平均值", "Dynamic power only, no leakage or short-circuit current; identical gate loads; average activity"],
            ["求解", "Solve", `P = 0.1 × 5 fF × 1.8² × 100 MHz × 10⁴ = ${(P15.P_VDD * 1e3).toFixed(2)} mW；1.2 V 时 ${(P15.P_low * 1e3).toFixed(2)} mW（降 56%）；FO4 ≤ 100 ps 要求 VDD ≥ ${vLim.toFixed(2)} V`, `P = 0.1 × 5 fF × 1.8² × 100 MHz × 10⁴ = ${(P15.P_VDD * 1e3).toFixed(2)} mW; at 1.2 V ${(P15.P_low * 1e3).toFixed(2)} mW (56% less); FO4 ≤ 100 ps needs VDD ≥ ${vLim.toFixed(2)} V`],
            ["检验", "Check", "虚拟实验 1.5：改电压、频率、翻转率，对照功耗曲线和 FO4 延时曲线", "Lab 1.5: vary supply, clock and activity against the power and FO4 delay plots"],
            ["修正", "Improve", "低电压、高温时漏电不能忽略；小车上电机耗电远大于芯片，芯片省电主要延长待机和传感器节点的电池寿命", "Leakage matters at low voltage and high temperature; on the car the motors dominate, so chip savings mainly extend standby and sensor-node battery life"]],
    everyday: ["手机省电模式：降频、降压，代价是变慢", "Phone power-saving mode lowers clock and voltage, at the cost of speed"],
  },
];

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "第1章 CMOS反相器 Chapter 1 The CMOS Inverter";

// ---- 封面
let s = pres.addSlide();
s.background = { color: NAVY };
s.addText("第 1 章  Chapter 1", T({ x: 0.8, y: 1.4, w: 8, h: 0.5, fontFace: CN, fontSize: 20, color: AMBER, bold: true }));
s.addText("CMOS 反相器", T({ x: 0.8, y: 2.0, w: 11.5, h: 1.1, fontFace: CN, fontSize: 44, color: WHITE, bold: true }));
s.addText("The CMOS Inverter", T({ x: 0.8, y: 3.05, w: 11.5, h: 0.6, fontFace: EN, fontSize: 26, color: "CADCFC" }));
s.addText([{ text: "从一个晶体管开关出发，理解数字芯片的电平、速度与功耗", options: { breakLine: true } },
           { text: "From one transistor switch to the levels, speed and power of digital chips", options: { fontFace: EN, fontSize: 14, color: "9FB3D1" } }],
  T({ x: 0.8, y: 4.0, w: 11.5, h: 0.9, fontFace: CN, fontSize: 17, color: "E6EDF7" }));
s.addText("数字集成电路设计 Digital Integrated Circuit Design  ·  问渠 WenQuest", T({ x: 0.8, y: 6.5, w: 10, h: 0.4, fontFace: CN, fontSize: 12, color: "9FB3D1" }));
s.addNotes("开场问题：机器人关节里的电机控制芯片，最基本的单元是什么？它的电平、速度、功耗由什么决定？\nOpening question: what is the most basic cell in a robot joint’s motor-control chip, and what sets its levels, speed and power?");

// ---- 本章内容
s = pres.addSlide();
s.background = { color: WHITE };
biTitle(s, "本章内容与每节课的结构", "Chapter map and how each lesson works", 0.45);
L.forEach((l, i) => {
  const y = 1.75 + i * 0.95;
  s.addShape(pres.shapes.OVAL, { x: 0.8, y, w: 0.62, h: 0.62, fill: { color: NAVY } });
  s.addText(l.no, T({ x: 0.8, y, w: 0.62, h: 0.62, fontFace: CN, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle" }));
  s.addText([{ text: l.zh, options: { breakLine: true } }, { text: l.en, options: { fontFace: EN, fontSize: 11, color: MUTED, bold: false } }],
    T({ x: 1.6, y: y - 0.04, w: 4.8, h: 0.72, fontFace: CN, fontSize: 16, bold: true, color: INK, valign: "middle" }));
  s.addText([{ text: "机器人问题：" + l.prob.zh, options: { breakLine: true } }, { text: "Robot: " + l.prob.en, options: { fontFace: EN, fontSize: 10, color: MUTED } }],
    T({ x: 6.5, y: y - 0.04, w: 6.2, h: 0.72, fontFace: CN, fontSize: 13, color: INK, valign: "middle" }));
});
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.8, y: 6.55, w: 11.9, h: 0.6, fill: { color: ICE }, line: { color: ICE }, rectRadius: 0.1 });
s.addText("每节课：实际问题 → 概念 → 动画 → 虚拟实验 → 建模求解    Each lesson: problem → concept → animation → virtual lab → modelling",
  T({ x: 1.0, y: 6.55, w: 11.5, h: 0.6, fontFace: CN, fontSize: 13, color: NAVY, bold: true, valign: "middle" }));
s.addNotes("芯片设计同样靠模型：先用简单模型估算，再用仿真和工艺库校准。本章每节从一个机器人问题出发，最后回到这个问题。\nChip design also runs on models: estimate with a simple model, then calibrate with simulation and the process library. Each lesson starts from a robot problem and returns to it.");

L.forEach((l) => {
  // A. 机器人问题
  let sl = pres.addSlide();
  sl.background = { color: PALE };
  tag(sl, `${l.no}  机器人问题  Robot problem`);
  biTitle(sl, l.prob.zh, l.prob.en);
  sl.addText([{ text: l.prob.text[0], options: { breakLine: true, paraSpaceAfter: 8 } }, { text: l.prob.text[1], options: { fontFace: EN, fontSize: 12, color: MUTED } }],
    T({ x: 0.7, y: 1.8, w: 5.6, h: 2.5, fontFace: CN, fontSize: 16, color: INK, valign: "top" }));
  sl.addText("已知  Given", T({ x: 0.7, y: 4.4, w: 5, h: 0.35, fontFace: CN, fontSize: 13, color: MUTED, bold: true }));
  sl.addText(biList(l.prob.given, 14, 10.5), T({ x: 0.7, y: 4.8, w: 5.6, h: 2.3, fontFace: CN, valign: "top" }));
  const iw = 6.3, ih = iw * 10 / 16;
  sl.addImage({ path: path.join(MEDIA, `robot_${l.lab}.png`), x: 6.6, y: 1.8, w: iw, h: ih });
  sl.addShape(pres.shapes.RECTANGLE, { x: 6.6, y: 1.8, w: iw, h: ih, fill: { type: "none" }, line: { color: "D9CFA8", width: 1 } });
  sl.addText("本节结束时，我们用建立的模型回答这个问题。  We will answer it with this lesson’s model at the end.",
    T({ x: 6.6, y: 1.8 + ih + 0.15, w: iw, h: 0.6, fontFace: CN, fontSize: 11, color: MUTED }));
  sl.addNotes("先让学生估一估、讨论 2 分钟，不急于给答案。本节最后回到这一页。\nLet students estimate and discuss for two minutes; return to this problem at the end.");

  // B. 概念
  const c = l.concept;
  sl = pres.addSlide();
  sl.background = { color: WHITE };
  tag(sl, `${l.no}  概念  Concept`);
  biTitle(sl, c.zh, c.en);
  sl.addText(biList(c.pts), T({ x: 0.7, y: 1.8, w: 11.9, h: 3.3, fontFace: CN, valign: "top" }));
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 5.35, w: 11.9, h: 1.4, fill: { color: ICE }, line: { color: ICE }, rectRadius: 0.12 });
  sl.addText(c.formula, T({ x: 1.0, y: 5.4, w: 11.4, h: 1.3, fontFace: "Cambria Math", fontSize: 18, color: NAVY, bold: true, valign: "middle" }));
  sl.addNotes("讲清公式中每个量的意义和模型的适用条件，再进入动画。\nExplain each quantity and the model’s conditions before the animation.");

  // C. 动画
  sl = pres.addSlide();
  sl.background = { color: NIGHT };
  tag(sl, `${l.no}  动画  Animation`);
  sl.addText([{ text: l.vq[0], options: { breakLine: true } }, { text: l.vq[1], options: { fontFace: EN, fontSize: 13, color: "9FB3D1", bold: false } }],
    T({ x: 0.7, y: 0.6, w: 12, h: 0.85, fontFace: CN, fontSize: 19, color: WHITE, bold: true }));
  const vw = 9.3, vh = vw * 9 / 16, vx = (13.333 - vw) / 2, vy = 1.6;
  sl.addMedia({ type: "video", path: path.join(VID, `${l.no}_${l.video}.mp4`), x: vx, y: vy, w: vw, h: vh, cover: b64(path.join(MEDIA, "poster_" + l.video + ".png")) });
  sl.addText("点击画面播放 · 中英字幕 · Click to play · bilingual captions", T({ x: vx, y: vy + vh + 0.08, w: vw, h: 0.3, fontFace: CN, fontSize: 11, color: "9FB3D1", align: "center" }));
  sl.addNotes("播放动画，在关键画面暂停提问。\nPlay the clip and pause at the key frame to ask the question on the slide.");

  // D. 虚拟实验
  sl = pres.addSlide();
  sl.background = { color: ICE };
  tag(sl, `${l.no}  虚拟实验  Virtual lab`);
  biTitle(sl, "动手试一试：" + l.zh, "Try it: " + l.en);
  const iw2 = 7.3, ih2 = iw2 * 725 / 1160, url = LAB;
  sl.addImage({ path: path.join(MEDIA, "lab_" + l.lab + ".png"), x: 0.7, y: 1.8, w: iw2, h: ih2, hyperlink: { url, tooltip: "打开虚拟实验 Open the virtual lab" } });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 1.8, w: iw2, h: ih2, fill: { type: "none" }, line: { color: "C9D3DD", width: 1 } });
  sl.addText("任务  Tasks", T({ x: 8.4, y: 1.8, w: 4.3, h: 0.35, fontFace: CN, fontSize: 14, color: MUTED, bold: true }));
  sl.addText(biList(l.tasks, 14, 10.5, INK, MUTED, true), T({ x: 8.4, y: 2.2, w: 4.3, h: 3.0, fontFace: CN, valign: "top" }));
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.4, y: 5.35, w: 4.3, h: 0.65, fill: { color: NAVY }, line: { color: NAVY }, rectRadius: 0.1, hyperlink: { url, tooltip: "打开虚拟实验" } });
  sl.addText([{ text: "打开虚拟实验  Open lab ▶", options: { hyperlink: { url } } }], T({ x: 8.4, y: 5.35, w: 4.3, h: 0.65, fontFace: CN, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle" }));
  sl.addText(`实验台中选“${l.no}”选项卡 · 课后按实验指导书完成实验报告\nChoose tab ${l.no} · write the lab report using the lab guide`, T({ x: 8.4, y: 6.1, w: 4.3, h: 0.6, fontFace: CN, fontSize: 11, color: MUTED, align: "center" }));
  sl.addNotes("课堂投屏演示机器人任务，其余任务课后完成，并按实验指导书写实验报告。\nDemonstrate the robot task in class; students finish the rest and the lab report after class.");

  // E. 回到实际问题：五步建模
  sl = pres.addSlide();
  sl.background = { color: WHITE };
  tag(sl, `${l.no}  回到实际问题  Back to the problem`);
  biTitle(sl, "建模求解：" + l.prob.zh, "Modelling: " + l.prob.en);
  const rows = [[
    { text: "步骤 Step", options: { bold: true, fill: { color: ICE }, color: INK } },
    { text: "内容 What we do", options: { bold: true, fill: { color: ICE }, color: INK } },
  ]];
  rows.push([{ text: "① 问题\nProblem", options: { bold: true } }, { text: [{ text: l.prob.text[0], options: { breakLine: true } }, { text: l.prob.text[1], options: { fontFace: EN, fontSize: 10, color: MUTED } }] }]);
  l.model.forEach(([zh, en, a, b], i) => {
    rows.push([{ text: `${"②③④⑤"[i]} ${zh}\n${en}`, options: { bold: true } }, { text: [{ text: a, options: { breakLine: true } }, { text: b, options: { fontFace: EN, fontSize: 10, color: MUTED } }] }]);
  });
  sl.addTable(rows, { x: 0.7, y: 1.75, w: 8.4, colW: [1.35, 7.05], fontFace: CN, fontSize: 12.5, color: INK, border: { type: "solid", pt: 0.75, color: "D5DEE8" }, valign: "middle", margin: 0.05 });
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.4, y: 1.75, w: 3.3, h: 3.6, fill: { color: PALE }, line: { color: PALE }, rectRadius: 0.12 });
  sl.addText([{ text: "生活中的例子", options: { bold: true, breakLine: true } }, { text: "Everyday example", options: { fontFace: EN, fontSize: 11, color: MUTED, breakLine: true } },
              { text: l.everyday[0], options: { fontSize: 13, breakLine: true, paraSpaceBefore: 8 } }, { text: l.everyday[1], options: { fontFace: EN, fontSize: 10, color: MUTED } }],
    T({ x: 9.6, y: 1.9, w: 2.9, h: 3.3, fontFace: CN, fontSize: 15, color: INK, valign: "top" }));
  sl.addText("芯片设计也靠模型：先用简单模型估算，再用仿真和工艺库校准，最后指出模型的局限。\nChip design runs on models: estimate simply, calibrate with simulation and the process library, then name the limits.",
    T({ x: 9.4, y: 5.5, w: 3.3, h: 1.4, fontFace: CN, fontSize: 10.5, color: MUTED, valign: "top" }));
  sl.addNotes("对照五步讲解，强调第⑤步：模型在哪里失效。实验报告第六部分按这五步写。数值为示意参数下的结果，以后按 SKY130 校准。\nWalk through the five steps, stressing step ⑤. Section 6 of the lab report follows them. Numbers use illustrative parameters, to be calibrated to SKY130.");
});

// ---- 例题：FO4 延时
const Wn = P.Wmin, Wp = r * P.Wmin, Id = M.idsatN(Wn), Rn = M.reqN(Wn), Cin = M.cin(Wn, Wp), Cself = (Wn + Wp) * P.Cd, CL = 4 * Cin + Cself, tphl = 0.69 * Rn * CL;
s = pres.addSlide();
s.background = { color: ICE };
tag(s, "例题  Worked example");
s.addText([{ text: `对称反相器 Wn = ${Wn} μm、Wp = ${f2(Wp)} μm，驱动 4 个相同反相器（FO4）。求 tPHL。`, options: { breakLine: true } },
           { text: `A symmetric inverter, Wn = ${Wn} μm and Wp = ${f2(Wp)} μm, drives four identical inverters (FO4). Find tPHL.`, options: { fontFace: EN, fontSize: 13, color: MUTED, bold: false } }],
  T({ x: 0.7, y: 0.75, w: 12, h: 1.4, fontFace: CN, fontSize: 20, color: INK, bold: true, valign: "top" }));
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 2.4, w: 12, h: 4.3, fill: { color: WHITE }, line: { color: "D5DEE8" }, rectRadius: 0.12 });
s.addText(biList([
  [`IDSAT,n = ½k′n(W/L)(VDD − VT)² = ${(Id * 1e6).toFixed(0)} μA`, `IDSAT,n = ½k′n(W/L)(VDD − VT)² = ${(Id * 1e6).toFixed(0)} μA`],
  [`Req,n ≈ ¾·VDD / IDSAT = ${f2(Rn / 1e3)} kΩ`, `Req,n ≈ ¾·VDD / IDSAT = ${f2(Rn / 1e3)} kΩ`],
  [`Cin = (Wn + Wp)·Cg = ${f2(Cin * 1e15)} fF；自载 (Wn + Wp)·Cd = ${f2(Cself * 1e15)} fF`, `Cin = (Wn + Wp)·Cg = ${f2(Cin * 1e15)} fF; self-load (Wn + Wp)·Cd = ${f2(Cself * 1e15)} fF`],
  [`CL = 4·Cin + 自载 = ${f2(CL * 1e15)} fF；tPHL = 0.69·Req,n·CL ≈ ${(tphl * 1e12).toFixed(1)} ps（虚拟实验 1.3 中验证）`, `CL = 4·Cin + self-load = ${f2(CL * 1e15)} fF; tPHL = 0.69·Req,n·CL ≈ ${(tphl * 1e12).toFixed(1)} ps (check it in lab 1.3)`]], 17, 12, INK, MUTED, true),
  T({ x: 1.0, y: 2.65, w: 11.4, h: 3.9, fontFace: CN, valign: "top" }));
s.addNotes("先让学生独立算 3 分钟，再展开；最后在虚拟实验 1.3 中设 Wp/Wn = 2.25、FO4 对照。\nGive students three minutes, then work through it and check in lab 1.3 with Wp/Wn = 2.25 at FO4.");

// ---- 本章小结
s = pres.addSlide();
s.background = { color: NAVY };
s.addText("本章小结", T({ x: 0.8, y: 0.5, w: 8, h: 0.7, fontFace: CN, fontSize: 30, color: WHITE, bold: true }));
s.addText("Chapter summary", T({ x: 0.8, y: 1.15, w: 8, h: 0.4, fontFace: EN, fontSize: 16, color: "9FB3D1" }));
s.addText(biList([["互补结构：稳态无直流通路；导通管相当于电阻 Ron", "Complementary structure: no static DC path; the on transistor acts as Ron"],
                  ["传输特性：VM 由两管强弱比决定，噪声容限保证抗干扰", "Transfer curve: VM set by the strength ratio; noise margins give immunity"],
                  ["延时：tp = 0.69·Req·CL；Wp/Wn = r 对称，≈ √r 最快", "Delay: tp = 0.69·Req·CL; Wp/Wn = r is symmetric, ≈ √r is fastest"],
                  ["大负载：等比反相器链，每级扇出约 4", "Large loads: a tapered chain with fan-out about 4 per stage"],
                  ["功耗：P = αCV²fN，降压最省电，但门会变慢", "Power: P = αCV²fN; lowering VDD saves most, but slows the gates"]], 17, 11.5, "E6EDF7", "9FB3D1"),
  T({ x: 0.8, y: 1.8, w: 11.8, h: 4.3, fontFace: CN, valign: "top" }));
s.addText("课后：5 个虚拟实验任务 ＋ 实验报告（任选一个机器人问题）；预习第 2 章 组合逻辑门\nAfter class: the five virtual labs + one lab report on a robot problem; preview Chapter 2, combinational gates",
  T({ x: 0.8, y: 6.2, w: 11.8, h: 0.8, fontFace: CN, fontSize: 14, color: AMBER }));
s.addNotes("回顾本章：一个反相器就包含了电平、速度、功耗三件事。后面的门电路、时序和版图都建立在这里。\nReview: one inverter already contains levels, speed and power; the gates, timing and layout that follow build on this.");

pres.writeFile({ fileName: OUT }).then(() => console.log("deck written", OUT, "slides", pres.slides.length));
