"""第 166b 轮：计算机厂案例 A——台式机主板 MB-PC 的 CPU 核心供电（多相降压 VRM）：
相数比较、纹波、损耗与效率、负载线（AVP）与输出电容、电压公差叠加；ngspice 开关仿真 + 平均模型负载阶跃；到计算机厂 SMT 线 40 块、上电测试量核心电压。

    python3 tools/cases/computer_a.py

外购件（智能功率级、控制器、电感、聚合物电容）写通用名称和示例参数；输入电容、去耦电容从问渠零件库选。输出到 factory/cases/computer/A/。
公差叠加算出的核心电压散布写回计算机厂清单 mb_vcore 的 sigma（本脚本核对两者一致）。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-computer.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
from cae import circuit as C  # noqa: E402

TOOLS = {
    "circuit": ("电路分析（ngspice）", "Circuit analysis (ngspice)", "/circuit"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间执行", "Shop floor", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "burnin": ("整机老化曲线", "System burn-in curves", "/burn-in"),
    "3d": ("3D 车间", "3D shop", "/3d"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("computer", "A", "简单", "台式机主板的 CPU 核心供电", "CPU core power on the desktop mainboard", "MB-PC CPU 供电（VRM）",
              "12 V 降到约 1.1 V、最大 140 A 给 CPU：比较 4 / 6 / 8 相选 6 相，算纹波、损耗与效率、负载线和输出电容，"
              "ngspice 开关仿真核对纹波和导通损耗、平均模型看 100 A 负载阶跃，电压公差叠加算出核心电压散布，写回工厂数据；SMT 线做 40 块、上电测试。",
              "12 V down to about 1.1 V at up to 140 A for the CPU: 4 / 6 / 8 phases compared and 6 chosen; ripple, losses, efficiency, load line and output capacitors calculated; "
              "ngspice switching simulation for ripple and conduction loss, averaged model for a 100 A load step; tolerance stack gives the core-voltage spread used by the plant; 40 boards built and tested.",
              "tools/cases/computer_a.py")

# 问渠零件库里有的：输入陶瓷电容、输入电解电容、去耦电容
CIN = L.lib_part("A-ELE-C1206", "10U-25V")
CBULK_IN = L.lib_part("A-ELE-CPEL", "470U-63V")
CDEC = L.lib_part("A-ELE-C0402", "100N")
LIBP = [CIN, CBULK_IN, CDEC]

# ---------------------------------------------------------------- 任务（示例值，量级按常见 125 W 台式 CPU）
VIN = 12.0                  # ATX 电源 12 V
VID = 1.25                  # 空载设定电压（CPU 发来的 VID，示例）
LL = 1.1e-3                 # 负载线 Ω（CPU 要求的“电流大一安、电压低 1.1 mV”）
ICCMAX, ITDC, ISTEP0, ISTEP1 = 140.0, 100.0, 30.0, 130.0
SLEW = 100e6                # 负载阶跃 100 A/μs
TOB = 15.0                  # 核心电压偏离负载线的允许范围 ±mV（工厂上电测试的公差，清单 mb_vcore）
ITEST = 10.0                # 上电测试时的负载电流 A
# 外购件示例参数（通用名称，型号待确认）
F_SW = 500e3
L_PH = 150e-9
DCR = 0.20e-3
RHS, RLS = 5.0e-3, 1.2e-3   # 智能功率级上管 / 下管导通电阻（示例）
T_EDGE = 8e-9               # 上管开通 + 关断的电压电流交叠时间之和（示例）
QG, VDRV = 25e-9, 5.0       # 两只管子栅电荷合计、驱动电压
T_DEAD, VF = 15e-9, 0.7     # 死区（每次）、体二极管压降
P_CORE = 0.30               # 每相电感铁损（示例）
P_CTRL = 0.6                # 控制器、驱动供电
CB_ONE, ESR_B, ESL_B = 560e-6, 6e-3, 1.2e-9      # 聚合物电容一只
N_MLCC, CM_EFF, ESR_M, ESL_M = 40, 10e-6, 3e-3, 0.4e-9   # 22 μF 0805 陶瓷电容 40 只，直流偏压下实际约 10 μF
F_I = 80e3                  # 控制环（电流环 + AVP）带宽：约开关频率 × 相数 / 40（示例设计值）
T_D = 0.5e-6                # 采样、PWM 延迟（一阶近似）


def phase_calc(n, i_out, vo=None):
    """n 相、输出 i_out 时：占空比、每相纹波、输出纹波电流、各项损耗（W）"""
    vo = VID - LL * i_out if vo is None else vo
    iph = i_out / n
    d = (vo + iph * (RLS + DCR)) / (VIN - iph * (RHS - RLS))
    dip = (VIN - vo) * d / (L_PH * F_SW)
    k = math.floor(n * d)                     # 同时导通的相数（D < 1/n 时 0）
    dio = (VIN - n * vo) * d / (L_PH * F_SW) if k == 0 else float("nan")
    irms2 = iph ** 2 + dip ** 2 / 12
    p = dict(hs=n * irms2 * d * RHS, ls=n * irms2 * (1 - d) * RLS, dcr=n * irms2 * DCR,
             sw=n * 0.5 * VIN * iph * T_EDGE * F_SW, gate=n * QG * VDRV * F_SW, dead=n * 2 * VF * iph * T_DEAD * F_SW,
             core=n * P_CORE, ctrl=P_CTRL)
    pl = sum(p.values())
    return dict(n=n, vo=vo, iph=iph, d=d, dip=dip, dio=dio, p=p, loss=pl, eff=vo * i_out / (vo * i_out + pl),
                slew_up=n * (VIN - vo) / L_PH, slew_dn=n * vo / L_PH)


# ================================================================ 1 任务书
brief = f"""# 设计任务书：台式机主板 CPU 核心供电

