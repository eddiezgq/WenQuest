"""53.5 节：中间工序尺寸与一次加工同时保证多个尺寸。
算例 53.5.1 GR-203 小齿轮孔的键槽：精车孔 → 插键槽 → 渗碳淬火 → 磨孔，求插键槽的工序尺寸 A（考虑与不考虑磨孔与精车孔的同轴度）；
算例 53.5.2 SH-301 工序 40 调头车左端面：一刀同时决定总长和齿轮位长度，两者谁是封闭环。"""
import _mfg as M
from bookout import out

TL = M.tol()
L = M.link
g = next(c for c in M.chains_data()["chains"] if c["item"] == "GR-203")
d1, d2 = g["before_heat"], g["drawing"]
R1 = L("精车孔半径 R1", d1["size_mm"] / 2, d1["es_mm"] / 2, d1["ei_mm"] / 2, -1)
R2 = L("磨孔半径 R2", d2["size_mm"] / 2, d2["es_mm"] / 2, d2["ei_mm"] / 2, +1)
c = g["char"]
A = TL.solve_link([R1, R2], (c["nominal"], c["es"], c["ei"]), "A", +1)
e = L("同轴度引起的偏移", 0, g["coaxiality"] / 2, -g["coaxiality"] / 2, +1)
Ae = TL.solve_link([R1, R2, e], (c["nominal"], c["es"], c["ei"]), "A", +1)
chk = TL.extreme([R1, R2, e, Ae])
assert abs(chk.es - c["es"]) < 1e-9 and abs(chk.ei - c["ei"]) < 1e-9
# 53.5.2：工序 40 的工序尺寸 L→S2 = 52、R→S3 = −55、R→L = −167；齿轮位长度 60 = 167 − 52 − 55 是间接得到的封闭环
p = M.plan()
r = TL.chart_from_plan(p["tolerance_chart"])
d60 = next(d for d in r["drawing"] if d["nominal"] == 60)
dL = next(d for d in r["drawing"] if d["nominal"] == 167)
out(A_nom=A.nominal, A_es=A.es, A_ei=A.ei, A_T=A.T, Ae_es=Ae.es, Ae_ei=Ae.ei, Ae_T=Ae.T, coax=g["coaxiality"], R1=R1.nominal, R2=R2.nominal,
    r60_es=d60["result"].es, r167_es=dL["result"].es, T167=2 * 0.2)
