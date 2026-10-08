"""M1.5 节的示意图。

图 M1.5.1：（a）协方差矩阵的特征值谱（标准化后，五个方向上的方差，和为 5）；
（b）这批零件在前两个主成分上的散布，箭头是前两个特征向量在"外径—粗糙度"平面上的投影。
"""
import numpy as np

from _chM1 import parts, standardize
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
Z, _, _ = standardize(parts())
Cov = Z.T @ Z / (len(Z) - 1)
lam, Q = np.linalg.eigh(Cov)
lam, Q = lam[::-1], Q[:, ::-1]
P = Z @ Q[:, :2]

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 4.0))
a.bar(range(1, 6), lam, color=C["z"], width=0.6)
a.set_xlabel(T("第几个主成分", "principal component"))
a.set_ylabel(T("特征值（方差）", "eigenvalue (variance)"))
a.set_title(T("(a) 特征值谱与累计解释比例", "(a) Eigenvalues and cumulative share"), fontsize=10)
a.grid(alpha=0.25, lw=0.5)
a2 = a.twinx()
a2.plot(range(1, 6), np.cumsum(lam) / lam.sum() * 100, "o-", color=C["accent"], lw=1.6, ms=5)
a2.set_ylim(0, 105)
a2.set_ylabel(T("累计解释比例（%）", "cumulative share (%)"), color=C["accent"])
a2.tick_params(axis="y", colors=C["accent"])

X = parts()
sc = b.scatter(P[:, 0], P[:, 1], s=16, c=X[:, 4], cmap="viridis", alpha=0.85, edgecolors="none")
cb = fig.colorbar(sc, ax=b)
cb.set_label(T("粗糙度 / µm", "roughness / µm"))
b.set_xlabel(T("第 1 主成分", "PC1"))
b.set_ylabel(T("第 2 主成分", "PC2"))
b.set_title(T("(b) 第 1 主成分与刀具磨损对应", "(b) PC1 tracks tool wear"), fontsize=10)
b.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "figM1_5_1")
