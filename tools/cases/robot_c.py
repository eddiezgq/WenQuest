"""第 161c 轮：机器人厂案例 C——六轴协作机器人 WQ-CR5 整机：臂长分配、连杆受力与有限元、刚度与频率、整机装配、运动学标定、负载跑合、出厂 5 台。

    python3 tools/cases/robot_c.py

几何、质量、载荷用机器人厂原件 cae/wqcr5.py；大臂有限元用数字工厂“仿真与分析”的结构示例 cae/struct_parts.py + cae/solve.py（CalculiX）；
刚度与固有频率用《机器人学》第 31 章 _ch31.py；整机标定用 sim/calib.py（实验 26 同一段代码）；制造用机器人厂仿真车间。
输出到 factory/cases/robot/C/。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-robot.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory"), str(ROOT / "textbook" / "robotics" / "ch31" / "code")]
os.environ.setdefault("WQ_CCX_SOLVER", "SPOOLES")

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402
from cae import wqcr5 as W  # noqa: E402
import _ch31 as C31  # noqa: E402

TOOLS = {
    "configurator": ("参数配置器", "Configurator", "/configurator"),
    "library": ("零件与机器人库", "Parts & robot library", "/library"),
    "mbd": ("运动与动力分析", "Motion & dynamics", "/mbd"),
    "cae": ("仿真与分析", "Simulation & analysis", "/cae"),
    "calib": ("整机标定", "Robot calibration", "/calib"),
    "lab28": ("负载跑合", "Load run-in", "/lab28"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间终端", "Shop-floor terminal", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "finance": ("经营与财务", "Business & finance", "/finance"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

S = W.summary()
case = L.Case("robot", "C", "完整", "六轴协作机器人 WQ-CR5（整机）", "Six-axis collaborative robot WQ-CR5 (complete)", "WQ-CR5",
              "整台协作机器人：臂长怎么分、连杆受力与大臂有限元、末端变形与固有频率、整机装配、激光跟踪仪标定、负载跑合，再在机器人厂出厂 5 台。",
              "The complete cobot: splitting the reach, link loads and upper-arm FEA, TCP deflection and natural frequency, assembly, laser-tracker calibration, load run-in, and 5 robots dispatched.",
              "tools/cases/robot_c.py")

# ================================================================ 1 任务书
brief = f"""# 设计任务书：六轴协作机器人 WQ-CR5

| 项目 | 要求 | 出处 |
|---|---|---|
| 负载 | {W.PAYLOAD_KG:g} kg | 产品规格 |
| 臂展 | {S['reach_mm']} mm | 产品规格 |
| 位置重复精度 | ≤ ±0.03 mm | 机器人厂出厂检验 |
| 绝对定位误差（标定后） | ≤ 0.5 mm | 出厂检验；`sim/calib.LIMIT_MM` |
| 整机质量 | 尽量轻（参考 20 kg 以内） | 协作机器人常见量级 |
| 关节模组 | J1、J2 WQJ-L，J3 WQJ-M，J4–J6 WQJ-S | 案例 A |
| 臂管 | 6061-T6 铝合金管：大臂 Ø{2000 * W.TUBES['upper'][0]:.0f}×{1000 * W.TUBES['upper'][1]:.0f}、小臂 Ø{2000 * W.TUBES['fore'][0]:.0f}×{1000 * W.TUBES['fore'][1]:.0f} | 《机器人学》第 31 章 |

**交付物**：臂长分配、连杆受力与有限元、刚度与频率、三维与 DH 参数、装配与标定工艺、首批 5 台的出厂记录与成本。
"""
case.step("brief", f"{W.PAYLOAD_KG:g} kg、臂展 {S['reach_mm']} mm；重复精度 ±0.03 mm，标定后绝对误差 ≤ 0.5 mm；模组用案例 A 的选型。",
          f"{W.PAYLOAD_KG:g} kg, {S['reach_mm']} mm reach; ±0.03 mm repeatability, ≤ 0.5 mm absolute error after calibration; modules from case A.",
          md=case.text("1_任务书.md", brief), tools=tools("configurator", "library"),
          facts=[("负载", "Payload", W.PAYLOAD_KG, "kg"), ("臂展", "Reach", S["reach_mm"], "mm"), ("整机质量", "Mass", S["mass_kg"], "kg")])

# ================================================================ 2 方案：臂长分配
q_out = np.radians(W.OUTSTRETCHED_DEG)
rows = []
for a2, a3 in ((0.38, 0.38), (0.40, 0.36), (0.42, 0.34)):
    with W.geometry(a2=a2, a3=a3):
        d = W.design(reach_mm=S["reach_mm"])
        jl = {j["joint"]: j for j in d["joints"]}
        defl = float(np.linalg.norm(sum(C31.deflection(q_out).values()))) * 1000
        rows.append([f"{a2 * 1000:.0f} / {a3 * 1000:.0f}", f"{abs(a2 - a3) * 1000:.0f} mm", f"{jl['J2']['need_peak']:.0f}", f"{jl['J3']['use_rms']:.2f}",
                     f"{defl:.2f} mm", "✓ 选定" if abs(a2 - 0.40) < 1e-9 else ""])
concept = f"""# 方案：臂展 {S['reach_mm']} mm 怎么分给大臂、小臂

