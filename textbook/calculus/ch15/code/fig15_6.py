"""图 15.6.1：左：1/√x 在 0 附近无界，但曲线下面积有限（=2）；换元 x = u² 后被积函数变成常数 2；
右：摆的四分之一周期积分的被积函数 1/√(cos θ − cos θ₀)（θ₀ = 90°）在上端无界，换元 sin(θ/2) = k sin φ 后变成光滑的函数。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(0.002, 1, 400)
a1.plot(x, 1 / np.sqrt(x), color=RED, lw=2, label=r"$1/\sqrt{x}$")
a1.fill_between(x, 0, 1 / np.sqrt(x), color=RED, alpha=0.15)
a1.plot([0, 1], [2, 2], color=BLUE, lw=2, label=T("换元 x = u² 后：2", "after x = u²: 2"))
a1.set_ylim(0, 8)
a1.set_xlabel("x  /  u")
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("无界的被积函数，有限的面积", "Unbounded integrand, finite area"), fontsize=10)
clean(a1, zero=False)
t0 = np.pi / 2
th = np.linspace(0, t0 - 1e-4, 600)
a2.plot(np.degrees(th), 1 / np.sqrt(np.cos(th) - np.cos(t0)), color=RED, lw=2, label=T("原被积函数（对 θ）", "original (in θ)"))
k = np.sin(t0 / 2)
ph = np.linspace(0, np.pi / 2, 300)
a2.plot(np.degrees(ph), np.sqrt(2) / np.sqrt(1 - k * k * np.sin(ph) ** 2), color=BLUE, lw=2, label=T("换元后（对 φ）", "after substitution (in φ)"))
a2.set_ylim(0, 8)
a2.set_xlabel(T("θ 或 φ / (°)", "θ or φ / (°)"))
a2.legend(fontsize=9, frameon=False, loc="upper left")
a2.set_title(T("换元把端点的奇异性“抹平”", "Substitution smooths out the endpoint singularity"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig15_6_1")
