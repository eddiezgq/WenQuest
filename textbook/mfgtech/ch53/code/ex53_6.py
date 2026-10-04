"""53.6 节：保证表面处理层的深度。算例 53.6.1 SH-101 轴承位：渗碳淬火后磨削，磨后渗碳层深度 1.0 ± 0.2，求渗碳工序的层深要求；
算例 53.6.2 镀铬活塞杆：镀后 Ø20 f7，镀层厚 0.02–0.03，求镀前的磨削尺寸（教学示意值）。"""
import _mfg as M
from bookout import out

TL = M.tol()
L = M.link
s = next(c for c in M.chains_data()["chains"] if c["item"] == "SH-101")
b, d, c = s["before_heat"], s["drawing"], s["char"]
r1 = L("渗碳前半径 r1", b["size_mm"] / 2, b["es_mm"] / 2, b["ei_mm"] / 2, -1)
r2 = L("磨后半径 r2", d["size_mm"] / 2, d["es_mm"] / 2, d["ei_mm"] / 2, +1)
t1 = TL.solve_link([r1, r2], (c["nominal"], c["es"], c["ei"]), "t1", +1)
grind = (r1.nominal - r2.nominal)          # 单边磨削量（名义）
# 渗碳淬火后的弯曲和胀大使轴承位相对中心孔有跳动，磨削时一侧多磨、一侧少磨：按 0.06 的跳动计，单边磨削量变化 ±0.03（基本尺寸为零的组成环）
e = L("热处理变形引起的偏心", 0, 0.03, -0.03, -1)
t1e = TL.solve_link([r1, r2, e], (c["nominal"], c["es"], c["ei"]), "t1", +1)
# 若渗碳前车削公差放宽到 0/−0.1，渗碳层深度的公差还剩多少
r1w = L("r1", b["size_mm"] / 2, 0, -0.05, -1)
t1w = TL.solve_link([r1w, r2], (c["nominal"], c["es"], c["ei"]), "t1", +1)
# 53.6.2 镀铬：镀后直径 D = D1 + 2t：Ø20 f7（−0.020/−0.041），t = 0.02–0.03 → 求镀前 D1（D1 为组成环、D 为封闭环）
t = L("镀层厚 2t", 0.05, 0.01, -0.01, +1)                       # 2t = 0.04–0.06
D1 = TL.solve_link([t], (20, -0.020, -0.041), "镀前直径 D1", +1)
out(t1e_min=t1e.min, t1e_max=t1e.max, t1e_T=t1e.T, t1_nom=t1.nominal, t1_es=t1.es, t1_ei=t1.ei, t1_min=t1.min, t1_max=t1.max, t1_T=t1.T, grind=grind, r1_T=r1.T, r2_T=r2.T,
    t1w_T=t1w.T, t1w_min=t1w.min, t1w_max=t1w.max, D1_nom=D1.nominal, D1_es=D1.es, D1_ei=D1.ei, D1_T=D1.T, D1_min=D1.min, D1_max=D1.max)