a₂ + a₃ = 臂展 − d₅。大臂比小臂长一点，手腕能收到底座附近（“死区”小）；但大臂越长，J2 的重力矩越大。

{L.md_table(["大臂 / 小臂 mm", "大小臂差", "J2 峰值需求 N·m", "J3 连续利用率", "末端重力变形", ""], rows)}

《机器人学》30.3 节按“死区 {W.DEAD_ZONE * 1000:.0f} mm”取 a₂ − a₃，得 400 / 360；三个方案模组都一样，差别在 J2 力矩和变形上很小。**选定 400 / 360**。
构型是常见的 UR 式：J2、J3、J4 三个平行轴，腕部偏置——运动学有封闭解，标定时 J2–J4 的轴向偏距只辨识得出和（第 7 步）。
"""
case.step("concept", "比较三种大小臂分配；按死区取 400 / 360，模组不变，差在 J2 力矩和变形上很小。",
          "Three upper/forearm splits compared; 400 / 360 chosen by the dead-zone rule; modules unchanged, small differences in J2 torque and deflection.",
          md=case.text("2_方案.md", concept), tools=tools("configurator"), facts=[("大臂 / 小臂", "Upper / forearm", "400 / 360", "mm")])

# ================================================================ 3 计算：连杆截面内力、管的应力
mat = {"E": W.E_AL, "yield": W.YIELD_AL}
sec_rows, sf_min = [], math.inf
for i, nm, key in ((1, "大臂", "upper"), (2, "小臂", "fore")):
    r, t_ = W.TUBES[key]
    pr = C31.tube_props(r, t_)
    for s_, pos in ((0.0, "根部"), (0.5, "中间"), (1.0, "端部")):
        sec = W.section(q_out, i, s_)
        sig = sec["Mb"] / (pr["I"] / r)
        tau = abs(sec["T"]) * r / pr["J"]
        vm = math.sqrt(sig ** 2 + 3 * tau ** 2)
        sf = W.YIELD_AL / vm
        sf_min = min(sf_min, sf)
        sec_rows.append([nm, pos, f"{sec['Mb']:.1f}", f"{sec['T']:.2f}", f"{sec['V']:.0f}", f"{vm / 1e6:.1f}", f"{sf:.0f}"])
calcmd = f"""# 计算：连杆截面内力与臂管应力

手臂水平伸直、工具朝下、带 {W.PAYLOAD_KG:g} kg（J2 重力矩接近最大的姿态），用 `wqcr5.section()` 求截面外侧所有零件（模组、管、罩壳、负载）的重力对截面形心的合力和合力矩：

{L.md_table(["连杆", "截面", "弯矩 N·m", "扭矩 N·m", "剪力 N", "冯·米塞斯应力 MPa", "对屈服的安全系数"], sec_rows)}

