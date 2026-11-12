"""第 161f 轮：电路板厂案例 A——关节驱动板的相电流采样：采样电阻 + 放大器，计算、ngspice、布局要点，到在线测试与功能测试。

    python3 tools/cases/pcb_a.py

计算与仿真用数字工厂“电路分析”例题 1（cae/circuit.py 的 sense，同一张网表、同一个蒙特卡洛）；电路与器件取驱动板 B 版的设计描述
（factory/designs/drv-joint/design.yaml 的 sense 功能块）；元件从零件库选；制造用电路板厂仿真车间。输出到 factory/cases/pcb/A/。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-pcb.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
from cae import circuit as C  # noqa: E402

TOOLS = {
    "circuit": ("电路分析：例题 1 相电流采样", "Circuit analysis: example 1", "/circuit"),
    "pcb": ("电路板设计（驱动板）", "PCB design (drive board)", "/pcb-design"),
    "fct": ("功能测试台", "Functional test bench", "/fct"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("pcb", "A", "简单", "关节驱动板的相电流采样", "Phase-current sensing on the joint drive board", "DRV-JOINT-B 相电流采样",
              "电机电流环要知道每一相电流：比较三种测法，选采样电阻 + 专用放大器；算灵敏度、量程、功耗、分辨率，用 ngspice 核对增益、带宽和元件容差，"
              "定布局要点（开尔文接法），到电路板厂在线测试量采样电阻、功能测试量电流误差，20 块板。",
              "The current loop needs each phase current: three methods compared, shunt + dedicated amplifier chosen; sensitivity, range, dissipation and resolution calculated, "
              "ngspice for gain, bandwidth and tolerances, layout rules (Kelvin connection), then in-circuit and functional test of 20 boards.",
              "tools/cases/pcb_a.py")

SH = L.lib_part("A-ELE-SHUNT", "2M")
AMP = L.lib_part("A-ELE-SOIC8", "INA240A1D")
MCU = L.lib_part("A-ELE-LQFP48", "STM32G431CBT6")
CAA = L.lib_part("A-ELE-C0402", "1N")
CDEC = L.lib_part("A-ELE-C0402", "100N")
RS = float(SH["row"]["r_ohm"])
GAIN = 20.0                          # INA240A1 的固定增益（器件数据待核对，设计描述 sense 功能块）
IP, IR = C.i_peak(), C.i_rated()
ADC = C.BOARD["adc_fs"]

# ================================================================ 1 任务书
brief = f"""# 设计任务书：相电流采样

**用在哪**　关节伺服驱动板 DRV-JOINT-B（电路板厂做、卖给机器人厂的关节模组），驱动 400 W 伺服电机，48 V 母线，逆变器 {C.BOARD['f_pwm'] / 1000:g} kHz。
磁场定向控制每个开关周期要读两到三相电流，电流环带宽和转矩精度都靠它。

| 项目 | 要求 | 出处 |
|---|---|---|
| 电流 | 额定 {IR:.1f} A、峰值 {IP:.1f} A（双向） | 电机选型助手（400 W 伺服：峰值 4.46 N·m ÷ 力矩常数 {C.BOARD['kt']} N·m/A） |
| ADC | {ADC:g} V 满量程、12 位（MCU `{MCU['size']}`，零件库） | 驱动板设计 |
| 精度 | 功能测试相电流误差 ±2 % | 电路板厂功能测试公差 |
| 带宽 | ≥ 电流环带宽的 10 倍（电流环约 2 kHz → ≥ 20 kHz） | 电路分析例题 6 |
| 共模 | 采样点电压随开关在 0–48 V 之间跳 | 逆变器 |
"""
case.step("brief", f"额定 {IR:.1f} A、峰值 {IP:.1f} A，3.3 V 12 位 ADC，误差 ±2 %，带宽 ≥ 20 kHz，共模 0–48 V 跳变。",
          f"{IR:.1f} A rated, {IP:.1f} A peak, 3.3 V 12-bit ADC, ±2 % error, bandwidth ≥ 20 kHz, common mode jumping 0–48 V.",
          md=case.text("1_任务书.md", brief), tools=tools("circuit"),
          facts=[("峰值电流", "Peak current", round(IP, 1), "A"), ("精度", "Accuracy", "±2", "%")])

# ================================================================ 2 方案
concept = f"""# 方案：三种测法

