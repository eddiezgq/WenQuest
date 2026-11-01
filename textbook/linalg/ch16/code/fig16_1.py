"""图 16.1.1：电机停机后的冷却（程序 16.1.1）。(a) 绕组与外壳温升随时间（横轴为对数刻度）：绕组先随快模态（τ ≈ 23 s）
迅速降到接近外壳，再与外壳一起随慢模态（τ ≈ 552 s）冷却；(b) 相平面：两条特征直线，轨线先沿快特征向量方向走，再贴着慢特征向量趋于原点。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _motor import A

lam, V = np.linalg.eig(A)
o = np.argsort(-lam); lam, V = lam[o].real, V[:, o].real
V = V / V[0]
x0 = np.array([60.0, 40.0])
c = np.linalg.solve(V, x0)
x = lambda t: (V * np.exp(lam * t)) @ c
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
ts = np.logspace(-0.5, np.log10(4000), 400)
X = np.array([x(t) for t in ts])
a1.semilogx(ts, X[:, 0], color=RED, lw=2, label=T("绕组温升", "winding rise"))
a1.semilogx(ts, X[:, 1], color=BLUE, lw=2, label=T("外壳温升", "housing rise"))
a1.semilogx(ts, c[0] * np.exp(lam[0] * ts), color=MUTED, lw=1.2, ls="--", label=T("慢模态 c₁exp(λ₁t)（第 1 分量）", "slow mode c₁exp(λ₁t) (1st comp.)"))
for tau, lab in ((-1 / lam[1], "τ₂"), (-1 / lam[0], "τ₁")):
    a1.axvline(tau, color=ACC, lw=0.8, ls=":")
    a1.text(tau * 1.05, 58, f"{lab} = {tau:.0f} s", color=ACC, fontsize=9)
a1.set_xlabel(T("时间 t / s（对数刻度）", "time t / s (log scale)")); a1.set_ylabel(T("温升 / K", "temperature rise / K"))
a1.legend(frameon=False, fontsize=8.5, loc="lower left")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(a) 先快后慢", "(a) Fast first, then slow"), fontsize=11)
tt = np.linspace(0, 4000, 4000)
Y = np.array([x(t) for t in tt])
a2.plot(Y[:, 0], Y[:, 1], color=INK, lw=2)
for k in (0, 10, 30, 100, 300, 1000):
    p = x(k)
    a2.plot(*p, "o", color=INK, ms=4)
    a2.text(p[0] + 1, p[1] - 2.5, f"{k} s", fontsize=8, color=INK)
for j, col, lab in ((0, GREEN, T("慢：v₁", "slow: v₁")), (1, RED, T("快：v₂", "fast: v₂"))):
    v = V[:, j] / np.linalg.norm(V[:, j])
    a2.plot([-70 * v[0], 70 * v[0]], [-70 * v[1], 70 * v[1]], color=col, lw=1.2, ls="--")
    a2.text(55 * v[0] + 2, 55 * v[1] - 4 + (10 if j else 0), lab, color=col, fontsize=10)
a2.set_xlim(-5, 70); a2.set_ylim(-10, 50); a2.set_aspect("equal")
a2.axhline(0, color=MUTED, lw=0.6); a2.axvline(0, color=MUTED, lw=0.6)
a2.set_xlabel(T("绕组温升 / K", "winding rise / K")); a2.set_ylabel(T("外壳温升 / K", "housing rise / K"))
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) 相平面上的轨线", "(b) The trajectory in the phase plane"), fontsize=11)
fig.tight_layout()
figure(fig, "fig16_1_1")
