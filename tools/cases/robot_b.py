"""第 161c 轮：机器人厂案例 B——大关节模组 WQJ-L（J1、J2 用），模组里面：谐波减速器、输出轴承、抱闸、电机温升、扭转刚度。

    python3 tools/cases/robot_b.py

载荷来自机器人厂原件 cae/wqcr5.py（重力载荷 joint_loads、MuJoCo 标准动作）；谐波减速器参数取零件库 D-RDC-HD-CSF（厂商目录）；
刚度与固有频率用《机器人学》第 31 章的函数（_ch31.py）；制造用机器人厂仿真车间的关节测试台。输出到 factory/cases/robot/B/。
"""
from __future__ import annotations

import csv
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-robot.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory"), str(ROOT / "textbook" / "robotics" / "ch31" / "code")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
from cae import motors as MO, wqcr5 as W  # noqa: E402
import _ch31 as C31  # noqa: E402

TOOLS = {
    "configurator": ("参数配置器", "Configurator", "/configurator"),
    "library": ("零件与机器人库", "Parts & robot library", "/library"),
    "mbd": ("运动与动力分析", "Motion & dynamics", "/mbd"),
    "cae": ("仿真与分析", "Simulation & analysis", "/cae"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "q8d": ("质量异常单（8D）", "Quality issues (8D)", "/quality/8d"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

CSF = {}
with open(ROOT / "library" / "catalog" / "D" / "D-RDC-HD-CSF" / "specs.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["ratio"] == "100":
            CSF[int(r["size_code"])] = {k: float(r[k]) if r[k] else None for k in ("T_rated_Nm", "T_repeat_Nm", "T_avg_Nm", "T_momentary_Nm", "n_avg_grease_rpm", "n_max_grease_rpm", "OD_mm", "L_mm", "mass_kg")}
_b = L.lib_part("A-BRG-DG", "6010")["row"]
BRG_6010 = {"d": float(_b["d_mm"]), "D": float(_b["D_mm"]), "B": float(_b["B_mm"]), "C_kN": 22.9, "C0_kN": 16.0,
            "src": "尺寸取零件库 A-BRG-DG/6010；零件库没录额定载荷，C、C₀ 取 SKF 6010（RS Components 商品页 uk.rs-online.com/web/p/ball-bearings/2867776，查于 2026-11-12）"}
LIBP = [L.lib_part("D-RDC-HD-CSF", "32-100"), L.lib_part("A-BRG-DG", "6010"), L.lib_part("A-SCR-SHC", "M5x16")]
SPACING = 0.016                      # 两只输出轴承背靠背并排，中心距 = 轴承宽 16 mm（模组长度紧，第 5 步）
LIFE_H = 20000.0                     # 本案例设定：两班、约五年
I_R, ETA = W.GEAR_RATIO, W.ETA
mod = W.MODULES["L"]
motor = next(x for x in MO.MOTORS if x[0] == mod["motor"][0])
D = W.design()
JL = {j["joint"]: j for j in D["joints"]}

case = L.Case("robot", "B", "中等", "大关节模组 WQJ-L", "Large joint module WQJ-L", "WQJ-L",
              "J1、J2 用的大关节模组里面：谐波减速器按平均负载和峰值核对、输出轴承承受倾覆力矩、抱闸保持力矩、电机温升、扭转刚度对末端变形和固有频率的影响，再在关节测试台测 20 只。",
              "Inside the large joint module used on J1 and J2: strain-wave gear checked on average and peak torque, output bearings under tilting moment, brake holding torque, motor heating, torsional stiffness and its effect on TCP deflection and natural frequency; then 20 modules on the test bench.",
              "tools/cases/robot_b.py")

# ================================================================ 1 任务书
q_out = np.radians(W.OUTSTRETCHED_DEG)
ld = {j: W.joint_loads(q_out, j) for j in (0, 1)}
brief = f"""# 设计任务书：大关节模组 WQJ-L

**用在哪**　WQ-CR5 的 J1（底座，绕竖直轴转）和 J2（肩，绕水平轴转）。同一种模组，两个位置受力完全不同。

| 项目 | J1 | J2 | 出处 |
|---|---|---|---|
| 峰值力矩需求 | {JL['J1']['need_peak']:.0f} N·m | {JL['J2']['need_peak']:.0f} N·m | 案例 A（含安全系数 {W.SAFETY}） |
| 连续力矩需求 | {JL['J1']['need_rms']:.0f} N·m | {JL['J2']['need_rms']:.0f} N·m | 案例 A |
| 手臂伸直、5 kg 时的重力载荷 | 轴向 {abs(ld[0]['axial']):.0f} N、倾覆力矩 **{ld[0]['tilt']:.0f} N·m** | 径向 {ld[1]['radial']:.0f} N、驱动力矩 {ld[1]['tau']:.0f} N·m | `wqcr5.joint_loads` |
| 外形 | Ø{2000 * mod['r']:.0f} × {1000 * mod['h']:.0f} mm，{mod['mass']:g} kg | 同左 | `wqcr5.MODULES` |
| 寿命（本案例设定） | {LIFE_H:,.0f} h | 同左 | 两班、约五年 |
| 抱闸 | 断电时保持手臂不掉 | 同左 | 协作机器人安全要求 |

**里面装什么**：伺服电机 400 W（带失电制动抱闸，电机厂 WQ-SM400）+ 谐波减速器 CSF-32-100 + 一对深沟球轴承 6010 + 电机端和输出端两个编码器 + 驱动板 B 版。
"""
case.step("brief", f"同一只 WQJ-L 用在 J1（倾覆力矩 {ld[0]['tilt']:.0f} N·m）和 J2（峰值需求 {JL['J2']['need_peak']:.0f} N·m）；寿命设定 {LIFE_H:,.0f} h。",
          f"The same WQJ-L sits on J1 (tilting moment {ld[0]['tilt']:.0f} N·m) and J2 (peak demand {JL['J2']['need_peak']:.0f} N·m); life set at {LIFE_H:,.0f} h.",
          md=case.text("1_任务书.md", brief), tools=tools("library"),
          facts=[("J2 峰值需求", "J2 peak demand", JL["J2"]["need_peak"], "N·m"), ("J1 倾覆力矩", "J1 tilting moment", ld[0]["tilt"], "N·m")])

# ================================================================ 2 方案：谐波减速器尺寸
mt = lambda name: next(x for x in MO.MOTORS if x[0] == name)  # noqa: E731
opt_rows = []
for size, mname in ((25, "伺服 200 W"), (25, "伺服 400 W"), (32, "伺服 400 W"), (32, "伺服 750 W")):
    g = CSF[size]
    m_ = mt(mname)
    cap_peak = min(m_[3] * I_R * ETA, g["T_repeat_Nm"])
    cap_rated = min(m_[2] * I_R * ETA, g["T_rated_Nm"])
    ok = JL["J2"]["need_peak"] <= cap_peak and JL["J2"]["need_rms"] <= cap_rated
    opt_rows.append([f"CSF-{size}-100 + {mname}", f"Ø{g['OD_mm']:g} × {g['L_mm']:g}，{g['mass_kg']:g} kg", f"{cap_peak:.0f}", f"{cap_rated:.0f}",
                     "✓ 选定" if (size, mname) == (32, "伺服 400 W") else ("✓" if ok else "✗"),
                     "电机峰值不够" if not ok and m_[3] * I_R * ETA < JL["J2"]["need_peak"] else ("连续不够" if not ok else "")])
concept = f"""# 方案：谐波减速器多大、电机多大

J2 要峰值 {JL['J2']['need_peak']:.0f} N·m、连续 {JL['J2']['need_rms']:.0f} N·m（案例 A）。候选（减速器参数取零件库 D-RDC-HD-CSF 的厂商目录，减速比 100，η = {ETA}）：

{L.md_table(["组合", "减速器外形、质量", "峰值能力 N·m", "额定能力 N·m", "", "卡在"], opt_rows)}

25 号减速器连续能力只有 {CSF[25]['T_rated_Nm']:g} N·m，J2 的连续需求 {JL['J2']['need_rms']:.0f} 超了；32 号配 400 W 正好，750 W 电机没必要（重、贵、发热多）。
**选定 CSF-32-100 + 400 W**；模组外径由减速器外径 Ø{CSF[32]['OD_mm']:g} 定。
"""
case.step("concept", "25 号减速器连续能力不够 J2；选 CSF-32-100 + 400 W，模组外径由减速器 Ø110 定。",
          "Size 25 cannot carry J2's continuous torque; CSF-32-100 with 400 W chosen; the module diameter follows the Ø110 gear.",
          md=case.text("2_方案.md", concept), tools=tools("configurator") + [("零件库：CSF 谐波减速器", "Library: CSF gears", "/library?ref=D-RDC-HD-CSF/32-100")],
          facts=[("减速器", "Strain-wave gear", "CSF-32-100", ""), ("电机", "Motor", "400 W", "")])

# ================================================================ 3 计算（与第 4 步共用：MuJoCo 标准动作的 J1、J2 力矩与速度）
import mujoco  # noqa: E402

m = mujoco.MjModel.from_xml_string(W.mjcf(friction=True, payload_kg=W.PAYLOAD_KG))
m.opt.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_CONTACT) | int(mujoco.mjtDisableBit.mjDSBL_LIMIT)
dd = mujoco.MjData(m)
t = np.arange(0.0, W.runin_duration(), 0.005)
tau, qd = [], []
for x in t:
    q, v, a = W.runin_ref(x)
    dd.qpos[:6], dd.qvel[:6], dd.qacc[:6] = q, v, a
    mujoco.mj_inverse(m, dd)
    tau.append(dd.qfrc_inverse[:6].copy())
    qd.append(v)
tau, qd = np.array(tau), np.array(qd)
g32 = CSF[32]
rows, chk = [], {}
for k, jn in ((0, "J1"), (1, "J2")):
    T = tau[:, k] * W.SAFETY
    n_in = np.abs(qd[:, k]) * I_R * 60 / (2 * math.pi)
    moving = n_in > 1
    # 平均负载转矩（厂商目录的定义：按转速加权的 10/3 次方平均）
    T_av = (np.sum(n_in[moving] * np.abs(T[moving]) ** (10 / 3)) / np.sum(n_in[moving])) ** 0.3
    n_av = float(np.mean(n_in))
    T_pk = float(np.abs(T).max())
    T_es = motor[3] * I_R * ETA                      # 急停：电机峰值力矩全压在减速器上
    chk[jn] = dict(T_av=T_av, n_av=n_av, T_pk=T_pk)
    rows.append([jn, f"{T_av:.0f} / {g32['T_avg_Nm']:g}", f"{T_pk:.0f} / {g32['T_repeat_Nm']:g}", f"{T_es:.0f} / {g32['T_momentary_Nm']:g}",
                 f"{n_av:.0f} / {g32['n_avg_grease_rpm']:g}"])
# 输出轴承：一对 6010，中心距 SPACING；倾覆力矩 + 径向力分到两只
FP = 1.1
brg_rows, L10_min = [], math.inf
for j, jn in ((0, "J1"), (1, "J2")):
    l = ld[j]
    Fr_each = l["tilt"] / SPACING + l["radial"] / 2
    Fa = abs(l["axial"])
    X_, Y_ = (1.0, 0.0) if Fa / max(Fr_each, 1e-9) <= 0.3 else (0.56, 1.6)
    P = FP * (X_ * Fr_each + Y_ * Fa)
    n_out = float(np.mean(np.abs(qd[:, j]))) * 60 / (2 * math.pi)
    L10 = (BRG_6010["C_kN"] * 1e3 / P) ** 3 * 1e6 / (60 * max(n_out, 0.1))
    L10_min = min(L10_min, L10)
    brg_rows.append([jn, f"{l['tilt']:.1f} N·m", f"{l['radial']:.0f} / {Fa:.0f} N", f"{Fr_each:.0f} N", f"{P:.0f} N", f"{n_out:.1f} r/min", f"{L10:,.0f} h"])
# 抱闸：手臂伸直、带负载时 J2 的重力矩 × 安全系数
brake_min = 160.0                                   # 关节测试台抱闸保持力矩下限（机器人厂清单 joint_test）
brake_need = W.SAFETY * JL["J2"]["g_max"]
# 电机温升：标准动作下电机侧均方根力矩 / 额定
r_mot = MO.check(tau[:, 1], qd[:, 1], np.gradient(qd[:, 1], t), motor, next(x for x in MO.HARMONIC if x[0] == "谐波 32 号"), I_R)
calcmd = f"""# 计算书：WQJ-L 模组

## 谐波减速器 CSF-32-100（零件库 D-RDC-HD-CSF，厂商目录第 10、19 页）

MuJoCo 跑标准动作（5 kg 负载，乘安全系数 {W.SAFETY}）：

{L.md_table(["关节", "平均负载转矩 / 允许", "启停峰值 / 允许", "急停冲击 / 瞬时允许", "平均输入转速 / 允许 r/min"], rows)}

平均负载转矩按厂商目录的定义（按转速加权的 10/3 次方平均）——这一项决定减速器寿命；急停时电机峰值力矩 {motor[3]:g} N·m × {I_R} × {ETA} 全压在减速器上。

## 输出轴承：一对 6010（中心距 {SPACING * 1000:.0f} mm）

6010：d {BRG_6010['d']}、D {BRG_6010['D']}、B {BRG_6010['B']}，C = {BRG_6010['C_kN']} kN（{BRG_6010['src']}）。手臂伸直、5 kg：

{L.md_table(["关节", "倾覆力矩", "径向 / 轴向力", "每只轴承径向", "当量载荷 P", "平均转速", "L₁₀h"], brg_rows)}

**J1 的倾覆力矩比 J2 大十几倍**：J1 竖着装，整条手臂的重量都变成翻转它的力矩；J2 横着装，重力大部分变成驱动力矩。所以输出轴承按 J1 校核。

## 抱闸

断电时手臂伸直、带 5 kg，J2 的重力矩 {JL['J2']['g_max']:.0f} N·m × {W.SAFETY} = **{brake_need:.0f} N·m**；关节测试台的抱闸保持力矩下限 {brake_min:g} N·m（输出端）。

## 电机温升

标准动作下 J2 电机侧均方根力矩 {r_mot['motor_rms']:.2f} N·m，额定 {motor[2]:g} N·m（{r_mot['motor_rms'] / motor[2]:.0%}），连续运行温升在额定以内。
"""
case.step("calc", f"谐波平均负载 {chk['J2']['T_av']:.0f}/{g32['T_avg_Nm']:g} N·m；输出轴承按 J1 校核，最短寿命 {L10_min:,.0f} h；抱闸要 {brake_need:.0f} N·m，下限 {brake_min:g}。",
          f"Gear average torque {chk['J2']['T_av']:.0f}/{g32['T_avg_Nm']:g} N·m; output bearings checked for J1, shortest life {L10_min:,.0f} h; brake needs {brake_need:.0f} N·m against a {brake_min:g} minimum.",
          md=case.text("3_计算书.md", calcmd), tools=tools("library"),
          facts=[("谐波平均负载", "Gear average torque", chk["J2"]["T_av"], "N·m"), ("轴承寿命", "Bearing life", L10_min, "h"), ("抱闸需求", "Brake demand", brake_need, "N·m")])
case.check("calc", "谐波平均负载转矩（J1、J2 较大者）", "Gear average load torque (J1/J2 worst)", max(c["T_av"] for c in chk.values()), "<=", g32["T_avg_Nm"], "N·m", "厂商目录")
case.check("calc", "谐波启停峰值", "Gear repeated peak", max(c["T_pk"] for c in chk.values()), "<=", g32["T_repeat_Nm"], "N·m", "厂商目录")
case.check("calc", "急停冲击", "Emergency-stop torque", motor[3] * I_R * ETA, "<=", g32["T_momentary_Nm"], "N·m", "厂商目录")
case.check("calc", "输出轴承最短寿命", "Shortest output-bearing life", L10_min, ">=", LIFE_H, "h", "ISO 281")
case.check("calc", "抱闸保持力矩需求不超过测试下限", "Brake demand within the test minimum", brake_need, "<=", brake_min, "N·m", "关节测试台")
case.check("calc", "电机均方根力矩 / 额定", "Motor RMS torque / rated", r_mot["motor_rms"] / motor[2], "<=", 1.0, "", "电机选型助手")

# ================================================================ 4 仿真：扭转刚度 → 末端变形、固有频率
Kc = C31.harmonic_stiffness()[32]
d0 = C31.deflection(q_out)
tot = np.linalg.norm(sum(d0.values()))
share = {k: float(np.linalg.norm(v)) for k, v in d0.items()}
f_modes, _ = C31.modes(q_out, C31.joint_K(0))
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.4), gridspec_kw={"width_ratios": [1.4, 1]})
keys = [k for k in share if share[k] > 1e-6]
axs[0].barh(keys, [share[k] * 1e3 for k in keys], color=[L.ACCENT if k in ("J1", "J2") else "#8aa4bd" for k in keys])
axs[0].set_xlabel("末端在重力下的位移分量 / mm（手臂伸直、5 kg）")
th = np.linspace(0, 1.2, 100)
Tcurve = np.where(th < 0.3, th * Kc[0] / 1e3, np.where(th < 0.8, 0.3 * Kc[0] / 1e3 + (th - 0.3) * Kc[1] / 1e3, 0.3 * Kc[0] / 1e3 + 0.5 * Kc[1] / 1e3 + (th - 0.8) * Kc[2] / 1e3))
axs[1].plot(th, Tcurve, color=L.ACCENT)
axs[1].axhline(JL["J2"]["g_max"], color=L.BAD, ls=":", lw=0.8)
axs[1].text(0.02, JL["J2"]["g_max"] + 3, "J2 重力矩", color=L.BAD, fontsize=8.5)
axs[1].set_xlabel("扭转角 / mrad（示意三段折线）")
axs[1].set_ylabel("力矩 / N·m")
case.fig(fig, "4_刚度与变形.png")
simmd = f"""# 仿真：扭转刚度对整机的影响

谐波减速器不是刚体：CSF-32-100 的扭转刚度分三段 K₁ / K₂ / K₃ = {Kc[0]:,.0f} / {Kc[1]:,.0f} / {Kc[2]:,.0f} N·m/rad（零件库厂商数据）。
用《机器人学》31.2 节的方法，把每个柔性的地方（六个关节、大臂和小臂的弯曲、扭转）在重力下转的小角度乘力臂，叠出末端位移：

{L.md_table(["来源", "末端位移"], [[k, f"{v * 1000:.3f} mm"] for k, v in share.items() if v > 1e-6])}

合计约 **{tot * 1000:.2f} mm**，其中 **J2 一项占 {share['J2'] / sum(share.values()):.0%}**——大臂铝管弯曲只占 {share['upper_bend'] / sum(share.values()):.0%}。
想让机器人更“硬”，先换刚度更大的减速器，加粗铝管用处不大。

用关节刚度 K₁ 和 MuJoCo 的质量矩阵求固有频率（31.5 节）：一阶 **{f_modes[0]:.1f} Hz**、二阶 {f_modes[1]:.1f} Hz。
位置环带宽要避开这几个频率，否则一动就抖。
"""
case.step("sim", f"末端重力变形约 {tot * 1000:.2f} mm，J2 减速器扭转占 {share['J2'] / sum(share.values()):.0%}；一阶固有频率 {f_modes[0]:.1f} Hz。",
          f"TCP gravity deflection about {tot * 1000:.2f} mm, {share['J2'] / sum(share.values()):.0%} of it from J2 gear torsion; first natural frequency {f_modes[0]:.1f} Hz.",
          md=case.text("4_刚度与固有频率.md", simmd), figs=[("4_刚度与变形.png", "末端变形的来源；谐波减速器的扭转刚度", "Sources of TCP deflection; strain-wave gear torsional stiffness")],
          tools=tools("mbd", "cae"), facts=[("末端变形", "TCP deflection", tot * 1000, "mm"), ("一阶频率", "First mode", f_modes[0], "Hz")])
case.check("sim", "末端重力变形", "TCP gravity deflection", tot * 1000, "<=", 5.0, "mm", "本案例设定（标定前可补偿）")

# ================================================================ 5 结构示意与三维
import build123d as bd  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

R_mod = 1000 * mod["r"]
H_mod = 1000 * mod["h"]
STACK = [  # (名称, 长 mm, 外径, 内径, 颜色, 长度是否有出处)
    ("输出法兰", 8, 96, 50, "#9aa5b1", "本案例定"), ("6010", 16, 80, 50, "#7f9cb8", "GB/T 276"), ("6010", 16, 80, 50, "#7f9cb8", "GB/T 276"),
    ("谐波 CSF-32", g32["L_mm"], g32["OD_mm"], 30, "#d9a441", "厂商目录"), ("抱闸", 14, 70, 20, "#c0392b", "示意"), ("电机 400 W", 60, 70, 14, "#2c6fbb", "示意"),
    ("编码器 + 驱动板", 12, 90, 20, "#2f9e44", "示意")]
z = 0.0
parts = []
for name, ln, Do, Di, col, src in STACK:
    parts.append((name, z, ln, Do, Di, col))
    z += ln
L_out = sum(x[1] for x in STACK[:4])
L_need = z
fig, ax = plt.subplots(figsize=(8.6, 3.8))
for k, (name, z0, ln, Do, Di, col) in enumerate(parts):
    for sg in (1, -1):
        ax.add_patch(Rectangle((z0, Di / 2 if sg > 0 else -Do / 2), ln, (Do - Di) / 2, fc=col, ec="k", lw=0.6, alpha=0.85))
    ax.text(z0 + ln / 2, Do / 2 + 4 + (k % 2) * 9, name, ha="center", fontsize=8)
ax.axvline(H_mod, color=L.BAD, ls="--", lw=1)
ax.text(H_mod + 2, -64, f"模型里的模组长 {H_mod:.0f}", color=L.BAD if H_mod < L_need else L.MUTED, fontsize=8.5)
ax.text(L_need / 2, 0, "空心轴 Ø50（走线）", ha="center", va="center", fontsize=8.5)
ax.set_xlim(-10, L_need + 30)
ax.set_ylim(-70, 80)
ax.set_aspect("equal")
ax.set_xlabel("沿关节轴 / mm（输出端在左）")
ax.set_title("WQJ-L 零件沿轴向排开（法兰、轴承、减速器按目录；抱闸、电机、编码器长度示意）", fontsize=9.5)
case.fig(fig, "5_结构示意.png")
A0 = (bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
cut = bd.Pos(0, 60, L_need / 2) * bd.Box(140, 120, L_need + 20)          # 剖开一半看里面
solid = bd.Compound([bd.Pos(0, 0, z0) * (bd.Cylinder(Do / 2, ln, align=A0) - bd.Cylinder(Di / 2, ln, align=A0)) - cut for name, z0, ln, Do, Di, _ in parts]
                    + [(bd.Cylinder(R_mod, L_need, align=A0) - bd.Cylinder(R_mod - 4, L_need, align=A0)) - cut])
bd.export_step(solid, str(case.path("WQJ-L-示意.step")))
L.render_solid(solid, case.path("5_三维剖视.png"), elev=25, azim=-50, size=(7, 4.4))
if H_mod >= L_need:
    LEN_NOTE = (f"- **模组长度**：零件排下来约 **{L_need:.0f} mm**。最初的动力学模型（`wqcr5.MODULES`）只写了 110 mm——光输出法兰、两只轴承、减速器就占 {L_out:.0f} mm，"
                f"放不下抱闸、电机和编码器；这个案例发现后，第 165 轮把模型改成 {H_mod:.0f} mm（质量不变，惯量跟着变；案例 A、C 和实验 24–28 已复核）。"
                "抱闸、电机、编码器的长度还是示意值，电机厂定了 WQ-SM400 的外形后再核一次。")
    LEN_SHORT = f"零件排下来约 {L_need:.0f} mm，模型已按它改（第 165 轮）；电机外形定了以后再核。"
else:
    LEN_NOTE = (f"- **长度对不上**：动力学模型里（`wqcr5.MODULES`）WQJ-L 长 {H_mod:.0f} mm；光输出法兰、两只轴承、减速器就占 {L_out:.0f} mm，"
                f"只剩 {H_mod - L_out:.0f} mm 给抱闸、电机、编码器和驱动板，放不下。按示意长度排下来约 **{L_need:.0f} mm**，模型要回头改。")
    LEN_SHORT = f"零件排下来约 {L_need:.0f} mm，模型里只有 {H_mod:.0f} mm——要回头改模型，再复算案例 A。"
cadmd = f"""# 结构：零件沿轴向排开

{L.md_table(["零件", "长 mm", "外径", "出处"], [[n, f"{ln:g}", f"Ø{Do:g}", src] for n, ln, Do, Di, col, src in STACK])}

- 从输出端起：输出法兰 → 一对 6010（背靠背并排）→ 谐波减速器 CSF-32 → 失电制动抱闸 → 400 W 电机 → 电机端编码器与驱动板；输出端编码器读输出法兰；中间 Ø50 空心轴走线。
- 模组外径 Ø{2 * R_mod:.0f} 由减速器外径定。
{LEN_NOTE}
- 输出轴承因此只能并排（中心距 = 轴承宽 16 mm），第 3 步按这个跨距算了 J1 的轴承寿命。
"""
cadmd += f"""
## 用到的零件库零件

{L.lib_md(LIBP, {"D-RDC-HD-CSF/32-100": "谐波减速器（外径、长、质量、额定、峰值、刚度都取零件库）", "A-BRG-DG/6010": "输出轴承 ×2", "A-SCR-SHC/M5x16": "壳体、法兰联接 ×16"})}
"""
case.step("cad", f"零件沿轴向排开：法兰、两只 6010、CSF-32 就占 {L_out:.0f} mm；模型里模组长 {H_mod:.0f} mm 放不下电机，按示意排下来约 {L_need:.0f} mm，模型数据要更新。",
          f"Parts stacked along the axis: flange, two 6010s and the CSF-32 already take {L_out:.0f} mm; the model's {H_mod:.0f} mm module cannot hold the motor; about {L_need:.0f} mm by the sketch, so the model data must be updated.",
          md=case.text("5_结构.md", cadmd), figs=[("5_结构示意.png", "WQJ-L 零件沿轴向排开（红线：模型里的模组长度）", "WQJ-L parts along the axis (red: module length in the model)"), ("5_三维剖视.png", "三维剖视（示意）", "3D cut-away (schematic)")],
          files=[("WQJ-L-示意.step", "结构示意 STEP", "Layout (STEP)")], tools=L.lib_tools(LIBP),
          facts=[("输出端占长", "Output-end length", L_out, "mm"), ("排下来约", "Stack length", L_need, "mm")])
case.check("cad", "输出法兰、轴承、减速器的长度不超过模组长度", "Flange, bearings and gear fit within the module length", L_out, "<=", H_mod, "mm", "动力学模型 wqcr5.MODULES")

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

steps = ["壳体 JH-L 精车、铣、钻孔（机加工，工序见“设计与工艺”页）", "压装输出轴承（一对 6010，背靠背，加预紧垫片）", "装谐波减速器：刚轮固定在壳体上、柔轮接输出法兰、波发生器接电机轴",
         "装抱闸、电机、电机端编码器；装驱动板（向电路板厂买 DRV-JOINT-B）", "装输出端编码器（向传感器厂买 WQ-ENC17），对零位", "上关节测试台：背隙、空载摩擦力矩、编码器零位标定残差、抱闸保持力矩、双编码器互检差"]
procmd = f"""# 装配工艺与测试

工艺路线 {F.BOMS['WQJ-L'][0]}：{"、".join(f"{op}（{m} min）" for op, m in F.ROUTINGS[F.BOMS['WQJ-L'][0]])}。

装配顺序：

{chr(10).join(f"{i + 1}. {s}" for i, s in enumerate(steps))}

两点要特别控制：
- **背隙**：谐波减速器本身几乎没有背隙，测出来的背隙主要来自输出轴承游隙和法兰联接——轴承必须预紧；
- **抱闸保持力矩**：每只都测（{brake_min:g}–320 N·m，输出端），低于下限的不能出厂（第 3 步算出 J2 需要 {brake_need:.0f}）。
"""
case.step("process", "六步装配；轴承预紧控制背隙，抱闸每只都测。", "Six assembly steps; bearing preload controls backlash; every brake is tested.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("装配 + 测试", "Assembly + test", sum(m for _, m in F.ROUTINGS[F.BOMS['WQJ-L'][0]]), "min")])

# ================================================================ 7 制造
from hub import mrp  # noqa: E402

sh = L.run_shop("WQJ-L", 20, "WO-CASE-RB-B", seed=262)
rows_q, cpk_min, fails, st = L.shop_table(sh["measurements"])
mc, oc = mrp.std_unit_cost("WQJ-L")
makemd = f"""# 关节测试台测 20 只 WQJ-L

{L.md_table(["特性", "公差", "件数", "均值", "标准差", "Cpk"], rows_q)}

20 只、{len(sh['measurements'])} 个测量值，不合格 **{fails}** 个，最低 Cpk {cpk_min:.2f}；用时 {sh['hours']:.1f} 小时。
标准成本：材料 ${mc:.2f}（谐波减速器、电机、编码器、驱动板占大头）+ 加工 ${oc:.2f} = **${mc + oc:.2f} / 只**。

背隙超差时怎么查：实验 25（关节背隙异常的追因与 8D）。
"""
case.step("make", f"20 只、不合格 {fails} 个，最低 Cpk {cpk_min:.2f}；标准成本 ${mc + oc:.2f}/只。",
          f"20 modules, {fails} out of tolerance, lowest Cpk {cpk_min:.2f}; standard cost ${mc + oc:.2f} each.",
          md=case.text("7_制造与测试.md", makemd), tools=tools("planner", "operator", "quality", "q8d"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", cpk_min, ""), ("标准成本", "Standard cost", f"${mc + oc:.2f}", "")])
case.check("make", "20 只测量不合格数", "Out-of-tolerance values in 20 modules", fails, "==", 0, "", "关节测试台")
case.check("make", "最低过程能力 Cpk", "Lowest Cpk", cpk_min, ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

## 校核一览

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

## 这只模组的要点

1. **同一只模组，J1 和 J2 受力不一样**：J2 考驱动力矩（减速器、电机），J1 考倾覆力矩（输出轴承）。
2. 减速器按**平均负载转矩**（决定寿命）和启停峰值核对，不是只看额定。
3. **刚度在减速器上**：末端变形一大半来自 J2 的谐波减速器扭转，加粗铝管用处不大。
4. 抱闸保持力矩每只都测，要盖过 J2 最大重力矩的 {W.SAFETY} 倍。
5. **模组长度**：{LEN_SHORT}

## 留给学生的问题

1. 为什么很多协作臂用一只交叉滚子轴承代替一对深沟球轴承？用零件库里的交叉滚子轴承，模组能短多少？
2. 换成刚度更高的 CSG-32（假设刚度高 30%），末端变形、一阶固有频率各变多少？
3. 负载从 5 kg 加到 6 kg，抱闸下限 160 N·m 还够吗？
4. 在“质量”页找背隙的控制图，背隙变大时先查哪几样（参考实验 25）？

相关：《机器人学》第 30 章（模组选择）、第 31 章（刚度、模态）、第 32 章（齿轮与谐波传动）；实验 9、24、25；案例 A（选型）、案例 C（整机）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；J2 考减速器、J1 考轴承，刚度在减速器上；模组长约 {L_need:.0f} mm。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; J2 loads the gear, J1 the bearings; stiffness sits in the gear.",
          md=case.text("8_总结.md", review), tools=tools("library"))
case.write()
