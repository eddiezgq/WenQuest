"""第 161e 轮：传感器厂案例 A——关节扭矩传感器 WQ-TS 的信号链：应变全桥 → 前置放大 → 抗混叠滤波 → 24 位 ADC。

    python3 tools/cases/sensor_a.py

电路仿真用数字工厂“电路分析”同一个 ngspice 接口（cae/circuit.py 的 run、同一个通用运放模型）；电桥输出取案例 B 的有限元结果；
元件尽量从问渠零件库选；制造用传感器厂仿真车间（扭矩传感器线）。输出到 factory/cases/sensor/A/。
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-sensor.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
import tslib as T  # noqa: E402
from cae import circuit as C  # noqa: E402

TOOLS = {
    "circuit": ("电路分析", "Circuit analysis", "/circuit"),
    "inst": ("虚拟仪器（扭矩传感器）", "Virtual instruments (torque sensor)", "/instruments"),
    "pcb": ("电路板设计", "PCB design", "/pcb-design"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("sensor", "A", "简单", "扭矩传感器信号链：电桥、放大、滤波、模数转换", "Torque-sensor signal chain: bridge, amplifier, filter, ADC", "WQ-TS 信号调理 SIG-TS",
              "把应变全桥几毫伏的信号变成控制器能用的数：比较三种信号链，算增益、带宽和噪声，用 ngspice 仿真增益、频响和元件容差——"
              "发现分立电阻做差分级会让零点随供桥电压漂、应变片阻值公差会让零点大到满量程的几十个百分点；传感器厂做 20 台看零点。",
              "Turning a few millivolts from a strain-gauge bridge into a number the controller can use: three signal chains compared; gain, bandwidth and noise calculated; "
              "ngspice for gain, frequency response and component tolerances — a discrete difference stage lets the zero drift with the excitation voltage, and gauge tolerance "
              "puts the bridge zero at tens of per cent of full scale; 20 sensors built and their zero checked.",
              "tools/cases/sensor_a.py")

# 电桥输出：案例 B 的有限元定稿值（先读 B 的结果；没有就当场算一遍）
bj = ROOT / "factory" / "cases" / "sensor" / "B" / "case.json"
MV = None
if bj.exists():
    for st_ in json.loads(bj.read_text(encoding="utf-8"))["steps"]:
        for f in st_.get("facts", []):
            if f["name"] == "定稿输出":
                MV = float(str(f["value"]).replace(",", ""))
if MV is None:
    MV = abs(T.fea(T.GEOM, "torque", T.T_FS)["mv_v"])
V_FS = T.V_EX * MV / 1000                 # 满量程电桥输出 V
RG_PART = L.lib_part("A-ELE-R0402", "120R")
RF_PART = L.lib_part("A-ELE-R0402", "10K")
RA_PART = L.lib_part("A-ELE-R0402", "1K")
CD_PART = L.lib_part("A-ELE-C0402", "100N")
CC_PART = L.lib_part("A-ELE-C0402", "10N")
RF, RG = float(RF_PART["row"]["r_ohm"]), float(RG_PART["row"]["r_ohm"])
GAIN = 1 + 2 * RF / RG
ADC_FS = 2.5                              # 24 位 Σ-Δ ADC 差分输入 ±2.5 V（基准取供桥电压的一半，比例测量）
NOISE_EN = 10e-9                          # 前置运放输入电压噪声 V/√Hz（零漂移精密运放的量级，示例；型号待确认）
ODR = 1000                                # ADC 输出 1 kHz（关节力矩环）
KB = 1.380649e-23

# ================================================================ 1 任务书
brief = f"""# 设计任务书：扭矩传感器的信号调理

**是什么**　WQ-TS 的弹性体上贴 4 片剪切型双栅应变片，组成一个全桥（每臂 {T.R_ARM:g} Ω，案例 B）。额定 ±{T.T_FS:g} N·m 时电桥只输出
**{MV:.3f} mV/V × {T.V_EX:g} V = {V_FS * 1000:.2f} mV**。信号调理板 SIG-TS 要把它放大、滤波、转成数字，送给关节控制器做力矩环。

| 项目 | 要求 | 出处 |
|---|---|---|
| 输入 | 全桥 {T.R_ARM:g} Ω，{MV:.3f} mV/V（额定），供桥 {T.V_EX:g} V | 案例 B 有限元；SIG-TS 5 V 基准 |
| 量程 | ±{T.T_FS:g} N·m，过载 {T.T_OVL:g} N·m 不削顶 | 清单 WQ-TS |
| 输出 | 24 位 ADC，{ODR} 次/秒 | 关节力矩环 1 kHz |
| 带宽 | −3 dB ≥ 500 Hz（力矩环要看得到） | 本案例设定 |
| 噪声 | 峰峰值 ≤ 0.05 %FS（{ODR} 次/秒时） | 本案例设定（终检非线性 ≤ 0.3 %FS 的六分之一） |
| 零点 | 终检零点输出 ±0.5 %FS | 传感器厂终检公差 |

