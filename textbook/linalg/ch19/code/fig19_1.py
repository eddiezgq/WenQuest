"""图 19.1.1：200 件减速器的检测数据。(a) 空载噪声与振动速度的散点：中心化就是把原点移到均值点；
(b) 六个项目的相关矩阵（颜色深浅表示相关系数）。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, figure, plt
from _qc import SHORT, SHORT_EN, X_I

X = X_I
m = X.mean(axis=0)
R = np.corrcoef(X.T)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.6), gridspec_kw={"width_ratios": [1.1, 1]})
a1.scatter(X[:, 2], X[:, 4], s=10, color=BLUE, alpha=0.6, lw=0)
a1.axvline(m[2], color=RED, lw=1, ls="--")
a1.axhline(m[4], color=RED, lw=1, ls="--")
a1.plot(m[2], m[4], "o", color=RED, ms=7)
a1.annotate(T("均值点（中心化后的原点）", "mean (origin after centring)"), xy=(m[2], m[4]), xytext=(m[2] + 1.2, m[4] - 0.45),
            color=RED, fontsize=9.5, arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
a1.set_xlabel(T("空载噪声 / dB(A)", "no-load noise / dB(A)"))
a1.set_ylabel(T("振动速度 / (mm/s)", "vibration velocity / (mm/s)"))
a1.set_title(T(f"(a) 噪声与振动：相关系数 {R[2, 4]:.2f}", f"(a) Noise and vibration: correlation {R[2, 4]:.2f}"), fontsize=11)
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
names = T(SHORT, SHORT_EN)
im = a2.imshow(R, cmap="RdBu_r", vmin=-1, vmax=1)
for i in range(6):
    for j in range(6):
        a2.text(j, i, f"{R[i, j]:.2f}", ha="center", va="center", fontsize=8.5, color="white" if abs(R[i, j]) > 0.6 else INK)
a2.set_xticks(range(6))
a2.set_xticklabels(names, fontsize=9)
a2.set_yticks(range(6))
a2.set_yticklabels(names, fontsize=9)
a2.set_title(T("(b) 相关矩阵 R", "(b) Correlation matrix R"), fontsize=11)
cb = fig.colorbar(im, ax=a2, shrink=0.8)
cb.outline.set_edgecolor(MUTED)
fig.tight_layout()
figure(fig, "fig19_1_1")
