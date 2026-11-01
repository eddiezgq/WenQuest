"""图 17.1.1：左：绞车提升 ROV 时拉力随提升距离的变化（缆绳越收越短，拉力线性减小），曲线下的面积是功；
右：把 UR5e 上臂从竖直下垂抬到水平，重力矩 m g d cos θ 随角度的变化，曲线下的面积是所做的功。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
y = np.linspace(0, 60, 200)
F = 120 + 3 * (60 - y)
a1.fill_between(y, 0, 120, color=BLUE, alpha=0.25, label=T("提升 ROV 的功 7.2 kJ", "work on the ROV: 7.2 kJ"))
a1.fill_between(y, 120, F, color=ACC, alpha=0.35, label=T("提升缆绳的功 5.4 kJ", "work on the cable: 5.4 kJ"))
a1.plot(y, F, color=INK, lw=2)
a1.set_xlabel(T("已提升的距离 y / m", "distance hauled y / m"))
a1.set_ylabel(T("拉力 F / N", "pull F / N"))
a1.set_ylim(0, 330)
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("功 = 力—位移曲线下的面积", "Work = area under the force–distance curve"), fontsize=10)
clean(a1)
th = np.linspace(-90, 0, 200)
tau = 8.393 * 9.81 * 0.2125 * np.cos(np.radians(th))
a2.fill_between(th, 0, tau, color=RED, alpha=0.2)
a2.plot(th, tau, color=RED, lw=2, label=T("重力矩 m g d cos θ", "gravity torque m g d cos θ"))
a2.set_xlabel(T("上臂角度 θ / (°)（−90° 竖直下垂，0° 水平）", "upper-arm angle θ / (°) (−90° hanging, 0° horizontal)"))
a2.set_ylabel(T("力矩 / (N·m)", "torque / (N·m)"))
a2.text(-60, 6, T("面积 = ∫τ dθ = m g d ≈ 17.5 J\n= 质心升高的势能", "area = ∫τ dθ = m g d ≈ 17.5 J\n= rise in potential energy"), fontsize=9)
a2.legend(fontsize=9, frameon=False, loc="upper left")
a2.set_title(T("转动时，功 = 力矩对转角的积分", "In rotation, work = ∫ torque dθ"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig17_1_1")