满量程 {V_FS * 1000:.2f} mV，0.05 %FS 就是 **{V_FS * 0.05 / 100 * 1e6:.1f} μV**——比一根导线两端的热电势还小。这个案例的难点全在“小”。
"""
case.step("brief", f"电桥满量程只有 {V_FS * 1000:.2f} mV；要 24 位、1 kHz、带宽 ≥ 500 Hz、噪声峰峰值 ≤ 0.05 %FS（{V_FS * 0.05 / 100 * 1e6:.1f} μV）。",
          f"The bridge gives only {V_FS * 1000:.2f} mV at full scale; 24-bit, 1 kHz, bandwidth ≥ 500 Hz, peak-to-peak noise ≤ 0.05 %FS ({V_FS * 0.05 / 100 * 1e6:.1f} μV).",
          md=case.text("1_任务书.md", brief), tools=tools("inst"),
          facts=[("满量程电桥输出", "Full-scale bridge output", round(V_FS * 1000, 2), "mV"), ("噪声要求", "Noise limit", round(V_FS * 0.05 / 100 * 1e6, 1), "μV p-p")])

# ================================================================ 2 方案
concept = f"""# 方案：三种信号链

| 方案 | 做法 | 好处 | 问题 |
|---|---|---|---|
| ① 电桥直接接带可编程增益的 24 位 ADC | ADC 内部放大 64–128 倍 | 元件最少 | 内部放大器噪声大；输入阻抗、抗混叠滤波受 ADC 限制 |
| ② 三运放仪表放大器 + 24 位 ADC | 前两级放大、第三级差分转单端 | 教科书做法 | 第三级（差分级）靠四个电阻相等来抑制共模——**分立电阻做不到** |
| ③ **两运放前置级（差分进、差分出）+ RC 抗混叠 + 差分输入 24 位 ADC** | 前置级只放大差分信号、共模原样通过；共模交给 ADC 的差分输入去抑制 | 增益只由一个电阻定；共模抑制不靠电阻匹配 | 两路运放要对称布线 |

**选 ③。** 关键在于：电桥两个输出端都在 {T.V_EX / 2:g} V 左右（共模电压），信号只是两者之差的几毫伏。方案 ② 的差分级用四个 1 % 电阻时，
共模电压会按电阻误差漏到输出（第 4 步用蒙特卡洛量一量有多大）。方案 ③ 的前置级：

  差分增益 G = 1 + 2·R_F / R_G，　共模增益 = 1（与电阻是否匹配无关）

**比例测量**：ADC 的基准取自同一个 {T.V_EX:g} V 供桥电压（分压到 {ADC_FS:g} V），供桥电压慢慢漂，电桥输出和基准一起漂，读数不变。
"""
case.step("concept", "三种信号链比较，选两运放前置级 + RC 抗混叠 + 差分 24 位 ADC：增益只由一个电阻定，共模抑制不靠电阻匹配；比例测量。",
          "Three signal chains compared; a two-op-amp front end + RC anti-alias filter + differential 24-bit ADC chosen: one resistor sets the gain, CMRR does not rely on resistor matching; ratiometric.",
          md=case.text("2_方案.md", concept), tools=tools("circuit"))

# ================================================================ 3 计算
v_out_fs = V_FS * GAIN
v_out_ovl = v_out_fs * T.T_OVL / T.T_FS
RFILT = float(RA_PART["row"]["r_ohm"])
CD, CC = float(CD_PART["row"]["c_f"]), float(CC_PART["row"]["c_f"])
f_diff = 1 / (2 * math.pi * 2 * RFILT * (CD + CC / 2))
f_cm = 1 / (2 * math.pi * RFILT * CC)
e_bridge = math.sqrt(4 * KB * 300 * T.R_ARM)                 # 电桥输出电阻 = 一个臂（两个半桥各 R/2，串起来 R）
e_amp = NOISE_EN * math.sqrt(2)
e_tot = math.sqrt(e_bridge ** 2 + e_amp ** 2)
nbw = min(f_diff * math.pi / 2, ODR / 2 * 1.1)               # 噪声带宽：一阶 RC 的 π/2·f_c，ADC 数字滤波截到约 ODR/2
v_rms = e_tot * math.sqrt(nbw)
pp_fs = 6.6 * v_rms / V_FS * 100
lsb_in = 2 * ADC_FS / 2 ** 24 / GAIN
i_ex = T.V_EX / T.R_ARM
p_grid = (T.V_EX / 4) ** 2 / T.R_GRID
calcmd = f"""# 计算：增益、量程、滤波、噪声

## 增益（零件库电阻）

R_F 用零件库 `{RF_PART['ref']}`（{RF:g} Ω），R_G 用 `{RG_PART['ref']}`（{RG:g} Ω）：

  G = 1 + 2 × {RF:g} / {RG:g} = **{GAIN:.1f}**

| | 电桥 | 前置级输出（差分） | ADC 量程 ±{ADC_FS:g} V 的占用 |
|---|---|---|---|
| 额定 {T.T_FS:g} N·m | {V_FS * 1000:.2f} mV | {v_out_fs:.3f} V | {v_out_fs / ADC_FS:.0%} |
| 过载 {T.T_OVL:g} N·m | {V_FS * 1.5 * 1000:.2f} mV | {v_out_ovl:.3f} V | {v_out_ovl / ADC_FS:.0%}（不削顶） |

