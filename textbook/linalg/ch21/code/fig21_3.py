"""图 21.3.1：格什戈林圆盘。(a) 算例 21.3.1：三个行圆盘互不相交，各含一个特征值（×）；虚线为列圆盘；
(b) 三个关节电机的热模型（单位 10⁻³ s⁻¹，只画原点附近）：行圆盘（灰）中绕组的圆盘碰到原点，证不出稳定；
对角相似变换 D⁻¹AD（D = diag(1, s, 1, s, 1, s)，s = 0.954）后的圆盘（彩色）都在左半平面，最右端给出最慢衰减率的界。"""
import math

import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _thermal import model


def discs(A):
    c = np.diag(A)
    return c, np.sum(np.abs(A), axis=1) - np.abs(c)


def draw(ax, c, r, col, ls="-", lw=1.6, alpha=0.10, scale=1.0):
    u = np.linspace(0, 2 * math.pi, 361)
    for ci, ri in zip(c, r):
        ax.fill(scale * (ci + ri * np.cos(u)), scale * ri * np.sin(u), color=col, alpha=alpha, lw=0)
        ax.plot(scale * (ci + ri * np.cos(u)), scale * ri * np.sin(u), color=col, lw=lw, ls=ls)


fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.25, 1]})
A = np.array([[10.0, 1.0, -0.5], [0.4, 4.0, 0.8], [0.6, 0.2, -2.0]])
c, r = discs(A)
cc, rc = discs(A.T)
for ci, ri, col in zip(c, r, (RED, GREEN, BLUE)):
    draw(a1, [ci], [ri], col)
draw(a1, cc, rc, MUTED, ls="--", lw=1, alpha=0)
ev = np.linalg.eigvals(A)
a1.plot(ev.real, ev.imag, "x", color=INK, ms=9, mew=2)
a1.set_aspect("equal")
a1.axhline(0, color=MUTED, lw=0.6)
a1.axvline(0, color=MUTED, lw=0.6)
a1.set_xlim(-3.6, 12)
a1.set_ylim(-2.2, 2.2)
a1.set_xlabel(T("实部", "real part"))
a1.set_ylabel(T("虚部", "imaginary part"))
a1.set_title(T("(a) 算例 21.3.1：行圆盘（实线）、列圆盘（虚线）、特征值（×）", "(a) Example 21.3.1: row discs (solid), column discs (dashed), eigenvalues (×)"), fontsize=10)
cap, G, Ath = model()
c, r = discs(Ath)
s = 0.954
D = np.diag([1, s] * 3)
c2, r2 = discs(np.linalg.inv(D) @ Ath @ D)
ev = np.linalg.eigvals(Ath)
ins = a2.inset_axes([0.60, 0.56, 0.38, 0.42])
for ax in (a2, ins):
    draw(ax, c, r, MUTED, lw=1.2, alpha=0.05, scale=1000)
    for i in range(6):
        draw(ax, [c2[i]], [r2[i]], RED if i % 2 == 0 else BLUE, scale=1000, alpha=0.06, lw=1.3)
    ax.plot(1000 * ev.real, 1000 * ev.imag, "x", color=INK, ms=8, mew=2)
    ax.axvline(0, color=INK, lw=1)
    ax.axhline(0, color=MUTED, lw=0.6)
ins.axvline(1000 * np.max(c2 + r2), color=RED, lw=1, ls=":")
ins.set_xlim(-6, 1)
ins.set_ylim(-2.5, 2.5)
ins.set_aspect("equal")
ins.tick_params(labelsize=7)
ins.set_title(T("原点附近放大", "zoom near 0"), fontsize=8)
a2.indicate_inset_zoom(ins, edgecolor=MUTED)
a2.set_aspect("equal")
a2.set_xlim(-90, 8)
a2.set_ylim(-45, 45)
a2.set_xlabel(T("实部 / 10⁻³ s⁻¹", "real part / 10⁻³ s⁻¹"))
a2.plot([], [], color=MUTED, label=T("原来的行圆盘", "original row discs"))
a2.plot([], [], color=RED, label=T("缩放后：绕组", "scaled: windings"))
a2.plot([], [], color=BLUE, label=T("缩放后：外壳", "scaled: housings"))
a2.legend(frameon=False, fontsize=8.5, loc="lower left")
a2.set_title(T("(b) 关节电机热模型", "(b) Joint-motor thermal model"), fontsize=10)
fig.tight_layout()
figure(fig, "fig21_3_1")
