"""图 1.7.1：本书八篇之间的依赖关系（箭头指向依赖它的篇）。"""
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

parts = {1: (T("一 向量与线性方程组\n第 2–6 章", "I Vectors & linear systems\nCh. 2–6"), (0, 3)),
         2: (T("二 向量空间与线性映射\n第 7–9 章", "II Vector spaces & maps\nCh. 7–9"), (0, 2)),
         3: (T("三 正交性\n第 10–12 章", "III Orthogonality\nCh. 10–12"), (-1.7, 1)),
         4: (T("四 特征值\n第 13–17 章", "IV Eigenvalues\nCh. 13–17"), (1.7, 1)),
         5: (T("五 SVD 与矩阵分析\n第 18–21 章", "V SVD & matrix analysis\nCh. 18–21"), (0, 0)),
         6: (T("六 数值线性代数\n第 22–26 章", "VI Numerical LA\nCh. 22–26"), (-1.7, -1)),
         7: (T("七 推广与抽象\n第 27–29 章", "VII Generalizations\nCh. 27–29"), (1.7, -1)),
         8: (T("八 应用\n第 30–42 章", "VIII Applications\nCh. 30–42"), (0, -2))}
edges = [(1, 2), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6), (5, 7), (6, 8), (7, 8), (3, 6), (4, 7), (5, 8)]
fig, ax = plt.subplots(figsize=(8.0, 7.2))
for a, b in edges:
    ax.add_patch(FancyArrowPatch(parts[a][1], parts[b][1], arrowstyle="-|>", mutation_scale=14, color=MUTED, lw=1.2, shrinkA=30, shrinkB=30))
for k, (txt, (x, y)) in parts.items():
    col = {1: BLUE, 2: BLUE, 3: GREEN, 4: GREEN, 5: ACC, 6: RED, 7: RED, 8: INK}[k]
    ax.add_patch(FancyBboxPatch((x - 0.78, y - 0.3), 1.56, 0.6, boxstyle="round,pad=0.04", fc="white", ec=col, lw=1.8))
    ax.text(x, y, txt, ha="center", va="center", fontsize=9.5)
ax.set_xlim(-2.6, 2.6)
ax.set_ylim(-2.6, 3.6)
ax.set_aspect("equal")
ax.axis("off")
figure(fig, "fig1_7_1")
