"""图 10.3.1：左：五次多项式关节运动 θ(t) 在前半段向上弯、后半段向下弯，拐点 T/2 处切线最陡（速度最大）；
右：三次、五次多项式与梯形速度曲线的角加速度，虚线为各自的均方根。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import cubic, quintic, trapezoid

Tt, D = 2.0, math.pi / 2
t = np.linspace(0, Tt, 801)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
th, w, a, _ = quintic(t, Tt, D)
a1.plot(t, th, color=INK, lw=2, label="θ(t)")
a1.axvspan(0, Tt / 2, color=GREEN, alpha=0.08, lw=0)
a1.axvspan(Tt / 2, Tt, color=RED, alpha=0.08, lw=0)
tm = Tt / 2
a1.plot(t[(t > 0.6) & (t < 1.4)], D / 2 + 15 * D / (8 * Tt) * (t[(t > 0.6) & (t < 1.4)] - tm), color=BLUE, lw=1.3, ls="--")
a1.plot([tm], [D / 2], "o", color=ACC, ms=7)
a1.set_xlabel("t / s")
a1.set_ylabel("θ / rad")
a1.set_title(T("θ″ > 0 向上弯（绿），θ″ < 0 向下弯（红），拐点处速度最大", "Concave up (green), down (red); fastest at the inflection point"), fontsize=10)
clean(a1, zero=False)
for (name, f, c) in ((T("三次", "cubic"), lambda t: cubic(t, Tt, D), BLUE), (T("五次", "quintic"), lambda t: quintic(t, Tt, D), RED),
                     (T("梯形速度", "trapezoid"), lambda t: trapezoid(t, Tt, D, Tt / 3), GREEN)):
    _, _, aa, _ = f(t)
    a2.plot(t, aa, color=c, lw=1.8, label=name)
    rms = math.sqrt(np.mean(aa * aa))
    a2.axhline(rms, color=c, lw=0.8, ls="--")
a2.set_xlabel("t / s")
a2.set_ylabel("α / (rad/s²)")
a2.set_title(T("同样的位移，均方根加速度不同（虚线）", "Same move, different RMS acceleration (dashed)"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="lower left")
clean(a2)
fig.tight_layout()
figure(fig, "fig10_3_1")
