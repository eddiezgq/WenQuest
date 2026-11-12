"""第 161f 轮：电路板厂案例 B——编码器读头板 ENC-RD：光电流 → 跨阻放大 → 正余弦 1 Vpp；细分误差预算、ngspice、容差，到贴片与功能测试。

    python3 tools/cases/pcb_b.py

电路仿真用数字工厂“电路分析”同一个 ngspice 接口和通用运放模型；码盘线数取传感器厂的编码器误差曲线（sim/enccurve.py）；
元件从零件库选；制造用电路板厂仿真车间（贴片线 + 后段）。输出到 factory/cases/pcb/B/。
"""
from __future__ import annotations

import math
import os
import random
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
from sim import enccurve as EC  # noqa: E402

TOOLS = {
    "circuit": ("电路分析", "Circuit analysis", "/circuit"),
    "enc": ("编码器误差曲线（传感器厂）", "Encoder error curve (sensor plant)", "/enc-curve"),
    "fct": ("功能测试台", "Functional test bench", "/fct"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("pcb", "B", "中等", "编码器读头板：光电流到正余弦信号", "Encoder read-head board: photocurrent to sine/cosine", "ENC-RD",
              "传感器厂的光电编码器要一块读头板：把几微安的光电流放大成 1 Vpp 的正余弦信号。算跨阻、带宽，ngspice 核对；"
              "把幅值、偏置、相位误差换算成细分误差（角秒），蒙特卡洛看 1 % 电阻和光电管不对称留下多少偏置；电路板厂做 50 块、功能测试四项。",
              "The optical encoder of the sensor plant needs a read-head board turning a few microamps of photocurrent into 1 Vpp sine/cosine signals: transimpedance and bandwidth "
              "calculated and checked in ngspice; amplitude, offset and phase errors converted to interpolation error in arc-seconds; Monte Carlo for the offset left by 1 % resistors "
              "and photodiode mismatch; 20 boards built and tested on four items.",
              "tools/cases/pcb_b.py")

RF_P = L.lib_part("A-ELE-R0402", "100K")
CF_P = L.lib_part("A-ELE-C0402", "10P")
CD_P = L.lib_part("A-ELE-C0402", "100N")
BUCK = L.lib_part("A-ELE-SOT", "LMR16006YQ")
CONN = L.lib_part("A-ELE-XH", "6P")
RF, CF = float(RF_P["row"]["r_ohm"]), float(CF_P["row"]["c_f"])
N = EC.LINES
PERIOD_AS = 360 * 3600 / N
I_DC, I_AC = 6e-6, 2.5e-6         # 每个光电管的直流、交流光电流 A（示例，型号待确认）
C_PD = 10e-12                     # 光电管结电容（示例）
JOINT_RPM = 6000 / 100            # 关节输出最高转速（电机 6000 r/min ÷ 减速比 100）
F_MAX = N * JOINT_RPM / 60
TOL = {"enc_amp": (0.8, 1.2), "enc_offset": (-20, 20), "enc_phase": (87, 93), "enc_interp": (0, 40)}

# ================================================================ 1 任务书
brief = f"""# 设计任务书：编码器读头板

**用在哪**　传感器厂的关节绝对值编码器 WQ-ENC17：玻璃码盘增量码道 {N} 线（一个信号周期 360°/{N} = {PERIOD_AS:.0f}″），读头上的光电管阵列给出
正、反相两对光电流（sin+、sin−、cos+、cos−）。读头板放大成差分 1 Vpp 的正余弦信号，编码器的处理器再细分（插值）出 17 位角度。

| 项目 | 要求 | 出处 |
|---|---|---|
| 输出 | 正余弦差分 1 Vpp（0.8–1.2），偏置 ±20 mV，A/B 相位差 90° ± 3° | 电路板厂功能测试公差 |
| 细分误差 | ≤ 40″（峰峰值） | 同上 |
| 最高信号频率 | 关节输出最高 {JOINT_RPM:g} r/min × {N} 线 = **{F_MAX / 1000:.1f} kHz**，幅值掉不超过 1 % | 机器人关节（电机 6000 r/min、减速比 100） |
| 光电流 | 每个光电管直流 {I_DC * 1e6:g} μA、交流幅值 {I_AC * 1e6:g} μA，结电容 {C_PD * 1e12:g} pF（示例） | 光电读头（型号待确认） |
"""
case.step("brief", f"{N} 线（一周期 {PERIOD_AS:.0f}″）；输出 1 Vpp、偏置 ±20 mV、相位 90±3°、细分误差 ≤ 40″；最高 {F_MAX / 1000:.1f} kHz。",
          f"{N} lines ({PERIOD_AS:.0f}″ per period); 1 Vpp, ±20 mV offset, 90±3° phase, ≤ 40″ interpolation error; up to {F_MAX / 1000:.1f} kHz.",
          md=case.text("1_任务书.md", brief), tools=tools("enc"), facts=[("线数", "Lines", N, ""), ("一个信号周期", "Signal period", round(PERIOD_AS), "″")])

# ================================================================ 2 方案
concept = f"""# 方案

| 方案 | 说明 | 取舍 |
|---|---|---|
| 一个光电管 + 跨阻放大 | 简单 | 光电流里的直流（环境光、LED 亮度）全进输出，偏置随温度、老化漂 |
| **正反相两个光电管各一级跨阻放大，再相减** | sin+ − sin−：直流相减抵消，交流加倍 | 多一级；偏置只剩两边不对称的部分 |
| 专用编码器信号调理芯片（清单 IC-ENC-AFE） | 跨阻、相减、自动增益都在片内 | 型号待确认；外围电阻电容决定增益和带宽 |

**选第二种的结构**（专用芯片内部也是这样做的，外接的反馈电阻、电容定增益和带宽——下面按分立结构算，数和芯片外围一样用）。
每一路：跨阻 R_f = {RF / 1000:g} kΩ（零件库 `{RF_P['ref']}`）、并联 C_f = {CF * 1e12:g} pF（`{CF_P['ref']}`）。
"""
case.step("concept", "正反相两个光电管各一级跨阻放大再相减：直流抵消、交流加倍；跨阻 100 kΩ、10 pF（零件库）。",
          "A transimpedance stage for each of the two antiphase photodiodes, then subtract: DC cancels, AC doubles; 100 kΩ and 10 pF from the library.",
          md=case.text("2_方案.md", concept), tools=L.lib_tools([RF_P, CF_P]))

# ================================================================ 3 计算：增益、带宽、细分误差预算
v_pp = 2 * I_AC * RF * 2          # 差分：两路各 ±I_AC·Rf，相减 → 幅值 2·I_AC·Rf，峰峰值 ×2
f_c = 1 / (2 * math.pi * RF * CF)
drop = (1 - 1 / math.sqrt(1 + (F_MAX / f_c) ** 2)) * 100
lag = math.degrees(math.atan(F_MAX / f_c))
amp = v_pp / 2


def interp_pp(offset_v=0.0, amp_ratio=1.0, phase_err_deg=0.0, h3=0.0, n=4096):
    """细分误差峰峰值（″）：数值算 atan2（sin、cos 带偏置、幅值不等、相位误差、三次谐波）减去真实角度"""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    s = amp * (np.sin(th) + h3 * np.sin(3 * th)) + offset_v
    c = amp * amp_ratio * (np.cos(th + math.radians(phase_err_deg)) + h3 * np.cos(3 * th))
    e = np.angle(np.exp(1j * (np.arctan2(s, c) - th)))
    return (e.max() - e.min()) / (2 * np.pi) * PERIOD_AS


bud = [["偏置 20 mV（公差上限）", interp_pp(offset_v=0.020)],
       ["两路幅值差 2 %", interp_pp(amp_ratio=1.02)],
       ["相位误差 3°（公差上限）", interp_pp(phase_err_deg=3.0)],
       ["三次谐波 1 %（码盘、光学，示例）", interp_pp(h3=0.01)],
       ["全部同时取上限", interp_pp(offset_v=0.020, amp_ratio=1.02, phase_err_deg=3.0, h3=0.01)]]
calcmd = f"""# 计算

## 增益与带宽

- 差分输出峰峰值 = 2 × (2 · I_ac · R_f) = 2 × 2 × {I_AC * 1e6:g} μA × {RF / 1000:g} kΩ = **{v_pp:.2f} Vpp**（要求 0.8–1.2）
- 每路直流 I_dc · R_f = {I_DC * RF:.2f} V，两路相减抵消
- 带宽 f_c = 1 / (2π · R_f · C_f) = **{f_c / 1000:.0f} kHz**；最高信号 {F_MAX / 1000:.1f} kHz 时幅值掉 {drop:.4f} %、相位滞后 {lag:.2f}°（两路一样，不影响 A/B 相位差）
- C_f 还管稳定：光电管结电容 {C_PD * 1e12:g} pF 在反相输入端，没有 C_f 跨阻放大器会振荡

## 细分误差预算（一个信号周期 {PERIOD_AS:.0f}″）

处理器用 atan2(sin, cos) 算周期内的角度。信号不理想时算出的角度在每个周期里起伏——这就是细分误差。数值算（每种误差单独、再一起）：

{L.md_table(["误差来源", "细分误差峰峰值 ″"], [[a, f"{b:.1f}"] for a, b in bud])}

规律：偏置让误差每周期起伏一次，幅值差、相位误差每周期两次；**都按电气角算，再除以线数**——{N} 线时 1° 电气角只有 {3600 / N:.2f}″。
读头板的公差全部取上限，细分误差 {bud[-1][1]:.1f}″，在 40″ 以内；剩下的余量留给码盘刻划、间隙（传感器厂）。
"""
case.step("calc", f"差分 {v_pp:.2f} Vpp、带宽 {f_c / 1000:.0f} kHz（{F_MAX / 1000:.1f} kHz 时掉 {drop:.3f} %）；读头板公差全取上限，细分误差 {bud[-1][1]:.1f}″（≤ 40″）。",
          f"{v_pp:.2f} Vpp differential, {f_c / 1000:.0f} kHz bandwidth ({drop:.3f} % drop at {F_MAX / 1000:.1f} kHz); with every board tolerance at its limit, interpolation error {bud[-1][1]:.1f}″ (≤ 40″).",
          md=case.text("3_计算书.md", calcmd), tools=tools("circuit", "enc"),
          facts=[("输出峰峰值", "Output", round(v_pp, 2), "Vpp"), ("带宽", "Bandwidth", round(f_c / 1000), "kHz"), ("最坏细分误差", "Worst-case interpolation error", round(bud[-1][1], 1), "″")])
case.check("calc", "最高信号频率时幅值下降", "Amplitude drop at the highest signal frequency", round(drop, 3), "<=", 1.0, "%", "任务书")
case.check("calc", "读头板公差全取上限的细分误差", "Interpolation error with all board tolerances at limit", round(bud[-1][1], 1), "<=", 40, "″", "功能测试公差")

# ================================================================ 4 仿真：ngspice（一路正弦：sin+ / sin− 两级跨阻 + 相减）
HEAD = "* ENC-RD sine channel (case 161f B)\n.param a0=1e5 gbw=10meg\n" + C.OPAMP + "\nVref ref 0 1.65\n"
TIA = (f"Ip ref np {I_DC:g}\nIpa ref np AC {I_AC:g}\nCdp np ref {C_PD:g}\nRfp np op {RF:g}\nCfp np op {CF:g}\nXp ref np op wqop\n"
       f"In ref nn {I_DC:g}\nIna ref nn AC {-I_AC:g}\nCdn nn ref {C_PD:g}\nRfn nn on {RF:g}\nCfn nn on {CF:g}\nXn ref nn on wqop\nEd dso 0 op on 1\n")
net_ac = HEAD + TIA + f".ac dec 40 100 10meg\n.meas ac g_lf FIND vm(dso) AT=1k\n.meas ac f3db WHEN vdb(dso)={20 * math.log10(2 * I_AC * RF) - 3:.6f} FALL=1\n.end\n"
net_dc = HEAD + TIA + ".dc Vref 1.6 1.7 0.05\n.meas dc off FIND v(dso) AT=1.65\n.end\n"
r_ac = C.run(net_ac)
m = r_ac["meas"]
amp_sim = m["g_lf"]
rnd = random.Random(1622)
offs = []
for _ in range(200):
    n = net_dc
    for el, tol in (("Rfp", 0.01), ("Rfn", 0.01), ("Ip", 0.02), ("In", 0.02)):
        n = C._scale(n, el, 1 + rnd.uniform(-tol, tol))
    offs.append(C.run(n, vectors=False)["meas"]["off"] * 1000)
offs = np.array(offs)
off_out = float(np.mean(np.abs(offs) > 20) * 100)
# 偏置调零后（处理器上电时转一圈记下平均值扣掉）剩的：测量分辨率级，按 2 mV 计（示例）
fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.0))
a = r_ac["plots"][0]["data"]
fr = np.array(a["frequency"])
fr = np.abs(fr[:, 0]) if fr.ndim == 2 else np.abs(fr)
vo = np.array(a["v(dso)"])
mag = np.hypot(vo[:, 0], vo[:, 1])
axs[0].semilogx(fr, 20 * np.log10(mag / mag[0]), color=L.ACCENT)
axs[0].axvline(F_MAX, color=L.OK, ls=":", lw=1)
axs[0].axhline(-3, color=L.MUTED, ls=":", lw=0.8)
axs[0].set_xlabel("频率 / Hz")
axs[0].set_ylabel("相对增益 / dB")
axs[0].set_title(f"带宽 {m['f3db'] / 1000:.0f} kHz（绿线 = 最高信号）", fontsize=9.5)
axs[1].hist(offs, bins=25, color="#8aa4bd")
axs[1].axvspan(-20, 20, color=L.OK, alpha=0.18)
axs[1].set_xlabel("差分偏置 / mV（R ±1 %、光电管 ±2 %）")
axs[1].set_title(f"200 次：{off_out:.0f} % 超 ±20 mV", fontsize=9.5)
th = np.linspace(0, 2 * np.pi, 400)
for off, col, lab in ((0, L.ACCENT, "理想"), (0.08, L.BAD, "偏置 80 mV")):
    axs[2].plot(amp * np.cos(th), amp * np.sin(th) + off, color=col, lw=1, label=lab)
