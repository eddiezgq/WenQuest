"""图 20.6.1：放大系数 M(r) 与相位滞后 φ(r) 随频率比 r 的变化（不同阻尼比）。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
r = np.linspace(0.01, 3, 1500)
cols = (RED, ACC, GREEN, BLUE, INK)
for z, col in zip((0.02, 0.1, 0.2, 0.5, 0.7), cols):
    M = 1 / np.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2)
    a1.semilogy(r, M, color=col, lw=1.8, label=f"ζ = {z:g}")
    a2.plot(r, np.degrees(np.arctan2(2 * z * r, 1 - r * r)), color=col, lw=1.8, label=f"ζ = {z:g}")
a1.axvline(1, color=MUTED, ls=":", lw=1)
a1.set_ylim(0.1, 40)
a1.set_xlabel(T("频率比 r = ω/ω_n", "frequency ratio r = ω/ω_n"))
a1.set_ylabel(T("放大系数 M（对数坐标）", "magnification M (log scale)"))
a1.set_title(T("放大系数：阻尼越小，共振峰越高越尖", "Magnification: less damping, taller and sharper peak"), fontsize=10)
a1.legend(fontsize=9, frameon=False)
for s_ in ("top", "right"):
    a1.spines[s_].set_visible(False)
a2.axhline(90, color=MUTED, ls=":", lw=1)
a2.axvline(1, color=MUTED, ls=":", lw=1)
a2.set_yticks([0, 45, 90, 135, 180])
a2.set_xlabel(T("频率比 r = ω/ω_n", "frequency ratio r = ω/ω_n"))
a2.set_ylabel(T("相位滞后 φ / °", "phase lag φ / °"))
a2.set_title(T("相位滞后：共振处恒为 90°", "Phase lag: always 90° at resonance"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig20_6_1")
