"""图 14.4.1：瑞利商与交错。(a) 三质量链（一端固定）的三个振型，以及试探振型 (1, 2, 3)、静变形 (3, 5, 6) 与第一振型的比较；
(b) 数轴上的特征值：原系统 λ₁ < λ₂ < λ₃（圆点），锁住第三个质量后 μ₁ < μ₂（方块），两组交错排列；
两个试探振型的瑞利商都不小于 λ₁。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

k = 1e4
K = k * np.array([[2.0, -1, 0], [-1, 2, -1], [0, -1, 1]])
w, V = np.linalg.eigh(K)
V = V * np.sign(V[2])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.0), gridspec_kw={"width_ratios": [1, 1.3]})
x = np.arange(0, 4)
for j, c in zip(range(3), (BLUE, GREEN, RED)):
    v = np.r_[0, V[:, j] / np.abs(V[:, j]).max()]
    a1.plot(x, v, "o-", color=c, lw=1.8, label=T(f"第 {j + 1} 振型", f"mode {j + 1}"))
for tr, c, ls, lab in (([1, 2, 3], MUTED, ":", T("试探 (1, 2, 3)", "trial (1, 2, 3)")), ([3, 5, 6], ACC, "--", T("静变形 (3, 5, 6)", "static (3, 5, 6)"))):
    v = np.r_[0, np.array(tr) / max(tr)]
    a1.plot(x, v, ls, color=c, lw=1.5, label=lab)
a1.axhline(0, color=MUTED, lw=0.6)
a1.set_xticks(x); a1.set_xticklabels([T("固定端", "fixed"), "1", "2", "3"])
a1.set_xlabel(T("质量编号", "mass")); a1.legend(frameon=False, fontsize=8.5, loc="lower left")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(a) 振型与试探振型", "(a) Modes and trial shapes"), fontsize=11)
mu = np.linalg.eigvalsh(K[:2, :2])
a2.axhline(0, color=MUTED, lw=1)
for v in w:
    a2.plot(v, 0, "o", color=BLUE, ms=10)
for v in mu:
    a2.plot(v, 0.25, "s", color=RED, ms=9)
r1 = np.array([1, 2, 3]) @ K @ [1, 2, 3] / 14
r2 = np.array([3, 5, 6]) @ K @ [3, 5, 6] / 70
a2.text(2200, -0.5, T(f"瑞利商：(1, 2, 3) → {r1:.0f}，(3, 5, 6) → {r2:.0f}，都 ≥ λ₁ = {w[0]:.0f}",
                      f"Rayleigh: (1, 2, 3) → {r1:.0f}, (3, 5, 6) → {r2:.0f}, both ≥ λ₁ = {w[0]:.0f}"), fontsize=9, color=ACC)
for i, v in enumerate(w):
    a2.text(v, 0.08 - 0.22, f"λ{chr(0x2081 + i)}", ha="center", fontsize=10, color=BLUE)
for i, v in enumerate(mu):
    a2.text(v, 0.38, f"μ{chr(0x2081 + i)}", ha="center", fontsize=10, color=RED)
a2.set_ylim(-0.7, 0.7); a2.set_yticks([])
a2.set_xlabel(T("ω² / s⁻²", "ω² / s⁻²"))
for s in ("top", "right", "left"):
    a2.spines[s].set_visible(False)
a2.text(200, 0.55, T("圆点：原系统；方块：锁住质量 3", "dots: original; squares: mass 3 locked"), fontsize=9, color=INK)
a2.set_title(T("(b) 特征值的交错与瑞利商的上界", "(b) Interlacing and Rayleigh upper bounds"), fontsize=11)
fig.tight_layout()
figure(fig, "fig14_4_1")
