"""6.6 节的计算：

算例 6.6.1  AGV 牵引两辆料车：加速度、两个挂钩的拉力，挂钩额定拉力限制下的最大驱动力（图 6.6.1）；
算例 6.6.2  带配重的货梯在制动器松开时的加速度和钢丝绳拉力（阿特伍德机，图 6.6.2）。
"""
import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 6.6.1
m0, m1, m2 = 80.0, 50.0, 30.0       # AGV、第一辆、第二辆料车，kg
F = 200.0                           # 驱动力，N
a = F / (m0 + m1 + m2)
T1 = (m1 + m2) * a                  # AGV 与第一辆车之间的挂钩
T2 = m2 * a                         # 两辆车之间的挂钩
# 隔离法逐个核对：AGV: F − T1 = m0 a；车 1: T1 − T2 = m1 a；车 2: T2 = m2 a
A = np.array([[m0, 1, 0], [m1, -1, 1], [m2, 0, -1]])
sol = np.linalg.solve(A, [F, 0, 0])
assert np.allclose(sol, [a, T1, T2])
T_rated = 150.0
F_max = T_rated * (m0 + m1 + m2) / (m1 + m2)
a_max = F_max / (m0 + m1 + m2)

# ---- 算例 6.6.2：阿特伍德机
m_cage, m_cw = 300.0, 330.0         # 轿厢（含货物）、配重，kg
a_lift = (m_cw - m_cage) * g / (m_cage + m_cw)
T_rope = 2 * m_cage * m_cw * g / (m_cage + m_cw)
assert abs((T_rope - m_cage * g) - m_cage * a_lift) < 1e-9 and abs((m_cw * g - T_rope) - m_cw * a_lift) < 1e-9
t1 = 1.0
v1, s1 = a_lift * t1, 0.5 * a_lift * t1 ** 2

out(m0=m0, m1=m1, m2=m2, m_tot=m0 + m1 + m2, F=F, a=a, T1=T1, T2=T2, T_rated=T_rated, F_max=F_max, a_max=a_max,
    m_cage=m_cage, m_cw=m_cw, a_lift=a_lift, T_rope=T_rope, W_cage=m_cage * g, W_cw=m_cw * g, v1=v1, s1_cm=100 * s1,
    a_lift_g=a_lift / g)

plt = style()
# 图 6.6.1：三个隔离体（AGV 在前，向右行驶）
fig, axs = plt.subplots(2, 1, figsize=(7.6, 3.6), gridspec_kw={"height_ratios": [1, 1]})
ax = axs[0]
d.cart(ax, 0.0, 0.0, w=0.8, label="2")
ax.plot([0.8, 0.92], [0.22, 0.22], color=d.INK, lw=2)
d.cart(ax, 0.92, 0.0, w=0.8, label="1")
ax.plot([1.72, 1.84], [0.22, 0.22], color=d.INK, lw=2)
d.agv(ax, 1.84, 0.0, w=1.0, label="AGV")
d.floor(ax, -0.2, 3.0)
d.arrow(ax, 3.1, 0.3, 0.5, 0, d.ACC, r"$\boldsymbol{a}$", off=(0.12, 0))
d.arrow(ax, 2.64, 0.0, 0.6, 0, d.FORCE, r"$F_\mathrm{d}$", off=(0.05, -0.1))
ax.set_xlim(-0.6, 4.2); ax.set_ylim(-0.15, 0.6); d.clean(ax)
ax = axs[1]
s = 0.007
blocks = [(-0.6, 0.8, d.CART, "2"), (1.0, 0.8, d.CART, "1"), (3.4, 1.0, d.BODY, "AGV")]
for x0, w, c, lab in blocks:
    ax.add_patch(plt.Rectangle((x0, -0.15), w, 0.3, fc=c, ec=d.INK, lw=1.2))
    ax.text(x0 + w / 2, 0, lab, ha="center", va="center", fontsize=10, color="white" if lab == "AGV" else d.INK)
d.arrow(ax, 0.2, 0.0, T2 * s, 0, "#2ca02c", r"$F_{\mathrm{T}2}$", where="mid", off=(0, 0.16))
d.arrow(ax, 1.0, 0.0, -T2 * s, 0, "#2ca02c", r"$F_{\mathrm{T}2}$", where="mid", off=(0, 0.16))
d.arrow(ax, 1.8, 0.0, T1 * s, 0, "#1d6fb8", r"$F_{\mathrm{T}1}$", where="mid", off=(0, 0.16))
d.arrow(ax, 3.4, 0.0, -T1 * s, 0, "#1d6fb8", r"$F_{\mathrm{T}1}$", where="mid", off=(0, 0.16))
d.arrow(ax, 3.9, -0.15, F * s, 0, d.FORCE, r"$F_\mathrm{d}$", off=(0.12, 0.06), ha="left")
ax.set_xlim(-0.7, 5.8); ax.set_ylim(-0.4, 0.35); d.clean(ax)
fig.text(0.5, 0.01, T("挂钩对两边车辆的拉力大小相等、方向相反（同色）；竖直方向的力相互抵消，略去",
                      "A coupler pulls the two vehicles with equal and opposite forces (same colour); vertical forces cancel and are left out"),
         ha="center", fontsize=8.5, color=d.MUTED)
figure(fig, "fig6_6_1")

# 图 6.6.2：货梯与配重
fig, ax = plt.subplots(figsize=(4.2, 4.0))
ax.add_patch(plt.Circle((0, 2.2), 0.35, fc="white", ec=d.INK, lw=1.5))
ax.plot([0, 0], [2.2, 2.75], color=d.INK, lw=1.5)
ax.plot([-0.6, 0.6], [2.75, 2.75], color=d.INK, lw=2.5)
ax.plot([-0.35, -0.35], [2.2, 1.0], color=d.INK, lw=1.2)
ax.plot([0.35, 0.35], [2.2, 0.4], color=d.INK, lw=1.2)
ax.add_patch(plt.Rectangle((-0.75, 0.2), 0.8, 0.8, fc=d.BODY, ec=d.INK, lw=1.2))
ax.text(-0.35, 0.6, T("轿厢", "cage"), ha="center", va="center", color="white", fontsize=10)
ax.add_patch(plt.Rectangle((0.15, -0.25), 0.4, 0.65, fc=d.CART, ec=d.INK, lw=1.2))
ax.text(0.35, 0.08, T("配重", "counter-\nweight"), ha="center", va="center", color=d.INK, fontsize=9)
s = 0.00025
d.arrow(ax, -0.35, 1.0, 0, T_rope * s, "#1d6fb8", r"$F_\mathrm{T}$", off=(-0.2, -0.3))
d.arrow(ax, -0.35, 0.2, 0, -m_cage * g * s, d.FORCE, r"$m_1 g$", off=(-0.32, 0.2))
d.arrow(ax, 0.35, 0.4, 0, T_rope * s, "#1d6fb8", r"$F_\mathrm{T}$", off=(0.25, -0.3))
d.arrow(ax, 0.35, -0.25, 0, -m_cw * g * s, d.FORCE, r"$m_2 g$", off=(0.3, 0.2))
d.arrow(ax, -1.15, 0.4, 0, 0.35, d.ACC, r"$a$", off=(-0.12, 0))
d.arrow(ax, 0.95, 0.5, 0, -0.35, d.ACC, r"$a$", off=(0.12, 0))
ax.set_xlim(-1.4, 1.3); ax.set_ylim(-1.2, 2.9); d.clean(ax)
figure(fig, "fig6_6_2")
