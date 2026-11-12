"""第 161c 轮：机器人厂案例 A——WQ-CR5 六个关节配模组（关节选型），从需求到关节测试台测 30 只模组。

    python3 tools/cases/robot_a.py

尺寸综合与模组选择用机器人厂原件 cae/wqcr5.py 的 design()（教材《机器人学》30.3 节、数字工厂“参数配置器”同一段代码）；
动力学用 MuJoCo（cae/wqcr5.mjcf()）；候选组合用电机选型助手 cae/motors.py；制造用数字工厂仿真车间（机器人厂清单）。
输出到 factory/cases/robot/A/。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-robot.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
from cae import motors as MO, wqcr5 as W  # noqa: E402

TOOLS = {
    "configurator": ("参数配置器", "Configurator", "/configurator"),
    "library": ("零件与机器人库", "Parts & robot library", "/library"),
    "mbd": ("运动与动力分析", "Motion & dynamics", "/mbd"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "finance": ("经营与财务", "Business & finance", "/finance"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

D = W.design()
J = D["joints"]
case = L.Case("robot", "A", "简单", "WQ-CR5 六个关节配模组（关节选型）", "Choosing joint modules for the six joints of the WQ-CR5", "WQJ-L、WQJ-M、WQJ-S",
              "按负载、臂展、速度算出每个关节的峰值和连续力矩需求，从三种关节模组里给六个关节选型，用 MuJoCo 跑一遍标准动作核对，再在关节测试台测 30 只模组。",
              "Peak and continuous torque demands of each joint from payload, reach and speed; choose one of three joint modules for each of the six joints, check with a MuJoCo run of the standard motion, then test 30 modules on the joint test bench.",
              "tools/cases/robot_a.py")

# ================================================================ 1 任务书
brief = f"""# 设计任务书：WQ-CR5 的关节选型

**用途**　机器人厂的六轴协作机器人 WQ-CR5：上下料、装配、检测一类工位，人机协作。

| 项目 | 要求 | 出处 |
|---|---|---|
| 额定负载 | {D['payload_kg']:g} kg（法兰前 0.06 m 的钢块，跑合台标准负载） | 产品规格；`wqcr5.RUNIN_LOAD` |
| 臂展 | {D['reach_m'] * 1000:.0f} mm（大臂 {D['a2'] * 1000:.0f}、小臂 {D['a3'] * 1000:.0f}） | 《机器人学》30.3 节尺寸综合 |
| 速度 | 标准：关节设计角加速度 {D['accel_deg_s2']}°/s² | `wqcr5.DESIGN_ACCEL` |
| 安全系数 | 峰值和连续需求都乘 {W.SAFETY} | `wqcr5.SAFETY` |
| 关节模组 | 只用三种：WQJ-L（400 W + 谐波 32 号）、WQJ-M（200 W + 25 号）、WQJ-S（100 W + 17 号），减速比都是 {W.GEAR_RATIO} | 机器人厂清单 |
| 通用化 | J1 与 J2 同一种，腕部三个关节同一种（备件少、装配线简单） | 30.3 节 |