两路输出都围绕共模 {T.V_EX / 2:g} V 摆动 ±{v_out_ovl / 2:.2f} V，单 5 V 供电的轨到轨运放够用。

## 抗混叠 RC（零件库电阻、电容）

两个 `{RA_PART['ref']}` 串在两路上，差分电容 `{CD_PART['ref']}`，两路各一个对地共模电容 `{CC_PART['ref']}`：

- 差分截止 f = 1 / (2π · 2R · (C_d + C_c/2)) = **{f_diff:.0f} Hz**（≥ 500 Hz ✓；ADC 输出 {ODR} 次/秒，奈奎斯特 {ODR / 2:g} Hz 之上靠 ADC 的数字滤波）
- 共模截止 1 / (2π·R·C_c) = {f_cm / 1000:.1f} kHz。差分电容要比共模电容大 10 倍以上：两个共模电容的误差会把共模噪声变成差分噪声，大差分电容把它压住。

## 噪声预算（折算到电桥输出端）

| 来源 | 噪声密度 |
|---|---|
| 电桥电阻热噪声 √(4kTR)，R = {T.R_ARM:g} Ω | {e_bridge * 1e9:.1f} nV/√Hz |
| 两个前置运放 {NOISE_EN * 1e9:g} nV/√Hz × √2（示例值） | {e_amp * 1e9:.1f} nV/√Hz |
| 合计 | **{e_tot * 1e9:.1f} nV/√Hz** |

噪声带宽约 {nbw:.0f} Hz → 有效值 {v_rms * 1e6:.2f} μV，峰峰值 ≈ 6.6 × 有效值 = {6.6 * v_rms * 1e6:.2f} μV = **{pp_fs:.3f} %FS**（要求 ≤ 0.05）。
ADC 的 1 个最低位折算到电桥只有 {lsb_in * 1e9:.2f} nV——24 位的“位数”不是瓶颈，**前置级的噪声才是**；增益放在 ADC 前面，ADC 自己的噪声就被除以 {GAIN:.0f}。

## 应变片自热