axs[2].set_aspect("equal")
axs[2].set_xlabel("cos / V")
axs[2].set_ylabel("sin / V")
axs[2].set_title("李萨如图：偏置让圆心偏开", fontsize=9.5)
axs[2].legend(fontsize=7.5)
case.fig(fig, "4_ngspice.png")
case.raw("4_正弦通道_ac.cir", net_ac.encode())
simmd = f"""# 仿真：ngspice

一路正弦通道：sin+、sin− 两个光电管（电流源 + 结电容）各接一级跨阻（通用运放，增益带宽积 10 MHz），再相减。网表 `4_正弦通道_ac.cir`。

| 量 | ngspice | 公式 |
|---|---|---|
| 差分幅值（1 kHz） | {amp_sim:.4f} V | {2 * I_AC * RF:.4f} V |
| −3 dB 带宽 | {m['f3db'] / 1000:.0f} kHz | {f_c / 1000:.0f} kHz（R_f C_f；运放也参与） |

## 偏置的蒙特卡洛

两路的 R_f 各 ±1 %（零件库 0402）、两个光电管直流光电流各 ±2 %（示例），200 次：差分偏置标准差 **{offs.std(ddof=1):.0f} mV**，{off_out:.0f} % 超出 ±20 mV。
直流 {I_DC * 1e6:g} μA × {RF / 1000:g} kΩ = {I_DC * RF:.1f} V 很大，两边差 1 % 就是几毫伏到几十毫伏——**相减不能完全抵消，偏置要调**：
专用芯片带偏置微调（出厂功能测试时写入），或者编码器处理器上电转动时自动扣除。功能测试的 ±20 mV 是调过以后的。
"""
case.step("sim", f"ngspice 幅值、带宽与公式一致；1 % 电阻 + 光电管 2 % 让偏置标准差 {offs.std(ddof=1):.0f} mV、{off_out:.0f} % 超差——偏置必须出厂调。",
          f"ngspice amplitude and bandwidth match the formulas; 1 % resistors and 2 % photodiodes give {offs.std(ddof=1):.0f} mV offset spread, {off_out:.0f} % out of tolerance — offset trimming at test is required.",
          md=case.text("4_ngspice仿真.md", simmd), figs=[("4_ngspice.png", "频响、偏置蒙特卡洛、李萨如图", "Frequency response, offset Monte Carlo, Lissajous")],
          files=[("4_正弦通道_ac.cir", "交流网表", "AC netlist")], tools=tools("circuit"),
          facts=[("带宽", "Bandwidth", round(m["f3db"] / 1000), "kHz"), ("未调偏置标准差", "Untrimmed offset std. dev.", round(offs.std(ddof=1)), "mV")])
