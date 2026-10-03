"""第 1 章五个虚拟实验的指导书内容（R7），中英对照。数值由 model.py 计算，保持与实验台一致。"""
import model as M

R = M.reference()
r = R["r"]
W11 = R["p11"]["Wn"]
VOL2 = None  # 1.1 第 3 题：Wn 不变、2 mA 时的 VOL
lo, hi = 0.0, M.VDD - M.VTn
for _ in range(60):
    mid = (lo + hi) / 2
    if M.idn(M.VDD, mid, W11) > 2e-3:
        hi = mid
    else:
        lo = mid
VOL2 = (lo + hi) / 2
N1, NR = R["p12"]["ratio1"], R["p12"]["ratio_r"]
T1, TS, TR = R["p13"]["ratio1"], R["p13"]["ratio_sqrt"], R["p13"]["ratio_r"]
C14 = R["p14"]
P15 = R["p15"]
f6 = C14["F"] ** (1 / 6)

LINK = "问渠课程页“虚拟实验”，或课件实验页的“打开虚拟实验”按钮 / the Virtual Lab link on the course page or the “Open virtual lab” button in the slides"
H = "数字集成电路设计 · 第 1 章 CMOS 反相器 · 虚拟实验"
HE = "Digital Integrated Circuit Design · Chapter 1 · Virtual Lab"
PARAM_NOTE = (f"模型参数（示意值，以后按 SKY130 校准）：VDD = {M.VDD} V，|VT| = {M.VTn} V，k′n = {M.kn*1e6:.0f} μA/V²，k′p = {M.kp*1e6:.0f} μA/V²，L = {M.L} μm，最小 W = {M.Wmin} μm。",
              f"Model parameters (illustrative, to be calibrated to SKY130): VDD = {M.VDD} V, |VT| = {M.VTn} V, k′n = {M.kn*1e6:.0f} μA/V², k′p = {M.kp*1e6:.0f} μA/V², L = {M.L} μm, minimum W = {M.Wmin} μm.")

