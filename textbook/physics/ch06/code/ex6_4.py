"""6.4 节的计算（驱动力记作 F_d，是地面对驱动轮的摩擦力）：

算例 6.4.1  AGV 推料车：两者的加速度、AGV 与料车之间的推力（图 6.4.1），并核对牛顿第三定律。
"""
from bookout import T, figure, out, style
from constants import g
import _draw as d

m_A, m_B = 120.0, 60.0      # AGV（含自身货物）与料车的质量，kg
F_drive = 150.0             # 地面对 AGV 驱动轮的摩擦力（驱动力），N；滚动阻力在第 7 章再计入
a = F_drive / (m_A + m_B)   # 整体法
P_on_B = m_B * a            # 隔离料车：AGV 对料车的推力
P_on_A = F_drive - m_A * a  # 隔离 AGV：料车对 AGV 的推力（向后）的大小
assert abs(P_on_A - P_on_B) < 1e-12           # 两个隔离体各自算出的结果满足第三定律

out(m_A=m_A, m_B=m_B, F_drive=F_drive, a=a, P=P_on_B, net_A=F_drive - P_on_A, W_A=m_A * g, W_B=m_B * g)

# ---- 图 6.4.1：两个隔离体，第三定律的力成对出现
plt = style()
fig, axs = plt.subplots(1, 3, figsize=(9.2, 2.9), gridspec_kw={"width_ratios": [1.25, 1, 1]})
ax = axs[0]
deck = d.agv(ax, 0.0, 0.0, w=1.0, label="A")
d.cart(ax, 1.02, 0.0, w=0.8, label="B")
d.floor(ax, -0.2, 2.1)
d.arrow(ax, 0.2, 0.75, 0.5, 0, d.ACC, r"$\boldsymbol{a}$", off=(0.12, 0))
ax.set_title(T("(a) AGV 推料车", "(a) AGV pushes a cart"), fontsize=11)
ax.set_xlim(-0.25, 2.15); ax.set_ylim(-0.25, 1.05); d.clean(ax)
s = 0.006                     # 1 N 画成 0.006 个单位
PAIR1, PAIR2 = "#c0392b", "#1d6fb8"
ax = axs[1]
ax.add_patch(plt.Rectangle((-0.4, -0.2), 0.8, 0.4, fc=d.BODY, ec=d.INK, lw=1.2))
ax.text(0, 0, "A", ha="center", va="center", color="white", fontsize=12)
d.arrow(ax, 0, -0.2, F_drive * s, 0, PAIR2, r"$\boldsymbol{F}_\mathrm{d}$", off=(0.1, -0.15))
d.arrow(ax, 0.4 + P_on_A * s, 0.05, -P_on_A * s, 0, PAIR1, r"$\boldsymbol{F}_{BA}$", off=(0.15, 0.17))
ax.set_title(T("(b) 隔离 AGV", "(b) the AGV alone"), fontsize=11)
ax.set_xlim(-0.8, 1.3); ax.set_ylim(-0.6, 0.6); d.clean(ax)
ax = axs[2]
ax.add_patch(plt.Rectangle((-0.35, -0.15), 0.7, 0.3, fc=d.CART, ec=d.INK, lw=1.2))
ax.text(0, 0, "B", ha="center", va="center", color=d.INK, fontsize=12)
d.arrow(ax, -0.35 - P_on_B * s, 0.0, P_on_B * s, 0, PAIR1, r"$\boldsymbol{F}_{AB}$", off=(-0.15, 0.17))
ax.set_title(T("(c) 隔离料车", "(c) the cart alone"), fontsize=11)
ax.set_xlim(-0.8, 1.0); ax.set_ylim(-0.6, 0.6); d.clean(ax)
fig.text(0.5, 0.02, T("竖直方向的重力与支持力相互抵消，图中略去；同色箭头为一对作用力与反作用力（另一个在地面上的未画出）",
                      "Vertical weights and normal forces cancel and are left out; arrows of one colour form an action–reaction pair (the partner on the floor is not drawn)"),
         ha="center", fontsize=8.5, color=d.MUTED)
figure(fig, "fig6_4_1")