**用在哪**　计算机厂自制的台式机主板 MB-PC（台式机 WQ-PC1、工控机 WQ-IPC 用同一块板）。CPU 满载约 125 W，核心电压约 1.1 V——
电压低、电流大：**最大 {ICCMAX:.0f} A**。ATX 电源只给 12 V，要在主板上 CPU 插座旁边降压，这块电路叫 VRM（电压调节模块）。

| 项目 | 要求 | 出处 |
|---|---|---|
| 输入 | {VIN:g} V（ATX 电源 8 针 CPU 供电） | 整机设计 |
| 空载电压（VID） | {VID:g} V（CPU 通过串行总线告诉 VRM） | CPU 规格（示例值） |
| 负载线（AVP） | {LL * 1000:g} mΩ：电流每大 1 A，电压低 {LL * 1000:g} mV | CPU 规格（示例值） |
| 最大电流 / 持续电流 | {ICCMAX:.0f} A / {ITDC:.0f} A | CPU 规格（示例值） |
| 负载阶跃 | {ISTEP0:.0f} → {ISTEP1:.0f} A，{SLEW / 1e6:.0f} A/μs | CPU 从空闲突然满载 |
| 电压偏离负载线 | ±{TOB:g} mV（静态公差 + 动态过冲合计） | CPU 规格；工厂上电测试 mb_vcore |
| 效率（{ITDC:.0f} A） | ≥ 88 % | 整机功耗、散热 |
| 板上位置 | 插座左侧和上方一条，宽不超过 30 mm | 主板布局 |

外购件（智能功率级、多相控制器、电感、聚合物电容）写通用名称和示例参数；输入电容、去耦电容从问渠零件库选。
"""
case.step("brief", f"12 V → 约 1.1 V，最大 {ICCMAX:.0f} A；负载线 {LL * 1000:g} mΩ；阶跃 {ISTEP0:.0f} → {ISTEP1:.0f} A；偏离负载线 ±{TOB:g} mV。",
          f"12 V to about 1.1 V, up to {ICCMAX:.0f} A; {LL * 1000:g} mΩ load line; {ISTEP0:.0f} → {ISTEP1:.0f} A step; ±{TOB:g} mV around the load line.",
          md=case.text("1_任务书.md", brief),
          facts=[("最大电流", "Max current", ICCMAX, "A"), ("负载线", "Load line", LL * 1000, "mΩ"), ("允许偏差", "Tolerance", TOB, "mV")])

# ================================================================ 2 方案
opts = [phase_calc(n, ITDC) for n in (4, 6, 8)]
opt_max = [phase_calc(n, ICCMAX) for n in (4, 6, 8)]
rows = []
for o, om in zip(opts, opt_max):
    rows.append([f"{o['n']} 相", f"{om['iph']:.0f} A", f"{o['dip']:.1f} A", f"{o['dio']:.1f} A", f"{o['loss']:.1f} W", f"{o['eff'] * 100:.1f} %",
                 f"{om['loss'] / om['n']:.2f} W", f"{o['slew_up'] / 1e6:.0f} A/μs", {4: "✗ 每颗功率级太热，效率差", 6: "✓ 选定", 8: "多两颗功率级，效率只高一点，插座旁放不下"}[o["n"]]])
concept = f"""# 方案：几相、怎么测电流、怎么控制

## 相数（开关频率 {F_SW / 1000:.0f} kHz、每相电感 {L_PH * 1e9:.0f} nH，同一种智能功率级）

{L.md_table(["相数", f"每相电流（{ICCMAX:.0f} A）", "每相纹波", "输出纹波电流", f"损耗（{ITDC:.0f} A）", "效率", f"每颗发热（{ICCMAX:.0f} A）", "电流上升最快", "结论"], rows)}

相数多：每相电流小，导通损耗按电流平方下降；几相错开开关（交错），纹波互相抵消一部分；电流能更快跟上负载。代价是功率级、电感多，板子面积和成本上去。
**选 6 相**：{ITDC:.0f} A 时效率 {opts[1]['eff'] * 100:.1f} %，每颗功率级最大 {opt_max[1]['loss'] / 6:.2f} W（贴片封装加主板铜皮、散热片能散）。

## 电流怎么测

| 办法 | 优点 | 缺点 | |
|---|---|---|---|
| 电感直流电阻（DCR）+ RC 网络 | 不用额外元件 | DCR 随温度变 40 %，要热敏电阻补偿，误差 ±5–8 % | |
| 智能功率级内部测电流（IMON） | 误差 ±2–3 %，不随电感温度变 | 功率级贵一点 | ✓ |

负载线靠测到的电流算“该降多少电压”，电流测不准，电压就不准。

## 控制：自适应电压定位（AVP）

