"""第 161h 轮：缝纫机厂案例 A——平缝机上轴 LS-101。
不重做设计：读第 138 轮 G2 的结果（docs/设计/WQ-LS/G2/结果.json、有限元.json、图）和主参数（tools/wqls/spec.py），整理成八步，
补“制造”一步（缝纫机厂仿真车间轴类线 40 根）。他们改了设计、重跑 tools/wqls/g2.py 以后，再跑本脚本，案例跟着更新。

    python3 tools/cases/sewing_a.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-sewing.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory"), str(ROOT / "tools" / "wqls")]

import caselib as L  # noqa: E402
import spec as S  # noqa: E402

G = ROOT / "docs" / "设计" / "WQ-LS"
R = json.loads((G / "G2" / "结果.json").read_text(encoding="utf-8"))
FE = json.loads((G / "G2" / "有限元.json").read_text(encoding="utf-8"))
SH2, SH3 = R["shaft"]["两支承"], R["shaft"]["三支承"]
TQ = R["torque"]
N = S.SEW["n"]

TOOLS = {
    "sew": ("缝纫机设计软件", "Sewing machine designer", "/library"),
    "cae": ("仿真与分析", "Simulation", "/cae"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "operator": ("车间执行", "Shop floor", "/work/operator"),
    "quality": ("质量", "Quality", "/work/quality"),
    "3d": ("3D 车间", "3D shop", "/3d"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731


def copy(src, name):
    return case.raw(name, (G / src).read_bytes())


case = L.Case("sewing", "A", "简单", "平缝机上轴 LS-101", "Upper shaft LS-101 of the lockstitch machine", "LS-101 上轴",
              "直驱平缝机的主轴：一转里 ±5 N·m 的惯性力矩全部从它通过。整理第 138 轮 G2 的计算：驱动力矩（MuJoCo 对照）、四个截面的疲劳、轴承寿命、临界转速、有限元，"
              "以及从教材 A 版到 D 版为什么一改再改；补缝纫机厂轴车间 40 根的制造与检验。",
              "The main shaft of the direct-drive lockstitch machine carries the ±5 N·m inertia torque of every revolution. Round 138 G2 results organised: drive torque "
              "(checked with MuJoCo), fatigue at four sections, bearing life, critical speed, FEA, and why the shaft went from revision A to D; plus 40 shafts made and inspected.",
              "tools/cases/sewing_a.py")

# ================================================================ 1 任务书
brief = f"""# 设计任务书：上轴 LS-101

**用在哪**　问渠工业直驱平缝机 WQ-LS（第 138 轮）的上轴：左端曲柄带针杆和挑线杆，中间送布偏心、同步带轮，右端直接装伺服电机转子和手轮。

| 项目 | 要求 | 出处 |
|---|---|---|
| 最高转速 | {N} r/min | G1 任务书 |
| 针距 | 1–{S.PERF['stitch_max']:g} mm，带倒缝 | G1 任务书 |
| 机臂空间 | 机针到立柱 {S.ARM['space_x']:.0f} mm（轴必须跨过去） | G1 任务书 |
| 疲劳安全系数 | ≥ 1.5（无限寿命） | 教材《机械设计》第 33 章 |
| 轴承寿命 L10h | ≥ 20 000 h | G2 计算书（G4 修订） |
| 临界转速 | ≥ 1.5 × 最高转速（刚性轴） | G2 计算书 |
| 材料与热处理 | 45 钢调质，轴颈高频淬火、磨削 | G2；缝纫机厂清单 |

本案例的数都读自第 138 轮 G2 的结果文件（`docs/设计/WQ-LS/G2/结果.json`，程序 `tools/wqls/g2.py`），没有另算。
"""
case.step("brief", f"直驱平缝机上轴：{N} r/min、跨过 {S.ARM['space_x']:.0f} mm 机臂；疲劳 ≥ 1.5、轴承 ≥ 20 000 h、临界转速 ≥ 1.5 倍。",
          f"Upper shaft of the direct-drive machine: {N} rpm, spans the {S.ARM['space_x']:.0f} mm arm; fatigue ≥ 1.5, bearings ≥ 20 000 h, critical speed ≥ 1.5×.",
          md=case.text("1_任务书.md", brief), facts=[("最高转速", "Max speed", N, "r/min")])

# ================================================================ 2 方案
concept = f"""# 方案：两支承还是三支承；A → D 四个版本