**要回答**：六个关节各装哪种模组？每个关节的峰值、连续力矩用了模组能力的多少？
"""
case.step("brief", f"{D['payload_kg']:g} kg、臂展 {D['reach_m'] * 1000:.0f} mm、设计角加速度 {D['accel_deg_s2']}°/s²；三种模组里给六个关节选。",
          f"{D['payload_kg']:g} kg, {D['reach_m'] * 1000:.0f} mm reach, {D['accel_deg_s2']}°/s² design acceleration; pick one of three modules for each joint.",
          md=case.text("1_任务书.md", brief), tools=tools("configurator", "library"),
          facts=[("负载", "Payload", D["payload_kg"], "kg"), ("臂展", "Reach", D["reach_m"] * 1000, "mm"), ("设计角加速度", "Design acceleration", D["accel_deg_s2"], "°/s²")])

# ================================================================ 2 方案
variants = [("标准：5 kg、860 mm、标准速度", W.PAYLOAD_KG, None, "standard"), ("快速：5 kg、860 mm、快速", W.PAYLOAD_KG, None, "fast"),
            ("长臂：5 kg、1000 mm", W.PAYLOAD_KG, 1000, "standard"), ("重载：7 kg、860 mm", 7.0, None, "standard"), ("轻载：3 kg、860 mm", 3.0, None, "standard")]
vrows = []
for name, pl, reach, sp in variants:
    d = W.design(payload_kg=pl, reach_mm=reach, speed=sp)
    mods = "、".join(W.MODULES[s]["code"][-1] for s in d["modules"]) if d["ok"] else "—（三种模组都不够）"
    vrows.append([name, mods, f"{d['mass_kg']:.1f} kg" if d["ok"] else "—", f"{max(j['use_rms'] for j in d['joints'] if j['use_rms']):.2f}" if d["ok"] else "—"])
own = [j["own"] for j in J]
concept = f"""# 方案：每个关节专门选，还是统一几种

## 只按每个关节自己的需求选

{L.md_table(["关节", "自己够用的最小模组", "通用化后"], [[j['joint'], j['own'], j['module']] for j in J])}

J1 自己用 WQJ-M 就够（它只转动、不抬重），但和 J2 统一成 WQJ-L：底座和肩部一种模组，备件、装配工装都少一种。腕部三个关节本来就是同一种。

## 改需求会怎样（同一段选型程序）

{L.md_table(["需求", "J1–J6 模组", "整机质量", "最紧的连续利用率"], vrows)}

- 快速、长臂、重载都会让模组不够或升级；轻载可以省成本，但会多出一种整机型号。
- **选定标准方案**：J1、J2 用 L，J3 用 M，J4–J6 用 S（与机器人厂清单一致）。
"""
case.step("concept", "J1 自己用 M 就够，与 J2 统一成 L；比较了快速、长臂、重载、轻载四种需求下的选型；选定 L、L、M、S、S、S。",
          "J1 alone would need only M but is unified with J2 as L; four other requirement sets compared; L, L, M, S, S, S chosen.",
          md=case.text("2_方案.md", concept), tools=tools("configurator"),
          facts=[("模组", "Modules", "L L M S S S", ""), ("整机质量", "Robot mass", D["mass_kg"], "kg")])
case.check("concept", "标准需求下三种模组够用", "Three modules suffice for the standard requirement", 1 if D["ok"] else 0, "==", 1, "", "30.3 节")

# ================================================================ 3 计算
rows = [[j["joint"], j["module"], f"{j['g_max']:.1f}", f"{j['M_max']:.3f}", f"{j['need_peak']:.1f}", f"{j['cap_peak']:.0f}", f"{j['use_peak']:.2f}",
         f"{j['need_rms']:.1f}", f"{j['cap_rated']:.1f}", f"{j['use_rms']:.2f}"] for j in J]
calcmd = f"""# 计算：每个关节的需求与模组能力

**峰值需求** = {W.SAFETY} × (最大重力矩 g_max + 最大连杆惯量 M_ii × 设计角加速度)，J2–J5 的角度按 30° 网格取遍（MuJoCo 逆动力学，不含转子）；电机还要带转子加速（折到关节侧 J_m i²）。
**连续需求** = {W.SAFETY} × 跑合台标准动作各关节力矩的均方根（含转子惯量）。
**模组能力**：峰值 = min(电机峰值 × i × η，谐波重复峰值)，额定 = min(电机额定 × i × η，谐波额定)，i = {W.GEAR_RATIO}，η = {W.ETA}。

{L.md_table(["关节", "模组", "g_max N·m", "M_max kg·m²", "峰值需求", "峰值能力", "利用率", "连续需求", "额定能力", "利用率"], rows)}