控制器让输出电压 = VID − 负载线 × 电流。好处：电流突然变大时，电压**本来就该往下走** {LL * 1000:g} mV/A，输出电容不用硬顶——
同样的偏差要求，电容少得多。
"""
case.step("concept", f"6 相（{ITDC:.0f} A 时效率 {opts[1]['eff'] * 100:.1f} %）；智能功率级测电流；自适应电压定位（AVP）。",
          f"6 phases ({opts[1]['eff'] * 100:.1f} % at {ITDC:.0f} A); current sensed in smart power stages; adaptive voltage positioning (AVP).",
          md=case.text("2_方案.md", concept), facts=[("相数", "Phases", 6, ""), ("效率", "Efficiency", round(opts[1]["eff"] * 100, 1), "%")])
case.check("concept", f"6 相 {ITDC:.0f} A 效率", f"6-phase efficiency at {ITDC:.0f} A", round(opts[1]["eff"] * 100, 1), ">=", 88.0, "%", "任务书")

# ================================================================ 3 计算
N = 6
pt = opts[1]
pm = opt_max[1]
tau_i = 1 / (2 * math.pi * F_I)
c_need = 1.96 * tau_i / LL                       # ζ ≥ 0.7
n_bulk = 6
c_tot = n_bulk * CB_ONE + N_MLCC * CM_EFF
zeta = 0.5 * math.sqrt(c_tot * LL / tau_i)
f_rip = N * F_SW


def z_bank(f, nb=n_bulk):
    w = 2 * math.pi * f
    zb = complex(ESR_B, w * ESL_B - 1 / (w * CB_ONE)) / nb
    zm = complex(ESR_M, w * ESL_M - 1 / (w * CM_EFF)) / N_MLCC
    return zb * zm / (zb + zm)


v_rip_hand = pt["dio"] * abs(z_bank(f_rip))
# 公差叠加（3σ 值，示例来自常见控制器、功率级规格）
STACK = [("VID 基准（DAC）", "±0.5 % × 1.25 V", 0.005 * VID * 1000),
         ("误差放大器失调", "±1.0 mV", 1.0),
         ("电流测量增益", f"±3 % × {LL * 1000:g} mΩ × {ITEST:g} A", 0.03 * LL * ITEST * 1000),
         ("上电测试表与夹具", "±1.5 mV", 1.5)]
three_sigma = math.sqrt(sum(x[2] ** 2 for x in STACK))
sigma = three_sigma / 3
cpk_pred = TOB / three_sigma
dyn_allow = TOB - three_sigma
p = pt["p"]
lrows = [["上管导通", f"{p['hs']:.2f}"], ["下管导通", f"{p['ls']:.2f}"], ["电感直流电阻", f"{p['dcr']:.2f}"], ["开关交叠", f"{p['sw']:.2f}"],
         ["栅极驱动", f"{p['gate']:.2f}"], ["死区体二极管", f"{p['dead']:.2f}"], ["电感铁损", f"{p['core']:.2f}"], ["控制器", f"{p['ctrl']:.2f}"],
         ["**合计**", f"**{pt['loss']:.2f}**"]]
calc = f"""# 计算书 Calculation

## 1 占空比与纹波 Duty and ripple（{ITDC:.0f} A，Vo = {pt['vo']:.3f} V）

| 量 Quantity | 公式 Formula | 结果 Result |
|---|---|---|
| 占空比 D | (Vo + I_ph·(R_LS + DCR)) / (Vin − I_ph·(R_HS − R_LS)) | {pt['d']:.4f} |
| 每相纹波 ΔI_ph | (Vin − Vo)·D / (L·f) | {pt['dip']:.2f} A |
| 输出纹波电流 ΔI_out（D < 1/N，同一时刻只有一相开） | (Vin − N·Vo)·D / (L·f) | {pt['dio']:.2f} A |
| 纹波频率 | N·f | {f_rip / 1e6:.1f} MHz |
| 输出纹波电压 | ΔI_out × \\|Z_电容组(N·f)\\| | {v_rip_hand * 1000:.2f} mV |

六相交错，输出纹波电流只有每相的 {pt['dio'] / pt['dip'] * 100:.0f} %。

## 2 损耗与效率 Losses and efficiency（{ITDC:.0f} A，W）

{L.md_table(["损耗 Loss", "W"], lrows)}

导通损耗 = 相数 × I_rms² × R，I_rms² = I_ph² + ΔI_ph²/12；开关交叠 = ½·Vin·I_ph·t·f；栅极 = Q_g·V_drv·f；死区 = 2·V_F·I_ph·t_dead·f。
效率 **{pt['eff'] * 100:.1f} %**（{ITDC:.0f} A），{pm['eff'] * 100:.1f} %（{ICCMAX:.0f} A）；{ICCMAX:.0f} A 时每颗功率级 {pm['loss'] / N:.2f} W。

## 3 输出电容：负载线 + 控制环 Output capacitance

AVP 下输出看进去像一个 {LL * 1000:g} mΩ 的电阻，控制环（带宽 f_i = {F_I / 1000:.0f} kHz，时间常数 τ = 1/(2π·f_i) = {tau_i * 1e6:.2f} μs）
和输出电容 C 组成二阶系统：τ·C·s² + C·s + 1/LL = 0，阻尼 ζ = ½·√(C·LL/τ)。不过冲要 ζ ≥ 0.7：

C ≥ 1.96·τ / LL = **{c_need * 1000:.2f} mF**

选 {n_bulk} 只 {CB_ONE * 1e6:.0f} μF 聚合物电容 + {N_MLCC} 只 22 μF 陶瓷（直流偏压下按 {CM_EFF * 1e6:.0f} μF 算）= {c_tot * 1000:.2f} mF，ζ = {zeta:.2f}。
电流上升最快 N·(Vin − Vo)/L = {pt['slew_up'] / 1e6:.0f} A/μs，比负载阶跃 {SLEW / 1e6:.0f} A/μs 快；下降最快 N·Vo/L = {pt['slew_dn'] / 1e6:.0f} A/μs，比阶跃慢——卸载时多出来的电流先进电容。

## 4 电压公差叠加 Tolerance stack（上电测试，{ITEST:g} A）