| 版本 | 为什么改 |
|---|---|
| A（教材 33.11） | 全长 297 mm，跨不过本机 {S.ARM['space_x']:.0f} mm 的机臂 |
| B | 按总体布置加长到 421 mm，两个 6201 |
| C | 机壳优化后立柱加宽，电机移到立柱外，后轴承外移，同步带轮移进轴身 |
| **D（现行）** | 做实体时挑线杆改为和针杆连杆共用曲柄销，曲柄都在轴端外侧；伸出变长，前端加粗到 Ø15、前轴承改 6202 |

**两支承 vs 加中间含油轴套（三支承）**（D 版，G2 结果）：

| 项目 | 两支承 | 三支承 |
|---|---|---|
| 前轴承寿命 L10h | {SH2['bearings'][0]['L10h']:,.0f} h | {SH3['bearings'][0]['L10h']:,.0f} h |
| 曲柄处挠度 | {SH2['defl_crank_um']:.0f} µm | {SH3['defl_crank_um']:.0f} µm |
| 一阶临界转速 | {SH2['nc'][0]:,.0f} r/min | {SH3['nc'][0]:,.0f} r/min |

三支承刚度好，但前轴承寿命反而下降（中间支承把弯矩分走，前轴承受力变大），三个孔还要一次镗出同轴；两支承已经够用——**不加**。
"""
case.step("concept", f"现行 D 版两支承；三支承挠度小但前轴承寿命 {SH3['bearings'][0]['L10h']:,.0f} h 不够，不加。",
          f"Revision D on two supports; a third support stiffens the shaft but cuts front bearing life to {SH3['bearings'][0]['L10h']:,.0f} h, so not used.",
          md=case.text("2_方案.md", concept))

# ================================================================ 3 计算
fat = SH2["fatigue"]
s_min = min(v["S"] for v in fat.values())
frows = [[k, f"{v['alpha'][0]:.2f} / {v['alpha'][1]:.2f}", f"{v['sa']:.1f} / {v['sm']:.1f}", f"{v['ta']:.1f}", f"**{v['S']:.2f}**"] for k, v in fat.items()]
L10 = [b["L10h"] for b in SH2["bearings"]]
calc = f"""# 计算书（摘自 G2 设计计算书第五节）

## 载荷

一转之内每个转角都算：曲柄（连杆力 + 曲柄销和平衡块的离心力，最大 {TQ['F_crank_max']:.0f} N）、挑线杆、送布偏心、同步带、电机转子重。
驱动力矩平均只有 {TQ['T_mean']:.3f} N·m（缝纫功率 {TQ['P_mean']:.0f} W），但一转之内在 {TQ['T_min']:.1f} … +{TQ['T_max']:.1f} N·m 之间起伏——**轴的疲劳由惯性力矩起伏决定，不由缝纫功率决定**。

## 疲劳（教材 33.11 的方法：截面一周 72 点随轴转一圈，理论应力集中系数用轴对称有限元算，DIN 743 合成）

{L.md_table(["截面", "α_σ / α_τ", "σ_a / σ_m MPa", "τ_a MPa", "安全系数 S"], frows)}

## 轴承、刚度、临界转速（{N} r/min）

| 项目 | 结果 | 要求 |
|---|---|---|
| 前轴承 L10h | {L10[0]:,.0f} h | ≥ 20 000 h |
| 后轴承 L10h | {L10[1]:,.0f} h | ≥ 20 000 h |
| 曲柄处挠度 | {SH2['defl_crank_um']:.0f} µm | 记录 |
| 一阶 / 二阶临界转速 | {SH2['nc'][0]:,.0f} / {SH2['nc'][1]:,.0f} r/min | ≥ {1.5 * N:,.0f} |
"""
case.step("calc", f"最危险截面疲劳安全系数 {s_min:.2f}；前轴承 {L10[0]:,.0f} h；临界转速 {SH2['nc'][0]:,.0f} r/min（{SH2['nc'][0] / N:.1f} 倍）。",
          f"Lowest fatigue safety factor {s_min:.2f}; front bearing {L10[0]:,.0f} h; critical speed {SH2['nc'][0]:,.0f} rpm ({SH2['nc'][0] / N:.1f}×).",
          md=case.text("3_计算书.md", calc), figs=[(copy("G2/4_上轴.png", "3_上轴.png"), "上轴载荷、弯矩与截面（G2）", "Shaft loads, moments and sections (G2)")],
          facts=[("疲劳安全系数", "Fatigue S", round(s_min, 2), ""), ("前轴承寿命", "Front bearing", round(L10[0]), "h"), ("临界转速", "Critical speed", round(SH2["nc"][0]), "r/min")])
case.check("calc", "最危险截面疲劳安全系数", "Lowest fatigue safety factor", round(s_min, 2), ">=", 1.5, "", "教材第 33 章")
case.check("calc", "前轴承寿命 L10h", "Front bearing life L10h", round(L10[0]), ">=", 20000, "h", "G2 计算书")
case.check("calc", "一阶临界转速 / 最高转速", "First critical / max speed", round(SH2["nc"][0] / N, 2), ">=", 1.5, "", "G2 计算书")

# ================================================================ 4 仿真
mj = R["mujoco"]
d_mj = mj["max_diff"] / mj["max_abs_ref"] * 100
simmd = f"""# 仿真：MuJoCo 对照驱动力矩，有限元看应力分布

