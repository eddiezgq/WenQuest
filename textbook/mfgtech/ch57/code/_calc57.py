"""第 57 章的工艺计算书：SH-101 各外圆的工序尺寸与余量，按“分析计算法”从最后一道工序往前推（第 50 章底稿 _calc50.py 的做法）。

最小余量（直径上）2Z_min = 2(Rz + H_a) + 2·√(ρ² + ε²)（式 57.1.3）：Rz、H_a 是上道工序留下的表面粗糙度与缺陷层深度，
ρ 是上道工序留下的空间偏差（弯曲、偏心、热处理变形），ε 是本道工序的装夹误差（两顶尖装夹取 0）。
各分量取数字工厂的企业工艺标准 WQ-PS-01（本章为 SH-101 补了“半精车后渗碳淬火”和“热轧圆钢”两行）——**教学示意值，不是国家标准**，
实际取值查工艺手册的余量表，渗碳淬火的变形最好实测一批零件。
"""
import math

from mfgcalc import CalcSheet

# 企业工艺标准 WQ-PS-01（教学示意值，mm）：上道工序 → (Rz, H_a, ρ, 说明)
WQ_PS_01 = {
    "半精车后渗碳淬火": (0.0125, 0.05, 0.10, "半精车 Ra 3.2（Rz ≈ 12.5 μm）；渗碳淬火的氧化、内氧化层；渗碳淬火的弯曲与变形（修研中心孔后）"),
    "粗车": (0.05, 0.05, 0.30, "粗车 Ra 12.5（Rz ≈ 50 μm）；粗车的塑性变形层；棒料弯曲与一夹一顶粗车的偏心"),
    "热轧圆钢": (0.15, 0.50, 0.20, "热轧表面 Rz ≈ 150 μm；氧化皮与脱碳层；棒料弯曲（142 mm 长）"),
}
STD = "企业工艺标准 WQ-PS-01（教学示意值）"
EPS_CHUCK = 0.05          # 粗车第一次装夹：三爪卡盘夹毛坯外圆的定心误差（示意）


def zmin(rz, ha, rho, eps=0.0):
    return 2 * (rz + ha) + 2 * math.sqrt(rho ** 2 + eps ** 2)


def ceil01(x):
    """工序尺寸往大取整到 0.1 mm（便于车间测量）；取整多出来的就是额外的保险。"""
    return math.ceil(round(x * 10, 6)) / 10


