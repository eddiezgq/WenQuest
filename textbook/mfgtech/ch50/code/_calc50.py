"""第 50 章的工艺计算书：SH-301 轴承位（或齿轮位）的工序尺寸与余量，按“分析计算法”从最后一道工序往前推。

算例 50.6.1、50.6.2 用它算出书中的数字；工程任务单 TS-50-1 用它导出发给学生的空白计算书（公式和出处已填、结果留空）。

最小余量（直径上）2Z_min = 2(Rz + H_a) + 2·√(ρ² + ε²)（式 50.6.3）：Rz、H_a 是上道工序留下的表面粗糙度与缺陷层深度，
ρ 是上道工序留下的空间偏差（弯曲、偏心），ε 是本道工序的装夹误差（两顶尖装夹取 0）。
各分量取数字工厂的企业工艺标准 WQ-PS-01——**教学示意值，不是国家标准**，实际取值查工艺手册的余量表。
"""
import math

from mfgcalc import CalcSheet, lookup

# 企业工艺标准 WQ-PS-01（教学示意值，mm）：上道工序 → (Rz, H_a, ρ)
WQ_PS_01 = {
    "粗车后调质": (0.05, 0.15, 0.25),        # 粗车 Ra 12.5（Rz≈50 μm）；调质的氧化脱碳层；调质弯曲
    "精车后铣键槽": (0.0125, 0.03, 0.03),     # 精车 Ra 3.2（Rz≈12.5 μm）；切削变形层；铣键槽后的变形与跳动
}
STD = "企业工艺标准 WQ-PS-01（教学示意值）"


def zmin(rz, ha, rho, eps=0.0):
    return 2 * (rz + ha) + 2 * math.sqrt(rho ** 2 + eps ** 2)


def ceil01(x):
    """工序尺寸往大取整到 0.1 mm（便于车间测量），留出的是额外的余量。"""
    return math.ceil(round(x * 10, 6)) / 10


def sheet(d=35.0, es=0.018, ei=0.002, name="轴承位", item="SH-301"):
    cs = CalcSheet(f"{item} {name} Ø{d:g}k6 的工序尺寸与余量", item=item, task="TS-50-1")
    cs.given("d", d, "mm", f"{name}图纸尺寸（{'k6' if (es, ei) == (0.018, 0.002) else '见图纸'}）", src=f"{item} 零件图；工厂检验模板“零件检验-输出轴”")
    cs.given("es, ei", f"+{es:g} / +{ei:g}", "mm", "上、下偏差", src=f"{item} 零件图")
    cs.find("A₂, A₁", "精车、粗车的工序尺寸及公差")
    cs.find("Z", "各道工序余量的最小值与最大值")
    T3 = es - ei
    T2 = lookup(cs, "T₂", "it_grades", dict(size_over_mm__lt=d, size_to_mm__ge=d), "IT8_um", "μm", "精车工序公差取 IT8（精车经济精度 IT7–IT8）") / 1000
    T1 = lookup(cs, "T₁", "it_grades", dict(size_over_mm__lt=d, size_to_mm__ge=d), "IT12_um", "μm", "粗车工序公差取 IT12") / 1000
    rz, ha, rho = WQ_PS_01["精车后铣键槽"]
    z3 = cs.step("2Z₃,min", "2Z_min = 2(Rz + H_a) + 2√(ρ² + ε²)", zmin(rz, ha, rho), "mm", "磨削的最小余量（直径上）", src=STD,
                 subst=f"2({rz} + {ha}) + 2√({rho}² + 0²)")
    a2 = cs.step("A₂", "A₂ ≥ d_max + 2Z₃,min + T₂，往大取整到 0.1", ceil01(d + es + z3 + T2), "mm", "精车工序尺寸（h8，上偏差 0）",
                 subst=f"{d + es:g} + {z3:.3f} + {T2:g}")
    rz, ha, rho = WQ_PS_01["粗车后调质"]
    z2 = cs.step("2Z₂,min", "2Z_min = 2(Rz + H_a) + 2√(ρ² + ε²)", zmin(rz, ha, rho), "mm", "精车的最小余量（直径上）", src=STD,
                 subst=f"2({rz} + {ha}) + 2√({rho}² + 0²)")
    a1 = cs.step("A₁", "A₁ ≥ A₂ + 2Z₂,min + T₁，往大取整到 0.1", ceil01(a2 + z2 + T1), "mm", "粗车工序尺寸（h12，上偏差 0）",
                 subst=f"{a2:g} + {z2:.3f} + {T1:g}")
    g3min = cs.step("2Z₃ 实际最小", "(A₂ − T₂) − d_max", (a2 - T2) - (d + es), "mm", "磨削余量的实际最小值", subst=f"({a2:g} − {T2:g}) − {d + es:g}")
    g3max = cs.step("2Z₃ 实际最大", "A₂ − d_min", a2 - (d + ei), "mm", "磨削余量的实际最大值", subst=f"{a2:g} − {d + ei:g}")
    g2min = cs.step("2Z₂ 实际最小", "(A₁ − T₁) − A₂", (a1 - T1) - a2, "mm", "精车余量的实际最小值", subst=f"({a1:g} − {T1:g}) − {a2:g}")
    g2max = cs.step("2Z₂ 实际最大", "A₁ − (A₂ − T₂)", a1 - (a2 - T2), "mm", "精车余量的实际最大值", subst=f"{a1:g} − ({a2:g} − {T2:g})")
    cs.check("2Z₃ 实际最小", g3min, ">=", z3, "磨削余量不小于最小余量")
    cs.check("2Z₂ 实际最小", g2min, ">=", z2, "精车余量不小于最小余量")
    cs.check("2Z₃ 实际最大", g3max, "<=", 0.4, "磨削余量不大于 0.4 mm（磨削工时与烧伤风险，企业标准示意）")
    cs.note("余量分量取自" + STD + "；拿到工艺手册的余量表后，按表核对。")
    cs.vals = dict(T1=T1, T2=T2, T3=T3, z3=z3, z2=z2, a2=a2, a1=a1, g3min=g3min, g3max=g3max, g2min=g2min, g2max=g2max)
    return cs