供桥电流 {T.V_EX:g} V / {T.R_ARM:g} Ω = {i_ex * 1000:.1f} mA，每个栅 {p_grid * 1000:.1f} mW。小栅贴在不锈钢上散热好，这个功率可以接受；
供桥电压再高，输出大了，但自热会让零点随通电时间漂。
"""
case.step("calc", f"增益 {GAIN:.1f}（零件库 R_G {RG:g} Ω）；额定 {v_out_fs:.2f} V、过载 {v_out_ovl:.2f} V 不削顶；RC 截止 {f_diff:.0f} Hz；噪声峰峰值 {pp_fs:.3f} %FS。",
          f"Gain {GAIN:.1f} (library R_G {RG:g} Ω); {v_out_fs:.2f} V rated, {v_out_ovl:.2f} V overload without clipping; RC cut-off {f_diff:.0f} Hz; noise {pp_fs:.3f} %FS p-p.",
          md=case.text("3_计算书.md", calcmd), tools=tools("circuit") + L.lib_tools([RF_PART, RG_PART, RA_PART, CD_PART, CC_PART]),
          facts=[("增益", "Gain", round(GAIN, 1), ""), ("差分截止频率", "Differential cut-off", round(f_diff), "Hz"), ("噪声峰峰值", "Noise p-p", round(pp_fs, 3), "%FS")])
case.check("calc", "过载时 ADC 量程占用", "ADC range used at overload", round(v_out_ovl / ADC_FS * 100), "<=", 90, "%", "留 10 % 余量放零点")
case.check("calc", "噪声峰峰值", "Noise peak-to-peak", round(pp_fs, 3), "<=", 0.05, "%FS", "任务书")

# ================================================================ 4 仿真：ngspice
K = 1.0 / T.T_FS          # 每 N·m 的相对输出（乘 V_FS）
HEAD = "* WQ-TS signal chain (case 161e A)\n.param a0=1e6 gbw=1meg\n" + C.OPAMP + "\n"
BRIDGE = (f"Vt t 0 DC 0 AC 1\nVex e 0 DC {T.V_EX:g}\n"
          f"Bsp a 0 V=V(e)/2*(1+{MV / 1000:.9g}*V(t)*{K:.9g})\nRsp a sp {T.R_ARM / 2:g}\n"
          f"Bsn b 0 V=V(e)/2*(1-{MV / 1000:.9g}*V(t)*{K:.9g})\nRsn b sn {T.R_ARM / 2:g}\n")
FRONT = (f"Xa sp n1 oa wqop\nRa oa n1 {RF:g}\nRg n1 n2 {RG:g}\nRb ob n2 {RF:g}\nXb sn n2 ob wqop\n"
         f"Rf1 oa fa {RFILT:g}\nRf2 ob fb {RFILT:g}\nCd fa fb {CD:g}\nCc1 fa 0 {CC:g}\nCc2 fb 0 {CC:g}\nEod od 0 fa fb 1\n")
net_dc = HEAD + BRIDGE + FRONT + (f".dc Vt {-T.T_OVL:g} {T.T_OVL:g} 5\n.meas dc vfs FIND v(od) AT={T.T_FS:g}\n.meas dc vovl FIND v(od) AT={T.T_OVL:g}\n"
                                  f".meas dc vzero FIND v(od) AT=0\n.meas dc vcm FIND v(fa) AT=0\n.end\n")
g_lf = 20 * math.log10(V_FS * K * GAIN)
net_ac = HEAD + BRIDGE + FRONT + f".ac dec 40 1 1meg\n.meas ac g_lf FIND vdb(od) AT=10\n.meas ac f3db WHEN vdb(od)={g_lf - 3:.6f} FALL=1\n.end\n"
r_dc = C.run(net_dc)
r_ac = C.run(net_ac)
m_dc, m_ac = r_dc["meas"], r_ac["meas"]
gain_err = abs(m_dc["vfs"] / v_out_fs - 1) * 100
dc_plot = r_dc["plots"][0]["data"]
tt = np.array(dc_plot.get("v-sweep") or dc_plot.get("vt-sweep") or next(v for k_, v in dc_plot.items() if "sweep" in k_.lower()))
vo = np.array(dc_plot["v(od)"])
fit = np.polyfit(tt, vo, 1)
lin_dev = np.max(np.abs(vo - np.polyval(fit, tt))) / v_out_fs * 100

# 蒙特卡洛 1：前置级电阻 1 %（零件库 0402 的公差）→ 满量程增益散布
rnd = random.Random(1615)
tol = float(RF_PART["row"]["tol_pct"]) / 100
mc_gain = []
for _ in range(60):
    n = net_dc
    for el in ("Ra", "Rb", "Rg"):
        n = C._scale(n, el, 1 + rnd.uniform(-tol, tol))
    mc_gain.append(C.run(n, vectors=False)["meas"]["vfs"])
mc_gain = np.array(mc_gain)
gain_spread = (mc_gain.max() - mc_gain.min()) / 2 / mc_gain.mean() * 100

# 蒙特卡洛 2：如果用方案 ②（三运放，差分级用 4 个 1 % 电阻）——零力矩时的输出（共模漏过来）
DIFF = f"Rd1 oa m {RF:g}\nRd2 m out {RF:g}\nRd3 ob p {RF:g}\nRd4 p ref {RF:g}\nXd p m out wqop\nVref ref 0 {T.V_EX / 2:g}\nEo3 o3 0 out ref 1\n"
# 方案 ② 的差分级参考端接一个独立的 2.5 V 基准；供桥电压漂 ±5 %（共模跟着漂 ±125 mV）时，零力矩输出变多少
EX_LO, EX_HI = 0.95 * T.V_EX, 1.05 * T.V_EX
net_3op = HEAD + BRIDGE + FRONT + DIFF + f".dc Vex {EX_LO:g} {EX_HI:g} {EX_HI - EX_LO:g}\n.meas dc zl FIND v(o3) AT={EX_LO:g}\n.meas dc zh FIND v(o3) AT={EX_HI:g}\n.end\n"
mc_3op = []
for _ in range(60):
    n = net_3op
    for el in ("Rd1", "Rd2", "Rd3", "Rd4"):
        n = C._scale(n, el, 1 + rnd.uniform(-tol, tol))
    mm = C.run(n, vectors=False)["meas"]
    mc_3op.append((mm["zh"] - mm["zl"]) / v_out_fs * 100)
mc_3op = np.array(mc_3op)
net_ours = HEAD + BRIDGE + FRONT + f".dc Vex {EX_LO:g} {EX_HI:g} {EX_HI - EX_LO:g}\n.meas dc zl FIND v(od) AT={EX_LO:g}\n.meas dc zh FIND v(od) AT={EX_HI:g}\n.end\n"
mc_ours = []
for _ in range(30):
    n = net_ours
    for el in ("Ra", "Rb", "Rg", "Rf1", "Rf2"):
        n = C._scale(n, el, 1 + rnd.uniform(-tol, tol))
    mm = C.run(n, vectors=False)["meas"]
    mc_ours.append((mm["zh"] - mm["zl"]) / v_out_fs * 100)
mc_ours = np.array(mc_ours)

# 蒙特卡洛 3：应变片阻值公差 → 电桥零点（8 个栅，真实电阻电桥）
GTOL = 0.003            # 应变片阻值公差 ±0.3 %（常见箔式应变片的量级，示例；型号待确认）
net_br = (f"* real 8-grid bridge, zero output\nVex e 0 {T.V_EX:g}\n"
          f"R1a e x1 {T.R_GRID:g}\nR1b x1 sp {T.R_GRID:g}\nR2a sp x2 {T.R_GRID:g}\nR2b x2 0 {T.R_GRID:g}\n"
          f"R3a e x3 {T.R_GRID:g}\nR3b x3 sn {T.R_GRID:g}\nR4a sn x4 {T.R_GRID:g}\nR4b x4 0 {T.R_GRID:g}\nEz bz 0 sp sn 1\n"
          f".dc Vex {T.V_EX - 0.1:g} {T.V_EX + 0.1:g} 0.1\n.meas dc vz FIND v(bz) AT={T.V_EX:g}\n.end\n")
mc_zero = []
for _ in range(200):
    n = net_br
    for el in ("R1a", "R1b", "R2a", "R2b", "R3a", "R3b", "R4a", "R4b"):
        n = C._scale(n, el, 1 + rnd.uniform(-GTOL, GTOL))
    mc_zero.append(C.run(n, vectors=False)["meas"]["vz"] / V_FS * 100)
mc_zero = np.array(mc_zero)
zero_sd = mc_zero.std(ddof=1)
zero_v_out = 3 * zero_sd / 100 * v_out_fs

fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.0))
fr = np.array(r_ac["plots"][0]["data"]["frequency"])
fr = np.abs(fr[:, 0]) if fr.ndim == 2 else np.abs(fr)
va = np.array(r_ac["plots"][0]["data"]["v(od)"])
vd = va[:, 0] + 1j * va[:, 1]
axs[0].semilogx(fr, 20 * np.log10(np.abs(vd) / np.abs(vd[0])), color=L.ACCENT)
axs[0].axhline(-3, color=L.MUTED, ls=":", lw=0.8)
axs[0].axvline(m_ac["f3db"], color=L.BAD, ls=":", lw=0.8)
axs[0].set_xlabel("频率 / Hz")
axs[0].set_ylabel("相对增益 / dB")
axs[0].set_title(f"频响：−3 dB 在 {m_ac['f3db']:.0f} Hz", fontsize=9.5)
axs[0].set_ylim(-40, 3)
axs[1].hist(mc_3op, bins=15, color="#8aa4bd", label="方案②：差分级 4 个 1 % 电阻")
axs[1].axvline(0, color=L.ACCENT, lw=2, label="方案③：≈ 0")
axs[1].set_xlabel("供桥 ±5 % 时零点的变化 / %FS")
axs[1].set_title("共模变化漏成零点漂移", fontsize=9.5)
axs[1].legend(fontsize=7.5)
axs[2].hist(mc_zero, bins=20, color="#8aa4bd")
axs[2].axvspan(-0.5, 0.5, color=L.OK, alpha=0.25, label="终检 ±0.5 %FS")
axs[2].set_xlabel("电桥零点 / %FS（应变片 ±0.3 %）")
axs[2].set_title("应变片阻值公差 → 电桥零点", fontsize=9.5)
axs[2].legend(fontsize=7.5)
case.fig(fig, "4_ngspice仿真.png")
case.raw("4_信号链_dc.cir", net_dc.encode())
case.raw("4_信号链_ac.cir", net_ac.encode())

simmd = f"""# 仿真：ngspice（数字工厂“电路分析”同一个接口、同一个通用运放模型）