| 测法 | 好处 | 问题 |
|---|---|---|
| 霍尔电流传感器 | 隔离、无损耗 | 贵、体积大、零点温漂大 |
| 下桥臂采样电阻 + 运放差分放大（例题 1 的通用电路） | 便宜，共模在地附近 | 只有下管导通时才有电流可读，占空比大时读不到；多一个电阻对 |
| **相线串采样电阻 + 专用电流采样放大器** | 任何时刻都能读；放大器能承受 −4…80 V 共模并抑制开关跳变（器件规格，待核对） | 放大器贵一点 |

**选相线串 {RS * 1000:g} mΩ 采样电阻（零件库 `{SH['ref']}`，2512 封装）+ 固定增益 20 的专用放大器（零件库 `{AMP['ref']}`）**，输出零点偏在 ADC 中间（{ADC / 2:g} V），双向。
固定增益放大器内部电阻激光修调，增益误差和共模抑制都比分立运放 + 1 % 电阻好得多——第 4 步用蒙特卡洛看分立电路的散布。
"""
case.step("concept", "三种测法比较，选相线采样电阻 + 专用放大器（零件库 2 mΩ、增益 20）：任何时刻可读，承受 48 V 共模跳变。",
          "Three methods compared; in-line shunt + dedicated amplifier chosen (library 2 mΩ, gain 20): readable at any time and tolerant of the 48 V common-mode swing.",
          md=case.text("2_方案.md", concept), tools=L.lib_tools([SH, AMP]))

# ================================================================ 3 计算
sens = GAIN * RS                       # V/A
rng = ADC / 2 / sens
swing = sens * IP
p_r, p_p = IR ** 2 * RS, IP ** 2 * RS
lsb = ADC / 4096 / sens
opts = []
for rs_m in (1.0, 2.0, 5.0):
    s_ = GAIN * rs_m * 1e-3
    opts.append([f"{rs_m:g} mΩ", f"{s_ * 1000:.0f} mV/A", f"±{ADC / 2 / s_:.1f} A", f"{IR ** 2 * rs_m * 1e-3 * 1000:.0f} mW", f"{ADC / 4096 / s_ * 1000:.1f} mA",
                 "量程 > 峰值" if ADC / 2 / s_ >= IP else "**量程不够**", "✓ 选定" if rs_m == 2.0 else ""])
calcmd = f"""# 计算

## 采样电阻取多大

{L.md_table(["采样电阻", "灵敏度（× 20）", "量程", "额定电流时功耗", "ADC 1 个最低位", "量程", ""], opts)}

电阻大，信号大、分辨率好，但发热和压降大，量程变小；**{RS * 1000:g} mΩ** 是量程覆盖峰值（{IP:.1f} A）里分辨率最好的。

## 选定值