{L.md_table(["来源 Source", "规格 Spec", "3σ / mV"], [[a, b, f"{c:.2f}"] for a, b, c in STACK])}

方和根 3σ = **{three_sigma:.2f} mV**，σ = {sigma:.2f} mV。±{TOB:g} mV 公差下预计 Cpk = {TOB:g} / {three_sigma:.2f} = **{cpk_pred:.2f}**；
留给负载阶跃的动态偏差 {TOB:g} − {three_sigma:.2f} = **{dyn_allow:.1f} mV**。
这个 σ 写进计算机厂清单 mb_vcore（原来按经验取 3 mV，Cpk 只有约 1.3；用测电流更准的智能功率级以后按 {math.ceil(sigma * 10) / 10:g} mV）。
"""
case.step("calc", f"{ITDC:.0f} A 损耗 {pt['loss']:.1f} W、效率 {pt['eff'] * 100:.1f} %；电容 ≥ {c_need * 1000:.2f} mF（选 {c_tot * 1000:.2f} mF）；公差叠加 3σ = {three_sigma:.1f} mV。",
          f"{pt['loss']:.1f} W loss, {pt['eff'] * 100:.1f} % efficiency at {ITDC:.0f} A; ≥ {c_need * 1000:.2f} mF needed ({c_tot * 1000:.2f} mF chosen); tolerance stack 3σ = {three_sigma:.1f} mV.",
          md=case.text("3_计算书.md", calc),
          facts=[("效率", "Efficiency", round(pt["eff"] * 100, 1), "%"), ("输出电容", "Output capacitance", round(c_tot * 1000, 2), "mF"),
                 ("阻尼 ζ", "Damping ζ", round(zeta, 2), ""), ("电压散布 3σ", "Voltage spread 3σ", round(three_sigma, 2), "mV")])
case.check("calc", "输出电容（ζ ≥ 0.7 所需）", "Output capacitance (needed for ζ ≥ 0.7)", round(c_tot * 1000, 2), ">=", round(c_need * 1000, 2), "mF", "第 3 节")
case.check("calc", f"{ICCMAX:.0f} A 时每颗功率级发热", f"Power-stage dissipation at {ICCMAX:.0f} A", round(pm["loss"] / N, 2), "<=", 3.0, "W", "功率级封装加铜皮散热（示例）")
case.check("calc", "预计核心电压 Cpk", "Predicted core-voltage Cpk", round(cpk_pred, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 4 仿真
iph = ITDC / N
dd = pt["d"]
T = 1 / F_SW
ss = ["* WQ MB-PC VRM: 6-phase interleaved buck, steady state at TDC (ideal switches + Ron)", f"Vin vin 0 {VIN:g}"]
for k in range(N):
    ss += [f"Vg{k} g{k} 0 pulse(0 5 {k * T / N:.6g} 1n 1n {dd * T - 1e-9:.6g} {T:.6g})", f"Bgl{k} gl{k} 0 v=5-v(g{k})",
           f"S{k}h vin sw{k} g{k} 0 swh", f"S{k}l sw{k} 0 gl{k} 0 swl", f"L{k} sw{k} m{k} {L_PH:g} ic={iph:g}", f"Vp{k} m{k} q{k} 0", f"R{k} q{k} pc {DCR:g}"]
ss += ["Vsum pc out 0", f".model swh sw vt=2.5 vh=0 ron={RHS:g} roff=1e5", f".model swl sw vt=2.5 vh=0 ron={RLS:g} roff=1e5",
       f"Cb out nb {n_bulk * CB_ONE:g} ic={pt['vo']:g}", f"Rb nb 0 {ESR_B / n_bulk:g}",
       f"Cm out nm {N_MLCC * CM_EFF:g} ic={pt['vo']:g}", f"Rm nm 0 {ESR_M / N_MLCC:g}",
       f"Iload out 0 {ITDC:g}", ".options numdgt=7", ".tran 2n 600u 0 2n uic",
       ".meas tran vavg avg v(out) from=580u to=600u", ".meas tran vpp pp v(out) from=580u to=600u",
       ".meas tran pin avg par('-v(vin)*i(Vin)') from=580u to=600u", ".meas tran ppc avg par('v(pc)*i(Vsum)') from=580u to=600u",
       ".meas tran iopp pp i(Vsum) from=580u to=600u", ".meas tran i0pp pp i(Vp0) from=580u to=600u",
       ".meas tran i0 avg i(Vp0) from=580u to=600u", ".meas tran i3 avg i(Vp3) from=580u to=600u", ".end"]
net_ss = "\n".join(ss)
r_ss = C.run(net_ss, timeout=120, max_points=200000)
m_ss = r_ss["meas"]
if r_ss["errors"] or "pin" not in m_ss:
    raise SystemExit("ngspice 稳态仿真失败：" + "；".join(r_ss["errors"]) + r_ss["log"][-800:])
loss_sim = m_ss["pin"] - m_ss["ppc"]
loss_hand = p["hs"] + p["ls"] + p["dcr"]
case.raw("4_稳态.cir", net_ss.encode())


def avp_net(nb, cscale=1.0, delay=T_D):
    sru, srd = pt["slew_up"], pt["slew_dn"]
    wc = 2 * math.pi * F_I
    v0 = VID - LL * ISTEP0
    t1, t2 = 50e-6, 50e-6 + (ISTEP1 - ISTEP0) / SLEW
    return "\n".join([
        "* WQ MB-PC VRM: averaged AVP model, 30 -> 130 A load step (phase current = state node ni, A)",
        f"Bc 0 ni i=max(-{srd:g},min({sru:g},{wc:g}*(({VID:g}-v(vs))/{LL:g}-v(ni))))", f"Cni ni 0 1 ic={ISTEP0:g}",
        f"Bs 0 vs i=(v(out)-v(vs))/{delay:g}", f"Cvs vs 0 1 ic={v0:g}", "Bph 0 out i=v(ni)",
        f"Cb out nb {nb * CB_ONE * cscale:g} ic={v0:g}", f"Rb nb nb2 {ESR_B / nb:g}", f"Lb nb2 0 {ESL_B / nb:g}",
        f"Cm out nm {N_MLCC * CM_EFF * cscale:g} ic={v0:g}", f"Rm nm nm2 {ESR_M / N_MLCC:g}", f"Lm nm2 0 {ESL_M / N_MLCC:g}",
        f"Iload out 0 pwl(0 {ISTEP0:g} {t1:g} {ISTEP0:g} {t2:g} {ISTEP1:g} 250u {ISTEP1:g} {250e-6 + (ISTEP1 - ISTEP0) / SLEW:g} {ISTEP0:g} 450u {ISTEP0:g})",
        ".options numdgt=7", ".tran 10n 450u 0 20n uic",
        ".meas tran vmin min v(out) from=50u to=230u", ".meas tran v130 avg v(out) from=230u to=250u",
        ".meas tran vmax max v(out) from=250u to=430u", ".meas tran v30 avg v(out) from=430u to=450u", ".end"])


def avp_run(nb, cscale=1.0, vectors=False):
    r = C.run(avp_net(nb, cscale), timeout=60, vectors=vectors, max_points=6000)
    m = r["meas"]
    if "vmin" not in m:
        raise SystemExit("ngspice 负载阶跃仿真失败：" + "；".join(r["errors"]) + r["log"][-800:])
    a1, a0 = VID - LL * ISTEP1, VID - LL * ISTEP0
    return dict(under=(m["vmin"] - a1) * 1000, over=(m["vmax"] - a0) * 1000, ss=(m["v130"] - a1) * 1000, plots=r["plots"])


sweep = {nb: avp_run(nb) for nb in (3, 4, 5, 6, 8)}
nom = avp_run(n_bulk, vectors=True)
aged = avp_run(n_bulk, cscale=0.8)
case.raw("4_负载阶跃.cir", avp_net(n_bulk).encode())
r_plot = C.run(net_ss.replace(".tran 2n 600u 0 2n uic", ".tran 2n 600u 590u 2n uic"), timeout=120, max_points=20000)

fig, axs = plt.subplots(1, 3, figsize=(11.2, 3.1))
d = r_plot["plots"][0]["data"]
t = np.array(d["time"]) * 1e6
for k in range(N):
    axs[0].plot(t - t[0], np.array(d[f"i(vp{k})"]), lw=0.9)
axs[0].plot(t - t[0], np.array(d["i(vsum)"]) / N, color="k", lw=1.2, ls="--", label="总电流 / 6")
axs[0].set_xlim(0, 4)
axs[0].set_xlabel("时间 / μs")
axs[0].set_ylabel("电流 / A")
axs[0].set_title(f"六相电流交错：每相纹波 {m_ss['i0pp']:.1f} A，总的 {m_ss['iopp']:.1f} A", fontsize=9.5)
axs[0].legend(fontsize=8, frameon=False)
dn = nom["plots"][0]["data"]
tn = np.array(dn["time"]) * 1e6
axs[1].plot(tn, np.array(dn["v(out)"]) * 1000, color=L.ACCENT, lw=1.2, label="输出电压")
il = np.interp(tn, [0, 50, 51, 250, 251, 450], [ISTEP0, ISTEP0, ISTEP1, ISTEP1, ISTEP0, ISTEP0])
axs[1].plot(tn, (VID - LL * il) * 1000, color=L.MUTED, ls="--", lw=0.8, label="负载线")
axs[1].fill_between(tn, (VID - LL * il) * 1000 - TOB, (VID - LL * il) * 1000 + TOB, color=L.OK, alpha=0.12, label=f"±{TOB:g} mV")
axs[1].set_xlabel("时间 / μs")
axs[1].set_ylabel("核心电压 / mV")
axs[1].set_title(f"{ISTEP0:.0f} → {ISTEP1:.0f} → {ISTEP0:.0f} A 负载阶跃", fontsize=9.5)
axs[1].legend(fontsize=7.5, frameon=False, loc="upper right")
nbs = sorted(sweep)
axs[2].plot(nbs, [-sweep[n]["under"] for n in nbs], "o-", color=L.ACCENT, label="跌到负载线以下")
axs[2].axhline(dyn_allow, color=L.BAD, ls="--", lw=0.8)
axs[2].text(3.05, dyn_allow + 1, f"动态允许 {dyn_allow:.1f} mV", fontsize=8, color=L.BAD)
axs[2].axvline(n_bulk, color=L.MUTED, ls=":", lw=0.8)
axs[2].set_xlabel(f"{CB_ONE * 1e6:.0f} μF 聚合物电容只数")
axs[2].set_ylabel("偏离负载线 / mV")
axs[2].set_title("电容少了阻尼不够、过冲大", fontsize=9.5)
fig.subplots_adjust(wspace=0.38)
case.fig(fig, "4_ngspice.png")

srows = [[f"{n} 只", f"{n * CB_ONE * 1000 + N_MLCC * CM_EFF * 1000:.2f} mF", f"{0.5 * math.sqrt((n * CB_ONE + N_MLCC * CM_EFF) * LL / tau_i):.2f}",
          f"{max(0.0, -sweep[n]['under']):.1f} mV", "✓" if -sweep[n]["under"] <= dyn_allow else "✗"] for n in nbs]
simmd = f"""# 仿真：ngspice（数字工厂“电路分析”用的同一个 ngspice）