电桥用戴维南等效（两个输出端各 {T.R_ARM / 2:g} Ω，电压随力矩线性变化）；运放开环 120 dB、增益带宽积 1 MHz（通用模型，示例参数）。网表：`4_信号链_dc.cir`、`4_信号链_ac.cir`，可以贴进“电路分析”页的网表框直接跑。

## 增益、线性、带宽

| 量 | ngspice | 公式 |
|---|---|---|
| 额定 {T.T_FS:g} N·m 输出 | {m_dc['vfs']:.4f} V | {v_out_fs:.4f} V（差 {gain_err:.2f} %，运放有限开环增益） |
| 过载 {T.T_OVL:g} N·m 输出 | {m_dc['vovl']:.4f} V | {v_out_ovl:.4f} V |
| 零力矩输出 / 共模 | {m_dc['vzero'] * 1e6:.2f} μV / {m_dc['vcm']:.3f} V | 0 / {T.V_EX / 2:g} V |
| 偏离直线（−{T.T_OVL:g}…+{T.T_OVL:g} N·m） | {lin_dev:.1e} %FS | — |
| −3 dB 带宽 | **{m_ac['f3db']:.0f} Hz** | {f_diff:.0f} Hz（RC；运放闭环带宽 ≈ 1 MHz / {GAIN:.0f} = {1e6 / GAIN / 1000:.1f} kHz 也参与） |

电路部分是线性的——传感器的非线性只来自弹性体和应变片（案例 B、C）。

## 元件容差（蒙特卡洛，零件库电阻 ±{tol * 100:g} %）

- **增益**：R_F、R_G 各 ±1 %，60 次，满量程输出散布 ±{gain_spread:.2f} %——是固定的比例误差，案例 C 的砝码标定一次修掉。
- **共模变化漏成零点漂移**：方案 ② 的差分级参考端接独立的 2.5 V 基准、用四个 1 % 电阻；供桥电压漂 ±5 %（共模漂 ±{T.V_EX * 0.025 * 1000:.0f} mV）时，
  零力矩输出变化 {mc_3op.min():+.2f} … {mc_3op.max():+.2f} %FS（标准差 {mc_3op.std(ddof=1):.2f} %FS）——共模恰好等于参考电压时看不出来，一漂就露馅；
  方案 ③（选定）在同样 1 % 电阻下变化最大 {np.abs(mc_ours).max():.1e} %FS（共模原样通过，交给差分 ADC）。**这就是第 2 步选 ③ 的原因，仿真把它量出来了。**

