"""50.3 节：SH-301 的毛坯——零件质量、毛坯质量、材料利用率与每件材料费（算例 50.3.1）；与 Ø45 棒料、近净形锻件比较。"""
import math

import _mfg as M
from bookout import out

RHO = 7.85e-6                       # 钢的密度，kg/mm³
segs, key = M.segments()
p = M.plan()
L_total = sum(L for _, L in segs)
V_part = sum(math.pi * d ** 2 / 4 * L for d, L in segs) - key["b"] * key["t"] * key["L"]      # 键槽按长方体扣除（两端圆弧略去）
m_part = V_part * RHO
bar_d = 50.0
L_blank = p["blank"]["length_mm"]
m_blank = math.pi * bar_d ** 2 / 4 * L_blank * RHO
bom_qty = dict(M.F.BOMS["SH-301"][1])["RM-45-D50"]
assert abs(m_blank - bom_qty) < 0.05            # 与 ERPNext BOM 的钢材用量一致（2.8 kg）
eta = m_part / m_blank
unit = M.price("RM-45-D50")
cost = bom_qty * unit
# 比较一：Ø45 棒料
m45 = math.pi * 45 ** 2 / 4 * L_blank * RHO
# 比较二：近净形毛坯（例如模锻件）——每段直径单边留 2.5 mm、两端各留 2 mm（示意）
V_near = sum(math.pi * (d + 5) ** 2 / 4 * L for d, L in segs) + math.pi * (segs[0][0] + 5) ** 2 / 4 * 4
m_near = V_near * RHO
out(L_total=L_total, L_blank=L_blank, allow_len=L_blank - L_total, m_part=m_part, m_blank=m_blank, bom_qty=bom_qty, eta_pct=100 * eta,
    unit=unit, cost=cost, m45=m45, eta45_pct=100 * m_part / m45, save45=(m_blank - m45) * unit, save45_k=(m_blank - m45) * unit * 1000,
    m_near=m_near, eta_near_pct=100 * m_part / m_near, save_near=(m_blank - m_near) * unit)