- **J2（肩）峰值最大**：手臂水平伸直时重力矩 {J[1]['g_max']:.0f} N·m。
- **J3（肘）连续利用率 {J[2]['use_rms']:.2f}**，是全机最紧的地方：J3 用 M 模组，200 W 电机的额定力矩 × 100 × 0.75 = {J[2]['cap_rated']:.1f} N·m，标准动作的均方根需求 {J[2]['need_rms']:.1f}。
  动作再快一点或者负载再重一点，J3 就要升 L（第 2 步“快速”“重载”两行）。
"""
# 零件库复核：三种模组的谐波减速器用零件库 D-RDC-HD-CSF（厂商目录）的值，模型 wqcr5.MODULES 里写的是电机选型助手的通用典型值
LIBH = {k: L.lib_part("D-RDC-HD-CSF", {"L": "32-100", "M": "25-100", "S": "17-100"}[k]) for k in ("L", "M", "S")}
lib_rows, lib_cap = [], {}
for k, v in W.MODULES.items():
    r_ = LIBH[k]["row"]
    Tr, Tp = float(r_["T_rated_Nm"]), float(r_["T_repeat_Nm"])
    mo = next(x for x in MO.MOTORS if x[0] == v["motor"][0])
    lib_cap[k] = {"peak": min(mo[3] * W.GEAR_RATIO * W.ETA, Tp), "rated": min(mo[2] * W.GEAR_RATIO * W.ETA, Tr)}
    lib_rows.append([v["code"], LIBH[k]["ref"], f"{v['gear'][1]:g} / {Tr:g}", f"{v['gear'][2]:g} / {Tp:g}", "一致" if (v["gear"][1], v["gear"][2]) == (Tr, Tp) else "**不一致**"])
lib_use = max(max(j["need_peak"] / lib_cap[W.JOINT_MODULE[i]]["peak"], j["need_rms"] / lib_cap[W.JOINT_MODULE[i]]["rated"]) for i, j in enumerate(J))
calcmd += f"""
## 用零件库复核减速器参数

模型（`wqcr5.MODULES`）里的谐波减速器额定、重复峰值是电机选型助手的通用典型值；零件库 D-RDC-HD-CSF 存的是厂商目录：

{L.md_table(["模组", "零件库编号", "额定 N·m（模型 / 零件库）", "重复峰值 N·m（模型 / 零件库）", ""], lib_rows)}

