"""11.3 节的计算：

算例 11.3.1  穿梭车（RGV，300 kg）以 0.80 m/s 撞上停着的 200 kg 小车并挂上（完全非弹性碰撞）：碰后速度、动能损失。
算例 11.3.2  一维碰撞的一般公式（恢复系数 e）：m₂ = 2m₁、v₂ = 0 时 e = 1、0.5、0 三种情况碰后的速度；
            碰后两者速度随质量比 m₂/m₁ 的变化（图 11.3.1）。
算例 11.3.3  测恢复系数：钢球从 1.00 m 高处落到钢板上弹起 0.81 m，落到橡胶输送带上弹起 0.16 m，求 e；
            零件从 0.30 m 高处落进料箱（e = 0.5），要多久才停止弹跳？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d


def collide(m1, m2, v1, v2, e):
    """一维碰撞：动量守恒 + 恢复系数 e = (v2' − v1')/(v1 − v2)。"""
    vc = (m1 * v1 + m2 * v2) / (m1 + m2)
    return vc - m2 * e * (v1 - v2) / (m1 + m2), vc + m1 * e * (v1 - v2) / (m1 + m2)


# ---- 算例 11.3.1
m1, m2, v1 = 300.0, 200.0, 0.80
v, _ = collide(m1, m2, v1, 0.0, 0.0)
K0, K1 = 0.5 * m1 * v1 ** 2, 0.5 * (m1 + m2) * v ** 2
out(m1=m1, m2=m2, v1=v1, v=v, K0=K0, K1=K1, dK=K0 - K1, frac=(K0 - K1) / K0, frac_formula=m2 / (m1 + m2))

# ---- 算例 11.3.2
for tag, e in (("1", 1.0), ("05", 0.5), ("0", 0.0)):
    a, b = collide(1.0, 2.0, 1.0, 0.0, e)
    assert abs(1.0 * a + 2.0 * b - 1.0) < 1e-12
    out(**{f"v1p_{tag}": a, f"v2p_{tag}": b, f"nv1p_{tag}": -a, f"Kfrac_{tag}": (0.5 * a * a + 0.5 * 2 * b * b) / 0.5})

# ---- 算例 11.3.3
h1 = 1.00
e_steel, e_rub = math.sqrt(0.81 / h1), math.sqrt(0.16 / h1)
h0, e0 = 0.30, 0.5
t1 = math.sqrt(2 * h0 / g)
t_total = t1 * (1 + 2 * e0 / (1 - e0))                          # 第一次下落 + 以后各次上下：t1·2e(1 + e + e² + …)
out(e_steel=e_steel, e_rub=e_rub, h0=h0, e0=e0, t1=t1, t_total=t_total)

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9))
r = np.linspace(0.05, 5, 300)
for e, ls in ((1.0, "-"), (0.5, "--"), (0.0, ":")):
    a = (1 - e * r) / (1 + r); b = (1 + e) / (1 + r)
    a1.plot(r, a, color=d.VA, lw=2, ls=ls, label=f"e = {e:g}")
    a2.plot(r, b, color=d.VR, lw=2, ls=ls, label=f"e = {e:g}")
for ax, title in ((a1, T("(a) 碰后物体 1 的速度 v₁′/v₁", "(a) body 1 after: v₁′/v₁")), (a2, T("(b) 碰后物体 2 的速度 v₂′/v₁", "(b) body 2 after: v₂′/v₁"))):
    ax.axhline(0, color=d.MUTED, lw=0.6); ax.axvline(1, color=d.MUTED, lw=0.6, ls=":")
    ax.set_xlabel(T("质量比 m₂/m₁", "mass ratio m₂/m₁")); ax.set_title(title, fontsize=9.5); ax.legend(frameon=False, fontsize=8); d.spines(ax)
a1.set_ylim(-1.05, 1.05); a2.set_ylim(0, 2.05)
fig.tight_layout()
figure(fig, "fig11_3_1")