## 应变片阻值公差 → 电桥零点

8 个栅各 ±{GTOL * 100:g} %（示例），真实电阻电桥 200 次：零点标准差 **{zero_sd:.0f} %FS**，最大 {np.abs(mc_zero).max():.0f} %FS。
应变片阻值的微小差别（0.3 % = 1 Ω）和满量程信号（{MV:.2f} mV/V 相当于阻值变化 {MV / 1000 * 100:.2f} %）是一个量级——**不调零根本不能用**：
3σ 零点放大后 {zero_v_out:.2f} V，ADC 量程 ±{ADC_FS:g} V，会挤掉过载余量甚至削顶。所以零点必须在电桥里（放大之前）用补偿电阻调平（清单 RES-COMP，案例 C 的“温度补偿”工序）。
"""
case.step("sim", f"ngspice：增益与公式差 {gain_err:.2f} %、带宽 {m_ac['f3db']:.0f} Hz；分立差分级在供桥漂 ±5 % 时零点变化达 {np.abs(mc_3op).max():.2f} %FS；应变片 ±0.3 % 让电桥零点标准差 {zero_sd:.0f} %FS，必须先调零。",
          f"ngspice: gain within {gain_err:.2f} % of the formula, bandwidth {m_ac['f3db']:.0f} Hz; a discrete difference stage shifts the zero by up to {np.abs(mc_3op).max():.2f} %FS for ±5 % excitation drift; ±0.3 % gauges give a {zero_sd:.0f} %FS bridge-zero spread, so zero balancing is mandatory.",
          md=case.text("4_ngspice仿真.md", simmd), figs=[("4_ngspice仿真.png", "频响、两种方案的零点、应变片公差引起的电桥零点", "Frequency response, zero offset of two chains, bridge zero from gauge tolerance")],
          files=[("4_信号链_dc.cir", "直流扫描网表", "DC sweep netlist"), ("4_信号链_ac.cir", "交流网表", "AC netlist")], tools=tools("circuit"),
          facts=[("带宽", "Bandwidth", round(m_ac["f3db"]), "Hz"), ("增益与公式差", "Gain vs formula", round(gain_err, 2), "%"), ("电桥零点标准差", "Bridge-zero std. dev.", round(zero_sd), "%FS")])
case.check("sim", "增益：ngspice 与公式相差", "Gain: ngspice vs formula", round(gain_err, 2), "<=", 0.5, "%", "公式核对")
case.check("sim", "−3 dB 带宽", "−3 dB bandwidth", round(m_ac["f3db"]), ">=", 500, "Hz", "任务书")
case.check("sim", "选定方案：供桥 ±5 % 时零点变化（1 % 电阻）", "Chosen chain: zero shift for ±5 % excitation (1 % resistors)", float(f"{np.abs(mc_ours).max():.2g}"), "<=", 0.01, "%FS", "蒙特卡洛")

# ================================================================ 5 原理图与元件清单
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.set_xlim(0, 100)
ax.set_ylim(0, 40)
ax.set_axis_off()


def box(x, y, w, h, t, c="#eef3f8"):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=c, ec=L.INK, lw=0.8))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=8)


# 电桥（菱形）
cx, cy, r = 12, 20, 9
pts = [(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)]
for i in range(4):
    (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % 4]
    ax.plot([x0, x1], [y0, y1], color=L.INK, lw=1)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ax.text(cx + (mx - cx) * 1.55, cy + (my - cy) * 1.55, ["臂1", "臂2", "臂4", "臂3"][i], fontsize=7, ha="center", va="center", color=L.ACCENT)
ax.text(cx, cy + r + 1.5, f"E+ {T.V_EX:g} V", ha="center", fontsize=7.5)
ax.text(cx, cy - r - 2.5, "E−", ha="center", fontsize=7.5)
ax.text(cx, cy, f"{T.R_ARM:g} Ω\n× 4", ha="center", va="center", fontsize=7)
ax.plot([cx + r, 30], [cy, 28], color=L.INK, lw=0.8)
ax.plot([cx - r, cx - r, 28, 30], [cy, 4, 4, 12], color=L.INK, lw=0.8)
ax.text(24, 29, "S+", fontsize=7.5)
ax.text(24, 5, "S−", fontsize=7.5)
box(30, 22, 12, 9, "运放 A\n（同相）")
box(30, 7, 12, 9, "运放 B\n（同相）")
box(32, 16.5, 8, 4, f"R_G {RG:g} Ω", "#fff6d6")
ax.text(43, 31.5, f"R_F {RF:g} Ω ×2：G = {GAIN:.1f}", fontsize=7.5)
ax.plot([42, 52], [26.5, 26.5], color=L.INK, lw=0.8)
ax.plot([42, 52], [11.5, 11.5], color=L.INK, lw=0.8)
box(52, 24, 7, 5, f"{RFILT / 1000:g} kΩ", "#fff6d6")
box(52, 9, 7, 5, f"{RFILT / 1000:g} kΩ", "#fff6d6")
ax.plot([59, 66], [26.5, 26.5], color=L.INK, lw=0.8)
ax.plot([59, 66], [11.5, 11.5], color=L.INK, lw=0.8)
ax.plot([62, 62], [11.5, 26.5], color=L.INK, lw=0.8)
box(60, 16, 4, 6, "", "#fff6d6")
ax.text(59.5, 19, f"C_d\n{CD * 1e9:g} nF", fontsize=6.5, ha="right", va="center")
ax.text(52, 33, f"C_c {CC * 1e9:g} nF ×2 对地", fontsize=7)
box(66, 8, 14, 22, f"24 位 Σ-Δ ADC\n差分输入 ±{ADC_FS:g} V\n基准 = 供桥/2\n（比例测量）")
ax.plot([80, 85], [19, 19], color=L.INK, lw=0.8)
box(85, 12, 13, 14, "MCU\nSTM32G431\n→ CAN\n（MCP2562）")
ax.text(50, 1, "示例原理图（框图级）；运放、ADC 型号待确认", ha="center", fontsize=7.5, color=L.MUTED)
case.fig(fig, "5_原理图.png")

LIBP = [RF_PART, RG_PART, RA_PART, CD_PART, CC_PART, L.lib_part("A-ELE-C0402", "100N"), L.lib_part("A-ELE-SOT", "AMS1117-5.0"),
        L.lib_part("A-ELE-LQFP48", "STM32G431CBT6"), L.lib_part("A-ELE-SOIC8", "MCP2562-E-SN"), L.lib_part("A-ELE-XH", "5P"), L.lib_part("A-ELE-XH", "4P")]
LIBP = list({p["ref"]: p for p in LIBP}.values())
cadmd = f"""# 原理图与元件清单