## 1 六相开关仿真（{ITDC:.0f} A 稳态）

理想开关 + 导通电阻、六只 {L_PH * 1e9:.0f} nH 电感错开 1/6 周期，跑 600 μs 到稳态（各相电流 {m_ss['i0']:.2f} / {m_ss['i3']:.2f} A……，均流），取最后 20 μs：

| 读数 | ngspice | 公式（第 3 步） | 相差 |
|---|---|---|---|
| 每相纹波 | {m_ss['i0pp']:.2f} A | {pt['dip']:.2f} A | {abs(m_ss['i0pp'] / pt['dip'] - 1) * 100:.1f} % |
| 输出纹波电流 | {m_ss['iopp']:.2f} A | {pt['dio']:.2f} A | {abs(m_ss['iopp'] / pt['dio'] - 1) * 100:.1f} % |
| 输出纹波电压 | {m_ss['vpp'] * 1000:.2f} mV | {v_rip_hand * 1000:.2f} mV | {abs(m_ss['vpp'] / v_rip_hand - 1) * 100:.1f} % |
| 导通损耗（上下管 + 电感 DCR） | {loss_sim:.2f} W | {loss_hand:.2f} W | {abs(loss_sim / loss_hand - 1) * 100:.1f} % |

纹波电压的公式只算了 3 MHz 基波（三角波还有谐波，陶瓷电容在高频的阻抗更低又被 ESR 托住），相差十几个百分点是这个原因，量级对得上；它本来就远小于公差，不作校核。开关交叠、栅极、死区、铁损理想开关模型里没有，按第 3 步公式加。网表 `4_稳态.cir`。

