"""图 1.7.1：本书九篇的关系。"""
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, ax = plt.subplots(figsize=(10, 5.2))
boxes = {
    "p1": (0.5, 4.0, T("第一篇\n函数、极限与连续", "Part I\nFunctions, limits, continuity")),
    "p2": (3.2, 5.0, T("第二篇\n一元微分学", "Part II\nDifferential calculus")),
    "p3": (3.2, 3.0, T("第三篇\n一元积分学", "Part III\nIntegral calculus")),
    "p4": (6.0, 5.0, T("第四篇\n常微分方程", "Part IV\nODEs")),
    "p5": (6.0, 3.0, T("第五篇\n无穷级数", "Part V\nInfinite series")),
    "p6": (3.2, 1.0, T("第六篇\n向量与曲线", "Part VI\nVectors and curves")),
    "p7": (6.0, 1.0, T("第七篇\n多元微分学", "Part VII\nSeveral variables")),
    "p8": (8.8, 1.0, T("第八篇\n多元积分与向量分析", "Part VIII\nMultiple integrals, vector analysis")),
    "p9": (8.8, 4.0, T("第九篇\n拓展与应用", "Part IX\nFurther topics, applications")),
}
for k, (x, y, txt) in boxes.items():
    ax.add_patch(plt.Rectangle((x - 1.15, y - 0.55), 2.3, 1.1, fc="#eef3f8" if k != "p9" else "#fdf1dc", ec=INK, lw=1.1))
    ax.text(x, y, txt, ha="center", va="center", fontsize=10)
arrows = [("p1", "p2"), ("p1", "p3"), ("p2", "p3"), ("p2", "p4"), ("p3", "p4"), ("p3", "p5"), ("p2", "p6"), ("p3", "p6"), ("p6", "p7"), ("p7", "p8"),
          ("p4", "p9"), ("p5", "p9"), ("p8", "p9")]
for a, b in arrows:
    xa, ya, _ = boxes[a]
    xb, yb, _ = boxes[b]
    ax.annotate("", xy=(xb, yb), xytext=(xa, ya), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.2, shrinkA=30, shrinkB=30))
ax.text(5.6, 6.0, T("【进阶】章分布在第一、三、五、七、八、九篇中，可整章跳过", "Advanced chapters sit inside Parts I, III, V, VII, VIII, IX and may be skipped"), color=MUTED, ha="center", fontsize=10)
ax.set_xlim(-0.8, 10.2)
ax.set_ylim(0.2, 6.3)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig1_7_1")