def sheet(d, es, ei, name, T2=0.05, T1=0.2, item="SH-101"):
    """一个磨削外圆的计算书：磨（图纸）← 半精车（T2）← 粗车（T1）。返回 CalcSheet，结果在 cs.vals。"""
    cs = CalcSheet(f"{item} {name} Ø{d:g}（{es:+g}/{ei:+g}）的工序尺寸与余量", item=item, task="TS-57-1")
    cs.given("d", d, "mm", f"{name}图纸尺寸", src=f"{item} 零件图（std/SH-101_part.yaml）")
    cs.given("es, ei", f"{es:+g} / {ei:+g}", "mm", "上、下偏差", src=f"{item} 零件图")
    cs.given("T₂", T2, "mm", "半精车（工序 30）的公差：经济精度 IT8–IT10，取 0.05", src="std/route_methods.yaml（半精车）")
    cs.given("T₁", T1, "mm", "粗车（工序 20）的公差：经济精度 IT11–IT13，取 0.2", src="std/route_methods.yaml（粗车）")
    cs.find("A₂, A₁", "半精车、粗车的工序尺寸及公差（入体标注）")
    cs.find("2Z", "各道工序余量的最小值与最大值")
    rz, ha, rho, _ = WQ_PS_01["半精车后渗碳淬火"]
    z3 = cs.step("2Z₃,min", "2Z_min = 2(Rz + H_a) + 2√(ρ² + ε²)", zmin(rz, ha, rho), "mm", "磨削的最小余量（直径上）", src=STD,
                 subst=f"2({rz} + {ha}) + 2√({rho}² + 0²)")
    a2 = cs.step("A₂", "A₂ ≥ d_max + 2Z₃,min + T₂，往大取整到 0.1", ceil01(d + es + z3 + T2), "mm", "半精车工序尺寸（上偏差 0）",
                 subst=f"{d + es:g} + {z3:.3f} + {T2:g}")
    rz, ha, rho, _ = WQ_PS_01["粗车"]
    z2 = cs.step("2Z₂,min", "2Z_min = 2(Rz + H_a) + 2√(ρ² + ε²)", zmin(rz, ha, rho), "mm", "半精车的最小余量（直径上）", src=STD,
                 subst=f"2({rz} + {ha}) + 2√({rho}² + 0²)")
    a1 = cs.step("A₁", "A₁ ≥ A₂ + 2Z₂,min + T₁，往大取整到 0.5", math.ceil(round((a2 + z2 + T1) * 2, 6)) / 2, "mm",
                 "粗车工序尺寸（上偏差 0；粗车尺寸取整到 0.5）", subst=f"{a2:g} + {z2:.3f} + {T1:g}")
    g3min = cs.step("2Z₃ 实际最小", "(A₂ − T₂) − d_max", (a2 - T2) - (d + es), "mm", "磨削余量的实际最小值", subst=f"({a2:g} − {T2:g}) − {d + es:g}")
    g3max = cs.step("2Z₃ 实际最大", "A₂ − d_min", a2 - (d + ei), "mm", "磨削余量的实际最大值", subst=f"{a2:g} − {d + ei:g}")
    g2min = cs.step("2Z₂ 实际最小", "(A₁ − T₁) − A₂", (a1 - T1) - a2, "mm", "半精车余量的实际最小值", subst=f"({a1:g} − {T1:g}) − {a2:g}")
    g2max = cs.step("2Z₂ 实际最大", "A₁ − (A₂ − T₂)", a1 - (a2 - T2), "mm", "半精车余量的实际最大值", subst=f"{a1:g} − ({a2:g} − {T2:g})")
    cs.check("2Z₃ 实际最小", g3min, ">=", z3, "磨削余量不小于最小余量")
    cs.check("2Z₂ 实际最小", g2min, ">=", z2, "半精车余量不小于最小余量")
    cs.check("2Z₃ 实际最大", g3max, "<=", 0.5, "渗碳件磨削余量不大于 0.5 mm（磨削工时、烧伤与硬化层，企业标准示意）")
    cs.note("余量分量取自" + STD + "；拿到工艺手册的余量表后，按表核对；渗碳淬火的变形 ρ 以实测为准。")
    cs.vals = dict(T1=T1, T2=T2, z3=z3, z2=z2, a2=a2, a1=a1, g3min=g3min, g3max=g3max, g2min=g2min, g2max=g2max)
    return cs


def bar_diameter(da=52.0, finish=1.5, bar_ei=-0.6, sizes=(50, 52, 55, 56, 58, 60, 63, 65)):
    """最大外圆（齿顶圆）需要的棒料直径：da + 精车余量 = 粗车尺寸 A₁（上偏差 0）；按式 (57.2.1)，棒料的最小直径
    ≥ A₁ + 毛坯的最小余量（热轧表面、弯曲、卡盘定心）。棒料按名义直径订货，要再扣去它的下偏差 bar_ei
    （热轧圆钢 Ø50–Ø80 取 −0.6 示意，以现行 GB/T 702 为准），取工厂常备的规格。"""
    rz, ha, rho, _ = WQ_PS_01["热轧圆钢"]
    z1 = zmin(rz, ha, rho, EPS_CHUCK)
    need = da + finish + z1                    # 棒料直径的最小值
    pick = next(s for s in sizes if s + bar_ei >= need - 1e-9)
    return dict(z1=z1, need=need, pick=pick, a_rough=da + finish, bar_ei=bar_ei, pick_min=pick + bar_ei)