## 2 负载阶跃（平均模型）

六相合成一个受控电流源：电流跟着 (VID − 采样电压)/负载线 走，带宽 {F_I / 1000:.0f} kHz，上升、下降各受电感限速（{pt['slew_up'] / 1e6:.0f} / {pt['slew_dn'] / 1e6:.0f} A/μs），
采样加 {T_D * 1e6:g} μs 延迟；电容带 ESR、ESL。网表 `4_负载阶跃.cir`。

{L.md_table(["聚合物电容", "总电容", "ζ（公式）", "跌到负载线以下", f"≤ {dyn_allow:.1f} mV"], srows)}

选定 {n_bulk} 只：跌到负载线以下 {max(0.0, -nom['under']):.1f} mV、卸载冲到负载线以上 {max(0.0, nom['over']):.1f} mV；**电容老化少 20 %** 时 {max(0.0, -aged['under']):.1f} / {max(0.0, aged['over']):.1f} mV，仍在 {dyn_allow:.1f} mV 内。
5 只刚好够，留一只给电容公差和老化。
"""
d_rip = max(abs(m_ss["i0pp"] / pt["dip"] - 1), abs(m_ss["iopp"] / pt["dio"] - 1)) * 100
d_loss = abs(loss_sim / loss_hand - 1) * 100
case.step("sim", f"开关仿真与公式：纹波相差 {d_rip:.1f} %、导通损耗相差 {d_loss:.1f} %；负载阶跃：{n_bulk} 只聚合物电容偏离负载线 {max(0.0, -nom['under'], nom['over']):.1f} mV，少 20 % 电容 {max(0.0, -aged['under'], aged['over']):.1f} mV。",
          f"Switching sim vs formulas: ripple within {d_rip:.1f} %, conduction loss within {d_loss:.1f} %; load step: {max(0.0, -nom['under'], nom['over']):.1f} mV off the load line with {n_bulk} polymer caps, {max(0.0, -aged['under'], aged['over']):.1f} mV with 20 % less capacitance.",
          md=case.text("4_ngspice仿真.md", simmd),
          figs=[("4_ngspice.png", "六相电流交错、负载阶跃、电容只数与过冲", "Interleaved phase currents, load step, capacitor count vs deviation")],
          files=[("4_稳态.cir", "六相开关仿真网表（ngspice）", "6-phase switching netlist (ngspice)"), ("4_负载阶跃.cir", "负载阶跃平均模型网表", "Averaged load-step netlist")],
          tools=tools("circuit"),
          facts=[("纹波相差", "Ripple difference", round(d_rip, 1), "%"), ("阶跃偏差", "Step deviation", round(max(0.0, -nom["under"], nom["over"]), 1), "mV")])
case.check("sim", "开关仿真与公式：纹波最大相差", "Switching sim vs formula: ripple", round(d_rip, 1), "<=", 5.0, "%", "核对公式")
case.check("sim", "开关仿真与公式：导通损耗相差", "Switching sim vs formula: conduction loss", round(d_loss, 1), "<=", 5.0, "%", "核对公式")
case.check("sim", "负载阶跃偏离负载线（电容少 20 %）", "Load-step deviation (20 % less capacitance)", round(max(0.0, -aged["under"], aged["over"]), 1), "<=", round(dyn_allow, 1), "mV", "第 3 步动态允许")

# ================================================================ 5 三维与布局
import build123d as bd  # noqa: E402

A0 = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
board = bd.Box(110, 80, 1.6, align=A0)
parts = [bd.Pos(25, 5, 1.6) * bd.Box(52, 45, 6, align=A0)]                       # CPU 插座（示意尺寸）
stages, inds = [], []
for k in range(N):                                                               # 插座左侧一列 3 相、上方一排 3 相
    x, y = (-22, -20 + k * 14) if k < 3 else (-2 + (k - 3) * 17, 33)
    if k < 3:
        stages.append(bd.Pos(x - 12, y, 1.6) * bd.Box(6, 5, 0.9, align=A0))
        inds.append(bd.Pos(x, y, 1.6) * bd.Box(10, 10, 8, align=A0))
    else:
        stages.append(bd.Pos(x, y + 9, 1.6) * bd.Box(6, 5, 0.9, align=A0))
        inds.append(bd.Pos(x, y - 2, 1.6) * bd.Box(10, 10, 8, align=A0))
caps = [bd.Pos(-8 + (i % 3) * 7, -26 + (i // 3) * 7, 1.6) * bd.Cylinder(3.15, 6, align=A0) for i in range(n_bulk)]
inb = [bd.Pos(-48, -10 + i * 20, 1.6) * bd.Cylinder(8, 17.5, align=A0) for i in range(2)]
asm = board
for s in parts + stages + inds + caps + inb:
    asm = asm + s
bd.export_step(asm, str(case.path("5_VRM布局.step")))
L.render_solid(asm, case.path("5_VRM三维.png"), elev=38, azim=-60, color=(0.55, 0.72, 0.60), size=(8, 5), swap=False)

fig, ax = plt.subplots(figsize=(7.6, 5.2))
ax.add_patch(plt.Rectangle((-55, -40), 110, 80, fc="#e8f1e8", ec=L.INK, lw=0.8))
ax.add_patch(plt.Rectangle((-1, -17.5), 52, 45, fc="#dfe6ee", ec=L.INK, lw=0.8))
ax.text(25, 5, "CPU 插座", ha="center", va="center", fontsize=10)
for k in range(N):
    x, y = (-22, -20 + k * 14) if k < 3 else (-2 + (k - 3) * 17, 33)
    sx, sy = (x - 12, y) if k < 3 else (x, y + 9)
    iy = y if k < 3 else y - 2
    ax.add_patch(plt.Rectangle((x - 5, iy - 5), 10, 10, fc="#c9d6e4", ec=L.INK, lw=0.6))
    ax.add_patch(plt.Rectangle((sx - 3, sy - 2.5), 6, 5, fc="#3b4a5a", ec=L.INK, lw=0.6))
    ax.text(x, iy, f"L{k + 1}", ha="center", va="center", fontsize=7.5)
for i in range(n_bulk):
    ax.add_patch(plt.Circle((-8 + (i % 3) * 7, -26 + (i // 3) * 7), 3.15, fc="#f2e3c6", ec=L.INK, lw=0.6))
for i in range(2):
    ax.add_patch(plt.Circle((-48, -10 + i * 20), 8, fc="#e9d4d4", ec=L.INK, lw=0.6))
ax.text(-48, 22, "12 V 输入\n电解电容", ha="center", fontsize=7.5)
ax.text(-8, -36.5, "输出聚合物电容 ×6", ha="center", fontsize=7.5)
ax.text(-34, -33, "功率级（深色）", fontsize=7.5)
ax.text(25, -30, "插座背面：22 μF 陶瓷 ×40", ha="center", fontsize=7.5, color=L.MUTED)
ax.set_xlim(-58, 58)
ax.set_ylim(-42, 44)
ax.set_aspect("equal")
ax.set_xlabel("mm")
ax.set_title("VRM 布局（俯视，示意）", fontsize=10)
case.fig(fig, "5_VRM布局.png")
cadmd = f"""# 三维与布局：插座左侧 3 相、上方 3 相