LABS = [
  {
    "no": "1.1", "file": "实验1.1 MOSFET 开关与 CMOS 反相器（光耦输入）",
    "zh": "MOSFET 开关与 CMOS 反相器", "en": "MOSFET Switches and the CMOS Inverter",
    "goal": [("理解 CMOS 反相器的互补结构：稳态时总有一个管子截止，没有静态直流通路。", "Understand the complementary structure: in steady state one transistor is always off, so there is no static DC path."),
             ("学会用 NMOS 输出特性与负载线求输出低电平 VOL。", "Find the output low level VOL from the NMOS output curve and the load line."),
             ("用线性区模型确定满足 VOL 要求的最小管宽。", "Use the linear-region model to size the transistor for a VOL requirement.")],
    "theory": [("NMOS 平方律模型：线性区 ID = k′n(W/L)[(VGS − VT)VDS − VDS²/2]，饱和区 ID = ½k′n(W/L)(VGS − VT)²。", "NMOS square-law model: linear region ID = k′n(W/L)[(VGS − VT)VDS − VDS²/2]; saturation ID = ½k′n(W/L)(VGS − VT)²."),
               ("输入为高时 VGS = VDD，NMOS 吸收负载电流 I，输出电压 VOL 满足 ID(VDD, VOL) = I。VDS 很小时 NMOS 近似为电阻 Ron ≈ 1/[k′n(W/L)(VDD − VT)]。", "With the input high, VGS = VDD and the NMOS sinks the load current I; VOL satisfies ID(VDD, VOL) = I. For small VDS the NMOS is roughly a resistor Ron ≈ 1/[k′n(W/L)(VDD − VT)]."),
               ("要求 VOL ≤ VOL,max 时，W ≥ I·L / {k′n[(VDD − VT)VOL,max − VOL,max²/2]}。", "For VOL ≤ VOL,max, W ≥ I·L / {k′n[(VDD − VT)VOL,max − VOL,max²/2]}."),
               PARAM_NOTE],
    "env": [("输入", "Input", "低 0 V / 高 1.8 V", "low 0 V / high 1.8 V"),
            ("NMOS 宽度 Wn", "NMOS width Wn", "0.42 – 12 μm", "0.42 – 12 μm"),
            ("负载电流", "Load current", "0.1 – 3 mA", "0.1 – 3 mA")],
    "steps": [("把输入切到低、高电平各一次，观察上方示意图中哪个管子导通、电流路径怎样。", "Switch the input low and high; watch which transistor conducts and where current flows."),
              ("输入为高，负载 1.00 mA。把 Wn 从 2 μm 逐步增大，记录 VOL 和工作区，填表 1。", "Input high, load 1.00 mA. Increase Wn from 2 μm and record VOL and region in Table 1."),
              ("找出 VOL 刚好不超过 0.2 V 的 Wn，与公式计算值比较。", "Find the Wn at which VOL just reaches 0.2 V and compare with the formula."),
              ("保持该 Wn，把负载改为 0.5、1.5、2.0 mA，记录 VOL，填表 2。", "Keep that Wn, set the load to 0.5, 1.5 and 2.0 mA, record VOL in Table 2.")],
    "tables": [
      ("表 1  负载 1 mA 时 VOL 与 Wn Table 1  VOL vs Wn at 1 mA", ["Wn  μm", "W/L", "工作区 Region", "VOL  V（测）", "Ron = VOL/I  Ω"],
       [["2.0", "", "", "", ""], ["4.0", "", "", "", ""], ["6.0", "", "", "", ""], ["8.0", "", "", "", ""], ["满足 0.2 V 的最小值 min for 0.2 V", "", "", "", ""]], [4.2, 2.0, 3.0, 3.0, 3.4]),
      ("表 2  Wn 固定时 VOL 与负载 Table 2  VOL vs load at fixed Wn", ["负载 Load  mA", "0.5", "1.0", "1.5", "2.0"],
       [["VOL  V（测）", "", "", "", ""], ["I·Ron（线性估算）", "", "", "", ""]], [4.2, 2.6, 2.6, 2.6, 2.6]),
    ],
    "cautions": [("负载电流超过 NMOS 饱和电流时，输出拉不下来，读数显示“饱和（拉不住）”。", "If the load exceeds the NMOS saturation current, the output cannot be pulled low; the reading shows “saturated”."),
                 ("参数是示意值，结果的数量级和趋势可靠，具体数字待按 SKY130 工艺库校准。", "Parameters are illustrative: magnitudes and trends are reliable; exact numbers await SKY130 calibration.")],
    "questions": [("表 2 中，负载从 1 mA 加到 2 mA，VOL 是否正好翻倍？为什么？", "In Table 2, does VOL exactly double when the load goes from 1 to 2 mA? Why?"),
                  ("为什么说 CMOS 反相器“静态功耗几乎为零”？接了光耦以后，芯片还有静态电流吗？", "Why is the static power of a CMOS inverter almost zero? With the optocoupler attached, is there still static current?")],
    "problem": ("关节驱动板的光耦输入", "Optocoupler input on a joint driver",
                f"芯片输出要吸收 1 mA 点亮光耦，VOL ≤ 0.2 V。(1) 求最小 Wn（参考：约 {W11:.2f} μm）。(2) 负载加到 2 mA，VOL 变成多少（参考：约 {VOL2:.2f} V）？(3) 若光耦需要 5 mA，只加宽 NMOS 合理吗？有哪些替代办法？",
                f"The output must sink 1 mA for the optocoupler with VOL ≤ 0.2 V. (1) Find the minimum Wn (reference: about {W11:.2f} μm). (2) At 2 mA, what is VOL (reference: about {VOL2:.2f} V)? (3) If the optocoupler needed 5 mA, is widening the NMOS sensible? What alternatives exist?"),
    "everyday": ("楼梯间的双控开关：两个开关互补，灯只有亮、灭两种状态。它和 CMOS 反相器有什么相似之处？", "Two-way stair light switches are complementary: the light is either on or off. How is this like a CMOS inverter?"),
  },
  {
    "no": "1.2", "file": "实验1.2 电压传输特性与噪声容限（编码器抗干扰）",
    "zh": "电压传输特性与噪声容限", "en": "Voltage Transfer Characteristic and Noise Margins",
    "goal": [("测出反相器的电压传输特性，认识开关阈值 VM 和各工作区。", "Measure the voltage transfer characteristic and identify the threshold VM and operating regions."),
             ("用斜率为 −1 的点确定 VIL、VIH，计算噪声容限。", "Find VIL and VIH from the slope = −1 points and compute the noise margins."),
             ("用噪声容限判断编码器信号受干扰时是否会误翻转。", "Use noise margins to judge whether a noisy encoder signal will switch falsely.")],
    "theory": [("两管电流相等决定输出：IDn(Vin, Vout) = IDp(VDD − Vin, VDD − Vout)。两管同时饱和处为开关阈值 VM = [VTn + r′(VDD − |VTp|)]/(1 + r′)，r′ = √[k′pWp/(k′nWn)]。", "Equal currents set the output: IDn(Vin, Vout) = IDp(VDD − Vin, VDD − Vout). Where both saturate, VM = [VTn + r′(VDD − |VTp|)]/(1 + r′), r′ = √[k′pWp/(k′nWn)]."),
               ("VIL、VIH 是传输特性斜率为 −1 的两点；NML = VIL − VOL，NMH = VOH − VIH。", "VIL and VIH are the slope = −1 points; NML = VIL − VOL, NMH = VOH − VIH."),
               (f"Wp/Wn = r = k′n/k′p = {r:.2f} 时两管等强，VM = VDD/2。", f"With Wp/Wn = r = k′n/k′p = {r:.2f} the two transistors are equally strong and VM = VDD/2."),
               PARAM_NOTE],
    "env": [("尺寸比 Wp/Wn", "Size ratio Wp/Wn", "0.5 – 4", "0.5 – 4"),
            ("输入游标", "Input cursor", "0 – 1.8 V", "0 – 1.8 V"),
            ("输入干扰幅度", "Input noise", "0 – 0.6 V", "0 – 0.6 V")],
    "steps": [("尺寸比 1，拖动输入游标从 0 到 1.8 V，观察两管工作区怎样变化，记录五个典型点，填表 1。", "Ratio 1: drag the input cursor from 0 to 1.8 V, watch the regions change and record five points in Table 1."),
              ("读出 VM、VIL、VIH、NML、NMH；把尺寸比改为 1.5、2.25、3.0 重复，填表 2。", "Read VM, VIL, VIH, NML and NMH; repeat for ratios 1.5, 2.25 and 3.0 in Table 2."),
              ("调尺寸比使 VM = 0.90 V，与理论值 r 比较。", "Adjust the ratio until VM = 0.90 V and compare with r."),
              ("把干扰幅度设为 0.30 V，找出两个噪声容限都不小于 0.6 V 的尺寸比范围。", "Set the noise to 0.30 V and find the range of ratios for which both margins are at least 0.6 V.")],
    "tables": [
      ("表 1  传输特性（Wp/Wn = 1） Table 1  Transfer curve", ["Vin  V", "0.30", "0.60", "0.80", "1.00", "1.50"],
       [["Vout  V", "", "", "", "", ""], ["NMOS 工作区", "", "", "", "", ""], ["PMOS 工作区", "", "", "", "", ""]], [3.6, 2.4, 2.4, 2.4, 2.4, 2.4]),
      ("表 2  尺寸比与噪声容限 Table 2  Ratio and noise margins", ["Wp/Wn", "VM  V（测）", "VM  V（公式）", "VIL / VIH  V", "NML  V", "NMH  V"],
       [["1.0", "", "", "", "", ""], ["1.5", "", "", "", "", ""], ["2.25", "", "", "", "", ""], ["3.0", "", "", "", "", ""]], [2.2, 2.6, 2.8, 3.0, 2.4, 2.4]),
    ],
    "cautions": [("中段曲线极陡，游标步长 0.01 V，VM 以“曲线”读数为准。", "The middle of the curve is very steep; the cursor step is 0.01 V, so read VM from the curve value."),
                 ("模型忽略沟道长度调制，真实器件的中段斜率是有限的。", "The model ignores channel-length modulation; real devices have a finite slope in the middle.")],
    "questions": [("尺寸比从 1 增大到 3，VM 向哪边移动？NML、NMH 怎样变化？", "As the ratio grows from 1 to 3, which way does VM move, and how do NML and NMH change?"),
                  ("为什么数字电路要求中段增益大于 1？串联十个反相器时有什么好处？", "Why must the gain in the middle exceed 1? What does this buy when ten inverters are chained?")],
    "problem": ("编码器信号的抗干扰", "Noise immunity of an encoder signal",
                f"编码器信号经 2 m 电缆进入芯片，叠加约 ±0.3 V 干扰。(1) Wp/Wn = 1 时 NML、NMH 各多少（参考：{N1['NML']:.2f}、{N1['NMH']:.2f} V）？(2) Wp/Wn = {r:.2f} 时呢（参考：均约 {NR['NML']:.2f} V）？(3) 要求容限不小于干扰的 2 倍，应怎样选尺寸？干扰更大时电路上还能怎么办（如施密特触发器、差分信号）？",
                f"The encoder signal travels 2 m of cable with about ±0.3 V of noise. (1) With Wp/Wn = 1, what are NML and NMH (reference: {N1['NML']:.2f} and {N1['NMH']:.2f} V)? (2) With Wp/Wn = {r:.2f} (reference: both about {NR['NML']:.2f} V)? (3) If the margins must be at least twice the noise, how would you size it, and what if the noise were larger (Schmitt trigger, differential signalling)?"),
    "everyday": ("声控楼道灯的触发阈值：太低会被杂音触发，太高叫不亮。阈值和“噪声容限”是什么关系？", "A sound-activated stair light: a low threshold is triggered by noise, a high one won’t respond. How does this relate to noise margin?"),
  },
  {
    "no": "1.3", "file": "实验1.3 尺寸与对称（时钟缓冲）",
    "zh": "尺寸与对称", "en": "Sizing and Symmetry",
    "goal": [("理解迁移率差别使同尺寸 PMOS 上拉更慢。", "Understand why a same-size PMOS pulls up more slowly."),
             ("用 RC 模型计算 tPHL、tPLH，学会对称尺寸设计。", "Compute tPHL and tPLH with the RC model and size for symmetry."),
             ("比较“对称尺寸”与“平均延时最小”两种设计目标。", "Compare the two goals: symmetric edges versus minimum average delay.")],
    "theory": [("等效电阻 Req ≈ ¾·VDD/IDSAT；延时 tPHL = 0.69·Req,n·CL，tPLH = 0.69·Req,p·CL，tp = (tPHL + tPLH)/2。", "Equivalent resistance Req ≈ ¾·VDD/IDSAT; tPHL = 0.69·Req,n·CL, tPLH = 0.69·Req,p·CL, tp = (tPHL + tPLH)/2."),
               ("负载 CL = 自载（漏极电容）＋扇出 × 下一级输入电容。加宽 PMOS 降低 Req,p，但增大输入电容。", "Load CL = self-load (drain capacitance) + fan-out × next-stage input capacitance. A wider PMOS lowers Req,p but raises input capacitance."),
               (f"Wp/Wn = r 时上升下降相等；Wp/Wn ≈ √r（约 {r**0.5:.2f}）时平均延时最小。", f"Wp/Wn = r equalises the edges; Wp/Wn ≈ √r (about {r**0.5:.2f}) minimises the average delay."),
               PARAM_NOTE],
    "env": [("尺寸比 Wp/Wn", "Size ratio Wp/Wn", "0.5 – 4", "0.5 – 4"),
            ("扇出", "Fan-out", "FO1 – FO8", "FO1 – FO8")],
    "steps": [("扇出 FO4，尺寸比依次取表 1 中的值，读出 tPHL、tPLH、tp、上升下降差，填表 1。", "At FO4, set each ratio in Table 1 and record tPHL, tPLH, tp and the mismatch."),
              ("从下方曲线找出 tp 最小的尺寸比，与 √r 比较。", "From the lower plot, find the ratio with the smallest tp and compare with √r."),
              ("尺寸比 2.25，把扇出改为 1、2、8，记录 tp，填表 2，分析 tp 与扇出的关系。", "At ratio 2.25, set fan-out to 1, 2 and 8, record tp in Table 2 and analyse how tp scales with fan-out.")],
    "tables": [
      ("表 1  FO4 下尺寸比与延时 Table 1  Ratio vs delay at FO4", ["Wp/Wn", "tPHL  ps", "tPLH  ps", "tp  ps", "差 Mismatch %"],
       [["1.0", "", "", "", ""], ["1.5", "", "", "", ""], ["2.25", "", "", "", ""], ["3.0", "", "", "", ""]], [2.6, 3.0, 3.0, 3.0, 3.4]),
      ("表 2  扇出与延时（Wp/Wn = 2.25） Table 2  Fan-out vs delay", ["扇出 Fan-out", "FO1", "FO2", "FO4", "FO8"],
       [["tp  ps", "", "", "", ""]], [3.4, 2.6, 2.6, 2.6, 2.6]),
    ],
    "cautions": [("波形用一阶 RC 近似，真实波形边沿形状略有不同，但延时数量级一致。", "Waveforms use a first-order RC approximation; real edge shapes differ slightly but the delay magnitude agrees."),
                 ("延时数值依赖示意参数，FO4 约几十皮秒的量级与 130 nm 级工艺相符。", "Delays depend on the illustrative parameters; tens of picoseconds for FO4 is consistent with a 130 nm-class process.")],
    "questions": [("为什么加宽 PMOS 后 tPHL 也会变长？", "Why does widening the PMOS also lengthen tPHL?"),
                  ("tp 与扇出大致成什么关系？为什么有一个“与扇出无关”的部分？", "Roughly how does tp scale with fan-out? Why is there a part that does not depend on fan-out?")],
    "problem": ("电机控制芯片的时钟缓冲", "The clock buffer of a motor-control chip",
                f"时钟缓冲上升下降不等会让占空比走样。(1) Wp/Wn = 1、FO4 时 tPHL、tPLH 各多少，相差百分之几（参考：{T1['tphl']*1e12:.0f}、{T1['tplh']*1e12:.0f} ps，{T1['mismatch']*100:.0f}%）？(2) 怎样取尺寸使两者相等（参考：Wp/Wn ≈ {r:.2f}，约 {TR['tp']*1e12:.0f} ps）？(3) 普通逻辑路径为什么常取 √r 附近（参考：tp ≈ {TS['tp']*1e12:.0f} ps）？",
                f"Unequal edges in the clock buffer distort the duty cycle. (1) With Wp/Wn = 1 at FO4, what are tPHL and tPLH and their mismatch (reference: {T1['tphl']*1e12:.0f} and {T1['tplh']*1e12:.0f} ps, {T1['mismatch']*100:.0f}%)? (2) How do you size for equal edges (reference: Wp/Wn ≈ {r:.2f}, about {TR['tp']*1e12:.0f} ps)? (3) Why do ordinary logic paths often use about √r (reference: tp ≈ {TS['tp']*1e12:.0f} ps)?"),
    "everyday": ("跷跷板两边体重不同，要挪支点才能平衡。尺寸比在反相器里起什么作用？", "On a seesaw with unequal weights you move the pivot to balance it. What plays that role in an inverter?"),
  },
  {
    "no": "1.4", "file": "实验1.4 传播延时与反相器链（驱动大负载）",
    "zh": "传播延时与反相器链", "en": "Propagation Delay and the Inverter Chain",
    "goal": [("理解小尺寸门驱动大负载时延时急剧增大的原因。", "Understand why a small gate driving a large load is so slow."),
             ("学会用等比反相器链优化驱动大负载的延时。", "Optimise the delay of driving a large load with a tapered inverter chain."),
             ("掌握“每级扇出约 4”的经验规则及其来源。", "Learn the rule of thumb of about 4 per stage and where it comes from.")],
    "theory": [("总扇出 F = CL/Cin。N 级等比链每级扇出 f = F^(1/N)，总延时 t = N·tp0·(γ + f)，tp0 = 0.69·Req·Cin，γ 为自载与输入电容之比。", "Total fan-out F = CL/Cin. In an N-stage tapered chain each stage has f = F^(1/N), total delay t = N·tp0·(γ + f), tp0 = 0.69·Req·Cin, γ = self-load / input capacitance."),
               ("忽略自载（γ = 0）时最优 f = e ≈ 2.7；考虑自载后最优 f 约 3.6–4，因此 N ≈ ln F / ln 4。", "Ignoring self-load (γ = 0) the optimum is f = e ≈ 2.7; with self-load the optimum is about 3.6–4, hence N ≈ ln F / ln 4."),
               ("级数为奇数时输出反相，为偶数时同相。", "An odd number of stages inverts the signal; an even number does not."),
               PARAM_NOTE],
    "env": [("级数 N", "Stages N", "1 – 10", "1 – 10"),
            ("负载 CL", "Load CL", "1 – 20 pF", "1 – 20 pF")],
    "steps": [("CL = 10 pF，级数从 1 到 10 依次设置，读出每级扇出 f 和总延时，填表 1。", "CL = 10 pF: set N from 1 to 10 and record f and total delay in Table 1."),
              ("找出总延时最小的级数，与 ln F / ln 4 比较。", "Find the N with the smallest delay and compare with ln F / ln 4."),
              ("找出延时小于 0.3 ns 的最少级数。", "Find the fewest stages that give a delay under 0.3 ns."),
              ("把 CL 改为 2 pF 和 20 pF，重复找最优级数，填表 2。", "Repeat for CL = 2 pF and 20 pF; record the optimum in Table 2.")],
    "tables": [
      ("表 1  级数与延时（CL = 10 pF） Table 1  Stages vs delay", ["N", "1", "2", "3", "4", "5", "6", "7", "8"],
       [["f", "", "", "", "", "", "", "", ""], ["总延时 ns", "", "", "", "", "", "", "", ""]], [2.8, 1.6, 1.6, 1.6, 1.6, 1.6, 1.6, 1.6, 1.6]),
      ("表 2  负载与最优级数 Table 2  Load vs optimum", ["CL  pF", "F", "ln F / ln 4", "最优 N（测）", "最小延时 ns"],
       [["2", "", "", "", ""], ["10", "", "", "", ""], ["20", "", "", "", ""]], [2.4, 2.6, 3.0, 3.2, 3.2]),
    ],
    "cautions": [("延时坐标是对数刻度。", "The delay axis is logarithmic."),
                 ("模型忽略走线电阻和焊盘电容的细节，只把它们合在 CL 里。", "The model lumps wiring and pad effects into CL.")],
    "questions": [("为什么级数太多反而变慢？", "Why does adding too many stages make it slower?"),
                  ("最优附近总延时变化很平缓，工程上会怎样取舍级数？", "Near the optimum the delay is flat. How would an engineer choose the number of stages?")],
    "problem": ("驱动板上的栅极驱动器", "Driving the gate driver on the board",
                f"芯片输出驱动约 10 pF 的总负载。(1) 最小对称反相器的输入电容和总扇出 F 各多少（参考：{C14['Cin']*1e15:.2f} fF，F ≈ {C14['F']:.0f}）？(2) 单级驱动延时多大（参考：约 {C14['t']['1']*1e9:.0f} ns）？(3) 取 6 级时每级扇出和总延时多少（参考：f ≈ {f6:.1f}，约 {C14['t']['6']*1e12:.0f} ps）？要求输出与输入同相时应取几级？",
                f"The chip output drives about 10 pF. (1) What are the minimum symmetric inverter’s input capacitance and the total fan-out F (reference: {C14['Cin']*1e15:.2f} fF, F ≈ {C14['F']:.0f})? (2) What is the single-stage delay (reference: about {C14['t']['1']*1e9:.0f} ns)? (3) With 6 stages, what are f and the total delay (reference: f ≈ {f6:.1f}, about {C14['t']['6']*1e12:.0f} ps)? How many stages if the output must not be inverted?"),
    "everyday": ("搬一件很重的东西，一个人搬太慢，分几段逐级加人接力更快。人越多越好吗？", "Moving something heavy: relays with more and more people at each stage go faster. Are more people always better?"),
  },
  {
    "no": "1.5", "file": "实验1.5 功耗（巡线小车控制芯片）",
    "zh": "功耗", "en": "Power",
    "goal": [("理解动态功耗来自对负载电容的反复充放电。", "Understand that dynamic power comes from repeatedly charging and discharging capacitance."),
             ("用 P = αCV²fN 估算芯片功耗，分析各因素的影响。", "Estimate chip power with P = αCV²fN and analyse each factor."),
             ("认识降压省电与速度之间的权衡。", "See the trade-off between lowering the supply and speed.")],
    "theory": [("每次 0→1 翻转电源送出 CV²：一半存进电容，一半在 PMOS 上变成热；1→0 时电容里的 ½CV² 在 NMOS 上变成热。", "Each 0→1 transition draws CV² from the supply: half is stored, half burnt in the PMOS; on 1→0 the stored ½CV² is burnt in the NMOS."),
               ("动态功耗 P = αCV²fN，α 为翻转率，N 为门数。功耗与电压平方成正比。", "Dynamic power P = αCV²fN, with activity α and gate count N; it scales with the square of the supply."),
               ("降低 VDD 使 IDSAT 下降、Req 上升，门延时变长：tp ∝ VDD/(VDD − VT)²。", "Lowering VDD lowers IDSAT and raises Req, so gate delay grows: tp ∝ VDD/(VDD − VT)²."),
               PARAM_NOTE],
    "env": [("电源电压", "Supply", "0.9 – 1.8 V", "0.9 – 1.8 V"),
            ("时钟频率", "Clock", "10 – 200 MHz", "10 – 200 MHz"),
            ("翻转率 α", "Activity α", "0.02 – 0.5", "0.02 – 0.5"),
            ("门数 N", "Gate count N", "1 000 – 100 000（对数刻度）", "1 000 – 100 000 (log scale)")],
    "steps": [("默认设置（1 万门、α = 0.1、100 MHz、1.8 V），读出动态功耗和 FO4 延时。", "Default settings (10 000 gates, α = 0.1, 100 MHz, 1.8 V): read the dynamic power and FO4 delay."),
              ("只改电压，依次取表 1 中的值，记录功耗和 FO4 延时。", "Change only the supply to each value in Table 1 and record power and FO4 delay."),
              ("只改频率或翻转率，验证功耗与它们成正比。", "Change only the clock or activity and verify that power is proportional."),
              ("找出 FO4 延时不超过 100 ps 的最低电压。", "Find the lowest supply with FO4 delay ≤ 100 ps.")],
    "tables": [
      ("表 1  电压、功耗与延时 Table 1  Supply, power and delay", ["VDD  V", "1.8", "1.5", "1.2", "1.0"],
       [["功耗 mW（测）", "", "", "", ""], ["功耗 mW（公式）", "", "", "", ""], ["FO4  ps", "", "", "", ""]], [3.8, 2.6, 2.6, 2.6, 2.6]),
      ("表 2  频率与翻转率（VDD = 1.8 V） Table 2  Clock and activity", ["设置 Setting", "50 MHz, α 0.1", "100 MHz, α 0.1", "200 MHz, α 0.1", "100 MHz, α 0.2"],
       [["功耗 mW", "", "", "", ""]], [3.0, 3.1, 3.1, 3.1, 3.1]),
    ],
    "cautions": [("模型不计漏电和短路电流，低电压、高温时漏电不可忽略。", "Leakage and short-circuit current are ignored; at low voltage or high temperature leakage matters."),
                 ("电池续航只计芯片本身，不含电机。", "Battery life counts only the chip, not the motors.")],
    "questions": [("电压降为原来的 2/3，功耗变为原来的多少？为什么不是 2/3？", "If the supply drops to 2/3, what fraction of the power remains, and why not 2/3?"),
                  ("为了省电同时降频和降压，计算速度会怎样变化？", "If you lower both clock and supply to save power, what happens to computing speed?")],
    "problem": ("巡线小车控制芯片的功耗预算", "Power budget of a line-following car controller",
                f"约 1 万个门，α = 0.1，100 MHz，每门 5 fF。(1) 1.8 V 时动态功耗多少（参考：{P15['P_VDD']*1e3:.2f} mW）？(2) 降到 1.2 V 呢（参考：{P15['P_low']*1e3:.2f} mW）？(3) 控制环要求 FO4 ≤ 100 ps，最低能降到多少伏？电机电流远大于芯片，芯片省电对整车续航有意义吗？什么场合有意义？",
                f"About 10 000 gates, α = 0.1, 100 MHz, 5 fF per gate. (1) Dynamic power at 1.8 V (reference: {P15['P_VDD']*1e3:.2f} mW)? (2) At 1.2 V (reference: {P15['P_low']*1e3:.2f} mW)? (3) If the control loop needs FO4 ≤ 100 ps, how low can the supply go? The motors draw far more than the chip—does saving chip power matter for battery life, and when does it?"),
    "everyday": ("手机的省电模式会降频、降压。它为什么能省电？代价是什么？", "Phone power-saving modes lower clock and voltage. Why does that save power, and what is the cost?"),
  },
]