- 灵敏度 G·R_s = 20 × {RS * 1000:g} mΩ = **{sens * 1000:.0f} mV/A**；零点 {ADC / 2:g} V；量程 ±{rng:.1f} A（峰值 {IP:.1f} A，余量 {rng / IP:.2f} 倍）
- 峰值电流时输出摆幅 {swing:.3f} V → 最低 {ADC / 2 - swing:.3f} V、最高 {ADC / 2 + swing:.3f} V，在 0–{ADC:g} V 之内
- 功耗：额定 {p_r * 1000:.0f} mW、峰值 {p_p * 1000:.0f} mW（峰值是短时的）；2512 封装额定 1 W 量级（器件数据待核对）——三相各一只
- 分辨率：12 位 ADC 一个最低位 = {lsb * 1000:.1f} mA（额定电流的 {lsb / IR * 100:.2f} %）
- 误差来源：采样电阻 ±{SH['row']['tol_pct']} %（零件库）、放大器增益误差、零点失调——前两项是比例误差，**出厂功能测试时按每块板标定**；零点每次上电、电机不转时读一次扣掉。
"""
case.step("calc", f"2 mΩ × 20 = {sens * 1000:.0f} mV/A，量程 ±{rng:.1f} A（峰值 {IP:.1f} A），额定功耗 {p_r * 1000:.0f} mW，分辨率 {lsb * 1000:.1f} mA。",
          f"2 mΩ × 20 = {sens * 1000:.0f} mV/A, range ±{rng:.1f} A (peak {IP:.1f} A), {p_r * 1000:.0f} mW at rated current, {lsb * 1000:.1f} mA resolution.",
          md=case.text("3_计算书.md", calcmd), tools=tools("circuit"),
          facts=[("灵敏度", "Sensitivity", round(sens * 1000), "mV/A"), ("量程", "Range", round(rng, 1), "A"), ("额定功耗", "Rated dissipation", round(p_r * 1000), "mW")])
case.check("calc", "量程 / 峰值电流", "Range / peak current", round(rng / IP, 2), ">=", 1.05, "", "设计描述 sense_headroom")

# ================================================================ 4 仿真
sim = C.simulate("sense", {"rs_mohm": RS * 1000, "gain": GAIN})
cmp_rows = [[r["label"], f"{r['sim']:.4g} {r['unit']}", f"{r['formula']:.4g} {r['unit']}", f"{r['diff'] * 100:.2f} %", "✓" if r["ok"] else "✗"] for r in sim["compare"]]
mc = C.montecarlo("sense", {"rs_mohm": RS * 1000, "gain": GAIN}, n=200, seed=1616)
mc_pct = 3 * mc["std"] / abs(mc["nominal"] - ADC / 2) * 100
b = C.build("sense", {"rs_mohm": RS * 1000, "gain": GAIN})
rdc = C.run(b["netlists"]["dc"])
rac = C.run(b["netlists"]["ac"])
fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.0))
d = rdc["plots"][0]["data"]
xk = next(k for k in d if "sweep" in k.lower() or k.lower().startswith("i"))
axs[0].plot(np.array(d[xk]), np.array(d["v(out)"]), color=L.ACCENT)
axs[0].axhline(0, color=L.MUTED, lw=0.5)
axs[0].axhline(ADC, color=L.MUTED, lw=0.5)
axs[0].axvspan(-IP, IP, color=L.OK, alpha=0.12)
axs[0].set_xlabel("相电流 / A")
axs[0].set_ylabel("放大器输出 / V")
axs[0].set_title("直流：40 mV/A，零点 1.65 V", fontsize=9.5)
a = rac["plots"][0]["data"]
fr = np.array(a["frequency"])
fr = np.abs(fr[:, 0]) if fr.ndim == 2 else np.abs(fr)
vo = np.array(a["v(out)"])
mag = np.hypot(vo[:, 0], vo[:, 1]) if vo.ndim == 2 else np.abs(vo)
axs[1].semilogx(fr, 20 * np.log10(mag / mag[0]), color=L.ACCENT)
axs[1].axhline(-3, color=L.MUTED, ls=":", lw=0.8)
axs[1].set_xlabel("频率 / Hz")
axs[1].set_ylabel("相对增益 / dB")
axs[1].set_title(f"交流：−3 dB 约 {sim['meas'].get('f3db', float('nan')) / 1000:.0f} kHz", fontsize=9.5)
edges = [mc["bin_lo"] + i * mc["bin_w"] for i in range(len(mc["hist"]))]
axs[2].bar(edges, mc["hist"], width=mc["bin_w"], color="#8aa4bd", align="edge")
axs[2].set_xlabel("峰值电流时输出 / V（分立 1 % 电阻）")
axs[2].set_title(f"蒙特卡洛 200 次：±{mc_pct:.1f} %（3σ）", fontsize=9.5)
case.fig(fig, "4_ngspice.png")
simmd = f"""# 仿真：数字工厂“电路分析”例题 1（同一张网表、同一个蒙特卡洛）

例题 1 用通用运放 + 四个电阻搭差分放大器（参数 rs_mohm = {RS * 1000:g}、gain = {GAIN:g}），用来核对公式；实际板子上换成固定增益的专用放大器。

{L.md_table(["读数", "ngspice", "公式", "相差", ""], cmp_rows)}