case.check("sim", "差分幅值：ngspice 与公式相差", "Amplitude: ngspice vs formula", round(abs(amp_sim / (2 * I_AC * RF) - 1) * 100, 2), "<=", 1.0, "%", "公式核对")

# ================================================================ 5 原理图（框图）与元件
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.set_xlim(0, 100)
ax.set_ylim(0, 34)
ax.set_axis_off()


def box(x, y, w, h, t, c="#eef3f8"):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=c, ec=L.INK, lw=0.8))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=8)


box(2, 4, 16, 26, "光电读头\nSNS-OPT\n（型号待确认）\nsin+ sin−\ncos+ cos−")
for i, (y, lab) in enumerate(((24, "sin+"), (18, "sin−"), (12, "cos+"), (6, "cos−"))):
    ax.plot([18, 28], [y + 1, y + 1], color=L.INK, lw=0.8)
    box(28, y - 1, 14, 4, f"跨阻 {RF / 1000:g}k‖{CF * 1e12:g}p", "#fff6d6")
    ax.plot([42, 52], [y + 1, y + 1], color=L.INK, lw=0.8)
box(52, 16, 12, 12, "相减\nsin = (+) − (−)")
box(52, 3, 12, 11, "相减\ncos")
box(70, 4, 14, 24, "信号调理芯片\nIC-ENC-AFE\n（含偏置微调）\n（型号待确认）")
ax.plot([64, 70], [22, 22], color=L.INK, lw=0.8)
ax.plot([64, 70], [8, 8], color=L.INK, lw=0.8)
box(88, 10, 11, 12, "插座\n差分\n1 Vpp")
ax.plot([84, 88], [16, 16], color=L.INK, lw=0.8)
ax.text(50, 0.5, f"示例框图；5 V 由 {BUCK['size']} 降压（零件库）", ha="center", fontsize=7.5, color=L.MUTED)
case.fig(fig, "5_框图.png")
LIBP = [RF_P, CF_P, CD_P, BUCK, CONN]
cadmd = f"""# 原理图（框图）与布局要点

![框图](5_框图.png)

{L.lib_md(LIBP, {RF_P['ref']: "跨阻 ×4", CF_P['ref']: "跨阻并联 ×4", CD_P['ref']: "去耦", BUCK['ref']: "5 V 电源", CONN['ref']: "输出插座（sin±、cos±、5 V、地）"})}

**布局要点**（跨阻放大器的输入是几微安、几百千欧——最怕漏电和耦合）：

1. 光电读头紧贴跨阻放大器，输入线越短越好；输入节点四周铺**保护环**（接参考电压），挡住板面漏电流。
2. 四路完全对称布线（对称才能相减抵消）：sin+ 与 sin−、cos+ 与 cos− 镜像摆放。
3. 降压电源的开关节点远离输入，放在板子另一端，底层铺地隔开。
4. 三防涂覆前彻底清洗：助焊剂残留在 100 kΩ 节点上就是漏电。

> 读头板还没有 KiCad 工程（驱动板、控制器有）；本案例到框图和布局要点为止，KiCad 工程按驱动板的设计描述方式以后补（第 161f 轮细则偏差 D-1）。
"""
case.step("cad", "框图、零件库元件、四条布局要点（保护环、对称、电源远离、清洗）；读头板 KiCad 工程以后补。",
          "Block diagram, library parts and four layout rules (guard ring, symmetry, supply far away, cleaning); the KiCad project of this board is to follow.",
          md=case.text("5_框图与布局.md", cadmd), figs=[("5_框图.png", "读头板框图", "Read-head board block diagram")], tools=L.lib_tools(LIBP))

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rt_smt = F.ROUTINGS[F.BOMS["SMT-ENC"][0]]
rt_be = F.ROUTINGS[F.BOMS["ENC-RD"][0]]
procmd = f"""# 工艺

贴片板 SMT-ENC（{len(rt_smt)} 道，同驱动板一条线）→ 后段 ENC-RD（{len(rt_be)} 道）。读头板特别要注意的：

| 工序 | 要点 |
|---|---|
| 来料、贴片 | 光电读头 SNS-OPT 是**湿敏元件**（清单备注）：开封后限时贴完，超时要烘烤；回流时窗口面朝上、不能沾助焊剂 |
| 选择焊 | 只有输出插座是通孔 |
| 三防涂覆 | 涂覆前清洗；**光学窗口要遮蔽**，涂上就挡光 |
| 程序烧录 | 写偏置微调值的默认值 |
| 功能测试 | 在标准码盘上转动，测幅值、偏置、相位差、细分误差；偏置先调后测 |
"""
case.step("process", "贴片 + 后段；湿敏的光电读头、涂覆遮蔽光学窗口、功能测试先调偏置再测。",
          "SMT + back end; moisture-sensitive optical sensor, mask the optical window during coating, trim the offset before functional test.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("工序", "Operations", len(rt_smt) + len(rt_be), "")])

# ================================================================ 7 制造
sh = L.run_shop("ENC-RD", 50, "WO-CASE-PCB-B", seed=1623)
rows_q, cpk_min, fails, st = L.shop_table([m_ for m_ in sh["measurements"] if m_["item"] == "ENC-RD"])
makemd = f"""# 制造：50 块读头板

电路板厂仿真车间后段做 50 块 ENC-RD（一个批次；20 块估 Cpk 散布太大）（{sh['hours']:.1f} 小时），功能测试四项：

{L.md_table(["特性", "公差", "块数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}**，最低 Cpk {cpk_min:.2f}。细分误差均值 {st['enc_interp']['mean']:.0f}″——比第 3 步读头板公差全取上限的 {bud[-1][1]:.1f}″ 大，
多出来的来自测试用标准码盘本身和光学（码盘刻划、间隙），不在这块板上。
"""
case.step("make", f"50 块功能测试四项，不合格 {fails}，最低 Cpk {cpk_min:.2f}；细分误差均值 {st['enc_interp']['mean']:.0f}″。",
          f"50 boards, four functional tests, {fails} failures, lowest Cpk {cpk_min:.2f}; mean interpolation error {st['enc_interp']['mean']:.0f}″.",
          md=case.text("7_制造与测试.md", makemd), tools=tools("planner", "operator", "quality", "fct"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", round(cpk_min, 2), "")])
case.check("make", "功能测试不合格项", "Functional-test failures", fails, "==", 0, "", "功能测试台")
case.check("make", "最低 Cpk", "Lowest Cpk", round(cpk_min, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **微安级信号先看对称**：正反相相减抵消了直流，但抵消不完——偏置要在出厂时调。
2. **误差要换算到用户关心的单位**：20 mV 偏置、3° 相位，到编码器就是几角秒；{N} 线把电气角缩小了 {N} 倍。
3. **一块板只管自己那一份**：细分误差的大头在码盘和光学（传感器厂），读头板的公差设计让它只占一小部分。

## 留给学生的问题

1. 把 C_f 换成零件库的 220 pF：带宽、最高转速时的幅值、噪声各怎么变？
2. 码盘换成 4096 线：信号频率、细分误差（角秒）怎么变？
3. 在传感器厂“编码器误差曲线”页找细分误差：它和本案例算的是不是一回事？

相关：数字工厂“电路分析”“功能测试台”；传感器厂“编码器误差曲线”；电路板厂实验 37、39；案例 A（相电流采样）、C（驱动板整板）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；{v_pp:.1f} Vpp、带宽 {f_c / 1000:.0f} kHz、最坏细分误差 {bud[-1][1]:.1f}″。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; {v_pp:.1f} Vpp, {f_c / 1000:.0f} kHz, worst-case interpolation error {bud[-1][1]:.1f}″.",
          md=case.text("8_总结.md", review), tools=tools("circuit", "enc"))
case.write()
print("ok", v_pp, f_c, drop, bud, m, offs.std(), off_out, cpk_min, fails)