## 驱动力矩（一转之内）

用问渠缝纫机设计软件的运动学 + 牛顿—欧拉逐转角算驱动力矩，再用数字工厂的 MuJoCo 多体动力学把刺布机构独立算一遍：
最大差 {mj['max_diff']:.4f} N·m，是峰值 {mj['max_abs_ref']:.2f} N·m 的 {d_mj:.2f} %——两种方法一致，载荷可信。

## 有限元（Gmsh + CalculiX）

取截面 I 弯矩最大的转角 φ = {FE['phi']:.0f}°（弯矩 {FE['M_I'] / 1000:.2f} N·m），加全部力和力矩；两个轴承位按铰支。
最大应力在截面 I 的圆角处，和“名义应力 × 应力集中系数”同一量级；圆角处网格偏粗，峰值会低估，所以**疲劳校核用第 3 步的表**，有限元用来看应力分布、找最危险的位置。
"""
case.step("sim", f"MuJoCo 与设计软件的驱动力矩最大差 {d_mj:.2f} %；有限元确认最危险位置在截面 I 圆角。",
          f"MuJoCo vs designer drive torque within {d_mj:.2f} %; FEA confirms the critical spot at the section I fillet.",
          md=case.text("4_仿真.md", simmd),
          figs=[(copy("G2/1_驱动力矩.png", "4_驱动力矩.png"), "一转之内的驱动力矩", "Drive torque over one revolution"),
                (copy("G2/2_MuJoCo对照.png", "4_MuJoCo对照.png"), "MuJoCo 对照", "MuJoCo cross-check"),
                (copy("G2/6_上轴有限元.png", "4_上轴有限元.png"), "上轴有限元", "Shaft FEA")],
          tools=tools("cae"), facts=[("MuJoCo 相差", "MuJoCo difference", round(d_mj, 2), "%")])
case.check("sim", "MuJoCo 与设计软件驱动力矩相差（占峰值）", "MuJoCo vs designer torque (of peak)", round(d_mj, 2), "<=", 1.0, "%", "核对模型")

# ================================================================ 5 三维与图纸：按现行轴段建模
import build123d as bd  # noqa: E402

shaft = None
for x0, x1, d, _ in S.UPPER_SEGS:
    seg = bd.Pos(0, 0, x0) * bd.Cylinder(d / 2, x1 - x0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    shaft = seg if shaft is None else shaft + seg
bd.export_step(shaft, str(case.path("5_LS-101.step")))
L.render_solid(shaft, case.path("5_上轴三维.png"), size=(10, 2.4))
srows = [[f"{x0:g}…{x1:g}", f"Ø{d:g}", nm] for x0, x1, d, nm in S.UPPER_SEGS]
cadmd = f"""# 三维与图纸：上轴 D 版

![上轴](5_上轴三维.png)

轴段（x 为沿轴位置，机针 x = 0，单位 mm；`tools/wqls/spec.py` 的 UPPER_SEGS）：

{L.md_table(["x", "直径", "装什么"], srows)}

