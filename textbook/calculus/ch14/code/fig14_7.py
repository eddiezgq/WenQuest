"""图 14.7.1：左：单摆周期与小振幅周期之比随振幅的变化（椭圆积分），1% 的位置约 23°；
右：两个“积不出来”的函数——误差函数 erf x 与正弦积分 Si x。"""
import math

import numpy as np
from scipy import special

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
th = np.linspace(1, 170, 400)
ratio = 2 / np.pi * special.ellipk(np.sin(np.radians(th) / 2) ** 2)
a1.plot(th, ratio, color=BLUE, lw=2)
a1.axhline(1.01, color=RED, lw=0.8, ls="--")
a1.axvline(22.8, color=RED, lw=0.8, ls="--")
a1.set_xlabel(T("振幅 θ₀ / (°)", "amplitude θ₀ / (°)"))
a1.set_ylabel("T / T₀")
a1.set_title(T("振幅大了，摆得慢", "Larger swings are slower"), fontsize=10)
clean(a1, zero=False)
x = np.linspace(0, 12, 600)
a2.plot(x, special.erf(x), color=GREEN, lw=2, label="erf x")
a2.plot(x, special.sici(x)[0], color=BLUE, lw=2, label="Si x")
a2.axhline(math.pi / 2, color=MUTED, lw=0.8, ls="--")
a2.set_xlabel("x")
a2.legend(fontsize=9, frameon=False, loc="lower right")
a2.set_title(T("用积分定义的函数：Si x → π/2", "Functions defined by integrals: Si x → π/2"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig14_7_1")