6061-T6 屈服强度 {W.YIELD_AL / 1e6:.0f} MPa。**应力只有几兆帕，强度富余几十倍**——协作机器人的臂管是按**刚度**和**重量**定的，不是按强度。
臂管外径由里面要穿的线缆和关节模组的法兰定，壁厚 3 mm 已经接近铝管能稳定加工的下限。
"""
case.step("calc", f"伸直带 {W.PAYLOAD_KG:g} kg，大臂根部弯矩最大；应力只有几 MPa，对屈服的安全系数最小 {sf_min:.0f}：臂管按刚度和重量定，不按强度。",
          f"Outstretched with {W.PAYLOAD_KG:g} kg the upper-arm root carries the largest moment; stresses are only a few MPa, minimum yield safety factor {sf_min:.0f}: tubes are sized by stiffness and weight, not strength.",
          md=case.text("3_计算.md", calcmd), tools=tools("cae"), facts=[("最小安全系数", "Lowest safety factor", sf_min, "")])
case.check("calc", "臂管对屈服的最小安全系数", "Lowest yield safety factor of the arm tubes", sf_min, ">=", 3.0, "", "《机器人学》31.1 节")

# ================================================================ 4 仿真：大臂有限元（CalculiX）+ 末端变形与固有频率
from cae import geometry as GE, materials as MA, solve as SV, struct_parts as SP  # noqa: E402

p = SP.params_of("wqcr5_upper")
step = SP.build("wqcr5_upper", p)
faces, _, _ = GE.faces(step)
ex = SP.example("wqcr5_upper", p, faces)
loads = []
for row in ex["rows"]:
    if row["kind"] == "fixed":
        loads.append({"type": "fixed", "faces": row["faces"]})
    elif row["kind"] == "force":
        loads.append({"type": "force", "faces": row["faces"], "vector_n": [row["fx"], row["fy"], row["fz"]]})
    elif row["kind"] == "moment":
        loads.append({"type": "moment", "faces": row["faces"], "vector_nmm": [1000 * row["mx"], 1000 * row["my"], 1000 * row["mz"]]})
stats, surf, _ = SV.solve(step, {"material": MA.get(ex["material_id"]), "loads": loads, "mesh": {"size_mm": ex["mesh_mm"]}})
fo = ex["formula"]
d_all = C31.deflection(q_out)
tot = float(np.linalg.norm(sum(d_all.values())))
share = {k: float(np.linalg.norm(v)) for k, v in d_all.items()}
f_modes, _ = C31.modes(q_out, C31.joint_K(0))
fig, ax = plt.subplots(figsize=(8.4, 3.2))
keys = [k for k in share if share[k] > 1e-6]
ax.barh(keys, [share[k] * 1e3 for k in keys], color=[L.ACCENT if k.startswith("J") else "#8aa4bd" for k in keys])
ax.set_xlabel("末端重力变形的来源 / mm（手臂伸直、5 kg）")
case.fig(fig, "4_末端变形来源.png")
vm_fe = stats.get("vm_max_mpa") or stats.get("von_mises_max_mpa") or stats.get("max_vm_mpa")
disp_fe = stats.get("disp_max_mm") or stats.get("u_max_mm")
vm_fe = round(float(vm_fe), 2) if vm_fe is not None else None
disp_fe = round(float(disp_fe), 3) if disp_fe is not None else None
simmd = f"""# 仿真：大臂有限元、整机变形与固有频率

## 大臂有限元（数字工厂“仿真与分析”的结构示例“WQ-CR5 大臂”，CalculiX）

大臂 = 6061-T6 铝管 Ø{p['D']:g}×{p['t']:g} + 两端法兰（厚 {p['flange_t']:g}，线缆孔 Ø{p['bore']:g}），长 {p['L']:g} mm。J2 端固定，J3 端加伸直、5 kg 时 J3 以外部分的重力（`wqcr5.upper_arm_end_loads`）。

| 量 | 有限元 | 梁理论 |
|---|---|---|
| 最大冯·米塞斯应力 | {vm_fe if vm_fe is not None else '—'} MPa | {fo['vm_mpa']} MPa（根部名义） |
| 端部位移 | {disp_fe if disp_fe is not None else '—'} mm | {fo['delta_mm']} mm |
| 单元 / 网格 | {stats.get('elements', '—')} / {stats.get('mesh_size_mm', ex['mesh_mm'])} mm | — |

有限元在法兰与管连接的转角处应力比名义值高（应力集中），但仍然很低；端部位移和梁理论相差不大——**这根管本身很硬**。

## 整机的末端变形（《机器人学》31.2 节）

{L.md_table(["来源", "末端位移 mm"], [[k, f"{v * 1000:.3f}"] for k, v in share.items() if v > 1e-6])}

合计约 **{tot * 1000:.2f} mm**；关节（谐波减速器扭转）占 {sum(v for k, v in share.items() if k.startswith('J')) / sum(share.values()):.0%}，臂管只占 {sum(v for k, v in share.items() if not k.startswith('J')) / sum(share.values()):.0%}。
重力变形是有规律的，标定和重力补偿能补掉大部分；重复精度看的是每次回到同一点的散布。

## 固有频率（关节刚度 K₁ + MuJoCo 质量矩阵）