全长 {S.UPPER_SEGS[-1][1] - S.UPPER_SEGS[0][0]:.0f} mm；台阶圆角 R0.5（受轴承内圈倒角限制）；轴颈 k5、磨削；曲柄座铣紧固平面（相位基准）。
三维模型 `5_LS-101.step`（按上表轴段，不含平面、键槽细节）。
"""
case.step("cad", f"D 版上轴：全长 {S.UPPER_SEGS[-1][1] - S.UPPER_SEGS[0][0]:.0f} mm，前 Ø15 装 6202、后 Ø12 装 6201，右端 Ø10 装转子和手轮。",
          f"Revision D: {S.UPPER_SEGS[-1][1] - S.UPPER_SEGS[0][0]:.0f} mm long, Ø15 with 6202 at the front, Ø12 with 6201 at the rear, Ø10 for rotor and handwheel.",
          md=case.text("5_三维与图纸.md", cadmd), figs=[("5_上轴三维.png", "上轴三维", "Shaft 3D")], files=[("5_LS-101.step", "上轴三维模型（STEP）", "Shaft 3D model (STEP)")])

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["LS-101"][0]]
procmd = f"""# 工艺：缝纫机厂轴类线

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt)])}

要点：调质后校直、粗精车分开（细长轴，长径比约 30）；**轴颈高频淬火后再校直、再磨**；曲柄紧固平面的相位是针杆、挑线、送布、旋梭定时的基准，检验时量。
"""
case.step("process", f"轴类线 {len(rt)} 道：调质、校直、精车、铣扁、轴颈高频淬火、再校直、磨外圆、检验。",
          f"{len(rt)} operations: Q&T, straightening, turning, flats, induction hardening, straightening again, grinding, inspection.",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("工序", "Operations", len(rt), "")])

# ================================================================ 7 制造
sh = L.run_shop("LS-101", 40, "WO-CASE-SW-A", seed=1611)
meas = sh["measurements"]
big = [m for m in meas if sum(1 for x in meas if x["characteristic"] == m["characteristic"]) >= 10]
rows_q, cpk_min, _, _ = L.shop_table(big)
rows_s, _, _, _ = L.shop_table([m for m in meas if m not in big]) if len(big) < len(meas) else ([], 0, 0, {})
fails = sum(1 for m in meas if m["result"] != "pass")
makemd = f"""# 制造：40 根上轴

缝纫机厂仿真车间轴类线做 40 根 LS-101（{sh['hours']:.1f} 小时），零件检验：

{L.md_table(["特性", "公差", "件数", "均值", "标准差", "Cpk"], rows_q)}

计量室抽检（每批几件，样本少不算 Cpk，只看合格）：

{L.md_table(["特性", "公差", "件数", "均值", "标准差", "Cpk（不用）"], rows_s) if rows_s else "（本批没有抽检记录）"}

不合格 **{fails}**，最低 Cpk {cpk_min:.2f}。
"""
case.step("make", f"40 根：不合格 {fails}，最低 Cpk {cpk_min:.2f}（轴承位直径、跳动、硬度、相位）。",
          f"40 shafts: {fails} failures, lowest Cpk {cpk_min:.2f} (bearing diameter, runout, hardness, phase).",
          md=case.text("7_制造与检验.md", makemd), tools=tools("planner", "operator", "quality", "3d"),
          facts=[("不合格", "Out of tolerance", fails, ""), ("最低 Cpk", "Lowest Cpk", round(cpk_min, 2), "")])
case.check("make", "不合格项", "Failures", fails, "==", 0, "", "零件检验")
case.check("make", "最低 Cpk（件数 ≥ 10 的特性）", "Lowest Cpk (characteristics with ≥ 10 parts)", round(cpk_min, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **高速机的轴由惯性决定**：缝纫功率只有 {TQ['P_mean']:.0f} W，一转里的力矩却起伏 ±5 N·m。
2. **设计跟着整机走**：教材的轴放不进这台机器，机壳、挑线机构一改，轴就跟着改了三版——每一版都重算一遍，程序化计算才跟得上。
3. **刚度好不等于更好**：加中间支承挠度减半，前轴承寿命却不够了。

## 留给学生的问题

1. 把最高转速提到 5500 r/min：哪一项最先不够？
2. 前轴承换回 6201 会怎样？

相关：第 138 轮 G2 设计计算书（`docs/设计/WQ-LS/G2/设计计算书.md`）；案例 C（整机）；教材《机械设计》第 33 章。截至 {case.meta['generated']}，数据取自 G2 结果文件。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；疲劳 {s_min:.2f}、前轴承 {L10[0]:,.0f} h。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; fatigue {s_min:.2f}, front bearing {L10[0]:,.0f} h.",
          md=case.text("8_总结.md", review), tools=tools("quality"))
case.write()
