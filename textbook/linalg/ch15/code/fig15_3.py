"""图 15.3.1：惯性定理。(a) 合同变换 B = CᵀAC 改变等值线的形状，但不改变类型：椭圆仍是椭圆，双曲线仍是双曲线；
(b) 谱切片：柔性臂杆模型（程序 15.3.1）中，K − (2πf)²M 的负主元个数随 f 变化的阶梯，台阶恰好落在各固有频率上；40 Hz 处为 3。"""
import numpy as np
import scipy.linalg as sl

from _fig import ACC, BLUE, INK, MUTED, RED, T, axes_box, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.3), gridspec_kw={"width_ratios": [1, 1.25]})
C = np.array([[1.0, 0.8], [0.3, 1.2]])
u = np.linspace(-2.2, 2.2, 301)
X, Y = np.meshgrid(u, u)
for A, col, ls in ((np.diag([1.0, 3.0]), BLUE, "-"), (np.diag([1.0, -1.0]), RED, "-")):
    for M, lw, al in ((A, 2.0, 1.0), (C.T @ A @ C, 1.4, 0.8)):
        Z = M[0, 0] * X ** 2 + 2 * M[0, 1] * X * Y + M[1, 1] * Y ** 2
        a1.contour(X, Y, Z, levels=[1], colors=[col], linewidths=lw, linestyles="-" if M is A else "--", alpha=al)
axes_box(a1, 2.2)
a1.plot([], [], color=BLUE, lw=2, label=T("x² + 3y² = 1（椭圆）", "x² + 3y² = 1 (ellipse)"))
a1.plot([], [], color=RED, lw=2, label=T("x² − y² = 1（双曲线）", "x² − y² = 1 (hyperbola)"))
a1.plot([], [], color=MUTED, lw=1.4, ls="--", label=T("合同变换 CᵀAC 之后", "after the congruence CᵀAC"))
a1.legend(frameon=False, fontsize=8.5, loc="lower left")
a1.set_title(T("(a) 合同变换不改变类型", "(a) A congruence keeps the type"), fontsize=11)

n, m, k, mp = 6, 0.5, 2e4, 0.5
K = k * (2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)); K[-1, -1] = k
M = m * np.eye(n); M[-1, -1] += mp
fr = np.sqrt(sl.eigh(K, M, eigvals_only=True)) / (2 * np.pi)


def neg(f):
    S = K - (2 * np.pi * f) ** 2 * M
    d = [S[0, 0]]
    for i in range(1, n):
        d.append(S[i, i] - S[i, i - 1] ** 2 / d[-1])
    return int((np.array(d) < 0).sum())


fs = np.linspace(0.05, 70, 2000)
a2.step(fs, [neg(f) for f in fs], where="post", color=BLUE, lw=2)
for i, f in enumerate(fr):
    a2.axvline(f, color=MUTED, lw=0.7, ls=":")
    a2.text(f, 6.35, f"{f:.1f}", ha="center", fontsize=8, color=MUTED)
a2.axvline(40, color=ACC, lw=1.5)
a2.plot(40, neg(40), "o", color=ACC, ms=7)
a2.text(41, neg(40) - 0.45, T("40 Hz：3 个负主元", "40 Hz: 3 negative pivots"), color=ACC, fontsize=9)
a2.set_ylim(-0.3, 6.8); a2.set_xlim(0, 70)
a2.set_xlabel(T("f / Hz", "f / Hz")); a2.set_ylabel(T("K − (2πf)²M 的负主元个数", "negative pivots of K − (2πf)²M"))
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) 负主元个数 = 低于 f 的固有频率个数", "(b) Negative pivots = natural frequencies below f"), fontsize=11, color=INK)
fig.tight_layout()
figure(fig, "fig15_3_1")
