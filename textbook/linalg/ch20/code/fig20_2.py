"""图 20.2.1：(a) A = [[1, −2], [3, 4]] 把三种单位球变成的图形：1-、2-、∞-范数的算子范数，就是像中离原点最远的点
（用同一种范数量）；(b) B = [[0.9, 1], [0, 0.9]] 的谱半径 0.9 < 1，可 ‖Bᵏ‖₂ 先升到约 4 再衰减。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, axes_box, figure, plt

A = np.array([[1.0, -2.0], [3.0, 4.0]])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.8), gridspec_kw={"width_ratios": [1, 1.2]})
t = np.linspace(0, 2 * math.pi, 1441)
C = np.vstack([np.cos(t), np.sin(t)])
for p, col, nm in ((1, RED, "₁"), (2, BLUE, "₂"), (np.inf, GREEN, "∞")):
    X = C / np.linalg.norm(C, p, axis=0)
    Y = A @ X
    a1.plot(X[0], X[1], color=col, lw=1, ls=":")
    a1.fill(Y[0], Y[1], color=col, alpha=0.08)
    a1.plot(Y[0], Y[1], color=col, lw=1.8, label=f"‖A‖{nm} = {np.linalg.norm(A, p):.2f}")
    k = int(np.argmax(np.linalg.norm(Y, p, axis=0)))
    a1.plot(Y[0, k], Y[1, k], "o", color=col, ms=6)
axes_box(a1, 7.5)
a1.legend(frameon=False, fontsize=8.5, loc="lower right")
a1.set_title(T("(a) 单位球（虚线）与它们在 A 下的像", "(a) Unit balls (dotted) and their images under A"), fontsize=11)
B = np.array([[0.9, 1.0], [0.0, 0.9]])
ks = np.arange(0, 81)
nk = [np.linalg.norm(np.linalg.matrix_power(B, k), 2) for k in ks]
a2.plot(ks, nk, "o-", color=RED, ms=3, lw=1.2, label="‖Bᵏ‖₂")
a2.plot(ks, 0.9 ** ks, color=BLUE, lw=1.6, label="ρ(B)ᵏ = 0.9ᵏ")
a2.plot(ks, np.linalg.norm(B, 2) ** ks, color=MUTED, lw=1, ls="--", label=T("‖B‖₂ᵏ（上界）", "‖B‖₂ᵏ (upper bound)"))
a2.set_ylim(0, 4.6)
a2.axhline(1, color=INK, lw=0.6, ls=":")
a2.set_xlabel("k")
a2.legend(frameon=False, fontsize=9)
a2.set_title(T("(b) 谱半径 < 1，范数却先升后降", "(b) Spectral radius < 1, yet the norm first grows"), fontsize=11)
for sp in ("top", "right"):
    a2.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig20_2_1")
