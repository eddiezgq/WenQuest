"""图 5.3.1：左：随机 12 阶矩阵的 L 与 U（颜色深浅表示元素大小）；右：n = 1000 时解 k 个右端所需的乘法次数，
每次都从头消元与分解一次再前代、回代的比较（双对数坐标）。"""
import numpy as np

from _fig import BLUE, RED, T, figure, plt

rng = np.random.default_rng(531)
n = 12
A = rng.standard_normal((n, n)) + n * np.eye(n)
U = A.copy()
L = np.eye(n)
for k in range(n - 1):
    for i in range(k + 1, n):
        L[i, k] = U[i, k] / U[k, k]
        U[i, k:] -= L[i, k] * U[k, k:]
fig = plt.figure(figsize=(11.0, 3.8))
g = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.6])
for j, (M, name) in enumerate(((L, "L"), (U, "U"))):
    ax = fig.add_subplot(g[0, j])
    ax.imshow(np.where(np.abs(M) > 1e-12, np.log10(np.abs(M) + 1e-3), np.nan), cmap="Blues", vmin=-2, vmax=1.2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(name, fontsize=12)
ax = fig.add_subplot(g[0, 2])
N = 1000
k = np.logspace(0, 3, 50)
solve = N ** 3 / 3 + N ** 2
ax.loglog(k, k * solve, color=RED, label=T("每次从头消元", "eliminate from scratch each time"))
ax.loglog(k, (N ** 3 - N) / 3 + k * N ** 2, color=BLUE, label=T("分解一次，再逐个前代、回代", "factor once, then substitute"))
ax.set_xlabel(T("右端的个数 k", "number of right-hand sides k"))
ax.set_ylabel(T("乘法次数", "multiplications"))
ax.legend(frameon=False, fontsize=9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig5_3_1")
