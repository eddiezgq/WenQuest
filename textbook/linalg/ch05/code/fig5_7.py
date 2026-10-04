"""图 5.7.1：200 阶矩阵，条件数从 10 到 10¹⁵：用 solve（LU 分解）与用 inv(A) @ b 解方程组的相对残差（对数坐标）。"""
import numpy as np

from _fig import BLUE, RED, T, figure, plt

rng = np.random.default_rng(57)


def make(n, cond):
    U, _ = np.linalg.qr(rng.standard_normal((n, n)))
    V, _ = np.linalg.qr(rng.standard_normal((n, n)))
    return U @ np.diag(np.logspace(0, -np.log10(cond), n)) @ V.T


conds = np.logspace(1, 15, 15)
rs, ri = [], []
for c in conds:
    A = make(200, c)
    b = A @ rng.standard_normal(200)
    nA = np.linalg.norm(A, 2)
    for x, lst in ((np.linalg.solve(A, b), rs), (np.linalg.inv(A) @ b, ri)):
        lst.append(np.linalg.norm(b - A @ x) / (nA * np.linalg.norm(x)))
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.loglog(conds, rs, "s-", color=BLUE, ms=4, label=T("solve：LU 分解", "solve: LU factorization"))
ax.loglog(conds, ri, "o-", color=RED, ms=4, label=T("inv(A) @ b：先求逆", "inv(A) @ b: invert first"))
ax.set_xlabel(T("条件数", "condition number"))
ax.set_ylabel(T("相对残差", "relative residual"))
ax.legend(frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig5_7_1")