**25 号的重复峰值模型写 178，厂商目录是 157**——以零件库为准：J3 的峰值能力变成 {lib_cap['M']['peak']:.0f} N·m，需求 {J[2]['need_peak']:.0f}，仍然够。
按零件库的值，六个关节最紧的一项利用率 {lib_use:.2f}。模型里的数据要改成零件库的（改了以后实验 9、24–28 的数字要一起核对）。
"""
case.check("calc", "按零件库减速器参数的最大利用率", "Largest utilisation with library gear data", lib_use, "<=", 1.0, "", "零件库 D-RDC-HD-CSF")
case.step("calc", f"J2 峰值需求 {J[1]['need_peak']:.0f} N·m（利用率 {J[1]['use_peak']:.2f}）；J3 连续利用率 {J[2]['use_rms']:.2f}，全机最紧。",
          f"J2 peak demand {J[1]['need_peak']:.0f} N·m (utilisation {J[1]['use_peak']:.2f}); J3 continuous utilisation {J[2]['use_rms']:.2f}, the tightest in the robot.",
          md=case.text("3_计算.md", calcmd), tools=tools("configurator") + L.lib_tools(list(LIBH.values())),
          facts=[("J2 峰值需求", "J2 peak demand", J[1]["need_peak"], "N·m"), ("J3 连续利用率", "J3 continuous use", J[2]["use_rms"], "")])
case.check("calc", "六个关节峰值利用率最大值", "Largest peak utilisation", max(j["use_peak"] for j in J), "<=", 1.0, "", "30.3 节")
case.check("calc", "六个关节连续利用率最大值", "Largest continuous utilisation", max(j["use_rms"] for j in J), "<=", 1.0, "", "30.3 节")

# ================================================================ 4 仿真：MuJoCo 跑标准动作，电机侧核对
import mujoco  # noqa: E402

m = mujoco.MjModel.from_xml_string(W.mjcf(friction=True, payload_kg=W.PAYLOAD_KG))
m.opt.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_CONTACT) | int(mujoco.mjtDisableBit.mjDSBL_LIMIT)
d_ = mujoco.MjData(m)
t = np.arange(0.0, W.runin_duration(), 0.005)
tau, qd_all, qdd_all = [], [], []
for x in t:
    q, qd, qdd = W.runin_ref(x)
    d_.qpos[:6], d_.qvel[:6], d_.qacc[:6] = q, qd, qdd
    mujoco.mj_inverse(m, d_)
    tau.append(d_.qfrc_inverse[:6].copy())
    qd_all.append(qd)
    qdd_all.append(qdd)
tau, qd_all, qdd_all = np.array(tau), np.array(qd_all), np.array(qdd_all)
lim = W.torque_limit()
fig, axs = plt.subplots(2, 3, figsize=(10, 5.2), sharex=True)
sim_rows = []
for k in range(6):
    ax = axs.flat[k]
    ax.plot(t, tau[:, k], color=L.ACCENT, lw=1.1)
    ax.axhline(lim[k], color=L.BAD, ls=":", lw=0.8)
    ax.axhline(-lim[k], color=L.BAD, ls=":", lw=0.8)
    ax.set_title(f"{W.JOINTS[k]}（{W.MODULES[W.JOINT_MODULE[k]]['code']}）", fontsize=9.5)
    ax.set_ylim(-1.15 * max(lim[k], np.abs(tau[:, k]).max()), 1.15 * max(lim[k], np.abs(tau[:, k]).max()))
    mod = W.MODULES[W.JOINT_MODULE[k]]
    mt = next(x for x in MO.MOTORS if x[0] == mod["motor"][0])
    mg = next(x for x in MO.HARMONIC if x[0] == mod["gear"][0])
    r = MO.check(tau[:, k], qd_all[:, k], qdd_all[:, k], mt, mg, W.GEAR_RATIO)
    sim_rows.append([W.JOINTS[k], f"{np.abs(tau[:, k]).max():.1f}", f"{np.sqrt(np.mean(tau[:, k] ** 2)):.1f}", f"{r['motor_peak']:.2f} / {mt[3]:g}",
                     f"{r['motor_rms']:.2f} / {mt[2]:g}", f"{r['motor_speed_rpm']:.0f} / {min(mt[4], mg[3])}", MO.WORST_NAME[r["worst"]], "✓" if r["ok"] else "✗"])
for ax in axs[1]:
    ax.set_xlabel("t / s")
for ax in axs[:, 0]:
    ax.set_ylabel("关节力矩 / N·m")
case.fig(fig, "4_标准动作关节力矩.png")
all_ok = all(r_[-1] == "✓" for r_ in sim_rows)
simmd = f"""# 仿真：MuJoCo 跑一遍跑合台的标准动作

带 {W.PAYLOAD_KG:g} kg 标准负载，从初始位姿经过三个位姿再回来（每段五次多项式 {W.RUNIN_SEG_S} s，段间停 {W.RUNIN_DWELL_S} s），
MuJoCo 逆动力学（含关节摩擦、转子惯量）算每个关节的力矩。红色虚线是模组的力矩上限。

再把关节力矩换到电机侧（τ_m = τ/(iη) + J_m α i），按电机选型助手的规则逐项核对（电机峰值 / 额定、转速）：

{L.md_table(["关节", "关节峰值 N·m", "关节均方根", "电机峰值 / 允许", "电机均方根 / 额定", "电机转速 / 允许 r/min", "最紧的一项", ""], sim_rows)}

