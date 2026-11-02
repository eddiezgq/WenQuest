"""图 22.3.1：30 × 30 网格的拉普拉斯矩阵（900 阶）按四种排序做乔列斯基分解，因子 L 的非零元分布（黑点）：
自然排序（带状，带内全部填满）、反向卡思尔–麦基（带宽变窄的“包络”）、最小度、嵌套剖分。标题中为 nnz(L)。"""
import numpy as np

from _fig import INK, T, figure, plt
from _sparse import fill, grid_laplacian, min_degree, nested_dissection, rcm

m = 30
G = grid_laplacian(m)
N = m * m
orders = [(T("自然排序", "natural"), list(range(N))), (T("反向卡思尔–麦基", "reverse Cuthill–McKee"), rcm(G)),
          (T("最小度", "minimum degree"), min_degree(G)), (T("嵌套剖分", "nested dissection"), nested_dissection(m))]
fig, axs = plt.subplots(1, 4, figsize=(14, 3.9))
for ax, (name, o) in zip(axs, orders):
    nnz, pat, fl = fill(G, o)
    r = np.array([p[0] for p in pat] + list(range(N)))
    c = np.array([p[1] for p in pat] + list(range(N)))
    ax.plot(c, r, ",", color=INK, rasterized=True)
    ax.set_xlim(0, N)
    ax.set_ylim(N, 0)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"{name}\nnnz(L) = {nnz}", fontsize=10)
fig.tight_layout()
figure(fig, "fig22_3_1")