![原理图](5_原理图.png)

## 用到的零件库元件

{L.lib_md(LIBP, {RF_PART['ref']: "R_F ×2（前置级反馈）", RG_PART['ref']: f"R_G ×1（定增益 {GAIN:.1f}）", RA_PART['ref']: "抗混叠 R ×2", CD_PART['ref']: "差分电容 C_d ×1；电源去耦 ×6",
                  CC_PART['ref']: "共模电容 C_c ×2", "A-ELE-SOT/AMS1117-5.0": "5 V 稳压（供桥 + 模拟电源）", "A-ELE-LQFP48/STM32G431CBT6": "读 ADC、温度补偿表、CAN 输出",
                  "A-ELE-SOIC8/MCP2562-E-SN": "CAN 收发器", "A-ELE-XH/5P": "电桥插座（E+、E−、S+、S−、屏蔽）", "A-ELE-XH/4P": "输出插座（电源、CAN）"})}

## 零件库里没有的（写通用类型，型号待确认）

| 位号 | 类型 | 要求 |
|---|---|---|
| U1 | 双路零漂移精密运放 | 输入噪声 ≤ 10 nV/√Hz、失调漂移 ≤ 0.05 μV/℃、轨到轨输出 |
| U2 | 24 位 Σ-Δ ADC | 差分输入、外部基准、≥ 1 kSPS、50/60 Hz 陷波可关 |
| — | 0.1 % 低温漂电阻（基准分压） | 25 ppm/℃ |

零件库 0402 电阻都是 1 % 的：做增益、滤波够用（误差标定掉），做方案 ② 的差分级不够——这是第 4 步仿真的结论。
"""
case.step("cad", f"框图级原理图；{len(LIBP)} 种元件从零件库选，运放、ADC 零件库没有，写通用类型待确认。",
          f"Block-level schematic; {len(LIBP)} component types from the library, op-amp and ADC not in the library and left as generic types to be confirmed.",
          md=case.text("5_原理图与元件.md", cadmd), figs=[("5_原理图.png", "信号调理原理图（框图级）", "Signal-conditioning schematic (block level)")],
          tools=tools("pcb") + L.lib_tools(LIBP), facts=[("零件库元件", "Library parts", len(LIBP), "种")])

# ================================================================ 6 工艺：组桥焊线
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["WQ-TS"][0]]
wire = [["臂 1（E+ → S+）", "轮辐 1 的 +45° 栅 → 轮辐 3 的 +45° 栅", f"{T.R_ARM:g}"],
        ["臂 2（S+ → E−）", "轮辐 1 的 −45° 栅 → 轮辐 3 的 −45° 栅", f"{T.R_ARM:g}"],
        ["臂 3（E+ → S−）", "轮辐 2 的 −45° 栅 → 轮辐 4 的 −45° 栅", f"{T.R_ARM:g}"],
        ["臂 4（S− → E−）", "轮辐 2 的 +45° 栅 → 轮辐 4 的 +45° 栅", f"{T.R_ARM:g}"]]
procmd = f"""# 工艺：组桥焊线（扭矩传感器线第 4 道）