这一段动作不带 {W.SAFETY} 倍的安全系数，所以比第 3 步的需求低；第 3 步的选型留够了余量。
"""
case.step("sim", f"MuJoCo 跑标准动作（带 {W.PAYLOAD_KG:g} kg），六个关节的电机峰值、均方根、转速都在额定内。",
          f"MuJoCo run of the standard motion with {W.PAYLOAD_KG:g} kg: motor peak, RMS and speed within rating on all six joints.",
          md=case.text("4_动力学仿真.md", simmd), figs=[("4_标准动作关节力矩.png", "标准动作中六个关节的力矩（红线：模组上限）", "Joint torques in the standard motion (red: module limits)")],
          tools=tools("mbd"), facts=[("J2 峰值", "J2 peak", float(np.abs(tau[:, 1]).max()), "N·m"), ("动作时长", "Motion time", W.runin_duration(), "s")])
case.check("sim", "六个关节电机侧校核", "Motor-side checks on six joints", 1 if all_ok else 0, "==", 1, "", "电机选型助手")

# ================================================================ 5 三维：整机模型（模组按选型着色）
import build123d as bd  # noqa: E402

import robotgeom as RG  # noqa: E402

arm = RG.arm_solid()
bd.export_step(arm, str(case.path("WQ-CR5.step")))
L.render_solid(arm, case.path("5_整机三维.png"), elev=18, azim=-60, size=(7, 6), swap=False)
mod_rows = [[k, v["code"], v["motor"][0], v["gear"][0], f"{v['mass']:g} kg", f"Ø{2000 * v['r']:.0f} × {1000 * v['h']:.0f}",
             "、".join(W.JOINTS[i] for i, s in enumerate(W.JOINT_MODULE) if s == k)] for k, v in W.MODULES.items()]
cadmd = f"""# 三维：整机模型与三种模组

整机三维由 `wqcr5.link_parts()` 的零件几何生成（与 MuJoCo 模型、零件库 B-ARM-WQCR5 同一份数据），初始位姿 {W.HOME_DEG}。

{L.md_table(["模组", "物料", "电机", "谐波减速器", "质量", "外形", "装在"], mod_rows)}

整机质量 {W.total_mass():.1f} kg，运动部分 {sum(l['mass'] for l in W.links()):.1f} kg。三种模组的内部结构见案例 B。
"""
cadmd += "\n零件库里有这台机器人（`B-ARM-WQCR5`，三维、DH、质量与本模型同一份）和三种谐波减速器（`D-RDC-HD-CSF`）。\n"
case.step("cad", f"由同一份模型数据生成整机三维；三种模组 L / M / S 装在 J1–J2 / J3 / J4–J6；整机 {W.total_mass():.1f} kg。",
          f"Robot 3D generated from the same model data; modules L / M / S on J1–J2 / J3 / J4–J6; {W.total_mass():.1f} kg.",
          md=case.text("5_三维.md", cadmd), figs=[("5_整机三维.png", "WQ-CR5 整机（初始位姿）", "WQ-CR5 in the home pose")],
          files=[("WQ-CR5.step", "整机 STEP", "Robot (STEP)")], tools=[("零件库：WQ-CR5", "Library: WQ-CR5", "/library?ref=B-ARM-WQCR5")],
          facts=[("整机质量", "Robot mass", W.total_mass(), "kg")])

# ================================================================ 6 工艺：关节模组的装配与测试
from factory import data as F  # noqa: E402

routing = F.ROUTINGS[F.BOMS["WQJ-L"][0]]
proc_rows = [[i + 1, op, F.OPERATIONS[op], mins] for i, (op, mins) in enumerate(routing)]
comp_rows = [[c, F.ITEMS[c][0] if c in F.ITEMS else c, q] for c, q in F.BOMS["WQJ-L"][1]]
procmd = f"""# 工艺：关节模组的装配与测试

三种模组同一条工艺路线（{F.BOMS['WQJ-L'][0]}）：

{L.md_table(["工序", "名称", "设备", "工时 / min"], proc_rows)}

WQJ-L 的物料清单：

{L.md_table(["物料", "名称", "用量"], comp_rows)}

