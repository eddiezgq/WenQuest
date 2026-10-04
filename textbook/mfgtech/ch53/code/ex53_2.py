"""53.2 节：极值法。算例 53.2.1 正计算——SH-301 键槽深度 d − t₁（工艺规程登记的尺寸链）；
算例 53.2.2 反计算——已知 d − t₁ 的要求和磨削、精车的尺寸，求铣键槽的工序尺寸 H；
算例 53.2.3 公差分配——五环轴向尺寸链按等公差法和等精度法分配公差。"""
import _mfg as M
from bookout import out

TL = M.tol()
p = M.plan()
ch = p["chains"][0]
links = [M.link(l["name"], l["nominal"], l["es"], l["ei"], l["sense"]) for l in ch["links"]]
r = TL.extreme(links)
c5 = next(c for c in p["characteristics"] if c["id"] == ch["char"])
ok = r.max <= c5["nominal"] + c5["es"] + 1e-9 and r.min >= c5["nominal"] + c5["ei"] - 1e-9
# 反计算：求 H
others = [l for l in links if not l.name.startswith("槽底")]
Hs = TL.solve_link(others, (c5["nominal"], c5["es"], c5["ei"]), "H", +1)
Hp = next(l for l in links if l.name.startswith("槽底"))
inside = Hp.max <= Hs.max + 1e-9 and Hp.min >= Hs.min - 1e-9
# 如果不考虑磨削（误按图纸尺寸铣到 35（0/−0.2））
naive = TL.extreme([M.link("H 误取 35", 35, 0, -0.2, 1)] + others)
# 公差分配：轴向尺寸链 A0 = A1 − A2 − A3 − A4，T0 = 0.4（教学示意）
noms = [167, 52, 55, 30]
eq = TL.allocate(0.4, noms, "equal_tolerance")
pr = TL.allocate(0.4, noms, "equal_precision")
iu = [TL.tolerance_unit(D) for D in noms]
a_um = 0.4 * 1000 / sum(iu)                      # 等精度法的公差单位数 a（IT9 为 40、IT10 为 64，GB/T 1800.1）
out(a_um=a_um, iu3=iu[2], iu4=iu[3], A0=r.nominal, es=r.es, ei=r.ei, T0=r.T, Tsum=r.detail["T_sum"], ok="满足" if ok else "不满足", spec=c5["spec"],
    H_nom=Hs.nominal, H_es=Hs.es, H_ei=Hs.ei, H_T=Hs.T, Hp_es=Hp.es, Hp_ei=Hp.ei, inside="在计算范围之内" if inside else "超出计算范围",
    naive_es=naive.es, naive_ei=naive.ei, naive_min=naive.min, naive_max=naive.max,
    eq=eq[0], pr1=pr[0], pr2=pr[1], pr3=pr[2], pr4=pr[3], iu1=TL.tolerance_unit(noms[0]), iu2=TL.tolerance_unit(noms[1]))
