"""图 4.6.1：特殊矩阵的“形状”（深色为非零元）：对角、上三角、置换、一维杆的三对角矩阵、二维网格（10×10 个节点）的稀疏矩阵。"""
import numpy as np
import scipy.sparse as sp

from _fig import INK, T, figure, plt

n = 10
D = np.diag(np.arange(1, n + 1))
U = np.triu(np.ones((n, n)))
P = np.eye(n)[np.random.default_rng(46).permutation(n)]
L1 = sp.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(n, n)).toarray()
I = sp.identity(n)
L2 = (sp.kron(I, sp.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(n, n))) + sp.kron(sp.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(n, n)), I)).toarray()
fig, axs = plt.subplots(1, 5, figsize=(12.0, 2.9))
for ax, (M, name) in zip(axs, ((D, T("对角", "diagonal")), (U, T("上三角", "upper triangular")), (P, T("置换", "permutation")),
                               (L1, T("三对角（一维杆）", "tridiagonal (1D bar)")), (L2, T("二维网格，100×100", "2D grid, 100×100")))):
    ax.spy(M, markersize=3.5 if M.shape[0] == n else 1.2, color=INK)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(name, fontsize=10)
fig.tight_layout()
figure(fig, "fig4_6_1")