**元件容差**：采样电阻、四个增益电阻都按 ±1 % 随机取 200 次，峰值电流时输出的散布 ±{mc_pct:.1f} %（3σ，相对摆幅）——
比任务书 ±2 % 还大。**分立方案必须逐块标定**；专用放大器的增益误差是器件规格里的一个小数（待核对），加上采样电阻 ±1 %，功能测试时标定一次就进 ±2 %。
带宽 {sim['meas'].get('f3db', float('nan')) / 1000:.0f} kHz 远高于 20 kHz；实际还要在 ADC 前加 RC（{CAA['size']} 电容，零件库）滤掉开关尖峰。
"""
case.step("sim", f"ngspice 与公式相差 ≤ {max(r['diff'] for r in sim['compare']) * 100:.2f} %；带宽 {sim['meas'].get('f3db', 0) / 1000:.0f} kHz；分立 1 % 电阻的散布 ±{mc_pct:.1f} %，要逐块标定。",
          f"ngspice within {max(r['diff'] for r in sim['compare']) * 100:.2f} % of the formulas; bandwidth {sim['meas'].get('f3db', 0) / 1000:.0f} kHz; ±{mc_pct:.1f} % spread with discrete 1 % resistors, so every board is calibrated.",
          md=case.text("4_ngspice仿真.md", simmd), figs=[("4_ngspice.png", "直流、交流、蒙特卡洛", "DC, AC, Monte Carlo")], tools=tools("circuit"),
          facts=[("带宽", "Bandwidth", round(sim["meas"].get("f3db", 0) / 1000), "kHz"), ("容差散布（3σ）", "Tolerance spread (3σ)", round(mc_pct, 1), "%")])
case.check("sim", "ngspice 与公式最大相差", "Largest ngspice-vs-formula difference", round(max(r["diff"] for r in sim["compare"]) * 100, 2), "<=", 3.0, "%", "例题 1 的核对规则")
case.check("sim", "−3 dB 带宽", "−3 dB bandwidth", round(sim["meas"].get("f3db", 0) / 1000), ">=", 20, "kHz", "任务书")


# ================================================================ 5 布局：驱动板 B 版的铜层图（KiCad 产物）
def svg_png(svg, png, w=1400):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": w, "height": int(w * 0.75)}, device_scale_factor=3)
        pg.goto(Path(svg).resolve().as_uri())
        pg.wait_for_timeout(300)
        el = pg.query_selector("svg")
        el.screenshot(path=str(png))
        br.close()


svg_png(ROOT / "factory" / "designs" / "drv-joint-b" / "out" / "pcb" / "F_Cu.svg", case.path("5_顶层铜.png"))
cadmd = f"""# 布局：开尔文接法和放大器位置

驱动板 B 版（`factory/designs/drv-joint-b`，KiCad 工程由设计描述生成、自动布线）顶层铜：

![顶层铜](5_顶层铜.png)

采样电阻 R21–R23（2512）串在三相输出上，相电流几十安培从电阻的大焊盘流过；**放大器的两根输入线从电阻焊盘内侧单独引出（开尔文接法）**，
不和大电流共用一段铜——否则焊盘和走线那几毫欧也被量进去（2 mΩ 的电阻，多 0.2 mΩ 的铜就是 10 % 误差）。其余要点：

1. 两根输入线并排走、等长，远离开关节点（相输出、栅极驱动）。
2. 放大器靠近采样电阻，输出到 ADC 的线可以长一点（低阻抗、已放大）；ADC 前 RC 靠近 MCU。
3. 放大器去耦 `{CDEC['ref']}` 贴着电源脚。
4. 采样电阻焊盘下面多打散热过孔到内层，额定 {p_r * 1000:.0f} mW 的热要散掉，电阻温度高了阻值会变。

{L.lib_md([SH, AMP, MCU, CAA, CDEC], {SH['ref']: "R21–R23（三相各一只）", AMP['ref']: "U 三只（三相各一只）", MCU['ref']: "ADC", CAA['ref']: "ADC 前 RC", CDEC['ref']: "去耦"})}
"""
case.step("cad", "驱动板 B 版顶层铜：采样电阻开尔文接法、放大器靠近电阻、输入线并排等长、焊盘下散热过孔。",
          "Drive board rev B top copper: Kelvin connection of the shunts, amplifier next to the shunt, paired equal-length inputs, thermal vias under the pads.",
          md=case.text("5_布局要点.md", cadmd), figs=[("5_顶层铜.png", "驱动板 B 版顶层铜（KiCad 产物）", "Drive board rev B top copper (KiCad output)")],
          tools=tools("pcb") + L.lib_tools([SH, AMP, MCU, CAA, CDEC]))

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rt_smt = F.ROUTINGS[F.BOMS["SMT-DRV-B"][0]]
rt_be = F.ROUTINGS[F.BOMS["DRV-JOINT-B"][0]]
procmd = f"""# 工艺：贴片线 + 后段

