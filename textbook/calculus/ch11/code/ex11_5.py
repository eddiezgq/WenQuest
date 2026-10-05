"""11.5 节：边际与弹性——机器人工作站的经济批量 Q* = √(2DS/H)，成本曲线在最优点附近很平；
利润最大的产量（边际收入 = 边际成本）；需求的价格弹性与收入最大的价格。"""
import math

from bookout import out

D, S, H = 12000, 800.0, 4.0           # 件/年，元/次（换型），元/(件·年)（库存持有成本）
C = lambda Q: D / Q * S + Q / 2 * H
out(D=D, S_=S, H=H)
Qs = math.sqrt(2 * D * S / H)
rows = []
for f in (0.5, 0.8, 1.0, 1.25, 1.5, 2.0):
    Q = f * Qs
    rows.append(f"| {f:g} | {Q:.0f} | {C(Q):.0f} | {(C(Q) / C(Qs) - 1) * 100:.1f} |")
out(Q_star=Qs, C_star=C(Qs), runs=D / Qs, eoq_tab="\n".join(rows))
# 利润：价格 p = 100 − 0.02q，成本 C = 20000 + 30q + 0.01q²
q_star = (100 - 30) / (0.04 + 0.02)
p_star = 100 - 0.02 * q_star
profit = q_star * p_star - (20000 + 30 * q_star + 0.01 * q_star ** 2)
out(q_star=q_star, p_star=p_star, profit=profit)