前三阶 {f_modes[0]:.1f} / {f_modes[1]:.1f} / {f_modes[2]:.1f} Hz。只算大臂这一根管一端固定，一阶有 {fo['f1_tip_hz']} Hz——**整机的低频来自关节，不来自臂管**。
"""
case.step("sim", f"大臂有限元最大应力 {vm_fe} MPa、端部位移 {disp_fe} mm；整机末端重力变形 {tot * 1000:.2f} mm，关节占 {sum(v for k, v in share.items() if k.startswith('J')) / sum(share.values()):.0%}；一阶频率 {f_modes[0]:.1f} Hz。",
          f"Upper-arm FEA: max stress {vm_fe} MPa, tip displacement {disp_fe} mm; TCP gravity deflection {tot * 1000:.2f} mm, {sum(v for k, v in share.items() if k.startswith('J')) / sum(share.values()):.0%} from joints; first mode {f_modes[0]:.1f} Hz.",
          md=case.text("4_有限元与刚度.md", simmd), figs=[("4_末端变形来源.png", "末端重力变形的来源", "Sources of TCP gravity deflection")],
          tools=tools("cae", "mbd"), facts=[("大臂最大应力", "Upper-arm max stress", vm_fe if vm_fe is not None else "—", "MPa"), ("末端变形", "TCP deflection", tot * 1000, "mm"), ("一阶频率", "First mode", f_modes[0], "Hz")])
if disp_fe is not None:
    case.check("sim", "大臂端部位移：有限元与梁理论相差", "Upper-arm tip displacement: FEA vs beam theory", abs(disp_fe / fo["delta_mm"] - 1) * 100, "<=", 15.0, "%", "31.3 节（核对有限元）")
case.check("sim", "整机末端重力变形", "TCP gravity deflection", tot * 1000, "<=", 5.0, "mm", "本案例设定（标定、重力补偿前）")
if vm_fe is not None:
    case.check("sim", "大臂有限元最大应力对屈服的安全系数", "Upper-arm FEA yield safety factor", W.YIELD_AL / 1e6 / float(vm_fe), ">=", 3.0, "", "31.3 节")

# ================================================================ 5 三维、DH 参数、物料清单
import build123d as bd  # noqa: E402
import robotgeom as RG  # noqa: E402

arm = RG.arm_solid()
bd.export_step(arm, str(case.path("WQ-CR5.step")))
L.render_solid(arm, case.path("5_整机三维.png"), elev=18, azim=-60, size=(7, 6), swap=False)
from factory import data as F  # noqa: E402

dh_rows = [[W.JOINTS[i], f"{d['a'] * 1000:g}", f"{math.degrees(d['alpha']):g}°", f"{d['d'] * 1000:g}", W.MODULES[W.JOINT_MODULE[i]]["code"]] for i, d in enumerate(W.DH)]
bom_rows = [[c, F.ITEMS[c][0] if c in F.ITEMS else c, q] for c, q in F.BOMS["WQ-CR5"][1]]
cadmd = f"""# 三维、DH 参数与物料清单

整机三维（初始位姿 {W.HOME_DEG}）由 `wqcr5.link_parts()` 生成，与 MuJoCo 模型、零件库 B-ARM-WQCR5 同一份数据。

**名义 DH 参数**（标准 DH；与整机标定 `sim/calib.NOMINAL` 一致）：

{L.md_table(["关节", "a mm", "α", "d mm", "模组"], dh_rows)}

**物料清单**（机器人厂清单，一层）：

{L.md_table(["物料", "名称", "用量"], bom_rows)}

整机 {S['mass_kg']} kg，运动部分 {S['moving_mass_kg']} kg。案例 B 发现 WQJ-L 的实际长度比模型长，模型数据更新后整机质量、惯量要复算。
"""
LIBP = [L.lib_part("D-RDC-HD-CSF", s_) for s_ in ("32-100", "25-100", "17-100")] + [L.lib_part("A-BRG-DG", s_) for s_ in ("6010", "6007", "6004")] + [L.lib_part("A-SCR-SHC", "M5x16")]
cadmd += f"""
## 用到的零件库零件

整机在零件库里是 `B-ARM-WQCR5`（三维、DH、质量与本模型同一份）；关节模组里的标准件、外购件：

{L.lib_md(LIBP, {"D-RDC-HD-CSF/32-100": "WQJ-L ×2（J1、J2）", "D-RDC-HD-CSF/25-100": "WQJ-M（J3）", "D-RDC-HD-CSF/17-100": "WQJ-S ×3（J4–J6）",
                 "A-BRG-DG/6010": "WQJ-L 输出轴承 ×2 / 只", "A-BRG-DG/6007": "WQJ-M 输出轴承 ×2", "A-BRG-DG/6004": "WQJ-S 输出轴承 ×2 / 只", "A-SCR-SHC/M5x16": "整机联接 ×24"})}

