"""图 9.4.1：左：ln x 与 x^0.1（横轴取对数）：x^0.1 起初落后，在约 3×10¹⁵ 处反超，此后把 ln x 甩开；
右：关节阶跃响应在 ζ → 1 时趋于临界阻尼的响应（ωₙ = 10 rad/s）。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
lx = np.linspace(0, 20, 400)                 # log10 x
x = 10.0 ** lx
a1.plot(lx, np.log(x), color=BLUE, lw=2, label="ln x")
a1.plot(lx, x ** 0.1, color=RED, lw=2, label="$x^{0.1}$")
a1.axvline(15.535, color=MUTED, lw=0.8, ls="--")
a1.set_xlabel("lg x")
a1.set_ylim(0, 60)
a1.set_title(T("x^0.1 在 x ≈ 3×10¹⁵ 处反超 ln x", "x^0.1 overtakes ln x near x ≈ 3×10¹⁵"), fontsize=10)
a1.legend(fontsize=9, frameon=False)
clean(a1, zero=False)
wn = 10.0
t = np.linspace(0, 1.0, 400)
for z, c in ((0.6, MUTED), (0.9, GREEN), (0.99, BLUE)):
    s = np.sqrt(1 - z * z)
    q = 1 - np.exp(-z * wn * t) * (np.cos(wn * s * t) + z / s * np.sin(wn * s * t))
    a2.plot(t, q, color=c, lw=1.6, label=f"ζ = {z}")
a2.plot(t, 1 - np.exp(-wn * t) * (1 + wn * t), color=RED, lw=2, ls="--", label=T("ζ = 1（极限）", "ζ = 1 (limit)"))
a2.set_xlabel("t / s")
a2.set_ylabel("q(t)")
a2.set_title(T("ζ → 1：欠阻尼公式趋于临界阻尼公式", "ζ → 1: the underdamped formula tends to the critical one"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="lower right")
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig9_4_1")