**贴片线**（SMT-DRV-B）：

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt_smt)])}

**后段**（DRV-JOINT-B）：

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt_be)])}

和相电流采样有关的：

- **锡膏印刷 / 检测**：2512 大焊盘要足够锡量，少锡会让接触电阻变大、量出来电流偏小；
- **在线测试（ICT）**：四线法量每只采样电阻（2 mΩ ± 1 %，两线法量不准——表笔接触电阻比它还大）；
- **功能测试（FCT）**：通已知电流，读 MCU 的采样值，算出每相增益写进板上存储（就是第 4 步说的“逐块标定”），再复测误差 ±2 %。
"""
case.step("process", f"贴片线 {len(rt_smt)} 道、后段 {len(rt_be)} 道；锡量、四线法测采样电阻、功能测试标定写入。",
          f"{len(rt_smt)} SMT and {len(rt_be)} back-end operations; paste volume, four-wire shunt test, per-board calibration at functional test.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer", "fct"), facts=[("工序", "Operations", len(rt_smt) + len(rt_be), "")])

# ================================================================ 7 制造
sh = L.run_shop("DRV-JOINT-B", 20, "WO-CASE-PCB-A", seed=1621)
meas = [m for m in sh["measurements"] if m["characteristic"] in ("ict_shunt", "fct_isense", "fct_drift")]
rows_q, cpk_min, fails, st = L.shop_table(meas)
makemd = f"""# 制造：20 块驱动板

电路板厂仿真车间后段做 20 块 DRV-JOINT-B（{sh['hours']:.1f} 小时），和电流采样有关的三项：

{L.md_table(["特性", "公差", "块数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}**，最低 Cpk {cpk_min:.2f}。采样电阻阻值的散布（ICT）比 ±1 % 公差小得多；相电流误差在标定后测，散布主要来自零点和噪声。
"""
case.step("make", f"20 块：采样电阻、相电流误差、老化零漂三项，不合格 {fails}，最低 Cpk {cpk_min:.2f}。",
          f"20 boards: shunt resistance, phase-current error and drift after burn-in; {fails} failures, lowest Cpk {cpk_min:.2f}.",
          md=case.text("7_制造与测试.md", makemd), tools=tools("planner", "operator", "quality", "fct"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", round(cpk_min, 2), "")])
case.check("make", "不合格项", "Failures", fails, "==", 0, "", "在线测试、功能测试")
case.check("make", "最低 Cpk", "Lowest Cpk", round(cpk_min, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **采样电阻是“信号大小 ↔ 发热、量程”的折中**：{RS * 1000:g} mΩ 是量程够的里面分辨率最好的。
2. **几毫欧的电阻，布局决定精度**：开尔文接法、散热过孔。
3. **比例误差标定掉，零点每次上电扣掉**：分立电路的 ±{mc_pct:.1f} % 散布也能用，但标定是必须的工序。

## 留给学生的问题

1. 在“电路分析”例题 1 把采样电阻改成 1 mΩ、增益改成 50：量程、功耗、带宽各怎么变？
2. 电机峰值电流加大到 45 A（换大电机），这块板要改什么？
3. 为什么功能测试要在老化之后再测一次零点？

相关：数字工厂“电路分析”“电路板设计”“功能测试台”；电路板厂实验 37（采样电阻卷号追因）、实验 39（一块驱动板从订单到交付）；案例 C（整块驱动板）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；{sens * 1000:.0f} mV/A、±{rng:.0f} A。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; {sens * 1000:.0f} mV/A, ±{rng:.0f} A.", md=case.text("8_总结.md", review), tools=tools("circuit", "fct"))
case.write()
print("ok", sim["compare"], mc_pct, cpk_min, fails)
