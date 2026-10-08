"""M1.7 节的示意图。

图 M1.7.1：（a）同一个最小二乘问题，用原始数据与标准化数据建立的正规方程，奇异值谱差了十个数量级；
（b）条件数决定最坏情况下误差被放大多少倍——横轴是人为构造的条件数，纵轴是实测的放大倍数，两者重合。
"""
import numpy as np

from _chM1 import parts, standardize
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
X = parts()
Z, _, _ = standardize(X)
Xt = np.c_[np.ones(len(X)), X[:, 0], X[:, 1], X[:, 2]]
Xz = np.c_[np.ones(len(Z)), Z[:, 0], Z[:, 1], Z[:, 2]]
s_raw = np.linalg.svd(Xt.T @ Xt, compute_uv=False)
s_std = np.linalg.svd(Xz.T @ Xz, compute_uv=False)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 3.8))
a.semilogy(range(1, 5), s_raw, "o-", color=C["x"], lw=1.6, ms=6, label=T("原始数据", "raw data"))
a.semilogy(range(1, 5), s_std, "s-", color=C["z"], lw=1.6, ms=6, label=T("按列标准化后", "standardized"))
a.set_xticks(range(1, 5))
a.set_xlabel(T("第几个奇异值", "index"))
a.set_ylabel(T("奇异值", "singular value"))
a.set_title(T("(a) 正规方程系数矩阵的奇异值", "(a) Singular values of the normal equations"), fontsize=10)
a.legend(fontsize=9)
a.grid(alpha=0.25, lw=0.5)

# （b）人为构造一串条件数，量一量放大倍数
kappas = np.logspace(1, 12, 23)
amps = []
g = np.random.default_rng(17)
Q, _ = np.linalg.qr(g.normal(0, 1, (4, 4)))
for k in kappas:
    M = Q @ np.diag(np.logspace(0, -np.log10(k), 4)) @ Q.T
    U_, s_, Vt_ = np.linalg.svd(M)
    bb = U_[:, 0] * s_[0]
    x0 = np.linalg.solve(M, bb)
    db = U_[:, -1] * 1e-12 * np.linalg.norm(bb)
    x1 = np.linalg.solve(M, bb + db)
    amps.append((np.linalg.norm(x1 - x0) / np.linalg.norm(x0)) / (np.linalg.norm(db) / np.linalg.norm(bb)))
b.loglog(kappas, amps, "o", color=C["z"], ms=5, label=T("实测的放大倍数", "measured amplification"))
b.loglog(kappas, kappas, "-", color=C["muted"], lw=1.2, label=T("条件数本身", "the condition number"))
b.set_xlabel(T("条件数 $\\kappa$", "condition number $\\kappa$"))
b.set_ylabel(T("最坏情况下的放大倍数", "worst-case amplification"))
b.set_title(T("(b) 条件数就是放大倍数的上界", "(b) The condition number is the bound"), fontsize=10)
b.legend(fontsize=9)
b.grid(alpha=0.25, lw=0.5, which="both")
fig.tight_layout()
figure(fig, "figM1_7_1")