扭矩传感器线：

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt)])}

## 组桥接线表

{L.md_table(["桥臂", "串联的两个栅", "阻值 Ω"], wire)}

（四根轮辐的剪应变同号；臂 3、4 接法与臂 1、2 相反，四个臂的变化才在电桥里相加。接反一对，输出直接变成零——终检一测就知道。）

## 工艺要点（每一条都对应第 4 步的一个数）

1. **焊点**：同一个桥的焊点用同一种焊锡、同样大小，热电势相互抵消；两处温差 1 ℃ 的铜–焊锡热电势就有几 μV，已经和噪声要求（{V_FS * 0.05 / 100 * 1e6:.1f} μV）同量级。
2. **引线**：四根信号线一样长、绞在一起；屏蔽层只在调理板一端接地。
3. **检验**：四个臂阻值相互差、桥路零点（未调零前）记下来，交给“温度补偿”工序算补偿电阻；绝缘电阻（应变片对弹性体）≥ 1 GΩ。
"""
case.step("process", "8 道工序；组桥接线表（相对轮辐串联）；焊点、引线、检验三条要点都对应仿真里的数。",
          "Eight operations; bridge wiring table (opposite spokes in series); three rules on solder joints, leads and inspection, each tied to a simulated number.",
          md=case.text("6_组桥工艺.md", procmd), tools=tools("engineer"), facts=[("工序", "Operations", len(rt), "")])

# ================================================================ 7 制造：20 台看零点
sh = L.run_shop("WQ-TS", 20, "WO-CASE-SN-A", seed=1611)
rows_q, cpk_min, fails, st = L.shop_table(sh["measurements"])
z = st["ts_zero"]
makemd = f"""# 制造：传感器厂做 20 台

仿真车间扭矩传感器线做 20 台（{sh['hours']:.0f} 小时）。终检五项：

{L.md_table(["特性（%FS）", "公差", "台数", "均值", "标准差", "Cpk"], rows_q)}

和这个案例直接相关的是**零点输出**：调零后均值 {z['mean']:+.3f} %FS、标准差 {z['sd']:.3f} %FS、Cpk {z['cpk']:.2f}。
对比第 4 步：不调零时电桥零点的标准差是 {zero_sd:.0f} %FS——“温度补偿”工序里的调零电阻把它压小了两个数量级以上。
"""
case.step("make", f"20 台，不合格 {fails} 项；零点输出标准差 {z['sd']:.3f} %FS、Cpk {z['cpk']:.2f}（不调零时 {zero_sd:.0f} %FS）。",
          f"20 sensors, {fails} failures; zero output std. dev. {z['sd']:.3f} %FS, Cpk {z['cpk']:.2f} (vs {zero_sd:.0f} %FS without balancing).",
          md=case.text("7_制造与终检.md", makemd), tools=tools("planner", "operator", "quality"),
          facts=[("零点 Cpk", "Zero Cpk", round(z["cpk"], 2), ""), ("不合格", "Out of tolerance", fails, "")])
case.check("make", "终检不合格项", "Final-test failures", fails, "==", 0, "", "扭矩终检台")
case.check("make", "零点输出 Cpk", "Zero-output Cpk", round(z["cpk"], 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **小信号先看噪声和零点，不看位数**：24 位 ADC 的最低位折到电桥只有 {lsb_in * 1e9:.2f} nV，真正的限制是前置级噪声（{pp_fs:.3f} %FS 峰峰值）。
2. **共模抑制不能靠分立电阻**：方案 ② 的差分级用 1 % 电阻，供桥一漂零点就跟着变（最大 {np.abs(mc_3op).max():.2f} %FS，比终检零点公差的一半还多）；方案 ③ 让共模原样通过、交给差分 ADC。
3. **应变片的公差和信号一样大**：不调零的电桥零点标准差 {zero_sd:.0f} %FS——调零必须在放大之前、在电桥里做。
4. 增益误差（±{gain_spread:.1f} %）是比例误差，标定修掉；**零点、噪声修不掉**，要在设计时压住。

## 留给学生的问题

1. 在“电路分析”页把 R_G 换成零件库的 1 kΩ：增益、过载余量、噪声各怎么变？
2. 供桥电压从 5 V 提到 10 V（实验“虚拟仪器”的扭矩传感器用 10 V）：输出、噪声（%FS）、自热各怎么变？
3. 为什么噪声带宽取 RC 截止频率的 π/2 倍？

相关：数字工厂“电路分析”“虚拟仪器（扭矩传感器）”；案例 B（弹性体）、案例 C（整机、补偿与标定）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；增益 {GAIN:.1f}、带宽 {m_ac['f3db']:.0f} Hz、噪声 {pp_fs:.3f} %FS。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; gain {GAIN:.1f}, bandwidth {m_ac['f3db']:.0f} Hz, noise {pp_fs:.3f} %FS.",
          md=case.text("8_总结.md", review), tools=tools("circuit", "inst"))
case.write()
print("ok", GAIN, m_dc, m_ac, gain_spread, mc_3op.std(), np.abs(mc_ours).max(), zero_sd, pp_fs)