刚度（K₁–K₃）、额定和峰值转矩都取零件库的厂商目录值；第 4 步的末端变形、固有频率就是用它们算的。
"""
case.step("cad", f"整机三维、名义 DH 参数、{len(bom_rows)} 行物料清单；整机 {S['mass_kg']} kg。",
          f"3D robot, nominal DH parameters, {len(bom_rows)}-line BOM; {S['mass_kg']} kg.",
          md=case.text("5_三维与清单.md", cadmd), figs=[("5_整机三维.png", "WQ-CR5（初始位姿）", "WQ-CR5 in the home pose")],
          files=[("WQ-CR5.step", "整机 STEP", "Robot (STEP)")], tools=[("零件库：WQ-CR5", "Library: WQ-CR5", "/library?ref=B-ARM-WQCR5")] + L.lib_tools(LIBP), facts=[("物料清单", "BOM lines", len(bom_rows), "")])

# ================================================================ 6 工艺：装配、标定、跑合
routing = F.ROUTINGS[F.BOMS["WQ-CR5"][0]]
from sim import calib as CB  # noqa: E402

procmd = f"""# 工艺：装配、标定、跑合、出厂

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(routing)])}

## 整机标定（实验 26 同一段代码 `sim/calib.py`）

- 几何误差模型：6 个关节 × 4 个偏差（零位 Δθ、偏距 Δd、连杆长度 Δa、扭角 Δα）= 24 个；
- 激光跟踪仪测工具点：{CB.N_DEFAULT} 个位姿铺满工作空间，噪声 σ {CB.SIG_TRACKER * 1e3:g} mm；
- 最小二乘辨识（奇异值分解，相邻平行轴 J2–J4 的轴向偏距只辨识得出和，自动放掉）；另取 {CB.N_VERIFY} 个位姿验证；
- 要求：标定后平均绝对定位误差 ≤ {CB.LIMIT_MM} mm。

## 负载跑合（实验 28）

装标准负载（{W.RUNIN_LOAD['mass']:g} kg 钢块）跑标准动作，记录各关节力矩，与动力学模型对比，查摩擦、背隙是否正常。
"""
case.step("process", f"{len(routing)} 道工序：装配、标定、负载跑合、出厂检验、包装；标定 24 个参数、{CB.N_DEFAULT} 个位姿。",
          f"{len(routing)} operations: assembly, calibration, load run-in, final inspection, packing; 24 parameters from {CB.N_DEFAULT} poses.",
          md=case.text("6_工艺.md", procmd), tools=tools("calib", "lab28"), facts=[("工序", "Operations", len(routing), "")])

# ================================================================ 7 制造：5 台
from hub import mrp  # noqa: E402

sh = L.run_shop("WQ-CR5", 5, "WO-CASE-RB-C", seed=363)
rows_q, cpk_min, fails, st = L.shop_table(sh["measurements"])
serials = sorted({m["part_serial"] for m in sh["measurements"]})
cal = [CB.case(sn) for sn in serials]
fig, ax = plt.subplots(figsize=(7.6, 3.0))
x = np.arange(len(cal))
ax.bar(x - 0.2, [c["before_mean_mm"] for c in cal], 0.4, color="#8aa4bd", label="标定前（名义 DH）")
ax.bar(x + 0.2, [c["after_mean_mm"] for c in cal], 0.4, color=L.ACCENT, label="标定后")
ax.axhline(CB.LIMIT_MM, color=L.BAD, ls=":", lw=0.9)
ax.set_xticks(x, [s[-6:] for s in serials])
ax.set_ylabel("验证点平均绝对误差 / mm")
ax.legend(frameon=False, fontsize=8.5)
case.fig(fig, "7_标定前后.png")
mc, oc = mrp.std_unit_cost("WQ-CR5")
makemd = f"""# 出厂 5 台

机器人厂仿真车间下一张 5 台的工单（各关节模组按案例 A、B 已经测好），装配 → 标定 → 负载跑合 → 出厂检验 → 包装，用 {sh['hours']:.1f} 小时：

{L.md_table(["特性", "公差 mm", "件数", "均值", "标准差", "Cpk"], rows_q)}

