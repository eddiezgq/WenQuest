"""图 1.4.1：《九章算术》方程第一题的筹算布列——三行（竖排，自右而左）在“遍乘直除”前后；图 1.4.2：线性代数史上的几个节点。"""
from _fig import ACC, BLUE, INK, MUTED, RED, T, figure, plt

before = {"右行": [3, 2, 1, 39], "中行": [2, 3, 1, 34], "左行": [1, 2, 3, 26]}
after = {"右行": [3, 2, 1, 39], "中行": [0, 5, 1, 24], "左行": [0, 0, 36, 99]}
rows = [T("上禾", "top grade"), T("中禾", "middle"), T("下禾", "low grade"), T("实（斗）", "total (dou)")]
cols_en = {"右行": "right", "中行": "middle", "左行": "left"}
fig, axs = plt.subplots(1, 2, figsize=(9.4, 3.9))
for ax, data, title in ((axs[0], before, T("布列：三行竖排，自右而左", "Layout: three columns, right to left")),
                        (axs[1], after, T("遍乘直除之后：左行只剩下禾", "After elimination: left column holds only the low grade"))):
    names = ["左行", "中行", "右行"]                                 # 画面上从左到右
    for c, nm in enumerate(names):
        ax.text(c + 1, 4.5, T(nm, cols_en[nm]), ha="center", fontsize=12, color=BLUE)
        for r, v in enumerate(data[nm]):
            ax.text(c + 1, 3.4 - r, str(v), ha="center", va="center", fontsize=15, color=RED if (v == 0) else INK)
    for r, lab in enumerate(rows):
        ax.text(0.2, 3.4 - r, lab, ha="left", va="center", fontsize=11, color=MUTED)
    ax.plot([0.15, 3.6], [0.95, 0.95], color=MUTED, lw=0.8)
    ax.set_xlim(0, 3.7)
    ax.set_ylim(-0.1, 5.0)
    ax.axis("off")
    ax.set_title(title, fontsize=11)
fig.tight_layout()
figure(fig, "fig1_4_1")

events = [(100, T("《九章算术》方程章", "Nine Chapters: fangcheng")), (263, T("刘徽注《九章算术》", "Liu Hui's commentary")),
          (1683, T("关孝和：行列式", "Seki: determinants")), (1693, T("莱布尼茨：行列式", "Leibniz: determinants")),
          (1750, T("克拉默法则", "Cramer's rule")), (1809, T("高斯：消元与最小二乘", "Gauss: elimination, least squares")),
          (1844, T("格拉斯曼：线性扩张论", "Grassmann: Ausdehnungslehre")), (1850, T("西尔维斯特：“矩阵”一词", "Sylvester: the word 'matrix'")), (1858, T("凯莱：矩阵理论", "Cayley: theory of matrices")),
          (1888, T("皮亚诺：向量空间公理", "Peano: vector-space axioms")), (1947, T("冯·诺伊曼、戈德斯坦：误差分析", "von Neumann, Goldstine: error analysis")),
          (1948, T("图灵：舍入误差与条件数", "Turing: rounding errors, condition")), (1965, T("戈卢布、卡汉：奇异值的计算方法", "Golub, Kahan: computing the SVD")), (1992, T("LAPACK 发布", "LAPACK released")),
          (1998, T("PageRank", "PageRank")), (2012, T("GPU 训练深度网络", "deep nets trained on GPUs"))]
fig, ax = plt.subplots(figsize=(7.6, 7.4))
n = len(events)
ax.plot([0, 0], [0.5, n + 0.5], color=INK, lw=1.5)
for k, (y, txt) in enumerate(events):
    Y = n - k
    ax.plot([0], [Y], "o", color=ACC if y < 1700 else BLUE, ms=7, zorder=3)
    ax.text(-0.15, Y, (T("约 ", "c. ") + str(y)) if y == 100 else str(y), ha="right", va="center", fontsize=11, color=ACC if y < 1700 else BLUE)
    ax.text(0.15, Y, txt, ha="left", va="center", fontsize=11)
ax.text(-0.15, n + 0.9, T("年份", "year"), ha="right", fontsize=10, color=MUTED)
ax.set_xlim(-1.4, 4.2)
ax.set_ylim(0.3, n + 1.2)
ax.axis("off")
figure(fig, "fig1_4_2")