![布局](5_VRM布局.png)

![三维](5_VRM三维.png)

布局要点：

1. **功率级 → 电感 → 插座**一条直线，大电流回路最短；12 V 输入陶瓷电容贴着每颗功率级的输入脚（开关时的高频电流就在这一小圈里转）。
2. 输出聚合物电容放插座边上，22 μF 陶瓷电容放**插座正背面**（离 CPU 最近，第 4 步的 ESL 按这个算）。
3. 功率级底部焊盘打满过孔到内层地，{ICCMAX:.0f} A 时每颗 {pm['loss'] / N:.2f} W 靠主板铜皮和上面的散热片散。
4. 电压采样线从插座背面的采样点差分引回控制器（远端采样），不和大电流共用铜。

## 用到的问渠零件库零件

{L.lib_md(LIBP, {CIN['ref']: "12 V 输入（每相 2 只，共 12 只）", CBULK_IN['ref']: "12 V 输入电解（2 只）", CDEC['ref']: "控制器、功率级去耦"})}

外购件（示例参数，型号待确认）：智能功率级 ×{N}（导通电阻 {RHS * 1000:g} / {RLS * 1000:g} mΩ，带电流输出）、多相数字控制器 ×1、{L_PH * 1e9:.0f} nH 电感 ×{N}（DCR {DCR * 1000:g} mΩ）、
{CB_ONE * 1e6:.0f} μF 2.5 V 聚合物电容 ×{n_bulk}、22 μF 0805 陶瓷电容 ×{N_MLCC}。三维模型 `5_VRM布局.step`（示意尺寸）。
"""
case.step("cad", "插座左侧 3 相、上方 3 相；功率级 → 电感 → 插座一条直线；陶瓷电容放插座背面；远端差分采样。",
          "Three phases left of the socket, three above; power stage → inductor → socket in a straight line; ceramics behind the socket; remote differential sensing.",
          md=case.text("5_布局.md", cadmd), figs=[("5_VRM布局.png", "VRM 布局（俯视）", "VRM layout (top view)"), ("5_VRM三维.png", "VRM 三维（示意）", "VRM 3D (schematic)")],
          files=[("5_VRM布局.step", "三维模型（STEP）", "3D model (STEP)")], tools=L.lib_tools(LIBP))

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["MB-PC"][0]]
procmd = f"""# 工艺：计算机厂主板 SMT 线

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt)])}

