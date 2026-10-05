"""图 13.5.1：轨迹的时间缩放。左：同一次 90° 转动用 T = 1、2、4 s 完成时的角加速度；
右：∫α² dt 随 T 的变化（双对数坐标），斜率 −3。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

D = np.pi / 2
s2 = lambda u: 60 * u - 180 * u ** 2 + 120 * u ** 3
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
for Tm, c in ((1.0, RED), (2.0, BLUE), (4.0, GREEN)):
    t = np.linspace(0, Tm, 300)
    a1.plot(t, D * s2(t / Tm) / Tm ** 2, color=c, lw=2, label=f"T = {Tm:g} s")
a1.set_xlabel("t / s")
a1.set_ylabel("α / (rad/s²)")
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("时间拉长一倍，角加速度降为四分之一", "Twice the time, a quarter of the acceleration"), fontsize=10)
clean(a1)
Ts = np.logspace(-0.5, 0.8, 30)
a2.loglog(Ts, 120 / 7 * D ** 2 / Ts ** 3, color=BLUE, lw=2)
for Tm in (0.5, 1, 2, 4):
    a2.loglog([Tm], [120 / 7 * D ** 2 / Tm ** 3], "o", color=RED, ms=5)
a2.set_xlabel("T / s")
a2.set_ylabel(r"$\int_0^T\alpha^2\,dt$ / (rad²/s³)")
a2.set_title(r"$\int_0^T\alpha^2\,dt = \frac{120}{7}\,\Delta^2/T^3$", fontsize=11)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig13_5_1")