关节测试台逐只测五项（与机器人厂清单 `joint_test` 一致）：背隙、空载摩擦力矩、编码器零位标定残差、抱闸保持力矩、双编码器互检差。
电机向电机厂买、编码器向传感器厂买、驱动板向电路板厂买（问渠数字工业园）。
"""
case.step("process", f"三种模组同一条路线：装配 {routing[0][1]} min、测试 {routing[1][1]} min；测试台逐只测五项。",
          f"One routing for all three modules: assembly {routing[0][1]} min, test {routing[1][1]} min; five characteristics tested on every module.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("测试项", "Test items", 5, "")])

# ================================================================ 7 制造：测 30 只模组
from hub import mrp  # noqa: E402

allm, cost_rows, hours = [], [], {}
for code in ("WQJ-L", "WQJ-M", "WQJ-S"):
    sh = L.run_shop(code, 10, f"WO-CASE-RB-A-{code}", seed=161)
    allm += sh["measurements"]
    hours[code] = sh["hours"]
    mc, oc = mrp.std_unit_cost(code)
    cost_rows.append([code, f"${mc:.2f}", f"${oc:.2f}", f"**${mc + oc:.2f}**"])
rows_q, cpk_min, fails, st = L.shop_table(allm)
makemd = f"""# 关节测试台测 30 只模组

WQJ-L、WQJ-M、WQJ-S 各下一张 10 只的工单，在机器人厂的仿真车间装配、上关节测试台（各用 {hours['WQJ-L']:.1f} / {hours['WQJ-M']:.1f} / {hours['WQJ-S']:.1f} 小时）：

{L.md_table(["特性", "公差", "件数", "均值", "标准差", "Cpk"], rows_q)}

30 只模组共 {len(allm)} 个测量值，不合格 **{fails}** 个，最低 Cpk {cpk_min:.2f}。

**标准成本**（零件按清单逐层汇总，电机、编码器、驱动板按向兄弟厂的采购价）：

{L.md_table(["模组", "材料", "加工", "合计 / 只"], cost_rows)}

想自己走一遍：在“订单与计划”接一台 WQ-CR5，算料会展开出 6 只模组的工单；“质量”页看关节测试的控制图；实验 25 就是这个测试台上的追因。
"""
case.step("make", f"30 只模组 {len(allm)} 个测量值、不合格 {fails} 个，最低 Cpk {cpk_min:.2f}。",
          f"30 modules, {len(allm)} measurements, {fails} out of tolerance, lowest Cpk {cpk_min:.2f}.",
          md=case.text("7_制造与测试.md", makemd), tools=tools("planner", "operator", "quality", "finance"),
          facts=[("测量值", "Measurements", len(allm), ""), ("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", cpk_min, "")])
case.check("make", "30 只模组测量不合格数", "Out-of-tolerance values in 30 modules", fails, "==", 0, "", "关节测试台")
case.check("make", "关节测试最低过程能力 Cpk", "Lowest Cpk of the joint test", cpk_min, ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

## 校核一览

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

## 选型结论

1. J1、J2 用 WQJ-L，J3 用 WQJ-M，J4–J6 用 WQJ-S。J1 本来 M 就够，为了通用化用 L。
2. 最紧的是 **J3 的连续力矩**（利用率 {J[2]['use_rms']:.2f}）：加快节拍或加大负载时先升 J3。
3. 峰值最大的是 J2，但离上限还远（利用率 {J[1]['use_peak']:.2f}）。

## 留给学生的问题

1. 在“参数配置器”里把负载改成 6 kg，哪个关节先不够？
2. J3 改用 L 模组：整机质量、J2 的需求、成本各变多少？
3. 标准动作里 J3 的力矩均方根主要来自重力还是惯性？把动作时间加倍再算一次。
4. 第 7 步哪一项的 Cpk 最低？它由哪个零件、哪道工序决定（参考实验 25）？

相关：《机器人学》第 30 章（需求分析、尺寸综合与模组选择）、第 24 章（动力学），实验 9（关节力矩与电机选型）、实验 24、25、28；案例 B（关节模组内部）、案例 C（整机）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；L、L、M、S、S、S，最紧的是 J3 连续力矩。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; L, L, M, S, S, S; J3 continuous torque is the tightest.",
          md=case.text("8_总结.md", review), tools=tools("configurator"))
case.write()