和 CPU 供电有关的：

- **锡膏印刷、检测**：功率级底部大焊盘用网格开孔，锡量 50–70 %，太多会把芯片顶起来、太少散热差；
- **X 光**：功率级（QFN 封装，焊点在底下）看底部焊盘空洞，空洞大了热阻大——和 CPU 插座、BGA 一起看；
- **在线测试 / 上电测试**：电子负载拉 {ITEST:g} A，量核心电压和“VID − 负载线 × 电流”的偏差，就是 mb_vcore（公差 ±{TOB:g} mV，第 3 步公差叠加）；
- **BIOS 烧录**：控制器的负载线、相数、过流点等参数随 BIOS 一起写入。
"""
case.step("process", f"主板 SMT 线 {len(rt)} 道：功率级大焊盘网格开孔、X 光看空洞、上电测试量核心电压偏差、BIOS 写控制器参数。",
          f"{len(rt)} SMT operations: grid stencil for the power-stage pads, X-ray for voids, power-on test of core-voltage deviation, controller settings with the BIOS.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("工序", "Operations", len(rt), "")])

# ================================================================ 7 制造
import yaml  # noqa: E402

plant = yaml.safe_load((ROOT / "factory" / "plants" / "wenquest-computer.yaml").read_text(encoding="utf-8"))
sig_plant = next(c["sigma"] for m in plant["measurements"] if m["item"] == "MB-PC" for c in m["chars"] if c["code"] == "mb_vcore")
sh = L.run_shop("MB-PC", 40, "WO-CASE-PC-A", seed=1661)
meas = sh["measurements"]
rows_q, cpk_min, fails, st = L.shop_table(meas)
vstat = st["mb_vcore"]
makemd = f"""# 制造：40 块台式机主板

计算机厂仿真车间 SMT 线做 40 块 MB-PC（{sh['hours']:.1f} 小时），在线测试记三项：

{L.md_table(["特性", "公差", "块数", "均值", "标准差", "Cpk"], rows_q)}

不合格 **{fails}**，最低 Cpk {cpk_min:.2f}。核心电压偏差标准差 {vstat['sd']:.2f} mV，第 3 步公差叠加预计 σ = {sigma:.2f} mV
（工厂数据 mb_vcore 的 σ 取 {sig_plant:g} mV，就是这个设计的结果）。
"""
case.step("make", f"40 块：核心电压偏差 σ {vstat['sd']:.2f} mV（预计 {sigma:.2f}），不合格 {fails}，最低 Cpk {cpk_min:.2f}。",
          f"40 boards: core-voltage deviation σ {vstat['sd']:.2f} mV (predicted {sigma:.2f}); {fails} failures, lowest Cpk {cpk_min:.2f}.",
          md=case.text("7_制造与测试.md", makemd), tools=tools("planner", "operator", "quality", "3d"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", round(cpk_min, 2), "")])
case.check("make", "工厂数据 mb_vcore 的 σ = 公差叠加结果（向上取 0.1 mV）", "Plant mb_vcore σ equals the tolerance stack (rounded up)", sig_plant, "==", math.ceil(sigma * 10) / 10, "mV", "第 3 步")
case.check("make", "不合格项", "Failures", fails, "==", 0, "", "在线测试")
case.check("make", "最低 Cpk", "Lowest Cpk", round(cpk_min, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **低电压大电流靠多相**：6 相把每相电流降到 {pm['iph']:.0f} A 以内，交错把输出纹波电流降到每相的 {pt['dio'] / pt['dip'] * 100:.0f} %。
2. **负载线让电容少一半**：AVP 下要的电容由“控制环带宽 + 负载线”决定（ζ 公式），仿真扫电容只数对上了公式。
3. **电压准不准是公差叠加出来的**：最大一项是基准 ±0.5 %；电流测量从电感 DCR 换成功率级内部测量，电压散布才进得了 ±{TOB:g} mV、Cpk 过 1.33——
   这个 σ 写进了工厂数据，工厂的合格率是设计决定的。

## 留给学生的问题

1. 开关频率从 500 kHz 提到 800 kHz：纹波、效率、需要的电容各怎么变？在“电路分析”里改网表 `4_稳态.cir` 试试。
2. 换 8 相能不能少用电容？（提示：电容由控制环带宽和负载线定，不直接由相数定。）
3. 笔记本主板 MB-NB 的 CPU 只有 45 W、核心电流约 60 A，几相合适？

相关：计算机厂帮助“主板、内存条、结构件与整机柜”；案例 B（服务器散热）、案例 C（算力中心）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；6 相、效率 {pt['eff'] * 100:.1f} %、电容 {c_tot * 1000:.2f} mF、电压 3σ {three_sigma:.1f} mV。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; 6 phases, {pt['eff'] * 100:.1f} % efficiency, {c_tot * 1000:.2f} mF, voltage 3σ {three_sigma:.1f} mV.",
          md=case.text("8_总结.md", review), tools=tools("circuit", "quality"))
case.write()
print("ok", round(loss_sim, 3), round(loss_hand, 3), m_ss["i0pp"], m_ss["iopp"], m_ss["vpp"], nom["under"], aged["under"], cpk_min, sigma)