## 每台的标定（激光跟踪仪 {CB.N_DEFAULT} 个位姿辨识，{CB.N_VERIFY} 个位姿验证）

{L.md_table(["出厂编号", "标定前平均 / 最大 mm", "标定后平均 / 最大 mm", "条件数", ""], [[c['serial'], f"{c['before_mean_mm']:.2f} / {c['before_max_mm']:.2f}", f"{c['after_mean_mm']:.3f} / {c['after_max_mm']:.3f}", c['cond'], "✓" if c['pass'] else "✗"] for c in cal])}

标定把绝对误差从约 1 mm 降到 0.1 mm 量级；降不到零，因为关节柔度、齿隙这类几何模型以外的误差补不了（第 4 步的变形里就有它）。

**标准成本**：材料 ${mc:,.2f}（六只关节模组占大头）+ 加工 ${oc:.2f} = **${mc + oc:,.2f} / 台**。

想自己走一遍：在“订单与计划”接一台 WQ-CR5（实验 24），“整机标定”页标一台（实验 26），“负载跑合”页跑一台（实验 28）。
"""
case.step("make", f"5 台出厂，{len(sh['measurements'])} 个测量值不合格 {fails} 个；标定后平均绝对误差 {min(c['after_mean_mm'] for c in cal):.2f}–{max(c['after_mean_mm'] for c in cal):.2f} mm；标准成本 ${mc + oc:,.0f}/台。",
          f"5 robots dispatched, {fails} of {len(sh['measurements'])} measurements out of tolerance; mean absolute error after calibration {min(c['after_mean_mm'] for c in cal):.2f}–{max(c['after_mean_mm'] for c in cal):.2f} mm; standard cost ${mc + oc:,.0f}.",
          md=case.text("7_出厂.md", makemd), figs=[("7_标定前后.png", "5 台标定前后的平均绝对误差（红线：0.5 mm）", "Mean absolute error before and after calibration (red: 0.5 mm)")],
          tools=tools("planner", "calib", "lab28", "quality", "finance"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("标定后最大平均误差", "Worst mean error after calibration", max(c["after_mean_mm"] for c in cal), "mm"), ("标准成本", "Standard cost", f"${mc + oc:,.0f}", "")])
case.check("make", "5 台出厂检验不合格数", "Out-of-tolerance values in 5 robots", fails, "==", 0, "", "出厂检验")
case.check("make", "位置重复精度过程能力 Cpk", "Repeatability Cpk", min(v["cpk"] for v in st.values()), ">=", 1.33, "", "常用要求")
case.check("make", "标定后平均绝对误差（最差一台）", "Mean absolute error after calibration (worst robot)", max(c["after_mean_mm"] for c in cal), "<=", CB.LIMIT_MM, "mm", "出厂检验")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

## 校核一览

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

## 整机设计的结论

1. **臂管按刚度和重量定**：应力只有几 MPa；末端变形 {tot * 1000:.1f} mm 里关节占大头，臂管只占一小部分。
2. **低频来自关节**：整机一阶 {f_modes[0]:.1f} Hz，单根大臂一端固定 {fo['f1_tip_hz']} Hz。
3. **精度靠标定**：名义 DH 下绝对误差约 1 mm，标定后 0.1 mm 量级；重复精度靠关节（背隙、编码器）。
4. **模型要跟着零件更新**：案例 B 发现 WQJ-L 比模型长，更新后复算质量、惯量和案例 A 的选型。

## 三个案例连起来看

案例 A 选模组 → 案例 B 看模组里面（发现模型里的长度偏短）→ 案例 C 把模组装成整机、标定、跑合。

## 留给学生的问题

1. 把大臂管换成碳纤维管（模量约为铝的 1.5 倍、密度约 60%），末端变形和整机质量各变多少？值不值？
2. 标定只用 10 个位姿、而且集中在一个角落，条件数和标定后的误差会怎样（实验 26）？
3. 末端变形主要来自 J2，如果在控制器里做重力补偿（按模型预先多转一点），能补掉多少？补不掉的是什么？
4. 案例 B 把 WQJ-L 加长到约 170 mm，在“参数配置器”里重新选型，J2 的需求变多少？

相关：《机器人学》第 30–32 章；实验 24（从订单到交付）、25、26（标定）、28（负载跑合）；案例 A、B。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；臂管按刚度定、低频来自关节、精度靠标定。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; tubes sized by stiffness, low modes from the joints, accuracy from calibration.",
          md=case.text("8_总结.md", review), tools=tools("configurator"))
case.write()
